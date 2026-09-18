import asyncio
from pathlib import Path
from types import SimpleNamespace
from threading import Lock

import pytest

from backend.application.services.chatbot_service import (
    ChatbotService,
    SlideGenerationInProgressError,
)
from backend.application.services.project_service import ProjectService
from backend.domain.entities.chat import ChatMessage, ChatSession


class ChatRepository:
    def __init__(self) -> None:
        self.session = ChatSession(
            id="session-1",
            user_id=7,
            project_id=None,
            title=None,
            history_summary=None,
            max_turns=5,
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
        )
        self.messages: list[ChatMessage] = []

    def get_session(self, session_id: str, user_id: int):
        return self.session if session_id == self.session.id and user_id == self.session.user_id else None

    def list_messages(self, session_id: str, user_id: int, *, limit: int = 1000):
        return list(self.messages)

    def append_turn(self, session_id: str, user_id: int, **kwargs):
        user_message = ChatMessage(
            id=1,
            session_id=session_id,
            role="user",
            content=kwargs["query"],
            standalone_query=kwargs["standalone_query"],
            model=kwargs["model"],
            effort=kwargs["effort"],
            metadata=kwargs.get("metadata") or {},
            created_at="2026-01-01T00:00:00",
        )
        assistant_message = ChatMessage(
            id=2,
            session_id=session_id,
            role="assistant",
            content=kwargs["answer"],
            standalone_query=kwargs["standalone_query"],
            model=kwargs["model"],
            effort=kwargs["effort"],
            metadata=kwargs.get("metadata") or {},
            created_at="2026-01-01T00:00:00",
        )
        self.messages.extend([user_message, assistant_message])
        return user_message, assistant_message


class ChatLLM:
    def generate_completion(self, messages, **kwargs):
        return "Đây là câu trả lời bình thường."


def _service_with_active_generation() -> ChatbotService:
    service = ChatbotService(ChatRepository(), ChatLLM())
    service._active_slide_generations = {7: "session-1"}
    service._active_slide_generations_lock = Lock()
    return service


def test_normal_chat_remains_available_during_slide_generation():
    service = _service_with_active_generation()

    result = asyncio.run(
        service.send_message("session-1", 7, "Giải thích ngắn gọn về chủ đề này")
    )

    assert result.assistant_message.content == "Đây là câu trả lời bình thường."


def test_second_explicit_slide_stream_is_rejected_during_generation():
    service = _service_with_active_generation()

    with pytest.raises(SlideGenerationInProgressError):
        asyncio.run(
            service.send_message(
                "session-1",
                7,
                "Tạo một deck khác",
                slide_callback=lambda *_: None,
            )
        )


def test_detached_slide_job_keeps_progress_after_subscriber_disconnects():
    async def scenario():
        service = ChatbotService(ChatRepository(), ChatLLM())

        async def fake_send_message(*args, **kwargs):
            callback = kwargs["slide_callback"]
            callback(
                "slide_completed",
                {"index": 0, "title": "First slide", "xml_path": "/tmp/slide.xml", "current": 1, "total": 3},
            )
            await asyncio.sleep(0)
            return SimpleNamespace(
                project_id=42,
                assistant_message=SimpleNamespace(
                    metadata={"slide_generation": {"project_name": "Test deck", "slide_count": 3}}
                ),
            )

        service.send_message = fake_send_message
        job = service.start_slide_generation(
            "session-1",
            7,
            "Bắt đầu tạo slide",
            model_name="genius-3",
            effort="medium",
            slide_count=3,
        )
        _, events = service.subscribe_slide_generation(job.id, 7)
        service.unsubscribe_slide_generation(job, events)
        await asyncio.wait_for(job.task, timeout=1)

        snapshot = service._slide_generation_snapshot(job)
        assert snapshot["phase"] == "completed"
        assert snapshot["project_id"] == 42
        assert snapshot["slides"][0]["title"] == "First slide"
        assert any(event[1] == "complete" for event in job.events)

    asyncio.run(scenario())


class ProjectRepository:
    def __init__(self) -> None:
        self.slides = []
        self.project_updates = []

    def create_project(self, **kwargs):
        return 42

    def save_metadata(self, **kwargs):
        return None

    def create_slide(self, slide):
        self.slides.append(slide)
        return len(self.slides)

    def update_project(self, **kwargs):
        self.project_updates.append(kwargs)


def test_project_import_normalizes_string_output_folder(tmp_path: Path):
    xml_folder = tmp_path / "output" / "xml"
    xml_folder.mkdir(parents=True)
    (xml_folder / "slide_1.xml").write_text("<slide />", encoding="utf-8")

    repository = ProjectRepository()
    project_id = ProjectService(repository).import_project_from_workflow(
        user_id=7,
        project_name="Test deck",
        source_type="chatbot",
        source_data={},
        slide_options={"output_format": "xml"},
        output_folder=str(tmp_path),
    )

    assert project_id == 42
    assert len(repository.slides) == 1
    assert repository.project_updates[-1]["status"] == "completed"
