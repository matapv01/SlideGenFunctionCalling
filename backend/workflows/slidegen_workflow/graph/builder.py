"""XML-only slide generation graph."""

from langgraph.graph import END, StateGraph

from backend.config import EXECUTOR_MAX_RETRIES
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.nodes.finalize_slide import finalize_slide
from backend.workflows.slidegen_workflow.nodes.next_slide_provider import provide_next_slide
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.slide_planner import planning_slide
from backend.workflows.slidegen_workflow.nodes.text_overflow_resolver import resolve_text_overflow
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import tool_call_executor
from backend.workflows.slidegen_workflow.nodes.xml_renderer import render_xml


def route_to_task(state: State) -> str:
    current_index = state.get("current_slide_index", -1)
    length = state.get("length_slide_chunks", 0)
    if current_index < length:
        return "generate_slide"
    return END


def evaluate_executor_decision(state: State) -> str:
    """Route every generated slide to overflow rules or retry generation."""
    decision = state.get("executor_decision", "fail")
    retry_count = state.get("retry_count", 0)
    if decision == "pass" or retry_count >= EXECUTOR_MAX_RETRIES:
        return "text_overflow_resolver"
    return "generate_slide"

def evaluate_overflow_decision(state: State) -> str:
    """Render only a slide whose whole-slide overflow repair has passed."""
    if state.get("overflow_failed") or (
        (state.get("overflow_report") or {}).get("status")
        == "overflow_remaining"
    ):
        return "generate_slide"
    return "render_xml"

def evaluate_vlm_decision(state: State) -> str:
    """Router check kết quả đánh giá của ViT (hoặc VLM)"""
    # ViT is observation-only: keep its result in state/logs, but never retry.
    return "finalizer"


def build_workflow(router_flags: bool = False) -> StateGraph:
    """Build the XML generation graph. ``router_flags`` is kept for API compatibility."""
    workflow = StateGraph(State)
    workflow.add_node("planning_slide", planning_slide)
    workflow.add_node("provide_next_slide", provide_next_slide)
    workflow.add_node("generate_slide", generate_slide)
    workflow.add_node("executor", tool_call_executor)
    workflow.add_node("text_overflow_resolver", resolve_text_overflow)
    workflow.add_node("render_xml", render_xml)
    workflow.add_node("finalizer", finalize_slide)

    workflow.set_entry_point("planning_slide")
    workflow.add_edge("planning_slide", "provide_next_slide")
    workflow.add_conditional_edges(
        "provide_next_slide",
        route_to_task,
        {"generate_slide": "generate_slide", END: END},
    )
    workflow.add_edge("generate_slide", "executor")
    workflow.add_conditional_edges(
        "executor",
        evaluate_executor_decision,
        {
            "text_overflow_resolver": "text_overflow_resolver",
            "generate_slide": "generate_slide",
        },
    )
    workflow.add_conditional_edges(
        "text_overflow_resolver",
        evaluate_overflow_decision,
        {
            "generate_slide": "generate_slide",
            "render_xml": "render_xml",
        },
    )
    # ViT remains available as legacy code, but is intentionally not wired
    # into this XML-only workflow because PNG capture is disabled.
    workflow.add_edge("render_xml", "finalizer")
    workflow.add_edge("finalizer", "provide_next_slide")
    return workflow
