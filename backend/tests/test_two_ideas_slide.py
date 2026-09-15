import xml.etree.ElementTree as ET

import pytest

from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_two_ideas_slide_xml,
)


def _textboxes(xml: str) -> list[ET.Element]:
    return ET.fromstring(xml).findall(".//textbox")


def test_light_background_gets_readable_idea_text_colors() -> None:
    boxes = _textboxes(
        generate_two_ideas_slide_xml(
            title="2.3. MARKET ANALYSIS",
            idea_titles=[
                "Initial investment requirement",
                "Brand reputation",
            ],
            idea_descriptions=[
                "Initial funding for R&D activities.",
                "Brand reputation is an important barrier.",
            ],
            background_color="#FFFFFF",
            title_color="#1A3A5F",
            heading_color="#1A3A5F",
            body_color="#34495E",
        )
    )

    assert boxes[0].get("color") == "#1A3A5F"
    assert boxes[1].get("color") == "#1A3A5F"
    assert boxes[2].get("color") == "#34495E"
    assert boxes[3].get("color") == "#1A3A5F"
    assert boxes[4].get("color") == "#34495E"


def test_dark_background_preserves_light_text_defaults() -> None:
    boxes = _textboxes(
        generate_two_ideas_slide_xml(
            title="TWO IDEAS",
            idea_titles=["FIRST", "SECOND"],
            idea_descriptions=["One.", "Two."],
        )
    )

    assert [box.get("color") for box in boxes] == [
        "#FFFFFF",
        "#FFFFFF",
        "#F1F1F1",
        "#FFFFFF",
        "#F1F1F1",
    ]


def test_two_ideas_requires_exactly_two_items() -> None:
    with pytest.raises(ValueError, match="exactly two"):
        generate_two_ideas_slide_xml(
            title="TWO IDEAS",
            idea_titles=["ONLY ONE"],
            idea_descriptions=["One."],
        )
