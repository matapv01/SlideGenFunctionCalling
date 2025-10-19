from __future__ import annotations

from typing_extensions import TypedDict

class PreviousSlideContext(TypedDict):

    content: str
    function_call: dict
    image_path: str

class SlidegenState(TypedDict):
    """
    The data that flows through the graph. This only contains items that are
    created or modified by the nodes during execution.
    """
    # Input
    object_name: str

    # Document processing state
    document_title: str
    document_structure: list[dict]
    document_outline: list[dict]
    slide_chunks: list[str]
    slide_positions: list
    slide_context_maps: list[str]
    slide_plans: list[dict]

    # Slide generation loop state
    current_slide_index: int
    length_slide_chunks: int
    current_slide_text: str
    current_tool_call: dict
    current_html_content: str
    current_html_path: str
    current_image_path: str
    previous_image_path: str
    previous_accepted_tool_call: dict
    previous_slide_context: PreviousSlideContext

    # Retry and evaluation state
    retry_count: int
    vlm_decision: str
    vlm_feedback: str

    # History and final results
    messages: list[dict]
    final_slides: list[dict]
    all_debug_info: list[dict]