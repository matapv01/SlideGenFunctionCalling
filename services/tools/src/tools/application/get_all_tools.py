from __future__ import annotations

from base import BaseModel
from base import BaseService

from typing import Any
from pydantic import Field
from pydantic import ConfigDict

from typing import List

from logger import get_logger


logger = get_logger(__name__)

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


class ListToolServiceOutput(BaseModel):
    """Response with all tools grouped by category."""
    all_tools: dict

class ListToolsService(BaseService):
    """Service for slide generation business logic."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    request: Any = Field(exclude=True)
    settings: Any = Field(exclude=True)
    
    def process(self) -> ListToolServiceOutput:
        """Get all tools grouped by category."""
        logger.info("Retrieving all tools grouped by category")
        categories_data = {}
        total_count = 0
        
        all_tools = self.request.app.state.registry.get_all_tools()
        
        logger.info("Retrieved all tools", extra={"total_count": total_count, "categories_count": len(categories_data)})
        
        return ListToolServiceOutput(
            all_tools=all_tools
        )
        