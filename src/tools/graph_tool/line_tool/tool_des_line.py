from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from .html_lib_line import (
    generate_line_chart_slide_1,
    generate_line_chart_slide_2,
    generate_line_chart_slide_3,
    generate_line_chart_slide_4,
    generate_line_chart_slide_5,
)


class GenerateLineChartSlide1(BaseModel):
    """Input schema for generate_line_chart_slide_1 - Playful Stamp themed chart for educational/renewable energy reports."""
    main_title: str = Field(...,description="Main title displayed at the top of the slide (10-60 characters). Example: 'Accelerating Growth of Renewable Energy Capacity'")
    subtitle: str = Field(...,description="Subtitle displayed below the main title, typically indicating report name and time period.")
    insight: str = Field(...,description="Text insight displayed in the left panel, providing key observations about the data (100-300 characters).")
    x_axis: str = Field(..., description="Label for X-axis (e.g., 'Year', 'Month', 'Quarter', 'Time Period').")
    y_axis: str = Field(..., description="Label for Y-axis (e.g., 'Installed Capacity', 'Revenue', 'Units Produced').")
    unit: str = Field(..., description="Unit appended to values (e.g., ' GW', '%', ' MW', ' units'). Appears in data labels when show_value=True.")
    show_value: bool = Field(default=False, description="Whether numeric values are displayed above chart points. Set to True for detailed reports, False for cleaner visuals.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed in the left panel below the insight box.")
    y_axis_min: float = Field(default=50, description="Minimum value of Y-axis. If None, auto-calculated from data with default padding.")
    y_axis_max: float = Field(default=260, description="Maximum value of Y-axis. If None, auto-calculated from data with default padding.")
    colors: List[str] = Field(..., description="List of colors for each line series. Playful theme defaults to orange (#FF8C00) and blue (#4A90E2).")
    time_points: List[str] = Field(..., description="List of time points on X-axis (e.g., years, months, quarters). Example: ['2019', '2020', '2021', '2022', '2023', '2024']")
    series: List[Dict[str, Union[str, List[float]]]] = Field(
        ...,
        description="""
        Line chart series data for comparing different energy sources or metrics.

        Structure:
        - series: list of series objects
            - name: series name (e.g., 'Solar Energy', 'Wind Energy', 'Hydro Power')
            - values: list of numeric values matching time_points length

        Rules:
        - Each series must have same length as time_points
        - Values should be positive numbers

        Example:
        [
            {
                "name": "Solar Energy",
                "values": [80, 95, 110, 150, 200, 250]
            },
            {
                "name": "Wind Energy", 
                "values": [70, 85, 100, 120, 150, 180]
            }
        ]
        """
    )

class GenerateLineChartSlide2(BaseModel):
    """Input schema for generate_line_chart_slide_2 - ML/AI model training convergence chart."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters). Example: 'Model Accuracy Converges with Minor Overfitting'")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating model, dataset, and training duration.")
    insight: str = Field(..., description="Text insight displayed in the left panel, providing key observations about model training behavior (200-500 characters).")
    x_axis: str = Field(..., description="Label for X-axis (e.g., 'Epoch', 'Iteration', 'Time').")
    y_axis: str = Field(...,description="Label for Y-axis (e.g., 'Accuracy', 'Loss', 'F1 Score').")
    unit: str = Field(...,description="Optional unit appended to values (e.g., '%', 'pts', ''). Appears in Y-axis labels.")
    show_value: bool = Field(default=False, description="Whether numeric values are displayed above chart points. Default False for cleaner ML visualizations.")
    y_axis_min: float = Field(default=40, description="Minimum value of Y-axis. Use 0 for loss curves, 40-60 for accuracy starting points.")
    y_axis_max: float = Field(default=100, description="Maximum value of Y-axis. Use 100 for accuracy/percentage metrics.")
    data_label_format: str = Field(default=None, description="Format for data labels. Special value 'percentage' formats as '{value}%'. Otherwise uses simple concatenation with unit.")
    colors: List[str] = Field(default=["#4F46E5", "#22C55E"], description="List of colors for each line series. ML theme defaults to indigo (#4F46E5) for training and green (#22C55E) for validation.")
    time_points: List[str] = Field(..., description="List of time points on X-axis. Can be unevenly spaced (e.g., epochs 1,5,10,15...). Example: ['Epoch 1', 'Epoch 5', 'Epoch 10']")
    series: List[Dict[str, Union[str, List[float]]]] = Field(
        ...,
        description="""
        Line chart series data for model performance metrics.

        Structure:
        - series: list of series objects
            - name: metric name (e.g., 'Training Accuracy', 'Validation Accuracy', 'Training Loss')
            - values: list of numeric values matching time_points length

        Rules:
        - Each series must have same length as time_points
        - Values should be within y_axis_min/y_axis_max range

        Example:
        [
            {
                "name": "Training Accuracy",
                "values": [45, 62, 75, 84, 90, 94, 97]
            },
            {
                "name": "Validation Accuracy", 
                "values": [43, 60, 73, 82, 87, 88, 88]
            }
        ]
        """
    )

class GenerateLineChartSlide3(BaseModel):
    """Input schema for generate_line_chart_slide_3."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'EV Market Leaders Expand the Gap'")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Southeast Asia EV Sales – Jan to Dec 2026'")
    insight: str = Field(..., description="Text insight displayed in the right panel, providing key observations about the data (100-300 characters).")
    x_axis: str = Field(..., description="Label for X-axis (e.g., 'Month', 'Year', 'Quarter').")
    y_axis: str = Field(..., description="Label for Y-axis (e.g., 'Units Sold', 'Revenue', 'Capacity').")
    unit: str = Field(..., description="Optional unit appended to values (e.g., 'K', 'GW', '%', '$'). Appears in Y-axis label and data labels.")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed on chart points.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed in the insight area.")
    y_axis_min: float = Field(default=20, description="Minimum value of Y-axis. If None, auto-calculated from data with 10% padding.")
    y_axis_max: float = Field(default=140, description="Maximum value of Y-axis. If None, auto-calculated from data with 10% padding.")
    data_label_format: str = Field(default="{value}K", description="Format string for values using .format(value=val) syntax. Example: '{value}K' or '{value:,.0f} units'.")
    colors: List[str] = Field(default=["#00F2FF", "#8B5CF6", "#EC4899"], description="List of colors for each line series. Each series gets a color in order.")
    time_points: List[str] = Field(..., description="List of time points on X-axis (e.g., ['Jan', 'Feb', 'Mar', ...] or ['2019', '2020', ...]).")
    series: List[Dict[str, Union[str, List[float]]]] = Field(
        ...,
        description="""
        Line chart series data.

        Structure:
        - series: list of series objects
            - name: series name (e.g., 'Tesla', 'BYD')
            - values: list of numeric values matching time_points length

        Rules:
        - Each series must have same length as time_points
        - Values should be positive numbers

        Example:
        [
            {
                "name": "Tesla",
                "values": [45, 50, 55, 60, 68, 75, 90, 105, 115, 120, 125, 130]
            },
            {
                "name": "BYD", 
                "values": [40, 48, 52, 58, 63, 70, 85, 95, 105, 110, 118, 122]
            }
        ]
        """
    )

class GenerateLineChartSlide4(BaseModel):
    """Input schema for generate_line_chart_slide_4."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Renewable Energy Capacity by Region'")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Global Renewable Energy Report – 2019 to 2024'")
    x_axis_label: str = Field(..., description="Label for X-axis (e.g., 'Year', 'Month', 'Quarter').")
    y_axis_label: str = Field(..., description="Label for Y-axis (e.g., 'Revenue', 'Capacity').")
    unit: str = Field(..., description="Optional unit appended to values (e.g., 'GW', '%', '$').")
    show_value: bool = Field(default=False, description="Whether numeric values are displayed on chart points.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed.")
    y_axis_min: float = Field(default=50, description="Minimum value of Y-axis (auto if None).")
    y_axis_max: float = Field(default=260, description="Maximum value of Y-axis (auto if None).")
    data_label_format: Optional[str] = Field(default=None, description="Format string for values (e.g., '{value}', '{value} units'). If None, uses default formatting.")
    colors: List[str] = Field(default=["#FF8C00", "#4A90E2"], description="List of colors for each line series.")
    time_points: List[str] = Field(..., description="List of time points (e.g., ['2019', '2020', '2021', '2022', '2023', '2024']).")
    series: List[Dict[str, Union[str, List[float]]]] = Field(
        ...,
        description="""
        Line chart series data.

        Structure:
        - series: list of series objects
            - name: series name (e.g., 'Solar Energy')
            - values: list of numeric values matching time_points

        Rules:
        - Each series must have same length as time_points

        Example:
        [
            {
                "name": "Solar Energy",
                "values": [80, 95, 110, 150, 200, 250]
            }
        ]
        """
    )

class GenerateLineChartSlide5(BaseModel):
    """Input schema for generate_line_chart_slide_5 - Medical-themed line chart for healthcare data."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10-60 characters). Example: 'Average Blood Pressure by Age Group'")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating unit and data source. Example: 'Unit: mmHg | Data Source: National Health Survey 2025'")
    insight: str = Field(..., description="Clinical insight text displayed in the right panel (100-300 characters). If empty, a default medical insight will be shown.")
    x_axis: str = Field(..., description="Label for X-axis (e.g., 'Age Group', 'Time Period', 'Category').")
    y_axis: str = Field(...,description="Label for Y-axis (e.g., 'Average Blood Pressure (mmHg)', 'Value', 'Measurement').")
    unit: str = Field(..., description="Unit appended to values (e.g., 'mmHg', '%', 'bpm', 'kg'). Appears in data labels and Y-axis.")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed above chart points.")
    show_legend: bool = Field(default=True,description="Whether legend is displayed in the insight area showing demographic/patient groups.")
    y_axis_min: float = Field(default=0,description="Minimum value of Y-axis. If 0, uses data minimum with 10% padding.")
    y_axis_max: Optional[float] = Field(default=None,description="Maximum value of Y-axis. If None, auto-calculated from data with 10% padding.")
    colors: List[str] = Field(default=["#E53935", "#1E88E5"],description="List of colors for each line series. Medical theme defaults to red (#E53935) and blue (#1E88E5).")
    categories: List[str] = Field(default=["18-25", "26-35", "36-45", "46-60", "60+"], description="List of categories on X-axis (e.g., age groups, time points). Example: ['18-25', '26-35', '36-45', '46-60', '60+']")
    series: List[Dict[str, Union[str, List[float]]]] = Field(
        ...,
        description="""
        Line chart series data for different demographics.

        Structure:
        - series: list of series objects
            - name: demographic/group name (e.g., 'Male', 'Female', 'Hypertensive')
            - values: list of numeric values matching categories length

        Rules:
        - Each series must have same length as categories
        - Values should be positive numbers

        Example:
        [
            {
                "name": "Male",
                "values": [118, 122, 128, 135, 142]
            },
            {
                "name": "Female", 
                "values": [80, 110, 100, 130, 138]
            }
        ]
        """
    )

LINE_TOOLS = [
    StructuredTool.from_function(
        func=generate_line_chart_slide_1,
        name="generate_line_chart_slide_1",
        description=(
            "Generates a playful stamp-themed Line Chart slide with a vibrant, presentation-ready design.\n"
            "The visual style combines a bright green background, bold typography, and a white stamp-like container, "
            "creating a fun yet structured layout for communicating time-based trends effectively.\n"
            "The slide layout is divided into three main sections:\n"
            "- Upper section: contains a large uppercase main title and a subtitle, positioned inside a wide header area within the white stamp container.\n"
            "- Left section: contains a dashed insight card for key observations and a vertical list of legends with colored markers.\n"
            "- Right section: features a large rounded chart container with a bold border, displaying an SVG line chart with multiple series, grid lines, and labeled axes.\n\n"
            "The layout uses a bright green full-screen background and a central white 'stamp' panel with soft shadows and perforated-style edges, "
            "creating a playful and engaging presentation style while maintaining clear data readability."
        ),
        args_schema=GenerateLineChartSlide1
    ),
    StructuredTool.from_function(
        func=generate_line_chart_slide_2,
        name="generate_line_chart_slide_2",
        description=(
            "Generates a modern line chart slide with a clean, structured layout.\n\n"
            "Slide layout:\n"
            "- Top section: contains the main title and subtitle aligned to the left.\n"
            "- Main content area is split into two columns:\n"
            "  • Left panel: displays a text insight block.\n"
            "  • Right panel: displays the line chart visualization.\n\n"
            "Additional layout elements:\n"
            "- A large decorative circular background shape is positioned on the left side.\n"
            "- A dotted grid pattern is positioned in the top-right area.\n"
            "- The chart includes axes, grid lines, multiple line series, and end-of-line labels.\n\n"

            "The layout emphasizes clear separation between textual insight and visual data."
        ),
        args_schema=GenerateLineChartSlide2
    ),
    StructuredTool.from_function(
        func=generate_line_chart_slide_3,
        name="generate_line_chart_slide_3",
        description=(
            "Generates a line chart slide with a structured dark layout.\n\n"
            "Slide layout:\n"
            "- Top section: contains the main title and subtitle aligned to the left.\n"
            "- Main content area is divided into two columns:\n"
            "  • Left (larger) panel: displays the line chart visualization.\n"
            "  • Right (smaller) panel: contains an insight text block at the top and an optional legend list below.\n\n"
            "Additional layout elements:\n"
            "- Chart includes axes, grid lines, multiple line series, and optional data labels.\n"
            "- Axis titles are shown inside the chart.\n"
            "- Legend appears as a vertical list below the insight.\n\n"
            "The layout separates data visualization and explanatory content into two distinct panels."
        ),
        args_schema=GenerateLineChartSlide3
    ),
    StructuredTool.from_function(
        func=generate_line_chart_slide_4,
        name="generate_line_chart_slide_4",
        description=(
            "Generates a line chart slide with a two-column layout.\n\n"

            "- Top: main title and subtitle.\n"
            "- Left: legend panel with decorative illustrations.\n"
            "- Right: line chart visualization.\n\n"

            "- Chart includes axes, grid lines, multiple line series, and optional value labels."
        ),
        args_schema=GenerateLineChartSlide4
    ),
    StructuredTool.from_function(
        func=generate_line_chart_slide_5,
        name="generate_line_chart_slide_5",
        description=(
            "Generates a line chart slide with a two-column layout.\n\n"
            "- Top: main title and subtitle.\n"
            "- Content split into two sections:\n"
            "  • Left (larger): line chart visualization.\n"
            "  • Right (smaller): insight text with legend below.\n\n"
            "- Chart includes axes, grid lines, multiple line series, and optional value labels."
        ),
        args_schema=GenerateLineChartSlide5
    )
]