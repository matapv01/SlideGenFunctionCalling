from typing import Any, Dict, Optional

from backend.workflows.pdf_workflow.graph.builder import build_pdf_workflow
from backend.workflows.pdf_workflow.graph.stage import State


async def run_pdf_workflow(
    pdf_file: str,
    workflow_mode: str,
    slide_options: Optional[Dict[str, Any]],
    graph_config: Dict[str, Any],
) -> State:
    """Run PDF preprocessing and return state for slide planning workflow."""
    workflow = build_pdf_workflow()
    app = workflow.compile()

    initial_input: State = {
        "pdf_file": pdf_file,
        "workflow_mode": workflow_mode,
        "slide_options": slide_options or {},
    }

    final_state: State = await app.ainvoke(initial_input, config=graph_config)
    return final_state
