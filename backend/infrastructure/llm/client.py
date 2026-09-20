# File: backend/infrastructure/llm/client.py

from typing import List
from langchain_openai import ChatOpenAI

class LLMClient: # Đổi tên thành Client cho rõ nghĩa
    """
    A robust wrapper class for language models via langchain_openai,
    featuring built-in retry logic and API key rotation.
    """
    def __init__(self, api_keys: List[str], base_url: str, model: str, temperature: float = 0.5, max_tokens: int = 4096, top_p: float = 1.0, add_stop_token: List[str] = None, timeout: float | None = None):
        if not api_keys or not isinstance(api_keys, list):
            raise ValueError("api_keys must be a non-empty list of strings.")

        self.api_keys = api_keys
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.add_stop_token = ["---\n", "STOP_HERE"]
        if add_stop_token:
            self.add_stop_token.extend(add_stop_token)

        self.current_key_index = 0
        current_api_key = self.api_keys[self.current_key_index]
        client_options = {
            "api_key": current_api_key,
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stop": self.add_stop_token,
        }
        if timeout is not None:
            client_options["timeout"] = max(1.0, float(timeout))
        self.llm = ChatOpenAI(
            **client_options
        )
