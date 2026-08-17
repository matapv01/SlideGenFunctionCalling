from backend.workflows.slidegen_workflow.tools import xml_tool
# Auto-generated from tools.py preserving all original parameter schemas
# This conversion maintains the exact parameter definitions from the source

import json

from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


# Import all slide generation functions from xml_tool

from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_business_proposal_cover_slide_xml,

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
class GenerateTechPitchDeckThankYouInput(BaseModel):
    company_name: str = Field(default="Arowwai\nIndustries", description="Company name shown on top left.")
    title: str = Field(default="THANK YOU!", description="Main title.")
    name: str = Field(default="Aaron Loeb", description="Name of the contact person.")
    role: str = Field(default="CEO & Founder", description="Role of the contact person.")
    phone: str = Field(default="+123-456-7890", description="Phone number.")
    website: str = Field(default="www.reallygreatsite.com", description="Website URL.")
    address: str = Field(default="123 Anywhere St., Any City, State,\nCountry 12345", description="Address.")
    profile_image_url: str = Field(default="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=500&h=500&fit=crop", description="URL for the profile image.")

class GenerateThynkUnlimitedThankYouInput(BaseModel):
    company_name: str = Field(default="Thynk Unlimited", description="Company name shown on top left.")
    title: str = Field(default="THANK YOU", description="Main title.")
    subtitle: str = Field(default="FOR YOUR ATTENTION", description="Subtitle.")
    date: str = Field(default="December 2023", description="Date pill text.")
    email: str = Field(default="hello@reallygreatsite.com", description="Contact email.")
    website: str = Field(default="www.reallygreatsite.com", description="Website URL.")
    image_url: str = Field(default="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?q=80&w=800&auto=format&fit=crop", description="URL for the right side image.")


class GenerateBusinessProposalCoverInput(BaseModel):
    brand_name: str = Field(default="Larana, Inc.", description="Brand name.")
    title: str = Field(default="BUSINESS PROPOSAL", description="Main title.")
    website: str = Field(default="www.reallygreatsite.com", description="Website URL.")
    email: str = Field(default="hello@reallygreatsite.com", description="Email address.")
    image1_url: str = Field(default="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab", description="Image 1 URL.")
    image2_url: str = Field(default="https://images.unsplash.com/photo-1577017040065-650ee4d43339", description="Image 2 URL.")
    image3_url: str = Field(default="https://images.unsplash.com/photo-1460472178825-e5240623afd5", description="Image 3 URL.")

class GenerateImageAndNumberedListSlideInput(BaseModel):
    title: str = Field(default="The Polar Climate and\nIts Extremes", description="Main title.")
    image_url: str = Field(default="https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=800&auto=format&fit=crop", description="URL for the image.")
    item1_number: str = Field(default="01", description="Number for item 1.")
    item1_title: str = Field(default="Endless Cold", description="Title for item 1.")
    item1_desc: str = Field(default="Temperatures drop far below zero for months, testing both human and wildlife adaptation to freezing conditions", description="Description for item 1.")
    item2_number: str = Field(default="02", description="Number for item 2.")
    item2_title: str = Field(default="Midnight Sun &amp; Polar Night", description="Title for item 2.")
    item2_desc: str = Field(default="The Arctic experiences months of sunlight and darkness, shaping unique biological and cultural rhythms", description="Description for item 2.")
    item3_number: str = Field(default="03", description="Number for item 3.")
    item3_title: str = Field(default="Adapting to Extremes", description="Title for item 3.")
    item3_desc: str = Field(default="Animals like polar bears and arctic foxes have evolved to thrive in this challenging, ever-changing climate", description="Description for item 3.")

class GenerateTechPitchDeckCoverSlideInput(BaseModel):
    company_name: str = Field(default="Arowwai\nIndustries", description="Company name.")
    title: str = Field(default="Technology\nPitch Deck", description="Main title.")
    subtitle: str = Field(default="By: Alexander Aronowitz", description="Subtitle.")
    image_url: str = Field(default="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=800&auto=format&fit=crop", description="URL for the cover image.")

INTRO_TOOLS = [
     StructuredTool.from_function(
        func=xml_tool.generate_image_and_numbered_list_slide_xml,
        name="generate_image_and_numbered_list_slide_xml",
        description="Generate an image and numbered list slide with an image on the left and 3 numbered points on the right.",
        args_schema=GenerateImageAndNumberedListSlideInput,
    ),
    StructuredTool.from_function(
        func=xml_tool.generate_tech_pitch_deck_cover_slide_xml,
        name="generate_tech_pitch_deck_cover_slide_xml",
        description="Generates a tech pitch deck cover slide with a large image and partial circle decor.",
        args_schema=GenerateTechPitchDeckCoverSlideInput,
    ),
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
    ),



    StructuredTool.from_function(
        func=generate_business_proposal_cover_slide_xml,
        name="generate_business_proposal_cover_slide_xml",
        description="Generates a business proposal cover slide with 3 diamond images.",
        args_schema=GenerateBusinessProposalCoverInput,
    ),
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




THANK_YOU_TOOLS = [
    StructuredTool.from_function(
        func=xml_tool.generate_tech_pitch_deck_thank_you_slide_xml,
        name="generate_tech_pitch_deck_thank_you_slide_xml",
        description="Generates a tech pitch deck thank you slide with contact information and a right-side image.",
        args_schema=GenerateTechPitchDeckThankYouInput,
    ),
    StructuredTool.from_function(
        func=xml_tool.generate_thynk_unlimited_thank_you_slide_xml,
        name="generate_thynk_unlimited_thank_you_slide_xml",
        description="Generates a thank you slide for Thynk Unlimited theme.",
        args_schema=GenerateThynkUnlimitedThankYouInput,
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
]

class GenerateAreaSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    data1_label: str = Field(default="Data 1", description="Text label for data1_label")
    data2_label: str = Field(default="Data 2", description="Text label for data2_label")
    data3_label: str = Field(default="Data 3", description="Text label for data3_label")
    data4_label: str = Field(default="Data 4", description="Text label for data4_label")
    data5_label: str = Field(default="Data 5", description="Text label for data5_label")
    data6_label: str = Field(default="Data 6", description="Text label for data6_label")


class GenerateColumnSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    item1_label: str = Field(default="Thailand", description="Text label for item1_label")
    item2_label: str = Field(default="Philippines", description="Text label for item2_label")
    item3_label: str = Field(default="Ethiopia", description="Text label for item3_label")
    item4_label: str = Field(default="Columbia", description="Text label for item4_label")
    item5_label: str = Field(default="Australia", description="Text label for item5_label")
    item6_label: str = Field(default="Vietnam", description="Text label for item6_label")
    item7_label: str = Field(default="Brazil", description="Text label for item7_label")


class GenerateComparisonSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    metric1_label: str = Field(default="Email Marketing", description="Text label for metric1_label")
    metric2_label: str = Field(default="SEO", description="Text label for metric2_label")
    metric1_value: str = Field(default="28%", description="Text label for metric1_value")
    metric2_value: str = Field(default="72%", description="Text label for metric2_value")


class GenerateDarkBarSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    market1_label: str = Field(default="Market 1", description="Text label for market1_label")
    market2_label: str = Field(default="Market 2", description="Text label for market2_label")
    trend1_label: str = Field(default="Trend 1", description="Text label for trend1_label")
    trend2_label: str = Field(default="Trend 2", description="Text label for trend2_label")
    trend3_label: str = Field(default="Trend 3", description="Text label for trend3_label")


class GenerateDarkPieSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    slice1_label: str = Field(default="Growth 1", description="Text label for slice1_label")
    slice1_value: str = Field(default="12.5%", description="Text label for slice1_value")
    slice2_label: str = Field(default="Growth 2", description="Text label for slice2_label")
    slice2_value: str = Field(default="25%", description="Text label for slice2_value")
    slice3_label: str = Field(default="Growth 3", description="Text label for slice3_label")
    slice3_value: str = Field(default="62.5%", description="Text label for slice3_value")


class GenerateDashboardSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    metric1_label: str = Field(default="Annual Revenue Target", description="Text label for metric1_label")
    metric1_value: str = Field(default="", description="Text label for metric1_value")
    metric2_label: str = Field(default="Current YTD (Q3)", description="Text label for metric2_label")
    metric2_value: str = Field(default=".7M", description="Text label for metric2_value")
    metric3_label: str = Field(default="Forecast Q4", description="Text label for metric3_label")
    metric3_value: str = Field(default="+5-7%", description="Text label for metric3_value")
    highlight_text: str = Field(default="Projected to exceed target", description="Text label for highlight_text")


class GenerateFinancialProjectionsSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    title_word1: str = Field(default="Financial", description="Text label for title_word1")
    title_word2: str = Field(default="Projections", description="Text label for title_word2")
    item1_label: str = Field(default="Item 1", description="Text label for item1_label")
    item1_value: str = Field(default="62.5%", description="Text label for item1_value")
    item2_label: str = Field(default="Item 2", description="Text label for item2_label")
    item2_value: str = Field(default="25%", description="Text label for item2_value")
    item3_label: str = Field(default="Item 3", description="Text label for item3_label")
    item3_value: str = Field(default="12.5%", description="Text label for item3_value")


class GenerateImageBarSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    image1_url: str = Field(default="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format", description="Image URL")


class GenerateLineSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    series1_label: str = Field(default="Production", description="Text label for series1_label")
    series2_label: str = Field(default="Sale", description="Text label for series2_label")
    series3_label: str = Field(default="Marketing", description="Text label for series3_label")
    month1_label: str = Field(default="January", description="Text label for month1_label")
    month2_label: str = Field(default="February", description="Text label for month2_label")
    month3_label: str = Field(default="March", description="Text label for month3_label")
    month4_label: str = Field(default="April", description="Text label for month4_label")
    month5_label: str = Field(default="May", description="Text label for month5_label")
    month6_label: str = Field(default="June", description="Text label for month6_label")


class GenerateMarketAnalysisSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    title_word1: str = Field(default="Market", description="Text label for title_word1")
    title_word2: str = Field(default="Analysis", description="Text label for title_word2")
    cat1_label: str = Field(default="Item 1", description="Text label for cat1_label")
    cat2_label: str = Field(default="Item 2", description="Text label for cat2_label")
    cat3_label: str = Field(default="Item 3", description="Text label for cat3_label")
    cat4_label: str = Field(default="Item 4", description="Text label for cat4_label")
    cat5_label: str = Field(default="Item 5", description="Text label for cat5_label")
    series1_label: str = Field(default="Series 1", description="Text label for series1_label")
    series2_label: str = Field(default="Series 2", description="Text label for series2_label")
    series3_label: str = Field(default="Series 3", description="Text label for series3_label")


class GeneratePeopleCultureSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    metric1_label: str = Field(default="Employee Engagement", description="Text label for metric1_label")
    metric1_value: str = Field(default="89%", description="Text label for metric1_value")
    metric2_label: str = Field(default="Average Training Hours", description="Text label for metric2_label")
    metric2_value: str = Field(default="37 hrs", description="Text label for metric2_value")
    metric3_label_part1: str = Field(default="Women in", description="Text label for metric3_label_part1")
    metric3_label_part2: str = Field(default="Leadership", description="Text label for metric3_label_part2")
    metric3_value: str = Field(default="50%", description="Text label for metric3_value")
    m1: str = Field(default="Jan", description="Text label for m1")
    m2: str = Field(default="Feb", description="Text label for m2")
    m3: str = Field(default="Mar", description="Text label for m3")
    m4: str = Field(default="Apr", description="Text label for m4")
    m5: str = Field(default="May", description="Text label for m5")
    m6: str = Field(default="Jun", description="Text label for m6")
    m7: str = Field(default="Jul", description="Text label for m7")
    m8: str = Field(default="Aug", description="Text label for m8")
    m9: str = Field(default="Sep", description="Text label for m9")
    m10: str = Field(default="Oct", description="Text label for m10")


class GenerateRadarSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    radar_label2: str = Field(default="S?c m?nh", description="Text label for radar_label2")
    radar_label5: str = Field(default="IQ", description="Text label for radar_label5")


class GenerateStackedBarSlideInput(BaseModel):
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    series1_label: str = Field(default="Seri 1", description="Text label for series1_label")
    series2_label: str = Field(default="Seri 2", description="Text label for series2_label")
    series3_label: str = Field(default="Seri 3", description="Text label for series3_label")
    y_axis_20: str = Field(default="20%", description="Text label for y_axis_20")
    y_axis_40: str = Field(default="40%", description="Text label for y_axis_40")
    y_axis_60: str = Field(default="60%", description="Text label for y_axis_60")
    y_axis_80: str = Field(default="80%", description="Text label for y_axis_80")
    y_axis_100: str = Field(default="100%", description="Text label for y_axis_100")
    item1_label: str = Field(default="Item 1", description="Text label for item1_label")
    item2_label: str = Field(default="Item 2", description="Text label for item2_label")
    item3_label: str = Field(default="Item 3", description="Text label for item3_label")
    item4_label: str = Field(default="Item 4", description="Text label for item4_label")


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
    title: str = Field(default="Default Title", description="The title of the slide")
    subtitle: str = Field(default="Default Subtitle", description="The subtitle of the slide")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the main title text.")
    subtitle_color: str = Field(default="#666666", description="Color of the subtitle text.")
    slice1_value: str = Field(default="11%", description="Text label for slice1_value")
    slice2_value: str = Field(default="28%", description="Text label for slice2_value")
    slice3_value: str = Field(default="22%", description="Text label for slice3_value")
    slice4_value: str = Field(default="23%", description="Text label for slice4_value")
    slice5_value: str = Field(default="16%", description="Text label for slice5_value")








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

    image_url: str = Field(default="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=800&auto=format&fit=crop", description="URL for the large image on the right.")

