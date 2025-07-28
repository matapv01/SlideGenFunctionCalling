import re
import logging
import src
from src.graph_state import graph_state
from typing import List, Dict, Any
logger = logging.getLogger(__name__)

def finalize_slide(state: graph_state) -> Dict[str, Any]:
    """
    Node hoàn tất: Lưu slide đã được chấp nhận và cập nhật context.
    """
    idx = state['current_slide_index']
    logger.info(f"--- Node: finalize_slide (Slide {idx + 1}) ---")
    
    # Ghi log thông tin slide
    logger.info(f"Finalizing slide {idx + 1}")
    logger.info(f"HTML path: {state.get('current_html_path', 'N/A')}")
    logger.info(f"Image path: {state.get('current_image_path', 'N/A')}")
    
    # Lưu thông tin slide cuối cùng
    final_slide_data = {
        "index": idx,
        "tool_call": state['current_tool_call'],
        "html_path": state.get('current_html_path', ''),
        "png_path": state.get('current_image_path', ''),
        "original_text": state['current_slide_text']
    }
    state['final_slides'].append(final_slide_data)
    logger.info(f"Đã thêm slide {idx + 1} vào danh sách final_slides (tổng: {len(state['final_slides'])})")
    
    # Reset retry_count cho slide tiếp theo
    state['retry_count'] = 0
    logger.info(f"Reset retry_count: {state['retry_count']}")
    
    # Cập nhật context cho slide tiếp theo
    new_context = {
        "content": state['current_slide_text'],
        "function_call": state['current_tool_call'],
        "image_path": state.get('current_image_path', '')
    }
    
    return {
        "previous_slide_context": new_context
    }