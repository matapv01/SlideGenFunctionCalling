from __future__ import annotations

from datetime import datetime
from base import BaseService

from typing import Any
from pydantic import Field
from pydantic import ConfigDict

from chromadb_client import ChromaDB
from logger import get_logger

logger = get_logger(__name__)


class ToolGenerationService(BaseService):
    """Service for slide generation business logic."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    request: Any = Field(exclude=True)
    settings: Any = Field(exclude=True)
    
    async def process(
        self,
        request: SlideGenerationRequest,
    ) -> SlideGenerationResponse:
        """
        Generate a slide using specified tool and parameters.
        
        Raises:
            ValueError: If tool not found
            TypeError: If parameters invalid
        """
        logger.info("Starting slide generation process for tool", extra={"tool_name": request.tool_name})
        logger.info("Request parameters received", extra={"params": request.params})
        
        tool_tuple = self.registry.get_tool(request.tool_name)
        
        if not tool_tuple:
            logger.warning("Tool not found in registry", extra={"tool_name": request.tool_name})
            raise ValueError(f"Tool '{request.tool_name}' not found")
        
        func, metadata = tool_tuple
        logger.info("Tool found", extra={"tool_name": request.tool_name, "category": metadata.category.value, "version": metadata.version})
        
        try:
            logger.info("Executing tool", extra={"tool_name": request.tool_name})
            html = func(**request.params)
            logger.info("Successfully generated HTML", extra={"tool_name": request.tool_name, "html_length": len(html)})
            
            return SlideGenerationResponse(
                tool_name=request.tool_name,
                html=html,
                category=metadata.category.value,
                metadata={
                    "generated_at": datetime.utcnow().isoformat(),
                    "version": metadata.version,
                }
            )
        except TypeError as e:
            logger.error("Invalid parameters for tool", extra={"tool_name": request.tool_name, "error": str(e), "params": request.params})
            raise TypeError(f"Invalid parameters: {str(e)}")
        except Exception as e:
            logger.error("Error generating slide", extra={"tool_name": request.tool_name, "error": str(e)})
            raise
    
    def get_tools_by_category(self, category: SlideCategory) -> ToolListResponse:
        """Get all tools in a category."""
        logger.info("Retrieving tools by category", extra={"category": category.value})
        metadatas = self.registry.list_tools_by_category(category)
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
    
    def get_all_tools(self) -> AllToolsResponse:
        """Get all tools grouped by category."""
        logger.info("Retrieving all tools grouped by category")
        categories_data = {}
        total_count = 0
        
        for category in SlideCategory:
            cat_response = self.get_tools_by_category(category)
            if cat_response.count > 0:
                categories_data[category.value] = cat_response
                total_count += cat_response.count
        
        logger.info("Retrieved all tools", extra={"total_count": total_count, "categories_count": len(categories_data)})
        return AllToolsResponse(
            total_count=total_count,
            categories=categories_data
        )
    
    def search_tools(self, query: str, top_k: int = 5) -> ToolListResponse:
        """
        Search tools by query using ChromaDB.
        
        Args:
            query: Search query string
            chromadb_client: ChromaDB client instance
            top_k: Number of results to return
            
        Returns:
            ToolListResponse with matching tools
        """
        try:
            # Get all tools from registry
            all_tools = self.registry.get_all_tools()
            
            # Prepare tool information for searching
            tool_docs = []
            tool_metadatas = []
            
            for tool_name, (func, metadata) in all_tools.items():
                doc = f"{tool_name} {metadata.description}"
                tool_docs.append(doc)
                tool_metadatas.append({
                    "tool_name": tool_name,
                    "category": metadata.category.value,
                })
            
            if not tool_docs:
                return ToolListResponse(category="search", count=0, tools=[])
            
            # Store tools in ChromaDB if not already there
            self.chromadb.store_vector(
                document_collections="tools",
                vectors=None,  # ChromaDB will handle embedding
                metadatas=tool_metadatas,
                ids=list(all_tools.keys()),
                documents=tool_docs,
            )
            
            # Query ChromaDB for similar tools
            # Note: query_embeddings should be embeddings, not text
            # For now, we'll use a simple text search by storing and querying
            results = self.chromadb.collections("tools").query(
                query_texts=[query],
                n_results=top_k,
            )
            
            tool_names = []
            if results.get("ids") and len(results["ids"]) > 0:
                tool_names = results["ids"][0]
            
            # Get tool metadata for results
            tools = []
            for tool_name in tool_names:
                tool_tuple = self.registry.get_tool(tool_name)
                if tool_tuple:
                    func, metadata = tool_tuple
                    tools.append(
                        ToolInfo(
                            name=metadata.name,
                            description=metadata.description,
                            category=metadata.category.value,
                            version=metadata.version,
                            tags=metadata.tags,
                        )
                    )
            
            return ToolListResponse(
                category="search",
                count=len(tools),
                tools=tools
            )
            
        except Exception as e:
            logger.error(f"Error searching tools: {str(e)}")
            raise