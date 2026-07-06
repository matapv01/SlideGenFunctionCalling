import math

def generate_pie_chart_slide_1(
    main_title = "Quarterly Revenue Breakdown",
    subtitle = "Data Source: Financial Year 2025 Reports",
    insight = "AI Services now account for nearly half of total revenue growth.",
    chart_type = "pie",
    unit = "%",
    show_value = True,
    show_legend = True,
    data_label_format = "{value}{unit}",
    items = [
        {"label": "AI Services", "value": 45},
        {"label": "Cloud Hosting", "value": 25},
        {"label": "Consulting", "value": 20},
        {"label": "Support", "value": 10}
    ]
) -> str:
    # Color and font configuration
    colors = ["#818CF8", "#2DD4BF", "#FBBF24", "#FB7185"]
    font_family = "Inter, sans-serif"
    accent_color = "#F472B6"
    main_title_color = "#38BDF8"
    subtitle_color = "#CCCCCC"
    insight_text_color = "#FFFFFF"
    main_title_font_size = "70px"
    subtitle_font_size = "32px"
    insight_font_size = "34px"
    legend_font_size = "25px"
    background_color = "#0F172A"
    
    # Calculate SVG Pie Chart Slices
    total = sum(item['value'] for item in items)
    cumulative_percent = 0
    svg_paths = ""
    legend_html = ""

    for i, item in enumerate(items):
        color = colors[i % len(colors)]
        percent = (item['value'] / total) * 100
           
        # For simplicity in a single-file HTML output, we use a stroke-dasharray approach
        offset = 100 - cumulative_percent + 25
        svg_paths += f'<circle r="15.9" cx="21" cy="21" fill="transparent" stroke="{color}" stroke-width="8" stroke-dasharray="{percent} {100-percent}" stroke-dashoffset="{offset}" />'
        
        cumulative_percent += percent
        
        if show_legend:
            formatted_value = data_label_format.format(value=item['value'], unit=unit) if show_value else ""
            label_suffix = f" ({formatted_value})" if show_value else ""
            legend_html += f'''
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: {legend_font_size}; height: {legend_font_size}; background: {color}; margin-right: 10px; border-radius: 3px;"></div>
                <span style="color: white; font-size: {legend_font_size};">{item['label']}{label_suffix}</span>
            </div>'''

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                background-color: {background_color};
                font-family: {font_family};
                color: white;
                height: 100vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                --accent-color: {accent_color};
                --main-title-color: {main_title_color};
                --subtitle-color: {subtitle_color};
                --insight-text-color: {insight_text_color};
                --main-title-font-size: {main_title_font_size};
                --subtitle-font-size: {subtitle_font_size};
                --insight-font-size: {insight_font_size};
                --legend-font-size: {legend_font_size};
            }}
            .upper-section {{
                padding: 60px 80px 20px 80px;
            }}
            .main-title {{
                font-size: var(--main-title-font-size);
                color: var(--main-title-color);
                font-weight: 800;
                margin: 0;
                text-transform: uppercase;
            }}
            .subtitle {{
                font-size: var(--subtitle-font-size);
                color: var(--subtitle-color);
                opacity: 0.8;
                margin-top: 10px;
            }}
            .main-content {{
                display: flex;
                flex: 1;
                padding: 0 80px 60px 80px;
                align-items: center;
            }}
            .left-section {{
                flex: 1;
                padding-right: 40px;
            }}
            .insight-box {{
                border-left: 5px solid var(--accent-color);
                padding: 20px 30px;
                background: rgba(255, 255, 255, 0.05);
                font-size: var(--insight-font-size);
                color: var(--insight-text-color);
                margin-bottom: 40px;
                line-height: 1.4;
            }}
            .right-section {{
                flex: 1;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .chart-container {{
                width: 450px;
                height: 450px;
            }}
            svg {{
                transform: rotate(-90deg);
                border-radius: 50%;
            }}
        </style>
    </head>
    <body>
        <div class="upper-section">
            <h1 class="main-title">{main_title}</h1>
            <div class="subtitle">{subtitle}</div>
        </div>
        
        <div class="main-content">
            <div class="left-section">
                <div class="insight-box">
                    {insight}
                </div>
                <div class="legend">
                    {legend_html}
                </div>
            </div>
            
            <div class="right-section">
                <div class="chart-container">
                    <svg viewBox="0 0 42 42" width="100%" height="100%">
                        {svg_paths}
                        {f'<circle r="12" cx="21" cy="21" fill="{background_color}" />' if chart_type == "donut" else ""}
                    </svg>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def generate_pie_chart_slide_2(
    main_title = "Technology Market Share 2024",
    subtitle = "Source: Global Tech Market Report",
    insight = (
        "AI services dominate the market with nearly half of the total share, "
        "while cloud infrastructure and cybersecurity continue to grow steadily."
    ),
    chart_type = "pie",
    unit = "%",
    show_value = True,
    show_legend = True,
    data_label_format = "{value}{unit}",
    items = [
        {"label": "AI Services", "value": 45},
        {"label": "Cloud Infrastructure", "value": 25},
        {"label": "Cybersecurity", "value": 18},
        {"label": "IoT Platforms", "value": 12}
    ]
) -> str:

    # Color and font configuration
    colors = ["#32CD32", "#FF7F50", "#FFD700", "#8A2BE2"]
    font_family = "Inter, sans-serif"
    accent_color = "#5FD9D3"
    main_title_color = "#5FD9D3"
    subtitle_color = "#FFFFFF"
    insight_text_color = "#FFFFFF"
    main_title_font_size = "70px"
    subtitle_font_size = "32px"
    insight_font_size = "34px"

    items = items or []
    # ===== SVG CONFIG =====
    svg_w, svg_h = 1000, 700
    center_x, center_y = svg_w / 2, svg_h / 2

    radius = 280
    inner_radius = radius * 0.6 if chart_type == "donut" else 0

    total = sum(item.get("value", 0) for item in items)
    if total == 0:
        total = 1

    chart_elements = ""
    current_angle = -90

    for idx, item in enumerate(items):

        value = item.get("value", 0)
        percentage = (value / total) * 100
        slice_angle = (value / total) * 360
        color = colors[idx % len(colors)]

        start_rad = math.radians(current_angle)
        end_rad = math.radians(current_angle + slice_angle)

        x1 = center_x + radius * math.cos(start_rad)
        y1 = center_y + radius * math.sin(start_rad)

        x2 = center_x + radius * math.cos(end_rad)
        y2 = center_y + radius * math.sin(end_rad)

        large_arc = 1 if slice_angle > 180 else 0

        if chart_type == "donut":

            ix1 = center_x + inner_radius * math.cos(start_rad)
            iy1 = center_y + inner_radius * math.sin(start_rad)

            ix2 = center_x + inner_radius * math.cos(end_rad)
            iy2 = center_y + inner_radius * math.sin(end_rad)

            path_data = (
                f"M {x1} {y1} "
                f"A {radius} {radius} 0 {large_arc} 1 {x2} {y2} "
                f"L {ix2} {iy2} "
                f"A {inner_radius} {inner_radius} 0 {large_arc} 0 {ix1} {iy1} Z"
            )

        else:

            path_data = (
                f"M {center_x} {center_y} "
                f"L {x1} {y1} "
                f"A {radius} {radius} 0 {large_arc} 1 {x2} {y2} Z"
            )

        chart_elements += f'''
        <path d="{path_data}" fill="{color}" stroke="{accent_color}" stroke-width="3"/>
        '''

        if show_value and slice_angle > 15:

            mid_rad = math.radians(current_angle + slice_angle / 2)

            label_r = (radius + inner_radius) / 2 if chart_type == "donut" else radius * 0.7

            lx = center_x + label_r * math.cos(mid_rad)
            ly = center_y + label_r * math.sin(mid_rad)

            label_text = data_label_format.replace("{value}", f"{percentage:.1f}").replace("{unit}", unit)

            chart_elements += f'''
            <text x="{lx}" y="{ly}" fill="white"
            font-size="20" font-weight="bold"
            text-anchor="middle"
            dominant-baseline="middle">
            {label_text}
            </text>
            '''

        current_angle += slice_angle

    # ===== LEGEND =====
    legend_html = ""

    if show_legend:

        for i, item in enumerate(items):

            color = colors[i % len(colors)]
            perc = (item.get("value", 0) / total) * 100

            legend_html += f'''
            <div style="display:flex;align-items:center;margin-bottom:20px;">
                <div style="width:24px;height:24px;background:{color};
                border-radius:4px;margin-right:15px;
                box-shadow:0 0 10px {color}66;"></div>

                <div style="color:white;font-size:24px;">
                {item.get("label","")}
                <span style="color:{accent_color};opacity:0.8;">
                ({perc:.1f}%)
                </span>
                </div>
            </div>
            '''

    # ===== HTML =====
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">

    <style>

    html,body{{
        width:1920px;
        height:1080px;
        margin:0;
        padding:0;
        overflow:hidden;
        font-family:{font_family};
        background: linear-gradient(135deg, #020c24, #1a2a4a, {accent_color});
        color:white;
        --accent-color: {accent_color};
        --main-title-color: {main_title_color};
        --subtitle-color: {subtitle_color};
        --insight-text-color: {insight_text_color};
        --main-title-font-size: {main_title_font_size};
        --subtitle-font-size: {subtitle_font_size};
        --insight-font-size: {insight_font_size};
    }}

    .bg-decoration{{
        position:absolute;
        width:100%;
        height:100%;
        z-index:0;
        background:radial-gradient(circle at 90% 90%, #1a2a4a 0%, transparent 50%);
    }}

    .container{{
    position:relative;
    z-index:1;
    padding:80px 100px;
    height:920px;
    display:flex;
    flex-direction:column;
    }}

    .header-box{{
    margin-bottom:60px;
    border-left:10px solid var(--accent-color);
    padding-left:35px;
    }}

    h1{{
        font-size: var(--main-title-font-size);
        color: var(--main-title-color);
        margin:0;
        text-transform:uppercase;
        letter-spacing:2px;
    }}

    .subtitle{{
        font-size: var(--subtitle-font-size);
        color: var(--subtitle-color);
        margin-top:10px;
        opacity:0.8;
    }}

    .content-grid{{
    display:flex;
    flex:1;
    gap:80px;
    align-items:center;
    }}

    .left-col{{
    flex:1;
    display:flex;
    flex-direction:column;
    }}

    .insight-box{{
        background:rgba(255,255,255,0.05);
        border:2px solid var(--accent-color);
        border-radius:25px;
        box-shadow:0 0 15px var(--accent-color)AA;
        padding:35px;
        margin-bottom:40px;
        font-size: var(--insight-font-size);
        color: var(--insight-text-color);
        line-height:1.5;
    }}

    .right-col{{
    flex:1.2;
    display:flex;
    justify-content:center;
    align-items:center;
    }}

    .right-col svg{{
    max-width:100%;
    height:auto;
    }}

    </style>
    </head>

    <body>

    <div class="bg-decoration"></div>

    <div class="container">

    <div class="header-box">
    <h1>{main_title}</h1>
    <div class="subtitle">{subtitle}</div>
    </div>

    <div class="content-grid">

    <div class="left-col">

    <div class="insight-box">
    {insight}
    </div>

    <div class="legend-container">
    {legend_html}
    </div>

    </div>

    <div class="right-col">

    <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
    {chart_elements}
    </svg>

    </div>

    </div>

    </div>

    </body>
    </html>
    """
    return html_code

def generate_pie_chart_slide_3(
    main_title: str = "MILITARY ALLOCATION",
    subtitle: str = "Regional Force Distribution & Resource Management",
    insight: str = (
        "The majority of forces are concentrated in regional units to ensure "
        "rapid response, while specialized corps maintain technical superiority "
        "across all major military routes."
    ),
    chart_type: str = "donut",
    unit: str = "%",
    show_value: bool = False,
    show_legend: bool = True,
    data_label_format: str = "{value}{unit}",
    items: list = [
        {"label": "Regional Units", "value": 40},
        {"label": "Specialized Corps", "value": 25},
        {"label": "Supply Division", "value": 20},
        {"label": "Scouting Network", "value": 15}
    ]
) -> str:
    """
    Hàm sinh HTML cho slide biểu đồ tròn phong cách Ingoude.
    Sử dụng màu xanh lục bảo đậm và màu vàng cát làm điểm nhấn.
    """
    
    # Color and font configuration
    colors = ["#c0935d", "#8e6d45", "#5c482e", "#d4af37", "#a67c00"]
    font_family = "'Cormorant Garamond', serif"
    accent_color = "#c0935d"
    main_title_color = "#f0f0f0"
    subtitle_color = "#c0935d"
    insight_text_color = "#ffffff"
    main_title_font_size = "100px"
    subtitle_font_size = "32px"
    insight_font_size = "30px"
    
    items = items or []
    # ===== SVG CONFIG =====
    svg_w, svg_h = 700, 700
    center_x, center_y = svg_w / 2, svg_h / 2
    radius = 280
    inner_radius = radius * 0.65 if chart_type == "donut" else 0

    total = sum(item.get("value", 0) for item in items)
    if total == 0: total = 1

    chart_elements = ""
    current_angle = -90

    for idx, item in enumerate(items):
        value = item.get("value", 0)
        percentage = (value / total) * 100
        slice_angle = (value / total) * 360
        color = colors[idx % len(colors)]

        start_rad = math.radians(current_angle)
        end_rad = math.radians(current_angle + slice_angle)

        x1 = center_x + radius * math.cos(start_rad)
        y1 = center_y + radius * math.sin(start_rad)
        x2 = center_x + radius * math.cos(end_rad)
        y2 = center_y + radius * math.sin(end_rad)

        large_arc = 1 if slice_angle > 180 else 0

        if chart_type == "donut":
            ix1 = center_x + inner_radius * math.cos(start_rad)
            iy1 = center_y + inner_radius * math.sin(start_rad)
            ix2 = center_x + inner_radius * math.cos(end_rad)
            iy2 = center_y + inner_radius * math.sin(end_rad)
            path_data = (
                f"M {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2} "
                f"L {ix2} {iy2} A {inner_radius} {inner_radius} 0 {large_arc} 0 {ix1} {iy1} Z"
            )
        else:
            path_data = (
                f"M {center_x} {center_y} L {x1} {y1} "
                f"A {radius} {radius} 0 {large_arc} 1 {x2} {y2} Z"
            )

        chart_elements += f'<path d="{path_data}" fill="{color}" stroke="#1a2e26" stroke-width="4"/>'

        if show_value and slice_angle > 15:
            mid_rad = math.radians(current_angle + slice_angle / 2)
            label_r = (radius + inner_radius) / 2 if chart_type == "donut" else radius * 0.7
            lx, ly = center_x + label_r * math.cos(mid_rad), center_y + label_r * math.sin(mid_rad)
            label_text = data_label_format.replace("{value}", f"{percentage:.1f}").replace("{unit}", unit)
            chart_elements += f'<text x="{lx}" y="{ly}" fill="white" font-size="22" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{label_text}</text>'

        current_angle += slice_angle

    # Trang trí tâm biểu đồ (Donut)
    if chart_type == "donut":
        chart_elements += f'''
        <circle cx="{center_x}" cy="{center_y}" r="{inner_radius - 5}" fill="none" stroke="{accent_color}" stroke-width="1" stroke-dasharray="10,5" opacity="0.5"/>
        <text x="{center_x}" y="{center_y}" fill="{accent_color}" font-size="40" text-anchor="middle" dominant-baseline="middle" font-family="{font_family}">100%</text>
        '''

    # ===== LEGEND =====
    legend_html = ""
    if show_legend:
        for i, item in enumerate(items):
            color = colors[i % len(colors)]
            perc = (item.get("value", 0) / total) * 100
            legend_html += f'''
            <div style="display:flex; align-items:center; margin-bottom:25px;">
                <div style="width:18px; height:18px; background:{color}; margin-right:15px; border:1px solid rgba(255,255,255,0.3);"></div>
                <div style="color:white; font-size:24px; font-weight:300; letter-spacing:1px;">
                    {item.get("label","").upper()} <span style="color:{accent_color}; margin-left:10px;">{perc:.1f}%</span>
                </div>
            </div>
            '''

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Inter:wght@300;400&display=swap" rel="stylesheet">
        <style>
            html, body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0; overflow: hidden;
                font-family: {font_family}; background-color: #1a2e26; color: white;
                --colors-0: {colors[0]};
                --colors-1: {colors[1]};
                --colors-2: {colors[2]};
                --colors-3: {colors[3]};
                --colors-4: {colors[4]};
                --accent-color: {accent_color};
                --main-title-color: {main_title_color};
                --subtitle-color: {subtitle_color};
                --insight-text-color: {insight_text_color};
                --main-title-font-size: {main_title_font_size};
                --subtitle-font-size: {subtitle_font_size};
                --insight-font-size: {insight_font_size};
            }}
            .main-container {{
                position: relative; width: 100%; height: 100%;
                display: flex; flex-direction: column; padding: 80px 100px; box-sizing: border-box;
            }}
            .top-border {{
                position: absolute; top: 0; left: 0; width: 100%; height: 15px; background: var(--accent-color);
            }}
            .header-section {{
                margin-bottom: 50px;
            }}
            h1 {{
                font-size: var(--main-title-font-size); color: var(--main-title-color); margin: 0;
                padding: 40px; margin-bottom: 50px; position: relative;
            }}
            .insight-card::before {{
                content: '❈'; position: absolute; top: -15px; left: 20px; background: #1a2e26;
                padding: 0 10px; color: {accent_color}; font-size: 24px;
            }}
            .insight-text {{
                font-size: {insight_font_size}; color: {insight_text_color}; line-height: 1.6; font-style: italic;
            }}
            .right-panel {{
                flex: 1.2; display: flex; justify-content: center; align-items: flex-start;
                background: radial-gradient(circle, rgba(192,147,93,0.05) 0%, transparent 70%);
            }}
        </style>
    </head>
    <body>
        <div class="top-border"></div>
        <div class="main-container">
            <div class="header-section">
                <h1>{main_title}</h1>
                <div class="subtitle">{subtitle}</div>
            </div>
            <div class="content-grid">
                <div class="left-panel">
                    <div class="insight-card">
                        <div class="insight-text">{insight}</div>
                    </div>
                    <div class="legend-box">
                        {legend_html}
                    </div>
                </div>
                <div class="right-panel">
                    <div class="svg-wrapper">
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
    return html_code

def generate_pie_chart_slide_4(
    main_title = "Global Ecosystem Distribution",
    subtitle = "Source: International Nature Conservation Report",
    insight = (
        "Forests make up the largest share of Earth's ecosystems, "
        "supporting the highest biodiversity, while oceans and wetlands "
        "play crucial roles in climate regulation and wildlife habitats."
    ),
    chart_type = "donut",
    unit = "%",
    show_value = True,
    show_legend = True,
    data_label_format = "{value}{unit}",
    items = [
            {"label": "Forests", "value": 40},
            {"label": "Oceans", "value": 30},
            {"label": "Grasslands", "value": 18},
            {"label": "Wetlands", "value": 12}
        ]
) -> str:
    """
    Tạo slide biểu đồ tròn hoặc donut với bố cục hiện đại.
    Phù hợp để trình bày tỷ lệ phần trăm, phân bổ ngân sách hoặc thị phần.
    """

    # ===== COLOR AND FONT CONFIGURATION =====
    colors = ["#5FD9D3", "#4ABFB9", "#36A6A0", "#248C87"]
    font_family = "Inter, sans-serif"
    accent_color = "#38B2AC"
    main_title_color = "#2C7A7B"
    subtitle_color = "#4A5568"
    insight_text_color = "#2D3748"
    main_title_font_size = "70px"
    subtitle_font_size = "32px"
    insight_font_size = "34px"

    # ===== 2. SVG CONFIG =====
    svg_w, svg_h = 800, 800
    center_x, center_y = svg_w / 2, svg_h / 2
    radius = 320
    inner_radius = radius * 0.6 if chart_type == "donut" else 0

    # ===== 3. TÍNH TỔNG & PHẦN TRĂM =====
    total = sum(item.get("value", 0) for item in items)
    if total == 0: total = 1

    # ===== 4. VẼ CHART =====
    chart_elements = ""
    current_angle = -90 
    
    for idx, item in enumerate(items):
        label = item.get("label", "")
        value = item.get("value", 0)
        percentage = (value / total) * 100
        color = colors[idx % len(colors)]
        slice_angle = (value / total) * 360
        
        start_angle_rad = math.radians(current_angle)
        end_angle_rad = math.radians(current_angle + slice_angle)
        
        # Điểm ngoài
        x1 = center_x + radius * math.cos(start_angle_rad)
        y1 = center_y + radius * math.sin(start_angle_rad)
        x2 = center_x + radius * math.cos(end_angle_rad)
        y2 = center_y + radius * math.sin(end_angle_rad)
        
        large_arc = 1 if slice_angle > 180 else 0
        
        if chart_type == "donut":
            # Điểm trong
            ix1 = center_x + inner_radius * math.cos(start_angle_rad)
            iy1 = center_y + inner_radius * math.sin(start_angle_rad)
            ix2 = center_x + inner_radius * math.cos(end_angle_rad)
            iy2 = center_y + inner_radius * math.sin(end_angle_rad)
            
            path_data = f"M {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2} L {ix2} {iy2} A {inner_radius} {inner_radius} 0 {large_arc} 0 {ix1} {iy1} Z"
        else:
            path_data = f"M {center_x} {center_y} L {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2} Z"
        
        chart_elements += f'<path d="{path_data}" fill="{color}" stroke="#ffffff" stroke-width="3" />'
        
        # Nhãn giá trị trên lát cắt
        if show_value and slice_angle > 15:
            mid_angle = math.radians(current_angle + slice_angle / 2)
            label_r = (radius + inner_radius) / 2 if chart_type == "donut" else radius * 0.7
            lx = center_x + label_r * math.cos(mid_angle)
            ly = center_y + label_r * math.sin(mid_angle)
            
            display_text = data_label_format.replace("{label}", label).replace("{value}", f"{percentage:.1f}").replace("{unit}", unit)
            chart_elements += f'<text x="{lx}" y="{ly}" fill="white" font-size="24" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{display_text}</text>'
            
        current_angle += slice_angle

    # ===== 5. LEGEND & INSIGHT =====
    legend_items = ""
    if show_legend:
        for idx, item in enumerate(items):
            color = colors[idx % len(colors)]
            perc = (item.get("value", 0) / total) * 100
            legend_items += f'''
            <div style="display:flex; align-items:center; margin-bottom:20px;">
                <div style="width:24px; height:24px; background:{color}; border-radius:6px; margin-right:15px;"></div>
                <div style="font-size:24px; color:{insight_text_color};">
                    <strong>{item.get("label")}</strong>: {item.get("value")}{unit} ({perc:.1f}%)
                </div>
            </div>'''

    # ===== 6. HTML RENDER =====
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

    body {{
        width:1920px;
        height:1080px;
        margin:0;
        padding:0;
        font-family:'{font_family}', sans-serif;
        background: linear-gradient(135deg,#e0f7f1 0%,#f7f3ff 100%);
        position:relative;
        overflow:hidden;
        --colors-0: {colors[0]};
        --colors-1: {colors[1]};
        --colors-2: {colors[2]};
        --colors-3: {colors[3]};
        --accent-color: {accent_color};
        --main-title-color: {main_title_color};
        --subtitle-color: {subtitle_color};
        --insight-text-color: {insight_text_color};
        --main-title-font-size: {main_title_font_size};
        --subtitle-font-size: {subtitle_font_size};
        --insight-font-size: {insight_font_size};
    }}

    .blob {{
        position:absolute;
        filter:blur(40px);
        opacity:0.6;
    }}

    .title-block {{
        position:absolute;
        top:80px;
        left:100px;
        font-size: var(--main-title-font-size);
        color: var(--main-title-color);
        font-weight:800;
    }}

    .subtitle-block {{
        position:absolute;
        top:160px;
        left:100px;
        font-size: var(--subtitle-font-size);
        color: var(--subtitle-color);
    }}

    .insight-block {{
        position:absolute;
        top:260px;
        left:100px;
        width:520px;
        background:rgba(255,255,255,0.5);
        backdrop-filter:blur(10px);
        border-radius:30px;
        padding:40px;
        font-size: var(--insight-font-size);
        color: var(--insight-text-color);
        line-height:1.6;
    }}

    .legend-block {{
        position:absolute;
        top:700px;
        left:100px;
        width:520px;
    }}

    .chart-block {{
        position:absolute;
        top:160px;
        right:120px;
        width:800px;
        height:800px;
    }}
    </style>
    </head>

    <body>

    <div class="blob" style="width:600px;height:600px;background:#63E6BE;top:-200px;left:-100px;border-radius:40% 60% 70% 30%;"></div>

    <div class="blob" style="width:500px;height:500px;background:#B197FC;bottom:-100px;right:-100px;border-radius:30% 70% 50% 50%;"></div>

    <div class="title-block">
    {main_title}
    </div>

    <div class="subtitle-block">
    {subtitle}
    </div>

    <div class="insight-block">
    {insight}
    </div>

    <div class="legend-block">
    {legend_items}
    </div>

    <div class="chart-block">
    <svg viewBox="0 0 800 800" width="100%" height="100%">
    {chart_elements}
    {f'<circle cx="400" cy="400" r="{inner_radius}" fill="transparent"/>' if chart_type == "donut" else ""}
    </svg>
    </div>

    </body>
    </html>
    """

def generate_pie_chart_slide_5(
    main_title = "Retail Banking Product Usage",
    subtitle = "Source: Global Banking Consumer Survey",
    insight = (
        "Savings accounts remain the most widely used banking product, "
        "while credit cards and personal loans continue to grow as "
        "consumers rely more on digital payments and flexible financing."
    ),
    chart_type = "donut",
    unit = "%",
    show_value = True,
    show_legend = True,
    data_label_format = "{value}{unit}",
    items = [
        {"label": "Savings Accounts", "value": 42},
        {"label": "Credit Cards", "value": 27},
        {"label": "Personal Loans", "value": 19},
        {"label": "Investment Accounts", "value": 12}
    ]
) -> str:

    # ===== 1. COLOR & FONT CONFIG =====
    colors = ["#5FD9D3", "#4ABFB9", "#36A6A0", "#248C87"]
    font_family = "Inter, sans-serif"
    accent_color = "#5FD9D3"
    main_title_color = "#5FD9D3"
    subtitle_color = "#FFFFFF"
    insight_text_color = "#FFFFFF"
    main_title_font_size = "70px"
    subtitle_font_size = "32px"
    insight_font_size = "34px"

    # ===== 2. DATA =====
    items = items or []

    # ===== 3. SVG CONFIG =====
    svg_w = 900
    svg_h = 700

    center_x = svg_w / 2
    center_y = svg_h / 2

    radius = 280
    inner_radius = radius * 0.6 if chart_type == "donut" else 0

    # ===== 4. CALCULATE =====
    total = sum(item.get("value", 0) for item in items)
    if total == 0:
        total = 1

    # ===== 5. DRAW PIE =====
    chart_elements = ""
    current_angle = -90

    for idx, item in enumerate(items):

        val = item.get("value", 0)

        percentage = (val / total) * 100
        slice_angle = (val / total) * 360

        color = colors[idx % len(colors)]

        start_rad = math.radians(current_angle)
        end_rad = math.radians(current_angle + slice_angle)

        x1_out = center_x + radius * math.cos(start_rad)
        y1_out = center_y + radius * math.sin(start_rad)

        x2_out = center_x + radius * math.cos(end_rad)
        y2_out = center_y + radius * math.sin(end_rad)

        large_arc = 1 if slice_angle > 180 else 0

        if chart_type == "donut":

            x1_in = center_x + inner_radius * math.cos(start_rad)
            y1_in = center_y + inner_radius * math.sin(start_rad)

            x2_in = center_x + inner_radius * math.cos(end_rad)
            y2_in = center_y + inner_radius * math.sin(end_rad)

            d = (
                f"M {x1_out} {y1_out} "
                f"A {radius} {radius} 0 {large_arc} 1 {x2_out} {y2_out} "
                f"L {x2_in} {y2_in} "
                f"A {inner_radius} {inner_radius} 0 {large_arc} 0 {x1_in} {y1_in} Z"
            )

        else:

            d = (
                f"M {center_x} {center_y} "
                f"L {x1_out} {y1_out} "
                f"A {radius} {radius} 0 {large_arc} 1 {x2_out} {y2_out} Z"
            )

        chart_elements += f'''
        <path d="{d}" fill="{color}" stroke="#ffffff" stroke-width="3"/>
        '''

        if show_value and slice_angle > 15:

            mid_angle = math.radians(current_angle + slice_angle / 2)

            label_r = (radius + inner_radius) / 2 if chart_type == "donut" else radius * 0.7

            lx = center_x + label_r * math.cos(mid_angle)
            ly = center_y + label_r * math.sin(mid_angle)

            label_text = data_label_format.replace(
                "{value}", f"{percentage:.1f}"
            ).replace("{label}", item.get("label", ""))

            chart_elements += f'''
            <text
                x="{lx}"
                y="{ly}"
                fill="white"
                font-size="20"
                font-weight="bold"
                text-anchor="middle"
                dominant-baseline="middle"
            >
                {label_text}
            </text>
            '''

        current_angle += slice_angle

    # ===== 6. LEGEND =====
    legend_items = ""

    if show_legend:

        for idx, item in enumerate(items):

            color = colors[idx % len(colors)]
            perc = (item.get("value", 0) / total) * 100

            legend_items += f'''
            <div style="display:flex;align-items:center;margin-bottom:12px;">
                <div style="width:24px;height:24px;background:{color};border-radius:4px;margin-right:15px;"></div>
                <div style="font-size:24px;color:#1F2937;">
                    {item.get("label")}
                    <span style="color:#6B7280;margin-left:8px;">
                        ({perc:.1f}%)
                    </span>
                </div>
            </div>
            '''

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>

    body {{
        width:1920px;
        height:1080px;
        margin:0;
        padding:0;
        font-family:{font_family};
        background:#FFFFFF;
        --colors-0: {colors[0]};
        --colors-1: {colors[1]};
        --colors-2: {colors[2]};
        --colors-3: {colors[3]};
        --accent-color: {accent_color};
        --main-title-color: {main_title_color};
        --subtitle-color: {subtitle_color};
        --insight-text-color: {insight_text_color};
        --main-title-font-size: {main_title_font_size};
        --subtitle-font-size: {subtitle_font_size};
        --insight-font-size: {insight_font_size};
    }}

    .container {{
        padding:80px 100px;
    }}

    .header {{
        border-left:12px solid var(--accent-color);
        padding-left:40px;
        margin-bottom:60px;
    }}

    h1 {{
        margin:0;
        font-size:var(--main-title-font-size);
        color:var(--main-title-color);
    }}

    .subtitle {{
        font-size:var(--subtitle-font-size);
        color:var(--subtitle-color);
    }}

    .layout {{
        display:flex;
        justify-content:space-between;
    }}

    .left-panel {{
        width:650px;
    }}

    .chart-panel {{
        width:900px;
    }}

    .insight-card {{
        background:var(--accent-color);
        border-radius:20px;
        padding:40px;
        margin-bottom:40px;
        border-top:5px solid var(--accent-color);
    }}

    .insight-text {{
        font-size:var(--insight-font-size);
        color:var(--insight-text-color);
    }}

    </style>
    </head>

    <body>

    <div class="container">

    <div class="header">
    <h1>{main_title}</h1>
    <div class="subtitle">{subtitle}</div>
    </div>

    <div class="layout">

    <div class="left-panel">

    <div class="insight-card">
    <div class="insight-text">{insight}</div>
    </div>

    <div class="legend-container">
    {legend_items}
    </div>

    </div>

    <div class="chart-panel">

    <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
    {chart_elements}
    </svg>

    </div>

    </div>

    </div>

    </body>
    </html>
    """

    return html_code

def generate_pie_chart_slide_6(
    main_title = "Global Personal Investment Allocation",
    subtitle = "Source: International Financial Market Report",
    insight = (
        "Stocks remain the dominant investment choice for long-term wealth growth, "
        "while bonds and real estate continue to provide stability and diversification "
        "in global personal portfolios."
    ),
    unit = "%",
    chart_type = "pie",
    show_value = True,
    show_legend = True,
    data_label_format = "{value}%",
    items = [
        {"label": "Stocks", "value": 45},
        {"label": "Bonds", "value": 25},
        {"label": "Real Estate", "value": 20},
        {"label": "Commodities", "value": 10}
    ]
) -> str:

    # Color and font configuration
    colors = ["#C9A227", "#A8892F", "#7A6525", "#4F4318"]
    font_family = "Inter, sans-serif"
    accent_color = "#C9A227"
    main_title_color = "#3A2F1F"
    subtitle_color = "#6B5E3B"
    insight_text_color = "#4B4030"
    main_title_font_size = "70px"
    subtitle_font_size = "32px"
    insight_font_size = "34px"

    items = items or []

    svg_w, svg_h = 900, 700
    center_x = svg_w / 2
    center_y = svg_h / 2
    radius = 280
    inner_radius = radius * 0.6 if chart_type == "donut" else 0

    total = sum(item.get("value", 0) for item in items)
    if total == 0:
        total = 1

    chart_elements = ""
    current_angle = -90

    for idx, item in enumerate(items):

        label = item.get("label", "")
        value = item.get("value", 0)

        percentage = (value / total) * 100
        color = colors[idx % len(colors)]
        slice_angle = (value / total) * 360

        start_angle_rad = math.radians(current_angle)
        end_angle_rad = math.radians(current_angle + slice_angle)

        x1 = center_x + radius * math.cos(start_angle_rad)
        y1 = center_y + radius * math.sin(start_angle_rad)

        x2 = center_x + radius * math.cos(end_angle_rad)
        y2 = center_y + radius * math.sin(end_angle_rad)

        large_arc_flag = 1 if slice_angle > 180 else 0

        if chart_type == "donut":

            ix1 = center_x + inner_radius * math.cos(start_angle_rad)
            iy1 = center_y + inner_radius * math.sin(start_angle_rad)

            ix2 = center_x + inner_radius * math.cos(end_angle_rad)
            iy2 = center_y + inner_radius * math.sin(end_angle_rad)

            path_data = (
                f"M {x1} {y1} "
                f"A {radius} {radius} 0 {large_arc_flag} 1 {x2} {y2} "
                f"L {ix2} {iy2} "
                f"A {inner_radius} {inner_radius} 0 {large_arc_flag} 0 {ix1} {iy1} Z"
            )

        else:

            path_data = (
                f"M {center_x} {center_y} "
                f"L {x1} {y1} "
                f"A {radius} {radius} 0 {large_arc_flag} 1 {x2} {y2} Z"
            )

        chart_elements += f'''
        <path d="{path_data}" fill="{color}" stroke="#F5EFE6" stroke-width="3"/>
        '''

        if show_value and slice_angle > 15:

            mid_angle = math.radians(current_angle + slice_angle / 2)

            label_r = (
                (radius + inner_radius) / 2
                if chart_type == "donut"
                else radius * 0.7
            )

            lx = center_x + label_r * math.cos(mid_angle)
            ly = center_y + label_r * math.sin(mid_angle)

            txt = (
                data_label_format
                .replace("{value}", f"{percentage:.1f}")
                .replace("{label}", label)
            )

            chart_elements += f'''
            <text x="{lx}" y="{ly}"
            font-size="20"
            text-anchor="middle"
            fill="white"
            font-weight="600"
            style="text-shadow:1px 1px 2px rgba(0,0,0,0.3)">
            {txt}
            </text>
            '''

        current_angle += slice_angle

    legend_items = ""

    if show_legend:
        for i, item in enumerate(items):

            color = colors[i % len(colors)]
            val_str = f"{item.get('value', 0)}{unit}"

            legend_items += f'''
            <div style="display:flex; align-items:center; margin-bottom:18px;">
                <div style="width:24px;height:24px;background:{color};
                border-radius:4px;margin-right:15px;"></div>

                <div style="font-size:24px;color:{main_title_color};flex:1;">
                    {item.get("label", "")}
                </div>

                <div style="font-size:24px;color:{accent_color};font-weight:bold;">
                    {val_str}
                </div>
            </div>
            '''

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">

    <style>

    html,body{{
    width:1920px;
    height:1080px;
    margin:0;
    padding:0;
    overflow:hidden;
    font-family:'{font_family}';
    background:#F8F6F1;
    --accent-color: {accent_color};
    --main-title-color: {main_title_color};
    --subtitle-color: {subtitle_color};
    --insight-text-color: {insight_text_color};
    --main-title-font-size: {main_title_font_size};
    --subtitle-font-size: {subtitle_font_size};
    --insight-font-size: {insight_font_size};
    --color-0: {colors[0]};
    --color-1: {colors[1]};
    --color-2: {colors[2]};
    --color-3: {colors[3]};
    }}

    .header{{
    position:absolute;
    top:80px;
    left:100px;
    border-left:12px solid var(--accent-color);
    padding-left:35px;
    }}

    h1{{
    font-size:var(--main-title-font-size);
    color:var(--main-title-color);
    margin:0;
    text-transform:uppercase;
    letter-spacing:2px;
    }}

    .subtitle{{
    font-size:var(--subtitle-font-size);
    color:var(--subtitle-color);
    margin-top:10px;
    }}

    .chart{{
    position:absolute;
    left:100px;
    top:260px;
    }}

    .insight{{
    position:absolute;
    right:120px;
    top:320px;
    width:640px;
    background:white;
    padding:45px;
    border-radius:20px;
    box-shadow:20px 20px 60px rgba(139,115,85,0.1);
    border-bottom:8px solid var(--accent-color);
    }}

    .insight-text{{
    font-size:var(--insight-font-size);
    color:var(--insight-text-color);
    line-height:1.6;
    font-style:italic;
    }}

    .legend{{
    position:absolute;
    right:550px;
    top:750px;
    width:300px;
    }}

    </style>
    </head>

    <body>

    <div class="header">
    <h1>{main_title}</h1>
    <div class="subtitle">{subtitle}</div>
    </div>

    <div class="chart">
    <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
    {chart_elements}
    </svg>
    </div>

    <div class="insight">
    <div class="insight-text">"{insight}"</div>
    </div>

    <div class="legend">
    {legend_items}
    </div>

    </body>
    </html>
    """

    return html_code

def generate_pie_chart_slide_7(
    main_title = "ELEGANCE CLASSY",
    subtitle = "Style Agency Infographics",
    pie1_insight = "Jupiter is the biggest planet of them all",
    pie2_insight = "Neptune is the farthest one from the sun",
    pie3_insight = "Mercury is the closest to the sun",
    chart_type = "pie",
    unit = "%",
    show_value = True,
    show_legend = True,
    data_label_format = "{value}{unit}",
    pie1_items = [
        {"label": "Jupiter", "value": 75},
        {"label": "other", "value": 25},
    ],
    pie2_items = [
        {"label": "Neptune", "value": 65},
        {"label": "other", "value": 35},
    ],
    pie3_items = [
        {"label": "Mercury", "value": 60},
        {"label": "other", "value": 40},
    ]
) -> str:
    """
    Generates a minimalist, elegant HTML slide with three pie charts.
    Inspired by the provided SVG template.
    Uses all provided parameters including unit, show_value, show_legend, and data_label_format.
    """
    
    # Color and font configuration
    colors = ["#c9b09a", "#6f7067"]
    font_family = "Outfit, sans-serif"
    accent_color = "#9a7a63"
    main_title_color = "#3a3730"
    subtitle_color = "#3a3730"
    insight_text_color = "#3a3730"
    main_title_font_size = "100px"
    subtitle_font_size = "36px"
    insight_font_size = "20px"
    legend_font_size = "24px"
    background_color = "#fefaf4"
    
    def generate_pie_svg(items, colors_list):
        total = sum(item['value'] for item in items)
        cumulative_percent = 0
        svg_slices = ""
        for i, item in enumerate(items):
            color = colors_list[i % len(colors_list)]
            percent = (item['value'] / total) * 100
            offset = 100 - cumulative_percent + 25
            svg_slices += f'<circle r="15.9" cx="21" cy="21" fill="transparent" stroke="{color}" stroke-width="10" stroke-dasharray="{percent} {100-percent}" stroke-dashoffset="{offset}" />'
            cumulative_percent += percent
        
        # Display value in center if show_value is True
        value_text = ""
        if show_value:
            main_val = items[0]['value']
            formatted_val = data_label_format.format(value=main_val, unit=unit)
            value_text = f'<text x="21" y="21" text-anchor="middle" dy=".3em" font-family="{font_family}" font-size="8" font-weight="700" fill="{main_title_color}" transform="rotate(90 21 21)">{formatted_val}</text>'
        
        donut_hole = f'<circle r="11" cx="21" cy="21" fill="{background_color}" />' if chart_type == "donut" else ""
        
        return f"""
        <svg viewBox="0 0 42 42" class="pie-svg">
            {svg_slices}
            {donut_hole}
            {value_text}
        </svg>
        """

    pie1_svg = generate_pie_svg(pie1_items, colors)
    pie2_svg = generate_pie_svg(pie2_items, colors)
    pie3_svg = generate_pie_svg(pie3_items, colors)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: {background_color};
                --text-color: {main_title_color};
                --accent-color: {accent_color};
                --secondary-accent: #b7b9ab;
                --dark-accent: #6f7067;
                --colors-0: {colors[0]};
                --colors-1: {colors[1]};
                --font-family: {font_family};
                --subtitle-color: {subtitle_color};
                --insight-text-color: {insight_text_color};
                --main-title-font-size: {main_title_font_size};
                --subtitle-font-size: {subtitle_font_size};
                --insight-font-size: {insight_font_size};
                --legend-font-size: {legend_font_size};
            }}
            body {{
                margin: 0;
                padding: 0;
                background-color: var(--bg-color);
                font-family: var(--font-family);
                color: var(--text-color);
                width: 1920px;
                height: 1080px;
                overflow: hidden;
                position: relative;
            }}
            .left-bar {{
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 70px;
                background-color: var(--accent-color);
            }}
            .top-right-box {{
                position: absolute;
                right: 0;
                top: 0;
                width: 236px;
                height: 77px;
                background-color: var(--secondary-accent);
            }}
            .bottom-right-box {{
                position: absolute;
                right: 70px;
                bottom: 0;
                width: 374px;
                height: 58px;
                background-color: var(--dark-accent);
            }}
            .container {{
                padding-left: 150px;
                padding-top: 100px;
                display: flex;
                flex-direction: column;
                height: 100%;
            }}
            .header {{
                margin-bottom: 80px;
            }}
            .main-title {{
                font-size: var(--main-title-font-size);
                font-weight: 700;
                margin: 0;
                line-height: 1.1;
                letter-spacing: -2px;
            }}
            .subtitle {{
                font-size: var(--subtitle-font-size);
                font-weight: 300;
                margin-top: 5px;
                opacity: 0.8;
                color: var(--subtitle-color);
            }}
            .charts-row {{
                display: flex;
                justify-content: space-between;
                width: 1400px;
                margin-top: 40px;
            }}
            .chart-item {{
                width: 400px;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }}
            .pie-container {{
                width: 280px;
                height: 280px;
                margin-bottom: 40px;
                position: relative;
            }}
            .pie-svg {{
                width: 100%;
                height: 100%;
                transform: rotate(-90deg);
            }}
            .chart-label {{
                font-size: var(--legend-font-size);
                font-weight: 700;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 2px;
                display: {"block" if show_legend else "none"};
            }}
            .insight-text {{
                font-size: var(--insight-font-size);
                font-weight: 400;
                line-height: 1.5;
                max-width: 350px;
                opacity: 0.9;
                color: var(--insight-text-color);
            }}
        </style>
    </head>
    <body>
        <div class="left-bar"></div>
        <div class="top-right-box"></div>
        <div class="bottom-right-box"></div>
        
        <div class="container">
            <div class="header">
                <h1 class="main-title">{main_title}</h1>
                <div class="subtitle">{subtitle}</div>
            </div>
            
            <div class="charts-row">
                <div class="chart-item">
                    <div class="pie-container">
                        {pie1_svg}
                    </div>
                    <div class="chart-label">{pie1_items[0]['label']}</div>
                    <div class="insight-text">{pie1_insight}</div>
                </div>
                
                <div class="chart-item">
                    <div class="pie-container">
                        {pie2_svg}
                    </div>
                    <div class="chart-label">{pie2_items[0]['label']}</div>
                    <div class="insight-text">{pie2_insight}</div>
                </div>
                
                <div class="chart-item">
                    <div class="pie-container">
                        {pie3_svg}
                    </div>
                    <div class="chart-label">{pie3_items[0]['label']}</div>
                    <div class="insight-text">{pie3_insight}</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def generate_pie_chart_slide_8(
        main_title = "Business Inforgraphic", 
        subtitle = "This is subtitle",     
        unit = "%",
        categories = ["North America", "Europe", "Asia"],
        insights = [
            "North America's shipment volume increased by 55% compared to last year.",
            "Europe experienced a significant growth of 76% in shipment volume.",
            "Asia had a steady increase of 43% in shipment volume.",
        ],
        series = [55, 76, 43]
    ) -> str:
    """
    Generates a generic HTML slide with a Grouped Bar Chart using the "Logistic Company" theme.
    """

    # ===== 1. COLOR AND FONT CONFIGURATION =====
    colors = ["#9CA3AF", "#85BA2A", "#5561D2"]
    font_family = "Inter, sans-serif"
    accent_color = "#FF6B35"
    main_title_color = "#1B2559"
    subtitle_color = "#6B7280"
    main_title_font_size = "64px"
    subtitle_font_size = "28px"
    insights_text_color = "#374151"
    insights_font_size = "26px"

    # ===== 2. LẤY THÔNG TIN =====
    title = main_title
    if subtitle:
        subtitle = f"<div style='font-size: {subtitle_font_size}; color: {subtitle_color}; margin-top: 10px;'>{subtitle}</div>"

    # ===== 3. RENDER ROWS (3 arcs) =====
    data_list = series
    
    arcs = []
    left_items = []
    right_items = []
    
    cx, cy = 400, 400
    base_r = 150
    stroke_w = 60
    
    for i in range(min(3, len(categories))):
        cat = categories[i]
        color = colors[i % len(colors)]
        val = data_list[i] if i < len(data_list) else 0
        desc = insights[i] if insights and i < len(insights) else ""
    
    # Calculate percentage for progress bar width
    percent = min(100, max(0, val))
    r = base_r + i * (stroke_w + 10)
    circumference = 2 * math.pi * r
    dashoffset = circumference * (1 - percent / 100)
    start_angle = 180 - (percent / 100 * 360) / 2
    
    arcs.append(f'''
        <!-- Background arc -->
        <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="none" stroke-width="{stroke_w}"/>
        <!-- Foreground arc -->
        <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke_w}" 
            stroke-dasharray="{circumference}" stroke-dashoffset="{dashoffset}" 
            transform="rotate({start_angle}, {cx}, {cy})" stroke-linecap="butt"/>
    ''')
    
    left_items.append(f'''
        <div style="background-color: #F3F4F6; border-radius: 60px 0 0 60px; padding: 30px 60px; margin-bottom: 40px; display: flex; flex-direction: column; justify-content: center; height: 160px; box-sizing: border-box; flex-grow: 1;">
        <div style="font-size: 32px; font-weight: bold; color: {color}; margin-bottom: 8px;">{cat}</div>
        <div style="font-size: {insights_font_size}; color: {insights_text_color}; line-height: 1.4;">{desc}</div>
        </div>
    ''')

    right_items.append(f'''
        <div style="background-color: #F3F4F6; border-radius: 0 60px 60px 0; padding: 30px 60px; margin-bottom: 40px; display: flex; align-items: center; height: 160px; box-sizing: border-box; gap: 40px; flex-grow: 1;">
        <div style="width: 80px; height: 80px; border-radius: 50%; background-color: {color}; display: flex; align-items: center; justify-content: center; color: white; flex-shrink: 0;">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            </svg>
        </div>
        <div style="font-size: 56px; font-weight: bold; color: {color};">
            {val}{unit}
        </div>
        </div>
    ''')

    rows_html = f'''
    <div style="display: flex; align-items: center; justify-content: center; width: 100%; position: relative;">
        <!-- Left Panel -->
        <div style="flex: 1.5; display: flex; flex-direction: column; z-index: 1; margin-right: -40px;">
        {''.join(left_items)}
        </div>
        
        <!-- Center SVG -->
        <div style="z-index: 10; display: flex; align-items: center; justify-content: center;">
        <svg width="680" height="680" viewBox="60 60 680 680">
            <!-- White background circle to hide overlapping panels -->
            <circle cx="400" cy="400" r="340" fill="white" />
            {''.join(arcs)}
        </svg>
        </div>
        
        <!-- Right Panel -->
        <div style="flex: 1.5; display: flex; flex-direction: column; z-index: 1; margin-left: -40px;">
        {''.join(right_items)}
        </div>
    </div>
    '''

    # ===== 4. HTML RENDER =====
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    html, body {{
    width: 1920px;
    height: 1080px;
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: {font_family};
    background-color: #FFFFFF;
    position: relative;
    --font-family: {font_family};
    --accent-color: {accent_color};
    --main-title-color: {main_title_color};
    --subtitle-color: {subtitle_color};
    --insights-text-color: {insights_text_color};
    --main-title-font-size: {main_title_font_size};
    --subtitle-font-size: {subtitle_font_size};
    --insights-font-size: {insights_font_size};
    --color-0: {colors[0]};
    --color-1: {colors[1]};
    --color-2: {colors[2]};
    }}
    
    /* Decorative Background Elements based on reference */
    .bg-shape-top {{
    position: absolute;
    top: -30px;
    left: 0;
    width: 400px;
    height: 150px;
    background: var(--main-title-color);
    clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
    z-index: 0;
    }}
    .bg-shape-accent {{
    position: absolute;
    top: 0;
    left: 0;
    width: 150px;
    height: 150px;
    background: var(--accent-color);
    clip-path: polygon(0 0, 80% 0, 0 80%);
    z-index: 1;
    }}
    .bg-shape-bottom {{
    position: absolute;
    bottom: -50px;
    right: -300px;
    width: 600px;
    height: 120px;
    background: var(--main-title-color);
    clip-path: polygon(10% 0, 100% 0, 100% 100%, 0% 100%);
    z-index: 0;
    }}
    
    .container {{
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 60px 80px 40px 80px;
    box-sizing: border-box;
    }}
    
    .header {{
    margin-bottom: 40px;
    padding-left: 20px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    }}
    
    .title-group h1 {{
    font-size: var(--main-title-font-size);
    color: var(--accent-color);
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 1px;
    }}
    
    .title-group h1 span {{
    color: var(--main-title-color);
    }}
    
    .subtitle {{
    font-size: var(--subtitle-font-size);
    color: var(--subtitle-color);
    margin-top: 10px;
    font-weight: 400;
    }}

    .main-content {{
    display: flex;
    flex: 1;
    gap: 40px;
    align-items: center;
    justify-content: space-between;
    }}
    
    .left-panel {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    }}
    
    .center-panel {{
    flex: 2;
    background: #FFFFFF;
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    }}

    .right-panel {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    }}
    
    .footer-mark {{
    position: absolute;
    bottom: 30px;
    right: 10px;
    color: white;
    font-size: 20px;
    font-weight: bold;
    z-index: 10;
    }}

    </style>
    </head>
    <body>

    <div class="bg-shape-top"></div>
    <div class="bg-shape-accent"></div>
    <div class="bg-shape-bottom"></div>
    <div class="footer-mark">www.reallygreatsite.com</div>

    <div class="container">
    <div class="header" style="justify-content: center; margin-bottom: 60px;">
        <div class="title-group" style="text-align: center;">
        <h1 style="color: #000000; font-size: 64px; text-transform: none;">{title}</h1>
        {f'<div class="subtitle">{subtitle}</div>' if subtitle else ""}
        </div>

    </div>

    <div class="main-content" style="flex-direction: column; align-items: stretch; justify-content: center; padding: 0 40px; box-sizing: border-box; max-width: 1600px; margin: 0 auto; width: 100%;">
        {rows_html}
    </div>
    </div>

    </body>
    </html>
    """
    return html_code
