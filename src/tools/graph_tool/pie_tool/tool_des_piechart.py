from pydantic import BaseModel, Field, List, Dict, Any
from langchain_core.tools import StructuredTool
from typing import Optional 
from html_lib_piechart import (
    generate_pie_chart_slide_8,
    generate_pie_chart_slide_1,
    generate_pie_chart_slide_2,
    generate_pie_chart_slide_3,
    generate_pie_chart_slide_4,
    generate_pie_chart_slide_5,
    generate_pie_chart_slide_6
)


class GeneratePieChartSlide1(BaseModel):
    """
    Input schema for generating a pie chart slide.
    """
    main_title: str = Field(default="Quarterly Revenue Breakdown", description="Primary heading of the slide.")
    subtitle: str = Field(default="Data Source: Financial Year 2025 Reports", description="Secondary text displayed below the main title.")
    insight: str = Field(default="AI Services now account for nearly half of total revenue growth.", description="Key analytical takeaway from the chart.")
    chart_type: str = Field(default="pie", description="Type of chart: 'pie' (full) or 'donut' (ring-style).")
    unit: str = Field(default="%", description="Unit of measurement for the values.")
    show_value: bool = Field(default=True, description="Whether to display numeric values on chart slices.")
    show_legend: bool = Field(default=True, description="Whether to display the legend.")
    data_label_format: str = Field(default="{value}{unit}", description="Template for data labels.")
    items: List[Dict[str, float]] = Field(
    ...,
    description="""
        List of data items.

        Structure:
        - items: list of objects
            - label: (str) Name of the category or data point
            - value: (float) Numeric value associated with the label

        Notes:
        - 'value' should be a number (int or float)
        - Labels should be unique to avoid duplication in visualization

        Example:
        [
            {"label": "AI Services", "value": 45},
            {"label": "Cloud Infrastructure", "value": 25}
        ]
        """
    )


class GeneratePieChartSlide2(BaseModel):
    """
    Input schema for generating a pie chart slide.
    """
    main_title: str = Field(..., description="Primary heading of the slide.")
    subtitle: str = Field(..., description="Secondary text displayed below the main title.")
    insight: str = Field(..., description="Key analytical takeaway from the chart.")
    chart_type: str = Field(default="pie", description="Type of chart: 'pie' (full) or 'donut' (ring-style).")
    unit: str = Field(..., description="Unit of measurement for the values.")
    show_value: bool = Field(default=True, description="Whether to display numeric values on chart slices.")
    show_legend: bool = Field(default=True, description="Whether to display the legend.")
    data_label_format: str = Field(default="{value}{unit}", description="Template for data labels.")
    items: List[Dict[str, float]] = Field(
        ...,
        description="""
        List of data items.

        Structure:
        - items: list of objects
            - label: (str) Name of the category or data point
            - value: (float) Numeric value associated with the label

        Notes:
        - 'value' should be a number (int or float)
        - Labels should be unique to avoid duplication in visualization

        Example:
        [
            {"label": "AI Services", "value": 45},
            {"label": "Cloud Infrastructure", "value": 25}
        ]
        """
    )

class GeneratePieChartSlide3Donut(BaseModel):
    """
    Input schema for generating a pie chart slide.
    """
    main_title: str = Field(..., description="Primary heading of the slide.")
    subtitle: str = Field(..., description="Secondary text providing context.")
    insight: str = Field(..., description="Key analytical takeaway from the chart.")
    chart_type: str = Field(default="donut", description="Type of chart: 'pie' (full) or 'donut' (ring-style).")
    unit: str = Field(default="%", description="Unit of measurement for values.")
    show_value: bool = Field(default=False, description="Whether to display numeric values on chart slices.")
    show_legend: bool = Field(default=True, description="Whether to display the legend.")
    data_label_format: str = Field(default="{value}{unit}", description="Template for data labels.")
    items: List[Dict[str, Any]] = Field(
        ...,
        description="""
        List of data items.

        Structure:
        - items: list of objects
            - label: (str) Name of the category or data point
            - value: (float) Numeric value associated with the label

        Notes:
        - 'value' should be a number (int or float)
        - Labels should be unique to avoid duplication in visualization

        Example:
        [
            {"label": "AI Services", "value": 45},
            {"label": "Cloud Infrastructure", "value": 25}
        ]
        """
    )


class GeneratePieChartSlide4(BaseModel):
    """
    Input schema for generate_pie_chart_slide_4.
    This schema defines all parameters required to generate
    a modern pie/donut chart slide with SVG rendering.
    """
    main_title: str = Field(..., description="Main title of the slide (10–60 characters).")
    subtitle: str = Field(..., description="Subtitle or data source displayed below the title.")
    insight: str = Field(..., description="Short analytical insight highlighting the key takeaway from the chart.")
    chart_type: str = Field(default="pie", description="Chart type: 'pie' or 'donut'. Determines whether the center is hollow.")
    unit: str = Field(default="%", description="Unit displayed in values (%, $, users, etc.).")
    show_value: bool = Field(default=True, description="Whether to display percentage values on chart slices.")
    show_legend: bool = Field(default=True, description="Whether to display the legend block.")
    data_label_format: str = Field(default="{value}{unit}", description="Template for slice labels. Supports {label}, {value}, {unit}.")
    items: List[Dict[str, Any]] = Field(
        ..., 
        description="""
        List of data items.

        Structure:
        - items: list of objects
            - label: (str) Name of the category or data point
            - value: (float) Numeric value associated with the label

        Notes:
        - 'value' should be a number (int or float)
        - Labels should be unique to avoid duplication in visualization

        Example:
        [
            {"label": "AI Services", "value": 45},
            {"label": "Cloud Infrastructure", "value": 25}
        ]
        """
    )

class GeneratePieChartSlide5(BaseModel):
    """
    Input schema for generate_pie_chart_slide_5.
    This schema defines all parameters required to generate a professional
    pie or donut chart slide using SVG rendering.
    """
    main_title: str = Field(..., description="Main title of the slide (10–60 characters).")
    subtitle: str = Field(..., description="Subtitle or data source displayed below the title.")
    insight: str = Field(..., description="Short analytical insight highlighting the key takeaway from the chart.")
    chart_type: str = Field(default="pie", description="Chart type: 'pie' or 'donut'. Determines whether the center is hollow.")
    unit: str = Field(default="%", description="Unit displayed in values (%, $, users, etc.).")
    show_value: bool = Field(default=True, description="Whether to display percentage values on chart slices.")
    show_legend: bool = Field(default=True, description="Whether to display the legend block.")
    data_label_format: str = Field(default="{value}{unit}", description="Template for slice labels. Supports {label}, {value}, {unit}.")
    items: List[Dict[str, Any]] = Field(
        ..., 
        description="""
        List of data items.

        Structure:
        - items: list of objects
            - label: (str) Name of the category or data point
            - value: (float) Numeric value associated with the label

        Notes:
        - 'value' should be a number (int or float)
        - Labels should be unique to avoid duplication in visualization

        Example:
        [
            {"label": "AI Services", "value": 45},
            {"label": "Cloud Infrastructure", "value": 25}
        ]
        """
    )

class GeneratePieChartSlide6(BaseModel):
    """
    Input schema for generate_pie_chart_slide_6.
    This schema describes parameters used to generate a financial-themed pie or donut chart slide.
    """
    main_title: str = Field(
        ...,
        description="Main title of the slide (10–60 characters)."
    )
    subtitle: str = Field(
        ...,
        description="Subtitle or data source displayed below the title."
    )
    insight: str = Field(
        ...,
        description="Short analytical insight or key takeaway describing the distribution of investment allocation."
    )
    chart_type: str = Field(
        default="donut",
        description="Type of pie chart: 'pie' for full pie chart or 'donut' for ring-style chart."
    )
    unit: str = Field(
        default="%",
        description="Unit displayed in values (%, $, users, etc.)."
    )
    show_value: bool = Field(
        default=True,
        description="Whether to display percentage values on chart slices."
    )
    show_legend: bool = Field(
        default=True,
        description="Whether to render the legend block beside the chart"
    )
    data_label_format: str = Field(
        default="{value}{unit}",
        description="Template for slice labels, e.g. '{value}%' or '{label}: {value}%'"
    )
    items: List[Dict[str, Any]] = Field(
        ...,
        description="""
        List of data items.

        Structure:
        - items: list of objects
            - label: (str) Name of the category or data point
            - value: (float) Numeric value associated with the label

        Notes:
        - 'value' should be a number (int or float)
        - Labels should be unique to avoid duplication in visualization

        Example:
        [
            {"label": "Stocks", "value": 45},
            {"label": "Bonds", "value": 25}
        ]
        """
    )

class GeneratePieChartSlide7(BaseModel):
    """
    Input schema for generate_pie_chart_slide_7.
    This schema defines parameters for generating an elegant three-pie-chart slide with minimalist design.
    """
    main_title: str = Field(..., description="Main title of the slide.")
    subtitle: str = Field(..., description="Subtitle displayed below the title.")
    pie1_insight: str = Field(..., description="Analytical insight for the first pie chart.")
    pie2_insight: str = Field(..., description="Analytical insight for the second pie chart.")
    pie3_insight: str = Field(..., description="Analytical insight for the third pie chart.")
    chart_type: str = Field(default="pie", description="Type of pie chart: 'pie' for full pie chart or 'donut' for ring-style chart.")
    unit: str = Field(default="%", description="Unit displayed in values (%, $, users, etc.).")
    show_value: bool = Field(default=True, description="Whether to display percentage values on chart slices.")
    show_legend: bool = Field(default=True, description="Whether to render the legend block beside the chart.")
    data_label_format: str = Field(default="{value}{unit}", description="Template for slice labels, e.g. '{value}%' or '{label}: {value}%'")
    pie1_items: List[Dict[str, Any]] = Field(
        ...,
        description="""
        List of data items for the first pie chart.

        Structure:
        - label: (str) Name of the category or data point
        - value: (float) Numeric value associated with the label

        Example:
        [
            {"label": "Jupiter", "value": 75},
            {"label": "Other", "value": 25}
        ]
        """
    )
    pie2_items: List[Dict[str, Any]] = Field(
        ...,
        description="""
        List of data items for the second pie chart.

        Structure:
        - label: (str) Name of the category or data point
        - value: (float) Numeric value associated with the label

        Example:
        [
            {"label": "Neptune", "value": 65},
            {"label": "Other", "value": 35}
        ]
        """
    )
    pie3_items: List[Dict[str, Any]] = Field(
        ...,
        description="""
        List of data items for the third pie chart.

        Structure:
        - label: (str) Name of the category or data point
        - value: (float) Numeric value associated with the label

        Example:
        [
            {"label": "Mercury", "value": 60},
            {"label": "Other", "value": 40}
        ]
        """
    )

class GeneratePieChartSlide8(BaseModel):    
    main_title: str = Field(..., description="Main title of the slide.")
    subtitle: str = Field(..., description="Subtitle providing context or data summary.")
    unit: str = Field(default="%", description="Measurement unit displayed after the number.")
    categories: List[str] = Field(..., description="List of categories to display (e.g., ['North America', 'Europe']).")
    insights: List[str] = Field(..., description="List of strings containing detailed analysis or insights texts for each category.")
    series: List[float] = Field(..., description="List of numerical values corresponding to each category. Example format: [45.0, 30.0, 25.0]")


GRAPH_TOOLS = [
    StructuredTool.from_function(
        func=generate_pie_chart_slide_1,
        name="generate_pie_chart_slide_1",
        description=(
            "The slide layout is divided into three main sections:\n"
            "- Upper section: Displays a large, bold main title in Teal and a white subtitle.\n"
            "- Left section: Contains a highlighted insight box with an accent border and a legend.\n"
            "- Right section: Features a high-contrast SVG pie or donut chart.\n"
        ),
        args_schema=GeneratePieChartSlide1
    ),
    StructuredTool.from_function(
        func=generate_pie_chart_slide_2,
        name="generate_pie_chart_slide_2",
        description=(
            "The slide layout is divided into three main sections:\n"
            "- Upper section: Contains the main title with a heavy left accent border and a cyan subtitle.\n"
            "- Left section: Reserved for a stylistic insight box with a semi-transparent background and a vertical list of legend items with glow effects.\n"
            "- Right section: Features a large, high-contrast SVG pie or donut chart centered in the space.\n"
            "The layout uses a dark tech-inspired theme (#020c24) for professional data visualization."
        ),
        args_schema=GeneratePieChartSlide2
    ),
    StructuredTool.from_function(
        func=generate_pie_chart_slide_3,
        name="generate_pie_chart_slide_3",
        description=(
            "The slide layout consists of three main sections:\n"
            "- Top: A full-width header with a large main title and a subtitle displayed directly beneath it.\n"
            "- Left column: An insight card containing the main explanatory text, followed by a vertical legend listing chart items with color indicators and percentage values.\n"
            "- Right column: A centered SVG pie or donut chart displayed inside a panel with a subtle radial gradient background.\n"
            "A thin horizontal accent bar is placed at the very top of the slide."
        ),
        args_schema=GeneratePieChartSlide3
    ),
    StructuredTool.from_function(
        func=generate_pie_chart_slide_4,
        name="generate_pie_chart_slide_4",
        description=(
            "The slide layout is divided into three main sections:\n"
            "- Upper section: Reserved for the main title and subtitle with a large, bold aesthetic.\n"
            "- Left section: Reserved for descriptive insights and a detailed legend explaining the data categories.\n"
            "- Right section: Reserved for the visual SVG pie or donut chart, designed with a clean, high-contrast style.\n\n"
            "The layout is designed to emphasize proportional data through a modern, pastel-themed interface."
        ),
        args_schema=GeneratePieChartSlide4
    ),
    StructuredTool.from_function(
        func=generate_pie_chart_slide_5,
        name="generate_pie_chart_slide_5",
        description=(
            "The slide structure consists of three main sections:\n"
            "- Top section: Contains the main title and subtitle with a vertical line accent.\n"
            "- Left section: Contains a highlighted Insight card and a legend list.\n"
            "- Right section: Contains a pie or donut chart rendered professionally using SVG.\n"
            "This design is optimized for financial reports and corporate presentations with an elegant color tone."
        ),
        args_schema=GeneratePieChartSlide5
    ),
    StructuredTool.from_function(
        func=generate_pie_chart_slide_6,
        name="generate_pie_chart_slide_6",
        description=(
            "The slide layout is divided into three main sections:\n"
            "- Upper section: contains the main title with a vertical accent bar and a subtitle.\n"
            "- Left section: occupies the majority of the left side, dedicated to a large, clean Pie or Donut chart.\n"
            "- Right section: features a styled insight box with a bottom accent border and a clean list of legend items with values.\n"
            "The layout uses a professional cream and gold-brown palette, ideal for financial stability and security topics."
        ),
        args_schema=GeneratePieChartSlide6
    ),
    StructuredTool.from_function(
        func=generate_pie_chart_slide_8,
        name="generate_pie_chart_slide_8",
        description=(
            "The slide layout is structured into two main sections:\n"
            "- Header section: centered at the top, displaying the main title and subtitle.\n"
            "- Content section: arranged horizontally with three aligned parts:\n"
            "  + Left panel: a vertical list of category insight cards with descriptive text.\n"
            "  + Center panel: a large radial multi-arc (circular) chart visualization.\n"
            "  + Right panel: a vertical list of value cards showing icons and highlighted numeric values.\n\n"
            "The layout emphasizes a central visual chart, supported by detailed insights on the left and key figures on the right."
        ),
        args_schema=GeneratePieChartSlide8
    )
]











