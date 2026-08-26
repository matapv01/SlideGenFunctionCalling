import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from backend.infrastructure.llm_providers import RemoteLLMProvider
from backend.infrastructure.llm_providers.base import APIConfig

# Cấu hình URL Cloudflare Tunnel từ server Colab/Kaggle của bạn
config = APIConfig()

remote_llm_provider = RemoteLLMProvider(config=config)

# Test 1: Simple prompt completion
prompt = "Xin chào. Trả lời bằng tiếng Việt Nam ngắn gọn."
print("--- TEST 1: Plain Text Completion ---")
try:
    response = remote_llm_provider.generate_completion(prompt)
    print("Response:", response)
except Exception as e:
    print("Test 1 error:", e)

# Test 2: Native Function Calling with tools schema
print("\n--- TEST 2: Native Function Calling with tools=[...] ---")
sample_tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_intro_slide1",
            "description": "Generate an introduction slide with title and author",
            "parameters": {
                "type": "object",
                "properties": {
                    "main_title": {"type": "string", "description": "The main presentation title"},
                    "author": {"type": "string", "description": "Presenter name"}
                },
                "required": ["main_title"]
            }
        }
    }
]

messages = [
    {"role": "system", "content": "You are an AI slide generator. Pick the best tool to format the slide."},
    {"role": "user", "content": "Tạo slide mở đầu cho bài thuyết trình về FPT Corporation."}
]

try:
    response_fc = remote_llm_provider.generate_completion(messages=messages, tools=sample_tools)
    print("Function Calling Response:")
    print(response_fc)
except Exception as e:
    print("Test 2 error:", e)

