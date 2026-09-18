from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievedContext:
    context: str
    citations: list[dict[str, Any]]


@dataclass(frozen=True)
class ChatDocument:
    """A document attached to a chatbot session."""

    id: str
    user_id: int
    project_id: int | None
    original_filename: str
    title: str | None
    status: str
    content_hash: str
    markdown_path: str | None
    structure: list[dict]
    error_message: str | None
    created_at: str
    updated_at: str
    # The active derived chunk generation. Older documents remain at zero
    # until the RAG service backfills their tree index.
    chunk_index_version: int = 0


@dataclass(frozen=True)
class ChatDocumentChunk:
    id: int
    document_id: str
    ordinal: int
    title: str
    section_path: str
    content: str
    level: int
    embedding: list[float]
    # Stable tree coordinates. Legacy rows may keep these empty and are
    # handled by the retriever's compatibility adapter.
    node_key: str = ""
    parent_node_key: str | None = None
    node_kind: str = "content"
