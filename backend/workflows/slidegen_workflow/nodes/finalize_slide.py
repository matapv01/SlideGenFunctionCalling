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
        total_slides = state.get("deck_slide_count") or (
            len(state["final_slides"]) + len(state.get("slide_chunks", []))
        )
        progress_tracker = configurable.get("parallel_progress_tracker")
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
        stream_callback(
            "slide_completed",
            {
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
                "total": total_slides,
            },
        )
        if is_new_completion:
            stream_callback(
                "progress",
                {
                    "current": current,
                    "total": total_slides,
                    "percentage": percentage,
                    "title": "Creating slides",
                    "message": f"Completed {current}/{total_slides} slides",
                },
            )

    state["retry_count"] = 0
    state["executor_retry_count"] = 0
    state["overflow_retry_count"] = 0
    state["previous_accepted_tool_call"] = state["current_tool_call"]

    # Feed accepted XML tool usage back into the retriever. This enables the
    # temporal-decay component on the next slides instead of keeping an empty
    # usage history throughout the workflow.
    tool_retriever = configurable.get("tool_retriever")
    tool_call = state.get("current_tool_call") or {}
    tool_name = tool_call.get("name")
    tool_category = (state.get("current_slide_plan") or {}).get("action")
    if tool_name and tool_category and tool_name != "default_fallback":
        local_history = list(state.get("batch_tool_usage_history") or [])
        local_history.append(
            {"category": tool_category, "tool_name": tool_name, "index": idx}
        )
        state["batch_tool_usage_history"] = local_history

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
