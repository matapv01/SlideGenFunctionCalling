import os

new_function = """

# ==========================================================
# 2. SLIDE WARM INTRO (Tông màu ấm, lề phải)
# ==========================================================
def generate_warm_intro_slide_xml(
    title: str = "Intro Template",
    subtitle: str = "Choose a topic and audience to generate a tailored introductory presentation",
    background_color: str = "#F2E6DF",
    title_color: str = "#5C4640",
    subtitle_color: str = "#A0716A",
) -> str:
    \"\"\"
    Sinh ra file XML cho slide Warm Intro với SVG background tông ấm (Be, Đào, Nâu) 
    và các khối văn bản căn lề phải, hỗ trợ tự động co chữ, ngắt dòng.
    \"\"\"
    slide_width = 1600
    slide_height = 900

    presentation = ET.Element(
        "presentation",
        schemaVersion="1.0",
        width=str(slide_width),
        height=str(slide_height),
        slideWidthInches="13.333",
        slideHeightInches="7.5",
    )

    slide = ET.SubElement(
        presentation,
        "slide",
        background=background_color,
    )

    # 1. Background (Watercolor blobs)
    bg_xml = f\"\"\"
    <svg x="0" y="0" width="{slide_width}" height="{slide_height}">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="100%" height="100%">
            <!-- Top Right Pink Blob -->
            <path d="M 1200 -50 C 1200 -50 1450 100 1650 50 C 1650 50 1650 400 1500 350 C 1350 300 1350 -50 1200 -50 Z" fill="#F4BDB3" opacity="0.8"/>
            
            <!-- Bottom Right Taupe Blob -->
            <path d="M 1400 1000 C 1400 1000 1450 750 1650 700 C 1650 700 1700 1000 1400 1000 Z" fill="#C2B7B2" opacity="0.8"/>
            
            <!-- Bottom Left Orange/Peach Blob -->
            <path d="M -50 950 C -50 950 100 650 300 850 C 500 1050 800 900 800 1050 C 800 1050 -50 1050 -50 950 Z" fill="#F5C4A6" opacity="0.7"/>
            
            <!-- Top Left Giant Brown Blob -->
            <path d="M -150 -150 C -150 -150 400 -50 550 100 C 700 250 550 500 400 650 C 250 800 -50 900 -200 900 Z" fill="#755E59" opacity="0.9"/>
            
            <!-- Overlay Bottom Left Dark Brown Blob -->
            <path d="M -100 550 C -100 550 200 500 250 800 C 300 1100 -50 1100 -100 550 Z" fill="#885A48" opacity="0.9"/>
        </svg>
    </svg>
    \"\"\"
    svg_element = ET.fromstring(bg_xml)
    slide.append(svg_element)

    # 2. Xử lý Textbox với tính năng Ruler (Ràng buộc lề phải)
    def textbox(
        text: str,
        x: float,
        y: float,
        width: float,
        height: float,
        font: str,
        font_path: str,
        size: float,
        min_font_size: float,
        color: str,
        align: str,
        vertical_align: str,
        single_line: bool,
        max_lines: int,
        overflow: str,
        reflow_on_resize: str,
        line_spacing: float,
        safety_ratio: float,
        margin_left: float,
        margin_right: float,
        margin_top: float,
        margin_bottom: float,
        bold: bool = False,
    ):
        try:
            image_font = ImageFont.truetype(font_path, int(size))
        except Exception:
            try:
                import sys
                fallback_path = "C:/Windows/Fonts/arial.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
                image_font = ImageFont.truetype(fallback_path, int(size))
            except Exception:
                image_font = ImageFont.load_default()
        
        words = str(text).split()
        if not words:
            return

        current_size = size
        lines = []

        while current_size >= min_font_size:
            try:
                test_font = ImageFont.truetype(font_path, int(current_size))
            except Exception:
                test_font = ImageFont.load_default()
            
            lines = []
            current_line = []
            
            for word in words:
                test_line = " ".join(current_line + [word])
                bbox = test_font.getbbox(test_line)
                w = bbox[2] - bbox[0]
                
                if w <= width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
            
            if current_line:
                lines.append(" ".join(current_line))
                
            if len(lines) <= max_lines:
                break
                
            current_size -= 2

        tb = ET.SubElement(
            slide,
            "textbox",
            x=str(x),
            y=str(y),
            width=str(width),
            height=str(height),
            font=font,
            size=str(current_size),
            min_font_size=str(min_font_size),
            color=color,
            align=align,
            vertical_align=vertical_align,
            single_line=str(single_line).lower(),
            max_lines=str(max_lines),
            overflow=overflow,
            reflow_on_resize=reflow_on_resize,
            line_spacing=str(line_spacing),
            safety_ratio=str(safety_ratio),
            margin_left=str(margin_left),
            margin_right=str(margin_right),
            margin_top=str(margin_top),
            margin_bottom=str(margin_bottom),
        )
        if bold:
            tb.set("bold", "true")
        tb.text = text

    # Các hằng số layout
    import sys
    font_path_regular = "C:/Windows/Fonts/arial.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
    font_path_bold = "C:/Windows/Fonts/arialbd.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial Bold.ttf"

    # Text container ở nửa bên phải (right-aligned)
    text_container_width = 800
    text_container_x = slide_width - text_container_width - 80 # Margin right = 80
    
    # Tính y_offset (chữ ở giữa theo chiều dọc)
    y_offset = slide_height / 2 + 50
    
    # Subtitle
    textbox(
        subtitle,
        x=text_container_x,
        y=y_offset + 20,
        width=text_container_width,
        height=140,
        font="Arial",
        font_path=font_path_regular,
        size=40,
        min_font_size=28,
        color=subtitle_color,
        align="right",
        vertical_align="top",
        single_line=False,
        max_lines=2,
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=1.1,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )
    
    # Title (Nằm ngay bên trên Subtitle)
    textbox(
        title,
        x=text_container_x,
        y=y_offset - 100,
        width=text_container_width,
        height=120,
        font="Arial",
        font_path=font_path_bold,
        size=96,
        min_font_size=64,
        color=title_color,
        align="right",
        vertical_align="bottom",
        single_line=False,
        max_lines=1,
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=1.0,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        bold=True,
    )

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    xml_content = minidom.parseString(
        raw_xml
    ).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content
"""

with open(r"backend\workflows\slidegen_workflow\tools\xml_tool.py", "a", encoding="utf-8") as f:
    f.write(new_function)

print("Appended generate_warm_intro_slide_xml to xml_tool.py")
