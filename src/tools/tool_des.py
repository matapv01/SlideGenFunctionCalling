# /app/src/tools.py

from typing import List, Dict, Any, Callable, Optional
from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool

# Import các hàm tạo HTML của bạn từ một file khác, ví dụ: 'html_lib.py'
# Đảm bảo rằng tên các hàm này khớp chính xác với tên tool.
from src.tools.html_tool import (
    generate_academic_slide,
    generate_content_slide,
    generate_two_column_slide,
    generate_project_circles_slide,
    generate_comparison_slide,
    generate_process_slide,
    generate_intro_slide,
    generate_body_slide1,
    generate_body_slide2,
    generate_body_slide3,
    generate_body_slide4,
    generate_body_slide5,
    generate_body_slide6,
    generate_body_slide7,
)

# ==============================================================================
# SECTION 1: ĐỊNH NGHĨA CÁC LỚP INPUT (ARGS_SCHEMA) BẰNG PYDANTIC
# ==============================================================================

class AcademicSlideInput(BaseModel):
    """Input schema for the generate_academic_slide tool."""
    title: str = Field(..., description="Main title of the slide. Default: 'YOUR TITLE HERE'.")
    description: str = Field(..., description="Description text below the title. Default: 'Add a short description'.")
    name: str = Field(default='Name: XXX', description="Name or attribution text. Default: 'Name: XXX'.")
    title_font_size: str = Field(default='48px', description="CSS font size for the title. Default: '48px'.")
    description_font_size: str = Field(default='32px', description="CSS font size for the description. Default: '32px'.")
    name_font_size: str = Field(default='18px', description="CSS font size for the name tag. Default: '18px'.")
    title_color: str = Field(default='#666666', description="CSS color for the title (e.g., '#666666'). Default: '#666666'.")
    description_color: str = Field(default='#888888', description="CSS color for the description. Default: '#888888'.")
    name_bg_color: str = Field(default='#777777', description="CSS background color for the name tag. Default: '#777777'.")
    name_text_color: str = Field(default='#ffffff', description="CSS text color for the name tag. Default: '#ffffff'.")
    background_color: str = Field(default='#ffffff', description="CSS background color for the slide. Default: '#ffffff'.")
    accent_color: str = Field(default='#a2c4c9', description="CSS background color for the slide container. Default: '#a2c4c9'.")
    divider_width: str = Field(default='60%', description="CSS width of the divider line. Default: '60%'.")
    divider_height: str = Field(default='2px', description="CSS height of the divider line. Default: '2px'.")
    divider_color: str = Field(default='#666666', description="CSS color of the divider line. Default: '#666666'.")
    icon_color: str = Field(default='#666666', description="CSS color for the graduation cap icon. Default: '#666666'.")
    box_shadow: str = Field(default='0 10px 30px rgba(0, 0, 0, 0.15)', description="CSS shadow effect for the slide. Default: '0 10px 30px rgba(0, 0, 0, 0.15)'.")
    font_family: str = Field(default='Arial, sans-serif', description="CSS font family for the slide. Default: 'Arial, sans-serif'.")

class ContentSlideInput(BaseModel):
    """Input schema for the generate_content_slide tool."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'CONTENT'.")
    items: List[str] = Field(..., description="List of item titles for the grid. Default: ['Your Title Here', ...] (6 items).")
    main_title_font_size: str = Field(default='60px', description="CSS font size for the main title. Default: '60px'.")
    number_font_size: str = Field(default='70px', description="CSS font size for item numbers. Default: '70px'.")
    item_title_font_size: str = Field(default='28px', description="CSS font size for item titles. Default: '28px'.")
    main_title_color: str = Field(default='#555555', description="CSS color for the main title. Default: '#555555'.")
    number_color: str = Field(default='#a2c4c9', description="CSS color for item numbers. Default: '#a2c4c9'.")
    item_title_color: str = Field(default='#555555', description="CSS color for item titles. Default: '#555555'.")
    background_color: str = Field(default='#ffffff', description="CSS background color for the slide. Default: '#ffffff'.")
    accent_color: str = Field(default='#a2c4c9', description="CSS color for corner accents. Default: '#a2c4c9'.")
    border_width: str = Field(default='30px', description="CSS width of the slide border. Default: '30px'.")
    font_family: str = Field(default='Arial, sans-serif', description="CSS font family for the slide. Default: 'Arial, sans-serif'.")
    num_columns: int = Field(default=3, description="Number of columns in the grid. Default: 3.", ge=1)
    num_rows: int = Field(default=2, description="Number of rows in the grid. Default: 2.", ge=1)

class TwoColumnSlideInput(BaseModel):
    """Input schema for the generate_two_column_slide tool."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'Your Title Here'.")
    left_column_titles: List[str] = Field(..., description="List of titles for the left column. Default: ['Your Title Here', 'Your Title Here'].")
    left_column_texts: List[str] = Field(..., description="List of texts for the left column. Default: two placeholder texts.")
    right_column_titles: List[str] = Field(..., description="List of titles for the right column. Default: ['Your Title Here', 'Your Title Here'].")
    right_column_texts: List[str] = Field(..., description="List of texts for the right column. Default: two placeholder texts.")
    main_title_font_size: str = Field(default='36px', description="CSS font size for the main title. Default: '36px'.")
    column_title_font_size: str = Field(default='24px', description="CSS font size for column titles. Default: '24px'.")
    column_text_font_size: str = Field(default='16px', description="CSS font size for column texts. Default: '16px'.")
    main_title_color: str = Field(default='#555555', description="CSS color for the main title. Default: '#555555'.")
    left_bg_color: str = Field(default='#a2c4c9', description="CSS background color for the left column. Default: '#a2c4c9'.")
    left_text_color: str = Field(default='#ffffff', description="CSS text color for the left column. Default: '#ffffff'.")
    right_title_color: str = Field(default='#555555', description="CSS color for right column titles. Default: '#555555'.")
    right_text_color: str = Field(default='#555555', description="CSS color for right column texts. Default: '#555555'.")
    border_color: str = Field(default='#a2c4c9', description="CSS color for the slide border. Default: '#a2c4c9'.")
    icon_color: str = Field(default='#a2c4c9', description="CSS color for right column icons. Default: '#a2c4c9'.")
    font_family: str = Field(default='Arial, sans-serif', description="CSS font family for the slide. Default: 'Arial, sans-serif'.")

class ProjectCirclesSlideInput(BaseModel):
    """Input schema for the generate_project_circles_slide tool."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'Your Title Here'.")
    project_names: List[str] = Field(..., description="List of three project names for the circles. Default: ['Project 1', 'Project 2', 'Project 3'].", min_length=3, max_length=3)
    left_title: str = Field(default='Your Title Here', description="Title for the left column.")
    right_title: str = Field(default='Your Title Here', description="Title for the right column.")
    left_text: str = Field(default='Placeholder text.', description="Text content for the left column.")
    right_text: str = Field(default='Placeholder text.', description="Text content for the right column.")
    footer_text: str = Field(default='Placeholder text.', description="Text content for the footer.")
    circle_colors: List[str] = Field(default=['#e1eff2', '#8cbeca', '#e1eff2'], description="List of three CSS colors for the circles.", min_length=3, max_length=3)
    main_title_font_size: str = Field(default='36px', description="CSS font size for the main title.")
    section_title_font_size: str = Field(default='24px', description="CSS font size for section titles.")
    text_font_size: str = Field(default='16px', description="CSS font size for main text.")
    footer_font_size: str = Field(default='14px', description="CSS font size for footer text.")
    title_color: str = Field(default='#555555', description="CSS color for all titles.")
    text_color: str = Field(default='#555555', description="CSS color for all text content.")
    circle_text_color: str = Field(default='#555555', description="CSS color for text in the circles. Note: Default color is dark for light default backgrounds.")
    background_color: str = Field(default='#ffffff', description="CSS background color for the slide.")
    accent_color: str = Field(default='#a2c4c9', description="CSS color for corner accents.")
    font_family: str = Field(default='Arial, sans-serif', description="CSS font family for the slide.")

class ComparisonSlideInput(BaseModel):
    """Input schema for the generate_comparison_slide tool."""
    main_title: str = Field(..., description="Main title of the slide.")
    left_title: str = Field(..., description="Title for the left column.")
    right_title: str = Field(..., description="Title for the right column.")
    left_text: str = Field(..., description="Text content for the left column.")
    right_text: str = Field(..., description="Text content for the right column.")
    left_icon: str = Field(default='gavel', description="Icon for the left column ('gavel' or 'custom').")
    right_icon: str = Field(default='scales', description="Icon for the right column ('scales' or 'custom').")
    custom_left_icon: str = Field(default='', description="Custom SVG code for left icon if 'custom'.")
    custom_right_icon: str = Field(default='', description="Custom SVG code for right icon if 'custom'.")
    main_title_font_size: str = Field(default='36px', description="CSS font size for the main title.")
    column_title_font_size: str = Field(default='28px', description="CSS font size for column titles.")
    text_font_size: str = Field(default='16px', description="CSS font size for text content.")
    title_color: str = Field(default='#555555', description="CSS color for all titles.")
    text_color: str = Field(default='#555555', description="CSS color for text content.")
    icon_color: str = Field(default='#a2c4c9', description="CSS color for icons.")
    background_color: str = Field(default='#ffffff', description="CSS background color for the slide.")
    accent_color: str = Field(default='#a2c4c9', description="CSS color for corner accents.")
    divider_color: str = Field(default='#555555', description="CSS color for the divider line.")
    font_family: str = Field(default='Arial, sans-serif', description="CSS font family for the slide.")

class ProcessSlideInput(BaseModel):
    """Input schema for the generate_process_slide tool."""
    main_title: str = Field(..., description="Main title of the slide.")
    left_title: str = Field(..., description="Title for the left box.")
    right_title: str = Field(..., description="Title for the right box.")
    left_content: str = Field(..., description="Content text for the left box.")
    right_content: str = Field(..., description="Content text for the right box.")
    main_title_font_size: str = Field(default='36px', description="CSS font size for the main title.")
    box_title_font_size: str = Field(default='28px', description="CSS font size for box titles.")
    content_font_size: str = Field(default='16px', description="CSS font size for content text.")
    title_color: str = Field(default='#555555', description="CSS color for the main title.")
    left_box_color: str = Field(default='#8cbeca', description="CSS background color for the left box.")
    right_box_color: str = Field(default='#c5e1e8', description="CSS background color for the right box.")
    text_color: str = Field(default='#ffffff', description="CSS color for text in the boxes.")
    arrow_color: str = Field(default='#f0f0f0', description="CSS color for the arrow connecting boxes.")
    background_color: str = Field(default='#ffffff', description="CSS background color for the slide.")
    accent_color: str = Field(default='#a2c4c9', description="CSS color for corner accents.")
    border_width: str = Field(default='30px', description="CSS width of the slide border.")
    font_family: str = Field(default='Arial, sans-serif', description="CSS font family for the slide.")
    box_width: str = Field(default='380px', description="CSS width of each box.")
    box_height: str = Field(default='350px', description="CSS height of each box.")
    box_border_radius: str = Field(default='5px', description="CSS border radius for the boxes.")

class IntroSlideInput(BaseModel):
    """Input schema for the generate_intro_slide tool."""
    main_title: str = Field(..., description="Main title text (e.g., 'Main Title').")
    subtitle1: str = Field(..., description="First subtitle text (e.g., 'Subtitle1').")
    subtitle2: str = Field(..., description="Second subtitle text (e.g., 'Subtitle2').")
    main_bg_color: str = Field(default='#ffffff', description="CSS main background color for the slide (e.g., '#ffffff').")
    accent_bg_color: str = Field(default='#6ea88a', description="CSS background color for the right section (e.g., '#6ea88a').")
    text_box_bg_color: str = Field(default='#c5e6b8', description="CSS background color for the text box (e.g., '#c5e6b8').")
    title_color: str = Field(default='#333333', description="CSS color for the main title (e.g., '#333333').")
    subtitle_color: str = Field(default='#555555', description="CSS color for the subtitles (e.g., '#555555').")
    line_color: str = Field(default='#e6c35c', description="CSS color for the horizontal divider line (e.g., '#e6c35c').")
    font_family: str = Field(default='Segoe UI, Arial, sans-serif', description="CSS font family for the slide.")
    main_title_font_size: str = Field(default='36px', description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default='16px', description="CSS font size for the subtitles.")
    main_title_font_style: str = Field(default='italic', description="CSS font style for the main title.")

class BodySlide1Input(BaseModel):
    """Input schema for the generate_body_slide1 tool."""
    vertical_title: str = Field(..., description="Vertical title text on the left (e.g., 'CONTENTS').")
    items_content: str = Field(..., description="HTML string for the content area, typically containing <ul> lists.")
    main_bg_color: str = Field(default='#e6f2dd', description="CSS background color for the main content area.")
    left_bg_color: str = Field(default='#ffffff', description="CSS background color for the left section.")
    title_color: str = Field(default='#333333', description="CSS color for the vertical title.")
    item_number_color: str = Field(default='#333333', description="CSS color for item numbers.")
    item_title_color: str = Field(default='#333333', description="CSS color for item titles.")
    item_text_color: str = Field(default='#555555', description="CSS color for item text.")
    vertical_title_font_size: str = Field(default='48px', description="CSS font size for the vertical title.")
    item_number_font_size: str = Field(default='28px', description="CSS font size for item numbers.")
    item_title_font_size: str = Field(default='18px', description="CSS font size for item titles.")
    item_text_font_size: str = Field(default='14px', description="CSS font size for item text.")
    font_family: str = Field(default='Segoe UI, Arial, sans-serif', description="CSS font family for the slide.")
    left_width: str = Field(default='15%', description="CSS width of the left section.")

class BodySlide2Input(BaseModel):
    """Input schema for the generate_body_slide2 tool."""
    main_title: str = Field(..., description="Main title of the slide.")
    subtitle1: str = Field(..., description="Subtitle for the first content section.")
    content1: str = Field(..., description="Content text for the first section.")
    subtitle2: str = Field(..., description="Subtitle for the second content section.")
    content2: str = Field(..., description="Content text for the second section.")
    subtitle3: str = Field(..., description="Subtitle for the third content section.")
    content3: str = Field(..., description="Content text for the third section.")
    main_bg_color: str = Field(default='#ffffff', description="CSS background color for the slide.")
    accent_color: str = Field(default='#d5e8b9', description="CSS color for accents and icon backgrounds.")
    title_color: str = Field(default='#333333', description="CSS color for the main title.")
    subtitle_color: str = Field(default='#333333', description="CSS color for subtitles.")
    content_color: str = Field(default='#555555', description="CSS color for content text.")
    title_font_size: str = Field(default='32px', description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default='20px', description="CSS font size for subtitles.")
    content_font_size: str = Field(default='16px', description="CSS font size for content text.")
    font_family: str = Field(default='Segoe UI, Arial, sans-serif', description="CSS font family for the slide.")
    icon1: str = Field(..., description="SVG code for the first section's icon.")
    icon2: str = Field(..., description="SVG code for the second section's icon.")
    icon3: str = Field(..., description="SVG code for the third section's icon.")

class BodySlide3Input(BaseModel):
    """Input schema for the generate_body_slide3 tool."""
    main_title: str = Field(..., description="Main title of the slide.")
    subtitle1: str = Field(..., description="Subtitle for the first content box.")
    content1: str = Field(..., description="Content text for the first content box.")
    subtitle2: str = Field(..., description="Subtitle for the second content box.")
    content2: str = Field(..., description="Content text for the second content box.")
    subtitle3: str = Field(..., description="Subtitle for the third content box.")
    content3: str = Field(..., description="Content text for the third content box.")
    main_bg_color: str = Field(default='#ffffff', description="CSS background color for the slide.")
    box_bg_color: str = Field(default='#e6f2dd', description="CSS background color for the content boxes.")
    accent_color: str = Field(default='#8cc63f', description="CSS color for accents and icons.")
    title_color: str = Field(default='#333333', description="CSS color for the main title.")
    subtitle_color: str = Field(default='#333333', description="CSS color for subtitles.")
    content_color: str = Field(default='#555555', description="CSS color for content text.")
    title_font_size: str = Field(default='32px', description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default='20px', description="CSS font size for subtitles.")
    content_font_size: str = Field(default='16px', description="CSS font size for content text.")
    font_family: str = Field(default='Segoe UI, Arial, sans-serif', description="CSS font family for the slide.")
    box_height: str = Field(default='250px', description="CSS height of the content boxes.")
    icon1: str = Field(..., description="SVG code for the first content box's icon.")
    icon2: str = Field(..., description="SVG code for the second content box's icon.")
    icon3: str = Field(..., description="SVG code for the third content box's icon.")

class BodySlide4Input(BaseModel):
    """Input schema for the generate_body_slide4 tool."""
    main_title: str = Field(..., description="Main title of the slide.")
    main_content: str = Field(..., description="Content text for the horizontal bar.")
    subtitle1: str = Field(..., description="Subtitle for the first image.")
    content1: str = Field(..., description="Content text for the first image.")
    subtitle2: str = Field(..., description="Subtitle for the second image.")
    content2: str = Field(..., description="Content text for the second image.")
    subtitle3: str = Field(..., description="Subtitle for the third image.")
    content3: str = Field(..., description="Content text for the third image.")
    main_bg_color: str = Field(default='#ffffff', description="CSS background color for the slide.")
    accent_color: str = Field(default='#d5e8b9', description="CSS color for accents and borders.")
    title_color: str = Field(default='#333333', description="CSS color for the main title.")
    content_color: str = Field(default='#555555', description="CSS color for content text.")
    subtitle_color: str = Field(default='#333333', description="CSS color for subtitles.")
    title_font_size: str = Field(default='32px', description="CSS font size for the main title.")
    content_font_size: str = Field(default='16px', description="CSS font size for content text.")
    subtitle_font_size: str = Field(default='18px', description="CSS font size for subtitles.")
    font_family: str = Field(default='Segoe UI, Arial, sans-serif', description="CSS font family for the slide.")

class BodySlide5Input(BaseModel):
    """Input schema for the generate_body_slide5 tool."""
    main_title: str = Field(..., description="Main title of the slide.")
    subtitle1: str = Field(..., description="Subtitle for the first content section.")
    content1: str = Field(..., description="Content text for the first content section.")
    subtitle2: str = Field(..., description="Subtitle for the second content section.")
    content2: str = Field(..., description="Content text for the second content section.")
    subtitle3: str = Field(..., description="Subtitle for the third content section.")
    content3: str = Field(..., description="Content text for the third content section.")
    subtitle4: str = Field(..., description="Subtitle for the fourth content section.")
    content4: str = Field(..., description="Content text for the fourth content section.")
    main_bg_color: str = Field(default='#ffffff', description="CSS background color for the slide.")
    accent_color: str = Field(default='#d5e8b9', description="CSS color for accents and borders.")
    title_color: str = Field(default='#333333', description="CSS color for the main title.")
    subtitle_color: str = Field(default='#6b9d34', description="CSS color for subtitles.")
    content_color: str = Field(default='#555555', description="CSS color for content text.")
    title_font_size: str = Field(default='32px', description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default='18px', description="CSS font size for subtitles.")
    content_font_size: str = Field(default='14px', description="CSS font size for content text.")
    font_family: str = Field(default='Segoe UI, Arial, sans-serif', description="CSS font family for the slide.")

class BodySlide6Input(BaseModel):
    """Input schema for the generate_body_slide6 tool."""
    main_title: str = Field(..., description="Main title of the slide.")
    subtitle1: str = Field(..., description="Subtitle for the first content section.")
    content1: str = Field(..., description="Content text for the first content section.")
    subtitle2: str = Field(..., description="Subtitle for the second content section.")
    content2: str = Field(..., description="Content text for the second content section.")
    main_bg_color: str = Field(default='#ffffff', description="CSS background color for the slide.")
    accent_color: str = Field(default='#d5e8b9', description="CSS color for accents and subtitle backgrounds.")
    title_color: str = Field(default='#333333', description="CSS color for the main title.")
    subtitle_color: str = Field(default='#333333', description="CSS color for subtitles.")
    content_color: str = Field(default='#555555', description="CSS color for content text.")
    title_font_size: str = Field(default='32px', description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default='18px', description="CSS font size for subtitles.")
    content_font_size: str = Field(default='16px', description="CSS font size for content text.")
    font_family: str = Field(default='Segoe UI, Arial, sans-serif', description="CSS font family for the slide.")

class BodySlide7Input(BaseModel):
    """Input schema for the generate_body_slide7 tool."""
    main_title: str = Field(..., description="Main title of the slide.")
    subtitle: str = Field(..., description="Subtitle for the right column.")
    content1: str = Field(..., description="First content text section.")
    content2: str = Field(..., description="Second content text section.")
    main_bg_color: str = Field(default='#ffffff', description="CSS background color for the slide.")
    accent_color: str = Field(default='#d5e8b9', description="CSS color for accents, such as the title accent block.")
    title_color: str = Field(default='#333333', description="CSS color for the main title.")
    subtitle_color: str = Field(default='#333333', description="CSS color for the subtitle.")
    content_color: str = Field(default='#4a90a0', description="CSS color for content text.")
    divider_color: str = Field(default='#d5e8b9', description="CSS color for the horizontal divider.")
    title_font_size: str = Field(default='32px', description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default='28px', description="CSS font size for the subtitle.")
    content_font_size: str = Field(default='16px', description="CSS font size for content text.")
    font_family: str = Field(default='Segoe UI, Arial, sans-serif', description="CSS font family for the slide.")

# ==============================================================================
# SECTION 2: TẠO DANH SÁCH ALL_TOOLS BẰNG StructuredTool
# ==============================================================================

ALL_TOOLS: List[StructuredTool] = [
    StructuredTool.from_function(
        func=generate_academic_slide,
        name="generate_academic_slide",
        description="Generates an HTML academic slide with a graduation cap icon, title, description, and name tag.",
        args_schema=AcademicSlideInput
    ),
    StructuredTool.from_function(
        func=generate_content_slide,
        name="generate_content_slide",
        description="Generates an HTML slide with a main title and a grid of numbered items, ideal for listing topics or points.",
        args_schema=ContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_two_column_slide,
        name="generate_two_column_slide",
        description="Generates an HTML slide with two columns of titles and texts, with customizable styling.",
        args_schema=TwoColumnSlideInput
    ),
    StructuredTool.from_function(
        func=generate_project_circles_slide,
        name="generate_project_circles_slide",
        description="Generates an HTML slide with a main title, two text columns, three project circles, and an alternating border design.",
        args_schema=ProjectCirclesSlideInput
    ),
    StructuredTool.from_function(
        func=generate_comparison_slide,
        name="generate_comparison_slide",
        description="Generates an HTML slide with a main title, two comparison columns with icons, and a matching border design.",
        args_schema=ComparisonSlideInput
    ),
    StructuredTool.from_function(
        func=generate_process_slide,
        name="generate_process_slide",
        description="Generates an HTML slide with a main title and two process boxes connected by an arrow.",
        args_schema=ProcessSlideInput
    ),
    StructuredTool.from_function(
        func=generate_intro_slide,
        name="generate_intro_slide",
        description="Generates an HTML introduction slide with a main title section on the left and an image on the right.",
        args_schema=IntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_body_slide1,
        name="generate_body_slide1",
        description="Generates an HTML slide with a vertical title on the left, content in the middle, and an image on the right, using a single HTML string for content.",
        args_schema=BodySlide1Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide2,
        name="generate_body_slide2",
        description="Generates an HTML slide with a main title, a large image on the left, and three content sections with icons on the right.",
        args_schema=BodySlide2Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide3,
        name="generate_body_slide3",
        description="Generates an HTML slide with a main title and three content boxes, each with an icon, subtitle, and content text in a three-column layout.",
        args_schema=BodySlide3Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide4,
        name="generate_body_slide4",
        description="Generates an HTML slide with a main title, a horizontal content bar, and three images with subtitles and content text.",
        args_schema=BodySlide4Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide5,
        name="generate_body_slide5",
        description="Generates an HTML slide with a main title, a 2x2 image grid on the left, and four content sections on the right.",
        args_schema=BodySlide5Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide6,
        name="generate_body_slide6",
        description="Generates an HTML slide with a main title, an image on the right, and two content sections on the left.",
        args_schema=BodySlide6Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide7,
        name="generate_body_slide7",
        description="Generates an HTML slide with a main title, three vertical images on the left, and a subtitle with two content sections on the right, separated by a divider.",
        args_schema=BodySlide7Input
    ),
]

# ==============================================================================
# SECTION 3: HÀM THỰC THI TOOL
# ==============================================================================

# Tạo một map để dễ dàng truy cập tool bằng tên, giúp tăng hiệu suất
TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}

def execute_tool(tool_call: Dict[str, Any]) -> str:
    """
    Thực thi một tool call (dictionary) và trả về kết quả (chuỗi HTML).
    """
    tool_name = tool_call.get("name")
    tool_args = tool_call.get("arguments", {})
    
    if not tool_name:
        raise ValueError("Tool call is missing a name.")
    
    if tool_name not in TOOL_MAP:
        # Trả về một thông báo lỗi thân thiện hơn nếu LLM bịa ra một tool không tồn tại
        error_message = f"Error: Tool with name '{tool_name}' not found. Available tools are: {list(TOOL_MAP.keys())}"
        print(error_message)
        return f"<html><body><h1>Invalid Tool Error</h1><p>{error_message}</p></body></html>"
        
    try:
        # Lấy đối tượng tool từ map
        tool_to_run = TOOL_MAP[tool_name]
        # .invoke sẽ tự động validate `tool_args` bằng `args_schema` của tool
        # và sau đó gọi hàm `func` với các đối số đã được validate.
        html_output = tool_to_run.invoke(tool_args)
        return str(html_output) # Đảm bảo output luôn là string
    except Exception as e:
        # Bắt lỗi validation từ Pydantic hoặc lỗi từ hàm thực thi
        error_message = f"Error executing tool '{tool_name}' with args {tool_args}: {e}"
        print(error_message)
        # Trả về một slide báo lỗi chi tiết
        return f"<html><body><h1>Tool Execution Error</h1><p>{error_message}</p></body></html>"