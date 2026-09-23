from typing import Any, Dict, List
from typing_extensions import TypedDict


class State(TypedDict, total=False):
    """State shared by manual preprocessing nodes."""

    # Input
    session_id: str
    document_title: str
    slide_chunks: List[Dict[str, Any]]
    document_structure: List[Dict[str, Any]]
    intro_slide: Dict[str, Any]
    slide_options: Dict[str, Any]

    # Output consumed by planning workflow
    document_outline: List[Dict[str, Any]]
    slide_positions: List[Any]
    section_ids: List[str]
    slide_context_maps: List[str]
    slide_types: List[str]
    approved_result: Dict[str, Any]
    update_result: Dict[str, Any]
