from backend.workflows.slidegen_workflow.tools import xml_tool
# Auto-generated from tools.py preserving all original parameter schemas
# This conversion maintains the exact parameter definitions from the source

import json

from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


# Import all slide generation functions from xml_tool
from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_dynamic_intro_slide_xml,
    generate_elegant_agenda_slide_xml,
    generate_dusk_transition_slide_xml,
    generate_vision_mission_slide_xml,
    generate_geometric_split_content_slide_xml,
    generate_memphis_grid_slide_xml,
    generate_elegant_points_slide_xml,
    generate_timeline_slide_xml,
    generate_colorful_team_grid_slide_xml,
    generate_quote_slide_xml,
    generate_reference_slide_xml,
    generate_modern_contact_slide_xml,
    generate_intro_slide_xml,
    generate_warm_intro_slide_xml,
    generate_elegant_education_slide_xml,
    generate_creative_team_slide_xml,
    generate_grid_team_slide_xml,
    generate_online_notebook_slide_xml,
    generate_classic_toc_slide_xml,
    generate_notebook_section_slide_xml,
    generate_science_2col_slide_xml,
    generate_thank_you_slide_xml,
    generate_thank_you_watching_slide_xml,
    generate_about_me_slide_xml,
    generate_content_2col_slide_xml,
    generate_pie_chart_slide_xml,
    generate_donut_chart_slide_xml
)


# ===========================================================================================
# PYDANTIC INPUT SCHEMAS ORDERED ACCORDING TO IMPORT SEQUENCE
# ===========================================================================================

# === SLIDE INTRO CLASSES ===

class GenerateElegantEducationSlideInput(BaseModel):
    title: str = Field(
        default="Elegant Education\nPack for Students",
        description="The main title of the presentation, displayed in large bold text.",
    )
    subtitle: str = Field(
        default="Here is where your presentation begins",
        description="The subtitle displayed below the main title.",
    )
    background_color: str = Field(
        default="#FFFFFF",
        description="Background color for the slide (default: #FFFFFF).",
    )
    title_color: str = Field(
        default="#3F474A",
        description="Color of the main title text.",
    )
    subtitle_color: str = Field(
        default="#515558",
        description="Color of the subtitle text.",
    )

class GenerateOnlineNotebookSlideInput(BaseModel):
    title: str = Field(
        default="ONLINE NOTEBOOK",
        description="The main title of the presentation. It will be split into two parts divided by a line.",
    )
    subtitle: str = Field(
        default="Here is where your presentation begins",
        description="The subtitle displayed below the main title.",
    )
    background_color: str = Field(
        default="#FFFFFF",
        description="Background color for the slide (default: #FFFFFF).",
    )
    title_color: str = Field(
        default="#1D4984",
        description="Color of the main title text.",
    )
    subtitle_color: str = Field(
        default="#2C3E50",
        description="Color of the subtitle text.",
    )

class GenerateClassicTocSlideInput(BaseModel):
    title: str = Field(
        default="Table of contents",
        description="The main title of the slide.",
    )
    items: list[dict] = Field(
        default=None,
        description="List of table of content items. Each dict should have 'number' (e.g. '01'), 'title' (MUST be short, 1-3 words max), and 'description' (MUST be very short, 3-6 words maximum). Maximum 6 items.",
    )
    background_color: str = Field(
        default="#EBE4D5",
        description="Background color for the slide (default: #EBE4D5).",
    )
    theme_color: str = Field(
        default="#4A3F35",
        description="Color of the borders and text (default: #4A3F35).",
    )

class GenerateNotebookSectionSlideInput(BaseModel):
    number: str = Field(
        default="01",
        description="Section number, typically a 2-digit string like '01', '02'.",
    )
    title: str = Field(
        default="Introduction",
        description="Main section title. Should be 1-3 words max.",
    )
    subtitle: str = Field(
        default="You can enter a subtitle here if you need it",
        description="Optional subtitle for the section. Usually a short phrase or sentence.",
    )

class GenerateScience2ColSlideInput(BaseModel):
    main_title: str = Field(
        default="From molecules to life",
        description="The main title at the top of the slide.",
    )
    col1_title: str = Field(
        default="Column 1",
        description="Title for the first column.",
    )
    col1_desc: str = Field(
        default="Description for the first column.",
        description="Main text content for the first column. Should be a paragraph.",
    )
    col2_title: str = Field(
        default="Column 2",
        description="Title for the second column.",
    )
    col2_desc: str = Field(
        default="Description for the second column.",
        description="Main text content for the second column. Should be a paragraph.",
    )

class GenerateThankYouSlideInput(BaseModel):
    title: str = Field(
        default="Thank You",
        description="The main text at the top, usually 'Thank You'.",
    )
    message: str = Field(
        default="We appreciate your trust and confidence in us. Your support is invaluable, and we look forward to serving you again.",
        description="A short gratitude message displayed below the title.",
    )

class GenerateThankYouWatchingSlideInput(BaseModel):
    title: str = Field(
        default="THANK YOU",
        description="The main title, usually 'THANK YOU'.",
    )
    message: str = Field(
        default="for watching",
        description="A short sub-message displayed below the title, like 'for watching'.",
    )

class GenerateAboutMeSlideInput(BaseModel):
    title: str = Field(
        default="About Me",
        description="The main title text.",
    )
    paragraph: str = Field(
        default="Lorem ipsum dolor amet, consectetur adipiscing elit, sed eiusmod tempor incididunt ut labore dolore magna aliqua. Lorem ipsum dolor amet, consectetur adipiscing elit, sed eiusmod tempor incididunt ut labore dolore magna aliqua.",
        description="The paragraph text about the person.",
    )
    image_url: str = Field(
        default="https://picsum.photos/seed/portrait/600/800",
        description="The URL for the portrait image (will be cropped as an oval).",
    )

class GenerateContent2ColSlideInput(BaseModel):
    title: str = Field(
        default="CONTENT",
        description="The main title text.",
    )
    subtitle_1: str = Field(
        default="PRIMARY REFERENCE TITLE",
        description="The first subtitle.",
    )
    paragraph_1: str = Field(
        default="Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. They serve various purposes and are effective tools.",
        description="The text content for the first section.",
    )
    subtitle_2: str = Field(
        default="SECONDARY REFERENCE TITLE",
        description="The second subtitle.",
    )
    paragraph_2: str = Field(
        default="Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. They serve various purposes and are effective tools.",
        description="The text content for the second section.",
    )
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=800&auto=format&fit=crop",
        description="The URL for the image on the right half.",
    )

class GenerateIntroSlideInput(BaseModel):
    title: str = Field(
        default="Your Presentation Title",
        description="The main title of the presentation.",
    )
    subtitle: str = Field(
        default="Here is where your presentation begins",
        description="The subtitle displayed below the main title.",
    )
    background_color: str = Field(
        default="#F2F3EC",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#333333",
        description="Color of the main title text.",
    )
    subtitle_color: str = Field(
        default="#666666",
        description="Color of the subtitle text.",
    )

class GenerateWarmIntroSlideInput(BaseModel):
    """Input schema for generate_warm_intro_slide_xml."""

    title: str = Field(
        ...,
        description="Main slide title. example: 'Intro Template'",
    )
    subtitle: str = Field(
        ...,
        description="Subtitle or short description below the main title. example: 'Choose a topic and audience to generate a tailored introductory presentation'",
    )
    background_color: str = Field(
        default="#F2E6DF",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#5C4640",
        description="Color of the main title text.",
    )
    subtitle_color: str = Field(
        default="#A0716A",
        description="Color of the subtitle text.",
    )

class GenerateCreativeTeamSlideInput(BaseModel):
    """Input schema for generate_creative_team_slide_xml."""

    title: str = Field(
        default="Our Creative Team",
        description="Main slide title.",
    )
    members: list[dict] = Field(
        default=None,
        description="List of team members. Each dictionary should have 'name', 'role', and 'image_url'. Maximum 4 members.",
    )
    background_color: str = Field(
        default="#FAFAFA",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#4A4036",
        description="Color of the main title text.",
    )

class GenerateGridTeamSlideInput(BaseModel):
    """Input schema for generate_grid_team_slide_xml."""

    title: str = Field(
        default="Add a Team\nMembers\nPage",
        description="Main slide title.",
    )
    members: list[dict] = Field(
        default=None,
        description="List of team members. Each dictionary should have 'name', 'role', and 'image_url'. Maximum 4 members.",
    )
    background_color: str = Field(
        default="#F8FAFC",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#1A2530",
        description="Color of the main title text.",
    )


class GeneratePieChartSlideInput(BaseModel):
    title: str = Field(default="Budget Pie Chart")
    subtitle: str = Field(default="Monthly Budget")
    items: list[dict] = Field(description="List of dicts: [{'label': 'Savings', 'value': 24.8, 'description': 'desc'}, ...]")

class GenerateDonutChartSlideInput(BaseModel):
    title: str = Field(default="ELEGANCE CLASSY")
    subtitle: str = Field(default="Style Agency Infographics")
    items: list[dict] = Field(description="List of 3 dicts: [{'label': 'JUPITER', 'value': 75, 'description': 'desc'}, ...]")

# ==========================================================
# CÁC CÔNG CỤ (TOOLS) ĐƯỢC ĐĂNG KÝ VỚI AI
# ==========================================================
INTRO_TOOLS = [
    StructuredTool.from_function(
        func=generate_intro_slide_xml,
        name="generate_intro_slide_xml",
        description="Generates an introductory cover slide with an abstract SVG blob background, a large centered main title, and a subtitle below it. Ideal for the opening slide of a presentation, title covers, and introductions.",
        args_schema=GenerateIntroSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_warm_intro_slide_xml,
        name="generate_warm_intro_slide_xml",
        description="Generates an introductory cover slide with a warm-toned abstract watercolor SVG background and right-aligned text. Ideal for artistic, modern, and warm opening slides.",
        args_schema=GenerateWarmIntroSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_elegant_education_slide_xml,
        name="generate_elegant_education_slide_xml",
        description="Generates an elegant educational introductory slide with a white background, grey abstract shapes on the left, a hexagonal geometric pattern and a brown circle on the top right, and a brown bar along the bottom edge. Ideal for academic or professional education presentations.",
        args_schema=GenerateElegantEducationSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_online_notebook_slide_xml,
        name="generate_online_notebook_slide_xml",
        description="Generates an 'Online Notebook' introductory cover slide with a left-side diagonal blue area, a central white ticket badge containing the title, and decorative elements like an eraser, notebook paper, and pen. The title is split into two parts by a horizontal divider line. Ideal for education, training, or playful presentations.",
        args_schema=GenerateOnlineNotebookSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_notebook_section_slide_xml,
        name="generate_notebook_section_slide_xml",
        description="Generate a 'Back to School' notebook section slide. It has a grid background, large section number, handwritten title, and playful vector decorations like a balloon, backpack, autumn leaves, and crayons.",
        args_schema=GenerateNotebookSectionSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_science_2col_slide_xml,
        name="generate_science_2col_slide_xml",
        description="Generate a 2-column science/biology style slide with pale green background, hexagon patterns, and a molecule graphic. Good for comparisons or side-by-side content.",
        args_schema=GenerateScience2ColSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_thank_you_slide_xml,
        name="generate_thank_you_slide_xml",
        description="Generate a handwritten watercolor style 'Thank You' slide with a large cursive title, floating hearts, and a bouquet of daisies.",
        args_schema=GenerateThankYouSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_thank_you_watching_slide_xml,
        name="generate_thank_you_watching_slide_xml",
        description="Generate a boho/abstract 'Thank You for watching' slide with torn paper shapes, line-art branches, and 3D bold marker text.",
        args_schema=GenerateThankYouWatchingSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_about_me_slide_xml,
        name="generate_about_me_slide_xml",
        description="Generate a minimalist elegant 'About Me' slide with a left text area, organic wavy corner blobs, and an oval portrait frame.",
        args_schema=GenerateAboutMeSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_content_2col_slide_xml,
        name="generate_content_2col_slide_xml",
        description="Generate a clean 2-column content slide with a large title, accent line, two text sections on the left, and a full-height image on the right.",
        args_schema=GenerateContent2ColSlideInput,
    )
]
TRANSITION_TOOLS = [
    StructuredTool.from_function(
        func=generate_classic_toc_slide_xml,
        name="generate_classic_toc_slide_xml",
        description="Generates a classic vintage 'Table of contents' slide with a decorative border and a 2x3 grid for items. Ideal for historical, classic, or elegant presentations. Supports up to 6 items.",
        args_schema=GenerateClassicTocSlideInput,
    )
]
TEAM_TOOLS = [
    StructuredTool.from_function(
        func=generate_creative_team_slide_xml,
        name="generate_creative_team_slide_xml",
        description="Generates a team introduction slide with 4 polaroid-style photos rotated dynamically. Ideal for introducing key team members.",
        args_schema=GenerateCreativeTeamSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_grid_team_slide_xml,
        name="generate_grid_team_slide_xml",
        description="Generates a team members slide with a 2x2 grid layout on the right and a large title on the left. The photos are circular with colorful borders.",
        args_schema=GenerateGridTeamSlideInput,
    )
]
THANK_YOU_TOOLS = []

class GenerateAreaSlideInput(BaseModel):
    """Input for generating a area slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateColumnSlideInput(BaseModel):
    """Input for generating a column slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateComparisonSlideInput(BaseModel):
    """Input for generating a comparison slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateDarkBarSlideInput(BaseModel):
    """Input for generating a dark bar slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateDarkPieSlideInput(BaseModel):
    """Input for generating a dark pie slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateDashboardSlideInput(BaseModel):
    """Input for generating a dashboard slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateFinancialProjectionsSlideInput(BaseModel):
    """Input for generating a financial projections slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateImageBarSlideInput(BaseModel):
    """Input for generating a image bar slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateLineSlideInput(BaseModel):
    """Input for generating a line slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateMarketAnalysisSlideInput(BaseModel):
    """Input for generating a market analysis slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GeneratePeopleCultureSlideInput(BaseModel):
    """Input for generating a people culture slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateRadarSlideInput(BaseModel):
    """Input for generating a radar slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateStackedBarSlideInput(BaseModel):
    """Input for generating a stacked bar slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateWaterfallSlideInput(BaseModel):
    """Input for generating a waterfall slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")



class GenerateAiContentSlideInput(BaseModel):
    """Input for generating a ai content slide slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateKeyAdvantagesSlideInput(BaseModel):
    """Input for generating a key advantages slide slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")


class GenerateSimpleDonutSlideInput(BaseModel):
    """Input for generating a simple donut slide."""
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    items: List[Dict[str, Any]] = Field(default=[], description="List of data items for the chart")








CHART_TOOLS = [
    StructuredTool.from_function(
        func=generate_pie_chart_slide_xml,
        name="generate_pie_chart_slide_xml",
        description="Generates a pie chart slide with a legend on the left.",
        args_schema=GeneratePieChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_donut_chart_slide_xml,
        name="generate_donut_chart_slide_xml",
        description="Generates a 3-donut chart slide horizontally aligned.",
        args_schema=GenerateDonutChartSlideInput,
    )
,

    StructuredTool.from_function(
        func=xml_tool.generate_area_slide_xml,
        name="generate_area_slide_xml",
        description="Generate a area slide.",
        args_schema=GenerateAreaSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_column_slide_xml,
        name="generate_column_slide_xml",
        description="Generate a column slide.",
        args_schema=GenerateColumnSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_comparison_slide_xml,
        name="generate_comparison_slide_xml",
        description="Generate a comparison slide.",
        args_schema=GenerateComparisonSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_dark_bar_slide_xml,
        name="generate_dark_bar_slide_xml",
        description="Generate a dark bar slide.",
        args_schema=GenerateDarkBarSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_dark_pie_slide_xml,
        name="generate_dark_pie_slide_xml",
        description="Generate a dark pie slide.",
        args_schema=GenerateDarkPieSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_dashboard_slide_xml,
        name="generate_dashboard_slide_xml",
        description="Generate a dashboard slide.",
        args_schema=GenerateDashboardSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_financial_projections_slide_xml,
        name="generate_financial_projections_slide_xml",
        description="Generate a financial projections slide.",
        args_schema=GenerateFinancialProjectionsSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_image_bar_slide_xml,
        name="generate_image_bar_slide_xml",
        description="Generate a image bar slide.",
        args_schema=GenerateImageBarSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_line_slide_xml,
        name="generate_line_slide_xml",
        description="Generate a line slide.",
        args_schema=GenerateLineSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_market_analysis_slide_xml,
        name="generate_market_analysis_slide_xml",
        description="Generate a market analysis slide.",
        args_schema=GenerateMarketAnalysisSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_people_culture_slide_xml,
        name="generate_people_culture_slide_xml",
        description="Generate a people culture slide.",
        args_schema=GeneratePeopleCultureSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_radar_slide_xml,
        name="generate_radar_slide_xml",
        description="Generate a radar slide.",
        args_schema=GenerateRadarSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_stacked_bar_slide_xml,
        name="generate_stacked_bar_slide_xml",
        description="Generate a stacked bar slide.",
        args_schema=GenerateStackedBarSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_waterfall_slide_xml,
        name="generate_waterfall_slide_xml",
        description="Generate a waterfall slide.",
        args_schema=GenerateWaterfallSlideInput,
    )
,

    StructuredTool.from_function(
        func=xml_tool.generate_ai_content_slide_slide_xml,
        name="generate_ai_content_slide_slide_xml",
        description="Generate a ai content slide slide.",
        args_schema=GenerateAiContentSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_key_advantages_slide_slide_xml,
        name="generate_key_advantages_slide_slide_xml",
        description="Generate a key advantages slide slide.",
        args_schema=GenerateKeyAdvantagesSlideInput,
    ),

    StructuredTool.from_function(
        func=xml_tool.generate_simple_donut_slide_xml,
        name="generate_simple_donut_slide_xml",
        description="Generate a simple donut slide.",
        args_schema=GenerateSimpleDonutSlideInput,
    )
]


class MemphisFeature(BaseModel):
    title: str
    desc: str

class TimelineEvent(BaseModel):
    year: str
    desc: str

class TeamMember(BaseModel):
    name: str
    role: str

ALL_TOOLS = INTRO_TOOLS + TRANSITION_TOOLS + TEAM_TOOLS + THANK_YOU_TOOLS + CHART_TOOLS

TOOLS_DICT = {'INTRO_TOOLS': INTRO_TOOLS,
               'TRANSITION_TOOLS': TRANSITION_TOOLS,
               'TEAM_TOOLS': TEAM_TOOLS,
               'THANK_YOU_TOOLS': THANK_YOU_TOOLS,
                'CHART_TOOLS': CHART_TOOLS
               }

# Tool utilities
TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}

def get_all_tool_names():
    """Return list of all available tool names."""
    return list(TOOL_MAP.keys())

def get_tool_by_name(name: str):
    """Get a specific tool by name."""
    return TOOL_MAP.get(name)

def execute_tool(tool_call: dict):
    """Execute a tool call with the provided arguments."""
    name = tool_call.get("name")
    args = tool_call.get("arguments", {})
    
    if name in TOOL_MAP:
        try:
            result = TOOL_MAP[name].invoke(args)
            return str(result)
        except Exception as e:
            print(f"Error executing tool '{name}': {e}")
            return None
        print(f"Tool '{name}' not found.")
        return None




def execute_tool_plan(tool_calls: list, tool_lookup: dict = None) -> tuple:
    """
    Execute one generator response: HTML slide tool FIRST, then Search 1..N.

    No LLM is invoked here. Search results are connected to HTML image
    parameters deterministically by schema/runtime declaration order.
    Returns (html_output, final_html_tool_call, search_history).
    """
    from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
        execute_image_search_plan,
    )

    if tool_lookup is None:
        tool_lookup = {t.name: t for tools in TOOLS_DICT.values() for t in tools}

    print(
        "\n🚀 [EXECUTE TOOL PLAN] Raw ordered calls:\n"
        f"{json.dumps(tool_calls, indent=2, ensure_ascii=False)}"
    )
    final_tool_call, search_history = execute_image_search_plan(
        tool_calls=tool_calls,
        tool_lookup=tool_lookup,
    )
    tool_name = final_tool_call.get("name", "unknown_tool")
    original_html_call = tool_calls[0]   # bản gốc từ LLM (image_url = "") — HTML tool FIRST
    search_calls = tool_calls[1:]        # search_ddgs_images calls từ LLM — AFTER

    # Build execution matrix theo cấu trúc training: tool_call trước, image_tool_call_N sau
    execution_matrix: dict = {"tool_call": original_html_call}
    for i, call in enumerate(search_calls, start=1):
        result_url = search_history[i - 1].get("result_url", "") if i - 1 < len(search_history) else ""
        execution_matrix[f"image_tool_call_{i}"] = {
            **call,
            "result_url": result_url,   # URL thực đã tìm được (chỉ để log, không lưu dataset)
        }

    print(
        "  📦 [PIPELINE TOOL CALL EXECUTION MATRIX]:\n"
        f"{json.dumps(execution_matrix, indent=2, ensure_ascii=False)}"
    )

    print(f"  🎨 [RENDER HTML] Executing tool '{tool_name}' to generate slide HTML...")
    html_out = execute_tool(final_tool_call)
    if html_out:
        print(f"  ✅ [SUCCESS] Tool '{tool_name}' rendered HTML successfully ({len(html_out)} bytes).")
    else:
        print(f"  ❌ [ERROR] Tool '{tool_name}' failed to render HTML.")
    return html_out, final_tool_call, search_history



TOOLS_DICT = {tool.name: tool for tool in ALL_TOOLS}
