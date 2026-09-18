import asyncio

from backend.application.services.slide_intent_service import SlideIntentService
from backend.application.services.chatbot_service import ChatbotService
from backend.application.services.language_service import detect_language


class DummyLLMProvider:
    def generate_completion(self, messages, **kwargs):
        return "{}"


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


def test_invalid_clarification_falls_back_to_four_options():
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
    assert len(decision.options) == 4
    assert decision.options[-1].is_other is True


def test_confirmation_requires_an_explicit_confirmation_phrase():
    assert ChatbotService._is_slide_confirmation("Bắt đầu tạo slide") is True
    assert ChatbotService._is_slide_confirmation("Xác nhận") is True
    assert ChatbotService._is_slide_confirmation("Tôi muốn bổ sung") is False
    assert ChatbotService._is_slide_confirmation("Không, để tôi sửa thêm") is False


def test_common_gen_slide_wording_enters_slide_flow():
    assert ChatbotService._looks_like_slide_request("gen slide về bác Hồ") is True
    assert ChatbotService._looks_like_slide_request("generate a deck about history") is True


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
    assert decision.options[-1].label == "Khác"


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


def test_attached_document_cannot_trigger_a_second_source_question():
    service = SlideIntentService(DummyLLMProvider())
    assert service.is_document_source_flow(
        {
            "question": "Bạn muốn nội dung slide dựa trên tài liệu nào?",
            "options": [
                {"label": "Tải lên file tài liệu", "value": "upload"},
                {"label": "Dán nội dung văn bản", "value": "paste"},
            ],
        }
    ) is True
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

    assert decision.state == "awaiting_confirmation"
    assert decision.message == fallback.message
    assert decision.options[0].label == "Bắt đầu tạo slide"
