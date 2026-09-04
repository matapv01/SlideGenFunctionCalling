import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.tools.xml_tool import (
    generate_instructions_slide_xml,
)
from backend.workflows.slidegen_workflow.utils.xml_overflow import analyze_xml_root


def test_wrapped_title_pushes_columns_and_footer_below_it() -> None:
    xml = generate_instructions_slide_xml(
        title="2.3. HTML FUNCTIONS LIBRARY",
        left_heading="FEATURES",
        left_paragraphs=[
            "Diverse HTML CSS slide library",
            "Each function includes details.",
            "Rich layouts and styles.",
        ],
        right_heading="TOOL STRUCTURE",
        right_paragraphs=[
            "Name, description and data type.",
            "Parameters and topic fit.",
            "Required parameters are clear.",
        ],
        footer_text="2. PROPOSED METHOD",
    )
    root = ET.fromstring(xml)
    textboxes = list(root.iter("textbox"))

    title = textboxes[0]
    column_boxes = textboxes[1:-1]
    footer = textboxes[-1]

    title_bottom = float(title.get("y")) + float(title.get("height"))
    first_column_top = min(float(box.get("y")) for box in column_boxes)
    columns_bottom = max(
        float(box.get("y")) + float(box.get("height"))
        for box in column_boxes
    )
    footer_top = float(footer.get("y"))

    assert first_column_top >= title_bottom + 25.0
    assert footer_top >= columns_bottom + 27.0
    assert footer_top + float(footer.get("height")) <= 900.0
    assert not any(record["overflow"] for record in analyze_xml_root(root))
