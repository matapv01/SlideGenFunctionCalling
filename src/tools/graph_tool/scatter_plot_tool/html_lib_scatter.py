def generate_scatter_plot_chart_slide_1(
    main_title = "Early Childhood Development Analysis",
    subtitle = "Correlation between Play Time and Social Skill Scores",
    insight = "Data shows a strong positive correlation: children with more than 4 hours of structured play weekly exhibit 30% higher social integration scores.",
    x_axis = "Weekly Play Time (Hours)",
    y_axis = "Social Skill Score (0-100)",
    unit = "pts",
    show_value = False,
    show_legend = True,
    x_axis_min = 0,
    x_axis_max = 8,
    y_axis_min = 30,
    y_axis_max = 200,
    series = [
        {
            "name": "Group A (Ages 3-4)",
            "points": [{"x": 2, "y": 45}, {"x": 3.5, "y": 58}, {"x": 5, "y": 72}, {"x": 6.2, "y": 85}]
        },
        {
            "name": "Group B (Ages 5-6)",
            "points": [{"x": 1.5, "y": 40}, {"x": 4, "y": 65}, {"x": 5.5, "y": 78}, {"x": 7, "y": 92}]
        }
    ]
) -> str:
    """
    Function to generate HTML for a scatter plot chart slide in a preschool educational style.
    Uses a blue color theme, decorative stickers, and a flat layout optimized for rendering.
    """

    # ===== STYLE CONFIGURATION =====
    colors = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#FF9F43"]
    font_family = "'Montserrat', sans-serif"
    accent_color = "#ffffff"
    main_title_color = "#ffffff"
    subtitle_color = "#3d4a85"
    insight_text_color = "#3d4a85"
    main_title_font_size = "70px"
    subtitle_font_size = "32px"
    insight_font_size = "28px"
    bg_color = "#7b92f7"

    # ===== 1. TÍNH TOÁN MIN/MAX ĐỂ SCALE BIỂU ĐỒ =====
    all_x = [p["x"] for s in series for p in s.get("points", [])]
    all_y = [p["y"] for s in series for p in s.get("points", [])]

    x_min = x_axis_min if x_axis_min is not None else 0
    x_max = x_axis_max if x_axis_max is not None else (max(all_x) if all_x else 100)
    y_min = y_axis_min if y_axis_min is not None else 0
    y_max = y_axis_max if y_axis_max is not None else (max(all_y) if all_y else 100)

    # Tránh chia cho 0
    if x_max == x_min: x_max += 1
    if y_max == y_min: y_max += 1

    # ===== 2. CẤU HÌNH SVG =====
    svg_w, svg_h = 1050, 650
    margin_t, margin_b, margin_l, margin_r = 60, 80, 100, 60
    chart_w = svg_w - margin_l - margin_r
    chart_h = svg_h - margin_t - margin_b

    chart_elements = ""

    # Vẽ Grid lines (ngang) và nhãn trục Y
    for i in range(6):
        ratio = i / 5
        y_pos = svg_h - margin_b - (ratio * chart_h)
        val = y_min + (y_max - y_min) * ratio
        chart_elements += f'<line x1="{margin_l}" y1="{y_pos}" x2="{svg_w - margin_r}" y2="{y_pos}" stroke="rgba(255,255,255,0.3)" stroke-width="1" />'
        chart_elements += f'<text x="{margin_l - 15}" y="{y_pos + 6}" font-size="18" text-anchor="end" fill="{main_title_color}">{val:g}</text>'

    # Vẽ các điểm dữ liệu
    for i, s in enumerate(series):
        color = colors[i % len(colors)]
        for p in s.get("points", []):
            cx = margin_l + ((p["x"] - x_min) / (x_max - x_min)) * chart_w
            cy = svg_h - margin_b - ((p["y"] - y_min) / (y_max - y_min)) * chart_h
            
            # Vẽ điểm với hiệu ứng sticker
            chart_elements += f'<circle cx="{cx}" cy="{cy}" r="12" fill="{color}" stroke="{accent_color}" stroke-width="3" />'
            
            if show_value:
                chart_elements += f'<text x="{cx}" y="{cy - 20}" font-size="16" text-anchor="middle" font-weight="bold" fill="{accent_color}">{p["y"]}{unit}</text>'

    # Vẽ trục X và Y chính
    chart_elements += f'<line x1="{margin_l}" y1="{svg_h - margin_b}" x2="{svg_w - margin_r}" y2="{svg_h - margin_b}" stroke="{accent_color}" stroke-width="4" stroke-linecap="round" />'
    chart_elements += f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{svg_h - margin_b}" stroke="{accent_color}" stroke-width="4" stroke-linecap="round" />'

    # Nhãn trục
    chart_elements += f'<text x="{margin_l + chart_w/2}" y="{svg_h - 20}" font-size="22" text-anchor="middle" fill="{accent_color}" font-weight="700">{x_axis}</text>'
    chart_elements += f'<text transform="rotate(-90)" x="{-margin_t - chart_h/2}" y="35" font-size="22" text-anchor="middle" fill="{accent_color}" font-weight="700">{y_axis}</text>'

    # ===== 3. RENDER LEGEND =====
    legend_html = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_html += f'''
            <div style="display:flex; align-items:center; margin-bottom:15px;">
                <div style="width:24px; height:24px; background:{color}; border:3px solid {accent_color}; border-radius:50%; margin-right:15px;"></div>
                <span style="font-size:24px; font-weight:700; color:{subtitle_color};">{s.get("name", "Group")}</span>
            </div>
            '''

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
            body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0; overflow: hidden;
                background-color: {bg_color}; font-family: {font_family};
                background-image: radial-gradient({accent_color} 2px, transparent 2px); background-size: 60px 60px;
            }}
            .header-box {{
                position: absolute; top: 60px; left: 100px; width: 1720px;
            }}
            .main-title {{
                font-size: {main_title_font_size}; font-weight: 700; color: {main_title_color}; margin: 0;
                text-shadow: 4px 4px 0px rgba(0,0,0,0.1);
            }}
            .subtitle-text {{
                font-size: {subtitle_font_size}; color: {subtitle_color}; margin-top: 10px; font-weight: 700;
            }}
            .chart-container {{
                position: absolute; top: 280px; left: 80px; width: {svg_w}px; height: {svg_h}px;
                background: rgba(255, 255, 255, 0.1); border-radius: 30px; border: 5px dashed rgba(255,255,255,0.4);
            }}
            .insight-container {{
                position: absolute; top: 280px; right: 100px; width: 550px;
            }}
            .insight-card {{
                background: #fffbe6; border: 8px solid {accent_color}; border-radius: 40px;
                padding: 40px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); margin-bottom: 40px;
            }}
            .insight-content {{
                font-size: {insight_font_size}; color: {insight_text_color}; line-height: 1.4; font-weight: 400;
            }}
            .legend-box {{
                background: rgba(255, 255, 255, 0.2); border-radius: 30px; padding: 30px; border: 4px solid {accent_color};
            }}
            .sticker {{
                position: absolute; font-size: 80px; background: {accent_color}; border-radius: 20px; padding: 10px;
                border: 5px solid {accent_color}; box-shadow: 5px 5px 0px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div class="sticker" style="top: 40px; right: 80px; transform: rotate(15deg);">✏️</div>
        <div class="sticker" style="top: 80px; right: 170px; transform: rotate(-10deg);">🎨</div>
        
        <div class="header-box">
            <h1 class="main-title">{main_title}</h1>
            <div class="subtitle-text">{subtitle if subtitle else ""}</div>
        </div>

        <div class="chart-container">
            <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                {chart_elements}
            </svg>
        </div>

        <div class="insight-container">
            <div class="insight-card">
                <div style="font-size: 30px; font-weight: 700; color: {subtitle_color}; margin-bottom: 15px;">Key Insight 💡</div>
                <div class="insight-content">{insight}</div>
            </div>
            <div class="legend-box">
                {legend_html}
            </div>
        </div>
    </body>
    </html>
    """

def generate_scatter_plot_chart_slide_2(
    main_title: str = "Relationship Between Travel Distance and Spending",
    subtitle: str = "Source: Tourist Behavior Survey 2024 | Sample: 200 Trips",
    insight: str = (
        "The scatter plot indicates a strong positive correlation between travel distance "
        "and total spending."
    ),
    x_axis= "Travel Distance (km)",
    y_axis = "Total Travel Spending (USD)",
    unit = "USD",
    show_value = False,
    show_legend = True,
    x_axis_min = 0,
    x_axis_max = 12000,
    y_axis_min = 0,
    y_axis_max = 6000,
    series = [
        {
            "name": "Domestic Travelers",
            "points": [
                {"x": 150, "y": 300},
                {"x": 300, "y": 450},
                {"x": 500, "y": 700},
                {"x": 800, "y": 900},
                {"x": 1200, "y": 1100},
                {"x": 2000, "y": 1500}
            ]
        },
        {
            "name": "International Travelers",
            "points": [
                {"x": 3000, "y": 2500},
                {"x": 5000, "y": 3200},
                {"x": 7000, "y": 4000},
                {"x": 9000, "y": 4800},
                {"x": 11000, "y": 5500},
                {"x": 2500, "y": 5000}
            ]
        }
    ]
) -> str:
    """
    Sinh HTML cho slide biểu đồ phân tán với phong cách 'Travel Plan'.
    Phân tích mối tương quan giữa các biến dựa trên tọa độ X và Y.
    """

    # ===== 1. STYLE CONFIGURATION =====
    colors = ["#008080", "#FFB347"]
    background_color = "#FEF9E1"
    insight_box_background_color = "#FFFFFF"
    chart_panel_background_color = "rgba(255, 255, 255, 0.5)"
    accent_color = "#008080"
    main_title_color = "#005F5F"
    subtitle_color = "#556B2F"
    insight_text_color = "#2C3E50"
    font_family = "'Inter', sans-serif"

    # ===== 2. TÍNH TOÁN MIN MAX VÀ SCALE =====
    all_x = [p["x"] for s in series for p in s.get("points", [])]
    all_y = [p["y"] for s in series for p in s.get("points", [])]

    x_min_val = x_axis_min if x_axis_min is not None else 0
    x_max_val = x_axis_max if x_axis_max is not None else (max(all_x) if all_x else 100)
    y_min_val = y_axis_min if y_axis_min is not None else 0
    y_max_val = y_axis_max if y_axis_max is not None else (max(all_y) if all_y else 100)

    if x_max_val == x_min_val: x_max_val += 1
    if y_max_val == y_min_val: y_max_val += 1

    # ===== 3. SVG CONFIG =====
    svg_w, svg_h = 1100, 700
    margin = {"top": 70, "bottom": 100, "left": 120, "right": 40}
    
    chart_w = svg_w - margin["left"] - margin["right"]
    chart_h = svg_h - margin["top"] - margin["bottom"]

    chart_elements = ""

    # Grid Y và Label Trục Y
    steps = 5
    for i in range(steps + 1):
        y_val_raw = y_min_val + (y_max_val - y_min_val) * (i / steps)
        y_pos = svg_h - margin["bottom"] - (i / steps) * chart_h
        
        chart_elements += f'<line x1="{margin["left"]}" y1="{y_pos}" x2="{svg_w - margin["right"]}" y2="{y_pos}" stroke="#E5E7EB" stroke-width="2" stroke-dasharray="8,4" />'
        chart_elements += f'<text x="{margin["left"] - 15}" y="{y_pos + 8}" font-size="20" text-anchor="end" fill="{subtitle_color}">{y_val_raw:g}</text>'

    # Trục X Labels
    for i in range(steps + 1):
        x_val_raw = x_min_val + (x_max_val - x_min_val) * (i / steps)
        x_pos = margin["left"] + (i / steps) * chart_w
        chart_elements += f'<text x="{x_pos}" y="{svg_h - margin["bottom"] + 40}" font-size="20" text-anchor="middle" fill="{subtitle_color}">{x_val_raw:g}</text>'

    # Trục chính
    chart_elements += f'''
        <line x1="{margin["left"]}" y1="{svg_h - margin["bottom"]}" x2="{svg_w - margin["right"]}" y2="{svg_h - margin["bottom"]}" stroke="{accent_color}" stroke-width="4" />
        <line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{svg_h - margin["bottom"]}" stroke="{accent_color}" stroke-width="4" />
    '''

    # Scatter Points
    for i, s in enumerate(series):
        color = colors[i % len(colors)]
        for p in s.get("points", []):
            px = margin["left"] + ((p["x"] - x_min_val) / (x_max_val - x_min_val)) * chart_w
            py = svg_h - margin["bottom"] - ((p["y"] - y_min_val) / (y_max_val - y_min_val)) * chart_h
            
            chart_elements += f'<circle cx="{px}" cy="{py}" r="12" fill="{color}" stroke="white" stroke-width="3" opacity="0.9" />'
            
            if show_value:
                chart_elements += f'<text x="{px}" y="{py - 20}" font-size="16" text-anchor="middle" fill="{insight_text_color}" font-weight="bold">{p["y"]}{unit}</text>'

    # Axis Labels
    chart_elements += f'''
        <text x="{margin["left"] + chart_w/2}" y="{svg_h - 20}" font-size="26" text-anchor="middle" font-weight="600" fill="{main_title_color}">{x_axis}</text>
        <text transform="rotate(-90)" x="{-margin["top"] - chart_h/2}" y="35" font-size="26" text-anchor="middle" font-weight="600" fill="{main_title_color}">{y_axis}</text>
    '''

    # ===== 4. LEGEND & INSIGHT =====
    legend_items = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_items += f'''
            <p style="display:flex; align-items:center; margin:0 0 15px 0;">
                <span style="display:inline-block; width:24px; height:24px; border-radius:50%; background:{color}; border:3px solid white; box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-right:15px;"></span>
                <span style="font-size:24px; font-weight:500; color:{insight_text_color};">{s.get("name", "Series")}</span>
            </p>
            '''

    # ===== 5. FINAL HTML RENDER =====
    html_code = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
            body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0;
                font-family: {font_family}; background-color: {background_color}; color: {insight_text_color};
                display: grid; 
                grid-template-rows: 280px 1fr;
                grid-template-columns: 1fr;
                row-gap: 20px;
                overflow: hidden;
            }}
            .header-section {{
                padding: 20px 100px 20px 100px;
            }}
            h1 {{
                font-size: 72px; color: {main_title_color}; margin: 0; font-weight: 800; 
                text-transform: uppercase; letter-spacing: -1px;
                border-left: 12px solid {accent_color}; padding-left: 35px;
            }}
            .subtitle {{
                font-size: 32px; color: {subtitle_color}; margin: 10px 0 0 47px; font-weight: 400;
            }}
            .content-area {{
                display: grid; 
                grid-template-columns: 500px 1fr;
                gap: 80px;
                padding: 10px 100px 60px 100px;
                position: center;
            }}
            .left-panel {{
                display: grid;
                grid-template-rows: auto auto;
                gap: 40px;
                align-content: space-around;
            }}
            .insight-box {{
                background: {insight_box_background_color}; padding: 30px; border-radius: 30px; 
                box-shadow: 15px 15px 0px rgba(0, 128, 128, 0.1);
                border: 3px solid {accent_color}; font-size: 28px; line-height: 1.5;
            }}
            .legend-area {{
                padding-left: 10px;
            }}
            .right-panel {{
                display: flex; align-items: center; justify-content: center;
                background: {chart_panel_background_color}; border-radius: 40px;
            }}
        </style>
    </head>
    <body>
        <div class="header-section">
            <h1>{main_title}</h1>
            <div class="subtitle">{subtitle if subtitle else ""}</div>
        </div>
        <div class="content-area">
            <div class="left-panel">
                <div class="insight-box">
                    {insight}
                </div>
                <div class="legend-area">
                    {legend_items}
                </div>
            </div>
            <div class="right-panel">
                <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                    {chart_elements}
                </svg>
            </div>
        </div>
    </body>
    </html> 
    """
    return html_code

def generate_scatter_plot_chart_slide_3(
    main_title: str = "Study Time and Exam Performance Trend",
    subtitle: str = "Study Time and Exam Performance Trend",
    insight: str = (
        "The scatter plot demonstrates a clear positive correlation between weekly "
        "self-study hours and final exam scores. Students participating in guided "
        "revision sessions consistently achieve higher scores at comparable effort "
        "levels."
    ),
    x_axis = "Weekly Self-Study Hours",
    y_axis = "Final Exam Score",
    unit = " points",
    show_value = False,
    show_legend = True,
    x_axis_min = 0,
    x_axis_max = 20,
    y_axis_min = 50,
    y_axis_max = 100,
    data_label_format = None,
    colors = ["#3D5A80", "#EE6C4D"],
    series = [
        {
            "name": "Independent Study Group",
            "points": [
                {"x": 3, "y": 58},
                {"x": 5, "y": 65},
                {"x": 7, "y": 72},
                {"x": 10, "y": 78},
                {"x": 14, "y": 82}
            ]
        },
        {
            "name": "Guided Revision Group",
            "points": [
                {"x": 4, "y": 68},
                {"x": 6, "y": 75},
                {"x": 9, "y": 85},
                {"x": 12, "y": 90},
                {"x": 15, "y": 94}
            ]
        }
    ]
) -> str:
    """
    Generates a professional scatter plot chart slide with a clean, 
    modern aesthetic inspired by educational and organic themes.
    """

    # ===== 0. STYLE CONFIGURATION (MOVED FROM PARAMETERS) =====
    font_family = "Inter, sans-serif"
    accent_color = "#7B8FB3"
    main_title_color = "#4A5E7B"
    subtitle_color = "#8E97A4"
    insight_text_color = "#4A5E7B"
    main_title_font_size = "65px"
    subtitle_font_size = "28px"
    insight_font_size = "30px"
    background_color = "#E8F5E9"

    # ===== 1. DATA PREPARATION =====
    x_label = x_axis
    y_label = y_axis

    # ===== 2. SVG CALCULATIONS =====
    svg_w, svg_h = 1100, 700
    margin = {"top": 60, "right": 60, "bottom": 100, "left": 120}
    
    chart_w = svg_w - margin["left"] - margin["right"]
    chart_h = svg_h - margin["top"] - margin["bottom"]

    # Calculate Data Boundaries
    all_points = [p for s in series for p in s.get("points", [])]
    all_x = [p["x"] for p in all_points] or [0]
    all_y = [p["y"] for p in all_points] or [0]

    x_min = x_axis_min if x_axis_min is not None else 0
    x_max = x_axis_max if x_axis_max is not None else max(all_x)
    y_min = y_axis_min if y_axis_min is not None else 0
    y_max = y_axis_max if y_axis_max is not None else max(all_y)

    # Add padding to boundaries if auto-calculated
    if x_max == x_min: x_max += 1
    if y_max == y_min: y_max += 1
    
    # Range buffers
    x_range = (x_max - x_min) * 1.1 if (x_max - x_min) != 0 else 1
    y_range = (y_max - y_min) * 1.1 if (y_max - y_min) != 0 else 1

    # ===== 3. RENDER SVG ELEMENTS =====
    chart_elements = ""

    # Grid lines (Horizontal)
    for i in range(6):
        y_tick = margin["top"] + (chart_h / 5) * i
        val = y_max - (i * (y_max - y_min) / 5)
        chart_elements += f'''
        <line x1="{margin["left"]}" y1="{y_tick}" x2="{svg_w - margin["right"]}" y2="{y_tick}" stroke="#E5E7EB" stroke-width="1" />
        <text x="{margin["left"] - 15}" y="{y_tick + 5}" font-size="18" text-anchor="end" fill="{subtitle_color}">{val:g}</text>
        '''

    # Axis lines
    chart_elements += f'''
    <line x1="{margin["left"]}" y1="{svg_h - margin["bottom"]}" x2="{svg_w - margin["right"]}" y2="{svg_h - margin["bottom"]}" stroke="{main_title_color}" stroke-width="2"/>
    <line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{svg_h - margin["bottom"]}" stroke="{main_title_color}" stroke-width="2"/>
    '''

    # Data Points
    for i, s in enumerate(series):
        color = colors[i % len(colors)]
        for p in s.get("points", []):
            # Scale coordinates
            cx = margin["left"] + ((p["x"] - x_min) / (x_max - x_min) * chart_w)
            cy = svg_h - margin["bottom"] - ((p["y"] - y_min) / (y_max - y_min) * chart_h)
            
            chart_elements += f'''
            <circle cx="{cx}" cy="{cy}" r="10" fill="{color}" stroke="white" stroke-width="2" opacity="0.9" />
            '''
            if show_value:
                label_text = data_label_format.format(**p) if data_label_format else f'{p["y"]}{unit}'
                chart_elements += f'''
                <text x="{cx}" y="{cy - 15}" font-size="16" text-anchor="middle" fill="{insight_text_color}">{label_text}</text>
                '''

    # Axis Labels
    chart_elements += f'''
    <text x="{margin["left"] + chart_w/2}" y="{svg_h - 30}" font-size="24" text-anchor="middle" font-weight="bold" fill="{main_title_color}">{x_label}</text>
    <text transform="rotate(-90)" x="{-margin["top"] - chart_h/2}" y="40" font-size="24" text-anchor="middle" font-weight="bold" fill="{main_title_color}">{y_label}</text>
    '''

    # ===== 4. LEGEND & INSIGHT HTML =====
    legend_items = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_items += f'''
            <div style="display:flex; align-items:center; margin-bottom:12px;">
                <div style="width:20px; height:20px; border-radius:50%; background:{color}; margin-right:12px; border:2px solid white; box-shadow:0 2px 4px rgba(0,0,0,0.1);"></div>
                <div style="font-size:22px; color:{main_title_color};">{s.get("name", "Series")}</div>
            </div>
            '''

    # ===== 5. FINAL HTML ASSEMBLY =====
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            html, body {{
                width: 1920px;
                height: 1080px;
                margin: 0;
                padding: 60px 80px;
                overflow: hidden;
                font-family: {font_family};
                background-color: {background_color};
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
            }}
            .header {{
                margin-bottom: 50px;
                border-left: 12px solid {accent_color};
                padding-left: 30px;
            }}
            h1 {{
                font-size: {main_title_font_size};
                color: {main_title_color};
                margin: 0;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .subtitle {{
                font-size: {subtitle_font_size};
                color: {subtitle_color};
                margin-top: 5px;
            }}
            .main-content {{
                display: flex;
                gap: 60px;
                align-items: flex-start;
            }}
            .left-panel {{
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 40px;
            }}
            .insight-card {{
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 10px 10px 0px {accent_color}22;
                border: 2px solid {accent_color}44;
                font-size: {insight_font_size};
                color: {insight_text_color};
                line-height: 1.6;
            }}
            .right-panel {{
                flex: 1.8;
                background: white;
                border-radius: 30px;
                padding: 30px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.05);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{main_title}</h1>
            {f'<p class="subtitle">{subtitle}</p>' if subtitle else ""}
        </div>
        <div class="main-content">
            <div class="left-panel">
                <div class="insight-card">
                    {insight}
                </div>
                <div class="legend-container">
                    {legend_items}
                </div>
            </div>
            <div class="right-panel">
                <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                    {chart_elements}
                </svg>
            </div>
        </div>
    </body>
    </html>
    """

def generate_scatter_plot_chart_slide_4(
    main_title: str = "Study Effort Drives Skill Mastery",
    subtitle: str = "Data from Online Python Course – Q4 2024 Cohort",
    insight: str = ("The scatter plot shows a strong positive relationship between weekly study hours "
        "and final skill assessment scores"),
    x_axis = "Weekly Study Hours",
    y_axis = "Final Skill Assessment Score",
    unit = " points",
    show_value = False,
    show_legend = True,
    x_axis_min = 0,
    x_axis_max = 25,
    y_axis_min = 40,
    y_axis_max = 100,
    data_label_format = None,
    colors = ["#4F46E5", "#F59E0B"],
    series = [
        {
            "name": "Self-Paced Learners",
            "points": [
                {"x": 4, "y": 55},
                {"x": 6, "y": 60},
                {"x": 8, "y": 68},
                {"x": 10, "y": 72},
                {"x": 14, "y": 82},
                {"x": 5, "y": 88}   # high score with lower effort (efficient learner)
            ]
        },
        {
            "name": "Instructor-Led Learners",
            "points": [
                {"x": 6, "y": 70},
                {"x": 9, "y": 78},
                {"x": 12, "y": 85},
                {"x": 15, "y": 90},
                {"x": 18, "y": 95},
                {"x": 20, "y": 97}
            ]
        }
    ]
) -> str:
    """
    Generates a professional scatter plot chart slide with a creative layout.
    The slide features a header section, an insight/legend panel on the left, 
    and a clean SVG scatter plot on the right.
    """

    # ===== 1. HARDCODED STYLES & OPTIONS =====
    font_family = "'Inter', sans-serif"
    accent_color = "#F59E0B"
    main_title_color = "#1F2937"
    subtitle_color = "#6B7280"
    insight_text_color = "#374151"
    main_title_font_size = "64px"
    subtitle_font_size = "28px"
    insight_font_size = "26px"

    # ===== 2. DATA PROCESSING =====
    x_label = x_axis
    y_label = y_axis

    # ===== 3. SVG & CHART CALCULATIONS =====
    svg_w, svg_h = 1100, 700
    margin = {"top": 60, "right": 60, "bottom": 100, "left": 100}
    chart_w = svg_w - margin["left"] - margin["right"]
    chart_h = svg_h - margin["top"] - margin["bottom"]

    # Calculate Min/Max for Scaling
    all_x = [p["x"] for s in series for p in s.get("points", [])]
    all_y = [p["y"] for s in series for p in s.get("points", [])]

    x_min = x_axis_min if x_axis_min is not None else 0
    x_max = x_axis_max if x_axis_max is not None else (max(all_x) if all_x else 100)
    y_min = y_axis_min if y_axis_min is not None else 0
    y_max = y_axis_max if y_axis_max is not None else (max(all_y) if all_y else 100)

    # Padding for min/max to prevent points on the edge
    if x_max == x_min: x_max += 1
    if y_max == y_min: y_max += 1

    # ===== 4. RENDER SVG ELEMENTS =====
    chart_elements = ""

    # Background Grid (Y-axis)
    grid_steps = 5
    for i in range(grid_steps + 1):
        y_val_grid = margin["top"] + (chart_h / grid_steps) * i
        y_display = y_max - (i * (y_max - y_min) / grid_steps)
        chart_elements += f'''
        <line x1="{margin["left"]}" y1="{y_val_grid}" x2="{svg_w - margin["right"]}" y2="{y_val_grid}" stroke="#E5E7EB" stroke-width="1" />
        <text x="{margin["left"] - 15}" y="{y_val_grid + 6}" font-size="18" text-anchor="end" fill="#9CA3AF">{round(y_display, 1)}</text>
        '''

    # Axes
    chart_elements += f'''
    <line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{svg_h - margin["bottom"]}" stroke="#374151" stroke-width="2"/>
    <line x1="{margin["left"]}" y1="{svg_h - margin["bottom"]}" x2="{svg_w - margin["right"]}" y2="{svg_h - margin["bottom"]}" stroke="#374151" stroke-width="2"/>
    '''

    # X-Axis Ticks
    for i in range(grid_steps + 1):
        x_val_grid = margin["left"] + (chart_w / grid_steps) * i
        x_display = x_min + (i * (x_max - x_min) / grid_steps)
        chart_elements += f'''
        <text x="{x_val_grid}" y="{svg_h - margin["bottom"] + 30}" font-size="18" text-anchor="middle" fill="#9CA3AF">{round(x_display, 1)}</text>
        '''

    # Scatter Points
    for i, s in enumerate(series):
        color = colors[i % len(colors)]
        for p in s.get("points", []):
            cx = margin["left"] + (p["x"] - x_min) / (x_max - x_min) * chart_w
            cy = svg_h - margin["bottom"] - (p["y"] - y_min) / (y_max - y_min) * chart_h
            
            chart_elements += f'''
            <circle cx="{cx}" cy="{cy}" r="12" fill="{color}" fill-opacity="0.7" stroke="{color}" stroke-width="2" />
            '''
            if show_value:
                label_text = data_label_format.format(**p) if data_label_format else f'{p["y"]}{unit}'
                chart_elements += f'<text x="{cx}" y="{cy - 18}" font-size="14" text-anchor="middle" font-weight="bold" fill="{main_title_color}">{label_text}</text>'

    # Axis Titles
    chart_elements += f'''
    <text x="{margin['left'] + chart_w/2}" y="{svg_h - 20}" font-size="22" text-anchor="middle" font-weight="bold" fill="{main_title_color}">{x_label}</text>
    <text transform="rotate(-90)" x="{-margin['top'] - chart_h/2}" y="30" font-size="22" text-anchor="middle" font-weight="bold" fill="{main_title_color}">{y_label}</text>
    '''

    # ===== 5. LEGEND & INSIGHT HTML =====
    legend_items = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_items += f'''
            <div style="display:flex; align-items:center; margin-bottom:12px;">
                <div style="width:20px; height:20px; background:{color}; border-radius:50%; margin-right:12px;"></div>
                <span style="font-size:22px; color:{main_title_color};">{s.get("name", "N/A")}</span>
            </div>
            '''

    # ===== 6. FINAL HTML CONSTRUCT =====
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
            html, body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0;
                font-family: {font_family}; background-color: #FFFFFF; overflow: hidden;
            }}
            .slide-container {{
                width: 100%; height: 100%; position: relative;
                background-image: radial-gradient(circle at 20px 20px, #f1f1f1 2px, transparent 0);
                background-size: 40px 40px;
            }}
            .top-section {{
                padding: 60px 100px 20px 100px;
                border-bottom: 2px dashed {accent_color};
            }}
            .main-content {{
                display: flex; padding: 40px 100px; gap: 60px;
            }}
            .left-column {{
                flex: 1; display: flex; flex-direction: column;
            }}
            .right-column {{
                flex: 2; background: #FAFAFA; border-radius: 40px; 
                padding: 30px; box-shadow: 15px 15px 0px {accent_color};
                border: 3px solid #333;
            }}
            .insight-box {{
                background: #FFF9E6; padding: 35px; border-radius: 20px;
                border: 2px solid {accent_color}; margin-bottom: 40px;
                font-size: {insight_font_size}; color: {insight_text_color};
                line-height: 1.6; position: relative;
            }}
            .insight-box::before {{
                content: "💡 Insight"; position: absolute; top: -20px; left: 20px;
                background: {accent_color}; color: white; padding: 5px 15px;
                border-radius: 10px; font-weight: bold; font-size: 20px;
            }}
            h1 {{ margin: 0; font-size: {main_title_font_size}; color: {main_title_color}; }}
            .subtitle {{ font-size: {subtitle_font_size}; color: {subtitle_color}; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="slide-container">
            <div class="top-section">
                <h1>{main_title}</h1>
                <div class="subtitle">{subtitle if subtitle else ""}</div>
            </div>
            <div class="main-content">
                <div class="left-column">
                    <div class="insight-box">{insight}</div>
                    <div class="legend-container">{legend_items}</div>
                </div>
                <div class="right-column">
                    <div>
                        <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                            {chart_elements}
                        </svg>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


def generate_scatter_plot_chart_slide_5(
    main_title: str = "Relationship Between App Usage Time and Monthly Spending",
    subtitle: str = "Source: Mobile App Analytics Report 2024 | Sample: 200 Users",
    insight: str = "Higher app usage correlates with increased digital spending among both user segments",

    x_axis: str = "Daily App Usage Time (minutes)",
    y_axis: str = "Monthly Digital Spending (USD)",
    unit: str = "USD",
    show_value: bool = False,
    show_legend: bool = True,

    x_axis_min: float = 0,
    x_axis_max: float = 600,
    y_axis_min: float = 0,
    y_axis_max: float = 500,

    series: list = [
        {
            "name": "Casual Users",
            "points": [
                {"x": 30, "y": 10},
                {"x": 60, "y": 20},
                {"x": 90, "y": 35},
                {"x": 120, "y": 50},
                {"x": 150, "y": 65},
                {"x": 180, "y": 80}
            ]
        },
        {
            "name": "Power Users",
            "points": [
                {"x": 240, "y": 120},
                {"x": 300, "y": 180},
                {"x": 360, "y": 250},
                {"x": 420, "y": 320},
                {"x": 480, "y": 400},
                {"x": 200, "y": 450}
            ]
        }
    ]
) -> str:
    """
    Generates a professional scatter plot chart slide with a futuristic tech startup theme.
    """

    # ===== 1. STYLE CONFIGURATION =====
    font_family = "'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    accent_color = "#009688"
    main_title_color = "#FFFFFF"
    subtitle_color = "rgba(255, 255, 255, 0.7)"
    insight_text_color = "#FFFFFF"
    main_title_font_size = "65px"
    subtitle_font_size = "32px"
    insight_font_size = "30px"
    colors = ["#008080", "#FFB347"]

    # ===== 2. DATA EXTRACTION =====
    x_axis_label = x_axis
    y_axis_label = y_axis

    # ===== 3. SVG CONFIGURATION =====
    svg_w, svg_h = 1100, 700
    margin_t, margin_b, margin_l, margin_r = 60, 100, 100, 60
    
    chart_w = svg_w - margin_l - margin_r
    chart_h = svg_h - margin_t - margin_b

    # ===== 4. SCALE CALCULATION =====
    all_x = [p["x"] for s in series for p in s.get("points", [])]
    all_y = [p["y"] for s in series for p in s.get("points", [])]

    x_min = x_axis_min if x_axis_min is not None else 0
    x_max = x_axis_max if x_axis_max is not None else (max(all_x) if all_x else 100)
    
    y_min = y_axis_min if y_axis_min is not None else 0
    y_max = y_axis_max if y_axis_max is not None else (max(all_y) if all_y else 100)

    if x_max == x_min: x_max += 1
    if y_max == y_min: y_max += 1

    # ===== 5. RENDER SVG ELEMENTS =====
    chart_elements = ""

    for i in range(6):
        y_tick = margin_t + (chart_h / 5) * i
        y_val = y_max - (i * (y_max - y_min) / 5)
        chart_elements += f'''
        <line x1="{margin_l}" y1="{y_tick}" x2="{svg_w - margin_r}" y2="{y_tick}" 
              stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
        <text x="{margin_l - 15}" y="{y_tick + 6}" font-size="18" text-anchor="end" fill="{subtitle_color}">{y_val:g}</text>
        '''

    chart_elements += f'''
    <line x1="{margin_l}" y1="{svg_h - margin_b}" x2="{svg_w - margin_r}" y2="{svg_h - margin_b}" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
    <line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{svg_h - margin_b}" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
    '''

    for i, s in enumerate(series):
        color = colors[i % len(colors)]
        for p in s.get("points", []):
            cx = margin_l + (p["x"] - x_min) / (x_max - x_min) * chart_w
            cy = svg_h - margin_b - (p["y"] - y_min) / (y_max - y_min) * chart_h
            
            chart_elements += f'''
            <circle cx="{cx}" cy="{cy}" r="12" fill="{color}" fill-opacity="0.3"/>
            <circle cx="{cx}" cy="{cy}" r="6" fill="{color}"/>
            '''
            
            if show_value:
                chart_elements += f'''
                <text x="{cx}" y="{cy - 18}" font-size="16" text-anchor="middle" fill="#FFFFFF">{p["y"]}{unit}</text>
                '''

    chart_elements += f'''
    <text x="{margin_l + chart_w/2}" y="{svg_h - 30}" font-size="22" text-anchor="middle" fill="{main_title_color}" font-weight="bold">{x_axis_label}</text>
    <text transform="rotate(-90)" x="{-margin_t - chart_h/2}" y="30" font-size="22" text-anchor="middle" fill="{main_title_color}" font-weight="bold">{y_axis_label}</text>
    '''

    # ===== 6. LEGEND & INSIGHT =====
    legend_html = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_html += f'''
            <div style="display:flex;align-items:center;margin-bottom:12px;">
                <div style="width:20px;height:20px;background:{color};border-radius:50%;margin-right:15px;box-shadow:0 0 10px {color}88;"></div>
                <span style="font-size:24px;color:#FFFFFF;opacity:0.9;">{s.get("name","Series")}</span>
            </div>
            '''

    insight_content = f'''
    <div style="background:rgba(255,255,255,0.05);padding:35px;border-radius:20px;border-left:5px solid {accent_color};">
        <div style="font-size:{insight_font_size};color:{insight_text_color};line-height:1.5;font-weight:300;">{insight}</div>
    </div>
    '''

    # ===== 7. FINAL HTML =====
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body, html {{
                width: 1920px; height: 1080px; margin: 0; padding: 0; overflow: hidden;
                font-family: {font_family};
                background: radial-gradient(circle at 10% 40%, rgba(0, 150, 136, 0.3) 0%, transparent 40%),
                            radial-gradient(circle at 90% 30%, rgba(106, 27, 154, 0.4) 0%, transparent 50%),
                            radial-gradient(circle at 50% 60%, rgba(26, 35, 126, 0.8) 0%, transparent 70%),
                            #03042e;
                color: #FFFFFF;
            }}
            .top-header {{
                padding: 60px 100px 0 100px;
                height: 200px;
            }}
            .main-container {{
                display: flex;
                padding: 0 100px;
                height: 750px;
                justify-content: space-between;
                align-items: flex-start;
            }}
            .content-left {{
                width: 550px;
            }}
            .chart-right {{
                width: 1100px;
                background: rgba(255, 255, 255, 0.03);
                border-radius: 30px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.1);
            }}
            h1 {{
                font-size: {main_title_font_size};
                margin: 0;
                font-weight: 500;
                letter-spacing: -2px;
            }}
            .subtitle {{
                font-size: {subtitle_font_size};
                color: {subtitle_color};
                margin-top: 10px;
                font-weight: 300;
            }}
            .footer-line {{
                position: absolute;
                bottom: 60px;
                left: 100px;
                right: 100px;
                display: flex;
                align-items: center;
                gap: 20px;
                opacity: 0.5;
            }}
            .line-draw {{ flex-grow: 1; height: 1px; background: rgba(255,255,255,0.3); }}
        </style>
    </head>
    <body>
        <div class="top-header">
            <h1>{main_title}</h1>
            <div class="subtitle">{subtitle}</div>
        </div>

        <div class="main-container">
            <div class="content-left">
                {insight_content}
                <div style="margin-top: 50px;">{legend_html}</div>
            </div>
            <div class="chart-right">
                <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" style="width:100%;height:100%;display:block;">
                    {chart_elements}
                </svg>
            </div>
        </div>

        <div class="footer-line">
            <span style="font-size: 20px;">Tech Startup Analytics</span>
            <div class="line-draw"></div>
        </div>
    </body>
    </html>
    """

def generate_scatter_plot_chart_slide_6(
    main_title: str = "Relationship Between Study Time and Academic Performance",
    subtitle: str = "Source: Education Analytics Report 2024 | Sample: 200 Students",
    insight: str = "High achievers tend to study more, but optimal study time varies among students",

    x_axis: str = "Daily Study Time (minutes)",
    y_axis: str = "Exam Score (Points)",
    unit: str = "",
    show_value: bool = False,
    show_legend: bool = True,
    x_axis_min: int = 0,
    x_axis_max: int = 600,
    y_axis_min: int = 0,
    y_axis_max: int = 500,

    series: list = [
        {
            "name": "Average Students",
            "points": [
                {"x": 30, "y": 10},
                {"x": 60, "y": 20},
                {"x": 90, "y": 35},
                {"x": 120, "y": 50},
                {"x": 150, "y": 65},
                {"x": 180, "y": 80}
            ]
        },
        {
            "name": "High Achievers",
            "points": [
                {"x": 240, "y": 120},
                {"x": 300, "y": 180},
                {"x": 360, "y": 250},
                {"x": 420, "y": 320},
                {"x": 480, "y": 400},
                {"x": 200, "y": 450}
            ]
        }
    ]
) -> str:
    """
    Hàm tạo slide biểu đồ phân tán (Scatter Plot) với theme 'AI In Education'.
    Sử dụng phong cách thiết kế hiện đại, các hình khối vuông trang trí và dải sóng nền.
    """

    # ===== 1. STYLE CONFIGURATION (MOVED FROM PARAMETERS) =====
    font_family = "'Montserrat', sans-serif"
    accent_color = "#008080"
    main_title_color = "#005F5F"
    subtitle_color = "#556B2F"
    insight_text_color = "#2C3E50"
    main_title_font_size = "80px"
    subtitle_font_size = "30px"
    insight_font_size = "28px"
    colors = ["#008080", "#FFB347"]

    # ===== 2. LẤY THÔNG TIN & CẤU HÌNH DỮ LIỆU =====
    options = {
        "unit": unit,
        "show_value": show_value,
        "show_legend": show_legend,
        "x_axis": x_axis,
        "y_axis": y_axis,
        "x_axis_min": x_axis_min,
        "x_axis_max": x_axis_max,
        "y_axis_min": y_axis_min,
        "y_axis_max": y_axis_max
    }

    data = {
        "series": series
    }

    series = data.get("series", [])

    unit = options.get("unit", "")
    show_value = options.get("show_value", False)
    show_legend = options.get("show_legend", True)
    
    x_label = options.get("x_axis", "X Axis")
    y_label = options.get("y_axis", "Y Axis")

    # ===== 3. SVG CONFIG & TÍNH TOÁN TỌA ĐỘ =====
    svg_w, svg_h = 1000, 600
    m_top, m_bottom, m_left, m_right = 60, 80, 100, 60
    
    c_w = svg_w - m_left - m_right
    c_h = svg_h - m_top - m_bottom

    # Tìm Min/Max để scale
    all_x = [p["x"] for s in series for p in s.get("points", [])]
    all_y = [p["y"] for s in series for p in s.get("points", [])]

    x_min = options.get("x_axis_min") if options.get("x_axis_min") is not None else 0
    x_max = options.get("x_axis_max") if options.get("x_axis_max") is not None else (max(all_x) if all_x else 100)
    y_min = options.get("y_axis_min") if options.get("y_axis_min") is not None else 0
    y_max = options.get("y_axis_max") if options.get("y_axis_max") is not None else (max(all_y) if all_y else 100)

    # Tránh chia cho 0
    dx = (x_max - x_min) if x_max != x_min else 1
    dy = (y_max - y_min) if y_max != y_min else 1

    # ===== 4. VẼ BIỂU ĐỒ (SVG ELEMENTS) =====
    chart_elements = ""
    
    # Grid lines (Y-axis)
    for i in range(5):
        y_tick = m_top + (c_h / 4) * i
        chart_elements += f'<line x1="{m_left}" y1="{y_tick}" x2="{svg_w - m_right}" y2="{y_tick}" stroke="#ccc" stroke-dasharray="4"/>'

    # Vẽ các điểm dữ liệu
    for i, s in enumerate(series):
        color = colors[i % len(colors)]
        for p in s.get("points", []):
            cx = m_left + (p["x"] - x_min) / dx * c_w
            cy = svg_h - m_bottom - (p["y"] - y_min) / dy * c_h
            
            chart_elements += f'<circle cx="{cx}" cy="{cy}" r="10" fill="{color}" opacity="0.8" />'
            if show_value:
                chart_elements += f'<text x="{cx}" y="{cy-15}" font-size="16" text-anchor="middle" fill="{main_title_color}">{p["y"]}{unit}</text>'

    # Trục tọa độ & Nhãn
    chart_elements += f'''
        <line x1="{m_left}" y1="{m_top}" x2="{m_left}" y2="{svg_h - m_bottom}" stroke="{main_title_color}" stroke-width="2"/>
        <line x1="{m_left}" y1="{svg_h - m_bottom}" x2="{svg_w - m_right}" y2="{svg_h - m_bottom}" stroke="{main_title_color}" stroke-width="2"/>
        <text x="{svg_w/2 + m_left/2}" y="{svg_h - 20}" font-size="22" text-anchor="middle" font-weight="bold" fill="{main_title_color}">{x_label}</text>
        <text transform="rotate(-90)" x="{-svg_h/2 + 10}" y="40" font-size="22" text-anchor="middle" font-weight="bold" fill="{main_title_color}">{y_label}</text>
    '''

    # ===== 5. LEGEND & INSIGHT HTML =====
    legend_items = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_items += f'''
            <div style="display:flex; align-items:center; margin-bottom:12px;">
                <div style="width:20px; height:20px; background:{color}; margin-right:10px; border-radius:4px;"></div>
                <span style="font-size:22px; color:{main_title_color}; font-weight:bold;">{s.get("name")}</span>
            </div>'''

    # ===== 6. GENERATE FINAL HTML =====
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;800;900&display=swap');
            html, body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0;
                overflow: hidden; font-family: {font_family};
                background-color: #e5dbf1; color: {main_title_color};
            }}
            .square {{
                position: absolute; background-color: {accent_color};
                width: 50px; height: 50px; opacity: 0.6; z-index: 1;
            }}
            .waves {{
                position: absolute; bottom: -10%; left: -10%; right: -10%; height: 60%;
                background: linear-gradient(110deg, rgba(255,255,255,0) 20%, rgba(215,188,245,0.4) 40%, rgba(255,255,255,0.6) 50%, rgba(196,160,233,0.3) 60%, rgba(255,255,255,0) 80%);
                transform: skewY(-8deg); z-index: 0;
            }}
            .header-container {{
                display: flex; justify-content: space-between; align-items: flex-start;
                padding: 80px 120px 0 120px; position: relative; z-index: 10;
            }}
            .title-box {{ flex: 2; }}
            .title-box h1 {{
                font-size: {main_title_font_size}; font-weight: 900; margin: 0;
                line-height: 1; text-transform: uppercase; color: {main_title_color};
            }}
            .subtitle-box {{
                flex: 1; text-align: right; font-size: {subtitle_font_size};
                color: {subtitle_color}; font-weight: 400; margin-top: 15px;
            }}
            .content-container {{
                display: flex; padding: 60px 120px; gap: 80px;
                position: relative; z-index: 10; align-items: center;
            }}
            .chart-area {{
                flex: 1.2; background: rgba(255,255,255,0.5);
                border-radius: 40px; padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.05);
            }}
            .insight-area {{
                flex: 1; display: flex; flex-direction: column; gap: 30px;
            }}
            .insight-text {{
                font-size: {insight_font_size}; line-height: 1.5;
                color: {insight_text_color}; background: rgba(255,255,255,0.3);
                padding: 30px; border-radius: 20px; border-left: 10px solid {accent_color};
            }}
        </style>
    </head>
    <body>
        <div class="square" style="top: 0; left: 55%; width: 70px; height: 70px;"></div>
        <div class="square" style="top: 45%; left: 0;"></div>
        <div class="square" style="bottom: 5%; left: 30%;"></div>
        <div class="square" style="top: 38%; right: 0; width: 80px; height: 80px;"></div>
        
        <div class="waves"></div>

        <div class="header-container">
            <div class="title-box">
                <h1>{main_title}</h1>
            </div>
            <div class="subtitle-box">
                {subtitle if subtitle else ""}
            </div>
        </div>

        <div class="content-container">
            <div class="insight-area">
                <div class="insight-text">{insight}</div>
                <div class="legend-box">{legend_items}</div>
            </div>
            <div class="chart-area">
                <svg width="100%" height="100%" viewBox="0 0 {svg_w} {svg_h}" preserveAspectRatio="xMidYMid meet">
                    {chart_elements}
                </svg>
            </div>
        </div>
    </body>
    </html>
    """

def generate_scatter_plot_chart_slide_7(
    main_title: str = "Relationship Between App Usage Time and Monthly Spending",
    subtitle: str = "Source: Mobile App Analytics Report 2024 | Sample: 200 Users",
    insight: str = "",
    x_axis= "App Usage Time (minutes/day)",
    y_axis = "Monthly Digital Spending (USD)",
    unit = "USD",
    show_value = False,
    show_legend = True,
    x_axis_min = 0,
    x_axis_max = 400,
    y_axis_min = 0,
    y_axis_max = 300,
    series = [
        {
            "name": "Casual Users",
            "points": [
                {"x": 30, "y": 10},
                {"x": 60, "y": 20},
                {"x": 90, "y": 35}
            ]
        },
        {
            "name": "Power Users",
            "points": [
                {"x": 240, "y": 120},
                {"x": 300, "y": 180},
                {"x": 360, "y": 250}
            ]
        }
    ]
) -> str:
    """
    Hàm sinh HTML cho slide biểu đồ phân tán với phong cách Renaissance cổ điển.
    Sử dụng SVG thuần và CSS Layout phẳng để tối ưu hóa việc render.
    """

    # ===== 1. STYLE CONFIGURATION =====
    colors = ["#a06d4f", "#6b8e23"]
    accent_color = "#a06d4f"
    main_title_color = "#3e2f25"
    subtitle_color = "#5a4638"
    insight_text_color = "#3e2f25"
    font_family = "'Playfair Display', serif"
    main_title_font_size = "60px"
    subtitle_font_size = "28px"
    insight_font_size = "30px"

    # ===== 2. TRÍCH XUẤT DỮ LIỆU =====
    data_input = {
        "series": series
    }

    chart_options = {
        "x_axis": x_axis,
        "y_axis": y_axis,
        "unit": unit,
        "show_value": show_value,
        "show_legend": show_legend,
        "x_axis_min": x_axis_min,
        "x_axis_max": x_axis_max,
        "y_axis_min": y_axis_min,
        "y_axis_max": y_axis_max
    }

    series = data_input.get("series", [])
    options = chart_options if chart_options else {}
    
    unit = options.get("unit", "")
    show_value = options.get("show_value", False)
    show_legend = options.get("show_legend", True)
    
    x_label = options.get("x_axis", "X Axis")
    y_label = options.get("y_axis", "Y Axis")

    # ===== 3. TÍNH TOÁN MIN/MAX ĐỂ SCALE BIỂU ĐỒ =====
    all_x = [p["x"] for s in series for p in s.get("points", [])]
    all_y = [p["y"] for s in series for p in s.get("points", [])]

    x_min = options.get("x_axis_min") if options.get("x_axis_min") is not None else 0
    x_max = options.get("x_axis_max") if options.get("x_axis_max") is not None else (max(all_x) if all_x else 100)
    y_min = options.get("y_axis_min") if options.get("y_axis_min") is not None else 0
    y_max = options.get("y_axis_max") if options.get("y_axis_max") is not None else (max(all_y) if all_y else 100)

    if x_max == x_min: x_max += 1
    if y_max == y_min: y_max += 1

    # ===== 4. CẤU HÌNH SVG =====
    svg_w, svg_h = 1100, 700
    margin_t, margin_b, margin_l, margin_r = 60, 80, 100, 40
    chart_w = svg_w - margin_l - margin_r
    chart_h = svg_h - margin_t - margin_b

    chart_elements = ""

    for i in range(6):
        y_ratio = i / 5
        y_pos = svg_h - margin_b - (y_ratio * chart_h)
        val = y_min + (y_max - y_min) * y_ratio
        chart_elements += f'<line x1="{margin_l}" y1="{y_pos}" x2="{svg_w - margin_r}" y2="{y_pos}" stroke="#c8a98d" stroke-dasharray="4,4" stroke-width="1" />'
        chart_elements += f'<text x="{margin_l - 15}" y="{y_pos + 6}" font-size="18" text-anchor="end" fill="{subtitle_color}">{int(val)}</text>'

    for i, s in enumerate(series):
        color = colors[i % len(colors)]
        for p in s.get("points", []):
            cx = margin_l + ((p["x"] - x_min) / (x_max - x_min)) * chart_w
            cy = svg_h - margin_b - ((p["y"] - y_min) / (y_max - y_min)) * chart_h
            
            chart_elements += f'<circle cx="{cx}" cy="{cy}" r="10" fill="{color}" fill-opacity="0.7" stroke="#3e2f25" stroke-width="1.5" />'
            
            if show_value:
                chart_elements += f'<text x="{cx}" y="{cy - 15}" font-size="16" text-anchor="middle" fill="{main_title_color}">{p["y"]}{unit}</text>'

    chart_elements += f'<line x1="{margin_l}" y1="{svg_h - margin_b}" x2="{svg_w - margin_r}" y2="{svg_h - margin_b}" stroke="{accent_color}" stroke-width="2" />'
    chart_elements += f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{svg_h - margin_b}" stroke="{accent_color}" stroke-width="2" />'

    chart_elements += f'<text x="{margin_l + chart_w/2}" y="{svg_h - 20}" font-size="22" text-anchor="middle" fill="{main_title_color}" font-weight="600">{x_label}</text>'
    chart_elements += f'<text transform="rotate(-90)" x="{-margin_t - chart_h/2}" y="35" font-size="22" text-anchor="middle" fill="{main_title_color}" font-weight="600">{y_label}</text>'

    legend_items = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_items += f'''
            <div style="display:flex; align-items:center; margin-bottom:12px;">
                <div style="width:20px; height:20px; background:{color}; border:1px solid #3e2f25; border-radius:50%; margin-right:12px;"></div>
                <span style="font-size:22px; color:{main_title_color};">{s.get("name", "Group")}</span>
            </div>
            '''
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0; overflow: hidden;
                background-color: #efe5d8; font-family: {font_family}; color: {main_title_color};
                background-image: radial-gradient(rgba(0,0,0,0.02) 1px, transparent 1px); background-size: 8px 8px;
            }}
            .corner {{ position: absolute; width: 100px; height: 100px; border: 3px solid {accent_color}; z-index: 10; }}
            .top-left {{ top: 30px; left: 30px; border-right: none; border-bottom: none; border-radius: 20px 0 0 0; }}
            .top-right {{ top: 30px; right: 30px; border-left: none; border-bottom: none; border-radius: 0 20px 0 0; }}
            .bottom-left {{ bottom: 30px; left: 30px; border-right: none; border-top: none; border-radius: 0 0 0 20px; }}
            .bottom-right {{ bottom: 30px; right: 30px; border-left: none; border-top: none; border-radius: 0 0 20px 0; }}
            
            .header-container {{
                position: absolute; top: 80px; left: 120px; width: 1680px;
                text-align: left; border-bottom: 2px solid {accent_color}; padding-bottom: 20px;
            }}
            .main-title {{ font-size: {main_title_font_size}; font-weight: 600; margin: 0; }}
            .subtitle-text {{ font-size: {subtitle_font_size}; color: {subtitle_color}; margin-top: 10px; font-style: italic; }}
            
            .chart-panel {{ position: absolute; top: 280px; left: 100px; width: {svg_w}px; height: {svg_h}px; }}
            
            .insight-panel {{
                position: absolute; top: 280px; right: 120px; width: 500px;
                background: rgba(255, 255, 255, 0.3); border: 1.5px solid {accent_color};
                padding: 40px; border-radius: 10px;
            }}
            .insight-title {{ font-size: 24px; font-weight: 600; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid {accent_color}; }}
            .insight-content {{ font-size: {insight_font_size}; color: {insight_text_color}; line-height: 1.5; }}
            .legend-container {{ margin-top: 40px; }}
        </style>
    </head>
    <body>
        <div class="corner top-left"></div>
        <div class="corner top-right"></div>
        <div class="corner bottom-left"></div>
        <div class="corner bottom-right"></div>

        <div class="header-container">
            <h1 class="main-title">{main_title}</h1>
            <div class="subtitle-text">{subtitle if subtitle else ""}</div>
        </div>

        <div class="chart-panel">
            <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                {chart_elements}
            </svg>
        </div>

        <div class="insight-panel">
            <div class="insight-title">Phân tích dữ liệu</div>
            <div class="insight-content">{insight}</div>
            <div class="legend-container">
                {legend_items}
            </div>
        </div>
    </body>
    </html>
    """
