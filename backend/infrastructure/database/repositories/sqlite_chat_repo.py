from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from backend.domain.entities.chat import ChatMessage, ChatSession
from backend.domain.ports.chat_repository import ChatRepository
from backend.infrastructure.database.connection import get_db_connection


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_from_row(row) -> ChatSession:
    return ChatSession(
        id=str(row["id"]),
        user_id=int(row["user_id"]),
        project_id=int(row["project_id"]) if row["project_id"] is not None else None,
        title=row["title"],
        history_summary=row["history_summary"],
        max_turns=int(row["max_turns"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        archived=bool(row["archived"]),
    )


def _message_from_row(row) -> ChatMessage:
    try:
        metadata = json.loads(row["metadata_json"] or "{}")
    except (TypeError, ValueError):
        metadata = {}
    return ChatMessage(
        id=int(row["id"]),
        session_id=str(row["session_id"]),
        role=str(row["role"]),
        content=str(row["content"]),
        standalone_query=row["standalone_query"],
        model=row["model"],
        effort=row["effort"],
        metadata=metadata if isinstance(metadata, dict) else {},
        created_at=str(row["created_at"]),
    )


class SqliteChatRepository(ChatRepository):
    """SQLite adapter for chat sessions and short-term conversation memory."""

    def create_session(
        self,
        user_id: int,
        *,
        project_id: int | None = None,
        title: str | None = None,
        max_turns: int = 5,
    ) -> ChatSession:
        session_id = str(uuid.uuid4())
        now = _now()
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO chatbot_sessions
                    (id, user_id, project_id, title, max_turns, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, user_id, project_id, title, max(1, max_turns), now, now),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM chatbot_sessions WHERE id = ?", (session_id,)
            ).fetchone()
        return _session_from_row(row)

    def get_session(self, session_id: str, user_id: int) -> ChatSession | None:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT * FROM chatbot_sessions WHERE id = ? AND user_id = ?",
                (session_id, user_id),
            ).fetchone()
        return _session_from_row(row) if row else None

    def list_sessions(
        self, user_id: int, *, include_archived: bool = False
    ) -> list[ChatSession]:
        query = (
            "SELECT s.* FROM chatbot_sessions AS s "
            "WHERE s.user_id = ? "
            "AND EXISTS ("
            "SELECT 1 FROM chatbot_messages AS m WHERE m.session_id = s.id"
            ")"
        )
        params: list[object] = [user_id]
        if not include_archived:
            query += " AND s.archived = 0"
        query += " ORDER BY s.updated_at DESC"
        with get_db_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [_session_from_row(row) for row in rows]

    def list_messages(
        self, session_id: str, user_id: int, *, limit: int = 1000
    ) -> list[ChatMessage]:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT m.*
                FROM chatbot_messages AS m
                JOIN chatbot_sessions AS s ON s.id = m.session_id
                WHERE m.session_id = ? AND s.user_id = ?
                ORDER BY m.id DESC
                LIMIT ?
                """,
                (session_id, user_id, max(1, limit)),
            ).fetchall()
        return [_message_from_row(row) for row in reversed(rows)]

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
    ) -> tuple[ChatMessage, ChatMessage]:
        now = _now()
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
        with get_db_connection() as conn:
            session = conn.execute(
                "SELECT id FROM chatbot_sessions WHERE id = ? AND user_id = ?",
                (session_id, user_id),
            ).fetchone()
            if session is None:
                raise LookupError("Chat session not found")

            user_cursor = conn.execute(
                """
                INSERT INTO chatbot_messages
                    (session_id, role, content, standalone_query, model, effort,
                     metadata_json, created_at)
                VALUES (?, 'user', ?, ?, ?, ?, ?, ?)
                """,
                (session_id, query, standalone_query, model, effort, metadata_json, now),
            )
            assistant_cursor = conn.execute(
                """
                INSERT INTO chatbot_messages
                    (session_id, role, content, standalone_query, model, effort,
                     metadata_json, created_at)
                VALUES (?, 'assistant', ?, ?, ?, ?, ?, ?)
                """,
                (session_id, answer, standalone_query, model, effort, metadata_json, now),
            )
            for order, citation in enumerate(citations or []):
                try:
                    chunk_id = int(citation["chunk_id"])
                    document_id = str(citation["document_id"])
                    similarity = float(citation.get("similarity", 0.0))
                except (KeyError, TypeError, ValueError):
                    continue
                conn.execute(
                    """
                    INSERT INTO chatbot_message_citations
                        (message_id, document_id, chunk_id, similarity, citation_order)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        assistant_cursor.lastrowid,
                        document_id,
                        chunk_id,
                        similarity,
                        order,
                    ),
                )
            conn.execute(
                """
                UPDATE chatbot_sessions
                SET title = COALESCE(NULLIF(title, ''), substr(?, 1, 80)),
                    project_id = COALESCE(?, project_id),
                    updated_at = ?
                WHERE id = ?
                """,
                (query, project_id, now, session_id),
            )
            conn.commit()
            user_row = conn.execute(
                "SELECT * FROM chatbot_messages WHERE id = ?", (user_cursor.lastrowid,)
            ).fetchone()
            assistant_row = conn.execute(
                "SELECT * FROM chatbot_messages WHERE id = ?",
                (assistant_cursor.lastrowid,),
            ).fetchone()
        return _message_from_row(user_row), _message_from_row(assistant_row)

    def update_history_summary(
        self, session_id: str, user_id: int, summary: str
    ) -> None:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE chatbot_sessions
                SET history_summary = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (summary, _now(), session_id, user_id),
            )
            if cursor.rowcount == 0:
                raise LookupError("Chat session not found")
            conn.commit()

    def archive_session(self, session_id: str, user_id: int) -> None:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE chatbot_sessions
                SET archived = 1, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (_now(), session_id, user_id),
            )
            if cursor.rowcount == 0:
                raise LookupError("Chat session not found")
            conn.commit()
