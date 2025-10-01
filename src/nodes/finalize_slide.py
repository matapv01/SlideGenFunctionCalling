
from src.graph.stage import State
from typing import Dict, Any
import time

def finalize_slide(state: State) -> Dict[str, Any]:
    """
    Node hoàn tất: Lưu slide đã được chấp nhận và cập nhật context.
    """
    start_time = time.time()
    idx = state['current_slide_index']
    print(f"\n---------------- Executing Node: finalize_slide (Slide {idx + 1}) ----------------")
    
    # Ghi log thông tin slide
    print(f"Finalizing slide {idx + 1}")
    print(f"HTML path: {state.get('current_html_path', 'N/A')}")
    print(f"Image path: {state.get('current_image_path', 'N/A')}")
    
    # Lưu thông tin slide cuối cùng
    final_slide_data = {
        "index": idx,
        "tool_call": state['current_tool_call'],
        "html_path": state.get('current_html_path', ''),
        "png_path": state.get('current_image_path', ''),
        "original_text": state['current_slide_text']
    }
    state['final_slides'].append(final_slide_data)
    state['slide_chunks'].pop(0)  # Xóa slide đã hoàn tất khỏi hàng đợi
    print(f"Đã thêm slide {idx + 1} vào danh sách final_slides (tổng: {len(state['final_slides'])})")
    
    # Reset retry_count cho slide tiếp theo
    state['retry_count'] = 0
    print(f"Reset retry_count: {state['retry_count']}")

    state['previous_accepted_tool_call'] = state['current_tool_call']
    end_time = time.time()
    print(f"Finalization of slide took {end_time - start_time:.2f} seconds.")
    return state