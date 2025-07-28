# /app/src/nodes/prepare_slide.py 

import logging
from typing import Dict, Any
from src.graph_state import graph_state

logger = logging.getLogger(__name__)

def prepare_next_slide(state: graph_state) -> graph_state:
    """
    Node chuẩn bị slide tiếp theo từ hàng đợi.
    """
    logger.info("--- Node: prepare_next_slide ---")
    if state['slide_chunks']:
        # Lấy slide tiếp theo từ hàng đợi
        next_chunk = state['slide_chunks'].pop(0)
        state['current_slide_text'] = next_chunk
        state['current_slide_index'] += 1
        # Reset retry_count cho slide mới
        state['retry_count'] = 0
        logger.info(f"Hàng đợi còn {len(state['slide_chunks'])} chunks. Chuẩn bị xử lý slide {state['current_slide_index'] + 1}.")
        logger.info(f"Reset retry_count cho slide mới: {state['retry_count']}")
    return state