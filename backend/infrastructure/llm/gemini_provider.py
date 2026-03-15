# File: backend/infrastructure/llm/gemini_provider.py

import logging
from typing import List, Dict, Any
from backend.domain.ports.llm_provider import LLMProvider
from backend.infrastructure.llm.client import LLMClient

logger = logging.getLogger(__name__)

class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_keys: str = None, base_url: str = None, model: str = None, temperature: float = None, max_tokens: int = None, top_p: float = None, add_stop_token: List[str] = None):
        self.llm_client = LLMClient(
            api_keys=api_keys,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            add_stop_token=add_stop_token
        ).llm
