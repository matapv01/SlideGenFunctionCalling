import xml.etree.ElementTree as ET

from backend.workflows.slidegen_workflow.nodes.tool_call_executor import validate_tool_call
from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    constrain_tool_call_to_candidates,
    execute_tool,
)


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


def test_split_content_layout_alias_executes_registered_tool() -> None:
    call = {
        "name": "generate_split_content_layout_slide_xml",
        "arguments": {
            "title": "Hai góc nhìn",
            "column_titles": ["Truyền thống", "Hiện đại"],
            "column_descriptions": ["Giá trị lâu đời", "Cách tiếp cận mới"],
        },
    }

    valid, errors = validate_tool_call(call)
    assert valid, errors
    assert ET.fromstring(execute_tool(call)).tag == "presentation"


def test_hallucinated_name_is_constrained_to_single_assigned_layout() -> None:
    call = {
        "name": "generate_hero_image_split_layout_slide_xml",
        "arguments": {"title": "Hà Nội"},
    }

    corrected = constrain_tool_call_to_candidates(
        call,
        ["generate_picture_quote_slide_xml"],
    )

    assert corrected["name"] == "generate_picture_quote_slide_xml"
    assert corrected["arguments"] == call["arguments"]


def test_unknown_name_is_not_guessed_when_multiple_layouts_are_available() -> None:
    call = {"name": "generate_four_image_grid_slide_xml", "arguments": {}}

    corrected = constrain_tool_call_to_candidates(
        call,
        ["generate_topics_overview_slide_xml", "generate_timeline_gallery_slide_xml"],
    )

    assert corrected["name"] == call["name"]


def test_registered_layout_is_not_renamed_with_incompatible_arguments() -> None:
    call = {
        "name": "generate_split_content_slide_xml",
        "arguments": {
            "title": "Kiến trúc",
            "column_titles": ["Tổng thể", "Hệ thống"],
            "column_descriptions": ["Các thành phần", "Quy trình xử lý"],
        },
    }

    corrected = constrain_tool_call_to_candidates(
        call,
        ["generate_platform_instructions_slide_xml"],
    )

    assert corrected == call


def test_social_media_cards_accept_loose_string_items() -> None:
    call = {
        "name": "generate_social_media_points_slide_xml",
        "arguments": {
            "title": "Hai phong cách thi đấu",
            "cards": ["Sức mạnh và tốc độ", "Kỹ thuật và kiến tạo"],
        },
    }

    valid, errors = validate_tool_call(call)
    assert valid, errors
    xml = execute_tool(call)
    assert "Slide content is temporarily unavailable" not in xml
    assert ET.fromstring(xml).tag == "presentation"


def test_problem_slide_accepts_object_items_and_scalar_card_colors() -> None:
    call = {
        "name": "generate_problem_slide_xml",
        "arguments": {
            "title": "Vấn đề",
            "description": "Ba thách thức chính",
            "problem_items": [
                {"title": "Chi phí cao"},
                {"description": "Quy trình chậm"},
            ],
            "card_colors": "#0D9488",
            "card_text_colors": "#FFFFFF",
        },
    }

    valid, errors = validate_tool_call(call)
    assert valid, errors
    xml = execute_tool(call)
    assert "Slide content is temporarily unavailable" not in xml
    assert ET.fromstring(xml).tag == "presentation"


def test_implementation_timeline_accepts_loose_milestone_shapes() -> None:
    call = {
        "name": "generate_implementation_timeline_slide_xml",
        "arguments": {
            "title": "Lộ trình triển khai",
            "subtitle": "Ba giai đoạn chính",
            "timeline_items": [
                "Khởi động dự án",
                {"phase": "Giai đoạn 2", "description": "Thử nghiệm"},
            ],
        },
    }

    valid, errors = validate_tool_call(call)
    assert valid, errors
    xml = execute_tool(call)
    assert "Slide content is temporarily unavailable" not in xml
    assert ET.fromstring(xml).tag == "presentation"


def test_three_ideas_accepts_combined_idea_objects() -> None:
    call = {
        "name": "generate_three_ideas_slide_xml",
        "arguments": {
            "title": "Ba ý tưởng",
            "ideas": [
                {"heading": "Một", "content": "Nội dung một"},
                {"heading": "Hai", "content": "Nội dung hai"},
                {"heading": "Ba", "content": "Nội dung ba"},
            ],
        },
    }

    valid, errors = validate_tool_call(call)
    assert valid, errors
    xml = execute_tool(call)
    assert "Slide content is temporarily unavailable" not in xml
    assert ET.fromstring(xml).tag == "presentation"


def test_deep_schema_validation_rejects_invalid_nested_items_before_execution() -> None:
    call = {
        "name": "generate_how_forge_works_slide_xml",
        "arguments": {
            "title": "Quy trình",
            "subtitle": "Các bước",
            "steps": ["Bước không đúng schema"],
        },
    }

    valid, errors = validate_tool_call(call)
    assert not valid
    assert any("SCHEMA_VALIDATION_ERROR" in error for error in errors)
