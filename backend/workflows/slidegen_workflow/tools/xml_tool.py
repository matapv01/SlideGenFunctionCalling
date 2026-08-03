from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom



# Slide conten 

def generate_content_creation_slide_xml(
    main_title: str = "Content\nCreation",
    original_title: str = "Original Content",
    original_description: str = (
        "Develop unique visuals, videos, and copy that align with your "
        "brand's message and resonate with your audience's interests. "
        "Create content that not only captures attention but also conveys "
        "the essence of your brand."
    ),
    curated_title: str = "Curated Content",
    curated_description: str = (
        "Share valuable curated content from reputable sources in your "
        "industry such as articles, videos, and graphics to enhance your "
        "original material and engage your audience in discussions."
    ),
    main_image_url: str = (
        "https://images.unsplash.com/"
        "photo-1625064757761-c9bccabf1163"
        "?auto=format&fit=crop&q=80&w=1800"
    ),
    portrait_image_url: str = (
        "https://images.unsplash.com/"
        "photo-1552113125-81af17f36b57"
        "?auto=format&fit=crop&q=80&w=1000"
    ),
    background_color: str = "#D2DADE",
    title_color: str = "#68767C",
    accent_color: str = "#E4AAA2",
    decoration_color: str = "#AEB9BE",
    text_color: str = "#111111",
) -> str:
    """
    Sinh XML cho slide Content Creation.

    AI có thể truyền:
    - main_title
    - original_title
    - original_description
    - curated_title
    - curated_description
    - main_image_url
    - portrait_image_url
    - các màu

    Bố cục và đồ họa trang trí được giữ cố định.
    """

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": "810",
            "height": "455",
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )

    slide = ET.SubElement(
        presentation,
        "slide",
        {"background": background_color},
    )

    def add_element(tag: str, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {key: str(value) for key, value in attrs.items()},
        )

    def add_textbox(text: str, **attrs):
        node = add_element("textbox", **attrs)
        node.text = text
        return node

    # Ảnh lớn bên trái
    add_element(
        "image",
        src=main_image_url,
        x=0,
        y=27,
        width=498,
        height=225,
    )

    # Tiêu đề lớn bên phải
    add_textbox(
        main_title,
        x=575,
        y=24,
        width=220,
        height=170,
        font="Georgia",
        size=48,
        min_font_size=38,
        color=title_color,
        single_line="false",
        max_lines=2,
        overflow="shrink",
        line_spacing=0.95,
        safety_ratio=0.97,
    )

    # Trang trí hình học
    add_element(
        "shape",
        type="ellipse",
        x=445,
        y=42,
        width=82,
        height=82,
        fill="none",
        line_color=decoration_color,
        line_width=16,
    )

    add_element(
        "shape",
        type="rectangle",
        x=436,
        y=43,
        width=17,
        height=90,
        fill="#E7EBED",
        line_color="none",
    )

    add_element(
        "shape",
        type="rectangle",
        x=459,
        y=43,
        width=17,
        height=90,
        fill="#E7EBED",
        line_color="none",
    )

    # Nền bo góc cho ảnh chân dung
    add_element(
        "shape",
        type="rounded_rectangle",
        x=568,
        y=205,
        width=229,
        height=250,
        fill=accent_color,
        line_color="none",
    )

    # Ảnh chân dung
    add_element(
        "image",
        src=portrait_image_url,
        x=568,
        y=205,
        width=229,
        height=250,
    )

    # Cột nội dung 1
    add_textbox(
        original_title,
        x=34,
        y=295,
        width=230,
        height=28,
        font="Arial",
        size=17,
        bold="true",
        color=text_color,
        single_line="true",
        min_font_size=13,
        overflow="shrink",
    )

    add_textbox(
        original_description,
        x=34,
        y=332,
        width=250,
        height=93,
        font="Arial",
        size=12,
        min_font_size=10,
        color=text_color,
        single_line="false",
        max_lines=5,
        overflow="shrink",
        line_spacing=1.18,
        safety_ratio=0.96,
    )

    # Cột nội dung 2
    add_textbox(
        curated_title,
        x=330,
        y=295,
        width=210,
        height=28,
        font="Arial",
        size=17,
        bold="true",
        color=text_color,
        single_line="true",
        min_font_size=13,
        overflow="shrink",
    )

    add_textbox(
        curated_description,
        x=330,
        y=332,
        width=225,
        height=93,
        font="Arial",
        size=12,
        min_font_size=10,
        color=text_color,
        single_line="false",
        max_lines=5,
        overflow="shrink",
        line_spacing=1.18,
        safety_ratio=0.96,
    )

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    pretty_xml = minidom.parseString(
        raw_xml
    ).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    )

    xml_content = pretty_xml.decode("utf-8")

    return xml_content

def generate_ai_content_slide_xml(
    title: str = "THE SLIDE TITLE GOES HERE",
    intro_text: str = (
        "Do you know what helps you make your point clear? "
        "Lists like this one:"
    ),
    bullet_items: list[str] = [
        "They’re simple",
        "You can organize your ideas clearly",
        "You’ll never forget to buy milk!",
     
    ],
    footer_text: str = (
        "You can replace the image. Just right-click on "
        "it and select “Replace image”"
    ),
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1485827404703-89b55fcc595e"
        "?q=85&w=1400&auto=format&fit=crop"
    ),
    background_color: str = "#E3EAED",
    title_color: str = "#101010",
    text_color: str = "#1B1B1B",
) -> str:
    """
    Sinh XML cho slide nội dung có ảnh bên phải.

    Không dùng class phụ.
    Layout linh hoạt:
    - Mỗi vùng nội dung là một textbox.
    - Tự wrap, đo chiều cao và xếp theo flow dọc.
    - Nếu nội dung dài, tự giảm gap, body font và title font.
    - Không để các textbox overlap nhau.
    """



    if not title.strip():
        raise ValueError("title không được để trống")

    if not bullet_items:
        raise ValueError("bullet_items phải có ít nhất một phần tử")

    canvas_width = 1600
    canvas_height = 900

    left_x = 120
    left_width = 690

    content_top = 76
    content_bottom = 832
    available_height = content_bottom - content_top

    image_x = 860
    image_y = 30
    image_width = 700
    image_height = 820

    def normalize_font_name(name: str) -> str:
        return "".join(
            char.lower()
            for char in name
            if char.isalnum()
        )

    def font_directories() -> list[Path]:
        directories: list[Path] = []

        windir = os.environ.get("WINDIR")
        if windir:
            directories.append(Path(windir) / "Fonts")

        directories.extend(
            [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".fonts",
                Path.home() / "Library/Fonts",
                Path("/Library/Fonts"),
            ]
        )

        return [
            path
            for path in directories
            if path.exists()
        ]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": "arial",
            "Georgia": "georgia",
            "Calibri": "calibri",
            "Aptos": "aptos",
            "Times New Roman": "times",
        }

        normalized = normalize_font_name(
            aliases.get(font_name, font_name)
        )

        candidates: list[tuple[int, Path]] = []

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {
                    ".ttf",
                    ".otf",
                    ".ttc",
                }:
                    continue

                stem = normalize_font_name(path.stem)

                if normalized not in stem:
                    continue

                score = 70

                if stem == normalized:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in (
                        "bold",
                        "bd",
                        "semibold",
                    )
                )
                has_italic = any(
                    token in stem
                    for token in (
                        "italic",
                        "it",
                        "oblique",
                    )
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 10
                elif has_bold:
                    score -= 10

                if italic and has_italic:
                    score += 20
                elif italic:
                    score -= 10
                elif has_italic:
                    score -= 10

                candidates.append((score, path))

        if candidates:
            candidates.sort(
                key=lambda item: item[0],
                reverse=True,
            )
            return candidates[0][1]

        fallback_name = (
            "DejaVuSans-BoldOblique.ttf"
            if bold and italic
            else "DejaVuSans-Bold.ttf"
            if bold
            else "DejaVuSans-Oblique.ttf"
            if italic
            else "DejaVuSans.ttf"
        )

        font = ImageFont.truetype(
            fallback_name,
            12,
        )
        font_path = getattr(font, "path", None)

        if not font_path:
            raise ValueError(
                f"Không tìm thấy font '{font_name}'"
            )

        return Path(font_path)

    canvas_dpi = 120.0

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(
        font_path: Path,
        font_size_pt: float,
    ) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(
                1,
                round(pt_to_canvas(font_size_pt)),
            ),
        )

    def measure_text_width(
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        font = load_font(
            font_path,
            font_size_pt,
        )

        if hasattr(font, "getlength"):
            return float(font.getlength(text))

        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(
        font_path: Path,
        font_size_pt: float,
        line_spacing: float,
    ) -> float:
        font = load_font(
            font_path,
            font_size_pt,
        )
        ascent, descent = font.getmetrics()

        return (
            float(ascent + descent)
            * line_spacing
        )

    def break_long_word(
        word: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        parts: list[str] = []
        current = ""

        for char in word:
            candidate = current + char

            if (
                current
                and measure_text_width(
                    candidate,
                    font_path,
                    font_size_pt,
                )
                > max_width
            ):
                parts.append(current)
                current = char
            else:
                current = candidate

        if current:
            parts.append(current)

        return parts or [""]

    def wrap_text(
        text: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        result: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                result.append("")
                continue

            current = ""

            for word in words:
                if (
                    measure_text_width(
                        word,
                        font_path,
                        font_size_pt,
                    )
                    > max_width
                ):
                    pieces = break_long_word(
                        word,
                        font_path,
                        font_size_pt,
                        max_width,
                    )
                else:
                    pieces = [word]

                for piece in pieces:
                    candidate = (
                        piece
                        if not current
                        else f"{current} {piece}"
                    )

                    if (
                        not current
                        or measure_text_width(
                            candidate,
                            font_path,
                            font_size_pt,
                        )
                        <= max_width
                    ):
                        current = candidate
                    else:
                        result.append(current)
                        current = piece

            if current:
                result.append(current)

        return result or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        max_width: float,
        line_spacing: float,
        vertical_padding: float = 6,
    ) -> dict:
        lines = wrap_text(
            text,
            font_path,
            font_size,
            max_width,
        )

        line_height = measure_line_height(
            font_path,
            font_size,
            line_spacing,
        )

        return {
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines) * line_height
                + vertical_padding
            ),
        }

    title_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=True,
    )
    body_font_path = resolve_font_path(
        body_font_name,
        bold=False,
    )

    title_font_size = 62.0
    title_min_font_size = 36.0

    body_font_size = 28.0
    body_min_font_size = 18.0

    title_line_spacing = 0.92
    body_line_spacing = 1.05
    bullet_line_spacing = 1.08

    title_intro_gap = 56.0
    intro_bullet_gap = 26.0
    bullet_footer_gap = 28.0
    minimum_gap = 14.0

    bullet_text = "\n".join(
        f"•  {item.strip()}"
        for item in bullet_items
        if item.strip()
    )

    if not bullet_text:
        raise ValueError(
            "bullet_items không chứa nội dung hợp lệ"
        )

    def calculate_all_layouts(
        current_title_size: float,
        current_body_size: float,
    ) -> dict:
        return {
            "title": layout_text(
                title,
                font_path=title_font_path,
                font_size=current_title_size,
                max_width=left_width,
                line_spacing=title_line_spacing,
                vertical_padding=8,
            ),
            "intro": layout_text(
                intro_text,
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=left_width,
                line_spacing=body_line_spacing,
                vertical_padding=6,
            ),
            "bullet": layout_text(
                bullet_text,
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=left_width,
                line_spacing=bullet_line_spacing,
                vertical_padding=6,
            ),
            "footer": layout_text(
                footer_text,
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=left_width,
                line_spacing=body_line_spacing,
                vertical_padding=6,
            ),
        }

    def total_required_height(
        layouts: dict,
        gap_1: float,
        gap_2: float,
        gap_3: float,
    ) -> float:
        return (
            layouts["title"]["height"]
            + gap_1
            + layouts["intro"]["height"]
            + gap_2
            + layouts["bullet"]["height"]
            + gap_3
            + layouts["footer"]["height"]
        )

    layouts = calculate_all_layouts(
        title_font_size,
        body_font_size,
    )

    total_height = total_required_height(
        layouts,
        title_intro_gap,
        intro_bullet_gap,
        bullet_footer_gap,
    )

    for _ in range(200):
        if total_height <= available_height:
            break

        changed = False

        if (
            title_intro_gap > minimum_gap
            or intro_bullet_gap > minimum_gap
            or bullet_footer_gap > minimum_gap
        ):
            title_intro_gap = max(
                minimum_gap,
                title_intro_gap - 2,
            )
            intro_bullet_gap = max(
                minimum_gap,
                intro_bullet_gap - 2,
            )
            bullet_footer_gap = max(
                minimum_gap,
                bullet_footer_gap - 2,
            )
            changed = True

        elif body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif title_font_size > title_min_font_size:
            title_font_size = max(
                title_min_font_size,
                title_font_size - 0.5,
            )
            changed = True

        if not changed:
            break

        layouts = calculate_all_layouts(
            title_font_size,
            body_font_size,
        )

        total_height = total_required_height(
            layouts,
            title_intro_gap,
            intro_bullet_gap,
            bullet_footer_gap,
        )

    if total_height > available_height:
        raise ValueError(
            "Nội dung quá dài để đặt vừa slide mà không overlap. "
            f"Cần {total_height:.1f}px nhưng vùng khả dụng chỉ "
            f"{available_height:.1f}px."
        )

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": str(canvas_width),
            "height": str(canvas_height),
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )

    slide = ET.SubElement(
        presentation,
        "slide",
        {"background": background_color},
    )

    def add(tag: str, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {
                key: str(value)
                for key, value in attrs.items()
                if value is not None
            },
        )

    def textbox(text: str, **attrs):
        node = add(
            "textbox",
            **attrs,
        )
        node.text = text
        return node

    add(
        "image",
        src=image_url,
        x=image_x,
        y=image_y,
        width=image_width,
        height=image_height,
    )

    cursor_y = float(content_top)

    title_y = cursor_y

    textbox(
        layouts["title"]["text"],
        x=left_x,
        y=title_y,
        width=left_width,
        height=layouts["title"]["height"],
        font=title_font_name,
        size=layouts["title"]["font_size"],
        min_font_size=layouts["title"]["font_size"],
        bold="true",
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["title"]["lines"]),
        overflow="clip",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    cursor_y += (
        layouts["title"]["height"]
        + title_intro_gap
    )

    intro_y = cursor_y

    textbox(
        layouts["intro"]["text"],
        x=left_x,
        y=intro_y,
        width=left_width,
        height=layouts["intro"]["height"],
        font=body_font_name,
        size=layouts["intro"]["font_size"],
        min_font_size=layouts["intro"]["font_size"],
        color=text_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["intro"]["lines"]),
        overflow="clip",
        line_spacing=body_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    cursor_y += (
        layouts["intro"]["height"]
        + intro_bullet_gap
    )

    bullet_y = cursor_y

    textbox(
        layouts["bullet"]["text"],
        x=left_x,
        y=bullet_y,
        width=left_width,
        height=layouts["bullet"]["height"],
        font=body_font_name,
        size=layouts["bullet"]["font_size"],
        min_font_size=layouts["bullet"]["font_size"],
        color=text_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["bullet"]["lines"]),
        overflow="clip",
        line_spacing=bullet_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    cursor_y += (
        layouts["bullet"]["height"]
        + bullet_footer_gap
    )

    footer_y = cursor_y

    textbox(
        layouts["footer"]["text"],
        x=left_x,
        y=footer_y,
        width=left_width,
        height=layouts["footer"]["height"],
        font=body_font_name,
        size=layouts["footer"]["font_size"],
        min_font_size=layouts["footer"]["font_size"],
        color=text_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["footer"]["lines"]),
        overflow="clip",
        line_spacing=body_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    print(
        "Layout đã fit:"
        f"\n  Title: {len(layouts['title']['lines'])} dòng, "
        f"{layouts['title']['font_size']:g}pt, "
        f"y={title_y:.1f}, h={layouts['title']['height']:.1f}"
        f"\n  Intro: {len(layouts['intro']['lines'])} dòng, "
        f"{layouts['intro']['font_size']:g}pt, "
        f"y={intro_y:.1f}, h={layouts['intro']['height']:.1f}"
        f"\n  Bullet: {len(layouts['bullet']['lines'])} dòng, "
        f"{layouts['bullet']['font_size']:g}pt, "
        f"y={bullet_y:.1f}, h={layouts['bullet']['height']:.1f}"
        f"\n  Footer: {len(layouts['footer']['lines'])} dòng, "
        f"{layouts['footer']['font_size']:g}pt, "
        f"y={footer_y:.1f}, h={layouts['footer']['height']:.1f}"
        f"\n  Tổng chiều cao: {total_height:.1f}/"
        f"{available_height:.1f}px"
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

def generate_two_ideas_slide_xml(
    title: str = "TWO IDEAS",
    idea_titles: list[str] = [
        "VENUS",
        "MERCURY",
    ],
    idea_descriptions: list[str] = [
        (
            "Venus has a beautiful name and is the second planet "
            "from the Sun. It’s hot and is the second-brightest "
            "natural object in the night sky."
        ),
        (
            "Mercury is the closest planet to the Sun and the "
            "smallest one in the Solar System. This planet’s name "
            "has nothing to do with the liquid metal."
        ),
    ],
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1529139574466-a303027c1d8b"
        "?q=85&w=1200&auto=format&fit=crop"
    ),
    background_color: str = "#1A1A1A",
    title_color: str = "#FFFFFF",
    heading_color: str = "#FFFFFF",
    body_color: str = "#F1F1F1",
) -> str:
    """
    Generate XML for a two-column ideas slide.

    The layout features a full-height image on the left and a dark
    content area on the right containing a main title and vertically
    stacked idea sections with headings and descriptions.
    """

    canvas_width = 1600
    canvas_height = 900

    image_x = 0
    image_y = 0
    image_width = 520
    image_height = 900

    content_x = 680
    content_width = 810
    content_top = 92
    content_bottom = 825
    available_height = content_bottom - content_top

    # =====================================================
    # Font helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            char.lower()
            for char in name
            if char.isalnum()
        )

    def font_directories() -> list[Path]:
        directories: list[Path] = []

        windir = os.environ.get("WINDIR")
        if windir:
            directories.append(Path(windir) / "Fonts")

        directories.extend(
            [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".fonts",
                Path.home() / "Library/Fonts",
                Path("/Library/Fonts"),
            ]
        )

        return [
            path
            for path in directories
            if path.exists()
        ]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
    ) -> Path:
        aliases = {
            "Arial": "arial",
            "Calibri": "calibri",
            "Aptos": "aptos",
            "Helvetica": "helvetica",
        }

        normalized = normalize_font_name(
            aliases.get(font_name, font_name)
        )

        candidates: list[tuple[int, Path]] = []

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {
                    ".ttf",
                    ".otf",
                    ".ttc",
                }:
                    continue

                stem = normalize_font_name(path.stem)

                if normalized not in stem:
                    continue

                score = 70

                if stem == normalized:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in (
                        "bold",
                        "bd",
                        "semibold",
                    )
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 10
                elif has_bold:
                    score -= 10

                candidates.append((score, path))

        if candidates:
            candidates.sort(
                key=lambda item: item[0],
                reverse=True,
            )
            return candidates[0][1]

        fallback = (
            "DejaVuSans-Bold.ttf"
            if bold
            else "DejaVuSans.ttf"
        )

        font = ImageFont.truetype(
            fallback,
            12,
        )
        font_path = getattr(font, "path", None)

        if not font_path:
            raise ValueError(
                f"Không tìm thấy font '{font_name}'"
            )

        return Path(font_path)

    canvas_dpi = 120.0

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(
        font_path: Path,
        font_size_pt: float,
    ) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(
                1,
                round(pt_to_canvas(font_size_pt)),
            ),
        )

    def measure_text_width(
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        font = load_font(
            font_path,
            font_size_pt,
        )

        if hasattr(font, "getlength"):
            return float(font.getlength(text))

        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(
        font_path: Path,
        font_size_pt: float,
        line_spacing: float,
    ) -> float:
        font = load_font(
            font_path,
            font_size_pt,
        )
        ascent, descent = font.getmetrics()

        return (
            float(ascent + descent)
            * line_spacing
        )

    def break_long_word(
        word: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        parts: list[str] = []
        current = ""

        for char in word:
            candidate = current + char

            if (
                current
                and measure_text_width(
                    candidate,
                    font_path,
                    font_size_pt,
                )
                > max_width
            ):
                parts.append(current)
                current = char
            else:
                current = candidate

        if current:
            parts.append(current)

        return parts or [""]

    def wrap_text(
        text: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        result: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                result.append("")
                continue

            current = ""

            for word in words:
                if (
                    measure_text_width(
                        word,
                        font_path,
                        font_size_pt,
                    )
                    > max_width
                ):
                    pieces = break_long_word(
                        word,
                        font_path,
                        font_size_pt,
                        max_width,
                    )
                else:
                    pieces = [word]

                for piece in pieces:
                    candidate = (
                        piece
                        if not current
                        else f"{current} {piece}"
                    )

                    if (
                        not current
                        or measure_text_width(
                            candidate,
                            font_path,
                            font_size_pt,
                        )
                        <= max_width
                    ):
                        current = candidate
                    else:
                        result.append(current)
                        current = piece

            if current:
                result.append(current)

        return result or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        max_width: float,
        line_spacing: float,
        padding: float = 4,
    ) -> dict:
        lines = wrap_text(
            text,
            font_path,
            font_size,
            max_width,
        )

        line_height = measure_line_height(
            font_path,
            font_size,
            line_spacing,
        )

        return {
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines) * line_height
                + padding
            ),
        }

    # =====================================================
    # Typography
    # =====================================================

    title_font_name = "Arial"
    heading_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=True,
    )
    heading_font_path = resolve_font_path(
        heading_font_name,
        bold=True,
    )
    body_font_path = resolve_font_path(
        body_font_name,
        bold=False,
    )

    title_font_size = 54.0
    title_min_font_size = 38.0

    heading_font_size = 36.0
    heading_min_font_size = 26.0

    body_font_size = 26.0
    body_min_font_size = 18.0

    title_line_spacing = 0.95
    heading_line_spacing = 0.98
    body_line_spacing = 1.08

    title_to_items_gap = 72.0
    heading_to_body_gap = 12.0
    item_gap = 70.0

    minimum_title_gap = 36.0
    minimum_item_gap = 28.0

    # =====================================================
    # Fit toàn bộ layout
    # =====================================================

    def calculate_layouts(
        current_title_size: float,
        current_heading_size: float,
        current_body_size: float,
    ) -> dict:
        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=current_title_size,
            max_width=content_width,
            line_spacing=title_line_spacing,
            padding=6,
        )

        item_layouts: list[dict] = []

        for item_title, item_description in zip(
            idea_titles,
            idea_descriptions,
        ):
            heading_layout = layout_text(
                item_title,
                font_path=heading_font_path,
                font_size=current_heading_size,
                max_width=content_width,
                line_spacing=heading_line_spacing,
                padding=4,
            )

            body_layout = layout_text(
                item_description,
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=content_width,
                line_spacing=body_line_spacing,
                padding=4,
            )

            item_layouts.append(
                {
                    "heading": heading_layout,
                    "body": body_layout,
                    "height": (
                        heading_layout["height"]
                        + heading_to_body_gap
                        + body_layout["height"]
                    ),
                }
            )

        total_height = (
            title_layout["height"]
            + title_to_items_gap
            + sum(
                item["height"]
                for item in item_layouts
            )
            + item_gap
            * max(
                0,
                len(item_layouts) - 1,
            )
        )

        return {
            "title": title_layout,
            "items": item_layouts,
            "total_height": total_height,
        }

    layouts = calculate_layouts(
        title_font_size,
        heading_font_size,
        body_font_size,
    )

    for _ in range(240):
        if layouts["total_height"] <= available_height:
            break

        changed = False

        if (
            title_to_items_gap > minimum_title_gap
            or item_gap > minimum_item_gap
        ):
            title_to_items_gap = max(
                minimum_title_gap,
                title_to_items_gap - 2,
            )
            item_gap = max(
                minimum_item_gap,
                item_gap - 2,
            )
            changed = True

        elif body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif heading_font_size > heading_min_font_size:
            heading_font_size = max(
                heading_min_font_size,
                heading_font_size - 0.5,
            )
            changed = True

        elif title_font_size > title_min_font_size:
            title_font_size = max(
                title_min_font_size,
                title_font_size - 0.5,
            )
            changed = True

        if not changed:
            break

        layouts = calculate_layouts(
            title_font_size,
            heading_font_size,
            body_font_size,
        )

    if layouts["total_height"] > available_height:
        raise ValueError(
            "Nội dung quá dài để đặt vừa slide mà không overlap. "
            f"Cần {layouts['total_height']:.1f}px nhưng vùng khả dụng "
            f"chỉ {available_height:.1f}px."
        )

    # Nếu nội dung ngắn, giữ bố cục gần ảnh mẫu nhưng
    # phân phối một phần khoảng trống còn lại vào item_gap.
    remaining_space = (
        available_height
        - layouts["total_height"]
    )

    if (
        remaining_space > 0
        and len(layouts["items"]) > 1
    ):
        added_gap = min(
            70.0,
            remaining_space
            / (len(layouts["items"]) - 1),
        )
        item_gap += added_gap

        layouts = calculate_layouts(
            title_font_size,
            heading_font_size,
            body_font_size,
        )

    # =====================================================
    # XML
    # =====================================================

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": str(canvas_width),
            "height": str(canvas_height),
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )

    slide = ET.SubElement(
        presentation,
        "slide",
        {"background": background_color},
    )

    def add(tag: str, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {
                key: str(value)
                for key, value in attrs.items()
                if value is not None
            },
        )

    def textbox(text: str, **attrs):
        node = add(
            "textbox",
            **attrs,
        )
        node.text = text
        return node

    add(
        "image",
        src=image_url,
        x=image_x,
        y=image_y,
        width=image_width,
        height=image_height,
    )

    cursor_y = float(content_top)

    textbox(
        layouts["title"]["text"],
        x=content_x,
        y=cursor_y,
        width=content_width,
        height=layouts["title"]["height"],
        font=title_font_name,
        size=layouts["title"]["font_size"],
        min_font_size=layouts["title"]["font_size"],
        bold="true",
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["title"]["lines"]),
        overflow="clip",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    cursor_y += (
        layouts["title"]["height"]
        + title_to_items_gap
    )

    for index, item in enumerate(
        layouts["items"]
    ):
        textbox(
            item["heading"]["text"],
            x=content_x,
            y=cursor_y,
            width=content_width,
            height=item["heading"]["height"],
            font=heading_font_name,
            size=item["heading"]["font_size"],
            min_font_size=item["heading"]["font_size"],
            bold="true",
            color=heading_color,
            align="left",
            vertical_align="top",
            single_line="false",
            max_lines=len(item["heading"]["lines"]),
            overflow="clip",
            line_spacing=heading_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        cursor_y += (
            item["heading"]["height"]
            + heading_to_body_gap
        )

        textbox(
            item["body"]["text"],
            x=content_x,
            y=cursor_y,
            width=content_width,
            height=item["body"]["height"],
            font=body_font_name,
            size=item["body"]["font_size"],
            min_font_size=item["body"]["font_size"],
            color=body_color,
            align="left",
            vertical_align="top",
            single_line="false",
            max_lines=len(item["body"]["lines"]),
            overflow="clip",
            line_spacing=body_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        cursor_y += item["body"]["height"]

        if index < len(layouts["items"]) - 1:
            cursor_y += item_gap

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

def generate_three_ideas_slide_xml(
    title: str = "THREE IDEAS",
    idea_titles: list[str] = [
        "MERCURY",
        "MARS",
        "VENUS",
    ],
    idea_descriptions: list[str] = [
        (
            "Mercury is the closest planet to the Sun and the Mercury is the closest planet to the Sun and the "
            "smallest one in the Solar System."
        ),
        (
            "Despite being red, Mars is actually a cold place. "
            "It’s full of iron oxide dust."
        ),
        (
            "Venus has a beautiful name and is the second "
            "planet from the Sun."
        ),
    ],
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1594035910387-fea47794261f"
        "?q=85&w=1200&auto=format&fit=crop"
    ),
    background_color: str = "#181818",
    title_color: str = "#FFFFFF",
    heading_color: str = "#FFFFFF",
    body_color: str = "#F2F2F2",
) -> str:
    """
    Generate XML for a split-layout ideas slide.

    The layout features a dark content area on the left and a
    full-height image panel on the right. The left side contains
    a large title at the top and multiple vertically stacked idea
    sections. Each section includes a heading and a centered
    description below it.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    if len(idea_titles) != len(idea_descriptions):
        raise ValueError(
            "idea_titles and idea_descriptions must have the same length"
        )

    if not idea_titles:
        raise ValueError("the slide must contain at least one idea")

    # =====================================================
    # Canvas and layout regions
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    content_x = 0
    content_y = 0
    content_width = 1065
    content_height = 900

    image_x = 1065
    image_y = 0
    image_width = 535
    image_height = 900

    text_x = 58
    text_width = 930

    content_top = 42
    content_bottom = 825
    available_height = content_bottom - content_top

    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            char.lower()
            for char in name
            if char.isalnum()
        )

    def font_directories() -> list[Path]:
        directories: list[Path] = []

        windir = os.environ.get("WINDIR")
        if windir:
            directories.append(Path(windir) / "Fonts")

        directories.extend(
            [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".fonts",
                Path.home() / "Library/Fonts",
                Path("/Library/Fonts"),
            ]
        )

        return [
            path
            for path in directories
            if path.exists()
        ]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
    ) -> Path:
        aliases = {
            "Arial": "arial",
            "Calibri": "calibri",
            "Aptos": "aptos",
            "Helvetica": "helvetica",
        }

        normalized = normalize_font_name(
            aliases.get(font_name, font_name)
        )

        candidates: list[tuple[int, Path]] = []

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {
                    ".ttf",
                    ".otf",
                    ".ttc",
                }:
                    continue

                stem = normalize_font_name(path.stem)

                if normalized not in stem:
                    continue

                score = 70

                if stem == normalized:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in (
                        "bold",
                        "bd",
                        "semibold",
                    )
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 10
                elif has_bold:
                    score -= 10

                candidates.append((score, path))

        if candidates:
            candidates.sort(
                key=lambda item: item[0],
                reverse=True,
            )
            return candidates[0][1]

        fallback = (
            "DejaVuSans-Bold.ttf"
            if bold
            else "DejaVuSans.ttf"
        )

        font = ImageFont.truetype(
            fallback,
            12,
        )
        font_path = getattr(font, "path", None)

        if not font_path:
            raise ValueError(
                f"Font '{font_name}' was not found"
            )

        return Path(font_path)

    canvas_dpi = 120.0

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(
        font_path: Path,
        font_size_pt: float,
    ) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(
                1,
                round(pt_to_canvas(font_size_pt)),
            ),
        )

    def measure_text_width(
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        font = load_font(
            font_path,
            font_size_pt,
        )

        if hasattr(font, "getlength"):
            return float(font.getlength(text))

        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(
        font_path: Path,
        font_size_pt: float,
        line_spacing: float,
    ) -> float:
        font = load_font(
            font_path,
            font_size_pt,
        )
        ascent, descent = font.getmetrics()

        return float(ascent + descent) * line_spacing

    def break_long_word(
        word: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        parts: list[str] = []
        current = ""

        for char in word:
            candidate = current + char

            if (
                current
                and measure_text_width(
                    candidate,
                    font_path,
                    font_size_pt,
                )
                > max_width
            ):
                parts.append(current)
                current = char
            else:
                current = candidate

        if current:
            parts.append(current)

        return parts or [""]

    def wrap_text(
        text: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        result: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                result.append("")
                continue

            current = ""

            for word in words:
                if (
                    measure_text_width(
                        word,
                        font_path,
                        font_size_pt,
                    )
                    > max_width
                ):
                    pieces = break_long_word(
                        word,
                        font_path,
                        font_size_pt,
                        max_width,
                    )
                else:
                    pieces = [word]

                for piece in pieces:
                    candidate = (
                        piece
                        if not current
                        else f"{current} {piece}"
                    )

                    if (
                        not current
                        or measure_text_width(
                            candidate,
                            font_path,
                            font_size_pt,
                        )
                        <= max_width
                    ):
                        current = candidate
                    else:
                        result.append(current)
                        current = piece

            if current:
                result.append(current)

        return result or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        max_width: float,
        line_spacing: float,
        padding: float = 4,
    ) -> dict:
        lines = wrap_text(
            text,
            font_path,
            font_size,
            max_width,
        )

        line_height = measure_line_height(
            font_path,
            font_size,
            line_spacing,
        )

        return {
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": len(lines) * line_height + padding,
        }

    # =====================================================
    # Typography settings
    # =====================================================

    title_font_name = "Arial"
    heading_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=True,
    )
    heading_font_path = resolve_font_path(
        heading_font_name,
        bold=True,
    )
    body_font_path = resolve_font_path(
        body_font_name,
        bold=False,
    )

    title_font_size = 58.0
    title_min_font_size = 40.0

    heading_font_size = 38.0
    heading_min_font_size = 26.0

    body_font_size = 27.0
    body_min_font_size = 18.0

    title_line_spacing = 0.95
    heading_line_spacing = 0.98
    body_line_spacing = 1.08

    title_to_items_gap = 70.0
    heading_to_body_gap = 10.0
    item_gap = 58.0

    minimum_title_gap = 32.0
    minimum_item_gap = 22.0

    # =====================================================
    # Fit the complete content layout
    # =====================================================

    def calculate_layouts(
        current_title_size: float,
        current_heading_size: float,
        current_body_size: float,
    ) -> dict:
        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=current_title_size,
            max_width=text_width,
            line_spacing=title_line_spacing,
            padding=6,
        )

        item_layouts: list[dict] = []

        for idea_title, idea_description in zip(
            idea_titles,
            idea_descriptions,
        ):
            heading_layout = layout_text(
                idea_title,
                font_path=heading_font_path,
                font_size=current_heading_size,
                max_width=text_width,
                line_spacing=heading_line_spacing,
                padding=3,
            )

            body_layout = layout_text(
                idea_description,
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=text_width,
                line_spacing=body_line_spacing,
                padding=3,
            )

            item_layouts.append(
                {
                    "heading": heading_layout,
                    "body": body_layout,
                    "height": (
                        heading_layout["height"]
                        + heading_to_body_gap
                        + body_layout["height"]
                    ),
                }
            )

        total_height = (
            title_layout["height"]
            + title_to_items_gap
            + sum(
                item["height"]
                for item in item_layouts
            )
            + item_gap
            * max(
                0,
                len(item_layouts) - 1,
            )
        )

        return {
            "title": title_layout,
            "items": item_layouts,
            "total_height": total_height,
        }

    layouts = calculate_layouts(
        title_font_size,
        heading_font_size,
        body_font_size,
    )

    for _ in range(260):
        if layouts["total_height"] <= available_height:
            break

        changed = False

        if (
            title_to_items_gap > minimum_title_gap
            or item_gap > minimum_item_gap
        ):
            title_to_items_gap = max(
                minimum_title_gap,
                title_to_items_gap - 2,
            )
            item_gap = max(
                minimum_item_gap,
                item_gap - 2,
            )
            changed = True

        elif body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif heading_font_size > heading_min_font_size:
            heading_font_size = max(
                heading_min_font_size,
                heading_font_size - 0.5,
            )
            changed = True

        elif title_font_size > title_min_font_size:
            title_font_size = max(
                title_min_font_size,
                title_font_size - 0.5,
            )
            changed = True

        if not changed:
            break

        layouts = calculate_layouts(
            title_font_size,
            heading_font_size,
            body_font_size,
        )

    if layouts["total_height"] > available_height:
        raise ValueError(
            "The content is too long to fit without overlap. "
            f"Required height: {layouts['total_height']:.1f}px; "
            f"available height: {available_height:.1f}px."
        )

    remaining_space = available_height - layouts["total_height"]

    if (
        remaining_space > 0
        and len(layouts["items"]) > 1
    ):
        item_gap += min(
            45.0,
            remaining_space
            / max(1, len(layouts["items"]) - 1),
        )

        layouts = calculate_layouts(
            title_font_size,
            heading_font_size,
            body_font_size,
        )

    # =====================================================
    # Build XML
    # =====================================================

    presentation = ET.Element(
        "presentation",
        {
            "schemaVersion": "1.0",
            "width": str(canvas_width),
            "height": str(canvas_height),
            "slideWidthInches": "13.333",
            "slideHeightInches": "7.5",
        },
    )

    slide = ET.SubElement(
        presentation,
        "slide",
        {"background": background_color},
    )

    def add(tag: str, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {
                key: str(value)
                for key, value in attrs.items()
                if value is not None
            },
        )

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    add(
        "image",
        src=image_url,
        x=image_x,
        y=image_y,
        width=image_width,
        height=image_height,
    )

    cursor_y = float(content_top)

    textbox(
        layouts["title"]["text"],
        x=text_x,
        y=cursor_y,
        width=text_width,
        height=layouts["title"]["height"],
        font=title_font_name,
        size=layouts["title"]["font_size"],
        min_font_size=layouts["title"]["font_size"],
        bold="true",
        color=title_color,
        align="right",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["title"]["lines"]),
        overflow="clip",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    cursor_y += (
        layouts["title"]["height"]
        + title_to_items_gap
    )

    for index, item in enumerate(
        layouts["items"]
    ):
        textbox(
            item["heading"]["text"],
            x=text_x,
            y=cursor_y,
            width=text_width,
            height=item["heading"]["height"],
            font=heading_font_name,
            size=item["heading"]["font_size"],
            min_font_size=item["heading"]["font_size"],
            bold="true",
            color=heading_color,
            align="right",
            vertical_align="top",
            single_line="false",
            max_lines=len(item["heading"]["lines"]),
            overflow="clip",
            line_spacing=heading_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        cursor_y += (
            item["heading"]["height"]
            + heading_to_body_gap
        )

        textbox(
            item["body"]["text"],
            x=text_x,
            y=cursor_y,
            width=text_width,
            height=item["body"]["height"],
            font=body_font_name,
            size=item["body"]["font_size"],
            min_font_size=item["body"]["font_size"],
            color=body_color,
            align="right",
            vertical_align="top",
            single_line="false",
            max_lines=len(item["body"]["lines"]),
            overflow="clip",
            line_spacing=body_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        cursor_y += item["body"]["height"]

        if index < len(layouts["items"]) - 1:
            cursor_y += item_gap

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
