"""Rule-based XML overflow resolver with bounded LLM summarization."""

from __future__ import annotations

import json
import inspect
import logging
import re
import xml.etree.ElementTree as ET
from typing import Any

from backend.config import (
    EXECUTOR_MAX_RETRIES,
    TEXT_OVERFLOW_MAX_BOXES_PER_ROUND,
    TEXT_OVERFLOW_MAX_ROUNDS,
)
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.utils.xml_overflow import (
    analyze_xml_root,
    public_overflow_report,
)

logger = logging.getLogger(__name__)
_MATH_MARKER_RE = re.compile(r"<\s*/?\s*math-field\b", re.IGNORECASE)


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


def _parse_summary(response: Any) -> str | None:
    raw = _response_text(response)
    if not raw:
        return None

    cleaned = raw.strip()
    if "```" in cleaned:
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE | re.DOTALL).strip()

    candidates = [cleaned]
    object_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if object_match:
        candidates.insert(0, object_match.group(0))

    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue

        if isinstance(payload, dict):
            value = payload.get("text") or payload.get("summary") or payload.get("rewritten_text")
            if isinstance(value, str) and value.strip():
                return value.strip()
        elif isinstance(payload, str) and payload.strip():
            return payload.strip()
    return None


def _summary_prompt(record: dict[str, Any], round_number: int) -> list[dict[str, str]]:
    current_text = record["text"]
    width_ratio = min(1.0, record["available_width"] / max(1.0, record["max_line_width"]))
    height_ratio = min(1.0, record["available_height"] / max(1.0, record["required_height"]))
    pressure_ratio = max(0.25, min(width_ratio, height_ratio))
    target_chars = max(12, int(len(current_text) * pressure_ratio * 0.82))
    max_lines = record["max_lines"] or max(1, int(record["available_height"] / max(1.0, record["required_height"] / max(1, record["line_count"]))))

    return [
        {
            "role": "system",
            "content": (
                "You are a strict slide copy editor. Shorten text only when it is too large "
                "for its existing XML textbox. Preserve the original language, key facts, names, "
                "numbers, and intent. Do not add claims, markdown, bullets, or commentary. "
                "Return JSON only in the form {\"text\": \"shortened text\"}."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "task": "Summarize this textbox so it fits without changing its font size.",
                    "round": round_number,
                    "overflow_reasons": record["reasons"],
                    "current_line_count": record["line_count"],
                    "allowed_lines": max_lines,
                    "approximate_target_characters": target_chars,
                    "text": current_text,
                },
                ensure_ascii=False,
            ),
        },
    ]


def _call_summarizer(llm: Any, record: dict[str, Any], round_number: int) -> str | None:
    messages = _summary_prompt(record, round_number)
    try:
        if hasattr(llm, "generate_completion"):
            response = llm.generate_completion(
                messages=messages,
                temperature=0.2,
            )
        elif hasattr(llm, "invoke"):
            response = llm.invoke(messages)
        else:
            logger.warning("Overflow resolver skipped: configured LLM has no invoke method")
            return None
    except Exception as exc:
        logger.warning("Overflow summarization failed for %s: %s", record["id"], exc)
        return None

    candidate = _parse_summary(response)
    if not candidate:
        logger.warning("Overflow summarizer returned no JSON text for %s", record["id"])
        return None

    original = record["text"].strip()
    if candidate.strip() == original or len(candidate.strip()) >= len(original):
        logger.warning("Overflow summarizer did not shorten textbox %s", record["id"])
        return None
    return candidate.strip()


def _replace_plain_text(element: ET.Element, replacement: str) -> bool:
    """Replace text while preserving textbox attributes and avoiding math loss."""
    if (
        any(child.tag.rsplit("}", 1)[-1].lower() == "math-field" for child in element)
        or _MATH_MARKER_RE.search("".join(element.itertext()))
    ):
        return False

    children = list(element)
    run_children = [
        child for child in children if child.tag.rsplit("}", 1)[-1].lower() == "run"
    ]
    if run_children:
        # Keep the first run's visual style (highlight/bold/color) instead of
        # dropping all rich-text formatting when the copy is rewritten.
        first_run = run_children[0]
        first_run.text = replacement
        first_run.tail = None
        for child in children:
            if child is not first_run:
                element.remove(child)
        element.text = None
        return True

    for child in children:
        element.remove(child)
    element.text = replacement
    return True


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

        record["measurement_source"] = "playwright"
        record["overflow"] = bool(browser_box.get("overflow"))
        record["reasons"] = list(browser_box.get("reasons") or [])
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
    records = analyze_xml_root(root)
    # XML/Pillow is the fast path. Only open a browser when XML already finds
    # a candidate or when a rewrite must be verified against the real DOM.
    if not force_browser and not any(record["overflow"] for record in records):
        return records, "xml"

    measure_overflow = getattr(capture_provider, "measure_xml_overflow", None)
    if not callable(measure_overflow):
        return records, "pillow"

    try:
        browser_report = measure_overflow(xml_content, slide_index=0)
        if inspect.isawaitable(browser_report):
            browser_report = await browser_report
        _merge_browser_measurement(records, browser_report or {})
        return records, "playwright"
    except Exception as exc:
        # Keep the deterministic fallback for tests and degraded environments.
        # The final render still uses the same Playwright provider and will
        # surface a hard error if the preview itself is unavailable.
        logger.warning("Playwright overflow measurement failed; using XML fallback: %s", exc)
        return records, "pillow"


async def resolve_text_overflow(state: State, config: dict[str, Any]) -> State:
    """Filter XML text boxes, rewrite only overflowing text, then re-measure."""
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
    capture_provider = configurable.get("capture_provider")
    max_rounds = max(0, int(configurable.get("text_overflow_max_rounds", TEXT_OVERFLOW_MAX_ROUNDS)))
    max_boxes = max(1, int(configurable.get("text_overflow_max_boxes", TEXT_OVERFLOW_MAX_BOXES_PER_ROUND)))
    rewrite_count = 0
    llm_calls = 0
    skipped_math_fields = 0
    skipped_unfixable = 0
    rounds_completed = 0

    measurement_source = "xml"
    force_browser = False
    records: list[dict[str, Any]] = []
    for round_number in range(1, max_rounds + 1):
        current_xml = ET.tostring(root, encoding="unicode")
        records, measurement_source = await _analyze_current_xml(
            root,
            current_xml,
            capture_provider,
            force_browser=force_browser,
        )
        force_browser = False
        overflowing = [record for record in records if record["overflow"]]
        rounds_completed = round_number
        logger.info(
            "XML overflow rules: slide=%s checked_boxes=%s overflowing_boxes=%s round=%s",
            state.get("current_slide_index", 0) + 1,
            len(records),
            len(overflowing),
            round_number,
        )

        if not overflowing or llm is None:
            if overflowing and llm is None:
                logger.warning("XML overflow found but no LLM is configured; keeping original text")
            break

        changed = 0
        for record in overflowing[:max_boxes]:
            if record["has_math_field"]:
                skipped_math_fields += 1
                logger.info("Skipping overflow rewrite for math textbox %s", record["id"])
                continue
            if not record["rewrite_possible"]:
                skipped_unfixable += 1
                logger.info(
                    "Skipping overflow rewrite for textbox %s: geometry cannot be fixed by shortening (%s)",
                    record["id"],
                    ", ".join(record["reasons"]),
                )
                continue

            llm_calls += 1
            replacement = _call_summarizer(llm, record, round_number)
            if replacement and _replace_plain_text(record["_element"], replacement):
                changed += 1
                rewrite_count += 1
                logger.info(
                    "Shortened overflowing textbox %s: %s -> %s chars",
                    record["id"],
                    len(record["text"]),
                    len(replacement),
                )

        if not changed:
            break
        # The XML has changed, so the next pass must validate the result with
        # the actual preview DOM rather than relying on Pillow alone.
        force_browser = True

    state["current_xml_content"] = ET.tostring(root, encoding="unicode")
    if force_browser:
        final_records, measurement_source = await _analyze_current_xml(
            root,
            state["current_xml_content"],
            capture_provider,
            force_browser=True,
        )
    else:
        final_records = records or analyze_xml_root(root)
    report = public_overflow_report(final_records)
    report.update(
        {
            "rounds": rounds_completed,
            "llm_calls": llm_calls,
            "rewrites": rewrite_count,
            "skipped_math_fields": skipped_math_fields,
            "skipped_unfixable": skipped_unfixable,
            "measurement_source": measurement_source,
            "status": "ok" if not any(record["overflow"] for record in final_records) else "overflow_remaining",
        }
    )
    state["overflow_rewrite_count"] = rewrite_count
    state["overflow_report"] = report
    remaining_overflow = report["overflowing_boxes"]
    if remaining_overflow:
        retry_count = int(state.get("retry_count", 0))
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
            raise RuntimeError(
                f"Slide {state.get('current_slide_index', 0) + 1} still has "
                f"{remaining_overflow} overflowing textbox(es) after retries"
            )
        state["overflow_failed"] = True
        state["retry_count"] = retry_count + 1
        state["executor_decision"] = "fail"
        state["executor_feedback"] = (
            "TEXT OVERFLOW VALIDATION FAILED. Regenerate the slide with shorter "
            "content or a safer textbox layout. "
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
