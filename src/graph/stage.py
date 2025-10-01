# src/graph/stage.py
from typing import List, Dict, TypedDict, Any
from src.utils.slide_context import slide_context # Assuming this is a class you have defined

class State(TypedDict, total=False):
    """
    The data that flows through the graph. This only contains items that are
    created or modified by the nodes during execution.
    """
    # Input
    docx_file: str

    # Document processing state
    document_title: str
    document_structure: List[Dict]
    document_outline: List[Dict]
    slide_chunks: List[str]
    slide_positions: List[Any]
    slide_context_maps: List[str]
    slide_plans: List[Dict]

    # Slide generation loop state
    current_slide_index: int
    length_slide_chunks: int
    current_slide_text: str
    current_tool_call: Dict
    current_html_content: str
    current_html_path: str
    current_image_path: str
    previous_image_path: str
    previous_accepted_tool_call: Dict
    previous_slide_context: slide_context

    # Retry and evaluation state
    retry_count: int
    vlm_decision: str
    vlm_feedback: str

    # History and final results
    messages: List[Dict[str, Any]]
    final_slides: List[Dict]
    all_debug_info: List[Dict]