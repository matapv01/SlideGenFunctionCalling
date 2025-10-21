"""
Intro slide tools - Introduction and title slide templates.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class GenerateTitleSlideInput(BaseModel):
    """Input schema for generate_title_slide."""
    main_title: str = Field(..., description="Main title text (10-30 characters)")
    subtitle: str = Field(..., description="Subtitle text (5-20 characters)")
    bg_color: str = Field(default="#1a4b8c", description="Primary background color (hex)")
    bg_gradient_to: str = Field(default="#2a6cb7", description="Gradient end color (hex)")
    text_color: str = Field(default="#FFFFFF", description="Text color (hex)")
    font_family: str = Field(default="Arial, sans-serif", description="Font family")
    show_skyline: Optional[bool] = Field(default=True, description="Show skyline")
    skyline_opacity: Optional[float] = Field(default=0.3, description="Skyline opacity")
    triangle_opacity: Optional[float] = Field(default=0.2, description="Triangle opacity")
    title_font_size: str = Field(default="5rem", description="Title font size")
    subtitle_font_size: str = Field(default="2rem", description="Subtitle font size")
    custom_css: str = Field(default="", description="Custom CSS")


class GenerateIntroductionSlideInput(BaseModel):
    """Input schema for generate_introduction_slide."""
    main_title: str = Field(..., description="Main title text (8-20 characters)")
    content_text: str = Field(..., description="Main content paragraph")
    bg_color: str = Field(default="#1a4b8c", description="Primary background color")
    bg_gradient_to: str = Field(default="#2a6cb7", description="Gradient end color")
    text_color: str = Field(default="#FFFFFF", description="Text color")
    title_font_size: str = Field(default="4rem", description="Title font size")
    content_font_size: str = Field(default="1.4rem", description="Content font size")
    font_family: str = Field(default="Arial, sans-serif", description="Font family")
    show_decorative_triangles: Optional[bool] = Field(default=True, description="Show decorative triangles")
    triangle_opacity: Optional[float] = Field(default=0.15, description="Triangle opacity")
    show_border: Optional[bool] = Field(default=True, description="Show border frame")
    border_opacity: Optional[float] = Field(default=0.4, description="Border opacity")


class GenerateIntroSlide1Input(BaseModel):
    """Input schema for generate_intro_slide1."""
    title: str = Field(..., description="Main title on left section")
    subtitle: str = Field(..., description="Subtitle under title")
    image_url: str = Field(..., description="Image URL for right section")
    bg_color: str = Field(default="#FFFFFF", description="Background color")
    text_color: str = Field(default="#333333", description="Text color")
    title_font_size: str = Field(default="3.5rem", description="Title font size")


class GenerateElegantIntroSlideInput(BaseModel):
    """Input schema for generate_elegant_intro_slide."""
    main_title: str = Field(..., description="Large title displayed in left column")
    subtitle: str = Field(..., description="Smaller subtitle text below main title")
    image_url: str = Field(default="https://images.pexels.com/photos/3807735/pexels-photo-3807735.jpeg", description="Image URL")
    font_family: str = Field(default="'Be Vietnam Pro', sans-serif", description="Font family")
    background_color: str = Field(default="#EAE3D9", description="Background color")
    text_color: str = Field(default="#4A403A", description="Text color")
    decoration_color_start: str = Field(default="#F7DC6F", description="Decoration gradient start")
    decoration_color_end: str = Field(default="#C9A842", description="Decoration gradient end")
    title_font_size: str = Field(default="3.5rem", description="Title font size")
    subtitle_font_size: str = Field(default="1.5rem", description="Subtitle font size")


class GenerateInspirationalQuoteSlideInput(BaseModel):
    """Input schema for generate_inspirational_quote_slide."""
    quote_text: str = Field(..., description="Quote text to display")
    author_name: str = Field(..., description="Quote author name")
    bg_image_url: str = Field(..., description="Background image URL")
    overlay_opacity: float = Field(default=0.5, description="Overlay opacity (0-1)")
    font_color: str = Field(default="#FFFFFF", description="Text color")
    quote_font_size: str = Field(default="2.5rem", description="Quote font size")


class GenerateTitleSlide2Input(BaseModel):
    """Input schema for generate_title_slide_2."""
    main_title: str = Field(..., description="Main title text")
    subtitle: str = Field(..., description="Subtitle text")
    highlight_word: Optional[str] = Field(default=None, description="Word to highlight with color")
    bg_color: str = Field(default="#003D7A", description="Primary background color")
    secondary_color: str = Field(default="#FF6B35", description="Secondary accent color")
    text_color: str = Field(default="#FFFFFF", description="Text color")
    title_font_size: str = Field(default="4rem", description="Title font size")


class GenerateDynamicIntroSlideInput(BaseModel):
    """Input schema for generate_dynamic_intro_slide."""
    main_title: str = Field(..., description="Main title")
    subtitle: str = Field(..., description="Subtitle")
    image_url: str = Field(..., description="Right-side image URL")
    bg_color: str = Field(default="#1F4788", description="Left panel background color")
    text_color: str = Field(default="#FFFFFF", description="Text color")
    title_font_size: str = Field(default="4rem", description="Title font size")


class GenerateBigConceptSlideInput(BaseModel):
    """Input schema for generate_big_concept_slide."""
    concept_title: str = Field(..., description="Main concept title")
    concept_description: str = Field(..., description="Concept description text")
    illustration_type: str = Field(default="planet", description="Type of illustration")
    bg_color: str = Field(default="#FFFFFF", description="Background color")
    accent_color: str = Field(default="#FF6B35", description="Accent color")
    text_color: str = Field(default="#333333", description="Text color")
    title_font_size: str = Field(default="3rem", description="Title font size")


class GenerateElegantAgendaSlideInput(BaseModel):
    """Input schema for generate_elegant_agenda_slide."""
    title: str = Field(..., description="Slide title")
    agenda_items: List[str] = Field(..., description="List of agenda items")
    image_url: str = Field(..., description="Left-side image URL")
    bg_color: str = Field(default="#F5F5F5", description="Background color")
    text_color: str = Field(default="#333333", description="Text color")
    title_color: str = Field(default="#1a4b8c", description="Title text color")


class GeneratePlayfulTitleSlideInput(BaseModel):
    """Input schema for generate_playful_title_slide."""
    main_title: str = Field(..., description="Main title")
    subtitle: str = Field(..., description="Subtitle")
    illustration_type: str = Field(default="penguin", description="Illustration type (penguin, etc)")
    primary_color: str = Field(default="#FF6B6B", description="Primary color")
    secondary_color: str = Field(default="#FFE66D", description="Secondary color")
    text_color: str = Field(default="#333333", description="Text color")


class GenerateMinimalistTitleSlideInput(BaseModel):
    """Input schema for generate_minimalist_title_slide."""
    main_title: str = Field(..., description="Main title")
    subtitle: str = Field(..., description="Subtitle")
    bg_color: str = Field(default="#0A0E27", description="Background color")
    text_color: str = Field(default="#FFFFFF", description="Text color")
    portal_color: str = Field(default="#00D4FF", description="Portal glow color")
    title_font_size: str = Field(default="4rem", description="Title font size")


class GenerateMissionSlideInput(BaseModel):
    """Input schema for generate_mission_slide."""
    section_title: str = Field(..., description="Section title (Mission/Vision/etc)")
    content_text: str = Field(..., description="Mission/Vision content")
    image_url: str = Field(..., description="Right-side image URL")
    bg_color: str = Field(default="#FFF8F3", description="Background color")
    title_color: str = Field(default="#8B7355", description="Title color")
    text_color: str = Field(default="#5A4A42", description="Text color")


# Tool metadata for intro tools
INTRO_TOOLS_INFO = {
    "generate_title_slide": {
        "description": "Generates a professional title slide with a blue gradient background, geometric shapes, and optional city skyline.",
        "input_schema": GenerateTitleSlideInput
    },
    "generate_introduction_slide": {
        "description": "Generates a professional introduction slide with gradient background and decorative elements.",
        "input_schema": GenerateIntroductionSlideInput
    },
    "generate_intro_slide1": {
        "description": "Generates an HTML introduction slide with a main title section on the left and an image on the right.",
        "input_schema": GenerateIntroSlide1Input
    },
    "generate_elegant_intro_slide": {
        "description": "Generates an elegant Introduction or Title slide, featuring an asymmetrical two-column layout with a large title on the left and a framed image on the right.",
        "input_schema": GenerateElegantIntroSlideInput
    },
    "generate_inspirational_quote_slide": {
        "description": "Generates a bright, airy, and sophisticated Quote Slide with full-screen background image and elegant typography.",
        "input_schema": GenerateInspirationalQuoteSlideInput
    },
    "generate_title_slide_2": {
        "description": "Generates an Introductory or Title Slide with a sharp diagonal split and layered color panels.",
        "input_schema": GenerateTitleSlide2Input
    },
    "generate_dynamic_intro_slide": {
        "description": "Generates an Introductory or Title slide with bold asymmetrical layout, full-height image on the right, and angled cutout.",
        "input_schema": GenerateDynamicIntroSlideInput
    },
    "generate_big_concept_slide": {
        "description": "Generates a high-impact Content Slide of the Big Concept type to highlight single major ideas.",
        "input_schema": GenerateBigConceptSlideInput
    },
    "generate_elegant_agenda_slide": {
        "description": "Generates an elegant, minimalist agenda or table of contents slide with two-column layout.",
        "input_schema": GenerateElegantAgendaSlideInput
    },
    "generate_playful_title_slide": {
        "description": "Generates a friendly, hand-drawn style title slide with charming illustration and playful typography.",
        "input_schema": GeneratePlayfulTitleSlideInput
    },
    "generate_minimalist_title_slide": {
        "description": "Generates a stunning, high-tech Title Slide with sophisticated dark theme and animated portal.",
        "input_schema": GenerateMinimalistTitleSlideInput
    },
    "generate_mission_slide": {
        "description": "Generates a Content Slide with two-column layout for presenting Mission, Vision, or Introduction.",
        "input_schema": GenerateMissionSlideInput
    },
}
