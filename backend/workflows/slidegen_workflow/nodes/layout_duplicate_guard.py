"""Reject repeated non-transition geometry before a batch accepts a slide."""

from backend.config import DUPLICATE_REGEN_MAX_ROUNDS, ENABLE_LAYOUT_DUPLICATE_CHECK
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.utils.layout_similarity import (
    build_layout_signature,
    find_layout_duplicate,
)


def guard_layout_duplicate(state: State) -> State:
    xml_content = state.get("current_xml_content", "")
    signature = build_layout_signature(xml_content)
    state["layout_signature"] = signature

    accepted = list(state.get("batch_layout_signatures") or [])
    slide_index = int(state.get("current_slide_index", -1))
    slide_type = state.get("current_slide_type")
    action = (state.get("current_slide_plan") or {}).get("action")
    exempt = slide_type == "transition" or action == "TRANSITION_TOOLS"

    duplicate = None
    if ENABLE_LAYOUT_DUPLICATE_CHECK and not exempt:
        duplicate = find_layout_duplicate(signature, slide_index, accepted)

    retry_count = int(state.get("duplicate_retry_count", 0))
    if duplicate and retry_count < DUPLICATE_REGEN_MAX_ROUNDS:
        matched, score = duplicate
        tool_name = (state.get("current_tool_call") or {}).get("name")
        excluded = list(state.get("duplicate_excluded_tools") or [])
        if tool_name and tool_name not in excluded:
            excluded.append(tool_name)
        state["duplicate_excluded_tools"] = excluded
        state["duplicate_retry_count"] = retry_count + 1
        state["duplicate_detected"] = True
        state["retry_count"] = 0
        state["executor_feedback"] = (
            f"LAYOUT_DUPLICATE: geometry is {score:.0%} similar to slide "
            f"{int(matched['index']) + 1}. Select a different layout tool and "
            "use visibly different element geometry while keeping the deck style."
        )
        print(
            f"Duplicate layout on slide {slide_index + 1}; retry "
            f"{state['duplicate_retry_count']}/{DUPLICATE_REGEN_MAX_ROUNDS}."
        )
        return state

    accepted.append(
        {
            "index": slide_index,
            "signature": signature,
            "tool_name": (state.get("current_tool_call") or {}).get("name"),
            "exempt": exempt,
        }
    )
    state["batch_layout_signatures"] = accepted
    state["duplicate_detected"] = False
    return state
