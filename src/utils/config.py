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

def setup_environment():
    """Load environment variables and set API keys and return a dictionary of them."""
    load_dotenv()
    api_keys = {
        "GEMINI_API_KEY": os.getenv('GEMINI_API_KEY'),
        # "AQUANG1": os.getenv('AQUANG1'),
        # "AQUANG2": os.getenv('AQUANG2'),
        # "MATA01": os.getenv('MATA01')
    }
    if "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = os.getenv('GEMINI_API_KEY')
    # if "AQUANG1" not in os.environ:
    #     os.environ["AQUANG1"] = os.getenv('AQUANG1')
    # if "AQUANG2" not in os.environ:
    #     os.environ["AQUANG2"] = os.getenv('AQUANG2')
    # if "MATA01" not in os.environ:
    #     os.environ["MATA01"] = os.getenv('MATA01')
    
    return api_keys

def initialize_chromedriver():
    try:
        # chrome_driver_path = shutil.which("chromedriver")
        # print(f"🔍 ChromeDriver path: {chrome_driver_path}")
        # if not chrome_driver_path:
        #     raise FileNotFoundError("ChromeDriver not found in PATH.")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
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
    

def capture_slide_image(driver, html_content, output_path):
    """
    Chụp ảnh slide từ HTML content và lưu vào output_path.
    """
    logger.info(f"Capturing slide image to {output_path}")
    
    # 1. Tạo thư mục tạm để lưu file HTML
    temp_dir = os.path.dirname(output_path)
    temp_html_path = os.path.join(temp_dir, "temporal_slide.html")
    
    try:
        # 2. Xử lý đường dẫn ảnh tương đối cho Linux/Docker
        modified_html = html_content
        
        # Tìm thư mục project hiện tại
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_folder = os.path.join(current_dir, "Image")
        
        # Xử lý đường dẫn tương đối đến thư mục Image
        
        # Pattern 1: src="Image/filename" 
        pattern1 = r'src="Image/([^"]+)"'
        def replace_image_path(match):
            image_name = match.group(1)
            full_image_path = os.path.join(image_folder, image_name)
            if os.path.exists(full_image_path):
                # Sử dụng file:// URI cho Linux
                return f'src="file://{full_image_path}"'
            else:
                logger.warning(f"Image not found: {full_image_path}")
                return match.group(0)
        
        modified_html = re.sub(pattern1, replace_image_path, modified_html)
        
        # Pattern 2: src="filename.png/jpg" (không có thư mục)
        pattern2 = r'src="([^/"]+\.(?:png|jpg|jpeg|gif|bmp|svg))"'
        def replace_image_only_path(match):
            image_name = match.group(1)
            full_image_path = os.path.join(image_folder, image_name)
            if os.path.exists(full_image_path):
                return f'src="file://{full_image_path}"'
            else:
                logger.warning(f"Image not found: {full_image_path}")
                return match.group(0)
        
        modified_html = re.sub(pattern2, replace_image_only_path, modified_html)
        
        # Pattern 3: các đường dẫn tương đối khác (không bắt đầu bằng http, file, data, hoặc /)
        pattern3 = r'src="(?!http|file|data:|/)([^"]+)"'
        def replace_relative_path(match):
            relative_path = match.group(1)
            # Nếu không phải là file ảnh đã xử lý ở trên
            if not re.match(r'[^/]+\.(?:png|jpg|jpeg|gif|bmp|svg)$', relative_path):
                full_path = os.path.join(current_dir, relative_path)
                if os.path.exists(full_path):
                    return f'src="file://{full_path}"'
                else:
                    logger.warning(f"File not found: {full_path}")
            return match.group(0)
        
        modified_html = re.sub(pattern3, replace_relative_path, modified_html)
        
        # 3. Ghi file HTML đã sửa
        with open(temp_html_path, "w", encoding="utf-8") as file:
            file.write(modified_html)
        
        # 4. Load trang và chụp ảnh
        driver.get(f"file://{os.path.abspath(temp_html_path)}")
        driver.set_window_size(1920, 1080)
        
        # Đợi trang load hoàn toàn
        time.sleep(3)
        
        # 5. Chụp ảnh toàn bộ viewport
        screenshot_bytes = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        # Resize về kích thước slide chuẩn giữ nguyên tỷ lệ
        image = image.resize((900, 500), Image.Resampling.LANCZOS)
        image.save(output_path)
        
        # 6. Dọn dẹp file tạm
        os.remove(temp_html_path)
        
        return image
        
    except Exception as e:
        logger.error(f"Error in capture_slide_image: {e}")
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
        raise

