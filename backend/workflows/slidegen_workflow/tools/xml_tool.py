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



def generate_pie_chart_slide_xml(
    title: str = "Budget Pie Chart",
    subtitle: str = "Monthly Budget",
    items: list = None,
    colors: list = None,
    background_color: str = "#FAF7F0",
    title_color: str = "#FFFFFF",
    subtitle_color: str = "#B6AE97",
    header_color: str = "#354F42",
    legend_bg_color: str = "#2F2E2C",
) -> str:
    """
    Generate an XML slide with a pie chart.
    `items` is a list of dicts: [{"label": "Savings", "value": 24.8, "description": "Details..."}, ...]
    """
    import math
    import html as html_mod

    if items is None:
        items = [
            {"label": "Savings", "value": 24.8, "description": "Monthly savings allocation"},
            {"label": "Rent", "value": 35.0, "description": "Housing and rent expenses"},
            {"label": "Food", "value": 20.2, "description": "Groceries and dining"},
            {"label": "Transport", "value": 12.0, "description": "Commuting costs"},
            {"label": "Others", "value": 8.0, "description": "Miscellaneous spending"},
        ]
    if colors is None:
        colors = ["#354F42", "#556B55", "#89947A", "#B6AE97", "#EBE2D0", "#D9C8A9", "#A49987"]

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <polygon points="50,50 1550,50 1550,250 50,250" fill="{header_color}"/>
    <textbox x="50" y="80" width="1500" height="80" font="Segoe UI" size="70" color="{title_color}" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="50" y="170" width="1500" height="50" font="Segoe UI" size="36" color="{subtitle_color}" italic="true" align="center" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <polygon points="50,300 700,300 700,850 50,850" fill="{legend_bg_color}"/>
'''

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

        circle_svg = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="{color}" stroke-width="{stroke_width}" stroke-dasharray="{dash} {circumference}" transform="rotate({current_angle_deg} {cx} {cy})" />'
        svg_elements.append(circle_svg)

        slice_angle = (percentage / 100) * 360
        mid_angle_deg = current_angle_deg + slice_angle / 2
        mid_angle_rad = math.radians(mid_angle_deg)

        lx = cx + label_r * math.cos(mid_angle_rad)
        ly = cy + label_r * math.sin(mid_angle_rad)

        text_anchor = "start" if math.cos(mid_angle_rad) >= 0 else "end"
        pct_color = legend_bg_color
        text_svg = f'<text x="{lx}" y="{ly}" font-family="Segoe UI" font-size="22" font-weight="bold" fill="{pct_color}" text-anchor="{text_anchor}" dominant-baseline="middle">{percentage:.1f}%</text>'
        svg_elements.append(text_svg)

        current_angle_deg += slice_angle

    svg_content = "".join(svg_elements)

    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="550" viewBox="0 0 800 550">{svg_content}</svg>')

    xml += f'''
    <svg x="750" y="300" width="800" height="550" pixel_width="800" pixel_height="550">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_donut_chart_slide_xml(
    title: str = "ELEGANCE CLASSY",
    subtitle: str = "Style Agency Infographics",
    items: list = None,
    colors: list = None,
    background_color: str = "#FCFBF9",
    title_color: str = "#333230",
    subtitle_color: str = "#8C8984",
    accent_color: str = "#9E8470",
    donut_bg_color: str = "#6E7266",
    donut_fg_color: str = "#CDAE9B",
) -> str:
    """
    Generate an XML slide with 3 horizontal donut progress charts.
    `items` is a list of exactly 3 dicts: [{"label": "JUPITER", "description": "...", "value": 75}, ...]
    """
    import math
    import html as html_mod

    if items is None:
        items = [
            {"label": "JUPITER", "value": 75, "description": "Jupiter is the largest planet in the solar system"},
            {"label": "SATURN", "value": 60, "description": "Saturn is known for its beautiful ring system"},
            {"label": "MARS", "value": 45, "description": "Mars is often called the Red Planet"},
        ]
    if colors is None:
        colors = [donut_fg_color] * 3

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <polygon points="0,0 45,0 45,900 0,900" fill="{accent_color}" line_color="none"/>
    <polygon points="1400,20 1600,20 1600,80 1400,80" fill="#B3B9AE" line_color="none"/>
    <polygon points="1230,840 1600,840 1600,900 1230,900" fill="#7A7E74" line_color="none"/>
    <textbox x="120" y="110" width="1200" height="100" font="Segoe UI" size="76" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true" line_spacing="1.0">{title}</textbox>
    <textbox x="120" y="210" width="1200" height="50" font="Segoe UI" size="30" color="{subtitle_color}" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true" line_spacing="1.0">{subtitle}</textbox>
'''

    cx_list = [350, 800, 1250]
    r = 90
    stroke_width = 60
    circumference = 2 * math.pi * r

    svg_elements = []

    for i, item in enumerate(items[:3]):
        cx = cx_list[i]
        cy = 150
        val = item.get('value', 0)
        percentage = min(max(val, 0), 100)
        dash = (percentage / 100) * circumference
        fg_color = colors[i % len(colors)]

        bg_circle = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{donut_bg_color}" stroke-width="{stroke_width}" />'
        fg_circle = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{fg_color}" stroke-width="{stroke_width}" stroke-dasharray="{dash} {circumference}" />'

        group = f'<g transform="rotate(180 {cx} {cy})">{bg_circle}{fg_circle}</g>'
        svg_elements.append(group)

        text = f'<text x="{cx}" y="{cy+15}" font-family="Arial" font-size="42" font-weight="bold" fill="{title_color}" text-anchor="middle">{int(percentage)}%</text>'
        svg_elements.append(text)

        label = item.get('label', '')
        desc = item.get('description', '')
        tx = cx - 200
        xml += f'''
    <textbox x="{tx}" y="640" width="400" height="40" font="Segoe UI" size="24" color="{title_color}" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{label}</textbox>
    <textbox x="{tx}" y="690" width="400" height="80" font="Segoe UI" size="18" color="{subtitle_color}" align="center" vertical_align="top" single_line="false" max_lines="3" reflow_on_resize="true" line_spacing="1.4">{desc}</textbox>
'''

    svg_content = "".join(svg_elements)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="300" viewBox="0 0 1600 300">{svg_content}</svg>')

    xml += f'''
    <svg x="0" y="320" width="1600" height="300" pixel_width="1600" pixel_height="300">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_bar_chart_slide_xml(
    title: str = "Quarterly Performance",
    subtitle: str = "Performance metrics overview",
    categories: list = None,
    series: list = None,
    colors: list = None,
    background_color: str = "#FFFFFF",
    title_color: str = "#1B2559",
    subtitle_color: str = "#6B7280",
    y_axis_label: str = "Value",
) -> str:
    '''
    Generate an XML slide with a dynamic vertical bar chart.
    '''
    import html as html_mod

    if categories is None:
        categories = ["Q1", "Q2", "Q3", "Q4"]
    if series is None:
        series = [{"name": "Revenue", "data": [45, 52, 68, 58]}]
    if colors is None:
        colors = ["#1B2559", "#FF6B35", "#4B9CD3", "#9CA3AF", "#34D399", "#F59E0B"]

    svg_w, svg_h = 1200, 600
    margin_top, margin_bottom, margin_left, margin_right = 40, 70, 80, 40
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    all_vals = [v for s in series for v in s.get("data", [])]
    val_max = max(all_vals) if all_vals else 100
    val_min = 0
    step = 10 ** (len(str(int(val_max))) - 1) if val_max > 0 else 10
    val_max = ((int(val_max) // step) + 1) * step

    num_cats = len(categories)
    num_series = len(series)
    slot_width = chart_w / max(num_cats, 1)
    bar_width = (slot_width * 0.7) / max(num_series, 1)
    padding = (slot_width * 0.3) / 2

    svg_parts = []
    num_grid = 5
    for i in range(num_grid + 1):
        y_ratio = i / num_grid
        y_pos = svg_h - margin_bottom - (y_ratio * chart_h)
        val_label = val_min + (val_max - val_min) * y_ratio
        svg_parts.append(f'<line x1="{margin_left}" y1="{y_pos:.1f}" x2="{svg_w - margin_right}" y2="{y_pos:.1f}" stroke="#E5E7EB" stroke-width="1"/>')
        svg_parts.append(f'<text x="{margin_left - 10}" y="{y_pos + 5:.1f}" font-family="Segoe UI" font-size="14" fill="#9CA3AF" text-anchor="end">{int(val_label)}</text>')

    for i, cat in enumerate(categories):
        for j, s in enumerate(series):
            data_val = s["data"][i] if i < len(s.get("data", [])) else 0
            bar_height = ((data_val - val_min) / max(val_max - val_min, 1)) * chart_h
            if bar_height < 0:
                bar_height = 0
            x_pos = margin_left + (i * slot_width) + padding + (j * bar_width)
            y_pos = svg_h - margin_bottom - bar_height
            color = colors[j % len(colors)]
            svg_parts.append(f'<rect x="{x_pos:.1f}" y="{y_pos:.1f}" width="{bar_width * 0.85:.1f}" height="{bar_height:.1f}" fill="{color}" rx="3"/>')
            svg_parts.append(f'<text x="{x_pos + bar_width * 0.42:.1f}" y="{y_pos - 6:.1f}" font-family="Segoe UI" font-size="12" fill="{color}" font-weight="bold" text-anchor="middle">{data_val}</text>')
        cat_x = margin_left + (i * slot_width) + (slot_width / 2)
        svg_parts.append(f'<text x="{cat_x:.1f}" y="{svg_h - margin_bottom + 25:.1f}" font-family="Segoe UI" font-size="14" fill="{title_color}" font-weight="bold" text-anchor="middle">{cat}</text>')

    if y_axis_label:
        svg_parts.append(f'<text transform="rotate(-90)" x="{-svg_h/2:.1f}" y="20" font-family="Segoe UI" font-size="14" fill="{subtitle_color}" text-anchor="middle">{y_axis_label}</text>')

    legend_parts = []
    for j, s in enumerate(series):
        lx = margin_left + j * 150
        color = colors[j % len(colors)]
        legend_parts.append(f'<rect x="{lx}" y="10" width="14" height="14" fill="{color}" rx="2"/>')
        legend_parts.append(f'<text x="{lx + 20}" y="22" font-family="Segoe UI" font-size="13" fill="{title_color}">{s.get("name", "Series")}</text>')
    svg_parts.extend(legend_parts)

    svg_inner = "\\n".join(svg_parts)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">{svg_inner}</svg>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <textbox x="60" y="40" width="1400" height="70" font="Segoe UI" size="42" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="60" y="110" width="1400" height="40" font="Segoe UI" size="22" color="{subtitle_color}" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="180" y="180" width="{svg_w}" height="{svg_h}" pixel_width="{svg_w}" pixel_height="{svg_h}">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_horizontal_bar_chart_slide_xml(
    title: str = "Market Comparison",
    subtitle: str = "Horizontal bar analysis",
    categories: list = None,
    series: list = None,
    colors: list = None,
    background_color: str = "#050505",
    title_color: str = "#FFFFFF",
    subtitle_color: str = "#DFFF00",
) -> str:
    '''
    Generate an XML slide with a dynamic horizontal bar chart.
    '''
    import html as html_mod

    if categories is None:
        categories = ["North America", "Europe", "Asia"]
    if series is None:
        series = [{"name": "2024", "data": [3, 6, 16]}, {"name": "2025", "data": [6, 14, 18]}]
    if colors is None:
        colors = ["#DFFF00", "#7B8C00", "#4B9CD3", "#FF6B35"]

    svg_w, svg_h = 1000, 700
    margin_top, margin_bottom, margin_left, margin_right = 60, 60, 220, 50
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    all_vals = [v for s in series for v in s.get("data", [])]
    val_max = max(all_vals) if all_vals else 100
    step = 10 ** (len(str(int(val_max))) - 1) if val_max > 0 else 10
    val_max = ((int(val_max) // step) + 1) * step

    num_cats = len(categories)
    num_series = len(series)
    slot_height = chart_h / max(num_cats, 1)
    bar_height = (slot_height * 0.6) / max(num_series, 1)

    svg_parts = []
    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        lx = margin_left + j * 140
        svg_parts.append(f'<circle cx="{lx}" cy="30" r="8" fill="{color}"/>')
        svg_parts.append(f'<text x="{lx + 15}" y="36" font-family="Segoe UI" font-size="16" fill="#FFFFFF">{s.get("name", "Series")}</text>')

    num_grid = 5
    for i in range(num_grid + 1):
        x_ratio = i / num_grid
        x_pos = margin_left + x_ratio * chart_w
        val_label = val_max * x_ratio
        svg_parts.append(f'<line x1="{x_pos:.1f}" y1="{margin_top}" x2="{x_pos:.1f}" y2="{svg_h - margin_bottom}" stroke="#222222" stroke-width="1"/>')
        svg_parts.append(f'<text x="{x_pos:.1f}" y="{svg_h - margin_bottom + 25}" font-family="Segoe UI" font-size="14" fill="#F0F0F0" text-anchor="middle">{int(val_label)}</text>')

    for i, cat in enumerate(categories):
        slot_y = margin_top + i * slot_height
        padding = (slot_height - num_series * bar_height) / 2
        label_y = slot_y + slot_height / 2
        svg_parts.append(f'<text x="{margin_left - 10}" y="{label_y + 5:.1f}" font-family="Segoe UI" font-size="16" fill="#F0F0F0" text-anchor="end">{cat}</text>')
        for j, s in enumerate(series):
            data_val = s["data"][i] if i < len(s.get("data", [])) else 0
            bar_w = (data_val / max(val_max, 1)) * chart_w
            y_pos = slot_y + padding + j * bar_height
            color = colors[j % len(colors)]
            svg_parts.append(f'<rect x="{margin_left}" y="{y_pos:.1f}" width="{bar_w:.1f}" height="{bar_height * 0.85:.1f}" fill="{color}" rx="4"/>')

    svg_inner = "\\n".join(svg_parts)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">{svg_inner}</svg>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <textbox x="60" y="50" width="600" height="80" font="Segoe UI" size="52" color="{title_color}" bold="true" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="60" y="140" width="600" height="60" font="Segoe UI" size="28" color="{subtitle_color}" bold="true" align="left" vertical_align="top" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="500" y="80" width="{svg_w}" height="{svg_h}" pixel_width="{svg_w}" pixel_height="{svg_h}">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_line_chart_slide_xml(
    title: str = "Revenue Trend",
    subtitle: str = "Monthly performance tracking",
    categories: list = None,
    series: list = None,
    colors: list = None,
    background_color: str = "#FFFFFF",
    title_color: str = "#1B2559",
    subtitle_color: str = "#6B7280",
) -> str:
    '''
    Generate an XML slide with a dynamic line chart.
    '''
    import html as html_mod

    if categories is None:
        categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    if series is None:
        series = [{"name": "Revenue", "data": [10, 25, 18, 30, 22, 40]}]
    if colors is None:
        colors = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]

    svg_w, svg_h = 1200, 550
    margin_top, margin_bottom, margin_left, margin_right = 50, 60, 80, 50
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    all_vals = [v for s in series for v in s.get("data", [])]
    val_max = max(all_vals) if all_vals else 100
    val_min = min(all_vals) if all_vals else 0
    if val_min > 0:
        val_min = 0
    val_range = val_max - val_min
    step = 10 ** (len(str(int(val_range))) - 1) if val_range > 0 else 10
    val_max = ((int(val_max) // step) + 1) * step

    num_cats = len(categories)
    svg_parts = []

    num_grid = 5
    for i in range(num_grid + 1):
        y_ratio = i / num_grid
        y_pos = svg_h - margin_bottom - y_ratio * chart_h
        val_label = val_min + (val_max - val_min) * y_ratio
        svg_parts.append(f'<line x1="{margin_left}" y1="{y_pos:.1f}" x2="{svg_w - margin_right}" y2="{y_pos:.1f}" stroke="#E5E7EB" stroke-width="1"/>')
        svg_parts.append(f'<text x="{margin_left - 10}" y="{y_pos + 5:.1f}" font-family="Segoe UI" font-size="13" fill="#9CA3AF" text-anchor="end">{int(val_label)}</text>')

    for i, cat in enumerate(categories):
        x_pos = margin_left + (i / max(num_cats - 1, 1)) * chart_w
        svg_parts.append(f'<text x="{x_pos:.1f}" y="{svg_h - margin_bottom + 25}" font-family="Segoe UI" font-size="13" fill="#6B7280" text-anchor="middle">{cat}</text>')

    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        data = s.get("data", [])
        points = []
        for i, val in enumerate(data):
            x = margin_left + (i / max(len(data) - 1, 1)) * chart_w
            y = svg_h - margin_bottom - ((val - val_min) / max(val_max - val_min, 1)) * chart_h
            points.append(f"{x:.1f},{y:.1f}")
        if points:
            path_d = "M " + " L ".join(points)
            svg_parts.append(f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
            for i, val in enumerate(data):
                x = margin_left + (i / max(len(data) - 1, 1)) * chart_w
                y = svg_h - margin_bottom - ((val - val_min) / max(val_max - val_min, 1)) * chart_h
                svg_parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"/>')
                svg_parts.append(f'<text x="{x:.1f}" y="{y - 12:.1f}" font-family="Segoe UI" font-size="11" fill="{color}" font-weight="bold" text-anchor="middle">{val}</text>')

    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        lx = margin_left + j * 140
        svg_parts.append(f'<line x1="{lx}" y1="15" x2="{lx + 20}" y2="15" stroke="{color}" stroke-width="3"/>')
        svg_parts.append(f'<text x="{lx + 28}" y="20" font-family="Segoe UI" font-size="13" fill="{title_color}">{s.get("name", "Series")}</text>')

    svg_inner = "\\n".join(svg_parts)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">{svg_inner}</svg>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <textbox x="60" y="40" width="1400" height="70" font="Segoe UI" size="42" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="60" y="110" width="1400" height="40" font="Segoe UI" size="22" color="{subtitle_color}" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="180" y="220" width="{svg_w}" height="{svg_h}" pixel_width="{svg_w}" pixel_height="{svg_h}">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_scatter_chart_slide_xml(
    title: str = "Correlation Analysis",
    subtitle: str = "Scatter plot visualization",
    x_label: str = "X Axis",
    y_label: str = "Y Axis",
    series: list = None,
    colors: list = None,
    background_color: str = "#FFFFFF",
    title_color: str = "#1B2559",
    subtitle_color: str = "#6B7280",
) -> str:
    '''
    Generate an XML slide with a dynamic scatter plot.
    '''
    import html as html_mod

    if series is None:
        series = [{"name": "Group A", "data": [[10, 20], [15, 35], [25, 15], [30, 40], [45, 25]]}]
    if colors is None:
        colors = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444"]

    svg_w, svg_h = 1100, 550
    margin_top, margin_bottom, margin_left, margin_right = 50, 60, 80, 50
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    all_x = [p[0] for s in series for p in s.get("data", [])]
    all_y = [p[1] for s in series for p in s.get("data", [])]
    x_min, x_max = (min(all_x), max(all_x)) if all_x else (0, 100)
    y_min, y_max = (min(all_y), max(all_y)) if all_y else (0, 100)
    if x_min > 0: x_min = 0
    if y_min > 0: y_min = 0
    x_step = 10 ** (len(str(int(x_max))) - 1) if x_max > 0 else 10
    y_step = 10 ** (len(str(int(y_max))) - 1) if y_max > 0 else 10
    x_max = ((int(x_max) // x_step) + 1) * x_step
    y_max = ((int(y_max) // y_step) + 1) * y_step

    svg_parts = []
    for i in range(6):
        y_ratio = i / 5
        y_pos = svg_h - margin_bottom - y_ratio * chart_h
        val = y_min + (y_max - y_min) * y_ratio
        svg_parts.append(f'<line x1="{margin_left}" y1="{y_pos:.1f}" x2="{svg_w - margin_right}" y2="{y_pos:.1f}" stroke="#E5E7EB" stroke-width="1"/>')
        svg_parts.append(f'<text x="{margin_left - 10}" y="{y_pos + 5:.1f}" font-family="Segoe UI" font-size="12" fill="#9CA3AF" text-anchor="end">{int(val)}</text>')
    for i in range(6):
        x_ratio = i / 5
        x_pos = margin_left + x_ratio * chart_w
        val = x_min + (x_max - x_min) * x_ratio
        svg_parts.append(f'<text x="{x_pos:.1f}" y="{svg_h - margin_bottom + 22}" font-family="Segoe UI" font-size="12" fill="#9CA3AF" text-anchor="middle">{int(val)}</text>')

    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        for pt in s.get("data", []):
            px = margin_left + ((pt[0] - x_min) / max(x_max - x_min, 1)) * chart_w
            py = svg_h - margin_bottom - ((pt[1] - y_min) / max(y_max - y_min, 1)) * chart_h
            svg_parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="{color}" opacity="0.75"/>')

    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        lx = margin_left + j * 140
        svg_parts.append(f'<circle cx="{lx + 7}" cy="15" r="6" fill="{color}"/>')
        svg_parts.append(f'<text x="{lx + 20}" y="20" font-family="Segoe UI" font-size="13" fill="{title_color}">{s.get("name", "Series")}</text>')

    svg_parts.append(f'<text x="{svg_w / 2:.1f}" y="{svg_h - 10}" font-family="Segoe UI" font-size="14" fill="{subtitle_color}" text-anchor="middle">{x_label}</text>')
    svg_parts.append(f'<text transform="rotate(-90)" x="{-svg_h / 2:.1f}" y="20" font-family="Segoe UI" font-size="14" fill="{subtitle_color}" text-anchor="middle">{y_label}</text>')

    svg_inner = "\\n".join(svg_parts)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">{svg_inner}</svg>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <textbox x="60" y="40" width="1400" height="70" font="Segoe UI" size="42" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="60" y="110" width="1400" height="40" font="Segoe UI" size="22" color="{subtitle_color}" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="220" y="220" width="{svg_w}" height="{svg_h}" pixel_width="{svg_w}" pixel_height="{svg_h}">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_stacked_bar_chart_slide_xml(
    title: str = "Budget Allocation",
    subtitle: str = "Stacked bar breakdown by category",
    categories: list = None,
    series: list = None,
    colors: list = None,
    background_color: str = "#FFFFFF",
    title_color: str = "#1B2559",
    subtitle_color: str = "#6B7280",
) -> str:
    '''
    Generate an XML slide with a dynamic stacked bar chart.
    '''
    import html as html_mod

    if categories is None:
        categories = ["2022", "2023", "2024"]
    if series is None:
        series = [{"name": "Marketing", "data": [20, 30, 25]}, {"name": "R&D", "data": [40, 35, 50]}, {"name": "Sales", "data": [15, 20, 18]}]
    if colors is None:
        colors = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]

    svg_w, svg_h = 1100, 550
    margin_top, margin_bottom, margin_left, margin_right = 50, 60, 80, 50
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    num_cats = len(categories)
    stacked_totals = []
    for i in range(num_cats):
        total = sum(s["data"][i] if i < len(s.get("data", [])) else 0 for s in series)
        stacked_totals.append(total)
    val_max = max(stacked_totals) if stacked_totals else 100
    step = 10 ** (len(str(int(val_max))) - 1) if val_max > 0 else 10
    val_max = ((int(val_max) // step) + 1) * step

    slot_width = chart_w / max(num_cats, 1)
    bar_width = slot_width * 0.6

    svg_parts = []
    for i in range(6):
        y_ratio = i / 5
        y_pos = svg_h - margin_bottom - y_ratio * chart_h
        val = val_max * y_ratio
        svg_parts.append(f'<line x1="{margin_left}" y1="{y_pos:.1f}" x2="{svg_w - margin_right}" y2="{y_pos:.1f}" stroke="#E5E7EB" stroke-width="1"/>')
        svg_parts.append(f'<text x="{margin_left - 10}" y="{y_pos + 5:.1f}" font-family="Segoe UI" font-size="13" fill="#9CA3AF" text-anchor="end">{int(val)}</text>')

    for i, cat in enumerate(categories):
        x_pos = margin_left + i * slot_width + (slot_width - bar_width) / 2
        y_bottom = svg_h - margin_bottom
        for j, s in enumerate(series):
            data_val = s["data"][i] if i < len(s.get("data", [])) else 0
            bar_h = (data_val / max(val_max, 1)) * chart_h
            y_top = y_bottom - bar_h
            color = colors[j % len(colors)]
            svg_parts.append(f'<rect x="{x_pos:.1f}" y="{y_top:.1f}" width="{bar_width:.1f}" height="{bar_h:.1f}" fill="{color}"/>')
            if bar_h > 18:
                svg_parts.append(f'<text x="{x_pos + bar_width / 2:.1f}" y="{y_top + bar_h / 2 + 5:.1f}" font-family="Segoe UI" font-size="12" fill="#FFFFFF" font-weight="bold" text-anchor="middle">{data_val}</text>')
            y_bottom = y_top
        svg_parts.append(f'<text x="{x_pos + bar_width / 2:.1f}" y="{svg_h - margin_bottom + 22}" font-family="Segoe UI" font-size="14" fill="{title_color}" font-weight="bold" text-anchor="middle">{cat}</text>')

    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        lx = margin_left + j * 130
        svg_parts.append(f'<rect x="{lx}" y="10" width="14" height="14" fill="{color}" rx="2"/>')
        svg_parts.append(f'<text x="{lx + 20}" y="22" font-family="Segoe UI" font-size="13" fill="{title_color}">{s.get("name", "Series")}</text>')

    svg_inner = "\\n".join(svg_parts)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">{svg_inner}</svg>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <textbox x="60" y="40" width="1400" height="70" font="Segoe UI" size="42" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="60" y="110" width="1400" height="40" font="Segoe UI" size="22" color="{subtitle_color}" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="220" y="220" width="{svg_w}" height="{svg_h}" pixel_width="{svg_w}" pixel_height="{svg_h}">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_waterfall_chart_slide_xml(
    title: str = "Revenue Waterfall",
    subtitle: str = "From start to end breakdown",
    items: list = None,
    colors: list = None,
    background_color: str = "#FFFFFF",
    title_color: str = "#1B2559",
    subtitle_color: str = "#6B7280",
) -> str:
    '''
    Generate an XML slide with a dynamic waterfall chart.
    '''
    import html as html_mod

    if items is None:
        items = [
            {"label": "Start", "value": 100, "type": "total"},
            {"label": "Growth", "value": 50, "type": "increase"},
            {"label": "Returns", "value": -20, "type": "decrease"},
            {"label": "Tax", "value": -15, "type": "decrease"},
            {"label": "End", "value": 115, "type": "total"},
        ]
    if colors is None:
        colors = ["#4F46E5", "#10B981", "#EF4444"]

    svg_w, svg_h = 1100, 520
    margin_top, margin_bottom, margin_left, margin_right = 40, 70, 80, 40
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    running = 0
    all_tops = []
    for item in items:
        if item.get("type") == "total":
            running = item["value"]
        else:
            running += item["value"]
        all_tops.append(running)
    val_max = max(max(all_tops), max(item["value"] for item in items if item.get("type") == "total")) if items else 100
    step_size = 10 ** (len(str(int(val_max))) - 1) if val_max > 0 else 10
    val_max = ((int(val_max) // step_size) + 1) * step_size

    num_items = len(items)
    slot_width = chart_w / max(num_items, 1)
    bar_width = slot_width * 0.55

    svg_parts = []
    for i in range(6):
        y_ratio = i / 5
        y_pos = svg_h - margin_bottom - y_ratio * chart_h
        val = val_max * y_ratio
        svg_parts.append(f'<line x1="{margin_left}" y1="{y_pos:.1f}" x2="{svg_w - margin_right}" y2="{y_pos:.1f}" stroke="#E5E7EB" stroke-width="1"/>')
        svg_parts.append(f'<text x="{margin_left - 10}" y="{y_pos + 5:.1f}" font-family="Segoe UI" font-size="12" fill="#9CA3AF" text-anchor="end">{int(val)}</text>')

    running = 0
    for i, item in enumerate(items):
        x_pos = margin_left + i * slot_width + (slot_width - bar_width) / 2
        item_type = item.get("type", "increase")
        val = item["value"]

        if item_type == "total":
            bar_h = (val / max(val_max, 1)) * chart_h
            y_top = svg_h - margin_bottom - bar_h
            color = colors[0]
            running = val
        elif item_type == "increase" or val > 0:
            bar_h = (abs(val) / max(val_max, 1)) * chart_h
            y_top = svg_h - margin_bottom - ((running + val) / max(val_max, 1)) * chart_h
            color = colors[1]
            running += val
        else:
            bar_h = (abs(val) / max(val_max, 1)) * chart_h
            y_top = svg_h - margin_bottom - (running / max(val_max, 1)) * chart_h
            color = colors[2]
            running += val

        svg_parts.append(f'<rect x="{x_pos:.1f}" y="{y_top:.1f}" width="{bar_width:.1f}" height="{max(bar_h, 1):.1f}" fill="{color}" rx="3"/>')
        svg_parts.append(f'<text x="{x_pos + bar_width / 2:.1f}" y="{y_top - 8:.1f}" font-family="Segoe UI" font-size="13" fill="{color}" font-weight="bold" text-anchor="middle">{val}</text>')
        svg_parts.append(f'<text x="{x_pos + bar_width / 2:.1f}" y="{svg_h - margin_bottom + 22}" font-family="Segoe UI" font-size="13" fill="{title_color}" text-anchor="middle">{item["label"]}</text>')

    svg_inner = "\\n".join(svg_parts)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">{svg_inner}</svg>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <textbox x="60" y="40" width="1400" height="70" font="Segoe UI" size="42" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="60" y="110" width="1400" height="40" font="Segoe UI" size="22" color="{subtitle_color}" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="220" y="230" width="{svg_w}" height="{svg_h}" pixel_width="{svg_w}" pixel_height="{svg_h}">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_radar_chart_slide_xml(
    title: str = "Skills Assessment",
    subtitle: str = "Multi-dimensional performance radar",
    labels: list = None,
    series: list = None,
    colors: list = None,
    background_color: str = "#FFFFFF",
    title_color: str = "#1B2559",
    subtitle_color: str = "#6B7280",
) -> str:
    '''
    Generate an XML slide with a dynamic radar/spider chart.
    '''
    import html as html_mod
    import math

    if labels is None:
        labels = ["Speed", "Power", "Skill", "Defense", "Stamina"]
    if series is None:
        series = [{"name": "Player A", "data": [80, 65, 90, 70, 85]}]
    if colors is None:
        colors = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444"]

    svg_w, svg_h = 700, 600
    cx, cy = svg_w / 2, svg_h / 2 + 20
    max_r = 220
    n = len(labels)

    svg_parts = []
    for level in range(1, 6):
        r = max_r * level / 5
        points_list = []
        for i in range(n):
            angle = (2 * math.pi * i / n) - math.pi / 2
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            points_list.append(f"{px:.1f},{py:.1f}")
        polygon_str = " ".join(points_list)
        svg_parts.append(f'<polygon points="{polygon_str}" fill="none" stroke="#E5E7EB" stroke-width="1"/>')

    for i in range(n):
        angle = (2 * math.pi * i / n) - math.pi / 2
        ex = cx + max_r * math.cos(angle)
        ey = cy + max_r * math.sin(angle)
        svg_parts.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#D1D5DB" stroke-width="1"/>')
        lx = cx + (max_r + 28) * math.cos(angle)
        ly = cy + (max_r + 28) * math.sin(angle)
        anchor = "middle"
        if math.cos(angle) > 0.3: anchor = "start"
        elif math.cos(angle) < -0.3: anchor = "end"
        svg_parts.append(f'<text x="{lx:.1f}" y="{ly + 5:.1f}" font-family="Segoe UI" font-size="14" fill="{title_color}" text-anchor="{anchor}">{labels[i]}</text>')

    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        data = s.get("data", [])
        pts = []
        for i, val in enumerate(data):
            r = max_r * min(val, 100) / 100
            angle = (2 * math.pi * i / n) - math.pi / 2
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            pts.append(f"{px:.1f},{py:.1f}")
        poly = " ".join(pts)
        svg_parts.append(f'<polygon points="{poly}" fill="{color}" fill-opacity="0.2" stroke="{color}" stroke-width="2.5"/>')
        for i, val in enumerate(data):
            r = max_r * min(val, 100) / 100
            angle = (2 * math.pi * i / n) - math.pi / 2
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            svg_parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color}"/>')

    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        lx = 20 + j * 140
        svg_parts.append(f'<rect x="{lx}" y="5" width="14" height="14" fill="{color}" rx="2"/>')
        svg_parts.append(f'<text x="{lx + 20}" y="17" font-family="Segoe UI" font-size="13" fill="{title_color}">{s.get("name", "Series")}</text>')

    svg_inner = "\\n".join(svg_parts)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">{svg_inner}</svg>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <textbox x="60" y="40" width="1400" height="70" font="Segoe UI" size="42" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="60" y="110" width="1400" height="40" font="Segoe UI" size="22" color="{subtitle_color}" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="430" y="200" width="{svg_w}" height="{svg_h}" pixel_width="{svg_w}" pixel_height="{svg_h}">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_area_chart_slide_xml(
    title: str = "Growth Trends",
    subtitle: str = "Area chart showing cumulative growth",
    categories: list = None,
    series: list = None,
    colors: list = None,
    background_color: str = "#FFFFFF",
    title_color: str = "#1B2559",
    subtitle_color: str = "#6B7280",
) -> str:
    '''
    Generate an XML slide with a dynamic area chart.
    '''
    import html as html_mod

    if categories is None:
        categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    if series is None:
        series = [{"name": "Users", "data": [100, 200, 180, 300, 250, 400]}]
    if colors is None:
        colors = ["#4F46E5", "#10B981", "#F59E0B"]

    svg_w, svg_h = 1200, 550
    margin_top, margin_bottom, margin_left, margin_right = 50, 60, 80, 50
    chart_w = svg_w - margin_left - margin_right
    chart_h = svg_h - margin_top - margin_bottom

    all_vals = [v for s in series for v in s.get("data", [])]
    val_max = max(all_vals) if all_vals else 100
    val_min = 0
    step = 10 ** (len(str(int(val_max))) - 1) if val_max > 0 else 10
    val_max = ((int(val_max) // step) + 1) * step

    svg_parts = []
    for i in range(6):
        y_ratio = i / 5
        y_pos = svg_h - margin_bottom - y_ratio * chart_h
        val = val_max * y_ratio
        svg_parts.append(f'<line x1="{margin_left}" y1="{y_pos:.1f}" x2="{svg_w - margin_right}" y2="{y_pos:.1f}" stroke="#E5E7EB" stroke-width="1"/>')
        svg_parts.append(f'<text x="{margin_left - 10}" y="{y_pos + 5:.1f}" font-family="Segoe UI" font-size="13" fill="#9CA3AF" text-anchor="end">{int(val)}</text>')

    num_cats = len(categories)
    for i, cat in enumerate(categories):
        x_pos = margin_left + (i / max(num_cats - 1, 1)) * chart_w
        svg_parts.append(f'<text x="{x_pos:.1f}" y="{svg_h - margin_bottom + 22}" font-family="Segoe UI" font-size="13" fill="#6B7280" text-anchor="middle">{cat}</text>')

    baseline_y = svg_h - margin_bottom
    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        data = s.get("data", [])
        line_pts = []
        for i, val in enumerate(data):
            x = margin_left + (i / max(len(data) - 1, 1)) * chart_w
            y = svg_h - margin_bottom - (val / max(val_max, 1)) * chart_h
            line_pts.append((x, y))

        if line_pts:
            area_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in line_pts)
            area_points = f"{line_pts[0][0]:.1f},{baseline_y:.1f} " + area_points + f" {line_pts[-1][0]:.1f},{baseline_y:.1f}"
            svg_parts.append(f'<polygon points="{area_points}" fill="{color}" fill-opacity="0.15"/>')
            path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in line_pts)
            svg_parts.append(f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="2.5"/>')
            for x, y in line_pts:
                svg_parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')

    for j, s in enumerate(series):
        color = colors[j % len(colors)]
        lx = margin_left + j * 140
        svg_parts.append(f'<rect x="{lx}" y="10" width="14" height="14" fill="{color}" rx="2" fill-opacity="0.3"/>')
        svg_parts.append(f'<text x="{lx + 20}" y="22" font-family="Segoe UI" font-size="13" fill="{title_color}">{s.get("name", "Series")}</text>')

    svg_inner = "\\n".join(svg_parts)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}">{svg_inner}</svg>')

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <textbox x="60" y="40" width="1400" height="70" font="Segoe UI" size="42" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="60" y="110" width="1400" height="40" font="Segoe UI" size="22" color="{subtitle_color}" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="180" y="220" width="{svg_w}" height="{svg_h}" pixel_width="{svg_w}" pixel_height="{svg_h}">{escaped_svg}</svg>
  </slide>
</presentation>
'''
    return xml

def generate_simple_donut_chart_slide_xml(
    title: str = "Market Share",
    subtitle: str = "Distribution overview",
    items: list = None,
    colors: list = None,
    background_color: str = "#FFFFFF",
    title_color: str = "#333333",
    subtitle_color: str = "#888888",
) -> str:
    '''
    Generate an XML slide with a single large donut chart.
    '''
    import html as html_mod
    import math

    if items is None:
        items = [{"label": "Product A", "value": 45}, {"label": "Product B", "value": 30}, {"label": "Product C", "value": 25}]
    if colors is None:
        colors = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]

    total = sum(item.get("value", 0) for item in items)
    if total == 0:
        total = 1

    cx, cy, r = 300, 250, 140
    stroke_w = 55
    circumference = 2 * math.pi * r
    svg_parts = []

    svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#F3F4F6" stroke-width="{stroke_w}"/>')

    current_angle = -90
    for i, item in enumerate(items):
        color = colors[i % len(colors)]
        val = item.get("value", 0)
        pct = (val / total) * 100
        dash = (pct / 100) * circumference
        svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke_w}" stroke-dasharray="{dash:.2f} {circumference:.2f}" transform="rotate({current_angle:.1f} {cx} {cy})" stroke-linecap="round"/>')
        current_angle += (pct / 100) * 360

    svg_parts.append(f'<text x="{cx}" y="{cy - 5}" font-family="Segoe UI" font-size="36" font-weight="bold" fill="{title_color}" text-anchor="middle">{total}</text>')
    svg_parts.append(f'<text x="{cx}" y="{cy + 25}" font-family="Segoe UI" font-size="16" fill="{subtitle_color}" text-anchor="middle">Total</text>')

    svg_inner = "\\n".join(svg_parts)
    escaped_svg = html_mod.escape(f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="500" viewBox="0 0 600 500">{svg_inner}</svg>')

    legend_xml = ""
    y_start = 300
    for i, item in enumerate(items):
        color = colors[i % len(colors)]
        label = item.get("label", "")
        val = item.get("value", 0)
        pct_val = int((val / total) * 100)
        legend_xml += f'''
    <polygon points="1050,{y_start + 5} 1070,{y_start + 5} 1070,{y_start + 25} 1050,{y_start + 25}" fill="{color}"/>
    <textbox x="1080" y="{y_start}" width="400" height="30" font="Segoe UI" size="20" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1">{label} ({pct_val}%)</textbox>
'''
        y_start += 45

    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <textbox x="60" y="60" width="1400" height="80" font="Segoe UI" size="48" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{title}</textbox>
    <textbox x="60" y="145" width="1400" height="40" font="Segoe UI" size="24" color="{subtitle_color}" align="left" vertical_align="middle" single_line="true" max_lines="1" reflow_on_resize="true">{subtitle}</textbox>
    <svg x="250" y="220" width="600" height="500" pixel_width="600" pixel_height="500">{escaped_svg}</svg>{legend_xml}
  </slide>
</presentation>
'''
    return xml

def generate_thynk_unlimited_thank_you_slide_xml(
    company_name: str = "Thynk Unlimited",
    title: str = "THANK YOU",
    subtitle: str = "FOR YOUR ATTENTION",
    date: str = "December 2023",
    email: str = "hello@reallygreatsite.com",
    website: str = "www.reallygreatsite.com",
    image_url: str = "https://images.unsplash.com/photo-1542744173-8e7e53415bb0?q=80&w=800&auto=format&fit=crop",
) -> str:
    """
    Generate a Thank You slide for the Thynk Unlimited theme.
    """
    color_primary = "#064AD0"
    color_light_blue = "#B8C8F1"
    color_bg_grey = "#F4F5F7"
    
    xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    
    <!-- Left Blue Bar -->
    <shape type="rounded_rectangle" x="-50" y="0" width="150" height="900" fill="{color_primary}" />

    <!-- Bottom Left Grey Area -->
    <shape type="rectangle" x="100" y="620" width="950" height="280" fill="{color_bg_grey}" />

    <!-- Right Side Image -->
    <image src="{image_url.replace('&', '&amp;')}" x="1050" y="0" width="550" height="900" crop="true" />
    
    <!-- Right Blue Bars -->
    <shape type="rectangle" x="1520" y="600" width="80" height="300" fill="{color_primary}" />
    <shape type="rectangle" x="1520" y="0" width="80" height="100" fill="{color_primary}" />
    
    <!-- Light Blue Shapes -->
    <!-- Top rounded box -->
    <shape type="rounded_rectangle" x="950" y="70" width="140" height="140" fill="{color_light_blue}" />
    
    <!-- Bottom donut -->
    <!-- Outer light blue circle -->
    <shape type="circle" x="730" y="780" width="220" height="220" fill="{color_light_blue}" />
    <!-- Inner grey circle (matches background grey) -->
    <shape type="circle" x="770" y="820" width="140" height="140" fill="{color_bg_grey}" />

    <!-- Thynk Unlimited Logo -->
    <polygon points="140,70 160,50 180,70 170,80 160,70 150,80" fill="{color_primary}" />
    <polygon points="140,90 160,70 180,90 170,100 160,90 150,100" fill="{color_primary}" />
    <textbox x="190" y="45" width="400" height="60" font="Segoe UI" size="28" color="#000000" bold="true" align="left" vertical_align="middle">{company_name.replace('&', '&amp;')}</textbox>

    <!-- Main Title -->
    <textbox x="135" y="280" width="800" height="150" font="Segoe UI" size="110" color="#000000" bold="true" align="left" vertical_align="middle" single_line="true">{title.replace('&', '&amp;')}</textbox>
    <textbox x="140" y="420" width="800" height="50" font="Segoe UI" size="32" color="#333333" align="left" vertical_align="middle" single_line="true">{subtitle.replace('&', '&amp;')}</textbox>

    <!-- Date Pill -->
    <shape type="rounded_rectangle" x="140" y="500" width="350" height="50" fill="{color_primary}" />
    <textbox x="140" y="500" width="350" height="50" font="Segoe UI" size="22" color="#FFFFFF" align="center" vertical_align="middle">{date.replace('&', '&amp;')}</textbox>

    <!-- Contact Info -->
    <!-- Email -->
    <shape type="circle" x="140" y="690" width="45" height="45" fill="{color_primary}" />
    <textbox x="140" y="690" width="45" height="45" font="Segoe UI" size="22" color="#FFFFFF" bold="true" align="center" vertical_align="middle" margin_left="0" margin_right="0" margin_top="0" margin_bottom="0">?</textbox>
    <textbox x="200" y="690" width="500" height="45" font="Segoe UI" size="24" color="#333333" align="left" vertical_align="middle">{email.replace('&', '&amp;')}</textbox>

    <!-- Website -->
    <shape type="circle" x="140" y="755" width="45" height="45" fill="{color_primary}" />
    <textbox x="140" y="755" width="45" height="45" font="Segoe UI" size="22" color="#FFFFFF" bold="true" align="center" vertical_align="middle" margin_left="0" margin_right="0" margin_top="0" margin_bottom="0">??</textbox>
    <textbox x="200" y="755" width="500" height="45" font="Segoe UI" size="24" color="#333333" align="left" vertical_align="middle">{website.replace('&', '&amp;')}</textbox>

  </slide>
</presentation>
"""
    return xml_template

def generate_tech_pitch_deck_thank_you_slide_xml(
    company_name="Arowwai\nIndustries",
    title="THANK YOU!",
    name="Aaron Loeb",
    role="CEO & Founder",
    phone="+123-456-7890",
    website="www.reallygreatsite.com",
    address="123 Anywhere St., Any City, State,\nCountry 12345",
    profile_image_url="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=500&h=500&fit=crop",
    image_url="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=800&auto=format&fit=crop"
) -> str:
    color_blue = "#185b9d"
    color_dark_text = "#0a2540"
    color_light_blue = "#5380a5"
    color_light_decor = "#d8e2eb"
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <!-- Right side Image -->
    <image src="{image_url.replace('&', '&amp;')}" x="1080" y="80" width="520" height="740" />
    <!-- Blue bars top and bottom right -->
    <shape type="rectangle" x="1080" y="0" width="520" height="80" fill="{color_light_blue}" />
    <shape type="rectangle" x="1080" y="820" width="520" height="80" fill="{color_light_blue}" />
    
    <!-- Left background decorations -->
    <shape type="circle" x="-200" y="600" width="480" height="480" fill="{color_light_decor}" />
    <shape type="circle" x="-80" y="650" width="400" height="400" fill="#ffffff" />
    <shape type="circle" x="-250" y="650" width="400" height="400" fill="{color_light_decor}" />
    
    <!-- Logo -->
    <polygon points="300,150 330,80 360,150" fill="{color_blue}" />
    <polygon points="340,150 360,110 380,150" fill="{color_light_blue}" />
    <textbox x="220" y="170" width="240" height="80" font="Arial" size="24" color="{color_blue}" bold="true" align="center" vertical_align="middle" single_line="false" max_lines="2" overflow="shrink" reflow_on_resize="true">{company_name.replace('&', '&amp;')}</textbox>
    
    <!-- Title -->
    <textbox x="140" y="260" width="800" height="140" font="Arial" size="110" color="{color_dark_text}" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1" overflow="shrink" reflow_on_resize="true">{title.replace('&', '&amp;')}</textbox>
    
    <!-- Profile section -->
    <shape type="circle" x="245" y="415" width="230" height="230" fill="#ffffff" stroke="{color_blue}" stroke_width="6" />
    <image src="{profile_image_url.replace('&', '&amp;')}" x="250" y="420" width="220" height="220" shape="circle" />
    
    <!-- Contact Info -->
    <!-- Name and Role -->
    <textbox x="500" y="420" width="450" height="40" font="Arial" size="36" color="{color_blue}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1" overflow="shrink" reflow_on_resize="true">{name.replace('&', '&amp;')}</textbox>
    <textbox x="500" y="465" width="450" height="30" font="Arial" size="24" color="{color_light_blue}" align="left" vertical_align="middle" single_line="true" max_lines="1" overflow="shrink" reflow_on_resize="true">{role.replace('&', '&amp;')}</textbox>
    
    <!-- Phone -->
    <shape type="circle" x="500" y="505" width="36" height="36" fill="{color_blue}" />
    <textbox x="500" y="505" width="36" height="36" font="Arial" size="22" color="#ffffff" bold="true" align="center" vertical_align="middle">??</textbox>
    <textbox x="550" y="505" width="400" height="36" font="Arial" size="22" color="{color_light_blue}" align="left" vertical_align="middle" single_line="true" max_lines="1" overflow="shrink" reflow_on_resize="true">{phone.replace('&', '&amp;')}</textbox>

    <!-- Website -->
    <shape type="circle" x="500" y="555" width="36" height="36" fill="{color_blue}" />
    <textbox x="500" y="555" width="36" height="36" font="Arial" size="22" color="#ffffff" bold="true" align="center" vertical_align="middle">??</textbox>
    <textbox x="550" y="555" width="400" height="36" font="Arial" size="22" color="{color_light_blue}" align="left" vertical_align="middle" single_line="true" max_lines="1" overflow="shrink" reflow_on_resize="true">{website.replace('&', '&amp;')}</textbox>

    <!-- Address -->
    <shape type="circle" x="500" y="605" width="36" height="36" fill="{color_blue}" />
    <textbox x="500" y="605" width="36" height="36" font="Arial" size="22" color="#ffffff" bold="true" align="center" vertical_align="middle">??</textbox>
    <textbox x="550" y="605" width="400" height="70" font="Arial" size="22" color="{color_light_blue}" align="left" vertical_align="top" single_line="false" max_lines="2" overflow="shrink" reflow_on_resize="true">{address.replace('&', '&amp;')}</textbox>

  </slide>
</presentation>
"""
    return xml


def generate_business_proposal_cover_slide_xml(
    brand_name: str = "Larana, Inc.",
    title: str = "BUSINESS PROPOSAL",
    website: str = "www.reallygreatsite.com",
    email: str = "hello@reallygreatsite.com",
    background_color: str = "#FFFFFF",
    title_color: str = "#0B2B5E",
    accent_color: str = "#0B2B5E",
    image1_url: str = "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=800&auto=format&fit=crop",
    image2_url: str = "https://images.unsplash.com/photo-1577017040065-650ee4d43339?q=80&w=800&auto=format&fit=crop",
    image3_url: str = "https://images.unsplash.com/photo-1460472178825-e5240623afd5?q=80&w=800&auto=format&fit=crop",
) -> str:
    """
    Generate XML for a Business Proposal Cover slide with 3 diamond image placeholders.
    """
    xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="{background_color}">
    <!-- Background -->
    <polygon points="0,0 1600,0 1600,900 0,900" fill="{background_color}"/>
    
    <!-- Left Gradient or shape -->
    <polygon points="0,250 120,250 120,650 0,650" fill="{accent_color}" opacity="0.8"/>
    
    <!-- Right side background block (Dark blue) -->
    <polygon points="1200,900 1600,500 1600,900" fill="{accent_color}"/>
    
    <!-- Top Right Corner Shape -->
    <polygon points="1600,0 1600,300 1300,0" fill="{accent_color}"/>
    
    <!-- Text Elements -->
    <textbox x="160" y="120" width="400" height="50" font="Arial" size="24" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1">{{brand_name}}</textbox>
    
    <textbox x="160" y="300" width="800" height="200" font="Arial" size="85" color="{title_color}" bold="true" align="left" vertical_align="middle" single_line="false" max_lines="2" line_spacing="1.1">{{title}}</textbox>
    
    <!-- Footer text -->
    <textbox x="210" y="630" width="400" height="40" font="Arial" size="24" color="{title_color}" align="left" vertical_align="middle" single_line="true" max_lines="1">{{website}}</textbox>
    <textbox x="210" y="690" width="400" height="40" font="Arial" size="24" color="{title_color}" align="left" vertical_align="middle" single_line="true" max_lines="1">{{email}}</textbox>
    
    <!-- Icons for Footer (Simple circles as placeholders) -->
    <circle cx="180" cy="650" r="18" fill="{accent_color}"/>
    <circle cx="180" cy="710" r="18" fill="{accent_color}"/>
    
    <!-- Diamond Images using <image> -->
    <image url="{{image1_url}}" x="850" y="350" width="300" height="300" />
    <image url="{{image2_url}}" x="1200" y="150" width="250" height="250" />
    <image url="{{image3_url}}" x="1200" y="550" width="250" height="250" />
    
    <!-- Decorations (Arrows) -->
    <polygon points="820,160 860,190 820,220" fill="{accent_color}"/>
    <polygon points="880,160 920,190 880,220" fill="none" line_color="{accent_color}" line_width="3"/>
    <polygon points="940,160 980,190 940,220" fill="{accent_color}"/>
    
  </slide>
</presentation>
"""
    return xml_template.format(
        brand_name=brand_name,
        title=title,
        website=website,
        email=email,
        image1_url=image1_url,
        image2_url=image2_url,
        image3_url=image3_url
    )


def generate_image_and_numbered_list_slide_xml(
    title="The Polar Climate and\nIts Extremes",
    image_url="https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=800&auto=format&fit=crop",
    item1_number="01",
    item1_title="Endless Cold",
    item1_desc="Temperatures drop far below zero for months, testing both human and wildlife adaptation to freezing conditions",
    item2_number="02",
    item2_title="Midnight Sun &amp; Polar Night",
    item2_desc="The Arctic experiences months of sunlight and darkness, shaping unique biological and cultural rhythms",
    item3_number="03",
    item3_title="Adapting to Extremes",
    item3_desc="Animals like polar bears and arctic foxes have evolved to thrive in this challenging, ever-changing climate"
) -> str:
    color_slate = "#728AA1"
    color_grey = "#9CA3AF"
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <!-- Image on the left -->
    <image src="{image_url.replace('&', '&amp;')}" shape="circle" x="100" y="100" width="700" height="700" />
    
    <!-- Main Title -->
    <textbox x="870" y="120" width="650" height="150" font="Arial" size="65" color="{color_slate}" bold="true" align="left" vertical_align="middle" single_line="false" max_lines="3" line_spacing="1.2">{title}</textbox>
    
    <!-- Item 1 -->
    <shape type="circle" x="875" y="365" width="70" height="70" fill="{color_slate}" />
    <textbox x="875" y="365" width="70" height="70" font="Arial" size="28" color="#FFFFFF" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1">{item1_number}</textbox>
    
    <textbox x="970" y="355" width="550" height="40" font="Arial" size="28" color="{color_slate}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1">{item1_title}</textbox>
    <textbox x="970" y="400" width="550" height="70" font="Arial" size="20" color="{color_grey}" bold="false" align="left" vertical_align="top" single_line="false" max_lines="3" line_spacing="1.2">{item1_desc}</textbox>
    
    <!-- Item 2 -->
    <shape type="circle" x="875" y="515" width="70" height="70" fill="{color_slate}" />
    <textbox x="875" y="515" width="70" height="70" font="Arial" size="28" color="#FFFFFF" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1">{item2_number}</textbox>
    
    <textbox x="970" y="505" width="550" height="40" font="Arial" size="28" color="{color_slate}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1">{item2_title}</textbox>
    <textbox x="970" y="550" width="550" height="70" font="Arial" size="20" color="{color_grey}" bold="false" align="left" vertical_align="top" single_line="false" max_lines="3" line_spacing="1.2">{item2_desc}</textbox>
    
    <!-- Item 3 -->
    <shape type="circle" x="875" y="665" width="70" height="70" fill="{color_slate}" />
    <textbox x="875" y="665" width="70" height="70" font="Arial" size="28" color="#FFFFFF" bold="true" align="center" vertical_align="middle" single_line="true" max_lines="1">{item3_number}</textbox>
    
    <textbox x="970" y="655" width="550" height="40" font="Arial" size="28" color="{color_slate}" bold="true" align="left" vertical_align="middle" single_line="true" max_lines="1">{item3_title}</textbox>
    <textbox x="970" y="700" width="550" height="70" font="Arial" size="20" color="{color_grey}" bold="false" align="left" vertical_align="top" single_line="false" max_lines="3" line_spacing="1.2">{item3_desc}</textbox>
    
  </slide>
</presentation>
"""
    return xml


def generate_tech_pitch_deck_cover_slide_xml(
    company_name="Arowwai\nIndustries",
    title="Technology\nPitch Deck",
    subtitle="By: Alexander Aronowitz",
    image_url="https://images.unsplash.com/photo-1522071820081-009f0129c71c?q=80&w=800&auto=format&fit=crop"
) -> str:
    color_blue = "#185b9d"
    color_dark_text = "#0a2540"
    color_light_blue = "#5380a5"
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<presentation schemaVersion="1.0" width="1600" height="900" slideWidthInches="13.333" slideHeightInches="7.5">
  <slide background="#FFFFFF">
    <!-- Background Decor -->
    <!-- Top left partial circle -->
    <shape type="circle" x="20" y="-80" width="160" height="160" fill="{color_blue}" />
    <!-- Top right partial circle -->
    <shape type="circle" x="1400" y="-150" width="300" height="300" fill="{color_blue}" />
    <!-- Bottom left partial circle -->
    <shape type="circle" x="-100" y="750" width="250" height="250" fill="{color_blue}" />
    <!-- Big bottom curve (giant circle) -->
    <shape type="circle" x="500" y="450" width="1600" height="1600" fill="{color_blue}" />
    
    <!-- Logo -->
    <polygon points="120,220 150,150 180,220" fill="{color_light_blue}" />
    <polygon points="160,220 180,180 200,220" fill="{color_blue}" />
    <textbox x="220" y="140" width="300" height="80" font="Arial" size="28" color="{color_light_blue}" bold="true" align="left" vertical_align="middle" single_line="false" max_lines="2">{company_name}</textbox>
    
    <!-- Texts -->
    <textbox x="120" y="320" width="700" height="220" font="Arial" size="90" color="{color_dark_text}" bold="true" align="left" vertical_align="middle" single_line="false" max_lines="2" line_spacing="1.2">{title}</textbox>
    <textbox x="120" y="580" width="600" height="50" font="Arial" size="32" color="{color_dark_text}" bold="false" align="left" vertical_align="middle" single_line="true" max_lines="1">{subtitle}</textbox>
    
    <!-- Laptop Graphic -->
    <!-- Screen Bezel -->
    <shape type="rounded_rectangle" x="830" y="280" width="640" height="430" fill="#222222" />
    <!-- Screen Content (Image) -->
    <image src="{image_url.replace('&', '&amp;')}" x="850" y="310" width="600" height="380" />
    <!-- Laptop Base Top -->
    <shape type="rounded_rectangle" x="750" y="710" width="800" height="15" fill="#e0e0e0" />
    <!-- Laptop Base Bottom -->
    <shape type="rounded_rectangle" x="780" y="725" width="740" height="10" fill="#a0a0a0" />
  </slide>
</presentation>
"""
    return xml


def generate_outlook_dashboard_slide_xml(
    title: str = "2026 Outlook",
    subtitle: str = "Goals & Strategic Priorities",
    progress_cards: list = None,
    line_chart_title: str = "Increase AI-driven advisory adoption",
    line_chart_labels: list = None,
    line_chart_data: list = None,
    regional_title: str = "New Regional Market",
    regional_targets: list = None,
    bg_color: str = "#EEF2F6"
) -> str:
    """
    Generate XML for a dashboard slide containing progress cards, a line chart, and regional gauge charts.
    """
    import math
    import html as html_mod
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    if progress_cards is None:
        progress_cards = [
            {"title": "Expand ESG-focused\\nfunds", "percentage": 25, "card_color": "#F6BE00", "bar_color": "#4A6CF7", "text_color": "#FFFFFF"},
            {"title": "Enhance cybersecurity &\\ncompliance automation", "percentage": 100, "card_color": "#5A67D8", "bar_color": "#F6BE00", "text_color": "#FFFFFF"}
        ]
    if line_chart_labels is None:
        line_chart_labels = ["2021", "2022", "2023", "2024", "2025", "2026"]
    if line_chart_data is None:
        line_chart_data = [9, 10, 13, 20, 22, 30]
    if regional_targets is None:
        regional_targets = [
            {"name": "Target Regional 1", "region": "Vietnam", "percentage": 92, "color": "#F6BE00"},
            {"name": "Target Regional 2", "region": "USA", "percentage": 95, "color": "#FF4B4B"}
        ]

    canvas_w = 1600
    canvas_h = 900

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": str(canvas_w),
            "height": str(canvas_h),
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )
    slide = ET.SubElement(presentation, "slide", {"background": bg_color})

    def add_element(tag, **attrs):
        return ET.SubElement(slide, tag, {key: str(value) for key, value in attrs.items()})

    def add_textbox(text, **attrs):
        node = add_element("textbox", **attrs)
        node.text = text
        return node

    # Background
    add_element("shape", type="rect", x=0, y=0, width=canvas_w, height=canvas_h, fill=bg_color, line_color="none")

    # Title & Subtitle
    add_textbox(title, x=80, y=80, width=800, height=80, font="Arial", size=72, bold="true", color="#333333", align="left", vertical_align="middle", single_line="true")
    add_textbox(subtitle, x=80, y=170, width=800, height=40, font="Arial", size=32, bold="false", color="#555555", align="left", vertical_align="middle", single_line="true")

    # Abstract Map (Dots) & Markers
    map_x, map_y, map_w, map_h = 750, 40, 800, 350
    map_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {map_w} {map_h}" width="{map_w}" height="{map_h}">'
    
    # Simple dotted map generator
    map_pattern = [
        "                xx   x x                ",
        "             xxxxxx xxxxxx        xx    ",
        "            xxxxxxxxxxxxxxxx     xxxx   ",
        "           xxxxxxxxxxxxxxxxxx   xxxxxx  ",
        "            xxxxxxxxxxxxxxxxxxxxxxxxxx  ",
        "            xxxxxxxxxxxxxxxxxxxxxxxxxx  ",
        "             xx xxxxxxxxxxxxxxxxxxxxx   ",
        "              x  xxxx   xxxxxxxxxxx     ",
        "                 xxx     xxxxx xxxx     ",
        "                 xx       xxx   xx      ",
        "                  x              x      ",
        "                                 xx     "
    ]
    dot_r = 3
    spacing_x = 18
    spacing_y = 22
    for r, row in enumerate(map_pattern):
        for c, char in enumerate(row):
            if char == 'x':
                px = 50 + c * spacing_x
                py = 50 + r * spacing_y
                map_svg += f'<circle cx="{px}" cy="{py}" r="{dot_r}" fill="#999999" fill-opacity="0.5"/>'
    
    # Markers (USA and Vietnam approximations based on pattern)
    markers = [
        {"cx": 180, "cy": 160, "color": "#FF4B4B", "label": "USA"},
        {"cx": 620, "cy": 220, "color": "#F6BE00", "label": "Vietnam"}
    ]
    for m in markers:
        # Pill background
        map_svg += f'<rect x="{m["cx"]-20}" y="{m["cy"]-15}" width="120" height="30" rx="15" fill="#FFFFFF" filter="drop-shadow(0px 4px 4px rgba(0,0,0,0.1))"/>'
        # Dot
        map_svg += f'<circle cx="{m["cx"]}" cy="{m["cy"]}" r="10" fill="{m["color"]}" />'
        # Text
        map_svg += f'<text x="{m["cx"]+20}" y="{m["cy"]+5}" font-family="Arial" font-size="14" font-weight="bold" fill="#333333">{m["label"]}</text>'
        
    map_svg += '</svg>'
    map_el = add_element("shape", type="freeform", x=map_x, y=map_y, width=map_w, height=map_h, fill="none", line_color="none")
    map_el.set("svg_data", html_mod.escape(map_svg))

    # Progress Cards
    card_y = 250
    card_w = 400
    card_h = 180
    for i, card in enumerate(progress_cards):
        cx = 80 + i * (card_w + 30)
        # Card Background
        add_element("shape", type="roundRect", x=cx, y=card_y, width=card_w, height=card_h, fill=card["card_color"], line_color="none")
        # Title
        add_textbox(card["title"], x=cx+30, y=card_y+30, width=card_w-60, height=80, font="Arial", size=24, bold="false", color=card["text_color"], align="left", vertical_align="top", single_line="false")
        
        # Progress Bar track
        add_element("shape", type="roundRect", x=cx+30, y=card_y+115, width=220, height=25, fill="#FFFFFF", line_color="none")
        add_element("shape", type="roundRect", x=cx+30, y=card_y+115, width=220, height=25, fill="#000000", line_color="none") # Will overlay transparency
        # To make it look transparent white, we can just use a lighter version of the background or white with opacity. Since we can't easily do opacity in pure XML standard shapes, we just use a light grey.
        # Actually, let's just use a solid light color for the track.
        add_element("shape", type="roundRect", x=cx+30, y=card_y+115, width=220, height=25, fill="#E2E8F0", line_color="none")
        # Progress Bar fill
        fill_w = max(20, int(220 * card["percentage"] / 100))
        add_element("shape", type="roundRect", x=cx+30, y=card_y+115, width=fill_w, height=25, fill=card["bar_color"], line_color="none")
        
        # Percentage Text
        add_textbox(f"{card['percentage']}%", x=cx+270, y=card_y+105, width=100, height=45, font="Arial", size=32, bold="true", color=card["text_color"], align="left", vertical_align="middle", single_line="true")

    # Line Chart Card
    line_x, line_y, line_w, line_h = 80, 460, 750, 400
    add_element("shape", type="roundRect", x=line_x, y=line_y, width=line_w, height=line_h, fill="#FFFFFF", line_color="none")
    
    add_textbox(line_chart_title, x=line_x+40, y=line_y+30, width=line_w-80, height=40, font="Arial", size=24, bold="false", color="#333333", align="left", vertical_align="middle", single_line="true")
    
    # SVG Line Chart
    chart_svg_w, chart_svg_h = line_w - 60, line_h - 100
    chart_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {chart_svg_w} {chart_svg_h}" width="{chart_svg_w}" height="{chart_svg_h}">'
    
    # Grid and Y axis
    max_val = max(line_chart_data) if line_chart_data else 30
    if max_val == 0: max_val = 1
    y_steps = 6
    grid_y_start = 20
    grid_y_end = chart_svg_h - 40
    chart_h_inner = grid_y_end - grid_y_start
    
    for i in range(y_steps + 1):
        y_val = i * (max_val / y_steps)
        py = grid_y_end - (i / y_steps) * chart_h_inner
        chart_svg += f'<line x1="40" y1="{py}" x2="{chart_svg_w-20}" y2="{py}" stroke="#EEEEEE" stroke-width="1"/>'
        chart_svg += f'<text x="30" y="{py+5}" font-family="Arial" font-size="14" fill="#999999" text-anchor="end">{int(y_val)}</text>'
        
    # Line path
    num_pts = len(line_chart_data)
    dx = (chart_svg_w - 80) / (num_pts - 1) if num_pts > 1 else 0
    pts = []
    for i, val in enumerate(line_chart_data):
        px = 60 + i * dx
        py = grid_y_end - (val / max_val) * chart_h_inner
        pts.append((px, py))
        
    path_d = f"M {pts[0][0]} {pts[0][1]} "
    for i in range(1, num_pts):
        # Smooth bezier curve
        cp1x = pts[i-1][0] + dx * 0.4
        cp1y = pts[i-1][1]
        cp2x = pts[i][0] - dx * 0.4
        cp2y = pts[i][1]
        path_d += f"C {cp1x} {cp1y}, {cp2x} {cp2y}, {pts[i][0]} {pts[i][1]} "
        
    chart_svg += f'<path d="{path_d}" fill="none" stroke="#F6BE00" stroke-width="3"/>'
    
    # Points
    for px, py in pts:
        chart_svg += f'<circle cx="{px}" cy="{py}" r="4" fill="#F6BE00" />'
        
    # Highlight last point
    if pts:
        last_px, last_py = pts[-1]
        chart_svg += f'<circle cx="{last_px}" cy="{last_py}" r="12" fill="#F6BE00" fill-opacity="0.2"/>'
        chart_svg += f'<circle cx="{last_px}" cy="{last_py}" r="6" fill="#F6BE00" />'
        # Label box
        box_w, box_h = 70, 40
        chart_svg += f'<rect x="{last_px-box_w/2}" y="{last_py+15}" width="{box_w}" height="{box_h}" rx="8" fill="#F4F4F4" />'
        chart_svg += f'<text x="{last_px}" y="{last_py+40}" font-family="Arial" font-size="18" font-weight="bold" fill="#333333" text-anchor="middle">{line_chart_data[-1]}%</text>'

    # X axis labels
    for i, label in enumerate(line_chart_labels):
        px = 60 + i * dx
        chart_svg += f'<text x="{px}" y="{chart_svg_h - 10}" font-family="Arial" font-size="14" fill="#999999" text-anchor="middle">{label}</text>'

    chart_svg += '</svg>'
    chart_el = add_element("shape", type="freeform", x=line_x+30, y=line_y+80, width=chart_svg_w, height=chart_svg_h, fill="none", line_color="none")
    chart_el.set("svg_data", html_mod.escape(chart_svg))

    # Regional Market Card
    reg_x, reg_y, reg_w, reg_h = 860, 460, 680, 400
    
    add_textbox(regional_title, x=reg_x, y=reg_y-40, width=reg_w, height=40, font="Arial", size=24, bold="false", color="#555555", align="left", vertical_align="middle", single_line="true")
    add_element("shape", type="roundRect", x=reg_x, y=reg_y, width=reg_w, height=reg_h, fill="#8B5CF6", line_color="none")
    
    gauge_svg_w, gauge_svg_h = reg_w, reg_h
    gauge_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {gauge_svg_w} {gauge_svg_h}" width="{gauge_svg_w}" height="{gauge_svg_h}">'
    
    # Gauges
    start_y = 60
    for i, t in enumerate(regional_targets):
        gy = start_y + i * 160
        # Text
        gauge_svg += f'<text x="50" y="{gy + 20}" font-family="Arial" font-size="24" fill="#FFFFFF">{t["name"]}</text>'
        gauge_svg += f'<circle cx="65" cy="{gy + 65}" r="4" fill="#FFFFFF" />'
        gauge_svg += f'<text x="80" y="{gy + 72}" font-family="Arial" font-size="20" fill="#E2E8F0">{t["region"]}</text>'
        
        # Half Donut (Gauge)
        gcx, gcy = 500, gy + 100
        rout = 80
        rin = 50
        
        # Background arc (grayish)
        gauge_svg += f'<path d="M {gcx-rout} {gcy} A {rout} {rout} 0 0 1 {gcx+rout} {gcy} L {gcx+rin} {gcy} A {rin} {rin} 0 0 0 {gcx-rin} {gcy} Z" fill="#F1F5F9" fill-opacity="0.8"/>'
        
        # Foreground arc
        val = t["percentage"] / 100
        angle = math.pi - (val * math.pi)
        px_out = gcx + rout * math.cos(angle)
        py_out = gcy - rout * math.sin(angle)
        px_in = gcx + rin * math.cos(angle)
        py_in = gcy - rin * math.sin(angle)
        
        gauge_svg += f'<path d="M {gcx-rout} {gcy} A {rout} {rout} 0 0 1 {px_out} {py_out} L {px_in} {py_in} A {rin} {rin} 0 0 0 {gcx-rin} {gcy} Z" fill="{t["color"]}"/>'
        
        # Percentage text
        gauge_svg += f'<text x="{gcx}" y="{gcy - 15}" font-family="Arial" font-size="28" fill="#FFFFFF" text-anchor="middle">{t["percentage"]}%</text>'
        
    gauge_svg += '</svg>'
    gauge_el = add_element("shape", type="freeform", x=reg_x, y=reg_y, width=gauge_svg_w, height=gauge_svg_h, fill="none", line_color="none")
    gauge_el.set("svg_data", html_mod.escape(gauge_svg))

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    return xml_content



def generate_performance_review_slide_xml(
    title: str = "ÄÃNH GIÃ HIá»†U SUáº¤T TOÃ€N DIá»†N",
    radar_labels: list = None,
    radar_series: list = None,
    area_labels: list = None,
    area_series: list = None,
    bullet_points: list = None,
    bg_color_top: str = "#FFFFFF",
    bg_color_bottom: str = "#F0F7FA",
    title_color: str = "#1E88E5",
    text_color: str = "#333333"
) -> str:
    """
    Generate XML for a performance review slide with a radar chart on the left and an area chart on the right.
    """
    import math
    import html as html_mod
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    if radar_labels is None:
        radar_labels = ["TÃ­nh nÄƒng", "Há»— trá»£", "Hiá»‡u quáº£ hoáº¡t Ä‘á»™ng", "Kháº£ nÄƒng sá»­ dá»¥ng", "GiÃ¡ trá»‹"]
    if radar_series is None:
        radar_series = [
            {"name": "TiÃªu chuáº©n", "data": [4, 3, 5, 6, 7], "color": "#42A5F5"},
            {"name": "Cao cáº¥p", "data": [8, 5, 8, 8, 4], "color": "#26C6DA"},
            {"name": "Sang trá»ng", "data": [9, 7, 5, 6, 5], "color": "#F48FB1"}
        ]
    if area_labels is None:
        area_labels = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"]
    if area_series is None:
        area_series = [
            {"name": "MÃ¡y tÃ­nh Ä‘á»ƒ bÃ n", "data": [0, 15, 20, 30, 31, 32, 30, 25, 12, 8, 2, 0], "color": "#42A5F5"},
            {"name": "Thiáº¿t bá»‹ di Ä‘á»™ng", "data": [0, 2, 8, 12, 23, 27, 40, 42, 48, 46, 24, 12], "color": "#F48FB1"}
        ]
    if bullet_points is None:
        bullet_points = [
            "DÃ²ng Ä‘Ã¡nh giÃ¡ vá» hiá»‡u suáº¥t",
            "DÃ²ng Ä‘Ã¡nh giÃ¡ vá» hiá»‡u suáº¥t",
            "DÃ²ng Ä‘Ã¡nh giÃ¡ vá» hiá»‡u suáº¥t"
        ]

    canvas_w = 1600
    canvas_h = 900

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": str(canvas_w),
            "height": str(canvas_h),
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )

    slide = ET.SubElement(
        presentation,
        "slide",
        {"background": bg_color_top},
    )

    def add_element(tag, **attrs):
        return ET.SubElement(slide, tag, {key: str(value) for key, value in attrs.items()})

    def add_textbox(text, **attrs):
        node = add_element("textbox", **attrs)
        node.text = text
        return node

    # Background bottom
    add_element("shape", type="rect", x=0, y=140, width=canvas_w, height=canvas_h-140, fill=bg_color_bottom, line_color="none")

    # Title decor
    add_element("shape", type="rect", x=40, y=40, width=60, height=60, fill="#1E88E5", line_color="none")
    add_element("shape", type="rect", x=110, y=40, width=10, height=60, fill="#F48FB1", line_color="none")

    # Title
    add_textbox(
        title.upper(),
        x=140, y=40, width=1400, height=60,
        font="Arial", size=48, bold="true", color=title_color,
        align="left", vertical_align="middle", single_line="true"
    )

    # RADAR CHART (Left)
    radar_cx, radar_cy = 450, 520
    radar_r = 250
    radar_max = 10
    
    svg_radar = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_w} {canvas_h}" width="{canvas_w}" height="{canvas_h}">'
    
    # Legend for Radar
    leg_x = 200
    leg_y = 180
    for s in radar_series:
        svg_radar += f'<circle cx="{leg_x}" cy="{leg_y}" r="8" fill="{s["color"]}" />'
        svg_radar += f'<text x="{leg_x+15}" y="{leg_y+5}" font-family="Arial" font-size="20" fill="#333">{s["name"]}</text>'
        leg_x += 180

    num_axes = len(radar_labels)
    angles = [i * 2 * math.pi / num_axes - math.pi / 2 for i in range(num_axes)]

    # Draw grid (polygons)
    for step in range(2, radar_max + 1, 2):
        r_step = (step / radar_max) * radar_r
        pts = []
        for angle in angles:
            px = radar_cx + r_step * math.cos(angle)
            py = radar_cy + r_step * math.sin(angle)
            pts.append(f"{px},{py}")
        svg_radar += f'<polygon points="{" ".join(pts)}" fill="none" stroke="#CCCCCC" stroke-dasharray="4,4" stroke-width="1"/>'
        # Add label for grid
        svg_radar += f'<text x="{radar_cx}" y="{radar_cy - r_step + 15}" font-family="Arial" font-size="14" fill="#666" text-anchor="middle">{step}</text>'
    
    # Draw axes
    for i, angle in enumerate(angles):
        px = radar_cx + radar_r * math.cos(angle)
        py = radar_cy + radar_r * math.sin(angle)
        svg_radar += f'<line x1="{radar_cx}" y1="{radar_cy}" x2="{px}" y2="{py}" stroke="#CCCCCC" stroke-dasharray="4,4" stroke-width="1"/>'
        
        # Label alignment
        anchor = "middle"
        dx, dy = 0, 0
        if math.cos(angle) > 0.1: anchor = "start"; dx = 10
        elif math.cos(angle) < -0.1: anchor = "end"; dx = -10
        if math.sin(angle) > 0.1: dy = 25
        elif math.sin(angle) < -0.1: dy = -10
        svg_radar += f'<text x="{px+dx}" y="{py+dy}" font-family="Arial" font-size="18" fill="#333" text-anchor="{anchor}">{radar_labels[i]}</text>'

    # Draw data polygons
    for s in radar_series:
        pts = []
        for i, val in enumerate(s["data"]):
            r_val = (val / radar_max) * radar_r
            px = radar_cx + r_val * math.cos(angles[i])
            py = radar_cy + r_val * math.sin(angles[i])
            pts.append(f"{px},{py}")
        svg_radar += f'<polygon points="{" ".join(pts)}" fill="{s["color"]}" fill-opacity="0.4" stroke="{s["color"]}" stroke-width="2"/>'

    # AREA CHART (Right)
    area_x, area_y = 950, 250
    area_w, area_h = 600, 400
    area_max = 50

    # Legend for Area
    leg_x = 1000
    leg_y = 180
    for s in area_series:
        svg_radar += f'<circle cx="{leg_x}" cy="{leg_y}" r="6" fill="{s["color"]}" />'
        svg_radar += f'<text x="{leg_x+15}" y="{leg_y+5}" font-family="Arial" font-size="16" fill="#333">{s["name"]}</text>'
        leg_x += 160

    # Area Grid
    for step in range(0, area_max + 1, 10):
        y_pos = area_y + area_h - (step / area_max) * area_h
        svg_radar += f'<line x1="{area_x}" y1="{y_pos}" x2="{area_x+area_w}" y2="{y_pos}" stroke="#DDDDDD" stroke-width="1"/>'
        svg_radar += f'<text x="{area_x-10}" y="{y_pos+5}" font-family="Arial" font-size="14" fill="#666" text-anchor="end">{step}</text>'

    # Area Paths
    num_pts = len(area_labels)
    dx = area_w / (num_pts - 1) if num_pts > 1 else area_w
    for s in area_series:
        path_d = f"M {area_x} {area_y + area_h} "
        for i, val in enumerate(s["data"]):
            px = area_x + i * dx
            py = area_y + area_h - (val / area_max) * area_h
            path_d += f"L {px} {py} "
        path_d += f"L {area_x + area_w} {area_y + area_h} Z"
        svg_radar += f'<path d="{path_d}" fill="{s["color"]}" fill-opacity="0.6" stroke="{s["color"]}" stroke-width="2"/>'

    # Area X labels
    for i, label in enumerate(area_labels):
        px = area_x + i * dx
        svg_radar += f'<text x="{px}" y="{area_y + area_h + 20}" font-family="Arial" font-size="14" fill="#333" text-anchor="middle">{label}</text>'

    svg_radar += '</svg>'
    
    chart_el = add_element("shape", type="freeform", x=0, y=0, width=canvas_w, height=canvas_h, fill="none", line_color="none")
    chart_el.set("svg_data", html_mod.escape(svg_radar))

    # Bullet Points (Bottom Right)
    bullet_y = 700
    for bullet in bullet_points:
        add_element("shape", type="oval", x=950, y=bullet_y+12, width=10, height=10, fill="#555555", line_color="none")
        add_textbox(
            bullet,
            x=980, y=bullet_y, width=580, height=40,
            font="Arial", size=28, bold="true", italic="true", color="#444444",
            align="left", vertical_align="middle", single_line="true"
        )
        bullet_y += 45

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    return xml_content



def generate_kpi_dashboard_slide_xml(
    title: str = "Primary KPI Dashboard",
    kpi_cards: list = None,
    chart_labels: list = None,
    chart_data: list = None,
    bg_color: str = "#F8F9FA"
) -> str:
    """
    Generate XML for a KPI dashboard slide with left-side progress cards and a right-side line chart.
    """
    import html as html_mod
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    if kpi_cards is None:
        kpi_cards = [
            {"title": "Revenue\\nand Sales", "percentage": 72, "color": "#F26D60"},
            {"title": "Achieved\\nConversion Rate", "percentage": 60, "color": "#E85EAE"},
            {"title": "Customer\\nRetention", "percentage": 86, "color": "#3BBA77"}
        ]
    if chart_labels is None:
        chart_labels = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    if chart_data is None:
        chart_data = [200, 700, 600, 900, 300, 600, 900, 250, 600, 500, 700, 600]

    canvas_w = 1600
    canvas_h = 900

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": str(canvas_w),
            "height": str(canvas_h),
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )
    slide = ET.SubElement(presentation, "slide", {"background": bg_color})

    def add_element(tag, **attrs):
        return ET.SubElement(slide, tag, {key: str(value) for key, value in attrs.items()})

    def add_textbox(text, **attrs):
        node = add_element("textbox", **attrs)
        node.text = text
        return node

    # Background
    add_element("shape", type="rect", x=0, y=0, width=canvas_w, height=canvas_h, fill=bg_color, line_color="none")

    # Abstract dots background (Top right and Bottom left)
    dot_color = "#FAD2D2"
    dot_r = 8
    spacing = 25
    # Top right cluster
    for r in range(8):
        for c in range(15):
            if (r+c) > 6 and (c-r) > 2:
                add_element("shape", type="oval", x=1200 + c*spacing, y=-50 + r*spacing, width=dot_r, height=dot_r, fill=dot_color, line_color="none")
    
    # Bottom left cluster
    for r in range(12):
        for c in range(8):
            if (r-c) > 2:
                add_element("shape", type="oval", x=-50 + c*spacing, y=600 + r*spacing, width=dot_r, height=dot_r, fill=dot_color, line_color="none")

    # Title Area
    add_element("shape", type="roundRect", x=600, y=100, width=100, height=10, fill="#F26D60", line_color="none")
    add_textbox(title, x=600, y=140, width=900, height=80, font="Segoe UI", size=64, bold="true", color="#111111", align="left", vertical_align="middle", single_line="true")

    # Left KPI Cards
    card_x = 80
    card_w = 450
    card_h = 220
    
    for i, card in enumerate(kpi_cards):
        cy = 80 + i * (card_h + 40)
        
        # Add shadow simulation (slightly offset light grey rect)
        add_element("shape", type="roundRect", x=card_x+5, y=cy+5, width=card_w, height=card_h, fill="#E2E8F0", line_color="none")
        # Card body
        add_element("shape", type="roundRect", x=card_x, y=cy, width=card_w, height=card_h, fill="#FFFFFF", line_color="none")
        
        # Text
        add_textbox(card["title"], x=card_x+40, y=cy+40, width=220, height=80, font="Segoe UI", size=26, bold="true", color="#222222", align="left", vertical_align="top", single_line="false")
        
        # Percentage
        add_textbox(f"{card['percentage']}%", x=card_x+250, y=cy+35, width=160, height=80, font="Segoe UI", size=54, bold="true", color=card["color"], align="right", vertical_align="top", single_line="true")
        
        # Progress Bar
        bar_y = cy + 140
        bar_w = 370
        bar_h = 28
        # Track
        add_element("shape", type="roundRect", x=card_x+40, y=bar_y, width=bar_w, height=bar_h, fill="#F1F5F9", line_color="none")
        # Fill
        fill_w = max(20, int(bar_w * card["percentage"] / 100))
        add_element("shape", type="roundRect", x=card_x+40, y=bar_y, width=fill_w, height=bar_h, fill=card["color"], line_color="none")

    # Right Chart Card
    chart_bg_x, chart_bg_y, chart_bg_w, chart_bg_h = 600, 340, 920, 480
    add_element("shape", type="roundRect", x=chart_bg_x+5, y=chart_bg_y+5, width=chart_bg_w, height=chart_bg_h, fill="#E2E8F0", line_color="none")
    add_element("shape", type="roundRect", x=chart_bg_x, y=chart_bg_y, width=chart_bg_w, height=chart_bg_h, fill="#FFFFFF", line_color="none")
    
    # Chart SVG
    svg_w, svg_h = chart_bg_w - 60, chart_bg_h - 60
    svg_x, svg_y = chart_bg_x + 30, chart_bg_y + 30
    chart_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'
    
    max_val = max(chart_data) if chart_data else 1000
    if max_val == 0: max_val = 1
    # Round max_val up to nearest nice number (e.g. 1000)
    import math
    pow10 = 10 ** math.floor(math.log10(max_val))
    max_val = math.ceil(max_val / pow10) * pow10
    if max_val == max(chart_data) and max_val > 10:
        max_val += pow10

    grid_y_start = 20
    grid_y_end = svg_h - 40
    chart_h_inner = grid_y_end - grid_y_start
    
    y_steps = 5
    for i in range(y_steps + 1):
        y_val = i * (max_val / y_steps)
        py = grid_y_end - (i / y_steps) * chart_h_inner
        chart_svg += f'<line x1="60" y1="{py}" x2="{svg_w-20}" y2="{py}" stroke="#E2E8F0" stroke-width="1"/>'
        chart_svg += f'<text x="50" y="{py+5}" font-family="Arial" font-size="16" fill="#555555" text-anchor="end">{int(y_val)}</text>'
        
    num_pts = len(chart_data)
    dx = (svg_w - 100) / (num_pts - 1) if num_pts > 1 else 0
    pts = []
    for i, val in enumerate(chart_data):
        px = 80 + i * dx
        py = grid_y_end - (val / max_val) * chart_h_inner
        pts.append((px, py))
        
    # Line
    if pts:
        path_d = f"M {pts[0][0]} {pts[0][1]} "
        for i in range(1, num_pts):
            path_d += f"L {pts[i][0]} {pts[i][1]} "
        chart_svg += f'<path d="{path_d}" fill="none" stroke="#2B5FEA" stroke-width="6"/>'
        
        # Dots
        for px, py in pts:
            chart_svg += f'<circle cx="{px}" cy="{py}" r="10" fill="#2B5FEA" />'

    # X axis labels
    for i, label in enumerate(chart_labels):
        px = 80 + i * dx
        chart_svg += f'<text x="{px}" y="{svg_h - 10}" font-family="Arial" font-size="16" fill="#555555" text-anchor="middle">{label}</text>'

    chart_svg += '</svg>'
    
    chart_el = add_element("shape", type="freeform", x=svg_x, y=svg_y, width=svg_w, height=svg_h, fill="none", line_color="none")
    chart_el.set("svg_data", html_mod.escape(chart_svg))

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    return xml_content



def generate_revenue_target_slide_xml(
    title: str = "Annual Revenue Target",
    top_left_card: dict = None,
    top_right_card: dict = None,
    bottom_card: dict = None,
    bar_chart_title: str = "Quarterly Revenue Data",
    bar_chart_labels: list = None,
    bar_chart_data: list = None,
    bg_color: str = "#F5F6F8"
) -> str:
    """
    Generate XML for an Annual Revenue Target slide with a donut chart and a bar chart.
    """
    import html as html_mod
    import xml.etree.ElementTree as ET
    import math
    from xml.dom import minidom

    if top_left_card is None:
        top_left_card = {"title": "Annual Target", "value": "$15M", "subtitle": "on track"}
    if top_right_card is None:
        top_right_card = {"title": "Forecast Q4", "value": "+6-8%", "subtitle": "projected growth"}
    if bottom_card is None:
        bottom_card = {"title": "Current YTD (Q3)", "value": "$11.2M", "subtitle": "74% achieved", "percentage": 74}
    if bar_chart_labels is None:
        bar_chart_labels = ["Q1", "Q2", "Q3", "Q4"]
    if bar_chart_data is None:
        bar_chart_data = [3, 4, 6, 4]

    canvas_w = 1600
    canvas_h = 900

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": str(canvas_w),
            "height": str(canvas_h),
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )
    slide = ET.SubElement(presentation, "slide", {"background": bg_color})

    def add_element(tag, **attrs):
        return ET.SubElement(slide, tag, {key: str(value) for key, value in attrs.items()})

    def add_textbox(text, **attrs):
        node = add_element("textbox", **attrs)
        node.text = text
        return node

    # Background
    add_element("shape", type="rect", x=0, y=0, width=canvas_w, height=canvas_h, fill=bg_color, line_color="none")

    # Abstract background wave simulation (just soft circles in corners)
    add_element("shape", type="oval", x=1300, y=-200, width=500, height=500, fill="#Eef0f4", line_color="#E2e6ec")
    add_element("shape", type="oval", x=1400, y=-100, width=400, height=400, fill="#Eef0f4", line_color="#E2e6ec")
    add_element("shape", type="oval", x=-200, y=700, width=400, height=400, fill="#Eef0f4", line_color="#E2e6ec")

    # Title
    add_textbox(title, x=80, y=80, width=1000, height=80, font="Segoe UI", size=60, bold="true", color="#16333F", align="left", vertical_align="middle", single_line="true")

    # Cards Base Layout
    card_y_top = 220
    card_y_bot = 530
    
    # Top Left Card
    tl_x = 80
    add_element("shape", type="roundRect", x=tl_x, y=card_y_top, width=340, height=280, fill="#0A93A6", line_color="none")
    # Icon Box
    add_element("shape", type="roundRect", x=tl_x+30, y=card_y_top+30, width=50, height=50, fill="#FCE679", line_color="none")
    add_textbox("+", x=tl_x+30, y=card_y_top+30, width=50, height=50, font="Segoe UI", size=32, bold="true", color="#0A93A6", align="center", vertical_align="middle", single_line="true")
    add_textbox(top_left_card["title"], x=tl_x+30, y=card_y_top+120, width=280, height=40, font="Segoe UI", size=22, bold="false", color="#B2DFDB", align="left", vertical_align="middle", single_line="true")
    add_textbox(top_left_card["value"], x=tl_x+30, y=card_y_top+160, width=280, height=60, font="Segoe UI", size=48, bold="true", color="#FFFFFF", align="left", vertical_align="middle", single_line="true")
    add_textbox(top_left_card["subtitle"], x=tl_x+30, y=card_y_top+220, width=280, height=30, font="Segoe UI", size=18, bold="false", color="#B2DFDB", align="left", vertical_align="middle", single_line="true")

    # Top Right Card
    tr_x = 450
    add_element("shape", type="roundRect", x=tr_x, y=card_y_top, width=340, height=280, fill="#0A93A6", line_color="none")
    add_element("shape", type="roundRect", x=tr_x+30, y=card_y_top+30, width=50, height=50, fill="#FCE679", line_color="none")
    # A fire/flame symbol or triangle
    add_textbox("â–²", x=tr_x+30, y=card_y_top+30, width=50, height=50, font="Segoe UI", size=24, bold="true", color="#0A93A6", align="center", vertical_align="middle", single_line="true")
    add_textbox(top_right_card["title"], x=tr_x+30, y=card_y_top+120, width=280, height=40, font="Segoe UI", size=22, bold="false", color="#B2DFDB", align="left", vertical_align="middle", single_line="true")
    add_textbox(top_right_card["value"], x=tr_x+30, y=card_y_top+160, width=280, height=60, font="Segoe UI", size=48, bold="true", color="#FFFFFF", align="left", vertical_align="middle", single_line="true")
    add_textbox(top_right_card["subtitle"], x=tr_x+30, y=card_y_top+220, width=280, height=30, font="Segoe UI", size=18, bold="false", color="#B2DFDB", align="left", vertical_align="middle", single_line="true")

    # Bottom Card
    add_element("shape", type="roundRect", x=80, y=card_y_bot, width=710, height=300, fill="#FFFFFF", line_color="#E2E8F0")
    add_element("shape", type="roundRect", x=110, y=card_y_bot+30, width=50, height=50, fill="#0D7685", line_color="none")
    # Clock symbol or circle
    add_textbox("âŠ™", x=110, y=card_y_bot+30, width=50, height=50, font="Segoe UI", size=28, bold="true", color="#FCE679", align="center", vertical_align="middle", single_line="true")
    add_textbox(bottom_card["title"], x=110, y=card_y_bot+120, width=280, height=40, font="Segoe UI", size=22, bold="false", color="#555555", align="left", vertical_align="middle", single_line="true")
    add_textbox(bottom_card["value"], x=110, y=card_y_bot+160, width=280, height=60, font="Segoe UI", size=48, bold="true", color="#111111", align="left", vertical_align="middle", single_line="true")
    add_textbox(bottom_card["subtitle"], x=110, y=card_y_bot+220, width=280, height=30, font="Segoe UI", size=18, bold="false", color="#888888", align="left", vertical_align="middle", single_line="true")

    # Donut Chart SVG
    donut_pct = bottom_card.get("percentage", 75)
    donut_w, donut_h = 240, 240
    donut_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {donut_w} {donut_h}" width="{donut_w}" height="{donut_h}">'
    cx, cy, r = donut_w//2, donut_h//2, 85
    circum = 2 * math.pi * r
    fill_len = (donut_pct / 100) * circum
    
    donut_svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#FDE68A" stroke-width="35"/>'
    donut_svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0D7685" stroke-width="35" stroke-dasharray="{fill_len} {circum}" transform="rotate(-90 {cx} {cy})"/>'
    donut_svg += f'<text x="{cx}" y="{cy+15}" font-family="Arial" font-size="44" font-weight="bold" fill="#111111" text-anchor="middle">{donut_pct}%</text>'
    donut_svg += '</svg>'
    
    donut_el = add_element("shape", type="freeform", x=480, y=card_y_bot+30, width=donut_w, height=donut_h, fill="none", line_color="none")
    donut_el.set("svg_data", html_mod.escape(donut_svg))

    # Right Bar Chart Card
    chart_bg_x, chart_bg_y, chart_bg_w, chart_bg_h = 820, 220, 700, 610
    add_element("shape", type="roundRect", x=chart_bg_x, y=chart_bg_y, width=chart_bg_w, height=chart_bg_h, fill="#FFFFFF", line_color="#E2E8F0")
    add_textbox(bar_chart_title, x=chart_bg_x+40, y=chart_bg_y+30, width=600, height=40, font="Segoe UI", size=24, bold="false", color="#333333", align="left", vertical_align="middle", single_line="true")
    add_textbox("Amount (in millions)", x=chart_bg_x-40, y=chart_bg_y+250, width=300, height=40, font="Segoe UI", size=18, bold="false", color="#777777", align="center", vertical_align="middle", single_line="true")
    # In presentation tools it's hard to rotate standard text box accurately without full transform support, we will just use SVG for rotated text
    
    svg_w, svg_h = chart_bg_w - 60, chart_bg_h - 100
    svg_x, svg_y = chart_bg_x + 30, chart_bg_y + 80
    chart_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="{svg_w}" height="{svg_h}">'
    
    # Rotated Y-axis label
    chart_svg += f'<text x="-{svg_h//2 + 50}" y="30" font-family="Arial" font-size="20" fill="#777777" transform="rotate(-90)" text-anchor="middle">Amount (in millions)</text>'

    max_val = max(bar_chart_data) if bar_chart_data else 6
    if max_val == 0: max_val = 1
    import math
    max_val = math.ceil(max_val)

    grid_y_start = 20
    grid_y_end = svg_h - 40
    chart_h_inner = grid_y_end - grid_y_start
    
    # Draw Y axis grid
    for i in range(max_val + 1):
        py = grid_y_end - (i / max_val) * chart_h_inner
        chart_svg += f'<line x1="80" y1="{py}" x2="{svg_w-20}" y2="{py}" stroke="#E2E8F0" stroke-width="1"/>'
        chart_svg += f'<text x="60" y="{py+5}" font-family="Arial" font-size="18" fill="#555555" text-anchor="end">{i}</text>'
        
    num_bars = len(bar_chart_data)
    if num_bars > 0:
        bar_w = 80
        dx = (svg_w - 120) / num_bars
        colors = ["#63DFD8", "#06B6D4", "#0493A6", "#0D6F82", "#105563", "#16333F"]
        
        for i, val in enumerate(bar_chart_data):
            bx = 100 + i * dx + (dx - bar_w) / 2
            bh = (val / max_val) * chart_h_inner
            by = grid_y_end - bh
            color = colors[i % len(colors)]
            chart_svg += f'<rect x="{bx}" y="{by}" width="{bar_w}" height="{bh}" fill="{color}" rx="5" />'
            
            # X label
            if i < len(bar_chart_labels):
                chart_svg += f'<text x="{bx + bar_w/2}" y="{svg_h - 10}" font-family="Arial" font-size="18" fill="#555555" text-anchor="middle">{bar_chart_labels[i]}</text>'

    chart_svg += '</svg>'
    
    chart_el = add_element("shape", type="freeform", x=svg_x, y=svg_y, width=svg_w, height=svg_h, fill="none", line_color="none")
    chart_el.set("svg_data", html_mod.escape(chart_svg))

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    return xml_content



def generate_modern_donut_chart_slide_xml(
    title: str = "NGUá»’N Lá»°C DOANH THU",
    chart_labels: list = None,
    chart_data: list = None,
    colors: list = None,
    background_color: str = "#F3FBFE",
    title_color: str = "#4B61FF",
    text_color: str = "#FFFFFF"
) -> str:
    """
    Generate XML for a modern donut chart slide with horizontal label bars on the right.
    """
    import math
    import html as html_mod
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    if chart_labels is None:
        chart_labels = ["KhÃ¡ch hÃ ng doanh nghiá»‡p", "KhÃ¡ch hÃ ng cÃ¡ nhÃ¢n", "Äáº¡i lÃ½ & Ä‘á»‘i tÃ¡c", "KhÃ¡ch hÃ ng dá»± Ã¡n"]
    if chart_data is None:
        chart_data = [45, 30, 15, 10]
    if colors is None:
        colors = ["#00E5FF", "#0099FF", "#9D84FF", "#6E5BFF"]
        
    canvas_w = 1600
    canvas_h = 900

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": str(canvas_w),
            "height": str(canvas_h),
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )

    slide = ET.SubElement(
        presentation,
        "slide",
        {"background": background_color},
    )

    def add_element(tag, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {key: str(value) for key, value in attrs.items()},
        )

    def add_textbox(text, **attrs):
        node = add_element("textbox", **attrs)
        node.text = text
        return node

    # Background
    add_element(
        "shape",
        type="rect",
        x=0, y=0,
        width=canvas_w, height=canvas_h,
        fill=background_color,
        line_color="none",
    )

    # Title
    add_textbox(
        title.upper(),
        x=80, y=80,
        width=1440, height=100,
        font="Arial", size=64, bold="true", color=title_color,
        align="center", vertical_align="middle", single_line="true"
    )

    # Calculate Donut Chart SVG
    donut_x = 100
    donut_y = 230
    donut_w = 650
    donut_h = 650
    cx, cy = donut_w / 2, donut_h / 2
    r_out = 300
    r_in = 150

    total = sum(chart_data)
    if total == 0:
        total = 1
    
    svg_chart = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {donut_w} {donut_h}" width="{donut_w}" height="{donut_h}">'
    
    current_angle = -math.pi / 2  # Start at top
    for val, color in zip(chart_data, colors):
        angle = (val / total) * 2 * math.pi
        
        x1_out = cx + r_out * math.cos(current_angle)
        y1_out = cy + r_out * math.sin(current_angle)
        x2_out = cx + r_out * math.cos(current_angle + angle)
        y2_out = cy + r_out * math.sin(current_angle + angle)
        
        x1_in = cx + r_in * math.cos(current_angle)
        y1_in = cy + r_in * math.sin(current_angle)
        x2_in = cx + r_in * math.cos(current_angle + angle)
        y2_in = cy + r_in * math.sin(current_angle + angle)
        
        large_arc = 1 if angle > math.pi else 0
        
        path_d = (
            f"M {x1_in} {y1_in} "
            f"L {x1_out} {y1_out} "
            f"A {r_out} {r_out} 0 {large_arc} 1 {x2_out} {y2_out} "
            f"L {x2_in} {y2_in} "
            f"A {r_in} {r_in} 0 {large_arc} 0 {x1_in} {y1_in} Z"
        )
        if val == total:
            path_d = (
                f"M {cx} {cy - r_out} "
                f"A {r_out} {r_out} 0 1 1 {cx} {cy + r_out} "
                f"A {r_out} {r_out} 0 1 1 {cx} {cy - r_out} "
                f"M {cx} {cy - r_in} "
                f"A {r_in} {r_in} 0 1 0 {cx} {cy + r_in} "
                f"A {r_in} {r_in} 0 1 0 {cx} {cy - r_in} Z"
            )
        
        svg_chart += f'<path d="{path_d}" fill="{color}" />'
        current_angle += angle
        
    svg_chart += '</svg>'
    
    chart_el = add_element("shape", type="freeform", x=donut_x, y=donut_y, width=donut_w, height=donut_h, fill="none", line_color="none")
    chart_el.set("svg_data", html_mod.escape(svg_chart))

    # Right side horizontal bars
    bar_x = 820
    bar_y_start = 280
    bar_w = 680
    bar_h = 100
    spacing = 130
    
    for i, (label, val, color) in enumerate(zip(chart_labels, chart_data, colors)):
        y_pos = bar_y_start + i * spacing
        
        # Draw rounded rect for the bar
        add_element(
            "shape",
            type="roundRect",
            x=bar_x, y=y_pos,
            width=bar_w, height=bar_h,
            fill=color,
            line_color="none",
        )
        
        # The percentage text
        percentage_text = f"{val:g} %"
        add_textbox(
            percentage_text,
            x=bar_x + 30, y=y_pos + 10,
            width=200, height=80,
            font="Arial", size=56, bold="true", color=text_color,
            align="left", vertical_align="middle", single_line="true"
        )
        
        # The label text
        add_textbox(
            label,
            x=bar_x + 220, y=y_pos + 25,
            width=430, height=50,
            font="Arial", size=26, bold="true", color=text_color,
            align="left", vertical_align="middle", single_line="true"
        )

    # Decorative buildings
    building_svg_left = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 400" width="200" height="400">'
        f'<path d="M0 400 L0 250 L40 250 L40 180 L160 180 L160 250 L200 250 L200 400 Z" fill="#9D84FF" opacity="0.15"/>'
        f'<rect x="20" y="200" width="160" height="200" fill="#00E5FF" opacity="0.3" rx="40"/>'
        f'<rect x="40" y="220" width="120" height="180" fill="#FFFFFF" opacity="0.4" rx="20"/>'
        f'<line x1="100" y1="220" x2="100" y2="400" stroke="#0099FF" stroke-width="4" opacity="0.3"/>'
        f'<line x1="40" y1="260" x2="160" y2="260" stroke="#0099FF" stroke-width="4" opacity="0.3"/>'
        f'<line x1="40" y1="300" x2="160" y2="300" stroke="#0099FF" stroke-width="4" opacity="0.3"/>'
        f'<line x1="40" y1="340" x2="160" y2="340" stroke="#0099FF" stroke-width="4" opacity="0.3"/>'
        f'<line x1="40" y1="380" x2="160" y2="380" stroke="#0099FF" stroke-width="4" opacity="0.3"/>'
        f'</svg>'
    )
    bldg_left = add_element("shape", type="freeform", x=0, y=550, width=180, height=350, fill="none", line_color="none")
    bldg_left.set("svg_data", html_mod.escape(building_svg_left))

    building_svg_right = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 400" width="200" height="400">'
        f'<path d="M0 400 L0 280 L40 280 L40 200 L160 200 L160 280 L200 280 L200 400 Z" fill="#9D84FF" opacity="0.15"/>'
        f'<rect x="20" y="220" width="160" height="180" fill="#0099FF" opacity="0.3" rx="40"/>'
        f'<rect x="40" y="240" width="120" height="160" fill="#FFFFFF" opacity="0.4" rx="20"/>'
        f'<line x1="100" y1="240" x2="100" y2="400" stroke="#6E5BFF" stroke-width="4" opacity="0.3"/>'
        f'<line x1="40" y1="280" x2="160" y2="280" stroke="#6E5BFF" stroke-width="4" opacity="0.3"/>'
        f'<line x1="40" y1="320" x2="160" y2="320" stroke="#6E5BFF" stroke-width="4" opacity="0.3"/>'
        f'<line x1="40" y1="360" x2="160" y2="360" stroke="#6E5BFF" stroke-width="4" opacity="0.3"/>'
        f'</svg>'
    )
    bldg_right = add_element("shape", type="freeform", x=1420, y=550, width=180, height=350, fill="none", line_color="none")
    bldg_right.set("svg_data", html_mod.escape(building_svg_right))

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    return xml_content



def generate_analysis_story_slide_xml(
    title: str = "PHÃ‚N TÃCH & CÃ‚U CHUYá»†N",
    badge_text: str = "BÃO CÃO",
    chart_title: str = "KPI cÃ¡c thÃ¡ng",
    chart_labels: list = None,
    chart_data: list = None,
    insights_title: str = "Nháº­n Ä‘á»‹nh chÃ­nh",
    insights: list = None,
    conclusion_text: str = "Káº¿t luáº­n: ÄÃ¢y lÃ  cÃ¢u káº¿t ngáº¯n gá»n, nháº¥n máº¡nh thÃ´ng Ä‘iá»‡p chÃ­nh vÃ  Ä‘á»‹nh hÆ°á»›ng tiáº¿p theo.",
    footer_text: str = "BÃ¡o cÃ¡o dá»± Ã¡n",
    page_number: str = "06",
    background_color: str = "#FFFFFF",
    primary_color: str = "#0B114F",
    secondary_color: str = "#4B7BFF",
    light_bg_color: str = "#EEF4FF",
    text_color: str = "#333333"
) -> str:
    """
    Generate XML for an Analysis & Story slide with a bar chart and key takeaways.
    """
    import html as html_mod
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    if chart_labels is None:
        chart_labels = ["T1", "T2", "T3", "T4", "T5", "T6"]
    if chart_data is None:
        chart_data = [750, 1000, 1300, 800, 250, 1500]
    if insights is None:
        insights = [
            "ÄÃ¢y lÃ  nháº­n Ä‘á»‹nh Ä‘áº§u tiÃªn tá»« dá»¯ liá»‡u.",
            "ÄÃ¢y lÃ  nháº­n Ä‘á»‹nh thá»© hai, giáº£i thÃ­ch nguyÃªn nhÃ¢n hoáº·c yáº¿u tá»‘ áº£nh hÆ°á»Ÿng.",
            "ÄÃ¢y lÃ  nháº­n Ä‘á»‹nh thá»© ba, gá»£i Ã½ hÃ nh Ä‘á»™ng hoáº·c cÆ¡ há»™i cáº£i thiá»‡n."
        ]

    canvas_w = 1600
    canvas_h = 900

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": str(canvas_w),
            "height": str(canvas_h),
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )

    slide = ET.SubElement(
        presentation,
        "slide",
        {"background": background_color},
    )

    def add_element(tag, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {key: str(value) for key, value in attrs.items()},
        )

    def add_textbox(text, **attrs):
        node = add_element("textbox", **attrs)
        node.text = text
        return node

    # Background shape
    add_element(
        "shape",
        type="rect",
        x=0, y=0,
        width=canvas_w, height=canvas_h,
        fill=background_color,
        line_color="none",
    )

    # Decorative swooshes on bottom right
    svg_bg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="1600" height="900">'
        f'<path d="M1200 900 Q1250 700 1600 550 L1600 900 Z" fill="{light_bg_color}" opacity="0.8"/>'
        f'<path d="M1350 900 Q1450 750 1600 650 L1600 900 Z" fill="{secondary_color}" opacity="0.9"/>'
        f'<path d="M1450 900 Q1500 800 1600 700 L1600 900 Z" fill="{primary_color}"/>'
        f'</svg>'
    )
    svg_bg_el = add_element("shape", type="freeform", x=0, y=0, width=1600, height=900, fill="none", line_color="none")
    svg_bg_el.set("svg_data", html_mod.escape(svg_bg))

    # Badge
    badge_w = 140
    badge_h = 40
    add_element(
        "shape",
        type="roundRect",
        x=80, y=80,
        width=badge_w, height=badge_h,
        fill=secondary_color,
        line_color="none",
    )
    
    badge_icon = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20">'
        f'<path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" fill="none" stroke="#FFFFFF" stroke-width="2"/>'
        f'<path d="M14 2V8H20" fill="none" stroke="#FFFFFF" stroke-width="2"/>'
        f'<path d="M8 13H16M8 17H16M8 9H10" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>'
        f'</svg>'
    )
    badge_icon_el = add_element("shape", type="freeform", x=95, y=90, width=20, height=20, fill="none", line_color="none")
    badge_icon_el.set("svg_data", html_mod.escape(badge_icon))
    
    add_textbox(
        badge_text,
        x=120, y=80,
        width=badge_w - 40, height=badge_h,
        font="Arial", size=16, bold="true", color="#FFFFFF",
        align="left", vertical_align="middle", single_line="true"
    )

    # Title
    add_textbox(
        title,
        x=80, y=140,
        width=1400, height=80,
        font="Arial", size=56, bold="true", color=primary_color,
        align="left", vertical_align="middle", single_line="true"
    )

    # Title underline
    add_element("shape", type="rect", x=80, y=230, width=120, height=6, fill=secondary_color, line_color="none")
    add_element("shape", type="rect", x=200, y=230, width=150, height=6, fill="#E0E0E0", line_color="none")

    # Left Panel - Chart Card
    add_element(
        "shape",
        type="roundRect",
        x=80, y=280,
        width=680, height=500,
        fill="#FFFFFF",
        line_color="#E0E0E0",
    )
    
    add_element("shape", type="oval", x=300, y=320, width=20, height=20, fill=secondary_color, line_color="none")
    add_textbox(
        chart_title,
        x=330, y=310,
        width=300, height=40,
        font="Arial", size=20, color=text_color,
        align="left", vertical_align="middle", single_line="true"
    )

    # Draw Bar Chart SVG
    chart_w = 560
    chart_h = 320
    chart_x = 120
    chart_y = 380

    svg_chart = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {chart_w} {chart_h}" width="{chart_w}" height="{chart_h}">'
    max_val = 2000
    y_steps = [0, 500, 1000, 1500, 2000]
    
    # Grid lines and Y labels
    for step in y_steps:
        y_pos = chart_h - (step / max_val * (chart_h - 40)) - 30
        svg_chart += f'<text x="40" y="{y_pos+5}" font-family="Arial" font-size="14" fill="#666666" text-anchor="end">{step:,}</text>'.replace(",", ".")
        svg_chart += f'<line x1="50" y1="{y_pos}" x2="{chart_w}" y2="{y_pos}" stroke="#EEEEEE" stroke-width="1"/>'

    # Bars and X labels
    bar_width = 45
    spacing = (chart_w - 60) / len(chart_labels)
    for i, (label, val) in enumerate(zip(chart_labels, chart_data)):
        x_center = 60 + i * spacing + spacing / 2
        bar_h = val / max_val * (chart_h - 40)
        y_pos = chart_h - bar_h - 30
        svg_chart += f'<rect x="{x_center - bar_width/2}" y="{y_pos}" width="{bar_width}" height="{bar_h}" fill="{secondary_color}" rx="4"/>'
        svg_chart += f'<text x="{x_center}" y="{chart_h}" font-family="Arial" font-size="16" fill="#333333" text-anchor="middle">{label}</text>'

    svg_chart += '</svg>'
    chart_el = add_element("shape", type="freeform", x=chart_x, y=chart_y, width=chart_w, height=chart_h, fill="none", line_color="none")
    chart_el.set("svg_data", html_mod.escape(svg_chart))

    # Right Panel - Insights Card
    add_element(
        "shape",
        type="roundRect",
        x=800, y=280,
        width=720, height=500,
        fill=light_bg_color,
        line_color="none",
    )

    # Insights Title & Icon
    bulb_icon = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="60" height="60">'
        f'<circle cx="24" cy="24" r="24" fill="#D2E3FF"/>'
        f'<path d="M24 12C19 12 15 16 15 21C15 24 17 26.5 19 28V31C19 32.1 19.9 33 21 33H27C28.1 33 29 32.1 29 31V28C31 26.5 33 24 33 21C33 16 29 12 24 12ZM21 35H27V36C27 37.1 26.1 38 25 38H23C21.9 38 21 37.1 21 36V35Z" fill="{secondary_color}"/>'
        f'</svg>'
    )
    bulb_el = add_element("shape", type="freeform", x=840, y=310, width=60, height=60, fill="none", line_color="none")
    bulb_el.set("svg_data", html_mod.escape(bulb_icon))

    add_textbox(
        insights_title,
        x=920, y=320,
        width=500, height=40,
        font="Arial", size=24, bold="true", color="#111111",
        align="left", vertical_align="middle", single_line="true"
    )

    # Bullet points
    bullet_y = 400
    for insight in insights:
        # Bullet
        add_element("shape", type="oval", x=850, y=bullet_y + 8, width=8, height=8, fill="#111111", line_color="none")
        add_textbox(
            insight,
            x=880, y=bullet_y,
            width=580, height=60,
            font="Arial", size=18, color="#333333",
            align="left", vertical_align="top", single_line="false", max_lines=2
        )
        bullet_y += 70

    # Separator Line
    add_element("shape", type="rect", x=840, y=630, width=640, height=2, fill="#C0D5FF", line_color="none")

    # Conclusion
    check_icon = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="30" height="30">'
        f'<circle cx="12" cy="12" r="11" fill="none" stroke="{text_color}" stroke-width="2"/>'
        f'<path d="M7 12L10 15L17 8" fill="none" stroke="{text_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )
    check_el = add_element("shape", type="freeform", x=840, y=670, width=30, height=30, fill="none", line_color="none")
    check_el.set("svg_data", html_mod.escape(check_icon))

    add_textbox(
        conclusion_text,
        x=880, y=665,
        width=580, height=80,
        font="Arial", size=18, bold="true", color="#111111",
        align="left", vertical_align="top", single_line="false", max_lines=3
    )

    # Footer Area
    add_element("shape", type="rect", x=0, y=830, width=1600, height=70, fill=primary_color, line_color="none")
    add_textbox(
        footer_text,
        x=80, y=830,
        width=400, height=70,
        font="Arial", size=18, color="#FFFFFF",
        align="left", vertical_align="middle", single_line="true"
    )
    add_textbox(
        page_number,
        x=1470, y=830,
        width=50, height=70,
        font="Arial", size=18, color="#FFFFFF",
        align="right", vertical_align="middle", single_line="true"
    )

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    return xml_content





def generate_dark_multi_line_chart_slide_xml(**kwargs) -> str:
    """Generates a dark multi line slide."""
    title = kwargs.get('title', 'Slide Title')
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<presentation schemaVersion=\"1.0\" width=\"810\" height=\"455\" slideWidthInches=\"13.333\" slideHeightInches=\"7.5\">
  <slide background=\"#1E3052\">
    <shape type=\"rect\" x=\"0\" y=\"0\" width=\"810\" height=\"455\" fill=\"#1E3052\" line_color=\"none\"/>
    <textbox x=\"40\" y=\"25\" width=\"500\" height=\"42\" font=\"Arial\" size=\"28\" bold=\"true\" color=\"#FFFFFF\" single_line=\"true\" min_font_size=\"22\" overflow=\"clip\">SALES RATE FOR 7 YEARS</textbox>
    <shape type=\"freeform\" x=\"0\" y=\"0\" width=\"810\" height=\"455\" fill=\"none\" line_color=\"none\" svg_data=\"&amp;lt;svg xmlns=&amp;quot;http://www.w3.org/2000/svg&amp;quot; viewBox=&amp;quot;0 0 810 455&amp;quot; width=&amp;quot;810&amp;quot; height=&amp;quot;455&amp;quot;&amp;gt;&amp;lt;line x1=&amp;quot;60&amp;quot; y1=&amp;quot;355.0&amp;quot; x2=&amp;quot;770&amp;quot; y2=&amp;quot;355.0&amp;quot; stroke=&amp;quot;#2A4468&amp;quot; stroke-width=&amp;quot;0.5&amp;quot; stroke-dasharray=&amp;quot;4,3&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;50&amp;quot; y=&amp;quot;355.0&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;10&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;0&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;60&amp;quot; y1=&amp;quot;286.2&amp;quot; x2=&amp;quot;770&amp;quot; y2=&amp;quot;286.2&amp;quot; stroke=&amp;quot;#2A4468&amp;quot; stroke-width=&amp;quot;0.5&amp;quot; stroke-dasharray=&amp;quot;4,3&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;50&amp;quot; y=&amp;quot;286.2&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;10&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;10&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;60&amp;quot; y1=&amp;quot;217.5&amp;quot; x2=&amp;quot;770&amp;quot; y2=&amp;quot;217.5&amp;quot; stroke=&amp;quot;#2A4468&amp;quot; stroke-width=&amp;quot;0.5&amp;quot; stroke-dasharray=&amp;quot;4,3&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;50&amp;quot; y=&amp;quot;217.5&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;10&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;20&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;60&amp;quot; y1=&amp;quot;148.8&amp;quot; x2=&amp;quot;770&amp;quot; y2=&amp;quot;148.8&amp;quot; stroke=&amp;quot;#2A4468&amp;quot; stroke-width=&amp;quot;0.5&amp;quot; stroke-dasharray=&amp;quot;4,3&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;50&amp;quot; y=&amp;quot;148.8&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;10&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;30&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;60&amp;quot; y1=&amp;quot;80.0&amp;quot; x2=&amp;quot;770&amp;quot; y2=&amp;quot;80.0&amp;quot; stroke=&amp;quot;#2A4468&amp;quot; stroke-width=&amp;quot;0.5&amp;quot; stroke-dasharray=&amp;quot;4,3&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;50&amp;quot; y=&amp;quot;80.0&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;10&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;40&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;60.0&amp;quot; y=&amp;quot;375&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;11&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;2016&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;178.3&amp;quot; y=&amp;quot;375&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;11&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;2017&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;296.7&amp;quot; y=&amp;quot;375&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;11&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;2018&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;415.0&amp;quot; y=&amp;quot;375&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;11&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;2019&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;533.3&amp;quot; y=&amp;quot;375&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;11&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;2020&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;651.7&amp;quot; y=&amp;quot;375&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;11&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;2021&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;770.0&amp;quot; y=&amp;quot;375&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;11&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;#8AABC4&amp;quot;&amp;gt;2022&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;60&amp;quot; y1=&amp;quot;355&amp;quot; x2=&amp;quot;770&amp;quot; y2=&amp;quot;355&amp;quot; stroke=&amp;quot;#4A6A8A&amp;quot; stroke-width=&amp;quot;1&amp;quot;/&amp;gt;
&amp;lt;polyline points=&amp;quot;60.0,286.2 178.3,114.4 296.7,251.9 415.0,251.9 533.3,162.5 651.7,114.4 770.0,286.2&amp;quot; fill=&amp;quot;none&amp;quot; stroke=&amp;quot;#FFD700&amp;quot; stroke-width=&amp;quot;2.5&amp;quot; stroke-linejoin=&amp;quot;round&amp;quot; stroke-linecap=&amp;quot;round&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;60.0&amp;quot; cy=&amp;quot;286.2&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FFD700&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;178.3&amp;quot; cy=&amp;quot;114.4&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FFD700&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;296.7&amp;quot; cy=&amp;quot;251.9&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FFD700&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;415.0&amp;quot; cy=&amp;quot;251.9&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FFD700&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;533.3&amp;quot; cy=&amp;quot;162.5&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FFD700&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;651.7&amp;quot; cy=&amp;quot;114.4&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FFD700&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;770.0&amp;quot; cy=&amp;quot;286.2&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FFD700&amp;quot;/&amp;gt;
&amp;lt;polyline points=&amp;quot;60.0,224.4 178.3,176.2 296.7,183.1 415.0,286.2 533.3,114.4 651.7,148.8 770.0,162.5&amp;quot; fill=&amp;quot;none&amp;quot; stroke=&amp;quot;#FF6B6B&amp;quot; stroke-width=&amp;quot;2.5&amp;quot; stroke-linejoin=&amp;quot;round&amp;quot; stroke-linecap=&amp;quot;round&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;60.0&amp;quot; cy=&amp;quot;224.4&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FF6B6B&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;178.3&amp;quot; cy=&amp;quot;176.2&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FF6B6B&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;296.7&amp;quot; cy=&amp;quot;183.1&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FF6B6B&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;415.0&amp;quot; cy=&amp;quot;286.2&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FF6B6B&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;533.3&amp;quot; cy=&amp;quot;114.4&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FF6B6B&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;651.7&amp;quot; cy=&amp;quot;148.8&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FF6B6B&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;770.0&amp;quot; cy=&amp;quot;162.5&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#FF6B6B&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;50&amp;quot; cy=&amp;quot;410&amp;quot; r=&amp;quot;6&amp;quot; fill=&amp;quot;#FFD700&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;62&amp;quot; y=&amp;quot;410&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;11&amp;quot; fill=&amp;quot;#FFFFFF&amp;quot;&amp;gt;Product 01&amp;lt;/text&amp;gt;
&amp;lt;circle cx=&amp;quot;190&amp;quot; cy=&amp;quot;410&amp;quot; r=&amp;quot;6&amp;quot; fill=&amp;quot;#FF6B6B&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;202&amp;quot; y=&amp;quot;410&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;11&amp;quot; fill=&amp;quot;#FFFFFF&amp;quot;&amp;gt;Product 02&amp;lt;/text&amp;gt;&amp;lt;/svg&amp;gt;\"/>
    <textbox x=\"470\" y=\"400\" width=\"310\" height=\"40\" font=\"Arial\" size=\"9\" color=\"#8AABC4\" single_line=\"false\" max_lines=\"3\" min_font_size=\"7\" overflow=\"clip\" line_spacing=\"1.3\">A business model is nothing more than a blueprint that explains how a company aims to make money</textbox>
  </slide>
</presentation>
"""

def generate_line_chart_report_slide_xml(**kwargs) -> str:
    """Generates a line chart report slide."""
    title = kwargs.get('title', 'Slide Title')
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<presentation schemaVersion=\"1.0\" width=\"810\" height=\"455\" slideWidthInches=\"13.333\" slideHeightInches=\"7.5\">
  <slide background=\"#F5F9F9\">
    <shape type=\"rect\" x=\"0\" y=\"0\" width=\"810\" height=\"455\" fill=\"#F5F9F9\" line_color=\"none\"/>
    <textbox x=\"80\" y=\"15\" width=\"650\" height=\"40\" font=\"Arial\" size=\"26\" bold=\"true\" color=\"#0D7377\" align=\"center\" single_line=\"true\" min_font_size=\"20\" overflow=\"clip\">Repeat Order Report Graph</textbox>
    <textbox x=\"80\" y=\"55\" width=\"650\" height=\"55\" font=\"Arial\" size=\"10\" color=\"#555555\" align=\"center\" single_line=\"false\" max_lines=\"3\" min_font_size=\"8\" overflow=\"clip\" line_spacing=\"1.3\">A repeat order report graph helps businesses track customer loyalty and sales data patterns.</textbox>
    <shape type=\"freeform\" x=\"0\" y=\"0\" width=\"810\" height=\"455\" fill=\"none\" line_color=\"none\" svg_data=\"&amp;lt;svg xmlns=&amp;quot;http://www.w3.org/2000/svg&amp;quot; viewBox=&amp;quot;0 0 810 455&amp;quot; width=&amp;quot;810&amp;quot; height=&amp;quot;455&amp;quot;&amp;gt;&amp;lt;line x1=&amp;quot;55&amp;quot; y1=&amp;quot;360.0&amp;quot; x2=&amp;quot;780&amp;quot; y2=&amp;quot;360.0&amp;quot; stroke=&amp;quot;#E0EDED&amp;quot; stroke-width=&amp;quot;0.5&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;47&amp;quot; y=&amp;quot;360.0&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;0&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;55&amp;quot; y1=&amp;quot;314.0&amp;quot; x2=&amp;quot;780&amp;quot; y2=&amp;quot;314.0&amp;quot; stroke=&amp;quot;#E0EDED&amp;quot; stroke-width=&amp;quot;0.5&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;47&amp;quot; y=&amp;quot;314.0&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;6&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;55&amp;quot; y1=&amp;quot;268.0&amp;quot; x2=&amp;quot;780&amp;quot; y2=&amp;quot;268.0&amp;quot; stroke=&amp;quot;#E0EDED&amp;quot; stroke-width=&amp;quot;0.5&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;47&amp;quot; y=&amp;quot;268.0&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;12&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;55&amp;quot; y1=&amp;quot;222.0&amp;quot; x2=&amp;quot;780&amp;quot; y2=&amp;quot;222.0&amp;quot; stroke=&amp;quot;#E0EDED&amp;quot; stroke-width=&amp;quot;0.5&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;47&amp;quot; y=&amp;quot;222.0&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;18&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;55&amp;quot; y1=&amp;quot;176.0&amp;quot; x2=&amp;quot;780&amp;quot; y2=&amp;quot;176.0&amp;quot; stroke=&amp;quot;#E0EDED&amp;quot; stroke-width=&amp;quot;0.5&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;47&amp;quot; y=&amp;quot;176.0&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;24&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;55&amp;quot; y1=&amp;quot;130.0&amp;quot; x2=&amp;quot;780&amp;quot; y2=&amp;quot;130.0&amp;quot; stroke=&amp;quot;#E0EDED&amp;quot; stroke-width=&amp;quot;0.5&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;47&amp;quot; y=&amp;quot;130.0&amp;quot; text-anchor=&amp;quot;end&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;30&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;55.0&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Jan&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;120.9&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Feb&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;186.8&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Mar&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;252.7&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Apr&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;318.6&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;May&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;384.5&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Jun&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;450.5&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Jul&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;516.4&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Aug&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;582.3&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Sep&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;648.2&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Oct&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;714.1&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Nov&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;780.0&amp;quot; y=&amp;quot;376&amp;quot; text-anchor=&amp;quot;middle&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;Dec&amp;lt;/text&amp;gt;
&amp;lt;line x1=&amp;quot;55&amp;quot; y1=&amp;quot;130&amp;quot; x2=&amp;quot;55&amp;quot; y2=&amp;quot;360&amp;quot; stroke=&amp;quot;#0D7377&amp;quot; stroke-width=&amp;quot;1&amp;quot;/&amp;gt;
&amp;lt;line x1=&amp;quot;55&amp;quot; y1=&amp;quot;360&amp;quot; x2=&amp;quot;780&amp;quot; y2=&amp;quot;360&amp;quot; stroke=&amp;quot;#0D7377&amp;quot; stroke-width=&amp;quot;1&amp;quot;/&amp;gt;
&amp;lt;polyline points=&amp;quot;55.0,321.7 120.9,344.7 186.8,260.3 252.7,245.0 318.6,260.3 384.5,214.3 450.5,321.7 516.4,321.7 582.3,291.0 648.2,176.0 714.1,268.0 780.0,206.7&amp;quot; fill=&amp;quot;none&amp;quot; stroke=&amp;quot;#0D7377&amp;quot; stroke-width=&amp;quot;2.0&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;55.0&amp;quot; cy=&amp;quot;321.7&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;120.9&amp;quot; cy=&amp;quot;344.7&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;186.8&amp;quot; cy=&amp;quot;260.3&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;252.7&amp;quot; cy=&amp;quot;245.0&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;318.6&amp;quot; cy=&amp;quot;260.3&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;384.5&amp;quot; cy=&amp;quot;214.3&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;450.5&amp;quot; cy=&amp;quot;321.7&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;516.4&amp;quot; cy=&amp;quot;321.7&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;582.3&amp;quot; cy=&amp;quot;291.0&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;648.2&amp;quot; cy=&amp;quot;176.0&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;714.1&amp;quot; cy=&amp;quot;268.0&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;circle cx=&amp;quot;780.0&amp;quot; cy=&amp;quot;206.7&amp;quot; r=&amp;quot;5.0&amp;quot; fill=&amp;quot;#0D7377&amp;quot;/&amp;gt;
&amp;lt;rect x=&amp;quot;345.0&amp;quot; y=&amp;quot;108&amp;quot; width=&amp;quot;10&amp;quot; height=&amp;quot;10&amp;quot; fill=&amp;quot;#0D7377&amp;quot; rx=&amp;quot;1&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;359.0&amp;quot; y=&amp;quot;114&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#0D7377&amp;quot;&amp;gt;2026&amp;lt;/text&amp;gt;&amp;lt;/svg&amp;gt;\"/>
    <shape type=\"rounded_rectangle\" x=\"40\" y=\"385\" width=\"200\" height=\"50\" fill=\"#FFFFFF\" line_color=\"#0D7377\" line_width=\"1\"/>
    <textbox x=\"48\" y=\"390\" width=\"184\" height=\"40\" font=\"Arial\" size=\"13\" bold=\"true\" color=\"#0D7377\" align=\"center\" vertical_align=\"middle\" single_line=\"false\" max_lines=\"2\" min_font_size=\"10\" overflow=\"clip\">October Is Peak</textbox>
    <shape type=\"rounded_rectangle\" x=\"255\" y=\"385\" width=\"200\" height=\"50\" fill=\"#FFFFFF\" line_color=\"#0D7377\" line_width=\"1\"/>
    <textbox x=\"263\" y=\"390\" width=\"184\" height=\"40\" font=\"Arial\" size=\"13\" bold=\"true\" color=\"#0D7377\" align=\"center\" vertical_align=\"middle\" single_line=\"false\" max_lines=\"2\" min_font_size=\"10\" overflow=\"clip\">+40% From Last Year</textbox>
  </slide>
</presentation>
"""

def generate_modern_pie_chart_slide_xml(**kwargs) -> str:
    """Generates a pie chart slide."""
    title = kwargs.get('title', 'Slide Title')
    return """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<presentation schemaVersion=\"1.0\" width=\"810\" height=\"455\" slideWidthInches=\"13.333\" slideHeightInches=\"7.5\">
  <slide background=\"#FFFFFF\">
    <shape type=\"rect\" x=\"0\" y=\"0\" width=\"810\" height=\"455\" fill=\"#FFFFFF\" line_color=\"none\"/>
    <textbox x=\"40\" y=\"25\" width=\"400\" height=\"50\" font=\"Arial\" size=\"32\" bold=\"true\" color=\"#111111\" single_line=\"true\" min_font_size=\"24\" overflow=\"clip\">Budget Pie Chart</textbox>
    <textbox x=\"40\" y=\"70\" width=\"350\" height=\"28\" font=\"Arial\" size=\"16\" color=\"#444444\" single_line=\"true\" min_font_size=\"12\" overflow=\"clip\">Monthly Budget</textbox>
    <shape type=\"freeform\" x=\"0\" y=\"0\" width=\"810\" height=\"455\" fill=\"none\" line_color=\"none\" svg_data=\"&amp;lt;svg xmlns=&amp;quot;http://www.w3.org/2000/svg&amp;quot; viewBox=&amp;quot;0 0 810 455&amp;quot; width=&amp;quot;810&amp;quot; height=&amp;quot;455&amp;quot;&amp;gt;&amp;lt;path d=&amp;quot;M 230,255 L 230.00,125.00 A 130,130 0 1 1 176.00,373.25 Z&amp;quot; fill=&amp;quot;#6366F1&amp;quot; stroke=&amp;quot;white&amp;quot; stroke-width=&amp;quot;1&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;385.0&amp;quot; y=&amp;quot;288.7&amp;quot; text-anchor=&amp;quot;middle&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#555555&amp;quot;&amp;gt;Food&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;312.6&amp;quot; y=&amp;quot;273.0&amp;quot; text-anchor=&amp;quot;middle&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;10&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;white&amp;quot;&amp;gt;56.8%&amp;lt;/text&amp;gt;
&amp;lt;path d=&amp;quot;M 230,255 L 176.00,373.25 A 130,130 0 0 1 105.27,218.37 Z&amp;quot; fill=&amp;quot;#FB923C&amp;quot; stroke=&amp;quot;white&amp;quot; stroke-width=&amp;quot;1&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;85.7&amp;quot; y=&amp;quot;320.9&amp;quot; text-anchor=&amp;quot;middle&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#555555&amp;quot;&amp;gt;Shelter&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;153.1&amp;quot; y=&amp;quot;290.1&amp;quot; text-anchor=&amp;quot;middle&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;10&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;white&amp;quot;&amp;gt;22.7%&amp;lt;/text&amp;gt;
&amp;lt;path d=&amp;quot;M 230,255 L 105.27,218.37 A 130,130 0 0 1 159.72,145.64 Z&amp;quot; fill=&amp;quot;#F87171&amp;quot; stroke=&amp;quot;white&amp;quot; stroke-width=&amp;quot;1&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;103.0&amp;quot; y=&amp;quot;160.0&amp;quot; text-anchor=&amp;quot;middle&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#555555&amp;quot;&amp;gt;Education&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;162.4&amp;quot; y=&amp;quot;204.4&amp;quot; text-anchor=&amp;quot;middle&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;10&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;white&amp;quot;&amp;gt;11.4%&amp;lt;/text&amp;gt;
&amp;lt;path d=&amp;quot;M 230,255 L 159.72,145.64 A 130,130 0 0 1 230.00,125.00 Z&amp;quot; fill=&amp;quot;#34D399&amp;quot; stroke=&amp;quot;white&amp;quot; stroke-width=&amp;quot;1&amp;quot;/&amp;gt;
&amp;lt;text x=&amp;quot;185.3&amp;quot; y=&amp;quot;102.8&amp;quot; text-anchor=&amp;quot;middle&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;9&amp;quot; fill=&amp;quot;#555555&amp;quot;&amp;gt;Savings&amp;lt;/text&amp;gt;
&amp;lt;text x=&amp;quot;206.2&amp;quot; y=&amp;quot;173.9&amp;quot; text-anchor=&amp;quot;middle&amp;quot; dominant-baseline=&amp;quot;central&amp;quot; font-family=&amp;quot;Arial&amp;quot; font-size=&amp;quot;10&amp;quot; font-weight=&amp;quot;bold&amp;quot; fill=&amp;quot;white&amp;quot;&amp;gt;9.1%&amp;lt;/text&amp;gt;&amp;lt;/svg&amp;gt;\"/>
    <shape type=\"rounded_rectangle\" x=\"470\" y=\"130\" width=\"12\" height=\"32\" fill=\"#6366F1\" line_color=\"none\"/>
    <textbox x=\"492\" y=\"128\" width=\"280\" height=\"22\" font=\"Arial\" size=\"14\" bold=\"true\" color=\"#111111\" single_line=\"true\" min_font_size=\"11\" overflow=\"clip\">Food</textbox>
    <textbox x=\"492\" y=\"148\" width=\"280\" height=\"36\" font=\"Arial\" size=\"11\" color=\"#666666\" single_line=\"false\" max_lines=\"2\" min_font_size=\"9\" overflow=\"clip\" line_spacing=\"1.15\">Briefly elaborate on what you want to discuss.</textbox>
    <shape type=\"rounded_rectangle\" x=\"470\" y=\"195\" width=\"12\" height=\"32\" fill=\"#FB923C\" line_color=\"none\"/>
    <textbox x=\"492\" y=\"193\" width=\"280\" height=\"22\" font=\"Arial\" size=\"14\" bold=\"true\" color=\"#111111\" single_line=\"true\" min_font_size=\"11\" overflow=\"clip\">Shelter</textbox>
    <textbox x=\"492\" y=\"213\" width=\"280\" height=\"36\" font=\"Arial\" size=\"11\" color=\"#666666\" single_line=\"false\" max_lines=\"2\" min_font_size=\"9\" overflow=\"clip\" line_spacing=\"1.15\">Briefly elaborate on what you want to discuss.</textbox>
    <shape type=\"rounded_rectangle\" x=\"470\" y=\"260\" width=\"12\" height=\"32\" fill=\"#F87171\" line_color=\"none\"/>
    <textbox x=\"492\" y=\"258\" width=\"280\" height=\"22\" font=\"Arial\" size=\"14\" bold=\"true\" color=\"#111111\" single_line=\"true\" min_font_size=\"11\" overflow=\"clip\">Education</textbox>
    <textbox x=\"492\" y=\"278\" width=\"280\" height=\"36\" font=\"Arial\" size=\"11\" color=\"#666666\" single_line=\"false\" max_lines=\"2\" min_font_size=\"9\" overflow=\"clip\" line_spacing=\"1.15\">Briefly elaborate on what you want to discuss.</textbox>
    <shape type=\"rounded_rectangle\" x=\"470\" y=\"325\" width=\"12\" height=\"32\" fill=\"#34D399\" line_color=\"none\"/>
    <textbox x=\"492\" y=\"323\" width=\"280\" height=\"22\" font=\"Arial\" size=\"14\" bold=\"true\" color=\"#111111\" single_line=\"true\" min_font_size=\"11\" overflow=\"clip\">Savings</textbox>
    <textbox x=\"492\" y=\"343\" width=\"280\" height=\"36\" font=\"Arial\" size=\"11\" color=\"#666666\" single_line=\"false\" max_lines=\"2\" min_font_size=\"9\" overflow=\"clip\" line_spacing=\"1.15\">Briefly elaborate on what you want to discuss.</textbox>
    <textbox x=\"40\" y=\"420\" width=\"300\" height=\"22\" font=\"Arial\" size=\"11\" color=\"#888888\" single_line=\"true\" overflow=\"clip\">www.reallygreatsite.com</textbox>
  </slide>
</presentation>
"""



