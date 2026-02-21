#---------------------- SLIDE INTRO
def generate_title_slide(
    main_title="BUSINESS PLAN",
    subtitle="2026 - 2030",
    bg_color="#1a4b8c",
    bg_gradient_to="#2a6cb7",
    text_color="#FFFFFF",
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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

def generate_title_slide_2(
    main_title="THIS IS YOUR<br><span class='highlight'>PRESENTATION</span><br>TITLE",
    font_family="'Montserrat', 'Inter', sans-serif",
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
    font_family="'Poppins', 'Inter', sans-serif",
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
    font_family="'Poppins', 'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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

# moi by Nam
def generate_training_intro_slide(
    main_title="Introduction",
    description_text="Briefly introduce yourself and explain the purpose of your training presentation. Discuss its objectives, and give the audience an idea of what to expect in the coming slides.",
    bg_color="#3a3a3a",
    title_color="#b8d89f",
    text_color="#e8d7a8",
    image_url="https://images.pexels.com/photos/3587620/pexels-photo-3587620.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    font_family="'Inter', sans-serif",
):
    """
    Generate a training introduction slide with dark background and bottom image.
    
    This slide features a two-section layout:
    - Top section: Dark background with title and description text
    - Bottom section: Full-width training/professional image
    
    :param main_title: Main title text (e.g., "Introduction")
    :param description_text: Description or explanation text below title
    :param bg_color: Background color for the top section (hex code)
    :param title_color: Color for the main title (hex code, light green by default)
    :param text_color: Color for the description text (hex code, light yellow by default)
    :param image_url: URL of the image to display in bottom section
    :param font_family: Font family for all text elements
    :param title_font_size: Font size for the main title
    :param text_font_size: Font size for the description text
    :param image_height: Height of the image section (percentage or px)
    :param custom_css: Additional custom CSS to be included
    :return: A string containing the HTML code for the slide
    """
    
    # Extract values if they're lists
    if isinstance(main_title, list) and len(main_title) > 0:
        main_title = main_title[0]
    
    if isinstance(description_text, list) and len(description_text) > 0:
        description_text = description_text[0]
    
    if isinstance(image_url, list) and len(image_url) > 0:
        image_url = image_url[0]

    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{ 
            font-size: 16px; 
            width: 100%;
            height: 100%;
        }}
        
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
            background: {bg_color};
            position: relative;
        }}
        
        /* Content wrapper for scaling */
        .content-wrapper {{
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: inherit;
        }}
        
        .outer-wrapper {{
            padding: 0;
            box-sizing: border-box;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        
        /* Top text section */
        .text-section {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 5% 7%;
            background: {bg_color};
        }}
        
        .title {{
            font-size: clamp(2rem, 8vw, 7rem);
            font-weight: 300;
            color: {title_color};
            margin-bottom: 2rem;
            letter-spacing: 0.02em;
            line-height: 1.1;
        }}
        
        .description {{
            font-size: clamp(1rem, 2.5vw, 2.4rem);
            color: {text_color};
            line-height: 1.5;
            max-width: 90%;
            font-weight: 300;
        }}
        
        /* Bottom image section */
        .image-section {{
            height: 55%;
            width: 100%;
            overflow: hidden;
            position: relative;
        }}
        
        .image-section img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
            display: block;
        }}
        

    </style>
</head>
<body>
    <div class="outer-wrapper">
        <div class="content-wrapper">
            <div class="slide-container">
                <!-- Top text section -->
                <div class="text-section">
                    <h1 class="title">{main_title}</h1>
                    <p class="description">{description_text}</p>
                </div>
                
                <!-- Bottom image section -->
                <div class="image-section">
                    <img src="{image_url}" alt="Training introduction image">
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_employee_intro_slide(
    main_title="Employee Transition Plan",
    subtitle="Use the following infographics to outline how your team or company will manage responsibilities and workflow during employee movement.",
    bg_color="#0d4d3d",
    title_color="#FFFFFF",
    subtitle_color="#FFFFFF",
    circle_color_1="#0a3d2f",
    circle_color_2="#10855b",
    circle_color_3="#2dd4bf",
    circle_color_4="#FFFFFF",
    font_family="'Inter', sans-serif",
):
    """
    Generate an Employee Introduction slide with decorative geometric circles.
    
    This function creates a modern presentation slide featuring:
    - Company name in top left
    - Large main title
    - Descriptive subtitle
    - Decorative overlapping circles on the right side
    - Professional green color scheme
    
    Args:
        company_name (str): Company name displayed at top left
        main_title (str): Main slide title
        subtitle (str): Descriptive text below title
        bg_color (str): Background color (default: dark green)
        company_text_color (str): Color for company name (default: cyan)
        title_color (str): Color for main title (default: white)
        subtitle_color (str): Color for subtitle (default: white)
        circle_color_1 (str): First circle color (darkest green)
        circle_color_2 (str): Second circle color (medium green)
        circle_color_3 (str): Third circle color (light cyan)
        circle_color_4 (str): Fourth circle color (white)
        font_family (str): Font family for all text
        
    Returns:
        str: Complete HTML code for the slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Employee Transition Plan</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {font_family};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            background: {bg_color};
            position: relative;
            overflow: hidden;
        }}
        
        .content-wrapper {{
            position: relative;
            width: 100%;
            height: 100%;
            padding: 80px 150px;
            z-index: 2;
        }}

        .main-content {{
            max-width: 900px;
        }}
        
        .main-title {{
            color: {title_color};
            font-size: 96px;
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 40px;
        }}
        
        .subtitle {{
            color: {subtitle_color};
            font-size: 24px;
            line-height: 1.6;
            font-weight: 400;
            max-width: 700px;
        }}
        
        .decorative-circles {{
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 900px;
            height: 900px;
            z-index: 1;
        }}
        
        .circle {{
            position: absolute;
            border-radius: 50%;
        }}
        
        .circle-1 {{
            width: 600px;
            height: 600px;
            background: radial-gradient(circle at 25% 25%, {circle_color_1}, #051f18, #000000);
            top: -80px;
            right: 180px;
            opacity: 0.95;
            box-shadow: 
                0 40px 100px rgba(0, 0, 0, 0.5),
                inset 0 0 80px rgba(45, 212, 191, 0.1);
        }}
        
        .circle-2 {{
            width: 520px;
            height: 520px;
            background: radial-gradient(circle at 35% 35%, {circle_color_2}, #0a5a3e, #042820);
            top: 40px;
            right: 120px;
            opacity: 0.9;
            box-shadow: 
                0 35px 80px rgba(16, 133, 91, 0.4),
                inset 0 0 60px rgba(45, 212, 191, 0.15);
        }}
        
        .circle-3 {{
            width: 450px;
            height: 450px;
            background: radial-gradient(circle at 30% 30%, {circle_color_3}, #16a174, #0e7557);
            top: 140px;
            right: 60px;
            opacity: 0.95;
            box-shadow: 
                0 30px 70px rgba(45, 212, 191, 0.3),
                inset 0 0 50px rgba(255, 255, 255, 0.1);
        }}
        
        .circle-4 {{
            width: 380px;
            height: 380px;
            background: radial-gradient(circle at 25% 25%, {circle_color_4}, #d1fae5, #a7f3d0);
            top: 250px;
            right: 10px;
            opacity: 1;
            box-shadow: 
                0 25px 60px rgba(255, 255, 255, 0.2),
                inset 0 0 40px rgba(45, 212, 191, 0.2);
        }}
        
        .circle-accent-1 {{
            width: 250px;
            height: 250px;
            background: radial-gradient(circle at 50% 50%, rgba(45, 212, 191, 0.4), rgba(45, 212, 191, 0.1), transparent);
            top: -120px;
            right: 450px;
            opacity: 0.7;
            filter: blur(30px);
        }}
        
        .circle-accent-2 {{
            width: 180px;
            height: 180px;
            background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1), transparent);
            bottom: -80px;
            right: 300px;
            opacity: 0.6;
            filter: blur(35px);
        }}
        
        .circle-accent-3 {{
            width: 320px;
            height: 320px;
            background: radial-gradient(circle at 50% 50%, rgba(16, 133, 91, 0.5), rgba(16, 133, 91, 0.2), transparent);
            top: 50%;
            right: 650px;
            transform: translateY(-50%);
            opacity: 0.5;
            filter: blur(40px);
        }}
        
        .circle-ring {{
            width: 700px;
            height: 700px;
            border: 3px solid rgba(45, 212, 191, 0.2);
            top: -100px;
            right: 150px;
            opacity: 0.4;
        }}
        
        .circle-ring-2 {{
            width: 500px;
            height: 500px;
            border: 2px solid rgba(255, 255, 255, 0.15);
            top: 100px;
            right: 200px;
            opacity: 0.3;
        }}
        
        /* Responsive wrapper for preview */
        .wrapper {{
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #1a1a1a;
        }}
        
        .scale-container {{
            transform-origin: center center;
        }}
        
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="scale-container" id="scaleContainer">
            <div class="slide-container">
                <div class="decorative-circles">
                    <div class="circle circle-ring"></div>
                    <div class="circle circle-ring-2"></div>
                    <div class="circle circle-accent-1"></div>
                    <div class="circle circle-accent-2"></div>
                    <div class="circle circle-accent-3"></div>
                    <div class="circle circle-1"></div>
                    <div class="circle circle-2"></div>
                    <div class="circle circle-3"></div>
                    <div class="circle circle-4"></div>
                </div>
                
                <div class="content-wrapper">
                    <div class="main-content">
                        <h1 class="main-title">{main_title}</h1>
                        <p class="subtitle">{subtitle}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_research_proposal_slide(
    title="Research Proposal Presentation",
    subtitle="PRODUCT RESEARCH PROPOSAL FOR INGOUDE COMPANY",
    bg_color="#FFFFFF",
    accent_color="#C4A57B",
    title_color="#000000",
    subtitle_color="#9B8B6F",
    left_bar_width="60"
):
    """
    Generate a minimalist research proposal title slide with geometric decorations.
    
    This function creates a clean, professional slide featuring:
    - Large bold title text
    - Subtitle in accent color
    - Geometric decorative elements (circles, arches, dots, bar)
    - Modern minimalist aesthetic
    
    Args:
        title (str): Main title text for the slide
        subtitle (str): Subtitle/description text
        bg_color (str): Background color (default: white)
        accent_color (str): Color for decorative elements (default: tan/brown)
        title_color (str): Color for main title (default: black)
        subtitle_color (str): Color for subtitle (default: darker tan)
        left_bar_width (str): Width of left decorative bar in pixels
    
    Returns:
        str: Complete HTML code for the slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Proposal Presentation</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background-color: {bg_color};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            background-color: {bg_color};
            overflow: hidden;
        }}
        
        /* Left decorative bar */
        .left-bar {{
            position: absolute;
            left: 0;
            top: 180px;
            width: {left_bar_width}px;
            height: 180px;
            background-color: {accent_color};
            opacity: 0.9;
        }}
        
        /* Content area */
        .content {{
            position: absolute;
            left: 120px;
            top: 50%;
            transform: translateY(-50%);
            max-width: 1200px;
            z-index: 10;
        }}
        
        .title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 110px;
            font-weight: 900;
            color: {title_color};
            line-height: 1.1;
            margin-bottom: 40px;
            letter-spacing: -2px;
        }}
        
        .subtitle {{
            font-family: 'Inter', sans-serif;
            font-size: 28px;
            font-weight: 500;
            color: {subtitle_color};
            letter-spacing: 4px;
            text-transform: uppercase;
        }}
        
        /* Decorative elements container */
        .decorations {{
            position: absolute;
            top: 0;
            right: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
            background-image: 
                linear-gradient({accent_color} 1px, transparent 1px),
                linear-gradient(90deg, {accent_color} 1px, transparent 1px);
            background-size: 40px 40px;
            opacity: 0.1;
        }}
        
        /* Central crosshair */
        .crosshair {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 400px;
            height: 400px;
        }}
        
        .crosshair-line {{
            position: absolute;
            background-color: {accent_color};
            opacity: 0.6;
        }}
        
        .crosshair-line.horizontal {{
            top: 50%;
            left: 0;
            width: 100%;
            height: 2px;
            transform: translateY(-50%);
        }}
        
        .crosshair-line.vertical {{
            top: 0;
            left: 50%;
            width: 2px;
            height: 100%;
            transform: translateX(-50%);
        }}
        
        /* Geometric shapes */
        .geometric-shape {{
            position: absolute;
            border: 2px solid {accent_color};
            opacity: 0.5;
        }}
        
        .triangle {{
            top: 200px;
            right: 300px;
            width: 0;
            height: 0;
            border-left: 50px solid transparent;
            border-right: 50px solid transparent;
            border-bottom: 86px solid {accent_color};
            opacity: 0.4;
        }}
        
        .square {{
            bottom: 300px;
            right: 200px;
            width: 80px;
            height: 80px;
            background-color: transparent;
        }}
        
        .hexagon {{
            top: 400px;
            left: 600px;
            width: 100px;
            height: 57px;
            background-color: {accent_color};
            position: relative;
            opacity: 0.3;
        }}
        
        .hexagon:before,
        .hexagon:after {{
            content: "";
            position: absolute;
            width: 0;
            border-left: 50px solid transparent;
            border-right: 50px solid transparent;
            left: 0;
        }}
        
        .hexagon:before {{
            bottom: 100%;
            border-bottom: 29px solid {accent_color};
        }}
        
        .hexagon:after {{
            top: 100%;
            border-top: 29px solid {accent_color};
        }}
        
        /* Data points */
        .data-point {{
            position: absolute;
            width: 8px;
            height: 8px;
            background-color: {accent_color};
            border-radius: 50%;
            opacity: 0.7;
        }}
        
        .data-point:nth-child(1) {{
            top: 250px;
            right: 350px;
        }}
        
        .data-point:nth-child(2) {{
            bottom: 350px;
            right: 250px;
        }}
        
        .data-point:nth-child(3) {{
            top: 450px;
            left: 650px;
        }}
        
        /* Responsive wrapper for preview */
        .wrapper {{
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #1a1a1a;
        }}
        
        .wrapper .slide-container {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="slide-container">
            <!-- Left decorative bar -->
            <div class="left-bar"></div>
            
            <!-- Main content -->
            <div class="content">
                <h1 class="title">{title}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
            
            <!-- Decorative elements -->
            <div class="decorations">
                <!-- Central crosshair -->
                <div class="crosshair">
                    <div class="crosshair-line horizontal"></div>
                    <div class="crosshair-line vertical"></div>
                </div>
                
                <!-- Geometric shapes -->
                <div class="triangle"></div>
                <div class="square geometric-shape"></div>
                <div class="hexagon"></div>
                
                <!-- Data points -->
                <div class="data-point"></div>
                <div class="data-point"></div>
                <div class="data-point"></div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_business_intro_slide(
    main_title="PRESENTATION",
    subtitle="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
    main_title_color="#0056d2",
    subtitle_color="#666666",
    accent_color="#0056d2",
    main_font="Arial, sans-serif",
    subtitle_font="Arial, sans-serif"
):
    """
    Generate a clean business presentation intro slide with centered text and decorative side circles.
    
    Args:
        main_title (str): Large main title text (e.g., "PRESENTATION")
        subtitle (str): Description text below main title
        bg_color (str): Background color (default: light gray)
        main_title_color (str): Color for main title (default: blue)
        subtitle_color (str): Color for subtitle text
        accent_color (str): Color for decorative circles
        main_font (str): Font family for main title
        subtitle_font (str): Font family for subtitle
    
    Returns:
        str: Complete HTML code for the business intro slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Presentation Intro</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: 1920px;
            height: 1080px;
            background: 
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 50px,
                    rgba(0, 86, 210, 0.03) 50px,
                    rgba(0, 86, 210, 0.03) 100px
                ),
                repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 50px,
                    rgba(0, 86, 210, 0.03) 50px,
                    rgba(0, 86, 210, 0.03) 100px
                ),
                linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }}
        
        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        
        .content {{
            text-align: center;
            z-index: 10;
            max-width: 1400px;
            padding: 0 100px;
        }}
        
        .main-title {{
            font-family: {main_font};
            font-size: 120px;
            font-weight: 900;
            color: {main_title_color};
            letter-spacing: 4px;
            margin-bottom: 30px;
            line-height: 1.1;
        }}
        
        .subtitle {{
            font-family: {subtitle_font};
            font-size: 28px;
            font-weight: 400;
            color: {subtitle_color};
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
        }}
        
        /* Decorative D-shapes on left and right */
        .circle-left {{
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 200px;
            height: 400px;
            background: {accent_color};
            border-radius: 0 200px 200px 0;
            z-index: 1;
        }}
        
        .circle-right {{
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 200px;
            height: 400px;
            background: {accent_color};
            border-radius: 200px 0 0 200px;
            z-index: 1;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Side circles -->
        <div class="circle-left"></div>
        <div class="circle-right"></div>
        
        <!-- Main content -->
        <div class="content">
            <div class="main-title">{main_title}</div>
            <div class="subtitle">{subtitle}</div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

# moi by Hien
def generate_title_slide_3(
    main_title="Your main presentation title",
    subtitle="Here is where your presentation begins",
    bg_color="#F5EBE0",
    text_color="#C41E3A",
    subtitle_color="#3D3D3D",
    font_family="'Lobster Two', 'Georgia', serif",
    show_top_lights=True,
    show_sparkles=True,
    custom_css=""
):
    """
    Generate a Christmas Lights themed presentation slide with string lights decoration.
    
    Parameters:
    - main_title: Main title text (default: "Your main presentation title")
    - subtitle: Subtitle text (default: "Here is where your presentation begins")
    - bg_color: Background color (default: "#F5EBE0")
    - text_color: Main title color (default: "#C41E3A")
    - subtitle_color: Subtitle color (default: "#3D3D3D")
    - font_family: Font family (default: "'Lobster Two', 'Georgia', serif")
    - show_top_lights: Show Christmas lights at top (default: True)
    - show_sparkles: Show decorative sparkles (default: True)
    - custom_css: Additional custom CSS (default: "")
    
    Returns:
    - HTML string for the slide
    """
    
    # Generate light bulbs with improved colors matching the image
    bulbs_html = ""
    bulb_colors = [
        ("#C85353", "#E87676", "#8B1A1A"),  # Red
        ("#D9B857", "#F0D67E", "#A88B2F"),  # Yellow
        ("#5BA9BD", "#7DC4D4", "#3A6B7A"),  # Blue
    ]
    
    # Positions for wire 1 - bulbs attached to upper wave points
    wire1_positions = [
        (55, 38), (180, 75), (380, 65), (580, 80), (780, 65), 
        (980, 80), (1180, 65), (1380, 80), (1580, 65), (1780, 80)
    ]
    
    # Positions for wire 2 - bulbs attached to lower wave points  
    wire2_positions = [
        (130, 62), (280, 88), (480, 42), (680, 82), (880, 42),
        (1080, 82), (1280, 42), (1480, 82), (1680, 42), (1850, 72)
    ]
    
    # Generate bulbs for wire 1
    for i, (x, y) in enumerate(wire1_positions):
        color_set = bulb_colors[i % 3]
        bulb_id = f"grad1-{i}"
        bulbs_html += f'''
                <g transform="translate({x}, {y})">
                    <defs>
                        <radialGradient id="{bulb_id}" cx="30%" cy="30%">
                            <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:1"/>
                            <stop offset="30%" style="stop-color:{color_set[1]};stop-opacity:1"/>
                            <stop offset="100%" style="stop-color:{color_set[2]};stop-opacity:1"/>
                        </radialGradient>
                    </defs>
                    <ellipse cx="2" cy="2" rx="17" ry="25" fill="#000" opacity="0.12"/>
                    <rect x="-6" y="-28" width="12" height="6" fill="#2a2a2a" rx="1"/>
                    <ellipse cx="0" cy="0" rx="15" ry="23" fill="url(#{bulb_id})"/>
                    <ellipse cx="-4" cy="-6" rx="5" ry="8" fill="white" opacity="0.7"/>
                </g>'''
    
    # Generate bulbs for wire 2
    for i, (x, y) in enumerate(wire2_positions):
        color_set = bulb_colors[i % 3]
        bulb_id = f"grad2-{i}"
        bulbs_html += f'''
                <g transform="translate({x}, {y})">
                    <defs>
                        <radialGradient id="{bulb_id}" cx="30%" cy="30%">
                            <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:1"/>
                            <stop offset="30%" style="stop-color:{color_set[1]};stop-opacity:1"/>
                            <stop offset="100%" style="stop-color:{color_set[2]};stop-opacity:1"/>
                        </radialGradient>
                    </defs>
                    <ellipse cx="2" cy="2" rx="17" ry="25" fill="#000" opacity="0.12"/>
                    <rect x="-6" y="-28" width="12" height="6" fill="#2a2a2a" rx="1"/>
                    <ellipse cx="0" cy="0" rx="15" ry="23" fill="url(#{bulb_id})"/>
                    <ellipse cx="-4" cy="-6" rx="5" ry="8" fill="white" opacity="0.7"/>
                </g>'''
    
    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title.replace('<br>', ' ')}</title>
    <link href="https://fonts.googleapis.com/css2?family=Lobster+Two:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: 1920px;
            height: 1080px;
            background: {bg_color};
            position: relative;
            overflow: hidden;
            font-family: {font_family};
        }}
        
        /* String Lights Top */
        .lights-top {{
            position: absolute;
            top: 0;
            left: 0;
            width: 1920px;
            height: 150px;
            display: {("block" if show_top_lights else "none")};
            z-index: 10;
        }}
        
        .lights-top svg {{
            width: 1920px;
            height: 150px;
        }}
        
        /* Content Container */
        .content {{
            position: absolute;
            top: 400px;
            left: 200px;
            width: 1520px;
            text-align: center;
            z-index: 5;
        }}
        
        .title {{
            font-size: 96px;
            color: {text_color};
            font-weight: 700;
            line-height: 1.1;
            margin: 0 0 40px 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .subtitle {{
            font-size: 32px;
            color: {subtitle_color};
            font-family: 'Georgia', serif;
            font-weight: 400;
            font-style: italic;
            margin: 0;
        }}
        
        /* Sparkles */
        .sparkle {{
            position: absolute;
            color: {text_color};
            font-size: 32px;
            opacity: {("0.6" if show_sparkles else "0")};
            z-index: 8;
        }}
        
        .sparkle-1 {{ top: 240px; left: 130px; transform: rotate(15deg); }}
        .sparkle-2 {{ top: 680px; left: 100px; transform: rotate(-20deg); font-size: 21px; }}
        .sparkle-3 {{ top: 240px; left: 1770px; transform: rotate(25deg); }}
        .sparkle-4 {{ top: 700px; left: 1780px; transform: rotate(-15deg); }}
        .sparkle-5 {{ top: 140px; left: 720px; transform: rotate(0deg); font-size: 21px; }}
        .sparkle-6 {{ top: 700px; left: 640px; transform: rotate(20deg); }}
        .sparkle-7 {{ top: 450px; left: 280px; transform: rotate(10deg); font-size: 24px; }}
        .sparkle-8 {{ top: 350px; left: 1600px; transform: rotate(-25deg); }}
        .sparkle-9 {{ top: 560px; left: 520px; transform: rotate(30deg); font-size: 19px; }}
        .sparkle-10 {{ top: 580px; left: 1340px; transform: rotate(-10deg); }}
        .sparkle-11 {{ top: 200px; left: 1100px; transform: rotate(20deg); font-size: 22px; }}
        .sparkle-12 {{ top: 630px; left: 1170px; transform: rotate(-30deg); font-size: 21px; }}
        
        {custom_css}
    </style>
</head>
<body>
    <!-- String Lights Top -->
    <div class="lights-top">
        <svg viewBox="0 0 1920 150" xmlns="http://www.w3.org/2000/svg">
            <!-- Two intertwined wire paths with smooth crossover pattern -->
            <path d="M -20 55 Q 80 30, 180 75 Q 280 110, 380 65 Q 480 30, 580 80 Q 680 115, 780 65 Q 880 30, 980 80 Q 1080 115, 1180 65 Q 1280 30, 1380 80 Q 1480 115, 1580 65 Q 1680 30, 1780 80 Q 1880 115, 1940 70" 
                  stroke="#2a2a2a" 
                  stroke-width="2.5" 
                  fill="none"
                  stroke-linecap="round"/>
            <path d="M -20 105 Q 80 80, 180 35 Q 280 65, 380 100 Q 480 80, 580 35 Q 680 65, 780 110 Q 880 80, 980 35 Q 1080 65, 1180 100 Q 1280 80, 1380 35 Q 1480 65, 1580 100 Q 1680 80, 1780 35 Q 1880 65, 1940 90" 
                  stroke="#2a2a2a" 
                  stroke-width="2.5" 
                  fill="none"
                  stroke-linecap="round"/>
            
            {bulbs_html}
        </svg>
    </div>

    
    <!-- Sparkles -->
    <div class="sparkle sparkle-1">✦</div>
    <div class="sparkle sparkle-2">✦</div>
    <div class="sparkle sparkle-3">✦</div>
    <div class="sparkle sparkle-4">✦</div>
    <div class="sparkle sparkle-5">✦</div>
    <div class="sparkle sparkle-6">✦</div>
    <div class="sparkle sparkle-7">✦</div>
    <div class="sparkle sparkle-8">✦</div>
    <div class="sparkle sparkle-9">✦</div>
    <div class="sparkle sparkle-10">✦</div>
    <div class="sparkle sparkle-11">✦</div>
    <div class="sparkle sparkle-12">✦</div>
    
    <!-- Main Content -->
    <div class="content">
        <h1 class="title">{main_title}</h1>
        <p class="subtitle">{subtitle}</p>
    </div>
</body>
</html>
    """
    
    return html_code

def generate_minimalist_slide(
    title="Your presentation title",
    subtitle="Here is where your presentation begins",
    font_family_title="Playfair Display, Georgia, serif",
    font_family_subtitle="Inter, sans-serif",
    background_color="#E8E3DC",
    text_color_title="#1A1A1A",
    text_color_subtitle="#4A4A4A",
    line_color="#2C2C2C",
    curve_color="#4A4A4A"
):
    """
    Generate a minimalist title slide with centered text and decorative curves.
    Uses fixed positioning (1920x1080px) compatible with HTML-to-absolute converter.
    Removes all responsive elements (flexbox, vw/vh units, @media queries) for reliable conversion.
    
    Args:
        title (str): The main title for the slide (112px serif font, centered at 1600px width)
        subtitle (str): Descriptive text below the title (26px sans-serif font)
        font_family_title (str): Font family for the title (default: Playfair Display, Georgia, serif)
        font_family_subtitle (str): Font family for the subtitle (default: Inter, sans-serif)
        background_color (str): The background color of the slide (default: #E8E3DC warm beige)
        text_color_title (str): Color for the title text (default: #1A1A1A dark gray)
        text_color_subtitle (str): Color for the subtitle text (default: #4A4A4A medium gray)
        line_color (str): Color for the horizontal decorative lines (default: #2C2C2C)
        curve_color (str): Color for the decorative SVG curves (default: #4A4A4A)
    
    Returns:
        str: Complete HTML code for the slide with fixed 1920x1080px dimensions and absolute positioning
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {font_family_subtitle};
            background-color: {background_color};
            width: 1920px;
            height: 1080px;
            overflow: hidden;
            position: relative;
        }}
        
        .title {{
            position: absolute;
            top: 450px;
            left: 160px;
            width: 1600px;
            font-family: {font_family_title};
            font-size: 112px;
            font-weight: 400;
            color: {text_color_title};
            text-align: center;
            line-height: 1.15;
            letter-spacing: -0.015em;
        }}
        
        .subtitle {{
            position: absolute;
            top: 620px;
            left: 160px;
            width: 1600px;
            font-family: {font_family_subtitle};
            font-size: 26px;
            font-weight: 300;
            color: {text_color_subtitle};
            text-align: center;
            letter-spacing: 0.015em;
        }}
        
        .top-line {{
            position: absolute;
            top: 40px;
            left: 0;
            width: 1920px;
            height: 2px;
            background-color: {line_color};
        }}
        
        .bottom-line {{
            position: absolute;
            top: 1040px;
            left: 0;
            width: 1920px;
            height: 2px;
            background-color: {line_color};
        }}
    </style>
</head>
<body>
    <!-- Top horizontal line -->
    <div class="top-line"></div>
    
    <!-- Top-left decorative curve -->
    <svg width="400" height="220" viewBox="0 0 400 220" style="position: absolute; top: 0; left: 0;">
        <path d="M 0 180 Q 80 80, 200 40 Q 280 20, 400 0" 
              stroke="{curve_color}" 
              stroke-width="2.5" 
              fill="none"
              stroke-linecap="round"/>
    </svg>
    
    <!-- Content -->
    <h1 class="title">{title}</h1>
    <p class="subtitle">{subtitle}</p>
    
    <!-- Bottom-right decorative curve -->
    <svg width="400" height="220" viewBox="0 0 400 220" style="position: absolute; bottom: 0; right: 0;">
        <path d="M 400 20 Q 300 170, 20 220" 
              stroke="{curve_color}" 
              stroke-width="3" 
              fill="none"
              stroke-linecap="round"/>
    </svg>
    
    <!-- Bottom horizontal line -->
    <div class="bottom-line"></div>
</body>
</html>"""
    
    return html_code



def generate_title_slide_5(
    top_left_text="Our shared moments",
    year="20XX",
    main_title="Your Title Here",
    bottom_text="Here is where your presentation begins",
    image_path="Image/generate_title_slide_5/Default_1.jpg",
    font_family="'Arial'",
    font_family_secondary="'Arial'",
    bg_color="#b8c8d4",
    text_color="#2c3e50",
    show_clover=True,
    show_decorative_lines=True,
    custom_css=""
):
    """
    Generate a notebook cover design slide with polaroid-style image and decorative elements.
    
    Parameters:
    - top_left_text: Text in top-left corner (default: "Our shared moments")
    - year: Year text in top-right corner (default: "20XX")
    - main_title: Main title text (default: "Your Title Here")
    - bottom_text: Text in bottom-right corner (default: "Here is where your presentation begins")
    - image_path: Path to polaroid image (default: "Image/generate_title_slide_5/Default_1.jpg")
    - font_family: Font for main title (default: "'Arial'")
    - font_family_secondary: Font for secondary text (default: "'Arial'")
    - bg_color: Background color (default: "#b8c8d4" - soft blue-gray)
    - text_color: Text color (default: "#2c3e50" - dark blue)
    - show_clover: Show four-leaf clover decoration (default: True)
    - show_decorative_lines: Show top/bottom decorative lines (default: True)
    - custom_css: Additional custom CSS (default: "")
    
    Returns:
    - HTML string for the slide
    """
    
    # SVG cho clover (cỏ bốn lá) - to hơn
    clover_svg = """
    <svg viewBox="0 0 100 100" style="width: 180px; height: 180px;">
        <g fill="#2d5f3f">
            <circle cx="35" cy="35" r="15"/>
            <circle cx="65" cy="35" r="15"/>
            <circle cx="35" cy="65" r="15"/>
            <circle cx="65" cy="65" r="15"/>
            <circle cx="50" cy="50" r="8"/>
            <rect x="48" y="65" width="4" height="25" fill="#2d5f3f"/>
        </g>
    </svg>
    """ if show_clover else ""
    
    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notebook Cover Design</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Courier New', monospace;
            width: 1920px;
            height: 1080px;
            overflow: hidden;
            background: {bg_color};
            background-image: 
                repeating-linear-gradient(0deg, rgba(255,255,255,0.03) 0px, transparent 1px, transparent 2px, rgba(255,255,255,0.03) 3px),
                repeating-linear-gradient(90deg, rgba(255,255,255,0.03) 0px, transparent 1px, transparent 2px, rgba(255,255,255,0.03) 3px);
            position: relative;
        }}
        
        .top-left {{
            position: absolute;
            top: 60px;
            left: 120px;
            font-size: 30px;
            color: {text_color};
            font-family: {font_family_secondary};
        }}
        
        .top-right {{
            position: absolute;
            top: 60px;
            right: 120px;
            font-size: 24px;
            color: {text_color};
            font-weight: bold;
            font-family: {font_family_secondary};
        }}
        
        .text-content {{
            position: absolute;
            top: 330px;
            left: 120px;
            max-width: 1000px;
            z-index: 1;
        }}
        
        .main-title {{
            font-size: 120px;
            color: {text_color};
            line-height: 1.2;
            font-weight: 400;
            font-family: {font_family};
            margin: 0;
        }}

        .image-container {{
            position: absolute;
            right: 200px;
            top: 240px;
            z-index: 2;
        }}

        .polaroid {{
            position: relative;
            width: 480px;
            height: 530px;
            background: white;
            padding: 18px;
            padding-bottom: 55px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.35);
            transform: rotate(6deg);
        }}

        .polaroid img {{
            width: 444px;
            height: 457px;
            object-fit: cover;
        }}
        
        .clover {{
            position: absolute;
            bottom: 30px;
            left: 120px;
            z-index: 10;
        }}
        
        .bottom-text {{
            position: absolute;
            bottom: 60px;
            right: 120px;
            font-size: 30px;
            color: {text_color};
            font-family: {font_family_secondary};
        }}
        
        .top-line {{
            position: absolute;
            top: 120px;
            left: 120px;
            width: 1680px;
            height: 3px;
            background: linear-gradient(to right, transparent, #8b4513 20%, #8b4513 80%, transparent);
        }}
        
        .horizontal-line {{
            position: absolute;
            bottom: 120px;
            left: 120px;
            width: 1680px;
            height: 3px;
            background: linear-gradient(to right, transparent, #8b4513 20%, #8b4513 80%, transparent);
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="top-left">{top_left_text}</div>
    <div class="top-right">{year}</div>
    
    <div class="text-content">
        <div class="main-title">{main_title}</div>
    </div>

    <div class="image-container">
        <div class="polaroid">
            <img src="{image_path}" alt="Notebook Cover Image">
        </div>
    </div>
    
    <div class="clover">{clover_svg}</div>
    {('<div class="top-line"></div>' if show_decorative_lines else '')}
    {('<div class="horizontal-line"></div>' if show_decorative_lines else '')}
    <div class="bottom-text">{bottom_text}</div>
</body>
</html>
    """
    
    return html_code



def generate_title_slide_7(
    main_title="Main Title Here",
    subtitle="Here is where your presentation begins",
    bg_color="#d4e8d4",
    card_bg_color="#faf8f0",
    border_color="#2d3e50",
    accent_color="#e17b6a",
    title_color="#2d3e50",
    subtitle_color="#6b7280",
    custom_css="",
):
    """
    Generate an HTML title slide with a single centered text frame and one bandage decoration above it.
    """

    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{main_title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family: 'Poppins', sans-serif; background-color:{bg_color}; min-height:100vh; display:flex; align-items:center; justify-content:center; overflow:hidden; }}
            .text-frame {{ width:1100px; padding:60px 80px; border-radius:24px; background:{card_bg_color}; border:5px solid {border_color}; box-shadow:0 12px 36px rgba(0,0,0,0.12); text-align:center; position:relative; }}
            .main-title {{ font-size:56px; font-weight:900; color:{title_color}; margin:0; }}
            .subtitle {{ font-size:34px; color:{subtitle_color}; margin-top:12px; line-height:1.2; }}
            .bandage-core {{ width:220px; height:70px; border-radius:24px; background:{accent_color}; box-shadow:0 8px 24px rgba(0,0,0,0.12); }}
            {custom_css}
        </style>
    </head>
    <body>
        <!-- Bandage (single element) positioned above the frame -->
        <div style="position:absolute; left:50%; top:32%; transform:translate(-50%,-50%); z-index:40;">
            <div class="bandage-core"></div>
        </div>

        <!-- Centered text frame with title above subtitle -->
        <div class="text-frame">
            <h1 class="main-title">{main_title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
    </body>
    </html>
    """

    return html_code

def generate_title_slide_11(
    main_title="Simple and Minimalist Thesis Defense",
    subtitle="Here is where your presentation begins",
    bg_left_color="#f5d7d7",
    bg_right_color="#e8e8e8",
    text_color="#2d2d2d"
):
    """
    Generate a ultra-minimalist introduction slide with split background colors.
    
    Parameters:
    - main_title: Main title text (str)
    - subtitle: Subtitle text below the title (str)
    - bg_left_color: Background color for left half (str)
    - bg_right_color: Background color for right half (str)
    - text_color: Text color (str)
    
    Returns:
    - HTML string for the slide
    """
    
    # Handle list inputs (take first element)
    if isinstance(main_title, list):
        main_title = main_title[0] if main_title else "Simple and Minimalist Thesis Defense"
    if isinstance(subtitle, list):
        subtitle = subtitle[0] if subtitle else "Here is where your presentation begins"
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minimalist Circle Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: linear-gradient(90deg, {bg_left_color} 0%, {bg_left_color} 50%, {bg_right_color} 50%, {bg_right_color} 100%);
            overflow: hidden;
            width: 100vw;
            height: 100vh;
        }}
        
        .slide-wrapper {{
            width: 1920px;
            height: 1080px;
            position: relative;
            transform-origin: top left;
        }}
        
        .slide-container {{
            width: 100%;
            height: 100%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        /* Content container */
        .content {{
            position: absolute;
            z-index: 5;
            text-align: center;
            top: 400px;
            left: 960px;
            transform: translateX(-50%);
            width: 1200px;
        }}
        
        .title {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 110px;
            font-weight: 400;
            color: {text_color};
            line-height: 1.2;
            margin-bottom: 0px;
        }}
        
        .subtitle {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            font-size: 36px;
            font-weight: 400;
            color: {text_color};
            margin-top: 40px;
            opacity: 0.9;
        }}
        
        /* Responsive scaling */
        @media (max-width: 1920px) {{
            .slide-wrapper {{
                transform: scale(0.8);
            }}
        }}
        
        @media (max-width: 1440px) {{
            .slide-wrapper {{
                transform: scale(0.6);
            }}
        }}
        
        @media (max-width: 768px) {{
            .slide-wrapper {{
                transform: scale(0.4);
            }}
        }}
        
        @media (max-width: 480px) {{
            .slide-wrapper {{
                transform: scale(0.25);
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-wrapper">
        <div class="slide-container">
            <!-- Content -->
            <div class="content">
                <h1 class="title">{main_title}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_title_slide_12(
    main_title="Elegant Black and White Thesis Defense",
    subtitle="Here is where your presentation begins",
    bg_color="#F5F5F5",
    circle_color="#E5E5E5",
    border_color="#000000",
    text_color="#000000"
):
    """
    Generate an elegant black and white minimalist slide with circular decoration.
    
    Args:
        main_title (str): Main title text
        subtitle (str): Subtitle text below main title
        bg_color (str): Background color (default: light gray)
        circle_color (str): Large circle decoration color (default: gray)
        border_color (str): Border frame color (default: black)
        text_color (str): Text color (default: black)
    
    Returns:
        str: Complete HTML code for the slide
    """
    
    # Handle list inputs by taking first element
    if isinstance(main_title, list):
        main_title = main_title[0] if main_title else "Elegant Black and White Thesis Defense"
    if isinstance(subtitle, list):
        subtitle = subtitle[0] if subtitle else "Here is where your presentation begins"
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elegant Black and White Thesis Defense</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&family=Open+Sans:wght@400&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Open Sans', sans-serif;
            background-color: {bg_color};
            overflow: hidden;
        }}
        
        .slide-wrapper {{
            width: 1920px;
            height: 1080px;
            position: relative;
            overflow: hidden;
            margin: 0 auto;
        }}
        
        /* Border frame */
        .border-frame {{
            position: absolute;
            top: 160px;
            left: 160px;
            right: 160px;
            bottom: 160px;
            border: 3px solid {border_color};
            z-index: 2;
        }}
        
        /* Large decorative circle */
        .decorative-circle {{
            position: absolute;
            top: 50%;
            right: -200px;
            transform: translateY(-50%);
            width: 700px;
            height: 700px;
            border-radius: 50%;
            background-color: {circle_color};
            z-index: 1;
        }}
        
        /* Content area */
        .content-wrapper {{
            position: absolute;
            top: 50%;
            left: 300px;
            transform: translateY(-50%);
            z-index: 3;
            max-width: 1100px;
        }}
        
        .main-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 88px;
            font-weight: 900;
            color: {text_color};
            line-height: 1.1;
            margin-bottom: 40px;
            letter-spacing: -1px;
        }}
        
        .subtitle {{
            font-family: 'Open Sans', sans-serif;
            font-size: 36px;
            font-weight: 400;
            color: {text_color};
            line-height: 1.4;
            opacity: 0.8;
        }}
        
        /* Responsive scaling */
        @media (max-width: 1920px) {{
            .slide-wrapper {{
                transform: scale(0.9);
            }}
        }}
        
        @media (max-width: 1600px) {{
            .slide-wrapper {{
                transform: scale(0.75);
            }}
        }}
        
        @media (max-width: 1280px) {{
            .slide-wrapper {{
                transform: scale(0.6);
            }}
        }}
        
        @media (max-width: 768px) {{
            .slide-wrapper {{
                transform: scale(0.35);
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-wrapper">
        <!-- Decorative circle -->
        <div class="decorative-circle"></div>
        
        <!-- Border frame -->
        <div class="border-frame"></div>
        
        <!-- Content -->
        <div class="content-wrapper">
            <h1 class="main-title">{main_title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_title_slide_13(
    main_title="Head of Presentation",
    subtitle="Here is where your presentation begins",
    bg_color="#E8F4F8",
    text_color="#1A1A4D",
    decoration_color="#A8D5E2",
):
    """
    Generate an HTML slide with diagonal geometric decorative elements
    matching the Inverse Functions design.
    
    Args:
        main_title: The main title text 
        subtitle: The subtitle text 
        bg_color: Background color (default: "#E8F4F8" - light cyan)
        text_color: Color for title and subtitle text (default: "#1A1A4D" - dark blue)
        decoration_color: Color for geometric decorations (default: "#A8D5E2" - light blue)
    
    Returns:
        HTML string for the complete slide
    """
    
    # Handle list inputs
    if isinstance(main_title, list):
        main_title = main_title[0] if main_title else "Inverse Functions"
    if isinstance(subtitle, list):
        subtitle = subtitle[0] if subtitle else "Here is where your presentation begins"
    if isinstance(bg_color, list):
        bg_color = bg_color[0] if bg_color else "#E8F4F8"
    if isinstance(text_color, list):
        text_color = text_color[0] if text_color else "#1A1A4D"
    if isinstance(decoration_color, list):
        decoration_color = decoration_color[0] if decoration_color else "#A8D5E2"
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inverse Functions Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Montserrat', sans-serif;
            overflow: hidden;
            background: linear-gradient(135deg, {bg_color} 0%, #D4E8F0 100%);
        }}

        .slide-wrapper {{
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}

        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .content {{
            text-align: center;
            z-index: 10;
            position: relative;
            max-width: 1400px;
        }}

        .main-title {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 100px;
            color: {text_color};
            line-height: 1.2;
            letter-spacing: -2px;
            margin-bottom: 30px;
        }}
        
        .subtitle {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 400;
            font-size: 40px;
            color: {text_color};
            opacity: 0.8;
            line-height: 1.4;
        }}

        /* Decorative geometric elements - rounded rectangles at diagonal angles */
        .geo-element {{
            position: absolute;
            border-radius: 50px;
            opacity: 0.6;
        }}

        /* Top-left corner elements */
        .geo-1 {{
            width: 120px;
            height: 350px;
            background: {decoration_color};
            top: -50px;
            left: -20px;
            transform: rotate(-45deg);
        }}

        .geo-2 {{
            width: 100px;
            height: 280px;
            background: {decoration_color};
            top: 20px;
            left: 120px;
            transform: rotate(-45deg);
            filter: brightness(0.85);
        }}

        .geo-3 {{
            width: 80px;
            height: 220px;
            background: {decoration_color};
            top: 80px;
            left: 240px;
            transform: rotate(-45deg);
            filter: brightness(1.1);
        }}

        /* Bottom-right corner elements */
        .geo-4 {{
            width: 100px;
            height: 280px;
            background: {decoration_color};
            bottom: 50px;
            right: 120px;
            transform: rotate(-45deg);
        }}

        .geo-5 {{
            width: 90px;
            height: 240px;
            background: {decoration_color};
            bottom: -30px;
            right: 0px;
            transform: rotate(-45deg);
            filter: brightness(0.85);
        }}

        .geo-6 {{
            width: 110px;
            height: 300px;
            background: {decoration_color};
            bottom: 100px;
            right: 250px;
            transform: rotate(-45deg);
            filter: brightness(1.1);
        }}

        /* Top-right small element */
        .geo-7 {{
            width: 70px;
            height: 180px;
            background: {decoration_color};
            top: 150px;
            right: 50px;
            transform: rotate(-45deg);
            filter: brightness(1.1);
        }}

        /* Small circle in top-left area */
        .geo-circle {{
            width: 80px;
            height: 80px;
            background: {decoration_color};
            border-radius: 50%;
            top: 50px;
            left: 50px;
            opacity: 0.5;
        }}

        /* Responsive scaling */
        @media (max-width: 1920px) {{
            .slide-container {{
                transform: scale(0.8);
            }}
        }}

        @media (max-width: 1440px) {{
            .slide-container {{
                transform: scale(0.6);
            }}
        }}

        @media (max-width: 1024px) {{
            .slide-container {{
                transform: scale(0.4);
            }}
        }}

        @media (max-width: 768px) {{
            .slide-container {{
                transform: scale(0.25);
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-wrapper">
        <div class="slide-container">
            <!-- Decorative geometric elements -->
            <div class="geo-element geo-circle"></div>
            <div class="geo-element geo-1"></div>
            <div class="geo-element geo-2"></div>
            <div class="geo-element geo-3"></div>
            <div class="geo-element geo-4"></div>
            <div class="geo-element geo-5"></div>
            <div class="geo-element geo-6"></div>
            <div class="geo-element geo-7"></div>

            <!-- Content -->
            <div class="content">
                <h1 class="main-title">{main_title}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_title_slide_15(
    main_title="SIMPLE MEETING",
    subtitle="Here is where your presentation begins",
    background_color="#F5F5F0",
    subtitle_color="#7A7A7A",
    title_color="#E8B45E",
    accent_line_color="#E37854",
    top_circle_color="#E37854",
    bottom_circle_color="#5A7A7F"
):
    """
    Generate a simple meeting slide with circles in corners.
    
    Parameters:
    - main_title: Main title text 
    - subtitle: Subtitle text above main title 
    - background_color: Background color (default: "#F5F5F0" - off white)
    - subtitle_color: Subtitle text color (default: "#7A7A7A" - gray)
    - title_color: Main title text color (default: "#E8B45E" - golden yellow)
    - accent_line_color: Horizontal line color (default: "#E37854" - coral orange)
    - top_circle_color: Top left circle color (default: "#E37854" - coral orange)
    - bottom_circle_color: Bottom right circle color (default: "#5A7A7F" - teal gray)
    
    Returns:
    - HTML string for the slide
    """
    
    # Handle list inputs by taking first element
    if isinstance(main_title, list):
        main_title = main_title[0] if main_title else "SIMPLE MEETING"
    if isinstance(subtitle, list):
        subtitle = subtitle[0] if subtitle else "Here is where your presentation begins"
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Meeting Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;800&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Montserrat', sans-serif;
            background-color: {background_color};
            overflow: hidden;
            width: 1920px;
            height: 1080px;
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}

        /* Top left circle decoration */
        .circle-top {{
            position: absolute;
            top: -350px;
            left: -350px;
            width: 700px;
            height: 700px;
            border-radius: 50%;
            background-color: {top_circle_color};
            z-index: 1;
        }}

        /* Bottom right circle decoration */
        .circle-bottom {{
            position: absolute;
            top: 730px;
            left: 1570px;
            width: 700px;
            height: 700px;
            border-radius: 50%;
            background-color: {bottom_circle_color};
            z-index: 1;
        }}

        /* Content container */
        .content {{
            position: relative;
            z-index: 10;
            text-align: center;
            max-width: 1400px;
            padding: 0 100px;
        }}

        .subtitle {{
            font-size: 32px;
            font-weight: 400;
            color: {subtitle_color};
            margin-bottom: 40px;
            letter-spacing: 0.5px;
        }}

        .main-title {{
            font-size: 100px;
            font-weight: 800;
            color: {title_color};
            letter-spacing: 8px;
            line-height: 1.1;
            margin-bottom: 30px;
        }}

        .accent-line {{
            width: 180px;
            height: 6px;
            background-color: {accent_line_color};
            margin: 0 auto;
            display: none;
        }}
    </style>
</head>
<body>
    <!-- Decorative circles -->
    <div class="circle-top"></div>
    <div class="circle-bottom"></div>
    
    <!-- Main content -->
    <div class="content">
        <div class="subtitle">{subtitle}</div>
        <h1 class="main-title">{main_title}</h1>
        <div class="accent-line"></div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_title_slide_17(
    main_title="Heading of Presentation",
    subtitle="Here is where your presentation begins",
    bg_color="#F5F5F5",
    title_color="#2D2D2D",
    subtitle_color="#6B6B6B",
    circle_color_1="#5DBBBB",
    circle_color_2="#6BA3C8",
    circle_color_3="#E8B858"
):
    """
    Generate a title slide with centered text content and decorative circles positioned at four corners.
    
    Parameters:
    - main_title: Main title text
    - subtitle: Subtitle text
    - bg_color: Background color
    - title_color: Main title color
    - subtitle_color: Subtitle text color
    - circle_color_1: First decorative circle color
    - circle_color_2: Second decorative circle color
    - circle_color_3: Third decorative circle color
    """
    
    # Handle list or string input for title
    if isinstance(main_title, list):
        main_title = main_title[0] if main_title else "TOWN HALL MEETING"
    
    if isinstance(subtitle, list):
        subtitle = subtitle[0] if subtitle else "Here is where your presentation begins"
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Town Hall Meeting Slide</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;800;900&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Montserrat', sans-serif;
            overflow: hidden;
        }}
        
        .slide-wrapper {{
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            background-color: {bg_color};
            position: relative;
            overflow: hidden;
        }}
        
        .content {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 10;
        }}
        
        .main-title {{
            font-size: 120px;
            font-weight: 900;
            color: {title_color};
            line-height: 1.2;
            letter-spacing: 2px;
            text-transform: uppercase;
            max-width: 1400px;
        }}
        
        .subtitle {{
            font-size: 40px;
            font-weight: 400;
            color: {subtitle_color};
            letter-spacing: 0.5px;
            margin-top: 30px;
        }}
        
        /* Decorative circles - all equal size, half visible */
        .circle {{
            position: absolute;
            border-radius: 50%;
            opacity: 0.6;
            width: 150px;
            height: 150px;
        }}
        
        /* Top left corner circles */
        .circle-tl-1 {{
            background-color: {circle_color_2};
            top: -75px;
            left: -75px;
        }}
        
        .circle-tl-2 {{
            background-color: {circle_color_3};
            top: 75px;
            left: -75px;
        }}
        
        /* Top right corner circles */
        .circle-tr-1 {{
            background-color: {circle_color_1};
            top: -75px;
            right: -75px;
        }}
        
        .circle-tr-2 {{
            background-color: {circle_color_2};
            top: 75px;
            right: -75px;
        }}
        
        /* Bottom left corner circles */
        .circle-bl-1 {{
            background-color: {circle_color_1};
            bottom: -75px;
            left: -75px;
        }}
        
        .circle-bl-2 {{
            background-color: {circle_color_2};
            bottom: 75px;
            left: -75px;
        }}
        
        /* Bottom right corner circles */
        .circle-br-1 {{
            background-color: {circle_color_1};
            bottom: -75px;
            right: -75px;
        }}
        
        .circle-br-2 {{
            background-color: {circle_color_3};
            bottom: 75px;
            right: -75px;
        }}
        

    </style>
</head>
<body>
    <div class="slide-wrapper">
        <div class="slide-container">
            <!-- Decorative circles in corners -->
            <div class="circle circle-tl-1"></div>
            <div class="circle circle-tl-2"></div>
            
            <div class="circle circle-tr-1"></div>
            <div class="circle circle-tr-2"></div>
            
            <div class="circle circle-bl-1"></div>
            <div class="circle circle-bl-2"></div>
            
            <div class="circle circle-br-1"></div>
            <div class="circle circle-br-2"></div>
            
            <!-- Main content -->
            <div class="content">
                <h1 class="main-title">{main_title}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_title_slide_18(
    main_title="Heading of Your Presentation",
    subtitle="Here is where your presentation begins",
    bg_pattern_color="#E8E8E8",
    card_bg_color="#F9ED9B",
    title_color="#000000",
    subtitle_color="#2D2D2D"
):
    """
    Generate a minimalist title slide with centered card containing title and subtitle on full-slide geometric cube pattern background.
    
    Parameters:
    - main_title: Main heading text
    - subtitle: Subtitle text below main title
    - bg_pattern_color: Color for the geometric cube pattern background
    - card_bg_color: Background color of center card
    - title_color: Color for main title text
    - subtitle_color: Color for subtitle text
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minimalist Pattern Meeting Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Open Sans', sans-serif;
            overflow: hidden;
            width: 1920px;
            height: 1080px;
            position: relative;
            background-color: #F5F5F5;
        }}
        
        .pattern-background {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }}
        
        .content-card {{
            position: absolute;
            top: 215px;
            left: 535px;
            width: 850px;
            height: 650px;
            background-color: {card_bg_color};
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px;
            z-index: 10;
        }}
        
        .main-title {{
            font-family: 'Bebas Neue', sans-serif;
            font-size: 110px;
            font-weight: 400;
            color: {title_color};
            text-align: center;
            line-height: 1.1;
            margin-bottom: 40px;
            letter-spacing: 2px;
            max-width: 730px;
            border: none;
            outline: none;
            background: none;
        }}
        
        .subtitle {{
            font-family: 'Open Sans', sans-serif;
            font-size: 36px;
            font-weight: 400;
            color: {subtitle_color};
            text-align: center;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <!-- Geometric pattern background -->
    <svg class="pattern-background" xmlns="http://www.w3.org/2000/svg" width="1920" height="1080">
                <defs>
                    <pattern id="cubePattern" x="0" y="0" width="80" height="140" patternUnits="userSpaceOnUse">
                        <!-- Cube faces using geometric shapes -->
                        <polygon points="40,0 80,23 80,93 40,70" fill="{bg_pattern_color}" opacity="1"/>
                        <polygon points="0,23 40,0 40,70 0,93" fill="{bg_pattern_color}" opacity="0.8"/>
                        <polygon points="40,70 80,93 40,116 0,93" fill="{bg_pattern_color}" opacity="0.6"/>
                    </pattern>
                </defs>
                <rect width="1920" height="1080" fill="#F5F5F5"/>
                <rect width="1920" height="1080" fill="url(#cubePattern)"/>
            </svg>
    
    <div class="content-card">
        <h1 class="main-title">{main_title}</h1>
        <p class="subtitle">{subtitle}</p>
    </div>
</body>
</html>"""
    
    return html_code

#----------------------SLIDE CHUYỂN SLIDE

def generate_geometric_transition_slide(
    headline="TRANSITION HEADLINE",
    subtitle="Let's start with the first set of slides",
    font_family="'Poppins', 'Inter', sans-serif",
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

def generate_dusk_transition_slide(
    headline="Transition Headline",
    subtitle="Let's start with the first set of slides",
    font_family="'Nunito', 'Inter', sans-serif",
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
    font_family="'Poppins', 'Inter', sans-serif",
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
    font_family="'Poppins', 'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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

# moi    
def generate_research_proposal_transition_slide(
    headline="TRANSITION HEADLINE",
    subtitle="Let's start with the first set of slides",
    bg_color="#FFFFFF",
    accent_color="#C4A57B",
    number_color="#C4A57B",
    headline_color="#000000",
    subtitle_color="#9B8B6F",
    left_bar_width="60",
):
    """
    Generate a minimalist transition slide with geometric decorations.
    
    This function creates a clean, professional transition slide featuring:
    - Bold headline text
    - Descriptive subtitle
    - Geometric decorative elements (crosshair, shapes, grid, bar)
    - Modern minimalist aesthetic
    
    Args:
        headline (str): Main headline text for the transition
        subtitle (str): Subtitle/description text
        bg_color (str): Background color (default: white)
        accent_color (str): Color for decorative elements (default: tan/brown)
        number_color (str): Color for section number (default: tan/brown)
        headline_color (str): Color for headline (default: black)
        subtitle_color (str): Color for subtitle (default: darker tan)
        left_bar_width (str): Width of left decorative bar in pixels
    
    Returns:
        str: Complete HTML code for the transition slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transition Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background-color: {bg_color};
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            background-color: {bg_color};
            overflow: hidden;
        }}
        
        /* Left decorative bar */
        .left-bar {{
            position: absolute;
            left: 0;
            top: 180px;
            width: {left_bar_width}px;
            height: 180px;
            background-color: {accent_color};
            opacity: 0.9;
        }}
        
        /* Content area */
        .content {{
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 10;
            max-width: 1400px;
        }}
        
        .headline {{
            font-family: 'Montserrat', sans-serif;
            font-size: 90px;
            font-weight: 900;
            color: {headline_color};
            line-height: 1.1;
            margin-bottom: 30px;
            letter-spacing: -2px;
            text-transform: uppercase;
        }}
        
        .subtitle {{
            font-family: 'Inter', sans-serif;
            font-size: 32px;
            font-weight: 500;
            color: {subtitle_color};
            letter-spacing: 1px;
        }}
        
        /* Decorative elements container */
        .decorations {{
            position: absolute;
            top: 0;
            right: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
            background-image: 
                linear-gradient({accent_color} 1px, transparent 1px),
                linear-gradient(90deg, {accent_color} 1px, transparent 1px);
            background-size: 40px 40px;
            opacity: 0.08;
        }}
        
        /* Central crosshair */
        .crosshair {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 500px;
            height: 500px;
        }}
        
        .crosshair-line {{
            position: absolute;
            background-color: {accent_color};
            opacity: 0.4;
        }}
        
        .crosshair-line.horizontal {{
            top: 50%;
            left: 0;
            width: 100%;
            height: 2px;
            transform: translateY(-50%);
        }}
        
        .crosshair-line.vertical {{
            top: 0;
            left: 50%;
            width: 2px;
            height: 100%;
            transform: translateX(-50%);
        }}
        
        /* Geometric shapes */
        .geometric-shape {{
            position: absolute;
            border: 2px solid {accent_color};
            opacity: 0.4;
        }}
        
        .triangle {{
            top: 150px;
            right: 250px;
            width: 0;
            height: 0;
            border-left: 50px solid transparent;
            border-right: 50px solid transparent;
            border-bottom: 86px solid {accent_color};
            opacity: 0.3;
        }}
        
        .square {{
            bottom: 200px;
            right: 300px;
            width: 80px;
            height: 80px;
            background-color: transparent;
        }}
        
        .hexagon {{
            top: 200px;
            left: 200px;
            width: 100px;
            height: 57px;
            background-color: {accent_color};
            position: relative;
            opacity: 0.25;
        }}
        
        .hexagon:before,
        .hexagon:after {{
            content: "";
            position: absolute;
            width: 0;
            border-left: 50px solid transparent;
            border-right: 50px solid transparent;
            left: 0;
        }}
        
        .hexagon:before {{
            bottom: 100%;
            border-bottom: 29px solid {accent_color};
        }}
        
        .hexagon:after {{
            top: 100%;
            border-top: 29px solid {accent_color};
        }}
        
        /* Data points */
        .data-point {{
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: {accent_color};
            border-radius: 50%;
            opacity: 0.5;
        }}
        
        .data-point:nth-child(1) {{
            top: 180px;
            right: 400px;
        }}
        
        .data-point:nth-child(2) {{
            bottom: 250px;
            right: 350px;
        }}
        
        .data-point:nth-child(3) {{
            top: 250px;
            left: 300px;
        }}
        
        .data-point:nth-child(4) {{
            bottom: 180px;
            left: 250px;
        }}
        
        /* Responsive wrapper for preview */
        .wrapper {{
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #1a1a1a;
        }}
        
        .wrapper .slide-container {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="slide-container">
            <!-- Left decorative bar -->
            <div class="left-bar"></div>
            
            <!-- Main content -->
            <div class="content">
                <h1 class="headline">{headline}</h1>
                <p class="subtitle">{subtitle}</p>
            </div>
            
            <!-- Decorative elements -->
            <div class="decorations">
                <!-- Central crosshair -->
                <div class="crosshair">
                    <div class="crosshair-line horizontal"></div>
                    <div class="crosshair-line vertical"></div>
                </div>
                
                <!-- Geometric shapes -->
                <div class="triangle"></div>
                <div class="square geometric-shape"></div>
                <div class="hexagon"></div>
                
                <!-- Data points -->
                <div class="data-point"></div>
                <div class="data-point"></div>
                <div class="data-point"></div>
                <div class="data-point"></div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_business_transition_slide(
    headline="TRANSITION",
    subtitle="Let's start with the next section",
    headline_color="#0056d2",
    subtitle_color="#666666",
    accent_color="#0056d2",
    headline_font="Arial, sans-serif",
    subtitle_font="Arial, sans-serif"
):
    """
    Generate a clean business transition slide with centered text and decorative side D-shapes.
    
    Args:
        headline (str): Main transition headline (e.g., "TRANSITION")
        subtitle (str): Subtitle text below headline
        headline_color (str): Color for headline (default: blue)
        subtitle_color (str): Color for subtitle text
        accent_color (str): Color for decorative D-shapes
        headline_font (str): Font family for headline
        subtitle_font (str): Font family for subtitle
    
    Returns:
        str: Complete HTML code for the business transition slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Transition</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: 1920px;
            height: 1080px;
            background: 
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 50px,
                    rgba(0, 86, 210, 0.03) 50px,
                    rgba(0, 86, 210, 0.03) 100px
                ),
                repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 50px,
                    rgba(0, 86, 210, 0.03) 50px,
                    rgba(0, 86, 210, 0.03) 100px
                ),
                linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }}
        
        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        
        .content {{
            text-align: center;
            z-index: 10;
            max-width: 1400px;
            padding: 0 100px;
        }}
        
        .headline {{
            font-family: {headline_font};
            font-size: 140px;
            font-weight: 900;
            color: {headline_color};
            letter-spacing: 8px;
            margin-bottom: 40px;
            line-height: 1.1;
            text-transform: uppercase;
        }}
        
        .subtitle {{
            font-family: {subtitle_font};
            font-size: 36px;
            font-weight: 400;
            color: {subtitle_color};
            line-height: 1.6;
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        /* Decorative D-shapes on left and right */
        .circle-left {{
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 200px;
            height: 400px;
            background: {accent_color};
            border-radius: 0 200px 200px 0;
            z-index: 1;
        }}
        
        .circle-right {{
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 200px;
            height: 400px;
            background: {accent_color};
            border-radius: 200px 0 0 200px;
            z-index: 1;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Side D-shapes -->
        <div class="circle-left"></div>
        <div class="circle-right"></div>
        
        <!-- Main content -->
        <div class="content">
            <div class="headline">{headline}</div>
            <div class="subtitle">{subtitle}</div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_section_header_slide_5(
    section_title="THIS IS THE TITLE OF THIS SECTION",
    bg_color="#1a3d4a",
    text_color="#ffffff",
    stripe_color="#2a5566",
    custom_css="",
):
    """
    Generate an HTML slide with a split design: title on left, stripes on right.
    """
    
    # Handle list inputs
    if isinstance(section_title, list):
        section_title = section_title[0] if section_title else "THIS IS THE TITLE OF THIS SECTION"
    
    # Create vertical stripes pattern (always shown)
    stripes_html = """
        <div class="stripes">
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
            <div class="stripe"></div>
        </div>
        """
    
    # Create curved line SVG (always shown)
    curved_line_html = f"""
        <svg class="curved-line" viewBox="0 0 600 200" xmlns="http://www.w3.org/2000/svg">
            <path d="M 0 100 Q 150 50, 300 100 T 600 100" 
                  stroke="{stripe_color}" 
                  stroke-width="2" 
                  fill="none"
                  opacity="0.4"/>
        </svg>
        """
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Section Slide</title>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            html {{
                width: 1920px;
                height: 1080px;
            }}
            
            body {{
                width: 1920px;
                height: 1080px;
                font-family: 'Playfair Display', serif;
                background: {bg_color};
                color: {text_color};
                position: relative;
                overflow: hidden;
            }}
            
            /* Title on left */
            .section-title {{
                position: absolute;
                top: 280px;
                left: 80px;
                width: 800px;
                font-size: 5rem;
                font-weight: 900;
                line-height: 1.1;
                letter-spacing: 0.02em;
                text-transform: uppercase;
                z-index: 2;
            }}
            
            /* Stripes on right */
            .stripes {{
                position: absolute;
                top: 0;
                right: 0;
                width: 960px;
                height: 1080px;
                display: flex;
                gap: 30px;
                opacity: 0.3;
            }}
            
            .stripe {{
                flex: 1;
                background: {stripe_color};
            }}
            
            /* Curved line */
            .curved-line {{
                position: absolute;
                bottom: 80px;
                left: 660px;
                width: 600px;
                height: 200px;
            }}
            
            {custom_css}
        </style>
    </head>
    <body>
        <h1 class="section-title">{section_title}</h1>
        {stripes_html}
        {curved_line_html}
    </body>
    </html>
    """
    
    return html_code

def generate_section_header_slide_6(
    title="INTRODUCTION",
    description="Here you can add a brief description of the topic you want to talk aboout.",
    bg_color="#ffffff",
    bg_gradient_to="#e3f2fd",
    title_color="#1a1a1a",
    text_color="#4a4a4a",
    underline_color="#1a1a1a",
    custom_css=""
):
    """
    Generates a clean and elegant section header slide with centered content.
    
    This function creates a simple introduction slide with a title, optional underline,
    and description text. The slide uses a gradient background and centers all content
    vertically and horizontally.
    
    Args:
        title: Main heading text for the slide
        description: Supporting text displayed below the title and underline
        bg_color: Starting color of the background gradient (top)
        bg_gradient_to: Ending color of the background gradient (bottom)
        title_color: Color of the main title text
        text_color: Color of the description text
        underline_color: Color of the decorative underline
        (Underline is always displayed in this variant.)
        custom_css: Additional CSS rules to inject into the style block
    
    """
    
    # Handle list inputs
    if isinstance(title, list):
        title = title[0] if title else "INTRODUCTION"
    if isinstance(description, list):
        description = description[0] if description else ""
    
    underline_html = '''
        <div class="underline"></div>
    '''
    
    html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(to bottom, {bg_color} 0%, {bg_gradient_to} 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 100px;
            position: relative;
        }}
        
        .content {{
            max-width: 1400px;
            text-align: center;
        }}
        
        .title {{
            font-size: 5rem;
            font-weight: 700;
            color: {title_color};
            letter-spacing: 0.05em;
            margin-bottom: 30px;
        }}
        
        .underline {{
            width: 100%;
            height: 3px;
            background-color: {underline_color};
            margin-bottom: 50px;
        }}
        
        .description {{
            font-size: 2rem;
            color: {text_color};
            line-height: 1.8;
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        /* Responsive adjustments */
        @media (max-width: 1920px) {{
            .slide-container {{
                width: 100vw;
                height: 100vh;
                transform: scale(calc(100vw / 1920));
                transform-origin: top left;
            }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="content">
            <h1 class="title">{title}</h1>
            {underline_html}
            <p class="description">{description}</p>
        </div>
    </div>
</body>
</html>'''
    
    return html_code

def generate_section_header_slide_8(
    main_title="Name of the section",
    subtitle="You can enter a subtitle here if you need it",
    bg_color="#FFB84D",
    text_color="#2C2C2C",
    subtitle_color="#4A4A4A",
    custom_css="",
):
    """
    Simplified section slide: left-aligned text and external SVG on the right.
    This definition intentionally overrides the previous one in the file.
    """
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Section Slide</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Arial', sans-serif;
            overflow: hidden;
            margin: 0;
            padding: 0;
            width: 1920px;
            height: 1080px;
            background: {bg_color};
            position: relative;
        }}
        .content {{
            position: absolute;
            left: 6%;
            top: 50%;
            transform: translateY(-50%);
            z-index: 20;
            text-align: left;
            width: 44%;
            padding-right: 20px;
        }}
        .main-title {{ font-size: 5rem; font-weight: 900; color: {text_color}; margin: 0 0 12px 0; line-height: 1.05; }}
        .subtitle {{ font-size: 2.5rem; color: {subtitle_color}; font-weight: 400; line-height: 1.6; max-width: 100%; margin: 0; }}
        .svg-decoration {{
            position: absolute;
            right: 50px;
            top: 100%;
            transform: translateY(-50%);
            width: 900px;
            height: 1024px;
            z-index: 10;
        }}
        {custom_css}
    </style>
</head>
<body>
    <div class="content">
        <h1 class="main-title">{main_title}</h1>
        <p class="subtitle">{subtitle}</p>
    </div>
    <!-- Embedded SVG decoration (placed on the right side) -->
    <div class="svg-decoration">
        <svg xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 1200" width="100%" height="100%" preserveAspectRatio="xMidYMid meet"> <defs> <linearGradient id="d"> <stop stop-color="#ff6134" offset="0"/> <stop stop-color="#f00" offset="1"/> </linearGradient> <linearGradient id="h"> <stop stop-color="#5f0000" stop-opacity="0" offset="0"/> <stop stop-color="#f00" stop-opacity="0" offset=".5"/> <stop stop-color="#590000" offset="1"/> </linearGradient> <linearGradient id="c"> <stop stop-color="#525252" offset="0"/> <stop stop-color="#d9d9d9" offset="1"/> </linearGradient> <linearGradient id="a"> <stop offset="0"/> <stop stop-opacity="0" offset="1"/> </linearGradient> <linearGradient id="b"> <stop stop-color="#fff" offset="0"/> <stop stop-color="#fff" stop-opacity="0" offset="1"/> </linearGradient> <linearGradient id="j"> <stop stop-color="#00575f" stop-opacity="0" offset="0"/> <stop stop-color="#0062ff" stop-opacity="0" offset=".5"/> <stop stop-color="#002859" offset="1"/> </linearGradient> <linearGradient id="k"> <stop stop-color="#34abff" offset="0"/> <stop stop-color="#0057ff" offset="1"/> </linearGradient> <linearGradient id="e"> <stop stop-color="#ffff34" offset="0"/> <stop stop-color="#ffc200" offset="1"/> </linearGradient> <linearGradient id="i"> <stop stop-color="#5a5f00" stop-opacity="0" offset="0"/> <stop stop-color="#ffde00" stop-opacity="0" offset=".5"/> <stop stop-color="#cf9800" offset="1"/> </linearGradient> <linearGradient id="ce" x1="336.15" x2="345.4" y1="1203.6" y2="608.36" gradientTransform="matrix(1.2302 -.27318 .17203 .77468 -201.81 -17.563)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="cd" x1="-683.5" x2="1100.7" y1="-283.39" y2="504.58" gradientTransform="matrix(.83134 -.18461 .25456 1.1464 -201.81 -17.563)" gradientUnits="userSpaceOnUse" xlink:href="#j"/> <linearGradient id="cc" x1="350.37" x2="285.9" y1="168.43" y2="601.16" gradientTransform="matrix(1.1836 -.26282 .17881 .80521 -201.81 -17.563)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <linearGradient id="cj" x1="309.16" x2="302.31" y1="900.84" y2="958.59" gradientTransform="matrix(1.2191 0 0 .82029 0 -6)" gradientUnits="userSpaceOnUse" xlink:href="#k"/> <linearGradient id="ci" x1="299.34" x2="301.38" y1="959.69" y2="945.18" gradientTransform="matrix(1.2191 0 0 .82029 0 -6)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="ch" x1="293.05" x2="311.93" y1="901.66" y2="937.79" gradientTransform="matrix(1.2191 0 0 .82029 0 -6)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="cg" x1="293.24" x2="310.45" y1="923.83" y2="927.12" gradientTransform="matrix(1.2191 0 0 .82029 0 -6)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="cf" x1="1063" x2="1075" y1="281.09" y2="396.2" gradientTransform="matrix(.36618 0 0 2.7309 0 -6)" gradientUnits="userSpaceOnUse" xlink:href="#c"/> <linearGradient id="cb" x1="423.76" x2="448.12" y1="614.4" y2="654.13" gradientTransform="matrix(.82209 0 0 1.2164 0 -6)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#c"/> <linearGradient id="ca" x1="608.27" x2="572.03" y1="588.05" y2="590.56" gradientTransform="matrix(.64452 0 0 1.5515 0 -6)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#c"/> <linearGradient id="bz" x1="469.01" x2="491.66" y1="838.2" y2="843.22" gradientTransform="matrix(.81392 0 0 1.2286 0 -6)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#c"/> <linearGradient id="by" x1="365.56" x2="374.19" y1="996.04" y2="1011.3" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="bx" x1="376.49" x2="387.39" y1="736.07" y2="743.21" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#a"/> <linearGradient id="bw" x1="423.76" x2="448.12" y1="614.4" y2="654.13" gradientTransform="matrix(-.78264 .25163 .37232 1.158 576.36 -7.9357)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#c"/> <linearGradient id="bv" x1="370.79" x2="381.53" y1="747.38" y2="754.63" gradientTransform="matrix(1.0103 -.1009 .097869 .97999 -17.724 122.41)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#a"/> <linearGradient id="bu" x1="608.27" x2="572.03" y1="588.05" y2="590.56" gradientTransform="matrix(-.61798 .18305 .44065 1.4876 597.5 -4.4262)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#c"/> <linearGradient id="bt" x1="293.24" x2="310.45" y1="923.83" y2="927.12" gradientTransform="matrix(1.213 -.12114 .081515 .81623 1.6793 116.44)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="bs" x1="293.05" x2="311.93" y1="901.66" y2="937.79" gradientTransform="matrix(1.213 -.12114 .081515 .81623 1.6793 116.44)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="br" x1="299.34" x2="301.38" y1="959.69" y2="945.18" gradientTransform="matrix(1.213 -.12114 .081515 .81623 1.6793 116.44)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="bq" x1="309.16" x2="302.31" y1="900.84" y2="958.59" gradientTransform="matrix(1.213 -.12114 .081515 .81623 1.6793 116.44)" gradientUnits="userSpaceOnUse" xlink:href="#d"/> <linearGradient id="bp" x1="336.15" x2="345.4" y1="1203.6" y2="608.36" gradientTransform="matrix(1.197 -.39408 .24816 .75375 -200.28 124.99)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="bo" x1="-683.5" x2="1100.7" y1="-283.39" y2="504.58" gradientTransform="matrix(.80888 -.26631 .36722 1.1154 -200.28 124.99)" gradientUnits="userSpaceOnUse" xlink:href="#h"/> <linearGradient id="bn" x1="350.37" x2="285.9" y1="168.43" y2="601.16" gradientTransform="matrix(1.1516 -.37914 .25794 .78345 -200.28 124.99)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <linearGradient id="bm" x1="1063" x2="1075" y1="281.09" y2="396.2" gradientTransform="matrix(.36436 -.036388 .27138 2.7174 1.6793 116.44)" gradientUnits="userSpaceOnUse" xlink:href="#c"/> <linearGradient id="bl" x1="469.01" x2="491.66" y1="838.2" y2="843.22" gradientTransform="matrix(.80989 -.080882 .12209 1.2225 1.6793 116.44)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#c"/> <linearGradient id="bk" x1="432.33" x2="442.94" y1="816.66" y2="835.01" gradientTransform="matrix(.80989 -.080882 .12209 1.2225 1.6793 116.44)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="bj" x1="391.06" x2="584.44" gradientUnits="userSpaceOnUse" xlink:href="#e"/> <linearGradient id="bi" x1="309.16" x2="302.31" y1="900.84" y2="958.59" gradientTransform="matrix(.86745 -.09367 .43221 .63112 -2.0673 133.58)" gradientUnits="userSpaceOnUse" xlink:href="#d"/> <linearGradient id="bh" x1="423.76" x2="448.12" y1="614.4" y2="654.13" gradientTransform="matrix(.75888 .31614 -.46778 1.1229 639.92 -47.664)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#c"/> <linearGradient id="bg" x1="370.79" x2="381.53" y1="747.38" y2="754.63" gradientTransform="matrix(.93728 .39046 -.37874 .90913 637.62 -42.126)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#a"/> <linearGradient id="bf" x1="432.33" x2="442.94" y1="816.66" y2="835.01" gradientTransform="matrix(.75133 .313 -.47247 1.1341 639.92 -47.664)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="be" x1="469.01" x2="491.66" y1="838.2" y2="843.22" gradientTransform="matrix(.75133 .313 -.47247 1.1341 639.92 -47.664)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#c"/> <linearGradient id="bd" x1="608.27" x2="572.03" y1="588.05" y2="590.56" gradientTransform="matrix(.59496 .24785 -.59666 1.4322 639.92 -47.664)" gradientUnits="userSpaceOnUse" spreadMethod="reflect" xlink:href="#c"/> <linearGradient id="bc" x1="293.24" x2="310.45" y1="923.83" y2="927.12" gradientTransform="matrix(1.1253 .46881 -.31545 .75721 639.92 -47.664)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="bb" x1="293.05" x2="311.93" y1="901.66" y2="937.79" gradientTransform="matrix(1.1253 .46881 -.31545 .75721 639.92 -47.664)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="ba" x1="299.34" x2="301.38" y1="959.69" y2="945.18" gradientTransform="matrix(1.1253 .46881 -.31545 .75721 639.92 -47.664)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="az" x1="309.16" x2="302.31" y1="900.84" y2="958.59" gradientTransform="matrix(1.1253 .46881 -.31545 .75721 639.92 -47.664)" gradientUnits="userSpaceOnUse" xlink:href="#e"/> <linearGradient id="ay" x1="336.15" x2="345.4" y1="1203.6" y2="608.36" gradientTransform="matrix(1.2406 .2209 -.13911 .78126 458.08 -135.94)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <linearGradient id="ax" x1="-683.5" x2="1100.7" y1="-283.39" y2="504.58" gradientTransform="matrix(.8384 .14928 -.20585 1.1561 458.08 -135.94)" gradientUnits="userSpaceOnUse" xlink:href="#i"/> <linearGradient id="aw" x1="681" x2="606.26" y1="1.5028" y2="160.02" gradientTransform="matrix(1.1936 .21253 -.14459 .81205 0 0)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <linearGradient id="av" x1="1063" x2="1075" y1="281.09" y2="396.2" gradientTransform="matrix(.33802 .14082 -1.0502 2.5209 639.92 -47.664)" gradientUnits="userSpaceOnUse" xlink:href="#c"/> <linearGradient id="au" x1="309.16" x2="302.31" y1="900.84" y2="958.59" gradientTransform="matrix(.55499 .017588 .092123 .42968 275.04 290.57)" gradientUnits="userSpaceOnUse" xlink:href="#e"/> <linearGradient id="at" x1="878.35" x2="921.76" y1="504.53" y2="572.13" gradientTransform="matrix(.49907 .54378 -.99819 .91612 586.87 -250.89)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <linearGradient id="as" x1="878.35" x2="921.76" y1="504.53" y2="572.13" gradientTransform="matrix(.73148 .098521 -.18085 1.3427 97.836 -77.665)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <radialGradient id="ao" cx="413.89" cy="440.37" r="359.53" gradientTransform="matrix(.96831 -.21503 .29652 1.3353 -211.6 -61.667)" gradientUnits="userSpaceOnUse"> <stop stop-color="#00f1ff" stop-opacity="0" offset="0"/> <stop stop-color="#00c9ff" stop-opacity="0" offset=".5"/> <stop stop-color="#0065a6" stop-opacity="0" offset=".75"/> <stop stop-color="#002454" offset="1"/> </radialGradient> <radialGradient id="ae" cx="413.89" cy="440.37" r="359.53" gradientTransform="matrix(.94215 -.31018 .42774 1.2992 -214.4 82.076)" gradientUnits="userSpaceOnUse"> <stop stop-color="#f00" stop-opacity="0" offset="0"/> <stop stop-color="#f00" stop-opacity="0" offset=".5"/> <stop stop-color="#a60000" stop-opacity="0" offset=".75"/> <stop stop-color="#540000" offset="1"/> </radialGradient> <radialGradient id="r" cx="413.89" cy="440.37" r="359.53" gradientTransform="matrix(.97653 .17388 -.23978 1.3466 466 -180.42)" gradientUnits="userSpaceOnUse"> <stop stop-color="#ffdf00" stop-opacity="0" offset="0"/> <stop stop-color="#ff9f00" stop-opacity="0" offset=".5"/> <stop stop-color="#ff9a00" stop-opacity="0" offset=".75"/> <stop stop-color="#793900" offset="1"/> </radialGradient> <radialGradient id="g" cx="457.14" cy="263.79" r="94.286" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="f" cx="480.13" cy="516.87" r="175.44" gradientTransform="scale(.83995 1.1905)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="am" cx="478.66" cy="290.04" r="372.49" gradientTransform="matrix(.96831 -.21503 .29652 1.3353 -211.6 -61.667)" gradientUnits="userSpaceOnUse" xlink:href="#j"/> <radialGradient id="al" cx="462.46" cy="233.67" r="330.33" gradientTransform="matrix(.96831 -.21503 .29652 1.3353 -211.6 -61.667)" gradientUnits="userSpaceOnUse" xlink:href="#k"/> <radialGradient id="ar" cx="214.76" cy="1378.8" r="15.406" gradientTransform="matrix(1.4686 0 0 .42526 72.665 179.83)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="aq" cx="378.57" cy="752.36" r="8.5714" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="ap" cx="269.79" cy="1031.8" r="32.826" gradientTransform="scale(1.3926 .71807)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <radialGradient id="an" cx="376.4" cy="753.87" r="27.902" gradientUnits="userSpaceOnUse" xlink:href="#c"/> <radialGradient id="ak" cx="247.71" cy="1161.1" r="14.647" fy="1161.4" gradientTransform="scale(1.5804 .63275)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <radialGradient id="aj" cx="247.71" cy="1161.1" r="14.647" fy="1161.4" gradientTransform="matrix(1.5726 -.15705 .062879 .62962 -17.724 122.41)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <radialGradient id="ai" cx="370.71" cy="771.55" r="27.48" gradientTransform="matrix(1.0103 -.1009 .097869 .97999 -18.321 116.44)" gradientUnits="userSpaceOnUse" xlink:href="#c"/> <radialGradient id="ah" cx="378.57" cy="752.36" r="8.5714" gradientTransform="matrix(.44933 -.21734 .43543 .90022 -57.849 230.67)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="ag" cx="214.76" cy="1378.8" r="15.406" gradientTransform="matrix(1.4614 -.14594 .04226 .42316 92.451 294.13)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="af" cx="269.79" cy="1031.8" r="32.826" gradientTransform="matrix(1.3039 -.33682 .14896 .45905 -58.59 432.36)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <radialGradient id="ad" cx="480.13" cy="516.87" r="175.44" gradientTransform="matrix(.38873 -.31541 .42025 .51793 -35.161 543.49)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="ac" cx="480.13" cy="516.87" r="175.44" gradientTransform="matrix(.65225 -.52924 .75014 .92449 -378.41 379.69)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="ab" cx="457.14" cy="263.79" r="94.286" gradientTransform="matrix(1.1513 -.37905 .37905 1.1513 -309.88 102.16)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="aa" cx="457.14" cy="263.79" r="94.286" gradientTransform="matrix(.40297 -.13267 .13267 .40297 97.222 186.94)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="z" cx="478.66" cy="290.04" r="372.49" gradientTransform="matrix(.94215 -.31018 .42774 1.2992 -214.4 82.076)" gradientUnits="userSpaceOnUse" xlink:href="#h"/> <radialGradient id="y" cx="462.46" cy="233.67" r="330.33" gradientTransform="matrix(.94215 -.31018 .42774 1.2992 -214.4 82.076)" gradientUnits="userSpaceOnUse" xlink:href="#d"/> <radialGradient id="x" cx="893.91" cy="318.43" r="179.96" gradientTransform="scale(.72831 1.373)" gradientUnits="userSpaceOnUse" xlink:href="#d"/> <radialGradient id="w" cx="247.71" cy="1161.1" r="14.647" fy="1161.4" gradientTransform="matrix(1.4589 .60775 -.24333 .5841 637.62 -42.126)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <radialGradient id="v" cx="370.71" cy="771.55" r="27.48" gradientTransform="matrix(.93728 .39046 -.37874 .90913 639.92 -47.664)" gradientUnits="userSpaceOnUse" xlink:href="#c"/> <radialGradient id="u" cx="378.57" cy="752.36" r="8.5714" gradientTransform="matrix(.49865 .021831 -.043739 .99904 550.94 34.141)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="t" cx="214.76" cy="1378.8" r="15.406" gradientTransform="matrix(1.3557 .56477 -.16354 .39256 635.54 151.82)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="s" cx="269.79" cy="1031.8" r="32.826" gradientTransform="matrix(1.3076 .32203 -.086631 .47478 437 201.86)" gradientUnits="userSpaceOnUse" xlink:href="#a"/> <radialGradient id="q" cx="480.13" cy="516.87" r="175.44" gradientTransform="matrix(.49183 -.093258 .12426 .65531 404.91 310.8)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="p" cx="480.13" cy="516.87" r="175.44" gradientTransform="matrix(.82525 -.15648 .22179 1.1697 180.44 3.7704)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="o" cx="457.14" cy="263.79" r="94.286" gradientTransform="matrix(1.1934 .21248 -.21248 1.1934 372.42 -208.03)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="n" cx="457.14" cy="263.79" r="94.286" gradientTransform="matrix(.41767 .074369 -.074369 .41767 690.59 59.723)" gradientUnits="userSpaceOnUse" xlink:href="#b"/> <radialGradient id="m" cx="478.66" cy="290.04" r="372.49" gradientTransform="matrix(.97653 .17388 -.23978 1.3466 466 -180.42)" gradientUnits="userSpaceOnUse" xlink:href="#i"/> <radialGradient id="l" cx="462.46" cy="233.67" r="330.33" gradientTransform="matrix(.97653 .17388 -.23978 1.3466 466 -180.42)" gradientUnits="userSpaceOnUse" xlink:href="#e"/> </defs> <g transform="translate(164.09 17.006)"> <path d="m369.76 746.35 40.333 399.16h7.1117l-37.384-400.17-10.061 1.0102z" fill="url(#cf)" fill-rule="evenodd"/> <path d="m558.54 282.83c39.66 178.6-67.947 439.47-174.54 466.06-103.81 25.979-315.74-169.78-355.4-348.38s46.86-349.91 193.13-382.39 297.16 86.108 336.82 264.71z" fill="url(#al)" fill-rule="evenodd" opacity=".75"/> <path d="m558.54 282.83c39.66 178.6-67.947 439.47-174.54 466.06-103.81 25.979-315.74-169.78-355.4-348.38s46.86-349.91 193.13-382.39 297.16 86.108 336.82 264.71z" fill="url(#am)" fill-rule="evenodd"/> <path d="m171.19 67.388c-12.157 0.12378-36.516 19.763-45.87 30.673-19.234 22.433-30.838 37.65-41.846 61.974-16.9 37.343 4.575 39.084 32.847 16.12 21.599-17.544-12.858 35.603-15.812 47.412-4.9339 19.723-24.964 31.75-34.405 42.761-9.848 11.486-7.2461 33.213-27.588 47.101-22.198 15.155 18.255 23.315 29.746 28.515 18.361 8.3097-10.76 46.533 27.888 20.148 22.79-15.559 16.769-31.547 31.92-1.2348 4.9966 9.997 47.588-37.134 49.59-40.28 2.3396-3.6754-3.8543-56.896-4.6394-60.431-0.01593-0.07178 13.061-19.124 28.823-15.181 24.45 6.1164 16.739 28.761 38.737 3.1049 11.176-13.035 25.825 50.398 26.334 52.687 7.2909 32.832 48.788-4.8665 62.289 3.7282 14.421 9.1801 9.0842 39.312 25.714 49.898 13.119 8.3514 43.278-30.363 47.42-36.871 13.556-21.296 0.68902-23.511 38.118 0.31566 26.363 16.782 22.406-31.973 58.262-1.2308 21.82 18.709 6.7702-20.076 7.1328-33.778 0.61195-23.122-11.942-57.191-20.132-77.478-4.6345-11.481 44.373 16.124 36.567 6.5134-14.238-17.529-32.694-32.145-45.858-48.351-17.055-20.997-24.405-34.878-36.559-59.197-10.501-21.011-5.9465-25.34-22.617-35.952-17.603-11.206-33.648 17.928-44.935-4.6553-7.8512-15.708-37.869 9.4224-52.683-0.00796-4.1717-2.6556-16.656-32.666-19.828-36.571-6.9822-8.5961-42.542 3.5936-54.234 6.1898l-11.157 2.4775c-12.796 2.8416-28.611 3.4267-42.457 6.5015-1.0072 0.22366-12.546 19.486-20.767 25.099z" fill="url(#cc)" fill-rule="evenodd" opacity=".6"/> <path transform="matrix(.41416 -.091969 .091969 .41416 88.064 73.647)" d="m551.43 263.79c0 52.073-42.213 94.286-94.286 94.286s-94.286-42.213-94.286-94.286 42.213-94.286 94.286-94.286 94.286 42.213 94.286 94.286z" fill="url(#g)" fill-rule="evenodd"/> <path transform="matrix(1.1833 -.26277 .26277 1.1833 -308.6 -51.166)" d="m551.43 263.79c0 52.073-42.213 94.286-94.286 94.286s-94.286-42.213-94.286-94.286 42.213-94.286 94.286-94.286 94.286 42.213 94.286 94.286z" fill="url(#g)" fill-rule="evenodd" opacity=".6"/> <path d="m221.72 18.129c-146.27 32.48-232.8 203.77-193.14 382.37s251.61 374.37 355.42 348.39c106.6-26.598 214.21-287.48 174.55-466.08s-190.56-297.16-336.83-264.68zm-5.2444 5.3581c5.1999-1.6039 11.041-2.4297 17.65-2.2548 19.368 0.51262 32.663 26.514 38.091 26.658 20.479 0.54202 30.72-19.317 45.575-18.924 18.58 0.49176 21.189 8.7208 32.842 16.139 10.823 6.8899 24.287 20.228 38.738 29.427 11.837 7.5353 32.715 24.002 47.104 27.601 13.508 3.3792 31.701 11.002 34.698 24.498 6.3324 28.516-14.448 21.375-14.899 38.425-0.62 23.425 41.676 16.277 48.04 44.936 6.5796 29.629-30.816 41.326-22.019 45.864 0.17767 0.09165 72.199 61.527 30.995 60.437-23.067-0.61051-67.778-34.504-74.698-6.8446-2.5144 10.051-25.863 61.413-44.016 39.065-38.873-47.858-17.132 7.8411-68.795 6.4738-17.014-0.45032-14.751-19.047-14.254-37.809 2.0721-78.291-54.609-11.471-55.159-37.497-1.6588-78.521 6.5776-10.145-17.647-39.969-14.593-17.967-25.614-36.775-52.063-23.555-40.782 20.383-6.405 29.476-4.9505 56.703 1.3524 25.317-31.749 21.715-17.676 39.041 4.7249 5.8171 30.882 53.188 22.316 47.735l-10.252-6.5264c-36.746-23.391-37.037 43.629-65.062-3.0943-21.787-36.324-21.001 20.857-50.222 37.498-11.176 33.51-15.372 9.7713-19.197-7.4531-3.4558-15.562-0.49431-28.606-4.3283-45.871-6.2542-28.164 15.771-21.03 28.811-41.514 7.5872-11.919 36.258-30.446 9.3167-37.185-14.15-3.5397-37.511 6.5336-19.844-10.222 11.358-10.773 59.758-50.389 37.207-69.724-12.698-10.888-49.658-41.663-8.3746-50.831 36.849-8.1828 45.989-9.051 46.799-39.651 0.65948-24.917 38.08-10.894 51.461-31.915 8.2807-13.008 18.212-24.848 33.812-29.66z" fill="url(#cd)" fill-rule="evenodd" opacity=".4"/> <path transform="matrix(.8353 -.54979 .54979 .8353 -404.37 218.18)" d="m568.57 602.36c0 128.6-73.553 232.86-164.29 232.86s-164.29-104.25-164.29-232.86 73.553-232.86 164.29-232.86 164.29 104.25 164.29 232.86z" fill="url(#f)" fill-rule="evenodd" opacity=".53"/> <path transform="matrix(.49782 -.32766 .30801 .46797 -79.096 415.27)" d="m568.57 602.36c0 128.6-73.553 232.86-164.29 232.86s-164.29-104.25-164.29-232.86 73.553-232.86 164.29-232.86 164.29 104.25 164.29 232.86z" fill="url(#f)" fill-rule="evenodd" opacity=".3"/> <path d="m223.16 647.36c-18.335-24.262-60.967-66.679-84.57-101.25-13.367-19.579-23.259-50.613 1.3224-49.962 37.268 0.98637 32.963 59.583 31.556-7.0075-0.0903-4.2743 28.978 44.927 54.783 4.3909 20.491-32.189 27.586 49.668 31.545 67.498 1.5402 6.9357 35.923 12.726 49.962 1.3223 35.296-28.67 6.9329 34.373 6.5667 48.21-0.89095 33.662 73.164-41.607 76.703-46.006 32.961-40.966 50.845-10.706 72.759-45.13 23.006-36.141 48.395-65.382 66.192-93.341 14.1-22.149-23.01-31.227 10.087-47.769 25.06-12.525 21.8 45.562 16.208 54.347-13.638 21.424-38.608 14.175-39.451 46.012-0.52715 19.917-0.87959 33.317 4.374 56.975 4.6926 21.132-20.482 53.457-30.251 68.803-13.828 21.722-3.488 30.228-31.562 44.26-19.256 9.6243-21.792 50.293-39.451 46.012-13.722 11.146-36.205 27.079-46.023 35.054-18.363 14.915-39.258-16.116-68.368-9.6522-21.973 4.8795-45.83-9.4892-58.286-20.169-11.998-10.287-20.75-37.527-24.097-52.596z" fill="url(#ce)" fill-rule="evenodd" opacity=".1"/> <path d="m558.54 282.83c39.66 178.6-67.947 439.47-174.54 466.06-103.81 25.979-315.74-169.78-355.4-348.38s46.86-349.91 193.13-382.39 297.16 86.108 336.82 264.71z" fill="url(#ao)" fill-rule="evenodd"/> <path transform="matrix(.95567 -.14762 .1429 .65673 -91.365 302.37)" d="m421.43 740.93c0.00747 13.021-20.462 23.578-45.714 23.578s-45.722-10.558-45.714-23.578c-0.00747-13.021 20.462-23.578 45.714-23.578s45.722 10.558 45.714 23.578z" fill="url(#ap)" fill-rule="evenodd" opacity=".3"/> <path d="m372.75 735.24c-5.9355 3.6492-15.409 17.309-18.183 24.244-1.5433 3.8583-9.0917 5.0509-13.132 7.0711-7.9485 3.9742-3.7394 11.112 4.0406 11.112 10.363 0 20.275 0.0143 30.305 2.0203 7.5648 1.513 15.433 1.0102 23.234 1.0102 7.9438 0 8.9786-5.2763 7.0711-9.0914-1.7358-3.4716-10.956-7.7692-13.132-12.122-2.0656-4.1313-1.8953-18.342-7.0711-22.223-0.38095-0.28571-6.7176-5.9639-13.132-2.0203z" fill="url(#cj)" fill-rule="evenodd"/> <path d="m372.75 735.24c-5.9355 3.6492-15.409 17.309-18.183 24.244-1.5433 3.8583-9.0917 5.0509-13.132 7.0711-7.9485 3.9742-3.7394 11.112 4.0406 11.112 10.363 0 20.275 0.0143 30.305 2.0203 7.5648 1.513 15.433 1.0102 23.234 1.0102 7.9438 0 8.9786-5.2763 7.0711-9.0914-1.7358-3.4716-10.956-7.7692-13.132-12.122-2.0656-4.1313-1.8953-18.342-7.0711-22.223-0.38095-0.28571-6.7176-5.9639-13.132-2.0203z" fill="url(#ci)" fill-rule="evenodd"/> <path d="m372.75 735.24c-5.9355 3.6492-15.409 17.309-18.183 24.244-1.5433 3.8583-9.0917 5.0509-13.132 7.0711-7.9485 3.9742-3.7394 11.112 4.0406 11.112 10.363 0 20.275 0.0143 30.305 2.0203 7.5648 1.513 15.433 1.0102 23.234 1.0102 7.9438 0 8.9786-5.2763 7.0711-9.0914-1.7358-3.4716-10.956-7.7692-13.132-12.122-2.0656-4.1313-1.8953-18.342-7.0711-22.223-0.38095-0.28571-6.7176-5.9639-13.132-2.0203z" fill="url(#ch)" fill-rule="evenodd" opacity=".46759"/> <path d="m372.75 735.24c-5.9355 3.6492-15.409 17.309-18.183 24.244-1.5433 3.8583-9.0917 5.0509-13.132 7.0711-7.9485 3.9742-3.7394 11.112 4.0406 11.112 10.363 0 20.275 0.0143 30.305 2.0203 7.5648 1.513 15.433 1.0102 23.234 1.0102 7.9438 0 8.9786-5.2763 7.0711-9.0914-1.7358-3.4716-10.956-7.7692-13.132-12.122-2.0656-4.1313-1.8953-18.342-7.0711-22.223-0.38095-0.28571-6.7176-5.9639-13.132-2.0203z" fill="url(#cg)" fill-rule="evenodd" opacity=".50926"/> <path d="m358.6 766.36c3.3826 0.43801 11.266-0.30613 16.576-1.5379 4.4948-1.0425 7.2171-1.3132 9.9457-3.8446 3.9482-3.6629 3.8424-0.52886 9.1169 1.895 2.9303 3.1286 7.1762 2.0828 10.147 8.1011 2.9303 2.7186-11.804 0-15.948 0-4.452 0-8.2997-0.76893-12.432-0.76893-2.8509 0-8.6656-1.0487-10.775-1.5378-3.2818-0.76117-1.5859-1.3708-6.6305-2.3068z" fill="url(#ar)" fill-rule="evenodd" opacity=".67593"/> <path transform="matrix(.4687 -.17161 .34381 .93904 -50.684 103.73)" d="m387.14 752.36c0 4.7339-3.8376 8.5714-8.5714 8.5714s-8.5714-3.8376-8.5714-8.5714 3.8376-8.5714 8.5714-8.5714 8.5714 3.8376 8.5714 8.5714z" fill="url(#aq)" fill-rule="evenodd" opacity=".46759"/> <path d="m384.1 745.83c-0.3158 0.0821-0.62775-0.17836-0.94162-0.26754 7.0312 1.4632 0.11247-0.14806 1.1833-1.5578-0.28866-0.20965-0.10011 0.09788-0.23015 0.22502l4.0129-9.4232c1.896 1.2204 3.96 1.8661 5.0791 4.0618 4.6622 11.939-2.839 20.797-15.457 15.351-8.5854-7.9009-5.3668-17.927 6.3536-18.753v10.365z" fill="url(#an)"/> <path d="m389.06 848.98c19.503 32.603-39.407 32.936-38.039 67.422 1.3817 34.843 31.458 19.787 50.022 50.331l1.3578 12.088c-27.175-37.964-52.084-27.652-53.159-61.72s44.852-45.57 40.61-61.82l-0.79116-6.3017z" fill="url(#ca)"/> <path d="m395.35 1000.7c-9.2864 13.302-34.107 17.943-33.956 2.474 0.35989-36.898 41.699-9.7649 42.919 20.404 0.59378 14.678-36.308 13.991-42.145 26.91l-1.0611-8.487c4.8986-11.006 39.145-9.5745 37.448-17.73-5.8074-27.907-21.85-36.132-32.52-27.469 1.285 15.131 21.256 9.9175 28.94-3.5845l0.37509 7.482z" fill="url(#bz)"/> <path d="m409.79 998.3c-9.2864 9.0131-48.541 18.335-48.39 7.8531l4.641-4.3172c1.285 10.252 35.69 0.5431 43.374-8.6056l0.37509 5.0697z" fill="url(#by)"/> <path d="m384.1 745.83c-0.3158 0.0821-0.62775-0.17836-0.94162-0.26754 7.0312 1.4632 0.11247-0.14806 1.1833-1.5578-0.28866-0.20965-0.10011 0.09788-0.23015 0.22502l4.0129-9.4232c1.896 1.2204 3.96 1.8661 5.0791 4.0618 4.6622 11.939-2.839 20.797-15.457 15.351-8.5854-7.9009-5.3668-17.927 6.3536-18.753v10.365z" fill="url(#bx)"/> <path d="m392.33 736.55c-9.7508 22.191-12.99 1.4424-21.293 2.7533-12.743-0.02489-32.129 6.3088-38.989 16.555-9.4043 14.048-13.051 28.868-5.669 47.75 7.4303 19.005 29.43 25.712 53.501 39.274l0.31106 4.0082c-18.274-14.306-48.774-14.918-58.939-36.509-10.303-21.883-9.6147-39.627 10.162-58.705 10.473-9.7433 22.831-17.617 37.494-17.937l23.422 2.8103z" fill="url(#cb)"/> <path d="m392.33 736.55c-9.7508 22.191-12.99 1.4424-21.293 2.7533-12.743-0.02489-16.792-5.2439-2.1289-5.5636l23.422 2.8103z" fill="url(#ak)" opacity=".63889"/> </g> <path d="m695.62 790.56-117.58 373.78 10.257 2.2731 113.3-374.65-5.9833-1.3983z" fill="url(#av)" fill-rule="evenodd"/> <path d="m1044.4 433.74c-32.07 180.12-231.72 379.54-340.35 363.1-105.82-15.939-226.17-278.15-194.1-458.26s177.82-304.98 325.32-278.72 241.2 193.76 209.13 373.88z" fill="url(#l)" fill-rule="evenodd" opacity=".75"/> <path d="m1044.4 433.74c-32.071 180.12-231.72 379.54-340.35 363.1-105.82-15.939-226.17-278.15-194.1-458.26s177.82-304.98 325.32-278.72 241.2 193.76 209.13 373.88z" fill="url(#m)" fill-rule="evenodd"/> <path d="m769.73 85.914c-11.27-4.5609-41.308 4.2011-54.138 10.675-26.381 13.311-42.945 22.896-62.46 41.116-29.961 27.973-10.807 37.838 24.122 27.512 26.685-7.8888-25.56 27.921-32.829 37.686-12.139 16.309-35.254 19.708-48.204 26.242-13.508 6.8155-19.461 27.872-43.58 32.87-26.319 5.4529 7.8851 28.542 16.493 37.762 13.754 14.732-27.827 38.817 17.996 29.323 27.02-5.5982 27.612-22.672 29.94 11.135 0.76797 11.15 58.208-15.978 61.267-18.112 3.5731-2.493 18.322-54.003 18.957-57.568 0.0129-0.07239 19.41-12.631 32.444-2.9293 20.217 15.048 4.3917 32.987 34.564 17.763 15.33-7.7349 4.4585 56.453 4.0474 58.762-5.8957 33.111 46.908 14.269 56.066 27.395 9.7818 14.02-6.7319 39.782 4.5483 55.949 8.8988 12.754 51.626-11.386 57.953-15.8 20.703-14.445 9.6772-21.438 35.065 14.95 17.882 25.629 32.979-20.898 54.255 21.269 12.948 25.661 13.97-15.929 19.574-28.438 9.4565-21.108 10.969-57.385 11.211-79.262 0.137-12.38 34.76 31.948 31.251 20.075-6.4022-21.656-17.819-42.246-23.738-62.268-7.6688-25.941-9.1154-41.581-10.984-68.704-1.6141-23.433 4.2552-25.678-7.0526-41.885-11.94-17.113-37.954 3.6099-39.689-21.577-1.2067-17.52-38.58-5.8649-48.629-20.267-2.8297-4.0556-2.8132-36.559-4.2397-41.384-3.1396-10.62-40.653-13.043-52.443-15.142l-11.252-2.0034c-12.905-2.2978-27.729-7.8393-41.693-10.326-1.0157-0.18086-19.074 13.163-28.822 15.183z" fill="url(#aw)" fill-rule="evenodd" opacity=".6"/> <path d="m901.29 210.91c-3.8726 21.749-24.643 36.241-46.393 32.369s-36.241-24.643-32.369-46.393 24.643-36.241 46.393-32.369 36.241 24.643 32.369 46.393z" fill="url(#n)" fill-rule="evenodd"/> <path d="m974.42 223.93c-11.065 62.141-70.409 103.55-132.55 92.482s-103.55-70.409-92.482-132.55 70.409-103.55 132.55-92.482 103.55 70.409 92.482 132.55z" fill="url(#o)" fill-rule="evenodd" opacity=".6"/> <path d="m835.32 59.873c-147.51-26.265-293.26 98.576-325.33 278.69s88.292 442.34 194.11 458.28c108.63 16.44 308.29-183 340.36-363.11s-61.631-347.59-209.14-373.86zm-6.9016 2.9293c5.4168 0.51906 11.126 2.0029 17.16 4.7059 17.682 7.9213 19.956 37.036 24.91 39.256 18.696 8.3757 35.787-6.0177 49.348 0.05774 16.962 7.599 16.206 16.198 24.11 27.528 7.3415 10.522 14.64 28.012 24.443 42.061 8.0292 11.508 20.969 34.737 32.867 43.593 11.17 8.3139 25.033 22.347 22.609 35.958-5.1206 28.759-21.557 14.175-28.53 29.74-9.5807 21.386 32.212 31.052 27.065 59.954-5.3206 29.881-44.339 26.297-37.963 33.87 0.12877 0.15292 42.986 84.56 5.3702 67.709-21.058-9.434-49.298-57.915-66.321-35.044-6.1864 8.3115-47.491 46.745-55.653 19.134-17.479-59.127-18.83 0.64981-65.994-20.48-15.533-6.9586-6.2918-23.255 1.3818-40.383 32.02-71.473-45.999-31.589-36.498-55.825 28.664-73.121 9.9731-6.8354-0.91946-43.681-6.562-22.197-9.5024-43.797-39.001-41.765-45.485 3.1329-17.248 24.746-26.375 50.439-8.4872 23.89-37.658 7.8361-31.33 29.242 2.1246 7.1868 8.0537 60.974 2.2435 52.646l-6.9542-9.9671c-24.925-35.723-50.967 26.031-58.869-27.876-6.1429-41.909-27.407 11.177-60.78 15.301-23.203 26.636-17.948 3.1084-14.855-14.262 2.7945-15.694 10.544-26.596 13.645-44.008 5.0574-28.403 22.646-13.348 42.56-27.242 11.587-8.0845 45.177-14.161 22.9-30.743-11.7-8.7089-37.139-8.394-14.387-17.068 14.628-5.5763 74.54-23.533 61.159-50.054-7.535-14.934-29.817-57.556 11.817-50.142 37.162 6.6169 45.933 9.3303 58.448-18.605 10.191-22.747 39.341 4.5877 59.777-9.6709 12.646-8.8235 26.367-15.934 42.618-14.377z" fill="url(#ax)" fill-rule="evenodd" opacity=".4"/> <path d="m851.27 489.67c23.958 126.35-28.885 242.48-118.03 259.39s-180.83-71.823-204.79-198.18 28.885-242.48 118.03-259.39 180.83 71.823 204.79 198.18z" fill="url(#p)" fill-rule="evenodd" opacity=".53"/> <path d="m800.7 579.23c13.422 70.787-18.765 136.34-71.893 146.41s-107.08-39.144-120.5-109.93 18.765-136.34 71.893-146.41 107.08 39.144 120.5 109.93z" fill="url(#q)" fill-rule="evenodd" opacity=".3"/> <path d="m594.67 641.27c-7.5955-29.447-30.637-84.997-39.13-125.99-4.8096-23.214-2.0073-55.665 20.434-45.612 34.022 15.242 7.515 67.678 31.824 5.6665 1.5604-3.9803 9.473 52.616 48.881 25.12 31.294-21.834 6.3642 56.456 3.1625 74.438-1.2454 6.9946 28.267 25.561 45.612 20.434 43.607-12.891-6.8184 34.395-12.478 47.028-13.768 30.731 83.538-10.272 88.497-12.972 46.18-25.14 51.052 9.6701 84.519-13.68 35.135-24.514 69.816-41.744 96.997-60.708 21.533-15.024-9.2324-37.674 27.682-40.217 27.949-1.9251 2.603 50.441-5.9384 56.401-20.828 14.532-41.09-1.762-54.111 27.303-8.1459 18.183-13.624 30.417-17.872 54.276-3.7946 21.311-39.464 41.47-54.383 51.879-21.118 14.734-14.844 26.563-46.155 28.719-21.476 1.4792-39.457 38.045-54.111 27.303-16.953 5.0117-43.834 11.074-55.964 14.66-22.687 6.7067-30.042-29.974-59.399-35.201-22.16-3.9457-38.657-26.384-46.048-41.032-7.1194-14.11-4.7236-42.621-2.0177-57.818z" fill="url(#ay)" fill-rule="evenodd" opacity=".1"/> <path d="m1044.4 433.74c-32.071 180.12-231.72 379.54-340.35 363.1-105.82-15.939-226.17-278.15-194.1-458.26s177.82-304.98 325.32-278.72 241.2 193.76 209.13 373.88z" fill="url(#r)" fill-rule="evenodd"/> <path d="m743.31 789.2c-1.5639 8.6109-22.057 10.858-45.768 5.0187s-41.657-17.553-40.079-26.161c1.5639-8.6109 22.057-10.858 45.768-5.0187s41.657 17.553 40.079 26.161z" fill="url(#s)" fill-rule="evenodd" opacity=".3"/> <path d="m698.96 779.91c-6.8824 1.086-20.88 10.052-26.108 15.387-2.9084 2.9681-10.335 1.1662-14.841 1.4773-8.8656 0.61199-7.7249 8.8192-0.54317 11.811 9.5657 3.985 18.71 7.8099 27.197 13.519 6.4012 4.3057 13.858 6.8672 21.058 9.867 7.3329 3.0548 10.317-1.4178 10.023-5.673-0.26729-3.8722-7.1255-11.385-7.4606-16.24-0.31809-4.6079 5.3038-17.66 2.0188-23.234-0.24178-0.41024-3.9076-8.0885-11.345-6.9149z" fill="url(#az)" fill-rule="evenodd"/> <path d="m698.96 779.91c-6.8824 1.086-20.88 10.052-26.108 15.387-2.9084 2.9681-10.335 1.1662-14.841 1.4773-8.8656 0.61199-7.7249 8.8192-0.54317 11.811 9.5657 3.985 18.71 7.8099 27.197 13.519 6.4012 4.3057 13.858 6.8672 21.058 9.867 7.3329 3.0548 10.317-1.4178 10.023-5.673-0.26729-3.8722-7.1255-11.385-7.4606-16.24-0.31809-4.6079 5.3038-17.66 2.0188-23.234-0.24178-0.41024-3.9076-8.0885-11.345-6.9149z" fill="url(#ba)" fill-rule="evenodd"/> <path d="m698.96 779.91c-6.8824 1.086-20.88 10.052-26.108 15.387-2.9084 2.9681-10.335 1.1662-14.841 1.4773-8.8656 0.61199-7.7249 8.8192-0.54317 11.811 9.5657 3.985 18.71 7.8099 27.197 13.519 6.4012 4.3057 13.858 6.8672 21.058 9.867 7.3329 3.0548 10.317-1.4178 10.023-5.673-0.26729-3.8722-7.1255-11.385-7.4606-16.24-0.31809-4.6079 5.3038-17.66 2.0188-23.234-0.24178-0.41024-3.9076-8.0885-11.345-6.9149z" fill="url(#bb)" fill-rule="evenodd" opacity=".46759"/> <path d="m698.96 779.91c-6.8824 1.086-20.88 10.052-26.108 15.387-2.9084 2.9681-10.335 1.1662-14.841 1.4773-8.8656 0.61199-7.7249 8.8192-0.54317 11.811 9.5657 3.985 18.71 7.8099 27.197 13.519 6.4012 4.3057 13.858 6.8672 21.058 9.867 7.3329 3.0548 10.317-1.4178 10.023-5.673-0.26729-3.8722-7.1255-11.385-7.4606-16.24-0.31809-4.6079 5.3038-17.66 2.0188-23.234-0.24178-0.41024-3.9076-8.0885-11.345-6.9149z" fill="url(#bc)" fill-rule="evenodd" opacity=".50926"/> <path d="m673.94 803.2c2.954 1.7051 10.517 4.0497 15.893 4.9549 4.55 0.76615 7.1671 1.5632 10.659 0.2757 5.0532-1.863 3.7503 0.98943 7.6871 5.2552 1.5018 4.0149 5.8234 4.6822 6.2512 11.38 1.6595 3.6364-10.897-4.5395-14.722-6.1331-4.1097-1.712-7.3658-3.9015-11.18-5.4907-2.6317-1.0963-7.596-4.3005-9.3546-5.563-2.7367-1.9647-0.93683-1.8752-5.2335-4.6792z" fill="url(#t)" fill-rule="evenodd" opacity=".67593"/> <path d="m711.08 794.23c-0.20706 4.7294-2.2885 8.4794-4.6491 8.3761s-4.1063-4.021-3.8993-8.7504 2.2885-8.4794 4.6491-8.3761 4.1063 4.021 3.8993 8.7503z" fill="url(#u)" fill-rule="evenodd" opacity=".46759"/> <path d="m705.36 794.06c-0.32309-0.04566-0.51089-0.40605-0.76633-0.60907 5.9278 4.0546 0.16076-0.09343 1.6914-0.98296-0.18584-0.30454-0.13005 0.05185-0.29899 0.11921l7.3281-7.1554c1.2809 1.8557 2.9379 3.2454 3.1266 5.7026-0.28744 12.814-10.618 18.106-20.172 8.2261-4.8868-10.595 1.9398-18.612 13.077-14.868l-3.9858 9.5676z" fill="url(#v)"/> <path d="m670.98 891.48c5.4655 37.595-49.744 14.957-61.743 47.317-12.124 32.695 22.131 30.655 27.522 65.989l-3.3953 11.681c-10.486-45.495-38.146-45.847-26.038-77.709s59.629-24.526 61.962-41.157l1.693-6.1213z" fill="url(#bd)"/> <path d="m619.74 1033.7c-13.688 8.7079-56.512 6.6035-50.425-7.6177 14.522-33.922 58.376 3.865 47.901 32.183-5.0964 13.778-38.896-1.0468-49.253 8.6333l2.2842-8.2425c8.7543-8.2756 39.817 6.2152 41.386-1.9654 5.3709-27.994-22.403-38.599-35.584-34.706-4.6325 14.461 33.936 14.172 46.221 4.6636l-2.531 7.0509z" fill="url(#be)"/> <path d="m617.74 1033.7c-13.688 8.7079-54.512 6.6035-48.425-7.6177l6.7343-4.0968c-4.6325 14.461 31.936 14.172 44.221 4.6636l-2.531 7.0509z" fill="url(#bf)"/> <path d="m705.36 794.06c-0.32309-0.04566-0.51089-0.40605-0.76633-0.60907 5.9278 4.0546 0.16076-0.09343 1.6914-0.98296-0.18584-0.30454-0.13005 0.05185-0.29899 0.11921l7.3281-7.1554c1.2809 1.8557 2.9379 3.2454 3.1266 5.7026-0.28744 12.814-10.618 18.106-20.172 8.2261-4.8868-10.595 1.9398-18.612 13.077-14.868l-3.9858 9.5676z" fill="url(#bg)"/> <path d="m716.53 788.65c-17.535 16.735-12.546-3.6637-20.714-5.6466-11.754-4.9235-32.085-6.5319-42.357 0.28891-14.083 9.3511-23.149 21.63-23.595 41.898-0.44949 20.401 19.383 35.929 36.387 57.704l-1.2542 3.8196c-11.367-20.233-41.39-33.404-42.47-57.243-1.0951-24.162 6.3633-40.277 31.956-50.283 13.415-4.9665 27.85-7.4825 41.508-2.139l20.54 11.601z" fill="url(#bh)"/> <path d="m716.53 788.65c-17.535 16.735-12.546-3.6637-20.714-5.6466-11.754-4.9235-13.484-11.298 0.17431-5.9545l20.54 11.601z" fill="url(#w)" opacity=".63889"/> <path d="m446.35 827.92 71.38 339.85 9.0567 0.8958-72.506-342.35-7.9305 1.6074z" fill="url(#bm)" fill-rule="evenodd"/> <path d="m586.15 348.33c57.212 173.77-23.94 444.04-127.37 481.1-100.71 36.166-331.05-137.57-388.26-311.34s11.857-352.83 154.17-399.69 304.25 56.152 361.46 229.92z" fill="url(#y)" fill-rule="evenodd" opacity=".75"/> <path d="m586.15 348.33c57.212 173.77-23.94 444.04-127.37 481.1-100.71 36.166-331.05-137.57-388.26-311.34s11.857-352.83 154.17-399.69 304.25 56.152 361.46 229.92z" fill="url(#z)" fill-rule="evenodd"/> <path transform="matrix(1.2202 0 0 1 -135.79 0)" d="m782.11 437.22a131.07 247.1 0 1 1-262.14 0 131.07 247.1 0 1 1 262.14 0z" fill="url(#x)" fill-rule="evenodd" opacity=".15"/> <path d="m179.32 172.45c-12.085 1.3313-34.371 23.294-42.595 35.08-16.91 24.233-26.944 40.528-35.48 65.825-13.106 38.838 8.4362 38.436 34.286 12.776 19.749-19.604-9.2562 36.704-11.022 48.749-2.9496 20.116-21.686 34.073-29.986 45.968-8.6579 12.408-3.9097 33.769-22.771 49.609-20.582 17.285 20.481 21.385 32.433 25.418 19.096 6.444-6.0822 47.372 29.752 17.277 21.131-17.746 13.552-33.057 31.639-4.4007 5.9653 9.451 43.662-41.679 45.342-45.008 1.9628-3.8897-9.4891-56.231-10.622-59.671-0.02298-0.06984 11.096-20.327 27.172-17.97 24.936 3.6564 19.514 26.955 38.854-0.75993 9.8258-14.081 30.706 47.582 31.439 49.809 10.517 31.945 48.063-9.6906 62.352-2.4801 15.262 7.7016 12.946 38.214 30.545 47.096 13.884 7.0063 40.046-34.514 43.522-41.401 11.373-22.538-1.6507-23.463 37.96-3.4738 27.9 14.079 19.118-34.042 57.851-7.0143 23.572 16.448 4.7416-20.65 3.7409-34.32-1.6887-23.068-17.566-55.721-27.731-75.094-5.7524-10.963 45.756 11.634 37.034 2.8474-15.909-16.027-35.727-28.737-50.436-43.555-19.057-19.199-27.75-32.28-42.261-55.271-12.537-19.863-8.4352-24.623-26.078-33.526-18.629-9.4008-31.699 21.183-45.175-0.16694-9.3733-14.85-36.745 13.139-52.423 5.2274-4.4149-2.2279-19.819-30.849-23.364-34.42-7.8018-7.8597-41.975 7.8034-53.35 11.549l-10.855 3.5739c-12.451 4.0992-28.129 6.2529-41.601 10.688-0.97996 0.32263-10.547 20.636-18.17 27.038z" fill="url(#bn)" fill-rule="evenodd" opacity=".6"/> <path d="m354.43 220.08c6.9084 20.983-4.5016 43.594-25.485 50.503s-43.594-4.5016-50.503-25.485 4.5016-43.594 25.485-50.503 43.594 4.5016 50.503 25.485z" fill="url(#aa)" fill-rule="evenodd"/> <path d="m424.99 196.85c19.738 59.953-12.862 124.55-72.814 144.29s-124.55-12.862-144.29-72.814 12.862-124.55 72.814-144.29 124.55 12.862 144.29 72.814z" fill="url(#ab)" fill-rule="evenodd" opacity=".6"/> <path d="m224.7 118.42c-142.31 46.854-211.4 225.9-154.19 399.67s287.56 347.52 388.28 311.35c103.43-37.059 184.58-307.34 127.37-481.12s-219.15-276.76-361.46-229.9zm-4.686 5.8527c5.0148-2.1127 10.745-3.5148 17.338-3.9975 19.323-1.4146 35.137 23.137 40.552 22.741 20.432-1.4957 28.649-22.274 43.469-23.359 18.537-1.357 21.95 6.5721 34.283 12.796 11.454 5.7802 26.177 17.714 41.47 25.432 12.527 6.3217 34.938 20.632 49.613 22.784 13.777 2.0201 32.638 7.7975 36.961 20.929 9.1348 27.746-12.253 22.705-11.007 39.715 1.7109 23.371 43.087 12.055 52.268 39.939 9.4914 28.829-26.557 44.184-17.352 47.825 0.1859 0.07354 77.955 54.048 36.847 57.058-23.013 1.6847-70.872-27.598-75.008 0.61222-1.5032 10.251-19.632 63.679-39.916 43.245-43.436-43.758-16.268 9.5048-67.811 13.278-16.975 1.2427-16.57-17.487-17.941-36.205-5.7181-78.109-55.479-5.9875-58.612-31.83-9.4534-77.967 5.5369-10.748-21.531-38.017-16.307-16.428-29.142-34.047-54.146-18.265-38.555 24.335-3.4441 29.967 0.70873 56.914 3.8615 25.057-29.434 24.763-13.708 40.605 5.2796 5.3188 36.015 49.856 26.949 45.281l-10.85-5.4753c-38.888-19.624-32.519 47.093-65.047 3.3864-25.289-33.979-18.825 22.841-46.247 42.303-7.7904 34.455-14.325 11.251-19.843-5.5085-4.9852-15.142-3.3345-28.415-8.8652-45.214-9.022-27.403 13.603-22.494 24.543-44.172 6.3652-12.614 33.053-33.898 5.5754-37.927-14.432-2.1161-36.676 10.229-20.762-8.1999 10.232-11.848 54.455-56.078 30.094-73.076-13.718-9.5719-53.552-36.522-13.384-49.747 35.853-11.804 44.862-13.576 42.627-44.105-1.8199-24.859 36.809-14.624 48.035-36.871 6.9471-13.767 15.653-26.535 30.697-32.873z" fill="url(#bo)" fill-rule="evenodd" opacity=".4"/> <path d="m442.64 489.2c81.03 99.865 89.602 227.17 19.145 284.33s-193.26 22.557-274.29-77.308-89.602-227.17-19.145-284.33 193.26-22.557 274.29 77.308z" fill="url(#ac)" fill-rule="evenodd" opacity=".53"/> <path d="m440.6 592.04c45.396 55.948 48.157 128.92 6.1664 162.99s-112.83 16.337-158.23-39.611-48.157-128.92-6.1664-162.99 112.83-16.337 158.23 39.611z" fill="url(#ad)" fill-rule="evenodd" opacity=".3"/> <path d="m288.67 744.39c-20.656-22.32-67.291-60.291-94.213-92.347-15.246-18.154-28.174-48.051-3.6491-49.846 37.181-2.7219 38.721 56.013 30.704-10.109-0.51461-4.2442 33.299 41.825 54.948-1.0747 17.191-34.066 32.385 46.68 38.096 64.029 2.2218 6.7483 37.01 9.0928 49.846-3.6491 32.273-32.035 10.314 33.513 11.325 47.319 2.4586 33.584 68.667-48.672 71.752-53.401 28.727-44.038 49.53-15.706 67.914-52.137 19.301-38.248 41.658-69.868 56.589-99.456 11.829-23.441-26-28.786 5.2904-48.535 23.691-14.953 26.22 43.17 21.528 52.468-11.441 22.673-37.009 17.942-34.683 49.705 1.4547 19.871 2.4356 33.239 10.014 56.259 6.7693 20.561-15.068 55.228-23.264 71.469-11.601 22.988-0.46685 30.425-27.007 47.177-18.204 11.49-16.687 52.209-34.683 49.705-12.546 12.454-33.335 30.543-42.312 39.454-16.79 16.666-40.666-12.135-68.989-2.8104-21.38 7.0389-46.546-4.8879-60.002-14.277-12.961-9.044-24.377-35.279-29.204-49.941z" fill="url(#bp)" fill-rule="evenodd" opacity=".1"/> <path d="m586.15 348.33c57.212 173.77-23.94 444.04-127.37 481.1-100.71 36.166-331.05-137.57-388.26-311.34s11.857-352.83 154.17-399.69 304.25 56.152 361.46 229.92z" fill="url(#ae)" fill-rule="evenodd"/> <path d="m489.69 804.11c2.7082 8.3222-14.266 20.022-37.91 26.13s-44.998 4.309-47.692-4.0168c-2.7082-8.3222 14.266-20.022 37.91-26.13s44.998-4.309 47.692 4.0168z" fill="url(#af)" fill-rule="evenodd" opacity=".3"/> <path d="m446.24 816.97c-5.5435 4.2209-13.612 18.754-15.684 25.931-1.1523 3.9925-8.5448 5.9294-12.364 8.341-7.5142 4.7444-2.6167 11.428 5.1248 10.655 10.311-1.0298 20.176-2.0005 30.355-1.0012 7.6777 0.75372 15.457-0.52845 23.219-1.3036 7.9045-0.7894 8.4098-6.1424 6.1326-9.749-2.0722-3.2819-11.673-6.642-14.272-10.757-2.466-3.9056-3.7086-18.062-9.2445-21.411-0.40746-0.24644-7.277-5.2668-13.268-0.70533z" fill="url(#bq)" fill-rule="evenodd"/> <path d="m446.24 816.97c-5.5435 4.2209-13.612 18.754-15.684 25.931-1.1523 3.9925-8.5448 5.9294-12.364 8.341-7.5142 4.7444-2.6167 11.428 5.1248 10.655 10.311-1.0298 20.176-2.0005 30.355-1.0012 7.6777 0.75372 15.457-0.52845 23.219-1.3036 7.9045-0.7894 8.4098-6.1424 6.1326-9.749-2.0722-3.2819-11.673-6.642-14.272-10.757-2.466-3.9056-3.7086-18.062-9.2445-21.411-0.40746-0.24644-7.277-5.2668-13.268-0.70533z" fill="url(#br)" fill-rule="evenodd"/> <path d="m446.24 816.97c-5.5435 4.2209-13.612 18.754-15.684 25.931-1.1523 3.9925-8.5448 5.9294-12.364 8.341-7.5142 4.7444-2.6167 11.428 5.1248 10.655 10.311-1.0298 20.176-2.0005 30.355-1.0012 7.6777 0.75372 15.457-0.52845 23.219-1.3036 7.9045-0.7894 8.4098-6.1424 6.1326-9.749-2.0722-3.2819-11.673-6.642-14.272-10.757-2.466-3.9056-3.7086-18.062-9.2445-21.411-0.40746-0.24644-7.277-5.2668-13.268-0.70533z" fill="url(#bs)" fill-rule="evenodd" opacity=".46759"/> <path d="m446.24 816.97c-5.5435 4.2209-13.612 18.754-15.684 25.931-1.1523 3.9925-8.5448 5.9294-12.364 8.341-7.5142 4.7444-2.6167 11.428 5.1248 10.655 10.311-1.0298 20.176-2.0005 30.355-1.0012 7.6777 0.75372 15.457-0.52845 23.219-1.3036 7.9045-0.7894 8.4098-6.1424 6.1326-9.749-2.0722-3.2819-11.673-6.642-14.272-10.757-2.466-3.9056-3.7086-18.062-9.2445-21.411-0.40746-0.24644-7.277-5.2668-13.268-0.70533z" fill="url(#bt)" fill-rule="evenodd" opacity=".50926"/> <path d="m435.26 849.34c3.4094 0.0997 11.179-1.4241 16.341-3.1775 4.3689-1.484 7.0509-2.0238 9.5144-4.814 3.5647-4.0372 3.7708-0.90807 9.2601 0.97965 3.2267 2.822 7.3476 1.3593 10.902 7.0526 3.1859 2.4139-11.746 1.173-15.87 1.5848-4.43 0.44241-8.335 0.05964-12.447 0.47029-2.8368 0.28331-8.7269-0.1824-10.874-0.45953-3.3412-0.43128-1.7143-1.2064-6.8269-1.6365z" fill="url(#ag)" fill-rule="evenodd" opacity=".67593"/> <path d="m443.7 823.82c2.0613 4.2616 2.0079 8.5502-0.11917 9.5791s-5.5224-1.5918-7.5836-5.8533-2.0079-8.5502 0.11918-9.5791 5.5224 1.5918 7.5836 5.8533z" fill="url(#ah)" fill-rule="evenodd" opacity=".46759"/> <path d="m438.59 826.38c-0.30608 0.11307-0.64237-0.1151-0.96355-0.17265 7.1418 0.75729 0.0972-0.1585 1.0227-1.6677-0.30807-0.17992-0.08989 0.10735-0.20665 0.24678l3.0566-9.7754c2.0079 1.026 4.1259 1.4634 5.4576 3.537 5.8255 11.416-0.75823 20.976-13.855 16.811-9.328-7.0086-7.1217-17.305 4.4586-19.292l1.03 10.313z" fill="url(#ai)"/> <path d="m464.55 908.06c-9.4404 36.799 49.867 38.173 58.35 71.627 8.5707 33.8-28.511 2.1226-37.637 36.68l2.1313 11.976c15.274-44.119 46.055-15.522 37.41-48.492s-58.676-48.74-59.223-65.525l-1.0311-6.2669z" fill="url(#bu)"/> <g transform="matrix(-.99601 .089248 .089248 .99601 894.77 -68.925)"> <path d="m491.89 1079.2c-7.9185 14.159-41.628 31.384-43.015 15.977-3.3086-36.751 53.223-24.29 57.435 5.6083 2.0494 14.546-34.737 17.53-39.263 30.965l-1.8992-8.3395c3.7807-11.438 38-13.417 35.501-21.363-8.5518-27.192-38.033-23.352-47.789-13.672 2.7822 14.928 33.601-2.5629 39.906-16.762l-0.87527 7.5863z" fill="url(#bl)"/> <path d="m489.62 1079.4c-7.9185 14.159-39.358 31.18-40.745 15.773l3.9849-6.8011c2.7822 14.928 31.331-2.3595 37.636-16.558l-0.87527 7.5863z" fill="url(#bk)"/> </g> <path d="m438.59 826.38c-0.30608 0.11307-0.64237-0.1151-0.96355-0.17265 7.1418 0.75729 0.0972-0.1585 1.0227-1.6677-0.30807-0.17992-0.08989 0.10735-0.20665 0.24678l3.0566-9.7754c2.0079 1.026 4.1259 1.4634 5.4576 3.537 5.8255 11.416-0.75823 20.976-13.855 16.811-9.328-7.0086-7.1217-17.305 4.4586-19.292l1.03 10.313z" fill="url(#bv)"/> <path d="m430.14 819.06c16.075 18.141 12.808-2.6027 21.113-3.896 12.124-3.9242 32.518-3.8281 42.185 3.8271 13.253 10.495 21.261 23.488 20.012 43.723-1.2567 20.367-26.318 14.183-45.082 34.462l0.93068 3.911c13.018-19.213 48.036-9.8287 51.105-33.494 3.1102-23.986-2.9757-40.668-27.643-52.777-12.953-6.07-27.128-9.7834-41.185-5.5998l-21.437 9.8443z" fill="url(#bw)"/> <path d="m445.85 816.33c-7.4974 23.05-12.782 2.7261-20.914 4.8556-12.683 1.2416-17.23-3.5493-2.6713-5.3245l23.585 0.4689z" fill="url(#aj)" opacity=".63889"/> <path transform="matrix(.98588 -.16181 .16746 .95261 -68.149 66.993)" d="m584.44 473.75a96.69 257.84 0 1 1-193.38 0 96.69 257.84 0 1 1 193.38 0z" fill="url(#bj)" fill-rule="evenodd" opacity=".15"/> <path d="m653.71 683.68c-2.3007 3.2637-1.8444 6.0549-0.16423 11.604 0.93475 3.0871-3.808 4.5847-5.6184 6.4494-3.5618 3.6684 3.1939 8.8365 8.7298 8.2387 7.3736-0.79623 14.434-1.5468 22.628-0.7741 6.1799 0.58278 11.514-0.40861 17.064-1.008 5.6524-0.61038 3.6087-4.7494 0.24127-7.5381-3.0643-2.5376-11.889-5.1357-15.731-8.3173-3.6466-3.0198-11.013-9.9661-16.741-12.555 0.65272 4.1068-7.9223 0.37365-10.409 3.9006z" fill="url(#bi)" fill-rule="evenodd" opacity=".15"/> <path d="m650.41 689.82c-6.113 15.956 4.0377 47.01 12.005 65.761 7.3191 15.227 15.94 29.876 27.587 42.183l-6.7716 6.1009c-11.662-13.528-20.585-29.018-28.232-45.127-7.2436-16.986-32.176-69.766-3.2666-78.734l-1.3221 9.8162z" fill="url(#as)" opacity=".1"/> <path d="m527.98 684.22c-2.2923 1.8259-5.071 8.8442-5.5551 12.437-0.26929 1.9988-3.5718 2.5146-5.1842 3.5145-3.1722 1.9671-0.4545 5.7665 3.0874 5.8788 4.7176 0.1495 9.2316 0.29999 14.023 1.4955 3.6138 0.90165 7.1393 0.75178 10.691 0.86432 3.6164 0.11461 3.495-2.6343 2.1981-4.6602-1.1801-1.8435-5.8601-4.2277-7.3397-6.539-1.4044-2.1938-2.9227-9.6349-5.7149-11.743-0.20551-0.15516-3.728-3.2209-6.2053-1.2477z" fill="url(#au)" fill-rule="evenodd" opacity=".15"/> <path d="m520.4 692.48c-14.908 8.3495-26.979 38.709-32.855 58.217-4.119 16.384-6.8686 33.159-5.7929 50.069l-9.1076 0.35515c-0.30527-17.858 2.7493-35.472 7.1814-52.744 5.3031-17.689 19.917-74.201 47.871-62.595l-7.2974 6.6974z" fill="url(#at)" opacity=".15"/> 
        </svg>
    </div>
</body>
</html>
"""
    return html_code

def generate_section_header_slide_9(
    main_title="Main Title Here",
    subtitle="Here you could describe the topic of the section",
    bg_gradient_from="#fef5e7",
    bg_gradient_to="#d4a574",
    text_color="#ffffff",
    custom_css=""
):
    """
    Generate a modern section header slide with house SVG illustration on the left and text on the right.
    
    Parameters:
    - main_title: Main title text displayed prominently on the right side
    - subtitle: Subtitle text below the main title
    - bg_gradient_from: Starting gradient color (default: light cream #fef5e7)
    - bg_gradient_to: Ending gradient color (default: warm brown #d4a574)
    - text_color: Color of all text elements (default: white)
    - custom_css: Additional CSS to inject
    
    Returns:
    - HTML string containing the complete slide with SVG container on left, text on right
    """
    
    if isinstance(main_title, list):
        main_title = main_title[0]
    if isinstance(subtitle, list):
        subtitle = subtitle[0]
    
    html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700;900&family=Roboto:wght@300;400&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            margin: 0;
            padding: 0 120px;
            font-family: 'Roboto', sans-serif;
            overflow: hidden;
            width: 1920px;
            height: 1080px;
            background: linear-gradient(135deg, {bg_gradient_from} 0%, {bg_gradient_to} 100%);
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        /* SVG Container - Left side */
        .svg-container {{
            position: relative;
            width: 50%;
            height: 95%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 5;
            filter: drop-shadow(0 10px 30px rgba(0, 0, 0, 0.3));
        }}
        
        .svg-container svg {{
            width: 100%;
            height: auto;
            max-height: 100%;
            opacity: 0.95;
            filter: brightness(1.1) saturate(0.9);
        }}
        
        /* Content area - Right side */
        .content {{
            position: relative;
            z-index: 10;
            text-align: right;
            max-width: 50%;
        }}
        
        .main-title {{
            font-family: 'Roboto Condensed', sans-serif;
            font-size: 4rem;
            font-weight: 900;
            color: {text_color};
            margin-bottom: 30px;
            line-height: 1.1;
            letter-spacing: 2px;
        }}
        
        .subtitle {{
            font-family: 'Roboto', sans-serif;
            font-size: 2rem;
            font-weight: 300;
            color: {text_color};
            opacity: 0.9;
            line-height: 1.6;
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <!-- SVG Container - Left side (paste your SVG here) -->
    <div class="svg-container">
        <!-- Paste your SVG code here -->
  <svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 1696.48 1415.91" version="1.1" viewBox="0 0 1696.5 1415.9">
    <style type="text/css">
      .st0{{fill-rule:evenodd;clip-rule:evenodd;fill:#B39E63;}} .st1{{fill:#A16837;}} .st2{{fill-rule:evenodd;clip-rule:evenodd;fill:#ECD8B3;}} .st3{{fill-rule:evenodd;clip-rule:evenodd;fill:#E8CD9F;}} .st4{{fill-rule:evenodd;clip-rule:evenodd;fill:#D3A364;}} .st5{{fill-rule:evenodd;clip-rule:evenodd;fill:#BE8450;}} .st6{{fill-rule:evenodd;clip-rule:evenodd;fill:#B17D42;}} .st7{{fill:#B17D42;}} .st8{{fill-rule:evenodd;clip-rule:evenodd;fill:#E2C28F;}} .st9{{fill-rule:evenodd;clip-rule:evenodd;fill:#D2C08D;}} .st10{{fill-rule:evenodd;clip-rule:evenodd;fill:#9A864D;}} .st11{{fill-rule:evenodd;clip-rule:evenodd;fill:#D1C0A1;}} .st12{{fill-rule:evenodd;clip-rule:evenodd;fill:#A16837;}}
    </style>
    <path class="st0" d="m1347.2 751.6c33.01 35.73 110.52 0.6 109.92-50.87 69.64-7.87 94.78-109.31 45.42-143.53 67.22-61.47 13.62-154.73-54.5-151.7 3.63-112.34-157.15-154.73-185.31-15.44-59.95-12.11-106.28 102.04-43.6 129.9-30.65 24.21-37.83 92.97 5.45 106.28-26.88 66.4 70.31 152 122.62 125.36"/>
    <path class="st1" d="m1289.8 509.6c-9.83-12.07-0.05-16.88 7.06-8.82 16.87 19.11 31.41 45.09 46.82 61.75 2.12-63.14 3.74-110.09 3.72-116.71-0.07-17.56 11.93-15.65 11.9-4.91-0.03 10.69-0.89 80.98-1.75 166.32 17.4-27.81 40.85-81.48 56.81-99.57 7.11-8.05 13.64-0.74 5.09 12.27-16.94 25.79-41.18 86.06-62.19 116.61-0.21 21.83-0.41 44.26-0.6 66.65 17.71-19.19 52.36-63.45 72.46-82.84 7.73-7.46 17.73-2.51 7.06 8.82-18.9 20.08-55.56 70.13-79.69 95.04-0.88 112.94-1.19 218.93 0.69 229.95-4.11 6.16-17.78 2.43-21.9 8.59-2.82-18.47 0.28-143.51 4.05-266.06-21.41-23.58-46.76-60.2-64.3-78.84-10.67-11.34-0.67-16.28 7.06-8.82 18.56 17.9 41.57 48.68 57.87 67.3 1.02-32.52 2.07-64.41 3.04-93.65-19.01-20.44-34.98-50.71-53.2-73.08"/>
    <path class="st0" d="m181 1033.7c-23.13-27.69 3.95-73.86 38.97-69.28-15.73-31.45 15.38-72.79 66.03-51.96-1.97-60.58 59.56-80.61 102.83-54.12 20.76-51.52 97.51-52.58 127.73 5.41 220.1 5.05 440.19 10.1 660.29 15.15 43.43-69.86 118.49-62.8 116.9-2.16 36.47-38.29 106.97-6.79 92.01 44.38 35.97-14.04 78.97 5.91 71.44 50.87 39.84-0.44 52.66 33.9 27.06 74.69-434.42-4.32-868.84-8.65-1303.3-12.98"/>
    <polygon class="st2" points="471.34 657.86 462.06 998.51 1216.3 1034.3 1214.9 640.63 707.28 307.94"/>
    <polygon class="st3" points="909.83 1019.8 1216.3 1034.3 1214.9 640.63 907.61 439.22"/>
    <path class="st4" d="m572.09 984.69 3.96-158.49c0-102.17 51.87-144.08 112.66-143.16 55.14 0.83 98.09 54.12 98.09 131.23l-3.81 181.15c-70.21-4.91-140.54-8.71-210.9-10.73"/>
    <path class="st1" d="m707.06 990.57 1.36-105.53-8.86-0.74-0.72 105.81c2.74 0.15 5.48 0.31 8.22 0.46m-5.41-131.39c-5.58-5.75-7.68-18.71-5.27-26.35 2.11-6.68 10.17-11.97 17.12-11.2 7.29 0.81 12.54 9.9 13.83 17.12 1.23 6.91-1.75 15.4-7.25 19.76-4.81 3.84-14.15 5.08-18.43 0.67zm-95.95 126.61-0.87-158.88c0-50.93 27.89-103.59 78.38-104.72 38.09-0.86 69.81 48.3 69.81 89.58l-1.78 181.53c-3.61-0.23-7.23-0.47-10.84-0.7 0.7-56.26 1.39-108.65 2.09-167.66 0-19.19-8.96-60.14-32.27-79.57l-0.74 57.61-9.39 3.67 0.46-67.6c-5.39-2.63-11.37-4.2-17.99-4.35-6.26-0.14-12.21 1.09-17.78 3.43v250.2c-3.14-0.16-6.28-0.31-9.43-0.45l2.55-246.2c-24.74 15.24-40.55 52.83-40.55 86.56l-2.6 157.9 5.07 0.2c-4.71-0.21-9.41-0.38-14.12-0.55z"/>
    <path class="st5" d="m664.77 738.12c5.58-2.34 11.52-3.57 17.78-3.43 6.62 0.14 12.6 1.71 17.99 4.35l-0.46 67.6 9.39-3.67 0.74-57.61c23.31 19.44 32.27 60.38 32.27 79.57-0.69 59.01-1.39 111.39-2.09 167.66-11.11-0.7-22.22-1.37-33.34-2.01l1.36-105.53-8.86-0.74-0.72 105.81c-11.35-0.63-22.71-1.23-34.07-1.79v-250.21zm-50.02 248 2.6-157.9c0-33.73 15.8-71.32 40.55-86.56l-2.55 246.2c-13.54-0.63-27.07-1.21-40.6-1.74zm86.9-126.94c-5.58-5.75-7.68-18.71-5.27-26.35 2.11-6.68 10.17-11.97 17.12-11.2 7.29 0.81 12.54 9.9 13.83 17.12 1.23 6.91-1.75 15.4-7.25 19.76-4.81 3.84-14.15 5.08-18.43 0.67z"/>
    <path class="st5" d="m1012.4 396.16c2.26-25.58 4.51-51.16 6.77-76.73-2.96-0.13-5.02-0.73-8.87-1.55-8.49-1.8-7.83-5.94-7.5-10.56l1.62-22.12c0.55-7.47 4.33-11.01 13.68-11.01 33.38-1.47 65.68-0.76 97.03 1.85 8.59 0 13.03 7.1 12.75 12.07l-1.41 24.4c-0.27 4.68-1.75 6.2-11.24 6.52 1.56 63.86 3.12 127.72 4.68 191.58-35.84-38.15-71.68-76.3-107.51-114.45"/>
    <path class="st6" d="m404.12 686.74c16.69 19.2 54.72 24.73 75.13 15.03 52.24-24.84 122.12-168.08 194.5-247.09 13.53-14.77 33.72-25.14 50.92 1.67 50.68 78.99 93.67 156.49 153.6 228.72 14.55 17.53 43.17 36.46 65.95 35.89 92.89-2.29 187.98 7.88 280.48 7.51 23.43-0.09 52.59-18.92 42.57-55.93-107.96-7.79-215.92-15.58-323.89-23.37-62.9-86.25-125.78-172.51-188.67-258.77-42.02 2.5-84.03 5.01-126.05 7.51-74.84 96.28-149.69 192.56-224.54 288.83"/>
    <path class="st4" d="m1219.7 690.08c-32.56 6.92-64.28 12.84-97.67-8.35-41.53 22.88-78.68 16.64-113.53-5.01-47.86 26.99-80.1 13.96-103.51-11.69-61.81-67.71-101.88-157.01-154.43-230.39-29.85-41.67-79.16-39.84-107.68-5.84-61.43 73.21-115.21 176.19-181.14 250.43-15.93 17.93-60.26 26.48-71.79-5.84-7.24-20.3-0.51-45.44 12.52-62.61 80.04-105.5 156.42-209.51 251.26-318.88 28.81-33.22 67.63-29.52 101.12-25.12 68.25 8.97 113.49 15.55 166.84 29.29 28.34 7.3 51.09 21.88 71.79 42.57 91.03 91.03 181.39 188.06 260.44 289.66 12.77 16.41 26.77 42.75 16.7 60.94-8.23 14.86-23.09 15.31-50.92 0.84"/>
    <path class="st2" d="m1012.1 907.27c0.76-30.57 1.52-50.57 2.29-81.14 0-30.38 29.67-49.8 57.14-50.28 21.27-0.38 51.71 21.81 51.71 48 1.05 32.76 2.09 54.95 3.14 87.71-38.09-1.44-76.18-2.87-114.28-4.29"/>
    <path class="st7" d="m486.81 542.28c1.41-1.81 4.01-2.14 5.82-0.73s2.13 4.01 0.73 5.82c-7.3 9.38-13.63 18.05-19.06 26.05-5.52 8.13-10.25 15.71-14.25 22.8-1.12 1.99-3.64 2.69-5.63 1.57s-2.69-3.64-1.57-5.63c4.13-7.31 8.97-15.09 14.61-23.38 5.71-8.41 12.14-17.23 19.35-26.5m127-123.36c1.49-1.74 4.1-1.94 5.84-0.45s1.94 4.1 0.45 5.84c-8.08 9.45-15.92 18.95-23.52 28.49-7.64 9.58-14.95 19.07-21.95 28.49-1.36 1.83-3.95 2.22-5.79 0.86s-2.22-3.95-0.86-5.79c7.18-9.65 14.55-19.23 22.11-28.71 7.6-9.55 15.5-19.12 23.72-28.73zm64.48-110.35c1.3-1.88 3.88-2.35 5.76-1.05s2.35 3.87 1.05 5.75l-32.08 46.23c-1.3 1.88-3.87 2.35-5.75 1.06-1.88-1.3-2.35-3.88-1.05-5.76l32.07-46.23zm480.87 270.98c-1.65-1.58-1.7-4.21-0.11-5.85 1.58-1.65 4.2-1.7 5.85-0.11 12.06 11.66 20.94 21.04 27.91 29.05 6.97 8 12.14 14.77 16.7 21.11 1.33 1.85 0.91 4.44-0.94 5.77s-4.44 0.91-5.77-0.94c-4.34-6.03-9.33-12.55-16.24-20.49-6.92-7.95-15.65-17.17-27.4-28.54zm-109.19-6.5c-1.6-1.63-1.58-4.25 0.05-5.85s4.25-1.58 5.85 0.05c8.42 8.52 15.72 17.08 21.98 25.68 6.28 8.63 11.46 17.24 15.6 25.83 0.99 2.06 0.13 4.54-1.93 5.53s-4.53 0.13-5.53-1.93c-3.95-8.21-8.88-16.4-14.82-24.57-5.98-8.21-13.02-16.46-21.2-24.74zm-79.47-17.16c-1.22-1.93-0.64-4.49 1.3-5.71 1.93-1.22 4.49-0.64 5.71 1.3l33.59 53.16c1.22 1.93 0.64 4.49-1.3 5.71-1.93 1.22-4.49 0.64-5.71-1.3l-33.59-53.16zm-66.18 7.18c-1.41-1.81-1.08-4.41 0.73-5.82s4.41-1.08 5.82 0.73c8.23 10.6 15.7 21.23 22.11 31.87 6.42 10.67 11.78 21.39 15.78 32.16 0.8 2.14-0.29 4.52-2.43 5.32s-4.52-0.29-5.32-2.43c-3.79-10.2-8.93-20.46-15.13-30.77-6.22-10.33-13.51-20.69-21.56-31.06zm-82.43-138.8c-1.47-1.75-1.24-4.37 0.52-5.84 1.75-1.47 4.37-1.24 5.84 0.52 9.71 11.63 18.71 23.27 26.66 34.94 7.96 11.69 14.87 23.43 20.36 35.2 0.97 2.07 0.07 4.53-1.99 5.5-2.07 0.97-4.53 0.07-5.5-1.99-5.27-11.3-11.96-22.65-19.72-34.03-7.76-11.41-16.6-22.85-26.17-34.3zm60.8 8.49c-1.34-1.85-0.93-4.44 0.93-5.79 1.85-1.34 4.44-0.93 5.79 0.93l30.84 42.61c1.34 1.85 0.93 4.45-0.92 5.79s-4.45 0.93-5.79-0.92l-30.85-42.62zm71.31 5.17c-1.16-1.97-0.51-4.51 1.46-5.67s4.51-0.51 5.67 1.46c2.2 3.69 4.34 7.71 6.48 11.72 4.05 7.6 8.11 15.21 13.4 21.79 6.14 7.63 13.55 14.26 20.97 20.88 3.86 3.45 7.72 6.9 11.31 10.38 1.64 1.59 1.67 4.21 0.08 5.85s-4.21 1.67-5.85 0.08c-3.66-3.55-7.36-6.86-11.05-10.16-7.69-6.88-15.39-13.76-21.91-21.86-5.75-7.14-10-15.11-14.24-23.08-2.02-3.76-4.03-7.53-6.32-11.39zm73.24 7.38c-1.44-1.77-1.17-4.38 0.6-5.82s4.38-1.17 5.82 0.6l39.08 48.21c1.44 1.77 1.17 4.38-0.6 5.82s-4.38 1.17-5.82-0.6l-39.08-48.21zm-76.29-100.2c-1.3-1.88-0.83-4.46 1.05-5.76s4.46-0.83 5.76 1.05l21.09 30.53c1.3 1.88 0.83 4.46-1.05 5.76s-4.46 0.83-5.76-1.05l-21.09-30.53zm-51.73-6.5c-1.3-1.88-0.83-4.46 1.05-5.76s4.46-0.83 5.76 1.05l28.41 41.11c1.3 1.88 0.83 4.46-1.05 5.76s-4.46 0.83-5.76-1.05l-28.41-41.11zm-83.63-13.54c-1.31-1.87-0.86-4.46 1.01-5.77s4.46-0.86 5.77 1.01c6.74 9.59 13.01 18.58 18.74 26.86 5.47 7.92 10.17 14.8 13.98 20.5 1.27 1.9 0.76 4.47-1.14 5.74s-4.47 0.76-5.74-1.14c-3.75-5.62-8.43-12.47-13.91-20.4-5.23-7.57-11.51-16.57-18.71-26.8zm-73.79-25.48c-1.43-1.78-1.15-4.39 0.63-5.82s4.39-1.15 5.82 0.63c9.82 12.23 17.31 22.66 23.45 32.54 6.18 9.95 11 19.35 15.47 29.47 0.92 2.1-0.03 4.54-2.12 5.46s-4.54-0.03-5.46-2.12c-4.32-9.79-8.97-18.86-14.91-28.43-6-9.63-13.3-19.8-22.88-31.73z"/>
    <path class="st1" d="m1024.5 319.32c-4.79 0.1-3.98-0.33-4.26-2.61s-1.53-5.56 3.26-5.66l83.66-0.33c4.79-0.1 8.91 1.67 9.18 3.95 0.28 2.28-10.09 4.22-14.88 4.32l-76.96 0.33zm91.87 45.74 0.2 8.28-49.43 1.97c-3.34 0.13-6.2-1.61-6.4-3.89-0.19-2.28 2.36-4.24 5.7-4.37l49.93-1.99zm-27.17-90.73-1.88 27.91c-0.22 3.23-3.3 4.39-6.89 2.6s-6.32-5.87-6.1-9.1l1.48-21.95c4.48 0.14 8.94 0.32 13.39 0.54z"/>
    <path class="st8" d="m835.66 776.7c5.24 2.19 17.6 3.23 25.07 2.49 6.54-0.65 12.05-3.53 11.68-6.13-0.4-2.72-8.87-4.86-15.75-5.48-6.58-0.6-14.91 0.34-19.4 2.29-3.93 1.71-5.62 5.15-1.6 6.83m-75.04-134.06c4.11 2.19 13.8 3.23 19.67 2.49 5.13-0.65 9.46-3.53 9.16-6.13-0.31-2.72-6.96-4.86-12.36-5.48-5.16-0.6-11.7 0.34-15.22 2.29-3.08 1.71-4.41 5.15-1.25 6.83zm-25.96-51.05c5.23-2.19 17.6-3.23 25.07-2.49 6.54 0.65 12.05 3.53 11.68 6.13-0.39 2.72-8.87 4.86-15.75 5.48-6.58 0.6-14.91-0.34-19.39-2.29-3.94-1.71-5.62-5.15-1.61-6.83zm-229.24 160.5c5.43-2.19 18.26-3.23 26.02-2.49 6.78 0.65 12.51 3.53 12.12 6.13-0.41 2.72-9.2 4.86-16.34 5.48-6.83 0.6-15.47-0.34-20.13-2.29-4.09-1.7-5.84-5.15-1.67-6.83z"/>
    <path class="st9" d="m40.27 1031c-43.33 11.7-64.7 34.99 3.92 49.66 36.03 7.7 143.23 0.17 118.3 27.3-51.3 55.82 240.96 94.57 259.34 107.29 9.18 6.35 1.39 7.71-32.31 17.45-49.4 14.28 15.83 27.65 31 30.54 73.35 13.97 117.23 9.89 182.94 27.8 12.25 3.34 48.84 25.71 20.55 37.41-46.93 19.41-37.81 34.64 51.32 54.06 217.37 47.36 555.58 48.44 702.59-23.75 53.73-26.38 77.29-56.75 5.65-88.63-10.32-4.59-27.7-20.46 15.68-30.05 15.04-3.32 55.03-7.8 60.44-22.21 5.14-13.71-78.36-24.26-36.91-40.51 76.44-29.97 160.82-45.23 239-70.33 64.73-20.78 24.82-42.67-6.53-52.27-353.38-108.17-577.03-38-855.77-58.19-152.16-11.02-304.9-17.07-457.35-11.3-101.7 3.84-203.61 19.19-301.86 45.73"/>
    <path class="st10" d="m446.81 987.14c-35.71-39.78 1.88-90.16 16.77-36.03-1.4-74.05 52.5-53.09 33.55 0.62 24.95-28.46 66.29-1.65 16.15 36.03-22.15-0.21-44.31-0.42-66.47-0.62"/>
    <path class="st10" d="m826.41 1001.4c-39.14-37.9 2.48-64.61 18.64-42.87-14.68-74.78 41.98-59.09 41.63-28.58 22.47-29.24 62.3-12.8 39.76 30.44 41.18-38.26 53.27 14.96 26.71 41.63-42.25-0.21-84.49-0.42-126.74-0.62"/>
    <path class="st10" d="m398.85 1198.5c-9-14.27 6.24-20.09 15.34-6.57 8.47 12.58 13.66 31.88 18.41 50.84 3.71 14.83-7.59 18.24-10.52 6.57-4.54-18.07-13.3-35.08-23.23-50.84m44.26-9.2c4.03-15.13 15.78-17.62 14.02 2.63-1.67 19.35-3.53 38.74-7.01 57.85-2.12 11.62-13.98 10.77-14.02-1.31-0.08-22.81 2.87-43.64 7.01-59.17zm29.37 22.79c14.65-10.36 18.41 1.02 9.19 11.84-7.46 8.75-9.42 17.7-14.46 28.04-6.55 13.45-15.89 11.17-13.15-0.44 3.28-13.83 6.81-31.24 18.42-39.44zm-104.75-114.82c-4.1 9.76 1.15 15.64 7.45 3.94 7.36-13.65 15.97-26.61 23.23-40.32 5.82-10.99-3.39-16.2-9.2-8.33-9.82 13.31-15.08 29.47-21.48 44.71zm-12.27 3.5c-1.61 12.61-12.23 13.7-13.15-6.13-0.98-21.3 5.1-42.48 10.52-63.11 2.62-9.98 11.91-7.35 10.52 3.51-2.82 21.88-5.1 43.84-7.89 65.73zm-27.17 10.08c3.63 14.22 13.08 12.03 12.13-0.88-1.65-22.42-5.24-45.56-13.45-66.62-3.92-10.06-17.68-12.59-15.34-0.88 4.49 22.4 9.19 39.16 16.66 68.38zm583.38-58.28c-8.07-11.04-15.94-7.66-10.67 4.13 4.06 9.09 8.44 18.09 13.77 26.5 4.16 6.56 11.98 4.46 9.29-6.2-2.24-8.85-7-17.06-12.39-24.43zm36.82 22.37c-2.65 10.82-12.35 12.36-13.42 2.06-1.01-9.7-0.94-19.59 0.34-29.25 2.18-16.4 11.56-19.54 13.08-3.79 0.99 10.28 2.46 20.95 0 30.98zm8.95 1.72c-3.68 7.52 2.3 11.44 8.26 4.82 5.47-6.08 11.18-12.55 13.77-20.31 2.8-8.4-3.54-13.71-8.26-7.92-5.72 7.02-9.79 15.28-13.77 23.41zm-13.42 122.17c-4.13 7.79 1.03 13.23 7.23 5.85 6.66-7.92 10.9-17.6 16.17-26.5 6.07-10.23-1.86-13.59-9.29-5.16-6.49 7.36-9.53 17.15-14.11 25.81zm-28.57 2.07c2.15 10.71 10.02 9.48 11.01-2.06 0.8-9.3 0.25-19.03-2.75-27.88-4.74-13.94-14.92-10.71-14.45 3.44 0.3 9.07 4.41 17.61 6.19 26.5zm-36.48-10.33c-4.19-6.16-1.59-14.47 7.57-7.23 6.32 5 10.98 12.2 14.11 19.62 2.96 7-1.63 11.6-5.85 6.88-5.55-6.19-11.16-12.39-15.83-19.27zm-56.44-71.58c-3.72 7.33 0.38 12.22 7.57 6.2 4.89-4.09 7.18-9.8 10.67-15.14 2.43-3.73-1.51-7.15-6.88-4.47-5.53 2.73-8.57 7.91-11.36 13.41zm-19.27-37.86c2.74-11.19 8.92-10.51 10.32 0.34 1.48 11.47 1.17 23.03-2.06 34.76-2.89 10.5-12.56 11.38-12.05-1.03 0.47-11.41 1.07-22.97 3.79-34.07zm374.92-65.66c-4.74 8.26 1.1 11.93 7.16 5.17 6.65-7.42 14.74-13.9 19.49-22.67 5.31-9.81-1.57-17.35-8.75-9.94-7.6 7.84-12.46 17.97-17.9 27.44zm-19.08-9.94c-2.22 11.93 7.22 16.92 11.13 5.17 6.06-18.21 6.77-33.4 11.13-52.09 3.43-14.7-4.24-23.92-9.15-10.34-6.65 18.41-9.53 38.01-13.11 57.26zm-11.53 10.74c3.04 6.94 9.93 4.38 7.95-3.58-3.64-14.61-7.22-29.33-12.72-43.34-3.79-9.65-14.43-7.38-12.33 3.58 2.93 15.25 10.86 29.12 17.1 43.34zm-367.37 99.62c2.63 6.04 7.36 2.4 7.57-5.16 0.28-10.12-2.71-20.11-5.16-29.94-1.76-7.07-10.76-7.73-11.01 0.35-0.38 11.92 3.54 23.12 8.6 34.75zm-476.46-3.72c4.3 10.91 13.56 5.78 9.64-7.89-3.85-13.43-8.47-19.15-15.78-26.29-6.83-6.68-14.89-1.04-10.52 7.89 4.57 9.31 12.86 16.64 16.66 26.29z"/>
    <path class="st10" d="m1289.4 993.65c10.17-14.29 20.11-28.75 35.93-39.4 10.12-6.82 18.01 8.48 6.76 16.7-10.97 8.01-20.25 15.74-30.66 23.17-4.02-0.17-8.03-0.33-12.03-0.47m-20.33-0.58c-7.49-24.95-16.21-49.66-19.69-75.41-3-22.18 13.26-29.95 18.29-7.55 5.27 23.49 3.98 47.98 5.97 71.97 7.29-25.58 10.26-35.58 20.28-54.87 7.67-14.76 29.09-12.73 20.68 2.78-10.83 19.98-24.5 40.08-34.77 63.36-3.6-0.11-7.18-0.2-10.76-0.28z"/>
    <path class="st2" d="m799.16 1312.6c29.46-17.44 101.53-18.96 142.6-15.35 35.9 3.16 68.58 19.27 66.99 34.36-2.17 20.65-48.7 28.92-93.63 32.41-36.24 2.81-86.16-0.05-110.81-10.91-21.62-9.52-26.05-28.14-5.15-40.51m-140.01-80.06c27.56-16.23 94.98-17.65 133.41-14.28 33.59 2.95 64.15 17.93 62.67 31.99-2.03 19.23-45.56 26.92-87.59 30.17-33.91 2.61-80.6-0.04-103.67-10.15-20.22-8.88-24.37-26.22-4.82-37.73zm-105.85-78.85c25.73-15.18 88.66-16.51 124.54-13.36 31.35 2.75 59.89 16.77 58.5 29.91-1.89 17.98-42.53 25.17-81.77 28.21-31.65 2.44-75.24-0.04-96.77-9.49-18.89-8.3-22.75-24.51-4.5-35.27zm-74.48-70.66c22.03-12.82 72.25-14.84 102.96-12.18 26.84 2.32 51.63 14.21 50.08 25.26-1.62 11.58-33.21 21.71-66.8 24.27-27.1 2.06-67.61-0.48-86.04-8.47-16.17-7-15.83-19.79-0.2-28.88zm87.42-60.09c21.5-8.54 72.25-13.17 102.96-10.81 26.84 2.07 49.49 12.61 47.95 22.42-1.62 10.28-36.41 18.79-64.67 21.54-27.01 2.62-61.21-0.43-79.64-7.51-16.18-6.22-23.1-19.09-6.6-25.64z"/>
    <path class="st11" d="m1066.1 251.38c-10.84 4.54-16.87 1.08-10.39-11.33 6.02-11.52 8.86-44.8-7.79-61.02-70.71-68.92-28.22-123.68 42.92-170.33 37.55-24.62 89.14 6.2 48.25 52.34-34.01 38.37-56.9 47.24-27.86 83.62 38.32 48.01-1.93 88.63-45.13 106.72"/>
    <path class="st2" d="m324.93 300.72c74.97-0.5 149.94-1.01 224.91-1.51 24.09-40.22-22.08-70.98-59.62-47.55-9.99-68.74-104.98-46.73-102.64 0.76-35.98-17.87-74.97 9.55-62.65 48.3"/>
    <path class="st2" d="m534.75 124.86c91.07 0.5 182.14 1.01 273.21 1.51 32.15-49.04-40.2-85.55-72.45-51.32 6.29-83.02-127.8-89.06-128.31 2.26-31.7-21.13-81.51-2.26-72.45 47.55"/>
    <path class="st5" d="m1208 1298.6c-1.09 12.12-2.18 24.25-3.27 36.37-7.27 4.49-23.03 6.54-21.82 13.46 0.98 5.62 6.28 3.96 17.09-1.09-1.58 5.45-8.06 13.46-4.94 15.51 6.69 4.39 13.99-6.85 15.12-18.06 10.2 3.14 13.65 3.97 16.54-1.24 1.36-2.45-0.09-6.34-10.36-7.49 2.06-15.52 4.12-31.03 6.18-46.55-4.84 3.03-9.69 6.06-14.54 9.09m-43.64 1.09c-1.67 12.04-3.67 24.02-11.64 34.91 8.21 3.15 9.11 6.43 8 9.87-2.19 6.78-12.85-0.53-19.28-1.87-8.61 5.1-17.8 12.08-22.63 9.12-2.95-1.81-1.16-5.41 8.81-10.57-7.72-1.78-9.87-3.47-9.09-7.27 1.02-4.97 16.52-3.7 25.09-3.64 4.08-11.64 5.23-23.28 6.91-34.91 4.62 1.45 9.22 2.91 13.83 4.36zm-79.65-120.02c-28.43 19.19-29.04-27.19-8.73-37.82-7.66-0.71-16.61-0.91-23.58-1.9-4.16-0.59-4.2-2.11-3.01-5.04 3.02-7.43 10.34-10.67 16.78-14.16-8.48-17.34-0.61-28.85 11.64-25.82-5.56-16.92 11-25.16 21.82-16 4.61-18.43 40.85-7.76 19.28 32l-1.09 61.1c-9.59 4.25-15.17 3.4-33.11 7.64z"/>
    <path class="st2" d="m1100.7 1124.3c3.42 0 6.18 2.77 6.18 6.18s-2.77 6.18-6.18 6.18-6.18-2.77-6.18-6.18c-0.01-3.41 2.76-6.18 6.18-6.18m-23.2 4.46c-2.6-13.1 7.62-25.14 19.87-28.62 17.02-4.84 32.93 7.97 39.53 23.06 16.37 37.42 69.2 87.31 119.98 11.96 16.87-25.03 43.01-0.23 25.43 21.84 18.48-7.65 35.87 6.16 11.81 34.87 12.12 8.96 7.2 34.48-17.53 47.56-1.99 48.91-54.29 73.47-100.16 71.43-32.88-1.46-74.2-24.37-90.23-54.55-16.29-30.63-0.89-88.19-8.7-127.55z"/>
    <path class="st8" d="m1134 1217.5c-1.1-5.73 4.25-7.68 5.27-2.77 8.46 40.74 51.85 50.18 67.65 30.22-6.28-2.59-3.53-8.77 1.66-7.21 22.82 6.85 37.38-17.61 20.24-24.95-6.44-2.76-2.09-7.31 3.05-6.1 22.19 5.23 12.57 43.02-15.25 38.26-18.41 28.96-72.77 23.63-82.62-27.45"/>
    <path class="st12" d="m1062.3 898.7-0.19-44.54-41.07 0.2c-0.09 13.85-0.22 30.37-0.31 44.03 13.73-0.06 27.63 0.07 41.57 0.31m55.16-44.81-37.81 0.19 0.39 44.98c12.69 0.28 25.35 0.62 37.86 0.95-0.17-13.73-0.29-31.15-0.44-46.12zm-38.39-67.28 0.42 48.55 37.73-0.37c-0.02-1.28-0.04-2.49-0.07-3.62-0.01-16.46-13.96-40.05-38.08-44.56zm-57.92 49.12 40.88-0.41-0.21-48.78c-25.84 4.16-40.31 25.91-40.67 49.19zm-21.02 62.92c-3.15 0.07-5.11 4.79-5.14 7.93l-0.09 9.8c-0.03 3.19 3.34 6.99 6.53 7 45.36 0.17 93.14 0.17 138.52 0.56 3.33 0.03 3.86-4.23 3.83-7.56l-0.09-9.9c-0.03-3.48-1.95-5.89-5.42-5.97l-1.76-0.04c-0.52-24.29-1.05-47.2-1.57-71.77 0-25.14-23.83-62.5-64.28-62-42.99 0.53-69.43 34.67-69.43 70.28-0.08 22.81-0.17 40.28-0.25 61.64l-0.85 0.03z"/>
  </svg>
    </div>
    
    <!-- Content - Right side -->
    <div class="content">
        <h1 class="main-title">{main_title}</h1>
        <p class="subtitle">{subtitle}</p>
    </div>
</body>
</html>'''
    
    return html_code

def generate_section_header_slide_10(
    main_title="Main Title Here",
    subtitle="You can enter a subtitle here if you need it",
    bg_color="#9BD89B",
    notebook_bg="#FFFFFF",
    title_color="#A84A3A",
    subtitle_color="#5A5A5A",
    sticky_note_colors=["#FFD966", "#FFB3B3"],
    custom_css=""
):
    """
    Generate a notebook-style overview slide with spiral binding and bookmark sticky notes.
    
    Parameters:
    - main_title: Main title text (default: "Main Title Here")
    - subtitle: Subtitle text displayed below the main title (default: "You can enter a subtitle here if you need it")
    - bg_color: Background color of the slide (default: "#9BD89B" - light green)
    - notebook_bg: Notebook paper background color (default: "#FFFFFF" - white)
    - title_color: Color of the main title text (default: "#A84A3A" - brown/red)
    - subtitle_color: Color of the subtitle text (default: "#5A5A5A" - gray)
    - sticky_note_colors: List of colors for bookmark sticky notes (default: ["#FFD966", "#FFB3B3"] - yellow and pink)
    - custom_css: Additional custom CSS to inject into the style block (default: "")
    
    Returns:
    - Complete HTML string for the slide
    """
    
    if isinstance(main_title, list):
        main_title = main_title[0]
    if isinstance(subtitle, list):
        subtitle = subtitle[0]
    
    # Generate sticky notes (always show)
    sticky_notes_html = ""
    if len(sticky_note_colors) >= 2:
        sticky_notes_html = f"""
        <div class="sticky-notes">
            <div class="sticky-note" style="background: {sticky_note_colors[0]};"></div>
            <div class="sticky-note" style="background: {sticky_note_colors[1]};"></div>
        </div>
        """
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{main_title} - Slide</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&family=Noto+Sans:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                margin: 0;
                padding: 0;
                font-family: 'Roboto', 'Noto Sans', sans-serif;
                overflow: hidden;
            }}
            
            .slide-container {{
                width: 1920px;
                height: 1080px;
                background: {bg_color};
                position: relative;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            
            .notebook {{
                width: 1400px;
                height: 700px;
                background: {notebook_bg};
                border-radius: 0 15px 15px 0;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                position: relative;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 60px 100px 60px 140px;
                background-image: 
                    repeating-linear-gradient(
                        to bottom,
                        transparent 0px,
                        transparent 39px,
                        rgba(180, 180, 180, 0.25) 39px,
                        rgba(180, 180, 180, 0.25) 40px
                    ),
                    linear-gradient(
                        to right,
                        transparent 0px,
                        transparent 89px,
                        rgba(255, 100, 100, 0.4) 89px,
                        rgba(255, 100, 100, 0.4) 92px,
                        transparent 92px
                    );
            }}
            
            .spiral-binding {{
                position: absolute;
                left: 15px;
                top: 40px;
                bottom: 40px;
                width: 60px;
                display: flex;
                flex-direction: column;
                justify-content: space-around;
                align-items: center;
                z-index: 10;
            }}
            
            .spiral-ring {{
                width: 35px;
                height: 45px;
                border: 5px solid #2a2a2a;
                border-radius: 50%;
                background: linear-gradient(to right, rgba(0,0,0,0.1) 0%, transparent 50%, rgba(255,255,255,0.3) 100%);
                box-shadow: inset -2px 0 4px rgba(0,0,0,0.3), inset 2px 0 4px rgba(255,255,255,0.3);
            }}
            
            .sticky-notes {{
                position: absolute;
                top: -50px;
                right: 200px;
                display: flex;
                flex-direction: row;
                gap: 30px;
                z-index: 5;
            }}
            
            .sticky-note {{
                width: 180px;
                height: 100px;
                border-radius: 3px;
                box-shadow: 0 6px 15px rgba(0,0,0,0.2);
                position: relative;
            }}
            
            .sticky-note::before {{
                content: '';
                position: absolute;
                top: -10px;
                left: 50%;
                transform: translateX(-50%);
                width: 60px;
                height: 20px;
                background: rgba(255, 255, 255, 0.4);
                border-radius: 2px;
            }}
            
            .section-number {{
                font-size: 4rem;
                font-weight: 900;
                color: #4A4A4A;
                font-family: 'Roboto', 'Noto Sans', sans-serif;
            }}
            
            .main-title {{
                font-size: 4rem;
                font-weight: 900;
                color: {title_color};
                text-align: center;
                margin-bottom: 50px;
                font-family: 'Roboto', 'Noto Sans', sans-serif;
                letter-spacing: 1px;
                width: 100%;
                max-width: 1200px;
                z-index: 3;
            }}
            
            .subtitle {{
                font-size: 2rem;
                font-weight: 400;
                color: {subtitle_color};
                text-align: center;
                line-height: 1.6;
                font-family: 'Noto Sans', 'Roboto', sans-serif;
                width: 100%;
                max-width: 1200px;
                z-index: 3;
            }}
            
            {custom_css}
        </style>
    </head>
    <body>
        <div class="slide-container">
            <div class="notebook">
                <div class="spiral-binding">
                    <div class="spiral-ring"></div>
                    <div class="spiral-ring"></div>
                    <div class="spiral-ring"></div>
                    <div class="spiral-ring"></div>
                    <div class="spiral-ring"></div>
                    <div class="spiral-ring"></div>
                    <div class="spiral-ring"></div>
                    <div class="spiral-ring"></div>
                    <div class="spiral-ring"></div>
                    <div class="spiral-ring"></div>
                </div>
                
                {sticky_notes_html}
                
                <div class="main-title">{main_title}</div>
                <div class="subtitle">{subtitle}</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_code

def generate_section_header_slide_12(
    main_title="What is <br> artificial intelligence?",
    bg_color="#f5f5f5",
    title_color="#2d3748",
    custom_css=""
):
    """
    Generate a minimal question slide with geometric background icons.
    
    Parameters:
    - main_title: Main title text
    - bg_color: Background color
    - title_color: Color of the main question/title text
    - custom_css: Additional custom CSS
    
    Returns:
    - HTML string
    """
    
    # Section number removed; always render the decorative arrow SVG

    # Wrap arrow and question in visible, positioned block containers so the
    # converter can detect them as separate elements.
    question_block_html = f'<div class="block question-block" style="position:absolute; top:320px; left:120px; width:1680px;"><div class="question">{main_title}</div></div>'
    
    # SVG decoration - wrapped in container for converter recognition
    svg_decoration_html = '''<div class="svg-decoration">
        <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 349.98 404.85" width="100%" height="100%" preserveAspectRatio="xMidYMid meet">
            <path d="m21.673 387.4c4.5311 3.232 17.093-3.7092 49.835-92.884 33.132-99.223 24.842-98.113 25.195-101.22" fill="none" stroke="#000" stroke-width="7.5808"/>
            <path d="m9.3338 385.21c-5.5634-0.15978-12.914-8.7261 11.535-105.52 20.728-67.241 34.065-95.705 42.635-100.65" fill="none" stroke="#000" stroke-width="7.5808"/>
            <path d="m61.099 188.17c-10.657-2.6855-5.8822-19.804 4.5119-19.243" fill="none" stroke="#000" stroke-width="7.5808"/>
            <path d="m62.697 183.18c-22.413 35.084-56.478 144.18-54.97 197.09-0.60276 2.2927 16.176 7.2052 17.088 5.5113 30.438-42.974 65.799-150.21 70.849-192.18-16.275-10.679-32.967-10.426-32.967-10.426z" fill="#8c9fbd" fill-rule="evenodd" stroke="#000" stroke-width=".75808"/>
            <path d="m95.724 198.47c7.003 1.0866 14.704-8.1263 6.0323-18.638" fill="none" stroke="#000" stroke-width="7.5808"/>
            <path d="m60.643 170.62c0.41893-30.713 20.418-81.326 23.13-89.395s34.271-83.326 54.962-77.064 15.761 49.195-4.0546 109.54-31.179 70.414-31.179 70.414" fill="none" stroke="#000" stroke-width="7.5808"/>
            <path d="m138.33 8.0324c-26.672-7.7494-73.214 116.23-74.078 162.46-1.6226 6.4141 8.773 5.6941 19.431 8.4432 10.951 2.8473 16.689 9.4584 18.172 3.5716 26.955-44.869 64.655-165.41 36.475-174.48z" fill="#8c9fbd" fill-rule="evenodd" stroke="#000" stroke-width=".75808"/>
            <path d="m59.342 177.84c-3.0174 10.06 8.254 6.7068 19.528 9.8798s20.139 10.726 22.553 3.5391-8.9971-15.837-18.174-17.69-21.447-4.1303-23.907 4.2715z" fill="#fae472" fill-rule="evenodd" stroke="#000" stroke-width="3.7904"/>
            <path d="m16.687 365.96c14.006-84.171 34.011-136.85 41.926-156.3 7.2339-20.325-10.548 53.861-14.186 64.687l-27.74 91.613z" fill="#fff" fill-opacity=".54167" fill-rule="evenodd"/>
            <path d="m73.835 167.51c10.3-61.664 30.716-108.86 36.591-116.65s-2.9963 28.3-2.9963 28.3l-33.595 88.354z" fill="#fff" fill-opacity=".54167" fill-rule="evenodd"/>
            <path d="m299.95 263.47c-2.5923-0.21458-5.2364-0.12238-7.8339-0.15105-20.089-0.35718-40.131-0.33793-60.223 0.14397-39.199 1.1043-79.194 2.0061-117.79 9.5691-1.3237 0.30448-9.4849 1.2978-10.201 3.1465-0.41149 1.0623 2.4222-1.051 2.6412-2.169 0.24313-1.2413-2.5334-3.6461-1.2706-3.5755 12.583 0.70346 26.129 4.7564 38.692 6.487 60.37 8.0202 121.77 11.682 181.68 22.654 70.271 16.203-32.569 30.647-46.417 31.868-44.378 3.3506-91.065 1.0639-134.84 9.6982-0.70183 0.21654 0.06344-5.6501 5.8595-2.8015 11.429 5.617 23.275 10.42 34.919 15.568 9.3567 4.1975 46.284 15.711 41.876 30.768-9.6527 12.142-34.543 10.79-48.474 11.519-17.674 0.76333-35.359 0.81646-53.046 0.90711-7.4686 0.06817-14.967 0.07921-22.397 0.9282-6.0326 0.73547-12.023 1.3194-18.092 1.6709-6.4636 0.36966-12.923 0.89954-19.363 1.5609-5.6366 0.66362-11.24 1.5034-16.906 1.8983-4.4927 0.26851-8.9764 0.65414-13.475 0.82453-4.0933 0.13039-8.1854 0.09711-12.28 0.03899-3.432-0.05008-6.8606-0.15735-10.28 0.2206l-2.5826-10.563c4.4102-0.41538 8.7977-0.3954 13.221-0.33603 3.6548 0.04764 7.3085 0.0822 10.963-0.0244 4.236-0.14708 8.4596-0.49794 12.692-0.72209 5.3906-0.34108 10.721-1.1824 16.086-1.7698 6.783-0.65499 13.579-1.1935 20.381-1.6097 5.6498-0.34735 11.22-0.97668 16.839-1.6301 8.398-0.87682 16.85-0.7782 25.283-0.70632 17.208 0.2056 34.409 0.37522 51.605-0.45325 9.1431-0.54983 18.434-1.1124 27.415-3.0235 0.66456-0.1414 6.4881-2.0766 6.6064-1.5154 1.6398 3.0727-4.8004-5.1582-7.7546-7.0031-8.413-5.2539-17.542-9.3368-26.549-13.442-4.9411-2.1898-71.688-24.188-36.103-30.023 45.252-4.9962 91.151-3.7838 136.54-7.7894 8.3014-0.87416 81.643-4.8198 44.088-15.768-58.6-13.412-120.19-16.717-179.87-22.926-11.232-1.1549-89.41-10.698-31.427-21.082 39.938-6.172 80.689-7.4134 121.01-9.1726 20.313-0.86285 40.616-1.5948 60.944-1.9562 2.5975-0.02866 5.2416 0.06353 7.8339-0.15104v10.892z" fill-opacity=".75"/>
            <path d="m8.6731 383.7c-3.8858 22.709 2.0327 25.782 14.192 4.3371-5.4783-0.44454-12.119-3.1366-14.192-4.3371z" fill="#929292" fill-rule="evenodd" stroke="#000" stroke-width="4.6243"/>
        </svg>
    </div>'''
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Question Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&family=Noto+Sans:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Roboto', 'Noto Sans', sans-serif;
            width: 1920px;
            height: 1080px;
            background: {bg_color};
            padding: 300px 120px;
        }}
        
        
        .question {{
            font-size: 6rem;
            font-weight: 700;
            color: {title_color};
            line-height: 1.3;
            background: rgba(255, 255, 255, 0.01);
            padding: 20px;
        }}
        
        .svg-decoration {{
            position: absolute;
            right: 50px;
            bottom: 50px;
            width: 500px;
            height: 680px;
            z-index: 5;
        }}
        
        {custom_css}
    </style>
</head>
<body>
    {question_block_html}
    {svg_decoration_html}
</body>
</html>"""
    
    return html_code


def generate_section_header_slide_15(
    main_title="This is the title of this section",
    bg_color="#0f2f1f",
    text_color="#f8f8f8",
    blob1_color="rgba(220, 38, 38, 0.5)",
    blob2_color="rgba(34, 139, 34, 0.5)",
    blob3_color="rgba(218, 165, 32, 0.4)",
    custom_css=""
):
    """
    Generate a Christmas-themed section header slide with festive gradient blobs and SVG illustration.
    Parameters:
    - main_title: Main title text (italic, bold, white)
    - bg_color: Background color (default: #0f2f1f - dark evergreen)
    - text_color: Text color (default: #f8f8f8 - bright white)
    - blob1_color: First gradient blob color (default: red - rgba(220, 38, 38, 0.5))
    - blob2_color: Second gradient blob color (default: forest green - rgba(34, 139, 34, 0.5))
    - blob3_color: Third gradient blob color (default: golden - rgba(218, 165, 32, 0.4))
    - custom_css: Additional custom CSS rules
    
    Returns:
    - Complete HTML string with embedded Christmas tree SVG illustration
    """
    
    # Always include blobs (static)
    blobs_html = f"""
        <div class="gradient-blob blob1"></div>
        <div class="gradient-blob blob2"></div>
        <div class="gradient-blob blob3"></div>
        """
    
    # project_name removed
    
    # section number removed (not used)
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gradient Colorful Title Slide</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background: {bg_color};
                color: {text_color};
                overflow: hidden;
            }}
            
            .slide-container {{
                width: 1920px;
                height: 1080px;
                position: relative;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            
            /* Gradient Blobs */
            .gradient-blob {{
                position: absolute;
                border-radius: 50%;
                filter: blur(100px);
                opacity: 1; /* static visible blobs */
                z-index: 1;
            }}
            
            .blob1 {{
                width: 500px;
                height: 500px;
                background: {blob1_color};
                top: 5%;
                right: 10%;
            }}
            
            .blob2 {{
                width: 600px;
                height: 600px;
                background: {blob2_color};
                bottom: 5%;
                right: 15%;
            }}
            
            .blob3 {{
                width: 450px;
                height: 450px;
                background: {blob3_color};
                bottom: 0%;
                right: 0%;
            }}
            
            /* Content Area - Left Side */
            .content {{
                position: relative;
                z-index: 10;
                padding: 100px 60px 100px 120px;
                width: 65%;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}
            
            /* SVG Container - Right Side */
            .svg-container {{
                position: relative;
                z-index: 10;
                width: 45%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 180px 120px 180px 60px;
            }}
            
            .svg-container svg {{
                max-width: 100%;
                max-height: 100%;
                width: auto;
                height: auto;
            }}
            
            /* Tagline removed */
            
            /* Project Name removed */
            
            /* Main Title */
            .main-title {{
                font-size: 4.5rem;
                font-weight: 900;
                font-style: italic;
                text-align: left;
                max-width: 900px;
                line-height: 1.2;
                margin-bottom: 30px;
                opacity: 1;
            }}
            
            /* Section Number */
            /* section-number removed */
            
            /* Animations */
            /* Animations removed - slide is static and converter-friendly */
            
            /* Responsive Design */
            @media (max-width: 1920px) {{
                .slide-container {{
                    width: 100vw;
                    height: 100vh;
                    transform-origin: top left;
                }}
            }}
            
            {custom_css}
        </style>
    </head>
    <body>
        <div class="slide-container">
            {blobs_html}
            
            <div class="content">
                <div class="main-title">{main_title}</div>
            </div>
            
            <div class="svg-container">
                <?xml version='1.0' encoding='utf-8'?>
                <svg xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 572.55 614.16">
                    <defs>
                    <linearGradient id="a">
                        <stop stop-color="#4e9a06" offset="0"/>
                        <stop stop-color="#73d216" offset="1"/>
                    </linearGradient>
                    <linearGradient id="h" x1="170.6" x2="84.474" y1="-70.642" y2="-103.64" gradientTransform="matrix(.52353 .30226 -.30226 .52353 188.6 91.779)" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#ffd543" offset="0"/>
                        <stop stop-color="#ffe791" offset="1"/>
                    </linearGradient>
                    <linearGradient id="b" x1="258.1" x2="290.29" y1="600.69" y2="603.63" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#8f5902" offset="0"/>
                        <stop stop-color="#c17d11" offset="1"/>
                    </linearGradient>
                    <linearGradient id="g" x2="0" y1="98.459" y2="247.42" gradientUnits="userSpaceOnUse" xlink:href="#a"/>
                    <linearGradient id="f" x1="285.07" x2="283.4" y1="205.98" y2="337.65" gradientUnits="userSpaceOnUse" xlink:href="#a"/>
                    <linearGradient id="e" x1="284.39" x2="286.44" y1="309.82" y2="420.19" gradientUnits="userSpaceOnUse" xlink:href="#a"/>
                    <linearGradient id="d" x1="292.54" x2="292.53" y1="389.45" y2="492.78" gradientUnits="userSpaceOnUse" xlink:href="#a"/>
                    <linearGradient id="c" x1="283.03" x2="284.77" y1="453.04" y2="581.74" gradientUnits="userSpaceOnUse" xlink:href="#a"/>
                    </defs>
                    <g transform="translate(9.7969 -27.143)">
                    <path d="m-1.634 620.28c11.293 3.917 22.509 7.1206 33.804 9.5199 11.462 2.4347 23.004 4.0412 34.789 4.7243 11.424 0.66221 23.075 0.45673 35.101-0.70301 11.183-1.0785 22.689-2.9821 34.637-5.7806 13.256-3.8968 25.307-8.6203 36.847-13.372 12.45-5.1265 24.307-10.286 36.441-14.476 12.146-4.1944 24.571-7.4175 38.148-8.6636 10.178-1.5292 20.528-2.4041 30.85-2.3895 10.355 0.0147 20.681 0.92464 30.776 2.9675 10.07 2.0376 19.909 5.2023 29.319 9.7299 9.7669 4.2818 19.642 8.0352 29.782 11.197 9.993 3.1161 20.243 5.6578 30.9 7.5645 10.124 1.8114 20.615 3.0498 31.602 3.6634 10.846 0.3877 21.575 0.58391 32.244 0.6467 10.791 0.0635 21.522-9e-3 32.251-0.15876s21.458-0.37506 32.245-0.61703c10.672-0.23942 21.402-0.49474 32.245-0.70774 7.0535 0.0765-2.4996 2.1618-19.363 3.748-7.088 0.66669-15.468 1.2452-24.449 1.5493-11.863 0.50187-22.837 1.1034-33.591 1.5573-11.193 0.47242-22.147 0.78491-33.616 0.65863-10.56-0.11627-21.556-0.60452-33.575-1.6824-12.472-0.97366-24.118-2.7432-35.247-5.138-11.9-2.5605-23.208-5.8358-34.303-9.6172-11.181-3.8106-22.144-8.1351-33.277-12.76-12.754-3.9386-25.727-5.8349-38.749-6.1338-13.051-0.29947-26.152 1.0056-39.131 3.4676-12.828 2.4331-25.537 5.9962-37.963 10.257-12.527 4.2951-24.766 9.2992-36.548 14.569-10.726 5.3084-21.889 9.1749-33.322 11.891-11.471 2.7254-23.213 4.2929-35.059 4.997-11.766 0.69946-23.633 0.54712-35.436-0.16842-11.877-0.72001-23.689-2.0103-35.267-3.5768-3.487-0.96157-14.1-2.1216-21.982-4.2537-9.1229-2.4679-14.586-6.238-1.1012-12.51" fill="#5a5148" stroke="#000" stroke-linecap="square" stroke-linejoin="round" stroke-width=".033"/>
                    <path d="m296.53 545.59c-17.378-0.10986-40.543 8.0028-51.25 17.719 0.18786 21.763-2.0564 34-5.9375 48.562 17.982 0.73415 33.744 5.7527 43.719 13.156 12.606-2.7256 24.791-7.7016 37.781-8.4375-1.9069-19.639-2.1312-38.238-2.625-57.125-0.63283-9.8722-9.7976-13.8-21.688-13.875z" fill="#764c02"/>
                    <path d="m294.65 553.6c-15.774-0.0997-36.803 7.2645-46.522 16.084 0.17052 19.755-1.8667 30.863-5.3897 44.082 16.323 0.66642 30.631 5.2219 39.685 11.942 11.443-2.4742 22.504-6.9911 34.296-7.6591-1.731-17.827-1.9346-34.71-2.3828-51.855-0.57445-8.9614-8.8937-12.527-19.687-12.595z" fill="url(#b)"/>
                    <path d="m281.99 97.229c-0.72644-0.0183-1.4618 0.035-2.25 0.125-7.6823 1.2992-13.525 14.134-20.469 31.25-4.3538 10.732-9.1505 23.152-15.094 35.438-5.5504 11.473-12.122 22.831-20.281 32.625-5.3597 6.4437-9.965 12.364-14.594 18.281s-9.2653 11.838-14.625 18.281c-10.897 12.064-9.5257 20.469-1.9375 23.594 1.4729 0.60658 3.1645 1.0234 5.0625 1.2188-1.7556 3.5205-3.5511 7.0212-5.4375 10.469-5.2735 9.6379-11.082 18.985-17.406 27.906-6.3517 8.9603-13.234 17.481-20.688 25.5 0.0231 11.468 7.649 16.036 16.625 16.281 0.29079 8e-3 0.5816 9.9e-4 0.875 0-0.48613 1.1076-0.96418 2.2105-1.4688 3.3125-4.6606 10.179-10.158 20.095-16.938 29.375-6.4663 8.8516-14.106 17.146-23.375 24.5-6.2028 9.7807 7.7267 18.83 19.531 17.656-1.4809 2.9554-2.9781 5.8935-4.5625 8.7812-5.0102 9.132-10.638 17.941-17.531 26.375-6.296 7.7034-11.599 11.699-22.531 22.188-7.5783 10.166-4.4191 16.616 3.8438 18.719 2.3324 0.59355 5.0767 0.832 8.0938 0.71875-4.7442 7.5362-9.7859 14.887-15.156 22-6.6832 8.8523-13.862 17.344-21.531 25.344s-15.827 15.508-24.5 22.438c-1.4886 11.444 5.8275 16.976 15.094 18.375 8.8063 1.3292 19.376-1.0764 25.75-5.6562 9.9524-4.1339 20.776-5.0039 31.125-3.0625s20.218 6.6908 28.188 13.781c9.641 5.9993 20.384 7.7556 31.219 7.125 10.804-0.62885 21.699-3.6313 31.656-7.1562 9.1364-1.2666 18.005 0.0979 26.812 2.25 8.7428 2.1362 17.417 5.0572 26.188 6.9375 8.7943 1.8854 17.7 2.7256 26.875 0.71875 7.7577-2.6659 15.305-6.6304 23.125-9.5 7.7669-2.8501 15.803-4.6202 24.531-2.9688 9.71 0.37621 19.254 3.8112 28.812 6 9.5975 2.1977 19.21 3.1392 28.906-1.4688 8.7521-2.687 16.57-8.3739 24.688-12.969 8.1942-4.6382 16.693-8.1635 26.656-6.3125 7.8366 0.72399 15.316 3.4152 22.812 5.875 7.5539 2.4784 15.126 4.722 23.062 4.5312 10.785-2.4641 13.083-8.2773 11.062-14.875-1.76-5.7463-6.7911-12.089-12.406-17.312-9.3126-8.7768-17.955-18.252-25.938-28.25-4.9797-6.237-9.7118-12.673-14.188-19.281 6.8576 1.6755 13.106 1.8692 17.75 0.6875 8.2629-2.1027 11.453-8.5524 3.875-18.719-8.8957-7.095-16.267-14.484-22.562-22.188-6.8932-8.4341-12.521-17.243-17.531-26.375-3.2837-5.9851-6.2855-12.133-9.2188-18.406 2.9593 0.56684 6.1659 0.60825 9.7188-0.1875 15.73-5.2288 1.0718-11.184-14.594-25.719-13.413-14.745-18.289-24.646-21.531-33.156-1.751-4.5956-3.0125-8.8071-4.9062-13.125 0.92771-8e-3 1.8243-0.037 2.7188-0.0937 12.215-0.77533 20.887-6.1075 13.531-15.5-9.2632-8.7123-16.697-16.402-22.938-23.594-8.0615-9.2899-14.131-17.749-19.5-26.5-4.6921-7.648-8.8739-15.589-13.406-24.438 1.0546-0.99194 2.0747-2.0733 3.0312-3.25 4.7872-8.5809 5.1676-21.954-2.3125-28.781-8.9002-9.4869-17.062-19.548-24.469-30.062-7.4631-10.593-14.177-21.659-20.156-33.094-5.9922-11.46-11.217-23.305-15.75-35.406-4.3415-9.017-8.5408-20.976-19.438-21.25z" fill="#4a9106"/>
                    <path d="m447.29 551.06-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                    <path d="m465.67 588.96c0 10.452-8.473 18.925-18.925 18.925s-18.925-8.473-18.925-18.925 8.4729-18.925 18.925-18.925 18.925 8.473 18.925 18.925z" fill="#640000"/>
                    <path d="m463.08 588.96c0 9.0202-7.3123 16.332-16.332 16.332s-16.332-7.3123-16.332-16.332 7.3123-16.332 16.332-16.332 16.332 7.3123 16.332 16.332z" fill="#cc0001"/>
                    <path d="m443.17 585.07c-2.7865 1.7001-6.0116 1.4858-7.2035-0.47854s0.10072-4.935 2.8872-6.6351 6.0116-1.4858 7.2035 0.47854-0.10071 4.935-2.8872 6.6351z" fill="#fabdbd"/>
                    <path d="m446.69 578.06c-0.74528-1.2283-2.1047-1.8669-3.5872-1.9654s-3.1231 0.31939-4.6382 1.2438-2.6392 2.1933-3.2334 3.5589-0.65346 2.8697 0.0918 4.098 2.1131 1.8807 3.5956 1.9792 3.1231-0.3194 4.6382-1.2438 2.6392-2.1933 3.2334-3.5589 0.6451-2.8835-0.10018-4.1118zm-1.2798 0.78085c0.44663 0.73608 0.45216 1.7012 1e-3 2.737s-1.361 2.0955-2.6324 2.8712-2.642 1.1077-3.7666 1.033-1.963-0.53161-2.4097-1.2677-0.45755-1.679-7e-3 -2.7148 1.3748-2.1039 2.6462-2.8796 2.6283-1.0993 3.7529-1.0246 1.9684 0.50943 2.4151 1.2455z" fill="#640000"/>
                    <g transform="translate(-227.31 66.726)">
                        <path d="m343.07 490.25-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                        <g transform="translate(15.765 11.549)">
                        <path d="m341.66 511.84c0 8.4271-6.8315 15.259-15.259 15.259s-15.259-6.8315-15.259-15.259 6.8315-15.259 15.259-15.259 15.259 6.8315 15.259 15.259z" fill="#132c51"/>
                        <path d="m339.57 511.84c0 7.2727-5.8957 13.168-13.168 13.168s-13.168-5.8957-13.168-13.168 5.8957-13.168 13.168-13.168 13.168 5.8957 13.168 13.168z" fill="#3466a5"/>
                        <path d="m323.52 508.7c-2.2466 1.3707-4.847 1.198-5.808-0.38584s0.0812-3.979 2.3278-5.3497 4.847-1.198 5.808 0.38584-0.0812 3.979-2.3278 5.3497z" fill="#cbdbed"/>
                        <path d="m326.36 503.05c-0.60089-0.99033-1.697-1.5052-2.8923-1.5846s-2.5181 0.25751-3.7396 1.0028-2.1279 1.7684-2.607 2.8694-0.52686 2.3138 0.074 3.3041 1.7037 1.5163 2.899 1.5958 2.5181-0.25752 3.7396-1.0028 2.1279-1.7684 2.607-2.8694 0.52013-2.3249-0.0808-3.3152zm-1.0319 0.62958c0.36011 0.59348 0.36456 1.3716 8.1e-4 2.2068s-1.0974 1.6895-2.1225 2.315-2.1302 0.89313-3.0369 0.83289-1.5827-0.42862-1.9428-1.0221-0.36891-1.3537-6e-3 -2.1889 1.1084-1.6963 2.1336-2.3217 2.1191-0.88636 3.0258-0.82612 1.5871 0.41074 1.9472 1.0042z" fill="#132c51"/>
                        </g>
                    </g>
                    <path d="m234.77 611.3c-20.091 0-37.849 5.3233-48.625 13.5 11.482-5.5423 27.093-8.9375 44.312-8.9375 18.274 0 34.745 3.8439 46.375 10-7.2747 1.5585-13.925 2.9263-21.219 3.5312-5.3914-0.0532-11.274 0.71769-16.156-2.0625l-5 3.1562c-1.8637 6.8115 32.807 0.28777 36.781-0.65625 7.3226-1.0873 14.417-3.2006 21.531-5.1875 11.355-3.0799 21.274-5.9601 36.094-4.9062 10.691 0.97877 13.748 2.3519 26.031 5.0312-4.1593-2.3778-8.6422-4.1581-13.188-5.6562-6.2167-2.3543-12.865-3.3442-19.5-3.0625-13.507 0.44493-26.107 5.6786-39.156 8.5-10.814-8.0262-28.405-13.25-48.281-13.25z" fill="#5a5148"/>
                    <path d="m176.28 470.5c-5.5536 0.12641-11.029 1.5392-16.406 3.5625-9.4497 3.5559-18.607 8.973-27.5 12.594-2.2657 0.79991-4.52 1.4724-6.6875 1.9688-3.9939 6.2871-8.1873 12.428-12.625 18.406-6.231 8.3938-12.932 16.445-20.062 24.062-7.1361 7.624-14.716 14.818-22.781 21.469-0.32865 4.1799 0.67039 6.9847 2.5 9.0625 1.9805 2.2491 5.1067 3.7586 8.9062 4.4375 7.5991 1.3578 17.575-0.91267 22.938-4.8438 0.17372-0.13574 0.36246-0.25107 0.5625-0.34375 9.9476-4.2154 20.741-5.1229 31.031-3.1875 10.28 1.9336 20.059 6.7045 28.031 13.812l0.0312 0.0312c8.672 5.4925 18.483 7.0744 28.469 6.4062 9.7065-0.64946 19.576-3.4257 28.781-6.75 0.18285-0.0604 0.37129-0.10224 0.5625-0.125 13.789-1.9503 26.659 2.1338 39.094 5.7188 12.392 3.5729 24.31 6.626 36.531 3.9375 7.1983-2.5492 14.529-6.5383 22.375-9.375 7.3708-2.6648 15.197-4.3142 23.812-2.75v-0.0312c9.8667 0.39001 19.153 3.8117 28.031 5.875s17.106 2.851 25.5-1.2188c0.12117-0.0608 0.24648-0.11306 0.375-0.15625 7.7204-2.4182 15.074-7.8259 23.031-12.406 7.8904-4.542 16.676-8.2614 26.938-6.4062 0.0866 0.0157 0.16322 0.0149 0.25 0.0312 7.5374 0.74857 14.531 3.119 21.281 5.375 7.3026 2.4406 14.319 4.745 21.406 4.6562 4.2007-1.0224 6.5204-2.5225 7.625-4.0312 1.129-1.5422 1.3652-3.2657 0.84375-5.6562-1.0428-4.7811-5.7802-11.342-11.281-16.562l-0.0312-0.0312c-8.7703-8.4328-16.912-17.496-24.438-27.062-5.2098-7.7836-10.48-13.546-15.188-18.844-7.1224-3.3347-14.406-7.2831-21.875-10.094-9.5588-3.597-19.385-5.2891-29.5-1.2188-7.6964 3.7687-14.756 9.9292-22.25 14.781-7.5716 4.9021-15.587 8.4687-25.156 6.875-10.004-3.8845-19.115-9.4835-28.344-14.812-9.825-3.4481-19.192-9.694-29.188-12.156-10.521-2.9092-19.736 0.46041-28.625 5.25-8.7954 4.739-17.272 10.868-26.438 13.75-9.5691 1.5937-17.616-1.9729-25.188-6.875-7.4943-4.8521-14.522-11.013-22.219-14.781-4.4252-1.7808-8.8055-2.4421-13.125-2.3438z" fill="url(#c)"/>
                    <path d="m157.39 466.22-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                    <path d="m175.77 504.13c0 10.452-8.473 18.925-18.925 18.925s-18.925-8.473-18.925-18.925 8.4729-18.925 18.925-18.925 18.925 8.473 18.925 18.925z" fill="#644600"/>
                    <path d="m173.18 504.13c0 9.0202-7.3123 16.332-16.332 16.332s-16.332-7.3123-16.332-16.332 7.3123-16.332 16.332-16.332 16.332 7.3123 16.332 16.332z" fill="#ffd543"/>
                    <path d="m153.27 500.23c-2.7865 1.7001-6.0116 1.4858-7.2035-0.47854s0.10072-4.935 2.8872-6.6351 6.0116-1.4858 7.2035 0.47854-0.10071 4.935-2.8872 6.6351z" fill="#fff0b9"/>
                    <path d="m156.79 493.23c-0.74528-1.2283-2.1047-1.8669-3.5872-1.9654s-3.1231 0.31939-4.6382 1.2438-2.6392 2.1933-3.2334 3.5589-0.65346 2.8697 0.0918 4.098 2.1131 1.8807 3.5956 1.9792 3.1231-0.3194 4.6382-1.2438 2.6392-2.1933 3.2334-3.5589 0.6451-2.8835-0.10018-4.1118zm-1.2798 0.78085c0.44663 0.73608 0.45216 1.7012 1e-3 2.737s-1.361 2.0955-2.6324 2.8712-2.642 1.1077-3.7666 1.033-1.963-0.53161-2.4097-1.2677-0.45755-1.679-7e-3 -2.7148 1.3748-2.1039 2.6462-2.8796 2.6283-1.0993 3.7529-1.0246 1.9684 0.50943 2.4151 1.2455z" fill="#644600"/>
                    <g transform="translate(-64.884 -9.391)">
                        <path d="m327.31 478.7-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                        <path d="m341.66 511.84c0 8.4271-6.8315 15.259-15.259 15.259s-15.259-6.8315-15.259-15.259 6.8315-15.259 15.259-15.259 15.259 6.8315 15.259 15.259z" fill="#640000"/>
                        <path d="m339.57 511.84c0 7.2727-5.8957 13.168-13.168 13.168s-13.168-5.8957-13.168-13.168 5.8957-13.168 13.168-13.168 13.168 5.8957 13.168 13.168z" fill="#cc0001"/>
                        <path d="m323.52 508.7c-2.2466 1.3707-4.847 1.198-5.808-0.38584s0.0812-3.979 2.3278-5.3497 4.847-1.198 5.808 0.38584-0.0812 3.979-2.3278 5.3497z" fill="#fabdbd"/>
                        <path d="m326.36 503.05c-0.60089-0.99033-1.697-1.5052-2.8923-1.5846s-2.5181 0.25751-3.7396 1.0028-2.1279 1.7684-2.607 2.8694-0.52686 2.3138 0.074 3.3041 1.7037 1.5163 2.899 1.5958 2.5181-0.25752 3.7396-1.0028 2.1279-1.7684 2.607-2.8694 0.52013-2.3249-0.0808-3.3152zm-1.0319 0.62958c0.36011 0.59348 0.36456 1.3716 8.1e-4 2.2068s-1.0974 1.6895-2.1225 2.315-2.1302 0.89313-3.0369 0.83289-1.5827-0.42862-1.9428-1.0221-0.36891-1.3537-6e-3 -2.1889 1.1084-1.6963 2.1336-2.3217 2.1191-0.88636 3.0258-0.82612 1.5871 0.41074 1.9472 1.0042z" fill="#640000"/>
                    </g>
                    <path d="m396.24 466.97-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                    <path d="m414.62 504.87c0 10.452-8.473 18.925-18.925 18.925s-18.925-8.473-18.925-18.925 8.4729-18.925 18.925-18.925 18.925 8.473 18.925 18.925z" fill="#132c51"/>
                    <path d="m412.03 504.87c0 9.0202-7.3123 16.332-16.332 16.332s-16.332-7.3123-16.332-16.332 7.3123-16.332 16.332-16.332 16.332 7.3123 16.332 16.332z" fill="#3466a5"/>
                    <path d="m392.12 500.98c-2.7865 1.7001-6.0116 1.4858-7.2035-0.47854s0.10072-4.935 2.8872-6.6351 6.0116-1.4858 7.2035 0.47854-0.10071 4.935-2.8872 6.6351z" fill="#cbdbed"/>
                    <path d="m395.64 493.97c-0.74528-1.2283-2.1047-1.8669-3.5872-1.9654s-3.1231 0.31939-4.6382 1.2438-2.6392 2.1933-3.2334 3.5589-0.65346 2.8697 0.0918 4.098 2.1131 1.8807 3.5956 1.9792 3.1231-0.3194 4.6382-1.2438 2.6392-2.1933 3.2334-3.5589 0.6451-2.8835-0.10018-4.1118zm-1.2798 0.78085c0.44663 0.73608 0.45216 1.7012 1e-3 2.737s-1.361 2.0955-2.6324 2.8712-2.642 1.1077-3.7666 1.033-1.963-0.53161-2.4097-1.2677-0.45755-1.679-7e-3 -2.7148 1.3748-2.1039 2.6462-2.8796 2.6283-1.0993 3.7529-1.0246 1.9684 0.50943 2.4151 1.2455z" fill="#132c51"/>
                    <path d="m291.44 398.97c-8.3242-0.0686-16.564 1.5817-23.75 5.4062-6.4718 4.4844-14.383 5.8398-22.406 5.4375-7.8847-0.39533-15.88-2.4829-22.812-5-11.352-5.298-24.993-7.3757-37.812-4.5-9.2419 1.6235-17.742 4.9811-25.625 8.9688-2.0266 4.1425-4.1026 8.2487-6.3438 12.281-4.785 8.6099-10.186 16.968-16.75 25-6.0002 7.3418-12.984 14.413-21.344 21.188-2.6456 3.6485-3.3792 6.3325-3.25 7.7812 0.13215 1.482 0.72818 2.3246 2.6562 3.2812 3.8305 1.9006 12.825 2.0387 22.562-1.375l0.0625-0.0312c8.1892-3.3619 17.093-8.6558 26.656-12.25 9.5871-3.6031 20.198-5.4349 31-1.0625l0.25 0.125c8.0921 3.9857 14.983 10.105 21.906 14.594 6.847 4.4396 13.348 7.2177 21.125 6 7.9124-2.5782 15.88-8.2591 24.594-12.969 8.7924-4.7523 18.822-8.4503 30.125-5.3438l0.0937 0.0312c10.493 2.6238 19.544 8.7172 28.312 11.812 0.22814 0.0832 0.44787 0.18781 0.65625 0.3125 8.7749 5.0965 17.239 10.26 26.25 13.844 7.7485 1.192 14.211-1.573 21.031-6 6.915-4.4885 13.813-10.608 21.906-14.594 0.0818-0.0447 0.16518-0.0864 0.25-0.125 10.802-4.3724 21.413-2.5406 31 1.0625 9.5635 3.5942 18.467 8.8881 26.656 12.25l0.0625 0.0312c9.7393 3.4143 18.733 3.2698 22.562 1.375 1.9276-0.95372 2.5244-1.7724 2.6562-3.25 0.12893-1.4444-0.60414-4.1324-3.25-7.7812-8.3705-6.7836-15.34-13.862-21.344-21.219-6.5667-8.0457-11.964-16.406-16.75-25.031-3.9425-7.1058-7.4626-14.413-10.875-21.844-6.162-3.128-11.937-6.6268-19.062-5.7812-16.033 4.2928-5.9515 24.794-23.812 26.906-10.478-1.3537-19.959-4.7401-29.094-8.7812-9.3343-4.1294-18.31-8.9482-27.625-12.938-7.884-4.2512-17.35-7.0585-26.906-7.6875-1.1893-0.0783-2.3733-0.1152-3.5625-0.125z" fill="url(#d)"/>
                    <g transform="translate(-143.44 -87.131)">
                        <path d="m327.31 478.7-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                        <path d="m341.66 511.84c0 8.4271-6.8315 15.259-15.259 15.259s-15.259-6.8315-15.259-15.259 6.8315-15.259 15.259-15.259 15.259 6.8315 15.259 15.259z" fill="#3b2242"/>
                        <path d="m339.57 511.84c0 7.2727-5.8957 13.168-13.168 13.168s-13.168-5.8957-13.168-13.168 5.8957-13.168 13.168-13.168 13.168 5.8957 13.168 13.168z" fill="#75507b"/>
                        <path d="m323.52 508.7c-2.2466 1.3707-4.847 1.198-5.808-0.38584s0.0812-3.979 2.3278-5.3497 4.847-1.198 5.808 0.38584-0.0812 3.979-2.3278 5.3497z" fill="#e4d4e2"/>
                        <path d="m326.36 503.05c-0.60089-0.99033-1.697-1.5052-2.8923-1.5846s-2.5181 0.25751-3.7396 1.0028-2.1279 1.7684-2.607 2.8694-0.52686 2.3138 0.074 3.3041 1.7037 1.5163 2.899 1.5958 2.5181-0.25752 3.7396-1.0028 2.1279-1.7684 2.607-2.8694 0.52013-2.3249-0.0808-3.3152zm-1.0319 0.62958c0.36011 0.59348 0.36456 1.3716 8.1e-4 2.2068s-1.0974 1.6895-2.1225 2.315-2.1302 0.89313-3.0369 0.83289-1.5827-0.42862-1.9428-1.0221-0.36891-1.3537-6e-3 -2.1889 1.1084-1.6963 2.1336-2.3217 2.1191-0.88636 3.0258-0.82612 1.5871 0.41074 1.9472 1.0042z" fill="#3b2242"/>
                    </g>
                    <g transform="translate(-13.882 -88.1)">
                        <path d="m327.31 478.7-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                        <path d="m341.66 511.84c0 8.4271-6.8315 15.259-15.259 15.259s-15.259-6.8315-15.259-15.259 6.8315-15.259 15.259-15.259 15.259 6.8315 15.259 15.259z" fill="#644600"/>
                        <path d="m339.57 511.84c0 7.2727-5.8957 13.168-13.168 13.168s-13.168-5.8957-13.168-13.168 5.8957-13.168 13.168-13.168 13.168 5.8957 13.168 13.168z" fill="#ffd543"/>
                        <path d="m323.52 508.7c-2.2466 1.3707-4.847 1.198-5.808-0.38584s0.0812-3.979 2.3278-5.3497 4.847-1.198 5.808 0.38584-0.0812 3.979-2.3278 5.3497z" fill="#fff0b9"/>
                        <path d="m326.36 503.05c-0.60089-0.99033-1.697-1.5052-2.8923-1.5846s-2.5181 0.25751-3.7396 1.0028-2.1279 1.7684-2.607 2.8694-0.52686 2.3138 0.074 3.3041 1.7037 1.5163 2.899 1.5958 2.5181-0.25752 3.7396-1.0028 2.1279-1.7684 2.607-2.8694 0.52013-2.3249-0.0808-3.3152zm-1.0319 0.62958c0.36011 0.59348 0.36456 1.3716 8.1e-4 2.2068s-1.0974 1.6895-2.1225 2.315-2.1302 0.89313-3.0369 0.83289-1.5827-0.42862-1.9428-1.0221-0.36891-1.3537-6e-3 -2.1889 1.1084-1.6963 2.1336-2.3217 2.1191-0.88636 3.0258-0.82612 1.5871 0.41074 1.9472 1.0042z" fill="#644600"/>
                    </g>
                    <path d="m218.19 320.06c-6.9608-0.15996-14.479 2.2886-23.188 9.2188-4.0591 3.9415-10.431 7.0085-16.938 8.2812-0.73701 1.6921-1.4983 3.3819-2.2812 5.0625-4.4384 9.5269-9.6616 18.819-16.094 27.562-6.1107 8.3067-13.315 16.112-22 23.094-1.0897 1.8291-1.1565 3.2169-0.59375 4.6875 0.58751 1.5354 2.0416 3.2003 4.1562 4.5625 4.1949 2.7022 10.757 3.9284 15.531 2.375 8.9665-4.959 18.927-9.4605 30.062-11.438l0.125-0.0312c12.808-2.8402 26.252-0.76741 37.531 4.4375v-0.0312c6.2977 2.2868 13.481 4.1256 20.438 4.5312 7.3564 0.42898 14.46-0.74332 20.062-4.625 0.0908-0.0573 0.18466-0.10945 0.28125-0.15625 8.3264-4.4314 17.862-5.9851 27.281-5.4062 9.5492 0.58678 18.979 3.3654 26.906 7.5938l0.25 0.125c8.7845 3.7784 17.151 8.1803 25.688 11.969 8.5995 3.8163 17.372 7.01 26.969 8.3125 3.4364-0.46796 5.1311-1.5605 6.375-3.125 1.2871-1.6188 2.103-4.004 2.9062-6.7812s1.6156-5.9095 3.4375-8.8438 4.8347-5.5282 9.2812-6.7188c0.13375-0.0305 0.26952-0.0514 0.40625-0.0625 7.7126-0.91511 13.784 2.7218 19.406 5.5938 5.5955 2.8585 10.688 5.0914 17.656 3.5625 3.1039-1.0746 4.1854-2.163 4.25-2.1875-0.0112-0.0208-0.0122-0.0381-0.0625-0.15625-0.14239-0.33426-0.56795-1.007-1.3125-1.8125-2.9782-3.222-10.378-8.3364-18.031-15.438-0.0541-0.0501-0.10619-0.10219-0.15625-0.15625-5.852-6.4332-10.067-11.979-13.219-16.906-4.9229-7.6965-7.2562-13.862-9.2188-19.375-1.1824-3.3214-2.213-6.3687-3.625-9.4688-4.8042-0.84687-9.5479-2.3128-13.594-4.4375-9.3797-4.7232-19.778-6.2399-29.875-4.9062-10.063 1.3293-19.817 5.4981-27.875 12.094-9.6308 5.4227-20.113 6.5276-30.531 5.25-10.368-1.2713-20.668-4.8956-30.062-9-11.191-4.5568-20.779-12.236-31.125-15.594-2.9829-0.96792-6.0548-1.5835-9.2188-1.6562zm217.91 81.562c0.0204 0.038 0.0201-3e-3 0.0312-0.0312l-0.0312 0.0312z" fill="url(#e)"/>
                    <path d="m363.52 320.32-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                    <path d="m381.9 358.22c0 10.452-8.473 18.925-18.925 18.925s-18.925-8.473-18.925-18.925 8.4729-18.925 18.925-18.925 18.925 8.473 18.925 18.925z" fill="#640000"/>
                    <path d="m379.31 358.22c0 9.0202-7.3123 16.332-16.332 16.332s-16.332-7.3123-16.332-16.332 7.3123-16.332 16.332-16.332 16.332 7.3123 16.332 16.332z" fill="#cc0001"/>
                    <path d="m359.4 354.33c-2.7865 1.7001-6.0116 1.4858-7.2035-0.47854s0.10072-4.935 2.8872-6.6351 6.0116-1.4858 7.2035 0.47854-0.10071 4.935-2.8872 6.6351z" fill="#fabdbd"/>
                    <path d="m362.93 347.32c-0.74528-1.2283-2.1047-1.8669-3.5872-1.9654s-3.1231 0.31939-4.6382 1.2438-2.6392 2.1933-3.2334 3.5589-0.65346 2.8697 0.0918 4.098 2.1131 1.8807 3.5956 1.9792 3.1231-0.3194 4.6382-1.2438 2.6392-2.1933 3.2334-3.5589 0.6451-2.8835-0.10018-4.1118zm-1.2798 0.78085c0.44663 0.73608 0.45216 1.7012 1e-3 2.737s-1.361 2.0955-2.6324 2.8712-2.642 1.1077-3.7666 1.033-1.963-0.53161-2.4097-1.2677-0.45755-1.679-7e-3 -2.7148 1.3748-2.1039 2.6462-2.8796 2.6283-1.0993 3.7529-1.0246 1.9684 0.50943 2.4151 1.2455z" fill="#640000"/>
                    <g transform="translate(18.729 8.1939)">
                        <path d="m227.95 312.07-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                        <g transform="translate(-99.356 -166.63)">
                        <path d="m341.66 511.84c0 8.4271-6.8315 15.259-15.259 15.259s-15.259-6.8315-15.259-15.259 6.8315-15.259 15.259-15.259 15.259 6.8315 15.259 15.259z" fill="#132c51"/>
                        <path d="m339.57 511.84c0 7.2727-5.8957 13.168-13.168 13.168s-13.168-5.8957-13.168-13.168 5.8957-13.168 13.168-13.168 13.168 5.8957 13.168 13.168z" fill="#3466a5"/>
                        <path d="m323.52 508.7c-2.2466 1.3707-4.847 1.198-5.808-0.38584s0.0812-3.979 2.3278-5.3497 4.847-1.198 5.808 0.38584-0.0812 3.979-2.3278 5.3497z" fill="#cbdbed"/>
                        <path d="m326.36 503.05c-0.60089-0.99033-1.697-1.5052-2.8923-1.5846s-2.5181 0.25751-3.7396 1.0028-2.1279 1.7684-2.607 2.8694-0.52686 2.3138 0.074 3.3041 1.7037 1.5163 2.899 1.5958 2.5181-0.25752 3.7396-1.0028 2.1279-1.7684 2.607-2.8694 0.52013-2.3249-0.0808-3.3152zm-1.0319 0.62958c0.36011 0.59348 0.36456 1.3716 8.1e-4 2.2068s-1.0974 1.6895-2.1225 2.315-2.1302 0.89313-3.0369 0.83289-1.5827-0.42862-1.9428-1.0221-0.36891-1.3537-6e-3 -2.1889 1.1084-1.6963 2.1336-2.3217 2.1191-0.88636 3.0258-0.82612 1.5871 0.41074 1.9472 1.0042z" fill="#132c51"/>
                        </g>
                    </g>
                    <path d="m247.91 239.62c-0.58222 7e-3 -1.1894 0.0276-1.8125 0.0625-17.37 3.9247-15.054 6.4122-25.844 13.406-6.671 3.1867-12.998 4.793-18.344 5.0312-1.4897 3.6142-2.9729 7.2236-4.8438 10.625-4.8414 8.8023-10.154 17.329-15.938 25.5-5.8025 8.198-12.087 16.034-18.875 23.406 0.17633 4.2185 1.5197 6.9408 3.5938 8.7812 2.2138 1.9644 5.4266 3.0187 9.125 3.1875 7.3969 0.33766 16.502-3.1054 21.156-7.625 0.0496-0.0545 0.10175-0.10666 0.15625-0.15625 12.751-10.147 23.799-10.509 33.531-7.0312s18.355 10.273 27.969 14.188h0.0625c8.5373 3.7299 17.757 6.967 26.938 8.1562 9.4349 1.2223 18.828 0.28137 27.375-4.5312 7.8454-6.3286 17.274-10.31 27.031-11.562 9.7659-1.2536 19.862 0.22652 28.969 4.8125l0.0312 0.0312c8.1562 4.2832 20.096 5.5696 28.031 4 3.9678-0.7848 6.7965-2.3353 7.7812-3.7812 0.49236-0.72298 0.64299-1.3677 0.5-2.3438-0.13993-0.95513-0.68381-2.2881-1.9062-3.875-8.4954-8.0003-15.39-15.106-21.188-21.781-7.4257-8.5502-13.044-16.376-18.031-24.406-3.7916-6.1054-7.2321-12.343-10.75-19.094-1.785 0.74156-3.6111 1.2695-5.4688 1.5625-6.3981 1.0091-13.07-0.71327-18.906-5.5938-5.3029-4.8798-12.861-5.927-21.812-4.8438-6.7945 0.8223-14.394 2.8658-22.406 5.4375-9.9318 0.53226-14.381-2.6963-18.938-5.875-4.1869-2.921-8.4542-5.7985-17.188-5.6875z" fill="url(#f)"/>
                    <g transform="translate(-30.025 -258.86)">
                        <path d="m343.07 490.25-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                        <path d="m357.42 523.39c0 8.4271-6.8315 15.259-15.259 15.259s-15.259-6.8315-15.259-15.259 6.8315-15.259 15.259-15.259 15.259 6.8315 15.259 15.259z" fill="#3b2242"/>
                        <path d="m355.33 523.39c0 7.2727-5.8957 13.168-13.168 13.168s-13.168-5.8957-13.168-13.168 5.8957-13.168 13.168-13.168 13.168 5.8957 13.168 13.168z" fill="#75507b"/>
                        <path d="m339.28 520.25c-2.2466 1.3707-4.847 1.198-5.808-0.38584s0.0812-3.979 2.3278-5.3497 4.847-1.198 5.808 0.38583-0.0812 3.979-2.3278 5.3497z" fill="#e4d4e2"/>
                        <path d="m342.12 514.6c-0.60089-0.99033-1.697-1.5052-2.8923-1.5846s-2.5181 0.25751-3.7396 1.0028-2.1279 1.7684-2.607 2.8694-0.52686 2.3138 0.074 3.3041 1.7037 1.5163 2.899 1.5958 2.5181-0.25752 3.7396-1.0028 2.1279-1.7684 2.607-2.8694 0.52013-2.3249-0.0808-3.3152zm-1.0319 0.62957c0.36011 0.59348 0.36456 1.3716 8.1e-4 2.2068s-1.0974 1.6895-2.1225 2.315-2.1302 0.89313-3.0369 0.83289-1.5827-0.42862-1.9428-1.0221-0.36891-1.3537-6e-3 -2.1889 1.1084-1.6963 2.1336-2.3217 2.1191-0.88636 3.0258-0.82612 1.5871 0.41074 1.9472 1.0042z" fill="#3b2242"/>
                    </g>
                    <g transform="translate(-128.66 -248.01)">
                        <path d="m343.07 490.25-2.6498 0.077 0.84793 20.081 1.275-0.077 0.52692-20.081z" fill="#312c29"/>
                        <path d="m357.42 523.39c0 8.4271-6.8315 15.259-15.259 15.259s-15.259-6.8315-15.259-15.259 6.8315-15.259 15.259-15.259 15.259 6.8315 15.259 15.259z" fill="#640000"/>
                        <path d="m355.33 523.39c0 7.2727-5.8957 13.168-13.168 13.168s-13.168-5.8957-13.168-13.168 5.8957-13.168 13.168-13.168 13.168 5.8957 13.168 13.168z" fill="#cc0001"/>
                        <path d="m339.28 520.25c-2.2466 1.3707-4.847 1.198-5.808-0.38584s0.0812-3.979 2.3278-5.3497 4.847-1.198 5.808 0.38583-0.0812 3.979-2.3278 5.3497z" fill="#fabdbd"/>
                        <path d="m342.12 514.6c-0.60089-0.99033-1.697-1.5052-2.8923-1.5846s-2.5181 0.25751-3.7396 1.0028-2.1279 1.7684-2.607 2.8694-0.52686 2.3138 0.074 3.3041 1.7037 1.5163 2.899 1.5958 2.5181-0.25752 3.7396-1.0028 2.1279-1.7684 2.607-2.8694 0.52013-2.3249-0.0808-3.3152zm-1.0319 0.62957c0.36011 0.59348 0.36456 1.3716 8.1e-4 2.2068s-1.0974 1.6895-2.1225 2.315-2.1302 0.89313-3.0369 0.83289-1.5827-0.42862-1.9428-1.0221-0.36891-1.3537-6e-3 -2.1889 1.1084-1.6963 2.1336-2.3217 2.1191-0.88636 3.0258-0.82612 1.5871 0.41074 1.9472 1.0042z" fill="#640000"/>
                    </g>
                    <path d="m281.18 112.61c-2.7981 0.44781-5.8974 3.4938-9.0938 8.9688s-6.4491 13.076-10.094 21.656c-3.7659 8.8655-7.9663 18.772-13.131 28.53-4.8321 9.1305-10.508 18.132-17.463 26.032-4.8852 5.558-9.1147 10.671-13.358 15.798-4.2199 5.099-8.4539 10.213-13.36 15.796l-0.0625 0.0625c-4.3276 4.5339-6.2253 8.3322-6.5625 10.938s0.48765 4.1052 2.5625 5.375c4.1375 2.5322 13.99 2.4716 24.906-2.4375 4.6514-2.8732 6.4747-4.8298 9.375-6.6875 2.9349-1.8799 6.7095-3.3433 14.75-5.0625 0.10242-0.0288 0.20689-0.0496 0.3125-0.0625 9.6403-0.51057 14.623 2.5556 18.75 5.2812 4.1041 2.7103 7.3901 5.0552 15.812 4.6562 8.402-2.5392 16.359-4.5487 23.469-4.9688 7.1752-0.42387 13.633 0.80691 18.438 4.9375 7e-3 6e-3 0.0241-6e-3 0.0312 0l0.0625 0.0625c9.6403 7.5565 21.546 5.4483 29.625-3.8125 1.9079-3.3054 3.0054-7.6204 2.8125-11.688-0.19558-4.1244-1.6389-7.8768-4.5312-10.375-0.0328-0.0405-0.064-0.0822-0.0937-0.125-8.1293-8.2002-15.579-16.882-22.359-25.96-6.882-9.2138-13.075-18.836-18.592-28.78-5.5649-10.03-10.442-20.387-14.642-30.979l-0.0625-0.15625c-2.138-4.2183-4.1679-8.8732-6.8438-12.188-2.6825-3.3225-5.6705-5.3096-10.656-4.8125" fill="url(#g)"/>
                    <path d="m322.54 153.14c-8.9 5.609-28.42-19.477-38.917-20.171s-33.147 21.607-41.232 14.876 9.7416-33.048 7.1574-43.245-30.792-24.848-26.889-34.617 34.44-0.94741 43.34-6.5565 14.117-36.964 24.614-36.27 11.544 32.462 19.628 39.193 39.517 2.0033 42.101 12.201-27.306 21.01-31.209 30.779 10.306 38.202 1.4062 43.811z" fill="#a07d00"/>
                    <path d="m316.42 142.55c-7.309 4.6063-23.339-15.995-31.96-16.565s-27.222 17.744-33.861 12.216 8.0002-27.14 5.8779-35.514-25.288-20.406-22.082-28.429 28.284-0.77805 35.593-5.3844 11.593-30.356 20.214-29.786 9.4801 26.659 16.12 32.187 32.453 1.6452 34.575 10.02-22.425 17.254-25.63 25.277 8.4638 31.373 1.1548 35.979z" fill="url(#h)"/>
                    </g>
                </svg>
                
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_code

def generate_section_header_slide_17(
    section_title="PROJECT SCHEDULE",
    section_subtitle="You could enter a subtitle here if you need it",
    bg_color="#f5f3ed",
    title_color="#d4af6a",
    subtitle_color="#7a8288",
    circle_left_color="#e8b558",
    circle_right_color="#d9653b",
    bar_color="#6b7f82"
):
    """
    Generate a section header slide with centered title, subtitle, decorative circles at corners, and horizontal bars.
    
    Parameters:
    - section_title: Section title text in uppercase
    - section_subtitle: Section subtitle text below main title
    - bg_color: Background color
    - title_color: Color for main title
    - subtitle_color: Color for subtitle text
    - circle_left_color: Color for top-left corner circle
    - circle_right_color: Color for bottom-right corner circle
    - bar_color: Color for horizontal decorative bars
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Schedule Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Montserrat', sans-serif;
            background-color: {bg_color};
            overflow: hidden;
        }}
        
        .slide-wrapper {{
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            background-color: {bg_color};
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        
        /* Decorative circles */
        .circle-left {{
            position: absolute;
            width: 550px;
            height: 550px;
            border-radius: 50%;
            background-color: {circle_left_color};
            top: -275px;
            left: -275px;
        }}
        
        .circle-right {{
            position: absolute;
            width: 550px;
            height: 550px;
            border-radius: 50%;
            background-color: {circle_right_color};
            bottom: -275px;
            right: -275px;
        }}
        
        /* Horizontal bars */
        .bar-top {{
            position: absolute;
            width: 780px;
            height: 35px;
            background-color: {bar_color};
            top: 85px;
            right: 0;
        }}
        
        .bar-bottom {{
            position: absolute;
            width: 780px;
            height: 35px;
            background-color: {bar_color};
            bottom: 200px;
            left: 115px;
        }}
        
        /* Content */
        .content {{
            position: relative;
            z-index: 10;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }}
        
        .main-title {{
            font-size: 110px;
            font-weight: 700;
            color: {title_color};
            letter-spacing: 8px;
            line-height: 1.1;
            margin-bottom: 20px;
            text-transform: uppercase;
        }}
        
        .subtitle {{
            font-size: 42px;
            font-weight: 400;
            color: {subtitle_color};
            max-width: 1100px;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="slide-wrapper">
        <div class="slide-container">
            <!-- Decorative elements -->
            <div class="circle-left"></div>
            <div class="circle-right"></div>
            <div class="bar-top"></div>
            <div class="bar-bottom"></div>
            
            <!-- Main content -->
            <div class="content">
                <div class="main-title">{section_title}</div>
                <div class="subtitle">{section_subtitle}</div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_section_header_slide_18(
    section_title="Main Title Here",
    section_subtitle="You could enter a subtitle here if you need it",
    bg_color="#f5f5f0",
    title_color="#E8B44F",
    subtitle_color="#666666",
    circle_blue="#6B9FBD",
    circle_yellow="#E8B44F",
    circle_teal="#6FBAAA"
):
    """
    Generate a minimalist section header slide with centered title, subtitle, and decorative circles at corners.
    
    Parameters:
    - section_title: Section title text for the section
    - section_subtitle: Section subtitle or description text
    - bg_color: Background color
    - title_color: Color for the main title text
    - subtitle_color: Color for the subtitle text
    - circle_blue: Color for blue decorative circles
    - circle_yellow: Color for yellow decorative circles
    - circle_teal: Color for teal decorative circles
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Section Slide - {section_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Montserrat', sans-serif;
            overflow: hidden;
            width: 1920px;
            height: 1080px;
            margin: 0;
            padding: 0;
            background-color: {bg_color};
            position: relative;
        }}
        
        /* Top-left circles - partially visible */
        .circle-group-top {{
            position: absolute;
            top: -60px;
            left: -60px;
            display: flex;
            gap: 10px;
        }}
        
        .circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
        }}
        
        .circle-blue {{
            background-color: {circle_blue};
        }}
        
        .circle-yellow {{
            background-color: {circle_yellow};
        }}
        
        .circle-teal {{
            background-color: {circle_teal};
        }}
        
        /* Bottom-right circles - partially visible */
        .circle-group-bottom {{
            position: absolute;
            bottom: -60px;
            right: -60px;
            display: flex;
            gap: 10px;
        }}
        
        /* Content */
        .content {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 10;
            max-width: 1400px;
        }}
        
        .main-title {{
            font-size: 90px;
            font-weight: 700;
            color: {title_color};
            line-height: 1.1;
            margin-bottom: 30px;
            letter-spacing: 2px;
        }}
        
        .subtitle {{
            font-size: 36px;
            font-weight: 400;
            color: {subtitle_color};
            line-height: 1.4;
        }}
        
    </style>
</head>
<body>
            <!-- Top-left decorative circles -->
            <div class="circle-group-top">
                <div class="circle circle-blue"></div>
                <div class="circle circle-yellow"></div>
                <div class="circle circle-teal"></div>
            </div>
            
            <!-- Bottom-right decorative circles -->
            <div class="circle-group-bottom">
                <div class="circle circle-blue"></div>
                <div class="circle circle-yellow"></div>
                <div class="circle circle-teal"></div>
            </div>
            
            <!-- Main content -->
            <div class="content">
                <h1 class="main-title">{section_title}</h1>
                <p class="subtitle">{section_subtitle}</p>
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif"
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
            <div class="icon-wrapper">
                {icon}
            </div>
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
    font_family="'Montserrat', 'Inter', sans-serif",
    bg_color="#F8FAFC",
    accent_panel_color="#6366F1",
    title_color="#FFFFFF",
    card_bg_color="#FFFFFF",
    card_border_color="#E5E7EB",
    list_title_color="#000000",
    list_text_color="#333333"
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
            background: {card_bg_color};
            border-radius: 1rem;
            padding: 2.5rem;
            position: relative;
            overflow: hidden;
            border: 1px solid {card_border_color};
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
    font_family="'Montserrat', 'Inter', sans-serif",
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
    font_family="'Montserrat', 'Inter', sans-serif",
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
    font_family="'Montserrat', 'Inter', sans-serif",
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



# def generate_business_overview_slide(
#     main_title="BUSINESS OVERVIEW",
#     sections=[
#         {
#             "icon": "chart-analysis",
#             "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
#         },
#         {
#             "icon": "innovation",
#             "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
#         },
#         {
#             "icon": "growth",
#             "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
#         }
#     ],
#     left_bg_color="#1a4b8c",
#     right_bg_color="#f8f9fa",
#     title_color="#FFFFFF",
#     icon_bg_color="#2a3f6b",
#     icon_color="#FFFFFF",
#     content_bg_color="#FFFFFF",
#     content_text_color="#1a4b8c",
#     font_family="'Inter', sans-serif",
#     show_border=False,
#     border_opacity=0.25,
#     section_spacing="30px",
#     icon_size="110px",
#     custom_css=""
# ):
#     """
#     Generate a professional business overview slide with icon-content sections layout.

#     :param main_title: Main title text (10-25 characters), displayed on the left side
#     :param sections: List of dictionaries with icon and content for each section,
#                     or list of lists where first element is content and second is icon
#     :param left_bg_color: Background color for the left title section (hex code)
#     :param right_bg_color: Background color for the right content area (hex code)
#     :param title_color: Color of the main title text (hex code)
#     :param icon_bg_color: Background color for icon containers (hex code)
#     :param icon_color: Color of the icons (hex code)
#     :param content_bg_color: Background color for content text areas (hex code)
#     :param content_text_color: Text color for content sections (hex code)
#     :param title_font_size: Font size for the main title
#     :param content_font_size: Font size for section content text
#     :param font_family: Font family for all text elements
#     :param show_border: Whether to show the dashed border frame
#     :param border_opacity: Opacity of the border frame (0.0 to 1.0)
#     :param section_spacing: Vertical spacing between content sections
#     :param icon_size: Size of the icon containers
#     :param custom_css: Additional custom CSS to be included
#     :return: A string containing the HTML code for the slide
#     """

#     # Icon SVG definitions
#     icons = {
#         "chart-analysis": '''<svg viewBox="0 0 24 24" fill="currentColor" width="55" height="55">
#             <path d="M3 3v18h18v-2H5V3H3zm4 14h2V9H7v8zm4 0h2V7h-2v10zm4 0h2v-4h-2v4zm3-12l-3 3-3-3-4 4-1.5-1.5L9 10l3-3 3 3 4-4z"/>
#         </svg>''',
#         "innovation": '''<svg viewBox="0 0 24 24" fill="currentColor" width="55" height="55">
#             <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z"/>
#             <circle cx="12" cy="9" r="1"/>
#             <path d="M12 6v2m0 4v2m-3-3h2m4 0h2"/>
#         </svg>''',
#         "growth": '''<svg viewBox="0 0 24 24" fill="currentColor" width="55" height="55">
#             <path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6h-6z"/>
#             <path d="M5 19h2v2H5zm4 0h2v2H9zm4 0h2v2h-2z"/>
#         </svg>'''
#     }

#     # Generate sections HTML
#     sections_html = ""
#     for i, section in enumerate(sections):
#         # Mới: Kiểm tra section có phải là list hay không và xử lý tương ứng
#         if isinstance(section, list):
#             # Giả định dữ liệu dạng [content, icon]
#             content = section[0] if len(section) > 0 else ""
#             icon_name = section[1] if len(section) > 1 else "chart-analysis"
#             icon_svg = icons.get(icon_name, icons["chart-analysis"])
#         else:
#             # Định dạng dictionary gốc
#             content = section.get("content", "")
#             icon_name = section.get("icon", "chart-analysis")
#             icon_svg = icons.get(icon_name, icons["chart-analysis"])
        
#         sections_html += f'''
#         <div class="content-section">
#             <div class="icon-container">
#                 {icon_svg}
#             </div>
#             <div class="text-container">
#                 {content}
#             </div>
#         </div>
#         '''

#     html_code = f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>{main_title}</title>
#     <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700;900&display=swap" rel="stylesheet">
#     <style>
#         body, html {{
#             margin: 0;
#             padding: 0;
#             height: 100%;
#             width: 100%;
#             font-family: {font_family};
#             overflow: hidden;
#         }}
        
#         .slide-container {{
#             width: 100%;
#             height: 100vh;
#             display: flex;
#             position: relative;
#             background: linear-gradient(135deg, {right_bg_color} 0%, #e9ecef 100%);
#         }}
        
#         .slide-border {{
#             position: absolute;
#             top: 45px;
#             left: 45px;
#             right: 45px;
#             bottom: 45px;
#             border: {("3px dashed rgba(26, 75, 140, " + str(border_opacity) + ")" if show_border else "none")};
#             border-radius: 12px;
#             pointer-events: none;
#             z-index: 5;
#         }}
        
#         .left-section {{
#             width: 40%;
#             background: linear-gradient(135deg, {left_bg_color} 0%, #0d2d5e 100%);
#             color: {title_color};
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             padding: 100px 60px;
#             position: relative;
#             z-index: 10;
#             box-shadow: 8px 0 30px rgba(0, 0, 0, 0.2);
#         }}
        
#         .title {{
#             font-size: 6rem;
#             font-weight: 900;
#             line-height: 1.1;
#             text-align: center;
#             letter-spacing: 0.1em;
#             text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
#             text-transform: uppercase;
#         }}
        
#         .right-section {{
#             width: 60%;
#             padding: 100px 80px;
#             display: flex;
#             flex-direction: column;
#             justify-content: center;
#             gap: 45px;
#             position: relative;
#             z-index: 10;
#         }}
        
#         .content-section {{
#             display: flex;
#             align-items: stretch;
#             box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
#             border-radius: 16px;
#             overflow: hidden;
#             min-height: 140px;
#         }}
        
#         .icon-container {{
#             width: {icon_size};
#             min-width: {icon_size};
#             background: linear-gradient(135deg, {icon_bg_color} 0%, #1a2942 100%);
#             color: {icon_color};
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             padding: 30px;
#         }}
        
#         .icon-container svg {{
#             filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.25));
#         }}
        
#         .text-container {{
#             flex: 1;
#             background: linear-gradient(135deg, {content_bg_color} 0%, #fafbfc 100%);
#             color: {content_text_color};
#             padding: 35px 45px;
#             font-size: 2.5rem;
#             line-height: 1.7;
#             display: flex;
#             align-items: center;
#             font-weight: 500;
#         }}
        
#         /* Decorative elements */
#         .left-section::before {{
#             content: '';
#             position: absolute;
#             top: 0;
#             right: -35px;
#             width: 70px;
#             height: 100%;
#             background: linear-gradient(90deg, transparent 0%, {left_bg_color} 50%, transparent 100%);
#             z-index: -1;
#             opacity: 0.6;
#         }}
        
#         .left-section::after {{
#             content: '';
#             position: absolute;
#             top: 50%;
#             left: 50%;
#             transform: translate(-50%, -50%);
#             width: 130%;
#             height: 130%;
#             background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
#             pointer-events: none;
#         }}
        
#         @media (max-width: 768px) {{
#             .slide-container {{
#                 flex-direction: column;
#             }}
            
#             .left-section, .right-section {{
#                 width: 100%;
#             }}
            
#             .left-section {{
#                 height: 30%;
#                 padding: 30px 20px;
#             }}
            
#             .right-section {{
#                 height: 70%;
#                 padding: 30px 20px;
#             }}
            
#             .title {{
#                 font-size: 2.5rem;
#             }}
            
#             .content-section {{
#                 margin-bottom: 10px !important;
#             }}
            
#             .icon-container {{
#                 width: 60px;
#                 min-width: 60px;
#                 padding: 15px;
#             }}
            
#             .icon-container svg {{
#                 width: 30px;
#                 height: 30px;
#             }}
            
#             .text-container {{
#                 padding: 15px 20px;
#                 font-size: 0.85rem;
#             }}
#         }}
        
#         @media (max-width: 480px) {{
#             .slide-border {{
#                 top: 15px;
#                 left: 15px;
#                 right: 15px;
#                 bottom: 15px;
#             }}
            
#             .title {{
#                 font-size: 2rem;
#             }}
            
#             .text-container {{
#                 font-size: 0.8rem;
#                 padding: 12px 15px;
#             }}
#         }}
        
#         {custom_css}
#     </style>
# </head>
# <body>
#     <div class="slide-container">
#         <!-- Border frame -->
#         <div class="slide-border"></div>
        
#         <!-- Left section with title -->
#         <div class="left-section">
#             <h1 class="title">{main_title}</h1>
#         </div>
        
#         <!-- Right section with content -->
#         <div class="right-section">
#             {sections_html}
#         </div>
#     </div>
# </body>
# </html>"""

#     return html_code



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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Nunito', 'Inter', sans-serif",
    sky_top_color="#ABB0EA",
    sky_bottom_color="#A2CFED",
    grid_dot_color="rgba(0, 0, 0, 0.05)",
    text_color="#1F2937",
    accent_color="#6366F1",
    font_size_multiplier=1.0,
    title_font_size=None,
    list_item_font_size=None,
    concluding_text_font_size=None,
    custom_css="",
    **kwargs
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
    font_family="'Montserrat', 'Inter', sans-serif",
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
    font_family="'Poppins', 'Inter', sans-serif",
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
    font_family="'Poppins', 'Inter', sans-serif",
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
    font_family="'Poppins', 'Inter', sans-serif",
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
    font_family="'Poppins', 'Inter', sans-serif",
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
    font_family="'Poppins', 'Inter', sans-serif",
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


def generate_company_mission_slide(
    main_title="OUR COMPANY OUR COMPANY OUR COMPANY OUR COMPANY",
    mission_items=[
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore"
    ],
    title_color="#000000",
    panel_bg_color="#0052CC",
    panel_text_color="#FFFFFF",
    number_bg_color="#E8E8E8",
    number_text_color="#000000",
    accent_bar_color="#0052CC",
    bg_color="#F5F5F5",
):
    """
    Generate a company mission slide with customizable numbered items.
    
    Parameters:
    - main_title: Main title text (default: "OUR COMPANY")
    - mission_items: List of mission item texts (default: 6 items with Lorem ipsum)
    - title_color: Color for main title
    - subtitle_color: Color for subtitle
    - panel_bg_color: Background color for right panel
    - panel_text_color: Text color inside panel
    - number_bg_color: Background color for number circles
    - number_text_color: Text color for numbers
    - accent_bar_color: Color for bottom accent bar
    - bg_color: Background color for slide
    - custom_css: Additional custom CSS
    
    Returns:
    - HTML code for the company mission slide
    """
    
    # Generate mission items HTML
    mission_items_html = ""
    for idx, item in enumerate(mission_items, 1):
        mission_items_html += f"""
        <div class="mission-item">
            <div class="number-circle">{idx}</div>
            <div class="mission-text">{item}</div>
        </div>
        """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Company Mission Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Arial', sans-serif;
            background-color: {bg_color};
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}

        .slide-wrapper {{
            width: 1920px;
            height: 1080px;
            background-color: {bg_color};
            position: relative;
            transform-origin: top left;
        }}

        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            gap: 60px;
            padding: 100px 0px 100px 80px;
        }}

        .left-section {{
            flex: 0 0 35%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 60px;
        }}

        .title-section {{
            margin-bottom: 20px;
        }}

        .main-title {{
            font-size: 64px;
            font-weight: 700;
            color: {title_color};
            letter-spacing: 3px;
            margin-bottom: 8px;
            line-height: 1.2;
        }}

        .left-text {{
            font-size: 24px;
            line-height: 1.7;
            color: {title_color};
            max-width: 600px;
            opacity: 0.9;
        }}

        .accent-bar {{
            width: 180px;
            height: 14px;
            background-color: {accent_bar_color};
            margin-top: 20px;
            border-radius: 2px;
        }}

        .right-section {{
            flex: 1;
            position: relative;
            display: flex;
            align-items: center;
        }}

        .mission-panel {{
            background-color: {panel_bg_color};
            border-radius: 50px 0 0 50px;
            padding: 70px 80px 70px 120px;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 48px;
            position: relative;
            overflow: visible;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        }}

        .mission-item {{
            display: flex;
            align-items: center;
            gap: 35px;
            position: relative;
        }}

        .number-circle {{
            position: absolute;
            left: -100px;
            width: 90px;
            height: 90px;
            background-color: {number_bg_color};
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 52px;
            font-weight: 900;
            color: {number_text_color};
            flex-shrink: 0;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }}

        .mission-text {{
            font-size: 28px;
            line-height: 1.65;
            color: {panel_text_color};
        }}


        @media (max-width: 1920px) {{
            .slide-wrapper {{
                transform: scale(calc(100vw / 1920));
            }}
        }}
    </style>
</head>
<body>
    <div class="slide-wrapper">
        <div class="slide-container">
            <div class="left-section">
                <div class="title-section">
                    <div class="main-title">{main_title}</div>
                </div>
                <div class="accent-bar"></div>
            </div>
            
            <div class="right-section">
                <div class="mission-panel">
                    {mission_items_html}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_methodology_slide(
    title="Methodology Methodology ",
    title_color="#000000",
    accent_color="#C9A86A",
    qualitative_title="Qualitative Methods",
    qualitative_text="Qualitative research methods involve collecting and analyzing non-numerical data to explore the underlying motivations, perceptions, and behaviors of individuals. In our research proposal, qualitative methods will be utilized to gain in-depth insights into consumer preferences, attitudes, and experiences related to the new product.",
    quantitative_title="Quantitative Methods",
    quantitative_text="Quantitative research methods involve collecting and analyzing numerical data to quantify relationships, trends, and patterns. In our research proposal, quantitative methods will be employed to measure the prevalence, frequency, and magnitude of certain phenomena related to the new product.",
    image_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2340&auto=format&fit=crop",
    bg_color="#F5F5F5",
    font_family="'Inter', sans-serif",
    custom_css=""
):
    """
    Generate a Methodology slide with two method boxes and professional image.
    
    Args:
        title: Main title text
        title_color: Color for the main title
        accent_color: Color for accent elements (bar, circles, boxes)
        qualitative_title: Title for qualitative methods box
        qualitative_text: Description text for qualitative methods
        quantitative_title: Title for quantitative methods box
        quantitative_text: Description text for quantitative methods
        image_url: URL for the right side professional image
        bg_color: Background color
        font_family: Font family for the text
        custom_css: Additional custom CSS
    
    Returns:
        str: Complete HTML code for the methodology slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Methodology Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {font_family};
            background-color: {bg_color};
            overflow: hidden;
        }}
        
        .slide-wrapper {{
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: {bg_color};
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            background-color: {bg_color};
            position: relative;
            overflow: hidden;
        }}
        
        /* Decorative circles in top right */
        .decorative-circles {{
            position: absolute;
            top: 0;
            right: 40%;
            width: 250px;
            height: 250px;
            z-index: 1;
        }}
        
        .circle {{
            position: absolute;
            border: 3px solid {accent_color};
            border-radius: 50%;
            opacity: 0.6;
        }}
        
        .circle-1 {{
            width: 100px;
            height: 100px;
            top: 30px;
            right: 80px;
        }}
        
        .circle-2 {{
            width: 130px;
            height: 130px;
            top: 15px;
            right: 65px;
        }}
        
        .circle-3 {{
            width: 160px;
            height: 160px;
            top: 0;
            right: 50px;
        }}
        
        .circle-4 {{
            width: 190px;
            height: 190px;
            top: -15px;
            right: 35px;
        }}
        
        .circle-5 {{
            width: 220px;
            height: 220px;
            top: -30px;
            right: 20px;
        }}
        
        /* Title Section */
        .title-section {{
            position: absolute;
            top: 30px;
            left: 0;
            display: flex;
            align-items: center;
            z-index: 2;
        }}
        
        .title-accent {{
            width: 100px;
            height: 100px;
            background-color: {accent_color};
            margin-right: 20px;
        }}
        
        .title {{
            font-size: 75px;
            font-weight: 900;
            color: {title_color};
            
        }}
        
        /* Content Section */
        .content-section {{
            position: absolute;
            top: 240px;
            left: 50px;
            right: 50px;
            display: flex;
            gap: 30px;
            height: 780px;
        }}
        
        /* Left side - Method boxes */
        .methods-container {{
            flex: 0 0 620px;
            display: flex;
            flex-direction: column;
            gap: 30px;
        }}
        
        .method-box {{
            padding: 40px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            flex: 1;
        }}
        
        .method-box.qualitative {{
            background-color: rgba(201, 168, 106, 0.3);
        }}
        
        .method-box.quantitative {{
            background-color: rgba(201, 168, 106, 0.5);
        }}
        
        .method-title {{
            font-size: 45px;
            font-weight: 700;
            color: {title_color};
            margin-bottom: 15px;
        }}
        
        .method-text {{
            font-size: 21px;
            line-height: 1.7;
            color: #1a1a1a;
        }}
        
        /* Right side - Image */
        .image-container {{
            flex: 1;
            position: relative;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-wrapper">
        <div class="slide-container">
            <!-- Decorative Circles -->
            <div class="decorative-circles">
                <div class="circle circle-1"></div>
                <div class="circle circle-2"></div>
                <div class="circle circle-3"></div>
                <div class="circle circle-4"></div>
                <div class="circle circle-5"></div>
            </div>
            
            <!-- Title Section -->
            <div class="title-section">
                <div class="title-accent"></div>
                <h1 class="title">{title}</h1>
            </div>
            
            <!-- Content Section -->
            <div class="content-section">
                <!-- Methods Container -->
                <div class="methods-container">
                    <!-- Qualitative Methods Box -->
                    <div class="method-box qualitative">
                        <h2 class="method-title">{qualitative_title}</h2>
                        <p class="method-text">{qualitative_text}</p>
                    </div>
                    
                    <!-- Quantitative Methods Box -->
                    <div class="method-box quantitative">
                        <h2 class="method-title">{quantitative_title}</h2>
                        <p class="method-text">{quantitative_text}</p>
                    </div>
                </div>
                
                <!-- Image Container -->
                <div class="image-container">
                    <img src="{image_url}" alt="Professional working with technology">
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_planning_phase_slide(
    title="Planning Phase",
    title_color="#C5E898",
    bg_color="#1A4D4D",
    marker_light_color="#C5E898",
    marker_dark_color="#4ECDC4",
    phases=None,
    timeline_color="#FFFFFF",
    custom_css=""
):
    """
    Generate a Planning Phase slide with timeline and icon markers.
    
    This function creates an HTML slide showing a planning phase timeline with
    4 stages represented by pin markers containing line art icons, connected by
    a horizontal timeline. Each stage has a title and description below.
    
    Args:
        title (str): Main title text (default: "Planning Phase")
        title_color (str): Color for the title (default: "#C5E898" - light yellow-green)
        bg_color (str): Background color (default: "#1A4D4D" - dark teal)
        marker_light_color (str): Color for light markers (default: "#C5E898")
        marker_dark_color (str): Color for dark markers (default: "#4ECDC4")
        phases (list): List of phase dictionaries with keys: 'name', 'description', 'icon_type', 'marker_color'
                       Options for icon_type: 'brain', 'checklist', 'design', 'puzzle'
                       Options for marker_color: 'light' or 'dark'
        timeline_color (str): Color for the timeline line and dots (default: "#FFFFFF")
        custom_css (str): Additional custom CSS to inject
    
    Returns:
        str: Complete HTML code for the planning phase slide
    """
    
    # Default phases if none provided
    if phases is None:
        phases = [
            {
                'name': 'Planning',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.',
                'icon_type': 'brain',
                'marker_color': 'light'
            },
            {
                'name': 'Analysis',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.',
                'icon_type': 'checklist',
                'marker_color': 'dark'
            },
            {
                'name': 'Design',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.',
                'icon_type': 'design',
                'marker_color': 'light'
            },
            {
                'name': 'Implementation',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.',
                'icon_type': 'puzzle',
                'marker_color': 'dark'
            }
        ]
    
    # Generate icon SVGs based on type
    def get_icon_svg(icon_type):
        icons = {
            'brain': '''
                <path d="M30,25 Q30,15 40,15 Q45,15 45,20 Q50,15 55,20 Q60,15 60,25 Q60,30 55,35 Q60,40 55,45 Q55,50 50,50 Q45,55 40,50 Q35,55 30,50 Q25,50 25,45 Q20,40 25,35 Q20,30 30,25 Z" fill="none" stroke="currentColor" stroke-width="2.5"/>
                <circle cx="42" cy="30" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
                <circle cx="48" cy="35" r="2" fill="none" stroke="currentColor" stroke-width="2"/>
                <path d="M35,30 Q35,35 40,35" fill="none" stroke="currentColor" stroke-width="2"/>
            ''',
            'checklist': '''
                <rect x="28" y="20" width="30" height="35" rx="3" fill="none" stroke="currentColor" stroke-width="2.5"/>
                <circle cx="43" cy="32" r="8" fill="none" stroke="currentColor" stroke-width="2.5"/>
                <path d="M40,32 L42,34 L46,30" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="32" y1="45" x2="38" y2="45" stroke="currentColor" stroke-width="2"/>
                <line x1="32" y1="50" x2="36" y2="50" stroke="currentColor" stroke-width="2"/>
                <path d="M48,30 L52,26 L54,28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            ''',
            'design': '''
                <rect x="30" y="23" width="28" height="20" rx="2" fill="none" stroke="currentColor" stroke-width="2.5"/>
                <line x1="33" y1="27" x2="55" y2="27" stroke="currentColor" stroke-width="1.5"/>
                <line x1="33" y1="31" x2="55" y2="31" stroke="currentColor" stroke-width="1.5"/>
                <line x1="33" y1="35" x2="55" y2="35" stroke="currentColor" stroke-width="1.5"/>
                <line x1="33" y1="39" x2="50" y2="39" stroke="currentColor" stroke-width="1.5"/>
                <path d="M52,45 L55,52 L58,45 L55,48 Z" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            ''',
            'puzzle': '''
                <path d="M32,25 L32,35 Q32,38 35,38 Q38,38 38,35 L38,25 L48,25 L48,35 L58,35 L58,45 L48,45 L48,55 L38,55 L38,45 Q38,42 35,42 Q32,42 32,45 L32,55 L22,55 L22,45 L22,35 L32,35 Z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
                <circle cx="35" cy="30" r="2" fill="currentColor"/>
                <circle cx="43" cy="40" r="2" fill="currentColor"/>
            '''
        }
        return icons.get(icon_type, icons['brain'])
    
    # Generate markers HTML - each marker created individually
    marker_1_bg = marker_light_color  # Planning - light
    marker_1_icon = '''
                <path d="M30,25 Q30,15 40,15 Q45,15 45,20 Q50,15 55,20 Q60,15 60,25 Q60,30 55,35 Q60,40 55,45 Q55,50 50,50 Q45,55 40,50 Q35,55 30,50 Q25,50 25,45 Q20,40 25,35 Q20,30 30,25 Z" fill="none" stroke="currentColor" stroke-width="2.5"/>
                <circle cx="42" cy="30" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
                <circle cx="48" cy="35" r="2" fill="none" stroke="currentColor" stroke-width="2"/>
                <path d="M35,30 Q35,35 40,35" fill="none" stroke="currentColor" stroke-width="2"/>
            '''
    
    marker_2_bg = marker_dark_color  # Analysis - dark
    marker_2_icon = '''
                <rect x="28" y="20" width="30" height="35" rx="3" fill="none" stroke="currentColor" stroke-width="2.5"/>
                <circle cx="43" cy="32" r="8" fill="none" stroke="currentColor" stroke-width="2.5"/>
                <path d="M40,32 L42,34 L46,30" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="32" y1="45" x2="38" y2="45" stroke="currentColor" stroke-width="2"/>
                <line x1="32" y1="50" x2="36" y2="50" stroke="currentColor" stroke-width="2"/>
                <path d="M48,30 L52,26 L54,28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            '''
    
    marker_3_bg = marker_light_color  # Design - light
    marker_3_icon = '''
                <rect x="30" y="23" width="28" height="20" rx="2" fill="none" stroke="currentColor" stroke-width="2.5"/>
                <line x1="33" y1="27" x2="55" y2="27" stroke="currentColor" stroke-width="1.5"/>
                <line x1="33" y1="31" x2="55" y2="31" stroke="currentColor" stroke-width="1.5"/>
                <line x1="33" y1="35" x2="55" y2="35" stroke="currentColor" stroke-width="1.5"/>
                <line x1="33" y1="39" x2="50" y2="39" stroke="currentColor" stroke-width="1.5"/>
                <path d="M52,45 L55,52 L58,45 L55,48 Z" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
            '''
    
    marker_4_bg = marker_dark_color  # Implementation - dark
    marker_4_icon = '''
                <path d="M32,25 L32,35 Q32,38 35,38 Q38,38 38,35 L38,25 L48,25 L48,35 L58,35 L58,45 L48,45 L48,55 L38,55 L38,45 Q38,42 35,42 Q32,42 32,45 L32,55 L22,55 L22,45 L22,35 L32,35 Z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
                <circle cx="35" cy="30" r="2" fill="currentColor"/>
                <circle cx="43" cy="40" r="2" fill="currentColor"/>
            '''
    
    markers_html = f'''
        <div class="phase-marker">
            <div class="marker-pin" style="--marker-bg: {marker_1_bg};">
                <svg viewBox="0 0 80 80" class="marker-icon" style="color: {bg_color};">
                    {marker_1_icon}
                </svg>
            </div>
        </div>
        <div class="phase-marker">
            <div class="marker-pin" style="--marker-bg: {marker_2_bg};">
                <svg viewBox="0 0 80 80" class="marker-icon" style="color: {bg_color};">
                    {marker_2_icon}
                </svg>
            </div>
        </div>
        <div class="phase-marker">
            <div class="marker-pin" style="--marker-bg: {marker_3_bg};">
                <svg viewBox="0 0 80 80" class="marker-icon" style="color: {bg_color};">
                    {marker_3_icon}
                </svg>
            </div>
        </div>
        <div class="phase-marker">
            <div class="marker-pin" style="--marker-bg: {marker_4_bg};">
                <svg viewBox="0 0 80 80" class="marker-icon" style="color: {bg_color};">
                    {marker_4_icon}
                </svg>
            </div>
        </div>
        '''
    
    # Generate timeline items HTML - each item created individually
    timeline_html = f'''
        <div class="timeline-item">
            <div class="timeline-track-segment">
                <div class="timeline-dot"></div>
            </div>
            <h3 class="phase-name">Planning</h3>
            <p class="phase-description">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.</p>
        </div>
        <div class="timeline-item">
            <div class="timeline-track-segment">
                <div class="timeline-dot"></div>
            </div>
            <h3 class="phase-name">Analysis</h3>
            <p class="phase-description">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.</p>
        </div>
        <div class="timeline-item">
            <div class="timeline-track-segment">
                <div class="timeline-dot"></div>
            </div>
            <h3 class="phase-name">Design</h3>
            <p class="phase-description">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.</p>
        </div>
        <div class="timeline-item">
            <div class="timeline-track-segment">
                <div class="timeline-dot"></div>
            </div>
            <h3 class="phase-name">Implementation</h3>
            <p class="phase-description">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do.</p>
        </div>
        '''
    
    html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: 1920px;
            height: 1080px;
            font-family: 'Arial', 'Segoe UI', Tahoma, sans-serif;
            background: {bg_color};
            color: white;
            overflow: hidden;
            padding: 80px 100px;
            display: flex;
            flex-direction: column;
        }}
        
        .title {{
            font-size: 90px;
            font-weight: 300;
            color: {title_color};
            margin-bottom: 100px;
            letter-spacing: 2px;
        }}
        
        .markers-container {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 60px;
            padding: 0 60px;
        }}
        
        .phase-marker {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: flex-end;
        }}
        
        .marker-pin {{
            width: 180px;
            height: 180px;
            background-color: var(--marker-bg);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }}
        
        .marker-icon {{
            width: 90px;
            height: 90px;
        }}
        
        .timeline-container {{
            padding: 0 60px;
        }}
        
        .timeline-items {{
            display: flex;
            justify-content: space-between;
            background: linear-gradient(to right, {timeline_color} 0%, {timeline_color} 100%);
            background-size: 100% 3px;
            background-position: center 15px;
            background-repeat: no-repeat;
        }}
        
        .timeline-item {{
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        
        .timeline-track-segment {{
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px;
        }}
        
        .timeline-dot {{
            width: 30px;
            height: 30px;
            background: {timeline_color};
            border-radius: 50%;
            border: 5px solid {bg_color};
        }}
        
        .phase-name {{
            font-size: 38px;
            font-weight: 600;
            color: white;
            margin-bottom: 20px;
            letter-spacing: 0.5px;
        }}
        
        .phase-description {{
            font-size: 22px;
            line-height: 1.6;
            color: rgba(255, 255, 255, 0.9);
            padding: 0 20px;
            text-align: center;
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <h1 class="title">{title}</h1>
    
    <div class="markers-container">
        <div class="phase-marker">
            <div class="marker-pin" style="--marker-bg: {marker_light_color};">
                <svg viewBox="0 0 80 80" class="marker-icon" style="color: {bg_color};">
                    <path d="M30,25 Q30,15 40,15 Q45,15 45,20 Q50,15 55,20 Q60,15 60,25 Q60,30 55,35 Q60,40 55,45 Q55,50 50,50 Q45,55 40,50 Q35,55 30,50 Q25,50 25,45 Q20,40 25,35 Q20,30 30,25 Z" fill="none" stroke="currentColor" stroke-width="2.5"/>
                    <circle cx="42" cy="30" r="3" fill="none" stroke="currentColor" stroke-width="2"/>
                    <circle cx="48" cy="35" r="2" fill="none" stroke="currentColor" stroke-width="2"/>
                    <path d="M35,30 Q35,35 40,35" fill="none" stroke="currentColor" stroke-width="2"/>
                </svg>
            </div>
        </div>
        <div class="phase-marker">
            <div class="marker-pin" style="--marker-bg: {marker_dark_color};">
                <svg viewBox="0 0 80 80" class="marker-icon" style="color: {bg_color};">
                    <rect x="28" y="20" width="30" height="35" rx="3" fill="none" stroke="currentColor" stroke-width="2.5"/>
                    <circle cx="43" cy="32" r="8" fill="none" stroke="currentColor" stroke-width="2.5"/>
                    <path d="M40,32 L42,34 L46,30" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
                    <line x1="32" y1="45" x2="38" y2="45" stroke="currentColor" stroke-width="2"/>
                    <line x1="32" y1="50" x2="36" y2="50" stroke="currentColor" stroke-width="2"/>
                    <path d="M48,30 L52,26 L54,28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </div>
        </div>
        <div class="phase-marker">
            <div class="marker-pin" style="--marker-bg: {marker_light_color};">
                <svg viewBox="0 0 80 80" class="marker-icon" style="color: {bg_color};">
                    <rect x="30" y="23" width="28" height="20" rx="2" fill="none" stroke="currentColor" stroke-width="2.5"/>
                    <line x1="33" y1="27" x2="55" y2="27" stroke="currentColor" stroke-width="1.5"/>
                    <line x1="33" y1="31" x2="55" y2="31" stroke="currentColor" stroke-width="1.5"/>
                    <line x1="33" y1="35" x2="55" y2="35" stroke="currentColor" stroke-width="1.5"/>
                    <line x1="33" y1="39" x2="50" y2="39" stroke="currentColor" stroke-width="1.5"/>
                    <path d="M52,45 L55,52 L58,45 L55,48 Z" fill="currentColor" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
                </svg>
            </div>
        </div>
        <div class="phase-marker">
            <div class="marker-pin" style="--marker-bg: {marker_dark_color};">
                <svg viewBox="0 0 80 80" class="marker-icon" style="color: {bg_color};">
                    <path d="M32,25 L32,35 Q32,38 35,38 Q38,38 38,35 L38,25 L48,25 L48,35 L58,35 L58,45 L48,45 L48,55 L38,55 L38,45 Q38,42 35,42 Q32,42 32,45 L32,55 L22,55 L22,45 L22,35 L32,35 Z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
                    <circle cx="35" cy="30" r="2" fill="currentColor"/>
                    <circle cx="43" cy="40" r="2" fill="currentColor"/>
                </svg>
            </div>
        </div>
    </div>
    
    <div class="timeline-container">
        <div class="timeline-items">
            {timeline_html}
        </div>
    </div>
</body>
</html>'''
    
    return html_code

def generate_timeline_slide(
    main_title="COMPANY HISTORY",
    subtitle="A journey of innovation and growth",
    milestones=[
        {"year": "2020", "title": "Foundation", "desc": "Started with a team of 5 visionaries."},
        {"year": "2021", "title": "Series A", "desc": "Raised $10M to expand operations."},
        {"year": "2022", "title": "Global Launch", "desc": "Entered 3 new international markets."},
        {"year": "2023", "title": "Market Leader", "desc": "Achieved #1 status in the industry."}
    ],
    bg_color="#1E1E2E",
    accent_color="#F43F5E",
    text_color="#FFFFFF",
    font_family="'Inter', sans-serif"
):
    """
    Generates a horizontal timeline slide to visualize progress or history.
    Layout: Horizontal axis with alternating or aligned milestones.
    """
    milestone_html = ""
    start_x = 200
    gap = 400
    
    for i, item in enumerate(milestones):
        x_pos = start_x + (i * gap)
        # Alternate positions for visual interest if desired, but kept linear here for flat structure reliability
        top_pos_circle = 540 - 15  # Center line is at 540px
        top_pos_title = 580  # Position for h3
        top_pos_desc = 619   # Position for p (580 + 29 height + 10 spacing)
        top_pos_year = 450
        
        milestone_html += f"""
        <div style="position: absolute; left: {x_pos}px; top: {top_pos_circle}px; width: 30px; height: 30px; background: {accent_color}; border: 4px solid {bg_color}; border-radius: 50%; z-index: 2; box-shadow: 0 0 0 4px {accent_color}40;"></div>
        
        <div style="position: absolute; left: {x_pos - 60}px; top: {top_pos_year}px; width: 150px; text-align: center;">
            <span style="font-size: 36px; font-weight: 800; color: {accent_color};">{item['year']}</span>
        </div>
        
        <div style="position: absolute; left: {x_pos - 100}px; top: {top_pos_title}px; width: 230px; text-align: center;">
            <h3 style="font-size: 24px; font-weight: 700; color: {text_color};">{item['title']}</h3>
        </div>
        <div style="position: absolute; left: {x_pos - 100}px; top: {top_pos_desc}px; width: 230px; text-align: center;">
            <p style="font-size: 18px; color: {text_color}; opacity: 0.7; line-height: 1.4;">{item['desc']}</p>
        </div>
        """

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html, body {{ width: 1920px; height: 1080px; font-family: {font_family}; background: {bg_color}; overflow: hidden; }}
        </style>
    </head>
    <body>
        <div style="position: absolute; top: 100px; left: 0; width: 1920px; text-align: center;">
            <h1 style="font-size: 72px; font-weight: 800; color: {text_color}; margin-bottom: 20px;">{main_title}</h1>
            <p style="font-size: 28px; color: {text_color}; opacity: 0.6;">{subtitle}</p>
        </div>

        <div style="position: absolute; top: 554px; left: 150px; width: 1620px; height: 2px; background: rgba(255,255,255,0.1);"></div>
        <div style="position: absolute; top: 554px; left: 150px; width: {len(milestones) * gap}px; height: 2px; background: {accent_color};"></div>

        {milestone_html}

        <svg style="position: absolute; bottom: 0; right: 0; width: 400px; height: 400px; opacity: 0.05;" viewBox="0 0 200 200">
            <circle cx="200" cy="200" r="180" fill="{text_color}" />
        </svg>
    </body>
    </html>"""
    return html

def generate_quote_slide(
    quote="Design is not  what it looks like and feels like. Design is how it works.",
    author="Steve Jobs",
    role="Co-founder, Apple",
    bg_color="#FAF9F6",
    quote_color="#18181B",
    accent_color="#EA580C",
    font_family="Playfair Display"
):
    """
    Generates an elegant quote slide centered on screen.
    """
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html, body {{ width: 1920px; height: 1080px; font-family: {font_family}, serif; background: {bg_color}; overflow: hidden; }}
        </style>
    </head>
    <body>
        <!-- Decorative quotation mark -->
        <div style="position: absolute; top: 180px; left: 200px; font-size: 300px; color: {accent_color}; opacity: 0.1; font-family: {font_family}, serif; line-height: 1; pointer-events: none;">"</div>
        
        <!-- Main quote text -->
        <h1 style="position: absolute; top: 300px; left: 300px; width: 1320px; font-size: 80px; font-weight: 700; color: {quote_color}; line-height: 1.3; font-style: italic; text-align: center;">
            {quote}
        </h1>
        
        <!-- Accent line -->
        <div style="position: absolute; top: 610px; left: 910px; width: 100px; height: 4px; background: {accent_color};"></div>
        
        <!-- Author name -->
        <h3 style="position: absolute; top: 654px; left: 300px; width: 1320px; font-size: 36px; font-weight: 700; color: {quote_color}; font-family: Inter, sans-serif; text-align: center;">{author}</h3>
        
        <!-- Author role -->
        <p style="position: absolute; top: 708px; left: 300px; width: 1320px; font-size: 24px; color: #71717A; font-family: Inter, sans-serif; text-align: center;">{role}</p>
        
        <div style="position: absolute; top: 60px; left: 60px; width: 1800px; height: 960px; border: 2px solid {quote_color}; opacity: 0.1; pointer-events: none;"></div>
    </body>
    </html>"""
    return html

def generate_classic_content_slide(
    main_title="MARKET OPPORTUNITY",
    paragraph="The global market for our solution is expanding rapidly. By leveraging our unique technology stack, we can capture significant market share in the next fiscal year.",
    bullet_points=[
        "Target audience growth of 15% YoY",
        "Low competition in the premium segment",
        "High barrier to entry for new players",
        "Strong demand for automated solutions"
    ],
    image_url="https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2015&auto=format&fit=crop",
    theme_color="#2563EB",
    text_color="#1F2937",
    bg_color="#FFFFFF"
):
    """
    Generates a classic content slide with Title, Paragraph, Bullet Points (Left) and Image (Right).
    Perfect for detailed explanations.
    """
    # Tạo HTML cho danh sách bullet points
    bullets_html = ""
    for i, point in enumerate(bullet_points):
        top_pos = 500 + (i * 60)
        bullets_html += f"""
        <div style="position: absolute; left: 120px; top: {top_pos}px; width: 750px; height: 50px;">
            <div style="display: flex; align-items: flex-start;">
                <div style="width: 10px; height: 10px; background: {theme_color}; border-radius: 50%; margin-top: 12px; margin-right: 20px; flex-shrink: 0;"></div>
                <p style="font-size: 24px; color: {text_color}; line-height: 1.4; width: 700px;">{point}</p>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html, body {{ width: 1920px; height: 1080px; font-family: 'Inter', sans-serif; background: {bg_color}; overflow: hidden; }}
        </style>
    </head>
    <body>
        <div style="position: absolute; top: 100px; left: 120px;">
            <div style="width: 100px; height: 8px; background: {theme_color}; margin-bottom: 30px;"></div>
            <h1 style="font-size: 72px; font-weight: 800; color: {text_color}; margin-bottom: 40px; text-transform: uppercase;">{main_title}</h1>
        </div>

        <div style="position: absolute; top: 300px; left: 120px; width: 750px;">
            <p style="font-size: 28px; line-height: 1.6; color: {text_color}; opacity: 0.8; margin-bottom: 40px;">
                {paragraph}
            </p>
        </div>

        {bullets_html}

        <div style="position: absolute; top: 100px; right: 120px; width: 800px; height: 880px; border-radius: 30px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.1);">
            <img src="{image_url}" style="width: 100%; height: 100%; object-fit: cover;">
        </div>
        
        <div style="position: absolute; bottom: 50px; left: 120px; font-size: 16px; color: {text_color}; opacity: 0.4;">
            CONFIDENTIAL - {main_title}
        </div>
    </body>
    </html>"""
    return html


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
    font_family="'Montserrat', 'Inter', sans-serif",
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
    font_family="'Inter', sans-serif",
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
    font_family="'Montserrat', 'Inter', sans-serif",
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
            font-size: clamp(2.5rem, 8vw, 7rem);
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


def generate_business_thank_you_slide(
    main_text="THANK YOU",
    subtitle="For your attention and time",
    main_text_color="#0056d2",
    subtitle_color="#666666",
    accent_color="#0056d2",
    main_font="Arial, sans-serif",
    subtitle_font="Arial, sans-serif"
):
    """
    Generate a clean business thank you slide with centered text and decorative side D-shapes.
    
    Args:
        main_text (str): Main thank you text (e.g., "THANK YOU")
        subtitle (str): Subtitle text below main text
        main_text_color (str): Color for main text (default: blue)
        subtitle_color (str): Color for subtitle text
        contact_color (str): Color for contact information
        accent_color (str): Color for decorative D-shapes
        main_font (str): Font family for main text
        subtitle_font (str): Font family for subtitle and contact
    
    Returns:
        str: Complete HTML code for the business thank you slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Thank You</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            width: 1920px;
            height: 1080px;
            background: 
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 50px,
                    rgba(0, 86, 210, 0.03) 50px,
                    rgba(0, 86, 210, 0.03) 100px
                ),
                repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 50px,
                    rgba(0, 86, 210, 0.03) 50px,
                    rgba(0, 86, 210, 0.03) 100px
                ),
                linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }}
        
        .slide-container {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        
        .content {{
            text-align: center;
            z-index: 10;
            max-width: 1400px;
            padding: 0 100px;
        }}
        
        .main-text {{
            font-family: {main_font};
            font-size: 160px;
            font-weight: 900;
            color: {main_text_color};
            letter-spacing: 12px;
            margin-bottom: 40px;
            line-height: 1.1;
        }}
        
        .subtitle {{
            font-family: {subtitle_font};
            font-size: 36px;
            font-weight: 400;
            color: {subtitle_color};
            line-height: 1.6;
            margin-bottom: 60px;
        }}
        
       
        /* Decorative D-shapes on left and right */
        .circle-left {{
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 200px;
            height: 400px;
            background: {accent_color};
            border-radius: 0 200px 200px 0;
            z-index: 1;
        }}
        
        .circle-right {{
            position: absolute;
            right: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 200px;
            height: 400px;
            background: {accent_color};
            border-radius: 200px 0 0 200px;
            z-index: 1;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Side D-shapes -->
        <div class="circle-left"></div>
        <div class="circle-right"></div>
        
        <!-- Main content -->
        <div class="content">
            <div class="main-text">{main_text}</div>
            <div class="subtitle">{subtitle}</div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_thank_you_slide_4(
    main_text="THANK YOU!",
    bg_color="#5B9BD5",
    bg_gradient_to="#A8D8F0",
    text_color="#2C5F8D",
    bubble_bg_color="#FFFFFF",
    font_family="Arial, sans-serif",
    show_speech_tail=True,
    custom_css=""
):
    """
    Generate a 'Thank You' slide with a speech bubble design.
    
    Parameters:
    - main_text: The thank you message text
    - bg_color: Background gradient start color (default: blue)
    - bg_gradient_to: Background gradient end color (default: light blue)
    - text_color: Color of the thank you text
    - bubble_bg_color: Background color of the speech bubble
    - font_family: Font family for the text (default: Arial, sans-serif)
    - show_speech_tail: Whether to show the speech bubble tail
    - custom_css: Additional custom CSS
    
    Returns:
    - HTML string for the thank you slide
    """
    
    # Handle list inputs (take first element)
    if isinstance(main_text, list):
        main_text = main_text[0] if main_text else "THANK YOU!"
    
    speech_tail_html = f'''
        <div class="speech-tail"></div>
    ''' if show_speech_tail else ''
    
    html_code = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You Slide</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            overflow: hidden;
        }}
        
        .slide-container {{
            width: 1920px;
            height: 1080px;
            position: relative;
            background: linear-gradient(135deg, {bg_color} 0%, {bg_gradient_to} 100%);
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .speech-bubble {{
            position: relative;
            background-color: {bubble_bg_color};
            padding: 60px 120px;
            border-radius: 20px;
            box-shadow: 
                0 20px 60px rgba(0, 0, 0, 0.3),
                0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .speech-tail {{
            position: absolute;
            bottom: -40px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 50px solid transparent;
            border-right: 50px solid transparent;
            border-top: 50px solid {bubble_bg_color};
            filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.2));
        }}
        
        .thank-you-text {{
            font-size: 5rem;
            font-weight: 900;
            color: {text_color};
            font-family: {font_family};
            text-align: center;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            text-shadow: 
                3px 3px 0px rgba(0, 0, 0, 0.1),
                -1px -1px 0px rgba(255, 255, 255, 0.5);
        }}
        
        /* Responsive scaling for smaller screens */
        @media screen and (max-width: 1920px) {{
            .slide-container {{
                width: 100vw;
                height: 100vh;
                transform-origin: center;
            }}
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="speech-bubble">
            <div class="thank-you-text">{main_text}</div>
            {speech_tail_html}
        </div>
    </div>
</body>
</html>
'''
    
    return html_code

def generate_thank_you_decorative_slide(
    main_text="THANK YOU!",
    bg_color="#2B5FA6",
    bg_gradient_to="#4A90E2",
    text_color="#FFFFFF",
    show_dots=True,
    num_dots=25,
    custom_css="",
):
    """
    Generate a decorative Thank You slide with dots.
    
    Parameters:
    - main_text: Main thank you text (default: "THANK YOU!")
    - bg_color: Background gradient start color (default: "#2B5FA6")
    - bg_gradient_to: Background gradient end color (default: "#4A90E2")
    - text_color: Text color (default: "#FFFFFF")
    - show_dots: Show decorative dots (default: True)
    - num_dots: Number of dots to display (default: 15)
    - custom_css: Additional custom CSS (default: "")
    
    Returns:
    - HTML string for the slide
    """
    
    # Handle list inputs
    if isinstance(main_text, list):
        main_text = main_text[0] if main_text else "THANK YOU!"
    
    # Generate random dots positions
    import random
    random.seed(42)  # Seed for consistent placement
    dots_html = ""
    if show_dots:
        for i in range(num_dots):
            size = random.choice([10, 14, 18])  # More uniform sizes
            # Distribute dots more evenly across screen
            top = random.randint(3, 25) if i < num_dots//2 else random.randint(75, 97)
            left = random.randint(5, 95)
            opacity = random.uniform(0.5, 0.85)
            delay = random.uniform(0, 2)
            dots_html += f"""
            <div class="dot" style="
                width: {size}px;
                height: {size}px;
                top: {top}%;
                left: {left}%;
                opacity: {opacity};
                animation-delay: {delay}s;
            "></div>
            """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            width: 1920px;
            height: 1080px;
            background: linear-gradient(135deg, {bg_color} 0%, {bg_gradient_to} 100%);
            overflow: hidden;
            position: relative;
            font-family: 'Arial Black', 'Arial Bold', Arial, sans-serif;
        }}
        
        .main-text {{
            position: absolute;
            top: 475px;
            left: 0;
            width: 100%;
            font-size: 96px;
            font-weight: 900;
            color: {text_color};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            text-align: center;
            text-shadow: 
                0 4px 0 rgba(0, 0, 0, 0.2),
                0 8px 0 rgba(0, 0, 0, 0.15),
                0 12px 0 rgba(0, 0, 0, 0.1),
                0 16px 20px rgba(0, 0, 0, 0.3);
            z-index: 10;
        }}
        
        .dot {{
            position: absolute;
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 50%;
        }}
        
        {custom_css}
    </style>
</head>
<body>
    {dots_html}
    <h1 class="main-text">{main_text}</h1>
</body>
</html>"""
    
    return html_code

def generate_watercolor_thank_you_slide(
    title="Thank You",
    bg_color="#f5f5f5",
    text_color="#1e3a5f",
    watercolor_color="#4dd0e1",
    watercolor_opacity=0.6,
    font_family="'Brush Script MT', cursive, serif",
    show_watercolor=True,
    custom_css=""
):
    """
    Generate a watercolor style 'Thank You' slide HTML.
    
    Parameters:
    - title: Main text (default: "Thank You")
    - bg_color: Background color (default: "#f5f5f5" - light gray)
    - text_color: Text color (default: "#1e3a5f" - dark blue)
    - watercolor_color: Watercolor splash color (default: "#4dd0e1" - cyan)
    - watercolor_opacity: Opacity of watercolor effect (default: 0.6)
    - font_family: Font for title (default: cursive/script style)
    - show_watercolor: Show watercolor background effect (default: True)
    - custom_css: Additional custom CSS
    
    Returns:
    - Complete HTML string for the slide
    """
    
    # Handle list inputs
    if isinstance(title, list):
        title = title[0] if title else "Thank You"
    
    watercolor_html = ""
    if show_watercolor:
        watercolor_html = f"""
        <div class="watercolor-splash" style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            height: 70%;
            background: radial-gradient(ellipse at center, 
                {watercolor_color} 0%, 
                rgba(77, 208, 225, 0.9) 15%,
                rgba(77, 208, 225, 0.7) 35%,
                rgba(77, 208, 225, 0.4) 60%,
                transparent 100%);
            filter: blur(50px);
            opacity: {watercolor_opacity};
            z-index: 1;
        "></div>
        
        <div class="watercolor-blob watercolor-blob-1" style="
            position: absolute;
            top: 20%;
            left: 20%;
            width: 300px;
            height: 300px;
            background: {watercolor_color};
            border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
            filter: blur(60px);
            opacity: 0.5;
            z-index: 1;
        "></div>
        
        <div class="watercolor-blob watercolor-blob-2" style="
            position: absolute;
            top: 25%;
            right: 15%;
            width: 350px;
            height: 350px;
            background: rgba(77, 208, 225, 0.8);
            border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
            filter: blur(55px);
            opacity: 0.45;
            z-index: 1;
        "></div>
        
        <div class="watercolor-blob watercolor-blob-3" style="
            position: absolute;
            bottom: 20%;
            left: 30%;
            width: 280px;
            height: 280px;
            background: rgba(77, 208, 225, 0.7);
            border-radius: 50% 60% 40% 70% / 50% 40% 60% 50%;
            filter: blur(65px);
            opacity: 0.4;
            z-index: 1;
        "></div>
        """
    
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thank You Slide</title>
        <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Pacifico&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: Arial, sans-serif;
                overflow: hidden;
                margin: 0;
                padding: 0;
                width: 100vw;
                height: 100vh;
            }}
            
            .slide-container {{
                width: 100vw;
                height: 100vh;
                position: relative;
                background: {bg_color};
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }}
            
            .content {{
                position: relative;
                z-index: 2;
                text-align: center;
            }}
            
            .title {{
                font-family: {font_family};
                font-size: 8rem;
                color: {text_color};
                font-weight: 700;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }}
            

            
            {custom_css}
        </style>
    </head>
    <body>
        <div class="slide-container">
            {watercolor_html}
            
            <div class="content">
                <h1 class="title">{title}</h1>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_code

def generate_thank_you_slide_5(
    main_text="Thank you!",
    bg_color="#f5f5f5",
    text_color="#2d3748",
    circle_color="#fbbf24",
    corner_shape_color="#2c5f6f",
    show_border=True,
    border_color="#1a1a1a",
    show_corner_circles=True,
    show_corner_shapes=True,
    custom_css=""
):
    """
    Generate a geometric Thank You slide with yellow circles and teal corner shapes.
    
    Parameters:
    - main_text: Main text content (default: "Thank you!")
    - bg_color: Background color (default: off-white)
    - text_color: Text color (default: dark gray)
    - circle_color: Color of decorative circles (default: yellow)
    - corner_shape_color: Color of corner shapes (default: dark teal)
    - show_border: Whether to show the border frame (default: True)
    - border_color: Color of the border (default: black)
    - show_corner_circles: Whether to show corner circles (default: True)
    - show_corner_shapes: Whether to show corner shapes (default: True)
    - custom_css: Additional custom CSS
    """
    
    # Handle list inputs
    if isinstance(main_text, list):
        main_text = main_text[0] if main_text else "Thank you!"
    
    border_style = f"border: 3px solid {border_color};" if show_border else ""
    
    circles_html = ""
    if show_corner_circles:
        circles_html = """
        <!-- Top Right Circles -->
        <div class="circle" style="top: 50px; right: 120px; width: 150px; height: 150px;"></div>
        <div class="circle" style="top: 50px; right: 290px; width: 150px; height: 150px;"></div>
        <div class="circle" style="top: 220px; right: 205px; width: 150px; height: 150px;"></div>
        
        <!-- Bottom Left Half Circle -->
        <div class="circle" style="bottom: -75px; left: 50px; width: 150px; height: 150px;"></div>
        """
    
    corner_shapes_html = ""
    if show_corner_shapes:
        corner_shapes_html = """
        <!-- Top Left Quarter Circle -->
        <div class="quarter-circle top-left"></div>
        
        <!-- Bottom Right Quarter Circle -->
        <div class="quarter-circle bottom-right"></div>
        """
    
    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Geometric Thank You Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Kalam:wght@700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Caveat', cursive;
            overflow: hidden;
            margin: 0;
            padding: 0;
            width: 100vw;
            height: 100vh;
            background: #e5e5e5;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .slide-container {{
            width: 100vw;
            height: 100vh;
            max-width: 100%;
            max-height: 100%;
            background: {bg_color};
            position: relative;
            overflow: hidden;
            padding: 3vw;
            {border_style}
        }}
        
        .content {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            z-index: 10;
        }}
        
        .main-text {{
            font-size: 8rem;
            font-weight: 700;
            color: {text_color};
            line-height: 1.2;
        }}
        
        .circle {{
            position: absolute;
            background: {circle_color};
            border-radius: 50%;
        }}
        
        .quarter-circle {{
            position: absolute;
            width: 280px;
            height: 280px;
            background: {corner_shape_color};
        }}
        
        .quarter-circle.top-left {{
            top: 0;
            left: 0;
            border-radius: 0 0 100% 0;
        }}
        
        .quarter-circle.bottom-right {{
            bottom: 0;
            right: 0;
            border-radius: 100% 0 0 0;
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <div class="slide-container">
        {corner_shapes_html}
        
        {circles_html}
        
        <div class="content">
            <div class="main-text">{main_text}</div>
        </div>
    </div>
</body>
</html>
"""
    
    return html_code

def generate_thank_you_slide_6(
    main_text="Thank you",
    bg_color="#F5E6D3",
    text_color="#1a3a52",
    show_decorative_elements=True,
    show_olive_branches=True,
    font_family="'Dancing Script', 'Brush Script MT', cursive",
    custom_css=""
):
    """
    Generate a 'Thank you' slide with elegant decorative elements.
    
    Args:
        main_text (str): Main text to display (default: "Thank you")
        bg_color (str): Background color (default: beige #F5E6D3)
        text_color (str): Text color (default: navy #1a3a52)
        show_decorative_elements (bool): Show sunburst patterns and dots
        show_olive_branches (bool): Show olive branch decorations
        font_family (str): Font family for the main text
        custom_css (str): Additional custom CSS
    
    Returns:
        str: Complete HTML code for the thank you slide
    """
    
    # Sunburst pattern SVG (decorative circular patterns)
    sunburst_pattern = '''
    <g class="sunburst">
        <circle cx="0" cy="0" r="25" fill="none" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="0" y1="-35" x2="0" y2="-30" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="24.7" y1="-17.5" x2="21.2" y2="-15" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="24.7" y1="17.5" x2="21.2" y2="15" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="0" y1="35" x2="0" y2="30" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="-24.7" y1="17.5" x2="-21.2" y2="15" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="-24.7" y1="-17.5" x2="-21.2" y2="-15" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="17.5" y1="-24.7" x2="15" y2="-21.2" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="17.5" y1="24.7" x2="15" y2="21.2" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="-17.5" y1="24.7" x2="-15" y2="21.2" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="-17.5" y1="-24.7" x2="-15" y2="-21.2" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="35" y1="0" x2="30" y2="0" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
        <line x1="-35" y1="0" x2="-30" y2="0" stroke="#d4c5b0" stroke-width="1.5" opacity="0.6"/>
    </g>
    '''
    
    # Olive branch SVG paths
    olive_branch_top = '''
    <g transform="translate(960, 220)">
        <path d="M 0,0 Q -5,-15 -10,-25" stroke="#7a8b7e" stroke-width="3" fill="none" stroke-linecap="round"/>
        <ellipse cx="-8" cy="-10" rx="8" ry="12" fill="#7a8b7e" opacity="0.8"/>
        <ellipse cx="-12" cy="-20" rx="7" ry="11" fill="#8a9b8e" opacity="0.8"/>
        <ellipse cx="-4" cy="-22" rx="6" ry="10" fill="#6a7b6e" opacity="0.8"/>
    </g>
    '''
    
    olive_branch_bottom = '''
    <g transform="translate(960, 580)">
        <path d="M 0,0 Q -8,12 -15,25" stroke="#7a8b7e" stroke-width="3" fill="none" stroke-linecap="round"/>
        <ellipse cx="-5" cy="8" rx="6" ry="10" fill="#8a9b8e" opacity="0.8"/>
        <ellipse cx="-10" cy="15" rx="7" ry="11" fill="#7a8b7e" opacity="0.8"/>
        <ellipse cx="-13" cy="22" rx="6" ry="10" fill="#6a7b6e" opacity="0.8"/>
    </g>
    '''
    generate_mission_slide
    # Decorative elements HTML
    decorative_elements_html = ""
    if show_decorative_elements:
        # Sunburst patterns at various positions
        sunburst_positions = [
            (250, 180), (450, 320), (250, 650), (320, 880),
            (1470, 120), (1670, 280), (1520, 650), (1700, 850),
            (750, 850), (1150, 820)
        ]
        
        for x, y in sunburst_positions:
            decorative_elements_html += f'<g transform="translate({x}, {y})">{sunburst_pattern}</g>'
        
        # Colored dots scattered around
        dots = [
            (356, 168, "#4a7c59"), (820, 165, "#d4a574"), (528, 190, "#e8b4a8"),
            (600, 110, "#f0f0f0"), (910, 110, "#f0f0f0"), (910, 460, "#e8b4a8"),
            (808, 470, "#d4a574"), (660, 250, "#d4a574"), (560, 560, "#4a7c59"),
            (1180, 250, "#f0f0f0"), (1000, 250, "#e8b4a8"), (1180, 450, "#4a7c59"),
            (445, 450, "#f0f0f0"), (810, 620, "#d4a574"), (865, 755, "#e8b4a8"),
            (710, 750, "#d4a574"), (340, 750, "#e8b4a8")
        ]
        
        for x, y, color in dots:
            decorative_elements_html += f'<circle cx="{x}" cy="{y}" r="4" fill="{color}" opacity="0.7"/>'
    
    # Olive branches HTML
    olive_branches_html = ""
    if show_olive_branches:
        olive_branches_html = olive_branch_top + olive_branch_bottom
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            width: 1920px;
            height: 1080px;
            background: {bg_color};
            overflow: hidden;
            position: relative;
        }}
        
        .decorative-svg {{
            position: absolute;
            top: 0;
            left: 0;
            width: 1920px;
            height: 1080px;
            z-index: 1;
        }}
        
        .thank-you-text {{
            position: absolute;
            top: 460px;
            left: 0;
            width: 100%;
            font-family: {font_family};
            font-size: 160px;
            color: {text_color};
            font-weight: 400;
            line-height: 1;
            margin: 0;
            font-style: italic;
            text-align: center;
            z-index: 10;
        }}
        
        {custom_css}
    </style>
</head>
<body>
    <svg class="decorative-svg" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
        {decorative_elements_html}
        {olive_branches_html}
    </svg>
    
    <h1 class="thank-you-text">{main_text}</h1>
</body>
</html>"""
    
    return html_code

def generate_thank_you_slide_7(
    main_text="THANK YOU!",
    bg_color="#F5F3F0",
    text_color="#7A6350",
    font_family="'Playfair Display', 'Georgia', serif"
):
    """
    Generate a thank you slide.
    
    Args:
        main_text (str): Main text to display (default: "THANK YOU!")
        bg_color (str): Background color (default: "#F5F3F0" - light warm gray)
        text_color (str): Text color (default: "#7A6350" - brown/taupe)
        font_family (str): Font family for main text
    
    Returns:
        str: Complete HTML code for the slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thank You Slide</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            width: 1920px;
            height: 1080px;
            font-family: {font_family};
            background: {bg_color};
            overflow: hidden;
            position: relative;
        }}
        
        .main-text {{
            position: absolute;
            top: 390px;
            left: 0;
            width: 100%;
            font-family: {font_family};
            font-size: 130px;
            font-weight: 400;
            color: {text_color};
            letter-spacing: 8px;
            text-align: center;
            z-index: 2;
            white-space: nowrap;
        }}
    </style>
</head>
<body>
    <div class="main-text">{main_text}</div>
</body>
</html>"""
    
    return html_code


def generate_modern_contact_slide(
    main_title="Thank You For Attention",
    company_name="Thynk Unlimited",
    website="www.reallygreatsite.com",
    email="hello@reallygreatsite.com",
    phone="+123-456-7890",
    primary_color="#1E88E5",
    secondary_color="#1565C0",
    text_color="#FFFFFF",
    contact_text_color="#333333",
    top_image_url="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop",
    bottom_image_url="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=2070&auto=format&fit=crop",
    font_family="'Roboto', sans-serif",
    show_logo=True
):
    """
    Generate a modern, geometric style 'Thank You' or Contact slide. 
    Features a dynamic blue angular overlay, integrated image placeholders, and a clean contact information section.

    :param main_title: The central large text (e.g., 'Thank You', 'Contact Us').
    :param company_name: Name of the company displayed near the logo.
    :param website: Website URL to display.
    :param email: Contact email address.
    :param phone: Contact phone number.
    :param primary_color: Main accent color (typically blue) for the geometric shape.
    :param secondary_color: Darker shade for gradients/depth.
    :param text_color: Color of the main title text on the colored background.
    :param contact_text_color: Color of the contact details on the white background.
    :param top_image_url: URL for the top-right background image (charts/abstract).
    :param bottom_image_url: URL for the bottom-right corner image (team/office).
    :param font_family: Font family for all text elements.
    :param show_logo: Whether to display the logo placeholder.
    :return: A string containing the HTML code for the slide.
    """

    # SVG Icons
    logo_svg = f"""
    <svg width="50" height="50" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5 45H45" stroke="{primary_color}" stroke-width="4" stroke-linecap="round"/>
        <rect x="10" y="25" width="8" height="15" fill="{primary_color}"/>
        <rect x="22" y="15" width="8" height="25" fill="{secondary_color}"/>
        <rect x="34" y="5" width="8" height="35" fill="{primary_color}"/>
    </svg>
    """

    globe_icon = f"""
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="{primary_color}" stroke-width="2"/>
        <path d="M2 12H22" stroke="{primary_color}" stroke-width="2"/>
        <path d="M12 2C14.5013 4.73835 15.9228 8.29203 16 12C15.9228 15.708 14.5013 19.2616 12 22C9.49872 19.2616 8.07725 15.708 8 12C8.07725 8.29203 9.49872 4.73835 12 2V2Z" stroke="{primary_color}" stroke-width="2"/>
    </svg>
    """

    email_icon = f"""
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="5" width="18" height="14" rx="2" stroke="{primary_color}" stroke-width="2"/>
        <path d="M3 7L12 13L21 7" stroke="{primary_color}" stroke-width="2"/>
    </svg>
    """

    phone_icon = f"""
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 16.92V19.92C22.0011 20.1986 21.9441 20.4742 21.8325 20.7294C21.7209 20.9846 21.5573 21.2137 21.3521 21.4019C21.1468 21.5901 20.9046 21.7331 20.6412 21.8215C20.3778 21.9099 20.0991 21.9416 19.823 21.914C16.7428 21.5796 13.7828 20.5252 11.16 18.81C8.68233 17.2023 6.64333 15.0933 5.12 12.59C3.5855 9.94723 2.66249 6.97341 2.44 3.89C2.41979 3.61483 2.45887 3.33777 2.55469 3.07693C2.6505 2.8161 2.8009 2.57745 2.99608 2.3768C3.19126 2.17614 3.42681 2.01809 3.68749 1.91295C3.94817 1.80781 4.22817 1.75803 4.51 1.767H7.51C8.00645 1.76229 8.48628 1.94162 8.86178 2.27218C9.23727 2.60274 9.48208 3.06129 9.552 3.564C9.67843 4.52055 9.91244 5.45942 10.25 6.36C10.3546 6.63854 10.3756 6.94273 10.3106 7.23277C10.2456 7.52281 10.0975 7.78508 9.885 7.985L8.615 9.255C10.0384 11.7578 12.1222 13.8416 14.625 15.265L15.895 13.995C16.1054 13.7915 16.3707 13.6508 16.6586 13.5898C16.9465 13.5288 17.2447 13.5501 17.518 13.651C18.4238 13.9902 19.3683 14.2248 20.33 14.351C20.8407 14.4239 21.3045 14.6789 21.6335 15.0678C21.9626 15.4566 22.1341 15.9525 22.115 16.455V16.92Z" stroke="{primary_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """

    html_code = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{main_title}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap" rel="stylesheet">
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
                background-color: #FFFFFF;
            }}
            
            .outer-wrapper {{
                padding: 0;
                box-sizing: border-box;
                width: 1920px;
                height: 1080px;
                overflow: hidden;
            }}

            /* Content wrapper for scaling */
            .content-wrapper {{
                position: absolute;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                width: 1920px;
                height: 1080px;
                overflow: hidden;
                background: #FFFFFF;
            }}
            
            .slide-container {{
                width: 1920px;
                height: 1080px;
                position: relative;
                background-color: #FFFFFF;
            }}

            /* --- Header / Logo Section --- */
            .header {{
                position: absolute;
                top: 50px;
                left: 80px;
                display: flex;
                align-items: center;
                gap: 20px;
                z-index: 20;
            }}

            .company-name {{
                font-size: 28px;
                font-weight: 500;
                color: #000;
                letter-spacing: 1px;
            }}

            /* --- Background Images --- */
            .top-right-image {{
                position: absolute;
                top: 0;
                right: 0;
                width: 65%;
                height: 60%;
                z-index: 1;
                overflow: hidden;
            }}

            .top-right-image img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                /* Mask to create the diagonal feel for the image underneath */
                clip-path: polygon(20% 0, 100% 0, 100% 100%, 0% 100%);
            }}

            .bottom-right-image {{
                position: absolute;
                bottom: 0;
                right: 0;
                width: 45%;
                height: 50%;
                z-index: 2;
            }}

            .bottom-right-image img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                /* Triangle cut for bottom corner */
                clip-path: polygon(30% 0, 100% 0, 100% 100%, 0% 100%);
            }}

            /* --- Main Geometric Blue Overlay --- */
            .blue-overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10;
                pointer-events: none; /* Let clicks pass through if needed */
            }}

            .blue-shape {{
                position: absolute;
                top: 20%;
                left: 0;
                width: 110%; /* Extend slightly to ensure coverage */
                height: 45%;
                background: linear-gradient(90deg, {primary_color} 0%, {secondary_color} 100%);
                /* Complex polygon to match the sample slide: starts flat, goes up, cuts down sharp */
                clip-path: polygon(
                    0% 20%,     /* Top Left Start */
                    35% 0%,     /* Angle Up */
                    100% 35%,   /* Top Right */
                    100% 80%,   /* Bottom Right */
                    75% 100%,   /* Angle Down */
                    0% 75%      /* Bottom Left */
                );
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                padding-left: 80px;
            }}

            .main-title {{
                font-size: 100px;
                font-weight: 900;
                color: {text_color};
                text-transform: capitalize;
                line-height: 1.1;
                margin-top: -20px; /* Slight optical adjustment */
                text-shadow: 0 4px 10px rgba(0,0,0,0.2);
                width: 70%;
            }}

            /* --- Contact Section --- */
            .contact-section {{
                position: absolute;
                bottom: 80px;
                left: 80px;
                display: flex;
                flex-direction: column;
                gap: 40px;
                z-index: 20;
            }}

            .contact-item {{
                display: flex;
                align-items: center;
                gap: 25px;
            }}

            .contact-text {{
                font-size: 32px;
                color: {contact_text_color};
                font-weight: 500;
            }}
            
            /* Decorative line under contacts */
            .contact-line {{
                height: 2px;
                width: 500px;
                background-color: {primary_color};
                margin-top: -10px;
                margin-left: 65px; /* Align with text */
                opacity: 0.7;
            }}

        </style>
    </head>
    <body>
        <div class="outer-wrapper">
            <div class="content-wrapper">
                <div class="slide-container">
                    
                    <div class="header">
                        {logo_svg if show_logo else ""}
                        <div class="company-name">{company_name}</div>
                    </div>

                    <div class="top-right-image">
                        <img src="{top_image_url}" alt="Business Analysis">
                    </div>
                    
                    <div class="blue-overlay">
                        <div class="blue-shape">
                            <h1 class="main-title">{main_title}</h1>
                        </div>
                    </div>

                    <div class="bottom-right-image">
                        <img src="{bottom_image_url}" alt="Teamwork">
                    </div>

                    <div class="contact-section">
                        <div class="contact-item">
                            {globe_icon}
                            <div class="contact-text">{website}</div>
                        </div>
                        <div class="contact-line"></div>
                        
                        <div class="contact-item">
                            {email_icon}
                            <div class="contact-text">{email}</div>
                        </div>
                        <div class="contact-line"></div>
                        
                        <div class="contact-item">
                            {phone_icon}
                            <div class="contact-text">{phone}</div>
                        </div>
                        <div class="contact-line"></div>
                    </div>

                </div>
            </div>
        </div>
    </body>
    </html>"""
    
    return html_code


def generate_closing_slide(
    main_text="THANK\nYOU!",
    quote_text="“Efficiency opens up more time to focus on the things that really matter.”",
    contact_text="@reallygreatsite",
    image_url="https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    bg_color="#FDFBF7",
    primary_color="#263238",
    accent_shape_color="#DDE6ED",
    font_family="'DM Sans', sans-serif",
    show_sunburst=True,
    show_dots=True,
    custom_css=""
):
    """
    Generate a modern, minimalist closing slide with a circular image mask, geometric accents, and bold typography.
    Suitable for "Thank You" slides, contact pages, or final thoughts.

    :param main_text: The large closing text (e.g., "THANK YOU!"). Supports newline characters.
    :param quote_text: A closing thought, quote, or secondary message displayed on the left.
    :param contact_text: Contact information or social media handle (e.g., "@username").
    :param image_url: URL for the feature image which will be masked in a circle.
    :param bg_color: Background color of the slide (hex code).
    :param primary_color: Color for the text and main graphic elements (hex code).
    :param accent_shape_color: Color for the decorative background shape behind the image (hex code).
    :param font_family: Font family for the text.
    :param show_sunburst: Whether to show the sunburst/line graphic.
    :param show_dots: Whether to show the dot grid pattern.
    :param custom_css: Additional CSS to override styles.
    :return: A string containing the HTML code for the slide.
    """

    # SVG Definitions
    sunburst_svg = f"""
    <svg class="sunburst-icon" viewBox="0 0 100 100" fill="none" stroke="{primary_color}" stroke-width="2" stroke-linecap="round">
        <line x1="50" y1="10" x2="50" y2="30" />
        <line x1="50" y1="70" x2="50" y2="90" />
        <line x1="90" y1="50" x2="70" y2="50" />
        <line x1="30" y1="50" x2="10" y2="50" />
        <line x1="78.28" y1="21.72" x2="64.14" y2="35.86" />
        <line x1="35.86" y1="64.14" x2="21.72" y2="78.28" />
        <line x1="78.28" y1="78.28" x2="64.14" y2="64.14" />
        <line x1="35.86" y1="35.86" x2="21.72" y2="21.72" />
        <circle cx="50" cy="50" r="8" fill="none" />
    </svg>
    """ if show_sunburst else ""

    # Generate Dot Pattern SVG
    dots_content = ""
    for r in range(4):
        for c in range(10):
            dots_content += f'<circle cx="{c * 15 + 5}" cy="{r * 15 + 5}" r="2.5" fill="{accent_shape_color}" />'
    
    dots_svg = f"""
    <svg class="dots-pattern" viewBox="0 0 150 60" xmlns="http://www.w3.org/2000/svg">
        {dots_content}
    </svg>
    """ if show_dots else ""

    # Search Icon SVG for contact
    search_icon_svg = f"""
    <svg class="search-icon" viewBox="0 0 24 24" fill="{primary_color}" xmlns="http://www.w3.org/2000/svg">
         <path d="M11 19C15.4183 19 19 15.4183 19 11C19 6.58172 15.4183 3 11 3C6.58172 3 3 6.58172 3 11C3 15.4183 6.58172 19 11 19Z" stroke="white" stroke-width="2" fill="{primary_color}"/>
         <path d="M21 21L16.65 16.65" stroke="{primary_color}" stroke-width="2" stroke-linecap="round"/>
    </svg>
    """

    formatted_main_text = main_text.replace('\n', '<br>')

    html_code = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Closing Slide</title>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
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
                background-color: {bg_color};
                color: {primary_color};
            }}
            
            body {{
                display: grid;
                grid-template-columns: 45% 55%;
                padding: 100px;
                position: relative;
            }}

            /* --- Left Column --- */
            .left-col {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                position: relative;
                padding-right: 50px;
            }}

            .quote-block {{
                font-size: 2.8rem;
                font-weight: 700;
                line-height: 1.3;
                margin-bottom: 80px;
                color: {primary_color};
                z-index: 10;
            }}

            .image-composition {{
                position: relative;
                width: 500px;
                height: 500px;
            }}

            .accent-blob {{
                position: absolute;
                bottom: -40px;
                left: -80px;
                width: 450px;
                height: 450px;
                background-color: {accent_shape_color};
                border-top-right-radius: 50%;
                border-bottom-right-radius: 20%;
                border-top-left-radius: 10%;
                z-index: 1;
            }}

            .image-circle {{
                width: 400px;
                height: 400px;
                border-radius: 50%;
                overflow: hidden;
                position: absolute;
                top: 0;
                left: 40px;
                z-index: 2;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}

            .image-circle img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}

            /* --- Right Column --- */
            .right-col {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                position: relative;
                padding-left: 50px;
            }}

            .decorations-top {{
                display: flex;
                align-items: center;
                gap: 40px;
                margin-bottom: 40px;
            }}

            .sunburst-icon {{
                width: 120px;
                height: 120px;
                opacity: 0.6;
            }}

            .dots-pattern {{
                width: 200px;
                height: 80px;
                opacity: 0.8;
            }}

            .contact-info {{
                display: flex;
                align-items: center;
                gap: 15px;
                font-size: 1.5rem;
                font-weight: 500;
                color: #7f8c8d;
                margin-bottom: 20px;
            }}

            .search-icon {{
                width: 30px;
                height: 30px;
            }}

            .main-title {{
                font-size: 11rem;
                line-height: 0.9;
                font-weight: 800;
                text-transform: uppercase;
                color: {primary_color};
                letter-spacing: -2px;
                margin-bottom: 30px;
            }}

            .title-underline {{
                width: 100%;
                max-width: 600px;
                height: 12px;
                background-color: {primary_color};
                border-radius: 6px;
            }}

            {custom_css}
        </style>
    </head>
    <body>
        <div class="left-col">
            <div class="quote-block">
                {quote_text}
            </div>
            
            <div class="image-composition">
                <div class="accent-blob"></div>
                <div class="image-circle">
                    <img src="{image_url}" alt="Smart Living" />
                </div>
            </div>
        </div>

        <div class="right-col">
            <div class="decorations-top">
                {sunburst_svg}
                {dots_svg}
            </div>

            <div class="contact-info">
                {search_icon_svg}
                <span>{contact_text}</span>
            </div>

            <h1 class="main-title">{formatted_main_text}</h1>
            <div class="title-underline"></div>
        </div>
    </body>
    </html>"""

    return html_code

def generate_minimalist_thank_you_slide(
    main_title="THANK<br>YOU",
    company_name="Timmerman Industries",
    date_text="02 May, 2024",
    primary_color="#59664D",
    secondary_color="#E8E8E8",
    bg_color="#FFFFFF",
    font_family="'Arial', sans-serif",
    show_shapes=True,
    custom_css=""
):
    """
    Generate a modern, minimalist 'Thank You' slide with geometric accents and vertical typography.
    Designed for 1920x1080 resolution.

    :param main_title: The main text content (supports <br> for line breaks). Default is stacked "THANK YOU".
    :param company_name: Text displayed vertically on the left side.
    :param date_text: Date or footer text displayed on the bottom right.
    :param primary_color: Main accent color for text and small decorations (Hex code).
    :param secondary_color: Color for the large geometric background blocks (Hex code).
    :param bg_color: Background color of the slide (Hex code).
    :param font_family: Font family for all text elements.
    :param show_shapes: Whether to show the geometric background blocks.
    :param custom_css: Additional custom CSS to be included.
    :return: A string containing the HTML code for the slide.
    """

    # SVG Definitions for Geometric Shapes
    
    # 1. Top Right Rectangle (Gray Block)
    rect_top_right_svg = f"""
    <div class="shape-rect-top-right">
        <svg width="500" height="300" viewBox="0 0 500 300" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="300" fill="{secondary_color}"/>
        </svg>
    </div>
    """ if show_shapes else ""

    # 2. Bottom Left Rectangle (Gray Block)
    rect_bottom_left_svg = f"""
    <div class="shape-rect-bottom-left">
        <svg width="500" height="300" viewBox="0 0 500 300" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="300" fill="{secondary_color}"/>
        </svg>
    </div>
    """ if show_shapes else ""

    # 3. Top Left Circle (Green Dot)
    circle_dot_svg = f"""
    <div class="shape-circle-dot">
        <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="30" cy="30" r="25" fill="{secondary_color if not show_shapes else '#C2C5AA'}"/> 
            <circle cx="30" cy="30" r="25" fill="{primary_color}" fill-opacity="0.4"/>
        </svg>
    </div>
    """

    # 4. Bottom Right Dotted Line
    dotted_line_svg = f"""
    <div class="shape-dotted-line">
        <svg width="20" height="250" viewBox="0 0 20 250" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="10" y1="0" x2="10" y2="250" stroke="{secondary_color}" stroke-width="8" stroke-dasharray="15 15" stroke-linecap="square"/>
        </svg>
    </div>
    """

    html_code = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thank You Slide</title>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&display=swap" rel="stylesheet">
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
                background-color: {bg_color};
                overflow: hidden;
                color: {primary_color};
            }}
            
            body {{
                position: relative;
            }}

            /* --- Geometric Shapes Positioning --- */
            .shape-rect-top-right {{
                position: absolute;
                top: 0;
                right: 0;
                z-index: 1;
            }}

            .shape-rect-bottom-left {{
                position: absolute;
                bottom: 0;
                left: 0;
                z-index: 1;
            }}

            .shape-circle-dot {{
                position: absolute;
                top: 80px;
                left: 80px;
                z-index: 2;
            }}

            .shape-dotted-line {{
                position: absolute;
                bottom: 80px;
                right: 280px; /* Positioned to the left of the date */
                z-index: 2;
            }}

            /* --- Text Content --- */
            .main-title {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 13rem; /* Huge size matching the image */
                font-weight: 700;
                text-transform: uppercase;
                line-height: 0.9;
                text-align: center;
                z-index: 10;
                letter-spacing: -2px;
            }}

            .vertical-text {{
                position: absolute;
                top: 350px; /* Adjusted to center vertically roughly */
                left: 100px;
                font-size: 1.8rem;
                font-weight: 400;
                text-transform: uppercase;
                letter-spacing: 2px;
                transform: rotate(-90deg);
                transform-origin: left top;
                white-space: nowrap;
                z-index: 10;
                color: {primary_color};
                opacity: 0.9;
            }}

            .date-text {{
                position: absolute;
                bottom: 80px;
                right: 80px;
                font-size: 2rem;
                font-weight: 400;
                text-align: right;
                z-index: 10;
                color: {primary_color};
            }}

            {custom_css}
        </style>
    </head>
    <body>
        {rect_top_right_svg}
        {rect_bottom_left_svg}
        {circle_dot_svg}
        {dotted_line_svg}

        <div class="vertical-text">{company_name}</div>
        
        <h1 class="main-title">{main_title}</h1>
        
        <div class="date-text">{date_text}</div>
    </body>
    </html>"""

    return html_code

def generate_minimalist_sage_slide(
    main_text="THANK YOU",
    top_text="Timmerman Industries",
    bottom_text="02 May, 2024",
    bg_color="#F7F9F9",
    accent_color="#FFDAC1",
    shape_color="#E0E7E5",
    text_color="#1A2F28",
    font_family="'Montserrat', sans-serif",
    show_glow_effects=True
):
    """
    Generates a minimalist slide with a soft sage green theme, featuring organic curved shapes 
    and soft glowing accents. Suitable for 'Thank You' slides, Title slides, or Section breaks.

    :param main_text: The central, largest text on the slide (e.g., "THANK YOU").
    :param top_text: Small text displayed at the top center (e.g., Company Name).
    :param bottom_text: Small text displayed at the bottom center (e.g., Date or Website).
    :param bg_color: The background color of the slide (Hex code).
    :param accent_color: Color for the glowing accents/orbs (Hex code, usually peach/orange).
    :param shape_color: Color for the large geometric curved shapes (Hex code, usually sage green).
    :param text_color: Color of the text elements (Hex code).
    :param font_family: Font family to use.
    :param show_glow_effects: Whether to render the soft blurred gradient orbs.
    :return: A string containing the HTML code for the slide.
    """

    # SVG Definitions for gradients and shapes
    # Creating a soft radial gradient for the "glow" effect
    svg_defs = f"""
    <defs>
        <filter id="blurFilter" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="30" />
        </filter>
        <radialGradient id="glowGradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
            <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="{accent_color}" stop-opacity="0"/>
        </radialGradient>
    </defs>
    """

    # Top Left Corner Shape (Quarter circle/blob)
    top_left_svg = f"""
    <svg class="shape-corner-tl" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
        <path d="M0,0 L300,0 A300,300 0 0,1 0,300 Z" fill="{shape_color}" opacity="0.5"/>
    </svg>
    """

    # Top Right Corner Shape
    top_right_svg = f"""
    <svg class="shape-corner-tr" viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
        <path d="M300,0 L0,0 A300,300 0 0,0 300,300 Z" fill="{shape_color}" opacity="0.5"/>
    </svg>
    """

    # Side Semi-circles (Left and Right)
    side_shapes_svg = f"""
    <svg class="shape-side-left" viewBox="0 0 150 400" xmlns="http://www.w3.org/2000/svg">
        <path d="M0,0 A200,400 0 0,1 0,400 Z" fill="{shape_color}" transform="translate(0,0) scale(-1,1) translate(-150,0)"/> 
        <ellipse cx="0" cy="200" rx="150" ry="300" fill="{shape_color}" opacity="0.6"/>
    </svg>
    <svg class="shape-side-right" viewBox="0 0 150 400" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="150" cy="200" rx="150" ry="300" fill="{shape_color}" opacity="0.6"/>
    </svg>
    """

    # Bottom Arch/Hill
    bottom_arch_svg = f"""
    <svg class="shape-bottom" viewBox="0 0 1920 300" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
        <path d="M0,300 L0,150 Q960,-100 1920,150 L1920,300 Z" fill="{shape_color}" opacity="0.4"/>
    </svg>
    """

    # Glow/Sparkle effects (Peach blobs)
    glow_effects_html = ""
    if show_glow_effects:
        glow_effects_html = f"""
        <svg class="glow-tl" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            {svg_defs}
            <circle cx="100" cy="100" r="80" fill="url(#glowGradient)" filter="url(#blurFilter)"/>
        </svg>
        <svg class="glow-tr" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="80" fill="url(#glowGradient)" filter="url(#blurFilter)"/>
        </svg>
        <svg class="sparkle-top" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
             <path d="M50,0 C55,40 60,45 100,50 C60,55 55,60 50,100 C45,60 40,55 0,50 C40,45 45,40 50,0 Z" fill="{accent_color}" opacity="0.8"/>
        </svg>
        <svg class="glow-bottom" viewBox="0 0 600 300" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="300" cy="300" rx="300" ry="150" fill="url(#glowGradient)" filter="url(#blurFilter)" opacity="0.7"/>
        </svg>
        """

    html_code = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Minimalist Sage Slide</title>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap" rel="stylesheet">
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

            body {{
                position: relative;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }}

            /* Typography */
            .top-text {{
                position: absolute;
                top: 80px;
                font-size: 1.5rem;
                letter-spacing: 0.1em;
                font-weight: 500;
                color: {text_color};
                opacity: 0.8;
                z-index: 20;
            }}

            .main-text {{
                font-size: 8rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: -0.02em;
                color: {text_color};
                z-index: 20;
                text-align: center;
                line-height: 1.1;
            }}

            .bottom-text {{
                position: absolute;
                bottom: 80px;
                font-size: 1.25rem;
                letter-spacing: 0.05em;
                color: {text_color};
                opacity: 0.7;
                z-index: 20;
                font-weight: 500;
            }}

            /* Shapes Positioning */
            .shape-corner-tl {{
                position: absolute;
                top: -50px;
                left: -50px;
                width: 300px;
                height: 300px;
                z-index: 1;
            }}

            .shape-corner-tr {{
                position: absolute;
                top: -50px;
                right: -50px;
                width: 300px;
                height: 300px;
                z-index: 1;
            }}

            .shape-side-left {{
                position: absolute;
                top: 50%;
                left: 0;
                transform: translateY(-50%);
                width: 150px;
                height: 400px;
                z-index: 1;
            }}

            .shape-side-right {{
                position: absolute;
                top: 50%;
                right: 0;
                transform: translateY(-50%);
                width: 150px;
                height: 400px;
                z-index: 1;
            }}

            .shape-bottom {{
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 400px;
                z-index: 1;
            }}

            /* Glow & Sparkle Positioning */
            .glow-tl {{
                position: absolute;
                top: 0;
                left: 0;
                width: 200px;
                height: 200px;
                z-index: 2;
            }}

            .glow-tr {{
                position: absolute;
                top: 0;
                right: 0;
                width: 200px;
                height: 200px;
                z-index: 2;
            }}
            
            .sparkle-top {{
                position: absolute;
                top: 150px;
                left: 50%;
                transform: translateX(-50%);
                width: 60px;
                height: 60px;
                z-index: 5;
            }}
            
            .sparkle-top-right {{
                position: absolute;
                top: 150px;
                right: 300px;
                width: 40px;
                height: 40px;
                z-index: 5;
            }}

            .glow-bottom {{
                position: absolute;
                bottom: 0;
                left: 50%;
                transform: translateX(-50%);
                width: 800px;
                height: 400px;
                z-index: 0;
                pointer-events: none;
            }}

        </style>
    </head>
    <body>
        {top_left_svg}
        {top_right_svg}
        {side_shapes_svg}
        {bottom_arch_svg}
        {glow_effects_html}
        
        <svg class="sparkle-top-right" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <path d="M50,0 C55,40 60,45 100,50 C60,55 55,60 50,100 C45,60 40,55 0,50 C40,45 45,40 50,0 Z" fill="{accent_color}" opacity="0.6"/>
        </svg>

        <div class="top-text">{top_text}</div>
        <div class="main-text">{main_text}</div>
        <div class="bottom-text">{bottom_text}</div>
    </body>
    </html>"""

    return html_code

def generate_thank_you_so_much_slide(
    main_text="Thank You",
    sub_text="So Much",
    presenter_label="Presented by :",
    presenter_name="Cahaya Dewi",
    organization_name="Larana University",
    phone_number="+123-456-7890",
    website="www.reallygreatsite.com",
    email="hello@reallygreatsite.com",
    bg_color="#F9F7F2",
    text_color="#5A6B6D",
    accent_color="#5A6B6D",
    font_family="'Inter', sans-serif",
    show_corner_accent=True
):
    """
    Generates a minimalist 'Thank You' slide with large typography, contact details, and subtle geometric background shapes.
    Designed to match the 'Blue and Beige Modern Minimalist' aesthetic.

    :param main_text: The primary large text (e.g., "Thank You").
    :param sub_text: The secondary large text, usually thinner weight (e.g., "So Much").
    :param presenter_label: Label for the presenter section (e.g., "Presented by :").
    :param presenter_name: Name of the presenter.
    :param organization_name: Name of the university or organization shown in the top left.
    :param phone_number: Contact phone number.
    :param website: Contact website URL.
    :param email: Contact email address.
    :param bg_color: Main background color (Off-white/Cream).
    :param text_color: Main text color (Slate/Grey).
    :param accent_color: Color for icons and graphical elements.
    :param font_family: Font family to use.
    :param show_corner_accent: Whether to show the geometric arrow in the bottom left.
    :return: A string containing the HTML code for the slide.
    """

    # SVG Icons Definitions
    
    # 1. Logo Icon (Stylized Lotus/Flower)
    logo_svg = f"""
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 40C20 40 22 30 30 25C35 22 40 20 40 20C40 20 30 18 25 10C22 5 20 0 20 0C20 0 18 10 10 15C5 18 0 20 0 20C0 20 10 22 15 30C18 35 20 40 20 40Z" fill="{text_color}"/>
        <path d="M20 30C20 30 21 25 25 22.5C27.5 21 30 20 30 20C30 20 25 19 22.5 15C21 12.5 20 10 20 10C20 10 19 15 15 17.5C12.5 19 10 20 10 20C10 20 15 21 17.5 25C19 27.5 20 30 20 30Z" fill="{bg_color}"/>
    </svg>
    """

    # 2. Phone Icon
    phone_svg = f"""
    <svg width="24" height="24" viewBox="0 0 24 24" fill="{text_color}" xmlns="http://www.w3.org/2000/svg">
        <path d="M20.01 15.38C18.8 15.38 17.64 15.19 16.55 14.83C16.21 14.71 15.82 14.8 15.56 15.07L13.7 17.42C10.28 15.77 7.78 13.06 6.3 9.91L8.85 7.63C9.07 7.42 9.17 7.08 9.07 6.78C8.75 5.75 8.58 4.67 8.58 3.56C8.58 3.05 8.13 2.6 7.62 2.6H4.07C3.56 2.6 3.12 3.05 3.12 3.56C3.12 13.68 10.74 22 20.01 22C20.48 22 20.89 21.57 20.89 21.05V17.35C20.89 16.83 20.48 16.39 20.01 16.39V15.38Z"/>
    </svg>
    """

    # 3. Web/Globe Icon
    web_svg = f"""
    <svg width="24" height="24" viewBox="0 0 24 24" fill="{text_color}" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM11 19.93C7.05 19.44 4 16.08 4 12C4 11.38 4.08 10.79 4.21 10.21L9 15V16C9 17.1 9.9 18 11 18V19.93ZM17.9 17.39C17.64 16.58 16.9 16 16 16H15V13C15 12.45 14.55 12 14 12H8V10H10C10.55 10 11 9.55 11 9V7H13C14.1 7 15 6.1 15 5V4.59C17.93 5.78 20 8.65 20 12C20 14.08 19.2 15.97 17.9 17.39Z"/>
    </svg>
    """

    # 4. Email Icon
    email_svg = f"""
    <svg width="24" height="24" viewBox="0 0 24 24" fill="{text_color}" xmlns="http://www.w3.org/2000/svg">
        <path d="M20 4H4C2.9 4 2.01 4.9 2.01 6L2 18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6C22 4.9 21.1 4 20 4ZM20 8L12 13L4 8V6L12 11L20 6V8Z"/>
    </svg>
    """

    # 5. Corner Arrow Accent
    corner_arrow_svg = f"""
    <svg width="250" height="100" viewBox="0 0 250 100" fill="none" xmlns="http://www.w3.org/2000/svg" class="corner-accent">
        <path d="M0 100 L0 50 L50 0 L250 0" stroke="{text_color}" stroke-width="4" fill="none"/>
        <path d="M20 100 L20 70 L70 20 L250 20" stroke="{text_color}" stroke-width="2" stroke-opacity="0.5" fill="none"/>
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
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700;800&display=swap" rel="stylesheet">
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

            body {{
                position: relative;
                padding: 80px 100px;
                display: grid;
                grid-template-rows: auto 1fr auto;
                gap: 0;
            }}

            /* --- Background Decoration --- */
            .bg-circle {{
                position: absolute;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.4);
                z-index: 0;
            }}

            .circle-1 {{
                width: 800px;
                height: 800px;
                top: -200px;
                right: -100px;
                border: 1px solid rgba(0,0,0,0.03);
            }}

            .circle-2 {{
                width: 600px;
                height: 600px;
                bottom: -150px;
                right: 200px;
                background-color: rgba(255, 255, 255, 0.6);
            }}

            /* --- Header / Logo --- */
            header {{
                display: flex;
                align-items: center;
                gap: 15px;
                z-index: 10;
            }}

            header span {{
                font-size: 24px;
                font-weight: 600;
                color: {text_color};
                letter-spacing: -0.02em;
            }}

            /* --- Main Content (Center) --- */
            .title-container {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                z-index: 10;
            }}

            .title-huge {{
                font-size: 200px;
                font-weight: 800;
                line-height: 0.85;
                letter-spacing: -0.04em;
                color: {text_color};
                margin-bottom: 0px;
            }}

            .subtitle-huge {{
                font-size: 100px;
                font-weight: 300; /* Thin weight */
                line-height: 0.9;
                letter-spacing: -0.04em;
                color: {text_color};
            }}

            /* --- Footer (Bottom) --- */
            footer {{
                position: relative;
                z-index: 10;
            }}

            .presenter-info {{
                position: absolute;
                bottom: 200px;
                left: 100px;
                display: flex;
                flex-direction: column;
                gap: 8px;
                z-index: 10;
            }}

            .presenter-info > span:first-child {{
                font-size: 20px;
                opacity: 0.7;
                font-weight: 400;
            }}

            .presenter-info > span:last-child {{
                font-size: 32px;
                font-weight: 700;
                letter-spacing: -0.01em;
            }}

            .contact-list {{
                position: absolute;
                bottom: 0;
                right: 0;
                display: flex;
                flex-direction: column;
                gap: 20px;
                text-align: left;
            }}

            .contact-item {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}

            .contact-item svg {{
                width: 40px;
                height: 40px;
                padding: 8px;
                background-color: rgba(90, 107, 109, 0.1);
                border-radius: 50%;
            }}
            
            .contact-item span {{
                font-size: 18px;
                font-weight: 400;
                opacity: 0.9;
            }}

            /* --- Decorative Corner --- */
            .corner-accent {{
                position: absolute;
                bottom: 0;
                left: 0;
                width: 350px;
                height: 150px;
                z-index: 5;
                display: {("block" if show_corner_accent else "none")};
            }}

        </style>
    </head>
    <body>
        <!-- Background decorations -->
        <div class="bg-circle circle-1"></div>
        <div class="bg-circle circle-2"></div>
        {corner_arrow_svg}
        
        <!-- Semantic HTML structure -->
        <header>
            {logo_svg}
            <span>{organization_name}</span>
        </header>

        <div class="title-container">
            <h1 class="title-huge">{main_text}</h1>
            <h2 class="subtitle-huge">{sub_text}</h2>
        </div>

        <footer>
            <div class="presenter-info">
                <span>{presenter_label}</span>
                <span>{presenter_name}</span>
            </div>

            <nav class="contact-list">
                <div class="contact-item">
                    {phone_svg}
                    <span>{phone_number}</span>
                </div>
                <div class="contact-item">
                    {web_svg}
                    <span>{website}</span>
                </div>
                <div class="contact-item">
                    {email_svg}
                    <span>{email}</span>
                </div>
            </nav>
        </footer>
    </body>
    </html>"""

    return html_code

def generate_brand_collaboration_closing_slide(
    main_title="Thank you",
    message_text="THANK YOU FOR TAKING THE TIME TO VIEW THIS PRESENTATION. I APPRECIATE YOUR INTEREST AND CONSIDERATION, AND I'M EXCITED ABOUT THE POSSIBILITY OF WORKING TOGETHER. LET'S CREATE SOMETHING MEANINGFUL, IMPACTFUL, AND BEAUTIFULLY ALIGNED.",
    signature_text="Looking forward to connecting soon!",
    brand_header="BRAND COLLABORATION",
    website_url="WWW.REALLYGREATSITE.COM",
    prepared_by="PREPARED BY:<br>OLIVIA WILSON",
    date_text="DATE:<br>01\\06\\2030",
    primary_color="#1D4E89",
    bg_color="#F5F2EB",
    left_image_url="https://images.unsplash.com/photo-1519052537078-e6302a4968d4?q=80&w=1740&auto=format&fit=crop",
    right_image_url="https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1740&auto=format&fit=crop",
    title_font="'Playfair Display', serif",
    body_font="'DM Sans', sans-serif",
    script_font="'Mrs Saint Delafield', cursive"
):
    """
    Generate a sophisticated 'Thank You' or closing slide with an asymmetrical image layout,
    elegant typography mixing serif and script fonts, and a textured paper background feel.

    :param main_title: The large central title text (e.g., "Thank you").
    :param message_text: The uppercase body paragraph below the title.
    :param signature_text: The handwritten-style text at the bottom center.
    :param brand_header: Small uppercase text in the top left corner.
    :param website_url: Small uppercase text in the top right corner.
    :param prepared_by: Text for the bottom left corner (supports <br> for line breaks).
    :param date_text: Text for the bottom right corner (supports <br> for line breaks).
    :param primary_color: The main color for text (Hex code).
    :param bg_color: The background color (light beige/paper color).
    :param left_image_url: URL for the large vertical image on the left.
    :param right_image_url: URL for the smaller image on the right.
    :param title_font: Font family for the main title.
    :param body_font: Font family for body text and headers.
    :param script_font: Font family for the signature text.
    :return: HTML string of the slide.
    """

    # SVG Noise Pattern for Paper Texture Effect
    svg_texture = """
    <div>
        <svg style="position: absolute; width: 0; height: 0; overflow: hidden;">
            <filter id="paper-noise">
                <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" stitchTiles="stitch" result="noise"/>
                <feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.4 0" in="noise" result="coloredNoise"/>
            </filter>
        </svg>
    </div>
    """

    html_code = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Brand Collaboration Closing Slide</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,500;700&family=Mrs+Saint+Delafield&family=Playfair+Display:wght@400;600&display=swap" rel="stylesheet">
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
                overflow: hidden;
                background-color: {bg_color};
                color: {primary_color};
                font-family: {body_font};
            }}

            body {{
                position: relative;
            }}

            body::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                opacity: 0.15;
                filter: url(#paper-noise);
                z-index: 0;
                pointer-events: none;
            }}

            /* --- Header & Footer Metadata --- */
            .meta-text {{
                position: absolute;
                font-size: 1.2rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                z-index: 10;
            }}

            .top-left {{ top: 60px; left: 80px; }}
            .top-right {{ top: 60px; right: 80px; }}
            .bottom-left {{ bottom: 60px; left: 80px; line-height: 1.4; }}
            .bottom-right {{ bottom: 60px; right: 80px; text-align: right; line-height: 1.4; }}

            /* --- Images --- */
            .img-left {{
                position: absolute;
                left: 110px;
                top: 200px;
                width: 460px;
                height: 650px;
                z-index: 5;
                overflow: hidden;
                filter: grayscale(100%);
                transition: filter 0.3s ease;
            }}

            .img-right {{
                position: absolute;
                right: 200px;
                bottom: 220px;
                width: 250px;
                height: 280px;
                z-index: 5;
                overflow: hidden;
                filter: grayscale(100%);
                transition: filter 0.3s ease;
            }}

            .img-left img,
            .img-right img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}

            /* --- Center Content --- */
            .center-content {{
                position: absolute;
                left: 50%;
                top: 48%;
                transform: translate(-40%, -50%); /* Slightly offset to right because of large left image */
                width: 800px;
                text-align: center;
                z-index: 10;
            }}

            .main-title {{
                font-family: {title_font};
                font-size: 10rem; /* Huge text */
                font-weight: 400; /* Serif usually looks better regular/light at this size */
                line-height: 0.9;
                margin-bottom: 3rem;
                letter-spacing: -0.02em;
                transform: scaleY(1.1); /* Slight vertical stretch for elegance */
            }}

            .message-block {{
                font-family: {body_font};
                font-size: 1.1rem;
                line-height: 1.6;
                font-weight: 700;
                text-transform: uppercase;
                max-width: 750px;
                margin: 0 auto 3rem auto;
                letter-spacing: 0.05em;
                text-align: center;
            }}

            .signature {{
                font-family: {script_font};
                font-size: 4rem;
                font-weight: 400;
                opacity: 0.9;
                text-align: center;
            }}

        </style>
    </head>
    <body>
        {svg_texture}
        
        <span class="meta-text top-left">{brand_header}</span>
        <span class="meta-text top-right">{website_url}</span>
        <span class="meta-text bottom-left">{prepared_by}</span>
        <span class="meta-text bottom-right">{date_text}</span>

        <figure class="img-left">
            <img src="{left_image_url}" alt="Brand Mood Image Left" />
        </figure>
        
        <figure class="img-right">
            <img src="{right_image_url}" alt="Fashion Detail Image Right" />
        </figure>

        <main class="center-content">
            <h1 class="main-title">{main_title}</h1>
            <p class="message-block">
                {message_text}
            </p>
            <p class="signature">{signature_text}</p>
        </main>
    </body>
    </html>"""

    return html_code

def generate_military_thank_you_slide(
    main_text="THANK YOU",
    description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. In luctus fermentum risus nec feugiat. Nunc condimentum mauris blandit orci convallis dapibus.",
    bg_image_url="https://images.unsplash.com/photo-1590236141044-bc849495115d?q=80&w=1920",
    primary_color="#4B5320",
    secondary_color="#556B2F",
    text_color="#000000",
    font_family="'Arial Black', 'Arial', sans-serif",
    overlay_opacity=0.2
):
    """
    Generate a professional military-style closing or thank you slide.
    Features a split-diagonal layout with olive green accents and bold typography.

    :param main_text: Large prominent text (e.g., 'THANK YOU' or 'Q&A').
    :param description: Supporting paragraph text for details or contact info.
    :param bg_image_url: Background image for the right/underlay section.
    :param primary_color: Main olive green color for the diagonal stripes.
    :param secondary_color: Lighter green for the thin separator line.
    :param text_color: Color for the main and description text.
    :param font_family: Font used for the slide. Bold sans-serif recommended.
    :param overlay_opacity: Opacity of the image background overlay.
    :return: A string containing the HTML code for the slide.
    """

    html_code = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{main_text}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            html {{ width: 1920px; height: 1080px; font-size: 16px; }}
            body {{
                width: 1920px; height: 1080px;
                font-family: {font_family};
                overflow: hidden;
                background-color: #f0f0f0;
            }}

            .outer-wrapper {{
                width: 1920px; height: 1080px;
                overflow: hidden;
                position: relative;
            }}

            .content-wrapper {{
                position: absolute;
                width: 1920px; height: 1080px;
                display: flex;
                align-items: center;
            }}

            /* Image Background with Overlay */
            .bg-image {{
                position: absolute;
                right: 0; top: 0;
                width: 100%; height: 100%;
                background: url('{bg_image_url}') center/cover no-repeat;
                z-index: 1;
            }}
            
            .bg-overlay {{
                position: absolute;
                width: 100%; height: 100%;
                background: rgba(255, 255, 255, {overlay_opacity});
                z-index: 2;
            }}

            /* Geometric Accents */
            .diagonal-block {{
                position: absolute;
                left: -100px; top: 0;
                width: 450px;
                height: 100%;
                background: {primary_color};
                transform: skewX(-15deg);
                z-index: 3;
                box-shadow: 20px 0 50px rgba(0,0,0,0.2);
            }}

            .separator-line {{
                position: absolute;
                left: calc(450px + 20px); top: 0;
                width: 15px;
                height: 100%;
                background: white;
                transform: skewX(-15deg);
                z-index: 3;
            }}

            /* Content Area */
            .text-content {{
                position: absolute;
                right: 150px;
                width: 800px;
                z-index: 10;
                text-align: left;
            }}

            .main-title {{
                font-size: 180px;
                line-height: 0.9;
                font-weight: 900;
                color: {text_color};
                margin-bottom: 40px;
                text-transform: uppercase;
                letter-spacing: -5px;
            }}

            .description {{
                font-size: 28px;
                line-height: 1.6;
                color: {text_color};
                max-width: 700px;
                font-weight: 400;
            }}

            /* SVG Placeholder for badges/icons */
            .badge-container {{
                position: absolute;
                left: 100px;
                top: 50%;
                transform: translateY(-50%);
                z-index: 5;
            }}
        </style>
    </head>
    <body>
        <div class="outer-wrapper">
            <div class="bg-image"></div>
            <div class="bg-overlay"></div>
            
            <div class="content-wrapper">
                <div class="diagonal-block"></div>
                <div class="separator-line"></div>
                
                <div class="badge-container">
                    <svg width="120" height="120" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L4.5 20.29L5.21 21L12 18L18.79 21L19.5 20.29L12 2Z" />
                    </svg>
                </div>

                <div class="text-content">
                    <h1 class="main-title">{main_text}</h1>
                    <p class="description">{description}</p>
                </div>
            </div>
        </div>
    </body>
    </html>"""
    return html_code

def generate_corporate2_thank_you_slide(
    main_title="THANK YOU",
    closing_message="We look forward to collaborating with you.",
    contact_email="contact@business.com",
    website="www.business.com",
    primary_color="#1E3A8A",
    accent_color="#3B82F6",
    text_color="#1F2937",
    bg_color="#F8FAFC",
    font_family="'Inter', sans-serif"
):
    """
    Generates a professional corporate Thank You slide with contact information.
    Features a clean, structured layout with a side accent panel.
    """
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 1920px; height: 1080px; font-family: {font_family}; background-color: {bg_color}; overflow: hidden; }}
        
        .side-panel {{
            position: absolute;
            left: 0; top: 0; width: 480px; height: 1080px;
            background-color: {primary_color};
            z-index: 1;
        }}
        
        .accent-bar {{
            position: absolute;
            left: 480px; top: 0; width: 20px; height: 1080px;
            background-color: {accent_color};
            z-index: 2;
        }}

        .main-content {{
            position: absolute;
            left: 600px; top: 300px;
            width: 1100px;
            z-index: 3;
        }}

        .title {{
            font-size: 144px;
            font-weight: 900;
            color: {primary_color};
            letter-spacing: 4px;
            margin-bottom: 20px;
        }}

        .message {{
            font-size: 48px;
            color: {text_color};
            margin-bottom: 80px;
            opacity: 0.8;
        }}

        .contact-info {{
            font-size: 32px;
            color: {text_color};
            line-height: 1.6;
        }}

        .contact-item {{
            margin-bottom: 15px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="side-panel"></div>
    <div class="accent-bar"></div>
    <div class="main-content">
        <h1 class="title">{main_title}</h1>
        <p class="message">{closing_message}</p>
        <div class="contact-info">
            <div class="contact-item">Email: {contact_email}</div>
            <div class="contact-item">Website: {website}</div>
        </div>
    </div>
</body>
</html>"""
    return html_code

def generate_creative_thank_you_slide(
    main_title="Questions?",
    subtitle="THANKS FOR WATCHING",
    image_url="https://images.unsplash.com/photo-1516321497487-e288fb19713f?q=80&w=2940&auto=format&fit=crop",
    bg_gradient_start="#FFF1F2",
    bg_gradient_end="#FCE7F3",
    accent_color="#BE123C",
    font_family="'Montserrat', sans-serif"
):
    """
    Generates a creative Thank You slide with aurora background shapes and a featured image.
    Perfect for portfolios or creative pitches.
    """
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 1920px; height: 1080px; font-family: {font_family}; 
                      background: linear-gradient(135deg, {bg_gradient_start}, {bg_gradient_end}); overflow: hidden; }}
        
        .aurora-1 {{
            position: absolute; width: 800px; height: 800px; 
            background: #FBCFE8; filter: blur(120px); border-radius: 50%;
            top: -200px; right: -200px; opacity: 0.6;
        }}

        .image-container {{
            position: absolute; left: 150px; top: 180px;
            width: 700px; height: 720px;
            border-radius: 40px; overflow: hidden;
            box-shadow: 0 30px 60px rgba(0,0,0,0.1);
            z-index: 5;
        }}

        .text-container {{
            position: absolute; left: 950px; top: 400px;
            width: 800px;
            z-index: 10;
        }}

        .subtitle {{
            font-size: 32px;
            font-weight: 700;
            color: {accent_color};
            letter-spacing: 8px;
            margin-bottom: 20px;
        }}

        .title {{
            font-size: 120px;
            font-weight: 900;
            color: #1F2937;
            line-height: 1;
        }}
    </style>
</head>
<body>
    <div class="aurora-1"></div>
    <div class="image-container">
        <img src="{image_url}" style="width: 100%; height: 100%; object-fit: cover;">
    </div>
    <div class="text-container">
        <p class="subtitle">{subtitle}</p>
        <h1 class="title">{main_title}</h1>
    </div>
</body>
</html>"""
    return html_code

def generate_tech_thank_you_slide(
    main_title="STAY CONNECTED",
    social_handle="@tech_studio",
    primary_neon="#00FFFF",
    bg_dark="#1a1a2e",
    font_family="'Montserrat', sans-serif"
):
    """
    Generates a tech-themed Thank You slide with neon glow effects and geometric SVG elements.
    """
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 1920px; height: 1080px; font-family: {font_family}; background-color: {bg_dark}; overflow: hidden; }}
        
        .grid-bg {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background-image: radial-gradient({primary_neon} 1px, transparent 1px);
            background-size: 50px 50px;
            opacity: 0.1;
        }}

        .neon-title {{
            position: absolute; left: 0; right: 0; top: 350px;
            font-size: 160px; font-weight: 900; text-align: center;
            color: {primary_neon};
            text-shadow: 0 0 20px {primary_neon}, 0 0 40px {primary_neon};
            letter-spacing: 15px;
        }}

        .social-box {{
            position: absolute; left: 760px; top: 650px;
            width: 400px; padding: 20px;
            border: 2px solid {primary_neon};
            border-radius: 10px;
            color: white; font-size: 32px; text-align: center;
            box-shadow: inset 0 0 15px rgba(0,255,255,0.2);
        }}
    </style>
</head>
<body>
    <div class="grid-bg"></div>
    <div class="neon-title">THANK YOU</div>
    <div class="social-box">{social_handle}</div>
</body>
</html>"""
    return html_code

def generate_minimalist_thank_you_slide_2(
    main_title="END.",
    footer_note="Copyright 2026 Studio",
    text_color="#000000",
    bg_color="#FFFFFF",
    font_family="'Inter', sans-serif"
):
    """
    Generates a minimalist Thank You slide focusing on high-end typography and white space.
    """
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 1920px; height: 1080px; font-family: {font_family}; background-color: {bg_color}; overflow: hidden; }}
        
        .main-title {{
            position: absolute; left: 120px; top: 400px;
            font-size: 280px; font-weight: 800;
            color: {text_color};
            line-height: 0.8;
        }}

        .divider {{
            position: absolute; left: 120px; top: 750px;
            width: 100px; height: 12px;
            background-color: {text_color};
        }}

        .footer {{
            position: absolute; left: 120px; bottom: 80px;
            font-size: 24px; text-transform: uppercase;
            letter-spacing: 4px;
            color: {text_color}; opacity: 0.5;
        }}
    </style>
</head>
<body>
    <h1 class="main-title">{main_title}</h1>
    <div class="divider"></div>
    <p class="footer">{footer_note}</p>
</body>
</html>"""
    return html_code

def generate_elegant_thank_you_slide(
    main_title="Thank You",
    subtitle="FOR YOUR KIND ATTENTION",
    bg_image="https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=2069&auto=format&fit=crop",
    overlay_color="rgba(255, 255, 255, 0.85)",
    font_family="'Playfair Display', serif"
):
    """
    Generates an elegant Thank You slide with an image background and a glassmorphism card.
    """
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ width: 1920px; height: 1080px; font-family: {font_family}; overflow: hidden; }}
        
        .bg-img {{
            position: absolute; width: 100%; height: 100%;
            object-fit: cover; z-index: 1;
        }}

        .glass-card {{
            position: absolute; left: 560px; top: 290px;
            width: 800px; height: 500px;
            background-color: {overlay_color};
            backdrop-filter: blur(10px);
            border-radius: 20px;
            z-index: 5;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            box-shadow: 0 40px 100px rgba(0,0,0,0.1);
        }}

        .title {{
            font-size: 110px; font-style: italic; color: #4A403A; margin-bottom: 20px;
        }}

        .subtitle {{
            font-size: 24px; letter-spacing: 6px; color: #8B7E74;
        }}
    </style>
</head>
<body>
    <img src="{bg_image}" class="bg-img">
    <div class="glass-card">
        <h1 class="title">{main_title}</h1>
        <p class="subtitle">{subtitle}</p>
    </div>
</body>
</html>"""
    return html_code

