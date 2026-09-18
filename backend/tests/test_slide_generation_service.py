import asyncio

from backend.application.services.slide_generation_service import SlideGenerationService
from backend.domain.entities.chat import ChatSession


class ScriptProvider:
    def __init__(self) -> None:
        self.calls = []

    def generate_completion(self, messages, **kwargs):
        self.calls.append((messages, kwargs))
        if len(self.calls) == 1:
            return "Preserve the user's explicit presentation requirements and apply them at the appropriate scope."
        if len(self.calls) == 2:
            return "# Deck\n\n## First\nContent\n\n## Second\nContent"
        return "# Deck\n\n## First\nContent\n\n## Second\nContent\n\n## Third\nContent"


class Workflow:
    def __init__(self) -> None:
        self.kwargs = None

    async def generate_from_chunks(self, **kwargs):
        self.kwargs = kwargs
        return "/tmp/slidegen-test-output"


class Projects:
    def __init__(self) -> None:
        self.kwargs = None

    def import_project_from_workflow(self, **kwargs):
        self.kwargs = kwargs
        return 42


def test_chat_generation_retries_script_until_selected_slide_count_matches():
    provider = ScriptProvider()
    workflow = Workflow()
    projects = Projects()
    service = SlideGenerationService(provider, workflow, projects)
    session = ChatSession(
        id="session-1",
        user_id=7,
        project_id=None,
        title=None,
        history_summary=None,
        max_turns=5,
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )

    result = asyncio.run(
        service.generate(
            session=session,
            prompt="Tạo bài giới thiệu",
            retrieved_context="",
            model_name="genius-3",
            effort="medium",
            target_slide_count=3,
        )
    )

    assert result.project_id == 42
    assert result.slide_count == 3
    assert len(provider.calls) == 3
    assert len(workflow.kwargs["slide_chunks"]) == 3
    assert workflow.kwargs["slide_options"]["target_slide_count"] == 3
    assert workflow.kwargs["slide_options"]["presentation_instruction"]
    assert "presentation" in provider.calls[0][0][0]["content"].lower()


def test_chat_generation_passes_llm_presentation_instruction_to_workflow():
    provider = ScriptProvider()
    workflow = Workflow()
    projects = Projects()
    service = SlideGenerationService(provider, workflow, projects)
    session = ChatSession(
        id="session-2",
        user_id=7,
        project_id=None,
        title=None,
        history_summary=None,
        max_turns=5,
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )

    asyncio.run(
        service.generate(
            session=session,
            prompt="Tạo slide với cách trình bày trực quan phù hợp với nội dung",
            retrieved_context="",
            model_name="genius-3",
            effort="medium",
            target_slide_count=3,
        )
    )

    instruction = workflow.kwargs["slide_options"]["presentation_instruction"]
    assert instruction
    assert len(provider.calls) == 3
