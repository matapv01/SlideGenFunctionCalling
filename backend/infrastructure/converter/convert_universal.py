from __future__ import annotations

import argparse
import base64
import binascii
from html import escape as html_escape
import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, unquote_to_bytes, urlparse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from lxml import etree
from pptx import Presentation
from pptx.chart.data import ChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

from backend.workflows.slidegen_workflow.utils.rich_text import (
    materialize_markdown_bold_runs,
    materialize_math_fields_in_xml,
)
from backend.infrastructure.converter.omml import (
    A_NS,
    A14_NS,
    M_NS,
    latex_to_omml,
)
from backend.config import MATHLIVE_PACKAGE_DIR, OUTPUT_DIR, PUPPETEER_EXECUTABLE_PATH


MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


class XMLSlideConverter:
    def __init__(
        self,
        xml_path: Path,
        output_path: Path,
        open_after_convert: bool = True,
    ) -> None:
        self.xml_path = xml_path.resolve()
        self.output_path = output_path.resolve()
        self.open_after_convert = open_after_convert
        self.base_dir = self.xml_path.parent

        self.prs = Presentation()
        self.canvas_width = 1600.0
        self.canvas_height = 900.0
        self.slide_width_inches = 13.333
        self.slide_height_inches = 7.5

        self.renderers = {
            "textbox": self.render_textbox,
            "shape": self.render_shape,
            "line": self.render_line,
            "polygon": self.render_polygon,
            "image": self.render_image,
            "svg": self.render_svg,
            "table": self.render_table,
            "piechart": self.render_chart,
            "barchart": self.render_chart,
            "linechart": self.render_chart,
        }

    def svg_renderer_candidates(self) -> list[Path]:
        candidates = [
            Path(
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            ),
            Path(
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ),
            Path(
                r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            ),
            Path("/usr/local/bin/chromium-playwright"),
            Path("/usr/bin/chromium"),
            Path("/usr/bin/chromium-browser"),
        ]

        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            candidates.append(
                Path(local_appdata)
                / "Google/Chrome/Application/chrome.exe"
            )

        if PUPPETEER_EXECUTABLE_PATH:
            candidates.insert(0, Path(PUPPETEER_EXECUTABLE_PATH))

        return [candidate for candidate in candidates if candidate.exists()]

    @staticmethod
    def mathlive_package_dir() -> Path | None:
        """Locate the local MathLive package used by the web preview."""
        repo_root = Path(__file__).resolve().parents[3]
        candidates = [
            repo_root / "frontend" / "node_modules" / "mathlive",
        ]
        if MATHLIVE_PACKAGE_DIR:
            candidates.insert(0, Path(MATHLIVE_PACKAGE_DIR).expanduser())

        for candidate in candidates:
            if (candidate / "mathlive-ssr.min.mjs").exists():
                return candidate
        return None

    def latex_to_mathlive_markup(self, formulas: list[str]) -> list[str]:
        """Convert LaTeX strings to MathLive HTML using the local SSR bundle."""
        if not formulas:
            return []

        node = shutil.which("node")
        package_dir = self.mathlive_package_dir()
        if node is None or package_dir is None:
            print(
                "Khong the render LaTeX: can node va frontend/node_modules/mathlive."
            )
            return []

        module_uri = (package_dir / "mathlive-ssr.min.mjs").resolve().as_uri()
        node_script = f"""
import fs from "node:fs";
import {{ convertLatexToMarkup }} from {json.dumps(module_uri)};

const formulas = JSON.parse(fs.readFileSync(0, "utf8"));
const markup = formulas.map((formula) => {{
  try {{
    return convertLatexToMarkup(String(formula || ""));
  }} catch (error) {{
    return "";
  }}
}});
process.stdout.write(JSON.stringify(markup));
"""

        try:
            completed = subprocess.run(
                [node, "--input-type=module", "-e", node_script],
                input=json.dumps(formulas, ensure_ascii=False),
                capture_output=True,
                text=True,
                timeout=20,
                check=True,
            )
            result = json.loads(completed.stdout)
            if isinstance(result, list) and len(result) == len(formulas):
                return [str(markup) for markup in result]
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
            print(f"Khong the convert LaTeX bang MathLive: {exc}")

        return []

    @staticmethod
    def mathlive_static_css(package_dir: Path) -> str:
        """Inline MathLive CSS and make its local font URLs browser-safe."""
        css_path = package_dir / "mathlive-static.css"
        if not css_path.exists():
            return ""
        css = css_path.read_text(encoding="utf-8")
        font_dir = package_dir / "fonts"

        # Chromium can reject file:// font URLs when the screenshot page is
        # another local file.  Embed the small KaTeX font files directly so
        # ordinary glyphs (E, a, mc, Greek letters, ...) are not rendered as
        # transparent while CSS-only fraction/radical lines still appear.
        for font_path in font_dir.glob("*"):
            if font_path.suffix.lower() not in {".woff", ".woff2", ".ttf"}:
                continue
            try:
                encoded = base64.b64encode(font_path.read_bytes()).decode("ascii")
            except OSError:
                continue
            mime_type = {
                ".woff": "font/woff",
                ".woff2": "font/woff2",
                ".ttf": "font/ttf",
            }[font_path.suffix.lower()]
            css = css.replace(
                f"url(fonts/{font_path.name})",
                f"url(data:{mime_type};base64,{encoded})",
            )

        # Make the browser wait for these embedded fonts instead of taking a
        # screenshot during a font-display swap.
        return css.replace('font-display:"swap"', "font-display:block")

    @staticmethod
    def latex_to_readable_text(latex: str) -> str:
        """Convert common LaTeX constructs to a readable math fallback.

        This is only used when the headless browser cannot rasterize text.
        Keeping the fallback Unicode-based means PowerPoint still receives a
        visible, editable text representation instead of a blank PNG.
        """
        value = (latex or "").replace("\\r\\n", "\n").replace("\\n", "\n")
        # XML generated by older slide tools encoded line breaks as literal
        # ``<br>`` text. Treat those markers as breaks in raster fallbacks.
        value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)

        greek = {
            "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ",
            "epsilon": "ε", "theta": "θ", "lambda": "λ", "mu": "μ",
            "pi": "π", "sigma": "σ", "phi": "φ", "omega": "ω",
            "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ",
            "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Omega": "Ω",
        }
        symbols = {
            "pm": "±", "times": "×", "cdot": "·", "le": "≤",
            "leq": "≤", "ge": "≥", "geq": "≥", "neq": "≠",
            "approx": "≈", "in": "∈", "notin": "∉", "to": "→",
            "rightarrow": "→", "infty": "∞", "partial": "∂",
            "nabla": "∇", "sum": "∑", "prod": "∏", "int": "∫",
            "log": "log", "ln": "ln", "sin": "sin", "cos": "cos",
            "tan": "tan", "lim": "lim",
        }
        mathcal = {
            "A": "𝒜", "B": "ℬ", "C": "𝒞", "D": "𝒟", "E": "ℰ",
            "F": "ℱ", "G": "𝒢", "H": "ℋ", "I": "ℐ", "J": "𝒥",
            "K": "𝒦", "L": "ℒ", "M": "ℳ", "N": "𝒩", "O": "𝒪",
            "P": "𝒫", "Q": "𝒬", "R": "ℛ", "S": "𝒮", "T": "𝒯",
            "U": "𝒰", "V": "𝒱", "W": "𝒲", "X": "𝒳", "Y": "𝒴",
            "Z": "𝒵",
        }
        superscript = str.maketrans(
            "0123456789+-=()nixy",
            "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱˣʸ",
        )
        subscript = str.maketrans(
            "0123456789+-=()aehiijklmnoprstuvx",
            "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ",
        )

        def group_value(value: str, start: int) -> tuple[str, int] | None:
            if start >= len(value) or value[start] != "{":
                return None
            depth = 0
            for index in range(start, len(value)):
                if value[index] == "{":
                    depth += 1
                elif value[index] == "}":
                    depth -= 1
                    if depth == 0:
                        return value[start + 1:index], index + 1
            return None

        def group_value(value: str, start: int) -> tuple[str, int] | None:
            if start >= len(value) or value[start] != "{":
                return None
            depth = 0
            for index in range(start, len(value)):
                if value[index] == "{":
                    depth += 1
                elif value[index] == "}":
                    depth -= 1
                    if depth == 0:
                        return value[start + 1:index], index + 1
            return None

        def script_value(text: str, table: dict[int, str], fallback: str) -> str:
            compact = re.sub(r"\s+", "", text)
            mapped = compact.translate(table)
            return mapped if mapped != compact else f"{fallback}{compact}{fallback}"

        # Resolve commands with braced arguments before removing braces.
        for _ in range(4):
            previous = value
            value = re.sub(
                r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}",
                lambda match: (
                    f"{XMLSlideConverter.latex_to_readable_text(match.group(1))}⁄"
                    f"{XMLSlideConverter.latex_to_readable_text(match.group(2))}"
                ),
                value,
            )
            value = re.sub(
                r"\\sqrt\s*\{([^{}]*)\}",
                lambda match: f"√({XMLSlideConverter.latex_to_readable_text(match.group(1))})",
                value,
            )
            value = re.sub(
                r"\\(?:text|mathrm|mathbf)\s*\{([^{}]*)\}",
                lambda match: match.group(1),
                value,
            )
            value = re.sub(
                r"\\mathcal\s*\{([^{}]*)\}",
                lambda match: "".join(mathcal.get(char, char) for char in match.group(1)),
                value,
            )
            value = re.sub(
                r"\\hat\s*\{([^{}]*)\}",
                lambda match: match.group(1) + "̂",
                value,
            )
            value = re.sub(
                r"\\vec\s*\{([^{}]*)\}",
                lambda match: match.group(1) + "⃗",
                value,
            )
            if value == previous:
                break

        value = re.sub(
            r"\^\s*\{([^{}]*)\}",
            lambda match: script_value(match.group(1), superscript, "^"),
            value,
        )
        value = re.sub(
            r"_\s*\{([^{}]*)\}",
            lambda match: script_value(match.group(1), subscript, "_"),
            value,
        )
        value = re.sub(
            r"\^\s*([A-Za-z0-9+\-=()])",
            lambda match: script_value(match.group(1), superscript, "^"),
            value,
        )
        value = re.sub(
            r"_\s*([A-Za-z0-9+\-=()])",
            lambda match: script_value(match.group(1), subscript, "_"),
            value,
        )
        value = re.sub(
            r"\\([A-Za-z]+)",
            lambda match: greek.get(match.group(1), symbols.get(match.group(1), match.group(1))),
            value,
        )
        value = value.replace("\\left", "").replace("\\right", "")
        value = value.replace("\\,", " ").replace("\\!", "")
        value = value.replace("\\\\", "\n").replace("{", "").replace("}", "")
        return re.sub(r"[ \t]+", " ", value).strip()

    @staticmethod
    def _fallback_font_path(element: ET.Element) -> Path | None:
        candidates = [
            Path(element.get("font_path", "")),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        return next((path for path in candidates if str(path) and path.exists()), None)

    def render_latex_fallback_image(
        self,
        element: ET.Element,
        png_path: Path,
    ) -> bool:
        """Render a visible Unicode-math fallback with Pillow."""
        font_path = self._fallback_font_path(element)
        if font_path is None:
            return False

        width = max(1, round(float(element.get("width", "300"))))
        height = max(1, round(float(element.get("height", "100"))))
        try:
            image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            raw_color = (element.get("color") or "#000000").lstrip("#")
            if len(raw_color) == 3:
                raw_color = "".join(char * 2 for char in raw_color)
            color = tuple(int(raw_color[index:index + 2], 16) for index in (0, 2, 4))
            source_parts: list[str] = []
            if element.text:
                source_parts.append(element.text)
            for child in element:
                if child.tag == "math-field":
                    source_parts.append(child.get("value") or child.text or "")
                else:
                    source_parts.append("".join(child.itertext()))
                if child.tail:
                    source_parts.append(child.tail)
            readable = XMLSlideConverter.latex_to_readable_text("".join(source_parts))
            if not readable:
                return False

            base_size = max(8, round(float(element.get("size", "24")) * 96 / 72))
            margin_left = max(0, round(float(element.get("margin_left", "0"))))
            margin_top = max(0, round(float(element.get("margin_top", "0"))))
            selected_font = None
            selected_lines = [readable]
            for size in range(base_size, 7, -1):
                font = ImageFont.truetype(str(font_path), size)
                lines: list[str] = []
                for paragraph in readable.splitlines() or [readable]:
                    current = ""
                    for char in paragraph:
                        candidate = current + char
                        if current and draw.textlength(candidate, font=font) > max(1, width - margin_left - 4):
                            lines.append(current)
                            current = char
                        else:
                            current = candidate
                    lines.append(current)
                bbox = draw.multiline_textbbox(
                    (margin_left, margin_top),
                    "\n".join(lines),
                    font=font,
                    spacing=max(1, round(size * 0.2)),
                )
                if bbox[3] - bbox[1] <= max(1, height - margin_top):
                    selected_font = font
                    selected_lines = lines
                    break
            if selected_font is None:
                selected_font = ImageFont.truetype(str(font_path), 7)

            draw.multiline_text(
                (margin_left, margin_top),
                "\n".join(selected_lines),
                font=selected_font,
                fill=(*color, 255),
                spacing=max(1, round(selected_font.size * 0.2)),
            )
            image.save(png_path)
            return image.getchannel("A").getbbox() is not None
        except (OSError, ValueError, TypeError):
            return False

    def math_textbox_html(
        self,
        element: ET.Element,
        formula_markup: list[str],
    ) -> str:
        """Build a fixed-size HTML canvas for a textbox containing formulas."""
        package_dir = self.mathlive_package_dir()
        css = self.mathlive_static_css(package_dir) if package_dir else ""
        formula_index = 0
        content: list[str] = []

        def html_text(value: str) -> str:
            # Some LLM calls use the two-character sequence ``\\n`` instead
            # of an actual newline in the surrounding prose.  Normalize it
            # here without touching the LaTeX stored inside math-field nodes.
            value = value.replace("\\r\\n", "\n").replace("\\n", "\n")
            value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
            return html_escape(value).replace("\n", "<br>")

        if element.text:
            content.append(html_text(element.text))

        for child in element:
            if child.tag == "math-field":
                markup = (
                    formula_markup[formula_index]
                    if formula_index < len(formula_markup)
                    else ""
                )
                formula_index += 1
                if markup:
                    content.append(
                        '<span class="math-formula">'
                        f"{markup}"
                        "</span>"
                    )
                else:
                    content.append(html_escape(child.text or ""))
            elif child.tag == "br":
                content.append("<br>")
            else:
                content.append(html_escape("".join(child.itertext())))

            if child.tail:
                content.append(html_text(child.tail))

        width = max(1, round(float(element.get("width", "300"))))
        height = max(1, round(float(element.get("height", "100"))))
        font_size = float(element.get("size", "24"))
        color = html_escape(element.get("color", "#000000"), quote=True)
        font = html_escape(element.get("font", "Arial"), quote=True)
        align = element.get("align", "left").lower()
        vertical_align = element.get("vertical_align", "top").lower()
        justify = {
            "left": "flex-start",
            "center": "center",
            "right": "flex-end",
        }.get(align, "flex-start")
        align_items = {
            "top": "flex-start",
            "middle": "center",
            "center": "center",
            "bottom": "flex-end",
        }.get(vertical_align, "flex-start")

        margin_left = element.get("margin_left", "0")
        margin_right = element.get("margin_right", "0")
        margin_top = element.get("margin_top", "0")
        margin_bottom = element.get("margin_bottom", "0")
        weight = "700" if self.to_bool(element.get("bold")) else "400"
        style = (
            f"width:{width}px;height:{height}px;"
            "box-sizing:border-box;overflow:hidden;"
            "background:transparent;display:flex;"
            f"align-items:{align_items};justify-content:{justify};"
        )
        inner_style = (
            "width:100%;white-space:pre-wrap;word-break:break-word;"
            f"text-align:{align};font-family:{font};font-size:{font_size}pt;"
            f"font-weight:{weight};line-height:{element.get('line_spacing', '1.0')};"
            f"color:{color};padding:{margin_top}pt {margin_right}pt "
            f"{margin_bottom}pt {margin_left}pt;box-sizing:border-box;"
        )
        return (
            "<!doctype html><html><head><meta charset='utf-8'>"
            f"<style>{css}"
            ".math-formula{display:inline-block;vertical-align:middle;}"
            ".math-formula math-field,.math-formula *{color:inherit !important;}"
            f"</style></head><body style='margin:0;"
            "padding:0;background:transparent;overflow:hidden;'>"
            f"<div style='{style}'><div style='{inner_style}'>"
            + "".join(content)
            + "</div></div></body></html>"
        )

    @staticmethod
    def _normalized_math_color(value: str | None) -> str:
        raw = str(value or "#000000").strip().lstrip("#")
        if len(raw) == 3:
            raw = "".join(char * 2 for char in raw)
        if not re.fullmatch(r"[0-9A-Fa-f]{6}", raw):
            return "#000000"
        return f"#{raw.upper()}"

    @staticmethod
    def _xml_tag(namespace: str, name: str) -> str:
        return f"{{{namespace}}}{name}"

    def _append_native_text_run(
        self,
        paragraph,
        text: str,
        element: ET.Element,
        *,
        color: str | None = None,
    ) -> None:
        """Append ordinary DrawingML text beside an OMML math run."""
        if not text:
            return

        font_name = element.get("font", "Arial")
        font_size = element.get("size", "24")
        bold = self.to_bool(element.get("bold"))
        italic = self.to_bool(element.get("italic"))
        text_color = self._normalized_math_color(color or element.get("color"))

        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        for index, line in enumerate(text.split("\n")):
            if index:
                paragraph._p.append(
                    etree.Element(self._xml_tag(A_NS, "br"))
                )
            if not line:
                continue
            run = etree.Element(self._xml_tag(A_NS, "r"))
            run_properties = etree.SubElement(
                run,
                self._xml_tag(A_NS, "rPr"),
                sz=str(max(1, round(float(font_size) * 100))),
                b="1" if bold else "0",
                i="1" if italic else "0",
            )
            solid_fill = etree.SubElement(
                run_properties,
                self._xml_tag(A_NS, "solidFill"),
            )
            etree.SubElement(
                solid_fill,
                self._xml_tag(A_NS, "srgbClr"),
                val=text_color.lstrip("#"),
            )
            etree.SubElement(
                run_properties,
                self._xml_tag(A_NS, "latin"),
                typeface=font_name,
            )
            text_node = etree.SubElement(run, self._xml_tag(A_NS, "t"))
            text_node.text = line
            paragraph._p.append(run)

    def _append_native_math(
        self,
        paragraph,
        formula: str,
        element: ET.Element,
        *,
        paragraph_math: bool = False,
        color: str | None = None,
    ) -> bool:
        wrapper = latex_to_omml(
            formula,
            color=self._normalized_math_color(color or element.get("color")),
            size_pt=float(element.get("size", "24")),
            paragraph=paragraph_math,
        )
        if wrapper is None:
            return False
        paragraph._p.append(wrapper)
        return True

    def _wrap_native_equation_with_fallback(
        self,
        slide,
        native_element,
        fallback_element,
    ) -> None:
        """Use native math in Office 2010+ and keep a visible old-Office fallback."""
        shape_tree = slide.shapes._spTree
        native_index = shape_tree.index(native_element)
        shape_tree.remove(native_element)
        shape_tree.remove(fallback_element)

        alternate = etree.Element(
            self._xml_tag(MC_NS, "AlternateContent"),
            nsmap={
                "mc": MC_NS,
                "a14": A14_NS,
                "m": M_NS,
            },
        )
        choice = etree.SubElement(
            alternate,
            self._xml_tag(MC_NS, "Choice"),
            Requires="a14",
        )
        choice.append(native_element)
        fallback = etree.SubElement(
            alternate,
            self._xml_tag(MC_NS, "Fallback"),
        )
        fallback.append(fallback_element)
        shape_tree.insert(native_index, alternate)

    def _fallback_math_picture(self, slide, element: ET.Element) -> bool:
        """Add a visible picture only when native OMML cannot be built."""
        png_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        png_file.close()
        png_path = Path(png_file.name)
        try:
            if not self.render_latex_fallback_image(element, png_path):
                return False
            slide.shapes.add_picture(
                str(png_path),
                self.x(element.get("x")),
                self.y(element.get("y")),
                self.x(element.get("width")),
                self.y(element.get("height")),
            )
            return True
        finally:
            png_path.unlink(missing_ok=True)

    def render_native_math_textbox(self, slide, element: ET.Element) -> bool:
        """Render a textbox containing LaTeX as an editable PowerPoint equation."""
        formula_nodes = [
            node for node in element.iter() if node.tag == "math-field"
        ]
        formulas = [
            node.get("value") or node.text or "" for node in formula_nodes
        ]
        if not formulas or any(not formula.strip() for formula in formulas):
            return False

        # Validate every formula before creating a shape. This lets the caller
        # use the raster fallback for an unsupported LaTeX construct without
        # leaving a half-built textbox behind.
        math_wrappers = []
        for formula in formulas:
            wrapper = latex_to_omml(
                formula,
                color=self._normalized_math_color(element.get("color")),
                size_pt=float(element.get("size", "24")),
                # PowerPoint's PresentationML math schema expects every
                # ``a14:m`` content block to contain ``m:oMathPara``.  This
                # remains valid when the equation is mixed with ordinary text
                # and avoids the repair dialog caused by an inline
                # ``m:oMath`` wrapper in some PowerPoint versions.
                paragraph=True,
            )
            if wrapper is None:
                return False
            math_wrappers.append(wrapper)

        x = float(element.get("x", "0"))
        y = float(element.get("y", "0"))
        width = float(element.get("width", "300"))
        height = float(element.get("height", "100"))
        box = slide.shapes.add_textbox(
            self.x(str(x)),
            self.y(str(y)),
            self.x(str(width)),
            self.y(str(height)),
        )
        box.name = "Editable Equation"

        text_frame = box.text_frame
        text_frame.clear()
        text_frame.word_wrap = not self.to_bool(
            element.get("single_line"),
            False,
        )
        text_frame.auto_size = MSO_AUTO_SIZE.NONE
        text_frame.margin_left = Pt(float(element.get("margin_left", "0")))
        text_frame.margin_right = Pt(float(element.get("margin_right", "0")))
        text_frame.margin_top = Pt(float(element.get("margin_top", "0")))
        text_frame.margin_bottom = Pt(float(element.get("margin_bottom", "0")))
        text_frame.vertical_anchor = {
            "top": MSO_ANCHOR.TOP,
            "middle": MSO_ANCHOR.MIDDLE,
            "center": MSO_ANCHOR.MIDDLE,
            "bottom": MSO_ANCHOR.BOTTOM,
        }.get(element.get("vertical_align", "top").lower(), MSO_ANCHOR.TOP)

        paragraph = text_frame.paragraphs[0]
        paragraph.alignment = {
            "left": PP_ALIGN.LEFT,
            "center": PP_ALIGN.CENTER,
            "right": PP_ALIGN.RIGHT,
            "justify": PP_ALIGN.JUSTIFY,
        }.get(element.get("align", "left").lower(), PP_ALIGN.LEFT)
        paragraph.space_before = Pt(0)
        paragraph.space_after = Pt(0)
        paragraph.line_spacing = float(element.get("line_spacing", "1.0"))

        # python-pptx creates an empty a:p. Keep its paragraph properties but
        # replace all ordinary runs with the mixed DrawingML/OMML content.
        paragraph_element = paragraph._p
        for child in list(paragraph_element):
            if child.tag != self._xml_tag(A_NS, "pPr"):
                paragraph_element.remove(child)

        formula_index = 0

        def append_content(text: str, source: ET.Element, color: str | None = None):
            self._append_native_text_run(
                paragraph,
                text,
                source,
                color=color,
            )

        if element.text:
            append_content(element.text, element)

        for child in element:
            if child.tag == "math-field":
                paragraph._p.append(math_wrappers[formula_index])
                formula_index += 1
            elif child.tag == "br":
                paragraph._p.append(etree.Element(self._xml_tag(A_NS, "br")))
            elif child.tag == "run":
                append_content(
                    child.text or "",
                    child,
                    color=child.get("color") or element.get("color"),
                )
            else:
                append_content("".join(child.itertext()), child)
            if child.tail:
                append_content(child.tail, element)

        # ``a:endParaRPr`` is optional in the DrawingML grammar, but it is
        # emitted by PowerPoint for every text paragraph.  Keeping it here
        # makes the generated AlternateContent branch compatible with older
        # PowerPoint validators as well.
        paragraph._p.append(
            etree.Element(
                self._xml_tag(A_NS, "endParaRPr"),
                lang="en-US",
                dirty="0",
            )
        )

        # Add a visible fallback image to the same AlternateContent block.
        # The native shape remains the branch PowerPoint chooses and therefore
        # stays editable through Insert Equation / Equation Tools.
        fallback_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fallback_file.close()
        fallback_path = Path(fallback_file.name)
        try:
            fallback_available = self.render_latex_fallback_image(
                element,
                fallback_path,
            )
            if fallback_available:
                fallback_picture = slide.shapes.add_picture(
                    str(fallback_path),
                    self.x(str(x)),
                    self.y(str(y)),
                    self.x(str(width)),
                    self.y(str(height)),
                )
                self._wrap_native_equation_with_fallback(
                    slide,
                    box._element,
                    fallback_picture._element,
                )
        finally:
            fallback_path.unlink(missing_ok=True)

        print(
            f"  Native equation: {formulas[0][:45]}"
            f"{'...' if len(formulas[0]) > 45 else ''}"
        )
        return True

    def render_math_textbox(self, slide, element: ET.Element) -> None:
        """Prefer a native editable equation, then use a visible picture fallback."""
        if self.render_native_math_textbox(slide, element):
            return
        if not self._fallback_math_picture(slide, element):
            self.render_textbox(slide, element)

    def render_math_picture(self, slide, element: ET.Element) -> None:
        """Legacy browser rasterizer retained for unsupported expressions."""
        formula_nodes = [
            node
            for node in element.iter()
            if node.tag == "math-field"
        ]
        formulas = [
            node.get("value") or node.text or ""
            for node in formula_nodes
        ]
        markup = self.latex_to_mathlive_markup(formulas)
        if len(markup) != len(formulas) or not all(markup):
            # Keep conversion recoverable if Node/MathLive is unavailable.
            self.render_textbox(slide, element)
            return

        browser_candidates = self.svg_renderer_candidates()
        if not browser_candidates:
            print("Khong tim thay trinh duyet de render cong thuc LaTeX.")
            self.render_textbox(slide, element)
            return

        pixel_width = max(1, round(float(element.get("width", "300"))))
        pixel_height = max(1, round(float(element.get("height", "100"))))
        html_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".html",
        )
        html_file.close()
        html_path = Path(html_file.name)
        png_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".png",
        )
        png_file.close()
        png_path = Path(png_file.name)

        try:
            html_path.write_text(
                self.math_textbox_html(element, markup),
                encoding="utf-8",
            )
            rendered = False
            # MathLive uses local KaTeX fonts.  A headless Chromium screenshot
            # can otherwise be taken during the font-swap window, producing a
            # valid but completely transparent PNG.  Retry with increasing
            # virtual time and verify the alpha channel before embedding it.
            for virtual_time_ms in (500, 1500, 3000):
                subprocess.run(
                    [
                        str(browser_candidates[0]),
                        "--headless",
                        "--disable-gpu",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--default-background-color=00000000",
                        "--hide-scrollbars",
                        "--run-all-compositor-stages-before-draw",
                        f"--virtual-time-budget={virtual_time_ms}",
                        f"--window-size={pixel_width},{pixel_height}",
                        f"--screenshot={png_path}",
                        html_path.resolve().as_uri(),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                try:
                    with Image.open(png_path) as rendered_image:
                        alpha = rendered_image.convert("RGBA").getchannel("A")
                        rendered = alpha.getbbox() is not None
                except (OSError, ValueError):
                    rendered = False
                if rendered:
                    break

            if not rendered:
                raise RuntimeError(
                    "MathLive screenshot is transparent after waiting for fonts"
                )

            slide.shapes.add_picture(
                str(png_path),
                self.x(element.get("x")),
                self.y(element.get("y")),
                self.x(element.get("width")),
                self.y(element.get("height")),
            )
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            print(f"Khong the render cong thuc LaTeX: {exc}")
            self.render_textbox(slide, element)
        finally:
            html_path.unlink(missing_ok=True)
            png_path.unlink(missing_ok=True)

    def close_open_output_presentation(self) -> None:
        if os.name != "nt":
            return

        script = r"""
$target = [System.IO.Path]::GetFullPath($env:PPTX_TO_CLOSE)

try {
    $app = [Runtime.InteropServices.Marshal]::GetActiveObject("PowerPoint.Application")
} catch {
    exit 0
}

$closed = $false

foreach ($presentation in @($app.Presentations)) {
    try {
        $current = [System.IO.Path]::GetFullPath($presentation.FullName)
    } catch {
        continue
    }

    if ([string]::Equals($current, $target, [System.StringComparison]::OrdinalIgnoreCase)) {
        $presentation.Saved = $true
        $presentation.Close()
        $closed = $true
    }
}

if ($closed) {
    Write-Output "Da dong file PPTX dang mo: $target"
}
"""

        env = os.environ.copy()
        env["PPTX_TO_CLOSE"] = str(self.output_path)

        try:
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    script,
                ],
                capture_output=True,
                env=env,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"Khong the kiem tra file PPTX dang mo: {exc}")
            return

        if completed.stdout.strip():
            print(completed.stdout.strip())

        if completed.returncode != 0 and completed.stderr.strip():
            print(
                "Khong the dong file PPTX dang mo: "
                f"{completed.stderr.strip()}"
            )

    @staticmethod
    def _transition_speed(duration_ms: int) -> str:
        """Map the editor's millisecond duration to PresentationML speed."""
        if duration_ms <= 450:
            return "fast"
        if duration_ms <= 1100:
            return "med"
        return "slow"

    def apply_slide_transition(self, slide, slide_node: ET.Element) -> None:
        """Write a slide transition into the PresentationML slide part.

        python-pptx does not expose transitions as a public API, so this uses
        the same small OOXML extension point that PowerPoint writes itself:
        ``p:clrMapOvr`` followed by ``p:transition``.  The transition belongs
        to the destination slide, matching PowerPoint's semantics.
        """
        attrs = slide_node.attrib
        transition_type = (attrs.get("transition") or "none").strip().lower()
        slide_element = slide._element
        transition_tag = self._xml_tag(P_NS, "transition")
        for existing in list(slide_element):
            if existing.tag == transition_tag:
                slide_element.remove(existing)

        if transition_type in {"", "none"}:
            return

        tag_map = {
            "fade": "fade",
            "push": "push",
            "wipe": "wipe",
            "split": "split",
            "cover": "cover",
            "uncover": "pull",
            "zoom": "zoom",
            "cut": "cut",
            "random": "random",
            "wheel": "wheel",
            "strips": "strips",
            "circle": "circle",
            "diamond": "diamond",
            "plus": "plus",
        }
        child_name = tag_map.get(transition_type)
        if child_name is None:
            print(f"  Bỏ qua transition không hỗ trợ: {transition_type}")
            return

        transition = OxmlElement("p:transition")
        try:
            duration_ms = int(float(attrs.get("transition_duration", "700")))
        except (TypeError, ValueError):
            duration_ms = 700
        duration_ms = max(120, min(3000, duration_ms))
        transition.set("spd", self._transition_speed(duration_ms))

        advance = (attrs.get("transition_advance") or "click").strip().lower()
        if advance in {"after", "both"}:
            try:
                delay_ms = int(float(attrs.get("transition_delay", "3000")))
            except (TypeError, ValueError):
                delay_ms = 3000
            delay_ms = max(500, min(60000, delay_ms))
            transition.set("advTm", str(delay_ms))
        transition.set("advClick", "0" if advance == "after" else "1")

        child = OxmlElement(f"p:{child_name}")
        direction = (attrs.get("transition_direction") or "l").strip().lower()
        side_direction = direction if direction in {"l", "r", "u", "d"} else "l"
        if child_name in {"push", "wipe", "cover", "pull", "strips"}:
            child.set("dir", side_direction)
        elif child_name == "split":
            child.set("orient", "vert" if side_direction in {"u", "d"} else "horz")
            child.set("dir", "in" if direction in {"in", "l", "u"} else "out")
        elif child_name == "zoom":
            child.set("dir", "out" if direction in {"out", "r", "d"} else "in")
        elif child_name == "wheel":
            child.set("spokes", "4")

        transition.append(child)
        color_map = slide_element.find(self._xml_tag(P_NS, "clrMapOvr"))
        insert_at = list(slide_element).index(color_map) + 1 if color_map is not None else 1
        slide_element.insert(insert_at, transition)

    # =========================================================
    # Helpers
    # =========================================================

    @staticmethod
    def to_bool(value: str | None, default: bool = False) -> bool:
        if value is None:
            return default
        return value.strip().lower() in {"true", "1", "yes", "on"}

    @staticmethod
    def rgb(value: str | None, default: str = "#000000") -> RGBColor:
        raw = (value or default).strip().lstrip("#")

        if len(raw) == 3:
            raw = "".join(char * 2 for char in raw)

        if len(raw) != 6:
            raise ValueError(f"Màu không hợp lệ: {value}")

        return RGBColor(
            int(raw[0:2], 16),
            int(raw[2:4], 16),
            int(raw[4:6], 16),
        )

    def x(self, value: str | None) -> int:
        return round(
            float(value or 0)
            / self.canvas_width
            * self.prs.slide_width
        )

    def y(self, value: str | None) -> int:
        return round(
            float(value or 0)
            / self.canvas_height
            * self.prs.slide_height
        )

    @property
    def canvas_dpi_x(self) -> float:
        return self.canvas_width / self.slide_width_inches

    @property
    def canvas_dpi_y(self) -> float:
        return self.canvas_height / self.slide_height_inches

    def pt_to_canvas_x(self, point_size: float) -> float:
        return point_size * self.canvas_dpi_x / 72.0

    def pt_to_canvas_y(self, point_size: float) -> float:
        return point_size * self.canvas_dpi_y / 72.0

    # =========================================================
    # Font resolution and text measurement
    # =========================================================

    @staticmethod
    def normalize_font_name(name: str) -> str:
        return "".join(char.lower() for char in name if char.isalnum())

    def font_directories(self) -> list[Path]:
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

        return [path for path in directories if path.exists()]

    def resolve_font_path(
        self,
        font_name: str,
        bold: bool = False,
        italic: bool = False,
        explicit_path: str | None = None,
    ) -> Path:
        if explicit_path:
            path = Path(explicit_path)
            if not path.is_absolute():
                path = self.base_dir / path
            if path.exists():
                try:
                    ImageFont.truetype(str(path), 12)
                    return path
                except OSError:
                    # The XML can point at an existing file that is not a
                    # readable font. Continue with the installed-font fallback.
                    pass

        # Một số tên hiển thị trong PowerPoint không giống tên file font Windows.
        font_aliases = {
            "Segoe UI Symbol": "seguisym",
            "Segoe UI": "segoeui",
            "Arial": "arial",
            "Times New Roman": "times",
            "Calibri": "calibri",
            "Aptos": "aptos",
        }

        alias = font_aliases.get(font_name)
        normalized_name = (
            self.normalize_font_name(alias)
            if alias
            else self.normalize_font_name(font_name)
        )

        style_tokens: list[str] = []
        if bold:
            style_tokens.extend(["bold", "bd", "semibold"])
        if italic:
            style_tokens.extend(["italic", "it", "oblique"])

        extensions = {".ttf", ".otf", ".ttc"}

        candidates: list[tuple[int, Path]] = []

        for directory in self.font_directories():
            try:
                font_files = directory.rglob("*")
            except OSError:
                continue

            for path in font_files:
                if path.suffix.lower() not in extensions:
                    continue

                stem = self.normalize_font_name(path.stem)
                score = 0

                if normalized_name == stem:
                    score += 100
                elif normalized_name in stem:
                    score += 70
                else:
                    continue

                if bold:
                    if any(token in stem for token in ("bold", "bd", "semibold")):
                        score += 20
                    else:
                        score -= 10

                if italic:
                    if any(token in stem for token in ("italic", "it", "oblique")):
                        score += 20
                    else:
                        score -= 10

                if not bold and any(token in stem for token in ("bold", "semibold")):
                    score -= 10

                if not italic and any(token in stem for token in ("italic", "oblique")):
                    score -= 10

                candidates.append((score, path))

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            for _, candidate in candidates:
                try:
                    ImageFont.truetype(str(candidate), 12)
                    return candidate
                except OSError:
                    continue

        # Pillow thường đi kèm DejaVuSans; dùng làm fallback để converter không crash.
        fallback_names = [
            "DejaVuSans-BoldOblique.ttf" if bold and italic else "",
            "DejaVuSans-Bold.ttf" if bold else "",
            "DejaVuSans-Oblique.ttf" if italic else "",
            "DejaVuSans.ttf",
            "FreeSansBoldOblique.ttf" if bold and italic else "",
            "FreeSansBold.ttf" if bold else "",
            "FreeSansOblique.ttf" if italic else "",
            "FreeSans.ttf",
            "LiberationSans-BoldItalic.ttf" if bold and italic else "",
            "LiberationSans-Bold.ttf" if bold else "",
            "LiberationSans-Italic.ttf" if italic else "",
            "LiberationSans-Regular.ttf",
        ]

        fallback_paths: list[Path] = []
        for directory in self.font_directories():
            for fallback in fallback_names:
                if not fallback:
                    continue
                direct_path = directory / fallback
                if direct_path.exists():
                    fallback_paths.append(direct_path)
                try:
                    fallback_paths.extend(
                        path
                        for path in directory.rglob(fallback)
                        if path not in fallback_paths
                    )
                except OSError:
                    continue

        for fallback_path in fallback_paths:
            try:
                ImageFont.truetype(str(fallback_path), 12)
                return fallback_path
            except OSError:
                continue

        # An arbitrary PowerPoint family such as Arial should not stop an
        # export. Use any readable installed font for measurement as the final
        # fallback; the requested family name remains on the PowerPoint run.
        for directory in self.font_directories():
            try:
                font_files = directory.rglob("*")
            except OSError:
                continue
            for font_path in font_files:
                if font_path.suffix.lower() not in extensions:
                    continue
                try:
                    ImageFont.truetype(str(font_path), 12)
                    return font_path
                except OSError:
                    continue

        raise ValueError(
            f"Không tìm thấy font '{font_name}'. "
            "Hãy cài font hoặc truyền font_path trong XML."
        )

    @staticmethod
    def load_font(font_path: Path, pixel_size: float) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(
            str(font_path),
            size=max(1, round(pixel_size)),
        )

    def measure_text_width_canvas(
        self,
        text: str,
        font_path: Path,
        font_size_pt: float,
    ) -> float:
        font = self.load_font(
            font_path,
            self.pt_to_canvas_y(font_size_pt),
        )

        if hasattr(font, "getlength"):
            return float(font.getlength(text))

        left, _, right, _ = font.getbbox(text)
        return float(right - left)

    def line_height_canvas(
        self,
        font_path: Path,
        font_size_pt: float,
        line_spacing: float,
    ) -> float:
        font = self.load_font(
            font_path,
            self.pt_to_canvas_y(font_size_pt),
        )
        ascent, descent = font.getmetrics()
        return float(ascent + descent) * line_spacing

    def break_long_word(
        self,
        word: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        pieces: list[str] = []
        current = ""

        for char in word:
            candidate = current + char
            if (
                current
                and self.measure_text_width_canvas(
                    candidate,
                    font_path,
                    font_size_pt,
                )
                > max_width
            ):
                pieces.append(current)
                current = char
            else:
                current = candidate

        if current:
            pieces.append(current)

        return pieces or [""]

    def wrap_paragraph(
        self,
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
            if (
                self.measure_text_width_canvas(
                    word,
                    font_path,
                    font_size_pt,
                )
                > max_width
            ):
                word_pieces = self.break_long_word(
                    word,
                    font_path,
                    font_size_pt,
                    max_width,
                )
            else:
                word_pieces = [word]

            for piece in word_pieces:
                candidate = piece if not current else f"{current} {piece}"

                if (
                    not current
                    or self.measure_text_width_canvas(
                        candidate,
                        font_path,
                        font_size_pt,
                    )
                    <= max_width
                ):
                    current = candidate
                else:
                    lines.append(current)
                    current = piece

        if current:
            lines.append(current)

        return lines

    def wrap_text(
        self,
        text: str,
        font_path: Path,
        font_size_pt: float,
        max_width: float,
    ) -> list[str]:
        # Giữ các xuống dòng mà XML đã chủ động đặt.
        source_paragraphs = text.splitlines() or [""]

        result: list[str] = []
        for paragraph in source_paragraphs:
            result.extend(
                self.wrap_paragraph(
                    paragraph.strip(),
                    font_path,
                    font_size_pt,
                    max_width,
                )
            )

        return result or [""]

    def calculate_text_layout(
        self,
        *,
        text: str,
        font_path: Path,
        initial_font_size: float,
        min_font_size: float,
        available_width: float,
        available_height: float,
        line_spacing: float,
        single_line: bool,
        max_lines: int | None,
        overflow: str,
        safety_ratio: float,
    ) -> tuple[list[str], float, float]:
        current_size = initial_font_size
        target_width = max(1.0, available_width * safety_ratio)
        target_height = max(1.0, available_height * safety_ratio)

        while current_size >= min_font_size:
            if single_line:
                normalized = " ".join(text.split())
                lines = [normalized]
            else:
                lines = self.wrap_text(
                    text,
                    font_path,
                    current_size,
                    target_width,
                )

            required_height = (
                len(lines)
                * self.line_height_canvas(
                    font_path,
                    current_size,
                    line_spacing,
                )
            )

            width_ok = all(
                self.measure_text_width_canvas(
                    line,
                    font_path,
                    current_size,
                )
                <= target_width
                for line in lines
            )
            height_ok = required_height <= target_height
            lines_ok = max_lines is None or len(lines) <= max_lines

            if width_ok and height_ok and lines_ok:
                return lines, current_size, required_height

            if overflow != "shrink":
                return lines, current_size, required_height

            current_size = round(current_size - 0.5, 2)

        final_size = min_font_size

        if single_line:
            lines = [" ".join(text.split())]
        else:
            lines = self.wrap_text(
                text,
                font_path,
                final_size,
                target_width,
            )

        required_height = (
            len(lines)
            * self.line_height_canvas(
                font_path,
                final_size,
                line_spacing,
            )
        )

        return lines, final_size, required_height

    # =========================================================
    # Textbox
    # =========================================================

    def apply_text_gradient(
        self,
        paragraph,
        start_color: str,
        end_color: str,
    ) -> None:
        def normalize_color(value: str) -> str:
            return value.strip().lstrip("#").upper()

        paragraph_properties = paragraph._p.get_or_add_pPr()
        character_properties = paragraph_properties.get_or_add_defRPr()

        for child in list(character_properties):
            if child.tag.rsplit("}", maxsplit=1)[-1] in {
                "solidFill",
                "gradFill",
            }:
                character_properties.remove(child)

        gradient_fill = OxmlElement("a:gradFill")
        gradient_stops = OxmlElement("a:gsLst")

        for position, color in (("0", start_color), ("100000", end_color)):
            gradient_stop = OxmlElement("a:gs")
            gradient_stop.set("pos", position)
            rgb_color = OxmlElement("a:srgbClr")
            rgb_color.set("val", normalize_color(color))
            gradient_stop.append(rgb_color)
            gradient_stops.append(gradient_stop)

        linear_gradient = OxmlElement("a:lin")
        linear_gradient.set("ang", "0")
        linear_gradient.set("scaled", "1")

        gradient_fill.append(gradient_stops)
        gradient_fill.append(linear_gradient)
        character_properties.append(gradient_fill)

    @staticmethod
    def read_rich_text_runs(e: ET.Element) -> list[dict[str, str]]:
        """Return flat XML ``<run>`` content, preserving per-run attributes."""
        run_nodes = e.findall("./run")
        if not run_nodes:
            return []

        runs = [
            {"text": run_node.text or "", **run_node.attrib}
            for run_node in run_nodes
        ]
        # Plain text rendering historically strips the textbox as a whole.
        # Apply the same behavior without removing meaningful spaces between runs.
        while runs and not runs[0]["text"]:
            runs.pop(0)
        while runs and not runs[-1]["text"]:
            runs.pop()
        if runs:
            runs[0]["text"] = runs[0]["text"].lstrip()
            runs[-1]["text"] = runs[-1]["text"].rstrip()
        return [run for run in runs if run["text"]]

    @staticmethod
    def rich_segments_for_lines(
        rich_runs: list[dict[str, str]],
        rendered_lines: list[str],
    ) -> list[list[tuple[str, dict[str, str]]]]:
        """Map wrapped lines back to their rich-run styles by character offset."""
        normalized_characters: list[str] = []
        normalized_styles: list[dict[str, str]] = []
        pending_space_style: dict[str, str] | None = None

        for rich_run in rich_runs:
            style = {
                key: value
                for key, value in rich_run.items()
                if key != "text"
            }
            for character in rich_run.get("text", ""):
                if character.isspace():
                    if pending_space_style is None:
                        pending_space_style = style
                    continue
                if pending_space_style is not None and normalized_characters:
                    normalized_characters.append(" ")
                    normalized_styles.append(pending_space_style)
                pending_space_style = None
                normalized_characters.append(character)
                normalized_styles.append(style)

        normalized_text = "".join(normalized_characters)
        cursor = 0
        result: list[list[tuple[str, dict[str, str]]]] = []

        for rendered_line in rendered_lines:
            line = " ".join(rendered_line.split())
            if not line:
                result.append([])
                continue

            start = normalized_text.find(line, cursor)
            if start < 0:
                # Keep the text visible if a future wrapping implementation
                # transforms characters in a way that cannot be mapped exactly.
                result.append([(rendered_line, {})])
                continue

            line_styles = normalized_styles[start : start + len(line)]
            segments: list[tuple[str, dict[str, str]]] = []
            segment_start = 0
            for index in range(1, len(line) + 1):
                if index < len(line) and line_styles[index] == line_styles[segment_start]:
                    continue
                segments.append(
                    (
                        line[segment_start:index],
                        line_styles[segment_start],
                    )
                )
                segment_start = index
            result.append(segments)
            cursor = start + len(line)

        return result

    def render_textbox(self, slide, e: ET.Element) -> None:
        rich_runs = self.read_rich_text_runs(e)
        text = (
            "".join(run["text"] for run in rich_runs)
            if rich_runs
            else "".join(e.itertext()).strip()
        )

        x = float(e.get("x", "0"))
        y = float(e.get("y", "0"))
        width = float(e.get("width", "300"))
        height = float(e.get("height", "100"))

        # Give textboxes a small amount of breathing room.  The XML layout
        # is measured in canvas pixels while PowerPoint uses its own font
        # metrics, so a slight expansion prevents premature wrapping.
        width_growth = width * 0.04
        height_growth = height * 0.08
        x = max(0.0, x - width_growth / 2.0)
        y = max(0.0, y - height_growth / 2.0)
        width = min(self.canvas_width - x, width + width_growth)
        height = min(self.canvas_height - y, height + height_growth)

        font_name = e.get("font", "Arial")
        font_size = float(e.get("size", "24"))
        min_font_size = float(e.get("min_font_size", "10"))

        bold = self.to_bool(e.get("bold"))
        italic = self.to_bool(e.get("italic"))
        single_line = self.to_bool(e.get("single_line"), False)
        reflow_on_resize = self.to_bool(
            e.get("reflow_on_resize"),
            False,
        )

        overflow = e.get("overflow", "shrink").lower()
        if overflow not in {"shrink", "resize", "clip"}:
            raise ValueError(
                "overflow phải là shrink, resize hoặc clip"
            )

        line_spacing = float(e.get("line_spacing", "1.0"))
        safety_ratio = float(e.get("safety_ratio", "0.97"))

        max_lines_value = e.get("max_lines")
        max_lines = (
            int(max_lines_value)
            if max_lines_value is not None
            else (1 if single_line else None)
        )

        margin_left_pt = float(e.get("margin_left", "0"))
        margin_right_pt = float(e.get("margin_right", "0"))
        margin_top_pt = float(e.get("margin_top", "0"))
        margin_bottom_pt = float(e.get("margin_bottom", "0"))

        available_width = (
            width
            - self.pt_to_canvas_x(margin_left_pt)
            - self.pt_to_canvas_x(margin_right_pt)
        )
        available_height = (
            height
            - self.pt_to_canvas_y(margin_top_pt)
            - self.pt_to_canvas_y(margin_bottom_pt)
        )

        font_path = self.resolve_font_path(
            font_name=font_name,
            bold=bold,
            italic=italic,
            explicit_path=e.get("font_path"),
        )

        lines, final_font_size, required_height = (
            self.calculate_text_layout(
                text=text,
                font_path=font_path,
                initial_font_size=font_size,
                min_font_size=min_font_size,
                available_width=available_width,
                available_height=available_height,
                line_spacing=line_spacing,
                single_line=single_line,
                max_lines=max_lines,
                overflow=overflow,
                safety_ratio=safety_ratio,
            )
        )

        final_height = height
        if overflow == "resize":
            final_height = max(
                height,
                required_height
                + self.pt_to_canvas_y(margin_top_pt)
                + self.pt_to_canvas_y(margin_bottom_pt),
            )

        box = slide.shapes.add_textbox(
            self.x(str(x)),
            self.y(str(y)),
            self.x(str(width)),
            self.y(str(final_height)),
        )

        # The final XML contrast guard may add an opaque textbox backplate
        # when text sits directly on an image or another unverifiable surface.
        # Preserve that safety layer in exported PowerPoint files as well as
        # in the web preview.
        textbox_fill = e.get("fill") or e.get("background")
        if textbox_fill and textbox_fill.lower() != "none":
            box.fill.solid()
            box.fill.fore_color.rgb = self.rgb(textbox_fill)
        else:
            box.fill.background()

        line_color = e.get("line_color")
        if line_color and line_color.lower() != "none":
            box.line.color.rgb = self.rgb(line_color)
        else:
            box.line.fill.background()

        tf = box.text_frame
        tf.clear()

        # single_line=true  -> tuyệt đối không xuống dòng.
        # single_line=false -> cho phép xuống dòng trong bounding box.
        # Converter vẫn tính trước các dòng; PowerPoint wrap là lớp dự phòng.
        tf.word_wrap = not single_line
        tf.auto_size = MSO_AUTO_SIZE.NONE

        tf.margin_left = Pt(margin_left_pt)
        tf.margin_right = Pt(margin_right_pt)
        tf.margin_top = Pt(margin_top_pt)
        tf.margin_bottom = Pt(margin_bottom_pt)

        vertical_map = {
            "top": MSO_ANCHOR.TOP,
            "middle": MSO_ANCHOR.MIDDLE,
            "center": MSO_ANCHOR.MIDDLE,
            "bottom": MSO_ANCHOR.BOTTOM,
        }
        tf.vertical_anchor = vertical_map.get(
            e.get("vertical_align", "top").lower(),
            MSO_ANCHOR.TOP,
        )

        align_map = {
            "left": PP_ALIGN.LEFT,
            "center": PP_ALIGN.CENTER,
            "right": PP_ALIGN.RIGHT,
            "justify": PP_ALIGN.JUSTIFY,
        }
        alignment = align_map.get(
            e.get("align", "left").lower(),
            PP_ALIGN.LEFT,
        )

        rendered_lines = lines
        if reflow_on_resize and not single_line:
            rendered_lines = [
                " ".join(paragraph.split())
                for paragraph in text.splitlines()
            ] or [""]

        rich_lines = (
            self.rich_segments_for_lines(rich_runs, rendered_lines)
            if rich_runs
            else []
        )

        for index, line in enumerate(rendered_lines):
            paragraph = (
                tf.paragraphs[0]
                if index == 0
                else tf.add_paragraph()
            )

            paragraph.alignment = alignment
            paragraph.space_before = Pt(0)
            paragraph.space_after = Pt(0)
            paragraph.line_spacing = line_spacing

            paragraph.font.name = font_name
            paragraph.font.size = Pt(final_font_size)
            paragraph.font.bold = bold
            paragraph.font.italic = italic
            paragraph.font.color.rgb = self.rgb(
                e.get("color"),
                "#000000",
            )

            if rich_runs:
                segments = rich_lines[index]
                if not segments:
                    paragraph.text = ""
                for segment_text, segment_style in segments:
                    run = paragraph.add_run()
                    run.text = segment_text
                    run.font.name = segment_style.get("font", font_name)
                    run.font.size = Pt(
                        float(segment_style.get("size", final_font_size))
                    )
                    run.font.bold = self.to_bool(
                        segment_style.get("bold"),
                        bold,
                    )
                    run.font.italic = self.to_bool(
                        segment_style.get("italic"),
                        italic,
                    )
                    run.font.color.rgb = self.rgb(
                        segment_style.get("color"),
                        e.get("color", "#000000"),
                    )
            else:
                paragraph.text = line

            gradient_start = e.get("gradient_start")
            gradient_end = e.get("gradient_end")
            if gradient_start and gradient_end and not rich_runs:
                self.apply_text_gradient(
                    paragraph,
                    gradient_start,
                    gradient_end,
                )

        print(
            f"  Textbox '{text[:35]}': "
            f"{font_size:g}pt -> {final_font_size:g}pt, "
            f"{len(lines)} dòng, "
            f"wrap={'off' if single_line else 'on'}, "
            f"reflow={'on' if reflow_on_resize else 'off'}"
        )

    # =========================================================
    # Shapes
    # =========================================================

    def apply_fill_opacity(self, shape, opacity_value: str | None) -> None:
        """Apply XML opacity to a PowerPoint solid fill."""
        if opacity_value is None:
            return

        try:
            opacity = max(0.0, min(1.0, float(opacity_value)))
        except (TypeError, ValueError):
            return

        if opacity >= 0.999:
            return

        drawingml_ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
        solid_fill = shape.fill._xPr.find(
            f"{{{drawingml_ns}}}solidFill"
        )
        if solid_fill is None:
            return

        color_node = None
        for tag_name in ("srgbClr", "schemeClr", "sysClr", "prstClr"):
            color_node = solid_fill.find(
                f"{{{drawingml_ns}}}{tag_name}"
            )
            if color_node is not None:
                break

        if color_node is None:
            return

        alpha_node = color_node.find(
            f"{{{drawingml_ns}}}alpha"
        )
        if alpha_node is None:
            alpha_node = OxmlElement("a:alpha")
            color_node.append(alpha_node)

        alpha_node.set("val", str(round(opacity * 100000)))

    def render_shape(self, slide, e: ET.Element) -> None:
        mapping = {
            "rectangle": MSO_SHAPE.RECTANGLE,
            "rounded_rectangle": MSO_SHAPE.ROUNDED_RECTANGLE,
            "circle": MSO_SHAPE.OVAL,
            "ellipse": MSO_SHAPE.OVAL,
            "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
            "diamond": MSO_SHAPE.DIAMOND,
            "hexagon": MSO_SHAPE.HEXAGON,
            "chevron": MSO_SHAPE.CHEVRON,
            "right_arrow": MSO_SHAPE.RIGHT_ARROW,
        }

        shape = slide.shapes.add_shape(
            mapping.get(
                e.get("type", "rectangle"),
                MSO_SHAPE.RECTANGLE,
            ),
            self.x(e.get("x")),
            self.y(e.get("y")),
            self.x(e.get("width")),
            self.y(e.get("height")),
        )

        fill = e.get("fill", "none")
        if fill == "none":
            shape.fill.background()
        else:
            shape.fill.solid()
            shape.fill.fore_color.rgb = self.rgb(fill)
            self.apply_fill_opacity(shape, e.get("opacity"))

        line_color = e.get("line_color", "none")
        if line_color == "none":
            shape.line.fill.background()
        else:
            shape.line.color.rgb = self.rgb(line_color)
            shape.line.width = Pt(
                float(e.get("line_width", "1"))
            )

        shape.rotation = float(e.get("rotation", "0"))

    def render_line(self, slide, e: ET.Element) -> None:
        line = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            self.x(e.get("x1")),
            self.y(e.get("y1")),
            self.x(e.get("x2")),
            self.y(e.get("y2")),
        )

        line.line.color.rgb = self.rgb(
            e.get("color"),
            "#000000",
        )
        line.line.width = Pt(float(e.get("width", "1")))

        # python-pptx versions differ in arrowhead support. Keep connector
        # export compatible by only applying arrowheads when the installed
        # line object exposes the native properties.
        arrowhead = getattr(line.line, "end_arrowhead", None)
        if self.to_bool(e.get("arrow_end")) and arrowhead is not None:
            try:
                from pptx.enum.dml import MSO_ARROWHEAD
                line.line.end_arrowhead = MSO_ARROWHEAD.TRIANGLE
            except (ImportError, AttributeError, ValueError):
                pass
        arrowhead = getattr(line.line, "begin_arrowhead", None)
        if self.to_bool(e.get("arrow_start")) and arrowhead is not None:
            try:
                from pptx.enum.dml import MSO_ARROWHEAD
                line.line.begin_arrowhead = MSO_ARROWHEAD.TRIANGLE
            except (ImportError, AttributeError, ValueError):
                pass

    @staticmethod
    def _is_number(value: str) -> bool:
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False

    @staticmethod
    def _table_rows(value: str | None) -> list[list[str]]:
        rows = [
            [cell.strip() for cell in row.split("|")]
            for row in (value or "Metric|Value;Revenue|120;Users|2400").split(";")
            if row.strip()
        ]
        column_count = max((len(row) for row in rows), default=1)
        return [row + [""] * (column_count - len(row)) for row in rows]

    def render_table(self, slide, e: ET.Element) -> None:
        rows = self._table_rows(e.get("data"))
        if not rows:
            return

        table_shape = slide.shapes.add_table(
            len(rows),
            len(rows[0]),
            self.x(e.get("x")),
            self.y(e.get("y")),
            self.x(e.get("width")),
            self.y(e.get("height")),
        )
        table = table_shape.table
        header_fill = e.get("header_fill", "#1E3A8A")
        header_color = e.get("header_color", "#FFFFFF")
        row_fill = e.get("row_fill", "#FFFFFF")
        stripe_fill = e.get("stripe_fill", "#EFF6FF")
        text_color = e.get("text_color", "#0F172A")
        font_size = max(8, float(e.get("font_size", "18")))

        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                cell = table.cell(row_index, column_index)
                cell.text = value
                cell.fill.solid()
                cell.fill.fore_color.rgb = self.rgb(
                    header_fill if row_index == 0 else stripe_fill if row_index % 2 == 0 else row_fill,
                )
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                for paragraph in cell.text_frame.paragraphs:
                    paragraph.alignment = PP_ALIGN.LEFT
                    for run in paragraph.runs:
                        run.font.name = e.get("font", "Arial")
                        run.font.size = Pt(font_size)
                        run.font.bold = row_index == 0 or column_index == 0
                        run.font.color.rgb = self.rgb(
                            header_color if row_index == 0 else text_color,
                        )

    def render_polygon(self, slide, e: ET.Element) -> None:
        points: list[tuple[int, int]] = []

        for item in e.get("points", "").split():
            px, py = item.split(",", maxsplit=1)
            points.append((self.x(px), self.y(py)))

        if len(points) < 3:
            raise ValueError("Polygon cần ít nhất 3 điểm")

        builder = slide.shapes.build_freeform(
            points[0][0],
            points[0][1],
        )
        builder.add_line_segments(points[1:], close=True)
        shape = builder.convert_to_shape()

        fill = e.get("fill", "none")
        if fill == "none":
            shape.fill.background()
        else:
            shape.fill.solid()
            shape.fill.fore_color.rgb = self.rgb(fill)
            self.apply_fill_opacity(shape, e.get("opacity"))

        line_color = e.get("line_color", "none")
        if line_color == "none":
            shape.line.fill.background()
        else:
            shape.line.color.rgb = self.rgb(line_color)
            shape.line.width = Pt(
                float(e.get("line_width", "1"))
            )

    # =========================================================
    # Images
    # =========================================================

    @staticmethod
    def _prepare_pptx_image(image_path: Path) -> tuple[Path, Path | None]:
        """Return an image path that python-pptx can embed.

        Pillow can decode formats such as WEBP, but ``python-pptx`` only
        accepts a smaller set of image formats.  Convert unsupported images
        to a temporary PNG while leaving already-supported images untouched.
        The second return value is the temporary path so callers can remove
        it after the shape has been created.
        """
        supported_formats = {"BMP", "GIF", "JPEG", "PNG", "TIFF", "WMF"}

        with Image.open(image_path) as source_image:
            image_format = (source_image.format or "").upper()
            if image_format in supported_formats:
                return image_path, None

            temporary = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".png",
            )
            temporary.close()
            converted_path = Path(temporary.name)

            # Preserve alpha when the source has it; RGB keeps the output
            # compact for ordinary images and avoids unsupported palette or
            # grayscale modes in downstream encoders.
            has_alpha = (
                "A" in source_image.getbands()
                or "transparency" in source_image.info
            )
            converted_image = source_image.convert(
                "RGBA" if has_alpha else "RGB"
            )
            try:
                converted_image.save(converted_path, format="PNG")
            except Exception:
                converted_path.unlink(missing_ok=True)
                raise
            finally:
                converted_image.close()

        return converted_path, converted_path

    @staticmethod
    def _decode_data_image(source: str) -> Path:
        """Materialize a browser data URL so python-pptx can embed it.

        The XML editor stores files selected from a device as data URLs.  A
        data URL is valid in the browser but is not a filesystem path, so it
        must be decoded before Pillow/python-pptx can read it.
        """
        header, payload = source.split(",", 1)
        metadata = header[5:].split(";")
        mime_type = (metadata[0] or "application/octet-stream").lower()
        if not mime_type.startswith("image/"):
            raise ValueError(f"Data URL khong phai la anh: {mime_type}")

        try:
            if "base64" in metadata[1:]:
                raw = base64.b64decode(payload, validate=True)
            else:
                raw = unquote_to_bytes(payload)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("Data URL anh khong hop le") from exc

        suffix = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/bmp": ".bmp",
            "image/tiff": ".tif",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
        }.get(mime_type) or mimetypes.guess_extension(mime_type) or ".img"
        temporary = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temporary.close()
        target = Path(temporary.name)
        try:
            target.write_bytes(raw)
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return target

    def resolve_image_source(self, source: str) -> tuple[Path, Path | None]:
        """Resolve remote, local, file://, and data URL image sources."""
        value = source.strip()
        if value.lower().startswith("data:image/"):
            temporary = self._decode_data_image(value)
            return temporary, temporary

        if value.lower().startswith(("http://", "https://")):
            temporary = self.download_image(value)
            return temporary, temporary

        if value.lower().startswith("file://"):
            parsed = urlparse(value)
            path_text = unquote(parsed.path)
            # file:///C:/... is parsed with an empty hostname on Windows;
            # UNC paths retain their hostname and are reconstructed here.
            if parsed.netloc and parsed.netloc.lower() != "localhost":
                path_text = f"//{parsed.netloc}{path_text}"
            elif os.name == "nt" and path_text.startswith("/") and len(path_text) > 2 and path_text[2] == ":":
                path_text = path_text[1:]
            image_path = Path(path_text)
        elif value.lower().startswith("/static/output/"):
            # Generated DOCX assets are stored under the persistent static
            # volume.  The XML keeps this browser-readable URL so the editor
            # can display it; export must resolve it back to the local file.
            relative_path = unquote(value[len("/static/output/"):].lstrip("/"))
            image_path = OUTPUT_DIR / relative_path
        else:
            image_path = Path(unquote(value))

        if not image_path.is_absolute():
            image_path = self.base_dir / image_path
        return image_path, None

    def download_image(self, url: str) -> Path:
        suffix = Path(url.split("?", maxsplit=1)[0]).suffix or ".jpg"

        temporary = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        )
        temporary.close()
        target = Path(temporary.name)

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
                )
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=30,
            ) as response:
                content_type = response.headers.get(
                    "Content-Type",
                    "",
                ).lower()

                if not content_type.startswith("image/"):
                    raise ValueError(
                        f"URL không trả về ảnh: {content_type}"
                    )

                target.write_bytes(response.read())

            return target
        except Exception:
            target.unlink(missing_ok=True)
            raise

    def render_image(self, slide, e: ET.Element) -> None:
        src = e.get("src")
        if not src:
            raise ValueError("Image thiếu src")

        temp_path: Path | None = None
        converted_path: Path | None = None

        try:
            image_path, temp_path = self.resolve_image_source(src)
        except Exception as exc:
            print(f"  Bỏ qua ảnh tải lỗi: {src[:160]}")
            print(f"  Lý do: {exc}")
            return

        try:
            if not image_path.exists():
                print(f"  Bỏ qua ảnh không tồn tại: {image_path}")
                return

            target_x = self.x(e.get("x"))
            target_y = self.y(e.get("y"))
            target_width = self.x(e.get("width"))
            target_height = self.y(e.get("height"))

            # SVG is a supported browser image format but Pillow/python-pptx
            # cannot embed it directly. Reuse the existing headless-browser
            # SVG renderer so imported SVG files/data URLs also export.
            if image_path.suffix.lower() == ".svg":
                svg_element = ET.Element("svg", dict(e.attrib))
                svg_element.text = image_path.read_text(encoding="utf-8")
                self.render_svg(slide, svg_element)
                return

            # Fill the requested box without stretching the source image.
            # The excess area is cropped symmetrically from the center.
            with Image.open(image_path) as source_image:
                source_width, source_height = source_image.size

            pptx_image_path, converted_path = self._prepare_pptx_image(
                image_path
            )

            picture = slide.shapes.add_picture(
                str(pptx_image_path),
                target_x,
                target_y,
                target_width,
                target_height,
            )

            if source_width > 0 and source_height > 0:
                source_ratio = source_width / source_height
                target_ratio = target_width / target_height

                if source_ratio > target_ratio:
                    visible_width = target_ratio / source_ratio
                    horizontal_crop = (1.0 - visible_width) / 2.0
                    picture.crop_left = horizontal_crop
                    picture.crop_right = horizontal_crop
                elif source_ratio < target_ratio:
                    visible_height = source_ratio / target_ratio
                    vertical_crop = (1.0 - visible_height) / 2.0
                    picture.crop_top = vertical_crop
                    picture.crop_bottom = vertical_crop
        finally:
            if converted_path is not None:
                converted_path.unlink(missing_ok=True)
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def render_svg(self, slide, e: ET.Element) -> None:
        svg_markup = "".join(e.itertext()).strip()
        if not svg_markup:
            raise ValueError("svg thieu noi dung")

        pixel_width = int(float(e.get("pixel_width", e.get("width", "1600"))))
        pixel_height = int(float(e.get("pixel_height", e.get("height", "900"))))

        browser_candidates = self.svg_renderer_candidates()
        if not browser_candidates:
            raise ValueError("Khong tim thay trinh duyet de render svg")

        svg_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".svg",
        )
        svg_file.close()
        svg_path = Path(svg_file.name)

        html_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".html",
        )
        html_file.close()
        html_path = Path(html_file.name)

        png_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".png",
        )
        png_file.close()
        png_path = Path(png_file.name)

        try:
            svg_path.write_text(
                svg_markup,
                encoding="utf-8",
            )

            html_path.write_text(
                (
                    "<!doctype html><html><head><meta charset=\"utf-8\">"
                    "<style>html,body{margin:0;padding:0;background:transparent;"
                    f"width:{pixel_width}px;height:{pixel_height}px;overflow:hidden;}}"
                    "img,svg{display:block;width:100%;height:100%;object-fit:fill;}"
                    "</style></head><body>"
                    f"<img src=\"file:///{svg_path.as_posix()}\" alt=\"svg\" />"
                    "</body></html>"
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    str(browser_candidates[0]),
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--default-background-color=00000000",
                    "--hide-scrollbars",
                    f"--window-size={pixel_width},{pixel_height}",
                    f"--screenshot={png_path}",
                    html_path.resolve().as_uri(),
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )

            slide.shapes.add_picture(
                str(png_path),
                self.x(e.get("x")),
                self.y(e.get("y")),
                self.x(e.get("width")),
                self.y(e.get("height")),
            )
        finally:
            svg_path.unlink(missing_ok=True)
            html_path.unlink(missing_ok=True)
            png_path.unlink(missing_ok=True)

    # =========================================================
    # Charts
    # =========================================================

    def render_chart(self, slide, e: ET.Element) -> None:
        chart_map = {
            "piechart": XL_CHART_TYPE.PIE,
            "barchart": XL_CHART_TYPE.COLUMN_CLUSTERED,
            "linechart": XL_CHART_TYPE.LINE_MARKERS,
        }

        series_nodes = e.findall("./series")
        data = ChartData()
        first_points: list[ET.Element] = []
        if series_nodes:
            first_points = series_nodes[0].findall("./point")
            categories = [point.get("label", "") for point in first_points]
            data.categories = categories

            for index, series in enumerate(series_nodes, start=1):
                values = [
                    float(point.get("value", "0"))
                    for point in series.findall("./point")
                ]
                data.add_series(series.get("name", f"Series {index}"), values)
        else:
            raw_values = [
                value.strip()
                for value in e.get("data", "").split(",")
                if value.strip()
            ]
            values = [float(value) for value in raw_values if self._is_number(value)]
            if not values:
                raise ValueError(f"{e.tag} thiếu series hoặc data")
            raw_labels = [label.strip() for label in e.get("labels", "").split(",") if label.strip()]
            data.categories = raw_labels if len(raw_labels) == len(values) else [str(index + 1) for index in range(len(values))]
            data.add_series(e.get("title", "Series 1"), values)

        frame = slide.shapes.add_chart(
            chart_map[e.tag],
            self.x(e.get("x")),
            self.y(e.get("y")),
            self.x(e.get("width")),
            self.y(e.get("height")),
            data,
        )

        chart = frame.chart
        chart.has_legend = self.to_bool(
            e.get("show_legend"),
            True,
        )

        if chart.has_legend:
            legend_map = {
                "bottom": XL_LEGEND_POSITION.BOTTOM,
                "top": XL_LEGEND_POSITION.TOP,
                "left": XL_LEGEND_POSITION.LEFT,
                "right": XL_LEGEND_POSITION.RIGHT,
            }
            chart.legend.position = legend_map.get(
                e.get("legend_position", "bottom"),
                XL_LEGEND_POSITION.BOTTOM,
            )

        plot = chart.plots[0]

        if self.to_bool(e.get("show_labels"), True):
            plot.has_data_labels = True
            labels = plot.data_labels
            labels.position = XL_LABEL_POSITION.BEST_FIT
            labels.show_percentage = (
                e.tag == "piechart"
                and self.to_bool(
                    e.get("show_percent"),
                    True,
                )
            )
            labels.show_value = self.to_bool(
                e.get("show_value"),
                e.tag != "piechart",
            )

        if e.tag == "piechart":
            for index, point_node in enumerate(first_points):
                color = point_node.get("color")
                if color:
                    point = chart.series[0].points[index]
                    point.format.fill.solid()
                    point.format.fill.fore_color.rgb = self.rgb(
                        color
                    )

    # =========================================================
    # Conversion
    # =========================================================

    def convert(self) -> None:
        if not self.xml_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy XML: {self.xml_path}"
            )

        # Keep the converter safe when it is called directly from the CLI or
        # a worker, bypassing the API normalization step.
        xml_content = self.xml_path.read_text(encoding="utf-8")
        normalized_xml = materialize_math_fields_in_xml(xml_content)
        normalized_xml = materialize_markdown_bold_runs(normalized_xml)
        root = ET.fromstring(normalized_xml)

        if root.tag != "presentation":
            raise ValueError("Thẻ gốc phải là <presentation>")

        self.canvas_width = float(root.get("width", "1600"))
        self.canvas_height = float(root.get("height", "900"))
        self.slide_width_inches = float(
            root.get("slideWidthInches", "13.333")
        )
        self.slide_height_inches = float(
            root.get("slideHeightInches", "7.5")
        )

        self.prs.slide_width = Inches(self.slide_width_inches)
        self.prs.slide_height = Inches(self.slide_height_inches)

        slide_nodes = root.findall("./slide")
        if not slide_nodes:
            raise ValueError("XML không có thẻ <slide>")

        for slide_index, slide_node in enumerate(
            slide_nodes,
            start=1,
        ):
            print(f"Đang tạo slide {slide_index}")

            slide = self.prs.slides.add_slide(
                self.prs.slide_layouts[6]
            )

            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = self.rgb(
                slide_node.get("background"),
                "#FFFFFF",
            )

            for element in slide_node:
                renderer = self.renderers.get(element.tag)
                if renderer is None:
                    raise ValueError(
                        f"Chưa hỗ trợ thẻ <{element.tag}>"
                    )
                if (
                    element.tag.lower() in {"textbox", "text"}
                    and any(node.tag == "math-field" for node in element.iter())
                ):
                    self.render_math_textbox(slide, element)
                else:
                    renderer(slide, element)

            self.apply_slide_transition(slide, slide_node)

        self.close_open_output_presentation()
        self.prs.save(self.output_path)
        if self.open_after_convert:
            try:
                os.startfile(str(self.output_path))
            except OSError as exc:
                print(f"Khong the mo file: {exc}")
        print(f"Đã tạo: {self.output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chuyển XML slide sang PowerPoint"
    )
    parser.add_argument("xml")
    parser.add_argument(
        "-o",
        "--output",
        default="output.pptx",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Khong tu mo file PPTX sau khi convert",
    )

    args = parser.parse_args()

    output_path = Path(args.output)

    # python-pptx chỉ tạo định dạng .pptx.
    if output_path.suffix.lower() != ".pptx":
        output_path = output_path.with_suffix(".pptx")

    XMLSlideConverter(
        Path(args.xml),
        output_path,
        open_after_convert=not args.no_open,
    ).convert()


if __name__ == "__main__":
    main()
