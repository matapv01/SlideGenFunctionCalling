"""
Thank you slide tools - Closing and thank you templates.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class GenerateThankYouSlideInput(BaseModel):
    """Input schema for generate_thank_you_slide."""
    title: str = Field(..., description="Main thank you message")
    subtitle: str = Field(..., description="Subtitle text")
    font_family: str = Field(default="'Poppins', sans-serif", description="Font family")
    background_gradient: str = Field(default="linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)", description="Background gradient")
    accent_color: str = Field(default="#FFD700", description="Accent color")
    card_color: str = Field(default="#FFFFFF", description="Card background color")
    text_color: str = Field(default="#333333", description="Text color")


class GenerateThankYouSlide2Input(BaseModel):
    """Input schema for generate_thank_you_slide_2."""
    main_text: str = Field(default="THANKS!", description="Main thank you message")
    question_text: str = Field(default="Any questions?", description="Q&A text")
    font_family_heading: str = Field(default="'Patrick Hand', cursive", description="Heading font")
    font_family_body: str = Field(default="'Lato', sans-serif", description="Body font")
    main_color: str = Field(default="#56B2E8", description="Main accent color")
    text_color: str = Field(default="#34495E", description="Text color")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="Background URL")


class GenerateThankYouSlide3Input(BaseModel):
    """Input schema for generate_thank_you_slide_3."""
    main_title: str = Field(..., description="Main title")
    phone_number: str = Field(default="123-456-7890", description="Phone number")
    email: str = Field(default="hello@example.com", description="Email address")
    show_phone: Optional[bool] = Field(default=True, description="Show phone number")
    show_email: Optional[bool] = Field(default=True, description="Show email")
    background_gradient_start: str = Field(default="#4A90E2", description="Gradient start color")
    background_gradient_end: str = Field(default="#2E5BBA", description="Gradient end color")


class GenerateCorporateThankYouSlideInput(BaseModel):
    """Input schema for generate_corporate_thank_you_slide."""
    thanks_text: str = Field(default="THANK YOU FOR WATCHING!", description="The main closing message")
    font_family: str = Field(default="'Montserrat', sans-serif", description="The font family for the text")
    accent_color: str = Field(default="#F97316", description="The primary accent color for the right panel")
    shadow_color: str = Field(default="#EA580C", description="The secondary accent color for the panel behind")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small smiley icon")


THANK_YOU_TOOLS_INFO = {
    "generate_thank_you_slide": {
        "description": "Modern thank you slide with gradient background and animated sparkles",
        "input_schema": GenerateThankYouSlideInput,
    },
    "generate_thank_you_slide_2": {
        "description": "Charming thank you slide with hand-drawn aesthetic and Q&A section",
        "input_schema": GenerateThankYouSlide2Input,
    },
    "generate_thank_you_slide_3": {
        "description": "Corporate thank you slide with contact information",
        "input_schema": GenerateThankYouSlide3Input,
    },
    "generate_corporate_thank_you_slide": {
        "description": "Minimalist corporate thank you slide with diagonal color panel",
        "input_schema": GenerateCorporateThankYouSlideInput,
    },
}
