# /app/src/nodes/slide_evaluator.py (SỬA ĐỔI VỚI with_structured_output)

import logging
import base64
import json
from typing import Literal, Dict, Any

# --- SỬA ĐỔI: Thêm Pydantic và Literal ---
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from src.stage import State

logger = logging.getLogger(__name__)

# --- SỬA ĐỔI: Định nghĩa cấu trúc output bằng Pydantic ---
# LangChain sẽ tự động sử dụng model này để buộc LLM trả về đúng định dạng.
class Evaluation(BaseModel):
    """
    Một đối tượng chứa phản hồi chi tiết và quyết định cuối cùng về slide.
    """
    feedback: str = Field(description="Phân tích chi tiết về những điểm tốt và những điểm cần cải thiện của slide. Cung cấp gợi ý cụ thể để làm slide tốt hơn.")
    decision: Literal["accept", "deny"] = Field(description="Quyết định cuối cùng. 'accept' nếu slide tốt, 'deny' nếu cần làm lại.")

# Các hàm tiện ích giữ nguyên
def image_to_base64(image_path: str) -> str:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Lỗi khi mã hóa ảnh sang base64: {image_path}, Lỗi: {e}")
        return ""

def slide_evaluator(state: State) -> State:
    """
    Node đánh giá slide: Sử dụng VLM và with_structured_output để đảm bảo
    kết quả trả về có cấu trúc và đáng tin cậy.
    """
    retry_count = state.get('retry_count', 0)
    idx = state['current_slide_index']
    logger.info(f"--- Node: slide_evaluator (Slide {idx + 1}, Thử lại lần {retry_count}) using structured_output ---")

    html_content = state.get('current_html_content', '')
    image_path = state.get('current_image_path', '')

    state['vlm_feedback'] = "No feedback provided."

    if not html_content or not image_path:
        logger.warning("Không có đủ nội dung HTML hoặc hình ảnh để đánh giá. Từ chối.")
        state['vlm_decision'] = "deny"
        state['vlm_feedback'] = "Không thể đánh giá vì thiếu mã HTML hoặc hình ảnh slide."
        state['retry_count'] = retry_count + 1
        return state

    # --- SỬA ĐỔI: Prompt được đơn giản hóa ---
    # Không cần phải hướng dẫn chi tiết về định dạng JSON nữa.
    prompt_template = """
Bạn là một chuyên gia đánh giá slide thuyết trình. Nhiệm vụ của bạn là đánh giá slide được cung cấp dưới dạng hình ảnh và mã HTML.
Dựa trên các tiêu chí sau, hãy đưa ra phản hồi và quyết định của bạn.

**Tiêu chí đánh giá:**
1.  **Nội dung (Content):** Slide có truyền tải đúng và đủ thông tin quan trọng không? Nội dung có súc tích, dễ hiểu không?
2.  **Bố cục (Layout):** Các thành phần có được sắp xếp cân đối, hợp lý không?
3.  **Thẩm mỹ (Aesthetics):** Phối màu, font chữ, kích thước chữ có hài hòa và dễ đọc không?

**Nội dung HTML của slide:**
```html
{html_content}
```

Bây giờ, hãy đánh giá slide (chủ yếu dựa vào hình ảnh) và đưa ra nhận xét cùng quyết định của bạn.
"""

    # Xây dựng tin nhắn đa phương thức (text + image)
    message_content = []
    formatted_prompt = prompt_template.format(html_content=html_content)
    message_content.append({"type": "text", "text": formatted_prompt})

    base64_image = image_to_base64(image_path)
    if base64_image:
        message_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{base64_image}"}
        })
    
    vlm_message = HumanMessage(content=message_content)

    # --- SỬA ĐỔI: Sử dụng with_structured_output ---
    # Quan trọng: Model trong state['llm'] phải hỗ trợ tool/function calling
    # ví dụ: gpt-4o, gpt-4-turbo, claude-3 models, gemini models.
    llm = state['llm']
    structured_llm = llm.with_structured_output(Evaluation)

    try:
        logger.info("Gửi yêu cầu đến VLM với structured_output...")
        # invoke sẽ trả về một đối tượng Pydantic 'Evaluation'
        response: Evaluation = structured_llm.invoke([vlm_message])
        
        logger.info(f"Quyết định của VLM: {response.decision}")
        logger.info(f"Phản hồi của VLM: {response.feedback}")

        state['vlm_decision'] = response.decision
        state['vlm_feedback'] = response.feedback

    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng khi gọi VLM với structured_output: {e}")
        state['vlm_decision'] = "deny"
        state['vlm_feedback'] = f"Đã xảy ra lỗi hệ thống trong quá trình đánh giá: {e}"

    # Cập nhật số lần thử lại nếu quyết định là 'deny'
    if state['vlm_decision'] == 'deny':
        state['retry_count'] = retry_count + 1
        logger.info(f"Slide bị từ chối. Tăng retry_count lên {state['retry_count']}")
    
    return state