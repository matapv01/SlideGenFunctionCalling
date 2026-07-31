import os
import sys
import requests
from dotenv import load_dotenv
from openai import OpenAI
def test_nvidia_api():
    # Load .env file
    load_dotenv()
    
    api_key = os.environ.get("NVIDIA_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
    
    if not api_key:
        print("❌ ERROR: NVIDIA_API_KEY is not set in .env file")
        return
        
    print(f"🔄 Testing NVIDIA API...")
    print(f"URL: {base_url}/chat/completions")
    print(f"Model: {model}")
    print("-" * 50)
    
    prompt = "Xin chào, bạn có thể tự giới thiệu ngắn gọn trong 1-2 câu không?"
    print(f"Prompt: {prompt}\n")
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 3000,
        "stream": False
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"].get("content")
        
        print("✅ SUCCESS! API returned:")
        print(f"\n{content}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP ERROR: {e}")
        print(f"Response details: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_openai_sdk_with_nvidia():
    load_dotenv()
    
    api_key = os.environ.get("NVIDIA_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
    
    if not api_key:
        print("❌ ERROR: NVIDIA_API_KEY is not set in .env file")
        return
        
    print(f"🔄 Testing NVIDIA API via OpenAI SDK (chat.completions.create)...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print("-" * 60)
    
    client = OpenAI(base_url=base_url, api_key=api_key)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Nói xin chào bằng tiếng Tây Ban Nha"}
    ]
    
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=500,
        )
        content = resp.choices[0].message.content
        print("✅ SUCCESS! OpenAI SDK returned:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    test_openai_sdk_with_nvidia()
