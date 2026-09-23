from __future__ import annotations

from typing import Protocol

from backend.domain.entities.chat import ChatMessage, ChatSession


class ChatRepository(Protocol):
    def create_session(
        self,
        user_id: int,
        *,
        project_id: int | None = None,
        title: str | None = None,
        max_turns: int = 5,
    ) -> ChatSession: ...

    def get_session(self, session_id: str, user_id: int) -> ChatSession | None: ...

    def list_sessions(self, user_id: int, *, include_archived: bool = False) -> list[ChatSession]: ...

    def list_messages(
        self, session_id: str, user_id: int, *, limit: int = 1000
    ) -> list[ChatMessage]: ...

    def append_turn(
        self,
        session_id: str,
        user_id: int,
        *,
        query: str,
        standalone_query: str,
        answer: str,
        model: str,
        effort: str,
        project_id: int | None = None,
        metadata: dict | None = None,
        citations: list[dict] | None = None,
    ) -> tuple[ChatMessage, ChatMessage]: ...

    def update_history_summary(
        self, session_id: str, user_id: int, summary: str
    ) -> None: ...

    def archive_session(self, session_id: str, user_id: int) -> None: ...
