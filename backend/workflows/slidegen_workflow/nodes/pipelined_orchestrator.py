"""Build the final slide jobs and generate them concurrently."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Any, Dict, List

from langchain_core.runnables import RunnableConfig

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import (
    _invoke_jobs,
    assign_layouts,
)
from backend.workflows.slidegen_workflow.utils.section_batches import (
    build_slide_jobs,
    group_slide_jobs,
)


def _set_progress_total(config: RunnableConfig, total: int | None) -> None:
    """Publish whether streaming consumers may show a known slide total."""
    tracker = (config or {}).get("configurable", {}).get("parallel_progress_tracker")
    if not tracker:
        return
    lock = tracker.get("lock")
    if lock:
        with lock:
            tracker["total_known"] = total is not None
            if total is None:
                tracker.pop("total_slides", None)
            else:
                tracker["total_slides"] = total
    else:
        tracker["total_known"] = total is not None
        if total is None:
            tracker.pop("total_slides", None)
        else:
            tracker["total_slides"] = total


async def _generate_one_slide(
    job: Dict[str, Any],
    state: State,
    config: RunnableConfig,
) -> List[Dict[str, Any]]:
    result = await _invoke_jobs([deepcopy(job)], state, config)
    return result.get("final_slides", [])


async def plan_and_generate_pipeline(
    state: State,
    config: RunnableConfig,
) -> Dict[str, Any]:
    """Generate the already-planned deck in parallel.

    Planning, image discovery, verification, and refinement happen in their
    own graph nodes before this function. Keeping this node generation-only
    prevents image search from being duplicated inside slide workers.
    """
    print("\n---------------- Executing Node: parallel_slide_generation ----------------")
    slide_chunks = list(state.get("slide_chunks") or [])
    slide_plans = list(state.get("slide_plans") or [])
    total_slides = len(slide_chunks)
    if not total_slides:
        return {
            "slide_plans": slide_plans,
            "slide_jobs": [],
            "section_batches": [],
            "deck_slide_count": 0,
            "final_slides": [],
        }

    _set_progress_total(config, None)
    jobs = build_slide_jobs({**state, "slide_plans": slide_plans})
    assignment = assign_layouts({"slide_jobs": jobs}, config)
    jobs = assignment.get("slide_jobs") or jobs
    state_for_workers = dict(state)
    state_for_workers["slide_jobs"] = jobs
    state_for_workers["deck_slide_count"] = total_slides

    tasks = [
        asyncio.create_task(_generate_one_slide(job, state_for_workers, config))
        for job in jobs
    ]
    _set_progress_total(config, total_slides)
    callback = (config or {}).get("configurable", {}).get("stream_callback")
    if callback:
        callback(
            "status",
            {
                "step": 3,
                "title": "Design Slides",
                "description": "Visual decisions are complete; generating slides in parallel",
                "message": "Generating slides",
            },
        )

    grouped_results = await asyncio.gather(*tasks)
    final_slides = [
        slide
        for worker_slides in grouped_results
        for slide in worker_slides
    ]
    final_slides.sort(key=lambda slide: int(slide.get("index", 0)))
    return {
        "slide_chunks": slide_chunks,
        "slide_context_maps": list(state.get("slide_context_maps") or []),
        "slide_positions": list(state.get("slide_positions") or []),
        "section_ids": list(state.get("section_ids") or []),
        "slide_plans": slide_plans,
        "slide_refinements": list(state.get("slide_refinements") or []),
        "slide_final_contents": list(state.get("slide_final_contents") or []),
        "slide_jobs": jobs,
        "section_batches": group_slide_jobs(jobs),
        "layout_assignment_report": assignment.get("layout_assignment_report", {}),
        "deck_slide_count": total_slides,
        "final_slides": final_slides,
        "slide_options": state.get("slide_options") or {},
        "image_search_candidates": state.get("image_search_candidates") or [],
        "approved_image_assignments": state.get("approved_image_assignments") or [],
        "document_image_assignments": state.get("document_image_assignments") or [],
    }
