# src/utils/config.py
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import shutil
import logging
logger = logging.getLogger(__name__)
import re
import time
from PIL import Image
import io

# Define the character limit as a constant for easy changes
SLIDE_CHAR_LIMIT = 600

def setup_environment():
    """Load environment variables and set API keys and return a dictionary of them."""
    load_dotenv()
    api_keys = {
        "AQUANG2": os.getenv('AQUANG2'),
        "GEMINI_API_KEY": os.getenv('GEMINI_API_KEY'),
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

def initialize_chromedriver():
    try:
        # chrome_driver_path = shutil.which("chromedriver")
        # print(f"🔍 ChromeDriver path: {chrome_driver_path}")
        # if not chrome_driver_path:
        #     raise FileNotFoundError("ChromeDriver not found in PATH.")

        chrome_options = Options()
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")  # Reduce logging noise
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        # Đặt kích thước cửa sổ theo tỷ lệ slide presentation
        chrome_options.add_argument("--window-size=1600,900")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")

        driver = webdriver.Chrome(options=chrome_options)
        
        # Tăng giới hạn thời gian chờ để tránh lỗi timeout
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        
        print("✅ ChromeDriver initialized successfully")
        return driver

    except Exception as e:
        print(f"❌ Error initializing ChromeDriver: {e}")
        import traceback; traceback.print_exc()
        return None
    