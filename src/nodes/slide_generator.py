import logging
import json
import re
from typing import Dict, Any, List
from langchain_core.tools import Tool

from src.stage import State
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate


logger = logging.getLogger(__name__)

SLIDEGEN_PROMPT = """# Smart Slide Generation Prompt (with Design Consistency & HTML Support)

    # Detect content language
    language = "Vietnamese" if is_vietnamese(slide_content) else "English"

    # Create a new slide that accurately conveys `slide_content`, fits the logical flow from the previous slide, 
    # and maintains full design coherence across the deck.

    INSTRUCTIONS FOR SMART SLIDE GENERATION

    1. CONTENT ANALYSIS & SUMMARIZATION:
    - Extract the key ideas from `slide_content`.
    - Rewrite the content into a clear and concise form that’s suitable for a slide.
    - Avoid copy-pasting long text blocks. Use bullet points, sections, or summaries.

    2. SLIDE FUNCTION SELECTION:
    - Choose the most suitable slide function for the current content, considering:
        a. Content type (list, narrative, explanation, process, comparison, etc.)
        b. Optimal visual layout for comprehension and impact
        c. Narrative flow from the previous slide
    - DO NOT default to the same slide function as before unless it fits naturally.
    - Example slide functions include:
        • `make_bullet_slide` – for short points or key facts  
        • `make_two_column_slide` – for comparison or parallel ideas  
        • `make_text_slide` – for deep explanations or storytelling  
        • `make_image_with_caption_slide` – for visual explanations  

    3. LANGUAGE:
    - All output text must be in `(language)`, matching the input content.

    4. VISUAL & DESIGN CONSISTENCY:
    Ensure that the new slide aligns stylistically with the previous one:
    - Use matching:
        • Font size and style  
        • Bullet point formatting  
        • Text alignment and spacing  
        • Background, title alignment, text padding  
        • Color themes and visual tone  
    - Avoid disruptive shifts like:
        × Sudden font downsizing (e.g. 14pt → 10pt)
        × Changing bullet type (e.g. dash → dot) without purpose
        × Inconsistent title placement (e.g. left-aligned → centered)

    5. HTML SUPPORT (ONLY WHEN NECESSARY):
    - You may insert basic HTML tags inside the content strings to fine-tune formatting — **only if justified**.
    - Acceptable use-cases:
        • `<br>` to control line breaks in tightly packed content
        • `<b>`, `<i>` to highlight keywords or distinctions
        • `<ul>`, `<li>` only when necessary to override default bullet behavior
        • `<span style="font-size: Xpx">` for inline size correction — use carefully!
    - HTML should **enhance clarity**, not clutter the slide or introduce inconsistency.
    - Avoid overusing or nesting tags unless truly needed for alignment or visual balance.

    6. SEMANTIC & LOGICAL CONTINUITY:
    - If the previous slide introduced a concept, this one may expand, contrast, or illustrate.
    - Make sure the tone, topic, and flow remain natural and progressive.
    - The audience should feel the transition is smooth and meaningful.

    7. PRESENTATION-READY STRUCTURE:
    - Use whitespace wisely.
    - Keep content digestible: avoid text-heavy layouts.
    - Place title and content to guide the viewer’s eye clearly.

    INPUT CONTEXT:
    - Previous slide content: {}
    - Previous function call: {}
    - Current slide content: {}

    OUTPUT REQUIREMENTS:
    - A **single slide function call**, e.g. `make_bullet_slide(...)`, with parameters written entirely in `(language)`.
    - Slide must be:
    ✓ Content-relevant  
    ✓ Layout-appropriate  
    ✓ Visually consistent  
    ✓ Logically connected  
    ✓ Clean and readable  
    ✓ Enhanced (only if necessary) with minimal HTML for formatting
"""



def extract_html_content(response_text):
    """
    Trích xuất nội dung HTML từ phản hồi của LLM.
    Cố gắng tìm phần HTML giữa các thẻ html hoặc body, hoặc lấy toàn bộ văn bản nếu không tìm thấy.
    """
    # Tìm kiếm mã HTML đầy đủ (bắt đầu bằng <!DOCTYPE hoặc <html>)
    html_full = re.search(r'<!DOCTYPE.*?html>|<html>.*?</html>', response_text, re.DOTALL)
    if html_full:
        return html_full.group(0)
    
    # Tìm kiếm nội dung trong thẻ body
    body_content = re.search(r'<body>.*?</body>', response_text, re.DOTALL)
    if body_content:
        return body_content.group(0)
    
    # Tìm kiếm bất kỳ mã HTML nào với thẻ div container
    div_content = re.search(r'<div.*?>.*?</div>', response_text, re.DOTALL)
    if div_content:
        return div_content.group(0)
    
    # Nếu không tìm thấy HTML, bọc văn bản bằng thẻ HTML cơ bản
    return f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; }}
            ul {{ margin-left: 20px; }}
            li {{ margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="slide">
            {response_text}
        </div>
    </body>
    </html>
    """

def slide_generator(state: State) -> State:
    """
    Node tạo slide: Sử dụng LLM để tạo slide từ nội dung văn bản.
    """
    idx = state['current_slide_index']
    logger.info(f"--- Node: slide_generator (Slide {idx + 1}) ---")
    
    # Lấy thông tin cần thiết từ state
    current_text = state['current_slide_text']
    llm = state['llm']
    
    # Gọi LLM để tạo slide
    try:


        logger.info(f"Attempt 1/5 with API key index 0...")
        # Sử dụng invoke trực tiếp mà không cần tool_choice
        llm_with_tools = llm.bind_tools(state['tools'])

        slidegen_prompt = ChatPromptTemplate.from_template(SLIDEGEN_PROMPT)
        slide_generator_runnable = slidegen_prompt | llm_with_tools

        response = slide_generator_runnable.invoke({"current_text": current_text})
        
        # Log thông tin phản hồi để debug
        response_content = response.content
        logger.info(f"LLM output (first 100 chars): {response}...")
        
        # Trích xuất HTML từ phản hồi
        html_content = extract_html_from_response(response_content)
        
        if not html_content or len(html_content) < 100:
            # Thử lại với một prompt khác nếu HTML quá ngắn
            logger.warning(f"HTML content quá ngắn: {len(html_content)} ký tự. Thử lại với prompt khác.")
            response = llm_with_tools.invoke(
                f"""Tạo một slide học thuật bằng HTML/CSS từ nội dung này: "{current_text}".
                
                Hãy trả về TOÀN BỘ mã HTML (bắt đầu với <!DOCTYPE html> và kết thúc với </html>).
                Đảm bảo slide có tiêu đề, nội dung được định dạng tốt, và thiết kế đẹp mắt."""
            )
            html_content = extract_html_from_response(response.content)
        
        # Log thông tin HTML được tạo
        logger.info(f"HTML content length: {len(html_content)} characters")
        
        # Kiểm tra nếu HTML vẫn không hợp lệ, tạo một HTML mặc định
        if not html_content or len(html_content) < 100:
            logger.warning("Tạo HTML mặc định vì không lấy được HTML hợp lệ từ LLM")
            html_content = create_default_html(current_text)
            
        # Tạo tool call giả
        tool_call_dict = {
            "name": "generate_academic_slide",
            "arguments": {
                "html_content": html_content
            }
        }
        
        # Cập nhật state với tool call
        state['current_tool_call'] = tool_call_dict
        logger.info(f"LLM returned tool call: generate_academic_slide")
        
        # Kiểm tra nếu nội dung quá dài
        if len(html_content) > 10000:
            state['is_redundant'] = True
            logger.warning(f"HTML content quá dài ({len(html_content)} ký tự). Đánh dấu slide là dư thừa.")
        else:
            state['is_redundant'] = False
                
    except Exception as e:
        logger.error(f"Lỗi khi gọi LLM: {e}")
        # Tạo HTML mặc định khi có lỗi
        html_content = create_default_html(current_text)
        tool_call_dict = {
            "name": "generate_academic_slide",
            "arguments": {
                "html_content": html_content
            }
        }
        state['current_tool_call'] = tool_call_dict
        state['is_redundant'] = False
        
    return state

def extract_html_from_response(response_text):
    """Trích xuất phần HTML từ phản hồi của LLM"""
    # Tìm đoạn HTML bắt đầu với <!DOCTYPE html> hoặc <html>
    html_start = response_text.find('<!DOCTYPE html>')
    if html_start == -1:
        html_start = response_text.find('<html>')
    
    if html_start == -1:
        # Không tìm thấy thẻ mở HTML, thử tìm bất kỳ thẻ HTML nào
        html_start = response_text.find('<')
        if html_start == -1:
            return ""
    
    # Tìm thẻ đóng HTML
    html_end = response_text.rfind('</html>')
    if html_end == -1:
        # Nếu không tìm thấy thẻ đóng, lấy toàn bộ nội dung từ vị trí bắt đầu
        return response_text[html_start:]
    
    # Trả về phần HTML hoàn chỉnh
    return response_text[html_start:html_end + 7]  # +7 để bao gồm cả "</html>"

def create_default_html(content_text):
    """Tạo HTML mặc định khi không lấy được từ LLM"""
    title = content_text.split('\n')[0] if '\n' in content_text else "Slide"
    content = content_text.replace('\n', '<br>')
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .slide {{
            width: 800px;
            height: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 40px;
            position: relative;
        }}
        .title {{
            font-size: 32px;
            color: #2c3e50;
            margin-bottom: 30px;
            text-align: center;
        }}
        .content {{
            font-size: 24px;
            line-height: 1.5;
            color: #34495e;
        }}
    </style>
</head>
<body>
    <div class="slide">
        <div class="title">{title}</div>
        <div class="content">{content}</div>
    </div>
</body>
</html>"""
    
    return html