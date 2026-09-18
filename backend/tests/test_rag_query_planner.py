import asyncio

from backend.application.services.rag_query_planner import RagQueryPlanner


GENERATION_CONFIG = {
    "provider_model": "test-model",
    "max_tokens": 4096,
    "temperature": 0.6,
    "top_p": 1.0,
}


class PlanningLLM:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0

    def generate_completion(self, messages, **kwargs):
        self.calls += 1
        return self.response


def test_planner_rewrites_document_request_into_search_queries():
    llm = PlanningLLM(
        '{"needs_rag": true, "queries": ["các luận điểm chính", '
        '"số liệu doanh thu theo năm"], "reason": "Cần dữ kiện trong file"}'
    )

    plan = asyncio.run(
        RagQueryPlanner(llm).plan(
            "Tạo deck từ tài liệu này",
            [],
            GENERATION_CONFIG,
            document_attached=True,
            slide_request=True,
            brief="Deck tổng hợp nội dung và số liệu trong tài liệu",
        )
    )

    assert plan.needs_rag is True
    assert plan.queries == ("các luận điểm chính", "số liệu doanh thu theo năm")
    assert plan.source == "llm"
    assert plan.mode == "deck_from_document"
    assert plan.include_root is True
    assert llm.calls == 1


def test_planner_can_skip_rag_for_casual_chat_with_document_attached():
    llm = PlanningLLM(
        '{"needs_rag": false, "queries": [], "reason": "Chỉ là lời chào"}'
    )

    plan = asyncio.run(
        RagQueryPlanner(llm).plan(
            "Xin chào",
            [],
            GENERATION_CONFIG,
            document_attached=True,
        )
    )

    assert plan.needs_rag is False
    assert plan.queries == ()


def test_planner_never_calls_llm_without_a_ready_document():
    llm = PlanningLLM("this should not be used")

    plan = asyncio.run(
        RagQueryPlanner(llm).plan(
            "Tóm tắt tài liệu",
            [],
            GENERATION_CONFIG,
            document_attached=False,
        )
    )

    assert plan.needs_rag is False
    assert plan.queries == ()
    assert plan.source == "none"
    assert llm.calls == 0


def test_planner_falls_back_to_a_safe_query_when_llm_output_is_invalid():
    llm = PlanningLLM("not valid json")

    plan = asyncio.run(
        RagQueryPlanner(llm).plan(
            "Phân tích tài liệu đã tải lên",
            [],
            GENERATION_CONFIG,
            document_attached=True,
        )
    )

    assert plan.needs_rag is True
    assert plan.queries == ("Phân tích tài liệu đã tải lên",)
    assert plan.source == "fallback"


def test_planner_preserves_overview_mode_and_tree_expansion_policy():
    llm = PlanningLLM(
        '{"needs_rag": true, "mode": "document_overview", '
        '"source_policy": "document_only", "queries": ["tài liệu nói về gì"], '
        '"include_root": true, "include_ancestors": false, '
        '"include_siblings": false, "max_detail_nodes": 0, '
        '"reason": "Cần xem outline tài liệu"}'
    )

    plan = asyncio.run(
        RagQueryPlanner(llm).plan(
            "Tài liệu này nói về gì?",
            [],
            GENERATION_CONFIG,
            document_attached=True,
        )
    )

    assert plan.mode == "document_overview"
    assert plan.source_policy == "document_only"
    assert plan.include_root is True
    assert plan.include_ancestors is False
    assert plan.max_detail_nodes == 0
