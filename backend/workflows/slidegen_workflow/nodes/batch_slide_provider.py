"""Provide slides sequentially from one section batch."""

from backend.workflows.slidegen_workflow.graph.stage import State


def provide_next_batch_slide(state: State) -> State:
    jobs = state.get("batch_slide_jobs") or []
    cursor = int(state.get("batch_cursor", 0))
    if cursor >= len(jobs):
        state["batch_done"] = True
        return state

    job = jobs[cursor]
    state["batch_cursor"] = cursor + 1
    state["batch_done"] = False
    state["current_slide_index"] = int(job["index"])
    state["current_slide_text"] = job.get("content", "")
    state["current_slide_context_map"] = job.get("context_map", "")
    state["current_slide_plan"] = job.get("plan") or {
        "thought": "Use a readable content layout.",
        "action": "CONTENT_TOOLS",
    }
    state["current_slide_position"] = job.get("position")
    state["current_slide_type"] = job.get("slide_type", "content")
    state["duplicate_excluded_tools"] = list(job.get("excluded_tools") or [])
    state["assigned_tool_candidates"] = list(job.get("assigned_tool_candidates") or [])
    state["preferred_tool_name"] = str(job.get("preferred_tool_name") or "")
    state["duplicate_retry_count"] = 0
    state["duplicate_detected"] = False
    state["retry_count"] = 0
    state["executor_feedback"] = ""
    state["vlm_feedback"] = ""
    state["overflow_report"] = {}
    state["overflow_rewrite_count"] = 0
    state["overflow_failed"] = False
    state["current_tool_call"] = {}
    state["current_tool_plan"] = []
    state["current_xml_content"] = ""
    state["current_xml_path"] = ""

    print(
        f"Batch {state.get('batch_id')} processing slide "
        f"{state['current_slide_index'] + 1}/{state.get('deck_slide_count', len(jobs))}"
    )
    return state
