import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_two_ideas_slide_xml,
)


def _textboxes(xml: str) -> list[ET.Element]:
    return ET.fromstring(xml).findall(".//textbox")


def test_light_background_gets_readable_idea_text_colors() -> None:
    boxes = _textboxes(
        generate_two_ideas_slide_xml(
            central_title="2.3. MARKET ANALYSIS",
            idea_1_title="Initial investment requirement",
            idea_1_text="Initial funding for R&D activities.",
            idea_2_title="Brand reputation",
            idea_2_text="Brand reputation is an important barrier.",
            background_color="#FFFFFF",
            title_color="#1A3A5F",
        )
    )

    # The caller changed only the background/title, so the old light defaults
    # must not remain invisible on the white content panel.
    assert boxes[0].get("color") == "#1A3A5F"
    assert boxes[1].get("color") == "#1A3A5F"
    assert boxes[2].get("color") == "#34495E"
    assert boxes[3].get("color") == "#1A3A5F"
    assert boxes[4].get("color") == "#34495E"


def test_dark_background_preserves_light_text_defaults() -> None:
    boxes = _textboxes(
        generate_two_ideas_slide_xml(
            central_title="TWO IDEAS",
            idea_1_title="FIRST",
            idea_1_text="One.",
            idea_2_title="SECOND",
            idea_2_text="Two.",
        )
    )

    assert [box.get("color") for box in boxes] == [
        "#FFFFFF",
        "#FFFFFF",
        "#F1F1F1",
        "#FFFFFF",
        "#F1F1F1",
    ]
