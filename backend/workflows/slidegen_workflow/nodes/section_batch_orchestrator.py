"""Assign deck-wide layouts, fan out independent slide jobs, then merge."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any, Dict, List

from langchain_core.runnables import RunnableConfig
from langgraph.constants import Send

from backend.config import TOOL_RETRIEVER_TOP_K, WORKFLOW_RECURSION_LIMIT
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    tool_matches_image_mode,
)
from backend.workflows.slidegen_workflow.utils.section_batches import (
    build_section_batches,
    group_slide_jobs,
)


def prepare_section_batches(state: State) -> Dict[str, Any]:
    jobs, batches = build_section_batches(state)
    print(
        f"Prepared {len(jobs)} canonical slide jobs in {len(batches)} section batches: "
        f"{[len(batch['jobs']) for batch in batches]}"
    )
    return {
        "slide_jobs": jobs,
        "section_batches": batches,
        "deck_slide_count": len(jobs),
    }


def _compatible_category(
    tools_dict: Dict[str, list],
    preferred_category: str,
    image_mode: str,
    approved_image_count: int,
) -> tuple[str | None, list, list]:
    """Find a category containing layouts compatible with the approved assets."""
    categories = [preferred_category]
    if preferred_category != "CONTENT_TOOLS" and "CONTENT_TOOLS" in tools_dict:
        categories.append("CONTENT_TOOLS")
    categories.extend(category for category in tools_dict if category not in categories)
    for category in categories:
        category_tools = list(tools_dict.get(category, []))
        compatible = [
            tool
            for tool in category_tools
            if tool_matches_image_mode(tool, image_mode, approved_image_count)
        ]
        if compatible:
            return category, category_tools, compatible
    return None, [], []


def assign_layouts(state: State, config: RunnableConfig) -> Dict[str, Any]:
    """Reserve layout tools before fan-out to keep parallel choices diverse."""
    configurable = config.get("configurable", {}) if config else {}
    tools_dict = configurable.get("tools_dict", {})
    tool_retriever = configurable.get("tool_retriever")
    strict_tool_retrieval = configurable.get("strict_tool_retrieval", False)
    jobs = deepcopy(state.get("slide_jobs") or [])
    usage: Counter[str] = Counter()
    last_global_tool = None
    last_tool_by_section: Dict[str, str] = {}
    transition_tool = None
    assignments = []

    for job in sorted(jobs, key=lambda item: int(item.get("index", 0))):
        plan = job.get("plan") or {}
        category = plan.get("action", "CONTENT_TOOLS")
        image_mode = str(plan.get("image_mode") or "").lower()
        approved_images = list(job.get("approved_images") or [])
        if image_mode not in {"none", "semantic"}:
            image_mode = "semantic" if approved_images else "none"
        if image_mode == "semantic" and not approved_images:
            image_mode = "none"
        selected_category, category_tools, compatible_tools = _compatible_category(
            tools_dict, category, image_mode, len(approved_images)
        )
        if image_mode == "semantic" and selected_category is None:
            if configurable.get("strict_image_layouts"):
                raise RuntimeError(
                    f"Slide {job.get('index')} has {len(approved_images)} approved images "
                    "but no layout with exactly that many image slots. Replan the slide."
                )
            # No registered XML layout can represent these assets; convert the
            # job completely to no-image before any prompt or reward is built.
            image_mode = "none"
            approved_images = []
            plan["approved_image_ids"] = []
            plan["image_search_intents"] = []
            plan["visual_layout_request"] = (
                "Use a clear no-image composition with readable hierarchy."
            )
            selected_category, category_tools, compatible_tools = _compatible_category(
                tools_dict, category, image_mode, 0
            )
        if selected_category is None:
            raise RuntimeError(
                f"No {image_mode} XML layout is available for category {category!r}"
            )
        category = selected_category
        plan["action"] = category
        plan["image_mode"] = image_mode
        if image_mode == "none":
            approved_images = []
            plan["approved_image_ids"] = []
            plan["image_search_intents"] = []
        job["approved_images"] = approved_images
        candidates = []
        if tool_retriever and compatible_tools:
            try:
                candidates = list(
                    tool_retriever.get_relevant_tools(
                        category=category,
                        query=(
                            plan.get("retrieval_query")
                            or plan.get("slide_topic")
                            or plan.get("thought", "")
                        ),
                        top_k=max(TOOL_RETRIEVER_TOP_K, len(category_tools)),
                        current_slide_index=int(job.get("index", 0)),
                    ) or []
                )
                candidates = [
                    tool for tool in candidates
                    if tool.name in {candidate.name for candidate in compatible_tools}
                ]
            except Exception as exc:
                if strict_tool_retrieval:
                    raise RuntimeError(
                        f"Strict layout retrieval failed for category {category!r}"
                    ) from exc
                print(f"Warning: layout pre-assignment retrieval failed: {exc}")
            if strict_tool_retrieval and not candidates:
                raise RuntimeError(
                    f"Strict layout retrieval returned no candidates for {category!r}"
                )

        # Keep semantic retrieval order, then append every category fallback so
        # local duplicate retries always have another layout available.
        ordered_names = []
        known_names = {tool.name for tool in compatible_tools}
        for tool in [*candidates, *compatible_tools]:
            name = getattr(tool, "name", None)
            if name and name in known_names and name not in ordered_names:
                ordered_names.append(name)

        section_id = str(job.get("section_id") or job.get("batch_id") or "section")
        if category == "TRANSITION_TOOLS" and transition_tool in ordered_names:
            chosen = transition_tool
        elif ordered_names:
            def score(name: str) -> tuple:
                rank = ordered_names.index(name)
                adjacent_penalty = 100 if name == last_global_tool else 0
                section_penalty = 40 if name == last_tool_by_section.get(section_id) else 0
                usage_penalty = usage[name] * 4
                return adjacent_penalty + section_penalty + usage_penalty + rank, rank

            chosen = min(ordered_names, key=score)
            if category == "TRANSITION_TOOLS" and transition_tool is None:
                transition_tool = chosen
        else:
            chosen = None

        if chosen:
            remaining = [name for name in ordered_names if name != chosen]
            job["preferred_tool_name"] = chosen
            job["assigned_tool_candidates"] = [chosen, *remaining]
            usage[chosen] += 1
            last_global_tool = chosen
            last_tool_by_section[section_id] = chosen
        job["plan"] = plan
        assignments.append(
            {
                "index": job.get("index"),
                "section_id": section_id,
                "category": category,
                "image_mode": image_mode or "any",
                "preferred_tool": chosen,
            }
        )

    return {
        "slide_jobs": jobs,
        "section_batches": group_slide_jobs(jobs),
        "layout_assignment_report": {
            "assignments": assignments,
            "tool_usage": dict(usage),
        },
    }


def dispatch_section_batches(state: State):
    """Fan out one immutable slide job per worker.

    The function name is kept for graph/test compatibility. Sections are still
    used during layout assignment, but generation no longer waits for the
    previous slide in a section.
    """
    batches = state.get("section_batches") or []
    if not batches:
        return "merge_batch_results"
    shared = {
        "deck_style_plan": state.get("deck_style_plan", {}),
        "deck_slide_count": state.get("deck_slide_count", 0),
        "slide_options": state.get("slide_options", {}),
        "slide_context_maps": list(state.get("slide_context_maps") or []),
        "output_format": state.get("output_format", "xml"),
        "document_title": state.get("document_title", ""),
    }
    sends = []
    for section_batch in batches:
        for job in section_batch.get("jobs") or []:
            slide_index = int(job.get("index", 0))
            single_slide_batch = {
                "batch_id": f"{section_batch['batch_id']}__slide_{slide_index}",
                "order": slide_index,
                "jobs": [job],
            }
            sends.append(
                Send(
                    "run_section_batch",
                    {"section_batch": single_slide_batch, **shared},
                )
            )
    return sends


def _worker_config(config: RunnableConfig) -> Dict[str, Any]:
    worker_config = dict(config or {})
    configurable = dict(worker_config.get("configurable", {}))
    configurable.update(
        {
            # Emit each completed slide immediately. A shared tracker keeps
            # progress monotonic across concurrent section workers.
            "suppress_slide_events": False,
            "record_tool_usage": False,
        }
    )
    worker_config["configurable"] = configurable
    worker_config["recursion_limit"] = max(
        WORKFLOW_RECURSION_LIMIT,
        int(worker_config.get("recursion_limit", WORKFLOW_RECURSION_LIMIT)),
    )
    return worker_config


async def _invoke_jobs(
    jobs: List[Dict[str, Any]],
    state: Dict[str, Any],
    config: RunnableConfig,
) -> Dict[str, Any]:
    # Lazy import keeps pure batch-planning and graph-routing tests independent
    # from heavyweight generation/model dependencies.
    from backend.workflows.slidegen_workflow.graph.batch_builder import get_batch_app

    batch_id = str(jobs[0].get("batch_id", "repair")) if jobs else "empty"
    worker_state: State = {
        "batch_id": batch_id,
        "batch_slide_jobs": deepcopy(jobs),
        "batch_cursor": 0,
        "batch_done": False,
        "batch_layout_signatures": [],
        "final_slides": [],
        "all_debug_info": [],
        "deck_style_plan": state.get("deck_style_plan", {}),
        "deck_slide_count": state.get("deck_slide_count", len(jobs)),
        "length_slide_chunks": state.get("deck_slide_count", len(jobs)),
        "slide_options": state.get("slide_options", {}),
        "output_format": state.get("output_format", "xml"),
        "document_title": state.get("document_title", ""),
        "current_slide_index": -1,
        "retry_count": 0,
        "executor_retry_count": 0,
        "overflow_retry_count": 0,
        "vlm_decision": "accept",
    }
    worker_config = _worker_config(config)
    semaphore = (
        (config or {}).get("configurable", {}).get("slide_generation_semaphore")
        if config
        else None
    )
    if semaphore is None:
        return await get_batch_app().ainvoke(worker_state, config=worker_config)

    # Dynamic Send fan-out can schedule more nested workers than the parent
    # graph's max_concurrency. The shared semaphore is the actual endpoint
    # protection for local Qwen generation.
    async with semaphore:
        return await get_batch_app().ainvoke(worker_state, config=worker_config)


async def run_section_batch(state: State, config: RunnableConfig) -> Dict[str, Any]:
    batch = state["section_batch"]
    result = await _invoke_jobs(batch.get("jobs") or [], state, config)
    return {
        "batch_results": [
            {
                "batch_id": batch["batch_id"],
                "order": batch["order"],
                "slides": result.get("final_slides", []),
            }
        ]
    }


def merge_batch_results(state: State) -> Dict[str, Any]:
    results = sorted(state.get("batch_results") or [], key=lambda item: item.get("order", 0))
    slides = [slide for result in results for slide in result.get("slides", [])]
    slides.sort(key=lambda slide: int(slide.get("index", 0)))
    return {"final_slides": slides}


def emit_final_slides(state: State, config: RunnableConfig) -> Dict[str, Any]:
    slides = sorted(state.get("final_slides") or [], key=lambda slide: int(slide.get("index", 0)))
    configurable = config.get("configurable", {}) if config else {}
    stream_callback = configurable.get("stream_callback")
    tool_retriever = configurable.get("tool_retriever")
    progress_tracker = configurable.get("parallel_progress_tracker")
    total = len(slides)

    for current, slide in enumerate(slides, start=1):
        tool_call = slide.get("tool_call") or {}
        tool_name = tool_call.get("name")
        tool_category = slide.get("tool_category")
        index = int(slide.get("index", current - 1))
        if tool_retriever and tool_name and tool_category and tool_name != "default_fallback":
            try:
                tool_retriever.record_tool_usage(tool_category, tool_name, index)
            except Exception as exc:
                print(f"Warning: could not record tool usage for {tool_name}: {exc}")

        already_emitted = False
        if progress_tracker:
            lock = progress_tracker.get("lock")
            if lock:
                with lock:
                    already_emitted = index in progress_tracker["completed_indices"]
            else:
                already_emitted = index in progress_tracker.get("completed_indices", set())

        # Workers normally emitted these slides as soon as they completed.
        # This fallback only fills an event that was missed before final merge.
        if stream_callback and not already_emitted:
            original = slide.get("original_text", {})
            title = original.get("title", "Untitled") if isinstance(original, dict) else "Untitled"
            stream_callback(
                "slide_completed",
                {
                    "index": index,
                    "title": title,
                    "xml_path": slide.get("xml_path", ""),
                    "content_path": slide.get("content_path", ""),
                    "format": "xml",
                    "png_path": "",
                    "transitions": slide.get("transitions", []),
                    "overflow_report": slide.get("overflow_report", {}),
                    "overflow_rewrite_count": slide.get("overflow_rewrite_count", 0),
                    "current": current,
                    "total": total,
                },
            )
            stream_callback(
                "progress",
                {
                    "current": current,
                    "total": total,
                    "percentage": current / total * 100 if total else 0,
                    "title": "Creating slides",
                    "message": f"Completed {current}/{total} slides",
                },
            )
    return {"final_slides": slides}
