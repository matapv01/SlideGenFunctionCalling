import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_content_creation_slide_xml,
)


def test_content_creation_uses_canonical_canvas_and_scaled_geometry() -> None:
    root = ET.fromstring(
        generate_content_creation_slide_xml(
            main_title="Content\nCreation",
            original_title="Original Content",
            curated_title="Curated Content",
        )
    )

    assert root.get("width") == "1600"
    assert root.get("height") == "900"

    elements = list(root.find("slide"))
    images = [element for element in elements if element.tag == "image"]
    textboxes = [element for element in elements if element.tag == "textbox"]

    # The old 810x455 coordinates made this template occupy only the
    # top-left portion when combined with a 1600x900 project document.
    assert float(images[0].get("width")) > 950.0
    assert float(images[1].get("x")) > 1100.0
    assert float(textboxes[0].get("x")) > 1100.0
    assert float(textboxes[0].get("width")) > 400.0

    for element in [*images, *textboxes]:
        x = float(element.get("x"))
        y = float(element.get("y"))
        width = float(element.get("width"))
        height = float(element.get("height"))
        assert 0.0 <= x <= 1600.0
        assert 0.0 <= y <= 900.0
        assert x + width <= 1600.0 + 0.5
        assert y + height <= 900.0 + 0.5
