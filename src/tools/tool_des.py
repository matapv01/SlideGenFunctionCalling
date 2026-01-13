# Auto-generated from tools.py preserving all original parameter schemas
# This conversion maintains the exact parameter definitions from the source

from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


# Import all slide generation functions from html_tool
from src.tools.html_tool import (
    generate_title_slide,   # slide intro
    generate_introduction_slide, # slide intro
    generate_intro_slide1, # slide intro
    generate_elegant_intro_slide,   # slide intro
    generate_inspirational_quote_slide, # slide intro
    generate_title_slide_2, # slide intro
    generate_dynamic_intro_slide,   # slide intro
    generate_big_concept_slide, # slide intro
    generate_elegant_agenda_slide, # slide intro
    generate_playful_title_slide, # slide intro
    generate_minimalist_title_slide,    # slide intro
    generate_mission_slide, # slide intro
    generate_training_intro_slide, # slide intro
    generate_employee_intro_slide, # slide intro
    generate_research_proposal_slide, # slide intro
    generate_business_intro_slide, # slide intro
    generate_company_mission_slide, # slide intro
    generate_title_slide_3,# slide intro(hien)
    generate_minimalist_slide, # slide intro(hien)
    generate_title_slide_4, # slide intro(hien)
    generate_title_slide_5, # slide intro(hien)
    generate_title_slide_6, # slide intro(hien)
  
    
    generate_geometric_transition_slide, # slide chuyển slide 
    generate_dusk_transition_slide, # slide chuyển slide
    generate_memphis_transition_slide, # slide chuyển slide
    generate_pushpin_section_header,    # slide chuyển slide
    generate_section_header_slide,  # slide chuyển slide
    generate_intro_slide, # slide chuyển slide
    generate_research_proposal_transition_slide, # slide chuyển slide
    generate_business_transition_slide, # slide chuyển slide
    generate_section_header_slide_5, # slide chuyển slide(hien)
    generate_section_header_slide_6, # slide chuyển slide(hien)
    generate_section_header_slide_8, # slide chuyển slide(hien)
    generate_section_header_slide_9, # slide chuyển slide(hien)
    generate_section_header_slide_10, # slide chuyển slide(hien)
    generate_section_header_slide_12, # slide chuyển slide(hien)
    generate_section_header_slide_13, # slide chuyển slide(hien)

    generate_section_header_slide_15, # slide chuyển slide(hien)



    generate_content_slide, # slide content
    generate_comparison_slide,  # slide content
    generate_process_slide,  # slide content
    generate_process_steps_slide, # slide content
    generate_icon_list_slide_2, # slide content
    generate_image_cutout_list_slide, # slide content
    generate_body_slide2,  # slide content
    generate_body_slide4,  # slide content
    generate_body_slide5,  # slide content
    generate_body_slide7,  # slide content
    generate_body_slide10,  # slide content
    generate_body_slide11,  # slide content
    generate_body_slide12,  # slide content
    generate_body_slide15,  # slide content
    generate_body_slide18,  # slide content
    generate_body_slide19,  # slide content
    generate_body_slide20,  # slide content
    generate_main_points_slide, # slide content
    generate_elegant_points_slide,  # slide content
    generate_corporate_content_slide,   # slide content
    generate_split_content_slide,   # slide content
    generate_corporate_multicolumn_slide,   # slide content
    generate_corporate_grid_slide,  # slide content
    generate_business_overview_slide,   # slide content
    generate_vision_mission_slide,  # slide content
    generate_strategic_goals_slide, # slide content
    generate_service_roadmap_slide, # slide content
    generate_financial_projections_slide_dark, # slide content
    generate_minimalist_tech_list_slide,    # slide content
    generate_centered_tech_columns_slide,   # slide content
    generate_split_layout_list_slide, # slide content
    generate_reference_slide,   # slide content
    generate_icon_list_slide,   # slide content
    generate_flexible_columns_slide, # slide content
    generate_text_with_image_slide, # slide content
    generate_instructions_slide,   # slide content
    generate_geometric_split_content_slide, # slide content
    generate_geometric_split_content_slide_2, # slide content
    generate_geometric_image_content_slide, # slide content
    generate_geometric_content_slide, # slide content
    generate_geometric_grid_slide,  # slide content
    generate_memphis_content_slide, # slide content
    generate_memphis_multicolumn_slide, # slide content
    generate_memphis_grid_slide, # slide content
    generate_premium_abstract_slide, # slide content
    generate_methodology_slide, # slide content
    generate_planning_phase_slide, # slide content



    generate_team_slide, # slide giới thiệu team 
    generate_colorful_team_grid_slide,  # slide giới thiệu team
    generate_corporate_team_slide, # slide giới thiệu team
    
    

    
    
    generate_thank_you_slide_3, # slide cảm ơn
    generate_corporate_thank_you_slide, # slide cảm ơn
    generate_business_thank_you_slide, # slide cảm ơn
    generate_thank_you_slide_4, # slide cảm ơn(hien)
    generate_thank_you_decorative_slide, # slide cảm ơn(hien)
    generate_watercolor_thank_you_slide, # slide cảm ơn(hien)
    generate_thank_you_slide_5, # slide cảm ơn(hien)
    generate_thank_you_slide_6, # slide cảm ơn(hien)
    generate_thank_you_slide_7, # slide cảm ơn(hien)

)

# ===========================================================================================
# PYDANTIC INPUT SCHEMAS ORDERED ACCORDING TO IMPORT SEQUENCE
# ===========================================================================================

# === SLIDE INTRO CLASSES ===

class GenerateTitleSlideInput(BaseModel):
    """Input schema for generate_title_slide."""
    main_title: str = Field(..., description="Main title text (10-30 characters), displayed prominently in the center. Default: 'BUSINESS PLAN'.")
    subtitle: str = Field(..., description="Subtitle text (5-20 characters), displayed below the main title. Default: '2026 - 2030'.")
    bg_color: str = Field(default="#1a4b8c", description="Primary background color (hex code).")
    bg_gradient_to: str = Field(default="#2a6cb7", description="Secondary background color for gradient effect (hex code).")
    text_color: str = Field(default="#FFFFFF", description="Color of the title and subtitle text (hex code).")
    font_family: str = Field(default="'Inter', sans-serif", description="Font family for all text elements.")
    show_skyline: Optional[bool] = Field(default=True, description="Whether to show the city skyline silhouette at the bottom. Default: True.")
    skyline_opacity: Optional[float] = Field(default=0.3, description="Opacity of the skyline silhouette (0.0 to 1.0). Default: 0.3.")
    triangle_opacity: Optional[float] = Field(default=0.2, description="Opacity of the triangle decorative elements (0.0 to 1.0). Default: 0.2.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show the border frame. Default: True.")
    custom_css: str = Field(default="", description="Additional custom CSS to be included.")


class GenerateIntroductionSlideInput(BaseModel):
    """Input schema for generate_introduction_slide."""
    main_title: str = Field(..., description="Main title text (8-20 characters). Default: 'INTRODUCTION'.")
    content_text: str = Field(..., description="Main content paragraph.. Default: Lorem ipsum text.")
    bg_color: str = Field(default="#1a4b8c", description="Primary background color (hex code).")
    bg_gradient_to: str = Field(default="#2a6cb7", description="Secondary background color for gradient effect (hex code).")
    text_color: str = Field(default="#FFFFFF", description="Color of all text elements (hex code).")
    font_family: str = Field(default="'Inter', sans-serif", description="Font family for all text elements.")
    show_decorative_triangles: Optional[bool] = Field(default=True, description="Whether to show decorative triangle elements. Default: True.")
    triangle_opacity: Optional[float] = Field(default=0.15, description="Opacity of the decorative triangles (0.0 to 1.0). Default: 0.15.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
    border_opacity: Optional[float] = Field(default=0.4, description="Opacity of the border frame (0.0 to 1.0). Default: 0.4.")
    content_max_width: str = Field(default="800px", description="Maximum width of the content area.")
    line_height: str = Field(default="1.6", description="Line height for the content text.")
    letter_spacing: str = Field(default="0.1em", description="Letter spacing for the title.")
    custom_css: str = Field(default="", description="Additional custom CSS to be included.")

class GenerateIntroSlide1Input(BaseModel):
    """Input schema for generate_intro_slide1."""
    main_title: str = Field(..., description="Main title text. Default: 'Main Title'.")
    subtitle1: str = Field(..., description="First subtitle text. Default: 'Subtitle1'.")
    subtitle2: str = Field(..., description="Second subtitle text. Default: 'Subtitle2'.")
    main_bg_color: str = Field(default="#ffffff", description="CSS main background color for the slide.")
    accent_bg_color: str = Field(default="#6ea88a", description="CSS background color for the right section.")
    text_box_bg_color: str = Field(default="#c5e6b8", description="CSS background color for the text box.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#555555", description="CSS color for the subtitles.")
    line_color: str = Field(default="#e6c35c", description="CSS color for the horizontal divider line.")
    font_family: str = Field(default="'Inter', sans-serif", description="CSS font family for the slide.")
    main_title_font_style: str = Field(default="italic", description="CSS font style for the main title.")
    image_url: str = Field(default="Image/generate_intro_slide1/Default_1.png", description="Path to the image file for the left side.")


class GenerateElegantIntroSlideInput(BaseModel):
    """Input schema for generate_elegant_intro_slide."""
    main_title: str = Field(..., description="The large title displayed in the left column. Default: 'Write Your Topic or Idea Here'.")
    subtitle: str = Field(..., description="The smaller subtitle text below the main title. Default: 'Briefly elaborate on what you want to discuss.'.")
    image_url: str = Field(default="https://images.pexels.com/photos/3807735/pexels-photo-3807735.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", description="URL for the main image to be displayed on the right.")
    font_family: str = Field(default="'Be Vietnam Pro', sans-serif", description="Font family for all text elements.")
    background_color: str = Field(default="#EAE3D9", description="Background color of the slide.")
    text_color: str = Field(default="#4A403A", description="Main text color for titles and descriptions.")
    decoration_color_start: str = Field(default="#F7DC6F", description="The starting color for the gold gradient decorations.")
    decoration_color_end: str = Field(default="#C9A842", description="The ending color for the gold gradient decorations.")

class GenerateInspirationalQuoteSlideInput(BaseModel):
    """Input schema for generate_inspirational_quote_slide."""
    quote_text: str = Field(..., description="The main quote or statement, displayed in a large, elegant font. Default: 'The best way to predict the future is to create it.'.")
    attribution_text: str = Field(..., description="The attribution for the quote (e.g., author, source). Default: 'Peter Drucker'.")
    font_family: str = Field(default="'Playfair Display', 'Inter', serif", description="Font family for all text elements. A serif font like 'Playfair Display' is recommended.")
    background_image_url: str = Field(default="https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=2069&auto=format&fit=crop", description="URL for the full-screen background image. A bright, clean image is recommended for this theme.")
    text_color: str = Field(default="#3A3A3A", description="Text color for the quote and attribution. A dark color is recommended for light backgrounds.")
    decoration_color: str = Field(default="rgba(0, 0, 0, 0.08)", description="Color of the large, decorative quotation marks. A subtle, semi-transparent color is recommended.")

class GenerateTitleSlide2Input(BaseModel):
    """Input schema for generate_title_slide_2."""
    main_title: str = Field(..., description="The entire title for the slide. Use <br> for line breaks and <span class='highlight'>word</span> to highlight a specific word. Default: 'THIS IS YOUR<br><span class=\'highlight\'>PRESENTATION</span><br>TITLE'.")
    font_family: str = Field(default="'Montserrat', 'Inter', sans-serif", description="The font family for all text elements.")
    accent_color: str = Field(default="#06B6D4", description="The primary accent color for the right panel and the highlighted word.")
    shadow_color: str = Field(default="#0E7490", description="The secondary (darker) accent color for the panel behind.")
    text_color: str = Field(default="#6B7280", description="The primary color for the non-highlighted text.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small icon above the title.")

class GenerateDynamicIntroSlideInput(BaseModel):
    """Input schema for generate_dynamic_intro_slide."""
    main_title: str = Field(..., description="The large, bold title for the slide. Default: 'Innovate. Create. Inspire.'.")
    subtitle: str = Field(..., description="The smaller subtitle text below the main title. Default: 'This is where we outline our core mission and the driving force behind our vision.'.")
    image_url: str = Field(default="https://images.unsplash.com/photo-1521737711867-e3b97375f902?q=80&w=1887&auto=format&fit=crop", description="URL for the full-height image on the right.")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="Font family for all text elements.")
    primary_color: str = Field(default="#4F46E5", description="The primary (brighter) color for the main part of the text block.")
    secondary_color: str = Field(default="#3730A3", description="The secondary (darker) color for the footer area of the text block.")
    text_color: str = Field(default="#FFFFFF", description="The color for the text.")

class GenerateBigConceptSlideInput(BaseModel):
    """Input schema for generate_big_concept_slide."""
    main_title: str = Field(..., description="The main, large title for the concept. Use <br> for line breaks. Default: 'BIG<br>CONCEPT'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Bring the attention of your audience over a key concept using icons or illustrations'.")
    icon_name: str = Field(..., description="Selects a pre-designed illustration scene to display. Default: 'space'.")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The main color for all text elements.")

class GenerateElegantAgendaSlideInput(BaseModel):
    """Input schema for generate_elegant_agenda_slide."""
    main_title: str = Field(..., description="The main title of the slide, typically using an elegant serif font. Default: 'Bài thuyết trình hôm nay'.")
    subtitle: str = Field(..., description="A small, uppercase subtitle to introduce the list. Default: 'CHỦ ĐỀ CHÍNH'.")
    agenda_items: List[str] = Field(..., description="""A list of strings representing the agenda points. Defualt: [
        "Về công ty chúng tôi",
        "Dịch vụ mạng xã hội",
        "Vấn đề/Cơ hội",
        "Giải pháp của chúng tôi",
        "Thực hiện kế hoạch",
        "Đội ngũ của chúng tôi"
    ]""")
    image_url: str = Field(default="A high-quality Unsplash image", description="URL of the image to be displayed on the left. A professional desk photo is recommended. Default: A high-quality Unsplash image.")
    accent_color: str = Field(default="#EAD6D6", description="The color of the decorative rectangle behind the image (hex code).")
    bg_color: str = Field(default="#FCFCFC", description="The main background color of the slide (hex code).")
    title_color: str = Field(default="#1F2937", description="Color for the main title (hex code).")
    subtitle_color: str = Field(default="#B48E8E", description="Color for the subtitle text (hex code).")
    text_color: str = Field(default="#4B5563", description="Color for the agenda list items (hex code).")
    font_family_title: str = Field(default="Playfair Display", description="The font family for the main title. An elegant serif font is recommended.")
    font_family_body: str = Field(default="Montserrat", description="The font family for all other text. A clean sans-serif is recommended.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

class GeneratePlayfulTitleSlideInput(BaseModel):
    """Input schema for generate_playful_title_slide."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks. Default: 'Introduction<br>to penguins'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Introduce penguins here. Mention their characteristics and unique behaviors.'.")
    illustration_character: str = Field(default="penguin", description="Selects a pre-drawn character illustration.")
    font_family_title: str = Field(default="'Patrick Hand', 'Inter', cursive", description="The handwritten-style font for the main title.")
    font_family_body: str = Field(default="'Lato', 'Inter', sans-serif", description="The clean sans-serif font for the subtitle.")
    top_bg_color: str = Field(default="#FFC947", description="The main background color (yellow).")
    bottom_bg_color: str = Field(default="#E8715D", description="The color of the strip at the bottom.")
    text_color: str = Field(default="#2D2D2D", description="The color for all text.")
    doodle_color: str = Field(default="#89CFF0", description="The color for the small decorative squiggles and stars.")

class GenerateMinimalistTitleSlideInput(BaseModel):
    """Input schema for generate_minimalist_title_slide."""
    main_title: str = Field(..., description="The main, large presentation title. Default: 'This is your presentation title'.")
    subtitle: str = Field(..., description="A smaller subtitle to provide more context or a tagline. Default: 'A subtitle to provide more context or a tagline'.")
    author_line: str = Field(..., description="A line for the presenter's name or company, displayed at the bottom. Default: 'Presented by Your Name / Company'.")
    font_family: str = Field(default="'Inter', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#111827", description="The dark background color of the slide.")
    text_color: str = Field(default="#F9FAFB", description="The color for the main title text.")
    subtitle_color: str = Field(default="#E5E7EB", description="The color for the subtitle and author line.")
    accent_color: str = Field(default="#38BDF8", description="The vibrant color for the glowing, animated portal.")

class GenerateMissionSlideInput(BaseModel):
    """Input schema for generate_mission_slide."""
    top_text: str = Field(..., description="A small heading displayed above the main title (e.g., 'Our Purpose', 'Core Philosophy'). Default: 'Subheading or Category'.")
    title: str = Field(..., description="The main, concise title of the slide. Default: 'Your Main Title Here'.")
    subtitle: str = Field(..., description="The main descriptive text, displayed in a larger, prominent area below the title. Default: 'Elaborate on your key message or provide a call to action. This text can be a bit longer.'.")
    image_url: str = Field(default="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?q=80&w=2084&auto=format&fit=crop", description="URL of the image to be displayed in the right column.")
    image_alt_text: str = Field(default="A team collaborating in a modern office, representing mission and goals", description="Alternative text for the image, for accessibility.")
    font_family: str = Field(default="'Inter', sans-serif", description="Font family for all text elements.")
    background_color_left: str = Field(default="#F5EBE0", description="Background color for the top content area in the left column (warm beige).")
    text_color_title: str = Field(default="#4E443F", description="Text color for the main title (dark brown).")
    text_color_top: str = Field(default="#4E443F", description="Text color for the top subheading (dark brown).")
    text_color_subtitle: str = Field(default="#475569", description="Text color for the main description/subtitle (neutral gray).")
    slide_background_color: str = Field(default="#FDFCFB", description="Overall background color for the entire slide (off-white/cream).")

class GenerateTrainingIntroSlideInput(BaseModel):
    """Input schema for generate_training_intro_slide."""
    main_title: str = Field(..., description="Main title text (e.g., 'Introduction'). Default: 'Introduction'.")
    description_text: str = Field(..., description="Description or explanation text below title. Default: 'Briefly introduce yourself and explain the purpose of your training presentation.'")
    bg_color: str = Field(default="#3a3a3a", description="Background color for the slide (hex code). Default: '#3a3a3a' (dark gray).")
    title_color: str = Field(default="#b8d89f", description="Color for the main title (hex code). Default: '#b8d89f' (light green).")
    text_color: str = Field(default="#e8d7a8", description="Color for the description text (hex code). Default: '#e8d7a8' (light yellow).")
    image_url: str = Field(default="https://images.pexels.com/photos/3587620/pexels-photo-3587620.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", description="URL of the image to display in bottom section.")
    font_family: str = Field(default="'Segoe UI', 'Arial', sans-serif", description="Font family for all text elements.")

class GenerateBusinessIntroSlideInput(BaseModel):
    """Input schema for generate_business_intro_slide."""
    main_title: str = Field(..., description="Large main title text , default='PRESENTATION'")
    subtitle: str = Field(..., description="Description text below main title.  default='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore'")
    main_title_color: str = Field(default="#0056d2", description="Color for main title (default: blue).")
    subtitle_color: str = Field(default="#666666", description="Color for subtitle text.")
    accent_color: str = Field(default="#0056d2", description="Color for decorative D-shapes on sides.")
    main_font: str = Field(default="Arial, sans-serif", description="Font family for main title.")
    subtitle_font: str = Field(default="Arial, sans-serif", description="Font family for subtitle.")

class GenerateTitleSlide3Input(BaseModel):
    """Input schema for generate_title_slide_3."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks. Default: 'Christmas Lights<br>Minitheme'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Here is where your presentation begins'.")
    bg_color: str = Field(default="#F5EBE0", description="The background color of the slide.")
    text_color: str = Field(default="#C41E3A", description="The color for the main title text.")
    subtitle_color: str = Field(default="#3D3D3D", description="The color for the subtitle text.")
    font_family: str = Field(default="'Lobster Two', 'Georgia', serif", description="The font family for all text elements.")
    show_top_lights: Optional[bool] = Field(default=True, description="Whether to show the Christmas lights at the top. Default: True.")
    show_sparkles: Optional[bool] = Field(default=True, description="Whether to show decorative sparkles on the slide. Default: True.")
    custom_css: str = Field(default="", description="Additional custom CSS to be included.")
    
class GenerateMinimalistSlideInput(BaseModel):
    """Input schema for generate_minimalist_slide."""
    title: str = Field(..., description="The main title for the slide. Default: 'Minimalist Business Slides'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Here is where your presentation begins'.")
    font_family_title: str = Field(default="Playfair Display, Georgia, serif", description="The font family for the title text.")
    font_family_subtitle: str = Field(default="Inter, sans-serif", description="The font family for the subtitle text.")
    background_color: str = Field(default="#E8E3DC", description="The background color of the slide.")
    text_color_title: str = Field(default="#1A1A1A", description="The color for the title text.")
    text_color_subtitle: str = Field(default="#4A4A4A", description="The color for the subtitle text.")
    line_color: str = Field(default="#2C2C2C", description="The color for the decorative lines.")
    curve_color: str = Field(default="#4A4A4A", description="The color for the decorative curves.")
    
class GenerateTitleSlide4Input(BaseModel):
    """Input schema for generate_title_slide_4."""
    title: str = Field(..., description="The main title for the slide. Use <br> for line breaks. Default: 'Your Presentation Title'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Your subtitle goes here'.")
    font_family: str = Field(default="Inter, system-ui, -apple-system, sans-serif", description="The font family for all text elements.")
    background_color: str = Field(default="#E8E3DC", description="The background color of the slide (warm beige/cream).")
    text_color: str = Field(default="#1A1A1A", description="The color for all text elements.")
    accent_color_1: str = Field(default="#E85D75", description="First accent color for decorative shapes (coral red).")
    accent_color_2: str = Field(default="#D8B4E2", description="Second accent color for decorative shapes (lavender).")
    
class GenerateTitleSlide5Input(BaseModel):
    """Input schema for generate_title_slide_5."""
    top_left_text: str = Field(default="Our shared moments", description="Text displayed in the top-left corner of the slide.")
    year: str = Field(default="20XX", description="Year displayed in the top-right corner of the slide.")
    main_title: str = Field(default="Your Title Here", description="The main title text for the notebook cover design.")
    bottom_text: str = Field(default="Here is where your presentation begins", description="Text displayed at the bottom-right of the slide.")
    image_path: str = Field(default="Image/generate_title_slide_5/Default_1.jpg", description="Path to the image displayed in the polaroid frame.")
    font_family: str = Field(default="'Arial'", description="Font family for all text elements on the slide.")
    font_family_secondary: str = Field(default="'Arial'", description="Font family for secondary text elements.")
    bg_color: str = Field(default="#b8c8d4", description="Background color of the slide in hex format.")
    text_color: str = Field(default="#2c3e50", description="Color of all text elements in hex format.")
    show_clover: bool = Field(default=True, description="Whether to display the four-leaf clover decoration.")
    show_decorative_lines: bool = Field(default=True, description="Whether to display decorative horizontal lines.")
    custom_css: str = Field(default="", description="Additional custom CSS to be included in the slide.")
    
class GenerateTitleSlide6Input(BaseModel):
    """Input schema for generate_title_slide_6."""
    main_title: str = Field(default="Your main title here", description="Main title text displayed prominently in the center of the content box.")
    subtitle: str = Field(default="- Your subtitle here -", description="Subtitle text displayed below the main title.")
    bg_color: str = Field(default="#E8D4F0", description="Background gradient start color in hex format.")
    bg_gradient_to: str = Field(default="#F0E4F8", description="Background gradient end color in hex format.")
    box_color: str = Field(default="#D4E8B4", description="Color of the central content box in hex format.")
    title_color: str = Field(default="#2D3436", description="Color of the title and subtitle text in hex format.")
    font_family: str = Field(default="Arial, monospace", description="Font family for title and subtitle text.")
    show_clouds: bool = Field(default=True, description="Whether to display cloud decorations at the top of the slide.")
    show_flower: bool = Field(default=True, description="Whether to display the cute flower character at the bottom-left corner.")
    custom_css: str = Field(default="", description="Additional custom CSS to be included in the slide.")
# === SLIDE CHUYỂN SLIDE CLASSES ===

class GenerateGeometricTransitionSlideInput(BaseModel):
    """Input schema for generate_geometric_transition_slide."""
    headline: str = Field(..., description="The main, uppercase headline for the transition. Default: 'TRANSITION HEADLINE'.")
    subtitle: str = Field(..., description="The smaller subtitle text displayed below the headline. Default: 'Let's start with the first set of slides'.")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    primary_text_color: str = Field(default="#FFFFFF", description="The color for the section number and the main headline.")
    subtitle_color: str = Field(default="#67E8F9", description="The accent color for the subtitle text.")

class GenerateDuskTransitionSlideInput(BaseModel):
    """Input schema for generate_dusk_transition_slide."""
    headline: str = Field(..., description="The main headline for the transition. Default: 'Transition Headline'.")
    subtitle: str = Field(..., description="The smaller subtitle text below the headline. Default: 'Let's start with the first set of slides'.")
    font_family: str = Field(default="'Nunito', sans-serif", description="The font family for all text elements.")
    headline_color: str = Field(default="#2C3E50", description="The color for the main headline text.")
    subtitle_color: str = Field(default="#4A5568", description="The color for the subtitle text.")
    number_color: str = Field(default="#FDE68A", description="The accent color for the section number.")
    sky_top_color: str = Field(default="#6B4F9B", description="The color for the top of the sky gradient (purple).")
    sky_mid_color: str = Field(default="#C07CB6", description="The color for the middle of the sky gradient (pink).")
    sky_bottom_color: str = Field(default="#F6B17B", description="The color for the bottom of the sky gradient (orange).")
    grid_dot_color: str = Field(default="rgba(255, 255, 255, 0.3)", description="The color and opacity for the dots in the background grid.")

class GenerateMemphisTransitionSlideInput(BaseModel):
    """Input schema for generate_memphis_transition_slide."""
    section_number: str = Field(default="1.", description="The number for the new section (e.g., '1.', '02').")
    headline: str = Field(..., description="The main headline for the transition. Default: 'Transition headline'.")
    subtitle: str = Field(..., description="The smaller subtitle text below the headline. Default: 'Let's start with the first set of slides'.")
    font_family_headline: str = Field(default="'Lora', 'Inter', serif", description="The elegant, serif font for the main headline and number.")
    font_family_body: str = Field(default="'Lato', 'Inter', sans-serif", description="The clean, sans-serif font for the subtitle.")
    top_panel_bg: str = Field(default="#19114B", description="The background color for the top half of the slide.")
    bottom_panel_bg: str = Field(default="#403271", description="The background color for the bottom half of the slide.")
    palette: List[str] = Field(default=["#F87171", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"], description="A list of 5 colors used for the various decorative shapes and accents. [0: Red/Magenta, 1: Orange/Yellow, 2: Purple, 3: Blue, 4: Green/Teal]")

class GeneratePushpinSectionHeaderInput(BaseModel):
    """Input schema for generate_pushpin_section_header."""
    main_title: str = Field(..., description="The main text for the section header. It will be displayed in large, uppercase letters. Default: 'Add a Section Header'.")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="The font family for the title.")
    bg_color: str = Field(default="#FDFCFB", description="The background color of the slide, with a subtle paper texture overlay.")
    text_color: str = Field(default="#1F2937", description="The color for the main title text.")
    accent_color: str = Field(default="#1F2937", description="The color for the horizontal divider line and the two flanking dots.")

class GenerateSectionHeaderSlideInput(BaseModel):
    """Input schema for generate_section_header_slide."""
    header_text: str = Field(..., description="The main, large text for the section header. Default: 'Add a Section Header'.")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="Font family for the header text.")
    bg_color: str = Field(default="#F8FAFC", description="The main background color of the slide (typically a very light off-white).")
    text_color: str = Field(default="#1E293B", description="The color for the header text.")
    gradient_color_1: str = Field(default="#A78BFA", description="The first color for the soft aurora gradient background (e.g., light purple).")
    gradient_color_2: str = Field(default="#F472B6", description="The second color for the soft aurora gradient background (e.g., pink).")
    gradient_color_3: str = Field(default="#7DD3FC", description="The third color for the soft aurora gradient background (e.g., light blue).")

class GenerateResearchProposalTransitionSlideInput(BaseModel):
    """Input schema for generate_research_proposal_transition_slide."""
    headline: str = Field(..., description="Main headline text for the transition. Default: 'TRANSITION HEADLINE'.")
    subtitle: str = Field(..., description="Subtitle/description text below the headline. Default: 'Let's start with the first set of slides'.")
    bg_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    accent_color: str = Field(default="#C4A57B", description="Color for decorative elements (geometric shapes, grid, bar).")
    number_color: str = Field(default="#C4A57B", description="Color for section number (if used).")
    headline_color: str = Field(default="#000000", description="Color for the main headline text.")
    subtitle_color: str = Field(default="#9B8B6F", description="Color for the subtitle text.")
    left_bar_width: str = Field(default="60", description="Width of left decorative bar in pixels.")

class GenerateBusinessTransitionSlideInput(BaseModel):
    """Input schema for generate_business_transition_slide."""
    headline: str = Field(..., description="Main transition headline  Default: 'TRANSITION'.")
    subtitle: str = Field(..., description="Subtitle text below headline. Default: 'Let's start with the first set of slides'.")
    headline_color: str = Field(default="#0056d2", description="Color for headline (default: blue).")
    subtitle_color: str = Field(default="#666666", description="Color for subtitle text.")
    accent_color: str = Field(default="#0056d2", description="Color for decorative D-shapes on sides.")
    headline_font: str = Field(default="Arial, sans-serif", description="Font family for headline.")
    subtitle_font: str = Field(default="Arial, sans-serif", description="Font family for subtitle.")

class GenerateIntroSlideInput(BaseModel):
    """Input schema for generate_intro_slide."""
    main_title: str = Field(..., description="Main title text. Default: 'Main Title'.")
    subtitle1: str = Field(..., description="First subtitle text. Default: 'Subtitle1'.")
    subtitle2: str = Field(..., description="Second subtitle text. Default: 'Subtitle2'.")
    main_bg_color: str = Field(default="#ffffff", description="CSS main background color for the slide.")
    accent_bg_color: str = Field(default="#6ea88a", description="CSS background color for the right section.")
    text_box_bg_color: str = Field(default="#c5e6b8", description="CSS background color for the text box.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#555555", description="CSS color for the subtitles.")
    line_color: str = Field(default="#e6c35c", description="CSS color for the horizontal divider line.")
    font_family: str = Field(default="'Inter', sans-serif", description="CSS font family for the slide.")
    main_title_font_style: str = Field(default="italic", description="CSS font style for the main title.")
    image_url: str = Field(default="Image/generate_intro_slide1/Default_1.png", description="URL or path to the image displayed on the slide.")

class GenerateEmployeeIntroSlideInput(BaseModel):
    """Input schema for generate_employee_intro_slide."""
    main_title: str = Field(..., description="Main slide title displayed prominently. Default: 'Employee Transition Plan'.")
    subtitle: str = Field(..., description="Descriptive text below the main title explaining the slide purpose. Default: 'Use the following infographics to outline how your team or company will manage responsibilities and workflow during employee movement.'.")
    bg_color: str = Field(default="#0d4d3d", description="Background color (hex code). Default: dark green (#0d4d3d).")
    title_color: str = Field(default="#FFFFFF", description="Color for the main title text (hex code). Default: white.")
    subtitle_color: str = Field(default="#FFFFFF", description="Color for the subtitle text (hex code). Default: white.")
    circle_color_1: str = Field(default="#0a3d2f", description="First decorative circle color - darkest green (hex code). Default: #0a3d2f.")
    circle_color_2: str = Field(default="#10855b", description="Second decorative circle color - medium green (hex code). Default: #10855b.")
    circle_color_3: str = Field(default="#2dd4bf", description="Third decorative circle color - light cyan (hex code). Default: #2dd4bf.")
    circle_color_4: str = Field(default="#FFFFFF", description="Fourth decorative circle color - white (hex code). Default: #FFFFFF.")
    font_family: str = Field(default="'Inter', sans-serif", description="Font family for all text elements on the slide.")

class GenerateResearchProposalSlideInput(BaseModel):
    """Input schema for generate_research_proposal_slide."""
    title: str = Field(..., description="The main title text for the slide. Default: 'Research Proposal Presentation'.")
    subtitle: str = Field(..., description="The subtitle text displayed below the main title. Default: 'PRODUCT RESEARCH PROPOSAL FOR INGOUDE COMPANY'.")
    bg_color: str = Field(default="#FFFFFF", description="Background color . Default: '#FFFFFF'.")
    accent_color: str = Field(default="#C4A57B", description="Color for decorative elements . Default: '#C4A57B'.")
    title_color: str = Field(default="#000000", description="Color for the main title . Default: '#000000'.")
    subtitle_color: str = Field(default="#9B8B6F", description="Color for the subtitle . Default: '#9B8B6F'.")
    left_bar_width: str = Field(default="60", description="Width of left decorative bar in pixels. Default: '60'.")

class GenerateCompanyMissionSlideInput(BaseModel):
    """Input schema for generate_company_mission_slide."""
    main_title: str = Field(..., description="Main title text displayed in the left section. Default: 'OUR COMPANY OUR COMPANY OUR COMPANY OUR COMPANY'.")
    mission_items: List[str] = Field(..., description="""List of mission item texts (4-7 items recommended). default=[
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore"
    ]""")
    title_color: str = Field(default="#000000", description="Color for main title . default='#000000'")
    subtitle_color: str = Field(default="#0052CC", description="Color for subtitle . default='#0052CC'")
    panel_bg_color: str = Field(default="#0052CC", description="Background color for right mission panel . default='#0052CC'")
    panel_text_color: str = Field(default="#FFFFFF", description="Text color inside mission panel . default='#FFFFFF'")
    number_bg_color: str = Field(default="#E8E8E8", description="Background color for number circles . default='#E8E8E8'")
    number_text_color: str = Field(default="#000000", description="Text color for numbers in circles . default='#000000'")
    accent_bar_color: str = Field(default="#0052CC", description="Color for bottom accent bar in left section (hex code). default='#0052CC'")
    bg_color: str = Field(default="#F5F5F5", description="Background color for the slide (hex code). default='#F5F5F5'")

class GenerateSectionHeaderSlide5Input(BaseModel):
    """Input schema for generate_section_header_slide_5."""
    section_title: str = Field(..., description="Main section title. Default: 'THIS IS THE TITLE OF THIS SECTION'.")
    bg_color: str = Field(default="#1a3d4a", description="Background color (default: dark teal).")
    text_color: str = Field(default="#ffffff", description="Text color (default: white).")
    stripe_color: str = Field(default="#2a5566", description="Color of decorative stripes (default: medium teal).")
    custom_css: str = Field(default="", description="Additional CSS to inject.")

class GenerateSectionHeaderSlide6Input(BaseModel):
    """Input schema for generate_section_header_slide_6."""
    title: str = Field(..., description="Main heading text for the slide.")
    description: str = Field(..., description="Supporting text displayed below the title and underline.")
    bg_color: str = Field(default="#ffffff", description="Starting color of the background gradient (top).")
    bg_gradient_to: str = Field(default="#e3f2fd", description="Ending color of the background gradient (bottom).")
    title_color: str = Field(default="#1a1a1a", description="Color of the main title text.")
    text_color: str = Field(default="#4a4a4a", description="Color of the description text.")
    underline_color: str = Field(default="#1a1a1a", description="Color of the decorative underline.")
    custom_css: str = Field(default="", description="Additional CSS rules to inject into the style block.")


class GenerateSectionHeaderSlide8Input(BaseModel):
    """Input schema for generate_section_header_slide_8."""
    main_title: str = Field(..., description="Main title text for the slide.")
    subtitle: str = Field(..., description="Subtitle text displayed below the title.")
    bg_color: str = Field(default="#FFB84D", description="Background color of the slide (warm peach/orange).")
    text_color: str = Field(default="#2C2C2C", description="Color of the main title text (dark gray).")
    subtitle_color: str = Field(default="#4A4A4A", description="Color of the subtitle text (medium gray).")
    custom_css: str = Field(default="", description="Additional CSS rules to inject into the style block.")
  
class GenerateSectionHeaderSlide9Input(BaseModel):
    """Input schema for generate_section_header_slide_9."""
    main_title: str = Field(..., description="Main title text for the slide. default='SECTION TITLE HERE'.")
    subtitle: str = Field(default="Here you could describe the topic of the section", description="Subtitle text displayed below the title.")
    bg_gradient_from: str = Field(default="#fef5e7", description="Starting gradient color (light cream).")
    bg_gradient_to: str = Field(default="#d4a574", description="Ending gradient color (warm brown).")
    text_color: str = Field(default="#ffffff", description="Color of all text elements.")
    custom_css: str = Field(default="", description="Additional CSS rules to inject into the style block.")

class GenerateSectionHeaderSlide10Input(BaseModel):
    """Input schema for generate_section_header_slide_10."""
    main_title: str = Field(..., description="Main title text for the slide. default='SECTION TITLE HERE'.")
    subtitle: str = Field(..., description="Subtitle text displayed below the title.")
    bg_color: str = Field(default="#9BD89B", description="Background color (light green).")
    notebook_bg: str = Field(default="#FFFFFF", description="Notebook paper background color.")
    title_color: str = Field(default="#A84A3A", description="Color of the main title (brown/red).")
    subtitle_color: str = Field(default="#5A5A5A", description="Color of the subtitle text (gray).")
    sticky_note_colors: list = Field(default=["#FFD966", "#FFB3B3"], description="List of colors for bookmark sticky notes at the top (yellow and pink).")
    custom_css: str = Field(default="", description="Additional CSS rules to inject into the style block.")

class GenerateSectionHeaderSlide12Input(BaseModel):
    """Input schema for generate_section_header_slide_12."""
    main_title: str = Field(..., description="Main title text (question) to display. default='WHAT IS THE MAIN <br> TOPIC OF THIS SECTION?'.")
    bg_color: str = Field(default="#f5f5f5", description="Background color of the slide (light gray).")
    title_color: str = Field(default="#2d3748", description="Color of the main title text (dark gray).")
    custom_css: str = Field(default="", description="Additional custom CSS.")

class GenerateSectionHeaderSlide13Input(BaseModel):
    """Input schema for generate_section_header_slide_13."""
    main_title: str = Field(..., description="Main title text for the slide.")
    subtitle: str = Field(..., description="Subtitle text displayed below the title.")
    bg_start_color: str = Field(default="#FFFFFF", description="Starting gradient color (white/left side).")
    bg_end_color: str = Field(default="#C8F4F0", description="Ending gradient color (light cyan/right side).")
    accent_gradient_color: str = Field(default="#FFB366", description="Accent gradient color for the bottom left corner (peach/orange).")
    text_color: str = Field(default="#1A1A1A", description="Color of all text elements (dark gray).")
    custom_css: str = Field(default="", description="Additional CSS rules to inject into the style block.")


class GenerateSectionHeaderSlide15Input(BaseModel):
    """Input schema for generate_section_header_slide_15."""
    main_title: str = Field(..., description="Main title text for the slide. default='MERRY CHRISTMAS AND HAPPY NEW YEAR!'.")
    bg_color: str = Field(default="#0f2f1f", description="Background color (default: dark evergreen green for Christmas theme).")
    text_color: str = Field(default="#f8f8f8", description="Text color (default: bright white).")
    blob1_color: str = Field(default="rgba(220, 38, 38, 0.5)", description="First gradient blob color (default: Christmas red).")
    blob2_color: str = Field(default="rgba(34, 139, 34, 0.5)", description="Second gradient blob color (default: forest green).")
    blob3_color: str = Field(default="rgba(218, 165, 32, 0.4)", description="Third gradient blob color (default: golden yellow).")
    custom_css: str = Field(default="", description="Additional CSS rules to inject into the style block.")


# === SLIDE CONTENT CLASSES ===

class GenerateContentSlideInput(BaseModel):
    """Input schema for generate_content_slide."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'CONTENT'.")
    items: List[str] = Field(..., description="List of item titles for the grid. Default: ['Your Title Here', ...] (6 items).")
    main_title_color: str = Field(default="#555555", description="CSS color for the main title.")
    number_color: str = Field(default="#a2c4c9", description="CSS color for item numbers.")
    item_title_color: str = Field(default="#555555", description="CSS color for item titles.")
    background_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#a2c4c9", description="CSS color for corner accents.")
    border_width: str = Field(default="30px", description="CSS width of the slide border.")
    font_family: str = Field(default="Arial, sans-serif", description="CSS font family for the slide.")
    num_columns: int  = Field(default=3, description="Number of columns in the grid. Default: 3.")
    num_rows: int  = Field(default=2, description="Number of rows in the grid. Default: 2.")

class GenerateComparisonSlideInput(BaseModel):
    """Input schema for generate_comparison_slide."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'Your Title Here'.")
    left_title: str = Field(..., description="Title for the left column. Default: 'Your Title Here'.")
    right_title: str = Field(..., description="Title for the right column. Default: 'Your Title Here'.")
    left_text: str = Field(..., description="Text content for the left column. Default: placeholder text.")
    right_text: str = Field(..., description="Text content for the right column. Default: placeholder text.")
    left_icon: str = Field(default="gavel", description="Icon for the left column ('gavel' or 'custom').")
    right_icon: str = Field(default="scales", description="Icon for the right column ('scales' or 'custom').")
    custom_left_icon: str = Field(default="''", description="Custom SVG code for left icon if 'custom'.")
    custom_right_icon: str = Field(default="''", description="Custom SVG code for right icon if 'custom'.")
    title_color: str = Field(default="#555555", description="CSS color for all titles.")
    text_color: str = Field(default="#555555", description="CSS color for text content.")
    icon_color: str = Field(default="#a2c4c9", description="CSS color for icons.")
    background_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#a2c4c9", description="CSS color for corner accents.")
    divider_color: str = Field(default="#555555", description="CSS color for the divider line.")
    font_family: str = Field(default="Arial, sans-serif", description="CSS font family for the slide.")

class GenerateProcessSlideInput(BaseModel):
    """Input schema for generate_process_slide."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'Your Title Here'.")
    left_title: str = Field(..., description="Title for the left box. Default: 'Your Title Here'.")
    right_title: str = Field(..., description="Title for the right box. Default: 'Your Title Here'.")
    left_content: str = Field(..., description="Content text for the left box. Default: placeholder text.")
    right_content: str = Field(..., description="Content text for the right box. Default: placeholder text.")
    title_color: str = Field(default="#555555", description="CSS color for the main title.")
    left_box_color: str = Field(default="#8cbeca", description="CSS background color for the left box.")
    right_box_color: str = Field(default="#c5e1e8", description="CSS background color for the right box.")
    text_color: str = Field(default="#ffffff", description="CSS color for text in the boxes.")
    arrow_color: str = Field(default="#f0f0f0", description="CSS color for the arrow connecting boxes.")
    background_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#a2c4c9", description="CSS color for corner accents.")
    border_width: str = Field(default="30px", description="CSS width of the slide border.")
    font_family: str = Field(default="Arial, sans-serif", description="CSS font family for the slide.")
    box_width: str = Field(default="380px", description="CSS width of each box.")
    box_height: str = Field(default="350px", description="CSS height of each box.")
    box_border_radius: str = Field(default="5px", description="CSS border radius for the boxes.")

class GenerateProcessStepsSlideInput(BaseModel):
    """Input schema for generate_process_steps_slide."""
    main_title: str = Field(..., description="The main title displayed in the left-hand colored panel. Default: 'Cách tiếp cận đề xuất'.")
    steps: List[Dict] = Field(..., description=f"""A list of step objects, each containing an image URL, a title, and a description. Default: [
        {{
            "image_url": "https://images.unsplash.com/photo-1516321497487-e288fb19713f?q=80&w=2940&auto=format&fit=crop",
            "title": "Thiết lập nền tảng số",
            "description": "Thuyết trình là công cụ giao tiếp có thể dùng để giảng dạy."
        }},
        {{
            "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
            "title": "Ra mắt các chiến dịch số",
            "description": "Thuyết trình là công cụ giao tiếp có thể dùng để giảng dạy."
        }},
        {{
            "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=2940&auto=format&fit=crop",
            "title": "Theo dõi kết quả",
            "description": "Thuyết trình là công cụ giao tiếp có thể dùng để giảng dạy."
        }}
    ]""")
    accent_color: str = Field(default="#EAD6D6", description="The color of the left title panel (hex code).")
    bg_color: str = Field(default="#FCFCFC", description="The main background color of the slide (hex code).")
    title_color: str = Field(default="#1F2937", description="Color for the main title in the left panel.")
    text_heading_color: str = Field(default="#374151", description="Color for the title of each step.")
    text_body_color: str = Field(default="#6B7280", description="Color for the description text of each step.")
    font_family_title: str = Field(default="'Playfair Display', 'Inter', serif", description="The font for the main title. An elegant serif font is recommended.")
    font_family_body: str = Field(default="'Montserrat', 'Inter', sans-serif", description="The font for all other text. A clean sans-serif is recommended.")
    custom_css: str = Field(default="", description="Additional custom CSS.")

class GenerateIconListSlide2Input(BaseModel):
    """Input schema for generate_icon_list_slide_2."""
    main_title: str = Field(..., description="The main title of the slide, typically using an elegant serif font. Default: 'Giải pháp'.")
    subtitle: str = Field(..., description="A smaller, uppercase subtitle below the main title. Default: 'CÁCH TIẾP CẬN ĐA KÊNH'.")
    items: List[str] = Field(..., description="A list of items, each with the raw SVG code for the icon and the corresponding text. Default: 3 items with network/phone/wifi icons and Vietnamese text.")
    accent_color: str = Field(default="#EAD6D6", description="The background color for the icon containers (hex code).")
    bg_color: str = Field(default="#FCFCFC", description="The main background color of the slide (hex code).")
    title_color: str = Field(default="#1F2937", description="Color for the main title.")
    subtitle_color: str = Field(default="#4B5563", description="Color for the subtitle.")
    text_color: str = Field(default="#374151", description="Color for the item text.")
    icon_color: str = Field(default="#FFFFFF", description="Fill color for the SVG icons inside the containers.")
    font_family_title: str = Field(default="'Playfair Display', 'Inter', serif", description="The font for the main title. An elegant serif font is recommended.")
    font_family_body: str = Field(default="'Montserrat', 'Inter', sans-serif", description="The font for all other text. A clean sans-serif is recommended.")
    custom_css: str = Field(default="", description="Additional custom CSS.")

class GenerateImageCutoutListSlideInput(BaseModel):
    """Input schema for generate_image_cutout_list_slide."""
    list_items: List[str] = Field(...,description=f"""A list of items to display, each with a 'title' (main point) and a 'description' (elaboration). default=[ {{"title": "Add a main point", "description": "Elaborate on what you want to discuss."}},{{"title": "Add a main point", "description": "Elaborate on what you want to discuss."}},{{"title": "Add a main point", "description": "Elaborate on what you want to discuss."}},{{"title": "Add a main point", "description": "Elaborate on what you want to discuss."}}]""")
    background_image_url: str = Field(default="https://images.unsplash.com/photo-1541746972996-4e0b0f43e02a?q=80&w=2940&auto=format&fit=crop", description="URL for the single, continuous background image that spans the entire slide. An atmospheric or abstract office photo is recommended.")
    content_bg_color: str = Field(default="#1A1A22", description="Background color for the main content panel that sits on top of the image.")
    text_heading_color: str = Field(default="#FFFFFF", description="Color for the main heading of each list item.")
    text_color: str = Field(default="#C0C0C0", description="Color for the secondary text (description).")
    accent_color: str = Field(default="#8A63D2", description="The accent color for the bullet points and decorative spinner.")
    line_color: str = Field(default="rgba(255, 255, 255, 0.2)", description="The color of the vertical guide line.")
    font_family_title: str = Field(default="'Source Serif 4', serif", description="The font family for item titles. A serif font is recommended.")
    font_family_body: str = Field(default="'Inter', sans-serif", description="The font family for item descriptions. A clean sans-serif is recommended.")
    custom_css: str = Field(default="", description="Additional custom CSS.")

class GenerateBodySlide2Input(BaseModel):
    """Input schema for generate_body_slide2."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'MainTitle'.")
    subtitle1: str = Field(..., description="Subtitle for the first content section. Default: 'SubTitle1'.")
    content1: str = Field(..., description="Content text for the first section. Default: 'Content1'.")
    subtitle2: str = Field(..., description="Subtitle for the second content section. Default: 'SubTitle2'.")
    content2: str = Field(..., description="Content text for the second section. Default: 'Content2'.")
    subtitle3: str = Field(..., description="Subtitle for the third content section. Default: 'SubTitle3'.")
    content3: str = Field(..., description="Content text for the third section. Default: 'Content3'.")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accents and icon backgrounds.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#333333", description="CSS color for subtitles.")
    content_color: str = Field(default="#555555", description="CSS color for content text.")
    font_family: str = Field(default="'Inter', sans-serif", description="CSS font family for the slide.")
    image_url: str = Field(default="Image/generate_body_slide2/Default_1.png", description="Path to the image file for the left side.")
    icon1: str = Field(default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M12 2v6M12 18v4M14.5 8a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0zM16.5 13a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0z"></path></svg>', description="SVG code for the first section's icon.")
    icon2: str = Field(default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>', description="SVG code for the second section's icon.")
    icon3: str = Field(default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>', description="SVG code for the third section's icon.")


class GenerateBodySlide4Input(BaseModel):
    """Input schema for generate_body_slide4."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'MainTitle'.")
    main_content: str = Field(..., description="Content text for the horizontal bar. Default: 'Content'.")
    subtitle1: str = Field(..., description="Subtitle for the first image. Default: 'Subtitle1'.")
    content1: str = Field(..., description="Content text for the first image. Default: 'Content1'.")
    subtitle2: str = Field(..., description="Subtitle for the second image. Default: 'Subtitle2'.")
    content2: str = Field(..., description="Content text for the second image. Default: 'Content2'.")
    subtitle3: str = Field(..., description="Subtitle for the third image. Default: 'Subtitle3'.")
    content3: str = Field(..., description="Content text for the third image. Default: 'Content3'.")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accents and borders.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    content_color: str = Field(default="#555555", description="CSS color for content text.")
    subtitle_color: str = Field(default="#333333", description="CSS color for subtitles.")
    font_family: str = Field(default="'Inter', sans-serif", description="CSS font family for the slide.")
    image_url_1: str = Field(default="Image/generate_body_slide4/Default_1.png", description="Path to the first image file.")
    image_url_2: str = Field(default="Image/generate_body_slide4/Default_2.png", description="Path to the second image file.")
    image_url_3: str = Field(default="Image/generate_body_slide4/Default_3.png", description="Path to the third image file.")

class GenerateBodySlide5Input(BaseModel):
    """Input schema for generate_body_slide5."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'MainTitle'.")
    subtitle1: str = Field(..., description="Subtitle for the first content section. Default: 'SUBTITLE1'.")
    content1: str = Field(..., description="Content text for the first content section. Default: 'Content1'.")
    subtitle2: str = Field(..., description="Subtitle for the second content section. Default: 'SUBTITLE2'.")
    content2: str = Field(..., description="Content text for the second content section. Default: 'Content2'.")
    subtitle3: str = Field(..., description="Subtitle for the third content section. Default: 'SUBTITLE3'.")
    content3: str = Field(..., description="Content text for the third content section. Default: 'Content3'.")
    subtitle4: str = Field(..., description="Subtitle for the fourth content section. Default: 'SUBTITLE4'.")
    content4: str = Field(..., description="Content text for the fourth content section. Default: 'Content4'.")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accents and borders.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#6b9d34", description="CSS color for subtitles.")
    content_color: str = Field(default="#555555", description="CSS color for content text.")
    font_family: str = Field(default="'Inter', sans-serif", description="CSS font family for the slide.")
    image_url_1: str = Field(default="Image/generate_body_slide5/Default_1.png", description="Path to the first image file.")
    image_url_2: str = Field(default="Image/generate_body_slide5/Default_2.png", description="Path to the second image file.")
    image_url_3: str = Field(default="Image/generate_body_slide5/Default_3.png", description="Path to the third image file.")
    image_url_4: str = Field(default="Image/generate_body_slide5/Default_4.png", description="Path to the fourth image file.")


class GenerateBodySlide7Input(BaseModel):
    """Input schema for generate_body_slide7."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'MainTitle'.")
    subtitle: str = Field(..., description="Subtitle for the right column. Default: 'SubTitle'.")
    content1: str = Field(..., description="First content text section. Default: 'Content1'.")
    content2: str = Field(..., description="Second content text section. Default: 'Content2'.")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accents, such as the title accent block.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#333333", description="CSS color for the subtitle.")
    content_color: str = Field(default="#4a90a0", description="CSS color for content text.")
    divider_color: str = Field(default="#d5e8b9", description="CSS color for the horizontal divider.")
    font_family: str = Field(default="'Inter', sans-serif", description="CSS font family for the slide.")
    image_url_1: str = Field(default="Image/generate_body_slide7/Default_1.png", description="Path to the first image file.")
    image_url_2: str = Field(default="Image/generate_body_slide7/Default_2.png", description="Path to the second image file.")
    image_url_3: str = Field(default="Image/generate_body_slide7/Default_3.png", description="Path to the third image file.")

class GenerateBodySlide10Input(BaseModel):
    """Input schema for generate_body_slide10."""
    main_title: str = Field(..., description="Main title of the slide displayed prominently at the top (e.g., 'Key Features Overview').")
    subtitle1: str = Field(..., description="Subtitle for the first content section. Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., '<b>Innovation</b> & Technology').")
    content1: str = Field(..., description="Content text for the first section. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'This covers <b>key innovations</b> in <i>modern technology</i>: <ul><li>Advanced <u>algorithms</u></li><li>Smart <span style=\"color: #e74c3c;\">automation</span></li><li>Enhanced user experience</li></ul>'")
    subtitle2: str = Field(..., description="Subtitle for the second content section. Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., 'Market <u>Analysis</u>').")
    content2: str = Field(..., description="Content text for the second section. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Comprehensive analysis of <b>market trends</b>: <ul><li>Consumer <i>behavior patterns</i></li><li>Emerging <u>market opportunities</u></li><li>Competitive <span style=\"color: #27ae60;\">advantages</span></li></ul>'")
    subtitle3: str = Field(..., description="Subtitle for the third content section. Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., 'Future <b>Roadmap</b>').")
    content3: str = Field(..., description="Content text for the third section. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Strategic planning for <b>sustainable growth</b>: <ul><li>Short-term <i>objectives</i></li><li>Long-term <u>vision</u></li><li>Resource <span style=\"color: #3498db;\">allocation</span></li></ul>'")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the entire slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accent elements including icon backgrounds and decorative elements.")
    title_color: str = Field(default="#333333", description="CSS color for the main title text.")
    subtitle_color: str = Field(default="#333333", description="CSS color for all subtitle text in the three content sections.")
    content_color: str = Field(default="#555555", description="CSS color for all content/body text in the three sections.")
    font_family: str = Field(default="'Inter', sans-serif", description="The CSS font family for all text on the slide.")
    image_url: str = Field(default="Image/generate_body_slide10/Default_1.png", description="Path to the image file for the left side.")
    icon1: str = Field(default="<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\">...</svg>", description="Complete SVG code for the first section's icon. Should be a valid SVG element with proper xmlns attribute.")
    icon2: str = Field(default="<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\">...</svg>", description="Complete SVG code for the second section's icon. Should be a valid SVG element with proper xmlns attribute.")
    icon3: str = Field(default="<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\">...</svg>", description="Complete SVG code for the third section's icon. Should be a valid SVG element with proper xmlns attribute.")

class GenerateBodySlide11Input(BaseModel):
    """Input schema for generate_body_slide11."""
    main_title: str = Field(..., description="The main title of the slide.")
    subtitle1: str = Field(..., description="Subtitle for the first content box. You can use HTML tags like '<b>' for emphasis.")
    content1: str = Field(..., description="Content for the first box. For structured bullet points, use '<ul>' and '<li>' tags. To highlight key phrases, use HTML tags like '<b>bold</b>', '<i>italic</i>', or '<span style=\"color:blue\">colored text</span>'. For sub-points (ý nhỏ), nest another '<ul>' inside an '<li>'.")
    icon1: str = Field(..., description="SVG code for the first section's icon(e.g., '<svg xmlns=\"http://www.w3.org/2000/svg\" ...>').")
    subtitle2: str = Field(..., description="Subtitle for the second content box. You can use HTML tags like '<b>' for emphasis.")
    content2: str = Field(..., description="Content for the second box. For structured bullet points, use '<ul>' and '<li>' tags. To highlight key phrases, use HTML tags like '<b>bold</b>', '<i>italic</i>', or '<span style=\"color:blue\">colored text</span>'. For sub-points (ý nhỏ), nest another '<ul>' inside an '<li>'.")
    icon2: str = Field(..., description="SVG code for the second section's icon(e.g., '<svg xmlns=\"http://www.w3.org/2000/svg\" ...>').")
    subtitle3: str = Field(..., description="Subtitle for the third content box. You can use HTML tags like '<b>' for emphasis.")
    content3: str = Field(..., description="Content for the third box. For structured bullet points, use '<ul>' and '<li>' tags. To highlight key phrases, use HTML tags like '<b>bold</b>', '<i>italic</i>', or '<span style=\"color:blue\">colored text</span>'. For sub-points, nest another '<ul>' inside an '<li>'.")
    icon3: str = Field(..., description="SVG code for the third section's icon.(e.g., '<svg xmlns=\"http://www.w3.org/2000/svg\" ...>')")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    box_bg_color: str = Field(default="#e6f2dd", description="CSS background color for the content boxes.")
    accent_color: str = Field(default="#8cc63f", description="CSS color for accents and icons.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#333333", description="CSS color for subtitles in the boxes.")
    content_color: str = Field(default="#555555", description="CSS color for content text in the boxes.")
    font_family: str = Field(default="'Inter', sans-serif", description="The CSS font family for all text on the slide.")
    box_height: str = Field(default="15.625rem", description="The CSS height of the content boxes, should be in REM units.")

class GenerateBodySlide12Input(BaseModel):
    """Input schema for generate_body_slide12."""
    main_title: str = Field(..., description="Main title of the slide displayed prominently at the top (e.g., 'Our Key Solutions').")
    main_content: str = Field(..., description="Content text for the horizontal bar section. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'We provide <b>comprehensive solutions</b> that deliver <i>measurable results</i>: <ul><li>Enhanced <u>performance</u></li><li>Improved <span style=\"color: #e74c3c;\">efficiency</span></li><li>Sustainable growth</li></ul>'")
    subtitle1: str = Field(..., description="Subtitle for the first image section. Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., '<b>Digital</b> Transformation').")
    content1: str = Field(..., description="Content text for the first image section. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Modernizing <b>business processes</b> through <i>innovative technology</i>: <ul><li>Cloud <u>migration</u></li><li>Process <span style=\"color: #27ae60;\">automation</span></li><li>Data analytics</li></ul>'")
    subtitle2: str = Field(..., description="Subtitle for the second image section. Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., 'Strategic <u>Planning</u>').")
    content2: str = Field(..., description="Content text for the second image section. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Comprehensive <b>strategy development</b> for <i>long-term success</i>: <ul><li>Market <u>analysis</u></li><li>Risk <span style=\"color: #3498db;\">assessment</span></li><li>Growth planning</li></ul>'")
    subtitle3: str = Field(..., description="Subtitle for the third image section. Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., 'Team <b>Development</b>').")
    content3: str = Field(..., description="Content text for the third image section. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Building <b>high-performance teams</b> through <i>targeted training</i>: <ul><li>Skill <u>development</u></li><li>Leadership <span style=\"color: #9b59b6;\">coaching</span></li><li>Performance optimization</li></ul>'")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the entire slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accent elements including borders, decorative elements, and highlights.")
    title_color: str = Field(default="#333333", description="CSS color for the main title text.")
    content_color: str = Field(default="#555555", description="CSS color for all content/body text including main content and image section content.")
    subtitle_color: str = Field(default="#333333", description="CSS color for all subtitle text in the three image sections.")
    font_family: str = Field(default="'Inter', sans-serif", description="The CSS font family for all text on the slide.")
    image_url_1: str = Field(default="Image/generate_body_slide12/Default_1.png", description="Path to the first image file.")
    image_url_2: str = Field(default="Image/generate_body_slide12/Default_2.png", description="Path to the second image file.")
    image_url_3: str = Field(default="Image/generate_body_slide12/Default_3.png", description="Path to the third image file.")


class GenerateBodySlide15Input(BaseModel):
    """Input schema for generate_body_slide15."""
    main_title: str = Field(..., description="Main title of the slide displayed at the top (e.g., 'Main Title').")
    subtitle: str = Field(..., description="Subtitle for the right column, appears as a section header (e.g., 'Subtitle').")
    content1: str = Field(..., description="First content text section. Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Empowering <b>talented teams</b> through <i>professional development</i>: <ul><li>Continuous <u>learning</u></li><li>Career <span style=\"color: #9b59b6;\">advancement</span></li><li>Collaborative culture</li></ul>'")
    content2: str = Field(..., description="Second content text section. Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Empowering <b>talented teams</b> through <i>professional development</i>: <ul><li>Continuous <u>learning</u></li><li>Career <span style=\"color: #9b59b6;\">advancement</span></li><li>Collaborative culture</li></ul>'")
    image_url: str = Field(default="Image/generate_body_slide15/Default_1.png", description="Path to the background image for the slide.")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accents, such as the title accent block.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#333333", description="CSS color for the subtitle.")
    content_color: str = Field(default="#555555", description="CSS color for content text.")
    font_family: str = Field(default="'Inter', sans-serif", description="CSS font family for the slide.")

class GenerateBodySlide18Input(BaseModel):
    """Input schema for generate_body_slide18."""
    main_title: str = Field(..., description="The main title displayed at the top center of the slide (e.g., 'Main title').")
    left_title: str = Field(..., description="The title for the left column (e.g., 'Subtitle 1').")
    right_title: str = Field(..., description="The title for the right column (e.g., 'Subtitle 2').")
    left_text: str = Field(..., description="Text content for the left column.'")
    right_text: str = Field(..., description="Text content for the right column.'")
    left_icon: str = Field(default="gavel", description="Icon to display in the left column. Options: 'gavel' (predefined gavel icon) or 'custom' (use custom SVG code).")
    right_icon: str = Field(default="scales", description="Icon to display in the right column. Options: 'scales' (predefined scales icon) or 'custom' (use custom SVG code).")
    custom_left_icon: str = Field(default="", description="Custom SVG code for the left icon. Only used when left_icon is set to 'custom'. Should be a complete SVG element with proper dimensions (recommended: 70x70px).")
    custom_right_icon: str = Field(default="", description="Custom SVG code for the right icon. Only used when right_icon is set to 'custom'. Should be a complete SVG element with proper dimensions (recommended: 70x70px).")
    title_color: str = Field(default="#555555", description="CSS color for all titles (main title and column titles).")
    text_color: str = Field(default="#555555", description="CSS color for all text content.")
    icon_color: str = Field(default="#a2c4c9", description="CSS color for the icons.")
    background_color: str = Field(default="#ffffff", description="CSS background color for the main content area.")
    accent_color: str = Field(default="#a2c4c9", description="CSS color for the border/frame background.")
    divider_color: str = Field(default="#555555", description="CSS color for the dashed divider line between columns.")
    font_family: str = Field(default="Arial, sans-serif", description="The CSS font family for all text on the slide.")

class GenerateBodySlide19Input(BaseModel):
    """Input schema for generate_body_slide19."""
    main_title: str = Field(..., description="The main title displayed at the top center of the slide (e.g., 'Your Title Here').")
    left_column_titles: List[str] = Field(..., description="Array of titles for the left column sections. Each title will be displayed as a section header in the left column.")
    left_column_texts: List[str] = Field(..., description="Array of text content for the left column sections. Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Presentations are <b>communication tools</b> that can be used as <i>demonstrations</i>: <ul><li>Interactive <u>engagement</u></li><li>Visual <span style=\"color: #e74c3c;\">storytelling</span></li><li>Audience participation</li></ul>'")
    right_column_titles: List[str] = Field(..., description="Array of titles for the right column sections. Each title will be displayed as a section header in the right column with an accompanying icon.")
    right_column_texts: List[str] = Field(..., description="Array of text content for the right column sections. Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Presentations are <b>communication tools</b> for <i>speeches and reports</i>: <ul><li>Professional <u>delivery</u></li><li>Clear <span style=\"color: #27ae60;\">messaging</span></li><li>Structured format</li></ul>'")
    main_title_color: str = Field(default="#555555", description="CSS color for the main title.")
    left_bg_color: str = Field(default="#a2c4c9", description="CSS background color for the left column.")
    left_text_color: str = Field(default="#ffffff", description="CSS color for all text in the left column (titles and content).")
    right_title_color: str = Field(default="#555555", description="CSS color for the titles in the right column.")
    right_text_color: str = Field(default="#555555", description="CSS color for the text content in the right column.")
    border_color: str = Field(default="#a2c4c9", description="CSS color for the outer border frame and right column border.")
    icon_color: str = Field(default="#a2c4c9", description="CSS color for the icons displayed in the right column sections.")
    font_family: str = Field(default="Arial, sans-serif", description="The CSS font family for all text on the slide.")

class GenerateBodySlide20Input(BaseModel):
    """Input schema for generate_body_slide20."""
    main_title: str = Field(..., description="The main title displayed at the top center of the slide (e.g., 'Main title').")
    left_title: str = Field(..., description="The title for the left column (e.g., 'Subtitle 1').")
    right_title: str = Field(..., description="The title for the right column (e.g., 'Subtitle 2').")
    left_text: str = Field(..., description="Text content for the left column.'")
    right_text: str = Field(..., description="Text content for the right column.'")
    left_icon: str = Field(default="gavel", description="Icon to display in the left column. Options: 'gavel' (predefined gavel icon), 'scales' (predefined scales icon), or 'custom' (use custom SVG code).")
    right_icon: str = Field(default="scales", description="Icon to display in the right column. Options: 'gavel' (predefined gavel icon), 'scales' (predefined scales icon), or 'custom' (use custom SVG code).")
    custom_left_icon: str = Field(default="", description="Custom SVG code for the left icon. Only used when left_icon is set to 'custom'. Should be a complete SVG element with proper dimensions (recommended: 70x70px).")
    custom_right_icon: str = Field(default="", description="Custom SVG code for the right icon. Only used when right_icon is set to 'custom'. Should be a complete SVG element with proper dimensions (recommended: 70x70px).")
    title_color: str = Field(default="#555555", description="CSS color for all titles (main title and column titles).")
    text_color: str = Field(default="#555555", description="CSS color for all text content.")
    icon_color: str = Field(default="#a2c4c9", description="CSS color for the icons.")
    background_color: str = Field(default="#ffffff", description="CSS background color for the main content area.")
    accent_color: str = Field(default="#a2c4c9", description="CSS color for the border/frame background.")
    divider_color: str = Field(default="#555555", description="CSS color for the dashed divider line between columns.")
    font_family: str = Field(default="Arial, sans-serif", description="The CSS font family for all text on the slide.")

class GenerateMainPointsSlideInput(BaseModel):
    """Input schema for generate_main_points_slide."""
    title: str = Field(..., description="Main title displayed at the top of the slide in uppercase")
    point1_title: str = Field(..., description="Title for the first point (plastic bag icon) - displayed in uppercase")
    point1_description: str = Field(..., description="Description text for the first point about plastic/waste management. .")
    point2_title: str = Field(..., description="Title for the second point (faucet icon) - displayed in uppercase")
    point2_description: str = Field(..., description="Description text for the second point about water conservation/management. .")
    point3_title: str = Field(..., description="Title for the third point (factory icon) - displayed in uppercase")
    point3_description: str = Field(..., description="Description text for the third point about industrial processes/manufacturing. .")
    font_family: str = Field(default=None, description="Font family for all text elements")

class GenerateElegantPointsSlideInput(BaseModel):
    """Input schema for generate_elegant_points_slide."""
    main_title: str = Field(..., description="A concise title at the top of the slide, styled to be less prominent than the main content. Default: 'Write Your Topic or Idea Here'.")
    points: List[Dict[str, str]] = Field(..., description="An array of exactly 4 objects, where each object represents a large, prominent content card with an icon, title, and description. Each point should have 'title' and 'description' keys. Default: [{'title': 'Add a Key Point', 'description': 'Briefly elaborate on the topic you want to discuss.'}, {'title': 'Add a Key Point', 'description': 'Briefly elaborate on the topic you want to discuss.'}, {'title': 'Add a Key Point', 'description': 'Briefly elaborate on the topic you want to discuss.'}, {'title': 'Add a Key Point', 'description': 'Briefly elaborate on the topic you want to discuss.'}].")
    font_family: str = Field(default="'Be Vietnam Pro', sans-serif", description="Font family for all text elements.")
    bg_color: str = Field(default="#FDFCFB", description="Overall background color of the slide (off-white).")
    card_bg_color: str = Field(default="#FFFFFF", description="Background color for the four content cards (pure white).")
    title_color: str = Field(default="#4E443F", description="Text color for the main title and card titles (dark brown).")
    text_color: str = Field(default="#5D534D", description="Text color for the card descriptions (lighter brown-gray).")
    accent_color: str = Field(default="#B99C6B", description="The accent color for the icons and their dividers (bronze/old gold).")


class GenerateCorporateContentSlideInput(BaseModel):
    """Input schema for generate_corporate_content_slide."""
    main_title: str = Field(..., description="The main title displayed in the colored panel on the left. To highlight a word, wrap it in `<span class='highlight'>...</span>`. Default: 'THIS IS A <span class=\'highlight\'>SLIDE</span> TITLE'.")
    list_items: List[Dict[str, str]] = Field(..., description="An array of objects, where each object represents a content card with its own title and description. Default: [{'title': 'First Key Point', 'description': 'Here you have a list of items, presented in a modern, card-based format.'}, {'title': 'Second Key Point', 'description': 'And some text to elaborate on the second main idea of your slide.'}, {'title': 'Third Key Point', 'description': 'But remember not to overload your slides with too much content.'}]")
    font_family: str = Field(default="'Montserrat', 'Inter', sans-serif", description="Font family for all text elements.")
    bg_color: str = Field(default="#F8FAFC", description="The background color for the main content area (typically off-white).")
    accent_panel_color: str = Field(default="#6366F1", description="The background color for the diagonal title panel.")
    title_color: str = Field(default="#FFFFFF", description="Text color for the main title on the colored panel.")
    card_bg_color: str = Field(default="#FFFFFF", description="Background color for the content cards.")
    card_border_color: str = Field(default="#E5E7EB", description="Border color for the content cards.")
    list_title_color: str = Field(default="#000000", description="Text color for the titles inside the content cards. Use dark colors for visibility on white backgrounds.")
    list_text_color: str = Field(default="#333333", description="Text color for the description text inside the content cards. Use dark colors for visibility on white backgrounds.")

class GenerateSplitContentSlideInput(BaseModel):
    """Input schema for generate_split_content_slide."""
    main_title: str = Field(..., description="The main title at the top of the slide. Use `<span class='highlight'>...</span>` to color a word with the accent color. Default: 'SPLIT YOUR CONTENT'.")
    columns: List[Dict[str, str]] = Field(..., description="An array of exactly 2 objects, each representing a content card with an icon, title, and description. Default: [{'icon_name': 'bulb', 'title': 'Title One', 'description': 'Description for the first column goes here. Elaborate on your point with clear and concise text.'}, {'icon_name': 'target', 'title': 'Title Two', 'description': 'Description for the second column. This layout is perfect for comparing two ideas side-by-side.'}]")
    font_family: str = Field(default="'Montserrat', 'Inter', sans-serif", description="Font family for all text elements.")
    bg_gradient_start: str = Field(default="#0F172A", description="The starting color (top) of the dark background gradient.")
    bg_gradient_end: str = Field(default="#1E293B", description="The ending color (bottom) of the dark background gradient.")
    title_color: str = Field(default="#FFFFFF", description="The color for the main title and the card titles.")
    text_color: str = Field(default="#D1D5DB", description="The color for the card descriptions.")
    accent_color: str = Field(default="#22D3EE", description="The neon accent color used for highlights, card borders, and icons.")

class GenerateCorporateMulticolumnSlideInput(BaseModel):
    """Input schema for generate_corporate_multicolumn_slide."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks and <span class='highlight'>word</span> to highlight. Will be displayed in large 2.5rem font. Default: 'IN TWO OR THREE<br><span class=\'highlight\'>COLUMNS</span>'.")
    columns: List[Dict[str, str]] = Field(..., description="An array of 2 or 3 objects, each representing a column. Each column will be displayed as a card with gradient background, rounded corners, and hover effects. Default: [{'title': 'Yellow', 'description': 'Is the color of gold, butter and ripe lemons.'}, {'title': 'Blue', 'description': 'Is the colour of the clear sky and the deep sea.'}, {'title': 'Red', 'description': 'Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage.'}]")
    font_family: str = Field(default="'Montserrat', 'Inter', sans-serif", description="The font family for all text elements. Enhanced with additional font weights (400, 600, 700, 800).")
    accent_color: str = Field(default="#8B5CF6", description="The primary accent color for the right panel, highlighted text, and card accent borders. Used in gradients for enhanced visual appeal.")
    shadow_color: str = Field(default="#7C3AED", description="The secondary (darker) accent color for the panel behind and gradient effects.")
    text_color: str = Field(default="#4B5563", description="The primary color for the body text.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small globe icon. Icon size increased to 3.5rem with drop-shadow effect.")

class GenerateCorporateGridSlideInput(BaseModel):
    """Input schema for generate_corporate_grid_slide."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks and <span class='highlight'>word</span> to highlight. Will be displayed in large 2.5rem font with uppercase styling. Default: 'LET'S <span class=\'highlight\'>REVIEW</span> SOME<br>CONCEPTS'.")
    grid_items: List[Dict[str, str]] = Field(..., description="An array of exactly 6 objects for the 2x3 grid. Each item will be displayed as a card with gradient background, rounded corners, hover effects, and colored top border. Grid automatically adjusts to 2 columns on smaller screens. Default: [{'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}]")
    font_family: str = Field(default="'Montserrat', 'Inter', sans-serif", description="The font family for all text elements. Enhanced with additional font weights (400, 600, 700, 800).")
    accent_color: str = Field(default="#22C55E", description="The primary accent color for the right panel, highlighted text, and card accent borders. Used in gradients for enhanced visual appeal.")
    shadow_color: str = Field(default="#16A34A", description="The secondary (darker) accent color for the panel behind and gradient effects.")
    text_color: str = Field(default="#6B7280", description="The primary color for the body text.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small pencil icon. Icon size increased to 3.5rem with drop-shadow effect.")

class GenerateBusinessOverviewSlideInput(BaseModel):
    """Input schema for generate_business_overview_slide."""
    main_title: str = Field(..., description="Main title text (10-25 characters), displayed on the left side. Default: 'BUSINESS OVERVIEW'.")
    sections: List[Dict] = Field(..., description="List of dictionaries with icon and content for each section. Icons: 'chart-analysis', 'innovation', 'growth'. . Default: 3 sections with Lorem ipsum content.")
    left_bg_color: str = Field(default="#1a4b8c", description="Background color for the left title section (hex code).")
    right_bg_color: str = Field(default="#f8f9fa", description="Background color for the right content area (hex code).")
    title_color: str = Field(default="#FFFFFF", description="Color of the main title text (hex code).")
    icon_bg_color: str = Field(default="#2a3f6b", description="Background color for icon containers (hex code).")
    icon_color: str = Field(default="#FFFFFF", description="Color of the icons (hex code).")
    content_bg_color: str = Field(default="#FFFFFF", description="Background color for content text areas (hex code).")
    content_text_color: str = Field(default="#1a4b8c", description="Text color for content sections (hex code).")
    font_family: str = Field(default="Arial, sans-serif", description="Font family for all text elements.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
    border_opacity: Optional[float] = Field(default=0, description="Opacity of the border frame (0.0 to 1.0). Default: 0.3.")
    section_spacing: str = Field(default="15px", description="Vertical spacing between content sections.")
    icon_size: str = Field(default="80px", description="Size of the icon containers.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

class GenerateVisionMissionSlideInput(BaseModel):
    """Input schema for generate_vision_mission_slide."""
    vision_title: str = Field(..., description="Title for the vision section (5-15 characters). Default: 'VISION'.")
    mission_title: str = Field(..., description="Title for the mission section (5-15 characters). Default: 'MISSION'.")
    vision_points: List[str] = Field(..., description="List of vision statements. . Default: 2 Lorem ipsum statements.")
    mission_points: List[str] = Field(..., description="List of mission statements. . Default: 2 Lorem ipsum statements.")
    vision_bg_color: str = Field(default="#1a4b8c", description="Background color for the vision section (hex code).")
    mission_bg_color: str = Field(default="#4a7bc8", description="Background color for the mission section (hex code).")
    text_color: str = Field(default="#FFFFFF", description="Color of all text elements (hex code).")
    vision_number_color: str = Field(default="rgba(74, 123, 200, 0.3)", description="Color of background numbers in vision section (rgba).")
    mission_number_color: str = Field(default="rgba(26, 75, 140, 0.3)", description="Color of background numbers in mission section (rgba).")
    font_family: str = Field(default="Arial, sans-serif", description="Font family for all text elements.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
    border_color: str = Field(default="#1a4b8c", description="Color of the border frame (hex code).")
    border_opacity: Optional[float] = Field(default=0, description="Opacity of the border frame (0.0 to 1.0). Default: 0.4.")
    show_geometric_pattern: Optional[bool] = Field(default=True, description="Whether to show geometric background pattern. Default: True.")
    pattern_opacity: Optional[float] = Field(default=0, description="Opacity of the geometric pattern (0.0 to 1.0). Default: 0.1.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

class GenerateStrategicGoalsSlideInput(BaseModel):
    """Input schema for generate_strategic_goals_slide."""
    main_title: str = Field(..., description="Main title text (10-25 characters), displayed on the left side. Default: 'STRATEGIC GOALS'.")
    goals: List[Dict] = Field(..., description="List of dictionaries with number and content for each strategic goal. . Default: 3 goals with Lorem ipsum content.")
    bg_image: str = Field(default="skyscrapers.jpg", description="Background image URL or path (skyscraper/city image recommended).")
    bg_overlay_color: str = Field(default="rgba(26, 75, 140, 0.85)", description="Color overlay for the background image (rgba with transparency).")
    title_color: str = Field(default="#FFFFFF", description="Color of the main title text (hex code).")
    number_bg_color: str = Field(default="#1a4b8c", description="Background color for the number circles (hex code).")
    number_text_color: str = Field(default="#FFFFFF", description="Text color for the numbers (hex code).")
    content_bg_color: str = Field(default="#FFFFFF", description="Background color for content text boxes (hex code).")
    content_text_color: str = Field(default="#1a4b8c", description="Text color for content (hex code).")
    font_family: str = Field(default="Arial, sans-serif", description="Font family for all text elements.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
    border_opacity: Optional[float] = Field(default=0, description="Opacity of the border frame (0.0 to 1.0). Default: 0.4.")
    number_circle_size: str = Field(default="80px", description="Size of the circular number containers.")
    content_padding: str = Field(default="20px", description="Padding inside content boxes.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

class GenerateServiceRoadmapSlideInput(BaseModel):
    """Input schema for generate_service_roadmap_slide."""
    main_title: str = Field(..., description="Main title text (10-30 characters), displayed at the top center. Default: 'SERVICE ROADMAP'.")
    roadmap_items: List[Dict] = Field(..., description="List of dictionaries with title and content for each roadmap phase. . Default: 4 phases with Lorem ipsum content.")
    bg_gradient_start: str = Field(default="#4A90E2", description="Starting color of the background gradient (hex code).")
    bg_gradient_end: str = Field(default="#2E5BBA", description="Ending color of the background gradient (hex code).")
    title_color: str = Field(default="#FFFFFF", description="Color of the main title text (hex code).")
    card_bg_color: str = Field(default="#FFFFFF", description="Background color for content cards (hex code).")
    card_text_color: str = Field(default="#2E5BBA", description="Text color for card content (hex code).")
    card_title_color: str = Field(default="#1A4480", description="Text color for card titles (hex code).")
    font_family: str = Field(default="Arial, sans-serif", description="Font family for all text elements.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
    border_color: str = Field(default="rgba(255, 255, 255, 0.3)", description="Color of the border frame (rgba with transparency).")
    show_decorative_triangles: Optional[bool] = Field(default=True, description="Whether to show decorative triangle elements. Default: True.")
    triangle_color: str = Field(default="rgba(255, 255, 255, 0.1)", description="Color of the decorative triangles (rgba with transparency).")
    card_border_radius: str = Field(default="20px", description="Border radius for content cards.")
    card_padding: str = Field(default="25px", description="Padding inside content cards.")
    card_shadow: str = Field(default="0 8px 24px rgba(0, 0, 0, 0.15)", description="Box shadow for content cards.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

class GenerateFinancialProjectionsSlideDarkInput(BaseModel):
    """Input schema for generate_financial_projections_slide_dark."""
    main_title: str = Field(..., description="Main title displayed at the top of the slide. Default: 'FINANCIAL PROJECTIONS'.")
    cards: List[Dict] = Field(..., description="List of dictionaries with 'title' and 'content' keys for each card. . Default: 3 cards with financial topics and Lorem ipsum content.")
    background_color: str = Field(default="#1E3A8A", description="Solid background color (dark blue).")
    main_title_color: str = Field(default="#FFFFFF", description="Color of the main title text.")
    card_background_color: str = Field(default="rgba(255, 255, 255, 0.95)", description="Background color of the cards.")
    card_title_color: str = Field(default="#1E3A8A", description="Color of the card titles.")
    card_content_color: str = Field(default="#374151", description="Color of the card content text.")
    border_color: str = Field(default="rgba(255, 255, 255, 0.3)", description="Color of the border elements.")
    font_family: str = Field(default="Segoe UI, Arial, sans-serif", description="Font family for all text elements.")
    main_title_font_weight: str = Field(default="700", description="Font weight of the main title.")
    main_title_letter_spacing: str = Field(default="0.05em", description="Letter spacing of the main title.")
    card_title_font_weight: str = Field(default="700", description="Font weight of the card titles.")
    card_title_letter_spacing: str = Field(default="0.02em", description="Letter spacing of the card titles.")
    card_content_line_height: str = Field(default="1.6", description="Line height of the card content.")
    card_content_font_weight: str = Field(default="400", description="Font weight of the card content.")
    slide_padding: str = Field(default="60px", description="Padding around the entire slide.")
    main_title_margin_bottom: str = Field(default="80px", description="Bottom margin below the main title.")
    cards_gap: str = Field(default="40px", description="Gap between the cards.")
    card_padding: str = Field(default="40px", description="Internal padding within each card.")
    card_border_radius: str = Field(default="12px", description="Border radius of the cards.")
    card_shadow: str = Field(default="0 8px 32px rgba(0, 0, 0, 0.2)", description="Box shadow of the cards.")
    card_title_margin_bottom: str = Field(default="25px", description="Bottom margin below card titles.")
    show_border_frame: Optional[bool] = Field(default=True, description="Whether to show dashed border frame. Default: True.")
    frame_border_style: str = Field(default="3px dashed", description="Style of the border frame.")
    frame_border_color: str = Field(default="rgba(255, 255, 255, 0.4)", description="Color of the border frame.")
    frame_border_radius: str = Field(default="12px", description="Border radius of the frame.")
    frame_padding: str = Field(default="80px", description="Padding inside the border frame.")
    additional_css: str = Field(default="''", description="Additional CSS to include.")

class GenerateMinimalistTechListSlideInput(BaseModel):
    """Input schema for generate_minimalist_tech_list_slide."""
    title: str = Field(..., description="The main title of the slide. Default: 'This is a slide title'.")
    list_items: List[str] = Field(..., description="A list of strings for the bullet points. Default: ['Here you have a list of items', 'And some text', 'But remember not to overload your slides with content'].")
    concluding_text: str = Field(..., description="A final sentence or phrase at the bottom, styled to stand out. Default: 'Your audience will listen to you or read the content, but won't do both.'.")
    title_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '3rem') for the main title.")
    list_item_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '1.5rem') for list items.")
    concluding_text_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '1.1rem') for the concluding text.")
    font_family: str = Field(default="'Nunito', sans-serif", description="CSS font-family for the slide.")
    sky_top_color: str = Field(default="#ABB0EA", description="The color for the top of the background gradient.")
    sky_bottom_color: str = Field(default="#A2CFED", description="The color for the bottom of the background gradient.")
    grid_dot_color: str = Field(default="rgba(0, 0, 0, 0.05)", description="The color of the dots in the background grid.")
    text_color: str = Field(default="#1F2937", description="The main color for all text elements.")
    accent_color: str = Field(default="#6366F1", description="The accent color for the side border and bullet points.")
    custom_css: str = Field(default="", description="Optional custom CSS for advanced styling.")

class GenerateCenteredTechColumnsSlideInput(BaseModel):
    """Input schema for generate_centered_tech_columns_slide."""
    title: str = Field(..., description="The main title for the slide's content. Default: 'You can also split your content'.")
    columns: List[Dict[str, str]] = Field(..., description="An array of objects, where each object represents a column with keys 'icon_name' (bulb, target, rocket), 'title', and 'description'. Default: [{'icon_name': 'bulb', 'title': 'Column One', 'description': 'Description for column one.'}, {'icon_name': 'target', 'title': 'Column Two', 'description': 'Description for column two.'}].")
    font_family: str = Field(default="'Nunito', sans-serif", description="The font family for all text elements.")
    text_color: str = Field(default="#F8FAFC", description="The color for all text elements.")
    sky_top_color: str = Field(default="#0F172A", description="Background color for the top of the slide.")
    sky_bottom_color: str = Field(default="#1E293B", description="Background color for the bottom of the slide.")
    grid_dot_color: str = Field(default="rgba(255, 255, 255, 0.1)", description="The color and opacity for the dots in the background grid.")
    accent_color: str = Field(default="#22D3EE", description="The accent color for borders and icons.")
    card_bg_color: str = Field(default="rgba(30, 41, 59, 0.5)", description="Background color for the content cards.")

class GenerateSplitLayoutListSlideInput(BaseModel):
    """Input schema for generate_split_layout_list_slide."""
    main_title: str = Field(..., description="The main title displayed in the left column. Supports HTML tags like <b>, <i>, and <br> for line breaks. Default: 'YOUR MAIN TOPIC'.")
    points: List[Dict[str, str]] = Field(..., description="A list of key points to display in the right column. Each point should have 'title' and 'description' keys.")
    font_size_multiplier: Optional[float] = Field(default=1.0, description="Adjusts the default responsive font size. 1.0 is standard. This is ignored if a fixed font size is set below.")
    main_title_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '4rem') for the main title, overriding automatic scaling.")
    point_title_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '1.25rem') for the point titles, overriding automatic scaling.")
    point_description_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '1rem') for the point descriptions, overriding automatic scaling.")
    font_family: str = Field(default="'Be Vietnam Pro', sans-serif", description="CSS font-family for the slide.")
    left_bg_color: str = Field(default="#6F6254", description="Background color for the left column (hex code).")
    right_bg_color: str = Field(default="#F5F0E8", description="Background color for the right column (hex code).")
    light_text_color: str = Field(default="#F5F0E8", description="Text color for the left column (hex code).")
    dark_text_color: str = Field(default="#6F6254", description="Text color for the right column (hex code).")
    divider_color: str = Field(default="#D3CFC7", description="Color of the divider line between points (hex code).")
    custom_css: str = Field(default=None, description="Optional custom CSS for advanced styling.")

class GenerateReferenceSlideInput(BaseModel):
    """Input schema for generate_reference_slide."""
    main_title: str = Field(..., description="The main, bold title at the top of the text column. Default: 'CONTENT'.")
    reference_items: List[Dict[str, str]] = Field(..., description="An array of objects, each representing a reference or key point. Each item should have 'title' and 'description' keys. Default: [{'title': 'PRIMARY REFERENCE TITLE', 'description': 'Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. They serve various purposes and are effective tools.'}, {'title': 'SECONDARY REFERENCE TITLE', 'description': 'Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. They serve various purposes and are effective tools.'}].")
    image_url: str = Field(default="https://images.unsplash.com/photo-1543269865-cbf427effbad?q=80&w=2070&auto=format&fit=crop", description="URL for the full-height image in the right column.")
    font_family: str = Field(default="'Be Vietnam Pro', sans-serif", description="Font family for all text elements.")
    bg_color: str = Field(default="#FFFFFF", description="The background color for the text column.")
    text_color: str = Field(default="#1F2937", description="The main text color for all text elements.")
    accent_color: str = Field(default="#3B82F6", description="The color for the decorative divider below the main title.")

class GenerateIconListSlideInput(BaseModel):
    """Input schema for generate_icon_list_slide."""
    main_title: str = Field(..., description="The supporting title displayed in the smaller, left column. Default: 'Write your topic or idea'.")
    points: List[Dict[str, str]] = Field(..., description="An array of objects, each representing a key point in the main content area. Each point should have 'icon_name', 'title', and 'description' keys. Default: [{ 'icon_name': 'megaphone', 'title': 'Add a main point', 'description': 'Briefly elaborate on what you want to discuss.' }, { 'icon_name': 'star', 'title': 'Add a main point', 'description': 'Briefly elaborate on what you want to discuss.' }, { 'icon_name': 'thumbs-up', 'title': 'Add a main point', 'description': 'Briefly elaborate on what you want to discuss.' }].")
    font_family: str = Field(default="'Montserrat', 'Inter', sans-serif", description="Font family for all text elements.")
    bg_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    main_title_color: str = Field(default="#111827", description="Text color for the main title.")
    point_title_color: str = Field(default="#1F2937", description="Text color for the point titles.")
    point_description_color: str = Field(default="#4B5563", description="Text color for the point descriptions.")
    accent_color: str = Field(default="#3B82F6", description="The single accent color used for all icon circles and the decorative divider.")

class GenerateFlexibleColumnsSlideInput(BaseModel):
    """Input schema for generate_flexible_columns_slide."""
    main_title: str = Field(..., description="The main title displayed at the top of the slide. Default: 'IN TWO OR THREE COLUMNS'.")
    columns: List[Dict[str, str]] = Field(..., description="An array of 1 to 6 objects, each representing a column with its own title and description. Default: [{'title': 'Yellow', 'description': 'Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange.'}, {'title': 'Blue', 'description': 'Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum.'}, {'title': 'Red', 'description': 'Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage.'}].")
    font_family_heading: str = Field(default="'Patrick Hand', 'Inter', cursive", description="The handwritten-style font for the main title.")
    font_family_body: str = Field(default="'Lato', 'Inter', sans-serif", description="The standard font for the column titles and text.")
    text_color: str = Field(default="#34495E", description="The color for all text elements.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the repeating paper texture background.")

class GenerateTextWithImageSlideInput(BaseModel):
    """Input schema for generate_text_with_image_slide."""
    title: str = Field(..., description="The introductory headline for the text column, styled to be smaller. Default: 'Tiltle'.")
    text_content: str = Field(..., description="The main paragraph or body text, displayed in a large font to be the central focus of the text column. Default: 'Content.'.")
    image_url: str = Field(default="https://images.pexels.com/photos/1778412/pexels-photo-1778412.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", description="URL for the full-height image on the right side.")
    font_family_heading: str = Field(default="'Patrick Hand', 'Inter', cursive", description="The handwritten-style font for the title.")
    font_family_body: str = Field(default="'Lato', 'Inter', sans-serif", description="The standard font for the body text.")
    text_color: str = Field(default="#34495E", description="The color for all text elements.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the repeating paper texture background.")
    doodle_border_url: str = Field(default="https://i.imgur.com/Qy2O1vN.png", description="URL for the seamless doodle image used as a border at the bottom.")

class GenerateInstructionsSlideInput(BaseModel):
    """Input schema for generate_instructions_slide."""
    main_title: str = Field(..., description="The main title displayed in the header bar. Default: 'TOPIC'.")
    columns: List[Dict[str, Union[str, List[str]]]] = Field(..., description="An array of exactly 3 objects, each representing a column. Each object should have 'title' and 'list_items' keys. The content is styled with large fonts for easy reading. Default: [{'title': 'TOPIC ONE', 'list_items': ['First instruction point.', 'Second instruction point.', 'Third instruction point.']}, {'title': 'TOPIC TWO', 'list_items': ['First instruction point.', 'Second instruction point.', 'Third instruction point.']}, {'title': 'TOPIC THREE', 'list_items': ['First instruction point.', 'Second instruction point.', 'Third instruction point.']}].")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="Font family for all text elements.")
    header_primary_color: str = Field(default="#4F46E5", description="The primary (brighter) color for the header.")
    header_secondary_color: str = Field(default="#1E293B", description="The secondary (darker) color for the header accent.")
    header_text_color: str = Field(default="#FFFFFF", description="Text color for the header.")
    body_title_color: str = Field(default="#1E293B", description="Text color for the column titles.")
    body_text_color: str = Field(default="#333333", description="Text color for the list items.")

class GenerateGeometricSplitContentSlideInput(BaseModel):
    """Input schema for generate_geometric_split_content_slide."""
    main_title: str = Field(..., description="The main title for the slide's content. Default: 'You can also split your content'.")
    columns: List[Dict[str, str]] = Field(..., description="""An array of objects, where each object represents a column. Default: [
        {"title": "White", "description": "Is the color of milk and fresh snow, the color produced by the combination of all the colors of the visible spectrum."},
        {"title": "Black", "description": "Is the color of ebony and of outer space. It has been the symbolic color of elegance, solemnity and authority."}
    ]""")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for all text elements.")

class GenerateGeometricSplitContentSlide2Input(BaseModel):
    """Input schema for generate_geometric_split_content_slide_2."""
    main_title: str = Field(..., description="The main title for the slide's content. Default: 'In two or three columns'.")
    columns: List[Dict[str, str]] = Field(..., description="""An array of objects, where each object represents a column. Default: [
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."}
    ]""")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for all text elements.")

class GenerateGeometricImageContentSlideInput(BaseModel):
    """Input schema for generate_geometric_image_content_slide."""
    image_url: str = Field(default="https://images.unsplash.com/photo-1557804506-669a67965ba0?q=80&w=2574&auto=format&fit=crop", description="The URL for the main image to be displayed in the custom-shaped container.")
    main_title: str = Field(..., description="The main title for the slide. Use a `<span class='highlight'>` tag to highlight a specific word. Default: 'A picture is worth a <span class='highlight'>thousand</span> words'.")
    description: str = Field(..., description="The paragraph of text that describes or complements the image. Default: 'A complex idea can be conveyed with just a single still image, namely making it possible to absorb large amounts of data quickly.'.")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for the non-highlighted text.")

class GenerateGeometricContentSlideInput(BaseModel):
    """Input schema for generate_geometric_content_slide."""
    main_title: str = Field(..., description="The main title for the content slide, rendered in extra-bold weight. Default: 'Our Core Strategy'.")
    list_items: List[str] = Field(..., description="A list of strings for the bullet points. Each string will be a separate list item rendered in semi-bold weight. Default: ['Focus on <b><i><u><span style=\'color:#A3E635;\'>user-centric design</span></u></i></b>.', 'Innovate with purpose and clarity.', 'Build for <b><i><u><span style=\'color:#A3E635;\'>scalability and performance</span></u></i></b>.']")
    concluding_text: str = Field(..., description="A final sentence or paragraph displayed below the list, rendered in semi-bold weight. Default: 'These principles guide our every move forward.'.")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="The font family for all text elements. Should support weights 600 and 800.")
    bg_color: str = Field(default="#2B233D", description="The dark background color of the slide.")
    text_color: str = Field(default="#E5E7EB", description="The main color for alls text elements.")
    bullet_color: str = Field(default="#FBBF24", description="The accent color for the chevron bullet points.")

class GenerateGeometricGridSlideInput(BaseModel):
    """Input schema for generate_geometric_grid_slide."""
    main_title: str = Field(..., description="The main title for the slide, displayed above the grid. Default: 'Let's review some concepts'.")
    grid_items: List[Dict[str, str]] = Field(..., description="""An array of exactly 6 objects, where each object populates a cell in the 2x3 grid. Default: [
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."},
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."}
    ]""")
    font_family: str = Field(default="'Poppins', 'Inter', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for all text elements.")

class GenerateMemphisContentSlideInput(BaseModel):
    """Input schema for generate_memphis_content_slide."""
    main_title: str = Field(..., description="The main title of the slide, displayed in the top panel. Default: 'This is a slide title'.")
    list_items: List[str] = Field(..., description="A list of strings for the bullet points in the bottom panel. Default: ['Here you have a list of items', 'And some text', 'But remember not to overload your slides with content'].")
    concluding_text: str = Field(..., description="A final sentence or paragraph displayed below the list. Default: 'Your audience will listen to you or read the content, but won't do both.'.")
    font_family_title: str = Field(default="'Lora', 'Inter', serif", description="The elegant, serif font for the main title.")
    font_family_body: str = Field(default="'Source Code Pro', monospace", description="The monospace font for the body content, giving it a techy feel.")
    top_panel_bg: str = Field(default="#19114B", description="The background color for the top half of the slide.")
    bottom_panel_bg: str = Field(default="#403271", description="The background color for the bottom half of the slide.")
    palette: List[str] = Field(default=["#F87171", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"], description="A list of 5 colors used for the various decorative shapes and accents.")

class GenerateMemphisMulticolumnSlideInput(BaseModel):
    """Input schema for generate_memphis_multicolumn_slide."""
    main_title: str = Field(..., description="The main title for the slide, displayed in the top panel. Default: 'In two or three columns'.")
    columns: List[Dict[str, str]] = Field(..., description="""An array of objects for the content columns in the bottom panel. Default: [
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."}
    ]""")
    font_family_title: str = Field(default="'Lora', 'Inter', serif", description="The elegant, serif font for the main title.")
    font_family_body: str = Field(default="'Source Code Pro', monospace", description="The monospace font for the column content.")
    top_panel_bg: str = Field(default="#19114B", description="The background color for the top panel.")
    bottom_panel_bg: str = Field(default="#403271", description="The background color for the bottom panel.")
    palette: List[str] = Field(default=["#F43F5E", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"], description="A list of 5 colors used for the various decorative shapes and accents.")

class GenerateMemphisGridSlideInput(BaseModel):
    """Input schema for generate_memphis_grid_slide."""
    main_title: str = Field(..., description="The main title for the slide, displayed in the top panel. Default: 'Let's review some concepts'.")
    grid_items: List[Dict[str, str]] = Field(..., description="""An array of exactly 6 objects, where each object populates a cell in the 2x3 grid. Default: '[
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."},
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."}
    ]""")
    font_family_title: str = Field(default="'Lora', 'Inter', serif", description="The elegant, serif font for the main title.")
    font_family_body: str = Field(default="'Source Code Pro', monospace", description="The monospace font for the grid content.")
    top_panel_bg: str = Field(default="#19114B", description="The background color for the top panel.")
    bottom_panel_bg: str = Field(default="#403271", description="The background color for the bottom panel.")
    palette: List[str] = Field(default=["#F43F5E", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"], description="A list of 5 colors used for the various decorative shapes and accents.")

class GeneratePremiumAbstractSlideInput(BaseModel):
    """Input schema for generate_premium_abstract_slide."""
    main_title: str = Field(..., description="The main title of the slide. Default: 'HR Management'.")
    content_paragraphs: List[str] = Field(..., description=f"""A list of strings for body text. Default: [
        "We foster a dynamic and supportive work environment where every individual can thrive. Our approach integrates technology and human-centric policies to build a resilient and engaged workforce.",
        "From talent acquisition to professional development, our comprehensive strategies ensure that our people are our greatest asset, driving innovation and success."
    ]""")
    bg_color: str = Field(default="#F8FAFC", description="The base background color (hex code).")
    aurora_color_1: str = Field(default="#FBCFE8", description="First color (hex code) for the aurora gradient effect.")
    aurora_color_2: str = Field(default="#CFFAFE", description="Second color (hex code) for the aurora gradient effect.")
    aurora_color_3: str = Field(default="#DDD6FE", description="Third color (hex code) for the aurora gradient effect.")
    title_color: str = Field(default="#881337", description="Color for the main title (hex code).")
    text_color: str = Field(default="#334155", description="Color for the paragraph text (hex code).")
    enable_animation: Optional[bool] = Field(default=True, description="Whether to enable subtle loading animations. Default: True.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show a subtle finishing border around the slide. Default: True.")
    font_family_title: str = Field(default="Poppins", description="Font family for the title from Google Fonts.")
    font_family_content: str = Field(default="Inter", description="Font family for the content from Google Fonts.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

class GenerateMethodologySlideInput(BaseModel):
    """Input schema for generate_methodology_slide"""
    title: str = Field(..., description="Main title text for the slide header. Default: 'Research Methodology'.")
    title_color: str = Field(default="#000000", description="Color for the main title")
    accent_color: str = Field(default="#C9A86A", description="Color for accent elements (bar, circles, method boxes)")
    qualitative_title: str = Field(..., description="Title for the qualitative methods section. Default: 'Qualitative Methods'.")
    qualitative_text: str = Field(..., description="Description text for qualitative methods. Default: 'Qualitative research methods involve collecting and analyzing non-numerical data to explore the underlying motivations, perceptions, and behaviors of individuals. In our research proposal, qualitative methods will be utilized to gain in-depth insights into consumer preferences, attitudes, and experiences related to the new product.'")
    quantitative_title: str = Field(..., description="Title for the quantitative methods section. Default: 'Quantitative Methods'.")
    quantitative_text: str = Field(..., description="Description text for quantitative methods. Default: 'Quantitative research methods involve collecting and analyzing numerical data to quantify relationships, trends, and patterns. In our research proposal, quantitative methods will be employed to measure the prevalence, frequency, and magnitude of certain phenomena related to the new product.'")
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2340&auto=format&fit=crop",
        description="URL for the professional image displayed on the right side"
    )
    bg_color: str = Field(default="#F5F5F5", description="Background color for the slide")
    font_family: str = Field(default="'Inter', sans-serif", description="Font family for all text on the slide")
    custom_css: str = Field(default="", description="Additional custom CSS for advanced styling")

class GeneratePlanningPhaseSlideInput(BaseModel):
    """Input schema for generate_planning_phase_slide"""
    title: str = Field(default="Planning Phase", description="Main title text for the slide header.")
    title_color: str = Field(default="#C5E898", description="Color for the title (default: light yellow-green)")
    bg_color: str = Field(default="#1A4D4D", description="Background color (default: dark teal)")
    marker_light_color: str = Field(default="#C5E898", description="Color for light markers")
    marker_dark_color: str = Field(default="#4ECDC4", description="Color for dark markers")
    phases: List[Dict[str, str]] = Field(default=[
        {'name': 'Planning', 'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.'},
        {'name': 'Analysis', 'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.'},
        {'name': 'Design', 'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.'},
        {'name': 'Implementation', 'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.'}
    ], description="List of 4 phase dictionaries, each with 'name' and 'description' keys. Icons and colors are automatically assigned in sequence: brain (light), checklist (dark), design (light), puzzle (dark).")
    timeline_color: str = Field(default="#FFFFFF", description="Color for the timeline line and dots")
    custom_css: str = Field(default="", description="Additional custom CSS to inject")

# === SLIDE GIỚI THIỆU TEAM CLASSES ===

class GenerateTeamSlideInput(BaseModel):
    """Input schema for generate_team_slide."""
    main_title: str = Field(..., description="The main title, displayed in the smaller, diagonal accent area. Default: 'Our Team'.")
    team_members: List[Dict[str, str]] = Field(..., description="Array of team member objects, each displayed in a large, professional card. Each member should have 'name', 'role', and 'image_url' keys. Recommended 3 members for this layout. Default: [{'name': 'Alex Johnson', 'role': 'Lead Developer', 'image_url': 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?q=80&w=1780&auto=format=fit=crop'}, {'name': 'Maria Garcia', 'role': 'Product Manager', 'image_url': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1887&auto=format=fit=crop'}, {'name': 'James Smith', 'role': 'UX/UI Designer', 'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1887&auto=format=fit=crop'}].")
    font_family: str = Field(default="'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", description="Font family for all text elements.")
    accent_bg_color: str = Field(default="#14B8A6", description="Background color for the diagonal accent area (teal).")
    main_bg_color: str = Field(default="#F8FAFC", description="Background color for the main content area where team cards are displayed (off-white).")
    title_color: str = Field(default="#FFFFFF", description="Text color for the main title.")
    name_color: str = Field(default="#111827", description="Text color for team member names (dark gray).")
    role_color: str = Field(default="#6B7280", description="Text color for team member roles (neutral gray).")

class GenerateColorfulTeamGridSlideInput(BaseModel):
    """Input schema for generate_colorful_team_grid_slide."""
    main_title: str = Field(..., description="The large title displayed in the left column. Default: 'Add a Team Members Page'.")
    subtitle: str = Field(..., description="The smaller subtitle text below the main title.")
    team_members: List[Dict[str, str]] = Field(..., description="An array of exactly 4 objects, each containing details for one team member with 'name', 'role', 'image_url', and 'color' keys. Default: [{'name': 'Olivia Chen', 'role': 'Lead Designer', 'image_url': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1887&auto=format=fit=crop', 'color': '#8A44A1'}, {'name': 'Ben Carter', 'role': 'Frontend Developer', 'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1887&auto=format=fit=crop', 'color': '#2E9A94'}, {'name': 'Aisha Khan', 'role': 'Project Manager', 'image_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1887&auto=format=fit=crop', 'color': '#D93B58'}, {'name': 'Leo Martinez', 'role': 'Marketing Head', 'image_url': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=1887&auto=format=fit=crop', 'color': '#F3C314'}].")
    font_family: str = Field(default="'Montserrat', 'Inter', sans-serif", description="Font family for all text elements.")
    bg_color: str = Field(default="#F8FAFC", description="Background color of the slide.")
    title_color: str = Field(default="#111827", description="Text color for the main title.")
    subtitle_color: str = Field(default=None, description="Text color for the subtitle.")
    card_text_color: str = Field(default="#1F2937", description="Text color for the name and role on the cards.")

class GenerateCorporateTeamSlideInput(BaseModel):
    """Input schema for generate_corporate_team_slide."""
    main_title: str = Field(..., description="The main title for the slide, e.g., 'Our Creative Team'. Default: 'Our Creative Team'.")
    team_members: List[Dict[str, str]] = Field(..., description="An array of objects, each representing a team member with their own photo. Default: [{'name': 'Olivia Chen', 'role': 'Lead Designer', 'image_url': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1887&auto=format=fit=crop'}, {'name': 'Ben Carter', 'role': 'Photographer', 'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1887&auto=format=fit=crop'}, {'name': 'Aisha Khan', 'role': 'Content Strategist', 'image_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1887&auto=format=fit=crop'}, {'name': 'Leo Martinez', 'role': 'Illustrator', 'image_url': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=1887&auto=format=fit=crop'}]")
    font_family_heading: str = Field(default="'Patrick Hand', 'Inter', cursive", description="The handwritten-style font for the main title and member names.")
    font_family_body: str = Field(default="'Lato', 'Inter', sans-serif", description="The standard font for the member roles.")
    text_color: str = Field(default="#4A403A", description="The main text color for names.")
    role_color: str = Field(default="#6B7280", description="The secondary text color for roles.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the repeating paper texture background.")

# === SLIDE CẢM ƠN CLASSES ===

class GenerateThankYouSlide3Input(BaseModel):
    """Input schema for generate_thank_you_slide_3."""
    main_title: str = Field(..., description="Main title text displayed prominently. Default: 'THANK YOU'.")
    phone_number: str = Field(default="123-456-7890", description="Phone number to display.")
    email: str = Field(default="hello@reallygreatsite.com", description="Email address to display.")
    show_phone: Optional[bool] = Field(default=True, description="Whether to show phone number. Default: True.")
    show_email: Optional[bool] = Field(default=True, description="Whether to show email address. Default: True.")
    background_gradient_start: str = Field(default="#4A90E2", description="Starting color of background gradient.")
    background_gradient_end: str = Field(default="#2E5BBA", description="Ending color of background gradient.")
    main_title_color: str = Field(default="#FFFFFF", description="Color of the main title text.")
    contact_text_color: str = Field(default="#FFFFFF", description="Color of contact information text.")
    contact_icon_color: str = Field(default="#FFFFFF", description="Color of contact icons.")
    border_color: str = Field(default="rgba(255, 255, 255, 0.4)", description="Color of the border frame.")
    geometric_shape_colors: List[str] = Field(default=[], description="List of colors for geometric shapes. Default: 4 rgba colors with transparency.")
    font_family: str = Field(default="Segoe UI, Arial, sans-serif", description="Font family for all text elements.")
    main_title_font_weight: str = Field(default="700", description="Font weight of the main title.")
    main_title_letter_spacing: str = Field(default="0.1em", description="Letter spacing of the main title.")
    contact_font_weight: str = Field(default="400", description="Font weight of contact information.")
    contact_margin_top: str = Field(default="60px", description="Top margin for contact section.")
    contact_gap: str = Field(default="40px", description="Gap between contact items.")
    slide_padding: str = Field(default="60px", description="Padding around the slide.")
    border_frame_padding: str = Field(default="80px", description="Padding inside the border frame.")
    border_style: str = Field(default="2px solid", description="Style of the border frame.")
    border_radius: str = Field(default="8px", description="Border radius of the frame.")
    show_geometric_shapes: Optional[bool] = Field(default=True, description="Whether to show geometric background shapes. Default: True.")
    shape_animation: Optional[bool] = Field(default=True, description="Whether to animate geometric shapes. Default: True.")
    phone_icon: str = Field(default="📞", description="Icon for phone number.")
    email_icon: str = Field(default="✉️", description="Icon for email.")
    icon_margin_right: str = Field(default="12px", description="Right margin for icons.")
    additional_css: str = Field(default="''", description="Additional CSS to include.")

class GenerateCorporateThankYouSlideInput(BaseModel):
    """Input schema for generate_corporate_thank_you_slide."""
    thanks_text: str = Field(default="THANK YOU FOR WACTCHING!", description="The main closing message, e.g., 'THANKS!'. .")
    font_family: str = Field(default="'Montserrat', 'Inter', sans-serif", description="The font family for the text.")
    accent_color: str = Field(default="#F97316", description="The primary accent color for the right panel and the 'Thanks' text.")
    shadow_color: str = Field(default="#EA580C", description="The secondary (darker) accent color for the panel behind.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small smiley icon.")

class GenerateBusinessThankYouSlideInput(BaseModel):
    """Input schema for generate_business_thank_you_slide."""
    main_text: str = Field(default="THANK YOU", description="Main thank you text (e.g., 'THANK YOU').")
    subtitle: str = Field(default="For your attention and time", description="Subtitle text below main text.")
    main_text_color: str = Field(default="#0056d2", description="Color for main text (default: blue).")
    subtitle_color: str = Field(default="#666666", description="Color for subtitle text.")
    accent_color: str = Field(default="#0056d2", description="Color for decorative D-shapes.")
    main_font: str = Field(default="Arial, sans-serif", description="Font family for main text.")
    subtitle_font: str = Field(default="Arial, sans-serif", description="Font family for subtitle.")
class GenerateThankYouSlide4Input(BaseModel):
    """Input schema for generate_thank_you_slide_4 (speech bubble thank you slide)."""
    main_text: str = Field(default="THANK YOU!", description="The thank you message text displayed in the speech bubble.")
    bg_color: str = Field(default="#5B9BD5", description="Background gradient start color. Default: blue.")
    bg_gradient_to: str = Field(default="#A8D8F0", description="Background gradient end color. Default: light blue.")
    text_color: str = Field(default="#2C5F8D", description="Color of the thank you text.")
    bubble_bg_color: str = Field(default="#FFFFFF", description="Background color of the speech bubble. Default: white.")
    font_family: str = Field(default="Arial, sans-serif", description="Font family for the thank you text.")
    show_speech_tail: bool = Field(default=True, description="Whether to show the speech bubble tail pointing downward.")
    custom_css: str = Field(default="", description="Additional custom CSS styles to apply.")

class GenerateThankYouDecorativeSlideInput(BaseModel):
    """Input schema for generate_thank_you_decorative_slide (decorative thank you slide with dots)."""
    main_text: str = Field(default="THANK YOU!", description="Main thank you text displayed in large, bold letters.")
    bg_color: str = Field(default="#2B5FA6", description="Background gradient start color. Default: deep blue.")
    bg_gradient_to: str = Field(default="#4A90E2", description="Background gradient end color. Default: lighter blue.")
    text_color: str = Field(default="#FFFFFF", description="Color of the main text. Default: white.")
    show_dots: Optional[bool] = Field(default=True, description="Whether to show decorative dots. Default: True.")
    num_dots: int = Field(default=25, description="Number of decorative dots to display. Default: 25.")
    custom_css: str = Field(default="", description="Additional custom CSS styles to apply.")

class GenerateWatercolorThankYouSlideInput(BaseModel):
    """Input schema for generate_watercolor_thank_you_slide (watercolor style thank you slide)."""
    title: str = Field(default="Thank You", description="Main thank you text displayed in elegant script font.")
    bg_color: str = Field(default="#f5f5f5", description="Background color of the slide. Default: light gray.")
    text_color: str = Field(default="#1e3a5f", description="Color of the main title text. Default: dark blue.")
    watercolor_color: str = Field(default="#4dd0e1", description="Color of the watercolor splash effect. Default: cyan.")
    watercolor_opacity: float = Field(default=0.6, description="Opacity of the watercolor effect (0.0 to 1.0). Default: 0.6.")
    font_family: str = Field(default="'Brush Script MT', cursive, serif", description="Font family for the title. Default: cursive/script style.")
    show_watercolor: Optional[bool] = Field(default=True, description="Whether to show watercolor background effects. Default: True.")
    custom_css: str = Field(default="", description="Additional custom CSS styles to apply.")
    
class GenerateThankYouSlide5Input(BaseModel):
    """Input schema for generate_thank_you_slide_5 (geometric thank you slide with circles and corner shapes)."""
    main_text: str = Field(default="Thank you!", description="Main text content displayed in the center.")
    bg_color: str = Field(default="#f5f5f5", description="Background color of the slide. Default: off-white.")
    text_color: str = Field(default="#2d3748", description="Color of the main text. Default: dark gray.")
    circle_color: str = Field(default="#fbbf24", description="Color of decorative circles. Default: yellow.")
    corner_shape_color: str = Field(default="#2c5f6f", description="Color of corner quarter-circle shapes. Default: dark teal.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show the border frame. Default: True.")
    border_color: str = Field(default="#1a1a1a", description="Color of the border frame. Default: black.")
    show_corner_circles: Optional[bool] = Field(default=True, description="Whether to show decorative circles. Default: True.")
    show_corner_shapes: Optional[bool] = Field(default=True, description="Whether to show corner quarter-circle shapes. Default: True.")
    custom_css: str = Field(default="", description="Additional custom CSS styles to apply.")

class GenerateThankYouSlide6Input(BaseModel):
    """Input schema for generate_thank_you_slide_6 (elegant thank you slide with decorative sunburst patterns and olive branches)."""
    main_text: str = Field(default="Thank you", description="Main text to display. Default: 'Thank you'.")
    bg_color: str = Field(default="#F5E6D3", description="Background color of the slide. Default: beige (#F5E6D3).")
    text_color: str = Field(default="#1a3a52", description="Color of the main text. Default: navy blue (#1a3a52).")
    show_decorative_elements: Optional[bool] = Field(default=True, description="Whether to show sunburst patterns and decorative dots. Default: True.")
    show_olive_branches: Optional[bool] = Field(default=True, description="Whether to show olive branch decorations. Default: True.")
    font_family: str = Field(default="'Dancing Script', 'Brush Script MT', cursive", description="Font family for the main text. Default: Dancing Script.")
    custom_css: str = Field(default="", description="Additional custom CSS styles to apply.")

class GenerateThankYouSlide7Input(BaseModel):
    """Input schema for generate_thank_you_slide_7 (elegant minimalist thank you slide)."""
    main_text: str = Field(default="THANK YOU!", description="Main text to display. Default: 'THANK YOU!'.")
    bg_color: str = Field(default="#F5F3F0", description="Background color of the slide. Default: light warm gray (#F5F3F0).")
    text_color: str = Field(default="#7A6350", description="Color of the main text. Default: brown/taupe (#7A6350).")
    font_family: str = Field(default="'Playfair Display', 'Georgia', serif", description="Font family for the main text. Default: Playfair Display.")
INTRO_TOOLS = [
    # === SLIDE INTRO ===
    StructuredTool.from_function(
        func=generate_title_slide,
        name="generate_title_slide",
        description="Generates a professional title slide with a blue gradient background, geometric shapes, and optional city skyline.",
        args_schema=GenerateTitleSlideInput
    ),
    StructuredTool.from_function(
        func=generate_introduction_slide,
        name="generate_introduction_slide",
        description="Generates a professional introduction slide with gradient background and decorative elements.",
        args_schema=GenerateIntroductionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_intro_slide1,
        name="generate_intro_slide1",
        description="Generates an HTML introduction slide with a  main title section on the left and an image on the right.",
        args_schema=GenerateIntroSlide1Input
    ),
    StructuredTool.from_function(
        func=generate_elegant_intro_slide,
        name="generate_elegant_intro_slide",
        description="Generates an elegant Introduction or Title slide, featuring an asymmetrical two-column layout with a large title on the left and a framed image on the right. Its unique features are the beautiful, golden botanical frame that adorns the image's bottom-right corner and a subtle cluster of stars at the top-left, creating a warm and celebratory feel. Ideal for presentation openers, chapter dividers, personal introductions, or event invitations.",
        args_schema=GenerateElegantIntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_inspirational_quote_slide,
        name="generate_inspirational_quote_slide",
        description="Generates a bright, airy, and sophisticated Quote Slide. It features a full-screen background image, elegant serif typography, and a semi-transparent, blurred content card to ensure readability. The design is framed by large, subtle decorative quotation marks, making it perfect for impactful opening statements, highlighting key messages, or as an elegant closing slide.",
        args_schema=GenerateInspirationalQuoteSlideInput
    ),
    StructuredTool.from_function(
        func=generate_title_slide_2,
        name="generate_title_slide_2",
        description="Generates a Introductory or Title Slide. It's ideal for starting a business, technology, or data-focused presentation. Its unique characteristics include a sharp diagonal split and a layered color panel. The title can optionally contain a highlighted word by using HTML tags.",
        args_schema=GenerateTitleSlide2Input
    ),
    StructuredTool.from_function(
        func=generate_business_intro_slide,
        name="generate_business_intro_slide",
        description="Generates a clean business presentation intro slide with centered text, decorative D-shapes on sides, and subtle grid background pattern.",
        args_schema=GenerateBusinessIntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_dynamic_intro_slide,
        name="generate_dynamic_intro_slide",
        description="Generates a  Introductory or Title slide. This is a great slide for opening a presentation or starting a new section. Its unique characteristics include a bold, asymmetrical layout with a full-height image on the right, and a solid color block on the left that features an angled cutout. The color block contains a large title, a subtitle, and abstract geometric decorations in the footer area (arcs and dots).",
        args_schema=GenerateDynamicIntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_big_concept_slide,
        name="generate_big_concept_slide",
        description="Generates a high-impact **Content Slide** of the 'Big Concept' or 'Emphasis' type. It is designed to highlight a single, major idea using a very large title and a prominent thematic illustration (e.g., a planet and stars), while maintaining the 'geometric theme'. This slide is perfect for introducing key pillars, core values, or pivotal moments in a presentation.",
        args_schema=GenerateBigConceptSlideInput
    ),
    StructuredTool.from_function(
        func=generate_elegant_agenda_slide,
        name="generate_elegant_agenda_slide",
        description="Generates an elegant, minimalist agenda or table of contents slide. Features a two-column layout with a framed image on the left and a text list on the right. The design uses a classic serif font for the title and a clean sans-serif for the body, making it ideal for professional, corporate, or academic presentations.",
        args_schema=GenerateElegantAgendaSlideInput
    ),
    StructuredTool.from_function(
        func=generate_playful_title_slide,
        name="generate_playful_title_slide",
        description="Generates a friendly, hand-drawn style title slide. Features a large, charming illustration (like a penguin) and playful typography. The layout consists of a main colored panel and a smaller strip at the bottom. Perfect for educational content, children's presentations, or any topic needing a warm, approachable feel.",
        args_schema=GeneratePlayfulTitleSlideInput
    ),
    StructuredTool.from_function(
        func=generate_minimalist_title_slide,
        name="generate_minimalist_title_slide",
        description="Generates a stunning, high-tech **Title Slide** for opening a presentation. This slide features a sophisticated dark theme, impactful typography, and a large, glowing, animated 'portal' on the right. The layout is modern and asymmetrical, making it perfect for technology, innovation, or futuristic topics where a strong, memorable first impression is crucial.",
        args_schema=GenerateMinimalistTitleSlideInput
    ),
    StructuredTool.from_function(
        func=generate_mission_slide,
        name="generate_mission_slide",
        description="Generates a Content Slide with a two-column, side-by-side layout, specifically designed for presenting a Mission, Vision, or Introduction. This layout is adjusted to emphasize the written content by making the text column significantly wider than the image column. The visual style is warm and elegant, using a beige and brown color palette, making it ideal for in-depth explanations where the text is the main focus.",
        args_schema=GenerateMissionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_training_intro_slide,
        name="generate_training_intro_slide",
        description="Generates a training introduction slide with dark background and bottom image. This slide features a two-section layout: top section with dark background containing title and description text, and bottom section with a full-width training/professional image. Perfect for training presentations, educational content, or professional workshops. Uses responsive design with automatic font scaling for different screen sizes.",
        args_schema=GenerateTrainingIntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_employee_intro_slide,
        name="generate_employee_intro_slide",
        description="Generates a professional introduction slide for Employee Intro Planning. Features a modern design with a large main title, descriptive subtitle, and decorative overlapping circles on the right side. Uses a professional green color scheme with radial gradients, shadows, and blur effects. Perfect for corporate presentations about workforce planning, organizational changes, HR strategies, or employee movement topics.",
        args_schema=GenerateEmployeeIntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_research_proposal_slide,
        name="generate_research_proposal_slide",
        description="Generates a minimalist research proposal title slide with geometric decorations. Features a clean, professional design with large bold title, subtitle in accent color, and scientific decorative elements including crosshair, geometric shapes (triangle, square, hexagon), and data points on a subtle grid background. Perfect for academic, research, or technical presentations requiring a sophisticated, data-driven aesthetic.",
        args_schema=GenerateResearchProposalSlideInput
    ),
    StructuredTool.from_function(
        func=generate_company_mission_slide,
        name="generate_company_mission_slide",
        description="Generates a professional company mission slide with numbered items. Features a two-column layout with main title on the left (35% width) and a blue mission panel on the right (65% width) that extends to the edge. Mission items are displayed vertically with large numbered circles positioned outside the panel to the left. Perfect for presenting company missions, values, core principles, or strategic objectives in a clean, modern design.",
        args_schema=GenerateCompanyMissionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_title_slide_3,
        name="generate_title_slide_3",
        description="Generates a festive and cheerful **Title or Introduction Slide** with a Christmas Lights theme. Features decorative string lights with colorful bulbs draped across the top, sparkling star accents scattered throughout, and warm holiday typography. The slide uses a cozy beige background with red title text and elegant serif fonts, creating a celebratory atmosphere perfect for holiday presentations, seasonal events, year-end reviews, or any presentation wanting a warm, festive touch.",
        args_schema=GenerateTitleSlide3Input
    ),
    StructuredTool.from_function(
        func=generate_minimalist_slide,
        name="generate_minimalist_slide",
        description="Generates an elegant and sophisticated **Title or Introduction Slide** with a minimalist design aesthetic using converter-compatible fixed positioning (1920x1080px). Features smooth decorative SVG curves in the top-left and bottom-right corners, horizontal line accents at top and bottom, and refined serif typography for the title (112px font) paired with clean sans-serif for the subtitle (26px font). Uses absolute positioning with pixel values instead of flexbox/responsive units for reliable HTML-to-absolute conversion. The warm beige/cream background creates a timeless, professional look perfect for business presentations, corporate meetings, consulting proposals, or any presentation requiring a clean, upscale, and distraction-free opening.",
        args_schema=GenerateMinimalistSlideInput
    ),
    StructuredTool.from_function(
        func=generate_title_slide_4,
        name="generate_title_slide_4",
        description="Generates a playful and modern **Title or Introduction Slide** with decorative geometric elements. Features a clean border frame with elegant corner curves, and colorful scattered shapes (circles and diamonds) in coral red, lavender, and black positioned at the corners and edges. The centered layout with bold sans-serif typography on a warm beige background creates a friendly yet professional aesthetic, perfect for creative presentations, design showcases, educational content, or any presentation needing a touch of visual interest while maintaining clarity and focus.",
        args_schema=GenerateTitleSlide4Input
    ),
    StructuredTool.from_function(
        func = generate_title_slide_5,
        name="generate_title_slide_5",
        description="Generates a warm and nostalgic **Title or Introduction Slide** with a notebook cover design aesthetic. Features a tilted polaroid-style photo frame with decorative hand-drawn doodles, a four-leaf clover icon, horizontal decorative lines at top and bottom, and personalized text elements in corners ('Our shared moments', year). The soft blue-gray background combined with elegant typography creates a scrapbook-like, memory-capturing feel. Perfect for personal presentations, photo albums, travel stories, memory collections, family events, or any presentation wanting an intimate, handcrafted, and sentimental opening that evokes cherished moments and personal connections.",
        args_schema=GenerateTitleSlide5Input,
    ),
    StructuredTool.from_function(
        func=generate_title_slide_6,
        name="generate_title_slide_6",
        description="Generates a playful and whimsical **Title or Introduction Slide** with a cartoon-style design using converter-compatible fixed positioning (1920x1080px). Features a rounded content box (1300x500px) with thick borders, soft pastel gradient background, fluffy white clouds floating at the top, and a cheerful flower character at the bottom-left corner. The design uses bold, friendly typography (68px title, 30px subtitle) with absolute positioning perfect for educational content, children's presentations, fun workshops, creative projects, or any presentation wanting a lighthearted, approachable, and joyful atmosphere that captures attention with its charming and inviting visual style.",
        args_schema=GenerateTitleSlide6Input,
    )
]

TRANSITION_TOOLS = [
    # === SLIDE CHUYỂN SLIDE ===
    StructuredTool.from_function(
        func=generate_geometric_transition_slide,
        name="generate_geometric_transition_slide",
        description="Generates a dynamic and modern **Transition or Section Header Slide**. Its most distinct characteristic is the use of vibrant, multi-colored geometric shapes (parallelograms) clustered in the corners. With a dark background and high-impact, centered text, this slide is perfect for introducing new sections in technology, creative, or modern corporate presentations.",
        args_schema=GenerateGeometricTransitionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_dusk_transition_slide,
        name="generate_dusk_transition_slide",
        description="Generates a minimalist, tech-focused Section Break or Transition Slide. It combines the dramatic dusk color scheme (purple-to-orange gradient) with the clean, modern aesthetic of a dot-grid background. This version removes the soft clouds/orbs for a more direct, uncluttered look, while keeping the animated rockets. It's perfect for marking new chapters in a technology, data, or corporate presentation that requires a sophisticated yet energetic visual.",
        args_schema=GenerateDuskTransitionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_memphis_transition_slide,
        name="generate_memphis_transition_slide",
        description="Generates a vibrant, retro 'Memphis-style' transition slide. Features a two-tone background, elegant typography, and a playful scattering of geometric shapes and patterns. Perfect for creative, design, or tech presentations that need a touch of personality.",
        args_schema=GenerateMemphisTransitionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_pushpin_section_header,
        name="generate_pushpin_section_header",
        description="Generates a minimalist and sophisticated **Title or Section Header Slide**. Its most distinctive feature is a large, central title that **elegantly intersects a horizontal decorative line**, flanked by two simple dots. This creates a clean, balanced, and high-end look, perfect for introducing new topics in a professional or creative presentation. (Note: The function name is a legacy from a previous design).",
        args_schema=GeneratePushpinSectionHeaderInput
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide,
        name="generate_section_header_slide",
        description="Generates a vibrant and dynamic Title or Section Header Slide. Its most distinctive feature is the animated 'geometric confetti' background, where sharp, minimalist shapes float upwards over a soft, aurora-like gradient. With its extra-large, centered title, this slide is perfect for creating a high-energy, modern opening or a memorable transition between topics.",
        args_schema=GenerateSectionHeaderSlideInput
    ),
    StructuredTool.from_function(
        func=generate_intro_slide,
        name="generate_intro_slide",
        description="Generates an HTML introduction slide with a  main title section on the left and an image on the right.",
        args_schema=GenerateIntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_research_proposal_transition_slide,
        name="generate_research_proposal_transition_slide",
        description="Generates a minimalist geometric transition slide with clean, professional aesthetic. Features a centered headline and subtitle with decorative geometric elements including a crosshair, shapes (triangle, square, hexagon), grid background overlay, and data points. Perfect for modern, technical, or research presentations requiring sophisticated section breaks.",
        args_schema=GenerateResearchProposalTransitionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_business_transition_slide,
        name="generate_business_transition_slide",
        description="Generates a clean business transition slide with centered text, decorative D-shapes on sides, and subtle grid background pattern. Features large uppercase headline and descriptive subtitle. Perfect for professional business presentations requiring clean section breaks.",
        args_schema=GenerateBusinessTransitionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide_5,
        name="generate_section_header_slide_5",
        description="Generates a split-design section header slide with title on left and decorative stripes on right. Features bold Playfair Display typography, a vertical stripe pattern, and a curved line decoration on a dark teal background. Perfect for creating elegant, architectural section dividers with a strong visual split and modern geometric aesthetic.",
        args_schema=GenerateSectionHeaderSlide5Input
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide_6,
        name="generate_section_header_slide_6",
        description="Generates a clean and elegant section header slide with centered content. Features a large title, decorative underline, and description text on a gradient background. Perfect for creating simple, professional section dividers or introduction slides with a minimalist, modern aesthetic.",
        args_schema=GenerateSectionHeaderSlide6Input
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide_8,
        name="generate_section_header_slide_8",
        description="Generates a cheerful balloon-themed section header slide with a modern, clean design. Features left-aligned title and subtitle text, with colorful balloon decorations (red, blue, yellow) positioned on the right side. Background uses a warm pastel gradient (peach to light pink) creating a bright, balanced, and festive atmosphere. No animations. Perfect for celebration-themed section dividers, party presentations, or any content requiring a fun, uplifting, and contemporary aesthetic.",
        args_schema=GenerateSectionHeaderSlide8Input
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide_9,
        name="generate_section_header_slide_9",
        description="Generates a modern section header slide with house SVG illustration container on the left and text on the right. Features a warm diagonal gradient background (light cream to warm brown), white text, and space for custom SVG artwork. Layout uses space-between alignment with SVG container (50% width) and content area (50% width). No animations. Perfect for visually enriched section dividers with custom illustrations or graphics.",
        args_schema=GenerateSectionHeaderSlide9Input
    ),
    
    StructuredTool.from_function(
        func=generate_section_header_slide_10,
        name="generate_section_header_slide_10",
        description="Generates a spiral-bound notebook-style slide with a realistic school/education aesthetic. Features a centered white notebook with spiral binding on the left (10 metal rings), horizontal ruled lines with light opacity, a vertical red margin line, bold title, and subtitle. Decorated with colorful bookmark sticky notes at the top edge (yellow and pink). Light green background. No animations. Perfect for educational or casual section dividers with a handwritten notebook feel.",
        args_schema=GenerateSectionHeaderSlide10Input
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide_12,
        name="generate_section_header_slide_12",
        description="Generates a minimalist question slide with clean design. Features a prominent question/title text on the left and a decorative pen SVG illustration with writing stroke on the bottom right. Light gray background for a professional, modern look. No animations. Perfect for Q&A sections, topic introduction slides, or thought-provoking questions with a clean, contemporary aesthetic.",
        args_schema=GenerateSectionHeaderSlide12Input
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide_13,
        name="generate_section_header_slide_13",
        description="Generates a modern section header slide with SVG illustration container on the right and text content on the left. Features a diagonal gradient background (white to light cyan), accent gradient at bottom left (peach/orange), and flexible layout with 55% text area and 45% SVG container. Text uses dark gray color with Roboto Mono font. Layout uses flexbox with space-between alignment for balanced composition. No animations. Perfect for visually enriched section dividers with custom SVG illustrations or graphics. The SVG container can hold any custom artwork.",
        args_schema=GenerateSectionHeaderSlide13Input
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide_15,
        name="generate_section_header_slide_15",
        description="Generates a Christmas-themed section header slide with festive gradient blobs and Christmas tree SVG illustration on the right. Features dark evergreen background, white text, and colorful festive gradient blobs (red, green, gold). Layout uses flexbox with text content on left (65% width) and SVG container on right (35% width). Text is large, italic, and bold. No animations. Perfect for holiday presentations and festive section dividers. Includes embedded Christmas tree SVG with ornaments and star.",
        args_schema=GenerateSectionHeaderSlide15Input
    )
]

CONTENT_TOOLS = [
    # === SLIDE CONTENT ===
    StructuredTool.from_function(
        func=generate_content_slide,
        name="generate_content_slide",
        description="Generates an HTML slide with a main title and a grid of numbered items, ideal for listing topics or points.",
        args_schema=GenerateContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_comparison_slide,
        name="generate_comparison_slide",
        description="Generates an HTML slide with a main title, two comparison columns with icons, and a matching border design.",
        args_schema=GenerateComparisonSlideInput
    ),
    StructuredTool.from_function(
        func=generate_process_slide,
        name="generate_process_slide",
        description="Generates an HTML slide with a main title and two process boxes connected by an arrow.",
        args_schema=GenerateProcessSlideInput
    ),
    StructuredTool.from_function(
        func=generate_process_steps_slide,
        name="generate_process_steps_slide",
        description="Generates a structured, multi-step process or plan slide. Features a three-column layout with a main title on a colored side panel, a vertical 'film strip' of images, and corresponding text descriptions for each step. The design is clean, elegant, and ideal for outlining strategies or project phases.",
        args_schema=GenerateProcessStepsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_icon_list_slide_2,
        name="generate_icon_list_slide_2",
        description="Generates a clean, minimalist slide for presenting solutions, features, or key points. It features a two-column layout with a large, elegant title on the left and a vertical list of icon-text pairs on the right. Ideal for corporate or business presentations requiring a sophisticated aesthetic.",
        args_schema=GenerateIconListSlide2Input
    ),
    StructuredTool.from_function(
        func=generate_image_cutout_list_slide,
        name="generate_image_cutout_list_slide",
        description="Generates a sophisticated list slide with a unique 'cut-out' effect, where the main content panel appears to sit on top of a continuous background image. Ideal for presenting key points, features, or agenda items in a modern, high-end style.",
        args_schema=GenerateImageCutoutListSlideInput
    ),
    StructuredTool.from_function(
        func=generate_body_slide2,
        name="generate_body_slide2",
        description="Generates an HTML slide with a main title, a large image on the left, and three content sections with icons on the right.",
        args_schema=GenerateBodySlide2Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide4,
        name="generate_body_slide4",
        description="Generates an HTML slide with a main title, a horizontal content bar, and three images with subtitles and content text.",
        args_schema=GenerateBodySlide4Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide5,
        name="generate_body_slide5",
        description="Generates an HTML slide with a main title, a 2x2 image grid on the left, and four content sections on the right.",
        args_schema=GenerateBodySlide5Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide7,
        name="generate_body_slide7",
        description="Generates an HTML slide with a main title, three vertical images on the left, and a subtitle with two content sections on the right, separated by a divider.",
        args_schema=GenerateBodySlide7Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide10,
        name="generate_body_slide10",
        description="Generates an HTML slide with a main title, a large image on the left, and three content sections with icons on the right.",
        args_schema=GenerateBodySlide10Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide11,
        name="generate_body_slide11",
        description="Generates an HTML slide with a main title and three content boxes with icons. Content fields support rich HTML formatting.",
        args_schema=GenerateBodySlide11Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide12,
        name="generate_body_slide12",
        description="Generates an HTML slide with a main title, a horizontal content bar, and three images with subtitles and content text.",
        args_schema=GenerateBodySlide12Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide15,
        name="generate_body_slide15",
        description="Generates an HTML slide with a main title, three vertical images on the left, and a subtitle with two content sections on the right, separated by a divider.",
        args_schema=GenerateBodySlide15Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide18,
        name="generate_body_slide18",
        description="Generates an HTML slide with a main title and two comparison columns separated by a dashed divider. Each column has an icon, title, and text content. The slide features a border design with accent color background.",
        args_schema=GenerateBodySlide18Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide19,
        name="generate_body_slide19",
        description="Generates an HTML slide with two columns containing multiple sections each. The left column has a colored background, while the right column is white with a border and includes icons for each section.",
        args_schema=GenerateBodySlide19Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide20,
        name="generate_body_slide20",
        description="Generates an HTML slide with a main title and two comparison columns separated by a dashed divider. Each column has an icon, title, and text content. The slide features a border design with accent color background.",
        args_schema=GenerateBodySlide20Input
    ),
    StructuredTool.from_function(
        func=generate_main_points_slide,
        name="generate_main_points_slide",
        description="Generate a professional main points slide with three columns featuring environmental/industrial icons (plastic bag, faucet, factory). Perfect for environmental presentations, sustainability topics, industrial processes, waste management discussions, or any three-point presentation requiring modern visual appeal.",
        args_schema=GenerateMainPointsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_elegant_points_slide,
        name="generate_elegant_points_slide",
        description="Generates a Content Slide designed to present four key points. This slide features an adjusted layout that intentionally de-emphasizes the main title to make the four content cards below the central focus. The visual style is bright, warm, and elegant, using an off-white background, floating cards with soft shadows, and decorative icons to introduce each point. It is ideal for presenting core values, key features, or strategic pillars where the details of the four points are most important.",
        args_schema=GenerateElegantPointsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_corporate_content_slide,
        name="generate_corporate_content_slide",
        description="Generates a bright and professional **Content Slide** with a dynamic diagonal layout. It features a large title on a vibrant, colored panel on the left, while the main content on the right is presented as a series of modern, numbered cards. The layout is **optimized for 2 to 4 items** to maintain a clean, balanced look. This slide is ideal for breaking down topics, listing key features, or presenting arguments in a structured, high-end, and visually engaging way.",
        args_schema=GenerateCorporateContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_split_content_slide,
        name="generate_split_content_slide",
        description="Generates a high-tech, dark-themed **Content Slide** designed for comparing two key points. This slide features a large central title and two prominent 'glassmorphism' style cards below, each with a glowing top border and a decorative icon. The layout is **strictly optimized for a two-column comparison** to maintain its balanced, modern aesthetic. Ideal for technology, strategy, or futuristic presentations.",
        args_schema=GenerateSplitContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_corporate_multicolumn_slide,
        name="generate_corporate_multicolumn_slide",
        description="Generates a professional Content Slide, designed for presenting information in two or three parallel columns. This tool maintains the modern corporate aesthetic with a dynamic diagonal split and a layered color panel. The main content area features a title with an icon, followed by the columns displayed in elegant cards with hover effects. Enhanced with larger typography, gradient backgrounds, and improved spacing for better visual impact. It's ideal for comparing features, presenting different viewpoints, or breaking down a topic into 2 or 3 key areas.",
        args_schema=GenerateCorporateMulticolumnSlideInput
    ),
    StructuredTool.from_function(
        func=generate_corporate_grid_slide,
        name="generate_corporate_grid_slide",
        description="Generates a Content Slide designed for presenting multiple items in a 2x3 grid layout. This tool maintains the modern corporate aesthetic with a dynamic diagonal split and a layered color panel. The main content area features a title with an icon, followed by a grid of six items displayed as interactive cards. Enhanced with larger typography, gradient backgrounds, hover effects, and improved spacing for better visual impact. This layout is optimized for presenting exactly six items, making it perfect for reviewing key concepts, displaying product features, or listing data points in an organized format.",
        args_schema=GenerateCorporateGridSlideInput
    ),
    StructuredTool.from_function(
        func=generate_business_overview_slide,
        name="generate_business_overview_slide",
        description="Generates a professional business overview slide with icon-content sections layout.",
        args_schema=GenerateBusinessOverviewSlideInput
    ),
    StructuredTool.from_function(
        func=generate_vision_mission_slide,
        name="generate_vision_mission_slide",
        description="Generates a professional vision and mission slide with split layout and numbered points.",
        args_schema=GenerateVisionMissionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_strategic_goals_slide,
        name="generate_strategic_goals_slide",
        description="Generates a professional strategic goals slide with numbered points and background image.",
        args_schema=GenerateStrategicGoalsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_service_roadmap_slide,
        name="generate_service_roadmap_slide",
        description="Generates a professional service roadmap slide with gradient background and decorative elements.",
        args_schema=GenerateServiceRoadmapSlideInput
    ),
    StructuredTool.from_function(
        func=generate_financial_projections_slide_dark,
        name="generate_financial_projections_slide_dark",
        description="Generates an HTML slide for financial projections with dark blue theme and three cards.",
        args_schema=GenerateFinancialProjectionsSlideDarkInput
    ),
    StructuredTool.from_function(
        func=generate_minimalist_tech_list_slide,
        name="generate_minimalist_tech_list_slide",
        description="Generates a bright, clean, and professional **Content Slide**. This slide is characterized by its large, highly-legible fonts and a modern, tech-inspired aesthetic. Key features include a subtle dot-grid background over a light gradient, a prominent decorative border on the left, and stylized circular bullet points. It's ideal for presenting key information, features, or principles in corporate or technology presentations where clarity and a polished look are paramount.",
        args_schema=GenerateMinimalistTechListSlideInput
    ),
    StructuredTool.from_function(
        func=generate_centered_tech_columns_slide,
        name="generate_centered_tech_columns_slide",
        description="Generates a clean, minimalist multi-column Content Slide, supporting up to 4 columns. This slide is ideal for comparing items in a corporate or tech-focused presentation. Its unique characteristics are a main title and a grid of columns, all centered on the page. The background features the minimalist tech style: a solid color with a dot grid and subtly appearing rockets, with no clouds or orbs.",
        args_schema=GenerateCenteredTechColumnsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_split_layout_list_slide,
        name="generate_split_layout_list_slide",
        description="Generates a professional Split-Layout List slide with a high-contrast design. Offers smart responsive font scaling by default, with optional overrides for fixed font sizes.",
        args_schema=GenerateSplitLayoutListSlideInput
    ),
    StructuredTool.from_function(
        func=generate_reference_slide,
        name="generate_reference_slide",
        description="Generates a modern and professional Content Slide. It features a high-contrast, two-column layout with a large text area on the left and a full-height image on the right. With its large, bold fonts and a vibrant accent divider, this slide is perfect for presenting key takeaways, sources, or contact information in a clear and visually engaging way.",
        args_schema=GenerateReferenceSlideInput
    ),
    StructuredTool.from_function(
        func=generate_icon_list_slide,
        name="generate_icon_list_slide",
        description="Generates a modern Content Slide with a two-column layout, specifically adjusted to emphasize a list of key points. The design features a smaller, minimalist title on the left and a prominent list of items on the right, where each point is highlighted by a large, uniformly colored icon. This slide is ideal for presenting core values, features, or steps where the details of the list are the primary focus.",
        args_schema=GenerateIconListSlideInput
    ),
    StructuredTool.from_function(
        func=generate_flexible_columns_slide,
        name="generate_flexible_columns_slide",
        description="Generates a versatile Content Slide, designed for the main body of a presentation. It is ideal for comparing products, listing features, or presenting multiple ideas side-by-side. Its clean, minimalist design features a notebook paper texture, top-aligned content, and a flexible grid that supports up to six columns, ensuring information is presented in a clear and organized manner.",
        args_schema=GenerateFlexibleColumnsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_text_with_image_slide,
        name="generate_text_with_image_slide",
        description="Generates a Content Slide for the main body of a presentation, featuring a doodle/notebook paper theme. This layout is specifically adjusted to emphasize a large block of text content on the left, with a smaller, handwritten-style title acting as an introduction. The right side features a full-height image. It's ideal for storytelling, educational content, or explaining a concept alongside a supporting visual.",
        args_schema=GenerateTextWithImageSlideInput
    ),
    StructuredTool.from_function(
        func=generate_instructions_slide,
        name="generate_instructions_slide",
        description="Generates a professional and highly legible Content Slide for instructions or feature lists. This slide is characterized by its clean, structured layout featuring a prominent two-tone header and a content area **strictly designed for a three-column layout to maintain visual balance.** It has been enhanced with **extra-large fonts and generous spacing** to ensure maximum readability and impact, making it ideal for presenting processes, guidelines, or key feature sets in a clear and modern way.",
        args_schema=GenerateInstructionsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_geometric_split_content_slide,
        name="generate_geometric_split_content_slide",
        description="Generates a **Content Slide** for comparing items in multiple columns (typically 2 or 3). This slide maintains the 'geometric theme' with a main title and a grid of content below. The layout is robustly designed to ensure decorative elements never overlap with the text, making it ideal for breaking down concepts, comparing features, or listing pros and cons.",
        args_schema=GenerateGeometricSplitContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_geometric_split_content_slide_2,
        name="generate_geometric_split_content_slide_2",
        description="Generates a **Content Slide** for comparing items in multiple columns (typically 2 or 3). This slide maintains the 'geometric theme' with a main title and a grid of content below. The layout is robustly designed to ensure decorative elements never overlap with the text, making it ideal for breaking down concepts, comparing features, or listing pros and cons.",
        args_schema=GenerateGeometricSplitContentSlide2Input
    ),
    StructuredTool.from_function(
        func=generate_geometric_image_content_slide,
        name="generate_geometric_image_content_slide",
        description="Generates a **Content Slide** with a prominent, custom-shaped image on the left and text on the right. This slide is part of the 'geometric theme' but uses more compact and subtle decorative shapes in the corners. It is ideal for visually illustrating a point or concept described in the text.",
        args_schema=GenerateGeometricImageContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_geometric_content_slide,
        name="generate_geometric_content_slide",
        description="Generates a **Content Slide** that matches the 'geometric theme'. It features subtle, colorful shapes in the corners and a dark background. The layout is correctly positioned to avoid overlap, and the text is intentionally made bolder for superior readability. It's the perfect companion to the geometric transition slide for presenting detailed points.",
        args_schema=GenerateGeometricContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_geometric_grid_slide,
        name="generate_geometric_grid_slide",
        description="Generates a **Content Slide** featuring a 2x3 grid, perfect for presenting six related concepts. This slide uses the 'geometric theme' with highly transparent decorative shapes to ensure they do not distract from the main text content. The layout is robust and prevents any overlap.",
        args_schema=GenerateGeometricGridSlideInput
    ),
    StructuredTool.from_function(
        func=generate_memphis_content_slide,
        name="generate_memphis_content_slide",
        description="Generates a  Content Slide with a distinctive 20/80 top-to-bottom panel ratio. The title is centered in the smaller top panel, while the main content is aligned to the top of the larger bottom panel. The slide is decorated with playful, retro geometric shapes, precisely positioned to match the sample.",
        args_schema=GenerateMemphisContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_memphis_multicolumn_slide,
        name="generate_memphis_multicolumn_slide",
        description="Generates a multi-column Content Slide with a 20/80 layout split. It's designed to present information in 2 or 3 columns within the larger bottom panel, while the title occupies the smaller top panel. The slide is decorated with an array of playful shapes, perfect for creative presentations.",
        args_schema=GenerateMemphisMulticolumnSlideInput
    ),
    StructuredTool.from_function(
        func=generate_memphis_grid_slide,
        name="generate_memphis_grid_slide",
        description="Generates a 'Memphis-style' content slide featuring a 2x3 grid. It uses the signature 20/80 panel layout and is specifically designed to display exactly six items. The playful decorative shapes are arranged to not interfere with the content, making it perfect for reviewing multiple concepts in a creative presentation.",
        args_schema=GenerateMemphisGridSlideInput
    ),
    StructuredTool.from_function(
        func=generate_premium_abstract_slide,
        name="generate_premium_abstract_slide",
        description="Generates a versatile content, introduction, or section divider slide. It features a premium, highly modern design with an 'aurora' gradient background and an abstract 'glassmorphism' graphic. Perfect for presenting key concepts, introducing a topic, or opening a new presentation section with a sophisticated, high-tech, and elegant first impression.",
        args_schema=GeneratePremiumAbstractSlideInput
    ),
    StructuredTool.from_function(
        func=generate_methodology_slide,
        name="generate_methodology_slide",
        description="Generates a professional methodology slide for research proposals. Features a two-column layout with qualitative and quantitative methods boxes on the left (displayed in stacked cards with accent color backgrounds at different opacities) and a professional technology/research image on the right. Includes decorative concentric circles and accent bar with the title. Perfect for academic, research, or scientific presentations requiring clear methodology explanation with modern, readable typography and professional visual appeal.",
        args_schema=GenerateMethodologySlideInput
    ),
    StructuredTool.from_function(
        func=generate_planning_phase_slide,
        name="generate_planning_phase_slide",
        description="Generates a Planning Phase slide with timeline and icon markers. This slide shows 4 stages represented by pin markers containing line art icons (brain, checklist, design, puzzle), each with its own timeline dot, title, and description. The markers are displayed horizontally above the timeline items, creating a visual flow. Perfect for presenting project phases, process steps, strategic planning stages, or any sequential workflow with 4 key stages. Features customizable colors for markers and timeline elements.",
        args_schema=GeneratePlanningPhaseSlideInput
    )
]

TEAM_TOOLS = [
    # === SLIDE GIỚI THIỆU TEAM ===
    StructuredTool.from_function(
        func=generate_team_slide,
        name="generate_team_slide",
        description="Generates a modern and dynamic Team Slide featuring a diagonal layout. This design intentionally minimizes the title area to emphasize the team members, who are presented in large, professional-looking cards with hover effects. The style is clean and contemporary, making it perfect for impactful introductions of key personnel in corporate or creative presentations.",
        args_schema=GenerateTeamSlideInput
    ),
    StructuredTool.from_function(
        func=generate_colorful_team_grid_slide,
        name="generate_colorful_team_grid_slide",
        description="Generates a modern and professional **Team Slide**. It features a two-column layout with a large title on the left and a visually balanced 2x2 grid of team member profiles on the right. **This design is optimized for exactly four members to maintain its symmetrical layout and visual impact.** Its most distinctive feature is the overlapping circular photo for each member, which has a vibrant, customizable color border, creating a dynamic 3D effect. This slide is perfect for introducing key personnel with a high-end, polished look.",
        args_schema=GenerateColorfulTeamGridSlideInput
    ),
    StructuredTool.from_function(
        func=generate_corporate_team_slide,
        name="generate_corporate_team_slide",
        description="Generates a creative and personal **Team Slide** with a 'Polaroid photo' theme. This slide is perfect for introducing team members in a warm and approachable way. Its unique characteristics include a central title and a grid of team member profiles, each styled to look like a Polaroid picture with a handwritten name. The photos are scattered and slightly rotated for a friendly, scrapbook-like feel. **The layout is flexible, but it is visually optimized for 3 to 4 members** to create a balanced, single-row composition.",
        args_schema=GenerateCorporateTeamSlideInput
    )
]

THANK_YOU_TOOLS = [
    # === SLIDE CẢM ƠN ===
    StructuredTool.from_function(
        func=generate_thank_you_slide_3,
        name="generate_thank_you_slide_3",
        description="Generates an HTML slide for thank you page with contact information and geometric background.",
        args_schema=GenerateThankYouSlide3Input
    ),
    StructuredTool.from_function(
        func=generate_corporate_thank_you_slide,
        name="generate_corporate_thank_you_slide",
        description="Generates a minimalist, corporate 'Thank You' or Closing Slide. It provides a clean and professional way to end a presentation. Its unique characteristics include a simple smiley icon, a bold 'Thanks!' message, and the signature dynamic diagonal color panel with a layered shadow effect. This slide is designed for a clean, impactful, and friendly conclusion.",
        args_schema=GenerateCorporateThankYouSlideInput
    ),
    StructuredTool.from_function(
        func=generate_business_thank_you_slide,
        name="generate_business_thank_you_slide",
        description="Generates a clean business thank you slide with professional aesthetic. Features large centered 'THANK YOU' text with subtitle, decorative D-shaped elements on left and right sides, and subtle grid background pattern. Maintains consistent business professional design language with the business intro and transition slides. Perfect for corporate presentations, business meetings, and professional closing slides.",
        args_schema=GenerateBusinessThankYouSlideInput
    ),
    StructuredTool.from_function(
        func = generate_thank_you_slide_4,
        name="generate_thank_you_slide_4",
        description="Generates a creative 'Thank You' slide featuring a speech bubble design. This slide includes a customizable thank you message inside a speech bubble with a gradient background, offering a friendly and engaging way to conclude presentations.",
        args_schema=GenerateThankYouSlide4Input
    ),
    StructuredTool.from_function(
        func = generate_thank_you_decorative_slide,
        name="generate_thank_you_decorative_slide",
        description="Generates a decorative Thank You slide with dots. Features a blue gradient background, large bold thank you text with shadow effects, and optional animated dots distributed evenly across the top and bottom areas for a clean and elegant closing slide.",
        args_schema=GenerateThankYouDecorativeSlideInput
    ),
    StructuredTool.from_function(
        func=generate_watercolor_thank_you_slide,
        name="generate_watercolor_thank_you_slide",
        description="Generates a beautiful 'Thank You' slide with a watercolor theme. Features a soft pastel gradient background, elegant script typography for the main thank you message, and decorative watercolor floral elements. Perfect for creative, educational, or personal presentations seeking a warm and artistic closing.",
        args_schema=GenerateWatercolorThankYouSlideInput
    ),
    StructuredTool.from_function(
        func=generate_thank_you_slide_5,
        name="generate_thank_you_slide_5",
        description="Generates a modern geometric 'Thank You' slide with a clean, minimalist design. Features a centered handwritten-style 'Thank you!' message on a light background with an inner border frame. The slide is decorated with two quarter-circle shapes in teal (top-left and bottom-right corners) and yellow circles (three circles arranged in a triangle at top-right, plus one half-circle cut off at bottom-left). This asymmetric geometric design creates visual balance while keeping the text prominent and readable. Perfect for professional presentations wanting a modern, geometric aesthetic for their closing slide.",
        args_schema=GenerateThankYouSlide5Input
    ),
    StructuredTool.from_function(
        func=generate_thank_you_slide_6,
        name="generate_thank_you_slide_6",
        description="Generates an elegant 'Thank You' slide with decorative elements including sunburst patterns, olive branches, and scattered colorful dots on a warm beige background. Features a large, flowing script font for the main text. The slide includes circular sunburst patterns placed at various positions around the slide, two olive branch decorations (one at top, one at bottom) flanking the text, and multicolored decorative dots scattered throughout. Perfect for presentations needing a sophisticated, vintage-inspired closing with natural, organic decorative elements.",
        args_schema=GenerateThankYouSlide6Input
    ),
    StructuredTool.from_function(
        func=generate_thank_you_slide_7,
        name="generate_thank_you_slide_7",
        description="Generates an elegant minimalist 'Thank You' slide. Features a clean, sophisticated design with a large serif font (Playfair Display) for the main text centered on the slide. The slide has a light warm gray background with generous white space, creating a refined and professional look. Perfect for presentations needing a simple, elegant closing that emphasizes beautiful typography without any decorative elements.",
        args_schema=GenerateThankYouSlide7Input
    )
]

# All available slide generation tools with complete parameter schemas
ALL_TOOLS = INTRO_TOOLS + TRANSITION_TOOLS + CONTENT_TOOLS + TEAM_TOOLS + THANK_YOU_TOOLS

TOOLS_DICT = {'INTRO_TOOLS': INTRO_TOOLS,
               'TRANSITION_TOOLS': TRANSITION_TOOLS,
               'CONTENT_TOOLS': CONTENT_TOOLS,
               'TEAM_TOOLS': TEAM_TOOLS,
               'THANK_YOU_TOOLS': THANK_YOU_TOOLS}

# Tool utilities
TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}

def get_all_tool_names():
    """Return list of all available tool names."""
    return list(TOOL_MAP.keys())

def get_tool_by_name(name: str):
    """Get a specific tool by name."""
    return TOOL_MAP.get(name)

def execute_tool(tool_call: dict):
    """Execute a tool call with the provided arguments."""
    name = tool_call.get("name")
    args = tool_call.get("arguments", {})
    
    if name in TOOL_MAP:
        try:
            result = TOOL_MAP[name].invoke(args)
            return str(result)
        except Exception as e:
            print(f"Error executing tool '{name}': {e}")
            return None
        print(f"Tool '{name}' not found.")
        return None