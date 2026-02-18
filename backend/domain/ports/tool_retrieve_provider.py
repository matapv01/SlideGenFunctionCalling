# File: backend/domain/ports/tool_retrieve_provider.py

from typing import List, Protocol, Dict, Any, Tuple

class ToolRetrieveProvider(Protocol):
    def __init__(self, tools_dict: Dict[str, List[Any]], index_path: str, api_key: str = None):
        """
        Initializes the ToolRetriever using Google Generative AI embeddings.

        Args:
            tools_dict (Dict[str, List[Any]]): The dictionary of all tools, categorized.
            index_path (str): Path to the directory where the FAISS index will be saved/loaded.
            api_key (str, optional): The API key for Google Generative AI.
        """
        ...
    def _build_and_save_retriever(self, category: str, tools: List[Any], base_index_path: str):
        """
        Builds a retriever for a specific category of tools and saves it to disk.

        Args:
            category (str): The category name for which the retriever is being built.
            tools (List[Any]): The list of tools in this category.
            base_index_path (str): The base directory path where the retriever index will be saved.
        """
        ...
    def retrieve_tools(self, query: str, category: str, top_k: int = 5) -> List[Tuple[str, Any]]:
        """
        Retrieves the most relevant tools for a given query and category.
        Args:
            query (str): The input query for which to find relevant tools.
            category (str): The category of tools to search within.
            top_k (int): The number of top relevant tools to return.
        Returns:
            List[Tuple[str, Any]]: A list of tuples containing tool names and their corresponding details.
        """
        ...