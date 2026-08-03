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
