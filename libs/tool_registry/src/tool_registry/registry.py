from __future__ import annotations

from typing import Dict
from typing import List
from typing import Callable
from typing import Optional

from .models import SlideCategory
from .models import SlideToolMetadata


class ToolRegistry:
    """Central registry for all slide generation tools."""
    
    def __init__(self):
        self._tools: Dict[str, tuple[Callable, SlideToolMetadata]] = {}
        self._categories: Dict[SlideCategory, List[str]] = {cat: [] for cat in SlideCategory}
    
    def register(
        self,
        name: str,
        func: Callable,
        category: SlideCategory,
        description: str = "",
        tags: List[str] = None,
        version: str = "1.0.0"
    ) -> None:
        """Register a tool in the registry."""
        metadata = SlideToolMetadata(
            name=name,
            category=category,
            description=description,
            version=version,
            tags=tags or []
        )
        self._tools[name] = (func, metadata)
        self._categories[category].append(name)
    
    def get_tool(self, name: str) -> Optional[tuple[Callable, SlideToolMetadata]]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: SlideCategory) -> Dict[str, tuple[Callable, SlideToolMetadata]]:
        """Get all tools in a category."""
        tool_names = self._categories[category]
        return {name: self._tools[name] for name in tool_names if name in self._tools}
    
    def get_all_tools(self) -> Dict[str, tuple[Callable, SlideToolMetadata]]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def get_category_counts(self) -> Dict[str, int]:
        """Get tool count per category."""
        return {
            cat.value: len([n for n in names if n in self._tools])
            for cat, names in self._categories.items()
        }
    
    def list_tools_by_category(self, category: SlideCategory) -> List[SlideToolMetadata]:
        """List metadata of all tools in a category."""
        return [metadata for _, metadata in self.get_tools_by_category(category).values()]