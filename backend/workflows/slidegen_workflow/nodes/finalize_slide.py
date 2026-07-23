# File: src/nodes/finalize_slide.py

from backend.workflows.slidegen_workflow.graph.stage import State
from langchain_core.runnables import RunnableConfig
import time
import os


def finalize_slide(state: State, config: RunnableConfig) -> State:
    """
    Lưu slide đã được chấp nhận và cập nhật context.
    """
    start_time = time.time()
    idx = state['current_slide_index']
    print(f"\n---------------- Executing Node: finalize_slide (Slide {idx + 1}) ----------------")

    # Ghi log thông tin slide
    print(f"Finalizing slide {idx + 1}")
    print(f"HTML path: {state.get('current_html_path', 'N/A')}")
    print(f"Image path: {state.get('current_image_path', 'N/A')}")

    # Thực hiện convert ngay tại đây nếu có conversion_service
    html_path = state.get('current_html_path', '')
    converted_html_path = html_path
    conversion_service = config.get('configurable', {}).get('conversion_service')

    if html_path and os.path.exists(html_path) and conversion_service:
        output_folder = config.get('configurable', {}).get('output_folder')
        if output_folder:
            converted_folder = os.path.join(output_folder, "converted")
            os.makedirs(converted_folder, exist_ok=True)
            converted_path = os.path.join(converted_folder, f"converted_{os.path.basename(html_path)}")

            success = conversion_service.convert_single_slide(html_path, converted_path)
            if success and os.path.exists(converted_path):
                converted_html_path = converted_path
                print(f"✅ Slide {idx + 1} converted successfully on the fly!")
            else:
                print(f"⚠️ Slide {idx + 1} conversion failed or skipped.")

    # Lưu thông tin slide cuối cùng (với đường dẫn HTML đã convert nếu thành công)
    final_slide_data = {
        "index": idx,
        "tool_call": state['current_tool_call'],
        "html_path": converted_html_path,
        "png_path": state.get('current_image_path', ''),
        "original_text": state['current_slide_text']
    }
    state['final_slides'].append(final_slide_data)

    # NOTE: Chunk popping is now handled in next_slide_provider.py for proper sync
    # No need to pop here anymore - it's already been popped when the chunk was selected

    # Emit streaming event for slide completion
    stream_callback = config.get('configurable', {}).get('stream_callback')
    if stream_callback:
        # Extract slide title from text
        slide_text = state.get('current_slide_text', {})
        slide_title = slide_text.get('title', 'Untitled') if isinstance(slide_text, dict) else 'Untitled'

        # Total = slides đã tạo + slides còn lại trong queue
        total_slides = len(state['final_slides']) + len(state.get('slide_chunks', []))
        percentage = (len(state['final_slides']) / total_slides * 100) if total_slides > 0 else 0

        stream_callback('slide_completed', {
            'index': idx,
            'title': slide_title,
            'html_path': converted_html_path,
            'png_path': state.get('current_image_path', ''),
            'current': len(state['final_slides']),
            'total': total_slides
        })

        stream_callback('progress', {
            'current': len(state['final_slides']),
            'total': total_slides,
            'percentage': percentage,
            'title': 'Creating slides',
            'message': f'Completed {len(state["final_slides"])}/{total_slides} slides'
        })
    print(f"Đã thêm slide {idx + 1} vào danh sách final_slides (tổng: {len(state['final_slides'])})")

    # Reset retry_count cho slide tiếp theo
    state['retry_count'] = 0
    print(f"Reset retry_count: {state['retry_count']}")

    state['previous_accepted_tool_call'] = state['current_tool_call']
    end_time = time.time()
    print(f"Finalization of slide took {end_time - start_time:.2f} seconds.")
    return state
