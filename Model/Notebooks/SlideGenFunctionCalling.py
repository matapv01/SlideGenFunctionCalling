
import os
import shutil
from docx import Document
import base64
import requests
import io
from PIL import Image
from weasyprint import HTML
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
import json
import weasyprint
import time
from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch


# Đường dẫn hoặc tên mô hình
model_name_or_path = "Qwen/Qwen2.5-7B-Instruct"

# Khởi tạo tokenizer và mô hình
tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
model = AutoModelForCausalLM.from_pretrained(
    model_name_or_path,
    torch_dtype="auto",
    device_map="auto",
    # load_in_8bit=True,
)

# Kiểm tra thiết bị
if torch.cuda.is_available():
    print("GPU is available.")
    print(f"Model is on device: {model.device}")
else:
    print("GPU is not available, model is on CPU.")


# @title Functions to
def generate_intro_slide(
    # Left section parameters
    left_bg_color='#DFE9FF',
    left_title="Title",
    left_title_color='#1F3685',
    left_title_font_size="48px",
    left_title_margin_bottom="20px",
    left_subtitle="Subtitle",
    left_subtitle_color='#2B4CC0',
    left_subtitle_font_size="24px",
    left_subtitle_margin_bottom="40px",
    left_section_padding="60px",
    left_col_md=6,

    # Right section parameters
    right_bg_color='#DFE9FF',
    right_image_src="path-to-your-image/image.png",
    right_image_alt="Image",
    right_image_width="100%",
    right_image_height="auto",
    right_image_border_radius="10px",
    right_section_padding="28px",
    right_section_border_radius="10px",
    right_col_md=4,
    right_col_offset=2,

    # Decoration parameters
    decor_bg_color='#FFFFFF',
    decor_top_bg_color='#A6B4E5',
    decor_bottom_bg_color='#A6B4E5',
    decor_top_height="50%",
    decor_bottom_height="30%",

    # Global parameters
    body_bg_color='#A6B4E5',
    font_family="Roboto, Arial, sans-serif",
    additional_css=""
):
    """
    Generates a highly customizable HTML slide with a split layout for presentations.

    Args:
        # [Existing parameters documentation...]
        # New parameters:
        left_title_font_size: Title font size in left section
        left_title_margin_bottom: Margin below title
        left_subtitle_font_size: Subtitle font size
        left_subtitle_margin_bottom: Margin below subtitle
        left_dots_font_size: Decorative dots size
        left_section_padding: Padding for left section
        left_col_md: Bootstrap column size for left section (1-12)
        right_image_width: Image width (e.g., "100%", "500px")
        right_image_height: Image height (e.g., "auto", "300px")
        right_image_border_radius: Image corner radius
        right_section_padding: Padding for right section
        right_section_border_radius: Right section corner radius
        right_col_md: Bootstrap column size for right section
        right_col_offset: Right column offset
        decor_top_bg_color: Top decoration color
        decor_bottom_bg_color: Bottom decoration color
        decor_top_height: Top decoration height
        decor_bottom_height: Bottom decoration height
        body_bg_color: Overall background color
        additional_css: Additional CSS rules
        # Handle decoration colors fallback
        decor_top = decor_top_bg_color or decor_bg_color
        decor_bottom = decor_bottom_bg_color or decor_bg_color
    """


    html_code = f"""<!DOCTYPE html>
<html lang='vn'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: {font_family};
            background-color: {body_bg_color}
        }};
        .left-section {{
            background-color: {left_bg_color};
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: {left_section_padding};
            box-sizing: border-box;
            z-index: 1;
        }}
        .left-section .title {{
            font-size: {left_title_font_size};
            font-weight: bold;
            color: {left_title_color};
            margin-bottom: {left_title_margin_bottom};
        }}
        .left-section .subtitle {{
            font-size: {left_subtitle_font_size};
            color: {left_subtitle_color};
            margin-bottom: {left_subtitle_margin_bottom};
        }}
        .right-section {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: {right_section_padding};
            background-color: {right_bg_color};
            border-radius: {right_section_border_radius};
            z-index: 1;
        }}
        .right-section img {{
            width: {right_image_width};
            height: {right_image_height};
            border-radius: {right_image_border_radius};
            object-fit: contain;
        }}
        .container::before {{
            content: '';
            position: absolute;
            width: 100%;
            height: {decor_top_height};
            background-color: {decor_top_bg_color};
            top: 50%;
            left: 0;
            z-index: -1;
        }}
        .decor-container {{
            position: absolute;
            width: 100%;
            height: {decor_bottom_height};
            background-color: {decor_bottom_bg_color};
            bottom: 0;
            left: 0;
            z-index: 0;
        }}
        {additional_css}
    </style>
</head>
<body>
    <div class='container d-flex flex-row justify-content-center align-items-center position-relative h-100'>
        <div class='row w-100'>
            <div class='col-md-{left_col_md} left-section'>
                <div class='title'>{left_title}</div>
                <div class='subtitle'>{left_subtitle}</div>
            </div>
            <div class='col-md-{right_col_md} offset-md-{right_col_offset} right-section'>
                <img src='{right_image_src}' alt='{right_image_alt}'>
            </div>
        </div>
    </div>
    <div class='decor-container'></div>

    <script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'></script>
</body>
</html>"""
    return html_code

def generate_split_layout_slide1(
    left_bg_color="#DFE9FF",
    left_title="Title",
    left_title_color="#1F3685",
    left_subtitle="SubTitle",
    left_subtitle_color="#2B4CC0",

    right_bg_color="#DFE9FF",
    right_image_src="path-to-your-image/image.png",
    right_image_alt="Image",
    decor_bg_color="#A6B4E5",
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
    bg_color="#e9f7fe",
    text_bg_color="#ffffff",
    text_color="#2e4e7e",
    keyword_color="#004080",
    image_bg_color="#b0d4f1",
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
    background_color="#e9f7fe",
    text_color="#2e4e7e",
    content_bg_color="#ffffff",
    content_shadow="0 6px 12px rgba(0, 0, 0, 0.1)",
    header_color="#004080",
    text_body_color="#2e4e7e",
    highlight_color="#ff4500",
    image_placeholder_text="[Image Placeholder]",
    image_bg_color="#b0d4f1",
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
    background_gradient=("#00c6ff", "#4facfe"),
    content_bg_opacity=0.8,
    content_shadow="0 4px 8px rgba(0, 0, 0, 0.1)",
    header_color="#333333",
    text_body_color="#333333",
    highlight_color="#ff4500",
    image_placeholder_text="Image Placeholder",
    image_bg_color="#cccccc",
    font_family="Roboto, Arial, sans-serif",
    paragraph_text="content paragraph"
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
    bg_color="#e0f7fa",  # Màu nền chính
    title_color='#003f72',
    objective_bg_color="#00c6ff",  # Màu nền của số thứ tự
    objective_text_color="#ffffff",  # Màu chữ của số thứ tự
    content_text_color="#ffffff",  # Màu chữ nội dung
    box_bg_color="#003f72",  # Màu nền của khung bao quanh content
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
    Tạo slide HTML với bố cục mục tiêu học tập.
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
    content_1="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris eleifend magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.",
    content_2="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris eleifend magna in sem rutrum luctus. Sed ullamcorper diam non venenatis dictum. Integer malesuada molestie mauris at scelerisque. Sed sit amet tempor nulla.",
    bg_color="#003f72",  # Màu nền chính
    title_color="#ffffff",  # Màu chữ tiêu đề
    content_color="#ffffff",  # Màu chữ nội dung
    number_bg_color="#00c6ff",  # Màu nền số thứ tự
    number_text_color="#ffffff",  # Màu chữ số thứ tự
    image_bg_color="#00c6ff",  # Màu nền khung chứa ảnh
    image_width="70%",  # Chiều rộng khung chứa ảnh
    image_height="60%",  # Chiều cao khung chứa ảnh
    border_radius="10px",  # Độ bo tròn cho các phần tử
    font_family="Roboto, Arial, sans-serif"  # Font chữ
):
    """
    Tạo slide HTML với bố cục về động vật đại dương.
    :param title: Tiêu đề của slide.
    :param content_1: Nội dung phần Animals 01.
    :param content_2: Nội dung phần Animals 02.
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
            <div class="number">Animals 01</div>
            <p class="content">{content_1}</p>
            <div class="number">Animals 02</div>
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
    elif name == "generate_conclusion_slide":
        return generate_conclusion_slide
    elif name == "generate_end_slide":
        return generate_end_slide
    else:
        raise ValueError(f"Function with name '{name}' not found.")



TOOLS = [
    {
  "type": "function",
  "function": {
    "name": "generate_intro_slide",
    "description": "Generate a highly customizable HTML slide with a split layout for presentations. This function creates an introduction slide with customizable left section containing title and subtitle, and a right section for an image. The slide includes decorative elements and supports extensive styling options.",
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
          "description": "Main title text displayed in the left section. Defaults to 'Title'.",
          "default": "Title"
        },
        "left_title_color": {
          "type": "string",
          "description": "Color of the title text. Defaults to '#1F3685'.",
          "default": "#1F3685"
        },
        "left_title_font_size": {
          "type": "string",
          "description": "Font size of the title text. Defaults to '48px'.",
          "default": "48px"
        },
        "left_title_margin_bottom": {
          "type": "string",
          "description": "Margin space below the title. Defaults to '20px'.",
          "default": "20px"
        },
        "left_subtitle": {
          "type": "string",
          "description": "Subtitle text displayed below the title in the left section. Defaults to 'Subtitle'.",
          "default": "Subtitle"
        },
        "left_subtitle_color": {
          "type": "string",
          "description": "Color of the subtitle text. Defaults to '#2B4CC0'.",
          "default": "#2B4CC0"
        },
        "left_subtitle_font_size": {
          "type": "string",
          "description": "Font size of the subtitle text. Defaults to '24px'.",
          "default": "24px"
        },
        "left_subtitle_margin_bottom": {
          "type": "string",
          "description": "Margin space below the subtitle. Defaults to '40px'.",
          "default": "40px"
        },
        "left_section_padding": {
          "type": "string",
          "description": "Padding inside the left section. Defaults to '60px'.",
          "default": "60px"
        },
        "left_col_md": {
          "type": "integer",
          "description": "Bootstrap column size for the left section (1-12). Defaults to 6.",
          "default": 6
        },
        "right_bg_color": {
          "type": "string",
          "description": "Background color of the right section. Defaults to '#DFE9FF'.",
          "default": "#DFE9FF"
        },
        "right_image_src": {
          "type": "string",
          "description": "Source URL or path to the image displayed in the right section. Defaults to 'path-to-your-image/image.png'.",
          "default": "path-to-your-image/image.png"
        },
        "right_image_alt": {
          "type": "string",
          "description": "Alternative text for the image. Defaults to 'Image'.",
          "default": "Image"
        },
        "right_image_width": {
          "type": "string",
          "description": "Width of the image (CSS value). Defaults to '100%'.",
          "default": "100%"
        },
        "right_image_height": {
          "type": "string",
          "description": "Height of the image (CSS value). Defaults to 'auto'.",
          "default": "auto"
        },
        "right_image_border_radius": {
          "type": "string",
          "description": "Border radius of the image (rounded corners). Defaults to '10px'.",
          "default": "10px"
        },
        "right_section_padding": {
          "type": "string",
          "description": "Padding inside the right section. Defaults to '28px'.",
          "default": "28px"
        },
        "right_section_border_radius": {
          "type": "string",
          "description": "Border radius of the right section. Defaults to '10px'.",
          "default": "10px"
        },
        "right_col_md": {
          "type": "integer",
          "description": "Bootstrap column size for the right section (1-12). Defaults to 4.",
          "default": 4
        },
        "right_col_offset": {
          "type": "integer",
          "description": "Bootstrap column offset for the right section. Defaults to 2.",
          "default": 2
        },
        "decor_bg_color": {
          "type": "string",
          "description": "Background color for decorative elements. Defaults to '#FFFFFF'.",
          "default": "#FFFFFF"
        },
        "decor_top_bg_color": {
          "type": "string",
          "description": "Background color for the top decorative element. Defaults to '#A6B4E5'.",
          "default": "#A6B4E5"
        },
        "decor_bottom_bg_color": {
          "type": "string",
          "description": "Background color for the bottom decorative element. Defaults to '#A6B4E5'.",
          "default": "#A6B4E5"
        },
        "decor_top_height": {
          "type": "string",
          "description": "Height of the top decorative element. Defaults to '50%'.",
          "default": "50%"
        },
        "decor_bottom_height": {
          "type": "string",
          "description": "Height of the bottom decorative element. Defaults to '30%'.",
          "default": "30%"
        },
        "body_bg_color": {
          "type": "string",
          "description": "Overall background color of the slide. Defaults to '#A6B4E5'.",
          "default": "#A6B4E5"
        },
        "font_family": {
          "type": "string",
          "description": "Font family for all text elements in the slide. Defaults to 'Roboto, Arial, sans-serif'.",
          "default": "Roboto, Arial, sans-serif"
        },
        "additional_css": {
          "type": "string",
          "description": "Additional CSS rules to be included in the slide's style section. Defaults to empty string.",
          "default": ""
        }
      },
      "required": []
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

# Step 1: Extract text from the .docx file
def extract_text_from_docx(file_path):
    """
    Extracts text from a .docx file.
    """
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        if para.text.strip():  # Ignore empty paragraphs
            text.append(para.text)
    return "\n".join(text)

# chia văn bản thành các khối có kích thước nhất định
# Step 2: Split text into chunks using LangChain
def split_text_into_chunks(text, chunk_size=300, chunk_overlap=50):
    """
    Splits text into chunks using LangChain's RecursiveCharacterTextSplitter.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks

# Input .docx file
docx_file = "/home/naver/Documents/Minh/SligenFunctionCalling/SlideGenFunctionCalling/Document/Test.docx"  # Replace with your .docx file path
# Convert .docx to slides
text = extract_text_from_docx(docx_file)
chunks = split_text_into_chunks(text, chunk_size=300, chunk_overlap=50)

for chunk in chunks:
    print(chunk)
    print("-" * 100)

# Step 1: Split the text by the delimiter "----------------------------------------------------------------------------------------------------"
# sections = text.strip().split("----------------------------------------------------------------------------------------------------")
sections = chunks

# Step 2: Clean and combine sections to ensure coherence
slide_contents = []
current_slide = ""
for section in sections:
    section = section.strip()
    if not section:
        continue
    # Nếu current_slide chưa có gì, thêm section ngay lập tức
    if not current_slide:
        current_slide = section
    else:
        # If the current slide is not too long, add the section to it
        if len(current_slide) + len(section) <= 1000:  # Adjust the limit as needed
            current_slide += "\n" + section if current_slide else section
        else:
            # If the current slide is too long, save it and start a new one
            slide_contents.append(current_slide)
            current_slide = section
# Add the last slide
if current_slide:
    slide_contents.append(current_slide)

# Step 3: Print the slide contents
for i, slide in enumerate(slide_contents):
    print(f"Slide {i + 1}:\n{slide}\n")

# Step 4: Save the slide contents to a list
slide_list = slide_contents

demand_prompt = """
Create a slide that match the following content, choose a function when you think it is best suit with the content:
You can also choose the function based on the previous slide content and function call, if there is no previous content or function call, which means this is the first slide.

Previous slide content:
{}

Previous function call:
{}

Current slide content:
{}

Current function call:
"""



def get_html_slide(pre_slide_content, pre_function_call, slide_content):
    MESSAGES = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user",  "content": demand_prompt.format(pre_slide_content, pre_function_call, slide_content)},
    ]


    # print(demand_prompt.format(pre_slide_content, pre_function_call, slide_content))

    tools = TOOLS
    global messages
    messages = MESSAGES[:]

    text = tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=False)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=512)
    global output_text
    output_text = tokenizer.batch_decode(outputs)[0][len(text):]
    return output_text

slide_function_calling_list = []
pre_slide_content = ""
pre_function_call = ""

for slide_content in slide_list:
    html_slide_call = get_html_slide(pre_slide_content, pre_function_call, slide_content)
    pre_slide_content = slide_content
    pre_function_call = html_slide_call
    print(html_slide_call)
    print("-" * 100)
    slide_function_calling_list.append(html_slide_call)


def try_parse_tool_calls(content: str):
    """Try parse the tool calls."""
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
            print(f"Failed to parse tool calls: the content is {m.group(1)} and {e}")
            pass
    if tool_calls:
        if offset > 0 and content[:offset].strip():
            c = content[:offset]
        else:
            c = ""
        return {"role": "assistant", "content": c, "tool_calls": tool_calls}
    return {"role": "assistant", "content": re.sub(r"<\|im_end\|>$", "", content)}

messages.append(try_parse_tool_calls(output_text))

if tool_calls := messages[-1].get("tool_calls", None):
    for tool_call in tool_calls:
        if fn_call := tool_call.get("function"):
            fn_name: str = fn_call["name"]
            fn_args: dict = fn_call["arguments"]

            fn_res: str = json.dumps(get_function_by_name(fn_name)(**fn_args))

            messages.append({
                "role": "tool",
                "name": fn_name,
                "content": fn_res,
            })

# Function to capture the HTML slide as an image

# Khởi tạo ChromeDriver một lần duy nhất
def initialize_chromedriver():
    try:
        chrome_driver_path = "/home/naver/.cache/selenium/chromedriver/linux64/134.0.6998.165/chromedriver"  # Thay bằng đường dẫn thực tế
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Chạy ẩn
        chrome_options.add_argument("--no-sandbox")  # Tắt sandbox
        chrome_options.add_argument("--disable-dev-shm-usage")  # Tránh lỗi bộ nhớ tạm
        chrome_options.add_argument("--disable-gpu")  # Tắt GPU
        chrome_options.add_argument("--window-size=1920,1080")  # Kích thước cửa sổ

        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error initializing ChromeDriver: {e}")
        return None

# Hàm chụp ảnh slide

def capture_slide_image(driver, html_content, output_path):
    try:
        # Lưu HTML tạm thời
        temp_html_path = "temporal_slide.html"
        with open(temp_html_path, "w", encoding="utf-8") as file:
            file.write(html_content)

        # Mở file HTML trong Selenium
        driver.get(f"file://{os.path.abspath(temp_html_path)}")
        driver.set_window_size(1920, 1080)  # Đặt kích thước cửa sổ

        # Chụp ảnh màn hình
        screenshot_bytes = driver.get_screenshot_as_png()

        # Chuyển đổi bytes thành đối tượng hình ảnh
        image = Image.open(io.BytesIO(screenshot_bytes))

        # Resize ảnh để phù hợp với mô hình
        image = image.resize((900, 500))

        # Lưu ảnh vào file đầu ra
        image.save(output_path)
        print(f"Ảnh đã được lưu tại: {output_path}")
        return image
    except Exception as e:
        print(f"Lỗi khi chụp ảnh: {e}")
        return None
    
def filter_string(s, s1, s2):
    # Tìm vị trí bắt đầu chuỗi s1 và kết thúc chuỗi s2
    start_index = s.find(s1)
    end_index = s.find(s2)

    # Kiểm tra xem cả s1 và s2 đều tồn tại trong chuỗi không
    if start_index != -1 and end_index != -1 and start_index < end_index:
        # Cắt chuỗi từ start_index đến end_index + len(s2) để bao gồm cả s2
        return s[start_index:end_index + len(s2)]
    else:
        # Nếu không tìm thấy s1 hoặc s2, trả về chuỗi rỗng hoặc chuỗi ban đầu
        return ""

def check_and_insert_char(s, i, char):
    # Kiểm tra xem ký tự tại vị trí i có phải là char không
    if s[i-1] != char:
        # Nếu không, chèn ký tự mới vào
        return s[:i] + char + s[i:]
    return s

def clean_slide_function (l):

  fixed_slide_function_calling_list = slide_function_calling_list.copy()

  for i in range(len(fixed_slide_function_calling_list)):
    fixed_slide_function_calling_list[i] = filter_string(fixed_slide_function_calling_list[i], '<tool_call>', '<|im_end|>')

  for i in range(len(fixed_slide_function_calling_list)):
    fixed_slide_function_calling_list[i] = check_and_insert_char(fixed_slide_function_calling_list[i], -20, '/')

  # Kiểm tra kết quả sau khi sửa
  print("slide_function_calling_list sau khi sửa:")
  for i, item in enumerate(fixed_slide_function_calling_list):
      print(f"Slide {i+1}: {item}")
      print("-" * 100)

  return fixed_slide_function_calling_list

slide_function_calling_list = clean_slide_function(slide_function_calling_list)

for i in slide_function_calling_list:
  print(i)
  print("-"*100)


VLMmodel = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct",
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
    
)

# default processer
VLMprocessor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct", use_fast=True)

# Chuẩn bị câu hỏi với tiêu chí cụ thể
criteria = """
1. The title must be clear and descriptive.
2. Text content should be readable with appropriate font size and color contrast.
3. Layout should be balanced, with no overlapping elements.
4. Images (if any) should be relevant and properly aligned.
5. Overall design should be visually appealing and professional.
"""

# Hàm đánh giá slide bằng VLM

# Hàm lọc slide lỗi
def filter_invalid_slides(html_content):
    invalid_html = "<html><body><h1>Lỗi tạo slide</h1></body></html>"
    return html_content != invalid_html

# Hàm xử lý tool call để tạo HTML (sửa để phát hiện lỗi nghiêm trọng)
def process_tool_call(tool_call_output):
    parsed_response = try_parse_tool_calls(tool_call_output)
    if not parsed_response or "tool_calls" not in parsed_response or not parsed_response["tool_calls"]:
        raise ValueError(f"tool_call_output không hợp lệ hoặc không chứa tool_calls: {tool_call_output}")

    tool_call = parsed_response["tool_calls"][0]
    fn_name = tool_call["function"]["name"]
    fn_args = tool_call["function"]["arguments"]
    try:
        html_content = get_function_by_name(fn_name)(**fn_args)
    except Exception as e:
        raise ValueError(f"Lỗi khi gọi hàm {fn_name} với arguments {fn_args}: {e}")

    return html_content


# Hàm đánh giá slide bằng VLM
def evaluate_slide_with_qwen(image_path, tool_call_output):
    try:
        # Đọc ảnh
        image = Image.open(image_path)

        # Chuẩn bị câu hỏi với tiêu chí
        question = f"""
        Evaluate this slide based on the following criteria:
        {criteria}
        If the slide does not meet all requirements, provide feedback and an improved version of the tool call.
        Keep the function name unchanged and only modify parameters.
        Current tool call:
        {tool_call_output}
        Your response must follow this format:
        <!-- accept/deny -->
        <!-- reason -->
       <tool_response>
        [tool_call_output with updated parameters if deny]
       </tool_call>
        """

        # Chuẩn bị đầu vào
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": question},
                ],
            }
        ]
        text = VLMprocessor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = VLMprocessor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to("cuda" if torch.cuda.is_available() else "cpu")

        # Dự đoán bằng mô hình
        with torch.no_grad():
            generated_ids = VLMmodel.generate(**inputs, max_new_tokens=512)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = VLMprocessor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        return output_text[0].strip()
    except Exception as e:
        print(f"Lỗi khi đánh giá slide bằng Qwen Vision: {e}")
        return None

# Hàm phân tích phản hồi từ VLM

def parse_vlm_response(vlm_response):
    try:
        print(f"Phản hồi từ VLM:\n{vlm_response}")
        lines = vlm_response.split("\n")

        # Kiểm tra định dạng cơ bản
        if len(lines) < 2:
            raise ValueError("Phản hồi từ VLM không đúng định dạng.")

        # Lấy trạng thái (accept/deny)
        status_line = lines[0].strip()
        if not status_line.startswith("<!--") or not status_line.endswith("-->"):
            raise ValueError("Dòng đầu tiên không chứa trạng thái.")
        status = status_line.strip("<!->").strip()

        # Lấy lý do từ chối (hoặc thông tin bổ sung nếu accept)
        reason_lines = []
        tool_calls = None

        if status == "accept":
            # Nếu trạng thái là accept, lý do nằm ở dòng thứ hai trở đi
            reason_lines = [line.strip() for line in lines[1:] if line.strip()]
            reason = "\n".join(reason_lines) if reason_lines else "No reason provided."
        elif status == "deny":
            # Nếu trạng thái là deny, lý do nằm ở dòng thứ hai trở đi cho đến khi gặp <tool_call>
            for i, line in enumerate(lines[1:], start=1):
                if line.strip().startswith("<tool_call>"):
                    # trích xuất từ đây đến cuối
                    tool_calls = "\n".join(lines[i:]).strip()
                    break
                reason_lines.append(line.strip())
            reason = "\n".join(reason_lines) if reason_lines else "No reason provided."
        else:
            raise ValueError(f"Trạng thái không hợp lệ: {status}")

        return status, reason, tool_calls
    except Exception as e:
        print(f"Lỗi khi phân tích phản hồi từ VLM: {e}")
        return None, None, None

# # Hàm đánh giá slide (giả lập)
# def evaluate_slide_image(html_content, slide_image):
#     return {'choices': [{'message': {'content': 'The slide is acceptable'}}]}

# Hàm tạo kế hoạch (giả lập)
def generate_plan_from_html(html_content):
    return "Kế hoạch chưa được triển khai"

# Xử lý slide_function_calling_list để tạo HTML và lưu file
df_dict = {"Raw Content": [], "Html Slide": [], "Plan": []}
pre_slide_content = ""  # Khởi tạo ngoài vòng lặp
pre_function_call = ""  # Khởi tạo ngoài vòng lặp

# Khởi tạo ChromeDriver một lần duy nhất
driver = initialize_chromedriver()
if not driver:
    print("Không thể khởi tạo ChromeDriver. Dừng chương trình.")
    exit(1)

# Số lần thử tối đa cho mỗi slide
max_attempts = 5

for i, (slide_content, tool_call_output) in enumerate(zip(slide_list, slide_function_calling_list)):
    df_dict["Raw Content"].append(slide_content)
    html_content = ""
    attempts = 0  # Đếm số lần thử cho slide hiện tại

    while attempts < max_attempts:
        attempts += 1
        print(f"Processing slide {i+1}, attempt {attempts}...")

        # Xử lý tool call để tạo HTML
        try:
            html_content = process_tool_call(tool_call_output)
        except ValueError as e:
            print(f"Slide {i+1} gặp lỗi nghiêm trọng: {e}")
            break

        # Kiểm tra nếu slide bị lỗi
        if not filter_invalid_slides(html_content):
            print(f"Slide {i+1} tạo HTML không hợp lệ: {html_content[:100]}...")
            break

        # Lưu file HTML tạm thời
        slide_dir = f"/home/naver/Documents/Minh/SligenFunctionCalling/SlideGenFunctionCalling/slide/slide_{i+1}"
        if not os.path.exists(slide_dir):
            os.makedirs(slide_dir)

        html_file_path = f"{slide_dir}/attempt_{attempts}.html"
        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML đã được lưu tại: {html_file_path}")

        # Chụp ảnh slide
        try:
            image_file_path = f"{slide_dir}/attempt_{attempts}.png"
            slide_image = capture_slide_image(driver, html_content, output_path=image_file_path)
        except Exception as e:
            print(f"Lỗi khi chụp ảnh slide {i+1}: {e}")
            slide_image = None
            break

        # Đánh giá slide bằng VLM
        try:
            evaluation_content = evaluate_slide_with_qwen(image_file_path, tool_call_output)
        except Exception as e:
            print(f"Lỗi khi đánh giá slide {i+1}: {e}")
            evaluation_content = "Retry"

        # Phân tích phản hồi từ VLM
        status, reason, new_tool_call_output = parse_vlm_response(evaluation_content)
        if not status or not reason:
            print("Phản hồi từ VLM không hợp lệ. Thử lại.")
            continue

        print(f"Trạng thái: {status}")
        print(f"Lý do: {reason}")

        # Nếu slide được chấp nhận, lưu mã HTML cuối cùng và kết thúc
        if status == "accept":
            print(f"Slide {i+1} được chấp nhận sau {attempts} lần thử.")
            final_html_path = f"{slide_dir}/final.html"
            final_image_path = f"{slide_dir}/final.png"
            with open(final_html_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
            if slide_image:
                slide_image.save(final_image_path)
            print(f"HTML và ảnh cuối cùng đã được lưu tại: {final_html_path} và {final_image_path}")
            break

        # Nếu slide không đạt yêu cầu, cập nhật tool_call_output
        if new_tool_call_output:
            print("Cập nhật tool_call_output với tham số mới.")
            tool_call_output = new_tool_call_output
            continue  # Quay lại đầu vòng lặp để thử lại

        # Nếu không thể cập nhật tool_call, dừng xử lý
        print("Không thể cập nhật tool_call_output. Dừng xử lý slide này.")
        break

    # Nếu vượt quá số lần thử mà vẫn không đạt yêu cầu
    if attempts == max_attempts and status != "accept":
        print(f"Slide {i+1} không đạt yêu cầu sau {max_attempts} lần thử. Lưu phiên bản cuối cùng của slide.")
        final_html_path = f"{slide_dir}/final.html"
        final_image_path = f"{slide_dir}/final.png"
        with open(final_html_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        if slide_image:
            slide_image.save(final_image_path)
        print(f"HTML và ảnh cuối cùng đã được lưu tại: {final_html_path} và {final_image_path}")

    # Lưu HTML và kế hoạch vào df_dict
    df_dict["Html Slide"].append(html_content)
    try:
        plan_content = generate_plan_from_html(html_content)
    except Exception as e:
        print(f"Lỗi khi tạo kế hoạch cho slide {i+1}: {e}")
        plan_content = "Kế hoạch không thể tạo"
    df_dict["Plan"].append(plan_content)

# Đóng trình duyệt sau khi hoàn thành
driver.quit()
print("Đã đóng trình duyệt.")

print("Đã hoàn thành xử lý (hoặc dừng do lỗi).")


# Định nghĩa các folder nguồn và đích
SOURCE_DIR = '/home/naver/Documents/Minh/SligenFunctionCalling/SlideGenFunctionCalling/slide'         # Thư mục chứa các slide con (slide1, slide2, ...)
HTML_OUTPUT_DIR = '/home/naver/Documents/Minh/SligenFunctionCalling/SlideGenFunctionCalling/slide_html'   # Thư mục chứa các file html sau khi copy
PNG_OUTPUT_DIR = '/home/naver/Documents/Minh/SligenFunctionCalling/SlideGenFunctionCalling/slide_png'     # Thư mục chứa các file png sau khi copy

# Tạo folder đích nếu chưa có
os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)
os.makedirs(PNG_OUTPUT_DIR, exist_ok=True)

# Duyệt qua từng thư mục slide
for slide_folder in os.listdir(SOURCE_DIR):
    slide_folder_path = os.path.join(SOURCE_DIR, slide_folder)
    
    # Kiểm tra folder hợp lệ
    if os.path.isdir(slide_folder_path) and slide_folder.startswith('slide'):
        slide_number = slide_folder.replace('slide', '')
        
        # Đường dẫn file HTML gốc và đích
        html_src = os.path.join(slide_folder_path, 'final.html')
        html_dst = os.path.join(HTML_OUTPUT_DIR, f'slide{slide_number}.html')

        # Đường dẫn file PNG gốc và đích
        png_src = os.path.join(slide_folder_path, 'final.png')
        png_dst = os.path.join(PNG_OUTPUT_DIR, f'slide{slide_number}.png')

        # Xử lý HTML
        if os.path.exists(html_src):
            shutil.copyfile(html_src, html_dst)
            print(f'✅ HTML: {html_src} -> {html_dst}')
        else:
            print(f'⚠️  Không tìm thấy {html_src}')

        # Xử lý PNG
        if os.path.exists(png_src):
            shutil.copyfile(png_src, png_dst)
            print(f'✅ PNG : {png_src} -> {png_dst}')
        else:
            print(f'⚠️  Không tìm thấy {png_src}')
