def generate_waterfall_chart_slide_1(
    main_title: str = "Financial Performance Overview",
    subtitle: str = "Annual Revenue and Expenditure Breakdown",
    insight: str = "Operating expenses significantly impacted our net profit, though overall revenue grew.",
    categories: list = ["Starting Cash", "Sales", "Services", "Fixed Costs", "Variable Costs", "Taxes", "Ending Cash"],
    values: list = [5000, 3000, 1500, -2000, -1000, -500, 6000],
    is_total: list = [True, False, False, False, False, False, True],
    unit: str = "$",
    show_value: bool = True,
    positive_color: str = "#2ECC71",
    negative_color: str = "#E74C3C",
    total_color: str = "#3498DB",
    accent_color: str = "#3498DB",
    main_title_color: str = "#2C3E50",
    subtitle_color: str = "#7F8C8D",
    insight_text_color: str = "#34495E",
    y_axis_label: str = "Amount",
) -> str:
    """
    Generates a generic HTML slide with a Waterfall Chart.
    """
    title = main_title
    sub = subtitle
    insight_text = insight
    f_family = "Arial, sans-serif"
    
    # SVG CONFIG
    svg_w, svg_h = 1150, 650
    margin_top, margin_bottom = 60, 80
    margin_left, margin_right = 100, 50

    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    # DATA PROCESSING
    # Calculate cumulative sums to find min and max for Y-axis
    cumulative = 0
    max_val = 0
    min_val = 0
    
    start_values = []
    end_values = []
    
    for idx, (val, total_flag) in enumerate(zip(values, is_total)):
        if total_flag:
            start_values.append(0)
            end_values.append(val)
            cumulative = val
        else:
            start_values.append(cumulative)
            cumulative += val
            end_values.append(cumulative)
            
        max_val = max(max_val, start_values[-1], end_values[-1])
        min_val = min(min_val, start_values[-1], end_values[-1])

    # Add padding to max and min
    val_range = max_val - min_val if max_val != min_val else 100
    y_max = max_val + val_range * 0.1
    y_min = min_val - val_range * 0.1 if min_val < 0 else 0
    
    if y_max == y_min:
        y_max = y_min + 10

    # DRAW CHART
    chart_elements = ""

    # Grid lines
    num_grid_lines = 5
    for i in range(num_grid_lines + 1):
        y_ratio = i / num_grid_lines
        y_pos = svg_h - margin_bottom - (y_ratio * chart_h)
        value_label = y_min + (y_max - y_min) * y_ratio
        
        chart_elements += f'''
        <line x1="{margin_left}" y1="{y_pos}" x2="{svg_w - margin_right}" y2="{y_pos}" 
              stroke="#E5E7EB" stroke-width="1" stroke-dasharray="0"/>
        '''
        chart_elements += f'''
        <text x="{margin_left - 15}" y="{y_pos + 5}" font-family="{f_family}" font-size="16" 
              fill="#9CA3AF" text-anchor="end">{int(value_label) if value_label % 1 == 0 else f"{value_label:.1f}"}</text>
        '''

    # Zero line if applicable
    if y_min < 0 < y_max:
        zero_y = svg_h - margin_bottom - ((0 - y_min) / (y_max - y_min) * chart_h)
        chart_elements += f'''
        <line x1="{margin_left}" y1="{zero_y}" x2="{svg_w - margin_right}" y2="{zero_y}" 
              stroke="#9CA3AF" stroke-width="2"/>
        '''

    # Bars
    num_cats = len(categories)
    slot_width = chart_w / num_cats
    padding = slot_width * 0.2
    bar_width = slot_width - padding

    for i in range(num_cats):
        start_v = start_values[i]
        end_v = end_values[i]
        val = values[i]
        is_t = is_total[i]
        cat = categories[i]

        top_v = max(start_v, end_v)
        bottom_v = min(start_v, end_v)
        
        top_y = svg_h - margin_bottom - ((top_v - y_min) / (y_max - y_min) * chart_h)
        bottom_y = svg_h - margin_bottom - ((bottom_v - y_min) / (y_max - y_min) * chart_h)
        bar_h = bottom_y - top_y
        
        x_pos = margin_left + (i * slot_width) + (padding / 2)
        
        # Determine color
        if is_t:
            color = total_color
        elif val >= 0:
            color = positive_color
        else:
            color = negative_color

        chart_elements += f'''
        <rect x="{x_pos}" y="{top_y}" width="{bar_width}" height="{bar_h}" 
              fill="{color}" rx="2" ry="2" />
        '''
        
        # Connector lines
        if i < num_cats - 1 and not is_t and not is_total[i+1]:
            conn_y = svg_h - margin_bottom - ((end_v - y_min) / (y_max - y_min) * chart_h)
            next_x = margin_left + ((i + 1) * slot_width) + (padding / 2)
            chart_elements += f'''
            <line x1="{x_pos + bar_width}" y1="{conn_y}" x2="{next_x}" y2="{conn_y}" 
                  stroke="#9CA3AF" stroke-width="1" stroke-dasharray="4"/>
            '''

        if show_value:
            text_y = top_y - 10 if val >= 0 or is_t else bottom_y + 20
            chart_elements += f'''
            <text x="{x_pos + bar_width/2}" y="{text_y}" 
                  font-family="{f_family}" font-size="14" fill="{color}" font-weight="bold" text-anchor="middle">
                {unit}{abs(val)}
            </text>
            '''

        chart_elements += f'''
        <text x="{x_pos + bar_width/2}" y="{svg_h - margin_bottom + 30}" 
              font-family="{f_family}" font-size="14" fill="{main_title_color}" font-weight="bold" text-anchor="middle">
            {cat}
        </text>
        '''

    if y_axis_label:
        chart_elements += f'''
        <text transform="rotate(-90)" x="{-svg_h/2}" y="30" 
              font-family="{f_family}" font-size="18" fill="{subtitle_color}" text-anchor="middle">
            {y_axis_label}
        </text>
        '''

    legend_html = f'''
    <div style="display:flex; flex-wrap:wrap; gap:20px; margin-top:30px;">
        <span style="display:flex; align-items:center; gap:8px;">
            <span style="width:16px; height:16px; background-color:{positive_color}; border-radius:4px; display:inline-block;"></span>
            <span style="font-family:{f_family}; font-size:18px; color:{main_title_color}; font-weight:500;">Increase</span>
        </span>
        <span style="display:flex; align-items:center; gap:8px;">
            <span style="width:16px; height:16px; background-color:{negative_color}; border-radius:4px; display:inline-block;"></span>
            <span style="font-family:{f_family}; font-size:18px; color:{main_title_color}; font-weight:500;">Decrease</span>
        </span>
        <span style="display:flex; align-items:center; gap:8px;">
            <span style="width:16px; height:16px; background-color:{total_color}; border-radius:4px; display:inline-block;"></span>
            <span style="font-family:{f_family}; font-size:18px; color:{main_title_color}; font-weight:500;">Total</span>
        </span>
    </div>
    '''

    insight_html = f"""
    <div style="
        font-family: {f_family};
        font-size: 26px;
        color: {insight_text_color};
        line-height: 1.6;
        background: #F3F4F6;
        padding: 30px;
        border-left: 6px solid {accent_color};
        border-radius: 0 12px 12px 0;
        margin-bottom: 20px;">
        {insight_text}
    </div>
    """

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
    .bg-shape-top {{
        position: absolute; top: 0; left: 0; width: 400px; height: 150px; background: {main_title_color};
        clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%); z-index: 0;
    }}
    .bg-shape-accent {{
        position: absolute; top: 0; left: 0; width: 150px; height: 150px; background: {accent_color};
        clip-path: polygon(0 0, 80% 0, 0 80%); z-index: 1;
    }}
    .container {{
        position: relative; z-index: 10; display: flex; flex-direction: column; height: 100%;
        padding: 60px 80px 40px 80px; box-sizing: border-box;
    }}
    .header {{
        margin-bottom: 40px; padding-left: 350px; display: flex; justify-content: space-between; align-items: flex-end;
    }}
    .title-group h1 {{
        font-size: 64px; color: {main_title_color}; margin: 0; text-transform: uppercase; letter-spacing: 1px;
    }}
    .subtitle {{
        font-size: 28px; color: {subtitle_color}; margin-top: 10px; font-weight: 400;
    }}
    .main-content {{
        display: flex; flex: 1; gap: 60px; align-items: center;
    }}
    .left-panel {{
        flex: 1; display: flex; flex-direction: column; justify-content: center;
    }}
    .right-panel {{
        flex: 2; display: flex; justify-content: center; align-items: center;
    }}
    </style>
    </head>
    <body>
    <div class="bg-shape-top"></div>
    <div class="bg-shape-accent"></div>
    <div class="container">
        <div class="header">
            <div class="title-group">
                <h1>{title}</h1>
                <div class="subtitle">{sub}</div>
            </div>
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

def generate_waterfall_chart_slide_2(
    main_title: str = "Financial Performance Overview",
    subtitle: str = "Annual Revenue and Expenditure Breakdown",
    insight: str = "Operating expenses significantly impacted our net profit, though overall revenue grew.",
    categories: list = ["Starting Cash", "Sales", "Services", "Fixed Costs", "Variable Costs", "Taxes", "Ending Cash"],
    values: list = [5000, 3000, 1500, -2000, -1000, -500, 6000],
    is_total: list = [True, False, False, False, False, False, True],
    unit: str = "$",
    show_value: bool = True,
    positive_color: str = "#2ECC71",
    negative_color: str = "#E74C3C",
    total_color: str = "#3498DB",
    accent_color: str = "#3498DB",
    main_title_color: str = "#2C3E50",
    subtitle_color: str = "#7F8C8D",
    insight_text_color: str = "#34495E",
    y_axis_label: str = "Amount",
    second_insight: str = "",
    image_url: str = "https://online.uj.ac.za/hs-fs/hubfs/young-colleagues-discussing-business-and-price-cha-2023-11-27-05-05-15-utc.jpg?width=850&height=475&name=young-colleagues-discussing-business-and-price-cha-2023-11-27-05-05-15-utc.jpg",
) -> str:
    """
    Generates a generic HTML slide with a Waterfall Chart.
    """
    title = main_title
    sub = subtitle
    insight_text = insight
    f_family = "Arial, sans-serif"
    
    # SVG CONFIG
    svg_w, svg_h = 1150, 650
    margin_top, margin_bottom = 60, 80
    margin_left, margin_right = 100, 50

    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    # DATA PROCESSING
    # Calculate cumulative sums to find min and max for Y-axis
    cumulative = 0
    max_val = 0
    min_val = 0
    
    start_values = []
    end_values = []
    
    for idx, (val, total_flag) in enumerate(zip(values, is_total)):
        if total_flag:
            start_values.append(0)
            end_values.append(val)
            cumulative = val
        else:
            start_values.append(cumulative)
            cumulative += val
            end_values.append(cumulative)
            
        max_val = max(max_val, start_values[-1], end_values[-1])
        min_val = min(min_val, start_values[-1], end_values[-1])

    # Add padding to max and min
    val_range = max_val - min_val if max_val != min_val else 100
    y_max = max_val + val_range * 0.1
    y_min = min_val - val_range * 0.1 if min_val < 0 else 0
    
    if y_max == y_min:
        y_max = y_min + 10

    # DRAW CHART
    chart_elements = ""

    # Grid lines
    num_grid_lines = 5
    for i in range(num_grid_lines + 1):
        y_ratio = i / num_grid_lines
        y_pos = svg_h - margin_bottom - (y_ratio * chart_h)
        value_label = y_min + (y_max - y_min) * y_ratio
        
        chart_elements += f'''
        <line x1="{margin_left}" y1="{y_pos}" x2="{svg_w - margin_right}" y2="{y_pos}" 
              stroke="#E5E7EB" stroke-width="1" stroke-dasharray="0"/>
        '''
        chart_elements += f'''
        <text x="{margin_left - 15}" y="{y_pos + 5}" font-family="{f_family}" font-size="16" 
              fill="#9CA3AF" text-anchor="end">{int(value_label) if value_label % 1 == 0 else f"{value_label:.1f}"}</text>
        '''

    # Zero line if applicable
    if y_min < 0 < y_max:
        zero_y = svg_h - margin_bottom - ((0 - y_min) / (y_max - y_min) * chart_h)
        chart_elements += f'''
        <line x1="{margin_left}" y1="{zero_y}" x2="{svg_w - margin_right}" y2="{zero_y}" 
              stroke="#9CA3AF" stroke-width="2"/>
        '''

    # Bars
    num_cats = len(categories)
    slot_width = chart_w / num_cats
    padding = slot_width * 0.2
    bar_width = slot_width - padding

    for i in range(num_cats):
        start_v = start_values[i]
        end_v = end_values[i]
        val = values[i]
        is_t = is_total[i]
        cat = categories[i]

        top_v = max(start_v, end_v)
        bottom_v = min(start_v, end_v)
        
        top_y = svg_h - margin_bottom - ((top_v - y_min) / (y_max - y_min) * chart_h)
        bottom_y = svg_h - margin_bottom - ((bottom_v - y_min) / (y_max - y_min) * chart_h)
        bar_h = bottom_y - top_y
        
        x_pos = margin_left + (i * slot_width) + (padding / 2)
        
        # Determine color
        if is_t:
            color = total_color
        elif val >= 0:
            color = positive_color
        else:
            color = negative_color

        chart_elements += f'''
        <rect x="{x_pos}" y="{top_y}" width="{bar_width}" height="{bar_h}" 
              fill="{color}" rx="2" ry="2" />
        '''
        
        # Connector lines
        if i < num_cats - 1 and not is_t and not is_total[i+1]:
            conn_y = svg_h - margin_bottom - ((end_v - y_min) / (y_max - y_min) * chart_h)
            next_x = margin_left + ((i + 1) * slot_width) + (padding / 2)
            chart_elements += f'''
            <line x1="{x_pos + bar_width}" y1="{conn_y}" x2="{next_x}" y2="{conn_y}" 
                  stroke="#9CA3AF" stroke-width="1" stroke-dasharray="4"/>
            '''

        if show_value:
            text_y = top_y - 10 if val >= 0 or is_t else bottom_y + 20
            chart_elements += f'''
            <text x="{x_pos + bar_width/2}" y="{text_y}" 
                  font-family="{f_family}" font-size="14" fill="{color}" font-weight="bold" text-anchor="middle">
                {unit}{abs(val)}
            </text>
            '''

        chart_elements += f'''
        <text x="{x_pos + bar_width/2}" y="{svg_h - margin_bottom + 30}" 
              font-family="{f_family}" font-size="14" fill="{main_title_color}" font-weight="bold" text-anchor="middle">
            {cat}
        </text>
        '''

    if y_axis_label:
        chart_elements += f'''
        <text transform="rotate(-90)" x="{-svg_h/2}" y="30" 
              font-family="{f_family}" font-size="18" fill="{subtitle_color}" text-anchor="middle">
            {y_axis_label}
        </text>
        '''

    # DATA PROCESSING (Pie Chart - Hyper)
    import math
    hyper_chart_elements = ""
    pie_cx, pie_cy = svg_w / 2, svg_h / 2
    pie_r = min(svg_w, svg_h) / 2 * 0.8
    total_val = sum([abs(v) for v in values]) if sum([abs(v) for v in values]) > 0 else 1
    
    current_angle = 0
    colors_list = [positive_color, negative_color, total_color, accent_color, "#9B59B6", "#E67E22", "#1ABC9C"]
    
    for i in range(num_cats):
        val = abs(values[i])
        cat = categories[i]
        color = colors_list[i % len(colors_list)]
        
        angle = (val / total_val) * 2 * math.pi
        
        if angle == 0:
            continue
            
        if angle >= 2 * math.pi - 0.001:
            hyper_chart_elements += f'<circle cx="{pie_cx}" cy="{pie_cy}" r="{pie_r}" fill="{color}" />'
        else:
            x1 = pie_cx + pie_r * math.cos(current_angle)
            y1 = pie_cy + pie_r * math.sin(current_angle)
            
            next_angle = current_angle + angle
            x2 = pie_cx + pie_r * math.cos(next_angle)
            y2 = pie_cy + pie_r * math.sin(next_angle)
            
            large_arc = 1 if angle > math.pi else 0
            
            hyper_chart_elements += f'''
            <path d="M {pie_cx} {pie_cy} L {x1} {y1} A {pie_r} {pie_r} 0 {large_arc} 1 {x2} {y2} Z" fill="{color}" />
            '''
            
            if show_value:
                mid_angle = current_angle + angle / 2
                text_x = pie_cx + (pie_r * 0.6) * math.cos(mid_angle)
                text_y = pie_cy + (pie_r * 0.6) * math.sin(mid_angle)
                hyper_chart_elements += f'''
                <text x="{text_x}" y="{text_y}" font-family="{f_family}" font-size="24" fill="#FFFFFF" font-weight="bold" text-anchor="middle">
                    {abs(values[i])}
                </text>
                '''
                
            current_angle = next_angle

    legend_html = f'''
    <div style="display:flex; flex-wrap:wrap; gap:20px; margin-top:30px;">
        <span style="display:flex; align-items:center; gap:8px;">
            <span style="width:16px; height:16px; background-color:{positive_color}; border-radius:4px; display:inline-block;"></span>
            <span style="font-family:{f_family}; font-size:18px; color:{main_title_color}; font-weight:500;">Increase</span>
        </span>
        <span style="display:flex; align-items:center; gap:8px;">
            <span style="width:16px; height:16px; background-color:{negative_color}; border-radius:4px; display:inline-block;"></span>
            <span style="font-family:{f_family}; font-size:18px; color:{main_title_color}; font-weight:500;">Decrease</span>
        </span>
        <span style="display:flex; align-items:center; gap:8px;">
            <span style="width:16px; height:16px; background-color:{total_color}; border-radius:4px; display:inline-block;"></span>
            <span style="font-family:{f_family}; font-size:18px; color:{main_title_color}; font-weight:500;">Total</span>
        </span>
    </div>
    '''

    insight_html = f"""
    <div style="
        font-family: {f_family};
        font-size: 26px;
        color: {insight_text_color};
        line-height: 1.6;
        margin-bottom: 20px;">
        {insight_text}
    </div>
    """

    second_insight_html = f"""
    <div style="
        font-family: {f_family};
        font-size: 22px;
        color: {insight_text_color};
        line-height: 1.6;
        margin-top: 20px;
        text-align: center;
        font-style: italic;">
        {second_insight}
    </div>
    """

    bg_image_html = f'<img src="{image_url}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.15; z-index: 0;">' if image_url else ""

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
    .bg-shape-top {{
        position: absolute; top: 0; left: 0; width: 400px; height: 150px; background: {main_title_color};
        clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%); z-index: 0;
    }}
    .bg-shape-accent {{
        position: absolute; top: 0; left: 0; width: 150px; height: 150px; background: {accent_color};
        clip-path: polygon(0 0, 80% 0, 0 80%); z-index: 1;
    }}
    .container {{
        position: relative; z-index: 10; display: flex; flex-direction: column; height: 100%;
        padding: 60px 80px 40px 80px; box-sizing: border-box;
    }}
    .header {{
        margin-bottom: 40px; padding-left: 350px; display: flex; justify-content: space-between; align-items: flex-end;
    }}
    .title-group h1 {{
        font-size: 64px; color: {main_title_color}; margin: 0; text-transform: uppercase; letter-spacing: 1px;
    }}
    .subtitle {{
        font-size: 28px; color: {subtitle_color}; margin-top: 10px; font-weight: 400;
    }}
    .main-content {{
        display: flex; flex: 1; gap: 60px; align-items: center;
    }}
    .left-panel {{
        flex: 3; display: flex; justify-content: center; align-items: center;
    }}
    .right-panel {{
        flex: 1; display: flex; flex-direction: column; justify-content: center;
    }}
    </style>
    </head>
    <body>
    {bg_image_html}
    <div class="bg-shape-top"></div>
    <div class="bg-shape-accent"></div>
    <div class="container">
        <div class="header">
            <div class="title-group">
                <h1>{title}</h1>
                <div class="subtitle">{sub}</div>
            </div>
        </div>
        <div class="main-content">
            <div class="left-panel">
                <div style="display: flex; flex-direction: column; align-items: center; width: 100%;">
                    <div style="display: flex; flex-direction: row; justify-content: center; gap: 30px; width: 100%;">
                        <svg width="{svg_w * 0.65}" height="{svg_h * 1.3}" viewBox="0 0 {svg_w} {svg_h}">
                            {chart_elements}
                        </svg>
                        <svg width="{svg_w * 0.65}" height="{svg_h * 1.3}" viewBox="0 0 {svg_w} {svg_h}">
                            {hyper_chart_elements}
                        </svg>
                    </div>
                    {second_insight_html}
                </div>
            </div>
            <div class="right-panel">
                {insight_html}
                {legend_html}
            </div>
        </div>
    </div>
    </body>
    </html>
    """
    return html_code

def generate_waterfall_chart_slide_3(
    main_title: str = "Financial Performance Overview",
    subtitle: str = "Annual Revenue and Expenditure Breakdown",
    insight: str = "Operating expenses significantly impacted our net profit, though overall revenue grew.",
    categories: list = ["Starting Cash", "Sales", "Services", "Fixed Costs", "Variable Costs", "Taxes", "Ending Cash"],
    values: list = [5000, 3000, 1500, -2000, -1000, -500, 6000],
    is_total: list = [True, False, False, False, False, False, True],
    unit: str = "$",
    show_value: bool = True,
    positive_color: str = "#2ECC71",
    negative_color: str = "#E74C3C",
    total_color: str = "#3498DB",
    accent_color: str = "#3498DB",
    main_title_color: str = "#2C3E50",
    subtitle_color: str = "#7F8C8D",
    insight_text_color: str = "#34495E",
    y_axis_label: str = "Amount",
    second_insight: str = "This highlights potential areas for cost reduction next year.",
    image_url: str = "https://taca.com.vn/wp-content/uploads/2025/01/du-bao-tai-chinh-1200x675.jpg"
) -> str:
    """
    Generates a generic HTML slide with a Waterfall Chart.
    """
    title = main_title
    sub = subtitle
    insight_text = insight
    f_family = "Arial, sans-serif"
    
    # SVG CONFIG
    svg_w, svg_h = 1150, 650
    margin_top, margin_bottom = 60, 80
    margin_left, margin_right = 100, 50

    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    # DATA PROCESSING
    # Calculate cumulative sums to find min and max for Y-axis
    cumulative = 0
    max_val = 0
    min_val = 0
    
    start_values = []
    end_values = []
    
    for idx, (val, total_flag) in enumerate(zip(values, is_total)):
        if total_flag:
            start_values.append(0)
            end_values.append(val)
            cumulative = val
        else:
            start_values.append(cumulative)
            cumulative += val
            end_values.append(cumulative)
            
        max_val = max(max_val, start_values[-1], end_values[-1])
        min_val = min(min_val, start_values[-1], end_values[-1])

    # Add padding to max and min
    val_range = max_val - min_val if max_val != min_val else 100
    y_max = max_val + val_range * 0.1
    y_min = min_val - val_range * 0.1 if min_val < 0 else 0
    
    if y_max == y_min:
        y_max = y_min + 10

    # DRAW CHART
    chart_elements = ""

    # Grid lines
    num_grid_lines = 5
    for i in range(num_grid_lines + 1):
        y_ratio = i / num_grid_lines
        y_pos = svg_h - margin_bottom - (y_ratio * chart_h)
        value_label = y_min + (y_max - y_min) * y_ratio
        
        chart_elements += f'''
        <line x1="{margin_left}" y1="{y_pos}" x2="{svg_w - margin_right}" y2="{y_pos}" 
              stroke="#E5E7EB" stroke-width="1" stroke-dasharray="0"/>
        '''
        chart_elements += f'''
        <text x="{margin_left - 15}" y="{y_pos + 5}" font-family="{f_family}" font-size="16" 
              fill="#9CA3AF" text-anchor="end">{int(value_label) if value_label % 1 == 0 else f"{value_label:.1f}"}</text>
        '''

    # Zero line if applicable
    if y_min < 0 < y_max:
        zero_y = svg_h - margin_bottom - ((0 - y_min) / (y_max - y_min) * chart_h)
        chart_elements += f'''
        <line x1="{margin_left}" y1="{zero_y}" x2="{svg_w - margin_right}" y2="{zero_y}" 
              stroke="#9CA3AF" stroke-width="2"/>
        '''

    # Bars
    num_cats = len(categories)
    slot_width = chart_w / num_cats
    padding = slot_width * 0.2
    bar_width = slot_width - padding

    for i in range(num_cats):
        start_v = start_values[i]
        end_v = end_values[i]
        val = values[i]
        is_t = is_total[i]
        cat = categories[i]

        top_v = max(start_v, end_v)
        bottom_v = min(start_v, end_v)
        
        top_y = svg_h - margin_bottom - ((top_v - y_min) / (y_max - y_min) * chart_h)
        bottom_y = svg_h - margin_bottom - ((bottom_v - y_min) / (y_max - y_min) * chart_h)
        bar_h = bottom_y - top_y
        
        x_pos = margin_left + (i * slot_width) + (padding / 2)
        
        # Determine color
        if is_t:
            color = total_color
        elif val >= 0:
            color = positive_color
        else:
            color = negative_color

        chart_elements += f'''
        <rect x="{x_pos}" y="{top_y}" width="{bar_width}" height="{bar_h}" 
              fill="{color}" rx="2" ry="2" />
        '''
        
        # Connector lines
        if i < num_cats - 1 and not is_t and not is_total[i+1]:
            conn_y = svg_h - margin_bottom - ((end_v - y_min) / (y_max - y_min) * chart_h)
            next_x = margin_left + ((i + 1) * slot_width) + (padding / 2)
            chart_elements += f'''
            <line x1="{x_pos + bar_width}" y1="{conn_y}" x2="{next_x}" y2="{conn_y}" 
                  stroke="#9CA3AF" stroke-width="1" stroke-dasharray="4"/>
            '''

        if show_value:
            text_y = top_y - 10 if val >= 0 or is_t else bottom_y + 20
            chart_elements += f'''
            <text x="{x_pos + bar_width/2}" y="{text_y}" 
                  font-family="{f_family}" font-size="14" fill="{color}" font-weight="bold" text-anchor="middle">
                {unit}{abs(val)}
            </text>
            '''

        chart_elements += f'''
        <text x="{x_pos + bar_width/2}" y="{svg_h - margin_bottom + 30}" 
              font-family="{f_family}" font-size="14" fill="{main_title_color}" font-weight="bold" text-anchor="middle">
            {cat}
        </text>
        '''

    if y_axis_label:
        chart_elements += f'''
        <text transform="rotate(-90)" x="{-svg_h/2}" y="30" 
              font-family="{f_family}" font-size="18" fill="{subtitle_color}" text-anchor="middle">
            {y_axis_label}
        </text>
        '''

    # DATA PROCESSING (Pie Chart - Hyper)
    import math
    hyper_chart_elements = ""
    pie_cx, pie_cy = svg_w / 2, svg_h / 2
    pie_r = min(svg_w, svg_h) / 2 * 0.8
    total_val = sum([abs(v) for v in values]) if sum([abs(v) for v in values]) > 0 else 1
    
    current_angle = 0
    colors_list = [positive_color, negative_color, total_color, accent_color, "#9B59B6", "#E67E22", "#1ABC9C"]
    
    for i in range(num_cats):
        val = abs(values[i])
        cat = categories[i]
        color = colors_list[i % len(colors_list)]
        
        angle = (val / total_val) * 2 * math.pi
        
        if angle == 0:
            continue
            
        if angle >= 2 * math.pi - 0.001:
            hyper_chart_elements += f'<circle cx="{pie_cx}" cy="{pie_cy}" r="{pie_r}" fill="{color}" />'
        else:
            x1 = pie_cx + pie_r * math.cos(current_angle)
            y1 = pie_cy + pie_r * math.sin(current_angle)
            
            next_angle = current_angle + angle
            x2 = pie_cx + pie_r * math.cos(next_angle)
            y2 = pie_cy + pie_r * math.sin(next_angle)
            
            large_arc = 1 if angle > math.pi else 0
            
            hyper_chart_elements += f'''
            <path d="M {pie_cx} {pie_cy} L {x1} {y1} A {pie_r} {pie_r} 0 {large_arc} 1 {x2} {y2} Z" fill="{color}" />
            '''
            
            if show_value:
                mid_angle = current_angle + angle / 2
                text_x = pie_cx + (pie_r * 0.6) * math.cos(mid_angle)
                text_y = pie_cy + (pie_r * 0.6) * math.sin(mid_angle)
                hyper_chart_elements += f'''
                <text x="{text_x}" y="{text_y}" font-family="{f_family}" font-size="24" fill="#FFFFFF" font-weight="bold" text-anchor="middle">
                    {abs(values[i])}
                </text>
                '''
                
            current_angle = next_angle

    legend_html = f'''
    <div style="display:flex; flex-direction:column; gap:20px; align-items:flex-start;">
        <span style="display:flex; align-items:center; gap:8px;">
            <span style="width:16px; height:16px; background-color:{positive_color}; border-radius:4px; display:inline-block;"></span>
            <span style="font-family:{f_family}; font-size:18px; color:{main_title_color}; font-weight:500;">Increase</span>
        </span>
        <span style="display:flex; align-items:center; gap:8px;">
            <span style="width:16px; height:16px; background-color:{negative_color}; border-radius:4px; display:inline-block;"></span>
            <span style="font-family:{f_family}; font-size:18px; color:{main_title_color}; font-weight:500;">Decrease</span>
        </span>
        <span style="display:flex; align-items:center; gap:8px;">
            <span style="width:16px; height:16px; background-color:{total_color}; border-radius:4px; display:inline-block;"></span>
            <span style="font-family:{f_family}; font-size:18px; color:{main_title_color}; font-weight:500;">Total</span>
        </span>
    </div>
    '''

    waterfall_insight_top = f"""<div style="font-family:{f_family}; font-size:22px; color:{insight_text_color}; text-align:center; margin-bottom:20px; z-index:10; position:relative;">{insight_text}</div>"""
    waterfall_insight_bottom = f"""<div style="font-family:{f_family}; font-size:20px; color:{insight_text_color}; text-align:center; margin-top:20px; font-style:italic; z-index:10; position:relative;">{second_insight}</div>"""
    pie_insight_top = f"""<div style="font-family:{f_family}; font-size:22px; color:{insight_text_color}; text-align:center; margin-bottom:20px; z-index:10; position:relative;">Cost proportions</div>"""
    pie_insight_bottom = f"""<div style="font-family:{f_family}; font-size:20px; color:{insight_text_color}; text-align:center; margin-top:20px; font-style:italic; z-index:10; position:relative;">Visualizing the magnitude of components.</div>"""

    bg_image_html = f'<img src="{image_url}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.15; z-index: 0;">' if image_url else ""

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
    .bg-shape-top {{
        position: absolute; top: 0; left: 0; width: 400px; height: 150px; background: {main_title_color};
        clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%); z-index: 0;
    }}
    .bg-shape-accent {{
        position: absolute; top: 0; left: 0; width: 150px; height: 150px; background: {accent_color};
        clip-path: polygon(0 0, 80% 0, 0 80%); z-index: 1;
    }}
    .container {{
        position: relative; z-index: 10; display: flex; flex-direction: column; height: 100%;
        padding: 60px 80px 40px 80px; box-sizing: border-box;
    }}
    .header {{
        margin-bottom: 40px; padding-left: 350px; display: flex; justify-content: space-between; align-items: flex-end;
    }}
    .title-group h1 {{
        font-size: 64px; color: {main_title_color}; margin: 0; text-transform: uppercase; letter-spacing: 1px;
    }}
    .subtitle {{
        font-size: 28px; color: {subtitle_color}; margin-top: 10px; font-weight: 400;
    }}
    .main-content {{
        display: flex; flex: 1; flex-direction: row; justify-content: center; align-items: center; width: 100%; gap: 20px;
    }}
    .chart-panel {{
        display: flex; flex-direction: column; align-items: center; width: 42%;
    }}
    .legend-panel {{
        display: flex; flex-direction: column; align-items: center; justify-content: center; width: 16%;
    }}
    </style>
    </head>
    <body>
    {bg_image_html}
    <div class="bg-shape-top"></div>
    <div class="bg-shape-accent"></div>
    <div class="container">
        <div class="header">
            <div class="title-group">
                <h1>{title}</h1>
                <div class="subtitle">{sub}</div>
            </div>
        </div>
        <div class="main-content">
            <div class="chart-panel">
                {waterfall_insight_top}
                <div style="background-color:rgba(255,255,255,0.9); border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.1); padding:60px 20px; width:100%; box-sizing:border-box; border: 1px solid rgba(0,0,0,0.05);">
                    <svg width="100%" viewBox="0 0 {svg_w} {svg_h}">
                        {chart_elements}
                    </svg>
                </div>
                {waterfall_insight_bottom}
            </div>
            <div class="legend-panel">
                {legend_html}
            </div>
            <div class="chart-panel">
                {pie_insight_top}
                <div style="background-color:rgba(255,255,255,0.9); border-radius:12px; box-shadow:0 4px 15px rgba(0,0,0,0.1); padding:60px 20px; width:100%; box-sizing:border-box; border: 1px solid rgba(0,0,0,0.05);">
                    <svg width="100%" viewBox="0 0 {svg_w} {svg_h}">
                        {hyper_chart_elements}
                    </svg>
                </div>
                {pie_insight_bottom}
            </div>
        </div>
    </div>
    </body>
    </html>
    """
    return html_code

