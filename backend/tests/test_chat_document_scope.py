from __future__ import annotations

from backend.infrastructure.database import connection
from backend.infrastructure.database.repositories.sqlite_chat_document_repo import (
    SqliteChatDocumentRepository,
)
from backend.infrastructure.database.repositories.sqlite_chat_repo import (
    SqliteChatRepository,
)


def _insert_user(email: str) -> int:
    with connection.get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (email, hashed_password)
            VALUES (?, ?)
            """,
            (email, "test-password-hash"),
        )
        conn.commit()
        return int(cursor.lastrowid)


def test_chat_documents_are_scoped_to_their_session_and_owner(tmp_path, monkeypatch):
    monkeypatch.setattr(
        connection,
        "DATABASE_PATH",
        str(tmp_path / "chat-document-scope.db"),
    )
    connection.init_db()

    owner_id = _insert_user("owner@example.com")
    other_user_id = _insert_user("other@example.com")
    chat_repository = SqliteChatRepository()
    document_repository = SqliteChatDocumentRepository()

    first_session = chat_repository.create_session(owner_id)
    second_session = chat_repository.create_session(owner_id)
    other_user_session = chat_repository.create_session(other_user_id)

    first_document = document_repository.create_document(
        document_id="document-first",
        user_id=owner_id,
        project_id=None,
        original_filename="first.docx",
        content_hash="hash-first",
    )
    second_document = document_repository.create_document(
        document_id="document-second",
        user_id=owner_id,
        project_id=None,
        original_filename="second.docx",
        content_hash="hash-second",
    )
    document_repository.link_document_to_session(
        first_session.id, first_document.id, owner_id
    )
    document_repository.link_document_to_session(
        second_session.id, second_document.id, owner_id
    )

    assert [item.id for item in document_repository.list_session_documents(
        first_session.id, owner_id
    )] == [first_document.id]
    assert [item.id for item in document_repository.list_session_documents(
        second_session.id, owner_id
    )] == [second_document.id]
    assert document_repository.list_session_documents(
        other_user_session.id, other_user_id
    ) == []
    assert document_repository.list_session_documents(
        first_session.id, other_user_id
    ) == []


def test_empty_chat_drafts_are_not_returned_as_history(tmp_path, monkeypatch):
    monkeypatch.setattr(
        connection,
        "DATABASE_PATH",
        str(tmp_path / "empty-chat-draft.db"),
    )
    connection.init_db()

    owner_id = _insert_user("draft-owner@example.com")
    chat_repository = SqliteChatRepository()
    draft = chat_repository.create_session(owner_id)

    assert chat_repository.list_sessions(owner_id) == []
    assert chat_repository.get_session(draft.id, owner_id) is not None
