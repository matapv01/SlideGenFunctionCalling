from langgraph.graph import StateGraph

from backend.workflows.doc_workflow.graph.stage import State
from backend.workflows.doc_workflow.nodes.auto_structure_generator import (
    generate_structure_from_plaintext,
)
from backend.workflows.doc_workflow.nodes.chunk_organizer import organize_chunks
from backend.workflows.doc_workflow.nodes.content_splitter import split_content
from backend.workflows.doc_workflow.nodes.document_converter import convert_document


def route_after_convert(state: State) -> str:
    """
    Route to auto-structure when no heading structure was detected.
    """
    doc_structure = state.get("document_structure", [])

    if doc_structure and len(doc_structure) > 0:
        return "split_content"

    return "auto_structure"


def build_doc_workflow(include_slide_chunks: bool = True) -> StateGraph:
    """Build the document workflow.

    The graph always produces the canonical Markdown/JSON document artifact.
    ``include_slide_chunks`` controls whether the legacy slide preparation
    stage is appended. This lets chatbot ingestion reuse document analysis
    without accidentally coupling RAG to slide generation.
    """
    workflow = StateGraph(State)

    workflow.add_node("convert_document", convert_document)
    workflow.add_node("auto_structure", generate_structure_from_plaintext)
    workflow.add_node("split_content", split_content)
    if include_slide_chunks:
        workflow.add_node("organize_chunks", organize_chunks)

    workflow.set_entry_point("convert_document")

    workflow.add_conditional_edges(
        "convert_document",
        route_after_convert,
        {"split_content": "split_content", "auto_structure": "auto_structure"},
    )
    workflow.add_edge("auto_structure", "split_content")
    if include_slide_chunks:
        workflow.add_edge("split_content", "organize_chunks")
        workflow.set_finish_point("organize_chunks")
    else:
        workflow.set_finish_point("split_content")

    return workflow
