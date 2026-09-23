"""Apply a deck-level style contract to compatible layout tool arguments."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, Set


_STYLE_FIELD_MAP = {
    "background_color": "background_color",
    "bg_color": "background_color",
    "main_bg_color": "background_color",
    "main_background_color": "background_color",
    "slide_background_color": "background_color",
    "primary_color": "primary_color",
    "dark_color": "primary_color",
    "secondary_color": "secondary_color",
    "accent_color": "accent_color",
    "theme_color": "accent_color",
    "highlight_color": "accent_color",
    "title_color": "primary_color",
    "main_title_color": "primary_color",
    "headline_color": "primary_color",
    "heading_color": "primary_color",
    "text_color": "text_color",
    "body_color": "text_color",
    "body_text_color": "text_color",
    "content_color": "text_color",
    "card_title_color": "text_color",
    "card_body_color": "text_color",
    "item_title_color": "text_color",
    "item_body_color": "text_color",
    "description_color": "secondary_color",
    "subtitle_color": "secondary_color",
    "footer_color": "secondary_color",
    "font_family": "font_family",
    "font": "font_family",
}


def _rgb(hex_color: str):
    if not isinstance(hex_color, str):
        return None
    value = hex_color.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(character * 2 for character in value)
    if len(value) != 6:
        return None
    try:
        return tuple(int(value[index:index + 2], 16) / 255.0 for index in (0, 2, 4))
    except ValueError:
        return None


def _relative_luminance(hex_color: str):
    color = _rgb(hex_color)
    if color is None:
        return None
    channels = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in color
    ]
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def _contrast_ratio(foreground: str, background: str) -> float:
    foreground_luminance = _relative_luminance(foreground)
    background_luminance = _relative_luminance(background)
    if foreground_luminance is None or background_luminance is None:
        return 0.0
    lighter = max(foreground_luminance, background_luminance)
    darker = min(foreground_luminance, background_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def _ensure_contrast(
    foreground: str,
    background: str,
    minimum_ratio: float,
    alternatives: Iterable[str],
) -> str:
    if _contrast_ratio(foreground, background) >= minimum_ratio:
        return foreground
    valid_alternatives = [
        color for color in alternatives
        if _contrast_ratio(color, background) >= minimum_ratio
    ]
    if valid_alternatives:
        return valid_alternatives[0]
    return max(
        [foreground, *alternatives],
        key=lambda color: _contrast_ratio(color, background),
    )


def _apply_contrast_guards(
    arguments: Dict[str, Any],
    fields: Set[str],
    deck_style: Dict[str, Any],
) -> None:
    """Keep semantic text colors readable on their actual layout surfaces."""
    dark_panel = arguments.get("dark_panel_color")
    dark_panel_text_fields = {
        "title_color",
        "heading_color",
        "body_color",
        "subtitle_color",
        "footer_color",
    }
    if "dark_panel_color" in fields and dark_panel:
        accent = deck_style.get("accent_color", "#FFFFFF")
        light = deck_style.get("background_color", "#FFFFFF")
        for field_name in dark_panel_text_fields:
            if field_name not in fields or not arguments.get(field_name):
                continue
            is_large_text = field_name in {"title_color", "heading_color"}
            alternatives = (
                [accent, "#FFFFFF", "#111111"]
                if field_name == "title_color"
                else ["#FFFFFF", light, accent, "#111111"]
            )
            arguments[field_name] = _ensure_contrast(
                arguments[field_name],
                dark_panel,
                3.0 if is_large_text else 4.5,
                alternatives,
            )

    def contrast_alternatives(surface_color: str) -> list[str]:
        accent = deck_style.get("accent_color", "#2563EB")
        text = deck_style.get("text_color", "#1F2937")
        luminance = _relative_luminance(surface_color)
        if luminance is not None and luminance < 0.35:
            return ["#FFFFFF", "#F8FAFC", accent, text, "#111111"]
        return ["#111111", text, deck_style.get("secondary_color", "#475569"), accent, "#FFFFFF"]

    # Generic light/dark surface guards. A chart panel is not necessarily the
    # deck's primary color, so protect the text that is rendered on each
    # surface instead of forcing every panel_color to primary_color.
    for surface_field, text_fields in (
        (
            "background_color",
            ("title_color", "text_color", "footer_color", "subtitle_color"),
        ),
        (
            "panel_color",
            ("axis_text_color", "legend_text_color", "panel_text_color", "chart_text_color"),
        ),
    ):
        surface_color = arguments.get(surface_field)
        if not surface_color:
            continue

        alternatives = contrast_alternatives(surface_color)
        for text_field in text_fields:
            if text_field not in fields or not arguments.get(text_field):
                continue
            if surface_field == "background_color" and dark_panel and text_field in dark_panel_text_fields:
                continue

            arguments[text_field] = _ensure_contrast(
                arguments[text_field],
                surface_color,
                3.0 if text_field == "title_color" else 4.5,
                alternatives,
            )

    surface_groups = (
        ("card_color", ("card_title_color", "card_body_color")),
        ("content_background_color", ("item_title_color", "item_body_color")),
        ("accent_color", ("star_color",)),
    )
    for surface_field, text_fields in surface_groups:
        surface_color = arguments.get(surface_field)
        if not surface_color:
            continue
        for text_field in text_fields:
            if text_field in fields and arguments.get(text_field):
                arguments[text_field] = _ensure_contrast(
                    arguments[text_field],
                    surface_color,
                    4.5,
                    ["#FFFFFF", "#111111"],
                )


def _tool_fields(tool: Any) -> Set[str]:
    args = getattr(tool, "args", None)
    if isinstance(args, dict):
        return set(args)
    schema = getattr(tool, "args_schema", None)
    if schema is not None:
        if hasattr(schema, "model_json_schema"):
            return set(schema.model_json_schema().get("properties", {}))
        if hasattr(schema, "schema"):
            return set(schema.schema().get("properties", {}))
    return set()


def apply_deck_style_to_tool_call(
    tool_call: Dict[str, Any],
    available_tools: Iterable[Any],
    deck_style: Dict[str, Any],
) -> Dict[str, Any]:
    """Override only style parameters explicitly supported by the chosen tool."""
    result = deepcopy(tool_call or {})
    if not result or not deck_style:
        return result

    selected = next(
        (tool for tool in available_tools if getattr(tool, "name", None) == result.get("name")),
        None,
    )
    if selected is None:
        return result

    fields = _tool_fields(selected)
    arguments = dict(result.get("arguments") or {})
    for argument_name, style_name in _STYLE_FIELD_MAP.items():
        if argument_name in fields and deck_style.get(style_name):
            arguments[argument_name] = deck_style[style_name]
    _apply_contrast_guards(arguments, fields, deck_style)
    result["arguments"] = arguments
    return result
