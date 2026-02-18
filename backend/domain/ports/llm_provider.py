# File: backend/domain/ports/llm_provider.py

from typing import Protocol, List, Dict, Any

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