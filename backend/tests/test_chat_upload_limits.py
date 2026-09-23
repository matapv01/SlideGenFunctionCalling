import asyncio
from types import SimpleNamespace

import pytest

import backend.application.services.document_rag_service as document_rag_module
from backend.application.services.document_rag_service import (
    DocumentRagService,
    DocumentUploadLimitError,
)
from backend.domain.entities.chat import ChatSession


MEGABYTE = 1024 * 1024


class _DocumentRepository:
    def __init__(self, documents=None):
        self.documents = list(documents or [])

    def list_session_documents(self, session_id: str, user_id: int):
        return list(self.documents)

    def create_document(self, **values):
        document = SimpleNamespace(
            id=values["document_id"],
            original_filename=values["original_filename"],
            size_bytes=values["size_bytes"],
        )
        self.documents.append(document)
        return document

    def link_document_to_session(self, session_id: str, document_id: str, user_id: int):
        return None


def _session() -> ChatSession:
    return ChatSession(
        id="session-1",
        user_id=7,
        project_id=None,
        title=None,
        history_summary=None,
        max_turns=20,
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )


def _service(repository) -> DocumentRagService:
    return DocumentRagService(
        repository=repository,
        embedding_provider=None,
        preprocessing_service=None,
    )


def test_docx_upload_rejects_a_file_above_the_plan_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(document_rag_module, "CHATBOT_DOCUMENTS_DIR", tmp_path)
    repository = _DocumentRepository()
    service = _service(repository)

    with pytest.raises(DocumentUploadLimitError, match="10 MB"):
        asyncio.run(
            service.create_pending_docx(
                session=_session(),
                original_filename="large.docx",
                content=b"x" * (10 * MEGABYTE + 1),
                max_file_bytes=10 * MEGABYTE,
                max_total_bytes=50 * MEGABYTE,
            )
        )

    assert repository.documents == []


def test_docx_upload_rejects_when_conversation_total_would_be_exceeded(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(document_rag_module, "CHATBOT_DOCUMENTS_DIR", tmp_path)
    repository = _DocumentRepository(
        [SimpleNamespace(id="existing", size_bytes=8 * MEGABYTE)]
    )
    service = _service(repository)

    with pytest.raises(DocumentUploadLimitError, match="10 MB"):
        asyncio.run(
            service.create_pending_docx(
                session=_session(),
                original_filename="another.docx",
                content=b"x" * (3 * MEGABYTE),
                max_file_bytes=10 * MEGABYTE,
                max_total_bytes=10 * MEGABYTE,
            )
        )

    assert len(repository.documents) == 1
