from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatSession:
    id: str
    user_id: int
    project_id: int | None
    title: str | None
    history_summary: str | None
    max_turns: int
    created_at: str
    updated_at: str
    archived: bool = False


@dataclass(frozen=True)
class ChatMessage:
    id: int
    session_id: str
    role: str
    content: str
    standalone_query: str | None
    model: str | None
    effort: str | None
    metadata: dict
    created_at: str
