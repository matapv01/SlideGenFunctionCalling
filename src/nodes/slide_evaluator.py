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

    criteria = """
    Improved Prompt for Slide Content Evaluation
    Please evaluate the slide according to the following detailed criteria. Assess not only the design and formatting, but also whether the content is placed in a suitable location, the meaning is clear, and the message supports the intended purpose of the slide.

    1. Title
        - Is the title clearly stating the main idea or topic of the slide (e.g., "Market Overview" instead of "Slide 2")?

        - Is the title placed in a prominent location (typically top center or top left)?

        - Is the font at least 4–6 points larger than the body text?

        - Is the title meaningful, concise, and contextually aligned with the slide’s content?

    Evaluate if the title actually reflects the core message of the slide and is not generic.

    2. Text Content
        - Is the font size at least 18 pt to ensure readability from a distance?

        - Does the text contrast clearly with the background (e.g., white on dark, black on light)?

        - Are sentences clear, concise (no more than 2 lines), and easy to scan?

        - Is the use of bullet points or short paragraphs (max 5 lines) applied effectively?

        - Is spelling, grammar, and punctuation correct?

        - Does the content logically support the purpose of the slide (informative, persuasive, etc.)?

        - Are the main points prioritized and placed in the most logical order?

    Check if the content is relevant, well-organized, and presented in a way that supports comprehension and focus.

    3. Layout and Content Placement
        - Are all elements (title, text, images, charts) well-aligned and not overlapping or cut off?

        - Is there sufficient white space to reduce visual clutter?

        - Are different content blocks clearly separated?

        - Are the most important messages placed in visually strong positions (top-left, center)?

        - Does the slide guide the viewer’s eye naturally (top → bottom or left → right)?

    Evaluate how effectively the layout guides the viewer and if content is located where it naturally makes sense to appear.

    4. Visuals and Images (if any)
        - Are images directly relevant to the content and purpose of the slide?

        - Are they high quality (not blurry or pixelated)?

        - Are images placed so they do not obscure or distract from text?

        - Do images enhance understanding or visual appeal, not just decoration?

    Assess if images help reinforce or explain the content — not just filler.

    5. Overall Visual Design
        - Are no more than 2–3 font types used?

        - Is the color scheme limited to 3–4 harmonious colors?

        - Are there minimal and tasteful transitions or animations?

        - Is the slide clean and easy to scan, with visual emphasis on key messages?

        - Is the visual hierarchy clear (title > main points > supporting text)?

    Consider if the overall aesthetic supports clarity and avoids distraction.

    6. Consistency with Other Slides (if applicable)
        - Are the background, font style, size, and color consistent with previous slides?

        - Is the layout structure (title placement, content areas) consistent?

        - Do the design choices support a cohesive narrative across slides?

    Check whether this slide feels like part of a unified deck or visually disconnected.

    Additional Evaluation Dimensions (Newly Added)
        - Content Meaning Accuracy: Does the text or visual element truly represent what it intends to convey? Is it logically accurate in the context?

        - Slide Purpose Fit: Does the slide serve its intended purpose (inform, compare, convince, summarize)? Does every element contribute to that goal?

        - Redundancy Check: Are there any duplicate or unnecessary elements that could be removed without losing meaning?
    """

    # --- SỬA ĐỔI: Prompt được đơn giản hóa ---
    # Không cần phải hướng dẫn chi tiết về định dạng JSON nữa.
    prompt_template = f"""
    Evaluate the following slide based on these criteria:
    {criteria}

    In addition, if a previous slide is available, evaluate consistency between the current and previous slides in the following aspects:
    - Background color
    - Text color
    - Font size
    - Font family

    Current tool call:  
    {tool_call_output}
    
    if you deny:
    - Generate a tool call using the current function . You MAY also modify the slide content **only if necessary**, such as:
    - The content is too long and overcrowds the slide.
    - The content lacks clarity or is not well structured for presentation.
    - The content does not match the selected slide layout appropriately.

    Allowed modifications include:
    - Trimming or summarizing overly long paragraphs
    - Splitting complex content into simpler bullets
    - Improving clarity, structure, or conciseness

    However, do NOT remove or alter the **core message** of the content. Preserve its intent and essential meaning.

    Respond with either:

    <!-- accept -->
    <!-- reason -->

    Or:

    <!-- deny -->
    <!-- reason -->

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