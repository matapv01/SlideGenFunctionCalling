import os
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from src.utils import config
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document


class ToolRetriever:
    """
    A retriever for dynamically finding the most relevant tools based on a query.
    It saves the FAISS index to disk to avoid re-calculating embeddings on startup.
    """
    def __init__(self, tools_dict: Dict[str, List[Any]], index_path: str):
        """
        Initializes the ToolRetriever using Google Generative AI embeddings.

        Args:
            tools_dict (Dict[str, List[Any]]): The dictionary of all tools, categorized.
            index_path (str): Path to the directory where the FAISS index will be saved/loaded.
        """
        print("Initializing ToolRetriever with Google Gemini Embeddings...")

        # The model name is the standard for Gemini embeddings.

        env_keys = config.setup_environment()
        api_keys = [v for v in env_keys.values() if v]
        if not api_keys:
            raise RuntimeError("Không có API key hợp lệ trong biến môi trường.")

        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_keys[0])

        self.retrievers = {}
        self.tools_dict = tools_dict

        if os.path.exists(index_path):
            print(f"Found existing index at '{index_path}'. Loading retrievers from disk...")
            for category in tools_dict.keys():
                category_index_path = os.path.join(index_path, category)
                if os.path.exists(category_index_path):
                    try:
                        # --- CHANGE: 'allow_dangerous_deserialization' is often not needed for Google's embeddings ---
                        vector_store = FAISS.load_local(
                            folder_path=category_index_path,
                            embeddings=self.embeddings,
                            allow_dangerous_deserialization=True  # Keep for safety with FAISS
                        )
                        self.retrievers[category] = vector_store.as_retriever()
                        print(f"  - Successfully loaded retriever for '{category}'.")
                    except Exception as e:
                        print(f"  - FAILED to load retriever for '{category}': {e}. Will rebuild it.")
                        self._build_and_save_retriever(category, tools_dict[category], index_path)
                else:
                    self._build_and_save_retriever(category, tools_dict[category], index_path)
        else:
            print(f"No index found at '{index_path}'. Building and saving new retrievers...")
            os.makedirs(index_path)
            for category, tools in tools_dict.items():
                self._build_and_save_retriever(category, tools, index_path)

        print("ToolRetriever initialized successfully.")

    def _build_and_save_retriever(self, category: str, tools: List[Any], base_index_path: str):
        # (This function remains exactly the same)
        if not tools:
            return
        category_index_path = os.path.join(base_index_path, category)
        try:
            print(f"  - Building retriever for category '{category}'...")
            documents = [Document(page_content=tool.description, metadata={"name": tool.name}) for tool in tools]
            vector_store = FAISS.from_documents(documents, self.embeddings)
            self.retrievers[category] = vector_store.as_retriever()
            vector_store.save_local(folder_path=category_index_path)
            print(f"  - Built and saved retriever for '{category}' at '{category_index_path}'.")
        except Exception as e:
            print(f"  - FAILED to build and save retriever for '{category}': {e}")

    def get_relevant_tools(self, category: str, query: str, top_k: int = 5) -> List[Any]:
        # (This function remains exactly the same)
        if category not in self.retrievers:
            return []
        retriever = self.retrievers[category]
        relevant_docs = retriever.invoke(query, k=top_k)
        relevant_tool_names = [doc.metadata['name'] for doc in relevant_docs]
        category_tool_map = {tool.name: tool for tool in self.tools_dict.get(category, [])}
        return [category_tool_map[name] for name in relevant_tool_names if name in category_tool_map]
