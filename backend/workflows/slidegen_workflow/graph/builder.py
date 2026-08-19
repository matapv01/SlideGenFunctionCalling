"""XML-only slide generation graph."""

from langgraph.graph import END, StateGraph

from backend.config import EXECUTOR_MAX_RETRIES
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.nodes.finalize_slide import finalize_slide
from backend.workflows.slidegen_workflow.nodes.next_slide_provider import provide_next_slide
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.slide_planner import planning_slide
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import tool_call_executor
from backend.workflows.slidegen_workflow.nodes.xml_renderer import render_xml
from backend.workflows.slidegen_workflow.nodes.slide_evaluator import slide_evaluator


def route_to_task(state: State) -> str:
    current_index = state.get("current_slide_index", -1)
    length = state.get("length_slide_chunks", 0)
    if current_index < length:
        return "generate_slide"
    return END


def evaluate_executor_decision(state: State) -> str:
    """Route every generated slide to XML rendering or retry generation."""
    decision = state.get("executor_decision", "fail")
    retry_count = state.get("retry_count", 0)
    if decision == "pass" or retry_count >= EXECUTOR_MAX_RETRIES:
        return "render_xml"
    return "generate_slide"

def evaluate_vlm_decision(state: State) -> str:
    """Router check kết quả đánh giá của ViT (hoặc VLM)"""
    decision = state.get("vlm_decision", "accept")
    retry_count = state.get("retry_count", 0)
    if decision == "accept" or retry_count >= EXECUTOR_MAX_RETRIES:
        return "finalizer"
    return "generate_slide"


def build_workflow(router_flags: bool = False) -> StateGraph:
    """Build the XML generation graph. ``router_flags`` is kept for API compatibility."""
    workflow = StateGraph(State)
    workflow.add_node("planning_slide", planning_slide)
    workflow.add_node("provide_next_slide", provide_next_slide)
    workflow.add_node("generate_slide", generate_slide)
    workflow.add_node("executor", tool_call_executor)
    workflow.add_node("render_xml", render_xml)
    workflow.add_node("evaluator", slide_evaluator)
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
        {"render_xml": "render_xml", "generate_slide": "generate_slide"},
    )
    workflow.add_edge("render_xml", "evaluator")
    workflow.add_conditional_edges(
        "evaluator",
        evaluate_vlm_decision,
        {"finalizer": "finalizer", "generate_slide": "generate_slide"},
    )
    workflow.add_edge("finalizer", "provide_next_slide")
    return workflow
