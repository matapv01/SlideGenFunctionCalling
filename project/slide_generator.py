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

def generate_split_layout_slide1(
    left_bg_color="#FFF3E0",
    left_title="Title",
    left_title_color="#EF6C00",
    left_subtitle="SubTitle",
    left_subtitle_color="#FB8C00",

    right_bg_color="#FFE0B2",
    right_image_src="path-to-your-image/image.png",
    right_image_alt="Image",
    decor_bg_color="#FFCC80",
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
    <!-- Bootstrap CSS -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: {decor_bg_color};
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
    title="Title",
    right_bg_color="#DFE9FF",
    bottom_right_title="Section Title",
    bottom_right_title_color="#1F3685",
    bottom_right_description="This section provides detailed insights and explanations.",
    bottom_right_description_color="#333",
    divider_color="#000",
    font_family="Roboto, Arial, sans-serif"
):
    """
    Generate a simplified split layout HTML slide without left section and image placeholders.

    :param title: The title of the HTML document.
    :param right_bg_color: Background color of the right section.
    :param bottom_right_title: Title displayed in the bottom right section.
    :param bottom_right_title_color: Color of the bottom right title.
    :param bottom_right_description: Description text in the bottom right section.
    :param bottom_right_description_color: Color of the bottom right description text.
    :param divider_color: Color of the divider in the bottom right section.
    :param font_family: Font family for the slide content.
    :return: A string containing the HTML code.
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap CSS -->
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: {right_bg_color};
        }}
        .right-section {{
            background-color: {right_bg_color};
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            padding: 20px;
            z-index: 2;
        }}
        .bottom-right {{
            background-color: white;
            padding: 50px;
            display: flex;
            justify-content: space-evenly;
            align-items: center;
            flex-direction: row;
            width: 80%;
            height: auto;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }}
        .bottom-right .title {{
            font-size: 64px;
            font-weight: bold;
            color: {bottom_right_title_color};
            margin: 0;
        }}
        .bottom-right .description {{
            font-size: 18px;
            color: {bottom_right_description_color};
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
    <div class="container-fluid h-100 d-flex justify-content-center align-items-center">
        <div class="bottom-right">
            <div class="col-md-4 title">{bottom_right_title}</div>
            <div class="divider"></div>
            <div class="col-md-4 description">
                {bottom_right_description}
            </div>
        </div>
    </div>

    <!-- Bootstrap JS and dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

    return html_code


def generate_body_slide1(
    title="Professional HTML Slide",
    slide_title="Slide Title",
    bg_color="#E8F5E9",
    text_bg_color="#FFFFFF",
    text_color="#2E7D32",
    keyword_color="#1B5E20",
    image_bg_color="#C8E6C9",
    image_placeholder_text="Image Placeholder",
    font_family="Roboto, Arial, sans-serif",
    content_paragraph="This is a customizable slide. Add your content here:",
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
    paragraph_text="This is a customizable slide content area. You can add any relevant information here"
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
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }}

        h1 {{
            color: {header_color};
            font-size: 2.8em;
        }}

        p {{
            font-size: 1.4em;
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
                width: 250px;
                height: 250px;
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
    title="Title",
    header_text="Subtitle",
    background_gradient=("#FFEBEE", "#FFCDD2"),
    content_bg_opacity=0.8,
    content_shadow="0 4px 8px rgba(0, 0, 0, 0.1)",
    header_color="#C62828",
    text_body_color="#D32F2F",
    highlight_color="#FF4500",
    image_placeholder_text="Image Placeholder",
    image_bg_color="#EF9A9A",
    font_family="Roboto, Arial, sans-serif",
    paragraph_text="content paragraph"
):
    """
    Generate a professional HTML slide body with customizable parameters.

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
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
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


def generate_body_slide4(
    title="Learning Objectives",
    objectives=None,
    bg_color="#E8F5E9",  # Màu nền chính
    title_color='#2E7D32',
    objective_bg_color="#388E3C",  # Màu nền của số thứ tự
    objective_text_color="#ffffff",  # Màu chữ của số thứ tự
    content_text_color="#ffffff",  # Màu chữ nội dung
    box_bg_color="#1B5E20",  # Màu nền của khung bao quanh content
    box_shadow="0 4px 12px rgba(0, 0, 0, 0.1)",  # Hiệu ứng bóng đổ cho khung
    box_border_radius="10px",  # Độ bo tròn góc cho khung
    box_padding="20px",  # Khoảng cách padding trong khung
    font_family="Roboto, Arial, sans-serif",  # Font chữ
    image_src="path-to-your-image/ocean-background.png",  # Đường dẫn đến hình nền
    image_width="100%",  # Chiều rộng hình nền
    image_height="auto",  # Chiều cao hình nền
    border_radius="50%"  # Độ bo tròn cho số thứ tự
):
    """
    Generate a professional HTML slide body with customizable parameters.
    :param title: Tiêu đề của slide.
    :param objectives: Danh sách các mục tiêu học tập (list of strings).
    :param bg_color: Màu nền chính.
    :param objective_bg_color: Màu nền của số thứ tự.
    :param objective_text_color: Màu chữ của số thứ tự.
    :param content_text_color: Màu chữ nội dung.
    :param box_bg_color: Màu nền của khung bao quanh content.
    :param box_shadow: Hiệu ứng bóng đổ cho khung.
    :param box_border_radius: Độ bo tròn góc cho khung.
    :param box_padding: Khoảng cách padding trong khung.
    :param font_family: Font chữ sử dụng.
    :param image_src: Đường dẫn đến hình nền.
    :param image_width: Chiều rộng của hình nền.
    :param image_height: Chiều cao của hình nền.
    :param border_radius: Độ bo tròn cho số thứ tự.
    :return: Mã HTML của slide.
    """
    if objectives is None:
        objectives = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Maecenas euismod magna in sem rutrum luctus. Sed ultringer diam non venenatis dictum.",
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
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css\" rel=\"stylesheet\">
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
        }}
        .title {{
            font-size: 2.5rem;
            margin-bottom: 40px;
            color: {title_color};
        }}
        .objectives-container {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .objective {{
            flex: 1 1 calc(50% - 40px);
            min-width: 300px;
            padding: 20px;
            box-sizing: border-box;
        }}
        .number {{
            background-color: {objective_bg_color};
            color: {objective_text_color};
            font-size: 2rem;
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
        }}
        .box p {{
            font-size: 1.2rem;
            line-height: 1.6;
            margin: 0;
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
    subtitle1 = "Subtitle1",
    subtitle2 = "Subtitle2",
    content_1="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris eleifend magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.",
    content_2="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris eleifend magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.",
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
            font-size: 2.5rem;
            color: {title_color};
            margin-bottom: 20px;
        }}
        .number {{
            background-color: {number_bg_color};
            color: {number_text_color};
            font-size: 1.2rem;
            padding: 10px 20px;
            border-radius: {border_radius};
            margin-bottom: 10px;
        }}
        .content {{
            font-size: 1.2rem;
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
    title="Title",
    feature_1_title="Feature 01",
    feature_1_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas euismod magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque.",
    feature_2_title="Feature 02",
    feature_2_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas euismod magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque.",
    feature_3_title="Feature 03",
    feature_3_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas euismod magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque.",
    feature_4_title="Feature 04",
    feature_4_content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas euismod magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque.",
    bg_color="#6D4C41",  # Màu nền chính
    title_color="#FFFFFF",  # Màu chữ tiêu đề
    content_color="#D7CCC8",  # Màu chữ nội dung
    number_bg_color="#BCAAA4",  # Màu nền số thứ tự
    number_text_color="#FFFFFF",  # Màu chữ số thứ tự
    font_family="Roboto, Arial, sans-serif"  # Font chữ
):
    """
    Generate a professional HTML slide body with customizable parameters.
    :param title: Tiêu đề chính của slide.
    :param feature_1_title, feature_2_title, feature_3_title, feature_4_title: Tiêu đề của các mục tiêu.
    :param feature_1_content, feature_2_content, feature_3_content, feature_4_content: Nội dung của các mục tiêu.
    :param bg_color: Màu nền chính.
    :param title_color: Màu chữ của tiêu đề.
    :param content_color: Màu chữ của nội dung.
    :param number_bg_color: Màu nền số thứ tự.
    :param number_text_color: Màu chữ số thứ tự.
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
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }}
        .title {{
            font-size: 2.5rem;
            color: {title_color};
            text-transform: uppercase;
            margin-bottom: 40px;
        }}
        .features-container {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            width: 80%;
            max-width: 1200px;
        }}
        .feature {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            text-align: left;
        }}
        .feature-title {{
            background-color: {number_bg_color};
            color: {number_text_color};
            font-size: 1.2rem;
            padding: 10px 20px;
            border-radius: 10px;
            margin-bottom: 10px;
        }}
        .feature-content {{
            font-size: 1.2rem;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">{title}</h1>
        <div class="features-container">
            <!-- Feature 01 -->
            <div class="feature">
                <div class="feature-title">{feature_1_title}</div>
                <p class="feature-content">{feature_1_content}</p>
            </div>
            <!-- Feature 02 -->
            <div class="feature">
                <div class="feature-title">{feature_2_title}</div>
                <p class="feature-content">{feature_2_content}</p>
            </div>
            <!-- Feature 03 -->
            <div class="feature">
                <div class="feature-title">{feature_3_title}</div>
                <p class="feature-content">{feature_3_content}</p>
            </div>
            <!-- Feature 04 -->
            <div class="feature">
                <div class="feature-title">{feature_4_title}</div>
                <p class="feature-content">{feature_4_content}</p>
            </div>
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
    elif name == "generate_split_content_slide1":
        return generate_split_layout_slide1
    elif name == "generate_split_content_slide2":
        return generate_split_layout_slide2
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
    elif name == "generate_body_slide6":
        return generate_body_slide6
    elif name == "generate_conclusion_slide":
        return generate_conclusion_slide
    elif name == "generate_end_slide":
        return generate_end_slide
    else:
        raise ValueError(f"Function with name '{name}' not found.")



TOOLS = [
    {
  "function": {
    "name": "generate_conclusion_slide",
    "description": "Generates a customizable HTML slide with a 'Conclusion' layout featuring dots and lines as decorations.",
    "parameters": {
      "title": {
        "type": "string",
        "default": "Conclusion",
        "description": "Slide title text."
      },
      "title_color": {
        "type": "string",
        "default": "#0F4662",
        "description": "Color of the title."
      },
      "title_font_size": {
        "type": "string",
        "default": "32px",
        "description": "Font size of the title."
      },
      "title_font_style": {
        "type": "string",
        "default": "italic",
        "description": "Font style of the title (e.g., 'italic')."
      },
      "title_margin_bottom": {
        "type": "string",
        "default": "5px",
        "description": "Bottom margin for the title."
      },
      "title_margin_left": {
        "type": "string",
        "default": "40px",
        "description": "Left margin for the title."
      },
      "content_text": {
        "type": "string",
        "default": "Content",
        "description": "Main content text of the slide."
      },
      "content_color": {
        "type": "string",
        "default": "#0F4662",
        "description": "Color of the content text."
      },
      "content_font_size": {
        "type": "string",
        "default": "16px",
        "description": "Font size of the content text."
      },
      "content_line_height": {
        "type": "string",
        "default": "1.6",
        "description": "Line height for the content text."
      },
      "content_width": {
        "type": "string",
        "default": "70%",
        "description": "Width of the content container."
      },
      "content_margin": {
        "type": "string",
        "default": "0 auto",
        "description": "Margin around the content."
      },
      "content_text_align": {
        "type": "string",
        "default": "center",
        "description": "Text alignment for the content."
      },
      "dot_color": {
        "type": "string",
        "default": "#0F4662",
        "description": "Color of the decorative dots."
      },
      "dot_size": {
        "type": "string",
        "default": "10px",
        "description": "Size of the decorative dots."
      },
      "dot_margin": {
        "type": "string",
        "default": "0 5px",
        "description": "Margin between dots."
      },
      "dot_count": {
        "type": "integer",
        "default": 5,
        "description": "Number of dots in each row."
      },
      "line_color": {
        "type": "string",
        "default": "#1a3d5c",
        "description": "Color of the horizontal lines."
      },
      "line_width": {
        "type": "string",
        "default": "50%",
        "description": "Width of the horizontal lines."
      },
      "line_height": {
        "type": "string",
        "default": "2px",
        "description": "Height/thickness of the horizontal lines."
      },
      "line_margin": {
        "type": "string",
        "default": "30px auto",
        "description": "Margin around the horizontal lines."
      },
      "slide_bg_color": {
        "type": "string",
        "default": "#f5f5f5",
        "description": "Background color of the slide."
      },
      "font_family": {
        "type": "string",
        "default": "Roboto, Arial, sans-serif",
        "description": "Font family for all text elements."
      },
      "additional_css": {
        "type": "string",
        "default": "",
        "description": "Additional CSS styles for customization."
      }
    }
  }
},
    {
        "type": "function",
        "function": {
            "name": "generate_split_layout_slide1",
            "description": "Generate a split layout HTML slide with customizable parameters for left and right sections, including background colors, text, image placeholders, and a bottom section with a title and description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "left_bg_color": {
                        "type": "string",
                        "description": "Background color of the left section. Defaults to '#DFE9FF'.",
                        "default": "#DFE9FF"
                    },
                    "left_title": {
                        "type": "string",
                        "description": "Tile displayed in the left section. Defaults to 'Title'.",
                        "default": "Title"
                    },
                    "left_title_color": {
                        "type": "string",
                        "description": "Text color of the left section. Defaults to '#1F3685'.",
                        "default": "#1F3685"
                    },
                    "left_subtitle": {
                        "type": "string",
                        "description": "Subtitle text in the left section. Defaults to 'Subtitle'.",
                        "default": "Subtitle"

                    },
                    "left_subtitle_color": {
                        "type": "string",
                        "description": "Text color of the subtitle in the left section. Defaults to '#2B4CC0'.",
                        "default": "#2B4CC0"
                    },
                    "right_bg_color": {
                        "type": "string",
                        "description": "Background color of the right section. Defaults to '#DFE9FF'.",
                        "default": "#DFE9FF"
                    },
                    "right_image_src": {
                        "type": "string",
                        "description": "Link to image of the right section. Defaults to 'path-to-your-image/image.png'.",
                        "default": "path-to-your-image/image.png"
                    },
                    "right_image_alt": {
                        "type": "string",
                        "description": "Text displayed in the image placeholder. Defaults to 'Image'.",
                        "default": "Image"
                    },
                    "decor_bg_color":{
                        "type": "string",
                        "description": "Background color of the decorative container.Default to '#A6B4E5'.",
                        "default": "#A6B4E5"
                    },
                    "font_family": {
                        "type": "string",
                        "description": "Font family for the slide content. Defaults to 'Roboto, Arial, sans-serif'.",
                        "default": "Roboto, Arial, sans-serif"
                    }
                },
                "required": []
            }
        }
    },
    {
  "type": "function",
  "function": {
    "name": "generate_split_layout_slide2",
    "description": "Generate a simplified split layout HTML slide without left section and image placeholders. This function creates a presentation slide with a right section containing a title and description, separated by a divider. The design is minimalist and focused on text content.",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "description": "The title of the HTML document. Defaults to 'Title'.",
          "default": "Title"
        },
        "right_bg_color": {
          "type": "string",
          "description": "Background color of the right section. Defaults to '#DFE9FF'.",
          "default": "#DFE9FF"
        },
        "bottom_right_title": {
          "type": "string",
          "description": "Title displayed in the bottom right section. Defaults to 'Section Title'.",
          "default": "Section Title"
        },
        "bottom_right_title_color": {
          "type": "string",
          "description": "Color of the bottom right title. Defaults to '#1F3685'.",
          "default": "#1F3685"
        },
        "bottom_right_description": {
          "type": "string",
          "description": "Description text in the bottom right section. Defaults to 'This section provides detailed insights and explanations.'.",
          "default": "This section provides detailed insights and explanations."
        },
        "bottom_right_description_color": {
          "type": "string",
          "description": "Color of the bottom right description text. Defaults to '#333'.",
          "default": "#333"
        },
        "divider_color": {
          "type": "string",
          "description": "Color of the divider in the bottom right section. Defaults to '#000'.",
          "default": "#000"
        },
        "font_family": {
          "type": "string",
          "description": "Font family for the slide content. Defaults to 'Roboto, Arial, sans-serif'.",
          "default": "Roboto, Arial, sans-serif"
        }
      },
      "required": []
    }
  }
},
{
        "type": "function",
        "function": {
            "name": "generate_body_slide1",
            "description": "Generate a professional HTML slide body with customizable content and styling. Use this function when you need to create a slide with a title, a main paragraph, a list of bullet points, and an image placeholder. The slide is designed for professional presentations and supports customization of colors, fonts, and content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the HTML document. Defaults to 'Professional HTML Slide Body'.",
                        "default": "Professional HTML Slide Body"
                    },
                    "slide_title": {
                        "type": "string",
                        "description": "The title displayed on the slide. Defaults to '2. Importance of Networking:'.",
                        "default": "2. Importance of Networking:"
                    },
                    "bg_color": {
                        "type": "string",
                        "description": "Background color of the page. Defaults to '#e9f7fe'.",
                        "default": "#e9f7fe"
                    },
                    "text_bg_color": {
                        "type": "string",
                        "description": "Background color of the text container. Defaults to '#ffffff'.",
                        "default": "#ffffff"
                    },
                    "text_color": {
                        "type": "string",
                        "description": "Text color of the slide content. Defaults to '#2e4e7e'.",
                        "default": "#2e4e7e"
                    },
                    "keyword_color": {
                        "type": "string",
                        "description": "Color for keywords in the slide content. Defaults to '#004080'.",
                        "default": "#004080"
                    },
                    "image_bg_color": {
                        "type": "string",
                        "description": "Background color of the image placeholder. Defaults to '#b0d4f1'.",
                        "default": "#b0d4f1"
                    },
                    "image_placeholder_text": {
                        "type": "string",
                        "description": "Text displayed in the image placeholder. Defaults to 'Image Placeholder'.",
                        "default": "Image Placeholder"
                    },
                    "font_family": {
                        "type": "string",
                        "description": "Font family for the slide content. Defaults to 'Arial, sans-serif'.",
                        "default": "Roboto, Arial, sans-serif"
                    },
                    "content_paragraph": {
                        "type": "string",
                        "description": "Main paragraph content of the slide. Defaults to a paragraph about the importance of networking.",
                        "default": "Networking is crucial for <span class=\"keyword\">personal development</span>. It fosters:"
                    },
                    "list_items": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "A list of bullet points to include in the slide. Each item should be a string. If not provided, defaults to a list about networking benefits.",
                        "default": [
                            "<span class=\"keyword\">Point 1</span>: Description of point 1.",
                            "<span class=\"keyword\">Point 2</span>: Description of point 2.",
                            "<span class=\"keyword\">Point 3</span>: Description of point 3.",
                            "<span class=\"keyword\">Point 4</span>: Description of point 4."
                        ]
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_body_slide2",
            "description": "Generate a professional HTML slide body with customizable layout, colors, and content. Use this function when you need to create a visually appealing slide with a header, a content paragraph, and an image placeholder. The function supports customization of background colors, text colors, fonts, and content, making it ideal for creating presentation slides.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the HTML document. Defaults to 'Power of Goal Setting'.",
                        "default": "Power of Goal Setting"
                    },
                    "header_text": {
                        "type": "string",
                        "description": "The main header text displayed on the slide. Defaults to 'The Power of Goal Setting'.",
                        "default": "The Power of Goal Setting"
                    },
                    "background_color": {
                        "type": "string",
                        "description": "The background color of the entire slide. Defaults to '#faf0e6'.",
                        "default": "#faf0e6"
                    },
                    "text_color": {
                        "type": "string",
                        "description": "The default text color for the slide. Defaults to '#333'.",
                        "default": "#333"
                    },
                    "content_bg_color": {
                        "type": "string",
                        "description": "The background color of the content box. Defaults to '#ffffff'.",
                        "default": "#ffffff"
                    },
                    "content_shadow": {
                        "type": "string",
                        "description": "The box shadow for the content container. Defaults to '0 4px 8px rgba(0, 0, 0, 0.1)'.",
                        "default": "0 4px 8px rgba(0, 0, 0, 0.1)"
                    },
                    "header_color": {
                        "type": "string",
                        "description": "The color of the header text. Defaults to '#3B5998'.",
                        "default": "#3B5998"
                    },
                    "text_body_color": {
                        "type": "string",
                        "description": "The color of the body text. Defaults to '#2f4f4f'.",
                        "default": "#2f4f4f"
                    },
                    "highlight_color": {
                        "type": "string",
                        "description": "The color for highlighted text (e.g., bold text). Defaults to '#ff4500'.",
                        "default": "#ff4500"
                    },
                    "image_placeholder_text": {
                        "type": "string",
                        "description": "The placeholder text for the image area. Defaults to '[Image Placeholder - Proportioned for future use]'.",
                        "default": "[Image Placeholder - Proportioned for future use]"
                    },
                    "image_bg_color": {
                        "type": "string",
                        "description": "The background color of the image placeholder. Defaults to '#e1e5ea'.",
                        "default": "#e1e5ea"
                    },
                    "font_family": {
                        "type": "string",
                        "description": "The font family for all text in the slide. Defaults to 'Arial, sans-serif'.",
                        "default": "Roboto, Arial, sans-serif"
                    },
                    "paragraph_text": {
                        "type": "string",
                        "description": "The main content paragraph for the slide. Defaults to a placeholder paragraph about goal setting.",
                        "default": "<strong>Goal setting</strong> is a crucial aspect of personal development that empowers individuals to define clear objectives, map out strategies, and cultivate a path toward growth. It provides direction, motivation, and accountability, helping people focus their efforts, overcome challenges, and achieve their aspirations."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_body_slide3",
            "description": "Generate a professional HTML slide body with a gradient background, a centered content box, and a single image placeholder. Use this function when you need to create a visually appealing slide with a header, a content paragraph, and one image placeholder. The function supports customization of background gradients, text colors, fonts, and content, making it ideal for creating modern presentation slides.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the HTML document. Defaults to 'The Future of Creative Industries: Digital Transformation and Immersive Experiences'.",
                        "default": "The Future of Creative Industries: Digital Transformation and Immersive Experiences"
                    },
                    "header_text": {
                        "type": "string",
                        "description": "The main header text displayed on the slide. Defaults to 'The Future of Creative Industries: Digital Transformation and Immersive Experiences'.",
                        "default": "The Future of Creative Industries: Digital Transformation and Immersive Experiences"
                    },
                    "background_gradient": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Gradient colors for the background, provided as an array of two color codes. Defaults to ['#4facfe', '#00c6ff'].",
                        "default": ["#4facfe", "#00c6ff"]
                    },
                    "content_bg_opacity": {
                        "type": "number",
                        "description": "Opacity for the content box background. Defaults to 0.8.",
                        "default": 0.8
                    },
                    "content_shadow": {
                        "type": "string",
                        "description": "Box shadow for the content container. Defaults to '0 4px 8px rgba(0, 0, 0, 0.1)'.",
                        "default": "0 4px 8px rgba(0, 0, 0, 0.1)"
                    },
                    "header_color": {
                        "type": "string",
                        "description": "Color of the header text. Defaults to '#333333'.",
                        "default": "#333333"
                    },
                    "text_body_color": {
                        "type": "string",
                        "description": "Color of the body text. Defaults to '#333333'.",
                        "default": "#333333"
                    },
                    "highlight_color": {
                        "type": "string",
                        "description": "Color for highlighted text (e.g., bold text). Defaults to '#ff4500'.",
                        "default": "#ff4500"
                    },
                    "image_placeholder_text": {
                        "type": "string",
                        "description": "Placeholder text for the image area. Defaults to 'Image Placeholder'.",
                        "default": "Image Placeholder"
                    },
                    "image_bg_color": {
                        "type": "string",
                        "description": "Background color of the image placeholder. Defaults to '#cccccc'.",
                        "default": "#cccccc"
                    },
                    "font_family": {
                        "type": "string",
                        "description": "The font family for all text in the slide. Defaults to 'Arial, sans-serif'.",
                        "default": "Roboto, Arial, sans-serif"
                    },
                    "paragraph_text": {
                        "type": "string",
                        "description": "The main content paragraph for the slide. Defaults to a placeholder paragraph about digital transformation and immersive experiences.",
                        "default": "The future of the <span class=\"bold\">creative industries</span> lies at the intersection of digital technology and immersive experiences. <span class=\"bold\">Virtual reality</span>, <span class=\"bold\">augmented reality</span>, and <span class=\"bold\">artificial intelligence</span> are revolutionizing how we create, consume, and interact with art, entertainment, and design. From immersive exhibitions to <span class=\"bold\">AI-powered storytelling</span>, these technologies are pushing the boundaries of imagination and engagement, opening up new possibilities for creativity and innovation."
                    }
                },
                "required": []
            }
        }
    },
    {
  "function": {
    "name": "generate_body_slide4",
    "description": "Generate a professional HTML slide body with a structured content box and numbered items. Use this function when you need to present key points, objectives, or topics in an organized and visually appealing format. The function supports customization of background colors, text colors, fonts, shadows, and more, making it suitable for various presentation needs.",
    "parameters": {
      "title": {
        "type": "string",
        "default": "Slide Title",
        "description": "The main title of the slide. Can be used for objectives, key points, or any content heading."
      },
      "objectives": {
        "type": "list of strings",
        "default": ["Objective1", "Objective2", "Objective3"],
        "description": "A list of key points or objectives to be displayed."
      },
      "bg_color": {
        "type": "string",
        "default": "#e0f7fa",
        "description": "The background color of the slide."
      },
      "title_color": {
        "type": "string",
        "default": "#003f72",
        "description": "The color of the slide title."
      },
      "objective_bg_color": {
        "type": "string",
        "default": "#00c6ff",
        "description": "The background color for the numbered items."
      },
      "objective_text_color": {
        "type": "string",
        "default": "#ffffff",
        "description": "The text color of the numbered items."
      },
      "content_text_color": {
        "type": "string",
        "default": "#ffffff",
        "description": "The text color of the content inside the box."
      },
      "box_bg_color": {
        "type": "string",
        "default": "#003f72",
        "description": "The background color of the content box."
      },
      "box_shadow": {
        "type": "string",
        "default": "0 4px 12px rgba(0, 0, 0, 0.1)",
        "description": "The box shadow effect for the content box."
      },
      "box_border_radius": {
        "type": "string",
        "default": "10px",
        "description": "The border radius for the content box."
      },
      "box_padding": {
        "type": "string",
        "default": "20px",
        "description": "The padding inside the content box."
      },
      "font_family": {
        "type": "string",
        "default": "Roboto, Arial, sans-serif",
        "description": "The font family used for the slide."
      },
      "image_src": {
        "type": "string",
        "default": "path-to-your-image/ocean-background.png",
        "description": "The source path for the background image."
      },
      "image_width": {
        "type": "string",
        "default": "100%",
        "description": "The width of the background image."
      },
      "image_height": {
        "type": "string",
        "default": "auto",
        "description": "The height of the background image."
      },
      "border_radius": {
        "type": "string",
        "default": "50%",
        "description": "The border radius applied to the numbered items."
      }
    }
  }
},

    {
  "function": {
    "name": "generate_body_slide5",
    "description": "Generate a structured HTML slide with two content sections and an image placeholder. Use this function to present comparisons, key points, or categorized information in a visually engaging layout. The function allows customization of background colors, text colors, fonts, border styles, and image settings, making it adaptable for various presentation needs.",
    "parameters": {
      "title": {
        "type": "string",
        "default": "Title",
        "description": "The main title of the slide, providing context for the content."
      },
      "content_1": {
        "type": "string",
        "default": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "description": "The content for the first section of the slide."
      },
      "content_2": {
        "type": "string",
        "default": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "description": "The content for the second section of the slide."
      },
      "bg_color": {
        "type": "string",
        "default": "#003f72",
        "description": "The background color of the slide."
      },
      "title_color": {
        "type": "string",
        "default": "#ffffff",
        "description": "The text color of the title."
      },
      "content_color": {
        "type": "string",
        "default": "#ffffff",
        "description": "The text color of the content sections."
      },
      "number_bg_color": {
        "type": "string",
        "default": "#00c6ff",
        "description": "The background color of the numbered elements."
      },
      "number_text_color": {
        "type": "string",
        "default": "#ffffff",
        "description": "The text color of the numbered elements."
      },
      "image_bg_color": {
        "type": "string",
        "default": "#00c6ff",
        "description": "The background color of the image container."
      },
      "image_width": {
        "type": "string",
        "default": "70%",
        "description": "The width of the image container."
      },
      "image_height": {
        "type": "string",
        "default": "60%",
        "description": "The height of the image container."
      },
      "border_radius": {
        "type": "string",
        "default": "10px",
        "description": "The border radius applied to various elements for a rounded look."
      },
      "font_family": {
        "type": "string",
        "default": "Roboto, Arial, sans-serif",
        "description": "The font family used for the slide content."
      }
    }
  }
},
    {
  "function": {
    "name": "generate_body_slide6",
    "description": "Generate an HTML slide with a structured layout to showcase multiple features or key points. This function is ideal for presenting categorized information in a visually engaging manner. It allows customization of background colors, text colors, fonts, and numbered elements, making it suitable for various presentation themes.",
    "parameters": {
      "title": {
        "type": "string",
        "default": "Title",
        "description": "The main title of the slide, summarizing the content."
      },
      "feature_1_title": {
        "type": "string",
        "default": "Feature 01",
        "description": "Title for the first feature or key point."
      },
      "feature_1_content": {
        "type": "string",
        "default": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "description": "Description or explanation of the first feature."
      },
      "feature_2_title": {
        "type": "string",
        "default": "Feature 02",
        "description": "Title for the second feature or key point."
      },
      "feature_2_content": {
        "type": "string",
        "default": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "description": "Description or explanation of the second feature."
      },
      "feature_3_title": {
        "type": "string",
        "default": "Feature 03",
        "description": "Title for the third feature or key point."
      },
      "feature_3_content": {
        "type": "string",
        "default": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "description": "Description or explanation of the third feature."
      },
      "feature_4_title": {
        "type": "string",
        "default": "Feature 04",
        "description": "Title for the fourth feature or key point."
      },
      "feature_4_content": {
        "type": "string",
        "default": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "description": "Description or explanation of the fourth feature."
      },
      "bg_color": {
        "type": "string",
        "default": "#003f72",
        "description": "The background color of the slide."
      },
      "title_color": {
        "type": "string",
        "default": "#ffffff",
        "description": "The text color of the title."
      },
      "content_color": {
        "type": "string",
        "default": "#ffffff",
        "description": "The text color of the feature descriptions."
      },
      "number_bg_color": {
        "type": "string",
        "default": "#00c6ff",
        "description": "The background color of the numbered elements."
      },
      "number_text_color": {
        "type": "string",
        "default": "#ffffff",
        "description": "The text color of the numbered elements."
      },
      "font_family": {
        "type": "string",
        "default": "Roboto, Arial, sans-serif",
        "description": "The font family used for the slide content."
      }
    }
  }
},
    {
  "function": {
    "name": "generate_conclusion_slide",
    "description": "Generates a customizable HTML slide with a 'Conclusion' layout featuring dots and lines as decorations.",
    "parameters": {
      "title": {
        "type": "string",
        "default": "Conclusion",
        "description": "Slide title text."
      },
      "title_color": {
        "type": "string",
        "default": "#0F4662",
        "description": "Color of the title."
      },
      "title_font_size": {
        "type": "string",
        "default": "32px",
        "description": "Font size of the title."
      },
      "title_font_style": {
        "type": "string",
        "default": "italic",
        "description": "Font style of the title (e.g., 'italic')."
      },
      "title_margin_bottom": {
        "type": "string",
        "default": "5px",
        "description": "Bottom margin for the title."
      },
      "title_margin_left": {
        "type": "string",
        "default": "40px",
        "description": "Left margin for the title."
      },
      "content_text": {
        "type": "string",
        "default": "Content",
        "description": "Main content text of the slide."
      },
      "content_color": {
        "type": "string",
        "default": "#0F4662",
        "description": "Color of the content text."
      },
      "content_font_size": {
        "type": "string",
        "default": "16px",
        "description": "Font size of the content text."
      },
      "content_line_height": {
        "type": "string",
        "default": "1.6",
        "description": "Line height for the content text."
      },
      "content_width": {
        "type": "string",
        "default": "70%",
        "description": "Width of the content container."
      },
      "content_margin": {
        "type": "string",
        "default": "0 auto",
        "description": "Margin around the content."
      },
      "content_text_align": {
        "type": "string",
        "default": "center",
        "description": "Text alignment for the content."
      },
      "dot_color": {
        "type": "string",
        "default": "#0F4662",
        "description": "Color of the decorative dots."
      },
      "dot_size": {
        "type": "string",
        "default": "10px",
        "description": "Size of the decorative dots."
      },
      "dot_margin": {
        "type": "string",
        "default": "0 5px",
        "description": "Margin between dots."
      },
      "dot_count": {
        "type": "integer",
        "default": 5,
        "description": "Number of dots in each row."
      },
      "line_color": {
        "type": "string",
        "default": "#1a3d5c",
        "description": "Color of the horizontal lines."
      },
      "line_width": {
        "type": "string",
        "default": "50%",
        "description": "Width of the horizontal lines."
      },
      "line_height": {
        "type": "string",
        "default": "2px",
        "description": "Height/thickness of the horizontal lines."
      },
      "line_margin": {
        "type": "string",
        "default": "30px auto",
        "description": "Margin around the horizontal lines."
      },
      "slide_bg_color": {
        "type": "string",
        "default": "#f5f5f5",
        "description": "Background color of the slide."
      },
      "font_family": {
        "type": "string",
        "default": "Roboto, Arial, sans-serif",
        "description": "Font family for all text elements."
      },
      "additional_css": {
        "type": "string",
        "default": "",
        "description": "Additional CSS styles for customization."
      }
    }
  }
},
    {
  "function": {
    "name": "generate_end_slide",
    "description": "Generates a customizable HTML slide with an end slide layout featuring decorative dots and lines.",
    "parameters": {
      "content_text": {
        "type": "string",
        "default": "THANK YOU!",
        "description": "Main content text of the slide."
      },
      "content_color": {
        "type": "string",
        "default": "#0F4662",
        "description": "Color of the content text."
      },
      "content_font_size": {
        "type": "string",
        "default": "56px",
        "description": "Font size of the content text."
      },
      "content_line_height": {
        "type": "string",
        "default": "1.6",
        "description": "Line height for the content text."
      },
      "content_width": {
        "type": "string",
        "default": "70%",
        "description": "Width of the content container."
      },
      "content_margin": {
        "type": "string",
        "default": "0 auto",
        "description": "Margin around the content."
      },
      "content_text_align": {
        "type": "string",
        "default": "center",
        "description": "Text alignment for the content."
      },
      "dot_color": {
        "type": "string",
        "default": "#0F4662",
        "description": "Color of the decorative dots."
      },
      "dot_size": {
        "type": "string",
        "default": "10px",
        "description": "Size of the decorative dots."
      },
      "dot_margin": {
        "type": "string",
        "default": "0 5px",
        "description": "Margin between dots."
      },
      "dot_count": {
        "type": "integer",
        "default": 5,
        "description": "Number of dots in each row."
      },
      "line_color": {
        "type": "string",
        "default": "#1a3d5c",
        "description": "Color of the horizontal lines."
      },
      "line_width": {
        "type": "string",
        "default": "50%",
        "description": "Width of the horizontal lines."
      },
      "line_height": {
        "type": "string",
        "default": "2px",
        "description": "Height/thickness of the horizontal lines."
      },
      "line_margin": {
        "type": "string",
        "default": "30px auto",
        "description": "Margin around the horizontal lines."
      },
      "slide_bg_color": {
        "type": "string",
        "default": "#f5f5f5",
        "description": "Background color of the slide."
      },
      "font_family": {
        "type": "string",
        "default": "Robo, Arial, sans-serif",
        "description": "Font family for all text elements."
      },
      "additional_css": {
        "type": "string",
        "default": "",
        "description": "Additional CSS styles for customization."
      }
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
    # Xác định ngôn ngữ của slide_content
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