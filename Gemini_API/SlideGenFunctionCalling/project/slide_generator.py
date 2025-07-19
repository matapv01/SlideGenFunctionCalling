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

import re
import json
import logging

logger = logging.getLogger(__name__)


def get_html_slide(pre_slide_content, pre_function_call, slide_content):
    logger.debug(f"Generating HTML slide for content: {slide_content[:50]}...")
    demand_prompt = """
    # Smart Slide Generation Prompt (with Design Consistency & Semantic Content Splitting)

    # Language Detection
    language = "Vietnamese" if is_vietnamese else "English"

    # Objective
    Create a single slide that conveys a single semantic block from `slide_content`, fits the logical flow from the previous slide, 
    and maintains full design coherence across the deck. Split unrelated content into `remaining_content` for subsequent slides, ensuring 
    no content from the current slide or previous slides is repeated in `remaining_content`.

    # Instructions for Smart Slide Generation

    ## 1. Content Analysis & Splitting
    - Analyze `slide_content` to identify distinct semantic blocks (e.g., "Title", "Introduction", "Section 1", "Section 2").
    - Assign only one semantic block (or two closely related blocks, e.g., "Title" and "Introduction") to the slide.
    - Split unrelated blocks into `remaining_content` for subsequent slides, even if content fits within one slide, to ensure clarity and focus.
    - Example:
        - Input: "Title: Green Environment. Introduction: Forests are vital. Section 1: Oxygen production. Section 2: Rivers."
        - Output:
            - Slide: Title + Introduction
            - `remaining_content`: "Section 1: Oxygen production. Section 2: Rivers."
    - Summarize the chosen block concisely (3–4 bullet points or 5–7 lines).
    - Remove placeholders (e.g., "Your Title Here", "Placeholder").
    - Ensure `remaining_content`:
        - Does NOT repeat any content included in the slide's `arguments`.
        - Does NOT repeat any content from previous slides ({0}).
        - Preserves semantic integrity (no mid-sentence or mid-idea splits).
        - Is distinct from the current slide's content to avoid duplication.
    - If no split is needed, return empty JSON (i.e., {{}}).
    - Output text in `(language)`.

    ## 2. Slide Function Selection
    - Evaluate ALL available slide functions:
        - `make_bullet_slide`
            - Parameters: `title` (string), `items` (list of strings)
            - Example: {{"name": "make_bullet_slide", "arguments": {{"title": "Title", "items": ["Point 1", "Point 2", "Point 3"]}}}}
        - `make_two_column_slide`
            - Parameters: `title` (string), `left_column_texts` (list of strings), `right_column_texts` (list of strings)
            - Example: {{"name": "make_two_column_slide", "arguments": {{"title": "Comparison", "left_column_texts": ["Left 1", "Left 2"], "right_column_texts": ["Right 1", "Right 2"]}}}}
        - `make_text_slide`
            - Parameters: `title` (string), `content` (string)
            - Example: {{"name": "make_text_slide", "arguments": {{"title": "Explanation", "content": "Detailed content."}}}}
        - `make_image_with_caption_slide`
            - Parameters: `title` (string), `image_path` (string), `caption` (string)
            - Example: {{"name": "make_image_with_caption_slide", "arguments": {{"title": "Image", "image_path": "path/to/image.jpg", "caption": "Image description"}}}}
        - `generate_content_slide`
            - Parameters: `title` (string), `content` (string)
            - Example: {{"name": "generate_content_slide", "arguments": {{"title": "Content", "content": "General content"}}}}
    - Choose based on:
        a. Content type (list → `make_bullet_slide`, comparison → `make_two_column_slide`, narrative → `make_text_slide`, visual → `make_image_with_caption_slide`).
        b. Optimal visual layout for comprehension.
        c. Narrative flow from previous slide ({0}, {1}).
        d. Fit within slide without overflow (max 3–4 bullet points or 5–7 lines).
    - Default to `generate_content_slide` if unsure.
    - Do NOT use invalid function names or parameters.

    ## 3. Visual & Design Consistency
    - Match the previous slide ({0}, {1}):
        - Font size: Minimum 1.5rem for titles, 1.125rem for body text (1rem = 16px).
        - Font family: Arial or same as previous slide.
        - Colors: Use background (#FFFFFF), title (#000000), body (#333333), highlights (#EF4444, #3B82F6, #388E3C).
        - Bullet formatting, text alignment (centered titles, left/justified body), and spacing.
    - Ensure ≥10% whitespace.
    - Avoid:
        - Font size < 1.125rem for body or < 1.5rem for titles.
        - Inconsistent colors or alignment.
        - Placeholder text like "Your Title Here".

    ## 4. Highlight Key Phrases
    - Highlight meaningful phrases in content slides (not intro/thank you slides).
    - Use: `<b><i><span style='color:#HEXCODE'>text</span></i></b>`.
    - Colors: `#EF4444` (primary), `#3B82F6` (related), `#388E3C` (environmental).
    - Limit to 2–3 colors per slide, consistent across deck.
    - Do NOT highlight non-key phrases (e.g., "also", "such as", "for example", slide titles).
    - Highlighting must be consistent: use same color for same concepts across slides.

    ## 5. HTML Support
    - Use HTML tags only when necessary:
        - `<br>` for line breaks.
        - `<b>`, `<i>` for emphasis.
        - `<ul>`, `<li>` for bullets.
        - `<span style="font-size: Xrem">`.
    - HTML must enhance clarity, not clutter.

    ## 6. Semantic & Logical Continuity
    - Ensure tone, topic, and flow align with previous slide ({0}, {1}).
    - Transitions should be smooth and meaningful.

    ## 7. Presentation-Ready Structure
    - Ensure ≥10% whitespace.
    - Limit to 3–4 bullet points or 5–7 lines.
    - Guide viewer’s eye with clear title and content placement.

    - Slide must be:
    - Content-relevant
    - Layout-appropriate
    - Visually consistent with previous slide
    - Free of placeholders

    ## 8: CRITICAL - REDUNDANCY CHECK
    **Before doing anything else, you MUST determine if the 'Current raw content' is redundant.**
    Content is considered **redundant** if its core message is already fully expressed or summarized in the 'Previous slide content'. It is **NOT redundant** if it elaborates on a topic that was only a title or a brief point previously.

    *   **Example of REDUNDANT content:**
        *   Previous slide: Title: "The Water Cycle", Body: "Evaporation, Condensation, Precipitation."
        *   Current content: "This slide is about the water cycle."
        *   **Decision:** This is redundant. The topic is already known.

    *   **Example of NOT REDUNDANT content:**
        *   Previous slide: Title: "Our Key Topics", Body: "1. The Water Cycle, 2. Photosynthesis."
        *   Current content: "The Water Cycle is the path that all water follows..."
        *   **Decision:** This is NOT redundant. It is the beginning of a new, detailed section.

    ### 9: INTELLIGENT CONTENT ANALYSIS & SPLITTING (Only if not redundant)
    This is the core of your task. You must understand the difference between **Metadata** and **Content**.

    **Definitions:**
    -   **Metadata:** Titles, subtitles, section headings (e.g., "Introduction:", "Chapter 2:", "Key Findings"). Its purpose is to introduce the content that follows.
    -   **Content:** The actual information, such as paragraphs, bullet points, or lists that elaborate on the metadata.

    **The Golden Rule of Splitting:**
    **METADATA AND ITS DIRECTLY RELATED CONTENT MUST STAY TOGETHER ON THE SAME SLIDE.**
    -   You are **NEVER** allowed to put a title on one slide and its first paragraph or first bullet point on the next slide. This is a critical error.
    -   A "semantic block" for a slide is defined as a cluster of (Metadata + its associated Content).

    **Your Splitting Process:**
    1.  **Identify Clusters:** Scan the 'Current raw content' to identify these "Metadata + Content" clusters.
    2.  **Assign to Slide:** Select **one complete cluster** for the current slide.
        *   **Correct Example:** If the content is "Title: The Sun. The sun is a star...", your slide **must** contain both the title and the first sentence/paragraph.
        *   **WRONG Example:** Putting "Title: The Sun" on one slide and "The sun is a star..." on the next is **forbidden**.
    3.  **Handle Overflow:** If the content *within that single cluster* is too long for one slide (e.g., a title with 10 bullet points), you then split the **Content part only**.
        *   **Correct Splitting:**
            *   Slide 1: Title + Bullet points 1-4.
            *   `remaining_content`: Bullet points 5-10 (You can optionally repeat the title here for context on the next slide).
    4.  **Place Excess Clusters:** Any other complete clusters found in the raw content should be moved entirely to `remaining_content`.
        *   **Example:**
            *   Input: "Section 1: ... (content for S1) ... Section 2: ... (content for S2) ..."
            *   Slide 1: Contains all of "Section 1: ... (content for S1) ...".
            *   `remaining_content`: "Section 2: ... (content for S2) ...".
    
    If the content is new, proceed.
    - Analyze `slide_content` to find the main semantic block.
    - Summarize it concisely.
    - If there's excess content, place it in the `remaining_content` field. Ensure this content is TRULY new and does not repeat what will be on the current slide.

    
    ---
    ### 10: FUNCTION & DESIGN SELECTION
    Your role as a designer is paramount here.
    
    **A. Function Selection:**
    - Choose the BEST function for the content type from the available tools (e.g., `make_bullet_slide` for lists, `make_text_slide` for paragraphs).
    - Tools available: `make_bullet_slide`, `make_two_column_slide`, `make_text_slide`, `generate_body_slide7`, etc.

    **B. Aesthetic Cohesion and Design Inheritance:**
    - **YOU MUST** create a slide that feels like part of the same presentation as the previous one.
    - **Reference the 'Previous function call' ({1}) as your style guide.**
    - **Inherit Design Parameters:** Your new function call's arguments for colors, fonts, and general layout MUST match the previous call unless the content strongly justifies a change.
    - **Ensure Readability:**
        - **Font Size:** Strictly adhere to >= 1.5rem for titles and >= 1.125rem for body text. **This is not negotiable.**
        - **Color Contrast:** Ensure text is easily readable against the background. Use professional and harmonious color palettes. Avoid jarring colors.
        - **Whitespace:** The slide must feel uncluttered. Aim for at least 10-15% whitespace.

    ## Input Context
    - Previous slide content: {0}
    - Previous function call: {1}
    - Current slide content: {2}

    ## Output Requirements
    Respond with:
    - A function call with supported parameters
    - A JSON object in text response with:
        - `remaining_content`: Excess content for next slide, EXCLUDING content used in the slide and content from previous slides ({0}), or empty string if no split.
        - `split_reason`: Reason for split, or empty string if no split.
        - 'is_redundant': true/false (if content is redundant, see above).
        - 'redundancy_reason': Reason for redundancy if 'is_redundant' is true.
        - Return {{}} if no split is needed and no redundant.
    """

    tools = types.Tool(function_declarations=TOOLS)
    contents = [
        types.Content(role="user", parts=[types.Part(text="You are an AI agent that generates HTML slides based on the provided content.")]),
        types.Content(role="user", parts=[types.Part(text=demand_prompt.format(pre_slide_content, pre_function_call, slide_content))])
    ]
    
    response = safe_generate_content("gemini-2.5-flash-preview-05-20", contents, tools)
    
    logger.debug(f"Response from API: {response}")
    print(f"Response from API: {response}")

    if not response or not hasattr(response, 'candidates') or not response.candidates:
        logger.error("Invalid or empty response from API")
        return {
            "function_call": {
                "name": "generate_content_slide",
                "arguments": {"title": "Error", "content": "Unable to generate slide due to invalid API response"}
            },
            "remaining_content": "",
            "split_reason": "",
            "is_redundant": False,
            "redundancy_reason": ""
        }

    function_call = None
    text = ""
    try:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                text += part.text
            if hasattr(part, "function_call") and part.function_call:
                function_call = part.function_call

    except AttributeError as e:
        logger.error(f"Error accessing response parts: {e}")
        logger.debug(f"Function call: {function_call}")
        logger.debug(f"text: {text}")
        r1 = ""
        r2 = {
                "function_call": {
                    "name": "generate_content_slide",
                    "arguments": {"title": "Error", "content": f"Unable to access API response: {str(e)}"}
                }
            }
        r3 = {
                "remaining_content": "",
                "split_reason": "",
                "is_redundant": False,
                "redundancy_reason": ""
            }
        return r1, r2, r3

    # Xử lý text response để lấy text_json
    text = re.sub(r'```json\n|\n```', '', text).strip()
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        text_json = json.loads(json_match.group(0)) if json_match else {}
        if json_match:
            text = text.replace(json_match.group(0), '').strip()
    except json.JSONDecodeError:
        logger.error(f"Failed to parse text response as JSON: {text}")
        text_json = {}

    logger.debug(f"LLM response: {text}, Function call: {function_call}, Text JSON: {text_json}")
    return text.strip(), function_call, text_json

from google import genai
from google.genai import types
from dotenv import load_dotenv
import time
import google.genai.errors

def safe_generate_content(model, contents, tools=None, max_retries=30, delay=15):
    API_KEY_LIST = ['GEMINI_API_KEY', 'AQUANG1', 'AQUANG2', 'MATA01']
    for attempt, i in zip(range(max_retries), range(len(API_KEY_LIST))):
        try:
            key_index = attempt % len(API_KEY_LIST)
            api_key_name = API_KEY_LIST[key_index]
            print(f"Attempt {attempt + 1}/{max_retries} with API key: {api_key_name}")
            client = genai.Client(api_key=os.getenv(api_key_name))

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
Please evaluate the slide using the following detailed criteria. Go beyond surface-level formatting: assess the clarity, structure, visual alignment, and most importantly, whether all content is properly visible and nothing is overflowing, cut off, or hidden.
1. Title
    •	Is the title clearly stating the main idea (e.g., “Market Overview” instead of “Slide 2”)?
    •	Is it placed prominently (top-left or top-center)?
    •	Is the font size ≥ 1.5rem (approx. 24pt)?
    •	Is the title meaningful and aligned with the content, not generic?
2. Text Content
    •	Is the body text font size ≥ 1.125rem (approx. 18pt)?
    •	Is contrast between text and background strong enough for readability?
    •	Are text blocks/bullets concise and limited to no more than 2 lines per point?
    •	Is the total number of lines on the slide ≤ 7?
    •	Is spelling, grammar, and punctuation correct?
    •	Does the text content support the slide’s purpose (e.g., explain, persuade)?
    •	Are the most important points ordered logically and prioritized visually?
3. Layout & Content Placement
    •	Are all elements well-aligned and within the visible frame?
    •	Is there at least 10% white space to avoid clutter?
    •	Are sections clearly separated (e.g., margins, spacing)?
    •	Are key messages placed in focal areas (top-left, center)?
    •	Does the slide layout guide the eye naturally (top→bottom or left→right)?
4. Visuals & Images (if applicable)
    •	Are visuals relevant and meaningful to the slide content?
    •	Are they high-resolution (not blurry or pixelated)?
    •	Do they avoid overlapping or obscuring text?
    •	Do they enhance understanding, not serve as mere decoration?
5. Overall Visual Design
    •	Are no more than 2–3 font types used?
    •	Are color choices limited to 3–4 visually cohesive colors?
    •	Are transitions/animations used minimally and appropriately?
    •	Is there a clear visual hierarchy (Title > Main Points > Details)?
    •	Is the design clean and easy to scan?
6. Consistency with Other Slides
    •	Are the background, font family, font sizes (in rem), and color scheme consistent with previous slides?
    •	Is the layout structure (title, content placement) the same across slides?
    •	Do design choices contribute to a coherent and professional deck?
7. Content Overflow & Occlusion Detection (CRITICAL)
You must thoroughly evaluate for hidden, cut-off, or overflowing content, which often undermines the slide's usability. Detect overflow by:
✅ Checking These Visual Indicators:
    •	Any text or visual cut off or pushed outside the visible area (typically 900×500px for content zones).
    •	Font sizes smaller than 1.125rem (body) or 1.5rem (title) used to force content to fit.
    •	More than 7 lines or bullet points.
    •	Text overlaps, misalignments, or stacking of elements that reduce readability.
    •	Lack of whitespace (<10% of slide area), making the content feel cramped.
🧠 Cross-Verification Method:
    •	Compare the content from the slide function call (e.g., make_bullet_slide(...)) with the rendered slide image.
    •	Identify if any portion of the content is missing in the image but was present in the function call — this is a clear sign of content occlusion or overflow.
    •	Use this comparison to detect hidden text, cropped sentences, or content pushed beyond slide bounds.
📤 Action if Overflow Detected:
If any overflow or occlusion is confirmed:
    •	Return a structured JSON object:
    {
    "remaining_content": "<semantically appropriate content for next slide>",
    "split_reason": "Split to prevent visual overflow and ensure readability."
    }
    •	Ensure that remaining_content preserves semantic integrity — do not cut mid-sentence or split incomplete ideas.
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

######################################################################################################3 them anh slide

    question = """
    You are a meticulous Slide Quality and Content Flow Analyst. Your task is to evaluate the current slide for quality, readability, and logical flow, especially when content needs to be split due to overflow.

    **Current Tool Call (What was intended for this slide):**
    {1}

    ---
    ### Part 1: Standard Quality Evaluation
    Evaluate the current slide image based on the general criteria provided here:
    {0}

    Pay close attention to consistency with the previous slide (if provided) in terms of background, colors, font family, and font sizes.

    ---
    ### Part 2: CRITICAL - Intelligent Content Splitting & Redundancy Prevention
    This is the most important part. If you deny the slide due to **content overflow, occlusion, or poor readability**, you MUST intelligently split the content.

    **Your Method: 3-Way Cross-Verification**
    To decide what content is "new" and what is "already shown," you must compare:
    1.  **Input Content (`tool_call_output`):** What was *supposed* to be on this slide.
    2.  **Rendered Image (Current Slide):** What is *actually visible* to the user right now.
    3.  **Previous Slide Image:** What the user has *already seen*.

    **STRICT Rules for `remaining_content`:**
    1.  **MUST BE NEW INFORMATION:** `remaining_content` must ONLY contain text and ideas that are **NOT fully visible** on the current slide or the previous slide.
    2.  **CONTEXTUAL HEADINGS ARE ALLOWED:** It is acceptable for `remaining_content` to start with the same **title or heading** as the current slide IF AND ONLY IF it is followed by **new, distinct body text/bullet points** that were not visible before.
    3.  **NEVER REPEAT BODY TEXT:** Do not include any full sentence or bullet point in `remaining_content` if that exact sentence/bullet is already clearly readable on the current or previous slide.
    4.  **MAINTAIN SEMANTIC INTEGRITY:** Never split a sentence or a single, cohesive idea in half.

    **Example Scenario:**
    - **`tool_call_output` contains:** A long section titled "The Water Cycle" with two points: "1. Evaporation is..." and "2. Condensation is...".
    - **Rendered slide image only shows:** The title "The Water Cycle" and the first point "1. Evaporation is...". The second point is cut off.

    -   **BAD `remaining_content`:** `"The Water Cycle. 1. Evaporation is... 2. Condensation is..."`
        *(Reason: This is wrong because it repeats "Evaporation", which is already visible.)*

    -   **GOOD `remaining_content`:** `"2. Condensation is..."`
        *(Reason: This is correct because it only includes the part that was not visible.)*

    -   **BEST `remaining_content`:** `"The Water Cycle\n\n2. Condensation is..."`
        *(Reason: This is even better because it provides the contextual heading for the new slide, ensuring flow, but only includes the NEW body content.)*

    ---
    ### Part 3: Your Response Format
    Based on your analysis, respond in the following format:

    **1. Text Response:**
    - Start with `<!-- accept -->` or `<!-- deny -->`.
    - Follow with `<!-- reason: [Your detailed explanation. If denying, explain EXACTLY why, e.g., 'Text overflow, point 3 is cut off.' or 'Font size is 1rem, which is below the 1.125rem minimum.'] -->`
    - **If and only if you are splitting content**, provide a JSON object (without markdown backticks) containing:
        - `remaining_content`: The semantically correct, non-duplicated content for the *next* slide.
        - `split_reason`: A clear reason, e.g., "Split to prevent overflow. Moved the 'Condensation' section to the next slide."
        - If no split is needed, return an empty JSON object: `{{}}`.

    **2. Function Call (Only if you respond with `<!-- deny -->`):**
    - Provide a **corrected function call** for the **CURRENT slide**.
    - This new call should fix the identified issues (e.g., reduce the number of items, increase font size, adjust content to fit).
    - **DO NOT** create a function call for the `remaining_content`. The main script will handle that in the next loop.
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
        logger.error("Invalid VLM response")
        return "<!-- deny -->", {"name": "generate_content_slide", "arguments": {"title": "Error", "content": "Invalid VLM response"}}, {"remaining_content": "", "split_reason": ""}

    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            text += part.text
        if hasattr(part, "function_call") and part.function_call:
            function_call = part.function_call

    text = re.sub(r'```json\n|\n```', '', text).strip()
    try:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        text_json = json.loads(json_match.group(0)) if json_match else {}
        text_json = {
            "remaining_content": text_json.get("remaining_content", ""),
            "split_reason": text_json.get("split_reason", "")
        }
        if json_match:
            text = text.replace(json_match.group(0), '').strip()
    except json.JSONDecodeError:
        logger.error(f"Failed to parse text response as JSON: {text}")
        text_json = {"remaining_content": "", "split_reason": ""}

    if function_call:
        function_call = {"name": function_call.name, "arguments": dict(function_call.args)}
    else:
        function_call = {"name": "generate_content_slide", "arguments": {"title": "Error", "content": "No function call returned"}}

    logger.debug(f"VLM response: {text}, Function call: {function_call}, Text JSON: {text_json}")
    return text.strip(), function_call, text_json



def generate_plan_from_html(html_content):
    return "Kế hoạch chưa được triển khai"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
import re
import tempfile
import time
import shutil
import zipfile

def process_slides(docx_file, output_folder):
    logger.info(f"Bắt đầu xử lý slides từ {docx_file}")
    chunks = inputProcessor(docx_file)
    slide_list = create_slide_list(chunks)
    logger.debug(f"Danh sách slide ban đầu: {slide_list}")

    slide_function_calling_list = []
    pre_slide_content = ""
    pre_function_call = ""
    api_call_cnt = 0
    i = 0

    driver = initialize_chromedriver()
    if not driver:
        raise Exception("Không thể khởi tạo ChromeDriver")

    with tempfile.TemporaryDirectory() as tmpdir:
        html_folder = os.path.join(tmpdir, "html")
        png_folder = os.path.join(tmpdir, "png")
        debug_folder = os.path.join(tmpdir, "debug")
        os.makedirs(html_folder, exist_ok=True)
        os.makedirs(png_folder, exist_ok=True)
        os.makedirs(debug_folder, exist_ok=True)

        html_files = []
        png_files = []
        max_attempts = 6
        previous_image_path = None

        while i < len(slide_list):
            logger.info("--" * 20)
            logger.info(f"Đang xử lý slide {i+1}")
            slide_content = slide_list[i]
            slide_content = re.sub(r'Your Title Here|Placeholder', '', slide_content, flags=re.IGNORECASE).strip()
            
            attempts = 0
            current_tool_call = None
            text = ""
            text_json = {"remaining_content": "", "split_reason": "", "is_redundant": False, "redundancy_reason": ""}
            isRedudant = False


            # Tạo folder debug cho slide
            slide_debug_folder = os.path.join(debug_folder, f"slide{i+1}")
            llm_debug_folder = os.path.join(slide_debug_folder, "LLM")
            vlm_debug_folder = os.path.join(slide_debug_folder, "VLM")
            os.makedirs(llm_debug_folder, exist_ok=True)
            os.makedirs(vlm_debug_folder, exist_ok=True)

            while attempts < max_attempts:
                attempts += 1
                logger.info(f"Thử gọi LLM lần {attempts} cho slide {i+1}")

                # Tạo folder attempt cho LLM
                llm_attempt_folder = os.path.join(llm_debug_folder, f"attempt{attempts}")
                os.makedirs(llm_attempt_folder, exist_ok=True)

                try:
                    # Gọi LLM để tạo tool call
                    text, current_tool_call, text_json = get_html_slide(pre_slide_content, pre_function_call, slide_content)
                    api_call_cnt += 1
                    
                    if text_json.get("is_redundant"):
                        logger.warning(f"Slide số {i+1} bị xác định là dư thừa. Lý do: {text_json.get('redundancy_reason')}. Bỏ qua slide này.")
                        isRedudant = True
                        break # Bỏ qua phần còn lại của vòng lặp này

                    # Lưu output của LLM vào file txt trong folder debug
                    llm_txt_path = os.path.join(llm_attempt_folder, f"output_slide_{i+1}_attempt_{attempts}.txt")
                    with open(llm_txt_path, "w", encoding="utf-8") as txt_file:
                        txt_file.write(f"Text: {text}\nTool Call: {current_tool_call}\nText JSON: {text_json}")

                    if 'remaining_content' in text_json:
                        remaining_content = text_json['remaining_content']
                        split_reason = text_json.get('split_reason', 'Không có lý do chia tách')
                        if remaining_content and remaining_content != slide_content:
                            logger.info(f"Chèn nội dung còn lại vào slide_list tại vị trí {i+2}: {remaining_content}")
                            slide_list.insert(i + 1, remaining_content)
                        else:
                            logger.warning(f"Bỏ qua remaining_content không hợp lệ: {remaining_content}")

                    # Tạo HTML
                    html_content = get_function_by_name(current_tool_call)
                    if not isinstance(html_content, str):
                        logger.error(f"Nội dung HTML tạo bởi LLM không hợp lệ: {html_content}")
                        html_content = "<html><body><h1>Lỗi</h1><p>Nội dung HTML tạo bởi LLM không hợp lệ</p></body></html>"
                        current_tool_call = {"name": "generate_content_slide", "arguments": {"title": slide_content[:50], "content": slide_content[:200]}}

                    temp_html_path = os.path.join(html_folder, f"slide_{i+1}_attempt_{attempts}.html")
                    llm_html_path = os.path.join(llm_attempt_folder, f"slide_{i+1}_attempt_{attempts}.html")
                    with open(temp_html_path, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    with open(llm_html_path, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    
                    temp_image_path = os.path.join(png_folder, f"slide_{i+1}_attempt_{attempts}.png")
                    llm_image_path = os.path.join(llm_attempt_folder, f"slide_{i+1}_attempt_{attempts}.png")
                    slide_image = capture_slide_image(driver, html_content, temp_image_path)

                    try:
                        if os.path.exists(temp_image_path):
                            shutil.copy2(temp_image_path, llm_image_path)
                        else:
                            logger.warning(f"Không tìm thấy file PNG để sao chép: {temp_image_path}")

                    except FileNotFoundError as e:
                        logger.warning(f"Bỏ qua lỗi sao chép file PNG: {e}")

                    max_vlm_attempts = 6
                    vlm_cnt = 1
                    slide_accepted = False


                    while vlm_cnt < max_vlm_attempts and not slide_accepted:

                        # Tạo folder attempt cho VLM
                        vlm_attempt_folder = os.path.join(vlm_debug_folder, f"attempt{vlm_cnt}")
                        os.makedirs(vlm_attempt_folder, exist_ok=True)

                        # Đánh giá bằng VLM
                        text, new_tool_call, text_json = evaluate_slide_with_vlm(temp_image_path, previous_image_path, current_tool_call)
                        logger.debug(f"Kết quả VLM: {text}, Tool call mới: {new_tool_call}, JSON: {text_json}")
                        api_call_cnt += 1
                        vlm_cnt += 1

                        # Lưu output của VLM vào file txt trong folder debug
                        vlm_txt_path = os.path.join(vlm_attempt_folder, f"vlm_output_slide_{i+1}_attempt_{attempts}_vlm_{vlm_cnt-1}.txt")
                        with open(vlm_txt_path, "w", encoding="utf-8") as txt_file:
                            txt_file.write(f"VLM Text: {text}\nVLM Tool Call: {new_tool_call}\nVLM Text JSON: {text_json}")

                        # Sao chép HTML và PNG vào VLM attempt folder
                        vlm_html_path = os.path.join(vlm_attempt_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.html")
                        vlm_image_path = os.path.join(vlm_attempt_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.png")
                        try:
                            if os.path.exists(temp_html_path):
                                shutil.copy2(temp_html_path, vlm_html_path)
                            else:
                                logger.warning(f"Không tìm thấy file HTML để sao chép: {temp_html_path}")
                        except FileNotFoundError as e:
                            logger.warning(f"Bỏ qua lỗi sao chép file HTML: {e}")
                        try:
                            if os.path.exists(temp_image_path):
                                shutil.copy2(temp_image_path, vlm_image_path)
                            else:
                                logger.warning(f"Không tìm thấy file PNG để sao chép: {temp_image_path}")
                        except FileNotFoundError as e:
                            logger.warning(f"Bỏ qua lỗi sao chép file PNG: {e}")

                            
                        if "<!-- accept -->" in text:
                            final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                            final_png_path = os.path.join(png_folder, f"slide_{i+1}.png")

                            try:
                                os.rename(temp_html_path, final_html_path)
                            except FileNotFoundError as e:
                                logger.warning(f"Bỏ qua lỗi đổi tên file HTML: {e}")
                            try:
                                os.rename(temp_image_path, final_png_path)
                            except FileNotFoundError as e:
                                logger.warning(f"Bỏ qua lỗi đổi tên file PNG: {e}")

                            html_files.append(final_html_path)
                            png_files.append(final_png_path)
                            slide_function_calling_list.append(current_tool_call)
                            pre_slide_content = slide_content
                            pre_function_call = current_tool_call
                            previous_image_path = final_png_path
                            slide_accepted = True
                            logger.info(f"Slide {i+1} được chấp nhận với tool call: {current_tool_call}")

                            break  # Thoát vòng lặp VLM nếu đã chấp nhận

                        elif "<!-- deny -->" in text:
                            logger.info(f"Slide {i+1} bị từ chối: {text}")
                            if new_tool_call:
                                if hasattr(new_tool_call, 'name') and hasattr(new_tool_call, 'args'):
                                    new_tool_call = {"name": new_tool_call.name, "arguments": new_tool_call.args}

                                current_tool_call = new_tool_call

                                # xóa các file tạm nếu không chấp nhận slide
                                os.remove(temp_html_path)
                                os.remove(temp_image_path)

                                # Tạo HTML
                                html_content = get_function_by_name(current_tool_call)
                                if not isinstance(html_content, str):
                                    logger.error(f"Nội dung HTML tạo bởi VLM không hợp lệ: {html_content}")
                                    html_content = "<html><body><h1>Lỗi</h1><p>Nội dung HTML tạo bởi VLM không hợp lệ</p></body></html>"
                                    current_tool_call = {"name": "generate_content_slide", "arguments": {"title": slide_content[:50], "content": slide_content[:200]}}

                                temp_html_path = os.path.join(html_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.html")
                                vlm_html_path = os.path.join(vlm_attempt_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.html")
                                with open(temp_html_path, "w", encoding="utf-8") as file:
                                    file.write(html_content)
                                with open(vlm_html_path, "w", encoding="utf-8") as file:
                                    file.write(html_content)
                                
                                temp_image_path = os.path.join(png_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.png")
                                vlm_image_path = os.path.join(vlm_attempt_folder, f"slide_{i+1}_attempt_{vlm_cnt-1}.png")
                                slide_image = capture_slide_image(driver, html_content, temp_image_path)

                                try:
                                    if os.path.exists(temp_image_path):
                                        shutil.copy2(temp_image_path, llm_image_path)
                                    else:
                                        logger.warning(f"Không tìm thấy file PNG để sao chép: {temp_image_path}")

                                except FileNotFoundError as e:
                                    logger.warning(f"Bỏ qua lỗi sao chép file PNG: {e}")

                            # Xử lý remaining_content
                            if 'remaining_content' in text_json:
                                remaining_content = text_json['remaining_content']
                                split_reason = text_json.get('split_reason', 'Không có lý do chia tách')
                                if remaining_content and remaining_content != slide_content:
                                    logger.info(f"Chèn nội dung còn lại vào slide_list tại vị trí {i+2}: {remaining_content}")
                                    slide_list.insert(i + 1, remaining_content)
                                    
                                else:
                                    logger.warning(f"Bỏ qua remaining_content không hợp lệ: {remaining_content}")

                    if not slide_accepted:
                        logger.warning(f"Slide {i+1} với số lần thử tối đa ({max_vlm_attempts})")
                        final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                        final_png_path = os.path.join(png_folder, f"slide_{i+1}.png")
                        try:
                            os.rename(temp_html_path, final_html_path)
                        except FileNotFoundError as e:
                                logger.warning(f"Bỏ qua lỗi đổi tên file HTML: {e}")
                        try:
                            os.rename(temp_image_path, final_png_path)
                        except FileNotFoundError as e:
                            logger.warning(f"Bỏ qua lỗi đổi tên file PNG: {e}")

                        html_files.append(final_html_path)
                        png_files.append(final_png_path)
                        slide_function_calling_list.append(current_tool_call)
                        pre_slide_content = slide_content
                        pre_function_call = current_tool_call
                        previous_image_path = final_png_path
                        logger.info(f"Slide {i+1} đạt tối đa lần đánh giá, lây tool call gần nhất: {current_tool_call}")

                    break # Thoát vòng lặp LLM nếu LLM không lỗi

                except FileNotFoundError as e:
                    logger.warning(f"Bỏ qua lỗi FileNotFoundError: {e}")

                except Exception as e:
                    logger.error(f"Lỗi khi xử lý slide {i+1} với LLM, thử {attempts}: {e}")
                    logger.error(f"tool_call: {current_tool_call}")
                    logger.error(f"text: {text}")
                    logger.error(f"text_json: {text_json}")
                    logger.error(f"Thử slide {i+1} với LLM lần thứ {attempts}/ {max_attempts} thất bại, sẽ thử lại sau 1 giây...")
                    raise # Ném lại lỗi để dừng chương trình
                
                time.sleep(1)  # Chờ 1 giây để tránh quá tải API

            if isRedudant:
                logger.info(f"Slide {i+1} bị xác định là dư thừa, bỏ qua slide này.")
                slide_list.pop(i)
                continue

            if slide_accepted or attempts >= max_attempts:
                i += 1

        logger.info(f"Tổng số lần gọi API: {api_call_cnt}")
        driver.quit()
        logger.info("Đóng ChromeDriver")

        zip_file_path = os.path.join(tmpdir, "slides.zip")
        try:
            with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for html_file in html_files:
                    if html_file and os.path.exists(html_file):
                        zipf.write(html_file, os.path.join("html", os.path.basename(html_file)))
                    else:
                        logger.error(f"File HTML không tồn tại: {html_file}")
                for png_file in png_files:
                    if png_file and os.path.exists(png_file):
                        zipf.write(png_file, os.path.join("png", os.path.basename(png_file)))
                    else:
                        logger.error(f"File PNG không tồn tại: {png_file}")
                # Thêm debug folder vào ZIP
                for root, dirs, files in os.walk(debug_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join("debug", os.path.relpath(file_path, debug_folder))
                        zipf.write(file_path, arcname)
            if not os.path.exists(zip_file_path):
                logger.error(f"ZIP file không được tạo: {zip_file_path}")
                raise FileNotFoundError(f"Không tạo được file ZIP: {zip_file_path}")
        except Exception as e:
            logger.error(f"Lỗi khi tạo ZIP file: {e}")
            raise

        final_zip_path = os.path.join(output_folder, "slides.zip")
        shutil.copy2(zip_file_path, final_zip_path)

    logger.debug(f"Danh sách slide cuối cùng: {slide_list}")
    logger.debug(f"Danh sách tool call cuối cùng: {slide_function_calling_list}")
    return final_zip_path