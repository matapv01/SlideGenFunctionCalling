import pytest
from pydantic import BaseModel, Field

from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    NoApprovedImageError,
    get_image_targets_in_order,
    inject_approved_images,
    tool_has_image_slots,
    tool_matches_image_mode,
)
from backend.workflows.slidegen_workflow.tools.ddgs_tool import (
    _parse_target_dimensions,
    _rank_image_results,
)
from backend.workflows.slidegen_workflow.tools.tool_des_xml import execute_tool_plan


class TwoImageSlideInput(BaseModel):
    title: str
    image_url_1: str = Field(default="", description="First image, portrait orientation.")
    image_url_2: str = Field(default="", description="Second image, wide landscape orientation.")


class NoImageSlideInput(BaseModel):
    title: str


class FakeTool:
    def __init__(self, schema):
        self.args_schema = schema


def test_image_mode_matches_layout_schema_and_asset_count():
    image_tool = FakeTool(TwoImageSlideInput)
    text_tool = FakeTool(NoImageSlideInput)

    assert tool_has_image_slots(image_tool)
    assert not tool_has_image_slots(text_tool)
    assert tool_matches_image_mode(text_tool, "none")
    assert not tool_matches_image_mode(image_tool, "none")
    assert tool_matches_image_mode(image_tool, "semantic")
    assert not tool_matches_image_mode(image_tool, "semantic", approved_image_count=1)
    assert tool_matches_image_mode(image_tool, "semantic", approved_image_count=2)


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

    targets = get_image_targets_in_order(
        FakeTool(TeamSlideInput),
        {
            "team_members": [
                {"name": "A", "image_url": ""},
                {"name": "B", "image_url": ""},
            ]
        },
    )

    assert [target["path_string"] for target in targets] == [
        "team_members[0].image_url",
        "team_members[1].image_url",
    ]


def test_inject_approved_images_preserves_schema_order():
    tool = FakeTool(TwoImageSlideInput)
    final_call, history = inject_approved_images(
        {
            "name": "generate_test_slide",
            "arguments": {"title": "AI"},
        },
        tool=tool,
        approved_images=[
            {"source_type": "search", "source_id": "one", "source_url": "https://example.com/one.jpg"},
            {"source_type": "search", "source_id": "two", "source_url": "https://example.com/two.jpg"},
        ],
        asset_dir=None,
    )

    assert final_call["arguments"]["image_url_1"].endswith("/one.jpg")
    assert final_call["arguments"]["image_url_2"].endswith("/two.jpg")
    assert [item["target_param"] for item in history] == [
        "image_url_1",
        "image_url_2",
    ]


def test_execute_tool_plan_accepts_only_approved_images():
    xml, final_call, history = execute_tool_plan(
        [
            {
                "name": "generate_modern_cover_slide_xml",
                "arguments": {"title": "Messi career highlights"},
            }
        ],
        approved_images=[
            {
                "source_type": "search",
                "source_id": "search:0",
                "source_url": "https://example.com/messi.jpg",
            }
        ],
    )

    assert "https://example.com/messi.jpg" in xml
    assert final_call["arguments"]["image_url"] == "https://example.com/messi.jpg"
    assert history[0]["source"] == "search"


def test_execute_tool_plan_rejects_unapproved_image_layout():
    with pytest.raises(NoApprovedImageError, match="IMAGE_ASSIGNMENT_EMPTY"):
        execute_tool_plan(
            [
                {
                    "name": "generate_modern_cover_slide_xml",
                    "arguments": {"title": "No image yet"},
                }
            ]
        )


def test_tool_without_images_does_not_require_assets():
    final_call, history = inject_approved_images(
        {"name": "generate_text_slide", "arguments": {"title": "Summary"}},
        tool=FakeTool(NoImageSlideInput),
        approved_images=[],
        asset_dir=None,
    )

    assert final_call["name"] == "generate_text_slide"
    assert history == []


def test_ddgs_ranking_prefers_target_dimensions_and_layout():
    results = [
        {"image": "https://example.com/wide.jpg", "width": 1920, "height": 1080},
        {"image": "https://example.com/square.jpg", "width": 900, "height": 900},
        {"image": "https://example.com/portrait.jpg", "width": 960, "height": 1080},
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

    assert _parse_target_dimensions("Recommended image size: 960x1080px") == (960, 1080)
    assert ranked[0]["image"] == "https://example.com/portrait.jpg"
