"""Rule-based measurement for text overflow in the XML slide schema."""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from PIL import ImageFont


TEXT_TAGS = {"textbox", "text"}
_BR_MARKER_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_MATH_MARKER_RE = re.compile(r"<\s*/?\s*math-field\b", re.IGNORECASE)
_FONT_CACHE: dict[tuple[str, bool, bool, int], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}


def _number(value: str | None, fallback: float = 0.0) -> float:
    try:
        return float(value) if value is not None else fallback
    except (TypeError, ValueError):
        return fallback


def _positive_number(value: str | None, fallback: float) -> float:
    return max(0.0, _number(value, fallback))


def _bool(value: str | None, fallback: bool = False) -> bool:
    if value is None:
        return fallback
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _font_candidates(font_name: str, bold: bool, italic: bool, explicit_path: str | None) -> list[Path | str]:
    candidates: list[Path | str] = []
    if explicit_path:
        candidates.append(Path(explicit_path).expanduser())

    requested = font_name.strip().strip('"\'')
    if requested:
        candidates.append(requested)

    suffix = "-BoldOblique.ttf" if bold and italic else (
        "-Bold.ttf" if bold else "-Oblique.ttf" if italic else ".ttf"
    )
    candidates.extend(
        [
            Path("/usr/share/fonts/truetype/dejavu") / f"DejaVuSans{suffix}",
            Path("/usr/share/fonts/truetype/freefont") / (
                "FreeSansBoldOblique.ttf" if bold and italic
                else "FreeSansBold.ttf" if bold
                else "FreeSansOblique.ttf" if italic
                else "FreeSans.ttf"
            ),
            Path("/usr/share/fonts/truetype/liberation") / (
                "LiberationSans-BoldItalic.ttf" if bold and italic
                else "LiberationSans-Bold.ttf" if bold
                else "LiberationSans-Italic.ttf" if italic
                else "LiberationSans-Regular.ttf"
            ),
        ]
    )

    windir = os.environ.get("WINDIR")
    if windir:
        candidates.append(Path(windir) / "Fonts" / "arial.ttf")
    return candidates


def _load_font(element: ET.Element, font_size_px: float) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_name = element.get("font") or element.get("font_family") or "Arial"
    bold = _bool(element.get("bold")) or element.get("font_weight", "").lower() in {"bold", "700", "800", "900"}
    italic = _bool(element.get("italic"))
    explicit_path = element.get("font_path")
    cache_key = (f"{font_name}|{explicit_path or ''}", bold, italic, max(1, round(font_size_px)))
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    size = max(1, round(font_size_px))
    for candidate in _font_candidates(font_name, bold, italic, explicit_path):
        try:
            font = ImageFont.truetype(str(candidate), size)
            _FONT_CACHE[cache_key] = font
            return font
        except (OSError, TypeError):
            continue

    font = ImageFont.load_default()
    _FONT_CACHE[cache_key] = font
    return font


def _text_width(font: ImageFont.ImageFont, text: str) -> float:
    if not text:
        return 0.0
    try:
        return float(font.getlength(text))
    except AttributeError:
        bbox = font.getbbox(text)
        return float(bbox[2] - bbox[0])


def _wrap_line(line: str, font: ImageFont.ImageFont, max_width: float) -> list[str]:
    words = re.findall(r"\S+", line)
    if not words:
        return [""]

    lines: list[str] = []
    current = ""
    for word in words:
        pieces: list[str] = []
        if _text_width(font, word) <= max_width:
            pieces = [word]
        else:
            piece = ""
            for character in word:
                candidate = piece + character
                if piece and _text_width(font, candidate) > max_width:
                    pieces.append(piece)
                    piece = character
                else:
                    piece = candidate
            if piece:
                pieces.append(piece)

        for piece in pieces:
            candidate = f"{current} {piece}" if current else piece
            if not current or _text_width(font, candidate) <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = piece

    if current:
        lines.append(current)
    return lines or [""]


def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: float, single_line: bool) -> list[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if single_line:
        return [" ".join(normalized.split())]

    lines: list[str] = []
    for paragraph in normalized.split("\n"):
        lines.extend(_wrap_line(paragraph, font, max_width))
    return lines or [""]


def _line_height(font: ImageFont.ImageFont, font_size_px: float, line_spacing: float) -> float:
    # The preview uses CSS ``line-height: <line_spacing>``. Use that same
    # line-box size instead of a generic glyph sample, which overestimates
    # short one-line headings and causes unnecessary LLM calls.
    return max(1.0, font_size_px * max(0.1, line_spacing))


def _text_content(element: ET.Element) -> str:
    text = "".join(element.itertext())
    text = _BR_MARKER_RE.sub("\n", text)
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def _measure_textbox(
    element: ET.Element,
    *,
    slide_width: float,
    slide_height: float,
    point_to_canvas_x: float,
    point_to_canvas_y: float,
    slide_index: int,
    textbox_index: int,
) -> dict[str, Any]:
    x = _number(element.get("x"))
    y = _number(element.get("y"))
    width = _positive_number(element.get("width"), 300.0)
    height = _positive_number(element.get("height"), 100.0)
    text = _text_content(element)
    font_size_pt = _positive_number(element.get("size"), 24.0)
    font_size_px = max(1.0, font_size_pt * point_to_canvas_y)
    font = _load_font(element, font_size_px)

    margin_left = _positive_number(element.get("margin_left"), 0.0) * point_to_canvas_x
    margin_right = _positive_number(element.get("margin_right"), 0.0) * point_to_canvas_x
    margin_top = _positive_number(element.get("margin_top"), 0.0) * point_to_canvas_y
    margin_bottom = _positive_number(element.get("margin_bottom"), 0.0) * point_to_canvas_y
    available_width = max(1.0, width - margin_left - margin_right)
    available_height = max(1.0, height - margin_top - margin_bottom)
    safety_ratio = max(0.1, min(1.0, _number(element.get("safety_ratio"), 0.97)))
    target_width = available_width * safety_ratio
    target_height = available_height * safety_ratio
    single_line = _bool(element.get("single_line"))
    line_spacing = _positive_number(element.get("line_spacing"), 1.0)
    lines = _wrap_text(text, font, target_width, single_line)
    line_widths = [_text_width(font, line) for line in lines]
    required_height = len(lines) * _line_height(font, font_size_px, line_spacing)
    max_lines_value = element.get("max_lines")
    max_lines = int(max_lines_value) if max_lines_value and max_lines_value.isdigit() else (1 if single_line else None)

    reasons: list[str] = []
    if any(line_width > target_width + 0.5 for line_width in line_widths):
        reasons.append("text_width")
    if required_height > target_height + 0.5:
        reasons.append("text_height")
    if max_lines is not None and len(lines) > max_lines:
        reasons.append("max_lines")
    if x < 0 or y < 0 or x + width > slide_width + 0.5 or y + height > slide_height + 0.5:
        reasons.append("slide_boundary")

    rewrite_possible = (
        "slide_boundary" not in reasons
        and (
            "text_width" in reasons
            or "max_lines" in reasons
            or ("text_height" in reasons and len(lines) > 1)
        )
    )

    has_math_field = any(
        child.tag.rsplit("}", 1)[-1].lower() == "math-field" for child in element
    ) or bool(_MATH_MARKER_RE.search("".join(element.itertext())))

    return {
        "id": element.get("id") or f"slide-{slide_index + 1}-textbox-{textbox_index + 1}",
        "slide_index": slide_index + 1,
        "textbox_index": textbox_index,
        "text": text,
        "text_length": len(text),
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "font_size": font_size_pt,
        "line_count": len(lines),
        "max_lines": max_lines,
        "max_line_width": max(line_widths or [0.0]),
        "available_width": target_width,
        "required_height": required_height,
        "available_height": target_height,
        "reasons": reasons,
        "overflow": bool(reasons),
        "rewrite_possible": rewrite_possible,
        "has_math_field": has_math_field,
        "_element": element,
    }


def analyze_xml_root(root: ET.Element) -> list[dict[str, Any]]:
    """Analyze eligible text boxes and keep private element references for rewriting."""
    canvas_width = _positive_number(root.get("width"), 1600.0)
    canvas_height = _positive_number(root.get("height"), 900.0)
    slide_width_inches = _positive_number(root.get("slideWidthInches"), 13.333)
    slide_height_inches = _positive_number(root.get("slideHeightInches"), 7.5)
    point_to_canvas_x = canvas_width / max(1.0, slide_width_inches * 72.0)
    point_to_canvas_y = canvas_height / max(1.0, slide_height_inches * 72.0)

    records: list[dict[str, Any]] = []
    for slide_index, slide in enumerate(
        node for node in root if node.tag.rsplit("}", 1)[-1].lower() == "slide"
    ):
        textbox_index = 0
        for element in slide.iter():
            if element.tag.rsplit("}", 1)[-1].lower() not in TEXT_TAGS:
                continue
            if not _text_content(element):
                continue
            records.append(
                _measure_textbox(
                    element,
                    slide_width=canvas_width,
                    slide_height=canvas_height,
                    point_to_canvas_x=point_to_canvas_x,
                    point_to_canvas_y=point_to_canvas_y,
                    slide_index=slide_index,
                    textbox_index=textbox_index,
                )
            )
            textbox_index += 1
    return records


def public_overflow_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Remove private XML references before storing the report in workflow state."""
    boxes = []
    for record in records:
        boxes.append({key: value for key, value in record.items() if not key.startswith("_")})
    return {
        "checked_boxes": len(boxes),
        "overflowing_boxes": sum(1 for box in boxes if box["overflow"]),
        "boxes": boxes,
    }
