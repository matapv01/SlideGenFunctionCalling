"""Detect overflow, harmonize the whole slide, and regenerate its layout."""

from __future__ import annotations

import json
import logging
import re
import xml.etree.ElementTree as ET
from typing import Any

from backend.config import (
    EXECUTOR_MAX_RETRIES,
    TEXT_OVERFLOW_MAX_ROUNDS,
)
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    canonical_tool_name,
    execute_tool as execute_xml_tool,
    get_tool_by_name,
    normalize_tool_arguments,
)
from backend.workflows.slidegen_workflow.utils.xml_overflow import (
    analyze_xml_root,
    public_overflow_report,
)

logger = logging.getLogger(__name__)
_MATH_MARKER_RE = re.compile(r"<\s*/?\s*math-field\b", re.IGNORECASE)
_LATEX_MARKER_RE = re.compile(
    r"(?:\$[^$]+\$|\\\([^)]*\\\)|\\\[[^]]*\\\]|\\(?:frac|sqrt|sum|int|begin)\b)",
    re.IGNORECASE | re.DOTALL,
)
_PROTECTED_ARGUMENT_KEY_TOKENS = {
    "color",
    "url",
    "image",
    "icon",
    "font",
    "opacity",
    "background",
    "fill",
    "stroke",
    "border",
    "radius",
    "width",
    "height",
    "position",
    "direction",
}


def _response_text(response: Any) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text") or block.get("content") or ""))
            else:
                parts.append(str(block))
        return "".join(parts).strip()
    if isinstance(content, dict):
        return str(content.get("text") or content.get("summary") or "").strip()
    return str(content or "").strip()


def _parse_slide_rewrite(response: Any) -> dict[str, Any] | None:
    """Extract a complete tool-argument object from a whole-slide LLM response."""
    raw = _response_text(response)
    if not raw:
        return None

    cleaned = raw.strip()
    if "```" in cleaned:
        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        ).strip()

    candidates = [cleaned]
    object_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if object_match:
        candidates.insert(0, object_match.group(0))

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        arguments = payload.get("arguments")
        if isinstance(arguments, dict):
            return arguments
    return None


def _is_protected_argument_key(key: str) -> bool:
    normalized = key.strip().lower()
    return any(token in normalized for token in _PROTECTED_ARGUMENT_KEY_TOKENS)


def _contains_math_text(text: str) -> bool:
    return bool(_MATH_MARKER_RE.search(text) or _LATEX_MARKER_RE.search(text))


def _merge_shortened_arguments(
    original: Any,
    candidate: Any,
    *,
    key: str = "",
) -> tuple[Any, int]:
    """Merge only safe, non-expanding textual changes into existing arguments.

    Tool structure, list cardinality, visual settings, URLs, and math-bearing
    strings remain authoritative from the original validated tool call.
    """
    if isinstance(original, dict):
        if not isinstance(candidate, dict):
            return original, 0
        merged: dict[str, Any] = {}
        changes = 0
        for child_key, original_value in original.items():
            candidate_value = candidate.get(child_key, original_value)
            merged_value, child_changes = _merge_shortened_arguments(
                original_value,
                candidate_value,
                key=child_key,
            )
            merged[child_key] = merged_value
            changes += child_changes
        return merged, changes

    if isinstance(original, list):
        if not isinstance(candidate, list) or len(candidate) != len(original):
            return original, 0
        merged_items = []
        changes = 0
        for original_item, candidate_item in zip(original, candidate):
            merged_item, child_changes = _merge_shortened_arguments(
                original_item,
                candidate_item,
                key=key,
            )
            merged_items.append(merged_item)
            changes += child_changes
        return merged_items, changes

    if isinstance(original, str):
        if (
            _is_protected_argument_key(key)
            or _contains_math_text(original)
            or not isinstance(candidate, str)
        ):
            return original, 0
        original_text = original.strip()
        original_leading_space = original[: len(original) - len(original.lstrip())]
        candidate_core = candidate.strip()
        if not candidate_core or len(candidate_core) > len(original_text):
            return original, 0
        if candidate_core == original_text:
            return original, 0
        candidate_text = f"{original_leading_space}{candidate_core}"
        return candidate_text, 1

    return original, 0


def _content_argument_inventory(
    value: Any,
    *,
    path: str = "arguments",
    key: str = "",
) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            inventory.extend(
                _content_argument_inventory(
                    child_value,
                    path=f"{path}.{child_key}",
                    key=child_key,
                )
            )
    elif isinstance(value, list):
        for index, child_value in enumerate(value):
            inventory.extend(
                _content_argument_inventory(
                    child_value,
                    path=f"{path}[{index}]",
                    key=key,
                )
            )
    elif (
        isinstance(value, str)
        and not _is_protected_argument_key(key)
    ):
        inventory.append(
            {
                "path": path,
                "characters": len(value),
                "protected_math": _contains_math_text(value),
                "text": value,
            }
        )
    return inventory


def _slide_rewrite_prompt(
    state: State,
    records: list[dict[str, Any]],
    tool_call: dict[str, Any],
    round_number: int,
) -> list[dict[str, str]]:
    arguments = tool_call.get("arguments") or {}
    boxes = [
        {
            "id": record["id"],
            "text": record["text"],
            "x": record["x"],
            "y": record["y"],
            "width": record["width"],
            "height": record["height"],
            "line_count": record["line_count"],
            "max_lines": record["max_lines"],
            "reasons": record["reasons"],
            "overflow": record["overflow"],
            "has_math_field": record["has_math_field"],
        }
        for record in records
    ]
    inventory = _content_argument_inventory(arguments)

    return [
        {
            "role": "system",
            "content": (
                "You are a strict presentation editor repairing one complete slide. "
                "Read every textbox and every editable content field, then rewrite and "
                "balance the slide copy as one coherent whole, never as an isolated fix "
                "for only the textbox reported as overflowing. Shorten content "
                "proportionally across related fields so the visual hierarchy remains "
                "balanced and every textbox can fit after the "
                "same slide generator recalculates its layout. Preserve the original "
                "language, facts, numbers, names, intent, and ordering. Keep concise "
                "labels concise. Never add claims, markdown, bullets, or commentary. "
                "Do not change URLs, colors, image/icon choices, visual settings, object "
                "keys, list lengths, or mathematical expressions. Return JSON only as "
                "{\"arguments\": <the complete revised arguments object>}."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "task": (
                        "Inspect the complete slide first, compare the relative emphasis "
                        "of every textbox, and rewrite all editable content fields together. "
                        "Shorten the longest or most space-consuming related fields "
                        "proportionally; keep an already concise label unchanged only when "
                        "it helps the hierarchy. Never summarize just the overflowing box. "
                        "Boxes outside the slide indicate that the surrounding content "
                        "also needs shortening so the generator can recalculate a compact layout."
                    ),
                    "round": round_number,
                    "tool_name": tool_call.get("name"),
                    "source_slide_content": state.get("current_slide_text", ""),
                    "textboxes": boxes,
                    "editable_content_inventory": inventory,
                    "current_arguments": arguments,
                },
                ensure_ascii=False,
            ),
        },
    ]


def _call_slide_rewriter(
    llm: Any,
    state: State,
    records: list[dict[str, Any]],
    tool_call: dict[str, Any],
    round_number: int,
    request_limiter=None,
) -> dict[str, Any] | None:
    messages = _slide_rewrite_prompt(
        state,
        records,
        tool_call,
        round_number,
    )
    try:
        if hasattr(llm, "generate_completion"):
            if request_limiter is None:
                response = llm.generate_completion(
                    messages=messages,
                    temperature=0.2,
                )
            else:
                with request_limiter.slot():
                    response = llm.generate_completion(
                        messages=messages,
                        temperature=0.2,
                    )
        elif hasattr(llm, "invoke"):
            if request_limiter is None:
                response = llm.invoke(messages)
            else:
                with request_limiter.slot():
                    response = llm.invoke(messages)
        else:
            logger.warning("Whole-slide overflow rewrite skipped: LLM has no invoke method")
            return None
    except Exception as exc:
        logger.warning("Whole-slide overflow rewrite failed: %s", exc)
        return None

    arguments = _parse_slide_rewrite(response)
    if arguments is None:
        logger.warning("Whole-slide overflow rewriter returned no arguments JSON")
    return arguments


def _preserve_transition_attributes(
    source_root: ET.Element,
    target_root: ET.Element,
) -> None:
    source_slides = [
        node
        for node in source_root
        if node.tag.rsplit("}", 1)[-1].lower() == "slide"
    ]
    target_slides = [
        node
        for node in target_root
        if node.tag.rsplit("}", 1)[-1].lower() == "slide"
    ]
    for source_slide, target_slide in zip(source_slides, target_slides):
        for name, value in source_slide.attrib.items():
            if name.startswith("transition"):
                target_slide.set(name, value)


def _regenerate_slide(
    tool_call: dict[str, Any],
    *,
    source_content: str,
    previous_root: ET.Element,
) -> ET.Element | None:
    tool_name = canonical_tool_name(str(tool_call.get("name") or ""))
    tool = get_tool_by_name(tool_name)
    if tool is None:
        logger.warning("Cannot regenerate overflow slide: unknown tool %s", tool_name)
        return None

    arguments = normalize_tool_arguments(
        tool_name,
        tool_call.get("arguments") or {},
    )
    schema = getattr(tool, "args_schema", None)
    if schema is not None and hasattr(schema, "model_validate"):
        try:
            schema.model_validate(arguments)
        except Exception as exc:
            logger.warning("Whole-slide rewrite produced invalid tool arguments: %s", exc)
            return None

    normalized_tool_call = {
        **tool_call,
        "name": tool_name,
        "arguments": arguments,
    }
    xml_content = execute_xml_tool(
        normalized_tool_call,
        source_content=source_content,
    )
    if not xml_content:
        logger.warning("Whole-slide generator returned empty XML")
        return None
    try:
        target_root = ET.fromstring(xml_content)
    except ET.ParseError as exc:
        logger.warning("Whole-slide generator returned invalid XML: %s", exc)
        return None
    if target_root.tag.rsplit("}", 1)[-1].lower() != "presentation":
        logger.warning("Whole-slide generator did not return a presentation root")
        return None
    if any(
        (node.text or "").strip() == "Slide content is temporarily unavailable"
        for node in target_root.iter()
    ):
        logger.warning("Whole-slide generator fell back instead of regenerating the slide")
        return None

    _preserve_transition_attributes(previous_root, target_root)
    return target_root


def _merge_browser_measurement(
    records: list[dict[str, Any]],
    browser_report: dict[str, Any],
) -> None:
    browser_boxes = browser_report.get("boxes") or []
    browser_by_id = {box.get("id"): box for box in browser_boxes if box.get("id")}

    for index, record in enumerate(records):
        browser_box = browser_by_id.get(record["id"])
        if browser_box is None and index < len(browser_boxes):
            # XML elements without explicit ids receive different generated
            # ids in Python and React. Their traversal order is stable, so use
            # position as the fallback join key.
            browser_box = browser_boxes[index]
        if not browser_box:
            continue

        xml_reasons = set(record.get("reasons") or [])
        browser_reasons = set(browser_box.get("reasons") or [])
        # The React preview deliberately expands and clamps textboxes for
        # editing. Keep source-XML boundary failures so that this visual
        # convenience cannot hide a box whose actual geometry is off-slide.
        if "slide_boundary" in xml_reasons:
            browser_reasons.add("slide_boundary")

        record["measurement_source"] = "playwright"
        record["overflow"] = bool(browser_reasons)
        record["reasons"] = sorted(browser_reasons)
        record["line_count"] = int(browser_box.get("line_count") or record["line_count"])
        if browser_box.get("max_lines") is not None:
            record["max_lines"] = browser_box["max_lines"]
        record["has_math_field"] = bool(record["has_math_field"] or browser_box.get("has_math_field"))
        record["rewrite_possible"] = (
            "slide_boundary" not in record["reasons"]
            and (
                "text_width" in record["reasons"]
                or "max_lines" in record["reasons"]
                or ("text_height" in record["reasons"] and record["line_count"] > 1)
            )
        )


async def _analyze_current_xml(
    root: ET.Element,
    xml_content: str,
    capture_provider: Any,
    *,
    force_browser: bool = False,
) -> tuple[list[dict[str, Any]], str]:
    # Overflow validation intentionally stays on the deterministic XML/Pillow
    # path. Opening Chromium for every rewrite is expensive and the XML
    # geometry is the persisted artifact that the workflow must keep valid.
    # ``capture_provider`` and ``force_browser`` remain in the signature for
    # compatibility with callers that provide the old measurement options.
    del xml_content, capture_provider, force_browser
    return analyze_xml_root(root), "pillow"


async def resolve_text_overflow(state: State, config: dict[str, Any]) -> State:
    """Rewrite an overflowing slide as a whole, regenerate it, then re-measure."""
    xml_content = state.get("current_xml_content", "")
    state["overflow_rewrite_count"] = 0
    state["overflow_failed"] = False
    state["overflow_report"] = {
        "checked_boxes": 0,
        "overflowing_boxes": 0,
        "boxes": [],
        "rounds": 0,
        "llm_calls": 0,
        "measurement_source": "pillow",
        "status": "empty_xml",
    }
    if not xml_content:
        logger.warning("Overflow resolver skipped: XML content is empty")
        return state

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as exc:
        logger.warning("Overflow resolver skipped: invalid XML: %s", exc)
        state["overflow_report"]["status"] = "invalid_xml"
        return state

    configurable = config.get("configurable", {}) if config else {}
    llm = configurable.get("llm")
    max_rounds = max(0, int(configurable.get("text_overflow_max_rounds", TEXT_OVERFLOW_MAX_ROUNDS)))
    rewrite_count = 0
    llm_calls = 0
    protected_math_field_ids: set[str] = set()
    skipped_unfixable = 0
    rounds_completed = 0

    measurement_source = "pillow"
    records: list[dict[str, Any]] = []
    for round_number in range(1, max_rounds + 1):
        current_xml = ET.tostring(root, encoding="unicode")
        records, measurement_source = await _analyze_current_xml(
            root,
            current_xml,
            None,
        )
        overflowing = [record for record in records if record["overflow"]]
        rounds_completed = round_number
        logger.info(
            "XML overflow rules: slide=%s checked_boxes=%s overflowing_boxes=%s round=%s",
            state.get("current_slide_index", 0) + 1,
            len(records),
            len(overflowing),
            round_number,
        )

        if not overflowing:
            break

        protected_math_field_ids.update(
            record["id"]
            for record in records
            if record["has_math_field"]
        )

        if llm is None:
            logger.warning(
                "Whole-slide overflow rewrite skipped: no LLM is configured"
            )
            skipped_unfixable += len(overflowing)
            break

        tool_call = state.get("current_tool_call") or {}
        original_arguments = tool_call.get("arguments")
        if not tool_call.get("name") or not isinstance(original_arguments, dict):
            logger.warning(
                "Whole-slide overflow rewrite skipped: current tool call is unavailable"
            )
            skipped_unfixable += len(overflowing)
            break

        llm_calls += 1
        rewriter_kwargs = {}
        if configurable.get("llm_request_limiter") is not None:
            rewriter_kwargs["request_limiter"] = configurable["llm_request_limiter"]
        candidate_arguments = _call_slide_rewriter(
            llm,
            state,
            records,
            tool_call,
            round_number,
            **rewriter_kwargs,
        )
        if candidate_arguments is None:
            skipped_unfixable += len(overflowing)
            break

        merged_arguments, changed_fields = _merge_shortened_arguments(
            original_arguments,
            candidate_arguments,
        )
        if changed_fields <= 0:
            logger.warning(
                "Whole-slide overflow rewriter did not shorten any safe content field"
            )
            skipped_unfixable += len(overflowing)
            break

        revised_tool_call = {
            **tool_call,
            "arguments": merged_arguments,
        }
        regenerated_root = _regenerate_slide(
            revised_tool_call,
            source_content=state.get("current_slide_text", ""),
            previous_root=root,
        )
        if regenerated_root is None:
            skipped_unfixable += len(overflowing)
            break

        root = regenerated_root
        rewrite_count += changed_fields
        revised_tool_call = {
            **revised_tool_call,
            "name": canonical_tool_name(revised_tool_call.get("name")),
            "arguments": normalize_tool_arguments(
                revised_tool_call.get("name"),
                revised_tool_call.get("arguments") or {},
            ),
        }
        state["current_tool_call"] = revised_tool_call

        current_plan = state.get("current_tool_plan")
        if isinstance(current_plan, list):
            replaced = False
            revised_plan = []
            for call in current_plan:
                if (
                    not replaced
                    and isinstance(call, dict)
                    and canonical_tool_name(call.get("name"))
                    == revised_tool_call.get("name")
                ):
                    revised_plan.append(revised_tool_call)
                    replaced = True
                else:
                    revised_plan.append(call)
            state["current_tool_plan"] = revised_plan

        logger.info(
            "Regenerated overflowing slide %s after harmonizing %s content fields",
            state.get("current_slide_index", 0) + 1,
            changed_fields,
        )

    state["current_xml_content"] = ET.tostring(root, encoding="unicode")
    state["last_valid_xml_content"] = state["current_xml_content"]
    current_tool_call = state.get("current_tool_call") or {}
    if current_tool_call.get("name") not in {"PARSE_ERROR", "default_fallback"}:
        state["last_valid_tool_call"] = current_tool_call
    # A rewrite may happen on the last allowed round.  ``records`` then still
    # describes the XML from before that rewrite; using it here reports a stale
    # overflow and can fail an otherwise repaired slide.  Always measure the
    # final regenerated root before deciding whether overflow remains.
    final_records, measurement_source = await _analyze_current_xml(
        root,
        state["current_xml_content"],
        None,
    )
    report = public_overflow_report(final_records)
    report.update(
        {
            "rounds": rounds_completed,
            "llm_calls": llm_calls,
            "rewrites": rewrite_count,
            # Formula boxes still participate in whole-slide repair. Only the
            # expressions themselves are immutable while layout is rebuilt.
            "protected_math_fields": len(protected_math_field_ids),
            "skipped_math_fields": 0,
            "skipped_unfixable": skipped_unfixable,
            "measurement_source": measurement_source,
            "status": "ok" if not any(record["overflow"] for record in final_records) else "overflow_remaining",
        }
    )
    state["overflow_rewrite_count"] = rewrite_count
    state["overflow_report"] = report
    remaining_overflow = report["overflowing_boxes"]
    if remaining_overflow:
        retry_count = int(state.get("overflow_retry_count", 0))
        logger.error(
            "SLIDE OVERFLOW FAILURE: slide=%s remaining_overflow=%s "
            "measurement=%s retry=%s/%s",
            state.get("current_slide_index", 0) + 1,
            remaining_overflow,
            measurement_source,
            retry_count,
            EXECUTOR_MAX_RETRIES,
        )
        if retry_count >= EXECUTOR_MAX_RETRIES:
            # Overflow is a quality warning, not a workflow-fatal error. Keep
            # the best regenerated XML, mark the report explicitly, and let
            # the graph render/finalize this slide before moving on.
            report["status"] = "accepted_with_overflow"
            report["accepted_with_overflow"] = True
            state["overflow_report"] = report
            state["overflow_failed"] = False
            logger.warning(
                "Accepting slide %s with %s overflowing textbox(es) after "
                "retries; continuing workflow",
                state.get("current_slide_index", 0) + 1,
                remaining_overflow,
            )
        else:
            state["overflow_failed"] = True
            state["overflow_retry_count"] = retry_count + 1
            state["retry_count"] = int(state.get("retry_count", 0)) + 1
            overflowing_tool = canonical_tool_name(
                (state.get("current_tool_call") or {}).get("name")
            )
            excluded = list(state.get("overflow_excluded_tools") or [])
            if overflowing_tool and overflowing_tool not in excluded:
                excluded.append(overflowing_tool)
            state["overflow_excluded_tools"] = excluded
            state["executor_decision"] = "fail"
            state["executor_feedback"] = (
                "WHOLE-SLIDE OVERFLOW VALIDATION FAILED. Read the complete slide "
                "content and regenerate the slide with all textual fields shortened "
                "proportionally and harmoniously. The previous layout could not fit after "
                "whole-slide repair, so use a different available XML layout with more "
                "suitable space. Preserve facts, "
                "numbers, names, images, colors, list structure, and mathematical expressions. "
                "No textbox may exceed its bounds or the slide boundary. "
                f"Remaining overflowing boxes: {remaining_overflow}."
            )
    else:
        state["overflow_failed"] = False

    logger.info(
        "XML overflow resolver completed: slide=%s rewrites=%s remaining_overflow=%s "
        "measurement=%s",
        state.get("current_slide_index", 0) + 1,
        rewrite_count,
        remaining_overflow,
        measurement_source,
    )
    return state
