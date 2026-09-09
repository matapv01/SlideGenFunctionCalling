"""Deterministically enforce readable text colors in generated slide XML.

LLM prompts and tool-argument guards improve color choices, but they are not a
safe final boundary: deck-level styling, rich-text materialization, or a layout
implementation can still place low-contrast text on a surface.  This module
audits the actual XML that will be persisted and repairs it before rendering.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Iterable


_HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?")
_TEXT_TAGS = {"text", "textbox"}
_SOLID_TAGS = {"rect", "rectangle", "shape", "polygon"}
_UNKNOWN_SURFACE_COLORS = tuple(
    dict.fromkeys(
        [
            "#000000",
            "#404040",
            "#808080",
            "#BFBFBF",
            "#FFFFFF",
            "#FF0000",
            "#00FF00",
            "#0000FF",
            "#FFFF00",
            "#00FFFF",
            "#FF00FF",
        ]
    )
)
_SAFE_LIGHT = "#FFFFFF"
_SAFE_DARK = "#111827"


def _tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1].lower()


def _normalize_hex(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    match = _HEX_COLOR_RE.fullmatch(value.strip())
    if match is None:
        return None
    color = match.group(0).upper()
    if len(color) == 4:
        color = "#" + "".join(channel * 2 for channel in color[1:])
    return color


def _rgb(color: str) -> tuple[float, float, float]:
    normalized = _normalize_hex(color)
    if normalized is None:
        raise ValueError(f"Invalid hex color: {color}")
    return tuple(
        int(normalized[index : index + 2], 16) / 255.0
        for index in (1, 3, 5)
    )


def _relative_luminance(color: str) -> float:
    channels = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in _rgb(color)
    ]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(foreground: str, background: str) -> float:
    """Return the WCAG contrast ratio for two hexadecimal colors."""
    foreground_luminance = _relative_luminance(foreground)
    background_luminance = _relative_luminance(background)
    lighter = max(foreground_luminance, background_luminance)
    darker = min(foreground_luminance, background_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def _number(element: ET.Element, name: str, default: float = 0.0) -> float:
    try:
        return float(element.get(name, str(default)))
    except (TypeError, ValueError):
        return default


def _opacity(element: ET.Element) -> float:
    return max(0.0, min(1.0, _number(element, "opacity", 1.0)))


def _bounds(element: ET.Element) -> tuple[float, float, float, float] | None:
    if _tag(element) == "polygon":
        points = _polygon_points(element)
        if not points:
            return None
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)

    if element.get("width") is None or element.get("height") is None:
        return None
    return (
        _number(element, "x"),
        _number(element, "y"),
        _number(element, "width"),
        _number(element, "height"),
    )


def _polygon_points(element: ET.Element) -> list[tuple[float, float]]:
    raw = element.get("points", "")
    values = re.findall(r"-?\d+(?:\.\d+)?", raw)
    if len(values) < 6 or len(values) % 2:
        return []
    return [
        (float(values[index]), float(values[index + 1]))
        for index in range(0, len(values), 2)
    ]


def _point_in_polygon(
    point: tuple[float, float],
    polygon: list[tuple[float, float]],
) -> bool:
    x, y = point
    inside = False
    previous = len(polygon) - 1
    for current, (current_x, current_y) in enumerate(polygon):
        previous_x, previous_y = polygon[previous]
        crosses = (current_y > y) != (previous_y > y)
        if crosses:
            boundary_x = (
                (previous_x - current_x)
                * (y - current_y)
                / ((previous_y - current_y) or 1e-12)
                + current_x
            )
            if x < boundary_x:
                inside = not inside
        previous = current
    return inside


def _contains(element: ET.Element, point: tuple[float, float]) -> bool:
    element_tag = _tag(element)
    if element_tag == "polygon":
        points = _polygon_points(element)
        return bool(points) and _point_in_polygon(point, points)

    bounds = _bounds(element)
    if bounds is None:
        return False
    x, y, width, height = bounds
    point_x, point_y = point
    if not (x <= point_x <= x + width and y <= point_y <= y + height):
        return False

    shape_type = (element.get("type") or "rectangle").lower()
    if element_tag == "shape" and shape_type in {"circle", "ellipse", "oval"}:
        if width <= 0 or height <= 0:
            return False
        normalized_x = (point_x - (x + width / 2.0)) / (width / 2.0)
        normalized_y = (point_y - (y + height / 2.0)) / (height / 2.0)
        return normalized_x * normalized_x + normalized_y * normalized_y <= 1.0
    return True


def _blend(
    foreground: str,
    background: str,
    alpha: float,
) -> str:
    foreground_rgb = _rgb(foreground)
    background_rgb = _rgb(background)
    channels = [
        round((front * alpha + back * (1.0 - alpha)) * 255)
        for front, back in zip(foreground_rgb, background_rgb)
    ]
    return "#" + "".join(f"{channel:02X}" for channel in channels)


def _deduplicate(colors: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(color for color in colors if _normalize_hex(color)))


def _svg_colors(element: ET.Element) -> list[str]:
    serialized = "".join(element.itertext())
    return _deduplicate(
        normalized
        for match in _HEX_COLOR_RE.findall(serialized)
        if (normalized := _normalize_hex(match)) is not None
    )


def _surface_after_layer(
    colors: list[str],
    layer: ET.Element,
    point: tuple[float, float],
) -> list[str]:
    if not _contains(layer, point) or _opacity(layer) <= 0.0:
        return colors

    layer_tag = _tag(layer)
    if layer_tag == "image":
        return list(_UNKNOWN_SURFACE_COLORS)
    if layer_tag == "svg":
        # Inline SVG may be partially transparent. Include both its declared
        # colors and the surface below instead of pretending one fill covers
        # the entire textbox.
        return _deduplicate([*colors, *_svg_colors(layer)])
    if layer_tag not in _SOLID_TAGS and layer_tag not in _TEXT_TAGS:
        return colors

    fill = _normalize_hex(layer.get("fill") or layer.get("background"))
    if fill is None:
        return colors

    alpha = _opacity(layer)
    if alpha >= 0.999:
        return [fill]
    return _deduplicate(_blend(fill, background, alpha) for background in colors)


def _sample_points(textbox: ET.Element) -> list[tuple[float, float]]:
    bounds = _bounds(textbox)
    if bounds is None:
        return []
    x, y, width, height = bounds
    horizontal = (0.2, 0.5, 0.8)
    vertical = (0.25, 0.5, 0.75)
    return [
        (x + width * horizontal_ratio, y + height * vertical_ratio)
        for horizontal_ratio in horizontal
        for vertical_ratio in vertical
    ]


def _surface_colors(
    slide: ET.Element,
    preceding_layers: list[ET.Element],
    textbox: ET.Element,
) -> list[str]:
    own_fill = _normalize_hex(textbox.get("fill") or textbox.get("background"))
    if own_fill is not None:
        return [own_fill]

    slide_background = _normalize_hex(slide.get("background"))
    initial = [slide_background] if slide_background else list(_UNKNOWN_SURFACE_COLORS)
    surfaces: list[str] = []
    for point in _sample_points(textbox):
        colors = list(initial)
        for layer in preceding_layers:
            colors = _surface_after_layer(colors, layer, point)
        surfaces.extend(colors)
    return _deduplicate(surfaces or initial)


def _required_ratio(element: ET.Element, parent: ET.Element | None = None) -> float:
    size = _number(element, "size", _number(parent, "size", 24.0) if parent is not None else 24.0)
    bold_value = element.get("bold")
    if bold_value is None and parent is not None:
        bold_value = parent.get("bold")
    bold = str(bold_value or "false").lower() in {"1", "true", "yes"}
    # Use a conservative large-text definition. Small and supporting text must
    # meet 4.5:1 even when a template happens to use an 18pt font.
    return 3.0 if bold and size >= 24.0 else 4.5


def _minimum_contrast(foreground: str, backgrounds: Iterable[str]) -> float:
    return min(contrast_ratio(foreground, background) for background in backgrounds)


def _pick_readable_color(
    current: str,
    backgrounds: list[str],
    minimum_ratio: float,
    preferred_colors: Iterable[str],
) -> str | None:
    candidates = _deduplicate(
        [current, *preferred_colors, _SAFE_LIGHT, "#F8FAFC", _SAFE_DARK, "#000000"]
    )
    for candidate in candidates:
        if _minimum_contrast(candidate, backgrounds) >= minimum_ratio:
            return candidate
    return None


def _choose_backplate_pair(
    current: str,
    minimum_ratio: float,
    preferred_colors: Iterable[str],
) -> tuple[str, str]:
    text_candidates = _deduplicate(
        [current, *preferred_colors, _SAFE_LIGHT, _SAFE_DARK, "#000000"]
    )
    for background in (_SAFE_LIGHT, _SAFE_DARK):
        for foreground in text_candidates:
            if contrast_ratio(foreground, background) >= minimum_ratio:
                return foreground, background
    return _SAFE_LIGHT, _SAFE_DARK


def _repair_text_color(
    element: ET.Element,
    backgrounds: list[str],
    minimum_ratio: float,
    preferred_colors: Iterable[str],
    *,
    inherited_color: str | None = None,
) -> tuple[str, dict | None]:
    current = _normalize_hex(element.get("color") or inherited_color) or _SAFE_DARK
    replacement = _pick_readable_color(
        current,
        backgrounds,
        minimum_ratio,
        preferred_colors,
    )
    if replacement is None or replacement == current:
        return current, None

    element.set("color", replacement)
    return replacement, {
        "kind": "text_color",
        "from": current,
        "to": replacement,
        "minimum_ratio": minimum_ratio,
        "actual_ratio": round(_minimum_contrast(replacement, backgrounds), 2),
    }


def enforce_xml_text_contrast(
    xml_content: str,
    *,
    preferred_colors: Iterable[str] = (),
    protect_unknown_surfaces: bool = True,
) -> tuple[str, list[dict]]:
    """Repair low-contrast text in the final slide XML.

    Solid slide/shape/polygon surfaces are evaluated geometrically. If a text
    box sits on an image or another surface whose pixels cannot be proven safe,
    strict mode adds an opaque text-box backplate and then validates base and
    rich-run colors against that backplate.
    """
    if not isinstance(xml_content, str) or not xml_content.strip():
        return xml_content, []

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return xml_content, []

    normalized_preferences = _deduplicate(
        color
        for color in preferred_colors
        if _normalize_hex(color) is not None
    )
    corrections: list[dict] = []

    for slide_index, slide in enumerate(
        element for element in root.iter() if _tag(element) == "slide"
    ):
        preceding_layers: list[ET.Element] = []
        textbox_index = 0
        for element in list(slide):
            if _tag(element) not in _TEXT_TAGS:
                preceding_layers.append(element)
                continue

            backgrounds = _surface_colors(slide, preceding_layers, element)
            minimum_ratio = _required_ratio(element)
            current = _normalize_hex(element.get("color")) or _SAFE_DARK
            replacement = _pick_readable_color(
                current,
                backgrounds,
                minimum_ratio,
                normalized_preferences,
            )

            if replacement is None and protect_unknown_surfaces:
                replacement, backplate = _choose_backplate_pair(
                    current,
                    minimum_ratio,
                    normalized_preferences,
                )
                element.set("fill", backplate)
                element.set("line_color", "none")
                element.set("contrast_backplate", "true")
                backgrounds = [backplate]
                corrections.append(
                    {
                        "kind": "backplate",
                        "slide_index": slide_index,
                        "textbox_index": textbox_index,
                        "fill": backplate,
                    }
                )

            final_color, correction = _repair_text_color(
                element,
                backgrounds,
                minimum_ratio,
                normalized_preferences,
            )
            if correction:
                correction.update(
                    {
                        "slide_index": slide_index,
                        "textbox_index": textbox_index,
                    }
                )
                corrections.append(correction)

            gradient_colors = [
                color
                for field in ("gradient_start", "gradient_end")
                if (color := _normalize_hex(element.get(field))) is not None
            ]
            if gradient_colors and any(
                _minimum_contrast(color, backgrounds) < minimum_ratio
                for color in gradient_colors
            ):
                element.attrib.pop("gradient_start", None)
                element.attrib.pop("gradient_end", None)
                element.set("color", final_color)
                corrections.append(
                    {
                        "kind": "unsafe_text_gradient_removed",
                        "slide_index": slide_index,
                        "textbox_index": textbox_index,
                        "to": final_color,
                    }
                )

            for run_index, run in enumerate(
                child for child in list(element) if _tag(child) == "run"
            ):
                run_background = _normalize_hex(
                    run.get("highlight") or run.get("background")
                )
                run_surfaces = [run_background] if run_background else backgrounds
                run_ratio = _required_ratio(run, element)
                _, run_correction = _repair_text_color(
                    run,
                    run_surfaces,
                    run_ratio,
                    normalized_preferences,
                    inherited_color=element.get("color"),
                )
                if run_correction:
                    run_correction.update(
                        {
                            "slide_index": slide_index,
                            "textbox_index": textbox_index,
                            "run_index": run_index,
                        }
                    )
                    corrections.append(run_correction)

            # A filled textbox can be the visible surface for a later textbox.
            preceding_layers.append(element)
            textbox_index += 1

    if not corrections:
        return xml_content, []
    return ET.tostring(root, encoding="unicode"), corrections
