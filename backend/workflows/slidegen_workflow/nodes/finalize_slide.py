"""Finalize XML slides and emit streaming progress."""

import time

from backend.workflows.slidegen_workflow.graph.stage import State
from langchain_core.runnables import RunnableConfig


def finalize_slide(state: State, config: RunnableConfig) -> State:
    start_time = time.time()
    idx = state["current_slide_index"]
    xml_path = state.get("current_xml_path", "")
    configurable = config.get("configurable", {}) if config else {}

    final_slide_data = {
        "index": idx,
        "tool_call": state["current_tool_call"],
        "xml_path": xml_path,
        "content_path": xml_path,
        "format": "xml",
        "png_path": "",
        "transitions": state.get("current_transitions", []),
        "vlm_evaluation_path": state.get("vlm_evaluation_path", ""),
        "vlm_evaluation_url": state.get("vlm_evaluation_url", ""),
        "overflow_report": state.get("overflow_report", {}),
        "overflow_rewrite_count": state.get("overflow_rewrite_count", 0),
        "contrast_report": state.get("current_contrast_report", []),
        "original_text": state.get("current_slide_text", ""),
        "batch_id": state.get("batch_id", ""),
        "slide_type": state.get("current_slide_type", "content"),
        "tool_category": (state.get("current_slide_plan") or {}).get("action"),
    }
    state.setdefault("final_slides", []).append(final_slide_data)

    stream_callback = config.get("configurable", {}).get("stream_callback")
    if configurable.get("suppress_slide_events"):
        stream_callback = None
    if stream_callback:
        slide_text = state.get("current_slide_text", {})
        slide_title = (
            slide_text.get("title", "Untitled")
            if isinstance(slide_text, dict)
            else "Untitled"
        )
        progress_tracker = configurable.get("parallel_progress_tracker")
        total_slides = state.get("deck_slide_count") or (
            len(state["final_slides"]) + len(state.get("slide_chunks", []))
        )
        total_known = True
        if progress_tracker is not None:
            total_known = bool(progress_tracker.get("total_known", True))
            if progress_tracker.get("total_slides"):
                total_slides = progress_tracker["total_slides"]
        if not total_known:
            total_slides = None

        is_new_completion = True
        if progress_tracker:
            lock = progress_tracker.get("lock")
            if lock:
                with lock:
                    completed_indices = progress_tracker.setdefault("completed_indices", set())
                    is_new_completion = idx not in completed_indices
                    completed_indices.add(idx)
                    current = len(completed_indices)
            else:
                completed_indices = progress_tracker.setdefault("completed_indices", set())
                is_new_completion = idx not in completed_indices
                completed_indices.add(idx)
                current = len(completed_indices)
        else:
            current = len(state["final_slides"])
        percentage = current / total_slides * 100 if total_slides else 0
        slide_completed_event = {
            "index": idx,
            "title": slide_title,
            "xml_path": xml_path,
            "content_path": xml_path,
            "format": "xml",
            "png_path": "",
            "transitions": state.get("current_transitions", []),
            "vlm_evaluation_url": state.get("vlm_evaluation_url", ""),
            "overflow_report": state.get("overflow_report", {}),
            "overflow_rewrite_count": state.get("overflow_rewrite_count", 0),
            "current": current,
        }
        if total_slides is not None:
            slide_completed_event["total"] = total_slides
        stream_callback("slide_completed", slide_completed_event)
        if is_new_completion:
            progress_message = f"Completed {current} slides"
            if total_slides is not None:
                progress_message = f"Completed {current}/{total_slides} slides"
            stream_callback(
                "progress",
                {
                    "current": current,
                    **({"total": total_slides} if total_slides is not None else {}),
                    "percentage": percentage,
                    "title": "Creating slides",
                    "message": progress_message,
                },
            )

    state["retry_count"] = 0
    state["executor_retry_count"] = 0
    state["overflow_retry_count"] = 0
    tool_retriever = configurable.get("tool_retriever")
    tool_call = state.get("current_tool_call") or {}
    tool_name = tool_call.get("name")
    tool_category = (state.get("current_slide_plan") or {}).get("action")

    if (
        configurable.get("record_tool_usage", True)
        and tool_retriever
        and tool_name
        and tool_category
        and tool_name != "default_fallback"
    ):
        try:
            tool_retriever.record_tool_usage(tool_category, tool_name, idx)
        except Exception as exc:
            print(f"Warning: could not record FAISS tool usage for {tool_name}: {exc}")

    state["previous_image_path"] = ""
    print(f"Added XML slide {idx + 1} to final_slides (total: {len(state['final_slides'])})")
    print(f"Finalization of XML slide took {time.time() - start_time:.2f} seconds.")
    return state
