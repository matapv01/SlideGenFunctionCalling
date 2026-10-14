"""Parse LLM highlight markers and apply them to generated slide XML."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any
import xml.etree.ElementTree as ET


DEFAULT_HIGHLIGHT_COLOR = "#2563EB"
MAX_HIGHLIGHTS_PER_SLIDE = 3

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
# Parse tags independently so nested or incomplete markers can be stripped
# without leaking their control syntax into visible text.
_HIGHLIGHT_TOKEN_RE = re.compile(
    r"\[\[hl\b[^\]]*\]\]|\[\[?/hl\]\]?",
    flags=re.IGNORECASE,
)
# The colour may be quoted or bare: a bare #RRGGBB stays valid inside JSON string values,
# where a raw double quote would end the string.
_CANONICAL_HIGHLIGHT_OPEN_RE = re.compile(
    r'^\[\[hl\s+color=(?:"(?P<color>[^\"]+)"|\'(?P<color_single>[^\']+)\'|(?P<color_bare>#[0-9A-Fa-f]{6}))\]\]$',
    flags=re.IGNORECASE,
)
_LEGACY_HIGHLIGHT_OPEN_RE = re.compile(
    r'^\[\[hl\s+bg="[^\"]+"\s+fg="(?P<color>[^\"]+)"\]\]$',
    flags=re.IGNORECASE,
)
LITERAL_MATH_FIELD_RE = re.compile(
    r"<math-field(?:\s+value=\"(?P<value>[^\"]*)\")?\s*>"
    r"(?P<body>.*?)"
    r"</math-field>",
    flags=re.IGNORECASE | re.DOTALL,
)
# Models occasionally return inline Markdown math even though the XML prompt
# requires <math-field>. Normalize the common delimiters at the XML boundary
# so browser preview, PPTX export, and saved slides all use the same path.
INLINE_LATEX_RE = re.compile(
    r"(?<!\\)(?:"
    r"\$\$(?P<display>.*?)\$\$|"
    r"\$(?P<inline>[^$\n]+?)\$|"
    r"\\\((?P<paren>.*?)\\\)|"
    r"\\\[(?P<bracket>.*?)\\\]"
    r")",
    flags=re.DOTALL,
)
# Some model responses omit the required <math-field> wrapper and write a
# short ASCII equation directly in a text box. Keep this intentionally narrow:
# only equation-shaped expressions and common derivative notation are lifted
# into math fields, so ordinary prose is not reclassified as mathematics.
_PLAIN_MATH_ATOM = (
    r"[A-Za-z](?:[A-Za-z0-9']|\([^()\n]*\)|\[[^\]\n]*\])*"
)
_SYMBOLIC_MATH_ATOM = r"[\wŷσΑ-Ωα-ω]+(?:\([^()\n]*\))?"
PLAIN_MATH_RE = re.compile(
    rf"(?<![\w])(?P<plain>"
    rf"(?:"
    rf"(?:d\s*/\s*dx\s+)?{_PLAIN_MATH_ATOM}"
    rf"(?:\s*(?:\^|/)\s*\(?[A-Za-z0-9+\-]+\)?)?"
    rf"(?:\s+{_PLAIN_MATH_ATOM})?\s*=\s*"
    rf"{_PLAIN_MATH_ATOM}"
    rf"(?:\s*(?:\^|/)\s*\(?[A-Za-z0-9+\-]+\)?)?"
    rf"(?:\s+{_PLAIN_MATH_ATOM})?"
    rf"|"
    rf"{_SYMBOLIC_MATH_ATOM}\s*=\s*"
    rf"(?=[^;\n.,:]*[∑√^/()+\-])[^;\n.,:]+?"
    rf")"
    rf")(?=$|[\s,.;:])",
    flags=re.IGNORECASE,
)
MATH_SEGMENT_RE = re.compile(
    rf"{INLINE_LATEX_RE.pattern}|{PLAIN_MATH_RE.pattern}",
    flags=re.IGNORECASE | re.DOTALL,
)
MARKDOWN_BOLD_RE = re.compile(r"\*\*(?P<text>.+?)\*\*", flags=re.DOTALL)


@dataclass(frozen=True)
class HighlightSpec:
    """One semantic text highlight selected by the LLM."""

    text: str
    text_color: str
    source_path: str = ""


def _math_segments(text: str) -> list[tuple[str, str]]:
    """Split text into ordinary text and supported LaTeX math segments."""
    segments: list[tuple[str, str]] = []
    cursor = 0
    for match in MATH_SEGMENT_RE.finditer(text):
        formula = next(
            (
                match.group(name)
                for name in ("display", "inline", "paren", "bracket", "plain")
                if match.group(name) is not None
            ),
            "",
        ).strip()
        if not formula:
            continue
        if match.start() > cursor:
            segments.append(("text", text[cursor:match.start()]))
        segments.append(("math", formula))
        cursor = match.end()
    if cursor < len(text):
        segments.append(("text", text[cursor:]))
    return segments or [("text", text)]


def _normalize_math_formula(formula: str) -> str:
    r"""Repair Markdown-escaped subscripts inside LaTeX math.

    LLM/Markdown output often turns ``_`` into ``\_`` even inside a math
    span. In LaTeX that is a literal underscore, so it prevents expressions
    such as ``\sum_{i=1}^{n}x_i`` from being parsed as scripts.
    """
    value = str(formula or "").replace(r"\_", "_")
    value = re.sub(
        r"\bd\s*/\s*dx\b",
        lambda _: r"\frac{d}{dx}",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(
        r"\bdf\s*/\s*dx\b",
        lambda _: r"\frac{df}{dx}",
        value,
        flags=re.IGNORECASE,
    )
    return re.sub(
        r"([A-Za-z0-9)\]])\^\(([^()\n]+)\)",
        lambda match: f"{match.group(1)}^{{{match.group(2)}}}",
        value,
    )


def _literal_math_segments(text: str) -> list[tuple[str, str]]:
    """Split escaped literal math-field tags and inline LaTeX together."""
    segments: list[tuple[str, str]] = []
    cursor = 0
    combined = re.compile(
        rf"{LITERAL_MATH_FIELD_RE.pattern}|{MATH_SEGMENT_RE.pattern}",
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in combined.finditer(text):
        if match.start() > cursor:
            segments.extend(_math_segments(text[cursor:match.start()]))
        if match.group("value") is not None or match.group("body") is not None:
            value = match.group("value") or match.group("body") or ""
            if value.strip():
                segments.append(("math", value.strip()))
        else:
            formula = next(
                (
                    match.group(name)
                    for name in ("display", "inline", "paren", "bracket", "plain")
                    if match.group(name) is not None
                ),
                "",
            ).strip()
            if formula:
                segments.append(("math", formula))
        cursor = match.end()
    if cursor < len(text):
        segments.extend(_math_segments(text[cursor:]))
    return segments or [("text", text)]


def _math_field(formula: str) -> ET.Element:
    field = ET.Element("math-field")
    field.text = _normalize_math_formula(formula)
    return field


def _materialize_textbox_math(textbox: ET.Element) -> bool:
    """Materialize math in leading text and direct run children."""
    changed = False
    for field in textbox.iter("math-field"):
        normalized = _normalize_math_formula(field.text or "")
        if normalized != (field.text or ""):
            field.text = normalized
            changed = True

    leading = textbox.text or ""
    leading_segments = _literal_math_segments(leading)
    if any(kind == "math" for kind, _ in leading_segments):
        textbox.text = None
        previous: ET.Element | None = None
        insert_index = 0
        for kind, value in leading_segments:
            if kind == "math":
                field = _math_field(value)
                textbox.insert(insert_index, field)
                insert_index += 1
                previous = field
            elif previous is None:
                textbox.text = (textbox.text or "") + value
            else:
                previous.tail = (previous.tail or "") + value
        changed = True

    # Runs cannot contain direct math fields in the XML schema consumed by
    # the preview/converter. Flatten a run with inline math into sibling runs
    # and math-field nodes while retaining all run styling attributes.
    for run in list(textbox):
        if run.tag != "run" or list(run):
            continue
        raw = run.text or ""
        segments = _literal_math_segments(raw)
        if not any(kind == "math" for kind, _ in segments):
            continue
        index = list(textbox).index(run)
        original_tail = run.tail
        replacements: list[ET.Element] = []
        for kind, value in segments:
            if not value:
                continue
            if kind == "math":
                replacements.append(_math_field(value))
            else:
                replacement = ET.Element("run", dict(run.attrib))
                replacement.text = value
                replacements.append(replacement)
        textbox.remove(run)
        for offset, replacement in enumerate(replacements):
            replacement.tail = original_tail if offset == len(replacements) - 1 else None
            textbox.insert(index + offset, replacement)
        changed = True
    return changed


def materialize_math_fields_in_xml(xml_content: str) -> str:
    """Turn literal ``<math-field>...</math-field>`` text into XML nodes.

    XML tool helpers receive text as Python strings, so ElementTree initially
    serializes an LLM-provided math-field as escaped text. Materializing it
    here gives both the browser preview and the PPT converter a real node.
    """
    if not str(xml_content or "").strip():
        return xml_content

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return xml_content

    changed = False
    # Export can receive XML from an older saved slide or from the editor,
    # where a literal math-field or inline Markdown math may still be escaped
    # inside either textbox tag. Normalize both supported text element names.
    for textbox in root.iter():
        if textbox.tag not in {"textbox", "text"}:
            continue
        changed = _materialize_textbox_math(textbox) or changed

    if not changed:
        return xml_content

    serialized = ET.tostring(root, encoding="unicode")
    if xml_content.lstrip().startswith("<?xml"):
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{serialized}'
    return serialized


def _markdown_bold_segments(
    text: str,
    attributes: dict[str, str],
) -> list[tuple[str, dict[str, str]]]:
    """Split ``**bold**`` spans into text and XML run attributes."""
    segments: list[tuple[str, dict[str, str]]] = []
    cursor = 0
    for match in MARKDOWN_BOLD_RE.finditer(text):
        if match.start() > cursor:
            segments.append((text[cursor:match.start()], dict(attributes)))
        bold_attributes = dict(attributes)
        bold_attributes["bold"] = "true"
        segments.append((match.group("text"), bold_attributes))
        cursor = match.end()
    if cursor < len(text):
        segments.append((text[cursor:], dict(attributes)))
    return segments or [(text, dict(attributes))]


def materialize_markdown_bold_runs(xml_content: str) -> str:
    """Turn Markdown bold markers in textboxes into editable XML runs."""
    if not str(xml_content or "").strip():
        return xml_content

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return xml_content

    changed = False
    for textbox in root.iter():
        if textbox.tag not in {"textbox", "text"}:
            continue
        if any(child.tag == "math-field" for child in list(textbox)):
            continue

        child_runs = [child for child in list(textbox) if child.tag == "run"]
        if child_runs:
            for run in child_runs:
                raw_text = run.text or ""
                if not MARKDOWN_BOLD_RE.search(raw_text):
                    continue
                index = list(textbox).index(run)
                textbox.remove(run)
                replacements = []
                for segment_text, attributes in _markdown_bold_segments(
                    raw_text,
                    dict(run.attrib),
                ):
                    if not segment_text:
                        continue
                    replacement = ET.Element("run", attributes)
                    replacement.text = segment_text
                    replacements.append(replacement)
                for offset, replacement in enumerate(replacements):
                    textbox.insert(index + offset, replacement)
                changed = True
            continue

        raw_text = textbox.text or ""
        if not MARKDOWN_BOLD_RE.search(raw_text):
            continue
        textbox.text = None
        for segment_text, attributes in _markdown_bold_segments(raw_text, {}):
            if not segment_text:
                continue
            run = ET.SubElement(textbox, "run", attributes)
            run.text = segment_text
        changed = True

    if not changed:
        return xml_content

    serialized = ET.tostring(root, encoding="unicode")
    if xml_content.lstrip().startswith("<?xml"):
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{serialized}'
    return serialized


def _normalize_hex_color(value: Any, fallback: str) -> str:
    candidate = str(value or "").strip()
    if not HEX_COLOR_RE.fullmatch(candidate):
        return fallback
    return candidate.upper()


def _phrase_pattern(phrase: str) -> re.Pattern[str] | None:
    words = re.findall(r"\S+", phrase)
    if not words:
        return None
    return re.compile(
        r"\s+".join(re.escape(word) for word in words),
        flags=re.IGNORECASE,
    )


def _phrase_matches(text: str, phrase: str) -> list[re.Match[str]]:
    pattern = _phrase_pattern(phrase)
    return list(pattern.finditer(text)) if pattern is not None else []


def extract_highlight_markers(
    arguments: dict[str, Any],
    source_content: str | None = None,
) -> tuple[dict[str, Any], list[HighlightSpec]]:
    """Remove highlight markers and retain only source-accurate phrases.

    Supported marker syntax::

        [[hl color="#2563EB"]]important text[[/hl]]

    The first three non-empty markers are retained as highlight metadata. Extra
    markers are still removed so they can never leak into visible slide text.
    The previous ``bg``/``fg`` syntax is accepted as input during migration,
    with only ``fg`` used as the text color. When source content is provided,
    a marker is retained only when its phrase occurs exactly once in that
    source, ignoring case and layout whitespace.
    """
    highlights: list[HighlightSpec] = []
    source_text = str(source_content or "")

    def clean(value: Any, path: str) -> Any:
        if isinstance(value, dict):
            return {
                key: clean(
                    child,
                    f"{path}.{key}" if path else str(key),
                )
                for key, child in value.items()
            }
        if isinstance(value, list):
            return [
                clean(child, f"{path}[{index}]")
                for index, child in enumerate(value)
            ]
        if not isinstance(value, str):
            return value

        def record(marked_text: str, requested_color: Any) -> str:
            phrase = marked_text.strip()
            source_matches = _phrase_matches(source_text, phrase)
            source_is_valid = not source_text.strip() or len(source_matches) == 1
            if (
                phrase
                and source_is_valid
                and len(highlights) < MAX_HIGHLIGHTS_PER_SLIDE
            ):
                highlights.append(
                    HighlightSpec(
                        text=phrase,
                        text_color=_normalize_hex_color(
                            requested_color,
                            DEFAULT_HIGHLIGHT_COLOR,
                        ),
                        source_path=path,
                    )
                )
            return marked_text

        def strip_and_record_markers() -> str:
            output: list[str] = []
            marked_parts: list[str] = []
            active_color: str | None = None
            depth = 0
            nested = False
            cursor = 0

            for match in _HIGHLIGHT_TOKEN_RE.finditer(value):
                segment = value[cursor:match.start()]
                if depth:
                    marked_parts.append(segment)
                else:
                    output.append(segment)

                token = match.group(0)
                if token.lstrip("[").lower().startswith("/hl"):
                    if depth:
                        depth -= 1
                        if depth == 0:
                            phrase = "".join(marked_parts)
                            if not nested and active_color is not None:
                                output.append(record(phrase, active_color))
                            else:
                                # Malformed nested markers are never promoted
                                # to styling; preserve the phrase as plain text.
                                output.append(phrase)
                            marked_parts = []
                            active_color = None
                            nested = False
                elif depth == 0:
                    canonical = _CANONICAL_HIGHLIGHT_OPEN_RE.fullmatch(token)
                    legacy = _LEGACY_HIGHLIGHT_OPEN_RE.fullmatch(token)
                    active_color = (
                        (canonical.group("color") or canonical.group("color_single") or canonical.group("color_bare"))
                        if canonical else
                        legacy.group("color") if legacy else None
                    )
                    depth = 1
                else:
                    depth += 1
                    nested = True
                cursor = match.end()

            tail = value[cursor:]
            if depth:
                marked_parts.append(tail)
                output.append("".join(marked_parts))
            else:
                output.append(tail)
            return "".join(output)

        return strip_and_record_markers()

    source = arguments if isinstance(arguments, dict) else {}
    return clean(source, ""), highlights


def _append_run(
    textbox: ET.Element,
    text: str,
    spec: HighlightSpec | None = None,
) -> None:
    if not text:
        return
    attributes: dict[str, str] = {}
    if spec is not None:
        attributes = {
            "emphasis": "highlight",
            "color": spec.text_color,
        }
    run = ET.SubElement(textbox, "run", attributes)
    run.text = text


def apply_highlights_to_xml(
    xml_content: str,
    highlights: list[HighlightSpec],
) -> str:
    """Convert matched textbox phrases to flat rich-text ``<run>`` nodes.

    Each marker is consumed once, in XML document order. Matching ignores case
    and treats any whitespace sequence as equivalent, which covers XML tools
    that uppercase titles or insert line breaks while measuring text.
    """
    if not highlights or not str(xml_content or "").strip():
        return xml_content

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return xml_content

    plain_textboxes: list[tuple[ET.Element, str]] = []
    for textbox in root.iter("textbox"):
        # Generated textboxes are plain text. Leave any pre-existing structured
        # content untouched so this postprocessor remains backwards compatible.
        if list(textbox):
            continue
        source_text = textbox.text or ""
        if source_text:
            plain_textboxes.append((textbox, source_text))

    # A phrase without a unique XML destination is ambiguous. Do not guess the
    # first occurrence because that can color the wrong title/body instance.
    candidates_by_spec: dict[int, tuple[int, int, int]] = {}
    for spec_index, spec in enumerate(highlights):
        candidates: list[tuple[int, int, int]] = []
        for textbox_index, (_, source_text) in enumerate(plain_textboxes):
            candidates.extend(
                (textbox_index, match.start(), match.end())
                for match in _phrase_matches(source_text, spec.text)
            )
        if len(candidates) == 1:
            candidates_by_spec[spec_index] = candidates[0]

    changed = False
    consumed_indexes: set[int] = set()
    for textbox_index, (textbox, source_text) in enumerate(plain_textboxes):
        matches: list[tuple[int, int, HighlightSpec]] = []
        occupied: list[tuple[int, int]] = []
        for spec_index, (candidate_textbox, start, end) in candidates_by_spec.items():
            if spec_index in consumed_indexes or candidate_textbox != textbox_index:
                continue
            if any(end <= left or start >= right for left, right in occupied):
                continue
            matches.append((start, end, highlights[spec_index]))
            occupied.append((start, end))
            consumed_indexes.add(spec_index)

        if not matches:
            continue

        textbox.text = None
        cursor = 0
        for start, end, spec in sorted(matches, key=lambda item: item[0]):
            _append_run(textbox, source_text[cursor:start])
            _append_run(textbox, source_text[start:end], spec)
            cursor = end
        _append_run(textbox, source_text[cursor:])
        changed = True

    if not changed:
        return xml_content

    serialized = ET.tostring(root, encoding="unicode")
    if xml_content.lstrip().startswith("<?xml"):
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{serialized}'
    return serialized
