from __future__ import annotations

from enum import Enum
from typing import Dict
from typing import List
from typing import Any

from base import BaseModel
from pydantic import Field

from dataclasses import dataclass


class SlideCategory(str, Enum):
    """Slide categories for organizing tools."""
    
    INTRO = "intro"
    TRANSITIONS = "transitions"
    CONTENT = "content"
    TEAM = "team"
    THANK_YOU = "thank_you"


@dataclass
class SlideToolMetadata:
    """Metadata for a slide generation tool."""
    name: str
    category: SlideCategory
    description: str
    version: str = "1.0.0"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class SlideGenerationRequest(BaseModel):
    """Request to generate a slide."""
    tool_name: str = Field(..., description="Name of the slide tool")
    params: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


class SlideGenerationResponse(BaseModel):
    """Response with generated slide HTML."""
    tool_name: str
    html: str
    category: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolInfo(BaseModel):
    """Information about a tool."""
    name: str
    description: str
    category: str
    version: str
    tags: List[str] = []


class ToolListResponse(BaseModel):
    """Response with list of tools."""
    category: str
    count: int
    tools: List[ToolInfo]


class AllToolsResponse(BaseModel):
    """Response with all tools grouped by category."""
    total_count: int
    categories: Dict[str, ToolListResponse]
