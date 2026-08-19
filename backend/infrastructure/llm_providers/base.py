# File: backend/infrastructure/llm_providers/base.py

"""
LLM Provider Adapters.

Cung cấp interface thống nhất cho việc gọi LLM từ nhiều nguồn:
1. LocalPyTorchLLMProvider : Chạy GPU local (model.generate) dùng cho RL Training (train.py)
2. NvidiaQwenLLMProvider   : Gọi NVIDIA API / vLLM / OpenAI-compatible API
3. GeminiLLMProvider       : Gọi Google Gemini API qua LangChain
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json
import os
from dataclasses import dataclass
import httpx
import logging
import asyncio

logger = logging.getLogger(__name__)


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


class LocalPyTorchLLMProvider(BaseLLMProvider):
    """
    Adapter dành riêng cho RL Training (train.py).
    Thực thi model.generate() trực tiếp trên PyTorch GPU VRAM local.
    """

    def __init__(
        self,
        model: Any,
        tokenizer: Any,
        model_name: str = "Qwen/Qwen3-8B",
        max_completion_length: int = 2048,
        gen_lock: Any = None,
        device: Any = None,
    ):
        super().__init__(provider_name="local_pytorch_qwen", model_type="qwen")
        self.model = model
        self.tokenizer = tokenizer
        self.model_name = model_name        # dùng bởi _get_qwen_config() trong slide_generator
        self.max_completion_length = max_completion_length
        self.gen_lock = gen_lock            # threading.Lock để thread-safe GPU inference
        self.device = device or getattr(model, "device", "cuda")

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 2000,
        temperature: float = 0.0,
    ) -> str:
        import torch

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tools=tools,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=8192).to(self.device)

        # Sử dụng max_completion_length của provider nếu max_tokens không được ghi đè
        effective_max_new_tokens = min(max_tokens, self.max_completion_length)

        import contextlib
        lock_ctx = self.gen_lock if self.gen_lock else contextlib.nullcontext()
        with lock_ctx:
            with torch.no_grad():
                out = self.model.generate(
                    **inputs,
                    max_new_tokens=effective_max_new_tokens,
                    temperature=temperature,
                    do_sample=(temperature > 0.0),
                    pad_token_id=self.tokenizer.eos_token_id,
                )

        completion = self.tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return completion.strip()


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
        llm_bound = self.llm.bind_tools(tools) if tools else self.llm
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


"""
Remote API Client để gọi FastAPI server
"""


@dataclass
class APIConfig:
    """Configuration from environment variables."""
 
    generate_api_url: str = ""
    api_timeout: int = 600
 
    def __post_init__(self):
        env_url = os.getenv("REMOTE_API_URL") or os.getenv("HOST_NAME", "https://mood-forestry-attending-organizations.trycloudflare.com")
        env_url = env_url.rstrip("/")
        if not env_url.endswith("/generate"):
            self.generate_api_url = env_url + "/generate"
        else:
            self.generate_api_url = env_url
 
        if self.api_timeout <= 0:
            raise ValueError("API_TIMEOUT must be positive")
 
    @classmethod
    def from_env(cls):
        return cls()
 
 
class APIError(Exception):
    """Exception for API errors"""
    pass
 
 
class RemoteLLMProvider(BaseLLMProvider):
    """
    Client để gọi remote FastAPI server hosting:
    - LLM Generate model (streaming NDJSON)
    """
 
    def __init__(self, config: Optional[APIConfig] = None):
        super().__init__(provider_name="remote_fastapi_llm", model_type="qwen")
        self.config = config or APIConfig.from_env()
        self.client = httpx.Client(
            timeout=self.config.api_timeout,
            verify=False  # Ignore SSL warnings cho ngrok / cloudflare
        )
        logger.info(f"RemoteLLMProvider initialized with URL={self.config.generate_api_url}")
 
    def _stream_generate(self, payload: Dict[str, Any], endpoint: str) -> str:
        """
        Gửi request tới endpoint streaming NDJSON, đọc từng dòng,
        ghép các 'delta' lại thành câu trả lời hoàn chỉnh.
 
        Mỗi dòng trả về là 1 JSON object độc lập, dạng:
          {"delta": "..."}                      -> mảnh text mới sinh ra
          {"done": true, "answer": "..."}        -> dòng cuối, full text
          {"error": "..."}                       -> server báo lỗi giữa chừng
        """
        full_answer = ""
        try:
            with self.client.stream(
                "POST",
                self.config.generate_api_url,
                json=payload,
                timeout=self.config.api_timeout,
            ) as response:
                response.raise_for_status()
 
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning(f"Bỏ qua dòng NDJSON không parse được: {line[:200]}")
                        continue
 
                    if "error" in data:
                        error_msg = f"API Error ({endpoint}): server báo lỗi khi generate - {data['error']}"
                        logger.error(error_msg)
                        raise APIError(error_msg)
 
                    # Tích lũy text từ các key phổ biến: delta, text, content
                    delta_text = data.get("delta") or data.get("text") or data.get("content") or ""
                    if delta_text:
                        full_answer += delta_text

                    if data.get("done"):
                        # Chỉ lấy data["answer"] nếu nó thực sự có nội dung (không rỗng)
                        final_ans = data.get("answer")
                        if final_ans and isinstance(final_ans, str) and final_ans.strip():
                            full_answer = final_ans
 
            return full_answer
 
        except httpx.HTTPStatusError as e:
            error_msg = f"API Error ({endpoint}): {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise APIError(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Connection Error ({endpoint}): {str(e)}"
            logger.error(error_msg)
            raise APIError(error_msg) from e
 
    def generate_completion(
        self,
        messages: Any,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Gọi /generate endpoint (streaming NDJSON) để generate text.
        Chấp nhận `messages` dạng List[Dict] hoặc chuỗi string `prompt`.
 
        Args:
            messages: Prompt string hoặc List các message dict
            tools: Danh sách tools (nếu có)
            max_tokens: Số token tối đa
            temperature: Sampling temperature
 
        Returns:
            Generated text string (đã ghép đầy đủ từ stream)
        """
        if isinstance(messages, str):
            prompt = messages
        elif isinstance(messages, list):
            prompt_parts = []
            for msg in messages:
                if isinstance(msg, dict):
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    prompt_parts.append(f"{role.capitalize()}: {content}")
                else:
                    prompt_parts.append(str(msg))
            prompt = "\n".join(prompt_parts)
        else:
            prompt = str(messages)
 
        if not prompt:
            raise ValueError("prompt must not be empty")
 
        logger.debug(f"Generating with prompt: {prompt[:50]}")
 
        try:
            payload = {
                "prompt": prompt,
                "max_length": max_tokens,
                "temperature": temperature,
            }
            answer = self._stream_generate(payload, "generate")
            logger.debug(f"Generated text length: {len(answer)}")
            return answer
 
        except APIError:
            raise
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise
    async def _stream_generate_async(
        self,
        async_client: httpx.AsyncClient,
        payload: Dict[str, Any],
        endpoint: str,
    ) -> str:
        full_answer = ""
        try:
            async with async_client.stream(
                "POST",
                self.config.generate_api_url,
                json=payload,
                timeout=self.config.api_timeout,
            ) as response:
                response.raise_for_status()
 
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
 
                    if "error" in data:
                        raise APIError(f"API Error ({endpoint}): {data['error']}")
 
                    if "delta" in data:
                        full_answer += data["delta"]
 
                    if data.get("done"):
                        full_answer = data.get("answer", full_answer)
 
            return full_answer
 
        except httpx.HTTPStatusError as e:
            raise APIError(f"API Error ({endpoint}): {e.response.status_code} - {e.response.text}") from e
        except httpx.RequestError as e:
            raise APIError(f"Connection Error ({endpoint}): {str(e)}") from e
 
    async def _generate_batch_async(
        self,
        prompts: List[str],
        max_tokens: int = 500,
        temperature: float = 0.7,
        max_concurrency: int = 8,
    ) -> List[str]:
        semaphore = asyncio.Semaphore(max_concurrency)
 
        async with httpx.AsyncClient(timeout=self.config.api_timeout, verify=False) as async_client:
 
            async def run_one(prompt: str) -> str:
                async with semaphore:  # giới hạn số request bắn cùng lúc, tránh vượt KV cache
                    payload = {
                        "prompt": prompt,
                        "max_length": max_tokens,
                        "temperature": temperature,
                    }
                    return await self._stream_generate_async(async_client, payload, "generate_batch")
 
            tasks = [run_one(p) for p in prompts]
            return await asyncio.gather(*tasks)
 
    def generate_batch(
        self,
        prompts: List[str],
        max_tokens: int = 500,
        temperature: float = 0.7,
        max_concurrency: int = 15,
    ) -> List[str]:
        """
        Sinh text cho NHIỀU prompt cùng lúc (đồng thời), để vLLM continuous-batch
        chúng trên GPU thay vì xử lý tuần tự từng cái một.
 
        Dùng khi cần sinh nội dung cho nhiều slide/nhiều mục cùng lúc.
 
        Args:
            prompts: danh sách các prompt cần sinh
            max_tokens, temperature: giống generate_completion
            max_concurrency: số request tối đa bắn đồng thời (nên đặt <= giá trị
                "Maximum concurrency" mà vLLM log lúc khởi động, để tránh OOM KV cache)
 
        Returns:
            List[str] kết quả, ĐÚNG THỨ TỰ với prompts đầu vào
        """
        return asyncio.run(
            self._generate_batch_async(prompts, max_tokens, temperature, max_concurrency)
        )