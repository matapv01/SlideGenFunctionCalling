from backend.workflows.slidegen_workflow.nodes.slide_planner import (
    _normalize_image_mode,
    _normalize_image_strategy,
    _normalize_plan_action,
    build_compact_slide_outline,
    normalize_image_sequence,
)
from backend.workflows.slidegen_workflow.nodes.slide_generator import (
    _build_decorative_image_query,
)


def test_compact_outline_contains_all_slide_contexts_without_raw_content():
    chunks = [
        {"heading": "Opening", "body": "private raw content"},
        {"heading": "Results", "body": "more private raw content"},
    ]
    contexts = ["[Slide 1] INTRO SLIDE", "[Slide 2] Results"]

    outline = build_compact_slide_outline(chunks, contexts)

    assert "[Slide 1] INTRO SLIDE" in outline
    assert "[Slide 2] Results" in outline
    assert "private raw content" not in outline


def test_planner_action_is_normalized_to_document_markers():
    assert _normalize_plan_action({}, {"heading": "INTRO"}, 0) == "INTRO_TOOLS"
    assert _normalize_plan_action({"action": "INTRO_TOOLS"}, {"heading": "Results"}, 1) == "CONTENT_TOOLS"
    assert _normalize_plan_action({"action": "CONTENT_TOOLS"}, {"slide_type": "transition"}, 2) == "TRANSITION_TOOLS"
    assert _normalize_plan_action({"action": "not_a_category"}, {"heading": "Results"}, 1) == "CONTENT_TOOLS"


def test_identity_slides_use_decorative_image_strategy():
    assert _normalize_image_mode({"image_mode": "none"}) == "none"
    assert _normalize_image_mode({"image_strategy": "semantic"}) == "semantic"

    assert _normalize_image_strategy(
        {"action": "TEAM_TOOLS", "image_strategy": "semantic"},
        {"heading": "Team"},
        2,
    ) == "decorative"

    query = _build_decorative_image_query(
        {"description": "portrait image"},
        "TEAM_TOOLS",
        "team brainstorming",
    )
    assert "John Smith" not in query
    assert "team" in query
    assert "illustration" in query
    assert "brainstorming" in query

    generic_query = _build_decorative_image_query(
        {"description": "supporting illustration"},
        "CONTENT_TOOLS",
        "workflow collaboration",
    )
    assert "John Smith" not in generic_query
    assert generic_query == "workflow collaboration conceptual illustration"


def test_content_image_policy_defaults_to_none_and_spaces_decorative_images():
    assert _normalize_image_mode({"action": "CONTENT_TOOLS"}) == "none"
    assert _normalize_image_mode({"action": "INTRO_TOOLS"}) == "decorative"

    plans = [
        {
            "action": "CONTENT_TOOLS",
            "image_mode": "semantic",
            "image_theme": "factory robotics",
        },
        {
            "action": "CONTENT_TOOLS",
            "image_mode": "decorative",
            "image_theme": "workflow collaboration",
        },
        {
            "action": "CONTENT_TOOLS",
            "image_mode": "decorative",
            "image_theme": "customer support",
        },
    ]

    normalize_image_sequence(plans)

    assert [plan["image_mode"] for plan in plans] == ["semantic", "none", "decorative"]
