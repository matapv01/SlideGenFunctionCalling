# src/graph/stage.py
import operator
from typing import Annotated, List, Dict, Any, Literal
from typing_extensions import TypedDict
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
    slide_topic: str = Field(
        default="",
        description=(
            "A concise semantic subject for this slide. Use it to guide the "
            "layout, editable text, icons, and image-search queries."
        ),
    )
    slide_purpose: str = Field(
        default="",
        description=(
            "One short sentence explaining the slide's main message in the "
            "context of the whole deck. Mention the concrete subject, person, "
            "event, place, time period, or relationship that a relevant visual "
            "must support. This is semantic context for image verification, not "
            "a layout instruction."
        ),
    )
    thought: str = Field(
        description=(
            "A concise creative brief of at most two sentences covering the "
            "message hierarchy, layout, and visual emphasis. Follow the shared "
            "deck style contract; do not invent a separate palette or typography."
        )
    )
    image_mode: Literal["none", "semantic", "decorative"] = Field(
        default="none",
        description=(
            "Default to none. Choose semantic only when an image is a concrete "
            "subject to search directly. Choose decorative only when the slide "
            "genuinely benefits from a supporting visual or is an intentional "
            "intro/transition/closing composition; never search a person's name, "
            "book title, or literal slide title."
        ),
    )
    image_strategy: Literal["semantic", "decorative"] = Field(
        default="decorative",
        description=(
            "Legacy compatibility field. Keep aligned with image_mode when the "
            "mode is semantic or decorative; use decorative for none."
        ),
    )
    image_theme: str = Field(
        default="",
        description=(
            "A short lower-case English visual motif for image search. For semantic "
            "imagery use the concrete subject; for decorative imagery use a "
            "safe conceptual motif such as 'workflow collaboration' or "
            "'customer support conversation'. Never use a person's name, "
            "book title, company name, or literal slide heading."
        ),
    )
    action: ToolCategory = Field(
        description="The single, most appropriate category of tools to use for generating this slide."
    )


class DeckStylePlan(BaseModel):
    """One visual contract shared by every slide in a deck."""

    deck_topic: str = "Untitled presentation"
    visual_direction: str = "Coherent editorial presentation with clear hierarchy"
    theme_name: str = "Modern editorial"
    font_family: str = "Arial"
    title_font_min: int = 36
    title_font_max: int = 48
    body_font_min: int = 18
    body_font_max: int = 28
    background_color: str = "#F8FAFC"
    primary_color: str = "#0F172A"
    secondary_color: str = "#475569"
    accent_color: str = "#0D9488"
    text_color: str = "#1F2937"
    image_style: str = "Clean editorial photography with consistent color grading"
    chart_style: str = "Minimal charts with direct labels and restrained grid lines"
    layout_density: Literal["airy", "balanced", "compact"] = "balanced"

class SlideJob(TypedDict, total=False):
    """Canonical scheduler input shared by every slide source."""

    index: int
    section_id: str
    section_order: int
    order_in_section: int
    slide_type: str
    content: Any
    context_map: str
    position: Any
    plan: Dict[str, Any]
    assigned_tool_candidates: List[str]
    excluded_tools: List[str]

class State(TypedDict, total=False):
    """
    The data that flows through the graph. This only contains items that are
    created or modified by the nodes during execution.
    """
    # Input
    docx_file: str
    slide_options: Dict  # Options for slide generation
    output_format: str  # XML-only output format


    # Document processing state
    document_title: str
    document_structure: List[Dict]
    plain_text: str  # Plain text content for auto-structure generation

    document_outline: List[Dict]
    slide_chunks: List[str]
    slide_positions: List[Any]
    section_ids: List[str]
    slide_context_maps: List[str]
    slide_plans: List[Dict]  # Contains 'action' field from planner (INTRO_TOOLS, etc.)
    deck_style_plan: Dict[str, Any]
    document_images: List[Dict[str, Any]]
    document_image_assignments: List[Dict[str, Any]]
    user_request: str

    # Parallel section orchestration. ``batch_results`` uses a reducer because
    # multiple LangGraph Send workers write to it concurrently.
    slide_jobs: List[Dict[str, Any]]
    section_batches: List[Dict[str, Any]]
    section_batch: Dict[str, Any]
    batch_slide_jobs: List[Dict[str, Any]]
    batch_id: str
    batch_cursor: int
    batch_done: bool
    deck_slide_count: int
    batch_results: Annotated[List[Dict[str, Any]], operator.add]
    batch_layout_signatures: List[Dict[str, Any]]
    duplicate_excluded_tools: List[str]
    overflow_excluded_tools: List[str]
    duplicate_retry_count: int
    duplicate_detected: bool
    layout_signature: Dict[str, Any]
    duplicate_report: Dict[str, Any]
    assigned_tool_candidates: List[str]
    preferred_tool_name: str
    layout_assignment_report: Dict[str, Any]

    # Slide generation loop state
    current_slide_index: int
    length_slide_chunks: int
    current_slide_text: str
    current_slide_plan: Dict
    current_slide_context_map: str
    current_slide_position: Any
    current_slide_type: str
    current_document_images: List[Dict[str, Any]]
    force_no_image_layout: bool
    current_tool_plan: List[Dict]
    current_search_history: List[Dict]
    current_tool_call: Dict
    current_xml_content: str
    current_xml_path: str
    current_image_path: str
    current_transitions: List[Dict[str, str]]
    current_contrast_report: List[Dict[str, Any]]
    previous_image_path: str
    highlight_color: str  # Color for highlighting key phrases in content slides
    candidate_tools: List[Any]  # Cached retrieved tools for retry attempts
    last_processed_slide_index: int  # Track slide index to reset tool cache on new slide

    # Retry and evaluation state
    retry_count: int
    executor_retry_count: int
    overflow_retry_count: int
    llm : Any
    vlm_decision: str
    vlm_feedback: str
    vlm_evaluation_path: str
    vlm_evaluation_url: str
    overflow_report: Dict[str, Any]
    overflow_rewrite_count: int
    overflow_failed: bool
    last_valid_xml_content: str
    last_valid_tool_call: Dict[str, Any]
    executor_decision: str  # "pass" or "fail" from tool_call_executor
    executor_feedback: str  # Detailed error description from executor

    # History and final results
    messages: List[Dict[str, Any]]
    final_slides: List[Dict]
    all_debug_info: List[Dict]
