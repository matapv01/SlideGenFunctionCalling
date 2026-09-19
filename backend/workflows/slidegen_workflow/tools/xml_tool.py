from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

from PIL import ImageFont


# Keep the requested font size even when the text exceeds its textbox.
# Overflow is handled by wrapping/clipping in the renderer; generation never
# silently reduces the requested font size.
AUTO_SHRINK_TEXT = False


def _resolve_font_fallback_path(
    bold: bool = False,
    italic: bool = False,
) -> Path:
    """Return a concrete font file path available in Linux/Docker or Windows."""
    candidates = [
        "DejaVuSans-BoldOblique.ttf"
        if bold and italic
        else "DejaVuSans-Bold.ttf"
        if bold
        else "DejaVuSans-Oblique.ttf"
        if italic
        else "DejaVuSans.ttf",
        "FreeSansBoldOblique.ttf"
        if bold and italic
        else "FreeSansBold.ttf"
        if bold
        else "FreeSansOblique.ttf"
        if italic
        else "FreeSans.ttf",
        "LiberationSans-BoldItalic.ttf"
        if bold and italic
        else "LiberationSans-Bold.ttf"
        if bold
        else "LiberationSans-Italic.ttf"
        if italic
        else "LiberationSans-Regular.ttf",
    ]
    directories = [
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/truetype/freefont"),
        Path("/usr/share/fonts/truetype/liberation"),
        Path("/usr/local/share/fonts"),
        Path.cwd(),
    ]
    windir = os.environ.get("WINDIR")
    if windir:
        directories.append(Path(windir) / "Fonts")

    for directory in directories:
        for filename in candidates:
            path = directory / filename
            if not path.exists():
                continue
            try:
                ImageFont.truetype(str(path), 12)
                return path
            except OSError:
                continue

    raise OSError("No usable fallback font was found in the runtime environment")


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

        fallback_name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        fallback_paths = [
            Path("/usr/share/fonts/truetype/dejavu") / fallback_name,
            Path("/usr/share/fonts/truetype/freefont") / ("FreeSansBold.ttf" if bold else "FreeSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation") / ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"),
            Path("/usr/local/share/fonts") / fallback_name,
            Path.cwd() / fallback_name,
        ]
        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue
            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        return _resolve_font_fallback_path(bold=bold)

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

    title_font_size = 58.0
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

    for _ in range(140 if AUTO_SHRINK_TEXT else 0):
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

        font_path = _resolve_font_fallback_path(bold=bold)

    

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

    title_font_size = 60.0
    title_min_font_size = 42.0

    subtitle_font_size = 20.0
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

        elif AUTO_SHRINK_TEXT and subtitle_font_size > subtitle_min_font_size:
            subtitle_font_size = max(
                subtitle_min_font_size,
                subtitle_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and title_font_size > title_min_font_size:
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
        overflow="clip",
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

def generate_elegant_professional_cover_slide_xml(
    title: str = "Messi cầu thủ vĩ đại nhất thế giới",
    subtitle: str = "Bài thuyết trình về Messi, cầu thủ bóng đá xuất sắc nhất mọi thời đại, với những thành tích và đóng góp đáng kinh ngạc cho đội tuyển quốc gia và câu lạc bộ.",
    presented_by_label: str = "PRESENTED BY",
    presenter_name: str = "NAME SURNAME",
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1517048676732-d65bc937f952"
        "?q=80&w=1200&auto=format&fit=crop"
    ),
    background_color: str = "#E5E5DB",
    panel_color: str = "#F2F0E7",
    title_color: str = "#64625C",
    subtitle_color: str = "#64625C",
    meta_label_color: str = "#76746E",
    meta_name_color: str = "#55534E",
    accent_color: str = "#9FA984",
) -> str:
    """
    Generate XML for an elegant editorial cover slide.

    The layout features a large image block on the left, a light content
    panel on the right, soft corner accents, a centered title and subtitle,
    and a small presenter credit near the bottom of the panel. The text
    layout is adaptive so longer content can use wider text areas, smaller
    font sizes, and adjusted spacing instead of feeling constrained.
    """



    canvas_width = 1600
    canvas_height = 900

    image_x = 112.0
    image_y = 92.0
    image_width = 650.0
    image_height = 716.0

    panel_x = 838.0
    panel_y = 92.0
    panel_width = 650.0
    panel_height = 716.0
    panel_center_x = panel_x + panel_width / 2

    # -----------------------------------------------------
    # Font helpers
    # -----------------------------------------------------

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": ["arial"],
            "Calibri": ["calibri"],
            "Aptos": ["aptos"],
            "Helvetica": ["helvetica", "arial"],
            "Arial": ["arial"],
            "Times New Roman": ["timesnewroman", "times"],
            "Garamond": ["garamond"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(
                font_name,
                [font_name],
            )
        ]

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

                if not any(
                    normalized in stem
                    for normalized in normalized_names
                ):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in (
                        "bold",
                        "bd",
                        "semibold",
                        "demi",
                    )
                )
                has_italic = any(
                    token in stem
                    for token in (
                        "italic",
                        "oblique",
                        "it",
                    )
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 10
                elif has_bold:
                    score -= 8

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(
                key=lambda item: item[0],
                reverse=True,
            )

            for _, path in candidates:
                try:
                    ImageFont.truetype(
                        str(path),
                        12,
                    )
                    return path
                except OSError:
                    continue

        windir = Path(
            os.environ.get(
                "WINDIR",
                "C:/Windows",
            )
        )
        windows_fonts = windir / "Fonts"

        if bold and italic:
            explicit_fallbacks = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                windows_fonts / "arialbi.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            explicit_fallbacks = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                windows_fonts / "aptos-bold.ttf",
                windows_fonts / "arialbd.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            explicit_fallbacks = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                windows_fonts / "aptos-italic.ttf",
                windows_fonts / "ariali.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            explicit_fallbacks = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                windows_fonts / "aptos.ttf",
                windows_fonts / "arial.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
                Path("/Library/Fonts/Arial.ttf"),
                Path.home() / "Library/Fonts/Arial.ttf",
            ]

        for fallback_path in explicit_fallbacks:
            if not fallback_path.exists():
                continue

            try:
                ImageFont.truetype(
                    str(fallback_path),
                    12,
                )
                return fallback_path
            except OSError:
                continue

        for directory in font_directories():
            try:
                font_files = directory.rglob("*")
            except OSError:
                continue

            for path in font_files:
                if path.suffix.lower() not in {
                    ".ttf",
                    ".otf",
                    ".ttc",
                }:
                    continue

                try:
                    ImageFont.truetype(
                        str(path),
                        12,
                    )
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    canvas_dpi = 120.0

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
        font = load_font(font_path, font_size_pt)
        if hasattr(font, "getlength"):
            return float(font.getlength(text))
        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(font_path: Path, font_size_pt: float, line_spacing: float) -> float:
        font = load_font(font_path, font_size_pt)
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

    def wrap_text(text: str, font_path: Path, font_size_pt: float, max_width: float) -> list[str]:
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
                continue

            current = ""

            for word in words:
                candidate = word if not current else f"{current} {word}"

                if (
                    not current
                    or measure_text_width(candidate, font_path, font_size_pt) <= max_width
                ):
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        box_width: float,
        line_spacing: float,
        padding: float = 2.0,
    ) -> dict:
        lines = wrap_text(text, font_path, font_size, box_width)
        line_height = measure_line_height(font_path, font_size, line_spacing)
        widest_line = 0.0

        for line in lines:
            widest_line = max(
                widest_line,
                measure_text_width(line, font_path, font_size),
            )

        return {
            "source_text": text,
            "text": "\n".join(lines),
            "lines": lines,
            "font_size": font_size,
            "box_width": box_width,
            "used_width": widest_line,
            "height": len(lines) * line_height + padding,
        }

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        width_candidates: list[float],
        max_height: float,
        line_spacing: float,
        padding: float = 2.0,
        prefer_fewer_lines: bool = True,
        prefer_wider_boxes: bool = True,
    ) -> dict:
        best = None

        for box_width in width_candidates:
            current_font_size = preferred_font_size

            while current_font_size >= min_font_size:
                layout = layout_text(
                    text,
                    font_path=font_path,
                    font_size=current_font_size,
                    box_width=box_width,
                    line_spacing=line_spacing,
                    padding=padding,
                )

                line_penalty = len(layout["lines"]) * (28.0 if prefer_fewer_lines else 6.0)
                width_bonus = -box_width * (0.08 if prefer_wider_boxes else 0.03)
                score = (
                    max(0.0, layout["height"] - max_height) * 1800
                    + (preferred_font_size - current_font_size) * 12
                    + line_penalty
                    + width_bonus
                )

                if best is None or score < best["score"]:
                    layout["score"] = score
                    best = layout

                if layout["height"] <= max_height:
                    layout["score"] = score
                    if best is None or score < best["score"]:
                        best = layout
                    break

                break

        return best

    title_font_path = resolve_font_path("Arial", bold=False)
    subtitle_font_path = resolve_font_path("Arial", italic=False)
    meta_font_path = resolve_font_path("Arial", bold=False)
    meta_bold_font_path = resolve_font_path("Arial", bold=True)

    panel_inner_left = panel_x + 52.0
    panel_inner_right = panel_x + panel_width - 52.0
    panel_inner_width = panel_inner_right - panel_inner_left

    display_title = (
        "Elegant\nProfessional"
        if title.strip() == "Elegant Professional"
        else title
    )

    title_layout = fit_text(
        display_title,
        font_path=title_font_path,
        preferred_font_size=58.0,
        min_font_size=18.0,
        width_candidates=[
            panel_inner_width - 110.0,
            panel_inner_width - 60.0,
            panel_inner_width - 20.0,
        ],
        max_height=188.0,
        line_spacing=1.04,
        padding=2.0,
        prefer_fewer_lines=True,
        prefer_wider_boxes=True,
    )

    subtitle_layout = fit_text(
        subtitle,
        font_path=subtitle_font_path,
        preferred_font_size=20.0,
        min_font_size=12.0,
        width_candidates=[
            270.0,
            340.0,
            430.0,
            panel_inner_width - 140.0,
        ],
        max_height=66.0,
        line_spacing=1.0,
        padding=1.0,
        prefer_fewer_lines=False,
        prefer_wider_boxes=True,
    )

    label_layout = fit_text(
        presented_by_label,
        font_path=meta_font_path,
        preferred_font_size=15.5,
        min_font_size=10.0,
        width_candidates=[220.0, 280.0, 340.0],
        max_height=26.0,
        line_spacing=1.0,
        padding=1.0,
        prefer_fewer_lines=False,
        prefer_wider_boxes=True,
    )

    name_layout = fit_text(
        presenter_name,
        font_path=meta_bold_font_path,
        preferred_font_size=16.5,
        min_font_size=10.0,
        width_candidates=[220.0, 300.0, 360.0],
        max_height=30.0,
        line_spacing=1.0,
        padding=1.0,
        prefer_fewer_lines=False,
        prefer_wider_boxes=True,
    )

    title_width = min(title_layout["box_width"], panel_inner_width)
    subtitle_width = min(subtitle_layout["box_width"], panel_inner_width - 70.0)
    meta_width = min(
        max(label_layout["box_width"], name_layout["box_width"]),
        panel_inner_width - 120.0,
    )

    title_x = panel_center_x - title_width / 2
    subtitle_x = panel_center_x - subtitle_width / 2
    meta_x = panel_center_x - meta_width / 2

    top_anchor = panel_y + 144.0
    title_y = top_anchor

    dynamic_gap_1 = 44.0 if title_layout["height"] <= 110.0 else 30.0
    subtitle_y = title_y + title_layout["height"] + dynamic_gap_1

    meta_y = panel_y + panel_height - 130.0

    # If title grows, allow the block to shift up slightly and subtitle to use less gap.
    if subtitle_y + subtitle_layout["height"] > panel_y + 470.0:
        overflow = subtitle_y + subtitle_layout["height"] - (panel_y + 470.0)
        title_y = max(panel_y + 118.0, title_y - overflow * 0.55)
        dynamic_gap_1 = 28.0
        subtitle_y = title_y + title_layout["height"] + dynamic_gap_1

    # If still tight, move the meta block a little lower and compress spacing gracefully.
    min_meta_top = subtitle_y + subtitle_layout["height"] + 52.0
    if meta_y < min_meta_top:
        meta_y = min_meta_top

    if meta_y + label_layout["height"] + name_layout["height"] + 10.0 > panel_y + panel_height - 46.0:
        meta_y = panel_y + panel_height - (
            label_layout["height"] + name_layout["height"] + 56.0
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
        node = add("textbox", **attrs)
        node.text = text
        return node

    # Soft vignette accents matching the reference slide.  SVG is used here
    # so the corners fade out smoothly instead of becoming hard-edged ovals.
    corner_wash = add(
        "svg",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=canvas_width,
        pixel_height=canvas_height,
    )
    corner_wash.text = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <radialGradient id="topLeft" cx="0%" cy="0%" r="72%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.86"/>
      <stop offset="42%" stop-color="{accent_color}" stop-opacity="0.46"/>
      <stop offset="68%" stop-color="{accent_color}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="bottomRight" cx="100%" cy="100%" r="72%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.86"/>
      <stop offset="42%" stop-color="{accent_color}" stop-opacity="0.46"/>
      <stop offset="68%" stop-color="{accent_color}" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1600" height="900" fill="url(#topLeft)"/>
  <rect width="1600" height="900" fill="url(#bottomRight)"/>
</svg>'''

    add(
        "image",
        src=image_url,
        x=image_x,
        y=image_y,
        width=image_width,
        height=image_height,
    )

    add(
        "shape",
        type="rectangle",
        x=panel_x,
        y=panel_y,
        width=panel_width,
        height=panel_height,
        fill=panel_color,
        line_color="none",
    )

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_width,
        height=title_layout["height"],
        font="Arial",
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(10.0, title_layout["font_size"] - 2.0),
        color=title_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.04,
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
        font="Arial",
        font_path=str(subtitle_font_path),
        size=subtitle_layout["font_size"],
        min_font_size=max(9.0, subtitle_layout["font_size"] - 2.0),
        italic="true",
        color=subtitle_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(subtitle_layout["lines"]),
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
        label_layout["source_text"],
        x=meta_x,
        y=meta_y,
        width=meta_width,
        height=label_layout["height"],
        font="Arial",
        font_path=str(meta_font_path),
        size=label_layout["font_size"],
        min_font_size=max(9.0, label_layout["font_size"] - 1.0),
        color=meta_label_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(label_layout["lines"]),
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
        name_layout["source_text"],
        x=meta_x,
        y=meta_y + label_layout["height"] + 10.0,
        width=meta_width,
        height=name_layout["height"],
        font="Arial",
        font_path=str(meta_bold_font_path),
        size=name_layout["font_size"],
        min_font_size=max(9.0, name_layout["font_size"] - 1.0),
        bold="true",
        color=meta_name_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(name_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.0,
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

def generate_elegant_fancy_font_cover_slide_xml(
    title: str = "Messi cầu thủ vĩ đại nhất thế giới túc cầu hiện tịa",
    subtitle: str = "Beauty Products Pitch Deck Beauty Products Pitch Deck Beauty Products Pitch Deck Beauty Products Pitch Deck",
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1612817288484-6f916006741a"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#D7D8C8",
    title_color: str = "#3F3627",
    subtitle_color: str = "#3F3627",
) -> str:
    """
    Generate XML for a minimalist beauty pitch deck cover slide.

    The layout features a wide hero image near the top, a very large
    elegant serif title underneath, and a smaller subtitle aligned to
    the same left edge. Text uses adaptive sizing and width so longer
    content stays balanced without overlapping the image or subtitle.
    """



    canvas_width = 1600
    canvas_height = 900

    image_x = 88.0
    image_y = 50.0
    image_width = 1408.0
    image_height = 500.0

    text_x = 90.0
    text_box_width = 1400.0
    title_y = 592.0
    title_max_height = 140.0
    subtitle_gap = 18.0
    subtitle_max_height = 90.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

    def font_directories() -> list[Path]:
        dirs: list[Path] = []
        windir = os.environ.get("WINDIR")
        if windir:
            dirs.append(Path(windir) / "Fonts")
        dirs.extend([
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path.home() / "Library/Fonts",
            Path("/Library/Fonts"),
        ])
        return [d for d in dirs if d.exists()]

    def resolve_font_path(font_name: str, bold: bool = False, italic: bool = False) -> Path:
        aliases = {
            "Arial": ["arial"],
            "Helvetica": ["helvetica", "arial"],
            "Times New Roman": ["timesnewroman", "times"],
            "Arial": ["arial", "timesnewroman", "times"],
            "Garamond": ["garamond", "timesnewroman", "times"],
            "Didot": ["didot", "timesnewroman", "times"],
            "Bodoni": ["bodoni", "timesnewroman", "times"],
        }
        names = [normalize_font_name(n) for n in aliases.get(font_name, [font_name])]
        candidates: list[tuple[int, Path]] = []
        for d in font_directories():
            try:
                files = d.rglob("*")
            except OSError:
                continue
            for p in files:
                if p.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue
                stem = normalize_font_name(p.stem)
                if not any(n in stem for n in names):
                    continue
                score = 70
                if stem in names:
                    score += 30
                has_bold = any(t in stem for t in ("bold", "bd", "semibold"))
                has_italic = any(t in stem for t in ("italic", "oblique", "it"))
                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 10
                elif has_bold:
                    score -= 6
                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 4
                candidates.append((score, p))
        candidates.sort(key=lambda x: x[0], reverse=True)
        for _, p in candidates:
            try:
                ImageFont.truetype(str(p), 12)
                return p
            except OSError:
                pass

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        wf = windir / "Fonts"
        fallback_paths = [
            wf / "times.ttf",
            wf / "arial.ttf",
            wf / "arial.ttf",
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        for p in fallback_paths:
            if p.exists():
                try:
                    ImageFont.truetype(str(p), 12)
                    return p
                except OSError:
                    pass
        for d in font_directories():
            try:
                for p in d.rglob("*"):
                    if p.suffix.lower() in {".ttf", ".otf", ".ttc"}:
                        try:
                            ImageFont.truetype(str(p), 12)
                            return p
                        except OSError:
                            pass
            except OSError:
                continue
        return _resolve_font_fallback_path(bold=bold, italic=italic)

    canvas_dpi = 120.0

    def pt_to_canvas(size: float) -> float:
        return size * canvas_dpi / 72.0

    def load_font(font_path: Path, size: float):
        return ImageFont.truetype(str(font_path), max(1, round(pt_to_canvas(size))))

    def text_width(text: str, font_path: Path, size: float) -> float:
        font = load_font(font_path, size)
        if hasattr(font, "getlength"):
            return float(font.getlength(text))
        l, _, r, _ = font.getbbox(text)
        return float(r - l)

    def line_height(font_path: Path, size: float, spacing: float) -> float:
        font = load_font(font_path, size)
        a, d = font.getmetrics()
        return float(a + d) * spacing

    def wrap_text(text: str, font_path: Path, size: float, max_width: float) -> list[str]:
        lines: list[str] = []
        for para in text.splitlines() or [text]:
            words = para.split()
            if not words:
                lines.append("")
                continue
            cur = ""
            for word in words:
                candidate = word if not cur else f"{cur} {word}"
                if not cur or text_width(candidate, font_path, size) <= max_width:
                    cur = candidate
                else:
                    lines.append(cur)
                    cur = word
            if cur:
                lines.append(cur)
        return lines or [""]

    def layout_text(text: str, font_path: Path, size: float, max_width: float, spacing: float) -> dict:
        lines = wrap_text(text, font_path, size, max_width)
        return {
            "source_text": text,
            "lines": lines,
            "font_size": size,
            "width": max_width,
            "height": len(lines) * line_height(font_path, size, spacing) + 2.0,
        }

    def fit_text(text: str, font_path: Path, preferred: float, minimum: float, max_width: float, max_height: float, spacing: float) -> dict:
        best = None
        size = preferred
        while size >= minimum:
            layout = layout_text(text, font_path, size, max_width, spacing)
            score = max(0, layout["height"] - max_height) * 1000 + (preferred - size) * 8 + len(layout["lines"]) * 18
            if best is None or score < best["score"]:
                layout["score"] = score
                best = layout
            if layout["height"] <= max_height:
                return layout
            size -= 0.5
        return best

    title_font_name = "Arial"
    subtitle_font_name = "Arial"
    title_font_path = resolve_font_path(title_font_name, bold=True)
    subtitle_font_path = resolve_font_path(subtitle_font_name, italic=True)

    title_layout = fit_text(
        title,
        title_font_path,
        preferred=48.0,
        minimum=26.0,
        max_width=text_box_width,
        max_height=title_max_height,
        spacing=0.86,
    )

    dynamic_gap = 14.0 if title_layout["height"] > 108.0 else subtitle_gap
    subtitle_y = title_y + title_layout["height"] + dynamic_gap
    subtitle_layout = fit_text(
        subtitle,
        subtitle_font_path,
        preferred=18.0,
        minimum=18.0,
        max_width=min(1200.0, text_box_width),
        max_height=subtitle_max_height,
        spacing=1.0,
    )

    if subtitle_y + subtitle_layout["height"] > 860.0:
        overflow = subtitle_y + subtitle_layout["height"] - 860.0
        title_y = max(592.0, title_y - overflow)
        subtitle_y = title_y + title_layout["height"] + dynamic_gap

    presentation = ET.Element("presentation", {
        "schemaVersion": "1.0",
        "width": str(canvas_width),
        "height": str(canvas_height),
        "slideWidthInches": "13.333",
        "slideHeightInches": "7.5",
    })
    slide = ET.SubElement(presentation, "slide", {"background": background_color})

    def add(tag: str, **attrs):
        return ET.SubElement(slide, tag, {k: str(v) for k, v in attrs.items() if v is not None})

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    add("image", src=image_url, x=image_x, y=image_y, width=image_width, height=image_height)

    textbox(
        title_layout["source_text"],
        x=text_x,
        y=title_y,
        width=title_layout["width"],
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(10.0, title_layout["font_size"] - 2.0),
        bold="true",
        color=title_color,
        align="left",
        vertical_align="middle",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.86,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        subtitle_layout["source_text"],
        x=text_x,
        y=subtitle_y,
        width=subtitle_layout["width"],
        height=subtitle_layout["height"],
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=subtitle_layout["font_size"],
        min_font_size=max(10.0, subtitle_layout["font_size"] - 2.0),
        italic="true",
        color=subtitle_color,
        align="left",
        vertical_align="middle",
        single_line="false",
        max_lines=len(subtitle_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.0,
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

def generate_intro_welcome_slide_xml(
    title: str = "Welcome to Our Today's Presentation Slide",
    subtitle: str = (
        "Here You Can Add Brief Text to Explain the Topic of Your Presentation\n"
        "This is Just a Demo So Consider Replacing These Texts with Your Own\n"
        "Presentation Content."
    ),
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1497366754035-f200968a6e72"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_overlay_color: str = "#FFFFFF",
    background_overlay_opacity: float = 0.10,
    panel_color: str = "#FFFFFF",
    panel_opacity: float = 0.76,
    accent_color: str = "#EA4B32",
    accent_opacity: float = 0.76,
    company_color: str = "#2D2A2B",
    headline_black_color: str = "#2B2929",
    description_color: str = "#2D2A2B",
) -> str:
    """
    Generate XML for a modern intro welcome slide.

    The layout uses a full-bleed office image background, a translucent white
    rounded panel, a bold orange rounded arrow frame, and only two left-aligned
    text blocks: a title and a subtitle.
    """



    canvas_width = 1600
    canvas_height = 900

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": ["arial"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri"],
            "Aptos": ["aptos"],
            "Arial": ["arial"],
            "Times New Roman": ["timesnewroman", "times"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(name in stem for name in normalized_names):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue
            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    canvas_dpi = 120.0

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
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
        def split_long_word(word: str) -> list[str]:
            chunks: list[str] = []
            current_chunk = ""
            for character in word:
                candidate = current_chunk + character
                if (
                    current_chunk
                    and measure_text_width(candidate, font_path, font_size_pt)
                    > max_width
                ):
                    chunks.append(current_chunk)
                    current_chunk = character
                else:
                    current_chunk = candidate
            if current_chunk:
                chunks.append(current_chunk)
            return chunks or [word]

        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current = ""

            for word in words:
                if measure_text_width(word, font_path, font_size_pt) > max_width:
                    if current:
                        lines.append(current)
                        current = ""
                    word_chunks = split_long_word(word)
                    lines.extend(word_chunks[:-1])
                    current = word_chunks[-1]
                    continue

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
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        max_width: float,
        line_spacing: float,
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
            "lines": lines,
            "font_size": font_size,
            "width": max_width,
            "height": len(lines) * line_height,
        }

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best = None

        while current_font_size >= min_font_size:
            layout = layout_text(
                text,
                font_path=font_path,
                font_size=current_font_size,
                max_width=max_width,
                line_spacing=line_spacing,
            )

            too_many_lines = (
                max_lines is not None
                and len(layout["lines"]) > max_lines
            )

            score = (
                max(0.0, layout["height"] - max_height) * 1700
                + max(0, len(layout["lines"]) - (max_lines or 99)) * 1100
                + (preferred_font_size - current_font_size) * 8
            )

            if best is None or score < best["score"]:
                layout["score"] = score
                best = layout

            if layout["height"] <= max_height and not too_many_lines:
                return layout

            break

        return best

    font_name = "Arial"
    font_path_regular = resolve_font_path(font_name, bold=False)
    font_path_bold = resolve_font_path(font_name, bold=True)

    title_box_width = 1100.0
    subtitle_box_width = 1180.0
    text_x = 78.0
    text_content_top = 286.0
    # Leave a small reserve for the converter's textbox safety expansion.
    text_content_bottom = 636.0
    text_content_height = text_content_bottom - text_content_top
    title_subtitle_gap = 30.0

    def build_text_layouts(scale: float) -> tuple[dict, dict]:
        title_layout = fit_text(
                title.strip(),
                font_path=font_path_bold,
                preferred_font_size=max(20.0, 54.0 * scale),
                min_font_size=22.0,
                max_width=title_box_width,
                max_height=150.0,
                line_spacing=0.95,
                max_lines=2,
            )
        subtitle_layout = fit_text(
                subtitle.strip(),
                font_path=font_path_regular,
                preferred_font_size=max(10.0, 20.0 * scale),
                min_font_size=10.0,
                max_width=subtitle_box_width,
                max_height=170.0,
                line_spacing=1.08,
                max_lines=5,
            )
        return title_layout, subtitle_layout

    # Scale the whole text stack only when its content cannot fit. This keeps
    # the requested hierarchy while guaranteeing that the blocks stay inside
    # the panel and do not collide with one another.
    text_scale = 1.0
    title_layout, subtitle_layout = build_text_layouts(text_scale)
    for _ in range(50):
        stack_height = (
            title_layout["height"]
            + title_subtitle_gap
            + subtitle_layout["height"]
        )
        if stack_height <= text_content_height:
            break
        text_scale = max(0.38, text_scale - 0.02)
        title_layout, subtitle_layout = build_text_layouts(text_scale)

    stack_height = (
        title_layout["height"]
        + title_subtitle_gap
        + subtitle_layout["height"]
    )
    stack_y = text_content_top + max(
        0.0,
        (text_content_height - stack_height) / 2.0,
    )
    title_y = stack_y
    subtitle_y = title_y + title_layout["height"] + title_subtitle_gap

    frame_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <filter id="softWhite" x="-5%" y="-10%" width="115%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="7" flood-color="#ffffff" flood-opacity="0.35"/>
    </filter>
  </defs>

  <rect x="0" y="0" width="1600" height="900" fill="{background_overlay_color}" opacity="{background_overlay_opacity:g}"/>

  <path
    d="
      M 0 220
      L 1100 220
      C 1180 220 1236 252 1288 326
      L 1364 435
      L 1288 544
      C 1236 618 1180 650 1100 650
      L 0 650
      Z
    "
    fill="{panel_color}"
    opacity="{panel_opacity:g}"
    filter="url(#softWhite)"
  />

  <path
    d="
      M -60 188
      L 1112 188
      C 1215 188 1276 232 1345 334
      L 1420 444
      L 1345 554
      C 1276 656 1215 698 1112 698
      L -60 698
    "
    fill="none"
    stroke="{accent_color}"
    stroke-width="70"
    stroke-linecap="square"
    stroke-linejoin="round"
    opacity="{accent_opacity:g}"
  />

  <path
    d="
      M -60 188
      L 1112 188
      C 1215 188 1276 232 1345 334
      L 1420 444
      L 1345 554
      C 1276 656 1215 698 1112 698
      L -60 698
    "
    fill="none"
    stroke="{accent_color}"
    stroke-width="30"
    stroke-linecap="square"
    stroke-linejoin="round"
    opacity="0.32"
  />
</svg>
""".strip()

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
        {"background": "#FFFFFF"},
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
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fit="cover",
        crop_x=0.55,
        crop_y=0.50,
    )

    frame_node = add(
        "svg",
        name="orange_arrow_panel",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=3200,
        pixel_height=1800,
    )
    frame_node.text = frame_svg

    textbox(
        title_layout["source_text"],
        x=text_x,
        y=title_y,
        width=title_box_width,
        height=title_layout["height"],
        font=font_name,
        font_path=str(font_path_bold),
        size=title_layout["font_size"],
        min_font_size=22.0,
        bold="true",
        color=headline_black_color,
        align="left",
        vertical_align="middle",
        single_line="false",
        max_lines=2,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.95,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    textbox(
        subtitle_layout["source_text"],
        x=text_x,
        y=subtitle_y,
        width=subtitle_box_width,
        height=subtitle_layout["height"],
        font=font_name,
        font_path=str(font_path_regular),
        size=subtitle_layout["font_size"],
        min_font_size=10.0,
        bold="false",
        color=description_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=5,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.08,
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

def generate_memorial_cover_slide_xml(
    title: str = "Welcome to Our Presentation on Memorial Day 2024 Celebration and Remembrance",
    subtitle: str = "A clear and engaging introduction to today's topic     with a focus on honoring and remembering those who have served.",
    image_url: str = (
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=85&w=1600&h=900&auto=format&fit=crop"
    ),
    background_color: str = "#F3F3F3",
    top_band_color: str = "#DECAC7",
    title_band_color: str = "#DECAC7",
    subtitle_color: str = "#111111",
    title_color: str = "#050505",
    stripe_blue_color: str = "#E7EEF1",
    stripe_pink_color: str = "#DECAC7",
    stripe_white_color: str = "#F8F8F8",
    image_overlay_color: str = "#FFFFFF",
) -> str:
    """
    Generate XML for an intro-style cover slide.

    The layout uses a full-bleed monochrome landscape photo, a narrow subtitle
    band, a large centered title band, and decorative vertical stripes.
    """


    # LLM/tool calls can occasionally omit optional text values or send them
    # as empty strings. Keep the XML generator total: an empty value should
    # produce a usable slide instead of failing during font measurement.
    title = str(title or "").strip()
    subtitle = str(subtitle or "").strip()
    image_url = str(image_url or "").strip() or (
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"
        "?q=85&w=1600&h=900&auto=format&fit=crop"
    )

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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
        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Times New Roman": [
                "timesnewroman",
                "times",
                "arial",
                "freeserif",
                "liberationserif",
                "dejavuserif",
            ],
            "Arial": [
                "arial",
                "timesnewroman",
                "times",
                "freeserif",
                "liberationserif",
                "dejavuserif",
            ],
            "Arial": [
                "arial",
                "calibri",
                "aptos",
                "freesans",
                "liberationsans",
                "dejavusans",
            ],
        }

        normalized_names = [
            normalize_font_name(item)
            for item in aliases.get(font_name, [font_name])
        ]

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
                if not any(name in stem for name in normalized_names):
                    continue

                score = 80 if any(name == stem for name in normalized_names) else 58

                has_bold = any(token in stem for token in ("bold", "bd", "semibold", "demi"))
                has_italic = any(token in stem for token in ("italic", "oblique", "it"))

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 6

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 4

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        if bold and italic:
            fallbacks = [
                windows_fonts / "timesbi.ttf",
                windows_fonts / "arialbi.ttf",
                windows_fonts / "arialbi.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"),
                Path("/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf"),
                Path("/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf"),
            ]
        elif italic:
            fallbacks = [
                windows_fonts / "timesi.ttf",
                windows_fonts / "ariali.ttf",
                windows_fonts / "ariali.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"),
                Path("/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"),
                Path("/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf"),
            ]
        elif bold:
            fallbacks = [
                windows_fonts / "timesbd.ttf",
                windows_fonts / "arialbd.ttf",
                windows_fonts / "arialbd.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
                Path("/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"),
                Path("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
            ]
        else:
            fallbacks = [
                windows_fonts / "times.ttf",
                windows_fonts / "arial.ttf",
                windows_fonts / "arial.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
                Path("/usr/share/fonts/truetype/freefont/FreeSerif.ttf"),
                Path("/usr/share/fonts/truetype/freefont/FreeSans.ttf"),
            ]

        for path in fallbacks:
            if not path.exists():
                continue
            try:
                ImageFont.truetype(str(path), 12)
                return path
            except OSError:
                continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(font_path), max(1, round(pt_to_canvas(font_size_pt))))

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
        font = load_font(font_path, font_size_pt)
        if hasattr(font, "getlength"):
            return float(font.getlength(text))
        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(font_path: Path, font_size_pt: float, line_spacing: float) -> float:
        font = load_font(font_path, font_size_pt)
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

    def wrap_text(text: str, font_path: Path, font_size_pt: float, max_width: float) -> list[str]:
        def split_long_word(word: str) -> list[str]:
            chunks: list[str] = []
            current_chunk = ""
            for character in word:
                candidate = current_chunk + character
                if (
                    current_chunk
                    and measure_text_width(candidate, font_path, font_size_pt) > max_width
                ):
                    chunks.append(current_chunk)
                    current_chunk = character
                else:
                    current_chunk = candidate
            if current_chunk:
                chunks.append(current_chunk)
            return chunks or [word]

        lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current = ""
            for word in words:
                if measure_text_width(word, font_path, font_size_pt) > max_width:
                    if current:
                        lines.append(current)
                        current = ""
                    chunks = split_long_word(word)
                    lines.extend(chunks[:-1])
                    current = chunks[-1]
                    continue

                candidate = word if not current else f"{current} {word}"
                if not current or measure_text_width(candidate, font_path, font_size_pt) <= max_width:
                    current = candidate
                else:
                    lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best_layout = None

        while current_font_size >= min_font_size:
            lines = wrap_text(text, font_path, current_font_size, max_width)
            line_height = measure_line_height(font_path, current_font_size, line_spacing)
            height = len(lines) * line_height

            too_many_lines = max_lines is not None and len(lines) > max_lines
            overflow_height = max(0.0, height - max_height)
            score = overflow_height * 2000 + max(0, len(lines) - (max_lines or 999)) * 1500 + (preferred_font_size - current_font_size) * 10

            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_font_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many_lines:
                return layout

            break

        return best_layout

    subtitle_font_name = "Arial"
    title_font_name = "Times New Roman"

    subtitle_font_path = resolve_font_path(subtitle_font_name, bold=False, italic=False)
    title_font_path = resolve_font_path(title_font_name, bold=False, italic=True)

    subtitle_layout = fit_text(
        subtitle.strip(),
        font_path=subtitle_font_path,
        preferred_font_size=18.0,
        min_font_size=10.0,
        max_width=820.0,
        max_height=150.0,
        line_spacing=1.0,
        max_lines=4,
    )

    title_layout = fit_text(
        title.strip(),
        font_path=title_font_path,
        preferred_font_size=58.0,
        min_font_size=18.0,
        max_width=1400.0,
        max_height=260.0,
        line_spacing=0.95,
        max_lines=4,
    )

    def measured_layout_width(layout: dict, font_path: Path) -> float:
        return max(
            [
                measure_text_width(line, font_path, layout["font_size"])
                for line in layout["lines"]
            ]
            or [0.0]
        )

    # Expand the background bands around the text first. Text keeps its
    # requested size; overflow is handled by the textbox renderer.
    subtitle_content_width = measured_layout_width(subtitle_layout, subtitle_font_path)
    subtitle_band_width = min(
        900.0,
        max(876.0, subtitle_content_width + 72.0),
    )
    subtitle_band_height = min(
        180.0,
        max(56.0, subtitle_layout["height"] + 24.0),
    )
    subtitle_band_x = (canvas_width - subtitle_band_width) / 2.0
    subtitle_band_y = 204.0 - subtitle_band_height / 2.0

    title_content_width = measured_layout_width(title_layout, title_font_path)
    title_box_width = min(
        1460.0,
        max(1230.0, title_content_width + 80.0),
    )
    title_band_height = min(
        280.0,
        max(126.0, title_layout["height"] + 36.0),
    )
    title_band_y = 442.0 - title_band_height / 2.0
    title_box_x = (canvas_width - title_box_width) / 2.0
    title_box_y = title_band_y + (title_band_height - title_layout["height"]) / 2.0

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

    slide = ET.SubElement(presentation, "slide", {"background": background_color})

    def add(tag: str, **attrs):
        return ET.SubElement(slide, tag, {k: str(v) for k, v in attrs.items() if v is not None})

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    add(
        "image",
        src=image_url,
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fit="cover",
        crop_x=0.50,
        crop_y=0.48,
    )

    add(
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=image_overlay_color,
        opacity=0.15,
        line_color="none",
    )

    add(
        "shape",
        type="rect",
        x=subtitle_band_x,
        y=subtitle_band_y,
        width=subtitle_band_width,
        height=subtitle_band_height,
        fill=top_band_color,
        opacity=0.96,
        line_color="none",
    )
    add(
        "shape",
        type="rect",
        x=0,
        y=title_band_y,
        width=canvas_width,
        height=title_band_height,
        fill=title_band_color,
        opacity=0.96,
        line_color="none",
    )
    stripe_width = 32
    stripe_height = 56
    stripe_gap = 18
    stripe_sequence = [
        stripe_blue_color,
        stripe_white_color,
        stripe_pink_color,
        stripe_white_color,
        stripe_blue_color,
        stripe_white_color,
        stripe_pink_color,
    ]

    def add_stripe_group(start_x: float, top_y: float) -> None:
        current_x = start_x
        for color in stripe_sequence:
            add(
                "shape",
                type="rect",
                x=current_x,
                y=top_y,
                width=stripe_width,
                height=stripe_height,
                fill=color,
                opacity=0.98,
                line_color="none",
            )
            current_x += stripe_width + stripe_gap

    stripe_group_width = len(stripe_sequence) * stripe_width + (len(stripe_sequence) - 1) * stripe_gap
    stripe_clearance = 18.0
    enough_room_for_stripes = (
        subtitle_band_width + 2.0 * (stripe_group_width + stripe_clearance)
        <= canvas_width
    )
    if enough_room_for_stripes:
        left_stripe_x = subtitle_band_x - stripe_group_width - stripe_clearance
        right_stripe_x = subtitle_band_x + subtitle_band_width + stripe_clearance
        stripe_y = subtitle_band_y + (subtitle_band_height - stripe_height) / 2.0
        add_stripe_group(left_stripe_x, stripe_y)
        add_stripe_group(right_stripe_x, stripe_y)
    # The intro layout uses only the top subtitle band and centered title.

    textbox(
        subtitle_layout["source_text"],
        x=subtitle_band_x + 28.0,
        y=subtitle_band_y + 8.0,
        width=subtitle_band_width - 56.0,
        height=subtitle_band_height - 16.0,
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=subtitle_layout["font_size"],
        min_font_size=10.0,
        color=subtitle_color,
        align="center",
        vertical_align="middle",
        bold="false",
        italic="false",
        single_line="false",
        overflow="clip",
        reflow_on_resize="true",
        max_lines=4,
        line_spacing=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    textbox(
        title_layout["source_text"],
        x=title_box_x,
        y=title_box_y,
        width=title_box_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=18.0,
        color=title_color,
        align="center",
        vertical_align="middle",
        bold="false",
        italic="true",
        single_line="false",
        overflow="clip",
        reflow_on_resize="true",
        max_lines=4,
        line_spacing=0.95,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

    return xml_content

def generate_social_topic_idea_slide_xml(
    title: str = "Write Your Topic or Write Your Topic or Idea On Write Your Topic or Idea On Social Media",
    subtitle: str = "Elaborate on what you want to discuss. Elaborate on what you want to discuss.",
    image_url: str = (
        "https://images.unsplash.com/photo-1551836022-d5d88e9218df?q=85&w=1200&auto=format&fit=crop"
    ),
    background_color: str = "#FFFFFF",
    accent_color: str = "#6F8369",
    title_color: str = "#26352A",
    subtitle_color: str = "#111111",
    line_color: str = "#3F3F3F",
) -> str:
    """
    Generate XML for a clean social media topic slide.

    The layout has a white text area on the left and a full-height portrait
    image on the right. The title is one editable string. A thin horizontal
    line and short subtitle sit near the lower-left.
    """


 

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(
            ch.lower()
            for ch in name
            if ch.isalnum()
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
        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": ["arial", "helvetica"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri", "aptos", "arial"],
            "Aptos": ["aptos", "calibri", "arial"],
            "Arial": ["arial", "times"],
            "Times New Roman": ["timesnewroman", "times", "arial"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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
                if not any(name in stem for name in normalized_names):
                    continue

                score = 70
                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if fallback_path.exists():
                try:
                    ImageFont.truetype(str(fallback_path), 12)
                    return fallback_path
                except OSError:
                    continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        if not text:
            return 0.0
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
        lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current = ""
            for word in words:
                candidate = word if not current else f"{current} {word}"
                if not current or measure_text_width(candidate, font_path, font_size_pt) <= max_width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)
        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_size = preferred_font_size
        best_layout = None

        while current_size >= min_font_size:
            lines = wrap_text(text, font_path, current_size, max_width)
            line_height = measure_line_height(font_path, current_size, line_spacing)
            height = len(lines) * line_height
            too_many_lines = max_lines is not None and len(lines) > max_lines
            overflow = max(0.0, height - max_height)

            score = (
                overflow * 1700
                + max(0, len(lines) - (max_lines or 999)) * 1200
                + (preferred_font_size - current_size) * 8
            )
            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many_lines:
                return layout

            break

        return best_layout

    title_font_name = "Arial"
    title_font_path = resolve_font_path(title_font_name, bold=True, italic=False)
    title_layout = fit_text(
        title,
        font_path=title_font_path,
        preferred_font_size=48.0,
        min_font_size=22.0,
        max_width=740.0,
        max_height=310.0,
        line_spacing=0.98,
        max_lines=4,
    )

    subtitle_font_path = resolve_font_path("Arial", bold=False)
    subtitle_layout = fit_text(
        subtitle.strip() or "Elaborate on what you want to discuss.",
        font_path=subtitle_font_path,
        preferred_font_size=18.0,
        min_font_size=11.0,
        max_width=680.0,
        max_height=76.0,
        line_spacing=1.1,
        max_lines=2,
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
    slide = ET.SubElement(presentation, "slide", {"background": background_color})

    def add(tag: str, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {key: str(value) for key, value in attrs.items() if value is not None},
        )

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    # Right image area.
    add(
        "image",
        src=image_url,
        x=888,
        y=0,
        width=712,
        height=900,
        fit="cover",
        crop_x=0.52,
        crop_y=0.46,
    )

    # One editable title string on the left, with a restrained accent marker.
    title_x = 72.0
    title_width = 740.0
    title_y = 164.0 + max(
        0.0,
        (310.0 - title_layout["height"]) / 2.0,
    )

    add(
        "shape",
        type="rect",
        x=26.0,
        y=title_y + 8.0,
        width=6.0,
        height=max(48.0, title_layout["height"] - 16.0),
        fill=accent_color,
        line_color="none",
    )

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=22.0,
        color=title_color,
        align="left",
        vertical_align="middle",
        bold="true",
        italic="false",
        single_line="false",
        max_lines=4,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.98,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    # Lower line and subtitle. The line is separate and comes before text.
    add(
        "line",
        x1=28,
        y1=650,
        x2=154,
        y2=650,
        color=line_color,
        width=1.2,
    )

    textbox(
        subtitle_layout["source_text"],
        x=182,
        y=650 - subtitle_layout["height"] / 2,
        width=subtitle_layout["width"],
        height=subtitle_layout["height"],
        font="Arial",
        font_path=str(subtitle_font_path),
        size=subtitle_layout["font_size"],
        min_font_size=11.0,
        color=subtitle_color,
        align="left",
        vertical_align="middle",
        bold="false",
        italic="false",
        single_line="false",
        max_lines=len(subtitle_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.1,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content

def generate_roman_empire_history_cover_slide_xml(
    subtitle: str = "History Subject for High School History Subject for High School History Subject for High School",
    title: str = "ROMAN EMPIRE ROMAN EMPIRE ROMAN EMPIRE",
    image_url: str = (
        "https://picsum.photos/seed/roman-empire-history/1600/620.jpg"
    ),
    background_color: str = "#D8B98A",
    parchment_overlay_color: str = "#C49A61",
    image_sepia_overlay_color: str = "#B07132",
    torn_paper_color: str = "#F3E9D7",
    torn_shadow_color: str = "#B89A72",
    subtitle_color: str = "#5A1E20",
    title_color: str = "#4A1118",
    blood_color: str = "#9E1018",
) -> str:
    """
    Generate XML for a Roman Empire history cover slide.

    The layout uses a wide image area on top, a torn-paper frame overlay
    across the lower part of the image, decorative parchment texture, red
    splatter accents, a script-style subtitle, and a large serif title.
    """

    clean_subtitle = str(subtitle or "").strip()
    clean_title = str(title or "").strip()

    clean_image_url = image_url.strip()
    if not clean_image_url:
        clean_image_url = "https://picsum.photos/seed/roman-empire-history/1600/620.jpg"

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(character.lower() for character in name if character.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Times New Roman": ["timesnewroman", "times", "arial"],
            "Arial": ["arial", "timesnewroman", "times"],
            "Garamond": ["garamond", "arial", "timesnewroman", "times"],
            "Arial": ["arial", "calibri", "aptos"],
            "Calibri": ["calibri", "arial", "aptos"],
        }

        normalized_names = [
            normalize_font_name(item)
            for item in aliases.get(font_name, [font_name])
        ]

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

                if not any(name in stem for name in normalized_names):
                    continue

                score = 80 if any(name == stem for name in normalized_names) else 58

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 6

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 4

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "timesbi.ttf",
                windows_fonts / "arialbi.ttf",
                windows_fonts / "arialbi.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "timesi.ttf",
                windows_fonts / "ariali.ttf",
                windows_fonts / "ariali.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "timesbd.ttf",
                windows_fonts / "arialbd.ttf",
                windows_fonts / "arialbd.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "times.ttf",
                windows_fonts / "arial.ttf",
                windows_fonts / "arial.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue
            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
        if not text:
            return 0.0

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
        def split_long_word(word: str) -> list[str]:
            chunks: list[str] = []
            current_chunk = ""

            for character in word:
                candidate = current_chunk + character
                if (
                    current_chunk
                    and measure_text_width(candidate, font_path, font_size_pt)
                    > max_width
                ):
                    chunks.append(current_chunk)
                    current_chunk = character
                else:
                    current_chunk = candidate

            return chunks + [current_chunk] if current_chunk else chunks or [word]

        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
                continue

            current = ""

            for word in words:
                if measure_text_width(word, font_path, font_size_pt) > max_width:
                    if current:
                        lines.append(current)
                        current = ""

                    chunks = split_long_word(word)
                    lines.extend(chunks[:-1])
                    current = chunks[-1]
                    continue

                candidate = word if not current else f"{current} {word}"

                if (
                    not current
                    or measure_text_width(candidate, font_path, font_size_pt)
                    <= max_width
                ):
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_size: float,
        min_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_size = preferred_size
        best_layout = None

        while current_size >= min_size:
            lines = wrap_text(text, font_path, current_size, max_width)
            line_height = measure_line_height(font_path, current_size, line_spacing)
            height = len(lines) * line_height
            too_many = max_lines is not None and len(lines) > max_lines
            overflow = max(0.0, height - max_height)

            score = (
                overflow * 2000
                + max(0, len(lines) - (max_lines or 999)) * 1500
                + (preferred_size - current_size) * 8
            )

            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many:
                return layout

            break

        return best_layout

    title_font_name = "Garamond"
    subtitle_font_name = "Times New Roman"

    title_font_path = resolve_font_path(title_font_name, bold=False, italic=False)
    subtitle_font_path = resolve_font_path(subtitle_font_name, bold=False, italic=True)

    # Responsive lower text group. The boxes are intentionally wider and may
    # use two lines. Font reduction is the final fallback after the group has
    # used the available vertical space and the title/subtitle gap.
    subtitle_x = 130.0
    subtitle_width = 1340.0
    title_x = 60.0
    title_width = 1480.0
    text_group_top = 604.0
    text_group_bottom = 866.0
    subtitle_title_gap = 18.0

    subtitle_size = 20.0
    title_size = 62.0
    subtitle_min_size = 14.0
    title_min_size = 24.0

    for _ in range(120):
        subtitle_layout = fit_text(
            clean_subtitle,
            font_path=subtitle_font_path,
            preferred_size=subtitle_size,
            min_size=subtitle_min_size,
            max_width=subtitle_width,
            max_height=104.0,
            line_spacing=0.95,
            max_lines=2,
        )

        title_layout = fit_text(
            clean_title.upper(),
            font_path=title_font_path,
            preferred_size=title_size,
            min_size=title_min_size,
            max_width=title_width,
            max_height=184.0,
            line_spacing=0.92,
            max_lines=2,
        )

        # Keep the next iteration aware of any reduction needed to fit a
        # textbox's own width/line constraints.
        subtitle_size = min(subtitle_size, float(subtitle_layout["font_size"]))
        title_size = min(title_size, float(title_layout["font_size"]))

        group_height = (
            float(subtitle_layout["height"])
            + subtitle_title_gap
            + float(title_layout["height"])
        )
        available_group_height = text_group_bottom - text_group_top

        if group_height <= available_group_height:
            break

        # Keep the requested font sizes. Overflow is handled by the renderer.
        break

    group_height = (
        float(subtitle_layout["height"])
        + subtitle_title_gap
        + float(title_layout["height"])
    )
    group_y = text_group_top + max(
        0.0,
        (text_group_bottom - text_group_top - group_height) / 2.0,
    )
    subtitle_y = group_y
    title_y = subtitle_y + float(subtitle_layout["height"]) + subtitle_title_gap

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

    slide = ET.SubElement(presentation, "slide", {"background": background_color})

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

    # Base parchment color.
    add(
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    texture_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <filter id="paperNoise">
      <feTurbulence type="fractalNoise" baseFrequency="0.012 0.018" numOctaves="4" seed="13"/>
      <feColorMatrix type="matrix"
        values="0.46 0 0 0 0.48
                0 0.36 0 0 0.36
                0 0 0.24 0 0.20
                0 0 0 0.20 0"/>
    </filter>
    <radialGradient id="oldPaper" cx="50%" cy="50%" r="74%">
      <stop offset="0%" stop-color="#F1D5AA" stop-opacity="0.20"/>
      <stop offset="68%" stop-color="{parchment_overlay_color}" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#6B3C1C" stop-opacity="0.20"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="1600" height="900" filter="url(#paperNoise)" opacity="0.62"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#oldPaper)"/>
  <circle cx="90" cy="100" r="150" fill="#A85E2E" opacity="0.08"/>
  <circle cx="1420" cy="120" r="180" fill="#8A4E28" opacity="0.08"/>
  <circle cx="310" cy="710" r="210" fill="#5A2E19" opacity="0.06"/>
</svg>
""".strip()

    texture_node = add(
        "svg",
        name="parchment_texture",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=3200,
        pixel_height=1800,
    )
    texture_node.text = texture_svg

    # Top image area. The torn paper overlay below creates the image frame.
    add(
        "image",
        src=clean_image_url,
        x=0,
        y=0,
        width=canvas_width,
        height=620,
        fit="cover",
        crop_x=0.50,
        crop_y=0.43,
    )

    add(
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=620,
        fill=image_sepia_overlay_color,
        opacity=0.22,
        line_color="none",
    )

    # Torn-paper frame. This is the key frame effect: it overlays the image
    # with an irregular edge while leaving the upper image visible.
    torn_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="420" viewBox="0 0 1600 420">
  <defs>
    <filter id="tornShadow" x="-10%" y="-20%" width="120%" height="150%">
      <feDropShadow dx="0" dy="-9" stdDeviation="8" flood-color="{torn_shadow_color}" flood-opacity="0.28"/>
    </filter>
    <filter id="fiber">
      <feTurbulence type="fractalNoise" baseFrequency="0.055" numOctaves="3" seed="22"/>
      <feColorMatrix type="saturate" values="0"/>
      <feComponentTransfer>
        <feFuncA type="table" tableValues="0 0.10"/>
      </feComponentTransfer>
    </filter>
  </defs>

  <path d="
      M -10 116
      C 34 109, 73 122, 119 112
      C 169 100, 207 127, 258 120
      C 303 114, 337 98, 383 108
      C 437 121, 485 129, 531 113
      C 581 96, 628 117, 672 112
      C 730 106, 764 127, 811 119
      C 858 111, 905 98, 957 113
      C 1004 126, 1057 111, 1108 121
      C 1169 134, 1219 102, 1270 114
      C 1327 127, 1380 122, 1434 111
      C 1492 99, 1539 119, 1610 106
      L 1610 430
      L -10 430
      Z"
    fill="{torn_paper_color}"
    filter="url(#tornShadow)"/>

  <path d="
      M -10 116
      C 34 109, 73 122, 119 112
      C 169 100, 207 127, 258 120
      C 303 114, 337 98, 383 108
      C 437 121, 485 129, 531 113
      C 581 96, 628 117, 672 112
      C 730 106, 764 127, 811 119
      C 858 111, 905 98, 957 113
      C 1004 126, 1057 111, 1108 121
      C 1169 134, 1219 102, 1270 114
      C 1327 127, 1380 122, 1434 111
      C 1492 99, 1539 119, 1610 106"
    fill="none"
    stroke="#FFFFFF"
    stroke-width="14"
    opacity="0.82"/>

  <rect x="-10" y="98" width="1620" height="330" fill="{torn_paper_color}" filter="url(#fiber)" opacity="0.72"/>
</svg>
""".strip()

    torn_node = add(
        "svg",
        name="torn_paper_frame",
        x=0,
        y=472,
        width=canvas_width,
        height=428,
        pixel_width=3200,
        pixel_height=856,
    )
    torn_node.text = torn_svg

    splatter_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <g fill="{blood_color}" opacity="0.86">
    <ellipse cx="24" cy="680" rx="13" ry="34" transform="rotate(42 24 680)"/>
    <ellipse cx="68" cy="724" rx="9" ry="30" transform="rotate(49 68 724)"/>
    <circle cx="7" cy="614" r="7"/>
    <circle cx="36" cy="633" r="5"/>
    <circle cx="85" cy="657" r="8"/>
    <path d="M 0 860 C 28 828, 55 842, 78 872 C 51 877, 22 875, 0 900 Z"/>
    <ellipse cx="1440" cy="736" rx="8" ry="28" transform="rotate(38 1440 736)"/>
    <ellipse cx="1490" cy="792" rx="10" ry="38" transform="rotate(55 1490 792)"/>
    <ellipse cx="1545" cy="824" rx="12" ry="42" transform="rotate(63 1545 824)"/>
    <circle cx="1513" cy="728" r="5"/>
    <circle cx="1572" cy="741" r="8"/>
    <circle cx="1430" cy="804" r="7"/>
  </g>
</svg>
""".strip()

    splatter_node = add(
        "svg",
        name="red_splatter_accents",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=3200,
        pixel_height=1800,
    )
    splatter_node.text = splatter_svg

    # Refined Roman frame and restrained ornamental accents. These sit above
    # the image and parchment layers, but stay outside the main text blocks.
    ornament_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <g fill="none" stroke="{torn_shadow_color}" stroke-linecap="round" stroke-linejoin="round">
    <rect x="24" y="24" width="1552" height="852" rx="6" stroke-width="3" opacity="0.58"/>
    <rect x="37" y="37" width="1526" height="826" rx="4" stroke-width="1.4" opacity="0.55"/>

    <path d="M 38 108 L 38 58 L 88 58" stroke-width="3" opacity="0.72"/>
    <path d="M 1562 108 L 1562 58 L 1512 58" stroke-width="3" opacity="0.72"/>
    <path d="M 38 792 L 38 842 L 88 842" stroke-width="3" opacity="0.72"/>
    <path d="M 1562 792 L 1562 842 L 1512 842" stroke-width="3" opacity="0.72"/>

    <line x1="235" y1="735" x2="485" y2="735" stroke-width="2" opacity="0.68"/>
    <line x1="1115" y1="735" x2="1365" y2="735" stroke-width="2" opacity="0.68"/>
  </g>

  <g fill="{title_color}" opacity="0.72">
    <polygon points="800,725 811,735 800,745 789,735"/>
    <circle cx="800" cy="735" r="3" fill="{torn_paper_color}"/>
  </g>

  <g fill="none" stroke="{title_color}" stroke-width="2.4" stroke-linecap="round" opacity="0.52">
    <path d="M 292 701 C 260 685, 238 668, 220 646"/>
    <path d="M 1308 701 C 1340 685, 1362 668, 1380 646"/>
  </g>

  <g fill="{title_color}" opacity="0.52">
    <ellipse cx="254" cy="679" rx="9" ry="4" transform="rotate(28 254 679)"/>
    <ellipse cx="241" cy="665" rx="9" ry="4" transform="rotate(18 241 665)"/>
    <ellipse cx="231" cy="650" rx="9" ry="4" transform="rotate(8 231 650)"/>
    <ellipse cx="1346" cy="679" rx="9" ry="4" transform="rotate(-28 1346 679)"/>
    <ellipse cx="1359" cy="665" rx="9" ry="4" transform="rotate(-18 1359 665)"/>
    <ellipse cx="1369" cy="650" rx="9" ry="4" transform="rotate(-8 1369 650)"/>
  </g>
</svg>
""".strip()

    ornament_node = add(
        "svg",
        name="roman_ornamental_frame",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=3200,
        pixel_height=1800,
    )
    ornament_node.text = ornament_svg

    textbox(
        subtitle_layout["source_text"],
        x=subtitle_x,
        y=subtitle_y,
        width=subtitle_width,
        height=subtitle_layout["height"],
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=subtitle_layout["font_size"],
        min_font_size=max(12.0, subtitle_layout["font_size"] - 1.0),
        color=subtitle_color,
        align="center",
        vertical_align="middle",
        bold="false",
        italic="true",
        single_line="false",
        max_lines=len(subtitle_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.95,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(20.0, title_layout["font_size"] - 1.0),
        color=title_color,
        align="center",
        vertical_align="middle",
        bold="false",
        italic="false",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.92,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    xml_content = minidom.parseString(raw_xml).toprettyxml(
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

        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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

    subtitle_font_size = 18.0
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

        elif AUTO_SHRINK_TEXT and subtitle_font_size > subtitle_min_font_size:
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

def generate_about_us_transition_slide_xml(
    title: str = "Messi vô địch thế giới",
    background_base_color: str = "#CED0C0",
    center_glow_color: str = "#9E8C70",
    inner_glow_color: str = "#B1A180",
    outer_glow_color: str = "#D9D8CC",
    title_color: str = "#3B3227",
) -> str:
    """
    Generate XML for a minimalist transition slide.

    The layout features a muted sage background with a soft warm radial
    glow in the center and one large centered serif title.
    """



    canvas_width = 1600
    canvas_height = 900

    title_center_x = canvas_width / 2
    title_center_y = 448.0
    title_max_width = 920.0
    title_max_height = 145.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Times New Roman": ["timesnewroman", "times"],
            "Arial": ["arial"],
            "Garamond": ["garamond"],
            "Arial": ["arial"],
            "Calibri": ["calibri"],
            "Aptos": ["aptos"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(normalized in stem for normalized in normalized_names):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 8

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        explicit_fallbacks = [
            windows_fonts / "times.ttf",
            windows_fonts / "timesnewroman.ttf",
            windows_fonts / "arial.ttf",
            windows_fonts / "garamond.ttf",
            windows_fonts / "arial.ttf",
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]

        for fallback_path in explicit_fallbacks:
            if not fallback_path.exists():
                continue

            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

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

    def tracked_title(text: str) -> str:
        cleaned = " ".join(text.strip().split())

        if len(cleaned) <= 2:
            return cleaned.upper()

        words = cleaned.upper().split()
        tracked_words = [" ".join(list(word)) for word in words]

        return "   ".join(tracked_words)

    def wrap_text(
        text: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        words = text.split()

        if not words:
            return [""]

        lines: list[str] = []
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"

            if (
                not current
                or measure_text_width(candidate, font_path, font_size_pt)
                <= max_width
            ):
                current = candidate
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        max_width: float,
        line_spacing: float,
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
            "lines": lines,
            "font_size": font_size,
            "height": len(lines) * line_height,
        }

    title_font_name = "Times New Roman"
    title_font_path = resolve_font_path(title_font_name)

    # Keep normal word spacing so the title wraps naturally instead of
    # separating every character and forcing one word onto each line.
    display_title = " ".join(title.strip().split())

    title_font_size = 58.0
    title_min_font_size = 28.0
    title_line_spacing = 1.0

    title_layout = layout_text(
        display_title,
        font_path=title_font_path,
        font_size=title_font_size,
        max_width=title_max_width,
        line_spacing=title_line_spacing,
    )

    for _ in range(140 if AUTO_SHRINK_TEXT else 0):
        if (
            title_layout["height"] <= title_max_height
            and len(title_layout["lines"]) <= 2
        ):
            break

        if title_font_size <= title_min_font_size:
            break

        title_font_size = max(
            title_min_font_size,
            title_font_size - 0.5,
        )

        title_layout = layout_text(
            display_title,
            font_path=title_font_path,
            font_size=title_font_size,
            max_width=title_max_width,
            line_spacing=title_line_spacing,
        )

    title_y = title_center_y - title_layout["height"] / 2
    title_x = title_center_x - title_max_width / 2

    background_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <radialGradient id="mainGlow" cx="50%" cy="47%" r="57%">
      <stop offset="0%" stop-color="{center_glow_color}" stop-opacity="0.78"/>
      <stop offset="24%" stop-color="{inner_glow_color}" stop-opacity="0.62"/>
      <stop offset="53%" stop-color="{outer_glow_color}" stop-opacity="0.52"/>
      <stop offset="100%" stop-color="{background_base_color}" stop-opacity="1"/>
    </radialGradient>
    <radialGradient id="topSoft" cx="50%" cy="0%" r="56%">
      <stop offset="0%" stop-color="#EFEDE2" stop-opacity="0.26"/>
      <stop offset="100%" stop-color="#EFEDE2" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="bottomWarm" cx="50%" cy="95%" r="65%">
      <stop offset="0%" stop-color="#A49778" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#A49778" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="1600" height="900" fill="{background_base_color}"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#mainGlow)"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#topSoft)"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#bottomWarm)"/>
</svg>
""".strip()

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
        {"background": background_base_color},
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
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=1600,
        pixel_height=900,
    )
    svg_node.text = background_svg

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_max_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(24.0, title_layout["font_size"] - 2.0),
        color=title_color,
        align="center",
        vertical_align="middle",
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

def generate_gallery_transition_slide_xml(
    title: str = "Messi vs Ronaldo - The Ultimate Showdown of Football Legends",
    image_url_1: str = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=85&w=1200&auto=format&fit=crop",
    image_url_2: str = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=85&w=1200&auto=format&fit=crop",
    image_url_3: str = "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=85&w=1200&auto=format&fit=crop",
    image_url_4: str = "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?q=85&w=1200&auto=format&fit=crop",
    image_url_5: str = "https://images.unsplash.com/photo-1517841905240-472988babdf9?q=85&w=1200&auto=format&fit=crop",
    image_url_6: str = "https://images.unsplash.com/photo-1512316609839-ce289d3eba0a?q=85&w=1200&auto=format&fit=crop",
    background_color: str = "#CDD0C1",
    title_color: str = "#3B3024",
) -> str:
    """
    Generate XML for a gallery transition slide.

    The layout features a soft neutral background, three landscape images
    across the top, three landscape images across the bottom, and one large
    centered serif title placed in the open middle area.
    """


    gallery_fallback_image = (
        "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"
        "?auto=compress&cs=tinysrgb&w=1600"
    )
    image_url_1 = str(image_url_1 or "").strip() or gallery_fallback_image
    image_url_2 = str(image_url_2 or "").strip() or gallery_fallback_image
    image_url_3 = str(image_url_3 or "").strip() or gallery_fallback_image
    image_url_4 = str(image_url_4 or "").strip() or gallery_fallback_image
    image_url_5 = str(image_url_5 or "").strip() or gallery_fallback_image
    image_url_6 = str(image_url_6 or "").strip() or gallery_fallback_image

    def image_url_by_number(number: int) -> str:
        if number == 1:
            return image_url_1
        if number == 2:
            return image_url_2
        if number == 3:
            return image_url_3
        if number == 4:
            return image_url_4
        if number == 5:
            return image_url_5
        if number == 6:
            return image_url_6
        return gallery_fallback_image

    canvas_width = 1600
    canvas_height = 900

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Times New Roman": ["timesnewroman", "times"],
            "Arial": ["arial"],
            "Garamond": ["garamond"],
            "Arial": ["arial"],
            "Calibri": ["calibri"],
            "Aptos": ["aptos"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(normalized in stem for normalized in normalized_names):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        fallback_paths = [
            windows_fonts / "times.ttf",
            windows_fonts / "arial.ttf",
            windows_fonts / "arial.ttf",
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue

            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

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
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
                continue

            current = ""

            for word in words:
                candidate = word if not current else f"{current} {word}"

                if (
                    not current
                    or measure_text_width(candidate, font_path, font_size_pt)
                    <= max_width
                ):
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

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
            "lines": lines,
            "font_size": font_size,
            "width": max_width,
            "height": len(lines) * line_height + padding,
        }

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        padding: float = 2.0,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best = None

        while current_font_size >= min_font_size:
            layout = layout_text(
                text,
                font_path=font_path,
                font_size=current_font_size,
                max_width=max_width,
                line_spacing=line_spacing,
                padding=padding,
            )

            too_many_lines = (
                max_lines is not None
                and len(layout["lines"]) > max_lines
            )

            score = (
                max(0.0, layout["height"] - max_height) * 1400
                + max(0, len(layout["lines"]) - (max_lines or 99)) * 900
                + (preferred_font_size - current_font_size) * 8
            )

            if best is None or score < best["score"]:
                layout["score"] = score
                best = layout

            if layout["height"] <= max_height and not too_many_lines:
                return layout

            break

        return best

    title_font_name = "Arial"
    title_font_path = resolve_font_path(title_font_name, bold=True)

    title_layout = fit_text(
        title.strip().upper(),
        font_path=title_font_path,
        preferred_font_size=58.0,
        min_font_size=40.0,
        max_width=1500.0,
        max_height=130.0,
        line_spacing=0.95,
        padding=1.0,
        max_lines=2,
    )

    left_margin = 8.0
    right_margin = 8.0
    column_gap = 40.0
    image_width = (canvas_width - left_margin - right_margin - 2 * column_gap) / 3
    image_height = 230.0

    top_row_y = 78.0
    bottom_row_y = 566.0

    image_x_positions = [
        left_margin,
        left_margin + image_width + column_gap,
        left_margin + 2 * (image_width + column_gap),
    ]

    title_x = canvas_width / 2 - 1500.0 / 2
    title_center_y = (
        top_row_y
        + image_height
        + (bottom_row_y - (top_row_y + image_height)) / 2
    )
    title_y = title_center_y - title_layout["height"] / 2

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

    background_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <radialGradient id="topRight" cx="100%" cy="0%" r="30%">
      <stop offset="0%" stop-color="#B6B39D" stop-opacity="0.62"/>
      <stop offset="55%" stop-color="#B6B39D" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="#B6B39D" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="bottomLeft" cx="0%" cy="100%" r="34%">
      <stop offset="0%" stop-color="#B6B39D" stop-opacity="0.46"/>
      <stop offset="55%" stop-color="#B6B39D" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#B6B39D" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="1600" height="900" fill="{background_color}"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#topRight)"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#bottomLeft)"/>
</svg>
""".strip()

    svg_node = add(
        "svg",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=1600,
        pixel_height=900,
    )
    svg_node.text = background_svg

    for index in range(3):
        add(
            "image",
            src=image_url_by_number(index + 1),
            x=image_x_positions[index],
            y=top_row_y,
            width=image_width,
            height=image_height,
            fit="cover",
        )

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=1500.0,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(40.0, title_layout["font_size"] - 2.0),
        bold="true",
        color=title_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.95,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    for index in range(3):
        add(
            "image",
            src=image_url_by_number(index + 4),
            x=image_x_positions[index],
            y=bottom_row_y,
            width=image_width,
            height=image_height,
            fit="cover",
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

def generate_slide_transition_slide_xml(
    title: str = "Social Media Sales Presentation Social Media Sales Presentation",
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1519085360753-af0119f7cbe7"
        "?q=85&w=1200&auto=format&fit=crop"
    ),
    right_image_url: str = (
        "https://images.unsplash.com/"
        "photo-1497366754035-f200968a6e72"
        "?q=85&w=1200&auto=format&fit=crop"
    ),
    background_color: str = "#FFFFFF",
    right_panel_color: str = "#6D8767",
    arc_color: str = "#819A7B",
    title_color: str = "#FFFFFF",
    line_color: str = "#2F3530",
) -> str:
    """
    Generate XML for a modern split cover slide.

    The layout places a portrait photo on the left with a thin horizontal
    divider line, and a green image-backed panel on the right with a large
    translucent arc decoration and one editable title string.
    """

    # Keep title as one plain string; do not introduce explicit line breaks.
    title = " ".join(title.split()) or "Social Media Sales Presentation"

    if not image_url.strip():
        image_url = (
            "https://images.unsplash.com/"
            "photo-1519085360753-af0119f7cbe7"
            "?q=85&w=1200&auto=format&fit=crop"
        )

    if not right_image_url.strip():
        right_image_url = (
            "https://images.unsplash.com/"
            "photo-1497366754035-f200968a6e72"
            "?q=85&w=1200&auto=format&fit=crop"
        )

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(
            ch.lower()
            for ch in name
            if ch.isalnum()
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
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": ["arial", "helvetica"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri", "aptos", "arial"],
            "Aptos": ["aptos", "calibri", "arial"],
            "Arial": ["arial", "times"],
            "Times New Roman": ["timesnewroman", "times", "arial"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(
                    normalized in stem
                    for normalized in normalized_names
                ):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(
                key=lambda item: item[0],
                reverse=True,
            )

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue

            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

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
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current = ""

            for word in words:
                candidate = word if not current else f"{current} {word}"
                if (
                    not current
                    or measure_text_width(candidate, font_path, font_size_pt) <= max_width
                ):
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best_layout = None

        while current_font_size >= min_font_size:
            lines = wrap_text(text, font_path, current_font_size, max_width)
            line_height = measure_line_height(font_path, current_font_size, line_spacing)
            height = len(lines) * line_height
            too_many_lines = max_lines is not None and len(lines) > max_lines
            overflow_height = max(0.0, height - max_height)

            score = (
                overflow_height * 1800
                + max(0, len(lines) - (max_lines or 999)) * 1300
                + (preferred_font_size - current_font_size) * 8
            )

            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_font_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many_lines:
                return layout

            break

        return best_layout

    font_name = "Arial"

    # Measure the complete title as one editable textbox. The string remains
    # a single value; the textbox may wrap naturally at the requested size.
    title_max_width = 620.0
    title_area_height = 310.0
    preferred_title_size = 58.0
    min_title_size = 24.0
    title_font_path = resolve_font_path(font_name, bold=False, italic=False)
    title_layout = fit_text(
        title,
        font_path=title_font_path,
        preferred_font_size=preferred_title_size,
        min_font_size=min_title_size,
        max_width=title_max_width,
        max_height=title_area_height,
        line_spacing=0.96,
        max_lines=4,
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
            {key: str(value) for key, value in attrs.items() if value is not None},
        )

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    # Left white area.
    add(
        "shape",
        type="rect",
        x=0,
        y=0,
        width=684,
        height=900,
        fill=background_color,
        line_color="none",
    )

    # Right background image + green overlay.
    add(
        "image",
        src=right_image_url,
        x=684,
        y=0,
        width=916,
        height=900,
        fit="cover",
        crop_x=0.52,
        crop_y=0.48,
    )

    add(
        "shape",
        type="rect",
        x=684,
        y=0,
        width=916,
        height=900,
        fill=right_panel_color,
        line_color="none",
        opacity=0.88,
    )

    # Large curved arc on right side.
    arc_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="916" height="900" viewBox="0 0 916 900">
  <path d="M 636 -150
           C 288 26 220 336 353 575
           C 477 799 700 873 926 918
           L 926 900
           C 628 813 493 666 431 522
           C 330 288 438 70 746 -102
           Z"
        fill="{arc_color}" opacity="{0.38:g}"/>
</svg>
"""

    arc_node = add(
        "svg",
        name="right_large_arc",
        x=684,
        y=0,
        width=916,
        height=900,
        pixel_width=1832,
        pixel_height=1800,
    )
    arc_node.text = arc_svg

    # Horizontal line first so it sits behind the portrait image.
    add(
        "line",
        x1=0,
        y1=452,
        x2=758,
        y2=452,
        color=line_color,
        width=1.2,
    )

    # Left portrait image on top of the line.
    add(
        "image",
        src=image_url,
        x=118,
        y=128,
        width=430,
        height=652,
        fit="cover",
        crop_x=0.50,
        crop_y=0.45,
    )

    # Single editable title on the right panel.
    title_x = 818.0
    title_y = 292.0 + (title_area_height - title_layout["height"]) / 2

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_max_width,
        height=title_layout["height"],
        font=font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=min_title_size,
        color=title_color,
        align="left",
        vertical_align="middle",
        bold="false",
        italic="false",
        single_line="false",
        max_lines=4,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.96,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content

def generate_green_social_media_transition_slide_xml(
    title: str = "Write Your Topic or Idea On Social Media",
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1516321318423-f06f85e504b3"
        "?q=85&w=1200&auto=format&fit=crop"
    ),
    background_color: str = "#6F8369",
    right_overlay_color: str = "#6F8369",
    right_overlay_opacity: float = 0.58,
    title_color: str = "#FFFFFF",
    line_color: str = "#D8E0D3",
) -> str:
    """
    Generate XML for a green social media transition slide.

    The layout uses a solid muted-green left panel, a tinted full-height image
    on the right, a short horizontal divider line, and one editable title
    string.
    """

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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
        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(font_name: str, bold: bool = False, italic: bool = False) -> Path:
        aliases = {
            "Arial": ["arial", "helvetica"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri", "aptos", "arial"],
            "Aptos": ["aptos", "calibri", "arial"],
            "Arial": ["arial", "times"],
            "Times New Roman": ["timesnewroman", "times", "arial"],
        }

        normalized_names = [normalize_font_name(name) for name in aliases.get(font_name, [font_name])]
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
                if not any(name in stem for name in normalized_names):
                    continue

                score = 70
                if stem in normalized_names:
                    score += 30

                has_bold = any(token in stem for token in ("bold", "bd", "semibold", "demi"))
                has_italic = any(token in stem for token in ("italic", "oblique", "it"))

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if fallback_path.exists():
                try:
                    ImageFont.truetype(str(fallback_path), 12)
                    return fallback_path
                except OSError:
                    continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(font_path), max(1, round(pt_to_canvas(font_size_pt))))

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
        font = load_font(font_path, font_size_pt)
        if hasattr(font, "getlength"):
            return float(font.getlength(text))
        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(font_path: Path, font_size_pt: float, line_spacing: float) -> float:
        font = load_font(font_path, font_size_pt)
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

    def wrap_text(text: str, font_path: Path, font_size_pt: float, max_width: float) -> list[str]:
        words = text.split()
        if not words:
            return [""]

        lines: list[str] = []
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"
            if not current or measure_text_width(candidate, font_path, font_size_pt) <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines or [""]

    def fit_line(
        text: str,
        *,
        font_path: Path,
        preferred_size: float,
        min_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int = 2,
    ) -> dict:
        current_size = preferred_size
        best_layout = None

        while current_size >= min_size:
            lines = wrap_text(text, font_path, current_size, max_width)
            line_height = measure_line_height(font_path, current_size, line_spacing)
            height = len(lines) * line_height

            overflow = max(0.0, height - max_height)
            too_many = len(lines) > max_lines

            score = (
                overflow * 1800
                + max(0, len(lines) - max_lines) * 1300
                + (preferred_size - current_size) * 8
            )

            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many:
                return layout

            break

        return best_layout

    font_name = "Arial"
    max_title_width = 760.0
    max_title_height = 330.0
    preferred_title_size = 43.0
    min_title_size = 22.0
    title_line_gap = 12.0

    title_font_path = resolve_font_path(font_name, bold=True, italic=False)
    title_layout = fit_line(
        title,
        font_path=title_font_path,
        preferred_size=preferred_title_size,
        min_size=min_title_size,
        max_width=max_title_width,
        max_height=max_title_height,
        line_spacing=0.96,
        max_lines=4,
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
            {key: str(value) for key, value in attrs.items() if value is not None},
        )

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    # Solid green background.
    add(
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    # Right image region.
    right_x = 1065.0
    right_w = canvas_width - right_x

    add(
        "image",
        src=image_url,
        x=right_x,
        y=0,
        width=right_w,
        height=canvas_height,
        fit="cover",
        crop_x=0.50,
        crop_y=0.45,
    )

    overlay_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{right_w:g}" height="{canvas_height:g}" viewBox="0 0 {right_w:g} {canvas_height:g}">
  <rect x="0" y="0" width="{right_w:g}" height="{canvas_height:g}" fill="{right_overlay_color}" opacity="{right_overlay_opacity:g}"/>
</svg>
""".strip()

    overlay_node = add(
        "svg",
        name="right_green_overlay",
        x=right_x,
        y=0,
        width=right_w,
        height=canvas_height,
        pixel_width=round(right_w * 2),
        pixel_height=canvas_height * 2,
    )
    overlay_node.text = overlay_svg

    # Short divider line on the left.
    add(
        "line",
        x1=0,
        y1=455,
        x2=158,
        y2=455,
        color=line_color,
        width=1.2,
    )

    # One editable title string.
    title_x = 198.0
    title_y = 300.0 + (max_title_height - title_layout["height"]) / 2.0

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=max_title_width,
        height=title_layout["height"],
        font=font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=min_title_size,
        color=title_color,
        align="left",
        vertical_align="middle",
        bold="true",
        italic="false",
        single_line="false",
        max_lines=4,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.96,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content

def generate_section_header_image_slide_xml(
    section_header: str = "Add a Section Header Here and a Subtitle if Needed or Leave Blank",
    image_url: str = (
        "https://images.unsplash.com/photo-1556761175-b413da4baf72?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#FFFFFF",
    header_color: str = "#6F8369",
    title_color: str = "#FFFFFF",
    divider_color: str = "#C9D4C3",
) -> str:
    """
    Generate XML for a section-header transition slide.

    The layout has a muted green header panel across the top, a short centered
    vertical divider line, a large centered section title, and a full-width
    image cropped into the lower half of the slide.
    """

    clean_header = section_header.strip()
   


    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": ["arial", "helvetica"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri", "aptos", "arial"],
            "Aptos": ["aptos", "calibri", "arial"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(name in stem for name in normalized_names):
                    continue

                score = 70
                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if fallback_path.exists():
                try:
                    ImageFont.truetype(str(fallback_path), 12)
                    return fallback_path
                except OSError:
                    continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

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
        if not text:
            return 0.0

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
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
                continue

            current = ""

            for word in words:
                candidate = word if not current else f"{current} {word}"

                if (
                    not current
                    or measure_text_width(candidate, font_path, font_size_pt)
                    <= max_width
                ):
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_size: float,
        min_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
    ) -> dict:
        current_size = preferred_size
        best_layout = None

        while current_size >= min_size:
            lines = wrap_text(text, font_path, current_size, max_width)
            line_height = measure_line_height(font_path, current_size, line_spacing)
            height = len(lines) * line_height
            overflow = max(0.0, height - max_height)

            score = overflow * 1800 + (preferred_size - current_size) * 8

            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height:
                return layout

            break

        return best_layout

    font_name = "Arial"
    title_font_path = resolve_font_path(font_name, bold=True)

    header_height = 438.0
    image_y = header_height
    image_height = canvas_height - image_y

    title_layout = fit_text(
        clean_header,
        font_path=title_font_path,
        preferred_size=44.0,
        min_size=18.0,
        max_width=1000.0,
        max_height=230.0,
        line_spacing=1.0,
    )

    title_x = 300.0
    title_y = 158.0 + (170.0 - title_layout["height"]) / 2

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
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=header_height,
        fill=header_color,
        line_color="none",
    )

    add(
        "line",
        x1=canvas_width / 2,
        y1=0,
        x2=canvas_width / 2,
        y2=108,
        color=divider_color,
        width=1.0,
        opacity=0.82,
    )

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=1000.0,
        height=title_layout["height"],
        font=font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(16.0, title_layout["font_size"] - 2.0),
        color=title_color,
        align="center",
        vertical_align="middle",
        bold="true",
        italic="false",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    add(
        "image",
        src=image_url,
        x=0,
        y=image_y,
        width=canvas_width,
        height=image_height,
        fit="cover",
        crop_x=0.50,
        crop_y=0.46,
    )

    raw_xml = ET.tostring(presentation, encoding="utf-8")

    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content


# Slide content

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
            "Arial": "arial",
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

        fallback_stem = (
            "FreeSansBoldOblique.ttf"
            if bold and italic
            else "FreeSansBold.ttf"
            if bold
            else "FreeSansOblique.ttf"
            if italic
            else "FreeSans.ttf"
        )
        liberation_stem = (
            "LiberationSans-BoldItalic.ttf"
            if bold and italic
            else "LiberationSans-Bold.ttf"
            if bold
            else "LiberationSans-Italic.ttf"
            if italic
            else "LiberationSans-Regular.ttf"
        )
        fallback_paths = [
            Path("/usr/share/fonts/truetype/dejavu") / fallback_name,
            Path("/usr/share/fonts/truetype/freefont") / fallback_stem,
            Path("/usr/share/fonts/truetype/liberation") / liberation_stem,
            Path("/usr/local/share/fonts") / fallback_name,
            Path.cwd() / fallback_name,
        ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue
            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        font_path = None
        return Path(_resolve_font_fallback_path(bold=bold))

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

    title_font_size = 56.0
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
        bullet_text = ""

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

        elif AUTO_SHRINK_TEXT and body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and title_font_size > title_min_font_size:
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
    idea_titles: list[str] | None = None,
    idea_descriptions: list[str] | None = None,
    image_url: str = "",
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

    if idea_titles is None:
        idea_titles = ["VENUS", "MERCURY"]
    if idea_descriptions is None:
        idea_descriptions = [
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
        ]

    if len(idea_titles) != 2 or len(idea_descriptions) != 2:
        raise ValueError(
            "generate_two_ideas_slide_xml requires exactly two idea titles "
            "and two idea descriptions."
        )

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

        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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

    title_font_size = 48.0
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

        elif AUTO_SHRINK_TEXT and body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and heading_font_size > heading_min_font_size:
            heading_font_size = max(
                heading_min_font_size,
                heading_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and title_font_size > title_min_font_size:
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
    idea_titles: list[str] | None = None,
    idea_descriptions: list[str] | None = None,
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

    if idea_titles is None:
        idea_titles = ["MERCURY", "MARS", "VENUS"]
    if idea_descriptions is None:
        idea_descriptions = [
            (
                "Mercury is the closest planet to the Sun and the "
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
        ]

    if len(idea_titles) != 3 or len(idea_descriptions) != 3:
        raise ValueError(
            "generate_three_ideas_slide_xml requires exactly three idea "
            "titles and three idea descriptions."
        )


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

        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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

    title_font_size = 52.0
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

        elif AUTO_SHRINK_TEXT and body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and heading_font_size > heading_min_font_size:
            heading_font_size = max(
                heading_min_font_size,
                heading_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and title_font_size > title_min_font_size:
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

        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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

    title_font_size = 46.0
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

    # Keep the columns below the actual title box when a long title wraps.
    # The previous fixed ``columns_top`` could place the first heading inside
    # a multi-line title.
    columns_top = max(
        columns_top,
        title_y + title_layout["height"] + 28.0,
    )

    for _ in range(100 if AUTO_SHRINK_TEXT else 0):
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

        elif AUTO_SHRINK_TEXT and body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and heading_font_size > heading_min_font_size:
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

    # The footer must follow the tallest column.  A fixed footer_y caused the
    # long body text to render underneath the footer, which made the two text
    # blocks overlap visually.
    columns_bottom = max(
        columns_top + left_layout["total_height"],
        columns_top + right_layout["total_height"],
    )
    footer_y = max(
        footer_y,
        columns_bottom + 28.0,
    )

    footer_layout = layout_text(
        footer_text,
        font_path=body_font_path,
        font_size=footer_font_size,
        max_width=footer_width,
        line_spacing=footer_line_spacing,
        padding=4,
    )

    for _ in range(80 if AUTO_SHRINK_TEXT else 0):
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
    column_titles: list[str] | None = None,
    column_descriptions: list[str] | None = None,
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

    if column_titles is None:
        column_titles = ["White", "Black"]
    if column_descriptions is None:
        column_descriptions = [
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
        ]

    if len(column_titles) != 2 or len(column_descriptions) != 2:
        raise ValueError(
            "generate_split_content_slide_xml requires exactly two column "
            "titles and two column descriptions."
        )

    column_titles = [str(value or "").strip() for value in column_titles]
    column_descriptions = [
        str(value or "").strip()
        for value in column_descriptions
    ]


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

        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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

    title_font_size = 46.0
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

    for _ in range(100 if AUTO_SHRINK_TEXT else 0):
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

        elif AUTO_SHRINK_TEXT and body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and heading_font_size > heading_min_font_size:
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

        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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

    title_font_size = 38.0
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

        elif AUTO_SHRINK_TEXT and body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and title_font_size > title_min_font_size:
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

        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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
                    if current:
                        result.append(current)
                        current = ""

                    chunks: list[str] = []
                    chunk = ""
                    for character in word:
                        candidate = chunk + character
                        if (
                            chunk
                            and measure_text_width(
                                candidate,
                                font_path,
                                font_size_pt,
                            )
                            > max_width
                        ):
                            chunks.append(chunk)
                            chunk = character
                        else:
                            chunk = candidate

                    if chunk:
                        chunks.append(chunk)

                    result.extend(chunks[:-1])
                    current = chunks[-1] if chunks else ""
                    continue

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

    title_font_size = 38.0
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

        # wrap_text() splits long unbroken strings by character, so width
        # safety is handled there. Height still controls the fit decision.
        width_fits = True

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

        elif AUTO_SHRINK_TEXT and body_font_size > body_min_font_size:
            body_font_size = max(
                body_min_font_size,
                body_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and title_font_size > title_min_font_size:
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


    # =====================================================
    # Canvas and layout regions
    # =====================================================

    canvas_width = 1600
    canvas_height = 900

    title_x = 22.0
    title_y = 38.0
    # Keep the title inside the left column, but give it the full usable
    # width.  The old 680px width made otherwise reasonable Vietnamese titles
    # wrap to three lines and pushed every content row downward.
    title_width = 760.0

    subtitle_x = 22.0
    subtitle_width = 760.0

    # The marker is a separate textbox (x=45, width=30). Leave a visible gap
    # before the label instead of starting it inside the marker box.
    content_x = 84.0
    marker_x = 45.0
    content_right = 795.0

    value_gap = 10.0
    subgoal_marker_x = 88.0
    subgoal_text_x = 122.0
    subgoal_width = content_right - subgoal_text_x

    content_bottom = 840.0

    title_to_subtitle_gap = 28.0
    subtitle_to_content_gap = 96.0
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

        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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

    title_font_size = 60.0
    title_min_font_size = 46.0

    subtitle_font_size = 20.0
    # The previous minimum (22pt) was larger than the starting 20pt size, so
    # the subtitle could never participate in fitting.
    subtitle_min_font_size = 16.0

    body_font_size = 24.0
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
            had_indentation = len(raw_detail) != len(stripped_detail)

            is_subitem = (
                had_indentation
                or stripped_detail.startswith(("- ", "• ", "◦ "))
            )

            # This renderer owns the list marker, so remove numbering supplied
            # by the document/model from the label (e.g. "1. Formula:").
            stripped_detail = re.sub(
                r"^\d+(?:\.\d+)*[.)]\s+",
                "",
                stripped_detail,
            )

            if is_subitem:
                for prefix in ("- ", "• ", "◦ "):
                    if stripped_detail.startswith(prefix):
                        stripped_detail = stripped_detail[
                            len(prefix):
                        ].strip()
                        break
                # Also handle inputs such as "• 1. Formula".
                stripped_detail = re.sub(
                    r"^\d+(?:\.\d+)*[.)]\s+",
                    "",
                    stripped_detail,
                )

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

            # Reserve a usable value column even when a model supplies an
            # unusually long label.  Let the label wrap inside this cap rather
            # than consuming the entire row and collapsing the value textbox.
            max_label_width = max(
                120.0,
                content_right - content_x - value_gap - 280.0,
            )
            raw_label_width = (
                single_line_width(
                    label,
                    body_bold_font_path,
                    current_body_size,
                )
                + 12.0
                if label
                else 0.0
            )
            label_width = min(raw_label_width, max_label_width)

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

        # This layout has a dense, variable-length detail list.  Let it
        # perform its own bounded fit even when the global auto-shrink switch
        # is disabled for other XML tools.
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
                single_line="false",
                max_lines=len(item["label"]["lines"]),
                overflow="clip",
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

    raw_timeline_items = (
        timeline_items
        if isinstance(timeline_items, (list, tuple))
        else [timeline_items]
    )
    normalized_timeline_items: list[dict[str, str]] = []
    for index, raw_item in enumerate(raw_timeline_items):
        item = raw_item if isinstance(raw_item, dict) else {}
        normalized_timeline_items.append(
            {
                "label": str(item.get("label") or "").strip(),
                "content": str(item.get("content") or "").strip(),
            }
        )
    timeline_items = normalized_timeline_items or [
        {"label": "", "content": ""}
    ]


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

        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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

    title_font_size = 46.0
    title_min_font_size = 36.0

    subtitle_font_size = 18.0
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

    for _ in range(80 if AUTO_SHRINK_TEXT else 0):
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

    for _ in range(80 if AUTO_SHRINK_TEXT else 0):
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

        if AUTO_SHRINK_TEXT and content_font_size > content_min_font_size:
            content_font_size = max(
                content_min_font_size,
                content_font_size - 0.5,
            )
            changed = True

        elif AUTO_SHRINK_TEXT and label_font_size > label_min_font_size:
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

    raw_problem_items = (
        problem_items
        if isinstance(problem_items, (list, tuple))
        else [problem_items]
    )
    problem_items = [
        str(item or "").strip()
        for item in raw_problem_items
    ] or [""]
    card_colors = list(card_colors or []) or ["#DDF2A6"]
    card_text_colors = list(card_text_colors or []) or ["#07520B"]



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
            "Arial": "arial",
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
        font_path = _resolve_font_fallback_path(bold=bold)

        return Path(_resolve_font_fallback_path(bold=bold))

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
                    break
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

                break

        if best_candidate is None:
            # Extremely defensive fallback.
            fallback_width = max(width_candidates)
            best_candidate = {
                "source_text": text,
                "text": text,
                "lines": [text],
                "font_size": preferred_font_size,
                "height": preferred_max_height,
                "width": fallback_width,
                "score": 10**9,
            }

        return best_candidate

    # =====================================================
    # Typography
    # =====================================================

    title_font_name = "Arial"
    description_font_name = "Arial"
    card_font_name = "Arial"

    title_font_path = resolve_font_path(title_font_name, bold=True)
    description_font_path = resolve_font_path(
        description_font_name,
        bold=False,
    )
    card_font_path = resolve_font_path(card_font_name, bold=False)

    title_color = title_color
    description_color = description_color

    title_font_size = 46.0
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
            overflow="clip",
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
        overflow="clip",
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

def generate_topics_overview_slide_xml(
    title: str = "Messi là cầu thủ vĩ đại nhất thế giới",
    topics: list[dict[str, str]] = [
        {
            "title": "ADD A MAIN POINT",
            "description": "Briefly elaborate on what you want to discuss.",
        },
        {
            "title": "Mesi là cầu thủ vĩ đại nhấtthế giới",
            "description": "Briefly elaborate on what you want to discuss.",
        },
        
        {
            "title": "ADD A MAIN POINT",
            "description": "Briefly elaborate on what you want to discuss.",
        },
    ],
    image_url_1: str = "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?q=85&w=1200&auto=format&fit=crop",
    image_url_2: str = "https://images.unsplash.com/photo-1556228720-195a672e8a03?q=85&w=1200&auto=format&fit=crop",
    image_url_3: str = "https://images.unsplash.com/photo-1596462502278-27bfdc403348?q=85&w=1200&auto=format&fit=crop",
    background_color: str = "#CDD0C1",
    title_color: str = "#3A3126",
    item_title_color: str = "#3A3126",
    item_description_color: str = "#3A3126",
    accent_color: str = "#9AA382",
) -> str:
    """
    Generate XML for a topics overview slide.

    The layout features a muted neutral background with soft corner
    accents, a large serif title near the top-left, and a flexible grid of
    image-backed topic items with centered titles and descriptions.
    """

    fallback_image = (
        "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"
        "?auto=compress&cs=tinysrgb&w=1600"
    )
    raw_topics = topics if isinstance(topics, (list, tuple)) else [topics]
    normalized_topics: list[dict[str, str]] = []
    for raw_topic in raw_topics:
        topic = raw_topic if isinstance(raw_topic, dict) else {}
        normalized_topics.append(
            {
                "title": str(topic.get("title") or "").strip(),
                "description": str(topic.get("description") or "").strip(),
            }
        )
    topics = normalized_topics or [
        {
            "title": "",
            "description": "",
        }
    ]
    image_urls = [
        str(image_url or "").strip() or fallback_image
        for image_url in (image_url_1, image_url_2, image_url_3)
    ]


    canvas_width = 1600
    canvas_height = 900

    # =====================================================
    # Font helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Times New Roman": ["timesnewroman", "times"],
            "Arial": ["arial"],
            "Garamond": ["garamond"],
            "Arial": ["arial"],
            "Calibri": ["calibri"],
            "Aptos": ["aptos"],
            "Helvetica": ["helvetica", "arial"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(
                    normalized in stem
                    for normalized in normalized_names
                ):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in (
                        "bold",
                        "bd",
                        "semibold",
                        "demi",
                    )
                )
                has_italic = any(
                    token in stem
                    for token in (
                        "italic",
                        "oblique",
                        "it",
                    )
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "timesbi.ttf",
                windows_fonts / "arialbi.ttf",
                windows_fonts / "arialbi.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "timesbd.ttf",
                windows_fonts / "arialbd.ttf",
                windows_fonts / "arialbd.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "timesi.ttf",
                windows_fonts / "ariali.ttf",
                windows_fonts / "ariali.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "times.ttf",
                windows_fonts / "arial.ttf",
                windows_fonts / "garamond.ttf",
                windows_fonts / "arial.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue

            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

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

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

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
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
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
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

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
            "height": len(lines) * line_height + padding,
            "width": max_width,
        }

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        padding: float = 2.0,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best = None

        while current_font_size >= min_font_size:
            layout = layout_text(
                text,
                font_path=font_path,
                font_size=current_font_size,
                max_width=max_width,
                line_spacing=line_spacing,
                padding=padding,
            )

            too_many_lines = (
                max_lines is not None
                and len(layout["lines"]) > max_lines
            )

            score = (
                max(0.0, layout["height"] - max_height) * 1200
                + max(0, len(layout["lines"]) - (max_lines or 99)) * 800
                + (preferred_font_size - current_font_size) * 8
            )

            if best is None or score < best["score"]:
                layout["score"] = score
                best = layout

            if layout["height"] <= max_height and not too_many_lines:
                return layout

            current_font_size -= 0.5

        return best

    # =====================================================
    # Dynamic layout
    # =====================================================

    title_font_name = "Arial"
    heading_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(title_font_name, bold=True)
    heading_font_path = resolve_font_path(heading_font_name, bold=True)
    body_font_path = resolve_font_path(body_font_name)

    count = len(topics)

    title_x = 88.0
    title_y = 94.0
    # The title sits above the full-width topic grid.  Limiting it to 700px
    # forced long titles into unnecessary extra lines on the left, where they
    # could overlap the first row of images.
    title_width = canvas_width - title_x - 88.0
    title_max_height = 150.0

    title_layout = fit_text(
        title.upper(),
        font_path=title_font_path,
        preferred_font_size=60.0,
        min_font_size=40.0,
        max_width=title_width,
        max_height=title_max_height,
        line_spacing=0.95,
        padding=2.0,
        max_lines=2,
    )

    if count <= 3:
        columns = count
    else:
        columns = min(3, count)

    rows = (count + columns - 1) // columns

    grid_x = 50.0
    grid_right = 1550.0
    grid_width = grid_right - grid_x

    # Move content up/down depending on title size and item count.
    grid_top = max(
        322.0 if rows == 1 else 272.0,
        title_y + title_layout["height"] + 30.0,
    )
    grid_bottom = 760.0 if rows == 1 else 822.0
    row_gap = 38.0 if rows == 1 else 30.0
    col_gap = 30.0 if columns >= 3 else 48.0

    item_width = (
        grid_width
        - col_gap * (columns - 1)
    ) / columns

    item_height = (
        grid_bottom
        - grid_top
        - row_gap * (rows - 1)
    ) / rows

    image_ratio = 0.58 if rows == 1 else 0.52
    image_height = item_height * image_ratio
    text_gap = 34.0 if rows == 1 else 18.0

    item_title_font = 25.0 if columns <= 3 else 23.0
    item_desc_font = 21.0 if columns <= 3 else 17.0

    title_text_layouts: list[dict] = []
    desc_text_layouts: list[dict] = []

    for topic in topics:
        text_width = item_width * 0.82

        heading_layout = fit_text(
            topic["title"].strip().upper(),
            font_path=heading_font_path,
            preferred_font_size=item_title_font,
            min_font_size=13.0,
            max_width=item_width * 0.98,
            max_height=item_height * 0.20,
            line_spacing=1.0,
            padding=1.0,
            max_lines=1,
        )

        desc_layout = fit_text(
            topic["description"].strip(),
            font_path=body_font_path,
            preferred_font_size=item_desc_font,
            min_font_size=10.0,
            max_width=text_width,
            max_height=item_height * 0.22,
            line_spacing=1.18,
            padding=1.0,
            max_lines=3 if rows == 1 else 2,
        )

        title_text_layouts.append(heading_layout)
        desc_text_layouts.append(desc_layout)

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

    background_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <radialGradient id="topLeft" cx="2%" cy="2%" r="42%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.88"/>
      <stop offset="55%" stop-color="{accent_color}" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="bottomRight" cx="98%" cy="98%" r="42%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.88"/>
      <stop offset="55%" stop-color="{accent_color}" stop-opacity="0.32"/>
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="1600" height="900" fill="{background_color}"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#topLeft)"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#bottomRight)"/>
</svg>
""".strip()

    svg_node = add(
        "svg",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=1600,
        pixel_height=900,
    )
    svg_node.text = background_svg

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(24.0, title_layout["font_size"] - 2.0),
        bold="true",
        color=title_color,
        align="left",
        vertical_align="top",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.95,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    for index, topic in enumerate(topics):
        row = index // columns
        col = index % columns

        item_x = grid_x + col * (item_width + col_gap)
        item_y = grid_top + row * (item_height + row_gap)

        image_x = item_x
        image_y = item_y
        image_width = item_width
        current_image_height = image_height

        text_center_x = item_x + item_width / 2

        add(
            "image",
            src=image_urls[index % len(image_urls)].strip(),
            x=image_x,
            y=image_y,
            width=image_width,
            height=current_image_height,
        )

        heading_layout = title_text_layouts[index]
        desc_layout = desc_text_layouts[index]

        heading_width = heading_layout["width"]
        heading_x = text_center_x - heading_width / 2
        heading_y = image_y + current_image_height + text_gap

        desc_width = desc_layout["width"]
        desc_x = text_center_x - desc_width / 2
        desc_y = heading_y + heading_layout["height"] + 16.0

        textbox(
            heading_layout["source_text"],
            x=heading_x,
            y=heading_y,
            width=heading_width,
            height=heading_layout["height"],
            font=heading_font_name,
            font_path=str(heading_font_path),
            size=heading_layout["font_size"],
            min_font_size=max(11.0, heading_layout["font_size"] - 2.0),
            bold="true",
            color=item_title_color,
            align="center",
            vertical_align="middle",
            single_line="false",
            max_lines=len(heading_layout["lines"]),
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
            desc_layout["source_text"],
            x=desc_x,
            y=desc_y,
            width=desc_width,
            height=desc_layout["height"],
            font=body_font_name,
            font_path=str(body_font_path),
            size=desc_layout["font_size"],
            min_font_size=max(9.0, desc_layout["font_size"] - 2.0),
            color=item_description_color,
            align="center",
            vertical_align="middle",
            single_line="false",
            max_lines=len(desc_layout["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=1.18,
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

def generate_timeline_gallery_slide_xml(
    title: str = "TIMELINE Meeting Agenda Slide Template (Editable) | Free Download | SlideModel",
    timeline_items: list[dict[str, str]] = [
        {
            "title": "ADD A MAIN POINT",
            "description": "Briefly elaborate on what you want to discuss.",
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1517841905240-472988babdf9"
                "?q=85&w=1200&auto=format&fit=crop"
            ),
        },
        {
            "title": "ADD A MAIN POINT Meeting Agenda Slide Template (Editable) | Free Download | SlideModel",
            "description": "Briefly elaborate on what you want to discuss.",
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1496747611176-843222e1e57c"
                "?q=85&w=1200&auto=format&fit=crop"
            ),
        },
        {
            "title": "ADD A MAIN POINT",
            "description": "Briefly elaborate on what you want to discuss.",
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1512316609839-ce289d3eba0a"
                "?q=85&w=1200&auto=format&fit=crop"
            ),
        },
        {
            "title": "ADD A MAIN POINT",
            "description": "Briefly elaborate on what you want to discuss.",
            "image_url": (
                "https://images.unsplash.com/"
                "photo-1524504388940-b1c1722653e1"
                "?q=85&w=1200&auto=format&fit=crop"
            ),
        },
    ],
    background_color: str = "#CDD0C1",
    title_color: str = "#3B3024",
    text_color: str = "#3B3024",
    timeline_color: str = "#9B8B6C",
    accent_color: str = "#B7B199",
) -> str:
    """
    Generate XML for a gallery timeline slide.

    The layout features a muted neutral background, a large centered serif
    title, a horizontal timeline with evenly distributed dots, and image/text
    milestones alternating above and below the timeline.
    """

    fallback_image = (
        "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"
        "?auto=compress&cs=tinysrgb&w=1600"
    )
    raw_timeline_items = (
        timeline_items
        if isinstance(timeline_items, (list, tuple))
        else [timeline_items]
    )
    normalized_timeline_items: list[dict[str, str]] = []
    for index, raw_item in enumerate(raw_timeline_items):
        item = raw_item if isinstance(raw_item, dict) else {}
        normalized_timeline_items.append(
            {
                "title": str(item.get("title") or "").strip(),
                "description": str(item.get("description") or "").strip(),
                "image_url": str(item.get("image_url") or "").strip() or fallback_image,
            }
        )
    timeline_items = normalized_timeline_items or [
        {
            "title": "",
            "description": "",
            "image_url": fallback_image,
        }
    ]

   

    canvas_width = 1600
    canvas_height = 900

    # =====================================================
    # Font helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Times New Roman": ["timesnewroman", "times"],
            "Arial": ["arial"],
            "Garamond": ["garamond"],
            "Arial": ["arial"],
            "Calibri": ["calibri"],
            "Aptos": ["aptos"],
            "Helvetica": ["helvetica", "arial"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(normalized in stem for normalized in normalized_names):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold:
            fallback_paths = [
                windows_fonts / "timesbd.ttf",
                windows_fonts / "arialbd.ttf",
                windows_fonts / "arialbd.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "times.ttf",
                windows_fonts / "arial.ttf",
                windows_fonts / "garamond.ttf",
                windows_fonts / "arial.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue

            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

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
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
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
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

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
            "height": len(lines) * line_height + padding,
            "width": max_width,
        }

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best = None

        while current_font_size >= min_font_size:
            layout = layout_text(
                text,
                font_path=font_path,
                font_size=current_font_size,
                max_width=max_width,
                line_spacing=line_spacing,
            )

            too_many_lines = (
                max_lines is not None
                and len(layout["lines"]) > max_lines
            )

            score = (
                max(0.0, layout["height"] - max_height) * 1500
                + max(0, len(layout["lines"]) - (max_lines or 99)) * 900
                + (preferred_font_size - current_font_size) * 8
            )

            if best is None or score < best["score"]:
                layout["score"] = score
                best = layout

            if layout["height"] <= max_height and not too_many_lines:
                return layout

            break

        return best

    # =====================================================
    # Layout
    # =====================================================

    count = len(timeline_items)

    title_font_name = "Arial"
    heading_font_name = "Arial"
    body_font_name = "Arial"

    title_font_path = resolve_font_path(title_font_name, bold=True)
    heading_font_path = resolve_font_path(heading_font_name, bold=True)
    body_font_path = resolve_font_path(body_font_name)

    title_layout = fit_text(
        title.strip().upper(),
        font_path=title_font_path,
        preferred_font_size=54.0,
        min_font_size=30.0,
        max_width=1500.0,
        max_height=130.0,
        line_spacing=0.95,
        max_lines=2,
    )

    title_x = canvas_width / 2 - 1500.0 / 2
    title_y = 70.0

    timeline_y = 500.0
    timeline_start_x = 210.0
    timeline_end_x = 1390.0

    if count == 1:
        dot_positions = [
            (timeline_start_x + timeline_end_x) / 2
        ]
    else:
        step_gap = (
            timeline_end_x
            - timeline_start_x
        ) / (count - 1)

        dot_positions = [
            timeline_start_x + index * step_gap
            for index in range(count)
        ]

    cell_width = (
        timeline_end_x
        - timeline_start_x
    ) / max(1, count - 1)

    if count == 1:
        text_box_width = 360.0
        image_width = 320.0
    elif count <= 4:
        text_box_width = 310.0
        image_width = 310.0
    elif count == 5:
        text_box_width = 250.0
        image_width = 250.0
    else:
        text_box_width = 220.0
        image_width = 220.0

    heading_width_limit = (
        520.0
        if count == 1
        else (timeline_end_x - timeline_start_x) / (count - 1) - 12.0
    )
    heading_box_width = max(
        text_box_width,
        min(text_box_width + 60.0, heading_width_limit),
    )

    image_height = image_width * 0.68

    top_image_y = 218.0
    top_text_y = 330.0

    bottom_text_y = 558.0
    bottom_image_y = 612.0

    dot_radius = 14.0

    heading_font_size = 20.0 if count <= 4 else 16.0
    description_font_size = 16.0 if count <= 4 else 12.5

    timeline_layouts: list[dict] = []

    for index, item in enumerate(timeline_items):
        title_text = item["title"].strip().upper()
        description_text = item["description"].strip()

        heading_layout = fit_text(
            title_text,
            font_path=heading_font_path,
            preferred_font_size=heading_font_size,
            min_font_size=16.0,
            max_width=heading_box_width,
            max_height=96.0,
            line_spacing=0.95,
            max_lines=3,
        )

        description_layout = fit_text(
            description_text,
            font_path=body_font_path,
            preferred_font_size=description_font_size,
            min_font_size=12.0,
            max_width=text_box_width,
            max_height=120.0,
            line_spacing=1.15,
            max_lines=4,
        )

        dot_x = dot_positions[index]

        # Alternating layout similar to the reference:
        # image above / text below, then text above / image below.
        image_on_top = index % 2 == 0

        image_x = dot_x - image_width / 2
        text_x = dot_x - text_box_width / 2
        heading_x = dot_x - heading_box_width / 2

        image_x = max(
            20.0,
            min(
                image_x,
                canvas_width - image_width - 20.0,
            ),
        )

        text_x = max(
            20.0,
            min(
                text_x,
                canvas_width - text_box_width - 20.0,
            ),
        )

        heading_x = max(
            20.0,
            min(
                heading_x,
                canvas_width - heading_box_width - 20.0,
            ),
        )

        content_height = (
            heading_layout["height"]
            + 10.0
            + description_layout["height"]
        )

        if image_on_top:
            image_y = top_image_y

            # Use the free space below for longer content while preserving
            # the requested font sizes.
            extra_height = max(0.0, content_height - 120.0)
            heading_y = min(
                bottom_text_y + extra_height * 0.65,
                canvas_height - 32.0 - content_height,
            )
            heading_y = max(bottom_text_y, heading_y)
        else:
            image_y = bottom_image_y

            # Move a taller text block upward so it stays clear of the
            # timeline instead of immediately reducing the font size.
            heading_y = min(
                top_text_y,
                timeline_y - 18.0 - content_height,
            )
            heading_y = max(top_image_y - 8.0, heading_y)

        description_y = (
            heading_y
            + heading_layout["height"]
            + 10.0
        )

        timeline_layouts.append(
            {
                "image_url": item["image_url"].strip(),
                "image_x": image_x,
                "image_y": image_y,
                "image_width": image_width,
                "image_height": image_height,
                "heading": heading_layout,
                "heading_x": heading_x,
                "heading_y": heading_y,
                "description": description_layout,
                "description_x": text_x,
                "description_y": description_y,
                "dot_x": dot_x,
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

    background_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <radialGradient id="topRight" cx="100%" cy="0%" r="32%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.62"/>
      <stop offset="58%" stop-color="{accent_color}" stop-opacity="0.16"/>
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="bottomLeft" cx="0%" cy="100%" r="35%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.48"/>
      <stop offset="62%" stop-color="{accent_color}" stop-opacity="0.13"/>
      <stop offset="100%" stop-color="{accent_color}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="1600" height="900" fill="{background_color}"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#topRight)"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#bottomLeft)"/>
</svg>
""".strip()

    svg_node = add(
        "svg",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=1600,
        pixel_height=900,
    )
    svg_node.text = background_svg

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=1500.0,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(28.0, title_layout["font_size"] - 2.0),
        bold="true",
        color=title_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.95,
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
        width=2.0,
    )

    for item in timeline_layouts:
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

    for item in timeline_layouts:
        add(
            "image",
            src=item["image_url"],
            x=item["image_x"],
            y=item["image_y"],
            width=item["image_width"],
            height=item["image_height"],
            fit="cover",
        )

        textbox(
            item["heading"]["source_text"],
            x=item["heading_x"],
            y=item["heading_y"],
            width=item["heading"]["width"],
            height=item["heading"]["height"],
            font=heading_font_name,
            font_path=str(heading_font_path),
            size=item["heading"]["font_size"],
            min_font_size=max(15.0, item["heading"]["font_size"] - 2.0),
            bold="true",
            color=text_color,
            align="center",
            vertical_align="middle",
            single_line="false",
            max_lines=len(item["heading"]["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=0.95,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        textbox(
            item["description"]["source_text"],
            x=item["description_x"],
            y=item["description_y"],
            width=item["description"]["width"],
            height=item["description"]["height"],
            font=body_font_name,
            font_path=str(body_font_path),
            size=item["description"]["font_size"],
            min_font_size=max(11.0, item["description"]["font_size"] - 2.0),
            color=text_color,
            align="center",
            vertical_align="middle",
            single_line="false",
            max_lines=len(item["description"]["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=1.15,
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

def generate_memorial_introduction_slide_xml(
    section_title: str = "Introduction",
    main_title: str = "Honoring Name Honoring Name Honoring Name Honoring Name",
    body_text: str = (
        "Today, we gather to celebrate the life of\n"
        "[Name]. As we reflect on the memories and\n"
        "moments shared with [him/her], we find\n"
        "solace in music, a universal language that\n"
        "speaks to the heart."
    ),
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1544005313-94ddf0286df2"
        "?q=85&w=1200&auto=format&fit=crop"
    ),
    background_color: str = "#DDEEF2",
    panel_color: str = "#E5CAC3",
    frame_color: str = "#F1F7F8",
    section_title_color: str = "#111111",
    main_title_color: str = "#050505",
    body_text_color: str = "#111111",
) -> str:
    """
    Generate XML for a memorial introduction slide.

    The layout places a large portrait image on the left and a soft pink
    framed text panel on the right. The right panel contains a centered
    section label, a large italic memorial title, and a centered body
    paragraph with flexible text fitting.
    """

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Times New Roman": ["timesnewroman", "times", "arial"],
            "Arial": ["arial", "timesnewroman", "times"],
            "Arial": ["arial", "calibri", "aptos"],
            "Calibri": ["calibri", "arial", "aptos"],
        }

        normalized_names = [
            normalize_font_name(item)
            for item in aliases.get(font_name, [font_name])
        ]

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

                if not any(name in stem for name in normalized_names):
                    continue

                score = 80 if any(name == stem for name in normalized_names) else 58

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 6

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 4

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "timesbi.ttf",
                windows_fonts / "arialbi.ttf",
                windows_fonts / "arialbi.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "timesi.ttf",
                windows_fonts / "ariali.ttf",
                windows_fonts / "ariali.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "timesbd.ttf",
                windows_fonts / "arialbd.ttf",
                windows_fonts / "arialbd.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "times.ttf",
                windows_fonts / "arial.ttf",
                windows_fonts / "arial.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for path in fallback_paths:
            if not path.exists():
                continue

            try:
                ImageFont.truetype(str(path), 12)
                return path
            except OSError:
                continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
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
        def split_long_word(word: str) -> list[str]:
            chunks: list[str] = []
            current_chunk = ""
            for character in word:
                candidate = current_chunk + character
                if (
                    current_chunk
                    and measure_text_width(candidate, font_path, font_size_pt)
                    > max_width
                ):
                    chunks.append(current_chunk)
                    current_chunk = character
                else:
                    current_chunk = candidate
            if current_chunk:
                chunks.append(current_chunk)
            return chunks or [word]

        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
                continue

            current = ""

            for word in words:
                if measure_text_width(word, font_path, font_size_pt) > max_width:
                    if current:
                        lines.append(current)
                        current = ""
                    chunks = split_long_word(word)
                    lines.extend(chunks[:-1])
                    current = chunks[-1]
                    continue

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
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best_layout = None

        while current_font_size >= min_font_size:
            lines = wrap_text(
                text,
                font_path,
                current_font_size,
                max_width,
            )
            line_height = measure_line_height(
                font_path,
                current_font_size,
                line_spacing,
            )
            height = len(lines) * line_height

            too_many_lines = (
                max_lines is not None
                and len(lines) > max_lines
            )

            overflow_height = max(0.0, height - max_height)
            score = (
                overflow_height * 2000
                + max(0, len(lines) - (max_lines or 999)) * 1500
                + (preferred_font_size - current_font_size) * 10
            )

            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_font_size,
                "width": max_width,
                "height": height,
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many_lines:
                return layout

            break

        return best_layout

    section_font_name = "Times New Roman"
    title_font_name = "Times New Roman"
    body_font_name = "Arial"

    section_font_path = resolve_font_path(section_font_name, bold=False, italic=False)
    title_font_path = resolve_font_path(title_font_name, bold=False, italic=True)
    body_font_path = resolve_font_path(body_font_name, bold=False, italic=False)

    image_x = 72.0
    image_y = 82.0
    image_w = 620.0
    image_h = 736.0

    panel_x = 748.0
    panel_y = 82.0
    panel_w = 724.0
    panel_h = 736.0

    text_box_x = panel_x + 112.0
    text_box_width = panel_w - 224.0
    content_top = panel_y + 48.0
    content_bottom = panel_y + panel_h - 48.0
    content_height = content_bottom - content_top
    text_gaps = (34.0, 42.0)

    def build_text_layouts(scale: float) -> tuple[dict, dict, dict]:
        section_layout = fit_text(
            section_title.strip(),
            font_path=section_font_path,
            preferred_font_size=max(12.0, 22.0 * scale),
            min_font_size=12.0,
            max_width=text_box_width,
            max_height=72.0,
            line_spacing=1.0,
            max_lines=2,
        )
        title_layout = fit_text(
            main_title.strip(),
            font_path=title_font_path,
            preferred_font_size=max(20.0, 46.0 * scale),
            min_font_size=22.0,
            max_width=text_box_width,
            max_height=230.0,
            line_spacing=0.92,
            max_lines=4,
        )
        body_layout = fit_text(
            body_text.strip(),
            font_path=body_font_path,
            preferred_font_size=max(10.0, 17.5 * scale),
            min_font_size=9.0,
            max_width=text_box_width,
            max_height=330.0,
            line_spacing=1.42,
            max_lines=10,
        )
        return section_layout, title_layout, body_layout

    # The panel has one managed text stack. It uses available vertical space
    # first; font reduction is only used when the complete stack cannot fit.
    text_scale = 1.0
    section_layout, title_layout, body_layout = build_text_layouts(text_scale)
    for _ in range(60):
        stack_height = (
            section_layout["height"]
            + text_gaps[0]
            + title_layout["height"]
            + text_gaps[1]
            + body_layout["height"]
        )
        if stack_height <= content_height:
            break
        text_scale = max(0.42, text_scale - 0.02)
        section_layout, title_layout, body_layout = build_text_layouts(text_scale)

    stack_height = (
        section_layout["height"]
        + text_gaps[0]
        + title_layout["height"]
        + text_gaps[1]
        + body_layout["height"]
    )
    stack_y = content_top + max(0.0, (content_height - stack_height) / 2.0)
    section_y = stack_y
    title_y = section_y + section_layout["height"] + text_gaps[0]
    body_y = title_y + title_layout["height"] + text_gaps[1]

    stripe_w = 26.0
    stripe_margin = 30.0
    stripe_y = panel_y + 40.0
    stripe_h = panel_h - 80.0

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
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    add(
        "image",
        src=image_url,
        x=image_x,
        y=image_y,
        width=image_w,
        height=image_h,
        fit="cover",
        crop_x=0.50,
        crop_y=0.42,
    )

    add(
        "shape",
        type="rect",
        x=panel_x,
        y=panel_y,
        width=panel_w,
        height=panel_h,
        fill=panel_color,
        line_color="none",
    )

    add(
        "shape",
        type="rect",
        x=panel_x + stripe_margin,
        y=stripe_y,
        width=stripe_w,
        height=stripe_h,
        fill=frame_color,
        line_color="none",
    )

    add(
        "shape",
        type="rect",
        x=panel_x + panel_w - stripe_margin - stripe_w,
        y=stripe_y,
        width=stripe_w,
        height=stripe_h,
        fill=frame_color,
        line_color="none",
    )

    textbox(
        section_layout["source_text"],
        x=text_box_x,
        y=section_y,
        width=text_box_width,
        height=section_layout["height"],
        font=section_font_name,
        font_path=str(section_font_path),
        size=section_layout["font_size"],
        min_font_size=12.0,
        color=section_title_color,
        align="center",
        vertical_align="middle",
        bold="false",
        italic="false",
        single_line="false",
        max_lines=2,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    textbox(
        title_layout["source_text"],
        x=text_box_x,
        y=title_y,
        width=text_box_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=22.0,
        color=main_title_color,
        align="center",
        vertical_align="middle",
        bold="false",
        italic="true",
        single_line="false",
        max_lines=4,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.92,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    textbox(
        body_layout["source_text"],
        x=text_box_x,
        y=body_y,
        width=text_box_width,
        height=body_layout["height"],
        font=body_font_name,
        font_path=str(body_font_path),
        size=body_layout["font_size"],
        min_font_size=9.0,
        color=body_text_color,
        align="center",
        vertical_align="top",
        bold="false",
        italic="false",
        single_line="false",
        max_lines=10,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.42,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content

def generate_legacy_of_love_slide_xml(
    title: str = "Messi Legacy of Love and Kindness",
    left_text: str = (
        "Though [Name] may no longer be with us\n"
        "in person, their legacy of love and kindness\n"
        "lives on. Let us carry forward the lessons\n"
        "they taught us and the love they bestowed\n"
        "upon us, keeping their memory alive in our\n"
        "thoughts and actions."
    ),
    right_text: str = (
        "Let us also honor their memory by embracing the\n"
        "values they held dear. Through acts of\n"
        "compassion, generosity, and understanding, we\n"
        "can perpetuate the essence of who they were,\n"
        "ensuring that their presence continues to\n"
        "illuminate our lives and those of others."
    ),
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1500530855697-b586d89ba3ee"
        "?q=85&w=1600&auto=format&fit=crop&sat=-100"
    ),
    background_color: str = "#F1F1F1",
    panel_color: str = "#E5CAC3",
    border_color: str = "#DDEEF2",
    title_color: str = "#050505",
    body_color: str = "#111111",
    image_overlay_color: str = "#FFFFFF",
    image_overlay_opacity: float = 0.12,
) -> str:
    """
    Generate XML for a memorial legacy slide.

    The layout uses a full-bleed grayscale landscape image, a wide framed
    title band near the top, and a large framed content panel with two
    balanced text columns.
    """


    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

    def font_directories() -> list[Path]:
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
        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(font_name: str, bold: bool = False, italic: bool = False) -> Path:
        aliases = {
            "Times New Roman": ["timesnewroman", "times", "arial"],
            "Arial": ["arial", "timesnewroman", "times"],
            "Arial": ["arial", "calibri", "aptos"],
            "Calibri": ["calibri", "arial", "aptos"],
        }
        normalized_names = [normalize_font_name(item) for item in aliases.get(font_name, [font_name])]
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
                if not any(name in stem for name in normalized_names):
                    continue
                score = 80 if any(name == stem for name in normalized_names) else 58
                has_bold = any(token in stem for token in ("bold", "bd", "semibold", "demi"))
                has_italic = any(token in stem for token in ("italic", "oblique", "it"))
                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 6
                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 4
                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        if bold and italic:
            fallback_paths = [windows_fonts / "timesbi.ttf", windows_fonts / "arialbi.ttf", windows_fonts / "arialbi.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf")]
        elif italic:
            fallback_paths = [windows_fonts / "timesi.ttf", windows_fonts / "ariali.ttf", windows_fonts / "ariali.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf")]
        elif bold:
            fallback_paths = [windows_fonts / "timesbd.ttf", windows_fonts / "arialbd.ttf", windows_fonts / "arialbd.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")]
        else:
            fallback_paths = [windows_fonts / "times.ttf", windows_fonts / "arial.ttf", windows_fonts / "arial.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
        for path in fallback_paths:
            if path.exists():
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue
        return _resolve_font_fallback_path(bold=bold, italic=italic)

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(font_path), max(1, round(pt_to_canvas(font_size_pt))))

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
        font = load_font(font_path, font_size_pt)
        if hasattr(font, "getlength"):
            return float(font.getlength(text))
        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(font_path: Path, font_size_pt: float, line_spacing: float) -> float:
        font = load_font(font_path, font_size_pt)
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

    def wrap_text(text: str, font_path: Path, font_size_pt: float, max_width: float) -> list[str]:
        def split_long_word(word: str) -> list[str]:
            chunks: list[str] = []
            current_chunk = ""
            for character in word:
                candidate = current_chunk + character
                if (
                    current_chunk
                    and measure_text_width(candidate, font_path, font_size_pt) > max_width
                ):
                    chunks.append(current_chunk)
                    current_chunk = character
                else:
                    current_chunk = candidate
            if current_chunk:
                chunks.append(current_chunk)
            return chunks or [word]

        lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue
            current = ""
            for word in words:
                if measure_text_width(word, font_path, font_size_pt) > max_width:
                    if current:
                        lines.append(current)
                        current = ""
                    chunks = split_long_word(word)
                    lines.extend(chunks[:-1])
                    current = chunks[-1]
                    continue

                candidate = word if not current else f"{current} {word}"
                if not current or measure_text_width(candidate, font_path, font_size_pt) <= max_width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines or [""]

    def fit_text(text: str, *, font_path: Path, preferred_font_size: float, min_font_size: float, max_width: float, max_height: float, line_spacing: float, max_lines: int | None = None) -> dict:
        current_font_size = preferred_font_size
        best_layout = None
        while current_font_size >= min_font_size:
            lines = wrap_text(text, font_path, current_font_size, max_width)
            line_height = measure_line_height(font_path, current_font_size, line_spacing)
            height = len(lines) * line_height
            too_many_lines = max_lines is not None and len(lines) > max_lines
            overflow_height = max(0.0, height - max_height)
            score = overflow_height * 2000 + max(0, len(lines) - (max_lines or 999)) * 1500 + (preferred_font_size - current_font_size) * 10
            layout = {"source_text": text, "lines": lines, "font_size": current_font_size, "width": max_width, "height": min(height, max_height), "score": score}
            if best_layout is None or score < best_layout["score"]:
                best_layout = layout
            if height <= max_height and not too_many_lines:
                return layout
            break
        return best_layout

    title_font_name = "Times New Roman"
    body_font_name = "Arial"
    title_font_path = resolve_font_path(title_font_name, bold=False, italic=True)
    body_font_path = resolve_font_path(body_font_name, bold=False, italic=False)

    title_layout = fit_text(title.strip(), font_path=title_font_path, preferred_font_size=50.0, min_font_size=20.0, max_width=1260.0, max_height=200.0, line_spacing=0.95, max_lines=2)
    left_layout = fit_text(left_text.strip(), font_path=body_font_path, preferred_font_size=18.5, min_font_size=10.0, max_width=560.0, max_height=380.0, line_spacing=1.42, max_lines=12)
    right_layout = fit_text(right_text.strip(), font_path=body_font_path, preferred_font_size=18.5, min_font_size=10.0, max_width=560.0, max_height=380.0, line_spacing=1.42, max_lines=12)

    top_panel_x = 92.0
    top_panel_y = 138.0
    top_panel_w = 1415.0
    top_panel_h = min(
        230.0,
        max(172.0, title_layout["height"] + 48.0),
    )

    lower_panel_x = 92.0
    lower_panel_y = max(416.0, top_panel_y + top_panel_h + 74.0)
    lower_panel_w = 1415.0
    max_lower_panel_h = canvas_height - lower_panel_y - 32.0
    lower_panel_h = min(
        max_lower_panel_h,
        max(354.0, max(left_layout["height"], right_layout["height"]) + 64.0),
    )
    body_content_top = lower_panel_y + 18.0
    body_content_bottom = lower_panel_y + lower_panel_h - 18.0
    body_content_height = body_content_bottom - body_content_top
    body_stack_height = max(left_layout["height"], right_layout["height"])
    body_y = body_content_top + max(
        0.0,
        (body_content_height - body_stack_height) / 2.0,
    )

    presentation = ET.Element("presentation", {"schemaVersion": "1.0", "width": str(canvas_width), "height": str(canvas_height), "slideWidthInches": "13.333", "slideHeightInches": "7.5"})
    slide = ET.SubElement(presentation, "slide", {"background": background_color})

    def add(tag: str, **attrs):
        return ET.SubElement(slide, tag, {key: str(value) for key, value in attrs.items() if value is not None})

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    add("image", src=image_url, x=0, y=0, width=canvas_width, height=canvas_height, fit="cover", crop_x=0.5, crop_y=0.45)
    add("shape", type="rect", x=0, y=0, width=canvas_width, height=canvas_height, fill=image_overlay_color, opacity=image_overlay_opacity, line_color="none")

    # Top title frame and panel
    add("shape", type="rect", x=top_panel_x, y=top_panel_y - 32.0, width=top_panel_w, height=top_panel_h + 64.0, fill=border_color, line_color="none", opacity=0.98)
    add("shape", type="rect", x=top_panel_x, y=top_panel_y, width=top_panel_w, height=top_panel_h, fill=panel_color, line_color="none", opacity=0.96)

    # Lower content frame and panel
    add("shape", type="rect", x=lower_panel_x, y=lower_panel_y - 32.0, width=lower_panel_w, height=lower_panel_h + 64.0, fill=border_color, line_color="none", opacity=0.98)
    add("shape", type="rect", x=lower_panel_x, y=lower_panel_y, width=lower_panel_w, height=lower_panel_h, fill=panel_color, line_color="none", opacity=0.96)

    textbox(title_layout["source_text"], x=170, y=top_panel_y + 24.0, width=1260, height=title_layout["height"], font=title_font_name, font_path=str(title_font_path), size=title_layout["font_size"], min_font_size=20.0, color=title_color, align="center", vertical_align="middle", bold="false", italic="true", single_line="false", max_lines=2, overflow="clip", reflow_on_resize="true", line_spacing=0.95, margin_left=0, margin_right=0, margin_top=0, margin_bottom=0, safety_ratio=1.0)
    textbox(left_layout["source_text"], x=160, y=body_y, width=560, height=left_layout["height"], font=body_font_name, font_path=str(body_font_path), size=left_layout["font_size"], min_font_size=10.0, color=body_color, align="center", vertical_align="top", bold="false", italic="false", single_line="false", max_lines=12, overflow="clip", reflow_on_resize="true", line_spacing=1.42, margin_left=0, margin_right=0, margin_top=0, margin_bottom=0, safety_ratio=1.0)
    textbox(right_layout["source_text"], x=880, y=body_y, width=560, height=right_layout["height"], font=body_font_name, font_path=str(body_font_path), size=right_layout["font_size"], min_font_size=10.0, color=body_color, align="center", vertical_align="top", bold="false", italic="false", single_line="false", max_lines=12, overflow="clip", reflow_on_resize="true", line_spacing=1.42, margin_left=0, margin_right=0, margin_top=0, margin_bottom=0, safety_ratio=1.0)

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
    return xml_content

def generate_social_media_points_slide_xml(
    title: str = "Write your topic or  wirta á  idea on social media thank for using this tool",
    cards: list[dict[str, str]]  = [
            {
                "title": "ADD A MAIN POINT ADD A MAIN POINT ADD A MAIN POINT",
                "description": "Briefly elaborate on what you want to discuss.",
            },
            {
                "title": "ADD A MAIN POINT",
                "description": "Briefly elaborate on what you want to discuss. Briefly elaborate on what you want to discuss. Briefly elaborate on what you want to discuss.",
            },
            
        ],
    background_color: str = "#FFFFFF",
    accent_color: str = "#6F8369",
    card_color: str = "#E9EDE9",
    title_color: str = "#000000",
    card_title_color: str = "#000000",
    card_body_color: str = "#000000",
    star_color: str = "#FFFFFF",
    divider_color: str = "#7C7C7C",
) -> str:
    """
    Generate XML for a clean social media key-points slide.

    The layout uses a white background, a small top divider, one editable
    headline, and a row of content cards with green headers and star icons.
    Cards are generated from a list and the layout adjusts spacing and text
    size to fit the available area.
    """

    clean_cards: list[dict[str, str]] = []
    for card in cards[:3]:
        card_title = str(card.get("title", "")).strip()
        description = str(card.get("description", "")).strip()

        if not card_title and not description:
            continue

        clean_cards.append(
            {
                "title": card_title or "ADD A MAIN POINT",
                "description": description or "Briefly elaborate on what you want to discuss.",
            }
        )

    if not clean_cards:
        clean_cards = [
            {
                "title": "ADD A MAIN POINT",
                "description": "Briefly elaborate on what you want to discuss.",
            }
        ]

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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
        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(font_name: str, bold: bool = False, italic: bool = False) -> Path:
        aliases = {
            "Arial": ["arial", "helvetica"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri", "aptos", "arial"],
            "Aptos": ["aptos", "calibri", "arial"],
            "Arial": ["arial", "times"],
            "Times New Roman": ["timesnewroman", "times", "arial"],
        }

        normalized_names = [normalize_font_name(name) for name in aliases.get(font_name, [font_name])]
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
                if not any(name in stem for name in normalized_names):
                    continue

                score = 70
                if stem in normalized_names:
                    score += 30

                has_bold = any(token in stem for token in ("bold", "bd", "semibold", "demi"))
                has_italic = any(token in stem for token in ("italic", "oblique", "it"))

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for path in fallback_paths:
            if path.exists():
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
        if not text:
            return 0.0
        font = load_font(font_path, font_size_pt)
        if hasattr(font, "getlength"):
            return float(font.getlength(text))
        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(font_path: Path, font_size_pt: float, line_spacing: float) -> float:
        font = load_font(font_path, font_size_pt)
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

    def wrap_text(text: str, font_path: Path, font_size_pt: float, max_width: float) -> list[str]:
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current = ""
            for word in words:
                candidate = word if not current else f"{current} {word}"
                if not current or measure_text_width(candidate, font_path, font_size_pt) <= max_width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_size: float,
        min_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_size = preferred_size
        best_layout = None

        while current_size >= min_size:
            lines = wrap_text(text, font_path, current_size, max_width)
            line_height = measure_line_height(font_path, current_size, line_spacing)
            height = len(lines) * line_height
            too_many = max_lines is not None and len(lines) > max_lines
            overflow = max(0.0, height - max_height)

            score = (
                overflow * 1800
                + max(0, len(lines) - (max_lines or 999)) * 1200
                + (preferred_size - current_size) * 8
            )

            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many:
                return layout

            break

        return best_layout

    title_font_name = "Arial"
    title_font_path = resolve_font_path(title_font_name, bold=True, italic=False)
    title_layout = fit_text(
        title,
        font_path=title_font_path,
        preferred_size=44.0,
        min_size=22.0,
        max_width=1400.0,
        max_height=120.0,
        line_spacing=1.0,
        max_lines=2,
    )

    card_count = len(clean_cards)
    if card_count == 1:
        columns = 1
    elif card_count == 2:
        columns = 2
    else:
        columns = 3

    rows = (card_count + columns - 1) // columns

    horizontal_margin = 26.0
    gap_x = 88.0 if columns == 3 else 72.0
    available_w = canvas_width - horizontal_margin * 2 - gap_x * (columns - 1)
    card_w = available_w / columns

    card_area_y = 336.0
    card_area_h = 485.0
    gap_y = 34.0
    card_h = (card_area_h - gap_y * (rows - 1)) / rows
    header_h = min(98.0, card_h * 0.24)

    card_title_font_path = resolve_font_path("Arial", bold=True)
    card_body_font_path = resolve_font_path("Arial", bold=False)

    card_layouts: list[dict[str, object]] = []
    for index, card in enumerate(clean_cards):
        card_title_layout = fit_text(
            card["title"],
            font_path=card_title_font_path,
        preferred_size=18.0,
            min_size=18,
            max_width=card_w - 70,
            max_height=max(30.0, card_h * 0.18),
            line_spacing=1.05,
            max_lines=2,
        )

        body_layout = fit_text(
            card["description"],
            font_path=card_body_font_path,
        preferred_size=16,
            min_size=15,
            max_width=card_w - 70,
            max_height=max(54.0, card_h - header_h - 120.0),
            line_spacing=1.22,
            max_lines=None,
        )

        row = index // columns
        col = index % columns
        x = horizontal_margin + col * (card_w + gap_x)
        y = card_area_y + row * (card_h + gap_y)

        card_layouts.append(
            {
                "x": x,
                "y": y,
                "title": card_title_layout,
                "body": body_layout,
            }
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
    slide = ET.SubElement(presentation, "slide", {"background": background_color})

    def add(tag: str, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {key: str(value) for key, value in attrs.items() if value is not None},
        )

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    add(
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    add(
        "line",
        x1=800,
        y1=0,
        x2=800,
        y2=94,
        color=divider_color,
        width=1.1,
    )

    # One editable centered title string.
    title_width = 1400.0
    title_y = 165.0
    textbox(
        title_layout["source_text"],
        x=(canvas_width - title_width) / 2.0,
        y=title_y,
        width=title_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=22.0,
        color=title_color,
        align="center",
        vertical_align="middle",
        bold="true",
        italic="false",
        single_line="false",
        max_lines=2,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    star_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 72 72">
  <path d="M36 5 L44.3 26.2 L67 26.2 L48.8 40.1 L55.8 66 L36 50.3 L16.2 66 L23.2 40.1 L5 26.2 L27.7 26.2 Z"
        fill="{star_color}"/>
</svg>
""".strip()

    for card in card_layouts:
        x = float(card["x"])
        y = float(card["y"])

        add(
            "shape",
            type="rect",
            x=x,
            y=y,
            width=card_w,
            height=card_h,
            fill=card_color,
            line_color="none",
        )

        add(
            "shape",
            type="rect",
            x=x,
            y=y,
            width=card_w,
            height=header_h,
            fill=accent_color,
            line_color="none",
        )

        star_node = add(
            "svg",
            name="card_star",
            x=x + card_w / 2 - 28,
            y=y + header_h / 2 - 28,
            width=56,
            height=56,
            pixel_width=216,
            pixel_height=216,
        )
        star_node.text = star_svg

        title_layout = card["title"]
        body_layout = card["body"]

        # Keep card content closer to the colored header while preserving a
        # small breathing gap below the header.
        content_top = y + header_h + 60.0
        title_y = content_top
        body_y = title_y + title_layout["height"] + 34.0

        textbox(
            title_layout["source_text"],
            x=x + 35,
            y=title_y,
            width=card_w - 70,
            height=title_layout["height"],
            font="Arial",
            font_path=str(card_title_font_path),
            size=title_layout["font_size"],
            min_font_size=max(7.0, title_layout["font_size"] - 2.0),
            color=card_title_color,
            align="center",
            vertical_align="middle",
            bold="true",
            italic="false",
            single_line="false",
            max_lines=len(title_layout["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=1.05,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
            safety_ratio=1.0,
        )

        textbox(
            body_layout["source_text"],
            x=x + 35,
            y=body_y,
            width=card_w - 70,
            height=body_layout["height"],
            font="Arial",
            font_path=str(card_body_font_path),
            size=body_layout["font_size"],
            min_font_size=max(7.0, body_layout["font_size"] - 2.0),
            color=card_body_color,
            align="center",
            vertical_align="top",
            bold="false",
            italic="false",
            single_line="false",
            max_lines=len(body_layout["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=1.22,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
            safety_ratio=1.0,
        )

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content

def generate_numbered_social_media_points_slide_xml(
    title: str = "Write Your Topic or Idea on Social Media Idea on Social Media Idea on Social Media",
    items: list[dict[str, str]]  = [
            {
                "title": "Messi is the GOAT of soccer Messi is the GOAT of soccer ",
                "description": "Elaborate on what you want to discuss Elaborate on what you want to discuss  Elaborate on what you want to discuss  Elaborate on what you want to discuss Elaborate on what you want to discuss Elaborate on what you want to discuss.",
            },
            {
                "title": "ADD A MAIN POINT",
                "description": "Elaborate on what you want to discuss.",
            },
            {
                "title": "ADD A MAIN POINT",
                "description": "Elaborate on what you want to discuss.",
            },
            {
                "title": "ADD A MAIN POINT",
                "description": "Elaborate on what you want to discuss.",
            },
            {
                "title": "ADD A MAIN POINT",
                "description": "Elaborate on what you want to discuss.",
            },
            {
                "title": "ADD A MAIN POINT",
                "description": "Elaborate on what you want to discuss.",
            },
        ],
    background_color: str = "#FFFFFF",
    content_background_color: str = "#F0F3F0",
    accent_color: str = "#6F8369",
    title_color: str = "#000000",
    item_title_color: str = "#000000",
    item_body_color: str = "#000000",
    divider_color: str = "#777777",
) -> str:
    """
    Generate XML for a numbered social media points slide.

    The layout uses one large title string at the top and places numbered
    content items in a balanced grid on a soft green-gray content background.
    Item numbers are generated from item order and are not separate input
    content.
    """

    clean_title = str(title or "").strip()

    raw_items = items if isinstance(items, (list, tuple)) else [items]
    normalized_items: list[dict[str, str]] = []
    for raw_item in raw_items:
        item = raw_item if isinstance(raw_item, dict) else {}
        normalized_items.append(
            {
                "title": str(item.get("title") or "").strip(),
                "description": str(item.get("description") or "").strip(),
            }
        )
    items = normalized_items or [
        {
            "title": "",
            "description": "",
        }
    ]

   

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": ["arial", "helvetica"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri", "aptos", "arial"],
            "Aptos": ["aptos", "calibri", "arial"],
            "Arial": ["arial", "times"],
            "Times New Roman": ["timesnewroman", "times", "arial"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(name in stem for name in normalized_names):
                    continue

                score = 70
                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue

            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
        if not text:
            return 0.0

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
        def split_long_word(word: str) -> list[str]:
            chunks: list[str] = []
            current_chunk = ""
            for character in word:
                candidate = current_chunk + character
                if (
                    current_chunk
                    and measure_text_width(candidate, font_path, font_size_pt) > max_width
                ):
                    chunks.append(current_chunk)
                    current_chunk = character
                else:
                    current_chunk = candidate
            return chunks + [current_chunk] if current_chunk else chunks or [word]

        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
                continue

            current = ""

            for word in words:
                if measure_text_width(word, font_path, font_size_pt) > max_width:
                    if current:
                        lines.append(current)
                        current = ""
                    chunks = split_long_word(word)
                    lines.extend(chunks[:-1])
                    current = chunks[-1]
                    continue

                candidate = word if not current else f"{current} {word}"

                if (
                    not current
                    or measure_text_width(candidate, font_path, font_size_pt)
                    <= max_width
                ):
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_size: float,
        min_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_size = preferred_size
        best_layout = None

        while current_size >= min_size:
            lines = wrap_text(text, font_path, current_size, max_width)
            line_height = measure_line_height(font_path, current_size, line_spacing)
            height = len(lines) * line_height
            too_many = max_lines is not None and len(lines) > max_lines
            overflow = max(0.0, height - max_height)

            score = (
                overflow * 1800
                + max(0, len(lines) - (max_lines or 999)) * 1200
                + (preferred_size - current_size) * 8
            )

            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many:
                return layout

            break

        return best_layout

    font_name = "Arial"
    title_font_path = resolve_font_path(font_name, bold=True)
    item_title_font_path = resolve_font_path(font_name, bold=True)
    item_body_font_path = resolve_font_path(font_name, bold=False)
    item_number_font_path = resolve_font_path(font_name, bold=True)

    title_layout = fit_text(
        clean_title,
        font_path=title_font_path,
        preferred_size=36.0,
        min_size=18.0,
        max_width=1400.0,
        max_height=128.0,
        line_spacing=1.04,
        max_lines=None,
    )

    item_count = len(items)

    if item_count == 1:
        columns = 1
    elif item_count == 2:
        columns = 2
    else:
        columns = 3

    rows = (item_count + columns - 1) // columns

    panel_x = 0.0
    panel_y = 372.0
    panel_w = canvas_width
    panel_h = 548.0

    content_left = 94.0
    content_right = 94.0
    content_top = panel_y + 98.0
    content_bottom = 88.0
    item_area_w = canvas_width - content_left - content_right
    item_area_h = panel_h - 98.0 - content_bottom

    gap_x = 88.0 if columns == 3 else 76.0
    gap_y = 92.0 if rows == 2 else 50.0

    cell_w = (item_area_w - gap_x * (columns - 1)) / columns
    cell_h = (item_area_h - gap_y * (rows - 1)) / rows

    number_w = 62.0
    title_gap = 18.0
    text_w = cell_w - number_w - title_gap
    title_body_gap = 14.0
    card_bottom_padding = 12.0
    minimum_body_height = 40.0
    item_layouts: list[dict[str, object]] = []
    for index, item in enumerate(items):
        row = index // columns
        col = index % columns

        x = content_left + col * (cell_w + gap_x)
        y = content_top + row * (cell_h + gap_y)

        # A row may use the gap before the next row. The last row may use the
        # remaining panel space. This delays font reduction until the text is
        # actually close to another card or to the panel boundary.
        next_row_y = (
            y + cell_h + gap_y
            if row < rows - 1
            else panel_y + panel_h - content_bottom
        )
        available_item_height = max(1.0, next_row_y - y)
        maximum_card_title_height = max(
            28.0,
            available_item_height
            - title_body_gap
            - card_bottom_padding
            - minimum_body_height,
        )

        title_item_layout = fit_text(
            item["title"],
            font_path=item_title_font_path,
        preferred_size=15.0,
            min_size=8.0,
            max_width=text_w,
            max_height=maximum_card_title_height,
            line_spacing=1.05,
            max_lines=3,
        )

        body_item_layout = fit_text(
            item["description"],
            font_path=item_body_font_path,
        preferred_size=13.0,
            min_size=7.5,
            max_width=text_w,
            max_height=max(
                minimum_body_height,
                available_item_height
                - title_item_layout["height"]
                - title_body_gap
                - card_bottom_padding,
            ),
            line_spacing=1.28,
            max_lines=None,
        )

        item_layouts.append(
            {
                "x": x,
                "y": y,
                "number": f"{index + 1:02d}",
                "title": title_item_layout,
                "body": body_item_layout,
            }
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
        node = add("textbox", **attrs)
        node.text = text
        return node

    add(
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    add(
        "line",
        x1=canvas_width / 2,
        y1=0,
        x2=canvas_width / 2,
        y2=92,
        color=divider_color,
        width=1.2,
        opacity=0.72,
    )

    # Keep the title as one string and one textbox. Wrapping is handled by the
    # textbox layout instead of creating a separate textbox for every word.
    textbox(
        title_layout["source_text"],
        x=100.0,
        y=176.0,
        width=1400.0,
        height=title_layout["height"],
        font=font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(16.0, title_layout["font_size"] - 2.0),
        color=title_color,
        align="center",
        vertical_align="middle",
        bold="true",
        italic="false",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.04,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    add(
        "shape",
        type="rect",
        x=panel_x,
        y=panel_y,
        width=panel_w,
        height=panel_h,
        fill=content_background_color,
        line_color="none",
    )

    for layout in item_layouts:
        x = float(layout["x"])
        y = float(layout["y"])

        textbox(
            str(layout["number"]),
            x=x,
            y=y,
            width=number_w,
            height=34.0,
            font=font_name,
            font_path=str(item_number_font_path),
            size=16.0,
            min_font_size=10.0,
            color=accent_color,
            align="left",
            vertical_align="middle",
            bold="true",
            italic="false",
            single_line="true",
            max_lines=1,
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
            safety_ratio=1.0,
        )

        title_item = layout["title"]
        body_item = layout["body"]

        text_x = x + number_w + title_gap

        textbox(
            title_item["source_text"],
            x=text_x,
            y=y,
            width=text_w,
            height=title_item["height"],
            font=font_name,
            font_path=str(item_title_font_path),
            size=title_item["font_size"],
            min_font_size=max(7.0, title_item["font_size"] - 2.0),
            color=item_title_color,
            align="left",
            vertical_align="top",
            bold="true",
            italic="false",
            single_line="false",
            max_lines=len(title_item["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=1.05,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
            safety_ratio=1.0,
        )

        textbox(
            body_item["source_text"],
            x=text_x,
            y=y + title_item["height"] + title_body_gap,
            width=text_w,
            height=body_item["height"],
            font=font_name,
            font_path=str(item_body_font_path),
            size=body_item["font_size"],
            min_font_size=max(7.0, body_item["font_size"] - 2.0),
            color=item_body_color,
            align="left",
            vertical_align="top",
            bold="false",
            italic="false",
            single_line="false",
            max_lines=len(body_item["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=1.28,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
            safety_ratio=1.0,
        )

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content

def generate_platform_instructions_slide_xml(
    items: list[dict[str, object]]  = [
            {
                "title": "GOOGLE SLIDES",
                "icon": "team",
                "accent_color": "#F04425",
                "subtitle": (
                    "Click on the \"Google Slides\" button\n"
                    "below this presentation preview.\n\n"
                    "Click on \"Make a copy.\"\n"
                    "Start editing your presentation.\n\n"
                    "You need to sign in to\n"
                    "your Google account."
                ),
            },
            {
                "title": "POWERPOINT",
                "icon": "idea",
                "accent_color": "#FFC817",
                "subtitle": (
                    "Click on the \"PowerPoint\" button\n"
                    "below this presentation preview.\n\n"
                    "Start editing your presentation.\n\n"
                    "Download and install\n"
                    "the fonts used in this presentation\n"
                    "as listed on the next page."
                ),
            },
            {
                "title": "CANVA",
                "icon": "target",
                "accent_color": "#70BFD6",
                "subtitle": (
                    "Click on the \"Canva\" button under\n"
                    "this presentation preview.\n\n"
                    "Start editing your presentation.\n\n"
                    "You need to sign in to\n"
                    "your Canva account."
                ),
            },
    ],
    background_color: str = "#F4F2EF",
    text_color: str = "#050505",
    line_color: str = "#050505",
) -> str:
    """
    Generate XML for a platform instruction slide.

    The layout uses evenly spaced instruction columns with a short colored
    accent line, a bold platform title, an organic color blob with a simple
    icon, and centered instructional text. The layout adapts to the number
    of platform items while preserving the requested text sizes.
    """


    clean_items: list[dict[str, object]] = []

    def flatten_text(value: object) -> str:
        # Treat both real newlines and the literal ``\\n`` sequence as spaces.
        return " ".join(str(value).replace("\\n", " ").split())

    for index, item in enumerate(items):
        title = flatten_text(item.get("title", ""))
        subtitle = flatten_text(item.get("subtitle", ""))
        icon = str(item.get("icon", "")).strip().lower()
        accent_color = str(
            item.get(
                "accent_color",
                line_color,
            )
        ).strip()

        if not title:
            title = f"PLATFORM {index + 1}"

        if not subtitle:
            subtitle = "Add instruction text for this platform."

        if not icon:
            icon = "star"

        if not accent_color:
            accent_color = line_color

        clean_items.append(
            {
                "title": title,
                "subtitle": subtitle,
                "icon": icon,
                "accent_color": accent_color,
            }
        )

    if not clean_items:
        clean_items = [
            {
                "title": "PLATFORM",
                "subtitle": "Add instruction text for this platform.",
                "icon": "star",
                "accent_color": line_color,
            }
        ]

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": ["arial", "helvetica"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri", "aptos", "arial"],
            "Aptos": ["aptos", "calibri", "arial"],
            "Arial": ["arial", "times"],
            "Times New Roman": ["timesnewroman", "times", "arial"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(name in stem for name in normalized_names):
                    continue

                score = 70
                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if fallback_path.exists():
                try:
                    ImageFont.truetype(str(fallback_path), 12)
                    return fallback_path
                except OSError:
                    continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        if not text:
            return 0.0

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
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
                continue

            current = ""

            for word in words:
                candidate = word if not current else f"{current} {word}"

                if (
                    not current
                    or measure_text_width(candidate, font_path, font_size_pt)
                    <= max_width
                ):
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_size: float,
        min_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_size = preferred_size
        best_layout = None

        while current_size >= min_size:
            lines = wrap_text(text, font_path, current_size, max_width)
            line_height = measure_line_height(font_path, current_size, line_spacing)
            height = len(lines) * line_height
            too_many = max_lines is not None and len(lines) > max_lines
            overflow = max(0.0, height - max_height)

            score = (
                overflow * 1800
                + max(0, len(lines) - (max_lines or 999)) * 1200
                + (preferred_size - current_size) * 8
            )

            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many:
                return layout

            break

        return best_layout

    def organic_blob_path(shape_index: int) -> str:
        paths = [
            "M100 8 C137 5 168 27 194 61 C218 92 226 132 199 160 C170 190 128 204 87 191 C49 179 25 154 11 116 C-2 82 21 44 47 23 C62 11 78 10 100 8 Z",
            "M109 10 C144 3 169 20 191 52 C217 91 207 147 181 172 C153 199 98 203 63 184 C32 167 10 119 20 80 C26 48 49 27 77 17 C87 14 98 12 109 10 Z",
            "M105 4 C128 11 155 9 179 26 C210 47 214 72 212 115 C211 151 179 188 145 197 C108 207 52 197 25 171 C0 147 6 93 24 60 C42 27 70 -5 105 4 Z",
            "M97 5 C132 3 160 20 188 49 C211 74 221 117 207 151 C190 192 145 204 100 196 C60 189 21 164 11 121 C2 82 21 39 51 18 C64 9 79 6 97 5 Z",
        ]
        return paths[shape_index % len(paths)]

    def icon_svg(icon_name: str, accent_color: str, shape_index: int) -> str:
        blob_path = organic_blob_path(shape_index)

        if icon_name == "team":
            icon = """
<g fill="none" stroke="#000000" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="110" cy="79" r="21"/>
  <circle cx="72" cy="99" r="15"/>
  <circle cx="150" cy="99" r="15"/>
  <path d="M74 149 L74 127 C74 116 82 110 94 110 L126 110 C138 110 146 116 146 127 L146 149 Z"/>
  <path d="M36 149 L36 130 C36 121 43 116 53 116 L76 116"/>
  <path d="M144 116 L167 116 C177 116 184 121 184 130 L184 149"/>
  <path d="M111 42 L111 25"/>
  <path d="M82 54 L72 39"/>
  <path d="M140 54 L150 39"/>
  <path d="M63 74 L47 68"/>
  <path d="M157 74 L173 68"/>
</g>
"""
        elif icon_name == "idea":
            icon = """
<g fill="none" stroke="#000000" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
  <path d="M111 40 C82 40 64 62 64 89 C64 109 75 121 87 134 C92 139 95 147 95 155 L127 155 C127 147 131 139 136 133 C148 120 158 108 158 88 C158 61 139 40 111 40 Z"/>
  <path d="M96 173 L126 173"/>
  <path d="M98 155 L124 155"/>
  <path d="M110 23 L110 9"/>
  <path d="M67 40 L57 27"/>
  <path d="M154 40 L164 27"/>
  <path d="M45 88 L31 88"/>
  <path d="M177 88 L191 88"/>
</g>
"""
        elif icon_name == "target":
            icon = """
<g fill="none" stroke="#000000" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="108" cy="91" r="56"/>
  <circle cx="108" cy="91" r="35"/>
  <circle cx="108" cy="91" r="13"/>
  <path d="M117 101 L164 148"/>
  <path d="M164 148 L156 121"/>
  <path d="M164 148 L137 141"/>
</g>
"""
        elif icon_name == "download":
            icon = """
<g fill="none" stroke="#000000" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
  <path d="M110 42 L110 130"/>
  <path d="M78 101 L110 133 L142 101"/>
  <path d="M55 162 L165 162"/>
  <path d="M55 162 L55 136"/>
  <path d="M165 162 L165 136"/>
</g>
"""
        else:
            icon = """
<g fill="none" stroke="#000000" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
  <path d="M111 33 L128 78 L176 78 L137 106 L152 152 L111 124 L70 152 L85 106 L46 78 L94 78 Z"/>
</g>
"""

        return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="240" height="220" viewBox="0 0 240 220">
  <path d="{blob_path}" fill="{accent_color}"/>
  {icon}
</svg>
""".strip()

    font_name = "Arial"
    title_font_path = resolve_font_path(font_name, bold=True)
    body_font_path = resolve_font_path(font_name, bold=True)

    count = len(clean_items)

    if count == 1:
        columns = 1
    elif count == 2:
        columns = 2
    else:
        columns = 3

    rows = (count + columns - 1) // columns

    margin_x = 46.0
    gap_x = 46.0 if columns == 3 else 58.0
    top_y = 82.0
    bottom_margin = 70.0
    row_gap = 44.0 if rows > 1 else 0.0

    available_width = canvas_width - margin_x * 2 - gap_x * (columns - 1)
    cell_width = available_width / columns

    available_height = canvas_height - top_y - bottom_margin - row_gap * (rows - 1)
    cell_height = available_height / rows

    title_y_offset = 38.0
    accent_line_w = min(280.0, cell_width * 0.54)
    accent_line_h = 9.0
    blob_size = min(270.0, max(150.0, cell_width * 0.42), cell_height * 0.30)
    body_top_gap = 42.0 if cell_height > 470 else 24.0

    item_layouts: list[dict[str, object]] = []

    for index, item in enumerate(clean_items):
        title_layout = fit_text(
            str(item["title"]).upper(),
            font_path=title_font_path,
            preferred_size=23.0,
            min_size=10.0,
            max_width=cell_width - 54.0,
            max_height=max(35.0, cell_height * 0.08),
            line_spacing=0.95,
            max_lines=2,
        )

        body_max_height = max(120.0, cell_height - 78.0 - title_layout["height"] - blob_size - body_top_gap)
        body_layout = fit_text(
            str(item["subtitle"]),
            font_path=body_font_path,
            preferred_size=16.0,
            min_size=8.0,
            max_width=cell_width - 24.0,
            max_height=body_max_height,
            line_spacing=1.22,
            max_lines=None,
        )

        row = index // columns
        col = index % columns
        cell_x = margin_x + col * (cell_width + gap_x)
        cell_y = top_y + row * (cell_height + row_gap)

        item_layouts.append(
            {
                "x": cell_x,
                "y": cell_y,
                "title": title_layout,
                "body": body_layout,
                "item": item,
                "index": index,
            }
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

    slide = ET.SubElement(presentation, "slide", {"background": background_color})

    def add(tag: str, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {key: str(value) for key, value in attrs.items() if value is not None},
        )

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    add(
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    for layout in item_layouts:
        x = float(layout["x"])
        y = float(layout["y"])
        item = layout["item"]
        title_layout = layout["title"]
        body_layout = layout["body"]
        index = int(layout["index"])

        accent_color = str(item["accent_color"])

        add(
            "shape",
            type="rect",
            x=x + cell_width / 2 - accent_line_w / 2,
            y=y,
            width=accent_line_w,
            height=accent_line_h,
            fill=accent_color,
            line_color="none",
        )

        textbox(
            title_layout["source_text"],
            x=x + 18.0,
            y=y + title_y_offset,
            width=cell_width - 36.0,
            height=title_layout["height"],
            font=font_name,
            font_path=str(title_font_path),
            size=title_layout["font_size"],
            min_font_size=max(8.0, title_layout["font_size"] - 2.0),
            color=text_color,
            align="center",
            vertical_align="middle",
            bold="true",
            italic="false",
            single_line="false",
            max_lines=len(title_layout["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=0.95,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
            safety_ratio=1.0,
        )

        blob_y = y + title_y_offset + title_layout["height"] + 52.0
        if rows > 1:
            blob_y = y + title_y_offset + title_layout["height"] + 24.0

        icon_node = add(
            "svg",
            name=f"platform_icon_{index + 1}",
            x=x + cell_width / 2 - blob_size / 2,
            y=blob_y,
            width=blob_size,
            height=blob_size * 0.92,
            pixel_width=round(blob_size * 4),
            pixel_height=round(blob_size * 0.92 * 4),
        )
        icon_node.text = icon_svg(
            str(item["icon"]),
            accent_color,
            index,
        )

        body_y = blob_y + blob_size * 0.92 + body_top_gap

        textbox(
            body_layout["source_text"],
            x=x + 10.0,
            y=body_y,
            width=cell_width - 20.0,
            height=body_layout["height"],
            font=font_name,
            font_path=str(body_font_path),
            size=body_layout["font_size"],
            min_font_size=max(7.0, body_layout["font_size"] - 2.0),
            color=line_color,
            align="center",
            vertical_align="top",
            bold="true",
            italic="false",
            single_line="false",
            max_lines=len(body_layout["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=1.22,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
            safety_ratio=1.0,
        )

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content



#=======================   slde cam on
def generate_hanging_thank_you_slide_xml(
    title: str = "Cam On",
    subtitle: str = (
        "This is a sample text Insert your desired text here This is a sample text\n"
        "Insert your desired text here Insert your desired text here"
        "Insert your desired text here Insert your desired text here"
    ),
    background_top_left: str = "#F73556",
    background_top_right: str = "#AC2D5F",
    background_bottom_left: str = "#B92E60",
    background_bottom_right: str = "#123064",
    card_color_1: str = "#FF755E",
    card_color_2: str = "#FFA31F",
    card_text_color: str = "#FFFFFF",
    string_color: str = "#111111",
    subtitle_color: str = "#FFF4E6",
) -> str:
    """
    Generate XML for a hanging thank-you slide.

    The layout features a red-to-blue gradient background, black hanging
    strings, individual warm gradient letter cards forming the main title,
    and a centered subtitle beneath the hanging cards.
    """


    letters = [
        character.upper()
        for character in title.strip()
        if not character.isspace()
    ]



    canvas_width = 1600
    canvas_height = 900

    # =====================================================
    # Font helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            ch.lower()
            for ch in name
            if ch.isalnum()
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
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": ["arial"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri"],
            "Aptos": ["aptos"],
            "Arial": ["arial"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(
                    normalized in stem
                    for normalized in normalized_names
                ):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in (
                        "bold",
                        "bd",
                        "semibold",
                        "demi",
                    )
                )
                has_italic = any(
                    token in stem
                    for token in (
                        "italic",
                        "oblique",
                        "it",
                    )
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 8

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(
                key=lambda item: item[0],
                reverse=True,
            )

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        if bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                windows_fonts / "aptos-bold.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                windows_fonts / "aptos.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue

            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        for directory in font_directories():
            try:
                files = directory.rglob("*")
            except OSError:
                continue

            for path in files:
                if path.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
                    continue

                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

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
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
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
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        max_width: float,
        line_spacing: float,
        padding: float = 0.0,
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
            "lines": lines,
            "font_size": font_size,
            "width": max_width,
            "height": len(lines) * line_height + padding,
        }

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best = None

        while current_font_size >= min_font_size:
            layout = layout_text(
                text,
                font_path=font_path,
                font_size=current_font_size,
                max_width=max_width,
                line_spacing=line_spacing,
            )

            too_many_lines = (
                max_lines is not None
                and len(layout["lines"]) > max_lines
            )

            score = (
                max(0.0, layout["height"] - max_height) * 1600
                + max(0, len(layout["lines"]) - (max_lines or 99)) * 1000
                + (preferred_font_size - current_font_size) * 8
            )

            if best is None or score < best["score"]:
                layout["score"] = score
                best = layout

            if layout["height"] <= max_height and not too_many_lines:
                return layout

            break

        return best

    title_font_name = "Arial"
    subtitle_font_name = "Arial"

    letter_font_path = resolve_font_path(
        title_font_name,
        bold=True,
    )
    subtitle_font_path = resolve_font_path(
        subtitle_font_name,
        bold=False,
    )

    # =====================================================
    # Dynamic letter card layout
    # =====================================================

    letter_count = len(letters)

    card_max_width = 150.0
    card_min_width = 78.0
    card_gap = 24.0

    card_width = (
        card_max_width
        if letter_count <= 8
        else max(
            card_min_width,
            (1360.0 - (letter_count - 1) * 14.0) / letter_count,
        )
    )

    if letter_count > 8:
        card_gap = 14.0

    total_cards_width = (
        letter_count * card_width
        + (letter_count - 1) * card_gap
    )

    while total_cards_width > 1350.0 and card_width > card_min_width:
        card_width -= 2.0
        total_cards_width = (
            letter_count * card_width
            + (letter_count - 1) * card_gap
        )

    card_height = min(
        132.0,
        max(92.0, card_width * 0.96),
    )
    card_radius = 10.0

    cards_start_x = canvas_width / 2 - total_cards_width / 2
    cards_base_y = 360.0

    # The reference has alternating hanging cards, so use small vertical
    # offsets while keeping all letters readable.
    y_offsets = [0.0, 32.0, -10.0, 26.0, -2.0, -8.0, 32.0, -10.0]

    letter_font_size = min(
        54.0,
        max(30.0, card_width * 0.42),
    )

    card_layouts: list[dict] = []

    for index, letter in enumerate(letters):
        x = cards_start_x + index * (card_width + card_gap)
        y = cards_base_y + y_offsets[index % len(y_offsets)]

        center_x = x + card_width / 2
        string_top_y = -12.0
        string_bottom_y = y + 6.0

        card_layouts.append(
            {
                "letter": letter,
                "x": x,
                "y": y,
                "width": card_width,
                "height": card_height,
                "center_x": center_x,
                "string_top_y": string_top_y,
                "string_bottom_y": string_bottom_y,
            }
        )

    subtitle_layout = fit_text(
        subtitle.strip(),
        font_path=subtitle_font_path,
        preferred_font_size=20.0,
        min_font_size=20,
        max_width=1000.0,
        max_height=82.0,
        line_spacing=1.15,
        max_lines=3,
    )

    subtitle_x = canvas_width / 2 - subtitle_layout["width"] / 2
    subtitle_y = 608.0

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
        {"background": background_bottom_right},
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

    background_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{background_top_left}"/>
      <stop offset="45%" stop-color="{background_top_right}"/>
      <stop offset="100%" stop-color="{background_bottom_right}"/>
    </linearGradient>
    <radialGradient id="warm" cx="12%" cy="0%" r="62%">
      <stop offset="0%" stop-color="{background_top_left}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="{background_top_left}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="cool" cx="75%" cy="100%" r="56%">
      <stop offset="0%" stop-color="{background_bottom_right}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="{background_bottom_right}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="1600" height="900" fill="url(#bg)"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#warm)"/>
  <rect x="0" y="0" width="1600" height="900" fill="url(#cool)"/>
</svg>
""".strip()

    svg_node = add(
        "svg",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=1600,
        pixel_height=900,
    )
    svg_node.text = background_svg

    def card_svg(
        width: float,
        height: float,
        radius: float,
    ) -> str:
        return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.2f} {height:.2f}">
  <defs>
    <linearGradient id="cardGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{card_color_1}"/>
      <stop offset="100%" stop-color="{card_color_2}"/>
    </linearGradient>
    <filter id="shadow" x="-22%" y="-22%" width="144%" height="144%">
      <feDropShadow dx="0" dy="12" stdDeviation="12" flood-color="#000000" flood-opacity="0.30"/>
    </filter>
  </defs>
  <rect x="0" y="0" width="{width:.2f}" height="{height:.2f}" rx="{radius:.2f}" ry="{radius:.2f}" fill="url(#cardGrad)" filter="url(#shadow)"/>
</svg>
""".strip()

    # Strings are behind cards.
    for card in card_layouts:
        x = card["center_x"]

        add(
            "line",
            x1=x - 4.0,
            y1=card["string_top_y"],
            x2=x - 4.0,
            y2=card["string_bottom_y"],
            color=string_color,
            width=3.0,
        )
        add(
            "line",
            x1=x + 4.0,
            y1=card["string_top_y"],
            x2=x + 4.0,
            y2=card["string_bottom_y"],
            color=string_color,
            width=3.0,
        )

    for card in card_layouts:
        x = card["center_x"]
        pin_y = card["y"] - 6.0

        # Small dark hanging connector above each card.
        add(
            "shape",
            type="circle",
            x=x - 7.0,
            y=pin_y,
            width=14.0,
            height=14.0,
            fill="#0C0C0C",
            line_color="none",
        )

        card_node = add(
            "svg",
            x=card["x"],
            y=card["y"],
            width=card["width"],
            height=card["height"],
            pixel_width=int(card["width"]),
            pixel_height=int(card["height"]),
        )
        card_node.text = card_svg(
            card["width"],
            card["height"],
            card_radius,
        )

        textbox(
            card["letter"],
            x=card["x"],
            y=card["y"] + card["height"] * 0.18,
            width=card["width"],
            height=card["height"] * 0.68,
            font=title_font_name,
            font_path=str(letter_font_path),
            size=letter_font_size,
            min_font_size=max(24.0, letter_font_size - 2.0),
            bold="true",
            color=card_text_color,
            align="center",
            vertical_align="middle",
            single_line="true",
            max_lines=1,
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=0.95,
            safety_ratio=1.0,
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    if subtitle.strip():
        textbox(
            subtitle_layout["source_text"],
            x=subtitle_x,
            y=subtitle_y,
            width=subtitle_layout["width"],
            height=subtitle_layout["height"],
            font=subtitle_font_name,
            font_path=str(subtitle_font_path),
            size=subtitle_layout["font_size"],
            min_font_size=max(9.0, subtitle_layout["font_size"] - 2.0),
            color=subtitle_color,
            align="center",
            vertical_align="middle",
            single_line="false",
            max_lines=len(subtitle_layout["lines"]),
            overflow="clip",
            reflow_on_resize="true",
            line_spacing=1.15,
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

def generate_business_thank_you_slide_xml(
    title: str = "Thank you",
    description: str = (
        "This slide is an editable slide with all your needs. Adapt it with "
        "your needs and it will capture all the audience attention.\n"
        "Capture your audience attention. Download this awesome creatives "
        "and bring your presentation to life, with our creativity."
        
    ),
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1521791136064-7986c2920216"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#111111",
    overlay_color: str = "#000000",
    title_color: str = "#FFFFFF",
    description_color: str = "#111111",
    accent_color: str = "#00D6D9",
    footer_bar_color: str = "#1697AA",
    white_panel_color: str = "#FFFFFF",
) -> str:
    """
    Generate XML for a business thank-you slide.

    The layout features a dark full-width image hero area, a cyan geometric
    outline accent, a large centered thank-you headline, a white description
    panel, and a teal footer bar.
    """



    canvas_width = 1600
    canvas_height = 900

    # =====================================================
    # Font helpers
    # =====================================================

    def normalize_font_name(name: str) -> str:
        return "".join(
            ch.lower()
            for ch in name
            if ch.isalnum()
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
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Times New Roman": ["timesnewroman", "times"],
            "Arial": ["arial"],
            "Garamond": ["garamond"],
            "Arial": ["arial"],
            "Calibri": ["calibri"],
            "Aptos": ["aptos"],
            "Helvetica": ["helvetica", "arial"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(
                font_name,
                [font_name],
            )
        ]

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

                if not any(
                    normalized in stem
                    for normalized in normalized_names
                ):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in (
                        "bold",
                        "bd",
                        "semibold",
                        "demi",
                    )
                )
                has_italic = any(
                    token in stem
                    for token in (
                        "italic",
                        "oblique",
                        "it",
                    )
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(
                key=lambda item: item[0],
                reverse=True,
            )

            for _, path in candidates:
                try:
                    ImageFont.truetype(
                        str(path),
                        12,
                    )
                    return path
                except OSError:
                    continue

        windir = Path(
            os.environ.get(
                "WINDIR",
                "C:/Windows",
            )
        )
        windows_fonts = windir / "Fonts"

        if bold and italic:
            fallback_paths = [
                windows_fonts / "timesbi.ttf",
                windows_fonts / "arialbi.ttf",
                windows_fonts / "arialbi.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "timesbd.ttf",
                windows_fonts / "arialbd.ttf",
                windows_fonts / "arialbd.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "timesi.ttf",
                windows_fonts / "ariali.ttf",
                windows_fonts / "ariali.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "times.ttf",
                windows_fonts / "arial.ttf",
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback_path in fallback_paths:
            if not fallback_path.exists():
                continue

            try:
                ImageFont.truetype(
                    str(fallback_path),
                    12,
                )
                return fallback_path
            except OSError:
                continue

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

                try:
                    ImageFont.truetype(
                        str(path),
                        12,
                    )
                    return path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

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
        lines: list[str] = []

        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()

            if not words:
                lines.append("")
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
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)

        return lines or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        max_width: float,
        line_spacing: float,
        padding: float = 0.0,
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
            "lines": lines,
            "font_size": font_size,
            "width": max_width,
            "height": len(lines) * line_height + padding,
        }

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best = None

        while current_font_size >= min_font_size:
            layout = layout_text(
                text,
                font_path=font_path,
                font_size=current_font_size,
                max_width=max_width,
                line_spacing=line_spacing,
            )

            too_many_lines = (
                max_lines is not None
                and len(layout["lines"]) > max_lines
            )

            score = (
                max(0.0, layout["height"] - max_height) * 1600
                + max(0, len(layout["lines"]) - (max_lines or 99)) * 850
                + (preferred_font_size - current_font_size) * 8
            )

            if best is None or score < best["score"]:
                layout["score"] = score
                best = layout

            if layout["height"] <= max_height and not too_many_lines:
                return layout

            break

        return best

    title_font_name = "Arial"
    description_font_name = "Arial"

    title_font_path = resolve_font_path(
        title_font_name,
        bold=True,
    )
    description_font_path = resolve_font_path(
        description_font_name,
    )

    hero_height = 542.0
    white_panel_y = hero_height
    footer_height = 28.0
    white_panel_height = canvas_height - white_panel_y - footer_height

    title_box_width = 680.0

    title_layout = fit_text(
        title.strip(),
        font_path=title_font_path,
        preferred_font_size=52.0,
        min_font_size=28.0,
        max_width=title_box_width,
        max_height=110.0,
        line_spacing=0.95,
        max_lines=2,
    )

    description_layout = fit_text(
        description.strip(),
        font_path=description_font_path,
        preferred_font_size=22.0,
        min_font_size=20,
        max_width=1320.0,
        max_height=180,
        line_spacing=1.18,
        max_lines=4,
    )

    title_x = 568.0
    title_y = 232.0

    description_x = canvas_width / 2 - description_layout["width"] / 2
    description_y = white_panel_y + (white_panel_height - description_layout["height"]) / 2 - 6.0

    accent_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="340" height="340" viewBox="0 0 340 340">
  <path d="M156 8 L28 136 L156 264" fill="none" stroke="{accent_color}" stroke-width="8" stroke-linecap="square" stroke-linejoin="miter"/>
  <path d="M199 8 L71 136 L199 264" fill="none" stroke="{accent_color}" stroke-width="8" stroke-linecap="square" stroke-linejoin="miter"/>
  <path d="M156 264 L232 188" fill="none" stroke="{accent_color}" stroke-width="8" stroke-linecap="square"/>
  <path d="M199 264 L275 188" fill="none" stroke="{accent_color}" stroke-width="8" stroke-linecap="square"/>
  <path d="M156 8 L232 84" fill="none" stroke="{accent_color}" stroke-width="8" stroke-linecap="square"/>
  <path d="M199 8 L275 84" fill="none" stroke="{accent_color}" stroke-width="8" stroke-linecap="square"/>
</svg>
""".strip()

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
        x=0,
        y=0,
        width=canvas_width,
        height=hero_height,
        fit="cover",
        crop_x=0.48,
        crop_y=0.42,
    )

    overlay_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="542" viewBox="0 0 1600 542">
  <rect x="0" y="0" width="1600" height="542" fill="{overlay_color}" opacity="0.68"/>
</svg>
""".strip()

    overlay_node = add(
        "svg",
        x=0,
        y=0,
        width=canvas_width,
        height=hero_height,
        pixel_width=1600,
        pixel_height=542,
    )
    overlay_node.text = overlay_svg

    svg_node = add(
        "svg",
        x=295,
        y=102,
        width=330,
        height=330,
        pixel_width=340,
        pixel_height=340,
    )
    svg_node.text = accent_svg

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_box_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(24.0, title_layout["font_size"] - 2.0),
        bold="true",
        color=title_color,
        align="left",
        vertical_align="middle",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.95,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    add(
        "shape",
        type="rectangle",
        x=0,
        y=white_panel_y,
        width=canvas_width,
        height=white_panel_height,
        fill=white_panel_color,
        line_color="none",
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
        min_font_size=max(8.5, description_layout["font_size"] - 2.0),
        color=description_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(description_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.18,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    add(
        "shape",
        type="rectangle",
        x=0,
        y=white_panel_y + white_panel_height,
        width=canvas_width,
        height=footer_height,
        fill=footer_bar_color,
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

def generate_dark_gold_thank_you_slide_xml(
    title: str = "THANK YOU THANK YOU THANK YOU",
    subtitle: str = (
        "Lorem ipsum dolor sit amet consectetur adipiscing elit maecenas "
        "porttitor congue massa fusce posuere magna sed pulvinar ultricies "
        "purus lectus malesuada libero sit amet."
    ),
    phone_text: str = "(123) 456-7890",
    email_text: str = "david.langford@email.com",
    website_text: str = "davidlangford.com",
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1486406146926-c627a92ad1ab"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#050505",
    panel_color: str = "#000000",
    title_color: str = "#F0B400",
    subtitle_color: str = "#FFFFFF",
    contact_color: str = "#F0B400",
    divider_color: str = "#A37A10",
    accent_color: str = "#7A6107",
) -> str:
    """
    Generate XML for a dark thank-you slide.

    The layout features a dimmed full-slide background image, a centered dark
    content panel, a geometric line accent, a large centered thank-you title,
    a supporting subtitle, a divider line, and three contact items aligned in
    a single row near the bottom of the panel.
    """

 

    canvas_width = 1600
    canvas_height = 900

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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
        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(font_name: str, bold: bool = False, italic: bool = False) -> Path:
        aliases = {
            "Arial": ["arial", "helvetica"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri", "aptos", "arial"],
            "Aptos": ["aptos", "calibri", "arial"],
            "Arial": ["arial", "times"],
            "Times New Roman": ["timesnewroman", "times", "arial"],
        }
        normalized_names = [normalize_font_name(name) for name in aliases.get(font_name, [font_name])]
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
                if not any(name in stem for name in normalized_names):
                    continue

                score = 70
                if stem in normalized_names:
                    score += 30

                has_bold = any(token in stem for token in ("bold", "bd", "semibold", "demi"))
                has_italic = any(token in stem for token in ("italic", "oblique", "it"))

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"
        if bold and italic:
            fallback_paths = [
                windows_fonts / "arialbi.ttf",
                windows_fonts / "calibriz.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "arialbd.ttf",
                windows_fonts / "calibrib.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "ariali.ttf",
                windows_fonts / "calibrii.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "arial.ttf",
                windows_fonts / "calibri.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for fallback in fallback_paths:
            if fallback.exists():
                try:
                    ImageFont.truetype(str(fallback), 12)
                    return fallback
                except OSError:
                    pass

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    canvas_dpi = 120.0

    def pt_to_canvas(size_pt: float) -> float:
        return size_pt * canvas_dpi / 72.0

    def load_font(font_path: Path, size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(font_path), max(1, round(pt_to_canvas(size_pt))))

    def measure_text_width(text: str, font_path: Path, size_pt: float) -> float:
        font = load_font(font_path, size_pt)
        if hasattr(font, "getlength"):
            return float(font.getlength(text))
        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(font_path: Path, size_pt: float, line_spacing: float) -> float:
        font = load_font(font_path, size_pt)
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

    def wrap_text(text: str, font_path: Path, size_pt: float, max_width: float) -> list[str]:
        lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current = ""
            for word in words:
                candidate = word if not current else f"{current} {word}"
                if not current or measure_text_width(candidate, font_path, size_pt) <= max_width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        max_width: float,
        line_spacing: float,
    ) -> dict:
        lines = wrap_text(text, font_path, font_size, max_width)
        line_height = measure_line_height(font_path, font_size, line_spacing)
        return {
            "source_text": text,
            "lines": lines,
            "font_size": font_size,
            "width": max_width,
            "height": len(lines) * line_height,
        }

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current = preferred_font_size
        best = None
        while current >= min_font_size:
            layout = layout_text(
                text,
                font_path=font_path,
                font_size=current,
                max_width=max_width,
                line_spacing=line_spacing,
            )
            too_many_lines = max_lines is not None and len(layout["lines"]) > max_lines
            score = (
                max(0.0, layout["height"] - max_height) * 2000
                + max(0, len(layout["lines"]) - (max_lines or 99)) * 1500
                + (preferred_font_size - current) * 8
            )
            if best is None or score < best["score"]:
                layout["score"] = score
                best = layout
            if layout["height"] <= max_height and not too_many_lines:
                return layout
            break
        return best

    title_font_name = "Arial"
    subtitle_font_name = "Arial"
    contact_font_name = "Arial"

    title_font_path = resolve_font_path(title_font_name, bold=True)
    subtitle_font_path = resolve_font_path(subtitle_font_name, bold=False)
    contact_font_path = resolve_font_path(contact_font_name, bold=False)

    panel_x = 102.0
    panel_y = 67.0
    panel_width = 1396.0
    panel_height = 618.0

    divider_y = panel_y + 442.0
    contact_y = panel_y + 500.0
    icon_size = 44.0

    # Keep the title/subtitle as one vertically managed group.  This lets the
    # group move into available space before either textbox is forced smaller.
    upper_content_top = panel_y + 155.0
    upper_content_bottom = divider_y - 34.0
    upper_content_height = upper_content_bottom - upper_content_top
    title_subtitle_gap = 30.0

    # Keep the requested sizes.  If the group is too tall, the renderer clips
    # the text instead of silently reducing its font size.
    title_preferred = 46.0
    subtitle_preferred = 20.0
    for _ in range(40 if AUTO_SHRINK_TEXT else 1):
        title_layout = fit_text(
            title.strip().upper(),
            font_path=title_font_path,
            preferred_font_size=title_preferred,
            min_font_size=24.0,
            max_width=1080.0,
            max_height=128.0,
            line_spacing=0.95,
            max_lines=1,
        )
        subtitle_layout = fit_text(
            subtitle.strip(),
            font_path=subtitle_font_path,
            preferred_font_size=subtitle_preferred,
            min_font_size=12.0,
            max_width=760.0,
            max_height=92.0,
            line_spacing=1.15,
            max_lines=2,
        )
        group_height = title_layout["height"] + title_subtitle_gap + subtitle_layout["height"]
        if group_height <= upper_content_height:
            break
        if AUTO_SHRINK_TEXT and subtitle_preferred > 12.0:
            subtitle_preferred = max(12.0, subtitle_preferred - 1.0)
        elif AUTO_SHRINK_TEXT and title_preferred > 24.0:
            title_preferred = max(24.0, title_preferred - 1.0)

    group_height = title_layout["height"] + title_subtitle_gap + subtitle_layout["height"]

    title_box_width = 1080.0
    title_x = panel_x + panel_width / 2 - title_box_width / 2
    title_y = upper_content_top + max(0.0, (upper_content_height - group_height) / 2.0)

    subtitle_x = panel_x + panel_width / 2 - subtitle_layout["width"] / 2
    subtitle_y = title_y + title_layout["height"] + title_subtitle_gap

    divider_x1 = panel_x + 136.0
    divider_x2 = panel_x + panel_width - 136.0

    contact_specs = [
        {"icon": "phone", "text": phone_text.strip(), "max_width": 185.0},
        {"icon": "email", "text": email_text.strip(), "max_width": 290.0},
        {"icon": "website", "text": website_text.strip(), "max_width": 210.0},
    ]

    contact_layouts: list[dict] = []
    for spec in contact_specs:
        text_layout = fit_text(
            spec["text"],
            font_path=contact_font_path,
            preferred_font_size=12.0,
            min_font_size=8.0,
            max_width=spec["max_width"],
            max_height=18.0,
            line_spacing=1.0,
            max_lines=1,
        )
        contact_layouts.append(
            {
                "icon": spec["icon"],
                "text_layout": text_layout,
            }
        )

    contact_gap = 72.0
    text_icon_gap = 20.0
    contact_total_width = sum(
        icon_size + text_icon_gap + item["text_layout"]["width"]
        for item in contact_layouts
    ) + contact_gap * (len(contact_layouts) - 1)
    contact_cursor_x = panel_x + (panel_width - contact_total_width) / 2.0
    for item in contact_layouts:
        item["icon_x"] = contact_cursor_x
        item["text_x"] = contact_cursor_x + icon_size + text_icon_gap
        contact_cursor_x += icon_size + text_icon_gap + item["text_layout"]["width"] + contact_gap

    overlay_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <rect x="0" y="0" width="1600" height="900" fill="#000000" opacity="0.60"/>
  <radialGradient id="vignette" cx="50%" cy="35%" r="80%">
    <stop offset="0%" stop-color="#000000" stop-opacity="0.08"/>
    <stop offset="100%" stop-color="#000000" stop-opacity="0.48"/>
  </radialGradient>
  <rect x="0" y="0" width="1600" height="900" fill="url(#vignette)"/>
</svg>
""".strip()

    corner_svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <path d="M0 670 C80 676 131 721 160 774 C184 817 223 866 280 900 L0 900 Z"
        fill="{accent_color}" opacity="0.82"/>
  <path d="M1513 0 C1513 58 1548 90 1600 99 L1600 0 Z"
        fill="{accent_color}" opacity="0.82"/>
</svg>
""".strip()

    def icon_svg(kind: str) -> str:
        if kind == "phone":
            path = f"""
<path d="M39 50 C49 66 62 78 78 87 C83 90 87 89 91 85 L97 76 C100 72 99 67 95 64 L81 55 C77 52 73 52 69 56 L65 60 C56 53 47 44 40 34 L44 30 C48 27 49 22 46 18 L37 5 C34 1 29 0 25 4 L15 13 C11 17 10 22 12 26 C17 34 25 43 39 50 Z"
      fill="none" stroke="{contact_color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
""".strip()
        elif kind == "email":
            path = f"""
<rect x="18" y="27" width="84" height="58" rx="7" fill="none" stroke="{contact_color}" stroke-width="5"/>
<path d="M22 33 L60 61 L98 33" fill="none" stroke="{contact_color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
""".strip()
        else:
            path = f"""
<circle cx="60" cy="60" r="42" fill="none" stroke="{contact_color}" stroke-width="5"/>
<path d="M18 60 H102" fill="none" stroke="{contact_color}" stroke-width="5" stroke-linecap="round"/>
<path d="M60 19 C47 35 42 48 42 60 C42 72 47 86 60 101 C73 86 78 72 78 60 C78 48 73 35 60 19 Z"
      fill="none" stroke="{contact_color}" stroke-width="5" stroke-linejoin="round"/>
""".strip()

        return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">
  <circle cx="60" cy="60" r="43" fill="none" stroke="{contact_color}" stroke-width="3"/>
  {path}
</svg>
""".strip()

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
    slide = ET.SubElement(presentation, "slide", {"background": background_color})

    def add(tag: str, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {key: str(value) for key, value in attrs.items() if value is not None},
        )

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    add(
        "image",
        src=image_url,
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fit="cover",
        crop_x=0.50,
        crop_y=0.36,
    )

    overlay_node = add(
        "svg",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=1600,
        pixel_height=900,
    )
    overlay_node.text = overlay_svg

    corner_node = add(
        "svg",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        pixel_width=1600,
        pixel_height=900,
    )
    corner_node.text = corner_svg

    add(
        "shape",
        type="rectangle",
        x=panel_x,
        y=panel_y,
        width=panel_width,
        height=panel_height,
        fill=panel_color,
        line_color="none",
    )

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_box_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=24.0,
        bold="true",
        color=title_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.95,
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
        width=subtitle_layout["width"],
        height=subtitle_layout["height"],
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=subtitle_layout["font_size"],
        min_font_size=12.0,
        color=subtitle_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(subtitle_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.15,
        safety_ratio=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    add(
        "line",
        x1=divider_x1,
        y1=divider_y,
        x2=divider_x2,
        y2=divider_y,
        color=divider_color,
        width=1.1,
    )

    for item in contact_layouts:
        icon_x = item["icon_x"]
        text_x = item["text_x"]

        icon_node = add(
            "svg",
            x=icon_x,
            y=contact_y - icon_size / 2,
            width=icon_size,
            height=icon_size,
            pixel_width=120,
            pixel_height=120,
        )
        icon_node.text = icon_svg(item["icon"])

        textbox(
            item["text_layout"]["source_text"],
            x=text_x,
            y=contact_y - item["text_layout"]["height"] / 2,
            width=item["text_layout"]["width"],
            height=item["text_layout"]["height"],
            font=contact_font_name,
            font_path=str(contact_font_path),
            size=item["text_layout"]["font_size"],
            min_font_size=max(7.0, item["text_layout"]["font_size"] - 2.0),
            color=contact_color,
            align="left",
            vertical_align="middle",
            single_line="false",
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

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content

def generate_paper_flight_thank_you_slide_xml(
    title: str = "Cảm On mọi người đã lắng nghe",
    background_color: str = "#F6F6F7",
    title_color: str = "#6A7193",
    cloud_color: str = "#E9EBF4",
    cloud_shadow_color: str = "#C9CCDD",
    mountain_color: str = "#E1E1E1",
    mountain_dark_color: str = "#D2D2D2",
    path_color: str = "#BCC0CF",
    orange_color: str = "#F2A212",
    envelope_color: str = "#75603C",
    envelope_shadow_color: str = "#D08407",
    paper_plane_color: str = "#D4D6DB",
    paper_plane_dark_color: str = "#9FA2AA",
    star_color: str = "#C4C7D1",
) -> str:
    """
    Generate XML for an illustrated thank-you slide.

    The slide uses separated decorative items such as mountains, clouds,
    flight paths, stars, dots, envelopes, and a paper plane. The envelope
    and paper plane keep one original vector design and are only rotated
    and repositioned when reused.
    """



    canvas_width = 1600
    canvas_height = 900

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

        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(
        font_name: str,
        bold: bool = False,
        italic: bool = False,
    ) -> Path:
        aliases = {
            "Arial": ["arial"],
            "Helvetica": ["helvetica", "arial"],
            "Calibri": ["calibri"],
            "Aptos": ["aptos"],
            "Arial": ["arial"],
            "Times New Roman": ["timesnewroman", "times"],
        }

        normalized_names = [
            normalize_font_name(name)
            for name in aliases.get(font_name, [font_name])
        ]

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

                if not any(normalized in stem for normalized in normalized_names):
                    continue

                score = 70

                if stem in normalized_names:
                    score += 30

                has_bold = any(
                    token in stem
                    for token in ("bold", "bd", "semibold", "demi")
                )
                has_italic = any(
                    token in stem
                    for token in ("italic", "oblique", "it")
                )

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 7

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 5

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)

            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windir = Path(os.environ.get("WINDIR", "C:/Windows"))
        windows_fonts = windir / "Fonts"

        fallback_paths = []
        if bold:
            fallback_paths.extend(
                [
                    windows_fonts / "arialbd.ttf",
                    windows_fonts / "calibrib.ttf",
                    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
                ]
            )
        else:
            fallback_paths.extend(
                [
                    windows_fonts / "arial.ttf",
                    windows_fonts / "calibri.ttf",
                    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                ]
            )

        for fallback_path in fallback_paths:
            if fallback_path.exists():
                try:
                    ImageFont.truetype(str(fallback_path), 12)
                    return fallback_path
                except OSError:
                    continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

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
        words = text.split()

        if not words:
            return [""]

        lines: list[str] = []
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"

            if (
                not current
                or measure_text_width(candidate, font_path, font_size_pt) <= max_width
            ):
                current = candidate
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines or [""]

    def layout_text(
        text: str,
        *,
        font_path: Path,
        font_size: float,
        max_width: float,
        line_spacing: float,
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
            "lines": lines,
            "font_size": font_size,
            "width": max_width,
            "height": len(lines) * line_height,
        }

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best = None

        while current_font_size >= min_font_size:
            layout = layout_text(
                text,
                font_path=font_path,
                font_size=current_font_size,
                max_width=max_width,
                line_spacing=line_spacing,
            )

            too_many_lines = (
                max_lines is not None
                and len(layout["lines"]) > max_lines
            )

            score = (
                max(0.0, layout["height"] - max_height) * 1700
                + max(0, len(layout["lines"]) - (max_lines or 99)) * 1100
                + (preferred_font_size - current_font_size) * 8
            )

            if best is None or score < best["score"]:
                layout["score"] = score
                best = layout

            if layout["height"] <= max_height and not too_many_lines:
                return layout

            break

        return best

    title_font_name = "Arial"
    title_font_path = resolve_font_path(
        title_font_name,
        bold=True,
    )

    title_box_width = 1040.0

    title_layout = fit_text(
        title.strip().upper(),
        font_path=title_font_path,
        preferred_font_size=64.0,
        min_font_size=30.0,
        max_width=title_box_width,
        max_height=130.0,
        line_spacing=0.95,
        max_lines=2,
    )

    title_x = canvas_width / 2 - title_box_width / 2
    title_underline_y = 798.0
    title_to_line_gap = 18.0
    title_y = title_underline_y - title_layout["height"] - title_to_line_gap

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

    def svg_node(
        name: str,
        x: float,
        y: float,
        width: float,
        height: float,
        svg_body: str,
        pixel_scale: float = 4.0,
    ) -> None:
        node = add(
            "svg",
            name=name,
            x=x,
            y=y,
            width=width,
            height=height,
            pixel_width=max(1, round(width * pixel_scale)),
            pixel_height=max(1, round(height * pixel_scale)),
        )
        node.text = svg_body.strip()

    def simple_svg(
        width: float,
        height: float,
        content: str,
    ) -> str:
        return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}">
  {content}
</svg>
""".strip()

    def asset_svg(
        content_width: float,
        content_height: float,
        content: str,
    ) -> str:
        return simple_svg(content_width, content_height, content)

    def add_asset_instance(
        name: str,
        x: float,
        y: float,
        width: float,
        height: float,
        rotation: float,
        asset_width: float,
        asset_height: float,
        asset_content: str,
        pixel_scale: float,
        inner_scale: float = 0.82,
    ) -> None:
        # Keep the original asset shape. The wrapper box is intentionally
        # larger than the visible asset so stroke, shadow, and rotated corners
        # are not clipped by the SVG boundary.
        uniform_scale = min(
            width / asset_width,
            height / asset_height,
        ) * inner_scale

        wrapped = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}" overflow="visible">
  <g transform="translate({width / 2:g} {height / 2:g}) rotate({rotation:g}) scale({uniform_scale:g}) translate({-asset_width / 2:g} {-asset_height / 2:g})">
    {asset_content}
  </g>
</svg>
""".strip()
        svg_node(
            name,
            x,
            y,
            width,
            height,
            wrapped,
            pixel_scale=pixel_scale,
        )

    def add_cloud(
        name: str,
        x: float,
        y: float,
        width: float,
        height: float,
        fill: str,
        opacity: float,
    ) -> None:
        content = f"""
<path d="
  M 0 {height:g}
  C {width * 0.05:g} {height * 0.58:g} {width * 0.24:g} {height * 0.44:g} {width * 0.39:g} {height * 0.52:g}
  C {width * 0.48:g} {height * 0.12:g} {width * 0.82:g} {height * 0.09:g} {width * 0.91:g} {height * 0.56:g}
  C {width * 1.04:g} {height * 0.57:g} {width * 1.10:g} {height * 0.75:g} {width:g} {height:g}
  Z"
  fill="{fill}"
  opacity="{opacity:g}"
/>
"""
        svg_node(
            name,
            x,
            y,
            width,
            height,
            simple_svg(width, height, content),
            pixel_scale=4.0,
        )

    def add_star(
        name: str,
        center_x: float,
        center_y: float,
        size: float,
        opacity: float,
    ) -> None:
        width = size
        height = size
        content = f"""
<path d="
  M {size * 0.5:g} 0
  L {size * 0.62:g} {size * 0.38:g}
  L {size:g} {size * 0.5:g}
  L {size * 0.62:g} {size * 0.62:g}
  L {size * 0.5:g} {size:g}
  L {size * 0.38:g} {size * 0.62:g}
  L 0 {size * 0.5:g}
  L {size * 0.38:g} {size * 0.38:g}
  Z"
  fill="{star_color}"
  opacity="{opacity:g}"
/>
"""
        svg_node(
            name,
            center_x - width / 2,
            center_y - height / 2,
            width,
            height,
            simple_svg(width, height, content),
            pixel_scale=4.5,
        )

    def add_dot(
        name: str,
        center_x: float,
        center_y: float,
        radius: float,
        opacity: float,
    ) -> None:
        add(
            "shape",
            name=name,
            type="circle",
            x=center_x - radius,
            y=center_y - radius,
            width=radius * 2,
            height=radius * 2,
            fill=orange_color,
            line_color="none",
            opacity=opacity,
        )

    def add_line_segment(
        name: str,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        width: float,
        opacity: float,
    ) -> None:
        add(
            "line",
            name=name,
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            color=title_color,
            width=width,
            opacity=opacity,
        )

    def add_path_svg(
        name: str,
        x: float,
        y: float,
        width: float,
        height: float,
        path_d: str,
        stroke_width: float,
    ) -> None:
        content = f"""
<path d="{path_d}"
  fill="none"
  stroke="{path_color}"
  stroke-width="{stroke_width:g}"
  stroke-dasharray="16 18"
  stroke-linecap="round"
  opacity="0.96"
/>
"""
        svg_node(
            name,
            x,
            y,
            width,
            height,
            simple_svg(width, height, content),
            pixel_scale=4.0,
        )

    envelope_asset_width = 160.0
    envelope_asset_height = 110.0
    envelope_asset_content = f"""
<defs>
  <filter id="shadow_env" x="-35%" y="-35%" width="170%" height="170%">
    <feDropShadow dx="0" dy="3" stdDeviation="2.5" flood-color="#000000" flood-opacity="0.12"/>
  </filter>
  <linearGradient id="frontGrad_env" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#FFD98B"/>
    <stop offset="58%" stop-color="{envelope_color}"/>
    <stop offset="100%" stop-color="{orange_color}"/>
  </linearGradient>
</defs>
<g filter="url(#shadow_env)">
  <g transform="translate(20 18)">
    <rect x="0" y="8" width="120" height="64" rx="7"
          fill="url(#frontGrad_env)"
          stroke="{envelope_shadow_color}" stroke-width="2.2"/>
    <path d="M 2 14 L 60 43 L 118 14"
          fill="none" stroke="{envelope_shadow_color}" stroke-width="2.4"
          stroke-linejoin="round"/>
    <path d="M 2 68 L 40 38"
          fill="none" stroke="{envelope_shadow_color}" stroke-width="2"/>
    <path d="M 118 68 L 80 38"
          fill="none" stroke="{envelope_shadow_color}" stroke-width="2"/>
    <path d="M 22 8 L 60 41 L 98 8"
          fill="#F7B32F" stroke="{envelope_shadow_color}" stroke-width="1.5"/>
    <path d="M 60 41 L 28 12"
          fill="none" stroke="#E8A323" stroke-width="1.4"/>
    <path d="M 60 41 L 92 12"
          fill="none" stroke="#E8A323" stroke-width="1.4"/>
  </g>
</g>
""".strip()

    plane_asset_width = 145.0
    plane_asset_height = 86.0
    plane_asset_content = f"""
<defs>
  <filter id="shadow_plane" x="-20%" y="-20%" width="150%" height="150%">
    <feDropShadow dx="0" dy="4" stdDeviation="2.8" flood-color="#000000" flood-opacity="0.12"/>
  </filter>
  <linearGradient id="planeGrad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#F0F1F4"/>
    <stop offset="100%" stop-color="{paper_plane_dark_color}"/>
  </linearGradient>
</defs>
<g filter="url(#shadow_plane)">
  <path d="M 2 {plane_asset_height * 0.38:g} L {plane_asset_width:g} 2 L {plane_asset_width * 0.42:g} {plane_asset_height:g} Z" fill="url(#planeGrad)"/>
  <path d="M {plane_asset_width * 0.42:g} {plane_asset_height:g} L {plane_asset_width * 0.49:g} {plane_asset_height * 0.46:g} L {plane_asset_width:g} 2 Z" fill="{paper_plane_dark_color}" opacity="0.78"/>
  <path d="M 2 {plane_asset_height * 0.38:g} L {plane_asset_width * 0.49:g} {plane_asset_height * 0.46:g} L {plane_asset_width * 0.42:g} {plane_asset_height:g} Z" fill="#DDE0E5"/>
  <path d="M {plane_asset_width * 0.49:g} {plane_asset_height * 0.46:g} L {plane_asset_width * 0.22:g} {plane_asset_height * 0.66:g} L {plane_asset_width * 0.42:g} {plane_asset_height:g} Z" fill="#A8ABB3" opacity="0.84"/>
  <path d="M {plane_asset_width * 0.49:g} {plane_asset_height * 0.46:g} L {plane_asset_width * 0.81:g} {plane_asset_height * 0.20:g}" fill="none" stroke="#B5B8BF" stroke-width="1.8"/>
</g>
""".strip()

    add(
        "shape",
        name="background",
        type="rectangle",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    svg_node(
        "mountain_main",
        100,
        610,
        1400,
        170,
        simple_svg(
            1400,
            170,
            f"""
<path d="M0 150 C98 98 154 24 240 18 C332 12 411 94 500 110 C612 130 695 96 778 120 C880 150 918 116 995 74 C1073 31 1132 -2 1217 16 C1295 32 1338 103 1400 148 L1400 170 L0 170 Z"
      fill="{mountain_color}" opacity="0.96"/>
""",
        ),
        pixel_scale=4.0,
    )

    svg_node(
        "mountain_dark",
        600,
        670,
        530,
        110,
        simple_svg(
            530,
            110,
            f"""
<path d="M0 110 C82 62 121 14 188 0 C250 -13 316 35 390 61 C439 79 477 92 530 83 L530 110 Z"
      fill="{mountain_dark_color}" opacity="0.75"/>
""",
        ),
        pixel_scale=4.0,
    )

    add_cloud("cloud_left", 270, 345, 255, 75, cloud_shadow_color, 0.92)
    add_cloud("cloud_center", 490, 220, 275, 110, cloud_color, 0.95)
    add_cloud("cloud_right", 1140, 362, 225, 70, cloud_color, 0.85)
    add_cloud("cloud_right_small", 1030, 360, 140, 52, cloud_color, 0.65)

    add_path_svg(
        "path_top",
        450,
        155,
        930,
        330,
        "M48 252 C-10 187 103 126 168 160 C232 194 156 308 84 277 C8 244 31 162 117 192 C214 227 241 173 255 100 C276 6 352 6 443 45 C564 97 604 151 722 142 C790 137 840 112 872 84 C888 70 899 53 908 38",
        5,
    )

    add_path_svg(
        "path_bottom",
        505,
        470,
        600,
        170,
        "M0 0 C62 77 182 111 304 92 C409 76 484 95 550 170",
        5,
    )

    add_asset_instance(
        "envelope_left",
        510,
        388,
        166,
        118,
        12,
        envelope_asset_width,
        envelope_asset_height,
        envelope_asset_content,
        pixel_scale=7.0,
        inner_scale=0.96,
    )

    add_asset_instance(
        "envelope_right",
        988,
        342,
        136,
        96,
        -8,
        envelope_asset_width,
        envelope_asset_height,
        envelope_asset_content,
        pixel_scale=7.0,
        inner_scale=0.94,
    )

    add_asset_instance(
        "paper_plane",
        1294,
        108,
        170,
        102,
        -15,
        plane_asset_width,
        plane_asset_height,
        plane_asset_content,
        pixel_scale=7.5,
        inner_scale=0.90,
    )

    add_star("star_left", 190, 520, 92, 0.78)
    add_star("star_top", 925, 165, 72, 0.70)
    add_star("star_right", 1158, 592, 84, 0.72)

    for dot in [
        ("dot_01", 338, 275, 7, 0.86),
        ("dot_02", 420, 470, 6, 0.94),
        ("dot_03", 500, 305, 5, 0.95),
        ("dot_04", 710, 572, 13, 0.90),
        ("dot_05", 862, 156, 13, 0.96),
        ("dot_06", 1037, 435, 9, 0.95),
        ("dot_07", 1224, 362, 8, 0.88),
        ("dot_08", 1398, 435, 8, 0.94),
        ("dot_09", 1481, 584, 9, 0.96),
        ("dot_10", 776, 362, 12, 0.84),
        ("dot_11", 984, 552, 12, 0.95),
    ]:
        add_dot(*dot)

    add_line_segment("underline_1", 226, title_underline_y, 958, title_underline_y, 6, 1.0)
    add_line_segment("underline_2", 1018, title_underline_y, 1458, title_underline_y, 6, 1.0)
    add_line_segment("underline_3", 902, 830, 1296, 830, 6, 0.86)
    add_line_segment("underline_4", 674, 860, 890, 860, 6, 0.76)
    add_line_segment("underline_5", 968, 860, 1060, 860, 6, 0.76)

    textbox(
        title_layout["source_text"],
        x=title_x,
        y=title_y,
        width=title_box_width,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=max(24.0, title_layout["font_size"] - 2.0),
        bold="true",
        color=title_color,
        align="center",
        vertical_align="middle",
        single_line="false",
        max_lines=len(title_layout["lines"]),
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.95,
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

def generate_closing_thank_you_memorial_slide_xml(
    closing_statement: str = "Write your closing statement",
    title: str = "Cảm ơn quí vị đã lắng nghe",
    subtitle: str = "Briefly elaborate on what you want to discuss. Briefly elaborate on what you want to discuss. Briefly elaborate on what you want to discuss.",
    image_url: str = (
        "https://images.unsplash.com/"
        "photo-1500530855697-b586d89ba3ee"
        "?q=85&w=1600&auto=format&fit=crop"
    ),
    background_color: str = "#DDEEF2",
    top_band_color: str = "#E5CAC3",
    title_band_color: str = "#DDEEF2",
    bottom_band_color: str = "#E5CAC3",
    closing_statement_color: str = "#111111",
    title_color: str = "#050505",
    subtitle_color: str = "#111111",
    image_overlay_color: str = "#FFFFFF",
) -> str:
    """
    Generate XML for a memorial-style closing thank-you slide.

    The layout uses a pale blue outer background, a centered grayscale-style
    landscape image, a narrow closing-statement band, a large blue title band,
    and a small subtitle band below it. Text is kept as source text with
    reflow enabled so it can adapt when edited.
    """

    if not closing_statement.strip():
        closing_statement = "Write your closing statement"
    if not title.strip():
        title = "Thank you"
    if not subtitle.strip():
        subtitle = "Briefly elaborate on what you want to discuss."

    canvas_width = 1600
    canvas_height = 900
    canvas_dpi = 120.0

    def normalize_font_name(name: str) -> str:
        return "".join(ch.lower() for ch in name if ch.isalnum())

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
        return [directory for directory in directories if directory.exists()]

    def resolve_font_path(font_name: str, bold: bool = False, italic: bool = False) -> Path:
        aliases = {
            "Times New Roman": ["timesnewroman", "times", "arial"],
            "Arial": ["arial", "timesnewroman", "times"],
            "Arial": ["arial", "calibri", "aptos"],
            "Calibri": ["calibri", "arial", "aptos"],
        }
        normalized_names = [normalize_font_name(item) for item in aliases.get(font_name, [font_name])]
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
                if not any(name in stem for name in normalized_names):
                    continue

                score = 80 if any(name == stem for name in normalized_names) else 58
                has_bold = any(token in stem for token in ("bold", "bd", "semibold", "demi"))
                has_italic = any(token in stem for token in ("italic", "oblique", "it"))

                if bold and has_bold:
                    score += 20
                elif bold:
                    score -= 8
                elif has_bold:
                    score -= 6

                if italic and has_italic:
                    score += 18
                elif italic:
                    score -= 8
                elif has_italic:
                    score -= 4

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, path in candidates:
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    continue

        windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        if bold and italic:
            fallback_paths = [
                windows_fonts / "timesbi.ttf",
                windows_fonts / "arialbi.ttf",
                windows_fonts / "arialbi.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"),
            ]
        elif italic:
            fallback_paths = [
                windows_fonts / "timesi.ttf",
                windows_fonts / "ariali.ttf",
                windows_fonts / "ariali.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
            ]
        elif bold:
            fallback_paths = [
                windows_fonts / "timesbd.ttf",
                windows_fonts / "arialbd.ttf",
                windows_fonts / "arialbd.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ]
        else:
            fallback_paths = [
                windows_fonts / "times.ttf",
                windows_fonts / "arial.ttf",
                windows_fonts / "arial.ttf",
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]

        for path in fallback_paths:
            if not path.exists():
                continue
            try:
                ImageFont.truetype(str(path), 12)
                return path
            except OSError:
                continue

        return _resolve_font_fallback_path(bold=bold, italic=italic)

    def pt_to_canvas(point_size: float) -> float:
        return point_size * canvas_dpi / 72.0

    def load_font(font_path: Path, font_size_pt: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            max(1, round(pt_to_canvas(font_size_pt))),
        )

    def measure_text_width(text: str, font_path: Path, font_size_pt: float) -> float:
        font = load_font(font_path, font_size_pt)
        if hasattr(font, "getlength"):
            return float(font.getlength(text))
        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def measure_line_height(font_path: Path, font_size_pt: float, line_spacing: float) -> float:
        font = load_font(font_path, font_size_pt)
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

    def wrap_text(text: str, font_path: Path, font_size_pt: float, max_width: float) -> list[str]:
        def split_long_word(word: str) -> list[str]:
            chunks: list[str] = []
            current_chunk = ""
            for character in word:
                candidate = current_chunk + character
                if (
                    current_chunk
                    and measure_text_width(candidate, font_path, font_size_pt) > max_width
                ):
                    chunks.append(current_chunk)
                    current_chunk = character
                else:
                    current_chunk = candidate
            return chunks + [current_chunk] if current_chunk else chunks or [word]

        lines: list[str] = []
        for paragraph in text.splitlines() or [text]:
            words = paragraph.split()
            if not words:
                lines.append("")
                continue

            current = ""
            for word in words:
                if measure_text_width(word, font_path, font_size_pt) > max_width:
                    if current:
                        lines.append(current)
                        current = ""
                    chunks = split_long_word(word)
                    lines.extend(chunks[:-1])
                    current = chunks[-1]
                    continue

                candidate = word if not current else f"{current} {word}"
                if not current or measure_text_width(candidate, font_path, font_size_pt) <= max_width:
                    current = candidate
                else:
                    if current:
                        lines.append(current)
                    current = word

            if current:
                lines.append(current)
        return lines or [""]

    def fit_text(
        text: str,
        *,
        font_path: Path,
        preferred_font_size: float,
        min_font_size: float,
        max_width: float,
        max_height: float,
        line_spacing: float,
        max_lines: int | None = None,
    ) -> dict:
        current_font_size = preferred_font_size
        best_layout = None

        while current_font_size >= min_font_size:
            lines = wrap_text(text, font_path, current_font_size, max_width)
            line_height = measure_line_height(font_path, current_font_size, line_spacing)
            height = len(lines) * line_height
            too_many_lines = max_lines is not None and len(lines) > max_lines
            overflow_height = max(0.0, height - max_height)
            score = (
                overflow_height * 2000
                + max(0, len(lines) - (max_lines or 999)) * 1500
                + (preferred_font_size - current_font_size) * 10
            )
            layout = {
                "source_text": text,
                "lines": lines,
                "font_size": current_font_size,
                "width": max_width,
                "height": min(height, max_height),
                "score": score,
            }

            if best_layout is None or score < best_layout["score"]:
                best_layout = layout

            if height <= max_height and not too_many_lines:
                return layout

            break

        return best_layout

    statement_font_name = "Times New Roman"
    title_font_name = "Times New Roman"
    subtitle_font_name = "Arial"

    statement_font_path = resolve_font_path(statement_font_name, bold=False, italic=False)
    title_font_path = resolve_font_path(title_font_name, bold=False, italic=True)
    subtitle_font_path = resolve_font_path(subtitle_font_name, bold=False, italic=False)

    statement_layout = fit_text(
        closing_statement.strip(),
        font_path=statement_font_path,
        preferred_font_size=24.0,
        min_font_size=11.0,
        max_width=1276.0,
        max_height=84.0,
        line_spacing=1.0,
        max_lines=2,
    )

    title_layout = fit_text(
        title.strip(),
        font_path=title_font_path,
        preferred_font_size=58.0,
        min_font_size=24.0,
        max_width=1240.0,
        max_height=240.0,
        line_spacing=0.9,
        max_lines=3,
    )

    subtitle_layout = fit_text(
        subtitle.strip(),
        font_path=subtitle_font_path,
        preferred_font_size=14.0,
        min_font_size=8.0,
        max_width=1180.0,
        max_height=72.0,
        line_spacing=1.0,
        max_lines=2,
    )

    image_x = 30.0
    image_y = 30.0
    image_w = 1540.0
    image_h = 840.0

    # The bands grow with the measured text.  The default values preserve the
    # original visual rhythm, while longer content gets more room before the
    # font is reduced.
    band_x = 130.0
    band_w = 1340.0
    content_bottom = image_y + image_h - 28.0

    statement_band_x = band_x
    statement_band_y = 214.0
    statement_band_w = band_w
    statement_band_h = max(
        76.0,
        min(124.0, statement_layout["height"] + 28.0),
    )

    title_band_x = band_x
    title_band_y = statement_band_y + statement_band_h + 53.0
    title_band_w = band_w
    title_band_h = max(
        205.0,
        min(290.0, title_layout["height"] + 64.0),
    )

    subtitle_band_x = band_x
    subtitle_band_y = title_band_y + title_band_h + 54.0
    subtitle_band_w = band_w
    subtitle_band_h = max(
        75.0,
        min(
            140.0,
            subtitle_layout["height"] + 34.0,
            content_bottom - subtitle_band_y,
        ),
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

    slide = ET.SubElement(presentation, "slide", {"background": background_color})

    def add(tag: str, **attrs):
        return ET.SubElement(
            slide,
            tag,
            {key: str(value) for key, value in attrs.items() if value is not None},
        )

    def textbox(text: str, **attrs):
        node = add("textbox", **attrs)
        node.text = text
        return node

    add(
        "shape",
        type="rect",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    add(
        "image",
        src=image_url,
        x=image_x,
        y=image_y,
        width=image_w,
        height=image_h,
        fit="cover",
        crop_x=0.52,
        crop_y=0.48,
        grayscale="true",
    )

    add(
        "shape",
        type="rect",
        x=image_x,
        y=image_y,
        width=image_w,
        height=image_h,
        fill=image_overlay_color,
        opacity=0.08,
        line_color="none",
    )

    add(
        "shape",
        type="rect",
        x=statement_band_x,
        y=statement_band_y,
        width=statement_band_w,
        height=statement_band_h,
        fill=top_band_color,
        opacity=0.96,
        line_color="none",
    )

    add(
        "shape",
        type="rect",
        x=title_band_x,
        y=title_band_y,
        width=title_band_w,
        height=title_band_h,
        fill=title_band_color,
        opacity=0.98,
        line_color="none",
    )

    add(
        "shape",
        type="rect",
        x=subtitle_band_x,
        y=subtitle_band_y,
        width=subtitle_band_w,
        height=subtitle_band_h,
        fill=bottom_band_color,
        opacity=0.96,
        line_color="none",
    )

    textbox(
        statement_layout["source_text"],
        x=statement_band_x + 42,
        y=statement_band_y + (statement_band_h - statement_layout["height"]) / 2,
        width=statement_band_w - 84,
        height=statement_layout["height"],
        font=statement_font_name,
        font_path=str(statement_font_path),
        size=statement_layout["font_size"],
        min_font_size=11.0,
        color=closing_statement_color,
        align="center",
        vertical_align="middle",
        bold="false",
        italic="false",
        single_line="false",
        max_lines=2,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    textbox(
        title_layout["source_text"],
        x=title_band_x + 50,
        y=title_band_y + (title_band_h - title_layout["height"]) / 2,
        width=title_band_w - 100,
        height=title_layout["height"],
        font=title_font_name,
        font_path=str(title_font_path),
        size=title_layout["font_size"],
        min_font_size=24.0,
        color=title_color,
        align="center",
        vertical_align="middle",
        bold="false",
        italic="true",
        single_line="false",
        max_lines=3,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=0.9,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    textbox(
        subtitle_layout["source_text"],
        x=subtitle_band_x + 62,
        y=subtitle_band_y + (subtitle_band_h - subtitle_layout["height"]) / 2,
        width=subtitle_band_w - 124,
        height=subtitle_layout["height"],
        font=subtitle_font_name,
        font_path=str(subtitle_font_path),
        size=subtitle_layout["font_size"],
        min_font_size=8.0,
        color=subtitle_color,
        align="center",
        vertical_align="middle",
        bold="false",
        italic="false",
        single_line="false",
        max_lines=2,
        overflow="clip",
        reflow_on_resize="true",
        line_spacing=1.0,
        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
        safety_ratio=1.0,
    )

    raw_xml = ET.tostring(presentation, encoding="utf-8")
    xml_content = minidom.parseString(raw_xml).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

    return xml_content


#Chart tool

def generate_monthly_sales_revenue_line_slide_xml(
    title: str = "Doanh thu bán hàng hàng tháng",

    data: list[dict[str, str | int | float]] = [
        {"label": "Th.1",  "value": 0},
        {"label": "Th.2",  "value": 10},
        {"label": "Th.3",  "value": 15},
        {"label": "Th.4",  "value": 45},
        {"label": "Th.5",  "value": 40},
        {"label": "Th.6",  "value": 50},
        {"label": "Th.7",  "value": 100},
        {"label": "Th.8",  "value": 85},
        {"label": "Th.9",  "value": 70},
        {"label": "Th.10", "value": 60},
        {"label": "Th.11", "value": 70},
        {"label": "Th.12", "value": 125},
    ],

    analysis_items: str = (
        "• Xu hướng: Biểu đồ cho thấy doanh thu biến động theo từng giai đoạn, "
        "tăng dần từ đầu kỳ và đạt mức cao nhất vào cuối chu kỳ theo dõi.\n"
        "• Tăng đột biến và giảm: Doanh thu tăng mạnh trong một số giai đoạn cao điểm, "
        "sau đó giảm nhẹ nhưng vẫn duy trì cao hơn mức trung bình ban đầu.\n"

    ),

    background_color: str = "#F3E5D6",
    text_color: str = "#2F2F2F",
    line_color: str = "#EF845E",
    grid_color: str = "#C8C0B8",
) -> str:
    """
    Generate XML for a monthly sales revenue line-chart slide.

    data format:
    [
        {"label": "Th.1", "value": 0},
        {"label": "Th.2", "value": 10},
        ...
    ]

    analysis_items format:
    A multiline string. Each line can represent one analysis point.
    """

    import math

    # =========================================================
    # Normalize
    # =========================================================

    title = str(title or "").strip()

    # =========================================================
    # Normalize data
    # =========================================================

    rows = (
        data
        if isinstance(data, (list, tuple))
        else [data]
    )

    normalized_data = []

    for index, raw_item in enumerate(rows):
        item = (
            raw_item
            if isinstance(raw_item, dict)
            else {}
        )

        label = str(
            item.get("label")
            or item.get("category")
            or item.get("name")
            or f"Th.{index + 1}"
        ).strip()

        try:
            value = float(
                item.get("value", 0)
            )
        except (TypeError, ValueError):
            value = 0.0

        normalized_data.append(
            {
                "label": label,
                "value": value,
            }
        )

    if len(normalized_data) < 2:
        raise ValueError(
            "Line chart cần ít nhất 2 điểm dữ liệu."
        )

    # =========================================================
    # Y-axis scale
    # =========================================================

    maximum = max(
        item["value"]
        for item in normalized_data
    )

    # Similar visual scale to reference image.
    rough_step = max(
        1.0,
        maximum / 6.0,
    )

    magnitude = 10 ** math.floor(
        math.log10(rough_step)
    )

    normalized_step = (
        rough_step / magnitude
    )

    if normalized_step <= 1:
        nice = 1
    elif normalized_step <= 2:
        nice = 2
    elif normalized_step <= 5:
        nice = 5
    else:
        nice = 10

    tick_step = nice * magnitude

    axis_max = (
        math.ceil(
            maximum / tick_step
        )
        * tick_step
    )

    # Give tallest point slight breathing room.
    if axis_max <= maximum:
        axis_max += tick_step

    # =========================================================
    # Canvas
    # =========================================================

    canvas_width = 1600
    canvas_height = 900

    # =========================================================
    # Header layout
    # =========================================================

    header_x = 105.0
    header_y = 60.0
    header_w = 1390.0

    title_x = header_x + 45
    title_y = header_y + 25
    title_w = header_w - 90
    title_h = 130.0

    # =========================================================
    # Chart layout
    # =========================================================

    plot_left = 175.0
    plot_top = 270.0
    plot_right = 1495.0
    plot_bottom = 630.0

    plot_w = (
        plot_right
        - plot_left
    )

    plot_h = (
        plot_bottom
        - plot_top
    )

    # =========================================================
    # Analysis layout
    # =========================================================

    analysis_x = 105.0
    analysis_y = 690.0
    analysis_w = 1390.0

    # =========================================================
    # Build XML
    # =========================================================

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
        {
            "background": background_color,
        },
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
        node.text = str(text)
        return node

    # =========================================================
    # Background
    # =========================================================

    add(
        "shape",
        type="rectangle",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    # =========================================================
    # Main title
    # =========================================================

    textbox(
        title,
        x=title_x,
        y=title_y,
        width=title_w,
        height=title_h,

        font="Arial",
        size=46,
        min_font_size=40,

        color=text_color,

        bold="true",
        italic="false",

        align="left",
        vertical_align="middle",

        single_line="false",
        max_lines=2,

        overflow="clip",
        reflow_on_resize="true",

        line_spacing=0.90,
        safety_ratio=1.0,

        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    # =========================================================
    # Y-axis grid + labels
    # =========================================================

    tick_values = []

    current = 0.0

    while current <= (
        axis_max + tick_step * 0.01
    ):
        tick_values.append(current)
        current += tick_step

    for tick in tick_values:

        ratio = tick / axis_max

        y = (
            plot_bottom
            - ratio * plot_h
        )

        add(
            "line",
            x1=plot_left,
            y1=y,
            x2=plot_right,
            y2=y,
            color=grid_color,
            width=0.65,
        )

        textbox(
            f"{tick:g}",
            x=plot_left - 66,
            y=y - 17,
            width=48,
            height=34,

            font="Arial",
            size=14,
            min_font_size=12,

            color=text_color,

            bold="false",

            align="right",
            vertical_align="middle",

            single_line="true",
            max_lines=1,

            overflow="clip",
            reflow_on_resize="true",

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    # =========================================================
    # X positions
    # =========================================================

    point_count = len(
        normalized_data
    )

    step_x = (
        plot_w
        / (point_count - 1)
    )

    point_positions = []

    for index, item in enumerate(
        normalized_data
    ):

        x = (
            plot_left
            + index * step_x
        )

        ratio = (
            float(item["value"])
            / axis_max
        )

        y = (
            plot_bottom
            - ratio * plot_h
        )

        point_positions.append(
            (
                x,
                y,
                float(item["value"]),
            )
        )

    # =========================================================
    # Connecting line
    # =========================================================

    for index in range(
        len(point_positions) - 1
    ):

        x1, y1, _ = (
            point_positions[index]
        )

        x2, y2, _ = (
            point_positions[index + 1]
        )

        add(
            "line",
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            color=line_color,
            width=1.8,
        )

    # =========================================================
    # Markers
    # =========================================================

    marker_size = 15.0

    for x, y, value in point_positions:

        add(
            "shape",
            type="circle",

            x=x - marker_size / 2,
            y=y - marker_size / 2,

            width=marker_size,
            height=marker_size,

            fill=line_color,
            line_color="none",
        )

    # =========================================================
    # X labels
    # =========================================================

    label_width = min(
        95.0,
        step_x * 0.95,
    )

    label_font_size = max(
        8.0,
        min(
            14.0,
            label_width * 0.26,
        ),
    )

    for index, item in enumerate(
        normalized_data
    ):

        x = point_positions[index][0]

        textbox(
            item["label"],

            x=x - label_width / 2,
            y=plot_bottom + 10,

            width=label_width,
            height=38,

            font="Arial",
            size=label_font_size,
            min_font_size=max(8.0, label_font_size - 2.0),

            color=text_color,

            bold="true",

            align="center",
            vertical_align="top",

            single_line="true",
            max_lines=1,

            overflow="clip",
            reflow_on_resize="true",

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    # =========================================================
    # Analysis title
    # =========================================================

    textbox(
        "Phân tích",

        x=analysis_x,
        y=analysis_y,

        width=190,
        height=34,

        font="Arial",
        size=17,
        min_font_size=15,

        color=text_color,

        bold="true",

        align="left",
        vertical_align="middle",

        single_line="true",
        max_lines=1,

        overflow="clip",
        reflow_on_resize="true",

        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    # =========================================================
    # Analysis text
    # =========================================================

    textbox(
        analysis_items,

        x=analysis_x + 10,
        y=analysis_y + 40,
        width=analysis_w - 20,
        height=270,

        font="Arial",
        size=15,
        min_font_size=10,

        color=text_color,

        bold="false",

        align="left",
        vertical_align="top",

        single_line="false",
        max_lines=10,

        overflow="shrink",
        reflow_on_resize="true",

        line_spacing=1.05,

        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    normalized_analysis = []

    analysis_row_y = (
        analysis_y + 40
    )

    for index, raw_item in enumerate(
        normalized_analysis[:5]
    ):

        item = (
            raw_item
            if isinstance(raw_item, dict)
            else {}
        )

        row_y = (
            analysis_row_y
            + index * 46
        )

        # Bullet
        textbox(
            "•",

            x=analysis_x + 10,
            y=row_y,

            width=20,
            height=42,

            font="Arial",
            size=17,

            color=text_color,

            align="center",
            vertical_align="middle",

            single_line="true",
            max_lines=1,

            overflow="clip",

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        # Bold analysis label
        analysis_title = str(
            item.get("title")
            or ""
        ).strip()

        title_box_w = max(
            140.0,
            min(
                310.0,
                125.0
                + len(analysis_title) * 7.0,
            )
        )

        textbox(
            analysis_title,

            x=analysis_x + 40,
            y=row_y,

            width=title_box_w,
            height=42,

            font="Arial",
            size=15,
            min_font_size=13,

            color=text_color,

            bold="true",

            align="left",
            vertical_align="middle",

            single_line="true",
            max_lines=1,

            overflow="shrink",
            reflow_on_resize="true",

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        textbox(
            str(
                item.get("text")
                or ""
            ),

            x=(
                analysis_x
                + 40
                + title_box_w
                + 5
            ),
            y=row_y,

            width=(
                analysis_w
                - title_box_w
                - 55
            ),
            height=42,

            font="Arial",
            size=14,
            min_font_size=11,

            color=text_color,

            bold="false",

            align="left",
            vertical_align="middle",

            single_line="false",
            max_lines=2,

            overflow="shrink",
            reflow_on_resize="true",

            line_spacing=1.0,

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    # =========================================================
    # Serialize
    # =========================================================

    raw_xml = ET.tostring(
        presentation,
        encoding="utf-8",
    )

    return minidom.parseString(
        raw_xml
    ).toprettyxml(
        indent="  ",
        encoding="UTF-8",
    ).decode("utf-8")

def generate_market_share_distribution_slide_xml(
    title: str = "Market Share\nDistribution Graph",
    intro_text: str = (
        "This graph tracks the market share of "
        "the company over a specified period."
    ),
    items: list[dict[str, str | int]] = [
        {
            "title": "International",
            "description": (
                "This graph tracks the market share "
                "of the company over a specified period."
            ),
            "value": 50,
            "color": "#7ED957",
        },
        {
            "title": "Local",
            "description": (
                "Targets consumers within a single "
                "country, focusing on national preferences."
            ),
            "value": 50,
            "color": "#FFBD59",
        },
   
    ],
    background_color: str = "#FFFFFF",
    title_color: str = "#000000",
    text_color: str = "#242424",
) -> str:
    """
    Generate XML for a market-share distribution slide.

    The slide contains a title, an introductory paragraph, a donut chart,
    percentage labels, and detail cards for each market-share category.
    Item values are automatically normalized for the donut chart.
    """

    # =========================================================
    # Normalize
    # =========================================================

    title = str(title or "").strip()
    intro_text = str(intro_text or "").strip()

    default_colors = [
        "#7ED957",
        "#FFBD59",
        "#FF5757",
        "#5DADE2",
        "#9B59B6",
    ]

    supported_icon_types = [
        "globe",
        "location",
        "region",
        "chart",
    ]

    def infer_icon_type(
        item_title: str,
        item_description: str,
        item_index: int,
    ) -> str:
        content = (
            f"{item_title} {item_description}"
        ).casefold()

        icon_keywords = {
            "globe": (
                "international",
                "global",
                "world",
                "worldwide",
                "overseas",
                "export",
                "quốc tế",
                "toàn cầu",
                "nước ngoài",
            ),
            "location": (
                "local",
                "domestic",
                "national",
                "country",
                "city",
                "location",
                "địa phương",
                "nội địa",
                "trong nước",
                "quốc gia",
                "thành phố",
            ),
            "region": (
                "region",
                "regional",
                "area",
                "zone",
                "territory",
                "khu vực",
                "vùng",
                "miền",
            ),
            "chart": (
                "share",
                "market",
                "sales",
                "revenue",
                "growth",
                "trend",
                "distribution",
                "tỷ trọng",
                "doanh thu",
                "tăng trưởng",
                "xu hướng",
                "phân bổ",
            ),
        }

        for icon_name, keywords in icon_keywords.items():
            if any(
                keyword in content
                for keyword in keywords
            ):
                return icon_name

        return supported_icon_types[
            item_index % len(supported_icon_types)
        ]

    raw_items = (
        items
        if isinstance(items, (list, tuple))
        else [items]
    )

    normalized_items: list[dict[str, object]] = []

    for index, raw_item in enumerate(raw_items):

        item = (
            raw_item
            if isinstance(raw_item, dict)
            else {}
        )

        try:
            value = float(
                item.get("value", 0)
            )
        except (TypeError, ValueError):
            value = 0.0

        if value <= 0:
            continue

        color = str(
            item.get("color")
            or default_colors[
                index % len(default_colors)
            ]
        ).strip()

        if not color.startswith("#"):
            color = "#" + color

        normalized_items.append(
            {
                "title": str(
                    item.get("title")
                    or f"Category {index + 1}"
                ).strip(),

                "description": str(
                    item.get("description")
                    or ""
                ).strip(),

                "value": value,

                "color": color,
            }
        )

    if not normalized_items:
        raise ValueError(
            "Market share slide cần ít nhất một item có value > 0."
        )

    for index, item in enumerate(
        normalized_items
    ):
        item["icon"] = infer_icon_type(
            str(item["title"]),
            str(item["description"]),
            index,
        )

    total = sum(
        float(item["value"])
        for item in normalized_items
    )

    for item in normalized_items:
        item["percentage"] = (
            float(item["value"])
            / total
            * 100.0
        )

    # =========================================================
    # Canvas
    # =========================================================

    canvas_width = 1600
    canvas_height = 900

    # =========================================================
    # Layout
    # =========================================================

    # Title
    title_x = 100.0
    title_y = 72.0
    title_w = 620.0
    title_h = 190.0

    # Top-right intro
    intro_x = 815.0
    intro_y = 120.0
    intro_w = 600.0
    intro_h = 110.0

    # Donut
    donut_x = 90.0
    donut_y = 300.0
    donut_size = 590.0

    # Right details adapt to the number of items.
    detail_area_x = 770.0
    detail_area_w = 650.0
    detail_start_y = 305.0
    detail_bottom_y = 850.0
    detail_column_gap = 25.0

    item_count = len(normalized_items)
    detail_columns = 1 if item_count <= 3 else 2
    detail_rows = (
        item_count + detail_columns - 1
    ) // detail_columns

    detail_column_w = (
        detail_area_w
        - detail_column_gap * (detail_columns - 1)
    ) / detail_columns

    detail_gap = min(
        215.0,
        max(
            125.0,
            (detail_bottom_y - detail_start_y)
            / max(detail_rows, 1),
        ),
    )

    detail_icon_size = (
        86.0
        if detail_columns == 1
        else 64.0
    )

    detail_text_offset = (
        detail_icon_size + 20.0
    )

    detail_title_font_size = (
        28.0
        if detail_columns == 1
        else 18.0
    )

    detail_body_font_size = (
        18.0
        if detail_columns == 1
        else 13.0
    )

    detail_body_min_font_size = (
        15.0
        if detail_columns == 1
        else 10.0
    )

    detail_title_h = (
        50.0
        if detail_columns == 1
        else 36.0
    )

    detail_body_offset = (
        58.0
        if detail_columns == 1
        else 45.0
    )

    detail_body_h = max(
        60.0,
        min(
            105.0,
            detail_gap - detail_body_offset - 8.0,
        ),
    )

    # =========================================================
    # XML root
    # =========================================================

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
        {
            "background": background_color,
        },
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
        node.text = str(text)
        return node

    # =========================================================
    # Background
    # =========================================================

    add(
        "shape",
        type="rectangle",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    # =========================================================
    # Main title
    # =========================================================

    textbox(
        title,
        x=title_x,
        y=title_y,
        width=title_w,
        height=title_h,

        font="Arial",
        size=48,
        min_font_size=42,

        color=title_color,

        bold="true",
        italic="false",

        align="left",
        vertical_align="top",

        single_line="false",
        max_lines=3,

        overflow="clip",
        reflow_on_resize="true",

        line_spacing=0.92,
        safety_ratio=1.0,

        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    # =========================================================
    # Intro paragraph
    # =========================================================

    textbox(
        intro_text,
        x=intro_x,
        y=intro_y,
        width=intro_w,
        height=intro_h,

        font="Arial",
        size=22,
        min_font_size=18,

        color=text_color,

        bold="false",
        italic="false",

        align="left",
        vertical_align="top",

        single_line="false",
        max_lines=4,

        overflow="clip",
        reflow_on_resize="true",

        line_spacing=1.02,
        safety_ratio=1.0,

        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    # =========================================================
    # Donut chart as SVG
    # =========================================================

    svg_node = add(
        "svg",
        x=donut_x,
        y=donut_y,
        width=donut_size,
        height=donut_size,
        pixel_width=900,
        pixel_height=900,
    )

    radius = 165.0
    cx = 250.0
    cy = 250.0

    circumference = (
        2
        * 3.141592653589793
        * radius
    )

    gap_degrees = 4.0

    svg_parts = [
        """
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="500"
    height="500"
    viewBox="0 0 500 500"
>
"""
    ]

    current_angle = -90.0

    for item in normalized_items:

        percentage = float(
            item["percentage"]
        )

        sweep = (
            percentage
            / 100.0
            * 360.0
        )

        effective_sweep = max(
            1.0,
            sweep - gap_degrees
        )

        arc_length = (
            effective_sweep
            / 360.0
            * circumference
        )

        rest_length = (
            circumference
            - arc_length
        )

        svg_parts.append(
            f"""
    <circle
        cx="{cx}"
        cy="{cy}"
        r="{radius}"
        fill="none"
        stroke="{item['color']}"
        stroke-width="92"
        stroke-linecap="butt"
        stroke-dasharray="{arc_length:.2f} {rest_length:.2f}"
        transform="rotate({current_angle:.2f} {cx} {cy})"
    />
"""
        )

        current_angle += sweep

    svg_parts.append(
        """
</svg>
"""
    )

    svg_node.text = "".join(
        svg_parts
    )

    # =========================================================
    # Percentage labels around donut
    # =========================================================

    import math

    current_angle = -90.0

    label_radius = 238.0

    for item in normalized_items:

        percentage = float(
            item["percentage"]
        )

        sweep = (
            percentage
            / 100.0
            * 360.0
        )

        center_angle = (
            current_angle
            + sweep / 2
        )

        angle_rad = math.radians(
            center_angle
        )

        label_center_x = (
            donut_x
            + donut_size / 2
            + math.cos(angle_rad)
            * (label_radius / 500.0 * donut_size)
        )

        label_center_y = (
            donut_y
            + donut_size / 2
            + math.sin(angle_rad)
            * (label_radius / 500.0 * donut_size)
        )

        textbox(
            f"{percentage:.0f}%",

            x=label_center_x - 45,
            y=label_center_y - 20,

            width=90,
            height=40,

            font="Arial",
            size=20,
            min_font_size=18,

            color="#000000",

            bold="true",
            italic="false",

            align="center",
            vertical_align="middle",

            single_line="true",
            max_lines=1,

            overflow="clip",
            reflow_on_resize="true",

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        current_angle += sweep

    # =========================================================
    # Icon SVG helpers
    # =========================================================

    def globe_icon_svg() -> str:
        return """
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 100 100">
  <g fill="none"
     stroke="#111111"
     stroke-width="4"
     stroke-linecap="round"
     stroke-linejoin="round">

    <circle cx="50" cy="50" r="30"/>

    <ellipse cx="50" cy="50"
             rx="14" ry="30"/>

    <path d="M20 50 H80"/>
    <path d="M26 36 H74"/>
    <path d="M26 64 H74"/>

    <path d="M64 20
             C78 26 83 39 78 53"/>

    <path d="M78 53
             L82 43"/>

    <path d="M78 53
             L68 50"/>

  </g>
</svg>
"""

    def location_icon_svg() -> str:
        return """
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 100 100">

  <g fill="none"
     stroke="#111111"
     stroke-width="4"
     stroke-linecap="round"
     stroke-linejoin="round">

    <path d="
        M50 18
        C34 18 25 29 25 43
        C25 61 50 78 50 78
        C50 78 75 61 75 43
        C75 29 66 18 50 18
    "/>

    <circle
        cx="50"
        cy="42"
        r="9"
    />

    <ellipse
        cx="50"
        cy="82"
        rx="27"
        ry="7"
    />

  </g>
</svg>
"""

    def region_icon_svg() -> str:
        return """
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 100 100">

  <g fill="none"
     stroke="#111111"
     stroke-width="3.6"
     stroke-linecap="round"
     stroke-linejoin="round">

    <circle
        cx="45"
        cy="52"
        r="27"
    />

    <path d="
        M25 35
        L35 30
        L40 36
        L36 44
        L27 43
        Z
    "/>

    <path d="
        M48 28
        L59 33
        L55 40
        L46 40
        L42 34
        Z
    "/>

    <path d="
        M31 55
        L42 50
        L50 58
        L47 70
        L37 72
        Z
    "/>

    <path d="
        M56 47
        L66 51
        L64 63
        L55 66
        L51 58
        Z
    "/>

    <path d="
        M76 22
        C66 22 61 29 61 37
        C61 47 76 57 76 57
        C76 57 91 47 91 37
        C91 29 86 22 76 22
        Z
    "/>

    <circle
        cx="76"
        cy="36"
        r="5"
    />

  </g>
</svg>
"""

    def chart_icon_svg() -> str:
        return """
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 100 100">

  <g fill="none"
     stroke="#111111"
     stroke-width="4"
     stroke-linecap="round"
     stroke-linejoin="round">

    <path d="M20 78 V22"/>
    <path d="M20 78 H84"/>
    <path d="M28 64 L43 50 L56 58 L76 32"/>

    <circle cx="28" cy="64" r="3" fill="#111111"/>
    <circle cx="43" cy="50" r="3" fill="#111111"/>
    <circle cx="56" cy="58" r="3" fill="#111111"/>
    <circle cx="76" cy="32" r="3" fill="#111111"/>

  </g>
</svg>
"""

    # =========================================================
    # Right detail items
    # =========================================================

    used_icon_types: set[str] = set()

    for index, item in enumerate(
        normalized_items
    ):

        column_index = (
            index % detail_columns
        )

        row_index = (
            index // detail_columns
        )

        card_x = (
            detail_area_x
            + column_index
            * (
                detail_column_w
                + detail_column_gap
            )
        )

        row_y = (
            detail_start_y
            + row_index * detail_gap
        )

        detail_icon_x = card_x
        detail_text_x = (
            card_x
            + detail_text_offset
        )

        detail_title_w = (
            detail_column_w
            - detail_text_offset
        )

        detail_body_w = detail_title_w

        # ---------------------------------------------
        # Colored icon square
        # ---------------------------------------------

        add(
            "shape",
            type="rectangle",

            x=detail_icon_x,
            y=row_y,

            width=detail_icon_size,
            height=detail_icon_size,

            fill=item["color"],
            line_color="none",
        )

        # ---------------------------------------------
        # Black icon
        # ---------------------------------------------

        icon_svg = add(
            "svg",

            x=detail_icon_x + 15,
            y=row_y + 15,

            width=detail_icon_size - 30,
            height=detail_icon_size - 30,

            pixel_width=300,
            pixel_height=300,
        )

        icon_type = str(
            item["icon"]
        ).lower()

        if icon_type in {
            "pin",
            "local",
        }:
            icon_type = "location"
        elif icon_type in {
            "map",
        }:
            icon_type = "region"
        elif icon_type in {
            "trend",
            "analytics",
            "other",
        }:
            icon_type = "chart"

        if (
            icon_type not in supported_icon_types
            or icon_type in used_icon_types
        ):
            unused_icon_types = [
                icon_name
                for icon_name in supported_icon_types
                if icon_name not in used_icon_types
            ]

            if unused_icon_types:
                icon_type = unused_icon_types[0]

        used_icon_types.add(icon_type)

        if icon_type in {
            "location",
        }:
            icon_svg.text = (
                location_icon_svg()
            )

        elif icon_type in {
            "region",
        }:
            icon_svg.text = (
                region_icon_svg()
            )

        elif icon_type in {
            "chart",
        }:
            icon_svg.text = (
                chart_icon_svg()
            )

        else:
            icon_svg.text = (
                globe_icon_svg()
            )

        # ---------------------------------------------
        # Detail title
        # ---------------------------------------------

        textbox(
            item["title"],

            x=detail_text_x,
            y=row_y - 1,

            width=detail_title_w,
            height=detail_title_h,

            font="Arial",
            size=detail_title_font_size,
            min_font_size=max(
                10.0,
                detail_title_font_size - 5.0,
            ),

            color="#000000",

            bold="true",
            italic="false",

            align="left",
            vertical_align="middle",

            single_line="true",
            max_lines=1,

            overflow="shrink",
            reflow_on_resize="true",

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

        # ---------------------------------------------
        # Description
        # ---------------------------------------------

        textbox(
            item["description"],

            x=detail_text_x,
            y=row_y + detail_body_offset,

            width=detail_body_w,
            height=detail_body_h,

            font="Arial",
            size=detail_body_font_size,
            min_font_size=detail_body_min_font_size,

            color=text_color,

            bold="false",
            italic="false",

            align="left",
            vertical_align="top",

            single_line="false",
            max_lines=4,

            overflow="shrink",
            reflow_on_resize="true",

            line_spacing=1.03,

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    # =========================================================
    # Serialize XML
    # =========================================================

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

def generate_best_selling_product_chart_slide_xml(
    title: str = "BEST SELLING PRODUCT",

    chart_data: list[dict[str, str | dict[str, int | float]]] = [
        {
            "category": "January",
            "series": {
                "Sunscreen": 7,
                "Moisturizer": 6,
                "Serum": 5,
            },
        },
        {
            "category": "February",
            "series": {
                "Sunscreen": 8,
                "Moisturizer": 8,
                "Serum": 4,
            },
        },
        {
            "category": "March",
            "series": {
                "Sunscreen": 15,
                "Moisturizer": 10,
                "Serum": 5,
            },
        },
        {
            "category": "April",
            "series": {
                "Sunscreen": 18,
                "Moisturizer": 14,
                "Serum": 8,
            },
        },
        
    ],

    footer_text: str = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Fusce ac rutrum ipsum. Suspendisse auctor aliquam ante id tempor. "
        "Ut id dolor aliquam, pellentesque odio vitae, tempus turpis."
    ),

    background_color: str = "#FFFFFF",
    panel_color: str = "#F8F8F8",

    title_color: str = "#2B8FB4",

    coral_color: str = "#FF7375",
    peach_color: str = "#F3C580",
    green_color: str = "#A6CE91",

    grid_color: str = "#C9C9C9",
    axis_text_color: str = "#161616",

    footer_color: str = "#626262",
) -> str:

    """
    Generate XML for a minimalist best-selling-product slide.

    Layout:
    - Large centered light-blue title
    - Large grouped column chart inside a very light gray panel
    - Centered footer paragraph

    chart_data:
    [
        {
            "category": "January",
            "series": {
                "Sunscreen": 7,
                "Moisturizer": 6,
                "Serum": 5
            }
        }
    ]

    """

    # =========================================================
    # Normalize
    # =========================================================

    title = str(title or "").strip()
    footer_text = str(footer_text or "").strip()

    # =========================================================
    # Normalize chart data
    # =========================================================

    rows = chart_data if isinstance(chart_data, (list, tuple)) else [chart_data]

    normalized_rows = []

    for index, raw_row in enumerate(rows):
        row = raw_row if isinstance(raw_row, dict) else {}

        category = str(
            row.get("category")
            or row.get("label")
            or f"Category {index + 1}"
        ).strip()

        series = row.get("series")
        series = series if isinstance(series, dict) else {}

        clean_series = {}

        for name, raw_value in series.items():
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                value = 0.0

            clean_series[str(name)] = max(0.0, value)

        normalized_rows.append(
            {
                "category": category,
                "series": clean_series,
            }
        )

    normalized_rows = normalized_rows[:6]

    if not normalized_rows:
        raise ValueError("chart_data cần ít nhất một category.")

    series_names = []

    for row in normalized_rows:
        for name in row["series"]:
            if name not in series_names:
                series_names.append(name)

    series_names = series_names[:3]

    if not series_names:
        raise ValueError("Chart cần ít nhất một series.")

    series_colors = [
        coral_color,
        peach_color,
        green_color,
    ]

    # =========================================================
    # Canvas
    # =========================================================

    canvas_width = 1600
    canvas_height = 900

    # =========================================================
    # Main layout
    # =========================================================

    # Title
    title_x = 300.0
    title_y = 105.0
    title_w = 1000.0
    title_h = 90.0

    # Main chart panel
    chart_panel_x = 95.0
    chart_panel_y = 255.0
    chart_panel_w = 1410.0
    chart_panel_h = 440.0

    # Footer
    footer_x = 230.0
    footer_y = 745.0
    footer_w = 1140.0
    footer_h = 95.0

    # =========================================================
    # Plot region
    # =========================================================

    plot_left = chart_panel_x + 90.0
    plot_top = chart_panel_y + 50.0
    plot_right = chart_panel_x + chart_panel_w - 42.0
    plot_bottom = chart_panel_y + chart_panel_h - 70.0

    plot_w = plot_right - plot_left
    plot_h = plot_bottom - plot_top

    # =========================================================
    # Determine axis maximum
    # =========================================================

    values = [
        float(row["series"].get(name, 0))
        for row in normalized_rows
        for name in series_names
    ]

    maximum = max(values or [1])

    if maximum <= 20:
        axis_max = 20.0
        tick_step = 5.0

    elif maximum <= 40:
        axis_max = 40.0
        tick_step = 10.0

    elif maximum <= 100:
        axis_max = 100.0
        tick_step = 25.0

    else:
        axis_max = maximum * 1.1
        tick_step = axis_max / 4

    # =========================================================
    # XML
    # =========================================================

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
        node.text = str(text)
        return node

    # =========================================================
    # Main background
    # =========================================================

    add(
        "shape",
        type="rectangle",
        x=0,
        y=0,
        width=canvas_width,
        height=canvas_height,
        fill=background_color,
        line_color="none",
    )

    # =========================================================
    # Title
    # Thin/light typography like reference image
    # =========================================================

    textbox(
        title.upper(),
        x=title_x,
        y=title_y,
        width=title_w,
        height=title_h,

        font="Arial",
        size=39,
        min_font_size=34,

        color=title_color,

        bold="false",
        italic="false",

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

    # =========================================================
    # Panels
    # Completely flat, no border, no radius
    # =========================================================

    add(
        "shape",
        type="rectangle",
        x=chart_panel_x,
        y=chart_panel_y,
        width=chart_panel_w,
        height=chart_panel_h,
        fill=panel_color,
        line_color="none",
    )


    # =========================================================
    # Legend
    # =========================================================

    legend_y = chart_panel_y + 18.0
    legend_item_gap = 210.0
    legend_total_w = len(series_names) * legend_item_gap
    legend_start_x = chart_panel_x + (chart_panel_w - legend_total_w) / 2

    for series_index, series_name in enumerate(series_names):
        color = series_colors[series_index % len(series_colors)]
        item_x = legend_start_x + series_index * legend_item_gap

        add(
            "shape",
            type="rectangle",
            x=item_x,
            y=legend_y + 7,
            width=18,
            height=18,
            fill=color,
            line_color="none",
        )

        textbox(
            series_name,
            x=item_x + 28,
            y=legend_y,
            width=165,
            height=32,
            font="Arial",
            size=13,
            min_font_size=11,
            color=axis_text_color,
            bold="false",
            align="left",
            vertical_align="middle",
            single_line="true",
            max_lines=1,
            overflow="clip",
            reflow_on_resize="true",
            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    # =========================================================
    # Grid lines + y-axis labels
    # =========================================================

    tick_count = 5

    for i in range(tick_count):

        value = i * tick_step

        if value > axis_max:
            value = axis_max

        ratio = value / axis_max

        y = plot_bottom - ratio * plot_h

        # Thin horizontal line
        add(
            "line",
            x1=plot_left,
            y1=y,
            x2=plot_right,
            y2=y,
            color=grid_color,
            width=0.8,
        )

        textbox(
            f"{value:g}",
            x=plot_left - 58,
            y=y - 16,
            width=42,
            height=32,

            font="Arial",
            size=14,
            min_font_size=12,

            color=axis_text_color,

            bold="false",

            align="right",
            vertical_align="middle",

            single_line="true",
            max_lines=1,

            overflow="clip",
            reflow_on_resize="true",

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    # =========================================================
    # Bars
    # Square, flat pastel bars like reference
    # =========================================================

    category_count = len(normalized_rows)

    category_slot = (
        plot_w / category_count
    )

    cluster_width = (
        category_slot * 0.72
    )

    small_gap = 3.0

    bar_width = (
        cluster_width
        - small_gap * (len(series_names) - 1)
    ) / len(series_names)

    bar_width = max(
        15.0,
        min(45.0, bar_width),
    )

    for category_index, row in enumerate(normalized_rows):

        category_center = (
            plot_left
            + category_slot * category_index
            + category_slot / 2
        )

        actual_cluster_w = (
            len(series_names) * bar_width
            + (len(series_names) - 1) * small_gap
        )

        cluster_x = (
            category_center
            - actual_cluster_w / 2
        )

        for series_index, series_name in enumerate(series_names):

            value = float(
                row["series"].get(
                    series_name,
                    0,
                )
            )

            bar_h = (
                value / axis_max
            ) * plot_h

            x = (
                cluster_x
                + series_index
                * (bar_width + small_gap)
            )

            y = (
                plot_bottom
                - bar_h
            )

            add(
                "shape",

                # IMPORTANT:
                # rectangle, NOT rounded_rectangle
                type="rectangle",

                x=x,
                y=y,

                width=bar_width,
                height=max(1.5, bar_h),

                fill=series_colors[
                    series_index
                    % len(series_colors)
                ],

                line_color="none",
            )

        # Category labels
        textbox(
            row["category"],
            x=(
                category_center
                - category_slot / 2
            ),
            y=plot_bottom + 15,

            width=category_slot,
            height=42,

            font="Arial",
            size=15,
            min_font_size=12,

            color=axis_text_color,

            bold="false",

            align="center",
            vertical_align="top",

            single_line="true",
            max_lines=1,

            overflow="clip",
            reflow_on_resize="true",

            margin_left=0,
            margin_right=0,
            margin_top=0,
            margin_bottom=0,
        )

    # =========================================================
    # Footer
    # =========================================================

    textbox(
        footer_text,

        x=footer_x,
        y=footer_y,

        width=footer_w,
        height=footer_h,

        font="Arial",
        size=16,
        min_font_size=14,

        color=footer_color,

        bold="false",
        italic="false",

        align="center",
        vertical_align="middle",

        single_line="false",
        max_lines=3,

        overflow="clip",
        reflow_on_resize="true",

        line_spacing=1.05,

        margin_left=0,
        margin_right=0,
        margin_top=0,
        margin_bottom=0,
    )

    # =========================================================
    # Serialize
    # =========================================================

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
