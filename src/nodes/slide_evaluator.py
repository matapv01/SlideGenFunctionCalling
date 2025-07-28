# /app/src/nodes/slide_evaluator.py (ĐÃ SỬA)

import logging
import base64
import os
import json
import re
from typing import Dict, Any

# --- Sửa đổi Import ---
from langchain_core.messages import HumanMessage, AIMessage

from src.graph_state import graph_state
from src.tools.tool_des import ALL_TOOLS 

logger = logging.getLogger(__name__)

def image_to_base64(image_path: str) -> str:
    """Hàm tiện ích để chuyển đổi file ảnh sang chuỗi base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def slide_evaluator(state: graph_state) -> graph_state:
    """
    Node đánh giá slide: Sử dụng LLM để đánh giá chất lượng của slide.
    """
    retry_count = state.get('retry_count', 0)
    idx = state['current_slide_index']
    logger.info(f"--- Node: slide_evaluator (Slide {idx + 1}, Thử lại lần {retry_count}) ---")
    
    # Lấy thông tin từ slide đã tạo
    tool_call = state['current_tool_call']
    tool_call_output = tool_call['arguments'].get('html_content', '')
    
    # Log nội dung HTML để dễ debug
    logger.info(f"HTML content to evaluate (first 100 chars): {tool_call_output[:100]}...")
    logger.info(f"HTML content length: {len(tool_call_output)} characters")
    
    # Kiểm tra nội dung HTML có đủ không
    if not tool_call_output or len(tool_call_output) < 100:
        logger.warning(f"Nội dung HTML quá ngắn hoặc không hợp lệ ({len(tool_call_output)} ký tự)")
        state['vlm_decision'] = "deny"  # Mặc định từ chối nếu không có nội dung
        
        # Tăng retry_count
        state['retry_count'] = state.get('retry_count', 0) + 1
        logger.info(f"Tăng retry_count lên {state['retry_count']}")
        
        # Kiểm tra nếu đã đạt số lần thử lại tối đa
        if state['retry_count'] >= state.get('max_retries', 3):
            logger.warning(f"Đã đạt số lần thử lại tối đa ({state.get('max_retries', 3)}). Buộc chấp nhận slide.")
            state['vlm_decision'] = "accept"  # Chấp nhận để thoát khỏi vòng lặp
        
        return state
    
    # Nếu tìm thấy đường dẫn ảnh, cập nhật state
    current_image_path = state.get('current_image_path', '')
    if current_image_path:
        # Đánh giá sử dụng VLM với cả text và hình ảnh
        try:
            # Tiêu chí đánh giá cho slide
            criteria = """
            1. Nội dung đầy đủ: Slide chứa đầy đủ thông tin quan trọng từ văn bản gốc.
            2. Dễ đọc: Văn bản rõ ràng, ngắn gọn và dễ đọc. Sử dụng bullet points hoặc số thứ tự khi thích hợp.
            3. Bố cục cân đối: Không quá nhiều hoặc quá ít nội dung. Sắp xếp thông tin hợp lý.
            4. Thẩm mỹ: Màu sắc hài hòa, font chữ phù hợp, kích thước chữ đủ lớn để đọc.
            """
            
            # Format câu hỏi cho LLM
            question_template = """Đánh giá slide học thuật sau dựa trên các tiêu chí: {criteria}

Nội dung slide:
{slide_content}

Quyết định của bạn là gì? Trả lời chỉ "accept" hoặc "deny"."""
            
            final_question = question_template.format(criteria=criteria, slide_content=tool_call_output)
            
            # Gọi LLM để đánh giá
            llm_instance = state['llm_instance']
            logger.info(f"Attempt 1/5 with API key index 0...")
            response = llm_instance.invoke(final_question)
            
            # Phân tích kết quả
            text_response = response.content.lower()
            decision = "accept" if "accept" in text_response else "deny"
            logger.info(f"Quyết định của LLM: {decision}")
            
            # Cập nhật state với quyết định
            state['vlm_decision'] = decision
            
        except Exception as e:
            logger.error(f"Lỗi khi đánh giá slide: {e}")
            state['vlm_decision'] = "deny"  # Mặc định từ chối nếu có lỗi
    else:
        # Không có ảnh để đánh giá, đánh giá chỉ dựa trên text
        logger.warning("Không tìm thấy đường dẫn ảnh để đánh giá")
        
        # Tiêu chí đánh giá cho slide
        criteria = """
        1. Nội dung đầy đủ: Slide chứa đầy đủ thông tin quan trọng từ văn bản gốc.
        2. Dễ đọc: Văn bản rõ ràng, ngắn gọn và dễ đọc. Sử dụng bullet points hoặc số thứ tự khi thích hợp.
        3. Bố cục cân đối: Không quá nhiều hoặc quá ít nội dung. Sắp xếp thông tin hợp lý.
        """
        
        # Format câu hỏi cho LLM
        question_template = """Đánh giá slide học thuật sau dựa trên các tiêu chí: {criteria}

Nội dung slide:
{slide_content}

Quyết định của bạn là gì? Trả lời chỉ "accept" hoặc "deny"."""
        
        final_question = question_template.format(criteria=criteria, slide_content=tool_call_output)
        
        # Gọi LLM để đánh giá
        llm_instance = state['llm_instance']
        logger.info(f"Attempt 1/5 with API key index 0...")
        response = llm_instance.invoke(final_question)
        
        # Phân tích kết quả
        text_response = response.content.lower()
        decision = "accept" if "accept" in text_response else "deny"
        logger.info(f"Quyết định của LLM: {decision}")
        
        # Cập nhật state với quyết định
        state['vlm_decision'] = decision
    
    return state