def generate_treemap_chart_slide_1(
    main_title="Stock Market Distribution by Sector",
    subtitle="Global Equity Markets – Q1 2026 Analysis",
    insight=(
        "Technology remains the dominant force, led by Software and Hardware. "
        "Finance follows closely, showing a balanced distribution across Banking and Insurance. "
        "Consumer Goods shows significant growth in E-commerce segments."
    ),
    unit = "B",
    show_value = True,
    show_label = True,
    data_label_format = "{label}: ${value}B",
    padding = 4,
    border_radius = 4,
    base_color = "#1E3A8A",
    accent_color = "#3B82F6",
    text_color = "#FFFFFF",
    border_color = "#1E293B",
    data = [
        {
            "label": "Technology",
            "value": 450,
            "children": [
                {"label": "Software", "value": 250},
                {"label": "Hardware", "value": 150},
                {"label": "Cloud", "value": 50}
            ]
        },
        {
            "label": "Finance",
            "value": 300,
            "children": [
                {"label": "Banking", "value": 180},
                {"label": "Insurance", "value": 120}
            ]
        },
        {
            "label": "Consumer",
            "value": 250,
            "children": [
                {"label": "Retail", "value": 150},
                {"label": "E-commerce", "value": 100}
            ]
        }
    ],
    font_family="'Inter', sans-serif",
    main_title_color="#FFFFFF",
    subtitle_color="#94A3B8",
    insight_text_color="#CBD5E1",
    main_title_font_size="64px",
    subtitle_font_size="28px",
    insight_font_size="26px"
) -> str:
    """
    Generates a professional treemap chart slide with a financial theme.
    The layout is optimized for high-density hierarchical data visualization.
    """

    # ===== 1. PREPARE DATA & OPTIONS =====
    data = data_input.get("data", [])
    options = chart_options
    unit = options.get("unit", "")
    show_value = options.get("show_value", True)
    show_label = options.get("show_label", True)
    label_format = options.get("data_label_format", "{label}: {value}")
    
    colors = options.get("colors", {})
    base_color = colors.get("base_color", "#1E3A8A")
    accent_color_val = colors.get("accent_color", "#3B82F6")
    text_color = colors.get("text_color", "#FFFFFF")
    border_color = colors.get("border_color", "#FFFFFF")
    padding = options.get("padding", 4)
    radius = options.get("border_radius", 4)

    total_value = sum(item.get("value", 0) for item in data)

    # ===== 2. TREEMAP LOGIC (SLICE & DICE) =====
    # Canvas dimensions for the SVG
    canvas_w = 1100
    canvas_h = 550
    
    svg_elements = []
    
    current_x = 0
    for i, parent in enumerate(data):
        p_label = parent.get("label", "")
        p_value = parent.get("value", 0)
        children = parent.get("children", [])
        
        # Calculate parent width based on proportion
        p_width = (p_value / total_value * canvas_w) if total_value > 0 else 0
        
        # Draw parent background grouping (slightly different shades)
        p_bg_color = base_color if i % 2 == 0 else "#1e40af"
        
        # Process children
        child_y = 0
        child_total = sum(c.get("value", 0) for c in children)
        
        for c_idx, child in enumerate(children):
            c_label = child.get("label", "")
            c_value = child.get("value", 0)
            c_height = (c_value / child_total * canvas_h) if child_total > 0 else 0
            
            # Formatting text
            display_text = label_format.replace("{label}", c_label).replace("{value}", str(c_value)).replace("{unit}", unit)
            
            # SVG Rect for leaf node
            svg_elements.append(f"""
            <g>
                <rect x="{current_x + padding}" y="{child_y + padding}" 
                      width="{p_width - 2*padding}" height="{c_height - 2*padding}" 
                      fill="{p_bg_color}" stroke="{border_color}" stroke-width="1" rx="{radius}" />
                <text x="{current_x + p_width/2}" y="{child_y + c_height/2}" 
                      fill="{text_color}" font-size="16" font-weight="600"
                      text-anchor="middle" dominant-baseline="middle" style="pointer-events: none;">
                    {display_text if show_label else ""}
                </text>
            </g>
            """)
            child_y += c_height
            
        current_x += p_width

    treemap_svg_html = f"""
    <div style="width: 1100px; height: 550px; margin-bottom: 30px;">
        <svg width="1100" height="550" viewBox="0 0 1100 550">
            {"".join(svg_elements)}
        </svg>
    </div>
    """

    # ===== 3. TABLE GENERATION =====
    table_rows = ""
    for item in data:
        table_rows += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 15px; font-weight: bold; color: {accent_color_val};">{item['label']}</td>
            <td style="padding: 15px; text-align: right; color: white;">{item['value']} {unit}</td>
            <td style="padding: 15px; text-align: right; color: #94A3B8;">{round(item['value']/total_value*100, 1)}%</td>
        </tr>
        """

    table_html = f"""
    <div style="position:relative; width:1100px; max-width:100vw; overflow-x:auto; margin:0 auto;">
        <table style="width:100%; min-width:600px; border-collapse:collapse; background:rgba(30,41,59,0.5); font-size:20px;">
            <thead>
                <tr style="background:#1E293B; color:#94A3B8; text-align:left;">
                    <th style="padding:15px;">Sector</th>
                    <th style="padding:15px; text-align:right;">Market Value</th>
                    <th style="padding:15px; text-align:right;">% Share</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """

    # ===== 4. FINAL HTML RENDER =====
    return f"""
    <html>
    <body style="margin: 0; padding: 60px; width: 1920px; height: 1080px; 
                 background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                 font-family: {font_family}; color: white; box-sizing: border-box; overflow: hidden;">
        
        <div style="margin-bottom: 60px; border-left: 10px solid {accent_color}; padding-left: 30px;">
            <h1 style="margin: 0; font-size: {main_title_font_size}; color: {main_title_color}; text-transform: uppercase; letter-spacing: 2px;">
                {main_title}
            </h1>
            <div style="font-size: {subtitle_font_size}; color: {subtitle_color}; margin-top: 10px;">
                {subtitle}
            </div>
        </div>

        <div style="display: flex; gap: 60px; align-items: flex-start;">
            <div style="width: 550px; background: rgba(255,255,255,0.05); padding: 40px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 20px; color: {accent_color}; font-weight: bold; margin-bottom: 20px; text-transform: uppercase;">Key Insights</div>
                <div style="font-size: {insight_font_size}; color: {insight_text_color}; line-height: 1.6; font-style: italic;">
                    "{insight}"
                </div>
            </div>

            <div style="flex: 1;">
                {treemap_svg_html}
                {table_html}
            </div>
        </div>

        <div style="position: absolute; bottom: 40px; right: 60px; font-size: 18px; color: #475569;">
            Wardiere Finance | Internal Strategy Document
        </div>
    </body>
    </html>
    """

def generate_treemap_chart_slide_2(
    main_title="Energy Distribution Across Physical Systems",
    subtitle="Physics Systems Analysis – Q1 2026",
    insight=(
        "Cơ năng chiếm tỷ trọng lớn nhất (50%), trong đó động năng dẫn đầu nhờ các hệ thống tịnh tiến. "
        "Nhiệt năng tập trung vào quá trình dẫn nhiệt trong kim loại. "
        "Điện năng duy trì ổn định với sự phân hóa rõ rệt giữa dòng điện xoay chiều và một chiều."
    ),
    unit= "J",
    show_value= True,
    show_label= True,
    data_label_format= "{label}: {value}J",
    padding= 6,
    border_radius= 4,
    base_color= "#1E3A8A",
    accent_color = "#E2E045",
    text_color = "#FFFFFF",
    border_color = "#FFFFFF",
    data=[
            {
                "label": "Mechanical Energy",
                "value": 500,
                "children": [
                    {
                        "label": "Kinetic Energy",
                        "value": 280,
                        "children": [
                            {"label": "Translational", "value": 150},
                            {"label": "Rotational", "value": 130}
                        ]
                    },
                    {
                        "label": "Potential Energy",
                        "value": 220,
                        "children": [
                            {
                                "label": "Gravitational",
                                "value": 140,
                                "children": [
                                    {"label": "Near Surface", "value": 90},
                                    {"label": "High Altitude", "value": 50}
                                ]
                            },
                            {
                                "label": "Elastic",
                                "value": 80,
                                "children": [
                                    {"label": "Spring Systems", "value": 50},
                                    {"label": "Material Deformation", "value": 30}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "label": "Thermal Energy",
                "value": 300,
                "children": [
                    {
                        "label": "Heat Transfer",
                        "value": 300,
                        "children": [
                            {
                                "label": "Conduction",
                                "value": 120,
                                "children": [
                                    {"label": "Metals", "value": 70},
                                    {"label": "Non-metals", "value": 50}
                                ]
                            },
                            {
                                "label": "Convection",
                                "value": 100,
                                "children": [
                                    {"label": "Natural", "value": 60},
                                    {"label": "Forced", "value": 40}
                                ]
                            },
                            {
                                "label": "Radiation",
                                "value": 80,
                                "children": [
                                    {"label": "Infrared", "value": 50},
                                    {"label": "Other EM Waves", "value": 30}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "label": "Electrical Energy",
                "value": 200,
                "children": [
                    {
                        "label": "Electric Circuits",
                        "value": 200,
                        "children": [
                            {
                                "label": "Current",
                                "value": 120,
                                "children": [
                                    {"label": "DC", "value": 70},
                                    {"label": "AC", "value": 50}
                                ]
                            },
                            {
                                "label": "Voltage",
                                "value": 80,
                                "children": [
                                    {"label": "Low Voltage", "value": 50},
                                    {"label": "High Voltage", "value": 30}
                                ]
                            }
                        ]
                    }
                ]
            }
        ],
    font_family="Inter, Arial, sans-serif",
    main_title_color="#1E3A8A",
    subtitle_color="#64748B",
    insight_text_color="#334155",
    main_title_font_size="64px",
    subtitle_font_size="28px",
    insight_font_size="26px"
) -> str:
    """
    Generates a professional Physics-themed Treemap slide.
    The layout uses a 2-column approach for insight and chart/table content.
    """

    # ===== 1. GET DATA & OPTIONS =====
    data = data_input.get("data", [])
    options = chart_options
    unit = options.get("unit", "")
    show_value = options.get("show_value", True)
    show_label = options.get("show_label", True)
    padding = options.get("padding", 4)
    colors = options.get("colors", {})
    
    base_color = colors.get("base_color", "#1E3A8A")
    accent_color_hex = colors.get("accent_color", "#E2E045")
    rect_text_color = colors.get("text_color", "#FFFFFF")
    border_color = colors.get("border_color", "#FFFFFF")

    # ===== 2. CALCULATE TREEMAP RECTANGLES (SLICE & DICE) =====
    rects_html = ""
    chart_w = 1100
    chart_h = 550

    shades = ["#1E3A8A", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD"]

    # Stack: mỗi phần tử là 1 vùng cần vẽ
    stack = [{
        "items": data,
        "x": 0,
        "y": 0,
        "w": chart_w,
        "h": chart_h,
        "depth": 0,
        "vertical": True
    }]

    while stack:
        node = stack.pop()

        items = node["items"]
        x = node["x"]
        y = node["y"]
        w = node["w"]
        h = node["h"]
        depth = node["depth"]
        vertical = node["vertical"]

        total = sum(i.get("value", 0) for i in items)
        if total == 0:
            continue

        offset = 0

        for item in items:
            val = item.get("value", 0)
            label = item.get("label", "")
            children = item.get("children", [])

            ratio = val / total

            if vertical:
                dw = w * ratio
                dh = h
                dx = x + offset
                dy = y
                offset += dw
            else:
                dw = w
                dh = h * ratio
                dx = x
                dy = y + offset
                offset += dh

            color = shades[depth % len(shades)]

            # Draw rect
            rects_html += f"""
            <rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" 
                fill="{color}" stroke="{border_color}" stroke-width="2" rx="{options.get('border_radius', 4)}" />
            """

            # Inner box
            inner_x = dx + padding
            inner_y = dy + padding
            inner_w = max(0, dw - 2 * padding)
            inner_h = max(0, dh - 2 * padding)

            # Draw label nếu đủ chỗ
            if show_label and inner_w > 40 and inner_h > 20:
                val_text = f"{val}{unit}" if show_value else ""
                
                # Tính font size tối ưu theo cả chiều rộng (chia 5-6 ký tự) và chiều cao
                fs_h = int(inner_h // 5)
                fs_w = int(inner_w // 4)  # ước lượng cho độ rộng chữ
                fs = min(20, max(10, min(fs_h, fs_w)))

                # Tách từ để đẩy xuống dòng (word wrapping) cho SVG
                words = label.split()
                tspan_html = ""
                line_height = fs + 2
                
                # Chiều cao offset ban đầu để căn giữa toàn bộ khối text
                # Giả sử có val_text ở dưới, thêm 1 dòng nữa
                total_lines = len(words) + (1 if val_text else 0)
                start_y_offset = - (total_lines - 1) * line_height / 2
                
                for j, word in enumerate(words):
                    t_dy = start_y_offset if j == 0 else line_height
                    tspan_html += f'<tspan x="{dx + dw/2}" dy="{t_dy}">{word}</tspan>'
                
                if val_text:
                    tspan_html += f'<tspan x="{dx + dw/2}" dy="{line_height}" fill="{accent_color_hex}" font-size="{fs - 2}px" font-weight="normal">{val_text}</tspan>'

                rects_html += f"""
                <text x="{dx + dw/2}" y="{dy + dh/2}" 
                    fill="{rect_text_color}" font-size="{fs}px" font-weight="bold"
                    text-anchor="middle" dominant-baseline="middle">
                    {tspan_html}
                </text>
                """

            # Push children vào stack (để xử lý tiếp)
            if children:
                stack.append({
                    "items": children,
                    "x": inner_x,
                    "y": inner_y,
                    "w": inner_w,
                    "h": inner_h,
                    "depth": depth + 1,
                    "vertical": not vertical  # đảo chiều
                })    

    # ===== 3. CONSTRUCT COMPONENTS =====
    
    # SVG Container
    treemap_svg_html = f"""
    <div style="width: 1100px; height: 550px; background: #F8FAFC; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
        <svg width="100%" height="100%" viewBox="0 0 1100 550">
            {rects_html}
        </svg>
    </div>
    """

    # Table Component
    total_val = sum(item.get('value', 0) for item in data)
    if total_val == 0:
        total_val = 1  # Avoid division by zero
        
    table_rows = ""
    for item in data:
        table_rows += f"""
        <tr style="border-bottom: 1px solid #E2E8F0;">
            <td style="padding: 15px; font-weight: 600; color: #1E3A8A;">{item.get('label')}</td>
            <td style="padding: 15px; text-align: right; color: #334155;">{item.get('value')} {unit}</td>
            <td style="padding: 15px; text-align: right; color: #64748B;">{round(item.get('value', 0)/total_val*100, 1)}%</td>
        </tr>
        """

    table_html = f"""
    <div style="margin-top: 40px; width: 1100px;">
        <table style="width: 1100px; table-layout: fixed; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; font-size: 22px;">
            <thead>
                <tr style="background: {base_color}; color: white; text-align: left;">
                    <th style="padding: 15px;">Physical System Category</th>
                    <th style="padding: 15px; text-align: right;">Energy Value</th>
                    <th style="padding: 15px; text-align: right;">Distribution (%)</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """

    # ===== 4. FINAL ASSEMBLY =====
    full_html = f"""
    <html>
    <body style="margin: 0; padding: 60px; width: 1920px; height: 1080px; font-family: {font_family}; background-color: #FFFFFF; color: #1E293B; box-sizing: border-box; overflow: hidden;">
        
        <!-- Header Section -->
        <div style="margin-bottom: 50px; border-left: 12px solid {accent_color_hex}; padding-left: 30px;">
            <div style="font-size: {main_title_font_size}; font-weight: 800; color: {main_title_color}; text-transform: uppercase; letter-spacing: -1px; margin-bottom: 10px;">
                {main_title}
            </div>
            <div style="font-size: {subtitle_font_size}; color: {subtitle_color}; font-weight: 400;">
                {subtitle}
            </div>
        </div>

        <!-- Main Content Section -->
        <div style="display: flex; gap: 60px; align-items: flex-start;">
            
            <!-- Left Column: Insight -->
            <div style="width: 500px; background: #F1F5F9; padding: 40px; border-radius: 20px; border-top: 6px solid {base_color};">
                <div style="font-size: 32px; font-weight: 700; color: {base_color}; margin-bottom: 25px; display: flex; align-items: center; gap: 15px;">
                    <span style="width: 40px; height: 40px; background: {base_color}; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px;">i</span>
                    Key Insights
                </div>
                <div style="font-size: {insight_font_size}; color: {insight_text_color}; line-height: 1.6; font-style: italic;">
                    "{insight}"
                </div>
                <div style="margin-top: 150px; border-top: 2px dashed #CBD5E1; padding-top: 30px;">
                    <div style="font-size: 20px; color: #64748B; font-weight: 600;">System Reference</div>
                    <div style="font-size: 18px; color: #94A3B8;">Ref: PHY-TREEMAP-2026-V1</div>
                </div>
            </div>

            <!-- Right Column: Visuals -->
            <div style="flex: 1;">
                {treemap_svg_html}
                {table_html}
            </div>
            
        </div>

        <!-- Decorative Footer Element -->
        <div style="position: absolute; bottom: 0; right: 0; width: 100%; height: 10px; background: {accent_color_hex};"></div>

    </body>
    </html>
    """
    
    return full_html

def generate_treemap_chart_slide_3(
    main_title="Phân Bổ Tài Nguyên Giáo Dục",
    subtitle="Báo cáo tổng kết học kỳ I - Năm học 2025-2026",
    insight=(
        "Khối Khoa học và Ngôn ngữ chiếm tỷ trọng lớn nhất trong ngân sách (tổng 70%). "
        "Trong đó, tài liệu đọc hiểu là hạng mục ưu tiên cao nhất trong bộ môn Ngôn ngữ."
    ),
    unit = "%",
    show_value = True,
    show_label = True,
    data_label_format = "{label}: {value}%",
    padding = 4,
    border_radius = 8,
    base_color = "#1a948e",
    text_color = "#ffffff",
    border_color = "#fbc02d",
    data = [
            {
                "label": "Ngôn ngữ",
                "value": 40,
                "children": [
                    {"label": "Đọc hiểu", "value": 20},
                    {"label": "Viết sáng tạo", "value": 15},
                    {"label": "Từ vựng", "value": 5}
                ]
            },
            {
                "label": "Khoa học",
                "value": 30,
                "children": [
                    {"label": "Vật lý", "value": 15},
                    {"label": "Sinh học", "value": 15}
                ]
            },
            {
                "label": "Nghệ thuật",
                "value": 20,
                "children": [
                    {"label": "Hội họa", "value": 12},
                    {"label": "Âm nhạc", "value": 8}
                ]
            },
            {
                "label": "Thể chất",
                "value": 10
            }
        ],
    font_family="'Poppins', 'Segoe UI', sans-serif",
    accent_color="#fbc02d",
    main_title_color="#e5533d",
    subtitle_color="#1a948e",
    insight_text_color="#333333",
    main_title_font_size="64px",
    subtitle_font_size="28px",
    insight_font_size="24px"
) -> str:
    """
    Sinh HTML cho slide biểu đồ Treemap với phong cách học thuật.
    Hỗ trợ dữ liệu phân cấp (2 cấp) và tự động tính toán layout rectangle.
    """

    # ===== 1. GET DATA & OPTIONS =====
    # Parameters are now passed directly, no need to extract from dictionaries
    radius = border_radius

    # Bảng màu luân phiên cho các category lớn
    color_palette = [base_color, "#1a948e", "#4db6ac", "#80cbc4", "#b2dfdb"]
    accent_palette = ["#e5533d", "#ff7043", "#ff8a65", "#ffab91"]

    # ===== 2. CALCULATE TREEMAP LAYOUT (Slice-and-Dice) =====
    total_val = sum(item.get("value", 0) for item in data)
    total_val = sum(item.get("value", 0) for item in data)
    
    # Canvas area
    canvas_w = 1100
    canvas_h = 600
    
    rects_html = ""
    current_x = 0
    
    for i, parent in enumerate(data):
        p_label = parent.get("label", "")
        p_value = parent.get("value", 0)
        children = parent.get("children", [])
        
        # Calculate parent width based on ratio
        p_width = (p_value / total_val) * canvas_w if total_val > 0 else 0
        p_color = color_palette[i % len(color_palette)]
        
        # Parent group background (optional border)
        rects_html += f"""
        <rect x="{current_x}" y="0" width="{p_width}" height="{canvas_h}" 
              fill="none" stroke="{accent_color}" stroke-width="2" rx="{radius}"/>
        """
        
        if not children:
            # Nếu không có con, vẽ 1 khối duy nhất
            display_text = f"{p_label} ({p_value}{unit})"
            rects_html += f"""
            <g>
                <rect x="{current_x + padding}" y="{padding}" width="{p_width - 2*padding}" height="{canvas_h - 2*padding}" 
                      fill="{p_color}" rx="{radius}"/>
                <text x="{current_x + p_width/2}" y="{canvas_h/2}" fill="{text_color}" 
                      font-size="20" text-anchor="middle" dominant-baseline="middle" font-weight="bold">
                    {p_label if show_label else ''}
                </text>
                <text x="{current_x + p_width/2}" y="{canvas_h/2 + 25}" fill="{text_color}" 
                      font-size="16" text-anchor="middle" dominant-baseline="middle">
                    {str(p_value) + unit if show_value else ''}
                </text>
            </g>
            """
        else:
            # Chia khối con theo chiều dọc (Vertical Slice)
            current_y = padding
            child_total = sum(c.get("value", 0) for c in children)
            
            for j, child in enumerate(children):
                c_label = child.get("label", "")
                c_value = child.get("value", 0)
                c_height = (c_value / child_total) * (canvas_h - 2*padding) if child_total > 0 else 0
                
                # Biến đổi màu cho con (đậm nhạt)
                c_fill = p_color if j % 2 == 0 else accent_palette[i % len(accent_palette)]
                opacity = 1.0 - (j * 0.15)
                
                rects_html += f"""
                <g>
                    <rect x="{current_x + padding}" y="{current_y}" width="{p_width - 2*padding}" height="{c_height - padding}" 
                          fill="{c_fill}" fill-opacity="{opacity}" rx="{radius/2}"/>
                    <text x="{current_x + p_width/2}" y="{current_y + c_height/2}" fill="{text_color}" 
                          font-size="16" text-anchor="middle" dominant-baseline="middle">
                        {c_label if show_label else ''}
                    </text>
                </g>
                """
                current_y += c_height
        
        current_x += p_width

    treemap_svg_html = f"""
    <div style="width: 1100px; height: 600px; margin: 0 auto;">
        <svg width="1100" height="600" viewBox="0 0 1100 600">
            {rects_html}
        </svg>
    </div>
    """

    # ===== 3. RENDER TABLE ROWS =====
    table_rows = ""
    for item in data:
        table_rows += f"""
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 15px; font-weight: bold; color: {subtitle_color};">{item.get('label')}</td>
            <td style="padding: 15px; text-align: right;">{item.get('value')}{unit}</td>
        </tr>
        """

    # ===== 4. FINAL HTML CONSTRUCTION =====
    # Lưu ý: Tuân thủ quy tắc không lồng div quá 1 cấp từ container chính
    html_content = f"""
    <div style="width: 1920px; height: 1080px; background-color: #f7ede2; 
                background-image: linear-gradient(45deg, #f2e1d1 25%, transparent 25%), linear-gradient(-45deg, #f2e1d1 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f2e1d1 75%), linear-gradient(-45deg, transparent 75%, #f2e1d1 75%);
                background-size: 60px 60px; border: 12px solid #fbc02d; box-sizing: border-box; 
                font-family: {font_family}; position: relative; overflow: hidden; padding: 60px;">
        
        <div style="width: 100%; margin-bottom: 40px;">
            <h1 style="margin: 0; font-size: {main_title_font_size}; color: {main_title_color}; text-transform: uppercase; letter-spacing: 2px;">{main_title}</h1>
            <p style="margin: 10px 0 0 0; font-size: {subtitle_font_size}; color: {subtitle_color}; font-style: italic;">{subtitle}</p>
        </div>

        <div style="float: left; width: 500px; background: rgba(255,255,255,0.8); padding: 30px; border-radius: 20px; border: 3px solid #fbc02d; margin-right: 40px;">
            <h3 style="color: {main_title_color}; margin-top: 0; font-size: 30px; border-bottom: 2px solid #fbc02d; padding-bottom: 10px;">Phân tích Key Insight</h3>
            <p style="font-size: {insight_font_size}; color: {insight_text_color}; line-height: 1.6;">{insight}</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 30px; background: white; font-size: 20px;">
                <thead>
                    <tr style="background: #fbc02d; color: black;">
                        <th style="padding: 12px; text-align: left;">Hạng mục</th>
                        <th style="padding: 12px; text-align: right;">Tỷ trọng</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div style="float: left; width: 1150px; background: white; padding: 20px; border-radius: 30px; border: 4px solid #1a948e; box-shadow: 10px 10px 0px rgba(26, 148, 142, 0.2);">
            {treemap_svg_html}
        </div>

        <div style="position: absolute; bottom: 40px; right: 60px; background: #fbc02d; padding: 10px 30px; border-radius: 40px; font-weight: bold; border: 2px solid #000;">
            9TH GRADE LANGUAGE ARTS
        </div>

    </div>
    """
    return html_content

def generate_treemap_chart_slide_4(
    main_title="Academic Resource Allocation 2025",
    subtitle="Distribution of Budget across University Departments",
    insight="STEM and Research departments account for over 55% of the total budget. The allocation for Arts and Humanities remains stable, while Student Services has seen a 12% increase compared to last year's fiscal report.",
    unit = "M",
    show_value = True,
    show_label = True,
    data_label_format = "{label}: ${value}{unit}",
    padding = 4,
    border_radius = 8,
    base_color = "#1a5073",
    accent_color = "#fdf9c4",
    border_color = "#ffffff",
    text_color = "#ffffff",
    data = [
            {
                "label": "STEM",
                "value": 450,
                "children": [
                    {"label": "Engineering", "value": 200},
                    {"label": "Medicine", "value": 150},
                    {"label": "Pure Sciences", "value": 100}
                ]
            },
            {
                "label": "Humanities",
                "value": 300,
                "children": [
                    {"label": "Arts", "value": 120},
                    {"label": "History", "value": 100},
                    {"label": "Literature", "value": 80}
                ]
            },
            {
                "label": "Services",
                "value": 250,
                "children": [
                    {"label": "Housing", "value": 150},
                    {"label": "Health", "value": 100}
                ]
            }
        ],
    font_family="'Lato', sans-serif",
    main_title_color="#1a5073",
    subtitle_color="#1a5073",
    insight_text_color="#1a5073",
    main_title_font_size="80px",
    subtitle_font_size="32px",
    insight_font_size="28px"
) -> str:
    """
    Generates a professional Treemap chart slide with a refined academic aesthetic.
    The treemap uses a 'Slice-and-Dice' algorithm to partition space hierarchically.
    """

    # ===== 1. GET DATA & OPTIONS =====
    accent_color_opt = accent_color
    rect_border_color = border_color
    rect_text_color = text_color
    radius = border_radius

    # ===== 2. TREEMAP CALCULATION (SLICE-AND-DICE) =====
    # SVG Viewbox: 1100 x 600
    svg_w = 1100
    svg_h = 600
    
    def get_color_shade(index, total_items):
        # Generates shades of the base color for visual hierarchy
        if total_items <= 1: return base_color
        opacity = 1 - (index / total_items) * 0.5
        return f"rgba(26, 80, 115, {opacity})"

    rects_html = ""
    total_val = sum(item.get("value", 0) for item in data)
    
    current_x = 0
    total_data_len = len(data)
    
    for i, parent in enumerate(data):
        p_val = parent.get("value", 0)
        p_label = parent.get("label", "")
        children = parent.get("children", [])
        
        # Calculate width of parent block (Vertical slicing)
        p_width = (p_val / total_val) * svg_w if total_val > 0 else 0
        
        # Process children (Horizontal slicing inside parent)
        current_y = 0
        p_total_children = sum(c.get("value", 0) for c in children)
        
        if not children:
            # If no children, render the parent as a single block
            rects_html += f"""
            <g>
                <rect x="{current_x + padding}" y="{padding}" width="{p_width - 2*padding}" height="{svg_h - 2*padding}" 
                      fill="{get_color_shade(i, total_data_len)}" rx="{radius}" stroke="{rect_border_color}" stroke-width="1"/>
                <text x="{current_x + p_width/2}" y="{svg_h/2}" fill="{rect_text_color}" font-size="20" text-anchor="middle" dominant-baseline="middle" font-weight="bold">
                    {p_label if show_label else ""} {f"({p_val}{unit})" if show_value else ""}
                </text>
            </g>"""
        else:
            for j, child in enumerate(children):
                c_val = child.get("value", 0)
                c_label = child.get("label", "")
                
                # Height of child block
                c_height = (c_val / p_total_children) * svg_h if p_total_children > 0 else 0
                
                display_text = data_label_format.format(label=c_label, value=c_val, unit=unit)
                
                rects_html += f"""
                <g>
                    <rect x="{current_x + padding}" y="{current_y + padding}" width="{p_width - 2*padding}" height="{c_height - 2*padding}" 
                          fill="{get_color_shade(i, total_data_len)}" opacity="{0.9 - (j*0.1)}" rx="{radius}" stroke="{rect_border_color}" stroke-width="1"/>
                    <text x="{current_x + p_width/2}" y="{current_y + c_height/2}" fill="{rect_text_color}" font-size="16" text-anchor="middle" dominant-baseline="middle">
                        {(c_label if show_label else "") if c_height > 40 else ""}
                        <tspan x="{current_x + p_width/2}" dy="1.2em" font-size="12" font-weight="bold">
                            {(str(c_val) + unit if show_value else "") if c_height > 60 else ""}
                        </tspan>
                    </text>
                </g>"""
                current_y += c_height
                
        current_x += p_width

    treemap_svg = f"""
    <div style="width:1100px; height:600px; background:rgba(255,255,255,0.2); border-radius:15px; padding:10px;">
        <svg width="1100" height="600" viewBox="0 0 1100 600">
            {rects_html}
        </svg>
    </div>
    """

    # ===== 3. TABLE SECTION =====
    table_rows = ""
    for item in data:
        table_rows += f"""
        <tr style="border-bottom: 1px solid rgba(26, 80, 115, 0.2);">
            <td style="padding:15px; font-weight:bold;">{item.get('label')}</td>
            <td style="padding:15px; text-align:right;">{item.get('value')}{unit}</td>
        </tr>
        """

    table_html = f"""
    <table style="width:100%; border-collapse: collapse; margin-top: 20px; font-size: 22px; color: {main_title_color}; background: {accent_color_opt}44; border-radius: 10px; overflow: hidden;">
        <thead>
            <tr style="background: {main_title_color}; color: white;">
                <th style="padding:15px; text-align:left;">Department</th>
                <th style="padding:15px; text-align:right;">Allocation</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    """

    # ===== 4. FINAL ASSEMBLY =====
    return f"""
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:wght@900&display=swap" rel="stylesheet">
    </head>
    <body style="margin:0; padding:0; width:1920px; height:1080px; background-color:#a2dcc1; font-family:{font_family}; overflow:hidden; color:{main_title_color}; position:relative;">
        
        <div style="position:absolute; width:800px; height:800px; background:{accent_color_opt}; border-radius:50%; top:-300px; left:-200px; z-index:1;"></div>
        <div style="position:absolute; width:600px; height:600px; border:2px solid rgba(255,255,255,0.5); border-radius:50%; top:400px; right:-100px; z-index:1;"></div>
        
        <div style="position:relative; z-index:10; padding: 60px 100px;">
            <div style="margin-bottom: 50px;">
                <h1 style="font-family:'Playfair Display', serif; font-size:{main_title_font_size}; margin:0; line-height:1.1; color:{main_title_color};">{main_title}</h1>
                <div style="font-size:{subtitle_font_size}; margin-top:10px; font-weight:300; opacity:0.8; color:{subtitle_color};">{subtitle}</div>
            </div>

            <div style="display:flex; gap:60px; align-items:flex-start;">
                <div style="flex:1;">
                    <div style="background:rgba(255,255,255,0.6); padding:40px; border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.05);">
                        <div style="font-size:{insight_font_size}; line-height:1.6; margin-bottom:30px; font-style:italic; color:{insight_text_color};">
                            "{insight}"
                        </div>
                        {table_html}
                    </div>
                </div>

                <div style="flex:1.5; display:flex; flex-direction:column; align-items:center;">
                    {treemap_svg}
                    <div style="margin-top:20px; font-size:18px; opacity:0.7;">
                        * Rectangles sized by relative budgetary weight
                    </div>
                </div>
            </div>
        </div>

        <div style="position:absolute; bottom:50px; left:100px; display:grid; grid-template-columns:repeat(6, 12px); gap:15px; z-index:10;">
            {"<div style='width:12px; height:12px; background:white; border-radius:50%;'></div>" * 18}
        </div>
    </body>
    </html>
    """

def generate_treemap_chart_slide_5(
    main_title="Cell Biology Composition",
    subtitle="Distribution of Macromolecules in a Typical Animal Cell",
    insight=(
        "Proteins constitute the largest fraction of cell mass, followed by lipids and carbohydrates. "
        "Nucleic acids, while vital for genetic information, represent a smaller percentage of the total volume."
    ),
    unit="%",
    show_value=True,
    show_label=True,
    data_label_format="{label}: {value}%",
    padding=6,
    border_radius=8,
    base_color="#d86c9e",
    text_color="#fce7cf",
    border_color="#4c234a",
    accent_color_chart="#f4be52",
    data = [
            {
                "label": "Proteins",
                "value": 55,
                "children": [
                    {"label": "Structural", "value": 30},
                    {"label": "Enzymatic", "value": 25}
                ]
            },
            {
                "label": "Lipids",
                "value": 25,
                "children": [
                    {"label": "Phospholipids", "value": 15},
                    {"label": "Cholesterol", "value": 10}
                ]
            },
            {
                "label": "Others",
                "value": 20,
                "children": [
                    {"label": "Carbs", "value": 12},
                    {"label": "RNA/DNA", "value": 8}
                ]
            }
        ],
    font_family="'Fredoka', sans-serif",
    accent_color="#d86c9e",
    main_title_color="#fce7cf",
    subtitle_color="#f4be52",
    insight_text_color="#fce7cf",
    main_title_font_size="100px",
    subtitle_font_size="35px",
    insight_font_size="28px"
) -> str:
    """
    Generates a professional Treemap Chart slide with a biological/educational theme.
    Layout: Title at top, Chart on the left, Insight and Table on the right.
    """

    # ===== 1. GET DATA & OPTIONS =====
    radius = border_radius

    # ===== 2. RENDER TREEMAP SVG (Simple Horizontal Split) =====
    # Canvas for Treemap: 1000 x 600
    svg_w = 1000
    svg_h = 600
    total_val = sum(item.get("value", 0) for item in data)
    
    treemap_elements = []
    current_x = 0
    
    # Predefined color palette for categories
    palette = [base_color, accent_color_chart, "#91518b", "#d35400", "#704231"]

    for i, parent in enumerate(data):
        p_val = parent.get("value", 0)
        p_label = parent.get("label", "")
        children = parent.get("children", [])
        
        # Calculate parent width based on ratio
        p_width = (p_val / total_val * svg_w) if total_val > 0 else 0
        p_color = palette[i % len(palette)]
        
        # Parent group
        parent_rect = f"""
        <rect x="{current_x + padding}" y="{padding}" width="{p_width - 2*padding}" height="{svg_h - 2*padding}" 
              fill="{p_color}" rx="{radius}" stroke="{border_color}" stroke-width="2" opacity="0.9" />
        """
        treemap_elements.append(parent_rect)
        
        # Child rectangles (Vertical splits within parent)
        if children:
            c_total = sum(c.get("value", 0) for c in children)
            current_y = padding
            for child in children:
                c_val = child.get("value", 0)
                c_label = child.get("label", "")
                c_height = (c_val / c_total * (svg_h - 2*padding)) if c_total > 0 else 0
                
                # Draw child boundary
                treemap_elements.append(f"""
                    <rect x="{current_x + padding + 5}" y="{current_y + 5}" width="{p_width - 2*padding - 10}" height="{c_height - 10}" 
                          fill="rgba(255,255,255,0.1)" rx="{radius/2}" stroke="rgba(255,255,255,0.2)" stroke-width="1" />
                """)
                
                # Labeling
                if show_label or show_value:
                    if show_label and show_value:
                        display_text = data_label_format.format(label=c_label, value=c_val, unit=unit)
                    elif show_label:
                        display_text = c_label
                    else:
                        display_text = f"{c_val}{unit}"
                    # Text positioning
                    tx = current_x + p_width / 2
                    ty = current_y + c_height / 2
                    treemap_elements.append(f"""
                        <text x="{tx}" y="{ty}" fill="{text_color}" font-size="18" font-weight="bold" 
                              text-anchor="middle" dominant-baseline="middle" style="font-family:{font_family};">
                            {display_text}
                        </text>
                    """)
                
                current_y += c_height
        else:
            # If no children, put parent label in center
            if show_label or show_value:
                if show_label and show_value:
                    display_text = data_label_format.format(label=p_label, value=p_val, unit=unit)
                elif show_label:
                    display_text = p_label
                else:
                    display_text = f"{p_val}{unit}"
                treemap_elements.append(f"""
                    <text x="{current_x + p_width/2}" y="{svg_h/2}" fill="{text_color}" font-size="24" font-weight="bold" 
                          text-anchor="middle" dominant-baseline="middle" style="font-family:{font_family};">
                        {display_text}
                    </text>
                """)

        current_x += p_width

    svg_content = "\n".join(treemap_elements)
    treemap_html = f"""
    <div style="width: 1100px; height: 650px; background: rgba(0,0,0,0.1); border-radius: 20px; padding: 20px;">
        <svg width="100%" height="100%" viewBox="0 0 {svg_w} {svg_h}">
            {svg_content}
        </svg>
    </div>
    """

    # ===== 3. RENDER TABLE =====
    table_rows = ""
    for item in data:
        table_rows += f"""
        <tr style="border-bottom: 1px solid rgba(252, 231, 207, 0.2);">
            <td style="padding: 15px; font-weight: bold; color: {accent_color_chart};">{item.get('label')}</td>
            <td style="padding: 15px; text-align: right;">{item.get('value')}{unit}</td>
        </tr>
        """

    table_html = f"""
    <div style="width: 100%; margin-top: 30px;">
        <table style="width: 100%; border-collapse: collapse; color: #fce7cf; font-size: 22px;">
            <thead>
                <tr style="border-bottom: 2px solid {accent_color_chart}; text-align: left;">
                    <th style="padding: 15px;">Component</th>
                    <th style="padding: 15px; text-align: right;">Value</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    """

    # ===== 4. FINAL HTML GENERATION =====
    return f"""
    <div style="width: 1920px; height: 1080px; background-color: #4c234a; font-family: {font_family}; color: #fce7cf; position: relative; overflow: hidden; box-sizing: border-box; padding: 60px 80px;">
        
        <div style="position: absolute; top: 40px; right: 40px; width: 200px; height: 80px; opacity: 0.4; background-image: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 40%22%3E%3Cpath d=%22M0 10 Q 25 40 50 10 T 100 10%22 stroke=%22%23f4be52%22 stroke-width=%222%22 fill=%22none%22/%3E%3Cpath d=%22M0 30 Q 25 0 50 30 T 100 30%22 stroke=%22%23d86c9e%22 stroke-width=%222%22 fill=%22none%22/%3E%3C/svg%3E');"></div>
        <div style="position: absolute; bottom: -50px; left: -50px; width: 400px; height: 400px; opacity: 0.1; background-image: url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22%3E%3Ccircle cx=%2250%22 cy=%2250%22 r=%2240%22 fill=%22white%22/%3E%3C/svg%3E');"></div>

        <div style="margin-bottom: 50px;">
            <h1 style="margin: 0; font-family: 'Playfair Display', serif; font-size: {main_title_font_size}; color: {main_title_color}; line-height: 1;">{main_title}</h1>
            <p style="margin: 10px 0 0 0; font-size: {subtitle_font_size}; color: {subtitle_color}; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;">{subtitle}</p>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 60px;">
            
            <div style="flex: 1.4;">
                {treemap_html}
            </div>

            <div style="flex: 1; display: flex; flex-direction: column; gap: 30px;">
                <div style="background: rgba(216, 108, 158, 0.15); border-left: 10px solid {accent_color}; padding: 30px; border-radius: 0 20px 20px 0;">
                    <h3 style="margin: 0 0 15px 0; color: {accent_color_chart}; font-size: 32px; text-transform: uppercase;">Key Analysis</h3>
                    <p style="margin: 0; font-size: {insight_font_size}; line-height: 1.5; color: {insight_text_color};">
                        {insight}
                    </p>
                </div>
                {table_html}
            </div>
            
        </div>

        <div style="position: absolute; bottom: 40px; left: 80px; font-size: 16px; color: {text_color}; opacity: 0.4; letter-spacing: 2px;">
            CELLULAR ANATOMY SERIES // 2026
        </div>
    </div>
    """