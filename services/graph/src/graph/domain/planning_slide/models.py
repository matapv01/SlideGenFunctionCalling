from __future__ import annotations

from base import BaseModel
from pydantic import Field
from typing import Literal

ToolCategory = Literal['INTRO_TOOLS', 'TRANSITION_TOOLS', 'CONTENT_TOOLS', 'TEAM_TOOLS', 'THANK_YOU_TOOLS']

class SlidePlan(BaseModel):
    """Defines the structure of a slide plan."""
    thought: str = Field(
        description="A detailed creative brief for designing the slide. Describe the desired visual style, color palette, layout, typography, and whether to include images, icons, or specific visual elements. This should be a guide for the next step."
    )
    action: ToolCategory = Field(
        description="The single, most appropriate category of tools to use for generating this slide."
    )