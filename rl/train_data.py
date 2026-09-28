"""Production-parity GRPO document and prompt preparation."""

from __future__ import annotations

import json
import random

from backend.workflows.slidegen_workflow.graph.stage import DeckStylePlan
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import assign_layouts
from rl.rewards.content_reward import _numeric_fact_records
from rl.slidegen_adapter import (
    QWEN_GENERATOR_SYSTEM_PROMPT,
    TOOLS_DICT,
    build_generator_human_prompt,
    format_tool_for_qwen,
)


def deck_style_for_document(document: list[dict]) -> dict:
    if not document:
        raise ValueError("Cannot prepare a document without slides")
    stored_style = document[0].get("style_context")
    if not isinstance(stored_style, dict) or not stored_style:
        raise ValueError(
            "GRPO training requires style_context from a rebuilt production corpus; "
            "rebuild the corpus instead of synthesizing a fallback deck style"
        )
    try:
        return DeckStylePlan.model_validate(stored_style).model_dump()
    except Exception as exc:
        raise ValueError("Rebuilt corpus contains an invalid deck style") from exc


def _layout_retrieval_query(
    *,
    topic: str,
    image_description: str,
    retrieval_query: str,
    purpose: str,
    content: str,
    design: str,
    tokenizer=None,
    max_tokens: int | None = None,
) -> str:
    fields = [
        ("Topic", topic[:300]),
        ("Image evidence", image_description[:900]),
        ("Slide query", retrieval_query[:500]),
        ("Purpose", purpose[:500]),
        ("Content", content[:1800]),
        ("Layout", design[:700]),
    ]
    if tokenizer is None or not max_tokens:
        return " | ".join(
            f"{label}: {value[:limit]}"
            for (label, value), limit in zip(
                fields, (100, 220, 160, 140, 220, 160), strict=True
            )
            if value
        )[:1100]

    capacity = max(24, int(max_tokens) - 20)
    weights = (0.15, 0.20, 0.16, 0.12, 0.20, 0.17)
    budgets = [max(3, int(capacity * weight)) for weight in weights]
    while sum(budgets) > capacity:
        largest = max(range(len(budgets)), key=budgets.__getitem__)
        budgets[largest] -= 1

    def compose() -> str:
        pieces = []
        for (label, value), budget in zip(fields, budgets, strict=True):
            if not value:
                continue
            token_ids = tokenizer.encode(str(value), add_special_tokens=False)
            clipped = tokenizer.decode(token_ids[:budget], skip_special_tokens=True).strip()
            if clipped:
                pieces.append(f"{label}: {clipped}")
        return " | ".join(pieces)

    query = compose()
    while len(tokenizer.encode(query, add_special_tokens=True)) > int(max_tokens):
        eligible = [index for index, budget in enumerate(budgets) if budget > 3]
        if not eligible:
            break
        budgets[max(eligible, key=budgets.__getitem__)] -= 1
        query = compose()
    return query


def normalize_jobs(document: list[dict], *, query_tokenizer=None, query_max_tokens=None) -> list[dict]:
    jobs = []
    for index, slide in enumerate(document):
        plan = dict(slide.get("plan") or {})
        if index == 0:
            plan["action"] = "INTRO_TOOLS"
        action = str(plan.get("action") or "CONTENT_TOOLS")
        image_assets = list(slide.get("approved_images") or [])
        image_mode = "semantic" if image_assets else "none"
        content = str(slide.get("user_prompt") or "").strip()
        design = str(plan.get("thought") or slide.get("design_instruction") or "")
        topic = str(
            plan.get("slide_topic")
            or slide.get("heading")
            or content.splitlines()[0][:160]
        ).strip()
        image_descriptions = [
            " ".join(
                str(image.get(key) or "").strip()
                for key in ("visual_notes", "caption_hint", "placement_hint")
            ).strip()
            for image in image_assets
        ]
        retrieval_query = _layout_retrieval_query(
            topic=topic,
            image_description=" ".join(image_descriptions),
            retrieval_query=str(plan.get("retrieval_query") or "").strip(),
            purpose=str(plan.get("slide_purpose") or "").strip(),
            content=content,
            design=design,
            tokenizer=query_tokenizer,
            max_tokens=query_max_tokens,
        )
        plan.update(
            {
                "action": action,
                "image_mode": image_mode,
                "slide_topic": topic,
                "retrieval_query": retrieval_query,
                "visual_layout_request": design,
            }
        )
        jobs.append(
            {
                "index": index,
                "batch_id": f"document-{slide.get('source_doc_id', 'unknown')}",
                "section_id": f"document-{slide.get('source_doc_id', 'unknown')}",
                "plan": plan,
                "content": content,
                "approved_images": image_assets,
                "source_slide": slide,
            }
        )
    return jobs


def prepare_document(
    document: list[dict],
    tokenizer,
    tool_retriever,
    *,
    strict_tool_retrieval: bool = False,
) -> list[dict]:
    embedding_model = getattr(getattr(tool_retriever, "embeddings", None), "model", None)
    query_tokenizer = getattr(embedding_model, "tokenizer", None)
    query_max_tokens = getattr(embedding_model, "max_seq_length", None)
    jobs = normalize_jobs(
        document,
        query_tokenizer=query_tokenizer,
        query_max_tokens=query_max_tokens,
    )
    assigned = assign_layouts(
        {"slide_jobs": jobs},
        {
            "configurable": {
                "tools_dict": TOOLS_DICT,
                "tool_retriever": tool_retriever,
                "strict_tool_retrieval": strict_tool_retrieval,
                "strict_image_layouts": True,
            }
        },
    )["slide_jobs"]
    deck_style = deck_style_for_document(document)
    style_json = json.dumps(deck_style, ensure_ascii=False, indent=2)
    samples = []
    for job in assigned:
        tool_name = str(job.get("preferred_tool_name") or "")
        if not tool_name:
            raise RuntimeError(
                f"No compatible {job['plan'].get('image_mode', 'none')} layout "
                f"for slide {job.get('index')}"
            )
        category = job["plan"]["action"]
        tool = next(
            (
                candidate
                for candidate in TOOLS_DICT[category]
                if candidate.name == tool_name
            ),
            None,
        )
        if tool is None:
            raise RuntimeError(f"Assigned layout is unavailable: {tool_name}")
        source = job["source_slide"]
        content = str(job.get("content") or "")
        design = str(job["plan"].get("visual_layout_request") or "")
        human_prompt = build_generator_human_prompt(
            deck_style_contract=style_json,
            slide_topic=str(job["plan"].get("slide_topic") or ""),
            slide_plan=json.dumps(job["plan"], ensure_ascii=False, indent=2),
            design_instruction=design,
            slide_content=content,
            assigned_tool_name=tool_name,
            slide_index=int(job["index"]),
            deck_length=len(jobs),
            image_mode=str(job["plan"].get("image_mode") or "none"),
            approved_images=job.get("approved_images") or [],
        )
        prompt = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": QWEN_GENERATOR_SYSTEM_PROMPT},
                {"role": "user", "content": human_prompt},
            ],
            tools=[format_tool_for_qwen(tool)],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        samples.append(
            {
                "prompt": prompt,
                "assigned_tool_name": tool_name,
                "source_content": str(source.get("source_content") or content).strip(),
                "numeric_facts": _numeric_fact_records(
                    str(source.get("source_content") or content).strip()
                ),
                "refined_content": content,
                "deck_style": deck_style,
                "source_doc_id": str(source.get("source_doc_id", "")),
                "slide_index": int(source.get("slide_index", job["index"])),
                "image_mode": str(job["plan"].get("image_mode") or "none"),
                "approved_images": job.get("approved_images") or [],
            }
        )
    return samples


def split_documents(
    documents: list[list[dict]], eval_docs: int, seed: int
) -> tuple[list, list]:
    if len(documents) <= eval_docs:
        raise ValueError(
            f"Corpus has {len(documents)} documents but GRPO_EVAL_DOCS={eval_docs}"
        )
    shuffled = list(documents)
    random.Random(seed).shuffle(shuffled)
    eval_documents = shuffled[:eval_docs]
    return shuffled[eval_docs:], eval_documents
