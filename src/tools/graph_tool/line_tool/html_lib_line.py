def generate_line_chart_slide_1(
    main_title: str = "Accelerating Growth of Renewable Energy Capacity",
    subtitle: str = "Global Renewable Energy Report – 2019 to 2024",
    insight: str = (
        "Both solar and wind energy capacity show steady growth from 2019 to 2021, "
        "followed by a noticeable acceleration after 2022."
    ),
    x_axis = "Year",
    y_axis = "Installed Capacity",
    unit = " GW",
    show_value = False,
    show_legend = True,
    y_axis_min = 50,
    y_axis_max = 260,
    colors= ["#FF8C00", "#4A90E2"],
    time_points = ["2019", "2020", "2021", "2022", "2023", "2024"],
    series = [
        {
            "name": "Solar Energy",
            "values": [80, 95, 110, 150, 200, 250]
        },
        {
            "name": "Wind Energy",
            "values": [70, 85, 100, 120, 150, 180]
        }
    ],
) -> str:
    """Tạo slide biểu đồ đường với phong cách 'Playful Stamp' vui nhộn, 
    phù hợp cho các báo cáo giáo dục, trò chơi hoặc kết quả thi đấu.
    """
    main_title_color = "#333333"
    subtitle_color = "#666666"
    insight_text_color = "#444444"
    main_title_font_size = "65px"
    subtitle_font_size = "30px"
    insight_font_size = "28px"

    # ===== 2. SVG CONFIG =====
    svg_w, svg_h = 1100, 600
    margin_top, margin_bottom = 60, 80
    margin_left, margin_right = 100, 60
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    # ===== 3. TÍNH MIN MAX =====
    all_values = [v for s in series for v in s.get("values", [])]
    if y_axis_min is None:
        y_axis_min = min(all_values) if all_values else 0
        
    if y_axis_max is None:
        y_axis_max = max(all_values) if all_values else 100

    if y_axis_max == y_axis_min:
        y_axis_max += 10

    # ===== 4. VẼ CHART (SVG ELEMENTS) =====
    chart_elements = ""

    # Grid Y & Labels
    steps = 5
    for i in range(steps + 1):
        y_pos = margin_top + (chart_h / steps) * i
        val = y_axis_max - (y_axis_max - y_axis_min) / steps * i
        chart_elements += f'''
        <line x1="{margin_left}" y1="{y_pos}" x2="{svg_w - margin_right}" y2="{y_pos}" 
              stroke="#DDDDDD" stroke-dasharray="5,5" stroke-width="1"/>
        <text x="{margin_left - 15}" y="{y_pos + 6}" font-size="18" text-anchor="end" 
              fill="{subtitle_color}" font-weight="bold">{int(val)}</text>
        '''

    # X-axis Labels
    if time_points:
        num_points = len(time_points)
        for i, label in enumerate(time_points):
            x_pos = margin_left + (i / max(num_points - 1, 1)) * chart_w
            chart_elements += f'''
            <text x="{x_pos}" y="{svg_h - margin_bottom + 40}" font-size="18" 
                  text-anchor="middle" fill="{subtitle_color}" font-weight="bold">{label}</text>
            <line x1="{x_pos}" y1="{svg_h - margin_bottom}" x2="{x_pos}" y2="{svg_h - margin_bottom + 10}" 
                  stroke="#333" stroke-width="2"/>
            '''

    # Trục tọa độ
    chart_elements += f'''
    <line x1="{margin_left}" y1="{svg_h-margin_bottom}" x2="{svg_w-margin_right}" y2="{svg_h-margin_bottom}" stroke="#333" stroke-width="3"/>
    <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{svg_h-margin_bottom}" stroke="#333" stroke-width="3"/>
    '''

    # Vẽ đường (Lines)
    for idx, s in enumerate(series):
        color = colors[idx % len(colors)]
        values = s.get("values", [])
        if not values or not time_points: continue
        
        points = []
        for i, val in enumerate(values):
            x = margin_left + (i / max(len(time_points) - 1, 1)) * chart_w
            y = svg_h - margin_bottom - (val - y_axis_min) / (y_axis_max - y_axis_min) * chart_h
            points.append(f"{x},{y}")
            
        # Line Path
        chart_elements += f'''
        <polyline points="{' '.join(points)}" fill="none" stroke="{color}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        '''
        
        # Points and Labels
        for i, val in enumerate(values):
            x = margin_left + (i / max(len(time_points) - 1, 1)) * chart_w
            y = svg_h - margin_bottom - (val - y_axis_min) / (y_axis_max - y_axis_min) * chart_h
            chart_elements += f'''
            <circle cx="{x}" cy="{y}" r="8" fill="white" stroke="{color}" stroke-width="4"/>
            '''
            if show_value:
                chart_elements += f'''
                <text x="{x}" y="{y-20}" font-size="18" text-anchor="middle" fill="{color}" font-weight="bold">{val}{unit}</text>
                '''

    # Axis Title
    chart_elements += f'''
    <text x="{svg_w/2 + margin_left/2}" y="{svg_h - 10}" font-size="20" text-anchor="middle" fill="{main_title_color}" font-weight="bold">{x_axis}</text>
    <text transform="rotate(-90)" x="{-svg_h/2}" y="30" font-size="20" text-anchor="middle" fill="{main_title_color}" font-weight="bold">{y_axis}</text>
    '''

    # ===== LEGEND & INSIGHT HTML =====
    legend_html = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_html += f'''
            <div style="display:flex; align-items:center; margin-bottom:15px; background:white; padding:10px 20px; border-radius:15px; border:3px solid {color};">
                <div style="width:20px; height:20px; background:{color}; border-radius:50%; margin-right:15px;"></div>
                <span style="font-size:22px; font-weight:bold; color:#333;">{s.get("name","")}</span>
            </div>'''

    # ===== 5. RENDER FINAL HTML =====
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Chalkboard+SE&family=Inter:weight@700&display=swap');
            body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0;
                background-color: #8ED645; /* Green background from image */
                font-family: 'Inter', sans-serif;
                overflow: hidden;
                display: flex; flex-direction: column;
            }}
            .stamp-container {{
                position: absolute; top: 50px; left: 50px;
                width: 1820px; height: 980px;
                background: white;
                border-radius: 20px;
                box-shadow: 20px 20px 0px rgba(0,0,0,0.1);
                /* Stamp perforated effect */
                background-image: radial-gradient(circle at 0 50%, transparent 20px, white 21px),
                                  radial-gradient(circle at 100% 50%, transparent 20px, white 21px),
                                  radial-gradient(circle at 50% 0, transparent 20px, white 21px),
                                  radial-gradient(circle at 50% 100%, transparent 20px, white 21px);
                background-size: 100% 100px, 100% 100px, 100px 100%, 100px 100%;
                background-repeat: repeat-y, repeat-y, repeat-x, repeat-x;
            }}
            .header-box {{
                position: absolute; top: 100px; left: 150px; width: 1620px;
            }}
            .title {{
                font-size: {main_title_font_size}; color: {main_title_color}; margin: 0;
                text-transform: uppercase; letter-spacing: 2px;
            }}
            .subtitle {{
                font-size: {subtitle_font_size}; color: {subtitle_color}; margin-top: 10px; font-weight: normal;
            }}
            .left-section {{
                position: absolute; top: 300px; left: 150px; width: 450px;
            }}
            .insight-card {{
                background: #F9F9F9; border: 4px dashed #CCC; border-radius: 20px;
                padding: 30px; margin-bottom: 40px; font-size: {insight_font_size};
                color: {insight_text_color}; line-height: 1.5;
            }}
            .chart-container {{
                position: absolute; top: 300px; left: 650px;
                width: 1150px; height: 650px;
                background: #FFFFFF; border: 5px solid #333; border-radius: 30px;
                padding: 20px;
            }}
            .decoration-arrow {{
                position: absolute; bottom: 50px; left: 50px; width: 150px; z-index: 10;
            }}
        </style>
    </head>
    <body>
        <div class="stamp-container"></div>
        
        <div class="header-box">
            <h1 class="title">{main_title}</h1>
            <div class="subtitle">{subtitle}</div>
        </div>

        <div class="left-section">
            <div class="insight-card">
                {insight}
            </div>
            <div class="legend-area">
                {legend_html}
            </div>
        </div>

        <div class="chart-container">
            <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                {chart_elements}
            </svg>
        </div>
    </body>
    </html>
    """
    return html_code

def generate_line_chart_slide_2(
    main_title = "Model Accuracy Converges with Minor Overfitting",
    subtitle = "ResNet-18 trained on CIFAR-10 Dataset (30 Epochs)", 
    insight = (
        "Training and validation accuracy both increase steadily during the first 15 epochs, "
        "indicating effective learning and rapid convergence. After epoch 20, training accuracy "
        "continues to improve while validation accuracy plateaus, suggesting mild overfitting. "
        "The gap remains controlled, implying overall stable generalization performance."
    ),
    x_axis = "Epoch",
    y_axis = "Accuracy",
    unit = "%",
    show_value = False,
    y_axis_min = 40,
    y_axis_max = 100,
    data_label_format = None,
    colors = ["#4F46E5", "#22C55E"],
    time_points = [
        "Epoch 1", "Epoch 5", "Epoch 10",
        "Epoch 15", "Epoch 20", "Epoch 25", "Epoch 30"
    ],
    series = [
        {
            "name": "Training Accuracy",
            "values": [45, 62, 75, 84, 90, 94, 97]
        },
        {
            "name": "Validation Accuracy",
            "values": [43, 60, 73, 82, 87, 88, 88]
        }
    ],

) -> str:
    """
    Generate a premium line chart HTML slide using the Global Economy theme.
    Refactored to accept explicit parameters instead of a raw dictionary.
    """

    # ===== 1. DATA EXTRACTION =====
    font_family: str = "Inter, sans-serif"
    main_title_color: str = "#1F2937"
    subtitle_color: str = "#4B5563"
    insight_text_color: str = "#374151"
    main_title_font_size: str = "64px"
    subtitle_font_size: str = "30px"
    insight_font_size: str = "32px"
    title = main_title
    subtitle = subtitle or ""
    insight = insight or ""
    time_points = time_points
    series = series
 
    # ===== 2. CHART CONFIG =====
    svg_w, svg_h = 1000, 500
    # Tăng margin right lên 180 để có không gian cho nhãn
    margin = {"top": 60, "bottom": 100, "left": 80, "right": 180}
    chart_w = svg_w - margin["left"] - margin["right"]
    chart_h = svg_h - margin["top"] - margin["bottom"]

    all_vals = [v for s in series for v in s.get("values", [])]
    y_max = y_axis_max if y_axis_max else (max(all_vals) * 1.2 if all_vals else 100)
    y_min = y_axis_min

    def get_x(i):
        return (
            margin["left"] + (i * chart_w / (len(time_points) - 1))
            if len(time_points) > 1
            else margin["left"] + chart_w / 2
        )

    def get_y(v):
        return svg_h - margin["bottom"] - ((v - y_min) / (y_max - y_min) * chart_h)

    # ===== 3. SVG DRAWING =====
    chart_elements = ""

    # Y-axis labels
    for i in range(5):
        y_val = svg_h - margin["bottom"] - (i * chart_h / 4)
        value = y_min + (i * (y_max - y_min) / 4)
        chart_elements += (
            f'<text x="{margin["left"] - 15}" y="{y_val + 5}" '
            f'font-size="16" text-anchor="end" fill="#64748b">{value:.0f}{unit}</text>'
        )

    # Horizontal grid lines
    for i in range(5):
        y_val = svg_h - margin["bottom"] - (i * chart_h / 4)
        chart_elements += (
            f'<line x1="{margin["left"]}" y1="{y_val}" '
            f'x2="{svg_w - margin["right"]}" y2="{y_val}" '
            f'stroke="#e2e8f0" stroke-width="1" />'
        )

    # Lines + areas
    for idx, s in enumerate(series):
        color = colors[idx % len(colors)]
        values = s.get("values", [])
        name = s.get("name", f"Series {idx + 1}")

        if not values:
            continue

        d_path = f"M {get_x(0)} {get_y(values[0])}"
        d_area = f"M {get_x(0)} {svg_h - margin['bottom']} L {get_x(0)} {get_y(values[0])}"

        for i in range(1, len(values)):
            d_path += f" L {get_x(i)} {get_y(values[i])}"
            d_area += f" L {get_x(i)} {get_y(values[i])}"

        d_area += f" L {get_x(len(values) - 1)} {svg_h - margin['bottom']} Z"

        chart_elements += f'<path d="{d_area}" fill="{color}" fill-opacity="0.1" />'
        chart_elements += (
            f'<path d="{d_path}" fill="none" stroke="{color}" '
            f'stroke-width="6" stroke-linecap="round" stroke-linejoin="round" />'
        )

        for i, v in enumerate(values):
            chart_elements += (
                f'<circle cx="{get_x(i)}" cy="{get_y(v)}" r="8" '
                f'fill="white" stroke="{color}" stroke-width="4" />'
            )
            if show_value:
                value_text = f"{v}{unit}" if unit else str(v)
                if data_label_format == "percentage":
                    value_text = f"{v}%"
                chart_elements += (
                    f'<text x="{get_x(i)}" y="{get_y(v) - 25}" '
                    f'font-size="18" text-anchor="middle" '
                    f'fill="#1e293b" font-weight="bold">{value_text}</text>'
                )

    # X-axis tick labels (Epoch 1 to Epoch 30)
    for i, label in enumerate(time_points):
        chart_elements += (
            f'<text x="{get_x(i)}" y="{svg_h - margin["bottom"] + 25}" '
            f'font-size="18" text-anchor="middle" fill="#64748b">{label}</text>'
        )
    
    # X-axis title (Epoch)
    if x_axis:
        chart_elements += (
            f'<text x="{margin["left"] + chart_w/2}" y="{svg_h - margin["bottom"] + 65}" '
            f'font-size="20" text-anchor="middle" fill="#475569" font-weight="600">{x_axis}</text>'
        )
    
    # Y-axis title
    if y_axis:
        chart_elements += (
            f'<text x="20" y="{margin["top"] + chart_h/2}" '
            f'font-size="18" text-anchor="middle" fill="#475569" font-weight="600" '
            f'transform="rotate(-90, 20, {margin["top"] + chart_h/2})">{y_axis}</text>'
        )
    
    # ===== DIRECT LABELS AT THE END OF LINES =====
    # Lấy giá trị cuối cùng của mỗi series
    last_index = len(time_points) - 1
    last_x = get_x(last_index)
    
    # Thu thập thông tin nhãn cho điểm cuối cùng
    label_info = []
    for idx, s in enumerate(series):
        values = s.get("values", [])
        if values:
            last_value = values[-1]
            last_y = get_y(last_value)
            name = s.get("name", f"Series {idx + 1}")
            color = colors[idx % len(colors)]
            label_info.append({
                "name": name,
                "y": last_y,
                "color": color,
                "value": last_value,
                "idx": idx
            })
    
    # Sắp xếp theo giá trị Y (từ trên xuống dưới)
    label_info.sort(key=lambda x: x["y"])
    
    # Kiểm tra và xử lý chồng lấp
    min_distance = 25  # Khoảng cách tối thiểu giữa các nhãn (px)
    for i in range(len(label_info) - 1):
        if label_info[i + 1]["y"] - label_info[i]["y"] < min_distance:
            # Nếu quá gần, đẩy nhãn trên lên và nhãn dưới xuống
            overlap = min_distance - (label_info[i + 1]["y"] - label_info[i]["y"])
            offset = overlap / 2
            label_info[i]["y_offset"] = -offset
            label_info[i + 1]["y_offset"] = offset
    
    # Thêm nhãn direct labeling
    for info in label_info:
        y_position = info["y"]
        # Áp dụng offset nếu có
        if "y_offset" in info:
            y_position += info["y_offset"]
        
        # Thêm nhãn với màu sắc tương ứng
        chart_elements += (
            f'<text x="{last_x + 15}" y="{y_position + 6}" '
            f'font-size="18" font-weight="600" text-anchor="start" '
            f'fill="{info["color"]}" '
            f'alignment-baseline="middle">{info["name"]}</text>'
        )

    # ===== 4. HTML OUTPUT =====
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            html, body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0;
                font-family: {font_family};
                background-color: white; overflow: hidden;
            }}
            
            /* Decorative Elements */
            .left-shape {{
                position: absolute;
                width: 1200px;
                height: 1200px;
                background-color: #f1fcf4;
                border-radius: 50%;
                left: -450px;
                top: -100px;
                z-index: 0;
            }}
            .dot-grid {{
                position: absolute;
                top: 80px;
                right: 100px;
                display: grid;
                grid-template-columns: repeat(10, 15px);
                gap: 15px;
                z-index: 1;
            }}
            .dot {{
                width: 8px;
                height: 8px;
                background-color: #fbbf24;
                border-radius: 50%;
            }}
            
            /* Header */
            .header {{
                margin-bottom: 40px;
                padding: 80px 100px 0 100px;
                position: relative;
                z-index: 2;
            }}
            h1 {{
                font-size: {main_title_font_size};
                font-weight: 800;
                color: {main_title_color};
                margin: 0;
            }}
            .subtitle {{
                font-size: {subtitle_font_size};
                color: {subtitle_color};
                margin-top: 15px;
            }}
            
            /* Main Content Flex */
            .main-flex {{
                display: flex;
                height: calc(100vh - 300px);
                gap: 60px;
                padding: 0 100px 80px 100px;
                position: relative;
                z-index: 2;
            }}
            .left-panel {{
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }}
            .right-panel {{
                flex: 1.5;
                background: transparent;
                border-radius: 40px;
                padding: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .insight {{
                font-size: {insight_font_size};
                color: {insight_text_color};
                line-height: 1.7;
                background: transparent;
                padding: 35px 40px;
                border-radius: 16px;
            }}
        </style>
    </head>
    <body>
        <!-- Decorative Background Elements -->
        <div class="left-shape"></div>
        <div class="dot-grid">
            {''.join('<div class="dot"></div>' for _ in range(30))}
        </div>
        
        <!-- Header -->
        <div class="header">
            <h1>{title}</h1>
            <p class="subtitle">{subtitle}</p>
        </div>
        
        <!-- Main Content -->
        <div class="main-flex">
            <div class="left-panel">
                <div class="insight">{insight}</div>
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


def generate_line_chart_slide_3(
    main_title = "EV Market Leaders Expand the Gap", 
    subtitle = "Southeast Asia EV Sales – Jan to Dec 2026", 
    insight = (
        "Tesla and BYD maintain strong upward momentum throughout the year, "
        "with Tesla accelerating sharply in Q3 following new model releases. "
    ), 
    x_axis = "Month",
    y_axis = "Units Sold",
    unit = "K",
    show_value = True,
    show_legend = True,
    y_axis_min = 20,
    y_axis_max = 140,
    data_label_format = "{value}K",
    colors = ["#00F2FF", "#8B5CF6", "#EC4899"],
    time_points = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ],
    series = [
        {
            "name": "Tesla",
            "values": [45, 50, 55, 60, 68, 75, 90, 105, 115, 120, 125, 130]
        },
        {
            "name": "BYD",
            "values": [40, 48, 52, 58, 63, 70, 85, 95, 105, 110, 118, 122]
        },
        {
            "name": "VinFast",
            "values": [30, 35, 40, 44, 50, 55, 60, 66, 70, 72, 74, 76]
        }
    ],

) -> str:
    # ===== 1. LẤY THÔNG TIN =====
    font_family: str = "Inter, sans-serif"
    accent_color: str = "#00F2FF"
    main_title_color: str = "#FFFFFF"
    subtitle_color: str = "#94A3B8"
    insight_text_color: str = "#E2E8F0"
    main_title_font_size: str = "64px"
    subtitle_font_size: str = "28px"
    insight_font_size: str = "30px"   
    
    # ===== 2. SVG CONFIG =====
    svg_w, svg_h = 1100, 600
    margin_top, margin_bottom = 60, 80
    margin_left, margin_right = 100, 40
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    # ===== 3. TÍNH MIN MAX =====
    all_values = [v for s in series for v in s.get("values", [])]
    y_min = y_axis_min or (min(all_values) * 0.9 if all_values else 0)
    y_max = y_axis_max or (max(all_values) * 1.1 if all_values else 100)
    if y_max == y_min: 
        y_max += 1

    # ===== 4. VẼ CHART ELEMENTS =====
    chart_elements = ""
    
    # Grid lines Y & Labels (with optional unit suffix)
    steps = 5
    for i in range(steps + 1):
        y_pos = margin_top + (chart_h / steps) * i
        val = y_max - (y_max - y_min) / steps * i
        # format y-axis tick label with unit if provided
        if unit:
            y_tick_label = f"{val:,.0f}{unit}"
        else:
            y_tick_label = f"{val:,.0f}"
        chart_elements += f'''
        <line x1="{margin_left}" y1="{y_pos}" x2="{svg_w - margin_right}" y2="{y_pos}" 
              stroke="#ffffff15" stroke-width="1" stroke-dasharray="5,5"/>
        <text x="{margin_left - 15}" y="{y_pos + 6}" font-size="16" text-anchor="end" 
              fill="{subtitle_color}">{y_tick_label}</text>
        '''

    # X-axis Labels
    num_points = len(time_points)
    for i, label in enumerate(time_points):
        x_pos = margin_left + (i / max(num_points - 1, 1)) * chart_w
        chart_elements += f'''
        <text x="{x_pos}" y="{svg_h - margin_bottom + 35}" font-size="16" 
              text-anchor="middle" fill="{subtitle_color}">{label}</text>
        <line x1="{x_pos}" y1="{svg_h - margin_bottom}" x2="{x_pos}" y2="{svg_h - margin_bottom + 8}" 
              stroke="{accent_color}" stroke-width="2"/>
        '''

    # Draw Lines, Points & Data Labels
    for idx, s in enumerate(series):
        color = colors[idx % len(colors)]
        values = s.get("values", [])
        if not values: continue
        
        path_points = []
        for i, val in enumerate(values):
            x = margin_left + (i / max(len(time_points) - 1, 1)) * chart_w
            y = svg_h - margin_bottom - (val - y_min) / (y_max - y_min) * chart_h
            path_points.append(f"{x},{y}")
        
        # Line Path with Glow Effect
        points_str = " ".join(path_points)
        chart_elements += f'''
        <polyline points="{points_str}" fill="none" stroke="{color}" stroke-width="4" 
                  stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 8px {color}66);"/>
        '''
        
        # Points
        for p in path_points:
            px, py = p.split(',')
            chart_elements += f'<circle cx="{px}" cy="{py}" r="6" fill="#0F172A" stroke="{color}" stroke-width="3"/>'
        
        # Data Labels (if show_value is True)
        if show_value:
            for i, val in enumerate(values):
                x = margin_left + (i / max(len(time_points) - 1, 1)) * chart_w
                y = svg_h - margin_bottom - (val - y_min) / (y_max - y_min) * chart_h
                label_text = data_label_format.format(value=val)
                chart_elements += f'''
                <text x="{x}" y="{y - 14}" font-size="12" font-weight="bold" 
                      text-anchor="middle" fill="{color}" stroke="#0F172A" stroke-width="1.5" 
                      paint-order="stroke">{label_text}</text>
                '''

    # ===== 5. LAYOUT COMPONENTS =====
    legend_html = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_html += f'''
            <div style="display:flex;align-items:center;margin-bottom:12px;background:rgba(255,255,255,0.05);padding:10px 20px;border-radius:10px;border-left:4px solid {color};">
                <span style="font-size:20px;color:#FFFFFF;font-weight:500;">{s.get("name","Series")}</span>
            </div>
            '''

    # Build axis titles with unit if provided
    y_axis_title = f"{y_axis} ({unit})" if unit else y_axis

    # ===== 6. FINAL HTML =====
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
            body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0;
                background-color: #020617; color: white;
                font-family: {font_family}; overflow: hidden;
                background-image: 
                    radial-gradient(circle at 20% 20%, #1e1b4b 0%, transparent 40%),
                    radial-gradient(circle at 80% 80%, #312e81 0%, transparent 40%),
                    linear-gradient(#0f172a 1px, transparent 1px),
                    linear-gradient(90deg, #0f172a 1px, transparent 1px);
                background-size: 100% 100%, 100% 100%, 60px 60px, 60px 60px;
            }}
            .header-container {{
                padding: 80px 100px 40px 100px;
                background: linear-gradient(to bottom, rgba(15,23,42,0.8), transparent);
            }}
            .main-title {{
                font-family: 'Orbitron', sans-serif;
                font-size: {main_title_font_size};
                color: {main_title_color};
                text-transform: uppercase; letter-spacing: 4px; margin: 0;
            }}
            .main-title span {{ color: {accent_color}; }}
            .subtitle {{
                font-size: {subtitle_font_size};
                color: {subtitle_color}; margin-top: 15px;
            }}
            .content-grid {{
                display: flex; padding: 0 100px; gap: 60px; height: 700px;
            }}
            .chart-area {{
                flex: 2; background: transparent;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px; padding: 20px;
                backdrop-filter: blur(5px);
                display: flex; align-items: center; justify-content: center;
            }}
            .insight-area {{
                flex: 1; display: flex; flex-direction: column; justify-content: flex-start;
            }}
            .insight-box {{
                background: transparent;
                border-radius: 20px; padding: 35px; margin-bottom: 30px;
                font-size: {insight_font_size}; color: {insight_text_color}; line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <div class="header-container">
            <h1 class="main-title">{main_title.split(' ')[0]} <span>{' '.join(main_title.split(' ')[1:])}</span></h1>
            <div class="subtitle">{subtitle}</div>
        </div>
        <div class="content-grid">
            <div class="chart-area">
                <div>
                    <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                        {chart_elements}
                        <text x="{svg_w/2}" y="{svg_h-10}" font-size="20" text-anchor="middle" fill="{accent_color}" font-weight="bold">{x_axis}</text>
                        <text transform="rotate(-90)" x="{-svg_h/2}" y="30" font-size="20" text-anchor="middle" fill="{accent_color}" font-weight="bold">{y_axis_title}</text>
                    </svg>
                </div>
            </div>
            <div class="insight-area">
                <div class="insight-box">{insight}</div>
                <div>{legend_html}</div>
            </div>
        </div>
    </body>
    </html>
    """

def generate_line_chart_slide_4(
    main_title = "Accelerating Growth of Renewable Energy Capacity",
    subtitle = "Global Renewable Energy Report – 2019 to 2024",
    x_axis_label = "Year",
    y_axis_label = "Installed Capacity",
    unit = " GW",
    show_value = False,
    show_legend = True,
    y_axis_min = 50,
    y_axis_max = 260,
    data_label_format = None,
    colors = ["#FF8C00", "#4A90E2"],
    time_points = ["2019", "2020", "2021", "2022", "2023", "2024"],
    series = [
        {
            "name": "Solar Energy",
            "values": [80, 95, 110, 150, 200, 250]
        },
        {
            "name": "Wind Energy",
            "values": [70, 85, 100, 120, 150, 180]
        }
    ],
) -> str:
    """
    Tạo slide biểu đồ đường với phong cách 'Playful Stamp' vui nhộn,
    phù hợp cho các báo cáo giáo dục, trò chơi hoặc kết quả thi đấu.
    """
    font_family = "Arial, sans-serif"  # FIXED: removed trailing comma
    accent_color = "#FF8C00"
    main_title_color = "#E2E2E2"
    subtitle_color = "#CFCACA"
    main_title_font_size = "65px"
    subtitle_font_size = "30px"
    
    # ===== ENERGY BACKGROUND IMAGE URL =====
    background_image_url = "https://images.pexels.com/photos/414837/pexels-photo-414837.jpeg?auto=compress&cs=tinysrgb&w=1920&h=1080&fit=crop"
    # Alternative: wind turbines + solar field - free to use (Pexels license)
    
    # ===== 2. SVG CONFIG =====
    svg_w, svg_h = 1100, 600
    margin_top, margin_bottom = 60, 80
    margin_left, margin_right = 100, 60
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    # ===== 3. TÍNH MIN MAX =====
    all_values = [v for s in series for v in s.get("values", [])]
    y_min = y_axis_min
    if y_min is None:
        y_min = min(all_values) if all_values else 0
        
    y_max = y_axis_max
    if y_max is None:
        y_max = max(all_values) if all_values else 100

    if y_max == y_min:
        y_max += 10

    # ===== 4. VẼ CHART (SVG ELEMENTS) =====
    chart_elements = ""

    # Grid Y & Labels
    steps = 5
    for i in range(steps + 1):
        y_pos = margin_top + (chart_h / steps) * i
        val = y_max - (y_max - y_min) / steps * i
        chart_elements += f'''
        <line x1="{margin_left}" y1="{y_pos}" x2="{svg_w - margin_right}" y2="{y_pos}" 
              stroke="#DDDDDD" stroke-dasharray="5,5" stroke-width="1"/>
        <text x="{margin_left - 15}" y="{y_pos + 6}" font-size="18" text-anchor="end" 
              fill="{subtitle_color}" font-weight="bold">{int(val)}</text>
        '''

    # X-axis Labels
    if time_points:
        num_points = len(time_points)
        for i, label in enumerate(time_points):
            x_pos = margin_left + (i / max(num_points - 1, 1)) * chart_w
            chart_elements += f'''
            <text x="{x_pos}" y="{svg_h - margin_bottom + 40}" font-size="18" 
                  text-anchor="middle" fill="{subtitle_color}" font-weight="bold">{label}</text>
            <line x1="{x_pos}" y1="{svg_h - margin_bottom}" x2="{x_pos}" y2="{svg_h - margin_bottom + 10}" 
                  stroke="#333" stroke-width="2"/>
            '''

    # Trục tọa độ
    chart_elements += f'''
    <line x1="{margin_left}" y1="{svg_h-margin_bottom}" x2="{svg_w-margin_right}" y2="{svg_h-margin_bottom}" stroke="#333" stroke-width="3"/>
    <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{svg_h-margin_bottom}" stroke="#333" stroke-width="3"/>
    '''

    # Vẽ đường (Lines)
    for idx, s in enumerate(series):
        color = colors[idx % len(colors)]
        values = s.get("values", [])
        if not values or not time_points: continue
        
        points = []
        for i, val in enumerate(values):
            x = margin_left + (i / max(len(time_points) - 1, 1)) * chart_w
            y = svg_h - margin_bottom - (val - y_min) / (y_max - y_min) * chart_h
            points.append(f"{x},{y}")
            
        # Line Path
        chart_elements += f'''
        <polyline points="{' '.join(points)}" fill="none" stroke="{color}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
        '''
        
        # Points and Labels
        for i, val in enumerate(values):
            x = margin_left + (i / max(len(time_points) - 1, 1)) * chart_w
            y = svg_h - margin_bottom - (val - y_min) / (y_max - y_min) * chart_h
            chart_elements += f'''
            <circle cx="{x}" cy="{y}" r="8" fill="white" stroke="{color}" stroke-width="4"/>
            '''
            if show_value:
                label_text = format(val, data_label_format) if data_label_format else str(val)
                chart_elements += f'''
                <text x="{x}" y="{y-20}" font-size="18" text-anchor="middle" fill="{color}" font-weight="bold">{label_text}{unit}</text>
                '''

    # Axis Title
    chart_elements += f'''
    <text x="{svg_w/2 + margin_left/2}" y="{svg_h - 10}" font-size="20" text-anchor="middle" fill="{main_title_color}" font-weight="bold">{x_axis_label}</text>
    <text transform="rotate(-90)" x="{-svg_h/2}" y="30" font-size="20" text-anchor="middle" fill="{main_title_color}" font-weight="bold">{y_axis_label}</text>
    '''

    # ===== LEGEND & INSIGHT HTML =====
    legend_html = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_html += f'''
            <div style="display:flex; align-items:center; margin-bottom:15px; background:white; padding:10px 20px; border-radius:15px; border:3px solid {color};">
                <div style="width:20px; height:20px; background:{color}; border-radius:50%; margin-right:15px;"></div>
                <span style="font-size:22px; font-weight:bold; color:#333;">{s.get("name","")}</span>
            </div>'''

    # ===== 5. RENDER FINAL HTML =====
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Chalkboard+SE&family=Inter:weight@700&display=swap');
            body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0;
                background-color: {accent_color};
                font-family: {font_family};
                overflow: hidden;
                display: flex; flex-direction: column;
                background-image: url('{background_image_url}');
                background-size: cover;
                background-position: center;
                position: relative;
            }}
            /* Dark overlay to improve text contrast on the image */
            body::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.45);
                z-index: 0;
            }}
            .stamp-container {{
                position: absolute; top: 50px; left: 50px;
                width: 1820px; height: 980px;
                background: transparent;
                border-radius: 20px;
     
            }}
            .header-box {{
                position: absolute; top: 65px; left: 150px; width: 1620px;
                z-index: 2;
            }}
            .title {{
                font-size: {main_title_font_size}; color: {main_title_color}; margin: 0;
                text-transform: uppercase; letter-spacing: 2px;
            }}
            .subtitle {{
                font-size: {subtitle_font_size}; color: {subtitle_color}; margin-top: 10px; font-weight: normal;
            }}
            .left-section {{
                position: absolute; top: 300px; left: 150px; width: 450px;
                z-index: 2;
            }}
            .chart-container {{
                position: absolute; top: 280px; left: 650px;
                width: 1150px; height: 650px;
                background: transparent; 
                padding: 20px;
                z-index: 2;
                border: 0.5px solid rgba(255, 255, 255, 0.8);
                border-radius: 15px;
                backdrop-filter: blur(12px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }}
            .decoration-arrow {{
                position: absolute; bottom: 50px; left: 50px; width: 150px; z-index: 2;
            }}
        </style>
    </head>
    <body>
        <div class="stamp-container"></div>
        
        <div class="header-box">
            <h1 class="title">{main_title}</h1>
            <div class="subtitle">{subtitle}</div>
        </div>

        <div class="left-section">
            <div class="legend-area">
                {legend_html}
            </div>
            <!-- Factory SVG Decoration -->
            <div style="margin-top: 60px; text-align: center;">
                <svg width="300" height="200" viewBox="0 0 300 200" style="opacity: 0.9;">
                    <!-- Factory Buildings -->
                    <path d="M20,200 L20,120 L60,80 L100,120 L100,60 L150,20 L200,60 L200,100 L240,60 L280,100 L280,200 Z" fill="#4A90E2"/>
                    <path d="M20,200 L20,120 L60,80 L100,120 L100,200 Z" fill="#357AB2"/>
                    <path d="M200,200 L200,100 L240,60 L280,100 L280,200 Z" fill="#357AB2"/>
                    
                    <!-- Chimneys -->
                    <rect x="120" y="20" width="20" height="50" fill="#357AB2"/>
                    <rect x="60" y="50" width="15" height="50" fill="#255A92"/>
                    
                    <!-- Windows -->
                    <rect x="45" y="140" width="15" height="20" fill="#FFD700" rx="3"/>
                    <rect x="120" y="100" width="15" height="20" fill="#FFD700" rx="3"/>
                    <rect x="165" y="100" width="15" height="20" fill="#FFD700" rx="3"/>
                    <rect x="120" y="150" width="15" height="20" fill="#FFD700" rx="3"/>
                    <rect x="165" y="150" width="15" height="20" fill="#FFD700" rx="3"/>
                    <rect x="235" y="130" width="15" height="20" fill="#FFD700" rx="3"/>
                    
                    <!-- Eco 'Smoke' Leaves -->
                    <path d="M125,-5 C110,-15 100,0 125,-5 C140,0 130,-15 125,-5 Z" fill="#8ED645"/>
                    <path d="M140,-20 C125,-30 115,-15 140,-20 C155,-15 145,-30 140,-20 Z" fill="#8ED645"/>
                    <path d="M65,25 C55,15 45,30 65,25 C75,30 65,15 65,25 Z" fill="#8ED645"/>
                </svg>
            </div>
            <!-- Electricity Worker SVG Decoration -->
            <div style="margin-top: 20px; text-align: center;">
                <svg width="150" height="150" viewBox="0 0 150 150" style="opacity: 0.9;">
                    <!-- Body/Uniform -->
                    <path d="M50,150 L50,105 C50,85 100,85 100,105 L100,150 Z" fill="#255A92"/>
                    <path d="M60,150 L60,110 C60,95 90,95 90,110 L90,150 Z" fill="#357AB2"/>
                    
                    <!-- Head -->
                    <circle cx="75" cy="70" r="16" fill="#FFCF9E"/>
                    
                    <!-- Hard Hat -->
                    <path d="M55,65 C55,40 95,40 95,65 L105,65 L105,70 L45,70 L45,65 Z" fill="#FFD700"/>
                    <rect x="70" y="50" width="10" height="8" fill="#E5C100" rx="2"/>
                    
                    <!-- Harness/Belt -->
                    <path d="M50,120 L100,120 L100,125 L50,125 Z" fill="#333333"/>
                    <rect x="70" y="118" width="10" height="10" fill="#FFD700" rx="2"/>
                    
                    <!-- Arms -->
                    <path d="M50,105 L35,125 L40,140" stroke="#255A92" stroke-width="12" stroke-linecap="round" fill="none"/>
                    <path d="M100,105 L115,125 L130,115" stroke="#255A92" stroke-width="12" stroke-linecap="round" fill="none"/>
                    
                    <!-- Wrench in Hand -->
                    <path d="M125,120 L145,100 L150,105 L130,125 Z" fill="#999999"/>
                    <circle cx="145" cy="100" r="6" fill="#999999"/>
                    <circle cx="145" cy="100" r="3" fill="#FFFFFF"/>
                </svg>
            </div>
        </div>

        <div class="chart-container">
            <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                {chart_elements}
            </svg>
        </div>
    </body>
    </html>
    """
    return html_code


def generate_line_chart_slide_5(
    main_title: str = "Average Blood Pressure by Age Group",
    subtitle: str = "Unit: mmHg | Data Source: National Health Survey 2025",
    insight: str = "",
    x_axis: str = "Age Group",
    y_axis: str = "Average Blood Pressure (mmHg)",
    unit: str = "mmHg",
    show_value: bool = True,
    show_legend: bool = True,
    y_axis_min: float = 0,
    y_axis_max: float = None,
    colors: list[str] = ["#E53935", "#1E88E5"],
    categories = ["18-25", "26-35", "36-45", "46-60", "60+"],
    series = [
        { "name": "Male", "values": [118, 122, 128, 135, 142] },
        { "name": "Female", "values": [80, 110, 100, 130, 138] }
    ],
) -> str:
    """
    Generates HTML code for a medical-themed line chart slide with modern healthcare aesthetics.
    """
    # ===== ADAPT INPUT → MAINTAIN EXISTING LOGIC =====
    font_family: str = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    accent_color: str = "#1068B0FF"
    main_title_color: str = "#1A237E"
    subtitle_color: str = "#37474F"
    insight_text_color: str = "#E2F4FF"
    legend_color: str = "#D4DCEA"
    main_title_font_size: str = "60px"  # Tăng từ 48px lên 60px
    subtitle_font_size: str = "18px"   # Giảm nhẹ để tạo thanh mảnh
    insight_font_size: str = "25px"
    # ===== 1. DATA INFORMATION EXTRACTION =====
    time_points = categories
    x_axis_label = x_axis
    y_axis_label = y_axis

    # ===== 2. SVG CONFIGURATION =====
    svg_w, svg_h = 1000, 600
    margin_t, margin_b, margin_l, margin_r = 80, 100, 100, 60
    chart_w = svg_w - margin_l - margin_r
    chart_h = svg_h - margin_t - margin_b
    
    all_values = [v for s in series for v in s.get("values", [])]
    y_min_input = y_axis_min
    y_max_input = y_axis_max
    y_min = float(y_min_input) if y_min_input is not None else (min(all_values) * 0.9 if all_values else 0)
    y_max = float(y_max_input) if y_max_input is not None else (max(all_values) * 1.1 if all_values else 100)
    if y_max == y_min:
        y_max += 1

    # ===== 3. CHART RENDERING =====
    chart_elements = ""
    
    # Grid lines and Y-axis labels
    steps = 6
    for i in range(steps + 1):
        y_pos = margin_t + (chart_h / steps) * i
        val = y_max - (y_max - y_min) / steps * i
        chart_elements += f'<line x1="{margin_l}" y1="{y_pos}" x2="{svg_w - margin_r}" y2="{y_pos}" stroke="#E0E0E0" stroke-dasharray="2,4" stroke-opacity="0.6"/><text x="{margin_l - 20}" y="{y_pos + 6}" font-size="14" text-anchor="end" fill="#757575" font-family="{font_family}">{val:g}</text>'
    
    # X-axis and Y-axis
    chart_elements += f'<line x1="{margin_l}" y1="{svg_h - margin_b}" x2="{svg_w - margin_r}" y2="{svg_h - margin_b}" stroke="#4A5568" stroke-width="2"/><line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{svg_h - margin_b}" stroke="#4A5568" stroke-width="2"/>'
    
    # X-axis labels
    num_points = len(time_points)
    for i, label in enumerate(time_points):
        x_pos = margin_l + (i / max(num_points - 1, 1)) * chart_w
        chart_elements += f'<text x="{x_pos}" y="{svg_h - margin_b + 35}" font-size="14" text-anchor="middle" fill="#4A5568" font-family="{font_family}">{label}</text>'
    
    # Draw each series line
    for idx, s in enumerate(series):
        color = colors[idx % len(colors)]
        values = s.get("values", [])
        if not values: continue
        
        path_points = []
        for i, val in enumerate(values):
            x = margin_l + (i / max(num_points - 1, 1)) * chart_w
            y = svg_h - margin_b - (val - y_min) / (y_max - y_min) * chart_h
            path_points.append(f"{x},{y}")
        
        # Main line with gradient effect
        chart_elements += f'<defs><linearGradient id="grad{idx}" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:{color};stop-opacity:0.7" /><stop offset="100%" style="stop-color:{color};stop-opacity:1" /></linearGradient></defs><path d="M {"L ".join(path_points)}" fill="none" stroke="url(#grad{idx})" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />'
        
        # Data points with glow effect
        for i, val in enumerate(values):
            x = margin_l + (i / max(num_points - 1, 1)) * chart_w
            y = svg_h - margin_b - (val - y_min) / (y_max - y_min) * chart_h
            
            chart_elements += f'<circle cx="{x}" cy="{y}" r="8" fill="{color}" stroke="white" stroke-width="3"><animate attributeName="r" values="7;8;7" dur="2s" repeatCount="indefinite"/></circle>'
            
            if show_value:
                chart_elements += f'<text x="{x}" y="{y - 15}" font-size="14" text-anchor="middle" font-weight="bold" fill="{color}" font-family="{font_family}">{val}{unit}</text>'
    
    # Axis labels
    chart_elements += f'<text x="{svg_w/2}" y="{svg_h - 20}" font-size="16" text-anchor="middle" fill="#4A5568" font-family="{font_family}">{x_axis_label}</text><text x="20" y="{svg_h/2}" font-size="16" text-anchor="middle" transform="rotate(-90, 20, {svg_h/2})" fill="#4A5568" font-family="{font_family}">{y_axis_label}</text>'

    # ===== 4. LEGEND =====
 # ===== 4. LEGEND (Đoạn này cần sửa) =====
    legend_html = ""
    if show_legend:
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            # SỬA Ở ĐÂY: Thay color:#2D3748 bằng color:{legend_color}
            legend_html += f"""
            <div style="display:flex; align-items:center; margin-bottom:16px;">
                <div style="width:28px; height:14px; background:{color}; border-radius:7px; margin-right:16px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                <span style="font-size:18px; color:{legend_color}; font-weight:600; font-family: {font_family};">
                    {s.get("name", "")}
                </span>
            </div>"""
    # ===== 5. HTML STRUCTURE =====
    html_code = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            body {{
                width: 1920px;
                height: 1080px;
                margin: 0;
                padding: 0;
                font-family: '{font_family}';
                position: relative;
                overflow: hidden;
            }}
            
            /* Blurred background image */
            body::before {{
                content: '';
                position: absolute;
                top: -10px;
                left: -10px;
                right: -10px;
                bottom: -10px;
                background-image: url("https://www.image2url.com/r2/default/images/1778126357628-dfd489ff-fb8d-4fd6-b9f5-70569c7d8df7.jpg");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                filter: blur(12px);
                z-index: -2;
            }}
            
            /* Dark overlay for better text contrast */
            body::after {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.35);
                z-index: -1;
            }}
            
            /* Header Section - Tối ưu bố cục */
            .header {{
                padding: 50px 100px 30px 100px;
                position: relative;
                z-index: 2;
                max-width: 1200px;
            }}
            
            /* Title - Glassmorphism effect với font-weight 800 */
            .title {{
                font-size: {main_title_font_size};
                font-weight: 800;
                color: {main_title_color};
                margin: 0;
                letter-spacing: -0.5px;
                background: transparent;
                display: inline-block;
                padding: 12px 28px;
                border-radius: 16px;
                text-shadow: 0 2px 8px rgba(255, 255, 255, 0.5);
                line-height: 1.2;
            }}
            
            /* Subtitle - Dạng tag thanh mảnh với accent border */
            .subtitle {{
                font-size: {subtitle_font_size};
                font-weight: 500;
                color: {subtitle_color};
                margin-top: 20px;
                background: rgba(255, 255, 255, 0.75);
                backdrop-filter: blur(8px);
                display: inline-block;
                padding: 10px 24px;
                border-radius: 30px;
                border-left: 4px solid {accent_color};
                letter-spacing: 0.3px;
                box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
            }}
            
            /* Header separator line */
            .header-separator {{
                margin: 25px 100px 0 100px;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), rgba(0, 121, 107, 0.3), rgba(255, 255, 255, 0.6), transparent);
                position: relative;
                z-index: 2;
            }}
            
            /* Medical Badge - Điều chỉnh vị trí gần Title hơn */
            .medical-badge {{
                display: inline-block;
                background: linear-gradient(135deg, {accent_color}, #0097A7);
                color: white;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.5px;
                box-shadow: 0 4px 12px rgba(0, 121, 107, 0.3);
                margin-bottom: 15px;
                backdrop-filter: blur(4px);
            }}
            
            .container {{
                flex: 1;
                display: flex;
                padding: 20px 100px 60px 100px;
                gap: 50px;
                position: relative;
                z-index: 2;
            }}
            
            .chart-card {{
                flex: 1.6;
                background: rgba(255, 255, 255, 0.92);
                border-radius: 24px;
                padding: 30px;
                border: 1px solid rgba(226, 232, 240, 0.8);
                backdrop-filter: blur(12px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            }}
        
            
            .insight-card {{
                flex: 1;
                background: transparent;
                padding: 40px;
                position: relative;
                overflow: hidden;
            }}
        
            
            .insight-card::before {{
                content: '⚕️';
                position: absolute;
                top: -15px;
                right: 30px;
                font-size: 120px;
                opacity: 0.08;
                transform: rotate(15deg);
            }}
            
            .insight-card::after {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 5px;
                background: linear-gradient(90deg, {accent_color}, #00BCD4, {accent_color});
                box-shadow: 0 2px 8px rgba(0, 121, 107, 0.3);
            }}
            
            .insight-title {{
                font-size: 20px;
                font-weight: 700;
                color: {accent_color};
                margin-bottom: 24px;
                display: flex;
                align-items: center;
                gap: 10px;
                padding-bottom: 16px;
                border-bottom: 2px solid rgba(0, 121, 107, 0.2);
                position: relative;
                z-index: 10;
            }}
            
            .insight-title::before {{
                content: '✓';
                display: inline-block;
                width: 24px;
                height: 24px;
                background: linear-gradient(135deg, {accent_color}, #0097A7);
                color: white;
                border-radius: 50%;
                text-align: center;
                line-height: 24px;
                font-weight: bold;
                margin-right: 8px;
                flex-shrink: 0;
            }}
            
            .insight-text {{
                font-size: {insight_font_size};
                color: {insight_text_color};
                line-height: 1.8;
                font-style: normal;
                font-weight: 500;
                position: relative;
                z-index: 10;
                padding: 20px 0;
                background: linear-gradient(to bottom, rgba(0, 121, 107, 0.03), transparent);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }}
            
            .legend {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 2px solid rgba(0, 121, 107, 0.2);
                position: relative;
                z-index: 10;
            }}
            
            .legend strong {{
                display: block;
                margin-bottom: 15px;
                color: {accent_color};
                font-size: 16px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .trend-indicator {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                margin-left: 8px;
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
                100% {{ transform: scale(1); }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="medical-badge">🏥 MEDICAL ANALYTICS</div>
            <div class="title">{main_title}</div>
            <div class="subtitle">{subtitle}</div>
        </div>
        
        <!-- Header Separator Line -->
        <div class="header-separator"></div>
        
        <div class="container">
            <div class="chart-card">
                <svg width="100%" height="100%" viewBox="0 0 {svg_w} {svg_h}">
                    {chart_elements}
                </svg>
            </div>
            
            <div class="insight-card">
                <div class="insight-title" color="{legend_color}">
                    Clinical Insights
                    <span class="trend-indicator" style="background: rgba(0, 121, 107, 0.2); color: {accent_color};">
                        TRENDS
                    </span>
                </div>
                
                <div class="insight-text">
                    {insight if insight else "Blood pressure shows a progressive increase with advancing age groups, indicating the importance of regular cardiovascular monitoring. The male demographic demonstrates consistently higher readings across all age brackets, suggesting gender-specific risk factors that warrant targeted intervention strategies."}
                </div>
                
                <div class="legend">
                    <strong style="display:block; margin-bottom: 15px; color: {legend_color}; font-size: 16px;">Patient Demographics:</strong>
                    {legend_html}
                </div>
            </div>
        </div>
    </body>
    </html>"""

    return html_code

