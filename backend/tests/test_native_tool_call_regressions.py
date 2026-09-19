from backend.workflows.slidegen_workflow.nodes.tool_call_executor import (
    _normalize_plan_for_execution,
)
from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    TOOLS_DICT,
    normalize_tool_arguments,
)


def _all_tools():
    return [tool for tools in TOOLS_DICT.values() for tool in tools]


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
