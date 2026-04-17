from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

class GenerateTableSlide1(BaseModel):
    """Input schema for generate_table_slide_1."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Renewable Energy Capacity by Region'")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Global Energy Research Lab – 2024 Data'")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the left panel, summarizing trends or comparisons in the table. Example: 'Asia leads in solar capacity while Europe dominates wind energy.'")
    unit: Optional[str] = Field(default=None, description="Optional unit appended to each value (e.g., 'GW', '%', '$').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value} units').")
    header_bg: str = Field(default="#76C2B4", description="Background color of the table header.")
    grid_color: str = Field(default="#D1D5DB", description="Color of table borders and grid lines.")
    text_color: str = Field(default="#333333", description="Color of table cell text.")
    highlight_bg: str = Field(default="#E6F4F1", description="Background color used for row labels.")
    columns: List[str] = Field(..., description="List of column names (e.g., ['Solar', 'Wind', 'Hydro']).")
    rows: List[Dict[str, str | List[float]]] = Field(
        ..., 
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row (e.g., 'Asia')
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
            - Used to compare categories across multiple metrics

            Example:
            [
                {
                    "label": "Asia",
                    "values": [620, 430, 510]
                }
            ]
        """
    )
    font_family: str = Field(default="Inter, Arial, sans-serif", description="Font family applied to the entire slide.")
    accent_color: str = Field(default="#76C2B4", description="Accent color used for highlights and decorations.")
    main_title_color: str = Field(default="#333333", description="Color of the main title.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle.")
    insight_text_color: str = Field(default="#444444", description="Color of the insight text.")
    main_title_font_size: str = Field(default="72px", description="Font size of the main title (e.g., '72px').")
    subtitle_font_size: str = Field(default="32px", description="Font size of the subtitle.")
    insight_font_size: str = Field(default="28px", description="Font size of the insight text.")

class GenerateTableSlide2(BaseModel):
    """Input schema for generate_table_slide_2."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Chemical Reagent Stability Analysis'")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Source: International Journal of Applied Chemistry 2026'")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the left panel, summarizing trends or comparisons in the table. Example: 'High-purity salts show better stability compared to organic compounds.'")
    unit: Optional[str] = Field(default=None, description="Optional unit appended to each value (e.g., '%', 'GW', '$').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value}%').")
    header_bg: str = Field(default="#3B3781", description="Background color of the table header.")
    grid_color: str = Field(default="#D1D5DB", description="Color of table borders and grid lines.")
    text_color: str = Field(default="#1F2937", description="Color of table cell text.")
    highlight_bg: str = Field(default="#F3F4F6", description="Background color used for alternating row highlights.")
    accent_color: str = Field(default="#FFB300", description="Accent color used for highlights and decorative elements.")
    columns: List[str] = Field(..., description="List of column names (e.g., ['Purity Level', 'Solubility', 'Reaction Yield']).")
    rows: List[Dict[str, str | List[float]]] = Field(
        ..., 
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row (e.g., 'Ethanol (C2H5OH)')
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
            - Used to compare experimental or chemical properties across samples

            Example:
            [
                {
                    "label": "Ethanol (C2H5OH)",
                    "values": [99.8, 100, 92]
                }
            ]
        """
    )
    font_family: str = Field(default="'Inter', sans-serif", description="Font family applied to the entire slide.")
    main_title_color: str = Field(default="#3B3781", description="Color of the main title.")
    subtitle_color: str = Field(default="#6B7280", description="Color of the subtitle.")
    insight_text_color: str = Field(default="#1F2937", description="Color of the insight text.")
    main_title_font_size: str = Field(default="72px", description="Font size of the main title (e.g., '72px').")
    subtitle_font_size: str = Field(default="30px", description="Font size of the subtitle.")
    insight_font_size: str = Field(default="28px", description="Font size of the insight text.")

class GenerateTableSlide3(BaseModel):
    """Input schema for generate_table_slide_3."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Islamic Cultural Contributions by Region'")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Global Islamic Heritage Study – 2024'")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the left panel. Can be left empty if no insight is needed.")
    unit: Optional[str] = Field(..., description="Optional unit appended to each value (e.g., '%', 'sites', 'count').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value} units').")
    header_bg: str = Field(default="linear-gradient(135deg, #D4AF37, #AA7C11)", description="Background style of the table header (supports solid color or gradient).")
    grid_color: str = Field(default="rgba(212, 175, 55, 0.2)", description="Color of table borders and grid lines.")
    text_color: str = Field(default="#FFFFFF", description="Color of table cell text.")
    highlight_bg: str = Field(default="rgba(10, 52, 39, 0.4)", description="Background color of the main content container.")
    columns: List[str] = Field(..., description="List of column names (e.g., ['Mosques', 'Scholars', 'Cultural Sites']).")
    rows: List[Dict[str, str | List[float]]] = Field(
        ..., 
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row (e.g., 'Middle East')
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
            - Used to compare cultural or regional metrics

            Example:
            [
                {
                    "label": "Middle East",
                    "values": [1200, 850, 400]
                }
            ]
        """
    )
    font_family: str = Field(default="'Outfit', sans-serif", description="Font family applied to the entire slide.")
    accent_color: str = Field(default="#D4AF37", description="Accent color used for highlights and decorative elements.")
    main_title_color: str = Field(default="#D4AF37", description="Color of the main title.")
    subtitle_color: str = Field(default="#E0E0E0", description="Color of the subtitle.")
    insight_text_color: str = Field(default="#FFFFFF", description="Color of the insight text.")
    main_title_font_size: str = Field(default="64px", description="Font size of the main title (e.g., '64px').")
    subtitle_font_size: str = Field(default="28px", description="Font size of the subtitle.")
    insight_font_size: str = Field(default="28px", description="Font size of the insight text.")

class GenerateTableSlide4(BaseModel):
    """Input schema for generate_table_slide_4."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Average Blood Pressure by Age Group'")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or data source. Example: 'Unit: mmHg | Data Source: National Health Survey 2025'")
    insight: Optional[str] = Field(..., description="Key analytical insight shown in the left panel, summarizing trends or health observations. Example: 'Blood pressure tends to increase with age across both genders.'")
    unit: Optional[str] = Field(..., description="Optional unit appended to each value (e.g., 'mmHg', '%').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value} mmHg').")
    header_bg: str = Field(default="#5D3B6B", description="Background color of the table header.")
    grid_color: str = Field(default="rgba(255, 255, 255, 0.1)", description="Color of table borders and grid lines.")
    text_color: str = Field(default="#FFFFFF", description="Color of table cell text.")
    highlight_bg: str = Field(default="rgba(232, 156, 180, 0.15)", description="Background color used for row labels or highlight areas.")
    columns: List[str] = Field(..., description="List of column names (e.g., ['18-25', '26-35', '36-45', '46-60', '60+']).")
    rows: List[Dict[str, str | List[float]]] = Field(
        ..., 
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row (e.g., 'Male', 'Female')
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
            - Used to compare groups across categories

            Example:
            [
                {
                    "label": "Male",
                    "values": [118, 122, 128, 135, 142]
                }
            ]
        """
    )
    font_family: str = Field(default="Inter, sans-serif", description="Font family applied to the entire slide.")
    accent_color: str = Field(default="#10B981", description="Accent color used for highlights and decorative elements.")
    main_title_color: str = Field(default="#4ADE80", description="Color of the main title.")
    subtitle_color: str = Field(default="#64748B", description="Color of the subtitle.")
    insight_text_color: str = Field(default="#2DD4BF", description="Color of the insight text.")
    main_title_font_size: str = Field(default="70px", description="Font size of the main title (e.g., '70px').")
    subtitle_font_size: str = Field(default="30px", description="Font size of the subtitle.")
    insight_font_size: str = Field(default="28px", description="Font size of the insight text.")

class GenerateTableSlide5(BaseModel):
    """Input schema for generate_table_slide_5."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide (10–60 characters). Example: 'Vietnamese Cultural Heritage by Region'")
    subtitle: Optional[str] = Field(..., description="Subtitle displayed below the main title, typically indicating context or theme. Example: 'Traditional Values & Cultural Assets across Vietnam'")
    insight: Optional[str] = Field(..., description="Key descriptive or analytical insight displayed in a full-width panel above the table. Typically explains cultural context or highlights regional differences.")
    unit: Optional[str] = Field(..., description="Optional unit appended to each value (e.g., '%', 'sites', 'count').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value} units').")
    header_bg: str = Field(default="linear-gradient(135deg, #8B0000, #5D0E0E)", description="Background style of the table header (supports solid color or gradient).")
    grid_color: str = Field(default="#D4AF37", description="Color of table borders and grid lines.")
    text_color: str = Field(default="#FFFFFF", description="Color of table cell text.")
    highlight_bg: str = Field(default="rgba(93, 14, 14, 0.6)", description="Background color used for row labels.")
    columns: List[str] = Field(..., description="List of column names (e.g., ['Festivals', 'Historical Sites', 'Traditional Crafts']).")
    rows: List[Dict[str, str | List[float]]] = Field(
        ..., 
        description="""
            Table row data.

            Structure:
            - rows: list of row objects
                - label: name of the row (e.g., 'Northern Vietnam')
                - values: list of numeric values corresponding to each column

            Notes:
            - Each row must have the same number of values as columns
            - Used to compare regional or categorical metrics

            Example:
            [
                {
                    "label": "Northern Vietnam",
                    "values": [120, 85, 60]
                }
            ]
        """
    )
    font_family: str = Field(default="'Times New Roman', serif", description="Font family applied to the entire slide.")
    accent_color: str = Field(default="#FFD700", description="Accent color used for highlights and decorative elements.")
    main_title_color: str = Field(default="#FFD700", description="Color of the main title.")
    subtitle_color: str = Field(default="#E0E0E0", description="Color of the subtitle.")
    insight_text_color: str = Field(default="#FFFFFF", description="Color of the insight text.")
    main_title_font_size: str = Field(default="64px", description="Font size of the main title (e.g., '64px').")
    subtitle_font_size: str = Field(default="28px", description="Font size of the subtitle.")
    insight_font_size: str = Field(default="28px", description="Font size of the insight text.")

class GenerateTableSlide6(BaseModel):
    """Input schema for generate_table_slide_6."""
    main_title: str = Field(default="Bức Tranh Làng Quê Việt Nam", description="Main title displayed at the top of the slide (10–60 characters).")
    subtitle: Optional[str] = Field(default="Đơn vị: Khu vực | Nguồn: Khảo sát nông thôn Việt Nam 2025", description="Subtitle displayed below the main title, typically indicating context or data source.")
    insight: Optional[str] = Field(default=None, description="Key analytical insight shown in the left panel. Leave empty if not needed.")
    unit: Optional[str] = Field(default="", description="Optional unit appended to each value (e.g., 'GW', '%', '$').")
    show_value: bool = Field(default=True, description="Whether numeric values are displayed inside table cells.")    
    data_label_format: str = Field(default="{value}", description="Format string used to display values (e.g., '{value}', '{value} units').")    
    header_bg: str = Field(default="linear-gradient(135deg, #2D6A4F, #1B4332)", description="Background color of the table header.")
    grid_color: str = Field(default="rgba(183, 228, 199, 0.35)", description="Color of table borders and grid lines.")
    text_color: str = Field(default="#081C15", description="Color of table cell text.")
    highlight_bg: str = Field(default="rgba(247, 241, 227, 0.9)", description="Background color used for row labels.")
    columns: List[str] = Field(default=["Nông nghiệp", "Chăn nuôi", "Thủ công"], description="List of column names.")
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
    font_family: str = Field(default="'Inter', sans-serif", description="Font family applied to the entire slide.")
    accent_color: str = Field(default="#D4AF37", description="Accent color used for highlights and decorations.")
    main_title_color: str = Field(default="#1B4332", description="Color of the main title.")
    subtitle_color: str = Field(default="#2D6A4F", description="Color of the subtitle.")
    insight_text_color: str = Field(default="#40916C", description="Color of the insight text.")
    main_title_font_size: str = Field(default="65px", description="Font size of the main title.")
    subtitle_font_size: str = Field(default="28px", description="Font size of the subtitle.")
    insight_font_size: str = Field(default="30px", description="Font size of the insight text.")


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
    )
]