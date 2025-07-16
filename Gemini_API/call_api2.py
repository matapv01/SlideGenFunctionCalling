#langchain
#google-genai==1.16.1

from google import genai
from google.genai import types
import os
# dotenv load
from dotenv import load_dotenv
load_dotenv()

from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import time


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
    font_family="Roboto, Arial, sans-serif",
    content_paragraph="This is a customizable slide. Add your content here:",
    para_font_size="24px",
    list_items=None
):
    """
    Generate a professional HTML slide body with customizable parameters.

    :param title: The title of the HTML document.
    :param title_font_size: Font size of the slide title.
    :param slide_title: The title displayed on the slide.
    :param bg_color: Background color of the page.
    :param text_bg_color: Background color of the text container.
    :param text_color: Text color of the slide content.
    :param keyword_color: Color for keywords.
    :param font_family: Font family for the slide content.
    :param content_paragraph: Main paragraph content.
    :param para_font_size: Font size of the paragraph and list items.
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
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
            height: 100vh;
            padding: 20px;
        }}
        .slide-title {{
            color: {keyword_color};
            font-size: {title_font_size};
            margin-bottom: 15px;
            font-weight: bolder;
        }}
        .slide-content {{
            background-color: {text_bg_color};
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            color: {text_color};
            max-width: 1000px; /* Adjusted width for a balanced look */
            width: 90%;
        }}
        .text-content {{
            width: 100%;
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
        .keyword {{
            color: {keyword_color};
            font-weight: bold;
        }}
        @media (max-width: 768px) {{
            .slide-content {{
                width: 100%;
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="slide-title">{slide_title}</div>
        <div class="slide-content">
            <div class="text-content">
                <p>{content_paragraph}</p>
                <ul>
                    {list_html}
                </ul>
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
    :param font_family: The font family to use for all text.
    :param paragraph_text: The content paragraph.
    :param para_font_size: Font size of the paragraph text.
    :return: A string containing the HTML code.
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
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
            padding: 20px;
        }}

        .content-box {{
            background-color: {content_bg_color};
            border-radius: 12px;
            box-shadow: {content_shadow};
            padding: 40px;
            color: {text_body_color};
            width: 90%;
            max-width: 1000px; 
            text-align: left;
        }}

        h1 {{
            color: {header_color};
            font-size: {header_font_size};
            margin-bottom: 20px;
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
                width: 100%;
                padding: 20px;
            }}
        }}
    </style>
</head>

<body>
    <div class="slide-container">
        <div class="content-box">
            <h1>{header_text}</h1>
            <p>{paragraph_text}</p>
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
        "Paragraph 1: Present with ease and wow any audience with Canva Presentations. Choose from over a thousand professionally-made templates to fit any objective or topic. Make it your own by customizing it with text and photos.",
        "Paragraph 2: Present with ease and wow any audience with Canva Presentations. Choose from over a thousand professionally-made templates to fit any objective or topic. Make it your own by customizing it with text and photos."
    ],
    left_bg_color="#F3F6FA",
    right_bg_color="#cdecda",
    text_color="#333333",
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

def get_function_by_name(tool_call):
    if tool_call.name == "generate_intro_slide":
        return generate_intro_slide(**tool_call.args)
    elif tool_call == "generate_body_slide1":
        return generate_body_slide1(**tool_call.args)
    elif tool_call == "generate_body_slide2":
        return generate_body_slide2(**tool_call.args)
    elif tool_call == "generate_body_slide3":
        return generate_body_slide3(**tool_call.args)
    elif tool_call == "generate_body_slide6":
        return generate_body_slide6(**tool_call.args)
    elif tool_call == "generate_body_slide7":
        return generate_body_slide7(**tool_call.args)
    elif tool_call == "generate_body_slide8":
        return generate_body_slide8(**tool_call.args)
    elif tool_call == "generate_conclusion_slide":
        return generate_conclusion_slide(**tool_call.args)
    else:
        raise ValueError(f"Function with name '{tool_call}' not found.")


# --- GEMINI TOOL DEFINITIONS (Adjusted from your original TOOLS) ---
TOOLS = [
    {
        "name": "generate_intro_slide",
        "description": "Generates a customizable HTML slide with an introduction layout. Use for introductory slides, section breaks, or simple title slides.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Main title text for the slide (e.g., 'Introduction', 'Chapter 1'). Should be concise."},
                "title_color": {"type": "string", "description": "CSS color for the title (e.g., '#0F4662', 'blue'). Default: '#0F4662'."},
                "title_font_size": {"type": "string", "description": "CSS font size for the title (e.g., '42px'). Default: '42px'."},
                "title_font_style": {"type": "string", "description": "CSS font style for the title (e.g., 'italic', 'normal'). Default: 'italic'."},
                "content_text": {"type": "string", "description": "Brief content text or subtitle. Keep it short for an intro slide. Default: 'Content'."},
                "content_color": {"type": "string", "description": "CSS color for content text. Default: '#0F4662'."},
                "content_font_size": {"type": "string", "description": "CSS font size for content. Default: '24px'."},
                "slide_bg_color": {"type": "string", "description": "CSS background color for the entire slide. Default: '#f5f5f5'."},
                # Added other relevant params from function signature with defaults, keep descriptions concise
                "dot_count": {"type": "integer", "description": "Number of decorative dots. Default: 5."},
                "font_family": {"type": "string", "description": "CSS font family. Default: 'Roboto, Arial, sans-serif'."},
            },
            "required": ["title"] # Example: title is usually required
        }
    },
    {
        "name": "generate_body_slide1",
        "description": "Generates a professional HTML slide with a title, a paragraph, and a list of bullet points. Ideal for presenting structured textual information in detail.",
        "parameters": {
            "type": "object",
            "properties": {
                "slide_title": {"type": "string", "description": "The main title displayed at the top of the slide content."},
                "content_paragraph": {"type": "string", "description": "The main paragraph text. Can be a summary or introductory text for the bullet points."},
                "list_items": {
                    "type": "array",
                    "description": "A list of strings, where each string is a bullet point. HTML can be embedded for emphasis (e.g., '<b>Keyword</b>: details').",
                    "items": {"type": "string"}
                },
                "title_font_size": {"type": "string", "description": "CSS font size for the slide_title. Default: '42px'."},
                "bg_color": {"type": "string", "description": "CSS background color for the entire slide. Default: '#E8F5E9'."},
                "text_bg_color": {"type": "string", "description": "CSS background color for the main text content area. Default: '#FFFFFF'."},
                "text_color": {"type": "string", "description": "CSS color for paragraph and list items. Default: '#2E7D32'."},
                "keyword_color": {"type": "string", "description": "CSS color for keywords (used for slide_title and can be used in list_items). Default: '#1B5E20'."},
                "font_family": {"type": "string", "description": "CSS font family. Default: 'Roboto, Arial, sans-serif'."},
                "para_font_size": {"type": "string", "description": "CSS font size for paragraph and list items. Default: '24px'."},
                "title": {"type": "string", "description": "HTML document title (browser tab). Default: 'Professional HTML Slide'."}
            },
            "required": ["slide_title", "content_paragraph"] # Example
        }
    }
]

import re
import json
import logging
logger = logging.getLogger(__name__)

def extract_text_from_docx(file_path):
    print(f"Extracting text from {file_path}")
    doc = Document(file_path)
    text = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(text)

def split_text_into_chunks(text, chunk_size=300, chunk_overlap=50):
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
            if len(current_slide) + len(section) <= 1000:
                current_slide += "\n" + section
            else:
                slide_list.append(current_slide)
                current_slide = section
    if current_slide:
        slide_list.append(current_slide)
    return slide_list

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
        - `<span style="font-size: Xrem">` for size correction (X ≥ 1.125 for body, X ≥ 1.5 for titles).
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
        - Return {{}} if no split is needed.
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
            "split_reason": ""
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
                "split_reason": ""
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

def safe_generate_content(model, contents, tools=None, max_retries=10, delay=15):
    API_KEY_LIST = ['MATA01', 'GEMINI_API_KEY',  'AQUANG1', 'AQUANG2']
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


docx_file = "C:\\Users\\pvmkt\\OneDrive\\Desktop\\SlideGenSourceCode\\Gemini_API\\SlideGenFunctionCalling\\Document\\nature.docx"  # Replace with your actual DOCX file path
print(f"Processing slides from {docx_file}")
text = extract_text_from_docx(docx_file)
chunks = split_text_into_chunks(text)
slide_list = create_slide_list(chunks)

slide_function_calling_list = []
pre_slide_content = ""
pre_function_call = ""
cnt = 1
api_call_cnt = 0
for slide_content in slide_list:
    text, current_tool_call, text_json = get_html_slide(pre_slide_content, pre_function_call, slide_content)
    api_call_cnt += 1
    print(f"Slide {cnt} processed, API call count: {api_call_cnt}")
    cnt += 1
    slide_function_calling_list.append(current_tool_call)
    pre_slide_content = slide_content
    pre_function_call = current_tool_call
    print(f"tool_call: {current_tool_call}")
    print(f"text: {text}")
    print(f"text_json: {text_json}")
print("All slides processed.")
