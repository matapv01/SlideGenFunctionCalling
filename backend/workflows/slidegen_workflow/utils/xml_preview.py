"""Render the XML slide schema to a browser preview for visual evaluation."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path


_BR_RE = re.compile(r"&lt;br\s*/?&gt;|<br\s*/?>", re.IGNORECASE)


def _number(value: str | None, fallback: float = 0.0) -> float:
    try:
        return float(value) if value is not None else fallback
    except (TypeError, ValueError):
        return fallback


def _attr(value: object) -> str:
    return html.escape(str(value), quote=True)


def _text_html(value: str | None) -> str:
    """Escape text while preserving the XML tool's literal ``<br>`` markers."""
    text = value or ""
    rendered = html.escape(text, quote=False)
    rendered = _BR_RE.sub("<br/>", rendered)
    return rendered.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")


def _source_url(source: str | None) -> str:
    value = (source or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://", "data:", "file:")):
        return value

    path = Path(value).expanduser()
    if path.exists():
        return path.resolve().as_uri()
    return value


def _color(value: str | None, fallback: str = "transparent") -> str:
    value = (value or "").strip()
    return fallback if not value or value.lower() == "none" else value


def _opacity(value: str | None, fallback: str = "1") -> str:
    parsed = _number(value, _number(fallback, 1.0))
    return str(max(0.0, min(1.0, parsed)))


def _style_bool(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _inline_svg(node: ET.Element) -> str:
    """Position an inline SVG string according to the XML element bounds."""
    raw_svg = "".join(node.itertext()).strip()
    if not raw_svg:
        return ""

    match = re.search(r"<svg\b([^>]*)>", raw_svg, flags=re.IGNORECASE)
    if not match:
        return ""

    attrs = match.group(1)
    attrs = re.sub(r"\s+(?:x|y|width|height)\s*=\s*(?:\"[^\"]*\"|'[^']*')", "", attrs, flags=re.IGNORECASE)
    x = _number(node.get("x"))
    y = _number(node.get("y"))
    width = _number(node.get("width"), 1600)
    height = _number(node.get("height"), 900)
    replacement = (
        f'<svg x="{_attr(x)}" y="{_attr(y)}" width="{_attr(width)}" '
        f'height="{_attr(height)}" preserveAspectRatio="none"{attrs}>'
    )
    return raw_svg[: match.start()] + replacement + raw_svg[match.end() :]


def _render_image(node: ET.Element) -> str:
    source = _source_url(node.get("src"))
    if not source:
        return ""

    x = _number(node.get("x"))
    y = _number(node.get("y"))
    width = _number(node.get("width"))
    height = _number(node.get("height"))
    fit = (node.get("fit") or "cover").strip().lower()
    object_fit = "contain" if fit == "contain" else "cover"
    opacity = _opacity(node.get("opacity"))
    return (
        f'<foreignObject x="{_attr(x)}" y="{_attr(y)}" width="{_attr(width)}" '
        f'height="{_attr(height)}" opacity="{_attr(opacity)}">'
        '<div xmlns="http://www.w3.org/1999/xhtml" '
        'style="width:100%;height:100%;overflow:hidden;background:transparent;">'
        f'<img src="{_attr(source)}" alt="" '
        f'style="display:block;width:100%;height:100%;object-fit:{object_fit};" />'
        "</div></foreignObject>"
    )


def _shape_points(shape_type: str, width: float, height: float) -> str | None:
    if shape_type == "triangle":
        return f"{width / 2},0 {width},{height} 0,{height}"
    if shape_type == "diamond":
        return f"{width / 2},0 {width},{height / 2} {width},{height} 0,{height / 2}"
    if shape_type == "hexagon":
        inset = width * 0.2
        return f"{inset},0 {width - inset},0 {width},{height / 2} {width - inset},{height} {inset},{height} 0,{height / 2}"
    if shape_type == "chevron":
        inset = width * 0.22
        return f"0,0 {width - inset},0 {width},{height / 2} {width - inset},{height} 0,{height} {inset},{height / 2}"
    if shape_type == "right_arrow":
        shaft = height * 0.32
        return f"0,{height / 2 - shaft} {width * 0.62},{height / 2 - shaft} {width * 0.62},0 {width},{height / 2} {width * 0.62},{height} {width * 0.62},{height / 2 + shaft} 0,{height / 2 + shaft}"
    return None


def _render_shape(node: ET.Element) -> str:
    x = _number(node.get("x"))
    y = _number(node.get("y"))
    width = _number(node.get("width"))
    height = _number(node.get("height"))
    shape_type = (node.get("type") or "rectangle").strip().lower()
    fill = _color(node.get("fill"))
    stroke = _color(node.get("line_color"))
    stroke_width = _number(node.get("line_width"), 1)
    opacity = _opacity(node.get("opacity"))
    rotation = _number(node.get("rotation"))
    transform = ""
    if rotation:
        transform = f' transform="rotate({_attr(rotation)} {_attr(x + width / 2)} {_attr(y + height / 2)})"'

    points = _shape_points(shape_type, width, height)
    if points:
        return (
            f'<polygon points="{_attr(points)}" fill="{_attr(fill)}" '
            f'stroke="{_attr(stroke)}" stroke-width="{_attr(stroke_width)}" '
            f'opacity="{_attr(opacity)}" transform="translate({_attr(x)} {_attr(y)})" />'
        )

    if shape_type in {"circle", "ellipse"}:
        return (
            f'<ellipse cx="{_attr(x + width / 2)}" cy="{_attr(y + height / 2)}" '
            f'rx="{_attr(width / 2)}" ry="{_attr(height / 2)}" fill="{_attr(fill)}" '
            f'stroke="{_attr(stroke)}" stroke-width="{_attr(stroke_width)}" '
            f'opacity="{_attr(opacity)}"{transform} />'
        )

    radius = min(width, height) * 0.12 if shape_type == "rounded_rectangle" else 0
    return (
        f'<rect x="{_attr(x)}" y="{_attr(y)}" width="{_attr(width)}" height="{_attr(height)}" '
        f'rx="{_attr(radius)}" fill="{_attr(fill)}" stroke="{_attr(stroke)}" '
        f'stroke-width="{_attr(stroke_width)}" opacity="{_attr(opacity)}"{transform} />'
    )


def _render_polygon(node: ET.Element) -> str:
    points = " ".join(node.get("points", "").split())
    if not points:
        return ""
    fill = _color(node.get("fill"))
    stroke = _color(node.get("line_color"))
    stroke_width = _number(node.get("line_width"), 1)
    return (
        f'<polygon points="{_attr(points)}" fill="{_attr(fill)}" '
        f'stroke="{_attr(stroke)}" stroke-width="{_attr(stroke_width)}" '
        f'opacity="{_attr(_opacity(node.get("opacity")))}" />'
    )


def _render_line(node: ET.Element) -> str:
    return (
        f'<line x1="{_attr(_number(node.get("x1")))}" y1="{_attr(_number(node.get("y1")))}" '
        f'x2="{_attr(_number(node.get("x2")))}" y2="{_attr(_number(node.get("y2")))}" '
        f'stroke="{_attr(_color(node.get("color"), "#000000"))}" '
        f'stroke-width="{_attr(_number(node.get("width"), 1))}" />'
    )


def _run_html(node: ET.Element, parent: ET.Element) -> str:
    text = _text_html("".join(node.itertext()))
    color = node.get("color") or parent.get("color") or "#111827"
    styles = [f"color:{color};"]
    if _style_bool(node.get("bold")) or _style_bool(parent.get("bold")):
        styles.append("font-weight:700;")
    if _style_bool(node.get("italic")) or _style_bool(parent.get("italic")):
        styles.append("font-style:italic;")
    if node.get("highlight") or node.get("background"):
        styles.append(f"background:{node.get('highlight') or node.get('background')};")
    return f'<span style="{_attr("".join(styles))}">{text}</span>'


def _textbox_content(node: ET.Element) -> str:
    if not list(node):
        return _text_html(node.text)

    parts = [_text_html(node.text)]
    for child in list(node):
        tag = child.tag.rsplit("}", 1)[-1].lower()
        if tag == "run":
            parts.append(_run_html(child, node))
        elif tag == "math-field":
            formula = child.get("value") or "".join(child.itertext())
            parts.append(
                f'<span style="font-style:italic;font-family:serif;white-space:pre-wrap;">'
                f"{_text_html(formula)}</span>"
            )
        else:
            parts.append(_text_html("".join(child.itertext())))
        parts.append(_text_html(child.tail))
    return "".join(parts)


def _render_textbox(node: ET.Element, point_to_px: float) -> str:
    x = _number(node.get("x"))
    y = _number(node.get("y"))
    width = _number(node.get("width"))
    height = _number(node.get("height"))
    font_size = _number(node.get("size"), 18) * point_to_px
    line_spacing = _number(node.get("line_spacing"), 1.08)
    align = (node.get("align") or "left").strip().lower()
    vertical = (node.get("vertical_align") or "top").strip().lower()
    justify = {"middle": "center", "center": "center", "bottom": "flex-end"}.get(vertical, "flex-start")
    font = node.get("font") or "Arial"
    font_weight = "700" if _style_bool(node.get("bold")) else node.get("font_weight", "400")
    font_style = "italic" if _style_bool(node.get("italic")) else "normal"
    white_space = "nowrap" if _style_bool(node.get("single_line")) else "pre-wrap"
    overflow = "hidden" if (node.get("overflow") or "clip") == "clip" else "visible"
    styles = (
        "width:100%;height:100%;"
        f"box-sizing:border-box;display:flex;flex-direction:column;justify-content:{justify};"
        f"font-family:{html.escape(font, quote=True)};font-size:{font_size}px;"
        f"font-weight:{font_weight};font-style:{font_style};color:{_attr(node.get('color') or '#111827')};"
        f"text-align:{_attr(align)};line-height:{line_spacing};white-space:{white_space};"
        f"overflow:{overflow};overflow-wrap:break-word;"
        f"padding:{_number(node.get('margin_top'))}px {_number(node.get('margin_right'))}px "
        f"{_number(node.get('margin_bottom'))}px {_number(node.get('margin_left'))}px;"
    )
    return (
        f'<foreignObject x="{_attr(x)}" y="{_attr(y)}" width="{_attr(width)}" '
        f'height="{_attr(height)}"><div xmlns="http://www.w3.org/1999/xhtml" '
        f'style="{_attr(styles)}">{_textbox_content(node)}</div></foreignObject>'
    )


def _render_element(node: ET.Element, point_to_px: float) -> str:
    tag = node.tag.rsplit("}", 1)[-1].lower()
    if tag == "image":
        return _render_image(node)
    if tag == "shape":
        return _render_shape(node)
    if tag == "polygon":
        return _render_polygon(node)
    if tag == "line":
        return _render_line(node)
    if tag in {"textbox", "text"}:
        return _render_textbox(node, point_to_px)
    if tag == "svg":
        return _inline_svg(node)
    if tag in {"piechart", "barchart", "linechart"}:
        x = _number(node.get("x"))
        y = _number(node.get("y"))
        width = _number(node.get("width"), 300)
        height = _number(node.get("height"), 200)
        return (
            f'<rect x="{_attr(x)}" y="{_attr(y)}" width="{_attr(width)}" height="{_attr(height)}" '
            'fill="transparent" stroke="#94a3b8" stroke-dasharray="8 6" />'
        )
    return ""


def build_xml_preview_html(xml_content: str, slide_index: int = 0) -> str:
    """Build a self-contained browser page for one XML slide."""
    root = ET.fromstring(xml_content)
    if root.tag.rsplit("}", 1)[-1] != "presentation":
        raise ValueError("XML root element must be <presentation>.")

    width = _number(root.get("width"), 1600)
    height = _number(root.get("height"), 900)
    slide_width_inches = _number(root.get("slideWidthInches"), 13.333)
    slide_nodes = [node for node in root if node.tag.rsplit("}", 1)[-1] == "slide"]
    if not slide_nodes:
        raise ValueError("XML presentation has no slide.")
    slide = slide_nodes[max(0, min(slide_index, len(slide_nodes) - 1))]
    point_to_px = width / max(1.0, slide_width_inches * 72.0)
    background = _color(slide.get("background"), "#FFFFFF")
    elements = "\n".join(_render_element(node, point_to_px) for node in slide if isinstance(node.tag, str))

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
html, body {{ margin: 0; width: 100%; height: 100%; overflow: hidden; background: #ffffff; }}
body {{ display: flex; align-items: center; justify-content: center; }}
svg.preview {{ display: block; width: 100vw; height: 100vh; }}
</style></head><body>
<svg class="preview" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {_attr(width)} {_attr(height)}" preserveAspectRatio="none">
  <rect x="0" y="0" width="{_attr(width)}" height="{_attr(height)}" fill="{_attr(background)}" />
  {elements}
</svg>
</body></html>"""
