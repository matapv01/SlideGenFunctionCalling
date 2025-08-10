# Auto-generated from tools.py preserving all original parameter schemas
# This conversion maintains the exact parameter definitions from the source

from typing import List, Dict, Any, Optional
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

  
    
    generate_geometric_transition_slide, # slide chuyển slide 
    generate_transition_slide_2, # slide chuyển slide
    generate_dusk_transition_slide, # slide chuyển slide
    generate_memphis_transition_slide, # slide chuyển slide
    generate_pushpin_section_header,    # slide chuyển slide
    generate_section_header_slide,  # slide chuyển slide
    generate_corporate_transition_slide,    # slide chuyển slide
    generate_intro_slide, # slide chuyển slide
    generate_credits_slide,     # slide chuyen slide

    generate_content_slide, # slide content
    generate_two_column_slide,  # slide content
    generate_project_circles_slide, # slide content
    generate_comparison_slide,  # slide content
    generate_process_slide,  # slide content
    generate_process_steps_slide, # slide content
    generate_icon_list_slide_2, # slide content
    generate_image_cutout_list_slide, # slide content
    generate_body_slide2,  # slide content
    generate_body_slide3,  # slide content
    generate_body_slide4,  # slide content
    generate_body_slide5,  # slide content
    generate_body_slide6,  # slide content
    generate_body_slide7,  # slide content
    generate_body_slide10,  # slide content
    generate_body_slide11,  # slide content
    generate_body_slide12,  # slide content
    generate_body_slide13,  # slide content
    generate_body_slide14,  # slide content
    generate_body_slide15,  # slide content
    generate_body_slide16,  # slide content
    generate_body_slide17,  # slide content
    generate_body_slide18,  # slide content
    generate_body_slide19,  # slide content
    generate_body_slide20,  # slide content
    generate_strategy_slide,  # slide content    
    generate_main_points_slide, # slide content
    generate_elegant_points_slide,  # slide content
    generate_horizontal_timeline_slide, # slide content
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


    generate_team_slide, # slide giới thiệu team 
    generate_colorful_team_grid_slide,  # slide giới thiệu team
    generate_corporate_team_slide, # slide giới thiệu team
    
    

    
    
    generate_thank_you_slide_2, # slide cảm ơn
    generate_thank_you_slide_3, # slide cảm ơn
    generate_thank_you_slide,   # slide cảm ơn
    generate_corporate_thank_you_slide, # slide cảm ơn


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
    font_family: str = Field(default="Arial, sans-serif", description="Font family for all text elements.")
    show_skyline: Optional[bool] = Field(default=True, description="Whether to show the city skyline silhouette at the bottom. Default: True.")
    skyline_opacity: Optional[float] = Field(default=0, description="Opacity of the skyline silhouette (0.0 to 1.0). Default: 0.3.")
    triangle_opacity: Optional[float] = Field(default=0, description="Opacity of the triangle decorative elements (0.0 to 1.0). Default: 0.2.")
    title_font_size: str = Field(default="5rem", description="Font size for the main title.")
    subtitle_font_size: str = Field(default="2rem", description="Font size for the subtitle.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")


class GenerateIntroductionSlideInput(BaseModel):
    """Input schema for generate_introduction_slide."""
    main_title: str = Field(..., description="Main title text (8-20 characters). Default: 'INTRODUCTION'.")
    content_text: str = Field(..., description="Main content paragraph.. Default: Lorem ipsum text.")
    bg_color: str = Field(default="#1a4b8c", description="Primary background color (hex code).")
    bg_gradient_to: str = Field(default="#2a6cb7", description="Secondary background color for gradient effect (hex code).")
    text_color: str = Field(default="#FFFFFF", description="Color of all text elements (hex code).")
    title_font_size: str = Field(default="4rem", description="Font size for the main title.")
    content_font_size: str = Field(default="1.4rem", description="Font size for the content text.")
    font_family: str = Field(default="Arial, sans-serif", description="Font family for all text elements.")
    show_decorative_triangles: Optional[bool] = Field(default=True, description="Whether to show decorative triangle elements. Default: True.")
    triangle_opacity: Optional[float] = Field(default=0, description="Opacity of the decorative triangles (0.0 to 1.0). Default: 0.15.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
    border_opacity: Optional[float] = Field(default=0, description="Opacity of the border frame (0.0 to 1.0). Default: 0.4.")
    content_max_width: str = Field(default="800px", description="Maximum width of the content area.")
    line_height: str = Field(default="1.6", description="Line height for the content text.")
    letter_spacing: str = Field(default="0.1em", description="Letter spacing for the title.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

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
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
    main_title_font_size: str = Field(default="36px", description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default="16px", description="CSS font size for the subtitles.")
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
    font_family: str = Field(default="'Playfair Display', serif", description="Font family for all text elements. A serif font like 'Playfair Display' is recommended.")
    background_image_url: str = Field(default="https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=2069&auto=format&fit=crop", description="URL for the full-screen background image. A bright, clean image is recommended for this theme.")
    text_color: str = Field(default="#3A3A3A", description="Text color for the quote and attribution. A dark color is recommended for light backgrounds.")
    decoration_color: str = Field(default="rgba(0, 0, 0, 0.08)", description="Color of the large, decorative quotation marks. A subtle, semi-transparent color is recommended.")

class GenerateTitleSlide2Input(BaseModel):
    """Input schema for generate_title_slide_2."""
    main_title: str = Field(..., description="The entire title for the slide. Use <br> for line breaks and <span class='highlight'>word</span> to highlight a specific word. Default: 'THIS IS YOUR<br><span class=\'highlight\'>PRESENTATION</span><br>TITLE'.")
    font_family: str = Field(default="'Montserrat', sans-serif", description="The font family for all text elements.")
    accent_color: str = Field(default="#06B6D4", description="The primary accent color for the right panel and the highlighted word.")
    shadow_color: str = Field(default="#0E7490", description="The secondary (darker) accent color for the panel behind.")
    text_color: str = Field(default="#6B7280", description="The primary color for the non-highlighted text.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small icon above the title.")

class GenerateDynamicIntroSlideInput(BaseModel):
    """Input schema for generate_dynamic_intro_slide."""
    main_title: str = Field(..., description="The large, bold title for the slide. Default: 'Innovate. Create. Inspire.'.")
    subtitle: str = Field(..., description="The smaller subtitle text below the main title. Default: 'This is where we outline our core mission and the driving force behind our vision.'.")
    image_url: str = Field(default="https://images.unsplash.com/photo-1521737711867-e3b97375f902?q=80&w=1887&auto=format&fit=crop", description="URL for the full-height image on the right.")
    font_family: str = Field(default="'Poppins', sans-serif", description="Font family for all text elements.")
    primary_color: str = Field(default="#4F46E5", description="The primary (brighter) color for the main part of the text block.")
    secondary_color: str = Field(default="#3730A3", description="The secondary (darker) color for the footer area of the text block.")
    text_color: str = Field(default="#FFFFFF", description="The color for the text.")

class GenerateBigConceptSlideInput(BaseModel):
    """Input schema for generate_big_concept_slide."""
    main_title: str = Field(..., description="The main, large title for the concept. Use <br> for line breaks. Default: 'BIG<br>CONCEPT'.")
    subtitle: str = Field(..., description="A smaller descriptive text below the main title. Default: 'Bring the attention of your audience over a key concept using icons or illustrations'.")
    icon_name: str = Field(..., description="Selects a pre-designed illustration scene to display. Default: 'space'.")
    font_family: str = Field(default="'Poppins', sans-serif", description="The font family for all text elements.")
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
    font_family_title: str = Field(default="'Patrick Hand', cursive", description="The handwritten-style font for the main title.")
    font_family_body: str = Field(default="'Lato', sans-serif", description="The clean sans-serif font for the subtitle.")
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
    font_family: str = Field(default="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", description="Font family for all text elements.")
    background_color_left: str = Field(default="#F5EBE0", description="Background color for the top content area in the left column (warm beige).")
    text_color_title: str = Field(default="#4E443F", description="Text color for the main title (dark brown).")
    text_color_top: str = Field(default="#4E443F", description="Text color for the top subheading (dark brown).")
    text_color_subtitle: str = Field(default="#475569", description="Text color for the main description/subtitle (neutral gray).")
    slide_background_color: str = Field(default="#FDFCFB", description="Overall background color for the entire slide (off-white/cream).")

# === SLIDE CHUYỂN SLIDE CLASSES ===

class GenerateGeometricTransitionSlideInput(BaseModel):
    """Input schema for generate_geometric_transition_slide."""
    section_number: str = Field(default="1.", description="The number for the new section (e.g., '1.', '02', 'B.').")
    headline: str = Field(..., description="The main, uppercase headline for the transition. Default: 'TRANSITION HEADLINE'.")
    subtitle: str = Field(..., description="The smaller subtitle text displayed below the headline. Default: 'Let's start with the first set of slides'.")
    font_family: str = Field(default="'Poppins', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    primary_text_color: str = Field(default="#FFFFFF", description="The color for the section number and the main headline.")
    subtitle_color: str = Field(default="#67E8F9", description="The accent color for the subtitle text.")

class GenerateTransitionSlide2Input(BaseModel):
    """Input schema for generate_transition_slide_2."""
    section_number: str = Field(default=None, description="The number or letter for the section (e.g., '1.', '2.', 'A.').")
    main_headline: str = Field(..., description="The large, uppercase headline for the transition. Default: 'HEADLINE'.")
    subtitle: str = Field(..., description="The smaller text below the headline. Default: 'Content'.")
    font_family_heading: str = Field(default="'Patrick Hand', cursive", description="The handwritten-style font for the headline and section number.")
    font_family_body: str = Field(default="'Lato', sans-serif", description="The standard font for the subtitle.")
    number_color: str = Field(default="#F37A59", description="The accent color for the section number.")
    text_color: str = Field(default="#2C3E50", description="The color for the headline and subtitle text.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the background texture. Defaults to a paper texture.")

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
    font_family_headline: str = Field(default="'Lora', serif", description="The elegant, serif font for the main headline and number.")
    font_family_body: str = Field(default="'Lato', sans-serif", description="The clean, sans-serif font for the subtitle.")
    top_panel_bg: str = Field(default="#19114B", description="The background color for the top half of the slide.")
    bottom_panel_bg: str = Field(default="#403271", description="The background color for the bottom half of the slide.")
    palette: List[str] = Field(default=["#F87171", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"], description="A list of 5 colors used for the various decorative shapes and accents. [0: Red/Magenta, 1: Orange/Yellow, 2: Purple, 3: Blue, 4: Green/Teal]")

class GeneratePushpinSectionHeaderInput(BaseModel):
    """Input schema for generate_pushpin_section_header."""
    main_title: str = Field(..., description="The main text for the section header. It will be displayed in large, uppercase letters. Default: 'Add a Section Header'.")
    font_family: str = Field(default="'Poppins', sans-serif", description="The font family for the title.")
    bg_color: str = Field(default="#FDFCFB", description="The background color of the slide, with a subtle paper texture overlay.")
    text_color: str = Field(default="#1F2937", description="The color for the main title text.")
    accent_color: str = Field(default="#1F2937", description="The color for the horizontal divider line and the two flanking dots.")

class GenerateSectionHeaderSlideInput(BaseModel):
    """Input schema for generate_section_header_slide."""
    header_text: str = Field(..., description="The main, large text for the section header. Default: 'Add a Section Header'.")
    font_family: str = Field(default="'Poppins', sans-serif", description="Font family for the header text.")
    bg_color: str = Field(default="#F8FAFC", description="The main background color of the slide (typically a very light off-white).")
    text_color: str = Field(default="#1E293B", description="The color for the header text.")
    gradient_color_1: str = Field(default="#A78BFA", description="The first color for the soft aurora gradient background (e.g., light purple).")
    gradient_color_2: str = Field(default="#F472B6", description="The second color for the soft aurora gradient background (e.g., pink).")
    gradient_color_3: str = Field(default="#7DD3FC", description="The third color for the soft aurora gradient background (e.g., light blue).")

class GenerateCorporateTransitionSlideInput(BaseModel):
    """Input schema for generate_corporate_transition_slide."""
    headline: str = Field(default="TRANSITION<br>HEADLINE", description="The main headline text. Use <br> for a new line to control line breaks.")
    subtitle: str = Field(default="Let's start with the first set of slides", description="The smaller subtitle text displayed below the main headline.")
    font_family: str = Field(default="'Montserrat', sans-serif", description="The font family for all text elements.")
    primary_color: str = Field(default="#FBBF24", description="The primary color for the angled panel.")
    shadow_color: str = Field(default="#EAB308", description="The shadow color for the panel behind.")
    headline_color: str = Field(default="#6B7280", description="The color for the main headline text.")
    subtitle_color: str = Field(default="#FFFFFF", description="The color for the subtitle text.")

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
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
    main_title_font_size: str = Field(default="36px", description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default="16px", description="CSS font size for the subtitles.")
    main_title_font_style: str = Field(default="italic", description="CSS font style for the main title.")

class GenerateCreditsSlideInput(BaseModel):
    """Input schema for generate_credits_slide."""
    main_text: str = Field(..., description="Main message text displayed in script font. .")
    credits_text: str = Field(..., description="Credits and acknowledgments text. .")
    font_family: str = Field(default=None, description="Font family for regular text")

# === SLIDE CONTENT CLASSES ===

class GenerateContentSlideInput(BaseModel):
    """Input schema for generate_content_slide."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'CONTENT'.")
    items: List[str] = Field(..., description="List of item titles for the grid. Default: ['Your Title Here', ...] (6 items).")
    main_title_font_size: str = Field(default="60px", description="CSS font size for the main title.")
    number_font_size: str = Field(default="70px", description="CSS font size for item numbers.")
    item_title_font_size: str = Field(default="28px", description="CSS font size for item titles.")
    main_title_color: str = Field(default="#555555", description="CSS color for the main title.")
    number_color: str = Field(default="#a2c4c9", description="CSS color for item numbers.")
    item_title_color: str = Field(default="#555555", description="CSS color for item titles.")
    background_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#a2c4c9", description="CSS color for corner accents.")
    border_width: str = Field(default="30px", description="CSS width of the slide border.")
    font_family: str = Field(default="Arial, sans-serif", description="CSS font family for the slide.")
    num_columns: int  = Field(default=3, description="Number of columns in the grid. Default: 3.")
    num_rows: int  = Field(default=2, description="Number of rows in the grid. Default: 2.")

class GenerateTwoColumnSlideInput(BaseModel):
    """Input schema for generate_two_column_slide."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'Your Title Here'.")
    left_column_titles: List[str] = Field(..., description="List of titles for the left column. Default: ['Your Title Here', 'Your Title Here'].")
    left_column_texts: List[str] = Field(..., description="List of texts for the left column. Default: two placeholder texts.")
    right_column_titles: List[str] = Field(..., description="List of titles for the right column. Default: ['Your Title Here', 'Your Title Here'].")
    right_column_texts: List[str] = Field(..., description="List of texts for the right column. Default: two placeholder texts.")
    main_title_font_size: str = Field(default="36px", description="CSS font size for the main title.")
    column_title_font_size: str = Field(default="24px", description="CSS font size for column titles.")
    column_text_font_size: str = Field(default="16px", description="CSS font size for column texts.")
    main_title_color: str = Field(default="#555555", description="CSS color for the main title.")
    left_bg_color: str = Field(default="#a2c4c9", description="CSS background color for the left column.")
    left_text_color: str = Field(default="#ffffff", description="CSS text color for the left column.")
    right_title_color: str = Field(default="#555555", description="CSS color for right column titles.")
    right_text_color: str = Field(default="#555555", description="CSS color for right column texts.")
    border_color: str = Field(default="#a2c4c9", description="CSS color for the slide border.")
    icon_color: str = Field(default="#a2c4c9", description="CSS color for right column icons.")
    font_family: str = Field(default="Arial, sans-serif", description="CSS font family for the slide.")

class GenerateProjectCirclesSlideInput(BaseModel):
    """Input schema for generate_project_circles_slide."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'Your Title Here'.")
    left_title: str = Field(default="Your Title Here", description="Title for the left column.")
    right_title: str = Field(default="Your Title Here", description="Title for the right column.")
    left_text: str = Field(default="placeholder text", description="Text content for the left column. Default: placeholder text.")
    right_text: str = Field(default="placeholder text", description="Text content for the right column. Default: placeholder text.")
    footer_text: str = Field(default="placeholder text", description="Text content for the footer. Default: placeholder text.")
    project_names: List[str] = Field(..., description="List of three project names for the circles. Default: ['Project 1', 'Project 2', 'Project 3'].")
    circle_colors: List[str] = Field(default=['#e1eff2', '#8cbeca', '#e1eff2'], description="List of three CSS colors for the circles. Default: ['#e1eff2', '#8cbeca', '#e1eff2'].")
    main_title_font_size: str = Field(default="36px", description="CSS font size for the main title.")
    section_title_font_size: str = Field(default="24px", description="CSS font size for section titles.")
    text_font_size: str = Field(default="16px", description="CSS font size for main text.")
    footer_font_size: str = Field(default="14px", description="CSS font size for footer text.")
    title_color: str = Field(default="#555555", description="CSS color for all titles.")
    text_color: str = Field(default="#555555", description="CSS color for all text content.")
    circle_text_color: str = Field(default="#ffffff", description="CSS color for text in the circles.")
    background_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#a2c4c9", description="CSS color for corner accents.")
    font_family: str = Field(default="Arial, sans-serif", description="CSS font family for the slide.")

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
    main_title_font_size: str = Field(default="36px", description="CSS font size for the main title.")
    column_title_font_size: str = Field(default="28px", description="CSS font size for column titles.")
    text_font_size: str = Field(default="16px", description="CSS font size for text content.")
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
    main_title_font_size: str = Field(default="36px", description="CSS font size for the main title.")
    box_title_font_size: str = Field(default="28px", description="CSS font size for box titles.")
    content_font_size: str = Field(default="16px", description="CSS font size for content text.")
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
    steps: List[str] = Field(..., description=f"""A list of step objects, each containing an image URL, a title, and a description. Default: [
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
    font_family_title: str = Field(default="'Playfair Display', serif", description="The font for the main title. An elegant serif font is recommended.")
    font_family_body: str = Field(default="'Montserrat', sans-serif", description="The font for all other text. A clean sans-serif is recommended.")
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
    font_family_title: str = Field(default="'Playfair Display', serif", description="The font for the main title. An elegant serif font is recommended.")
    font_family_body: str = Field(default="'Montserrat', sans-serif", description="The font for all other text. A clean sans-serif is recommended.")
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
    title_font_size: str = Field(default="32px", description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default="20px", description="CSS font size for subtitles.")
    content_font_size: str = Field(default="16px", description="CSS font size for content text.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
    image_url: str = Field(default="Image/generate_body_slide2/Default_1.png", description="Path to the image file for the left side.")
    icon1: str = Field(default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M12 2v6M12 18v4M14.5 8a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0zM16.5 13a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0z"></path></svg>', description="SVG code for the first section's icon.")
    icon2: str = Field(default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>', description="SVG code for the second section's icon.")
    icon3: str = Field(default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>', description="SVG code for the third section's icon.")

class GenerateBodySlide3Input(BaseModel):
    """Input schema for generate_body_slide3."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'MainTitle'.")
    subtitle1: str = Field(..., description="Subtitle for the first content box. Default: 'SUBTITLE1'.")
    content1: str = Field(..., description="Content text for the first content box. Default: 'Content1'.")
    subtitle2: str = Field(..., description="Subtitle for the second content box. Default: 'SUBTITLE2'.")
    content2: str = Field(..., description="Content text for the second content box. Default: 'Content2'.")
    subtitle3: str = Field(..., description="Subtitle for the third content box. Default: 'SUBTITLE3'.")
    content3: str = Field(..., description="Content text for the third content box. Default: 'Content3'.")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    box_bg_color: str = Field(default="#e6f2dd", description="CSS background color for the content boxes.")
    accent_color: str = Field(default="#8cc63f", description="CSS color for accents and icons.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#333333", description="CSS color for subtitles.")
    content_color: str = Field(default="#555555", description="CSS color for content text.")
    title_font_size: str = Field(default="32px", description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default="20px", description="CSS font size for subtitles.")
    content_font_size: str = Field(default="16px", description="CSS font size for content text.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
    box_height: str = Field(default="250px", description="CSS height of the content boxes.")
    icon1: str = Field(default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 9l-5 5-2-2-4 4"></path></svg>', description="SVG code for the first content box's icon.")
    icon2: str = Field(default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>', description="SVG code for the second content box's icon.")
    icon3: str = Field(default='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>', description="SVG code for the third content box's icon.")

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
    title_font_size: str = Field(default="32px", description="CSS font size for the main title.")
    content_font_size: str = Field(default="16px", description="CSS font size for content text.")
    subtitle_font_size: str = Field(default="18px", description="CSS font size for subtitles.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
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
    title_font_size: str = Field(default="32px", description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default="18px", description="CSS font size for subtitles.")
    content_font_size: str = Field(default="14px", description="CSS font size for content text.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
    image_url_1: str = Field(default="Image/generate_body_slide5/Default_1.png", description="Path to the first image file.")
    image_url_2: str = Field(default="Image/generate_body_slide5/Default_2.png", description="Path to the second image file.")
    image_url_3: str = Field(default="Image/generate_body_slide5/Default_3.png", description="Path to the third image file.")
    image_url_4: str = Field(default="Image/generate_body_slide5/Default_4.png", description="Path to the fourth image file.")

class GenerateBodySlide6Input(BaseModel):
    """Input schema for generate_body_slide6."""
    main_title: str = Field(..., description="Main title of the slide. Default: 'MainTitle'.")
    subtitle1: str = Field(..., description="Subtitle for the first content section. Default: 'SUBTITLE1'.")
    content1: str = Field(..., description="Content text for the first content section. Default: 'Content1'.")
    subtitle2: str = Field(..., description="Subtitle for the second content section. Default: 'SUBTITLE2'.")
    content2: str = Field(..., description="Content text for the second content section. Default: 'Content2'.")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accents and subtitle backgrounds.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#333333", description="CSS color for subtitles.")
    content_color: str = Field(default="#555555", description="CSS color for content text.")
    title_font_size: str = Field(default="32px", description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default="18px", description="CSS font size for subtitles.")
    content_font_size: str = Field(default="16px", description="CSS font size for content text.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
    image_url: str = Field(default="Image/generate_body_slide6/Default_1.png", description="Path to the image file for the right side.")

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
    title_font_size: str = Field(default="32px", description="CSS font size for the main title.")
    subtitle_font_size: str = Field(default="28px", description="CSS font size for the subtitle.")
    content_font_size: str = Field(default="16px", description="CSS font size for content text.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
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
    title_font_size: str = Field(default="2rem", description="CSS font size for the main title, should be in REM units for responsive design.")
    subtitle_font_size: str = Field(default="1.25rem", description="CSS font size for all subtitles, should be in REM units for responsive design.")
    content_font_size: str = Field(default="1rem", description="CSS font size for all content text, should be in REM units for responsive design.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="The CSS font family for all text on the slide.")
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
    title_font_size: str = Field(default="2rem", description="CSS font size for the main title, should be in REM units.")
    subtitle_font_size: str = Field(default="1.25rem", description="CSS font size for subtitles, should be in REM units.")
    content_font_size: str = Field(default="1rem", description="CSS font size for content text, should be in REM units.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="The CSS font family for all text on the slide.")
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
    title_font_size: str = Field(default="2rem", description="CSS font size for the main title, should be in REM units for responsive design.")
    content_font_size: str = Field(default="1rem", description="CSS font size for all content text, should be in REM units for responsive design.")
    subtitle_font_size: str = Field(default="1.125rem", description="CSS font size for all subtitles, should be in REM units for responsive design.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="The CSS font family for all text on the slide.")
    image_url_1: str = Field(default="Image/generate_body_slide12/Default_1.png", description="Path to the first image file.")
    image_url_2: str = Field(default="Image/generate_body_slide12/Default_2.png", description="Path to the second image file.")
    image_url_3: str = Field(default="Image/generate_body_slide12/Default_3.png", description="Path to the third image file.")

class GenerateBodySlide13Input(BaseModel):
    """Input schema for generate_body_slide13."""
    main_title: str = Field(..., description="Main title of the slide displayed prominently at the top (e.g., 'Our Four Pillars of Success').")
    subtitle1: str = Field(..., description="Subtitle for the first content section (top-left). Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., '<b>Innovation</b> & Research').")
    content1: str = Field(..., description="Content text for the first content section (top-left). Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Leading <b>innovation</b> through <i>cutting-edge research</i>: <ul><li>Advanced <u>technology</u></li><li>Creative <span style=\"color: #e74c3c;\">solutions</span></li><li>Future-ready products</li></ul>'")
    subtitle2: str = Field(..., description="Subtitle for the second content section (top-right). Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., 'Customer <u>Excellence</u>').")
    content2: str = Field(..., description="Content text for the second content section (top-right). Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Delivering <b>exceptional service</b> and <i>customer satisfaction</i>: <ul><li>24/7 <u>support</u></li><li>Personalized <span style=\"color: #27ae60;\">experiences</span></li><li>Continuous improvement</li></ul>'")
    subtitle3: str = Field(..., description="Subtitle for the third content section (bottom-left). Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., 'Sustainable <b>Growth</b>').")
    content3: str = Field(..., description="Content text for the third content section (bottom-left). Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Building <b>sustainable business</b> practices for <i>long-term success</i>: <ul><li>Environmental <u>responsibility</u></li><li>Social <span style=\"color: #3498db;\">impact</span></li><li>Economic viability</li></ul>'")
    subtitle4: str = Field(..., description="Subtitle for the fourth content section (bottom-right). Can include HTML formatting like <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span> (e.g., 'Team <b>Excellence</b>').")
    content4: str = Field(..., description="Content text for the fourth content section (bottom-right).  Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Empowering <b>talented teams</b> through <i>professional development</i>: <ul><li>Continuous <u>learning</u></li><li>Career <span style=\"color: #9b59b6;\">advancement</span></li><li>Collaborative culture</li></ul>'")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the entire slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accent elements including borders, decorative elements, and highlights.")
    title_color: str = Field(default="#333333", description="CSS color for the main title text.")
    subtitle_color: str = Field(default="#6b9d34", description="CSS color for all subtitle text in the four content sections.")
    content_color: str = Field(default="#555555", description="CSS color for all content/body text in the four sections.")
    title_font_size: str = Field(default="32px", description="CSS font size for the main title, should be in REM units for responsive design.")
    subtitle_font_size: str = Field(default="18px", description="CSS font size for all subtitles, should be in REM units for responsive design.")
    content_font_size: str = Field(default="14px", description="CSS font size for all content text, should be in REM units for responsive design.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="The CSS font family for all text on the slide.")
    image_url: str = Field(default="Image/generate_body_slide13/Default_1.png", description="Path to the image file for the left side.")

class GenerateBodySlide14Input(BaseModel):
    """Input schema for generate_body_slide14."""
    main_title: str = Field(..., description="Main title of the slide displayed at the top (e.g., 'Main Title').")
    subtitle1: str = Field(..., description="Subtitle for the first content section, appears as a section header (e.g., 'Subtitle1').")
    content1: str = Field(..., description="Content text for the first content section. Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Empowering <b>talented teams</b> through <i>professional development</i>: <ul><li>Continuous <u>learning</u></li><li>Career <span style=\"color: #9b59b6;\">advancement</span></li><li>Collaborative culture</li></ul>'")
    subtitle2: str = Field(..., description="Subtitle for the second content section, appears as a section header (e.g., 'Subtitle2').")
    content2: str = Field(..., description="Content text for the second content section. Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Empowering <b>talented teams</b> through <i>professional development</i>: <ul><li>Continuous <u>learning</u></li><li>Career <span style=\"color: #9b59b6;\">advancement</span></li><li>Collaborative culture</li></ul>'")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accents and subtitle backgrounds.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    subtitle_color: str = Field(default="#333333", description="CSS color for subtitles.")
    content_color: str = Field(default="#555555", description="CSS color for content text.")
    title_font_size: str = Field(default="32px", description="CSS font size for the main title, should be in REM units.")
    subtitle_font_size: str = Field(default="18px", description="CSS font size for subtitles, should be in REM units.")
    content_font_size: str = Field(default="16px", description="CSS font size for content text, should be in REM units.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
    image_url_1: str = Field(default="Image/generate_body_slide14/Default_1.png", description="Path to the first image file.")
    image_url_2: str = Field(default="Image/generate_body_slide14/Default_2.png", description="Path to the second image file.")

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
    title_font_size: str = Field(default="2rem", description="CSS font size for the main title, should be in REM units.")
    subtitle_font_size: str = Field(default="1.125rem", description="CSS font size for the subtitle, should be in REM units.")
    content_font_size: str = Field(default="1rem", description="CSS font size for content text, should be in REM units.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")

class GenerateBodySlide16Input(BaseModel):
    """Input schema for generate_body_slide16."""
    main_title: str = Field(..., description="Main title of the slide displayed at the top with an accent block (e.g., 'MainTitle').")
    section1_content: str = Field(..., description="HTML content for the first section with icon. Structure: '<ul>Section Title<li>Point 1</li><li>Point 2</li></ul>'. The first text node in <ul> becomes the section title. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. Example: '<ul>Core <b>Values</b><li>Innovation and <i>creativity</i></li><li>Customer <u>satisfaction</u></li><li>Team <span style=\"color: #9b59b6;\">collaboration</span></li></ul>'")
    section2_content: str = Field(..., description="HTML content for the second section with icon. Structure: '<ul>Section Title<li>Point 1</li><li>Point 2</li></ul>'. The first text node in <ul> becomes the section title. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. Example: '<ul>Core <b>Values</b><li>Innovation and <i>creativity</i></li><li>Customer <u>satisfaction</u></li><li>Team <span style=\"color: #9b59b6;\">collaboration</span></li></ul>'")
    section3_content: str = Field(..., description="HTML content for the third section with icon. Structure: '<ul>Section Title<li>Point 1</li><li>Point 2</li></ul>'. The first text node in <ul> becomes the section title. Use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. Example: '<ul>Core <b>Values</b><li>Innovation and <i>creativity</i></li><li>Customer <u>satisfaction</u></li><li>Team <span style=\"color: #9b59b6;\">collaboration</span></li></ul>'")
    main_bg_color: str = Field(default="#ffffff", description="CSS background color for the slide.")
    left_bg_color: str = Field(default="#d5e8b9", description="CSS background color for the left column containing the content sections.")
    accent_color: str = Field(default="#d5e8b9", description="CSS color for accent elements like the title accent block and icons.")
    title_color: str = Field(default="#333333", description="CSS color for the main title.")
    section_title_color: str = Field(default="#ffffff", description="CSS color for section titles.")
    content_color: str = Field(default="#333333", description="CSS color for content text and bullet points.")
    main_title_font_size: str = Field(default="1.625rem", description="CSS font size for the main title, should be in REM units.")
    section_title_font_size: str = Field(default="0.9375rem", description="CSS font size for section titles, should be in REM units.")
    content_font_size: str = Field(default="0.8125rem", description="CSS font size for content text, should be in REM units.")
    font_family: str = Field(default="'Segoe UI', Arial, sans-serif", description="CSS font family for the slide.")
    container_padding: str = Field(default="2.1875rem", description="CSS padding for the slide container, should be in REM units.")
    left_column_width: str = Field(default="58%", description="CSS width for the left column as a percentage.")
    right_column_width: str = Field(default="42%", description="CSS width for the right column as a percentage.")
    left_column_padding: str = Field(default="1.5625rem", description="CSS padding for the left column, should be in REM units.")
    title_margin_bottom: str = Field(default="1.5625rem", description="CSS bottom margin for the title section, should be in REM units.")
    icon_size: str = Field(default="2.8125rem", description="CSS size for the circular icon containers, should be in REM units.")
    icon_margin_right: str = Field(default="0.75rem", description="CSS right margin for icons, should be in REM units.")
    section_margin: str = Field(default="0.5rem", description="CSS margin for content sections, should be in REM units.")
    divider_margin: str = Field(default="0.75rem", description="CSS margin for section dividers, should be in REM units.")
    icon1: str = Field(default="<svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"10\"/></svg>", description="SVG code for the first section icon.")
    icon2: str = Field(default="<svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"10\"/></svg>", description="SVG code for the second section icon.")
    icon3: str = Field(default="<svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><circle cx=\"12\" cy=\"12\" r=\"10\"/></svg>", description="SVG code for the third section icon.")
    image_path: str = Field(default="Picture2.png", description="Path to the image file for the right column.")

class GenerateBodySlide17Input(BaseModel):
    """Input schema for generate_body_slide17."""
    main_title: str = Field(..., description="The main title displayed at the top center of the slide (e.g., 'Main title').")
    left_title: str = Field(..., description="The subtitle for the left column content (e.g., 'Subtitle 1').")
    right_title: str = Field(..., description="The subtitle for the right column content (e.g., 'Subtitle 2').")
    left_text: str = Field(..., description="The main text content for the left column. Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Empowering <b>talented teams</b> through <i>professional development</i>: <ul><li>Continuous <u>learning</u></li><li>Career <span style=\"color: #9b59b6;\">advancement</span></li><li>Collaborative culture</li></ul>'")
    right_text: str = Field(..., description="The main text content for the right column. Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. For structured content with main points and sub-points, use <ul> and <li> tags. Example: 'Achieving <b>sustainable growth</b> through <i>innovation</i>: <ul><li>Market <u>expansion</u></li><li>Product <span style=\"color: #e74c3c;\">differentiation</span></li><li>Customer satisfaction</li></ul>'")
    footer_text: str = Field(..., description="Summary or concluding text displayed at the bottom of the slide. Should use HTML tags to highlight key phrases: <b>bold</b>, <i>italic</i>, <u>underline</u>, or <span style=\"color: #...;\">colored text</span>. Can also include structured content with <ul> and <li> tags for bullet points.")
    circle_colors: List[str] = Field(default=["#e1eff2", "#8cbeca", "#e1eff2"], description="Array of three CSS color values for the circles. Order: [left circle, center circle, right circle].")
    main_title_font_size: str = Field(default="2.25rem", description="CSS font size for the main title, should be in REM units.")
    section_title_font_size: str = Field(default="1.5rem", description="CSS font size for the section titles (left and right), should be in REM units.")
    text_font_size: str = Field(default="1rem", description="CSS font size for the main text content, should be in REM units.")
    footer_font_size: str = Field(default="0.875rem", description="CSS font size for the footer text, should be in REM units.")
    title_color: str = Field(default="#555555", description="CSS color for all titles (main title and section titles).")
    text_color: str = Field(default="#555555", description="CSS color for all text content including footer.")
    circle_text_color: str = Field(default="#ffffff", description="CSS color for any text that might be displayed inside the circles.")
    background_color: str = Field(default="#ffffff", description="CSS background color for the slide content area.")
    accent_color: str = Field(default="#a2c4c9", description="CSS color for the decorative corner elements.")
    font_family: str = Field(default="Arial, sans-serif", description="The CSS font family for all text on the slide.")

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
    main_title_font_size: str = Field(default="36px", description="CSS font size for the main title.")
    column_title_font_size: str = Field(default="28px", description="CSS font size for the column titles.")
    text_font_size: str = Field(default="16px", description="CSS font size for the text content.")
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
    main_title_font_size: str = Field(default="2.25rem", description="CSS font size for the main title, should be in REM units.")
    column_title_font_size: str = Field(default="1.5rem", description="CSS font size for the column section titles, should be in REM units.")
    column_text_font_size: str = Field(default="1rem", description="CSS font size for the column text content, should be in REM units.")
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
    main_title_font_size: str = Field(default="2.25rem", description="CSS font size for the main title.")
    column_title_font_size: str = Field(default="1.75rem", description="CSS font size for the column titles.")
    text_font_size: str = Field(default="1rem", description="CSS font size for the text content.")
    title_color: str = Field(default="#555555", description="CSS color for all titles (main title and column titles).")
    text_color: str = Field(default="#555555", description="CSS color for all text content.")
    icon_color: str = Field(default="#a2c4c9", description="CSS color for the icons.")
    background_color: str = Field(default="#ffffff", description="CSS background color for the main content area.")
    accent_color: str = Field(default="#a2c4c9", description="CSS color for the border/frame background.")
    divider_color: str = Field(default="#555555", description="CSS color for the dashed divider line between columns.")
    font_family: str = Field(default="Arial, sans-serif", description="The CSS font family for all text on the slide.")

class GenerateStrategySlideInput(BaseModel):
    """Input schema for generate_strategy_slide."""
    main_title: str = Field(..., description="A brief, concise title for the header section. Default: 'Your Strategic Topic Here'.")
    subtitle: str = Field(..., description="A short subtitle providing context, displayed below the main title. Default: 'Add your key message or objective statement.'.")
    left_column_title: str = Field(..., description="The main, large title for the left content card. Default: 'First Strategic Point'.")
    left_column_content: str = Field(..., description="The detailed description text for the left content card. Default: 'Elaborate on your first main point or strategy. Provide details and benefits.'.")
    right_column_title: str = Field(..., description="The main, large title for the right content card. Default: 'Second Strategic Point'.")
    right_column_content: str = Field(..., description="The detailed description text for the right content card. Default: 'Elaborate on your second main point or strategy. Provide details and benefits.'.")
    font_family: str = Field(default="'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", description="The font family for all text elements.")
    header_bg_color: str = Field(default="#E0F2FE", description="Background color for the minimalist header section (light blue).")
    content_bg_color: str = Field(default="#F8FAFC", description="Overall background color for the main content area (off-white).")
    card_bg_color: str = Field(default="#FFFFFF", description="Background color for the two prominent content cards.")
    title_color: str = Field(default="#1E3A8A", description="Text color for all titles (header and column titles) (dark navy).")
    subtitle_color: str = Field(default="#475569", description="Text color for the header subtitle and the column content text (neutral gray).")
    accent_color: str = Field(default="#3B82F6", description="The accent color used for the decorative icons above each column (vibrant blue).")

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

class GenerateHorizontalTimelineSlideInput(BaseModel):
    """Input schema for generate_horizontal_timeline_slide."""
    title: str = Field(..., description="Main title displayed at the top of the slide. Default: 'Add a Timeline Page'.")
    timeline_items: List[Dict[str, str]] = Field(..., description="Array of timeline milestones. Each item should have 'year', 'position', 'main_point', and 'description' keys. A maximum of 5 items is strongly recommended for optimal visual clarity on the clean, bright layout. Default: [{'year': '2015', 'position': 'bottom', 'main_point': 'Add a main point', 'description': 'Elaborate on what you want to discuss.'}, {'year': '2016', 'position': 'top', 'main_point': 'Add a main point', 'description': 'Elaborate on what you want to discuss.'}, {'year': '2017', 'position': 'bottom', 'main_point': 'Add a main point', 'description': 'Elaborate on what you want to discuss.'}, {'year': '2018', 'position': 'top', 'main_point': 'Add a main point', 'description': 'Elaborate on what you want to discuss.'}, {'year': '2019', 'position': 'bottom', 'main_point': 'Add a main point', 'description': 'Elaborate on what you want to discuss.'}].")
    font_family: str = Field(default="'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", description="Font family for all text elements. 'Inter' is recommended for this modern design.")

class GenerateCorporateContentSlideInput(BaseModel):
    """Input schema for generate_corporate_content_slide."""
    main_title: str = Field(..., description="The main title displayed in the colored panel on the left. To highlight a word, wrap it in `<span class='highlight'>...</span>`. Default: 'THIS IS A <span class=\'highlight\'>SLIDE</span> TITLE'.")
    list_items: List[Dict[str, str]] = Field(..., description="An array of objects, where each object represents a content card with its own title and description. Default: [{'title': 'First Key Point', 'description': 'Here you have a list of items, presented in a modern, card-based format.'}, {'title': 'Second Key Point', 'description': 'And some text to elaborate on the second main idea of your slide.'}, {'title': 'Third Key Point', 'description': 'But remember not to overload your slides with too much content.'}]")
    font_family: str = Field(default="'Montserrat', sans-serif", description="Font family for all text elements.")
    bg_color: str = Field(default="#F8FAFC", description="The background color for the main content area (typically off-white).")
    accent_panel_color: str = Field(default="#6366F1", description="The background color for the diagonal title panel.")
    title_color: str = Field(default="#FFFFFF", description="Text color for the main title on the colored panel.")
    list_title_color: str = Field(default="#1F2937", description="Text color for the titles inside the content cards.")
    list_text_color: str = Field(default="#4B5563", description="Text color for the description text inside the content cards.")

class GenerateSplitContentSlideInput(BaseModel):
    """Input schema for generate_split_content_slide."""
    main_title: str = Field(..., description="The main title at the top of the slide. Use `<span class='highlight'>...</span>` to color a word with the accent color. Default: 'SPLIT YOUR CONTENT'.")
    columns: List[Dict[str, str]] = Field(..., description="An array of exactly 2 objects, each representing a content card with an icon, title, and description. Default: [{'icon_name': 'bulb', 'title': 'Title One', 'description': 'Description for the first column goes here. Elaborate on your point with clear and concise text.'}, {'icon_name': 'target', 'title': 'Title Two', 'description': 'Description for the second column. This layout is perfect for comparing two ideas side-by-side.'}]")
    font_family: str = Field(default="'Montserrat', sans-serif", description="Font family for all text elements.")
    bg_gradient_start: str = Field(default="#0F172A", description="The starting color (top) of the dark background gradient.")
    bg_gradient_end: str = Field(default="#1E293B", description="The ending color (bottom) of the dark background gradient.")
    title_color: str = Field(default="#FFFFFF", description="The color for the main title and the card titles.")
    text_color: str = Field(default="#D1D5DB", description="The color for the card descriptions.")
    accent_color: str = Field(default="#22D3EE", description="The neon accent color used for highlights, card borders, and icons.")

class GenerateCorporateMulticolumnSlideInput(BaseModel):
    """Input schema for generate_corporate_multicolumn_slide."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks and <span class='highlight'>word</span> to highlight. Will be displayed in large 2.5rem font. Default: 'IN TWO OR THREE<br><span class=\'highlight\'>COLUMNS</span>'.")
    columns: List[Dict[str, str]] = Field(..., description="An array of 2 or 3 objects, each representing a column. Each column will be displayed as a card with gradient background, rounded corners, and hover effects. Default: [{'title': 'Yellow', 'description': 'Is the color of gold, butter and ripe lemons.'}, {'title': 'Blue', 'description': 'Is the colour of the clear sky and the deep sea.'}, {'title': 'Red', 'description': 'Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage.'}]")
    font_family: str = Field(default="'Montserrat', sans-serif", description="The font family for all text elements. Enhanced with additional font weights (400, 600, 700, 800).")
    accent_color: str = Field(default="#8B5CF6", description="The primary accent color for the right panel, highlighted text, and card accent borders. Used in gradients for enhanced visual appeal.")
    shadow_color: str = Field(default="#7C3AED", description="The secondary (darker) accent color for the panel behind and gradient effects.")
    text_color: str = Field(default="#4B5563", description="The primary color for the body text.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small globe icon. Icon size increased to 3.5rem with drop-shadow effect.")

class GenerateCorporateGridSlideInput(BaseModel):
    """Input schema for generate_corporate_grid_slide."""
    main_title: str = Field(..., description="The main title for the slide. Use <br> for line breaks and <span class='highlight'>word</span> to highlight. Will be displayed in large 2.5rem font with uppercase styling. Default: 'LET'S <span class=\'highlight\'>REVIEW</span> SOME<br>CONCEPTS'.")
    grid_items: List[Dict[str, str]] = Field(..., description="An array of exactly 6 objects for the 2x3 grid. Each item will be displayed as a card with gradient background, rounded corners, hover effects, and colored top border. Grid automatically adjusts to 2 columns on smaller screens. Default: [{'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}, {'title': 'title', 'description': 'description.'}]")
    font_family: str = Field(default="'Montserrat', sans-serif", description="The font family for all text elements. Enhanced with additional font weights (400, 600, 700, 800).")
    accent_color: str = Field(default="#22C55E", description="The primary accent color for the right panel, highlighted text, and card accent borders. Used in gradients for enhanced visual appeal.")
    shadow_color: str = Field(default="#16A34A", description="The secondary (darker) accent color for the panel behind and gradient effects.")
    text_color: str = Field(default="#6B7280", description="The primary color for the body text.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small pencil icon. Icon size increased to 3.5rem with drop-shadow effect.")
    bg_color: str = Field(default="#FFFFFF", description="The background color of the entire slide. Default is white.")

class GenerateBusinessOverviewSlideInput(BaseModel):
    """Input schema for generate_business_overview_slide."""
    main_title: str = Field(..., description="Main title text (10-25 characters), displayed on the left side. Default: 'BUSINESS OVERVIEW'.")
    sections: List[str] = Field(..., description="List of dictionaries with icon and content for each section. Icons: 'chart-analysis', 'innovation', 'growth'. . Default: 3 sections with Lorem ipsum content.")
    left_bg_color: str = Field(default="#1a4b8c", description="Background color for the left title section (hex code).")
    right_bg_color: str = Field(default="#f8f9fa", description="Background color for the right content area (hex code).")
    title_color: str = Field(default="#FFFFFF", description="Color of the main title text (hex code).")
    icon_bg_color: str = Field(default="#2a3f6b", description="Background color for icon containers (hex code).")
    icon_color: str = Field(default="#FFFFFF", description="Color of the icons (hex code).")
    content_bg_color: str = Field(default="#FFFFFF", description="Background color for content text areas (hex code).")
    content_text_color: str = Field(default="#1a4b8c", description="Text color for content sections (hex code).")
    title_font_size: str = Field(default="3.5rem", description="Font size for the main title.")
    content_font_size: str = Field(default="0.95rem", description="Font size for section content text.")
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
    title_font_size: str = Field(default="4rem", description="Font size for section titles.")
    content_font_size: str = Field(default="1rem", description="Font size for content text.")
    number_font_size: str = Field(default="8rem", description="Font size for large background numbers.")
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
    goals: List[str] = Field(..., description="List of dictionaries with number and content for each strategic goal. . Default: 3 goals with Lorem ipsum content.")
    bg_image: str = Field(default="skyscrapers.jpg", description="Background image URL or path (skyscraper/city image recommended).")
    bg_overlay_color: str = Field(default="rgba(26, 75, 140, 0.85)", description="Color overlay for the background image (rgba with transparency).")
    title_color: str = Field(default="#FFFFFF", description="Color of the main title text (hex code).")
    number_bg_color: str = Field(default="#1a4b8c", description="Background color for the number circles (hex code).")
    number_text_color: str = Field(default="#FFFFFF", description="Text color for the numbers (hex code).")
    content_bg_color: str = Field(default="#FFFFFF", description="Background color for content text boxes (hex code).")
    content_text_color: str = Field(default="#1a4b8c", description="Text color for content (hex code).")
    title_font_size: str = Field(default="4.5rem", description="Font size for the main title.")
    number_font_size: str = Field(default="2.5rem", description="Font size for the numbers.")
    content_font_size: str = Field(default="0.9rem", description="Font size for content text.")
    font_family: str = Field(default="Arial, sans-serif", description="Font family for all text elements.")
    show_border: Optional[bool] = Field(default=True, description="Whether to show the dashed border frame. Default: True.")
    border_opacity: Optional[float] = Field(default=0, description="Opacity of the border frame (0.0 to 1.0). Default: 0.4.")
    number_circle_size: str = Field(default="80px", description="Size of the circular number containers.")
    content_padding: str = Field(default="20px", description="Padding inside content boxes.")
    custom_css: str = Field(default="''", description="Additional custom CSS to be included.")

class GenerateServiceRoadmapSlideInput(BaseModel):
    """Input schema for generate_service_roadmap_slide."""
    main_title: str = Field(..., description="Main title text (10-30 characters), displayed at the top center. Default: 'SERVICE ROADMAP'.")
    roadmap_items: List[str] = Field(..., description="List of dictionaries with title and content for each roadmap phase. . Default: 4 phases with Lorem ipsum content.")
    bg_gradient_start: str = Field(default="#4A90E2", description="Starting color of the background gradient (hex code).")
    bg_gradient_end: str = Field(default="#2E5BBA", description="Ending color of the background gradient (hex code).")
    title_color: str = Field(default="#FFFFFF", description="Color of the main title text (hex code).")
    card_bg_color: str = Field(default="#FFFFFF", description="Background color for content cards (hex code).")
    card_text_color: str = Field(default="#2E5BBA", description="Text color for card content (hex code).")
    card_title_color: str = Field(default="#1A4480", description="Text color for card titles (hex code).")
    title_font_size: str = Field(default="4rem", description="Font size for the main title.")
    card_title_font_size: str = Field(default="1.2rem", description="Font size for card titles.")
    card_content_font_size: str = Field(default="0.9rem", description="Font size for card content text.")
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
    cards: List[str] = Field(..., description="List of dictionaries with 'title' and 'content' keys for each card. . Default: 3 cards with financial topics and Lorem ipsum content.")
    background_color: str = Field(default="#1E3A8A", description="Solid background color (dark blue).")
    main_title_color: str = Field(default="#FFFFFF", description="Color of the main title text.")
    card_background_color: str = Field(default="rgba(255, 255, 255, 0.95)", description="Background color of the cards.")
    card_title_color: str = Field(default="#1E3A8A", description="Color of the card titles.")
    card_content_color: str = Field(default="#374151", description="Color of the card content text.")
    border_color: str = Field(default="rgba(255, 255, 255, 0.3)", description="Color of the border elements.")
    font_family: str = Field(default="Segoe UI, Arial, sans-serif", description="Font family for all text elements.")
    main_title_font_size: str = Field(default="4.5rem", description="Font size of the main title.")
    main_title_font_weight: str = Field(default="700", description="Font weight of the main title.")
    main_title_letter_spacing: str = Field(default="0.05em", description="Letter spacing of the main title.")
    card_title_font_size: str = Field(default="1.8rem", description="Font size of the card titles.")
    card_title_font_weight: str = Field(default="700", description="Font weight of the card titles.")
    card_title_letter_spacing: str = Field(default="0.02em", description="Letter spacing of the card titles.")
    card_content_font_size: str = Field(default="1rem", description="Font size of the card content.")
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
    font_size_multiplier: Optional[float] = Field(default=1.0, description="Adjusts the default responsive font size. 1.0 is standard. Ignored if a fixed font size is set.")
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
    columns: List[Dict[str, str]] = Field(..., description="An array of objects, where each object represents a column. Default: [{'icon_name': 'bulb', 'title': 'Column One', 'description': 'Description for column one.'}, {'icon_name': 'target', 'title': 'Column Two', 'description': 'Description for column two.'}].")
    font_family: str = Field(default="'Nunito', sans-serif", description="The font family for all text elements.")
    text_color: str = Field(default="#F8FAFC", description="The color for all text elements.")
    sky_color: str = Field(default="#0F172A", description="The solid background color for the slide. Note: This parameter is not used in the current function implementation.")
    grid_dot_color: str = Field(default="rgba(255, 255, 255, 0.1)", description="The color and opacity for the dots in the background grid.")

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
    font_family: str = Field(default="'Montserrat', sans-serif", description="Font family for all text elements.")
    bg_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    main_title_color: str = Field(default="#111827", description="Text color for the main title.")
    point_title_color: str = Field(default="#1F2937", description="Text color for the point titles.")
    point_description_color: str = Field(default="#4B5563", description="Text color for the point descriptions.")
    accent_color: str = Field(default="#3B82F6", description="The single accent color used for all icon circles and the decorative divider.")

class GenerateFlexibleColumnsSlideInput(BaseModel):
    """Input schema for generate_flexible_columns_slide."""
    main_title: str = Field(..., description="The main title displayed at the top of the slide. Default: 'IN TWO OR THREE COLUMNS'.")
    columns: List[Dict[str, str]] = Field(..., description="An array of 1 to 6 objects, each representing a column with its own title and description. Default: [{'title': 'Yellow', 'description': 'Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange.'}, {'title': 'Blue', 'description': 'Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum.'}, {'title': 'Red', 'description': 'Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage.'}].")
    font_family_heading: str = Field(default="'Patrick Hand', cursive", description="The handwritten-style font for the main title.")
    font_family_body: str = Field(default="'Lato', sans-serif", description="The standard font for the column titles and text.")
    text_color: str = Field(default="#34495E", description="The color for all text elements.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the repeating paper texture background.")

class GenerateTextWithImageSlideInput(BaseModel):
    """Input schema for generate_text_with_image_slide."""
    title: str = Field(..., description="The introductory headline for the text column, styled to be smaller. Default: 'Tiltle'.")
    text_content: str = Field(..., description="The main paragraph or body text, displayed in a large font to be the central focus of the text column. Default: 'Content.'.")
    image_url: str = Field(default="https://images.pexels.com/photos/1778412/pexels-photo-1778412.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1", description="URL for the full-height image on the right side.")
    font_family_heading: str = Field(default="'Patrick Hand', cursive", description="The handwritten-style font for the title.")
    font_family_body: str = Field(default="'Lato', sans-serif", description="The standard font for the body text.")
    text_color: str = Field(default="#34495E", description="The color for all text elements.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the repeating paper texture background.")
    doodle_border_url: str = Field(default="https://i.imgur.com/Qy2O1vN.png", description="URL for the seamless doodle image used as a border at the bottom.")

class GenerateInstructionsSlideInput(BaseModel):
    """Input schema for generate_instructions_slide."""
    main_title: str = Field(..., description="The main title displayed in the header bar. Default: 'TOPIC'.")
    columns: List[Dict[str,List[str]]] = Field(..., description="An array of exactly 3 objects, each representing a column. Each object should have 'title' and 'list_items' keys. The content is styled with large fonts for easy reading. Default: [{'title': 'TOPIC ONE', 'list_items': ['First instruction point.', 'Second instruction point.', 'Third instruction point.']}, {'title': 'TOPIC TWO', 'list_items': ['First instruction point.', 'Second instruction point.', 'Third instruction point.']}, {'title': 'TOPIC THREE', 'list_items': ['First instruction point.', 'Second instruction point.', 'Third instruction point.']}].")
    font_family: str = Field(default="'Poppins', sans-serif", description="Font family for all text elements.")
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
    font_family: str = Field(default="'Poppins', sans-serif", description="The font family for all text elements.")
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
    font_family: str = Field(default="'Poppins', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for all text elements.")

class GenerateGeometricImageContentSlideInput(BaseModel):
    """Input schema for generate_geometric_image_content_slide."""
    image_url: str = Field(default="https://images.unsplash.com/photo-1557804506-669a67965ba0?q=80&w=2574&auto=format&fit=crop", description="The URL for the main image to be displayed in the custom-shaped container.")
    main_title: str = Field(..., description="The main title for the slide. Use a `<span class='highlight'>` tag to highlight a specific word. Default: 'A picture is worth a <span class='highlight'>thousand</span> words'.")
    description: str = Field(..., description="The paragraph of text that describes or complements the image. Default: 'A complex idea can be conveyed with just a single still image, namely making it possible to absorb large amounts of data quickly.'.")
    font_family: str = Field(default="'Poppins', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for the non-highlighted text.")

class GenerateGeometricContentSlideInput(BaseModel):
    """Input schema for generate_geometric_content_slide."""
    main_title: str = Field(..., description="The main title for the content slide, rendered in extra-bold weight. Default: 'Our Core Strategy'.")
    list_items: List[str] = Field(..., description="A list of strings for the bullet points. Each string will be a separate list item rendered in semi-bold weight. Default: ['Focus on <b><i><u><span style=\'color:#A3E635;\'>user-centric design</span></u></i></b>.', 'Innovate with purpose and clarity.', 'Build for <b><i><u><span style=\'color:#A3E635;\'>scalability and performance</span></u></i></b>.']")
    concluding_text: str = Field(..., description="A final sentence or paragraph displayed below the list, rendered in semi-bold weight. Default: 'These principles guide our every move forward.'.")
    font_family: str = Field(default="'Poppins', sans-serif", description="The font family for all text elements. Should support weights 600 and 800.")
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
    font_family: str = Field(default="'Poppins', sans-serif", description="The font family for all text elements.")
    bg_color: str = Field(default="#0F172A", description="The dark background color of the slide.")
    text_color: str = Field(default="#FFFFFF", description="The color for all text elements.")

class GenerateMemphisContentSlideInput(BaseModel):
    """Input schema for generate_memphis_content_slide."""
    main_title: str = Field(..., description="The main title of the slide, displayed in the top panel. Default: 'This is a slide title'.")
    list_items: List[str] = Field(..., description="A list of strings for the bullet points in the bottom panel. Default: ['Here you have a list of items', 'And some text', 'But remember not to overload your slides with content'].")
    concluding_text: str = Field(..., description="A final sentence or paragraph displayed below the list. Default: 'Your audience will listen to you or read the content, but won't do both.'.")
    font_family_title: str = Field(default="'Lora', serif", description="The elegant, serif font for the main title.")
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
    font_family_title: str = Field(default="'Lora', serif", description="The elegant, serif font for the main title.")
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
    font_family_title: str = Field(default="'Lora', serif", description="The elegant, serif font for the main title.")
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
    font_family: str = Field(default="'Montserrat', sans-serif", description="Font family for all text elements.")
    bg_color: str = Field(default="#F8FAFC", description="Background color of the slide.")
    title_color: str = Field(default="#111827", description="Text color for the main title.")
    subtitle_color: str = Field(default=None, description="Text color for the subtitle.")
    card_text_color: str = Field(default="#1F2937", description="Text color for the name and role on the cards.")

class GenerateCorporateTeamSlideInput(BaseModel):
    """Input schema for generate_corporate_team_slide."""
    main_title: str = Field(..., description="The main title for the slide, e.g., 'Our Creative Team'. Default: 'Our Creative Team'.")
    team_members: List[Dict[str, str]] = Field(..., description="An array of objects, each representing a team member with their own photo. Default: [{'name': 'Olivia Chen', 'role': 'Lead Designer', 'image_url': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1887&auto=format=fit=crop'}, {'name': 'Ben Carter', 'role': 'Photographer', 'image_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1887&auto=format=fit=crop'}, {'name': 'Aisha Khan', 'role': 'Content Strategist', 'image_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1887&auto=format=fit=crop'}, {'name': 'Leo Martinez', 'role': 'Illustrator', 'image_url': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=1887&auto=format=fit=crop'}]")
    font_family_heading: str = Field(default="'Patrick Hand', cursive", description="The handwritten-style font for the main title and member names.")
    font_family_body: str = Field(default="'Lato', sans-serif", description="The standard font for the member roles.")
    text_color: str = Field(default="#4A403A", description="The main text color for names.")
    role_color: str = Field(default="#6B7280", description="The secondary text color for roles.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the repeating paper texture background.")

# === SLIDE CẢM ƠN CLASSES ===

class GenerateThankYouSlide2Input(BaseModel):
    """Input schema for generate_thank_you_slide_2."""
    main_text: str = Field(default="THANKS!", description="The main 'Thanks!' message, displayed in a large, handwritten font.")
    question_text: str = Field(default="Any questions?", description="The secondary text, typically for Q&A.")
    font_family_heading: str = Field(default="'Patrick Hand', cursive", description="The handwritten-style font for the main text.")
    font_family_body: str = Field(default="'Lato', sans-serif", description="The standard font for the secondary text.")
    main_color: str = Field(default="#56B2E8", description="The main accent color for the heart icon and the main text.")
    text_color: str = Field(default="#34495E", description="The color for the secondary text.")
    bg_url: str = Field(default="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png", description="URL for the background texture.")

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
    main_title_font_size: str = Field(default="6rem", description="Font size of the main title.")
    main_title_font_weight: str = Field(default="700", description="Font weight of the main title.")
    main_title_letter_spacing: str = Field(default="0.1em", description="Letter spacing of the main title.")
    contact_font_size: str = Field(default="1.2rem", description="Font size of contact information.")
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

class GenerateThankYouSlideInput(BaseModel):
    """Input schema for generate_thank_you_slide."""
    title: str = Field(..., description="The main, extra-large thank-you message. Default: 'Thank You!'.")
    subtitle: str = Field(..., description="The subtext displayed below the main title. Default: 'We appreciate your time and attention. Please feel free to reach out with any questions.'.")
    font_family: str = Field(default="'Poppins', 'Segoe UI', sans-serif", description="The font family for all text. 'Poppins' is highly recommended for this modern design.")
    background_gradient: str = Field(default="linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)", description="A CSS linear-gradient string for the slide's animated background.")
    accent_color: str = Field(default="#FFD700", description="The main accent color used for the title, heart icon, and animated sparkles. Gold is the default.")
    card_color: str = Field(default="#FFFFFF", description="The background color of the central content card.")
    text_color: str = Field(default="#333333", description="The color of the subtitle text.")

class GenerateCorporateThankYouSlideInput(BaseModel):
    """Input schema for generate_corporate_thank_you_slide."""
    thanks_text: str = Field(default="THANK YOU FOR WACTCHING!", description="The main closing message, e.g., 'THANKS!'. .")
    font_family: str = Field(default="'Montserrat', sans-serif", description="The font family for the text.")
    accent_color: str = Field(default="#F97316", description="The primary accent color for the right panel and the 'Thanks' text.")
    shadow_color: str = Field(default="#EA580C", description="The secondary (darker) accent color for the panel behind.")
    icon_color: str = Field(default="#D1D5DB", description="The color for the small smiley icon.")

# All available slide generation tools with complete parameter schemas
ALL_TOOLS = [
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

    # === SLIDE CHUYỂN SLIDE ===
    StructuredTool.from_function(
        func=generate_geometric_transition_slide,
        name="generate_geometric_transition_slide",
        description="Generates a dynamic and modern **Transition or Section Header Slide**. Its most distinct characteristic is the use of vibrant, multi-colored geometric shapes (parallelograms) clustered in the corners. With a dark background and high-impact, centered text, this slide is perfect for introducing new sections in technology, creative, or modern corporate presentations.",
        args_schema=GenerateGeometricTransitionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_transition_slide_2,
        name="generate_transition_slide_2",
        description="Generates a Transition or Section Break Slide with a charming, hand-drawn aesthetic. This slide is characterized by its notebook paper background and friendly, handwritten-style fonts. It has been enhanced with **extra-large, high-impact typography** for the section number, headline, and subtitle, making it an unmissable and bold divider between topics. Perfect for educational presentations, creative workshops, or any talk wanting a fun and clear structural break.",
        args_schema=GenerateTransitionSlide2Input
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
        func=generate_corporate_transition_slide,
        name="generate_corporate_transition_slide",
        description="Generates a modern and architectural **Section Header or Transition Slide**. It features a striking design with multiple overlapping, angled color panels on the right, creating a strong sense of depth and structure. The left side is a clean text area with large, impactful typography (including a section number), making this slide perfect for introducing new chapters in a professional, high-tech, or corporate presentation.",
        args_schema=GenerateCorporateTransitionSlideInput
    ),
    StructuredTool.from_function(
        func=generate_intro_slide,
        name="generate_intro_slide",
        description="Generates an HTML introduction slide with a  main title section on the left and an image on the right.",
        args_schema=GenerateIntroSlideInput
    ),
    StructuredTool.from_function(
        func=generate_credits_slide,
        name="generate_credits_slide",
        description="Generate a credits/thank you slide with warm peach gradient background, emoji characters, and decorative dots. Features script typography for main content and branded header badge. Perfect for presentation endings, acknowledgments, template credits, or closing slides in creative, educational, and business presentations.",
        args_schema=GenerateCreditsSlideInput
    ),

    # === SLIDE CONTENT ===
    StructuredTool.from_function(
        func=generate_content_slide,
        name="generate_content_slide",
        description="Generates an HTML slide with a main title and a grid of numbered items, ideal for listing topics or points.",
        args_schema=GenerateContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_two_column_slide,
        name="generate_two_column_slide",
        description="Generates an HTML slide with two columns of titles and texts, with customizable styling.",
        args_schema=GenerateTwoColumnSlideInput
    ),
    StructuredTool.from_function(
        func=generate_project_circles_slide,
        name="generate_project_circles_slide",
        description="Generates an HTML slide with a main title, two text columns, three project circles, and an alternating border design.",
        args_schema=GenerateProjectCirclesSlideInput
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
        func=generate_body_slide3,
        name="generate_body_slide3",
        description="Generates an HTML slide with a main title and three content boxes, each with an icon, subtitle, and content text in a three-column layout.",
        args_schema=GenerateBodySlide3Input
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
        func=generate_body_slide6,
        name="generate_body_slide6",
        description="Generates an HTML slide with a main title, an image on the right, and two content sections on the left.",
        args_schema=GenerateBodySlide6Input
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
        func=generate_body_slide13,
        name="generate_body_slide13",
        description="Generates an HTML slide with a main title, a 2x2 image grid on the left, and four content sections on the right.",
        args_schema=GenerateBodySlide13Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide14,
        name="generate_body_slide14",
        description="Generates an HTML slide with a main title, an image on the right, and two content sections on the left.",
        args_schema=GenerateBodySlide14Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide15,
        name="generate_body_slide15",
        description="Generates an HTML slide with a main title, three vertical images on the left, and a subtitle with two content sections on the right, separated by a divider.",
        args_schema=GenerateBodySlide15Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide16,
        name="generate_body_slide16",
        description="Generates an HTML slide with a two-column layout: left column contains a main title and three icon-based content sections with bullet points, right column displays an image.",
        args_schema=GenerateBodySlide16Input
    ),
    StructuredTool.from_function(
        func=generate_body_slide17,
        name="generate_body_slide17",
        description="Generates an HTML slide with three overlapping circles in the center, text content on left and right sides, and decorative corner elements.",
        args_schema=GenerateBodySlide17Input
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
        func=generate_strategy_slide,
        name="generate_strategy_slide",
        description="Generates a **Content Slide** with a two-column layout, specifically designed to emphasize the main content over the header. This slide features a bright, clean, and professional aesthetic with a minimalist header, an off-white background, and two prominent content cards, each highlighted by a large icon. It's ideal for presenting detailed strategies, in-depth comparisons, or core business pillars where the two main points require maximum space and attention.",
        args_schema=GenerateStrategySlideInput
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
        func=generate_horizontal_timeline_slide,
        name="generate_horizontal_timeline_slide",
        description="Generates a clean, bright, and professional horizontal timeline slide. Features a light gray gradient background, vibrant blue accents, and clean white content cards with soft shadows. The layout alternates milestones above and below a central timeline. Optimized for up to 5 key events, ideal for corporate presentations, project roadmaps, or company histories that require a clear and elegant look.",
        args_schema=GenerateHorizontalTimelineSlideInput
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
    ),

    # === SLIDE CẢM ƠN ===
    StructuredTool.from_function(
        func=generate_thank_you_slide_2,
        name="generate_thank_you_slide_2",
        description="Generates a charming 'Thank You' or Closing slide. This is an ideal slide for ending a presentation. Its unique characteristics include a notebook paper background with faint, hand-drawn school-themed doodles, a large sketchy heart icon, and a friendly, handwritten 'Thanks!' title. This tool is perfect for educational presentations, workshops, student projects, or any setting wanting a creative and approachable closing.",
        args_schema=GenerateThankYouSlide2Input
    ),
    StructuredTool.from_function(
        func=generate_thank_you_slide_3,
        name="generate_thank_you_slide_3",
        description="Generates an HTML slide for thank you page with contact information and geometric background.",
        args_schema=GenerateThankYouSlide3Input
    ),
    StructuredTool.from_function(
        func=generate_thank_you_slide,
        name="generate_thank_you_slide",
        description="Generates a vibrant and celebratory 'Thank You' slide with extra-large text and animated, floating sparkles. Features a dynamic purple-to-blue gradient background, a clean white card, and gold accents for a prominent, eye-catching effect. Perfect for making a memorable and high-impact final impression.",
        args_schema=GenerateThankYouSlideInput
    ),
    StructuredTool.from_function(
        func=generate_corporate_thank_you_slide,
        name="generate_corporate_thank_you_slide",
        description="Generates a minimalist, corporate 'Thank You' or Closing Slide. It provides a clean and professional way to end a presentation. Its unique characteristics include a simple smiley icon, a bold 'Thanks!' message, and the signature dynamic diagonal color panel with a layered shadow effect. This slide is designed for a clean, impactful, and friendly conclusion.",
        args_schema=GenerateCorporateThankYouSlideInput
    ),
]

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
