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

    # Smart Slide Generation Prompt (with Design Consistency & HTML Support)

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

    # load dotenv
    from dotenv import load_dotenv
    load_dotenv()

    # Configure tools
    tools = types.Tool(function_declarations=TOOLS)

    # Define user prompt
    contents = [
        types.Content(
            role="user", parts=[types.Part(text="You are a AI agent that generates HTML slides based on the provided content.")],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part(
                    text=demand_prompt.format(pre_slide_content, pre_function_call, slide_content),
                )
            ],
        )
    ]
    
    response = safe_generate_content("gemini-2.5-flash-preview-05-20", contents, tools)
    
    # Check for a function call
    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        # Log the response
        logger.info(f"respond: {response.text}")
        logger.info(f"Function to call: {function_call.name}")
        logger.info(f"Arguments: {function_call.args}")
        #  In a real app, you would call your function here:
        #  result = schedule_meeting(**function_call.args)
        return function_call
    else:
        logger.info("No function call found in the response.")
        logger.info(response.text)
        return {"name": "generate_split_layout_slide1", "arguments": {"left_title": "Error", "left_subtitle": "No function call found"}}

import time
import google.genai.errors

def safe_generate_content(model, contents, tools=None, max_retries=10, delay=15):
    API_KEY_LIST = ['GEMINI_API_KEY', 'AQUANG1', 'AQUANG2', 'MATA01']
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
            return response
        except google.genai.errors.ServerError as e:
            if '503' in str(e):
                print(f"Model overloaded (attempt {attempt + 1}), retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise
    raise RuntimeError("Max retries reached. Model still overloaded.")


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

def evaluate_slide_with_vlm(image_path, previous_image_path, tool_call_output):
    logger.info(f"Evaluating slide: {image_path} with previous: {previous_image_path}")

    # Configure tools
    tools = types.Tool(function_declarations=TOOLS)
    contents = []

    # Load ảnh slide hiện tại
    # image = PILImage.open(image_path)
    with open(image_path, 'rb') as f:
      image_bytes = f.read()

    # Slide hiện tại
    current_image_part = types.Part.from_bytes(
                            data=image_bytes,
                            mime_type='image/png',
                         )
    contents.append( 
        types.Content(
            role="user",
            parts=[
                current_image_part,
                types.Part(text = "This is the current slide."),
            ]
        )
    )

    # Thêm ảnh slide trước đó nếu có
    if previous_image_path and os.path.exists(previous_image_path):
        # previous_image = PILImage.open(previous_image_path)

        with open(previous_image_path, 'rb') as f:
            pre_image_bytes = f.read()

        # Slide hiện tại
        pre_image_part = types.Part.from_bytes(
                                data=pre_image_bytes,
                                mime_type='image/png',
                            )
        contents.append( 
            types.Content(
                role="user",
                parts=[
                    pre_image_part,
                    types.Part(text = "This is the previous slide."),
                ]
            )
        )

    # Câu hỏi đánh giá
    question = f"""
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

    contents.append( 
            types.Content(
                role="user",
                parts=[
                    types.Part(text = question),
                ]
            )
        )
    
    # Send request with function declarations
    
    response = safe_generate_content("gemini-2.5-flash-preview-05-20", contents, tools)
    text = ""
    function_call = None

    for part in response.candidates[0].content.parts:
        if hasattr(part, "text") and part.text:
            text += part.text
        if hasattr(part, "function_call") and part.function_call:
            function_call = part.function_call

    return text.strip(), function_call


def generate_plan_from_html(html_content):
    return "Kế hoạch chưa được triển khai"


def process_slides(docx_file, output_folder):
    logger.info(f"Processing slides from {docx_file}")
    # text = extract_text_from_docx(docx_file)
    # chunks = split_text_into_chunks(text)
    chunks = inputProcessor(docx_file)  # Sử dụng hàm inputProcessor từ input_funcs.py
    slide_list = create_slide_list(chunks)

    slide_function_calling_list = []
    pre_slide_content = ""
    pre_function_call = ""
    cnt = 1
    api_call_cnt = 0
    for slide_content in slide_list:
        logger.info("--" * 20)
        logger.info(f"Slide {cnt} processing")
        html_slide_call = get_html_slide(pre_slide_content, pre_function_call, slide_content)
        api_call_cnt += 1
        logger.info(f"Slide {cnt} processed, API call count: {api_call_cnt}")
        cnt += 1
        slide_function_calling_list.append(html_slide_call)
        pre_slide_content = slide_content
        pre_function_call = html_slide_call
    print("All slides processed.")

    for x in slide_function_calling_list:
        logger.info("-------------------FC LIST-------------------")
        logger.info(x)
        logger.info("-------------------")

    driver = initialize_chromedriver()
    if not driver:
        raise Exception("Cannot initialize ChromeDriver")

    # Sử dụng tempfile.TemporaryDirectory() để quản lý thư mục tạm *bên trong* process_slides
    with tempfile.TemporaryDirectory() as tmpdir:
        html_folder = os.path.join(tmpdir, "html")
        png_folder = os.path.join(tmpdir, "png")
        os.makedirs(html_folder, exist_ok=True)
        os.makedirs(png_folder, exist_ok=True)

        html_files = []
        png_files = []
        max_attempts = 3
        previous_image_path = None

        for i, (slide_content, tool_call_output) in enumerate(zip(slide_list, slide_function_calling_list)):
            attempts = 0
            html_content = ""
            slide_image = None

            while attempts < max_attempts:
                attempts += 1
                logger.info(f"Processing slide {i+1}, attempt {attempts}")
                try:
                    html_content = get_function_by_name(tool_call_output)

                    temp_html_path = os.path.join(html_folder, f"slide_{i+1}_attempt_{attempts}.html")
                    with open(temp_html_path, "w", encoding="utf-8") as file:
                        file.write(html_content)

                    temp_image_path = os.path.join(png_folder, f"slide_{i+1}_attempt_{attempts}.png")
                    slide_image = capture_slide_image(driver, html_content, temp_image_path)

                    text, new_tool_call = evaluate_slide_with_vlm(temp_image_path, previous_image_path, tool_call_output)

                    if "<!-- accept -->" in text:
                        final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                        final_png_path = os.path.join(png_folder, f"slide_{i+1}.png")
                        os.rename(temp_html_path, final_html_path)
                        os.rename(temp_image_path, final_png_path)
                        html_files.append(final_html_path)
                        png_files.append(final_png_path)
                        previous_image_path = final_png_path
                        logger.info(f"Slide {i+1} accepted")
                        attempts -= 1
                        break  # Thoát vòng lặp while nếu slide được chấp nhận
                    elif "<!-- deny -->" in text and new_tool_call:
                        tool_call_output = new_tool_call
                        logger.info(f"Slide {i+1} denied, retrying with new tool call")

                except Exception as e:
                    logger.error(f"Error processing slide {i+1}, attempt {attempts}: {e}")
                    # Không break ở đây, để thử lại nếu còn attempts

            if attempts == max_attempts:  # Đã thử hết số lần cho phép
                logger.warning(f"Slide {i+1} max attempts reached")
                
                temp_html_path = os.path.join(html_folder, f"slide_{i+1}_attempt_{attempts}.html")
                temp_image_path = os.path.join(png_folder, f"slide_{i+1}_attempt_{attempts}.png")

                final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                final_png_path = os.path.join(png_folder, f"slide_{i+1}.png")
                os.rename(temp_html_path, final_html_path)
                os.rename(temp_image_path, final_png_path)
                html_files.append(final_html_path)
                png_files.append(final_png_path)
                previous_image_path = final_png_path

        driver.quit()
        logger.info("ChromeDriver closed")


        # Tạo file zip *trong* thư mục tạm của process_slide
        zip_file_path = os.path.join(tmpdir, "slides.zip")  # Đặt tên file ZIP trong thư mục tạm
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for html_file in html_files:
                if os.path.exists(html_file):  # Kiểm tra sự tồn tại *trước khi* thêm
                    zipf.write(html_file, os.path.join("html", os.path.basename(html_file)))
                else:
                    logger.error(f"File not found: {html_file}") # Log lỗi nếu file không tồn tại
            for png_file in png_files:
                if os.path.exists(png_file):
                    zipf.write(png_file, os.path.join("png", os.path.basename(png_file)))
                else:
                    logger.error(f"File not found: {png_file}")

        # *Sau khi* tạo xong ZIP, kiểm tra xem nó có tồn tại không
        if not os.path.exists(zip_file_path):
            raise FileNotFoundError(f"ZIP file not created: {zip_file_path}")

        # Copy file zip ra output_folder trước khi temp dir bị xóa
        final_zip_path = os.path.join(output_folder, "slides.zip")
        shutil.copy2(zip_file_path, final_zip_path) # copy cả metadata


    return final_zip_path  # Trả về đường dẫn đến file ZIP *trong output_folder*

