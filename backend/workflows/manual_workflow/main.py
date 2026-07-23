from typing import Any, Dict, List, Optional

from backend.workflows.manual_workflow.graph.builder import (
    build_manual_approve_workflow,
    build_manual_update_workflow,
    build_manual_workflow,
)
from backend.workflows.manual_workflow.graph.stage import State


async def run_manual_workflow(
    slide_chunks: List[Dict[str, Any]],
    title: str,
    slide_options: Optional[Dict[str, Any]],
    graph_config: Dict[str, Any],
) -> State:
    """Run manual preprocessing workflow and return normalized state."""
    workflow = build_manual_workflow()
    app = workflow.compile()

    initial_input: State = {
        "document_title": title,
        "slide_chunks": slide_chunks,
        "slide_options": slide_options or {},
    }

    final_state: State = await app.ainvoke(initial_input, config=graph_config)
    return final_state


async def run_manual_approve_workflow(
    session_id: str,
    document_title: str,
    document_structure: List[Dict[str, Any]],
    slide_options: Optional[Dict[str, Any]],
    graph_config: Dict[str, Any],
) -> State:
    """Run manual approve workflow from editor tree structure."""
    workflow = build_manual_approve_workflow()
    app = workflow.compile()

    initial_input: State = {
        "session_id": session_id,
        "document_title": document_title,
        "document_structure": document_structure,
        "slide_options": slide_options or {},
    }

    final_state: State = await app.ainvoke(initial_input, config=graph_config)
    return final_state


async def run_manual_update_workflow(
    session_id: str,
    document_structure: List[Dict[str, Any]],
    intro_slide: Optional[Dict[str, Any]],
    graph_config: Dict[str, Any],
) -> State:
    """Run manual update workflow to persist editor structure."""
    workflow = build_manual_update_workflow()
    app = workflow.compile()

    initial_input: State = {
        "session_id": session_id,
        "document_structure": document_structure,
        "intro_slide": intro_slide or {},
    }

    final_state: State = await app.ainvoke(initial_input, config=graph_config)
    return final_state
