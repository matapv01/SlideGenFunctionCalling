"""
Content slide tools - Body and content templates.
Includes 50+ content layout variations.
"""

from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field


class GenericContentSlideInput(BaseModel):
    """Generic input schema for content slides - accepts any parameters as kwargs."""
    main_title: Optional[str] = Field(default=None, description="Main title of the slide")
    content_text: Optional[str] = Field(default=None, description="Main content text")
    items: Optional[List[str]] = Field(default=None, description="List of items for grid/list layouts")
    left_title: Optional[str] = Field(default=None, description="Left column title")
    right_title: Optional[str] = Field(default=None, description="Right column title")
    left_content: Optional[str] = Field(default=None, description="Left column content")
    right_content: Optional[str] = Field(default=None, description="Right column content")
    bg_color: Optional[str] = Field(default="#FFFFFF", description="Background color")
    text_color: Optional[str] = Field(default="#333333", description="Text color")
    accent_color: Optional[str] = Field(default="#2563EB", description="Accent color")
    image_url: Optional[str] = Field(default=None, description="Image URL")
    kwargs: Optional[Dict[str, Any]] = Field(default={}, description="Additional parameters")


class GenerateContentSlideInput(BaseModel):
    """Input schema for generate_content_slide."""
    main_title: str = Field(..., description="Main title of the slide")
    items: List[str] = Field(..., description="List of item titles for grid")
    main_title_font_size: str = Field(default="60px", description="Title font size")
    number_font_size: str = Field(default="70px", description="Number font size")
    item_title_font_size: str = Field(default="28px", description="Item title font size")
    main_title_color: str = Field(default="#555555", description="Title color")
    number_color: str = Field(default="#a2c4c9", description="Number color")
    item_title_color: str = Field(default="#555555", description="Item title color")
    background_color: str = Field(default="#ffffff", description="Background color")
    accent_color: str = Field(default="#a2c4c9", description="Accent color")
    num_columns: int = Field(default=3, description="Number of columns")
    num_rows: int = Field(default=2, description="Number of rows")


class GenerateTwoColumnSlideInput(BaseModel):
    """Input schema for generate_two_column_slide."""
    main_title: str = Field(..., description="Main title")
    left_column_titles: List[str] = Field(..., description="Left column titles")
    left_column_texts: List[str] = Field(..., description="Left column texts")
    right_column_titles: List[str] = Field(..., description="Right column titles")
    right_column_texts: List[str] = Field(..., description="Right column texts")
    main_title_font_size: str = Field(default="36px", description="Title font size")
    column_title_font_size: str = Field(default="24px", description="Column title font size")
    column_text_font_size: str = Field(default="16px", description="Column text font size")


class GenerateComparisonSlideInput(BaseModel):
    """Input schema for generate_comparison_slide."""
    main_title: str = Field(..., description="Main title")
    left_title: str = Field(..., description="Left column title")
    right_title: str = Field(..., description="Right column title")
    left_text: str = Field(..., description="Left column text")
    right_text: str = Field(..., description="Right column text")
    left_icon: str = Field(default="gavel", description="Left icon")
    right_icon: str = Field(default="scales", description="Right icon")


class GenerateProcessSlideInput(BaseModel):
    """Input schema for generate_process_slide."""
    main_title: str = Field(..., description="Main title")
    left_title: str = Field(..., description="Left box title")
    right_title: str = Field(..., description="Right box title")
    left_content: str = Field(..., description="Left box content")
    right_content: str = Field(..., description="Right box content")
    main_title_font_size: str = Field(default="36px", description="Title font size")
    left_box_color: str = Field(default="#8cbeca", description="Left box color")
    right_box_color: str = Field(default="#c5e1e8", description="Right box color")


CONTENT_TOOLS_INFO = {
    "generate_content_slide": {
        "description": "Grid layout content slide",
        "input_schema": GenericContentSlideInput,
    },
    "generate_two_column_slide": {
        "description": "Two-column content slide",
        "input_schema": GenericContentSlideInput,
    },
    "generate_project_circles_slide": {
        "description": "Project circles layout slide",
        "input_schema": GenericContentSlideInput,
    },
    "generate_comparison_slide": {
        "description": "Comparison slide with two columns",
        "input_schema": GenericContentSlideInput,
    },
    "generate_process_slide": {
        "description": "Process flow slide with arrow",
        "input_schema": GenericContentSlideInput,
    },
    "generate_process_steps_slide": {
        "description": "Process steps vertical layout",
        "input_schema": GenericContentSlideInput,
    },
    "generate_icon_list_slide_2": {
        "description": "Icon list slide with decorative elements",
        "input_schema": GenericContentSlideInput,
    },
    "generate_image_cutout_list_slide": {
        "description": "List slide with image cutouts",
        "input_schema": GenericContentSlideInput,
    },
    "generate_body_slide2": {"description": "Body slide variant 2", "input_schema": GenericContentSlideInput},
    "generate_body_slide3": {"description": "Body slide variant 3", "input_schema": GenericContentSlideInput},
    "generate_body_slide4": {"description": "Body slide variant 4", "input_schema": GenericContentSlideInput},
    "generate_body_slide5": {"description": "Body slide variant 5", "input_schema": GenericContentSlideInput},
    "generate_body_slide6": {"description": "Body slide variant 6", "input_schema": GenericContentSlideInput},
    "generate_body_slide7": {"description": "Body slide variant 7", "input_schema": GenericContentSlideInput},
    "generate_body_slide10": {"description": "Body slide variant 10", "input_schema": GenericContentSlideInput},
    "generate_body_slide11": {"description": "Body slide variant 11", "input_schema": GenericContentSlideInput},
    "generate_body_slide12": {"description": "Body slide variant 12", "input_schema": GenericContentSlideInput},
    "generate_body_slide13": {"description": "Body slide variant 13", "input_schema": GenericContentSlideInput},
    "generate_body_slide14": {"description": "Body slide variant 14", "input_schema": GenericContentSlideInput},
    "generate_body_slide15": {"description": "Body slide variant 15", "input_schema": GenericContentSlideInput},
    "generate_body_slide16": {"description": "Body slide variant 16", "input_schema": GenericContentSlideInput},
    "generate_body_slide17": {"description": "Body slide variant 17", "input_schema": GenericContentSlideInput},
    "generate_body_slide18": {"description": "Body slide variant 18", "input_schema": GenericContentSlideInput},
    "generate_body_slide19": {"description": "Body slide variant 19", "input_schema": GenericContentSlideInput},
    "generate_body_slide20": {"description": "Body slide variant 20", "input_schema": GenericContentSlideInput},
    "generate_strategy_slide": {"description": "Strategy overview slide", "input_schema": GenericContentSlideInput},
    "generate_main_points_slide": {"description": "Main points highlight slide", "input_schema": GenericContentSlideInput},
    "generate_elegant_points_slide": {"description": "Elegant points listing", "input_schema": GenericContentSlideInput},
    "generate_horizontal_timeline_slide": {"description": "Timeline slide", "input_schema": GenericContentSlideInput},
    "generate_corporate_content_slide": {"description": "Corporate content layout", "input_schema": GenericContentSlideInput},
    "generate_split_content_slide": {"description": "Split content layout", "input_schema": GenericContentSlideInput},
    "generate_corporate_multicolumn_slide": {"description": "Multi-column corporate layout", "input_schema": GenericContentSlideInput},
    "generate_corporate_grid_slide": {"description": "Corporate grid layout", "input_schema": GenericContentSlideInput},
    "generate_business_overview_slide": {"description": "Business overview", "input_schema": GenericContentSlideInput},
    "generate_vision_mission_slide": {"description": "Vision and mission slide", "input_schema": GenericContentSlideInput},
    "generate_strategic_goals_slide": {"description": "Strategic goals slide", "input_schema": GenericContentSlideInput},
    "generate_service_roadmap_slide": {"description": "Service roadmap", "input_schema": GenericContentSlideInput},
    "generate_financial_projections_slide_dark": {"description": "Financial projections", "input_schema": GenericContentSlideInput},
    "generate_minimalist_tech_list_slide": {"description": "Tech minimalist list", "input_schema": GenericContentSlideInput},
    "generate_centered_tech_columns_slide": {"description": "Centered tech columns", "input_schema": GenericContentSlideInput},
    "generate_split_layout_list_slide": {"description": "Split layout list", "input_schema": GenericContentSlideInput},
    "generate_reference_slide": {"description": "Reference slide", "input_schema": GenericContentSlideInput},
    "generate_icon_list_slide": {"description": "Icon list slide", "input_schema": GenericContentSlideInput},
    "generate_flexible_columns_slide": {"description": "Flexible columns layout", "input_schema": GenericContentSlideInput},
    "generate_text_with_image_slide": {"description": "Text with image layout", "input_schema": GenericContentSlideInput},
    "generate_instructions_slide": {"description": "Instructions slide", "input_schema": GenericContentSlideInput},
    "generate_geometric_split_content_slide": {"description": "Geometric split layout", "input_schema": GenericContentSlideInput},
    "generate_geometric_split_content_slide_2": {"description": "Geometric split layout variant 2", "input_schema": GenericContentSlideInput},
    "generate_geometric_image_content_slide": {"description": "Geometric image content", "input_schema": GenericContentSlideInput},
    "generate_geometric_content_slide": {"description": "Geometric content layout", "input_schema": GenericContentSlideInput},
    "generate_geometric_grid_slide": {"description": "Geometric grid layout", "input_schema": GenericContentSlideInput},
    "generate_memphis_content_slide": {"description": "Memphis style content", "input_schema": GenericContentSlideInput},
    "generate_memphis_multicolumn_slide": {"description": "Memphis multi-column", "input_schema": GenericContentSlideInput},
    "generate_memphis_grid_slide": {"description": "Memphis grid layout", "input_schema": GenericContentSlideInput},
    "generate_premium_abstract_slide": {"description": "Premium abstract layout", "input_schema": GenericContentSlideInput},
}
