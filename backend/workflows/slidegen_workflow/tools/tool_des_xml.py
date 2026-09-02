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
    generate_donut_chart_slide_xml,
    # Dynamic chart functions
    generate_bar_chart_slide_xml,
    generate_horizontal_bar_chart_slide_xml,
    generate_line_chart_slide_xml,
    generate_scatter_chart_slide_xml,
    generate_stacked_bar_chart_slide_xml,
    generate_waterfall_chart_slide_xml,
    generate_radar_chart_slide_xml,
    generate_area_chart_slide_xml,
    generate_simple_donut_chart_slide_xml,
    generate_outlook_dashboard_slide_xml,
    generate_performance_review_slide_xml,
    generate_kpi_dashboard_slide_xml,
    generate_revenue_target_slide_xml,
    generate_modern_donut_chart_slide_xml,
    generate_analysis_story_slide_xml,
    generate_dark_multi_line_chart_slide_xml,
    generate_line_chart_report_slide_xml,
    generate_modern_pie_chart_slide_xml,
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
    """Input for pie chart slide with colored slices and a left-side legend panel."""
    title: str = Field(
        default="Budget Pie Chart",
        description="Main title displayed in a colored header banner at the top. Example: 'Revenue Distribution', 'Market Share 2024'.",
    )
    subtitle: str = Field(
        default="Monthly Budget",
        description="Subtitle displayed in the header banner below the title. Example: 'Q4 Financial Overview'.",
    )
    items: List[Dict[str, Any]] = Field(
        default=[
            {"label": "Savings", "value": 24.8, "description": "Monthly savings allocation"},
            {"label": "Rent", "value": 35.0, "description": "Housing and rent expenses"},
            {"label": "Food", "value": 20.2, "description": "Groceries and dining"},
            {"label": "Transport", "value": 12.0, "description": "Commuting costs"},
            {"label": "Others", "value": 8.0, "description": "Miscellaneous spending"},
        ],
        description="List of pie slices. Each dict has 'label' (str, category name), 'value' (number, raw value — percentages are auto-calculated), and 'description' (str, short explanation shown in legend). Maximum 6 items. Example: [{'label': 'Marketing', 'value': 35, 'description': 'Digital and offline campaigns'}]",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional list of hex colors for each slice. Default uses an earthy green-beige palette. Example: ['#354F42', '#556B55', '#89947A']",
    )
    background_color: str = Field(default="#FAF7F0", description="Background color of the slide (warm off-white by default).")
    title_color: str = Field(default="#FFFFFF", description="Color of the title text (displayed on the header banner).")
    subtitle_color: str = Field(default="#B6AE97", description="Color of the subtitle text.")
    header_color: str = Field(default="#354F42", description="Background color of the top header banner.")
    legend_bg_color: str = Field(default="#2F2E2C", description="Background color of the left legend panel.")

class GenerateDonutChartSlideInput(BaseModel):
    """Input for 3 horizontal donut progress charts with labels and descriptions below."""
    title: str = Field(
        default="ELEGANCE CLASSY",
        description="Main title displayed in large bold text at the top left. Example: 'Project Progress', 'Performance Metrics'.",
    )
    subtitle: str = Field(
        default="Style Agency Infographics",
        description="Subtitle displayed below the title. Example: 'Q3 Department KPIs'.",
    )
    items: List[Dict[str, Any]] = Field(
        default=[
            {"label": "JUPITER", "value": 75, "description": "Jupiter is the largest planet in the solar system"},
            {"label": "SATURN", "value": 60, "description": "Saturn is known for its beautiful ring system"},
            {"label": "MARS", "value": 45, "description": "Mars is often called the Red Planet"},
        ],
        description="Exactly 3 donut items. Each dict has 'label' (str, shown below the donut), 'value' (number 0-100, percentage filled), and 'description' (str, explanation text below label). Example: [{'label': 'Design', 'value': 85, 'description': 'UI/UX completion rate'}]",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional list of hex colors for each donut foreground arc. Example: ['#CDAE9B', '#A0C4A8', '#8BAFD4']",
    )
    background_color: str = Field(default="#FCFBF9", description="Background color of the slide.")
    title_color: str = Field(default="#333230", description="Color of the title and percentage text.")
    subtitle_color: str = Field(default="#8C8984", description="Color of the subtitle and description text.")
    accent_color: str = Field(default="#9E8470", description="Color of the left decorative bar.")
    donut_bg_color: str = Field(default="#6E7266", description="Background ring color of each donut.")
    donut_fg_color: str = Field(default="#CDAE9B", description="Default foreground arc color (used when colors is not provided).")

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

# ===========================================================================================
# DYNAMIC CHART INPUT SCHEMAS — LLM truyền dữ liệu thực (categories, series, items)
# ===========================================================================================

class GenerateBarChartSlideInput(BaseModel):
    """Input for vertical bar chart slide with white background, gridlines, and grouped bars."""
    title: str = Field(default="Quarterly Performance", description="Main title displayed at the top left in large bold text. Example: 'Sales Performance 2024', 'Department Budget Comparison'.")
    subtitle: str = Field(default="Performance metrics overview", description="Subtitle below the title in smaller gray text. Example: 'Year-over-year revenue analysis'.")
    categories: List[str] = Field(
        default=["Q1", "Q2", "Q3", "Q4"],
        description="Category labels along the X axis (bottom). Each category gets one group of bars. Example: ['Q1', 'Q2', 'Q3', 'Q4'] or ['Jan', 'Feb', 'Mar'].",
    )
    series: List[Dict[str, Any]] = Field(
        default=[{"name": "Revenue", "data": [45, 52, 68, 58]}],
        description="Data series for the chart. Each dict has 'name' (legend label) and 'data' (list of numbers, one per category). Multiple series create grouped/clustered bars. Example: [{'name': 'Revenue', 'data': [45, 52, 68, 58]}, {'name': 'Cost', 'data': [30, 28, 42, 35]}].",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional hex colors for each series. Defaults to navy-orange palette. Example: ['#1B2559', '#FF6B35'].",
    )
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#1B2559", description="Color of the title text and category labels.")
    subtitle_color: str = Field(default="#6B7280", description="Color of the subtitle text.")
    y_axis_label: str = Field(default="Value", description="Label for the Y axis (rotated vertically on the left).")


class GenerateHorizontalBarChartSlideInput(BaseModel):
    """Input for horizontal bar chart slide with dark background and neon accents."""
    title: str = Field(default="Market Comparison", description="Main title on the top left in large bold white text. Example: 'Regional Revenue', 'Top Markets'.")
    subtitle: str = Field(default="Horizontal bar analysis", description="Subtitle in neon-green below the title. Example: 'Year-over-year comparison by region'.")
    categories: List[str] = Field(
        default=["North America", "Europe", "Asia"],
        description="Category labels on the Y axis (left side). Good for long text labels. Example: ['North America', 'Europe', 'Asia Pacific'].",
    )
    series: List[Dict[str, Any]] = Field(
        default=[{"name": "2024", "data": [3, 6, 16]}, {"name": "2025", "data": [6, 14, 18]}],
        description="Data series. Each dict has 'name' (legend label) and 'data' (list of numbers, one per category). Example: [{'name': '2024', 'data': [3, 6, 16]}, {'name': '2025', 'data': [6, 14, 18]}].",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional hex colors for each series. Defaults to neon-green/olive. Example: ['#DFFF00', '#7B8C00'].",
    )
    background_color: str = Field(default="#050505", description="Background color (dark by default for high-contrast look).")
    title_color: str = Field(default="#FFFFFF", description="Color of the title text (white for dark background).")
    subtitle_color: str = Field(default="#DFFF00", description="Color of the subtitle text (neon accent).")


class GenerateLineChartSlideInput(BaseModel):
    """Input for line chart slide with connected data points and value labels."""
    title: str = Field(default="Revenue Trend", description="Main title at top left in large bold text. Example: 'Monthly Growth', 'User Acquisition Trend'.")
    subtitle: str = Field(default="Monthly performance tracking", description="Subtitle below the title. Example: 'Jan-Jun 2024 performance tracking'.")
    categories: List[str] = Field(
        default=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        description="Time-period or category labels along the X axis. Example: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] or ['Week 1', 'Week 2', 'Week 3'].",
    )
    series: List[Dict[str, Any]] = Field(
        default=[{"name": "Revenue", "data": [10, 25, 18, 30, 22, 40]}],
        description="Data series. Each dict has 'name' (legend label) and 'data' (list of numbers). Multiple series create multiple colored lines with separate legends. Example: [{'name': 'Revenue', 'data': [10, 25, 18, 30, 22, 40]}, {'name': 'Profit', 'data': [5, 12, 8, 18, 10, 25]}].",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional hex colors for each line. Defaults to indigo-emerald-amber palette. Example: ['#4F46E5', '#10B981'].",
    )
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#1B2559", description="Color of the title and axis label text.")
    subtitle_color: str = Field(default="#6B7280", description="Color of the subtitle text.")


class GenerateScatterChartSlideInput(BaseModel):
    """Input for scatter plot slide with colored circle markers and axis labels."""
    title: str = Field(default="Correlation Analysis", description="Main title at top left. Example: 'Height vs Weight', 'Price vs Demand'.")
    subtitle: str = Field(default="Scatter plot visualization", description="Subtitle below the title. Example: 'Product correlation study'.")
    x_label: str = Field(default="X Axis", description="Label for the X axis (displayed at the bottom center). Example: 'Height (cm)', 'Price ($)'.")
    y_label: str = Field(default="Y Axis", description="Label for the Y axis (displayed vertically on the left). Example: 'Weight (kg)', 'Units Sold'.")
    series: List[Dict[str, Any]] = Field(
        default=[{"name": "Group A", "data": [[10, 20], [15, 35], [25, 15], [30, 40], [45, 25]]}],
        description="Scatter data series. Each dict has 'name' (legend label) and 'data' (list of [x, y] coordinate pairs). Multiple series create different colored groups. Example: [{'name': 'Males', 'data': [[170, 70], [180, 85]]}, {'name': 'Females', 'data': [[160, 55], [165, 60]]}].",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional hex colors for each series group. Example: ['#4F46E5', '#10B981'].",
    )
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#1B2559", description="Color of the title and legend text.")
    subtitle_color: str = Field(default="#6B7280", description="Color of the subtitle and axis label text.")


class GenerateStackedBarChartSlideInput(BaseModel):
    """Input for stacked bar chart slide showing part-to-whole breakdown per category."""
    title: str = Field(default="Budget Allocation", description="Main title at top left. Example: 'Resource Allocation', 'Revenue Breakdown by Source'.")
    subtitle: str = Field(default="Stacked bar breakdown by category", description="Subtitle below the title. Example: 'Marketing, R&D, and Sales spend 2022-2024'.")
    categories: List[str] = Field(
        default=["2022", "2023", "2024"],
        description="Category labels along the X axis. Each category has one stacked bar. Example: ['2022', '2023', '2024'] or ['Dept A', 'Dept B'].",
    )
    series: List[Dict[str, Any]] = Field(
        default=[{"name": "Marketing", "data": [20, 30, 25]}, {"name": "R&D", "data": [40, 35, 50]}, {"name": "Sales", "data": [15, 20, 18]}],
        description="Data series stacked on top of each other. Each dict has 'name' (segment label in legend) and 'data' (list of numbers, one per category). Value labels are shown inside segments when tall enough. Example: [{'name': 'Marketing', 'data': [20, 30, 25]}, {'name': 'R&D', 'data': [40, 35, 50]}].",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional hex colors for each stacked segment. Defaults to indigo-emerald-amber palette. Example: ['#4F46E5', '#10B981', '#F59E0B'].",
    )
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#1B2559", description="Color of the title and category labels.")
    subtitle_color: str = Field(default="#6B7280", description="Color of the subtitle text.")


class GenerateWaterfallChartSlideInput(BaseModel):
    """Input for waterfall chart slide showing incremental gains and losses."""
    title: str = Field(default="Revenue Waterfall", description="Main title at top left. Example: 'Revenue to Profit Bridge', 'Budget Impact Analysis'.")
    subtitle: str = Field(default="From start to end breakdown", description="Subtitle below the title. Example: 'Q4 Financial Waterfall'.")
    items: List[Dict[str, Any]] = Field(
        default=[
            {"label": "Start", "value": 100, "type": "total"},
            {"label": "Growth", "value": 50, "type": "increase"},
            {"label": "Returns", "value": -20, "type": "decrease"},
            {"label": "Tax", "value": -15, "type": "decrease"},
            {"label": "End", "value": 115, "type": "total"},
        ],
        description=(
            "Waterfall steps. Each dict has 'label' (step name), 'value' (number), and 'type' ('total' for absolute baseline/final, "
            "'increase' for positive change shown in green, 'decrease' for negative change shown in red). "
            "Typically starts and ends with 'total' type. Example: "
            "[{'label': 'Revenue', 'value': 500, 'type': 'total'}, {'label': 'COGS', 'value': -200, 'type': 'decrease'}, "
            "{'label': 'Gross Profit', 'value': 300, 'type': 'total'}]."
        ),
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="3 hex colors: [total_color, increase_color, decrease_color]. Defaults to [blue, green, red]. Example: ['#4F46E5', '#10B981', '#EF4444'].",
    )
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#1B2559", description="Color of the title and step labels.")
    subtitle_color: str = Field(default="#6B7280", description="Color of the subtitle text.")


class GenerateRadarChartSlideInput(BaseModel):
    """Input for radar/spider chart slide with concentric polygon grids and filled data areas."""
    title: str = Field(default="Skills Assessment", description="Main title at top left. Example: 'Team Capability Map', 'Product Feature Comparison'.")
    subtitle: str = Field(default="Multi-dimensional performance radar", description="Subtitle below the title. Example: 'Engineering team Q4 assessment'.")
    labels: List[str] = Field(
        default=["Speed", "Power", "Skill", "Defense", "Stamina"],
        description="Axis labels displayed around the radar perimeter (one per spoke). Best with 4-8 dimensions. Example: ['Speed', 'Power', 'Skill', 'Defense', 'Stamina'].",
    )
    series: List[Dict[str, Any]] = Field(
        default=[{"name": "Player A", "data": [80, 65, 90, 70, 85]}],
        description="Data series. Each dict has 'name' (legend label) and 'data' (list of numbers 0-100, one per label). Multiple series create overlapping semi-transparent filled polygons. Example: [{'name': 'Team A', 'data': [80, 65, 90, 70, 85]}, {'name': 'Team B', 'data': [60, 80, 70, 90, 50]}].",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional hex colors for each series polygon. Example: ['#4F46E5', '#10B981'].",
    )
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#1B2559", description="Color of the title and axis labels.")
    subtitle_color: str = Field(default="#6B7280", description="Color of the subtitle text.")


class GenerateAreaChartSlideInput(BaseModel):
    """Input for area chart slide with filled regions under data lines."""
    title: str = Field(default="Growth Trends", description="Main title at top left. Example: 'User Growth Over Time', 'Website Traffic Trends'.")
    subtitle: str = Field(default="Area chart showing cumulative growth", description="Subtitle below the title. Example: 'Monthly active users Jan-Jun 2024'.")
    categories: List[str] = Field(
        default=["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        description="Time-period or category labels along the X axis. Example: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'].",
    )
    series: List[Dict[str, Any]] = Field(
        default=[{"name": "Users", "data": [100, 200, 180, 300, 250, 400]}],
        description="Data series. Each dict has 'name' (legend label) and 'data' (list of numbers). The area under each line is filled with a semi-transparent version of the line color. Multiple series create overlapping filled areas. Example: [{'name': 'Organic', 'data': [100, 200, 180, 300]}, {'name': 'Paid', 'data': [50, 80, 120, 150]}].",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional hex colors for each series. Area fill uses 15% opacity of the same color. Example: ['#4F46E5', '#10B981'].",
    )
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#1B2559", description="Color of the title text.")
    subtitle_color: str = Field(default="#6B7280", description="Color of the subtitle text.")


class GenerateSimpleDonutChartSlideInput(BaseModel):
    """Input for single large donut chart slide with a right-side legend list."""
    title: str = Field(default="Market Share", description="Main title at top left in large bold text. Example: 'Portfolio Allocation', 'Browser Market Share'.")
    subtitle: str = Field(default="Distribution overview", description="Subtitle below the title. Example: 'Q4 2024 distribution by product'.")
    items: List[Dict[str, Any]] = Field(
        default=[{"label": "Product A", "value": 45}, {"label": "Product B", "value": 30}, {"label": "Product C", "value": 25}],
        description="Donut segments. Each dict has 'label' (segment name) and 'value' (number — raw value, percentage is auto-calculated). The total of all values is shown in the donut center. Example: [{'label': 'Chrome', 'value': 65}, {'label': 'Safari', 'value': 19}, {'label': 'Firefox', 'value': 10}, {'label': 'Other', 'value': 6}].",
    )
    colors: Optional[List[str]] = Field(
        default=None,
        description="Optional hex colors for each segment. Defaults to indigo-emerald-amber-red palette. Example: ['#4F46E5', '#10B981', '#F59E0B'].",
    )
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    title_color: str = Field(default="#333333", description="Color of the title and legend text.")
    subtitle_color: str = Field(default="#888888", description="Color of the subtitle text.")









class GenerateOutlookDashboardSlideInput(BaseModel):
    """Input schema for generate_outlook_dashboard_slide_xml."""

    title: str = Field(default="2026 Outlook", description="Main slide title.")
    subtitle: str = Field(default="Goals & Strategic Priorities", description="Subtitle text.")
    progress_cards: List[Dict[str, Union[str, int]]] = Field(..., description="Progress cards. Each dict needs 'title', 'percentage', 'card_color', 'bar_color', 'text_color'.")
    line_chart_title: str = Field(default="Increase AI-driven advisory adoption", description="Title for the line chart.")
    line_chart_labels: List[str] = Field(default=["2021", "2022", "2023", "2024", "2025", "2026"], description="Labels for the line chart X-axis.")
    line_chart_data: List[float] = Field(default=[9, 10, 13, 20, 22, 30], description="Data for the line chart.")
    regional_title: str = Field(default="New Regional Market", description="Title for the regional targets section.")
    regional_targets: List[Dict[str, Union[str, int]]] = Field(..., description="Regional targets. Each dict needs 'name', 'region', 'percentage', 'color'.")
    bg_color: str = Field(default="#EEF2F6", description="Slide background color.")

StructuredTool.from_function(
        func=generate_outlook_dashboard_slide_xml,
        name="generate_outlook_dashboard_slide_xml",
        description="Generates an outlook dashboard slide with progress cards, a line chart, and regional gauge charts.",
        args_schema=GenerateOutlookDashboardSlideInput,
    ),


class GeneratePerformanceReviewSlideInput(BaseModel):
    """Input schema for generate_performance_review_slide_xml."""

    title: str = Field(default="ÄÃNH GIÃ HIá»†U SUáº¤T TOÃ€N DIá»†N", description="Main slide title.")
    radar_labels: List[str] = Field(default=["TÃ­nh nÄƒng", "Há»— trá»£", "Hiá»‡u quáº£ hoáº¡t Ä‘á»™ng", "Kháº£ nÄƒng sá»­ dá»¥ng", "GiÃ¡ trá»‹"], description="Labels for the radar chart axes.")
    radar_series: List[Dict[str, Union[str, List[float]]]] = Field(..., description="Radar chart data. Each dict needs 'name', 'data', and 'color'. example: [{'name': 'TiÃªu chuáº©n', 'data': [4, 3, 5, 6, 7], 'color': '#42A5F5'}]")
    area_labels: List[str] = Field(default=["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"], description="Labels for the area chart X-axis.")
    area_series: List[Dict[str, Union[str, List[float]]]] = Field(..., description="Area chart data. Each dict needs 'name', 'data', and 'color'. example: [{'name': 'MÃ¡y tÃ­nh Ä‘á»ƒ bÃ n', 'data': [0, 15, 20, 30, 31, 32], 'color': '#42A5F5'}]")
    bullet_points: List[str] = Field(default=["DÃ²ng Ä‘Ã¡nh giÃ¡ vá» hiá»‡u suáº¥t"], description="List of bullet points to display at the bottom right.")
    bg_color_top: str = Field(default="#FFFFFF", description="Top background color.")
    bg_color_bottom: str = Field(default="#F0F7FA", description="Bottom background color.")
    title_color: str = Field(default="#1E88E5", description="Color of the main title text.")
    text_color: str = Field(default="#333333", description="General text color.")

StructuredTool.from_function(
        func=generate_performance_review_slide_xml,
        name="generate_performance_review_slide_xml",
        description="Generates a performance review slide containing a radar chart on the left and an area chart on the right, with bullet points at the bottom right.",
        args_schema=GeneratePerformanceReviewSlideInput,
    ),


class GenerateKPIDashboardSlideInput(BaseModel):
    """Input schema for generate_kpi_dashboard_slide_xml."""

    title: str = Field(default="Primary KPI Dashboard", description="Main slide title.")
    kpi_cards: List[Dict[str, Union[str, int]]] = Field(
        default=[
            {"title": "Revenue\\nand Sales", "percentage": 72, "color": "#F26D60"},
            {"title": "Achieved\\nConversion Rate", "percentage": 60, "color": "#E85EAE"},
            {"title": "Customer\\nRetention", "percentage": 86, "color": "#3BBA77"}
        ],
        description="KPI cards. Each dict needs 'title', 'percentage', 'color'."
    )
    chart_labels: List[str] = Field(default=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], description="Labels for the line chart X-axis.")
    chart_data: List[float] = Field(default=[200, 700, 600, 900, 300, 600, 900, 250, 600, 500, 700, 600], description="Data for the line chart.")
    bg_color: str = Field(default="#F8F9FA", description="Slide background color.")

StructuredTool.from_function(
        func=generate_kpi_dashboard_slide_xml,
        name="generate_kpi_dashboard_slide_xml",
        description="Generates a primary KPI dashboard slide with 3 progress cards on the left and a large line chart on the right.",
        args_schema=GenerateKPIDashboardSlideInput,
    ),


class GenerateRevenueTargetSlideInput(BaseModel):
    """Input schema for generate_revenue_target_slide_xml."""

    title: str = Field(default="Annual Revenue Target", description="Main slide title.")
    top_left_card: Dict[str, str] = Field(
        default={"title": "Annual Target", "value": "$15M", "subtitle": "on track"},
        description="Top left teal card."
    )
    top_right_card: Dict[str, str] = Field(
        default={"title": "Forecast Q4", "value": "+6-8%", "subtitle": "projected growth"},
        description="Top right teal card."
    )
    bottom_card: Dict[str, Union[str, int]] = Field(
        default={"title": "Current YTD (Q3)", "value": "$11.2M", "subtitle": "74% achieved", "percentage": 74},
        description="Bottom wide card with a donut chart."
    )
    bar_chart_title: str = Field(default="Quarterly Revenue Data", description="Title for the bar chart card.")
    bar_chart_labels: List[str] = Field(default=["Q1", "Q2", "Q3", "Q4"], description="Labels for the bar chart X-axis.")
    bar_chart_data: List[float] = Field(default=[3, 4, 6, 4], description="Data for the bar chart.")
    bg_color: str = Field(default="#F5F6F8", description="Slide background color.")

StructuredTool.from_function(
        func=generate_revenue_target_slide_xml,
        name="generate_revenue_target_slide_xml",
        description="Generates an Annual Revenue Target slide with KPI cards (including a donut chart) and a bar chart.",
        args_schema=GenerateRevenueTargetSlideInput,
    ),


class GenerateModernDonutChartSlideInput(BaseModel):
    """Input schema for generate_modern_donut_chart_slide_xml."""

    title: str = Field(default="NGUá»’N Lá»°C DOANH THU", description="Main title displayed at the top center.")
    chart_labels: List[str] = Field(default=["KhÃ¡ch hÃ ng doanh nghiá»‡p", "KhÃ¡ch hÃ ng cÃ¡ nhÃ¢n", "Äáº¡i lÃ½ & Ä‘á»‘i tÃ¡c", "KhÃ¡ch hÃ ng dá»± Ã¡n"], description="Labels for the donut chart segments and right-side bars.")
    chart_data: List[float] = Field(default=[45, 30, 15, 10], description="Data values (percentages) for the donut chart.")
    colors: Optional[List[str]] = Field(default=["#00E5FF", "#0099FF", "#9D84FF", "#6E5BFF"], description="List of hex color codes for each segment.")
    background_color: str = Field(default="#F3FBFE", description="Background color of the slide.")
    title_color: str = Field(default="#4B61FF", description="Color of the main title text.")
    text_color: str = Field(default="#FFFFFF", description="Color of the text inside the colored bars.")

StructuredTool.from_function(
        func=generate_modern_donut_chart_slide_xml,
        name="generate_modern_donut_chart_slide_xml",
        description="Generates an infographic donut chart slide with a modern design, large donut chart on the left, and horizontal colored label bars on the right with percentages. Ideal for revenue breakdown, budget distribution, or demographic statistics.",
        args_schema=GenerateModernDonutChartSlideInput,
    ),


class GenerateAnalysisStorySlideInput(BaseModel):
    """Input schema for generate_analysis_story_slide_xml."""

    title: str = Field(default="PHÃ‚N TÃCH & CÃ‚U CHUYá»†N", description="Main slide title.")
    badge_text: str = Field(default="BÃO CÃO", description="Text for the top left badge.")
    chart_title: str = Field(default="KPI cÃ¡c thÃ¡ng", description="Title for the chart on the left.")
    chart_labels: List[str] = Field(default=["T1", "T2", "T3", "T4", "T5", "T6"], description="Labels for the X-axis.")
    chart_data: List[float] = Field(default=[750, 1000, 1300, 800, 250, 1500], description="Data values for the bar chart.")
    insights_title: str = Field(default="Nháº­n Ä‘á»‹nh chÃ­nh", description="Title for the insights card on the right.")
    insights: List[str] = Field(default=["ÄÃ¢y lÃ  nháº­n Ä‘á»‹nh Ä‘áº§u tiÃªn tá»« dá»¯ liá»‡u.", "ÄÃ¢y lÃ  nháº­n Ä‘á»‹nh thá»© hai, giáº£i thÃ­ch nguyÃªn nhÃ¢n hoáº·c yáº¿u tá»‘ áº£nh hÆ°á»Ÿng.", "ÄÃ¢y lÃ  nháº­n Ä‘á»‹nh thá»© ba, gá»£i Ã½ hÃ nh Ä‘á»™ng hoáº·c cÆ¡ há»™i cáº£i thiá»‡n."], description="List of bullet points for insights.")
    conclusion_text: str = Field(default="Káº¿t luáº­n: ÄÃ¢y lÃ  cÃ¢u káº¿t ngáº¯n gá»n, nháº¥n máº¡nh thÃ´ng Ä‘iá»‡p chÃ­nh vÃ  Ä‘á»‹nh hÆ°á»›ng tiáº¿p theo.", description="Text for the conclusion at the bottom of insights card.")
    footer_text: str = Field(default="BÃ¡o cÃ¡o dá»± Ã¡n", description="Footer text on the left.")
    page_number: str = Field(default="06", description="Page number on the right.")
    background_color: str = Field(default="#FFFFFF", description="Background color.")
    primary_color: str = Field(default="#0B114F", description="Primary theme color (dark blue).")
    secondary_color: str = Field(default="#4B7BFF", description="Secondary theme color (light blue).")
    light_bg_color: str = Field(default="#EEF4FF", description="Light background color for the right panel.")
    text_color: str = Field(default="#333333", description="Text color.")


class DarkMultiLineChartSlideInput(BaseModel):
    """Input schema for generate_dark_multi_line_chart_slide_xml."""
    title: str = Field(default="Slide Title", description="Main slide title.")
    
class LineChartReportSlideInput(BaseModel):
    """Input schema for generate_line_chart_report_slide_xml."""
    title: str = Field(default="Slide Title", description="Main slide title.")
    
class ModernPieChartSlideInput(BaseModel):
    """Input schema for generate_modern_pie_chart_slide_xml."""
    title: str = Field(default="Slide Title", description="Main slide title.")
    

CHART_TOOLS = [
    StructuredTool.from_function(
        func=generate_dark_multi_line_chart_slide_xml,
        name="generate_dark_multi_line_chart_slide_xml",
        description="Generates generate_dark_multi_line_chart_slide_xml slide.",
        args_schema=DarkMultiLineChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_line_chart_report_slide_xml,
        name="generate_line_chart_report_slide_xml",
        description="Generates generate_line_chart_report_slide_xml slide.",
        args_schema=LineChartReportSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_modern_pie_chart_slide_xml,
        name="generate_modern_pie_chart_slide_xml",
        description="Generates generate_modern_pie_chart_slide_xml slide.",
        args_schema=ModernPieChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_outlook_dashboard_slide_xml,
        name="generate_outlook_dashboard_slide_xml",
        description="Generates generate_outlook_dashboard_slide_xml slide.",
        args_schema=GenerateOutlookDashboardSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_performance_review_slide_xml,
        name="generate_performance_review_slide_xml",
        description="Generates generate_performance_review_slide_xml slide.",
        args_schema=GeneratePerformanceReviewSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_kpi_dashboard_slide_xml,
        name="generate_kpi_dashboard_slide_xml",
        description="Generates generate_kpi_dashboard_slide_xml slide.",
        args_schema=GenerateKPIDashboardSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_revenue_target_slide_xml,
        name="generate_revenue_target_slide_xml",
        description="Generates generate_revenue_target_slide_xml slide.",
        args_schema=GenerateRevenueTargetSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_modern_donut_chart_slide_xml,
        name="generate_modern_donut_chart_slide_xml",
        description="Generates generate_modern_donut_chart_slide_xml slide.",
        args_schema=GenerateModernDonutChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_analysis_story_slide_xml,
        name="generate_analysis_story_slide_xml",
        description="Generates generate_analysis_story_slide_xml slide.",
        args_schema=GenerateAnalysisStorySlideInput,
    ),

    # === Pie & Donut (items-based) ===
    StructuredTool.from_function(
        func=generate_pie_chart_slide_xml,
        name="generate_pie_chart_slide_xml",
        description=(
            "Generates a professional pie chart slide with a dark green header banner, a dark left-side legend panel showing colored squares with labels and descriptions, "
            "and a large pie chart on the right with percentage labels around slices. Uses an earthy green-beige color palette by default. "
            "Best for: budget breakdowns, market share, revenue distribution, composition analysis. "
            "Data: items=[{'label': 'Marketing', 'value': 35, 'description': 'Digital campaigns'}]. Max 6 slices. Values are auto-converted to percentages."
        ),
        args_schema=GeneratePieChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_donut_chart_slide_xml,
        name="generate_donut_chart_slide_xml",
        description=(
            "Generates an elegant slide with exactly 3 horizontal donut progress rings, each showing a percentage (0-100%) with bold text in the center, "
            "and a label + description below each donut. Has a thin left accent bar and subtle corner decorations. "
            "Best for: KPI dashboards, progress tracking, comparing 3 metrics/goals side by side. "
            "Data: items=[{'label': 'Design', 'value': 85, 'description': 'Completion rate'}]. Exactly 3 items required."
        ),
        args_schema=GenerateDonutChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_simple_donut_chart_slide_xml,
        name="generate_simple_donut_chart_slide_xml",
        description=(
            "Generates a clean single large donut chart centered on the left with a total value in the middle, and a color-coded legend list on the right showing each segment's label and percentage. "
            "Best for: market share, portfolio allocation, survey results, any proportional data visualization. "
            "Data: items=[{'label': 'Product A', 'value': 45}, {'label': 'Product B', 'value': 30}]. Supports any number of segments."
        ),
        args_schema=GenerateSimpleDonutChartSlideInput,
    ),

    # === Bar Charts (categories + series) ===
    StructuredTool.from_function(
        func=generate_bar_chart_slide_xml,
        name="generate_bar_chart_slide_xml",
        description=(
            "Generates a vertical bar chart slide with a white background, gridlines, value labels on top of each bar, and a color-coded legend. "
            "Supports multiple series for grouped/clustered bars. Bars are auto-scaled from data values with rounded corners. "
            "Best for: quarterly comparison, revenue vs cost, year-over-year metrics, category comparison. "
            "Data: categories=['Q1','Q2','Q3','Q4'], series=[{'name':'Revenue','data':[45,52,68,58]}]. Y-axis auto-scales."
        ),
        args_schema=GenerateBarChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_horizontal_bar_chart_slide_xml,
        name="generate_horizontal_bar_chart_slide_xml",
        description=(
            "Generates a horizontal bar chart slide with a sleek dark background (#050505), neon-green accent subtitle, circle-shaped legend markers, "
            "and category labels on the left. Title and subtitle are on the left side, chart on the right. "
            "Best for: regional comparison, ranking data, long category labels that need horizontal space. "
            "Data: categories=['North America','Europe','Asia'], series=[{'name':'2024','data':[3,6,16]}]."
        ),
        args_schema=GenerateHorizontalBarChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_stacked_bar_chart_slide_xml,
        name="generate_stacked_bar_chart_slide_xml",
        description=(
            "Generates a stacked bar chart slide where multiple data series are stacked on top of each other within each category bar. "
            "Shows value labels inside each segment when tall enough. Includes gridlines and a color-coded legend. "
            "Best for: budget allocation over time, resource distribution, part-to-whole comparison across categories. "
            "Data: categories=['2022','2023','2024'], series=[{'name':'Marketing','data':[20,30,25]}, {'name':'R&D','data':[40,35,50]}]."
        ),
        args_schema=GenerateStackedBarChartSlideInput,
    ),

    # === Line & Area Charts (categories + series) ===
    StructuredTool.from_function(
        func=generate_line_chart_slide_xml,
        name="generate_line_chart_slide_xml",
        description=(
            "Generates a line chart slide with smooth connected lines, circular data point markers, and value labels above each point. "
            "Supports multiple series as separate colored lines with a legend. Includes gridlines and axis labels. "
            "Best for: trend analysis over time, monthly/quarterly performance tracking, growth visualization. "
            "Data: categories=['Jan','Feb','Mar','Apr','May','Jun'], series=[{'name':'Revenue','data':[10,25,18,30,22,40]}]."
        ),
        args_schema=GenerateLineChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_area_chart_slide_xml,
        name="generate_area_chart_slide_xml",
        description=(
            "Generates an area chart slide with filled semi-transparent areas under each line, data point markers, and a legend. "
            "The filled area emphasizes volume/magnitude over time. Supports multiple overlapping series. "
            "Best for: cumulative growth, volume trends, showing magnitude of change over time (users, revenue, traffic). "
            "Data: categories=['Jan','Feb','Mar','Apr','May','Jun'], series=[{'name':'Users','data':[100,200,180,300,250,400]}]."
        ),
        args_schema=GenerateAreaChartSlideInput,
    ),

    # === Specialized Charts ===
    StructuredTool.from_function(
        func=generate_scatter_chart_slide_xml,
        name="generate_scatter_chart_slide_xml",
        description=(
            "Generates a scatter plot slide with semi-transparent circle markers, gridlines, X/Y axis labels, and a color-coded legend. "
            "Each data point is an [x, y] coordinate pair. Supports multiple groups/series. "
            "Best for: correlation analysis, distribution visualization, comparing two numerical variables, clustering patterns. "
            "Data: series=[{'name':'Group A','data':[[10,20],[15,35],[25,15]]}], x_label='Height', y_label='Weight'."
        ),
        args_schema=GenerateScatterChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_radar_chart_slide_xml,
        name="generate_radar_chart_slide_xml",
        description=(
            "Generates a radar/spider chart slide with concentric polygon gridlines, axis spokes with labels around the perimeter, "
            "and filled semi-transparent data polygons with point markers. The chart is centered on the slide. "
            "Best for: skills assessment, multi-dimensional comparison, product feature scoring, team capability mapping. "
            "Data: labels=['Speed','Power','Skill','Defense','Stamina'], series=[{'name':'Player A','data':[80,65,90,70,85]}]. Values 0-100."
        ),
        args_schema=GenerateRadarChartSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_waterfall_chart_slide_xml,
        name="generate_waterfall_chart_slide_xml",
        description=(
            "Generates a waterfall chart slide showing incremental positive and negative changes between a start and end total. "
            "Uses 3 colors: blue for totals, green for increases, red for decreases. Includes gridlines and value labels above each bar. "
            "Best for: financial breakdown (revenue to profit), budget changes, showing how individual factors contribute to a final result. "
            "Data: items=[{'label':'Start','value':100,'type':'total'}, {'label':'Growth','value':50,'type':'increase'}, {'label':'Tax','value':-15,'type':'decrease'}, {'label':'End','value':135,'type':'total'}]."
        ),
        args_schema=GenerateWaterfallChartSlideInput,
    ),
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


