from typing import Any, Dict, List, TypedDict


class State(TypedDict, total=False):
    """State shared by document preprocessing nodes."""

    # Input
    docx_file: str
    workflow_mode: str
    slide_options: Dict[str, Any]

    # Intermediate/final preprocessing outputs
    document_title: str
    document_structure: List[Dict[str, Any]]
    plain_text: str
    document_outline: List[Dict[str, Any]]
    slide_chunks: List[Dict[str, Any]]
    slide_positions: List[Any]
    slide_context_maps: List[str]
