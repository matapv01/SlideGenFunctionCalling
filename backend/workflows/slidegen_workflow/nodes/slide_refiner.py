"""Phase-two slide planner that reconciles approved visual evidence."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from backend.config import PLANNER_MAX_CONCURRENCY, PLANNING_BATCH_SIZE
from backend.workflows.slidegen_workflow.graph.stage import (
    SlideRefinementBatch,
    State,
)

logger = logging.getLogger(__name__)

_REFINER_SYSTEM_PROMPT = """
You are the final presentation-content planner. Reconcile an existing slide
plan with zero or more verified visual assets.

Rules:
- Preserve facts, names, dates, claims, and the user's intended meaning from the
  source content. Never invent a fact from an image.
- Use visual notes only to explain how an approved image supports the slide,
  how it may be captioned, or where it belongs.
- If no image is approved, produce a clear no-image composition request. Do not
  request another image and do not mention a search provider.
- If an image is approved, adapt only the wording or hierarchy needed to make
  the image and message coherent. Do not turn a decorative image into evidence.
- Keep the final content concise and presentation-ready while retaining the
  source meaning. Return one refinement for each input slide, in order.
- `retrieval_query` is a short factual query for a final document retrieval
  pass. Use an empty string when the supplied slide content is already enough.
- Return only the structured response; do not return markdown or commentary.
"""

_REFINER_HUMAN_PROMPT = """
DECK TOPIC:
{deck_topic}

DECK OUTLINE:
{deck_outline}

PRESENTATION INSTRUCTION:
{presentation_instruction}

SLIDES TO REFINE (JSON):
{slides}
"""


def _as_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return dict(value or {}) if isinstance(value, dict) else {}


def _content_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        values: list[str] = []
        for value in content.values():
            if isinstance(value, (str, int, float)):
                values.append(str(value))
            elif isinstance(value, list):
                values.extend(str(item) for item in value if isinstance(item, (str, int, float)))
        return "\n".join(values)
    if isinstance(content, list):
        return "\n".join(_content_text(item) for item in content)
    return str(content or "")


def _deck_outline(state: State) -> str:
    return "\n".join(
        str(item).strip()
        for item in state.get("slide_context_maps") or []
        if str(item).strip()
    )[:3500]


def _approved_by_slide(state: State) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = {}
    for image in state.get("approved_image_assignments") or []:
        if not isinstance(image, dict):
            continue
        try:
            index = int(image.get("slide_index", -1))
        except (TypeError, ValueError):
            continue
        if index >= 0:
            grouped.setdefault(index, []).append(image)
    return grouped


def _fallback_refinement(
    index: int,
    content: Any,
    plan: dict[str, Any],
    approved_images: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "slide_index": index,
        "final_content": _content_text(content),
        "visual_layout_request": (
            (
                str(plan.get("visual_layout_request") or "").strip()
                or "Use the approved visual as supporting evidence with a concise caption."
            )
            if approved_images
            else "Use a clear no-image composition with readable hierarchy."
        )[:500],
        "retrieval_query": (
            str(plan.get("slide_topic") or "").strip()[:300]
            if approved_images
            else ""
        ),
        "image_mode": "semantic" if approved_images else "none",
    }


def _invoke_refinement_batch(chain, payload: dict[str, Any], config: RunnableConfig):
    limiter = (config or {}).get("configurable", {}).get("llm_request_limiter")
    if limiter is None:
        return chain.invoke(payload)
    with limiter.slot():
        return chain.invoke(payload)


def refine_slide_plans(state: State, config: RunnableConfig) -> State:
    """Create final content/layout briefs after image verification."""
    print("\n---------------- Executing Node: slide_planner_phase_2 ----------------")
    started = time.perf_counter()
    chunks = list(state.get("slide_chunks") or [])
    plans = list(state.get("slide_plans") or [])
    if not chunks:
        state["slide_refinements"] = []
        state["slide_final_contents"] = []
        logger.info("Phase-two planner skipped: no slides (%.2fs)", time.perf_counter() - started)
        return state

    configurable = config.get("configurable", {}) if config else {}
    llm = configurable.get("planner_llm") or configurable.get("llm")
    options = state.get("slide_options") or {}
    style = state.get("deck_style_plan") or {}
    grouped_images = _approved_by_slide(state)
    fallback = [
        _fallback_refinement(
            index,
            content,
            plans[index] if index < len(plans) and isinstance(plans[index], dict) else {},
            grouped_images.get(index, []),
        )
        for index, content in enumerate(chunks)
    ]
    # A text-only deck has no visual evidence to reconcile. Reusing the
    # phase-one content and its no-image layout brief avoids an unnecessary
    # second planner request on the common path.
    if not grouped_images:
        logger.info(
            "Phase-two planner skipped: no approved images (%.2fs)",
            time.perf_counter() - started,
        )
        return _apply_refinements(state, fallback, grouped_images)
    if llm is None:
        logger.info(
            "Phase-two planner skipped: no planner provider (%.2fs)",
            time.perf_counter() - started,
        )
        return _apply_refinements(state, fallback, grouped_images)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _REFINER_SYSTEM_PROMPT),
            ("human", _REFINER_HUMAN_PROMPT),
        ]
    )
    chain = prompt | llm.with_structured_output(SlideRefinementBatch)
    # Slides without approved images already have a deterministic no-image
    # fallback. Refine only slides that actually gained visual evidence; this
    # avoids spending planner calls on unchanged text-only slides.
    refinement_indices = [
        index
        for index in sorted(grouped_images)
        if 0 <= index < len(chunks)
    ]
    batch_payloads: list[tuple[list[int], dict[str, Any]]] = []
    for start in range(0, len(refinement_indices), PLANNING_BATCH_SIZE):
        batch_indices = refinement_indices[start : start + PLANNING_BATCH_SIZE]
        slides = []
        for index in batch_indices:
            plan = plans[index] if index < len(plans) else {}
            images = grouped_images.get(index, [])
            slides.append(
                {
                    "slide_index": index,
                    "source_content": _content_text(chunks[index])[:5000],
                    "phase_1_plan": plan,
                    "approved_images": [
                        {
                            "source_id": image.get("source_id"),
                            "source_type": image.get("source_type"),
                            "source_url": image.get("source_url"),
                            "source_path": image.get("source_path"),
                            "role": image.get("role"),
                            "visual_notes": image.get("visual_notes"),
                            "caption_hint": image.get("caption_hint"),
                            "placement_hint": image.get("placement_hint"),
                        }
                        for image in images
                    ],
                }
            )
        batch_payloads.append(
            (
                batch_indices,
                {
                    "deck_topic": str(
                        style.get("deck_topic") or state.get("document_title") or ""
                    ),
                    "deck_outline": _deck_outline(state),
                    "presentation_instruction": str(
                        options.get("presentation_instruction") or ""
                    ),
                    "slides": json.dumps(slides, ensure_ascii=False, default=str),
                },
            )
        )

    refinements: list[dict[str, Any]] = []
    try:
        def invoke_payload(item: tuple[list[int], dict[str, Any]]) -> list[dict[str, Any]]:
            batch_indices, payload = item
            result = _invoke_refinement_batch(chain, payload, config)
            raw = _as_dict(result).get("refinements")
            if not isinstance(raw, list) or len(raw) != len(batch_indices):
                raise ValueError("phase-two planner returned an incomplete batch")
            normalized: list[dict[str, Any]] = []
            for fallback_index, refinement in zip(batch_indices, raw):
                item_dict = _as_dict(refinement)
                item_dict.setdefault("slide_index", fallback_index)
                normalized.append(item_dict)
            return normalized

        # The shared request limiter still caps total LLM pressure. Running
        # independent phase-two batches concurrently removes an avoidable
        # serial wait when a deck has many image-backed slides.
        with ThreadPoolExecutor(
            max_workers=min(
                max(1, int(PLANNER_MAX_CONCURRENCY)),
                max(1, len(batch_payloads)),
            )
        ) as executor:
            for batch_refinements in executor.map(invoke_payload, batch_payloads):
                refinements.extend(batch_refinements)
    except Exception as exc:
        if configurable.get("strict_grpo_preprocessing"):
            raise RuntimeError("Slide refinement failed during GRPO corpus rebuild") from exc
        logger.warning("Phase-two planner failed; preserving phase-one plans: %s", exc)
        logger.info("Phase-two planner fallback completed in %.2fs", time.perf_counter() - started)
        return _apply_refinements(state, fallback, grouped_images)

    normalized: list[dict[str, Any]] = []
    by_index: dict[int, dict[str, Any]] = {}
    for fallback_index, item in enumerate(refinements):
        if not isinstance(item, dict):
            continue
        try:
            slide_index = int(item.get("slide_index", fallback_index))
        except (TypeError, ValueError):
            continue
        if 0 <= slide_index < len(chunks):
            by_index[slide_index] = item
    for index, fallback_item in enumerate(fallback):
        item = dict(fallback_item)
        candidate = by_index.get(index) or {}
        item["slide_index"] = index
        item["final_content"] = str(candidate.get("final_content") or item["final_content"]).strip()
        item["visual_layout_request"] = str(
            candidate.get("visual_layout_request") or item["visual_layout_request"]
        ).strip()[:500]
        item["retrieval_query"] = str(candidate.get("retrieval_query") or "").strip()[:300]
        item["image_mode"] = "semantic" if grouped_images.get(index) else "none"
        normalized.append(item)
    logger.info(
        "Phase-two planner completed in %.2fs (%d image-backed slides)",
        time.perf_counter() - started,
        len(refinement_indices),
    )
    return _apply_refinements(state, normalized, grouped_images)


def _apply_refinements(
    state: State,
    refinements: list[dict[str, Any]],
    grouped_images: dict[int, list[dict[str, Any]]],
) -> State:
    plans = [dict(item) if isinstance(item, dict) else {} for item in state.get("slide_plans") or []]
    final_contents: list[str] = []
    for index, refinement in enumerate(refinements):
        content = str(refinement.get("final_content") or "").strip()
        final_contents.append(content)
        if index >= len(plans):
            plans.append({})
        plans[index].update(
            {
                "final_content": content,
                "retrieval_query": str(refinement.get("retrieval_query") or "").strip()[:300],
                "visual_layout_request": str(
                    refinement.get("visual_layout_request") or ""
                ).strip()[:500],
                "image_mode": "semantic" if grouped_images.get(index) else "none",
                "image_search_intents": [],
                "approved_image_ids": [
                    str(image.get("source_id") or "")
                    for image in grouped_images.get(index, [])
                ],
            }
        )
    state["slide_plans"] = plans
    state["slide_refinements"] = refinements
    state["slide_final_contents"] = final_contents
    return state
