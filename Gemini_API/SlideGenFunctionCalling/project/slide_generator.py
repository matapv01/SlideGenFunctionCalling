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
        print(f"respond: {response.text}")
        print(f"Function to call: {function_call.name}")
        print(f"Arguments: {function_call.args}")
        #  In a real app, you would call your function here:
        #  result = schedule_meeting(**function_call.args)
        return function_call
    else:
        print("No function call found in the response.")
        print(response.text)
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
        chrome_options.add_argument("--window-size=1920,1080")

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
        # 2. Chỉ thêm prefix file:/// vào đường dẫn tuyệt đối
        modified_html = html_content.replace(
            'C:/',
            'file:///C:/'
        )
        
        # 3. Ghi file HTML đã sửa
        with open(temp_html_path, "w", encoding="utf-8") as file:
            file.write(modified_html)
        
        # 4. Load trang và đợi cho ảnh load
        driver.get(f"file:///{os.path.abspath(temp_html_path)}")
        time.sleep(2)
        
        # 5. Chụp và xử lý ảnh
        screenshot_bytes = driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot_bytes))
        image = image.resize((900, 500))
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
    1. Title: 
        ●	The title must clearly state the main topic of the slide in a concise way (e.g., ‘Customer Survey Results’ instead of ‘Slide 1’). 
        ●	The font size of the title should be at least 4–6 points larger than the body text to ensure prominence. 
        ●	Use a clean, professional font (such as Arial, Helvetica, or Calibri). Place the title in a prominent position, typically at the top of the slide. 
    2. Text content: 
        ●	Font size should be at least 18 pt to ensure readability, even from a distance. 
        ●	Text color must have strong contrast with the background (e.g., white text on dark background or black text on light background).
        ●	Sentences should be concise (no more than 2 lines per sentence). 
        ●	Use bullet points or short paragraphs (fewer than 5 lines each) to avoid dense blocks of text.
        ●	 Ensure there are no spelling or grammar errors. 
    3. Layout: 
        ●	Elements (title, text, images, graphics) must not overlap or be cut off. 
        ●	Maintain consistent spacing (margins) to avoid a cluttered look. 
        ●	Visually separate different sections (e.g., using white space or subtle dividers). 
    4. Images (if any): 
        ●	Images must be directly relevant to the slide’s content. 
        ●	Ensure images are placed appropriately and do not cover any text. Use images of good quality (not pixelated or stretched) with proper resolution (at least 72 dpi for presentations). 
    5. Overall design:
        ●	 Use no more than 2–3 font families to maintain consistency. 
        ●	Limit the color palette to 3–4 main colors to avoid visual chaos. 
        ●	Avoid excessive animations or effects that might distract from the content.
        ●	 Keep the slide clean and uncluttered, focusing on key points.
    6. Consistency with previous slide (if applicable): 
        ●	Use the same background color, text color, font size, and font family as the previous slide to maintain visual coherence. 
        ●	Keep the overall layout consistent, with the title and main sections in the same positions. 
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
    text = extract_text_from_docx(docx_file)
    chunks = split_text_into_chunks(text)
    slide_list = create_slide_list(chunks)

    slide_function_calling_list = []
    pre_slide_content = ""
    pre_function_call = ""
    cnt = 1
    api_call_cnt = 0
    for slide_content in slide_list:
        html_slide_call = get_html_slide(pre_slide_content, pre_function_call, slide_content)
        api_call_cnt += 1
        print(f"Slide {cnt} processed, API call count: {api_call_cnt}")
        cnt += 1
        slide_function_calling_list.append(html_slide_call)
        pre_slide_content = slide_content
        pre_function_call = html_slide_call
    print("All slides processed.")

    for x in slide_function_calling_list:
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

