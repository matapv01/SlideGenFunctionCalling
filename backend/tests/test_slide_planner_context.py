from backend.workflows.slidegen_workflow.nodes.slide_planner import (
    _normalize_image_strategy,
    _normalize_plan_action,
    build_compact_slide_outline,
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
    assert _normalize_image_strategy(
        {"action": "TEAM_TOOLS", "image_strategy": "semantic"},
        {"heading": "Team"},
        2,
    ) == "decorative"

    query = _build_decorative_image_query(
        {"description": "portrait image"},
        "TEAM_TOOLS",
    )
    assert "John Smith" not in query
    assert "team" in query
    assert "illustration" in query

    generic_query = _build_decorative_image_query(
        {"description": "supporting illustration"},
        "CONTENT_TOOLS",
    )
    assert "John Smith" not in generic_query
    assert generic_query == "conceptual editorial illustration presentation"
