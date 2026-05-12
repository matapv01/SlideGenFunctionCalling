from langgraph.graph import StateGraph

from backend.workflows.pdf_workflow.graph.stage import State
from backend.workflows.pdf_workflow.nodes.document_converter import convert_document
from backend.workflows.doc_workflow.nodes.auto_structure_generator import generate_structure_from_plaintext
from backend.workflows.doc_workflow.nodes.content_splitter import split_content
from backend.workflows.doc_workflow.nodes.chunk_organizer import organize_chunks


def route_after_convert(state: State) -> str:
    """
    Route to auto-structure when no heading structure was detected.
    """
    doc_structure = state.get("document_structure", [])

    if doc_structure and len(doc_structure) > 0:
        return "split_content"

    return "auto_structure"


def build_pdf_workflow() -> StateGraph:
    """Build the PDF preprocessing workflow graph."""
    workflow = StateGraph(State)

    workflow.add_node("convert_document", convert_document)
    workflow.add_node("auto_structure", generate_structure_from_plaintext)
    workflow.add_node("split_content", split_content)
    workflow.add_node("organize_chunks", organize_chunks)

    workflow.set_entry_point("convert_document")

    workflow.add_conditional_edges(
        "convert_document",
        route_after_convert,
        {"split_content": "split_content", "auto_structure": "auto_structure"},
    )
    workflow.add_edge("auto_structure", "split_content")
    workflow.add_edge("split_content", "organize_chunks")
    workflow.set_finish_point("organize_chunks")

    return workflow
