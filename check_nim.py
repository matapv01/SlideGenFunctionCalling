import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

req = urllib.request.Request(
    "https://integrate.api.nvidia.com/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)

try:
    with urllib.request.urlopen(req) as response:
        models = json.loads(response.read())
        print([m["id"] for m in models.get("data", [])])
except Exception as e:
    print("Error:", e)
