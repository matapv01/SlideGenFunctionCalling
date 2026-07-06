from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from .html_lib_waterfall import (
    generate_waterfall_chart_slide_1,
    generate_waterfall_chart_slide_2,
    generate_waterfall_chart_slide_3,
)

class GenerateWaterfallChartSlide1(BaseModel):
    """Input schema for generate_waterfall_chart_slide_1"""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters).")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    insight: str = Field(..., description="Text insight or general description.")
    categories: List[str] = Field(..., description="List of categories for the X-axis.")
    values: List[float] = Field(
        ...,
        description="List of numeric values corresponding to each category. Positive values represent increase, negative represent decrease. Example: [5000, 3000, 1500, -2000, -1000, -500, 6000]"
    )
    is_total: List[bool] = Field(
        ...,
        description="List of booleans indicating if the value is a total (starts from 0) or a delta (starts from previous value). Example: [True, False, False, False, False, False, True]"
    )
    unit: str = Field(..., description="Unit appended to values (e.g., '$', '%', 'M').")
    show_value: bool = Field(..., description="Whether numeric values are displayed above chart bars.")
    positive_color: str = Field(..., description="Hex color for positive values (increase).")
    negative_color: str = Field(..., description="Hex color for negative values (decrease).")
    total_color: str = Field(..., description="Hex color for total values.")
    accent_color: str = Field(..., description="Hex color for the accent elements.")
    main_title_color: str = Field(default="#2C3E50", description="Hex color for the main title part.")
    subtitle_color: str = Field(default="#7F8C8D", description="Hex color for the subtitle text.")
    insight_text_color: str = Field(default="#34495E", description="Hex color for the insights description text.")
    y_axis_label: str = Field(..., description="Label for Y-axis.")

class GenerateWaterfallChartSlide2(BaseModel):
    """Input schema for generate_waterfall_chart_slide_2"""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters).")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    insight: str = Field(..., description="Text insight or general description.")
    categories: List[str] = Field(..., description="List of categories for the X-axis.")
    values: List[float] = Field(
        ...,
        description="List of numeric values corresponding to each category. Positive values represent increase, negative represent decrease. Example: [5000, 3000, 1500, -2000, -1000, -500, 6000]"
    )
    is_total: List[bool] = Field(
        ...,
        description="List of booleans indicating if the value is a total (starts from 0) or a delta (starts from previous value). Example: [True, False, False, False, False, False, True]"
    )
    unit: str = Field(..., description="Unit appended to values (e.g., '$', '%', 'M').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed above chart bars.")
    positive_color: str = Field(default="#2ECC71", description="Hex color for positive values (increase).")
    negative_color: str = Field(default="#E74C3C", description="Hex color for negative values (decrease).")
    total_color: str = Field(default="#3498DB", description="Hex color for total values.")
    accent_color: str = Field(default="#3498DB", description="Hex color for the accent elements.")
    main_title_color: str = Field(default="#2C3E50", description="Hex color for the main title part.")
    subtitle_color: str = Field(default="#7F8C8D", description="Hex color for the subtitle text.")
    insight_text_color: str = Field(default="#34495E", description="Hex color for the insights description text.")
    y_axis_label: str = Field(default="Amount", description="Label for Y-axis.")
    second_insight: str = Field(..., description="Second text insight positioned below the chart.")
    image_url: str = Field(..., description="URL of the background image to display on the slide.")

class GenerateWaterfallChartSlide3(BaseModel):
    """Input schema for generate_waterfall_chart_slide_3."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters).")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    insight: str = Field(..., description="Primary text insight positioned in the top wrapper of the chart.")
    categories: List[str] = Field(..., description="List of categories for the X-axis of the waterfall chart. Ordered sequentially. Example: ['Starting Cash', 'Sales', 'Services', 'Fixed Costs', 'Variable Costs', 'Taxes', 'Ending Cash']")
    values: List[float] = Field(..., description="List of numeric values corresponding to each category. Positive values represent increase, negative represent decrease. Example: [5000, 3000, 1500, -2000, -1000, -500, 6000]")
    is_total: List[bool] = Field(..., description="List of booleans indicating if the value is a total (starts from 0) or a delta (starts from previous value). Example: [True, False, False, False, False, False, True]")
    unit: str = Field(..., description="Unit appended to values (e.g., '$', '%', 'M').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed above chart bars.")
    positive_color: str = Field(default="#2ECC71", description="CSS hex color for positive values (increase).")
    negative_color: str = Field(default="#E74C3C", description="CSS hex color for negative values (decrease).")
    total_color: str = Field(default="#3498DB", description="CSS hex color for total values.")
    accent_color: str = Field(default="#3498DB", description="CSS hex color for accent elements and decorative shapes.")
    main_title_color: str = Field(default="#2C3E50", description="CSS hex color for the main title.")
    subtitle_color: str = Field(default="#7F8C8D", description="CSS hex color for the subtitle.")
    insight_text_color: str = Field(default="#34495E", description="CSS hex color for the insight text.")
    y_axis_label: str = Field(..., description="Label displayed vertically on the Y-axis.")
    second_insight: str = Field(..., description="Secondary insight text positioned below the waterfall chart.")
    image_url: str = Field(..., description="URL of the background image to display on the slide.")

WATERFALL_TOOLS = [
    StructuredTool.from_function(
        func=generate_waterfall_chart_slide_1,
        name="generate_waterfall_chart_slide_1",
        description=(
            "Generates a Waterfall Chart slide.\n\n"
            "Slide layout:\n"
            "- Top section: contains the main title and subtitle.\n"
            "- Main content area is divided into two panels:\n"
            "  • Left panel: contains an insight text block and a legend for Increase, Decrease, and Total.\n"
            "  • Right panel: displays the waterfall chart visualization showing cumulative effect of sequentially introduced positive or negative values.\n\n"
            "Additional layout elements:\n"
            "- Clean background with decorative geometric shapes at the top-left."
        ),
        args_schema=GenerateWaterfallChartSlide1
    ),
    StructuredTool.from_function(
        func=generate_waterfall_chart_slide_2,
        name="generate_waterfall_chart_slide_2",
        description=(
            "Generates a dual-chart Waterfall & Pie Chart slide.\n\n"
            "Slide layout:\n"
            "- Top section: contains the main title and subtitle.\n"
            "- Main content area is divided into two panels:\n"
            "  • Left panel: contains the waterfall chart and a pie chart displayed side-by-side, with a secondary insight below them.\n"
            "  • Right panel: displays the primary insight text block and a combined legend.\n\n"
            "Additional layout elements:\n"
            "- Support for a full background image and decorative geometric shapes."
        ),
        args_schema=GenerateWaterfallChartSlide2
    ),
    StructuredTool.from_function(
        func=generate_waterfall_chart_slide_3,
        name="generate_waterfall_chart_slide_3",
        description=(
            "Generates a multi-chart slide with a Waterfall chart, a Pie chart, and a Mindmap.\n\n"
            "Slide layout:\n"
            "- Top section: displays the main title and subtitle.\n"
            "- Main content area: arranged into multiple panels using flexbox layout.\n"
            "  • Waterfall panel: a wrapped container holding the waterfall chart and its corresponding top and bottom insights.\n"
            "  • Legend panel: a vertical legend positioned between charts.\n"
            "  • Pie panel: a wrapped container holding the pie chart and its top/bottom insights.\n"
            "  • Mindmap panel: a radial mindmap diagram with its own insight wrappers.\n\n"
            "Additional layout elements:\n"
            "- Floating background image with geometric accent shapes."
        ),
        args_schema=GenerateWaterfallChartSlide3
    )
]

