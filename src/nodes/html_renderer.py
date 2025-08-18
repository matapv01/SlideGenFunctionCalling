# /app/src/nodes/html_renderer.py

import logging
import os
from typing import Dict, Any
import asyncio
from src.tools.tool_des import execute_tool 
from src.stage import State
from src.utils.config import initialize_playwright

async def html_renderer(state: State) -> State:
    """
    Node HTML Renderer: Tạo file HTML từ tool call và chụp ảnh slide.
    """
    retry_count = state.get('retry_count', 0)
    idx = state['current_slide_index']
    print(f"\n---------------- Executing Node: html_renderer (Slide {idx + 1}, Thử lại lần {retry_count}) ----------------")
    await asyncio.sleep(2)  # Reduced sleep time as Playwright is faster
    
    # Lấy nội dung từ tool call
    html_content = state['current_html_content']
    
    # Log thông tin HTML để dễ debug
    print(f"HTML content (first 100 chars): {html_content[:100]}...")
    print(f"HTML content length: {len(html_content)} characters")
    
    # Lấy Playwright instance từ state hoặc khởi tạo lại nếu không có
    playwright_instance = state.get('playwright_instance')
    while not playwright_instance:
        print("Playwright instance không tìm thấy trong state")
        try:
            playwright_instance = await initialize_playwright()
            state['playwright_instance'] = playwright_instance
            print("Đã khởi tạo lại Playwright thành công")
        except Exception as e:
            print(f"Lỗi khi khởi tạo lại Playwright: {e}")
            state['current_html_path'] = ''
            state['current_image_path'] = ''
            return state
    
    # Tạo tên file dựa trên index
    html_filename = f"slide_{idx + 1}.html"
    html_path = os.path.join(state['temp_dir'], "html", html_filename)
    
    # Lưu file HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Đã lưu HTML tại: {html_path}")
    
    # Chụp ảnh slide
    try:
        page = await playwright_instance['context'].new_page()
        # Tải trang HTML
        url = f"file:///{html_path}"
        await page.goto(url)
        
        # Đợi để trang load hoàn toàn
        await page.wait_for_load_state('networkidle')
        
        # Tạo tên file ảnh
        png_filename = f"slide_{idx + 1}.png"
        png_path = os.path.join(state['temp_dir'], "png", png_filename)
        
        # Chụp ảnh
        await page.screenshot(path=png_path, full_page=True)
        print(f"Đã chụp ảnh tại: {png_path}")
        
        # Cập nhật state
        if state.get('current_slide_index') > 0:
            state['previous_image_path'] = state.get('current_image_path', '')
        state['current_html_path'] = html_path
        state['current_image_path'] = png_path
        state['current_html_content'] = html_content

        # Debug info
        if 'temp_debug_dir' in state:
            html_debug_filename = f"slide_{idx + 1}_{retry_count}.html"
            html_debug_path = os.path.join(state['temp_debug_dir'], "html", html_debug_filename)
            os.makedirs(os.path.dirname(html_debug_path), exist_ok=True)
            with open(html_debug_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            png_debug_filename = f"slide_{idx + 1}_{retry_count}.png"
            png_debug_path = os.path.join(state['temp_debug_dir'], "png", png_debug_filename)
            os.makedirs(os.path.dirname(png_debug_path), exist_ok=True)
            await page.screenshot(path=png_debug_path, full_page=True)

            debug_slide_data = {
                "index": idx,
                "tool_call": state.get('current_tool_call', {}),
                "html_path": html_debug_path,
                "png_path": png_debug_path,
                "feedback": state.get('vlm_feedback', ''),
                "retry_count": retry_count
            }
            
            if 'all_debug_info' in state:
                state['all_debug_info'].append(debug_slide_data)
        
        await page.close()
    
    except Exception as e:
        print(f"Lỗi khi chụp ảnh slide: {e}")
        state['current_html_path'] = html_path
        state['current_html_content'] = html_content
    
    return state