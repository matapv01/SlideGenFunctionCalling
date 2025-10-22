from __future__ import annotations

from base import BaseModel
from base import BaseService

from typing import Any
from pydantic import Field
from pydantic import ConfigDict

from  tool_registry import SlideCategory
from litellm import LiteLLMEmbeddingInput

from logger import get_logger

logger = get_logger(__name__)

class SearchToolInput(BaseModel):
    """Input for searching relevant tool."""
    thought: str
    category: SlideCategory
    
class SearchToolOutput(BaseModel):
    """Output for searching relevant tool."""
    tool_names: list
    
class SearchToolService(BaseService):
    """Service to search for relevant tools based on a query."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    request: Any = Field(exclude=True)
    settings: Any = Field(exclude=True)
    
    def process(self, inputs: SearchToolInput) -> SearchToolOutput:
        """Process the search tool request."""
        
        with self.request.app.state.litellm.client as client:
        
            query = self.request.app.state.litellm.embedding(
                client=client,
                inputs=LiteLLMEmbeddingInput(
                    input=inputs.thought,
                    embedding_model=self.settings.litellm.embedding_model,
                    dimensions=self.settings.litellm.dimensions,
                )
            )
        
        relevant_tools = self.request.app.state.registry.search_tools(
            query=query.vector,
            category=inputs.category.value,
            threshold=self.settings.threshold
        )
        
        tool_names = [tool['name'] for tool in relevant_tools]
        
        return SearchToolOutput(tool_names=tool_names)