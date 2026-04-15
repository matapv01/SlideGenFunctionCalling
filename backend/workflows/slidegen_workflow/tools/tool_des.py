# Auto-generated from tools.py preserving all original parameter schemas
# This conversion maintains the exact parameter definitions from the source

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


# Import all slide generation functions from html_tool
from backend.workflows.slidegen_workflow.tools.html_tool import (
    generate_title_slide,   # slide intro
    generate_introduction_slide, # slide intro
    generate_intro_slide1, # slide intro
    generate_elegant_intro_slide,   # slide intro
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
    generate_title_slide_5, # slide intro(hien)
    generate_title_slide_7, # slide intro(hien)
    generate_title_slide_11, # slide intro(hien)
    generate_title_slide_12, # slide intro(hien)
    generate_title_slide_13, # slide intro(hien)
    generate_title_slide_15, # slide intro(hien)
    generate_title_slide_17, # slide intro(hien)
    generate_title_slide_18, # slide intro(hien)
  
    
    
    generate_dusk_transition_slide, # slide chuyển slide
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
    generate_section_header_slide_15, # slide chuyển slide(hien)
    generate_section_header_slide_17,   # slide chuyển slide(hien)
    generate_section_header_slide_18,   # slide chuyển slide(hien)



    generate_content_slide, # slide content
    generate_comparison_slide,  # slide content
    generate_process_slide,  # slide content
    generate_process_steps_slide, # slide content
    generate_image_cutout_list_slide, # slide content
    generate_body_slide4,  # slide content
    generate_body_slide5,  # slide content
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
    # generate_business_overview_slide,   # slide content
    generate_vision_mission_slide,  # slide content
    generate_service_roadmap_slide, # slide content
    generate_minimalist_tech_list_slide,    # slide content
    generate_split_layout_list_slide, # slide content
    generate_reference_slide,   # slide content
    generate_icon_list_slide,   # slide content
    generate_flexible_columns_slide, # slide content
    generate_text_with_image_slide, # slide content
    generate_geometric_split_content_slide, # slide content
    generate_geometric_split_content_slide_2, # slide content
    generate_geometric_image_content_slide, # slide content
    generate_geometric_grid_slide,  # slide content
    generate_memphis_content_slide, # slide content
    generate_memphis_multicolumn_slide, # slide content
    generate_memphis_grid_slide, # slide content
    generate_methodology_slide, # slide content
    generate_planning_phase_slide, # slide content
    generate_timeline_slide, # slide content
    generate_quote_slide, # slide content
    generate_classic_content_slide, # slide content



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
    generate_modern_contact_slide, # slide cảm ơn (mhung)
    generate_closing_slide, # slide cảm ơn (mhung)
    generate_minimalist_thank_you_slide,
    generate_minimalist_sage_slide, # slide cảm ơn (mhung)
    generate_thank_you_so_much_slide,   # slide cảm ơn (mhung)
    generate_brand_collaboration_closing_slide, # slide cảm ơn (mhung)
    generate_military_thank_you_slide,  # slide cảm ơn (mhung)
    generate_corporate2_thank_you_slide, 
    generate_creative_thank_you_slide, 
    generate_tech_thank_you_slide,
    generate_minimalist_thank_you_slide_2,
    generate_elegant_thank_you_slide,

    generate_line_chart_slide_2 , # slide biểu đồ đường (mhung)
    generate_line_chart_slide_3 ,# slide biểu đồ đường (mhung)
    generate_radar_chart_slide_1 ,# slide biểu đồ radar (mhung)
    generate_pie_chart_slide_1 ,# slide biểu đồ tròn (mhung)
    generate_scatter_plot_chart_slide_2 ,# slide biểu đồ scatter (mhung)
    generate_bar_chart_slide_2 ,# slide biểu đồ cột (mhung)
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
    main_title_font_style: str = Field(default="italic", description="CSS font style for the main title.")
    image_url: str = Field(default="Image/generate_intro_slide1/Default_1.png", description="Path to the image file for the left side.")


class GenerateElegantIntroSlideInput(BaseModel):
    """Input schema for generate_elegant_intro_slide."""
    main_title: str = Field(..., description="The large title displayed in the left column. Default: 'Write Your Topic or Idea Here'.")
    subtitle: str = Field(..., description="The smaller subtitle text below the main title. Default: 'Briefly elaborate on what you want to discuss.'.")
    image_url: str = Field(default="https://images.pexels.com/photos/3807735/pexels-photo-3807735.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", description="URL for the main image to be displayed on the right.")
    background_color: str = Field(default="#EAE3D9", description="Background color of the slide.")
    text_color: str = Field(default="#4A403A", description="Main text color for titles and descriptions.")
    decoration_color_start: str = Field(default="#F7DC6F", description="The starting color for the gold gradient decorations.")
    decoration_color_end: str = Field(default="#C9A842", description="The ending color for the gold gradient decorations.")


class GenerateTitleSlide2Input(BaseModel):
    """Input schema for generate_title_slide_2."""
    main_title: str = Field(..., description="The entire title for the slide. Use <br> for line breaks and <span class='highlight'>word</span> to highlight a specific word. Default: 'THIS IS YOUR<br><span class=\'highlight\'>PRESENTATION</span><br>TITLE'.")
    accent_color: str = Field(default="#06B6D4", description="The primary accent color for the right panel and the highlighted word.")
    shadow_color: str = Field(default="#0E7490", description="The secondary (darker) accent color for the panel behind.")
    text_color: str = Field(default="#6B7280", description="The primary color for the non-highlighted text.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small icon above the title.")

class GenerateDynamicIntroSlideInput(BaseModel):
    """Input schema for generate_dynamic_intro_slide."""
    main_title: str = Field(..., description="The large, bold title for the slide. Default: 'Innovate. Create. Inspire.'.")
    subtitle: str = Field(..., description="The smaller subtitle text below the main title. Default: 'This is where we outline our core mission and the driving force behind our vision.'.")
    image_url: str = Field(default="https://images.unsplash.com/photo-1521737711867-e3b97375f902?q=80&w=1887&auto=format&fit=crop", description="URL for the full-height image on the right.")
    primary_color: str = Field(default="#4F46E5", description="The primary (brighter) color for the main part of the text block.")
    secondary_color: str = Field(default="#3730A3", description="The secondary (darker) color for the footer area of the text block.")
    text_color: str = Field(default="#FFFFFF", description="The color for the text.")

class GenerateBigConceptSlideInput(BaseModel):
    """Input schema for generate_big_concept_slide."""
    main_title: str = Field(..., description="The main, large title for the concept. Use <br> for line breaks. Default: 'BIG<br>CONCEPT'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Bring the attention of your audience over a key concept using icons or illustrations'.")
    icon_name: str = Field(..., description="Selects a pre-designed illustration scene to display. Default: 'space'.")
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
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

class GeneratePlayfulTitleSlideInput(BaseModel):
    """Input schema for generate_playful_title_slide."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks. Default: 'Introduction<br>to penguins'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Introduce penguins here. Mention their characteristics and unique behaviors.'.")
    illustration_character: str = Field(default="penguin", description="Selects a pre-drawn character illustration.")
    top_bg_color: str = Field(default="#FFC947", description="The main background color (yellow).")
    bottom_bg_color: str = Field(default="#E8715D", description="The color of the strip at the bottom.")
    text_color: str = Field(default="#2D2D2D", description="The color for all text.")
    doodle_color: str = Field(default="#89CFF0", description="The color for the small decorative squiggles and stars.")

class GenerateMinimalistTitleSlideInput(BaseModel):
    """Input schema for generate_minimalist_title_slide."""
    main_title: str = Field(..., description="The main, large presentation title. Default: 'This is your presentation title'.")
    subtitle: str = Field(..., description="A smaller subtitle to provide more context or a tagline. Default: 'A subtitle to provide more context or a tagline'.")
    author_line: str = Field(..., description="A line for the presenter's name or company, displayed at the bottom. Default: 'Presented by Your Name / Company'.")
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

class GenerateBusinessIntroSlideInput(BaseModel):
    """Input schema for generate_business_intro_slide."""
    main_title: str = Field(..., description="Large main title text , default='PRESENTATION'")
    subtitle: str = Field(..., description="Description text below main title.  default='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore'")
    main_title_color: str = Field(default="#0056d2", description="Color for main title (default: blue).")
    subtitle_color: str = Field(default="#666666", description="Color for subtitle text.")
    accent_color: str = Field(default="#0056d2", description="Color for decorative D-shapes on sides.")

class GenerateTitleSlide3Input(BaseModel):
    """Input schema for generate_title_slide_3."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks. Default: 'Christmas Lights<br>Minitheme'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Here is where your presentation begins'.")
    bg_color: str = Field(default="#F5EBE0", description="The background color of the slide.")
    text_color: str = Field(default="#C41E3A", description="The color for the main title text.")
    subtitle_color: str = Field(default="#3D3D3D", description="The color for the subtitle text.")
    show_top_lights: Optional[bool] = Field(default=True, description="Whether to show the Christmas lights at the top. Default: True.")
    show_sparkles: Optional[bool] = Field(default=True, description="Whether to show decorative sparkles on the slide. Default: True.")
    custom_css: str = Field(default="", description="Additional custom CSS to be included.")
    
class GenerateMinimalistSlideInput(BaseModel):
    """Input schema for generate_minimalist_slide."""
    title: str = Field(..., description="The main title for the slide. Default: 'Minimalist Business Slides'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Here is where your presentation begins'.")
    background_color: str = Field(default="#E8E3DC", description="The background color of the slide.")
    text_color_title: str = Field(default="#1A1A1A", description="The color for the title text.")
    text_color_subtitle: str = Field(default="#4A4A4A", description="The color for the subtitle text.")
    line_color: str = Field(default="#2C2C2C", description="The color for the decorative lines.")
    curve_color: str = Field(default="#4A4A4A", description="The color for the decorative curves.")
    
 
class GenerateTitleSlide5Input(BaseModel):
    """Input schema for generate_title_slide_5."""
    top_left_text: str = Field(default="Our shared moments", description="Text displayed in the top-left corner of the slide.")
    year: str = Field(default="20XX", description="Year displayed in the top-right corner of the slide.")
    main_title: str = Field(default="Your Title Here", description="The main title text for the notebook cover design.")
    bottom_text: str = Field(default="Here is where your presentation begins", description="Text displayed at the bottom-right of the slide.")
    image_path: str = Field(default="Image/generate_title_slide_5/Default_1.jpg", description="Path to the image displayed in the polaroid frame.")
    bg_color: str = Field(default="#b8c8d4", description="Background color of the slide in hex format.")
    text_color: str = Field(default="#2c3e50", description="Color of all text elements in hex format.")
    show_clover: bool = Field(default=True, description="Whether to display the four-leaf clover decoration.")
    show_decorative_lines: bool = Field(default=True, description="Whether to display decorative horizontal lines.")
    custom_css: str = Field(default="", description="Additional custom CSS to be included in the slide.")
    

class GenerateTitleSlide7Input(BaseModel):
    """Input schema for generate_title_slide_7."""
    main_title: str = Field(..., description="Main title text displayed prominently (e.g., 'BUSINESS PLAN').")
    subtitle: str = Field(..., description="Subtitle text displayed below the main title.")
    bg_color: str = Field(default="#F5F7FA", description="Background color of the slide (hex code).")
    card_bg_color: str = Field(default="#FFFFFF", description="Background color for the text card or frame (hex code).")
    border_color: str = Field(default="#E5E7EB", description="Border color for framed elements (hex code).")
    accent_color: str = Field(default="#B99C6B", description="Accent color used for decorative elements (hex code).")
    title_color: str = Field(default="#1F2937", description="Color of the main title text (hex code).")
    subtitle_color: str = Field(default="#4B5563", description="Color of the subtitle text (hex code).")
    custom_css: str = Field(default="", description="Additional custom CSS to include.")

class GenerateTitleSlide11Input(BaseModel):
    """Input schema for generate_title_slide_11."""
    main_title: str = Field(..., description="Main title text displayed in large Georgia serif font.")
    subtitle: str = Field(..., description="Subtitle text shown below the title.")
    bg_left_color: str = Field(default="#f5d7d7", description="Background color for left half of the slide (hex).")
    bg_right_color: str = Field(default="#e8e8e8", description="Background color for right half of the slide (hex).")
    text_color: str = Field(default="#2d2d2d", description="Color for all text elements (hex).")

class GenerateTitleSlide12Input(BaseModel):
    """Input schema for generate_title_slide_12."""
    main_title: str = Field(..., description="Main title text in Montserrat bold font.")
    subtitle: str = Field(..., description="Subtitle text shown below the title.")
    bg_color: str = Field(default="#F5F5F5", description="Background color of the slide (hex).")
    circle_color: str = Field(default="#E5E5E5", description="Color of the large decorative circle on the right (hex).")
    border_color: str = Field(default="#000000", description="Color of the rectangular border frame (hex).")
    text_color: str = Field(default="#000000", description="Color for all text elements (hex).")

class GenerateTitleSlide13Input(BaseModel):
    """Input schema for generate_title_slide_13."""
    main_title: str = Field(..., description="Main title text in Montserrat extra-bold font.")
    subtitle: str = Field(..., description="Subtitle text shown below the title.")
    bg_color: str = Field(default="#E8F4F8", description="Starting color for diagonal gradient background (hex).")
    text_color: str = Field(default="#1A1A4D", description="Color for title and subtitle text (hex).")
    decoration_color: str = Field(default="#A8D5E2", description="Color for geometric decorations - rounded rectangles and circle (hex).")

class GenerateTitleSlide15Input(BaseModel):
    """Input schema for generate_title_slide_15."""
    main_title: str = Field(..., description="Main title text in Montserrat bold uppercase font.")
    subtitle: str = Field(..., description="Subtitle text shown above the main title.")
    background_color: str = Field(default="#F5F5F0", description="Background color for the slide (hex).")
    subtitle_color: str = Field(default="#7A7A7A", description="Color for the subtitle text (hex).")
    title_color: str = Field(default="#E8B45E", description="Color for the main title text (hex, default golden yellow).")
    accent_line_color: str = Field(default="#E37854", description="Color for the decorative horizontal line below title (hex, default coral orange).")
    top_circle_color: str = Field(default="#E37854", description="Color for the top-left decorative circle (hex, default coral orange).")
    bottom_circle_color: str = Field(default="#5A7A7F", description="Color for the bottom-right decorative circle (hex, default teal gray).")

class GenerateTitleSlide17Input(BaseModel):
    """Input schema for generate_title_slide_17."""
    main_title: str = Field(..., description="Main title text.")
    subtitle: str = Field(..., description="Subtitle text.")
    bg_color: str = Field(default="#F5F5F5", description="Background color (hex).")
    title_color: str = Field(default="#2D2D2D", description="Main title color (hex).")
    subtitle_color: str = Field(default="#6B6B6B", description="Subtitle text color (hex).")
    circle_color_1: str = Field(default="#5DBBBB", description="First decorative circle color (hex).")
    circle_color_2: str = Field(default="#6BA3C8", description="Second decorative circle color (hex).")
    circle_color_3: str = Field(default="#E8B858", description="Third decorative circle color (hex).")

class GenerateTitleSlide18Input(BaseModel):
    """Input schema for generate_title_slide_18."""
    main_title: str = Field(..., description="Main heading text.")
    subtitle: str = Field(..., description="Subtitle text below main title.")
    bg_pattern_color: str = Field(default="#E8E8E8", description="Color for the geometric cube pattern background (hex).")
    card_bg_color: str = Field(default="#F9ED9B", description="Background color of center card (hex).")
    title_color: str = Field(default="#000000", description="Color for main title text (hex).")
    subtitle_color: str = Field(default="#2D2D2D", description="Color for subtitle text (hex).")

# === SLIDE CHUYỂN SLIDE CLASSES ===

class GenerateDuskTransitionSlideInput(BaseModel):
    """Input schema for generate_dusk_transition_slide."""
    headline: str = Field(..., description="The main headline for the transition. Default: 'Transition Headline'.")
    subtitle: str = Field(..., description="The smaller subtitle text below the headline. Default: 'Let's start with the first set of slides'.")
    headline_color: str = Field(default="#2C3E50", description="The color for the main headline text.")
    subtitle_color: str = Field(default="#4A5568", description="The color for the subtitle text.")
    number_color: str = Field(default="#FDE68A", description="The accent color for the section number.")
    sky_top_color: str = Field(default="#6B4F9B", description="The color for the top of the sky gradient (purple).")
    sky_mid_color: str = Field(default="#C07CB6", description="The color for the middle of the sky gradient (pink).")
    sky_bottom_color: str = Field(default="#F6B17B", description="The color for the bottom of the sky gradient (orange).")
    grid_dot_color: str = Field(default="rgba(255, 255, 255, 0.3)", description="The color and opacity for the dots in the background grid.")

class GeneratePushpinSectionHeaderInput(BaseModel):
    """Input schema for generate_pushpin_section_header."""
    main_title: str = Field(..., description="The main text for the section header. It will be displayed in large, uppercase letters. Default: 'Add a Section Header'.")
    bg_color: str = Field(default="#FDFCFB", description="The background color of the slide, with a subtle paper texture overlay.")
    text_color: str = Field(default="#1F2937", description="The color for the main title text.")
    accent_color: str = Field(default="#1F2937", description="The color for the horizontal divider line and the two flanking dots.")

class GenerateSectionHeaderSlideInput(BaseModel):
    """Input schema for generate_section_header_slide."""
    header_text: str = Field(..., description="The main, large text for the section header. Default: 'Add a Section Header'.")
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


class GenerateSectionHeaderSlide15Input(BaseModel):
    """Input schema for generate_section_header_slide_15."""
    main_title: str = Field(..., description="Main title text for the slide. default='MERRY CHRISTMAS AND HAPPY NEW YEAR!'.")
    bg_color: str = Field(default="#0f2f1f", description="Background color (default: dark evergreen green for Christmas theme).")
    text_color: str = Field(default="#f8f8f8", description="Text color (default: bright white).")
    blob1_color: str = Field(default="rgba(220, 38, 38, 0.5)", description="First gradient blob color (default: Christmas red).")
    blob2_color: str = Field(default="rgba(34, 139, 34, 0.5)", description="Second gradient blob color (default: forest green).")
    blob3_color: str = Field(default="rgba(218, 165, 32, 0.4)", description="Third gradient blob color (default: golden yellow).")
    custom_css: str = Field(default="", description="Additional CSS rules to inject into the style block.")

class GenerateSectionHeaderSlide17Input(BaseModel):
    """Input schema for generate_section_header_slide_17."""
    section_title: str = Field(..., description="Main title text in uppercase. Default: PROJECT SCHEDULE.")
    section_subtitle: str = Field(..., description="Subtitle text below main title. Default: You could enter a subtitle here if you need it")
    bg_color: str = Field(default="#f5f3ed", description="Background color (hex).")
    title_color: str = Field(default="#d4af6a", description="Color for main title (hex).")
    subtitle_color: str = Field(default="#7a8288", description="Color for subtitle text (hex).")
    circle_left_color: str = Field(default="#e8b558", description="Color for top-left corner circle (hex).")
    circle_right_color: str = Field(default="#d9653b", description="Color for bottom-right corner circle (hex).")
    bar_color: str = Field(default="#6b7f82", description="Color for horizontal decorative bars (hex).")


class GenerateSectionHeaderSlide18Input(BaseModel):
    """Input schema for generate_section_header_slide_18."""
    section_title: str = Field(..., description="Main title text. Default: ANALYSIS AND RESULTS.")
    section_subtitle: str = Field(..., description="Subtitle text below main title. Default: You could enter a subtitle here if you need it")
    bg_color: str = Field(default="#f5f5f0", description="Background color (hex).")
    title_color: str = Field(default="#E8B44F", description="Color for main title (hex).")
    subtitle_color: str = Field(default="#666666", description="Color for subtitle text (hex).")
    circle_blue: str = Field(default="#6B9FBD", description="Color for blue circles (hex).")
    circle_yellow: str = Field(default="#E8B44F", description="Color for yellow circles (hex).")
    circle_teal: str = Field(default="#6FBAAA", description="Color for teal circles (hex).")



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
    custom_css: str = Field(default="", description="Additional custom CSS.")

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
    image_url_1: str = Field(default="Image/generate_body_slide5/Default_1.png", description="Path to the first image file.")
    image_url_2: str = Field(default="Image/generate_body_slide5/Default_2.png", description="Path to the second image file.")
    image_url_3: str = Field(default="Image/generate_body_slide5/Default_3.png", description="Path to the third image file.")
    image_url_4: str = Field(default="Image/generate_body_slide5/Default_4.png", description="Path to the fourth image file.")


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

class GenerateMainPointsSlideInput(BaseModel):
    """Input schema for generate_main_points_slide."""
    title: str = Field(..., description="Main title displayed at the top of the slide in uppercase")
    point1_title: str = Field(..., description="Title for the first point (plastic bag icon) - displayed in uppercase")
    point1_description: str = Field(..., description="Description text for the first point about plastic/waste management. .")
    point2_title: str = Field(..., description="Title for the second point (faucet icon) - displayed in uppercase")
    point2_description: str = Field(..., description="Description text for the second point about water conservation/management. .")
    point3_title: str = Field(..., description="Title for the third point (factory icon) - displayed in uppercase")
    point3_description: str = Field(..., description="Description text for the third point about industrial processes/manufacturing. .")

class GenerateElegantPointsSlideInput(BaseModel):
    """Input schema for generate_elegant_points_slide."""
    main_title: str = Field(..., description="A concise title at the top of the slide, styled to be less prominent than the main content. Default: 'Write Your Topic or Idea Here'.")
    points: List[Dict[str, str]] = Field(..., description="An array of exactly 4 objects, where each object represents a large, prominent content card with an icon, title, and description. Each point should have 'title' and 'description' keys. Default: [{'title': 'Add a Key Point', 'description': 'Briefly elaborate on the topic you want to discuss.'}, {'title': 'Add a Key Point', 'description': 'Briefly elaborate on the topic you want to discuss.'}, {'title': 'Add a Key Point', 'description': 'Briefly elaborate on the topic you want to discuss.'}, {'title': 'Add a Key Point', 'description': 'Briefly elaborate on the topic you want to discuss.'}].")
    bg_color: str = Field(default="#FDFCFB", description="Overall background color of the slide (off-white).")
    card_bg_color: str = Field(default="#FFFFFF", description="Background color for the four content cards (pure white).")
    title_color: str = Field(default="#4E443F", description="Text color for the main title and card titles (dark brown).")
    text_color: str = Field(default="#5D534D", description="Text color for the card descriptions (lighter brown-gray).")
    accent_color: str = Field(default="#B99C6B", description="The accent color for the icons and their dividers (bronze/old gold).")


class GenerateCorporateContentSlideInput(BaseModel):
    """Input schema for generate_corporate_content_slide."""
    main_title: str = Field(..., description="The main title displayed in the colored panel on the left. To highlight a word, wrap it in `<span class='highlight'>...</span>`. Default: 'THIS IS A <span class=\'highlight\'>SLIDE</span> TITLE'.")
    list_items: List[Dict[str, str]] = Field(..., description="An array of objects, where each object represents a content card with its own title and description. Default: [{'title': 'First Key Point', 'description': 'Here you have a list of items, presented in a modern, card-based format.'}, {'title': 'Second Key Point', 'description': 'And some text to elaborate on the second main idea of your slide.'}, {'title': 'Third Key Point', 'description': 'But remember not to overload your slides with too much content.'}]")
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
    bg_gradient_start: str = Field(default="#0F172A", description="The starting color (top) of the dark background gradient.")
    bg_gradient_end: str = Field(default="#1E293B", description="The ending color (bottom) of the dark background gradient.")
    title_color: str = Field(default="#FFFFFF", description="The color for the main title and the card titles.")
    text_color: str = Field(default="#D1D5DB", description="The color for the card descriptions.")
    accent_color: str = Field(default="#22D3EE", description="The neon accent color used for highlights, card borders, and icons.")

class GenerateCorporateMulticolumnSlideInput(BaseModel):
    """Input schema for generate_corporate_multicolumn_slide."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks and <span class='highlight'>word</span> to highlight. Will be displayed in large 2.5rem font. Default: 'IN TWO OR THREE<br><span class=\'highlight\'>COLUMNS</span>'.")
    columns: List[Dict[str, str]] = Field(..., description="An array of 2 or 3 objects, each representing a column. Each column will be displayed as a card with gradient background, rounded corners, and hover effects. Default: [{'title': 'Yellow', 'description': 'Is the color of gold, butter and ripe lemons.'}, {'title': 'Blue', 'description': 'Is the colour of the clear sky and the deep sea.'}, {'title': 'Red', 'description': 'Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage.'}]")
    accent_color: str = Field(default="#8B5CF6", description="The primary accent color for the right panel, highlighted text, and card accent borders. Used in gradients for enhanced visual appeal.")
    shadow_color: str = Field(default="#7C3AED", description="The secondary (darker) accent color for the panel behind and gradient effects.")
    text_color: str = Field(default="#4B5563", description="The primary color for the body text.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small globe icon. Icon size increased to 3.5rem with drop-shadow effect.")

class GenerateCorporateGridSlideInput(BaseModel):
    """Input schema for generate_corporate_grid_slide."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks and <span class='highlight'>word</span> to highlight. Will be displayed in large 2.5rem font with uppercase styling. Default: 'LET'S <span class=\'highlight\'>REVIEW</span> SOME<br>CONCEPTS'.")
    grid_items: List[Dict[str, str]] = Field(..., description="An array of exactly 6 objects for the 2x3 grid. Each item will be displayed as a card with gradient background, rounded corners, hover effects, and colored top border. Grid automatically adjusts to 2 columns on smaller screens. Default: [{'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}]")
    accent_color: str = Field(default="#22C55E", description="The primary accent color for the right panel, highlighted text, and card accent borders. Used in gradients for enhanced visual appeal.")
    shadow_color: str = Field(default="#16A34A", description="The secondary (darker) accent color for the panel behind and gradient effects.")
    text_color: str = Field(default="#6B7280", description="The primary color for the body text.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small pencil icon. Icon size increased to 3.5rem with drop-shadow effect.")

# class GenerateBusinessOverviewSlideInput(BaseModel):
#     """Input schema for generate_business_overview_slide."""
#     main_title: str = Field(..., description="Main title text (10-25 characters), displayed on the left side. Default: 'BUSINESS OVERVIEW'.")
#     sections: List[Dict] = Field(..., description="List of dictionaries with icon and content for each section. Icons: 'chart-analysis', 'innovation', 'growth'. . Default: 3 sections with Lorem ipsum content.")
#     left_bg_color: str = Field(default="#1a4b8c", description="Background color for the left title section (hex code).")
#     right_bg_color: str = Field(default="#f8f9fa", description="Background color for the right content area (hex code).")
#     title_color: str = Field(default="#FFFFFF", description="Color of the main title text (hex code).")
#     icon_bg_color: str = Field(default="#2a3f6b", description="Background color for icon containers (hex code).")
#     icon_color: str = Field(default="#FFFFFF", description="Color of the icons (hex code).")
#     content_bg_color: str = Field(default="#FFFFFF", description="Background color for content text areas (hex code).")
#     content_text_color: str = Field(default="#1a4b8c", description="Text color for content sections (hex code).")
#     show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
#     border_opacity: Optional[float] = Field(default=0, description="Opacity of the border frame (0.0 to 1.0). Default: 0.3.")
#     section_spacing: str = Field(default="15px", description="Vertical spacing between content sections.")
#     icon_size: str = Field(default="80px", description="Size of the icon containers.")
#     custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

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
    show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
    border_color: str = Field(default="#1a4b8c", description="Color of the border frame (hex code).")
    border_opacity: Optional[float] = Field(default=0, description="Opacity of the border frame (0.0 to 1.0). Default: 0.4.")
    show_geometric_pattern: Optional[bool] = Field(default=True, description="Whether to show geometric background pattern. Default: True.")
    pattern_opacity: Optional[float] = Field(default=0, description="Opacity of the geometric pattern (0.0 to 1.0). Default: 0.1.")
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
    show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
    border_color: str = Field(default="rgba(255, 255, 255, 0.3)", description="Color of the border frame (rgba with transparency).")
    show_decorative_triangles: Optional[bool] = Field(default=True, description="Whether to show decorative triangle elements. Default: True.")
    triangle_color: str = Field(default="rgba(255, 255, 255, 0.1)", description="Color of the decorative triangles (rgba with transparency).")
    card_border_radius: str = Field(default="20px", description="Border radius for content cards.")
    card_padding: str = Field(default="25px", description="Padding inside content cards.")
    card_shadow: str = Field(default="0 8px 24px rgba(0, 0, 0, 0.15)", description="Box shadow for content cards.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")


class GenerateMinimalistTechListSlideInput(BaseModel):
    """Input schema for generate_minimalist_tech_list_slide."""
    title: str = Field(..., description="The main title of the slide. Default: 'This is a slide title'.")
    list_items: List[str] = Field(..., description="A list of strings for the bullet points. Default: ['Here you have a list of items', 'And some text', 'But remember not to overload your slides with content'].")
    concluding_text: str = Field(..., description="A final sentence or phrase at the bottom, styled to stand out. Default: 'Your audience will listen to you or read the content, but won't do both.'.")
    title_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '3rem') for the main title.")
    list_item_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '1.5rem') for list items.")
    concluding_text_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '1.1rem') for the concluding text.")
    sky_top_color: str = Field(default="#ABB0EA", description="The color for the top of the background gradient.")
    sky_bottom_color: str = Field(default="#A2CFED", description="The color for the bottom of the background gradient.")
    grid_dot_color: str = Field(default="rgba(0, 0, 0, 0.05)", description="The color of the dots in the background grid.")
    text_color: str = Field(default="#1F2937", description="The main color for all text elements.")
    accent_color: str = Field(default="#6366F1", description="The accent color for the side border and bullet points.")
    custom_css: str = Field(default="", description="Optional custom CSS for advanced styling.")

class GenerateSplitLayoutListSlideInput(BaseModel):
    """Input schema for generate_split_layout_list_slide."""
    main_title: str = Field(..., description="The main title displayed in the left column. Supports HTML tags like <b>, <i>, and <br> for line breaks. Default: 'YOUR MAIN TOPIC'.")
    points: List[Dict[str, str]] = Field(..., description="A list of key points to display in the right column. Each point should have 'title' and 'description' keys.")
    font_size_multiplier: Optional[float] = Field(default=1.0, description="Adjusts the default responsive font size. 1.0 is standard. This is ignored if a fixed font size is set below.")
    main_title_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '4rem') for the main title, overriding automatic scaling.")
    point_title_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '1.25rem') for the point titles, overriding automatic scaling.")
    point_description_font_size: str = Field(default=None, description="Optional. Set a fixed CSS font size (e.g., '1rem') for the point descriptions, overriding automatic scaling.")
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
    bg_color: str = Field(default="#FFFFFF", description="The background color for the text column.")
    text_color: str = Field(default="#1F2937", description="The main text color for all text elements.")
    accent_color: str = Field(default="#3B82F6", description="The color for the decorative divider below the main title.")

class GenerateIconListSlideInput(BaseModel):
    """Input schema for generate_icon_list_slide."""
    main_title: str = Field(..., description="The supporting title displayed in the smaller, left column. Default: 'Write your topic or idea'.")
    points: List[Dict[str, str]] = Field(..., description="An array of objects, each representing a key point in the main content area. Each point should have 'icon_name', 'title', and 'description' keys. Default: [{ 'icon_name': 'megaphone', 'title': 'Add a main point', 'description': 'Briefly elaborate on what you want to discuss.' }, { 'icon_name': 'star', 'title': 'Add a main point', 'description': 'Briefly elaborate on what you want to discuss.' }, { 'icon_name': 'thumbs-up', 'title': 'Add a main point', 'description': 'Briefly elaborate on what you want to discuss.' }].")
    bg_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    main_title_color: str = Field(default="#111827", description="Text color for the main title.")
    point_title_color: str = Field(default="#1F2937", description="Text color for the point titles.")
    point_description_color: str = Field(default="#4B5563", description="Text color for the point descriptions.")
    accent_color: str = Field(default="#3B82F6", description="The single accent color used for all icon circles and the decorative divider.")

class GenerateFlexibleColumnsSlideInput(BaseModel):
    """Input schema for generate_flexible_columns_slide."""
    main_title: str = Field(..., description="The main title displayed at the top of the slide. Default: 'IN TWO OR THREE COLUMNS'.")
    columns: List[Dict[str, str]] = Field(..., description="An array of 1 to 6 objects, each representing a column with its own title and description. Default: [{'title': 'Yellow', 'description': 'Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange.'}, {'title': 'Blue', 'description': 'Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum.'}, {'title': 'Red', 'description': 'Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage.'}].")
    text_color: str = Field(default="#34495E", description="The color for all text elements.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the repeating paper texture background.")

class GenerateTextWithImageSlideInput(BaseModel):
    """Input schema for generate_text_with_image_slide."""
    title: str = Field(..., description="The introductory headline for the text column, styled to be smaller. Default: 'Tiltle'.")
    text_content: str = Field(..., description="The main paragraph or body text, displayed in a large font to be the central focus of the text column. Default: 'Content.'.")
    image_url: str = Field(default="https://images.pexels.com/photos/1778412/pexels-photo-1778412.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", description="URL for the full-height image on the right side.")
    text_color: str = Field(default="#34495E", description="The color for all text elements.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the repeating paper texture background.")
    doodle_border_url: str = Field(default="https://i.imgur.com/Qy2O1vN.png", description="URL for the seamless doodle image used as a border at the bottom.")

class GenerateGeometricSplitContentSlideInput(BaseModel):
    """Input schema for generate_geometric_split_content_slide."""
    main_title: str = Field(..., description="The main title for the slide's content. Default: 'You can also split your content'.")
    columns: List[Dict[str, str]] = Field(..., description="""An array of objects, where each object represents a column. Default: [
        {"title": "White", "description": "Is the color of milk and fresh snow, the color produced by the combination of all the colors of the visible spectrum."},
        {"title": "Black", "description": "Is the color of ebony and of outer space. It has been the symbolic color of elegance, solemnity and authority."}
    ]""")
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
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for all text elements.")

class GenerateGeometricImageContentSlideInput(BaseModel):
    """Input schema for generate_geometric_image_content_slide."""
    image_url: str = Field(default="https://images.unsplash.com/photo-1557804506-669a67965ba0?q=80&w=2574&auto=format&fit=crop", description="The URL for the main image to be displayed in the custom-shaped container.")
    main_title: str = Field(..., description="The main title for the slide. Use a `<span class='highlight'>` tag to highlight a specific word. Default: 'A picture is worth a <span class='highlight'>thousand</span> words'.")
    description: str = Field(..., description="The paragraph of text that describes or complements the image. Default: 'A complex idea can be conveyed with just a single still image, namely making it possible to absorb large amounts of data quickly.'.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for the non-highlighted text.")


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
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for all text elements.")

class GenerateMemphisContentSlideInput(BaseModel):
    """Input schema for generate_memphis_content_slide."""
    main_title: str = Field(..., description="The main title of the slide, displayed in the top panel. Default: 'This is a slide title'.")
    list_items: List[str] = Field(..., description="A list of strings for the bullet points in the bottom panel. Default: ['Here you have a list of items', 'And some text', 'But remember not to overload your slides with content'].")
    concluding_text: str = Field(..., description="A final sentence or paragraph displayed below the list. Default: 'Your audience will listen to you or read the content, but won't do both.'.")
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
    top_panel_bg: str = Field(default="#19114B", description="The background color for the top panel.")
    bottom_panel_bg: str = Field(default="#403271", description="The background color for the bottom panel.")
    palette: List[str] = Field(default=["#F43F5E", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"], description="A list of 5 colors used for the various decorative shapes and accents.")

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

class GenerateTimelineSlideInput(BaseModel):
    """Input schema for generate_timeline_slide."""
    main_title: str = Field(
        default="COMPANY HISTORY", 
        description="Main title of the slide."
    )
    subtitle: str = Field(
        default="A journey of innovation and growth", 
        description="Subtitle text below the main title."
    )
    milestones: List[Dict[str, str]] = Field(
        default=[
            {"year": "2020", "title": "Foundation", "desc": "Started with a team of 5 visionaries."},
            {"year": "2021", "title": "Series A", "desc": "Raised $10M to expand operations."},
            {"year": "2022", "title": "Global Launch", "desc": "Entered 3 new international markets."},
            {"year": "2023", "title": "Market Leader", "desc": "Achieved #1 status in the industry."}
        ],
        description="List of milestones to display on the timeline. Each dict should have 'year', 'title', and 'desc' keys. Recommended 4-5 items."
    )
    bg_color: str = Field(
        default="#1E1E2E", 
        description="Background color hex code."
    )
    accent_color: str = Field(
        default="#F43F5E", 
        description="Accent color for the timeline line and active elements."
    )
    text_color: str = Field(
        default="#FFFFFF", 
        description="Color for text elements."
    )

class GenerateQuoteSlideInput(BaseModel):
    """Input schema for generate_quote_slide."""
    quote: str = Field(
        ..., 
        description="The main quote text or core message to display. Default: 'Design is not just what it looks like and feels like. Design is how it works.'"
    )
    author: str = Field(
        default="Steve Jobs",
        description="Name of the author or speaker."
    )
    role: str = Field(
        default="Co-founder, Apple", 
        description="Role or title of the author (e.g., 'CEO', 'Founder')."
    )
    bg_color: str = Field(
        default="#FAF9F6", 
        description="Background color hex code (usually light for elegance)."
    )
    quote_color: str = Field(
        default="#18181B", 
        description="Color of the quote text."
    )
    accent_color: str = Field(
        default="#EA580C", 
        description="Accent color for decorative elements (lines, quotation marks)."
    )

class GenerateClassicContentSlideInput(BaseModel):
    """Input schema for generate_classic_content_slide."""
    main_title: str = Field(
        default="MARKET OPPORTUNITY", 
        description="The main headline of the content slide."
    )
    paragraph: str = Field(
        ..., 
        description="A detailed paragraph explaining the topic (2-3 sentences). Default: 'The market opportunity for our innovative solution is vast and growing rapidly. With increasing demand for efficient and user-friendly products, we are well-positioned to capture significant market share and drive substantial growth in the coming years.'"
    )
    bullet_points: List[str] = Field(
        default=[
        "Target audience growth of 15% YoY",
        "Low competition in the premium segment",
        "High barrier to entry for new players",
        "Strong demand for automated solutions"
    ], 
        description="List of key points/bullets to display on the left side."
    )
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2015", 
        description="URL of the illustrative image on the right side."
    )
    theme_color: str = Field(
        default="#2563EB", 
        description="Primary theme color for accents and bullets."
    )
    text_color: str = Field(
        default="#1F2937", 
        description="Main text color."
    )
    bg_color: str = Field(
        default="#FFFFFF", 
        description="Background color hex code."
    )

# === SLIDE GIỚI THIỆU TEAM CLASSES ===

class GenerateTeamSlideInput(BaseModel):
    """Input schema for generate_team_slide."""
    main_title: str = Field(..., description="The main title, displayed in the smaller, diagonal accent area. Default: 'Our Team'.")
    team_members: List[Dict[str, str]] = Field(..., description="Array of team member objects, each displayed in a large, professional card. Each member should have 'name', 'role', and 'image_url' keys. Recommended 3 members for this layout. Default: [{'name': 'Alex Johnson', 'role': 'Lead Developer', 'image_url': 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?q=80&w=1780&auto=format=fit=crop'}, {'name': 'Maria Garcia', 'role': 'Product Manager', 'image_url': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1887&auto=format=fit=crop'}, {'name': 'James Smith', 'role': 'UX/UI Designer', 'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1887&auto=format=fit=crop'}].")
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
    bg_color: str = Field(default="#F8FAFC", description="Background color of the slide.")
    title_color: str = Field(default="#111827", description="Text color for the main title.")
    subtitle_color: str = Field(default=None, description="Text color for the subtitle.")
    card_text_color: str = Field(default="#1F2937", description="Text color for the name and role on the cards.")

class GenerateCorporateTeamSlideInput(BaseModel):
    """Input schema for generate_corporate_team_slide."""
    main_title: str = Field(..., description="The main title for the slide, e.g., 'Our Creative Team'. Default: 'Our Creative Team'.")
    team_members: List[Dict[str, str]] = Field(..., description="An array of objects, each representing a team member with their own photo. Default: [{'name': 'Olivia Chen', 'role': 'Lead Designer', 'image_url': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1887&auto=format=fit=crop'}, {'name': 'Ben Carter', 'role': 'Photographer', 'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1887&auto=format=fit=crop'}, {'name': 'Aisha Khan', 'role': 'Content Strategist', 'image_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1887&auto=format=fit=crop'}, {'name': 'Leo Martinez', 'role': 'Illustrator', 'image_url': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=1887&auto=format=fit=crop'}]")
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
class GenerateThankYouSlide4Input(BaseModel):
    """Input schema for generate_thank_you_slide_4 (speech bubble thank you slide)."""
    main_text: str = Field(default="THANK YOU!", description="The thank you message text displayed in the speech bubble.")
    bg_color: str = Field(default="#5B9BD5", description="Background gradient start color. Default: blue.")
    bg_gradient_to: str = Field(default="#A8D8F0", description="Background gradient end color. Default: light blue.")
    text_color: str = Field(default="#2C5F8D", description="Color of the thank you text.")
    bubble_bg_color: str = Field(default="#FFFFFF", description="Background color of the speech bubble. Default: white.")
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
    custom_css: str = Field(default="", description="Additional custom CSS styles to apply.")

class GenerateThankYouSlide7Input(BaseModel):
    """Input schema for generate_thank_you_slide_7 (elegant minimalist thank you slide)."""
    main_text: str = Field(default="THANK YOU!", description="Main text to display. Default: 'THANK YOU!'.")
    bg_color: str = Field(default="#F5F3F0", description="Background color of the slide. Default: light warm gray (#F5F3F0).")
    text_color: str = Field(default="#7A6350", description="Color of the main text. Default: brown/taupe (#7A6350).")

class GenerateModernContactSlideInput(BaseModel):
    """Input schema for generate_modern_contact_slide."""
    main_title: str = Field(default="Thank You For Attention", description="The central large text (e.g., 'Thank You', 'Contact Us').")
    company_name: str = Field(default="Thynk Unlimited", description="Name of the company displayed near the logo.")
    website: str = Field(default="www.reallygreatsite.com", description="Website URL to display.")
    email: str = Field(default="hello@reallygreatsite.com", description="Contact email address.")
    phone: str = Field(default="+123-456-7890", description="Contact phone number.")
    primary_color: str = Field(default="#1E88E5", description="Main accent color (hex code, typically blue) for the geometric shape.")
    secondary_color: str = Field(default="#1565C0", description="Darker shade (hex code) for gradients/depth.")
    text_color: str = Field(default="#FFFFFF", description="Color of the main title text on the colored background.")
    contact_text_color: str = Field(default="#333333", description="Color of the contact details on the white background.")
    top_image_url: str = Field(default="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop", description="URL for the top-right background image (charts/abstract).")
    bottom_image_url: str = Field(default="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=2070&auto=format&fit=crop", description="URL for the bottom-right corner image (team/office).")
    show_logo: Optional[bool] = Field(default=True, description="Whether to display the logo placeholder.")

class GenerateClosingSlideInput(BaseModel):
    """Input schema for generate_closing_slide."""
    main_text: str = Field(default="THANK\nYOU!", description="The large closing text displayed on the right. Use newline characters for multiple lines.")
    quote_text: str = Field(default="“Efficiency opens up more time to focus on the things that really matter.”", description="A closing thought, quote, or secondary message displayed on the left.")
    contact_text: str = Field(default="@reallygreatsite", description="Contact information or social media handle.")
    image_url: str = Field(default="https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", description="URL for the feature image which will be masked in a circle.")
    bg_color: str = Field(default="#FDFBF7", description="Background color of the slide (hex code). Default is a warm off-white.")
    primary_color: str = Field(default="#263238", description="Color for the text and main graphic elements (hex code). Default is dark slate.")
    accent_shape_color: str = Field(default="#DDE6ED", description="Color for the decorative background shape behind the image (hex code).")
    show_sunburst: Optional[bool] = Field(default=True, description="Whether to show the sunburst/line graphic.")
    show_dots: Optional[bool] = Field(default=True, description="Whether to show the dot grid pattern.")
    custom_css: str = Field(default="", description="Additional custom CSS to be included.")

class GenerateMinimalistThankYouSlideInput(BaseModel):
    """Input schema for generate_minimalist_thank_you_slide."""
    main_title: str = Field(default="THANK<br>YOU", description="The main large text centered on the slide. Use <br> for line breaks. Default: 'THANK<br>YOU'.")
    company_name: str = Field(default="Timmerman Industries", description="Vertical text displayed on the left side. Default: 'Timmerman Industries'.")
    date_text: str = Field(default="02 May, 2024", description="Date or footer text displayed at the bottom right. Default: '02 May, 2024'.")
    primary_color: str = Field(default="#59664D", description="Main accent color for text and decorations (Hex code). Default: Olive Green (#59664D).")
    secondary_color: str = Field(default="#E8E8E8", description="Color for the background geometric blocks (Hex code). Default: Light Gray (#E8E8E8).")
    bg_color: str = Field(default="#FFFFFF", description="Background color of the slide (Hex code). Default: White.")
    show_shapes: Optional[bool] = Field(default=True, description="Whether to show the decorative corner rectangles. Default: True.")
    custom_css: str = Field(default="", description="Additional custom CSS to append to the style block.")

class GenerateMinimalistSageSlideInput(BaseModel):
    """Input schema for generate_minimalist_sage_slide."""
    main_text: str = Field(default="THANK YOU", description="The central, largest text on the slide. Default: 'THANK YOU'.")
    top_text: str = Field(default="Timmerman Industries", description="Small text displayed at the top center. Default: 'Timmerman Industries'.")
    bottom_text: str = Field(default="02 May, 2024", description="Small text displayed at the bottom center. Default: '02 May, 2024'.")
    bg_color: str = Field(default="#F7F9F9", description="The background color of the slide (Hex code). Default: Off-white.")
    accent_color: str = Field(default="#FFDAC1", description="Color for the glowing accents/orbs (Hex code). Default: Pastel Peach.")
    shape_color: str = Field(default="#E0E7E5", description="Color for the large geometric curved shapes (Hex code). Default: Sage Green.")
    text_color: str = Field(default="#1A2F28", description="Color of the text elements (Hex code). Default: Dark Green.")
    show_glow_effects: bool = Field(default=True, description="Whether to render the soft blurred gradient orbs.")

class GenerateThankYouSoMuchSlideInput(BaseModel):
    """Input schema for generate_thank_you_so_much_slide."""
    main_text: str = Field(default="Thank You", description="The primary large text displayed (Bold weight).")
    sub_text: str = Field(default="So Much", description="The secondary large text displayed below the main text (Light/Thin weight).")
    presenter_label: str = Field(default="Presented by :", description="Label text above the presenter's name.")
    presenter_name: str = Field(default="Cahaya Dewi", description="Name of the presenter displayed in the bottom left.")
    organization_name: str = Field(default="Larana University", description="Name of the university or organization shown in the header.")
    phone_number: str = Field(default="+123-456-7890", description="Contact phone number.")
    website: str = Field(default="www.reallygreatsite.com", description="Contact website URL.")
    email: str = Field(default="hello@reallygreatsite.com", description="Contact email address.")
    bg_color: str = Field(default="#F9F7F2", description="Primary background color (hex code). Default is a light cream/beige.")
    text_color: str = Field(default="#5A6B6D", description="Primary text color (hex code). Default is a slate grey.")
    accent_color: str = Field(default="#5A6B6D", description="Color for icons and graphical elements.")
    show_corner_accent: Optional[bool] = Field(default=True, description="Whether to show the decorative geometric arrow in the bottom left corner.")

class GenerateBrandCollaborationClosingSlideInput(BaseModel):
    """Input schema for generate_brand_collaboration_closing_slide."""
    main_title: str = Field(default="Thank you", description="The large central title text. Default: 'Thank you'.")
    message_text: str = Field(
        default="THANK YOU FOR TAKING THE TIME TO VIEW THIS PRESENTATION. I APPRECIATE YOUR INTEREST AND CONSIDERATION, AND I'M EXCITED ABOUT THE POSSIBILITY OF WORKING TOGETHER.", 
        description="The uppercase body paragraph below the title."
    )
    signature_text: str = Field(default="Looking forward to connecting soon!", description="The handwritten-style text at the bottom center.")
    brand_header: str = Field(default="BRAND COLLABORATION", description="Small uppercase text in the top left corner.")
    website_url: str = Field(default="WWW.REALLYGREATSITE.COM", description="Small uppercase text in the top right corner.")
    prepared_by: str = Field(default="PREPARED BY:<br>OLIVIA WILSON", description="Text for the bottom left corner (supports <br> for line breaks).")
    date_text: str = Field(default="DATE:<br>01\\06\\2030", description="Text for the bottom right corner (supports <br> for line breaks).")
    primary_color: str = Field(default="#1D4E89", description="The main color for text (Hex code). Default: Deep Blue.")
    bg_color: str = Field(default="#F5F2EB", description="The background color (Hex code). Default: Light Paper Beige.")
    left_image_url: str = Field(
        default="https://images.unsplash.com/photo-1519052537078-e6302a4968d4?q=80&w=1740&auto=format&fit=crop", 
        description="URL for the large vertical image on the left."
    )
    right_image_url: str = Field(
        default="https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1740&auto=format&fit=crop", 
        description="URL for the smaller image on the right."
    )

class GenerateMilitaryThankYouSlideInput(BaseModel):
    """Input schema for generate_military_thank_you_slide."""
    main_text: str = Field(default="THANK YOU", description="The main large text on the slide, typically 'THANK YOU' or a section title.")
    description: str = Field(default="Contact us for further information.", description="Small descriptive paragraph or contact details displayed below the title.")
    bg_image_url: str = Field(default="https://images.unsplash.com/photo-1590236141044-bc849495115d?q=80&w=1920", description="URL for the background image showing military personnel or equipment.")
    primary_color: str = Field(default="#4B5320", description="The primary olive green/military color for the design accents (Hex).")
    secondary_color: str = Field(default="#556B2F", description="The secondary lighter green or accent color (Hex).")
    text_color: str = Field(default="#000000", description="The color of the typography (Hex).")
    overlay_opacity: float = Field(default=0.2, description="The opacity of the white overlay on the background image (0.0 to 1.0).")

class GenerateCorporate2ThankYouInput(BaseModel):
    """Input schema for generate_corporate2_thank_you_slide ."""
    main_title: str = Field(default="THANK YOU", description="The large main title text displayed prominently (e.g., 'THANK YOU').")
    closing_message: str = Field(default="We look forward to collaborating with you.", description="Closing message or subtitle text displayed below the main title.")
    contact_email: str = Field(default="contact@business.com", description="Contact email address to display on the slide.")
    website: str = Field(default="www.business.com", description="Website URL to display on the slide.")
    primary_color: str = Field(default="#1E3A8A", description="Primary color for decorative elements and accents (Hex code).")
    accent_color: str = Field(default="#3B82F6", description="Accent color for highlights and secondary elements (Hex code).")
    text_color: str = Field(default="#7A6350", description="Color for the main text content (Hex code).")
    bg_color: str = Field(default="#F5F3F0", description="Background color of the slide (Hex code).")

class GenerateCreativeThankYouInput(BaseModel):
    """Input schema for generate_creative_thank_you_slide ."""
    main_title: str = Field(default="Any Questions?", description="The large main title text displayed prominently (e.g., 'Any Questions?', 'Thank You').")
    subtitle: str = Field(default="THANKS FOR WATCHING", description="Subtitle text displayed below or above the main title, typically in uppercase.")
    image_url: str = Field(default="https://images.unsplash.com/photo-1516321497487-e288fb19713f?q=80&w=2940&auto=format&fit=crop", description="URL of the background or decorative image to display on the slide.")
    bg_gradient_start: str = Field(default="#F5F3F0", description="Starting color of the background gradient (Hex code).")
    bg_gradient_end: str = Field(default="#F5F3F0", description="Ending color of the background gradient (Hex code).")
    accent_color: str = Field(default="#BE123C", description="Accent color for decorative elements and highlights (Hex code).")

class GenerateTechThankYouInput(BaseModel):
    main_title: str = Field(default="THANK YOU", description="The main title text displayed prominently in large letters (e.g., 'THANK YOU').")
    social_handle: str = Field(default="@tech_studio", description="Social media handle or username to display (e.g., '@tech_studio', '@yourcompany').")
    primary_neon: str = Field(default="#00FFFF", description="Primary neon color for glowing effects and accent elements (Hex code).")
    bg_dark: str = Field(default="#1a1a2e", description="Dark background color of the slide (Hex code).")

class GenerateMinimalistThankYouInput2(BaseModel):
    main_title: str = Field(default="END.", description="The main title text displayed prominently in large, bold letters (e.g., 'END.', 'THANK YOU').")
    footer_note: str = Field(default="2026 Portfolio Studio", description="Footer note or information displayed at the bottom of the slide (e.g., '2026 Portfolio Studio', company name, date).")
    text_color: str = Field(default="#000000", description="Text color for all text elements on the slide (Hex code).")
    bg_color: str = Field(default="#FFFFFF", description="Background color of the slide (Hex code).")

class GenerateElegantThankYouInput(BaseModel):
    main_title: str = Field(default="Thank You", description="The stylized, decorative thank you text displayed in elegant script or serif font.")
    subtitle: str = Field(default="FOR YOUR KIND ATTENTION", description="Subtitle text displayed below the main title, typically in uppercase letters.")
    bg_image: str = Field(default="https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=2069&auto=format&fit=crop", description="URL of the elegant or sophisticated background image to display on the slide.")
    overlay_color: str = Field(default="rgba(255, 255, 255, 0.85)", description="Semi-transparent overlay color applied over the background image to ensure text readability (RGBA format).")


#---LINE CHART SLIDES-------------------------------------------------------------------------    
class GenerateLineChartSlide2(BaseModel):
    """Schema for generate_line_chart_slide_2"""
    main_title: str = Field(..., description=(  
            "Primary headline of the slide describing the overall evolution or trend "
            "displayed in the line chart (10–60 characters). "
            "The title should communicate insight or direction, not just restate the metric name. "
            "Example: Improvement of Model Accuracy During Training"
        ),
    )
    subtitle: Optional[str] = Field(..., description=(
            "Contextual information that frames the chart, such as model type, dataset, "
            "training duration, or experimental setting. "
            "This helps the audience understand where and how the time-series data was produced. "
            "Example: CNN trained on Image Classification Dataset (50 Epochs)"
        )
    )
    insight: Optional[str] = Field(..., description=(
            "A short analytical takeaway highlighting key patterns in the data, "
            "such as convergence speed, stabilization, divergence between series, "
            "or signs of overfitting. "
            "This field should explain why the trend matters rather than repeating values. "
            "Example: Training accuracy rises steadily, while validation accuracy plateaus after Epoch 20, suggesting mild overfitting."
        )
    )

    x_axis: str = Field(
        ...,
        description="Label for the X-axis (time progression). Example: Epoch."
    )
    y_axis: str = Field(
        ...,
        description="Label for the Y-axis metric being measured. Example: Accuracy."
    )
    unit: str = Field(
        ...,
        description="Unit suffix appended to values when labels are shown. Example: %."
    )
    show_value: bool = Field(
        default=False,
        description="Whether to display numeric labels on chart points."
    )
    show_legend: bool = Field(
        default=True,
        description="Whether to display chart legend for multiple series."
    )
    y_axis_min: Optional[float] = Field(
        default=40,
        description="Minimum Y-axis value used for chart scaling."
    )
    y_axis_max: Optional[float] = Field(
        default=100,
        description="Maximum Y-axis value used for chart scaling."
    )
    data_label_format: Optional[str] = Field(
        default=None,
        description="Optional formatting template for value labels. Example: {value}% or {value} pts."
    )
    colors: List[str] = Field(
        default=["#4F46E5", "#22C55E"],
        description="Color list used for each line series in order."
    )
    time_points: List[str] = Field(
        ...,
        description="Ordered labels along the X-axis representing time progression. Example: ['Epoch 1', 'Epoch 5', 'Epoch 10', 'Epoch 15', 'Epoch 20', 'Epoch 25', 'Epoch 30']."
    )
    series: List[Dict[str, str | List[Dict[str, float]]]] = Field(
        ...,
        description="Series data for the line chart. Each object should include 'name' and 'values'. Example: [{'name': 'Training Accuracy', 'values': [45, 62, 75, 84, 90, 94, 97]}, {'name': 'Validation Accuracy', 'values': [43, 60, 73, 82, 87, 88, 88]}]."
    )

    font_family: str = Field(
        default="Inter, sans-serif",
        description="Main font family used across the slide."
    )
    
    accent_color: str = Field(
        default="#4F46E5",
        description=(
            "Primary accent color used for highlights, markers, or emphasis elements. "
            "This color should complement the line colors while maintaining visual balance."
        )
    )
    main_title_color: str = Field(
        default="#1F2937",
        description=(
            "Text color for the main title, chosen to create strong visual hierarchy "
            "and immediately communicate the slide’s key message."
        )
    )
    subtitle_color: str = Field(
        default="#4B5563",
        description=(
            "Color applied to subtitle text, intentionally softer than the main title "
            "to provide context without competing for attention."
        )
    )
    insight_text_color: str = Field(
        default="#374151",
        description=(
            "Color used for the insight section, optimized for comfortable reading "
            "of analytical commentary beneath the chart."
        )
    )
    body_background_color: str = Field(
        default="#ffffff",
        description="Background color of the slide body."
    )
    left_shape_background_color: str = Field(
        default="#f1fcf4",
        description="Background color of the decorative left circular shape."
    )
    right_panel_background_color: str = Field(
        default="rgba(255, 255, 255, 0.6)",
        description="Background color of the right chart panel."
    )
    insight_background_color: str = Field(
        default="#f8fafc",
        description="Background color of the insight card."
    )


class GenerateLineChartSlide3(BaseModel):
    """Schema for generate_line_chart_slide_3"""
    main_title: str = Field(..., description=(
            "Main headline communicating the overall direction or competitive "
            "movement shown in the chart (10–60 characters). "
            "The title should reflect a meaningful observation rather than "
            "simply naming the metric. "
            "Example: EV Sales Momentum Accelerates Across Major Brands"
        ),
    )

    subtitle: Optional[str] = Field(..., description=(
            "Supporting context that clarifies the scope of the dataset, "
            "such as geographic market, reporting period, or data source. "
            "This helps viewers interpret the time-series correctly. "
            "Example: Southeast Asia Market – January to December 2026"
        )
    )

    insight: str = Field(..., description=(
            "Concise analytical commentary summarizing the most important "
            "patterns observed in the chart. "
            "This may highlight acceleration, seasonal peaks, widening gaps "
            "between brands, or emerging leaders. "
            "The explanation should focus on interpretation and implications, "
            "not just restating numeric values."
        )
    )

    x_axis: str = Field(
        default="Month",
        description=(
            "Label for the horizontal (X) axis, describing the time dimension "
            "or categorical grouping of the data points. "
            "Example: 'Month', 'Quarter', 'Week'."
        )
    )

    y_axis: str = Field(
        default="Units Sold",
        description=(
            "Label for the vertical (Y) axis, describing the measured metric. "
            "Example: 'Units Sold', 'Revenue (USD)', 'Market Share (%)'."
        )
    )

    unit: str = Field(
        default="K",
        description=(
            "Unit suffix appended to numeric values on the chart axes or data labels. "
            "Example: 'K' for thousands, 'M' for millions, '%' for percentages."
        )
    )

    show_value: bool = Field(
        default=False,
        description=(
            "Whether to display numeric data labels directly on each data point "
            "along the lines. Useful for dense datasets where exact values matter."
        )
    )

    show_legend: bool = Field(
        default=True,
        description=(
            "Whether to display the series legend panel alongside the chart. "
            "Recommended when there are multiple series to distinguish."
        )
    )

    y_axis_min: float = Field(
        default=20,
        description=(
            "Minimum value for the Y axis scale. "
            "Setting this above zero can emphasize relative differences between series. "
            "Example: 20 (starts axis at 20 instead of 0)."
        )
    )

    y_axis_max: float = Field(
        default=140,
        description=(
            "Maximum value for the Y axis scale. "
            "Should be set above the highest data value to avoid clipping. "
            "Example: 140."
        )
    )

    data_label_format: str = Field(
        default="{value}K",
        description=(
            "Template string for formatting data point labels when show_value is True. "
            "Use '{value}' as the placeholder for the numeric value. "
            "Example: '{value}K', '{value}%', '${value}M'."
        )
    )

    colors: List[str] = Field(
        default=["#00F2FF", "#8B5CF6", "#EC4899"],
        description=(
            "Ordered list of hex color codes assigned to each series in the chart. "
            "Colors are cycled if there are more series than colors provided. "
            "Each color is used for the line stroke, data point markers, and legend indicator. "
            "Example: ['#00F2FF', '#8B5CF6', '#EC4899']."
        )
    )

    time_points: List[str] = Field(
        ...,
        description=(
            "Ordered list of labels for each point on the X axis, representing "
            "the time intervals or categories at which data is recorded. "
            "The length of this list determines the number of data points per series. "
            "Example: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] "
            "or ['Q1', 'Q2', 'Q3', 'Q4']."
        )
    )

    series: List[Dict[str, str | List[float]]] = Field(
        ...,
        description=(
            "List of data series objects to plot on the line chart. "
            "Each object must contain: "
            "'name' (str) — the series label shown in the legend; "
            "'values' (List[float]) — numeric data points corresponding to each time_point in order. "
            "The length of each 'values' list must match the length of time_points. "
            "Example: [{'name': 'Tesla', 'values': [45, 60, 90, 130]}, "
            "{'name': 'BYD', 'values': [40, 48, 52, 58]}, "
            "{'name': 'VinFast', 'values': [30, 35, 40, 44]}]."
        )
    )


    accent_color: str = Field(
        default="#00F2FF",
        description=(
            "Primary highlight color used for decorative elements, "
            "emphasis accents, or active markers. "
            "It should align with the dark-tech theme of the slide."
        )
    )

    main_title_color: str = Field(
        default="#FFFFFF",
        description=(
            "Text color of the main title. "
            "Designed to provide strong contrast against a dark background "
            "and immediately draw viewer attention."
        )
    )

    subtitle_color: str = Field(
        default="#94A3B8",
        description=(
            "Secondary text color used for contextual information. "
            "It should be visually softer than the main title "
            "while remaining clearly legible."
        )
    )

    insight_text_color: str = Field(
        default="#E2E8F0",
        description=(
            "Color applied to the analytical insight section. "
            "Optimized for readability in longer explanatory text "
            "under dark presentation themes."
        )
    )

    bg_color: str = Field(
        default="#020617",
        description=(
            "Background color of the slide (hex code). "
            "Default is a very dark navy (#020617) to create a dark-tech theme. "
            "Example: '#020617', '#0A0A1A', '#1a1a2e', '#FFFFFF'."
        )
    )

class GenerateRadarChartSlide1(BaseModel):
    """
    Input schema strictly matching generate_radar_chart_slide_1 function.
    This schema describes parameters used to generate a radar chart slide
    """
    # ===== CONTENT =====
    main_title: str = Field(..., description="Main title of the radar chart slide.")
    subtitle: str = Field(..., description="Subtitle providing context such as report source or timeframe.")
    insight: str = Field(..., description="Key takeaway or analysis derived from the radar chart.")
    # ===== DISPLAY OPTIONS =====
    unit: str = Field(..., description="Unit of measurement (e.g., điểm, %, level).")
    show_value: bool = Field(default=True, description="Show value labels on each data point.")
    data_label_format: str = Field(default="{value}", description="Format string for data labels (e.g., {value}/10).")
    # ===== RADAR STRUCTURE =====
    axes: List[str] = Field(..., description="List of dimensions (axes). Example: ['Medical', 'Psychological', 'Nutrition']")
    series: List[Dict[str, str | List[float]]] = Field(..., description=
        """
        List of data series. Each series contains a label and values array. Values length must match axes length.
        Example:
        [
            {
                "label": "Current",
                "values": [8, 7, 9, 6, 8]
            },
        ]   
        """
    )
    # ===== RADAR CONFIG =====
    max_value: float = Field(default=10, description="Maximum value of the radar scale.")
    num_levels: int = Field(default=5, description="Number of grid levels (rings).")
    show_grid_lines: bool = Field(default=True, description="Show background grid levels.")
    show_axis_lines: bool = Field(default=True, description="Show axis lines.")
    # ===== COLORS =====
    axis_color: str = Field(default="#D1D5DB", description="Color of axis lines.")
    grid_color: str = Field(default="#E5E7EB", description="Color of grid lines.")
    label_color: str = Field(default="#374151", description="Color of axis labels.")
    accent_color: str = Field(default="#F4A261", description="Primary accent color.")
    background: str = Field(default="#F8F8F8", description="Solid background color of the slide/canvas.")
    background_image: str = Field(default="none", description="Background image source (URL, CSS image value, or 'none').")
    insight_box_background: str = Field(default="rgba(71, 123, 157, 0.10)", description="Background color of the insight/commentary box.")
    legend_background: str = Field(default="#FFFFFF", description="Background color of the legend container.")
    legend_swatch_current_background: str = Field(default="#1D3557", description="Legend swatch color representing the current series.")
    legend_swatch_target_background: str = Field(default="#F4A261", description="Legend swatch color representing the target/benchmark series.")
    # ===== STYLE =====
    main_title_color: str = Field(default="#1D3557", description="Color of main title.")
    subtitle_color: str = Field(default="#457B9D", description="Color of subtitle.")
    insight_text_color: str = Field(default="#1D3557", description="Color of insight text.")

class GeneratePieChartSlide1(BaseModel):
    """
    Input schema for generate_pie_chart_slide_1
    This schema defines all visual and content elements required to render the slide,
    including titles, data, styling, and display options.
    """
    main_title: str = Field(..., description="Primary heading of the slide. Should clearly describe what the pie chart represents.")
    subtitle: str = Field(..., description="Secondary text displayed below the main title. Typically used for data source, timeframe, or additional context.")
    insight: str = Field(..., description="Short analytical takeaway or key message derived from the chart data. Should highlight the most important insight.")
    chart_type: str = Field(default="pie", description="Type of chart: 'pie' (full) or 'donut' (ring-style with center space).")
    unit: str = Field(default="%", description="Unit of measurement for the values (e.g., %, $, users). This may be displayed in labels or legends.")
    show_value: bool = Field(default=True, description="Controls whether numeric values are displayed directly on the pie chart slices.")
    show_legend: bool = Field(default=True, description="Controls whether the legend (mapping colors to labels) is displayed on the slide.")
    data_label_format: str = Field(default="{value}{unit}", description="Template string for formatting data labels on the chart. Use placeholders like {value}, {label}, or {unit}.")
    colors: List[str] = Field(default=["#5FD9D3", "#4ABFB9", "#36A6A0", "#248C87"], description="List of colors for pie chart slices. Each color corresponds to an item in 'items' by index order.")
    items: List[Dict[str, str | float]] = Field(..., 
        description=(
            "List of data points for the pie chart. "
            "Each item must be an object with 'label' (string) and 'value' (number). "
            "Example: {\"label\": \"AI Services\", \"value\": 45}"
        )
    )
    accent_color: str = Field(default="#5FD9D3", description="Primary accent color used for highlights and borders.")
    main_title_color: str = Field(default="#5FD9D3", description="Color of the main title.")
    subtitle_color: str = Field(default="#FFFFFF", description="Color of the subtitle.")
    insight_text_color: str = Field(default="#FFFFFF", description="Color of the insight text.")
    background_color: str = Field(default="#0F172A", description="Background color of the slide.")

class GenerateScatterPlotChartSlide2(BaseModel):
    """Input schema for generate_scatter_plot_chart_slide_2"""
    main_title: str = Field(..., description="""
            "Main title of the slide, summarizing the core message of the scatter plot "
            "within a travel context (10–60 characters). "
            "Example: Relationship Between Travel Distance and Spending"""
        )
    subtitle: str = Field(..., description="""
            "Subtitle or supplementary information such as data source, survey scope, "
            "or collection period. "
            "Example: Source: Tourist Behavior Survey 2024"
        """)
    insight: str = Field(..., description="""
            "A concise analytical statement derived from the chart, highlighting key trends, "
            "correlations, or notable outliers in travel behavior. "
            "Example: International travelers spend disproportionately more for trips above 7000 km."
        """)
    x_axis: str = Field(
        ...,
        description="Label for the X-axis metric represented in the scatter plot. Example: Travel Distance (km)."
    )
    y_axis: str = Field(
        ...,
        description="Label for the Y-axis metric represented in the scatter plot. Example: Total Travel Spending (USD)."
    )
    unit: str = Field(
        ...,
        description="Unit suffix used when displaying point value labels. Example: USD, $, k VND."
    )
    show_value: bool = Field(
        default=False,
        description="Whether to show value labels above each scatter point. Example: True."
    )
    show_legend: bool = Field(
        default=True,
        description="Whether to display the legend panel for each data series. Example: True."
    )
    x_axis_min: float = Field(
        default=0,
        description="Minimum value for the X-axis scale. Example: 0."
    )
    x_axis_max: float = Field(
        default=12000,
        description="Maximum value for the X-axis scale. Example: 12000."
    )
    y_axis_min: float = Field(
        default=0,
        description="Minimum value for the Y-axis scale. Example: 0."
    )
    y_axis_max: float = Field(
        default=6000,
        description="Maximum value for the Y-axis scale. Example: 6000."
    )
    colors: List[str] = Field(
        default=["#008080", "#FFB347"],
        description="Color palette applied to scatter series points in order. Example: ['#008080', '#FFB347']."
    )
    background_color: str = Field(
        default="#FEF9E1",
        description="Background color of the full slide. Example: #FEF9E1."
    )
    insight_box_background_color: str = Field(
        default="#FFFFFF",
        description="Background color of the insight text box. Example: #FFFFFF."
    )
    chart_panel_background_color: str = Field(
        default="rgba(255, 255, 255, 0.5)",
        description="Background color of the chart container panel. Example: rgba(255, 255, 255, 0.5)."
    )
    series: List[Dict[str, str | List[Dict[str, float]]]] = Field(
        ...,
        description=(
            "List of scatter data series. Each series includes 'name' and 'points'; "
            "each point is an object with numeric 'x' and 'y' values. "
            "Example: [{'name': 'Domestic Travelers', 'points': [{'x': 150, 'y': 300}, {'x': 1200, 'y': 1100}]}]."
        )
    )
    accent_color: str = Field(
        default="#008080",
        description="Primary accent color (CSS value) used for decorative and emphasis elements. Example: #008080."
    )
    main_title_color: str = Field(
        default="#005F5F",
        description="Text color for the main title, designed to stand out against the slide background. Example: #005F5F."
    )
    subtitle_color: str = Field(
        default="#556B2F",
        description="Text color for the subtitle or data source information. Example: #556B2F."
    )
    insight_text_color: str = Field(
        default="#2C3E50",
        description="Text color for the insight section, ensuring clarity and neutral tone. Example: #2C3E50."
    )

class GenerateBarChartSlide2(BaseModel):
    """Input schema for generate_bar_chart_slide_2."""
    main_title: str = Field(..., description="""
        Main title of the chart (10–60 characters). Example: Ocean Temperature vs. Depth Analysis
        """)
    subtitle: str = Field(..., description="""
        Subtitle, unit, or data source. Example: Data Source: Marine Institute 2025
        """)
    insight: str = Field(..., description="""
        Description or main insight of the slide. Example: Temperature drops steadily as depth increases in both oceans.
        """)

    x_axis: str = Field(
        ...,
        description="Label for the X-axis metric. Example: Ocean Depth (meters)."
    )

    y_axis: str = Field(
        ...,
        description="Label for the Y-axis metric. Example: Average Temperature °C."
    )

    unit: str = Field(
        ...,
        description="Unit suffix used for values. Example: °C."
    )

    show_value: bool = Field(
        default=True,
        description="Whether to show value labels on bars. Example: True."
    )

    show_legend: bool = Field(
        default=True,
        description="Whether to show the legend panel. Example: True."
    )

    y_axis_min: float = Field(
        default=0,
        description="Minimum value for Y-axis scale. Example: 0."
    )

    y_axis_max: Optional[float] = Field(
        default=None,
        description="Maximum value for Y-axis scale. Example: 30."
    )

    data_label_format: Optional[str] = Field(
        default=None,
        description="Template format for data labels. Example: {value}°C."
    )

    colors: List[str] = Field(
        default=["#00695C", "#26A69A"],
        description="Color palette for each bar series. Example: ['#00695C', '#26A69A']."
    )

    background_color: str = Field(
        default="#E0F7FA",
        description="Background color of the full slide. Example: #E0F7FA."
    )

    insight_box_background_color: str = Field(
        default="rgba(255, 255, 255, 0.5)",
        description="Background color for the insight box. Example: rgba(255, 255, 255, 0.5)."
    )

    chart_panel_background_color: str = Field(
        default="rgba(255, 255, 255, 0.6)",
        description="Background color of the chart panel. Example: rgba(255, 255, 255, 0.6)."
    )

    categories: List[str] = Field(
        default=["Surface", "50m", "100m", "200m", "500m"],
        description="Categories shown on X-axis. Example: ['Surface', '50m', '100m', '200m', '500m']."
    )

    series: List[Dict[str, str | List[float]]] = Field(
        default=[
            {
                "name": "Pacific Ocean",
                "values": [28, 22, 18, 12, 5]
            },
            {
                "name": "Atlantic Ocean",
                "values": [26, 21, 17, 11, 4]
            }
        ],
        description=(
            "List of bar chart series. Each series has 'name' and 'values'. "
            "Example: [{'name': 'Pacific Ocean', 'values': [28, 22, 18, 12, 5]}]."
        )
    )
    
    
    accent_color: str = Field(
        default="#A67C52",
        description="CSS accent color for decorative elements."
    )
    
    main_title_color: str = Field(
        default="#3D4E5D",
        description="CSS color for the main title."
    )
    
    subtitle_color: str = Field(
        default="#6B7280",
        description="CSS color for subtitle."
    )
    
    insight_text_color: str = Field(
        default="#374151",
        description="CSS color for insight text."
    )


INTRO_TOOLS = [
    # === SLIDE INTRO ===
    StructuredTool.from_function(
        func=generate_title_slide,
        name="generate_title_slide",
        description="""Generates a professional and corporate Title Slide featuring a centered text alignment within a dashed geometric frame. This slide utilizes a 135-degree linear gradient background layered with exactly four floating decorative triangles and an optional silhouette city skyline at the base. Ideal for Business Plans, Annual Reports, or Project Proposals where a structured and authoritative visual identity is required.""",
        args_schema=GenerateTitleSlideInput
    ),
    StructuredTool.from_function(
        func=generate_introduction_slide,
        name="generate_introduction_slide",
        description="""Generates a professional and minimalist Introduction Slide featuring a centered content frame enclosed in a dashed border. Adorned with 4 floating decorative triangles and a subtle 3-shape geometric cluster over a dual-color gradient background. Ideal for opening presentations or setting the tone for a high-level executive summary.""",
        args_schema=GenerateIntroductionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_intro_slide1,
        name="generate_intro_slide1",
        description="Generates a modern and marketing-focused Split-Screen Slide with a 60/40 asymmetrical layout. Features a floating rounded content box on the left balanced by a framed image container and dual horizontal accent bars. Ideal for brand introductions or marketing pitches where visual balance is key.",
        args_schema=GenerateIntroSlide1Input
    ),
    StructuredTool.from_function(
        func=generate_elegant_intro_slide,
        name="generate_elegant_intro_slide",
        description="""Generates an elegant and sophisticated Media Intro Slide utilizing a balanced 2-column grid. Defined by a unique botanical frame SVG and a 3-star gold gradient cluster decorating a 16:9 image wrapper. Ideal for creative portfolios, lifestyle presentations, or luxury brand stories where aesthetics are paramount.""",
        args_schema=GenerateElegantIntroSlideInput
    ),

    StructuredTool.from_function(
        func=generate_title_slide_2,
        name="generate_title_slide_2",
        description="""Generates a corporate and dynamic Title Slide featuring a sharp vertical diagonal split layout. Incorporates a shadow-offset color panel and a 3-row minimalist line-chart icon for technical emphasis. Ideal for corporate quarterly reports or high-stakes business strategy sessions.""",
        args_schema=GenerateTitleSlide2Input
    ),
    StructuredTool.from_function(
        func=generate_business_intro_slide,
        name="generate_business_intro_slide",
        description="Generates a high-impact and energetic Vision Slide using a bold angled polygon divider. Detailed with a decorative footer containing a 2x2 geometric dot grid and concentric arc patterns alongside a full-bleed image. Ideal for mission statements, startup pitch decks, or motivational segments.",
        args_schema=GenerateBusinessIntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_dynamic_intro_slide,
        name="generate_dynamic_intro_slide",
        description="Generates a bold and creative Concept Highlight Slide arranged in a 1.2:1 grid layout. Showcases a custom space-themed vector set including a blue planet and 3 yellow stars, framed by a 7-piece layered geometric shape cluster in the corners. Ideal for brainstorming sessions or emphasizing a single revolutionary key takeaway.",
        args_schema=GenerateDynamicIntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_big_concept_slide,
        name="generate_big_concept_slide",
        description="Generates a minimalist and sophisticated Table of Contents Slide featuring a 2-column centered layout. Distinguishable by a signature Dusty Rose accent-block backdrop that offsets a single framed image against a clean list of agenda items. Ideal for outlining meeting roadmaps or providing a structured overview of presentation topics.",
        args_schema=GenerateBigConceptSlideInput
    ),
    StructuredTool.from_function(
        func=generate_elegant_agenda_slide,
        name="generate_elegant_agenda_slide",
        description="Generates a whimsical and educational Character Title Slide featuring a 50/50 vertical split with a colored 15% bottom horizon bar. Centered around a unique hand-drawn penguin SVG doodle and 4 organic star-wave scribbles. Ideal for children's education, storytelling, or lighthearted workshop introductions.",
        args_schema=GenerateElegantAgendaSlideInput
    ),
    StructuredTool.from_function(
        func=generate_playful_title_slide,
        name="generate_playful_title_slide",
        description="Generates a whimsical and friendly Hand-drawn Title Slide featuring a 50/50 vertical split with a hand-drawn penguin SVG, organic star-wave scribbles, and a 15% height bottom horizon bar. Ideal for children's education or lighthearted storytelling topics where a charming and approachable feel is needed.",
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
        func = generate_title_slide_5,
        name="generate_title_slide_5",
        description="Generates a warm and nostalgic **Title or Introduction Slide** with a notebook cover design aesthetic. Features a tilted polaroid-style photo frame with decorative hand-drawn doodles, a four-leaf clover icon, horizontal decorative lines at top and bottom, and personalized text elements in corners ('Our shared moments', year). The soft blue-gray background combined with elegant typography creates a scrapbook-like, memory-capturing feel. Perfect for personal presentations, photo albums, travel stories, memory collections, family events, or any presentation wanting an intimate, handcrafted, and sentimental opening that evokes cherished moments and personal connections.",
        args_schema=GenerateTitleSlide5Input,
    ),

    StructuredTool.from_function(
        func=generate_title_slide_7,
        name="generate_title_slide_7",
        description="""Generates a playful and crafty Title Slide featuring a centered 1100px text frame with a thick border. Distinguished by a single floating 220x70px bandage-core element anchored above the frame to create a unique "pasted" look. Ideal for casual team syncs or creative project workshops.""",
        args_schema=GenerateTitleSlide7Input
    ),
    StructuredTool.from_function(
        func=generate_title_slide_11,
        name="generate_title_slide_11",
        description="""Generates an ultra-minimalist Introduction Slide featuring a sharp 50/50 vertical split background. Defined by its massive 110px serif typography and a clean bisection of two solid colors without any additional geometric noise. Ideal for formal thesis defenses or academic presentations requiring high clarity.""",
        args_schema=GenerateTitleSlide11Input
    )
    ,
    StructuredTool.from_function(
        func=generate_title_slide_12,
        name="generate_title_slide_12",
        description="Generates an elegant and sophisticated Thesis Slide featuring a centered content area enclosed within a 160px inset border frame. Defined by a massive 700px decorative circle anchored to the right edge, bleeding off the slide for a modern asymmetrical touch. Ideal for high-end project proposals or artistic portfolios.",
        args_schema=GenerateTitleSlide12Input
    ),
    StructuredTool.from_function(
        func=generate_title_slide_13,
        name="generate_title_slide_13",
        description="Generates a geometric and math-inspired Functional Slide featuring a centered text layout over a diagonal composition. Characterized by a set of 7 rounded rectangles (pill shapes) rotated at precisely -45 degrees in a multi-layered corner arrangement. Ideal for scientific lectures, logic-based tutorials, or mathematics presentations.",
        args_schema=GenerateTitleSlide13Input
    ),
    StructuredTool.from_function(
        func=generate_title_slide_15,
        name="generate_title_slide_15",
        description="Generates a simple and vibrant Meeting Slide featuring a centered 100px bold title layout. Anchored by two giant 700px diameter corner circles positioned at the top-left and bottom-right extremities to frame the content. Ideal for general business meetings or high-energy project kick-offs.",
        args_schema=GenerateTitleSlide15Input
    ),
    StructuredTool.from_function(
        func=generate_title_slide_17,
        name="generate_title_slide_17",
        description="Generates a clean and modern Town Hall Slide featuring a centered 1400px wide text group. Distinctive for its symmetrical 4-corner decoration, consisting of 8 identical 150px semi-visible circles paired at every corner of the slide. Ideal for all-hands company meetings or collaborative announcement headers.",
        args_schema=GenerateTitleSlide17Input
    ),
    StructuredTool.from_function(
        func=generate_title_slide_18,
        name="generate_title_slide_18",
        description="Generates a textured and architectural Title Slide featuring a floating 850x650px content card. Set against a complex 3D isometric cube pattern background generated via custom SVG with exactly 80x140px pattern units. Ideal for strategic planning, architectural overviews, or design-heavy presentations.",
        args_schema=GenerateTitleSlide18Input
    ),

    
]

TRANSITION_TOOLS = [
    # === SLIDE CHUYỂN SLIDE ===
    StructuredTool.from_function(
        func=generate_dusk_transition_slide,
        name="generate_dusk_transition_slide",
        description="Generates a minimalist, tech-focused Section Break or Transition Slide. It combines the dramatic dusk color scheme (purple-to-orange gradient) with the clean, modern aesthetic of a dot-grid background. This version removes the soft clouds/orbs for a more direct, uncluttered look, while keeping the animated rockets. It's perfect for marking new chapters in a technology, data, or corporate presentation that requires a sophisticated yet energetic visual.",
        args_schema=GenerateDuskTransitionSlideInput
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
        func=generate_section_header_slide_15,
        name="generate_section_header_slide_15",
        description="Generates a Christmas-themed section header slide with festive gradient blobs and Christmas tree SVG illustration on the right. Features dark evergreen background, white text, and colorful festive gradient blobs (red, green, gold). Layout uses flexbox with text content on left (65% width) and SVG container on right (35% width). Text is large, italic, and bold. No animations. Perfect for holiday presentations and festive section dividers. Includes embedded Christmas tree SVG with ornaments and star.",
        args_schema=GenerateSectionHeaderSlide15Input
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide_17,
        name="generate_section_header_slide_17",
        description="Generates a section header slide with centered title, subtitle, decorative circles at corners, and horizontal bars. Features Montserrat typography with customizable colors for background, title, subtitle, corner circles, and decorative bars. Perfect for project schedules, section dividers, and minimalist transitions.",
        args_schema=GenerateSectionHeaderSlide17Input
    ),
    StructuredTool.from_function(
        func=generate_section_header_slide_18,
        name="generate_section_header_slide_18",
        description="Generates a minimalist section header slide with centered title, subtitle, and decorative circles at corners. Features Inter typography with customizable colors for background, title, subtitle, and corner circle groups (blue, yellow, teal). Perfect for modern section dividers and minimalist transitions.",
        args_schema=GenerateSectionHeaderSlide18Input
    ),


]

CONTENT_TOOLS = [
    # === SLIDE CONTENT ===
    StructuredTool.from_function(
        func=generate_content_slide,
        name="generate_content_slide",
        description="Generates a clean and minimalist Content Slide featuring a configurable NxM grid of numbered cards with top-edge accent gradients. This layout utilizes a central focal title and structural content cards with soft shadow depth and subtle border outlines. Ideal for Table of Contents, Agenda Overviews, or Key Takeaway summaries where clear information hierarchy and systematic categorization are required.",
        args_schema=GenerateContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_comparison_slide,
        name="generate_comparison_slide",
        description="""Generates a symmetrical Comparison Slide featuring two vertical content columns separated by a central dashed vertical divider. This layout integrates two distinct SVG icons (defaulting to gavel and scales) centered above paired headings and descriptive body text. Ideal for Pros and Cons analysis, Legal or Ethical comparisons, and "Before vs. After" scenarios where a balanced visual weight between two opposing or complementary concepts is essential.""",
        args_schema=GenerateComparisonSlideInput
    ),
    StructuredTool.from_function(
        func=generate_process_slide,
        name="generate_process_slide",
        description="Generates a dynamic Process Flow Slide featuring two large, rounded content boxes bridged by a central circular floating arrow. This structure utilizes a horizontal bilateral layout with customizable primary and secondary box colors and high-contrast typography. Ideal for Sequential Workflows, Input-Output diagrams, or Strategic Transitions where a clear directional movement from one phase to the next is the primary intent.",
        args_schema=GenerateProcessSlideInput
    ),
    StructuredTool.from_function(
        func=generate_process_steps_slide,
        name="generate_process_steps_slide",
        description="Generates a structured and elegant Multi-step Process Slide featuring a 30/70 vertical split with a colored title panel. This layout utilizes a vertical image strip of exactly three square thumbnails paired with italicized serif typography for a refined aesthetic. Ideal for detailing implementation plans, digital transformation roadmaps, or chronological project phases.",
        args_schema=GenerateProcessStepsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_image_cutout_list_slide,
        name="generate_image_cutout_list_slide",
        description="Generates a sophisticated and modern Key Points List Slide featuring a 70% width right-aligned content panel layered over a full-bleed background. This design includes a unique rotating geometric spinner and a vertical guide line with distinct spherical bullet points for high-end readability. Ideal for showcasing core business values, primary strategic objectives, or executive summary points.",
        args_schema=GenerateImageCutoutListSlideInput
    ),
    StructuredTool.from_function(
        func=generate_body_slide4,
        name="generate_body_slide4",
        description="Generates a dynamic and engaging Image Gallery Slide featuring a full-width gradient content bar positioned above a horizontal row of exactly three vertical cards. Each card contains an image with a distinct left-side color border and a centered subtitle for clear categorization. Ideal for portfolio showcases, team member introductions, or comparing three separate product categories.",
        args_schema=GenerateBodySlide4Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide5,
        name="generate_body_slide5",
        description="Generates an organized and comprehensive Visual Grid Slide featuring a symmetrical 2x2 image grid on the left and a 2x2 text grid on the right. This layout uses color-coded image overlays and vertical border-left accents to maintain a clear and systematic information hierarchy. Ideal for quarterly performance reviews, multi-departmental status updates, or complex four-point conceptual breakdowns.",
        args_schema=GenerateBodySlide5Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide10,
        name="generate_body_slide10",
        description="Generates a clean and authoritative Feature Slide featuring a large, left-aligned image frame with a double-layered accent border and three stacked icon-based content items on the right. Each content section includes an interactive hover-lift effect and custom SVG icons in rounded-gradient containers. Ideal for Product Features, Service Offerings, or Key Pillars where high-impact imagery balances detailed bullet points.",
        args_schema=GenerateBodySlide10Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide11,
        name="generate_body_slide11",
        description="Generates a bold and systematic Three-column Info Slide featuring exactly three vertical content boxes, each crowned by a floating circular SVG icon. This structure uses a top-heavy visual hierarchy with uppercase subtitles and centered body text within soft-gradient containers. Ideal for Core Values, Strategic Goals, or High-level Process Summaries where parity between three distinct concepts is required.",
        args_schema=GenerateBodySlide11Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide12,
        name="generate_body_slide12",
        description="Generates a professional and descriptive Image Gallery Slide featuring a full-width horizontal gradient content bar above a 1x3 row of vertical image cards. Each card is uniquely identified by an all-around accent border and a bottom-aligned text area for concise descriptions. Ideal for Market Segments, Team Introductions, or Product Comparisons where a horizontal overview leads into specific categorical details.",
        args_schema=GenerateBodySlide12Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide15,
        name="generate_body_slide15",
        description="""Generates a sleek and list-oriented Content Slide featuring a 2.5/2.5 horizontal split with two stacked bulleted list sections on the left and a large portrait image on the right. This layout utilizes colored "subtitle-containers" and custom dot bullets to categorize complex information clearly. Ideal for Executive Summaries, Key Findings, or Detailed Capabilities lists where structured text needs a strong visual anchor.""",
        args_schema=GenerateBodySlide15Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide18,
        name="generate_body_slide18",
        description="""Generates a balanced and corporate Comparison Slide featuring two symmetrical vertical columns separated by a central divider line. Each side integrates a large-scale SVG icon (defaulting to gavel and scales) above centered headings and descriptive body text. Ideal for Legal Frameworks, Pro-and-Con Analysis, or "This vs. That" scenarios requiring a high-contrast, professional comparison layout.""",
        args_schema=GenerateBodySlide18Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide19,
        name="generate_body_slide19",
        description="Generates a high-contrast and divided Informational Slide featuring a blue-background left column for primary text and a white-background right column for icon-supplemented sections. This layout uses absolute-flat positioning and distinct color blocking to separate two primary content streams. Ideal for Comparing Internal vs. External factors, Policy Summaries, or Two-part Strategic Overviews with functional icons.",
        args_schema=GenerateBodySlide19Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide20,
        name="generate_body_slide20",
        description="Generates a minimalist and elegant Comparison Slide featuring two vertical columns with icons housed in exactly two rounded-square translucent containers. The layout is anchored by a central thin vertical divider with 40% opacity and a large centered main title. Ideal for Executive Comparisons, Decision Matrix highlights, or Core Concept dualities where a clean, airy aesthetic is paramount.",
        args_schema=GenerateBodySlide20Input
    ),
    StructuredTool.from_function(
        func=generate_main_points_slide,
        name="generate_main_points_slide",
        description="""Generates a high-impact and industrial Main Points Slide featuring a balanced 3-column horizontal layout with specialized environmental CSS icons (bag, faucet, and factory) inside glowing teal glassmorphism orbs set against a dark navy canvas. Ideal for sustainability reports, ecological impact discussions, or green initiative pitches where thematic visual consistency is required.""",
        args_schema=GenerateMainPointsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_elegant_points_slide,
        name="generate_elegant_points_slide",
        description="""Generates an elegant and refined Key Points Slide featuring exactly 4 vertical columns of content cards optimized for high-resolution displays. This layout incorporates a unique visual DNA of central gold-accented icon-dividers and elevated soft-shadow cards with sophisticated serif headings. Ideal for luxury branding presentations, high-end strategic summaries, or core philosophy overviews where premium aesthetics are essential.""",
        args_schema=GenerateElegantPointsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_corporate_content_slide,
        name="generate_corporate_content_slide",
        description="""Generates a professional and bright Content Slide featuring an asymmetrical split layout with an angled title panel and a vertical right-hand list column. It utilizes a sharp geometric clip-path angled panel and large-scale ghosted numbering on content cards for a modern corporate look. Ideal for onboarding guides, business strategy pitches, or structured service descriptions requiring a clean and authoritative hierarchy.""",
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
        description="""Generates a clean and minimalist Multi-column Slide featuring a flexible 2 or 3 column horizontal layout paired with a decorative right-aligned color panel. This design is defined by an angled right-side clip-path divider and content modules anchored by vibrant top-edge gradient accent bars. Ideal for comparative feature lists, project pillar descriptions, or high-level category breakdowns in a corporate setting.""",
        args_schema=GenerateCorporateMulticolumnSlideInput
    ),
    StructuredTool.from_function(
        func=generate_corporate_grid_slide,
        name="generate_corporate_grid_slide",
        description="Generates a systematic and organized Concept Review Grid featuring a 3x2 matrix of six content cards paired with a right-aligned geometric accent panel. This tool uses a unique double-layered angled clip-path background element and oversized bold typography to emphasize key terminology. Ideal for recap sessions, concept glossaries, or multi-point tactical checklists where high information density must remain legible.",
        args_schema=GenerateCorporateGridSlideInput
    ),
    # StructuredTool.from_function(
    #     func=generate_business_overview_slide,
    #     name="generate_business_overview_slide",
    #     description="Generates a professional business overview slide with icon-content sections layout.",
    #     args_schema=GenerateBusinessOverviewSlideInput
    # ),
    StructuredTool.from_function(
        func=generate_vision_mission_slide,
        name="generate_vision_mission_slide",
        description="Generates a professional and balanced Vision & Mission Slide featuring a 50/50 symmetrical vertical split layout. This slide incorporates large oversized ghosted background numbers and an intricate geometric background pattern layered with exactly two decorative triangles. Ideal for corporate strategy overviews, organizational goal setting, or establishing institutional core values where a dual-focus information hierarchy is required.",
        args_schema=GenerateVisionMissionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_service_roadmap_slide,
        name="generate_service_roadmap_slide",
        description="Generates a modern and structured Service Roadmap Slide featuring a balanced 2x2 grid of exactly four floating content cards. This design utilizes a unique four-corner decorative triangle frame and cards anchored by top-edge linear gradient accent bars against a bold gradient background. Ideal for project implementation phases, service evolution roadmaps, or multi-stage strategic planning where sequential progress must be clearly visualized.",
        args_schema=GenerateServiceRoadmapSlideInput
    ),
    StructuredTool.from_function(
        func=generate_minimalist_tech_list_slide,
        name="generate_minimalist_tech_list_slide",
        description="Generates a clean and minimalist Tech List Slide featuring a left-aligned vertical bulleted list paired with a distinct italicized concluding text block. This design is characterized by a background radial dot grid overlay and a full-height solid vertical accent bar that anchors the left margin. Ideal for technical product specifications, engineering feature summaries, or concise software development checklists where readability is the primary intent.",
        args_schema=GenerateMinimalistTechListSlideInput
    ),

    StructuredTool.from_function(
        func=generate_split_layout_list_slide,
        name="generate_split_layout_list_slide",
        description="Generates a minimalist and sophisticated Split-Layout List Slide featuring a 35/65 asymmetrical horizontal split between a solid-colored left title panel and a right content pane. The right-side column utilizes horizontal hairline dividers to separate expanded key points with uppercase bold headings and detailed descriptions. Ideal for strategic priority lists, core concept elaborations, or topical deep-dives where a stark visual separation between the main topic and supporting details is paramount.",
        args_schema=GenerateSplitLayoutListSlideInput
    ),
    StructuredTool.from_function(
        func=generate_reference_slide,
        name="generate_reference_slide",
        description="Generates a professional and corporate Reference Slide featuring a 60/40 horizontal split between a left-aligned text panel and a full-bleed right-aligned image column. This design is anchored by a high-contrast horizontal title-divider and oversized bold headings for maximum impact. Ideal for detailing research citations, bibliographies, or key supporting evidence where a strong visual anchor is required.",
        args_schema=GenerateReferenceSlideInput
    ),
    StructuredTool.from_function(
        func=generate_icon_list_slide,
        name="generate_icon_list_slide",
        description="Generates a minimalist and modern Icon List Slide featuring a grid-based layout with a distinct title column on the left and a vertical list of points on the right. It utilizes large spherical accent-colored icon containers and a 1:1.2 structural ratio to emphasize categorical content. Ideal for highlighting top three strategic priorities, core benefits, or multifaceted concept breakdowns.",
        args_schema=GenerateIconListSlideInput
    ),
    StructuredTool.from_function(
        func=generate_flexible_columns_slide,
        name="generate_flexible_columns_slide",
        description="""Generates a creative and airy Multi-column Slide featuring a flexible 2-to-3 column horizontal layout positioned in the upper half of the screen. This slide utilizes a unique visual DNA of cursive "Patrick Hand" typography set against a subtle lined-paper texture background with significant bottom-page negative space. Ideal for informal brainstorming summaries, creative comparative lists, or content requiring a sketchbook aesthetic.""",
        args_schema=GenerateFlexibleColumnsSlideInput
    ),
    StructuredTool.from_function(
        func=generate_text_with_image_slide,
        name="generate_text_with_image_slide",
        description="""Generates a creative and airy Text with Image Slide featuring a 35/65 asymmetrical horizontal split between a left-aligned text panel and a right-aligned image column. This design utilizes a unique visual DNA of cursive "Patrick Hand" typography set against a subtle lined-paper texture background with significant bottom-page negative space. Ideal for informal brainstorming summaries, creative comparative lists, or content requiring a sketchbook aesthetic.Generates an artistic and layered Text-Image Slide featuring a 1.5:1 ratio horizontal split with descriptive content on the left and a full-height portrait image on the right. It is defined by a unique dual-texture background where the text column sits on a "paper pattern" overlay while the image column remains clean. Ideal for visual storytelling, editorial-style project overviews, or human-centric business commentary.""",
        args_schema=GenerateTextWithImageSlideInput
    ),
    StructuredTool.from_function(
        func=generate_geometric_split_content_slide,
        name="generate_geometric_split_content_slide",
        description="""Generates a bold and high-tech Split Content Slide featuring a symmetric horizontal layout housed within a designated central "safe zone" to prevent overlap. This tool utilizes a unique visual DNA of multi-layered translucent geometric rectangle clusters in opposing corners and a deep navy canvas. Ideal for high-tech product comparisons, futuristic business briefings, or strategic two-point analytical summaries.""",
        args_schema=GenerateGeometricSplitContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_geometric_split_content_slide_2,
        name="generate_geometric_split_content_slide_2",
        description="Generates a vibrant and structured Multi-column Slide featuring a wide content wrapper optimized for exactly three horizontal columns. The design incorporates distinct clusters of floating colorful geometric polygons and horizontal separation to ensure maximum legibility against a dark backdrop. Ideal for triple-threat comparative analysis, outlining multifaceted strategic pillars, or complex categorization in a high-tech environment.",
        args_schema=GenerateGeometricSplitContentSlide2Input
    ),
    StructuredTool.from_function(
        func=generate_geometric_image_content_slide,
        name="generate_geometric_image_content_slide",
        description="""Generates a modern and avant-garde Image Content Slide featuring a horizontal split between a custom-shaped image on the left and a focused text panel on the right. It utilizes a unique geometric clip-path polygon for the image frame and compact corner-aligned shape clusters to maintain thematic consistency. Ideal for high-impact visionary quotes, defining a core brand concept, or showcasing hero imagery with a technological edge.""",
        args_schema=GenerateGeometricImageContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_geometric_grid_slide,
        name="generate_geometric_grid_slide",
        description="""Generates a clean and focused Geometric Grid Slide featuring a 2x3 matrix of six content items housed within a central safe zone. This layout utilizes a unique visual DNA of faded shape clusters in the corners with low-opacity transparent geometric overlays to maintain a modern, high-tech aesthetic without distracting from the text. Ideal for concept reviews, multi-point definitions, or categorized summaries where clarity and information density are paramount.""",
        args_schema=GenerateGeometricGridSlideInput
    ),
    StructuredTool.from_function(
        func=generate_memphis_content_slide,
        name="generate_memphis_content_slide",
        description="""Generates a vibrant and eclectic Memphis-style Content Slide featuring a dramatic 20/80 vertical layout split. This design utilizes precisely positioned geometric shape clusters—including dashed squares, floating triangles, and circles—set against a dual-toned deep purple background. Ideal for high-impact concluding statements or key takeaway summaries where a bold, retro-modern visual statement is required.""",
        args_schema=GenerateMemphisContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_memphis_multicolumn_slide,
        name="generate_memphis_multicolumn_slide",
        description="""Generates a bold and structured Memphis-style Multi-column Slide featuring exactly three horizontal content columns positioned within a tiered 20/80 layout. It incorporates unique SVG pattern fills, such as dots and stripes, alongside specialized "pentagon" clip-path geometric elements in the panel corners. Ideal for comparative feature lists or triple strategic pillar overviews that require a sophisticated artistic edge.""",
        args_schema=GenerateMemphisMulticolumnSlideInput
    ),
    StructuredTool.from_function(
        func=generate_memphis_grid_slide,
        name="generate_memphis_grid_slide",
        description="Generates an energetic and organized Memphis-style Grid Slide featuring a symmetrical 2x3 matrix of exactly six content items. This layout utilizes a unique visual DNA of pattern-filled circular overlays, dashed-line shapes, and a dark tiered background split to anchor dense information. Ideal for concept reviews or multifaceted project summaries where high information density must be paired with high-energy design.",
        args_schema=GenerateMemphisGridSlideInput
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
        description="Generates a strategic and sleek Planning Phase Slide featuring a linear horizontal timeline connecting exactly four large circular pin markers. This structure utilizes a unique visual DNA of high-contrast spherical markers containing custom line-art SVGs—brain, checklist, design, and puzzle—aligned atop a dotted progress track. Ideal for project lifecycles, implementation phases, or sequential strategic planning milestones where a clear roadmap is essential.",
        args_schema=GeneratePlanningPhaseSlideInput
    ),
    StructuredTool.from_function(
        func=generate_timeline_slide,
        name="generate_timeline_slide",
        description="""Generates a professional and chronological Timeline Slide featuring a horizontal progress axis with multiple milestone nodes. This layout utilizes a vibrant accent-colored line with glowing circular nodes and a large translucent background circular watermark for added depth. Ideal for visualizing company history, project roadmaps, or product evolution over specific yearly intervals.""",
        args_schema=GenerateTimelineSlideInput
    ),
    StructuredTool.from_function(
    func=generate_quote_slide,
    name="generate_quote_slide",
    description="""Generates an elegant and minimalist Quote Slide featuring a centered large-format italicized quote with a matching author attribution and role. It incorporates a unique large-scale translucent decorative quotation mark backdrop and a thin outer border frame for a sophisticated, high-end look. Ideal for showcasing executive visions, customer testimonials, or inspirational industry insights.""",
    args_schema=GenerateQuoteSlideInput
    ),
    StructuredTool.from_function(
    func=generate_classic_content_slide,
    name="generate_classic_content_slide",
    description="""Generates a classic and informative Content Slide featuring a 50/50 horizontal split layout with a text-heavy left column and a large rounded-corner image on the right. This slide is defined by a distinctive vertical theme-color accent bar above the title and color-coded circular bullet points for clear readability. Ideal for detailed business explanations, market opportunity analysis, or capability overviews.""",
    args_schema=GenerateClassicContentSlideInput
    ),

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
    ),
    StructuredTool.from_function(
        func=generate_modern_contact_slide,
        name="generate_modern_contact_slide",
        description="Generates a modern 'Thank You' or Contact slide featuring a large blue geometric overlay, integrated images, and clear contact details.",
        args_schema=GenerateModernContactSlideInput
    ),
    StructuredTool.from_function(
        func=generate_closing_slide,
        name="generate_closing_slide",
        description="Generates a modern, minimalist closing or 'Thank You' slide with asymmetric layout, circular image mask, and geometric decorative elements.",
        args_schema=GenerateClosingSlideInput
    ),
    StructuredTool.from_function(
        func=generate_minimalist_thank_you_slide,
        name="generate_minimalist_thank_you_slide",
        description="Generates a modern, clean 'Thank You' slide with large centered typography, vertical side text, and geometric decorative blocks.",
        args_schema=GenerateMinimalistThankYouSlideInput
    ),
    StructuredTool.from_function(
        func=generate_minimalist_sage_slide,
        name="generate_minimalist_sage_slide",
        description="Generates a minimalist, elegant slide with a soft sage green and peach theme, featuring organic curved shapes and glow effects. Best used for 'Thank You', Title, or clean transitional slides.",
        args_schema=GenerateMinimalistSageSlideInput
    ),
    StructuredTool.from_function(
        func=generate_thank_you_so_much_slide,
        name="generate_thank_you_so_much_slide",
        description="Generates a minimalist 'Thank You' / End slide with contact details, following a clean Blue/Beige aesthetic.",
        args_schema=GenerateThankYouSoMuchSlideInput
    ),
    StructuredTool.from_function(
        func=generate_brand_collaboration_closing_slide,
        name="generate_brand_collaboration_closing_slide",
        description="Generates a sophisticated closing/thank you slide with an asymmetrical image layout, elegant serif and script typography, and a paper-textured background.",
        args_schema=GenerateBrandCollaborationClosingSlideInput
    ),
    StructuredTool.from_function(
        func=generate_military_thank_you_slide,
        name="generate_military_thank_you_slide",
        description="Generates a professional military-themed presentation slide with a diagonal split layout, ideal for 'Thank You' or section break slides.",
        args_schema=GenerateMilitaryThankYouSlideInput
    ),
    StructuredTool.from_function(
        func=generate_corporate2_thank_you_slide,
        name="generate_corporate2_thank_you_slide",
        description="Generates a professional corporate 'Thank You' slide with navy blue and white color scheme. Features a clean layout with company logo placeholder, contact email, and website information. Uses elegant Playfair Display typography with decorative accent elements. Perfect for business presentations, corporate meetings, and professional closing slides requiring a sophisticated, trustworthy aesthetic.",
        args_schema=GenerateCorporate2ThankYouInput
    ),
    StructuredTool.from_function(
        func=generate_creative_thank_you_slide,
        name="generate_creative_thank_you_slide",
        description="Generates a creative and artistic 'Thank You' slide featuring a large background or decorative image, artistic typography, and vibrant accent colors. The design combines visual impact with elegant Playfair Display fonts and customizable gradient backgrounds. Perfect for creative presentations, design portfolios, marketing pitches, or any presentation wanting to make a bold, memorable closing statement with strong visual appeal.",
        args_schema=GenerateCreativeThankYouInput
    ),
    StructuredTool.from_function(
        func=generate_tech_thank_you_slide,
        name="generate_tech_thank_you_slide",
        description="Generates a modern tech-style 'Thank You' slide with neon glow effects, dark background, and social media icons. Features futuristic design elements with glowing text effects, high-tech aesthetic, and modern typography. Includes customizable social media icon links. Perfect for technology presentations, startup pitches, product launches, or any presentation targeting a tech-savvy audience wanting a cutting-edge, digital-forward closing slide.",
        args_schema=GenerateTechThankYouInput
    ),
    StructuredTool.from_function(
        func=generate_minimalist_thank_you_slide_2,
        name="generate_minimalist_thank_you_slide_2",
        description="Generates a clean, minimalist 'Thank You' slide with modern design featuring large, bold typography without excessive decorations. Emphasizes whitespace and simplicity with a focused message and contemporary fonts. The ultra-minimal approach creates maximum impact through restraint and clarity. Perfect for modern business presentations, professional meetings, or any presentation wanting a sleek, sophisticated closing that lets the message speak for itself.",
        args_schema=GenerateMinimalistThankYouInput2
    ),
    StructuredTool.from_function(
        func=generate_elegant_thank_you_slide,
        name="generate_elegant_thank_you_slide",
        description="Generates an elegant and sophisticated 'Thank You' slide featuring a beautiful background image, handwritten-style script typography, and generous whitespace. The design combines refined aesthetics with flowing calligraphy fonts and breathable layout spacing. Creates a luxurious, high-end feel with artistic typography. Perfect for wedding presentations, luxury brand pitches, upscale events, formal ceremonies, or any presentation requiring a refined, graceful closing with timeless elegance.",
        args_schema=GenerateElegantThankYouInput
    )
]
CHART_TOOLS = [
    StructuredTool.from_function(
        func=generate_line_chart_slide_2,
        name="generate_line_chart_slide_2",
        description=(
            "Generates a modern, data-driven Line Chart slide with a refined Global Economy aesthetic.\n"
            "The visual style emphasizes structured analytical storytelling, combining clean typography, "

            "The slide layout is divided into three main sections:\n"
            "- Upper section: reserved for main title and subtitle positioned on the right side.\n"
            "- Left section: reserved for the line chart display with decorative circular shape and dot grid pattern.\n"
            "- Right section: reserved for chart description, including textual content such as insights and interpretation.\n\n"
            "The layout is designed to present visual data trends alongside supporting explanatory text in a modern Global Economy style."
        ),
        args_schema=GenerateLineChartSlide2
    ),

    StructuredTool.from_function(
        func=generate_line_chart_slide_3,
        name="generate_line_chart_slide_3",
        description=(
            "Generates a Line Chart slide for presenting multi-series performance data over time.\n"
            "The slide layout is divided into three main sections:\n"
            "- Upper section: title and subtitle.\n"
            "- Left section (Large): SVG line chart with axes and grid.\n"
            "- Right section (Sidebar): insight text box and legend.\n"
        ),
        args_schema=GenerateLineChartSlide3
    ),
    StructuredTool.from_function(
        func=generate_radar_chart_slide_1,
        name="generate_radar_chart_slide_1",
        description=(
            "The slide layout consists of a full-width header at the top and a two-column content section below.\n"
            "- The header displays a large bold main title with a smaller subtitle underneath.\n"
            "- The lower section is split into two columns:\n"
            "  • Left column: contains a highlighted insight card with soft gradients and borders, followed by a rounded legend box listing series labels with colored swatches.\n"
            "  • Right column: displays a large centered radar chart rendered in SVG.\n"
            "- The overall layout emphasizes clear hierarchy: title → insight → legend → chart, with balanced spacing and a professional healthcare-themed aesthetic."
        ),
        args_schema=GenerateRadarChartSlide1
    ),
    StructuredTool.from_function(
        func=generate_pie_chart_slide_1,
        name="generate_pie_chart_slide_1",
        description=(
            "The slide layout is divided into three main sections:\n"
            "- Upper section: Displays a large, bold main title in Teal and a white subtitle.\n"
            "- Left section: Contains a highlighted insight box with an accent border and a legend.\n"
            "- Right section: Features a high-contrast SVG pie or donut chart.\n"
        ),
        args_schema=GeneratePieChartSlide1
    ),
    StructuredTool.from_function(
        func=generate_scatter_plot_chart_slide_2,
        name="generate_scatter_plot_chart_slide_2",
        description=(
            "Generates a travel-themed Scatter Plot slide with a polished, presentation-ready design.\n"
            "The slide layout is divided into three main sections:\n"
            "- Upper section: Reserved for the main title and subtitle, featuring a strong accent border.\n"
            "- Left section: Reserved for the analytical insight box and data legend, styled with a travel-themed shadow effect.\n"
            "- Right section: Reserved for a large SVG scatter plot chart inside a soft-background container.\n"
            "The layout is designed to highlight correlations between variables with a clean, hand-crafted aesthetic."
        ),
        args_schema=GenerateScatterPlotChartSlide2
    ),
    StructuredTool.from_function(
        func=generate_bar_chart_slide_2,
        name="generate_bar_chart_slide_2",
        description=(
            "Generates a clean and modern Bar Chart slide with a refined, presentation-ready aesthetic.\n"
            "Visual style emphasizes clarity and balance, using soft accent colors and readable typography.\n"
            
            "Layout:\n"
            "- Upper section: Prominent main title with optional subtitle for context or units.\n"
            "- Left section: Insight section highlighting key observations, accompanied by a clear legend.\n"
            "- Right section: Structured SVG Grouped Bar Chart displayed inside a neat container.\n"
            "Best suited for comparing multiple data series across shared categories in reports or business reviews."
        ),
        args_schema=GenerateBarChartSlide2
    ),
]

# All available slide generation tools with complete parameter schemas
ALL_TOOLS = INTRO_TOOLS + TRANSITION_TOOLS + CONTENT_TOOLS + TEAM_TOOLS + THANK_YOU_TOOLS + CHART_TOOLS

TOOLS_DICT = {'INTRO_TOOLS': INTRO_TOOLS,
               'TRANSITION_TOOLS': TRANSITION_TOOLS,
               'CONTENT_TOOLS': CONTENT_TOOLS,
               'TEAM_TOOLS': TEAM_TOOLS,
               'THANK_YOU_TOOLS': THANK_YOU_TOOLS,
                'CHART_TOOLS': CHART_TOOLS
               }

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