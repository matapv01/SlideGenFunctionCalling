from __future__ import annotations

from .tools import tool_collections

from base import BaseModel
from base import BaseService

from typing import Dict
from typing import List
from typing import Set
from typing import Any

from litellm import LiteLLMService
from chromadb_client import ChromaDB
from langchain_core.tools import StructuredTool
from .settings import ToolStorageSetting

class ToolStorageInput(BaseModel):

    tool_maps: Dict[str, StructuredTool] = {}

class ToolStorageService(BaseService):

    chromadb: ChromaDB
    litellm: LiteLLMService
    tool_storage_setting: ToolStorageSetting

    def process(self, inputs: ToolStorageInput) -> None:
        pass

    def process(self, inputs: ToolStorageInput) -> None:
        
        for tool_list in tool_collections:
            for tool in tool_list:
                inputs.tool_maps[tool.name] = tool
        

        try:
            existing_ids: Set[str] = set(self.chromadb.collections(
                document_collections=self.tool_storage_setting.collection_name
            ).get(include=[])['ids'])



        except Exception as e:
            existing_ids = set()

        tools_to_embed: List[StructuredTool] = []
        for tool_name, tool in inputs.tool_maps.items():
            if tool_name not in existing_ids:
                tools_to_embed.append(tool)

        if not tools_to_embed:
            return

        try:
            documents = [tool.description for tool in tools_to_embed]
            metadatas = [{"name": tool.name} for tool in tools_to_embed]
            ids = [tool.name for tool in tools_to_embed]
            
            tool_embeddings = self.litellm.embedding(documents)

            self.chromadb.collections(document_collections=self.tool_storage_setting.collection_name).add(
                embeddings=tool_embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            raise

    def discover_tools(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not query:
            return []

        if self.chromadb.collections(document_collections=self.tool_storage_setting.collection_name).count() == 0:
            return []

        try:
            query_embedding = self.litellm.embedding(query)

            results = self.chromadb.collections(document_collections=self.tool_storage_setting.collection_name).query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            tool_definitions: List[Dict[str, Any]] = []
            if 'ids' in results and results['ids']:
                tool_ids = results['ids'][0] 
                
                for tool_id in tool_ids:
                    tool = self.tool_map.get(tool_id)
                    
                    if tool:
                        tool_def = {
                            "name": tool.name,
                            "description": tool.description,
                            "args_schema": tool.args_schema.model_json_schema()
                        }
                        tool_definitions.append(tool_def)
            
            return tool_definitions

        except Exception as e:
            print(f"Lỗi trong quá trình discover_tools: {e}")
            return []