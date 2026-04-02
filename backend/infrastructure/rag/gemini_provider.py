# File: backend/infrastructure/rag/gemini_provider.py

import os
import json
import hashlib
from typing import List, Dict, Any, Tuple
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
        
        # Cache for pre-computed tool description embeddings (used by MMR)
        self._embedding_cache: Dict[str, np.ndarray] = {}

        if getattr(config, 'FAISS_FORCE_REBUILD', False) and os.path.exists(index_path):
            print(f"FAISS_FORCE_REBUILD is True. Deleting old index at '{index_path}' to re-index all tools...")
            import shutil
            shutil.rmtree(index_path)

        if os.path.exists(index_path):
            print(f"Found existing index at '{index_path}'. Checking for updates...")
            for category in tools_dict.keys():
                category_index_path = os.path.join(index_path, category)
                metadata_path = os.path.join(category_index_path, "metadata.json")
                
                if os.path.exists(category_index_path):
                    try:
                        # Always check for incremental updates
                        self._build_and_save_retriever(category, tools_dict[category], index_path)
                        
                        # Load the index (either cached or updated)
                        if category not in self.vector_stores:
                            vector_store = FAISS.load_local(
                                folder_path=category_index_path,
                                embeddings=self.embeddings,
                                allow_dangerous_deserialization=True
                            )
                            self.retrievers[category] = vector_store.as_retriever()
                            self.vector_stores[category] = vector_store
                    except Exception as e:
                        print(f"  - FAILED to process retriever for '{category}': {e}. Will rebuild it.")
                        self._build_and_save_retriever(category, tools_dict[category], index_path)
                else:
                    self._build_and_save_retriever(category, tools_dict[category], index_path)
        else:
            print(f"No index found at '{index_path}'. Building and saving new retrievers...")
            os.makedirs(index_path)
            for category, tools in tools_dict.items():
                self._build_and_save_retriever(category, tools, index_path)

        # Pre-compute and cache all tool description embeddings for MMR
        self._precompute_embeddings()

        print("ToolRetriever initialized successfully.")

    def _build_and_save_retriever(self, category: str, tools: List[Any], base_index_path: str):
        """Build FAISS index for a category with incremental update support."""
        if not tools: return
        
        category_index_path = os.path.join(base_index_path, category)
        metadata_path = os.path.join(category_index_path, "metadata.json")
        
        # Compute current tools metadata (name → hash of description)
        current_tools_meta = {}
        for tool in tools:
            desc_hash = hashlib.md5(tool.description.encode()).hexdigest()
            current_tools_meta[tool.name] = desc_hash
        
        # Load existing metadata if available
        existing_meta = {}
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    existing_meta = json.load(f)
            except:
                pass
        
        # Detect changes
        new_tools = [t for t in tools if t.name not in existing_meta]
        changed_tools = [t for t in tools if t.name in existing_meta and existing_meta.get(t.name) != current_tools_meta[t.name]]
        deleted_tool_names = set(existing_meta.keys()) - set(current_tools_meta.keys())
        
        # If no changes and index exists, skip
        if not new_tools and not changed_tools and not deleted_tool_names and os.path.exists(category_index_path):
            print(f"  - No changes detected for '{category}'. Skipping rebuild.")
            return
        
        print(f"  - Building retriever for category '{category}'...")
        if new_tools:
            print(f"    • {len(new_tools)} new tools")
        if changed_tools:
            print(f"    • {len(changed_tools)} changed tools")
        if deleted_tool_names:
            print(f"    • {len(deleted_tool_names)} deleted tools")
        
        try:
            # Determine if we need full rebuild or can do incremental
            needs_full_rebuild = bool(changed_tools or deleted_tool_names)
            
            if needs_full_rebuild:
                # Full rebuild: changed or deleted tools require rebuilding entire index
                # (FAISS add_documents() only appends, cannot update/delete)
                if changed_tools:
                    print(f"    • {len(changed_tools)} changed tools - full rebuild required")
                if deleted_tool_names:
                    print(f"    • {len(deleted_tool_names)} deleted tools - full rebuild required")
                
                documents = [Document(page_content=tool.description, metadata={"name": tool.name}) for tool in tools]
                vector_store = FAISS.from_documents(documents, self.embeddings)
                print(f"    • Rebuilt index with {len(tools)} tools")
                
            elif new_tools:
                # Incremental: only new tools, can safely append
                vector_store = None
                if os.path.exists(category_index_path):
                    try:
                        vector_store = FAISS.load_local(
                            folder_path=category_index_path,
                            embeddings=self.embeddings,
                            allow_dangerous_deserialization=True
                        )
                        print(f"    • Loaded existing index for incremental update")
                    except Exception as e:
                        print(f"    • Failed to load existing index: {e}. Rebuilding from scratch.")
                        vector_store = None
                
                documents = [Document(page_content=tool.description, metadata={"name": tool.name}) for tool in new_tools]
                
                if vector_store is None:
                    # Create new index
                    vector_store = FAISS.from_documents(documents, self.embeddings)
                else:
                    # Safely append new tools only
                    vector_store.add_documents(documents)
                
                print(f"    • Added {len(new_tools)} new tools to index")
            else:
                # Should not reach here (would have been skipped earlier)
                return
            
            # Save index and metadata
            if vector_store is not None:
                self.retrievers[category] = vector_store.as_retriever()
                self.vector_stores[category] = vector_store
                vector_store.save_local(folder_path=category_index_path)
                with open(metadata_path, 'w') as f:
                    json.dump(current_tools_meta, f, indent=2)
                print(f"  - Built and saved retriever for '{category}' at '{category_index_path}'.")
            
        except Exception as e:
            print(f"  - FAILED to build and save retriever for '{category}': {e}")

    def _precompute_embeddings(self):
        """Pre-compute embeddings for all tool descriptions at init time.
        This avoids expensive per-slide embed_query calls during MMR."""
        print("  - Pre-computing tool description embeddings for MMR cache...")
        for category, tools in self.tools_dict.items():
            for tool in tools:
                if tool.name not in self._embedding_cache:
                    try:
                        emb = np.array(self.embeddings.embed_query(tool.description))
                        self._embedding_cache[tool.name] = emb
                    except Exception as e:
                        print(f"  - WARNING: Failed to embed '{tool.name}': {e}")
        print(f"  - Cached {len(self._embedding_cache)} tool embeddings.")

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
        usage_history: deque[Tuple[str, int]] = self.tool_usage_history.get(category, deque())
        temporal_window = config.TOOL_RETRIEVER_TEMPORAL_WINDOW
        decay_weight = config.TOOL_RETRIEVER_TEMPORAL_DECAY_WEIGHT
        
        for tool_name, base_score in tool_scores.items():
            # Count how many times this tool was used in the temporal window
            recent_usage_count: int = 0
            
            for used_tool_name, used_slide_index in usage_history:
                if used_tool_name == tool_name:
                    # Check if within temporal window
                    slides_ago = int(current_slide_index) - int(used_slide_index)
                    if 0 < slides_ago <= temporal_window:
                        recent_usage_count += 1
            
            # Apply steep exponential decay penalty: e.g. weight=0.5 -> 0.5^1 = 0.5, 0.5^2 = 0.25
            if recent_usage_count > 0:
                decay_factor = float(max(0.01, (1.0 - decay_weight) ** recent_usage_count))
                adjusted_score = float(base_score) * decay_factor
            else:
                adjusted_score = base_score
            
            adjusted_scores[tool_name] = adjusted_score
        
        return adjusted_scores

    def _calculate_mmr_scores(
        self, 
        candidate_names: List[str],
        candidate_scores: Dict[str, float],
        query_embedding: np.ndarray,
        top_k: int,
        lambda_param: float
    ) -> List[str]:
        """
        Apply MMR (Maximal Marginal Relevance) using pre-cached embeddings.
        
        Args:
            candidate_names: List of candidate tool names (pre-sorted by score)
            candidate_scores: Dict mapping tool_name -> similarity score
            query_embedding: The query embedding vector
            top_k: Number of tools to select
            lambda_param: MMR lambda (0-1, higher = more relevance, lower = more diversity)
            
        Returns:
            List of selected tool names (in order of selection)
        """
        if not config.TOOL_RETRIEVER_ENABLE_MMR or len(candidate_names) <= top_k:
            return candidate_names[:top_k]
        
        # Use cached embeddings — no API calls needed
        candidate_embeddings = {}
        valid_candidates = []
        for name in candidate_names:
            if name in self._embedding_cache:
                candidate_embeddings[name] = self._embedding_cache[name]
                valid_candidates.append(name)
            else:
                # Fallback: still include but skip for diversity calc
                valid_candidates.append(name)
        
        top_k_int = int(top_k)
        if len(valid_candidates) <= top_k_int:
            return valid_candidates[:top_k_int]
        
        def cosine_similarity(vec1, vec2):
            norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return float(np.dot(vec1, vec2) / (norm1 * norm2))
        
        # MMR algorithm using cached embeddings
        selected = []
        remaining = list(valid_candidates)
        
        # Step 1: Select most relevant (highest score)
        best = max(remaining, key=lambda n: candidate_scores.get(n, 0.0))
        selected.append(best)
        remaining.remove(best)
        
        # Step 2-K: Balance relevance and diversity
        while len(selected) < top_k and remaining:
            best_mmr_score = float('-inf')
            best_name = None
            
            for name in remaining:
                # Relevance component (normalized score)
                relevance = candidate_scores.get(name, 0.0)
                
                # Diversity component (max similarity to already selected)
                max_sim = 0.0
                if name in candidate_embeddings:
                    for sel_name in selected:
                        if sel_name in candidate_embeddings:
                            sim = cosine_similarity(
                                candidate_embeddings[name],
                                candidate_embeddings[sel_name]
                            )
                            max_sim = max(max_sim, sim)
                
                # MMR score
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
                
                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_name = name
            
            if best_name is not None:
                selected.append(best_name)
                remaining.remove(best_name)
        
        return selected

    def get_relevant_tools(
        self, 
        category: str, 
        query: str, 
        top_k: int = 5,
        current_slide_index: int = 0
    ) -> List[Any]:
        """
        Get relevant tools using FAISS similarity scores, temporal decay, and MMR diversity.
        
        Args:
            category: Tool category
            query: Search query (e.g., creative thought from planner)
            top_k: Number of tools to return
            current_slide_index: Current slide index for temporal decay
            
        Returns:
            List of selected tools
        """
        if category not in self.vector_stores: 
            return []
        
        vector_store = self.vector_stores[category]
        num_candidates = top_k * config.TOOL_RETRIEVER_CANDIDATE_MULTIPLIER
        
        # Step 1: Use similarity_search_with_score for REAL FAISS distances
        try:
            results_with_scores = vector_store.similarity_search_with_score(query, k=num_candidates)
        except Exception as e:
            print(f"  - FAISS search failed: {e}. Falling back to retriever.")
            candidate_docs = self.retrievers[category].invoke(query)
            results_with_scores = [(doc, 1.0) for doc in candidate_docs]
        
        if not results_with_scores:
            return []
        
        # Convert L2 distances to similarity scores (0 to 1)
        # Assuming maximum reasonable L2 distance for normalized embeddings is ~2.0
        # We cap it to avoid negative scores.
        fixed_max_distance = 2.0
        similarity_scores = {}
        for doc, distance in results_with_scores:
            # Score = 1.0 (perfect match) to 0.0 (opposite)
            score = max(0.0, 1.0 - (distance / fixed_max_distance))
            similarity_scores[doc.metadata['name']] = score
        
        # Step 2: Apply Temporal Decay
        adjusted_scores = self._apply_temporal_decay(
            similarity_scores, 
            category, 
            current_slide_index
        )
        
        # Sort candidate names by adjusted scores
        candidate_names = sorted(
            adjusted_scores.keys(),
            key=lambda name: adjusted_scores[name],
            reverse=True
        )
        
        # Step 3: Apply MMR for diversity using cached embeddings
        try:
            query_embedding = np.array(self.embeddings.embed_query(query))
        except Exception as e:
            print(f"  - Query embedding failed: {e}. Skipping MMR.")
            query_embedding = None
        
        if query_embedding is not None:
            selected_tool_names = self._calculate_mmr_scores(
                candidate_names,
                adjusted_scores,
                query_embedding,
                top_k,
                config.TOOL_RETRIEVER_MMR_LAMBDA
            )
        else:
            selected_tool_names = candidate_names[:top_k]
        
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
