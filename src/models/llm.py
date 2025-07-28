import os
import time
from typing import List, Dict, Any
import logging

from langchain_openai import ChatOpenAI
# Quan trọng: Cần import các loại lỗi cụ thể từ thư viện openai
import openai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class llm:
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
        
        logger.info(f"LLM class initialized for model '{model}' with {len(self.api_keys)} API keys.")

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
        logger.info(f"ChatOpenAI instance created/updated with API key index: {self.current_key_index}")

    def _rotate_key_and_recreate_instance(self):
        """Rotates to the next API key and recreates the LLM instance."""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.warning(f"Rotating API key. New key index: {self.current_key_index}")
        self._create_llm_instance()

    def invoke(self, prompt: str, tools: List[Dict] = None, max_retries: int = 5, delay: int = 15) -> Any:
        """
        Invokes the LLM with a given prompt, applying retry logic and API key rotation on failure.
        
        Args:
            prompt (str): The input prompt for the model.
            tools (List[Dict], optional): A list of tools to bind for this specific call.
            max_retries (int): The maximum number of retries before giving up.
            delay (int): The delay in seconds between retries.
            
        Returns:
            The content of the LLM response.
            
        Raises:
            RuntimeError: If all retries with all API keys fail.
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # Gắn tools (nếu có) cho lần gọi này
                llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm
                
                logger.info(f"Attempt {attempt + 1}/{max_retries} with API key index {self.current_key_index}...")
                
                # Gọi invoke
                response = llm_with_tools.invoke(prompt)
                
                # Nếu thành công, trả về kết quả ngay lập tức
                return response
            
            # Xử lý các lỗi cụ thể từ OpenAI/Langchain
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit error: {e}. Rotating key and retrying after {delay}s...")
                last_exception = e
                self._rotate_key_and_recreate_instance()
                time.sleep(delay)
                
            except (openai.APIError, openai.APITimeoutError, openai.APIConnectionError) as e:
                logger.error(f"API error on attempt {attempt + 1}: {e}. Retrying after {delay}s...")
                last_exception = e
                # Không cần xoay key cho lỗi timeout hoặc lỗi kết nối, chỉ cần thử lại
                time.sleep(delay)
                
            except Exception as e:
                # Bắt các lỗi không mong muốn khác
                logger.critical(f"An unexpected error occurred: {e}. Rotating key and retrying...")
                last_exception = e
                self._rotate_key_and_recreate_instance()
                time.sleep(delay)

        # Nếu tất cả các lần thử lại đều thất bại
        raise RuntimeError(f"Max retries ({max_retries}) reached. Last error: {last_exception}")

    def stream(self, prompt: str):
        """
        Stream the response from the LLM.
        Lưu ý: Logic retry cho streaming sẽ phức tạp hơn và cần được xử lý riêng.
        """
        return self.llm.stream(prompt)

# # --- VÍ DỤ SỬ DỤNG ---
# if __name__ == "__main__":
#     # Lấy danh sách API keys từ .env (ví dụ: OPENAI_API_KEY_1, OPENAI_API_KEY_2)
#     api_keys = [
#         os.getenv("OPENAI_API_KEY_1"),
#         os.getenv("OPENAI_API_KEY_2"),
#         # Thêm các key khác nếu có
#     ]
#     # Lọc bỏ các key rỗng (nếu có)
#     api_keys = [key for key in api_keys if key]
    
#     if not api_keys:
#         print("Không tìm thấy API key nào trong file .env. Vui lòng đặt OPENAI_API_KEY_1, ...")
#     else:
#         # Khởi tạo lớp LLM
#         llm_instance = LLM(
#             api_keys=api_keys,
#             base_url="https://api.openai.com/v1",  # Hoặc URL của server local
#             model="gpt-3.5-turbo"
#         )

#         # Ví dụ gọi invoke
#         try:
#             prompt = "Hello, world! Tell me a short story."
#             response = llm_instance.invoke(prompt, max_retries=len(api_keys) * 2) # Thử lại 2 lần trên mỗi key
            
#             print("\n--- Response Content ---")
#             print(response.content)

#         except RuntimeError as e:
#             print(f"\nFailed to get response after all retries: {e}")

#         # Ví dụ gọi invoke với tools
#         try:
#             print("\n--- Invoking with tools ---")
#             weather_tool = {
#                 "type": "function",
#                 "function": {
#                     "name": "get_current_weather",
#                     "description": "Get the current weather in a given location",
#                     "parameters": {
#                         "type": "object",
#                         "properties": {
#                             "location": {
#                                 "type": "string",
#                                 "description": "The city and state, e.g. San Francisco, CA",
#                             },
#                             "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
#                         },
#                         "required": ["location"],
#                     },
#                 },
#             }

#             response_with_tool = llm_instance.invoke(
#                 "What is the weather like in Boston?",
#                 tools=[weather_tool]
#             )

#             print("\n--- Response with Tool Call ---")
#             print(response_with_tool)
#             # In ra tool call nếu có
#             if response_with_tool.tool_calls:
#                 print("\nTool Call Detected:")
#                 print(response_with_tool.tool_calls[0])

#         except RuntimeError as e:
#             print(f"\nFailed to get response with tools: {e}")