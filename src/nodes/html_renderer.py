# File: src/nodes/html_renderer.py

import os
from src.graph.stage import State
from langchain_core.runnables import RunnableConfig
import time


async def render_html(state: State, config: RunnableConfig) -> State:
    """
    Tạo file HTML từ phần raw html text được cung cấp và chụp lại màn hình.
    """

    start_time = time.time()
    idx = state['current_slide_index']
    retry_count = state.get('retry_count', 0)
    print(f"\n---------------- Node HTML Render: Rendering slide thứ {idx + 1}, Thử lại lần {retry_count}) ----------------")

    configurable = config["configurable"]
    playwright_instance = configurable.get('playwright_instance')
    temp_dir = configurable.get('temp_dir')
    temp_debug_dir = configurable.get('temp_debug_dir')

    if not all([playwright_instance, temp_dir]):
        raise ValueError("Missing required resources (playwright, temp_dir) in config.")

    html_content = state['current_html_content']

    # Define paths using resources from config
    html_filename = f"slide_{idx + 1}.html"
    html_path = os.path.join(temp_dir, "html", html_filename)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Đã lưu HTML tại: {html_path}")

    try:
        page = await playwright_instance['context'].new_page()
        url = f"file:///{os.path.abspath(html_path)}"
        await page.goto(url, wait_until="networkidle")

        png_filename = f"slide_{idx + 1}.png"
        png_path = os.path.join(temp_dir, "png", png_filename)

        await page.screenshot(path=png_path, full_page=True)
        print(f"Đã chụp ảnh tại: {png_path}")

        state['current_html_path'] = html_path
        state['current_image_path'] = png_path

        if temp_debug_dir:
            html_debug_path = os.path.join(temp_debug_dir, "html", f"slide_{idx + 1}_{retry_count}.html")
            png_debug_path = os.path.join(temp_debug_dir, "png", f"slide_{idx + 1}_{retry_count}.png")

            with open(html_debug_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            await page.screenshot(path=png_debug_path, full_page=True)

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

        await page.close()

    except Exception as e:
        print(f"Lỗi khi chụp ảnh slide: {e}")
        state['current_html_path'] = html_path

    end_time = time.time()
    print(f"HTML rendering and screenshot took {end_time - start_time:.2f} seconds.")

    return state
