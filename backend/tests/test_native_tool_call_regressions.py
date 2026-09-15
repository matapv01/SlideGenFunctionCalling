from backend.workflows.slidegen_workflow.nodes.slide_generator import (
    _complete_native_tool_plan,
)
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import (
    _normalize_plan_for_execution,
)
from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    TOOLS_DICT,
    normalize_tool_arguments,
)


def _all_tools():
    return [tool for tools in TOOLS_DICT.values() for tool in tools]


def test_missing_native_image_calls_are_completed_from_tool_schema():
    tool = next(
        tool for tool in _all_tools()
        if tool.name == "generate_ai_content_slide_xml"
    )
    plan = [
        {
            "name": tool.name,
            "arguments": {
                "title": "Content",
                "intro_text": "Description",
                "bullet_items": ["Point one"],
                "footer_text": "Footer",
                "image_url": "",
            },
        }
    ]

    completed = _complete_native_tool_plan(
        plan,
        [tool],
        "Content creation marketing",
    )

    assert [call["name"] for call in completed] == [
        tool.name,
        "search_ddgs_images",
    ]
    assert all(call["arguments"]["query"] for call in completed[1:])


def test_json_encoded_array_arguments_are_decoded():
    normalized = normalize_tool_arguments(
        "generate_ai_content_slide_xml",
        {
            "title": "AI",
            "intro_text": "Intro",
            "bullet_items": '["One"]',
        },
    )

    assert normalized["bullet_items"] == ["One"]


def test_execution_plan_drops_schema_fields_not_supported_by_function():
    tool = next(
        tool for tool in _all_tools()
        if tool.name == "generate_monthly_sales_revenue_line_slide_xml"
    )
    plan = _normalize_plan_for_execution(
        [
            {
                "name": tool.name,
                "arguments": {
                    "title": "Revenue",
                    "data": [],
                    "analysis_items": "Trend",
                    "border_color": "#3A3937",
                },
            }
        ],
        {tool.name: tool},
    )

    assert "border_color" not in plan[0]["arguments"]
