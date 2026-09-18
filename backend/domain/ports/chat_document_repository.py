from __future__ import annotations

from typing import Protocol

from backend.domain.entities.chat_document import ChatDocument, ChatDocumentChunk


class ChatDocumentRepository(Protocol):
    def create_document(
        self,
        *,
        document_id: str,
        user_id: int,
        project_id: int | None,
        original_filename: str,
        content_hash: str,
    ) -> ChatDocument: ...

    def get_document(self, document_id: str, user_id: int) -> ChatDocument | None: ...

    def link_document_to_session(
        self, session_id: str, document_id: str, user_id: int
    ) -> None: ...

    def remove_document_from_session(
        self, session_id: str, document_id: str, user_id: int
    ) -> None: ...

    def list_session_documents(
        self, session_id: str, user_id: int
    ) -> list[ChatDocument]: ...

    def set_document_ready(
        self,
        document_id: str,
        user_id: int,
        *,
        title: str,
        markdown_path: str,
        structure: list[dict],
        chunks: list[dict],
    ) -> ChatDocument: ...

    def replace_document_chunks(
        self,
        document_id: str,
        user_id: int,
        *,
        chunks: list[dict],
    ) -> None: ...

    def set_document_failed(
        self, document_id: str, user_id: int, error_message: str
    ) -> ChatDocument | None: ...

    def list_session_chunks(
        self, session_id: str, user_id: int
    ) -> list[ChatDocumentChunk]: ...
