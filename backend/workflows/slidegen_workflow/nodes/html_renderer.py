# File: backend/workflows/slidegen_workflow/nodes/html_renderer.py

import os
import time
import shutil
from backend.workflows.slidegen_workflow.graph.stage import State
from langchain_core.runnables import RunnableConfig

# 🟢 REFACTOR: Không còn import Playwright ở đây.
# Node này giao việc chụp ảnh cho CaptureProvider.

async def render_html(state: State, config: RunnableConfig) -> State:
    """
    Node: HTML Renderer
    Responsibility: Save raw HTML and delegate screenshotting to the CaptureProvider.
    """
    start_time = time.time()
    idx = state['current_slide_index']
    retry_count = state.get('retry_count', 0)
    print(f"\n---------------- Node HTML Render: Rendering slide thứ {idx + 1}, Thử lại lần {retry_count} ----------------")

    # 1. Get Dependencies from Config
    configurable = config["configurable"]
    capture_provider = configurable.get('capture_provider') # 🟢 Dùng CaptureProvider
    temp_dir = configurable.get('temp_dir')
    temp_debug_dir = configurable.get('temp_debug_dir')

    if not all([capture_provider, temp_dir]):
        raise ValueError("Missing required resources (capture_provider, temp_dir) in config.")

    html_content = state['current_html_content']

    # 2. Define standard paths
    html_filename = f"slide_{idx + 1}.html"
    html_path = os.path.join(temp_dir, "html", html_filename)
    png_filename = f"slide_{idx + 1}.png"
    png_path = os.path.join(temp_dir, "png", png_filename)

    # 3. Save HTML to disk
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Đã lưu HTML tại: {html_path}")

    try:
        # 4. 🟢 DELEGATE TO INFRASTRUCTURE
        # Gọi CaptureProvider. Trả về đúng đường dẫn file PNG.
        await capture_provider.generate_slide_from_html(html_content, png_path)
        print(f"Đã chụp ảnh tại: {png_path}")

        state['current_html_path'] = html_path
        state['current_image_path'] = png_path

        # 5. Handle Debug Info (Tối ưu hóa tốc độ)
        if temp_debug_dir:
            html_debug_path = os.path.join(temp_debug_dir, "html", f"slide_{idx + 1}_{retry_count}.html")
            png_debug_path = os.path.join(temp_debug_dir, "png", f"slide_{idx + 1}_{retry_count}.png")

            # Thay vì chụp màn hình lần 2 gây chậm, ta chỉ việc copy file đã render!
            shutil.copy2(html_path, html_debug_path)
            if os.path.exists(png_path):
                shutil.copy2(png_path, png_debug_path)

            debug_info = state.get("all_debug_info", [])
            debug_info.append({
                "index": idx,
                "tool_call": state.get('current_tool_call', {}),
                "html_path": html_debug_path,
                "png_path": png_debug_path,
                "feedback": state.get('vlm_feedback', ''),
                "retry_count": retry_count
            })
            state['all_debug_info'] = debug_info

    except Exception as e:
        print(f"❌ Lỗi khi chụp ảnh slide: {e}")
        # Vẫn lưu lại HTML path dù có lỗi chụp ảnh để không làm gãy hoàn toàn flow
        state['current_html_path'] = html_path

    end_time = time.time()
    print(f"HTML rendering and screenshot took {end_time - start_time:.2f} seconds.")

    return state
