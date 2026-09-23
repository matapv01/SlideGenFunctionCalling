import asyncio

from backend.application.services.slide_intent_service import SlideIntentService
from backend.application.services.language_service import detect_language
from backend.domain.entities.chat import ChatMessage


class DummyLLMProvider:
    def __init__(self, response="{}"):
        self.response = response

    def generate_completion(self, messages, **kwargs):
        return self.response


def test_clarification_options_always_end_with_custom_option():
    service = SlideIntentService(DummyLLMProvider())

    decision = service._normalise_decision(
        {
            "type": "clarification",
            "question": "Bạn muốn bộ slide theo hướng nào?",
            "options": [
                {"label": "Ra mắt", "value": "Ra mắt sản phẩm"},
                {"label": "Phân tích", "value": "Phân tích vấn đề"},
                {"label": "Khác", "value": "custom"},
            ],
            "brief": "Một bộ slide giới thiệu sản phẩm",
        },
        current_brief="Một bộ slide giới thiệu sản phẩm",
        fallback=service._fallback_clarification("", "vi"),
        language="vi",
    )

    assert decision.state == "clarifying"
    assert len(decision.options) == 3
    assert decision.options[-1].label == "Khác"
    assert decision.options[-1].is_other is True


def test_invalid_clarification_fails_closed_without_biased_options():
    service = SlideIntentService(DummyLLMProvider())

    decision = service._normalise_decision(
        {
            "type": "clarification",
            "question": "Bạn muốn gì?",
            "options": ["Chỉ một option"],
        },
        current_brief="Tạo slide",
        fallback=service._fallback_clarification("Tạo slide", "vi"),
        language="vi",
    )

    assert decision.state == "clarifying"
    assert decision.options == ()


def test_llm_router_uses_conversation_meaning_instead_of_phrase_rules():
    history = [
        ChatMessage(
            id=1,
            session_id="session-1",
            role="user",
            content="Mình muốn làm một bài thuyết trình về Messi",
            standalone_query=None,
            model=None,
            effort=None,
            metadata={},
            created_at="2026-01-01T00:00:00",
        ),
    ]

    slide_service = SlideIntentService(
        DummyLLMProvider('{"intent":"slide_creation","reason":"The user is continuing the deck request."}')
    )
    chat_service = SlideIntentService(
        DummyLLMProvider('{"intent":"chat","reason":"The user is asking a general question."}')
    )
    config = {"provider_model": "test-model", "max_tokens": 4096, "temperature": 0.4, "top_p": 1.0}

    assert asyncio.run(slide_service.classify("Tạo đi", history, config)).intent == "slide_creation"
    assert asyncio.run(chat_service.classify("Bạn khỏe không?", history, config)).intent == "chat"


def test_vietnamese_detection_handles_tones_and_unaccented_input():
    assert detect_language("gen slide về bác Hồ") == "vi"
    assert detect_language("tao slide ve bac Ho") == "vi"
    assert detect_language("generate a deck about history") == "en"


def test_slide_planner_rejects_wrong_language_user_facing_output():
    service = SlideIntentService(DummyLLMProvider())
    fallback = service._fallback_clarification("gen slide về bác Hồ", "vi")

    decision = service._normalise_decision(
        {
            "type": "clarification",
            "question": "What should the deck focus on?",
            "options": ["Launch", "Analysis", "Training"],
        },
        current_brief="gen slide về bác Hồ",
        fallback=fallback,
        language="vi",
    )

    assert decision.message == fallback.message
    assert decision.options == ()


def test_slide_planner_does_not_replace_a_vietnamese_brief_with_english():
    service = SlideIntentService(DummyLLMProvider())
    current_brief = "gen slide về bác Hồ"

    decision = service._normalise_decision(
        {
            "type": "confirmation",
            "message": "I have enough direction now. Shall I start creating the slides?",
            "brief": "A presentation about Ho Chi Minh",
        },
        current_brief=current_brief,
        fallback=service._fallback_confirmation(current_brief, [], "vi"),
        language="vi",
        target_slide_count=10,
        max_slide_count=50,
    )

    assert decision.brief == current_brief
    assert decision.message == "Mình đã đủ thông tin. Bắt đầu tạo slide nhé?"


def test_slide_planner_returns_llm_confirmation_as_generation_action():
    service = SlideIntentService(DummyLLMProvider())
    decision = service._normalise_decision(
        {
            "type": "start",
            "action": "start_generation",
            "brief": "Tạo bộ slide về Messi",
        },
        current_brief="Tạo bộ slide về Messi",
        fallback=service._fallback_confirmation("Tạo bộ slide về Messi", [], "vi"),
        language="vi",
        target_slide_count=6,
        max_slide_count=50,
    )

    assert decision.start_generation is True
    assert decision.options == ()


def test_slide_flow_always_asks_for_count_before_llm_preflight():
    service = SlideIntentService(DummyLLMProvider())

    decision = asyncio.run(
        service.start(
            "gen slide về bác Hồ",
            [],
            {
                "provider_model": "qwen",
                "max_tokens": 2048,
                "temperature": 0.4,
                "top_p": 1.0,
            },
            max_slide_count=50,
        )
    )

    assert decision.state == "clarifying"
    assert decision.question_kind == "slide_count"
    assert decision.target_slide_count is None
    assert len(decision.options) == 4
    assert decision.options[-1].action == "other"


def test_slide_flow_with_count_reaches_llm_preflight():
    service = SlideIntentService(
        DummyLLMProvider(
            '{"type":"confirmation","message":"Mình đã đủ thông tin. '
            'Bắt đầu tạo slide nhé?","brief":"Một bộ slide về AI"}'
        )
    )

    decision = asyncio.run(
        service.start(
            "Tạo slide về AI",
            [],
            {
                "provider_model": "qwen",
                "max_tokens": 2048,
                "temperature": 0.4,
                "top_p": 1.0,
            },
            max_slide_count=50,
            requested_slide_count=6,
        )
    )

    assert decision.state == "awaiting_confirmation"
    assert decision.target_slide_count == 6


def test_slide_flow_returns_upgrade_choice_when_count_exceeds_plan():
    service = SlideIntentService(DummyLLMProvider())

    decision = asyncio.run(
        service.start(
            "gen slide về bác Hồ 60 slide",
            [],
            {
                "provider_model": "qwen",
                "max_tokens": 2048,
                "temperature": 0.4,
                "top_p": 1.0,
            },
            max_slide_count=50,
        )
    )

    assert decision.state == "limit_reached"
    assert decision.question_kind == "slide_count"
    assert decision.options[-1].action == "upgrade"


def test_attached_document_question_is_not_rewritten_by_a_phrase_rule():
    service = SlideIntentService(DummyLLMProvider())
    fallback = service._fallback_confirmation(
        "gen slide theo tài liệu",
        [],
        "vi",
        target_slide_count=6,
        max_slide_count=50,
    )

    decision = service._normalise_decision(
        {
            "type": "clarification",
            "question": "Bạn muốn nội dung slide dựa trên tài liệu nào?",
            "options": [
                {"label": "Tải lên file tài liệu", "value": "upload"},
                {"label": "Dán nội dung văn bản", "value": "paste"},
                {"label": "Tóm tắt theo chủ đề", "value": "summary"},
            ],
            "brief": "gen slide theo tài liệu",
        },
        current_brief="gen slide theo tài liệu",
        fallback=fallback,
        language="vi",
        target_slide_count=6,
        max_slide_count=50,
        document_attached=True,
    )

    assert decision.state == "clarifying"
    assert decision.message == "Bạn muốn nội dung slide dựa trên tài liệu nào?"
