from typing import Any, Dict, Optional

from backend.workflows.doc_workflow.graph.builder import build_doc_workflow
from backend.workflows.doc_workflow.graph.stage import State


async def run_doc_workflow(
    docx_file: str,
    workflow_mode: str,
    slide_options: Optional[Dict[str, Any]],
    graph_config: Dict[str, Any],
) -> State:
    """Run document preprocessing and return state for slide planning workflow."""
    workflow = build_doc_workflow()
    app = workflow.compile()

    initial_input: State = {
        "docx_file": docx_file,
        "workflow_mode": workflow_mode,
        "slide_options": slide_options or {},
    }

    final_state: State = await app.ainvoke(initial_input, config=graph_config)
    return final_state
