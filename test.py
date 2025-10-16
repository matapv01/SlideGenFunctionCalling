from __future__ import annotations

import os
from dotenv import load_dotenv
from litellm import embedding

load_dotenv()

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

response = embedding(model='models/embedding-001', input=["good morning from litellm"])

print(response)