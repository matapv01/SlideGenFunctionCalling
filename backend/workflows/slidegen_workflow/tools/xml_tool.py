from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom


#Slide Intro
def generate_modern_cover_slide_xml(
    title: str = "THIS IS YOUR PRESENTATION TITLE THIS IS YOUR PRESENTATION TITLE",
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1497366754035-f200968a6e72"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#F4F4F4",
    dark_panel_color: str = "#23242B",
    accent_color: str = "#98F033",
    title_color: str = "#98F033",
) -> str:
    """
    Generate XML for a modern cover slide.

    The layout features a bright photo background on the right,
    a dark diagonal panel on the left, a bold accent bar aligned
    directly with the diagonal boundary, and a large title inside
    the dark panel.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    # =====================================================
    # Canvas and layout regions
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    image_x = 515
    image_y = 0
    image_width = 1085
    image_height = 900

    title_x = 78
    title_y = 210
    title_max_height = 420
    title_right_padding = 40.0

    panel_top_x = 965.0
    panel_bottom_x = 595.0
    panel_top_y = 0.0
    panel_bottom_y = 900.0

    dark_panel_points = (
        f"0,0 "
        f"{panel_top_x:.2f},0 "
        f"{panel_bottom_x:.2f},900 "
        f"0,900"
    )

    accent_top_y = 145.0
    accent_bottom_y = 708.0
    accent_width = 48.0
    accent_overlap = 5.0

    def diagonal_x_at_y(y: float) -> float:
        ratio = (
            (y - panel_top_y)
            / (panel_bottom_y - panel_top_y)
        )

        return (
            panel_top_x
            + ratio
            * (panel_bottom_x - panel_top_x)
        )

    def title_width_for_height(text_height: float) -> float:
        title_bottom_y = min(
            canvas_height,
            title_y + min(text_height, title_max_height),
        )

        return max(
            1.0,
            diagonal_x_at_y(title_bottom_y)
            - title_x
            - title_right_padding,
        )

    accent_top_inner_x = (
        diagonal_x_at_y(accent_top_y)
        - accent_overlap
    )

    accent_bottom_inner_x = (
        diagonal_x_at_y(accent_bottom_y)
        - accent_overlap
    )

    accent_points = (
        f"{accent_top_inner_x:.2f},{accent_top_y:.2f} "
        f"{accent_top_inner_x + accent_width:.2f},{accent_top_y:.2f} "
        f"{accent_bottom_inner_x + accent_width:.2f},{accent_bottom_y:.2f} "
        f"{accent_bottom_inner_x:.2f},{accent_bottom_y:.2f}"
    )

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
                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 6,
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

    def longest_word_width(
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        words = text.split()

        if not words:
            return 0.0

        return max(
            measure_text_width(
                word,
                font_path,
                font_size_pt,
            )
            for word in words
        )

    # =====================================================
    # Typography settings
    # =====================================================

    title_font_name = "Arial"
    title_font_path = resolve_font_path(
        title_font_name,
        bold=False,
    )

    title_font_size = 64.0
    title_min_font_size = 34.0
    title_line_spacing = 0.96

    def layout_title_at_size(font_size: float) -> dict:
        title_width = title_width_for_height(title_max_height)

        for _ in range(8):
            layout = layout_text(
                title,
                font_path=title_font_path,
                font_size=font_size,
                max_width=title_width,
                line_spacing=title_line_spacing,
                padding=8,
            )

            next_title_width = title_width_for_height(
                layout["height"]
            )

            if abs(next_title_width - title_width) < 0.5:
                layout["width"] = title_width
                return layout

            title_width = next_title_width

        layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=font_size,
            max_width=title_width,
            line_spacing=title_line_spacing,
            padding=8,
        )
        layout["width"] = title_width
        return layout

    title_layout = layout_title_at_size(title_font_size)

    for _ in range(140):
        if (
            title_layout["height"] <= title_max_height
            and len(title_layout["lines"]) <= 5
            and longest_word_width(
                title,
                title_font_path,
                title_font_size,
            )
            <= title_layout["width"]
        ):
            break

        if title_font_size <= title_min_font_size:
            break

        title_font_size = max(
            title_min_font_size,
            title_font_size - 0.5,
        )

        title_layout = layout_title_at_size(title_font_size)

    if title_layout["height"] > title_max_height:
        raise ValueError(
            "The title is too long to fit the slide without overlap"
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

    add(
        "polygon",
        points=dark_panel_points,
        fill=dark_panel_color,
        line_color="none",
    )

    add(
        "polygon",
        points=accent_points,
        fill=accent_color,
        line_color="none",
    )

    textbox(
        title,
        x=title_x,
        y=title_y,
        width=title_layout["width"],
        height=title_layout["height"],
        font=title_font_name,
        size=title_layout["font_size"],
        min_font_size=title_layout["font_size"],
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
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

def generate_it_sales_proposal_cover_inline_vector_xml_closer(
    brand_name: str = "FORGE",
    title: str = "IT Software Sales Proposal",
    subtitle: str = "Modern productivity for secure, high-performing teams",
    prepared_for: str = "Value Financials",
    date_text: str = "June 2035",
    background_color: str = "#1A0B3A",
    title_color: str = "#F7F2FF",
    subtitle_color: str = "#FFFFFF",
    subtitle_bar_color: str = "#6545A2",
    brand_color: str = "#F7F2FF",
    footer_color: str = "#F7F2FF",
) -> str:
    """
    Generate XML for a premium software proposal cover slide.

    The layout features an inline vector ribbon decoration on the left,
    a compact brand mark near the top-right, a large proposal title,
    a horizontal subtitle bar, and two footer labels along the bottom.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    if not subtitle.strip():
        raise ValueError("subtitle must not be empty")

    # =====================================================
    # Canvas and layout regions
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    decoration_x = 0.0
    decoration_y = 0.0
    decoration_width = 760.0
    decoration_height = 900.0

    content_x = 600.0
    content_right = 1530.0
    content_width = content_right - content_x

    brand_y = 105.0
    brand_icon_width = 58.0
    brand_gap = 18.0

    main_top = 245.0
    main_bottom = 700.0
    available_main_height = main_bottom - main_top

    title_to_subtitle_gap = 42.0
    minimum_gap = 20.0

    footer_y = 825.0
    footer_left_x = content_x
    footer_left_width = 470.0
    footer_right_width = 200.0
    footer_right_x = content_right - footer_right_width


    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
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
            directory
            for directory in directories
            if directory.exists()
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

        font = ImageFont.truetype(fallback, 12)
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

        return (
            float(ascent + descent)
            * line_spacing
        )

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
                word_width = measure_text_width(
                    word,
                    font_path,
                    font_size_pt,
                )

                if word_width > max_width:
                    raise ValueError(
                        f"The word '{word}' is wider than "
                        "the available text area"
                    )

                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 3.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines) * line_height
                + padding
            ),
        }

    # =====================================================
    # Typography and responsive fitting
    # =====================================================

    title_font_name = "Arial"
    subtitle_font_name = "Arial"
    brand_font_name = "Arial"
    footer_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=False,
    )
    subtitle_font_path = resolve_font_path(
        subtitle_font_name,
        bold=False,
    )
    brand_font_path = resolve_font_path(
        brand_font_name,
        bold=True,
    )
    footer_font_path = resolve_font_path(
        footer_font_name,
        bold=False,
    )

    title_font_size = 70.0
    title_min_font_size = 42.0

    subtitle_font_size = 26.0
    subtitle_min_font_size = 17.0

    title_line_spacing = 0.95
    subtitle_line_spacing = 1.0

    subtitle_bar_padding_x = 34.0
    subtitle_bar_padding_y = 12.0

    def calculate_main_layout(
        current_title_size: float,
        current_subtitle_size: float,
        current_gap: float,
    ) -> dict:
        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=current_title_size,
            max_width=content_width,
            line_spacing=title_line_spacing,
            padding=4,
        )

        subtitle_text_width = max(
            1.0,
            content_width
            - 2 * subtitle_bar_padding_x,
        )

        subtitle_layout = layout_text(
            subtitle,
            font_path=subtitle_font_path,
            font_size=current_subtitle_size,
            max_width=subtitle_text_width,
            line_spacing=subtitle_line_spacing,
            padding=3,
        )

        subtitle_bar_height = (
            subtitle_layout["height"]
            + 2 * subtitle_bar_padding_y
        )

        total_height = (
            title_layout["height"]
            + current_gap
            + subtitle_bar_height
        )

        group_y = (
            main_top
            + max(
                0.0,
                available_main_height - total_height,
            )
            / 2
        )

        return {
            "title": title_layout,
            "subtitle": subtitle_layout,
            "subtitle_bar_height": subtitle_bar_height,
            "total_height": total_height,
            "group_y": group_y,
        }

    layouts = calculate_main_layout(
        title_font_size,
        subtitle_font_size,
        title_to_subtitle_gap,
    )

    for _ in range(220):
        if layouts["total_height"] <= available_main_height:
            break

        changed = False

        if title_to_subtitle_gap > minimum_gap:
            title_to_subtitle_gap = max(
                minimum_gap,
                title_to_subtitle_gap - 1,
            )
            changed = True

        elif subtitle_font_size > subtitle_min_font_size:
            subtitle_font_size = max(
                subtitle_min_font_size,
                subtitle_font_size - 0.5,
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

        layouts = calculate_main_layout(
            title_font_size,
            subtitle_font_size,
            title_to_subtitle_gap,
        )

    if layouts["total_height"] > available_main_height:
        raise ValueError(
            "The proposal title and subtitle are too long "
            "to fit without overlap"
        )

    title_y = layouts["group_y"]
    subtitle_bar_y = (
        title_y
        + layouts["title"]["height"]
        + title_to_subtitle_gap
    )
    subtitle_y = (
        subtitle_bar_y
        + subtitle_bar_padding_y
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

    svg_node = add(
        "svg",
        x=decoration_x,
        y=decoration_y,
        width=decoration_width,
        height=decoration_height,
        pixel_width=900,
        pixel_height=900,
    )
    svg_node.text = """
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="900" viewBox="0 0 900 900" style="background: transparent;">
  <defs>
    <linearGradient id="outer" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#4A2C82"/>
      <stop offset="45%" stop-color="#805AD5"/>
      <stop offset="100%" stop-color="#B794F4"/>
    </linearGradient>
    <linearGradient id="middle" x1="0" y1="0" x2="1" y2="0.9">
      <stop offset="0%" stop-color="#6B46C1"/>
      <stop offset="55%" stop-color="#9F7AEA"/>
      <stop offset="100%" stop-color="#D6BCFA"/>
    </linearGradient>
    <linearGradient id="inner" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#805AD5"/>
      <stop offset="50%" stop-color="#B794F4"/>
      <stop offset="100%" stop-color="#E9D8FD"/>
    </linearGradient>
    <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="10" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <g opacity="0.18">
    <rect x="360" y="58" width="250" height="190" fill="#B794F4"/>
    <rect x="360" y="384" width="250" height="190" fill="#9F7AEA"/>
    <rect x="108" y="575" width="205" height="300" fill="#8B5CF6"/>
  </g>

  <path
    d="M0,210 C185,35 420,28 620,58 C650,332 540,602 305,760 C170,850 63,880 0,882 Z"
    fill="url(#outer)"
    opacity="0.96"/>

  <path
    d="M0,410 C180,210 382,194 590,250 C548,470 438,635 258,760 C132,846 52,870 0,876 Z"
    fill="url(#middle)"
    opacity="0.98"/>

  <path
    d="M0,640 C154,410 338,350 535,384 C470,580 363,704 211,798 C112,858 44,874 0,878 Z"
    fill="url(#inner)"
    opacity="0.98"
    filter="url(#softGlow)"/>

  <path
    d="M150,900 C145,750 200,636 312,598 C390,571 457,590 510,640 C412,734 302,824 150,900 Z"
    fill="#8B5CF6"
    opacity="0.82"/>
</svg>
""".strip()

    textbox(
        "✣",
        x=content_x,
        y=brand_y,
        width=brand_icon_width,
        height=58,
        font=brand_font_name,
        font_path=str(brand_font_path),
        size=42,
        min_font_size=42,
        bold="true",
        color=brand_color,
        align="center",
        vertical_align="middle",
        single_line="true",
        max_lines=1,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.0,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        brand_name,
        x=content_x + brand_icon_width + brand_gap,
        y=brand_y + 5,
        width=260,
        height=50,
        font=brand_font_name,
        font_path=str(brand_font_path),
        size=30,
        min_font_size=22,
        bold="true",
        color=brand_color,
        align="left",
        vertical_align="middle",
        single_line="false",
        max_lines=2,
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=1.0,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        layouts["title"]["source_text"],
        x=content_x,
        y=title_y,
        width=content_width,
        height=layouts["title"]["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=layouts["title"]["font_size"],
        min_font_size=layouts["title"]["font_size"],
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["title"]["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    add(
        "shape",
        type="rect",
        x=content_x,
        y=subtitle_bar_y,
        width=content_width,
        height=layouts["subtitle_bar_height"],
        fill=subtitle_bar_color,
        line_color="none",
    )

    textbox(
        layouts["subtitle"]["source_text"],
        x=content_x + subtitle_bar_padding_x,
        y=subtitle_y,
        width=content_width - 2 * subtitle_bar_padding_x,
        height=layouts["subtitle"]["height"],
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=layouts["subtitle"]["font_size"],
        min_font_size=layouts["subtitle"]["font_size"],
        color=subtitle_color,
        align="center",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["subtitle"]["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=subtitle_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        f"Prepared for {prepared_for}",
        x=footer_left_x,
        y=footer_y,
        width=footer_left_width,
        height=42,
        font=footer_font_name,
        font_path=str(footer_font_path),
        size=22,
        min_font_size=16,
        color=footer_color,
        align="left",
        vertical_align="middle",
        single_line="false",
        max_lines=2,
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=1.0,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        date_text,
        x=footer_right_x,
        y=footer_y,
        width=footer_right_width,
        height=42,
        font=footer_font_name,
        font_path=str(footer_font_path),
        size=22,
        min_font_size=16,
        color=footer_color,
        align="right",
        vertical_align="middle",
        single_line="false",
        max_lines=2,
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=1.0,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
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

#slide transition
def generate_transition_headline_slide_xml(
    title: str = "Messi và sự nghiệp của anh ấy",
    subtitle: str = "Let’s start with the first set of slides Let’s start with the first set of slides",
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1522202176988-66273c2fd55f"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#FFFFFF",
    dark_panel_color: str = "#292A30",
    accent_color: str = "#98F20F",
    title_color: str = "#98F20F",
    subtitle_color: str = "#2ED329",
) -> str:
    """
    Generate XML for a transition slide with a large headline.

    The layout features a full-slide image, a dark diagonal panel
    on the left, a bright accent bar centered on the diagonal edge,
    a large transition headline, and a smaller supporting subtitle
    placed below it.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    if not subtitle.strip():
        raise ValueError("subtitle must not be empty")

    # =====================================================
    # Canvas and panel geometry
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    image_x = 0
    image_y = 0
    image_width = 1600
    image_height = 900

    panel_top_x = 760.0
    panel_bottom_x = 340.0
    panel_top_y = 0.0
    panel_bottom_y = 900.0

    dark_panel_points = (
        f"0,0 "
        f"{panel_top_x:.2f},0 "
        f"{panel_bottom_x:.2f},900 "
        f"0,900"
    )

    accent_top_y = 275.0
    accent_bottom_y = 720.0
    accent_width = 64.0

    def diagonal_x_at_y(y: float) -> float:
        ratio = (
            (y - panel_top_y)
            / (panel_bottom_y - panel_top_y)
        )

        return (
            panel_top_x
            + ratio
            * (panel_bottom_x - panel_top_x)
        )

    accent_top_center_x = diagonal_x_at_y(
        accent_top_y
    )
    accent_bottom_center_x = diagonal_x_at_y(
        accent_bottom_y
    )
    accent_half_width = accent_width / 2.0

    accent_points = (
        f"{accent_top_center_x - accent_half_width:.2f},"
        f"{accent_top_y:.2f} "
        f"{accent_top_center_x + accent_half_width:.2f},"
        f"{accent_top_y:.2f} "
        f"{accent_bottom_center_x + accent_half_width:.2f},"
        f"{accent_bottom_y:.2f} "
        f"{accent_bottom_center_x - accent_half_width:.2f},"
        f"{accent_bottom_y:.2f}"
    )

    text_left = 70.0
    text_right_padding = 24.0

    title_top_limit = 145.0
    title_bottom_limit = 735.0
    text_center_y = 450.0

    title_to_subtitle_gap = 32.0
    minimum_gap = 12.0

    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
        )

    def font_directories() -> list[Path]:
        directories: list[Path] = []

        windir = os.environ.get("WINDIR")
        if windir:
            directories.append(
                Path(windir) / "Fonts"
            )

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
            directory
            for directory in directories
            if directory.exists()
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
        font_path = getattr(
            font,
            "path",
            None,
        )

        if not font_path:
            raise ValueError(
                f"Font '{font_name}' was not found"
            )

        return Path(font_path)

    canvas_dpi = 120.0

    def pt_to_canvas(
        point_size: float,
    ) -> float:
        return (
            point_size
            * canvas_dpi
            / 72.0
        )

    def load_font(
        font_path: Path,
        font_size_pt: float,
    ) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(
                1,
                round(
                    pt_to_canvas(font_size_pt)
                ),
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
            return float(
                font.getlength(text)
            )

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
                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 2.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines)
                * line_height
                + padding
            ),
        }

    def longest_word_width(
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        words = text.split()

        if not words:
            return 0.0

        return max(
            measure_text_width(
                word,
                font_path,
                font_size_pt,
            )
            for word in words
        )

    # =====================================================
    # Typography and responsive fitting
    # =====================================================

    title_font_name = "Arial"
    subtitle_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=True,
    )
    subtitle_font_path = resolve_font_path(
        subtitle_font_name,
        bold=False,
    )

    subtitle_font_size = 20.0
    subtitle_min_font_size = 14.0
    title_min_font_size = 34.0
    title_ratio = 2
    title_font_size = subtitle_font_size * title_ratio

    title_line_spacing = 0.98
    subtitle_line_spacing = 1.0

    def text_width_for_block(
        block_y: float,
        block_height: float,
    ) -> float:
        block_bottom_y = (
            block_y
            + block_height
        )

        safe_right_edge = (
            diagonal_x_at_y(
                block_bottom_y
            )
            - accent_half_width
            - text_right_padding
        )

        return max(
            1.0,
            safe_right_edge - text_left,
        )

    def calculate_layouts(
        current_subtitle_size: float,
        current_gap: float,
    ) -> dict:
        current_title_size = max(
            title_min_font_size,
            current_subtitle_size * title_ratio,
        )

        estimated_group_y = text_center_y
        estimated_group_height = 170.0
        result = None

        for _ in range(12):
            estimated_width = text_width_for_block(
                estimated_group_y,
                estimated_group_height,
            )

            title_layout = layout_text(
                title,
                font_path=title_font_path,
                font_size=current_title_size,
                max_width=estimated_width,
                line_spacing=title_line_spacing,
                padding=2,
            )

            subtitle_layout = layout_text(
                subtitle,
                font_path=subtitle_font_path,
                font_size=current_subtitle_size,
                max_width=estimated_width,
                line_spacing=subtitle_line_spacing,
                padding=2,
            )

            total_height = (
                title_layout["height"]
                + current_gap
                + subtitle_layout["height"]
            )

            group_y = max(
                title_top_limit,
                min(
                    text_center_y
                    - total_height / 2,
                    title_bottom_limit
                    - total_height,
                ),
            )

            title_width = text_width_for_block(
                group_y,
                title_layout["height"],
            )
            title_layout = layout_text(
                title,
                font_path=title_font_path,
                font_size=current_title_size,
                max_width=title_width,
                line_spacing=title_line_spacing,
                padding=2,
            )

            subtitle_y = (
                group_y
                + title_layout["height"]
                + current_gap
            )
            subtitle_width = text_width_for_block(
                subtitle_y,
                subtitle_layout["height"],
            )
            subtitle_layout = layout_text(
                subtitle,
                font_path=subtitle_font_path,
                font_size=current_subtitle_size,
                max_width=subtitle_width,
                line_spacing=subtitle_line_spacing,
                padding=2,
            )

            total_height = (
                title_layout["height"]
                + current_gap
                + subtitle_layout["height"]
            )

            group_y = max(
                title_top_limit,
                min(
                    text_center_y
                    - total_height / 2,
                    title_bottom_limit
                    - total_height,
                ),
            )

            title_width = text_width_for_block(
                group_y,
                title_layout["height"],
            )
            subtitle_y = (
                group_y
                + title_layout["height"]
                + current_gap
            )
            subtitle_width = text_width_for_block(
                subtitle_y,
                subtitle_layout["height"],
            )

            result = {
                "title": title_layout,
                "title_width": title_width,
                "subtitle": subtitle_layout,
                "subtitle_width": subtitle_width,
                "gap": current_gap,
                "total_height": total_height,
                "group_y": group_y,
            }

            if (
                abs(group_y - estimated_group_y) < 0.5
                and abs(total_height - estimated_group_height) < 0.5
            ):
                break

            estimated_group_y = group_y
            estimated_group_height = total_height

        return result

    layouts = calculate_layouts(
        subtitle_font_size,
        title_to_subtitle_gap,
    )

    for _ in range(160):
        width_fits = (
            longest_word_width(
                title,
                title_font_path,
                layouts["title"]["font_size"],
            )
            <= layouts["title_width"]
            and longest_word_width(
                subtitle,
                subtitle_font_path,
                layouts["subtitle"]["font_size"],
            )
            <= layouts["subtitle_width"]
        )

        fits = (
            layouts["group_y"] >= title_top_limit
            and layouts["group_y"] + layouts["total_height"] <= title_bottom_limit
            and width_fits
        )

        if fits:
            break

        changed = False

        if title_to_subtitle_gap > minimum_gap:
            title_to_subtitle_gap = max(
                minimum_gap,
                title_to_subtitle_gap - 1,
            )
            changed = True

        elif subtitle_font_size > subtitle_min_font_size:
            subtitle_font_size = max(
                subtitle_min_font_size,
                subtitle_font_size - 0.5,
            )
            changed = True

        if not changed:
            break

        layouts = calculate_layouts(
            subtitle_font_size,
            title_to_subtitle_gap,
        )

    if (
        layouts["group_y"] < title_top_limit
        or layouts["group_y"] + layouts["total_height"] > title_bottom_limit
    ):
        raise ValueError(
            "The transition text is too long to fit without overlap"
        )

    title_y = layouts["group_y"]
    subtitle_y = (
        title_y
        + layouts["title"]["height"]
        + layouts["gap"]
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

    add(
        "polygon",
        points=dark_panel_points,
        fill=dark_panel_color,
        line_color="none",
    )

    add(
        "polygon",
        points=accent_points,
        fill=accent_color,
        line_color="none",
    )

    textbox(
        layouts["title"]["source_text"],
        x=text_left,
        y=title_y,
        width=layouts["title_width"],
        height=layouts["title"]["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=layouts["title"]["font_size"],
        min_font_size=layouts["title"]["font_size"],
        bold="true",
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["title"]["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        layouts["subtitle"]["source_text"],
        x=text_left,
        y=subtitle_y,
        width=layouts["subtitle_width"],
        height=layouts["subtitle"]["height"],
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=layouts["subtitle"]["font_size"],
        min_font_size=layouts["subtitle"]["font_size"],
        color=subtitle_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["subtitle"]["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=subtitle_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
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

# Slide content

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


def generate_our_history_slide_xml(
    title: str = "OUR HISTORY",
    event_titles: list[str] = [
        "SATURN",
        "MARS",
        "NEPTUNE",
    ],
    event_descriptions: list[str] = [
        "Saturn is composed of hydrogen and helium.",
        "Despite being red, Mars is actually a cold place.",
        "Neptune is the farthest planet from the Sun.",
        "Neptune is the farthest planet from the Sun.",

    ],
    event_years: list[str] = [
        "XX",
        "XX",
        "XX",
        "XX"
    ],
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1495474472287-4d71bcdd2085"
        "?q=85&w=1200&auto=format&fit=crop"
    ),
    background_color: str = "#151515",
    title_color: str = "#FFFFFF",
    heading_color: str = "#FFFFFF",
    body_color: str = "#F2F2F2",
    year_color: str = "#FFFFFF",
    line_color: str = "#E8E8E8",
) -> str:
    """
    Generate XML for a split-layout history slide.

    The layout features a dark content area on the left and a
    tall image panel on the right. The left area contains a large
    title at the top and multiple vertically stacked history
    sections. Each section includes a heading, a description,
    a year marker, and a thin vertical separator line.
    """


    canvas_width = 1600
    canvas_height = 900

    image_x = 1155
    image_y = 0
    image_width = 445
    image_height = 900

    content_x = 80
    content_width = 1000
    content_top = 60
    content_bottom = 835
    available_height = content_bottom - content_top

    title_block_x = 200
    title_block_width = 700

    text_column_x = 70
    text_column_width = 700

    year_column_x = 820
    year_column_width = 120

    line_x = 870

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
    year_font_name = "Arial"

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
    year_font_path = resolve_font_path(
        year_font_name,
        bold=True,
    )

    title_font_size = 56.0
    title_min_font_size = 38.0

    heading_font_size = 34.0
    heading_min_font_size = 24.0

    body_font_size = 25.0
    body_min_font_size = 17.0

    year_font_size = 28.0
    year_min_font_size = 20.0

    title_line_spacing = 0.95
    heading_line_spacing = 0.98
    body_line_spacing = 1.08
    year_line_spacing = 1.0

    title_to_items_gap = 64.0
    item_gap = 42.0
    heading_to_body_gap = 10.0

    minimum_title_gap = 30.0
    minimum_item_gap = 18.0

    # =====================================================
    # Fit the complete content layout
    # =====================================================

    def calculate_layouts(
        current_title_size: float,
        current_heading_size: float,
        current_body_size: float,
        current_year_size: float,
    ) -> dict:
        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=current_title_size,
            max_width=title_block_width,
            line_spacing=title_line_spacing,
            padding=6,
        )

        item_layouts: list[dict] = []

        for event_title, event_description, event_year in zip(
            event_titles,
            event_descriptions,
            event_years,
        ):
            heading_layout = layout_text(
                event_title,
                font_path=heading_font_path,
                font_size=current_heading_size,
                max_width=text_column_width,
                line_spacing=heading_line_spacing,
                padding=2,
            )

            body_layout = layout_text(
                event_description,
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=text_column_width,
                line_spacing=body_line_spacing,
                padding=2,
            )

            year_layout = layout_text(
                event_year,
                font_path=year_font_path,
                font_size=current_year_size,
                max_width=year_column_width,
                line_spacing=year_line_spacing,
                padding=2,
            )

            text_block_height = (
                heading_layout["height"]
                + heading_to_body_gap
                + body_layout["height"]
            )

            line_height = max(
                84.0,
                body_layout["height"] + 26.0,
            )

            item_layouts.append(
                {
                    "heading": heading_layout,
                    "body": body_layout,
                    "year": year_layout,
                    "text_block_height": text_block_height,
                    "line_height": line_height,
                    "height": max(
                        text_block_height,
                        year_layout["height"] + line_height,
                    ),
                }
            )

        total_height = (
            title_layout["height"]
            + title_to_items_gap
            + sum(item["height"] for item in item_layouts)
            + item_gap * max(0, len(item_layouts) - 1)
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
        year_font_size,
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

        elif year_font_size > year_min_font_size:
            year_font_size = max(
                year_min_font_size,
                year_font_size - 0.5,
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
            year_font_size,
        )

    if layouts["total_height"] > available_height:
        raise ValueError(
            "The content is too long to fit without overlap. "
            f"Required height: {layouts['total_height']:.1f}px; "
            f"available height: {available_height:.1f}px."
        )

    remaining_space = available_height - layouts["total_height"]

    if remaining_space > 0:
        if len(layouts["items"]) > 1:
            extra_gap = min(
                34.0,
                remaining_space / max(1, len(layouts["items"]) - 1),
            )
            item_gap += extra_gap
            layouts = calculate_layouts(
                title_font_size,
                heading_font_size,
                body_font_size,
                year_font_size,
            )
        else:
            title_to_items_gap += min(remaining_space, 50.0)
            layouts = calculate_layouts(
                title_font_size,
                heading_font_size,
                body_font_size,
                year_font_size,
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
        x=title_block_x,
        y=cursor_y,
        width=title_block_width,
        height=layouts["title"]["height"],
        font=title_font_name,
        size=layouts["title"]["font_size"],
        min_font_size=layouts["title"]["font_size"],
        bold="true",
        color=title_color,
        align="center",
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

    for index, item in enumerate(layouts["items"]):
        item_top = cursor_y

        textbox(
            item["heading"]["text"],
            x=text_column_x,
            y=item_top,
            width=text_column_width,
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

        textbox(
            item["body"]["text"],
            x=text_column_x,
            y=item_top + item["heading"]["height"] + heading_to_body_gap,
            width=text_column_width,
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

        textbox(
            item["year"]["text"],
            x=year_column_x,
            y=item_top + 2,
            width=year_column_width,
            height=item["year"]["height"],
            font=year_font_name,
            size=item["year"]["font_size"],
            min_font_size=item["year"]["font_size"],
            bold="true",
            color=year_color,
            align="center",
            vertical_align="top",
            single_line="false",
            max_lines=len(item["year"]["lines"]),
            overflow="clip",
            line_spacing=year_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        add(
            "line",
            x1=line_x,
            y1=item_top + item["year"]["height"] + 18,
            x2=line_x,
            y2=item_top + item["year"]["height"] + 18 + item["line_height"],
            color=line_color,
            width=1.2,
        )

        cursor_y += item["height"]

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

def generate_instructions_slide_xml(
    title: str = "INSTRUCTIONS FOR USE",
    left_heading: str = "EDIT IN GOOGLE SLIDES",
    left_paragraphs: list[str] = [
        (
            'Click on the button under the presentation preview that says '
            '“Use as Google Slides Theme”.'
        ),
        (
            "You will get a copy of this document on your Google Drive and will be able to edit, add or delete slides."
        ),
        (
            "You have to be signed in to your Google account."
        ),
    ],
    right_heading: str = "EDIT IN POWERPOINT®",
    right_paragraphs: list[str] = [
        (
            'Click on the button under the presentation preview that says '
            '“Download as PowerPoint template”. You will get a .pptx file '
            'that you can edit in PowerPoint.'
        ),
        (
            "Remember to download and install the fonts used in this "
            "presentation."
        ),
    ],
    footer_text: str = (
        "More info on how to use this template at "
        "slidescarnival.com/help-use-presentation-template\n"
        "This template is free to use under Creative Commons Attribution "
        "license. You can keep the Credits slide or mention SlidesCarnival "
        "and other resources used in a slide footer."
    ),
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1497032628192-86f99bcd76bc"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#F3F4F7",
    dark_panel_color: str = "#34343B",
    accent_color: str = "#98F20F",
    title_color: str = "#98F20F",
    heading_color: str = "#FFFFFF",
    body_color: str = "#FFFFFF",
    footer_color: str = "#39C62F",
) -> str:
    """
    Generate XML for an instructional split-layout slide.

    The layout features a dark diagonal content panel on the left,
    a bright workspace image on the right, a large title at the top,
    two text columns in the center, a green information block near
    the bottom, and a slanted accent bar aligned with the diagonal edge.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    if not left_heading.strip() or not right_heading.strip():
        raise ValueError("column headings must not be empty")

    if not left_paragraphs or not right_paragraphs:
        raise ValueError("both content columns must contain text")

    # =====================================================
    # Canvas and panel geometry
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    image_x = 760
    image_y = 0
    image_width = 840
    image_height = 900

    panel_top_x = 1115.0
    panel_bottom_x = 760.0
    panel_top_y = 0.0
    panel_bottom_y = 900.0

    dark_panel_points = (
        f"0,0 "
        f"{panel_top_x:.2f},0 "
        f"{panel_bottom_x:.2f},900 "
        f"0,900"
    )

    accent_top_y = 305.0
    accent_bottom_y = 610.0
    accent_width = 54.0
    accent_overlap = 5.0

    def diagonal_x_at_y(y: float) -> float:
        ratio = (
            (y - panel_top_y)
            / (panel_bottom_y - panel_top_y)
        )

        return (
            panel_top_x
            + ratio
            * (panel_bottom_x - panel_top_x)
        )

    accent_top_inner_x = (
        diagonal_x_at_y(accent_top_y)
        - accent_overlap
    )

    accent_bottom_inner_x = (
        diagonal_x_at_y(accent_bottom_y)
        - accent_overlap
    )

    accent_points = (
        f"{accent_top_inner_x:.2f},{accent_top_y:.2f} "
        f"{accent_top_inner_x + accent_width:.2f},{accent_top_y:.2f} "
        f"{accent_bottom_inner_x + accent_width:.2f},{accent_bottom_y:.2f} "
        f"{accent_bottom_inner_x:.2f},{accent_bottom_y:.2f}"
    )

    content_left = 74.0
    content_right_padding = 72.0
    content_top = 145.0
    content_bottom = 825.0

    title_y = 145.0
    title_width = 720.0

    columns_top = 255.0
    column_gap = 42.0
    column_width = 365.0
    left_column_x = 74.0
    right_column_x = (
        left_column_x
        + column_width
        + column_gap
    )

    footer_x = 74.0
    footer_y = 675.0
    footer_width = 680.0
    footer_max_height = 150.0

    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
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
            directory
            for directory in directories
            if directory.exists()
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
                word_width = measure_text_width(
                    word,
                    font_path,
                    font_size_pt,
                )

                if word_width > max_width:
                    raise ValueError(
                        f"The word '{word}' is wider than the available area"
                    )

                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 4.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines) * line_height
                + padding
            ),
        }

    def join_paragraphs(paragraphs: list[str]) -> str:
        return "\n".join(
            paragraph.strip()
            for paragraph in paragraphs
            if paragraph.strip()
        )

    # =====================================================
    # Typography and responsive fitting
    # =====================================================

    title_font_name = "Arial"
    heading_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=False,
    )
    heading_font_path = resolve_font_path(
        heading_font_name,
        bold=True,
    )
    body_font_path = resolve_font_path(
        body_font_name,
        bold=False,
    )

    title_font_size = 50.0
    title_min_font_size = 34.0

    heading_font_size = 21.0
    heading_min_font_size = 16.0

    body_font_size = 19.0
    body_min_font_size = 14.0

    footer_font_size = 17.0
    footer_min_font_size = 13.0

    title_line_spacing = 0.96
    heading_line_spacing = 1.0
    body_line_spacing = 1.12
    footer_line_spacing = 1.08

    heading_to_body_gap = 10.0
    paragraph_gap = 11.0
    minimum_heading_to_body_gap = 5.0
    minimum_paragraph_gap = 5.0

    left_text = join_paragraphs(left_paragraphs)
    right_text = join_paragraphs(right_paragraphs)

    def calculate_column_layout(
        heading: str,
        paragraphs: list[str],
        current_heading_size: float,
        current_body_size: float,
        current_heading_gap: float,
        current_paragraph_gap: float,
    ) -> dict:
        heading_layout = layout_text(
            heading,
            font_path=heading_font_path,
            font_size=current_heading_size,
            max_width=column_width,
            line_spacing=heading_line_spacing,
            padding=2,
        )

        paragraph_layouts: list[dict] = []

        for paragraph in paragraphs:
            paragraph_layouts.append(
                layout_text(
                    paragraph,
                    font_path=body_font_path,
                    font_size=current_body_size,
                    max_width=column_width,
                    line_spacing=body_line_spacing,
                    padding=2,
                )
            )

        total_height = (
            heading_layout["height"]
            + current_heading_gap
            + sum(
                paragraph["height"]
                for paragraph in paragraph_layouts
            )
            + current_paragraph_gap
            * max(
                0,
                len(paragraph_layouts) - 1,
            )
        )

        return {
            "heading": heading_layout,
            "paragraphs": paragraph_layouts,
            "total_height": total_height,
        }

    title_layout = layout_text(
        title,
        font_path=title_font_path,
        font_size=title_font_size,
        max_width=title_width,
        line_spacing=title_line_spacing,
        padding=4,
    )

    for _ in range(100):
        if title_layout["height"] <= 78:
            break

        if title_font_size <= title_min_font_size:
            break

        title_font_size = max(
            title_min_font_size,
            title_font_size - 0.5,
        )

        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=title_font_size,
            max_width=title_width,
            line_spacing=title_line_spacing,
            padding=4,
        )

    left_layout = calculate_column_layout(
        left_heading,
        left_paragraphs,
        heading_font_size,
        body_font_size,
        heading_to_body_gap,
        paragraph_gap,
    )

    right_layout = calculate_column_layout(
        right_heading,
        right_paragraphs,
        heading_font_size,
        body_font_size,
        heading_to_body_gap,
        paragraph_gap,
    )

    available_column_height = footer_y - columns_top - 28.0

    for _ in range(180):
        tallest_column = max(
            left_layout["total_height"],
            right_layout["total_height"],
        )

        if tallest_column <= available_column_height:
            break

        changed = False

        if (
            heading_to_body_gap
            > minimum_heading_to_body_gap
            or paragraph_gap
            > minimum_paragraph_gap
        ):
            heading_to_body_gap = max(
                minimum_heading_to_body_gap,
                heading_to_body_gap - 1,
            )
            paragraph_gap = max(
                minimum_paragraph_gap,
                paragraph_gap - 1,
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

        if not changed:
            break

        left_layout = calculate_column_layout(
            left_heading,
            left_paragraphs,
            heading_font_size,
            body_font_size,
            heading_to_body_gap,
            paragraph_gap,
        )

        right_layout = calculate_column_layout(
            right_heading,
            right_paragraphs,
            heading_font_size,
            body_font_size,
            heading_to_body_gap,
            paragraph_gap,
        )

    if max(
        left_layout["total_height"],
        right_layout["total_height"],
    ) > available_column_height:
        raise ValueError(
            "The column content is too long to fit without overlap"
        )

    footer_layout = layout_text(
        footer_text,
        font_path=body_font_path,
        font_size=footer_font_size,
        max_width=footer_width,
        line_spacing=footer_line_spacing,
        padding=4,
    )

    for _ in range(80):
        if footer_layout["height"] <= footer_max_height:
            break

        if footer_font_size <= footer_min_font_size:
            break

        footer_font_size = max(
            footer_min_font_size,
            footer_font_size - 0.5,
        )

        footer_layout = layout_text(
            footer_text,
            font_path=body_font_path,
            font_size=footer_font_size,
            max_width=footer_width,
            line_spacing=footer_line_spacing,
            padding=4,
        )

    if footer_layout["height"] > footer_max_height:
        raise ValueError(
            "The footer text is too long to fit without overlap"
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

    add(
        "polygon",
        points=dark_panel_points,
        fill=dark_panel_color,
        line_color="none",
    )

    add(
        "polygon",
        points=accent_points,
        fill=accent_color,
        line_color="none",
    )

    textbox(
        title_layout["source_text"],
        x=content_left,
        y=title_y,
        width=title_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=title_layout["font_size"],
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    def render_column(
        x: float,
        layout: dict,
    ) -> None:
        cursor_y = columns_top

        textbox(
            layout["heading"]["source_text"],
            x=x,
            y=cursor_y,
            width=column_width,
            height=layout["heading"]["height"],
            font=heading_font_name,
            font_path=str(heading_font_path),
            size=layout["heading"]["font_size"],
            min_font_size=layout["heading"]["font_size"],
            bold="true",
            color=heading_color,
            align="left",
            vertical_align="top",
            single_line="false",
            max_lines=len(layout["heading"]["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=heading_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        cursor_y += (
            layout["heading"]["height"]
            + heading_to_body_gap
        )

        for index, paragraph in enumerate(
            layout["paragraphs"]
        ):
            textbox(
                paragraph["source_text"],
                x=x,
                y=cursor_y,
                width=column_width,
                height=paragraph["height"],
                font=body_font_name,
                font_path=str(body_font_path),
                size=paragraph["font_size"],
                min_font_size=paragraph["font_size"],
                color=body_color,
                align="left",
                vertical_align="top",
                single_line="false",
                max_lines=len(paragraph["lines"]),
                overflow="clip",
                reflow_on_resize="true",
                line_spacing=body_line_spacing,
                safety_ratio=1.0,
                margin_left=0,
                margin_right=0,
                margin_top=0,
                margin_bottom=0,
            )

            cursor_y += paragraph["height"]

            if index < len(layout["paragraphs"]) - 1:
                cursor_y += paragraph_gap

    render_column(
        left_column_x,
        left_layout,
    )

    render_column(
        right_column_x,
        right_layout,
    )

    textbox(
        footer_layout["source_text"],
        x=footer_x,
        y=footer_y,
        width=footer_width,
        height=footer_layout["height"],
        font=body_font_name,
        font_path=str(body_font_path),
        size=footer_layout["font_size"],
        min_font_size=footer_layout["font_size"],
        color=footer_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(footer_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=footer_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
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

def generate_split_content_slide_xml(
    title: str = "YOU CAN ALSO SPLIT YOUR CONTENT  YOUR CONTENT  YOUR CONTENT",
    column_titles: list[str] = [
        "White",
        "Black",
    ],
    column_descriptions: list[str] = [
        (
            "Is the color of milk and fresh snow, the color "
            "produced by the combination of all the colors "
            "of the visible spectrum."
        ),
        (
            "Is the color of ebony and of outer space. It has "
            "been the symbolic color of elegance, solemnity "
            "and authority."
        ),
    ],
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1497366754035-f200968a6e72"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#F3F4F7",
    dark_panel_color: str = "#34343B",
    accent_color: str = "#98F20F",
    title_color: str = "#98F20F",
    heading_color: str = "#FFFFFF",
    body_color: str = "#FFFFFF",
) -> str:
    """
    Generate XML for a split-content slide.

    The layout features a full-slide workspace image, a dark diagonal
    panel covering the left side, a large title at the top, two text
    columns below it, and a bright slanted accent bar aligned with
    the diagonal edge.
    """


    # =====================================================
    # Canvas and panel geometry
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    image_x = 0
    image_y = 0
    image_width = 1600
    image_height = 900

    panel_top_x = 1115.0
    panel_bottom_x = 760.0
    panel_top_y = 0.0
    panel_bottom_y = 900.0

    dark_panel_points = (
        f"0,0 "
        f"{panel_top_x:.2f},0 "
        f"{panel_bottom_x:.2f},900 "
        f"0,900"
    )

    accent_top_y = 285.0
    accent_bottom_y = 595.0
    accent_width = 54.0

    def diagonal_x_at_y(y: float) -> float:
        ratio = (
            (y - panel_top_y)
            / (panel_bottom_y - panel_top_y)
        )

        return (
            panel_top_x
            + ratio
            * (panel_bottom_x - panel_top_x)
        )

    accent_top_x = (
        diagonal_x_at_y(accent_top_y)
        - accent_width / 2
    )

    accent_bottom_x = (
        diagonal_x_at_y(accent_bottom_y)
        - accent_width / 2
    )

    accent_points = (
        f"{accent_top_x:.2f},{accent_top_y:.2f} "
        f"{accent_top_x + accent_width:.2f},{accent_top_y:.2f} "
        f"{accent_bottom_x + accent_width:.2f},{accent_bottom_y:.2f} "
        f"{accent_bottom_x:.2f},{accent_bottom_y:.2f}"
    )

    content_left = 64.0
    content_top = 70.0

    title_y = 70.0
    title_right_padding = 80.0

    minimum_columns_top = 250.0
    columns_bottom = canvas_height - 60.0
    column_gap = 72.0
    column_width = 350.0
    left_column_x = 64.0
    title_to_columns_gap = 18.0

    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
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
            directory
            for directory in directories
            if directory.exists()
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
                word_width = measure_text_width(
                    word,
                    font_path,
                    font_size_pt,
                )

                if word_width > max_width:
                    raise ValueError(
                        f"The word '{word}' is wider than the available area"
                    )

                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 4.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines) * line_height
                + padding
            ),
        }

    # =====================================================
    # Typography and responsive fitting
    # =====================================================

    title_font_name = "Arial"
    heading_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=False,
    )
    heading_font_path = resolve_font_path(
        heading_font_name,
        bold=True,
    )
    body_font_path = resolve_font_path(
        body_font_name,
        bold=False,
    )

    title_font_size = 50.0
    title_min_font_size = 34.0

    heading_font_size = 25.0
    heading_min_font_size = 18.0

    body_font_size = 26.0
    body_min_font_size = 17.0

    title_line_spacing = 0.96
    heading_line_spacing = 1.0
    body_line_spacing = 1.08

    heading_to_body_gap = 16.0
    minimum_heading_to_body_gap = 8.0

    def title_width_for_height(text_height: float) -> float:
        title_bottom_y = min(
            canvas_height,
            title_y + text_height,
        )

        return max(
            1.0,
            diagonal_x_at_y(title_bottom_y)
            - content_left
            - title_right_padding,
        )

    def layout_title_at_size(font_size: float) -> dict:
        title_width = title_width_for_height(
            0
        )

        for _ in range(8):
            layout = layout_text(
                title,
                font_path=title_font_path,
                font_size=font_size,
                max_width=title_width,
                line_spacing=title_line_spacing,
                padding=6,
            )

            next_title_width = title_width_for_height(
                layout["height"]
            )

            if abs(
                next_title_width - title_width
            ) < 0.5:
                layout["width"] = title_width
                return layout

            title_width = next_title_width

        layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=font_size,
            max_width=title_width,
            line_spacing=title_line_spacing,
            padding=6,
        )
        layout["width"] = title_width

        return layout

    title_layout = layout_title_at_size(
        title_font_size
    )

    for _ in range(100):
        pushed_columns_top = (
            title_y
            + title_layout["height"]
            + title_to_columns_gap
        )

        if (
            pushed_columns_top <= minimum_columns_top
            or title_font_size <= title_min_font_size
        ):
            break

        title_font_size = max(
            title_min_font_size,
            title_font_size - 0.5,
        )

        title_layout = layout_title_at_size(
            title_font_size
        )

    columns_top = max(
        minimum_columns_top,
        title_y
        + title_layout["height"]
        + title_to_columns_gap,
    )

    available_column_height = max(
        1.0,
        columns_bottom - columns_top,
    )

    def calculate_columns(
        current_heading_size: float,
        current_body_size: float,
        current_gap: float,
    ) -> list[dict]:
        layouts: list[dict] = []

        for column_title, column_description in zip(
            column_titles,
            column_descriptions,
        ):
            heading_layout = layout_text(
                column_title,
                font_path=heading_font_path,
                font_size=current_heading_size,
                max_width=column_width,
                line_spacing=heading_line_spacing,
                padding=2,
            )

            body_layout = layout_text(
                column_description,
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=column_width,
                line_spacing=body_line_spacing,
                padding=2,
            )

            layouts.append(
                {
                    "heading": heading_layout,
                    "body": body_layout,
                    "height": (
                        heading_layout["height"]
                        + current_gap
                        + body_layout["height"]
                    ),
                }
            )

        return layouts

    column_layouts = calculate_columns(
        heading_font_size,
        body_font_size,
        heading_to_body_gap,
    )

    for _ in range(180):
        tallest_column = max(
            layout["height"]
            for layout in column_layouts
        )

        if tallest_column <= available_column_height:
            break

        changed = False

        if (
            heading_to_body_gap
            > minimum_heading_to_body_gap
        ):
            heading_to_body_gap = max(
                minimum_heading_to_body_gap,
                heading_to_body_gap - 1,
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

        if not changed:
            break

        column_layouts = calculate_columns(
            heading_font_size,
            body_font_size,
            heading_to_body_gap,
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

    add(
        "polygon",
        points=dark_panel_points,
        fill=dark_panel_color,
        line_color="none",
    )

    add(
        "polygon",
        points=accent_points,
        fill=accent_color,
        line_color="none",
    )

    textbox(
        title_layout["source_text"],
        x=content_left,
        y=title_y,
        width=title_layout["width"],
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=title_layout["font_size"],
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    for index, layout in enumerate(
        column_layouts
    ):
        column_x = (
            left_column_x
            + index
            * (
                column_width
                + column_gap
            )
        )

        cursor_y = columns_top

        textbox(
            layout["heading"]["source_text"],
            x=column_x,
            y=cursor_y,
            width=column_width,
            height=layout["heading"]["height"],
            font=heading_font_name,
            font_path=str(heading_font_path),
            size=layout["heading"]["font_size"],
            min_font_size=layout["heading"]["font_size"],
            bold="true",
            color=heading_color,
            align="left",
            vertical_align="top",
            single_line="false",
            max_lines=len(layout["heading"]["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=heading_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        cursor_y += (
            layout["heading"]["height"]
            + heading_to_body_gap
        )

        textbox(
            layout["body"]["source_text"],
            x=column_x,
            y=cursor_y,
            width=column_width,
            height=layout["body"]["height"],
            font=body_font_name,
            font_path=str(body_font_path),
            size=layout["body"]["font_size"],
            min_font_size=layout["body"]["font_size"],
            color=body_color,
            align="left",
            vertical_align="top",
            single_line="false",
            max_lines=len(layout["body"]["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=body_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
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

def generate_picture_quote_slide_xml(
    title: str = "A PICTURE IS WORTH THOUSAND WORDS",
    content: str = (
        "A complex idea can be conveyed with just a single still image, "
        "namely making it possible to absorb large amounts of data quickly."
    ),
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1521737711867-e3b97375f902"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#FFFFFF",
    accent_color: str = "#98F20F",
    title_color: str = "#7CCF1A",
    body_color: str = "#858392",
) -> str:
    """
    Generate XML for a split image-and-text slide.

    The layout features a large image on the left, a white content
    panel on the right, a slanted accent bar centered on the diagonal
    boundary, and a title with supporting text arranged vertically.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    if not content.strip():
        raise ValueError("content must not be empty")

    # =====================================================
    # Canvas and panel geometry
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    image_x = 0
    image_y = 0
    image_width = 1010
    image_height = 900

    panel_top_x = 965.0
    panel_bottom_x = 610.0
    panel_top_y = 0.0
    panel_bottom_y = 900.0

    white_panel_points = (
        f"{panel_top_x:.2f},0 "
        f"1600,0 "
        f"1600,900 "
        f"{panel_bottom_x:.2f},900"
    )

    accent_top_y = 310.0
    accent_bottom_y = 610.0
    accent_width = 54.0

    def diagonal_x_at_y(y: float) -> float:
        ratio = (
            (y - panel_top_y)
            / (panel_bottom_y - panel_top_y)
        )

        return (
            panel_top_x
            + ratio
            * (panel_bottom_x - panel_top_x)
        )

    accent_top_center_x = diagonal_x_at_y(
        accent_top_y
    )
    accent_bottom_center_x = diagonal_x_at_y(
        accent_bottom_y
    )
    accent_half_width = accent_width / 2.0

    accent_points = (
        f"{accent_top_center_x - accent_half_width:.2f},"
        f"{accent_top_y:.2f} "
        f"{accent_top_center_x + accent_half_width:.2f},"
        f"{accent_top_y:.2f} "
        f"{accent_bottom_center_x + accent_half_width:.2f},"
        f"{accent_bottom_y:.2f} "
        f"{accent_bottom_center_x - accent_half_width:.2f},"
        f"{accent_bottom_y:.2f}"
    )

    content_x = 980.0
    content_right = 1510.0
    content_width = content_right - content_x

    content_top = 260.0
    content_bottom = 720.0
    available_height = content_bottom - content_top

    title_to_body_gap = 34.0
    minimum_gap = 18.0

    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
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
            directory
            for directory in directories
            if directory.exists()
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
                word_width = measure_text_width(
                    word,
                    font_path,
                    font_size_pt,
                )

                if word_width > max_width:
                    raise ValueError(
                        f"The word '{word}' is wider than the available area"
                    )

                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 4.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines) * line_height
                + padding
            ),
        }

    # =====================================================
    # Typography and responsive fitting
    # =====================================================

    title_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=False,
    )
    body_font_path = resolve_font_path(
        body_font_name,
        bold=False,
    )

    title_font_size = 42.0
    title_min_font_size = 28.0

    body_font_size = 31.0
    body_min_font_size = 18.0

    title_line_spacing = 0.98
    body_line_spacing = 1.12

    def calculate_layouts(
        current_title_size: float,
        current_body_size: float,
        current_gap: float,
    ) -> dict:
        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=current_title_size,
            max_width=content_width,
            line_spacing=title_line_spacing,
            padding=4,
        )

        body_layout = layout_text(
            content,
            font_path=body_font_path,
            font_size=current_body_size,
            max_width=content_width,
            line_spacing=body_line_spacing,
            padding=4,
        )

        total_height = (
            title_layout["height"]
            + current_gap
            + body_layout["height"]
        )

        return {
            "title": title_layout,
            "body": body_layout,
            "total_height": total_height,
        }

    layouts = calculate_layouts(
        title_font_size,
        body_font_size,
        title_to_body_gap,
    )

    for _ in range(180):
        if layouts["total_height"] <= available_height:
            break

        changed = False

        if title_to_body_gap > minimum_gap:
            title_to_body_gap = max(
                minimum_gap,
                title_to_body_gap - 1,
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

        layouts = calculate_layouts(
            title_font_size,
            body_font_size,
            title_to_body_gap,
        )

    if layouts["total_height"] > available_height:
        raise ValueError(
            "The content is too long to fit without overlap"
        )

    remaining_space = (
        available_height
        - layouts["total_height"]
    )

    content_group_y = (
        content_top
        + remaining_space / 2
    )

    title_y = content_group_y
    body_y = (
        title_y
        + layouts["title"]["height"]
        + title_to_body_gap
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

    add(
        "polygon",
        points=white_panel_points,
        fill=background_color,
        line_color="none",
    )

    add(
        "polygon",
        points=accent_points,
        fill=accent_color,
        line_color="none",
    )

    textbox(
        layouts["title"]["source_text"],
        x=content_x,
        y=title_y,
        width=content_width,
        height=layouts["title"]["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=layouts["title"]["font_size"],
        min_font_size=layouts["title"]["font_size"],
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["title"]["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        layouts["body"]["source_text"],
        x=content_x,
        y=body_y,
        width=content_width,
        height=layouts["body"]["height"],
        font=body_font_name,
        font_path=str(body_font_path),
        size=layouts["body"]["font_size"],
        min_font_size=layouts["body"]["font_size"],
        color=body_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["body"]["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=body_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
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

def generate_bullet_content_slide_xml(
    title: str = "THIS IS A SLIDE TITLE THIS IS A SLIDE TITLE",
    bullet_items: list[str] = [
        "Here you have a list of items",
        "And some text And some text  some text And some text",
        (
            "But remember not to overload your slides with content"
        ),
    ],
    closing_text: str = (
        "Your audience will listen to you or read "
        "the content, but won’t do both."
    ),
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1499750310107-5fef28a66643"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#FFFFFF",
    dark_panel_color: str = "#2D2E34",
    accent_color: str = "#98F20F",
    title_color: str = "#98F20F",
    bullet_color: str = "#98F20F",
    body_color: str = "#FFFFFF",
) -> str:
    """
    Generate XML for a diagonal split-content slide.

    The layout features a full-slide image, a dark diagonal panel
    on the left, a bright accent bar centered on the diagonal edge,
    a title at the top, a vertically stacked bullet list, and a
    supporting text block below the list.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    if not bullet_items:
        raise ValueError(
            "bullet_items must contain at least one item"
        )

    if not closing_text.strip():
        raise ValueError("closing_text must not be empty")

    # =====================================================
    # Canvas and panel geometry
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    image_x = 0
    image_y = 0
    image_width = 1600
    image_height = 900

    panel_top_x = 1055.0
    panel_bottom_x = 705.0
    panel_top_y = 0.0
    panel_bottom_y = 900.0

    dark_panel_points = (
        f"0,0 "
        f"{panel_top_x:.2f},0 "
        f"{panel_bottom_x:.2f},900 "
        f"0,900"
    )

    accent_top_y = 270.0
    accent_bottom_y = 550.0
    accent_width = 58.0

    def diagonal_x_at_y(y: float) -> float:
        ratio = (
            (y - panel_top_y)
            / (panel_bottom_y - panel_top_y)
        )

        return (
            panel_top_x
            + ratio
            * (panel_bottom_x - panel_top_x)
        )

    accent_top_center_x = diagonal_x_at_y(
        accent_top_y
    )
    accent_bottom_center_x = diagonal_x_at_y(
        accent_bottom_y
    )
    accent_half_width = accent_width / 2.0

    accent_points = (
        f"{accent_top_center_x - accent_half_width:.2f},"
        f"{accent_top_y:.2f} "
        f"{accent_top_center_x + accent_half_width:.2f},"
        f"{accent_top_y:.2f} "
        f"{accent_bottom_center_x + accent_half_width:.2f},"
        f"{accent_bottom_y:.2f} "
        f"{accent_bottom_center_x - accent_half_width:.2f},"
        f"{accent_bottom_y:.2f}"
    )

    text_left = 62.0
    bullet_text_left = 132.0
    text_right_padding = 58.0

    content_top = 118.0
    content_bottom = 760.0

    title_to_bullets_gap = 42.0
    bullet_gap = 12.0
    bullets_to_closing_gap = 28.0

    minimum_title_gap = 22.0
    minimum_bullet_gap = 6.0
    minimum_closing_gap = 16.0

    bullet_marker_width = 44.0

    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
        )

    def font_directories() -> list[Path]:
        directories: list[Path] = []

        windir = os.environ.get("WINDIR")
        if windir:
            directories.append(
                Path(windir) / "Fonts"
            )

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
            directory
            for directory in directories
            if directory.exists()
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

                candidates.append(
                    (score, path)
                )

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
        font_path = getattr(
            font,
            "path",
            None,
        )

        if not font_path:
            raise ValueError(
                f"Font '{font_name}' was not found"
            )

        return Path(font_path)

    canvas_dpi = 120.0

    def pt_to_canvas(
        point_size: float,
    ) -> float:
        return (
            point_size
            * canvas_dpi
            / 72.0
        )

    def load_font(
        font_path: Path,
        font_size_pt: float,
    ) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(
                1,
                round(
                    pt_to_canvas(font_size_pt)
                ),
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
            return float(
                font.getlength(text)
            )

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
                word_width = measure_text_width(
                    word,
                    font_path,
                    font_size_pt,
                )

                if word_width > max_width:
                    raise ValueError(
                        f"The word '{word}' is wider "
                        "than the available area"
                    )

                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 3.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines)
                * line_height
                + padding
            ),
        }

    def longest_word_width(
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        words = text.split()

        if not words:
            return 0.0

        return max(
            measure_text_width(
                word,
                font_path,
                font_size_pt,
            )
            for word in words
        )

    # =====================================================
    # Typography and responsive fitting
    # =====================================================

    title_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=False,
    )
    body_font_path = resolve_font_path(
        body_font_name,
        bold=False,
    )

    title_font_size = 42.0
    title_min_font_size = 30.0

    body_font_size = 28.0
    body_min_font_size = 17.0

    title_line_spacing = 0.98
    body_line_spacing = 1.08

    def width_for_block(
        block_left: float,
        block_y: float,
        block_height: float,
    ) -> float:
        safe_right_edge = (
            diagonal_x_at_y(
                block_y + block_height
            )
            - accent_half_width
            - text_right_padding
        )

        return max(
            1.0,
            safe_right_edge - block_left,
        )

    def calculate_layouts(
        current_title_size: float,
        current_body_size: float,
        current_title_gap: float,
        current_bullet_gap: float,
        current_closing_gap: float,
    ) -> dict:
        cursor_y = content_top

        title_width = width_for_block(
            text_left,
            cursor_y,
            90.0,
        )

        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=current_title_size,
            max_width=title_width,
            line_spacing=title_line_spacing,
            padding=3,
        )

        title_width = width_for_block(
            text_left,
            cursor_y,
            title_layout["height"],
        )

        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=current_title_size,
            max_width=title_width,
            line_spacing=title_line_spacing,
            padding=3,
        )

        title_y = cursor_y

        cursor_y += (
            title_layout["height"]
            + current_title_gap
        )

        bullet_layouts: list[dict] = []

        for item in bullet_items:
            estimated_width = width_for_block(
                bullet_text_left,
                cursor_y,
                70.0,
            )

            item_layout = layout_text(
                item,
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=estimated_width,
                line_spacing=body_line_spacing,
                padding=3,
            )

            item_width = width_for_block(
                bullet_text_left,
                cursor_y,
                item_layout["height"],
            )

            item_layout = layout_text(
                item,
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=item_width,
                line_spacing=body_line_spacing,
                padding=3,
            )

            bullet_layouts.append(
                {
                    "layout": item_layout,
                    "x": bullet_text_left,
                    "y": cursor_y,
                    "width": item_width,
                    "height": item_layout["height"],
                }
            )

            cursor_y += item_layout["height"]

            if len(bullet_layouts) < len(bullet_items):
                cursor_y += current_bullet_gap

        cursor_y += current_closing_gap

        closing_width = width_for_block(
            text_left,
            cursor_y,
            100.0,
        )

        closing_layout = layout_text(
            closing_text,
            font_path=body_font_path,
            font_size=current_body_size,
            max_width=closing_width,
            line_spacing=body_line_spacing,
            padding=3,
        )

        closing_width = width_for_block(
            text_left,
            cursor_y,
            closing_layout["height"],
        )

        closing_layout = layout_text(
            closing_text,
            font_path=body_font_path,
            font_size=current_body_size,
            max_width=closing_width,
            line_spacing=body_line_spacing,
            padding=3,
        )

        closing_y = cursor_y
        total_bottom = (
            closing_y + closing_layout["height"]
        )

        width_fits = (
            longest_word_width(
                title,
                title_font_path,
                current_title_size,
            )
            <= title_width
            and longest_word_width(
                closing_text,
                body_font_path,
                current_body_size,
            )
            <= closing_width
            and all(
                longest_word_width(
                    item,
                    body_font_path,
                    current_body_size,
                )
                <= item_data["width"]
                for item, item_data in zip(
                    bullet_items,
                    bullet_layouts,
                )
            )
        )

        return {
            "title": title_layout,
            "title_x": text_left,
            "title_y": title_y,
            "title_width": title_width,
            "bullets": bullet_layouts,
            "closing": closing_layout,
            "closing_x": text_left,
            "closing_y": closing_y,
            "closing_width": closing_width,
            "total_bottom": total_bottom,
            "width_fits": width_fits,
        }

    layouts = calculate_layouts(
        title_font_size,
        body_font_size,
        title_to_bullets_gap,
        bullet_gap,
        bullets_to_closing_gap,
    )

    for _ in range(220):
        fits = (
            layouts["total_bottom"] <= content_bottom
            and layouts["width_fits"]
        )

        if fits:
            break

        changed = False

        if (
            title_to_bullets_gap
            > minimum_title_gap
            or bullet_gap
            > minimum_bullet_gap
            or bullets_to_closing_gap
            > minimum_closing_gap
        ):
            title_to_bullets_gap = max(
                minimum_title_gap,
                title_to_bullets_gap - 1,
            )
            bullet_gap = max(
                minimum_bullet_gap,
                bullet_gap - 1,
            )
            bullets_to_closing_gap = max(
                minimum_closing_gap,
                bullets_to_closing_gap - 1,
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

        layouts = calculate_layouts(
            title_font_size,
            body_font_size,
            title_to_bullets_gap,
            bullet_gap,
            bullets_to_closing_gap,
        )

    if (
        layouts["total_bottom"] > content_bottom
        or not layouts["width_fits"]
    ):
        raise ValueError(
            "The content is too long to fit without "
            "splitting words or overlapping other elements"
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

    def add(
        tag: str,
        **attrs,
    ):
        return ET.SubElement(
            slide,
            tag,
            {
                key: str(value)
                for key, value in attrs.items()
                if value is not None
            },
        )

    def textbox(
        text: str,
        **attrs,
    ):
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

    add(
        "polygon",
        points=dark_panel_points,
        fill=dark_panel_color,
        line_color="none",
    )

    add(
        "polygon",
        points=accent_points,
        fill=accent_color,
        line_color="none",
    )

    textbox(
        layouts["title"]["source_text"],
        x=layouts["title_x"],
        y=layouts["title_y"],
        width=layouts["title_width"],
        height=layouts["title"]["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=layouts["title"]["font_size"],
        min_font_size=layouts["title"]["font_size"],
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(
            layouts["title"]["lines"]
        ),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    for item_data in layouts["bullets"]:
        textbox(
            "–",
            x=text_left,
            y=item_data["y"],
            width=bullet_marker_width,
            height=item_data["height"],
            font=body_font_name,
            font_path=str(body_font_path),
            size=item_data["layout"]["font_size"],
            min_font_size=item_data["layout"]["font_size"],
            color=bullet_color,
            align="left",
            vertical_align="top",
            single_line="true",
            max_lines=1,
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=body_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        textbox(
            item_data["layout"]["source_text"],
            x=item_data["x"],
            y=item_data["y"],
            width=item_data["width"],
            height=item_data["height"],
            font=body_font_name,
            font_path=str(body_font_path),
            size=item_data["layout"]["font_size"],
            min_font_size=item_data["layout"]["font_size"],
            color=body_color,
            align="left",
            vertical_align="top",
            single_line="false",
            max_lines=len(
                item_data["layout"]["lines"]
            ),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=body_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    textbox(
        layouts["closing"]["source_text"],
        x=layouts["closing_x"],
        y=layouts["closing_y"],
        width=layouts["closing_width"],
        height=layouts["closing"]["height"],
        font=body_font_name,
        font_path=str(body_font_path),
        size=layouts["closing"]["font_size"],
        min_font_size=layouts["closing"]["font_size"],
        color=body_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(
            layouts["closing"]["lines"]
        ),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=body_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
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

def generate_client_snapshot_slide_xml(
    title: str = "Client snapshot, snapshot",
    subtitle: str = "About Value Financials",
    client_details: list[str] = [
        "Industry: Financial services and banking",
        "Team size: 300+ employees",
        (
        "Current setup: Disconnected productivity tools, "
        "shared drives, and manual handoffs"
        ),
        "Primary goals:",
        "  Improve cross-team collaboration",
        "  Standardize workflows across departments",
        (
            "  Support growth while meeting regulatory "
            "requirements"
        ),
    ],
    top_image_url: str = (
        "https://images.unsplash.com/"
        "photo-1552664730-d307ca884978"
        "?q=85&w=1200&auto=format&fit=crop"
    ),
    bottom_image_url: str = (
        "https://images.unsplash.com/"
        "photo-1556761175-b413da4baf72"
        "?q=85&w=1200&auto=format&fit=crop"
    ),
    background_color: str = "#1A0B3A",
    title_color: str = "#A678FF",
    subtitle_color: str = "#F7F2FF",
    body_color: str = "#F7F2FF",
) -> str:
    """
    Generate XML for a client snapshot slide.

    The layout features a dark purple background, a large title and
    short subtitle on the left, a structured bullet summary below,
    a footer link near the bottom-left, and two large stacked images
    on the right.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    if not subtitle.strip():
        raise ValueError("subtitle must not be empty")

    if not client_details:
        raise ValueError(
            "client_details must contain at least one item"
        )

    if any(not item.strip() for item in client_details):
        raise ValueError(
            "client_details must not contain empty items"
        )

    # =====================================================
    # Canvas and layout regions
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    title_x = 22.0
    title_y = 38.0
    title_width = 680.0

    subtitle_x = 22.0
    subtitle_width = 700.0

    content_x = 68.0
    marker_x = 45.0
    content_right = 795.0

    value_gap = 10.0
    subgoal_marker_x = 88.0
    subgoal_text_x = 122.0
    subgoal_width = content_right - subgoal_text_x

    content_bottom = 760.0

    title_to_subtitle_gap = 34.0
    subtitle_to_content_gap = 125.0
    bullet_gap = 13.0
    goal_gap = 8.0

    minimum_title_gap = 18.0
    minimum_subtitle_gap = 55.0
    minimum_bullet_gap = 7.0
    minimum_goal_gap = 4.0

    image_x = 845.0
    image_width = 715.0
    top_image_y = 32.0
    top_image_height = 410.0
    bottom_image_y = 474.0
    bottom_image_height = 410.0

    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
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
            directory
            for directory in directories
            if directory.exists()
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

        font = ImageFont.truetype(fallback, 12)
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

        return (
            float(ascent + descent)
            * line_spacing
        )

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
                word_width = measure_text_width(
                    word,
                    font_path,
                    font_size_pt,
                )

                if word_width > max_width:
                    raise ValueError(
                        f"The word '{word}' is wider than "
                        "the available text area"
                    )

                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 3.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines) * line_height
                + padding
            ),
        }

    def single_line_width(
        text: str,
        font_path: Path,
        font_size: float,
    ) -> float:
        return measure_text_width(
            text,
            font_path,
            font_size,
        )

    # =====================================================
    # Typography and responsive fitting
    # =====================================================

    title_font_name = "Arial"
    subtitle_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=True,
    )
    subtitle_font_path = resolve_font_path(
        subtitle_font_name,
        bold=True,
    )
    body_font_path = resolve_font_path(
        body_font_name,
        bold=False,
    )
    body_bold_font_path = resolve_font_path(
        body_font_name,
        bold=True,
    )

    title_font_size = 71.0
    title_min_font_size = 46.0

    subtitle_font_size = 31.0
    subtitle_min_font_size = 22.0

    body_font_size = 27.0
    body_min_font_size = 18.0

    title_line_spacing = 0.95
    subtitle_line_spacing = 1.0
    body_line_spacing = 1.18

    def calculate_layouts(
        current_title_size: float,
        current_subtitle_size: float,
        current_body_size: float,
        current_title_gap: float,
        current_subtitle_gap: float,
        current_bullet_gap: float,
        current_goal_gap: float,
    ) -> dict:
        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=current_title_size,
            max_width=title_width,
            line_spacing=title_line_spacing,
            padding=3,
        )

        subtitle_y = (
            title_y
            + title_layout["height"]
            + current_title_gap
        )

        subtitle_layout = layout_text(
            subtitle,
            font_path=subtitle_font_path,
            font_size=current_subtitle_size,
            max_width=subtitle_width,
            line_spacing=subtitle_line_spacing,
            padding=3,
        )

        cursor_y = (
            subtitle_y
            + subtitle_layout["height"]
            + current_subtitle_gap
        )

        bullet_layouts: list[dict] = []

        for detail in client_details:
            raw_detail = detail.rstrip()
            stripped_detail = raw_detail.lstrip()

            is_subitem = (
                len(raw_detail) != len(stripped_detail)
                or stripped_detail.startswith(
                    ("- ", "• ", "◦ ")
                )
            )

            if is_subitem:
                for prefix in ("- ", "• ", "◦ "):
                    if stripped_detail.startswith(prefix):
                        stripped_detail = stripped_detail[
                            len(prefix):
                        ].strip()
                        break

                sub_marker_layout = layout_text(
                    "◦",
                    font_path=body_font_path,
                    font_size=current_body_size,
                    max_width=30.0,
                    line_spacing=body_line_spacing,
                    padding=2,
                )

                subitem_layout = layout_text(
                    stripped_detail,
                    font_path=body_font_path,
                    font_size=current_body_size,
                    max_width=subgoal_width,
                    line_spacing=body_line_spacing,
                    padding=2,
                )

                subitem_height = max(
                    sub_marker_layout["height"],
                    subitem_layout["height"],
                )

                bullet_layouts.append(
                    {
                        "subgoal": True,
                        "marker": sub_marker_layout,
                        "value": subitem_layout,
                        "marker_x": subgoal_marker_x,
                        "value_x": subgoal_text_x,
                        "value_width": subgoal_width,
                        "y": cursor_y,
                        "height": subitem_height,
                    }
                )

                cursor_y += (
                    subitem_height
                    + current_goal_gap
                )
                continue

            raw_label, separator, raw_value = (
                stripped_detail.partition(":")
            )

            if separator:
                label = f"{raw_label.strip()}:"
                value = raw_value.strip()
            else:
                label = ""
                value = stripped_detail

            marker_layout = layout_text(
                "•",
                font_path=body_font_path,
                font_size=current_body_size,
                max_width=36.0,
                line_spacing=body_line_spacing,
                padding=2,
            )

            label_width = (
                single_line_width(
                    label,
                    body_bold_font_path,
                    current_body_size,
                )
                + 12.0
                if label
                else 0.0
            )

            label_layout = (
                layout_text(
                    label,
                    font_path=body_bold_font_path,
                    font_size=current_body_size,
                    max_width=max(label_width, 1.0),
                    line_spacing=body_line_spacing,
                    padding=2,
                )
                if label
                else {
                    "source_text": "",
                    "text": "",
                    "lines": [],
                    "font_size": current_body_size,
                    "height": 0.0,
                }
            )

            value_x = (
                content_x + label_width + value_gap
                if label
                else content_x
            )
            value_width = max(
                1.0,
                content_right - value_x,
            )

            value_layout = (
                layout_text(
                    value,
                    font_path=body_font_path,
                    font_size=current_body_size,
                    max_width=value_width,
                    line_spacing=body_line_spacing,
                    padding=2,
                )
                if value.strip()
                else {
                    "source_text": "",
                    "text": "",
                    "lines": [],
                    "font_size": current_body_size,
                    "height": 0.0,
                }
            )

            row_height = max(
                marker_layout["height"],
                label_layout["height"],
                value_layout["height"],
            )

            bullet_layouts.append(
                {
                    "marker": marker_layout,
                    "label": label_layout,
                    "value": value_layout,
                    "marker_x": marker_x,
                    "label_x": content_x,
                    "value_x": value_x,
                    "label_width": label_width,
                    "value_width": value_width,
                    "y": cursor_y,
                    "height": row_height,
                }
            )

            cursor_y += (
                row_height
                + current_bullet_gap
            )

        if bullet_layouts:
            last_item = bullet_layouts[-1]
            cursor_y -= (
                current_goal_gap
                if last_item.get("subgoal")
                else current_bullet_gap
            )

        return {
            "title": title_layout,
            "subtitle": subtitle_layout,
            "subtitle_y": subtitle_y,
            "bullets": bullet_layouts,
            "content_bottom": cursor_y,
        }

    layouts = calculate_layouts(
        title_font_size,
        subtitle_font_size,
        body_font_size,
        title_to_subtitle_gap,
        subtitle_to_content_gap,
        bullet_gap,
        goal_gap,
    )

    for _ in range(260):
        if layouts["content_bottom"] <= content_bottom:
            break

        changed = False

        if (
            subtitle_to_content_gap > minimum_subtitle_gap
            or title_to_subtitle_gap > minimum_title_gap
            or bullet_gap > minimum_bullet_gap
            or goal_gap > minimum_goal_gap
        ):
            subtitle_to_content_gap = max(
                minimum_subtitle_gap,
                subtitle_to_content_gap - 2,
            )
            title_to_subtitle_gap = max(
                minimum_title_gap,
                title_to_subtitle_gap - 1,
            )
            bullet_gap = max(
                minimum_bullet_gap,
                bullet_gap - 1,
            )
            goal_gap = max(
                minimum_goal_gap,
                goal_gap - 1,
            )
            changed = True

        elif body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif subtitle_font_size > subtitle_min_font_size:
            subtitle_font_size = max(
                subtitle_min_font_size,
                subtitle_font_size - 0.5,
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
            subtitle_font_size,
            body_font_size,
            title_to_subtitle_gap,
            subtitle_to_content_gap,
            bullet_gap,
            goal_gap,
        )

    if layouts["content_bottom"] > content_bottom:
        raise ValueError(
            "The client snapshot content is too long to fit "
            "without overlapping other elements"
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

    textbox(
        layouts["title"]["source_text"],
        x=title_x,
        y=title_y,
        width=title_width,
        height=layouts["title"]["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=layouts["title"]["font_size"],
        min_font_size=layouts["title"]["font_size"],
        bold="true",
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["title"]["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        layouts["subtitle"]["source_text"],
        x=subtitle_x,
        y=layouts["subtitle_y"],
        width=subtitle_width,
        height=layouts["subtitle"]["height"],
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=layouts["subtitle"]["font_size"],
        min_font_size=layouts["subtitle"]["font_size"],
        bold="true",
        color=subtitle_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(layouts["subtitle"]["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=subtitle_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    for item in layouts["bullets"]:
        if item.get("subgoal"):
            textbox(
                item["marker"]["source_text"],
                x=item["marker_x"],
                y=item["y"],
                width=26,
                height=item["height"],
                font=body_font_name,
                font_path=str(body_font_path),
                size=item["marker"]["font_size"],
                min_font_size=item["marker"]["font_size"],
                color=body_color,
                align="left",
                vertical_align="top",
                single_line="true",
                max_lines=1,
                overflow="clip",
                reflow_on_resize="true",
                line_spacing=body_line_spacing,
                safety_ratio=1.0,
                margin_left=0,
                margin_right=0,
                margin_top=0,
                margin_bottom=0,
            )

            textbox(
                item["value"]["source_text"],
                x=item["value_x"],
                y=item["y"],
                width=item["value_width"],
                height=item["value"]["height"],
                font=body_font_name,
                font_path=str(body_font_path),
                size=item["value"]["font_size"],
                min_font_size=item["value"]["font_size"],
                color=body_color,
                align="left",
                vertical_align="top",
                single_line="false",
                max_lines=len(item["value"]["lines"]),
                overflow="clip",
                reflow_on_resize="true",
                line_spacing=body_line_spacing,
                safety_ratio=1.0,
                margin_left=0,
                margin_right=0,
                margin_top=0,
                margin_bottom=0,
            )
            continue

        textbox(
            item["marker"]["source_text"],
            x=item["marker_x"],
            y=item["y"],
            width=30,
            height=item["height"],
            font=body_font_name,
            font_path=str(body_font_path),
            size=item["marker"]["font_size"],
            min_font_size=item["marker"]["font_size"],
            color=body_color,
            align="left",
            vertical_align="top",
            single_line="true",
            max_lines=1,
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=body_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        if item["label"]["source_text"].strip():
            textbox(
                item["label"]["source_text"],
                x=item["label_x"],
                y=item["y"],
                width=item["label_width"],
                height=item["label"]["height"],
                font=body_font_name,
                font_path=str(body_bold_font_path),
                size=item["label"]["font_size"],
                min_font_size=item["label"]["font_size"],
                bold="true",
                color=body_color,
                align="left",
                vertical_align="top",
                single_line="true",
                max_lines=1,
                overflow="shrink",
                reflow_on_resize="true",
                line_spacing=body_line_spacing,
                safety_ratio=1.0,
                margin_left=0,
                margin_right=0,
                margin_top=0,
                margin_bottom=0,
            )

        if item["value"]["source_text"].strip():
            textbox(
                item["value"]["source_text"],
                x=item["value_x"],
                y=item["y"],
                width=item["value_width"],
                height=item["value"]["height"],
                font=body_font_name,
                font_path=str(body_font_path),
                size=item["value"]["font_size"],
                min_font_size=item["value"]["font_size"],
                color=body_color,
                align="left",
                vertical_align="top",
                single_line="false",
                max_lines=len(item["value"]["lines"]),
                overflow="clip",
                reflow_on_resize="true",
                line_spacing=body_line_spacing,
                safety_ratio=1.0,
                margin_left=0,
                margin_right=0,
                margin_top=0,
                margin_bottom=0,
            )

    add(
        "image",
        src=top_image_url,
        x=image_x,
        y=top_image_y,
        width=image_width,
        height=top_image_height,
    )

    add(
        "image",
        src=bottom_image_url,
        x=image_x,
        y=bottom_image_y,
        width=image_width,
        height=bottom_image_height,
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

def generate_how_forge_works_slide_xml(
    title: str = "How Forge works How Forge works",
    subtitle: str = (
        "From setup to daily use, Forge fits into how your team operates."
    ),
    steps: list[dict[str, str]] = [
        {
            "step": "Step 1",
            "content": (
                "Connect teams, files, and existing systems"
            ),
        },
        {
            "step": "Step 2",
            "content": (
                "Configure shared workspaces and approval workflows"
            ),
        },
        {
            "step": "Step 3",
            "content": (
                "Roll out to teams with guided onboarding"
            ),
        },
        {
            "step": "Step 4",
            "content": (
                "Monitor usage, productivity, and adoption in real time"
            ),
        },
        {
            "step": "Step 5",
            "content": (
                "Monitor usage, productivity, and adoption in real time"
            ),
        },
    ],
    background_color: str = "#1A0B3A",
    title_color: str = "#A678FF",
    subtitle_color: str = "#F7F2FF",
    step_label_color: str = "#FFFFFF",
    step_body_color: str = "#F7F2FF",
    arrow_color: str = "#FFFFFF",
) -> str:
    """
    Generate XML for a process overview slide.

    The layout features a dark purple background, abstract circular
    decoration on the left, a title and subtitle block on the left,
    and a vertical sequence of step cards connected by arrows on
    the right.
    """

    if not steps:
        raise ValueError(
            "steps must contain at least one item"
        )

    if any(
        not isinstance(step, dict)
        or not step.get("step", "").strip()
        or not step.get("content", "").strip()
        for step in steps
    ):
        raise ValueError(
            "Each step must be a dictionary with non-empty step and content"
        )

    # =====================================================
    # Canvas and layout regions
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    safe_margin_x = 64.0
    safe_margin_top = 56.0
    safe_margin_bottom = 56.0

    cards_x = 650.0
    cards_right = canvas_width - safe_margin_x
    cards_width = cards_right - cards_x
    cards_top = safe_margin_top
    cards_bottom = canvas_height - safe_margin_bottom
    cards_area_height = cards_bottom - cards_top

    left_column_right = cards_x - 60.0
    left_column_width = left_column_right - safe_margin_x
    left_column_center_x = safe_margin_x + left_column_width / 2

    title_x = safe_margin_x
    title_y = safe_margin_top
    title_width = left_column_width
    title_max_width = left_column_width

    subtitle_x = safe_margin_x
    subtitle_width = left_column_width
    subtitle_max_width = left_column_width
    title_to_subtitle_gap = 48.0
    title_to_subtitle_min_gap = 26.0

    decoration_preferred_y = 380.0
    decoration_preferred_width = 398.0
    decoration_preferred_height = 460.0
    decoration_width = decoration_preferred_width
    decoration_height = decoration_preferred_height
    decoration_x = left_column_center_x - decoration_width / 2
    decoration_y = decoration_preferred_y

    card_height = 110.0
    card_min_height = 86.0
    card_gap = 55.0
    card_min_gap = 25.0
    card_radius = 14.0

    card_padding_left = 56.0
    card_padding_right = 45.0
    label_width = 180.0
    label_to_body_gap = 58.0

    arrow_x = cards_x + 118.0
    arrow_gap_from_card = 0.0

    # =====================================================
    # Inline vector decoration
    # =====================================================

    decoration_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="520" height="600" viewBox="0 0 520 600">
  <defs>
    <linearGradient id="simpleGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#29144F"/>
      <stop offset="52%" stop-color="#6540A9"/>
      <stop offset="100%" stop-color="#9865EE"/>
    </linearGradient>
    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="12"/>
    </filter>
  </defs>

  <g opacity="0.48" filter="url(#softGlow)">
    <circle cx="260" cy="100" r="82" fill="#8959D9"/>
    <path
      d="M58,170 H462 V188
         C462,300 395,365 260,365
         C125,365 58,300 58,188 Z"
      fill="#8959D9"/>
    <path
      d="M0,286 H520 V326
         C520,475 445,570 260,630
         C75,570 0,475 0,326 Z"
      fill="#8959D9"/>
  </g>

  <circle cx="260" cy="100" r="82" fill="url(#simpleGradient)"/>

  <path
    d="M58,170 H462 V188
       C462,300 395,365 260,365
       C125,365 58,300 58,188 Z"
    fill="url(#simpleGradient)"/>

  <path
    d="M0,286 H520 V326
       C520,475 445,570 260,630
       C75,570 0,475 0,326 Z"
    fill="url(#simpleGradient)"/>
</svg>
""".strip()

    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
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
            directory
            for directory in directories
            if directory.exists()
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

        font = ImageFont.truetype(fallback, 12)
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

        return (
            float(ascent + descent)
            * line_spacing
        )

    def wrap_text(
        text: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        def split_long_word(word: str) -> list[str]:
            if (
                measure_text_width(
                    word,
                    font_path,
                    font_size_pt,
                )
                <= max_width
            ):
                return [word]

            chunks: list[str] = []
            current = ""

            for character in word:
                candidate = f"{current}{character}"

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
                    chunks.append(current)
                    current = character

            if current:
                chunks.append(current)

            return chunks or [word]

        result: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words: list[str] = []

            for word in paragraph.split():
                words.extend(split_long_word(word))

            if not words:
                result.append("")
                continue

            current = ""

            for word in words:
                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 3.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines) * line_height
                + padding
            ),
        }

    # =====================================================
    # Typography and responsive fitting
    # =====================================================

    title_font_name = "Arial"
    subtitle_font_name = "Arial"
    step_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=True,
    )
    subtitle_font_path = resolve_font_path(
        subtitle_font_name,
        bold=True,
    )
    step_label_font_path = resolve_font_path(
        step_font_name,
        bold=True,
    )
    step_body_font_path = resolve_font_path(
        step_font_name,
        bold=True,
    )

    title_font_size = 48.0
    title_min_font_size = title_font_size

    subtitle_font_size = 21.0
    subtitle_min_font_size = subtitle_font_size

    step_label_font_size = 29.0
    step_label_min_font_size = 21.0

    step_body_font_size = 15.0
    step_body_min_font_size = 12.0

    title_line_spacing = 0.92
    subtitle_line_spacing = 1.18
    step_line_spacing = 1.05

    text_to_decoration_gap = 36.0
    decoration_bottom = canvas_height - safe_margin_bottom

    def calculate_left_text_layout() -> tuple[dict, dict, float, float]:
        current_title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=title_font_size,
            max_width=title_width,
            line_spacing=title_line_spacing,
            padding=8,
        )

        current_subtitle_y = (
            title_y
            + current_title_layout["height"]
            + title_to_subtitle_gap
        )

        current_subtitle_layout = layout_text(
            subtitle,
            font_path=subtitle_font_path,
            font_size=subtitle_font_size,
            max_width=subtitle_width,
            line_spacing=subtitle_line_spacing,
            padding=8,
        )

        current_text_bottom = (
            current_subtitle_y
            + current_subtitle_layout["height"]
        )

        return (
            current_title_layout,
            current_subtitle_layout,
            current_subtitle_y,
            current_text_bottom,
        )

    for _ in range(80):
        (
            title_layout,
            subtitle_layout,
            subtitle_y,
            text_bottom,
        ) = calculate_left_text_layout()

        if text_bottom <= decoration_bottom:
            break

        changed_text_box = False

        if title_width < title_max_width:
            title_width = min(
                title_max_width,
                title_width + 12.0,
            )
            changed_text_box = True

        if subtitle_width < subtitle_max_width:
            subtitle_width = min(
                subtitle_max_width,
                subtitle_width + 12.0,
            )
            changed_text_box = True

        if (
            not changed_text_box
            and title_to_subtitle_gap > title_to_subtitle_min_gap
        ):
            title_to_subtitle_gap = max(
                title_to_subtitle_min_gap,
                title_to_subtitle_gap - 2.0,
            )
            changed_text_box = True

        if not changed_text_box:
            break

    decoration_y = max(
        decoration_preferred_y,
        text_bottom + text_to_decoration_gap,
    )

    decoration_width = decoration_preferred_width
    decoration_height = decoration_preferred_height
    decoration_x = left_column_center_x - decoration_width / 2

    parsed_steps = [
        (
            step["step"].strip(),
            step["content"].strip(),
        )
        for step in steps
    ]

    def calculate_step_layouts(
        current_card_height: float,
        current_gap: float,
        current_label_size: float,
        current_body_size: float,
    ) -> dict:
        layouts: list[dict] = []
        cursor_y = cards_top

        body_x = (
            cards_x
            + card_padding_left
            + label_width
            + label_to_body_gap
        )
        body_width = max(
            1.0,
            cards_right
            - body_x
            - card_padding_right,
        )

        for label, body in parsed_steps:
            label_layout = layout_text(
                label,
                font_path=step_label_font_path,
                font_size=current_label_size,
                max_width=label_width,
                line_spacing=step_line_spacing,
                padding=2,
            )

            body_layout = layout_text(
                body,
                font_path=step_body_font_path,
                font_size=current_body_size,
                max_width=body_width,
                line_spacing=step_line_spacing,
                padding=2,
            )

            text_height = max(
                label_layout["height"],
                body_layout["height"],
            )

            item_height = max(
                current_card_height,
                text_height + 24.0,
            )

            layouts.append(
                {
                    "label": label_layout,
                    "body": body_layout,
                    "x": cards_x,
                    "y": cursor_y,
                    "width": cards_width,
                    "height": item_height,
                    "label_x": cards_x + card_padding_left,
                    "body_x": body_x,
                    "body_width": body_width,
                }
            )

            cursor_y += item_height + current_gap

        if layouts:
            cursor_y -= current_gap

        return {
            "items": layouts,
            "total_height": cursor_y - cards_top,
        }

    step_layouts = calculate_step_layouts(
        card_height,
        card_gap,
        step_label_font_size,
        step_body_font_size,
    )

    for _ in range(200):
        if step_layouts["total_height"] <= cards_area_height:
            break

        changed = False

        if card_gap > card_min_gap:
            card_gap = max(
                card_min_gap,
                card_gap - 2,
            )
            changed = True

        elif card_height > card_min_height:
            card_height = max(
                card_min_height,
                card_height - 2,
            )
            changed = True

        elif step_body_font_size > step_body_min_font_size:
            step_body_font_size = max(
                step_body_min_font_size,
                step_body_font_size - 0.5,
            )
            changed = True

        elif step_label_font_size > step_label_min_font_size:
            step_label_font_size = max(
                step_label_min_font_size,
                step_label_font_size - 0.5,
            )
            changed = True

        if not changed:
            break

        step_layouts = calculate_step_layouts(
            card_height,
            card_gap,
            step_label_font_size,
            step_body_font_size,
        )

    if step_layouts["total_height"] > cards_area_height:
        raise ValueError(
            "The process steps are too long to fit without overlap"
        )

    cards_offset_y = (
        cards_area_height
        - step_layouts["total_height"]
    ) / 2

    for item in step_layouts["items"]:
        item["y"] += cards_offset_y

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

    svg_node = add(
        "svg",
        x=decoration_x,
        y=decoration_y,
        width=decoration_width,
        height=decoration_height,
        pixel_width=520,
        pixel_height=600,
    )
    svg_node.text = decoration_svg

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=title_min_font_size,
        bold="true",
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        subtitle_layout["source_text"],
        x=subtitle_x,
        y=subtitle_y,
        width=subtitle_width,
        height=subtitle_layout["height"],
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=subtitle_layout["font_size"],
        min_font_size=subtitle_min_font_size,
        bold="true",
        color=subtitle_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(subtitle_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=subtitle_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    def rounded_card_svg(
        width: float,
        height: float,
        radius: float,
    ) -> str:
        return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{int(width)}" height="{int(height)}" viewBox="0 0 {width:.2f} {height:.2f}">
  <defs>
    <linearGradient id="cardGradient" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#8750F7"/>
      <stop offset="100%" stop-color="#3E335F"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{width:.2f}" height="{height:.2f}" rx="{radius:.2f}" ry="{radius:.2f}" fill="url(#cardGradient)"/>
</svg>
""".strip()

    for index, item in enumerate(step_layouts["items"]):
        card_svg_node = add(
            "svg",
            x=item["x"],
            y=item["y"],
            width=item["width"],
            height=item["height"],
            pixel_width=int(item["width"]),
            pixel_height=int(item["height"]),
        )
        card_svg_node.text = rounded_card_svg(
            item["width"],
            item["height"],
            card_radius,
        )

        label_y = (
            item["y"]
            + (item["height"] - item["label"]["height"]) / 2
        )
        body_y = (
            item["y"]
            + (item["height"] - item["body"]["height"]) / 2
        )

        textbox(
            item["label"]["source_text"],
            x=item["label_x"],
            y=label_y,
            width=label_width,
            height=item["label"]["height"],
            font=step_font_name,
            font_path=str(step_label_font_path),
            size=item["label"]["font_size"],
            min_font_size=item["label"]["font_size"],
            bold="true",
            color=step_label_color,
            align="left",
            vertical_align="top",
            single_line="false",
            max_lines=len(item["label"]["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=step_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        textbox(
            item["body"]["source_text"],
            x=item["body_x"],
            y=body_y,
            width=item["body_width"],
            height=item["body"]["height"],
            font=step_font_name,
            font_path=str(step_body_font_path),
            size=item["body"]["font_size"],
            min_font_size=item["body"]["font_size"],
            bold="true",
            color=step_body_color,
            align="left",
            vertical_align="top",
            single_line="false",
            max_lines=len(item["body"]["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=step_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        if index < len(step_layouts["items"]) - 1:
            next_item = step_layouts["items"][index + 1]
            arrow_top = item["y"] + item["height"] + arrow_gap_from_card
            arrow_bottom = next_item["y"] - arrow_gap_from_card

            add(
                "line",
                x1=arrow_x,
                y1=arrow_top,
                x2=arrow_x,
                y2=arrow_bottom - 10,
                color=arrow_color,
                width=1.4,
            )

            add(
                "polygon",
                points=(
                    f"{arrow_x - 6:.2f},{arrow_bottom - 10:.2f} "
                    f"{arrow_x + 6:.2f},{arrow_bottom - 10:.2f} "
                    f"{arrow_x:.2f},{arrow_bottom:.2f}"
                ),
                fill=arrow_color,
                line_color="none",
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

def generate_implementation_timeline_slide_xml(
    title: str = "Implementation timeline Implementation timeline",
    subtitle: str = (
        "Forge offers a structured rollout designed for minimal disruption"
    ),
    timeline_items: list[dict[str, str]] = [
        {
            "label": "Week 1",
            "content": "Kickoff and workspace setup ",
        },
        {
            "label": "Week 2",
            "content": "Workflow configuration and security policies",
        },
        {
            "label": "Week 3",
            "content": "Team onboarding and training",
        },
        {
            "label": "Week 4",
            "content": "Go-live and optimization",
        },
    ],
    background_color: str = "#1A0B3A",
    title_color: str = "#A678FF",
    subtitle_color: str = "#F7F2FF",
    timeline_color: str = "#A678FF",
    label_color: str = "#F7F2FF",
    content_color: str = "#F7F2FF",
) -> str:
    """
    Generate XML for an implementation timeline slide.

    The layout features a dark purple background, a large title and
    subtitle at the top-left, an abstract inline vector decoration
    at the top-right, and a horizontal timeline with labeled milestones
    across the lower half of the slide.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    if not subtitle.strip():
        raise ValueError("subtitle must not be empty")

    if not timeline_items:
        raise ValueError("timeline_items must contain at least one item")

    if any(
        not isinstance(item, dict)
        or not item.get("label", "").strip()
        or not item.get("content", "").strip()
        for item in timeline_items
    ):
        raise ValueError(
            "Each timeline item must contain non-empty label and content"
        )

    # =====================================================
    # Canvas and layout regions
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    safe_left = 24.0
    safe_right = 24.0

    title_x = 24.0
    title_y = 70.0
    title_width = 1040.0
    subtitle_x = 24.0
    subtitle_width = 1110.0
    title_to_subtitle_gap = 20.0

    decoration_width = 360.0
    decoration_height = 405.0
    decoration_x = canvas_width - decoration_width
    decoration_y = 0.0

    timeline_y = 610.0
    timeline_start_x = 60.0
    timeline_end_x = canvas_width - 60.0
    dot_radius = 15.0

    label_y_gap = 46.0
    content_y_gap = 42.0
    item_cell_padding = 24.0

    content_bottom_limit = 820.0

    # =====================================================
    # Inline vector decoration
    # =====================================================

    decoration_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="252" height="284" viewBox="0 0 252 284" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="panelGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#9A78DB"/>
      <stop offset="52%" stop-color="#8D69CE"/>
      <stop offset="100%" stop-color="#614B94"/>
    </linearGradient>
    <linearGradient id="mainDiscGrad" x1="0.36" y1="0" x2="0.7" y2="1">
      <stop offset="0%" stop-color="#D7C6FF" stop-opacity="0.94"/>
      <stop offset="44%" stop-color="#B493F2" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#8A5FDC" stop-opacity="0.76"/>
    </linearGradient>
    <linearGradient id="innerDiscGrad" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0%" stop-color="#B79AFF"/>
      <stop offset="100%" stop-color="#7E58C9"/>
    </linearGradient>
    <linearGradient id="backArcGrad" x1="0" y1="0" x2="0.75" y2="1">
      <stop offset="0%" stop-color="#4A3A68" stop-opacity="0.78"/>
      <stop offset="100%" stop-color="#251844" stop-opacity="0.96"/>
    </linearGradient>
    <filter id="softEdge" x="-16%" y="-16%" width="132%" height="132%">
      <feGaussianBlur stdDeviation="2.2"/>
    </filter>
  </defs>

  <!-- soft dark arc behind the composition -->
  <circle cx="136" cy="0" r="119" fill="url(#backArcGrad)" filter="url(#softEdge)"/>

  <!-- rounded panel visible beneath the sweeping disc -->
  <rect x="16" y="82" width="154" height="155" rx="17" ry="17"
        fill="url(#panelGrad)"/>

  <!-- large translucent disc creates the curved sweep over the panel -->
  <circle cx="252" cy="0" r="236" fill="url(#mainDiscGrad)"/>

  <!-- dark outer ring cropped by the top and right edges -->
  <circle cx="252" cy="0" r="115" fill="#190B39"/>

  <!-- illuminated inner disc leaves the soft purple crescent -->
  <circle cx="252" cy="0" r="75" fill="url(#innerDiscGrad)"/>
</svg>
""".strip()

    # =====================================================
    # Font measurement helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
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
            directory
            for directory in directories
            if directory.exists()
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

        font = ImageFont.truetype(fallback, 12)
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

        return (
            float(ascent + descent)
            * line_spacing
        )

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
                word_width = measure_text_width(
                    word,
                    font_path,
                    font_size_pt,
                )

                if word_width > max_width:
                    raise ValueError(
                        f"The word '{word}' is wider than "
                        "the available text area"
                    )

                candidate = (
                    word
                    if not current
                    else f"{current} {word}"
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
                    current = word

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
        padding: float = 3.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": (
                len(lines) * line_height
                + padding
            ),
        }

    # =====================================================
    # Typography and responsive fitting
    # =====================================================

    title_font_name = "Arial"
    subtitle_font_name = "Arial"
    label_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=False,
    )
    subtitle_font_path = resolve_font_path(
        subtitle_font_name,
        bold=True,
    )
    label_font_path = resolve_font_path(
        label_font_name,
        bold=True,
    )
    body_font_path = resolve_font_path(
        body_font_name,
        bold=True,
    )

    title_font_size = 52.0
    title_min_font_size = 36.0

    subtitle_font_size = 21.0
    subtitle_min_font_size = 15.0

    label_font_size = 23.0
    label_min_font_size = 17.0

    content_font_size = 13.5
    content_min_font_size = 10.5

    title_line_spacing = 0.95
    subtitle_line_spacing = 1.0
    label_line_spacing = 1.0
    content_line_spacing = 1.12

    title_layout = layout_text(
        title,
        font_path=title_font_path,
        font_size=title_font_size,
        max_width=title_width,
        line_spacing=title_line_spacing,
        padding=3,
    )

    for _ in range(80):
        if title_layout["height"] <= 74.0:
            break

        if title_font_size <= title_min_font_size:
            break

        title_font_size = max(
            title_min_font_size,
            title_font_size - 0.5,
        )

        title_layout = layout_text(
            title,
            font_path=title_font_path,
            font_size=title_font_size,
            max_width=title_width,
            line_spacing=title_line_spacing,
            padding=3,
        )

    subtitle_y = (
        title_y
        + title_layout["height"]
        + title_to_subtitle_gap
    )

    subtitle_layout = layout_text(
        subtitle,
        font_path=subtitle_font_path,
        font_size=subtitle_font_size,
        max_width=subtitle_width,
        line_spacing=subtitle_line_spacing,
        padding=3,
    )

    for _ in range(80):
        if subtitle_layout["height"] <= 52.0:
            break

        if subtitle_font_size <= subtitle_min_font_size:
            break

        subtitle_font_size = max(
            subtitle_min_font_size,
            subtitle_font_size - 0.5,
        )

        subtitle_layout = layout_text(
            subtitle,
            font_path=subtitle_font_path,
            font_size=subtitle_font_size,
            max_width=subtitle_width,
            line_spacing=subtitle_line_spacing,
            padding=3,
        )

    item_count = len(timeline_items)

    timeline_text_left = safe_left
    timeline_text_right = canvas_width - safe_right
    cell_width = (
        timeline_text_right - timeline_text_left
    ) / item_count

    cell_ranges: list[tuple[float, float]] = []
    item_positions: list[float] = []

    for index in range(item_count):
        cell_left = (
            timeline_text_left
            + index * cell_width
        )
        cell_right = cell_left + cell_width
        dot_x = (
            cell_left + cell_right
        ) / 2

        cell_ranges.append(
            (
                cell_left,
                cell_right,
            )
        )
        item_positions.append(dot_x)

    timeline_start_x = item_positions[0]
    timeline_end_x = item_positions[-1]

    def calculate_timeline_layouts(
        current_label_size: float,
        current_content_size: float,
    ) -> dict:
        item_layouts: list[dict] = []

        max_bottom = 0.0

        for index, item in enumerate(timeline_items):
            dot_x = item_positions[index]
            cell_left, cell_right = cell_ranges[index]

            item_text_width = max(
                80.0,
                cell_right
                - cell_left
                - 2 * item_cell_padding,
            )
            text_x = (
                dot_x - item_text_width / 2
            )

            label_layout = layout_text(
                item["label"].strip(),
                font_path=label_font_path,
                font_size=current_label_size,
                max_width=item_text_width,
                line_spacing=label_line_spacing,
                padding=2,
            )

            content_layout = layout_text(
                item["content"].strip(),
                font_path=body_font_path,
                font_size=current_content_size,
                max_width=item_text_width,
                line_spacing=content_line_spacing,
                padding=2,
            )

            label_y = (
                timeline_y
                - label_y_gap
                - label_layout["height"]
            )
            content_y = timeline_y + content_y_gap

            max_bottom = max(
                max_bottom,
                content_y + content_layout["height"],
            )

            item_layouts.append(
                {
                    "dot_x": dot_x,
                    "text_x": text_x,
                    "text_width": item_text_width,
                    "label": label_layout,
                    "label_y": label_y,
                    "content": content_layout,
                    "content_y": content_y,
                }
            )

        return {
            "items": item_layouts,
            "max_bottom": max_bottom,
        }

    timeline_layout = calculate_timeline_layouts(
        label_font_size,
        content_font_size,
    )

    for _ in range(160):
        if timeline_layout["max_bottom"] <= content_bottom_limit:
            break

        changed = False

        if content_font_size > content_min_font_size:
            content_font_size = max(
                content_min_font_size,
                content_font_size - 0.5,
            )
            changed = True

        elif label_font_size > label_min_font_size:
            label_font_size = max(
                label_min_font_size,
                label_font_size - 0.5,
            )
            changed = True

        if not changed:
            break

        timeline_layout = calculate_timeline_layouts(
            label_font_size,
            content_font_size,
        )

    if timeline_layout["max_bottom"] > content_bottom_limit:
        raise ValueError(
            "The timeline content is too long to fit without overlap"
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

    svg_node = add(
        "svg",
        x=decoration_x,
        y=decoration_y,
        width=decoration_width,
        height=decoration_height,
        pixel_width=252,
        pixel_height=284,
    )
    svg_node.text = decoration_svg

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=title_layout["font_size"],
        bold="true",
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        subtitle_layout["source_text"],
        x=subtitle_x,
        y=subtitle_y,
        width=subtitle_width,
        height=subtitle_layout["height"],
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=subtitle_layout["font_size"],
        min_font_size=subtitle_layout["font_size"],
        bold="true",
        color=subtitle_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(subtitle_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=subtitle_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    add(
        "line",
        x1=timeline_start_x,
        y1=timeline_y,
        x2=timeline_end_x,
        y2=timeline_y,
        color=timeline_color,
        width=1.0,
    )

    for item in timeline_layout["items"]:
        add(
            "shape",
            type="circle",
            x=item["dot_x"] - dot_radius,
            y=timeline_y - dot_radius,
            width=dot_radius * 2,
            height=dot_radius * 2,
            fill=timeline_color,
            line_color="none",
        )

        textbox(
            item["label"]["source_text"],
            x=item["text_x"],
            y=item["label_y"],
            width=item["text_width"],
            height=item["label"]["height"],
            font=label_font_name,
            font_path=str(label_font_path),
            size=item["label"]["font_size"],
            min_font_size=item["label"]["font_size"],
            bold="true",
            color=label_color,
            align="center",
            vertical_align="top",
            single_line="false",
            max_lines=len(item["label"]["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=label_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        textbox(
            item["content"]["source_text"],
            x=item["text_x"],
            y=item["content_y"],
            width=item["text_width"],
            height=item["content"]["height"],
            font=body_font_name,
            font_path=str(body_font_path),
            size=item["content"]["font_size"],
            min_font_size=item["content"]["font_size"],
            bold="true",
            color=content_color,
            align="center",
            vertical_align="top",
            single_line="false",
            max_lines=len(item["content"]["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=content_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
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

def generate_problem_slide_xml(
    title: str = "The problem The problem The problem The problem",
    description: str = (
        "Keeping commercial spaces clean sounds simple—but many businesses Keeping commercial spaces clean sounds simple—but many businesses "
        "struggle with:"
    ),
    problem_items: list[str] = [
        "Missed cleaning tasks",
        "Different cleaners every visit",
        "Spaces that don’t stay clean for long",
        "No clear accountability across teams",
    ],
    card_colors: list[str] = [
        "#DDF2A6",
        "#9ED98C",
        "#00580A",
        "#7BC96F",
        "#4FA95C",
    ],
    card_text_colors: list[str] = [
        "#07520B",
        "#07520B",
        "#FFFFFF",
        "#07520B",
        "#FFFFFF",
    ],
    background_color: str = "#F7F7F2",
    title_color: str = "#07520B",
    description_color: str = "#07520B",
) -> str:
    """
    Generate XML for a problem statement slide.

    The layout features a row of large rounded cards hanging from the
    top edge, each containing a centered statement, with a title and
    supporting description anchored in the lower-left area.

    The text layout is adaptive: if the title, description, or card text
    becomes longer, the function automatically changes width, font size,
    spacing, and vertical placement to keep the slide balanced instead of
    throwing a fitting error.
    """

    if not title.strip():
        raise ValueError("title must not be empty")

    if not description.strip():
        raise ValueError("description must not be empty")

    if not problem_items:
        raise ValueError("problem_items must contain at least one item")

    if any(not item.strip() for item in problem_items):
        raise ValueError("problem_items must not contain empty items")

    if len(problem_items) > 5:
        raise ValueError("This layout supports up to five problem cards")

    if not card_colors:
        raise ValueError("card_colors must not be empty")

    if not card_text_colors:
        raise ValueError("card_text_colors must not be empty")

    canvas_width = 1600
    canvas_height = 900

    # =====================================================
    # Font helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            character.lower()
            for character in name
            if character.isalnum()
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
            directory
            for directory in directories
            if directory.exists()
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
            "Georgia": "georgia",
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
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                stem = normalize_font_name(path.stem)

                if normalized not in stem:
                    continue

                score = 70

                if stem == normalized:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 10
                elif has_bold:
                    score -= 10

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            return candidates[0][1]

        fallback = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        font = ImageFont.truetype(fallback, 12)
        font_path = getattr(font, "path", None)

        if not font_path:
            raise ValueError(f"Font '{font_name}' was not found")

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
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        font = load_font(font_path, font_size_pt)

        if hasattr(font, "getlength"):
            return float(font.getlength(text))

        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(
        font_path: Path,
        font_size_pt: float,
        line_spacing: float,
    ) -> float:
        font = load_font(font_path, font_size_pt)
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

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
                candidate = word if not current else f"{current} {word}"

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
                    if current:
                        result.append(current)
                    current = word

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
        padding: float = 3.0,
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
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "height": len(lines) * line_height + padding,
        }

    def fit_text_best_effort(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        width_candidates: list[float],
        preferred_max_height: float,
        absolute_min_font_size: float,
        line_spacing: float,
        padding: float = 3.0,
    ) -> dict:
        best_candidate = None

        for width in width_candidates:
            current_size = preferred_font_size

            while current_size >= absolute_min_font_size:
                try:
                    candidate = layout_text(
                        text,
                        font_path=font_path,
                        font_size=current_size,
                        max_width=width,
                        line_spacing=line_spacing,
                        padding=padding,
                    )
                except Exception:
                    current_size = round(current_size - 0.5, 2)
                    continue

                candidate["width"] = width

                score = (
                    max(0.0, candidate["height"] - preferred_max_height) * 1000
                    + max(0.0, preferred_font_size - current_size) * 10
                    + (max(width_candidates) - width) * 0.01
                )

                if (
                    best_candidate is None
                    or score < best_candidate["score"]
                ):
                    candidate["score"] = score
                    best_candidate = candidate

                if (
                    candidate["height"] <= preferred_max_height
                    and current_size >= min_font_size
                ):
                    candidate["score"] = score
                    return candidate

                current_size = round(current_size - 0.5, 2)

        if best_candidate is None:
            # Extremely defensive fallback.
            fallback_width = max(width_candidates)
            best_candidate = {
                "source_text": text,
                "text": text,
                "lines": [text],
                "font_size": absolute_min_font_size,
                "height": preferred_max_height,
                "width": fallback_width,
                "score": 10**9,
            }

        return best_candidate

    # =====================================================
    # Typography
    # =====================================================

    title_font_name = "Arial"
    description_font_name = "Georgia"
    card_font_name = "Arial"

    title_font_path = resolve_font_path(title_font_name, bold=True)
    description_font_path = resolve_font_path(
        description_font_name,
        bold=False,
    )
    card_font_path = resolve_font_path(card_font_name, bold=False)

    title_color = title_color
    description_color = description_color

    title_font_size = 50.0
    description_font_size = 22.0

    title_line_spacing = 0.95
    description_line_spacing = 1.16
    card_line_spacing = 1.08

    count = len(problem_items)

    card_font_defaults = {
        1: 34.0,
        2: 29.0,
        3: 25.0,
        4: 19.0,
        5: 16.0,
    }
    card_min_defaults = {
        1: 22.0,
        2: 20.0,
        3: 17.0,
        4: 11.5,
        5: 9.5,
    }

    # =====================================================
    # Dynamic cards geometry
    # =====================================================

    cards_area_x = 120.0
    cards_area_width = 1440.0
    cards_top_crop_base = -105.0

    effective_gap = 28.0 if count <= 3 else 18.0 if count == 4 else 12.0
    available_width = cards_area_width - effective_gap * (count - 1)
    card_width = available_width / count

    bottom_targets = {
        1: [560.0],
        2: [510.0, 580.0],
        3: [470.0, 540.0, 620.0],
        4: [455.0, 510.0, 570.0, 640.0],
        5: [440.0, 485.0, 530.0, 585.0, 645.0],
    }[count]

    card_specs: list[dict] = []

    for index in range(count):
        x = cards_area_x + index * (card_width + effective_gap)
        y = cards_top_crop_base + index * 12.0
        bottom = bottom_targets[index]
        height = bottom - y

        side_padding = max(
            18.0,
            min(50.0, card_width * 0.10),
        )

        max_text_height = min(
            230.0,
            height - 70.0,
        )

        card_specs.append(
            {
                "x": x,
                "y": y,
                "width": card_width,
                "height": height,
                "text_center_y": y + height * 0.53,
                "side_padding": side_padding,
                "max_text_height": max_text_height,
            }
        )

    # =====================================================
    # Bottom-left text block - adaptive instead of hard fail
    # =====================================================

    text_block_left = 16.0
    text_block_top_base = 610.0
    text_block_bottom = 880.0
    preferred_gap = 20.0

    title_layout = None
    description_layout = None
    title_x = text_block_left
    title_y = text_block_top_base
    description_x = text_block_left
    description_y = title_y

    width_candidates = [760.0, 860.0, 980.0, 1100.0]

    for width in width_candidates:
        candidate_title = fit_text_best_effort(
            title,
            font_path=title_font_path,
            preferred_font_size=title_font_size,
            min_font_size=34.0,
            width_candidates=[width],
            preferred_max_height=115.0,
            absolute_min_font_size=10.0,
            line_spacing=title_line_spacing,
        )

        local_gap = 22.0 if candidate_title["height"] < 80 else 14.0
        local_title_y = text_block_top_base

        remaining_height = (
            text_block_bottom
            - (local_title_y + candidate_title["height"] + local_gap)
        )

        if remaining_height < 36.0:
            local_title_y = max(
                540.0,
                text_block_bottom
                - candidate_title["height"]
                - local_gap
                - 36.0,
            )
            remaining_height = (
                text_block_bottom
                - (local_title_y + candidate_title["height"] + local_gap)
            )

        candidate_description = fit_text_best_effort(
            description,
            font_path=description_font_path,
            preferred_font_size=description_font_size,
            min_font_size=15.0,
            width_candidates=[width],
            preferred_max_height=max(remaining_height, 36.0),
            absolute_min_font_size=9.0,
            line_spacing=description_line_spacing,
        )

        total_height = (
            candidate_title["height"]
            + local_gap
            + candidate_description["height"]
        )

        score = (
            max(0.0, total_height - (text_block_bottom - local_title_y)) * 1000
            + max(0.0, title_font_size - candidate_title["font_size"]) * 10
            + max(0.0, description_font_size - candidate_description["font_size"]) * 4
            + (1100.0 - width) * 0.02
        )

        if title_layout is None or score < title_layout["combined_score"]:
            candidate_title["combined_score"] = score
            title_layout = candidate_title
            description_layout = candidate_description
            title_x = text_block_left
            title_y = local_title_y
            description_x = text_block_left
            description_y = (
                title_y
                + title_layout["height"]
                + local_gap
            )

    # Final defensive move: if the description still runs too low, shift both upward.
    overflow = (
        description_y
        + description_layout["height"]
        - text_block_bottom
    )
    if overflow > 0:
        shift = min(
            overflow,
            max(0.0, title_y - 520.0),
        )
        title_y -= shift
        description_y -= shift

    # =====================================================
    # Card text fitting
    # =====================================================

    card_layouts: list[dict] = []

    for index, item in enumerate(problem_items):
        spec = card_specs[index]
        text_width = spec["width"] - 2 * spec["side_padding"]

        card_layout = fit_text_best_effort(
            item,
            font_path=card_font_path,
            preferred_font_size=card_font_defaults[count],
            min_font_size=card_min_defaults[count],
            width_candidates=[text_width],
            preferred_max_height=spec["max_text_height"],
            absolute_min_font_size=8.0,
            line_spacing=card_line_spacing,
        )

        text_x = spec["x"] + spec["side_padding"]
        text_y = spec["text_center_y"] - card_layout["height"] / 2

        card_layouts.append(
            {
                "spec": spec,
                "layout": card_layout,
                "text_x": text_x,
                "text_y": text_y,
                "text_width": text_width,
            }
        )

    # =====================================================
    # XML assembly
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

    for index, card_data in enumerate(card_layouts):
        spec = card_data["spec"]
        card_fill = card_colors[index % len(card_colors)]
        card_text_color = card_text_colors[index % len(card_text_colors)]

        add(
            "shape",
            type="rounded_rectangle",
            x=spec["x"],
            y=spec["y"],
            width=spec["width"],
            height=spec["height"],
            fill=card_fill,
            line_color="none",
        )

        textbox(
            card_data["layout"]["source_text"],
            x=card_data["text_x"],
            y=card_data["text_y"],
            width=card_data["text_width"],
            height=card_data["layout"]["height"],
            font=card_font_name,
            font_path=str(card_font_path),
            size=card_data["layout"]["font_size"],
            min_font_size=max(8.0, card_data["layout"]["font_size"] - 1.0),
            color=card_text_color,
            align="center",
            vertical_align="middle",
            single_line="false",
            max_lines=len(card_data["layout"]["lines"]),
            overflow="shrink",
            reflow_on_resize="true",
            line_spacing=card_line_spacing,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_layout["width"],
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(10.0, title_layout["font_size"] - 1.0),
        bold="true",
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=title_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        description_layout["source_text"],
        x=description_x,
        y=description_y,
        width=description_layout["width"],
        height=description_layout["height"],
        font=description_font_name,
        font_path=str(description_font_path),
        size=description_layout["font_size"],
        min_font_size=max(9.0, description_layout["font_size"] - 1.0),
        color=description_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(description_layout["lines"]),
        overflow="shrink",
        reflow_on_resize="true",
        line_spacing=description_line_spacing,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content
