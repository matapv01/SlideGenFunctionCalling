
def generate_bar_chart_slide_1(
    main_title: str = "Quarterly Logistics Performance",
    subtitle: str = "Performance metrics across key operational hubs",
    insight: str = "Import volumes have seen a significant 20% surge in Q3 compared to previous quarters.",
    categories: list = ["Q1", "Q2", "Q3", "Q4"],
    series: list = [
        {"name": "Import", "data": [45, 52, 68, 58]},
        {"name": "Export", "data": [38, 41, 44, 50]}
    ],
    unit: str = " tons",
    show_value: bool = True,
    show_legend: bool = True,
    colors: list = ["#1B2559", "#FF6B35", "#4B5563", "#9CA3AF"],
    accent_color: str = "#FF6B35",
    main_title_color: str = "#1B2559",
    subtitle_color: str = "#6B7280",
    insight_text_color: str = "#374151",
    y_axis_label: str = "Volume",
) -> str:
    """
    Generates a generic HTML slide with a Grouped Bar Chart using the "Logistic Company" theme.
    """

    # ===== 1. LẤY THÔNG TIN =====
    title = main_title
    sub = subtitle
    insight_text = insight

    # ===== STYLE CONFIG =====
    font_family: str = "Arial, sans-serif"
    f_family = font_family
    c_accent = accent_color
    c_title = main_title_color
    c_sub = subtitle_color
    c_insight = insight_text_color
    main_title_font_size: str = "70px"
    subtitle_font_size: str = "32px"
    insight_font_size: str = "30px"
    fs_title = main_title_font_size
    fs_sub = subtitle_font_size
    fs_insight = insight_font_size
    x_axis_label = ""
    y_axis_min = 0
    y_axis_max = None

    # ===== 2. SVG CONFIG =====
    svg_w, svg_h = 1150, 650
    margin_top, margin_bottom = 60, 80
    margin_left, margin_right = 100, 50

    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    # ===== 3. TÍNH TOÁN DATA =====
    # Find max value for Y scaling
    all_values = []
    for s in series:
        all_values.extend(s.get("data", []))
    
    val_max = y_axis_max
    if val_max is None:
        val_max = max(all_values) if all_values else 100
        val_max = val_max * 1.1 # Add top padding

    val_min = y_axis_min
    
    if val_max == val_min:
        val_max += 10

    # Grid calculations
    num_grid_lines = 5
    
    # Bar calculations
    num_cats = len(categories) if categories else 1
    num_series = len(series) if series else 1
    
    # Calculate widths
    # Slot width = space allocated for one category
    slot_width = chart_w / num_cats
    padding_group = slot_width * 0.2 # 20% padding between groups
    group_width = slot_width - padding_group
    bar_width = group_width / num_series

    # ===== 4. VẼ CHART =====
    chart_elements = ""

    # -- Background Grid --
    for i in range(num_grid_lines + 1):
        y_ratio = i / num_grid_lines
        y_pos = svg_h - margin_bottom - (y_ratio * chart_h)
        value_label = val_min + (val_max - val_min) * y_ratio
        
        # Grid line
        chart_elements += f'''
        <line x1="{margin_left}" y1="{y_pos}" x2="{svg_w - margin_right}" y2="{y_pos}" 
              stroke="#E5E7EB" stroke-width="1" stroke-dasharray="0"/>
        '''
        # Y-Axis Label
        chart_elements += f'''
        <text x="{margin_left - 15}" y="{y_pos + 5}" font-family="{f_family}" font-size="16" 
              fill="#9CA3AF" text-anchor="end">{int(value_label) if value_label % 1 == 0 else f"{value_label:.1f}"}</text>
        '''

    # -- Bars --
    for i, cat in enumerate(categories):
        # Center X of the category slot
        slot_x_start = margin_left + (i * slot_width) + (padding_group / 2)
        
        for j, s in enumerate(series):
            data_val = s["data"][i] if i < len(s["data"]) else 0
            
            # Height calculation
            bar_height = ((data_val - val_min) / (val_max - val_min)) * chart_h
            if bar_height < 0: bar_height = 0
            
            x_pos = slot_x_start + (j * bar_width)
            y_pos = svg_h - margin_bottom - bar_height
            
            color = colors[j % len(colors)]
            
            # Rect
            chart_elements += f'''
            <rect x="{x_pos}" y="{y_pos}" width="{bar_width * 0.85}" height="{bar_height}" 
                  fill="{color}" rx="4" ry="4" />
            '''
            
            # Value Label (on top of bar)
            if show_value:
                chart_elements += f'''
                <text x="{x_pos + (bar_width * 0.85)/2}" y="{y_pos - 8}" 
                      font-family="{f_family}" font-size="14" fill="{color}" font-weight="bold" text-anchor="middle">
                    {data_val}{unit}
                </text>
                '''

        # Category Label (X-axis)
        cat_x_center = margin_left + (i * slot_width) + (slot_width / 2)
        chart_elements += f'''
        <text x="{cat_x_center}" y="{svg_h - margin_bottom + 30}" 
              font-family="{f_family}" font-size="18" fill="{c_title}" font-weight="bold" text-anchor="middle">
            {cat}
        </text>
        '''

    # -- Axis Titles --
    if y_axis_label:
        chart_elements += f'''
        <text transform="rotate(-90)" x="{-svg_h/2}" y="30" 
              font-family="{f_family}" font-size="18" fill="{c_sub}" text-anchor="middle">
            {y_axis_label}
        </text>
        '''

    # ===== LEGEND (HTML side) =====
    legend_html = ""
    if show_legend:
        legend_html += '<div style="display:flex; flex-wrap:wrap; gap:20px; margin-top:30px;">'
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_html += f'''
                <span style="display:flex; align-items:center; gap:8px;">
                    <span style="width:16px; height:16px; background-color:{color}; border-radius:4px; display:inline-block;"></span>
                    <span style="font-family:{f_family}; font-size:18px; color:{c_title}; font-weight:500;">{s.get("name", "Series")}</span>
                </span>
            '''
        legend_html += '</div>'

    # ===== INSIGHT =====
    insight_html = f"""
    <div style="
        font-family: {f_family};
        font-size: {fs_insight};
        color: {c_insight};
        line-height: 1.6;
        background: #F3F4F6;
        padding: 30px;
        border-left: 6px solid {c_accent};
        border-radius: 0 12px 12px 0;
        margin-bottom: 20px;">
        {insight_text}
    </div>
    """

    # ===== 5. HTML RENDER =====
    # Logistic Theme: White BG, Navy/Orange accents, clean layout
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
        font-family: {f_family};
        background-color: #FFFFFF;
        position: relative;
    }}
    
    /* Decorative Background Elements based on reference */
    .bg-shape-top {{
        position: absolute;
        top: 0;
        left: 0;
        width: 400px;
        height: 150px;
        background: {c_title}; /* Navy */
        clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
        z-index: 0;
    }}
    .bg-shape-accent {{
        position: absolute;
        top: 0;
        left: 0;
        width: 150px;
        height: 150px;
        background: {c_accent}; /* Orange */
        clip-path: polygon(0 0, 80% 0, 0 80%);
        z-index: 1;
    }}
    .bg-shape-bottom {{
        position: absolute;
        bottom: 0;
        right: 0;
        width: 300px;
        height: 120px;
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
        padding-left: 350px;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }}
    
    .title-group h1 {{
        font-size: {fs_title};
        color: {c_accent}; /* Orange Title like 'Logistic' */
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .title-group h1 span {{
        color: {c_title}; /* Navy part like 'Company' */
    }}
    
    .subtitle {{
        font-size: {fs_sub};
        color: {c_sub};
        margin-top: 10px;
        font-weight: 400;
    }}

    .main-content {{
        display: flex;
        flex: 1;
        gap: 60px;
        align-items: center;
    }}
    
    .left-panel {{
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    
    .right-panel {{
        flex: 2;
        display: flex;
        justify-content: center;
        align-items: center;
    }}
    
    .footer-mark {{
        position: absolute;
        bottom: 30px;
        right: 40px;
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
        <div class="header">
            <div class="title-group">
                <h1>{title}</h1>
                <div class="subtitle">{sub}</div>
            </div>
            <div style="font-size: 24px; color: {c_title}; font-weight: bold; opacity: 0.5;">2024 REPORT</div>
        </div>

        <div class="main-content">
            <div class="left-panel">

                {insight_html}
                {legend_html}
            </div>

            <div class="right-panel">
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
    return html_code

def generate_bar_chart_slide_2(
        main_title = "Global Trade Analysis",
        subtitle = "Maritime shipping volume across major regions",
        insight = "The Pacific region continues to dominate maritime shipping, driven by strong export growth in East Asia.",
        x_axis = "Regions",
        y_axis = "Shipping Volume (TEU)",
        unit = "M",
        show_value = True,
        show_legend = True,
        y_axis_min = 0,
        y_axis_max = None,
        colors = ["#00695C", "#26A69A", "#4DD0E1", "#0277BD", "#00838F"],
        categories = ["Pacific", "Atlantic", "Indian Ocean", "Mediterranean"],
        series = [
            {"name": "2023", "values": [120, 85, 60, 45]},
            {"name": "2024", "values": [135, 90, 65, 50]}
        ],
        accent_color = "#00897B",
        main_title_color = "#104c64",
        subtitle_color = "#457b8c",
        insight_text_color = "#2c5f70",


    ) -> str:
    """
    Generates an Ocean-themed Grouped Bar Chart slide based on the provided data and style.
    """

    # ===== 1. LẤY THÔNG TIN & XỬ LÝ DỮ LIỆU =====
    title = main_title
    sub = subtitle
    ins = insight
    
    x_axis_label = x_axis
    y_axis_label = y_axis

    # ===== STYLE CONFIG (OCEAN THEME) =====
    font_family = "'Quicksand', 'Varela Round', 'Verdana', sans-serif",
    bg_color = "#E0F7FA" # Light Cyan background like the water
    accent = accent_color
    title_col = main_title_color
    sub_col = subtitle_color
    ins_col = insight_text_color
    title_fs = "80px"
    sub_fs = "36px"
    ins_fs = "28px"

    # ===== 2. SVG CONFIG =====
    svg_w, svg_h = 1100, 700
    margin_top, margin_bottom = 60, 80
    margin_left, margin_right = 100, 60

    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    # ===== 3. TÍNH TOÁN MIN/MAX =====
    # Lấy tất cả giá trị từ các series
    all_values = []
    for s in series:
        all_values.extend(s.get("values", []))
    
    if not all_values:
        all_values = [0]

    y_min = y_axis_min if y_axis_min is not None else 0
    y_max = y_axis_max if y_axis_max is not None else (max(all_values) * 1.1 if all_values else 100)

    # 🛡 Tránh chia cho 0
    if y_max <= y_min:
        y_max = y_min + 10

    # ===== 4. VẼ CHART (SVG GENERATION) =====
    chart_elements = ""

    # -- Background Chart Decor --
    chart_elements += f'''
    <rect x="{margin_left}" y="{margin_top}" width="{chart_w}" height="{chart_h}" 
          fill="white" fill-opacity="0.3" rx="20" ry="20" />
    '''

    # -- Grid Lines (Nét đứt mềm mại) --
    num_ticks = 5
    for i in range(num_ticks + 1):
        # Grid ngang (Y-axis)
        val_y = y_min + (y_max - y_min) * (i / num_ticks)
        pos_y = svg_h - margin_bottom - (i / num_ticks) * chart_h
        
        chart_elements += f'''
        <line x1="{margin_left}" y1="{pos_y}" x2="{svg_w - margin_right}" y2="{pos_y}" 
              stroke="#B2EBF2" stroke-width="2" stroke-dasharray="5,5"/>
        '''
        # Label Y
        chart_elements += f'''
        <text x="{margin_left - 15}" y="{pos_y + 5}" font-family="{font_family}" 
              font-size="16" fill="{sub_col}" text-anchor="end">{int(val_y) if val_y == int(val_y) else f"{val_y:.1f}"}</text>
        '''

    # -- Axis Labels --
    # X Label
    if x_axis_label:
        chart_elements += f'''
        <text x="{margin_left + chart_w/2}" y="{svg_h - 20}" font-family="{font_family}" 
              font-size="20" fill="{title_col}" font-weight="bold" text-anchor="middle">{x_axis_label}</text>
        '''
    # Y Label
    if y_axis_label:
        chart_elements += f'''
        <text transform="rotate(-90)" x="{-svg_h/2}" y="30" font-family="{font_family}" 
              font-size="20" fill="{title_col}" font-weight="bold" text-anchor="middle">{y_axis_label}</text>
        '''

    # -- Grouped Bar Chart --
    num_categories = len(categories)
    num_series = len(series)
    
    if num_categories > 0 and num_series > 0:
        # Tính toán kích thước và khoảng cách
        group_width = chart_w / num_categories * 0.8  # 80% của không gian dành cho mỗi nhóm
        bar_width = group_width / num_series * 0.85   # 85% của không gian nhóm chia đều cho các cột
        group_spacing = chart_w / num_categories
        
        for cat_idx, category in enumerate(categories):
            # Vị trí trung tâm của nhóm cột
            group_center_x = margin_left + (cat_idx + 0.5) * group_spacing
            
            # Vẽ các cột trong nhóm
            for series_idx, s in enumerate(series):
                values = s.get("values", [])
                if cat_idx < len(values):
                    value = values[cat_idx]
                    color = colors[series_idx % len(colors)]
                    
                    # Tính toán vị trí và chiều cao của cột
                    bar_height = (value - y_min) / (y_max - y_min) * chart_h
                    bar_x = group_center_x - group_width/2 + series_idx * (group_width / num_series) + (group_width / num_series - bar_width) / 2
                    bar_y = svg_h - margin_bottom - bar_height
                    
                    # Vẽ cột với bo góc
                    chart_elements += f'''
                    <rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" 
                          fill="{color}" rx="5" ry="5"/>
                    '''
                    
                    # Hiển thị giá trị trên cột (nếu bật)
                    if show_value:
                        chart_elements += f'''
                        <text x="{bar_x + bar_width/2}" y="{bar_y - 8}" font-family="{font_family}" 
                              font-size="14" fill="{title_col}" text-anchor="middle" font-weight="bold">{value}{unit}</text>
                        '''
            
            # Nhãn danh mục (category) trên trục X
            chart_elements += f'''
            <text x="{group_center_x}" y="{svg_h - margin_bottom + 25}" font-family="{font_family}" 
                  font-size="16" fill="{title_col}" text-anchor="middle">{category}</text>
            '''

    # ===== LEGEND (HTML) =====
    legend_html = ""
    if show_legend:
        legend_html = '<div class="legend-container">'
        for i, s in enumerate(series):
            color = colors[i % len(colors)]
            legend_html += f'''
            <div class="legend-item">
                <div class="legend-dot" style="background-color:{color}; box-shadow: 0 0 0 1px {color};"></div>
                <div class="legend-label">{s.get("name", "Series")}</div>
            </div>
            '''
        legend_html += '</div>'

    # ===== INSIGHT (HTML) =====
    insight_html = ins

    # ===== 5. HTML RENDER =====
    # Cấu trúc: Header + 2 Cột (Left: Insight/Legend - Right: Chart)
    # Background có thêm vài bong bóng trang trí bằng CSS thuần (border-radius)
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
            background-color: {bg_color};
            /* Hiệu ứng gradient nhẹ giống nước */
            background: linear-gradient(135deg, #E0F7FA 0%, #B2EBF2 100%);
        }}

        /* Bong bóng trang trí nền */
        .bubble-bg {{
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.4);
            z-index: 0;
        }}

        .container {{
            position: relative;
            z-index: 1;
            padding: 80px 100px;
            display: flex;
            flex-direction: column;
            height: 100%;
            box-sizing: border-box;
        }}

        .header {{
            margin-bottom: 40px;
        }}

        h1 {{
            font-size: {title_fs};
            color: {title_col};
            margin: 0;
            font-weight: 800;
            letter-spacing: -1px;
        }}

        .subtitle {{
            font-size: {sub_fs};
            color: {sub_col};
            margin-top: 15px;
            font-weight: 500;
        }}

        .content-flex {{
            display: flex;
            flex: 1;
            gap: 60px;
            align-items: center; 
        }}

        .left-col {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .right-col {{
            flex: 1.6;
            background: rgba(255, 255, 255, 0.6);
            border-radius: 40px;
            padding: 20px;
            box-shadow: 0 20px 50px rgba(0, 137, 123, 0.1);
            display: flex;
            justify-content: center;
            align-items: center;
            backdrop-filter: blur(10px);
        }}
        
        .insight-box {{
            font-size: {ins_fs};
            color: {ins_col};
            font-family: {font_family};
            line-height: 1.6;
        }}
        
        .legend-container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-top: 40px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .legend-dot {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 8px;
            border: 2px solid white;
        }}
        
        .legend-label {{
            font-size: 20px;
            color: {title_col};
            font-family: {font_family};
        }}

    </style>
    </head>
    <body>
        <div class="bubble-bg" style="width: 300px; height: 300px; top: -50px; left: -50px;"></div>
        <div class="bubble-bg" style="width: 150px; height: 150px; bottom: 100px; right: 200px;"></div>
        <div class="bubble-bg" style="width: 80px; height: 80px; top: 100px; right: 40%;"></div>

        <div class="container">
            <div class="header">
                <h1>{title}</h1>
                {f'<div class="subtitle">{sub}</div>' if sub else ""}
            </div>

            <div class="content-flex">
                <div class="left-col">
                    <div class="insight-box">{ins}</div>
                    {legend_html}
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


def generate_bar_chart_slide_3(
        main_title = "Student Performance Analysis",
        subtitle = "Comparing average grades across different subjects",
        x_axis = "Subjects",
        y_axis = "Average Score",
        unit = "",
        show_value = True,
        show_legend = True,
        y_axis_min = 0,
        y_axis_max = None,
        colors = ["#4A5E7B", "#F5B041", "#A67C52", "#B5B191"],
        categories = ["Math", "Science", "English", "History"],
        series = [
            {"name": "Class A", "values": [85, 92, 78, 80]},
            {"name": "Class B", "values": [80, 88, 82, 75]}
        ],
        data_label_format = "{value}",
        main_title_color = "#4A5E7B",
        subtitle_color = "#8E97A4",
        image_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT3jt3HxXUeFzHPpte0_XVx2FuYiUqYEXELOaVwMGPLuRo0onkYXLylC7dg&s=10"
    ) -> str:
    """
    Tạo slide biểu đồ cột (Grouped Bar Chart) với phong cách giáo dục, 
    lấy cảm hứng từ theme 'My Family'.
    """

    # ===== 1. LẤY THÔNG TIN DỮ LIỆU =====
    x_axis_label = x_axis
    y_axis_label = y_axis
    font_family = "Inter, sans-serif"
    main_title_font_size = "65px"
    subtitle_font_size = "28px"
    # ===== 2. SVG CONFIG & TÍNH TOÁN =====
    svg_w, svg_h = 1100, 600
    margin_t, margin_b, margin_l, margin_r = 60, 80, 100, 40
    chart_w = svg_w - margin_l - margin_r
    chart_h = svg_h - margin_t - margin_b

    all_values = [v for s in series for v in s.get("values", [])]
    y_min = y_axis_min
    y_max = y_axis_max
    if y_max is None:
        y_max = max(all_values) * 1.1 if all_values else 100
    if y_max == y_min: y_max += 1

    # ===== 3. VẼ BIỂU ĐỒ (SVG ELEMENTS) =====
    chart_elements = ""

    # Grid lines & Y-axis labels
    steps = 5
    for i in range(steps + 1):
        y_pos = margin_t + (chart_h / steps) * i
        val = y_max - (y_max - y_min) / steps * i
        chart_elements += f'''
        <line x1="{margin_l}" y1="{y_pos}" x2="{svg_w - margin_r}" y2="{y_pos}" stroke="#E5E7EB" stroke-dasharray="5,5" />
        <text x="{margin_l - 15}" y="{y_pos + 6}" font-size="18" text-anchor="end" fill="{subtitle_color}">{val:.0f}</text>
        '''

    # Grouped Bars logic
    num_cats = len(categories)
    num_series = len(series)
    
    if num_cats > 0:
        cat_width = chart_w / num_cats
        # Chiều rộng mỗi cột (bar), chừa khoảng cách giữa các nhóm
        gap_between_groups = 0.2 
        available_bar_space = cat_width * (1 - gap_between_groups)
        bar_width = available_bar_space / num_series

        for c_idx, cat in enumerate(categories):
            x_group_start = margin_l + c_idx * cat_width + (cat_width * gap_between_groups / 2)
            
            # X-axis labels
            chart_elements += f'<text x="{x_group_start + available_bar_space/2}" y="{svg_h - margin_b + 40}" font-size="20" text-anchor="middle" fill="{main_title_color}" font-weight="bold">{cat}</text>'
            
            for s_idx, s in enumerate(series):
                val = s.get("values", [])[c_idx] if c_idx < len(s.get("values", [])) else 0
                color = colors[s_idx % len(colors)]
                
                h = ((val - y_min) / (y_max - y_min)) * chart_h
                x_bar = x_group_start + s_idx * bar_width
                y_bar = svg_h - margin_b - h
                
                # Vẽ cột với bo góc phía trên (rx)
                chart_elements += f'''
                <rect x="{x_bar + 5}" y="{y_bar}" width="{max(bar_width - 10, 5)}" height="{h}" fill="{color}" rx="8" />
                '''
                
                if show_value:
                    label = data_label_format.replace("{value}", str(val)) + unit
                    chart_elements += f'<text x="{x_bar + bar_width/2}" y="{y_bar - 10}" font-size="16" text-anchor="middle" fill="{main_title_color}" font-weight="bold">{label}</text>'

    # Axis Title
    chart_elements += f'<text x="{svg_w/2 + margin_l/2}" y="{svg_h - 10}" font-size="22" text-anchor="middle" fill="{main_title_color}" font-weight="600">{x_axis_label}</text>'
    chart_elements += f'<text transform="rotate(-90)" x="{-svg_h/2}" y="30" font-size="22" text-anchor="middle" fill="{main_title_color}" font-weight="600">{y_axis_label}</text>'

    # ===== 4. CẤU TRÚC LEGEND & INSIGHT =====
    legend_html = ""
    if show_legend:
        for i, s in enumerate(series):
            legend_html += f'''
            <div style="display:flex; align-items:center;">
                <div style="width:24px; height:24px; background:{colors[i % len(colors)]}; border-radius:50%; margin-right:12px;"></div>
                <span style="font-size:24px; color:{main_title_color}; font-weight:500;">{s.get("name")}</span>
            </div>
            '''

    # ===== 5. GENERATE FINAL HTML =====
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                width: 1920px; height: 1080px; margin: 0; padding: 0;
                background-color: #FDF5E6; /* Light beige */
                font-family: {font_family};
                display: flex; flex-direction: column;
                overflow: hidden;
            }}
            .top-bar {{
                padding: 60px 100px 20px 100px;
            }}
            .title-box {{
                display: inline-block;
            }}
            h1 {{ margin: 0; font-size: {main_title_font_size}; color: {main_title_color}; text-transform: capitalize; }}
            .subtitle {{ font-size: {subtitle_font_size}; color: {subtitle_color}; margin-top: 10px; padding-left: 20px; }}
            
            .content-area {{
                display: flex;
                flex: 1;
                padding: 0 80px 60px 80px;
                gap: 40px;
            }}
            .left-panel {{
                flex: 1.5;
                display: flex; flex-direction: column;
                justify-content: flex-start;
            }}
            .legend-container {{
                display: flex;
                gap: 30px;
                margin-bottom: 40px;
                padding-left: 20px;
            }}
            .chart-panel {{
                display: flex; align-items: flex-start; justify-content: flex-start;
            }}
            .right-panel {{
                flex: 1;
                display: flex; align-items: center; justify-content: center;
            }}
            .image-capsule {{
                width: 500px;
                height: 800px;
                border-radius: 250px;
                object-fit: cover;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            .decoration-star {{
                position: absolute; color: white; font-size: 40px;
            }}
        </style>
    </head>
    <body>
        <div class="decoration-star" style="top:40px; left:40px;">✦</div>
        <div class="decoration-star" style="top:100px; left:80px;">✦</div>
        
        <div class="top-bar">
            <div class="title-box">
                <h1>{main_title}</h1>
            </div>
            <div class="subtitle">{subtitle}</div>
        </div>

        <div class="content-area">
            <div class="left-panel">
                <div class="legend-container">
                    {legend_html}
                </div>
                <div class="chart-panel">
                    <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                        {chart_elements}
                    </svg>
                </div>
            </div>

            <div class="right-panel">
                <img class="image-capsule" src="{image_url}" alt="Decoration">
            </div>
        </div>
    </body>
    </html>
    """


def generate_bar_chart_slide_4(
        main_title = "Business Inforgraphic", 
        subtitle = "Detailed shipment analysis for the fiscal year 2024",
        insight = "The shipment volume has shown a steady increase compared to last year.",
        x_axis = "Regions",
        y_axis = "Percentage",
        unit = "%",
        show_value = True,
        show_legend = True,
        y_axis_min = 0,
        y_axis_max = None,
        colors= ["#1B2559", "#FF6B35", "#4B5563", "#9CA3AF","#85BA2A", "#5561D2"],
        categories = ["North America", "Europe", "Asia", "South America", "Africa", "Australia"],
        insights = [
            "North America's shipment volume increased by 15% compared to last year.",
            "Europe experienced a significant growth of 25% in shipment volume.",
            "Asia had a steady increase of 10% in shipment volume.",
            "South America's shipment volume remained stable with a slight increase of 5%.",
            "Africa saw a remarkable growth of 40% in shipment volume.",
            "Australia experienced a moderate increase of 20% in shipment volume."
        ],
        series = [20, 10, 5, 5, 40, 20],
        accent_color = "#FF6B35",
        main_title_color = "#1B2559",
        subtitle_color = "#6B7280",
        insight_text_color = "#374151",
    ) -> str:
    """
    Generates a generic HTML slide with a Grouped Bar Chart using the "Logistic Company" theme.
    """

    # ===== 1. LẤY THÔNG TIN =====
    title = main_title
    sub = subtitle
    insight_text = insight
    font_family = "Inter, sans-serif"
    main_title_font_size = "64px"
    subtitle_font_size = "28px"
    insight_font_size = "26px"
    # The parameters are now used directly as they are passed to the function.
    # unit, show_value, show_legend, y_axis_min, y_axis_max, colors, categories, series
    # are all already available from the function arguments.

    y_axis_label = y_axis
    x_axis_label = x_axis

    # Normalize series: if it's a flat list of numbers, wrap it in the expected dict structure
    if series and isinstance(series, list) and not isinstance(series[0], dict):
        series = [{"name": y_axis_label if y_axis_label else "Series 1", "data": series}]

    # ===== STYLE CONFIG =====
    # Override defaults if not provided, leaning towards the image theme
    f_family = font_family if font_family else "Arial, sans-serif"
    c_accent = accent_color if accent_color else "#FF6B35"
    c_title = main_title_color if main_title_color else "#1B2559"
    c_sub = subtitle_color if subtitle_color else "#6B7280"
    c_insight = insight_text_color if insight_text_color else "#374151"

    fs_title = main_title_font_size
    fs_sub = subtitle_font_size
    fs_insight = insight_font_size

    # ===== 2. SVG CONFIG =====
    svg_w, svg_h = 1150, 650
    margin_top, margin_bottom = 60, 80
    margin_left, margin_right = 100, 50

    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    # ===== 3. TÍNH TOÁN DATA =====
    # Find max value for Y scaling
    all_values = []
    for s in series:
        all_values.extend(s.get("data", []))
    
    val_max = y_axis_max
    if val_max is None:
        val_max = max(all_values) if all_values else 100
        val_max = val_max * 1.1 # Add top padding

    val_min = y_axis_min
    
    if val_max == val_min:
        val_max += 10

    # Grid calculations
    num_grid_lines = 5
    
    # Bar calculations
    num_cats = len(categories) if categories else 1
    num_series = len(series) if series else 1
    
    # Calculate widths
    # Slot width = space allocated for one category
    slot_width = chart_w / num_cats
    padding_group = slot_width * 0.2 # 20% padding between groups
    group_width = slot_width - padding_group
    bar_width = group_width / num_series

    # ===== 4. VẼ CHART =====
    chart_elements = ""

    # -- Background Grid --
    for i in range(num_grid_lines + 1):
        y_ratio = i / num_grid_lines
        y_pos = svg_h - margin_bottom - (y_ratio * chart_h)
        value_label = val_min + (val_max - val_min) * y_ratio
        
        # Grid line
        chart_elements += f'''
        <line x1="{margin_left}" y1="{y_pos}" x2="{svg_w - margin_right}" y2="{y_pos}" 
              stroke="#E5E7EB" stroke-width="1" stroke-dasharray="0"/>
        '''
        # Y-Axis Label
        chart_elements += f'''
        <text x="{margin_left - 15}" y="{y_pos + 5}" font-family="{f_family}" font-size="16" 
              fill="#9CA3AF" text-anchor="end">{int(value_label) if value_label % 1 == 0 else f"{value_label:.1f}"}</text>
        '''

    # -- Bars --
    for i, cat in enumerate(categories):
        # Center X of the category slot
        slot_x_start = margin_left + (i * slot_width) + (padding_group / 2)
        
        for j, s in enumerate(series):
            data_val = s["data"][i] if i < len(s["data"]) else 0
            
            # Height calculation
            bar_height = ((data_val - val_min) / (val_max - val_min)) * chart_h
            if bar_height < 0: bar_height = 0
            
            x_pos = slot_x_start + (j * bar_width)
            y_pos = svg_h - margin_bottom - bar_height
            
            # Use color by category if only one series, otherwise by series
            if len(series) == 1:
                color = colors[i % len(colors)]
            else:
                color = colors[j % len(colors)]
            
            # Rect
            chart_elements += f'''
            <rect x="{x_pos}" y="{y_pos}" width="{bar_width * 0.85}" height="{bar_height}" 
                  fill="{color}" rx="4" ry="4" />
            '''
            
            # Value Label (on top of bar)
            if show_value:
                chart_elements += f'''
                <text x="{x_pos + (bar_width * 0.85)/2}" y="{y_pos - 8}" 
                      font-family="{f_family}" font-size="14" fill="{color}" font-weight="bold" text-anchor="middle">
                    {data_val}{unit}
                </text>
                '''

        # Category Label (X-axis)
        cat_x_center = margin_left + (i * slot_width) + (slot_width / 2)
        chart_elements += f'''
        <text x="{cat_x_center}" y="{svg_h - margin_bottom + 30}" 
              font-family="{f_family}" font-size="18" fill="{c_title}" font-weight="bold" text-anchor="middle">
            {cat}
        </text>
        '''

    # -- Axis Titles --
    if y_axis_label:
        chart_elements += f'''
        <text transform="rotate(-90)" x="{-svg_h/2}" y="30" 
              font-family="{f_family}" font-size="18" fill="{c_sub}" text-anchor="middle">
            {y_axis_label}
        </text>
        '''

    # ===== LEGEND (HTML side) =====
    legend_left_html = ""
    legend_right_html = ""
    if show_legend:
        data_list = series[0]["data"] if series else []
        half = (len(categories) + 1) // 2
        
        legend_left_html += '<div style="display:flex; flex-direction:column; gap:30px; margin-top:30px;">'
        for i in range(half):
            if i >= len(categories): break
            cat = categories[i]
            color = colors[i % len(colors)]
            val = data_list[i] if i < len(data_list) else 0
            desc = insights[i] if insights and i < len(insights) else ""
            legend_left_html += f'''
                <div style="display:flex; flex-direction:column; gap:8px; font-family:{f_family}; color:#000;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="width:24px; height:24px; background-color:{color}; border-radius:50%; border: 1px solid #000; display:inline-block;"></span>
                        <span style="font-size:28px;">{val}{unit}</span>
                    </div>
                    <div style="font-size:26px; padding-left:34px;">{cat}</div>
                    <div style="font-size:22px; padding-left:34px; line-height:1.4; max-width:300px;">{desc}</div>
                </div>
            '''
        legend_left_html += '</div>'

        legend_right_html += '<div style="display:flex; flex-direction:column; gap:30px; margin-top:30px;">'
        for i in range(half, len(categories)):
            cat = categories[i]
            color = colors[i % len(colors)]
            val = data_list[i] if i < len(data_list) else 0
            desc = insights[i] if insights and i < len(insights) else ""
            legend_right_html += f'''
                <div style="display:flex; flex-direction:column; gap:8px; font-family:{f_family}; color:#000;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="width:24px; height:24px; background-color:{color}; border-radius:50%; border: 1px solid #000; display:inline-block;"></span>
                        <span style="font-size:28px;">{val}{unit}</span>
                    </div>
                    <div style="font-size:26px; padding-left:34px;">{cat}</div>
                    <div style="font-size:22px; padding-left:34px; line-height:1.4; max-width:300px;">{desc}</div>
                </div>
            '''
        legend_right_html += '</div>'

    # ===== INSIGHT =====
    insight_html = f"""
    <div style="
        font-family: {f_family};
        font-size: {fs_insight};
        color: {c_insight};
        line-height: 1.6;
        background: #F3F4F6;
        padding: 30px;
        border-left: 6px solid {c_accent};
        border-radius: 0 12px 12px 0;
        margin-bottom: 20px;">
        {insight_text}
    </div>
    """

    # ===== 5. HTML RENDER =====
    # Logistic Theme: White BG, Navy/Orange accents, clean layout
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
        font-family: {f_family};
        background-color: #FFFFFF;
        position: relative;
    }}
    
    /* Decorative Background Elements based on reference */
    .bg-shape-top {{
        position: absolute;
        top: -500px;
        left: 0;
        width: 400px;
        height: 150px;
        background: {c_title}; /* Navy */
        clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
        z-index: 0;
    }}
    .bg-shape-accent {{
        position: absolute;
        top: 0;
        left: 0;
        width: 150px;
        height: 150px;
        background: {c_accent}; /* Orange */
        clip-path: polygon(0 0, 80% 0, 0 80%);
        z-index: 1;
    }}
    .bg-shape-bottom {{
        position: absolute;
        bottom: 0;
        right: 0;
        width: 150px;
        height: 150px;
        background: {c_title};
        clip-path: polygon(100% 0, 100% 100%, 0% 100%);
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
        font-size: {fs_title};
        color: {c_accent}; /* Orange Title like 'Logistic' */
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .title-group h1 span {{
        color: {c_title}; /* Navy part like 'Company' */
    }}
    
    .subtitle {{
        font-size: {fs_sub};
        color: {c_sub};
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
        right: 40px;
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
    <div class="footer-mark"></div>

    <div class="container">
        <div class="header">
            <div class="title-group">
                <h1>{title}</h1>
                <div class="subtitle">{sub}</div>
            </div>
            <div style="font-size: 24px; color: {c_title}; font-weight: bold; opacity: 0.5;">2024 REPORT</div>
        </div>

        <div class="main-content">
            <div class="left-panel">
                {legend_left_html}
            </div>

            <div class="center-panel">
                <div>
                    <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">
                        {chart_elements}
                    </svg>
                </div>
            </div>

            <div class="right-panel">
                {legend_right_html}
            </div>
        </div>
    </div>

    </body>
    </html>
    """
    return html_code


def generate_bar_chart_slide_5(
        main_title = "Business Inforgraphic", 
        subtitle = "Detailed shipment analysis for the fiscal year 2024",
        unit = "%",
        colors= ["#1B2559", "#FF6B35", "#4B5563", "#9CA3AF","#85BA2A", "#5561D2"],
        categories = ["North America", "Europe", "Asia", "South America", "Africa"],
        insights = [
            "North America's shipment volume increased by 15% compared to last year.",
            "Europe experienced a significant growth of 25% in shipment volume.",
            "Asia had a steady increase of 10% in shipment volume.",
            "South America's shipment volume remained stable with a slight increase of 5%.",
            "Africa saw a remarkable growth of 40% in shipment volume."
        ],
        series = [20, 10, 5, 5, 40],
        accent_color = "#FF6B35",
        main_title_color = "#1B2559",
        subtitle_color = "#6B7280",
        insights_text_color = "#374151",
    ) -> str:
    """
    Generates a generic HTML slide with a Grouped Bar Chart using the "Logistic Company" theme.
    """

    # ===== 1. LẤY THÔNG TIN =====
    title = main_title
    if subtitle:
        subtitle = f"<div style='font-size: {subtitle_font_size}; color: {subtitle_color}; margin-top: 10px;'>{subtitle}</div>"

    # ===== STYLE CONFIG =====
    # Override defaults if not provided, leaning towards the image theme
    f_family = font_family if font_family else "Arial, sans-serif"
    c_accent = accent_color if accent_color else "#FF6B35"
    c_title = main_title_color if main_title_color else "#1B2559"
    c_sub = subtitle_color if subtitle_color else "#6B7280"
    c_insight = insights_text_color if insights_text_color else "#374151"
    font_family = "Inter, sans-serif",
    main_title_font_size = "64px",
    subtitle_font_size = "28px",
    insights_font_size = "26px"
    fs_title = main_title_font_size
    fs_sub = subtitle_font_size
    fs_insight = insights_font_size

    # ===== 2. RENDER ROWS =====
    data_list = series
    rows_html = ""
    for i, cat in enumerate(categories):
        color = colors[i % len(colors)]
        val = data_list[i] if i < len(data_list) else 0
        desc = insights[i] if insights and i < len(insights) else ""
        
        # Calculate percentage for progress bar width
        percent = min(100, max(0, val))

        rows_html += f'''
        <div style="display: flex; align-items: center; gap: 30px; margin-bottom: 25px; width: 100%;">
            <!-- Progress Bar -->
            <div style="flex: 2; height: 40px; background-color: #F3F4F6; border-radius: 20px; overflow: hidden; position: relative; margin-right: 20px;">
                <div style="width: {percent}%; height: 100%; background-color: {color}; border-radius: 20px;"></div>
            </div>
            
            <!-- Percentage -->
            <div style="width: 100px; font-size: 40px; font-weight: bold; color: {color}; text-align: right; margin-right: 20px;">
                {val}{unit}
            </div>
            
            <!-- Circle Icon -->
            <div style="width: 80px; height: 80px; border-radius: 50%; background-color: {color}; display: flex; align-items: center; justify-content: center; color: white; flex-shrink: 0; margin-right: 20px;">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                </svg>
            </div>
            
            <!-- Text Content -->
            <div style="flex: 2; text-align: right; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 32px; font-weight: bold; color: #000000; margin-bottom: 8px;">{cat}</div>
                <div style="font-size: {fs_insight}; color: {c_insight}; line-height: 1.4;">{desc}</div>
            </div>
        </div>
        '''
    # Since we are using HTML for the rows, we don't need SVG chart variables.
    svg_w, svg_h = 0, 0

    # ===== 5. HTML RENDER =====
    # Logistic Theme: White BG, Navy/Orange accents, clean layout
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
        font-family: {f_family};
        background-color: #FFFFFF;
        position: relative;
    }}
    
    /* Decorative Background Elements based on reference */
    .bg-shape-top {{
        position: absolute;
        top: -500px;
        left: 0;
        width: 400px;
        height: 150px;
        background: {c_title}; /* Navy */
        clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%);
        z-index: 0;
    }}
    .bg-shape-accent {{
        position: absolute;
        top: 0;
        left: 0;
        width: 150px;
        height: 150px;
        background: {c_accent}; /* Orange */
        clip-path: polygon(0 0, 80% 0, 0 80%);
        z-index: 1;
    }}
    .bg-shape-bottom {{
        position: absolute;
        bottom: 0;
        right: 0;
        width: 150px;
        height: 150px;
        background: {c_title};
        clip-path: polygon(100% 0, 100% 100%, 0% 100%);
        z-index: 0;
    }}
    
    .container {{
        position: relative;
        z-index: 10;
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 40px 80px 20px 80px;
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
        font-size: {fs_title};
        color: {c_accent}; /* Orange Title like 'Logistic' */
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .title-group h1 span {{
        color: {c_title}; /* Navy part like 'Company' */
    }}
    
    .subtitle {{
        font-size: {fs_sub};
        color: {c_sub};
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
        bottom: 10px;
        right: 5px;
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
    <div class="footer-mark"></div>

    <div class="container">
        <div class="header" style="justify-content: center; margin-bottom: 30px;">
            <div class="title-group" style="text-align: center;">
                <h1 style="color: #000000; font-size: 64px; text-transform: none;">{title}</h1>
                {subtitle if subtitle else ""}
            </div>

        </div>

        <div class="main-content" style="flex-direction: column; align-items: stretch; justify-content: center; padding: 0 40px; box-sizing: border-box; max-width: 1400px; margin: 0 auto; width: 100%;">
            {rows_html}
        </div>
    </div>

    </body>
    </html>
    """
    return html_code