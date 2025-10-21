"""
Service layer for managing slide generation tools.

This module provides a centralized service for managing and discovering
all available slide generation tools from different domains via metadata.
"""

from typing import Optional
from .models import SlideCategory
from .tools import (
    INTRO_TOOLS_INFO,
    TRANSITIONS_TOOLS_INFO,
    CONTENT_TOOLS_INFO,
    TEAM_TOOLS_INFO,
    THANK_YOU_TOOLS_INFO,
)

class ToolRegistryService:
    """
    Service for managing slide generation tool metadata across all domains.
    
    Provides access to tool schemas and metadata from intro, transitions,
    content, team, and thank_you domains.
    """
    
    def __init__(self):
        """Initialize the tool registry service."""
        self._tool_registry = {}
        self._initialized = False
        self.initialize()
    
    def initialize(self) -> None:
        """Initialize and collect all available tool metadata from all domains."""
        if self._initialized:
            return
        
        self._register_intro_tools()
        self._register_transition_tools()
        self._register_content_tools()
        self._register_team_tools()
        self._register_thank_you_tools()
        
        self._initialized = True
    
    def _register_intro_tools(self) -> None:
        """Register all intro slide generation tool metadata."""
        self._tool_registry[SlideCategory.INTRO] = INTRO_TOOLS_INFO
    
    def _register_transition_tools(self) -> None:
        """Register all transition/section header slide generation tool metadata."""
        self._tool_registry[SlideCategory.TRANSITIONS] = TRANSITIONS_TOOLS_INFO
    
    def _register_content_tools(self) -> None:
        """Register all content slide generation tool metadata."""
        self._tool_registry[SlideCategory.CONTENT] = CONTENT_TOOLS_INFO
    
    def _register_team_tools(self) -> None:
        """Register all team slide generation tool metadata."""
        self._tool_registry[SlideCategory.TEAM] = TEAM_TOOLS_INFO
    
    def _register_thank_you_tools(self) -> None:
        """Register all thank you slide generation tool metadata."""
        self._tool_registry[SlideCategory.THANK_YOU] = THANK_YOU_TOOLS_INFO
    
    def get_tools_metadata(self, category: Optional[SlideCategory] = None) -> dict:
        """Get tool metadata, optionally filtered by category."""
        if category:
            return self._tool_registry.get(category, {})
        return self._tool_registry
    
    def get_all_tools(self) -> dict:
        """Get all tools across all categories in flat format."""
        all_tools = {}
        for category_tools in self._tool_registry.values():
            all_tools.update(category_tools)
        return all_tools
    
    def get_tool(self, tool_name: str) -> Optional[dict]:
        """Get a specific tool by name."""
        for category_tools in self._tool_registry.values():
            if tool_name in category_tools:
                return {
                    "name": tool_name,
                    **category_tools[tool_name]
                }
        return None
    
    def search_tools(
        self,
        query: str,
        category: Optional[SlideCategory] = None
    ) -> list:
        """
        Search for relevant tools based on query string and optional category.
        
        Args:
            query: Search query string (searches tool name and description)
            category: Optional category filter
            
        Returns:
            List of matching tools with their metadata
        """
        query_lower = query.lower()
        results = []
        
        # Determine which categories to search
        categories_to_search = [category] if category else list(self._tool_registry.keys())
        
        for cat in categories_to_search:
            tools = self._tool_registry.get(cat, {})
            
            for tool_name, tool_info in tools.items():
                # Check if query matches tool name or description
                name_match = query_lower in tool_name.lower()
                desc_match = query_lower in tool_info.get("description", "").lower()
                
                if name_match or desc_match:
                    results.append({
                        "category": cat.value,
                        "name": tool_name,
                        "description": tool_info.get("description", ""),
                        "input_schema": tool_info.get("input_schema"),
                    })
        
        return results
    
    def get_tools_by_category(self, category: SlideCategory) -> list:
        """Get all tools in a specific category."""
        tools = self._tool_registry.get(category, {})
        return [
            {
                "name": tool_name,
                "description": tool_info.get("description", ""),
                "input_schema": tool_info.get("input_schema"),
            }
            for tool_name, tool_info in tools.items()
        ]
    
    def get_category_stats(self) -> dict:
        """Get statistics about tools across categories."""
        stats = {}
        total = 0
        
        for category, tools in self._tool_registry.items():
            count = len(tools)
            stats[category.value] = count
            total += count
        
        stats["total"] = total
        return stats