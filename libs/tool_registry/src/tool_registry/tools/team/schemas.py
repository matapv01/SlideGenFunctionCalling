"""
Team slide tools - Team member presentation templates.
"""

from typing import List, Dict
from pydantic import BaseModel, Field


class GenerateTeamSlideInput(BaseModel):
    """Input schema for generate_team_slide."""
    main_title: str = Field(..., description="Main title for team slide")
    team_members: List[Dict[str, str]] = Field(..., description="List of team members with name, role, image_url")
    font_family: str = Field(default="'Inter', sans-serif", description="Font family")
    accent_bg_color: str = Field(default="#14B8A6", description="Accent background color")
    main_bg_color: str = Field(default="#F8FAFC", description="Main background color")
    title_color: str = Field(default="#FFFFFF", description="Title color")
    name_color: str = Field(default="#111827", description="Member name color")
    role_color: str = Field(default="#6B7280", description="Member role color")


class GenerateColorfulTeamGridSlideInput(BaseModel):
    """Input schema for generate_colorful_team_grid_slide."""
    main_title: str = Field(..., description="Main title")
    subtitle: str = Field(..., description="Subtitle text")
    team_members: List[Dict[str, str]] = Field(..., description="Exactly 4 team members")
    font_family: str = Field(default="'Montserrat', sans-serif", description="Font family")
    bg_color: str = Field(default="#F8FAFC", description="Background color")
    title_color: str = Field(default="#111827", description="Title color")


class GenerateCorporateTeamSlideInput(BaseModel):
    """Input schema for generate_corporate_team_slide."""
    main_title: str = Field(..., description="Main title")
    team_members: List[Dict[str, str]] = Field(..., description="Team members list")
    font_family_heading: str = Field(default="'Patrick Hand', cursive", description="Heading font")
    font_family_body: str = Field(default="'Lato', sans-serif", description="Body font")
    text_color: str = Field(default="#4A403A", description="Text color")
    role_color: str = Field(default="#6B7280", description="Role color")


TEAM_TOOLS_INFO = {
    "generate_team_slide": {
        "description": "Modern team slide with diagonal layout",
        "input_schema": GenerateTeamSlideInput,
    },
    "generate_colorful_team_grid_slide": {
        "description": "Colorful 2x2 grid team slide",
        "input_schema": GenerateColorfulTeamGridSlideInput,
    },
    "generate_corporate_team_slide": {
        "description": "Corporate team slide with Polaroid style",
        "input_schema": GenerateCorporateTeamSlideInput,
    },
}
