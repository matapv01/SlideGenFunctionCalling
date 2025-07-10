import os
import shutil
import tempfile
from docx import Document
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter

import logging
import zipfile

from google import genai
from google.genai import types

import os
# dotenv load
from dotenv import load_dotenv
load_dotenv()

from PIL import Image as PILImage
from io import BytesIO

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from google import genai
from google.genai import types
import os
# dotenv load
from dotenv import load_dotenv
load_dotenv()

from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import time

from tools import *
from html_lib import *
from parse_funcs import *
from input_funcs import *




def extract_text_from_docx(file_path):
    print(f"Extracting text from {file_path}")
    doc = Document(file_path)
    text = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(text)

def split_text_into_chunks(text, chunk_size=200, chunk_overlap=50):
    print("Splitting text into chunks")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_text(text)

def create_slide_list(chunks):
    print("Creating slide list")
    slide_list = []
    current_slide = ""
    for section in chunks:
        section = section.strip()
        if not section:
            continue
        if not current_slide:
            current_slide = section
        else:
            if len(current_slide) + len(section) <= 600:
                current_slide += "\n" + section
            else:
                slide_list.append(current_slide)
                current_slide = section
    if current_slide:
        slide_list.append(current_slide)
    return slide_list

def get_html_slide(pre_slide_content, pre_function_call, slide_content):
    print(f"Generating HTML slide for content: {slide_content[:50]}...")
    demand_prompt = """
    # Smart Slide Generation Prompt (with Design Consistency & Semantic Content Splitting)

    # Detect content language
    language = "Vietnamese" if is_vietnamese('{2}') else "English"

    # Create a new slide that accurately conveys `slide_content`, fits the logical flow from the previous slide, 
    # and maintains full design coherence across the deck.

    INSTRUCTIONS FOR SMART SLIDE GENERATION

    1. CONTENT ANALYSIS & SUMMARIZATION:
    - Extract key ideas from `slide_content`.
    - Rewrite content concisely for a slide, using bullet points or sections.
    - Remove any placeholder text like "Your Title Here", "Placeholder", or similar.
    - Identify semantic blocks (e.g., Introduction, Part 1, Part 2).

    2. SLIDE FUNCTION SELECTION:
    - Evaluate ALL available slide functions:
        - `make_bullet_slide` – for short points (max 3–4 bullet points)
        - `make_two_column_slide` – for comparisons
        - `make_text_slide` – for explanations
        - `make_image_with_caption_slide` – for visuals
        - `generate_content_slide` – for general content
    - Consider:
        a. Content type (list, narrative, comparison, etc.)
        b. Optimal visual layout for comprehension
        c. Narrative flow from previous slide ({0})
        d. Fit within slide without overflow (max 3–4 bullet points or 5–7 lines)
    - Choose the best function to avoid overflow.
    - Split content if it exceeds 3–4 bullet points or 5–7 lines.

    3. LANGUAGE:
    - Output text in `(language)`, matching input.

    4. VISUAL & DESIGN CONSISTENCY:
    - Match the previous slide ({0}, {1}):
        - Font size: Minimum 1.5rem for titles, 1.125rem for body text (1rem = 16px).
        - Font family: Arial or same as previous slide.
        - Colors: Use same background, text, and title colors as previous slide.
        - Bullet formatting, text alignment, and spacing.
    - Avoid:
        - Font size < 1.125rem for body or < 1.5rem for titles.
        - Inconsistent colors or alignment.
        - Placeholder text like "Your Title Here".

    5. HTML SUPPORT:
    - Use HTML tags only when necessary:
        - `<br>` for line breaks.
        - `<b>`, `<i>` for emphasis.
        - `<ul>`, `<li>` for bullets.
        - `<span style="font-size: Xrem">` for size correction (X ≥ 1.125 for body, X ≥ 1.5 for titles).
    - HTML must enhance clarity, not clutter.

    6. Highlight key phrase:
    - Use `<b><i><span style='color:...'>...</span></i></b>` for key phrases.
    - Requirements:
        - Exact structure for all key phrases.
        - Vary color values for clarity, but keep tag structure identical.
        - Do not highlight placeholders or filler words (e.g., “also,” “such as”).
    - Example: `<b><i><span style='color:#EF4444;'>Hợp tác toàn cầu</span></i></b>`.

    7. SEMANTIC & LOGICAL CONTINUITY:
    - Ensure tone, topic, and flow align with previous slide.
    - Transitions should be smooth and meaningful.

    8. PRESENTATION-READY STRUCTURE:
    - Ensure ≥10% whitespace.
    - Limit to 3–4 bullet points or 5–7 lines.
    - Guide viewer’s eye with clear title and content placement.

    9. CONTENT FIT EVALUATION & SEMANTIC SPLITTING:
    - Check if `slide_content` fits without overcrowding.
    - If too long (>3–4 bullet points or >5–7 lines), split and return:
        - JSON object with:
            - `tokens_used`: Tokens for visible content (use `sentence-transformers/all-MiniLM-L6-v2`).
            - `remaining_content`: Content for next slide, preserving semantic integrity.
            - `split_reason`: Why and how content was split (e.g., "Split to limit to 3 bullet points").
        - Semantic splitting:
            - Split at semantic block boundaries (e.g., Slide 1: Part 1, Slide 2: Part 2).
            - Good example:
                - Slide 1: 3 bullet points
                - Slide 2: Remaining points
            - Bad example (avoid):
                - Slide 1: Half of Part 1
                - Slide 2: Rest of Part 1 + Part 2
            - Do not split mid-sentence or mid-idea.
            - ENSURE `remaining_content` excludes content in current slide.
    - If content fits, return {{}}.

    INPUT CONTEXT:
    - Previous slide content: {0}
    - Previous function call: {1}
    - Current slide content: {2}

    OUTPUT REQUIREMENTS:
    - A single slide function call (e.g., `make_bullet_slide(...)`) with parameters in `(language)`.
    - Include only supported parameters (e.g., `title`, `content`).
    - Include JSON with `tokens_used`, `remaining_content`, `split_reason` if split, or {{}} if not.
    - Slide must be:
        - Content-relevant
        - Layout-appropriate
        - Visually consistent with previous slide
        - Free of placeholders
    """

    tools = types.Tool(function_declarations=TOOLS)
    contents = [
        types.Content(role="user", parts=[types.Part(text="You are an AI agent that generates HTML slides based on the provided content.")]),
        types.Content(role="user", parts=[types.Part(text=demand_prompt.format(pre_slide_content, pre_function_call, slide_content))])
    ]
    
    response = safe_generate_content("gemini-2.5-flash-preview-05-20", contents, tools)
    
    if not response or not hasattr(response, 'candidates') or not response.candidates or not response.candidates[0].content:
        logger.error("Invalid or empty response from API")
        return {"name": "generate_content_slide", "arguments": {"title": "Lỗi", "content": "Không thể tạo slide do phản hồi API không hợp lệ"}}, {}

    function_call = None
    text_response = ""
    try:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                text_response += part.text
            if hasattr(part, "function_call") and part.function_call:
                function_call = part.function_call
    except AttributeError as e:
        logger.error(f"Error accessing response parts: {e}")
        return {"name": "generate_content_slide", "arguments": {"title": "Lỗi", "content": f"Không thể truy cập phản hồi API: {str(e)}"}}, {}

    if not function_call:
        logger.info(f"No function call found in response: {text_response}")
        return {"name": "generate_content_slide", "arguments": {"title": "Lỗi", "content": "Không tìm thấy lệnh gọi hàm"}}, {}

    # Chuyển FunctionCall thành dict
    if hasattr(function_call, 'name') and hasattr(function_call, 'args'):
        function_call = {"name": function_call.name, "arguments": function_call.args}

    text_response = re.sub(r'```json\n|\n```', '', text_response).strip()
    try:
        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
        text_json = json.loads(json_match.group(0)) if json_match else {}
        if json_match:
            text_response = text_response.replace(json_match.group(0), '').strip()
    except json.JSONDecodeError:
        logger.error(f"Failed to parse text response as JSON: {text_response}")
        text_json = {}

    logger.debug(f"Function call from get_html_slide: {function_call}")
    logger.debug(f"Text response JSON: {text_json}")
    return function_call, text_json


import time
import google.genai.errors

def safe_generate_content(model, contents, tools=None, max_retries=10, delay=15):
    API_KEY_LIST = ['GEMINI_API_KEY', 'MATA01', 'AQUANG1', 'AQUANG2']
    for attempt, i in zip(range(max_retries), range(len(API_KEY_LIST))):
        try:
            print(f"Attempt {attempt + 1} with API key: {API_KEY_LIST[i]}")
            client = genai.Client(api_key=os.getenv(API_KEY_LIST[i]))

            config = types.GenerateContentConfig(tools=[tools]) if tools else None
            # Send request with function declarations
            response = client.models.generate_content(
                model=model,
                config=config,
                contents=contents,
            )        
            
            # Kiểm tra tính hợp lệ của phản hồi
            if not response or not hasattr(response, 'candidates') or not response.candidates:
                error_msg = f"Invalid response: {response}. Response is None, missing candidates, or candidates empty."
                logger.error(error_msg)
                last_error = error_msg
                print(f"Invalid response (attempt {attempt + 1}), retrying in {delay}s...")
                time.sleep(delay)
                continue

            logger.info("Valid response received.")
            return response

        except google.genai.errors.ServerError as e:
            last_error = str(e)
            if '503' in str(e):
                print(f"Model overloaded (attempt {attempt + 1}), retrying in {delay}s...")
            elif '500' in str(e):
                print(f"Limit quota (attempt {attempt + 1}), retrying in {delay}s...")
            else:
                print(f"Eror: {str(e)} (attempt {attempt + 1}), retrying in {delay}s...")
            time.sleep(delay)
            continue

        except Exception as e:
            last_error = str(e)
            print(f"Unexpected error: {str(e)} (attempt {attempt + 1}), retrying in {delay}s...")
            logger.error(f"Unexpected error with key {API_KEY_LIST[i]}: {e}")
            time.sleep(delay)
            continue

    raise RuntimeError(f"Max retries reached. Last error: {last_error or 'Unknown error'}")


import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def initialize_chromedriver():
    try:
        chrome_driver_path = shutil.which("chromedriver")
        print(f"🔍 ChromeDriver path: {chrome_driver_path}")
        if not chrome_driver_path:
            raise FileNotFoundError("ChromeDriver not found in PATH.")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        # Đặt kích thước cửa sổ theo tỷ lệ slide presentation
        chrome_options.add_argument("--window-size=1600,900")
        chrome_options.add_argument("--force-device-scale-factor=1")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")

        driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
        print("✅ ChromeDriver initialized successfully")
        return driver

    except Exception as e:
        print(f"❌ Error initializing ChromeDriver: {e}")
        import traceback; traceback.print_exc()
        return None

def capture_slide_image(driver, html_content, output_path):
    """
    Chụp ảnh slide từ HTML content và lưu vào output_path.
    """
    logger.info(f"Capturing slide image to {output_path}")
    
    # 1. Tạo thư mục tạm để lưu file HTML
    temp_dir = os.path.dirname(output_path)
    temp_html_path = os.path.join(temp_dir, "temporal_slide.html")
    
    try:
        # 2. Xử lý đường dẫn ảnh tương đối cho Linux/Docker
        modified_html = html_content
        
        # Tìm thư mục project hiện tại
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_folder = os.path.join(current_dir, "Image")
        
        # Xử lý đường dẫn tương đối đến thư mục Image
        import re
        
        # Pattern 1: src="Image/filename" 
        pattern1 = r'src="Image/([^"]+)"'
        def replace_image_path(match):
            image_name = match.group(1)
            full_image_path = os.path.join(image_folder, image_name)
            if os.path.exists(full_image_path):
                # Sử dụng file:// URI cho Linux
                return f'src="file://{full_image_path}"'
            else:
                logger.warning(f"Image not found: {full_image_path}")
                return match.group(0)
        
        modified_html = re.sub(pattern1, replace_image_path, modified_html)
        
        # Pattern 2: src="filename.png/jpg" (không có thư mục)
        pattern2 = r'src="([^/"]+\.(?:png|jpg|jpeg|gif|bmp|svg))"'
        def replace_image_only_path(match):
            image_name = match.group(1)
            full_image_path = os.path.join(image_folder, image_name)
            if os.path.exists(full_image_path):
                return f'src="file://{full_image_path}"'
            else:
                logger.warning(f"Image not found: {full_image_path}")
                return match.group(0)
        
        modified_html = re.sub(pattern2, replace_image_only_path, modified_html)
        
        # Pattern 3: các đường dẫn tương đối khác (không bắt đầu bằng http, file, data, hoặc /)
        pattern3 = r'src="(?!http|file|data:|/)([^"]+)"'
        def replace_relative_path(match):
            relative_path = match.group(1)
            # Nếu không phải là file ảnh đã xử lý ở trên
            if not re.match(r'[^/]+\.(?:png|jpg|jpeg|gif|bmp|svg)$', relative_path):
                full_path = os.path.join(current_dir, relative_path)
                if os.path.exists(full_path):
                    return f'src="file://{full_path}"'
                else:
                    logger.warning(f"File not found: {full_path}")
            return match.group(0)
        
        modified_html = re.sub(pattern3, replace_relative_path, modified_html)
        
        # 3. Ghi file HTML đã sửa
        with open(temp_html_path, "w", encoding="utf-8") as file:
            file.write(modified_html)
        
        # 4. Load trang và chụp ảnh
        driver.get(f"file://{os.path.abspath(temp_html_path)}")
        driver.set_window_size(1920, 1080)
        
        # Đợi trang load hoàn toàn
        time.sleep(3)
        
        # 5. Chụp ảnh toàn bộ viewport
        screenshot_bytes = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot_bytes))
        
        # Resize về kích thước slide chuẩn giữ nguyên tỷ lệ
        image = image.resize((900, 500), Image.Resampling.LANCZOS)
        image.save(output_path)
        
        # 6. Dọn dẹp file tạm
        os.remove(temp_html_path)
        
        return image
        
    except Exception as e:
        logger.error(f"Error in capture_slide_image: {e}")
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
        raise

criteria = """
Improved Prompt for Slide Content Evaluation
Please evaluate the slide according to the following detailed criteria. Assess not only the design and formatting, but also whether the content is placed in a suitable location, the meaning is clear, and the message supports the intended purpose of the slide.

1. Title
    - Is the title clearly stating the main idea or topic of the slide (e.g., "Market Overview" instead of "Slide 2")?
    - Is the title placed in a prominent location (typically top center or top left)?
    - Is the font at least 1.5rem (approximately 24pt, assuming 1rem = 16px) for titles to ensure prominence?
    - Is the title meaningful, concise, and contextually aligned with the slide’s content?
Evaluate if the title actually reflects the core message of the slide and is not generic.

2. Text Content
    - Is the font size at least 1.125rem (approximately 18pt) for body text to ensure readability from a distance?
    - Does the text contrast clearly with the background (e.g., white on dark, black on light)?
    - Are sentences clear, concise (no more than 2 lines per bullet), and easy to scan?
    - Is the number of lines limited to 5–7 per slide to avoid overcrowding?
    - Is spelling, grammar, and punctuation correct?
    - Does the content logically support the purpose of the slide (informative, persuasive, etc.)?
    - Are the main points prioritized and placed in the most logical order?

3. Layout and Content Placement
    - Are all elements (title, text, images, charts) well-aligned and not overlapping or cut off?
    - Is there sufficient white space (at least 10% of slide area) to reduce visual clutter?
    - Are different content blocks clearly separated (e.g., by margins or dividers)?
    - Are the most important messages placed in visually strong positions (top-left, center)?
    - Does the slide guide the viewer’s eye naturally (top → bottom or left → right)?

4. Visuals and Images (if any)
    - Are images directly relevant to the content and purpose of the slide?
    - Are they high quality (not blurry or pixelated)?
    - Are images placed so they do not obscure or distract from text?
    - Do images enhance understanding or visual appeal, not just decoration?

5. Overall Visual Design
    - Are no more than 2–3 font types used?
    - Is the color scheme limited to 3–4 harmonious colors?
    - Are there minimal and tasteful transitions or animations?
    - Is the slide clean and easy to scan, with visual emphasis on key messages?
    - Is the visual hierarchy clear (title > main points > supporting text)?

6. Consistency with Other Slides (if applicable)
    - Are the background, font style, size (in rem), and color consistent with previous slides?
    - Is the layout structure (title placement, content areas) consistent?
    - Do the design choices support a cohesive narrative across slides?

7. Content Overflow Detection
    - Check for content overflow or occlusion, indicated by:
        - Text being cut off or extending beyond the slide boundaries (outside 900x500px).
        - Font size reduced below 1.125rem for body text or 1.5rem for titles.
        - Too many lines of text (more than 5–7 bullet points or paragraphs).
        - Insufficient white space (less than 10% of slide area).
        - Text or elements overlapping or obscured, making them unreadable.
    - If overflow or occlusion is detected, return a JSON object with `tokens_used` and `remaining_content` to split the content, ensuring semantic integrity.
"""


def evaluate_slide_with_vlm(image_path, previous_image_path, tool_call_output):
    logger.info(f"Evaluating slide: {image_path} with previous: {previous_image_path}")
    tools = types.Tool(function_declarations=TOOLS)
    contents = []

    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    current_image_part = types.Part.from_bytes(data=image_bytes, mime_type='image/png')
    contents.append(
        types.Content(
            role="user",
            parts=[
                current_image_part,
                types.Part(text="This is the current slide."),
            ]
        )
    )

    if previous_image_path and os.path.exists(previous_image_path):
        with open(previous_image_path, 'rb') as f:
            pre_image_bytes = f.read()
        pre_image_part = types.Part.from_bytes(data=pre_image_bytes, mime_type='image/png')
        contents.append(
            types.Content(
                role="user",
                parts=[
                    pre_image_part,
                    types.Part(text="This is the previous slide."),
                ]
            )
        )

    question = """
    Evaluate the following slide based on these criteria:
    {0}

    In addition, if a previous slide is available, evaluate consistency in:
    - Background color
    - Text color
    - Font size (in rem)
    - Font family

    Current tool call:  
    {1}
    
    If you deny the slide or detect content overflow or occlusion:
        • Check for:
            o Text cut off or extending beyond 900x500px.
            o Font size < 1.125rem for body or < 1.5rem for titles (1rem = 16px).
            o More than 3–4 bullet points or 5–7 lines.
            o Insufficient whitespace (<10% slide area).
            o Overlapping or obscured text/elements.
        • If overflow or occlusion detected:
            o Prioritize adjusting font size (≥1.125rem for body, ≥1.5rem for titles) to resolve overflow.
            o If font size adjustment fails, split content into multiple slides, preserving semantic meaning.
        • Semantic splitting guidelines:
            o Identify semantic blocks (e.g., Part 1, Part 2) from tool call or visible text.
            o Split at block boundaries (e.g., Slide 1: Part 1, Slide 2: Part 2).
            o Good example:
                - Slide 1: 3 bullet points
                - Slide 2: Remaining points
            o Bad example (avoid):
                - Slide 1: Half of Part 1
                - Slide 2: Rest of Part 1 + Part 2
            o If a block is too long, split into sub-blocks (e.g., Part 1a, Part 1b).
            o Do not split mid-sentence or mid-idea.
            o Remove placeholders like "Your Title Here" or "Placeholder".
            o ENSURE `remaining_content` excludes content already displayed.
        • Generate a tool call using the same function as the current tool_call_output (or a more suitable function) with:
            o Adjusted content (max 3–4 bullet points).
            o Font size ≥ 1.125rem for body, ≥ 1.5rem for titles.
            o Colors matching the previous slide.
            o No placeholders.
        • Include JSON in text response:
            o `tokens_used`: Tokens for visible content (use `sentence-transformers/all-MiniLM-L6-v2`).
            o `remaining_content`: Content for next slide.
            o `split_reason`: Why and how content was split (e.g., "Split to limit to 3 bullet points").
        • Allowed modifications:
            o Increase font size to meet thresholds.
            o Trim or summarize to fit 3–4 bullet points or 5–7 lines.
            o Adjust layout for whitespace and no occlusion.
        • Do NOT alter core message or intent.
        • Do NOT highlight non-key phrases (e.g., placeholders, “also,” “such as”).
        • Key phrases must use: `<b><i><span style='color:...'>...</span></i></b>`.

    Respond with:
    - Text response:
        - `<!-- accept -->` or `<!-- deny -->`
        - `<!-- reason: [Detailed explanation, e.g., font size < 1.125rem, text cut off] -->`
        - JSON with `tokens_used`, `remaining_content`, `split_reason` if split, or {{}}. No markdown code blocks.
    - A function call (if denied) with supported parameters.
    """

    contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text=question.format(criteria, tool_call_output))]
        )
    )

    response = safe_generate_content("gemini-2.5-flash-preview-05-20", contents, tools)
    text = ""
    function_call = None

    if not response or not hasattr(response, 'candidates') or not response.candidates:
        logger.error("Invalid response from VLM")
        return "<!-- deny -->", {"name": "generate_content_slide", "arguments": {"title": "Error", "content": "Invalid VLM response"}}, {}

    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            text += part.text
        if hasattr(part, "function_call") and part.function_call:
            function_call = part.function_call

    text = re.sub(r'```json\n|\n```', '', text).strip()
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        text_json = json.loads(json_match.group(0)) if json_match else {}
        if json_match:
            text = text.replace(json_match.group(0), '').strip()
    except json.JSONDecodeError:
        logger.error(f"Failed to parse text response as JSON: {text}")
        text_json = {}

    logger.debug(f"VLM response: {text}, Function call: {function_call}, Text JSON: {text_json}")
    return text.strip(), function_call, text_json



def generate_plan_from_html(html_content):
    return "Kế hoạch chưa được triển khai"


def process_slides(docx_file, output_folder):
    logger.info(f"Processing slides from {docx_file}")
    chunks = inputProcessor(docx_file)
    slide_list = create_slide_list(chunks)
    logger.debug(f"Initial slide_list: {slide_list}")

    slide_function_calling_list = []
    pre_slide_content = ""
    pre_function_call = ""
    cnt = 1
    api_call_cnt = 0
    i = 0
    while i < len(slide_list):
        logger.info("--" * 20)
        logger.info(f"Slide {cnt} processing")
        slide_content = slide_list[i]
        # Loại bỏ placeholder từ slide_content
        slide_content = re.sub(r'Your Title Here|Placeholder', '', slide_content, flags=re.IGNORECASE).strip()
        try:
            html_slide_call, text_json = get_html_slide(pre_slide_content, pre_function_call, slide_content)
            logger.debug(f"html_slide_call for slide {cnt}: {html_slide_call}")
        except Exception as e:
            logger.error(f"Error generating HTML slide {cnt}: {e}")
            html_slide_call = {"name": "generate_content_slide", "arguments": {"title": "Error", "content": f"Failed to generate slide: {str(e)}"}}
            text_json = {}
        api_call_cnt += 1
        logger.info(f"Slide {cnt} processed, API call count: {api_call_cnt}")

        if 'tokens_used' in text_json and 'remaining_content' in text_json:
            remaining_content = text_json['remaining_content']
            split_reason = text_json.get('split_reason', 'No split reason provided')
            if (remaining_content and remaining_content != slide_content and 
                remaining_content not in slide_list[:i] and 
                not any(remaining_content in prev_content for prev_content in slide_list[:i])):
                logger.info(f"Slide {cnt} only processed {text_json['tokens_used']} tokens, adding remaining content to slide_list. Split reason: {split_reason}")
                slide_list.insert(i + 1, remaining_content)
                logger.debug(f"Updated slide_list after slide {cnt}: {slide_list}")
            else:
                logger.warning(f"Skipping remaining_content for slide {cnt} due to duplication or invalid content: {remaining_content}. Split reason: {split_reason}")
        
        slide_function_calling_list.append(html_slide_call)
        pre_slide_content = slide_content
        pre_function_call = html_slide_call
        cnt += 1
        i += 1

    print("All slides processed.")

    for x in slide_function_calling_list:
        logger.info("-------------------FC LIST-------------------")
        logger.info(x)
        logger.info("-------------------")

    driver = initialize_chromedriver()
    if not driver:
        raise Exception("Cannot initialize ChromeDriver")

    with tempfile.TemporaryDirectory() as tmpdir:
        html_folder = os.path.join(tmpdir, "html")
        png_folder = os.path.join(tmpdir, "png")
        os.makedirs(html_folder, exist_ok=True)
        os.makedirs(png_folder, exist_ok=True)

        html_files = []
        png_files = []
        max_attempts = 6  # Tăng max_attempts
        previous_image_path = None
        slide_accepted = False

        for i, (slide_content, tool_call_output) in enumerate(zip(slide_list, slide_function_calling_list)):
            attempts = 0
            current_tool_call = tool_call_output
            if hasattr(current_tool_call, 'name') and hasattr(current_tool_call, 'args'):
                current_tool_call = {"name": current_tool_call.name, "arguments": current_tool_call.args}

            while attempts < max_attempts:
                attempts += 1
                try:
                    html_content = get_function_by_name(current_tool_call)
                    if not isinstance(html_content, str):
                        logger.error(f"Invalid HTML content for slide {i+1}, attempt {attempts}: {html_content}")
                        html_content = "<html><body><h1>Error</h1><p>Invalid HTML content</p></body></html>"
                    elif 'font-size: 14px' in html_content or 'font-size: 0.875rem' in html_content:
                        logger.warning(f"Font size too small detected in HTML for slide {i+1}, adjusting tool call")
                        if 'content' in current_tool_call['arguments']:
                            current_tool_call['arguments']['content'] = f"<span style='font-size: 18px'>{current_tool_call['arguments']['content']}</span>"
                        elif 'items' in current_tool_call['arguments']:
                            current_tool_call['arguments']['items'] = [f"<span style='font-size: 18px'>{item}</span>" for item in current_tool_call['arguments']['items']]
                        elif 'left_column_texts' in current_tool_call['arguments']:
                            current_tool_call['arguments']['left_column_texts'] = [f"<span style='font-size: 18px'>{text}</span>" for text in current_tool_call['arguments']['left_column_texts']]
                            current_tool_call['arguments']['right_column_texts'] = [f"<span style='font-size: 18px'>{text}</span>" for text in current_tool_call['arguments']['right_column_texts']]
                        html_content = get_function_by_name(current_tool_call)

                    temp_html_path = os.path.join(html_folder, f"slide_{i+1}_attempt_{attempts}.html")
                    with open(temp_html_path, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    temp_image_path = os.path.join(png_folder, f"slide_{i+1}_attempt_{attempts}.png")
                    slide_image = capture_slide_image(driver, html_content, temp_image_path)

                    text, new_tool_call, text_json = evaluate_slide_with_vlm(temp_image_path, previous_image_path, current_tool_call)

                    if "<!-- accept -->" in text:
                        final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                        final_png_path = os.path.join(png_folder, f"slide_{i+1}.png")
                        os.rename(temp_html_path, final_html_path)
                        os.rename(temp_image_path, final_png_path)
                        html_files.append(final_html_path)
                        png_files.append(final_png_path)
                        previous_image_path = final_png_path
                        slide_accepted = True
                        break
                    elif "<!-- deny -->" in text and new_tool_call:
                        if hasattr(new_tool_call, 'name') and hasattr(new_tool_call, 'args'):
                            new_tool_call = {"name": new_tool_call.name, "arguments": new_tool_call.args}
                        if 'tokens_used' in text_json and 'remaining_content' in text_json:
                            remaining_content = text_json['remaining_content']
                            split_reason = text_json.get('split_reason', 'No split reason provided')
                            if (remaining_content and remaining_content != slide_content and 
                                remaining_content not in slide_list and 
                                not any(remaining_content in prev_content for prev_content in slide_list)):
                                logger.info(f"Adding remaining content to slide_list for slide {i+2}: {remaining_content}")
                                slide_list.insert(i + 1, remaining_content)
                                slide_function_calling_list.insert(i + 1, new_tool_call)
                            else:
                                logger.warning(f"Skipping remaining_content for slide {i+1}: {remaining_content}")
                        current_tool_call = new_tool_call
                        logger.info(f"Slide {i+1} denied, retrying with new tool call: {new_tool_call}")
                except Exception as e:
                    logger.error(f"Error processing slide {i+1}, attempt {attempts}: {e}")
                    continue

            if not slide_accepted:
                logger.warning(f"Slide {i+1} max attempts reached without acceptance")
                final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                final_png_path = os.path.join(png_folder, f"slide_{i+1}.png")
                default_html = "<html><body><h1>Error</h1><p>Slide could not be generated.</p></body></html>"
                with open(final_html_path, "w", encoding="utf-8") as file:
                    file.write(default_html)
                capture_slide_image(driver, default_html, final_png_path)
                html_files.append(final_html_path)
                png_files.append(final_png_path)
                previous_image_path = final_png_path
                logger.info(f"Slide {i+1} generated default slide due to max attempts")

        driver.quit()
        logger.info("ChromeDriver closed")

        zip_file_path = os.path.join(tmpdir, "slides.zip")
        with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            for html_file in html_files:
                if html_file and os.path.exists(html_file):
                    zipf.write(html_file, os.path.join("html", os.path.basename(html_file)))
                else:
                    logger.error(f"File not found or skipped: {html_file}")
            for png_file in png_files:
                if png_file and os.path.exists(png_file):
                    zipf.write(png_file, os.path.join("png", os.path.basename(png_file)))
                else:
                    logger.error(f"File not found or skipped: {png_file}")

        if not os.path.exists(zip_file_path):
            raise FileNotFoundError(f"ZIP file not created: {zip_file_path}")

        final_zip_path = os.path.join(output_folder, "slides.zip")
        shutil.copy2(zip_file_path, final_zip_path)

    logger.debug(f"Final slide_list: {slide_list}")
    return final_zip_path