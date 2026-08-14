"""Parse LLM highlight markers and apply them to generated slide XML."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any
import xml.etree.ElementTree as ET


DEFAULT_HIGHLIGHT_COLOR = "#2563EB"
MAX_HIGHLIGHTS_PER_SLIDE = 3

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
HIGHLIGHT_MARKER_RE = re.compile(
    r"\[\[hl\s+color=\"(?P<color>[^\"]+)\"\]\]"
    r"(?P<text>.*?)"
    r"\[\[/hl\]\]",
    flags=re.IGNORECASE | re.DOTALL,
)
# Accept the earlier marker during migration, but only retain its foreground
# color. New generation is instructed to use ``color=`` exclusively.
LEGACY_HIGHLIGHT_MARKER_RE = re.compile(
    r"\[\[hl\s+bg=\"(?P<background>[^\"]+)\"\s+"
    r"fg=\"(?P<foreground>[^\"]+)\"\]\]"
    r"(?P<text>.*?)"
    r"\[\[/hl\]\]",
    flags=re.IGNORECASE | re.DOTALL,
)
LITERAL_MATH_FIELD_RE = re.compile(
    r"<math-field(?:\s+value=\"(?P<value>[^\"]*)\")?\s*>"
    r"(?P<body>.*?)"
    r"</math-field>",
    flags=re.IGNORECASE | re.DOTALL,
)
MARKDOWN_BOLD_RE = re.compile(r"\*\*(?P<text>.+?)\*\*", flags=re.DOTALL)


@dataclass(frozen=True)
class HighlightSpec:
    """One semantic text highlight selected by the LLM."""

    text: str
    text_color: str
    source_path: str = ""


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
    # where a literal math-field may still be escaped inside either textbox
    # tag.  Normalize both supported text element names at this boundary.
    for textbox in root.iter():
        if textbox.tag not in {"textbox", "text"}:
            continue
        if list(textbox):
            continue
        raw_text = textbox.text or ""
        matches = list(LITERAL_MATH_FIELD_RE.finditer(raw_text))
        if not matches:
            continue

        textbox.text = raw_text[: matches[0].start()]
        for index, match in enumerate(matches):
            field = ET.SubElement(textbox, "math-field")
            value = match.group("value")
            body = match.group("body") or ""
            if value is not None:
                field.set("value", value)
            if body:
                field.text = body
            next_start = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(raw_text)
            )
            field.tail = raw_text[match.end() : next_start]
        changed = True

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

        def replace(match: re.Match[str]) -> str:
            marked_text = match.group("text")
            return record(marked_text, match.group("color"))

        def replace_legacy(match: re.Match[str]) -> str:
            marked_text = match.group("text")
            return record(marked_text, match.group("foreground"))

        without_legacy_markers = LEGACY_HIGHLIGHT_MARKER_RE.sub(
            replace_legacy,
            value,
        )
        return HIGHLIGHT_MARKER_RE.sub(replace, without_legacy_markers)

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
