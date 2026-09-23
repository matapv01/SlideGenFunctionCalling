# File: backend/infrastructure/llm/gemini_provider.py

import logging
from typing import Any, Dict, List
from backend.domain.ports.llm_provider import LLMProvider
from backend.infrastructure.llm.client import LLMClient
from backend.infrastructure.llm.request_limiter import LLMRequestLimiter

logger = logging.getLogger(__name__)

class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_keys: str = None, base_url: str = None, model: str = None, temperature: float = None, max_tokens: int = None, top_p: float = None, add_stop_token: List[str] = None, request_limiter: LLMRequestLimiter | None = None, request_timeout: float | None = None):
        self.request_limiter = request_limiter
        self.request_timeout = request_timeout
        self.llm_client = LLMClient(
            api_keys=api_keys,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            add_stop_token=add_stop_token,
            timeout=request_timeout,
        ).llm

    def generate_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 2000,
        temperature: float = 0.5,
        top_p: float = 1.0,
    ) -> str:
        """Reuse the configured LangChain client for plain text responses."""
        overrides = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }
        if model:
            overrides["model"] = model
        llm = self.llm_client.bind(**overrides)
        if tools:
            llm = llm.bind_tools(tools)
        if self.request_limiter is None:
            response = llm.invoke(messages)
        else:
            with self.request_limiter.slot(timeout=self.request_timeout):
                response = llm.invoke(messages)
        content = getattr(response, "content", "") or ""
        if isinstance(content, list):
            content = "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in content
            )
        return str(content).strip()
