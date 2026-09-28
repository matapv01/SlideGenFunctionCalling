from typing import Any, Dict, Optional

from backend.workflows.doc_workflow.graph.builder import build_doc_workflow
from backend.workflows.doc_workflow.graph.stage import State


async def run_doc_workflow(
    docx_file: str,
    workflow_mode: str = "auto",
    slide_options: Optional[Dict[str, Any]] = None,
    graph_config: Optional[Dict[str, Any]] = None,
    include_slide_chunks: bool = True,
    atomic_section_titles: Optional[list[str]] = None,
) -> State:
    """Run canonical document preprocessing.

    The optional slide stage remains enabled by default for existing DOCX
    generation callers. Chatbot ingestion disables it and receives only the
    document artifact needed by the RAG index.
    """
    workflow = build_doc_workflow(include_slide_chunks=include_slide_chunks)
    app = workflow.compile()

    initial_input: State = {
        "docx_file": docx_file,
        "workflow_mode": workflow_mode,
        "slide_options": slide_options or {},
        "atomic_section_titles": atomic_section_titles or [],
    }

    final_state: State = await app.ainvoke(initial_input, config=graph_config or {})
    return final_state
