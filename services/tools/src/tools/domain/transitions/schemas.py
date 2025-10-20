"""
Transitions slide tools - Section headers and transition templates.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class GenerateGeometricTransitionSlideInput(BaseModel):
    """Input schema for generate_geometric_transition_slide."""
    section_number: str = Field(default="1.", description="Section number (e.g., '1.', '02', 'B.')")
    headline: str = Field(..., description="Main uppercase headline for transition")
    subtitle: str = Field(..., description="Smaller subtitle text below headline")
    font_family: str = Field(default="'Poppins', sans-serif", description="Font family")
    bg_color: str = Field(default="#0F172A", description="Dark background color")
    primary_text_color: str = Field(default="#FFFFFF", description="Text color for headline")
    subtitle_color: str = Field(default="#67E8F9", description="Accent color for subtitle")


class GenerateTransitionSlide2Input(BaseModel):
    """Input schema for generate_transition_slide_2."""
    section_number: Optional[str] = Field(default=None, description="Section number")
    main_headline: str = Field(..., description="Large uppercase headline")
    subtitle: str = Field(..., description="Smaller text below headline")
    font_family_heading: str = Field(default="'Patrick Hand', cursive", description="Heading font")
    font_family_body: str = Field(default="'Lato', sans-serif", description="Body font")
    number_color: str = Field(default="#F37A59", description="Section number color")
    text_color: str = Field(default="#2C3E50", description="Text color")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="Background texture URL")


class GenerateDuskTransitionSlideInput(BaseModel):
    """Input schema for generate_dusk_transition_slide."""
    section_title: str = Field(..., description="Section title")
    section_number: Optional[str] = Field(default=None, description="Section number")
    bg_color_start: str = Field(default="#6B21A8", description="Gradient start color")
    bg_color_end: str = Field(default="#EA580C", description="Gradient end color")
    text_color: str = Field(default="#FFFFFF", description="Text color")
    title_font_size: str = Field(default="3.5rem", description="Title font size")


class GenerateMemphisTransitionSlideInput(BaseModel):
    """Input schema for generate_memphis_transition_slide."""
    headline: str = Field(..., description="Main section headline")
    subtitle: str = Field(..., description="Section subtitle")
    bg_color_1: str = Field(default="#FFE66D", description="Background color 1")
    bg_color_2: str = Field(default="#95E1D3", description="Background color 2")
    text_color: str = Field(default="#333333", description="Text color")
    accent_color: str = Field(default="#F38181", description="Accent color")


class GeneratePushpinSectionHeaderInput(BaseModel):
    """Input schema for generate_pushpin_section_header."""
    section_title: str = Field(..., description="Section title")
    title_font_size: str = Field(default="3rem", description="Title font size")
    text_color: str = Field(default="#333333", description="Text color")
    bg_color: str = Field(default="#FFFFFF", description="Background color")
    line_color: str = Field(default="#333333", description="Decorative line color")


class GenerateSectionHeaderSlideInput(BaseModel):
    """Input schema for generate_section_header_slide."""
    header_text: str = Field(..., description="Main section header text")
    font_family: str = Field(default="'Poppins', sans-serif", description="Font family")
    bg_color: str = Field(default="#F8FAFC", description="Background color")
    text_color: str = Field(default="#1E293B", description="Text color")
    gradient_color_1: str = Field(default="#A78BFA", description="Gradient color 1")
    gradient_color_2: str = Field(default="#F472B6", description="Gradient color 2")
    gradient_color_3: str = Field(default="#7DD3FC", description="Gradient color 3")


class GenerateCorporateTransitionSlideInput(BaseModel):
    """Input schema for generate_corporate_transition_slide."""
    section_number: str = Field(default="01", description="Section number")
    section_title: str = Field(..., description="Section title")
    bg_color: str = Field(default="#1F2937", description="Left panel background color")
    panel_color: str = Field(default="#2563EB", description="Accent panel color")
    text_color: str = Field(default="#FFFFFF", description="Text color")
    title_font_size: str = Field(default="3.5rem", description="Title font size")


class GenerateIntroSlideInput(BaseModel):
    """Input schema for generate_intro_slide."""
    title: str = Field(..., description="Main title on left section")
    subtitle: str = Field(..., description="Subtitle under title")
    image_url: str = Field(..., description="Image URL for right section")
    bg_color: str = Field(default="#FFFFFF", description="Background color")
    text_color: str = Field(default="#333333", description="Text color")
    title_font_size: str = Field(default="3.5rem", description="Title font size")


class GenerateCreditsSlideInput(BaseModel):
    """Input schema for generate_credits_slide."""
    main_text: str = Field(..., description="Main content text")
    subtitle_text: str = Field(..., description="Subtitle or secondary text")
    badge_text: Optional[str] = Field(default="Created with", description="Badge text")
    bg_color: str = Field(default="#FDDCC8", description="Background color")
    text_color: str = Field(default="#8B4513", description="Text color")
    accent_color: str = Field(default="#FF6B6B", description="Accent color")


TRANSITIONS_TOOLS_INFO = {
    "generate_geometric_transition_slide": {
        "description": "Dynamic transition slide with geometric shapes in corners.",
        "input_schema": GenerateGeometricTransitionSlideInput,
    },
    "generate_transition_slide_2": {
        "description": "Transition slide with hand-drawn aesthetic and notebook paper background.",
        "input_schema": GenerateTransitionSlide2Input,
    },
    "generate_dusk_transition_slide": {
        "description": "Minimalist tech-focused transition slide with dusk color gradient.",
        "input_schema": GenerateDuskTransitionSlideInput,
    },
    "generate_memphis_transition_slide": {
        "description": "Vibrant retro Memphis-style transition slide.",
        "input_schema": GenerateMemphisTransitionSlideInput,
    },
    "generate_pushpin_section_header": {
        "description": "Minimalist section header with elegant line decoration.",
        "input_schema": GeneratePushpinSectionHeaderInput,
    },
    "generate_section_header_slide": {
        "description": "Section header with aurora gradient background and animated confetti.",
        "input_schema": GenerateSectionHeaderSlideInput,
    },
    "generate_corporate_transition_slide": {
        "description": "Modern corporate transition with overlapping angled color panels.",
        "input_schema": GenerateCorporateTransitionSlideInput,
    },
    "generate_intro_slide": {
        "description": "Introduction slide with main title on left and image on right.",
        "input_schema": GenerateIntroSlideInput,
    },
    "generate_credits_slide": {
        "description": "Credits or thank you slide with warm peach gradient background.",
        "input_schema": GenerateCreditsSlideInput,
    },
}
