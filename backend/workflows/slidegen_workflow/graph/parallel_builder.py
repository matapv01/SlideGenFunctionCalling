"""Deck graph with pipelined planning and independent slide generation."""

from langgraph.graph import END, StateGraph

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.nodes.deck_style_planner import create_deck_style
from backend.workflows.slidegen_workflow.nodes.pipelined_orchestrator import (
    plan_and_generate_pipeline,
)
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import (
    assign_layouts,
    dispatch_section_batches,
    emit_final_slides,
    merge_batch_results,
    prepare_section_batches,
    run_section_batch,
)
from backend.workflows.slidegen_workflow.nodes.slide_planner import planning_slide
from backend.workflows.slidegen_workflow.nodes.image_verifier import verify_document_images


def build_parallel_workflow() -> StateGraph:
    workflow = StateGraph(State)
    workflow.add_node("create_deck_style", create_deck_style)
    workflow.add_node("verify_document_images", verify_document_images)
    workflow.add_node("plan_and_generate_pipeline", plan_and_generate_pipeline)
    # Keep the old nodes registered for compatibility with integrations that
    # inspect the graph. The active path below uses the pipeline node instead.
    workflow.add_node("planning_slide", planning_slide)
    workflow.add_node("prepare_section_batches", prepare_section_batches)
    workflow.add_node("assign_layouts", assign_layouts)
    workflow.add_node("run_section_batch", run_section_batch)
    workflow.add_node("merge_batch_results", merge_batch_results)
    workflow.add_node("emit_final_slides", emit_final_slides)

    workflow.set_entry_point("create_deck_style")
    workflow.add_edge("create_deck_style", "verify_document_images")
    workflow.add_edge("verify_document_images", "plan_and_generate_pipeline")
    workflow.add_edge("plan_and_generate_pipeline", "emit_final_slides")
    workflow.add_edge("emit_final_slides", END)
    return workflow
