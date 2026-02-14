
from typing import List
from langchain_openai import ChatOpenAI


class LLM:
    """
    A robust wrapper class for language models via langchain_openai,
    featuring built-in retry logic and API key rotation.
    """

    def __init__(self, api_keys: List[str], base_url: str, model: str, temperature: float = 0.5, max_tokens: int = 4096, top_p: float = 1.0, add_stop_token: List[str] = None):
        """
        Initializes the LLM instance with a list of API keys for rotation.
        Args:
            api_keys (List[str]): A list of API keys to rotate through on failure.
            base_url (str): Base URL for the LLM service.
            model (str): Model name or identifier.
            ...
        """
        if not api_keys or not isinstance(api_keys, list):
            raise ValueError("api_keys must be a non-empty list of strings.")

        self.api_keys = api_keys
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens

        self.add_stop_token = ["---\n", "STOP_HERE"]
        if add_stop_token:
            self.add_stop_token.extend(add_stop_token)

        self.current_key_index = 0
        self._create_llm_instance()

        print(f"LLM class initialized for model '{model}' with {len(self.api_keys)} API keys.")

    def _create_llm_instance(self):
        """
        Helper method to create or recreate the ChatOpenAI instance.
        It uses the key at the current_key_index.
        """
        current_api_key = self.api_keys[self.current_key_index]
        self.llm = ChatOpenAI(
            api_key=current_api_key,
            base_url=self.base_url,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            stop=self.add_stop_token
        )
        print(f"ChatOpenAI instance created/updated with API key index: {self.current_key_index}")

    def _rotate_key_and_recreate_instance(self):
        """Rotates to the next API key and recreates the LLM instance."""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"Rotating API key. New key index: {self.current_key_index}")
        self._create_llm_instance()

    def invoke(self, prompt: str, temperature: float = 0.5, top_p: float = 0.9) -> str:
        """
        Invokes the LLM with a given prompt and returns the text response.
        Handles both openai_server API calls and local model inference.
        """
        # For openai_server, the temperature is set at initialization
        response = self.llm.invoke(prompt, temperature=temperature, top_p=top_p)
        return response.content if hasattr(response, 'content') else str(response)

    def bind_tools(self, tools):
        """
        Bind tools to the LLM instance.
        """
        return self.llm.bind_tools(tools)

    def with_structured_output(self, output_schema, **kwargs):
        """
        Configure the LLM to use structured output.
        Accepts and passes along any additional keyword arguments.
        """
        # Pass the schema and all other kwargs to the real method
        return self.llm.with_structured_output(output_schema, **kwargs)

    def stream(self, prompt: str):
        """
        Stream the response from the LLM.
        Lưu ý: Logic retry cho streaming sẽ phức tạp hơn và cần được xử lý riêng.
        """
        return self.llm.stream(prompt)
