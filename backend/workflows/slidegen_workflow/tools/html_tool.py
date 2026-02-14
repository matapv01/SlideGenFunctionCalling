#---------------------- SLIDE INTRO
def generate_title_slide(
    main_title="BUSINESS PLAN",
    subtitle="2026 - 2030",
    bg_color="#1a4b8c",
    bg_gradient_to="#2a6cb7",
    text_color="#FFFFFF",
    font_family="'Arial', sans-serif",
    show_skyline=True,
    skyline_opacity=0.3,
    triangle_opacity=0.2,
    show_border=True,
    custom_css=""
):
    """
    Generate a professional title slide with a blue gradient background and geometric shapes.

    :param main_title: Main title text (10-30 characters), displayed prominently in the center
    :param subtitle: Subtitle text (5-20 characters), displayed below the main title
    :param bg_color: Primary background color (hex code)
    :param bg_gradient_to: Secondary background color for gradient effect (hex code)
    :param text_color: Color of the title and subtitle text (hex code)
    :param font_family: Font family for all text elements
    :param show_skyline: Whether to show the city skyline silhouette at the bottom
    :param skyline_opacity: Opacity of the skyline silhouette (0.0 to 1.0)
    :param triangle_opacity: Opacity of the triangle decorative elements (0.0 to 1.0)
    :param title_font_size: Font size for the main title
    :param subtitle_font_size: Font size for the subtitle
    :param show_border: Whether to show the dashed border frame
    :param custom_css: Additional custom CSS to be included
    :return: A string containing the HTML code for the slide
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, {bg_color} 0%, {bg_gradient_to} 100%);
            position: relative;
            color: {text_color};
            padding: 60px;
            box-sizing: border-box;
        }}
        
        /* Content wrapper for scaling */
        .content-wrapper {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 1920px;
            height: 1080px;
            overflow: visible;
            background: inherit;
        }}
        
        .outer-wrapper {{
            padding: 0;
            box-sizing: border-box;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
        }}

        .content-frame {{
            width: 90%;
            max-width: 1200px;
            padding: 80px;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 5;
        }}
        
        .content-frame:not(.no-border) {{
            border: 2px dashed rgba(255, 255, 255, 0.3);
        }}
        
        .title {{
            font-size: 6rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            z-index: 10;
            letter-spacing: 2px;
        }}
        
        .subtitle {{
            font-size: 4rem;
            text-align: center;
            z-index: 10;
        }}
        
        /* Decorative triangles */
        .triangle {{
            position: absolute;
            width: 0;
            height: 0;
            opacity: {triangle_opacity};
            z-index: 1;
        }}
        
        .triangle-1 {{
            border-left: 100px solid transparent;
            border-right: 100px solid transparent;
            border-bottom: 200px solid rgba(255, 255, 255, 0.1);
            top: 10%;
            left: 5%;
            transform: rotate(15deg);
        }}
        
        .triangle-2 {{
            border-left: 80px solid transparent;
            border-right: 80px solid transparent;
            border-bottom: 160px solid rgba(255, 255, 255, 0.1);
            top: 20%;
            right: 10%;
            transform: rotate(-25deg);
        }}
        
        .triangle-3 {{
            border-left: 120px solid transparent;
            border-right: 120px solid transparent;
            border-bottom: 240px solid rgba(255, 255, 255, 0.1);
            bottom: 5%;
            left: 15%;
            transform: rotate(45deg);
        }}
        
        .triangle-4 {{
            border-left: 90px solid transparent;
            border-right: 90px solid transparent;
            border-bottom: 180px solid rgba(255, 255, 255, 0.1);
            bottom: 15%;
            right: 5%;
            transform: rotate(-35deg);
        }}
        
        /* City skyline */
        .skyline {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 100px;
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100"><path d="M0,100 L0,70 L20,70 L20,40 L40,40 L40,60 L60,60 L60,50 L80,50 L80,80 L100,80 L100,60 L120,60 L120,30 L140,30 L140,50 L160,50 L160,70 L180,70 L180,50 L200,50 L200,30 L220,30 L220,40 L240,40 L240,60 L260,60 L260,50 L280,50 L280,70 L300,70 L300,40 L320,40 L320,60 L340,60 L340,50 L360,50 L360,30 L380,30 L380,60 L400,60 L400,40 L420,40 L420,70 L440,70 L440,50 L460,50 L460,60 L480,60 L480,30 L500,30 L500,50 L520,50 L520,40 L540,40 L540,60 L560,60 L560,70 L580,70 L580,50 L600,50 L600,40 L620,40 L620,60 L640,60 L640,30 L660,30 L660,50 L680,50 L680,70 L700,70 L700,60 L720,60 L720,40 L740,40 L740,50 L760,50 L760,30 L780,30 L780,60 L800,60 L800,50 L820,50 L820,70 L840,70 L840,40 L860,40 L860,60 L880,60 L880,50 L900,50 L900,30 L920,30 L920,60 L940,60 L940,40 L960,40 L960,70 L980,70 L980,50 L1000,50 L1000,100 Z" fill="black" opacity="0.3"/></svg>');
            background-size: cover;
            opacity: {skyline_opacity};
            display: {("block" if show_skyline else "none")};
            z-index: 2;
        }}
        
        @media (max-width: 768px) {{
            .outer-wrapper {{
                transform: scale(0.4);
                transform-origin: top left;
            }}
        }}
        
        @media (max-width: 480px) {{
            .outer-wrapper {{
                transform: scale(0.25);
                transform-origin: top left;
            }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="outer-wrapper">
        <div class="content-wrapper">
            <div class="slide-container">
                <!-- Decorative triangles -->
                <div class="triangle triangle-1"></div>
                <div class="triangle triangle-2"></div>
                <div class="triangle triangle-3"></div>
                <div class="triangle triangle-4"></div>
                
                <!-- Content -->
                <div class="content-frame{(" no-border" if not show_border else "")}">
                    <h1 class="title">{main_title}</h1>
                    <div class="subtitle">{subtitle}</div>
                </div>
                
                <!-- City skyline -->
                <div class="skyline"></div>
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_code

def generate_introduction_slide(
    main_title="INTRODUCTION",
    content_text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse quis enim pretium, bibendum ante ullamcorper, tincidunt augue. ",
    bg_color="#1a4b8c",
    bg_gradient_to="#2a6cb7",
    text_color="#FFFFFF",
    font_family="'Arial', sans-serif",
    show_decorative_triangles=True,
    triangle_opacity=0.15,
    show_border=True,
    border_opacity=0.4,
    content_max_width="800px",
    line_height="1.6",
    letter_spacing="0.1em",
    custom_css=""
):
    """
    Generate a professional introduction slide with gradient background and decorative elements.

    :param main_title: Main title text (8-20 characters) or list where first element is title
    :param content_text: Main content paragraph or list where first element is content
    :param bg_color: Primary background color (hex code)
    :param bg_gradient_to: Secondary background color for gradient effect (hex code)
    :param text_color: Color of all text elements (hex code)
    :param title_font_size: Font size for the main title
    :param content_font_size: Font size for the content text
    :param font_family: Font family for all text elements
    :param show_decorative_triangles: Whether to show decorative triangle elements
    :param triangle_opacity: Opacity of the decorative triangles (0.0 to 1.0)
    :param show_border: Whether to show the dashed border frame
    :param border_opacity: Opacity of the border frame (0.0 to 1.0)
    :param content_max_width: Maximum width of the content area
    :param line_height: Line height for the content text
    :param letter_spacing: Letter spacing for the title
    :param custom_css: Additional custom CSS to be included
    :return: A string containing the HTML code for the slide
    """

    # Extract title and content if they're lists
    if isinstance(main_title, list) and len(main_title) > 0:
        main_title = main_title[0]
    
    if isinstance(content_text, list) and len(content_text) > 0:
        content_text = content_text[0]

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, {bg_color} 0%, {bg_gradient_to} 100%);
            position: relative;
            color: {text_color};
            padding: 60px;
            box-sizing: border-box;
        }}
        
        /* Content wrapper for scaling */
        .content-wrapper {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 1920px;
            height: 1080px;
            overflow: visible;
            background: inherit;
        }}
        
        .outer-wrapper {{
            padding: 0;
            box-sizing: border-box;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
        }}

        .content-frame {{
            width: 100%;
            max-width: 1400px;
            padding: 80px;
            position: relative;
            text-align: center;
        }}
        
        .content-frame:not(.no-border) {{
            border: 3px dashed rgba(255, 255, 255, 0.4);
            border-radius: 12px;
        }}
        
        
        .title {{
            font-size: 6rem;
            font-weight: 700;
            margin-bottom: 40px;
            letter-spacing: {letter_spacing};
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .content {{
            font-size: 2.25rem;
            line-height: {line_height};
            font-weight: 300;
            text-align: center;
            max-width: 90%;
            margin: 0 auto;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }}
        
        /* Decorative triangles */
        .triangle {{
            position: absolute;
            opacity: {triangle_opacity if show_decorative_triangles else 0};
            z-index: 1;
        }}
        
        .triangle-top-left {{
            top: 5%;
            left: 5%;
            width: 0;
            height: 0;
            border-left: 120px solid transparent;
            border-right: 120px solid transparent;
            border-bottom: 200px solid rgba(255, 255, 255, 0.1);
            transform: rotate(15deg);
        }}
        
        .triangle-top-right {{
            top: 8%;
            right: 8%;
            width: 0;
            height: 0;
            border-left: 100px solid transparent;
            border-right: 100px solid transparent;
            border-bottom: 180px solid rgba(255, 255, 255, 0.1);
            transform: rotate(-25deg);
        }}
        
        .triangle-bottom-left {{
            bottom: 10%;
            left: 3%;
            width: 0;
            height: 0;
            border-left: 80px solid transparent;
            border-right: 80px solid transparent;
            border-bottom: 140px solid rgba(255, 255, 255, 0.1);
            transform: rotate(45deg);
        }}
        
        .triangle-bottom-right {{
            bottom: 5%;
            right: 5%;
            width: 0;
            height: 0;
            border-left: 110px solid transparent;
            border-right: 110px solid transparent;
            border-bottom: 190px solid rgba(255, 255, 255, 0.1);
            transform: rotate(-35deg);
        }}
        
        /* Additional geometric shapes */
        .geometric-shape {{
            position: absolute;
            opacity: {triangle_opacity * 0.7 if show_decorative_triangles else 0};
            z-index: 2;
        }}
        
        .shape-1 {{
            top: 15%;
            left: 15%;
            width: 60px;
            height: 60px;
            background: rgba(255, 255, 255, 0.05);
            transform: rotate(45deg);
        }}
        
        .shape-2 {{
            top: 20%;
            right: 20%;
            width: 40px;
            height: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 50%;
        }}
        
        .shape-3 {{
            bottom: 25%;
            left: 20%;
            width: 50px;
            height: 50px;
            background: rgba(255, 255, 255, 0.05);
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
        }}
        
        @media (max-width: 768px) {{
            .outer-wrapper {{
                transform: scale(0.4);
                transform-origin: top left;
            }}
        }}
        
        @media (max-width: 480px) {{
            .outer-wrapper {{
                transform: scale(0.25);
                transform-origin: top left;
            }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="outer-wrapper">
        <div class="content-wrapper">
            <div class="slide-container">
                <!-- Decorative triangles -->
                <div class="triangle triangle-top-left"></div>
                <div class="triangle triangle-top-right"></div>
                <div class="triangle triangle-bottom-left"></div>
                <div class="triangle triangle-bottom-right"></div>
                
                <!-- Additional geometric shapes -->
                <div class="geometric-shape shape-1"></div>
                <div class="geometric-shape shape-2"></div>
                <div class="geometric-shape shape-3"></div>
                
                <!-- Main content -->
                <div class="content-frame{(" no-border" if not show_border else "")}">
                    <h1 class="title">{main_title}</h1>
                    <div class="content">{content_text}</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

    return html_code

def generate_intro_slide1(
    main_title="Main Title",
    subtitle1="Subtitle1",
    subtitle2="Subtitle2",
    main_bg_color="#ffffff",
    accent_bg_color="#6ea88a",
    text_box_bg_color="#c5e6b8",
    title_color="#333333",
    subtitle_color="#555555",
    line_color="#e6c35c",
    font_family="'Segoe UI', Arial, sans-serif",
    main_title_font_style="italic",
    image_url="Image/generate_intro_slide1/Default_1.png"        # Thêm tham số cho URL ảnh
):
    """
    Tạo slide HTML với thiết kế marketing có nền tràn viền như các slide khác.
    Các tham số kích thước nên được truyền vào dưới dạng chuỗi với đơn vị REM.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            background-color: {accent_bg_color};
            overflow: hidden;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            position: relative;
            background-color: {accent_bg_color};
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
            display: flex;
        }}
        
        .left-content {{
            flex: 0 0 60%;
            height: 100%;
            position: relative;
            background-color: {main_bg_color};
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .right-content {{
            flex: 0 0 40%;
            height: 100%;
            background-color: {accent_bg_color};
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .image-container {{
            width: 80%;
            height: 70%;
            background-color: white;
            border-radius: 1rem;
            box-shadow: 0 1rem 2rem rgba(0,0,0,0.15);
            overflow: hidden;
            position: relative;
            z-index: 3;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .accent-bar-top {{
            position: absolute;
            top: 0;
            left: 0;
            width: 4rem; /* 64px - larger for better visibility */
            height: 2rem; /* 32px */
            background-color: {text_box_bg_color};
            z-index: 1;
        }}
        
        .accent-bar-middle {{
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 4rem; /* 64px - larger */
            background-color: {text_box_bg_color};
            transform: translateY(-50%);
            z-index: 1;
        }}
        
        .content-box {{
            background-color: {text_box_bg_color};
            padding: 6rem; /* Increased padding */
            border-radius: 1.5rem; /* Rounded corners */
            z-index: 2;
            position: relative;
            width: 85%; 
            height: 85%; 
            max-width: none; 
            box-shadow: 0 1.5rem 3rem rgba(0,0,0,0.15); /* Deeper shadow */
            display: flex;
            flex-direction: column;
            justify-content: center;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .main-title {{
            font-size: 5.5rem; /* Larger title */
            color: {title_color};
            margin: 0 0 2.5rem 0; 
            font-weight: 800;
            font-style: {main_title_font_style};
            line-height: 1.1;
            text-align: center;
            letter-spacing: -0.02em;
        }}
        
        .subtitle {{
            font-size: 2.2rem; /* Larger subtitle */
            color: {subtitle_color};
            margin: 1.5rem 0; 
            line-height: 1.5;
            text-align: center;
            font-weight: 300;
        }}
        
        .divider {{
            width: 60%; 
            height: 0.4rem; 
            background-color: {line_color};
            margin: 3.5rem auto 0 auto; 
            border-radius: 0.2rem;
            opacity: 0.8;
        }}
        
        .decorative-element {{
            position: absolute;
            background-color: {text_box_bg_color};
            opacity: 0.5;
            z-index: 1;
        }}
        
        .deco-1 {{
            top: 1rem;
            right: 1rem;
            width: 4rem; /* 64px - smaller so they don't interfere with image */
            height: 4rem;
            border-radius: 50%;
        }}
        
        .deco-2 {{
            bottom: 1rem;
            right: 1rem;
            width: 3rem; /* 48px - smaller square */
            height: 3rem;
            transform: rotate(45deg);
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="slide-inner-container">
            <!-- Accent bars -->
            <div class="accent-bar-top"></div>
            <div class="accent-bar-middle"></div>
            
            <!-- Left content area -->
            <div class="left-content">
                <div class="content-box">
                    <h1 class="main-title">{main_title}</h1>
                    <p class="subtitle">{subtitle1}</p>
                    <p class="subtitle">{subtitle2}</p>
                </div>
            </div>
            
            <!-- Right content area -->
            <div class="right-content">
                <div class="image-container">
                    <img src="{image_url}" alt="slide visual">
                </div>
                <div class="decorative-element deco-1"></div>
                <div class="decorative-element deco-2"></div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_elegant_intro_slide(
    main_title="My Amazing Presentation",
    subtitle="This is a test slide to demonstrate the improved layout and styling.",
    image_url="https://images.pexels.com/photos/3807735/pexels-photo-3807735.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    font_family="'Be Vietnam Pro', sans-serif",
    background_color="#EAE3D9",
    text_color="#4A403A",
    decoration_color_start="#F7DC6F",
    decoration_color_end="#C9A842"
):
    """
    Generates an elegant intro slide optimized for 1920x1080 screenshots with balanced layout.
    Features improved proportions, spacing, and visual hierarchy.
    """

    # SVG Definitions
    gradient_def = f"""
    <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:{decoration_color_start};stop-opacity:1" />
        <stop offset="100%" style="stop-color:{decoration_color_end};stop-opacity:1" />
    </linearGradient>
    """
    
    star_svg = """
    <svg class="star" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <polygon points="50,0 61,39 100,50 61,61 50,100 39,61 0,50 39,39" fill="url(#goldGradient)"/>
    </svg>
    """
    
    botanical_frame_svg = f"""
    <svg class="botanical-frame" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <defs>{gradient_def}</defs>
        <g fill="url(#goldGradient)" stroke="url(#goldGradient)" stroke-width="1" stroke-linecap="round">
            <!-- Main Stem -->
            <path d="M 190,10 C 120,80 110,120 10,190" fill="none" stroke-width="2"/>

            <!-- Leaves on the right -->
            <path d="M 190,10 C 180,50 160,60 145,60 C 160,60 170,80 185,90" fill="none"/>
            <path d="M 160,65 C 150,95 120,110 110,105 C 120,110 130,130 145,140" fill="none"/>

            <!-- Leaves on the left -->
            <path d="M 80,185 C 110,175 125,150 120,140 C 125,150 145,160 160,170" fill="none"/>
            <path d="M 15,190 C 45,180 60,150 55,145 C 60,150 80,165 95,175" fill="none"/>

            <!-- Berries -->
            <circle cx="120" cy="80" r="4"/>
            <circle cx="105" cy="125" r="4"/>
            <circle cx="70" cy="165" r="4"/>
        </g>
    </svg>
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elegant Intro Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            background-color: {background_color};
            color: {text_color};
            overflow: hidden;
        }}

        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            background-color: {background_color};
            display: grid;
            grid-template-columns: 1fr 1fr;
            align-items: center;
            padding: 80px 120px;
            gap: 80px;
        }}

        .text-column {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding-right: 40px;
            z-index: 10;
        }}

        .main-title {{
            font-size: 112px;
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 40px;
            max-width: 720px;
        }}

        .subtitle {{
            font-size: 36px;
            line-height: 1.6;
            opacity: 0.85;
            max-width: 600px;
            font-weight: 400;
        }}

        .image-column {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .image-wrapper {{
            position: relative;
            width: 100%;
            max-width: 560px;
            height: 420px;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}

        .main-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}

        /* --- Decorations --- */
        .star-cluster {{
            position: absolute;
            top: -20px;
            left: -20px;
            width: 80px;
            height: 80px;
            pointer-events: none;
            z-index: 20;
        }}
        
        .star-cluster .star {{ 
            position: absolute; 
            opacity: 0.9; 
        }}
        
        .star-cluster .star:nth-child(1) {{ 
            width: 28px; 
            height: 28px; 
            top: 0; 
            left: 0; 
        }}
        
        .star-cluster .star:nth-child(2) {{ 
            width: 22px; 
            height: 22px; 
            top: 30px; 
            left: 10px; 
        }}
        
        .star-cluster .star:nth-child(3) {{ 
            width: 18px; 
            height: 18px; 
            top: 8px; 
            left: 36px; 
        }}

        .botanical-frame {{
            position: absolute;
            bottom: -40px;
            right: -40px;
            width: 200px;
            height: 200px;
            opacity: 0.8;
            pointer-events: none;
            transform: scaleX(-1);
            z-index: 5;
        }}

        /* Content wrapper for scaling */
        .content-wrapper {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 1920px;
            height: 1080px;
            overflow: visible;
            background: inherit;
        }}
        
        .outer-wrapper {{
            padding: 0;
            box-sizing: border-box;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
        }}

    </style>
</head>
<body>
    <div class="outer-wrapper">
        <div class="content-wrapper">
            <div class="slide-container">
                <div class="text-column">
                    <h1 class="main-title">{main_title}</h1>
                    <p class="subtitle">{subtitle}</p>
                </div>
                <div class="image-column">
                    <div class="image-wrapper">
                        <img class="main-image" src="{image_url}" alt="Introductory image" />
                        <div class="star-cluster">
                            {star_svg}
                            {star_svg}
                            {star_svg}
                        </div>
                        {botanical_frame_svg}
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_inspirational_quote_slide(
    quote_text="The best way to predict the future is to create it.",
    attribution_text="Peter Drucker",
    font_family="'Playfair Display', serif",
    background_image_url="https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=2069&auto=format&fit=crop",
    text_color="#3A3A3A"
):
    """
    Generates a clean and elegant quote slide with a light-themed background image.
    Features elegant serif typography with a simple, focused design.
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inspirational Quote Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        /* OVERRIDE EDITOR BACKGROUND - HIGHEST SPECIFICITY */
        div[style*="background: white"], 
        div[style*="background: #FFFFFF"],
        div[style*="background-color: white"],
        div[style*="background-color: #FFFFFF"],
        #canvas,
        [data-bg*="#FFFFFF"] {{
            background-image: url('{background_image_url}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-color: transparent !important;
        }}
        
        html#html.html {{ 
            font-size: 16px !important;
            height: 100vh !important;
            width: 100vw !important;
            font-family: {font_family} !important;
            background-image: url('{background_image_url}') !important;
            background-size: cover !important;
            background-position: center !important;
            color: {text_color} !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            overflow: hidden !important;
        }}
        
        body#body.body, html#html.html {{
            height: 100vh !important;
            width: 100vw !important;
            font-family: {font_family} !important;
            background-image: url('{background_image_url}') !important;
            background-size: cover !important;
            background-position: center !important;
            color: {text_color} !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            overflow: hidden !important;
        }}

        .slide-container {{
            width: 95%;
            max-width: 85rem;
            text-align: center;
            position: relative;
            background-color: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(8px);
            padding: 9rem;
            border-radius: 1.5rem;
        }}

        .quote-text {{
            font-size: clamp(5.25rem, 10.5vw, 9rem);
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 4.5rem;
            /* Bỏ bóng đổ vì không cần thiết trên nền sáng */
        }}

        .attribution-text {{
            font-size: 3rem;
            font-style: italic;
            font-weight: 400;
            opacity: 0.9;
        }}

        @media (max-width: 48rem) {{
            .slide-container {{ padding: 3rem 2rem; }}
            .slide-container::before {{ font-size: 15rem; top: -6rem; left: -2rem; }}
            .slide-container::after {{ font-size: 15rem; bottom: -8rem; right: -2rem; }}
        }}
    </style>
</head>
<body id="body" class="body">
    <div class="slide-container">
        <h1 class="quote-text">“{quote_text}”</h1>
        <p class="attribution-text">— {attribution_text}</p>
    </div>
</body>
</html>"""
    
    return html_code

def generate_title_slide_2(
    main_title="THIS IS YOUR<br><span class='highlight'>PRESENTATION</span><br>TITLE",
    font_family="'Montserrat', sans-serif",
    accent_color="#06B6D4",
    shadow_color="#0E7490",
    text_color="#6B7280",
    icon_color="#D1D5DB"
):
    """
    Generates a modern, corporate title slide with a dynamic diagonal split.
    Features a two-tone color panel. The title can optionally contain a highlighted word.
    """

    # SVG icon for a presentation chart
    icon_svg = f"""
    <svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 3v18h18"/>
        <path d="m19 9-5 5-4-4-3 3"/>
    </svg>
    """

    # SVG clip-path definition for the diagonal shape
    clip_path_svg = """
    <svg width="0" height="0">
      <defs>
        <clipPath id="angled-title-divider" clipPathUnits="objectBoundingBox">
          <polygon points="0.3 0, 1 0, 1 1, 0 1" />
        </clipPath>
      </defs>
    </svg>
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Corporate Title Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: #FFFFFF;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            position: relative;
            border-top: 4px solid #F3F4F6;
        }}

        .text-column {{
            flex: 1;
            padding: 4rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .color-column {{
            flex: 1;
            position: relative;
            background-color: {accent_color};
            clip-path: url(#angled-title-divider);
        }}

        .color-column::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: {shadow_color};
            clip-path: url(#angled-title-divider);
            transform: translateX(-1.5rem);
            z-index: -1;
        }}
        
        .icon-svg {{
            width: 3rem;
            height: 3rem;
            margin-bottom: 1.5rem;
        }}

        .main-title {{
            font-size: clamp(2.5rem, 7vw, 6rem);
            font-weight: 800;
            color: {text_color};
            line-height: 1.1;
            text-transform: uppercase;
        }}
        
        .highlight {{
            color: {accent_color};
        }}
        
        @media (max-width: 48rem) {{
            .text-column {{ text-align: center; align-items: center; }}
            .color-column {{ display: none; }}
        }}

    </style>
</head>
<body>
    {clip_path_svg}
    <div class="slide-container">
        <div class="text-column">
            {icon_svg}
            <h1 class="main-title">{main_title}</h1>
        </div>
        <div class="color-column"></div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_dynamic_intro_slide(
    # ĐÃ THAY ĐỔI: Chữ mặc định mới, phù hợp với font lớn
    main_title="Innovate. Create. Inspire.",
    subtitle="This is where we outline our core mission and the driving force behind our vision.",
    # ĐÃ THAY ĐỔI: Ảnh nền mới, hiện đại hơn
    image_url="https://images.unsplash.com/photo-1521737711867-e3b97375f902?q=80&w=1887&auto=format&fit=crop",
    font_family="'Poppins', sans-serif",
    primary_color="#4F46E5",
    secondary_color="#3730A3",
    text_color="#FFFFFF"
):
    """
    Generates a dynamic introductory slide with larger fonts for greater impact,
    an angled divider, and geometric decorations.
    """
    
    clip_path_svg = """
    <svg width="0" height="0">
      <defs>
        <clipPath id="angled-divider" clipPathUnits="objectBoundingBox">
          <polygon points="0 0, 1 0, 1 0.85, 0.85 1, 0 1" />
        </clipPath>
      </defs>
    </svg>
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynamic Intro Slide - Large Text</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            background-color: white;
        }}

        .text-column {{
            flex: 1.2;
            background-color: {primary_color};
            color: {text_color};
            clip-path: url(#angled-divider);
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 6rem 5rem;
        }}

        .image-column {{
            flex: 1;
            background-image: url('{image_url}');
            background-size: cover;
            background-position: center;
        }}

        .title-group {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .main-title {{
            font-size: clamp(3.5rem, 6vw, 6rem);
            font-weight: 700;
            line-height: 1.15;
            margin-bottom: 6rem;
            letter-spacing: -0.02em;
        }}

        .subtitle {{
            font-size: 2rem;
            font-weight: 400;
            line-height: 1.6;
            opacity: 0.95;
            max-width: 42rem;
        }}

        .footer-decor {{
            width: 100%;
            height: 5rem;
            background-color: {secondary_color};
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
        }}
        
        .arcs {{
            width: 5rem;
            height: 5rem;
            position: relative;
        }}
        .arcs::before, .arcs::after {{
            content: '';
            position: absolute;
            border-radius: 50%;
            border: 0.125rem solid {text_color};
            left: -3.5rem;
            top: 50%;
            transform: translateY(-50%);
        }}
        .arcs::before {{ width: 7rem; height: 7rem; }}
        .arcs::after {{ width: 6rem; height: 6rem; }}

        .dots-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
        }}
        .dot {{
            width: 0.75rem;
            height: 0.75rem;
            background-color: {text_color};
            border-radius: 50%;
        }}
        
        @media (max-width: 64rem) {{
            .text-column {{
                flex: 1;
                clip-path: none;
            }}
            .image-column {{ flex: 1; }}
        }}

        @media (max-width: 48rem) {{
            .slide-container {{ flex-direction: column; }}
            .text-column, .image-column {{ flex: none; width: 100%; }}
            .text-column {{ height: 60vh; padding: 2.5rem; justify-content: center; text-align: center; }}
            .image-column {{ height: 40vh; }}
            .footer-decor {{ display: none; }}
        }}
    </style>
</head>
<body>
    {clip_path_svg}
    <div class="slide-container">
        <div class="text-column">
            <div class="title-group">
                <h1 class="main-title">{main_title}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
            <div class="footer-decor">
                <div class="arcs"></div>
                <div class="dots-grid">
                    <div class="dot"></div><div class="dot"></div>
                    <div class="dot"></div><div class="dot"></div>
                </div>
            </div>
        </div>
        <div class="image-column"></div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_big_concept_slide(
    main_title="BIG<br>CONCEPT",
    subtitle="Bring the attention of your audience over a key concept using icons or illustrations",
    icon_name="space",
    font_family="'Poppins', sans-serif",
    bg_color="#0F172A",
    text_color="#FFFFFF"
):
    """
    Generates a 'Big Concept' slide with a space-themed illustration (planet and stars).
    Maintains the geometric corner design and clean, bold typography.
    """
    
    # SVG definitions - The red rocket has been removed.
    icons = {
        "space": f"""
            <div class="illustration-container">
                <svg class="icon-planet" viewBox="0 0 60 60" fill="#7DD3FC" xmlns="http://www.w3.org/2000/svg">
                    <path d="M51.9,20.6c-3-5.2-7.8-9.1-13.6-11.1C32.1,7.2,25.4,6,18.9,6.9c-5.1,0.7-9.8,2.7-13.7,5.9C-2,19.9-0.2,31.8,7,39
                        c4.5,4.5,10.4,7,16.8,7c5.6,0,11-1.8,15.5-5.1C48,35.1,53.8,27.7,51.9,20.6z"/>
                    <path d="M58.5,39.6c-2.3,0-4.5-0.3-6.7-0.8c-7.2-1.8-12.2-6.5-14-12.7c-0.7-2.5-0.6-5.1,0.2-7.6c0.5-1.5,1.1-3,1.9-4.3
                        c-4,6.3-4.3,14.2-0.8,20.8c2.9,5.5,8.5,9.3,15,10.2c1.4,0.2,2.8,0.3,4.2,0.3c3.7,0,7.3-0.9,10.5-2.6
                        C67.1,43.2,63.1,39.6,58.5,39.6z"/>
                    <circle cx="21.5" cy="18.9" r="1.5" fill="#0F172A"/>
                    <circle cx="16.9" cy="25.5" r="1" fill="#0F172A"/>
                    <circle cx="27.8" cy="26.9" r="2" fill="#0F172A"/>
                </svg>
                <svg class="icon-star" style="top: 0; right: 8rem;" viewBox="0 0 24 24" fill="#FACC15" xmlns="http://www.w3.org/2000/svg"><path d="M12,17.3l-5.3,3.2l1.4-6.2L3.5,9.5l6.3-0.5L12,3.2l2.2,5.8l6.3,0.5l-4.6,4.8l1.4,6.2L12,17.3z"/></svg>
                <svg class="icon-star" style="top: 5rem; right: 0;" viewBox="0 0 24 24" fill="#FACC15" xmlns="http://www.w3.org/2000/svg"><path d="M12,17.3l-5.3,3.2l1.4-6.2L3.5,9.5l6.3-0.5L12,3.2l2.2,5.8l6.3,0.5l-4.6,4.8l1.4,6.2L12,17.3z"/></svg>
                <svg class="icon-star" style="top: 10rem; right: 6rem;" viewBox="0 0 24 24" fill="#FACC15" xmlns="http://www.w3.org/2000/svg"><path d="M12,17.3l-5.3,3.2l1.4-6.2L3.5,9.5l6.3-0.5L12,3.2l2.2,5.8l6.3,0.5l-4.6,4.8l1.4,6.2L12,17.3z"/></svg>
            </div>
        """
    }
    
    icon_svg_html = icons.get(icon_name, "<div>Icon not found</div>")

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Big Concept Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
            color: {text_color};
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            padding: 4rem;
        }}
        
        .main-content-grid {{
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            align-items: center;
            gap: 2rem;
            width: 100%;
            max-width: 80rem;
            z-index: 10;
        }}

        .text-column {{
            padding-right: 3rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .big-title {{
            font-size: 5.5rem;
            font-weight: 800;
            line-height: 1.05;
            text-transform: uppercase;
            margin-bottom: 3rem;
            letter-spacing: -0.02em;
        }}

        .subtitle {{
            font-size: 2rem;
            line-height: 1.6;
            font-weight: 400;
            max-width: 90%;
            opacity: 0.95;
        }}
        
        .icon-column {{
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            height: 25rem;
        }}
        
        .illustration-container {{
            position: relative;
            width: 100%;
            height: 100%;
        }}
        
        .illustration-container svg {{
            position: absolute;
            transform: rotate(-15deg);
        }}
        
        .icon-planet {{ width: 15rem; height: 15rem; top: 2rem; right: 1rem; }}
        /* Rocket CSS rule removed */
        .icon-star {{ width: 2.5rem; height: 2.5rem; }}

        /* Reused Geometric Shapes */
        .shape-cluster {{ position: absolute; pointer-events: none; z-index: 1; transform: scale(0.85); }}
        .shape {{ position: absolute; border-radius: 8px; }}
        .top-right {{ top: 5rem; right: 5rem; width: 25rem; height: 20rem; }}
        .shape-tr-1 {{ width: 14rem; height: 14rem; background-color: #1E3A8A; opacity: 0.6; top: 0; right: 8rem; transform: rotate(15deg); }}
        .shape-tr-2 {{ width: 15rem; height: 15rem; background-color: #34D399; opacity: 0.7; top: 2rem; right: 0; transform: rotate(25deg); }}
        .shape-tr-3 {{ width: 13rem; height: 13rem; background-color: #6366F1; opacity: 0.6; top: 8rem; right: 10rem; transform: rotate(35deg); }}
        .shape-tr-4 {{ width: 12rem; height: 12rem; background: linear-gradient(45deg, #F59E0B, #FBBF24); opacity: 0.8; top: 12rem; right: 2rem; transform: rotate(10deg); }}
        .bottom-left {{ bottom: 3rem; left: -5rem; width: 25rem; height: 20rem; }}
        .shape-bl-1 {{ width: 12rem; height: 12rem; background-color: #4F46E5; opacity: 0.5; bottom: 0; left: 10rem; transform: rotate(-25deg); }}
        .shape-bl-2 {{ width: 14rem; height: 14rem; background-color: #10B981; opacity: 0.4; bottom: 8rem; left: 2rem; transform: rotate(-35deg); }}
        .shape-bl-3 {{ width: 16rem; height: 16rem; background: linear-gradient(45deg, #EF4444, #F97316); opacity: 0.7; bottom: 0; left: 0; transform: rotate(-15deg); }}

        @media (max-width: 64rem) {{
            .main-content-grid {{ grid-template-columns: 1fr; text-align: center; }}
            .text-column {{ padding-right: 0; order: 2; }}
            .icon-column {{ order: 1; height: 15rem; margin-bottom: 2rem; }}
            .subtitle {{ max-width: none; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="shape-cluster top-right"></div>
        <div class="shape-cluster bottom-left"></div>
        <div class="main-content-grid">
            <div class="text-column">
                <h1 class="big-title">{main_title}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
            <div class="icon-column">
                {icon_svg_html}
            </div>
        </div>
        <div class="shape-cluster top-right">
            <div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3"></div><div class="shape shape-tr-4"></div>
        </div>
        <div class="shape-cluster bottom-left">
             <div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div>
        </div>
    </div>
</body>
</html>"""
    return html_code

def generate_elegant_agenda_slide(
    main_title="Bài thuyết trình hôm nay",
    subtitle="CHỦ ĐỀ CHÍNH",
    agenda_items=[
        "Về công ty chúng tôi",
        "Dịch vụ mạng xã hội",
        "Vấn đề/Cơ hội",
        "Giải pháp của chúng tôi",
        "Thực hiện kế hoạch",
        "Đội ngũ của chúng tôi"
    ],
    # --- Hình ảnh và màu sắc ---
    image_url="https://images.unsplash.com/photo-1484417894907-623942c8ee29?q=80&w=2832&auto=format&fit=crop",
    accent_color="#EAD6D6", # Dusty Rose
    bg_color="#FCFCFC",
    title_color="#1F2937", # Dark Gray
    subtitle_color="#B48E8E",
    text_color="#4B5563", # Medium Gray
    # --- Font chữ ---
    font_family_title="'Playfair Display', serif",
    font_family_body="'Montserrat', sans-serif",
    custom_css=""
):
    """
    Generates an elegant, minimalist agenda or table of contents slide.
    Features a two-column layout with a framed image on the left and a text list on the right.
    """
    
    agenda_list_html = "".join([f"<li class='agenda-item'>{item}</li>" for item in agenda_items])

    html_code = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500&family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{ font-size: 16px; }}
        body, html {{
            margin: 0; padding: 0; height: 100%; width: 100%;
            font-family: {font_family_body};
            overflow: hidden;
            background-color: {bg_color};
        }}
        
        .slide-container {{
            width: 100%; height: 100vh;
            display: flex; align-items: center; justify-content: center;
            padding: 4vw; box-sizing: border-box;
        }}
        
        .content-wrapper {{
            display: flex; align-items: center; justify-content: center;
            width: 100%; max-width: 75rem; /* 1200px */
        }}
        
        /* Image Section with Decorative Frame */
        .image-section {{
            flex: 1;
            position: relative;
            height: 28rem; /* 448px */
        }}
        .accent-bg {{
            position: absolute;
            top: 0;
            left: 0;
            width: 90%;
            height: 90%;
            background-color: {accent_color};
            z-index: 1;
        }}
        .main-image {{
            position: absolute;
            bottom: 0;
            right: 0;
            width: 90%;
            height: 90%;
            object-fit: cover;
            z-index: 2;
            box-shadow: 0 1rem 2rem rgba(0,0,0,0.1);
        }}
        
        /* Text Section */
        .text-section {{
            flex: 1;
            padding-left: 5rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .main-title {{
            font-family: {font_family_title};
            font-size: 5rem;
            font-weight: 600;
            font-style: italic;
            color: {title_color};
            margin: 0 0 2rem 0;
            line-height: 1.15;
            letter-spacing: -0.01em;
        }}
        
        .subtitle {{
            font-size: 1.15rem;
            font-weight: 600;
            color: {subtitle_color};
            text-transform: uppercase;
            letter-spacing: 0.25em;
            margin-bottom: 2.5rem;
        }}

        .agenda-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        .agenda-item {{
            font-size: 1.75rem;
            color: {text_color};
            margin-bottom: 1.5rem;
            font-weight: 400;
            line-height: 1.4;
        }}

        /* Responsive Design */
        @media (max-width: 56.25em) {{ /* 900px */
            .text-section {{ padding-left: 3rem; }}
            .main-title {{ font-size: 3rem; }}
            .agenda-item {{ font-size: 1rem; }}
        }}
        @media (max-width: 48em) {{ /* 768px */
            .content-wrapper {{ flex-direction: column; }}
            .image-section {{ width: 80%; height: 20rem; margin-bottom: 3rem; }}
            .text-section {{ width: 80%; padding-left: 0; text-align: center; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="content-wrapper">
            <div class="image-section">
                <div class="accent-bg"></div>
                <img src="{image_url}" alt="Workspace" class="main-image">
            </div>
            <div class="text-section">
                <h1 class="main-title">{main_title}</h1>
                <h3 class="subtitle">{subtitle}</h3>
                <ul class="agenda-list">
                    {agenda_list_html}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_code

def generate_playful_title_slide(
    main_title="Introduction<br>to penguins",
    subtitle="Introduce penguins here. Mention their characteristics and unique behaviors.",
    illustration_character="penguin",
    font_family_title="'Patrick Hand', cursive",
    font_family_body="'Lato', sans-serif",
    top_bg_color="#FFC947",
    bottom_bg_color="#E8715D",
    text_color="#2D2D2D",
    doodle_color="#89CFF0"
):
    """
    Generates a friendly, hand-drawn style title slide. Features a large, charming
    illustration and playful typography, perfect for educational or light-hearted topics.
    """
    illustrations = {
        "penguin": f"""
            <div class="illustration-wrapper">
                <svg class="doodle doodle-1" viewBox="0 0 100 50"><path d="M 10 40 Q 30 10 50 25 T 90 20" stroke="{doodle_color}" stroke-width="8" fill="none" stroke-linecap="round"/></svg>
                <svg class="doodle doodle-2" viewBox="0 0 30 30"><path d="M15 2 L19 11 L29 11 L21 17 L24 27 L15 21 L6 27 L9 17 L1 11 L11 11 Z" fill="{doodle_color}"/></svg>
                <svg class="doodle doodle-3" viewBox="0 0 100 50"><path d="M 10 20 Q 30 40 50 25 T 90 30" stroke="{doodle_color}" stroke-width="8" fill="none" stroke-linecap="round"/></svg>
                <svg class="doodle doodle-4" viewBox="0 0 30 30"><path d="M15 2 L19 11 L29 11 L21 17 L24 27 L15 21 L6 27 L9 17 L1 11 L11 11 Z" fill="{doodle_color}"/></svg>
                <svg class="penguin-svg" viewBox="0 0 200 220" xmlns="http://www.w3.org/2000/svg"><g transform="translate(0, 10)"><path d="M 80 200 Q 70 205 60 200 L 65 210 Z" fill="#E8B48E"/><path d="M 120 200 Q 130 205 140 200 L 135 210 Z" fill="#E8B48E"/><path d="M 100 0 C 40 0, 10 60, 10 130 Q 10 200, 100 200 Q 190 200, 190 130 C 190 60, 160 0, 100 0 Z" fill="#2D2D2D"/><path d="M 100 55 C 70 55, 50 80, 50 130 Q 50 180, 100 180 Q 150 180, 150 130 C 150 80, 130 55, 100 55 Z" fill="#FFFFFF"/><path d="M 100 20 C 140 20, 160 60, 150 90 L 100 80 L 50 90 C 40 60, 60 20, 100 20 Z" fill="#FFFFFF"/><rect x="65" y="80" width="70" height="25" fill="#D92E2E" rx="5"/><path d="M 90 65 L 110 65 L 100 78 Z" fill="#FF8C61"/><circle cx="85" cy="55" r="5" fill="#2D2D2D"/><circle cx="115" cy="55" r="5" fill="#2D2D2D"/><circle cx="70" cy="65" r="8" fill="#FADADD" opacity="0.8"/><circle cx="130" cy="65" r="8" fill="#FADADD" opacity="0.8"/><path d="M 80 90 L 65 160 L 85 155 L 95 95 Z" fill="#D92E2E" transform="rotate(-5, 80, 90)"/><rect x="68" y="98" width="12" height="5" fill="#FFFFFF"/><rect x="67" y="110" width="14" height="5" fill="#FFFFFF"/><rect x="66" y="122" width="16" height="5" fill="#FFFFFF"/><rect x="65" y="134" width="18" height="5" fill="#FFFFFF"/><path d="M 65 160 L 63 168 M 70 158 L 68 166 M 75 157 L 73 165 M 80 156 L 78 164 M 85 155 L 83 163" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/><path d="M 95 18 Q 100 10 105 18" stroke="#2D2D2D" stroke-width="2" fill="none" stroke-linecap="round"/></g></svg>
            </div>
        """
    }
    illustration_html = illustrations.get(illustration_character, "<div>Illustration not found.</div>")
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Playful Title Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }} html {{ font-size: 16px; }}
        body, html {{ height: 100vh; width: 100vw; overflow: hidden; }}
        .slide-container {{ width: 100%; height: 100%; background-color: {top_bg_color}; position: relative; display: grid; grid-template-columns: 1fr 1fr; align-items: center; padding: 4rem 5rem; }}
        .slide-container::after {{ content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 15%; background-color: {bottom_bg_color}; z-index: 0; }}
        .text-column {{ z-index: 10; display: flex; flex-direction: column; justify-content: center; }}
        .main-title {{ font-family: 'Patrick Hand', cursive; font-size: clamp(3.5rem, 8vw, 6.5rem); font-weight: 400; color: #2D2D2D; line-height: 1.15; margin-bottom: 2.5rem; }}
        .subtitle {{ font-family: {font_family_body}; font-size: 2rem; color: {text_color}; line-height: 1.6; max-width: 45ch; font-weight: 400; }}
        .illustration-column {{ z-index: 5; display: flex; align-items: center; justify-content: center; }}
        .illustration-wrapper {{ position: relative; width: 90%; max-width: 450px; }}
        .penguin-svg {{ width: 100%; height: auto; filter: drop-shadow(5px 5px 10px rgba(0,0,0,0.1)); }}
        .doodle {{ position: absolute; opacity: 0.7; }}
        .doodle-1 {{ width: 6rem; top: 0; left: 25%; transform: rotate(15deg); }}
        .doodle-2 {{ width: 2rem; top: 2rem; right: 0; transform: rotate(25deg); }}
        .doodle-3 {{ width: 6rem; bottom: 5rem; right: -1rem; transform: rotate(-20deg) scaleX(-1); }}
        .doodle-4 {{ width: 2rem; bottom: 2rem; left: 0; transform: rotate(-15deg); }}
        @media (max-width: 48rem) {{ .slide-container {{ grid-template-columns: 1fr; text-align: center; }} .text-column {{ order: 2; }} .illustration-column {{ order: 1; }} .subtitle {{ margin: 0 auto; }} }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="text-column"><h1 class="main-title">{main_title}</h1><p class="subtitle">{subtitle}</p></div>
        <div class="illustration-column">{illustration_html}</div>
    </div>
</body>
</html>"""
    return html_code

def generate_minimalist_title_slide(
    main_title="This is your presentation title",
    subtitle="A subtitle to provide more context or a tagline",
    author_line="Presented by Your Name / Company",
    font_family="'Inter', sans-serif",
    bg_color="#111827",
    text_color="#F9FAFB",
    subtitle_color="#E5E7EB",
    accent_color="#38BDF8"
):
    """
    Generates a stunning, STATIC high-tech title slide with a dark theme
    and a glowing portal. The portal no longer animates.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Title Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --accent-color: {accent_color};
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
            color: {text_color};
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding: 4rem 5rem;
            position: relative;
        }}

        .text-content {{
            max-width: 50%;
            z-index: 2;
        }}

        .main-title {{
            font-size: clamp(3.5rem, 8vw, 6.5rem);
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 2rem;
        }}

        .subtitle {{
            font-size: 1.85rem;
            line-height: 1.6;
            color: {subtitle_color};
            opacity: 0.9;
            margin-bottom: 3rem;
            max-width: 35ch;
        }}
        
        .author-line {{
            font-size: 1.3rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            opacity: 0.7;
        }}

        .glowing-portal {{
            position: absolute;
            width: 45rem;
            height: 45rem;
            right: -10rem;
            top: 50%;
            transform: translateY(-50%);
            border: 4px solid var(--accent-color);
            border-radius: 50%;
            box-shadow: 
                0 0 20px 0 var(--accent-color),
                inset 0 0 20px 0 var(--accent-color),
                0 0 60px 10px rgba(56, 189, 248, 0.3);
            /* ĐÃ XÓA: animation: spin 80s linear infinite; */
            z-index: 1;
        }}

        /* ĐÃ XÓA: @keyframes spin */

        @media (max-width: 64rem) {{
            .slide-container {{ 
                flex-direction: column;
                justify-content: center;
                text-align: center;
                padding: 2rem;
            }}
            .text-content {{ max-width: 100%; }}
            .glowing-portal {{
                width: 30rem;
                height: 30rem;
                right: 50%;
                top: 50%;
                transform: translate(50%, -50%);
                opacity: 0.3;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="glowing-portal"></div>
        <div class="text-content">
            <h1 class="main-title">{main_title}</h1>
            <p class="subtitle">{subtitle}</p>
            <p class="author-line">{author_line}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_mission_slide(
    top_text="Subheading or Category",
    title="Your Main Title Here",
    subtitle="Elaborate on your key message or provide a call to action. This text can be a bit longer.",
    image_url="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?q=80&w=2084&auto=format&fit=crop", 
    image_alt_text="A team collaborating in a modern office, representing mission and goals",
    font_family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    background_color_left="#F5EBE0",
    text_color_title="#4E443F",
    text_color_top="#4E443F",
    text_color_subtitle="#475569",
    slide_background_color="#FDFCFB"
):
    """
    Generates a mission slide with an adjusted layout: smaller titles and a larger, more prominent description area.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en"> 
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mission and Goals - Adjusted Layout</title>
    <style>
        :root {{
            --base-font-size: 16px; 
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            font-size: var(--base-font-size);
        }}
        
        .slide-container {{
            width: 100vw;
            height: 100vh;
            background-color: {slide_background_color}; 
            display: flex;
            overflow: hidden;
        }}
        
        .left-column {{
            /* ĐÃ SỬA ĐỔI: Tăng không gian cho cột văn bản (từ 2 thành 3) */
            flex: 3; 
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow-y: auto; 
        }}

        .left-column-top-content {{
            background-color: {background_color_left};
            padding: 3rem 4rem; /* Điều chỉnh lại padding */
            border-top-right-radius: 1.5rem; 
            border-bottom-right-radius: 1.5rem; 
            /* ĐÃ SỬA ĐỔI: Giảm chiều cao tối thiểu để nhường không gian cho description */
            min-height: 45vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .top-text {{
            /* ĐÃ SỬA ĐỔI: Giảm kích thước chữ */
            font-size: 1.3rem;
            color: {text_color_top};
            margin-bottom: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.05em;
        }}
        
        .main-title {{
            /* ĐÃ SỬA ĐỔI: Giảm kích thước chữ của tiêu đề chính */
            font-size: clamp(3rem, 5vw, 5rem); 
            color: {text_color_title};
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 1rem;
        }}
        
        .subtitle-text {{
            /* ĐÃ SỬA ĐỔI: Tăng kích thước chữ của description và padding */
            font-size: 1.85rem; 
            color: {text_color_subtitle};
            line-height: 1.7;
            padding: 3rem 4rem; 
            flex-grow: 1;
            font-weight: 400;
        }}
        
        .right-column {{
            /* ĐÃ SỬA ĐỔI: Giữ nguyên flex: 1 để cột trái rộng hơn */
            flex: 1; 
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            padding: 2rem; 
        }}
        
        .right-column img {{
            display: block;
            width: 100%; 
            height: 100%; 
            object-fit: cover; 
            border-radius: 1rem; 
        }}

        @media (max-width: 48rem) {{ 
            .slide-container {{
                flex-direction: column;
            }}
            .left-column, .right-column {{
                flex: none; /* Reset flex ratio on mobile */
            }}
            .left-column {{
                order: 1;
                width: 100%; 
                height: auto; 
            }}
            .left-column-top-content {{
                border-radius: 0; 
                padding: 2.5rem 2rem;
                min-height: 0; 
            }}
            .main-title {{
                font-size: clamp(2rem, 7vw, 2.8rem);
            }}
            .subtitle-text {{
                font-size: 1.1rem;
                padding: 2rem;
            }}
            .right-column {{
                order: 2;
                width: 100%; 
                height: 40vh; 
                padding: 1.5rem; 
            }}
        }}

    </style>
</head>
<body>
    <div class="slide-container">
        <div class="left-column">
            <div class="left-column-top-content">
                <p class="top-text">{top_text}</p>
                <h1 class="main-title">{title}</h1>
            </div>
            <p class="subtitle-text">{subtitle}</p>
        </div>
        <div class="right-column">
            <img src="{image_url}" alt="{image_alt_text}">
        </div>
    </div>
</body>
</html>"""
    return html_code

#----------------------SLIDE CHUYỂN SLIDE
def generate_geometric_transition_slide(
    headline="TRANSITION HEADLINE",
    subtitle="Let's start with the first set of slides",
    font_family="'Poppins', sans-serif",
    bg_color="#0F172A",
    primary_text_color="#FFFFFF",
    subtitle_color="#67E8F9"
):
    """
    Generates a modern, dynamic transition slide with colorful geometric shapes.
    Features a dark background with high-contrast, centered text. Ideal for tech
    or creative presentations.
    """
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Geometric Transition Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
            color: {primary_text_color};
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            position: relative;
        }}

        .text-content {{
            z-index: 10;
            max-width: 90%;
            width: 100%;
        }}

        .headline {{
            font-size: clamp(6rem, 10vw, 8rem) !important;
            font-weight: 700;
            text-transform: uppercase;
            line-height: 1.25;
            margin-bottom: 3rem;
            display: block;
            width: 100%;
        }}

        .subtitle {{
            font-size: 3.5rem !important;
            font-weight: 500;
            color: {subtitle_color};
            line-height: 1.5;
            display: block;
            width: 100%;
        }}

        /* --- Geometric Shapes --- */
        .shape-cluster {{
            position: absolute;
            width: 40%;
            height: 40%;
            pointer-events: none;
        }}

        .shape-cluster.top-right {{
            top: 0;
            right: 0;
        }}

        .shape-cluster.bottom-left {{
            bottom: 0;
            left: 0;
        }}

        .shape {{
            position: absolute;
            transform-origin: center center;
            transform: skewX(-20deg) rotate(15deg);
        }}

        /* Top-Right Shapes Palette */
        .shape-tr-1 {{ width: 10rem; height: 10rem; background-color: #34D399; opacity: 0.9; top: 6rem; right: 5rem; z-index: 2; }}
        .shape-tr-2 {{ width: 12rem; height: 12rem; background-color: #6366F1; opacity: 0.8; top: 10rem; right: 9rem; z-index: 1; }}
        .shape-tr-3 {{ width: 8rem; height: 8rem; background: linear-gradient(45deg, #F87171, #FBBF24); opacity: 1; top: 16rem; right: 5rem; z-index: 3; }}
        .shape-tr-4 {{ width: 9rem; height: 9rem; background-color: #1E3A8A; opacity: 0.5; top: 3rem; right: 13rem; z-index: 0; }}

        /* Bottom-Left Shapes Palette */
        .shape-bl-1 {{ width: 8rem; height: 8rem; background-color: #34D399; opacity: 0.7; bottom: 10rem; left: 3rem; z-index: 2; }}
        .shape-bl-2 {{ width: 7rem; height: 7rem; background-color: #FBBF24; opacity: 0.9; bottom: 7rem; left: 8rem; z-index: 3; }}
        .shape-bl-3 {{ width: 11rem; height: 11rem; background-color: #A78BFA; opacity: 1; bottom: 2rem; left: 11rem; z-index: 2; }}
        .shape-bl-4 {{ width: 10rem; height: 10rem; background: linear-gradient(45deg, #EF4444, #FB923C); opacity: 1; bottom: 2rem; left: 5rem; z-index: 4; }}
        .shape-bl-5 {{ width: 9rem; height: 9rem; background-color: #1E3A8A; opacity: 0.8; bottom: 9rem; left: 7rem; z-index: 1; }}
        .shape-bl-6 {{ width: 6rem; height: 6rem; background-color: #60A5FA; opacity: 0.4; bottom: 14rem; left: 2rem; z-index: 0; }}

        @media (max-width: 48rem) {{
            .shape-cluster {{ transform: scale(0.7); }}
            .top-right {{ top: -5rem; right: -5rem; }}
            .bottom-left {{ bottom: -5rem; left: -5rem; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="shape-cluster top-right">
            <div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3"></div><div class="shape shape-tr-4"></div>
        </div>
        <div class="shape-cluster bottom-left">
            <div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div><div class="shape shape-bl-4"></div><div class="shape shape-bl-5"></div><div class="shape shape-bl-6"></div>
        </div>
        <div class="text-content">
            <h2 class="headline">{headline}</h2>
            <p class="subtitle">{subtitle}</p>
        </div>
    </div>
</body>
</html>"""
    return html_code

def generate_transition_slide_2(
    main_headline="HEADLINE",
    subtitle="Content",
    font_family_heading="'Patrick Hand', cursive",
    font_family_body="'Lato', sans-serif",
    number_color="#F37A59",
    text_color="#2C3E50",
    bg_url="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png"
):
    """
    Generates a doodle-themed transition slide optimized for 1920x1080 screenshots
    with large, impactful fonts for bold and clear section breaks.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transition Slide - Large Font</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        /* OVERRIDE EDITOR BACKGROUND - HIGHEST SPECIFICITY */
        div[style*="background: white"], 
        div[style*="background: #FFFFFF"],
        div[style*="background-color: white"],
        div[style*="background-color: #FFFFFF"],
        #canvas,
        [data-bg*="#FFFFFF"] {{
            background: url('{bg_url}') repeat center !important;
            background-color: #FFFFFF !important;
        }}
        html#html.html {{ 
            font-size: 16px !important; 
            width: 1920px !important; 
            height: 1080px !important;
            background-color: #FFFFFF !important;
            background-image: url('{bg_url}') !important;
            background-repeat: repeat !important;
            background-position: center !important;
            background-size: auto !important;
        }}
        
        body#body.body, html#html.html {{
            height: 1080px !important;
            width: 1920px !important;
            font-family: {font_family_body} !important;
            color: {text_color} !important;
            overflow: hidden !important;
            background-color: #FFFFFF !important;
            background-image: url('{bg_url}') !important;
            background-repeat: repeat !important;
            background-position: center !important;
            background-size: auto !important;
        }}

        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 80px 120px;
            background: transparent !important;
        }}

        .text-box {{
            min-width: 70%;
            min-height: 40%;
            transform: scale(1.4);
            text-align: center;
        }}

        .main-headline {{
            font-family: {font_family_heading};
            font-size: 80px;
            color: {text_color};
            text-transform: uppercase;
            font-weight: 600;
            line-height: 1.1;
            margin-bottom: 120px;
            max-width: 1400px;
        }}

        .subtitle {{
            font-size: 40px;
            font-weight: 400;
            line-height: 1.6;
            max-width: 1200px;
        }}

        /* Content wrapper for scaling */
        .content-wrapper {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 1920px;
            height: 1080px;
            overflow: visible;
            background: transparent !important;
        }}
        
        .outer-wrapper {{
            padding: 0;
            box-sizing: border-box;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
            background: transparent !important;
        }}
    </style>
</head>
<body>
    <div class="outer-wrapper">
        <div class="content-wrapper">
            <div class="slide-container">
                <h1 class="main-headline">{main_headline}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_dusk_transition_slide(
    headline="Transition Headline",
    subtitle="Let's start with the first set of slides",
    font_family="'Nunito', sans-serif",
    headline_color="#2C3E50",
    subtitle_color="#4A5568",
    number_color="#FDE68A",
    sky_top_color="#6B4F9B",
    sky_mid_color="#C07CB6",
    sky_bottom_color="#F6B17B",
    grid_dot_color="rgba(255, 255, 255, 0.3)"
):
    """
    Generates a minimalist, tech-themed transition slide with a dusk color palette.
    This version is static, with launching rockets removed.
    """
    
    # ĐÃ XÓA: Toàn bộ phần cấu hình và HTML của tên lửa đã được loại bỏ.
    rockets_html = ""

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minimalist Dusk Transition</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            text-align: center;
            background-image: 
                radial-gradient(circle, {grid_dot_color} 1px, transparent 1px),
                linear-gradient(to bottom, {sky_top_color}, {sky_mid_color}, {sky_bottom_color});
            background-size: 20px 20px, 100% 100%;
        }}
        
        /* --- ĐÃ XÓA: Toàn bộ phần CSS của tên lửa --- */

        .headline {{
            font-size: 5rem !important;
            font-weight: 700;
            color: {headline_color};
            line-height: 1.25;
            margin: 0 auto 3rem auto;
            text-align: center !important;
            display: block;
            width: 100%;
            padding: 0 100px;
        }}

        .subtitle {{
            font-size: 3rem !important;
            font-weight: 400;
            color: {subtitle_color};
            line-height: 1.5;
            margin: 0 auto 0 auto;
            text-align: center !important;
            display: block;
            width: 100%;
            padding: 0 100px;
        }}

    </style>
</head>
<body>
    <div class="slide-container">
        <!-- {rockets_html} bây giờ là chuỗi rỗng -->
        {rockets_html}
        <h1 class="headline">{headline}</h1>
        <p class="subtitle">{subtitle}</p>
    </div>
</body>
</html>"""
    
    return html_code

def generate_memphis_transition_slide(
    headline="Transition headline",
    subtitle="Let's start with the first set of slides",
    font_family_headline="'Lora', serif",
    font_family_body="'Lato', sans-serif",
    top_panel_bg="#19114B",
    bottom_panel_bg="#403271",
    palette=["#F87171", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"]
):
    """
    Generates a vibrant, retro, and STATIC 'Memphis-style' transition slide.
    The rotating icon animation has been removed.
    """
    svg_patterns = f"""<svg width="0" height="0" style="position:absolute;"><defs><pattern id="pattern-dots" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="2" fill="{palette[3]}" /></pattern><pattern id="pattern-stripes" x="0" y="0" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="{palette[0]}" stroke-width="4" /></pattern></defs></svg>"""
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Memphis Transition Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&family=Lora:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }} html {{ font-size: 16px; }}
        body, html {{ height: 100vh; width: 100vw; overflow: hidden; font-family: {font_family_body}; }}
        .slide-container {{ width: 100%; height: 100%; display: flex; flex-direction: column; position: relative; }}
        .top-panel, .bottom-panel {{ flex: 1; position: relative; overflow: hidden; }}
        .top-panel {{ background-color: {top_panel_bg}; display: flex; justify-content: center; align-items: flex-end; padding-bottom: 5rem; }}
        .bottom-panel {{ background-color: {bottom_panel_bg}; }}
        .text-content {{
            text-align: center;
            transform: scale(1.3);
            min-width: 50vw;
            min-height: 25vh; 
        }}
        .section-number {{ font-family: {font_family_headline}; font-size: 3rem; font-weight: 400; color: {palette[3]}; opacity: 0.8; }}
        .headline {{ font-family: {font_family_headline}; font-size: 4rem; font-weight: 700; margin-bottom: 5rem ; color: #FFFFFF; }}
        .subtitle {{font-size: 2rem; font-weight: 500; margin-bottom: 8rem; color: {palette[1]}; }}
        .shape {{ position: absolute; }}
        .shape-tl-1 {{ width: 8rem; height: 8rem; background: url(#pattern-dots); top: 4rem; left: 6rem; border-radius: 50%; opacity: 0.8; }}
        .shape-tl-2 {{ width: 0; height: 0; border-left: 3rem solid transparent; border-right: 3rem solid transparent; border-bottom: 5rem solid {palette[0]}; top: 12rem; left: 3rem; transform: rotate(-25deg); }}
        .shape-tl-3 {{ width: 5rem; height: 5rem; border: 3px solid {palette[4]}; top: 2rem; left: 1rem; clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%); }}
        .shape-tr-1 {{ width: 7rem; height: 7rem; border-radius: 50%; border: 3px dashed {palette[1]}; top: 3rem; right: 8rem; }}
        .shape-tr-2 {{ width: 6rem; height: 6rem; background: {palette[2]}; opacity: 0.5; top: 1rem; right: 2rem; clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%); transform: rotate(20deg); }}
        .shape-tr-3 {{ width: 9rem; height: 9rem; background: url(#pattern-stripes); border-radius: 50%; top: 8rem; right: 3rem; transform: rotate(45deg); opacity: 0.9; }}
        .shape-bl-1 {{ width: 0; height: 0; border-left: 4rem solid transparent; border-right: 4rem solid transparent; border-bottom: 7rem solid {palette[1]}; bottom: 2rem; left: 1rem; transform: rotate(15deg) scaleX(-1); }}
        .shape-bl-2 {{ width: 6rem; height: 6rem; border: 3px dashed {palette[2]}; border-radius: 50%; bottom: 8rem; left: 9rem; }}
        .shape-bl-3 {{ width: 4rem; height: 4rem; background-color: {palette[0]}; bottom: 1rem; left: 12rem; transform: rotate(30deg); }}
        .shape-br-1 {{ width: 5rem; height: 5rem; background-color: {palette[3]}; border-radius: 50%; bottom: 2rem; right: 1rem; }}
        .shape-br-2 {{ width: 9rem; height: 9rem; background: url(#pattern-dots); bottom: 6rem; right: 5rem; clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%); transform: rotate(-15deg); }}
        .shape-br-3 {{ width: 0; height: 0; border-left: 2rem solid transparent; border-right: 2rem solid transparent; border-bottom: 3.5rem solid {palette[4]}; bottom: 1rem; right: 10rem; transform: rotate(45deg); opacity: 0.7;}}
    </style>
</head>
<body>
    {svg_patterns}
    <div class="slide-container">
        <div class="top-panel"><div class="text-content"><h2 class="headline">{headline}</h2><p class="subtitle">{subtitle}</p></div><div class="shape shape-tl-1"></div><div class="shape shape-tl-2"></div><div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3"></div></div>
        <div class="bottom-panel"><div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div><div class="shape shape-br-1"></div><div class="shape shape-br-2"></div><div class="shape shape-br-3"></div></div>
    </div>
</body>
</html>"""
    return html_code

def generate_pushpin_section_header(
    main_title="Add a Section Header",
    font_family="'Poppins', sans-serif",
    # ĐÃ THAY ĐỔI: Bảng màu mới tối giản và chuyên nghiệp
    bg_color="#FDFCFB",
    text_color="#1F2937",    # Xám đen
    accent_color="#1F2937"   # Dùng cùng màu cho sự đồng nhất
):
    """
    Generates a minimalist and sophisticated section header slide, featuring a central
    title that elegantly intersects with a decorative horizontal line.
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Section Header - Minimalist Design</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        /* OVERRIDE EDITOR BACKGROUND - HIGHEST SPECIFICITY */
        div[style*="background: white"], 
        div[style*="background: #FFFFFF"],
        div[style*="background-color: white"],
        div[style*="background-color: #FFFFFF"],
        #canvas,
        [data-bg*="#FFFFFF"] {{
            background: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png') repeat center !important;
            background-color: {bg_color} !important;
        }}
        
        html#html.html {{ 
            font-size: 16px !important;
            height: 100vh !important;
            width: 100vw !important;
            font-family: {font_family} !important;
            overflow: hidden !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            background-color: {bg_color} !important;
            background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png') !important;
            background-repeat: repeat !important;
            background-position: center !important;
        }}
        
        body#body.body, html#html.html {{
            height: 100vh !important;
            width: 100vw !important;
            font-family: {font_family} !important;
            overflow: hidden !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            background-color: {bg_color} !important;
            background-image: url('https://www.toptal.com/designers/subtlepatterns/uploads/paper.png') !important;
            background-repeat: repeat !important;
            background-position: center !important;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }}
        
        /* ĐÃ THAY ĐỔI: Container cho toàn bộ khối tiêu đề và đường kẻ */
        .title-block {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            max-width: 70rem;
        }}
        
        /* Đường kẻ trang trí */
        .divider-line {{
            position: absolute;
            width: 100%;
            height: 6px;
            background-color: {accent_color};
            z-index: 1;
        }}

        .main-title {{
            font-size: 6rem !important;
            color: {text_color};
            font-weight: 800;
            line-height: 1.2;
            text-align: center !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background-color: {bg_color};
            padding: 0 3rem;
            z-index: 2;
            display: block;
            width: auto;
            margin: 0 auto;
            position: relative;
        }}

        /* Các chấm trang trí */
        .dot {{
            width: 1.5rem;
            height: 1.5rem;
            background-color: {accent_color};
            border-radius: 50%;
            z-index: 3;
        }}

        .left-dot {{
            margin-right: 3rem;
        }}

        .right-dot {{
            margin-left: 3rem;
        }}

    </style>
</head>
<body id="body" class="body">
    <div class="slide-container">
        <div class="title-block">
            <div class="dot left-dot"></div>
            <div class="divider-line"></div>
            <h1 class="main-title">{main_title}</h1>
            <div class="dot right-dot"></div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_section_header_slide(
    header_text="Add a Section Header",
    font_family="'Poppins', sans-serif",
    bg_color="#F8FAFC",
    text_color="#1E293B",
    gradient_color_1="#A78BFA",
    gradient_color_2="#F472B6",
    gradient_color_3="#7DD3FC"
):
    """
    Generates a vibrant and STATIC section header slide, featuring a soft aurora background.
    Animated shapes have been removed.
    """
    
    # ĐÃ XÓA: Toàn bộ phần HTML của các hình khối đã được loại bỏ.
    shapes_svg_html = ""

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Section Header Slide - Geometric shapes</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
            position: relative;
        }}

        .graphic-background {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            overflow: hidden; z-index: 1;
        }}
        .circle {{
            position: absolute; border-radius: 50%;
            background: linear-gradient(135deg, {gradient_color_1}, {gradient_color_2}, {gradient_color_3});
            filter: blur(120px);
            opacity: 0.5;
        }}
        .circle-1 {{ width: 30rem; height: 30rem; top: -10rem; left: -10rem; }}
        .circle-2 {{ width: 30rem; height: 30rem; bottom: -15rem; right: -15rem; }}

        .slide-container {{
            width: 100%; height: 100%; display: flex;
            justify-content: center; align-items: center;
            padding: 4rem; position: relative;
            z-index: 3;
        }}
        
        .header-text {{
            font-size: clamp(3.5rem, 8vw, 6.5rem);
            font-weight: 800;
            line-height: 1.15;
            color: {text_color};
            text-align: center;
            max-width: 20ch;
        }}

        /* ĐÃ XÓA: Toàn bộ phần CSS cho các hình khối động đã được loại bỏ. */

    </style>
</head>
<body>
    <div class="graphic-background">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
    </div>
    <!-- {shapes_svg_html} sẽ là chuỗi rỗng -->
    {shapes_svg_html}
    <div class="slide-container">
        <h1 class="header-text">{header_text}</h1>
    </div>
</body>
</html>"""
    
    return html_code


def generate_intro_slide(
    main_title="Main Title",
    subtitle1="Subtitle1",
    subtitle2="Subtitle2",
    main_bg_color="#ffffff",
    accent_bg_color="#6ea88a",
    text_box_bg_color="#c5e6b8",
    title_color="#333333",
    subtitle_color="#555555",
    line_color="#e6c35c",
    font_family="'Segoe UI', Arial, sans-serif",
    main_title_font_style="italic",
    image_url="Image/generate_intro_slide1/Default_1.png"
):
    """
    Tạo slide HTML với thiết kế marketing có nền tràn viền như các slide khác.
    Các tham số kích thước nên được truyền vào dưới dạng chuỗi với đơn vị REM.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            background-color: {accent_bg_color};
            overflow: hidden;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            position: relative;
            background-color: {accent_bg_color};
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
            display: flex;
        }}
        
        .left-content {{
            flex: 0 0 60%;
            height: 100%;
            position: relative;
            background-color: {main_bg_color};
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .right-content {{
            flex: 0 0 40%;
            height: 100%;
            background-color: {accent_bg_color};
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .image-container {{
            width: 80%;
            height: 70%;
            background-color: white;
            border-radius: 1rem;
            box-shadow: 0 1rem 2rem rgba(0,0,0,0.15);
            overflow: hidden;
            position: relative;
            z-index: 3;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .accent-bar-top {{
            position: absolute;
            top: 0;
            left: 0;
            width: 4rem; /* 64px - larger for better visibility */
            height: 2rem; /* 32px */
            background-color: {text_box_bg_color};
            z-index: 1;
        }}
        
        .accent-bar-middle {{
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 4rem; /* 64px - larger */
            background-color: {text_box_bg_color};
            transform: translateY(-50%);
            z-index: 1;
        }}
        
        .content-box {{
            background-color: {text_box_bg_color};
            padding: 5rem; /* 80px - much larger padding */
            border-radius: 0.5rem;
            z-index: 2;
            position: relative;
            width: 90%; /* 90% of left-content width */
            height: 85%; /* 85% of left-content height */
            max-width: none; /* Remove max-width constraint */
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .main-title {{
            font-size: 5.5rem !important;
            color: {title_color};
            margin: 0 0 3rem 0;
            font-weight: bold;
            font-style: {main_title_font_style};
            line-height: 1.2;
            text-align: center !important;
            display: block;
            width: 100%;
        }}
        
        .subtitle {{
            font-size: 2.5rem !important;
            color: {subtitle_color};
            margin: 1rem 0;
            line-height: 1.4;
            text-align: center !important;
            display: block;
            width: 100%;
        }}
        
        .divider {{
            width: 80%; /* 80% width instead of 100% */
            height: 0.25rem; /* 4px - thicker */
            background-color: {line_color};
            margin: 3rem auto 0 auto; /* 48px top margin, centered */
            border-radius: 0.125rem;
        }}
        
        .decorative-element {{
            position: absolute;
            background-color: {text_box_bg_color};
            opacity: 0.5;
            z-index: 1;
        }}
        
        .deco-1 {{
            top: 1rem;
            right: 1rem;
            width: 4rem; /* 64px - smaller so they don't interfere with image */
            height: 4rem;
            border-radius: 50%;
        }}
        
        .deco-2 {{
            bottom: 1rem;
            right: 1rem;
            width: 3rem; /* 48px - smaller square */
            height: 3rem;
            transform: rotate(45deg);
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="slide-inner-container">
            <!-- Accent bars -->
            <div class="accent-bar-top"></div>
            <div class="accent-bar-middle"></div>
            
            <!-- Left content area -->
            <div class="left-content">
                <div class="content-box">
                    <h1 class="main-title">{main_title}</h1>
                    <p class="subtitle">{subtitle1}</p>
                    <p class="subtitle">{subtitle2}</p>
                    <div class="divider"></div>
                </div>
            </div>
            
            <!-- Right content area -->
            <div class="right-content">
                <div class="image-container">
                    <img src="{image_url}" alt="slide visual">
                </div>
                <div class="decorative-element deco-1"></div>
                <div class="decorative-element deco-2"></div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
    
#------------------------SLIDE CONTENT
def generate_content_slide(
    main_title="CONTENT",
    items=None,
    main_title_color="#555555",
    number_color="#a2c4c9",
    item_title_color="#555555",
    background_color="#ffffff",
    accent_color="#a2c4c9",
    border_width="30px",
    font_family="Arial, sans-serif",
    num_columns=3,
    num_rows=2,
):
    """
    Generates an HTML slide with a main title and a grid of numbered items.
    
    Parameters:
    - main_title: The main title of the slide
    - items: List of item titles (default is ["Your Title Here"] * 6)
    - main_title_font_size: Font size for the main title
    - number_font_size: Font size for the item numbers
    - item_title_font_size: Font size for the item titles
    - main_title_color: Color for the main title
    - number_color: Color for the item numbers
    - item_title_color: Color for the item titles
    - background_color: Background color of the slide
    - accent_color: Color for the corner accents
    - border_width: Width of the border around the slide
    - font_family: Font family for the slide
    - num_columns: Number of columns in the grid
    - num_rows: Number of rows in the grid
    
    Returns:
    - HTML code for the content slide
    """
    
    # Default values if not provided
    if items is None:
        items = ["Your Title Here"] * 6
    
    # Ensure we have enough items
    num_items = num_columns * num_rows
    if len(items) < num_items:
        items.extend(["Your Title Here"] * (num_items - len(items)))
    elif len(items) > num_items:
        items = items[:num_items]
    
    # Generate HTML for grid items
    grid_items_html = ""
    for i in range(num_items):
        item_number = str(i + 1).zfill(2)
        item_title = items[i]
        
        grid_items_html += f"""
        <div class="content-card">
            <div class="item-number">{item_number}</div>
            <div class="item-title">{item_title}</div>
        </div>
        """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body {{
            font-family: {font_family};
            background: {accent_color};
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}

        .slide-container {{
            width: 95vw;
            height: 90vh;
            max-width: 1400px;
            max-height: 900px;
            background: {background_color};
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            padding: 4rem;
            position: relative;
        }}

        .slide-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, {accent_color}, {number_color});
            border-radius: 20px 20px 0 0;
        }}
        
        .main-title {{
            font-size: 5rem !important;
            font-weight: 700;
            color: {main_title_color};
            text-align: center !important;
            margin-bottom: 3rem;
            letter-spacing: 0.02em;
            position: relative;
            display: block;
            width: 100%;
        }}

        .main-title::after {{
            content: '';
            position: absolute;
            bottom: -1rem;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: {number_color};
            border-radius: 2px;
        }}
        
        .grid-container {{
            display: grid;
            grid-template-columns: repeat({num_columns}, 1fr);
            grid-template-rows: repeat({num_rows}, 1fr);
            gap: 2rem;
            flex: 1;
            padding: 1rem 0;
        }}
        
        .content-card {{
            background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7));
            border: 2px solid {accent_color}20;
            border-radius: 16px;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            position: relative;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
            overflow: hidden;
        }}

        .content-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, {number_color}, {accent_color});
        }}
        
        .item-number {{
            font-size: 3rem !important;
            font-weight: 700;
            color: {number_color};
            margin-bottom: 1rem;
            line-height: 1;
            position: relative;
            text-align: center !important;
            display: block;
        }}

        .item-number::after {{
            content: '';
            position: absolute;
            bottom: -0.5rem;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 2px;
            background: {number_color}40;
            border-radius: 1px;
        }}
        
        .item-title {{
            font-size: 2rem !important;
            font-weight: 500;
            color: {item_title_color};
            line-height: 1.4;
            text-align: center !important;
            display: block;
            width: 100%;
        }}

        /* Responsive Design */
        @media (max-width: 75rem) {{
            .slide-container {{ padding: 3rem; }}
            .main-title {{ font-size: 3rem; }}
            .item-number {{ font-size: 3rem; }}
            .item-title {{ font-size: 1.1rem; }}
        }}

        @media (max-width: 50rem) {{
            .slide-container {{ 
                width: 98vw;
                height: 95vh;
                padding: 2rem;
            }}
            .main-title {{ 
                font-size: 2.5rem; 
                margin-bottom: 2rem;
            }}
            .grid-container {{ 
                grid-template-columns: repeat(2, 1fr);
                grid-template-rows: repeat(3, 1fr);
                gap: 1.5rem;
            }}
            .content-card {{ padding: 1.5rem; }}
            .item-number {{ font-size: 2.5rem; }}
            .item-title {{ font-size: 1rem; }}
        }}

        @media (max-width: 30rem) {{
            .grid-container {{ 
                grid-template-columns: 1fr;
                grid-template-rows: repeat(6, 1fr);
                gap: 1rem;
            }}
            .content-card {{ padding: 1rem; }}
            .item-number {{ font-size: 2rem; }}
            .item-title {{ font-size: 0.9rem; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <h1 class="main-title">{main_title}</h1>
        
        <div class="grid-container">
            {grid_items_html}
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_comparison_slide(
    main_title="Your Title Here",
    left_title="Your Title Here",
    right_title="Your Title Here",
    left_text="Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience. Presentation are communication tools that can be used as demontrations, lectures, reports, and more.",
    right_text="Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience. Presentation are communication tools that can be used as demontrations, lectures, reports, and more.",
    left_icon="gavel",  # Options: "gavel", "custom"
    right_icon="scales",  # Options: "scales", "custom"
    custom_left_icon="",  # Custom SVG code if left_icon is "custom"
    custom_right_icon="",  # Custom SVG code if right_icon is "custom"
    title_color="#555555",
    text_color="#555555",
    icon_color="#a2c4c9",
    background_color="#ffffff",
    accent_color="#a2c4c9",
    divider_color="#555555",
    font_family="Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title and two comparison columns with icons.
    The slide has a border design that matches the image exactly.
    
    Parameters:
    - main_title: The main title of the slide
    - left_title: Title for the left column
    - right_title: Title for the right column
    - left_text: Text content for the left column
    - right_text: Text content for the right column
    - left_icon: Icon for the left column ("gavel" or "custom")
    - right_icon: Icon for the right column ("scales" or "custom")
    - custom_left_icon: Custom SVG code for left icon if left_icon is "custom"
    - custom_right_icon: Custom SVG code for right icon if right_icon is "custom"
    - main_title_font_size: Font size for the main title
    - column_title_font_size: Font size for the column titles
    - text_font_size: Font size for the text content
    - title_color: Color for all titles
    - text_color: Color for all text content
    - icon_color: Color for the icons
    - background_color: Background color of the slide
    - accent_color: Color for the corner accents
    - divider_color: Color for the divider line
    - font_family: Font family for the slide
    
    Returns:
    - HTML code for the comparison slide
    """
    
    # Define the SVG icons
    gavel_icon = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="70" height="70" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 13L3 2M14 13L9 18M14 13L16 11L20 15L18 17M14 6L17 9M9 1L3 7M20 21H4"/>
    </svg>"""
    
    scales_icon = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="70" height="70" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 3v18M8 21h8M7 8l-4 4M17 8l4 4M5 12a2 2 0 1 0 4 0 2 2 0 1 0-4 0M15 12a2 2 0 1 0 4 0 2 2 0 1 0-4 0"/>
        <path d="M5 12h14"/>
    </svg>"""
    
    # Select the appropriate icons
    if left_icon == "gavel":
        left_icon_html = gavel_icon
    elif left_icon == "custom":
        left_icon_html = custom_left_icon
    else:
        left_icon_html = gavel_icon
        
    if right_icon == "scales":
        right_icon_html = scales_icon
    elif right_icon == "custom":
        right_icon_html = custom_right_icon
    else:
        right_icon_html = scales_icon
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparison Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            background-color: {accent_color};
            color: {title_color};
            overflow: hidden;
        }}

        .slide-background {{
            position: absolute;
            left: 120px;
            top: 80px;
            width: 1680px;
            height: 920px;
            background-color: {background_color};
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .main-title {{
            position: absolute;
            left: 200px;
            top: 140px;
            width: 1520px;
            font-size: 80px;
            font-weight: 700;
            color: {title_color};
            text-align: center;
            line-height: 1.2;
        }}
        
        .left-column {{
            position: absolute;
            left: 200px;
            top: 260px;
            width: 730px;
            height: 680px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 50px 40px;
            text-align: center;
        }}
        
        .right-column {{
            position: absolute;
            left: 990px;
            top: 260px;
            width: 730px;
            height: 680px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 50px 40px;
            text-align: center;
        }}
        
        .divider {{
            position: absolute;
            left: 960px;
            top: 280px;
            width: 3px;
            height: 640px;
            border-left: 3px dashed {divider_color};
        }}
        
        .left-icon {{
            margin-bottom: 40px;
        }}
        
        .right-icon {{
            margin-bottom: 40px;
        }}
        
        .left-title {{
            font-size: 45px;
            font-weight: 700;
            color: {title_color};
            text-align: center;
            margin-bottom: 30px;
            line-height: 1.3;
        }}
        
        .right-title {{
            font-size: 45px;
            font-weight: 700;
            color: {title_color};
            text-align: center;
            margin-bottom: 30px;
            line-height: 1.3;
        }}
        
        .left-text {{
            font-size: 30px;
            color: {text_color};
            text-align: center;
            line-height: 1.6;
        }}
        
        .right-text {{
            font-size: 30px;
            color: {text_color};
            text-align: center;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <!-- Background layer -->
    <div class="slide-background"></div>
    
    <!-- Main title -->
    <h1 class="main-title">{main_title}</h1>
    
    <!-- Left column -->
    <div class="left-column">
        <div class="left-icon">
            {left_icon_html}
        </div>
        <h2 class="left-title">{left_title}</h2>
        <p class="left-text">{left_text}</p>
    </div>
    
    <!-- Divider -->
    <div class="divider"></div>
    
    <!-- Right column -->
    <div class="right-column">
        <div class="right-icon">
            {right_icon_html}
        </div>
        <h2 class="right-title">{right_title}</h2>
        <p class="right-text">{right_text}</p>
    </div>
</body>
</html>"""
    
    return html_code

def generate_process_slide(
    main_title="Your Title Here",
    left_title="Your Title Here",
    right_title="Your Title Here",
    left_content="Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience. Presentation are communication tools that can be used as demontrations, lectures, reports, and more.",
    right_content="Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience. Presentation are communication tools that can be used as demontrations, lectures, reports, and more.",
    title_color="#555555",
    left_box_color="#8cbeca",
    right_box_color="#70c5da",
    text_color="#ffffff",
    arrow_color="#f0f0f0",
    background_color="#ffffff",
    accent_color="#a2c4c9",
    border_width="30px",
    font_family="Arial, sans-serif",
    box_width="380px",
    box_height="350px",
    box_border_radius="5px",
):
    """
    Generates an HTML slide with a main title and two process boxes connected by an arrow.
    
    Parameters:
    - main_title: The main title of the slide
    - left_title: Title for the left box
    - right_title: Title for the right box
    - left_content: Content text for the left box
    - right_content: Content text for the right box
    - main_title_font_size: Font size for the main title
    - box_title_font_size: Font size for the box titles
    - content_font_size: Font size for the content text
    - title_color: Color for the main title
    - left_box_color: Background color for the left box
    - right_box_color: Background color for the right box
    - text_color: Color for the text in the boxes
    - arrow_color: Color for the arrow connecting the boxes
    - background_color: Background color of the slide
    - accent_color: Color for the corner accents
    - border_width: Width of the border around the slide
    - font_family: Font family for the slide
    - box_width: Width of each box
    - box_height: Height of each box
    - box_border_radius: Border radius for the boxes
    
    Returns:
    - HTML code for the process slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Process Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body {{
            font-family: {font_family};
            background: {accent_color};
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}

        .slide-container {{
            width: 98vw;
            height: 96vh;
            max-width: 1600px;
            max-height: 1000px;
            background: {background_color};
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            padding: 5rem;
            position: relative;
        }}
        
        .main-title {{
            font-size: 6rem !important;
            font-weight: 700;
            color: {title_color};
            text-align: center !important;
            margin-bottom: 4rem;
            line-height: 1.2;
            display: block;
            width: 100%;
        }}
        
        .boxes-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            flex: 1;
            gap: 2rem;
        }}
        
        .process-box {{
            flex: 1;
            max-width: 650px;
            background: var(--box-color);
            border-radius: 25px;
            padding: 5rem;
            color: {text_color};
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            z-index: 2;
        }}

        .left-box {{
            --box-color: {left_box_color};
        }}
        
        .right-box {{
            --box-color: {right_box_color};
        }}
        
        .box-title {{
            font-size: 3.5rem !important;
            font-weight: 600;
            margin-bottom: 2.5rem;
            text-align: center !important;
            display: block;
            width: 100%;
        }}
        
        .box-content {{
            font-size: 2rem !important;
            line-height: 1.8;
            text-align: center !important;
            display: block;
            width: 100%;
        }}
        
        .arrow-container {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 3;
        }}

        .arrow {{
            width: 100px;
            height: 100px;
            background: {left_box_color};
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .arrow::before {{
            content: '→';
            font-size: 2.8rem !important;
            color: {text_color};
            font-weight: bold;
        }}

     

        /* Responsive Design */
        @media (max-width: 75rem) {{
            .slide-container {{ padding: 3rem; }}
            .main-title {{ font-size: 2.25rem; }}
            .box-title {{ font-size: 1.5rem; }}
            .box-content {{ font-size: 1rem; }}
        }}

        @media (max-width: 50rem) {{
            .slide-container {{ 
                padding: 2rem;
                width: 95vw;
                height: 90vh;
            }}
            .main-title {{ font-size: 2rem; margin-bottom: 2.5rem; }}
            .boxes-container {{ 
                flex-direction: column; 
                gap: 2rem;
            }}
            .process-box {{ 
                max-width: 100%;
                padding: 2rem;
            }}
            .arrow-container {{
                position: relative;
                top: auto;
                left: auto;
                transform: none;
                margin: 1rem 0;
            }}
            .arrow::before {{
                content: '↓';
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <h1 class="main-title">{main_title}</h1>
        
        <div class="boxes-container">
            <!-- Left Process Box -->
            <div class="process-box left-box">
                <h2 class="box-title">{left_title}</h2>
                <p class="box-content">{left_content}</p>
            </div>
            
            <!-- Arrow Connection -->
            <div class="arrow-container">
                <div class="arrow"></div>
            </div>
            
            <!-- Right Process Box -->
            <div class="process-box right-box">
                <h2 class="box-title">{right_title}</h2>
                <p class="box-content">{right_content}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

# form business
def generate_process_steps_slide(
    main_title="Cách tiếp cận đề xuất",
    steps=[
        {
            "image_url": "https://images.unsplash.com/photo-1516321497487-e288fb19713f?q=80&w=2940&auto=format&fit=crop",
            "title": "Thiết lập nền tảng số",
            "description": "Thuyết trình là công cụ giao tiếp có thể dùng để giảng dạy."
        },
        {
            "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
            "title": "Ra mắt các chiến dịch số",
            "description": "Thuyết trình là công cụ giao tiếp có thể dùng để giảng dạy."
        },
        {
            "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=2940&auto=format&fit=crop",
            "title": "Theo dõi kết quả",
            "description": "Thuyết trình là công cụ giao tiếp có thể dùng để giảng dạy."
        }
    ],
    accent_color="#EAD6D6",
    bg_color="#FCFCFC",
    title_color="#1F2937",
    text_heading_color="#374151",
    text_body_color="#6B7280",
    font_family_title="'Playfair Display', serif",
    font_family_body="'Montserrat', sans-serif",
    custom_css=""
):
    """
    Generates a structured, multi-step process or plan slide.
    Features a three-column layout with a title panel, an image strip, and corresponding text.
    """
    
    images_html = ""
    steps_text_html = ""
    for step in steps:
        images_html += f"<img src='{step.get('image_url', '')}' alt='{step.get('title', '')}' class='step-image'>"
        steps_text_html += f"""
        <div class="step-item">
            <h3 class="step-title">{step.get('title', '')}</h3>
            <p class="step-description">{step.get('description', '')}</p>
        </div>
        """

    html_code = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500&family=Montserrat:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{ font-size: 16px; }}
        body, html {{
            margin: 0; padding: 0; height: 100%; width: 100%;
            font-family: {font_family_body};
            overflow: hidden;
            background-color: {bg_color};
        }}
        
        .slide-container {{
            width: 100%; height: 100vh;
            display: flex; align-items: center; justify-content: center;
        }}
        
        .content-wrapper {{
            display: flex;
            width: 100%; height: 100%;
            max-width: 80rem; /* 1280px */
        }}
        
        .title-section {{
            flex: 0 0 30%;
            background-color: {accent_color};
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            box-sizing: border-box;
        }}
        
        .main-title {{
            font-family: {font_family_title};
            font-size: 6rem;
            font-weight: 500;
            font-style: italic;
            color: {title_color};
            line-height: 1.3;
            text-align: center;
        }}
        
        .steps-layout {{
            flex: 1;
            display: flex;
            align-items: center;
            padding: 3rem 4rem;
        }}
        
        .image-strip-section {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 1.5rem;
            height: 100%;
            max-height: 35rem; /* 560px */
        }}
        .step-image {{
            width: 10rem; /* 160px */
            height: 10rem; /* 160px */
            object-fit: cover;
            box-shadow: 0 0.5rem 1.5rem rgba(0,0,0,0.07);
        }}
        
        .steps-text-section {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding-left: 3rem;
            height: 100%;
            max-height: 35rem; /* 560px */
        }}
        .step-item {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .step-title {{
            font-size: 2.4rem;
            font-weight: 500;
            color: {text_heading_color};
            margin: 0 0 0.5rem 0;
        }}
        .step-description {{
            font-size: 1.5rem;
            color: {text_body_color};
            line-height: 1.6;
            margin: 0;
            max-width: 25rem; /* 400px */
        }}

        @media (max-width: 64em) {{ /* 1024px */
            .steps-layout {{ padding: 2rem; }}
            .main-title {{ font-size: 2.5rem; }}
        }}

        @media (max-width: 48em) {{ /* 768px */
            .content-wrapper {{ flex-direction: column; }}
            .title-section {{ flex: 0 0 auto; width: 100%; height: 8rem; }}
            .steps-layout {{ flex-direction: column; padding: 2rem; align-items: flex-start; overflow-y: auto; }}
            .image-strip-section, .steps-text-section {{
                 flex-direction: row; justify-content: flex-start; gap: 1rem;
                 width: 100%; max-height: none; height: auto;
                 padding-left: 0;
            }}
             .image-strip-section {{
                 align-items: flex-start; /* Fix image alignment */
                 flex-wrap: wrap; /* Allow wrapping */
             }}
            .steps-text-section {{
                display: block; /* Change from flex to block */
            }}
            .step-item {{ margin-bottom: 2rem; }}
            .step-image {{ width: 8rem; height: 8rem; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="content-wrapper">
            <div class="title-section">
                <h1 class="main-title">{main_title}</h1>
            </div>
            <div class="steps-layout">
                <div class="image-strip-section">
                    {images_html}
                </div>
                <div class="steps-text-section">
                    {steps_text_html}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_code




def generate_icon_list_slide_2(
    main_title="Giải pháp",
    subtitle="CÁCH TIẾP CẬN ĐA KÊNH",
    items=[
        {
            "icon_svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/></svg>',
            "text": "Hiện diện trực tuyến"
        },
        {
            "icon_svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>',
            "text": "Các chiến dịch số"
        },
        {
            "icon_svg": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M0 8c3.42 0 6.55 1.31 8.83 3.59L12 15l3.17-3.41A12.42 12.42 0 0024 8h-3c-1.93 0-3.68.79-4.95 2.05L12 14.1l-4.05-4.05A6.97 6.97 0 003 8H0z M1 22h22v-2H1v2zm2-2h18v-2H3v2zm2-2h14v-2H5v2z"/></svg>',
            "text": "Hiện diện trực tuyến"
        }
    ],
    accent_color="#EAD6D6",
    bg_color="#FCFCFC",
    title_color="#1F2937",
    subtitle_color="#4B5563",
    text_color="#374151",
    icon_color="#FFFFFF",
    font_family_title="'Playfair Display', serif",
    font_family_body="'Montserrat', sans-serif",
    custom_css=""
):
    """
    Generates a clean, minimalist slide for presenting solutions, features, or key points.
    Features a two-column layout with a large title on the left and a vertical list of icon-text pairs.
    """
    
    list_items_html = ""
    for item in items:
        list_items_html += f"""
        <div class="list-item">
            <div class="icon-container">
                {item.get('icon_svg', '')}
            </div>
            <p class="item-text">{item.get('text', '')}</p>
        </div>
        """

    html_code = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500&family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{ font-size: 16px; }}
        body, html {{
            margin: 0; padding: 0; height: 100%; width: 100%;
            font-family: {font_family_body};
            overflow: hidden;
            background-color: {bg_color};
        }}
        
        .slide-container {{
            width: 100%; height: 100vh;
            display: flex; align-items: center; justify-content: center;
            padding: 4vw; box-sizing: border-box;
        }}
        
        .content-wrapper {{
            display: flex;
            align-items: center;
            width: 100%;
            max-width: 70rem; /* 1120px */
            transform: scale(1.2);
            min-height: 60vh;
        }}
        
        .title-section {{
            flex: 1;
            padding-right: 4rem;
        }}
        
        .main-title {{
            font-family: {font_family_title};
            font-size: 4.5rem;
            font-weight: 700;
            font-style: italic;
            color: {title_color};
            margin-bottom: 2rem;
            line-height: 1.1;
        }}
        
        .subtitle {{
            color: {subtitle_color};
            font-size: 1.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .list-section {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 3rem;
        }}
        
        .list-item {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }}

        .icon-container {{
            flex-shrink: 0;
            width: 7rem;
            height: 7rem;
            background-color: {accent_color};
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .icon-container svg {{
            width: 4rem;
            height: 4rem;
            fill: {icon_color};
        }}
        
        .item-text {{
            font-size: 1.8rem;
            font-weight: 600;
            margin: 0;
            color: {text_color};
            line-height: 7rem;
        }}

        @media (max-width: 48em) {{ /* 768px */
            .content-wrapper {{ flex-direction: column; text-align: center; }}
            .title-section {{ padding-right: 0; margin-bottom: 3rem; }}
            .list-section {{ width: 100%; align-items: flex-start; }}
            .main-title {{ font-size: 3.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="content-wrapper">
            <div class="title-section">
                <h1 class="main-title">{main_title}</h1>
                <h2 class="subtitle">{subtitle}</h2>
            </div>
            <div class="list-section">
                {list_items_html}
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_code




def generate_image_cutout_list_slide(
    list_items=[
        {"title": "Add a main point", "description": "Elaborate on what you want to discuss."},
        {"title": "Add a main point", "description": "Elaborate on what you want to discuss."},
        {"title": "Add a main point", "description": "Elaborate on what you want to discuss."},
        {"title": "Add a main point", "description": "Elaborate on what you want to discuss."}
    ],
    # --- Thiết kế & Màu sắc ---
    background_image_url="https://images.unsplash.com/photo-1541746972996-4e0b0f43e02a?q=80&w=2940&auto=format&fit=crop",
    content_bg_color="#1A1A22",
    text_heading_color="#FFFFFF",
    text_color="#C0C0C0",
    accent_color="#8A63D2",
    line_color="rgba(255, 255, 255, 0.2)",
    # --- Font chữ ---
    font_family_title="'Source Serif 4', serif",
    font_family_body="'Inter', sans-serif",
    custom_css=""
):
    """
    Generates a sophisticated list slide with a unique 'cut-out' effect.
    The main content panel appears to sit on top of a continuous background image.
    """
    
    list_items_html = "".join([
        f"""<div class="list-item">
            <h3 class="item-title">{item.get('title', '')}</h3>
            <p class="item-description">{item.get('description', '')}</p>
        </div>"""
        for item in list_items
    ])

    # SVG for the decorative spinner
    spinner_svg = f'''
    <svg class="decorative-spinner" width="60" height="60" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <g fill="none" stroke="{accent_color}" stroke-width="4">
            {''.join([f'<circle cx="50" cy="50" r="45" stroke-dasharray="2.9 8.8" transform="rotate({i * 15} 50 50)"/>' for i in range(1)])}
        </g>
    </svg>
    '''

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Key Points Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600&family=Inter:wght@400&display=swap" rel="stylesheet">
    <style>
        :root {{ font-size: 16px; }}
        body, html {{
            margin: 0; padding: 0; height: 100%; width: 100%;
            overflow: hidden;
            background-color: #111;
        }}
        
        .slide-container {{
            width: 100%; height: 100vh;
            position: relative;
            background-image: url('{background_image_url}');
            background-size: cover;
            background-position: center;
        }}
        
        .content-panel {{
            position: absolute;
            top: 0;
            right: 0;
            width: 70%;
            height: 100%;
            background-color: {content_bg_color};
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding: 4rem 4rem 4rem 6rem;
            box-sizing: border-box;
        }}
        
        .decorative-spinner {{
            position: absolute;
            top: 2rem;
            right: 3rem;
            animation: spin 10s linear infinite;
        }}


        .list-container {{
            width: 100%;
            max-width: 35rem; /* 560px */
            position: relative;
            padding-left: 1.5rem;
        }}
        
        /* The vertical guide line */
        .list-container::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0.5rem;
            bottom: 0.5rem;
            width: 2px;
            background-color: {line_color};
        }}
        
        .list-item {{
            position: relative;
            padding-left: 3rem;
            margin-bottom: 3.5rem;
        }}
        .list-item:last-child {{ margin-bottom: 0; }}

        /* The custom bullet point */
        .list-item::before {{
            content: '';
            position: absolute;
            left: -0.6rem; /* -(dot_width/2) */
            top: 0.5rem;
            width: 1.2rem;
            height: 1.2rem;
            background-color: {accent_color};
            border-radius: 50%;
        }}
        
        .item-title {{
            font-family: {font_family_title};
            font-size: 2.2rem;
            font-weight: 600;
            color: {text_heading_color};
            margin: 0 0 0.5rem 0;
        }}
        
        .item-description {{
            font-family: {font_family_body};
            font-size: 1.6rem;
            color: {text_color};
            line-height: 1.6;
            margin: 0;
            opacity: 0.9;
        }}

        @media (max-width: 48em) {{
            .content-panel {{
                width: 100%;
                padding: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="content-panel">
            {spinner_svg}
            <div class="list-container">
                {list_items_html}
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_code




def generate_body_slide2(
    # Main parameters
    main_title="MainTitle",
    
    # Content parameters
    subtitle1="SubTitle1",
    content1="Content1",
    subtitle2="SubTitle2",
    content2="Content2",
    subtitle3="SubTitle3",
    content3="Content3",
    
    # Style parameters
    main_bg_color="#ffffff",  # White background
    accent_color="#d5e8b9",   # Light green accent
    title_color="#333333",
    subtitle_color="#333333",
    content_color="#555555",
    font_family="'Segoe UI', Arial, sans-serif",
    image_url="Image/generate_body_slide2/Default_1.png",

    # Icon parameters - SVG paths for each icon
    icon1="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M12 2v6M12 18v4M14.5 8a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0zM16.5 13a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0z"></path></svg>""",  # Lightbulb
    icon2="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>""",  # Target
    icon3="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>""",  # Bar chart
):
    """
    Generates an HTML slide with a main title, large image on the left,
    and three content sections with icons on the right - Full viewport design.
    
    Parameters:
    - main_title: The main title of the slide
    
    Content parameters:
    - subtitle1, subtitle2, subtitle3: Subtitles for each content section
    - content1, content2, content3: Content text for each section
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - accent_color: Color for accents and icon backgrounds
    - title_color: Color for the main title
    - subtitle_color: Color for subtitles
    - content_color: Color for content text
    - title_font_size: Font size for the main title
    - subtitle_font_size: Font size for subtitles
    - content_font_size: Font size for content text
    - font_family: Font family for the slide
    
    Icon parameters:
    - icon1, icon2, icon3: SVG code for each icon
    
    Returns:
    - HTML code for the slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image with Icons Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ 
            font-size: 16px; 
            width: 100vw; 
            height: 100vh;
            overflow: hidden;
        }}
        
        body {{
            font-family: {font_family};
            background-color: {accent_color}; /* Full viewport accent background */
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            padding: 3rem 4rem; /* 48px 64px */
            position: relative;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 2.5rem; /* 40px */
        }}
        
        .title-accent {{
            width: 2.5rem; /* 40px - increased size */
            height: 2.5rem; /* 40px */
            background: linear-gradient(135deg, {accent_color}, rgba(213, 232, 185, 0.8));
            margin-right: 1.25rem; /* 20px */
            border-radius: 0.5rem; /* 8px */
            box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
        }}
        
        .main-title {{
            font-size: 3.5rem; 
            color: {title_color};
            font-weight: 600;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            flex: 1;
            gap: 2.5rem; /* 40px */
        }}
        
        .image-section {{
            flex: 2;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.5rem; /* 24px */
            background: rgba(255,255,255,0.9);
            border-radius: 1rem; /* 16px */
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}
        
        .image-frame {{
            width: 100%;
            height: 100%;
            position: relative;
            overflow: hidden;
            border-radius: 0.75rem; /* 12px */
        }}
        
        .image-accent {{
            position: absolute;
            top: 0;
            left: 0;
            width: 95%;
            height: 95%;
            border: 0.5rem solid {accent_color}; /* 8px */
            border-radius: 0.75rem; /* 12px */
            z-index: 1;
            transition: all 0.3s ease;
        }}
        
        .image-section:hover .image-accent {{
            border-width: 0.75rem; /* 12px - expand on hover */
            background: linear-gradient(45deg, {accent_color}20, transparent);
        }}
        
        .image-container {{
            position: absolute;
            top: 1.5rem; /* 24px */
            left: 1.5rem; /* 24px */
            width: 95%;
            height: 95%;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            overflow: hidden;
            z-index: 2;
            border-radius: 0.75rem; /* 12px */
            transition: transform 0.3s ease;
        }}
        
        .image-section:hover .image-container {{
            transform: scale(1.02); /* subtle zoom on hover */
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 0.75rem; /* 12px */
            transition: transform 0.3s ease;
        }}
        
        .image-section:hover .image-container img {{
            transform: scale(1.05); /* image zoom effect */
        }}
        
        .content-section {{
            flex: 3;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 2rem; /* 32px */
        }}
        
        .content-item {{
            display: flex;
            align-items: flex-start;
            background: rgba(255,255,255,0.9);
            padding: 1.5rem; /* 24px */
            border-radius: 1rem; /* 16px */
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border-left: 0.25rem solid {accent_color}; /* 4px */
            position: relative;
            overflow: hidden;
        }}
        
        .content-item:hover {{
            transform: translateX(0.5rem); /* 8px horizontal shift */
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.15);
            border-left-width: 0.5rem; /* 8px - expand border */
        }}
        
        .content-item::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 0.25rem; /* 4px */
            height: 100%;
            background: linear-gradient(to bottom, {accent_color}, rgba(213, 232, 185, 0.5));
            transform: scaleY(0);
            transition: transform 0.3s ease;
            transform-origin: top;
        }}
        
        .content-item:hover::before {{
            transform: scaleY(1);
        }}
        
        .icon-container {{
            width: 4rem; /* 64px - increased size */
            height: 4rem; /* 64px */
            background: linear-gradient(135deg, {accent_color}, rgba(213, 232, 185, 0.8));
            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: 1.5rem; /* 24px */
            flex-shrink: 0;
            border-radius: 0.75rem; /* 12px */
            box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .content-item:hover .icon-container {{
            transform: scale(1.1) rotate(5deg); /* hover effect */
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15);
        }}
        
        .icon-container svg {{
            width: 2rem; /* 32px - increased size */
            height: 2rem; /* 32px */
            stroke: #333333;
            transition: all 0.3s ease;
        }}
        
        .content-item:hover .icon-container svg {{
            stroke: #ffffff;
            transform: scale(1.1);
        }}
        
        .content-text {{
            flex: 1;
        }}
        
        .subtitle {{
            font-size: 2.2rem;
            color: {subtitle_color};
            margin: 0 0 0.75rem 0; /* 12px */
            font-weight: 600;
            position: relative;
        }}
        
        .subtitle::after {{
            content: '';
            position: absolute;
            bottom: -0.25rem; /* -4px */
            left: 0;
            width: 2rem; /* 32px */
            height: 0.125rem; /* 2px */
            background: {accent_color};
            border-radius: 0.0625rem; /* 1px */
            transition: width 0.3s ease;
        }}
        
        .content-item:hover .subtitle::after {{
            width: 4rem; /* 64px - expand underline on hover */
        }}
        
        .content {{
            font-size: 1.5rem;
            color: {content_color};
            margin: 0;
            line-height: 1.6;
            padding: 0.75rem; /* 12px */
            background: rgba(213, 232, 185, 0.1);
            border-radius: 0.5rem; /* 8px */
            transition: all 0.3s ease;
        }}
        
        .content-item:hover .content {{
            background: rgba(213, 232, 185, 0.2);
            transform: translateY(-0.125rem); /* -2px */
        }}
        
        /* Responsive design */
        @media screen and (max-width: 75rem) {{
            body {{
                padding: 3rem 5rem;
            }}
            
            .content-layout {{
                flex-direction: column;
                gap: 2rem;
            }}
            
            .image-section {{
                flex: none;
                height: 20rem;
            }}
            
            .content-section {{
                flex: none;
                gap: 1.5rem;
            }}
        }}
        
        @media screen and (max-width: 50rem) {{
            body {{
                padding: 2rem 3rem;
            }}
            
            .slide-inner-container {{
                padding: 2rem 3rem;
            }}
            
            .content-item {{
                padding: 1rem;
            }}
            
            .icon-container {{
                width: 3rem;
                height: 3rem;
                margin-right: 1rem;
            }}
            
            .icon-container svg {{
                width: 1.5rem;
                height: 1.5rem;
            }}
            
            .main-title {{
                font-size: 2rem;
            }}
            
            .subtitle {{
                font-size: 1.25rem;
            }}
            
            .content {{
                font-size: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-inner-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Image Section -->
            <div class="image-section">
                <div class="image-frame">
                    <div class="image-accent"></div>
                    <div class="image-container">
                        <img src="{image_url}" alt="Slide image">
                    </div>
                </div>
            </div>
            
            <!-- Content Section -->
            <div class="content-section">
                <!-- Content Item 1 -->
                <div class="content-item">
                    <div class="icon-container">
                        {icon1}
                    </div>
                    <div class="content-text">
                        <h3 class="subtitle">{subtitle1}</h3>
                        <p class="content">{content1}</p>
                    </div>
                </div>
                
                <!-- Content Item 2 -->
                <div class="content-item">
                    <div class="icon-container">
                        {icon2}
                    </div>
                    <div class="content-text">
                        <h3 class="subtitle">{subtitle2}</h3>
                        <p class="content">{content2}</p>
                    </div>
                </div>
                
                <!-- Content Item 3 -->
                <div class="content-item">
                    <div class="icon-container">
                        {icon3}
                    </div>
                    <div class="content-text">
                        <h3 class="subtitle">{subtitle3}</h3>
                        <p class="content">{content3}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code




def generate_body_slide4(
    # Main parameters
    main_title="MainTitle",
    main_content="Content",
    
    # Content parameters
    subtitle1="Subtitle1",
    content1="Content1",
    subtitle2="Subtitle2",
    content2="Content2",
    subtitle3="Subtitle3",
    content3="Content3",
    
    # Style parameters
    main_bg_color="#ffffff",  # White background
    accent_color="#d5e8b9",   # Light green accent
    title_color="#333333",
    content_color="#555555",
    subtitle_color="#333333",
    font_family="'Segoe UI', Arial, sans-serif",
    image_url_1="Image/generate_body_slide4/Default_1.png",
    image_url_2="Image/generate_body_slide4/Default_2.png",
    image_url_3="Image/generate_body_slide4/Default_3.png"
):
    """
    Generates an HTML slide with a main title, horizontal content bar,
    and three images with subtitles and content - Full viewport design.
    
    Parameters:
    - main_title: The main title of the slide
    - main_content: Content for the horizontal bar
    
    Content parameters:
    - subtitle1, subtitle2, subtitle3: Subtitles for each image
    - content1, content2, content3: Content text for each image
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - accent_color: Color for accents and borders
    - title_color: Color for the main title and subtitles
    - content_color: Color for content text
    - subtitle_color: Color for subtitles
    - title_font_size: Font size for the main title
    - content_font_size: Font size for content text
    - subtitle_font_size: Font size for subtitles
    - font_family: Font family for the slide
    
    Returns:
    - HTML code for the slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Gallery Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ 
            font-size: 16px; 
            width: 100vw; 
            height: 100vh;
            overflow: hidden;
        }}
        
        body {{
            font-family: {font_family};
            background-color: {accent_color}; /* Full viewport accent background */
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            padding: 3rem 4rem; /* 48px 64px */
            position: relative;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 2.5rem; /* 40px */
        }}
        
        .title-accent {{
            width: 2.5rem; /* 40px - increased size */
            height: 2.5rem; /* 40px */
            background: linear-gradient(135deg, {accent_color}, rgba(213, 232, 185, 0.8));
            margin-right: 1.25rem; /* 20px */
            border-radius: 0.5rem; /* 8px */
            box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
        }}
        
        .main-title {{
            font-size: 3.5rem;
            color: {title_color};
            font-weight: 600;
            margin: 0;
        }}
        
        .content-bar {{
            width: 100%;
            background: linear-gradient(135deg, {accent_color}, rgba(213, 232, 185, 0.9));
            padding: 1.5rem 2.5rem; /* 24px 40px */
            margin-bottom: 2.5rem; /* 40px */
            border-radius: 0.75rem; /* 12px */
            text-align: center;
            color: {content_color};
            font-size: 1.6rem;
            font-weight: 500;
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}
        
        .content-bar::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 0.25rem; /* 4px */
            background: linear-gradient(90deg, {title_color}, {accent_color});
        }}
        
        .image-gallery {{
            display: flex;
            justify-content: space-between;
            width: 100%;
            flex: 1;
            align-items: stretch;
            gap: 2rem; /* 32px */
        }}
        
        .image-item {{
            flex: 1;
            display: flex;
            flex-direction: column;
            background: rgba(255,255,255,0.9);
            border-radius: 1.25rem; /* 20px */
            padding: 2rem; /* 32px */
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 0.125rem solid transparent; /* 2px */
            position: relative;
            overflow: hidden;
        }}
        
        .image-item:hover {{
            transform: translateY(-0.5rem); /* -8px hover lift */
            box-shadow: 0 1rem 2rem rgba(0,0,0,0.15);
            border-color: {accent_color};
        }}
        
        .image-container {{
            position: relative;
            width: 100%;
            height: 15rem; /* 240px - increased height */
            margin-bottom: 1.25rem; /* 20px */
            overflow: hidden;
            border-radius: 0.75rem; /* 12px */
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        }}
        
        .image-border {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-left: 0.5rem solid {accent_color}; /* 8px */
            border-radius: 0.75rem 0 0 0.75rem; /* 12px */
            z-index: 1;
            transition: all 0.3s ease;
        }}
        
        .image-item:hover .image-border {{
            border-left-width: 1rem; /* 16px - expand on hover */
            background: linear-gradient(to right, {accent_color}, transparent 70%);
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
            border-radius: 0.75rem; /* 12px */
        }}
        
        .image-item:hover .image-container img {{
            transform: scale(1.05); /* zoom effect on hover */
        }}
        
        .subtitle {{
            font-size: 2rem;
            color: {subtitle_color};
            margin: 0 0 1rem 0; /* 16px */
            font-weight: 600;
            text-align: center;
            position: relative;
        }}
        
        .subtitle::after {{
            content: '';
            position: absolute;
            bottom: -0.25rem; /* -4px */
            left: 50%;
            transform: translateX(-50%);
            width: 2rem; /* 32px */
            height: 0.125rem; /* 2px */
            background: {accent_color};
            border-radius: 0.0625rem; /* 1px */
            transition: width 0.3s ease;
        }}
        
        .image-item:hover .subtitle::after {{
            width: 4rem; /* 64px - expand underline on hover */
        }}
        
        .image-content {{
            font-size: 1.5rem;
            color: {content_color};
            margin: 0;
            text-align: center;
            line-height: 1.6;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.25rem; /* 20px */
            background: rgba(213, 232, 185, 0.1);
            border-radius: 0.5rem; /* 8px */
            transition: all 0.3s ease;
        }}
        
        .image-item:hover .image-content {{
            background: rgba(213, 232, 185, 0.2);
            transform: translateY(-0.125rem); /* -2px */
        }}
        
        /* Responsive design */
        @media screen and (max-width: 75rem) {{
            body {{
                padding: 3rem 5rem;
            }}
            
            .image-gallery {{
                flex-direction: column;
                gap: 1.5rem;
            }}
            
            .image-item {{
                flex-direction: row;
                align-items: center;
            }}
            
            .image-container {{
                width: 40%;
                height: 12rem;
                margin-bottom: 0;
                margin-right: 1.5rem;
            }}
            
            .content-area {{
                flex: 1;
            }}
        }}
        
        @media screen and (max-width: 50rem) {{
            body {{
                padding: 2rem 3rem;
            }}
            
            .slide-inner-container {{
                padding: 2rem 3rem;
            }}
            
            .image-item {{
                flex-direction: column;
                padding: 1rem;
            }}
            
            .image-container {{
                width: 100%;
                height: 10rem;
                margin-right: 0;
                margin-bottom: 1rem;
            }}
            
            .main-title {{
                font-size: 2rem;
            }}
            
            .subtitle {{
                font-size: 1.25rem;
            }}
            
            .image-content {{
                font-size: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-inner-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Bar -->
        <div class="content-bar">
            {main_content}
        </div>
        
        <!-- Image Gallery -->
        <div class="image-gallery">
            <!-- Image Item 1 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="{image_url_1}" alt="Image 1">
                </div>
                <div class="content-area">
                    <h3 class="subtitle">{subtitle1}</h3>
                    <p class="image-content">{content1}</p>
                </div>
            </div>
            
            <!-- Image Item 2 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="{image_url_2}" alt="Image 2">
                </div>
                <div class="content-area">
                    <h3 class="subtitle">{subtitle2}</h3>
                    <p class="image-content">{content2}</p>
                </div>
            </div>
            
            <!-- Image Item 3 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="{image_url_3}" alt="Image 3">
                </div>
                <div class="content-area">
                    <h3 class="subtitle">{subtitle3}</h3>
                    <p class="image-content">{content3}</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
# sửa biến trong tool



def generate_body_slide5(
    # Main parameters
    main_title="MainTitle",
    
    # Content parameters
    subtitle1="SUBTITLE1",
    content1="Content1",
    subtitle2="SUBTITLE2",
    content2="Content2",
    subtitle3="SUBTITLE3",
    content3="Content3",
    subtitle4="SUBTITLE4",
    content4="Content4",
    
    # Style parameters
    main_bg_color="#ffffff",  # White background
    accent_color="#d5e8b9",   # Light green accent
    title_color="#333333",
    subtitle_color="#6b9d34", # Green color for subtitles
    content_color="#555555",
    font_family="'Segoe UI', Arial, sans-serif",
    image_url_1="Image/generate_body_slide5/Default_1.png",
    image_url_2="Image/generate_body_slide5/Default_2.png",
    image_url_3="Image/generate_body_slide5/Default_3.png",
    image_url_4="Image/generate_body_slide5/Default_4.png",
):
    """
    Generates an HTML slide with a main title, 2x2 image grid on the left,
    and four content sections on the right - Full viewport design.
    
    Parameters:
    - main_title: The main title of the slide
    
    Content parameters:
    - subtitle1, subtitle2, subtitle3, subtitle4: Subtitles for each content section
    - content1, content2, content3, content4: Content text for each section
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - accent_color: Color for accents and borders
    - title_color: Color for the main title
    - subtitle_color: Color for subtitles
    - content_color: Color for content text
    - title_font_size: Font size for the main title
    - subtitle_font_size: Font size for subtitles
    - content_font_size: Font size for content text
    - font_family: Font family for the slide
    
    Returns:
    - HTML code for the slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Grid Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ 
            font-size: 16px; 
            width: 100vw; 
            height: 100vh;
            overflow: hidden;
        }}
        
        body {{
            font-family: {font_family};
            background-color: {accent_color}; /* Full viewport accent background */
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            padding: 3rem 4rem; /* 48px 64px */
            position: relative;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 2.5rem; /* 40px */
        }}
        
        .title-accent {{
            width: 2.5rem; /* 40px - increased size */
            height: 2.5rem; /* 40px */
            background: linear-gradient(135deg, {accent_color}, rgba(213, 232, 185, 0.8));
            margin-right: 1.25rem; /* 20px */
            border-radius: 0.5rem; /* 8px */
            box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
        }}
        
        .main-title {{
            font-size: 3.5rem;
            color: {title_color};
            font-weight: 600;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            flex: 1;
            gap: 2.5rem; /* 40px */
        }}
        
        .image-section {{
            flex: 2;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.9);
            border-radius: 1rem; /* 16px */
            padding: 2rem; /* 32px */
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.1);
            border-left: 0.25rem solid {accent_color}; /* accent border */
        }}
        
        .image-grid {{
            width: 100%;
            height: 100%;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 1rem; /* 16px */
        }}
        
        .image-card {{
            position: relative;
            border-radius: 0.75rem; /* 12px */
            overflow: hidden;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .image-card:hover {{
            transform: scale(1.05) rotate(1deg); /* hover effect */
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.15);
            z-index: 2;
        }}
        
        .image-container {{
            width: 100%;
            height: 100%;
            position: relative;
            overflow: hidden;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}
        
        .image-card:hover .image-container img {{
            transform: scale(1.1); /* zoom effect on hover */
        }}
        
        .image-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 0.5rem; /* 8px - increased overlay */
            background: linear-gradient(90deg, {accent_color}, rgba(213, 232, 185, 0.8));
            transition: all 0.3s ease;
        }}
        
        .image-card:hover .image-overlay {{
            height: 25%; /* expand overlay on hover */
            background: linear-gradient(to top, {accent_color}, transparent);
        }}
        
        .content-sections {{
            flex: 3;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 2rem;
        }}
        
        .content-item {{
            background: rgba(255,255,255,0.9);
            border-radius: 1rem; /* 16px */
            padding: 2rem;
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border-left: 0.25rem solid {subtitle_color}; /* subtitle color border */
            position: relative;
            overflow: hidden;
        }}
        
        .content-item:hover {{
            transform: translateY(-0.25rem); /* -4px hover lift */
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.15);
        }}
        
        .content-item::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 0.25rem; /* 4px */
            background: linear-gradient(90deg, {subtitle_color}, rgba(107, 157, 52, 0.6));
            transform: scaleX(0);
            transition: transform 0.3s ease;
            transform-origin: left;
        }}
        
        .content-item:hover::before {{
            transform: scaleX(1);
        }}
        
        .subtitle {{
            font-size: 2rem;
            color: {subtitle_color};
            margin: 0 0 1rem 0;
            font-weight: 600;
            position: relative;
        }}
        
        .subtitle::after {{
            content: '';
            position: absolute;
            bottom: -0.25rem; /* -4px */
            left: 0;
            width: 2rem; /* 32px */
            height: 0.125rem; /* 2px */
            background: {subtitle_color};
            border-radius: 0.0625rem; /* 1px */
        }}
        
        .content {{
            font-size: 1.6rem;
            color: {content_color};
            margin: 0;
            line-height: 1.6;
            padding: 1rem;
            background: rgba(107, 157, 52, 0.05); /* subtitle color with low opacity */
            border-radius: 0.5rem; /* 8px */
            transition: all 0.3s ease;
        }}
        
        .content-item:hover .content {{
            background: rgba(107, 157, 52, 0.1);
            transform: translateX(0.25rem); /* 4px */
        }}
        
        /* Responsive design */
        @media screen and (max-width: 75rem) {{
            body {{
                padding: 3rem 5rem;
            }}
            
            .content-layout {{
                flex-direction: column;
                gap: 2rem;
            }}
            
            .image-section {{
                flex: none;
                height: 20rem;
            }}
            
            .content-sections {{
                flex: none;
                gap: 1rem;
            }}
        }}
        
        @media screen and (max-width: 50rem) {{
            body {{
                padding: 2rem 3rem;
            }}
            
            .slide-inner-container {{
                padding: 2rem 3rem;
            }}
            
            .content-sections {{
                grid-template-columns: 1fr;
                grid-template-rows: repeat(4, 1fr);
            }}
            
            .content-item {{
                padding: 1rem;
            }}
            
            .main-title {{
                font-size: 2rem;
            }}
            
            .subtitle {{
                font-size: 1.25rem;
            }}
            
            .content {{
                font-size: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-inner-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Image Section -->
            <div class="image-section">
                <div class="image-grid">
                    <div class="image-card">
                        <div class="image-container">
                            <img src="{image_url_1}" alt="Image 1">
                            <div class="image-overlay"></div>
                        </div>
                    </div>
                    <div class="image-card">
                        <div class="image-container">
                            <img src="{image_url_2}" alt="Image 2">
                            <div class="image-overlay"></div>
                        </div>
                    </div>
                    <div class="image-card">
                        <div class="image-container">
                            <img src="{image_url_3}" alt="Image 3">
                            <div class="image-overlay"></div>
                        </div>
                    </div>
                    <div class="image-card">
                        <div class="image-container">
                            <img src="{image_url_4}" alt="Image 4">
                            <div class="image-overlay"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Content Sections -->
            <div class="content-sections">
                <div class="content-item">
                    <h3 class="subtitle">{subtitle1}</h3>
                    <p class="content">{content1}</p>
                </div>
                <div class="content-item">
                    <h3 class="subtitle">{subtitle2}</h3>
                    <p class="content">{content2}</p>
                </div>
                <div class="content-item">
                    <h3 class="subtitle">{subtitle3}</h3>
                    <p class="content">{content3}</p>
                </div>
                <div class="content-item">
                    <h3 class="subtitle">{subtitle4}</h3>
                    <p class="content">{content4}</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
# sửa biến trong tool





def generate_body_slide7(
    # Main parameters
    main_title="MainTitle",
    subtitle="SubTitle",
  
    # Content parameters
    content1="Content1",
    content2="Content2",
    
    # Style parameters
    main_bg_color="#ffffff",  # White background
    accent_color="#d5e8b9",   # Light green accent
    title_color="#333333",
    subtitle_color="#333333",
    content_color="#4a90a0",  # Teal/blue color for content
    divider_color="#d5e8b9",  # Light green divider
    font_family="'Segoe UI', Arial, sans-serif",
    image_url_1="Image/generate_body_slide7/Default_1.png",
    image_url_2="Image/generate_body_slide7/Default_2.png",
    image_url_3="Image/generate_body_slide7/Default_3.png",

):
    """
    Generates an HTML slide with a main title, three vertical images on the left,
    and content with subtitle on the right - Full viewport design.
    
    Parameters:
    - main_title: The main title of the slide
    - subtitle: The subtitle on the right side
    
    Content parameters:
    - content1, content2: Content text sections
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - accent_color: Color for accents
    - title_color: Color for the main title
    - subtitle_color: Color for the subtitle
    - content_color: Color for content text
    - divider_color: Color for the horizontal divider
    - title_font_size: Font size for the main title
    - subtitle_font_size: Font size for the subtitle
    - content_font_size: Font size for content text
    - font_family: Font family for the slide
    
    Returns:
    - HTML code for the slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vertical Images Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ 
            font-size: 16px; 
            width: 100vw; 
            height: 100vh;
            overflow: hidden;
        }}
        
        body {{
            font-family: {font_family};
            background-color: {accent_color}; /* Full viewport accent background */
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            padding: 3rem 4rem; /* 48px 64px */
            position: relative;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 2.5rem; /* 40px */
        }}
        
        .title-accent {{
            width: 2.5rem; /* 40px - increased size */
            height: 2.5rem; /* 40px */
            background: linear-gradient(135deg, {accent_color}, rgba(213, 232, 185, 0.8));
            margin-right: 1.25rem; /* 20px */
            border-radius: 0.5rem; /* 8px */
            box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
        }}
        
        .main-title {{
            font-size: 4.5rem;
            color: {title_color};
            font-weight: 600;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            flex: 1;
            gap: 2.5rem; /* 40px */
        }}
        
        .image-section {{
            flex: 2;
            display: flex;
            flex-direction: column;
            gap: 1rem; /* 16px */
        }}
        
        .image-card {{
            flex: 1;
            background: rgba(255,255,255,0.9);
            border-radius: 0.75rem; /* 12px */
            overflow: hidden;
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
            border-left: 0.25rem solid {accent_color}; /* accent border */
        }}
        
        .image-card:hover {{
            transform: translateX(0.5rem) scale(1.02); /* hover effect */
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.15);
        }}
        
        .image-container {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: relative;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}
        
        .image-card:hover .image-container img {{
            transform: scale(1.05); /* zoom effect on hover */
        }}
        
        .image-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 0.25rem; /* 4px */
            background: linear-gradient(90deg, {accent_color}, rgba(213, 232, 185, 0.8));
        }}
        
        .content-section {{
            flex: 3;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: rgba(255,255,255,0.9);
            border-radius: 1rem; /* 16px */
            padding: 3rem;
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.1);
            border-left: 0.25rem solid {accent_color}; /* accent border */
        }}
        
        .subtitle {{
            font-size: 2.5rem;
            color: {subtitle_color};
            margin: 0 0 2rem 0;
            font-weight: 600;
            position: relative;
        }}
        
        .subtitle::after {{
            content: '';
            position: absolute;
            bottom: -0.5rem; /* -8px */
            left: 0;
            width: 4rem; /* 64px */
            height: 0.25rem; /* 4px */
            background: linear-gradient(90deg, {divider_color}, rgba(213, 232, 185, 0.6));
            border-radius: 0.125rem; /* 2px */
        }}
        
        .content {{
            font-size: 2rem;
            color: {content_color};
            margin: 0 0 2rem 0;
            line-height: 1.6;
            padding: 1.25rem;
            background: rgba(74, 144, 160, 0.05); /* content color with low opacity */
            border-radius: 0.5rem; /* 8px */
            border-left: 0.25rem solid {content_color}; /* content accent */
            transition: all 0.3s ease;
        }}
        
        .content:hover {{
            background: rgba(74, 144, 160, 0.1);
            transform: translateX(0.25rem); /* 4px */
        }}
        
        .content:last-child {{
            margin-bottom: 0;
        }}
        
        /* Responsive design */
        @media screen and (max-width: 75rem) {{
            body {{
                padding: 3rem 5rem;
            }}
            
            .content-layout {{
                flex-direction: column;
                gap: 2rem;
            }}
            
            .image-section {{
                flex: none;
                height: 20rem;
                flex-direction: row;
            }}
            
            .content-section {{
                flex: none;
            }}
        }}
        
        @media screen and (max-width: 50rem) {{
            body {{
                padding: 2rem 3rem;
            }}
            
            .slide-inner-container {{
                padding: 2rem 3rem;
            }}
            
            .image-section {{
                flex-direction: column;
                height: 15rem;
            }}
            
            .main-title {{
                font-size: 2rem;
            }}
            
            .subtitle {{
                font-size: 1.5rem;
            }}
            
            .content {{
                font-size: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-inner-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Image Section -->
            <div class="image-section">
                <div class="image-card">
                    <div class="image-container">
                        <img src="{image_url_1}" alt="Image 1">
                        <div class="image-overlay"></div>
                    </div>
                </div>
                <div class="image-card">
                    <div class="image-container">
                        <img src="{image_url_2}" alt="Image 2">
                        <div class="image-overlay"></div>
                    </div>
                </div>
                <div class="image-card">
                    <div class="image-container">
                        <img src="{image_url_3}" alt="Image 3">
                        <div class="image-overlay"></div>
                    </div>
                </div>
            </div>
            
            <!-- Content Section -->
            <div class="content-section">
                <h2 class="subtitle">{subtitle}</h2>
                <p class="content">{content1}</p>
                <p class="content">{content2}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
# sửa biến trong tool


def generate_body_slide10(
    # Main parameters
    main_title="MainTitle",
    
    # Content parameters
    subtitle1="SubTitle1",
    content1="Content1",
    subtitle2="SubTitle2",
    content2="Content2",
    subtitle3="SubTitle3",
    content3="Content3",
    
    # Style parameters
    main_bg_color="#ffffff",
    accent_color="#d5e8b9",
    title_color="#333333",
    subtitle_color="#333333",
    content_color="#555555",
    font_family="'Segoe UI', Arial, sans-serif",
    image_url="Image/generate_body_slide10/Default_1.png",

    # Icon parameters - SVG paths for each icon
    icon1="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M12 2v6M12 18v4M14.5 8a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0zM16.5 13a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0z"></path></svg>""",  # Lightbulb
    icon2="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>""",  # Target
    icon3="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>""",  # Bar chart
):
    """
    Generates an HTML slide with a main title, large image on the left,
    and three content sections with icons on the right - Full viewport design.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image with Icons Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ 
            font-size: 16px; 
            width: 100vw; 
            height: 100vh;
            overflow: hidden;
        }}
        
        body {{
            font-family: {font_family};
            background-color: {accent_color}; /* Full viewport accent background */
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            padding: 3rem 4rem; /* 48px 64px */
            position: relative;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 2rem;
        }}
        
        .title-accent {{
            width: 2.5rem; /* 40px - tăng kích thước */
            height: 2.5rem; /* 40px */
            background-color: {accent_color};
            margin-right: 1.25rem; /* 20px */
            border-radius: 0.5rem; /* 8px */
        }}
        
        .main-title {{
            font-size: 4.5rem;
            color: {title_color};
            font-weight: 600;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            flex: 1;
            gap: 2.5rem; /* 40px - gap giữa image và content */
        }}
        
        .image-section {{
            flex: 2;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.9);
            border-radius: 1rem; /* 16px */
            padding: 2rem; /* 32px */
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.1);
        }}
        
        .image-frame {{
            width: 100%;
            height: 100%;
            position: relative;
            max-height: 28rem; /* 448px */
            border-radius: 0.75rem; /* 12px */
            overflow: hidden;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        }}
        
        .image-accent {{
            position: absolute;
            top: -0.5rem; /* -8px */
            left: -0.5rem; /* -8px */
            width: calc(100% + 1rem);
            height: calc(100% + 1rem);
            border: 0.25rem solid {accent_color}; /* 4px */
            border-radius: 1rem; /* 16px */
            box-sizing: border-box;
            z-index: 1;
        }}
        
        .image-container {{
            position: relative;
            width: 100%;
            height: 100%;
            z-index: 2;
            border-radius: 0.75rem; /* 12px */
            overflow: hidden;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}
        
        .image-section:hover .image-container img {{
            transform: scale(1.05); /* zoom effect on hover */
        }}
        
        .content-section {{
            flex: 3;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 1.5rem;
        }}
        
        .content-item {{
            display: flex;
            align-items: flex-start;
            background: rgba(255,255,255,0.9);
            border-radius: 0.75rem; /* 12px */
            padding: 1.5rem;
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border-left: 0.25rem solid {accent_color}; /* accent border */
        }}
        
        .content-item:hover {{
            transform: translateX(0.5rem); /* 8px - hover effect */
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.15);
        }}
        
        .icon-container {{
            width: 5rem;
            height: 5rem;
            background: linear-gradient(135deg, {accent_color}, rgba(213, 232, 185, 0.8));
            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: 1.5rem; /* 24px */
            flex-shrink: 0;
            border-radius: 0.75rem; /* 12px */
            box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .content-item:hover .icon-container {{
            transform: scale(1.1) rotate(5deg); /* hover animation */
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15);
        }}
        
        .icon-container svg {{
            width: 2.5rem;
            height: 2.5rem;
            stroke: #333333;
            filter: drop-shadow(0 0.125rem 0.25rem rgba(0,0,0,0.1));
        }}
        
        .content-text {{
            flex: 1;
        }}
        
        .subtitle {{
            font-size: 2rem;
            color: {subtitle_color};
            margin: 0 0 0.5rem 0;
            font-weight: 600;
        }}
        
        .content {{
            font-size: 1.6rem;
            color: {content_color};
            margin: 0;
            line-height: 1.5;
        }}
        
        /* Responsive design */
        @media screen and (max-width: 75rem) {{
            body {{
                padding: 3rem 5rem;
            }}
            
            .content-layout {{
                flex-direction: column;
                gap: 2rem;
            }}
            
            .image-section {{
                flex: none;
                height: 20rem;
            }}
            
            .content-section {{
                flex: none;
                gap: 1.5rem;
            }}
        }}
        
        @media screen and (max-width: 50rem) {{
            body {{
                padding: 2rem 3rem;
            }}
            
            .slide-inner-container {{
                padding: 2rem 3rem;
            }}
            
            .content-item {{
                flex-direction: column;
                text-align: center;
            }}
            
            .icon-container {{
                margin-right: 0;
                margin-bottom: 1rem;
            }}
            
            .title-font-size {{
                font-size: 2rem;
            }}
            
            .subtitle-font-size {{
                font-size: 1.25rem;
            }}
            
            .content-font-size {{
                font-size: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-inner-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Image Section -->
            <div class="image-section">
                <div class="image-frame">
                    <div class="image-accent"></div>
                    <div class="image-container">
                        <img src="{image_url}" alt="Slide image">
                    </div>
                </div>
            </div>
            
            <!-- Content Section -->
            <div class="content-section">
                <!-- Content Item 1 -->
                <div class="content-item">
                    <div class="icon-container">
                        {icon1}
                    </div>
                    <div class="content-text">
                        <h3 class="subtitle">{subtitle1}</h3>
                        <p class="content">{content1}</p>
                    </div>
                </div>
                
                <!-- Content Item 2 -->
                <div class="content-item">
                    <div class="icon-container">
                        {icon2}
                    </div>
                    <div class="content-text">
                        <h3 class="subtitle">{subtitle2}</h3>
                        <p class="content">{content2}</p>
                    </div>
                </div>
                
                <!-- Content Item 3 -->
                <div class="content-item">
                    <div class="icon-container">
                        {icon3}
                    </div>
                    <div class="content-text">
                        <h3 class="subtitle">{subtitle3}</h3>
                        <p class="content">{content3}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
# sửa biến trong tool




def generate_body_slide11(
    # Main parameters
    main_title="MainTitle",
    
    # Content parameters
    subtitle1="SUBTITLE1",
    content1="Content1",
    subtitle2="SUBTITLE2",
    content2="Content2",
    subtitle3="SUBTITLE3",
    content3="Content3",
    
    # Style parameters
    main_bg_color="#ffffff",
    box_bg_color="#e6f2dd",
    accent_color="#e6f2dd",
    title_color="#333333",
    subtitle_color="#333333",
    content_color="#555555",
    font_family="'Segoe UI', Arial, sans-serif",
    box_height="15.625rem",
    
    # Icon parameters - SVG paths for each icon
    icon1="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 9l-5 5-2-2-4 4"></path></svg>""",
    icon2="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>""",
    icon3="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>""",
):
    """
    Generates an HTML slide with a main title and three content boxes with icons.
    Full viewport design with modern styling.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Three Column Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ 
            font-size: 16px; 
            width: 100vw; 
            height: 100vh;
            overflow: hidden;
        }}
        
        body {{
            font-family: {font_family};
            background-color: {accent_color}; /* Full viewport accent background */
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            padding: 3rem 4rem; /* 48px 64px */
            position: relative;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 2.5rem;
        }}
        
        .title-accent {{
            width: 2.5rem; /* 40px - tăng kích thước */
            height: 2.5rem; /* 40px */
            background-color: {box_bg_color};
            margin-right: 1.25rem; /* 20px */
            border-radius: 0.5rem; /* 8px */
        }}
        
        .main-title {{
            font-size: 4.5rem;
            color: {title_color};
            font-weight: 600;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            justify-content: space-between;
            flex: 1;
            gap: 2rem; /* 32px - tạo gap giữa boxes */
            align-items: stretch;
        }}
        
        .content-box {{
            flex: 1;
            background: linear-gradient(135deg, {box_bg_color}, rgba(230, 242, 221, 0.8));
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 4.5rem 2rem 2rem;
            border-radius: 1rem;
            text-align: center;
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 0.125rem solid rgba(255,255,255,0.3);
        }}
        
        .content-box:hover {{
            transform: translateY(-0.5rem); /* 8px - hover effect */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
        }}
        
        .icon-circle {{
            width: 6rem;
            height: 6rem;
            border-radius: 50%;
            background: linear-gradient(135deg, #ffffff, #f8f9fa);
            position: absolute;
            top: -3rem;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 0.75rem 1.5rem rgba(0, 0, 0, 0.15);
            border: 0.25rem solid rgba(255,255,255,0.8);
            transition: all 0.3s ease;
        }}
        
        .content-box:hover .icon-circle {{
            transform: scale(1.1) rotate(5deg); /* hover animation */
            box-shadow: 0 1rem 2rem rgba(0, 0, 0, 0.2);
        }}
        
        .icon-circle svg {{
            stroke: {accent_color};
            width: 2.5rem;
            height: 2.5rem;
            filter: drop-shadow(0 0.125rem 0.25rem rgba(0,0,0,0.1));
        }}
        
        .subtitle {{
            font-size: 2rem;
            color: {subtitle_color};
            margin: 0 0 1.5rem 0;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05rem;
        }}
        
        .content {{
            font-size: 1.6rem;
            color: {content_color};
            margin: 0;
            line-height: 1.6;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* Responsive design */
        @media screen and (max-width: 75rem) {{
            body {{
                padding: 3rem 5rem;
            }}
            
            .content-layout {{
                flex-direction: column;
                gap: 1.5rem;
            }}
            
            .content-box {{
                padding: 3rem 1.5rem 1.5rem;
            }}
            
            .icon-circle {{
                width: 4rem;
                height: 4rem;
                top: -2rem;
            }}
            
            .icon-circle svg {{
                width: 1.5rem;
                height: 1.5rem;
            }}
        }}
        
        @media screen and (max-width: 50rem) {{
            body {{
                padding: 2rem 3rem;
            }}
            
            .slide-inner-container {{
                padding: 2rem 3rem;
            }}
            
            .title-section {{
                margin-bottom: 2rem;
            }}
            
            .title-font-size {{
                font-size: 2rem;
            }}
            
            .subtitle-font-size {{
                font-size: 1.25rem;
            }}
            
            .content-font-size {{
                font-size: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-inner-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Content Box 1 -->
            <div class="content-box">
                <div class="icon-circle">
                    {icon1}
                </div>
                <h3 class="subtitle">{subtitle1}</h3>
                <p class="content">{content1}</p>
            </div>
            
            <!-- Content Box 2 -->
            <div class="content-box">
                <div class="icon-circle">
                    {icon2}
                </div>
                <h3 class="subtitle">{subtitle2}</h3>
                <p class="content">{content2}</p>
            </div>
            
            <!-- Content Box 3 -->
            <div class="content-box">
                <div class="icon-circle">
                    {icon3}
                </div>
                <h3 class="subtitle">{subtitle3}</h3>
                <p class="content">{content3}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
# sửa biến trong tool



def generate_body_slide12(
    # Main parameters
    main_title="MainTitle",
    main_content="Content",
    
    # Content parameters
    subtitle1="Subtitle1",
    content1="Content1",
    subtitle2="Subtitle2",
    content2="Content2",
    subtitle3="Subtitle3",
    content3="Content3",
    
    # Style parameters
    main_bg_color="#ffffff",
    accent_color="#d5e8b9",
    title_color="#333333",
    content_color="#555555",
    subtitle_color="#333333",
    font_family="'Segoe UI', Arial, sans-serif",
    image_url_1="Image/generate_body_slide12/Default_1.png",
    image_url_2="Image/generate_body_slide12/Default_2.png",
    image_url_3="Image/generate_body_slide12/Default_3.png",

):
    """
    Generates an HTML slide with a main title, horizontal content bar,
    and three images with subtitles and content - Full viewport design.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Gallery Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ 
            font-size: 16px; 
            width: 100vw; 
            height: 100vh;
            overflow: hidden;
        }}
        
        body {{
            font-family: {font_family};
            background-color: {accent_color}; /* Full viewport accent background */
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            padding: 3rem 4rem; /* 48px 64px */
            position: relative;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 2rem; /* 32px */
        }}
        
        .title-accent {{
            width: 2.5rem; /* 40px - tăng kích thước */
            height: 2.5rem; /* 40px */
            background-color: {accent_color};
            margin-right: 1.25rem; /* 20px */
            border-radius: 0.5rem; /* 8px */
        }}
        
        .main-title {{
            font-size: 4.5rem;
            color: {title_color};
            font-weight: 600;
            margin: 0;
        }}
        
        .content-bar {{
            width: 100%;
            background: linear-gradient(135deg, {accent_color}, rgba(213, 232, 185, 0.8));
            padding: 1.5rem 2.5rem;
            margin-bottom: 2rem;
            border-radius: 0.75rem;
            text-align: center;
            color: {content_color};
            font-size: 1.6rem;
            font-weight: 500;
            box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
            border: 0.125rem solid rgba(255,255,255,0.3);
        }}
        
        .image-gallery {{
            display: flex;
            justify-content: space-between;
            flex: 1;
            gap: 2rem; /* 32px - tạo gap giữa items */
            align-items: stretch;
        }}
        
        .image-item {{
            flex: 1;
            display: flex;
            flex-direction: column;
            background: rgba(255,255,255,0.9);
            border-radius: 1.25rem;
            padding: 2rem;
            box-shadow: 0 0.75rem 1.5rem rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .image-item:hover {{
            transform: translateY(-0.5rem); /* 8px - hover effect */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15);
        }}
        
        .image-container {{
            position: relative;
            width: 100%;
            height: 18rem; /* 288px - tăng chiều cao */
            margin-bottom: 1.5rem; /* 24px */
            overflow: hidden;
            border-radius: 0.75rem; /* 12px */
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        }}
        
        .image-border {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0.25rem solid {accent_color}; /* 4px border all around */
            border-radius: 0.75rem; /* 12px */
            box-sizing: border-box;
            z-index: 1;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 0.5rem; /* 8px */
            transition: transform 0.3s ease;
        }}
        
        .image-item:hover .image-container img {{
            transform: scale(1.05); /* zoom effect on hover */
        }}
        
        .subtitle {{
            font-size: 2rem;
            color: {subtitle_color};
            margin: 0 0 1rem 0;
            font-weight: 600;
            text-align: center;
            color: {accent_color};
        }}
        
        .image-content {{
            font-size: 1.5rem;
            color: {content_color};
            margin: 0;
            text-align: center;
            line-height: 1.6;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* Responsive design */
        @media screen and (max-width: 75rem) {{
            body {{
                padding: 3rem 5rem;
            }}
            
            .image-gallery {{
                flex-direction: column;
                gap: 1.5rem;
            }}
            
            .image-container {{
                height: 15rem;
            }}
        }}
        
        @media screen and (max-width: 50rem) {{
            body {{
                padding: 2rem 3rem;
            }}
            
            .slide-inner-container {{
                padding: 2rem 3rem;
            }}
            
            .title-font-size {{
                font-size: 2rem;
            }}
            
            .content-font-size {{
                font-size: 1rem;
            }}
            
            .subtitle-font-size {{
                font-size: 1.25rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-inner-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Bar -->
        <div class="content-bar">
            {main_content}
        </div>
        
        <!-- Image Gallery -->
        <div class="image-gallery">
            <!-- Image Item 1 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="{image_url_1}" alt="Image 1">
                </div>
                <h3 class="subtitle">{subtitle1}</h3>
                <p class="image-content">{content1}</p>
            </div>
            
            <!-- Image Item 2 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="{image_url_2}" alt="Image 2">
                </div>
                <h3 class="subtitle">{subtitle2}</h3>
                <p class="image-content">{content2}</p>
            </div>
            
            <!-- Image Item 3 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="{image_url_3}" alt="Image 3">
                </div>
                <h3 class="subtitle">{subtitle3}</h3>
                <p class="image-content">{content3}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
# sửa biến trong tool


# sửa biến trong tool 

def generate_body_slide15(
    # Main parameters
    main_title="MainTitle",
    
    # Content parameters
    content1="""
        <ul>SubTitle1
            <li>Point 1</li>
            <li>Point 2</li>
            <li>Point 3</li>
        </ul>
    """,
    content2="""
        <ul>SubTitle2
            <li>Point 1</li>
            <li>Point 2</li>
            <li>Point 3</li>
        </ul>
    """,

    # Style parameters (đã chuyển sang rem)
    main_bg_color="#ffffff",
    accent_color="#d5e8b9",
    title_color="#333333",
    subtitle_color="#333333",
    content_color="#555555",
    font_family="'Segoe UI', Arial, sans-serif",
    image_url="Image/generate_body_slide15/Default_1.png",  # Default image path
):
    """
    Generates an HTML slide with an image on the right and two content sections on the left.
    All size parameters are now in REM.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Right Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ 
            font-size: 16px; 
            width: 100vw; 
            height: 100vh;
            overflow: hidden;
        }}
        
        body {{
            font-family: {font_family};
            background-color: {accent_color}; /* Accent color cho toàn màn hình */
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {main_bg_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15); /* 0 20px 40px */
            display: flex;
            flex-direction: column;
            padding: 2.5rem 5rem; /* 40px 80px */
            position: relative;
            justify-content: space-between;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 2rem;
        }}
        
        .title-accent {{
            width: 1.875rem; /* 30px */
            height: 1.875rem; /* 30px */
            background-color: {accent_color};
            margin-right: 0.9375rem; /* 15px */
            border-radius: 0.25rem; /* 4px - thêm border radius */
        }}
        
        .main-title {{
            font-size: 4.5rem;
            color: {title_color};
            font-weight: 600;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            flex: 1; /* chiếm toàn bộ space còn lại */
            gap: 2.5rem; /* 40px - tạo gap giữa columns */
        }}
        
        .left-column {{
            flex: 2.5; /* tăng từ 2 lên 2.5 để content có nhiều space hơn */
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 2rem; /* 32px */
        }}
        
        .right-column {{
            flex: 2.5; /* giảm từ 3 xuống 2.5 để ảnh nhỏ hơn */
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .image-container {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            border-radius: 0.5rem; /* 8px - thêm border radius */
            box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1); /* thêm shadow */
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease; /* thêm hover effect */
        }}
        
        .image-container:hover img {{
            transform: scale(1.02); /* zoom nhẹ khi hover */
        }}
        
        .content-section {{
            display: flex;
            flex-direction: column;
        }}
        
        .subtitle-container {{
            background-color: {accent_color};
            padding: 1.25rem 2rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.1);
        }}
        
        /* CSS cho nội dung chèn vào */
        .content-section ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .content-section ul li {{
            font-size: 1.6rem;
            color: {content_color};
            line-height: 1.6;
            padding-left: 1rem;
            position: relative;
            margin-bottom: 0.5rem;
        }}
        
        .content-section ul li::before {{
            content: '•';
            color: {accent_color}; /* đổi màu bullet */
            position: absolute;
            left: 0;
            font-weight: bold;
        }}

        /* Giả định dòng đầu tiên của <ul> là subtitle */
        .content-section ul {{
            font-size: 2.5rem;
            color: {subtitle_color};
            font-weight: 600;
            margin-bottom: 0.75rem;
        }}

    </style>
</head>
<body>
    <div class="slide-inner-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Left Column with Content Sections -->
            <div class="left-column">
                <!-- Content Section 1 -->
                <div class="content-section">
                    <div class="subtitle-container">
                        {content1}
                    </div>
                </div>
                
                <!-- Content Section 2 -->
                <div class="content-section">
                    <div class="subtitle-container">
                        {content2}
                    </div>
                </div>
            </div>
            
            <!-- Right Column with Image -->
            <div class="right-column">
                <div class="image-container">
                    <img src="{image_url}" alt="Slide image">
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
# sửa biến trong tool 





def generate_body_slide18(
    main_title="Main title",
    left_title="Subtitle 1",
    right_title="Subtitle 2",
    left_text="Content1",
    right_text="Content2",
    left_icon="gavel",  # Options: "gavel", "custom"
    right_icon="scales",  # Options: "scales", "custom"
    custom_left_icon="",  # Custom SVG code if left_icon is "custom"
    custom_right_icon="",  # Custom SVG code if right_icon is "custom"
    # Style parameters (đã chuyển sang rem cho consistency)
    main_title_font_size="3rem",          # THAY ĐỔI: 48px -> 3rem
    column_title_font_size="2.25rem",     # THAY ĐỔI: 36px -> 2.25rem
    text_font_size="1.375rem",            # THAY ĐỔI: 22px -> 1.375rem
    title_color="#555555",
    text_color="#555555",
    icon_color="#a2c4c9",
    background_color="#ffffff",
    accent_color="#a2c4c9",
    divider_color="#555555",
    font_family="Arial, sans-serif"
):
    """
    Generates an HTML slide with a main title and two comparison columns with icons.
    The slide has a border design that matches the image exactly.
    
    Parameters:
    - main_title: The main title of the slide
    - left_title: Title for the left column
    - right_title: Title for the right column
    - left_text: Text content for the left column
    - right_text: Text content for the right column
    - left_icon: Icon for the left column ("gavel" or "custom")
    - right_icon: Icon for the right column ("scales" or "custom")
    - custom_left_icon: Custom SVG code for left icon if left_icon is "custom"
    - custom_right_icon: Custom SVG code for right icon if right_icon is "custom"
    - main_title_font_size: Font size for the main title
    - column_title_font_size: Font size for the column titles
    - text_font_size: Font size for the text content
    - title_color: Color for all titles
    - text_color: Color for all text content
    - icon_color: Color for the icons
    - background_color: Background color of the slide
    - accent_color: Color for the corner accents
    - divider_color: Color for the divider line
    - font_family: Font family for the slide
    
    Returns:
    - HTML code for the comparison slide
    """
    
    # Define the SVG icons
    gavel_icon = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="90" height="90" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 13L3 2M14 13L9 18M14 13L16 11L20 15L18 17M14 6L17 9M9 1L3 7M20 21H4"/>
    </svg>"""
    
    scales_icon = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="90" height="90" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 3v18M8 21h8M7 8l-4 4M17 8l4 4M5 12a2 2 0 1 0 4 0 2 2 0 1 0-4 0M15 12a2 2 0 1 0 4 0 2 2 0 1 0-4 0"/>
        <path d="M5 12h14"/>
    </svg>"""
    
    # Select the appropriate icons
    if left_icon == "gavel":
        left_icon_html = gavel_icon
    elif left_icon == "custom":
        left_icon_html = custom_left_icon
    else:
        left_icon_html = gavel_icon
        
    if right_icon == "scales":
        right_icon_html = scales_icon
    elif right_icon == "custom":
        right_icon_html = custom_right_icon
    else:
        right_icon_html = scales_icon
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparison Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            background-color: {accent_color};
            color: {text_color};
            overflow: hidden;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            position: relative;
            background-color: {accent_color};
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 5rem 7.5rem; /* 80px 120px */
        }}

        .slide-inner-container {{
            width: 100%;
            height: 100%;
            max-width: 105rem; /* 1680px */
            max-height: 57.5rem; /* 920px */
            background-color: {background_color};
            border-radius: 1rem; /* 16px */
            box-shadow: 0 1.25rem 2.5rem rgba(0,0,0,0.15); /* 0 20px 40px */
            display: flex;
            flex-direction: column;
            padding: 3.75rem 5rem; /* 60px 80px */
            position: relative;
            justify-content: center;
        }}
        
        .main-title {{
            font-size: 4.5rem;
            font-weight: 700;
            color: {title_color};
            text-align: center;
            margin-bottom: 3rem;
            line-height: 1.2;
        }}
        
        .columns-container {{
            display: flex;
            flex: 1;
            align-items: center;
            justify-content: space-between;
            gap: 2rem; /* 32px */
            height: 100%;
            max-width: 100%;
        }}
        
        .column {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
            padding: 1rem 2rem;
            max-width: calc(50% - 1rem);
        }}
        
        .icon-container {{
            margin-bottom: 2rem;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 6rem;
        }}
        
        .column-title {{
            font-size: 2.8rem;
            font-weight: 600;
            color: {title_color};
            text-align: center;
            margin: 0 0 1.5rem 0;
            line-height: 1.3;
        }}
        
        .column-text {{
            font-size: 1.8rem;
            color: {text_color};
            text-align: center;
            line-height: 1.5;
            max-width: 100%;
        }}
        
        .divider {{
            width: 0.125rem; /* 2px */
            height: 60%;
            background: {divider_color};
            border: none;
            align-self: center;
            opacity: 0.4;
            flex-shrink: 0;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="slide-inner-container">
            <h1 class="main-title">{main_title}</h1>
            
            <div class="columns-container">
                <div class="column">
                    <div class="icon-container">
                        {left_icon_html}
                    </div>
                    <h2 class="column-title">{left_title}</h2>
                    <p class="column-text">{left_text}</p>
                </div>
                
                <div class="divider"></div>
                
                <div class="column">
                    <div class="icon-container">
                        {right_icon_html}
                    </div>
                    <h2 class="column-title">{right_title}</h2>
                    <p class="column-text">{right_text}</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
# sửa biến trong tool 



def generate_body_slide19(
    main_title="Your Title Here",
    left_column_titles=["Your Title Here", "Your Title Here"],
    left_column_texts=[
        "Presentations are communication tools that can be used as demonstrations.",
        "Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience."
    ],
    right_column_titles=["Your Title Here", "Your Title Here"],
    right_column_texts=[
        "Presentations are communication tools that can be used as speeches, reports, and more.",
        "Presentations are communication tools that can be used as speeches, reports, and more."
    ],
    # Style parameters (đã chuyển sang rem)
    
    main_title_color="#555555",
    left_bg_color="#a2c4c9",
    left_text_color="#ffffff",
    right_title_color="#555555",
    right_text_color="#555555",
    border_color="#a2c4c9",
    icon_color="#a2c4c9",
    font_family="Arial, sans-serif",
):
    """
    Generates an HTML slide with two columns. All size parameters are now in REM.
    """
    
    # Create left column sections HTML
    left_sections_html = ""
    for i, (title, text) in enumerate(zip(left_column_titles, left_column_texts)):
        left_sections_html += f"""
        <div class="left-section">
            <h2>{title}</h2>
            <p>{text}</p>
        </div>
        """
    
    # Create right column sections HTML
    right_sections_html = ""
    icons = [
        # Document with pencil icon
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="ICON_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <path d="M16 13l-4 4h-4v-4l8-8z"></path>
        </svg>""",
        # Magnifying glass icon
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="ICON_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>"""
    ]
    
    for i, (title, text) in enumerate(zip(right_column_titles, right_column_texts)):
        icon = icons[i % len(icons)].replace("ICON_COLOR", icon_color)
        right_sections_html += f"""
        <div class="right-section-{i}">
            <div class="icon-{i}">{icon}</div>
            <h2 class="right-title-{i}">{title}</h2>
            <p class="right-text-{i}">{text}</p>
        </div>
        """
    
    # Create the HTML content with CSS - Flat absolute positioning
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Two Column Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            background-color: {border_color};
            color: {right_text_color};
            overflow: hidden;
        }}

        .slide-background {{
            position: absolute;
            left: 120px;
            top: 80px;
            width: 1680px;
            height: 920px;
            background-color: #ffffff;
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .main-title {{
            position: absolute;
            left: 200px;
            top: 140px;
            width: 1520px;
            font-size: 4.5rem;
            font-weight: 700;
            color: {main_title_color};
            text-align: center;
            line-height: 1.2;
        }}
        
        .left-column {{
            position: absolute;
            left: 200px;
            top: 243px;
            width: 730px;
            height: 717px;
            background-color: {left_bg_color};
            border-radius: 8px;
            padding: 40px;
        }}
        
        .left-section {{
            margin-bottom: 32px;
        }}
        
        .left-section:last-child {{
            margin-bottom: 0;
        }}
        
        .left-section h2 {{
            font-size: 2.5rem;
            font-weight: 600;
            color: {left_text_color};
            margin-bottom: 16px;
            line-height: 1.3;
        }}
        
        .left-section p {{
            font-size: 1.6rem;
            color: {left_text_color};
            line-height: 1.5;
            opacity: 0.95;
        }}
        
        .right-section-0 {{
            position: absolute;
            left: 990px;
            top: 280px;
            width: 730px;
            height: 320px;
        }}
        
        .icon-0 {{
            position: absolute;
            left: 0;
            top: 0;
            width: 80px;
            height: 80px;
            background-color: rgba(162, 196, 201, 0.1);
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .icon-0 svg {{
            width: 60px;
            height: 60px;
        }}
        
        .right-title-0 {{
            position: absolute;
            left: 100px;
            top: 0;
            width: 630px;
            font-size: 2.5rem;
            font-weight: 600;
            color: {right_title_color};
            line-height: 1.3;
        }}
        
        .right-text-0 {{
            position: absolute;
            left: 100px;
            top: 65px;
            width: 630px;
            font-size: 1.6rem;
            color: {right_text_color};
            line-height: 1.5;
        }}
        
        .right-section-1 {{
            position: absolute;
            left: 990px;
            top: 640px;
            width: 730px;
            height: 320px;
        }}
        
        .icon-1 {{
            position: absolute;
            left: 0;
            top: 0;
            width: 80px;
            height: 80px;
            background-color: rgba(162, 196, 201, 0.1);
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .icon-1 svg {{
            width: 60px;
            height: 60px;
        }}
        
        .right-title-1 {{
            position: absolute;
            left: 100px;
            top: 0;
            width: 630px;
            font-size: 2.5rem;
            font-weight: 600;
            color: {right_title_color};
            line-height: 1.3;
        }}
        
        .right-text-1 {{
            position: absolute;
            left: 100px;
            top: 65px;
            width: 630px;
            font-size: 1.6rem;
            color: {right_text_color};
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <!-- Background layer -->
    <div class="slide-background"></div>
    
    <!-- Main title -->
    <h1 class="main-title">{main_title}</h1>
    
    <!-- Left column -->
    <div class="left-column">
        {left_sections_html}
    </div>
    
    <!-- Right column sections -->
    {right_sections_html}
</body>
</html>"""
    
    return html_code
# sửa biến trong tool 


def generate_body_slide20(
    main_title="Your Title Here",
    left_title="Your Title Here",
    right_title="Your Title Here",
    left_text="Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience. Presentation are communication tools that can be used as demontrations, lectures, reports, and more.",
    right_text="Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience. Presentation are communication tools that can be used as demontrations, lectures, reports, and more.",
    left_icon="gavel",
    right_icon="scales",
    custom_left_icon="",
    custom_right_icon="",
    # Style parameters (đã chuyển sang rem)
    
    title_color="#555555",
    text_color="#555555",
    icon_color="#a2c4c9",
    background_color="#ffffff",
    accent_color="#a2c4c9",
    divider_color="#555555",
    font_family="Arial, sans-serif",
):
    """
    Generates an HTML slide with two comparison columns. All size parameters are now in REM.
    """
    
    # Define the SVG icons
    # Kích thước icon cũng được chuyển đổi sang rem và tăng lên
    gavel_icon = f"""<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 13L3 2M14 13L9 18M14 13L16 11L20 15L18 17M14 6L17 9M9 1L3 7M20 21H4"/>
    </svg>"""
    
    scales_icon = f"""<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 3v18M8 21h8M7 8l-4 4M17 8l4 4M5 12a2 2 0 1 0 4 0 2 2 0 1 0-4 0M15 12a2 2 0 1 0 4 0 2 2 0 1 0-4 0"/>
        <path d="M5 12h14"/>
    </svg>"""
    
    # Select the appropriate icons
    if left_icon == "gavel":
        left_icon_html = gavel_icon
    elif left_icon == "custom":
        left_icon_html = custom_left_icon
    else:
        left_icon_html = gavel_icon
        
    if right_icon == "scales":
        right_icon_html = scales_icon
    elif right_icon == "custom":
        right_icon_html = custom_right_icon
    else:
        right_icon_html = scales_icon
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comparison Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            background-color: {accent_color};
            color: {text_color};
            overflow: hidden;
        }}

        .slide-background {{
            position: absolute;
            left: 120px;
            top: 80px;
            width: 1680px;
            height: 920px;
            background-color: {background_color};
            border-radius: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .main-title {{
            position: absolute;
            left: 200px;
            top: 140px;
            width: 1520px;
            font-size: 4.5rem;
            font-weight: 700;
            color: {title_color};
            text-align: center;
            line-height: 1.2;
        }}
        
        .left-column {{
            position: absolute;
            left: 260px;
            top: 280px;
            width: 650px;
            height: 620px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 0 32px;
            text-align: center;
        }}
        
        .right-column {{
            position: absolute;
            left: 1010px;
            top: 280px;
            width: 650px;
            height: 620px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 0 32px;
            text-align: center;
        }}
        
        .divider {{
            position: absolute;
            left: 960px;
            top: 290px;
            width: 2px;
            height: 600px;
            background-color: {divider_color};
            opacity: 0.3;
        }}
        
        .left-icon {{
            width: 100px;
            height: 100px;
            background-color: rgba(162, 196, 201, 0.1);
            border-radius: 16px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 28px;
        }}
        
        .left-icon svg {{
            width: 80px;
            height: 80px;
        }}
        
        .right-icon {{
            width: 100px;
            height: 100px;
            background-color: rgba(162, 196, 201, 0.1);
            border-radius: 16px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 28px;
        }}
        
        .right-icon svg {{
            width: 80px;
            height: 80px;
        }}
        
        .left-title {{
            font-size: 2.8rem;
            font-weight: 600;
            color: {title_color};
            text-align: center;
            margin-bottom: 24px;
            line-height: 1.3;
        }}
        
        .right-title {{
            font-size: 2.8rem;
            font-weight: 600;
            color: {title_color};
            text-align: center;
            margin-bottom: 24px;
            line-height: 1.3;
        }}
        
        .left-text {{
            font-size: 1.8rem;
            color: {text_color};
            text-align: center;
            line-height: 1.6;
            max-width: 90%;
        }}
        
        .right-text {{
            font-size: 1.8rem;
            color: {text_color};
            text-align: center;
            line-height: 1.6;
            max-width: 90%;
        }}
    </style>
</head>
<body>
    <!-- Background layer -->
    <div class="slide-background"></div>
    
    <!-- Main title -->
    <h1 class="main-title">{main_title}</h1>
    
    <!-- Divider -->
    <div class="divider"></div>
    
    <!-- Left column -->
    <div class="left-column">
        <div class="left-icon">
            {left_icon_html}
        </div>
        <h2 class="left-title">{left_title}</h2>
        <p class="left-text">{left_text}</p>
    </div>
    
    <!-- Right column -->
    <div class="right-column">
        <div class="right-icon">
            {right_icon_html}
        </div>
        <h2 class="right-title">{right_title}</h2>
        <p class="right-text">{right_text}</p>
    </div>
</body>
</html>"""
    
    return html_code
# sửa biến trong tool 




def generate_main_points_slide(
    title="WRITE YOUR TOPIC OR IDEA",
    point1_title="ADD A MAIN POINT",
    point1_description="Briefly elaborate on what you want to discuss.",
    point2_title="ADD A MAIN POINT", 
    point2_description="Briefly elaborate on what you want to discuss.",
    point3_title="ADD A MAIN POINT",
    point3_description="Briefly elaborate on what you want to discuss.",
    font_family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
):
    """
    Generates a completely static main points slide with three columns featuring environmental icons.
    All animations and hover effects have been removed.
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Main Points Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            background-color: #111827;
            overflow: hidden;
            position: relative;
        }}
        
        .slide-container {{
            height: 100vh;
            width: 100vw;
            padding: 4rem 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        
        .main-title {{
            font-size: 4.5rem;
            font-weight: 700;
            color: #10d9c4;
            text-align: center;
            margin-bottom: 5rem;
            letter-spacing: 2px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            text-transform: uppercase;
        }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 5rem;
            max-width: 1200px;
            width: 100%;
            align-items: center;
        }}
        
        .point-column {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            /* ĐÃ XÓA: transition và hover effect */
        }}
        
        .icon-circle {{
            width: 170px;
            height: 170px;
            background: rgba(255, 255, 255, 0.1);
            border: 4px solid #10d9c4;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 2.5rem;
            position: relative;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(16, 217, 196, 0.3);
        }}
        
        /* Plastic Bag Icon */
        .plastic-bag-icon {{
            width: 90px;
            height: 90px;
            position: relative;
        }}

        .bag-body {{
            width: 40px;
            height: 45px;
            background: #10d9c4;
            border-radius: 4px 4px 12px 12px;
            position: absolute;
            top: 12px;
            left: 15px;
            border: 3px solid #0891b2;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }}

        .bag-handles {{
            position: absolute;
            top: 0;
            left: 15px;
            width: 40px;
            height: 20px;
        }}

        .bag-handle-left {{
            width: 12px;
            height: 16px;
            background: transparent;
            border: 3px solid #10d9c4;
            border-radius: 50%;
            position: absolute;
            top: 0;
            left: 2px;
            border-bottom: none;
        }}

        .bag-handle-right {{
            width: 12px;
            height: 16px;
            background: transparent;
            border: 3px solid #10d9c4;
            border-radius: 50%;
            position: absolute;
            top: 0;
            right: 2px;
            border-bottom: none;
        }}

        .bag-details {{
            position: absolute;
            top: 20px;
            left: 20px;
            width: 30px;
            height: 30px;
        }}

        .bag-line {{
            width: 25px;
            height: 2px;
            background: #0891b2;
            margin: 6px 0;
            border-radius: 1px;
            opacity: 0.7;
        }}
        
        /* Faucet Icon */
        .faucet-icon {{
            width: 90px;
            height: 90px;
            position: relative;
        }}

        .faucet-main {{
            width: 35px;
            height: 20px;
            background: #10d9c4;
            border-radius: 18px 18px 0 0;
            position: absolute;
            top: 22px;
            left: 17px;
            border: 3px solid #0891b2;
            border-bottom: none;
        }}

        .faucet-spout {{
            width: 22px;
            height: 12px;
            background: #10d9c4;
            border-radius: 0 0 11px 11px;
            position: absolute;
            top: 32px;
            left: 24px;
            border: 3px solid #0891b2;
            border-top: none;
        }}

        .faucet-lever {{
            width: 8px;
            height: 16px;
            background: #10d9c4;
            border-radius: 4px;
            position: absolute;
            top: 8px;
            left: 31px;
            border: 2px solid #0891b2;
        }}

        .faucet-lever::after {{
            content: '';
            width: 14px;
            height: 4px;
            background: #10d9c4;
            border-radius: 2px;
            position: absolute;
            top: 3px;
            left: -3px;
            border: 2px solid #0891b2;
        }}

        .water-drops {{
            position: absolute;
            top: 46px;
            left: 32px;
        }}

        .water-drop {{
            width: 4px;
            height: 6px;
            background: #10d9c4;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            position: absolute;
            border: 1px solid #0891b2;
        }}

        /* ĐÃ XÓA: Hoạt ảnh giọt nước */
        .water-drop:nth-child(1) {{
            top: 0;
            left: 0;
        }}

        .water-drop:nth-child(2) {{
            top: 8px;
            left: 1px;
        }}
        
        /* Factory Icon */
        .factory-icon {{
            width: 90px;
            height: 90px;
            position: relative;
        }}

        .factory-main {{
            width: 45px;
            height: 32px;
            background: #10d9c4;
            border-radius: 3px;
            position: absolute;
            bottom: 8px;
            left: 12px;
            border: 3px solid #0891b2;
        }}

        .factory-windows {{
            position: absolute;
            top: 6px;
            left: 6px;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 4px;
            width: 30px;
        }}

        .factory-window {{
            width: 6px;
            height: 6px;
            background: #0891b2;
            border-radius: 1px;
        }}

        .factory-chimney1 {{
            width: 8px;
            height: 25px;
            background: #10d9c4;
            border-radius: 4px 4px 0 0;
            position: absolute;
            top: 5px;
            left: 25px;
            border: 3px solid #0891b2;
            border-bottom: none;
        }}

        .factory-chimney2 {{
            width: 6px;
            height: 18px;
            background: #10d9c4;
            border-radius: 3px 3px 0 0;
            position: absolute;
            top: 12px;
            left: 42px;
            border: 2px solid #0891b2;
            border-bottom: none;
        }}

        /* ĐÃ XÓA: Hoạt ảnh khói */
        .smoke-cloud {{
            position: absolute;
            top: 0;
            left: 27px;
        }}

        .smoke-puff {{
            width: 4px;
            height: 4px;
            background: #10d9c4;
            border-radius: 50%;
            position: absolute;
            opacity: 0.8;
        }}

        .smoke-puff:nth-child(1) {{ top: 2px; left: 0; }}
        .smoke-puff:nth-child(2) {{ top: -2px; left: 3px; }}
        .smoke-puff:nth-child(3) {{ top: -6px; left: 1px; }}
        .smoke-puff:nth-child(4) {{ top: -9px; left: 4px; }}
        .smoke-puff:nth-child(5) {{ top: -12px; left: 0px; }}
        
        .point-title {{
            font-size: 2rem;
            font-weight: 700;
            color: white;
            margin-bottom: 1.2rem;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        
        .point-description {{
            font-size: 1.6rem;
            color: rgba(255, 255, 255, 0.9);
            line-height: 1.6;
            max-width: 280px;
            font-weight: 400;
        }}
        
        @media (max-width: 768px) {{
            .slide-container {{
                padding: 2rem 1rem;
            }}
            
            .main-title {{
                font-size: 2rem;
                margin-bottom: 3rem;
                letter-spacing: 1px;
            }}
            
            .content-grid {{
                grid-template-columns: 1fr;
                gap: 3rem;
            }}
            
            .icon-circle {{
                width: 120px;
                height: 120px;
            }}
            
            .point-title {{
                font-size: 1.2rem;
            }}
            
            .point-description {{
                font-size: 1rem;
                max-width: 280px;
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <h1 class="main-title">{title}</h1>
        
        <div class="content-grid">
            <div class="point-column">
                <div class="icon-circle">
                    <div class="plastic-bag-icon">
                        <div class="bag-body"></div>
                        <div class="bag-handles">
                            <div class="bag-handle-left"></div>
                            <div class="bag-handle-right"></div>
                        </div>
                        <div class="bag-details">
                            <div class="bag-line"></div>
                            <div class="bag-line"></div>
                            <div class="bag-line"></div>
                        </div>
                    </div>
                </div>
                <h3 class="point-title">{point1_title}</h3>
                <p class="point-description">{point1_description}</p>
            </div>
            
            <div class="point-column">
                <div class="icon-circle">
                    <div class="faucet-icon">
                        <div class="faucet-main"></div>
                        <div class="faucet-spout"></div>
                        <div class="faucet-lever"></div>
                        <div class="water-drops">
                            <div class="water-drop"></div>
                            <div class="water-drop"></div>
                        </div>
                    </div>
                </div>
                <h3 class="point-title">{point2_title}</h3>
                <p class="point-description">{point2_description}</p>
            </div>
            
            <div class="point-column">
                <div class="icon-circle">
                    <div class="factory-icon">
                        <div class="factory-main"></div>
                        <div class="factory-windows">
                            <div class="factory-window"></div>
                            <div class="factory-window"></div>
                            <div class="factory-window"></div>
                        </div>
                        <div class="factory-chimney1"></div>
                        <div class="factory-chimney2"></div>
                        <div class="smoke-cloud">
                            <div class="smoke-puff"></div>
                            <div class="smoke-puff"></div>
                            <div class="smoke-puff"></div>
                            <div class="smoke-puff"></div>
                            <div class="smoke-puff"></div>
                        </div>
                    </div>
                </div>
                <h3 class="point-title">{point3_title}</h3>
                <p class="point-description">{point3_description}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code



def generate_elegant_points_slide(
    main_title="Write Your Topic or Idea Here",
    points=[
        {
            "title": "Add a Key Point",
            "description": "Briefly elaborate on the topic you want to discuss."
        },
        {
            "title": "Add a Key Point",
            "description": "Briefly elaborate on the topic you want to discuss."
        },
        {
            "title": "Add a Key Point",
            "description": "Briefly elaborate on the topic you want to discuss."
        },
        {
            "title": "Add a Key Point",
            "description": "Briefly elaborate on the topic you want to discuss."
        }
    ],
    font_family="'Be Vietnam Pro', sans-serif",
    bg_color="#FDFCFB",
    card_bg_color="#FFFFFF",
    title_color="#4E443F",
    text_color="#5D534D",
    accent_color="#B99C6B"
):
    """
    Generates an elegant points slide optimized for 1920x1080 screenshots
    with an adjusted layout that emphasizes the content grid over the title.
    """

    icons_svg = [
        """<svg class="point-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2A7 7 0 0 0 5 9c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74A7 7 0 0 0 12 2M9 21a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-1H9z"></path></svg>""",
        """<svg class="point-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2m0 18a8 8 0 1 1 8-8a8 8 0 0 1-8 8m0-14a6 6 0 1 0 6 6a6 6 0 0 0-6-6m0 10a4 4 0 1 1 4-4a4 4 0 0 1-4 4m0-6a2 2 0 1 0 2 2a2 2 0 0 0-2-2"></path></svg>""",
        """<svg class="point-icon" viewBox="0 0 24 24"><path fill="currentColor" d="m3.5 18.49l6-6.01l4 4L22 6.92L20.59 5.51L13.5 12.5l-4-4l-7.5 7.5z"></path></svg>""",
        """<svg class="point-icon" viewBox="0 0 24 24"><path fill="currentColor" d="M12 8a4 4 0 1 0 0 8a4 4 0 0 0 0-8m0 6a2 2 0 1 1 0-4a2 2 0 0 1 0 4m6.6-4.95l-.71-.71l-1.42 1.42l.71.71c.39.39.39 1.02 0 1.41l-1.42 1.42l-.71.71l1.42 1.42l.71-.71l1.42-1.42l-.71-.71c-.39-.39-.39-1.02 0-1.41M5.4 7.05L4 5.64l.71-.71l1.42 1.42l-.71.71c-.39.39-1.02.39-1.41 0l-1.42-1.42l-.71-.71L4 5.64M18.36 5.64l.71.71l1.42-1.42l-.71-.71a.996.996 0 0 0-1.41 0l-1.42 1.42l-.71.71l1.42 1.42zm-12.72 12.72l-.71-.71l-1.42 1.42l.71.71c.39.39.39 1.02 0 1.41l-1.42 1.42l-.71.71l1.42 1.42l.71-.71l1.42-1.42l-.71-.71c-.39-.39-.39-1.02 0-1.41Z"></path></svg>"""
    ]

    points_html = ""
    for i, point in enumerate(points):
        icon = icons_svg[i % len(icons_svg)]
        points_html += f"""
        <div class="point-card">
            {icon}
            <div class="icon-divider"></div>
            <h2 class="point-title">{point['title']}</h2>
            <p class="point-description">{point['description']}</p>
        </div>
        """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elegant Points Slide - 1920x1080</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            background-color: {bg_color};
            color: {text_color};
            overflow: hidden;
        }}

        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            padding: 80px 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            text-align: center;
        }}

        .main-title {{
            font-size: 90px;
            font-weight: 800;
            color: {title_color};
            margin-bottom: 80px;
            line-height: 1.2;
        }}

        .points-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 60px;
            flex: 1;
            align-items: center;
        }}

        .point-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: {card_bg_color};
            padding: 50px 40px;
            border-radius: 20px;
            border: 1px solid #EAE2D6;
            box-shadow: 0 15px 40px rgba(0,0,0,0.1);
            height: 100%;
        }}
        
        .point-icon {{
            width: 100px;
            height: 100px;
            color: {accent_color};
        }}
        
        .icon-divider {{
            width: 80px;
            height: 5px;
            background-color: {accent_color};
            border-radius: 2px;
            margin: 30px 0;
        }}

        .point-title {{
            font-size: 42px;
            font-weight: 600;
            color: {title_color};
            margin-bottom: 25px;
            margin-top: 10px;

            line-height: 1.3;
        }}

        .point-description {{
            font-size: 26px;
            line-height: 1.7;
            text-align: center;
        }}

        /* Content wrapper for scaling */
        .content-wrapper {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 1920px;
            height: 1080px;
            overflow: visible;
            background: inherit;
        }}
        
        .outer-wrapper {{
            padding: 0;
            box-sizing: border-box;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
        }}

    </style>
</head>
<body>
    <div class="outer-wrapper">
        <div class="content-wrapper">
            <div class="slide-container">
                <h1 class="main-title">{main_title}</h1>
                <div class="points-grid">
                    {points_html}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
#xong

def generate_corporate_content_slide(
    main_title="THIS IS A <span class='highlight'>SLIDE</span> TITLE",
    list_items=[
        { "title": "First Key Point", "description": "Here you have a list of items, presented in a modern, card-based format." },
        { "title": "Second Key Point", "description": "And some text to elaborate on the second main idea of your slide." },
        { "title": "Third Key Point", "description": "But remember not to overload your slides with too much content." }
    ],
    font_family="'Montserrat', sans-serif",
    bg_color="#F8FAFC",
    accent_panel_color="#6366F1",
    title_color="#FFFFFF",
    list_title_color="#1F2937",
    list_text_color="#4B5563"
):
    """
    Generates a bright, professional, and STATIC content slide.
    Hover effects have been removed.
    """

    list_html = ""
    for i, item in enumerate(list_items):
        number = f"{i+1:02d}"
        list_html += f"""
        <div class="list-item-card">
            <div class="item-content">
                <h3 class="list-item-title">{item['title']}</h3>
                <p class="list-item-description">{item['description']}</p>
            </div>
        </div>
        """

    clip_path_svg = """
    <svg width="0" height="0">
      <defs>
        <clipPath id="angled-title-panel" clipPathUnits="objectBoundingBox">
          <polygon points="0 0, 1 0, 0.85 1, 0 1" />
        </clipPath>
      </defs>
    </svg>
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Corporate Content Slide - Bright Design</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex; position: relative;
        }}

        .accent-panel {{
            flex: 1;
            background-color: {accent_panel_color};
            clip-path: url(#angled-title-panel);
            display: flex;
            align-items: center;
            padding: 4rem;
        }}

        .slide-title {{
            font-size: clamp(3.5rem, 6vw, 6rem);
            font-weight: 800;
            color: {title_color};
            text-transform: uppercase;
            max-width: 15ch;
            line-height: 1.1;
        }}
        .highlight {{ color: {bg_color}; opacity: 0.8; }}
        
        .content-column {{
            flex: 1.2;
            padding: 4rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 2rem;
        }}

        .list-item-card {{
            background: #FFFFFF;
            border-radius: 1rem;
            padding: 2.5rem;
            position: relative;
            overflow: hidden;
            border: 1px solid #E5E7EB;
            box-shadow: 0 8px 25px rgba(0,0,0,0.07);
            /* ĐÃ XÓA: transition */
        }}
        /* ĐÃ XÓA: khối :hover */

        .item-number {{
            position: absolute;
            top: -1rem; right: 1rem;
            font-size: 5rem;
            font-weight: 800;
            color: rgba(30, 41, 59, 0.05);
            z-index: 1;
        }}
        .item-content {{ position: relative; z-index: 2; }}

        .list-item-title {{
            font-size: 2.2rem;
            font-weight: 700;
            color: {list_title_color};
            margin-bottom: 1rem;
        }}
        .list-item-description {{
            font-size: 1.6rem;
            line-height: 1.6;
            color: {list_text_color};
        }}
        
        @media (max-width: 64rem) {{
            .slide-container {{ flex-direction: column; }}
            .accent-panel {{ flex: 0.5; width: 100%; clip-path: none; text-align: center; }}
            .slide-title {{ max-width: none; }}
            .content-column {{ flex: 1; width: 100%; }}
        }}
    </style>
</head>
<body>
    {clip_path_svg}
    <div class="slide-container">
        <div class="accent-panel">
            <h1 class="slide-title">{main_title}</h1>
        </div>
        <div class="content-column">
            {list_html}
        </div>
    </div>
</body>
</html>"""
    
    return html_code



def generate_split_content_slide(
    main_title="SPLIT YOUR CONTENT",
    columns=[
        { "icon_name": "bulb", "title": "Title One", "description": "Description for the first column goes here. Elaborate on your point with clear and concise text." },
        { "icon_name": "target", "title": "Title Two", "description": "Description for the second column. This layout is perfect for comparing two ideas side-by-side." }
    ],
    font_family="'Montserrat', sans-serif",
    bg_gradient_start="#0F172A",
    bg_gradient_end="#1E293B",
    title_color="#FFFFFF",
    text_color="#D1D5DB",
    accent_color="#22D3EE"
):
    """
    Generates a high-tech, STATIC, dark-themed slide for comparing two points.
    Hover effects have been removed.
    """

    icons = {
        "bulb": '<path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74A7 7 0 0 0 12 2M9 21a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-1H9z"/>',
        "target": '<path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2m0 18a8 8 0 1 1 8-8a8 8 0 0 1-8 8m0-14a6 6 0 1 0 6 6a6 6 0 0 0-6-6m0 10a4 4 0 1 1 4-4a4 4 0 0 1-4 4m0-6a2 2 0 1 0 2 2a2 2 0 0 0-2-2"/>'
    }

    columns_html = ""
    for col in columns:
        icon_svg = icons.get(col.get("icon_name"), "")
        columns_html += f"""
        <div class="column-card">
            <div class="card-header">
                <svg class="column-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">{icon_svg}</svg>
            </div>
            <h2 class="column-title">{col['title']}</h2>
            <p class="column-description">{col['description']}</p>
        </div>
        """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Split Content Slide - High-Tech Design</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            background: linear-gradient(135deg, {bg_gradient_start}, {bg_gradient_end});
            color: {text_color};
            overflow: hidden;
        }}

        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            padding: 80px 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            text-align: center;
        }}

        .main-title {{
            font-size: 90px;
            font-weight: 800;
            color: {title_color};
            text-transform: uppercase;
            text-align: center;
            margin-bottom: 80px;
            line-height: 1.2;
        }}
        .highlight {{ color: {accent_color}; }}
        
        .columns-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 80px;
            flex: 1;
            align-items: center;
        }}

        .column-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-top: 3px solid {accent_color};
            box-shadow: 0 0 30px rgba(34, 211, 238, 0.1);
            padding: 60px 50px;
            border-radius: 20px;
            height: 100%;
        }}

        .card-header {{
            margin-bottom: 40px;
            color: {accent_color};
        }}
        .column-icon {{
            width: 80px;
            height: 80px;
        }}

        .column-title {{
            font-size: 48px;
            font-weight: 700;
            color: {title_color};
            margin-bottom: 25px;
            line-height: 1.3;
        }}
        .column-description {{
            font-size: 28px;
            line-height: 1.7;
            color: {text_color};
            text-align: center;
        }}

        /* Content wrapper for scaling */
        .content-wrapper {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 1920px;
            height: 1080px;
            overflow: visible;
            background: inherit;
        }}
        
        .outer-wrapper {{
            padding: 0;
            box-sizing: border-box;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
        }}

    </style>
</head>
<body>
    <div class="outer-wrapper">
        <div class="content-wrapper">
            <div class="slide-container">
                <h1 class="main-title">{main_title}</h1>
                <div class="columns-grid">
                    {columns_html}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code





def generate_corporate_multicolumn_slide(
    main_title="IN TWO OR THREE<br><span class='highlight'>COLUMNS</span>",
    columns=[
        { "title": "Yellow", "description": "Is the color of gold, butter and ripe lemons." },
        { "title": "Blue", "description": "Is the colour of the clear sky and the deep sea." },
        { "title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage." }
    ],
    font_family="'Montserrat', sans-serif",
    accent_color="#8B5CF6",
    shadow_color="#7C3AED",
    text_color="#4B5563",
    icon_color="#D1D5DB"
):
    """
    Generates a professional, STATIC content slide for presenting information in 2 or 3 columns.
    Hover effects have been removed.
    """
    icon_svg = f"""<svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>"""
    columns_html = "".join([f"""<div class="info-column"><h2 class="column-title">{col['title']}</h2><p class="column-description">{col['description']}</p></div>""" for col in columns])
    clip_path_svg = """<svg width="0" height="0"><defs><clipPath id="angled-multi-divider" clipPathUnits="objectBoundingBox"><polygon points="0.15 0, 1 0, 1 1, 0 1" /></clipPath></defs></svg>"""
    grid_template_style = f"repeat({len(columns)}, 1fr)"

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Multi-Column Content Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }} html {{ font-size: 18px; }}
        body, html {{ height: 100vh; width: 100vw; font-family: {font_family}; overflow: hidden; background-color: #FFFFFF; }}
        .slide-container {{ width: 100%; height: 100%; display: flex; position: relative; border-top: 6px solid #F3F4F6; }}
        .content-area {{ flex: 2; padding: 4rem 5rem; display: flex; flex-direction: column; justify-content: center; }}
        .color-panel {{ flex: 1; position: relative; background: linear-gradient(135deg, {accent_color} 0%, {shadow_color} 100%); clip-path: url(#angled-multi-divider); }}
        .color-panel::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, {shadow_color} 0%, #6D28D9 100%); clip-path: url(#angled-multi-divider); transform: translateX(-2rem); z-index: -1; }}
        .title-group {{ display: flex; align-items: center; gap: 1.5rem; margin-bottom: 5rem; }}
        .icon-svg {{ width: 4.5rem; height: 4.5rem; flex-shrink: 0; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }}
        .slide-title {{ font-size: 3.5rem; font-weight: 800; color: {text_color}; text-transform: uppercase; line-height: 1.1; letter-spacing: 0.5px; }}
        .highlight {{ color: {accent_color}; text-shadow: 0 2px 4px rgba(139, 92, 246, 0.3); }}
        .columns-grid {{ display: grid; grid-template-columns: {grid_template_style}; gap: 3rem; padding-left: 5rem; }}
        .info-column {{
            position: relative; padding: 2.5rem 2rem;
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
            border-radius: 16px; border: 1px solid #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .info-column::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, {accent_color}, {shadow_color}); border-radius: 16px 16px 0 0; }}
        .column-title {{ font-size: 2.2rem; font-weight: 700; color: {text_color}; margin-bottom: 1.2rem; text-transform: uppercase; letter-spacing: 0.5px; }}
        .column-description {{ color: {text_color}; font-size: 1.6rem; line-height: 1.7; font-weight: 400; }}
        @media (max-width: 1400px) {{ .slide-title {{ font-size: 3rem; }} .column-title {{ font-size: 1.9rem; }} .column-description {{ font-size: 1.4rem; }} }}
        @media (max-width: 1200px) {{ .content-area {{ padding: 3rem 4rem; }} .columns-grid {{ gap: 2rem; padding-left: 3rem; }} }}
    </style>
</head>
<body>
    {clip_path_svg}
    <div class="slide-container">
        <div class="content-area"><div class="title-group">{icon_svg}<h1 class="slide-title">{main_title}</h1></div><div class="columns-grid">{columns_html}</div></div>
        <div class="color-panel"></div>
    </div>
</body>
</html>"""
    
    return html_code




def generate_corporate_grid_slide(
    main_title="LET'S <span class='highlight'>REVIEW</span> SOME<br>CONCEPTS",
    grid_items=[
        { "title": "title", "description": "description." },
        { "title": "title", "description": "description." },
        { "title": "title", "description": "description." },
        { "title": "title", "description": "description." },        
        { "title": "title", "description": "description." },
        { "title": "title", "description": "description." }
    ],
    font_family="'Montserrat', sans-serif",
    accent_color="#22C55E",
    shadow_color="#16A34A",
    text_color="#6B7280",
    icon_color="#D1D5DB"
):
    icon_svg = f"""
    <svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
    </svg>
    """

    grid_items_html = ""
    for item in grid_items:
        grid_items_html += f"""
        <div class="grid-item">
            <h2 class="item-title">{item['title']}</h2>
            <p class="item-description">{item['description']}</p>
        </div>
        """
    
    clip_path_svg = """
    <svg width="0" height="0">
      <defs>
        <clipPath id="angled-grid-divider" clipPathUnits="objectBoundingBox">
          <polygon points="0.15 0, 1 0, 1 1, 0 1" />
        </clipPath>
      </defs>
    </svg>
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grid Content Slide - Adjusted</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 18px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: #FFFFFF;
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex; position: relative;
            border-top: 4px solid #F3F4F6;
        }}

        .content-area {{
            flex: 2.5;
            padding: 5.5rem;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }}
        
        .color-panel {{
            flex: 1;
            position: relative;
            background-color: {accent_color};
            clip-path: url(#angled-grid-divider);
        }}

        .color-panel::before {{
            content: ''; position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: {shadow_color};
            clip-path: url(#angled-grid-divider);
            transform: translateX(-1.5rem);
            z-index: -1;
        }}
        
        .title-group {{ 
            display: flex; 
            align-items: center; 
            gap: 2rem; 
            margin-bottom: 5.5rem; 
            padding-bottom: 0.5rem;
        }}
        .icon-svg {{ width: 4.5rem; height: 4.5rem; flex-shrink: 0; }}
        .slide-title {{
            font-size: 3.5rem;
            font-weight: 800;
            color: {text_color};
            text-transform: uppercase;
            line-height: 1.2;
        }}
        .highlight {{ color: {accent_color}; }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 3.5rem 4rem;
            padding-left: 6rem;
        }}

        .item-title {{ 
            font-size: 2.75rem; /* TO HƠN */
            font-weight: 800; 
            color: {text_color}; 
            margin-bottom: 1.25rem; 
        }}
        .item-description {{ 
            color: {text_color}; 
            font-size: 2rem;  /* TO HƠN */
            line-height: 1.9; 
        }}

        @media (max-width: 64rem) {{
            .content-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
         @media (max-width: 48rem) {{
            .slide-container {{ flex-direction: column; }}
            .content-area, .color-panel {{ flex: none; width: 100%; }}
            .content-area {{ height: 70vh; padding: 2rem; justify-content: center; }}
            .color-panel {{ height: 30vh; clip-path: none; }}
            .color-panel::before {{ display: none; }}
            .content-grid {{ grid-template-columns: 1fr; padding-left: 0; text-align: center; }}
            .title-group {{ justify-content: center; }}
        }}
    </style>
</head>
<body>
    {clip_path_svg}
    <div class="slide-container">
        <div class="content-area">
            <div class="title-group">
                {icon_svg}
                <h1 class="slide-title">{main_title}</h1>
            </div>
            <div class="content-grid">
                {grid_items_html}
            </div>
        </div>
        <div class="color-panel"></div>
    </div>
</body>
</html>"""
    
    return html_code



def generate_business_overview_slide(
    main_title="BUSINESS OVERVIEW",
    sections=[
        {
            "icon": "chart-analysis",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        },
        {
            "icon": "innovation",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        },
        {
            "icon": "growth",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        }
    ],
    left_bg_color="#1a4b8c",
    right_bg_color="#f8f9fa",
    title_color="#FFFFFF",
    icon_bg_color="#2a3f6b",
    icon_color="#FFFFFF",
    content_bg_color="#FFFFFF",
    content_text_color="#1a4b8c",
    font_family="'Segoe UI', 'Roboto', sans-serif",
    show_border=False,
    border_opacity=0.25,
    section_spacing="30px",
    icon_size="110px",
    custom_css=""
):
    """
    Generate a professional business overview slide with icon-content sections layout.

    :param main_title: Main title text (10-25 characters), displayed on the left side
    :param sections: List of dictionaries with icon and content for each section,
                    or list of lists where first element is content and second is icon
    :param left_bg_color: Background color for the left title section (hex code)
    :param right_bg_color: Background color for the right content area (hex code)
    :param title_color: Color of the main title text (hex code)
    :param icon_bg_color: Background color for icon containers (hex code)
    :param icon_color: Color of the icons (hex code)
    :param content_bg_color: Background color for content text areas (hex code)
    :param content_text_color: Text color for content sections (hex code)
    :param title_font_size: Font size for the main title
    :param content_font_size: Font size for section content text
    :param font_family: Font family for all text elements
    :param show_border: Whether to show the dashed border frame
    :param border_opacity: Opacity of the border frame (0.0 to 1.0)
    :param section_spacing: Vertical spacing between content sections
    :param icon_size: Size of the icon containers
    :param custom_css: Additional custom CSS to be included
    :return: A string containing the HTML code for the slide
    """

    # Icon SVG definitions
    icons = {
        "chart-analysis": '''<svg viewBox="0 0 24 24" fill="currentColor" width="55" height="55">
            <path d="M3 3v18h18v-2H5V3H3zm4 14h2V9H7v8zm4 0h2V7h-2v10zm4 0h2v-4h-2v4zm3-12l-3 3-3-3-4 4-1.5-1.5L9 10l3-3 3 3 4-4z"/>
        </svg>''',
        "innovation": '''<svg viewBox="0 0 24 24" fill="currentColor" width="55" height="55">
            <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z"/>
            <circle cx="12" cy="9" r="1"/>
            <path d="M12 6v2m0 4v2m-3-3h2m4 0h2"/>
        </svg>''',
        "growth": '''<svg viewBox="0 0 24 24" fill="currentColor" width="55" height="55">
            <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6h-6z"/>
            <path d="M5 19h2v2H5zm4 0h2v2H9zm4 0h2v2h-2z"/>
        </svg>'''
    }

    # Generate sections HTML
    sections_html = ""
    for i, section in enumerate(sections):
        # Mới: Kiểm tra section có phải là list hay không và xử lý tương ứng
        if isinstance(section, list):
            # Giả định dữ liệu dạng [content, icon]
            content = section[0] if len(section) > 0 else ""
            icon_name = section[1] if len(section) > 1 else "chart-analysis"
            icon_svg = icons.get(icon_name, icons["chart-analysis"])
        else:
            # Định dạng dictionary gốc
            content = section.get("content", "")
            icon_name = section.get("icon", "chart-analysis")
            icon_svg = icons.get(icon_name, icons["chart-analysis"])
        
        sections_html += f'''
        <div class="content-section">
            <div class="icon-container">
                {icon_svg}
            </div>
            <div class="text-container">
                {content}
            </div>
        </div>
        '''

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            font-family: {font_family};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 100%;
            height: 100vh;
            display: flex;
            position: relative;
            background: linear-gradient(135deg, {right_bg_color} 0%, #e9ecef 100%);
        }}
        
        .slide-border {{
            position: absolute;
            top: 45px;
            left: 45px;
            right: 45px;
            bottom: 45px;
            border: {("3px dashed rgba(26, 75, 140, " + str(border_opacity) + ")" if show_border else "none")};
            border-radius: 12px;
            pointer-events: none;
            z-index: 5;
        }}
        
        .left-section {{
            width: 40%;
            background: linear-gradient(135deg, {left_bg_color} 0%, #0d2d5e 100%);
            color: {title_color};
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 100px 60px;
            position: relative;
            z-index: 10;
            box-shadow: 8px 0 30px rgba(0, 0, 0, 0.2);
        }}
        
        .title {{
            font-size: 6rem;
            font-weight: 900;
            line-height: 1.1;
            text-align: center;
            letter-spacing: 0.1em;
            text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
            text-transform: uppercase;
        }}
        
        .right-section {{
            width: 60%;
            padding: 100px 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 45px;
            position: relative;
            z-index: 10;
        }}
        
        .content-section {{
            display: flex;
            align-items: stretch;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
            border-radius: 16px;
            overflow: hidden;
            min-height: 140px;
        }}
        
        .icon-container {{
            width: {icon_size};
            min-width: {icon_size};
            background: linear-gradient(135deg, {icon_bg_color} 0%, #1a2942 100%);
            color: {icon_color};
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 30px;
        }}
        
        .icon-container svg {{
            filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.25));
        }}
        
        .text-container {{
            flex: 1;
            background: linear-gradient(135deg, {content_bg_color} 0%, #fafbfc 100%);
            color: {content_text_color};
            padding: 35px 45px;
            font-size: 2.5rem;
            line-height: 1.7;
            display: flex;
            align-items: center;
            font-weight: 500;
        }}
        
        /* Decorative elements */
        .left-section::before {{
            content: '';
            position: absolute;
            top: 0;
            right: -35px;
            width: 70px;
            height: 100%;
            background: linear-gradient(90deg, transparent 0%, {left_bg_color} 50%, transparent 100%);
            z-index: -1;
            opacity: 0.6;
        }}
        
        .left-section::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 130%;
            height: 130%;
            background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
            pointer-events: none;
        }}
        
        @media (max-width: 768px) {{
            .slide-container {{
                flex-direction: column;
            }}
            
            .left-section, .right-section {{
                width: 100%;
            }}
            
            .left-section {{
                height: 30%;
                padding: 30px 20px;
            }}
            
            .right-section {{
                height: 70%;
                padding: 30px 20px;
            }}
            
            .title {{
                font-size: 2.5rem;
            }}
            
            .content-section {{
                margin-bottom: 10px !important;
            }}
            
            .icon-container {{
                width: 60px;
                min-width: 60px;
                padding: 15px;
            }}
            
            .icon-container svg {{
                width: 30px;
                height: 30px;
            }}
            
            .text-container {{
                padding: 15px 20px;
                font-size: 0.85rem;
            }}
        }}
        
        @media (max-width: 480px) {{
            .slide-border {{
                top: 15px;
                left: 15px;
                right: 15px;
                bottom: 15px;
            }}
            
            .title {{
                font-size: 2rem;
            }}
            
            .text-container {{
                font-size: 0.8rem;
                padding: 12px 15px;
            }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Border frame -->
        <div class="slide-border"></div>
        
        <!-- Left section with title -->
        <div class="left-section">
            <h1 class="title">{main_title}</h1>
        </div>
        
        <!-- Right section with content -->
        <div class="right-section">
            {sections_html}
        </div>
    </div>
</body>
</html>"""

    return html_code



def generate_vision_mission_slide(
    vision_title="VISION",
    mission_title="MISSION",
    vision_points=[
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    ],
    mission_points=[
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    ],
    vision_bg_color="#1a4b8c",
    mission_bg_color="#4a7bc8",
    text_color="#FFFFFF",
    vision_number_color="rgba(74, 123, 200, 0.3)",
    mission_number_color="rgba(26, 75, 140, 0.3)",
    font_family="'Arial', sans-serif",
    show_border=True,
    border_color="#1a4b8c",
    border_opacity=0.4,
    show_geometric_pattern=True,
    pattern_opacity=0.1,
    custom_css=""
):
    """
    Generate a professional vision and mission slide with split layout and numbered points.

    :param vision_title: Title for the vision section (5-15 characters)
    :param mission_title: Title for the mission section (5-15 characters)
    :param vision_points: List of vision statements or list of lists where first element is vision text
    :param mission_points: List of mission statements or list of lists where first element is mission text
    :param vision_bg_color: Background color for the vision section (hex code)
    :param mission_bg_color: Background color for the mission section (hex code)
    :param text_color: Color of all text elements (hex code)
    :param title_font_size: Font size for section titles
    :param content_font_size: Font size for content text
    :param number_font_size: Font size for large background numbers
    :param vision_number_color: Color of background numbers in vision section (rgba)
    :param mission_number_color: Color of background numbers in mission section (rgba)
    :param font_family: Font family for all text elements
    :param show_border: Whether to show the dashed border frame
    :param border_color: Color of the border frame (hex code)
    :param border_opacity: Opacity of the border frame (0.0 to 1.0)
    :param show_geometric_pattern: Whether to show geometric background pattern
    :param pattern_opacity: Opacity of the geometric pattern (0.0 to 1.0)
    :param custom_css: Additional custom CSS to be included
    :return: A string containing the HTML code for the slide
    """

    # Generate vision points HTML
    vision_html = ""
    for i, point in enumerate(vision_points, 1):
        # Xử lý point dạng list hoặc string
        point_text = point[0] if isinstance(point, list) and len(point) > 0 else point
        
        vision_html += f'''
        <div class="content-point">
            <div class="point-number">{i:02d}</div>
            <div class="point-text">{point_text}</div>
        </div>
        '''

    # Generate mission points HTML
    mission_html = ""
    for i, point in enumerate(mission_points, 1):
        # Xử lý point dạng list hoặc string
        point_text = point[0] if isinstance(point, list) and len(point) > 0 else point
        
        mission_html += f'''
        <div class="content-point">
            <div class="point-number">{i:02d}</div>
            <div class="point-text">{point_text}</div>
        </div>
        '''

    # Generate background numbers for vision
    vision_bg_numbers = ""
    for i in range(1, len(vision_points) + 1):
        vision_bg_numbers += f'<div class="bg-number bg-number-{i}">{i:02d}</div>'

    # Generate background numbers for mission
    mission_bg_numbers = ""
    for i in range(1, len(mission_points) + 1):
        mission_bg_numbers += f'<div class="bg-number bg-number-{i}">{i:02d}</div>'

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{vision_title} & {mission_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            font-family: {font_family};
            overflow: hidden;
            background: linear-gradient(135deg, #e8f4f8 0%, #d1e7dd 100%);
        }}
        
        .slide-container {{
            width: 100%;
            height: 100vh;
            display: flex;
            position: relative;
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .slide-border {{
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            bottom: 20px;
            border: {("2px dashed " + border_color if show_border else "none")};
            opacity: {border_opacity};
            pointer-events: none;
            z-index: 5;
        }}
        
        .section {{
            width: 50%;
            position: relative;
            padding: 60px 40px;
            color: {text_color};
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        
        .vision-section {{
            background-color: {vision_bg_color};
            margin-right: 10px;
            margin-bottom: 10px;
        }}
        
        .mission-section {{
            background-color: {mission_bg_color};
            margin-left: 10px;
            margin-bottom: 10px;
        }}
        
        .section-title {{
            font-size: 6rem;
            font-weight: 700;
            margin-bottom: 80px;
            text-align: center;
            letter-spacing: 0.08em;
            z-index: 10;
            position: relative;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        .content-point {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 35px;
            position: relative;
            z-index: 10;
        }}
        
        .point-number {{
            font-size: 2.4rem;
            font-weight: 700;
            margin-right: 25px;
            min-width: 65px;
            opacity: 0.95;
        }}
        
        .point-text {{
            font-size: 1.8rem;
            line-height: 1.7;
            flex: 1;
            font-weight: 400;
        }}
        
        /* Background numbers */
        .bg-number {{
            position: absolute;
            font-size: 8rem;
            font-weight: 900;
            z-index: 1;
            pointer-events: none;
            user-select: none;
        }}
        
        .vision-section .bg-number {{
            color: {vision_number_color};
        }}
        
        .mission-section .bg-number {{
            color: {mission_number_color};
        }}
        
        .bg-number-1 {{
            top: 20%;
            right: -20px;
        }}
        
        .bg-number-2 {{
            bottom: 20%;
            left: -20px;
        }}
        
        .bg-number-3 {{
            top: 50%;
            right: -30px;
            transform: translateY(-50%);
        }}
        
        .bg-number-4 {{
            bottom: 10%;
            right: -25px;
        }}
        
        /* Geometric pattern */
        .geometric-pattern {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            opacity: {pattern_opacity if show_geometric_pattern else 0};
            z-index: 2;
            background-image: 
                linear-gradient(45deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%),
                linear-gradient(-45deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%);
            background-size: 60px 60px, 80px 80px;
            background-position: 0 0, 30px 30px;
        }}
        
        /* Decorative triangles */
        .triangle {{
            position: absolute;
            width: 0;
            height: 0;
            opacity: 0.1;
            z-index: 3;
        }}
        
        .triangle-1 {{
            border-left: 60px solid transparent;
            border-right: 60px solid transparent;
            border-bottom: 100px solid rgba(255, 255, 255, 0.2);
            top: 10%;
            left: 10%;
            transform: rotate(15deg);
        }}
        
        .triangle-2 {{
            border-left: 40px solid transparent;
            border-right: 40px solid transparent;
            border-bottom: 80px solid rgba(255, 255, 255, 0.2);
            bottom: 15%;
            right: 15%;
            transform: rotate(-25deg);
        }}
        
        @media (max-width: 768px) {{
            .slide-container {{
                flex-direction: column;
                padding: 20px;
            }}
            
            .section {{
                width: 100%;
                height: 50%;
                padding: 30px 20px;
            }}
            
            .vision-section {{
                margin-right: 0;
                margin-bottom: 10px;
            }}
            
            .mission-section {{
                margin-left: 0;
                margin-top: 10px;
            }}
            
            .section-title {{
                font-size: 3.5rem;
                margin-bottom: 30px;
            }}
            
            .point-text {{
                font-size: 1.4rem;
            }}
            
            .bg-number {{
                font-size: 4rem;
            }}
            
            .content-point {{
                margin-bottom: 20px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .section-title {{
                font-size: 2.8rem;
            }}
            
            .point-text {{
                font-size: 1.2rem;
            }}
            
            .point-number {{
                font-size: 1.8rem;
                margin-right: 18px;
                min-width: 40px;
            }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Border frame -->
        <div class="slide-border"></div>
        
        <!-- Vision Section -->
        <div class="section vision-section">
            <div class="geometric-pattern"></div>
            {vision_bg_numbers}
            <div class="triangle triangle-1"></div>
            
            <h1 class="section-title">{vision_title}</h1>
            <div class="content-area">
                {vision_html}
            </div>
        </div>
        
        <!-- Mission Section -->
        <div class="section mission-section">
            <div class="geometric-pattern"></div>
            {mission_bg_numbers}
            <div class="triangle triangle-2"></div>
            
            <h1 class="section-title">{mission_title}</h1>
            <div class="content-area">
                {mission_html}
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_code


def generate_strategic_goals_slide(
    main_title="STRATEGIC GOALS",
    goals=[
        {
            "number": "01",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        },
        {
            "number": "02",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        },
        {
            "number": "03",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        }
    ],
    bg_image="skyscrapers.jpg",
    bg_overlay_color="rgba(26, 75, 140, 0.85)",
    title_color="#FFFFFF",
    number_bg_color="#1a4b8c",
    number_text_color="#FFFFFF",
    content_bg_color="#FFFFFF",
    content_text_color="#1a4b8c",
    font_family="'Arial', sans-serif",
    show_border=True,
    border_opacity=0.4,
    number_circle_size="80px",
    content_padding="20px",
    custom_css=""
):
    """
    Generate a professional strategic goals slide with numbered points and background image.

    :param main_title: Main title text (10-25 characters), displayed on the left side
    :param goals: List of dictionaries with number and content for each strategic goal,
                 or list of lists where first element is content and second is number
    :param bg_image: Background image URL or path (skyscraper/city image recommended)
    :param bg_overlay_color: Color overlay for the background image (rgba with transparency)
    :param title_color: Color of the main title text (hex code)
    :param number_bg_color: Background color for the number circles (hex code)
    :param number_text_color: Text color for the numbers (hex code)
    :param content_bg_color: Background color for content text boxes (hex code)
    :param content_text_color: Text color for content (hex code)
    :param title_font_size: Font size for the main title
    :param number_font_size: Font size for the numbers
    :param content_font_size: Font size for content text
    :param font_family: Font family for all text elements
    :param show_border: Whether to show the dashed border frame
    :param border_opacity: Opacity of the border frame (0.0 to 1.0)
    :param number_circle_size: Size of the circular number containers
    :param content_padding: Padding inside content boxes
    :param custom_css: Additional custom CSS to be included
    :return: A string containing the HTML code for the slide
    """

    # Generate goals HTML
    goals_html = ""
    for i, goal in enumerate(goals):
        # Xử lý goal dạng list hoặc dictionary
        if isinstance(goal, list):
            # Nếu goal là list thì giả định [content, number]
            if len(goal) >= 2:
                # Kiểm tra loại dữ liệu của phần tử đầu tiên
                if isinstance(goal[0], str) and not goal[0].isdigit():
                    content = goal[0]
                    number = goal[1] if len(goal) > 1 and goal[1] else f"{i+1:02d}"
                else:
                    number = goal[0] if goal[0] else f"{i+1:02d}"
                    content = goal[1] if len(goal) > 1 else ""
            else:
                content = goal[0] if len(goal) > 0 else ""
                number = f"{i+1:02d}"
        else:
            # Đối với dictionary, sử dụng get() như trước
            number = goal.get("number", f"{i+1:02d}")
            content = goal.get("content", "")
        
        goals_html += f'''
        <div class="goal-item">
            <div class="number-circle">
                <span>{number}</span>
            </div>
            <div class="content-box">
                <div class="content-text">{content}</div>
            </div>
        </div>
        '''

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            font-family: {font_family};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 100%;
            height: 100vh;
            position: relative;
            background-image: url('{bg_image}');
            background-size: cover;
            background-position: center;
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .bg-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: {bg_overlay_color};
            z-index: 1;
        }}
        
        .slide-border {{
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            bottom: 20px;
            border: {("2px dashed rgba(255, 255, 255, " + str(border_opacity) + ")" if show_border else "none")};
            pointer-events: none;
            z-index: 5;
        }}
        
        .content-wrapper {{
            position: relative;
            z-index: 10;
            display: flex;
            height: 100%;
        }}
        
        .title-section {{
            width: 40%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .main-title {{
            font-size: 4.5rem;
            font-weight: 700;
            color: {title_color};
            line-height: 1.1;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .goals-section {{
            width: 60%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 20px;
        }}
        
        .goal-item {{
            display: flex;
            align-items: center;
        }}
        
        .number-circle {{
            width: {number_circle_size};
            height: {number_circle_size};
            min-width: {number_circle_size};
            background-color: {number_bg_color};
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 20px;
            z-index: 20;
            position: relative;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        
        .number-circle span {{
            color: {number_text_color};
            font-size: 2.5rem;
            font-weight: 700;
        }}
        
        .content-box {{
            flex: 1;
            background-color: {content_bg_color};
            border-radius: 8px;
            padding: {content_padding};
            padding-left: {content_padding};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10;
            position: relative;
        }}
        
        .content-text {{
            color: {content_text_color};
            font-size: 0.9rem;
            line-height: 1.5;
        }}
        
        @media (max-width: 768px) {{
            .content-wrapper {{
                flex-direction: column;
            }}
            
            .title-section, .goals-section {{
                width: 100%;
            }}
            
            .title-section {{
                height: 30%;
                align-items: flex-start;
                justify-content: center;
            }}
            
            .goals-section {{
                height: 70%;
            }}
            
            .main-title {{
                font-size: 2.5rem;
                text-align: center;
                margin-top: 20px;
            }}
            
            .number-circle {{
                width: 60px;
                height: 60px;
                min-width: 60px;
                margin-right: 15px;
            }}
            
            .number-circle span {{
                font-size: 1.8rem;
            }}
            
            .content-box {{
                padding: 15px;
            }}
            
            .content-text {{
                font-size: 0.8rem;
            }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Background overlay -->
        <div class="bg-overlay"></div>
        
        <!-- Border frame -->
        <div class="slide-border"></div>
        
        <!-- Content -->
        <div class="content-wrapper">
            <!-- Title section -->
            <div class="title-section">
                <h1 class="main-title">{main_title}</h1>
            </div>
            
            <!-- Goals section -->
            <div class="goals-section">
                {goals_html}
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_code




def generate_service_roadmap_slide(
    main_title="SERVICE ROADMAP",
    roadmap_items=[
        {
            "title": "Phase 1",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        },
        {
            "title": "Phase 2", 
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        },
        {
            "title": "Phase 3",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        },
        {
            "title": "Phase 4",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        }
    ],
    bg_gradient_start="#4A90E2",
    bg_gradient_end="#2E5BBA",
    title_color="#FFFFFF",
    card_bg_color="#FFFFFF",
    card_text_color="#2E5BBA",
    card_title_color="#1A4480",
    font_family="'Arial', sans-serif",
    show_border=True,
    border_color="rgba(255, 255, 255, 0.3)",
    show_decorative_triangles=True,
    triangle_color="rgba(255, 255, 255, 0.1)",
    card_border_radius="20px",
    card_padding="25px",
    card_shadow="0 8px 24px rgba(0, 0, 0, 0.15)",
    custom_css=""
):
    """
    Generate a professional service roadmap slide with gradient background and decorative elements.

    :param main_title: Main title text (10-30 characters), displayed at the top center
    :param roadmap_items: List of dictionaries with title and content for each roadmap phase,
                         or list of lists where first element is title and second is content
    :param bg_gradient_start: Starting color of the background gradient (hex code)
    :param bg_gradient_end: Ending color of the background gradient (hex code)
    :param title_color: Color of the main title text (hex code)
    :param card_bg_color: Background color for content cards (hex code)
    :param card_text_color: Text color for card content (hex code)
    :param card_title_color: Text color for card titles (hex code)
    :param title_font_size: Font size for the main title
    :param card_title_font_size: Font size for card titles
    :param card_content_font_size: Font size for card content text
    :param font_family: Font family for all text elements
    :param show_border: Whether to show the dashed border frame
    :param border_color: Color of the border frame (rgba with transparency)
    :param show_decorative_triangles: Whether to show decorative triangle elements
    :param triangle_color: Color of the decorative triangles (rgba with transparency)
    :param card_border_radius: Border radius for content cards
    :param card_padding: Padding inside content cards
    :param card_shadow: Box shadow for content cards
    :param custom_css: Additional custom CSS to be included
    :return: A string containing the HTML code for the slide
    """

    # Generate roadmap items HTML
    items_html = ""
    for i, item in enumerate(roadmap_items):
        # Xử lý item dạng list hoặc dictionary
        if isinstance(item, list):
            # Giả định dữ liệu dạng [title, content]
            title = item[0] if len(item) > 0 else f"Phase {i+1}"
            content = item[1] if len(item) > 1 else ""
        else:
            # Định dạng dictionary gốc
            title = item.get("title", f"Phase {i+1}")
            content = item.get("content", "")
            
        items_html += f'''
        <div class="roadmap-card">
            <h3 class="card-title">{title}</h3>
            <div class="card-content">{content}</div>
        </div>
        '''

    # Generate decorative triangles
    triangles_html = ""
    if show_decorative_triangles:
        triangles_html = '''
        <!-- Top triangles -->
        <div class="triangle triangle-top-left"></div>
        <div class="triangle triangle-top-right"></div>
        
        <!-- Bottom triangles -->
        <div class="triangle triangle-bottom-left"></div>
        <div class="triangle triangle-bottom-right"></div>
        '''

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            font-family: {font_family};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 100%;
            height: 100vh;
            position: relative;
            background: linear-gradient(135deg, {bg_gradient_start} 0%, {bg_gradient_end} 100%);
            padding: 40px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }}
        
        .slide-border {{
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            bottom: 20px;
            border: {("2px dashed " + border_color if show_border else "none")};
            pointer-events: none;
            z-index: 5;
        }}
        
        .triangle {{
            position: absolute;
            width: 0;
            height: 0;
            z-index: 2;
        }}
        
        .triangle-top-left {{
            top: 0;
            left: 0;
            border-left: 120px solid {triangle_color};
            border-bottom: 120px solid transparent;
        }}
        
        .triangle-top-right {{
            top: 0;
            right: 0;
            border-right: 120px solid {triangle_color};
            border-bottom: 120px solid transparent;
        }}
        
        .triangle-bottom-left {{
            bottom: 0;
            left: 0;
            border-left: 120px solid {triangle_color};
            border-top: 120px solid transparent;
        }}
        
        .triangle-bottom-right {{
            bottom: 0;
            right: 0;
            border-right: 120px solid {triangle_color};
            border-top: 120px solid transparent;
        }}
        
        .content-wrapper {{
            position: relative;
            z-index: 10;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        
        .title-section {{
            text-align: center;
            margin-bottom: 60px;
            margin-top: 40px;
        }}
        
        .main-title {{
            font-size: 6rem;
            font-weight: 700;
            color: {title_color};
            letter-spacing: 0.1em;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            margin: 0;
        }}
        
        .roadmap-grid {{
            flex: 1;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
        }}
        
        .roadmap-card {{
            background-color: {card_bg_color};
            border-radius: {card_border_radius};
            padding: {card_padding};
            box-shadow: {card_shadow};
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .roadmap-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
        }}
        
        .roadmap-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, {bg_gradient_start}, {bg_gradient_end});
        }}
        
        .card-title {{
            font-size: 3rem;
            font-weight: 700;
            color: {card_title_color};
            margin: 0 0 15px 0;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .card-content {{
            font-size: 2.1rem;
            color: {card_text_color};
            line-height: 1.6;
            margin: 0;
        }}
        
        @media (max-width: 768px) {{
            .slide-container {{
                padding: 20px;
            }}
            
            .main-title {{
                font-size: 2.5rem;
            }}
            
            .roadmap-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            .roadmap-card {{
                padding: 20px;
            }}
            
            .card-title {{
                font-size: 1rem;
            }}
            
            .card-content {{
                font-size: 0.8rem;
            }}
            
            .triangle {{
                display: none;
            }}
        }}
        
        @media (max-width: 480px) {{
            .title-section {{
                margin-bottom: 30px;
                margin-top: 20px;
            }}
            
            .main-title {{
                font-size: 2rem;
            }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Decorative triangles -->
        {triangles_html}
        
        <!-- Border frame -->
        <div class="slide-border"></div>
        
        <!-- Content -->
        <div class="content-wrapper">
            <!-- Title section -->
            <div class="title-section">
                <h1 class="main-title">{main_title}</h1>
            </div>
            
            <!-- Roadmap grid -->
            <div class="roadmap-grid">
                {items_html}
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_code




def generate_financial_projections_slide_dark(
    # Main title
    main_title="FINANCIAL PROJECTIONS",
    
    # Card content
    cards=[
        {
            "title": "REVENUE FORECASTS",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse quis enim pretium, bibendum ante ullamcorper, tincidunt augue. Nunc sed lorem aliquam, malesuada lectus eu, placerat lorem. Proin at aliquet sapien, vitae elementum mi."
        },
        {
            "title": "EXPENSE PROJECTIONS", 
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse quis enim pretium, bibendum ante ullamcorper, tincidunt augue. Nunc sed lorem aliquam, malesuada lectus eu, placerat lorem. Proin at aliquet sapien, vitae elementum mi."
        },
        {
            "title": "FUNDING REQUIREMENTS",
            "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse quis enim pretium, bibendum ante ullamcorper, tincidunt augue. Nunc sed lorem aliquam, malesuada lectus eu, placerat lorem. Proin at aliquet sapien, vitae elementum mi."
        }
    ],
    
    # Colors - Dark Theme
    background_color="#1E3A8A",  # Deep blue
    main_title_color="#FFFFFF",
    card_background_color="rgba(255, 255, 255, 0.95)",
    card_title_color="#1E3A8A",
    card_content_color="#374151",
    border_color="rgba(255, 255, 255, 0.3)",
    
    # Typography
    font_family="'Segoe UI', 'Arial', sans-serif",
    main_title_font_weight="700",
    main_title_letter_spacing="0.05em",
    card_title_font_weight="700",
    card_title_letter_spacing="0.02em",
    card_content_line_height="1.6",
    card_content_font_weight="400",
    
    # Layout
    slide_padding="60px",
    main_title_margin_bottom="80px",
    cards_gap="40px",
    card_padding="40px",
    card_border_radius="12px",
    card_shadow="0 8px 32px rgba(0, 0, 0, 0.2)",
    card_title_margin_bottom="25px",
    
    # Border frame
    show_border_frame=True,
    frame_border_style="3px dashed",
    frame_border_color="rgba(255, 255, 255, 0.4)",
    frame_border_radius="12px",
    frame_padding="80px",
    
    # Responsive
    mobile_title_font_size="2.8rem",
    mobile_card_title_font_size="1.4rem",
    mobile_card_content_font_size="0.9rem",
    mobile_cards_gap="20px",
    mobile_card_padding="25px",
    mobile_slide_padding="30px",
    mobile_frame_padding="40px",
    
    # Additional styling
    additional_css=""
):
    """
    Generate an HTML slide for financial projections with dark blue theme and three cards.
    
    :param main_title: Main title displayed at the top of the slide
    :param cards: List of dictionaries with 'title' and 'content' keys for each card,
                 or list of lists where first element is title and second is content
    :param background_color: Solid background color (dark blue)
    :param main_title_color: Color of the main title text
    :param card_background_color: Background color of the cards
    :param card_title_color: Color of the card titles
    :param card_content_color: Color of the card content text
    :param border_color: Color of the border elements
    :param font_family: Font family for all text elements
    :param main_title_font_size: Font size of the main title
    :param main_title_font_weight: Font weight of the main title
    :param main_title_letter_spacing: Letter spacing of the main title
    :param card_title_font_size: Font size of the card titles
    :param card_title_font_weight: Font weight of the card titles
    :param card_title_letter_spacing: Letter spacing of the card titles
    :param card_content_font_size: Font size of the card content
    :param card_content_line_height: Line height of the card content
    :param card_content_font_weight: Font weight of the card content
    :param slide_padding: Padding around the entire slide
    :param main_title_margin_bottom: Bottom margin below the main title
    :param cards_gap: Gap between the cards
    :param card_padding: Internal padding within each card
    :param card_border_radius: Border radius of the cards
    :param card_shadow: Box shadow of the cards
    :param card_title_margin_bottom: Bottom margin below card titles
    :param show_border_frame: Whether to show dashed border frame
    :param frame_border_style: Style of the border frame
    :param frame_border_color: Color of the border frame
    :param frame_border_radius: Border radius of the frame
    :param frame_padding: Padding inside the border frame
    :param mobile_title_font_size: Main title font size on mobile
    :param mobile_card_title_font_size: Card title font size on mobile
    :param mobile_card_content_font_size: Card content font size on mobile
    :param mobile_cards_gap: Gap between cards on mobile
    :param mobile_card_padding: Card padding on mobile
    :param mobile_slide_padding: Slide padding on mobile
    :param mobile_frame_padding: Frame padding on mobile
    :param additional_css: Additional CSS to include
    :return: A string containing the HTML code for the slide
    """
    
    # Generate cards HTML
    cards_html = ""
    for card in cards:
        # Handle both dictionary and list formats
        if isinstance(card, list):
            # Assume list format: [title, content]
            title = card[0] if len(card) > 0 else ""
            content = card[1] if len(card) > 1 else ""
        else:
            # Original dictionary format
            title = card.get('title', '')
            content = card.get('content', '')
        
        cards_html += f"""
        <div class="financial-card">
            <h2 class="card-title">{title}</h2>
            <p class="card-content">{content}</p>
        </div>
        """
    
    # Generate border frame
    frame_class = "content-frame" if show_border_frame else "content-frame no-border"
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body, html {{
            height: 100%;
            font-family: {font_family};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 100vw;
            height: 100vh;
            background-color: {background_color};
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: {slide_padding};
            position: relative;
            box-sizing: border-box;
        }}
        
        .content-frame {{
            width: 100%;
            max-width: 1400px;
            padding: {frame_padding};
            position: relative;
            text-align: center;
        }}
        
        .content-frame:not(.no-border) {{
            border: {frame_border_style} {frame_border_color};
            border-radius: {frame_border_radius};
        }}
        
        .main-title {{
            font-size: 4.5rem;
            font-weight: {main_title_font_weight};
            color: {main_title_color};
            margin-bottom: {main_title_margin_bottom};
            letter-spacing: {main_title_letter_spacing};
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .cards-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: {cards_gap};
            width: 100%;
        }}
        
        .financial-card {{
            background-color: {card_background_color};
            padding: {card_padding};
            border-radius: {card_border_radius};
            box-shadow: {card_shadow};
            text-align: left;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        
        .financial-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        }}
        
        .card-title {{
            font-size: 2.3rem;
            font-weight: {card_title_font_weight};
            color: {card_title_color};
            margin-bottom: {card_title_margin_bottom};
            letter-spacing: {card_title_letter_spacing};
            text-align: center;
        }}
        
        .card-content {{
            font-size: 1.5rem;
            line-height: {card_content_line_height};
            color: {card_content_color};
            font-weight: {card_content_font_weight};
            margin: 0;
        }}
        
        /* Responsive Design */
        @media (max-width: 1200px) {{
            .cards-container {{
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 30px;
            }}
            
            .main-title {{
                font-size: 3.5rem;
            }}
            
            .content-frame {{
                padding: 60px;
            }}
        }}
        
        @media (max-width: 768px) {{
            .slide-container {{
                padding: {mobile_slide_padding};
            }}
            
            .content-frame {{
                padding: {mobile_frame_padding};
            }}
            
            .main-title {{
                font-size: {mobile_title_font_size};
                margin-bottom: 50px;
            }}
            
            .cards-container {{
                grid-template-columns: 1fr;
                gap: {mobile_cards_gap};
            }}
            
            .financial-card {{
                padding: {mobile_card_padding};
            }}
            
            .card-title {{
                font-size: {mobile_card_title_font_size};
            }}
            
            .card-content {{
                font-size: {mobile_card_content_font_size};
            }}
        }}
        
        @media (max-width: 480px) {{
            .main-title {{
                font-size: 2.2rem;
                margin-bottom: 40px;
            }}
            
            .card-title {{
                font-size: 1.2rem;
            }}
            
            .card-content {{
                font-size: 0.85rem;
            }}
            
            .financial-card {{
                padding: 20px;
            }}
            
            .content-frame {{
                padding: 30px 20px;
            }}
        }}
        
        {additional_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="{frame_class}">
            <h1 class="main-title">{main_title}</h1>
            
            <div class="cards-container">
                {cards_html}
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    return html_code



def generate_minimalist_tech_list_slide(
    title="This is a slide title",
    list_items=[
        "Here you have a list of items",
        "And some text",
        "But remember not to overload your slides with content"
    ],
    concluding_text="Your audience will listen to you or read the content, but won’t do both.",
    font_family="'Nunito', sans-serif",
    sky_top_color="#ABB0EA",
    sky_bottom_color="#A2CFED",
    grid_dot_color="rgba(0, 0, 0, 0.05)",
    text_color="#1F2937",
    accent_color="#6366F1",
    font_size_multiplier=1.0,
    title_font_size=None,
    list_item_font_size=None,
    concluding_text_font_size=None,
    custom_css=""
):
    """
    Generates a bright, clean, and STATIC tech-themed list slide.
    Animated rockets have been removed.
    """
    
    bullet_svg = f"""
    <svg class="bullet-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="9" stroke="{accent_color}" stroke-width="2" fill="#FFFFFF" />
        <circle cx="12" cy="12" r="4" fill="{accent_color}" />
    </svg>
    """
    
    list_items_html = "".join([f'<li class="list-item">{bullet_svg}<span>{item}</span></li>' for item in list_items])
    
    # ĐÃ XÓA: Phần tạo HTML cho tên lửa.
    rockets_html = ""

    # Logic sinh font-size giữ nguyên
    if title_font_size: title_style = f"font-size: {title_font_size};"
    else: title_style = f"font-size: clamp(calc(4rem * {font_size_multiplier}), calc((5vw + 1.5rem) * {font_size_multiplier}), calc(6.5rem * {font_size_multiplier}));"
    if list_item_font_size: list_item_style = f"font-size: {list_item_font_size};"
    else: list_item_style = f"font-size: clamp(calc(1.8rem * {font_size_multiplier}), calc((2vw + 0.5rem) * {font_size_multiplier}), calc(2.4rem * {font_size_multiplier}));"
    if concluding_text_font_size: concluding_text_style = f"font-size: {concluding_text_font_size};"
    else: concluding_text_style = f"font-size: clamp(calc(1.8rem * {font_size_multiplier}), calc((2vw + 0.5rem) * {font_size_multiplier}), calc(2.4rem * {font_size_multiplier}));"

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bright Tech List Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{
            height: 100vh; width: 100vw; font-family: {font_family};
            overflow: hidden;
            background-color: {sky_top_color};
            background-image: 
                radial-gradient(circle, {grid_dot_color} 1px, transparent 1px),
                linear-gradient(to bottom, {sky_top_color}, {sky_bottom_color});
            background-size: 25px 25px, 100% 100%;
        }}
        .slide-container {{
            width: 100%; height: 100%; display: flex;
            align-items: center; position: relative;
        }}
        
        /* ĐÃ XÓA: Toàn bộ CSS cho tên lửa và animation peek */

        .accent-border {{
            position: absolute;
            left: 4rem; top: 4rem; bottom: 4rem;
            width: 5px;
            background: {accent_color};
            border-radius: 3px;
        }}
        
        .content-wrapper {{
            z-index: 10;
            padding: 4rem 4rem 4rem 8rem;
            max-width: 70%;
        }}
        
        .slide-title {{
            {title_style}
            font-weight: 800; color: {text_color};
            margin-bottom: 3rem;
        }}
        .item-list {{ list-style: none; margin-bottom: 2.5rem; }}
        .list-item {{
            display: flex; align-items: flex-start;
            {list_item_style}
            color: {text_color}; line-height: 1.8;
            margin-bottom: 1.5rem;
        }}
        .bullet-icon {{
            width: 1.2em; height: 1.2em;
            margin-right: 1.2rem; margin-top: 0.2em;
            flex-shrink: 0;
        }}
        .concluding-text {{
            {concluding_text_style}
            color: {text_color}; line-height: 1.8;
            border-left: 4px solid {accent_color};
            padding-left: 1.5rem;
            font-style: italic;
        }}
        
        @media (max-width: 768px) {{
            .content-wrapper {{ max-width: 90%; padding: 4rem 2rem; }}
            .accent-border {{ left: 1.5rem; top: 2rem; bottom: 2rem; }}
            .slide-container {{ justify-content: center; text-align: center; }}
            .list-item, .concluding-text {{ text-align: left; }}
        }}
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="accent-border"></div>
        {rockets_html}
        <div class="content-wrapper">
            <h1 class="slide-title">{title}</h1>
            <ul class="item-list">
                {list_items_html}
            </ul>
            <p class="concluding-text">{concluding_text}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_code



def generate_centered_tech_columns_slide(
    title="You can also split your content",
    columns=[
        { "icon_name": "bulb", "title": "Column One", "description": "Description for column one." },
        { "icon_name": "target", "title": "Column Two", "description": "Description for column two." }
    ],
    page_number=None,
    font_family="'Nunito', sans-serif",
    text_color="#F8FAFC",
    page_number_color="#94A3B8",
    sky_top_color="#0F172A",
    sky_bottom_color="#1E293B",
    grid_dot_color="rgba(255, 255, 255, 0.1)",
    accent_color="#22D3EE",
    card_bg_color="rgba(30, 41, 59, 0.5)"
):
    """
    Generates a high-tech, STATIC slide with a top-aligned layout. 
    Animated rockets have been removed.
    """
    
    icons = {
        "bulb": '<path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-2.26c1.81-1.27 3-3.36 3-5.74A7 7 0 0 0 12 2M9 21a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-1H9z"/>',
        "target": '<path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2m0 18a8 8 0 1 1 8-8a8 8 0 0 1-8 8m0-14a6 6 0 1 0 6 6a6 6 0 0 0-6-6m0 10a4 4 0 1 1 4-4a4 4 0 0 1-4 4m0-6a2 2 0 1 0 2 2a2 2 0 0 0-2-2"/>',
        "rocket": '<path d="M5.5 2.5L2 6l3.5 3.5L2 13l3.5 3.5L9 13l3.5 3.5L16 13l-3.5-3.5L16 6l-3.5-3.5L9 6z"/>'
    }

    columns_html = ""
    for col in columns:
        icon_svg = icons.get(col.get("icon_name"), "")
        columns_html += f"""
        <div class="column-card">
            <div class="column-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">{icon_svg}</svg>
            </div>
            <h2 class="column-title">{col["title"]}</h2>
            <p class="column-description">{col["description"]}</p>
        </div>
        """

    page_number_html = f'<div class="page-number">{page_number}</div>' if page_number else ""
    
    # ĐÃ XÓA: Phần tạo HTML cho tên lửa.
    rockets_html = ""

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>High-Tech Columns Slide - Top Aligned</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, html {{ height: 100vh; width: 100vw; font-family: {font_family}; overflow: hidden; }}
        .slide-container {{
            width: 100%; height: 100%; display: flex;
            justify-content: flex-start; 
            align-items: center;
            flex-direction: column;
            position: relative; 
            padding: 6rem 4rem;
            background-color: {sky_top_color};
        }}
        
        /* ĐÃ XÓA: Toàn bộ CSS cho tên lửa và animation peek */
        
        .content-wrapper {{ z-index: 10; color: {text_color}; text-align: center; width: 100%; max-width: 100rem; }}
        
        .slide-title {{
            font-size: clamp(5rem, 7vw, 5.5rem);
            font-weight: 800;
            margin-bottom: 15rem;
        }}
        
        .columns-grid {{
            display: grid;
            grid-template-columns: repeat({len(columns)}, 1fr);
            gap: 5rem;
        }}

        .column-card {{
            background: {card_bg_color};
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid {accent_color};
            box-shadow: 0 0 20px {accent_color}33;
            padding: 5rem;
            border-radius: 1rem;
            text-align: left;
        }}

        .column-icon {{
            color: {accent_color};
            margin-bottom: 2rem;
        }}
        .column-icon svg {{
            width: 5rem;
            height: 5rem;
        }}

        .column-title {{
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: {text_color};
        }}
        .column-description {{
            font-size: 2.2rem;
            line-height: 1.7;
            opacity: 0.8;
            color: {text_color};
        }}
        .page-number {{
            position: absolute; bottom: 2rem; left: 50%;
            transform: translateX(-50%); font-size: 1rem;
            font-weight: 700; color: {page_number_color};
            z-index: 10;
        }}
        @media (max-width: 64rem) {{
            .slide-container {{ padding-top: 4rem; overflow-y: auto; height: auto; min-height: 100vh; }}
            .columns-grid {{ grid-template-columns: 1fr; }}
            .slide-title {{ text-align: center; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        {rockets_html}
        <div class="content-wrapper">
            <h1 class="slide-title">{title}</h1>
            <div class="columns-grid">
                {columns_html}
            </div>
        </div>
        {page_number_html}
    </div>
</body>
</html>"""
    
    return html_code



def generate_split_layout_list_slide(
    main_title="YOUR MAIN TOPIC",
    points=[
        {
            "title": "ADD A KEY POINT",
            "description": "Briefly elaborate on this key point to provide more details and context for your audience."
        },
        {
            "title": "ADD A KEY POINT", 
            "description": "Briefly elaborate on this key point to provide more details and context for your audience."
        },
        {
            "title": "ADD A KEY POINT",
            "description": "Briefly elaborate on this key point to provide more details and context for your audience."
        }
    ],
    font_family="'Be Vietnam Pro', sans-serif",
    left_bg_color="#6F6254",
    right_bg_color="#F5F0E8",
    light_text_color="#F5F0E8",
    dark_text_color="#6F6254",
    divider_color="#D3CFC7",
    # Font control parameters
    main_title_font_size=None,
    point_title_font_size=None,
    point_description_font_size=None,
    custom_css=""
):
    """
    Generates a professional Split-Layout List slide, offering both responsive and fixed font size controls.
    """

    points_html = ""
    for point in points:
        points_html += f"""
        <div class="point-item">
            <h2 class="point-title">{point['title']}</h2>
            <p class="point-description">{point['description']}</p>
        </div>
        """

    # Generate CSS for font sizes based on parameters
    # Main Title Style
    if main_title_font_size:
        main_title_style = f"font-size: {main_title_font_size};"
    else:
        main_title_style = f"font-size: clamp(calc(2.5rem * 1.3), calc(6vw * 1.3), calc(4rem * 1.3));"
    
    # Point Title Style
    if point_title_font_size:
        point_title_style = f"font-size: {point_title_font_size};"
    else:
        point_title_style = f"font-size: clamp(calc(1.1rem * 1.3), calc((1.5vw + 0.2rem) * 1.3), calc(1.35rem * 1.3));"

    # Point Description Style
    if point_description_font_size:
        point_desc_style = f"font-size: {point_description_font_size};"
    else:
        point_desc_style = f"font-size: clamp(calc(1rem * 1.3), calc((1vw + 0.1rem) * 1.3), calc(1.1rem * 1.3));"

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Split-Layout List Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh; width: 100vw;
            font-family: {font_family}; overflow: hidden;
        }}
        .slide-container {{ width: 100%; height: 100%; display: flex; }}
        .left-column {{
            flex: 1; max-width: 35%;
            background-color: {left_bg_color}; color: {light_text_color};
            padding: 3rem; display: flex; flex-direction: column;
            justify-content: center; align-items: center; text-align: center;
        }}
        .right-column {{
            flex: 2; background-color: {right_bg_color}; color: {dark_text_color};
            padding: 4rem 3rem; overflow-y: auto;
        }}
        .points-list {{ display: flex; flex-direction: column; gap: 2rem; }}
        .point-item:not(:last-child) {{
            padding-bottom: 2rem; border-bottom: 1px solid {divider_color};
        }}

        /* Font size styles */
        .main-title {{
            {main_title_style}
            font-weight: 900; line-height: 1.2; text-transform: uppercase;
        }}
        .point-title {{
            {point_title_style}
            font-weight: 900; text-transform: uppercase; margin-bottom: 0.75rem;
        }}
        .point-description {{
            {point_desc_style}
            line-height: 1.6; font-weight: 400; max-width: 45rem;
        }}
        
        @media (max-width: 768px) {{
            .slide-container {{ flex-direction: column; overflow-y: auto; }}
            .left-column {{ max-width: 100%; width: 100%; flex: none; height: auto; min-height: 12rem; padding: 2rem; }}
            .right-column {{ flex: none; width: 100%; padding: 2.5rem 2rem; }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="left-column">
            <h1 class="main-title">{main_title}</h1>
        </div>
        <div class="right-column">
            <div class="points-list">
                {points_html}
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code




def generate_reference_slide(
    main_title="CONTENT",
    reference_items=[
        {
            "title": "PRIMARY REFERENCE TITLE",
            "description": "Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. They serve various purposes and are effective tools."
        },
        {
            "title": "SECONDARY REFERENCE TITLE",
            "description": "Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. They serve various purposes and are effective tools."
        }
    ],
    # ĐÃ THAY ĐỔI: Đặt một URL ảnh mặc định chất lượng cao, hoạt động tốt
    image_url="https://images.unsplash.com/photo-1543269865-cbf427effbad?q=80&w=2070&auto=format&fit=crop",
    font_family="'Be Vietnam Pro', sans-serif",
    bg_color="#FFFFFF",
    text_color="#1F2937",
    accent_color="#3B82F6"
):
    """
    Generates a professional reference slide with large fonts, a default high-quality image,
    and elegant decorative elements.
    """

    items_html = ""
    for item in reference_items:
        items_html += f"""
        <div class="reference-item">
            <h2 class="reference-title">{item['title']}</h2>
            <p class="reference-description">{item['description']}</p>
        </div>
        """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reference Slide - Enhanced</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
        }}

        .text-column {{
            flex: 0.6; 
            background-color: {bg_color};
            color: {text_color};
            padding: 5rem 6rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .image-column {{
            flex: 0.4;
            background-image: url('{image_url}');
            background-size: cover;
            background-position: center;
        }}

        .main-title {{
            font-size: 5rem;
            font-weight: 900;
            text-transform: uppercase;
            margin-bottom: 1.5rem;
        }}
        
        .title-divider {{
            width: 100px;
            height: 5px;
            background: {accent_color};
            border: none;
            border-radius: 3px;
            margin-bottom: 4rem;
        }}

        .references-list {{
            display: flex;
            flex-direction: column;
            gap: 3rem;
        }}

        .reference-title {{
            font-size: 2.4rem;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 1rem;
        }}

        .reference-description {{
            font-size: 2rem;
            line-height: 1.7;
            font-weight: 400;
            max-width: 45rem;
        }}
        
        @media (max-width: 64rem) {{
             .text-column {{ padding: 4rem; }}
        }}

        @media (max-width: 48rem) {{
            .slide-container {{
                flex-direction: column-reverse; 
                overflow-y: auto;
                height: auto;
                min-height: 100vh;
            }}
            .text-column, .image-column {{
                flex: none;
                width: 100%;
            }}
            .image-column {{
                height: 20rem; 
            }}
             .text-column {{
                padding: 3rem 2rem;
             }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="text-column">
            <h1 class="main-title">{main_title}</h1>
            <hr class="title-divider" />
            <div class="references-list">
                {items_html}
            </div>
        </div>
        <div class="image-column"></div>
    </div>
</body>
</html>"""
    
    return html_code






def generate_icon_list_slide(
    main_title="Write your topic or idea",
    points=[
        { "icon_name": "megaphone", "title": "Add a main point", "description": "Briefly elaborate on what you want to discuss." },
        { "icon_name": "star", "title": "Add a main point", "description": "Briefly elaborate on what you want to discuss." },
        { "icon_name": "thumbs-up", "title": "Add a main point", "description": "Briefly elaborate on what you want to discuss." }
    ],
    font_family="'Montserrat', sans-serif",
    bg_color="#FFFFFF",
    main_title_color="#111827",
    point_title_color="#1F2937",
    point_description_color="#4B5563",
    accent_color="#3B82F6"
):
    """
    Generates an icon list slide optimized for 1920x1080 screenshots
    with an adjusted layout that emphasizes the list of points over the main title.
    """

    icons = {
        "megaphone": '<path d="M12 8V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v3H2l-1.99 9.95A2 2 0 002 20h12c1.1 0 2-.9 2-2v-3h2v-4h-4zm-2 0H6V5h4v3z"/>',
        "star": '<path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>',
        "thumbs-up": '<path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/>'
    }

    points_html = ""
    for point in points:
        icon_svg_path = icons.get(point['icon_name'], "")
        points_html += f"""
        <div class="point-item">
            <div class="icon-circle" style="background-color: {accent_color};">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" width="50px" height="50px">
                    {icon_svg_path}
                </svg>
            </div>
            <div class="text-content">
                <h2 class="point-title" style="color: {point_title_color};">{point['title']}</h2>
                <p class="point-description" style="color: {point_description_color};">{point['description']}</p>
            </div>
        </div>
        """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Icon List Slide - 1920x1080</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            background-color: {bg_color};
            overflow: hidden;
        }}

        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            align-items: center;
            gap: 80px;
            padding: 80px 120px;
        }}

        .title-column {{
            padding-right: 40px;
        }}

        .main-title {{
            font-size: 100px;
            font-weight: 800;
            line-height: 1.2;
            color: {main_title_color};
            margin-bottom: 30px;
        }}

        .title-divider {{
            height: 8px;
            width: 120px;
            background-color: {accent_color};
            border-radius: 4px;
            border: none;
        }}

        .points-column {{
            display: flex;
            flex-direction: column;
            gap: 60px;
        }}

        .point-item {{
            display: flex;
            align-items: center;
            gap: 40px;
        }}

        .icon-circle {{
            width: 130px;
            height: 130px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 6px 20px {accent_color}33;
        }}

        .point-title {{
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 15px;
        }}

        .point-description {{
            font-size: 32px;
            line-height: 1.8;
            font-weight: 400;
        }}

        /* Content wrapper for scaling */
        .content-wrapper {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 1920px;
            height: 1080px;
            overflow: visible;
            background: inherit;
        }}
        
        .outer-wrapper {{
            padding: 0;
            box-sizing: border-box;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
        }}

    </style>
</head>
<body>
    <div class="outer-wrapper">
        <div class="content-wrapper">
            <div class="slide-container">
                <div class="title-column">
                    <h1 class="main-title">{main_title}</h1>
                    <hr class="title-divider" />
                </div>
                <div class="points-column">
                    {points_html}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_flexible_columns_slide(
    main_title="IN TWO OR THREE COLUMNS",
    columns=[
        {
            "title": "Yellow",
            "description": "Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange."
        },
        {
            "title": "Blue",
            "description": "Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum."
        },
        {
            "title": "Red",
            "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."
        }
    ],
    font_family_heading="'Patrick Hand', cursive",
    font_family_body="'Lato', sans-serif",
    text_color="#34495E",
    bg_url="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png"
):
    """
    Generates a slide with content positioned higher on the page to create more empty space at the bottom.
    """

    columns_html = ""
    for column in columns:
        columns_html += f"""
        <div class="column">
            <h2 class="column-title">{column['title']}</h2>
            <p class="column-description">{column['description']}</p>
        </div>
        """

    grid_columns_style = f"repeat({len(columns)}, 1fr)"

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minimalist Columns Slide - Positioned Higher</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato&family=Patrick+Hand&display=swap" rel="stylesheet">

    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        /* OVERRIDE EDITOR BACKGROUND - HIGHEST SPECIFICITY */
        div[style*="background: white"], 
        div[style*="background: #FFFFFF"],
        div[style*="background-color: white"],
        div[style*="background-color: #FFFFFF"],
        #canvas,
        [data-bg*="#FFFFFF"] {{
            background-color: #F8F8F8 !important;
            background-image: 
                linear-gradient(to bottom, transparent 98%, #E0E0E0 98%),
                url('{bg_url}') !important;
            background-repeat: repeat, repeat !important;
            background-position: top, top !important;
            background-size: 3.5rem 3.5rem, auto !important;
        }}

        body#body.body, html#html.html {{
            height: 100vh !important;
            width: 100vw !important;
            font-family: {font_family_body} !important;
            color: {text_color} !important;
            overflow: hidden !important;
            background-color: #F8F8F8 !important;
            background-image: 
                linear-gradient(to bottom, transparent 98%, #E0E0E0 98%),
                url('{bg_url}') !important;
            background-repeat: repeat, repeat !important;
            background-position: top, top !important;
            background-size: 3.5rem 3.5rem, auto !important;
        }}

        .slide-container {{
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
            align-items: center !important;
            padding: 3rem 3rem !important;
            background: transparent !important;
        }}

        .main-title {{
            font-family: 'Patrick Hand', cursive;
            font-size: clamp(4rem, 8vw, 5rem); 
            text-transform: uppercase;
            margin-bottom: 10rem; 
            font-weight: 400;
            text-align: center;
        }}
        .content-grid {{
            width: 100%;
            max-width: 90rem;
            display: grid;
            grid-template-columns: {grid_columns_style};
            gap: 4.5rem;
        }}

        .column-title {{
            font-weight: 700;
            font-size: 3.2rem;
            margin-bottom: 1.5rem;
        }}

        .column-description {{
            font-size: 2.2rem;
            line-height: 2;
        }}

        @media (max-width: 64rem) {{
            .content-grid {{
                grid-template-columns: 1fr;
            }}
            body, html {{
                height: auto;
                min-height: 100vh;
                overflow-y: auto;
            }}
            .slide-container {{
                padding: 3rem 2.5rem;
            }}
        }}
    </style>
</head>
<body id="body" class="body">
    <div class="slide-container">
        <h1 class="main-title">{main_title}</h1>
        <div class="content-grid">
            {columns_html}
        </div>
    </div>
</body>
</html>"""

    return html_code





def generate_text_with_image_slide(
    title="Tiltle Tiltle TiltleTiltle Tiltle",
    text_content="Content.",
    image_url="https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1920&q=80",
    font_family_heading="'Patrick Hand', cursive",
    font_family_body="'Lato', sans-serif",
    text_color="#34495E",
    bg_url="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png",
    doodle_border_url="https://i.imgur.com/Qy2O1vN.png"
):
    """
    Generates a doodle-themed, two-column slide with text on the left and a full-height image on the right.
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text and Image Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family_body};
            color: {text_color};
            overflow: hidden;
            background-color: #F8F8F8;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
        }}

        .text-column {{
            flex: 1.5; /* Takes more space */
            padding: 2rem 4rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            /* Layered background for the text column only */
            background-image: url('{bg_url}');
            background-repeat: repeat;
            background-position: center;
            background-size: auto;
        }}
        
        .image-column {{
            flex: 1; /* Takes less space */
            background-image: url('{image_url}');
            background-size: cover;
            background-position: center;
        }}

        .title {{
            font-family: {font_family_heading};
            font-size: clamp(3rem, 4vw, 4rem);
            font-weight: 400;
            text-transform: uppercase;
            margin-bottom: 1.5rem;
        }}
        
        .text-content {{
            font-size: 2rem;
            line-height: 1.8;
            max-width: 35ch; /* Limit line length for readability */
        }}
        
        /* --- Responsive Design --- */
        @media (max-width: 48rem) {{ /* 768px */
            .slide-container {{
                flex-direction: column;
            }}
            .text-column {{
                height: 60vh;
                padding: 2rem 2rem 4rem 2rem;
                justify-content: center;
                text-align: center;
            }}
            .text-content {{
                margin: 0 auto;
            }}
            .image-column {{
                height: 40vh;
            }}
        }}

    </style>
</head>
<body>
    <div class="slide-container">
        <div class="text-column">
            <h1 class="title">{title}</h1>
            <p class="text-content">{text_content}</p>
        </div>
        <div class="image-column"></div>
    </div>
</body>
</html>"""
    
    return html_code



def generate_instructions_slide(
    main_title="TOPIC",
    columns=[
        { "title": ["TOPIC ONE"], "list_items": ["First instruction point.", "Second instruction point.", "Third instruction point."] },
        { "title": ["TOPIC TWO"], "list_items": ["First instruction point.", "Second instruction point.", "Third instruction point."] },
        { "title": ["TOPIC THREE"], "list_items": ["First instruction point.", "Second instruction point.", "Third instruction point."] }
    ],
    font_family="'Poppins', sans-serif",
    header_primary_color="#4F46E5",
    header_secondary_color="#1E293B",
    header_text_color="#FFFFFF",
    body_title_color="#1E293B",
    body_text_color="#333333"
):
    """
    Generates a professional three-column instructions slide with extra-large,
    impactful fonts and generous spacing.
    """
    
    columns_html = ""
    for column in columns:
        title = column["title"]
        if isinstance(title, str):
            title = [title]
        list_items_html = "".join([f"<li>{item}</li>" for item in column['list_items']])
        title_items_html = "".join([f"<li>{item}</li>" for item in title])

        columns_html += f"""
        <div class="column">
            <h2 class="column-title">{title_items_html}</h2>
            <ul class="instruction-list">
                {list_items_html}
            </ul>
        </div>
        """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instructions Slide - Extra Large</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            background-color: #FFFFFF;
            overflow: hidden;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}

        .header-bar {{
            width: 100%;
            background-color: {header_primary_color};
            color: {header_text_color};
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header-title {{
            /* ĐÃ SỬA ĐỔI: To hơn một chút */
            font-size: clamp(3.5rem, 4vw, 4.5rem);
            font-weight: 700;
            padding: 2.5rem 3.5rem;
        }}
        
        .header-accent {{
            background-color: {header_secondary_color};
            height: 100%;
            padding: 2.5rem;
            display: flex;
            align-items: center;
        }}
        
        .dots-icon {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.4rem;
        }}
        .dot {{
            width: 0.7rem;
            height: 0.7rem;
            background-color: {header_text_color};
            border-radius: 50%;
        }}

        .content-grid {{
            padding: 5rem; /* Tăng padding để thoáng hơn */
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 3.5rem; /* Tăng gap */
            flex-grow: 1;
        }}
        
        .column-title {{
            /* ĐÃ SỬA ĐỔI: To hơn một chút */
            font-size: 3rem;
            font-weight: 800;
            color: {body_title_color};
            text-transform: uppercase;
            margin-bottom: 2.5rem; /* Tăng lề dưới */
        }}
        
        .instruction-list {{
            list-style: none;
            padding: 0;
            display: flex;
            flex-direction: column;
            gap: 1.5rem; /* Tăng khoảng cách */
        }}
        
        .instruction-list li {{
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            /* ĐÃ SỬA ĐỔI: To hơn một chút */
            font-size: 2rem;
            color: {body_text_color};
            line-height: 1.7;
        }}

        .instruction-list li::before {{
            content: '•';
            color: {header_primary_color};
            font-weight: 800;
            /* ĐÃ SỬA ĐỔI: To hơn một chút */
            font-size: 2.2rem;
            margin-top: 0.15rem;
        }}
        
        @media (max-width: 64rem) {{
            .content-grid {{ 
                grid-template-columns: 1fr; 
                max-width: 45rem; 
                margin: 0 auto;
                padding: 4rem 2rem;
            }}
            body, html {{
                 height: auto;
                 min-height: 100vh;
                 overflow-y: auto;
            }}
        }}

    </style>
</head>
<body>
    <div class="slide-container">
        <div class="header-bar">
            <h1 class="header-title">{main_title}</h1>
            <div class="header-accent">
                <div class="dots-icon">
                    <div class="dot"></div><div class="dot"></div>
                    <div class="dot"></div><div class="dot"></div>
                </div>
            </div>
        </div>
        <div class="content-grid">
            {columns_html}
        </div>
    </div>
</body>
</html>"""
    
    return html_code




def generate_geometric_split_content_slide(
    main_title="You can also split your content",
    columns=[
        {
            "title": "White",
            "description": "Is the color of milk and fresh snow, the color produced by the combination of all the colors of the visible spectrum."
        },
        {
            "title": "Black",
            "description": "Is the color of ebony and of outer space. It has been the symbolic color of elegance, solemnity and authority."
        }
    ],
    font_family="'Poppins', sans-serif",
    bg_color="#0F172A",
    text_color="#FFFFFF"
):
    """
    Generates a multi-column content slide with a robust layout that prevents
    text and decorative shapes from ever overlapping.
    """
    columns_html = ""
    for col in columns:
        columns_html += f"""
        <div class="column-item">
            <h3 class="column-title">{col['title']}</h3>
            <p class="column-description">{col['description']}</p>
        </div>
        """

    grid_template_style = f"repeat({len(columns)}, 1fr)"

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Split Content Slide - Final Fix</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
            color: {text_color};
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex;
            align-items: center;
            justify-content: center; /* Center the content wrapper */
            position: relative;
            padding: 4rem;
        }}

        /* FIX: Create a safe zone for all text content */
        .content-wrapper {{
            width: 100%;
            max-width: 85rem; /* Max width to prevent collision */
            position: relative;
            z-index: 10;
            padding: 0 4rem; /* Inner padding for safety */
        }}
        
        .main-title {{
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 4rem;
        }}

        .columns-grid {{
            display: grid;
            grid-template-columns: {grid_template_style};
            gap: 4rem;
        }}

        .column-title {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }}

        .column-description {{
            font-size: 2rem;
            font-weight: 600;
            line-height: 1.6;
        }}

        /* Shapes are positioned relative to the viewport, outside the content wrapper */
        .shape-cluster {{ position: absolute; pointer-events: none; z-index: 1; transform: scale(0.85); }}
        .shape {{ position: absolute; border-radius: 8px; }}
        .top-right {{ top: 5rem; right: 5rem; width: 25rem; height: 20rem; }}
        .shape-tr-1 {{ width: 14rem; height: 14rem; background-color: #1E3A8A; opacity: 0.6; top: 0; right: 8rem; transform: rotate(15deg); }}
        .shape-tr-2 {{ width: 15rem; height: 15rem; background-color: #34D399; opacity: 0.7; top: 2rem; right: 0; transform: rotate(25deg); }}
        .shape-tr-3 {{ width: 13rem; height: 13rem; background-color: #6366F1; opacity: 0.6; top: 8rem; right: 10rem; transform: rotate(35deg); }}
        .shape-tr-4 {{ width: 12rem; height: 12rem; background: linear-gradient(45deg, #F59E0B, #FBBF24); opacity: 0.8; top: 12rem; right: 2rem; transform: rotate(10deg); }}
        .bottom-left {{ bottom: 3rem; left: -5rem; width: 25rem; height: 20rem; }}
        .shape-bl-1 {{ width: 12rem; height: 12rem; background-color: #4F46E5; opacity: 0.5; bottom: 0; left: 10rem; transform: rotate(-25deg); }}
        .shape-bl-2 {{ width: 14rem; height: 14rem; background-color: #10B981; opacity: 0.4; bottom: 8rem; left: 2rem; transform: rotate(-35deg); }}
        .shape-bl-3 {{ width: 16rem; height: 16rem; background: linear-gradient(45deg, #EF4444, #F97316); opacity: 0.7; bottom: 0; left: 0; transform: rotate(-15deg); }}

        @media (max-width: 75rem) {{
            .content-wrapper {{ padding: 0 1rem; }}
        }}
        @media (max-width: 48rem) {{
            .columns-grid {{ grid-template-columns: 1fr; gap: 2rem; }}
            .main-title {{ text-align: center; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="content-wrapper">
            <h1 class="main-title">{main_title}</h1>
            <div class="columns-grid">
                {columns_html}
            </div>
        </div>
        <div class="shape-cluster top-right">
            <div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3"></div><div class="shape shape-tr-4"></div>
        </div>
        <div class="shape-cluster bottom-left">
             <div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div>
        </div>
    </div>
</body>
</html>"""
    return html_code





def generate_geometric_split_content_slide_2(
    main_title="In two or three columns",
    columns=[
        {
            "title": "Yellow",
            "description": "Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange."
        },
        {
            "title": "Blue",
            "description": "Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum."
        },
        {
            "title": "Red",
            "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."
        }
    ],
    font_family="'Poppins', sans-serif",
    bg_color="#0F172A",
    text_color="#FFFFFF"
):
    """
    Generates a multi-column content slide with a robust layout that prevents
    text and decorative shapes from ever overlapping. Maintains the 'geometric theme'.
    """
    columns_html = ""
    for col in columns:
        columns_html += f"""
        <div class="column-item">
            <h3 class="column-title">{col['title']}</h3>
            <p class="column-description">{col['description']}</p>
        </div>
        """

    grid_template_style = f"repeat({len(columns)}, 1fr)"

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Column Slide - Safe Layout</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
            color: {text_color};
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            padding: 4rem;
        }}

        .content-wrapper {{
            width: 100%;
            max-width: 90rem; /* Wide safe zone for 3 columns */
            position: relative;
            z-index: 10;
            padding: 0 4rem;
        }}
        
        .main-title {{
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 4rem;
        }}

        .columns-grid {{
            display: grid;
            grid-template-columns: {grid_template_style};
            gap: 4rem;
        }}

        .column-title {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }}

        .column-description {{
            font-size: 2rem;
            font-weight: 600;
            line-height: 1.6;
        }}

        /* Decorative shapes are positioned relative to the viewport, outside the content wrapper */
        .shape-cluster {{ position: absolute; pointer-events: none; z-index: 1; transform: scale(0.85); }}
        .shape {{ position: absolute; border-radius: 8px; }}
        .top-right {{ top: 5rem; right: 5rem; width: 25rem; height: 20rem; }}
        .shape-tr-1 {{ width: 14rem; height: 14rem; background-color: #1E3A8A; opacity: 0.6; top: 0; right: 8rem; transform: rotate(15deg); }}
        .shape-tr-2 {{ width: 15rem; height: 15rem; background-color: #34D399; opacity: 0.7; top: 2rem; right: 0; transform: rotate(25deg); }}
        .shape-tr-3 {{ width: 13rem; height: 13rem; background-color: #6366F1; opacity: 0.6; top: 8rem; right: 10rem; transform: rotate(35deg); }}
        .shape-tr-4 {{ width: 12rem; height: 12rem; background: linear-gradient(45deg, #F59E0B, #FBBF24); opacity: 0.8; top: 12rem; right: 2rem; transform: rotate(10deg); }}
        .bottom-left {{ bottom: 3rem; left: -5rem; width: 25rem; height: 20rem; }}
        .shape-bl-1 {{ width: 12rem; height: 12rem; background-color: #4F46E5; opacity: 0.5; bottom: 0; left: 10rem; transform: rotate(-25deg); }}
        .shape-bl-2 {{ width: 14rem; height: 14rem; background-color: #10B981; opacity: 0.4; bottom: 8rem; left: 2rem; transform: rotate(-35deg); }}
        .shape-bl-3 {{ width: 16rem; height: 16rem; background: linear-gradient(45deg, #EF4444, #F97316); opacity: 0.7; bottom: 0; left: 0; transform: rotate(-15deg); }}

        @media (max-width: 75rem) {{
            .content-wrapper {{ padding: 0 1rem; max-width: 100%; }}
        }}
        @media (max-width: 48rem) {{
            .columns-grid {{ grid-template-columns: 1fr; gap: 2.5rem; }}
            .main-title {{ text-align: center; }}
            .slide-container {{ padding: 2rem; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="content-wrapper">
            <h1 class="main-title">{main_title}</h1>
            <div class="columns-grid">
                {columns_html}
            </div>
        </div>
        <div class="shape-cluster top-right">
            <div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3"></div><div class="shape shape-tr-4"></div>
        </div>
        <div class="shape-cluster bottom-left">
             <div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div>
        </div>
    </div>
</body>
</html>"""
    return html_code


def generate_geometric_image_content_slide(
    image_url="https://images.unsplash.com/photo-1557804506-669a67965ba0?q=80&w=2574&auto=format&fit=crop",
    main_title="A picture is worth a <span class='highlight'>thousand</span> words",
    description="A complex idea can be conveyed with just a single still image, namely making it possible to absorb large amounts of data quickly.",
    font_family="'Poppins', sans-serif",
    bg_color="#0F172A",
    text_color="#FFFFFF"
):
    """
    Generates a content slide with a custom-shaped image on the left and text on the right.
    Features compact, subtle geometric shapes in the corners to maintain the theme.
    """

    clip_path_svg = """
    <svg width="0" height="0">
      <defs>
        <clipPath id="custom-image-shape" clipPathUnits="objectBoundingBox">
          <polygon points="0 0, 0.85 0, 1 0.15, 1 0.85, 0.85 1, 0 1" />
        </clipPath>
      </defs>
    </svg>
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Content Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
            color: {text_color};
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex;
            align-items: center;
            position: relative;
        }}
        
        .image-column {{
            flex: 1.1;
            height: 100%;
            clip-path: url(#custom-image-shape);
        }}
        
        .image-column img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .text-column {{
            flex: 1;
            padding: 4rem 6rem;
            position: relative;
            z-index: 10;
        }}

        .main-title {{
            font-size: 5rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 4rem;
        }}

        

        .description {{
            font-size: 2rem;
            font-weight: 600;
            line-height: 1.6;
            max-width: 45ch;
        }}

        /* FIX: Compact decorative shapes */
        .shape-cluster {{
            position: absolute;
            pointer-events: none;
            z-index: 5;
            transform: scale(0.75);
        }}
        .shape {{ position: absolute; border-radius: 6px; }}

        .top-right {{
            top: 2rem; right: 2rem;
            width: 20rem; height: 15rem;
        }}
        .shape-tr-1 {{ width: 10rem; height: 10rem; background-color: #1E3A8A; opacity: 0.6; top: 0; right: 8rem; transform: rotate(15deg); }}
        .shape-tr-2 {{ width: 12rem; height: 12rem; background-color: #34D399; opacity: 0.8; top: 1rem; right: 0; transform: rotate(25deg); }}
        .shape-tr-3 {{ width: 9rem; height: 9rem; background-color: #A855F7; opacity: 0.7; top: -1rem; right: 0.5rem; transform: rotate(-15deg) scaleX(-1); }}
        .shape-tr-4 {{ width: 8rem; height: 8rem; background: #F43F5E; opacity: 0.9; top: 8rem; right: 6rem; transform: rotate(10deg); }}

        .bottom-left {{
            bottom: 2rem; left: -6rem;
            width: 20rem; height: 15rem;
        }}
        .shape-bl-1 {{ width: 10rem; height: 10rem; background-color: #4F46E5; opacity: 0.5; bottom: 0; left: 10rem; transform: rotate(-25deg); }}
        .shape-bl-2 {{ width: 12rem; height: 12rem; background-color: #10B981; opacity: 0.5; bottom: 5rem; left: 2rem; transform: rotate(-35deg); }}
        .shape-bl-3 {{ width: 14rem; height: 14rem; background: linear-gradient(45deg, #EF4444, #F97316); opacity: 0.8; bottom: -2rem; left: 0; transform: rotate(-15deg); }}
        
        @media (max-width: 64rem) {{
            .slide-container {{ flex-direction: column; }}
            .image-column {{ flex: 1; width: 100%; clip-path: none; }}
            .text-column {{ flex: 0.8; width: 100%; padding: 2rem; text-align: center; }}
            .main-title {{ font-size: 2.5rem; }}
            .description {{ font-size: 1.2rem; max-width: none; }}
        }}

    </style>
</head>
<body>
    {clip_path_svg}
    <div class="slide-container">
        <div class="image-column">
            <img src="{image_url}" alt="A descriptive image for the slide content">
        </div>
        <div class="text-column">
            <h1 class="main-title">{main_title}</h1>
            <p class="description">{description}</p>
        </div>
        
        <div class="shape-cluster top-right">
            <div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3"></div><div class="shape shape-tr-4"></div>
        </div>
        <div class="shape-cluster bottom-left">
             <div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div>
        </div>
    </div>
</body>
</html>"""
    return html_code





def generate_geometric_content_slide(
    main_title="Our Core Strategy",
    list_items=[
        "Focus on <b><i><u><span style='color:#A3E635;'>user-centric design</span></u></i></b>.",
        "Innovate with purpose and clarity.",
        "Build for <b><i><u><span style='color:#A3E635;'>scalability and performance</span></u></i></b>."
    ],
    concluding_text="These principles guide our every move forward.",
    font_family="'Poppins', sans-serif",
    bg_color="#2B233D",
    text_color="#E5E7EB",
    bullet_color="#FBBF24"
):
    """
    Generates a modern content slide with bolder text and subtle geometric shapes.
    The text is thicker for better readability on a dark background.
    """
    list_html = ""
    for item in list_items:
        list_html += f"<li>{item}</li>\n"

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Geometric Content Slide - Bolder Text</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <!-- FIX: Imported bolder font weights (600, 800) -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
            color: {text_color};
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex;
            align-items: center;
            justify-content: flex-start;
            position: relative;
            padding: 5rem 8rem;
        }}

        .content-area {{
            position: relative;
            z-index: 10;
            max-width: 65ch;
        }}

        .slide-title {{
            font-size: 4rem;
            /* FIX: Title is now Extra-Bold */
            font-weight: 800;
            margin-bottom: 4rem;
        }}
        
        .content-list {{
            list-style: none;
            margin-bottom: 4rem;
        }}

        .content-list li {{
            font-size: 2.5rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
            padding-left: 3rem;
            position: relative;
            /* FIX: Body text is now Semi-Bold */
            font-weight: 600;
        }}

        .content-list li::before {{
            content: '>';
            position: absolute;
            left: 0;
            top: 5px;
            color: {bullet_color};
            font-weight: 800; /* Made bullet heavier to match text */
        }}
        
        .concluding-text {{
            font-size: 2.5rem;
            line-height: 1.6;
            /* FIX: Body text is now Semi-Bold */
            font-weight: 600;
        }}

        /* Shapes are unchanged from the previous fix */
        .shape-cluster {{
            position: absolute;
            pointer-events: none;
            z-index: 1;
            transform: scale(0.85); 
        }}
        .shape {{ position: absolute; border-radius: 8px; }}
        .top-right {{ top: 5rem; right: 5rem; width: 25rem; height: 20rem; }}
        .shape-tr-1 {{ width: 14rem; height: 14rem; background-color: #1E3A8A; opacity: 0.6; top: 0; right: 8rem; transform: rotate(15deg); }}
        .shape-tr-2 {{ width: 15rem; height: 15rem; background-color: #34D399; opacity: 0.7; top: 2rem; right: 0; transform: rotate(25deg); }}
        .shape-tr-3 {{ width: 13rem; height: 13rem; background-color: #6366F1; opacity: 0.6; top: 8rem; right: 10rem; transform: rotate(35deg); }}
        .shape-tr-4 {{ width: 12rem; height: 12rem; background: linear-gradient(45deg, #F59E0B, #FBBF24); opacity: 0.8; top: 12rem; right: 2rem; transform: rotate(10deg); }}
        .bottom-left {{ bottom: 3rem; left: -5rem; width: 25rem; height: 20rem; }}
        .shape-bl-1 {{ width: 12rem; height: 12rem; background-color: #4F46E5; opacity: 0.5; bottom: 0; left: 10rem; transform: rotate(-25deg); }}
        .shape-bl-2 {{ width: 14rem; height: 14rem; background-color: #10B981; opacity: 0.4; bottom: 8rem; left: 2rem; transform: rotate(-35deg); }}
        .shape-bl-3 {{ width: 16rem; height: 16rem; background: linear-gradient(45deg, #EF4444, #F97316); opacity: 0.7; bottom: 0; left: 0; transform: rotate(-15deg); }}
        
        @media (max-width: 96rem) {{ .slide-container {{ padding: 4rem; }} }}
        @media (max-width: 64rem) {{
            .slide-title {{ font-size: 2.25rem; }}
            .content-list li, .concluding-text {{ font-size: 1.4rem; }}
            .shape-cluster {{ transform: scale(0.7); }}
        }}
         @media (max-width: 48rem) {{
            .shape-cluster {{ display: none; }}
            .slide-container {{ justify-content: center; text-align: center; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="shape-cluster top-right">
            <div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3"></div><div class="shape shape-tr-4"></div>
        </div>
        <div class="shape-cluster bottom-left">
             <div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div>
        </div>
        <div class="content-area">
            <h2 class="slide-title">{main_title}</h2>
            <ul class="content-list">
                {list_html}
            </ul>
            <p class="concluding-text">{concluding_text}</p>
        </div>
    </div>
</body>
</html>"""
    return html_code



def generate_geometric_grid_slide(
    main_title="Let's review some concepts",
    grid_items=[
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."},
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons. In the spectrum of visible light, yellow is found between green and orange."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea. It is located between violet and green on the optical spectrum."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."}
    ],
    font_family="'Poppins', sans-serif",
    bg_color="#0F172A",
    text_color="#FFFFFF"
):
    """
    Generates a 2x3 grid slide with very subtle and transparent decorative shapes,
    ensuring content is the primary focus.
    """
    grid_items_html = ""
    for item in grid_items:
        grid_items_html += f"""
        <div class="grid-item">
            <h3 class="item-title">{item['title']}</h3>
            <p class="item-description">{item['description']}</p>
        </div>
        """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Grid Content Slide - Faded Shapes</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {bg_color};
            color: {text_color};
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            padding: 4rem;
        }}

        .content-wrapper {{
            width: 100%;
            max-width: 90rem;
            position: relative;
            z-index: 10;
            padding: 0 4rem;
        }}
        
        .main-title {{
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 4rem;
        }}

        .content-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 3rem 4rem;
        }}

        .item-title {{
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.75rem;
        }}

        .item-description {{
            font-size: 1.5rem;
            font-weight: 600;
            line-height: 1.6;
        }}

        /* FIX: Opacity values significantly reduced for a more subtle effect */
        .shape-cluster {{ position: absolute; pointer-events: none; z-index: 1; transform: scale(0.5); }}
        .shape {{ position: absolute; border-radius: 8px; }}
        .top-right {{ top: 5rem; right: 5rem; width: 25rem; height: 20rem; }}
        .shape-tr-1 {{ width: 14rem; height: 14rem; background-color: #1E3A8A; opacity: 0.3; top: 0; right: 8rem; transform: rotate(15deg); }}
        .shape-tr-2 {{ width: 15rem; height: 15rem; background-color: #34D399; opacity: 0.4; top: 2rem; right: 0; transform: rotate(25deg); }}
        .shape-tr-3 {{ width: 13rem; height: 13rem; background-color: #6366F1; opacity: 0.3; top: 8rem; right: 10rem; transform: rotate(35deg); }}
        .shape-tr-4 {{ width: 12rem; height: 12rem; background: linear-gradient(45deg, #F59E0B, #FBBF24); opacity: 0.5; top: 12rem; right: 2rem; transform: rotate(10deg); }}
        .bottom-left {{ bottom: 3rem; left: -5rem; width: 25rem; height: 20rem; }}
        .shape-bl-1 {{ width: 12rem; height: 12rem; background-color: #4F46E5; opacity: 0.2; bottom: 0; left: 10rem; transform: rotate(-25deg); }}
        .shape-bl-2 {{ width: 14rem; height: 14rem; background-color: #10B981; opacity: 0.2; bottom: 8rem; left: 2rem; transform: rotate(-35deg); }}
        .shape-bl-3 {{ width: 16rem; height: 16rem; background: linear-gradient(45deg, #EF4444, #F97316); opacity: 0.4; bottom: 0; left: 0; transform: rotate(-15deg); }}

        @media (max-width: 75rem) {{
            .content-wrapper {{ padding: 0 1rem; max-width: 100%; }}
            .content-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        @media (max-width: 48rem) {{
            .content-grid {{ grid-template-columns: 1fr; }}
            .main-title {{ text-align: center; }}
            .slide-container {{ padding: 2rem; }}
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="content-wrapper">
            <h1 class="main-title">{main_title}</h1>
            <div class="content-grid">
                {grid_items_html}
            </div>
        </div>
        <div class="shape-cluster top-right">
            <div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3"></div><div class="shape shape-tr-4"></div>
        </div>
        <div class="shape-cluster bottom-left">
             <div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div>
        </div>
    </div>
</body>
</html>"""
    return html_code




def generate_memphis_content_slide(
    main_title="This is a slide title",
    list_items=[
        "Here you have a list of items",
        "And some text",
        "But remember not to overload your slides with content"
    ],
    concluding_text="Your audience will listen to you or read the content, but won't do both.",
    font_family_title="'Lora', serif",
    font_family_body="'Source Code Pro', monospace",
    top_panel_bg="#19114B",
    bottom_panel_bg="#403271",
    palette=["#F87171", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"]
):
    """
    Generates a 'Memphis-style' content slide with a dramatic 20/80 layout split
    and precisely positioned decorative elements to match the user's final sample.
    """
    list_html = "".join(f"<li>{item}</li>" for item in list_items)
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Memphis Content Slide - 20/80 Layout</title>
    <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }} html {{ font-size: 16px; }}
        body, html {{ height: 100vh; width: 100vw; overflow: hidden; }}
        .slide-container {{ width: 100%; height: 100%; display: flex; flex-direction: column; position: relative; color: #FFFFFF; }}
        .top-panel, .bottom-panel {{ position: relative; overflow: hidden; display: flex; justify-content: center; }}
        .top-panel {{ background-color: {top_panel_bg}; flex-basis: 20%; align-items: center; }}
        .bottom-panel {{ background-color: {bottom_panel_bg}; flex-basis: 80%; align-items: flex-start; padding-top: 6rem; }}
        .panel-content {{ width: 100%; max-width: 75rem; padding: 2rem 4rem; }}
        .main-title {{ font-family: {font_family_title}; font-size: 3rem; font-weight: 600; text-align: center; }}
        .content-list {{ font-family: {font_family_body}; list-style: none; margin-bottom: 3rem; }}
        .content-list li {{ font-size: 2rem; line-height: 1.7; padding-left: 2.5rem; position: relative; margin-bottom: 0.5rem; }}
        .content-list li::before {{ content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 1rem; height: 1rem; border-radius: 50%; border: 2px solid {palette[1]}; }}
        .concluding-text {{ font-family: {font_family_body}; font-size: 2rem; line-height: 1.7; max-width: 60ch; }}
        .shape {{ position: absolute; }}
        .shape-tl-1 {{ width: 4rem; height: 4rem; border: 2px dashed {palette[0]}; top: 2rem; left: 2rem; transform: rotate(-25deg); }}
        .shape-tl-2 {{ width: 0; height: 0; border-left: 1.5rem solid transparent; border-right: 1.5rem solid transparent; border-bottom: 2.5rem solid {palette[0]}; top: 3.5rem; left: 7rem; transform: rotate(20deg); opacity: 0.8; }}
        .shape-tr-1 {{ width: 6rem; height: 6rem; border: 2px dashed {palette[1]}; border-radius: 50%; top: 1rem; right: 1rem; }}
        .shape-tr-2 {{ width: 0; height: 0; border-left: 2rem solid transparent; border-right: 2rem solid transparent; border-bottom: 3.5rem solid {palette[3]}; top: 2rem; right: 8rem; transform: rotate(25deg); }}
        .shape-bl-1 {{ width: 1.5rem; height: 1.5rem; background-color: {palette[3]}; bottom: 2rem; left: 5rem; }}
        .shape-bl-2 {{ width: 0; height: 0; border-right: 2rem solid {palette[3]}; border-top: 1.5rem solid transparent; border-bottom: 1.5rem solid transparent; bottom: 3rem; left: 2rem; }}
        .shape-br-1 {{ width: 5rem; height: 5rem; background-color: {palette[0]}; border-radius: 50%; bottom: 3rem; right: 4rem; opacity: 0.8; }}
        .shape-br-2 {{ width: 0; height: 0; border-left: 2.5rem solid transparent; border-right: 2.5rem solid transparent; border-bottom: 4rem solid {palette[1]}; bottom: 7rem; right: 9rem; transform: rotate(45deg); opacity: 0.9; }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="top-panel">
            <div class="panel-content"><h1 class="main-title">{main_title}</h1></div>
            <div class="shape shape-tl-1"></div><div class="shape shape-tl-2"></div>
            <div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div>
        </div>
        <div class="bottom-panel">
            <div class="panel-content"><ul class="content-list">{list_html}</ul><p class="concluding-text">{concluding_text}</p></div>
            <div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div>
            <div class="shape shape-br-1"></div><div class="shape shape-br-2"></div>
        </div>
    </div>
</body>
</html>"""
    return html_code


def generate_memphis_multicolumn_slide(
    main_title="In two or three columns",
    columns=[
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."}
    ],
    font_family_title="'Lora', serif",
    font_family_body="'Source Code Pro', monospace",
    top_panel_bg="#19114B",
    bottom_panel_bg="#403271",
    palette=["#F43F5E", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"]
):
    """
    Generates a STATIC 'Memphis-style' multi-column slide. The rotating icon animation has been removed.
    """
    svg_patterns = f"""<svg width="0" height="0" style="position:absolute;"><defs><pattern id="pattern-dots" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="2" fill="{palette[3]}" /></pattern><pattern id="pattern-stripes" x="0" y="0" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="{palette[1]}" stroke-width="4" /></pattern></defs></svg>"""
    columns_html = "".join([f"""<div class="column-item"><h3 class="column-title">{col['title']}</h3><p class="column-description">{col['description']}</p></div>""" for col in columns])
    grid_template_style = f"repeat({len(columns)}, 1fr)"
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Memphis Multi-Column Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }} html {{ font-size: 16px; }}
        body, html {{ height: 100vh; width: 100vw; overflow: hidden; }}
        .slide-container {{ width: 100%; height: 100%; display: flex; flex-direction: column; position: relative; color: #FFFFFF; }}
        .top-panel, .bottom-panel {{ position: relative; overflow: hidden; display: flex; justify-content: center; }}
        .top-panel {{ background-color: {top_panel_bg}; flex-basis: 20%; align-items: center; }}
        .bottom-panel {{ background-color: {bottom_panel_bg}; flex-basis: 80%; align-items: flex-start; padding-top: 6rem; }}
        .panel-content {{ width: 100%; max-width: 80rem; padding: 2rem 4rem; }}
        .main-title {{ font-family: {font_family_title}; font-size: 3.5rem; font-weight: 600; text-align: center; }}
        .columns-grid {{ display: grid; grid-template-columns: {grid_template_style}; gap: 3rem 5rem; }}
        .column-title {{ font-family: {font_family_body}; font-size: 2.5rem; font-weight: 600; margin-bottom: 1.5rem; }}
        .column-description {{ font-family: {font_family_body}; font-size: 1.75rem; line-height: 1.6; }}
        .shape {{ position: absolute; }} .pentagon {{ clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%); }}
        .shape-tl-1 {{ width: 6rem; height: 6rem; background: {palette[2]}; opacity: 0.4; top: 1rem; left: 8rem; }}
        .shape-tl-2 {{ width: 8rem; height: 8rem; background: url(#pattern-dots); top: -1rem; left: 1rem; border-radius: 50%; opacity: 0.8; }}
        .shape-tl-3 {{ width: 5rem; height: 5rem; border: 3px solid {palette[0]}; top: 7rem; left: 2rem; }}
        .shape-tr-1 {{ width: 5rem; height: 5rem; border: 3px dashed {palette[1]}; border-radius: 50%; top: 1rem; right: 8rem; }}
        .shape-tr-2 {{ width: 9rem; height: 9rem; background: url(#pattern-stripes); border-radius: 50%; top: 4rem; right: 1rem; transform: rotate(45deg); opacity: 0.9; }}
        .shape-tr-3 {{ width: 4rem; height: 4rem; border: 3px solid {palette[3]}; top: 9rem; right: 12rem; }}
        .shape-bl-1 {{ width: 7rem; height: 7rem; border: 3px dashed {palette[2]}; border-radius: 50%; bottom: 1rem; left: 8rem; }}
        .shape-bl-2 {{ width: 0; height: 0; border-left: 3rem solid transparent; border-right: 3rem solid transparent; border-bottom: 5rem solid {palette[0]}; bottom: 8rem; left: 2rem; transform: rotate(-15deg); }}
        .shape-bl-3 {{ width: 9rem; height: 9rem; background: url(#pattern-stripes); bottom: 1rem; left: -1rem; clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%); transform: rotate(-25deg); opacity: 0.7; }}
        .shape-br-1 {{ width: 6rem; height: 6rem; border: 3px solid {palette[0]}; border-radius: 50%; bottom: 2rem; right: 2rem; }}
        .shape-br-2 {{ width: 8rem; height: 8rem; background: url(#pattern-dots); border-radius: 50%; bottom: 1rem; right: 9rem; }}
        .shape-br-3 {{ width: 0; height: 0; border-left: 2rem solid transparent; border-right: 2rem solid transparent; border-bottom: 3.5rem solid {palette[1]}; bottom: 10rem; right: 4rem; transform: rotate(45deg); opacity: 0.7;}}
    </style>
</head>
<body>
    {svg_patterns}
    <div class="slide-container">
        <div class="top-panel"><div class="panel-content"><h1 class="main-title">{main_title}</h1></div><div class="shape shape-tl-1 pentagon"></div><div class="shape shape-tl-2"></div><div class="shape shape-tl-3 pentagon"></div><div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3 pentagon"></div></div>
        <div class="bottom-panel"><div class="panel-content"><div class="columns-grid">{columns_html}</div></div><div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div><div class="shape shape-br-1"></div><div class="shape shape-br-2"></div><div class="shape shape-br-3"></div></div>
    </div>
</body>
</html>"""
    
    return html_code




def generate_memphis_grid_slide(
    main_title="Let's review some concepts",
    grid_items=[
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."},
        {"title": "Yellow", "description": "Is the color of gold, butter and ripe lemons."},
        {"title": "Blue", "description": "Is the colour of the clear sky and the deep sea."},
        {"title": "Red", "description": "Is the color of blood, and because of this it has historically been associated with sacrifice, danger and courage."}
    ],
    font_family_title="'Lora', serif",
    font_family_body="'Source Code Pro', monospace",
    top_panel_bg="#19114B",
    bottom_panel_bg="#403271",
    palette=["#F43F5E", "#FBBF24", "#A78BFA", "#60A5FA", "#34D399"]
):
    """
    Generates a STATIC 'Memphis-style' 2x3 grid slide. The rotating icon animation has been removed.
    """
    if len(grid_items) != 6:
        raise ValueError("This function requires exactly 6 items for the grid_items parameter.")
    svg_patterns = f"""<svg width="0" height="0" style="position:absolute;"><defs><pattern id="pattern-dots" x="0" y="0" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="2" fill="{palette[3]}" /></pattern><pattern id="pattern-stripes" x="0" y="0" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="{palette[1]}" stroke-width="4" /></pattern></defs></svg>"""
    grid_html = "".join(f"""<div class="grid-item"><h3 class="item-title">{item['title']}</h3><p class="item-description">{item['description']}</p></div>""" for item in grid_items)
    grid_template_style = f"repeat(3, 1fr)"
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Memphis Grid Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600&family=Source+Code+Pro:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }} html {{ font-size: 16px; }}
        body, html {{ height: 100vh; width: 100vw; overflow: hidden; }}
        .slide-container {{ width: 100%; height: 100%; display: flex; flex-direction: column; position: relative; color: #FFFFFF; }}
        .top-panel, .bottom-panel {{ position: relative; overflow: hidden; display: flex; justify-content: center; }}
        .top-panel {{ background-color: {top_panel_bg}; flex-basis: 20%; align-items: center; }}
        .bottom-panel {{ background-color: {bottom_panel_bg}; flex-basis: 80%; align-items: flex-start; padding-top: 6rem; }}
        .panel-content {{ width: 100%; max-width: 80rem; padding: 2rem 4rem; }}
        .main-title {{ font-family: {font_family_title}; font-size: 2.25rem; font-weight: 600; text-align: center; }}
        .columns-grid {{ display: grid; grid-template-columns: {grid_template_style}; gap: 3rem 4rem; }}
        .item-title {{ font-family: {font_family_body}; font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; }}
        .item-description {{ font-family: {font_family_body}; font-size: 1.1rem; line-height: 1.6; }}
        .shape {{ position: absolute; }} .pentagon {{ clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%); }}
        .shape-tl-1 {{ width: 6rem; height: 6rem; background: {palette[2]}; opacity: 0.4; top: 1rem; left: 8rem; }}
        .shape-tl-2 {{ width: 8rem; height: 8rem; background: url(#pattern-dots); top: -1rem; left: 1rem; border-radius: 50%; opacity: 0.8; }}
        .shape-tl-3 {{ width: 5rem; height: 5rem; border: 3px solid {palette[0]}; top: 7rem; left: 2rem; }}
        .shape-tr-1 {{ width: 5rem; height: 5rem; border: 3px dashed {palette[1]}; border-radius: 50%; top: 1rem; right: 8rem; }}
        .shape-tr-2 {{ width: 9rem; height: 9rem; background: url(#pattern-stripes); border-radius: 50%; top: 4rem; right: 1rem; transform: rotate(45deg); opacity: 0.9; }}
        .shape-tr-3 {{ width: 4rem; height: 4rem; border: 3px solid {palette[3]}; top: 9rem; right: 12rem; }}
        .shape-bl-1 {{ width: 7rem; height: 7rem; border: 3px dashed {palette[2]}; border-radius: 50%; bottom: 1rem; left: 8rem; }}
        .shape-bl-2 {{ width: 0; height: 0; border-left: 3rem solid transparent; border-right: 3rem solid transparent; border-bottom: 5rem solid {palette[0]}; bottom: 8rem; left: 2rem; transform: rotate(-15deg); }}
        .shape-bl-3 {{ width: 9rem; height: 9rem; background: url(#pattern-stripes); bottom: 1rem; left: -1rem; clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%); transform: rotate(-25deg); opacity: 0.7; }}
        .shape-br-1 {{ width: 6rem; height: 6rem; border: 3px solid {palette[0]}; border-radius: 50%; bottom: 2rem; right: 2rem; }}
        .shape-br-2 {{ width: 8rem; height: 8rem; background: url(#pattern-dots); border-radius: 50%; bottom: 1rem; right: 9rem; }}
        .shape-br-3 {{ width: 0; height: 0; border-left: 2rem solid transparent; border-right: 2rem solid transparent; border-bottom: 3.5rem solid {palette[1]}; bottom: 10rem; right: 4rem; transform: rotate(45deg); opacity: 0.7;}}
    </style>
</head>
<body>
    {svg_patterns}
    <div class="slide-container">
        <div class="top-panel"><div class="panel-content"><h1 class="main-title">{main_title}</h1></div><div class="shape shape-tl-1 pentagon"></div><div class="shape shape-tl-2"></div><div class="shape shape-tl-3 pentagon"></div><div class="shape shape-tr-1"></div><div class="shape shape-tr-2"></div><div class="shape shape-tr-3 pentagon"></div></div>
        <div class="bottom-panel"><div class="panel-content"><div class="columns-grid">{grid_html}</div></div><div class="shape shape-bl-1"></div><div class="shape shape-bl-2"></div><div class="shape shape-bl-3"></div><div class="shape shape-br-1"></div><div class="shape shape-br-2"></div><div class="shape shape-br-3"></div></div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_premium_abstract_slide(
    main_title="HR Management",
    content_paragraphs=[
        "We foster a dynamic and supportive work environment where every individual can thrive. Our approach integrates technology and human-centric policies to build a resilient and engaged workforce.",
        "From talent acquisition to professional development, our comprehensive strategies ensure that our people are our greatest asset, driving innovation and success."
    ],
    # --- Bảng màu thiết kế cao cấp ---
    bg_color="#F8FAFC", # Off-white, rất nhẹ
    aurora_color_1="#FBCFE8", # Pink
    aurora_color_2="#CFFAFE", # Cyan
    aurora_color_3="#DDD6FE", # Lavender
    title_color="#881337", # Deep Raspberry
    text_color="#334155",  # Slate Gray
    # --- Tùy chỉnh khác ---
    enable_animation=True,
    show_border=True,
    font_family_title="'Poppins', sans-serif",
    font_family_content="'Inter', sans-serif",
    custom_css=""
):
    """
    Generate a premium, modern slide with an aurora gradient background and abstract glassmorphism graphics.

    :param main_title: The main title of the slide.
    :param content_paragraphs: A list of strings for body text.
    :param bg_color: The base background color.
    :param aurora_color_1: First color for the aurora gradient effect.
    :param aurora_color_2: Second color for the aurora gradient effect.
    :param aurora_color_3: Third color for the aurora gradient effect.
    :param title_color: Color for the main title.
    :param text_color: Color for the paragraph text.
    :param enable_animation: Whether to enable subtle load animations.
    :param show_border: Whether to show a subtle finishing border.
    :param font_family_title: Font family for the title.
    :param font_family_content: Font family for the content.
    :param custom_css: Additional custom CSS.
    :return: HTML string for the slide.
    """

    paragraphs_html = "".join([f"<p class='content-paragraph'>{p}</p>" for p in content_paragraphs])
    animation_class = "animated" if enable_animation else ""

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&family=Inter:wght@400&display=swap" rel="stylesheet">
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            overflow: hidden;
            background-color: {bg_color};
            color: {text_color};
        }}
        
        .slide-container {{
            width: 100%;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 4vw;
            box-sizing: border-box;
            position: relative;
        }}
        
        /* Aurora Gradient Background */
        .aurora-shape {{
            position: absolute;
            filter: blur(120px);
            opacity: 0.4;
            border-radius: 50%;
        }}
        .aurora-1 {{
            width: 450px;
            height: 450px;
            top: -150px;
            left: -150px;
            background: {aurora_color_1};
        }}
        .aurora-2 {{
            width: 400px;
            height: 400px;
            bottom: -150px;
            right: -100px;
            background: {aurora_color_2};
        }}
        .aurora-3 {{
            width: 300px;
            height: 300px;
            top: 50%;
            right: 15%;
            transform: translateY(-50%);
            background: {aurora_color_3};
            opacity: 0.3;
        }}

        .slide-border {{
            position: absolute;
            top: 20px;
            left: 20px;
            right: 20px;
            bottom: 20px;
            border: 1px solid rgba(0, 0, 0, 0.05);
            border-radius: 20px;
            display: { "block" if show_border else "none" };
        }}

        .content-wrapper {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            max-width: 1200px;
            position: relative;
            z-index: 1;
        }}
        
        .text-section {{
            flex-basis: 50%;
            padding-right: 40px;
        }}
        
        .graphic-section {{
            flex-basis: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 400px;
        }}
        
        .main-title {{
            font-family: {font_family_title};
            font-size: 4.5rem;
            font-weight: 600;
            color: {title_color};
            margin: 0 0 30px 0;
            line-height: 1.15;
        }}
        
        .content-paragraph {{
            font-family: {font_family_content};
            font-size: 1.1rem;
            line-height: 1.8;
            margin-bottom: 20px;
            max-width: 500px;
        }}

        /* Abstract Glassmorphism Graphic */
        .abstract-graphic {{
            position: relative;
            width: 380px;
            height: 380px;
        }}
        .abstract-shape {{
            position: absolute;
            border-radius: 30%;
            transition: transform 0.4s ease-out;
        }}
        .shape1 {{
            width: 380px;
            height: 380px;
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 50%;
        }}
        .shape2 {{
            width: 180px;
            height: 180px;
            top: 30px;
            left: 10px;
            background: {aurora_color_1};
            opacity: 0.8;
            border-radius: 45% 55% 70% 30% / 30% 30% 70% 70%;
            transform: rotate(-15deg);
        }}
        .shape3 {{
            width: 200px;
            height: 200px;
            bottom: 20px;
            right: 0px;
            background: {aurora_color_2};
            opacity: 0.8;
            border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
            transform: rotate(15deg);
        }}
        
        

        /* Responsive */
        @media (max-width: 900px) {{
            .main-title {{ font-size: 3.2rem; }}
        }}
        @media (max-width: 768px) {{
            .content-wrapper {{ flex-direction: column-reverse; text-align: center; }}
            .text-section {{ padding-right: 0; margin-top: 40px; align-items: center; display:flex; flex-direction:column;}}
            .graphic-section {{ flex-basis: auto; width: 60%; height: 300px; margin-bottom: 20px; }}
            .abstract-graphic, .shape1 {{ width: 300px; height: 300px; }}
            .shape2 {{ width: 140px; height: 140px; }}
            .shape3 {{ width: 160px; height: 160px; }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container {animation_class}">
        <div class="aurora-shape aurora-1"></div>
        <div class="aurora-shape aurora-2"></div>
        <div class="aurora-shape aurora-3"></div>
        <div class="slide-border"></div>

        <div class="content-wrapper">
            <div class="text-section">
                <h1 class="main-title">{main_title}</h1>
                <div class="content-area">
                    {paragraphs_html}
                </div>
            </div>
            <div class="graphic-section">
                <div class="abstract-graphic">
                    <div class="abstract-shape shape1"></div>
                    <div class="abstract-shape shape2"></div>
                    <div class="abstract-shape shape3"></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    return html_code

#-------------------  # slide giới thiệu team

def generate_team_slide(
    main_title="Our Team",
    team_members=[
        {
            "name": "Alex Johnson",
            "role": "Lead Developer",
            "image_url": "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?q=80&w=1780&auto=format=fit=crop"
        },
        {
            "name": "Maria Garcia",
            "role": "Product Manager",
            "image_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1887&auto=format=fit=crop"
        },
        {
            "name": "James Smith",
            "role": "UX/UI Designer",
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1887&auto=format=fit=crop"
        }
    ],
    font_family="'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    accent_bg_color="#14B8A6",
    main_bg_color="#F8FAFC",
    title_color="#FFFFFF",
    name_color="#111827",
    role_color="#6B7280"
):
    """
    Generates a modern, STATIC team slide with a diagonal layout, large fonts,
    and professional member cards. Hover effects have been removed.
    """
    
    team_html = ""
    for member in team_members:
        team_html += f"""
        <div class="team-member-card">
            <div class="member-photo">
                <img src="{member['image_url']}" alt="{member['name']}" />
            </div>
            <div class="member-info">
                <h3 class="member-name">{member['name']}</h3>
                <p class="member-role">{member['role']}</p>
            </div>
        </div>
        """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Slide - Dynamic Design</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: {main_bg_color};
        }}
        
        .slide-container {{
            height: 100vh;
            width: 100vw;
            display: flex;
            position: relative;
        }}
        
        .left-background {{
            position: absolute;
            top: 0;
            left: 0;
            width: 45%;
            height: 100%;
            background: {accent_bg_color};
            clip-path: polygon(0 0, 100% 0, 65% 100%, 0% 100%);
            z-index: 1;
        }}

        .title-container {{
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 35%;
            text-align: center;
            z-index: 2;
            padding: 2rem;
        }}
        
        .main-title {{
            font-size: clamp(3rem, 6vw, 5rem);
            color: {title_color};
            font-weight: 800;
            line-height: 1.1;
        }}
        
        .right-content-area {{
            position: relative;
            flex: 1;
            padding: 4rem;
            padding-left: 38%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 2rem;
            z-index: 2;
        }}
        
        .team-member-card {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
            background: #FFFFFF;
            padding: 1.25rem;
            border-radius: 1rem;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
            /* ĐÃ XÓA: transition: transform 0.3s ease, box-shadow 0.3s ease; */
        }}
        
        /* ĐÃ XÓA: Khối CSS .team-member-card:hover đã được loại bỏ hoàn toàn. */
        
        .member-photo img {{
            width: 6.5rem;
            height: 6.5rem;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid {accent_bg_color};
        }}
        
        .member-name {{
            font-size: 1.75rem;
            color: {name_color};
            font-weight: 600;
            margin-bottom: 0.3rem;
        }}
        
        .member-role {{
            font-size: 1.1rem;
            color: {role_color};
        }}
        
        @media (max-width: 64rem) {{
            .left-background {{ width: 100%; height: 35%; clip-path: none; }}
            .title-container {{ width: 100%; top: 17.5%; }}
            .right-content-area {{ padding: 2rem; padding-top: 38%; }}
            .slide-container {{ flex-direction: column; }}
        }}
        
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="left-background"></div>
        <div class="title-container">
            <h1 class="main-title">{main_title}</h1>
        </div>
        <div class="right-content-area">
            {team_html}
        </div>
    </div>
</body>
</html>"""
    
    return html_code




def generate_colorful_team_grid_slide(
    main_title="Add a Team Members Page",
    team_members=[
        { "name": "Olivia Chen", "role": "Lead Designer", "image_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1887&auto=format=fit=crop", "color": "#8A44A1" },
        { "name": "Ben Carter", "role": "Frontend Developer", "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1887&auto=format=fit=crop", "color": "#2E9A94" },
        { "name": "Aisha Khan", "role": "Project Manager", "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1887&auto=format=fit=crop", "color": "#D93B58" },
        { "name": "Leo Martinez", "role": "Marketing Head", "image_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=1887&auto=format=fit=crop", "color": "#F3C314" }
    ],
    font_family="'Montserrat', sans-serif",
    bg_color="#F8FAFC",
    title_color="#111827",
    card_text_color="#1F2937"
):
    """
    Generates a vibrant, STATIC team slide with a spacious and balanced grid layout.
    Hover effects have been removed.
    """
    
    team_members_html = ""
    for member in team_members:
        team_members_html += f"""
        <div class="team-card" style="--member-color: {member['color']};">
            <img class="member-photo" src="{member['image_url']}" alt="{member['name']}" />
            <div class="member-info">
                <h2 class="member-name">{member['name']}</h2>
                <p class="member-role">{member['role']}</p>
            </div>
        </div>
        """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Team Members Slide - Spacious Design</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; width: 1920px; height: 1080px; }}
        body, html {{
            height: 1080px;
            width: 1920px;
            font-family: {font_family};
            background-color: {bg_color};
            overflow: hidden;
        }}

        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            background-color: {bg_color};
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            align-items: center;
            gap: 80px;
            padding: 80px 120px;
        }}

        .text-column {{ padding-right: 40px; }}

        .main-title {{
            font-size: 110px;
            font-weight: 800;
            line-height: 1.2;
            color: {title_color};
            margin-bottom: 20px;
        }}
        
        .title-divider {{
            height: 8px;
            width: 120px;
            background: linear-gradient(90deg, #8A44A1, #2E9A94, #F3C314);
            border: none;
            border-radius: 4px;
            margin-bottom: 40px;
        }}
        
        .team-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
        }}
        
        .team-card {{
            position: relative;
            background-color: #FFFFFF;
            border-radius: 20px;
            padding-top: 80px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .member-photo {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            object-fit: cover;
            display: block;
            position: absolute;
            top: -60px; 
            left: 50%;
            transform: translateX(-50%);
            border: 8px solid var(--member-color);
            background-color: white;
        }}
        
        .member-info {{
            padding: 30px 20px 40px;
            color: {card_text_color};
        }}
        
        .member-name {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .member-role {{
            font-size: 24px;
            font-weight: 400;
            opacity: 0.8;
        }}

        /* Content wrapper for scaling */
        .content-wrapper {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 1920px;
            height: 1080px;
            overflow: visible;
            background: inherit;
        }}
        
        .outer-wrapper {{
            padding: 0;
            box-sizing: border-box;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
        }}

    </style>
</head>
<body>
    <div class="outer-wrapper">
        <div class="content-wrapper">
            <div class="slide-container">
                <div class="text-column">
                    <h1 class="main-title">{main_title}</h1>
                    <hr class="title-divider" />
                </div>
                <div class="team-grid">
                    {team_members_html}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code
#ngon

def generate_corporate_team_slide(
    main_title="Our Creative Team",
    team_members=[
        { "name": "Olivia Chen", "role": "Lead Designer", "image_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1887&auto=format=fit=crop" },
        { "name": "Ben Carter", "role": "Photographer", "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1887&auto=format=fit=crop" },
        { "name": "Aisha Khan", "role": "Content Strategist", "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1887&auto=format=fit=crop" },
        { "name": "Leo Martinez", "role": "Illustrator", "image_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=1887&auto=format=fit=crop" }
    ],
    font_family_heading="'Patrick Hand', cursive",
    font_family_body="'Lato', sans-serif",
    text_color="#4A403A",
    role_color="#6B7280",
    bg_url="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png"
):
    """
    Generates a creative, personal, and STATIC 'Meet the Team' slide with a Polaroid photo theme.
    Hover effects have been removed.
    """
    team_members_html = "".join([f"""<div class="polaroid-card"><img class="member-photo" src="{member['image_url']}" alt="{member['name']}" /><div class="member-info"><h2 class="member-name">{member['name']}</h2><p class="member-role">{member['role']}</p></div></div>""" for member in team_members])
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Team Presentation - Polaroid Style</title>
    <link href="https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        /* OVERRIDE EDITOR BACKGROUND - HIGHEST SPECIFICITY */
        div[style*="background: white"], 
        div[style*="background: #FFFFFF"],
        div[style*="background-color: white"],
        div[style*="background-color: #FFFFFF"],
        #canvas,
        [data-bg*="#FFFFFF"] {{
            background: url('{bg_url}') repeat center !important;
            background-color: #F8F8F8 !important;
        }}
        
        html#html.html {{ font-size: 16px !important; }}
        
        body#body.body, html#html.html {{
            height: 100vh !important; 
            width: 100vw !important; 
            font-family: {font_family_body} !important; 
            overflow: hidden !important; 
            background-color: #F8F8F8 !important; 
            background-image: url('{bg_url}') !important;
            background-repeat: repeat !important;
            background-position: center !important;
            background-size: auto !important;
        }}
        
        .slide-container {{ 
            width: 100% !important; 
            height: 100% !important; 
            display: flex !important; 
            flex-direction: column !important;
            background: transparent !important;
        }}
        .title-section {{ width: 100%; display: flex; justify-content: center; align-items: center; padding: 4rem 4rem 2rem 4rem; }}
        .main-title {{ font-family: {font_family_heading}; font-size: clamp(2.5rem, 6vw, 4rem); font-weight: 400; color: {text_color}; margin: 0; text-align: center; }}
        .content-section {{ flex: 1; width: 100%; display: flex; justify-content: center; align-items: center; padding: 0 4rem 4rem 4rem; }}
        .team-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 3rem; width: 100%; max-width: 80rem; }}
        .polaroid-card {{
            background: #FFFFFF; padding: 1rem 1rem 1.5rem 1rem; border-radius: 0.25rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .polaroid-card:nth-child(4n+1) {{ transform: rotate(-4deg); }}
        .polaroid-card:nth-child(4n+2) {{ transform: rotate(2deg); }}
        .polaroid-card:nth-child(4n+3) {{ transform: rotate(5deg); }}
        .polaroid-card:nth-child(4n+4) {{ transform: rotate(-2deg); }}
        .member-photo {{ width: 100%; display: block; margin-bottom: 1rem; }}
        .member-info {{ text-align: center; }}
        .member-name {{ font-family: {font_family_heading}; font-size: 1.75rem; color: {text_color}; margin-bottom: 0.25rem; }}
        .member-role {{ font-size: 1rem; color: {role_color}; line-height: 1.5; }}
        @media (max-width: 48rem) {{ body, html {{ height: auto; min-height: 100vh; overflow-y: auto; }} }}
    </style>
</head>
<body id="body" class="body">
    <div class="slide-container">
        <div class="title-section">
            <h1 class="main-title">{main_title}</h1>
        </div>
        <div class="content-section">
            <div class="team-grid">{team_members_html}</div>
        </div>
    </div>
</body>
</html>"""
    return html_code


#------------------------ SLIDE THANK YOU
def generate_thank_you_slide_2(
    main_text="THANKS!",
    question_text="Any questions?",
    
    font_family_heading="'Patrick Hand', cursive",
    font_family_body="'Lato', sans-serif",
    main_color="#56B2E8",
    text_color="#34495E",
    bg_url="https://www.toptal.com/designers/subtlepatterns/uploads/paper.png"
):
    """
    Generates a doodle-themed thank you slide with larger, more impactful fonts.
    """
    
    heart_svg = f"""
    <svg class="heart-icon" viewBox="0 0 100 95" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 15.7C35.2-12.2 0 4.6 0 32.5 0 52.2 21.9 66.9 50 90c28.1-23.1 50-37.8 50-57.5C100 4.6 64.8-12.2 50 15.7z"
              fill="none" stroke="{main_color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        <g stroke="{main_color}" stroke-width="1.5" stroke-linecap="round">
            <line x1="60" y1="45" x2="75" y2="40" />
            <line x1="62" y1="50" x2="80" y2="45" />
            <line x1="64" y1="55" x2="84" y2="50" />
            <line x1="66" y1="60" x2="86" y2="55" />
            <line x1="68" y1="65" x2="85" y2="60" />
        </g>
    </svg>
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You Slide - Large Font</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Patrick+Hand&family=Lato:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        /* OVERRIDE EDITOR BACKGROUND - HIGHEST SPECIFICITY */
        div[style*="background: white"], 
        div[style*="background: #FFFFFF"],
        div[style*="background-color: white"],
        div[style*="background-color: #FFFFFF"],
        #canvas,
        [data-bg*="#FFFFFF"] {{
            background: linear-gradient(to bottom, transparent 98.5%, #E0E0E0 98.5%), url('{bg_url}') !important;
            background-size: 3.5rem 3.5rem, auto !important;
            background-color: #FFFFFF !important;
        }}
        
        html#html.html {{ 
            font-size: 16px !important;
            height: 100vh !important;
            width: 100vw !important;
            font-family: {font_family_body} !important;
            color: {text_color} !important;
            overflow: hidden !important;
            background-color: #FFFFFF !important;
            background-image: linear-gradient(to bottom, transparent 98.5%, #E0E0E0 98.5%), url('{bg_url}') !important;
            background-size: 3.5rem 3.5rem, auto !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}
        
        body#body.body, html#html.html {{
            height: 100vh !important;
            width: 100vw !important;
            font-family: {font_family_body} !important;
            color: {text_color} !important;
            overflow: hidden !important;
            background-color: #FFFFFF !important;
            background-image: linear-gradient(to bottom, transparent 98.5%, #E0E0E0 98.5%), url('{bg_url}') !important;
            background-size: 3.5rem 3.5rem, auto !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        .slide-container {{
            width: 100vw;
            height: 100vh;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 3rem;
            position: relative;
            box-sizing: border-box;
            margin: 0;
        }}

        .heart-icon {{
            /* ĐÃ SỬA ĐỔI: Icon to hơn để nổi bật */
            width: 12rem;
            margin-bottom: 2rem;
        }}
        
        .main-text {{
            font-family: {font_family_heading};
            /* ĐÃ SỬA ĐỔI: Font to hơn để dễ nhìn trên web */
            font-size: clamp(5rem, 14vw, 10rem);
            color: {main_color};
            margin-bottom: 2rem;
            line-height: 1;
            white-space: nowrap;
            overflow: visible;
            transform: scale(1.1);
        }}

        .question-text {{
            /* ĐÃ SỬA ĐỔI: Font to hơn */
            font-size: 3rem;
            font-weight: 700;
            line-height: 1.3;
        }}
        
        @media (max-width: 48rem) {{
            .heart-icon {{ width: 6rem; }}
            .main-text {{ 
                font-size: clamp(3rem, 10vw, 6rem);
                transform: scale(1);
            }}
            .question-text {{ font-size: 1.5rem; }}
            .slide-container {{ padding: 2rem; }}
        }}
        
        @media (max-width: 30rem) {{
            .main-text {{ 
                font-size: 2.5rem;
                letter-spacing: -1px;
            }}
            .question-text {{ font-size: 1.2rem; }}
        }}
        
        /* Web container override */
        @media (min-width: 769px) {{
            .slide-container {{
                transform: scale(1.2);
                transform-origin: center center;
            }}
        }}
    </style>
</head>
<body id="body" class="body">
    <div class="slide-container">
        {heart_svg}
        <h1 class="main-text">{main_text}</h1>
        <p class="question-text">{question_text}</p>
    </div>
</body>
</html>"""
    
    return html_code




def generate_thank_you_slide_3(
    # Main content
    main_title="THANK YOU",
    
    # Contact information
    phone_number="123-456-7890",
    email="hello@reallygreatsite.com",
    show_phone=True,
    show_email=True,
    
    # Colors
    background_gradient_start="#4A90E2",
    background_gradient_end="#2E5BBA",
    main_title_color="#FFFFFF",
    contact_text_color="#FFFFFF",
    contact_icon_color="#FFFFFF",
    border_color="rgba(255, 255, 255, 0.4)",
    geometric_shape_colors=[
        "rgba(255, 255, 255, 0.1)",
        "rgba(255, 255, 255, 0.05)",
        "rgba(135, 206, 250, 0.2)",
        "rgba(100, 149, 237, 0.15)"
    ],
    
    # Typography
    font_family="'Segoe UI', 'Arial', sans-serif",
    main_title_font_size="6rem",
    main_title_font_weight="700",
    main_title_letter_spacing="0.1em",
    contact_font_size="1.2rem",
    contact_font_weight="400",
    contact_margin_top="60px",
    contact_gap="40px",
    
    # Layout
    slide_padding="60px",
    border_frame_padding="80px",
    border_style="2px solid",
    border_radius="8px",
    
    # Geometric shapes
    show_geometric_shapes=True,
    shape_animation=True,
    
    # Icons
    phone_icon="📞",
    email_icon="✉️",
    icon_margin_right="12px",
    
    # Responsive
    mobile_title_font_size="3.5rem",
    mobile_contact_font_size="1rem",
    mobile_contact_gap="25px",
    mobile_slide_padding="30px",
    mobile_border_padding="40px",
    
    # Additional styling
    additional_css=""
):
    """
    Generate an HTML slide for thank you page with contact information and geometric background.
    
    :param main_title: Main title text displayed prominently
    :param phone_number: Phone number to display
    :param email: Email address to display
    :param show_phone: Whether to show phone number
    :param show_email: Whether to show email address
    :param background_gradient_start: Starting color of background gradient
    :param background_gradient_end: Ending color of background gradient
    :param main_title_color: Color of the main title text
    :param contact_text_color: Color of contact information text
    :param contact_icon_color: Color of contact icons
    :param border_color: Color of the border frame
    :param geometric_shape_colors: List of colors for geometric shapes
    :param font_family: Font family for all text elements
    :param main_title_font_size: Font size of the main title
    :param main_title_font_weight: Font weight of the main title
    :param main_title_letter_spacing: Letter spacing of the main title
    :param contact_font_size: Font size of contact information
    :param contact_font_weight: Font weight of contact information
    :param contact_margin_top: Top margin for contact section
    :param contact_gap: Gap between contact items
    :param slide_padding: Padding around the slide
    :param border_frame_padding: Padding inside the border frame
    :param border_style: Style of the border frame
    :param border_radius: Border radius of the frame
    :param show_geometric_shapes: Whether to show geometric background shapes
    :param shape_animation: Whether to animate geometric shapes
    :param phone_icon: Icon for phone number
    :param email_icon: Icon for email
    :param icon_margin_right: Right margin for icons
    :param mobile_title_font_size: Title font size on mobile
    :param mobile_contact_font_size: Contact font size on mobile
    :param mobile_contact_gap: Contact gap on mobile
    :param mobile_slide_padding: Slide padding on mobile
    :param mobile_border_padding: Border padding on mobile
    :param additional_css: Additional CSS to include
    :return: A string containing the HTML code for the slide
    """
    
    # Generate contact information HTML
    contact_html = ""
    if show_phone:
        contact_html += f"""
        <div class="contact-item">
            <span class="contact-icon">{phone_icon}</span>
            <span class="contact-text">{phone_number}</span>
        </div>
        """
    
    if show_email:
        contact_html += f"""
        <div class="contact-item">
            <span class="contact-icon">{email_icon}</span>
            <span class="contact-text">{email}</span>
        </div>
        """
    
    # Generate geometric shapes HTML
    geometric_shapes_html = ""
    if show_geometric_shapes:
        animation_class = "animated" if shape_animation else ""
        geometric_shapes_html = f"""
        <div class="geometric-background {animation_class}">
            <div class="shape shape-1"></div>
            <div class="shape shape-2"></div>
            <div class="shape shape-3"></div>
            <div class="shape shape-4"></div>
            <div class="shape shape-5"></div>
            <div class="shape shape-6"></div>
            <div class="shape shape-7"></div>
            <div class="shape shape-8"></div>
        </div>
        """
    
    # Generate shape colors CSS
    shape_colors_css = ""
    for i, color in enumerate(geometric_shape_colors[:8], 1):
        shape_colors_css += f"""
        .shape-{i} {{
            background-color: {color};
        }}
        """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body, html {{
            height: 100%;
            font-family: {font_family};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, {background_gradient_start} 0%, {background_gradient_end} 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: {slide_padding};
            position: relative;
            box-sizing: border-box;
        }}
        
        .geometric-background {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }}
        
        .shape {{
            position: absolute;
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
            transition: transform 0.3s ease;
        }}
        
        .shape-1 {{
            width: 200px;
            height: 200px;
            top: 10%;
            left: 5%;
            transform: rotate(45deg);
        }}
        
        .shape-2 {{
            width: 150px;
            height: 150px;
            top: 20%;
            left: 15%;
            transform: rotate(-30deg);
        }}
        
        .shape-3 {{
            width: 180px;
            height: 180px;
            top: 5%;
            right: 10%;
            transform: rotate(60deg);
        }}
        
        .shape-4 {{
            width: 120px;
            height: 120px;
            top: 25%;
            right: 20%;
            transform: rotate(-45deg);
        }}
        
        .shape-5 {{
            width: 160px;
            height: 160px;
            bottom: 15%;
            left: 8%;
            transform: rotate(30deg);
        }}
        
        .shape-6 {{
            width: 140px;
            height: 140px;
            bottom: 25%;
            left: 20%;
            transform: rotate(-60deg);
        }}
        
        .shape-7 {{
            width: 190px;
            height: 190px;
            bottom: 10%;
            right: 5%;
            transform: rotate(75deg);
        }}
        
        .shape-8 {{
            width: 130px;
            height: 130px;
            bottom: 30%;
            right: 15%;
            transform: rotate(-15deg);
        }}
        
        .animated .shape:hover {{
            transform: scale(1.1) rotate(var(--rotation));
        }}
        
        {shape_colors_css}
        
        .content-frame {{
            border: {border_style} {border_color};
            border-radius: {border_radius};
            padding: {border_frame_padding};
            position: relative;
            z-index: 2;
            text-align: center;
            backdrop-filter: blur(5px);
            background: rgba(255, 255, 255, 0.05);
            width: 100%;
            max-width: 800px;
        }}
        
        .main-title {{
            font-size: 8rem;
            font-weight: {main_title_font_weight};
            color: {main_title_color};
            letter-spacing: {main_title_letter_spacing};
            text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            margin-bottom: 0;
        }}
        
        .contact-section {{
            margin-top: {contact_margin_top};
            display: flex;
            justify-content: center;
            align-items: center;
            gap: {contact_gap};
            flex-wrap: wrap;
        }}
        
        .contact-item {{
            display: flex;
            align-items: center;
            color: {contact_text_color};
            font-size: 3rem;
            font-weight: {contact_font_weight};
        }}
        
        .contact-icon {{
            margin-right: {icon_margin_right};
            color: {contact_icon_color};
            font-size: 1.2em;
        }}
        
        .contact-text {{
            color: {contact_text_color};
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .slide-container {{
                padding: {mobile_slide_padding};
            }}
            
            .content-frame {{
                padding: {mobile_border_padding};
            }}
            
            .main-title {{
                font-size: {mobile_title_font_size};
            }}
            
            .contact-section {{
                gap: {mobile_contact_gap};
                flex-direction: column;
            }}
            
            .contact-item {{
                font-size: {mobile_contact_font_size};
            }}
            
            .shape {{
                width: 80px !important;
                height: 80px !important;
            }}
        }}
        
        @media (max-width: 480px) {{
            .main-title {{
                font-size: 2.5rem;
                letter-spacing: 0.05em;
            }}
            
            .contact-item {{
                font-size: 0.9rem;
            }}
            
            .content-frame {{
                padding: 30px 20px;
            }}
        }}
        
        {additional_css}
    </style>
</head>
<body>
    <div class="slide-container">
        {geometric_shapes_html}
        
        <div class="content-frame">
            <h1 class="main-title">{main_title}</h1>
            
            <div class="contact-section">
                {contact_html}
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    return html_code




def generate_corporate_thank_you_slide(
        
    thanks_text="THANK YOU FOR WACTCHING!",
    font_family="'Montserrat', sans-serif",
    accent_color="#F97316",
    shadow_color="#EA580C",
    icon_color="#D1D5DB"
):
    """
    Generates a minimalist, corporate 'Thank You' slide.
    Features a simple icon, a thank you message, and the signature diagonal split design.
    """

    # SVG icon for a simple smiley face
    icon_svg = f"""
    <svg class="icon-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
        <line x1="9" y1="9" x2="9.01" y2="9"></line>
        <line x1="15" y1="9" x2="15.01" y2="9"></line>
    </svg>
    """
    
    # SVG clip-path definition
    clip_path_svg = """
    <svg width="0" height="0">
      <defs>
        <clipPath id="angled-thanks-divider" clipPathUnits="objectBoundingBox">
          <polygon points="0.15 0, 1 0, 1 1, 0 1" />
        </clipPath>
      </defs>
    </svg>
    """

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ font-size: 16px; }}
        body, html {{
            height: 100vh;
            width: 100vw;
            font-family: {font_family};
            overflow: hidden;
            background-color: #FFFFFF;
        }}

        .slide-container {{
            width: 100%; height: 100%;
            display: flex; position: relative;
        }}

        .content-column {{
            flex: 2;
            padding: 4rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .color-panel {{
            flex: 1;
            position: relative;
            background-color: {accent_color};
            clip-path: url(#angled-thanks-divider);
        }}

        .color-panel::before {{
            content: ''; position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: {shadow_color};
            clip-path: url(#angled-thanks-divider);
            transform: translateX(-1.5rem);
            z-index: -1;
        }}
        
        .icon-svg {{
            width: 3rem;
            height: 3rem;
            margin-bottom: 1.5rem;
        }}

        .main-thanks-text {{
            font-size: clamp(2.5rem, 8vw, 4rem);
            font-weight: 800;
            color: {accent_color};
            text-transform: uppercase;
        }}
        
        @media (max-width: 48rem) {{
            .content-column {{ text-align: center; align-items: center; }}
            .color-panel {{ display: none; }}
        }}

    </style>
</head>
<body>
    {clip_path_svg}
    <div class="slide-container">
        <div class="content-column">
            {icon_svg}
            <h1 class="main-thanks-text">{thanks_text}</h1>
        </div>
        <div class="color-panel"></div>
    </div>
</body>
</html>"""
    
    return html_code

