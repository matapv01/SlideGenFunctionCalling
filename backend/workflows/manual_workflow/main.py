from typing import Any, Dict, List, Optional

from backend.workflows.manual_workflow.graph.builder import build_manual_workflow
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
