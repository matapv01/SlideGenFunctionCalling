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

prompt = "Xin chào. Trả lời bằng tiếng Việt Nam"
response = remote_llm_provider.generate_completion(prompt)
print(response)
