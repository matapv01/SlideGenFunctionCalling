# src/graph/stage.py
from typing import List, Dict, TypedDict, Any, Literal
from pydantic import BaseModel, Field

# Define the allowed tool categories based on your TOOLS_DICT keys
ToolCategory = Literal['INTRO_TOOLS', 'TRANSITION_TOOLS', 'CONTENT_TOOLS', 'TEAM_TOOLS', 'THANK_YOU_TOOLS', 'CHART_TOOLS']


class Evaluation(BaseModel):
    """
    An object containing detailed feedback and final decision about the slide.
    """
    feedback: str = Field(description="Detailed analysis of what's good and what needs improvement in the slide. Provide specific suggestions to make the slide better.")
    decision: Literal["accept", "deny"] = Field(description="Final decision. 'accept' if slide is good, 'deny' if it needs to be redone.")


class SlidePlan(BaseModel):
    """Defines the structure of a slide plan."""
    thought: str = Field(
        description="A detailed creative brief for designing the slide. Describe the desired visual style, color palette, layout, typography, and whether to include images, icons, or specific visual elements. This should be a guide for the next step."
    )
    action: ToolCategory = Field(
        description="The single, most appropriate category of tools to use for generating this slide."
    )

class slide_context(TypedDict):
    """Lưu trữ context của slide trước đó."""
    content: str
    function_call: Dict
    image_path: str

class State(TypedDict, total=False):
    """
    The data that flows through the graph. This only contains items that are
    created or modified by the nodes during execution.
    """
    # Input
    docx_file: str
    slide_options: Dict  # Options for slide generation
    workflow_mode: str  # Workflow mode (auto, no_structure, manual)


    # Document processing state
    document_title: str
    document_structure: List[Dict]
    plain_text: str  # Plain text content for auto-structure generation

    document_outline: List[Dict]
    slide_chunks: List[str]
    slide_positions: List[Any]
    slide_context_maps: List[str]
    slide_plans: List[Dict]  # Contains 'action' field from planner (INTRO_TOOLS, etc.)

    # Slide generation loop state
    current_slide_index: int
    length_slide_chunks: int
    current_slide_text: str
    current_slide_plan: Dict
    current_slide_context_map: str
    current_tool_plan: List[Dict]
    current_search_history: List[Dict]
    current_tool_call: Dict
    current_html_content: str
    current_html_path: str
    current_image_path: str
    previous_image_path: str
    previous_accepted_tool_call: Dict
    previous_slide_context: slide_context
    highlight_color: str  # Color for highlighting key phrases in content slides
    previous_transition_tool_call: Dict  # Store previous transition tool for consistency

    # Retry and evaluation state
    retry_count: int
    llm : Any
    vlm_decision: str
    vlm_feedback: str
    executor_decision: str  # "pass" or "fail" from tool_call_executor
    executor_feedback: str  # Detailed error description from executor

    # History and final results
    messages: List[Dict[str, Any]]
    final_slides: List[Dict]
    all_debug_info: List[Dict]
