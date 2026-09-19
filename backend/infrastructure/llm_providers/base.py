# File: backend/infrastructure/llm_providers/base.py

"""
LLM Provider Adapters.

Cung cấp interface thống nhất cho việc gọi LLM từ nhiều nguồn:
1. NvidiaQwenLLMProvider   : Gọi NVIDIA API / vLLM / OpenAI-compatible API
2. GeminiLLMProvider       : Gọi Google Gemini API qua LangChain
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json


class BaseLLMProvider(ABC):
    """Abstract Base Class cho tất cả LLM Providers trong hệ thống."""

    def __init__(self, provider_name: str, model_type: str = "qwen"):
        self.provider_name = provider_name
        self.model_type = model_type  # "qwen" hoặc "gemini"

    @abstractmethod
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.5,
    ) -> str:
        """Sinh chuỗi completion text từ messages và tools."""
        pass

    def invoke(self, input_data: Any, config: Optional[Any] = None, **kwargs) -> Any:
        """Alias cho LangChain interface compatibility."""
        if isinstance(input_data, list):
            messages = input_data
        elif isinstance(input_data, str):
            messages = [{"role": "user", "content": input_data}]
        elif isinstance(input_data, dict):
            messages = [input_data]
        else:
            messages = [{"role": "user", "content": str(input_data)}]
            
        content = self.generate_completion(messages=messages)
        
        class ProviderAIMessage:
            def __init__(self, text):
                self.content = text
        return ProviderAIMessage(content)


class NvidiaQwenLLMProvider(BaseLLMProvider):
    """
    Adapter cho NVIDIA NIM API / vLLM / OpenAI-compatible API endpoints.
    """

    def __init__(self, model_name: str, base_url: str, api_key: str):
        super().__init__(provider_name="nvidia_qwen_api", model_type="qwen")
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key

        from openai import OpenAI
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.5,
    ) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            print(f"⚠️ NvidiaQwenLLMProvider error: {e}")
            return ""


class GeminiAPIProvider(BaseLLMProvider):
    """
    Adapter cho Google Gemini API.
    Tái sử dụng LLMClient / GeminiLLMProvider cũ từ backend/infrastructure/llm/
    """

    def __init__(
        self,
        langchain_llm: Any = None,
        api_keys: Optional[List[str]] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.5,
    ):
        super().__init__(provider_name="google_gemini_api", model_type="gemini")
        if langchain_llm:
            self.llm = langchain_llm
        elif api_keys:
            from backend.infrastructure.llm.client import LLMClient
            self.llm = LLMClient(
                api_keys=api_keys if isinstance(api_keys, list) else [api_keys],
                base_url=base_url,
                model=model or "gemini-2.5-pro",
                temperature=temperature,
            ).llm
        else:
            raise ValueError("Cần truyền langchain_llm hoặc api_keys cho GeminiLLMProvider.")

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.5,
    ) -> str:
        # Every caller that supplies tools expects a tool invocation, not a
        # prose answer.  Leaving the choice on ``auto`` lets Gemini return
        # ordinary text under load or after a retry prompt, which the slide
        # workflow cannot execute.
        llm_bound = (
            self.llm.bind_tools(tools, tool_choice="required")
            if tools
            else self.llm
        )
        resp = llm_bound.invoke(messages)
        
        # Nếu Gemini trả về native tool_calls qua LangChain AIMessage
        if hasattr(resp, "tool_calls") and resp.tool_calls:
            tool_plan = [
                {
                    "name": tc.get("name"),
                    "arguments": tc.get("args", {}),
                }
                for tc in resp.tool_calls
            ]
            return json.dumps({"tool_calls": tool_plan}, ensure_ascii=False)
            
        return getattr(resp, "content", "") or ""
