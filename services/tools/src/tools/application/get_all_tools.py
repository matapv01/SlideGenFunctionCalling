from __future__ import annotations

from base import BaseModel
from base import BaseService

from typing import Any
from pydantic import Field
from pydantic import ConfigDict

from typing import Dict
from typing import List

from logger import get_logger

from tool_registry import SlideCategory

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
    total_count: int
    categories: Dict[str, ToolListResponse]

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
        
        for category in SlideCategory:
            cat_response = self.__get_tools_by_category(category)
            if cat_response.count > 0:
                categories_data[category.value] = cat_response
                total_count += cat_response.count
        
        logger.info("Retrieved all tools", extra={"total_count": total_count, "categories_count": len(categories_data)})
        
        return ListToolServiceOutput(
            total_count=total_count,
            categories=categories_data
        )
        
    def __get_tools_by_category(self, category: SlideCategory) -> ToolListResponse:
        """Get all tools in a category."""
        logger.info("Retrieving tools by category", extra={"category": category.value})
        metadatas = self.request.app.state.registry.list_tools_by_category(category)
        tools = [
            ToolInfo(
                name=m.name,
                description=m.description,
                category=m.category.value,
                version=m.version,
                tags=m.tags,
            )
            for m in metadatas
        ]
        logger.info("Retrieved tools by category", extra={"category": category.value, "count": len(tools)})
        return ToolListResponse(
            category=category.value,
            count=len(tools),
            tools=tools
        )
