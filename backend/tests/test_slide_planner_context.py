from backend.workflows.slidegen_workflow.nodes.slide_planner import (
    _normalize_image_mode,
    _normalize_plan_action,
    build_compact_slide_outline,
    normalize_planner_result,
    normalize_image_sequence,
    prepare_planner_context,
)
from backend.workflows.slidegen_workflow.nodes.slide_generator import (
    _resolve_image_mode,
)


class _PlannerLLM:
    def with_structured_output(self, _schema):
        return lambda value: value


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


def test_deck_instruction_is_shared_by_every_planner_input():
    instruction = "Apply a coherent visual direction to all relevant content slides."
    result = prepare_planner_context(
        {
            "slide_chunks": [
                {"heading": "Opening", "slide_type": "intro"},
                {"heading": "Results", "slide_type": "content"},
                {"heading": "Conclusion", "slide_type": "content"},
            ],
            "slide_options": {"presentation_instruction": instruction},
        },
        {"configurable": {"planner_llm": _PlannerLLM()}},
    )

    assert result["presentation_instruction"] == instruction
    assert [item["presentation_instruction"] for item in result["all_inputs"]] == [
        instruction,
        instruction,
        instruction,
    ]


def test_image_mode_requires_an_explicit_current_mode():
    assert _normalize_image_mode({"image_mode": "none"}) == "none"
    assert _normalize_image_mode({"image_mode": "semantic"}) == "semantic"

    assert _resolve_image_mode({"action": "TEAM_TOOLS", "image_mode": "none"}) == "none"
    assert _resolve_image_mode({"action": "CONTENT_TOOLS", "image_mode": "semantic"}) == "semantic"


def test_content_image_policy_uses_only_explicit_search_intents():
    assert _normalize_image_mode({"action": "CONTENT_TOOLS"}) == "none"

    plans = [
        {
            "action": "CONTENT_TOOLS",
            "image_mode": "semantic",
            "image_search_intents": [{"query": "factory robotics"}],
        },
        {
            "action": "CONTENT_TOOLS",
            "image_mode": "semantic",
            "image_search_intents": [],
        },
        {
            "action": "CONTENT_TOOLS",
            "image_mode": "none",
            "image_search_intents": [],
        },
    ]

    normalize_image_sequence(plans)

    assert [plan["image_mode"] for plan in plans] == ["semantic", "none", "none"]


def test_planner_normalizes_slide_purpose_for_image_context():
    plan = normalize_planner_result(
        {
            "slide_topic": "Hành trình ra đi",
            "slide_purpose": "Mở đầu hành trình Nguyễn Ái Quốc ra đi tìm đường cứu nước năm 1911.",
            "thought": "Use a strong historical opening composition.",
            "image_mode": "semantic",
            "image_search_intents": [],
            "action": "INTRO_TOOLS",
        },
        {"heading": "Hành trình ra đi"},
        0,
    )

    assert plan["slide_purpose"].startswith("Mở đầu hành trình Nguyễn Ái Quốc")
