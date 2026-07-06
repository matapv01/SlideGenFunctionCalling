from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from .html_lib_bar import (
    generate_bar_chart_slide_1,
    generate_bar_chart_slide_2,
    generate_bar_chart_slide_3,
    generate_bar_chart_slide_4,
    generate_bar_chart_slide_5,
)


class GenerateBarChartSlide1(BaseModel):
    """Input schema for generate_bar_chart_slide_1"""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters).")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    insight: str = Field(..., description="Text insight or general description.")
    categories: List[str] = Field(..., description="List of categories for the X-axis.")
    series: List[float] = Field(
        ...,
        description="List of numeric values corresponding to each category for the bar sizes and labels. Example: [45, 52, 68, 58]"
    )
    unit: str = Field(..., description="Unit appended to values (e.g., '%', 'M').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed above chart bars.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed on the left panel.")
    colors: List[str] = Field(default=["#1B2559", "#FF6B35", "#4B5563", "#9CA3AF"], description="List of hex colors for the bars and icons.")
    accent_color: str = Field(default="#FF6B35", description="Hex color for the accent elements.")
    main_title_color: str = Field(default="#1B2559", description="Hex color for the main title part.")
    subtitle_color: str = Field(default="#6B7280", description="Hex color for the subtitle text.")
    insight_text_color: str = Field(default="#374151", description="Hex color for the insights description text.")
    y_axis_label: str = Field(default="Volume", description="Label for Y-axis.")

class GenerateBarChartSlide2(BaseModel):
    """Input schema for generate_bar_chart_slide_2"""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters).")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    insight: str = Field(..., description="Text insight or general description.")
    x_axis: str = Field(..., description="Label for X-axis.")
    y_axis: str = Field(..., description="Label for Y-axis.")
    unit: str = Field(..., description="Unit appended to values (e.g., '%', 'M').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed above chart bars.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed.")
    y_axis_min: float = Field(default=0, description="Minimum value of Y-axis.")
    y_axis_max: float = Field(default=None, description="Maximum value of Y-axis. If None, auto-calculated.")
    colors: List[str] = Field(default=["#00695C", "#26A69A", "#4DD0E1", "#0277BD", "#00838F"], description="List of hex colors for the bars and icons.")
    categories: List[str] = Field(default=["Pacific", "Atlantic", "Indian Ocean", "Mediterranean"], description="List of categories or regions to display.")
    series: List[float] = Field(
        ...,
        description="List of numeric values corresponding to each category for the bar sizes and labels. Example: [120, 85, 60, 45]"
    )
    main_title_color: str = Field(default="#104c64", description="Hex color for the main title part.")
    subtitle_color: str = Field(default="#457b8c", description="Hex color for the subtitle text.")
    insight_text_color: str = Field(default="#2c5f70", description="Hex color for the insights description text.")

class GenerateBarChartSlide3(BaseModel):
    """Input schema for generate_bar_chart_slide_3"""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters).")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    x_axis: str = Field(..., description="Label for X-axis.")
    y_axis: str = Field(..., description="Label for Y-axis.")
    unit: str = Field(..., description="Unit appended to values (e.g., '%', 'M').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed above chart bars.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed on the left panel.")
    y_axis_min: float = Field(default=0, description="Minimum value of Y-axis.")
    y_axis_max: float = Field(default=None, description="Maximum value of Y-axis. If None, auto-calculated.")
    colors: List[str] = Field(..., description="List of hex colors for the bars and icons.")
    categories: List[str] = Field(..., description="List of categories or regions to display.")
    series: List[float] = Field(
        ...,
        description="List of numeric values corresponding to each category for the bar sizes and labels. Example: [20, 30, 50, 70]"
    )
    data_label_format: str = Field(default="{value}", description="Format string for data labels.")
    main_title_color: str = Field(default="#4A5E7B", description="Hex color for the main title part.")
    subtitle_color: str = Field(default="#8E97A4", description="Hex color for the subtitle text.")
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=2022&auto=format&fit=crop",
        description="URL of the image to display in the right capsule panel."
    )

class GenerateBarChartSlide4(BaseModel):
    """Input schema for generate_bar_chart_slide_4"""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters).")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    insight: str = Field(..., description="Text insight or general description.")
    x_axis: str = Field(..., description="Label for X-axis (e.g., 'Regions').")
    y_axis: str = Field(..., description="Label for Y-axis (e.g., 'Percentage').")
    unit: str = Field(..., description="Unit appended to values (e.g., '%', 'M').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed above chart bars.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed on the left and right panels.")
    y_axis_min: float = Field(default=0, description="Minimum value of Y-axis.")
    y_axis_max: float = Field(default=None, description="Maximum value of Y-axis.")
    colors: List[str] = Field(..., description="List of hex colors for the bars and icons.")
    categories: List[str] = Field(..., description="List of categories or regions to display.")
    insights: List[str] = Field(..., description="List of text descriptions or insights corresponding to each category.")
    series: List[float] = Field(
        ...,
        description="List of numeric values for each category. Example: [20, 30, 50, 70]"
    )
    accent_color: str = Field(default="#FF6B35", description="Hex color for the accent elements.")
    main_title_color: str = Field(default="#1B2559", description="Hex color for the main title part.")
    subtitle_color: str = Field(default="#6B7280", description="Hex color for the subtitle text.")
    insight_text_color: str = Field(default="#374151", description="Hex color for the insights description text.")

class GenerateBarChartSlide5(BaseModel):
    """Input schema for generate_bar_chart_slide_5"""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters). Example: 'Business Inforgraphic'")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating report name and time period.")
    unit: str = Field(..., description="Unit appended to values (e.g., '%', 'M', 'K', ' USD'). Appears in data labels.")
    colors: List[str] = Field(..., description="List of hex colors for the bars and icons. Theme defaults to navy, orange, gray, green, blue.")
    categories: List[str] = Field(
        ..., 
        description="List of categories or regions to display. Example: ['North America', 'Europe', 'Asia', 'South America', 'Africa']"
    )
    insights: List[str] = Field(
        ...,
        description="List of text descriptions or insights corresponding to each category. Must have the same length as categories. Example: ['Strong market presence with 30% growth', 'Steady performance with 5% increase']"
    )
    series: List[float] = Field(
        ...,
        description="List of numeric values corresponding to each category for the bar sizes and labels. Must have the same length as categories. Example: [45, 52, 68, 58, 34]"
    )
    accent_color: str = Field(default="#FF6B35", description="Hex color for the accent elements (e.g., orange).")
    main_title_color: str = Field(default="#1B2559", description="Hex color for the main title part (e.g., navy).")
    subtitle_color: str = Field(default="#6B7280", description="Hex color for the subtitle text (e.g., gray).")
    insights_text_color: str = Field(default="#374151", description="Hex color for the insights description text.")
    
BAR_TOOLS = [
    StructuredTool.from_function(
        func=generate_bar_chart_slide_1,
        name="generate_bar_chart_slide_1",
        description=(
            "Generates a Logistic Company-themed Grouped Bar Chart slide.\n\n"
            "Slide layout:\n"
            "- Top section: contains the main title and subtitle.\n"
            "- Main content area is divided into two panels:\n"
            "  • Left panel: contains an insight text block and a horizontal legend.\n"
            "  • Right panel: displays the grouped bar chart visualization with grid lines and labeled axes.\n\n"
            "Additional layout elements:\n"
            "- The background is white with decorative geometric shapes at the top-left and bottom-right corners."
        ),
        args_schema=GenerateBarChartSlide1
    ),
    StructuredTool.from_function(
        func=generate_bar_chart_slide_2,
        name="generate_bar_chart_slide_2",
        description=(
            "Generates an Ocean-themed Grouped Bar Chart slide.\n\n"
            "Slide layout:\n"
            "- Top section: contains the main title and subtitle.\n"
            "- Main content area is divided into two columns:\n"
            "  • Left column: displays a text insight block and a vertical legend.\n"
            "  • Right column (highlighted with a blurred background): displays the grouped bar chart.\n\n"
            "Additional layout elements:\n"
            "- The background features a light cyan water-like gradient with soft floating decorative bubbles."
        ),
        args_schema=GenerateBarChartSlide2
    ),
    StructuredTool.from_function(
        func=generate_bar_chart_slide_3,
        name="generate_bar_chart_slide_3",
        description=(
            "Generates an educational themed Grouped Bar Chart slide with an image capsule layout.\n\n"
            "Slide layout:\n"
            "- Top section: contains the main title and subtitle aligned to the left.\n"
            "- Main content area is divided into two columns:\n"
            "  • Left panel (larger): displays a horizontal legend at the top and the grouped bar chart visualization below it.\n"
            "  • Right panel (smaller): displays a large, vertical, capsule-shaped image.\n\n"
            "Additional layout elements:\n"
            "- The background is light beige with small decorative star elements.\n"
            "- The chart has no enclosing box, blending seamlessly with the background.\n"
            "- This layout is highly effective for visual storytelling, combining data visualization on the left with a prominent thematic image on the right."
        ),
        args_schema=GenerateBarChartSlide3
    ),
    StructuredTool.from_function(
        func=generate_bar_chart_slide_4,
        name="generate_bar_chart_slide_4",
        description=(
            "Generates a Logistic Company-themed Grouped Bar Chart slide with a three-column layout.\n\n"
            "Slide layout:\n"
            "- Top section: contains the main title and subtitle aligned to the left, and a faded '2024 REPORT' text aligned to the right.\n"
            "- Main content area is divided into three columns:\n"
            "  • Left panel: displays the first half of the legend (category names, values, and text insights).\n"
            "  • Center panel: displays the grouped bar chart visualization with grid lines and labeled axes.\n"
            "  • Right panel: displays the second half of the legend.\n\n"
            "Additional layout elements:\n"
            "- The background is white with decorative geometric shapes at the top-left and bottom-right corners.\n"
            "- The layout separates the chart in the center and surrounds it with detailed text insights on both sides."
        ),
        args_schema=GenerateBarChartSlide4
    ),
    StructuredTool.from_function(
        func=generate_bar_chart_slide_5,
        name="generate_bar_chart_slide_5",
        description=(
            "Generates a Logistic Company-themed Grouped Bar Chart slide with a clean, vertical list layout.\n\n"
            "Slide layout:\n"
            "- Top section: contains the main title and subtitle, centered.\n"
            "- Main content area: displays a vertical list of categories. Each category row consists of:\n"
            "  • A horizontal progress bar representing the value.\n"
            "  • The numeric value with its unit.\n"
            "  • A circular icon matching the category color.\n"
            "  • A text block containing the category name and its associated insight description, aligned to the right.\n\n"
            "Additional layout elements:\n"
            "- The background is white with decorative geometric shapes at the top-left and bottom-right corners.\n"
            "- This layout is highly effective for presenting detailed, itemized analysis where each data point requires an explanatory text."
        ),
        args_schema=GenerateBarChartSlide5
    ) 
]