from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from typing import Optional, Union
from typing import List, Dict, Optional
from .html_lib_scatter import (
    generate_scatter_plot_chart_slide_1,
    generate_scatter_plot_chart_slide_2,
    generate_scatter_plot_chart_slide_3,
    generate_scatter_plot_chart_slide_4,
    generate_scatter_plot_chart_slide_5,
    generate_scatter_plot_chart_slide_6,
    generate_scatter_plot_chart_slide_7
)

class GenerateScatterPlotChart1(BaseModel):
    """Input schema for generate_scatter_plot_chart_slide_1."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Early Childhood Development Analysis'")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Correlation between Play Time and Social Skill Scores'")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the right panel, summarizing trends or correlations in the scatter plot.")
    x_axis: str = Field(..., description="Label for the X-axis (e.g., 'Weekly Play Time (Hours)').")
    y_axis: str = Field(..., description="Label for the Y-axis (e.g., 'Social Skill Score (0-100)').")
    unit: str = Field(..., description="Unit displayed with values (e.g., 'pts', 'points').")
    show_value: bool = Field(default=False, description="Whether numeric values are displayed above each scatter point.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed for different data series.")
    x_axis_min: float = Field(default=None, description="Minimum value for X-axis. If not provided, it is computed from data.")
    x_axis_max: float = Field(default=None, description="Maximum value for X-axis. If not provided, it is computed from data.")
    y_axis_min: float = Field(default=None, description="Minimum value for Y-axis. If not provided, it is computed from data.")
    y_axis_max: float = Field(default=None, description="Maximum value for Y-axis. If not provided, it is computed from data.")
    series: List[Dict[str, str | List[Dict[str, float]]]] = Field(
        ...,
        description="""
            Scatter plot data in series format.

            Structure:
            - series: list of data series
                - name: Name of the series
                - points: list of (x, y) coordinates

            Notes:
            - Each point must contain numeric 'x' and 'y'
            - Multiple series are supported
            - Used to visualize relationships or correlations

            Example:
            [
                {
                    "name": "Group A (Ages 3-4)",
                    "points": [
                        {"x": 2, "y": 45},
                        {"x": 3.5, "y": 58}
                    ]
                }
            ]
        """
    )

class GenerateScatterPlotChartSlide2(BaseModel):
    """Input schema for generate_scatter_plot_chart_slide_2"""
    main_title: str = Field(..., description="Main title of the slide, summarizing the core message of the scatter plot within a travel context (10–60 characters). Example: Relationship Between Travel Distance and Spending")
    subtitle: str = Field(..., description="Subtitle or supplementary information such as data source, survey scope, or collection period. Example: Source: Tourist Behavior Survey 2024")
    insight: str = Field(..., description="A concise analytical statement derived from the chart, highlighting key trends, correlations, or notable outliers in travel behavior. Example: International travelers spend disproportionately more for trips above 7000 km.")
    x_axis: str = Field(..., description="Label for the X-axis metric represented in the scatter plot. Example: Travel Distance (km).")
    y_axis: str = Field(..., description="Label for the Y-axis metric represented in the scatter plot. Example: Total Travel Spending (USD).")
    unit: str = Field(..., description="Unit suffix used when displaying point value labels. Example: USD, $, k VND.")
    show_value: bool = Field(default=False, description="Whether to show value labels above each scatter point. Example: True.")
    show_legend: bool = Field(default=True, description="Whether to display the legend panel for each data series. Example: True.")
    x_axis_min: float = Field(default=0, description="Minimum value for the X-axis scale. Example: 0.")
    x_axis_max: float = Field(default=12000, description="Maximum value for the X-axis scale. Example: 12000.")
    y_axis_min: float = Field(default=0, description="Minimum value for the Y-axis scale. Example: 0.")
    y_axis_max: float = Field(default=6000, description="Maximum value for the Y-axis scale. Example: 6000.")
    series: List[Dict[str, str | List[Dict[str, float]]]] = Field(
        ...,
        description=(
            "List of scatter data series. Each series includes 'name' and 'points'; "
            "each point is an object with numeric 'x' and 'y' values. "
            "Example: [{'name': 'Domestic Travelers', 'points': [{'x': 150, 'y': 300}, {'x': 1200, 'y': 1100}]}]."
        )
    )

class GenerateScatterPlotChartSlide3(BaseModel):
    """Input schema for generate_scatter_plot_chart_slide_3."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Study Time and Exam Performance Trend'")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Education Performance Study 2026'")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the left panel, summarizing trends or correlations in the scatter plot. Example: 'Students attending guided revision sessions consistently outperform independent learners.'")
    x_axis: str = Field(..., description="Label for the X-axis (e.g., 'Weekly Self-Study Hours').")
    y_axis: str = Field(..., description="Label for the Y-axis (e.g., 'Final Exam Score').")
    unit: str = Field(..., description="Unit displayed with values (e.g., 'points', '%', 'USD').")
    show_value: bool = Field(default=False, description="Whether numeric values are displayed above each scatter point.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed for different data series.")
    data_label_format: Optional[str] = Field(default=None, description="Optional format string for data labels (not used if show_value is False).")
    x_axis_min: float = Field(default=0, description="Minimum value for X-axis. If not provided, it is computed from data.")
    x_axis_max: float = Field(default=20, description="Maximum value for X-axis. If not provided, it is computed from data.")
    y_axis_min: float = Field(default=50, description="Minimum value for Y-axis. If not provided, it is computed from data.")
    y_axis_max: float = Field(default=100, description="Maximum value for Y-axis. If not provided, it is computed from data.")
    colors: list[str] = Field(default=["#3D5A80", "#EE6C4D"], description="List of colors applied to scatter series. Colors cycle if there are more series than colors.")
    series: List[Dict[str, str | List[Dict[str, float]]]] = Field(
        ...,
        description="""
            Scatter plot data in series format.

            Structure:
            - series: list of data series
                - name: Name of the series
                - points: list of (x, y) coordinates

            Notes:
            - Each point must contain numeric 'x' and 'y'
            - Multiple series are supported
            - Used to visualize relationships or correlations

            Example:
            [
                {
                    "name": "Independent Study Group",
                    "points": [
                        {"x": 3, "y": 58},
                        {"x": 5, "y": 65}
                    ]
                }
            ]
        """
    )

class GenerateScatterPlotChartSlide4(BaseModel):
    """Input schema for generate_scatter_plot_chart_slide_4."""   
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Study Effort Drives Skill Mastery'")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Online Course Analysis – Q4 2024'")
    insight: str = Field(..., description="Key analytical insight shown in the left panel, summarizing trends or correlations in the scatter plot. Example: 'Higher weekly study hours generally lead to better skill assessment scores.'")
    x_axis: str = Field(..., description="Label for the X-axis (e.g., 'Weekly Study Hours').")
    y_axis: str = Field(..., description="Label for the Y-axis (e.g., 'Final Skill Assessment Score').")
    unit: str = Field(..., description="Unit displayed with values (e.g., 'points', '%', 'USD').")
    show_value: bool = Field(default=False, description="Whether numeric values are displayed above each scatter point.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed for different data series.")
    data_label_format: Optional[str] = Field(default=None, description="Optional format string for data labels (not used if show_value is False).")
    x_axis_min: float = Field(default=0, description="Minimum value for X-axis. If not provided, it is computed from data.")
    x_axis_max: float = Field(default=25, description="Maximum value for X-axis. If not provided, it is computed from data.")
    y_axis_min: float = Field(default=40, description="Minimum value for Y-axis. If not provided, it is computed from data.")
    y_axis_max: float = Field(default=100, description="Maximum value for Y-axis. If not provided, it is computed from data.")
    colors: list[str] = Field(default=["#4F46E5", "#F59E0B"], description="List of colors applied to scatter series. Colors cycle if there are more series than colors.")
    series: List[Dict[str, str | List[Dict[str, float]]]] = Field(
        ...,
        description="""
            Scatter plot data in series format.

            Structure:
            - series: list of data series
                - name: Name of the series
                - points: list of (x, y) coordinates

            Notes:
            - Each point must contain numeric 'x' and 'y'
            - Multiple series are supported
            - Used to visualize relationships or correlations

            Example:
            [
                {
                    "name": "Self-Paced Learners",
                    "points": [
                        {"x": 4, "y": 55},
                        {"x": 6, "y": 60}
                    ]
                }
            ]
        """
    )

class GenerateScatterPlotChartSlide5(BaseModel):
    """Input schema for generate_scatter_plot_chart_slide_5."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Relationship Between App Usage Time and Monthly Spending'")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Source: Mobile App Analytics Report 2024 | Sample: 200 Users'")
    insight: str = Field(..., description="Key analytical insight shown in the left panel, summarizing trends or correlations in the scatter plot. Example: 'Higher app usage correlates with increased digital spending among both user segments'")
    x_axis: str = Field(..., description="Label for the X-axis (e.g., 'Daily App Usage Time (minutes)').")
    y_axis: str = Field(..., description="Label for the Y-axis (e.g., 'Monthly Digital Spending (USD)').")
    unit: str = Field(..., description="Unit displayed with values (e.g., 'USD', '%', 'points').")
    show_value: bool = Field(default=False, description="Whether numeric values are displayed above each scatter point.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed for different data series.")
    x_axis_min: float = Field(default=0, description="Minimum value for X-axis. Example: 0.")
    x_axis_max: float = Field(default=600, description="Maximum value for X-axis. Example: 600.")
    y_axis_min: float = Field(default=0, description="Minimum value for Y-axis. Example: 0.")
    y_axis_max: float = Field(default=500, description="Maximum value for Y-axis. Example: 500.")
    series: List[Dict[str, str | List[Dict[str, float]]]] = Field(
        ...,
        description="""
            Scatter plot data in series format.

            Structure:
            - series: list of data series
                - name: Name of the series
                - points: list of (x, y) coordinates

            Notes:
            - Each point must contain numeric 'x' and 'y'
            - Multiple series are supported
            - Used to visualize relationships or correlations

            Example:
            [
                {
                    "name": "Casual Users",
                    "points": [
                        {"x": 30, "y": 10},
                        {"x": 60, "y": 20}
                    ]
                }
            ]
        """
    )


class GenerateScatterPlotChartSlide6(BaseModel):
    """Input schema for generate_scatter_plot_chart_slide_6."""
    main_title: str = Field(..., description="Main title displayed prominently in the header section (10–60 characters). Example: 'Relationship Between Study Time and Academic Performance'")
    subtitle: str = Field(..., description="Subtitle displayed on the top-right of the header, typically indicating data source or context. Example: 'Source: Education Analytics Report 2024'")
    insight: str = Field(..., description="Key analytical insight displayed in a highlighted box on the left panel, summarizing trends or correlations in the scatter plot. Example: 'High achievers tend to study more, but optimal study time varies among students.'")
    x_axis: str = Field(..., description="Label for the X-axis (e.g., 'Daily Study Time (minutes)').")
    y_axis: str = Field(..., description="Label for the Y-axis (e.g., 'Exam Score (Points)').")
    unit: str = Field(..., description="Unit displayed with values (e.g., '%', 'points', 'USD').")
    show_value: bool = Field(default=False, description="Whether numeric values are displayed above each scatter point.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed for different data series.")
    x_axis_min: float = Field(default=0, description="Minimum value for X-axis. If not provided, it is computed from data.")
    x_axis_max: float = Field(default=600, description="Maximum value for X-axis. If not provided, it is computed from data.")
    y_axis_min: float = Field(default=0, description="Minimum value for Y-axis. If not provided, it is computed from data.")
    y_axis_max: float = Field(default=500, description="Maximum value for Y-axis. If not provided, it is computed from data.")
    series: List[Dict[str, str | List[Dict[str, float]]]] = Field(
        ...,
        description="""
            Scatter plot data in series format.

            Structure:
            - series: list of data series
                - name: Name of the series
                - points: list of (x, y) coordinates

            Notes:
            - Each point must contain numeric 'x' and 'y'
            - Multiple series are supported
            - Used to visualize relationships or correlations between variables

            Example:
            [
                {
                    "name": "Average Students",
                    "points": [
                        {"x": 30, "y": 10},
                        {"x": 60, "y": 20}
                    ]
                }
            ]
        """
    )

class GenerateScatterPlotChartSlide7(BaseModel):
    """Input schema for generate_scatter_plot_chart_slide_7."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Relationship Between App Usage Time and Monthly Spending'")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Source: Mobile App Analytics Report 2024'")
    insight: str = Field(..., description="Key analytical insight shown in the right panel, summarizing trends or correlations in the scatter plot. Example: 'Power users tend to spend significantly more than casual users.'")
    x_axis: str = Field(..., description="Label for the X-axis (e.g., 'App Usage Time (minutes/day)').")
    y_axis: str = Field(..., description="Label for the Y-axis (e.g., 'Monthly Digital Spending (USD)').")
    unit: str = Field(..., description="Unit displayed with values (e.g., '%', 'USD', 'points').")
    show_value: bool = Field(default=False, description="Whether numeric values are displayed above each scatter point.")
    show_legend: bool = Field(default=True, description="Whether legend is displayed for different data series.")
    x_axis_min: float = Field(default=0, description="Minimum value for X-axis. If not provided, it is computed from data.")
    x_axis_max: float = Field(default=400, description="Maximum value for X-axis. If not provided, it is computed from data.")
    y_axis_min: float = Field(default=0, description="Minimum value for Y-axis. If not provided, it is computed from data.")
    y_axis_max: float = Field(default=300, description="Maximum value for Y-axis. If not provided, it is computed from data.")
    series: List[Dict[str, str | List[Dict[str, float]]]] = Field(
        ...,
        description="""
            Scatter plot data in series format.

            Structure:
            - series: list of data series
                - name: Name of the series
                - points: list of (x, y) coordinates

            Notes:
            - Each point must contain numeric 'x' and 'y'
            - Multiple series are supported
            - Used to visualize relationships or correlations

            Example:
            [
                {
                    "name": "Casual Users",
                    "points": [
                        {"x": 30, "y": 10},
                        {"x": 60, "y": 20}
                    ]
                }
            ]
        """
    )


SCATTER_PLOT_TOOLS = [
    StructuredTool.from_function(
        func=generate_scatter_plot_chart_slide_1,
        name="generate_scatter_plot_chart_slide_1",
        description=(
            "The slide layout is structured into two main areas:\n"
            "- Top section: displays the main title and subtitle with a vertical accent bar for visual emphasis.\n"
            "- Left section: reserved for displaying a scatter plot chart and axis labels within a dashed container.\n"
            "- Right section: reserved for chart description, including an insight card and a legend box.\n\n"
            "The layout is designed to present visual data alongside supporting explanatory text in a playful, education-themed style."
        ),
        args_schema=GenerateScatterPlotChart1
    ),
    StructuredTool.from_function(
        func=generate_scatter_plot_chart_slide_2,
        name="generate_scatter_plot_chart_slide_2",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left area: displays a scatter plot chart visualization.\n"
            "  + Right column: presents an insight panel with descriptive text and a legend below.\n\n"
            "The layout emphasizes data visualization on the left and analytical interpretation on the right."
        ),
        args_schema=GenerateScatterPlotChartSlide2
    ),
    StructuredTool.from_function(
        func=generate_scatter_plot_chart_slide_3,
        name="generate_scatter_plot_chart_slide_3",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left column: presents an insight panel with descriptive text and a legend below.\n"
            "  + Right column: displays the scatter plot chart visualization.\n\n"
            "The layout emphasizes analytical interpretation on the left and data visualization on the right."
        ),
        args_schema=GenerateScatterPlotChartSlide3
    ),
    StructuredTool.from_function(
        func=generate_scatter_plot_chart_slide_4,
        name="generate_scatter_plot_chart_slide_4",
        description=(
            "The slide layout is structured into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top, separated by a dashed accent line.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left column: contains a highlighted insight box followed by a legend list.\n"
            "  + Right column: features the scatter plot chart inside a styled container with rounded corners, border, and shadow.\n\n"
            "The layout combines a decorative header, a visually emphasized insight panel, and a prominent chart area."
        ),
        args_schema=GenerateScatterPlotChartSlide4
    ),
    StructuredTool.from_function(
    func=generate_scatter_plot_chart_slide_5,
        name="generate_scatter_plot_chart_slide_5",
        description=(
            "The slide uses a full-width dark background with gradient effects and is structured into three main sections:\n"
            "- Top header: displays the main title and subtitle aligned to the left.\n"
            "- Main content area: arranged in a two-column layout:\n"
            "  + Left column: contains an insight panel styled as a highlighted card, followed by a vertical legend list.\n"
            "  + Right column: features the scatter plot chart inside a rounded container with subtle border and blur effects.\n"
            "- Bottom footer: includes a horizontal divider line with a small label aligned to the left.\n\n"
            "The layout emphasizes a modern, tech-oriented visual style with strong contrast between textual insights and data visualization."
        ),
        args_schema=GenerateScatterPlotChartSlide5
    ),
    StructuredTool.from_function(
        func=generate_scatter_plot_chart_slide_6,
        name="generate_scatter_plot_chart_slide_6",
        description=(
            "The slide features a modern, visually rich layout with decorative background elements including soft wave shapes and floating square accents.\n\n"
            "- Header section: positioned at the top with a split layout:\n"
            "  + Left side: displays a large, bold main title.\n"
            "  + Right side: shows the subtitle aligned to the right.\n\n"
            "- Main content section: arranged in a horizontal two-column layout:\n"
            "  + Left column: contains an insight panel styled as a soft card with a highlighted left border, followed by a vertical legend list.\n"
            "  + Right column: displays the scatter plot chart inside a rounded container with a light background and subtle shadow.\n\n"
            "The overall design emphasizes a clean, modern aesthetic with strong visual separation between insight content and data visualization, enhanced by decorative background elements."
        ),
        args_schema=GenerateScatterPlotChartSlide6
    ),
    StructuredTool.from_function(
        func=generate_scatter_plot_chart_slide_7,
        name="generate_scatter_plot_chart_slide_7",
        description=(
            "The slide layout uses an absolute-positioned composition with three main sections:\n"
            "- Header section: displays the main title and subtitle at the top, spanning the full width.\n"
            "- Chart section: positioned on the left side, showing the scatter plot visualization.\n"
            "- Insight section: positioned on the right side as a boxed panel containing analytical text and a legend below.\n\n"
            "The layout emphasizes visual balance with the chart on the left and interpretive insights on the right."
        ),
        args_schema=GenerateScatterPlotChartSlide7
    )
]