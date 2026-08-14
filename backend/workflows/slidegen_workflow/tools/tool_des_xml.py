# Auto-generated from tools.py preserving all original parameter schemas
# This conversion maintains the exact parameter definitions from the source

import json
from xml.sax.saxutils import escape

from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

from backend.workflows.slidegen_workflow.utils.rich_text import (
    apply_highlights_to_xml,
    extract_highlight_markers,
    materialize_markdown_bold_runs,
    materialize_math_fields_in_xml,
)


# Import all slide generation functions from xml_tool
from backend.workflows.slidegen_workflow.tools.xml_tool import (
    #slide intro
    generate_modern_cover_slide_xml,
    generate_it_sales_proposal_cover_inline_vector_xml_closer,
    generate_elegant_professional_cover_slide_xml,
    generate_elegant_fancy_font_cover_slide_xml,
    generate_intro_welcome_slide_xml,
    generate_memorial_cover_slide_xml,
    generate_social_topic_idea_slide_xml,
    generate_roman_empire_history_cover_slide_xml,


    #slide transition
    generate_transition_headline_slide_xml,
    generate_about_us_transition_slide_xml,
    generate_gallery_transition_slide_xml,
    generate_slide_transition_slide_xml,
    generate_green_social_media_transition_slide_xml,
    generate_section_header_image_slide_xml,


    #slide content
    generate_three_ideas_slide_xml,
    generate_content_creation_slide_xml,
    generate_ai_content_slide_xml,
    generate_two_ideas_slide_xml,
    generate_our_history_slide_xml,
    generate_instructions_slide_xml,
    generate_split_content_slide_xml,
    generate_picture_quote_slide_xml,
    generate_bullet_content_slide_xml,
    generate_client_snapshot_slide_xml,
    generate_how_forge_works_slide_xml,
    generate_implementation_timeline_slide_xml,
    generate_problem_slide_xml,
    generate_topics_overview_slide_xml,
    generate_timeline_gallery_slide_xml,
    generate_memorial_introduction_slide_xml,
    generate_legacy_of_love_slide_xml,
    generate_social_media_points_slide_xml,
    generate_numbered_social_media_points_slide_xml,
    generate_platform_instructions_slide_xml,

    #slide thank you
    generate_hanging_thank_you_slide_xml,
    generate_business_thank_you_slide_xml,
    generate_dark_gold_thank_you_slide_xml,
    generate_paper_flight_thank_you_slide_xml,
    generate_closing_thank_you_memorial_slide_xml
)

# ===========================================================================================
# PYDANTIC INPUT SCHEMAS ORDERED ACCORDING TO IMPORT SEQUENCE
# ===========================================================================================

# === SLIDE INTRO CLASSES ===
class GenerateModernCoverSlideInput(BaseModel):
    """Input schema for generate_modern_cover_slide_xml."""

    title: str = Field(..., description="Main presentation title displayed inside the dark diagonal panel on the left. example: 'THIS IS YOUR PRESENTATION TITLE'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=85&w=1600&auto=format&fit=crop", description="URL for a landscape image sized 1085 × 900 px with an approximately 1.21:1 aspect ratio.")    
    background_color: str = Field(default="#F4F4F4", description="Background color of the slide.")
    dark_panel_color: str = Field(default="#23242B", description="Color of the dark diagonal panel displayed on the left side.")
    accent_color: str = Field(default="#98F033", description="Color of the accent bar aligned with the diagonal panel boundary.")
    title_color: str = Field(default="#98F033", description="Color of the main title text.")

class GenerateItSalesProposalCoverInlineVectorCloserInput(BaseModel):
    """Input schema for generate_it_sales_proposal_cover_inline_vector_xml_closer."""

    brand_name: str = Field(..., description="Brand name displayed near the top of the slide. example: 'FORGE'")
    title: str = Field(..., description="Main proposal title displayed in the center-right content area. example: 'IT Software Sales Proposal'")
    subtitle: str = Field(..., description="Supporting subtitle displayed inside the horizontal bar. example: 'Modern productivity for secure, high-performing teams'")
    prepared_for: str = Field(..., description="Client or organization name displayed in the bottom-left footer. example: 'Value Financials'")
    date_text: str = Field(..., description="Date text displayed in the bottom-right footer. example: 'June 2035'")
    background_color: str = Field(default="#1A0B3A", description="Background color of the slide.")
    title_color: str = Field(default="#F7F2FF", description="Color of the main proposal title.")
    subtitle_color: str = Field(default="#FFFFFF", description="Color of the subtitle text.")
    subtitle_bar_color: str = Field(default="#6545A2", description="Color of the horizontal subtitle bar.")
    brand_color: str = Field(default="#F7F2FF", description="Color of the brand icon and brand name.")
    footer_color: str = Field(default="#F7F2FF", description="Color of the footer text.")

class GenerateElegantProfessionalCoverSlideInput(BaseModel):
    """Input schema for generate_elegant_professional_cover_slide_xml."""

    title: str = Field(..., description="Main presentation title displayed in the right content panel. example: 'Messi cầu thủ vĩ đại nhất thế giới'")
    subtitle: str = Field(..., description="Supporting subtitle displayed below the main title. example: 'Bài thuyết trình về Messi và những thành tích nổi bật của anh ấy.'")
    presented_by_label: str = Field(..., description="Small presenter label displayed near the bottom of the content panel. example: 'PRESENTED BY'")
    presenter_name: str = Field(..., description="Presenter name displayed below the presenter label. example: 'NAME SURNAME'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1517048676732-d65bc937f952?q=80&w=1200&auto=format&fit=crop", description="URL for a portrait image sized 650 × 716 px with an approximately 0.91:1 aspect ratio.")
    background_color: str = Field(default="#E5E5DB", description="Background color of the slide.")
    panel_color: str = Field(default="#F2F0E7", description="Color of the right content panel.")
    title_color: str = Field(default="#64625C", description="Color of the main title.")
    subtitle_color: str = Field(default="#64625C", description="Color of the subtitle.")
    meta_label_color: str = Field(default="#76746E", description="Color of the presenter label.")
    meta_name_color: str = Field(default="#55534E", description="Color of the presenter name.")
    accent_color: str = Field(default="#9FA984", description="Color of the soft corner accents.")

class GenerateElegantFancyFontCoverSlideInput(BaseModel):
    """Input schema for generate_elegant_fancy_font_cover_slide_xml."""

    title: str = Field(..., description="Main presentation title displayed below the hero image. example: 'Messi cầu thủ vĩ đại nhất thế giới'")
    subtitle: str = Field(..., description="Supporting subtitle displayed below the main title. example: 'Beauty Products Pitch Deck'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1612817288484-6f916006741a?q=85&w=1600&auto=format&fit=crop", description="URL for a wide landscape image sized 1408 × 500 px with an approximately 2.82:1 aspect ratio.")
    background_color: str = Field(default="#D7D8C8", description="Background color of the slide.")
    title_color: str = Field(default="#3F3627", description="Color of the main title.")
    subtitle_color: str = Field(default="#3F3627", description="Color of the subtitle.")

class GenerateIntroWelcomeSlideInput(BaseModel):
    """Input schema for generate_intro_welcome_slide_xml."""

    title: str = Field(..., description="Main welcome headline displayed inside the left-aligned translucent panel. Recommended maximum of 90 characters and up to 2 lines. example: 'Welcome to Our Today’s Presentation'")
    subtitle: str = Field(..., description="Supporting presentation introduction displayed below the title. Recommended maximum of 350 characters and up to 5 lines. example: 'Here you can add a brief explanation of the presentation topic.'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=85&w=1600&auto=format&fit=crop", description="URL for a landscape background image displayed at 1600 × 900 px in PowerPoint with a 16:9 aspect ratio.")
    background_overlay_color: str = Field(default="#FFFFFF", description="Color of the translucent overlay placed over the full-slide background image.")
    background_overlay_opacity: float = Field(default=0.10, description="Opacity of the full-slide background overlay, where 0 is transparent and 1 is fully opaque.")
    panel_color: str = Field(default="#FFFFFF", description="Color of the translucent rounded content panel behind the title and subtitle.")
    panel_opacity: float = Field(default=0.76, description="Opacity of the rounded content panel, where 0 is transparent and 1 is fully opaque.")
    accent_color: str = Field(default="#EA4B32", description="Color of the large rounded arrow-frame accent surrounding the content panel.")
    accent_opacity: float = Field(default=0.76, description="Opacity of the arrow-frame accent, where 0 is transparent and 1 is fully opaque.")
    company_color: str = Field(default="#2D2A2B", description="Reserved color for company or branding text; this parameter is currently not rendered by the slide layout.")
    headline_black_color: str = Field(default="#2B2929", description="Color of the main welcome headline.")
    description_color: str = Field(default="#2D2A2B", description="Color of the supporting subtitle.")

class GenerateMemorialCoverSlideInput(BaseModel):
    """Input schema for generate_memorial_cover_slide_xml."""

    title: str = Field(..., description="Main presentation title displayed inside the large centered title band. Recommended maximum of 180 characters and up to 4 lines. example: 'Welcome to Our Presentation on Memorial Day 2024 Celebration and Remembrance'")
    subtitle: str = Field(..., description="Short supporting introduction displayed inside the narrow upper band. Recommended maximum of 240 characters and up to 4 lines. example: 'A clear and engaging introduction focused on honoring and remembering those who have served.'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=85&w=1600&h=900&auto=format&fit=crop", description="URL for a landscape background image displayed at 1600 × 900 px in PowerPoint with a 16:9 aspect ratio.")
    background_color: str = Field(default="#F3F3F3", description="Fallback background color used when the background image is unavailable.")
    top_band_color: str = Field(default="#DECAC7", description="Color of the narrow band containing the supporting subtitle.")
    title_band_color: str = Field(default="#DECAC7", description="Color of the large horizontal band containing the main title.")
    subtitle_color: str = Field(default="#111111", description="Color of the supporting subtitle.")
    title_color: str = Field(default="#050505", description="Color of the centered main title.")
    stripe_blue_color: str = Field(default="#E7EEF1", description="Blue color used in the decorative vertical stripe groups.")
    stripe_pink_color: str = Field(default="#DECAC7", description="Pink color used in the decorative vertical stripe groups.")
    stripe_white_color: str = Field(default="#F8F8F8", description="White color used between the colored decorative stripes.")
    image_overlay_color: str = Field(default="#FFFFFF", description="Color of the translucent overlay placed over the full-slide background image.")

class GenerateSocialTopicIdeaSlideInput(BaseModel):
    """Input schema for generate_social_topic_idea_slide_xml."""

    title: str = Field(..., description="Main topic or idea title displayed as one editable text block in the upper-left area. example: 'Write Your Topic or Idea on Social Media'")
    subtitle: str = Field(..., description="Short supporting explanation displayed beside the horizontal line in the lower-left area. The text supports up to 2 lines. When empty, the function uses a default supporting sentence. example: 'Elaborate on the key idea you want to discuss.'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1551836022-d5d88e9218df?q=85&w=1200&auto=format&fit=crop", description="URL for a portrait image displayed at 712 × 900 px in PowerPoint with an approximately 0.79:1 aspect ratio.")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide and the left text area.")
    accent_color: str = Field(default="#6F8369", description="Color of the narrow vertical accent marker beside the title.")
    title_color: str = Field(default="#26352A", description="Color of the main topic title.")
    subtitle_color: str = Field(default="#111111", description="Color of the supporting subtitle.")
    line_color: str = Field(default="#3F3F3F", description="Color of the short horizontal line displayed before the subtitle.")

class GenerateRomanEmpireHistoryCoverSlideInput(BaseModel):
    """Input schema for generate_roman_empire_history_cover_slide_xml."""

    subtitle: str = Field(..., description="Supporting history subject label displayed in italic text above the main title. The text supports up to 2 wrapped lines. example: 'History Subject for High School'")
    title: str = Field(..., description="Large Roman Empire presentation title displayed below the subtitle in uppercase serif text. The text supports up to 2 wrapped lines. example: 'ROMAN EMPIRE'")
    image_url: str = Field(default="https://picsum.photos/seed/roman-empire-history/1600/620.jpg", description="URL for a wide landscape image displayed at 1600 × 620 px in PowerPoint with an approximately 2.58:1 aspect ratio.")
    background_color: str = Field(default="#D8B98A", description="Base parchment background color of the slide.")
    parchment_overlay_color: str = Field(default="#C49A61", description="Color used in the aged parchment texture and vignette overlay.")
    image_sepia_overlay_color: str = Field(default="#B07132", description="Color of the sepia overlay applied over the upper image.")
    torn_paper_color: str = Field(default="#F3E9D7", description="Color of the torn-paper layer covering the lower edge of the image.")
    torn_shadow_color: str = Field(default="#B89A72", description="Color of the torn-paper shadow, ornamental border, and decorative frame details.")
    subtitle_color: str = Field(default="#5A1E20", description="Color of the italic supporting subtitle.")
    title_color: str = Field(default="#4A1118", description="Color of the large Roman Empire title and ornamental details.")
    blood_color: str = Field(default="#9E1018", description="Color of the decorative red splatter accents.")

# === SLIDE TRANSITION CLASSES ===
class GenerateTransitionHeadlineSlideInput(BaseModel):
    """Input schema for generate_transition_headline_slide_xml."""

    title: str = Field(..., description="Large transition headline displayed inside the dark diagonal panel. example: 'Messi và sự nghiệp của anh ấy'")
    subtitle: str = Field(..., description="Supporting subtitle displayed below the main headline. example: 'Let’s start with the first set of slides'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=85&w=1600&auto=format&fit=crop", description="URL for a full-slide landscape image sized 1600 × 900 px with a 16:9 aspect ratio.")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    dark_panel_color: str = Field(default="#292A30", description="Color of the dark diagonal panel.")
    accent_color: str = Field(default="#98F20F", description="Color of the slanted accent bar.")
    title_color: str = Field(default="#98F20F", description="Color of the main headline.")
    subtitle_color: str = Field(default="#2ED329", description="Color of the supporting subtitle.")

class GenerateAboutUsTransitionSlideInput(BaseModel):
    """Input schema for generate_about_us_transition_slide_xml."""

    title: str = Field(..., description="Main transition title displayed at the center of the slide. example: 'Messi vô địch thế giới'")
    background_base_color: str = Field(default="#CED0C0", description="Base background color of the slide.")
    center_glow_color: str = Field(default="#9E8C70", description="Color of the central radial glow.")
    inner_glow_color: str = Field(default="#B1A180", description="Color of the inner glow layer.")
    outer_glow_color: str = Field(default="#D9D8CC", description="Color of the outer glow layer.")
    title_color: str = Field(default="#3B3227", description="Color of the centered transition title.")

class GenerateGalleryTransitionSlideInput(BaseModel):
    """Input schema for generate_gallery_transition_slide_xml."""

    title: str = Field(..., description="Main transition title displayed at the center of the slide. example: 'Messi vs Ronaldo - The Ultimate Showdown of Football Legends'")
    image_url_1: str = Field(default="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image displayed at approximately 501.33 × 230 px in PowerPoint with an approximately 2.18:1 aspect ratio.")
    image_url_2: str = Field(default="https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image displayed at approximately 501.33 × 230 px in PowerPoint with an approximately 2.18:1 aspect ratio.")
    image_url_3: str = Field(default="https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image displayed at approximately 501.33 × 230 px in PowerPoint with an approximately 2.18:1 aspect ratio.")
    image_url_4: str = Field(default="https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image displayed at approximately 501.33 × 230 px in PowerPoint with an approximately 2.18:1 aspect ratio.")
    image_url_5: str = Field(default="https://images.unsplash.com/photo-1517841905240-472988babdf9?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image displayed at approximately 501.33 × 230 px in PowerPoint with an approximately 2.18:1 aspect ratio.")
    image_url_6: str = Field(default="https://images.unsplash.com/photo-1512316609839-ce289d3eba0a?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image displayed at approximately 501.33 × 230 px in PowerPoint with an approximately 2.18:1 aspect ratio.")
    background_color: str = Field(default="#CDD0C1", description="Background color of the slide.")
    title_color: str = Field(default="#3B3024", description="Color of the centered transition title.")

class GenerateSlideTransitionSlideInput(BaseModel):
    """Input schema for generate_slide_transition_slide_xml."""

    title: str = Field(..., description="Main transition title displayed as one editable text string on the right panel. Whitespace is normalized automatically, and the title supports up to 4 wrapped lines. example: 'Social Media Sales Presentation'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?q=85&w=1200&auto=format&fit=crop", description="URL for a portrait image displayed at 430 × 652 px in PowerPoint with an approximately 0.66:1 aspect ratio.")
    right_image_url: str = Field(default="https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=85&w=1200&auto=format&fit=crop", description="URL for a nearly square landscape image displayed at 916 × 900 px in PowerPoint with an approximately 1.02:1 aspect ratio.")
    background_color: str = Field(default="#FFFFFF", description="Color of the left slide area and fallback slide background.")
    right_panel_color: str = Field(default="#6D8767", description="Color of the translucent overlay applied over the right-side image.")
    arc_color: str = Field(default="#819A7B", description="Color of the large curved decorative arc on the right panel.")
    title_color: str = Field(default="#FFFFFF", description="Color of the transition title.")
    line_color: str = Field(default="#2F3530", description="Color of the thin horizontal divider line extending behind the left portrait image.")

class GenerateGreenSocialMediaTransitionSlideInput(BaseModel):
    """Input schema for generate_green_social_media_transition_slide_xml."""

    title: str = Field(..., description="Main transition title displayed as one editable, bold, left-aligned text block on the green panel. The text supports up to 4 wrapped lines. example: 'Write Your Topic or Idea On Social Media'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=85&w=1200&auto=format&fit=crop", description="URL for a portrait image displayed at 535 × 900 px in PowerPoint with an approximately 0.59:1 aspect ratio.")
    background_color: str = Field(default="#6F8369", description="Background color of the slide and the solid left content panel.")
    right_overlay_color: str = Field(default="#6F8369", description="Color of the translucent overlay applied over the right-side image.")
    right_overlay_opacity: float = Field(default=0.58, description="Opacity of the overlay applied over the right-side image, where 0 is transparent and 1 is fully opaque.")
    title_color: str = Field(default="#FFFFFF", description="Color of the main transition title.")
    line_color: str = Field(default="#D8E0D3", description="Color of the short horizontal divider line positioned to the left of the title.")

class GenerateSectionHeaderImageSlideInput(BaseModel):
    """Input schema for generate_section_header_image_slide_xml."""

    section_header: str = Field(..., description="Section heading displayed as a bold, centered, editable text block inside the upper green panel. The text automatically wraps and reduces in size to fit a 1000 × 230 px text area. example: 'Social Media Marketing Strategy'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1556761175-b413da4baf72?q=85&w=1600&auto=format&fit=crop", description="URL for a wide landscape image displayed at 1600 × 462 px in PowerPoint with an approximately 3.46:1 aspect ratio.")
    background_color: str = Field(default="#FFFFFF", description="Fallback background color of the slide.")
    header_color: str = Field(default="#6F8369", description="Background color of the upper section-header panel.")
    title_color: str = Field(default="#FFFFFF", description="Color of the centered section heading.")
    divider_color: str = Field(default="#C9D4C3", description="Color of the short vertical divider line centered above the section heading.")

# === SLIDE CONTENT CLASSES ===

class GenerateContentCreationSlideInput(BaseModel):
    """Input schema for generate_content_creation_slide_xml."""

    main_title: str = Field(
        ...,
        description="Main slide title shown on the upper-right area. example: 'CONTENT CREATION'",
    )
    original_title: str = Field(
        ...,
        description="Heading for the first content block. example: 'Original Content'",
    )
    original_description: str = Field(
        ...,
        description="Description text for the original content block. example: 'Develop unique visuals, videos, and copy that align with your brand's message and resonate with your audience's interests. Create content that not only captures attention but also conveys the essence of your brand.'",
    )
    curated_title: str = Field(
        ...,
        description="Heading for the second content block.  example: 'Curated Content'",
    )
    curated_description: str = Field(
        ...,
        description="Description text for the curated content block. example: 'Share valuable curated content from reputable sources in your industry such as articles, videos, and graphics to enhance your original material and engage your audience in discussions.'"
    )
    main_image_url: str = Field(
        default="https://images.unsplash.com/photo-1625064757761-c9bccabf1163?auto=format&fit=crop&q=80&w=1800",
        description="URL for a landscape image sized 498 × 225 px with an approximately 2.21:1 aspect ratio.",
    )
    portrait_image_url: str = Field(
        default="https://images.unsplash.com/photo-1552113125-81af17f36b57?auto=format&fit=crop&q=80&w=1000",
        description="URL for a near-square portrait image sized 229 × 250 px with an approximately 0.92:1 aspect ratio.",
    )
    background_color: str = Field(
        default="#D2DADE",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#68767C",
        description="Color of the main title text.",
    )
    accent_color: str = Field(
        default="#E4AAA2",
        description="Accent color for the rounded rectangle behind the portrait.",
    )
    decoration_color: str = Field(
        default="#AEB9BE",
        description="Color of the decorative ellipse and bars.",
    )
    text_color: str = Field(
        default="#111111",
        description="Color of the body text and section titles.",
    )

class GenerateAiContentSlideInput(BaseModel):
    """Input schema for generate_ai_content_slide_xml."""

    title: str = Field(
        ...,
        description="Main title text displayed at the top-left of the slide. example: 'THE SLIDE TITLE GOES HERE'",
    )
    intro_text: str = Field(
        ...,
        description="Introductory paragraph displayed under the title. example: 'Do you know what helps you make your point clear? Lists like this one:'",
    )
    bullet_items: List[str] = Field(
        ...,
        description="List of bullet points displayed in the body area. example: ['They are simple', 'You can organize your ideas clearly', 'You will never forget to buy milk!']",
    )
    footer_text: str = Field(
        ...,
        description="Footer note displayed below the bullet list. example: 'You can replace the image. Just right-click on it and select \"Replace image\"'",
    )
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=85&w=1400&auto=format&fit=crop",
        description="URL for a portrait image sized 700 × 820 px with an approximately 0.85:1 aspect ratio.",
    )
    background_color: str = Field(
        default="#E3EAED",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#101010",
        description="Color of the main title text.",
    )
    text_color: str = Field(
        default="#1B1B1B",
        description="Color of the intro, bullet, and footer text.",
    )

class GenerateTwoIdeasSlideInput(BaseModel):
    """Input schema for generate_two_ideas_slide_xml."""

    title: str = Field(
        ...,
        description="Main title text displayed in the content area. example: 'TWO IDEAS'",
    )
    idea_titles: List[str] = Field(
        ...,
        description="List of idea headings. Must have the same length as idea_descriptions. example: ['Venus', 'Mercury']",
    )
    idea_descriptions: List[str] = Field(
        ...,
        description="List of supporting descriptions for each idea title. example: ['Venus is the second planet from the Sun.', 'Mercury is the closest planet to the Sun.']",
    )
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1529139574466-a303027c1d8b?q=85&w=1200&auto=format&fit=crop",
        description="URL for a portrait image sized 520 × 900 px with an approximately 0.58:1 aspect ratio.",
    )
    background_color: str = Field(
        default="#1A1A1A",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#FFFFFF",
        description="Color of the main title text.",
    )
    heading_color: str = Field(
        default="#FFFFFF",
        description="Color of each idea heading.",
    )
    body_color: str = Field(
        default="#F1F1F1",
        description="Color of each idea description.",
    )

class GenerateThreeIdeasSlideInput(BaseModel):
    """Input schema for generate_three_ideas_slide_xml."""
    title: str = Field(
        ...,
        description="Main title text displayed at the top of the slide. example: 'THREE IDEAS' ",
    )
    idea_titles: List[str] = Field(
        ... ,
        description="List of idea headings. Must have the same length as idea_descriptions. example: ['Mercury', 'Mars', 'Venus']",
    )
    idea_descriptions: List[str] = Field(
        ...,
        description="List of supporting descriptions for each idea title. example: ['Mercury is the closest planet to the Sun.', 'Mars is known as the Red Planet.', 'Venus has a thick, toxic atmosphere.']",
    )
    image_url: str = Field(
        default="https://images.unsplash.com/photo-1594035910387-fea47794261f?q=85&w=1200&auto=format&fit=crop",
        description="URL for a portrait image sized 535 × 900 px with an approximately 0.59:1 aspect ratio.",
    )
    background_color: str = Field(
        default="#181818",
        description="Background color of the slide.",
    )
    title_color: str = Field(
        default="#FFFFFF",
        description="Color of the main title text.",
    )
    heading_color: str = Field(
        default="#FFFFFF",
        description="Color of each idea heading.",
    )
    body_color: str = Field(
        default="#F2F2F2",
        description="Color of each idea description.",
    )

class GenerateOurHistorySlideInput(BaseModel):
    """Input schema for generate_our_history_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top of the content area. example: 'OUR HISTORY'")
    event_titles: List[str] = Field(..., description="List of event headings displayed in vertically stacked history sections. Must have the same length as event_descriptions and event_years. example: ['SATURN', 'MARS', 'NEPTUNE']")
    event_descriptions: List[str] = Field(..., description="List of supporting descriptions for each history event. Must have the same length as event_titles and event_years. example: ['Saturn is composed of hydrogen and helium.', 'Despite being red, Mars is actually a cold place.', 'Neptune is the farthest planet from the Sun.']")
    event_years: List[str] = Field(..., description="List of year or timeline labels displayed beside each history event. Must have the same length as event_titles and event_descriptions. example: ['1998', '2005', '2024']")
    image_url: str = Field(default="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=85&w=1200&auto=format&fit=crop", description="URL for a portrait image sized 445 × 900 px with an approximately 1:2 aspect ratio.")    
    background_color: str = Field(default="#151515", description="Background color of the slide.")
    title_color: str = Field(default="#FFFFFF", description="Color of the main title text.")
    heading_color: str = Field(default="#FFFFFF", description="Color of each event heading.")
    body_color: str = Field(default="#F2F2F2", description="Color of each event description.")
    year_color: str = Field(default="#FFFFFF", description="Color of each year or timeline label.")
    line_color: str = Field(default="#E8E8E8", description="Color of the vertical timeline separator lines.")

class GenerateInstructionsSlideInput(BaseModel):
    """Input schema for generate_instructions_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top-left of the dark content panel. example: 'INSTRUCTIONS FOR USE'")
    left_heading: str = Field(..., description="Heading for the left instruction column. example: 'EDIT IN GOOGLE SLIDES'")
    left_paragraphs: List[str] = Field(..., description="List of instructional paragraphs displayed under the left heading. example: ['Click on the button under the presentation preview that says “Use as Google Slides Theme”.', 'You will get a copy of this document on your Google Drive and will be able to edit, add or delete slides.', 'You have to be signed in to your Google account.']")
    right_heading: str = Field(..., description="Heading for the right instruction column. example: 'EDIT IN POWERPOINT®'")
    right_paragraphs: List[str] = Field(..., description="List of instructional paragraphs displayed under the right heading. example: ['Click on the button under the presentation preview that says “Download as PowerPoint template”. You will get a .pptx file that you can edit in PowerPoint.', 'Remember to download and install the fonts used in this presentation.']")
    footer_text: str = Field(..., description="Information or licensing text displayed near the bottom-left of the slide. example: 'More info on how to use this template at slidescarnival.com/help-use-presentation-template'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?q=85&w=1600&auto=format&fit=crop", description="URL for a near-square portrait image sized 840 × 900 px with an approximately 0.93:1 aspect ratio.")    
    background_color: str = Field(default="#F3F4F7", description="Background color of the slide.")
    dark_panel_color: str = Field(default="#34343B", description="Color of the dark diagonal content panel on the left side.")
    accent_color: str = Field(default="#98F20F", description="Color of the slanted accent bar aligned with the diagonal panel boundary.")
    title_color: str = Field(default="#98F20F", description="Color of the main title text.")
    heading_color: str = Field(default="#FFFFFF", description="Color of the left and right column headings.")
    body_color: str = Field(default="#FFFFFF", description="Color of the instructional paragraph text.")
    footer_color: str = Field(default="#39C62F", description="Color of the footer information text.")

class GenerateSplitContentSlideInput(BaseModel):
    """Input schema for generate_split_content_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top-left of the dark diagonal content panel. example: 'YOU CAN ALSO SPLIT YOUR CONTENT'")
    column_titles: List[str] = Field(..., description="List of column headings displayed below the main title. Must have the same length as column_descriptions. example: ['White', 'Black']")
    column_descriptions: List[str] = Field(..., description="List of supporting descriptions for each column heading. Must have the same length as column_titles. example: ['White is the color of milk and fresh snow.', 'Black is the color of ebony and outer space.']")
    image_url: str = Field(default="https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=85&w=1600&auto=format&fit=crop", description="URL for a full-slide landscape image rendered at 1600 × 900 px with a 16:9 aspect ratio. The image covers the entire slide, while a dark diagonal panel overlays most of the left side. Use a wide, high-resolution image with the main subject positioned toward the right side so it remains visible and is not obscured by the content panel.")    
    background_color: str = Field(default="#F3F4F7", description="Background color of the slide.")
    dark_panel_color: str = Field(default="#34343B", description="Color of the dark diagonal content panel covering the left side.")
    accent_color: str = Field(default="#98F20F", description="Color of the bright slanted accent bar aligned with the diagonal boundary.")
    title_color: str = Field(default="#98F20F", description="Color of the main slide title.")
    heading_color: str = Field(default="#FFFFFF", description="Color of the column headings.")
    body_color: str = Field(default="#FFFFFF", description="Color of the column description text.")

class GeneratePictureQuoteSlideInput(BaseModel):
    """Input schema for generate_picture_quote_slide_xml."""

    title: str = Field(..., description="Main slide title displayed in the right content panel. example: 'A PICTURE IS WORTH THOUSAND WORDS'")
    content: str = Field(..., description="Supporting text displayed below the title. example: 'A complex idea can be conveyed with just a single still image.'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1521737711867-e3b97375f902?q=85&w=1600&auto=format&fit=crop", description="URL for a landscape image sized 1010 × 900 px with an approximately 1.12:1 aspect ratio.")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide and right content panel.")
    accent_color: str = Field(default="#98F20F", description="Color of the slanted accent bar.")
    title_color: str = Field(default="#7CCF1A", description="Color of the main title text.")
    body_color: str = Field(default="#858392", description="Color of the supporting text.")

class GenerateBulletContentSlideInput(BaseModel):
    """Input schema for generate_bullet_content_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top-left of the dark diagonal panel. example: 'THIS IS A SLIDE TITLE'")
    bullet_items: List[str] = Field(..., description="List of plain bullet-point contents displayed below the title. IMPORTANT: send only the text for each item; do not prefix items with •, -, *, 1., 1), or any other numbering because the renderer adds exactly one bullet marker. example: ['Here you have a list of items', 'And some text', 'But remember not to overload your slides with content']")
    closing_text: str = Field(..., description="Supporting text displayed below the bullet list. example: 'Your audience will listen to you or read the content, but won’t do both.'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1499750310107-5fef28a66643?q=85&w=1600&auto=format&fit=crop", description="URL for a full-slide landscape image sized 1600 × 900 px with a 16:9 aspect ratio.")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    dark_panel_color: str = Field(default="#2D2E34", description="Color of the dark diagonal panel.")
    accent_color: str = Field(default="#98F20F", description="Color of the slanted accent bar.")
    title_color: str = Field(default="#98F20F", description="Color of the main title.")
    bullet_color: str = Field(default="#98F20F", description="Color of the bullet markers.")
    body_color: str = Field(default="#FFFFFF", description="Color of the bullet and closing text.")

class GenerateClientSnapshotSlideInput(BaseModel):
    """Input schema for generate_client_snapshot_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top-left. example: 'Client snapshot'")
    subtitle: str = Field(..., description="Supporting subtitle displayed below the main title. example: 'About Value Financials'")
    client_details: List[str] = Field(..., description="List of plain client information and goals displayed as structured bullet points. IMPORTANT: each item must contain content only, without •, -, *, 1., 1), or other numbering; the renderer adds one marker. Use 'Label: value' for a main detail. For a nested goal, use two leading spaces but still no bullet or number. example: ['Industry: Financial services and banking', 'Team size: 300+ employees', 'Primary goals:', '  Improve cross-team collaboration']")
    top_image_url: str = Field(default="https://images.unsplash.com/photo-1552664730-d307ca884978?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image sized 715 × 410 px with an approximately 1.74:1 aspect ratio.")
    bottom_image_url: str = Field(default="https://images.unsplash.com/photo-1556761175-b413da4baf72?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image sized 715 × 410 px with an approximately 1.74:1 aspect ratio.")
    background_color: str = Field(default="#1A0B3A", description="Background color of the slide.")
    title_color: str = Field(default="#A678FF", description="Color of the main title.")
    subtitle_color: str = Field(default="#F7F2FF", description="Color of the subtitle.")
    body_color: str = Field(default="#F7F2FF", description="Color of the client details text.")

class GenerateHowForgeWorksSlideInput(BaseModel):
    """Input schema for generate_how_forge_works_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top-left. example: 'How Forge works'")
    subtitle: str = Field(..., description="Supporting subtitle displayed below the main title. example: 'From setup to daily use, Forge fits into how your team operates.'")
    steps: List[Dict[str, str]] = Field(..., description="List of process steps displayed as vertically connected cards. Each item must contain a 'step' label and a 'content' description. example: [{'step': 'Step 1', 'content': 'Connect teams, files, and existing systems'}, {'step': 'Step 2', 'content': 'Configure shared workspaces and approval workflows'}]")
    background_color: str = Field(default="#1A0B3A", description="Background color of the slide.")
    title_color: str = Field(default="#A678FF", description="Color of the main title.")
    subtitle_color: str = Field(default="#F7F2FF", description="Color of the subtitle.")
    step_label_color: str = Field(default="#FFFFFF", description="Color of the step labels.")
    step_body_color: str = Field(default="#F7F2FF", description="Color of the step descriptions.")
    arrow_color: str = Field(default="#FFFFFF", description="Color of the arrows connecting the step cards.")

class GenerateImplementationTimelineSlideInput(BaseModel):
    """Input schema for generate_implementation_timeline_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top-left. example: 'Implementation timeline'")
    subtitle: str = Field(..., description="Supporting subtitle displayed below the main title. example: 'Forge offers a structured rollout designed for minimal disruption'")
    timeline_items: List[Dict[str, str]] = Field(..., description="List of timeline milestones displayed across a horizontal timeline. Each item must contain a 'label' and a 'content' field. example: [{'label': 'Week 1', 'content': 'Kickoff and workspace setup'}, {'label': 'Week 2', 'content': 'Workflow configuration and security policies'}]")
    background_color: str = Field(default="#1A0B3A", description="Background color of the slide.")
    title_color: str = Field(default="#A678FF", description="Color of the main title.")
    subtitle_color: str = Field(default="#F7F2FF", description="Color of the subtitle.")
    timeline_color: str = Field(default="#A678FF", description="Color of the timeline line and milestone circles.")
    label_color: str = Field(default="#F7F2FF", description="Color of the milestone labels.")
    content_color: str = Field(default="#F7F2FF", description="Color of the milestone descriptions.")

class GenerateProblemSlideInput(BaseModel):
    """Input schema for generate_problem_slide_xml."""

    title: str = Field(..., description="Main problem statement title displayed in the lower-left area. example: 'The problem'")
    description: str = Field(..., description="Supporting description displayed below the main title. example: 'Keeping commercial spaces clean sounds simple—but many businesses struggle with:'")
    problem_items: List[str] = Field(..., description="List of problem statements displayed inside large rounded cards. Supports up to five items. example: ['Missed cleaning tasks', 'Different cleaners every visit', 'Spaces that don’t stay clean for long']")
    card_colors: List[str] = Field(default=["#DDF2A6", "#9ED98C", "#00580A", "#7BC96F", "#4FA95C"], description="List of background colors applied cyclically to the problem cards.")
    card_text_colors: List[str] = Field(default=["#07520B", "#07520B", "#FFFFFF", "#07520B", "#FFFFFF"], description="List of text colors applied cyclically to the problem cards.")
    background_color: str = Field(default="#F7F7F2", description="Background color of the slide.")
    title_color: str = Field(default="#07520B", description="Color of the main title.")
    description_color: str = Field(default="#07520B", description="Color of the supporting description.")

class GenerateTopicsOverviewSlideInput(BaseModel):
    """Input schema for generate_topics_overview_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top-left. example: 'Messi là cầu thủ vĩ đại nhất thế giới'")
    topics: List[Dict[str, str]] = Field(..., min_length=1, max_length=3, description="List of topic items displayed in a grid. Supports a maximum of 3 items. Each item must contain 'title' and 'description'. example: [{'title': 'ADD A MAIN POINT', 'description': 'Briefly elaborate on what you want to discuss.'}]")
    image_url_1: str = Field(default="https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image sized approximately 480 × 254 px with an approximately 1.89:1 aspect ratio.")
    image_url_2: str = Field(default="https://images.unsplash.com/photo-1556228720-195a672e8a03?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image sized approximately 480 × 254 px with an approximately 1.89:1 aspect ratio.")
    image_url_3: str = Field(default="https://images.unsplash.com/photo-1596462502278-27bfdc403348?q=85&w=1200&auto=format&fit=crop", description="URL for a landscape image sized approximately 480 × 254 px with an approximately 1.89:1 aspect ratio.")
    background_color: str = Field(default="#CDD0C1", description="Background color of the slide.")
    title_color: str = Field(default="#3A3126", description="Color of the main title.")
    item_title_color: str = Field(default="#3A3126", description="Color of the topic titles.")
    item_description_color: str = Field(default="#3A3126", description="Color of the topic descriptions.")
    accent_color: str = Field(default="#9AA382", description="Color of the soft corner accents.")

class GenerateTimelineGallerySlideInput(BaseModel):
    """Input schema for generate_timeline_gallery_slide_xml."""

    title: str = Field(..., description="Main slide title displayed at the top-center. example: 'Company Development Timeline'")
    timeline_items: List[Dict[str, str]] = Field(..., min_length=1, max_length=6, description="List of 1 to 6 timeline milestones arranged alternately above and below a horizontal timeline. Each item must contain exactly three fields: 'title' is the short milestone heading displayed in uppercase; 'description' is the supporting explanation displayed below the milestone heading; and 'image_url' is the URL of the landscape image associated with that milestone. The image is displayed in PowerPoint at 320 × 217.6 px for 1 item, 310 × 210.8 px for 2–4 items, 250 × 170 px for 5 items, or 220 × 149.6 px for 6 items, with an approximately 1.47:1 aspect ratio. example: [{'title': 'PRODUCT LAUNCH', 'description': 'Introduce the first product version to selected customers.', 'image_url': 'https://example.com/product-launch.jpg'}]")
    background_color: str = Field(default="#CDD0C1", description="Background color of the slide.")
    title_color: str = Field(default="#3B3024", description="Color of the main slide title.")
    text_color: str = Field(default="#3B3024", description="Color of the timeline item titles and descriptions.")
    timeline_color: str = Field(default="#9B8B6C", description="Color of the horizontal timeline and milestone dots.")
    accent_color: str = Field(default="#B7B199", description="Color of the soft decorative corner accents.")

class GenerateMemorialIntroductionSlideInput(BaseModel):
    """Input schema for generate_memorial_introduction_slide_xml."""

    section_title: str = Field(..., description="Short section label displayed at the top-center of the right panel. Recommended maximum of 80 characters and up to 2 lines. example: 'Introduction'")
    main_title: str = Field(..., description="Large italic memorial heading displayed below the section label. Recommended maximum of 180 characters and up to 4 lines. example: 'Honoring the Life and Legacy of Name'")
    body_text: str = Field(..., description="Supporting memorial paragraph displayed below the main title. Recommended maximum of 700 characters and up to 10 lines. example: 'Today, we gather to celebrate the life of [Name] and reflect on the memories shared together.'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=85&w=1200&auto=format&fit=crop", description="URL for a portrait image displayed at 620 × 736 px in PowerPoint with an approximately 0.84:1 aspect ratio.")
    background_color: str = Field(default="#DDEEF2", description="Background color surrounding the image and right content panel.")
    panel_color: str = Field(default="#E5CAC3", description="Background color of the right text panel.")
    frame_color: str = Field(default="#F1F7F8", description="Color of the two vertical decorative frame stripes inside the right panel.")
    section_title_color: str = Field(default="#111111", description="Color of the section label.")
    main_title_color: str = Field(default="#050505", description="Color of the large italic memorial title.")
    body_text_color: str = Field(default="#111111", description="Color of the supporting body paragraph.")

class GenerateLegacyOfLoveSlideInput(BaseModel):
    """Input schema for generate_legacy_of_love_slide_xml."""

    title: str = Field(..., description="Main memorial title displayed inside the centered upper framed panel. The title is rendered in italic text and supports up to 2 lines. example: 'A Legacy of Love and Kindness'")
    left_text: str = Field(..., description="First memorial paragraph displayed in the left column of the lower framed panel. The text supports up to 12 lines. example: 'Though [Name] may no longer be with us, their legacy of love and kindness lives on.'")
    right_text: str = Field(..., description="Second memorial paragraph displayed in the right column of the lower framed panel. The text supports up to 12 lines. example: 'Let us honor their memory by embracing the values they held dear.'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=85&w=1600&auto=format&fit=crop&sat=-100", description="URL for a landscape background image displayed at 1600 × 900 px in PowerPoint with a 16:9 aspect ratio.")
    background_color: str = Field(default="#F1F1F1", description="Fallback background color used when the background image is unavailable.")
    panel_color: str = Field(default="#E5CAC3", description="Color of the upper title panel and lower two-column content panel.")
    border_color: str = Field(default="#DDEEF2", description="Color of the outer frames surrounding the title and content panels.")
    title_color: str = Field(default="#050505", description="Color of the italic memorial title.")
    body_color: str = Field(default="#111111", description="Color of the text in both memorial content columns.")
    image_overlay_color: str = Field(default="#FFFFFF", description="Color of the translucent overlay placed over the full-slide background image.")
    image_overlay_opacity: float = Field(default=0.12, description="Opacity of the full-slide image overlay, where 0 is transparent and 1 is fully opaque.")

class GenerateSocialMediaPointsSlideInput(BaseModel):
    """Input schema for generate_social_media_points_slide_xml."""

    title: str = Field(..., description="Main slide headline displayed as one centered editable text block above the cards. The title supports up to 2 wrapped lines. example: 'Key Social Media Strategies'")
    cards: list[dict[str, str]] = Field(..., min_length=1, max_length=3, description="List of 1 to 3 content cards displayed in a horizontal row. Each card must contain two fields: 'title' is the bold main point displayed below the colored header and supports up to 2 wrapped lines; 'description' is the supporting explanation displayed below the card title. The function processes only the first 3 items. Cards with both fields empty are ignored, while a missing title or description is replaced with fallback text. example: [{'title': 'BUILD A CONSISTENT BRAND', 'description': 'Use consistent visuals and messaging across every social media platform.'}]")
    background_color: str = Field(default="#FFFFFF", description="Background color of the slide.")
    accent_color: str = Field(default="#6F8369", description="Color of the header area at the top of each content card.")
    card_color: str = Field(default="#E9EDE9", description="Background color of the main body area of each content card.")
    title_color: str = Field(default="#000000", description="Color of the main slide headline.")
    card_title_color: str = Field(default="#000000", description="Color of the bold title inside each content card.")
    card_body_color: str = Field(default="#000000", description="Color of the supporting description inside each content card.")
    star_color: str = Field(default="#FFFFFF", description="Color of the star icon displayed inside each card header.")
    divider_color: str = Field(default="#7C7C7C", description="Color of the short vertical divider line positioned above the main slide headline.")

class GenerateNumberedSocialMediaPointsSlideInput(BaseModel):
    """Input schema for generate_numbered_social_media_points_slide_xml."""

    title: str = Field(..., description="Main slide title displayed as one centered editable text block above the content panel. The text automatically wraps and reduces in size to fit a 1400 × 128 px text area. example: 'Key Social Media Strategies'")
    items: list[dict[str, str]] = Field(..., description="List of one or more numbered content items arranged in a responsive grid with up to 3 columns and additional rows when needed. Each item must contain two fields: 'title' is the bold main point displayed beside its automatically generated two-digit number and supports up to 3 wrapped lines; 'description' is the supporting explanation displayed below the item title and automatically wraps to fit the remaining cell height. Item numbers such as '01', '02', and '03' are generated from the list order and must not be included in the input. example: [{'title': 'BUILD A CONSISTENT BRAND', 'description': 'Use consistent visuals and messaging across every social media platform.'}]")
    background_color: str = Field(default="#FFFFFF", description="Background color of the upper title area.")
    content_background_color: str = Field(default="#F0F3F0", description="Background color of the lower numbered-content panel.")
    accent_color: str = Field(default="#6F8369", description="Color of the automatically generated item numbers.")
    title_color: str = Field(default="#000000", description="Color of the main slide title.")
    item_title_color: str = Field(default="#000000", description="Color of each bold item title.")
    item_body_color: str = Field(default="#000000", description="Color of each supporting item description.")
    divider_color: str = Field(default="#777777", description="Color of the short vertical divider line centered above the main title.")

class GeneratePlatformInstructionsSlideInput(BaseModel):
    """Input schema for generate_platform_instructions_slide_xml."""

    items: list[dict[str, str]] = Field(..., description="List of platform instruction items arranged in a responsive layout with up to 3 columns and additional rows when needed. Each item contains four string fields: 'title' is the bold platform heading displayed above the icon and supports up to 2 wrapped lines; 'subtitle' is the centered instructional text displayed below the icon; 'icon' selects the icon design and supports 'team', 'idea', 'target', and 'download', while any other string renders a star icon; and 'accent_color' is the hexadecimal color used for the short accent line and organic icon background. Blank or missing values are replaced with fallback content by the function. example: [{'title': 'GOOGLE SLIDES', 'subtitle': 'Click the Google Slides button and make a copy of the presentation.', 'icon': 'team', 'accent_color': '#F04425'}]")
    background_color: str = Field(default="#F4F2EF", description="Background color of the slide.")
    text_color: str = Field(default="#050505", description="Color of each platform title.")
    line_color: str = Field(default="#050505", description="Color of the instructional text and the fallback accent color used when an item does not provide an accent_color.")

# === SLIDE Thank you ===
class GenerateHangingThankYouSlideInput(BaseModel):
    """Input schema for generate_hanging_thank_you_slide_xml."""

    title: str = Field(..., description="Main thank-you title formed by individual hanging letter cards. Supports a maximum of 14 visible characters, excluding spaces. example: 'THANK YOU'")
    subtitle: str = Field(..., description="Supporting message displayed below the hanging title cards. example: 'Thank you for your time and attention.'")
    background_top_left: str = Field(default="#F73556", description="Color used in the top-left area of the background gradient.")
    background_top_right: str = Field(default="#AC2D5F", description="Color used in the top-right area of the background gradient.")
    background_bottom_left: str = Field(default="#B92E60", description="Color used in the bottom-left area of the background gradient.")
    background_bottom_right: str = Field(default="#123064", description="Color used in the bottom-right area of the background gradient.")
    card_color_1: str = Field(default="#FF755E", description="Starting color of the gradient applied to each hanging letter card.")
    card_color_2: str = Field(default="#FFA31F", description="Ending color of the gradient applied to each hanging letter card.")
    card_text_color: str = Field(default="#FFFFFF", description="Color of the letters displayed inside the hanging cards.")
    string_color: str = Field(default="#111111", description="Color of the strings and connectors holding the letter cards.")
    subtitle_color: str = Field(default="#FFF4E6", description="Color of the supporting subtitle.")

class GenerateBusinessThankYouSlideInput(BaseModel):
    """Input schema for generate_business_thank_you_slide_xml."""

    title: str = Field(..., description="Main thank-you headline displayed over the hero image. Supports a maximum of 50 characters and up to 2 lines. example: 'Thank you'")
    description: str = Field(..., description="Supporting closing message displayed in the centered white panel below the hero image. The text can use up to 4 lines. example: 'Thank you for your time and attention. We look forward to working with you.'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1521791136064-7986c2920216?q=85&w=1600&auto=format&fit=crop", description="URL for a wide landscape image displayed at 1600 × 542 px in PowerPoint with an approximately 2.95:1 aspect ratio.")
    background_color: str = Field(default="#111111", description="Fallback background color of the slide.")
    overlay_color: str = Field(default="#000000", description="Color of the dark transparent overlay placed over the hero image.")
    title_color: str = Field(default="#FFFFFF", description="Color of the thank-you headline.")
    description_color: str = Field(default="#111111", description="Color of the supporting description.")
    accent_color: str = Field(default="#00D6D9", description="Color of the geometric outline decoration in the hero area.")
    footer_bar_color: str = Field(default="#1697AA", description="Color of the narrow footer bar at the bottom of the slide.")
    white_panel_color: str = Field(default="#FFFFFF", description="Background color of the description panel.")

class GenerateDarkGoldThankYouSlideInput(BaseModel):
    """Input schema for generate_dark_gold_thank_you_slide_xml."""

    title: str = Field(..., description="Main thank-you headline displayed in one centered line inside the dark panel. Recommended maximum of 40 characters. example: 'THANK YOU'")
    subtitle: str = Field(..., description="Supporting closing message displayed below the title. Recommended maximum of 180 characters and up to 2 lines. example: 'Thank you for your time and attention. We look forward to working with you.'")
    phone_text: str = Field(..., description="Phone number displayed beside the phone icon in one line. example: '(123) 456-7890'")
    email_text: str = Field(..., description="Email address displayed beside the email icon in one line. example: 'david.langford@email.com'")
    website_text: str = Field(..., description="Website address displayed beside the website icon in one line. example: 'davidlangford.com'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=85&w=1600&auto=format&fit=crop", description="URL for a landscape background image displayed at 1600 × 900 px in PowerPoint with a 16:9 aspect ratio.")
    background_color: str = Field(default="#050505", description="Fallback background color of the slide.")
    panel_color: str = Field(default="#000000", description="Background color of the centered content panel.")
    title_color: str = Field(default="#F0B400", description="Color of the main thank-you headline.")
    subtitle_color: str = Field(default="#FFFFFF", description="Color of the supporting subtitle.")
    contact_color: str = Field(default="#F0B400", description="Color of the contact text and contact icons.")
    divider_color: str = Field(default="#A37A10", description="Color of the horizontal divider line above the contact information.")
    accent_color: str = Field(default="#7A6107", description="Color of the decorative corner accents.")

class GeneratePaperFlightThankYouSlideInput(BaseModel):
    """Input schema for generate_paper_flight_thank_you_slide_xml."""

    title: str = Field(..., description="Main thank-you message displayed near the bottom-center of the slide. Recommended maximum of 40 characters and up to 2 lines. example: 'Cảm ơn mọi người đã lắng nghe'")
    background_color: str = Field(default="#F6F6F7", description="Background color of the slide.")
    title_color: str = Field(default="#6A7193", description="Color of the main thank-you title and decorative underline segments.")
    cloud_color: str = Field(default="#E9EBF4", description="Primary color of the illustrated clouds.")
    cloud_shadow_color: str = Field(default="#C9CCDD", description="Color of the darker cloud shadow elements.")
    mountain_color: str = Field(default="#E1E1E1", description="Primary color of the large mountain illustration.")
    mountain_dark_color: str = Field(default="#D2D2D2", description="Color of the darker foreground mountain illustration.")
    path_color: str = Field(default="#BCC0CF", description="Color of the dashed flight paths.")
    orange_color: str = Field(default="#F2A212", description="Primary orange color used for decorative dots and envelope gradients.")
    envelope_color: str = Field(default="#F5B13C", description="Primary color of the envelope illustrations.")
    envelope_shadow_color: str = Field(default="#D08407", description="Color of the envelope outlines, folds, and shadows.")
    paper_plane_color: str = Field(default="#D4D6DB", description="Primary light color of the paper plane illustration.")
    paper_plane_dark_color: str = Field(default="#9FA2AA", description="Darker color used for the folded sections of the paper plane.")
    star_color: str = Field(default="#C4C7D1", description="Color of the decorative star illustrations.")

class GenerateClosingThankYouMemorialSlideInput(BaseModel):
    """Input schema for generate_closing_thank_you_memorial_slide_xml."""

    closing_statement: str = Field(default="Write your closing statement", description="Short closing statement displayed inside the upper horizontal band. The text supports up to 2 lines. example: 'In loving memory of a life that touched us all.'")
    title: str = Field(default="Cảm ơn quí vị đã lắng nghe", description="Large italic thank-you title displayed inside the central blue band. The text supports up to 3 lines. example: 'Cảm ơn quý vị đã lắng nghe'")
    subtitle: str = Field(default="Briefly elaborate on what you want to discuss. Briefly elaborate on what you want to discuss. Briefly elaborate on what you want to discuss.", description="Supporting closing message displayed inside the lower horizontal band. The text supports up to 2 lines. example: 'Thank you for joining us in honoring and remembering this meaningful legacy.'")
    image_url: str = Field(default="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=85&w=1600&auto=format&fit=crop", description="URL for a landscape image displayed at 1540 × 840 px in PowerPoint with an approximately 1.83:1 aspect ratio.")
    background_color: str = Field(default="#DDEEF2", description="Color of the outer slide background surrounding the centered image.")
    top_band_color: str = Field(default="#E5CAC3", description="Background color of the upper closing-statement band.")
    title_band_color: str = Field(default="#DDEEF2", description="Background color of the central title band.")
    bottom_band_color: str = Field(default="#E5CAC3", description="Background color of the lower subtitle band.")
    closing_statement_color: str = Field(default="#111111", description="Color of the closing statement.")
    title_color: str = Field(default="#050505", description="Color of the large italic thank-you title.")
    subtitle_color: str = Field(default="#111111", description="Color of the supporting subtitle.")
    image_overlay_color: str = Field(default="#FFFFFF", description="Color of the translucent overlay placed over the grayscale background image.")

INTRO_TOOLS = [

    StructuredTool.from_function(
    func=generate_modern_cover_slide_xml,
    name="generate_modern_cover_slide_xml",
    description="Generates a modern intro slide with a large image on the right, a dark diagonal panel on the left, a bright accent bar aligned with the diagonal boundary, and a large presentation title inside the dark panel. Ideal for presentation covers, opening slides, project introductions, business proposals, portfolios, and modern corporate presentations.",
    args_schema=GenerateModernCoverSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_it_sales_proposal_cover_inline_vector_xml_closer,
    name="generate_it_sales_proposal_cover_inline_vector_xml_closer",
    description="Generates a premium software sales proposal cover slide with an inline vector ribbon decoration, a brand mark, a large proposal title, a horizontal subtitle bar, client information, and a date footer. Ideal for IT proposals, software sales presentations, business offers, and technology pitch decks.",
    args_schema=GenerateItSalesProposalCoverInlineVectorCloserInput,
    ),
    StructuredTool.from_function(
    func=generate_elegant_professional_cover_slide_xml,
    name="generate_elegant_professional_cover_slide_xml",
    description="Generates an elegant editorial cover slide with a large portrait image on the left, a light content panel on the right, a centered title and subtitle, presenter information, and soft decorative corner accents. Ideal for professional presentations, portfolios, personal introductions, editorial covers, and formal project decks.",
    args_schema=GenerateElegantProfessionalCoverSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_elegant_fancy_font_cover_slide_xml,
    name="generate_elegant_fancy_font_cover_slide_xml",
    description="Generates a minimalist editorial cover slide with a wide hero image near the top, a large elegant serif title below it, and a smaller supporting subtitle aligned to the same left edge. Ideal for beauty presentations, fashion decks, luxury products, editorial portfolios, and premium brand introductions.",
    args_schema=GenerateElegantFancyFontCoverSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_intro_welcome_slide_xml,
    name="generate_intro_welcome_slide_xml",
    description="Generates a modern welcome slide with a full-slide 16:9 background image, a translucent white content panel, a bold orange arrow-frame accent, a title of up to approximately 90 characters, and a supporting subtitle of up to approximately 350 characters.",
    args_schema=GenerateIntroWelcomeSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_memorial_cover_slide_xml,
    name="generate_memorial_cover_slide_xml",
    description="Generates an editorial memorial-style cover slide with a full-slide 16:9 landscape image, a narrow subtitle band, a large centered title band, and decorative vertical stripe groups. Ideal for commemorative presentations, historical topics, ceremonies, remembrance events, and formal introductions.",
    args_schema=GenerateMemorialCoverSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_social_topic_idea_slide_xml,
    name="generate_social_topic_idea_slide_xml",
    description="Generates a clean social media topic slide with a large editable title and supporting subtitle on the left, a vertical accent marker, a short horizontal divider, and a full-height portrait image on the right.",
    args_schema=GenerateSocialTopicIdeaSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_roman_empire_history_cover_slide_xml,
    name="generate_roman_empire_history_cover_slide_xml",
    description="Generates a Roman Empire history cover slide with a wide upper image, sepia treatment, aged parchment texture, a torn-paper transition, decorative Roman-style framing, red splatter accents, an italic subtitle, and a large serif title.",
    args_schema=GenerateRomanEmpireHistoryCoverSlideInput,
    ),
]
TRANSITION_TOOLS = [
    StructuredTool.from_function(
    func=generate_transition_headline_slide_xml,
    name="generate_transition_headline_slide_xml",
    description="Generates a transition slide with a full-slide image, a dark diagonal panel on the left, a bright slanted accent bar, a large headline, and a supporting subtitle. Ideal for section introductions, chapter transitions, topic dividers, and presentation milestones.",
    args_schema=GenerateTransitionHeadlineSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_about_us_transition_slide_xml,
    name="generate_about_us_transition_slide_xml",
    description="Generates a minimalist transition slide with a muted background, a soft layered radial glow, and one large centered serif title. Ideal for section dividers, chapter introductions, topic transitions, about-us sections, and presentation milestones.",
    args_schema=GenerateAboutUsTransitionSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_gallery_transition_slide_xml,
    name="generate_gallery_transition_slide_xml",
    description="Generates a gallery transition slide with three landscape images across the top, three landscape images across the bottom, and one large centered title in the open middle area. Ideal for visual section dividers, comparisons, portfolios, galleries, showcases, and presentation transitions.",
    args_schema=GenerateGalleryTransitionSlideInput,
    ),
    StructuredTool.from_function(
        func=generate_slide_transition_slide_xml,
        name="generate_slide_transition_slide_xml",
        description="Generates a modern split transition slide with a portrait image on the left, a thin horizontal divider, and an image-backed green panel on the right containing a curved arc decoration and one editable title supporting up to 4 wrapped lines.",
        args_schema=GenerateSlideTransitionSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_green_social_media_transition_slide_xml,
    name="generate_green_social_media_transition_slide_xml",
    description="Generates a green social media transition slide with a solid left content panel, one editable title supporting up to 4 wrapped lines, a short horizontal divider, and a tinted full-height portrait image on the right.",
    args_schema=GenerateGreenSocialMediaTransitionSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_section_header_image_slide_xml,
    name="generate_section_header_image_slide_xml",
    description="Generates a section-header transition slide with a muted green upper panel, a centered vertical divider, one editable section heading, and a full-width landscape image across the lower portion of the slide.",
    args_schema=GenerateSectionHeaderImageSlideInput,
    ),
]

CONTENT_TOOLS = [
    # === XML CONTENT SLIDES ===
    StructuredTool.from_function(
        func=generate_content_creation_slide_xml,
        name="generate_content_creation_slide_xml",
        description="""Generates a content-creation slide with a large image on the left, a portrait image on the right, and two text content blocks for original content and curated content. Ideal for marketing, editorial, brand storytelling, and content strategy presentations.""",
        args_schema=GenerateContentCreationSlideInput
    ),
    StructuredTool.from_function(
        func=generate_ai_content_slide_xml,
        name="generate_ai_content_slide_xml",
        description="""Generates a flexible AI/content slide with a large title, intro text, bullet list, footer note, and a right-side image panel. Ideal for explaining a concept, feature list, process notes, or educational content.""",
        args_schema=GenerateAiContentSlideInput
    ),
    StructuredTool.from_function(
        func=generate_two_ideas_slide_xml,
        name="generate_two_ideas_slide_xml",
        description="""Generates a two-ideas slide with a full-height image panel on the left and a dark content area on the right containing a title, two idea headings, and supporting descriptions. Ideal for comparing two concepts or presenting two key points.""",
        args_schema=GenerateTwoIdeasSlideInput
    ),
    StructuredTool.from_function(
        func=generate_three_ideas_slide_xml,
        name="generate_three_ideas_slide_xml",
        description="""Generates a split-layout three-ideas slide with a dark content area, a large title, three idea headings, three supporting descriptions, and a full-height image panel on the right. Ideal for explaining three concepts, comparisons, highlights, or key points.""",
        args_schema=GenerateThreeIdeasSlideInput
    ),
    StructuredTool.from_function(
    func=generate_our_history_slide_xml,
    name="generate_our_history_slide_xml",
    description="Generates a split-layout history slide with a dark content area on the left and a full-height image panel on the right. The content area contains a large title and multiple vertically stacked history events, with right-aligned headings and descriptions, year markers, and vertical separator lines. Ideal for company histories, project milestones, product evolution, timelines, and organizational growth.",
    args_schema=GenerateOurHistorySlideInput,
    ),
    StructuredTool.from_function(
    func=generate_instructions_slide_xml,
    name="generate_instructions_slide_xml",
    description="Generates an instructional split-layout slide with a dark diagonal content panel on the left, a large workspace image on the right, a main title, two instruction columns, a footer information block, and a slanted accent bar. Ideal for usage instructions, onboarding guides, presentation tutorials, setup steps, and documentation slides.",
    args_schema=GenerateInstructionsSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_split_content_slide_xml,
    name="generate_split_content_slide_xml",
    description="Generates a split-content slide with a full-slide workspace image, a dark diagonal content panel on the left, a large title, multiple text columns, and a bright slanted accent bar aligned with the panel boundary. Ideal for comparisons, paired concepts, contrasting ideas, feature summaries, and side-by-side content presentations.",
    args_schema=GenerateSplitContentSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_picture_quote_slide_xml,
    name="generate_picture_quote_slide_xml",
    description="Generates a split image-and-text slide with a large image on the left, a white content panel on the right, a slanted accent bar, a title, and supporting text. Ideal for quotes, key messages, visual statements, and concept highlights.",
    args_schema=GeneratePictureQuoteSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_bullet_content_slide_xml,
    name="generate_bullet_content_slide_xml",
     description="Generates a diagonal split-content slide with a full-slide image, a dark panel on the left, a bright accent bar, a title, a bullet list, and supporting closing text. For bullet_items, provide plain item text only—never include •, -, *, 1., or 1) because the renderer adds the bullet marker. Ideal for key points, summaries, recommendations, feature lists, and instructional content.",
    args_schema=GenerateBulletContentSlideInput,
    ),  
    StructuredTool.from_function(
    func=generate_client_snapshot_slide_xml,
    name="generate_client_snapshot_slide_xml",
     description="Generates a client snapshot slide with a large title, subtitle, structured client details and goals on the left, and two stacked landscape images on the right. Provide client_details as plain text only—never include •, -, *, 1., or 1); use two leading spaces only for nested goals. Ideal for client profiles, company overviews, customer summaries, business context, and proposal presentations.",
    args_schema=GenerateClientSnapshotSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_how_forge_works_slide_xml,
    name="generate_how_forge_works_slide_xml",
    description="Generates a process overview slide with a title and subtitle on the left, an abstract vector decoration, and vertically connected process-step cards on the right. Ideal for workflows, implementation plans, onboarding processes, operating models, and step-by-step explanations.",
    args_schema=GenerateHowForgeWorksSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_implementation_timeline_slide_xml,
    name="generate_implementation_timeline_slide_xml",
    description="Generates an implementation timeline slide with a large title and subtitle, an abstract vector decoration, and horizontally arranged milestones containing labels and descriptions. Ideal for project schedules, rollout plans, implementation phases, product roadmaps, and delivery timelines.",
    args_schema=GenerateImplementationTimelineSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_problem_slide_xml,
    name="generate_problem_slide_xml",
    description="Generates a problem statement slide with up to five large rounded cards hanging from the top edge, each containing a problem item, plus a title and supporting description in the lower-left area. Ideal for presenting pain points, business challenges, customer problems, operational issues, and project motivations.",
    args_schema=GenerateProblemSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_topics_overview_slide_xml,
    name="generate_topics_overview_slide_xml",
    description="Generates a topics overview slide with a large title, soft corner accents, and up to three image-backed topic items containing titles and descriptions. Ideal for agenda points, key topics, main concepts, presentation overviews, and section summaries.",
    args_schema=GenerateTopicsOverviewSlideInput,
    ),  
    StructuredTool.from_function(
    func=generate_timeline_gallery_slide_xml,
    name="generate_timeline_gallery_slide_xml",
    description="Generates a gallery timeline slide with one to six milestones arranged along a horizontal timeline. Each milestone contains a title, description, and landscape image, with content alternating above and below the timeline.",
    args_schema=GenerateTimelineGallerySlideInput,
    ),
    StructuredTool.from_function(
    func=generate_memorial_introduction_slide_xml,
    name="generate_memorial_introduction_slide_xml",
    description="Generates a memorial introduction slide with a large portrait image on the left and a framed text panel on the right containing a section label, an italic main title, and a supporting paragraph.",
    args_schema=GenerateMemorialIntroductionSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_legacy_of_love_slide_xml,
    name="generate_legacy_of_love_slide_xml",
    description="Generates a memorial legacy slide with a full-slide landscape background image, an upper framed title panel, and a lower framed panel containing two balanced memorial text columns.",
    args_schema=GenerateLegacyOfLoveSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_social_media_points_slide_xml,
    name="generate_social_media_points_slide_xml",
    description="Generates a social media key-points slide with a centered headline, a top divider, and a responsive row containing 1 to 3 cards with colored headers, star icons, main-point titles, and supporting descriptions.",
    args_schema=GenerateSocialMediaPointsSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_numbered_social_media_points_slide_xml,
    name="generate_numbered_social_media_points_slide_xml",
    description="Generates a numbered social media points slide with a centered title and a responsive lower content grid containing automatically numbered item titles and supporting descriptions.",
    args_schema=GenerateNumberedSocialMediaPointsSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_platform_instructions_slide_xml,
    name="generate_platform_instructions_slide_xml",
    description="Generates a platform instruction slide with a responsive multi-column layout, colored accent lines, bold platform headings, organic icon backgrounds, selectable icon designs, and centered instructional text.",
    args_schema=GeneratePlatformInstructionsSlideInput,
    ),
]

# All available slide generation tools with complete parameter schemas


TEAM_TOOLS = []
THANK_YOU_TOOLS = [
    StructuredTool.from_function(
    func=generate_hanging_thank_you_slide_xml,
    name="generate_hanging_thank_you_slide_xml",
    description="Generates a colorful thank-you slide with a gradient background, hanging strings, individual letter cards forming a title of up to 14 visible characters excluding spaces, and a centered supporting subtitle.",
    args_schema=GenerateHangingThankYouSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_business_thank_you_slide_xml,
    name="generate_business_thank_you_slide_xml",
    description="Generates a professional business thank-you slide with a full-width dark hero image, a title of up to 50 characters, a geometric accent, a white closing-message panel, and a teal footer bar.",
    args_schema=GenerateBusinessThankYouSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_dark_gold_thank_you_slide_xml,
    name="generate_dark_gold_thank_you_slide_xml",
    description="Generates a dark and gold thank-you slide with a full-slide background image, a centered content panel, a one-line title, a supporting subtitle, a divider, and phone, email, and website contact information.",
    args_schema=GenerateDarkGoldThankYouSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_paper_flight_thank_you_slide_xml,
    name="generate_paper_flight_thank_you_slide_xml",
    description="Generates an illustrated thank-you slide with a title of up to approximately 40 characters, mountains, clouds, dashed flight paths, stars, envelopes, a paper plane, decorative dots, and underline elements.",
    args_schema=GeneratePaperFlightThankYouSlideInput,
    ),
    StructuredTool.from_function(
    func=generate_closing_thank_you_memorial_slide_xml,
    name="generate_closing_thank_you_memorial_slide_xml",
    description="Generates a memorial-style closing thank-you slide with a centered grayscale landscape image, an upper closing-statement band, a large central title band, and a lower supporting subtitle band.",
    args_schema=GenerateClosingThankYouMemorialSlideInput,
    ),
]
CHART_TOOLS = []

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


def _safe_xml_for_failed_tool(tool_name: str) -> str:
    """Return valid XML so one failed generator never empties the slide."""
    safe_name = escape(tool_name or "xml_tool")
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#F3F3F3">
    <shape type="rect" x="0" y="0" width="1600" height="900" fill="#F3F3F3" line_color="none" />
    <textbox x="120" y="300" width="1360" height="120" font="FreeSans" size="48" color="#111111" align="center" vertical_align="middle" overflow="clip">{safe_name}</textbox>
    <textbox x="120" y="450" width="1360" height="80" font="FreeSans" size="24" color="#555555" align="center" vertical_align="middle" overflow="clip">Slide content is temporarily unavailable</textbox>
  </slide>
</presentation>'''

def get_all_tool_names():
    """Return list of all available tool names."""
    return list(TOOL_MAP.keys())

def get_tool_by_name(name: str):
    """Get a specific tool by name."""
    return TOOL_MAP.get(name)

def execute_tool(tool_call: dict, source_content: str | None = None):
    """Execute a tool call with the provided arguments."""
    name = tool_call.get("name")
    args = tool_call.get("arguments", {})
    
    if name in TOOL_MAP:
        try:
            clean_args, highlights = extract_highlight_markers(
                args,
                source_content=source_content,
            )
            result = TOOL_MAP[name].invoke(clean_args)
            result_text = str(result) if result is not None else ""
            if result_text.strip() and result_text.strip().lower() != "none":
                result_text = materialize_math_fields_in_xml(result_text)
                result_text = apply_highlights_to_xml(
                    result_text,
                    highlights,
                )
                result_text = materialize_markdown_bold_runs(result_text)
                return result_text
            raise ValueError("XML tool returned empty content")
        except Exception as e:
            print(f"Error executing tool '{name}': {e}")
            if name.endswith("_xml"):
                print(f"Using safe XML fallback for tool '{name}'.")
                return _safe_xml_for_failed_tool(name)
            return None

    print(f"Tool '{name}' not found.")
    return None




def execute_tool_plan(
    tool_calls: list,
    tool_lookup: dict = None,
    source_content: str | None = None,
) -> tuple:
    """
    Execute one generator response: XML slide tool FIRST, then Search 1..N.

    No LLM is invoked here. Search results are connected to XML image
    parameters deterministically by schema/runtime declaration order.
    Returns (xml_output, final_xml_tool_call, search_history).
    """
    from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
        execute_image_search_plan,
    )

    if tool_lookup is None:
        tool_lookup = {t.name: t for tools in TOOLS_DICT.values() for t in tools}

    print(
        "\n🚀 [EXECUTE TOOL PLAN] Raw ordered calls:\n"
        f"{json.dumps(tool_calls, indent=2, ensure_ascii=False)}"
    )
    try:
        final_tool_call, search_history = execute_image_search_plan(
            tool_calls=tool_calls,
            tool_lookup=tool_lookup,
        )
    except Exception as error:
        # A malformed/missing image-search plan must not discard an otherwise
        # usable XML slide. Execute the first XML call with its own image
        # defaults and let execute_tool provide the final safe XML fallback if
        # the call itself is also invalid.
        print(f"Warning: XML tool plan normalization failed: {error}")
        if (
            isinstance(tool_calls, list)
            and tool_calls
            and isinstance(tool_calls[0], dict)
        ):
            final_tool_call = tool_calls[0]
        else:
            final_tool_call = {
                "name": "xml_tool_plan_fallback_xml",
                "arguments": {},
            }
        search_history = []
    tool_name = final_tool_call.get("name", "unknown_tool")
    original_xml_call = (
        tool_calls[0]
        if isinstance(tool_calls, list) and tool_calls
        else final_tool_call
    )
    search_calls = tool_calls[1:] if isinstance(tool_calls, list) else []

    # Build execution matrix theo cấu trúc training: tool_call trước, image_tool_call_N sau
    execution_matrix: dict = {"tool_call": original_xml_call}
    for i, call in enumerate(search_calls, start=1):
        result_url = search_history[i - 1].get("result_url", "") if i - 1 < len(search_history) else ""
        execution_matrix[f"image_tool_call_{i}"] = {
            **call,
            "result_url": result_url,   # URL thực đã tìm được (chỉ để log, không lưu dataset)
        }

    print(
        "  📦 [PIPELINE TOOL CALL EXECUTION MATRIX]:\n"
        f"{json.dumps(execution_matrix, indent=2, ensure_ascii=False)}"
    )

    print(f"  🎨 [RENDER XML] Executing tool '{tool_name}' to generate slide XML...")
    xml_out = execute_tool(final_tool_call, source_content=source_content)
    if not xml_out:
        print(f"  Warning: Tool '{tool_name}' returned no XML; using safe fallback.")
        xml_out = _safe_xml_for_failed_tool(tool_name)
    if xml_out:
        print(f"  ✅ [SUCCESS] Tool '{tool_name}' rendered XML successfully ({len(xml_out)} bytes).")
    else:
        print(f"  ❌ [ERROR] Tool '{tool_name}' failed to render XML.")
    return xml_out, final_tool_call, search_history
