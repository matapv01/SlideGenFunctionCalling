# Auto-generated from tools.py preserving all original parameter schemas
# This conversion maintains the exact parameter definitions from the source

import json

from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


# Import all slide generation functions from xml_tool
from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_three_ideas_slide_xml,
    generate_content_creation_slide_xml,
    generate_ai_content_slide_xml,
    generate_two_ideas_slide_xml,
    generate_our_history_slide_xml,
)

# ===========================================================================================
# PYDANTIC INPUT SCHEMAS ORDERED ACCORDING TO IMPORT SEQUENCE
# ===========================================================================================

# === SLIDE INTRO CLASSES ===

class GenerateContentCreationSlideInput(BaseModel):
    """Input schema for generate_content_creation_slide_xml."""

    main_title: str = Field(
        ...,
        description="Main slide title shown on the upper-right area. example: 'CONTENT CREATION'",
    )
    original_title: str = Field(
        ...,
        description="Heading for the first content block. example: 'Original Content'",
    )
    original_description: str = Field(
        ...,
        description="Description text for the original content block. example: 'Develop unique visuals, videos, and copy that align with your brand's message and resonate with your audience's interests. Create content that not only captures attention but also conveys the essence of your brand.'",
    )
    curated_title: str = Field(
        ...,
        description="Heading for the second content block.  example: 'Curated Content'",
    )
    curated_description: str = Field(
        ...,
        description="Description text for the curated content block. example: 'Share valuable curated content from reputable sources in your industry such as articles, videos, and graphics to enhance your original material and engage your audience in discussions.'"
    )
    main_image_url: str = Field(
        default="https://images.unsplash.com/photo-1625064757761-c9bccabf1163?auto=format&fit=crop&q=80&w=1800",
        description="URL for the large landscape image on the left.",
    )
    portrait_image_url: str = Field(
        default="https://images.unsplash.com/photo-1552113125-81af17f36b57?auto=format&fit=crop&q=80&w=1000",
        description="URL for the portrait image on the right.",
    )
    background_color: str = Field(
        default="#D2DADE",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#68767C",
        description="Color of the main title text.",
    )
    accent_color: str = Field(
        default="#E4AAA2",
        description="Accent color for the rounded rectangle behind the portrait.",
    )
    decoration_color: str = Field(
        default="#AEB9BE",
        description="Color of the decorative ellipse and bars.",
    )
    text_color: str = Field(
        default="#111111",
        description="Color of the body text and section titles.",
    )


class GenerateAiContentSlideInput(BaseModel):
    """Input schema for generate_ai_content_slide_xml."""

    title: str = Field(
        ...,
        description="Main title text displayed at the top-left of the slide. example: 'THE SLIDE TITLE GOES HERE'",
    )
    intro_text: str = Field(
        ...,
        description="Introductory paragraph displayed under the title. example: 'Do you know what helps you make your point clear? Lists like this one:'",
    )
    bullet_items: List[str] = Field(
        ...,
        description="List of bullet points displayed in the body area. example: ['They are simple', 'You can organize your ideas clearly', 'You will never forget to buy milk!']",
    )
    footer_text: str = Field(
        ...,
        description="Footer note displayed below the bullet list. example: 'You can replace the image. Just right-click on it and select \"Replace image\"'",
    )
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=85&w=1400&auto=format&fit=crop",
        description="URL for the image displayed on the right side.",
    )
    background_color: str = Field(
        default="#E3EAED",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#101010",
        description="Color of the main title text.",
    )
    text_color: str = Field(
        default="#1B1B1B",
        description="Color of the intro, bullet, and footer text.",
    )


class GenerateTwoIdeasSlideInput(BaseModel):
    """Input schema for generate_two_ideas_slide_xml."""

    title: str = Field(
        ...,
        description="Main title text displayed in the content area. example: 'TWO IDEAS'",
    )
    idea_titles: List[str] = Field(
        ...,
        description="List of idea headings. Must have the same length as idea_descriptions. example: ['Venus', 'Mercury']",
    )
    idea_descriptions: List[str] = Field(
        ...,
        description="List of supporting descriptions for each idea title. example: ['Venus is the second planet from the Sun.', 'Mercury is the closest planet to the Sun.']",
    )
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1529139574466-a303027c1d8b?q=85&w=1200&auto=format&fit=crop",
        description="URL for the full-height image panel on the left side.",
    )
    background_color: str = Field(
        default="#1A1A1A",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#FFFFFF",
        description="Color of the main title text.",
    )
    heading_color: str = Field(
        default="#FFFFFF",
        description="Color of each idea heading.",
    )
    body_color: str = Field(
        default="#F1F1F1",
        description="Color of each idea description.",
    )



class GenerateThreeIdeasSlideInput(BaseModel):
    """Input schema for generate_three_ideas_slide_xml."""
    title: str = Field(
        ...,
        description="Main title text displayed at the top of the slide. example: 'THREE IDEAS' ",
    )
    idea_titles: List[str] = Field(
        ... ,
        description="List of idea headings. Must have the same length as idea_descriptions. example: ['Mercury', 'Mars', 'Venus']",
    )
    idea_descriptions: List[str] = Field(
        ...,
        description="List of supporting descriptions for each idea title. example: ['Mercury is the closest planet to the Sun.', 'Mars is known as the Red Planet.', 'Venus has a thick, toxic atmosphere.']",
    )
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1594035910387-fea47794261f?q=85&w=1200&auto=format&fit=crop",
        description="URL for the full-height image panel on the right side.",
    )
    background_color: str = Field(
        default="#181818",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#FFFFFF",
        description="Color of the main title text.",
    )
    heading_color: str = Field(
        default="#FFFFFF",
        description="Color of each idea heading.",
    )
    body_color: str = Field(
        default="#F2F2F2",
        description="Color of each idea description.",
    )

class GenerateOurHistorySlideInput(BaseModel):
    """Input schema for generate_our_history_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top of the content area. example: 'OUR HISTORY'")
    event_titles: List[str] = Field(..., description="List of event headings displayed in vertically stacked history sections. Must have the same length as event_descriptions and event_years. example: ['SATURN', 'MARS', 'NEPTUNE']")
    event_descriptions: List[str] = Field(..., description="List of supporting descriptions for each history event. Must have the same length as event_titles and event_years. example: ['Saturn is composed of hydrogen and helium.', 'Despite being red, Mars is actually a cold place.', 'Neptune is the farthest planet from the Sun.']")
    event_years: List[str] = Field(..., description="List of year or timeline labels displayed beside each history event. Must have the same length as event_titles and event_descriptions. example: ['1998', '2005', '2024']")
    image_url: str = Field(default="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=85&w=1200&auto=format&fit=crop", description="URL for the full-height image panel displayed on the right side.")
    background_color: str = Field(default="#151515", description="Background color of the slide.")
    title_color: str = Field(default="#FFFFFF", description="Color of the main title text.")
    heading_color: str = Field(default="#FFFFFF", description="Color of each event heading.")
    body_color: str = Field(default="#F2F2F2", description="Color of each event description.")
    year_color: str = Field(default="#FFFFFF", description="Color of each year or timeline label.")
    line_color: str = Field(default="#E8E8E8", description="Color of the vertical timeline separator lines.")

CONTENT_TOOLS = [
    # === XML CONTENT SLIDES ===
    StructuredTool.from_function(
        func=generate_content_creation_slide_xml,
        name="generate_content_creation_slide_xml",
        description="""Generates a content-creation slide with a large image on the left, a portrait image on the right, and two text content blocks for original content and curated content. Ideal for marketing, editorial, brand storytelling, and content strategy presentations.""",
        args_schema=GenerateContentCreationSlideInput
    ),
    StructuredTool.from_function(
        func=generate_ai_content_slide_xml,
        name="generate_ai_content_slide_xml",
        description="""Generates a flexible AI/content slide with a large title, intro text, bullet list, footer note, and a right-side image panel. Ideal for explaining a concept, feature list, process notes, or educational content.""",
        args_schema=GenerateAiContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_two_ideas_slide_xml,
        name="generate_two_ideas_slide_xml",
        description="""Generates a two-ideas slide with a full-height image panel on the left and a dark content area on the right containing a title, two idea headings, and supporting descriptions. Ideal for comparing two concepts or presenting two key points.""",
        args_schema=GenerateTwoIdeasSlideInput
    ),
    StructuredTool.from_function(
        func=generate_three_ideas_slide_xml,
        name="generate_three_ideas_slide_xml",
        description="""Generates a split-layout three-ideas slide with a dark content area, a large title, three idea headings, three supporting descriptions, and a full-height image panel on the right. Ideal for explaining three concepts, comparisons, highlights, or key points.""",
        args_schema=GenerateThreeIdeasSlideInput
    ),
    StructuredTool.from_function(
    func=generate_our_history_slide_xml,
    name="generate_our_history_slide_xml",
    description="Generates a split-layout history slide with a dark content area on the left and a full-height image panel on the right. The content area contains a large title and multiple vertically stacked history events, with right-aligned headings and descriptions, year markers, and vertical separator lines. Ideal for company histories, project milestones, product evolution, timelines, and organizational growth.",
    args_schema=GenerateOurHistorySlideInput,
    ),
    
]

# All available slide generation tools with complete parameter schemas
INTRO_TOOLS = []
TRANSITION_TOOLS = []
TEAM_TOOLS = []
THANK_YOU_TOOLS = []
CHART_TOOLS = []

ALL_TOOLS = INTRO_TOOLS + TRANSITION_TOOLS + CONTENT_TOOLS + TEAM_TOOLS + THANK_YOU_TOOLS + CHART_TOOLS

TOOLS_DICT = {'INTRO_TOOLS': INTRO_TOOLS,
               'TRANSITION_TOOLS': TRANSITION_TOOLS,
               'CONTENT_TOOLS': CONTENT_TOOLS,
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
