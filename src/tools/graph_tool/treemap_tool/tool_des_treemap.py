from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from typing import Optional 
from .html_lib_treemap import (
    generate_treemap_chart_slide_1,
    generate_treemap_chart_slide_2,
    generate_treemap_chart_slide_3,
    generate_treemap_chart_slide_4,
    generate_treemap_chart_slide_5
)

class GenerateTreemapChartSlide1(BaseModel):
    """Input schema for generate_treemap_chart_slide_1"""
    main_title: str = Field(..., description="Main title of the treemap chart slide (10–60 characters).")
    subtitle: str = Field(..., description="Subtitle, unit, or data source.")
    insight: str = Field(..., description="Narrative insight explaining key patterns.")
    unit: str = Field(..., description="Unit appended to values (e.g., 'B', 'M', '%').")
    show_label: bool = Field(default=True, description="Whether to display labels inside blocks.")
    data_label_format: str = Field(default="{label}: ${value}B", description='Template format for labels. Supports {label}, {value}, and {unit} placeholders.')
    padding: float = Field(default=4, description="Inner spacing between rectangles.")
    data: list[dict[str, str | int | list[dict]]] = Field(
        ...,
        description="""
        Hierarchical treemap data structure.

        Structure:
        - label: Name of the category
        - value: Numeric value for the category
        - children: List of sub-categories with their own label, value, and optional children

        Example:
        [
            {
                "label": "Technology",
                "value": 450,
                "children": [
                    {"label": "Software", "value": 250},
                    {"label": "Hardware", "value": 150},
                    {"label": "Cloud", "value": 50}
                ]
            },
            {
                "label": "Finance",
                "value": 300,
                "children": [
                    {"label": "Banking", "value": 180},
                    {"label": "Insurance", "value": 120}
                ]
            }
        ]
        """
    )


class GenerateTreemapChartSlide2(BaseModel):
    """Input schema for generate_treemap_chart_slide_physics."""
    main_title: str = Field(..., description="Main title of the treemap chart slide (10–60 characters). Example: Energy Distribution Across Physical Systems")
    subtitle: str = Field(..., description="Subtitle, unit, or data source. Example: Physics Systems Analysis – Q1 2026")
    insight: str = Field(..., description="Narrative insight explaining energy distribution across physical systems such as mechanical, thermal, and electrical domains")
    unit: str = Field(default=..., description="Energy unit (e.g., J, kJ, eV).")
    show_value: bool = Field(default=True, description="Whether to display numeric values inside treemap blocks.")
    show_label: bool = Field(default=True, description="Whether to display labels inside treemap blocks.")
    data_label_format: str = Field(default=..., description='Template format for labels. Example: "{label}: {value}J".')
    data: list[dict[str, str | int | list[dict]]] = Field(
        ...,
        description="""
        Treemap data represents hierarchical energy distribution in physical systems.

        Structure:
        - label: Name of the energy category (e.g., Mechanical Energy)
        - value: Total energy value
        - children: Nested breakdown into subtypes (e.g., Kinetic, Potential)

        Rules:
        - Parent value should equal or exceed sum of children values
        - All values must be numeric
        - Hierarchy should reflect physical meaning (energy → type → mechanism)
        - Treemap uses proportional area to represent energy magnitude
        - Layout follows slice-and-dice (alternating horizontal/vertical splits)

        Example:
        [
            {
                "label": "Mechanical Energy",
                "value": 500,
                "children": [
                    {"label": "Kinetic Energy", "value": 300},
                    {"label": "Potential Energy", "value": 200}
                ]
            },
            {
                "label": "Thermal Energy",
                "value": 300,
                "children": [
                    {"label": "Conduction", "value": 150},
                    {"label": "Convection", "value": 100},
                    {"label": "Radiation", "value": 50}
                ]
            },
            {
                "label": "Electrical Energy",
                "value": 200,
                "children": [
                    {"label": "AC", "value": 120},
                    {"label": "DC", "value": 80}
                ]
            }
        ]
        """
    )

class GenerateTreemapChartSlide3(BaseModel):
    """Input schema for generate_treemap_chart_slide_3."""
    main_title: str = Field(..., description="Main title of the slide (10–60 characters).")
    subtitle: Optional[str] = Field(..., description="Subtitle or data source displayed below the main title.")
    insight: Optional[str] = Field(..., description="Narrative insight or key takeaway derived from the treemap.")
    unit: str = Field(..., description="Unit displayed with values (e.g., %, $, J, M).")
    show_value: bool = Field(default=True, description="Whether to display numeric values inside treemap blocks.")
    show_label: bool = Field(default=True, description="Whether to display labels inside treemap blocks.")
    data_label_format: str = Field(default="{label}: ${value}{unit}", description="Template string for displaying labels and values.")
    data: list[dict[str, str | int | list[dict]]] = Field(
        ...,
        description="""
            Treemap data in hierarchical format.

            Structure:
            - label: Name of category
            - value: Numeric value
            - children: Optional list of subcategories

            Notes:
            - Parent value should equal or exceed sum of children values
            - All values must be numeric
            - Hierarchy should reflect physical meaning (energy → type → mechanism)
            - Treemap uses proportional area to represent energy magnitude
            - Layout follows slice-and-dice (alternating horizontal/vertical splits)

            Example:
            [
                {
                    "label": "STEM",
                    "value": 450,
                    "children": [
                        {"label": "Engineering", "value": 200},
                        {"label": "Medicine", "value": 150},
                        {"label": "Pure Sciences", "value": 100}
                    ]
                },
                {
                    "label": "Humanities",
                    "value": 300,
                    "children": [
                        {"label": "Arts", "value": 120},
                        {"label": "History", "value": 100},
                        {"label": "Literature", "value": 80}
                    ]
                },
                {
                    "label": "Services",
                    "value": 250,
                    "children": [
                        {"label": "Housing", "value": 150},
                        {"label": "Health", "value": 100}
                    ]
                }
            ]
        """
    )

class GenerateTreemapChartSlide4(BaseModel):
    """Input schema for generate_treemap_chart_slide_4."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters).")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source.")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the left panel, usually summarizing trends or highlights from the data.")
    unit: str = Field(..., description="Unit displayed with values (e.g., 'M', '%', '$').")
    show_value: bool = Field(True, description="Whether numeric values are displayed inside treemap blocks.")
    show_label: bool = Field(True, description="Whether category labels are displayed inside treemap blocks.")
    data_label_format: str = Field(default="{label}: ${value}{unit}", description="Template string for formatting labels inside blocks. Example: '{label}: ${value}{unit}'.")
    data: list[dict[str, str | int | list[dict]]] = Field(
        ...,
        description="""
            Treemap data in hierarchical format.

            Structure:
            - label: Name of category
            - value: Numeric value
            - children: Optional list of subcategories

            Notes:
            - Parent value should equal or exceed sum of children values
            - All values must be numeric
            - Hierarchy should reflect meaningful category relationships
            - Treemap uses proportional area to represent magnitude
            - Layout follows slice-and-dice (alternating horizontal/vertical splits)

            Example:
            [
                {
                    "label": "STEM",
                    "value": 450,
                    "children": [
                        {"label": "Engineering", "value": 200},
                        {"label": "Medicine", "value": 150},
                        {"label": "Pure Sciences", "value": 100}
                    ]
                },
                {
                    "label": "Humanities",
                    "value": 300,
                    "children": [
                        {"label": "Arts", "value": 120},
                        {"label": "History", "value": 100},
                        {"label": "Literature", "value": 80}
                    ]
                },
                {
                    "label": "Services",
                    "value": 250,
                    "children": [
                        {"label": "Housing", "value": 150},
                        {"label": "Health", "value": 100}
                    ]
                }
            ]
        """
    )

class GenerateTreemapChartSlide5(BaseModel):
    """Input schema for generate_treemap_chart_slide_5."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters).")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source.")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the right panel, summarizing trends or observations from the data.")
    unit: str = Field(..., description="Unit displayed with values (e.g., '%', 'USD', 'units').")
    show_value: bool = Field(True, description="Whether numeric values are displayed inside treemap blocks.")
    show_label: bool = Field(True, description="Whether category labels are displayed inside treemap blocks.")
    data_label_format: str = Field(default="{label}: {value}%", description="Template string for formatting labels inside blocks. Example: '{label}: {value}%'.")
    data: list[dict[str, str | int | list[dict]]] = Field(
        ...,
        description="""
            Treemap data in hierarchical format.

            Structure:
            - label: Name of category
            - value: Numeric value
            - children: Optional list of subcategories

            Notes:
            - Parent value should equal or exceed sum of children values
            - All values must be numeric
            - Layout uses horizontal split for parent and vertical split for children
            - Rectangle size represents proportional value

            Example:
            [
                {
                    "label": "Proteins",
                    "value": 55,
                    "children": [
                        {"label": "Structural", "value": 30},
                        {"label": "Enzymatic", "value": 25}
                    ]
                }
            ]
        """
    )


TREEMAP_TOOLS = [
    StructuredTool.from_function(
        func=generate_treemap_chart_slide_1,
        name="generate_treemap_chart_slide_1",
        description=(
            "The slide layout is structured into two main areas:\n"
            "- Top section: displays the main title and subtitle with a vertical accent bar for visual emphasis.\n"
            "- Main content area: arranged in a two-column layout.\n"
            "  • Left column: a styled insight panel highlighting key narrative takeaways.\n"
            "  • Right column: contains a treemap chart on top and a summary data table below.\n\n"
            "The layout is designed to balance qualitative insights with hierarchical data visualization and tabular comparison."
        ),
        args_schema=GenerateTreemapChartSlide1
    ),
    StructuredTool.from_function(
        func=generate_treemap_chart_slide_2,
        name="generate_treemap_chart_slide_2",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle of the slide.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left column: shows an insight panel with descriptive text.\n"
            "  + Right column: displays a treemap chart and a supporting data table below it.\n\n"
            "The layout is optimized for presenting hierarchical data and part-to-whole relationships."
        ),
        args_schema=GenerateTreemapChartSlide2
    ),
    StructuredTool.from_function(
        func=generate_treemap_chart_slide_3,
        name="generate_treemap_chart_slide_3",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left column: presents an insight panel with descriptive text and a data table below.\n"
            "  + Right column: displays a treemap chart visualization.\n\n"
            "The layout emphasizes analytical insight on the left and visual data representation on the right."
        ),
        args_schema=GenerateTreemapChartSlide3
    ),
    StructuredTool.from_function(
        func=generate_treemap_chart_slide_4,
        name="generate_treemap_chart_slide_4",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left column: contains an insight panel with descriptive text and a data table below it.\n"
            "  + Right column: displays a treemap chart visualization with a small caption beneath it.\n\n"
            "The layout separates textual insight and tabular data on the left from hierarchical visualization on the right."
        ),
        args_schema=GenerateTreemapChartSlide4
    ),
    StructuredTool.from_function(
        func=generate_treemap_chart_slide_5,
        name="generate_treemap_chart_slide_5",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left column: displays a treemap chart visualization.\n"
            "  + Right column: presents an insight panel with descriptive text and a data table below.\n\n"
            "The layout emphasizes visual data representation on the left and analytical insight on the right."
        ),
        args_schema=GenerateTreemapChartSlide5
    )
]