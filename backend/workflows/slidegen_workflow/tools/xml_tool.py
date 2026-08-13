from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom
import os
from PIL import ImageFont



# ==========================================================
# 1. SLIDE INTRO (Giới thiệu, Cover)
# ==========================================================
def generate_intro_slide_xml(
    title: str = "Intro Template",
    subtitle: str = "Choose a topic and audience to generate a tailored introductory presentation",
    background_color: str = "#F4F6F7",
    title_color: str = "#1C4670",
    subtitle_color: str = "#38618C",
) -> str:
    """
    Sinh XML cho slide Intro (Tiêu đề chính) với background SVG blob.
    Tích hợp thuật toán đo đạc và co giãn text tự động.
    """
    import os

    if not title.strip():
        raise ValueError("title không được để trống")

    canvas_width = 1600
    canvas_height = 900

    content_max_width = 1200
    content_max_height = 500
    content_x = (canvas_width - content_max_width) / 2

    def normalize_font_name(name: str) -> str:
        return "".join(
            char.lower()
            for char in name
            if char.isalnum()
        )

    def font_directories() -> list[str]:
        from pathlib import Path
        directories: list[Path] = []
        windir = os.environ.get("WINDIR")
        if windir:
            directories.append(Path(windir) / "Fonts")
        directories.extend([
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path.home() / "Library/Fonts",
            Path("/Library/Fonts"),
        ])
        return [path for path in directories if path.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ):
        from pathlib import Path
        aliases = {
            "Arial": "arial",
            "Georgia": "georgia",
            "Calibri": "calibri",
            "Aptos": "aptos",
            "Times New Roman": "times",
        }
        normalized = normalize_font_name(aliases.get(font_name, font_name))
        candidates = []
        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue
            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue
                stem = normalize_font_name(path.stem)
                if normalized not in stem:
                    continue
                score = 70
                if stem == normalized:
                    score += 30
                has_bold = any(token in stem for token in ("bold", "bd", "semibold"))
                has_italic = any(token in stem for token in ("italic", "it", "oblique"))
                if bold and has_bold: score += 20
                elif bold: score -= 10
                elif has_bold: score -= 10
                if italic and has_italic: score += 20
                elif italic: score -= 10
                elif has_italic: score -= 10
                candidates.append((score, path))
        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            return candidates[0][1]

        from PIL import ImageFont
        fallback_name = (
            "DejaVuSans-BoldOblique.ttf" if bold and italic else
            "DejaVuSans-Bold.ttf" if bold else
            "DejaVuSans-Oblique.ttf" if italic else "DejaVuSans.ttf"
        )
        font = ImageFont.truetype(fallback_name, 12)
        font_path = getattr(font, "path", None)
        if not font_path:
            raise ValueError(f"Không tìm thấy font '{font_name}'")
        return Path(font_path)

    canvas_dpi = 120.0
    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path, font_size_pt: float):
        from PIL import ImageFont
        return ImageFont.truetype(str(font_path), max(1, round(pt_to_canvas(font_size_pt))))

    def measure_text_width(text: str, font_path, font_size_pt: float) -> float:
        font = load_font(font_path, font_size_pt)
        if hasattr(font, "getlength"):
            return float(font.getlength(text))
        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(font_path, font_size_pt: float, line_spacing: float) -> float:
        font = load_font(font_path, font_size_pt)
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

    def break_long_word(word: str, font_path, font_size_pt: float, max_width: float) -> list[str]:
        parts = []
        current = ""
        for char in word:
            candidate = current + char
            if current and measure_text_width(candidate, font_path, font_size_pt) > max_width:
                parts.append(current)
                current = char
            else:
                current = candidate
        if current:
            parts.append(current)
        return parts or [""]

    def wrap_text(text: str, font_path, font_size_pt: float, max_width: float) -> list[str]:
        result = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                result.append("")
                continue
            current = ""
            for word in words:
                if measure_text_width(word, font_path, font_size_pt) > max_width:
                    pieces = break_long_word(word, font_path, font_size_pt, max_width)
                else:
                    pieces = [word]
                for piece in pieces:
                    candidate = piece if not current else f"{current} {piece}"
                    if not current or measure_text_width(candidate, font_path, font_size_pt) <= max_width:
                        current = candidate
                    else:
                        result.append(current)
                        current = piece
            if current:
                result.append(current)
        return result or [""]

    def layout_text(text: str, font_path, font_size: float, max_width: float, line_spacing: float, padding: float = 6):
        lines = wrap_text(text, font_path, font_size, max_width)
        line_height = measure_line_height(font_path, font_size, line_spacing)
        return {
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": len(lines) * line_height + padding,
        }

    title_font_name = "Arial"
    subtitle_font_name = "Arial"

    title_font_path = resolve_font_path(title_font_name, bold=True)
    subtitle_font_path = resolve_font_path(subtitle_font_name, bold=False)

    title_font_size = 96.0
    title_min_font_size = 48.0
    subtitle_font_size = 36.0
    subtitle_min_font_size = 20.0

    title_line_spacing = 1.05
    subtitle_line_spacing = 1.1

    gap = 40.0
    minimum_gap = 20.0

    def calculate_layouts(c_title_size, c_subtitle_size):
        t_layout = layout_text(title, title_font_path, c_title_size, content_max_width, title_line_spacing, 10)
        s_layout = layout_text(subtitle, subtitle_font_path, c_subtitle_size, content_max_width, subtitle_line_spacing, 10)
        return t_layout, s_layout

    t_layout, s_layout = calculate_layouts(title_font_size, subtitle_font_size)
    total_height = t_layout["height"] + gap + s_layout["height"] if subtitle.strip() else t_layout["height"]

    for _ in range(200):
        if total_height <= content_max_height:
            break
        changed = False
        if gap > minimum_gap:
            gap = max(minimum_gap, gap - 2)
            changed = True
        elif subtitle_font_size > subtitle_min_font_size:
            subtitle_font_size = max(subtitle_min_font_size, subtitle_font_size - 1)
            changed = True
        elif title_font_size > title_min_font_size:
            title_font_size = max(title_min_font_size, title_font_size - 1)
            changed = True
        
        if not changed:
            break
        
        t_layout, s_layout = calculate_layouts(title_font_size, subtitle_font_size)
        total_height = t_layout["height"] + gap + s_layout["height"] if subtitle.strip() else t_layout["height"]

    if total_height > content_max_height:
        raise ValueError("Nội dung quá dài để đặt vừa slide.")

    group_y = (canvas_height - total_height) / 2
    title_y = group_y
    subtitle_y = group_y + t_layout["height"] + gap

    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    presentation = ET.Element("presentation", {
        "schemaVersion": "1.0",
        "width": str(canvas_width),
        "height": str(canvas_height),
        "slideWidthInches": "13.333",
        "slideHeightInches": "7.5",
    })

    slide = ET.SubElement(presentation, "slide", {"background": background_color})

    def add(tag: str, **attrs):
        return ET.SubElement(slide, tag, {key: str(value) for key, value in attrs.items() if value is not None})

    def add_textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    svg_node = add(
        "svg",
        x="0", y="0",
        width=str(canvas_width), height=str(canvas_height),
        pixel_width=str(canvas_width), pixel_height=str(canvas_height)
    )
    svg_node.text = """
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" style="background: transparent;">
  <rect width="1600" height="900" fill="#F4F6F7" />
  <path d="M0,0 L0,300 C150,250 200,100 400,0 Z" fill="#E2E8EC" />
  <path d="M0,550 C150,550 250,750 550,900 L0,900 Z" fill="#9ACAED" />
  <path d="M0,750 C100,750 150,850 350,900 L0,900 Z" fill="#1C4670" />
  <path d="M1200,0 C1250,150 1450,200 1600,300 L1600,0 Z" fill="#9ACAED" />
  <path d="M1350,0 C1350,80 1450,120 1600,150 L1600,0 Z" fill="#1C4670" />
  <path d="M1300,900 C1350,700 1500,600 1600,550 L1600,900 Z" fill="#E2E8EC" />
  <circle cx="280" cy="680" r="10" fill="#1C4670" />
  <circle cx="580" cy="830" r="15" fill="#1C4670" />
  <circle cx="170" cy="730" r="8" fill="#9ACAED" />
  <circle cx="1000" cy="50" r="18" fill="#1C4670" />
  <circle cx="1400" cy="200" r="10" fill="#9ACAED" />
  <circle cx="1580" cy="350" r="15" fill="#1C4670" />
  <circle cx="750" cy="850" r="8" fill="#9ACAED" />
</svg>
""".strip()

    add_textbox(
        t_layout["source_text"],
        x=content_x, y=title_y,
        width=content_max_width, height=t_layout["height"],
        font=title_font_name, size=t_layout["font_size"], min_font_size=t_layout["font_size"],
        color=title_color, bold="true", align="center", vertical_align="middle",
        single_line="false", max_lines=len(t_layout["lines"]), overflow="clip",
        line_spacing=title_line_spacing, safety_ratio=1.0,
        margin_left=0, margin_right=0, margin_top=0, margin_bottom=0
    )

    if subtitle.strip():
        add_textbox(
            s_layout["source_text"],
            x=content_x, y=subtitle_y,
            width=content_max_width, height=s_layout["height"],
            font=subtitle_font_name, size=s_layout["font_size"], min_font_size=s_layout["font_size"],
            color=subtitle_color, align="center", vertical_align="middle",
            single_line="false", max_lines=len(s_layout["lines"]), overflow="clip",
            line_spacing=subtitle_line_spacing, safety_ratio=1.0,
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0
        )

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    return minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")



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
    """
    Sinh ra file XML cho slide Warm Intro với SVG background tông ấm (Be, Đào, Nâu) 
    và các khối văn bản căn lề phải, hỗ trợ tự động co chữ, ngắt dòng.
    """
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
    svg_node = ET.SubElement(
        slide,
        "svg",
        x="0", y="0",
        width=str(slide_width), height=str(slide_height),
        pixel_width=str(slide_width), pixel_height=str(slide_height)
    )
    svg_node.text = f"""
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
""".strip()

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
    # Sử dụng font mảnh, thanh lịch cho slide Warm Intro thay vì Arial thô cứng
    font_path_regular = "C:/Windows/Fonts/segoeuil.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
    font_name = "Segoe UI Light"

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
        height=200,
        font=font_name,
        font_path=font_path_regular,
        size=40,
        min_font_size=24,
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
        font=font_name,
        font_path=font_path_regular,
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
        bold=False,  # Bỏ in đậm để nhìn mảnh mai, sang trọng hơn
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


# ==========================================================
# 3. SLIDE CREATIVE TEAM (Đội ngũ sáng tạo)
# ==========================================================
def generate_creative_team_slide_xml(
    title: str = "Our Creative Team",
    members: list[dict] = None,
    background_color: str = "#F0F0F0",
    title_color: str = "#594A42",
) -> str:
    """
    Sinh ra file XML cho slide Our Creative Team với 4 thẻ ảnh Polaroid nằm nghiêng nghệ thuật.
    """
    if members is None:
        members = [
            {"name": "Olivia Chen", "role": "Lead Designer", "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&h=500&fit=crop"},
            {"name": "Ben Carter", "role": "Photographer", "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=500&h=500&fit=crop"},
            {"name": "Aisha Khan", "role": "Content Strategist", "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=500&h=500&fit=crop"},
            {"name": "Leo Martinez", "role": "Illustrator", "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=500&h=500&fit=crop"},
        ]
        
    # Giới hạn tối đa 4 thành viên cho layout này
    members = members[:4]

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

    # Các hằng số layout
    import sys
    font_path_regular = "C:/Windows/Fonts/comic.ttf" if sys.platform == "win32" else "/Library/Fonts/Comic Sans MS.ttf"
    font_path_bold = "C:/Windows/Fonts/comicbd.ttf" if sys.platform == "win32" else "/Library/Fonts/Comic Sans MS Bold.ttf"

    def add_textbox(**kwargs):
        tb = ET.SubElement(slide, "textbox")
        for k, v in kwargs.items():
            if k == 'text':
                tb.text = str(v)
            else:
                tb.set(k, str(v))
        return tb

    # 1. Title
    add_textbox(
        text=title,
        x=0,
        y=70,
        width=slide_width,
        height=120,
        font="Comic Sans MS",
        font_path=font_path_bold,
        size=72,
        min_font_size=48,
        color=title_color,
        align="center",
        vertical_align="middle",
        single_line="true",
        max_lines=1,
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=1.0,
        safety_ratio=1.0,
        margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
        bold="true",
    )

    # 2. Polaroids
    # Khung chứa 4 thẻ
    total_cards = len(members)
    card_width = 300
    card_height = 440
    gap = 40
    total_width = total_cards * card_width + (total_cards - 1) * gap
    start_x = (slide_width - total_width) / 2
    start_y = 230
    
    # Góc nghiêng cho 4 thẻ để tạo cảm giác tự nhiên ngẫu nhiên
    rotations = [-3, 2, -1, 4]

    for i, member in enumerate(members):
        x = start_x + i * (card_width + gap)
        y = start_y
        rot = rotations[i % len(rotations)]
        
        # Shadow giả lập đằng sau (Hình chữ nhật xám mờ bị dịch xuống và sang phải)
        rect_shadow = ET.SubElement(
            slide,
            "shape",
            type="rectangle",
            x=str(x + 8),
            y=str(y + 12),
            width=str(card_width),
            height=str(card_height),
            fill="#CCCCCC",
            rotation=str(rot),
        )
        
        # Polaroid Card Background (Hình chữ nhật trắng)
        rect_bg = ET.SubElement(
            slide,
            "shape",
            type="rectangle",
            x=str(x),
            y=str(y),
            width=str(card_width),
            height=str(card_height),
            fill="#FFFFFF",
            rotation=str(rot),
        )
        
        # Ảnh đại diện (vuông)
        img_size = 260
        img_x = x + 20
        img_y = y + 20
        
        img = ET.SubElement(
            slide,
            "image",
            x=str(img_x),
            y=str(img_y),
            width=str(img_size),
            height=str(img_size),
            src=member.get("image_url", ""),
            rotation=str(rot),
        )
        
        # Tên nhân sự
        name_y = img_y + img_size + 25
        add_textbox(
            text=member.get("name", "Name"),
            x=x,
            y=name_y,
            width=card_width,
            height=40,
            font="Comic Sans MS",
            font_path=font_path_bold,
            size=28,
            min_font_size=20,
            color="#333333",
            align="center",
            vertical_align="middle",
            single_line="true",
            max_lines=1,
            overflow="shrink",
            reflow_on_resize="true",
            line_spacing=1.0,
            safety_ratio=1.0,
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
            bold="true",
            rotation=str(rot),
        )
        
        # Chức danh
        role_y = name_y + 45
        add_textbox(
            text=member.get("role", "Role"),
            x=x,
            y=role_y,
            width=card_width,
            height=30,
            font="Comic Sans MS",
            font_path=font_path_regular,
            size=18,
            min_font_size=14,
            color="#777777",
            align="center",
            vertical_align="middle",
            single_line="true",
            max_lines=1,
            overflow="shrink",
            reflow_on_resize="true",
            line_spacing=1.0,
            safety_ratio=1.0,
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
            rotation=str(rot),
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


# ==========================================================
# 4. SLIDE GRID TEAM (2x2 Grid)
# ==========================================================
def generate_grid_team_slide_xml(
    title: str = "Add a Team\nMembers\nPage",
    members: list[dict] = None,
    background_color: str = "#F3F6F9",
    title_color: str = "#1A2530",
) -> str:
    """
    Sinh ra file XML cho slide Add a Team Members Page với Grid 2x2.
    """
    if members is None:
        members = [
            {"name": "Olivia Chen", "role": "Lead Designer", "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300&h=300&fit=crop"},
            {"name": "Ben Carter", "role": "Frontend Developer", "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300&h=300&fit=crop"},
            {"name": "Aisha Khan", "role": "Project Manager", "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&h=300&fit=crop"},
            {"name": "Leo Martinez", "role": "Marketing Head", "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=300&h=300&fit=crop"},
        ]
        
    members = members[:4]

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

    import sys
    font_path_regular = "C:/Windows/Fonts/segoeui.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
    font_path_bold = "C:/Windows/Fonts/segoeuib.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial Bold.ttf"
    font_path_black = "C:/Windows/Fonts/ariblk.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial Black.ttf"

    def add_textbox(**kwargs):
        tb = ET.SubElement(slide, "textbox")
        for k, v in kwargs.items():
            if k == 'text':
                tb.text = str(v)
            else:
                tb.set(k, str(v))
        return tb

    # 1. Title (Left side)
    add_textbox(
        text=title,
        x=120,
        y=220,
        width=650,
        height=340,
        font="Arial Black",
        font_path=font_path_black,
        size=72,
        min_font_size=48,
        color=title_color,
        align="left",
        vertical_align="bottom",
        single_line="false",
        max_lines=3,
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=1.0,
        safety_ratio=1.0,
        margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
        bold="true",
    )
    
    # Colorful gradient line below title
    colors = ["#8E44AD", "#27AE60", "#E74C3C", "#F1C40F"]
    line_y = 575
    for i, color in enumerate(colors):
        ET.SubElement(
            slide, "shape", type="rectangle",
            x=str(120 + i * 20), y=str(line_y),
            width="20", height="6",
            fill=color,
            line_color="none"
        )

    # 2. Grid (Right side)
    card_width = 320
    card_height = 180
    img_size = 120
    col_gap = 40
    row_gap = 100
    
    start_x = 750
    start_y = 200

    for i, member in enumerate(members):
        col = i % 2
        row = i // 2
        
        x = start_x + col * (card_width + col_gap)
        y = start_y + row * (card_height + row_gap)
        color = colors[i % len(colors)]
        
        # Shadow
        ET.SubElement(
            slide, "shape", type="rounded_rectangle",
            x=str(x + 8), y=str(y + 12),
            width=str(card_width), height=str(card_height),
            fill="#E1E5EB",
            line_color="none"
        )
        
        # White Card
        ET.SubElement(
            slide, "shape", type="rounded_rectangle",
            x=str(x), y=str(y),
            width=str(card_width), height=str(card_height),
            fill="#FFFFFF",
            line_color="none"
        )
        
        # Image Border Ring
        img_x = x + (card_width - img_size) / 2
        img_y = y - (img_size / 2)
        ET.SubElement(
            slide, "shape", type="circle",
            x=str(img_x - 6), y=str(img_y - 6),
            width=str(img_size + 12), height=str(img_size + 12),
            fill=color,
            line_color="none"
        )
        # Inner white ring
        ET.SubElement(
            slide, "shape", type="circle",
            x=str(img_x - 3), y=str(img_y - 3),
            width=str(img_size + 6), height=str(img_size + 6),
            fill="#FFFFFF",
            line_color="none"
        )
        
        # Image (circle shaped)
        ET.SubElement(
            slide, "image",
            x=str(img_x), y=str(img_y),
            width=str(img_size), height=str(img_size),
            src=member.get("image_url", ""),
            shape="circle"
        )
        
        # Name
        name_y = img_y + img_size + 20
        add_textbox(
            text=member.get("name", "Name"),
            x=x, y=name_y,
            width=card_width, height=35,
            font="Segoe UI", font_path=font_path_bold,
            size=24, min_font_size=18,
            color="#2C3E50", align="center", vertical_align="middle",
            single_line="true", max_lines=1, overflow="shrink", reflow_on_resize="true",
            line_spacing=1.0, safety_ratio=1.0,
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
            bold="true",
        )
        
        # Role
        role_y = name_y + 35
        add_textbox(
            text=member.get("role", "Role"),
            x=x, y=role_y,
            width=card_width, height=30,
            font="Segoe UI", font_path=font_path_regular,
            size=16, min_font_size=12,
            color="#7F8C8D", align="center", vertical_align="middle",
            single_line="true", max_lines=1, overflow="shrink", reflow_on_resize="true",
            line_spacing=1.0, safety_ratio=1.0,
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
        )

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    return xml_content

# ==========================================================
# 5. ELEGANT EDUCATION TITLE SLIDE
# ==========================================================
def cubic_bezier(t, p0, p1, p2, p3):
    x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
    y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
    return x, y

def clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    t0 = 0.0
    t1 = 1.0
    dx = x2 - x1
    dy = y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]
    for i in range(4):
        if p[i] == 0:
            if q[i] < 0: return None
        else:
            t = q[i] / p[i]
            if p[i] < 0:
                if t > t1: return None
                if t > t0: t0 = t
            else:
                if t < t0: return None
                if t < t1: t1 = t
    if t0 <= t1:
        return (x1 + t0*dx, y1 + t0*dy, x1 + t1*dx, y1 + t1*dy)
    return None

def generate_elegant_education_slide_xml(
    title: str = "Elegant Education\nPack for Students",
    subtitle: str = "Here is where your presentation begins",
    background_color: str = "#FFFFFF",
    title_color: str = "#3F474A",
    subtitle_color: str = "#515558",
) -> str:
    """
    Sinh XML cho slide Elegant Education Title với SVG patterns và co giãn text tự động.
    """
    if not title.strip():
        raise ValueError("title không được để trống")

    import sys
    import math
    canvas_width = 1600
    canvas_height = 900
    content_max_width = 1300
    content_max_height = 500
    content_x = (canvas_width - content_max_width) / 2

    font_path_regular = "C:/Windows/Fonts/segoeui.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
    font_path_black = "C:/Windows/Fonts/ariblk.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial Black.ttf"

    presentation = ET.Element(
        "presentation",
        schemaVersion="1.0",
        width=str(canvas_width),
        height=str(canvas_height),
        slideWidthInches="13.333",
        slideHeightInches="7.5",
    )
    slide = ET.SubElement(presentation, "slide", background=background_color)
    
    # ---------------- NATIVE SHAPES INSTEAD OF SVG ----------------
    
    # Top Left Gray Blob
    pts = [(0, 0), (600, 0)]
    for i in range(1, 21):
        t = i / 20.0
        x, y = cubic_bezier(t, (600, 0), (500, 250), (200, 200), (0, 500))
        pts.append((int(x), int(y)))
    top_left_points = " ".join([f"{x},{y}" for x, y in pts])
    ET.SubElement(slide, "polygon", points=top_left_points, fill="#9D9C8D", line_color="none")
    
    # Bottom Left Gray Blob
    ET.SubElement(slide, "shape", type="circle", x="200", y="650", width="100", height="130", fill="#A4A69B", line_color="none")
    
    # Right Brown Blob (clipped to right edge)
    pts_brown = []
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        x = 1525 + 175 * math.cos(rad)
        y = 275 + 175 * math.sin(rad)
        if x > 1600:
            x = 1600
        pts_brown.append((int(x), int(y)))
    brown_points = " ".join([f"{x},{y}" for x, y in pts_brown])
    ET.SubElement(slide, "polygon", points=brown_points, fill="#CDA590", line_color="none")
    
    # Bottom Brown Bar
    ET.SubElement(slide, "shape", type="rectangle", x="0", y="840", width="1600", height="60", fill="#C8A590", line_color="none")
    
    # Top Right Geometric Pattern (Honeycomb grid using native <line> elements to avoid opaque fill)
    lines_to_draw = []
    
    R = 45
    dx = R * math.sqrt(3)  # ~78
    dy = R * 1.5           # 67.5
    
    start_x = 1250
    start_y = 0
    centers = []
    for row in range(5):
        y = start_y + row * dy
        x_offset = start_x if row % 2 == 0 else start_x + dx / 2
        for col in range(6):
            x = x_offset + col * dx
            centers.append((x, y))
            
    for cx, cy in centers:
        hex_pts = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            hex_pts.append((cx + R * math.cos(angle_rad), cy + R * math.sin(angle_rad)))
        
        for i in range(6):
            p1 = hex_pts[i]
            p2 = hex_pts[(i+1)%6]
            lines_to_draw.append((p1[0], p1[1], p2[0], p2[1]))

    for x1, y1, x2, y2 in lines_to_draw:
        # Clip to the slide canvas so they don't overflow
        clipped = clip_line(x1, y1, x2, y2, 0, 0, 1600, 900)
        if clipped:
            cx1, cy1, cx2, cy2 = clipped
            ET.SubElement(slide, "line", x1=str(int(cx1)), y1=str(int(cy1)), x2=str(int(cx2)), y2=str(int(cy2)), color="#3F474A", width="1")

    # Title TextBox
    title_tb = ET.SubElement(
        slide, "textbox",
        x=str(content_x), y="320",
        width=str(content_max_width), height="200",
        font="Arial Black", font_path=font_path_black,
        size="100", min_font_size="48",
        color=title_color, align="center", vertical_align="bottom",
        single_line="false", max_lines="3", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.1", bold="true"
    )
    title_tb.text = title

    # Subtitle TextBox
    if subtitle.strip():
        sub_tb = ET.SubElement(
            slide, "textbox",
            x=str(content_x), y="550",
            width=str(content_max_width), height="100",
            font="Segoe UI", font_path=font_path_regular,
            size="40", min_font_size="24",
            color=subtitle_color, align="center", vertical_align="top",
            single_line="false", max_lines="2", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.2"
        )
        sub_tb.text = subtitle

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    return minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

# ==========================================================
# 6. ONLINE NOTEBOOK TITLE SLIDE
# ==========================================================
def rot(x, y, cx, cy, deg):
    import math
    rad = math.radians(deg)
    nx = cx + (x - cx)*math.cos(rad) - (y - cy)*math.sin(rad)
    ny = cy + (x - cx)*math.sin(rad) + (y - cy)*math.cos(rad)
    return int(nx), int(ny)

def generate_online_notebook_slide_xml(
    title: str = "ONLINE NOTEBOOK",
    subtitle: str = "Here is where your presentation begins",
    background_color: str = "#FFFFFF",
    title_color: str = "#1E4E8C",
    subtitle_color: str = "#2C3E50",
) -> str:
    """
    Sinh XML cho slide Online Notebook Title với các rule co giãn text nghiêm ngặt.
    Phiên bản Premium: faked shadows, inward circular corners, realistic props, Arial Rounded font.
    """
    import sys
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    import math

    if not title.strip():
        raise ValueError("title không được để trống")
        
    words = title.strip().split(" ", 1)
    title1 = words[0]
    title2 = words[1] if len(words) > 1 else ""

    canvas_width = 1600
    canvas_height = 900

    # Fonts
    font_path_regular = "C:/Windows/Fonts/segoeui.ttf" if sys.platform == "win32" else "/Library/Fonts/Arial.ttf"
    # Dùng Arial Rounded MT Bold cho cảm giác marker/notebook
    font_path_bold = "C:/Windows/Fonts/ARLRDBD.TTF" if sys.platform == "win32" else "/Library/Fonts/Arial Bold.ttf"

    presentation = ET.Element(
        "presentation",
        schemaVersion="1.0",
        width=str(canvas_width),
        height=str(canvas_height),
        slideWidthInches="13.333",
        slideHeightInches="7.5",
    )
    slide = ET.SubElement(presentation, "slide", background=background_color)
    
    # 1. Background
    # Left Polygon (Light Blue)
    bg_pts = [(0, 0), (600, 0), (1600, 900), (0, 900)]
    bg_points_str = " ".join([f"{x},{y}" for x, y in bg_pts])
    ET.SubElement(slide, "polygon", points=bg_points_str, fill="#B8D3F8", line_color="none")
    
    # Left Dark Blue Bar
    ET.SubElement(slide, "shape", type="rectangle", x="0", y="0", width="80", height="900", fill="#77A3EA", line_color="none")

    # 2. Ticket Badge (with faked drop shadow)
    R = 40
    X, Y, W, H = 250, 150, 1100, 600
    
    # Build ticket points with circular arcs for inward corners
    ticket_pts = []
    # Top-left cutout: Center (X, Y), arc from 90 to 0 degrees
    for deg in range(90, -1, -10):
        rad = math.radians(deg)
        ticket_pts.append((int(X + R*math.cos(rad)), int(Y + R*math.sin(rad))))
    
    # Top-right cutout: Center (X+W, Y), arc from 180 to 90 degrees
    for deg in range(180, 89, -10):
        rad = math.radians(deg)
        ticket_pts.append((int(X+W + R*math.cos(rad)), int(Y + R*math.sin(rad))))
        
    # Bottom-right cutout: Center (X+W, Y+H), arc from 270 to 180 degrees
    for deg in range(270, 179, -10):
        rad = math.radians(deg)
        ticket_pts.append((int(X+W + R*math.cos(rad)), int(Y+H + R*math.sin(rad))))
        
    # Bottom-left cutout: Center (X, Y+H), arc from 360 to 270 degrees
    for deg in range(360, 269, -10):
        rad = math.radians(deg)
        ticket_pts.append((int(X + R*math.cos(rad)), int(Y+H + R*math.sin(rad))))

    # Shadow for Ticket
    shadow_pts = [(x+15, y+15) for x, y in ticket_pts]
    shadow_str = " ".join([f"{x},{y}" for x, y in shadow_pts])
    ET.SubElement(slide, "polygon", points=shadow_str, fill="#9ABAE5", line_color="none") # Drop shadow color blends with bg

    # Ticket Base
    ticket_points_str = " ".join([f"{x},{y}" for x, y in ticket_pts])
    ET.SubElement(slide, "polygon", points=ticket_points_str, fill="#FFFFFF", line_color="#000000", line_width="2")

    # 3. Eraser (Top Left)
    eraser_cx, eraser_cy = 250, 80
    eraser_deg = 20
    ew, eh = 80, 120
    
    eraser_base = [(-ew/2, -eh/2), (ew/2, -eh/2), (ew/2, eh/2), (-ew/2, eh/2)]
    eraser_top = [(-ew/2, -eh/2), (ew/2, -eh/2), (ew/2, 0), (-ew/2, 0)]
    eraser_bot = [(-ew/2, 0), (ew/2, 0), (ew/2, eh/2), (-ew/2, eh/2)]
    
    # Shadow
    e_shadow = [(x+10, y+10) for x, y in eraser_base]
    e_shadow_rot = [rot(px, py, 0, 0, eraser_deg) for px, py in e_shadow]
    e_shadow_str = " ".join([f"{int(x+eraser_cx)},{int(y+eraser_cy)}" for x, y in e_shadow_rot])
    ET.SubElement(slide, "polygon", points=e_shadow_str, fill="#9ABAE5", line_color="none")
    
    # Pink top
    e_top_rot = [rot(px, py, 0, 0, eraser_deg) for px, py in eraser_top]
    e_top_str = " ".join([f"{int(x+eraser_cx)},{int(y+eraser_cy)}" for x, y in e_top_rot])
    ET.SubElement(slide, "polygon", points=e_top_str, fill="#FFAFA3", line_color="#000000", line_width="2")
    
    # Beige bottom sleeve
    e_bot_rot = [rot(px, py, 0, 0, eraser_deg) for px, py in eraser_bot]
    e_bot_str = " ".join([f"{int(x+eraser_cx)},{int(y+eraser_cy)}" for x, y in e_bot_rot])
    ET.SubElement(slide, "polygon", points=e_bot_str, fill="#FFE5D9", line_color="#000000", line_width="2")

    # 4. Notebook Paper (Top Right)
    paper_cx, paper_cy = 1350, 180
    paper_deg = 12
    pw, ph = 240, 320
    paper_base = [(-pw/2, -ph/2), (pw/2, -ph/2), (pw/2, ph/2), (-pw/2, ph/2)]
    
    # Shadow
    p_shadow = [(x+12, y+12) for x, y in paper_base]
    p_shadow_rot = [rot(px, py, 0, 0, paper_deg) for px, py in p_shadow]
    p_shadow_str = " ".join([f"{int(x+paper_cx)},{int(y+paper_cy)}" for x, y in p_shadow_rot])
    # For white background, shadow needs to be light gray
    ET.SubElement(slide, "polygon", points=p_shadow_str, fill="#E0E0E0", line_color="none")
    
    # Paper white base
    p_base_rot = [rot(px, py, 0, 0, paper_deg) for px, py in paper_base]
    p_base_str = " ".join([f"{int(x+paper_cx)},{int(y+paper_cy)}" for x, y in p_base_rot])
    ET.SubElement(slide, "polygon", points=p_base_str, fill="#FFFFFF", line_color="#000000", line_width="2")
    
    # Lines inside paper
    for i in range(1, 7):
        line_y = -ph/2 + i * 45
        x1, x2 = -pw/2 + 20, pw/2 - 20
        rx1, ry1 = rot(x1, line_y, 0, 0, paper_deg)
        rx2, ry2 = rot(x2, line_y, 0, 0, paper_deg)
        ET.SubElement(slide, "line", 
                      x1=str(int(rx1+paper_cx)), y1=str(int(ry1+paper_cy)), 
                      x2=str(int(rx2+paper_cx)), y2=str(int(ry2+paper_cy)), 
                      color="#000000", width="1")

    # 5. Pen (Bottom Right)
    pen_cx, pen_cy = 1300, 750
    deg = -45
    # Build parts of pen around 0,0 and rotate
    pen_w = 26
    pen_l = 360
    
    # Shadow for entire pen (use the body+cap bounding rect)
    pen_shadow_pts = [(-pen_w/2+10, -pen_l/2+10), (pen_w/2+10, -pen_l/2+10), (pen_w/2+10, pen_l/2+10), (-pen_w/2+10, pen_l/2+10)]
    ps_rot = [rot(px, py, 0, 0, deg) for px, py in pen_shadow_pts]
    ps_str = " ".join([f"{int(x+pen_cx)},{int(y+pen_cy)}" for x, y in ps_rot])
    ET.SubElement(slide, "polygon", points=ps_str, fill="#9ABAE5", line_color="none")

    # Body
    body_pts = [(-pen_w/2, -pen_l/2 + 60), (pen_w/2, -pen_l/2 + 60), (pen_w/2, pen_l/2), (-pen_w/2, pen_l/2)]
    # Silver Cone Tip
    cone_pts = [(-pen_w/2, -pen_l/2 + 60), (pen_w/2, -pen_l/2 + 60), (6, -pen_l/2 + 20), (-6, -pen_l/2 + 20)]
    # Black tip
    tip_pts = [(-6, -pen_l/2 + 20), (6, -pen_l/2 + 20), (0, -pen_l/2)]
    # Cap (Top part of pen)
    cap_pts = [(-pen_w/2, pen_l/2 - 100), (pen_w/2, pen_l/2 - 100), (pen_w/2, pen_l/2), (-pen_w/2, pen_l/2)]
    # Clip (Silver piece on cap)
    clip_pts = [(-pen_w/2 - 6, pen_l/2 - 80), (-pen_w/2, pen_l/2 - 80), (-pen_w/2, pen_l/2 - 20), (-pen_w/2 - 6, pen_l/2 - 20)]
    
    shapes = [
        (tip_pts, "#000000"), 
        (cone_pts, "#D9D9D9"), 
        (body_pts, "#15466B"), 
        (cap_pts, "#0C304A"), 
        (clip_pts, "#D9D9D9")
    ]
    
    for shape_pts, fill in shapes:
        rot_pts = [rot(px, py, 0, 0, deg) for px, py in shape_pts]
        final_pts = [(rx + pen_cx, ry + pen_cy) for rx, ry in rot_pts]
        pts_str = " ".join([f"{int(x)},{int(y)}" for x, y in final_pts])
        ET.SubElement(slide, "polygon", points=pts_str, fill=fill, line_color="#000000", line_width="2")

    # Divider Line
    if title2:
        ET.SubElement(slide, "line", x1="450", y1="450", x2="1150", y2="450", color=title_color, width="4")

    # Title Part 1
    title1_tb = ET.SubElement(
        slide, "textbox",
        x="350", y="200",
        width="900", height="240",
        font="Arial Rounded MT Bold", font_path=font_path_bold,
        size="120", min_font_size="40",
        color=title_color, align="center", vertical_align="bottom",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="false"
    )
    title1_tb.text = title1

    # Title Part 2
    if title2:
        title2_tb = ET.SubElement(
            slide, "textbox",
            x="350", y="460",
            width="900", height="200",
            font="Arial Rounded MT Bold", font_path=font_path_bold,
            size="120", min_font_size="40",
            color=title_color, align="center", vertical_align="top",
            single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.0", bold="false"
        )
        title2_tb.text = title2

    # Subtitle TextBox
    if subtitle.strip():
        sub_tb = ET.SubElement(
            slide, "textbox",
            x="400", y="600" if not title2 else "660",
            width="800", height="100",
            font="Segoe UI", font_path=font_path_regular,
            size="36", min_font_size="20",
            color=subtitle_color, align="center", vertical_align="middle" if not title2 else "top",
            single_line="false", max_lines="2", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.2"
        )
        sub_tb.text = subtitle

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    return minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

# ==========================================================
# 7. CLASSIC TABLE OF CONTENTS SLIDE
# ==========================================================
def generate_classic_toc_slide_xml(
    title: str = "Table of contents",
    items: list = None,
    background_color: str = "#EBE4D5",
    theme_color: str = "#4A3F35",
) -> str:
    """
    Sinh XML cho slide Mục lục phong cách cổ điển (Classic/Vintage TOC).
    Có khung viền hoàng gia và hỗ trợ lưới 2x3 (tối đa 6 mục).
    """
    import sys
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    if items is None:
        items = []

    canvas_width = 1600
    canvas_height = 900

    # Fonts
    # Ưu tiên các font Serif cổ điển
    if sys.platform == "win32":
        font_path_serif = "C:/Windows/Fonts/georgia.ttf"
        font_path_serif_bold = "C:/Windows/Fonts/georgiab.ttf"
    else:
        font_path_serif = "/Library/Fonts/Georgia.ttf"
        font_path_serif_bold = "/Library/Fonts/Georgia Bold.ttf"

    presentation = ET.Element(
        "presentation",
        schemaVersion="1.0",
        width=str(canvas_width),
        height=str(canvas_height),
        slideWidthInches="13.333",
        slideHeightInches="7.5",
    )
    slide = ET.SubElement(presentation, "slide", background=background_color)
    
    # --- DECORATIVE BORDERS ---
    # Outer Border
    ox, oy, ow, oh = 40, 40, 1520, 820
    ET.SubElement(slide, "shape", type="rectangle", x=str(ox), y=str(oy), width=str(ow), height=str(oh), fill="none", line_color=theme_color, line_width="2")
    
    # Inner Border
    ix, iy, iw, ih = 60, 60, 1480, 780
    ET.SubElement(slide, "shape", type="rectangle", x=str(ix), y=str(iy), width=str(iw), height=str(ih), fill="none", line_color=theme_color, line_width="1")
    
    # 4 Corner Squares
    # Each square is placed such that its center is exactly where the outer and inner border would meet or just decorative.
    # The image shows squares placed at the 4 corners between inner and outer borders.
    sq_size = 30
    corners = [
        (ox - 5, oy - 5), # Top-left
        (ox + ow - sq_size + 5, oy - 5), # Top-right
        (ox - 5, oy + oh - sq_size + 5), # Bottom-left
        (ox + ow - sq_size + 5, oy + oh - sq_size + 5) # Bottom-right
    ]
    for cx, cy in corners:
        ET.SubElement(slide, "shape", type="rectangle", x=str(cx), y=str(cy), width=str(sq_size), height=str(sq_size), fill="none", line_color=theme_color, line_width="2")
        
    # --- MAIN TITLE ---
    title_tb = ET.SubElement(
        slide, "textbox",
        x="400", y="120",
        width="800", height="100",
        font="Georgia", font_path=font_path_serif,
        size="72", min_font_size="36",
        color=theme_color, align="center", vertical_align="middle",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="false"
    )
    title_tb.text = title

    # --- GRID ITEMS (Max 6) ---
    max_items = 6
    display_items = items[:max_items]
    
    # Tọa độ tâm các cột và hàng
    centers_x = [300, 800, 1300]
    centers_y = [340, 660]
    
    for idx, item in enumerate(display_items):
        row = idx // 3
        col = idx % 3
        
        cx = centers_x[col]
        cy = centers_y[row]
        
        box_width = 380
        start_x = cx - box_width // 2
        
        number = item.get("number", f"{idx+1:02d}")
        item_title = item.get("title", f"Section {idx+1}")
        description = item.get("description", "You can describe the topic of the section here")
        
        # Top line for number
        ET.SubElement(slide, "line", x1=str(cx - 50), y1=str(cy - 90), x2=str(cx + 50), y2=str(cy - 90), color=theme_color, width="2")
        
        # Number Textbox
        num_tb = ET.SubElement(
            slide, "textbox",
            x=str(start_x), y=str(cy - 80),
            width=str(box_width), height="50",
            font="Georgia", font_path=font_path_serif_bold,
            size="40", min_font_size="20",
            color=theme_color, align="center", vertical_align="middle",
            single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.0", bold="true"
        )
        num_tb.text = number
        
        # Bottom line for number
        ET.SubElement(slide, "line", x1=str(cx - 50), y1=str(cy - 30), x2=str(cx + 50), y2=str(cy - 30), color=theme_color, width="2")
        
        # Item Title Textbox
        it_tb = ET.SubElement(
            slide, "textbox",
            x=str(start_x), y=str(cy - 20),
            width=str(box_width), height="80",
            font="Georgia", font_path=font_path_serif_bold,
            size="24", min_font_size="24",
            color=theme_color, align="center", vertical_align="middle",
            single_line="false", max_lines="2", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.0", bold="true"
        )
        it_tb.text = item_title
        
        # Description Textbox
        desc_tb = ET.SubElement(
            slide, "textbox",
            x=str(start_x), y=str(cy + 70),
            width=str(box_width), height="50",
            font="Georgia", font_path=font_path_serif,
            size="16", min_font_size="16",
            color=theme_color, align="center", vertical_align="top",
            single_line="false", max_lines="2", overflow="shrink", reflow_on_resize="true",
            line_spacing="1.2", bold="false"
        )
        desc_tb.text = description

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    return minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
def generate_notebook_section_slide_xml(
    number: str = "01",
    title: str = "Introduction",
    subtitle: str = "You can enter a subtitle here if you need it",
    background_color: str = "#FFFFFF"
) -> str:
    """
    Generate a 'Back to School' notebook section slide.
    """
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    import math

    root = ET.Element("presentation")
    slide = ET.SubElement(root, "slide")
    
    # White Background
    ET.SubElement(slide, "polygon", points="0,0 1600,0 1600,900 0,900", fill=background_color, line_color="none")
    
    # Grid lines
    grid_color = "#E8F0F4"
    grid_size = 50
    for x in range(0, 1600, grid_size):
        ET.SubElement(slide, "line", x1=str(x), y1="0", x2=str(x), y2="900", color=grid_color, width="1")
    for y in range(0, 900, grid_size):
        ET.SubElement(slide, "line", x1="0", y1=str(y), x2="1600", y2=str(y), color=grid_color, width="1")

    # Helper to draw a stylized leaf (6-point polygon)
    def draw_leaf(parent, x, y, angle_deg, scale, color):
        pts = [
            (0, 0),
            (10 * scale, -6 * scale),
            (20 * scale, -6 * scale),
            (30 * scale, 0),
            (20 * scale, 6 * scale),
            (10 * scale, 6 * scale)
        ]
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        rotated_pts = []
        for px, py in pts:
            nx = x + px * cos_a - py * sin_a
            ny = y + px * sin_a + py * cos_a
            rotated_pts.append(f"{nx},{ny}")
        ET.SubElement(parent, "polygon", points=" ".join(rotated_pts), fill=color, line_color="none")
        
    # Helper to draw tilted rectangle (crayon body)
    def draw_tilted_rect(parent, cx, cy, w, h, angle_deg, color):
        hw, hh = w/2, h/2
        pts = [
            (-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)
        ]
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rotated_pts = []
        for px, py in pts:
            nx = cx + px * cos_a - py * sin_a
            ny = cy + px * sin_a + py * cos_a
            rotated_pts.append(f"{nx},{ny}")
        ET.SubElement(parent, "polygon", points=" ".join(rotated_pts), fill=color, line_color="none")

    # Helper to draw crayon tip
    def draw_tilted_triangle(parent, cx, cy, w, h, angle_deg, color):
        # Base width w, height h pointing up
        hw = w/2
        pts = [
            (-hw, 0), (hw, 0), (0, -h)
        ]
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rotated_pts = []
        for px, py in pts:
            nx = cx + px * cos_a - py * sin_a
            ny = cy + px * sin_a + py * cos_a
            rotated_pts.append(f"{nx},{ny}")
        ET.SubElement(parent, "polygon", points=" ".join(rotated_pts), fill=color, line_color="none")

    # 1. Top-Left Balloon
    balloon_color = "#F9E2A0"
    ET.SubElement(slide, "shape", type="circle", x="20", y="10", width="180", height="220", fill=balloon_color, line_color="none")
    ET.SubElement(slide, "polygon", points="100,225 120,225 110,245", fill=balloon_color, line_color="none")
    # String
    ET.SubElement(slide, "line", x1="110", y1="240", x2="105", y2="340", color="#A0A0A0", width="2")

    # 2. Top-Right Leaves (Autumn)
    leaf_colors = ["#F47C20", "#F9A826", "#E34A27"]
    draw_leaf(slide, 1470, 30, 130, 4.0, leaf_colors[0])
    draw_leaf(slide, 1420, 70, 160, 3.0, leaf_colors[1])
    draw_leaf(slide, 1500, 140, 100, 3.5, leaf_colors[2])
    draw_leaf(slide, 1470, 200, 110, 2.5, leaf_colors[0])
    draw_leaf(slide, 1390, 30, 170, 2.0, leaf_colors[2])

    # 3. Bottom-Left Backpack
    bp_x, bp_y = 30, 640
    bp_blue = "#5499C7"
    bp_dark = "#2980B9"
    # Main body
    ET.SubElement(slide, "shape", type="rounded_rectangle", x=str(bp_x), y=str(bp_y), width="220", height="240", fill=bp_blue, line_color="none")
    # Flap
    ET.SubElement(slide, "polygon", points=f"{bp_x},{bp_y+50} {bp_x+220},{bp_y+50} {bp_x+200},{bp_y+120} {bp_x+20},{bp_y+120}", fill=bp_dark, line_color="none")
    # Front pocket
    ET.SubElement(slide, "shape", type="rounded_rectangle", x=str(bp_x+20), y=str(bp_y+130), width="180", height="110", fill=bp_blue, line_color="none")
    # Keychains/Fluff
    ET.SubElement(slide, "shape", type="circle", x=str(bp_x+60), y=str(bp_y+150), width="40", height="40", fill="#F4D03F", line_color="none")
    ET.SubElement(slide, "shape", type="circle", x=str(bp_x+100), y=str(bp_y+170), width="35", height="35", fill="#E74C3C", line_color="none")
    # Straps (top handle)
    ET.SubElement(slide, "shape", type="circle", x=str(bp_x+60), y=str(bp_y-30), width="100", height="60", fill="none", line_color=bp_dark, line_width="10")

    # 4. Bottom-Right Crayons
    # Crayon 1: Green
    cx1, cy1, a1 = 1420, 720, -30
    draw_tilted_rect(slide, cx1, cy1, 40, 160, a1, "#F4E5D4") # Wrapper
    draw_tilted_rect(slide, cx1, cy1, 40, 40, a1, "#1E8449") # Band
    # Crayon green tip (offsetting center along angle)
    tx1 = cx1 + math.cos(math.radians(a1 - 90)) * 80
    ty1 = cy1 + math.sin(math.radians(a1 - 90)) * 80
    draw_tilted_triangle(slide, tx1, ty1, 40, 30, a1, "#1E8449")
    
    # Crayon 2: Blue
    cx2, cy2, a2 = 1270, 820, 45
    draw_tilted_rect(slide, cx2, cy2, 40, 160, a2, "#F4E5D4") # Wrapper
    draw_tilted_rect(slide, cx2, cy2, 40, 40, a2, "#2874A6") # Band
    tx2 = cx2 + math.cos(math.radians(a2 - 90)) * 80
    ty2 = cy2 + math.sin(math.radians(a2 - 90)) * 80
    draw_tilted_triangle(slide, tx2, ty2, 40, 30, a2, "#2874A6")

    # 5. Splatters (Random blue circles)
    splatters = [
        (600, 50, 15), (630, 40, 8), (590, 80, 10), (620, 90, 12),
        (1400, 500, 20), (1440, 480, 10), (1420, 530, 15),
        (350, 800, 18), (300, 850, 12)
    ]
    for sx, sy, sr in splatters:
        ET.SubElement(slide, "shape", type="circle", x=str(sx), y=str(sy), width=str(sr*2), height=str(sr*2), fill="#A9D9D9", line_color="none")
        
    # Sprinkles (Plus signs)
    def draw_plus(parent, cx, cy, size, color, width):
        ET.SubElement(parent, "line", x1=str(cx - size), y1=str(cy), x2=str(cx + size), y2=str(cy), color=color, width=width)
        ET.SubElement(parent, "line", x1=str(cx), y1=str(cy - size), x2=str(cx), y2=str(cy + size), color=color, width=width)
        
    draw_plus(slide, 320, 180, 15, "#F39C12", "3")
    draw_plus(slide, 1300, 250, 10, "#E74C3C", "3")
    draw_plus(slide, 1200, 750, 12, "#F39C12", "3")

    # --- TEXT BOXES ---
    # Number
    num_tb = ET.SubElement(
        slide, "textbox",
        x="600", y="230",
        width="400", height="120",
        font="Segoe UI", font_path="",
        size="96", min_font_size="60",
        color="#D56259", align="center", vertical_align="middle",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="true", italic="false"
    )
    num_tb.text = number

    # Title
    title_tb = ET.SubElement(
        slide, "textbox",
        x="200", y="380",
        width="1200", height="160",
        font="Arial", font_path="",
        size="110", min_font_size="50",
        color="#2E2E2E", align="center", vertical_align="middle",
        single_line="false", max_lines="2", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="true", italic="false"
    )
    title_tb.text = title

    # Subtitle
    sub_tb = ET.SubElement(
        slide, "textbox",
        x="300", y="600",
        width="1000", height="80",
        font="Segoe UI", font_path="",
        size="32", min_font_size="20",
        color="#555555", align="center", vertical_align="middle",
        single_line="false", max_lines="2", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.2", bold="false", italic="false"
    )
    sub_tb.text = subtitle

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    return xml_str
def generate_science_2col_slide_xml(
    main_title: str = "From molecules to life",
    col1_title: str = "Column 1",
    col1_desc: str = "Description for the first column.",
    col2_title: str = "Column 2",
    col2_desc: str = "Description for the second column.",
) -> str:
    """
    Generate a 2-column science/biology style slide with pale green background, hexagon patterns, and a molecule graphic. Good for comparisons or side-by-side content.
    """
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    import sys

    # Font handling
    if sys.platform == "win32":
        font_path = "C:/Windows/Fonts/arial.ttf"
        font_path_bold = "C:/Windows/Fonts/arialbd.ttf"
    else:
        font_path = "/Library/Fonts/Arial.ttf"
        font_path_bold = "/Library/Fonts/Arial Bold.ttf"

    root = ET.Element("presentation")
    slide = ET.SubElement(root, "slide")
    
    # 1. Background
    bg_color = "#DCE6D3"
    ET.SubElement(slide, "polygon", points="0,0 1600,0 1600,900 0,900", fill=bg_color, line_color="none")
    
    # 2. Hexagon Patterns (Clipped to slide bounds using polygon)
    # Top-Left Hexagon
    ET.SubElement(slide, "polygon", points="25.0,130.0 115.0,85.0 115.0,0.0 0.0,0.0 0.0,117.5", fill="#4A775C", line_color="none")
    
    # Top-Right Hexagon
    ET.SubElement(slide, "polygon", points="1485.0,75.0 1575.0,120.0 1600.0,107.5 1600.0,0.0 1485.0,0.0", fill="#9EB1A8", line_color="none")
    
    # Bottom-Right Cluster (3 hexagons)
    ET.SubElement(slide, "polygon", points="1525.0,715.0 1450.0,752.5 1450.0,827.5 1525.0,865.0 1600.0,827.5 1600.0,752.5", fill="#A1C2B0", line_color="none")
    ET.SubElement(slide, "polygon", points="1540.0,852.5 1540.0,900.0 1600.0,900.0 1600.0,822.5", fill="#C48E59", line_color="none")
    ET.SubElement(slide, "polygon", points="1540.0,672.5 1540.0,747.5 1600.0,777.5 1600.0,642.5", fill="#888172", line_color="none")

    # Bottom-Left Borders (Hexagons cut off)
    ET.SubElement(slide, "polygon", points="10.0,830.0 80.0,795.0 80.0,725.0 10.0,690.0 0.0,695.0 0.0,825.0", fill="#C48E59", line_color="none")
    ET.SubElement(slide, "polygon", points="80.0,845.0 10.0,810.0 0.0,815.0 0.0,900.0 80.0,900.0", fill="#A1C2B0", line_color="none")

    # 3. Molecule Graphic
    # Center atom
    mx, my = 220, 750
    # Connecting Lines (White)
    ET.SubElement(slide, "line", x1=str(mx), y1=str(my), x2=str(mx-80), y2=str(my+70), color="#FFFFFF", width="4")
    ET.SubElement(slide, "line", x1=str(mx), y1=str(my), x2=str(mx-60), y2=str(my-50), color="#FFFFFF", width="4")
    ET.SubElement(slide, "line", x1=str(mx-80), y1=str(my+70), x2=str(mx-100), y2=str(my-20), color="#FFFFFF", width="4")
    ET.SubElement(slide, "line", x1=str(mx-80), y1=str(my+70), x2=str(mx-20), y2=str(my+120), color="#FFFFFF", width="4")

    # Atoms (Circles)
    def draw_atom(cx, cy, r, color):
        ET.SubElement(slide, "shape", type="circle", x=str(cx-r), y=str(cy-r), width=str(r*2), height=str(r*2), fill=color, line_color="none")

    draw_atom(mx, my, 45, "#785B3C") # Center big brown
    draw_atom(mx-80, my+70, 35, "#785B3C") # Bottom left brown
    draw_atom(mx-60, my-50, 25, "#4A775C") # Top green
    draw_atom(mx-100, my-20, 20, "#4A775C") # Far left green
    draw_atom(mx-20, my+120, 25, "#4A775C") # Bottom green

    # 4. Text Boxes
    text_color = "#312C28"

    # Main Title
    title_tb = ET.SubElement(
        slide, "textbox",
        x="300", y="100",
        width="1000", height="100",
        font="Georgia", font_path="",
        size="60", min_font_size="40",
        color=text_color, align="center", vertical_align="middle",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="true"
    )
    title_tb.text = main_title

    # --- COLUMN 1 (Left) ---
    col1_x = 200
    col_width = 550
    col_title_y = 280
    col_title_h = 50
    col_content_y = 350
    col_content_h = 300
    
    c1_title_tb = ET.SubElement(
        slide, "textbox",
        x=str(col1_x), y=str(col_title_y),
        width=str(col_width), height=str(col_title_h),
        font="Georgia", font_path="",
        size="32", min_font_size="24",
        color=text_color, align="left", vertical_align="bottom",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="true"
    )
    c1_title_tb.text = col1_title

    c1_desc_tb = ET.SubElement(
        slide, "textbox",
        x=str(col1_x), y=str(col_content_y),
        width=str(col_width), height=str(col_content_h),
        font="Segoe UI", font_path="",
        size="18", min_font_size="14",
        color=text_color, align="left", vertical_align="top",
        single_line="false", max_lines="12", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.2", bold="false"
    )
    c1_desc_tb.text = col1_desc

    # --- COLUMN 2 (Right) ---
    col2_x = 850
    
    c2_title_tb = ET.SubElement(
        slide, "textbox",
        x=str(col2_x), y=str(col_title_y),
        width=str(col_width), height=str(col_title_h),
        font="Georgia", font_path="",
        size="32", min_font_size="24",
        color=text_color, align="left", vertical_align="bottom",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="true"
    )
    c2_title_tb.text = col2_title

    c2_desc_tb = ET.SubElement(
        slide, "textbox",
        x=str(col2_x), y=str(col_content_y),
        width=str(col_width), height=str(col_content_h),
        font="Segoe UI", font_path="",
        size="18", min_font_size="14",
        color=text_color, align="left", vertical_align="top",
        single_line="false", max_lines="12", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.2", bold="false"
    )
    c2_desc_tb.text = col2_desc

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    return xml_str
def generate_thank_you_slide_xml(
    title: str = "Thank You",
    message: str = "We appreciate your trust and confidence in us. Your support is invaluable, and we look forward to serving you again.",
) -> str:
    """
    Generate a handwritten watercolor style 'Thank You' slide with a large cursive title, floating hearts, and a bouquet of daisies.
    """
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    import math

    root = ET.Element("presentation")
    slide = ET.SubElement(root, "slide")
    
    # 1. Background
    bg_color = "#FFFFFF"
    ET.SubElement(slide, "polygon", points="0,0 1600,0 1600,900 0,900", fill=bg_color, line_color="none")

    # Colors
    yellow_dark = "#F5B041"
    yellow_light = "#FAD7A1"
    green_stem = "#7CB342"
    text_dark = "#55534F"
    text_light = "#A3A09A"

    # 2. Splatters (Top Left and Bottom Right)
    import random
    random.seed(42) # For reproducible layout

    def draw_splatters(origin_x, origin_y, dir_x, dir_y, count, spread, max_r, min_r):
        for _ in range(count):
            dx = random.uniform(-spread*0.2, spread) * dir_x
            dy = random.uniform(-spread*0.2, spread) * dir_y
            rx = origin_x + dx
            ry = origin_y + dy
            
            d = math.hypot(dx, dy)
            
            # Larger dots closer to origin, smaller further away
            ratio = max(0, 1 - (d / spread))
            base_r = min_r + (max_r - min_r) * (ratio ** 1.5)
            
            # Add random variation
            r = base_r * random.uniform(0.5, 1.5)
            r = max(min_r, min(max_r, r))
            
            # Prevent overflowing slide bounds
            rx = max(r + 2, min(1600 - r - 2, rx))
            ry = max(r + 2, min(900 - r - 2, ry))
            
            color = random.choice([yellow_dark, yellow_light, "#FDEBD0"])
            ET.SubElement(slide, "shape", type="circle", x=str(rx-r), y=str(ry-r), width=str(r*2), height=str(r*2), fill=color, line_color="none")

    draw_splatters(100, 50, 1, 1, 80, 500, 16, 1.5)
    draw_splatters(1500, 850, -1, -1, 50, 350, 12, 1.5)

    # 3. Daisies (Bouquet)
    def draw_daisy(cx, cy, scale, angle_offset, draw_stem_to_x):
        # Stem
        ET.SubElement(slide, "line", x1=str(cx), y1=str(cy), x2=str(draw_stem_to_x), y2="900", color=green_stem, width="5")
        
        # Leaves on stem
        leaf_y = cy + (900 - cy) * 0.5
        leaf_x = cx + (draw_stem_to_x - cx) * 0.5
        ET.SubElement(slide, "shape", type="ellipse", x=str(leaf_x - 10*scale), y=str(leaf_y), width=str(20*scale), height=str(40*scale), fill=green_stem, line_color="none", rotation="45")
        ET.SubElement(slide, "shape", type="ellipse", x=str(leaf_x + 10*scale), y=str(leaf_y + 20), width=str(20*scale), height=str(40*scale), fill=green_stem, line_color="none", rotation="-45")

        # Petals
        num_petals = 12
        petal_w = 20 * scale
        petal_h = 60 * scale
        for i in range(num_petals):
            angle = i * (360 / num_petals) + angle_offset
            rad = math.radians(angle)
            # Offset the petal slightly from the center
            dist = 15 * scale
            px = cx + math.sin(rad) * dist - petal_w / 2
            py = cy - math.cos(rad) * dist - petal_h / 2
            
            ET.SubElement(
                slide, "shape", type="ellipse", 
                x=str(px), y=str(py), width=str(petal_w), height=str(petal_h), 
                fill="#FFFFFF", line_color=yellow_light, rotation=str(angle)
            )
        
        # Center
        center_r = 18 * scale
        ET.SubElement(slide, "shape", type="circle", x=str(cx - center_r), y=str(cy - center_r), width=str(center_r*2), height=str(center_r*2), fill=yellow_dark, line_color="none")

    daisies = [
        (1000, 450, 1.2, 0, 1150),
        (1150, 350, 1.0, 10, 1200),
        (1300, 330, 1.3, 5, 1250),
        (1400, 480, 1.0, 15, 1300),
        (1100, 580, 0.9, 20, 1180),
        (1250, 520, 1.1, -10, 1230),
        (950, 620, 0.8, -5, 1120),
        (1380, 650, 0.8, 12, 1280),
    ]

    for dx, dy, dscale, dang, dstx in daisies:
        draw_daisy(dx, dy, dscale, dang, dstx)

    # 4. Hearts
    def draw_heart(cx, cy, size, rotation):
        ET.SubElement(slide, "shape", type="heart", x=str(cx - size/2), y=str(cy - size/2), width=str(size), height=str(size), fill=yellow_dark, line_color="none", rotation=str(rotation))

    draw_heart(750, 200, 80, -20)
    draw_heart(850, 280, 70, 15)
    draw_heart(780, 380, 60, -10)

    # 5. Text Boxes
    # Main Title (Handwritten style)
    title_tb = ET.SubElement(
        slide, "textbox",
        x="100", y="250",
        width="800", height="300",
        font="Segoe Print", font_path="C:/Windows/Fonts/segoepr.ttf",
        size="140", min_font_size="60",
        color=text_dark, align="left", vertical_align="middle",
        single_line="true", max_lines="2", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="true"
    )
    title_tb.text = title

    # Message
    msg_tb = ET.SubElement(
        slide, "textbox",
        x="120", y="620",
        width="800", height="200",
        font="Georgia", font_path="",
        size="14", min_font_size="10",
        color=text_light, align="left", vertical_align="top",
        single_line="false", max_lines="4", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.3", bold="false"
    )
    msg_tb.text = message

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    return xml_str
def generate_thank_you_watching_slide_xml(
    title: str = "THANK YOU",
    message: str = "for watching",
) -> str:
    """
    Generate a boho/abstract 'Thank You for watching' slide with torn paper shapes, line-art branches, and 3D bold marker text.
    """
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    import math

    root = ET.Element("presentation")
    slide = ET.SubElement(root, "slide")
    
    # 1. Background
    bg_color = "#F9F6F0"
    ET.SubElement(slide, "polygon", points="0,0 1600,0 1600,900 0,900", fill=bg_color, line_color="none")

    # Colors
    peach = "#F5D0B5"
    dark_grey = "#4A4A4A"
    brown = "#733F2E"
    orange = "#B85C38"

    # 2. Torn Paper Polygons
    # Top Right
    tr_points = "800.0,0.0 950.0,50.0 1050.0,20.0 1250.0,80.0 1350.0,50.0 1550.0,300.0 1600.0,350.0 1600.0,0.0"
    ET.SubElement(slide, "polygon", points=tr_points, fill=peach, line_color="none")
    
    # Bottom Left
    bl_points = "0.0,550.0 150.0,600.0 200.0,570.0 450.0,720.0 500.0,680.0 750.0,900.0 0.0,900.0"
    ET.SubElement(slide, "polygon", points=bl_points, fill=peach, line_color="none")

    # 3. Line-art Branches
    def draw_branch(sx, sy, ex, ey, leaf_len=80, leaf_w=25, num_pairs=3):
        ET.SubElement(slide, "line", x1=str(sx), y1=str(sy), x2=str(ex), y2=str(ey), color=brown, width="4")
        dx = ex - sx
        dy = ey - sy
        angle = math.atan2(dy, dx)
        
        def add_leaf(cx, cy, leaf_angle_offset):
            l_ang = angle + math.radians(leaf_angle_offset)
            
            # center of leaf
            lx = cx + math.cos(l_ang) * (leaf_len / 2)
            ly = cy + math.sin(l_ang) * (leaf_len / 2)
            
            # Clamp center so leaf stays inside
            clx = max(leaf_len/2, min(1600 - leaf_len/2, lx))
            cly = max(leaf_len/2, min(900 - leaf_len/2, ly))
            
            ET.SubElement(slide, "shape", type="ellipse", 
                          x=str(clx - leaf_w/2), y=str(cly - leaf_len/2), 
                          width=str(leaf_w), height=str(leaf_len), 
                          fill="none", line_color=brown, 
                          rotation=str(math.degrees(l_ang) + 90))
            
            # Vein goes from stem (cx, cy) to the tip of the leaf
            tip_x = cx + math.cos(l_ang) * (leaf_len * 0.85)
            tip_y = cy + math.sin(l_ang) * (leaf_len * 0.85)
            
            tip_x = max(5, min(1595, tip_x))
            tip_y = max(5, min(895, tip_y))
            
            ET.SubElement(slide, "line", 
                          x1=str(cx), y1=str(cy), 
                          x2=str(tip_x), y2=str(tip_y), 
                          color=brown, width="2")

        # Tip leaf points exactly along the stem
        add_leaf(ex, ey, 0)
        
        # Side leaves spread beautifully along the stem
        for i in range(num_pairs):
            # t goes from 0.2 to 0.8
            t_val = 0.2 + 0.6 * (i / max(1, num_pairs - 1))
            cx = sx + dx * t_val
            cy = sy + dy * t_val
            add_leaf(cx, cy, 35)
            add_leaf(cx, cy, -35)

    # Top-left branches (parallel to avoid overlap)
    draw_branch(80, 0, 330, 250, leaf_len=80, leaf_w=25, num_pairs=3)
    draw_branch(0, 150, 150, 300, leaf_len=60, leaf_w=20, num_pairs=2)
    
    # Bottom-right branches (parallel to avoid overlap)
    draw_branch(1520, 900, 1270, 650, leaf_len=80, leaf_w=25, num_pairs=3)
    draw_branch(1600, 750, 1450, 600, leaf_len=60, leaf_w=20, num_pairs=2)

    # 4. Springs / Swirls
    def draw_spring(cx, cy, r, loops, pitch, rotation_deg, color):
        segments = int(30 * loops)
        points = []
        rad_rot = math.radians(rotation_deg)
        for i in range(segments + 1):
            t = i / 30 * math.pi * 2
            px = r * math.cos(t)
            py = r * math.sin(t) + (t / (2*math.pi)) * pitch
            
            # Rotate
            rx = px * math.cos(rad_rot) - py * math.sin(rad_rot)
            ry = px * math.sin(rad_rot) + py * math.cos(rad_rot)
            
            # Clamp to prevent overflow
            px_clamped = max(5, min(1595, cx + rx))
            py_clamped = max(5, min(895, cy + ry))
            points.append((px_clamped, py_clamped))
            
        for i in range(len(points) - 1):
            ET.SubElement(slide, "line", x1=str(points[i][0]), y1=str(points[i][1]), x2=str(points[i+1][0]), y2=str(points[i+1][1]), color=color, width="4")

    draw_spring(180, 520, 25, 2.5, 40, -45, orange)
    draw_spring(1400, 380, 25, 2.5, 50, 60, orange)
    draw_spring(650, 750, 20, 2.0, 30, 15, orange)
    draw_spring(400, 180, 18, 1.5, 25, 30, orange)
    draw_spring(1200, 220, 20, 2.0, 35, -30, orange)
    
    # White swirls over abstract background
    draw_spring(300, 850, 30, 2.5, 40, -10, "#FFFFFF")
    draw_spring(1450, 100, 40, 2.5, 50, 45, "#FFFFFF")

    # 5. Stars
    def draw_star(cx, cy, size, color):
        pts = []
        for i in range(8):
            angle = i * math.pi / 4
            r = size if i % 2 == 0 else size * 0.3
            pts.append(f"{cx + r * math.cos(angle):.1f},{cy + r * math.sin(angle):.1f}")
        ET.SubElement(slide, "polygon", points=" ".join(pts), fill=color, line_color="none")

    draw_star(350, 750, 60, "#FFFFFF")
    draw_star(300, 180, 50, "#FFFFFF")

    # 6. Typography (Title and Message)
    title_w = 1200
    title_h = 250
    title_x = 200
    title_y = 350
    
    # Shadow text (offset by +8px)
    title_shadow = ET.SubElement(
        slide, "textbox",
        x=str(title_x + 8), y=str(title_y + 8),
        width=str(title_w), height=str(title_h),
        font="Comic Sans MS", font_path="C:/Windows/Fonts/comic.ttf",
        size="180", min_font_size="80",
        color=brown, align="center", vertical_align="middle",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="true"
    )
    title_shadow.text = title.upper()

    # Main text
    title_main = ET.SubElement(
        slide, "textbox",
        x=str(title_x), y=str(title_y),
        width=str(title_w), height=str(title_h),
        font="Comic Sans MS", font_path="C:/Windows/Fonts/comic.ttf",
        size="180", min_font_size="80",
        color=dark_grey, align="center", vertical_align="middle",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="true"
    )
    title_main.text = title.upper()

    # Message text (cursive)
    msg_tb = ET.SubElement(
        slide, "textbox",
        x="800", y="580",
        width="400", height="100",
        font="Segoe Print", font_path="C:/Windows/Fonts/segoepr.ttf",
        size="48", min_font_size="24",
        color=brown, align="center", vertical_align="top",
        single_line="true", max_lines="1", overflow="shrink", reflow_on_resize="true",
        line_spacing="1.0", bold="false"
    )
    msg_tb.text = message

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    return xml_str


def generate_about_me_slide_xml(
    title: str = "About Me",
    paragraph: str = "Lorem ipsum dolor amet, consectetur adipiscing elit, sed eiusmod tempor incididunt ut labore dolore magna aliqua. Lorem ipsum dolor amet, consectetur adipiscing elit, sed eiusmod tempor incididunt ut labore dolore magna aliqua.",
    image_url: str = "https://picsum.photos/seed/portrait/600/800"
) -> str:
    """
    Generate a minimalist elegant 'About Me' slide with a left text area, organic wavy corner blobs, and an oval portrait frame.
    """
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    root = ET.Element("presentation")
    slide = ET.SubElement(root, "slide")
    
    # Helpers for organic shapes
    def evaluate_bezier(p0, p1, p2, p3, steps=20):
        pts = []
        for i in range(steps):
            t = i / steps
            x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
            y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
            pts.append((x, y))
        return pts

    def generate_wavy_curve(points, steps=15):
        res = []
        n = len(points)
        for i in range(n - 1):
            p0 = points[max(0, i - 1)]
            p1 = points[i]
            p2 = points[i + 1]
            p3 = points[min(n - 1, i + 2)]
            cp1 = (p1[0] + (p2[0] - p0[0])/6, p1[1] + (p2[1] - p0[1])/6)
            cp2 = (p2[0] - (p3[0] - p1[0])/6, p2[1] - (p3[1] - p1[1])/6)
            res.extend(evaluate_bezier(p1, cp1, cp2, p2, steps))
        res.append(points[-1])
        return res

    def clamp(val, min_val, max_val):
        return max(min_val, min(max_val, val))

    def draw_organic_blob(polygon_pts, fill_color):
        clamped_pts = [(clamp(p[0], 0, 1600), clamp(p[1], 0, 900)) for p in polygon_pts]
        pts_str = " ".join([f"{p[0]},{p[1]}" for p in clamped_pts])
        ET.SubElement(slide, "polygon", points=pts_str, fill=fill_color, line_color="none")

    def draw_wavy_line(line_pts, color, width="2"):
        clamped_pts = [(clamp(p[0], 0, 1600), clamp(p[1], 0, 900)) for p in line_pts]
        pts_str = " ".join([f"{p[0]},{p[1]}" for p in clamped_pts])
        # Use polyline so the line is continuous and smoothly jointed
        ET.SubElement(slide, "polyline", points=pts_str, line_color=color, line_width=width, fill="none")

    # 1. Background (Beige)
    bg_color = "#F7F2EB"
    ET.SubElement(slide, "polygon", points="0,0 1600,0 1600,900 0,900", fill=bg_color, line_color="none")

    # 2. Organic Corner Blobs (Decorations)
    blob_color = "#EADBCD"
    line_color = "#997458"
    
    # Top Right Blob
    tr_curve = generate_wavy_curve([(1150, 0), (1250, 150), (1450, 200), (1600, 100)])
    tr_poly = tr_curve + [(1600, 0), (1150, 0)]
    draw_organic_blob(tr_poly, blob_color)
    
    # Top Right Wavy Line
    tr_line_curve = generate_wavy_curve([(1450, 0), (1350, 100), (1500, 250), (1600, 250)])
    draw_wavy_line(tr_line_curve, line_color, "4")

    # Bottom Left Blob
    bl_curve = generate_wavy_curve([(0, 650), (100, 700), (250, 800), (200, 900)])
    bl_poly = bl_curve + [(0, 900), (0, 650)]
    draw_organic_blob(bl_poly, blob_color)
    
    # Bottom Left Wavy Line
    bl_line_curve = generate_wavy_curve([(0, 780), (150, 800), (250, 850), (250, 900)])
    draw_wavy_line(bl_line_curve, line_color, "4")

    # 3. Left Text Content
    ET.SubElement(slide, "textbox", x="130", y="260", width="600", height="120", font="Segoe UI Light", size="80", color="#3E281C", align="left", vertical_align="middle", single_line="true", max_lines="1", reflow_on_resize="true", line_spacing="1.0", bold="false").text = title

    ET.SubElement(slide, "textbox", x="130", y="400", width="700", height="400", font="Segoe UI", size="26", color="#665246", align="left", vertical_align="top", single_line="false", max_lines="7", overflow="shrink", reflow_on_resize="true", line_spacing="1.3", bold="false").text = paragraph

    # 4. Oval Portrait Frame (Right side)
    # Reduced image frame size from 600x700 to 500x600, and moved slightly right.
    ix, iy, iw, ih = 950, 150, 500, 600
    
    border_w = 6
    ET.SubElement(slide, "shape", type="ellipse", x=str(ix - border_w), y=str(iy - border_w), width=str(iw + border_w * 2), height=str(ih + border_w * 2), fill=line_color, line_color="none")

    # Image
    ET.SubElement(slide, "image", src=image_url, x=str(ix), y=str(iy), width=str(iw), height=str(ih), shape="ellipse")

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    return xml_str


def generate_content_2col_slide_xml(
    title: str = "CONTENT",
    subtitle_1: str = "PRIMARY REFERENCE TITLE",
    paragraph_1: str = "Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. They serve various purposes and are effective tools.",
    subtitle_2: str = "SECONDARY REFERENCE TITLE",
    paragraph_2: str = "Presentations are communication tools that can be used as demonstrations, lectures, speeches, reports, and more. They serve various purposes and are effective tools.",
    image_url: str = "https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=800&auto=format&fit=crop"
) -> str:
    """
    Generate a clean 2-column content slide with a large title, accent line, two text sections on the left, and a full-height image on the right.
    """
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    root = ET.Element("presentation")
    slide = ET.SubElement(root, "slide")
    
    # 1. Background (White)
    bg_color = "#FFFFFF"
    ET.SubElement(slide, "polygon", points="0,0 1600,0 1600,900 0,900", fill=bg_color, line_color="none")

    # 2. Left Column Content
    text_color_dark = "#162235"
    text_color_light = "#575F6A"
    accent_color = "#4285F4"
    left_x = "100"
    content_width = "620"
    
    # Main Title
    ET.SubElement(slide, "textbox", x=left_x, y="150", width="600", height="100", font="Segoe UI", size="60", color=text_color_dark, align="left", vertical_align="middle", single_line="true", max_lines="1", reflow_on_resize="true", line_spacing="1.0", bold="true").text = title

    # Accent Line
    # A short thick blue line under the title
    ET.SubElement(slide, "line", x1=left_x, y1="260", x2="250", y2="260", color=accent_color, width="6")

    # Section 1
    ET.SubElement(slide, "textbox", x=left_x, y="340", width=content_width, height="50", font="Segoe UI", size="24", color=text_color_dark, align="left", vertical_align="middle", single_line="true", max_lines="1", reflow_on_resize="true", line_spacing="1.0", bold="true").text = subtitle_1

    ET.SubElement(slide, "textbox", x=left_x, y="400", width=content_width, height="120", font="Segoe UI", size="18", color=text_color_light, align="left", vertical_align="top", single_line="false", max_lines="4", overflow="shrink", reflow_on_resize="true", line_spacing="1.5", bold="false").text = paragraph_1

    # Section 2
    ET.SubElement(slide, "textbox", x=left_x, y="580", width=content_width, height="50", font="Segoe UI", size="24", color=text_color_dark, align="left", vertical_align="middle", single_line="true", max_lines="1", reflow_on_resize="true", line_spacing="1.0", bold="true").text = subtitle_2

    ET.SubElement(slide, "textbox", x=left_x, y="640", width=content_width, height="120", font="Segoe UI", size="18", color=text_color_light, align="left", vertical_align="top", single_line="false", max_lines="4", overflow="shrink", reflow_on_resize="true", line_spacing="1.5", bold="false").text = paragraph_2

    # 3. Right Column Image (Full height)
    # 1600x900 slide, left half is 800, right half is 800
    # crop="true" ensures the image is scaled and center-cropped to fill 800x900 without distortion
    ET.SubElement(slide, "image", src=image_url, x="800", y="0", width="800", height="900", crop="true")

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    return xml_str



def generate_pie_chart_slide_xml(title: str, subtitle: str, items: list) -> str:
    """
    Generate an XML slide with a pie chart.
    `items` is a list of dicts: [{"label": "Savings", "value": 24.8, "description": "Details..."}, ...]
    """
    import math
    
    # Base layout
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FAF7F0">
    <polygon points="50,50 1550,50 1550,250 50,250" fill="#354F42"/>
    <textbox x="50" y="80" width="1500" height="80" font="Segoe UI" size="70" color="#FFFFFF" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="50" y="170" width="1500" height="50" font="Segoe UI" size="36" color="#B6AE97" italic="true" align="center" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <polygon points="50,300 700,300 700,850 50,850" fill="#2F2E2C"/>
'''
    colors = ["#354F42", "#556B55", "#89947A", "#B6AE97", "#EBE2D0", "#D9C8A9", "#A49987"]
    
    # Render legend
    y_start = 320
    for i, item in enumerate(items[:6]):
        color = colors[i % len(colors)]
        label = item.get('label', '')
        desc = item.get('description', '')
        
        xml += f'''
    <polygon points="80,{y_start+10} 100,{y_start+10} 100,{y_start+70} 80,{y_start+70}" fill="{color}"/>
    <textbox x="130" y="{y_start}" width="530" height="40" font="Segoe UI" size="26" color="#FFFFFF" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{label}</textbox>
    <textbox x="130" y="{y_start+45}" width="530" height="60" font="Segoe UI" size="16" color="#D0D0D0" align="left" vertical_align="top" single_line="false" max_lines="2" reflow_on_resize="true" line_spacing="1.2">{desc}</textbox>
'''
        y_start += 105

    # Render pie chart SVG
    total_val = sum([item.get('value', 0) for item in items])
    if total_val == 0: total_val = 1
    
    cx, cy, r = 400, 275, 100
    stroke_width = 200
    circumference = 2 * math.pi * r
    label_r = r + stroke_width / 2 + 40
    
    svg_elements = []
    current_angle_deg = -90
    
    for i, item in enumerate(items):
        color = colors[i % len(colors)]
        val = item.get('value', 0)
        percentage = (val / total_val) * 100
        dash = (percentage / 100) * circumference
        
        # Circle slice
        circle_svg = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="{dash} {circumference}" transform="rotate({current_angle_deg} {cx} {cy})" />'
        svg_elements.append(circle_svg)
        
        # Label position
        slice_angle = (percentage / 100) * 360
        mid_angle_deg = current_angle_deg + slice_angle / 2
        mid_angle_rad = math.radians(mid_angle_deg)
        
        lx = cx + label_r * math.cos(mid_angle_rad)
        ly = cy + label_r * math.sin(mid_angle_rad)
        
        text_anchor = "start" if math.cos(mid_angle_rad) >= 0 else "end"
        text_svg = f'<text x="{lx}" y="{ly}" font-family="Segoe UI" font-size="22" font-weight="bold" fill="#2F2E2C" text-anchor="{text_anchor}" dominant-baseline="middle">{percentage:.1f}%</text>'
        svg_elements.append(text_svg)
        
        current_angle_deg += slice_angle

    svg_content = "".join(svg_elements)
    
    # Properly escape XML for the inner SVG payload
    import html
    escaped_svg = html.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="550" viewBox="0 0 800 550">{svg_content}</svg>')
    
    xml += f'''
    <svg x="750" y="300" width="800" height="550" pixel_width="800" pixel_height="550">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_donut_chart_slide_xml(title: str, subtitle: str, items: list) -> str:
    """
    Generate an XML slide with a donut chart (3 distinct donuts horizontally).
    `items` is a list of exactly 3 dicts: [{"label": "JUPITER", "description": "...", "value": 75}, ...]
    """
    import math
    import html
    
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FCFBF9">
    <polygon points="0,0 45,0 45,900 0,900" fill="#9E8470" line_color="none"/>
    <polygon points="1400,20 1600,20 1600,80 1400,80" fill="#B3B9AE" line_color="none"/>
    <polygon points="1230,840 1600,840 1600,900 1230,900" fill="#7A7E74" line_color="none"/>
    <textbox x="120" y="110" width="1200" height="100" font="Segoe UI" size="76" color="#333230" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true" line_spacing="1.0">{title}</textbox>
    <textbox x="120" y="210" width="1200" height="50" font="Segoe UI" size="30" color="#8C8984" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true" line_spacing="1.0">{subtitle}</textbox>
'''
    
    cx_list = [350, 800, 1250]
    r = 90
    stroke_width = 60
    circumference = 2 * math.pi * r
    
    svg_elements = []
    
    # 3 donut charts
    for i, item in enumerate(items[:3]):
        cx = cx_list[i]
        cy = 150
        val = item.get('value', 0)
        percentage = min(max(val, 0), 100)
        dash = (percentage / 100) * circumference
        
        # Background circle
        bg_circle = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#6E7266" stroke-width="{stroke_width}" />'
        
        # Foreground circle
        fg_circle = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#CDAE9B" stroke-width="{stroke_width}" stroke-dasharray="{dash} {circumference}" />'
        
        group = f'<g transform="rotate(180 {cx} {cy})">{bg_circle}{fg_circle}</g>'
        svg_elements.append(group)
        
        # Text in center
        text = f'<text x="{cx}" y="{cy+15}" font-family="Arial" font-size="42" font-weight="bold" fill="#333230" text-anchor="middle">{int(percentage)}%</text>'
        svg_elements.append(text)

        # Legend text outside SVG
        label = item.get('label', '')
        desc = item.get('description', '')
        tx = cx - 200
        xml += f'''
    <textbox x="{tx}" y="640" width="400" height="40" font="Segoe UI" size="24" color="#333230" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{label}</textbox>
    <textbox x="{tx}" y="690" width="400" height="80" font="Segoe UI" size="18" color="#8C8984" align="center" vertical_align="top" single_line="false" max_lines="3" reflow_on_resize="true" line_spacing="1.4">{desc}</textbox>
'''

    svg_content = "".join(svg_elements)
    escaped_svg = html.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="300" viewBox="0 0 1600 300">{svg_content}</svg>')
    
    xml += f'''
    <svg x="0" y="320" width="1600" height="300" pixel_width="1600" pixel_height="300">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_area_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for area.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <polygon points="50,40 70,40 70,55 50,55" fill="#3A5EC5"/>
    <polygon points="75,40 95,40 95,55 75,55" fill="#4A9EBD"/>
    <polygon points="50,60 70,60 70,75 50,75" fill="#4A9EBD"/>
    <polygon points="75,60 95,60 95,75 75,75" fill="#3A5EC5"/>
    <textbox x="110" y="40" width="300" height="40" font="Segoe UI" size="20" color="#111111" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1">{title}</textbox>
    <textbox x="950" y="40" width="100" height="40" font="Segoe UI" size="18" color="#555555" align="center" vertical_align="middle" single_line="true">{subtitle}</textbox>
    <textbox x="1060" y="40" width="100" height="40" font="Segoe UI" size="18" color="#555555" align="center" vertical_align="middle" single_line="true">Service</textbox>
    <textbox x="1170" y="40" width="100" height="40" font="Segoe UI" size="18" color="#555555" align="center" vertical_align="middle" single_line="true">About Us</textbox>
    <textbox x="1280" y="40" width="100" height="40" font="Segoe UI" size="18" color="#555555" align="center" vertical_align="middle" single_line="true">Contact</textbox>
    <polygon points="1450,45 1485,45 1485,48 1450,48" fill="#3A5EC5"/>
    <polygon points="1450,55 1485,55 1485,58 1450,58" fill="#3A5EC5"/>
    <textbox x="150" y="200" width="350" height="150" font="Segoe UI" size="55" color="#111111" bold="true" align="left" vertical_align="top" single_line="false" max_lines="2" reflow_on_resize="true">Marketing
Data</textbox>
    <textbox x="150" y="400" width="350" height="40" font="Segoe UI" size="24" color="#3A5EC5" bold="true" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">About Data</textbox>
    <textbox x="150" y="450" width="350" height="200" font="Segoe UI" size="16" color="#666666" align="left" vertical_align="top" single_line="false" max_lines="8" reflow_on_resize="true" line_spacing="1.2">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</textbox>
    <svg x="150" y="660" width="200" height="60" pixel_width="200" pixel_height="60">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;200&quot; height=&quot;60&quot;&gt;&lt;rect x=&quot;0&quot; y=&quot;0&quot; width=&quot;180&quot; height=&quot;55&quot; rx=&quot;27.5&quot; fill=&quot;#3A5EC5&quot;/&gt;&lt;/svg&gt;</svg>
    <textbox x="150" y="660" width="180" height="55" font="Segoe UI" size="14" color="#FFFFFF" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1">Learn More</textbox>
    <svg x="550" y="180" width="950" height="550" pixel_width="950" pixel_height="550">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;950&quot; height=&quot;550&quot; viewBox=&quot;0 0 950 550&quot;&gt;&lt;rect x=&quot;0&quot; y=&quot;0&quot; width=&quot;900&quot; height=&quot;520&quot; rx=&quot;30&quot; fill=&quot;#F8F9FA&quot;/&gt;&lt;line x1=&quot;100&quot; y1=&quot;430.0&quot; x2=&quot;800&quot; y2=&quot;430.0&quot; stroke=&quot;#E5E5E5&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;80&quot; y=&quot;435.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;0&lt;/text&gt;&lt;line x1=&quot;100&quot; y1=&quot;377.14285714285717&quot; x2=&quot;800&quot; y2=&quot;377.14285714285717&quot; stroke=&quot;#E5E5E5&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;80&quot; y=&quot;382.14285714285717&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;20&lt;/text&gt;&lt;line x1=&quot;100&quot; y1=&quot;324.2857142857143&quot; x2=&quot;800&quot; y2=&quot;324.2857142857143&quot; stroke=&quot;#E5E5E5&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;80&quot; y=&quot;329.2857142857143&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;40&lt;/text&gt;&lt;line x1=&quot;100&quot; y1=&quot;271.42857142857144&quot; x2=&quot;800&quot; y2=&quot;271.42857142857144&quot; stroke=&quot;#E5E5E5&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;80&quot; y=&quot;276.42857142857144&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;60&lt;/text&gt;&lt;line x1=&quot;100&quot; y1=&quot;218.57142857142858&quot; x2=&quot;800&quot; y2=&quot;218.57142857142858&quot; stroke=&quot;#E5E5E5&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;80&quot; y=&quot;223.57142857142858&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;80&lt;/text&gt;&lt;line x1=&quot;100&quot; y1=&quot;165.71428571428572&quot; x2=&quot;800&quot; y2=&quot;165.71428571428572&quot; stroke=&quot;#E5E5E5&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;80&quot; y=&quot;170.71428571428572&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;100&lt;/text&gt;&lt;line x1=&quot;100&quot; y1=&quot;112.85714285714289&quot; x2=&quot;800&quot; y2=&quot;112.85714285714289&quot; stroke=&quot;#E5E5E5&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;80&quot; y=&quot;117.85714285714289&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;120&lt;/text&gt;&lt;line x1=&quot;100&quot; y1=&quot;60.0&quot; x2=&quot;800&quot; y2=&quot;60.0&quot; stroke=&quot;#E5E5E5&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;80&quot; y=&quot;65.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;140&lt;/text&gt;&lt;text x=&quot;100.0&quot; y=&quot;455&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#111111&quot; text-anchor=&quot;middle&quot;&gt;Data 1&lt;/text&gt;&lt;text x=&quot;240.0&quot; y=&quot;455&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#111111&quot; text-anchor=&quot;middle&quot;&gt;Data 2&lt;/text&gt;&lt;text x=&quot;380.0&quot; y=&quot;455&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#111111&quot; text-anchor=&quot;middle&quot;&gt;Data 3&lt;/text&gt;&lt;text x=&quot;520.0&quot; y=&quot;455&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#111111&quot; text-anchor=&quot;middle&quot;&gt;Data 4&lt;/text&gt;&lt;text x=&quot;660.0&quot; y=&quot;455&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#111111&quot; text-anchor=&quot;middle&quot;&gt;Data 5&lt;/text&gt;&lt;text x=&quot;800.0&quot; y=&quot;455&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#111111&quot; text-anchor=&quot;middle&quot;&gt;Data 6&lt;/text&gt;&lt;path d=&quot;M100.0,430 L100.0,350.7142857142857 L240.0,311.07142857142856 L380.0,213.28571428571428 L520.0,205.35714285714286 L660.0,102.28571428571428 L800.0,126.07142857142856 L800.0,430 Z&quot; fill=&quot;#4A9EBD&quot; opacity=&quot;0.75&quot;/&gt;&lt;path d=&quot;M100.0,350.7142857142857 L240.0,311.07142857142856 L380.0,213.28571428571428 L520.0,205.35714285714286 L660.0,102.28571428571428 L800.0,126.07142857142856&quot; fill=&quot;none&quot; stroke=&quot;#4A9EBD&quot; stroke-width=&quot;2&quot;/&gt;&lt;path d=&quot;M100.0,430 L100.0,400.92857142857144 L240.0,387.7142857142857 L380.0,276.71428571428567 L520.0,311.07142857142856 L660.0,213.28571428571428 L800.0,126.07142857142856 L800.0,430 Z&quot; fill=&quot;#5681D5&quot; opacity=&quot;0.75&quot;/&gt;&lt;path d=&quot;M100.0,400.92857142857144 L240.0,387.7142857142857 L380.0,276.71428571428567 L520.0,311.07142857142856 L660.0,213.28571428571428 L800.0,126.07142857142856&quot; fill=&quot;none&quot; stroke=&quot;#5681D5&quot; stroke-width=&quot;2&quot;/&gt;&lt;path d=&quot;M100.0,430 L100.0,430.0 L240.0,400.92857142857144 L380.0,329.57142857142856 L520.0,350.7142857142857 L660.0,345.42857142857144 L800.0,258.2142857142857 L800.0,430 Z&quot; fill=&quot;#3A5EC5&quot; opacity=&quot;0.75&quot;/&gt;&lt;path d=&quot;M100.0,430.0 L240.0,400.92857142857144 L380.0,329.57142857142856 L520.0,350.7142857142857 L660.0,345.42857142857144 L800.0,258.2142857142857&quot; fill=&quot;none&quot; stroke=&quot;#3A5EC5&quot; stroke-width=&quot;2&quot;/&gt;&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_column_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for column.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <polygon points="0,0 350,0 350,900 0,900" fill="#E9F9F8"/>
    <textbox x="50" y="80" width="250" height="200" font="Segoe UI" size="55" color="#111111" bold="true" align="left" vertical_align="top" single_line="false" max_lines="4" reflow_on_resize="true">Coffee
Culture</textbox>
    <textbox x="50" y="600" width="250" height="250" font="Segoe UI" size="28" color="#222222" align="left" vertical_align="top" single_line="false" max_lines="8" reflow_on_resize="true" line_spacing="1.4">{title}</textbox>
    <svg x="350" y="0" width="1250" height="900" pixel_width="1250" pixel_height="900">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1250&quot; height=&quot;900&quot; viewBox=&quot;0 0 1250 900&quot;&gt;&lt;line x1=&quot;120&quot; y1=&quot;770.0&quot; x2=&quot;1120&quot; y2=&quot;770.0&quot; stroke=&quot;#333333&quot; stroke-width=&quot;3&quot;/&gt;&lt;text x=&quot;90&quot; y=&quot;777.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#333333&quot; text-anchor=&quot;end&quot;&gt;0&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;661.6666666666666&quot; x2=&quot;1120&quot; y2=&quot;661.6666666666666&quot; stroke=&quot;#E0E0E0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;90&quot; y=&quot;668.6666666666666&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#333333&quot; text-anchor=&quot;end&quot;&gt;10&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;553.3333333333334&quot; x2=&quot;1120&quot; y2=&quot;553.3333333333334&quot; stroke=&quot;#E0E0E0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;90&quot; y=&quot;560.3333333333334&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#333333&quot; text-anchor=&quot;end&quot;&gt;20&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;445.0&quot; x2=&quot;1120&quot; y2=&quot;445.0&quot; stroke=&quot;#E0E0E0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;90&quot; y=&quot;452.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#333333&quot; text-anchor=&quot;end&quot;&gt;30&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;336.6666666666667&quot; x2=&quot;1120&quot; y2=&quot;336.6666666666667&quot; stroke=&quot;#E0E0E0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;90&quot; y=&quot;343.6666666666667&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#333333&quot; text-anchor=&quot;end&quot;&gt;40&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;228.33333333333337&quot; x2=&quot;1120&quot; y2=&quot;228.33333333333337&quot; stroke=&quot;#E0E0E0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;90&quot; y=&quot;235.33333333333337&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#333333&quot; text-anchor=&quot;end&quot;&gt;50&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;120.0&quot; x2=&quot;1120&quot; y2=&quot;120.0&quot; stroke=&quot;#E0E0E0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;90&quot; y=&quot;127.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#333333&quot; text-anchor=&quot;end&quot;&gt;60&lt;/text&gt;&lt;rect x=&quot;161.42857142857144&quot; y=&quot;390.8333333333333&quot; width=&quot;60.0&quot; height=&quot;379.1666666666667&quot; fill=&quot;#7FE5DC&quot;/&gt;&lt;text x=&quot;191.42857142857144&quot; y=&quot;805&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;Thailand&lt;/text&gt;&lt;rect x=&quot;304.28571428571433&quot; y=&quot;195.83333333333337&quot; width=&quot;60.0&quot; height=&quot;574.1666666666666&quot; fill=&quot;#35D5CD&quot;/&gt;&lt;text x=&quot;334.28571428571433&quot; y=&quot;805&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;Philippines&lt;/text&gt;&lt;rect x=&quot;447.14285714285717&quot; y=&quot;277.08333333333337&quot; width=&quot;60.0&quot; height=&quot;492.91666666666663&quot; fill=&quot;#3ABEEB&quot;/&gt;&lt;text x=&quot;477.14285714285717&quot; y=&quot;805&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;Ethiopia&lt;/text&gt;&lt;rect x=&quot;590.0&quot; y=&quot;488.3333333333333&quot; width=&quot;60.0&quot; height=&quot;281.6666666666667&quot; fill=&quot;#2B88D8&quot;/&gt;&lt;text x=&quot;620.0&quot; y=&quot;805&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;Columbia&lt;/text&gt;&lt;rect x=&quot;732.8571428571429&quot; y=&quot;607.5&quot; width=&quot;60.0&quot; height=&quot;162.5&quot; fill=&quot;#7FE5DC&quot;/&gt;&lt;text x=&quot;762.8571428571429&quot; y=&quot;805&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;Australia&lt;/text&gt;&lt;rect x=&quot;875.7142857142858&quot; y=&quot;293.33333333333337&quot; width=&quot;60.0&quot; height=&quot;476.66666666666663&quot; fill=&quot;#35D5CD&quot;/&gt;&lt;text x=&quot;905.7142857142858&quot; y=&quot;805&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;Vietnam&lt;/text&gt;&lt;rect x=&quot;1018.5714285714286&quot; y=&quot;553.3333333333334&quot; width=&quot;60.0&quot; height=&quot;216.66666666666666&quot; fill=&quot;#3ABEEB&quot;/&gt;&lt;text x=&quot;1048.5714285714284&quot; y=&quot;805&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;Brazil&lt;/text&gt;&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_comparison_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for comparison.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <polygon points="10,10 1590,10 1590,890 10,890" fill="#FFFFFF"/>
    <svg x="10" y="10" width="1580" height="880" pixel_width="1580" pixel_height="880">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1580&quot; height=&quot;880&quot; viewBox=&quot;0 0 1580 880&quot;&gt;&lt;rect x=&quot;0&quot; y=&quot;0&quot; width=&quot;1580&quot; height=&quot;880&quot; rx=&quot;15&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#EAEAEA&quot; stroke-width=&quot;2&quot;/&gt;&lt;/svg&gt;</svg>
    <textbox x="250" y="80" width="1100" height="150" font="Segoe UI" size="35" color="#182E87" bold="true" align="center" vertical_align="top" single_line="false" max_lines="4" reflow_on_resize="true">The Marketing Campaign Results Analysis highlights the
campaign's performance against its goals, showcasing key
achievements and areas for improvement.</textbox>
    <textbox x="80" y="800" width="500" height="40" font="Segoe UI" size="20" color="#005BD4" bold="true" align="left" vertical_align="middle" single_line="true">{title}</textbox>
    <textbox x="100" y="380" width="400" height="150" font="Segoe UI" size="120" color="#182E87" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <textbox x="110" y="540" width="350" height="200" font="Segoe UI" size="22" color="#182E87" align="left" vertical_align="top" single_line="false" max_lines="6" reflow_on_resize="true" line_spacing="1.2">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi et quam vehicula, ornare nunc sed, ultricies purus.</textbox>
    <textbox x="1150" y="380" width="400" height="150" font="Segoe UI" size="120" color="#182E87" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">28%</textbox>
    <textbox x="1160" y="540" width="350" height="200" font="Segoe UI" size="22" color="#182E87" align="left" vertical_align="top" single_line="false" max_lines="6" reflow_on_resize="true" line_spacing="1.2">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi et quam vehicula, ornare nunc sed, ultricies purus.</textbox>
    <svg x="500" y="300" width="600" height="500" pixel_width="600" pixel_height="500">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;600&quot; height=&quot;500&quot; viewBox=&quot;0 0 600 500&quot;&gt;&lt;circle cx=&quot;180&quot; cy=&quot;30&quot; r=&quot;12&quot; fill=&quot;#005BD4&quot;/&gt;&lt;text x=&quot;200&quot; y=&quot;36&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#182E87&quot;&gt;Email Marketing&lt;/text&gt;&lt;circle cx=&quot;380&quot; cy=&quot;30&quot; r=&quot;12&quot; fill=&quot;#182E87&quot;/&gt;&lt;text x=&quot;400&quot; y=&quot;36&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#182E87&quot;&gt;SEO&lt;/text&gt;&lt;circle cx=&quot;300&quot; cy=&quot;260&quot; r=&quot;100.0&quot; fill=&quot;transparent&quot; stroke=&quot;#005BD4&quot; stroke-width=&quot;200&quot; stroke-dasharray=&quot;175.92918860102844 628.3185307179587&quot; transform=&quot;rotate(-90 300 260)&quot; /&gt;&lt;circle cx=&quot;300&quot; cy=&quot;260&quot; r=&quot;100.0&quot; fill=&quot;transparent&quot; stroke=&quot;#182E87&quot; stroke-width=&quot;200&quot; stroke-dasharray=&quot;452.3893421169302 628.3185307179587&quot; transform=&quot;rotate(10.800000000000011 300 260)&quot; /&gt;&lt;text x=&quot;392.4615891330947&quot; y=&quot;183.50912123015723&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;28&quot; font-weight=&quot;bold&quot; fill=&quot;#FFFFFF&quot; text-anchor=&quot;middle&quot; dominant-baseline=&quot;middle&quot;&gt;28%&lt;/text&gt;&lt;text x=&quot;207.53841086690528&quot; y=&quot;336.49087876984277&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;28&quot; font-weight=&quot;bold&quot; fill=&quot;#FFFFFF&quot; text-anchor=&quot;middle&quot; dominant-baseline=&quot;middle&quot;&gt;72%&lt;/text&gt;&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_dark_bar_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for dark bar.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#050505">
    <polygon points="5,5 1595,5 1595,895 5,895" fill="#050505"/>
    <textbox x="100" y="100" width="600" height="120" font="Segoe UI" size="100" color="#FFFFFF" bold="true" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="100" y="230" width="600" height="140" font="Segoe UI" size="120" color="#DFFF00" bold="true" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="100" y="450" width="400" height="350" pixel_width="400" pixel_height="350">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;400&quot; height=&quot;350&quot; viewBox=&quot;0 0 400 350&quot;&gt;&lt;rect x=&quot;0&quot; y=&quot;0&quot; width=&quot;400&quot; height=&quot;350&quot; rx=&quot;50&quot; fill=&quot;#DFFF00&quot;/&gt;&lt;line x1=&quot;335.0&quot; y1=&quot;70.0&quot; x2=&quot;350.0&quot; y2=&quot;70.0&quot; stroke=&quot;#050505&quot; stroke-width=&quot;8&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;332.5&quot; y1=&quot;74.3301270189222&quot; x2=&quot;340.0&quot; y2=&quot;87.32050807568876&quot; stroke=&quot;#050505&quot; stroke-width=&quot;8&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;327.5&quot; y1=&quot;74.3301270189222&quot; x2=&quot;320.0&quot; y2=&quot;87.32050807568878&quot; stroke=&quot;#050505&quot; stroke-width=&quot;8&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;325.0&quot; y1=&quot;70.0&quot; x2=&quot;310.0&quot; y2=&quot;70.0&quot; stroke=&quot;#050505&quot; stroke-width=&quot;8&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;327.5&quot; y1=&quot;65.6698729810778&quot; x2=&quot;320.0&quot; y2=&quot;52.67949192431123&quot; stroke=&quot;#050505&quot; stroke-width=&quot;8&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;332.5&quot; y1=&quot;65.6698729810778&quot; x2=&quot;340.0&quot; y2=&quot;52.67949192431123&quot; stroke=&quot;#050505&quot; stroke-width=&quot;8&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;circle cx=&quot;330&quot; cy=&quot;70&quot; r=&quot;8&quot; fill=&quot;#050505&quot;/&gt;&lt;/svg&gt;</svg>
    <textbox x="150" y="530" width="300" height="120" font="Segoe UI" size="100" color="#050505" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">27%</textbox>
    <textbox x="150" y="670" width="300" height="100" font="Segoe UI" size="24" color="#050505" align="left" vertical_align="top" single_line="false" max_lines="3" reflow_on_resize="true" line_spacing="1.3">Lorem ipsum dolor sit amet,
consectetur adipiscing elit.</textbox>
    <svg x="500" y="50" width="1000" height="800" pixel_width="1000" pixel_height="800">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1000&quot; height=&quot;800&quot; viewBox=&quot;0 0 1000 800&quot;&gt;&lt;circle cx=&quot;400&quot; cy=&quot;30&quot; r=&quot;10&quot; fill=&quot;#DFFF00&quot;/&gt;&lt;text x=&quot;420&quot; y=&quot;36&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#FFFFFF&quot;&gt;Market 1&lt;/text&gt;&lt;circle cx=&quot;550&quot; cy=&quot;30&quot; r=&quot;10&quot; fill=&quot;#7B8C00&quot;/&gt;&lt;text x=&quot;570&quot; y=&quot;36&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#FFFFFF&quot;&gt;Market 2&lt;/text&gt;&lt;line x1=&quot;250.0&quot; y1=&quot;100&quot; x2=&quot;250.0&quot; y2=&quot;710&quot; stroke=&quot;#222222&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;250.0&quot; y=&quot;735&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;18&quot; fill=&quot;#F0F0F0&quot; text-anchor=&quot;middle&quot;&gt;0&lt;/text&gt;&lt;line x1=&quot;400.0&quot; y1=&quot;100&quot; x2=&quot;400.0&quot; y2=&quot;710&quot; stroke=&quot;#222222&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;400.0&quot; y=&quot;735&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;18&quot; fill=&quot;#F0F0F0&quot; text-anchor=&quot;middle&quot;&gt;5&lt;/text&gt;&lt;line x1=&quot;550.0&quot; y1=&quot;100&quot; x2=&quot;550.0&quot; y2=&quot;710&quot; stroke=&quot;#222222&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;550.0&quot; y=&quot;735&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;18&quot; fill=&quot;#F0F0F0&quot; text-anchor=&quot;middle&quot;&gt;10&lt;/text&gt;&lt;line x1=&quot;700.0&quot; y1=&quot;100&quot; x2=&quot;700.0&quot; y2=&quot;710&quot; stroke=&quot;#222222&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;700.0&quot; y=&quot;735&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;18&quot; fill=&quot;#F0F0F0&quot; text-anchor=&quot;middle&quot;&gt;15&lt;/text&gt;&lt;line x1=&quot;850.0&quot; y1=&quot;100&quot; x2=&quot;850.0&quot; y2=&quot;710&quot; stroke=&quot;#222222&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;850.0&quot; y=&quot;735&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;18&quot; fill=&quot;#F0F0F0&quot; text-anchor=&quot;middle&quot;&gt;20&lt;/text&gt;&lt;text x=&quot;230&quot; y=&quot;206.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#F0F0F0&quot; text-anchor=&quot;end&quot;&gt;Trend 1&lt;/text&gt;&lt;rect x=&quot;250&quot; y=&quot;130.0&quot; width=&quot;90.0&quot; height=&quot;70.0&quot; rx=&quot;5&quot; fill=&quot;#DFFF00&quot;/&gt;&lt;rect x=&quot;250&quot; y=&quot;200.0&quot; width=&quot;180.0&quot; height=&quot;70.0&quot; rx=&quot;5&quot; fill=&quot;#7B8C00&quot;/&gt;&lt;text x=&quot;230&quot; y=&quot;406.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#F0F0F0&quot; text-anchor=&quot;end&quot;&gt;Trend 2&lt;/text&gt;&lt;rect x=&quot;250&quot; y=&quot;330.0&quot; width=&quot;240.0&quot; height=&quot;70.0&quot; rx=&quot;5&quot; fill=&quot;#DFFF00&quot;/&gt;&lt;rect x=&quot;250&quot; y=&quot;400.0&quot; width=&quot;420.0&quot; height=&quot;70.0&quot; rx=&quot;5&quot; fill=&quot;#7B8C00&quot;/&gt;&lt;text x=&quot;230&quot; y=&quot;606.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#F0F0F0&quot; text-anchor=&quot;end&quot;&gt;Trend 3&lt;/text&gt;&lt;rect x=&quot;250&quot; y=&quot;530.0&quot; width=&quot;480.0&quot; height=&quot;70.0&quot; rx=&quot;5&quot; fill=&quot;#DFFF00&quot;/&gt;&lt;rect x=&quot;250&quot; y=&quot;600.0&quot; width=&quot;540.0&quot; height=&quot;70.0&quot; rx=&quot;5&quot; fill=&quot;#7B8C00&quot;/&gt;&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_dark_pie_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for dark pie.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#050505">
    <polygon points="5,5 1595,5 1595,895 5,895" fill="#050505"/>
    <textbox x="100" y="120" width="600" height="120" font="Segoe UI" size="100" color="#FFFFFF" bold="true" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="100" y="240" width="600" height="140" font="Segoe UI" size="120" color="#DFFF00" bold="true" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <textbox x="100" y="420" width="400" height="150" font="Segoe UI" size="24" color="#F0F0F0" align="left" vertical_align="top" single_line="false" max_lines="4" reflow_on_resize="true" line_spacing="1.2">Lorem ipsum dolor sit amet,
consectetur adipiscing elit.
Morbi et quam vehicula.</textbox>
    <svg x="100" y="750" width="80" height="80" pixel_width="80" pixel_height="80">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;80&quot; height=&quot;80&quot; viewBox=&quot;0 0 80 80&quot;&gt;&lt;line x1=&quot;48.0&quot; y1=&quot;40.0&quot; x2=&quot;65.0&quot; y2=&quot;40.0&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;46.92820323027551&quot; y1=&quot;44.0&quot; x2=&quot;61.65063509461097&quot; y2=&quot;52.5&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;44.0&quot; y1=&quot;46.92820323027551&quot; x2=&quot;52.5&quot; y2=&quot;61.65063509461096&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;40.0&quot; y1=&quot;48.0&quot; x2=&quot;40.0&quot; y2=&quot;65.0&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;36.0&quot; y1=&quot;46.92820323027551&quot; x2=&quot;27.500000000000007&quot; y2=&quot;61.65063509461097&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;33.07179676972449&quot; y1=&quot;44.0&quot; x2=&quot;18.34936490538903&quot; y2=&quot;52.5&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;32.0&quot; y1=&quot;40.0&quot; x2=&quot;15.0&quot; y2=&quot;40.0&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;33.07179676972449&quot; y1=&quot;36.0&quot; x2=&quot;18.349364905389034&quot; y2=&quot;27.499999999999996&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;36.0&quot; y1=&quot;33.07179676972449&quot; x2=&quot;27.49999999999999&quot; y2=&quot;18.349364905389038&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;40.0&quot; y1=&quot;32.0&quot; x2=&quot;39.99999999999999&quot; y2=&quot;15.0&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;44.0&quot; y1=&quot;33.07179676972449&quot; x2=&quot;52.5&quot; y2=&quot;18.349364905389034&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;line x1=&quot;46.92820323027551&quot; y1=&quot;36.0&quot; x2=&quot;61.65063509461096&quot; y2=&quot;27.49999999999999&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;3&quot; stroke-linecap=&quot;round&quot;/&gt;&lt;circle cx=&quot;40&quot; cy=&quot;40&quot; r=&quot;12&quot; fill=&quot;#DFFF00&quot;/&gt;&lt;/svg&gt;</svg>
    <svg x="600" y="80" width="900" height="740" pixel_width="900" pixel_height="740">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;900&quot; height=&quot;740&quot; viewBox=&quot;0 0 900 740&quot;&gt;&lt;circle cx=&quot;500&quot; cy=&quot;370&quot; r=&quot;150.0&quot; fill=&quot;transparent&quot; stroke=&quot;#7B8C00&quot; stroke-width=&quot;300&quot; stroke-dasharray=&quot;117.80972450961724 942.4777960769379&quot; transform=&quot;rotate(-90 500 370)&quot; /&gt;&lt;text x=&quot;633.9392013277815&quot; y=&quot;36.64216362104963&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#FFFFFF&quot; text-anchor=&quot;start&quot;&gt;Growth 1&lt;/text&gt;&lt;text x=&quot;633.9392013277815&quot; y=&quot;61.64216362104963&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#FFFFFF&quot; text-anchor=&quot;start&quot;&gt;12.5%&lt;/text&gt;&lt;circle cx=&quot;500&quot; cy=&quot;370&quot; r=&quot;150.0&quot; fill=&quot;transparent&quot; stroke=&quot;#A8C000&quot; stroke-width=&quot;300&quot; stroke-dasharray=&quot;235.61944901923448 942.4777960769379&quot; transform=&quot;rotate(-45.0 500 370)&quot; /&gt;&lt;text x=&quot;850.0&quot; y=&quot;360.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#FFFFFF&quot; text-anchor=&quot;start&quot;&gt;Growth 2&lt;/text&gt;&lt;text x=&quot;850.0&quot; y=&quot;385.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#FFFFFF&quot; text-anchor=&quot;start&quot;&gt;25%&lt;/text&gt;&lt;circle cx=&quot;500&quot; cy=&quot;370&quot; r=&quot;150.0&quot; fill=&quot;transparent&quot; stroke=&quot;#DFFF00&quot; stroke-width=&quot;300&quot; stroke-dasharray=&quot;589.0486225480862 942.4777960769379&quot; transform=&quot;rotate(45.0 500 370)&quot; /&gt;&lt;text x=&quot;176.64216362104963&quot; y=&quot;493.93920132778146&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#FFFFFF&quot; text-anchor=&quot;end&quot;&gt;Growth 3&lt;/text&gt;&lt;text x=&quot;176.64216362104963&quot; y=&quot;518.9392013277815&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#FFFFFF&quot; text-anchor=&quot;end&quot;&gt;62.5%&lt;/text&gt;&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_dashboard_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for dashboard.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#EDF2F7">
    <svg x="0" y="0" width="1600" height="900" pixel_width="1600" pixel_height="900">&lt;svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"&gt;
        &lt;!-- Title --&gt;
        &lt;text x="100" y="100" font-family="Segoe UI" font-size="54" fill="#333333"&gt;Annual &lt;tspan font-weight="bold" fill="#222222"&gt;Revenue Target&lt;/tspan&gt;&lt;/text&gt;

        &lt;!-- Left Panel Cards --&gt;
        &lt;!-- Card 1: Blue --&gt;
        &lt;rect x="100" y="180" width="380" height="180" rx="24" fill="#5068DD" /&gt;
        &lt;circle cx="140" cy="225" r="14" fill="none" stroke="#FFFFFF" stroke-width="2"/&gt;
        &lt;path d="M140 218 L140 232 M133 225 L147 225" stroke="#FFFFFF" stroke-width="2"/&gt;
        &lt;text x="170" y="232" font-family="Segoe UI" font-size="20" fill="#FFFFFF" opacity="0.9"&gt;Annual Revenue Target&lt;/text&gt;
        &lt;text x="125" y="295" font-family="Segoe UI" font-size="48" font-weight="bold" fill="#FFFFFF"&gt;$12M&lt;/text&gt;
        &lt;text x="125" y="325" font-family="Segoe UI" font-size="18" fill="#FFFFFF" opacity="0.8"&gt;on target&lt;/text&gt;

        &lt;!-- Card 2: Yellow --&gt;
        &lt;rect x="100" y="390" width="380" height="180" rx="24" fill="#F2B71A" /&gt;
        &lt;circle cx="140" cy="435" r="14" fill="none" stroke="#FFFFFF" stroke-width="2"/&gt;
        &lt;polyline points="133 430 140 437 150 425" fill="none" stroke="#FFFFFF" stroke-width="2"/&gt;
        &lt;text x="170" y="442" font-family="Segoe UI" font-size="20" fill="#FFFFFF" opacity="0.9"&gt;Current YTD (Q3)&lt;/text&gt;
        &lt;text x="125" y="505" font-family="Segoe UI" font-size="48" font-weight="bold" fill="#FFFFFF"&gt;$8.7M&lt;/text&gt;
        &lt;text x="125" y="535" font-family="Segoe UI" font-size="18" fill="#FFFFFF" opacity="0.8"&gt;72% to target&lt;/text&gt;

        &lt;!-- Card 3: Pink --&gt;
        &lt;rect x="100" y="600" width="380" height="180" rx="24" fill="#F13A5C" /&gt;
        &lt;circle cx="140" cy="645" r="14" fill="none" stroke="#FFFFFF" stroke-width="2"/&gt;
        &lt;path d="M140 635 Q145 640 145 645 A 5 5 0 0 1 135 645 Q135 640 140 635" fill="none" stroke="#FFFFFF" stroke-width="2"/&gt;
        &lt;text x="170" y="652" font-family="Segoe UI" font-size="20" fill="#FFFFFF" opacity="0.9"&gt;Forecast Q4&lt;/text&gt;
        &lt;text x="125" y="715" font-family="Segoe UI" font-size="48" font-weight="bold" fill="#FFFFFF"&gt;+5-7%&lt;/text&gt;
        &lt;text x="125" y="745" font-family="Segoe UI" font-size="18" fill="#FFFFFF" opacity="0.8"&gt;Expected Growth&lt;/text&gt;

        &lt;!-- Right Panel (White Area) --&gt;
        &lt;rect x="520" y="180" width="980" height="600" rx="30" fill="#FFFFFF" /&gt;
        &lt;text x="570" y="240" font-family="Segoe UI" font-size="28" fill="#444444" font-weight="bold"&gt;Annual Financial Goals&lt;/text&gt;

        &lt;!-- Chart Y-Axis --&gt;
        &lt;line x1="620" y1="700" x2="1420" y2="700" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="600" y="706" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="end"&gt;0&lt;/text&gt;
        
        &lt;line x1="620" y1="640" x2="1420" y2="640" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="600" y="646" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="end"&gt;2&lt;/text&gt;

        &lt;line x1="620" y1="580" x2="1420" y2="580" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="600" y="586" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="end"&gt;4&lt;/text&gt;

        &lt;line x1="620" y1="520" x2="1420" y2="520" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="600" y="526" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="end"&gt;6&lt;/text&gt;

        &lt;line x1="620" y1="460" x2="1420" y2="460" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="600" y="466" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="end"&gt;8&lt;/text&gt;

        &lt;line x1="620" y1="400" x2="1420" y2="400" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="600" y="406" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="end"&gt;10&lt;/text&gt;

        &lt;line x1="620" y1="340" x2="1420" y2="340" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="600" y="346" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="end"&gt;12&lt;/text&gt;

        &lt;line x1="620" y1="280" x2="1420" y2="280" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="600" y="286" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="end"&gt;14&lt;/text&gt;

        &lt;!-- Chart X-Axis --&gt;
        &lt;text x="720" y="740" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="middle"&gt;Q1&lt;/text&gt;
        &lt;text x="920" y="740" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="middle"&gt;Q2&lt;/text&gt;
        &lt;text x="1120" y="740" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="middle"&gt;Q3&lt;/text&gt;
        &lt;text x="1320" y="740" font-family="Segoe UI" font-size="18" fill="#A0A0A0" text-anchor="middle"&gt;Q4&lt;/text&gt;

        &lt;!-- Chart Data Points --&gt;
        &lt;path d="M 720 535 L 920 475 L 1120 439 L 1320 316" fill="none" stroke="#9B51E0" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/&gt;
        
        &lt;circle cx="720" cy="535" r="5" fill="#9B51E0" /&gt;
        &lt;circle cx="920" cy="475" r="5" fill="#9B51E0" /&gt;
        &lt;circle cx="1120" cy="439" r="5" fill="#9B51E0" /&gt;
        &lt;circle cx="1320" cy="316" r="12" fill="#E8D5F8" /&gt;
        &lt;circle cx="1320" cy="316" r="6" fill="#9B51E0" /&gt;

        &lt;!-- Tooltip --&gt;
        &lt;rect x="1180" y="240" width="280" height="50" rx="8" fill="#F4F4F4" stroke="#EAEAEA" stroke-width="1" /&gt;
        &lt;polygon points="1310,290 1320,300 1330,290" fill="#F4F4F4" stroke="#EAEAEA" stroke-width="1" /&gt;
        &lt;polygon points="1311,290 1320,298 1329,290" fill="#F4F4F4" /&gt; 
        &lt;text x="1320" y="271" font-family="Segoe UI" font-size="20" fill="#444444" font-weight="bold" text-anchor="middle"&gt;Projected to exceed target&lt;/text&gt;

&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_financial_projections_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for financial projections.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#F4F4F4">
    <svg x="0" y="0" width="1600" height="900" pixel_width="1600" pixel_height="900">&lt;svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"&gt;
    &lt;!-- Faint background elements --&gt;
    &lt;circle cx="1400" cy="-50" r="250" fill="#EAEAEA" /&gt;
    &lt;circle cx="1050" cy="950" r="150" fill="#EAEAEA" /&gt;
    &lt;circle cx="-50" cy="450" r="120" fill="#EAEAEA" /&gt;

    &lt;!-- Corner Polygons (Yellow) --&gt;
    &lt;!-- Top Left --&gt;
    &lt;polygon points="0,0 150,0 50,150 0,100" fill="#F4D37E" /&gt;
    &lt;polygon points="0,150 70,120 70,220 0,220" fill="#F4D37E" /&gt;
    &lt;polygon points="150,0 300,0 200,80" fill="#D8AC51" /&gt;
    &lt;polygon points="0,0 150,0 0,60" fill="#D8AC51" /&gt;
    &lt;!-- Bottom Right --&gt;
    &lt;polygon points="1600,900 1350,900 1450,750 1600,800" fill="#F4D37E" /&gt;
    &lt;polygon points="1600,750 1530,780 1530,680 1600,680" fill="#F4D37E" /&gt;
    &lt;polygon points="1350,900 1250,900 1300,820" fill="#D8AC51" /&gt;

    &lt;!-- Top Left Logo --&gt;
    &lt;circle cx="110" cy="80" r="14" fill="#D8AC51" /&gt;
    &lt;path d="M100 80 L120 80 L110 100 Z" fill="#F4D37E" /&gt;
    &lt;path d="M125 70 L140 85 L125 100 L110 85 Z" fill="#F4D37E" /&gt;
    &lt;text x="160" y="90" font-family="Segoe UI" font-size="24" fill="#1A1B4B" font-weight="600"&gt;Thynk Unlimited&lt;/text&gt;

    &lt;!-- Bottom Left URL --&gt;
    &lt;text x="90" y="810" font-family="Segoe UI" font-size="24" fill="#1A1B4B" font-weight="600"&gt;www.reallygreatsite.com&lt;/text&gt;

    &lt;!-- Right Side Content --&gt;
    &lt;text x="830" y="340" font-family="Segoe UI" font-size="85" fill="#090C5C" font-weight="400"&gt;Financial&lt;/text&gt;
    &lt;text x="830" y="440" font-family="Segoe UI" font-size="85" fill="#090C5C" font-weight="400"&gt;Projections&lt;/text&gt;

    &lt;!-- Right Side Paragraph --&gt;
    &lt;text x="830" y="600" font-family="Segoe UI" font-size="20" fill="#222222" font-weight="400"&gt;
        &lt;tspan x="830" dy="0"&gt;Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed&lt;/tspan&gt;
        &lt;tspan x="830" dy="30"&gt;do eiusmod tempor incididunt ut labore et dolore magna&lt;/tspan&gt;
        &lt;tspan x="830" dy="30"&gt;aliqua. Ut enim ad minim veniam, quis nostrud exercitation&lt;/tspan&gt;
        &lt;tspan x="830" dy="30"&gt;ullamco laboris nisi ut aliquip ex ea commodo consequat.&lt;/tspan&gt;
    &lt;/text&gt;

    &lt;!-- Donut Chart --&gt;
    &lt;g transform="translate(0, 0)"&gt;
        &lt;circle cx="480" cy="480" r="185" fill="transparent" stroke="#090C5C" stroke-width="130" stroke-dasharray="726.50 1162.40" transform="rotate(-90 480 480)"/&gt;
        &lt;circle cx="480" cy="480" r="185" fill="transparent" stroke="#EED27A" stroke-width="130" stroke-dasharray="290.60 1162.40" transform="rotate(135 480 480)"/&gt;
        &lt;circle cx="480" cy="480" r="185" fill="transparent" stroke="#05073B" stroke-width="130" stroke-dasharray="145.30 1162.40" transform="rotate(225 480 480)"/&gt;
    &lt;/g&gt;

    &lt;!-- Chart Labels --&gt;
    &lt;text x="790" y="585" font-family="Segoe UI" font-size="16" fill="#333333" font-weight="600" text-anchor="middle"&gt;Item 1&lt;/text&gt;
    &lt;text x="790" y="605" font-family="Segoe UI" font-size="16" fill="#333333" font-weight="600" text-anchor="middle"&gt;62.5%&lt;/text&gt;

    &lt;text x="200" y="475" font-family="Segoe UI" font-size="16" fill="#333333" font-weight="600" text-anchor="middle"&gt;Item 2&lt;/text&gt;
    &lt;text x="200" y="495" font-family="Segoe UI" font-size="16" fill="#333333" font-weight="600" text-anchor="middle"&gt;25%&lt;/text&gt;

    &lt;text x="375" y="225" font-family="Segoe UI" font-size="16" fill="#333333" font-weight="600" text-anchor="middle"&gt;Item 3&lt;/text&gt;
    &lt;text x="375" y="245" font-family="Segoe UI" font-size="16" fill="#333333" font-weight="600" text-anchor="middle"&gt;12.5%&lt;/text&gt;

&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_image_bar_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for image bar.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <svg x="10" y="10" width="1580" height="880" pixel_width="1580" pixel_height="880">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1580&quot; height=&quot;880&quot; viewBox=&quot;0 0 1580 880&quot;&gt;&lt;rect x=&quot;0&quot; y=&quot;0&quot; width=&quot;1580&quot; height=&quot;880&quot; rx=&quot;20&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#EAEAEA&quot; stroke-width=&quot;2&quot;/&gt;&lt;/svg&gt;</svg>
    <textbox x="100" y="100" width="500" height="80" font="Segoe UI" size="70" color="#182E87" bold="true" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="100" y="190" width="500" height="80" font="Segoe UI" size="70" color="#005BD4" bold="true" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <textbox x="100" y="310" width="500" height="150" font="Segoe UI" size="24" color="#182E87" align="left" vertical_align="top" single_line="false" max_lines="4" reflow_on_resize="true" line_spacing="1.3">Lorem ipsum dolor sit amet, consectetur
adipiscing elit. Morbi et quam vehicula, ornare
nunc sed, ultricies purus.</textbox>
    <textbox x="100" y="800" width="500" height="40" font="Segoe UI" size="18" color="#005BD4" bold="true" align="left" vertical_align="middle" single_line="true">Marketing Campaign Results Analysis</textbox>
    <svg x="100" y="520" width="550" height="250" pixel_width="550" pixel_height="250">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;550&quot; height=&quot;250&quot; viewBox=&quot;0 0 550 250&quot;&gt;&lt;line x1=&quot;0&quot; y1=&quot;197.5&quot; x2=&quot;500&quot; y2=&quot;197.5&quot; stroke=&quot;#F0F0F0&quot; stroke-width=&quot;1&quot;/&gt;&lt;line x1=&quot;0&quot; y1=&quot;145.0&quot; x2=&quot;500&quot; y2=&quot;145.0&quot; stroke=&quot;#F0F0F0&quot; stroke-width=&quot;1&quot;/&gt;&lt;line x1=&quot;0&quot; y1=&quot;92.5&quot; x2=&quot;500&quot; y2=&quot;92.5&quot; stroke=&quot;#F0F0F0&quot; stroke-width=&quot;1&quot;/&gt;&lt;line x1=&quot;0&quot; y1=&quot;40.0&quot; x2=&quot;500&quot; y2=&quot;40.0&quot; stroke=&quot;#F0F0F0&quot; stroke-width=&quot;1&quot;/&gt;&lt;rect x=&quot;22.5&quot; y=&quot;119.80000000000001&quot; width=&quot;80.0&quot; height=&quot;130.2&quot; fill=&quot;#005BD4&quot;/&gt;&lt;text x=&quot;62.5&quot; y=&quot;109.80000000000001&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#182E87&quot; text-anchor=&quot;middle&quot;&gt;62&lt;/text&gt;&lt;rect x=&quot;147.5&quot; y=&quot;82.0&quot; width=&quot;80.0&quot; height=&quot;168.0&quot; fill=&quot;#005BD4&quot;/&gt;&lt;text x=&quot;187.5&quot; y=&quot;72.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#182E87&quot; text-anchor=&quot;middle&quot;&gt;80&lt;/text&gt;&lt;rect x=&quot;272.5&quot; y=&quot;50.5&quot; width=&quot;80.0&quot; height=&quot;199.5&quot; fill=&quot;#005BD4&quot;/&gt;&lt;text x=&quot;312.5&quot; y=&quot;40.5&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#182E87&quot; text-anchor=&quot;middle&quot;&gt;95&lt;/text&gt;&lt;rect x=&quot;397.5&quot; y=&quot;113.5&quot; width=&quot;80.0&quot; height=&quot;136.5&quot; fill=&quot;#005BD4&quot;/&gt;&lt;text x=&quot;437.5&quot; y=&quot;103.5&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#182E87&quot; text-anchor=&quot;middle&quot;&gt;65&lt;/text&gt;&lt;/svg&gt;</svg>
    <image src="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&amp;fit=crop&amp;q=80&amp;w=750&amp;h=700" x="750" y="100" width="750" height="700" shape="roundrect" rx="20" ry="20"/>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_line_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for line.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FAFAFA">
    <svg x="0" y="0" width="1600" height="900" pixel_width="1600" pixel_height="900">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1600&quot; height=&quot;900&quot; viewBox=&quot;0 0 1600 900&quot;&gt;&lt;rect x=&quot;250&quot; y=&quot;60&quot; width=&quot;1100&quot; height=&quot;90&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#8A2BE2&quot; stroke-width=&quot;6&quot;/&gt;&lt;rect x=&quot;380.0&quot; y=&quot;800&quot; width=&quot;30&quot; height=&quot;30&quot; rx=&quot;8&quot; fill=&quot;#0080FF&quot;/&gt;&lt;text x=&quot;430.0&quot; y=&quot;822&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;24&quot; font-weight=&quot;bold&quot; fill=&quot;#0A0A1A&quot;&gt;Production&lt;/text&gt;&lt;rect x=&quot;660.0&quot; y=&quot;800&quot; width=&quot;30&quot; height=&quot;30&quot; rx=&quot;8&quot; fill=&quot;#A060FF&quot;/&gt;&lt;text x=&quot;710.0&quot; y=&quot;822&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;24&quot; font-weight=&quot;bold&quot; fill=&quot;#0A0A1A&quot;&gt;Sale&lt;/text&gt;&lt;rect x=&quot;940.0&quot; y=&quot;800&quot; width=&quot;30&quot; height=&quot;30&quot; rx=&quot;8&quot; fill=&quot;#00C0FF&quot;/&gt;&lt;text x=&quot;990.0&quot; y=&quot;822&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;24&quot; font-weight=&quot;bold&quot; fill=&quot;#0A0A1A&quot;&gt;Marketing&lt;/text&gt;&lt;/svg&gt;</svg>
    <textbox x="250" y="60" width="1100" height="90" font="Segoe UI" size="65" color="#111111" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <svg x="100" y="200" width="1400" height="550" pixel_width="1400" pixel_height="550">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1400&quot; height=&quot;550&quot; viewBox=&quot;0 0 1400 550&quot;&gt;&lt;rect x=&quot;10&quot; y=&quot;10&quot; width=&quot;1380&quot; height=&quot;500&quot; rx=&quot;15&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#E6E6E6&quot; stroke-width=&quot;2&quot;/&gt;&lt;line x1=&quot;120&quot; y1=&quot;410.0&quot; x2=&quot;1320&quot; y2=&quot;410.0&quot; stroke=&quot;#F2F2F2&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;100&quot; y=&quot;416.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;0&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;340.0&quot; x2=&quot;1320&quot; y2=&quot;340.0&quot; stroke=&quot;#F2F2F2&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;100&quot; y=&quot;346.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;12&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;270.0&quot; x2=&quot;1320&quot; y2=&quot;270.0&quot; stroke=&quot;#F2F2F2&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;100&quot; y=&quot;276.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;24&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;200.0&quot; x2=&quot;1320&quot; y2=&quot;200.0&quot; stroke=&quot;#F2F2F2&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;100&quot; y=&quot;206.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;36&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;130.0&quot; x2=&quot;1320&quot; y2=&quot;130.0&quot; stroke=&quot;#F2F2F2&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;100&quot; y=&quot;136.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;48&lt;/text&gt;&lt;line x1=&quot;120&quot; y1=&quot;60.0&quot; x2=&quot;1320&quot; y2=&quot;60.0&quot; stroke=&quot;#F2F2F2&quot; stroke-width=&quot;2&quot;/&gt;&lt;text x=&quot;100&quot; y=&quot;66.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#444444&quot; text-anchor=&quot;end&quot;&gt;60&lt;/text&gt;&lt;text x=&quot;120.0&quot; y=&quot;445&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;January&lt;/text&gt;&lt;text x=&quot;360.0&quot; y=&quot;445&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;February&lt;/text&gt;&lt;text x=&quot;600.0&quot; y=&quot;445&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;March&lt;/text&gt;&lt;text x=&quot;840.0&quot; y=&quot;445&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;April&lt;/text&gt;&lt;text x=&quot;1080.0&quot; y=&quot;445&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;May&lt;/text&gt;&lt;text x=&quot;1320.0&quot; y=&quot;445&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; font-weight=&quot;bold&quot; fill=&quot;#222222&quot; text-anchor=&quot;middle&quot;&gt;June&lt;/text&gt;&lt;path d=&quot;M120.0,340.0 C240.0,340.0 240.0,386.6666666666667 360.0,386.6666666666667 C480.0,386.6666666666667 480.0,293.33333333333337 600.0,293.33333333333337 C720.0,293.33333333333337 720.0,322.5 840.0,322.5 C960.0,322.5 960.0,118.33333333333331 1080.0,118.33333333333331 C1200.0,118.33333333333331 1200.0,235.0 1320.0,235.0&quot; fill=&quot;none&quot; stroke=&quot;#0080FF&quot; stroke-width=&quot;4&quot;/&gt;&lt;circle cx=&quot;120.0&quot; cy=&quot;340.0&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#0080FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;360.0&quot; cy=&quot;386.6666666666667&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#0080FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;600.0&quot; cy=&quot;293.33333333333337&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#0080FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;840.0&quot; cy=&quot;322.5&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#0080FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;1080.0&quot; cy=&quot;118.33333333333331&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#0080FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;1320.0&quot; cy=&quot;235.0&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#0080FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;path d=&quot;M120.0,410.0 C240.0,410.0 240.0,340.0 360.0,340.0 C480.0,340.0 480.0,188.33333333333334 600.0,188.33333333333334 C720.0,188.33333333333334 720.0,235.0 840.0,235.0 C960.0,235.0 960.0,223.33333333333334 1080.0,223.33333333333334 C1200.0,223.33333333333334 1200.0,264.16666666666663 1320.0,264.16666666666663&quot; fill=&quot;none&quot; stroke=&quot;#A060FF&quot; stroke-width=&quot;4&quot;/&gt;&lt;circle cx=&quot;120.0&quot; cy=&quot;410.0&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#A060FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;360.0&quot; cy=&quot;340.0&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#A060FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;600.0&quot; cy=&quot;188.33333333333334&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#A060FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;840.0&quot; cy=&quot;235.0&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#A060FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;1080.0&quot; cy=&quot;223.33333333333334&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#A060FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;1320.0&quot; cy=&quot;264.16666666666663&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#A060FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;path d=&quot;M120.0,305.0 C240.0,305.0 240.0,235.0 360.0,235.0 C480.0,235.0 480.0,264.16666666666663 600.0,264.16666666666663 C720.0,264.16666666666663 720.0,176.66666666666669 840.0,176.66666666666669 C960.0,176.66666666666669 960.0,165.00000000000003 1080.0,165.00000000000003 C1200.0,165.00000000000003 1200.0,135.83333333333331 1320.0,135.83333333333331&quot; fill=&quot;none&quot; stroke=&quot;#00C0FF&quot; stroke-width=&quot;4&quot;/&gt;&lt;circle cx=&quot;120.0&quot; cy=&quot;305.0&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#00C0FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;360.0&quot; cy=&quot;235.0&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#00C0FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;600.0&quot; cy=&quot;264.16666666666663&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#00C0FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;840.0&quot; cy=&quot;176.66666666666669&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#00C0FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;1080.0&quot; cy=&quot;165.00000000000003&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#00C0FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;circle cx=&quot;1320.0&quot; cy=&quot;135.83333333333331&quot; r=&quot;5&quot; fill=&quot;#FFFFFF&quot; stroke=&quot;#00C0FF&quot; stroke-width=&quot;3&quot;/&gt;&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_market_analysis_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for market analysis.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#0B1151">
    <svg x="0" y="0" width="1600" height="900" pixel_width="1600" pixel_height="900">&lt;svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"&gt;
    &lt;!-- Dark subtle background accents --&gt;
    &lt;circle cx="200" cy="0" r="300" fill="#060833" opacity="0.6"/&gt;
    &lt;circle cx="800" cy="450" r="250" fill="#060833" opacity="0.5"/&gt;
    &lt;circle cx="1500" cy="900" r="400" fill="#060833" opacity="0.4"/&gt;

    &lt;!-- Corner Polygons (Yellow) --&gt;
    &lt;!-- Top Right --&gt;
    &lt;polygon points="1600,0 1450,0 1550,150 1600,100" fill="#F4D37E" /&gt;
    &lt;polygon points="1600,150 1530,120 1530,220 1600,220" fill="#F4D37E" /&gt;
    &lt;polygon points="1450,0 1300,0 1400,80" fill="#D8AC51" /&gt;
    &lt;polygon points="1600,0 1450,0 1600,60" fill="#D8AC51" /&gt;
    &lt;!-- Bottom Left --&gt;
    &lt;polygon points="0,900 250,900 150,750 0,800" fill="#F4D37E" /&gt;
    &lt;polygon points="0,750 70,780 70,680 0,680" fill="#F4D37E" /&gt;
    &lt;polygon points="250,900 350,900 300,820" fill="#D8AC51" /&gt;

    &lt;!-- Top Left Logo --&gt;
    &lt;circle cx="110" cy="80" r="14" fill="#D8AC51" /&gt;
    &lt;path d="M100 80 L120 80 L110 100 Z" fill="#F4D37E" /&gt;
    &lt;path d="M125 70 L140 85 L125 100 L110 85 Z" fill="#F4D37E" /&gt;
    &lt;text x="160" y="90" font-family="Segoe UI" font-size="24" fill="#FFFFFF" font-weight="600"&gt;Thynk Unlimited&lt;/text&gt;

    &lt;!-- Bottom Right URL --&gt;
    &lt;text x="1100" y="810" font-family="Segoe UI" font-size="24" fill="#FFFFFF" font-weight="600"&gt;www.reallygreatsite.com&lt;/text&gt;

    &lt;!-- Right Side Content --&gt;
    &lt;text x="850" y="320" font-family="Segoe UI" font-size="85" fill="#FFFFFF" font-weight="400"&gt;Market&lt;/text&gt;
    &lt;text x="850" y="420" font-family="Segoe UI" font-size="85" fill="#FFFFFF" font-weight="400"&gt;Analysis&lt;/text&gt;

    &lt;!-- Right Side Paragraph --&gt;
    &lt;text x="850" y="520" font-family="Segoe UI" font-size="20" fill="#E0E0E0" font-weight="400"&gt;
        &lt;tspan x="850" dy="0"&gt;Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed&lt;/tspan&gt;
        &lt;tspan x="850" dy="30"&gt;do eiusmod tempor incididunt ut labore et dolore magna&lt;/tspan&gt;
        &lt;tspan x="850" dy="30"&gt;aliqua. Ut enim ad minim veniam, quis nostrud exercitation&lt;/tspan&gt;
        &lt;tspan x="850" dy="30"&gt;ullamco laboris nisi ut aliquip ex ea commodo consequat.&lt;/tspan&gt;
        &lt;tspan x="850" dy="60"&gt;Duis aute irure dolor in reprehenderit in voluptate velit esse&lt;/tspan&gt;
        &lt;tspan x="850" dy="30"&gt;cillum dolore eu fugiat nulla pariatur. Excepteur sint&lt;/tspan&gt;
        &lt;tspan x="850" dy="30"&gt;occaecat cupidatat non proident, sunt in culpa qui officia&lt;/tspan&gt;
        &lt;tspan x="850" dy="30"&gt;deserunt mollit anim id est laborum.&lt;/tspan&gt;
    &lt;/text&gt;

    &lt;!-- Line Chart Area --&gt;
    &lt;!-- Grid Lines (Horizontal) --&gt;
    &lt;!-- Y=50 --&gt;
    &lt;line x1="150" y1="200" x2="700" y2="200" stroke="#333A70" stroke-width="2"/&gt;
    &lt;text x="130" y="206" font-family="Segoe UI" font-size="16" fill="#A0A0A0" text-anchor="end"&gt;50&lt;/text&gt;
    &lt;!-- Y=40 --&gt;
    &lt;line x1="150" y1="300" x2="700" y2="300" stroke="#333A70" stroke-width="2"/&gt;
    &lt;text x="130" y="306" font-family="Segoe UI" font-size="16" fill="#A0A0A0" text-anchor="end"&gt;40&lt;/text&gt;
    &lt;!-- Y=30 --&gt;
    &lt;line x1="150" y1="400" x2="700" y2="400" stroke="#333A70" stroke-width="2"/&gt;
    &lt;text x="130" y="406" font-family="Segoe UI" font-size="16" fill="#A0A0A0" text-anchor="end"&gt;30&lt;/text&gt;
    &lt;!-- Y=20 --&gt;
    &lt;line x1="150" y1="500" x2="700" y2="500" stroke="#333A70" stroke-width="2"/&gt;
    &lt;text x="130" y="506" font-family="Segoe UI" font-size="16" fill="#A0A0A0" text-anchor="end"&gt;20&lt;/text&gt;
    &lt;!-- Y=10 --&gt;
    &lt;line x1="150" y1="600" x2="700" y2="600" stroke="#333A70" stroke-width="2"/&gt;
    &lt;text x="130" y="606" font-family="Segoe UI" font-size="16" fill="#A0A0A0" text-anchor="end"&gt;10&lt;/text&gt;
    &lt;!-- Y=0 --&gt;
    &lt;line x1="150" y1="700" x2="700" y2="700" stroke="#333A70" stroke-width="2"/&gt;
    &lt;text x="130" y="706" font-family="Segoe UI" font-size="16" fill="#A0A0A0" text-anchor="end"&gt;0&lt;/text&gt;

    &lt;!-- X-Axis Labels --&gt;
    &lt;text x="150" y="730" font-family="Segoe UI" font-size="16" fill="#E0E0E0" text-anchor="middle"&gt;Item 1&lt;/text&gt;
    &lt;text x="287.5" y="730" font-family="Segoe UI" font-size="16" fill="#E0E0E0" text-anchor="middle"&gt;Item 2&lt;/text&gt;
    &lt;text x="425" y="730" font-family="Segoe UI" font-size="16" fill="#E0E0E0" text-anchor="middle"&gt;Item 3&lt;/text&gt;
    &lt;text x="562.5" y="730" font-family="Segoe UI" font-size="16" fill="#E0E0E0" text-anchor="middle"&gt;Item 4&lt;/text&gt;
    &lt;text x="700" y="730" font-family="Segoe UI" font-size="16" fill="#E0E0E0" text-anchor="middle"&gt;Item 5&lt;/text&gt;

    &lt;!-- Legend --&gt;
    &lt;circle cx="250" cy="160" r="8" fill="#5747D7"/&gt;
    &lt;text x="270" y="166" font-family="Segoe UI" font-size="16" fill="#E0E0E0"&gt;Series 1&lt;/text&gt;

    &lt;circle cx="360" cy="160" r="8" fill="#F2C85B"/&gt;
    &lt;text x="380" y="166" font-family="Segoe UI" font-size="16" fill="#E0E0E0"&gt;Series 2&lt;/text&gt;

    &lt;circle cx="470" cy="160" r="8" fill="#FFFFFF"/&gt;
    &lt;text x="490" y="166" font-family="Segoe UI" font-size="16" fill="#E0E0E0"&gt;Series 3&lt;/text&gt;

    &lt;!-- Lines --&gt;
    &lt;!-- Series 1 (Purple: #5747D7) --&gt;
    &lt;path d="M 150 680 L 287.5 570 L 425 350 L 562.5 450 L 700 380" fill="none" stroke="#5747D7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/&gt;
    &lt;circle cx="150" cy="680" r="4" fill="#5747D7"/&gt;
    &lt;circle cx="287.5" cy="570" r="4" fill="#5747D7"/&gt;
    &lt;circle cx="425" cy="350" r="4" fill="#5747D7"/&gt;
    &lt;circle cx="562.5" cy="450" r="4" fill="#5747D7"/&gt;
    &lt;circle cx="700" cy="380" r="4" fill="#5747D7"/&gt;

    &lt;!-- Series 2 (Yellow: #F2C85B) --&gt;
    &lt;path d="M 150 580 L 287.5 670 L 425 500 L 562.5 550 L 700 220" fill="none" stroke="#F2C85B" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/&gt;
    &lt;circle cx="150" cy="580" r="4" fill="#F2C85B"/&gt;
    &lt;circle cx="287.5" cy="670" r="4" fill="#F2C85B"/&gt;
    &lt;circle cx="425" cy="500" r="4" fill="#F2C85B"/&gt;
    &lt;circle cx="562.5" cy="550" r="4" fill="#F2C85B"/&gt;
    &lt;circle cx="700" cy="220" r="4" fill="#F2C85B"/&gt;

    &lt;!-- Series 3 (White: #FFFFFF) --&gt;
    &lt;path d="M 150 540 L 287.5 400 L 425 450 L 562.5 330 L 700 310" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/&gt;
    &lt;circle cx="150" cy="540" r="4" fill="#FFFFFF"/&gt;
    &lt;circle cx="287.5" cy="400" r="4" fill="#FFFFFF"/&gt;
    &lt;circle cx="425" cy="450" r="4" fill="#FFFFFF"/&gt;
    &lt;circle cx="562.5" cy="330" r="4" fill="#FFFFFF"/&gt;
    &lt;circle cx="700" cy="310" r="4" fill="#FFFFFF"/&gt;

&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_people_culture_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for people culture.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#F4F5F7">
    <svg x="0" y="0" width="1600" height="900" pixel_width="1600" pixel_height="900">&lt;svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"&gt;
        &lt;!-- Title --&gt;
        &lt;text x="100" y="120" font-family="Segoe UI" font-size="54" font-weight="600" fill="#1A2F33"&gt;People &amp;amp; Culture&lt;/text&gt;

        &lt;!-- Left Panel Card 1: Employee Engagement (Teal) --&gt;
        &lt;rect x="100" y="180" width="360" height="300" rx="24" fill="#068D9D" /&gt;
        &lt;!-- Icon background --&gt;
        &lt;rect x="140" y="220" width="60" height="60" rx="16" fill="#F5E38C" /&gt;
        &lt;!-- People Icon --&gt;
        &lt;path d="M160 250 A 6 6 0 1 1 160 238 A 6 6 0 1 1 160 250 M150 262 Q160 252 170 262 L170 265 L150 265 Z" fill="none" stroke="#068D9D" stroke-width="3"/&gt;
        &lt;path d="M180 250 A 6 6 0 1 1 180 238 A 6 6 0 1 1 180 250 M170 262 Q180 252 190 262 L190 265 L170 265 Z" fill="none" stroke="#068D9D" stroke-width="3"/&gt;

        &lt;text x="140" y="330" font-family="Segoe UI" font-size="24" fill="#FFFFFF" opacity="0.9"&gt;Employee Engagement&lt;/text&gt;
        &lt;text x="140" y="400" font-family="Segoe UI" font-size="64" font-weight="bold" fill="#FFFFFF"&gt;89%&lt;/text&gt;
        &lt;text x="270" y="390" font-family="Segoe UI" font-size="20" fill="#FFFFFF" opacity="0.8"&gt;satisfaction&lt;/text&gt;
        &lt;text x="140" y="440" font-family="Segoe UI" font-size="20" fill="#B0E5E5"&gt;(+5%)&lt;/text&gt;

        &lt;!-- Left Panel Card 2: Training Hours (Teal) --&gt;
        &lt;rect x="100" y="520" width="360" height="300" rx="24" fill="#068D9D" /&gt;
        &lt;!-- Icon background --&gt;
        &lt;rect x="140" y="560" width="60" height="60" rx="16" fill="#F5E38C" /&gt;
        &lt;!-- Clock Icon --&gt;
        &lt;circle cx="170" cy="590" r="14" fill="none" stroke="#068D9D" stroke-width="3"/&gt;
        &lt;polyline points="170 583 170 590 176 594" fill="none" stroke="#068D9D" stroke-width="3" stroke-linecap="round"/&gt;

        &lt;text x="140" y="670" font-family="Segoe UI" font-size="24" fill="#FFFFFF" opacity="0.9"&gt;Average Training Hours&lt;/text&gt;
        &lt;text x="140" y="740" font-family="Segoe UI" font-size="64" font-weight="bold" fill="#FFFFFF"&gt;37 hrs&lt;/text&gt;
        &lt;text x="330" y="730" font-family="Segoe UI" font-size="20" fill="#FFFFFF" opacity="0.8"&gt;per employee&lt;/text&gt;
        &lt;text x="140" y="780" font-family="Segoe UI" font-size="20" fill="#B0E5E5"&gt;(+12%)&lt;/text&gt;

        &lt;!-- Right Panel Top (Chart) --&gt;
        &lt;rect x="500" y="180" width="1000" height="440" rx="24" fill="#FFFFFF" /&gt;
        &lt;text x="540" y="240" font-family="Segoe UI" font-size="24" fill="#333333"&gt;Monthly Growth (%)&lt;/text&gt;
        
        &lt;!-- Legend --&gt;
        &lt;circle cx="680" cy="280" r="8" fill="#80E5E5"/&gt;
        &lt;text x="700" y="286" font-family="Segoe UI" font-size="18" fill="#555555"&gt;Employee Engagement:&lt;/text&gt;
        
        &lt;circle cx="980" cy="280" r="8" fill="#54B2D3"/&gt;
        &lt;text x="1000" y="286" font-family="Segoe UI" font-size="18" fill="#555555"&gt;Training hours&lt;/text&gt;
        
        &lt;circle cx="1180" cy="280" r="8" fill="#3384B6"/&gt;
        &lt;text x="1200" y="286" font-family="Segoe UI" font-size="18" fill="#555555"&gt;Women in leadership&lt;/text&gt;

        &lt;!-- Y-Axis Lines --&gt;
        &lt;line x1="560" y1="350" x2="1440" y2="350" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="540" y="356" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="end"&gt;3%&lt;/text&gt;

        &lt;line x1="560" y1="410" x2="1440" y2="410" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="540" y="416" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="end"&gt;2%&lt;/text&gt;

        &lt;line x1="560" y1="470" x2="1440" y2="470" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="540" y="476" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="end"&gt;1%&lt;/text&gt;

        &lt;line x1="560" y1="530" x2="1440" y2="530" stroke="#F0F0F0" stroke-width="2"/&gt;
        &lt;text x="540" y="536" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="end"&gt;0%&lt;/text&gt;

        &lt;!-- X-Axis Labels --&gt;
        &lt;text x="580" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;Jan&lt;/text&gt;
        &lt;text x="675" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;Feb&lt;/text&gt;
        &lt;text x="771" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;Mar&lt;/text&gt;
        &lt;text x="866" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;Apr&lt;/text&gt;
        &lt;text x="962" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;May&lt;/text&gt;
        &lt;text x="1057" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;Jun&lt;/text&gt;
        &lt;text x="1153" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;Jul&lt;/text&gt;
        &lt;text x="1248" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;Aug&lt;/text&gt;
        &lt;text x="1344" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;Sep&lt;/text&gt;
        &lt;text x="1440" y="560" font-family="Segoe UI" font-size="16" fill="#888888" text-anchor="middle"&gt;Oct&lt;/text&gt;

        &lt;!-- Stacked Area Paths --&gt;
        &lt;!-- Area 1 (Top / Dark Blue) --&gt;
        &lt;path d="M 580 446 L 675 425 L 771 413 L 866 398 L 962 380 L 1057 392 L 1153 398 L 1248 398 L 1344 401 L 1440 392 L 1440 410 L 1344 419 L 1248 428 L 1153 428 L 1057 428 L 962 422 L 866 440 L 771 449 L 675 455 L 580 470 Z" fill="#77B1C6" /&gt;
        
        &lt;!-- Area 2 (Middle / Light Blue) --&gt;
        &lt;path d="M 580 470 L 675 455 L 771 449 L 866 440 L 962 422 L 1057 428 L 1153 428 L 1248 428 L 1344 419 L 1440 410 L 1440 488 L 1344 482 L 1248 488 L 1153 494 L 1057 500 L 962 503 L 866 509 L 771 512 L 675 515 L 580 518 Z" fill="#91D0E3" /&gt;
        
        &lt;!-- Area 3 (Bottom / Cyan) --&gt;
        &lt;path d="M 580 518 L 675 515 L 771 512 L 866 509 L 962 503 L 1057 500 L 1153 494 L 1248 488 L 1344 482 L 1440 488 L 1440 530 L 580 530 Z" fill="#A5F0ED" /&gt;

        &lt;!-- Line Borders for Crispness --&gt;
        &lt;polyline points="580 446 675 425 771 413 866 398 962 380 1057 392 1153 398 1248 398 1344 401 1440 392" fill="none" stroke="#488CA9" stroke-width="2" /&gt;
        &lt;polyline points="580 470 675 455 771 449 866 440 962 422 1057 428 1153 428 1248 428 1344 419 1440 410" fill="none" stroke="#5DB0D2" stroke-width="2" /&gt;
        &lt;polyline points="580 518 675 515 771 512 866 509 962 503 1057 500 1153 494 1248 488 1344 482 1440 488" fill="none" stroke="#7CE0D3" stroke-width="2" /&gt;

        &lt;!-- Right Panel Bottom (Yellow Card) --&gt;
        &lt;rect x="500" y="660" width="1000" height="160" rx="24" fill="#F1DA80" /&gt;
        &lt;rect x="540" y="700" width="60" height="60" rx="16" fill="#08778C" /&gt;
        &lt;!-- Globe Icon --&gt;
        &lt;circle cx="570" cy="730" r="14" fill="none" stroke="#FFFFFF" stroke-width="2"/&gt;
        &lt;ellipse cx="570" cy="730" rx="6" ry="14" fill="none" stroke="#FFFFFF" stroke-width="2"/&gt;
        &lt;line x1="556" y1="730" x2="584" y2="730" stroke="#FFFFFF" stroke-width="2"/&gt;

        &lt;text x="620" y="725" font-family="Segoe UI" font-size="24" fill="#333333"&gt;Women in&lt;/text&gt;
        &lt;text x="620" y="755" font-family="Segoe UI" font-size="24" fill="#333333"&gt;Leadership&lt;/text&gt;

        &lt;!-- 10 Women Icons --&gt;
        &lt;g transform="translate(730, 700) scale(1.6)"&gt;
            &lt;!-- 5 Filled --&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#068D9D" transform="translate(0, 0)"/&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#068D9D" transform="translate(24, 0)"/&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#068D9D" transform="translate(48, 0)"/&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#068D9D" transform="translate(72, 0)"/&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#068D9D" transform="translate(96, 0)"/&gt;
            &lt;!-- 5 Outline/White --&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#FFFFFF" transform="translate(120, 0)"/&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#FFFFFF" transform="translate(144, 0)"/&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#FFFFFF" transform="translate(168, 0)"/&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#FFFFFF" transform="translate(192, 0)"/&gt;
            &lt;path d="M 12 10 C 12 10 7 12 5 18 L 8 18 L 8 28 L 11 28 L 11 20 L 13 20 L 13 28 L 16 28 L 16 18 L 19 18 C 17 12 12 10 12 10 Z M 12 8 A 4 4 0 1 0 12 0 A 4 4 0 1 0 12 8 Z" fill="#FFFFFF" transform="translate(216, 0)"/&gt;
        &lt;/g&gt;

        &lt;text x="1270" y="750" font-family="Segoe UI" font-size="64" font-weight="bold" fill="#068D9D"&gt;50%&lt;/text&gt;
        &lt;text x="1395" y="745" font-family="Segoe UI" font-size="20" fill="#6B7853"&gt;(+5%)&lt;/text&gt;
&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_radar_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for radar.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <polygon points="0,0 450,0 450,900 0,900" fill="#F4F4F4"/>
    <textbox x="50" y="60" width="350" height="150" font="Segoe UI" size="46" color="#111111" bold="true" align="left" vertical_align="top" single_line="false" max_lines="3" reflow_on_resize="true">{title}</textbox>
    <textbox x="50" y="220" width="350" height="150" font="Segoe UI" size="24" color="#333333" align="left" vertical_align="top" single_line="false" max_lines="5" reflow_on_resize="true" line_spacing="1.3">{subtitle}</textbox>
    <textbox x="50" y="650" width="350" height="200" font="Segoe UI" size="18" color="#444444" align="left" vertical_align="top" single_line="false" max_lines="8" reflow_on_resize="true" line_spacing="1.3">Đoạn văn giải thích nguồn dữ liệu, nêu bật những gì biểu đồ minh họa và cung cấp hướng dẫn.</textbox>
    <svg x="450" y="0" width="1150" height="900" pixel_width="1150" pixel_height="900">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1150&quot; height=&quot;900&quot; viewBox=&quot;0 0 1150 900&quot;&gt;&lt;circle cx=&quot;305.0&quot; cy=&quot;120&quot; r=&quot;12&quot; fill=&quot;#4A4A4A&quot;/&gt;&lt;text x=&quot;330.0&quot; y=&quot;127&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;22&quot; fill=&quot;#222222&quot;&gt;Người mới&lt;/text&gt;&lt;circle cx=&quot;485.0&quot; cy=&quot;120&quot; r=&quot;12&quot; fill=&quot;#9B9B9B&quot;/&gt;&lt;text x=&quot;510.0&quot; y=&quot;127&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;22&quot; fill=&quot;#222222&quot;&gt;Bậc trung&lt;/text&gt;&lt;circle cx=&quot;665.0&quot; cy=&quot;120&quot; r=&quot;12&quot; fill=&quot;#D8D8D8&quot;/&gt;&lt;text x=&quot;690.0&quot; y=&quot;127&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;22&quot; fill=&quot;#222222&quot;&gt;Quản lý&lt;/text&gt;&lt;polygon points=&quot;575.0,444.0 628.2591649125286,482.69504831500296 607.9159741283785,545.304951684997 542.0840258716215,545.304951684997 521.7408350874714,482.69504831500296&quot; fill=&quot;none&quot; stroke=&quot;#B0B0B0&quot; stroke-dasharray=&quot;4 4&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;575&quot; y=&quot;436.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#555555&quot; text-anchor=&quot;middle&quot;&gt;2&lt;/text&gt;&lt;polygon points=&quot;575.0,388.0 681.5183298250572,465.39009663000587 640.831948256757,590.6099033699941 509.16805174324304,590.6099033699941 468.4816701749428,465.3900966300059&quot; fill=&quot;none&quot; stroke=&quot;#B0B0B0&quot; stroke-dasharray=&quot;4 4&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;575&quot; y=&quot;380.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#555555&quot; text-anchor=&quot;middle&quot;&gt;4&lt;/text&gt;&lt;polygon points=&quot;575.0,332.0 734.7774947375858,448.08514494500884 673.7479223851354,635.9148550549912 476.25207761486456,635.9148550549912 415.2225052624142,448.08514494500884&quot; fill=&quot;none&quot; stroke=&quot;#B0B0B0&quot; stroke-dasharray=&quot;4 4&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;575&quot; y=&quot;324.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#555555&quot; text-anchor=&quot;middle&quot;&gt;6&lt;/text&gt;&lt;polygon points=&quot;575.0,276.0 788.0366596501144,430.7801932600118 706.6638965135139,681.2198067399883 443.3361034864861,681.2198067399883 361.9633403498856,430.7801932600118&quot; fill=&quot;none&quot; stroke=&quot;#B0B0B0&quot; stroke-dasharray=&quot;4 4&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;575&quot; y=&quot;268.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#555555&quot; text-anchor=&quot;middle&quot;&gt;8&lt;/text&gt;&lt;line x1=&quot;575&quot; y1=&quot;500&quot; x2=&quot;575.0&quot; y2=&quot;220.0&quot; stroke=&quot;#D0D0D0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;575.0&quot; y=&quot;175.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#111111&quot; text-anchor=&quot;middle&quot; dominant-baseline=&quot;middle&quot;&gt;Xây dựng thương hiệu&lt;/text&gt;&lt;line x1=&quot;575&quot; y1=&quot;500&quot; x2=&quot;841.295824562643&quot; y2=&quot;413.4752415750147&quot; stroke=&quot;#D0D0D0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;884.0933677959249&quot; y=&quot;399.5694768281421&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#111111&quot; text-anchor=&quot;start&quot; dominant-baseline=&quot;middle&quot;&gt;Khai phá dữ liệu&lt;/text&gt;&lt;line x1=&quot;575&quot; y1=&quot;500&quot; x2=&quot;739.5798706418925&quot; y2=&quot;726.5247584249853&quot; stroke=&quot;#D0D0D0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;766.0302069950537&quot; y=&quot;762.9305231718579&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#111111&quot; text-anchor=&quot;start&quot; dominant-baseline=&quot;middle&quot;&gt;Chuẩn đối sánh&lt;/text&gt;&lt;line x1=&quot;575&quot; y1=&quot;500&quot; x2=&quot;410.42012935810754&quot; y2=&quot;726.5247584249853&quot; stroke=&quot;#D0D0D0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;383.96979300494627&quot; y=&quot;762.9305231718579&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#111111&quot; text-anchor=&quot;end&quot; dominant-baseline=&quot;middle&quot;&gt;Sơ đồ hóa lộ trình&lt;/text&gt;&lt;line x1=&quot;575&quot; y1=&quot;500&quot; x2=&quot;308.704175437357&quot; y2=&quot;413.47524157501476&quot; stroke=&quot;#D0D0D0&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;265.9066322040751&quot; y=&quot;399.5694768281421&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; fill=&quot;#111111&quot; text-anchor=&quot;end&quot; dominant-baseline=&quot;middle&quot;&gt;Copywriting&lt;/text&gt;&lt;polygon points=&quot;575.0,220.0 841.295824562643,413.4752415750147 739.5798706418925,726.5247584249853 410.42012935810754,726.5247584249853 308.704175437357,413.47524157501476&quot; fill=&quot;none&quot; stroke=&quot;#B0B0B0&quot; stroke-dasharray=&quot;4 4&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;575&quot; y=&quot;212.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#555555&quot; text-anchor=&quot;middle&quot;&gt;10&lt;/text&gt;&lt;text x=&quot;{{cx}}&quot; y=&quot;{{cy - 8}}&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;16&quot; fill=&quot;#555555&quot; text-anchor=&quot;middle&quot;&gt;0&lt;/text&gt;&lt;polygon points=&quot;575.0,360.0 681.5183298250572,465.39009663000587 624.3739611925678,567.9574275274956 509.16805174324304,590.6099033699941 495.1112526312071,474.04257247250445&quot; fill=&quot;#4A4A4A&quot; opacity=&quot;0.6&quot; stroke=&quot;#4A4A4A&quot; stroke-width=&quot;2&quot;/&gt;&lt;polygon points=&quot;575.0,304.0 788.0366596501144,430.7801932600118 673.7479223851354,635.9148550549912 426.8781164222968,703.8722825824867 441.8520877186785,456.73762078750735&quot; fill=&quot;#9B9B9B&quot; opacity=&quot;0.6&quot; stroke=&quot;#9B9B9B&quot; stroke-width=&quot;2&quot;/&gt;&lt;polygon points=&quot;575.0,248.0 841.295824562643,413.4752415750147 706.6638965135139,681.2198067399883 410.42012935810754,726.5247584249853 361.9633403498856,430.7801932600118&quot; fill=&quot;#D8D8D8&quot; opacity=&quot;0.6&quot; stroke=&quot;#D8D8D8&quot; stroke-width=&quot;2&quot;/&gt;&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_stacked_bar_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for stacked bar.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FAF7F0">
    <svg x="0" y="0" width="1600" height="900" pixel_width="1600" pixel_height="900">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1600&quot; height=&quot;900&quot; viewBox=&quot;0 0 1600 900&quot;&gt;&lt;path d=&quot;M0,0 L350,0 C350,150 200,250 0,250 Z&quot; fill=&quot;#A47754&quot; opacity=&quot;0.8&quot;/&gt;&lt;path d=&quot;M0,0 L200,0 C200,100 120,150 0,150 Z&quot; fill=&quot;#4D3B2E&quot; opacity=&quot;0.9&quot;/&gt;&lt;circle cx=&quot;230&quot; cy=&quot;50&quot; r=&quot;15&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;circle cx=&quot;280&quot; cy=&quot;110&quot; r=&quot;22&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;path d=&quot;M1250,0 L1600,0 L1600,250 C1450,200 1350,100 1250,0 Z&quot; fill=&quot;#4D3B2E&quot; opacity=&quot;0.9&quot;/&gt;&lt;path d=&quot;M1500,280 C1450,270 1420,300 1450,330 C1480,360 1550,370 1600,350 L1600,280 Z&quot; fill=&quot;#A47754&quot; opacity=&quot;0.8&quot;/&gt;&lt;path d=&quot;M0,900 L250,900 C250,820 180,750 0,720 Z&quot; fill=&quot;#4D3B2E&quot; opacity=&quot;0.9&quot;/&gt;&lt;path d=&quot;M0,650 C80,650 120,700 80,750 C40,800 100,850 150,900 L0,900 Z&quot; fill=&quot;#A47754&quot; opacity=&quot;0.8&quot;/&gt;&lt;path d=&quot;M1600,900 L1150,900 C1250,800 1400,700 1600,600 Z&quot; fill=&quot;#A47754&quot; opacity=&quot;0.8&quot;/&gt;&lt;circle cx=&quot;1080&quot; cy=&quot;850&quot; r=&quot;18&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;circle cx=&quot;1180&quot; cy=&quot;780&quot; r=&quot;12&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;circle cx=&quot;1250&quot; cy=&quot;880&quot; r=&quot;25&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;/svg&gt;</svg>
    <textbox x="100" y="80" width="1400" height="160" font="Segoe UI" size="76" color="#4D3B2E" bold="true" align="center" vertical_align="middle" single_line="false" max_lines="2" reflow_on_resize="true">{title}</textbox>
    <textbox x="780" y="320" width="700" height="500" font="Segoe UI" size="26" color="#4D3B2E" align="justify" vertical_align="top" single_line="false" max_lines="20" reflow_on_resize="true" line_spacing="1.4">{subtitle}</textbox>
    <svg x="200" y="350" width="600" height="550" pixel_width="600" pixel_height="550">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;600&quot; height=&quot;550&quot; viewBox=&quot;0 0 600 550&quot;&gt;&lt;circle cx=&quot;50&quot; cy=&quot;20&quot; r=&quot;8&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;text x=&quot;65&quot; y=&quot;25&quot; font-family=&quot;Arial&quot; font-size=&quot;16&quot; fill=&quot;#4D3B2E&quot;&gt;Seri 1&lt;/text&gt;&lt;circle cx=&quot;170&quot; cy=&quot;20&quot; r=&quot;8&quot; fill=&quot;#A47754&quot;/&gt;&lt;text x=&quot;185&quot; y=&quot;25&quot; font-family=&quot;Arial&quot; font-size=&quot;16&quot; fill=&quot;#4D3B2E&quot;&gt;Seri 2&lt;/text&gt;&lt;circle cx=&quot;290&quot; cy=&quot;20&quot; r=&quot;8&quot; fill=&quot;#EBE2D0&quot;/&gt;&lt;text x=&quot;305&quot; y=&quot;25&quot; font-family=&quot;Arial&quot; font-size=&quot;16&quot; fill=&quot;#4D3B2E&quot;&gt;Seri 3&lt;/text&gt;&lt;line x1=&quot;70&quot; y1=&quot;420.0&quot; x2=&quot;520&quot; y2=&quot;420.0&quot; stroke=&quot;#E0DCD3&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;60&quot; y=&quot;425.0&quot; font-family=&quot;Arial&quot; font-size=&quot;14&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;end&quot;&gt;0%&lt;/text&gt;&lt;line x1=&quot;70&quot; y1=&quot;350.0&quot; x2=&quot;520&quot; y2=&quot;350.0&quot; stroke=&quot;#E0DCD3&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;60&quot; y=&quot;355.0&quot; font-family=&quot;Arial&quot; font-size=&quot;14&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;end&quot;&gt;20%&lt;/text&gt;&lt;line x1=&quot;70&quot; y1=&quot;280.0&quot; x2=&quot;520&quot; y2=&quot;280.0&quot; stroke=&quot;#E0DCD3&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;60&quot; y=&quot;285.0&quot; font-family=&quot;Arial&quot; font-size=&quot;14&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;end&quot;&gt;40%&lt;/text&gt;&lt;line x1=&quot;70&quot; y1=&quot;210.0&quot; x2=&quot;520&quot; y2=&quot;210.0&quot; stroke=&quot;#E0DCD3&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;60&quot; y=&quot;215.0&quot; font-family=&quot;Arial&quot; font-size=&quot;14&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;end&quot;&gt;60%&lt;/text&gt;&lt;line x1=&quot;70&quot; y1=&quot;140.0&quot; x2=&quot;520&quot; y2=&quot;140.0&quot; stroke=&quot;#E0DCD3&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;60&quot; y=&quot;145.0&quot; font-family=&quot;Arial&quot; font-size=&quot;14&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;end&quot;&gt;80%&lt;/text&gt;&lt;line x1=&quot;70&quot; y1=&quot;70.0&quot; x2=&quot;520&quot; y2=&quot;70.0&quot; stroke=&quot;#E0DCD3&quot; stroke-width=&quot;1&quot;/&gt;&lt;text x=&quot;60&quot; y=&quot;75.0&quot; font-family=&quot;Arial&quot; font-size=&quot;14&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;end&quot;&gt;100%&lt;/text&gt;&lt;rect x=&quot;92.5&quot; y=&quot;280.0&quot; width=&quot;67.5&quot; height=&quot;140.0&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;rect x=&quot;92.5&quot; y=&quot;140.0&quot; width=&quot;67.5&quot; height=&quot;140.0&quot; fill=&quot;#A47754&quot;/&gt;&lt;rect x=&quot;92.5&quot; y=&quot;70.0&quot; width=&quot;67.5&quot; height=&quot;70.0&quot; fill=&quot;#EBE2D0&quot;/&gt;&lt;text x=&quot;126.25&quot; y=&quot;445&quot; font-family=&quot;Arial&quot; font-size=&quot;16&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;middle&quot;&gt;Item 1&lt;/text&gt;&lt;rect x=&quot;205.0&quot; y=&quot;280.0&quot; width=&quot;67.5&quot; height=&quot;140.0&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;rect x=&quot;205.0&quot; y=&quot;164.5&quot; width=&quot;67.5&quot; height=&quot;115.5&quot; fill=&quot;#A47754&quot;/&gt;&lt;rect x=&quot;205.0&quot; y=&quot;70.0&quot; width=&quot;67.5&quot; height=&quot;94.5&quot; fill=&quot;#EBE2D0&quot;/&gt;&lt;text x=&quot;238.75&quot; y=&quot;445&quot; font-family=&quot;Arial&quot; font-size=&quot;16&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;middle&quot;&gt;Item 2&lt;/text&gt;&lt;rect x=&quot;317.5&quot; y=&quot;262.5&quot; width=&quot;67.5&quot; height=&quot;157.5&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;rect x=&quot;317.5&quot; y=&quot;168.0&quot; width=&quot;67.5&quot; height=&quot;94.5&quot; fill=&quot;#A47754&quot;/&gt;&lt;rect x=&quot;317.5&quot; y=&quot;69.99999999999999&quot; width=&quot;67.5&quot; height=&quot;98.00000000000001&quot; fill=&quot;#EBE2D0&quot;/&gt;&lt;text x=&quot;351.25&quot; y=&quot;445&quot; font-family=&quot;Arial&quot; font-size=&quot;16&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;middle&quot;&gt;Item 3&lt;/text&gt;&lt;rect x=&quot;430.0&quot; y=&quot;280.0&quot; width=&quot;67.5&quot; height=&quot;140.0&quot; fill=&quot;#4D3B2E&quot;/&gt;&lt;rect x=&quot;430.0&quot; y=&quot;112.0&quot; width=&quot;67.5&quot; height=&quot;168.0&quot; fill=&quot;#A47754&quot;/&gt;&lt;rect x=&quot;430.0&quot; y=&quot;70.0&quot; width=&quot;67.5&quot; height=&quot;42.0&quot; fill=&quot;#EBE2D0&quot;/&gt;&lt;text x=&quot;463.75&quot; y=&quot;445&quot; font-family=&quot;Arial&quot; font-size=&quot;16&quot; fill=&quot;#4D3B2E&quot; text-anchor=&quot;middle&quot;&gt;Item 4&lt;/text&gt;&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_waterfall_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for waterfall.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <svg x="0" y="0" width="1600" height="900" pixel_width="1600" pixel_height="900">&lt;svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900"&gt;
    &lt;!-- Title --&gt;
    &lt;text x="800" y="140" font-family="Segoe UI" font-size="64" fill="#222222" font-weight="300" text-anchor="middle"&gt;Waterfall Diagram&lt;/text&gt;

    &lt;!-- Legend --&gt;
    &lt;rect x="420" y="180" width="12" height="12" fill="#008080" /&gt;
    &lt;text x="440" y="191" font-family="Segoe UI" font-size="16" fill="#666666"&gt;Increase&lt;/text&gt;
    
    &lt;rect x="520" y="180" width="12" height="12" fill="#2C3E50" /&gt;
    &lt;text x="540" y="191" font-family="Segoe UI" font-size="16" fill="#666666"&gt;Decrease&lt;/text&gt;
    
    &lt;rect x="620" y="180" width="12" height="12" fill="#FFA577" /&gt;
    &lt;text x="640" y="191" font-family="Segoe UI" font-size="16" fill="#666666"&gt;Total&lt;/text&gt;

    &lt;!-- Chart Y-Axis and Grid Lines --&gt;
    &lt;!-- 180 --&gt;
    &lt;line x1="160" y1="210" x2="880" y2="210" stroke="#EAEAEA" stroke-width="2"/&gt;
    &lt;text x="140" y="215" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;180&lt;/text&gt;
    &lt;!-- 160 --&gt;
    &lt;line x1="160" y1="270" x2="880" y2="270" stroke="#EAEAEA" stroke-width="2"/&gt;
    &lt;text x="140" y="275" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;160&lt;/text&gt;
    &lt;!-- 140 --&gt;
    &lt;line x1="160" y1="330" x2="880" y2="330" stroke="#EAEAEA" stroke-width="2"/&gt;
    &lt;text x="140" y="335" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;140&lt;/text&gt;
    &lt;!-- 120 --&gt;
    &lt;line x1="160" y1="390" x2="880" y2="390" stroke="#EAEAEA" stroke-width="2"/&gt;
    &lt;text x="140" y="395" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;120&lt;/text&gt;
    &lt;!-- 100 --&gt;
    &lt;line x1="160" y1="450" x2="880" y2="450" stroke="#EAEAEA" stroke-width="2"/&gt;
    &lt;text x="140" y="455" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;100&lt;/text&gt;
    &lt;!-- 80 --&gt;
    &lt;line x1="160" y1="510" x2="880" y2="510" stroke="#EAEAEA" stroke-width="2"/&gt;
    &lt;text x="140" y="515" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;80&lt;/text&gt;
    &lt;!-- 60 --&gt;
    &lt;line x1="160" y1="570" x2="880" y2="570" stroke="#EAEAEA" stroke-width="2"/&gt;
    &lt;text x="140" y="575" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;60&lt;/text&gt;
    &lt;!-- 40 --&gt;
    &lt;line x1="160" y1="630" x2="880" y2="630" stroke="#EAEAEA" stroke-width="2"/&gt;
    &lt;text x="140" y="635" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;40&lt;/text&gt;
    &lt;!-- 20 --&gt;
    &lt;line x1="160" y1="690" x2="880" y2="690" stroke="#EAEAEA" stroke-width="2"/&gt;
    &lt;text x="140" y="695" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;20&lt;/text&gt;
    &lt;!-- 0 --&gt;
    &lt;line x1="160" y1="750" x2="880" y2="750" stroke="#CCCCCC" stroke-width="2"/&gt;
    &lt;text x="140" y="755" font-family="Segoe UI" font-size="14" fill="#888888" text-anchor="end"&gt;0&lt;/text&gt;

    &lt;!-- X-Axis Labels --&gt;
    &lt;text x="210" y="775" font-family="Segoe UI" font-size="14" fill="#666666" text-anchor="middle"&gt;Category 1&lt;/text&gt;
    &lt;text x="295" y="775" font-family="Segoe UI" font-size="14" fill="#666666" text-anchor="middle"&gt;Category 2&lt;/text&gt;
    &lt;text x="380" y="775" font-family="Segoe UI" font-size="14" fill="#666666" text-anchor="middle"&gt;Category 3&lt;/text&gt;
    &lt;text x="465" y="775" font-family="Segoe UI" font-size="14" fill="#666666" text-anchor="middle"&gt;Category 4&lt;/text&gt;
    &lt;text x="550" y="775" font-family="Segoe UI" font-size="14" fill="#666666" text-anchor="middle"&gt;Category 5&lt;/text&gt;
    &lt;text x="635" y="775" font-family="Segoe UI" font-size="14" fill="#666666" text-anchor="middle"&gt;Category 6&lt;/text&gt;
    &lt;text x="720" y="775" font-family="Segoe UI" font-size="14" fill="#666666" text-anchor="middle"&gt;Category 7&lt;/text&gt;
    &lt;text x="805" y="775" font-family="Segoe UI" font-size="14" fill="#666666" text-anchor="middle"&gt;Category 8&lt;/text&gt;

    &lt;!-- Columns and Connectors --&gt;
    &lt;!-- Cat 1 (100) --&gt;
    &lt;rect x="185" y="450" width="50" height="300" fill="#FFA577" /&gt;
    &lt;text x="210" y="440" font-family="Segoe UI" font-size="16" fill="#666666" text-anchor="middle"&gt;100&lt;/text&gt;
    &lt;line x1="235" y1="450" x2="270" y2="450" stroke="#AAAAAA" stroke-width="1"/&gt;

    &lt;!-- Cat 2 (+20 -&gt; 120) --&gt;
    &lt;rect x="270" y="390" width="50" height="60" fill="#008080" /&gt;
    &lt;text x="295" y="380" font-family="Segoe UI" font-size="16" fill="#666666" text-anchor="middle"&gt;20&lt;/text&gt;
    &lt;line x1="320" y1="390" x2="355" y2="390" stroke="#AAAAAA" stroke-width="1"/&gt;

    &lt;!-- Cat 3 (+50 -&gt; 170) --&gt;
    &lt;rect x="355" y="240" width="50" height="150" fill="#008080" /&gt;
    &lt;text x="380" y="230" font-family="Segoe UI" font-size="16" fill="#666666" text-anchor="middle"&gt;50&lt;/text&gt;
    &lt;line x1="405" y1="240" x2="440" y2="240" stroke="#AAAAAA" stroke-width="1"/&gt;

    &lt;!-- Cat 4 (-40 -&gt; 130) --&gt;
    &lt;rect x="440" y="240" width="50" height="120" fill="#2C3E50" /&gt;
    &lt;text x="465" y="380" font-family="Segoe UI" font-size="16" fill="#666666" text-anchor="middle"&gt;-40&lt;/text&gt;
    &lt;line x1="490" y1="360" x2="525" y2="360" stroke="#AAAAAA" stroke-width="1"/&gt;

    &lt;!-- Cat 5 (Total = 130) --&gt;
    &lt;rect x="525" y="360" width="50" height="390" fill="#FFA577" /&gt;
    &lt;text x="550" y="350" font-family="Segoe UI" font-size="16" fill="#666666" text-anchor="middle"&gt;130&lt;/text&gt;
    &lt;line x1="575" y1="360" x2="610" y2="360" stroke="#AAAAAA" stroke-width="1"/&gt;

    &lt;!-- Cat 6 (-60 -&gt; 70) --&gt;
    &lt;rect x="610" y="360" width="50" height="180" fill="#2C3E50" /&gt;
    &lt;text x="635" y="560" font-family="Segoe UI" font-size="16" fill="#666666" text-anchor="middle"&gt;-60&lt;/text&gt;
    &lt;line x1="660" y1="540" x2="695" y2="540" stroke="#AAAAAA" stroke-width="1"/&gt;

    &lt;!-- Cat 7 (+70 -&gt; 140) --&gt;
    &lt;rect x="695" y="330" width="50" height="210" fill="#008080" /&gt;
    &lt;text x="720" y="320" font-family="Segoe UI" font-size="16" fill="#666666" text-anchor="middle"&gt;70&lt;/text&gt;
    &lt;line x1="745" y1="330" x2="780" y2="330" stroke="#AAAAAA" stroke-width="1"/&gt;

    &lt;!-- Cat 8 (Total = 140) --&gt;
    &lt;rect x="780" y="330" width="50" height="420" fill="#FFA577" /&gt;
    &lt;text x="805" y="320" font-family="Segoe UI" font-size="16" fill="#666666" text-anchor="middle"&gt;140&lt;/text&gt;

    &lt;!-- Right Side Text Blocks --&gt;
    &lt;!-- Block 1 --&gt;
    &lt;rect x="950" y="280" width="80" height="80" fill="#008080" /&gt;
    &lt;!-- Mini Icon --&gt;
    &lt;polyline points="970,335 970,325 980,325 980,335" fill="none" stroke="#FFFFFF" stroke-width="3"/&gt;
    &lt;polyline points="985,335 985,310 995,310 995,335" fill="none" stroke="#FFFFFF" stroke-width="3"/&gt;
    &lt;polyline points="1000,335 1000,295 1010,295 1010,335" fill="none" stroke="#FFFFFF" stroke-width="3"/&gt;

    &lt;text x="1050" y="310" font-family="Segoe UI" font-size="20" fill="#666666"&gt;
        &lt;tspan x="1050" dy="0"&gt;Lorem ipsum dolor sit amet, consectetur&lt;/tspan&gt;
        &lt;tspan x="1050" dy="25"&gt;adipiscing elit. Ut pulvinar, lectus ut sodales&lt;/tspan&gt;
        &lt;tspan x="1050" dy="25"&gt;maximus, quam dolor vestibulum justo.&lt;/tspan&gt;
    &lt;/text&gt;
    &lt;line x1="1050" y1="390" x2="1500" y2="390" stroke="#CCCCCC" stroke-width="2"/&gt;

    &lt;!-- Block 2 --&gt;
    &lt;rect x="950" y="450" width="80" height="80" fill="#2C3E50" /&gt;
    &lt;polyline points="970,490 980,500 995,475" fill="none" stroke="#FFFFFF" stroke-width="3"/&gt;
    &lt;line x1="970" y1="510" x2="1010" y2="510" stroke="#FFFFFF" stroke-width="3"/&gt;
    
    &lt;text x="1050" y="480" font-family="Segoe UI" font-size="20" fill="#666666"&gt;
        &lt;tspan x="1050" dy="0"&gt;Lorem ipsum dolor sit amet, consectetur&lt;/tspan&gt;
        &lt;tspan x="1050" dy="25"&gt;adipiscing elit. Ut pulvinar, lectus ut sodales&lt;/tspan&gt;
        &lt;tspan x="1050" dy="25"&gt;maximus, quam dolor vestibulum justo.&lt;/tspan&gt;
    &lt;/text&gt;
    &lt;line x1="1050" y1="560" x2="1500" y2="560" stroke="#CCCCCC" stroke-width="2"/&gt;

    &lt;!-- Block 3 --&gt;
    &lt;rect x="950" y="620" width="80" height="80" fill="#FFA577" /&gt;
    &lt;circle cx="990" cy="660" r="15" fill="none" stroke="#FFFFFF" stroke-width="3"/&gt;
    &lt;line x1="990" y1="650" x2="990" y2="670" stroke="#FFFFFF" stroke-width="3"/&gt;
    
    &lt;text x="1050" y="650" font-family="Segoe UI" font-size="20" fill="#666666"&gt;
        &lt;tspan x="1050" dy="0"&gt;Lorem ipsum dolor sit amet, consectetur&lt;/tspan&gt;
        &lt;tspan x="1050" dy="25"&gt;adipiscing elit. Ut pulvinar, lectus ut sodales&lt;/tspan&gt;
        &lt;tspan x="1050" dy="25"&gt;maximus, quam dolor vestibulum justo.&lt;/tspan&gt;
    &lt;/text&gt;
    &lt;line x1="1050" y1="730" x2="1500" y2="730" stroke="#CCCCCC" stroke-width="2"/&gt;

    &lt;!-- Footer --&gt;
    &lt;text x="120" y="860" font-family="Segoe UI" font-size="16" fill="#AAAAAA"&gt;7/10/2018&lt;/text&gt;
    &lt;text x="1450" y="860" font-family="Segoe UI" font-size="16" fill="#AAAAAA"&gt;2&lt;/text&gt;

    &lt;!-- Bottom Color Bars --&gt;
    &lt;rect x="120" y="880" width="440" height="20" fill="#008080" /&gt;
    &lt;rect x="570" y="880" width="440" height="20" fill="#2C3E50" /&gt;
    &lt;rect x="1020" y="880" width="460" height="20" fill="#FFA577" /&gt;

&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)

def generate_ai_content_slide_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for ai content slide.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#E3EAED">
    <image src="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=85&amp;w=1400&amp;auto=format&amp;fit=crop" x="860" y="30" width="700" height="820"/>
    <textbox x="120" y="76.0" width="690" height="328.15999999999997" font="Arial" size="62.0" min_font_size="62.0" bold="true" color="#101010" align="left" vertical_align="top" single_line="false" max_lines="3" overflow="clip" line_spacing="0.92" safety_ratio="1.0" margin_left="0" margin_right="0" margin_top="0" margin_bottom="0">THE SLIDE
TITLE GOES
HERE!</textbox>
    <textbox x="120" y="418.15999999999997" width="690" height="94.2" font="Arial" size="22.0" min_font_size="22.0" color="#1B1B1B" align="left" vertical_align="top" single_line="false" max_lines="2" overflow="clip" line_spacing="1.05" safety_ratio="1.0" margin_left="0" margin_right="0" margin_top="0" margin_bottom="0">Do you know what helps you make your
point clear? Lists like this one:</textbox>
    <textbox x="120" y="526.36" width="690" height="142.07999999999998" font="Arial" size="22.0" min_font_size="22.0" color="#1B1B1B" align="left" vertical_align="top" single_line="false" max_lines="3" overflow="clip" line_spacing="1.08" safety_ratio="1.0" margin_left="0" margin_right="0" margin_top="0" margin_bottom="0">• They’re simple
• You can organize your ideas clearly
• You’ll never forget to buy milk!</textbox>
    <textbox x="120" y="682.44" width="690" height="138.3" font="Arial" size="22.0" min_font_size="22.0" color="#1B1B1B" align="left" vertical_align="top" single_line="false" max_lines="3" overflow="clip" line_spacing="1.05" safety_ratio="1.0" margin_left="0" margin_right="0" margin_top="0" margin_bottom="0">You can replace the image. Just
right-click on it and select “Replace
image”</textbox>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_key_advantages_slide_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for key advantages slide.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="810" height="455" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#D4DCE0">
    <shape type="ellipse" x="30" y="20" width="58" height="58" fill="none" line_color="#EEF1F2" line_width="18"/>
    <shape type="ellipse" x="735" y="-36" width="120" height="120" fill="none" line_color="#EEF1F2" line_width="34"/>
    <shape type="ellipse" x="31" y="280" width="115" height="115" fill="none" line_color="#B7C0C5" line_width="26"/>
    <textbox x="82" y="170" width="660" height="100" font="Georgia" size="58" color="#6E7A7F" single_line="true" min_font_size="42" overflow="shrink" safety_ratio="0.96">{title}</textbox>
    <shape type="circle" x="69" y="57" width="90" height="90" fill="#EAB0A8" line_color="none"/>
    <textbox x="94" y="76" width="50" height="45" font="Arial" size="30" color="#64747A" align="center" vertical_align="middle" single_line="true" overflow="shrink">{subtitle}</textbox>
    <textbox x="178" y="65" width="170" height="30" font="Arial" size="16" bold="true" color="#111111" single_line="true" overflow="shrink">Advantage 01</textbox>
    <textbox x="178" y="92" width="250" height="55" font="Arial" size="12" color="#111111" max_lines="3" overflow="shrink" line_spacing="1.15">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut.</textbox>
    <shape type="circle" x="442" y="57" width="90" height="90" fill="#EAB0A8" line_color="none"/>
    <textbox x="462" y="79" width="50" height="45" font="Arial" size="30" color="#64747A" align="center" vertical_align="middle" single_line="true" overflow="shrink">♙</textbox>
    <textbox x="556" y="65" width="170" height="30" font="Arial" size="16" bold="true" color="#111111" single_line="true" overflow="shrink">Advantage 02</textbox>
    <textbox x="556" y="92" width="225" height="55" font="Arial" size="12" color="#111111" max_lines="3" overflow="shrink" line_spacing="1.15">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut.</textbox>
    <shape type="circle" x="69" y="316" width="90" height="90" fill="#EAB0A8" line_color="none"/>
    <textbox x="92" y="336" width="50" height="45" font="Arial" size="30" color="#64747A" align="center" vertical_align="middle" single_line="true" overflow="shrink">✎</textbox>
    <textbox x="178" y="326" width="170" height="30" font="Arial" size="16" bold="true" color="#111111" single_line="true" overflow="shrink">Advantage 03</textbox>
    <textbox x="178" y="353" width="250" height="55" font="Arial" size="12" color="#111111" max_lines="3" overflow="shrink" line_spacing="1.15">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut.</textbox>
    <shape type="circle" x="442" y="316" width="90" height="90" fill="#EAB0A8" line_color="none"/>
    <textbox x="462" y="337" width="50" height="45" font="Arial" size="30" color="#64747A" align="center" vertical_align="middle" single_line="true" overflow="shrink">◉</textbox>
    <textbox x="556" y="326" width="170" height="30" font="Arial" size="16" bold="true" color="#111111" single_line="true" overflow="shrink">Advantage 04</textbox>
    <textbox x="556" y="353" width="225" height="55" font="Arial" size="12" color="#111111" max_lines="3" overflow="shrink" line_spacing="1.15">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut.</textbox>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)


def generate_simple_donut_slide_xml(title: str = "Default Title", subtitle: str = "Default Subtitle", items: list = None) -> str:
    """
    Generate an XML slide for simple donut.
    """
    if items is None:
        items = []
    
    # Template
    xml_template = r"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <polygon points="10,10 1590,10 1590,890 10,890" fill="#FFFFFF"/>
    <svg x="10" y="10" width="1580" height="880" pixel_width="1580" pixel_height="880">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1580&quot; height=&quot;880&quot; viewBox=&quot;0 0 1580 880&quot;&gt;&lt;rect x=&quot;0&quot; y=&quot;0&quot; width=&quot;1580&quot; height=&quot;880&quot; rx=&quot;15&quot; fill=&quot;#FAFAFA&quot; stroke=&quot;#EAEAEA&quot; stroke-width=&quot;2&quot;/&gt;&lt;/svg&gt;</svg>
    <textbox x="100" y="120" width="500" height="80" font="Segoe UI" size="50" color="#2A82BD" bold="true" align="left" vertical_align="top" single_line="false" max_lines="2" reflow_on_resize="true">{title}</textbox>
    <textbox x="100" y="200" width="500" height="50" font="Segoe UI" size="30" color="#333333" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <polygon points="100,400 125,400 125,425 100,425" fill="#6A73A9"/>
    <textbox x="145" y="392" width="400" height="40" font="Segoe UI" size="24" color="#1F4D70" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">ORGANIC</textbox>
    <polygon points="100,480 125,480 125,505 100,505" fill="#6C93CD"/>
    <textbox x="145" y="472" width="400" height="40" font="Segoe UI" size="24" color="#1F4D70" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">SEARCH ENGINE</textbox>
    <polygon points="100,560 125,560 125,585 100,585" fill="#6EB1DF"/>
    <textbox x="145" y="552" width="400" height="40" font="Segoe UI" size="24" color="#1F4D70" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">EMAIL MARKETING</textbox>
    <polygon points="100,640 125,640 125,665 100,665" fill="#6CD5DF"/>
    <textbox x="145" y="632" width="400" height="40" font="Segoe UI" size="24" color="#1F4D70" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">SOCIAL MEDIA</textbox>
    <polygon points="100,720 125,720 125,745 100,745" fill="#95E6E6"/>
    <textbox x="145" y="712" width="400" height="40" font="Segoe UI" size="24" color="#1F4D70" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">REFERRAL LINK</textbox>
    <svg x="600" y="100" width="900" height="700" pixel_width="900" pixel_height="700">&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;900&quot; height=&quot;700&quot; viewBox=&quot;0 0 900 700&quot;&gt;&lt;circle cx=&quot;450&quot; cy=&quot;350&quot; r=&quot;240&quot; fill=&quot;transparent&quot; stroke=&quot;#6A73A9&quot; stroke-width=&quot;45&quot; stroke-dasharray=&quot;165.87609210954108 1507.9644737231006&quot; transform=&quot;rotate(-90 450 350)&quot; /&gt;&lt;text x=&quot;550.7745312729742&quot; y=&quot;70.08797123611788&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; font-weight=&quot;bold&quot; fill=&quot;#2A4866&quot; text-anchor=&quot;start&quot; dominant-baseline=&quot;middle&quot;&gt;11%&lt;/text&gt;&lt;circle cx=&quot;450&quot; cy=&quot;350&quot; r=&quot;240&quot; fill=&quot;transparent&quot; stroke=&quot;#6C93CD&quot; stroke-width=&quot;45&quot; stroke-dasharray=&quot;422.2300526424682 1507.9644737231006&quot; transform=&quot;rotate(-50.4 450 350)&quot; /&gt;&lt;text x=&quot;747.5&quot; y=&quot;350.0&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; font-weight=&quot;bold&quot; fill=&quot;#2A4866&quot; text-anchor=&quot;start&quot; dominant-baseline=&quot;middle&quot;&gt;28%&lt;/text&gt;&lt;circle cx=&quot;450&quot; cy=&quot;350&quot; r=&quot;240&quot; fill=&quot;transparent&quot; stroke=&quot;#6EB1DF&quot; stroke-width=&quot;45&quot; stroke-dasharray=&quot;331.75218421908215 1507.9644737231006&quot; transform=&quot;rotate(50.400000000000006 450 350)&quot; /&gt;&lt;text x=&quot;450.0&quot; y=&quot;647.5&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; font-weight=&quot;bold&quot; fill=&quot;#2A4866&quot; text-anchor=&quot;middle&quot; dominant-baseline=&quot;middle&quot;&gt;22%&lt;/text&gt;&lt;circle cx=&quot;450&quot; cy=&quot;350&quot; r=&quot;240&quot; fill=&quot;transparent&quot; stroke=&quot;#6CD5DF&quot; stroke-width=&quot;45&quot; stroke-dasharray=&quot;346.83182895631313 1507.9644737231006&quot; transform=&quot;rotate(129.6 450 350)&quot; /&gt;&lt;text x=&quot;156.16271867294654&quot; y=&quot;396.5392533494687&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; font-weight=&quot;bold&quot; fill=&quot;#2A4866&quot; text-anchor=&quot;end&quot; dominant-baseline=&quot;middle&quot;&gt;23%&lt;/text&gt;&lt;circle cx=&quot;450&quot; cy=&quot;350&quot; r=&quot;240&quot; fill=&quot;transparent&quot; stroke=&quot;#95E6E6&quot; stroke-width=&quot;45&quot; stroke-dasharray=&quot;241.2743157956961 1507.9644737231006&quot; transform=&quot;rotate(212.39999999999998 450 350)&quot; /&gt;&lt;text x=&quot;306.6782819547397&quot; y=&quot;89.29876268695057&quot; font-family=&quot;Segoe UI&quot; font-size=&quot;20&quot; font-weight=&quot;bold&quot; fill=&quot;#2A4866&quot; text-anchor=&quot;end&quot; dominant-baseline=&quot;middle&quot;&gt;16%&lt;/text&gt;&lt;/svg&gt;</svg>
  </slide>
</presentation>
"""
    
    return xml_template.format(title=title, subtitle=subtitle)





