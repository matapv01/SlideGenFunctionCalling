"""Pipeline planner batches into slide generation workers."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Any, Dict, List

from langchain_core.runnables import RunnableConfig

from backend.config import PLANNING_BATCH_SIZE
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import (
    _invoke_jobs,
    assign_layouts,
)
from backend.workflows.slidegen_workflow.nodes.slide_planner import (
    _invoke_planner_batch,
    fallback_slide_plan,
    normalize_planner_result,
    normalize_image_sequence,
    prepare_planner_context,
)
from backend.workflows.slidegen_workflow.utils.section_batches import (
    build_slide_jobs,
    group_slide_jobs,
)


def _plans_for_job_build(
    slide_chunks: List[Any],
    planned_by_index: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Fill not-yet-planned slides with deterministic metadata fallbacks.

    ``build_slide_jobs`` needs the complete deck to calculate sections. Future
    slides therefore receive a temporary plan, while the current batch always
    uses the real structured planner output.
    """
    return [
        planned_by_index.get(index) or fallback_slide_plan(content, index)
        for index, content in enumerate(slide_chunks)
    ]


def _jobs_for_batch(
    state: State,
    slide_chunks: List[Any],
    planned_by_index: Dict[int, Dict[str, Any]],
    start: int,
    end: int,
) -> List[Dict[str, Any]]:
    job_state = dict(state)
    job_state["slide_chunks"] = slide_chunks
    job_state["slide_plans"] = _plans_for_job_build(slide_chunks, planned_by_index)
    jobs = build_slide_jobs(job_state)
    return jobs[start:end]


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
    """Plan and generate in overlapping batches.

    The planner remains sequential at batch level so the whole-deck outline and
    plan ordering stay deterministic. Generation tasks from batch N are started
    before planning batch N+1 begins, while the shared worker semaphore keeps
    the local model endpoint bounded.
    """
    print(
        "\n---------------- Executing Node: "
        "pipelined planner + generator ----------------"
    )

    planner_context = prepare_planner_context(state, config)
    slide_chunks = planner_context["slide_chunks"]
    slide_context_maps = planner_context["slide_context_maps"]
    slide_positions = planner_context["slide_positions"]
    section_ids = planner_context["section_ids"]
    all_inputs = planner_context["all_inputs"]
    planner_chain = planner_context["planner_chain"]
    planner_batch_chain = planner_context.get("planner_batch_chain")
    stream_callback = planner_context["stream_callback"]

    if not all_inputs or planner_chain is None:
        return {
            "slide_plans": [],
            "slide_jobs": [],
            "section_batches": [],
            "deck_slide_count": 0,
            "final_slides": [],
        }

    total_slides = len(all_inputs)
    # Generation starts before the planner has completed the whole deck. Do
    # not let one-slide worker state be mistaken for the final deck total.
    _set_progress_total(config, None)
    planned_by_index: Dict[int, Dict[str, Any]] = {}
    allocated_jobs: List[Dict[str, Any]] = []
    generation_tasks: List[asyncio.Task] = []
    last_assignment: Dict[str, Any] = {}

    print(
        f"Total slides to pipeline: {total_slides}. "
        f"Planning batches: {PLANNING_BATCH_SIZE}."
    )

    for start in range(0, total_slides, PLANNING_BATCH_SIZE):
        end = min(start + PLANNING_BATCH_SIZE, total_slides)
        print(f"  -> Planning batch: slides {start + 1}-{end}...")
        batch_inputs = all_inputs[start:end]

        try:
            # The structured batch call is synchronous in the LangChain
            # wrapper. Run it in a thread so already-started generator tasks
            # keep progressing.
            batch_results = await asyncio.to_thread(
                _invoke_planner_batch,
                planner_batch_chain,
                planner_chain,
                batch_inputs,
                config,
            )
            batch_plans = [
                normalize_planner_result(
                    plan,
                    slide_chunks[start + offset],
                    start + offset,
                )
                for offset, plan in enumerate(batch_results)
            ]
        except Exception as exc:
            print(
                f"  -> Planner batch {start + 1}-{end} failed; "
                f"using fallbacks: {exc}"
            )
            batch_plans = [
                fallback_slide_plan(slide_chunks[index], index)
                for index in range(start, end)
            ]

        for index, plan in enumerate(batch_plans, start=start):
            planned_by_index[index] = plan

        # Reconcile image decisions across the batches already planned. This
        # keeps independent planner calls from placing decorative images on
        # every consecutive content slide.
        normalize_image_sequence(
            [planned_by_index[index] for index in range(end)]
        )

        batch_jobs = _jobs_for_batch(
            state,
            slide_chunks,
            planned_by_index,
            start,
            end,
        )
        allocated_jobs.extend(batch_jobs)

        # Re-run the deterministic allocator over all known jobs so the new
        # batch sees the layouts already reserved by earlier batches.
        last_assignment = assign_layouts(
            {"slide_jobs": allocated_jobs},
            config,
        )
        allocated_jobs = last_assignment["slide_jobs"]
        jobs_by_index = {
            int(job["index"]): job
            for job in allocated_jobs
            if int(job.get("index", -1)) in range(start, end)
        }

        for index in range(start, end):
            job = jobs_by_index.get(index)
            if job is not None:
                generation_tasks.append(
                    asyncio.create_task(_generate_one_slide(job, state, config))
                )
        print(
            f"     ... batch {start + 1}-{end} dispatched; "
            "planning continues while generation runs."
        )

    _set_progress_total(config, total_slides)
    if stream_callback:
        stream_callback(
            "status",
            {
                "step": 3,
                "title": "Design Slides",
                "description": "Planning complete; generation is finishing in parallel",
                "message": "All slide plans are ready",
            },
        )

    grouped_results = await asyncio.gather(*generation_tasks)
    final_slides = [
        slide
        for worker_slides in grouped_results
        for slide in worker_slides
    ]
    final_slides.sort(key=lambda slide: int(slide.get("index", 0)))

    ordered_plans = [planned_by_index[index] for index in range(total_slides)]
    return {
        "slide_chunks": slide_chunks,
        "slide_context_maps": slide_context_maps,
        "slide_positions": slide_positions,
        "section_ids": section_ids,
        "slide_plans": ordered_plans,
        "slide_jobs": allocated_jobs,
        "section_batches": group_slide_jobs(allocated_jobs),
        "layout_assignment_report": last_assignment.get(
            "layout_assignment_report", {}
        ),
        "deck_slide_count": total_slides,
        "final_slides": final_slides,
    }
