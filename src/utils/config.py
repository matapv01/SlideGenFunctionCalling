import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import logging
logger = logging.getLogger(__name__)
import re
from PIL import Image
import io

# Define the character limit as a constant for easy changes
SLIDE_CHAR_LIMIT = 600

def setup_environment():
    """Load environment variables and set API keys and return a dictionary of them."""
    load_dotenv()
    api_keys = {
        "GEMINI_API_KEY": os.getenv('GEMINI_API_KEY'),
        "AQUANG2": os.getenv('AQUANG2'),
        "MATA01": os.getenv('MATA01'),
        "AQUANG1": os.getenv('AQUANG1')
    }
    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = os.getenv('GEMINI_API_KEY')
    if "AQUANG1" not in os.environ:
        os.environ["AQUANG1"] = os.getenv('AQUANG1')
    if "AQUANG2" not in os.environ:
        os.environ["AQUANG2"] = os.getenv('AQUANG2')
    if "MATA01" not in os.environ:
        os.environ["MATA01"] = os.getenv('MATA01')
    
    return api_keys
async def initialize_playwright():
    try:
        playwright = await async_playwright().__aenter__()
        browser = await playwright.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--disable-extensions",
            "--disable-plugins",
        ])
        context = await browser.new_context(
            viewport={"width": 1600, "height": 900},
            device_scale_factor=1
        )
        print("✅ Playwright initialized successfully")
        return {"playwright": playwright, "browser": browser, "context": context}
    except Exception as e:
        print(f"❌ Error initializing Playwright: {e}")
        import traceback; traceback.print_exc()
        return None