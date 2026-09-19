"""Deck graph with pipelined planning and independent slide generation."""

from langgraph.graph import END, StateGraph

from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.nodes.deck_style_planner import create_deck_style
from backend.workflows.slidegen_workflow.nodes.pipelined_orchestrator import (
    plan_and_generate_pipeline,
)
from backend.workflows.slidegen_workflow.nodes.image_candidate_search import (
    search_image_candidates,
)
from backend.workflows.slidegen_workflow.nodes.image_verifier import verify_slide_images
from backend.workflows.slidegen_workflow.nodes.slide_refiner import refine_slide_plans
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import (
    emit_final_slides,
)
from backend.workflows.slidegen_workflow.nodes.slide_planner import planning_slide


def build_parallel_workflow() -> StateGraph:
    workflow = StateGraph(State)
    workflow.add_node("create_deck_style", create_deck_style)
    workflow.add_node("search_image_candidates", search_image_candidates)
    workflow.add_node("verify_slide_images", verify_slide_images)
    workflow.add_node("refine_slide_plans", refine_slide_plans)
    workflow.add_node("plan_and_generate_pipeline", plan_and_generate_pipeline)
    workflow.add_node("planning_slide", planning_slide)
    workflow.add_node("emit_final_slides", emit_final_slides)

    workflow.set_entry_point("create_deck_style")
    # The pipeline plans the complete deck first, runs the document-image
    # verifier with those semantic plans, and only then dispatches slide
    # workers. Keeping verification inside the pipeline avoids starting a
    # worker before its document-image assignments are known.
    workflow.add_edge("create_deck_style", "planning_slide")
    workflow.add_edge("planning_slide", "search_image_candidates")
    workflow.add_edge("search_image_candidates", "verify_slide_images")
    workflow.add_edge("verify_slide_images", "refine_slide_plans")
    workflow.add_edge("refine_slide_plans", "plan_and_generate_pipeline")
    workflow.add_edge("plan_and_generate_pipeline", "emit_final_slides")
    workflow.add_edge("emit_final_slides", END)
    return workflow
