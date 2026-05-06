def generate_table_slide_1(
    main_title="Renewable Energy Capacity by Region",
    subtitle="Global Energy Research Lab – 2024 Data",
    insight=(
        "Asia shows the largest installed renewable capacity, particularly in solar energy. "
        "Europe maintains strong wind power production, while hydro remains a stable base "
        "energy source across multiple regions."
    ),
    unit = " GW",
    show_value = True,
    data_label_format = "{value}",
    columns =  ["Solar", "Wind", "Hydro"],
    rows = [
        {"label": "Asia", "values": [620, 430, 510]},
        {"label": "Europe", "values": [310, 520, 260]},
        {"label": "North America", "values": [290, 340, 300]},
        {"label": "South America", "values": [150, 120, 380]}
    ],
)->str:
    """
    Slide deck with a Science Lab style.
    Suitable for research reports, group projects, or technical data analysis.
    """
    
    # ===== COLOR & FONT VARIABLES =====
    header_bg = "#76C2B4"
    grid_color = "#D1D5DB"
    text_color = "#333333"
    highlight_bg = "#E6F4F1"
    accent_color = "#76C2B4"
    main_title_color = "#333333"
    subtitle_color = "#666666"
    insight_text_color = "#444444"
    font_family = "Inter, Arial, sans-serif"
    main_title_font_size = "72px"
    subtitle_font_size = "32px"
    insight_font_size = "28px"

    # ===== 1. DATA PREPARATION =====
    # Using parameters directly instead of data_input and chart_options

    # ===== 2. PROCESS TABLE =====
    table_rows_html = ""
    for row in rows:
        label = row.get("label", "")
        values = row.get("values", [])
        cells_html = ""

        for value in values:
            formatted_value = ""
            if show_value:
                formatted_value = data_label_format.replace("{value}", str(value))
                if unit:
                    formatted_value += unit

            cells_html += f"""
            <td style="padding:20px; border-bottom:1px solid {grid_color}; text-align:center; font-size:24px; color:{text_color};">
                {formatted_value}
            </td>
            """

        table_rows_html += f"""
        <tr style="background-color: white;">
            <td style="padding:20px; border-bottom:1px solid {grid_color}; font-weight:700; font-size:24px; color:{main_title_color}; background:{highlight_bg}66;">
                {label}
            </td>
            {cells_html}
        </tr>
        """

    header_cells = ""
    for col in columns:
        header_cells += f"""
        <th style="padding:22px; background:{header_bg}; border-bottom:3px solid rgba(0,0,0,0.1); font-size:24px; color:white; text-transform:uppercase; letter-spacing:1px; width:25%;">
            {col}
        </th>
        """

    table_html = f"""
    <table style="border-collapse:collapse; width:60%; background:white; border-radius:15px; box-shadow:0 10px 30px rgba(0,0,0,0.05); table-layout:fixed;">
        <thead>
            <tr>
                <th style="padding:22px; background:{header_bg}; border-bottom:3px solid rgba(0,0,0,0.1); font-size:24px; color:white; text-transform:uppercase; width:25%;">
                    Hạng mục
                </th>
                {header_cells}
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>
    """

    # ===== 3. DESIGN SVG (LAB ICONS) =====
    decorations_svg = f"""
    <!-- Top Right Decoration (Atom / Science Theme) -->
    <div style="position:absolute; top:350px; right:50px; width:350px; height:350px; opacity:0.12; pointer-events:none; z-index:0;">
        <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="100" cy="100" rx="80" ry="25" transform="rotate(30 100 100)" stroke="{header_bg}" stroke-width="4"/>
            <ellipse cx="100" cy="100" rx="80" ry="25" transform="rotate(-30 100 100)" stroke="{header_bg}" stroke-width="4"/>
            <ellipse cx="100" cy="100" rx="80" ry="25" transform="rotate(90 100 100)" stroke="{header_bg}" stroke-width="4"/>
            <circle cx="100" cy="100" r="15" fill="{accent_color}"/>
            <circle cx="160" cy="30" r="8" fill="{header_bg}" fill-opacity="0.6"/>
            <circle cx="180" cy="60" r="5" fill="{accent_color}" fill-opacity="0.8"/>
            <circle cx="30" cy="150" r="6" fill="{header_bg}" fill-opacity="0.5"/>
        </svg>
    </div>

    <!-- Bottom Right Decoration (Beaker) -->
    <div style="position:absolute; bottom:20px; right:30px; width:180px; height:180px; opacity:0.25; pointer-events:none; z-index:0;">
        <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M140 40V140C140 151.046 131.046 160 120 160H80C68.9543 160 60 151.046 60 140V40" stroke="{header_bg}" stroke-width="8" stroke-linecap="round"/>
            <path d="M50 40H150" stroke="{header_bg}" stroke-width="8" stroke-linecap="round"/>
            <rect x="75" y="100" width="50" height="40" fill="{header_bg}" fill-opacity="0.3" />
            <circle cx="160" cy="60" r="10" fill="{header_bg}" fill-opacity="0.2" />
            <circle cx="175" cy="90" r="6" fill="{header_bg}" fill-opacity="0.2" />
        </svg>
    </div>
    """

    # ===== 4. RENDER HTML =====
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    html, body {{
      width:1920px;
      height:1080px;
      margin:0;
      padding:0;
      overflow:hidden;
      font-family:{font_family};
      background: radial-gradient({grid_color} 2px, transparent 2px), linear-gradient(135deg, #FFFFFF 0%, {highlight_bg} 40%, {accent_color}66 100%);
      background-size: 40px 40px, 100% 100%;
    }}

    .header-container {{
      padding: 80px 100px 0 100px;
    }}

    .title-box {{
      display: inline-block;
      background: {header_bg};
      padding: 10px 40px;
      border-radius: 50px;
      margin-bottom: 20px;
    }}

    h1 {{
      font-size: {main_title_font_size};
      color: {main_title_color};
      margin: 0;
      font-weight: 900;
      text-transform: uppercase;
    }}

    .subtitle {{
      font-size: {subtitle_font_size};
      color: {subtitle_color};
      margin-top: 10px;
      font-weight: 500;
    }}

    .main-flex {{
      display: flex;
      padding: 60px 100px;
      gap: 60px;
      height: 600px;
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
      align-items: center;
    }}

    .insight-card {{
      background: white;
      padding: 40px;
      border-radius: 20px;
      border-left: 15px solid {accent_color};
      box-shadow: 10px 10px 0px {accent_color}33;
      font-size: {insight_font_size};
      color: {insight_text_color};
      line-height: 1.6;
    }}
    </style>
    </head>

    <body>
        <div class="header-container">
            <h1>{main_title}</h1>
            {f'<div class="subtitle">{subtitle}</div>' if subtitle else ""}
        </div>

        <div class="main-flex">
            <div class="left-panel">
                <div class="insight-card">
                    {insight}
                </div>
            </div>

            <div class="right-panel">
                {table_html}
            </div>
        </div>

        {decorations_svg}
    </body>
    </html>
    """
    return html_code

def generate_table_slide_2(
        main_title = "Chemical Reagent Stability Analysis", 
        subtitle = "Source: International Journal of Applied Chemistry 2026", 
        insight = "Chemical reagents exhibit varying stability under standard laboratory conditions, with high-purity salts generally showing better long-term stability compared to organic solvents and reactive compounds.",
        unit = "%",    
        show_value = True,
        data_label_format = "{value}%",
        columns = ["Purity Level", "Solubility", "Reaction Yield"],
        rows = [
            {"label": "Ethanol (C2H5OH)", "values": [99.8, 100, 92]},
            {"label": "Sulfuric Acid (H2SO4)", "values": [98.5, 100, 88]},
            {"label": "Sodium Chloride (NaCl)", "values": [99.9, 36, 95]},
            {"label": "Silver Nitrate (AgNO3)", "values": [99.5, 216, 84]}
        ]
    ) -> str:
    """
    Generates a professional table slide with a Chemistry Lab theme.
    Features a clean layout, purple/yellow accents, and stylized table borders.
    """
    
    # ===== COLOR & FONT VARIABLES =====
    header_bg = "#3B3781"
    grid_color = "#D1D5DB"
    text_color = "#1F2937"
    highlight_bg = "#F3F4F6"
    accent_color = "#FFB300"
    main_title_color = "#3B3781"
    subtitle_color = "#6B7280"
    insight_text_color = "#1F2937"
    font_family = "'Inter', sans-serif"
    main_title_font_size = "72px"
    subtitle_font_size = "30px"
    insight_font_size = "28px"

    # ===== 1. DATA PREPARATION =====
    # Using parameters directly instead of data_input and chart_options

    # ===== 2. TABLE DATA PROCESSING =====
    table_rows_html = ""
    for index, row in enumerate(rows):
        label = row.get("label", "")
        values = row.get("values", [])
        
        # Stripe effect cho các hàng
        row_bg = "white" if index % 2 == 0 else highlight_bg

        cells_html = ""
        for value in values:
            formatted_value = ""
            if show_value:
                formatted_value = data_label_format.replace("{value}", str(value))
                if unit:
                    formatted_value += unit

            cells_html += f"""
            <td style="padding:25px 30px; border-bottom:2px solid {grid_color}; text-align:center; font-size:24px; color:{text_color};">
                {formatted_value}
            </td>
            """

        table_rows_html += f"""
        <tr style="background:{row_bg};">
            <td style="padding:25px 30px; border-bottom:2px solid {grid_color}; font-weight:700; font-size:24px; color:{header_bg}; text-align:left;">
                {label}
            </td>
            {cells_html}
        </tr>
        """

    # ===== HEADER RENDER =====
    header_cells = ""
    for col in columns:
        header_cells += f"""
        <th style="padding:25px 30px; background:{header_bg}; color:white; font-size:26px; font-weight:600; text-align:center; border-right:1px solid rgba(255,255,255,0.1);">
            {col}
        </th>
        """

    table_html = f"""
    <table style="border-collapse:collapse; width:100%; border-radius:20px; overflow:hidden; box-shadow:0 15px 35px rgba(59,55,129,0.1);">
        <thead>
            <tr>
                <th style="padding:25px 30px; background:{header_bg}; color:{accent_color}; font-size:26px; font-weight:800; text-align:left;">
                    Element/Exp
                </th>
                {header_cells}
            </tr>
        </thead>
        <tbody>
            {table_rows_html}
        </tbody>
    </table>
    """

    # ===== 3. DECORATIVE SVG (Chemistry Style) =====
    beaker_svg = f"""
    <div style="position:absolute; bottom:120px; right:80px; width:150px; height:150px; opacity:0.6;">
        <svg viewBox="0 0 100 100" fill="none">
            <path d="M30 20 L30 80 Q30 90 40 90 L60 90 Q70 90 70 80 L70 20 Z" stroke="{header_bg}" stroke-width="3"/>
            <path d="M30 40 L70 40" stroke="{header_bg}" stroke-width="2" stroke-dasharray="4 2"/>
            <path d="M30 65 L70 65" stroke="{accent_color}" stroke-width="5"/>
            <circle cx="45" cy="55" r="3" fill="{accent_color}"/>
            <circle cx="55" cy="48" r="2" fill="{header_bg}"/>
        </svg>
    </div>
    """

    # ===== 4. HTML RENDER =====
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    html, body {{
      width:1920px;
      height:1080px;
      margin:0;
      padding:0;
      overflow:hidden;
      font-family:{font_family};
      background-color:#FDFCFE;
    }}
    .slide-container {{
      width:100%;
      height:100%;
      padding:80px 100px;
      box-sizing:border-box;
      position:relative;
      background: radial-gradient(circle at 90% 10%, #F3E8FF 0%, transparent 40%);
    }}
    .header-section {{
      margin-bottom:60px;
      border-left:12px solid {accent_color};
      padding-left:35px;
    }}
    h1 {{
      font-size:{main_title_font_size};
      color:{main_title_color};
      margin:0;
      text-transform: uppercase;
      letter-spacing: -1px;
    }}
    .subtitle {{
      font-size:{subtitle_font_size};
      color:{subtitle_color};
      margin-top:15px;
      font-weight: 500;
    }}
    .main-flex {{
      display: flex;
      gap: 50px;
      margin-top: 20px;
      position: relative;
      z-index: 10;
      align-items: center;
    }}
    .left-panel {{
      flex: 1;
    }}
    .right-panel {{
      flex: 2;
    }}
    .insight-card {{
      background: white;
      padding: 35px;
      border-radius: 16px;
      border-left: 10px solid {accent_color};
      font-size: {insight_font_size};
      color: {insight_text_color};
      line-height: 1.6;
      box-shadow: 0 10px 25px rgba(59,55,129,0.05);
    }}
    .top-blob {{
      position:absolute; top:-100px; right:-100px; width:400px; height:400px; 
      background: {accent_color}; opacity: 0.1; border-radius: 50%;
    }}
    </style>
    </head>
    <body>
        <div class="slide-container">
            <div class="top-blob"></div>
            
            <div class="header-section">
                <h1>{main_title}</h1>
                {f'<div class="subtitle">{subtitle}</div>' if subtitle else ""}
            </div>

            <div class="main-flex">
                <div class="left-panel">
                    {f'<div class="insight-card">{insight}</div>' if insight else ''}
                </div>
                <div class="right-panel">
                    {table_html}
                </div>
            </div>

            {beaker_svg}
        </div>
    </body>
    </html>
    """

    return html_code

def generate_table_slide_3(
        main_title="Islamic Cultural Contributions by Region",
        subtitle="Global Islamic Heritage Study – 2024",
        insight="",
        unit = "",
        show_value = True,
        data_label_format = "{value}",
        columns = ["Mosques", "Scholars", "Cultural Sites"],
        rows = [
            {"label": "Middle East", "values": [1200, 850, 400]},
            {"label": "Southeast Asia", "values": [900, 300, 150]},
            {"label": "South Asia", "values": [1100, 500, 220]},
            {"label": "North Africa", "values": [800, 450, 300]}
        ]
    ) -> str:
    """
    Tạo slide bảng với phong cách Hồi giáo trang nhã sang trọng.
    """
    
    # ===== COLOR & FONT VARIABLES =====
    header_bg = "linear-gradient(135deg, #D4AF37, #AA7C11)"
    grid_color = "rgba(212, 175, 55, 0.2)"
    text_color = "#FFFFFF"
    highlight_bg = "rgba(10, 52, 39, 0.4)"
    accent_color = "#D4AF37"
    main_title_color = "#D4AF37"
    subtitle_color = "#E0E0E0"
    insight_text_color = "#FFFFFF"
    font_family = "'Outfit', sans-serif"
    main_title_font_size = "64px"
    subtitle_font_size = "28px"
    insight_font_size = "28px"

    # ===== 1. LẤY THÔNG TIN VÀ XỬ LÝ DỮ LIỆU =====

    # ===== 2. XỬ LÝ HTML TABLE =====
    table_rows_html = ""
    for row in rows:
        label = row.get("label", "")
        values = row.get("values", [])
        cells_html = ""

        for value in values:
            formatted_value = ""
            if show_value:
                formatted_value = data_label_format.replace("{value}", str(value))
                if unit:
                    formatted_value += unit

            cells_html += f"""
            <td style="padding:18px; border-bottom:2px solid {grid_color}; text-align:center; font-size:24px; color:{text_color};">
                {formatted_value}
            </td>"""

        table_rows_html += f"""
        <tr style="background-color: transparent; transition: all 0.3s ease;" class="table-row-hover">
            <td style="padding:18px; border-bottom:2px solid {grid_color}; font-weight:600; font-size:24px; color:{main_title_color}; background:rgba(212, 175, 55, 0.05); font-family: 'Cinzel', serif;">
                {label}
            </td>
            {cells_html}
        </tr>"""

    header_cells = "".join([f'<th style="padding:22px; background:{header_bg}; color:#0A3427; font-size:24px; font-family: \'Cinzel\', serif; text-transform:uppercase; letter-spacing:2px; font-weight:700;">{col}</th>' for col in columns])

    table_html = f"""
    <table style="border-collapse:collapse; width:100%; border-radius:15px; overflow:hidden; box-shadow:0 15px 40px rgba(0,0,0,0.6); background:rgba(6, 31, 23, 0.7); backdrop-filter:blur(10px); border: 2px solid #D4AF37;">
        <thead>
            <tr>
                <th style="padding:22px; background:{header_bg}; color:#0A3427; font-size:24px; text-align:left; font-family: \'Cinzel\', serif; font-weight:700;">Category</th>
                {header_cells}
            </tr>
        </thead>
        <tbody>{table_rows_html}</tbody>
    </table>"""

    # ===== 3. HỌA TIẾT TRANG TRÍ (SVG) =====
    lantern_svg = f"""
    <div class="lantern-container">
    <svg width="100" height="150" viewBox="0 0 100 150" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M50 0V20M30 40C30 30 70 30 70 40V80C70 90 30 90 30 80V40Z" stroke="{accent_color}" stroke-width="2.5" filter="url(#glow)"/>
        <path d="M35 45L65 45M35 75L65 75M50 40V85" stroke="{accent_color}" stroke-width="2"/>
        <path d="M40 85L30 110H70L60 85" fill="{accent_color}" fill-opacity="0.2" stroke="{accent_color}" stroke-width="2.5"/>
        <circle cx="50" cy="60" r="8" fill="#FFF2CC" filter="url(#glow_light)" />
        <defs>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <filter id="glow_light" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>
    </svg>
    </div>"""

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
        html, body {{
            width:1920px; height:1080px; margin:0; padding:0; overflow:hidden;
            font-family: {font_family}; 
            background-color: #123C2A;
            background-image: 
                radial-gradient(circle at top, rgba(212, 175, 55, 0.15) 0%, transparent 60%),
                url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Cg fill='none' stroke='%23D4AF37' stroke-width='1.5' stroke-opacity='0.12'%3E%3Cpath d='M40 0L80 40L40 80L0 40zm0 20L60 40 40 60 20 40z'/%3E%3Ccircle cx='40' cy='40' r='10'/%3E%3Cpath d='M0 0h80v80H0z' stroke-opacity='0.05'/%3E%3C/g%3E%3C/svg%3E");
            background-size: 100% 100%, 80px 80px;
            background-repeat: no-repeat, repeat;
        }}
        .slide-container {{
            position:relative; width:100%; height:100%;
            display:flex; flex-direction:column; padding: 130px 140px; box-sizing:border-box;
        }}
        .header-section {{
            display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:40px;
        }}
        .title-group {{
            border-left:8px solid {accent_color}; padding-left:30px;
        }}
        h1 {{
            font-family: 'Cinzel', Georgia, 'Times New Roman', serif;
            font-size:{main_title_font_size}; color:{main_title_color}; margin:0; font-weight:700; text-transform:uppercase;
            letter-spacing: 3px;
            text-shadow: 0px 2px 4px rgba(0,0,0,0.6);
        }}
        .subtitle {{
            font-size:{subtitle_font_size}; color:{subtitle_color}; margin-top:12px; font-weight: 400;
            letter-spacing: 1px;
            text-shadow: 0px 1px 2px rgba(0,0,0,0.6);
        }}
        .main-content {{
            display:flex; gap:60px; align-items:flex-start;
            background: {highlight_bg};
            backdrop-filter: blur(8px);
            border: 1.5px solid rgba(212, 175, 55, 0.3);
            border-radius: 20px;
            padding: 45px;
            box-shadow: inset 0 0 30px rgba(0,0,0,0.6), 0 10px 40px rgba(0,0,0,0.5);
        }}
        .insight-panel {{
            flex: 1;
            font-size: {insight_font_size};
            color: {insight_text_color};
            line-height: 1.6;
            padding-right: 20px;
            font-weight: 300;
            text-shadow: 0px 1px 2px rgba(0,0,0,0.8);
        }}
        .table-panel {{
            flex:2;
            table-layout:fixed;
        }}
        .table-row-hover:hover {{
            background: rgba(212, 175, 55, 0.12) !important;
            transform: scale(1.008);
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
        }}
        .lantern-container {{
            filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.5));
        }}
        .decoration-bottom {{
            position:absolute; bottom:120px; left:140px; right:140px; height:2px;
            background: linear-gradient(to right, transparent, {accent_color}, transparent);
            opacity: 0.4;
        }}
    </style>
    </head>
    <body>
        <div class="slide-container">
            <div class="header-section">
                <div class="title-group">
                    <h1>{main_title}</h1>
                    {f'<div class="subtitle">{subtitle}</div>' if subtitle else ""}
                </div>
                <div>{lantern_svg}</div>
            </div>

            <div class="main-content">
                {f'<div class="insight-panel">{insight}</div>' if insight else ''}
                <div class="table-panel">
                    {table_html}
                </div>
            </div>
            
            <div class="decoration-bottom"></div>
        </div>
    </body>
    </html>
    """
    return html_code

def generate_table_slide_4(
    main_title: str = "Average Blood Pressure by Age Group", 
    subtitle: str = "Unit: mmHg | Data Source: National Health Survey 2025", 
    insight: str = "Healthcare is important, Keep your health in check!",
    x_axis: str = "Age Group",
    y_axis: str = "Average Blood Pressure (mmHg)",
    unit: str = "mmHg",
    show_value: bool = True,
    show_legend: bool = True,
    y_axis_min: float = 0,
    y_axis_max: float = None,
    data_label_format: str = None,
    colors: list[str] = ["#C62828", "#1565C0"], 
    categories = ["18-25", "26-35", "36-45", "46-60", "60+"],
    series = [
        {
        "name": "Male",
        "values": [118, 122, 128, 135, 142]
        },
        {
        "name": "Female",
        "values": [112, 118, 124, 130, 138]
        }
    ],
    ) -> str:
    """
    Tạo slide bảng chuyên nghiệp với phong cách thiết kế hiện đại, 
    lấy cảm hứng từ lĩnh vực y tế/điều dưỡng.
    """

    # Thiết lập giá trị mặc định cho chart_options và data_input nếu không được cung cấp

    chart_options = {
        "unit": unit,
        "show_value": show_value,
        "show_legend": show_legend,
        "y_axis_min": y_axis_min,
        "y_axis_max": y_axis_max,
        "data_label_format": data_label_format,
        "colors": colors,
        "x_axis": x_axis,
        "y_axis": y_axis
    }

    data_input = {
        "categories": categories,
        "series": series
    }

    # ===== 1. LẤY THÔNG TIN DỮ LIỆU =====
    columns = data_input.get("columns", [])
    rows = data_input.get("rows", [])

    # Nếu không có rows từ data_input, tạo từ series
    if not rows:
        rows = []
        for item in series:
            row_data = {
                "label": item["name"],
                "values": item["values"]
            }
            rows.append(row_data)

    # Nếu không có columns từ data_input, tạo từ categories
    if not columns:
        columns = categories

    options = chart_options 
    unit = options.get("unit", "")
    show_value = options.get("show_value", True)
    data_label_format = options.get("data_label_format") or "{value}"

    # ===== 2. XỬ LÝ DỮ LIỆU BẢNG (ROWS) =====
    table_rows_html = ""
    for row in rows:
        label = row.get("label", "")
        values = row.get("values", [])
        
        cells_html = ""
        for value in values:
            formatted_value = data_label_format.replace("{value}", str(value)) if show_value else ""
            if unit and formatted_value:
                formatted_value += unit

            cells_html += f"""
        <td style="padding:25px; border-bottom:1px solid var(--grid-color); text-align:center; font-size:24px; color:var(--text-color);">
        {formatted_value}
        </td>
        """

        table_rows_html += f"""
    <tr style="transition: background 0.3s;">
        <td style="padding:25px; border-bottom:1px solid var(--grid-color); font-weight:600; font-size:24px; color:var(--accent-color); background:var(--highlight-bg);">
        {label}
        </td>
        {cells_html}
    </tr>
    """

    # ===== 3. XỬ LÝ TIÊU ĐỀ BẢNG (HEADER) =====
    header_cells = ""
    for col in columns:
        header_cells += f"""
    <th style="padding:25px; background:var(--header-bg); border-bottom:2px solid var(--accent-color); font-size:22px; color:#FFFFFF; text-transform:uppercase; letter-spacing:1px;">
        {col}
    </th>
    """

    table_html = f"""
    <table style="border-collapse:collapse; width:100%; background:rgba(255,255,255,0.05); border-radius:20px; overflow:hidden; backdrop-filter:blur(10px);">
    <thead>
        <tr>
        <th style="padding:25px; background:var(--header-bg); border-bottom:2px solid var(--accent-color); font-size:22px; color:#FFFFFF; text-transform:uppercase; text-align:left;">
            Metric / Category
        </th>
        {header_cells}
        </tr>
    </thead>
    <tbody>
        {table_rows_html}
    </tbody>
    </table>
    """

    # ===== 4. HTML RENDER =====
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    :root {{
      --font-family: 'Inter', sans-serif;
      --header-bg: #5D3B6B;
      --grid-color: rgba(255, 255, 255, 0.1);
      --text-color: #FFFFFF;
      --highlight-bg: rgba(232, 156, 180, 0.15);
      --accent-color: #E89CB4;
      --main-title-color: #4ADE80;
      --subtitle-color: #64748B;
      --insight-text-color: #2DD4BF;
      --main-title-font-size: 70px;
      --subtitle-font-size: 30px;
      --insight-font-size: 28px;
    }}

    html, body {{
      width:1920px;
      height:1080px;
      margin:0;
      padding:0;
      overflow:hidden;
      font-family: var(--font-family);
      background: radial-gradient(circle at 20% 20%, #4A2B52 0%, #2D1B33 100%);
      color: white;
    }}

    .medical-pattern {{
      position: absolute;
      width: 100%;
      height: 100%;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cpath stroke='rgba(255,255,255,0.05)' stroke-width='3' stroke-linejoin='round' fill='none' d='M0,80 L40,80 L50,40 L70,120 L80,80 L160,80'/%3E%3Cpath fill='rgba(255,255,255,0.03)' d='M125,25 h10 v10 h10 v10 h-10 v10 h-10 v-10 h-10 v-10 h10 z'/%3E%3C/svg%3E");
      background-size: 160px 160px;
      z-index: 0;
    }}

    .content-container {{
      position: relative;
      z-index: 1;
      padding: 80px 100px;
      display: flex;
      flex-direction: column;
      height: 100%;
      box-sizing: border-box;
    }}

    .header-section {{
      margin-bottom: 60px;
      border-left: 12px solid var(--accent-color);
      padding-left: 40px;
    }}

    h1 {{
      font-size: var(--main-title-font-size);
      font-weight: 800;
      color: var(--main-title-color);
      margin: 0;
      text-transform: uppercase;
      letter-spacing: -1px;
    }}

    .subtitle {{
      font-size: var(--subtitle-font-size);
      color: var(--subtitle-color);
      margin-top: 15px;
      font-weight: 300;
    }}

    .main-grid {{
      display: flex;
      gap: 60px;
      flex: 1;
      align-items: flex-start;
    }}

    .left-column {{
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 40px;
    }}

    .insight-panel {{
      flex: 1;
      background: rgba(255, 255, 255, 0.08);
      padding: 50px;
      border-radius: 30px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .insight-text {{
      font-size: var(--insight-font-size);
      color: var(--insight-text-color);
      line-height: 1.6;
      font-style: italic;
    }}

    .table-panel {{
      flex: 2;
    }}

    .accent-bar {{
      width: 80px;
      height: 6px;
      background: var(--accent-color);
      margin-bottom: 30px;
      border-radius: 3px;
    }}

    </style>
    </head>
    <body>
    <div class="medical-pattern"></div>
    <div class="content-container">
        <div class="header-section">
        <h1>{main_title}</h1>
        {f'<div class="subtitle">{subtitle}</div>' if subtitle else ""}
        </div>

        <div class="main-grid">
        <div class="left-column">
            <div class="insight-panel">
            <div class="accent-bar"></div>
            <div class="insight-text">
                "{insight}"
            </div>
            </div>
            <div class="medical-svg" style="display:flex; justify-content:center; align-items:center; flex:1; opacity: 0.3;">
            <svg width="250" height="250" viewBox="0 0 24 24" fill="none" stroke="var(--accent-color)" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
            </div>
        </div>

        <div class="table-panel">
            {table_html}
        </div>
        </div>
    </div>
    </body>
    </html>
    """
    return html_code

def generate_table_slide_5(
    main_title: str = "Vietnamese Cultural Heritage by Region",
    subtitle: str = "Traditional Values & Cultural Assets across Vietnam",
    insight: str = "Vietnam's rich cultural heritage is deeply rooted in its regional diversity, with the North known for its vibrant festivals, the Central region for its historical sites, and the South for its traditional crafts. This slide highlights the unique cultural assets of each region, showcasing the importance of preserving these traditions for future generations.",
    unit: str = "",
    show_value: bool = True,
    data_label_format: str = "{value}",
    columns = ["Festivals", "Historical Sites", "Traditional Crafts"],
    rows = [
        {"label": "Northern Vietnam", "values": [120, 85, 60]},
        {"label": "Central Vietnam", "values": [95, 70, 55]},
        {"label": "Southern Vietnam", "values": [80, 60, 40]}
    ]
) -> str:

    # ===== TABLE =====
    table_rows_html = ""
    for row in rows:
        label = row.get("label", "")
        values = row.get("values", [])
        cells_html = ""

        for value in values:
            formatted_value = ""
            if show_value:
                formatted_value = data_label_format.replace("{value}", str(value))
                if unit:
                    formatted_value += unit

            cells_html += f"""
            <td style="padding:18px; border:1px solid var(--grid-color); text-align:center; font-size:24px; color:var(--text-color);">
            {formatted_value}
            </td>
            """

        table_rows_html += f"""
        <tr style="background: rgba(139, 0, 0, 0.2);">
            <td style="padding:18px; border:1px solid var(--grid-color); font-weight:bold; font-size:24px; color:var(--accent-color); background:var(--highlight-bg);">
            {label}
            </td>
            {cells_html}
        </tr>
        """

    header_cells = ""
    for col in columns:
        header_cells += f"""
    <th style="padding:22px; background:var(--header-bg); border:2px solid var(--grid-color); font-size:24px; color:var(--accent-color); text-transform:uppercase;">
        {col}
    </th>
    """

    table_html = f"""
    <table style="border-collapse:collapse; width:100%; border:2px solid var(--grid-color); box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
    <thead>
        <tr>
        <th style="padding:22px; background:var(--header-bg); border:2px solid var(--grid-color); font-size:24px; color:var(--accent-color);">CATEGORY</th>
        {header_cells}
        </tr>
    </thead>
    <tbody>
        {table_rows_html}
    </tbody>
    </table>
    """

    # ===== HTML =====
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    :root {{
      --header-bg: linear-gradient(135deg, #8B0000, #5D0E0E);
      --grid-color: #D4AF37;
      --text-color: #FFFFFF;
      --highlight-bg: rgba(93, 14, 14, 0.6);
      --accent-color: #FFD700;
      --main-title-color: #FFD700;
      --subtitle-color: #E0E0E0;
      --insight-text-color: #FFFFFF;
      --font-family: 'Times New Roman', serif;
      --main-title-font-size: 64px;
      --subtitle-font-size: 28px;
      --insight-font-size: 28px;
    }}

    html, body {{
      width:1920px; height:1080px; margin:0;
      font-family: var(--font-family);
      background-color: #4A0404;
      background-image: 
    radial-gradient(circle at 50% 50%, rgba(212,175,55,0.1) 0%, transparent 70%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'%3E%3Cg stroke='rgba(212,175,55,0.15)' stroke-width='1.5' fill='none'%3E%3Ccircle cx='60' cy='60' r='50'/%3E%3Ccircle cx='60' cy='60' r='35'/%3E%3Cpath stroke-linejoin='round' d='M60,10 L70,45 L105,60 L70,75 L60,110 L50,75 L15,60 L50,45 Z'/%3E%3Ccircle cx='60' cy='60' r='15' fill='rgba(212,175,55,0.05)'/%3E%3Cpath d='M0,0 L120,120 M120,0 L0,120' stroke='rgba(212,175,55,0.05)'/%3E%3C/g%3E%3C/svg%3E");
      background-size: 100% 100%, 120px 120px;
      color: #FFFFFF;
    }}

    .container {{
      width: 100%; height: 100%;
      display: flex;
      flex-direction: column;
      padding: 60px 100px;
      border: 20px solid var(--grid-color);
      box-sizing: border-box;
    }}

    h1 {{
      font-size: var(--main-title-font-size);
      color: var(--main-title-color);
      margin: 0;
      text-transform: uppercase;
    }}

    .subtitle {{
      font-size: var(--subtitle-font-size);
      color: var(--subtitle-color);
      margin-top: 10px;
    }}

    .insight-box {{
      margin-top: 40px;
      font-size: var(--insight-font-size);
      color: var(--insight-text-color);
      background: rgba(0,0,0,0.3);
      padding: 30px 40px;
      border-left: 10px solid var(--grid-color);
      line-height: 1.6;
    }}

    .table-container {{
      margin-top: 50px;
    }}

    </style>
    </head>

    <body>
    <div class="container">
        <h1>{main_title}</h1>
        <div class="subtitle">{subtitle}</div>

        <!-- Insight trên -->
        <div class="insight-box">
        {insight}
        </div>

        <!-- Table dưới -->
        <div class="table-container">
        {table_html}
        </div>
    </div>
    </body>
    </html>
    """
    return html_code

def generate_table_slide_6(
    main_title="Bức Tranh Làng Quê Việt Nam",
    subtitle="Đơn vị: Khu vực | Nguồn: Khảo sát nông thôn Việt Nam 2025",
    insight="Khu vực nông thôn Việt Nam thể hiện sự đa dạng trong hoạt động kinh tế, từ nông nghiệp đến chăn nuôi và thủ công.",
    unit="",
    show_value=True,
    data_label_format="{value}",
    columns=["Nông nghiệp", "Chăn nuôi", "Thủ công"],
    rows=[
        {"label": "Đồng bằng", "values": [1200, 850, 400]},
        {"label": "Trung du", "values": [900, 600, 300]},
        {"label": "Miền núi", "values": [700, 500, 450]},
        {"label": "Ven biển", "values": [800, 650, 200]}
    ]
    ) -> str:
    """
    Hàm sinh slide bảng với phong cách Làng quê Việt Nam.
    Sử dụng tông màu xanh lá cây và vàng lúa, lấy cảm hứng từ thiên nhiên và sự mộc mạc.
    """

    # ===== 1. XỬ LÝ DỮ LIỆU =====
    columns = columns or []
    rows = rows or []

    # ===== 2. RENDER DATA ROWS =====
    table_rows_html = ""
    for row in rows:
        label = row.get("label", "")
        values = row.get("values", [])

        cells_html = ""
        for value in values:
            formatted_value = ""
            if show_value:
                val_str = str(value)
                formatted_value = data_label_format.replace("{value}", val_str).replace("{unit}", unit)
                if unit and "{unit}" not in data_label_format:
                    formatted_value += unit

            cells_html += f"""
            <td style="
            padding: 20px 25px;
            border-bottom: 1px solid var(--grid-color);
            text-align: center;
            font-size: 24px;
            color: var(--text-color);
            ">
            {formatted_value}
            </td>
            """

        table_rows_html += f"""
        <tr style="transition: background 0.3s;">
            <td style="
            padding: 20px 25px;
            border-bottom: 1px solid var(--grid-color);
            font-weight: 700;
            font-size: 24px;
            color: var(--main-title-color);
            background: var(--highlight-bg);
            border-left: 5px solid var(--accent-color);
            ">
            {label}
            </td>
            {cells_html}
        </tr>
        """

    # ===== 3. RENDER HEADER =====
    header_cells = ""
    for col in columns:
        header_cells += f"""
        <th style="
            padding: 22px 25px;
            background: var(--header-bg);
            color: #FFFFFF;
            font-size: 24px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 3px solid var(--accent-color);
        ">
            {col}
        </th>
        """

    table_html = f"""
    <table style="
    border-collapse: collapse;
    width: 100%;
    background: rgba(255, 255, 255, 0.82);
    border-radius: 15px 15px 0 0;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    ">
    <thead>
        <tr>
        <th style="
            padding: 22px 25px;
            background: var(--header-bg);
            color: #FFFFFF;
            font-size: 24px;
            border-bottom: 3px solid var(--accent-color);
            text-align: left;
        ">
            Danh mục
        </th>
        {header_cells}
        </tr>
    </thead>
    <tbody>
        {table_rows_html}
    </tbody>
    </table>
    """

    # ===== 4. INSIGHT BOX =====
    insight_html = f"""
    <div style="
    padding: 40px;
    background: white;
    border-radius: 20px;
    border-right: 10px solid var(--accent-color);
    box-shadow: 10px 10px 0px var(--grid-color);
    min-height: 220px;
    ">
    <div style="
        font-size: 18px;
        color: var(--accent-color);
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 15px;
        letter-spacing: 2px;
    ">
        Nhận định chuyên gia
    </div>
    <div style="
        font-size: var(--insight-font-size);
        color: var(--insight-text-color);
        line-height: 1.6;
        font-style: italic;
    ">
        "{insight}"
    </div>
    </div>
    """

    # ===== 5. FINAL HTML RENDER =====
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    :root {{
        --header-bg: linear-gradient(135deg, #2D6A4F, #1B4332);
        --grid-color: rgba(183, 228, 199, 0.35);
        --text-color: #081C15;
        --highlight-bg: rgba(247, 241, 227, 0.9);
        --accent-color: #D4AF37;
        --main-title-color: #1B4332;
        --subtitle-color: #2D6A4F;
        --insight-text-color: #40916C;
        --font-family: 'Inter', sans-serif;
        --main-title-font-size: 65px;
        --subtitle-font-size: 28px;
        --insight-font-size: 30px;
    }}

    html, body {{
        width: 1920px;
        height: 1080px;
        margin: 0;
        padding: 0;
        overflow: hidden;
        font-family: var(--font-family);
        background-color: #F0F4F0;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'%3E%3Cg stroke='rgba(45,106,79,0.08)' stroke-width='2' fill='none' stroke-linecap='round'%3E%3Cpath d='M40,80 C40,60 40,40 40,20 C30,30 25,45 40,50 C50,30 55,45 40,50 M30,60 C20,50 15,65 30,70 M50,60 C60,50 65,65 50,70'/%3E%3C/g%3E%3C/svg%3E");
        background-size: 80px 80px;
    }}

    .container {{
        padding: 80px 100px;
        height: 100%;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
    }}

    .header-section {{
        margin-bottom: 60px;
        position: relative;
    }}

    .header-section::before {{
        content: "";
        position: absolute;
        left: -30px;
        top: 0;
        width: 12px;
        height: 100%;
        background: var(--accent-color);
        border-radius: 6px;
    }}

    h1 {{
        font-size: var(--main-title-font-size);
        color: var(--main-title-color);
        margin: 0;
        font-weight: 800;
        letter-spacing: -1px;
    }}

    .subtitle {{
        font-size: var(--subtitle-font-size);
        color: var(--subtitle-color);
        margin-top: 15px;
        font-weight: 400;
    }}

    .content-layout {{
        display: flex;
        gap: 60px;
        align-items: flex-start;
    }}

    .table-wrapper {{
        flex: 1.5;
    }}

    .insight-wrapper {{
        flex: 1;
    }}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header-section">
        <h1>{main_title}</h1>
        {f'<div class="subtitle">{subtitle}</div>' if subtitle else ""}
        </div>

        <div class="content-layout">
        <div class="insight-wrapper">
            {insight_html}
            <div style="
            margin-top: 40px;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 300px;
            width: 100%;
            opacity: 0.4;
            gap: 20px;
            ">
            <!-- Conical Hat SVG -->
            <svg width="120" height="120" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M50 10L10 80C10 80 30 90 50 90C70 90 90 80 90 80L50 10Z" fill="var(--main-title-color)" opacity="0.8"/>
                <path d="M20 73C30 80 40 82 50 82C60 82 70 80 80 73" stroke="white" stroke-width="2" stroke-linecap="round"/>
                <path d="M30 55C40 60 45 62 50 62C55 62 60 60 70 55" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
            </div>
        </div>

        <div class="table-wrapper">
            {table_html}
        </div>
        </div>
    </div>

    </body>
    </html>
    """
    return html_code

def generate_table_slide_7(
    main_title="ELEGANCE CLASSY",
    subtitle="Minimalist Table Infographics",
    show_legend=True,
    legend_items=[
        {"label": "Marketing", "color": "#9a7a63"},
        {"label": "Financial", "color": "#b7b9ab"},
        {"label": "Sales", "color": "#faeaaa"}
    ],
    columns=["Mon", "Tue", "Wed", "Thu", "Fri"],
    rows=[
        {
            "label": "Week 1",
            "cells": [None, "Financial", None, None, None]
        },
        {
            "label": "Week 2",
            "cells": [None, None, None, "Sales", None]
        },
        {
            "label": "Week 3",
            "cells": ["Marketing", None, None, None, None]
        },
    ],
) -> str:
    """
    Generates a minimalist, elegant HTML table slide with brand decorative elements.
    Uses legend_items labels instead of color codes for automatic color mapping.
    """
    bg_light="#fefaf4"
    bg_dark="#3a3730"
    
    # Create a color mapping from legend labels to colors
    color_map = {item['label']: item['color'] for item in legend_items} if legend_items else {}
    
    # ===== STYLE VARIABLES =====
    header_bg = bg_light
    grid_color = "#9a7a6344"
    text_color = bg_dark
    font_family = "Outfit, sans-serif"
    main_title_color = bg_dark
    subtitle_color = f"{bg_dark}aa"
    main_title_font_size = "100px"
    subtitle_font_size = "36px"
    text_col_default = "#6f7067"

    # ===== 1. DATA PROCESSING =====
    header_html = ""
    for col_label in columns:
        label = col_label if isinstance(col_label, str) else col_label.get("label", str(col_label))
        header_html += f'<th style="padding: 30px 20px; border: 1px solid {grid_color}; text-align: center; color: {text_col_default}; background: {bg_light}; font-weight: 700; font-size: 40px; min-width: 200px;">{label}</th>'

    table_rows_html = ""
    for row in rows:
        row_label = row.get("label", "")
        cells = row.get("cells", [])
        
        cells_html = ""
        for cell in cells:
            # cell can be: None (light bg) or a legend label string
            if cell and cell in color_map:
                bg = color_map[cell]
                text_col = "white" if cell == "Marketing" else text_col_default
            else:
                bg = bg_light
                text_col = text_col_default
            
            cell_style = f"padding: 25px 20px; border: 1px solid {grid_color}; text-align: center; color: {text_col}; font-size: 28px; line-height: 1.2; background: {bg};"
            cells_html += f'<td style="{cell_style}"></td>'

        table_rows_html += f"""
        <tr>
            <td style="padding: 30px 20px; border: 1px solid {grid_color}; font-weight: 700; color: {text_col_default}; background: {bg_light}; font-size: 40px; text-align: center;">
                {row_label}
            </td>
            {cells_html}
        </tr>
        """

    legend_html = ""
    if show_legend and legend_items:
        items_html = ""
        for item in legend_items:
            items_html += f"""
            <div class="legend-item">
                <div class="legend-circle" style="background-color: {item['color']};"></div>
                <span class="legend-label">{item['label']}</span>
            </div>
            """
        legend_html = f'<div class="legend-container">{items_html}</div>'

    # ===== 2. FINAL HTML =====
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-light: {bg_light};
                --bg-dark: {bg_dark};
                --grid-line: {grid_color};
                --text-default: {text_col_default};
            }}
            body {{
                margin: 0;
                padding: 0;
                background-color: var(--bg-light);
                font-family: {font_family};
                color: var(--text-default);
                width: 1920px;
                height: 1080px;
                overflow: hidden;
                position: relative;
            }}
            .left-bar {{
                position: absolute;
                left: 0;
                top: 0;
                bottom: 650px;
                width: 70px;
                background-color: #c9b09a;
            }}
            .top-box-mini {{
                position: absolute;
                right: 0;
                top: 0;
                width: 483px;
                height: 50px;
                background-color: #b7b9ab;
            }}
            .bottom-left-box {{
                position: absolute;
                left: 0;
                bottom: 0;
                width: 235px;
                height: 77px;
                background-color: #b7b9ab;
            }}
            .bottom-right-box {{
                position: absolute;
                right: 70px;
                bottom: 0;
                width: 374px;
                height: 58px;
                background-color: #b7b9ab;
            }}
            .container {{
                padding: 80px 100px 80px 170px;
                display: flex;
                flex-direction: column;
                height: 100%;
                box-sizing: border-box;
            }}
            .header {{
                margin-bottom: 20px;
            }}
            .main-title {{
                font-size: {main_title_font_size};
                font-weight: 700;
                margin: 0;
                line-height: 1.1;
                letter-spacing: -2px;
                color: {main_title_color};
            }}
            .subtitle {{
                font-size: {subtitle_font_size};
                font-weight: 300;
                margin-top: 5px;
                opacity: 0.8;
                color: {subtitle_color};
            }}
            .legend-container {{
                display: flex;
                gap: 60px;
                margin: 40px 0;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 20px;
            }}
            .legend-circle {{
                width: 45px;
                height: 45px;
                border-radius: 50%;
                border: 2px solid var(--grid-line);
            }}
            .legend-label {{
                font-size: 42px;
                font-weight: 700;
                color: var(--text-default);
                letter-spacing: -0.5px;
            }}
            .content-layout {{
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .table-wrapper {{
                width: 100%;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 10px 30px rgba(0,0,0,0.05);
                border: 1px solid var(--grid-line);
            }}
        </style>
    </head>
    <body>
        <div class="left-bar"></div>
        <div class="top-box-mini"></div>
        <div class="bottom-left-box"></div>
        <div class="bottom-right-box"></div>
        
        <div class="container">
            <div class="header">
                <h1 class="main-title">{main_title}</h1>
                <div class="subtitle">{subtitle}</div>
            </div>
            
            {legend_html}
            
            <div class="content-layout">
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th style="padding: 20px; border: 1px solid {grid_color}; text-align: left; background: {bg_light};"></th>
                                {header_html}
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_code
