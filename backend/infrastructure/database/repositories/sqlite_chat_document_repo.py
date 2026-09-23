from __future__ import annotations

import json
from datetime import datetime, timezone

from backend.config import CHATBOT_DOCUMENTS_DIR
from backend.domain.entities.chat_document import ChatDocument, ChatDocumentChunk
from backend.domain.ports.chat_document_repository import ChatDocumentRepository
from backend.infrastructure.database.connection import get_db_connection

CHUNK_ORDINAL_GENERATION_BASE = 1_000_000


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _document_from_row(row) -> ChatDocument:
    try:
        structure = json.loads(row["structure_json"] or "[]")
    except (TypeError, ValueError):
        structure = []
    try:
        images = json.loads(row["images_json"] or "[]")
    except (TypeError, ValueError, KeyError):
        images = []
    size_bytes = int(row["size_bytes"] or 0)
    if size_bytes <= 0:
        # Backfill the effective size for documents created before the column
        # existed. New rows always persist the value explicitly.
        try:
            size_bytes = (CHATBOT_DOCUMENTS_DIR / f"{row['id']}.docx").stat().st_size
        except OSError:
            size_bytes = 0
    return ChatDocument(
        id=str(row["id"]),
        user_id=int(row["user_id"]),
        project_id=int(row["project_id"]) if row["project_id"] is not None else None,
        original_filename=str(row["original_filename"]),
        title=row["title"],
        status=str(row["status"]),
        content_hash=str(row["content_hash"]),
        markdown_path=row["markdown_path"],
        structure=structure if isinstance(structure, list) else [],
        error_message=row["error_message"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        chunk_index_version=int(row["chunk_index_version"] or 0),
        size_bytes=size_bytes,
        images=images if isinstance(images, list) else [],
    )


def _chunk_from_row(row) -> ChatDocumentChunk:
    try:
        embedding = json.loads(row["embedding_json"])
    except (TypeError, ValueError):
        embedding = []
    return ChatDocumentChunk(
        id=int(row["id"]),
        document_id=str(row["document_id"]),
        ordinal=int(row["ordinal"]),
        title=str(row["title"]),
        section_path=str(row["section_path"]),
        content=str(row["content"]),
        level=int(row["level"]),
        embedding=embedding if isinstance(embedding, list) else [],
        node_key=str(row["node_key"] or ""),
        parent_node_key=(
            str(row["parent_node_key"])
            if row["parent_node_key"] is not None
            else None
        ),
        node_kind=str(row["node_kind"] or "content"),
    )


def _insert_chunks(
    conn,
    document_id: str,
    chunks: list[dict],
    *,
    index_version: int,
) -> None:
    for chunk in chunks:
        ordinal = int(chunk["ordinal"])
        if ordinal < 0 or ordinal >= CHUNK_ORDINAL_GENERATION_BASE:
            raise ValueError("Document chunk ordinal exceeds the index limit")
        conn.execute(
            """
            INSERT INTO chatbot_document_chunks
                (document_id, ordinal, title, section_path, content,
                 level, node_key, parent_node_key, node_kind,
                 embedding_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                index_version * CHUNK_ORDINAL_GENERATION_BASE + ordinal,
                str(chunk["title"]),
                str(chunk["section_path"]),
                str(chunk["content"]),
                int(chunk.get("level", 1)),
                str(chunk.get("node_key") or ""),
                chunk.get("parent_node_key"),
                str(chunk.get("node_kind") or "content"),
                json.dumps(chunk["embedding"], ensure_ascii=False),
            ),
        )


class SqliteChatDocumentRepository(ChatDocumentRepository):
    """SQLite adapter for chatbot documents and their retrieval chunks."""

    def create_document(
        self,
        *,
        document_id: str,
        user_id: int,
        project_id: int | None,
        original_filename: str,
        content_hash: str,
        size_bytes: int = 0,
    ) -> ChatDocument:
        now = _now()
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO chatbot_documents
                    (id, user_id, project_id, original_filename, status,
                     content_hash, size_bytes, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'processing', ?, ?, ?, ?)
                """,
                (
                    document_id,
                    user_id,
                    project_id,
                    original_filename,
                    content_hash,
                    max(0, int(size_bytes)),
                    now,
                    now,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM chatbot_documents WHERE id = ? AND user_id = ?",
                (document_id, user_id),
            ).fetchone()
        return _document_from_row(row)

    def get_document(self, document_id: str, user_id: int) -> ChatDocument | None:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT * FROM chatbot_documents WHERE id = ? AND user_id = ?",
                (document_id, user_id),
            ).fetchone()
        return _document_from_row(row) if row else None

    def link_document_to_session(
        self, session_id: str, document_id: str, user_id: int
    ) -> None:
        now = _now()
        with get_db_connection() as conn:
            allowed = conn.execute(
                """
                SELECT d.id
                FROM chatbot_documents AS d
                JOIN chatbot_sessions AS s ON s.user_id = d.user_id
                WHERE d.id = ? AND d.user_id = ? AND s.id = ? AND s.user_id = ?
                """,
                (document_id, user_id, session_id, user_id),
            ).fetchone()
            if allowed is None:
                raise LookupError("Document or chat session not found")
            conn.execute(
                """
                INSERT OR IGNORE INTO chatbot_session_documents
                    (session_id, document_id, created_at)
                VALUES (?, ?, ?)
                """,
                (session_id, document_id, now),
            )
            conn.commit()

    def remove_document_from_session(
        self, session_id: str, document_id: str, user_id: int
    ) -> None:
        """Detach a document and remove its orphaned RAG data."""
        with get_db_connection() as conn:
            allowed = conn.execute(
                """
                SELECT d.id
                FROM chatbot_documents AS d
                JOIN chatbot_session_documents AS sd ON sd.document_id = d.id
                JOIN chatbot_sessions AS s ON s.id = sd.session_id
                WHERE sd.session_id = ? AND sd.document_id = ?
                  AND s.user_id = ? AND d.user_id = ?
                """,
                (session_id, document_id, user_id, user_id),
            ).fetchone()
            if allowed is None:
                raise LookupError("Document or chat session not found")

            conn.execute(
                """
                DELETE FROM chatbot_session_documents
                WHERE session_id = ? AND document_id = ?
                """,
                (session_id, document_id),
            )
            still_linked = conn.execute(
                """
                SELECT 1
                FROM chatbot_session_documents
                WHERE document_id = ?
                LIMIT 1
                """,
                (document_id,),
            ).fetchone()
            if still_linked is None:
                # Foreign keys are not enabled consistently by all legacy
                # database connections, so clean dependants explicitly.
                conn.execute(
                    "DELETE FROM chatbot_message_citations WHERE document_id = ?",
                    (document_id,),
                )
                conn.execute(
                    "DELETE FROM chatbot_document_chunks WHERE document_id = ?",
                    (document_id,),
                )
                conn.execute(
                    "DELETE FROM chatbot_documents WHERE id = ? AND user_id = ?",
                    (document_id, user_id),
                )
            conn.commit()

    def list_session_documents(
        self, session_id: str, user_id: int
    ) -> list[ChatDocument]:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT d.*
                FROM chatbot_documents AS d
                JOIN chatbot_session_documents AS sd ON sd.document_id = d.id
                JOIN chatbot_sessions AS s ON s.id = sd.session_id
                WHERE sd.session_id = ? AND s.user_id = ? AND d.user_id = ?
                ORDER BY sd.created_at ASC
                """,
                (session_id, user_id, user_id),
            ).fetchall()
        return [_document_from_row(row) for row in rows]

    def set_document_ready(
        self,
        document_id: str,
        user_id: int,
        *,
        title: str,
        markdown_path: str,
        structure: list[dict],
        chunks: list[dict],
        images: list[dict] | None = None,
    ) -> ChatDocument:
        now = _now()
        structure_json = json.dumps(structure, ensure_ascii=False)
        with get_db_connection() as conn:
            owner = conn.execute(
                """
                SELECT id, COALESCE(chunk_index_version, 0) AS chunk_index_version
                FROM chatbot_documents
                WHERE id = ? AND user_id = ?
                """,
                (document_id, user_id),
            ).fetchone()
            if owner is None:
                raise LookupError("Document not found")

            index_version = int(owner["chunk_index_version"] or 0) + 1
            _insert_chunks(
                conn,
                document_id,
                chunks,
                index_version=index_version,
            )
            conn.execute(
                """
                UPDATE chatbot_documents
                SET title = ?, status = 'ready', markdown_path = ?,
                    structure_json = ?, images_json = ?, error_message = NULL,
                    chunk_index_version = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (
                    title,
                    markdown_path,
                    structure_json,
                    json.dumps(images or [], ensure_ascii=False),
                    index_version,
                    now,
                    document_id,
                    user_id,
                ),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM chatbot_documents WHERE id = ? AND user_id = ?",
                (document_id, user_id),
            ).fetchone()
        return _document_from_row(row)

    def replace_document_chunks(
        self,
        document_id: str,
        user_id: int,
        *,
        chunks: list[dict],
    ) -> None:
        """Activate a new derived index generation without changing the source.

        Previous generations remain addressable by historical citation rows;
        ``list_session_chunks`` exposes only the newly activated generation.
        """
        if not chunks:
            raise ValueError("Cannot replace a document index with no chunks")

        with get_db_connection() as conn:
            owner = conn.execute(
                """
                SELECT id, COALESCE(chunk_index_version, 0) AS chunk_index_version
                FROM chatbot_documents
                WHERE id = ? AND user_id = ? AND status = 'ready'
                """,
                (document_id, user_id),
            ).fetchone()
            if owner is None:
                raise LookupError("Document not found")

            index_version = int(owner["chunk_index_version"] or 0) + 1
            _insert_chunks(
                conn,
                document_id,
                chunks,
                index_version=index_version,
            )
            conn.execute(
                """
                UPDATE chatbot_documents
                SET chunk_index_version = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (index_version, _now(), document_id, user_id),
            )
            conn.commit()

    def set_document_failed(
        self, document_id: str, user_id: int, error_message: str
    ) -> ChatDocument | None:
        with get_db_connection() as conn:
            conn.execute(
                """
                UPDATE chatbot_documents
                SET status = 'failed', error_message = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (error_message[:2000], _now(), document_id, user_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM chatbot_documents WHERE id = ? AND user_id = ?",
                (document_id, user_id),
            ).fetchone()
        return _document_from_row(row) if row else None

    def list_session_chunks(
        self, session_id: str, user_id: int
    ) -> list[ChatDocumentChunk]:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT c.*
                FROM chatbot_document_chunks AS c
                JOIN chatbot_session_documents AS sd ON sd.document_id = c.document_id
                JOIN chatbot_sessions AS s ON s.id = sd.session_id
                JOIN chatbot_documents AS d ON d.id = c.document_id
                WHERE sd.session_id = ? AND s.user_id = ?
                  AND d.user_id = ? AND d.status = 'ready'
                  AND c.ordinal >= d.chunk_index_version * ?
                  AND c.ordinal < (d.chunk_index_version + 1) * ?
                ORDER BY c.document_id, c.ordinal
                """,
                (
                    session_id,
                    user_id,
                    user_id,
                    CHUNK_ORDINAL_GENERATION_BASE,
                    CHUNK_ORDINAL_GENERATION_BASE,
                ),
            ).fetchall()
        return [_chunk_from_row(row) for row in rows]
