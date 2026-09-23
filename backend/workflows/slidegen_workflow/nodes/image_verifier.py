"""Verify document and search images before the final slide plan."""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from langchain_core.runnables import RunnableConfig

from backend.config import VLM_REQUEST_MAX_CONCURRENCY
from backend.workflows.slidegen_workflow.graph.stage import State

logger = logging.getLogger(__name__)


def _slide_context(state: State, index: int) -> dict[str, str]:
    chunks = list(state.get("slide_chunks") or [])
    plans = list(state.get("slide_plans") or [])
    chunk = chunks[index] if index < len(chunks) else {}
    plan = plans[index] if index < len(plans) and isinstance(plans[index], dict) else {}
    if isinstance(chunk, dict):
        title = str(chunk.get("title") or chunk.get("heading") or "")
        content = str(chunk.get("content") or chunk.get("body") or "")
    else:
        title = ""
        content = str(chunk or "")
    return {
        "slide_content": content[:3000],
        "slide_topic": str(plan.get("slide_topic") or title)[:500],
        "slide_purpose": str(plan.get("slide_purpose") or "")[:900],
        "visual_layout_request": str(plan.get("visual_layout_request") or "")[:500],
    }


def _deck_context(state: State) -> dict[str, str]:
    options = state.get("slide_options") or {}
    style = state.get("deck_style_plan") or {}
    outline = "\n".join(
        str(item).strip()
        for item in (state.get("slide_context_maps") or [])
        if str(item).strip()
    )[:3500]
    return {
        "deck_topic": str(style.get("deck_topic") or state.get("document_title") or "")[:900],
        "deck_outline": outline,
        "presentation_instruction": str(options.get("presentation_instruction") or "")[:1400],
    }


def _verify_search_group(
    verifier,
    group: dict[str, Any],
    state: State,
) -> list[dict[str, Any]]:
    slide_index = int(group.get("slide_index", -1))
    candidates = [
        item for item in group.get("candidates") or []
        if isinstance(item, dict) and str(item.get("source_url") or "").strip()
    ]
    if slide_index < 0 or not candidates:
        return []

    slide = _slide_context(state, slide_index)
    deck = _deck_context(state)
    urls = [str(item["source_url"]) for item in candidates]
    result = verifier.verify_search_candidates(
        candidates=urls,
        query=str(group.get("query") or ""),
        slide_content=slide["slide_content"],
        target_description=str(group.get("role") or "illustration"),
        presentation_instruction=deck["presentation_instruction"],
        slide_topic=slide["slide_topic"],
        slide_purpose=slide["slide_purpose"],
        deck_topic=deck["deck_topic"],
        deck_outline=deck["deck_outline"],
        rendered_slide_content=slide["slide_content"],
    )
    if not result or not result.get("available"):
        return []

    by_url = {str(item["source_url"]): item for item in candidates}
    decisions = {
        str(item.get("url")): item
        for item in result.get("decisions") or []
        if isinstance(item, dict) and item.get("url")
    }
    assignments: list[dict[str, Any]] = []
    for url in result.get("approved") or []:
        candidate = by_url.get(str(url))
        if not candidate:
            continue
        decision = decisions.get(str(url), {})
        try:
            confidence = float(decision.get("confidence") or 0)
        except (TypeError, ValueError):
            confidence = 0.0
        assignments.append(
            {
                **candidate,
                "slide_index": slide_index,
                "query": str(group.get("query") or ""),
                "role": str(group.get("role") or "illustration"),
                "visual_notes": str(decision.get("reason") or "")[:500],
                "caption_hint": str(decision.get("caption_hint") or "")[:300],
                "placement_hint": str(decision.get("placement_hint") or "")[:300],
                "confidence": confidence,
            }
        )
    return assignments[:1]


def _verify_document_images(verifier, state: State) -> list[dict[str, Any]]:
    options = state.get("slide_options") or {}
    images = list(state.get("document_images") or options.get("document_images") or [])
    if not images or not state.get("slide_chunks"):
        return []
    deck = _deck_context(state)
    try:
        assignments = verifier.assign_document_images(
            images=images,
            slide_chunks=list(state.get("slide_chunks") or []),
            user_request=str(state.get("user_request") or options.get("user_request") or ""),
            slide_plans=list(state.get("slide_plans") or []),
            deck_topic=deck["deck_topic"],
            deck_outline=deck["deck_outline"],
            presentation_instruction=deck["presentation_instruction"],
        )
    except Exception:
        logger.exception("Document image verification failed")
        return []
    normalized: list[dict[str, Any]] = []
    for item in assignments or []:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                **item,
                "source_type": "document",
                "source_id": str(item.get("image_id") or item.get("content_hash") or ""),
                "visual_notes": str(item.get("reason") or "")[:500],
                "caption_hint": str(item.get("caption_hint") or "")[:300],
                "placement_hint": str(item.get("placement_hint") or "")[:300],
            }
        )
    return normalized


def verify_slide_images(state: State, config: RunnableConfig) -> State:
    """Verify every image source selected before planner phase two.

    Search candidates and embedded DOCX assets share one output contract. No
    image is approved by default: unavailable, rejected, or malformed inputs
    simply produce an empty assignment for that slide.
    """
    print("\n---------------- Executing Node: image_verifier ----------------")
    started = time.perf_counter()
    options = dict(state.get("slide_options") or {})
    verifier = (config or {}).get("configurable", {}).get("image_relevance_verifier")
    candidates = list(
        state.get("image_search_candidates")
        or options.get("image_search_candidates")
        or []
    )
    if verifier is None:
        assignments: list[dict[str, Any]] = []
    else:
        jobs = [
            group for group in candidates
            if isinstance(group, dict) and group.get("candidates")
        ]
        assignments = []
        with ThreadPoolExecutor(
            max_workers=min(VLM_REQUEST_MAX_CONCURRENCY, max(1, len(jobs) + 1))
        ) as executor:
            futures = [
                executor.submit(_verify_search_group, verifier, group, state)
                for group in jobs
            ]
            document_future = executor.submit(_verify_document_images, verifier, state)
            for future in as_completed([*futures, document_future]):
                try:
                    assignments.extend(future.result())
                except Exception:
                    logger.exception("Image verification worker failed")

    assignments.sort(
        key=lambda item: (
            int(item.get("slide_index", 0)),
            str(item.get("source_type") or ""),
            str(item.get("source_id") or item.get("source_url") or ""),
        )
    )
    state["approved_image_assignments"] = assignments
    state["document_image_assignments"] = [
        item for item in assignments if item.get("source_type") == "document"
    ]
    options["approved_image_assignments"] = assignments
    options["document_image_assignments"] = state["document_image_assignments"]
    state["slide_options"] = options
    print(f"  -> Approved {len(assignments)} image assignment(s)")
    logger.info(
        "Image verification completed in %.2fs (%d assignments)",
        time.perf_counter() - started,
        len(assignments),
    )
    return state
