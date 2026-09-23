"""Single-slide generation subgraph used by each parallel slide worker."""

from langgraph.graph import END, StateGraph

from backend.config import EXECUTOR_MAX_RETRIES
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.nodes.batch_slide_provider import provide_next_batch_slide
from backend.workflows.slidegen_workflow.nodes.finalize_slide import finalize_slide
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.text_overflow_resolver import resolve_text_overflow
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import tool_call_executor
from backend.workflows.slidegen_workflow.nodes.xml_renderer import render_xml


def _route_batch(state: State) -> str:
    return END if state.get("batch_done") else "generate_slide"


def _route_executor(state: State) -> str:
    if (
        state.get("executor_decision") == "pass"
        or state.get("executor_retry_count", 0) >= EXECUTOR_MAX_RETRIES
    ):
        return "text_overflow_resolver"
    return "generate_slide"


def _route_overflow(state: State) -> str:
    report = state.get("overflow_report") or {}
    if state.get("overflow_failed") or report.get("status") == "overflow_remaining":
        return "generate_slide"
    return "render_xml"


def build_batch_workflow() -> StateGraph:
    workflow = StateGraph(State)
    workflow.add_node("provide_next_batch_slide", provide_next_batch_slide)
    workflow.add_node("generate_slide", generate_slide)
    workflow.add_node("executor", tool_call_executor)
    workflow.add_node("text_overflow_resolver", resolve_text_overflow)
    workflow.add_node("render_xml", render_xml)
    workflow.add_node("finalizer", finalize_slide)

    workflow.set_entry_point("provide_next_batch_slide")
    workflow.add_conditional_edges(
        "provide_next_batch_slide",
        _route_batch,
        {"generate_slide": "generate_slide", END: END},
    )
    workflow.add_edge("generate_slide", "executor")
    workflow.add_conditional_edges(
        "executor",
        _route_executor,
        {
            "text_overflow_resolver": "text_overflow_resolver",
            "generate_slide": "generate_slide",
        },
    )
    workflow.add_conditional_edges(
        "text_overflow_resolver",
        _route_overflow,
        {"generate_slide": "generate_slide", "render_xml": "render_xml"},
    )
    # Layouts are assigned globally before fan-out, so this worker has no
    # mutable list of previously accepted slides to compare against.
    workflow.add_edge("render_xml", "finalizer")
    workflow.add_edge("finalizer", "provide_next_batch_slide")
    return workflow


_BATCH_APP = build_batch_workflow().compile()


def get_batch_app():
    return _BATCH_APP
