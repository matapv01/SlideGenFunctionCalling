import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.nodes.tool_call_executor import (
    _fallback_xml_for_failed_tool,
    _store_best_available_fallback,
)


def test_parse_failure_fallback_displays_source_content_not_internal_error() -> None:
    xml = _fallback_xml_for_failed_tool(
        {"name": "PARSE_ERROR", "arguments": {}},
        "MISSING_NATIVE_TOOL_CALL",
        "4\n2. Phương pháp được đề xuất\n- Kiến trúc tổng thể\n- Kiến trúc hệ thống",
    )

    root = ET.fromstring(xml)
    visible_text = "\n".join(node.text or "" for node in root.findall(".//textbox"))
    assert "2. Phương pháp được đề xuất" in visible_text
    assert "Kiến trúc tổng thể" in visible_text
    assert "PARSE_ERROR" not in visible_text
    assert "MISSING_NATIVE_TOOL_CALL" not in visible_text


def test_later_parse_failure_reuses_last_valid_xml() -> None:
    previous_xml = _fallback_xml_for_failed_tool(
        {},
        "",
        "Slide hợp lệ\nNội dung đã tạo",
    )
    previous_call = {
        "name": "generate_platform_instructions_slide_xml",
        "arguments": {"items": []},
    }
    state = {
        "last_valid_xml_content": previous_xml,
        "last_valid_tool_call": previous_call,
        "current_slide_text": "Nội dung mới",
    }

    def _must_not_execute(*_args, **_kwargs):
        raise AssertionError("last valid XML should be reused without executing fallback")

    _store_best_available_fallback(
        state,
        _must_not_execute,
        {"name": "PARSE_ERROR", "arguments": {}},
        "missing tool call",
    )

    assert state["current_xml_content"] == previous_xml
    assert state["current_tool_call"] == previous_call
