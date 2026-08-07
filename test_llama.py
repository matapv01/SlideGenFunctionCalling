import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

payload = {
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
}

req = urllib.request.Request(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    data=json.dumps(payload).encode('utf-8'),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req) as response:
        print("Success:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} {e.reason}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
