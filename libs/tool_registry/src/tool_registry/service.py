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
import numpy as np
from litellm import LiteLLMService
from litellm import LiteLLMEmbeddingInput


class ToolRegistryService:
    """
    Service for managing slide generation tool metadata across all domains.
    
    Provides access to tool schemas and metadata from intro, transitions,
    content, team, and thank_you domains.
    """
    
    def __init__(self, litellm_service: LiteLLMService):
        """Initialize the tool registry service.
        
        Args:
            litellm_service: LiteLLM service for generating embeddings
        """
        self._tool_registry = {}
        self._initialized = False
        self._tool_embeddings = {}  # Cache for tool embeddings
        self._litellm_service = litellm_service
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
        
        # Generate embeddings for all tools if litellm service is available
        self._generate_tool_embeddings()
        
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
    
    def _convert_category(self, category: Optional[str]) -> Optional[SlideCategory]:
        """
        Convert string category to SlideCategory enum.
        
        Args:
            category: Category as string (e.g., 'intro', 'content')
            
        Returns:
            SlideCategory enum or None
        """
        if category is None:
            return None
        
        try:
            return SlideCategory(category.lower())
        except ValueError:
            raise ValueError(f"Invalid category: {category}. Must be one of {[c.value for c in SlideCategory]}")
    
    def search_tools(
        self,
        query: list,
        threshold: float,
        category: str | None = None
    ) -> list:
        """
        Search for relevant tools using vector embedding similarity.
        
        Args:
            query: Query embedding vector (list of floats)
            category: Optional category filter as string (e.g., 'intro', 'content', 'team')
            threshold: Minimum similarity score (0-1) to include results
            
        Returns:
            List of matching tools with their metadata, sorted by similarity score
        """
        if not isinstance(query, (list, np.ndarray)):
            raise ValueError("Query must be an embedding vector (list or numpy array)")
        
        # Convert string category to enum if provided
        category_enum = self._convert_category(category)
        
        query_vector = np.array(query)
        results = []
        
        # Determine which categories to search
        categories_to_search = [category_enum] if category_enum else list(self._tool_registry.keys())
        
        for cat in categories_to_search:
            tools = self._tool_registry.get(cat, {})
            
            for tool_name, tool_info in tools.items():
                # Get or create tool text representation for embedding
                tool_text = self._get_tool_representation(tool_name, tool_info)
                
                # Calculate similarity
                similarity = self._calculate_similarity(query_vector, tool_text, cat, tool_name)
                
                # Filter by threshold
                if similarity >= threshold:
                    results.append({
                        "category": cat.value,
                        "name": tool_name,
                        "description": tool_info.get("description", ""),
                        "input_schema": tool_info.get("input_schema"),
                        "similarity_score": similarity
                    })
        
        # Sort by similarity score in descending order
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return results
    
    def _get_tool_representation(self, tool_name: str, tool_info: dict) -> str:
        """
        Get text representation of a tool for embedding.
        
        Args:
            tool_name: Name of the tool
            tool_info: Tool metadata dictionary
            
        Returns:
            Combined text representation of the tool
        """
        parts = [
            tool_name.lower(),
            tool_info.get("description", "").lower(),
        ]
        
        # Add tags if available
        if "tags" in tool_info and tool_info["tags"]:
            parts.extend([tag.lower() for tag in tool_info["tags"]])
        
        return " ".join(filter(None, parts))
    
    def _generate_tool_embeddings(self) -> None:
        """
        Generate embeddings for all tools using the LiteLLM service.
        """
        # Generate embeddings for each tool individually
        for category, tools in self._tool_registry.items():
            for tool_name, tool_info in tools.items():
                tool_text = self._get_tool_representation(tool_name, tool_info)
                
                # Generate embedding for this tool
                with self._litellm_service.client as client:
                    embedding_result = self._litellm_service.embedding(
                        client=client,
                        inputs=LiteLLMEmbeddingInput(
                            input=tool_text,
                            embedding_model=self._litellm_service.embedding_model,
                            dimensions=self._litellm_service.dimensions,
                        )
                    )
                
                # Store embedding
                self._tool_embeddings[(category, tool_name)] = np.array(embedding_result.vector)
    
    def _calculate_similarity(self, query_vector: np.ndarray, tool_text: str, category: SlideCategory, tool_name: str) -> float:
        """
        Calculate cosine similarity between query embedding and tool embedding.
        
        Args:
            query_vector: Query embedding vector
            tool_text: Text representation of the tool (fallback)
            category: Tool category
            tool_name: Tool name
            
        Returns:
            Similarity score between 0 and 1
        """
        # Use cached embedding if available
        tool_key = (category, tool_name)
        if tool_key in self._tool_embeddings:
            tool_vector = self._tool_embeddings[tool_key]
            
            # Calculate cosine similarity
            query_norm = np.linalg.norm(query_vector)
            tool_norm = np.linalg.norm(tool_vector)
            
            if query_norm == 0 or tool_norm == 0:
                return 0.0
            
            similarity = np.dot(query_vector, tool_vector) / (query_norm * tool_norm)
            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, (similarity + 1) / 2))
        
            
        with self._litellm_service.client as client:
            tool_embedding_result = self._litellm_service.embedding(
                client=client,
                inputs=LiteLLMEmbeddingInput(
                    input=tool_text,
                    embedding_model=self._litellm_service.embedding_model,
                    dimensions=self._litellm_service.dimensions,
                )
            )
        
        tool_vector = np.array(tool_embedding_result.vector)
        
        # Calculate cosine similarity
        query_norm = np.linalg.norm(query_vector)
        tool_norm = np.linalg.norm(tool_vector)
        
        if query_norm == 0 or tool_norm == 0:
            return 0.0
        
        similarity = np.dot(query_vector, tool_vector) / (query_norm * tool_norm)
        return max(0.0, min(1.0, (similarity + 1) / 2))
        
    def get_tools_by_category(self, category: str) -> list:
        """Get all tools in a specific category.
        
        Args:
            category: Category as string (e.g., 'intro', 'content')
            
        Returns:
            List of tools in the category
        """
        category_enum = self._convert_category(category)
        tools = self._tool_registry.get(category_enum, {})
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