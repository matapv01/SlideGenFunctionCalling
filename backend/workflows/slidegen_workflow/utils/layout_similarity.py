"""Content-independent XML layout signatures and similarity scoring."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Optional, Tuple
import xml.etree.ElementTree as ET

from backend.config import ADJACENT_LAYOUT_SIMILARITY, GLOBAL_LAYOUT_SIMILARITY

_GEOMETRY_KEYS = ("x", "y", "width", "height", "cx", "cy", "r")
_STRUCTURAL_KEYS = (
    "type",
    "align",
    "vertical_align",
    "orientation",
    "chart_type",
    "clip",
)
_LAYOUT_TAGS = {
    "textbox",
    "image",
    "shape",
    "line",
    "polygon",
    "svg",
    "group",
    "chart",
    "table",
    "video",
}


def _tag_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _quantize(value: Any, quantum: int = 20) -> str:
    try:
        number = float(value)
        return str(int(round(number / quantum) * quantum))
    except (TypeError, ValueError):
        return str(value)


def build_layout_signature(xml_content: str) -> Dict[str, Any]:
    """Describe element geometry while intentionally ignoring text and colors."""
    root = ET.fromstring(xml_content)
    features: Counter[str] = Counter()

    def walk(element: ET.Element, depth: int = 0) -> None:
        tag = _tag_name(element.tag)
        if tag in _LAYOUT_TAGS:
            parts = [tag]
            for key in _GEOMETRY_KEYS:
                if key in element.attrib:
                    parts.append(f"{key}={_quantize(element.attrib[key])}")
            for key in _STRUCTURAL_KEYS:
                if key in element.attrib:
                    parts.append(f"{key}={element.attrib[key]}")
            parts.append(f"depth={depth}")
            features["|".join(parts)] += 1
        for child in element:
            walk(child, depth + 1)

    walk(root)

    return {
        "features": dict(features),
        "element_count": sum(features.values()),
    }
def layout_similarity(left: Dict[str, Any], right: Dict[str, Any]) -> float:
    left_counter = Counter(left.get("features") or {})
    right_counter = Counter(right.get("features") or {})
    denominator = max(sum(left_counter.values()), sum(right_counter.values()), 1)
    overlap = sum((left_counter & right_counter).values())
    return overlap / denominator


def find_layout_duplicate(
    signature: Dict[str, Any],
    slide_index: int,
    accepted: List[Dict[str, Any]],
) -> Optional[Tuple[Dict[str, Any], float]]:
    best: Optional[Tuple[Dict[str, Any], float]] = None
    for candidate in accepted:
        if candidate.get("exempt"):
            continue
        score = layout_similarity(signature, candidate.get("signature") or {})
        threshold = (
            ADJACENT_LAYOUT_SIMILARITY
            if abs(slide_index - int(candidate.get("index", -999))) == 1
            else GLOBAL_LAYOUT_SIMILARITY
        )
        if score >= threshold and (best is None or score > best[1]):
            best = (candidate, score)
    return best
