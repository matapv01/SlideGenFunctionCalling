import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.nodes.tool_call_executor import validate_tool_call
from backend.workflows.slidegen_workflow.tools.tool_des_xml import execute_tool


def test_numbered_list_legacy_name_is_normalized_to_registered_tool() -> None:
    call = {
        "name": "generate_numbered_list_slide_xml",
        "arguments": {
            "title": "CONTENTS",
            "items": ["Project summary", "Market overview"],
            "background_color": "#FFFFFF",
            "accent_color": "#008080",
            "text_color": "#111111",
            "subtitle": "Detailed presentation contents",
            "image_position": "Right",
            "image_url": "",
        },
    }

    valid, errors = validate_tool_call(call)
    assert valid, errors
    # A stale candidate list must not turn a known alias back into an
    # unregistered-tool failure; execution uses the canonical registry.
    valid, errors = validate_tool_call(call, available_tool_names=["some_other_tool"])
    assert valid, errors

    xml = execute_tool(call)
    root = ET.fromstring(xml)
    assert root.tag == "presentation"
    assert "Project summary" in {node.text for node in root.findall(".//textbox")}
    assert "Market overview" in {node.text for node in root.findall(".//textbox")}
