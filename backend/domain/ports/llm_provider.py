# File: backend/domain/ports/llm_provider.py

from typing import Any, Dict, List, Protocol

class LLMProvider(Protocol):
    """Interface giao tiếp với các mô hình ngôn ngữ lớn"""
    def __init__(self):
        """
        Khởi tạo LLM Provider, có thể load API key hoặc config cần thiết.
        """
        ...
    async def generate_slide_structure(
        self, 
        title: str, 
        user_prompt: str, 
        slide_constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Sinh cấu trúc slide từ ý tưởng.
        Service không cần biết bên dưới là Gemini, GPT hay Claude.
        Service cũng không cần biết Prompt trông như thế nào.
        """
        ...

    def generate_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 2000,
        temperature: float = 0.5,
        top_p: float = 1.0,
    ) -> str:
        """Sinh text completion dùng chung cho các application service."""
        ...
