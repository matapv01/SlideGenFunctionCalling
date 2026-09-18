"""Generate a hierarchy for DOCX content that has no explicit headings.

The model is deliberately responsible only for the outline. Source text stays
in the backend and is assigned to outline nodes by block id. This keeps the
LLM response small, prevents it from having to reproduce a long document as
JSON, and guarantees that a malformed response cannot erase source content.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Sequence

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from backend.workflows.doc_workflow.graph.stage import State
from backend.workflows.doc_workflow.utils.prompts import (
    AUTO_STRUCTURE_SYSTEM_PROMPT,
    HUMAN_PROMPT_TEMPLATE_AUTO as HUMAN_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)

AUTO_STRUCTURE_MAX_BLOCK_CHARS = 2_200
AUTO_STRUCTURE_MAX_RETRIES = 2
AUTO_STRUCTURE_MAX_OUTPUT_TOKENS = 4_096


def _split_source_blocks(
    text: str,
    max_chars: int = AUTO_STRUCTURE_MAX_BLOCK_CHARS,
) -> list[dict[str, str]]:
    """Split source text into stable, ordered blocks without dropping content."""
    clean_text = str(text or "").strip()
    if not clean_text:
        return []

    paragraphs = [
        part.strip()
        for part in re.split(r"\n\s*\n+", clean_text)
        if part.strip()
    ]
    if not paragraphs:
        paragraphs = [clean_text]

    blocks: list[str] = []
    limit = max(256, int(max_chars))
    for paragraph in paragraphs:
        remaining = paragraph
        while len(remaining) > limit:
            cut = remaining.rfind("\n", 0, limit + 1)
            if cut < limit // 2:
                cut = remaining.rfind(" ", 0, limit + 1)
            if cut < limit // 2:
                cut = limit
            blocks.append(remaining[:cut].strip())
            remaining = remaining[cut:].strip()
        if remaining:
            blocks.append(remaining)

    return [
        {"id": f"p{index:04d}", "text": block}
        for index, block in enumerate(blocks, start=1)
        if block
    ]


def _render_source_blocks(blocks: Sequence[dict[str, str]]) -> str:
    return "\n\n".join(
        f"[BLOCK {block['id']}]\n{block['text']}"
        for block in blocks
    )


def _balanced_json_candidates(raw: str) -> list[str]:
    """Extract balanced JSON array/object candidates from a model response."""
    text = str(raw or "").strip()
    candidates: list[str] = []

    for start, character in enumerate(text):
        if character not in "[{":
            continue

        stack: list[str] = []
        in_string = False
        escaped = False
        for index in range(start, len(text)):
            current = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == '"':
                    in_string = False
                continue

            if current == '"':
                in_string = True
                continue
            if current in "[{":
                stack.append(current)
                continue
            if current not in "]}":
                continue

            if not stack or (current == "]" and stack[-1] != "[") or (
                current == "}" and stack[-1] != "{"
            ):
                break
            stack.pop()
            if not stack:
                candidates.append(text[start : index + 1])
                break

    return candidates


def _parse_json_response(raw: str) -> Any:
    """Parse JSON even when the model wraps it in a markdown fence/prose."""
    errors: list[str] = []
    for candidate in _balanced_json_candidates(raw):
        try:
            return json.loads(candidate, strict=False)
        except json.JSONDecodeError as error:
            errors.append(str(error))

    if not errors:
        raise ValueError("Could not find a complete JSON array in the LLM response")
    raise ValueError(f"LLM returned invalid JSON: {errors[-1]}")


def _normalise_outline(
    payload: Any,
    valid_block_ids: set[str],
) -> tuple[list[dict[str, Any]], set[str]]:
    """Validate the compact outline and remove duplicate/unknown block IDs."""
    if isinstance(payload, dict):
        for key in ("sections", "outline", "items", "children"):
            if isinstance(payload.get(key), list):
                payload = payload[key]
                break
        else:
            payload = [payload]
    if not isinstance(payload, list):
        raise ValueError("LLM outline is not a JSON array")

    assigned: set[str] = set()

    def visit(raw_node: Any, depth: int) -> dict[str, Any] | None:
        if not isinstance(raw_node, dict):
            return None

        raw_title = (
            raw_node.get("title")
            or raw_node.get("heading")
            or raw_node.get("name")
        )
        title = " ".join(str(raw_title or "").split()).strip()
        if not title:
            return None

        raw_ids = raw_node.get("block_ids")
        if raw_ids is None:
            raw_ids = raw_node.get("paragraph_ids")
        if not isinstance(raw_ids, list):
            raw_ids = []

        candidate_ids: list[str] = []
        for raw_id in raw_ids:
            block_id = str(raw_id).strip()
            if block_id in valid_block_ids and block_id not in candidate_ids:
                candidate_ids.append(block_id)

        raw_children = raw_node.get("children")
        if not isinstance(raw_children, list):
            raw_children = raw_node.get("sections")
        if not isinstance(raw_children, list):
            raw_children = raw_node.get("sub_sections", [])
        children = [
            child
            for child in (visit(item, depth + 1) for item in raw_children)
            if child is not None
        ]

        # Let explicit child sections claim their blocks first. If a model
        # repeats a broad parent range in addition to child IDs, this keeps
        # the hierarchy instead of flattening all content into the parent.
        block_ids = [
            block_id
            for block_id in candidate_ids
            if block_id not in assigned
        ]
        assigned.update(block_ids)

        if not block_ids and not children:
            return None
        return {
            "level": depth,
            "title": title,
            "block_ids": block_ids,
            "children": children,
        }

    nodes = [
        node
        for node in (visit(item, 1) for item in payload)
        if node is not None
    ]
    if not nodes:
        raise ValueError("LLM outline did not contain any usable sections")
    return nodes, assigned


def _materialise_outline(
    outline: Sequence[dict[str, Any]],
    blocks: Sequence[dict[str, str]],
    assigned: set[str],
) -> list[dict[str, Any]]:
    """Attach original source blocks to the validated outline."""
    blocks_by_id = {block["id"]: block["text"] for block in blocks}

    def visit(node: dict[str, Any], depth: int) -> dict[str, Any]:
        content = "\n\n".join(
            blocks_by_id[block_id]
            for block_id in node.get("block_ids", [])
            if block_id in blocks_by_id
        ).strip()
        children = [
            visit(child, depth + 1)
            for child in node.get("children", [])
            if isinstance(child, dict)
        ]
        return {
            "level": depth,
            "title": node["title"],
            "content": content,
            "children": children,
        }

    materialised = [visit(node, 1) for node in outline]
    remaining = [
        block["text"]
        for block in blocks
        if block["id"] not in assigned
    ]
    if remaining:
        materialised.append(
            {
                "level": 1,
                "title": "Additional content",
                "content": "\n\n".join(remaining).strip(),
                "children": [],
            }
        )
    return materialised


def _fallback_structure(document_title: str, plain_text: str) -> list[dict[str, Any]]:
    """Keep RAG usable when the outline model is unavailable or invalid."""
    return [
        {
            "level": 1,
            "title": document_title or "Document content",
            "content": plain_text.strip(),
            "children": [],
        }
    ]


def _bind_outline_llm(llm: Any) -> Any:
    """Use a small deterministic output budget when the provider supports it."""
    bind = getattr(llm, "bind", None)
    if not callable(bind):
        return llm
    try:
        return bind(temperature=0.0, max_tokens=AUTO_STRUCTURE_MAX_OUTPUT_TOKENS)
    except Exception:
        return llm


def generate_structure_from_plaintext(state: State, config: RunnableConfig) -> State:
    """Generate an outline and materialise it with untouched source blocks."""
    print("\n---------------- Executing Node: generate_structure_from_plaintext ----------------")

    if state.get("document_structure"):
        print("Skipping auto-structure: document_structure already exists")
        return state

    start_time = time.time()
    configurable = config["configurable"]
    llm = configurable.get("llm")
    request_limiter = configurable.get("llm_request_limiter")

    stream_callback = configurable.get("stream_callback")
    if stream_callback:
        stream_callback(
            "status",
            {
                "step": 1,
                "title": "Auto-Generating Structure",
                "description": "AI analysis in progress",
                "message": "Generating a compact document outline...",
            },
        )

    document_title = str(state.get("document_title") or "Untitled Document")
    plain_text = str(state.get("plain_text") or "").strip()
    if not llm:
        raise ValueError("LLM is not found in config. Cannot generate structure.")
    if not plain_text:
        raise ValueError("No plain_text found in state. Cannot generate structure.")

    blocks = _split_source_blocks(plain_text)
    if not blocks:
        raise ValueError("No source blocks found in document.")

    prompt = ChatPromptTemplate.from_messages(
        [("system", AUTO_STRUCTURE_SYSTEM_PROMPT), ("human", HUMAN_PROMPT_TEMPLATE)]
    )
    chain = prompt | _bind_outline_llm(llm) | StrOutputParser()
    prompt_values = {
        "document_title": document_title,
        "source_blocks": _render_source_blocks(blocks),
    }

    last_error: Exception | None = None
    for attempt in range(AUTO_STRUCTURE_MAX_RETRIES + 1):
        retry_instruction = ""
        if attempt:
            retry_instruction = (
                "The previous response was invalid. Retry with strict JSON only. "
                "Do not include source text, comments, markdown fences, or trailing commas. "
                "Every block ID must be copied exactly from the input."
            )
        try:
            payload = {
                **prompt_values,
                "retry_instruction": retry_instruction,
            }
            if request_limiter is None:
                raw_response = chain.invoke(payload)
            else:
                with request_limiter.slot():
                    raw_response = chain.invoke(payload)
            payload = _parse_json_response(str(raw_response or ""))
            outline, assigned = _normalise_outline(
                payload,
                {block["id"] for block in blocks},
            )
            state["document_outline"] = outline
            state["document_structure"] = _materialise_outline(
                outline,
                blocks,
                assigned,
            )
            state["document_structure_origin"] = "llm"
            print(
                f"Generated outline from {len(blocks)} source blocks on attempt "
                f"{attempt + 1}."
            )
            print(f"Structure generation took {time.time() - start_time:.2f} seconds")
            return state
        except Exception as error:
            last_error = error
            logger.warning(
                "Auto-structure attempt %s/%s failed: %s",
                attempt + 1,
                AUTO_STRUCTURE_MAX_RETRIES + 1,
                error,
            )

    # Do not make a valid DOCX unusable just because the outline call failed.
    # The canonical Markdown remains searchable as one root node and can be
    # restructured later without losing source content.
    state["document_outline"] = []
    state["document_structure"] = _fallback_structure(document_title, plain_text)
    state["document_structure_origin"] = "fallback"
    state["document_preamble"] = ""
    logger.warning(
        "Using flat document fallback after %s outline attempts: %s",
        AUTO_STRUCTURE_MAX_RETRIES + 1,
        last_error,
    )
    print(
        "Outline generation failed after retries; keeping the document as a "
        "searchable root node."
    )
    print(f"Structure fallback took {time.time() - start_time:.2f} seconds")
    return state
