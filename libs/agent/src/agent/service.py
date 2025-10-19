from __future__ import annotations
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from typing import List

class AgentService:
    """
    This class acts as a factory for creating configured LLM client instances.
    Its primary responsibility is to create and return a configured LLM client.
    It also manages API key rotation.
    """
    def __init__(
        self,
        api_keys: List[str],
        base_url: str,
        model: str,
        temperature: float = 0.7,
        top_p: int = 1,
        max_tokens: int = 1024,
        add_stop_token: List[str] = None
    ):
        if not api_keys:
            raise ValueError("API keys list must not be empty")
            
        self.api_keys = api_keys
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.add_stop_token = add_stop_token
        self.current_key_index = 0

    def _get_next_key(self) -> str:
        """
        Get the next API key from the list and rotate the index.
        """
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    def client(self, temperature: float = None, top_p: float = None, max_tokens: int = None) -> BaseChatModel:
        """
        Create and return a new configured ChatOpenAI instance.
        This is the primary factory method.

        Allows overriding some settings with method arguments when needed.
        """
        api_key = self._get_next_key()
        
        final_temp = temperature if temperature is not None else self.temperature
        final_top_p = top_p if top_p is not None else self.top_p
        final_max_tokens = max_tokens if max_tokens is not None else self.max_tokens

        print(f"[AgentService] Creating client with key ending: ...{api_key[-4:]}")
        
        return ChatOpenAI(
            api_key=api_key,
            base_url=self.base_url,
            model=self.model,
            temperature=final_temp,
            max_tokens=final_max_tokens,
            model_kwargs={
                "top_p": final_top_p,
                "stop": self.add_stop_token
            }
        )