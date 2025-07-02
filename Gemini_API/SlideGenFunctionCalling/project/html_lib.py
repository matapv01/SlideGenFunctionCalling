def generate_intro_slide(
    main_title="Main Title",
    subtitle1="Subtitle1",
    subtitle2="Subtitle2",
    main_bg_color="#ffffff",
    accent_bg_color="#6ea88a",  # Teal/blue-green color
    text_box_bg_color="#c5e6b8",  # Light green color
    title_color="#333333",
    subtitle_color="#555555",
    line_color="#e6c35c",  # Gold/yellow line color
    font_family="'Segoe UI', Arial, sans-serif",
    main_title_font_size="36px",
    subtitle_font_size="16px",
    main_title_font_style="italic",
):
    """
    Generates an HTML slide with a marketing design featuring a title section on the left
    and an image on the right, exactly matching the provided design.
    
    Parameters:
    - main_title: The main title text
    - subtitle1: The first subtitle text
    - subtitle2: The second subtitle text
    - main_bg_color: Main background color
    - accent_bg_color: Background color for the right side
    - text_box_bg_color: Background color for the text box
    - title_color: Color for the main title
    - subtitle_color: Color for the subtitles
    - line_color: Color for the horizontal line
    - font_family: Font family for the text
    - main_title_font_size: Font size for the main title
    - subtitle_font_size: Font size for the subtitles
    - main_title_font_style: Font style for the main title (normal, italic, etc.)
    
    Returns:
    - HTML code for the marketing slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .left-section {{
            position: absolute;
            top: 0;
            left: 0;
            width: 60%;
            height: 100%;
            background-color: {main_bg_color};
        }}
        
        .right-section {{
            position: absolute;
            top: 0;
            right: 0;
            width: 40%;
            height: 100%;
            background-color: {accent_bg_color};
        }}
        
        .green-bar-top {{
            position: absolute;
            top: 0;
            left: 0;
            width: 40px;
            height: 20px;
            background-color: {text_box_bg_color};
            z-index: 1;
        }}
        
        .green-bar-middle {{
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 60px;
            background-color: {text_box_bg_color};
            transform: translateY(-50%);
            z-index: 1;
        }}
        
        .text-box {{
            position: absolute;
            top: 50%;
            left: 10%;
            transform: translateY(-50%);
            width: 40%;
            background-color: {text_box_bg_color};
            padding: 30px;
            z-index: 2;
        }}
        
        .main-title {{
            font-size: {main_title_font_size};
            color: {title_color};
            margin: 0 0 15px 0;
            font-weight: bold;
            font-style: {main_title_font_style};
            line-height: 1.2;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 5px 0;
        }}
        
        .divider {{
            width: 100%;
            height: 2px;
            background-color: {line_color};
            margin-top: 15px;
        }}
        
        .image-frame {{
            position: absolute;
            top: 50%;
            right: 10%;
            transform: translateY(-50%);
            width: 30%;
            height: 70%;
            border: 10px solid white;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            z-index: 2;
        }}
        
        .image-frame img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Left and right sections -->
        <div class="left-section"></div>
        <div class="right-section"></div>
        
        <!-- Small green bar at top left -->
        <div class="green-bar-top"></div>
        
        <!-- Green bar across the middle -->
        <div class="green-bar-middle"></div>
        
        <!-- Text box -->
        <div class="text-box">
            <h1 class="main-title">{main_title}</h1>
            <p class="subtitle">{subtitle1}</p>
            <p class="subtitle">{subtitle2}</p>
            <div class="divider"></div>
        </div>
        
        <!-- Image frame -->
        <div class="image-frame">
            <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture1.png" alt="slide visual">
        </div>
    </div>
</body>
</html>"""
    
    return html_code
    

def generate_body_slide1(
    # Main parameters
    vertical_title="CONTENTS",
    
    # Style parameters
    main_bg_color="#e6f2dd",  # Light green background
    left_bg_color="#ffffff",  # White background for left section
    title_color="#333333",
    item_number_color="#333333",
    item_title_color="#333333",
    item_text_color="#555555",
    vertical_title_font_size="48px",
    item_number_font_size="28px",
    item_title_font_size="18px",
    item_text_font_size="14px",
    font_family="'Segoe UI', Arial, sans-serif",
    left_width="15%",
    
    # Content parameter - direct HTML content
    items_content="""
        <ul>title1
            <li>content1</li>
        </ul>
        <ul>title2
            <li>content2</li>
        </ul>
        <ul>title3
            <li>content3</li>
        </ul>
        <ul>title4
            <li>content4</li>
        </ul>
        """,
):
    """
    Generates an HTML slide with a vertical title on the left, content in the middle,
    and an image on the right. Content is provided as a single HTML string.
    
    Parameters:
    - vertical_title: The vertical title text on the left
    - image_path: Path to the image file
    
    Style parameters:
    - main_bg_color: Background color for the main content area
    - left_bg_color: Background color for the left section with vertical title
    - title_color: Color for the vertical title
    - item_number_color: Color for the item numbers
    - item_title_color: Color for the item titles
    - item_text_color: Color for the item text
    - vertical_title_font_size: Font size for the vertical title
    - item_number_font_size: Font size for the item numbers
    - item_title_font_size: Font size for the item titles
    - item_text_font_size: Font size for the item text
    - font_family: Font family for the slide
    - left_width: Width of the left section with vertical title
    
    Content parameter:
    - items_content: HTML string containing all content to be displayed in the content area
    
    Returns:
    - HTML code for the contents slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contents Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
        }}
        
        .left-section {{
            width: {left_width};
            height: 100%;
            background-color: {left_bg_color};
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }}
        
        .vertical-title {{
            font-size: {vertical_title_font_size};
            color: {title_color};
            writing-mode: vertical-rl;
            transform: rotate(180deg);
            text-transform: uppercase;
            letter-spacing: 4px;
            font-weight: bold;
        }}
        
        .green-square {{
            position: absolute;
            top: 20px;
            left: 20px;
            width: 40px;
            height: 20px;
            background-color: {main_bg_color};
        }}
        
        .main-section {{
            flex: 1;
            display: flex;
            position: relative;
        }}
        
        .content-area {{
            width: 65%;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .image-area {{
            width: 35%;
            height: 100%;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .image-area img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        /* Styling for the content */
        .content-area ul {{
            margin-bottom: 30px;
            padding-left: 0;
            list-style-type: none;
        }}
        
        .content-area ul li {{
            font-size: {item_text_font_size};
            color: {item_text_color};
            margin-bottom: 5px;
            margin-left: 20px;
        }}
        
        /* First line of each ul is treated as a title */
        .content-area ul::before {{
            content: attr(data-title);
            display: block;
            font-size: {item_title_font_size};
            color: {item_title_color};
            margin-bottom: 10px;
            font-style: italic;
        }}
        
        /* Add numbers before each ul */
        .content-area ul {{
            position: relative;
            padding-left: 50px;
        }}
        
        .content-area ul::after {{
            content: counter(item, decimal-leading-zero);
            counter-increment: item;
            position: absolute;
            left: 0;
            top: 0;
            font-size: {item_number_font_size};
            color: {item_number_color};
            font-weight: 300;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Left section with vertical title -->
        <div class="left-section">
            <div class="green-square"></div>
            <div class="vertical-title">{vertical_title}</div>
        </div>
        
        <!-- Main section with content and image -->
        <div class="main-section">
            <div class="content-area">
                <style>
                    .content-area {{
                        counter-reset: item;
                    }}
                </style>
                {items_content}
            </div>
            
            <div class="image-area">
                <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture2.png" alt="Decorative image">
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
    title_font_size="32px",
    subtitle_font_size="20px",
    content_font_size="16px",
    font_family="'Segoe UI', Arial, sans-serif",
    
    # Icon parameters - SVG paths for each icon
    icon1="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M12 2v6M12 18v4M14.5 8a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0zM16.5 13a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0z"></path></svg>""",  # Lightbulb
    icon2="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>""",  # Target
    icon3="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>""",  # Bar chart
):
    """
    Generates an HTML slide with a main title, large image on the left,
    and three content sections with icons on the right.
    
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .title-section {{
            position: absolute;
            top: 40px;
            left: 40px;
            display: flex;
            align-items: center;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            position: absolute;
            top: 100px;
            left: 0;
            width: 100%;
            height: calc(100% - 100px);
        }}
        
        .image-section {{
            width: 45%;
            height: 100%;
            position: relative;
            padding: 20px;
            box-sizing: border-box;
        }}
        
        .image-frame {{
            width: 100%;
            height: 80%;
            position: relative;
            overflow: hidden;
        }}
        
        .image-accent {{
            position: absolute;
            top: 0;
            left: 0;
            width: 90%;
            height: 90%;
            border: 15px solid {accent_color};
            box-sizing: border-box;
            z-index: 1;
        }}
        
        .image-container {{
            position: absolute;
            top: 20px;
            left: 20px;
            width: 90%;
            height: 90%;
            background-color: #f0f0f0;
            overflow: hidden;
            z-index: 2;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .content-section {{
            width: 55%;
            height: 100%;
            padding: 20px 40px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .content-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 30px;
        }}
        
        .icon-container {{
            width: 50px;
            height: 50px;
            background-color: {accent_color};
            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: 20px;
            flex-shrink: 0;
        }}
        
        .icon-container svg {{
            width: 24px;
            height: 24px;
            stroke: #333333;
        }}
        
        .content-text {{
            flex: 1;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 5px 0;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
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
                        <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture3.png" alt="Slide image">
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

def generate_body_slide3(
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
    main_bg_color="#ffffff",  # White background
    box_bg_color="#e6f2dd",   # Light green background for boxes
    accent_color="#8cc63f",   # Green accent color
    title_color="#333333",
    subtitle_color="#333333",
    content_color="#555555",
    title_font_size="32px",
    subtitle_font_size="20px",
    content_font_size="16px",
    font_family="'Segoe UI', Arial, sans-serif",
    box_height="250px",       # Adjusted height for content boxes
    
    # Icon parameters - SVG paths for each icon
    icon1="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 9l-5 5-2-2-4 4"></path></svg>""",  # Line chart
    icon2="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>""",  # Bar chart
    icon3="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>""",  # Presentation chart
):
    """
    Generates an HTML slide with a main title and three content boxes with icons.
    
    Parameters:
    - main_title: The main title of the slide
    
    Content parameters:
    - subtitle1, subtitle2, subtitle3: Subtitles for each content box
    - content1, content2, content3: Content text for each box
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - box_bg_color: Background color for the content boxes
    - accent_color: Color for accents and icons
    - title_color: Color for the main title
    - subtitle_color: Color for subtitles
    - content_color: Color for content text
    - title_font_size: Font size for the main title
    - subtitle_font_size: Font size for subtitles
    - content_font_size: Font size for content text
    - font_family: Font family for the slide
    - box_height: Height of the content boxes
    
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
    <title>Three Column Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 60px; /* Increased margin to move content boxes down */
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {box_bg_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            justify-content: space-between;
            align-items: center; /* Center content boxes vertically */
            height: calc(100% - 120px); /* Adjusted to account for larger title margin */
        }}
        
        .content-box {{
            width: 31%;
            height: {box_height}; /* Fixed height for content boxes */
            background-color: {box_bg_color};
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 60px 20px 20px;
            box-sizing: border-box;
            text-align: center;
        }}
        
        .icon-circle {{
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background-color: #ffffff;
            position: absolute;
            top: -35px;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .icon-circle svg {{
            stroke: {accent_color};
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 15px 0;
            font-weight: bold;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
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
    title_font_size="32px",
    content_font_size="16px",
    subtitle_font_size="18px",
    font_family="'Segoe UI', Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title, horizontal content bar,
    and three images with subtitles and content.
    
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-bar {{
            width: 100%;
            background-color: {accent_color};
            padding: 10px 20px;
            margin-bottom: 30px;
            box-sizing: border-box;
            text-align: center;
            color: {content_color};
            font-size: {content_font_size};
            font-style: italic;
        }}
        
        .image-gallery {{
            display: flex;
            justify-content: space-between;
            width: 100%;
        }}
        
        .image-item {{
            width: 30%;
            text-align: center;
        }}
        
        .image-container {{
            position: relative;
            width: 100%;
            height: 200px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        
        .image-border {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-left: 8px solid {accent_color};
            box-sizing: border-box;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 5px 0;
            font-style: italic;
            text-align: center;
        }}
        
        .image-content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            text-align: center;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
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
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture4.1.png" alt="Image 1">
                </div>
                <h3 class="subtitle">{subtitle1}</h3>
                <p class="image-content">{content1}</p>
            </div>
            
            <!-- Image Item 2 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture4.2.png" alt="Image 2">
                </div>
                <h3 class="subtitle">{subtitle2}</h3>
                <p class="image-content">{content2}</p>
            </div>
            
            <!-- Image Item 3 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture4.3.png" alt="Image 3">
                </div>
                <h3 class="subtitle">{subtitle3}</h3>
                <p class="image-content">{content3}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_body_slide8(
    # Main parameters
    main_title="MainTitle",
    
    # Content parameters
    section1_title="SubTitle 1",
    section1_content="Content1",
    section2_title="SubTitle 2",
    section2_content="Content2",
    section3_title="SubTitle 3",
    section3_content="Content3",
    
    
    # Style parameters
    main_bg_color="#ffffff",  # White background
    left_bg_color="#d5e8b9",  # Light green background for left column
    accent_color="#d5e8b9",   # Light green accent color
    title_color="#333333",
    section_title_color="#ffffff",
    content_color="#333333",
    main_title_font_size="28px",
    section_title_font_size="16px",
    content_font_size="14px",
    font_family="'Segoe UI', Arial, sans-serif",
    
    # Icon parameters - SVG paths for each icon
    icon1="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>""",  # Magnifying glass
    icon2="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M12 2v6M12 18v4M14.5 8a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0zM16.5 13a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0z"></path></svg>""",  # Lightbulb
    icon3="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12c0 6-4.39 10-9.806 10C7.792 22 4.24 19.665 3 16"></path><path d="M2 12c0-6 4.39-10 9.806-10C16.209 2 19.76 4.335 21 8"></path><path d="M7 17l-4-1 1 4"></path><path d="M17 7l4 1-1-4"></path></svg>""",  # Circular arrows
):
    """
    Generates an HTML slide with a main title, two-column layout with icons and content on the left,
    and an image on the right.
    
    Parameters:
    - main_title: The main title of the slide
    
    Content parameters:
    - section1_title, section2_title, section3_title: Titles for each section
    - section1_content, section2_content, section3_content: Content text for each section
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - left_bg_color: Background color for the left column
    - accent_color: Color for accents and icons
    - title_color: Color for the main title
    - section_title_color: Color for section titles
    - content_color: Color for content text
    - main_title_font_size: Font size for the main title
    - section_title_font_size: Font size for section titles
    - content_font_size: Font size for content text
    - font_family: Font family for the slide
    
    Icon parameters:
    - icon1, icon2, icon3: SVG code for each section icon
    
    Returns:
    - HTML code for the slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Two Column Icon Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {main_title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            height: calc(100% - 80px);
        }}
        
        .left-column {{
            width: 60%;
            background-color: {left_bg_color};
            padding: 30px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        .right-column {{
            width: 40%;
            position: relative;
            overflow: hidden;
        }}
        
        .right-column img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .content-section {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 10px;
        }}
        
        .icon-circle {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        
        .icon-circle svg {{
            stroke: {accent_color};
        }}
        
        .section-content {{
            flex: 1;
        }}
        
        .section-title {{
            font-size: {section_title_font_size};
            color: {section_title_color};
            margin: 0 0 5px 0;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section-text {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.4;
        }}
        
        .divider {{
            width: 100%;
            border-top: 1px dashed rgba(0, 0, 0, 0.2);
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Left Column with Icons and Content -->
            <div class="left-column">
                <!-- Section 1 -->
                <div class="content-section">
                    <div class="icon-circle">
                        {icon1}
                    </div>
                    <div class="section-content">
                        <h3 class="section-title">{section1_title}</h3>
                        <p class="section-text">{section1_content}</p>
                    </div>
                </div>
                
                <div class="divider"></div>
                
                <!-- Section 2 -->
                <div class="content-section">
                    <div class="icon-circle">
                        {icon2}
                    </div>
                    <div class="section-content">
                        <h3 class="section-title">{section2_title}</h3>
                        <p class="section-text">{section2_content}</p>
                    </div>
                </div>
                
                <div class="divider"></div>
                
                <!-- Section 3 -->
                <div class="content-section">
                    <div class="icon-circle">
                        {icon3}
                    </div>
                    <div class="section-content">
                        <h3 class="section-title">{section3_title}</h3>
                        <p class="section-text">{section3_content}</p>
                    </div>
                </div>
            </div>
            
            <!-- Right Column with Image -->
            <div class="right-column">
                <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture2.png" alt="Decorative image">
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

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
    title_font_size="32px",
    subtitle_font_size="18px",
    content_font_size="14px",
    font_family="'Segoe UI', Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title, 2x2 image grid on the left,
    and four content sections on the right.
    
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .left-accent {{
            position: absolute;
            top: 0;
            left: 0;
            width: 10px;
            height: 100%;
            background-color: {accent_color};
        }}
        
        .right-accent {{
            position: absolute;
            top: 0;
            right: 0;
            width: 10px;
            height: 100%;
            background-color: {accent_color};
        }}
        
        .title-section {{
            position: absolute;
            top: 30px;
            left: 30px;
            display: flex;
            align-items: center;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            position: absolute;
            top: 100px;
            left: 30px;
            width: calc(100% - 60px);
            height: calc(100% - 130px);
        }}
        
        .image-grid {{
            width: 45%;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 10px;
        }}
        
        .grid-image {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: relative;
        }}
        
        .grid-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .image-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 10px;
            background-color: {accent_color};
        }}
        
        .content-sections {{
            width: 55%;
            padding-left: 40px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 20px;
        }}
        
        .content-section {{
            display: flex;
            flex-direction: column;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 10px 0;
            font-style: italic;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.4;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="left-accent"></div>
        <div class="right-accent"></div>
        
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Image Grid -->
            <div class="image-grid">
                <div class="grid-image">
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture5.1.png" alt="Image 1">
                    <div class="image-overlay"></div>
                </div>
                <div class="grid-image">
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture5.2.png" alt="Image 2">
                    <div class="image-overlay"></div>
                </div>
                <div class="grid-image">
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture5.3.png" alt="Image 3">
                    <div class="image-overlay"></div>
                </div>
                <div class="grid-image">
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture5.4.png" alt="Image 4">
                    <div class="image-overlay"></div>
                </div>
            </div>
            
            <!-- Content Sections -->
            <div class="content-sections">
                <div class="content-section">
                    <h3 class="subtitle">{subtitle1}</h3>
                    <p class="content">{content1}</p>
                </div>
                <div class="content-section">
                    <h3 class="subtitle">{subtitle2}</h3>
                    <p class="content">{content2}</p>
                </div>
                <div class="content-section">
                    <h3 class="subtitle">{subtitle3}</h3>
                    <p class="content">{content3}</p>
                </div>
                <div class="content-section">
                    <h3 class="subtitle">{subtitle4}</h3>
                    <p class="content">{content4}</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_body_slide6(
    # Main parameters
    main_title="MainTitle",
    
    # Content parameters
    subtitle1="SUBTITLE1",
    content1="Content1",
    subtitle2="SUBTITLE2",
    content2="Content2",
    
    # Style parameters
    main_bg_color="#ffffff",  # White background
    accent_color="#d5e8b9",   # Light green accent
    title_color="#333333",
    subtitle_color="#333333",
    content_color="#555555",
    title_font_size="32px",
    subtitle_font_size="18px",
    content_font_size="16px",
    font_family="'Segoe UI', Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title, image on the right,
    and two content sections on the left.
    
    Parameters:
    - main_title: The main title of the slide
    
    Content parameters:
    - subtitle1, subtitle2: Subtitles for each content section
    - content1, content2: Content text for each section
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - accent_color: Color for accents and subtitle backgrounds
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
    <title>Image Right Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 40px;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            height: calc(100% - 80px);
        }}
        
        .left-column {{
            width: 40%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 40px;
        }}
        
        .right-column {{
            width: 60%;
            padding-left: 40px;
            box-sizing: border-box;
        }}
        
        .image-container {{
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .content-section {{
            display: flex;
            flex-direction: column;
        }}
        
        .subtitle-container {{
            background-color: {accent_color};
            padding: 8px 15px;
            display: inline-block;
            margin-bottom: 10px;
            align-self: flex-start;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0;
            font-weight: bold;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.5;
            padding-left: 15px;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
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
                        <h3 class="subtitle">{subtitle1}</h3>
                    </div>
                    <p class="content">{content1}</p>
                </div>
                
                <!-- Content Section 2 -->
                <div class="content-section">
                    <div class="subtitle-container">
                        <h3 class="subtitle">{subtitle2}</h3>
                    </div>
                    <p class="content">{content2}</p>
                </div>
            </div>
            
            <!-- Right Column with Image -->
            <div class="right-column">
                <div class="image-container">
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture6.png" alt="Slide image">
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


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
    title_font_size="32px",
    subtitle_font_size="28px",
    content_font_size="16px",
    font_family="'Segoe UI', Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title, three vertical images on the left,
    and content with subtitle on the right.
    
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 40px;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            height: calc(100% - 80px);
        }}
        
        .left-column {{
            width: 40%;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .image-container {{
            width: 100%;
            height: calc(33.33% - 7px);
            overflow: hidden;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .right-column {{
            width: 60%;
            padding-left: 40px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 15px 0;
            font-weight: normal;
            font-style: italic;
        }}
        
        .divider {{
            width: 100%;
            height: 3px;
            background-color: {divider_color};
            margin-bottom: 30px;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0 0 20px 0;
            line-height: 1.6;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Left Column with Images -->
            <div class="left-column">
                <div class="image-container">
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture7.1.png" alt="Image 1">
                </div>
                <div class="image-container">
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture7.2.png" alt="Image 2">
                </div>
                <div class="image-container">
                    <img src="C:/Users/pvmkt/OneDrive/Documents/SlideGen/SlideGenSourceCode/SlideGenFunctionCalling/project/Image/Picture7.3.png" alt="Image 3">
                </div>
            </div>
            
            <!-- Right Column with Content -->
            <div class="right-column">
                <h2 class="subtitle">{subtitle}</h2>
                <div class="divider"></div>
                <p class="content">{content1}</p>
                <p class="content">{content2}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_academic_slide(
    title="YOUR TITLE HERE",
    description="Add a short description",
    name="Name: XXX",
    title_font_size="48px",
    description_font_size="32px",
    name_font_size="18px",
    title_color="#666666",
    description_color="#888888",
    name_bg_color="#777777",
    name_text_color="#ffffff",
    background_color="#ffffff",
    accent_color="#a2c4c9",
    divider_width="60%",
    divider_height="2px",
    divider_color="#666666",
    icon_color="#666666",
    box_shadow="0 10px 30px rgba(0, 0, 0, 0.15)",
    font_family="Arial, sans-serif",
):
    """
    Generates an HTML academic slide with a graduation cap icon.
    
    Parameters:
    - title: The main title of the slide
    - description: The description text
    - name: The name or attribution text
    - title_font_size: Font size for the title
    - description_font_size: Font size for the description
    - name_font_size: Font size for the name tag
    - title_color: Color for the title
    - description_color: Color for the description
    - name_bg_color: Background color for the name tag
    - name_text_color: Text color for the name tag
    - background_color: Background color of the slide
    - accent_color: Color for the slide container background
    - divider_width: Width of the divider line
    - divider_height: Height of the divider line
    - divider_color: Color of the divider line
    - icon_color: Color of the graduation cap icon
    - box_shadow: Shadow effect for the slide
    - font_family: Font family for the slide
    
    Returns:
    - HTML code for the academic slide
    """
    
    # Create the HTML content with CSS using f-strings
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Academic Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            position: relative;
            width: 1000px;
            height: 560px;
            background-color: {accent_color};
            overflow: hidden;
        }}
        
        .slide {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            height: 80%;
            background-color: {background_color};
            box-shadow: {box_shadow};
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
            box-sizing: border-box;
            z-index: 1;
        }}
        
        .icon {{
            margin-bottom: 20px;
        }}
        
        .icon svg {{
            width: 80px;
            height: 80px;
            fill: {icon_color};
        }}
        
        .title {{
            font-size: {title_font_size};
            font-weight: bold;
            color: {title_color};
            text-align: center;
            margin: 0;
            text-transform: uppercase;
        }}
        
        .divider {{
            width: {divider_width};
            height: {divider_height};
            background-color: {divider_color};
            margin: 30px 0;
            opacity: 0.5;
        }}
        
        .description {{
            font-size: {description_font_size};
            color: {description_color};
            text-align: center;
            margin: 0 0 40px 0;
            font-weight: 300;
        }}
        
        .name-tag {{
            background-color: {name_bg_color};
            color: {name_text_color};
            padding: 10px 25px;
            border-radius: 30px;
            font-size: {name_font_size};
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="slide">
            <div class="icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512">
                    <path d="M320 32c-8.1 0-16.1 1.4-23.7 4.1L15.8 137.4C6.3 140.9 0 149.9 0 160s6.3 19.1 15.8 22.6l57.9 20.9C57.3 229.3 48 259.8 48 291.9v28.1c0 28.4-10.8 57.7-22.3 80.8c-6.5 13-13.9 25.8-22.5 37.6C0 442.7-.9 448.3 .9 453.4s6 8.9 11.2 10.2l64 16c4.2 1.1 8.7 .3 12.4-2s6.3-6.1 7.1-10.4c8.6-42.8 4.3-81.2-2.1-108.7C90.3 344.3 86 329.8 80 316.5v-2.9c0-12.6 1.3-25 3.3-37.3l80 28.9C175.1 308.5 187.5 311 200 311c21.1 0 42-5.9 60.2-16.9L559.6 174.8c6.5-3.7 10.4-10.6 10.4-18.1c0-11.3-9.1-20.4-20.4-20.4c-3.3 0-6.6 .8-9.6 2.4L361.5 210.3C341.8 220 320 215.9 320 215.9s-21.8 4.1-41.5-5.6L54.6 118.5 320 36.6l265.4 81.9-50.5 28.8c-27.3 15.6-39.9 47.5-30.7 77.3c2.2 7.2 10 11.1 17.1 8.9c7.2-2.2 11.1-9.9 8.9-17.1c-5.4-17.4 2-37.1 17.7-46.9l59.1-33.8c9.5-5.4 15.4-15.6 15.4-26.6s-5.9-21.2-15.4-26.6L343.7 36.1C335.6 32.8 327.8 31 320 31zM128 408c0 35.3 86 72 192 72s192-36.7 192-72L496 262.6l-96.7 55.3c-25.3 14.4-53.7 22.1-83 22.1c-25.2 0-49.9-5.7-72.3-16.4L128 262.6V408z"/>
                </svg>
            </div>
            <h1 class="title">{title}</h1>
            <div class="divider"></div>
            <p class="description">{description}</p>
            <div class="name-tag">{name}</div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_content_slide(
    main_title="CONTENT",
    items=None,
    main_title_font_size="60px",
    number_font_size="70px",
    item_title_font_size="28px",
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
        <div class="grid-item">
            <div class="item-number" style="font-size: {number_font_size}; color: {number_color};">{item_number}</div>
            <div class="item-title" style="font-size: {item_title_font_size}; color: {item_title_color};">{item_title}</div>
        </div>
        """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            overflow: hidden;
        }}
        
        /* Background with accent color */
        .slide-background {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: {accent_color};
        }}
        
        /* Main content area with white background */
        .slide-content {{
            position: absolute;
            top: {border_width};
            left: {border_width};
            right: {border_width};
            bottom: {border_width};
            background-color: {background_color};
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            padding: 40px;
            box-sizing: border-box;
            overflow: hidden; /* Prevent scrolling */
        }}
        
        .main-title {{
            font-size: {main_title_font_size};
            color: {main_title_color};
            text-align: center;
            margin-top: 0;
            margin-bottom: 50px;
            font-weight: bold;
        }}
        
        .grid-container {{
            display: grid;
            grid-template-columns: repeat({num_columns}, 1fr);
            grid-template-rows: repeat({num_rows}, 1fr);
            gap: 30px;
            flex: 1;
        }}
        
        .grid-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }}
        
        .item-number {{
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .item-title {{
            font-weight: normal;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Background with accent color -->
        <div class="slide-background"></div>
        
        <!-- Main content area with white background -->
        <div class="slide-content">
            <h1 class="main-title">{main_title}</h1>
            
            <div class="grid-container">
                {grid_items_html}
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code



def generate_two_column_slide(
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
    main_title_font_size="36px",
    column_title_font_size="24px",
    column_text_font_size="16px",
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
    Generates an HTML slide with two columns matching the exact layout in the image.
    
    Parameters:
    - main_title: The main title of the slide
    - left_column_titles: List of titles for the left column sections
    - left_column_texts: List of texts for the left column sections
    - right_column_titles: List of titles for the right column sections
    - right_column_texts: List of texts for the right column sections
    - main_title_font_size: Font size for the main title
    - column_title_font_size: Font size for the column titles
    - column_text_font_size: Font size for the column texts
    - main_title_color: Color of the main title
    - left_bg_color: Background color of the left column
    - left_text_color: Text color for the left column
    - right_title_color: Title color for the right column
    - right_text_color: Text color for the right column
    - border_color: Color for the border around the slide
    - icon_color: Color for the icons in the right column
    - font_family: Font family for the slide
    
    Returns:
    - HTML code for the two-column slide
    """
    
    # Create left column sections HTML
    left_sections_html = ""
    for i, (title, text) in enumerate(zip(left_column_titles, left_column_texts)):
        left_sections_html += f"""
        <div class="left-section" style="margin-bottom: 30px;">
            <h2 style="font-size: {column_title_font_size}; color: {left_text_color}; margin-top: 0; margin-bottom: 10px;">{title}</h2>
            <p style="font-size: {column_text_font_size}; color: {left_text_color}; margin: 0;">{text}</p>
        </div>
        """
    
    # Create right column sections HTML
    right_sections_html = ""
    icons = [
        # Document with pencil icon
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="ICON_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <path d="M16 13l-4 4h-4v-4l8-8z"></path>
        </svg>""",
        # Magnifying glass icon
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="ICON_COLOR" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>"""
    ]
    
    for i, (title, text) in enumerate(zip(right_column_titles, right_column_texts)):
        icon = icons[i % len(icons)].replace("ICON_COLOR", icon_color)
        right_sections_html += f"""
        <div class="right-section" style="display: flex; align-items: flex-start; margin-bottom: 30px;">
            <div style="margin-right: 15px; flex-shrink: 0;">{icon}</div>
            <div>
                <h2 style="font-size: {column_title_font_size}; color: {right_title_color}; margin-top: 0; margin-bottom: 10px;">{title}</h2>
                <p style="font-size: {column_text_font_size}; color: {right_text_color}; margin: 0;">{text}</p>
            </div>
        </div>
        """
    
    # Create the HTML content with CSS
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Two Column Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-outer-container {{
            width: 1000px;
            height: 560px;
            background-color: {border_color};
            padding: 30px;
            box-sizing: border-box;
        }}
        
        .slide-inner-container {{
            width: 100%;
            height: 100%;
            background-color: #ffffff;
            display: flex;
            flex-direction: column;
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .main-title {{
            font-size: {main_title_font_size};
            color: {main_title_color};
            text-align: center;
            margin-top: 0;
            margin-bottom: 40px;
        }}
        
        .columns-container {{
            display: flex;
            flex: 1;
            gap: 30px;
        }}
        
        .left-column {{
            flex: 1;
            background-color: {left_bg_color};
            padding: 30px;
        }}
        
        .right-column {{
            flex: 1;
            background-color: #ffffff;
            border: 1px solid {border_color};
            padding: 30px;
        }}
    </style>
</head>
<body>
    <div class="slide-outer-container">
        <div class="slide-inner-container">
            <h1 class="main-title">{main_title}</h1>
            
            <div class="columns-container">
                <div class="left-column">
                    {left_sections_html}
                </div>
                
                <div class="right-column">
                    {right_sections_html}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_project_circles_slide(
    main_title="Your Title Here",
    left_title="Your Title Here",
    right_title="Your Title Here",
    left_text="Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. Most of the time, they're presented before an audience.",
    right_text="Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. Most of the time, they're presented before an audience.",
    footer_text="Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience. Presentation are communication tools that can be used as demontrations, lectures, reports, and more.",
    project_names=["Project 1", "Project 2", "Project 3"],
    circle_colors=["#e1eff2", "#8cbeca", "#e1eff2"],
    main_title_font_size="36px",
    section_title_font_size="24px",
    text_font_size="16px",
    footer_font_size="14px",
    title_color="#555555",
    text_color="#555555",
    circle_text_color="#ffffff",
    background_color="#ffffff",
    accent_color="#a2c4c9",
    font_family="Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title, two text columns, and three project circles in the middle.
    The slide has an alternating blue and white border as shown in the image.
    
    Parameters:
    - main_title: The main title of the slide
    - left_title: Title for the left column
    - right_title: Title for the right column
    - left_text: Text content for the left column
    - right_text: Text content for the right column
    - footer_text: Text content for the footer
    - project_names: List of three project names for the circles
    - circle_colors: List of three colors for the circles
    - main_title_font_size: Font size for the main title
    - section_title_font_size: Font size for the section titles
    - text_font_size: Font size for the main text
    - footer_font_size: Font size for the footer text
    - title_color: Color for all titles
    - text_color: Color for all text content
    - circle_text_color: Color for the text in the circles
    - background_color: Background color of the slide
    - accent_color: Color for the corner accents
    - font_family: Font family for the slide
    
    Returns:
    - HTML code for the project circles slide with alternating border
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Circles Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {background_color};
        }}
        
        /* Top-left corner */
        .corner-tl {{
            position: absolute;
            top: 0;
            left: 0;
            width: 300px;
            height: 300px;
            background-color: {accent_color};
            clip-path: polygon(0 0, 100% 0, 0 100%);
            z-index: 0;
        }}
        
        /* Top-right corner */
        .corner-tr {{
            position: absolute;
            top: 0;
            right: 0;
            width: 300px;
            height: 300px;
            background-color: {accent_color};
            clip-path: polygon(100% 0, 0 0, 100% 100%);
            z-index: 0;
        }}
        
        /* Bottom-left corner */
        .corner-bl {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 300px;
            height: 300px;
            background-color: {accent_color};
            clip-path: polygon(0 100%, 100% 100%, 0 0);
            z-index: 0;
        }}
        
        /* Bottom-right corner */
        .corner-br {{
            position: absolute;
            bottom: 0;
            right: 0;
            width: 300px;
            height: 300px;
            background-color: {accent_color};
            clip-path: polygon(100% 100%, 0 100%, 100% 0);
            z-index: 0;
        }}
        
        .content {{
            position: absolute;
            top: 30px;
            left: 30px;
            right: 30px;
            bottom: 30px;
            background-color: {background_color};
            z-index: 1;
            display: flex;
            flex-direction: column;
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .main-title {{
            font-size: {main_title_font_size};
            color: {title_color};
            text-align: center;
            margin-top: 0;
            margin-bottom: 40px;
        }}
        
        .content-container {{
            display: flex;
            flex: 1;
            margin-bottom: 30px;
        }}
        
        .text-column {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            padding: 0 20px;
        }}
        
        .left-column {{
            text-align: right;
        }}
        
        .right-column {{
            text-align: left;
        }}
        
        .circles-column {{
            flex: 1;
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .circle {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            position: absolute;
            color: {circle_text_color};
            font-weight: bold;
            font-size: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .circle-1 {{
            background-color: {circle_colors[0]};
            left: 50%;
            top: 0;
            transform: translateX(-100%);
            z-index: 1;
        }}
        
        .circle-2 {{
            background-color: {circle_colors[1]};
            left: 50%;
            top: 50%;
            transform: translate(-50%, -30%);
            width: 180px;
            height: 180px;
            z-index: 3;
            font-size: 24px;
        }}
        
        .circle-3 {{
            background-color: {circle_colors[2]};
            left: 50%;
            top: 0;
            transform: translateX(0%);
            z-index: 2;
        }}
        
        .section-title {{
            font-size: {section_title_font_size};
            color: {title_color};
            margin-top: 0;
            margin-bottom: 15px;
        }}
        
        .section-text {{
            font-size: {text_font_size};
            color: {text_color};
            line-height: 1.5;
            margin: 0;
        }}
        
        .footer {{
            font-size: {footer_font_size};
            color: {text_color};
            text-align: center;
            line-height: 1.5;
            margin: 0;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Corner decorations for alternating border -->
        <div class="corner-tl"></div>
        <div class="corner-tr"></div>
        <div class="corner-bl"></div>
        <div class="corner-br"></div>
        
        <div class="content">
            <h1 class="main-title">{main_title}</h1>
            
            <div class="content-container">
                <div class="text-column left-column">
                    <h2 class="section-title">{left_title}</h2>
                    <p class="section-text">{left_text}</p>
                </div>
                
                <div class="circles-column">
                    <div class="circle circle-1">{project_names[0]}</div>
                    <div class="circle circle-2">{project_names[1]}</div>
                    <div class="circle circle-3">{project_names[2]}</div>
                </div>
                
                <div class="text-column right-column">
                    <h2 class="section-title">{right_title}</h2>
                    <p class="section-text">{right_text}</p>
                </div>
            </div>
            
            <p class="footer">{footer_text}</p>
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
    main_title_font_size="36px",
    column_title_font_size="28px",
    text_font_size="16px",
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            overflow: hidden;
        }}
        
        /* Background with accent color */
        .slide-background {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: {accent_color};
        }}
        
        /* Main content area with white background */
        .slide-content {{
            position: absolute;
            top: 30px;
            left: 30px;
            right: 30px;
            bottom: 30px;
            background-color: {background_color};
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .main-title {{
            font-size: {main_title_font_size};
            color: {title_color};
            text-align: center;
            margin-top: 0;
            margin-bottom: 40px;
        }}
        
        .columns-container {{
            display: flex;
            flex: 1;
            position: relative;
        }}
        
        .column {{
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 0 30px;
        }}
        
        .icon-container {{
            margin-bottom: 30px;
        }}
        
        .column-title {{
            font-size: {column_title_font_size};
            color: {title_color};
            text-align: center;
            margin-top: 0;
            margin-bottom: 20px;
        }}
        
        .column-text {{
            font-size: {text_font_size};
            color: {text_color};
            text-align: center;
            line-height: 1.5;
        }}
        
        .divider {{
            position: absolute;
            top: 0;
            bottom: 0;
            left: 50%;
            width: 2px;
            border-left: 2px dashed {divider_color};
            transform: translateX(-50%);
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Background with accent color -->
        <div class="slide-background"></div>
        
        <!-- Main content area with white background -->
        <div class="slide-content">
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






def generate_process_slide(
    main_title="Your Title Here",
    left_title="Your Title Here",
    right_title="Your Title Here",
    left_content="Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience. Presentation are communication tools that can be used as demontrations, lectures, reports, and more.",
    right_content="Presentation are communication tools that can be used as demontrations, lectures, reports, and more. it is mostly presented before an audience. Presentation are communication tools that can be used as demontrations, lectures, reports, and more.",
    main_title_font_size="36px",
    box_title_font_size="28px",
    content_font_size="16px",
    title_color="#555555",
    left_box_color="#8cbeca",
    right_box_color="#c5e1e8",
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            overflow: hidden;
        }}
        
        /* Background with accent color */
        .slide-background {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: {accent_color};
        }}
        
        /* Main content area with white background */
        .slide-content {{
            position: absolute;
            top: {border_width};
            left: {border_width};
            right: {border_width};
            bottom: {border_width};
            background-color: {background_color};
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            padding: 40px;
            box-sizing: border-box;
            overflow: hidden; /* Prevent scrolling */
        }}
        
        .main-title {{
            font-size: {main_title_font_size};
            color: {title_color};
            text-align: center;
            margin-top: 0;
            margin-bottom: 50px;
        }}
        
        .boxes-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            flex: 1;
        }}
        
        /* Arrow connecting the boxes */
        .arrow {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 200px;
            height: 100px;
            background-color: {arrow_color};
            clip-path: polygon(0 40%, 75% 40%, 75% 0, 100% 50%, 75% 100%, 75% 60%, 0 60%);
            z-index: 1;
        }}
        
        .box {{
            width: {box_width};
            height: {box_height};
            border-radius: {box_border_radius};
            padding: 25px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            color: {text_color};
            z-index: 2;
        }}
        
        .left-box {{
            background-color: {left_box_color};
        }}
        
        .right-box {{
            background-color: {right_box_color};
        }}
        
        .box-title {{
            font-size: {box_title_font_size};
            margin-top: 0;
            margin-bottom: 20px;
        }}
        
        .box-content {{
            font-size: {content_font_size};
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Background with accent color -->
        <div class="slide-background"></div>
        
        <!-- Main content area with white background -->
        <div class="slide-content">
            <h1 class="main-title">{main_title}</h1>
            
            <div class="boxes-container">
                <!-- Arrow connecting the boxes -->
                <div class="arrow"></div>
                
                <!-- Left box -->
                <div class="box left-box">
                    <h2 class="box-title">{left_title}</h2>
                    <p class="box-content">{left_content}</p>
                </div>
                
                <!-- Right box -->
                <div class="box right-box">
                    <h2 class="box-title">{right_title}</h2>
                    <p class="box-content">{right_content}</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_marketing_slide(
    main_title="COMMERCIAL PRODUCT MARKETING",
    subtitle1="Advertising Film And Television Media",
    subtitle2="Corporate Publicity",
    main_bg_color="#ffffff",
    accent_bg_color="#6ea88a",  # Teal/blue-green color
    text_box_bg_color="#c5e6b8",  # Light green color
    title_color="#333333",
    subtitle_color="#555555",
    line_color="#e6c35c",  # Gold/yellow line color
    font_family="'Segoe UI', Arial, sans-serif",
    main_title_font_size="36px",
    subtitle_font_size="16px",
    main_title_font_style="italic",
):
    """
    Generates an HTML slide with a marketing design featuring a title section on the left
    and an image on the right, exactly matching the provided design.
    
    Parameters:
    - main_title: The main title text
    - subtitle1: The first subtitle text
    - subtitle2: The second subtitle text
    - image_path: Path to the image file
    - main_bg_color: Main background color
    - accent_bg_color: Background color for the right side
    - text_box_bg_color: Background color for the text box
    - title_color: Color for the main title
    - subtitle_color: Color for the subtitles
    - line_color: Color for the horizontal line
    - font_family: Font family for the text
    - main_title_font_size: Font size for the main title
    - subtitle_font_size: Font size for the subtitles
    - main_title_font_style: Font style for the main title (normal, italic, etc.)
    
    Returns:
    - HTML code for the marketing slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marketing Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .left-section {{
            position: absolute;
            top: 0;
            left: 0;
            width: 60%;
            height: 100%;
            background-color: {main_bg_color};
        }}
        
        .right-section {{
            position: absolute;
            top: 0;
            right: 0;
            width: 40%;
            height: 100%;
            background-color: {accent_bg_color};
        }}
        
        .green-bar-top {{
            position: absolute;
            top: 0;
            left: 0;
            width: 40px;
            height: 20px;
            background-color: {text_box_bg_color};
            z-index: 1;
        }}
        
        .green-bar-middle {{
            position: absolute;
            top: 50%;
            left: 0;
            width: 100%;
            height: 60px;
            background-color: {text_box_bg_color};
            transform: translateY(-50%);
            z-index: 1;
        }}
        
        .text-box {{
            position: absolute;
            top: 50%;
            left: 10%;
            transform: translateY(-50%);
            width: 40%;
            background-color: {text_box_bg_color};
            padding: 30px;
            z-index: 2;
        }}
        
        .main-title {{
            font-size: {main_title_font_size};
            color: {title_color};
            margin: 0 0 15px 0;
            font-weight: bold;
            font-style: {main_title_font_style};
            line-height: 1.2;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 5px 0;
        }}
        
        .divider {{
            width: 100%;
            height: 2px;
            background-color: {line_color};
            margin-top: 15px;
        }}
        
        .image-frame {{
            position: absolute;
            top: 50%;
            right: 10%;
            transform: translateY(-50%);
            width: 30%;
            height: 70%;
            border: 10px solid white;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            z-index: 2;
        }}
        
        .image-frame img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Left and right sections -->
        <div class="left-section"></div>
        <div class="right-section"></div>
        
        <!-- Small green bar at top left -->
        <div class="green-bar-top"></div>
        
        <!-- Green bar across the middle -->
        <div class="green-bar-middle"></div>
        
        <!-- Text box -->
        <div class="text-box">
            <h1 class="main-title">{main_title}</h1>
            <p class="subtitle">{subtitle1}</p>
            <p class="subtitle">{subtitle2}</p>
            <div class="divider"></div>
        </div>
        
        <!-- Image frame -->
        <div class="image-frame">
            <img src="{image_path}" alt="Marketing visual">
        </div>
    </div>
</body>
</html>"""
    
    return html_code
    

def generate_contents_slide(
    # Main parameters
    vertical_title="CONTENTS",
    
    # Style parameters
    main_bg_color="#e6f2dd",  # Light green background
    left_bg_color="#ffffff",  # White background for left section
    title_color="#333333",
    item_number_color="#333333",
    item_title_color="#333333",
    item_text_color="#555555",
    vertical_title_font_size="48px",
    item_number_font_size="28px",
    item_title_font_size="18px",
    item_text_font_size="14px",
    font_family="'Segoe UI', Arial, sans-serif",
    left_width="15%",
    
    # Content parameter - direct HTML content
    items_content="""
        <ul>title1
            <li>content1</li>
        </ul>
        <ul>title2
            <li>content2</li>
        </ul>
        <ul>title3
            <li>content3</li>
        </ul>
        <ul>title4
            <li>content4</li>
        </ul>
        """,
):
    """
    Generates an HTML slide with a vertical title on the left, content in the middle,
    and an image on the right. Content is provided as a single HTML string.
    
    Parameters:
    - vertical_title: The vertical title text on the left
    - image_path: Path to the image file
    
    Style parameters:
    - main_bg_color: Background color for the main content area
    - left_bg_color: Background color for the left section with vertical title
    - title_color: Color for the vertical title
    - item_number_color: Color for the item numbers
    - item_title_color: Color for the item titles
    - item_text_color: Color for the item text
    - vertical_title_font_size: Font size for the vertical title
    - item_number_font_size: Font size for the item numbers
    - item_title_font_size: Font size for the item titles
    - item_text_font_size: Font size for the item text
    - font_family: Font family for the slide
    - left_width: Width of the left section with vertical title
    
    Content parameter:
    - items_content: HTML string containing all content to be displayed in the content area
    
    Returns:
    - HTML code for the contents slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contents Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
        }}
        
        .left-section {{
            width: {left_width};
            height: 100%;
            background-color: {left_bg_color};
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }}
        
        .vertical-title {{
            font-size: {vertical_title_font_size};
            color: {title_color};
            writing-mode: vertical-rl;
            transform: rotate(180deg);
            text-transform: uppercase;
            letter-spacing: 4px;
            font-weight: bold;
        }}
        
        .green-square {{
            position: absolute;
            top: 20px;
            left: 20px;
            width: 40px;
            height: 20px;
            background-color: {main_bg_color};
        }}
        
        .main-section {{
            flex: 1;
            display: flex;
            position: relative;
        }}
        
        .content-area {{
            width: 65%;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .image-area {{
            width: 35%;
            height: 100%;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .image-area img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        /* Styling for the content */
        .content-area ul {{
            margin-bottom: 30px;
            padding-left: 0;
            list-style-type: none;
        }}
        
        .content-area ul li {{
            font-size: {item_text_font_size};
            color: {item_text_color};
            margin-bottom: 5px;
            margin-left: 20px;
        }}
        
        /* First line of each ul is treated as a title */
        .content-area ul::before {{
            content: attr(data-title);
            display: block;
            font-size: {item_title_font_size};
            color: {item_title_color};
            margin-bottom: 10px;
            font-style: italic;
        }}
        
        /* Add numbers before each ul */
        .content-area ul {{
            position: relative;
            padding-left: 50px;
        }}
        
        .content-area ul::after {{
            content: counter(item, decimal-leading-zero);
            counter-increment: item;
            position: absolute;
            left: 0;
            top: 0;
            font-size: {item_number_font_size};
            color: {item_number_color};
            font-weight: 300;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Left section with vertical title -->
        <div class="left-section">
            <div class="green-square"></div>
            <div class="vertical-title">{vertical_title}</div>
        </div>
        
        <!-- Main section with content and image -->
        <div class="main-section">
            <div class="content-area">
                <style>
                    .content-area {{
                        counter-reset: item;
                    }}
                </style>
                {items_content}
            </div>
            
            <div class="image-area">
                <img src="{image_path}" alt="Decorative image">
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_image_with_icons_slide(
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
    title_font_size="32px",
    subtitle_font_size="20px",
    content_font_size="16px",
    font_family="'Segoe UI', Arial, sans-serif",
    
    # Icon parameters - SVG paths for each icon
    icon1="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M12 2v6M12 18v4M14.5 8a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0zM16.5 13a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0z"></path></svg>""",  # Lightbulb
    icon2="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>""",  # Target
    icon3="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>""",  # Bar chart
):
    """
    Generates an HTML slide with a main title, large image on the left,
    and three content sections with icons on the right.
    
    Parameters:
    - main_title: The main title of the slide
    - image_path: Path to the image file
    
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .title-section {{
            position: absolute;
            top: 40px;
            left: 40px;
            display: flex;
            align-items: center;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            position: absolute;
            top: 100px;
            left: 0;
            width: 100%;
            height: calc(100% - 100px);
        }}
        
        .image-section {{
            width: 45%;
            height: 100%;
            position: relative;
            padding: 20px;
            box-sizing: border-box;
        }}
        
        .image-frame {{
            width: 100%;
            height: 80%;
            position: relative;
            overflow: hidden;
        }}
        
        .image-accent {{
            position: absolute;
            top: 0;
            left: 0;
            width: 90%;
            height: 90%;
            border: 15px solid {accent_color};
            box-sizing: border-box;
            z-index: 1;
        }}
        
        .image-container {{
            position: absolute;
            top: 20px;
            left: 20px;
            width: 90%;
            height: 90%;
            background-color: #f0f0f0;
            overflow: hidden;
            z-index: 2;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .content-section {{
            width: 55%;
            height: 100%;
            padding: 20px 40px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .content-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 30px;
        }}
        
        .icon-container {{
            width: 50px;
            height: 50px;
            background-color: {accent_color};
            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: 20px;
            flex-shrink: 0;
        }}
        
        .icon-container svg {{
            width: 24px;
            height: 24px;
            stroke: #333333;
        }}
        
        .content-text {{
            flex: 1;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 5px 0;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
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
                        <img src="{image_path}" alt="Slide image">
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

def generate_three_column_slide(
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
    main_bg_color="#ffffff",  # White background
    box_bg_color="#e6f2dd",   # Light green background for boxes
    accent_color="#8cc63f",   # Green accent color
    title_color="#333333",
    subtitle_color="#333333",
    content_color="#555555",
    title_font_size="32px",
    subtitle_font_size="20px",
    content_font_size="16px",
    font_family="'Segoe UI', Arial, sans-serif",
    box_height="250px",       # Adjusted height for content boxes
    
    # Icon parameters - SVG paths for each icon
    icon1="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"></path><path d="M18 9l-5 5-2-2-4 4"></path></svg>""",  # Line chart
    icon2="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 20V10M12 20V4M6 20v-6"></path></svg>""",  # Bar chart
    icon3="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>""",  # Presentation chart
):
    """
    Generates an HTML slide with a main title and three content boxes with icons.
    
    Parameters:
    - main_title: The main title of the slide
    
    Content parameters:
    - subtitle1, subtitle2, subtitle3: Subtitles for each content box
    - content1, content2, content3: Content text for each box
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - box_bg_color: Background color for the content boxes
    - accent_color: Color for accents and icons
    - title_color: Color for the main title
    - subtitle_color: Color for subtitles
    - content_color: Color for content text
    - title_font_size: Font size for the main title
    - subtitle_font_size: Font size for subtitles
    - content_font_size: Font size for content text
    - font_family: Font family for the slide
    - box_height: Height of the content boxes
    
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
    <title>Three Column Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 60px; /* Increased margin to move content boxes down */
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {box_bg_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            justify-content: space-between;
            align-items: center; /* Center content boxes vertically */
            height: calc(100% - 120px); /* Adjusted to account for larger title margin */
        }}
        
        .content-box {{
            width: 31%;
            height: {box_height}; /* Fixed height for content boxes */
            background-color: {box_bg_color};
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 60px 20px 20px;
            box-sizing: border-box;
            text-align: center;
        }}
        
        .icon-circle {{
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background-color: #ffffff;
            position: absolute;
            top: -35px;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .icon-circle svg {{
            stroke: {accent_color};
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 15px 0;
            font-weight: bold;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
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

def generate_image_gallery_slide(
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
    title_font_size="32px",
    content_font_size="16px",
    subtitle_font_size="18px",
    font_family="'Segoe UI', Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title, horizontal content bar,
    and three images with subtitles and content.
    
    Parameters:
    - main_title: The main title of the slide
    - main_content: Content for the horizontal bar
    
    Image parameters:
    - image1_path, image2_path, image3_path: Paths to the three images
    
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-bar {{
            width: 100%;
            background-color: {accent_color};
            padding: 10px 20px;
            margin-bottom: 30px;
            box-sizing: border-box;
            text-align: center;
            color: {content_color};
            font-size: {content_font_size};
            font-style: italic;
        }}
        
        .image-gallery {{
            display: flex;
            justify-content: space-between;
            width: 100%;
        }}
        
        .image-item {{
            width: 30%;
            text-align: center;
        }}
        
        .image-container {{
            position: relative;
            width: 100%;
            height: 200px;
            margin-bottom: 15px;
            overflow: hidden;
        }}
        
        .image-border {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border-left: 8px solid {accent_color};
            box-sizing: border-box;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 5px 0;
            font-style: italic;
            text-align: center;
        }}
        
        .image-content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            text-align: center;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
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
                    <img src="{image1_path}" alt="Image 1">
                </div>
                <h3 class="subtitle">{subtitle1}</h3>
                <p class="image-content">{content1}</p>
            </div>
            
            <!-- Image Item 2 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="{image2_path}" alt="Image 2">
                </div>
                <h3 class="subtitle">{subtitle2}</h3>
                <p class="image-content">{content2}</p>
            </div>
            
            <!-- Image Item 3 -->
            <div class="image-item">
                <div class="image-container">
                    <div class="image-border"></div>
                    <img src="{image3_path}" alt="Image 3">
                </div>
                <h3 class="subtitle">{subtitle3}</h3>
                <p class="image-content">{content3}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_two_column_icon_slide(
    # Main parameters
    main_title="MainTitle",
    
    # Content parameters
    section1_title="SubTitle 1",
    section1_content="Content1",
    section2_title="SubTitle 2",
    section2_content="Content2",
    section3_title="SubTitle 3",
    section3_content="Content3",
    
    
    # Style parameters
    main_bg_color="#ffffff",  # White background
    left_bg_color="#d5e8b9",  # Light green background for left column
    accent_color="#d5e8b9",   # Light green accent color
    title_color="#333333",
    section_title_color="#ffffff",
    content_color="#333333",
    main_title_font_size="28px",
    section_title_font_size="16px",
    content_font_size="14px",
    font_family="'Segoe UI', Arial, sans-serif",
    
    # Icon parameters - SVG paths for each icon
    icon1="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>""",  # Magnifying glass
    icon2="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M12 2v6M12 18v4M14.5 8a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0zM16.5 13a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0z"></path></svg>""",  # Lightbulb
    icon3="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12c0 6-4.39 10-9.806 10C7.792 22 4.24 19.665 3 16"></path><path d="M2 12c0-6 4.39-10 9.806-10C16.209 2 19.76 4.335 21 8"></path><path d="M7 17l-4-1 1 4"></path><path d="M17 7l4 1-1-4"></path></svg>""",  # Circular arrows
):
    """
    Generates an HTML slide with a main title, two-column layout with icons and content on the left,
    and an image on the right.
    
    Parameters:
    - main_title: The main title of the slide
    
    Content parameters:
    - section1_title, section2_title, section3_title: Titles for each section
    - section1_content, section2_content, section3_content: Content text for each section
    
    Image parameters:
    - right_image_path: Path to the image on the right side
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - left_bg_color: Background color for the left column
    - accent_color: Color for accents and icons
    - title_color: Color for the main title
    - section_title_color: Color for section titles
    - content_color: Color for content text
    - main_title_font_size: Font size for the main title
    - section_title_font_size: Font size for section titles
    - content_font_size: Font size for content text
    - font_family: Font family for the slide
    
    Icon parameters:
    - icon1, icon2, icon3: SVG code for each section icon
    
    Returns:
    - HTML code for the slide
    """
    
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Two Column Icon Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {main_title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            height: calc(100% - 80px);
        }}
        
        .left-column {{
            width: 60%;
            background-color: {left_bg_color};
            padding: 30px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        .right-column {{
            width: 40%;
            position: relative;
            overflow: hidden;
        }}
        
        .right-column img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .content-section {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 10px;
        }}
        
        .icon-circle {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        
        .icon-circle svg {{
            stroke: {accent_color};
        }}
        
        .section-content {{
            flex: 1;
        }}
        
        .section-title {{
            font-size: {section_title_font_size};
            color: {section_title_color};
            margin: 0 0 5px 0;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .section-text {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.4;
        }}
        
        .divider {{
            width: 100%;
            border-top: 1px dashed rgba(0, 0, 0, 0.2);
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Left Column with Icons and Content -->
            <div class="left-column">
                <!-- Section 1 -->
                <div class="content-section">
                    <div class="icon-circle">
                        {icon1}
                    </div>
                    <div class="section-content">
                        <h3 class="section-title">{section1_title}</h3>
                        <p class="section-text">{section1_content}</p>
                    </div>
                </div>
                
                <div class="divider"></div>
                
                <!-- Section 2 -->
                <div class="content-section">
                    <div class="icon-circle">
                        {icon2}
                    </div>
                    <div class="section-content">
                        <h3 class="section-title">{section2_title}</h3>
                        <p class="section-text">{section2_content}</p>
                    </div>
                </div>
                
                <div class="divider"></div>
                
                <!-- Section 3 -->
                <div class="content-section">
                    <div class="icon-circle">
                        {icon3}
                    </div>
                    <div class="section-content">
                        <h3 class="section-title">{section3_title}</h3>
                        <p class="section-text">{section3_content}</p>
                    </div>
                </div>
            </div>
            
            <!-- Right Column with Image -->
            <div class="right-column">
                <img src="{right_image_path}" alt="Decorative image">
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code

def generate_image_grid_slide(
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
    title_font_size="32px",
    subtitle_font_size="18px",
    content_font_size="14px",
    font_family="'Segoe UI', Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title, 2x2 image grid on the left,
    and four content sections on the right.
    
    Parameters:
    - main_title: The main title of the slide
    
    Image parameters:
    - image1_path, image2_path, image3_path, image4_path: Paths to the four images
    
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .left-accent {{
            position: absolute;
            top: 0;
            left: 0;
            width: 10px;
            height: 100%;
            background-color: {accent_color};
        }}
        
        .right-accent {{
            position: absolute;
            top: 0;
            right: 0;
            width: 10px;
            height: 100%;
            background-color: {accent_color};
        }}
        
        .title-section {{
            position: absolute;
            top: 30px;
            left: 30px;
            display: flex;
            align-items: center;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            position: absolute;
            top: 100px;
            left: 30px;
            width: calc(100% - 60px);
            height: calc(100% - 130px);
        }}
        
        .image-grid {{
            width: 45%;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 10px;
        }}
        
        .grid-image {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            position: relative;
        }}
        
        .grid-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .image-overlay {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 10px;
            background-color: {accent_color};
        }}
        
        .content-sections {{
            width: 55%;
            padding-left: 40px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 20px;
        }}
        
        .content-section {{
            display: flex;
            flex-direction: column;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 10px 0;
            font-style: italic;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.4;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="left-accent"></div>
        <div class="right-accent"></div>
        
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Image Grid -->
            <div class="image-grid">
                <div class="grid-image">
                    <img src="{image1_path}" alt="Image 1">
                    <div class="image-overlay"></div>
                </div>
                <div class="grid-image">
                    <img src="{image2_path}" alt="Image 2">
                    <div class="image-overlay"></div>
                </div>
                <div class="grid-image">
                    <img src="{image3_path}" alt="Image 3">
                    <div class="image-overlay"></div>
                </div>
                <div class="grid-image">
                    <img src="{image4_path}" alt="Image 4">
                    <div class="image-overlay"></div>
                </div>
            </div>
            
            <!-- Content Sections -->
            <div class="content-sections">
                <div class="content-section">
                    <h3 class="subtitle">{subtitle1}</h3>
                    <p class="content">{content1}</p>
                </div>
                <div class="content-section">
                    <h3 class="subtitle">{subtitle2}</h3>
                    <p class="content">{content2}</p>
                </div>
                <div class="content-section">
                    <h3 class="subtitle">{subtitle3}</h3>
                    <p class="content">{content3}</p>
                </div>
                <div class="content-section">
                    <h3 class="subtitle">{subtitle4}</h3>
                    <p class="content">{content4}</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_image_right_slide(
    # Main parameters
    main_title="MainTitle",
    
    # Content parameters
    subtitle1="SUBTITLE1",
    content1="Content1",
    subtitle2="SUBTITLE2",
    content2="Content2",
    
    # Style parameters
    main_bg_color="#ffffff",  # White background
    accent_color="#d5e8b9",   # Light green accent
    title_color="#333333",
    subtitle_color="#333333",
    content_color="#555555",
    title_font_size="32px",
    subtitle_font_size="18px",
    content_font_size="16px",
    font_family="'Segoe UI', Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title, image on the right,
    and two content sections on the left.
    
    Parameters:
    - main_title: The main title of the slide
    - image_path: Path to the image file
    
    Content parameters:
    - subtitle1, subtitle2: Subtitles for each content section
    - content1, content2: Content text for each section
    
    Style parameters:
    - main_bg_color: Background color for the slide
    - accent_color: Color for accents and subtitle backgrounds
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
    <title>Image Right Slide</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 40px;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            height: calc(100% - 80px);
        }}
        
        .left-column {{
            width: 40%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 40px;
        }}
        
        .right-column {{
            width: 60%;
            padding-left: 40px;
            box-sizing: border-box;
        }}
        
        .image-container {{
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .content-section {{
            display: flex;
            flex-direction: column;
        }}
        
        .subtitle-container {{
            background-color: {accent_color};
            padding: 8px 15px;
            display: inline-block;
            margin-bottom: 10px;
            align-self: flex-start;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0;
            font-weight: bold;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0;
            line-height: 1.5;
            padding-left: 15px;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
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
                        <h3 class="subtitle">{subtitle1}</h3>
                    </div>
                    <p class="content">{content1}</p>
                </div>
                
                <!-- Content Section 2 -->
                <div class="content-section">
                    <div class="subtitle-container">
                        <h3 class="subtitle">{subtitle2}</h3>
                    </div>
                    <p class="content">{content2}</p>
                </div>
            </div>
            
            <!-- Right Column with Image -->
            <div class="right-column">
                <div class="image-container">
                    <img src="{image_path}" alt="Slide image">
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code


def generate_vertical_images_slide(
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
    title_font_size="32px",
    subtitle_font_size="28px",
    content_font_size="16px",
    font_family="'Segoe UI', Arial, sans-serif",
):
    """
    Generates an HTML slide with a main title, three vertical images on the left,
    and content with subtitle on the right.
    
    Parameters:
    - main_title: The main title of the slide
    - subtitle: The subtitle on the right side
    
    Image parameters:
    - image1_path, image2_path, image3_path: Paths to the three images
    
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
        body {{
            margin: 0;
            padding: 0;
            font-family: {font_family};
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        
        .slide-container {{
            width: 1000px;
            height: 560px;
            position: relative;
            background-color: {main_bg_color};
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            padding: 40px;
            box-sizing: border-box;
        }}
        
        .title-section {{
            display: flex;
            align-items: center;
            margin-bottom: 40px;
        }}
        
        .title-accent {{
            width: 30px;
            height: 30px;
            background-color: {accent_color};
            margin-right: 15px;
        }}
        
        .main-title {{
            font-size: {title_font_size};
            color: {title_color};
            font-weight: normal;
            font-style: italic;
            margin: 0;
        }}
        
        .content-layout {{
            display: flex;
            width: 100%;
            height: calc(100% - 80px);
        }}
        
        .left-column {{
            width: 40%;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .image-container {{
            width: 100%;
            height: calc(33.33% - 7px);
            overflow: hidden;
        }}
        
        .image-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .right-column {{
            width: 60%;
            padding-left: 40px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }}
        
        .subtitle {{
            font-size: {subtitle_font_size};
            color: {subtitle_color};
            margin: 0 0 15px 0;
            font-weight: normal;
            font-style: italic;
        }}
        
        .divider {{
            width: 100%;
            height: 3px;
            background-color: {divider_color};
            margin-bottom: 30px;
        }}
        
        .content {{
            font-size: {content_font_size};
            color: {content_color};
            margin: 0 0 20px 0;
            line-height: 1.6;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Title Section -->
        <div class="title-section">
            <div class="title-accent"></div>
            <h1 class="main-title">{main_title}</h1>
        </div>
        
        <!-- Content Layout -->
        <div class="content-layout">
            <!-- Left Column with Images -->
            <div class="left-column">
                <div class="image-container">
                    <img src="{image1_path}" alt="Image 1">
                </div>
                <div class="image-container">
                    <img src="{image2_path}" alt="Image 2">
                </div>
                <div class="image-container">
                    <img src="{image3_path}" alt="Image 3">
                </div>
            </div>
            
            <!-- Right Column with Content -->
            <div class="right-column">
                <h2 class="subtitle">{subtitle}</h2>
                <div class="divider"></div>
                <p class="content">{content1}</p>
                <p class="content">{content2}</p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_code