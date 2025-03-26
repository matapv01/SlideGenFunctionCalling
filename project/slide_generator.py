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
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import logging
import zipfile

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
    vlm_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
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
# @title Functions to
def generate_intro_slide(
    # Title parameters
    title="Introduction",
    title_color='#0F4662',
    title_font_size="42px",
    title_font_style="italic",
    title_margin_bottom="5px",
    title_margin_left="40px",

    # Content parameters
    content_text="Content",
    content_color="#0F4662",
    content_font_size="24px",
    content_line_height="1.6",
    content_width="70%",
    content_margin="0 auto",
    content_text_align="center",

    # Decoration parameters
    dot_color="#0F4662",
    dot_size="10px",
    dot_margin="0 5px",
    dot_count=5,
    line_color="#1a3d5c",
    line_width="50%",
    line_height="2px",
    line_margin="30px auto",

    # Slide parameters
    slide_bg_color="#f5f5f5",
    font_family="Roboto, Arial, sans-serif",
    additional_css=""
):
    """
    Generates a customizable HTML slide with a 'Conclusion' layout featuring dots and lines as decorations.

    Args:
        title: Slide title text
        title_color: Color of the title
        title_font_size: Font size of title
        title_font_style: Font style for title (e.g., "italic")
        title_margin_bottom: Bottom margin for title
        title_margin_left: Left margin for title

        content_text: Main content text
        content_color: Color of content text
        content_font_size: Font size of content
        content_line_height: Line height for content
        content_width: Width of content container
        content_margin: Margin around content
        content_text_align: Text alignment for content

        dot_color: Color of decorative dots
        dot_size: Size of decorative dots
        dot_margin: Margin between dots
        dot_count: Number of dots in each row
        line_color: Color of horizontal lines
        line_width: Width of horizontal lines
        line_height: Height/thickness of horizontal lines
        line_margin: Margin around horizontal lines

        slide_bg_color: Background color of the slide
        font_family: Font family for all text
        additional_css: Additional CSS styles
    """

    # Generate dots HTML
    dots_html = ""
    for _ in range(dot_count):
        dots_html += f'<span class="dot"></span>'

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: {slide_bg_color};
        }}
        .slide-container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 40px;
            box-sizing: border-box;
        }}
        .title {{
            font-size: {title_font_size};
            color: {title_color};
            font-style: {title_font_style};
            margin-bottom: {title_margin_bottom};
            margin-left: {title_margin_left};
        }}
        .content-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
        }}
        .content {{
            color: {content_color};
            font-size: {content_font_size};
            line-height: {content_line_height};
            width: {content_width};
            margin: {content_margin};
            text-align: {content_text_align};
        }}
        .horizontal-line {{
            width: {line_width};
            height: {line_height};
            background-color: {line_color};
            margin: {line_margin};
        }}
        .dots-container {{
            display: flex;
            justify-content: center;
            margin: 10px 0;
        }}
        .dot {{
            display: inline-block;
            width: {dot_size};
            height: {dot_size};
            border-radius: 50%;
            background-color: {dot_color};
            margin: {dot_margin};
        }}
        {additional_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="title">{title}</div>

        <div class="content-container">
            <div class="dots-container">
                {dots_html}
            </div>

            <div class="horizontal-line"></div>

            <div class="content">
                {content_text}
            </div>

            <div class="horizontal-line"></div>

            <div class="dots-container">
                {dots_html}
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_code


def generate_body_slide1(
    title="Professional HTML Slide",
    title_font_size="42px",
    slide_title="Slide Title",
    bg_color="#E8F5E9",
    text_bg_color="#FFFFFF",
    text_color="#2E7D32",
    keyword_color="#1B5E20",
    image_bg_color="#C8E6C9",
    image_placeholder_text="Image Placeholder",
    font_family="Roboto, Arial, sans-serif",
    content_paragraph="This is a customizable slide. Add your content here:",
    para_font_size="24px",
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
            "<span class=\"keyword\">Point 1</span>: Description of point 1.",
            "<span class=\"keyword\">Point 2</span>: Description of point 2.",
            "<span class=\"keyword\">Point 3</span>: Description of point 3.",
            "<span class=\"keyword\">Point 4</span>: Description of point 4."
        ]

    list_html = "\n".join(f"<li>{item}</li>" for item in list_items)

    html_code = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
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
            font-size: {title_font_size};
            margin-bottom: 15px;
            font-weight: bolder;
        }}
        .slide-content {{
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            background-color: {text_bg_color};
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            color: {text_color};
            max-width: 1100px; /* Tăng kích thước tối đa của khung */
            width: 100%;
        }}
        .text-content {{
            flex: 3; /* Tăng tỉ lệ phần text để mở rộng */
            margin-right: 30px;
        }}
        .text-content p {{
            margin-bottom: 18px;
            font-size: {para_font_size};
            line-height: 1.7;
        }}
        .text-content ul {{
            list-style: none;
            padding: 0;
        }}
        .text-content li {{
            margin-top: 14px;
            font-size: {para_font_size};
        }}
        .image-placeholder {{
            flex: 1;
            background-color: {image_bg_color};
            width: 300px; /* Tăng kích thước ảnh */
            height: 300px;
            border-radius: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #333333;
            font-size: 24px;
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
    title="Slide Header",
    header_text="Key Insights",
    header_font_size="42px",
    background_color="#E8F5E9",
    text_color="#004D40",
    content_bg_color="#FFFFFF",
    content_shadow="0 6px 12px rgba(0, 0, 0, 0.1)",
    header_color="#00251A",
    text_body_color="#00695C",
    highlight_color="#FF4500",
    image_placeholder_text="[Image Placeholder]",
    image_bg_color="#B2DFDB",
    font_family="Roboto, Arial, sans-serif",
    paragraph_text="This is a customizable slide content area. You can add any relevant information here",
    para_font_size="24px"
):
    """
    Generate a professional HTML slide body for various presentation topics.

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
    <title>{title}</title>
    <script src=\"https://polyfill.io/v3/polyfill.min.js?features=es6\"></script>
    <script id=\"MathJax-script\" async src=\"https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js\"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href=\"https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
        body, html {{
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
            border-radius: 12px;
            box-shadow: {content_shadow};
            width: 90%;
            padding: 40px;
            color: {text_color};
        }}

        .text-section {{
            flex: 2;
            padding: 30px;
            color: {text_body_color};
        }}

        .image-box {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {image_bg_color};
            border-radius: 12px;
            width: 300px;
            height: 300px;
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }}

        h1 {{
            color: {header_color};
            font-size: {header_font_size};
        }}

        p {{
            font-size: {para_font_size};
            line-height: 1.8em;
        }}

        strong {{
            color: {highlight_color};
            font-weight: bold;
        }}

        @media (max-width: 768px) {{
            .content-box {{
                flex-direction: column;
                align-items: center;
                text-align: center;
                padding: 20px;
            }}
            .image-box {{
                width: 150px;
                height: 150px;
                margin-top: 20px;
            }}
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
                {image_placeholder_text}
            </div>
        </div>
    </div>
</body>

</html>"""

    return html_code

def generate_body_slide3(
    title="title",
    tile_font_size = "42px",
    subtitle="subtitle",
    subtitle_font_size = "32px",
    content_paragraphs=[
        "Paragraph 1 Present with ease and wow any audience with Canva Presentations. Choose from over a thousand professionally-made templates to fit any objective or topic. Make it your own by customizing it with text and photos.",
        "Paragraph 2 Present with ease and wow any audience with Canva Presentations. Choose from over a thousand professionally-made templates to fit any objective or topic. Make it your own by customizing it with text and photos."
    ],
    left_bg_color="#F3F6FA",
    right_bg_color="#0B1320",
    text_color="#FFFFFF",
    title_color="#000000",
    subtitle_color="#333333",
    icon_color="#FF9800",
    corner_icon_color="#3D5AFE",
    font_family="Roboto, Arial, sans-serif"
):
    paragraphs_html = "".join(f"<p>{p}</p>" for p in content_paragraphs)
    
    html_code = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            height: 100vh;
            width: 100vw;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {left_bg_color};
        }}
        .slide-container {{
            display: flex;
            width: 100vw;
            height: 100vh;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 0;
            overflow: hidden;
        }}
        .left-container {{
            flex: 1;
            padding: 60px;
            background-color: {left_bg_color};
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: flex-start;
        }}
        .title {{
            font-size: {tile_font_size};
            font-weight: bold;
            color: {title_color};
            margin-bottom: 20px;
            align-self: flex-start;
        }}
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            align-self: flex-start;
        }}
        .right-container {{
            flex: 2;
            padding: 40px;
            background-color: {right_bg_color};
            color: {text_color};
            border-radius: 20px;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        .corner-icons {{
            position: absolute;
            top: 10px;
            right: 10px;
            display: flex;
            gap: 5px;
        }}
        .corner-icons span, .bottom-icons span {{
            width: 12px;
            height: 12px;
            background-color: {corner_icon_color};
            border-radius: 50%;
            display: inline-block;
        }}
        .bottom-icons {{
            position: absolute;
            bottom: 10px;
            left: 20px;
            display: flex;
            gap: 5px;
        }}
        .bottom-icons span {{ background-color: {icon_color}; }}
    </style>
</head>
<body>
    <div class=\"slide-container\">
        <div class=\"left-container\">
            <div class=\"title\">{title}</div>
            <div class=\"subtitle\">{subtitle}</div>
        </div>
        <div class=\"right-container\">
            <div class=\"corner-icons\">
                <span></span><span></span><span></span>
            </div>
            {paragraphs_html}
            <div class=\"bottom-icons\">
                <span></span><span></span><span></span>
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_code

def generate_body_slide4(
    title="Learning Objectives",
    title_font_size="42px",
    para_font_size="24px",
    objectives=None,
    bg_color="#E8F5E9",
    title_color='#2E7D32',
    objective_bg_color="#388E3C",
    objective_text_color="#ffffff",
    content_text_color="#ffffff",
    box_bg_color="#1B5E20",
    box_shadow="0 4px 12px rgba(0, 0, 0, 0.1)",
    box_border_radius="10px",
    box_padding="20px",
    font_family="Roboto, Arial, sans-serif",
    image_src="path-to-your-image/ocean-background.png",
    image_width="100%",
    image_height="auto",
    border_radius="50%"
):
    if objectives is None:
        objectives = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Maecenas euismod magna in sem rutrum luctus. Sed ultricies diam non venenatis dictum.",
            "Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        ]
    
    objective_html = "".join(
        f"""
        <div class="objective">
            <div class="number">{index + 1}</div>
            <div class="box">
                <p>{content}</p>
            </div>
        </div>
        """
        for index, content in enumerate(objectives)
    )
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: {bg_color};
            color: {content_text_color};
            display: flex;
            justify-content: center;
            align-items: center;
            background-image: url('{image_src}');
            background-size: cover;
            background-position: center;
        }}
        .container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            width: 100%;
            max-width: 1200px;
            padding: 20px;
        }}
        .title {{
            font-size: {title_font_size};
            margin-bottom: 40px;
            color: {title_color};
        }}
        .objectives-container {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            width: 100%;
        }}
        .objective {{
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100%;
        }}
        .number {{
            background-color: {objective_bg_color};
            color: {objective_text_color};
            font-size: 28px;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: {border_radius};
            margin-bottom: 20px;
        }}
        .box {{
            background-color: {box_bg_color};
            color: {content_text_color};
            padding: {box_padding};
            border-radius: {box_border_radius};
            box-shadow: {box_shadow};
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            box-sizing: border-box;
        }}
        .box p {{
            font-size: {para_font_size};
            line-height: 1.6;
            margin: 0;
            text-align: center;
        }}
        @media (max-width: 768px) {{
            .objectives-container {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">{title}</h1>
        <div class="objectives-container">
            {objective_html}
        </div>
    </div>
</body>
</html>"""
    return html_code


def generate_body_slide5(
    title="Title",
    title_font_size="42px",
    subtitle1 = "Subtitle1",
    subtitle2 = "Subtitle2",
    subtile_font_size="24px",
    content_1="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris eleifend magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.",
    content_2="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris eleifend magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.",
    content_font_size="20px",
    bg_color="#0277BD",  # Màu nền chính
    title_color="#FFFFFF",  # Màu chữ tiêu đề
    content_color="#E1F5FE",  # Màu chữ nội dung
    number_bg_color="#039BE5",  # Màu nền số thứ tự
    number_text_color="#FFFFFF",  # Màu chữ số thứ tự
    image_bg_color="#E1F5FE",  # Màu nền khung chứa ảnh
    image_width="70%",  # Chiều rộng khung chứa ảnh
    image_height="60%",  # Chiều cao khung chứa ảnh
    border_radius="10px",  # Độ bo tròn cho các phần tử
    font_family="Roboto, Arial, sans-serif"  # Font chữ
):
    """
    Generate a professional HTML slide body with customizable parameters.
    :param title: Tiêu đề của slide.
    :param content_1: Nội dung phần 01.
    :param content_2: Nội dung phần 02.
    :param bg_color: Màu nền chính.
    :param title_color: Màu chữ tiêu đề.
    :param content_color: Màu chữ nội dung.
    :param number_bg_color: Màu nền số thứ tự.
    :param number_text_color: Màu chữ số thứ tự.
    :param image_bg_color: Màu nền khung chứa ảnh.
    :param image_width: Chiều rộng khung chứa ảnh.
    :param image_height: Chiều cao khung chứa ảnh.
    :param border_radius: Độ bo tròn cho các phần tử.
    :param font_family: Font chữ sử dụng.
    :return: Mã HTML của slide.
    """
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: {bg_color};
            color: {content_color};
        }}
        .container {{
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}
        .left-section {{
            flex: 1;
            padding: 40px;
            box-sizing: border-box;
        }}
        .title {{
            font-size: {title_font_size};
            color: {title_color};
            margin-bottom: 20px;
        }}
        .number {{
            background-color: {number_bg_color};
            color: {number_text_color};
            font-size: {subtile_font_size};
            padding: 10px 20px;
            border-radius: {border_radius};
            margin-bottom: 10px;
        }}
        .content {{
            font-size: {content_font_size};
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        .right-section {{
            position: relative;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }}
        .image-container {{
            width: {image_width};
            height: {image_height};
            background-color: {image_bg_color};
            border-radius: {border_radius};
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .bubble {{
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: #00c6ff;
            border-radius: 50%;
            opacity: 0.8;
        }}
        .bubble.bubble-1 {{
            top: 50px;
            right: 150px;
        }}
        .bubble.bubble-2 {{
            top: 100px;
            right: 100px;
        }}
        .bubble.bubble-3 {{
            top: 150px;
            right: 50px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="left-section">
            <h1 class="title">{title}</h1>
            <div class="number">{subtitle1}</div>
            <p class="content">{content_1}</p>
            <div class="number">{subtitle2}</div>
            <p class="content">{content_2}</p>
        </div>
        <div class="right-section">
            <div class="image-container">Image</div>
            <div class="bubble bubble-1"></div>
            <div class="bubble bubble-2"></div>
            <div class="bubble bubble-3"></div>
        </div>
    </div>
</body>
</html>"""
    return html_code

def generate_body_slide6(
    title="TITLE",
    sections=None,
    title_font_size="42px",
    section_title_font_size="24px",
    section_content_font_size="20px",
    title_color="#1a1a1a",
    title_font_family="Roboto, Arial, sans-serif",
    subtitle_bg_color="#1a1a1a",
    subtitle_text_color="#ffffff",
    box_border_color="#1a1a1a",
    box_border_radius="12px",
    box_padding="20px",
    box_shadow="0 4px 12px rgba(0, 0, 0, 0.15)",
    font_family="Roboto, Arial, sans-serif",
    bullet_color="#333",
):
    if sections is None:
        sections = {
            "SubTitle1": [
                "Content1",
                "Content2",
                "Content3",
                "Content4",
            ],
            "SubTitle2": [
                "Content5",
                "Content6",
                "Content7",
            ],
            "SubTitle3": [
                "Content8",
                "Content9",
                "Content10",
            ],
        }

    sections_html = "".join(
        f"""
        <div class="section">
            <div class="section-title">{section}</div>
            <div class="section-content">
                <ul>
                    {''.join(f'<li>{point}</li>' for point in points)}
                </ul>
            </div>
        </div>
        """
        for section, points in sections.items()
    )

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
        body {{
            font-family: {font_family};
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #f8f9fa;
        }}
        .title {{
            font-size: {title_font_size};
            font-family: {title_font_family};
            font-weight: bold;
            color: {title_color};
            text-align: center;
            margin-top: 40px;
        }}
        .divider {{
            width: 60%;
            height: 3px;
            background-color: {title_color};
            margin: 10px auto 20px;
            position: relative;
        }}
        .dots {{
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            position: absolute;
            right: 0;
            top: -6px;
        }}
        .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        .dot:nth-child(1) {{ background-color: #ff6b6b; }}
        .dot:nth-child(2) {{ background-color: #ffa502; }}
        .dot:nth-child(3) {{ background-color: #1e90ff; }}
        .sections-container {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}
        .section {{
            width: 300px;
            border: 2px solid {box_border_color};
            border-radius: {box_border_radius};
            box-shadow: {box_shadow};
            overflow: hidden;
            background: white;
        }}
        .section-title {{
            background-color: {subtitle_bg_color};
            color: {subtitle_text_color};
            font-size: {section_title_font_size};
            font-weight: bold;
            padding: 12px;
            text-align: center;
            border-top-left-radius: {box_border_radius};
            border-top-right-radius: {box_border_radius};
        }}
        .section-content {{
            padding: {box_padding};
        }}
        .section-content ul {{
            padding-left: 20px;
            margin: 0;
        }}
        .section-content li {{
            font-size: {section_content_font_size};
            line-height: 1.6;
            color: {bullet_color};
            list-style-type: disc;
        }}
    </style>
</head>
<body>
    <div class="title">{title}</div>
    <div class="divider">
        <div class="dots">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    </div>
    <div class="sections-container">
        {sections_html}
    </div>
</body>
</html>"""
    
    return html_code

def generate_body_slide7(
    title="Title",
    content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis vel dolor ante. Nullam feugiat egestas elit et vehicula. Proin venenatis, orci nec cursus tristique, nulla risus mattis eros, id accumsan massa elit eu augue. Mauris massa ipsum, pharetra id nibh eget, sodales facilisis enim.",
    title_font_size="42px",
    content_font_size="24px",
    bg_color="#FFFBEB",
    title_color="#000000",
    content_color="#333333",
    corner_decoration_color="#FDE68A",
    font_family="Roboto, Arial, sans-serif"
):
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
        }}
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {bg_color};
            font-family: {font_family};
        }}
        .slide-container {{
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 0 10%;
            box-sizing: border-box;
            background-color: white;
        }}
        .corner-decoration {{
            position: absolute;
            width: 200px;
            height: 200px;
            background-color: {corner_decoration_color};
            opacity: 0.3;
            z-index: 1;
        }}
        .top-left {{
            top: 0;
            left: 0;
            border-radius: 0 0 100% 0;
        }}
        .bottom-right {{
            bottom: 0;
            right: 0;
            border-radius: 100% 0 0 0;
        }}
        .title {{
            font-size: {title_font_size};
            text-align: center;
            color: {title_color};
            margin-bottom: 30px;
            font-weight: bold;
            letter-spacing: 4px;
            z-index: 2;
            position: relative;
            top: -50px;
        }}
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            line-height: 1.8;
            max-width: 1000px;
            padding: 0 30px;
            z-index: 2;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="corner-decoration top-left"></div>
        <div class="corner-decoration bottom-right"></div>
        <h1 class="title">{title}</h1>
        <p class="content">{content}</p>
    </div>
</body>
</html>"""
    return html_code


def generate_body_slide8(
    title="DISCUSSION",
    points=[
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis vel dolor ante.",
        "Nullam feugiat egestas elit et vehicula. Proin venenatis, orci nec cursus tristique."
    ],
    title_font_size="42px",
    content_font_size="24px",
    bg_color="#FFFBEB",
    title_color="#000000",
    content_color="#333333",
    corner_decoration_color="#FDE68A",
    font_family="Roboto, Arial, sans-serif"
):
    # Xử lý danh sách các điểm
    points_html = "".join(f"<li>{point}</li>" for point in points)
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
        }}
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: {bg_color};
            font-family: {font_family};
        }}
        .slide-container {{
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 0 10%;
            box-sizing: border-box;
            background-color: white;
        }}
        .corner-decoration {{
            position: absolute;
            width: 200px;
            height: 200px;
            background-color: {corner_decoration_color};
            opacity: 0.3;
            z-index: 1;
        }}
        .top-left {{
            top: 0;
            left: 0;
            border-radius: 0 0 100% 0;
        }}
        .bottom-right {{
            bottom: 0;
            right: 0;
            border-radius: 100% 0 0 0;
        }}
        .title {{
            font-size: {title_font_size};
            text-align: center;
            color: {title_color};
            margin-bottom: 30px;
            font-weight: bold;
            letter-spacing: 4px;
            z-index: 2;
            position: relative;
            top: -50px;
        }}
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            line-height: 1.8;
            max-width: 1000px;
            padding: 0 30px;
            z-index: 2;
        }}
        /* List styling */
        ul {{
            list-style-type: disc;
            padding-left: 40px;
            margin: 0;
        }}
        li {{
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="corner-decoration top-left"></div>
        <div class="corner-decoration bottom-right"></div>
        <h1 class="title">{title}</h1>
        <div class="content">
            <ul>
                {points_html}
            </ul>
        </div>
    </div>
</body>
</html>"""
    return html_code

def generate_conclusion_slide(
    # Title parameters
    title="Conclusion",
    title_color='#0F4662',
    title_font_size="32px",
    title_font_style="italic",
    title_margin_bottom="5px",
    title_margin_left="40px",

    # Content parameters
    content_text="Content",
    content_color="#0F4662",
    content_font_size="16px",
    content_line_height="1.6",
    content_width="70%",
    content_margin="0 auto",
    content_text_align="center",

    # Decoration parameters
    dot_color="#0F4662",
    dot_size="10px",
    dot_margin="0 5px",
    dot_count=5,
    line_color="#1a3d5c",
    line_width="50%",
    line_height="2px",
    line_margin="30px auto",

    # Slide parameters
    slide_bg_color="#f5f5f5",
    font_family="Roboto, Arial, sans-serif",
    additional_css=""
):
    """
    Generates a customizable HTML slide with a 'Conclusion' layout featuring dots and lines as decorations.

    Args:
        title: Slide title text
        title_color: Color of the title
        title_font_size: Font size of title
        title_font_style: Font style for title (e.g., "italic")
        title_margin_bottom: Bottom margin for title
        title_margin_left: Left margin for title

        content_text: Main content text
        content_color: Color of content text
        content_font_size: Font size of content
        content_line_height: Line height for content
        content_width: Width of content container
        content_margin: Margin around content
        content_text_align: Text alignment for content

        dot_color: Color of decorative dots
        dot_size: Size of decorative dots
        dot_margin: Margin between dots
        dot_count: Number of dots in each row
        line_color: Color of horizontal lines
        line_width: Width of horizontal lines
        line_height: Height/thickness of horizontal lines
        line_margin: Margin around horizontal lines

        slide_bg_color: Background color of the slide
        font_family: Font family for all text
        additional_css: Additional CSS styles
    """

    # Generate dots HTML
    dots_html = ""
    for _ in range(dot_count):
        dots_html += f'<span class="dot"></span>'

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: {slide_bg_color};
        }}
        .slide-container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 40px;
            box-sizing: border-box;
        }}
        .title {{
            font-size: {title_font_size};
            color: {title_color};
            font-style: {title_font_style};
            margin-bottom: {title_margin_bottom};
            margin-left: {title_margin_left};
        }}
        .content-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
        }}
        .content {{
            color: {content_color};
            font-size: {content_font_size};
            line-height: {content_line_height};
            width: {content_width};
            margin: {content_margin};
            text-align: {content_text_align};
        }}
        .horizontal-line {{
            width: {line_width};
            height: {line_height};
            background-color: {line_color};
            margin: {line_margin};
        }}
        .dots-container {{
            display: flex;
            justify-content: center;
            margin: 10px 0;
        }}
        .dot {{
            display: inline-block;
            width: {dot_size};
            height: {dot_size};
            border-radius: 50%;
            background-color: {dot_color};
            margin: {dot_margin};
        }}
        {additional_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="title">{title}</div>

        <div class="content-container">
            <div class="dots-container">
                {dots_html}
            </div>

            <div class="horizontal-line"></div>

            <div class="content">
                {content_text}
            </div>

            <div class="horizontal-line"></div>

            <div class="dots-container">
                {dots_html}
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_code

def generate_end_slide(

    # Content parameters
    content_text="THANK YOU!",
    content_color="#0F4662",
    content_font_size="56px",
    content_line_height="1.6",
    content_width="70%",
    content_margin="0 auto",
    content_text_align="center",

    # Decoration parameters
    dot_color="#0F4662",
    dot_size="10px",
    dot_margin="0 5px",
    dot_count=5,
    line_color="#1a3d5c",
    line_width="50%",
    line_height="2px",
    line_margin="30px auto",

    # Slide parameters
    slide_bg_color="#f5f5f5",
    font_family="Robo, Arial, sans-serif",
    additional_css=""
):
    """
    Generates a customizable HTML slide with a 'Conclusion' layout featuring dots and lines as decorations.

    Args:
        title: Slide title text
        title_color: Color of the title
        title_font_size: Font size of title
        title_font_style: Font style for title (e.g., "italic")
        title_margin_bottom: Bottom margin for title
        title_margin_left: Left margin for title

        content_text: Main content text
        content_color: Color of content text
        content_font_size: Font size of content
        content_line_height: Line height for content
        content_width: Width of content container
        content_margin: Margin around content
        content_text_align: Text alignment for content

        dot_color: Color of decorative dots
        dot_size: Size of decorative dots
        dot_margin: Margin between dots
        dot_count: Number of dots in each row
        line_color: Color of horizontal lines
        line_width: Width of horizontal lines
        line_height: Height/thickness of horizontal lines
        line_margin: Margin around horizontal lines

        slide_bg_color: Background color of the slide
        font_family: Font family for all text
        additional_css: Additional CSS styles
    """

    # Generate dots HTML
    dots_html = ""
    for _ in range(dot_count):
        dots_html += f'<span class="dot"></span>'

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: {slide_bg_color};
        }}
        .slide-container {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: 40px;
            box-sizing: border-box;
        }}
        .content-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
        }}
        .content {{
            color: {content_color};
            font-size: {content_font_size};
            line-height: {content_line_height};
            width: {content_width};
            margin: {content_margin};
            text-align: {content_text_align};
        }}
        .horizontal-line {{
            width: {line_width};
            height: {line_height};
            background-color: {line_color};
            margin: {line_margin};
        }}
        .dots-container {{
            display: flex;
            justify-content: center;
            margin: 10px 0;
        }}
        .dot {{
            display: inline-block;
            width: {dot_size};
            height: {dot_size};
            border-radius: 50%;
            background-color: {dot_color};
            margin: {dot_margin};
        }}
        {additional_css}
    </style>
</head>
<body>
    <div class="slide-container">

        <div class="content-container">
            <div class="dots-container">
                {dots_html}
            </div>

            <div class="horizontal-line"></div>

            <div class="content">
                {content_text}
            </div>

            <div class="horizontal-line"></div>

            <div class="dots-container">
                {dots_html}
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_code


# @title Function Descriptions
def get_function_by_name(name):
    if name == "generate_intro_slide":
        return generate_intro_slide
    elif name == "generate_body_slide1":
        return generate_body_slide1
    elif name == "generate_body_slide2":
        return generate_body_slide2
    elif name == "generate_body_slide3":
        return generate_body_slide3
    elif name == "generate_body_slide4":
        return generate_body_slide4
    elif name == "generate_body_slide5":
        return generate_body_slide5
    elif name == "generate_body_slide8":
        return generate_body_slide8
    elif name == "generate_conclusion_slide":
        return generate_conclusion_slide
    else:
        raise ValueError(f"Function with name '{name}' not found.")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "generate_intro_slide",
            "description": "Generates a customizable HTML slide with an introduction layout featuring dots and lines as decorations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "default": "Introduction", "description": "Slide title text"},
                    "title_color": {"type": "string", "default": "#0F4662", "description": "Color of the title"},
                    "title_font_size": {"type": "string", "default": "42px", "description": "Font size of the title"},
                    "title_font_style": {"type": "string", "default": "italic", "description": "Font style for the title (e.g., 'italic')"},
                    "title_margin_bottom": {"type": "string", "default": "5px", "description": "Bottom margin for the title"},
                    "title_margin_left": {"type": "string", "default": "40px", "description": "Left margin for the title"},
                    "content_text": {"type": "string", "default": "Content", "description": "Main content text"},
                    "content_color": {"type": "string", "default": "#0F4662", "description": "Color of content text"},
                    "content_font_size": {"type": "string", "default": "24px", "description": "Font size of content"},
                    "content_line_height": {"type": "string", "default": "1.6", "description": "Line height for content"},
                    "content_width": {"type": "string", "default": "70%", "description": "Width of content container"},
                    "content_margin": {"type": "string", "default": "0 auto", "description": "Margin around content"},
                    "content_text_align": {"type": "string", "default": "center", "description": "Text alignment for content"},
                    "dot_color": {"type": "string", "default": "#0F4662", "description": "Color of decorative dots"},
                    "dot_size": {"type": "string", "default": "10px", "description": "Size of decorative dots"},
                    "dot_margin": {"type": "string", "default": "0 5px", "description": "Margin between dots"},
                    "dot_count": {"type": "integer", "default": 5, "description": "Number of dots in each row"},
                    "line_color": {"type": "string", "default": "#1a3d5c", "description": "Color of horizontal lines"},
                    "line_width": {"type": "string", "default": "50%", "description": "Width of horizontal lines"},
                    "line_height": {"type": "string", "default": "2px", "description": "Height/thickness of horizontal lines"},
                    "line_margin": {"type": "string", "default": "30px auto", "description": "Margin around horizontal lines"},
                    "slide_bg_color": {"type": "string", "default": "#f5f5f5", "description": "Background color of the slide"},
                    "font_family": {"type": "string", "default": "Roboto, Arial, sans-serif", "description": "Font family for all text"},
                    "additional_css": {"type": "string", "default": "", "description": "Additional CSS styles"}
                },
                "required": []
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "generate_body_slide2",
            "description": "Generate a professional HTML slide body with a header, a content paragraph, and an image placeholder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "default": "Slide Header", "description": "The title of the HTML document"},
                    "header_text": {"type": "string", "default": "Key Insights", "description": "The main header of the slide"},
                    "header_font_size": {"type": "string", "default": "42px", "description": "Font size of the header text"},
                    "background_color": {"type": "string", "default": "#E8F5E9", "description": "The background color of the entire slide"},
                    "text_color": {"type": "string", "default": "#004D40", "description": "The default text color"},
                    "content_bg_color": {"type": "string", "default": "#FFFFFF", "description": "Background color for the content box"},
                    "content_shadow": {"type": "string", "default": "0 6px 12px rgba(0, 0, 0, 0.1)", "description": "Box shadow for the content container"},
                    "header_color": {"type": "string", "default": "#00251A", "description": "Color of the header text"},
                    "text_body_color": {"type": "string", "default": "#00695C", "description": "Color of the body text"},
                    "highlight_color": {"type": "string", "default": "#FF4500", "description": "Color for highlighted text"},
                    "image_placeholder_text": {"type": "string", "default": "[Image Placeholder]", "description": "Placeholder text for the main image area"},
                    "image_bg_color": {"type": "string", "default": "#B2DFDB", "description": "Background color of the image placeholder"},
                    "font_family": {"type": "string", "default": "Roboto, Arial, sans-serif", "description": "The font family to use for all text"},
                    "paragraph_text": {"type": "string", "default": "This is a customizable slide content area. You can add any relevant information here", "description": "The content paragraph"},
                    "para_font_size": {"type": "string", "default": "24px", "description": "Font size of the paragraph text"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_body_slide3",
            "description": "Generate a professional HTML slide body with a split layout, including a title, subtitle, and multiple content paragraphs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "default": "title", "description": "The main title of the slide"},
                    "tile_font_size": {"type": "string", "default": "42px", "description": "Font size of the title (Note: parameter name in function is 'tile_font_size', not 'title_font_size')"},
                    "subtitle": {"type": "string", "default": "subtitle", "description": "The subtitle of the slide"},
                    "subtitle_font_size": {"type": "string", "default": "32px", "description": "Font size of the subtitle"},
                    "content_paragraphs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [
                            "Paragraph 1 Present with ease and wow any audience with Canva Presentations. Choose from over a thousand professionally-made templates to fit any objective or topic. Make it your own by customizing it with text and photos.",
                            "Paragraph 2 Present with ease and wow any audience with Canva Presentations. Choose from over a thousand professionally-made templates to fit any objective or topic. Make it your own by customizing it with text and photos."
                        ],
                        "description": "A list of paragraphs to display in the right section"
                    },
                    "left_bg_color": {"type": "string", "default": "#F3F6FA", "description": "Background color of the left section"},
                    "right_bg_color": {"type": "string", "default": "#0B1320", "description": "Background color of the right section"},
                    "text_color": {"type": "string", "default": "#FFFFFF", "description": "Text color of the content paragraphs"},
                    "title_color": {"type": "string", "default": "#000000", "description": "Color of the title"},
                    "subtitle_color": {"type": "string", "default": "#333333", "description": "Color of the subtitle"},
                    "icon_color": {"type": "string", "default": "#FF9800", "description": "Color of the bottom decorative icons"},
                    "corner_icon_color": {"type": "string", "default": "#3D5AFE", "description": "Color of the corner decorative icons"},
                    "font_family": {"type": "string", "default": "Roboto, Arial, sans-serif", "description": "Font family for the slide content"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_body_slide4",
            "description": "Generate a professional HTML slide body with a structured content box and numbered items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "default": "Learning Objectives", "description": "The main title of the slide"},
                    "title_font_size": {"type": "string", "default": "42px", "description": "Font size of the title"},
                    "para_font_size": {"type": "string", "default": "24px", "description": "Font size of the paragraph text"},
                    "objectives": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [
                            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                            "Maecenas euismod magna in sem rutrum luctus. Sed ultricies diam non venenatis dictum.",
                            "Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.",
                            "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
                        ],
                        "description": "A list of objectives or key points to be displayed"
                    },
                    "bg_color": {"type": "string", "default": "#E8F5E9", "description": "The background color of the slide"},
                    "title_color": {"type": "string", "default": "#2E7D32", "description": "The color of the slide title"},
                    "objective_bg_color": {"type": "string", "default": "#388E3C", "description": "The background color for the numbered items"},
                    "objective_text_color": {"type": "string", "default": "#ffffff", "description": "The text color of the numbered items"},
                    "content_text_color": {"type": "string", "default": "#ffffff", "description": "The text color of the content inside the box"},
                    "box_bg_color": {"type": "string", "default": "#1B5E20", "description": "The background color of the content box"},
                    "box_shadow": {"type": "string", "default": "0 4px 12px rgba(0, 0, 0, 0.1)", "description": "The box shadow effect for the content box"},
                    "box_border_radius": {"type": "string", "default": "10px", "description": "The border radius for the content box"},
                    "box_padding": {"type": "string", "default": "20px", "description": "The padding inside the content box"},
                    "font_family": {"type": "string", "default": "Roboto, Arial, sans-serif", "description": "The font family used for the slide"},
                    "image_src": {"type": "string", "default": "path-to-your-image/ocean-background.png", "description": "The source path for the background image"},
                    "image_width": {"type": "string", "default": "100%", "description": "The width of the background image"},
                    "image_height": {"type": "string", "default": "auto", "description": "The height of the background image"},
                    "border_radius": {"type": "string", "default": "50%", "description": "The border radius applied to the numbered items"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_body_slide5",
            "description": "Generate a structured HTML slide with two content sections and an image placeholder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "default": "Title", "description": "The main title of the slide"},
                    "title_font_size": {"type": "string", "default": "42px", "description": "Font size of the title"},
                    "subtitle1": {"type": "string", "default": "Subtitle1", "description": "Subtitle for the first content section"},
                    "subtitle2": {"type": "string", "default": "Subtitle2", "description": "Subtitle for the second content section"},
                    "subtile_font_size": {"type": "string", "default": "24px", "description": "Font size of the subtitles (Note: parameter name in function is 'subtile_font_size', not 'subtitle_font_size')"},
                    "content_1": {"type": "string", "default": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris eleifend magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.", "description": "The content for the first section"},
                    "content_2": {"type": "string", "default": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris eleifend magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.", "description": "The content for the second section"},
                    "content_font_size": {"type": "string", "default": "20px", "description": "Font size of the content text"},
                    "bg_color": {"type": "string", "default": "#0277BD", "description": "The main background color of the slide"},
                    "title_color": {"type": "string", "default": "#FFFFFF", "description": "The text color of the title"},
                    "content_color": {"type": "string", "default": "#E1F5FE", "description": "The text color of the content sections"},
                    "number_bg_color": {"type": "string", "default": "#039BE5", "description": "The background color of the numbered elements"},
                    "number_text_color": {"type": "string", "default": "#FFFFFF", "description": "The text color of the numbered elements"},
                    "image_bg_color": {"type": "string", "default": "#E1F5FE", "description": "The background color of the image container"},
                    "image_width": {"type": "string", "default": "70%", "description": "The width of the image container"},
                    "image_height": {"type": "string", "default": "60%", "description": "The height of the image container"},
                    "border_radius": {"type": "string", "default": "10px", "description": "The border radius applied to various elements"},
                    "font_family": {"type": "string", "default": "Roboto, Arial, sans-serif", "description": "The font family used for the slide content"}
                },
                "required": []
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "generate_body_slide8",
            "description": "Generate a professional HTML slide body with a centered title and a list of bullet points, enhanced with decorative semi-transparent circular corners.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "default": "DISCUSSION", "description": "The main title of the slide"},
                    "points": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [
                            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis vel dolor ante.",
                            "Nullam feugiat egestas elit et vehicula. Proin venenatis, orci nec cursus tristique."
                        ],
                        "description": "A list of bullet points to be displayed"
                    },
                    "title_font_size": {"type": "string", "default": "42px", "description": "Font size of the main title"},
                    "content_font_size": {"type": "string", "default": "24px", "description": "Font size of the bullet point text"},
                    "bg_color": {"type": "string", "default": "#FFFBEB", "description": "Background color of the entire slide body"},
                    "title_color": {"type": "string", "default": "#000000", "description": "Color of the main title text"},
                    "content_color": {"type": "string", "default": "#333333", "description": "Color of the bullet point text"},
                    "corner_decoration_color": {"type": "string", "default": "#FDE68A", "description": "Color of the semi-transparent circular decorations in the corners"},
                    "font_family": {"type": "string", "default": "Roboto, Arial, sans-serif", "description": "Font family for both title and content"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_body_slide1",
            "description": "Generate a professional HTML slide body with a title, a main paragraph, a list of bullet points, and an image placeholder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "default": "Professional HTML Slide", "description": "The title of the HTML document"},
                    "title_font_size": {"type": "string", "default": "42px", "description": "Font size of the slide title"},
                    "slide_title": {"type": "string", "default": "Slide Title", "description": "The title displayed on the slide"},
                    "bg_color": {"type": "string", "default": "#E8F5E9", "description": "Background color of the page"},
                    "text_bg_color": {"type": "string", "default": "#FFFFFF", "description": "Background color of the text container"},
                    "text_color": {"type": "string", "default": "#2E7D32", "description": "Text color of the slide content"},
                    "keyword_color": {"type": "string", "default": "#1B5E20", "description": "Color for keywords"},
                    "image_bg_color": {"type": "string", "default": "#C8E6C9", "description": "Background color of the image placeholder"},
                    "image_placeholder_text": {"type": "string", "default": "Image Placeholder", "description": "Text displayed in the image placeholder"},
                    "font_family": {"type": "string", "default": "Roboto, Arial, sans-serif", "description": "Font family for the slide content"},
                    "content_paragraph": {"type": "string", "default": "This is a customizable slide. Add your content here:", "description": "Main paragraph content"},
                    "para_font_size": {"type": "string", "default": "24px", "description": "Font size of the paragraph text"},
                    "list_items": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [
                            "<span class=\"keyword\">Point 1</span>: Description of point 1.",
                            "<span class=\"keyword\">Point 2</span>: Description of point 2.",
                            "<span class=\"keyword\">Point 3</span>: Description of point 3.",
                            "<span class=\"keyword\">Point 4</span>: Description of point 4."
                        ],
                        "description": "A list of bullet points to include"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_conclusion_slide",
            "description": "Generates a customizable HTML slide with a 'Conclusion' layout featuring dots and lines as decorations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "default": "Conclusion", "description": "Slide title text"},
                    "title_color": {"type": "string", "default": "#0F4662", "description": "Color of the title"},
                    "title_font_size": {"type": "string", "default": "32px", "description": "Font size of the title"},
                    "title_font_style": {"type": "string", "default": "italic", "description": "Font style for the title (e.g., 'italic')"},
                    "title_margin_bottom": {"type": "string", "default": "5px", "description": "Bottom margin for the title"},
                    "title_margin_left": {"type": "string", "default": "40px", "description": "Left margin for the title"},
                    "content_text": {"type": "string", "default": "Content", "description": "Main content text"},
                    "content_color": {"type": "string", "default": "#0F4662", "description": "Color of content text"},
                    "content_font_size": {"type": "string", "default": "16px", "description": "Font size of content"},
                    "content_line_height": {"type": "string", "default": "1.6", "description": "Line height for content"},
                    "content_width": {"type": "string", "default": "70%", "description": "Width of content container"},
                    "content_margin": {"type": "string", "default": "0 auto", "description": "Margin around content"},
                    "content_text_align": {"type": "string", "default": "center", "description": "Text alignment for content"},
                    "dot_color": {"type": "string", "default": "#0F4662", "description": "Color of decorative dots"},
                    "dot_size": {"type": "string", "default": "10px", "description": "Size of decorative dots"},
                    "dot_margin": {"type": "string", "default": "0 5px", "description": "Margin between dots"},
                    "dot_count": {"type": "integer", "default": 5, "description": "Number of dots in each row"},
                    "line_color": {"type": "string", "default": "#1a3d5c", "description": "Color of horizontal lines"},
                    "line_width": {"type": "string", "default": "50%", "description": "Width of horizontal lines"},
                    "line_height": {"type": "string", "default": "2px", "description": "Height/thickness of horizontal lines"},
                    "line_margin": {"type": "string", "default": "30px auto", "description": "Margin around horizontal lines"},
                    "slide_bg_color": {"type": "string", "default": "#f5f5f5", "description": "Background color of the slide"},
                    "font_family": {"type": "string", "default": "Roboto, Arial, sans-serif", "description": "Font family for all text"},
                    "additional_css": {"type": "string", "default": "", "description": "Additional CSS styles"}
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
    # slide_content's language
    language = "Vietnamese" if is_vietnamese(slide_content) else "English"
    Create a slide that matches the following content, choose a function when you think it is best suited with the content and the content of the slide should be base on input slide content. If the input text is in language, your output (including all text fields in the function call) MUST also be in language:
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
    logger.info("slide function calls list")
    logger.info("Cleaning slide function calls")
    fixed_list = slide_function_calling_list.copy()
    for i in range(len(fixed_list)):
        fixed_list[i] = filter_string(fixed_list[i], '<tool_call>', '<|im_end|>')
        fixed_list[i] = check_and_insert_char(fixed_list[i], -20, '/')
    return fixed_list

def process_tool_call(tool_call_output):
    logger.info(f"Processing tool call: {tool_call_output}")
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
6. If there is a previous slide, ensure consistency in background color, text color, font size, and font family.
"""

def evaluate_slide_with_qwen(image_path, previous_image_path, tool_call_output):
    logger.info(f"Evaluating slide: {image_path} with previous: {previous_image_path}")
    if not vlm_model or not vlm_processor:
        logger.error("VLM model or processor not loaded")
        return "Model not loaded"
    
    # Load ảnh slide hiện tại
    image = Image.open(image_path)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": "This is the current slide."},
            ],
        }
    ]
    
    # Thêm ảnh slide trước đó nếu có
    if previous_image_path and os.path.exists(previous_image_path):
        previous_image = Image.open(previous_image_path)
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": previous_image},
                    {"type": "text", "text": "This is the previous slide."},
                ],
            }
        )
    
    # Câu hỏi đánh giá
    question = f"""
Evaluate this slide based on the following criteria:
{criteria}
If there is a previous slide, also check for consistency in background color, text color, font size, and font family between the current and previous slides.
Current tool call: {tool_call_output}
Your response must follow this format:
<!-- accept/deny -->
<!-- reason -->
<tool_call>
[tool_call_output with updated parameters if deny] IMPORTANT: Keep the original text content in 'content_paragraph' and 'list_items' UNCHANGED.  Only modify parameters related to appearance (e.g., colors, layout, image_placeholder_text).
</tool_call>
"""
    messages.append({"role": "user", "content": [{"type": "text", "text": question}]})

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
    logger.info(f"Parsing VLM response: {vlm_response}")
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
                    html_content = process_tool_call(tool_call_output)
                    if not filter_invalid_slides(html_content):
                        logger.warning(f"Slide {i+1} is invalid")
                        break

                    temp_html_path = os.path.join(html_folder, f"slide_{i+1}_attempt_{attempts}.html")
                    with open(temp_html_path, "w", encoding="utf-8") as file:
                        file.write(html_content)

                    temp_image_path = os.path.join(png_folder, f"slide_{i+1}_attempt_{attempts}.png")
                    slide_image = capture_slide_image(driver, html_content, temp_image_path)

                    evaluation_content = evaluate_slide_with_qwen(temp_image_path, previous_image_path, tool_call_output)
                    status, reason, new_tool_call = parse_vlm_response(evaluation_content)

                    if status == "accept":
                        final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                        final_png_path = os.path.join(png_folder, f"slide_{i+1}.png")
                        os.rename(temp_html_path, final_html_path)
                        os.rename(temp_image_path, final_png_path)
                        html_files.append(final_html_path)
                        png_files.append(final_png_path)
                        previous_image_path = final_png_path
                        logger.info(f"Slide {i+1} accepted")
                        break  # Thoát vòng lặp while nếu slide được chấp nhận
                    elif status == "deny" and new_tool_call:
                        tool_call_output = new_tool_call
                        logger.info(f"Slide {i+1} denied, retrying with new tool call")

                except Exception as e:
                    logger.error(f"Error processing slide {i+1}, attempt {attempts}: {e}")
                    # Không break ở đây, để thử lại nếu còn attempts

            if attempts == max_attempts:  # Đã thử hết số lần cho phép
                logger.warning(f"Slide {i+1} max attempts reached")
                # Có thể xử lý bằng cách bỏ qua slide này hoặc thêm một slide lỗi
                # Ví dụ: Thêm một slide lỗi
                final_html_path = os.path.join(html_folder, f"slide_{i+1}.html")
                final_png_path = os.path.join(png_folder, f"slide_{i + 1}.png")

                with open(final_html_path, 'w') as f:
                    f.write('<html><body><h1>Error Creating Slide</h1></body></html>')  # Tạo nội dung HTML lỗi
                # Tạo 1 ảnh trắng để thay thế.
                img = Image.new('RGB', (900, 500), color='white')
                img.save(final_png_path)

                html_files.append(final_html_path)
                png_files.append(final_png_path)
                previous_image_path = final_png_path  # CẬP NHẬT previous_image_path

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