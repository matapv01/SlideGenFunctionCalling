import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_bullet_content_slide_xml,
)


def test_long_bullet_content_does_not_collapse_textbox_width() -> None:
    long_item = (
        "This is deliberately long bullet content used to push later "
        "items below the nominal slide boundary during layout."
    )

    root = ET.fromstring(
        generate_bullet_content_slide_xml(
            title="Layout regression",
            bullet_items=[long_item] * 6,
            closing_text="A closing statement that also needs a usable box.",
        )
    )

    textboxes = root.findall(".//textbox")
    content_boxes = [
        textbox
        for textbox in textboxes
        if float(textbox.get("width", "0")) != 44.0
    ]

    assert content_boxes
    assert min(float(box.get("width", "0")) for box in content_boxes) >= 486.0
