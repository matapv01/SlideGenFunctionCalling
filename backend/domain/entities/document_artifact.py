"""Canonical document representation shared by ingestion and RAG."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


DocumentBlockKind = Literal[
    "heading",
    "paragraph",
    "image",
    "table",
    "page_break",
]


@dataclass(frozen=True)
class DocumentBlock:
    """One ordered block from the source document."""

    kind: DocumentBlockKind
    index: int
    text: str = ""
    asset_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentArtifact:
    """Normalized document output consumed by preprocessing and RAG."""

    title: str
    plain_text: str
    markdown: str
    structure: list[dict[str, Any]]
    blocks: list[DocumentBlock] = field(default_factory=list)
    assets: list[dict[str, Any]] = field(default_factory=list)
    source_type: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)
