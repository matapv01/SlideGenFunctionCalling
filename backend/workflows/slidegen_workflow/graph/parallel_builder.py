"""Deck graph: style once, plan once, then fan out independent slide jobs."""

from langgraph.graph import END, StateGraph

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.nodes.deck_style_planner import create_deck_style
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import (
    assign_layouts,
    dispatch_section_batches,
    emit_final_slides,
    merge_batch_results,
    prepare_section_batches,
    run_section_batch,
)
from backend.workflows.slidegen_workflow.nodes.slide_planner import planning_slide


def build_parallel_workflow() -> StateGraph:
    workflow = StateGraph(State)
    workflow.add_node("create_deck_style", create_deck_style)
    workflow.add_node("planning_slide", planning_slide)
    workflow.add_node("prepare_section_batches", prepare_section_batches)
    workflow.add_node("assign_layouts", assign_layouts)
    workflow.add_node("run_section_batch", run_section_batch)
    workflow.add_node("merge_batch_results", merge_batch_results)
    workflow.add_node("emit_final_slides", emit_final_slides)

    workflow.set_entry_point("create_deck_style")
    workflow.add_edge("create_deck_style", "planning_slide")
    workflow.add_edge("planning_slide", "prepare_section_batches")
    workflow.add_edge("prepare_section_batches", "assign_layouts")
    workflow.add_conditional_edges("assign_layouts", dispatch_section_batches)
    workflow.add_edge("run_section_batch", "merge_batch_results")
    workflow.add_edge("merge_batch_results", "emit_final_slides")
    workflow.add_edge("emit_final_slides", END)
    return workflow
