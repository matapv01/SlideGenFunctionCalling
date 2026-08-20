"""Helpers for assigning PowerPoint slide transitions to generated XML."""

from __future__ import annotations

import random
import xml.etree.ElementTree as ET
from typing import Any


# Keep the pool modern and restrained.  The XML -> PPTX converter maps these
# names to the corresponding PresentationML transition elements.
RANDOM_TRANSITION_TYPES = (
    "fade",
    "push",
    "wipe",
    "split",
    "cover",
    "uncover",
    "zoom",
    "circle",
    "diamond",
    "plus",
)
_DIRECTIONAL_TRANSITIONS = {"push", "wipe", "cover", "uncover", "split", "zoom"}
_DIRECTIONS = ("l", "r", "u", "d")
DEFAULT_TRANSITION_DURATION_MS = 700


def apply_random_slide_transitions(
    xml_content: str,
    *,
    rng: random.Random | Any | None = None,
) -> tuple[str, list[dict[str, str]]]:
    """Assign a random transition to every ``<slide>`` in an XML document.

    The generated attributes are consumed later by ``XMLSlideConverter``.
    Keeping the transition in the XML means the generation workflow remains
    XML-only and does not need to open a browser or create a PNG.

    Invalid or non-presentation XML is returned unchanged.  The existing XML
    validator remains responsible for reporting malformed tool output.
    """
    if not isinstance(xml_content, str) or not xml_content.strip():
        return xml_content, []

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return xml_content, []

    slide_nodes = [node for node in root if node.tag.rsplit("}", 1)[-1] == "slide"]
    if not slide_nodes:
        return xml_content, []

    chooser = rng or random
    applied: list[dict[str, str]] = []
    for slide_node in slide_nodes:
        transition_type = str(chooser.choice(RANDOM_TRANSITION_TYPES))
        slide_node.set("transition", transition_type)
        slide_node.set("transition_duration", str(DEFAULT_TRANSITION_DURATION_MS))
        slide_node.set("transition_advance", "click")

        transition_info = {"type": transition_type}
        if transition_type in _DIRECTIONAL_TRANSITIONS:
            direction = str(chooser.choice(_DIRECTIONS))
            slide_node.set("transition_direction", direction)
            transition_info["direction"] = direction
        else:
            slide_node.attrib.pop("transition_direction", None)

        applied.append(transition_info)

    return ET.tostring(root, encoding="unicode"), applied
