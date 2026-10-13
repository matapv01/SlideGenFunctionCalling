"""Deterministically shrink text that does not fit its textbox in generated slide XML.

A textbox declares both ``size`` and ``min_font_size``. When the measured text
overflows the box, step the font size down until it fits or the declared
minimum is reached.  Anything still overflowing at the minimum is left for the
caller to handle (LLM rewrite in the workflow, a reward penalty in RL).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.utils.xml_overflow import analyze_xml_root

_FIT_REASONS = {"text_height", "text_width", "max_lines"}
_SHRINK_STEP = 0.94
_DEFAULT_MIN_RATIO = 0.6
_MAX_ROUNDS = 24


def _minimum_size(element: ET.Element, original: float) -> float:
    try:
        declared = float(element.get("min_font_size", ""))
    except (TypeError, ValueError):
        declared = original * _DEFAULT_MIN_RATIO
    return min(original, max(1.0, declared))


def fit_xml_text(xml_content: str) -> tuple[str, list[dict]]:
    """Return XML whose overflowing textboxes were shrunk, plus a report of each change."""
    if not isinstance(xml_content, str) or not xml_content.strip():
        return xml_content, []
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return xml_content, []

    original: dict[int, tuple[ET.Element, float]] = {}
    for _ in range(_MAX_ROUNDS):
        changed = False
        for record in analyze_xml_root(root):
            if not _FIT_REASONS.intersection(record["reasons"]):
                continue
            element = record["_element"]
            size = float(record["font_size"])
            start = original.setdefault(id(element), (element, size))[1]
            target = max(_minimum_size(element, start), round(size * _SHRINK_STEP, 2))
            if target < size - 1e-6:
                element.set("size", f"{target:g}")
                changed = True
        if not changed:
            break

    report = [
        {"textbox": element.get("id") or "", "from": start, "to": float(element.get("size"))}
        for element, start in original.values()
        if float(element.get("size")) < start - 1e-6
    ]
    if not report:
        return xml_content, []
    return ET.tostring(root, encoding="unicode"), report
