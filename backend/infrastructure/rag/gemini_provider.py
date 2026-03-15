# File: backend/infrastructure/rag/gemini_provider.py

import os
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from collections import deque
import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.domain.ports.tool_retrieve_provider import ToolRetrieveProvider
from langchain_core.documents import Document
from backend import config

class GeminiToolRetrieveProvider(ToolRetrieveProvider):
    def __init__(self, tools_dict: Dict[str, List[Any]], index_path: str, api_key: str = None):
        """
        Initializes the ToolRetriever using Google Generative AI embeddings.

        Args:
            tools_dict (Dict[str, List[Any]]): The dictionary of all tools, categorized.
            index_path (str): Path to the directory where the FAISS index will be saved/loaded.
        """
        print("Initializing ToolRetriever with Google Gemini Embeddings...")

        # The model name is the standard for Gemini embeddings.

        self.embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", google_api_key=api_key)

        self.retrievers = {}
        self.vector_stores: dict = {}
        self.tools_dict = tools_dict
        self.tool_usage_history = {category: deque(maxlen=config.TOOL_RETRIEVER_TEMPORAL_WINDOW * 2) 
                                     for category in tools_dict.keys()}

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
        if not tools: return
        category_index_path = os.path.join(base_index_path, category)
        try:
            print(f"  - Building retriever for category '{category}'...")
            documents = [Document(page_content=tool.description, metadata={"name": tool.name}) for tool in tools]
            vector_store = FAISS.from_documents(documents, self.embeddings)
            self.retrievers[category] = vector_store.as_retriever()
            self.vector_stores[category] = vector_store  # Store for MMR
            vector_store.save_local(folder_path=category_index_path)
            print(f"  - Built and saved retriever for '{category}' at '{category_index_path}'.")
        except Exception as e:
            print(f"  - FAILED to build and save retriever for '{category}': {e}")

    def _apply_temporal_decay(
        self, 
        tool_scores: Dict[str, float],
        category: str,
        current_slide_index: int
    ) -> Dict[str, float]:
        """
        Apply temporal decay penalty to recently used tools.
        
        Args:
            tool_scores: Dict mapping tool_name -> base_score
            category: Tool category
            current_slide_index: Current slide being generated
            
        Returns:
            Dict mapping tool_name -> adjusted_score with temporal penalty applied
        """
        if not config.TOOL_RETRIEVER_ENABLE_TEMPORAL_DECAY:
            return tool_scores
        
        adjusted_scores = {}
        usage_history = self.tool_usage_history.get(category, deque())
        temporal_window = config.TOOL_RETRIEVER_TEMPORAL_WINDOW
        decay_weight = config.TOOL_RETRIEVER_TEMPORAL_DECAY_WEIGHT
        
        for tool_name, base_score in tool_scores.items():
            # Count how many times this tool was used in the temporal window
            recent_usage_count = 0
            
            for used_tool_name, used_slide_index in usage_history:
                if used_tool_name == tool_name:
                    # Check if within temporal window
                    slides_ago = current_slide_index - used_slide_index
                    if 0 < slides_ago <= temporal_window:
                        recent_usage_count += 1
            
            # Apply decay penalty
            if recent_usage_count > 0:
                decay_penalty = 1.0 / (1.0 + decay_weight * recent_usage_count)
                adjusted_score = base_score * decay_penalty
            else:
                adjusted_score = base_score
            
            adjusted_scores[tool_name] = adjusted_score
        
        return adjusted_scores

    def _calculate_mmr_scores(
        self, 
        candidate_docs: List[Document],
        query: str,
        category: str,
        top_k: int,
        lambda_param: float
    ) -> List[str]:
        """
        Apply MMR (Maximal Marginal Relevance) algorithm to select diverse tools.
        
        Args:
            candidate_docs: List of candidate documents from initial retrieval
            query: The original query string
            category: Tool category
            top_k: Number of tools to select
            lambda_param: MMR lambda (0-1, higher = more relevance, lower = more diversity)
            
        Returns:
            List of selected tool names (in order of selection)
        """
        if not config.TOOL_RETRIEVER_ENABLE_MMR or len(candidate_docs) <= top_k:
            # If MMR disabled or not enough candidates, just return top docs
            return [doc.metadata['name'] for doc in candidate_docs[:top_k]]
        
        # Get embeddings for query and all candidates
        try:
            query_embedding = np.array(self.embeddings.embed_query(query))
            
            # Get candidate embeddings from tool descriptions
            candidate_texts = [doc.page_content for doc in candidate_docs]
            candidate_embeddings = np.array([
                self.embeddings.embed_query(text) for text in candidate_texts
            ])
            
            # Calculate initial relevance scores (cosine similarity with query)
            def cosine_similarity(vec1, vec2):
                return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            relevance_scores = [
                cosine_similarity(query_embedding, emb) for emb in candidate_embeddings
            ]
            
            # MMR algorithm
            selected_indices = []
            remaining_indices = list(range(len(candidate_docs)))
            
            # Step 1: Select most relevant document
            best_idx = max(remaining_indices, key=lambda i: relevance_scores[i])
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
            
            # Step 2-K: Select remaining documents balancing relevance and diversity
            while len(selected_indices) < top_k and remaining_indices:
                best_mmr_score = float('-inf')
                best_idx = None
                
                for idx in remaining_indices:
                    # Relevance component
                    relevance = relevance_scores[idx]
                    
                    # Diversity component (max similarity to already selected)
                    max_similarity = max(
                        cosine_similarity(candidate_embeddings[idx], candidate_embeddings[sel_idx])
                        for sel_idx in selected_indices
                    )
                    
                    # MMR score
                    mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity
                    
                    if mmr_score > best_mmr_score:
                        best_mmr_score = mmr_score
                        best_idx = idx
                
                if best_idx is not None:
                    selected_indices.append(best_idx)
                    remaining_indices.remove(best_idx)
            
            # Return selected tool names in order
            return [candidate_docs[idx].metadata['name'] for idx in selected_indices]
        
        except Exception as e:
            print(f"  - MMR calculation failed: {e}. Falling back to simple ranking.")
            return [doc.metadata['name'] for doc in candidate_docs[:top_k]]

    def get_relevant_tools(
        self, 
        category: str, 
        query: str, 
        top_k: int = 5,
        current_slide_index: int = 0
    ) -> List[Any]:
        """
        Get relevant tools using MMR and temporal decay.
        
        Args:
            category: Tool category
            query: Search query (e.g., creative thought from planner)
            top_k: Number of tools to return
            current_slide_index: Current slide index for temporal decay
            
        Returns:
            List of selected tools
        """
        if category not in self.retrievers: 
            return []
        
        # Step 1: Retrieve larger candidate pool
        retriever = self.retrievers[category]
        num_candidates = top_k * config.TOOL_RETRIEVER_CANDIDATE_MULTIPLIER
        candidate_docs = retriever.invoke(query, k=num_candidates)
        
        if not candidate_docs:
            return []
        
        # Step 2: Apply Temporal Decay to initial scores
        # Create initial scores (assuming FAISS returns docs sorted by similarity)
        initial_scores = {
            doc.metadata['name']: 1.0 - (i * 0.01)  # Slight decay for ranking
            for i, doc in enumerate(candidate_docs)
        }
        
        adjusted_scores = self._apply_temporal_decay(
            initial_scores, 
            category, 
            current_slide_index
        )
        
        # Re-sort candidates by adjusted scores
        candidate_docs_sorted = sorted(
            candidate_docs,
            key=lambda doc: adjusted_scores.get(doc.metadata['name'], 0.0),
            reverse=True
        )
        
        # Step 3: Apply MMR for diversity
        selected_tool_names = self._calculate_mmr_scores(
            candidate_docs_sorted,
            query,
            category,
            top_k,
            config.TOOL_RETRIEVER_MMR_LAMBDA
        )
        
        # Step 4: Map back to tool objects
        category_tool_map = {tool.name: tool for tool in self.tools_dict.get(category, [])}
        selected_tools = [category_tool_map[name] for name in selected_tool_names if name in category_tool_map]
        
        return selected_tools

    def record_tool_usage(self, category: str, tool_name: str, slide_index: int):
        """
        Record that a tool was used at a specific slide index.
        This is used for temporal decay penalties.
        
        Args:
            category: Tool category
            tool_name: Name of the tool that was used
            slide_index: Index of the slide where it was used
        """
        if category in self.tool_usage_history:
            self.tool_usage_history[category].append((tool_name, slide_index))
            print(f"  📊 Recorded usage: {tool_name} at slide {slide_index}")
