import os
import shutil
from docx import Document
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tải mô hình Qwen2.5-7B-Instruct
model_name_or_path = "Qwen/Qwen2.5-7B-Instruct"
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        torch_dtype="auto",
        device_map="auto",
    )
    logger.info("Qwen2.5-7B-Instruct loaded successfully.")
except Exception as e:
    logger.error(f"Error loading Qwen2.5-7B-Instruct: {e}")
    model = None
    tokenizer = None

# Tải mô hình Qwen2.5-VL-7B-Instruct
vlm_model_name = "Qwen/Qwen2.5-VL-7B-Instruct"
try:
    vlm_model = Qwen2VLForConditionalGeneration.from_pretrained(
        vlm_model_name,
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
        device_map="auto",
    )
    vlm_processor = AutoProcessor.from_pretrained(vlm_model_name, use_fast=True)
    logger.info("Qwen2.5-VL-7B-Instruct loaded successfully.")
except Exception as e:
    logger.error(f"Error loading Qwen2.5-VL-7B-Instruct: {e}")
    vlm_model = None
    vlm_processor = None

# Các hàm tạo HTML slide 
def generate_split_layout_slide1(
    left_bg_color="#F8F8F8",
    left_title="Báo cáo VNPT-AI về bài toán Function Calling",
    left_title_color="#2C4B7D",
    left_subtitle="Báo cáo về các bài báo đã tìm hiểu được",
    left_subtitle_color="#333",
    left_dots="•••••",
    left_dots_color="#2C4B7D",
    right_bg_color="#F8F8F8",
    right_image_src="path-to-your-image/LLM-image.png",
    right_image_alt="LLM Image",
    decor_bg_color="#2C4B7D",
    font_family="Roboto, Arial, sans-serif"
):
    """
    Generate a split-layout HTML slide with customizable parameters.

    :param left_bg_color: Background color of the left section.
    :param left_title: Title text in the left section.
    :param left_title_color: Color of the title in the left section.
    :param left_subtitle: Subtitle text in the left section.
    :param left_subtitle_color: Color of the subtitle in the left section.
    :param left_dots: Text or symbols for the dots section in the left section.
    :param left_dots_color: Color of the dots in the left section.
    :param right_bg_color: Background color of the right section.
    :param right_image_src: Source path for the image in the right section.
    :param right_image_alt: Alt text for the image in the right section.
    :param decor_bg_color: Background color of the decorative container.
    :param font_family: Font family for the slide content.
    :return: A string containing the HTML code.
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: #E0E0E0;
        }}
        .left-section {{
            background-color: {left_bg_color};
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 60px;
            box-sizing: border-box;
            z-index: 1;
        }}
        .left-section .title {{
            font-size: 48px;
            font-weight: bold;
            color: {left_title_color};
            margin-bottom: 20px;
        }}
        .left-section .subtitle {{
            font-size: 24px;
            color: {left_subtitle_color};
            margin-bottom: 40px;
        }}
        .left-section .dots {{
            font-size: 36px;
            color: {left_dots_color};
        }}
        .right-section {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 28px;
            background-color: {right_bg_color};
            border-radius: 10px;
            z-index: 1;
        }}
        .right-section img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
        }}
        .container::before {{
            content: '';
            position: absolute;
            width: 100%;
            height: 50%;
            background-color: {decor_bg_color};
            top: 50%;
            left: 0;
            z-index: -1;
        }}
        .decor-container {{
            position: absolute;
            width: 100%;
            height: 30%;
            background-color: {decor_bg_color};
            bottom: 0;
            left: 0;
            z-index: 0;
        }}
    </style>
</head>
<body>
    <div class='container d-flex flex-row justify-content-center align-items-center position-relative h-100'>
        <div class="row w-100">
            <div class="col-md-6 left-section">
                <div class="title">{left_title}</div>
                <div class="subtitle">{left_subtitle}</div>
                <div class="dots">{left_dots}</div>
            </div>
            <div class="col-md-4 offset-md-1 right-section">
                <img src="{right_image_src}" alt="{right_image_alt}">
            </div>
        </div>
    </div>
    <div class="decor-container"></div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

    return html_code

def generate_split_layout_slide2(
    title="Split Layout HTML Slide",
    left_bg_color="#2C4B7D",
    left_text_color="white",
    left_number="01",
    right_bg_color="#F0F0F0",
    image_placeholder_text_1="LLM (Large Language Model) logo Placeholder",
    image_placeholder_text_2="LLM Agent Pipeline Placeholder",
    bottom_title="UltraTool",
    bottom_title_color="#2C4B7D",
    bottom_description="UltraTool cải thiện gọi hàm nhờ lập kế hoạch, xây dựng tools theo yêu cầu phức tạp, và tạo Tool mới khi cần thiết nếu các tool hiện có không đáp ứng được.",
    bottom_description_color="#333",
    divider_color="#000",
    font_family="Roboto, Arial, sans-serif"
):
    """
    Generate a split layout HTML slide with customizable parameters.

    :param title: The title of the HTML document.
    :param left_bg_color: Background color of the left section.
    :param left_text_color: Text color of the left section.
    :param left_number: The number displayed in the left section.
    :param right_bg_color: Background color of the right section.
    :param image_placeholder_text_1: Text displayed in the first image placeholder.
    :param image_placeholder_text_2: Text displayed in the second image placeholder.
    :param bottom_title: Title displayed in the bottom right section.
    :param bottom_title_color: Color of the bottom title.
    :param bottom_description: Description text in the bottom right section.
    :param bottom_description_color: Color of the bottom description text.
    :param divider_color: Color of the divider in the bottom right section.
    :param font_family: Font family for the slide content.
    :return: A string containing the HTML code.
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: {right_bg_color};
        }}
        .left-section {{
            background-color: {left_bg_color};
            color: {left_text_color};
            display: flex;
            justify-content: top;
            align-items: center;
            flex-direction: column;
            padding: 20px;
            z-index: 1;
        }}
        .left-section .number {{
            font-size: 120px;
            font-weight: bold;
            margin-top: 80px;
        }}
        .right-section {{
            background-color: {right_bg_color};
            display: flex;
            flex-direction: column;
            justify-content: space-evenly;
            padding: 20px;
            z-index: 2;
        }}
        .image-placeholder {{
            background-color: #ccc;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #000;
            height: 250px;
        }}
        .bottom-right {{
            background-color: white;
            padding: 50px;
            display: flex;
            justify-content: space-evenly;
            align-items: center;
            flex-direction: row;
            margin-left: -40%;
            margin-right: 10%;
            height: 50%;
        }}
        .bottom-right .title {{
            font-size: 64px;
            font-weight: bold;
            color: {bottom_title_color};
            margin: 0;
        }}
        .bottom-right .description {{
            font-size: 18px;
            color: {bottom_description_color};
            line-height: 1.6;
            margin: 0;
            width: 50%;
        }}
        .divider {{
            width: 2px;
            height: 100px;
            background-color: {divider_color};
            margin: 0 30px;
        }}
    </style>
</head>
<body>
    <div class="container-fluid h-100">
        <div class="row h-100">
            <div class="col-md-4 d-flex flex-column align-items-center left-section">
                <div class="number">{left_number}</div>
            </div>
            <div class="col-md-8 d-flex flex-column justify-content-between right-section">
                <div class="row top-right">
                    <div class="col-md-6 image-placeholder">{image_placeholder_text_1}</div>
                    <div class="col-md-6 image-placeholder">{image_placeholder_text_2}</div>
                </div>
                <div class="bottom-right">
                    <div class="col-md-4 title">{bottom_title}</div>
                    <div class="divider"></div>
                    <div class="col-md-4 description">
                        {bottom_description}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS and dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

    return html_code

def generate_body_slide1(
    title="Professional HTML Slide Body",
    slide_title="2. Importance of Networking:",
    bg_color="#e9f7fe",
    text_bg_color="#ffffff",
    text_color="#2e4e7e",
    keyword_color="#004080",
    image_bg_color="#b0d4f1",
    image_placeholder_text="Image Placeholder",
    font_family="Roboto, Arial, sans-serif",
    content_paragraph="Networking is crucial for <span class=\"keyword\">personal development</span>. It fosters:",
    list_items=None
):
    """
    Generate a professional HTML slide body with customizable parameters.

    :param title: The title of the HTML document.
    :param slide_title: The title displayed on the slide.
    :param bg_color: Background color of the page.
    :param text_bg_color: Background color of the text container.
    :param text_color: Text color of the slide content.
    :param keyword_color: Color for keywords.
    :param image_bg_color: Background color of the image placeholder.
    :param image_placeholder_text: Text displayed in the image placeholder.
    :param font_family: Font family for the slide content.
    :param content_paragraph: Main paragraph content.
    :param list_items: A list of bullet points to include.
    :return: A string containing the HTML code.
    """
    if list_items is None:
        list_items = [
            "<span class=\"keyword\">Connections</span>: Builds relationships with professionals in various fields, expanding opportunities and access to knowledge.",
            "<span class=\"keyword\">Mentorship</span>: Enhances professional growth through guidance and support from established individuals.",
            "<span class=\"keyword\">Career Advancement</span>: Connects individuals with potential employers, job leads, and career-enhancing resources.",
            "<span class=\"keyword\">Collaboration</span>: Facilitates sharing of ideas, best practices, and projects, leading to innovation and professional growth."
        ]

    list_html = "\n".join(f"<li>{item}</li>" for item in list_items)

    html_code = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">

    <title>{title}</title>
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
        body, html {{
            height: 100%;
            margin: 0;
            font-family: {font_family};
            background-color: {bg_color};
        }}
        .slide-container {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            padding: 20px;
        }}
        .slide-title {{
            color: {keyword_color};
            font-size: 3em;
            margin-bottom: 15px;
            font-weight: bolder;
        }}
        .slide-content {{
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            background-color: {text_bg_color};
            padding: 35px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            color: {text_color};
            max-width: 980px;
            width: 100%;
        }}
        .text-content {{
            flex: 2;
            margin-right: 20px;
        }}
        .text-content p {{
            margin-bottom: 15px;
            font-size: 1.4em;
            line-height: 1.6;
        }}
        .text-content ul {{
            list-style: none;
            padding: 0;
        }}
        .text-content li {{
            margin-top: 12px;
            font-size: 1.2em;
        }}
        .keyword {{
            font-weight: bold;
            color: {keyword_color};
        }}
        .image-placeholder {{
            flex: 1;
            background-color: {image_bg_color};
            width: 250px;
            height: 250px;
            border-radius: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #333333;
            font-size: 1.1em;
            font-weight: bold;
        }}
        @media (max-width: 768px) {{
            .slide-content {{
                flex-direction: column;
                align-items: center;
            }}
            .text-content, .image-placeholder {{
                margin: 0;
                width: 100%;
                max-width: none;
            }}
            .image-placeholder {{
                margin-top: 20px;
                height: 220px;
            }}
        }}
    </style>
    <script src=\"https://polyfill.io/v3/polyfill.min.js?features=es6\"></script>
    <script type=\"text/javascript\" id=\"MathJax-script\" async
            src=\"https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js\"></script>
</head>
<body>
    <div class=\"slide-container\">
        <div class=\"slide-title\">{slide_title}</div>
        <div class=\"slide-content\">
            <div class=\"text-content\">
                <p>{content_paragraph}</p>
                <ul>
                    {list_html}
                </ul>
            </div>
            <div class=\"image-placeholder\">
                {image_placeholder_text}
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_code

def generate_body_slide2(
    title="Power of Goal Setting",
    header_text="The Power of Goal Setting",
    background_color="#faf0e6",
    text_color="#333",
    content_bg_color="#ffffff",
    content_shadow="0 4px 8px rgba(0, 0, 0, 0.1)",
    header_color="#3B5998",
    text_body_color="#2f4f4f",
    highlight_color="#ff4500",
    image_placeholder_text="[Image Placeholder - Proportioned for future use]",
    image_bg_color="#e1e5ea",
    font_family="Roboto, Arial, sans-serif",
    paragraph_text=(
        "<strong>Goal setting</strong> is a crucial aspect of personal development that empowers individuals to define clear objectives, map out strategies, and cultivate a path toward growth. "
        "It provides direction, motivation, and accountability, helping people focus their efforts, overcome challenges, and achieve their aspirations."
    )
):
    """
    Generate a professional HTML slide body for presenting content on the power of goal setting.

    :param title: The title of the HTML document.
    :param header_text: The main header of the slide.
    :param background_color: The background color of the entire slide.
    :param text_color: The default text color.
    :param content_bg_color: Background color for the content box.
    :param content_shadow: Box shadow for the content container.
    :param header_color: Color of the header text.
    :param text_body_color: Color of the body text.
    :param highlight_color: Color for highlighted text.
    :param image_placeholder_text: Placeholder text for the main image area.
    :param image_bg_color: Background color of the image placeholder.
    :param font_family: The font family to use for all text.
    :param paragraph_text: The content paragraph.
    :return: A string containing the HTML code.
    """

    html_code = f"""<!DOCTYPE html>
<html lang=\"en\">

<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">

    <title>{title}</title>
    <script src=\"https://polyfill.io/v3/polyfill.min.js?features=es6\"></script>
    <script id=\"MathJax-script\" async src=\"https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js\"></script>
    <link href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
        body,
        html {{
            height: 100%;
            margin: 0;
            font-family: {font_family};
            background-color: {background_color};
        }}

        .slide-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: {background_color};
        }}

        .content-box {{
            display: flex;
            flex-direction: row;
            background-color: {content_bg_color};
            border-radius: 10px;
            box-shadow: {content_shadow};
            width: 85%;
            padding: 20px;
            color: {text_color};
        }}

        .text-section {{
            flex: 1;
            padding: 20px;
            margin-right: 20px;
            color: {text_body_color};
        }}

        .image-box {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {image_bg_color};
            border-radius: 10px;
        }}

        h1 {{
            color: {header_color};
            font-size: 2.5em;
        }}

        p {{
            font-size: 1.2em;
            line-height: 1.6em;
        }}

        strong {{
            color: {highlight_color};
            font-weight: bold;
        }}
    </style>
</head>

<body>
    <div class=\"slide-container\">
        <div class=\"content-box\">
            <div class=\"text-section\">
                <h1>{header_text}</h1>
                <p>{paragraph_text}</p>
            </div>
            <div class=\"image-box\">
                <p style=\"color: #777;\">{image_placeholder_text}</p>
            </div>
        </div>
    </div>
</body>

</html>"""

    return html_code

def generate_body_slide3(
    title="The Future of Creative Industries: Digital Transformation and Immersive Experiences",
    header_text="The Future of Creative Industries: Digital Transformation and Immersive Experiences",
    background_gradient=("#4facfe", "#00c6ff"),
    content_bg_opacity=0.8,
    content_shadow="0 4px 8px rgba(0, 0, 0, 0.1)",
    header_color="#333333",
    text_body_color="#333333",
    highlight_color="#ff4500",
    image_placeholder_text="Image Placeholder",
    image_bg_color="#cccccc",
    font_family="Roboto, Arial, sans-serif",
    paragraph_text=(
        "The future of the <span class=\"bold\">creative industries</span> lies at the intersection of digital technology and immersive experiences. "
        "<span class=\"bold\">Virtual reality</span>, <span class=\"bold\">augmented reality</span>, and <span class=\"bold\">artificial intelligence</span> are revolutionizing how we create, consume, and interact with art, entertainment, and design. "
        "From immersive exhibitions to <span class=\"bold\">AI-powered storytelling</span>, these technologies are pushing the boundaries of imagination and engagement, opening up new possibilities for creativity and innovation."
    )
):
    """
    Generate a professional HTML slide body for presenting content on digital transformation and immersive experiences in the creative industries.

    :param title: The title of the HTML document.
    :param header_text: The main header of the slide.
    :param background_gradient: Gradient colors for the background.
    :param content_bg_opacity: Opacity for the content box background.
    :param content_shadow: Box shadow for the content container.
    :param header_color: Color of the header text.
    :param text_body_color: Color of the body text.
    :param highlight_color: Color for highlighted text.
    :param image_placeholder_text: Placeholder text for the main image area.
    :param image_bg_color: Background color of the image placeholder.
    :param font_family: The font family to use for all text.
    :param paragraph_text: The content paragraph.
    :return: A string containing the HTML code.
    """

    gradient_css = f"background: linear-gradient(to right, {background_gradient[0]}, {background_gradient[1]});"

    html_code = f"""<!DOCTYPE html>
<html lang=\"en\">

<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">

    <title>{title}</title>
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            {gradient_css}
            color: #ffffff;
            font-family: {font_family};
        }}

        .custom-background {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            {gradient_css}
        }}

        .content-container {{
            background-color: rgba(255, 255, 255, {content_bg_opacity});
            border-radius: 10px;
            padding: 30px;
            box-shadow: {content_shadow};
            max-width: 800px;
            width: 90%;
            text-align: center;
        }}

        .custom-title {{
            color: {header_color};
            font-weight: bold;
            font-size: 2rem;
            margin-bottom: 15px;
        }}

        .custom-text {{
            font-size: 1.1rem;
            color: {text_body_color};
            margin-bottom: 20px;
        }}

        .bold {{
            font-weight: bold;
        }}

        .image-placeholder {{
            background-color: {image_bg_color};
            width: 100%;
            height: 200px;
            max-width: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
            border-radius: 5px;
            margin: auto;
        }}
    </style>
</head>
<body>
    <div class=\"custom-background\">
        <div class=\"content-container\">
            <h1 class=\"custom-title\">{header_text}</h1>
            <div class=\"custom-text\">
                {paragraph_text}
            </div>
            <div class=\"d-flex justify-content-center\">
                <div class=\"image-placeholder\">
                    <span>{image_placeholder_text}</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_code

# @title Function Descriptions
def get_function_by_name(name):
  """
  Lấy hàm hoặc lớp từ tên của nó.

  Args:
      name (str): Tên của hàm cần lấy.

  Returns:
      function: Hàm tương ứng với tên được cung cấp.

  Raises:
      ValueError: Nếu không tìm thấy hàm với tên được cung cấp.
  """
  if name == "generate_split_layout_slide1":
      return generate_split_layout_slide1
  elif name == "generate_split_layout_slide2":
      return generate_split_layout_slide2
  elif name == "generate_body_slide1":
      return generate_body_slide1
  elif name == "generate_body_slide2":
      return generate_body_slide2
  elif name == "generate_body_slide3":
      return generate_body_slide3
  else:
      raise ValueError(f"Function with name '{name}' not found.")



TOOLS = [
  {
      "type": "function",
      "function": {
          "name": "generate_split_layout_slide1",
          "description": "Generate a split-layout HTML slide with customizable parameters for left and right sections.",
          "parameters": {
              "type": "object",
              "properties": {
                  "left_bg_color": {"type": "string", "description": "Background color of the left section.", "default": "#F8F8F8"},
                  "left_title": {"type": "string", "description": "Title text in the left section.", "default": "Báo cáo VNPT-AI về bài toán Function Calling"},
                  "left_title_color": {"type": "string", "description": "Color of the title in the left section.", "default": "#2C4B7D"},
                  "left_subtitle": {"type": "string", "description": "Subtitle text in the left section.", "default": "Báo cáo về các bài báo đã tìm hiểu được"},
                  "left_subtitle_color": {"type": "string", "description": "Color of the subtitle in the left section.", "default": "#333"},
                  "left_dots": {"type": "string", "description": "Dots displayed in the left section.", "default": "•••••"},
                  "left_dots_color": {"type": "string", "description": "Color of the dots in the left section.", "default": "#2C4B7D"},
                  "right_bg_color": {"type": "string", "description": "Background color of the right section.", "default": "#F8F8F8"},
                  "right_image_src": {"type": "string", "description": "Source of the image in the right section.", "default": "path-to-your-image/LLM-image.png"},
                  "right_image_alt": {"type": "string", "description": "Alt text for the image in the right section.", "default": "LLM Image"},
                  "decor_bg_color": {"type": "string", "description": "Background color of the decorative container.", "default": "#2C4B7D"},
                  "font_family": {"type": "string", "description": "Font family for the slide content.", "default": "Roboto, Arial, sans-serif"}
              },
              "required": []
          }
      }
  },
  {
      "type": "function",
      "function": {
          "name": "generate_split_layout_slide2",
          "description": "Generate a split-content HTML slide with customizable parameters for the left and right sections.",
          "parameters": {
              "type": "object",
              "properties": {
                  "title": {"type": "string", "description": "The title of the HTML document.", "default": "Split Layout HTML Slide"},
                  "left_bg_color": {"type": "string", "description": "Background color of the left section.", "default": "#2C4B7D"},
                  "left_text_color": {"type": "string", "description": "Text color of the left section.", "default": "white"},
                  "left_number": {"type": "string", "description": "The number displayed in the left section.", "default": "01"},
                  "right_bg_color": {"type": "string", "description": "Background color of the right section.", "default": "#F0F0F0"},
                  "image_placeholder_text_1": {"type": "string", "description": "Text displayed in the first image placeholder.", "default": "LLM (Large Language Model) logo Placeholder"},
                  "image_placeholder_text_2": {"type": "string", "description": "Text displayed in the second image placeholder.", "default": "LLM Agent Pipeline Placeholder"},
                  "bottom_title": {"type": "string", "description": "Title displayed in the bottom right section.", "default": "UltraTool"},
                  "bottom_title_color": {"type": "string", "description": "Color of the bottom title.", "default": "#2C4B7D"},
                  "bottom_description": {"type": "string", "description": "Description text in the bottom right section.", "default": "UltraTool cải thiện gọi hàm nhờ lập kế hoạch, xây dựng tools theo yêu cầu phức tạp, và tạo Tool mới khi cần thiết nếu các tool hiện có không đáp ứng được."},
                  "bottom_description_color": {"type": "string", "description": "Color of the bottom description text.", "default": "#333"},
                  "divider_color": {"type": "string", "description": "Color of the divider in the bottom right section.", "default": "#000"},
                  "font_family": {"type": "string", "description": "Font family for the slide content.", "default": "Roboto, Arial, sans-serif"}
              },
              "required": []
          }
      }
  },
  {
      "type": "function",
      "function": {
          "name": "generate_body_slide1",
          "description": "Generate a professional HTML slide body with customizable content and styling.",
          "parameters": {
              "type": "object",
              "properties": {
                  "title": {"type": "string", "description": "The title of the HTML document.", "default": "Professional HTML Slide Body"},
                  "slide_title": {"type": "string", "description": "The title displayed on the slide.", "default": "2. Importance of Networking:"},
                  "bg_color": {"type": "string", "description": "Background color of the page.", "default": "#e9f7fe"},
                  "text_bg_color": {"type": "string", "description": "Background color of the text container.", "default": "#ffffff"},
                  "text_color": {"type": "string", "description": "Text color of the slide content.", "default": "#2e4e7e"},
                  "keyword_color": {"type": "string", "description": "Color for keywords.", "default": "#004080"},
                  "image_bg_color": {"type": "string", "description": "Background color of the image placeholder.", "default": "#b0d4f1"},
                  "image_placeholder_text": {"type": "string", "description": "Text displayed in the image placeholder.", "default": "Image Placeholder"},
                  "font_family": {"type": "string", "description": "Font family for the slide content.", "default": "Roboto, Arial, sans-serif"},
                  "content_paragraph": {"type": "string", "description": "Main paragraph content.", "default": "Networking is crucial for <span class=\"keyword\">personal development</span>. It fosters:"},
                  "list_items": {"type": "array", "items": {"type": "string"}, "description": "A list of bullet points to include."}
              },
              "required": []
          }
      }
  },
  {
      "type": "function",
      "function": {
          "name": "generate_body_slide2",
          "description": "Generate a professional HTML slide body for presenting content on the power of goal setting.",
          "parameters": {
              "type": "object",
              "properties": {
                  "title": {"type": "string", "description": "The title of the HTML document.", "default": "Power of Goal Setting"},
                  "header_text": {"type": "string", "description": "The main header of the slide.", "default": "The Power of Goal Setting"},
                  "background_color": {"type": "string", "description": "The background color of the entire slide.", "default": "#faf0e6"},
                  "text_color": {"type": "string", "description": "The default text color.", "default": "#333"},
                  "content_bg_color": {"type": "string", "description": "Background color for the content box.", "default": "#ffffff"},
                  "content_shadow": {"type": "string", "description": "Box shadow for the content container.", "default": "0 4px 8px rgba(0, 0, 0, 0.1)"},
                  "header_color": {"type": "string", "description": "Color of the header text.", "default": "#3B5998"},
                  "text_body_color": {"type": "string", "description": "Color of the body text.", "default": "#2f4f4f"},
                  "highlight_color": {"type": "string", "description": "Color for highlighted text.", "default": "#ff4500"},
                  "image_placeholder_text": {"type": "string", "description": "Placeholder text for the main image area.", "default": "[Image Placeholder - Proportioned for future use]"},
                  "image_bg_color": {"type": "string", "description": "Background color of the image placeholder.", "default": "#e1e5ea"},
                  "font_family": {"type": "string", "description": "The font family to use for all text.", "default": "Roboto, Arial, sans-serif"},
                  "paragraph_text": {"type": "string", "description": "The content paragraph.", "default": "<strong>Goal setting</strong> is a crucial aspect of personal development that empowers individuals to define clear objectives, map out strategies, and cultivate a path toward growth."}
              },
              "required": []
          }
      }
  },
  {
      "type": "function",
      "function": {
          "name": "generate_body_slide3",
          "description": "Generate a professional HTML slide body for presenting content on digital transformation and immersive experiences in the creative industries.",
          "parameters": {
              "type": "object",
              "properties": {
                  "title": {"type": "string", "description": "The title of the HTML document.", "default": "Digital Transformation and Immersive Experiences"},
                  "header_text": {"type": "string", "description": "The main header of the slide.", "default": "The Future of Creative Industries"},
                  "background_gradient": {"type": "array", "items": {"type": "string"}, "description": "Gradient colors for the background.", "default": ["#4facfe", "#00c6ff"]},
                  "content_bg_opacity": {"type": "number", "description": "Opacity for the content box background.", "default": 0.8},
                  "content_shadow": {"type": "string", "description": "Box shadow for the content container.", "default": "0 4px 8px rgba(0, 0, 0, 0.1)"},
                  "header_color": {"type": "string", "description": "Color of the header text.", "default": "#333333"},
                  "text_body_color": {"type": "string", "description": "Color of the body text.", "default": "#333333"},
                  "highlight_color": {"type": "string", "description": "Color for highlighted text.", "default": "#ff4500"},
                  "image_placeholder_text": {"type": "string", "description": "Placeholder text for the main image area.", "default": "Image Placeholder"},
                  "image_bg_color": {"type": "string", "description": "Background color of the image placeholder.", "default": "#cccccc"},
                  "font_family": {"type": "string", "description": "The font family to use for all text.", "default": "Roboto, Arial, sans-serif"},
                  "paragraph_text": {"type": "string", "description": "The content paragraph.", "default": "The future of the <span class=\"bold\">creative industries</span> lies at the intersection of digital technology and immersive experiences."}
              },
              "required": []
          }
      }
  }
]

def extract_text_from_docx(file_path):
    logger.info(f"Extracting text from {file_path}")
    doc = Document(file_path)
    text = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(text)

def split_text_into_chunks(text, chunk_size=300, chunk_overlap=50):
    logger.info("Splitting text into chunks")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_text(text)

def create_slide_list(chunks):
    logger.info("Creating slide list")
    slide_list = []
    current_slide = ""
    for section in chunks:
        section = section.strip()
        if not section:
            continue
        if not current_slide:
            current_slide = section
        else:
            if len(current_slide) + len(section) <= 1000:
                current_slide += "\n" + section
            else:
                slide_list.append(current_slide)
                current_slide = section
    if current_slide:
        slide_list.append(current_slide)
    return slide_list

def get_html_slide(pre_slide_content, pre_function_call, slide_content):
    logger.info(f"Generating HTML slide for content: {slide_content[:50]}...")
    demand_prompt = """
Create a slide that matches the following content, choose a function when you think it is best suited with the content:
Previous slide content: {}
Previous function call: {}
Current slide content: {}
Current function call:
"""
    messages = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud."},
        {"role": "user", "content": demand_prompt.format(pre_slide_content, pre_function_call, slide_content)},
    ]
    if not model or not tokenizer:
        logger.error("Model or tokenizer not loaded")
        return '<tool_call>\n{"name": "generate_split_layout_slide1", "arguments": {"left_title": "Error", "left_subtitle": "Model not loaded"}}\n</tool_call>'
    text = tokenizer.apply_chat_template(messages, tools=TOOLS, add_generation_prompt=True, tokenize=False)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=512)
    return tokenizer.batch_decode(outputs)[0][len(text):]

def try_parse_tool_calls(content: str):
    tool_calls = []
    offset = 0
    for i, m in enumerate(re.finditer(r"<tool_call>\n(.+)?\n</tool_call>", content)):
        if i == 0:
            offset = m.start()
        try:
            func = json.loads(m.group(1))
            tool_calls.append({"type": "function", "function": func})
            if isinstance(func["arguments"], str):
                func["arguments"] = json.loads(func["arguments"])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool calls: {e}")
    if tool_calls:
        return {"role": "assistant", "content": content[:offset].strip() if offset > 0 else "", "tool_calls": tool_calls}
    return {"role": "assistant", "content": re.sub(r"<\|im_end\|>$", "", content)}

def filter_string(s, s1, s2):
    start_index = s.find(s1)
    end_index = s.find(s2)
    if start_index != -1 and end_index != -1 and start_index < end_index:
        return s[start_index:end_index + len(s2)]
    return ""

def check_and_insert_char(s, i, char):
    if s[i-1] != char:
        return s[:i] + char + s[i:]
    return s

def clean_slide_function(slide_function_calling_list):
    logger.info("Cleaning slide function calls")
    fixed_list = slide_function_calling_list.copy()
    for i in range(len(fixed_list)):
        fixed_list[i] = filter_string(fixed_list[i], '<tool_call>', '<|im_end|>')
        fixed_list[i] = check_and_insert_char(fixed_list[i], -20, '/')
    return fixed_list

def process_tool_call(tool_call_output):
    logger.info(f"Processing tool call: {tool_call_output[:50]}...")
    parsed_response = try_parse_tool_calls(tool_call_output)
    if not parsed_response or "tool_calls" not in parsed_response or not parsed_response["tool_calls"]:
        raise ValueError(f"Invalid tool_call_output: {tool_call_output}")
    tool_call = parsed_response["tool_calls"][0]
    fn_name = tool_call["function"]["name"]
    fn_args = tool_call["function"]["arguments"]
    try:
        return get_function_by_name(fn_name)(**fn_args)
    except Exception as e:
        logger.error(f"Error calling function {fn_name}: {e}")
        raise ValueError(f"Error calling function {fn_name}: {e}")

def initialize_chromedriver():
    chrome_driver_path = "/home/naver/.cache/selenium/chromedriver/linux64/134.0.6998.165/chromedriver"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(chrome_driver_path)
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("ChromeDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Error initializing ChromeDriver: {e}")
        return None

def capture_slide_image(driver, html_content, output_path):
    logger.info(f"Capturing slide image to {output_path}")
    temp_html_path = "temporal_slide.html"
    with open(temp_html_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    driver.get(f"file://{os.path.abspath(temp_html_path)}")
    driver.set_window_size(1920, 1080)
    screenshot_bytes = driver.get_screenshot_as_png()
    image = Image.open(io.BytesIO(screenshot_bytes))
    image = image.resize((900, 500))
    image.save(output_path)
    os.remove(temp_html_path)
    return image

def filter_invalid_slides(html_content):
    invalid_html = "<html><body><h1>Lỗi tạo slide</h1></body></html>"
    return html_content != invalid_html

criteria = """
1. The title must be clear and descriptive.
2. Text content should be readable with appropriate font size and color contrast.
3. Layout should be balanced, with no overlapping elements.
4. Images (if any) should be relevant and properly aligned.
5. Overall design should be visually appealing and professional.
"""

def evaluate_slide_with_qwen(image_path, tool_call_output):
    logger.info(f"Evaluating slide: {image_path}")
    if not vlm_model or not vlm_processor:
        logger.error("VLM model or processor not loaded")
        return "Model not loaded"
    image = Image.open(image_path)
    question = f"""
Evaluate this slide based on the following criteria:
{criteria}
If the slide does not meet all requirements, provide feedback and an improved version of the tool call.
Current tool call: {tool_call_output}
Your response must follow this format:
<!-- accept/deny -->
<!-- reason -->
<tool_call>
[tool_call_output with updated parameters if deny]
</tool_call>
"""
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": question},
            ],
        }
    ]
    text = vlm_processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = vlm_processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to("cuda" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        generated_ids = vlm_model.generate(**inputs, max_new_tokens=512)
    generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
    output_text = vlm_processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)
    return output_text[0].strip()

def parse_vlm_response(vlm_response):
    logger.info(f"Parsing VLM response: {vlm_response[:50]}...")
    lines = vlm_response.split("\n")
    if len(lines) < 2:
        return None, None, None
    status = lines[0].strip("<!->").strip()
    reason_lines = []
    tool_call = None
    if status == "accept":
        reason_lines = [line.strip() for line in lines[1:] if line.strip()]
    elif status == "deny":
        for i, line in enumerate(lines[1:], start=1):
            if line.strip().startswith("<tool_call>"):
                tool_call = "\n".join(lines[i:]).strip()
                break
            reason_lines.append(line.strip())
    reason = "\n".join(reason_lines) if reason_lines else "No reason provided."
    return status, reason, tool_call

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
    for slide_content in slide_list:
        html_slide_call = get_html_slide(pre_slide_content, pre_function_call, slide_content)
        slide_function_calling_list.append(html_slide_call)
        pre_slide_content = slide_content
        pre_function_call = html_slide_call

    slide_function_calling_list = clean_slide_function(slide_function_calling_list)

    driver = initialize_chromedriver()
    if not driver:
        raise Exception("Cannot initialize ChromeDriver")

    html_files = []
    png_files = []
    max_attempts = 5

    for i, (slide_content, tool_call_output) in enumerate(zip(slide_list, slide_function_calling_list)):
        attempts = 0
        html_content = ""
        slide_image = None

        while attempts < max_attempts:
            attempts += 1
            logger.info(f"Processing slide {i+1}, attempt {attempts}")
            try:
                html_content = process_tool_call(tool_call_output)
                if not filter_invalid_slides(html_content):
                    logger.warning(f"Slide {i+1} is invalid")
                    break

                html_path = f"{output_folder}/slide_{i+1}_attempt_{attempts}.html"
                with open(html_path, "w", encoding="utf-8") as file:
                    file.write(html_content)

                image_path = f"{output_folder}/slide_{i+1}_attempt_{attempts}.png"
                slide_image = capture_slide_image(driver, html_content, image_path)

                evaluation_content = evaluate_slide_with_qwen(image_path, tool_call_output)
                status, reason, new_tool_call = parse_vlm_response(evaluation_content)

                if status == "accept":
                    final_html_path = f"{output_folder}/slide_{i+1}.html"
                    final_png_path = f"{output_folder}/slide_{i+1}.png"
                    with open(final_html_path, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    slide_image.save(final_png_path)
                    html_files.append(final_html_path)
                    png_files.append(final_png_path)
                    logger.info(f"Slide {i+1} accepted")
                    break
                elif status == "deny" and new_tool_call:
                    tool_call_output = new_tool_call
                    logger.info(f"Slide {i+1} denied, retrying with new tool call")
            except Exception as e:
                logger.error(f"Error processing slide {i+1}, attempt {attempts}: {e}")
                break

        if attempts == max_attempts:
            final_html_path = f"{output_folder}/slide_{i+1}.html"
            final_png_path = f"{output_folder}/slide_{i+1}.png"
            with open(final_html_path, "w", encoding="utf-8") as file:
                file.write(html_content)
            if slide_image:
                slide_image.save(final_png_path)
            html_files.append(final_html_path)
            png_files.append(final_png_path)
            logger.warning(f"Slide {i+1} max attempts reached")

    driver.quit()
    logger.info("ChromeDriver closed")
    return html_files, png_files