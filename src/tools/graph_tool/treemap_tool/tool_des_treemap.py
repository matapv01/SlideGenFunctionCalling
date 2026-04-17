from typing import List, TypedDict
from html_lib_treemap import (
    generate_treemap_chart_slide_1,
    generate_treemap_chart_slide_2,
    generate_treemap_chart_slide_3,
    generate_treemap_chart_slide_4,
    generate_treemap_chart_slide_5
)

class GenerateTreemapChartSlide1(BaseModel):
    """Input schema for generate_treemap_chart_slide_1"""
    main_title: str = Field(
        default="Stock Market Distribution by Sector",
        description="Main title of the treemap chart slide (10–60 characters)."
    )

    subtitle: str = Field(
        default="Global Equity Markets – Q1 2026 Analysis",
        description="Subtitle, unit, or data source."
    )

    insight: str = Field(
        default=(
            "Technology remains the dominant force, led by Software and Hardware. "
            "Finance follows closely, showing a balanced distribution across Banking and Insurance. "
            "Consumer Goods shows significant growth in E-commerce segments."
        ),
        description="Narrative insight explaining key patterns."
    )
    unit: Optional[str] = Field(default="B", description="Optional unit appended to values")
    show_value: bool = Field(default=True, description="Whether to display numeric values inside blocks.")
    show_label: bool = Field(default=True, description="Whether to display labels inside blocks.")
    data_label_format: Optional[str] = Field(default="{label}: ${value}B", description='Template format for labels')
    padding: float = Field(default=4, description="Inner spacing between rectangles.")
    border_radius: float = Field(default=4, description="Rounded corner radius for blocks.")
    base_color: str = Field(default="#1E3A8A", description="Primary color for treemap blocks.")
    accent_color: str = Field(default="#3B82F6", description="Accent color used for UI highlights and decorations")
    text_color: str = Field(default="#FFFFFF", description="Text color inside blocks.")
    border_color: str = Field(default="#1E293B", description="Border color of rectangles.")
    data: list[dict[str, str | int | list[dict]]] = Field(
        default=...,
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
    font_family: str = Field(default="Inter, sans-serif", description="Main font family for the slide")
    main_title_color: str = Field(default="#FFFFFF", description="Color of the main title")
    subtitle_color: str = Field(default="#94A3B8", description="Color of the subtitle text")
    insight_text_color: str = Field(default="#CBD5E1", description="Color of the insight text block")
    main_title_font_size: str = Field(default="64px", description="Font size for the main title")
    subtitle_font_size: str = Field(default="28px", description="Font size for the subtitle")
    insight_font_size: str = Field(default="26px", description="Font size for the insight text")


class GenerateTreemapChartSlide2(BaseModel):
    """Input schema for generate_treemap_chart_slide_physics."""
    main_title: str = Field(default=..., description="Main title of the treemap chart slide (10–60 characters). Example: Energy Distribution Across Physical Systems")
    subtitle: str = Field(default=..., description="Subtitle, unit, or data source. Example: Physics Systems Analysis – Q1 2026")
    insight: str = Field(default=..., description="Narrative insight explaining energy distribution across physical systems such as mechanical, thermal, and electrical domains")
    unit: Optional[str] = Field(default=..., description="Energy unit (e.g., J, kJ, eV).")
    show_value: bool = Field(default=True, description="Whether to display numeric values inside treemap blocks.")
    show_label: bool = Field(default=True, description="Whether to display labels inside treemap blocks.")
    data_label_format: Optional[str] = Field(default=..., description='Template format for labels. Example: "{label}: {value}J".')
    padding: float = Field(default=6, description="Inner spacing between rectangles in the treemap layout.")
    border_radius: float = Field(default=4, description="Rounded corner radius for treemap blocks.")
    base_color: str = Field(default="#1E3A8A", description="Primary color used for treemap blocks (physics theme, e.g., deep blue).")
    accent_color: str = Field(default="#E2E045", description="Accent color used to highlight values or key segments.")
    text_color: str = Field(default="#FFFFFF", description="Text color displayed inside treemap blocks.")
    border_color: str = Field(default="#FFFFFF", description="Border color of treemap rectangles.")
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
    font_family: str = Field(default="Inter, Arial, sans-serif", description="Main font family for the slide")
    main_title_color: str = Field(default="#1E3A8A", description="Color of the main title")
    subtitle_color: str = Field(default="#64748B", description="Color of the subtitle text")
    insight_text_color: str = Field(default="#334155", description="Color of the insight text block")
    main_title_font_size: str = Field(default="64px", description="Font size for the main title")
    subtitle_font_size: str = Field(default="28px", description="Font size for the subtitle")
    insight_font_size: str = Field(default="26px",description="Font size for the insight text")

class GenerateTreemapChartSlide3(BaseModel):
    """Input schema for generate_treemap_chart_slide_3."""
    main_title: str = Field(default="Phân Bổ Tài Nguyên Giáo Dục",description="Main title of the slide (10–60 characters).")
    subtitle: Optional[str] = Field(default="Báo cáo tổng kết học kỳ I - Năm học 2025-2026",description="Subtitle or data source displayed below the main title.")
    insight: Optional[str] = Field(default="Khối Khoa học và Ngôn ngữ chiếm tỷ trọng lớn nhất trong ngân sách (tổng 70%). Trong đó, tài liệu đọc hiểu là hạng mục ưu tiên cao nhất trong bộ môn Ngôn ngữ.",description="Narrative insight or key takeaway derived from the treemap.")
    unit: str = Field(default="%", description="Unit displayed with values (e.g., %, $, J).")
    show_value: bool = Field(default=True,description="Whether to display numeric values inside treemap blocks.")
    show_label: bool = Field(default=True,description="Whether to display labels inside treemap blocks.")
    data_label_format: str = Field(default="{label}: {value}%",description="Template string for displaying labels and values.")
    padding: float = Field(default=4,description="Inner spacing between rectangles in the treemap.")
    border_radius: float = Field(default=8,description="Corner radius for treemap rectangles.")
    base_color: str = Field(default="#1a948e",description="Primary color used for treemap blocks.")
    text_color: str = Field(default="#ffffff",description="Text color inside treemap blocks.")
    border_color: str = Field(default="#fbc02d",description="Border color of treemap groups.")
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
                    "label": "Technology",
                    "value": 45,
                    "children": [
                        {"label": "Software", "value": 25},
                        {"label": "Hardware", "value": 15},
                        {"label": "Services", "value": 5}
                    ]
                },
                {
                    "label": "Finance",
                    "value": 30,
                    "children": [
                        {"label": "Banking", "value": 15},
                        {"label": "Insurance", "value": 10},
                        {"label": "Investments", "value": 5}
                    ]
                },
                {
                    "label": "Healthcare",
                    "value": 25,
                    "children": [
                        {"label": "Pharma", "value": 10},
                        {"label": "Devices", "value": 8},
                        {"label": "Services", "value": 7}
                    ]
                }
            ]
        """
    )
    font_family: str = Field(default="'Poppins', 'Segoe UI', sans-serif", description="Font family used for the entire slide.")
    accent_color: str = Field(default="#fbc02d", description="Accent color used for borders and highlights.")
    main_title_color: str = Field(default="#e5533d", description="Color of the main title text.")
    subtitle_color: str = Field(default="#1a948e", description="Color of the subtitle text.")
    insight_text_color: str = Field(default="#333333", description="Color of the insight text.")
    main_title_font_size: str = Field(default="64px", description="Font size of the main title.")
    subtitle_font_size: str = Field(default="28px", description="Font size of the subtitle.")
    insight_font_size: str = Field(default="24px", description="Font size of the insight text.")

class GenerateTreemapChartSlide4(BaseModel):
    """Input schema for generate_treemap_chart_slide_4."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters).")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source.")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the left panel, usually summarizing trends or highlights from the data.")
    unit: str = Field(..., description="Unit displayed with values (e.g., 'M', '%', '$').")
    show_value: bool = Field(True, description="Whether numeric values are displayed inside treemap blocks.")
    show_label: bool = Field(True, description="Whether category labels are displayed inside treemap blocks.")
    data_label_format: str = Field(default="{label}: ${value}{unit}", description="Template string for formatting labels inside blocks. Example: '{label}: ${value}{unit}'.")
    padding: float = Field(default=4, description="Spacing between treemap rectangles.")
    border_radius: float = Field(default=8, description="Corner radius applied to treemap rectangles.")
    base_color: str = Field(default="#1a5073", description="Primary color used for treemap blocks.")
    accent_color: str = Field(default="#fdf9c4", description="Accent color used for decorative elements and table background.")
    border_color: str = Field(default="#ffffff", description="Border color for treemap rectangles.")
    text_color: str = Field(default="#ffffff", description="Text color inside treemap blocks.")
    data: list[dict[str, Any]] = Field(
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
                    "label": "Technology",
                    "value": 45,
                    "children": [
                        {"label": "Software", "value": 25},
                        {"label": "Hardware", "value": 15},
                        {"label": "Services", "value": 5}
                    ]
                },
                {
                    "label": "Finance",
                    "value": 30,
                    "children": [
                        {"label": "Banking", "value": 15},
                        {"label": "Insurance", "value": 10},
                        {"label": "Investments", "value": 5}
                    ]
                },
                {
                    "label": "Healthcare",
                    "value": 25,
                    "children": [
                        {"label": "Pharma", "value": 10},
                        {"label": "Devices", "value": 8},
                        {"label": "Services", "value": 7}
                    ]
                }
            ]
        """
    )
    font_family: str = Field(default="'Lato', sans-serif", description="Font family applied to the entire slide.")
    main_title_color: str = Field(default="#1a5073", description="Color of the main title.")
    subtitle_color: str = Field(default="#1a5073", description="Color of the subtitle.")
    insight_text_color: str = Field(default="#1a5073", description="Color of the insight text.")
    main_title_font_size: str = Field(default="80px", description="Font size of the main title (e.g., '80px').")
    subtitle_font_size: str = Field(default="32px", description="Font size of the subtitle.")
    insight_font_size: str = Field(default="28px", description="Font size of the insight text.")

class GenerateTreemapChartSlide5(BaseModel):
    """Input schema for generate_treemap_chart_slide_5."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters).")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source.")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the right panel, summarizing trends or observations from the data.")
    unit: str = Field(..., description="Unit displayed with values (e.g., '%', 'USD', 'units').")
    show_value: bool = Field(True, description="Whether numeric values are displayed inside treemap blocks.")
    show_label: bool = Field(True, description="Whether category labels are displayed inside treemap blocks.")
    data_label_format: str = Field(default="{label}: {value}%", description="Template string for formatting labels inside blocks. Example: '{label}: {value}%'.")
    padding: float = Field(default=6, description="Spacing between treemap rectangles.")
    border_radius: float = Field(default=8, description="Corner radius applied to treemap rectangles.")
    base_color: str = Field(default="#d86c9e", description="Primary color used for treemap blocks.")
    accent_color_chart: str = Field(default="#f4be52", description="Accent color used for highlighting chart elements and table headers.")
    border_color: str = Field(default="#4c234a", description="Border color for treemap rectangles.")
    text_color: str = Field(default="#fce7cf", description="Text color inside treemap blocks.")
    data: list[dict[str, Any]] = Field(
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
    font_family: str = Field(default="'Fredoka', sans-serif", description="Font family applied to the entire slide.")
    accent_color: str = Field(default="#d86c9e", description="Accent color used for insight panel decoration.")
    main_title_color: str = Field(default="#fce7cf", description="Color of the main title.")
    subtitle_color: str = Field(default="#f4be52", description="Color of the subtitle.")
    insight_text_color: str = Field(default="#fce7cf", description="Color of the insight text.")
    main_title_font_size: str = Field(default="100px", description="Font size of the main title (e.g., '100px').")
    subtitle_font_size: str = Field(default="35px", description="Font size of the subtitle.")
    insight_font_size: str = Field(default="28px", description="Font size of the insight text.")


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