# /app/src/nodes/html_renderer.py (ĐÃ SỬA)

import logging
import os
from typing import Dict, Any
import time

# Import hàm thực thi tool duy nhất
from src.tools.tool_des import execute_tool 
from src.stage import State
from src.utils.config import capture_slide_image 

def html_renderer(state: State) -> State:
    """
    Node HTML Renderer: Tạo file HTML từ tool call và cap ảnh slide.
    """
    retry_count = state.get('retry_count', 0)
    idx = state['current_slide_index']
    print(f"\n---------------- Executing Node: html_renderer (Slide {idx + 1}, Thử lại lần {retry_count}) ----------------")
    time.sleep(20)
    
    # Lấy nội dung từ tool call
    html_content = state['current_html_content']
    
    # Log thông tin HTML để dễ debug
    print(f"HTML content (first 100 chars): {html_content[:100]}...")
    print(f"HTML content length: {len(html_content)} characters")
    
    # Lấy driver từ state hoặc khởi tạo lại nếu không có
    driver = state.get('driver')
    if not driver:
        print("Driver không tìm thấy trong state, có thể đã bị đóng")
        
        # Cố gắng khởi tạo lại driver một cách an toàn
        try:
            # Sử dụng phương thức khởi tạo ChromeDriver trực tiếp
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Thiết lập tùy chọn cho Chrome
            chrome_options = Options()
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1600,900")
            
            # Khởi tạo driver
            try:
                driver = webdriver.Chrome(options=chrome_options)
                # Lưu driver mới vào state
                state['driver'] = driver
                print("Đã khởi tạo lại ChromeDriver thành công")
            except Exception as e:
                print(f"Không thể khởi tạo Chrome trực tiếp: {e}")
                # Thêm thông tin HTML vào state và tiếp tục mà không có driver
                state['current_html_content'] = html_content
                state['current_html_path'] = ''
                state['current_image_path'] = ''
                return state
        except Exception as e:
            print(f"Lỗi khi khởi tạo lại ChromeDriver: {e}")
            # Thêm thông tin HTML vào state và tiếp tục mà không có driver
            state['current_html_content'] = html_content
            state['current_html_path'] = ''
            state['current_image_path'] = ''
            return state
    
    # Tạo tên file dựa trên index và số lần thử
    html_filename = f"slide_{idx + 1}_{retry_count}.html"
    html_path = os.path.join(state['temp_dir'], "html", html_filename)
    
    # Lưu file HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Đã lưu HTML tại: {html_path}")
    
    # Chụp ảnh slide
    try:
        # Tải trang HTML
        url = f"file:///{html_path}"
        driver.get(url)
        
        # Đợi một chút để trang load
        time.sleep(1)
        
        # Tạo tên file ảnh
        png_filename = f"slide_{idx + 1}_{retry_count}.png"
        png_path = os.path.join(state['temp_dir'], "png", png_filename)
        
        # Chụp ảnh
        driver.save_screenshot(png_path)
        print(f"Đã chụp ảnh tại: {png_path}")
        
        # Cập nhật state với đường dẫn
        state['current_html_path'] = html_path
        state['current_image_path'] = png_path
        state['current_html_content'] = html_content
        
    except Exception as e:
        print(f"Lỗi khi chụp ảnh slide: {e}")
        # Vẫn lưu đường dẫn HTML
        state['current_html_path'] = html_path
        state['current_html_content'] = html_content
    
    return state