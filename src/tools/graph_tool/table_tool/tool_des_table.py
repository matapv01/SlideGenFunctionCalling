from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from .html_lib_table import (
    generate_table_slide_1,
    generate_table_slide_2,
    generate_table_slide_3,
    generate_table_slide_4,
    generate_table_slide_5,
    generate_table_slide_6,
    generate_table_slide_7
)
class GenerateTableSlide1(BaseModel):
    """Input schema for generate_table_slide_1."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide.")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    insight: str = Field(..., description="Key analytical insight shown in the left panel.")
    unit: str = Field(..., description="Unit appended to each value (e.g., 'GW', '%', '$').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value} units').")
    columns: List[str] = Field(..., description="List of column names.")
    rows: List[Dict[str, str | List[float]]] = Field(
        ...,
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
        """
    )

class GenerateTableSlide2(BaseModel):
    """Input schema for generate_table_slide_2."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide.")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    insight: str = Field(..., description="Key analytical insight shown in the left panel.")
    unit: str = Field(..., description="Unit appended to each value (e.g., '%', 'GW', '$').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}{unit}", description="Format string used to display values (e.g., '{value}', '{value}%').")
    columns: List[str] = Field(..., description="List of column names.")
    rows: List[Dict[str, str | List[float]]] = Field(
        ...,
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
        """
    )

class GenerateTableSlide3(BaseModel):
    """Input schema for generate_table_slide_3."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide.")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    insight: str = Field(..., description="Key analytical insight shown in the left panel.")
    unit: str = Field(..., description="Unit appended to each value (e.g., '%', 'sites', 'count').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}{unit}", description="Format string used to display values (e.g., '{value}', '{value} units').")
    columns: List[str] = Field(..., description="List of column names.")
    rows: List[Dict[str, str | List[float]]] = Field(
        ...,
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
        """
    )

class GenerateTableSlide4(BaseModel):
    """Input schema for generate_table_slide_4."""
    main_title: str = Field(default="Average Blood Pressure by Age Group", description="Main title displayed at the top of the slide.")
    subtitle: str = Field(default="Unit: mmHg | Data Source: National Health Survey 2025", description="Subtitle displayed below the main title.")
    insight: str = Field(default="Healthcare is important, Keep your health in check!", description="Key analytical insight shown in the left panel.")
    unit: str = Field(default="mmHg", description="Optional unit appended to each value (e.g., 'mmHg', '%').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value} mmHg').")
    categories: List[str] = Field(default=["18-25", "26-35", "36-45", "46-60", "60+"], description="List of category labels for columns.")
    series: List[Dict[str, Any]] = Field(
        ...,
        description="""
            Series data with names and values.

            Structure:
            - series: list of series objects
                - name: name of the series (e.g., 'Male', 'Female')
                - values: list of numeric values corresponding to each category

            Notes:
            - Each series must have the same number of values as categories
        """
    )

class GenerateTableSlide5(BaseModel):
    """Input schema for generate_table_slide_5."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters).")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating context or theme.")
    insight: str = Field(..., description="Key descriptive or analytical insight displayed in a full-width panel above the table.")
    unit: str = Field(default="", description="Optional unit appended to each value (e.g., '%', 'sites', 'count').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value} units').")
    columns: List[str] = Field(..., description="List of column names.")
    rows: List[Dict[str, str | List[float]]] = Field(
        ...,
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
        """
    )

class GenerateTableSlide6(BaseModel):
    """Input schema for generate_table_slide_6."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters).")
    subtitle: str = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source.")
    insight: str = Field(..., description="Key analytical insight shown in the left panel. Leave empty if not needed.")
    unit: str = Field(..., description="Optional unit appended to each value (e.g., 'GW', '%', '$').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")    
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value} units').")
    columns: List[str] = Field(..., description="List of column names.")
    rows: List[Dict[str, str | List[float]]] = Field(
        ...,
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
        """
    )

class GenerateTableSlide7(BaseModel):
    """Input schema for generate_table_slide_7."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide.")
    subtitle: str = Field(..., description="Subtitle displayed below the main title.")
    show_legend: bool = Field(..., description="Whether to display the legend.")
    legend_items: List[Dict[str, str]] = Field(
        ...,
        description="""List of legend items with label-to-color mapping.
        Each item contains:
        - label: (str) Legend label name that matches cell content
        - color: (str) Hex color code for that legend item

        Example:
        [
            {"label": "Marketing", "color": "#9a7a63"},
            {"label": "Financial", "color": "#b7b9ab"}
        ]"""
    )
    columns: List[str] = Field(..., description="List of column header labels (e.g., ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']).")
    rows: List[Dict] = Field(
        ...,
        description="""Table row data with cells mapped to legend labels.
        Structure:
        - label: (str) Row header name
        - cells: (list) Cell values, each can be:
            - None (renders with light background)
            - A string matching a legend_items label (renders with that label's color)

        Example:
        [
            {
                "label": "Week 1",
                "cells": [None, "Financial", None, None, None]
            }
        ]"""
    )

TABLE_TOOLS = [
    StructuredTool.from_function(
        func=generate_table_slide_1,
        name="generate_table_slide_1",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left column: presents an insight panel with descriptive text.\n"
            "  + Right column: displays a styled data table with columns and rows, with svg next to the right.\n\n"
            "The layout emphasizes analytical interpretation on the left and structured data comparison on the right."
        ),
        args_schema=GenerateTableSlide1
    ),
    StructuredTool.from_function(
        func=generate_table_slide_2,
        name="generate_table_slide_2",
        description=(
            "This slide has a clean Chemistry Lab-themed layout:\n"
            "- Upper section: features a large, bold main title with a vertical accent bar, "
            "and a subtitle beneath it.\n"
            "- Lower section: displays a high-contrast, rounded-corner table showing experimental data.\n"
            "- Decorative elements include a semi-transparent top blob and a Chemistry-style beaker SVG for visual flair.\n"
            "Overall design emphasizes readability and a professional scientific aesthetic."
        ),
        args_schema=GenerateTableSlide2
    ),
    StructuredTool.from_function(
        func=generate_table_slide_3,
        name="generate_table_slide_3",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Upper section: displays the main title and subtitle with an Islamic luxury style, "
            "accompanied by a decorative lantern element on the right.\n"
            "- Lower section: contains a single full-width panel featuring a large stylized data table.\n"
            "The table is the central focus, designed with elegant gold accents, soft glow effects, "
            "and a refined cultural aesthetic."
        ),
        args_schema=GenerateTableSlide3
    ),
    StructuredTool.from_function(
        func=generate_table_slide_4,
        name="generate_table_slide_4",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top with a vertical accent bar.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left column: presents an insight panel with highlighted text and a decorative medical-themed icon below.\n"
            "  + Right column: displays a styled data table with columns and rows.\n\n"
            "The layout emphasizes health insights on the left and structured data comparison on the right."
        ),
        args_schema=GenerateTableSlide4
    ),
    StructuredTool.from_function(
        func=generate_table_slide_5,
        name="generate_table_slide_5",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top.\n"
            "- Content section: uses a vertical layout:\n"
            "  + Upper section: presents a full-width insight panel with descriptive text.\n"
            "  + Lower section: displays a styled data table with columns and rows.\n\n"
            "The layout emphasizes contextual explanation at the top and structured data comparison below."
        ),
        args_schema=GenerateTableSlide5
    ),
    StructuredTool.from_function(
        func=generate_table_slide_6,
        name="generate_table_slide_6",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top.\n"
            "- Content section: uses a two-column layout:\n"
            "  + Left column: presents an insight panel with descriptive text and a decorative visual below.\n"
            "  + Right column: displays a styled data table with row labels and multiple columns.\n\n"
            "The layout emphasizes narrative insight on the left and structured data comparison on the right."
        ),
        args_schema=GenerateTableSlide6
    ),
    StructuredTool.from_function(
        func=generate_table_slide_7,
        name="generate_table_slide_7",
        description=(
            "The slide layout is divided into two main sections:\n"
            "- Header section: displays the main title and subtitle at the top.\n"
            "- Content section: centered layout containing:\n"
            "  + An optional horizontal legend displayed below the header.\n"
            "  + A full-width table where rows and columns form a grid structure.\n\n"
            "Each cell in the table is visually encoded using background colors mapped from legend items, "
            "creating a clean and minimalist table-based infographic."
        ),
        args_schema=GenerateTableSlide7
    )
]