from typing import Any, Dict, List, TypedDict


class State(TypedDict, total=False):
    """State shared by manual preprocessing nodes."""

    # Input
    document_title: str
    slide_chunks: List[Dict[str, Any]]
    slide_options: Dict[str, Any]

    # Output consumed by planning workflow
    document_structure: List[Dict[str, Any]]
    slide_context_maps: List[str]
