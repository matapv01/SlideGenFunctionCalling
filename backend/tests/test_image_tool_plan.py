import json

import pytest
from pydantic import BaseModel, Field

from backend.workflows.slidegen_workflow.executors import tool_plan_executor
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    ToolPlanError,
    execute_image_search_plan,
    get_image_targets_in_order,
)
from backend.workflows.slidegen_workflow.tools.ddgs_tool import (
    _parse_target_dimensions,
    _rank_image_results,
)
from backend.workflows.slidegen_workflow.tools.tool_des_xml import execute_tool_plan
from backend.workflows.slidegen_workflow.utils.helper import (
    parse_tool_call_json,
    parse_tool_calls_json,
)


class TwoImageSlideInput(BaseModel):
    title: str
    image_url_1: str = Field(
        default="",
        description="First image, portrait orientation.",
    )
    image_url_2: str = Field(
        default="",
        description="Second image, wide landscape orientation.",
    )


class NoImageSlideInput(BaseModel):
    title: str


class FakeTool:
    def __init__(self, schema):
        self.args_schema = schema


def test_parse_repeated_qwen_tool_calls_preserves_order():
    raw = """
<tool_call>
{"name":"search_ddgs_images","arguments":{"query":"medical diagnosis","layout":"Tall"}}
</tool_call>
<tool_call>
{"name":"generate_test_slide","arguments":{"title":"AI in healthcare"}}
</tool_call>
"""

    calls = parse_tool_calls_json(raw)

    assert [call["name"] for call in calls] == [
        "search_ddgs_images",
        "generate_test_slide",
    ]
    assert parse_tool_call_json(raw)["name"] == "generate_test_slide"


def test_parse_tool_calls_wrapper():
    raw = json.dumps(
        {
            "tool_calls": [
                {
                    "name": "search_ddgs_images",
                    "arguments": {"query": "medical diagnosis"},
                },
                {
                    "name": "generate_test_slide",
                    "arguments": {"title": "AI"},
                },
            ]
        }
    )

    assert len(parse_tool_calls_json(raw)) == 2


def test_parse_list_inside_single_tool_call_tag():
    raw = (
        "<tool_call>"
        '[{"name":"search_ddgs_images","arguments":{"query":"hospital"}},'
        '{"name":"generate_test_slide","arguments":{"title":"AI"}}]'
        "</tool_call>"
    )

    assert [call["name"] for call in parse_tool_calls_json(raw)] == [
        "search_ddgs_images",
        "generate_test_slide",
    ]


def test_schema_image_targets_keep_declaration_order():
    targets = get_image_targets_in_order(
        FakeTool(TwoImageSlideInput),
        {"title": "AI"},
    )

    assert [target["path_string"] for target in targets] == [
        "image_url_1",
        "image_url_2",
    ]


def test_nested_runtime_image_targets_are_supported():
    class TeamSlideInput(BaseModel):
        team_members: list[dict[str, str]]

    arguments = {
        "team_members": [
            {"name": "A", "image_url": ""},
            {"name": "B", "image_url": ""},
        ]
    }

    targets = get_image_targets_in_order(
        FakeTool(TeamSlideInput),
        arguments,
    )

    assert [target["path_string"] for target in targets] == [
        "team_members[0].image_url",
        "team_members[1].image_url",
    ]


def test_execute_searches_then_injects_by_search_order(monkeypatch):
    def fake_search(query, layout=None, size=None, max_results=3, **kwargs):
        return json.dumps([f"https://example.com/{query.replace(' ', '-')}.jpg"])

    monkeypatch.setattr(tool_plan_executor, "search_ddgs_images", fake_search)
    monkeypatch.setattr(tool_plan_executor, "_pick_live_url", lambda urls: urls[0])

    plan = [
        {
            "name": "generate_test_slide",
            "arguments": {"title": "AI in healthcare"},
        },
        {
            "name": "search_ddgs_images",
            "arguments": {"query": "medical diagnosis", "layout": "Tall"},
        },
        {
            "name": "search_ddgs_images",
            "arguments": {"query": "surgical robot", "layout": "Wide"},
        },
    ]

    final_call, history = execute_image_search_plan(
        plan,
        {"generate_test_slide": FakeTool(TwoImageSlideInput)},
    )

    assert final_call["arguments"]["image_url_1"].endswith(
        "/medical-diagnosis.jpg"
    )
    assert final_call["arguments"]["image_url_2"].endswith(
        "/surgical-robot.jpg"
    )
    assert [item["name"] for item in history] == [
        "search_ddgs_images",
        "search_ddgs_images",
    ]
    assert [item["arguments"]["query"] for item in history] == [
        "medical diagnosis",
        "surgical robot",
    ]
    assert [item["target_param"] for item in history] == [
        "image_url_1",
        "image_url_2",
    ]


def test_execute_tool_plan_renders_real_xml_slide_with_injected_image(monkeypatch):
    def fake_search(query, layout=None, size=None, max_results=3, **kwargs):
        return json.dumps(["https://example.com/messi.jpg"])

    monkeypatch.setattr(tool_plan_executor, "search_ddgs_images", fake_search)
    monkeypatch.setattr(tool_plan_executor, "_pick_live_url", lambda urls: urls[0])

    xml, final_call, history = execute_tool_plan(
        [
            {
                "name": "generate_modern_cover_slide_xml",
                "arguments": {
                    "title": "Messi career highlights",
                    "image_url": "",
                },
            },
            {
                "name": "search_ddgs_images",
                "arguments": {
                    "query": "Lionel Messi football",
                    "layout": "Tall",
                    "size": "Large",
                },
            },
        ]
    )

    assert "https://example.com/messi.jpg" in xml
    assert final_call["arguments"]["image_url"] == "https://example.com/messi.jpg"
    assert history[0]["target_param"] == "image_url"


def test_ddgs_ranking_prefers_target_dimensions_and_layout():
    results = [
        {
            "image": "https://example.com/wide.jpg",
            "width": 1920,
            "height": 1080,
        },
        {
            "image": "https://example.com/square.jpg",
            "width": 900,
            "height": 900,
        },
        {
            "image": "https://example.com/portrait.jpg",
            "width": 960,
            "height": 1080,
        },
    ]

    ranked = _rank_image_results(
        results,
        target_description=(
            "Recommended image size: 960x1080px "
            "(portrait, covers right half of slide)."
        ),
        layout="Tall",
        size="Large",
    )

    assert _parse_target_dimensions("Recommended image size: 960x1080px") == (
        960,
        1080,
    )
    assert ranked[0]["image"] == "https://example.com/portrait.jpg"


def test_plan_rejects_wrong_search_count():
    plan = [
        {
            "name": "generate_test_slide",
            "arguments": {"title": "AI"},
        },
        {
            "name": "search_ddgs_images",
            "arguments": {"query": "medical diagnosis"},
        },
    ]

    with pytest.raises(ToolPlanError, match="requires 2 image search"):
        execute_image_search_plan(
            plan,
            {"generate_test_slide": FakeTool(TwoImageSlideInput)},
        )


def test_tool_without_images_accepts_only_html_call():
    final_call, history = execute_image_search_plan(
        [{"name": "generate_text_slide", "arguments": {"title": "Summary"}}],
        {"generate_text_slide": FakeTool(NoImageSlideInput)},
    )

    assert final_call["name"] == "generate_text_slide"
    assert history == []
