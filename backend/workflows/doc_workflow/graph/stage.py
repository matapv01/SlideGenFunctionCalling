from typing import Any, Dict, List
from typing_extensions import TypedDict


class State(TypedDict, total=False):
    """State shared by document preprocessing nodes."""

    # Input
    docx_file: str
    # Compatibility-only flag for the old DOCX endpoint. The canonical
    # preprocessor uses automatic structure detection.
    workflow_mode: str
    slide_options: Dict[str, Any]

    # Intermediate/final preprocessing outputs
    document_title: str
    document_structure: List[Dict[str, Any]]
    plain_text: str
    # Text before the first explicit heading. It is kept separately during
    # the scan so mixed documents can be structured and merged without
    # re-processing sections that already have headings.
    document_preamble: str
    document_structure_origin: str
    document_outline: List[Dict[str, Any]]
    # Headings supplied by an upstream parser that must remain atomic. OCR
    # tables use this marker so the content splitter does not send a large
    # table back to the LLM for hierarchical rewriting.
    atomic_section_titles: List[str]
    slide_chunks: List[Dict[str, Any]]
    slide_positions: List[Any]
    slide_context_maps: List[str]
    # Private embedded DOCX image metadata produced by the canonical
    # preprocessor when a chatbot document id/output directory is supplied.
    document_images: List[Dict[str, Any]]
