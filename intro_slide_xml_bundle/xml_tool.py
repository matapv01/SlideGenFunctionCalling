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

