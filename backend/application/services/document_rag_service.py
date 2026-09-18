from __future__ import annotations

import asyncio
import hashlib
import logging
import math
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.config import (
    CHATBOT_DOCUMENTS_DIR,
    CHATBOT_RAG_CHUNK_CHARS,
    CHATBOT_RAG_DETAIL_NODE_LIMIT,
    CHATBOT_RAG_MAX_ANCESTOR_DEPTH,
    CHATBOT_RAG_MAX_CONTEXT_CHARS,
    CHATBOT_RAG_MAX_SIBLINGS,
    CHATBOT_RAG_MIN_SIMILARITY,
    CHATBOT_RAG_OVERVIEW_SECTION_LIMIT,
    CHATBOT_RAG_TOP_K,
    CHATBOT_UPLOAD_MAX_BYTES,
)
from backend.application.services.document_preprocessing_service import (
    DocumentPreprocessingService,
)
from backend.domain.entities.chat import ChatSession
from backend.domain.entities.chat_document import ChatDocumentChunk, RetrievedContext
from backend.domain.ports.chat_document_repository import ChatDocumentRepository
from backend.domain.ports.embedding_provider import EmbeddingProvider

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _ChunkRef:
    """A chunk plus normalized tree coordinates.

    Rows written before the hierarchical index existed are normalized here so
    they remain retrievable while new uploads use stable node metadata.
    """

    chunk: ChatDocumentChunk
    node_key: str
    parent_node_key: str | None
    node_kind: str

    @property
    def identity(self) -> tuple[str, str]:
        return self.chunk.document_id, self.node_key


@dataclass
class _NodeGroup:
    identity: tuple[str, str]
    document_id: str
    node_key: str
    parent_node_key: str | None
    level: int
    node_kind: str
    chunks: list[_ChunkRef]


@dataclass(frozen=True)
class _Selection:
    score: float
    ref: _ChunkRef
    role: str


class DocumentRagService:
    """Document ingestion and hierarchical retrieval for chatbot sessions.

    The service follows the cloned RAG project's useful boundaries without
    importing its PostgreSQL/LangGraph runtime:

    DOCX -> canonical Markdown/JSON -> section chunks -> embeddings ->
    scoped retrieval -> source-aware context.

    Retrieval uses the preprocessed heading tree as the document hierarchy,
    runs multi-facet query variants, grades candidates by cosine similarity,
    deduplicates context at packing time, and keeps provenance for citations.
    """

    def __init__(
        self,
        repository: ChatDocumentRepository,
        embedding_provider: EmbeddingProvider,
        preprocessing_service: DocumentPreprocessingService,
    ) -> None:
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.preprocessing_service = preprocessing_service
        self._legacy_reindex_lock = asyncio.Lock()
        self._legacy_reindex_attempted: set[tuple[int, str]] = set()

    def list_session_documents(self, session_id: str, user_id: int):
        return self.repository.list_session_documents(session_id, user_id)

    def has_ready_documents(self, session: ChatSession) -> bool:
        """Return whether this conversation has an indexed document available.

        The chatbot preflight uses the same repository boundary as retrieval so
        it can skip asking the user to choose/upload a source that is already
        attached to the current conversation.
        """
        return any(
            document.status == "ready"
            for document in self.repository.list_session_documents(
                session.id, session.user_id
            )
        )

    def remove_document_from_session(
        self, *, session: ChatSession, document_id: str
    ) -> None:
        """Detach a document and clean its files when no session uses it."""
        document = self.repository.get_document(document_id, session.user_id)
        if document is None:
            raise LookupError("Document not found")

        self.repository.remove_document_from_session(
            session.id, document_id, session.user_id
        )
        # A document is normally private to one conversation, but keep shared
        # rows/files intact if a future adapter links it to another session.
        if self.repository.get_document(document_id, session.user_id) is None:
            self._remove_document_files(document)

    @staticmethod
    def _remove_document_files(document) -> None:
        root = CHATBOT_DOCUMENTS_DIR.resolve()
        paths = [root / f"{document.id}.docx"]
        if document.markdown_path:
            paths.append(Path(document.markdown_path))
        for path in paths:
            try:
                resolved = path.resolve()
                if resolved == root or root not in resolved.parents:
                    continue
                resolved.unlink(missing_ok=True)
            except OSError:
                logger.warning("Unable to remove chatbot document file %s", path)

    async def ingest_docx(
        self,
        *,
        session: ChatSession,
        original_filename: str,
        content: bytes,
    ):
        """Preprocess and index one DOCX for the selected conversation."""
        if not original_filename.lower().endswith(".docx"):
            raise ValueError("Chỉ hỗ trợ tài liệu DOCX ở phiên bản này")
        if not content:
            raise ValueError("Tệp DOCX rỗng")
        if len(content) > CHATBOT_UPLOAD_MAX_BYTES:
            raise ValueError("Tệp DOCX vượt quá giới hạn 25 MB")

        document_id = str(uuid.uuid4())
        content_hash = hashlib.sha1(content).hexdigest()
        source_path = CHATBOT_DOCUMENTS_DIR / f"{document_id}.docx"
        markdown_path = CHATBOT_DOCUMENTS_DIR / f"{document_id}.md"
        source_path.write_bytes(content)
        document = self.repository.create_document(
            document_id=document_id,
            user_id=session.user_id,
            project_id=session.project_id,
            original_filename=Path(original_filename).name,
            content_hash=content_hash,
        )
        self.repository.link_document_to_session(
            session.id, document.id, session.user_id
        )

        try:
            state = await self.preprocessing_service.preprocess_for_chatbot(
                docx_file=str(source_path),
            )
            markdown = str(state.get("plain_text") or "").strip()
            structure = state.get("document_structure") or []
            title = str(
                state.get("document_title") or Path(original_filename).stem
            ).strip()
            if not markdown:
                raise ValueError("Không đọc được nội dung DOCX")

            markdown_path.write_text(markdown, encoding="utf-8")
            logical_chunks = self._build_chunks(
                structure if isinstance(structure, list) else [],
                markdown,
                document_title=title,
            )
            embeddings = await asyncio.to_thread(
                self.embedding_provider.embed_documents,
                [chunk["embedding_text"] for chunk in logical_chunks],
            )
            if len(embeddings) != len(logical_chunks):
                raise RuntimeError("Embedding provider returned an invalid result")
            chunks = [
                {**chunk, "embedding": vector}
                for chunk, vector in zip(logical_chunks, embeddings)
            ]
            return self.repository.set_document_ready(
                document.id,
                session.user_id,
                title=title,
                markdown_path=str(markdown_path),
                structure=structure,
                chunks=chunks,
            )
        except Exception as exc:
            self.repository.set_document_failed(
                document.id, session.user_id, str(exc)
            )
            # Keep the canonical source for a failed document so the error can
            # be diagnosed/reprocessed; it is never exposed without ownership.
            raise

    async def retrieve(
        self, session: ChatSession, query: str
    ) -> RetrievedContext:
        return await self.retrieve_many(session, [query])

    async def retrieve_many(
        self,
        session: ChatSession,
        queries: list[str],
        *,
        mode: str = "targeted_section",
        include_root: bool = False,
        include_ancestors: bool = True,
        include_siblings: bool = False,
        max_detail_nodes: int = CHATBOT_RAG_DETAIL_NODE_LIMIT,
        target_slide_count: int | None = None,
    ) -> RetrievedContext:
        """Retrieve context with a document-tree-aware strategy.

        Overview/deck requests prioritize root and high-level section summaries
        for coverage. Targeted requests first find anchor nodes, then expand
        through their parents, children and siblings according to the plan.
        ``max_detail_nodes`` is a hard budget for anchor and child detail
        nodes; root, section summaries, ancestors and sibling summaries do
        not consume that budget.
        """
        clean_queries: list[str] = []
        seen_queries: set[str] = set()
        for query in queries:
            clean_query = " ".join(str(query).split()).strip()
            key = clean_query.casefold()
            if not clean_query or key in seen_queries:
                continue
            seen_queries.add(key)
            clean_queries.append(clean_query)
        if not clean_queries:
            return RetrievedContext(context="", citations=[])

        chunks = self.repository.list_session_chunks(session.id, session.user_id)
        if not chunks:
            return RetrievedContext(context="", citations=[])

        if any(not (chunk.node_key or "").strip() for chunk in chunks):
            await self._upgrade_legacy_indexes(session, chunks)
            # Re-read after a successful upgrade so the current request uses
            # the materialized tree instead of the compatibility coordinates.
            chunks = self.repository.list_session_chunks(session.id, session.user_id)
            if not chunks:
                return RetrievedContext(context="", citations=[])

        refs, nodes, children = self._build_tree_index(chunks)
        rankings, chunk_scores, node_scores = await self._rank_queries(
            refs, clean_queries
        )
        normalized_mode = mode if mode in {
            "document_overview",
            "deck_from_document",
            "targeted_section",
            "topic_grounded",
            "multi_facet",
        } else "targeted_section"
        max_detail_nodes = max(
            0,
            min(
                CHATBOT_RAG_DETAIL_NODE_LIMIT * 2,
                int(max_detail_nodes or 0),
            ),
        )

        if normalized_mode in {"document_overview", "deck_from_document"}:
            selections = self._retrieve_overview(
                nodes,
                rankings,
                chunk_scores,
                node_scores,
                mode=normalized_mode,
                max_detail_nodes=max_detail_nodes,
                target_slide_count=target_slide_count,
            )
            documents = self.repository.list_session_documents(
                session.id, session.user_id
            )
            prefaces = self._legacy_overview_prefaces(documents, nodes)
        elif normalized_mode == "topic_grounded":
            selections = self._retrieve_topic_grounded(
                nodes,
                children,
                rankings,
                chunk_scores,
                node_scores,
                include_ancestors=include_ancestors,
                include_siblings=include_siblings,
                max_detail_nodes=max_detail_nodes,
            )
            prefaces = []
        else:
            selections = self._retrieve_targeted(
                nodes,
                children,
                rankings,
                chunk_scores,
                node_scores,
                include_root=include_root,
                include_ancestors=include_ancestors,
                include_siblings=include_siblings,
                max_detail_nodes=max_detail_nodes,
            )
            prefaces = []

        return self._pack_context(selections, prefaces=prefaces)

    async def _upgrade_legacy_indexes(
        self,
        session: ChatSession,
        chunks: list[ChatDocumentChunk],
    ) -> None:
        """Backfill tree rows for documents indexed by the former flat schema.

        This is lazy and transactional: an existing conversation gets the
        improved hierarchy on its first retrieval, while a failed backfill
        leaves the old index available as a safe fallback. No source document
        or canonical structure is modified.
        """
        get_document = getattr(self.repository, "get_document", None)
        replace_chunks = getattr(self.repository, "replace_document_chunks", None)
        if not callable(get_document) or not callable(replace_chunks):
            return

        candidate_ids = sorted(
            {
                chunk.document_id
                for chunk in chunks
                if not (chunk.node_key or "").strip()
            }
        )
        if not candidate_ids:
            return

        async with self._legacy_reindex_lock:
            current_chunks = self.repository.list_session_chunks(
                session.id, session.user_id
            )
            chunks_by_document: dict[str, list[ChatDocumentChunk]] = {}
            for chunk in current_chunks:
                chunks_by_document.setdefault(chunk.document_id, []).append(chunk)

            for document_id in candidate_ids:
                attempt_key = (session.user_id, document_id)
                if attempt_key in self._legacy_reindex_attempted:
                    continue
                self._legacy_reindex_attempted.add(attempt_key)

                try:
                    document = get_document(document_id, session.user_id)
                    if document is None or document.status != "ready":
                        continue
                    structure = (
                        document.structure
                        if isinstance(document.structure, list)
                        else []
                    )
                    markdown = self._read_markdown(document.markdown_path)
                    if not markdown and not structure:
                        markdown = "\n\n".join(
                            chunk.content
                            for chunk in chunks_by_document.get(document_id, [])
                            if chunk.content.strip()
                        )
                    if not markdown and not structure:
                        logger.warning(
                            "Skipping legacy RAG backfill for document %s: "
                            "canonical source is unavailable",
                            document_id,
                        )
                        continue

                    logical_chunks = self._build_chunks(
                        structure,
                        markdown,
                        document_title=(
                            document.title
                            or Path(document.original_filename).stem
                            or "Document"
                        ),
                    )
                    embeddings = await asyncio.to_thread(
                        self.embedding_provider.embed_documents,
                        [chunk["embedding_text"] for chunk in logical_chunks],
                    )
                    if len(embeddings) != len(logical_chunks):
                        raise RuntimeError(
                            "Embedding provider returned an invalid result"
                        )
                    replace_chunks(
                        document_id,
                        session.user_id,
                        chunks=[
                            {**chunk, "embedding": vector}
                            for chunk, vector in zip(logical_chunks, embeddings)
                        ],
                    )
                    logger.info(
                        "Backfilled hierarchical RAG index for document %s (%d chunks)",
                        document_id,
                        len(logical_chunks),
                    )
                except Exception:
                    # A transient embedding/provider failure should be
                    # retried by a later request. Permanent cases (missing
                    # source or a non-ready document) are kept in the
                    # attempted set above so they do not log on every turn.
                    self._legacy_reindex_attempted.discard(attempt_key)
                    # Retrieval must remain available for old rows even when a
                    # source file was removed or the local embedding model has
                    # a transient failure.
                    logger.exception(
                        "Unable to backfill hierarchical RAG index for document %s",
                        document_id,
                    )

    @staticmethod
    def _read_markdown(path: str | None) -> str:
        if not path:
            return ""
        try:
            markdown_path = Path(path)
            if not markdown_path.is_file():
                return ""
            return markdown_path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            return ""

    async def _rank_queries(
        self,
        refs: list[_ChunkRef],
        queries: list[str],
    ) -> tuple[
        list[list[tuple[float, _ChunkRef]]],
        dict[int, float],
        dict[tuple[str, str], float],
    ]:
        query_variants: list[list[str]] = []
        all_variants: list[str] = []
        for query in queries:
            variants: list[str] = []
            seen: set[str] = set()
            for variant in self._query_variants(query):
                key = variant.casefold()
                if key in seen:
                    continue
                seen.add(key)
                variants.append(variant)
                all_variants.append(variant)
            query_variants.append(variants)

        query_vectors = await asyncio.to_thread(
            self.embedding_provider.embed_documents, all_variants
        )
        if len(query_vectors) != len(all_variants):
            raise RuntimeError("Embedding provider returned an invalid result")

        rankings: list[list[tuple[float, _ChunkRef]]] = []
        chunk_scores: dict[int, float] = {}
        node_scores: dict[tuple[str, str], float] = {}
        vector_offset = 0
        for variants in query_variants:
            best_by_node: dict[tuple[str, str], tuple[float, _ChunkRef]] = {}
            for variant in variants:
                query_vector = query_vectors[vector_offset]
                vector_offset += 1
                for ref in refs:
                    score = self._score_ref(variant, query_vector, ref)
                    previous_chunk_score = chunk_scores.get(ref.chunk.id)
                    if previous_chunk_score is None or score > previous_chunk_score:
                        chunk_scores[ref.chunk.id] = score
                    previous_node = best_by_node.get(ref.identity)
                    if previous_node is None or score > previous_node[0]:
                        best_by_node[ref.identity] = (score, ref)
                    previous_global_node = node_scores.get(ref.identity)
                    if previous_global_node is None or score > previous_global_node:
                        node_scores[ref.identity] = score
            rankings.append(
                sorted(best_by_node.values(), key=lambda item: item[0], reverse=True)
            )
        return rankings, chunk_scores, node_scores

    def _score_ref(
        self,
        query: str,
        query_vector: list[float],
        ref: _ChunkRef,
    ) -> float:
        score = self._cosine(query_vector, ref.chunk.embedding)
        score += self._lexical_bonus(query, ref.chunk) * 0.08
        # Summary nodes are intentionally slightly favored for broad queries;
        # detail nodes still win when their semantic/lexical match is stronger.
        if ref.node_kind in {"root_summary", "section_summary"}:
            score += 0.015
        return score

    @classmethod
    def _build_tree_index(
        cls,
        chunks: list[ChatDocumentChunk],
    ) -> tuple[
        list[_ChunkRef],
        dict[tuple[str, str], _NodeGroup],
        dict[tuple[str, str], list[tuple[str, str]]],
    ]:
        refs: list[_ChunkRef] = []
        nodes: dict[tuple[str, str], _NodeGroup] = {}
        for chunk in chunks:
            node_key, parent_node_key = cls._normalise_coordinates(chunk)
            node_kind = (chunk.node_kind or "content").strip() or "content"
            ref = _ChunkRef(
                chunk=chunk,
                node_key=node_key,
                parent_node_key=parent_node_key,
                node_kind=node_kind,
            )
            refs.append(ref)
            group = nodes.get(ref.identity)
            if group is None:
                group = _NodeGroup(
                    identity=ref.identity,
                    document_id=chunk.document_id,
                    node_key=node_key,
                    parent_node_key=parent_node_key,
                    level=max(0, int(chunk.level)),
                    node_kind=node_kind,
                    chunks=[],
                )
                nodes[ref.identity] = group
            group.chunks.append(ref)

        children: dict[tuple[str, str], list[tuple[str, str]]] = {}
        for identity, group in nodes.items():
            if group.parent_node_key:
                parent_identity = (group.document_id, group.parent_node_key)
                children.setdefault(parent_identity, []).append(identity)
        for identities in children.values():
            identities.sort(key=lambda item: min(
                ref.chunk.ordinal
                for ref in nodes[item].chunks
            ))
        return refs, nodes, children

    @staticmethod
    def _normalise_coordinates(
        chunk: ChatDocumentChunk,
    ) -> tuple[str, str | None]:
        node_key = (chunk.node_key or "").strip()
        path_parts = [part.strip() for part in chunk.section_path.split("/") if part.strip()]
        if not node_key:
            node_key = (
                "legacy:" + "|".join(path_parts)
                if path_parts
                else f"legacy:chunk:{chunk.id}"
            )
        parent_node_key = (chunk.parent_node_key or "").strip() or None
        if parent_node_key is None and node_key != "root":
            if node_key.startswith("legacy:") and len(path_parts) > 1:
                parent_node_key = "legacy:" + "|".join(path_parts[:-1])
            else:
                parent_node_key = "root"
        return node_key, parent_node_key

    def _retrieve_overview(
        self,
        nodes: dict[tuple[str, str], _NodeGroup],
        rankings: list[list[tuple[float, _ChunkRef]]],
        chunk_scores: dict[int, float],
        node_scores: dict[tuple[str, str], float],
        *,
        mode: str,
        max_detail_nodes: int,
        target_slide_count: int | None,
    ) -> list[_Selection]:
        selections: list[_Selection] = []
        root_groups = sorted(
            (
                group
                for group in nodes.values()
                if group.node_key == "root"
            ),
            key=lambda group: group.document_id,
        )
        for group in root_groups:
            ref = self._best_ref(group, chunk_scores, prefer_summary=True)
            if ref is not None:
                selections.append(_Selection(node_scores.get(group.identity, 0.0), ref, "root"))

        section_groups = [
            group
            for group in nodes.values()
            if group.node_key != "root"
            and (
                group.node_kind == "section_summary"
                or group.level <= 2
            )
        ]
        section_groups.sort(key=self._group_order)
        desired_sections = max(6, (target_slide_count or 8) * 2)
        desired_sections = min(CHATBOT_RAG_OVERVIEW_SECTION_LIMIT, desired_sections)
        chosen_sections = self._choose_overview_sections(
            section_groups,
            desired_sections,
            node_scores,
        )
        chosen_identities = {group.identity for group in chosen_sections}
        for group in chosen_sections:
            ref = self._best_ref(group, chunk_scores, prefer_summary=True)
            if ref is not None:
                selections.append(_Selection(node_scores.get(group.identity, 0.0), ref, "section"))

        if mode != "deck_from_document" or max_detail_nodes <= 0:
            return selections

        detail_candidates: list[tuple[float, _ChunkRef]] = []
        for ranking in rankings:
            detail_candidates.extend(
                (score, ref)
                for score, ref in ranking
                if ref.node_kind == "content"
                and self._belongs_to_selected_branch(
                    ref.identity,
                    chosen_identities,
                    nodes,
                )
            )
        detail_candidates.sort(key=lambda item: item[0], reverse=True)
        seen_nodes: set[tuple[str, str]] = set()
        for score, ref in detail_candidates:
            if ref.identity in seen_nodes:
                continue
            seen_nodes.add(ref.identity)
            selections.append(_Selection(score, ref, "detail"))
            if len(seen_nodes) >= max_detail_nodes:
                break
        return selections

    @classmethod
    def _choose_overview_sections(
        cls,
        groups: list[_NodeGroup],
        limit: int,
        node_scores: dict[tuple[str, str], float],
    ) -> list[_NodeGroup]:
        if not groups or limit <= 0:
            return []
        top_level = [group for group in groups if group.level <= 1]
        if len(top_level) >= limit:
            return cls._spread_groups(top_level, limit)

        chosen = list(top_level)
        chosen_identities = {group.identity for group in chosen}
        remaining = [
            group for group in groups if group.identity not in chosen_identities
        ]
        remaining.sort(
            key=lambda group: node_scores.get(group.identity, 0.0),
            reverse=True,
        )
        chosen.extend(remaining[: max(0, limit - len(chosen))])
        return sorted(chosen, key=cls._group_order)

    @staticmethod
    def _spread_groups(groups: list[_NodeGroup], limit: int) -> list[_NodeGroup]:
        if len(groups) <= limit:
            return list(groups)
        if limit == 1:
            return [groups[0]]
        indexes = {
            round(index * (len(groups) - 1) / (limit - 1))
            for index in range(limit)
        }
        return [group for index, group in enumerate(groups) if index in indexes]

    @staticmethod
    def _group_order(group: _NodeGroup) -> tuple[str, int]:
        return (
            group.document_id,
            min(ref.chunk.ordinal for ref in group.chunks),
        )

    @classmethod
    def _belongs_to_selected_branch(
        cls,
        identity: tuple[str, str],
        selected_identities: set[tuple[str, str]],
        nodes: dict[tuple[str, str], _NodeGroup],
    ) -> bool:
        current = identity
        visited: set[tuple[str, str]] = set()
        while current not in visited:
            if current in selected_identities:
                return True
            visited.add(current)
            group = nodes.get(current)
            if group is None or not group.parent_node_key:
                return False
            current = (group.document_id, group.parent_node_key)
        return False

    def _retrieve_topic_grounded(
        self,
        nodes: dict[tuple[str, str], _NodeGroup],
        children: dict[tuple[str, str], list[tuple[str, str]]],
        rankings: list[list[tuple[float, _ChunkRef]]],
        chunk_scores: dict[int, float],
        node_scores: dict[tuple[str, str], float],
        *,
        include_ancestors: bool,
        include_siblings: bool,
        max_detail_nodes: int,
    ) -> list[_Selection]:
        """Probe the outline before expanding evidence for a requested topic.

        A topic request may be unrelated to the attached document. The root is
        still useful to establish that relationship, but detail expansion is
        gated by a real matching high-level section so unrelated content is
        not injected into the slide brief.
        """
        selections: list[_Selection] = []
        for group in sorted(
            (group for group in nodes.values() if group.node_key == "root"),
            key=lambda item: item.document_id,
        ):
            ref = self._best_ref(group, chunk_scores, prefer_summary=True)
            if ref is not None:
                selections.append(
                    _Selection(node_scores.get(group.identity, 0.0), ref, "root")
                )

        outline_groups = [
            group
            for group in nodes.values()
            if group.node_key != "root"
            and (
                group.node_kind == "section_summary"
                or group.level <= 2
            )
            and node_scores.get(group.identity, 0.0)
            >= CHATBOT_RAG_MIN_SIMILARITY
        ]
        outline_groups.sort(
            key=lambda group: (
                -node_scores.get(group.identity, 0.0),
                self._group_order(group),
            )
        )
        outline_limit = max(2, min(6, max_detail_nodes or 6))
        selected_outline_identities = {
            group.identity for group in outline_groups[:outline_limit]
        }
        for group in outline_groups[:outline_limit]:
            ref = self._best_ref(group, chunk_scores, prefer_summary=True)
            if ref is not None:
                selections.append(
                    _Selection(
                        node_scores.get(group.identity, 0.0),
                        ref,
                        "section",
                    )
                )

        selections.extend(
            self._retrieve_targeted(
                nodes,
                children,
                rankings,
                chunk_scores,
                node_scores,
                include_root=False,
                include_ancestors=include_ancestors,
                include_siblings=include_siblings,
                max_detail_nodes=max_detail_nodes,
                allowed_branch_identities=selected_outline_identities,
            )
        )
        return selections

    def _retrieve_targeted(
        self,
        nodes: dict[tuple[str, str], _NodeGroup],
        children: dict[tuple[str, str], list[tuple[str, str]]],
        rankings: list[list[tuple[float, _ChunkRef]]],
        chunk_scores: dict[int, float],
        node_scores: dict[tuple[str, str], float],
        *,
        include_root: bool,
        include_ancestors: bool,
        include_siblings: bool,
        max_detail_nodes: int,
        allowed_branch_identities: set[tuple[str, str]] | None = None,
    ) -> list[_Selection]:
        detail_budget = max(0, max_detail_nodes)
        anchor_limit = min(CHATBOT_RAG_TOP_K, detail_budget)
        anchors: list[tuple[float, _ChunkRef]] = []
        seen_anchor_nodes: set[tuple[str, str]] = set()

        def is_allowed(ref: _ChunkRef) -> bool:
            return (
                allowed_branch_identities is None
                or self._belongs_to_selected_branch(
                    ref.identity,
                    allowed_branch_identities,
                    nodes,
                )
            )

        # Reserve one anchor for each planner facet before filling the rest by
        # global score, preventing one broad facet from starving the others.
        for ranking in rankings:
            for score, ref in ranking:
                if score < CHATBOT_RAG_MIN_SIMILARITY:
                    continue
                if ref.node_key == "root" or ref.identity in seen_anchor_nodes:
                    continue
                if not is_allowed(ref):
                    continue
                anchors.append((score, ref))
                seen_anchor_nodes.add(ref.identity)
                break
            if len(anchors) >= anchor_limit:
                break

        global_candidates: dict[tuple[str, str], tuple[float, _ChunkRef]] = {}
        for ranking in rankings:
            for score, ref in ranking:
                if ref.node_key == "root":
                    continue
                previous = global_candidates.get(ref.identity)
                if previous is None or score > previous[0]:
                    global_candidates[ref.identity] = (score, ref)
        for score, ref in sorted(
            global_candidates.values(), key=lambda item: item[0], reverse=True
        ):
            if len(anchors) >= anchor_limit:
                break
            if ref.identity in seen_anchor_nodes:
                continue
            if score < CHATBOT_RAG_MIN_SIMILARITY:
                continue
            if not is_allowed(ref):
                continue
            anchors.append((score, ref))
            seen_anchor_nodes.add(ref.identity)

        selections: list[_Selection] = []
        if include_root:
            for root_group in sorted(
                (group for group in nodes.values() if group.node_key == "root"),
                key=lambda item: item.document_id,
            ):
                root_ref = self._best_ref(
                    root_group, chunk_scores, prefer_summary=True
                )
                if root_ref is not None:
                    selections.append(
                        _Selection(
                            node_scores.get(root_group.identity, 0.0),
                            root_ref,
                            "root",
                        )
                    )

        detail_node_identities: set[tuple[str, str]] = set()
        for score, anchor_ref in anchors:
            if len(detail_node_identities) >= detail_budget:
                break
            group = nodes.get(anchor_ref.identity)
            if group is None:
                continue

            if include_ancestors:
                selections.extend(
                    self._ancestor_selections(
                        group,
                        nodes,
                        chunk_scores,
                        node_scores,
                    )
                )

            anchor_ref = self._best_ref(
                group,
                chunk_scores,
                prefer_summary=False,
            ) or anchor_ref
            selections.append(_Selection(score, anchor_ref, "anchor"))
            detail_node_identities.add(anchor_ref.identity)

            child_identities = children.get(group.identity, [])
            if child_identities:
                child_candidates = sorted(
                    (
                        (node_scores.get(identity, 0.0), identity)
                        for identity in child_identities
                    ),
                    reverse=True,
                )
                for child_score, child_identity in child_candidates[:2]:
                    if len(detail_node_identities) >= detail_budget:
                        break
                    if child_identity in detail_node_identities:
                        continue
                    child_group = nodes.get(child_identity)
                    if child_group is None:
                        continue
                    child_ref = self._best_ref(
                        child_group, chunk_scores, prefer_summary=False
                    )
                    if child_ref is not None:
                        selections.append(_Selection(child_score, child_ref, "detail"))
                        detail_node_identities.add(child_identity)

            if include_siblings and group.parent_node_key:
                parent_identity = (group.document_id, group.parent_node_key)
                sibling_identities = [
                    identity
                    for identity in children.get(parent_identity, [])
                    if identity != group.identity
                ]
                sibling_identities.sort(
                    key=lambda identity: node_scores.get(identity, 0.0),
                    reverse=True,
                )
                for sibling_identity in sibling_identities[:CHATBOT_RAG_MAX_SIBLINGS]:
                    sibling_group = nodes.get(sibling_identity)
                    if sibling_group is None:
                        continue
                    sibling_ref = self._best_ref(
                        sibling_group, chunk_scores, prefer_summary=True
                    )
                    if sibling_ref is not None:
                        selections.append(_Selection(
                            node_scores.get(sibling_identity, 0.0),
                            sibling_ref,
                            "sibling",
                        ))
        return selections

    def _ancestor_selections(
        self,
        group: _NodeGroup,
        nodes: dict[tuple[str, str], _NodeGroup],
        chunk_scores: dict[int, float],
        node_scores: dict[tuple[str, str], float],
    ) -> list[_Selection]:
        selections: list[_Selection] = []
        current_key = group.parent_node_key
        for _ in range(CHATBOT_RAG_MAX_ANCESTOR_DEPTH):
            if not current_key:
                break
            ancestor = nodes.get((group.document_id, current_key))
            if ancestor is None:
                break
            ref = self._best_ref(ancestor, chunk_scores, prefer_summary=True)
            if ref is not None:
                selections.append(_Selection(
                    node_scores.get(ancestor.identity, 0.0),
                    ref,
                    "ancestor",
                ))
            current_key = ancestor.parent_node_key
        return list(reversed(selections))

    @staticmethod
    def _best_ref(
        group: _NodeGroup,
        chunk_scores: dict[int, float],
        *,
        prefer_summary: bool,
    ) -> _ChunkRef | None:
        if not group.chunks:
            return None
        if prefer_summary:
            preferred = [
                ref
                for ref in group.chunks
                if ref.node_kind in {"root_summary", "section_summary"}
            ]
        else:
            preferred = [
                ref for ref in group.chunks if ref.node_kind == "content"
            ]
        candidates = preferred or group.chunks
        return max(
            candidates,
            key=lambda ref: (chunk_scores.get(ref.chunk.id, 0.0), -ref.chunk.ordinal),
        )

    @staticmethod
    def _legacy_overview_prefaces(
        documents: list[Any],
        nodes: dict[tuple[str, str], _NodeGroup],
    ) -> list[str]:
        prefaces: list[str] = []
        for document in documents:
            if (document.id, "root") in nodes:
                continue
            structure = document.structure if isinstance(document.structure, list) else []
            titles = [
                str(node.get("title") or "").strip()
                for node in structure
                if isinstance(node, dict) and str(node.get("title") or "").strip()
            ]
            if not titles:
                continue
            prefaces.append(
                "[Document overview]\n"
                f"{document.title or document.original_filename}\n"
                "Main sections: "
                + "; ".join(titles[:24])
            )
        return prefaces

    @staticmethod
    def _pack_context(
        selections: list[_Selection],
        *,
        prefaces: list[str],
    ) -> RetrievedContext:
        role_order = {
            "root": 0,
            "legacy_overview": 0,
            "ancestor": 1,
            "section": 2,
            "anchor": 3,
            "detail": 4,
            "sibling": 5,
        }
        unique: dict[int, tuple[int, int, _Selection]] = {}
        for position, selection in enumerate(selections):
            priority = role_order.get(selection.role, 4)
            previous = unique.get(selection.ref.chunk.id)
            candidate = (priority, position, selection)
            if previous is None or candidate[:2] < previous[:2]:
                unique[selection.ref.chunk.id] = candidate

        ordered = sorted(unique.values(), key=lambda item: (item[0], item[1]))
        context_parts = [preface.strip() for preface in prefaces if preface.strip()]
        citations: list[dict[str, Any]] = []
        seen_content: set[str] = set()
        current_size = sum(len(part) for part in context_parts)
        for _, _, selection in ordered:
            chunk = selection.ref.chunk
            content = chunk.content.strip()
            fingerprint = hashlib.sha1(content.encode("utf-8")).hexdigest()
            if not content or fingerprint in seen_content:
                continue
            part = (
                f"[Source {len(citations) + 1} | level {chunk.level} | "
                f"{selection.ref.node_kind} | section: {chunk.section_path}]\n"
                f"{content}"
            )
            if current_size + len(part) > CHATBOT_RAG_MAX_CONTEXT_CHARS:
                continue
            context_parts.append(part)
            current_size += len(part)
            seen_content.add(fingerprint)
            citations.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "section": chunk.section_path,
                    "title": chunk.title,
                    "level": chunk.level,
                    "node_key": selection.ref.node_key,
                    "parent_node_key": selection.ref.parent_node_key,
                    "node_kind": selection.ref.node_kind,
                    "role": selection.role,
                    "similarity": round(float(selection.score), 4),
                }
            )

        return RetrievedContext(
            context="\n\n".join(context_parts),
            citations=citations,
        )

    @staticmethod
    def _query_variants(query: str) -> list[str]:
        clean = " ".join(query.split())
        variants = [clean]
        # The source RAG graph decomposes multi-facet questions before
        # retrieval. Keep that behavior deterministic and cheap for this
        # service, while the answer LLM still sees the original question.
        facets = re.split(
            r"\s+(?:và|and|also|cũng như)\s+|[;?]\s*",
            clean,
            flags=re.I,
        )
        existing = {value.lower() for value in variants}
        for facet in facets:
            facet = facet.strip(" .")
            if len(facet) >= 12 and facet.lower() not in existing:
                variants.append(facet)
                existing.add(facet.lower())
        return variants[:4]

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        dot = sum(float(a) * float(b) for a, b in zip(left, right))
        left_norm = math.sqrt(sum(float(a) * float(a) for a in left))
        right_norm = math.sqrt(sum(float(b) * float(b) for b in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)

    @staticmethod
    def _lexical_bonus(query: str, chunk: ChatDocumentChunk) -> float:
        query_terms = set(re.findall(r"\w{3,}", query.lower()))
        section_terms = set(
            re.findall(
                r"\w{3,}",
                f"{chunk.title} {chunk.section_path} {chunk.content}".lower(),
            )
        )
        if not query_terms:
            return 0.0
        return len(query_terms & section_terms) / len(query_terms)

    @classmethod
    def _build_chunks(
        cls,
        structure: list[dict[str, Any]],
        markdown: str,
        *,
        document_title: str = "Document",
    ) -> list[dict[str, Any]]:
        """Materialize the canonical document tree into retrievable nodes.

        The preprocessing workflow already decided which regions are
        structured and which regions needed LLM assistance. This method does
        not reinterpret that result. It only assigns stable coordinates and
        creates three retrieval representations:

        * one compact root overview per document;
        * one section summary for high-level/branch nodes;
        * detail chunks for the node's own body, never for its descendants.

        Keeping summaries and details in the same node group lets retrieval
        choose coverage for broad requests and evidence for targeted ones
        without flattening the source hierarchy.
        """
        chunks: list[dict[str, Any]] = []
        title = " ".join(str(document_title or "Document").split()).strip()
        title = title or "Document"

        def clean_title(node: dict[str, Any], fallback: str) -> str:
            value = " ".join(str(node.get("title") or "").split()).strip()
            return value or fallback

        def child_nodes(node: dict[str, Any]) -> list[dict[str, Any]]:
            value = node.get("children")
            if not isinstance(value, list):
                return []
            return [child for child in value if isinstance(child, dict)]

        def compact_preview(value: Any, limit: int = 720) -> str:
            text = " ".join(str(value or "").split()).strip()
            if len(text) <= limit:
                return text
            return text[: max(0, limit - 1)].rstrip() + "…"

        def add_piece(
            *,
            node_title: str,
            path: list[str],
            content: str,
            level: int,
            node_key: str,
            parent_node_key: str | None,
            node_kind: str,
            max_chars: int = CHATBOT_RAG_CHUNK_CHARS,
        ) -> None:
            text = str(content or "").strip()
            if not text and not node_title.strip():
                return

            section_path = " / ".join([*path, node_title] if node_title else path)
            if node_kind in {"root_summary", "section_summary"}:
                summary = text or f"Section: {node_title or title}"
                pieces = [summary[:max_chars].rstrip()]
            else:
                pieces = cls._split_text(text, max_chars)
                if not pieces:
                    return

            for piece in pieces:
                embedding_text = f"{section_path}\n{piece}".strip()
                chunks.append(
                    {
                        "ordinal": len(chunks),
                        "title": node_title or title,
                        "section_path": section_path or title,
                        # Keep the path in the persisted content for backwards
                        # compatibility with the old flat index and to make
                        # citations understandable to the answer model.
                        "content": embedding_text,
                        "embedding_text": embedding_text,
                        "level": max(0, level),
                        "node_key": node_key,
                        "parent_node_key": parent_node_key,
                        "node_kind": node_kind,
                    }
                )

        top_level_nodes = [
            node for node in structure if isinstance(node, dict)
        ]
        root_lines = [f"Document: {title}"]
        if top_level_nodes:
            root_lines.append("Main sections:")
            for index, node in enumerate(top_level_nodes, start=1):
                node_title = clean_title(node, f"Section {index}")
                line = f"- {node_title}"
                preview = compact_preview(node.get("content"))
                if preview:
                    line += f": {preview}"
                children = child_nodes(node)
                child_titles = [
                    clean_title(child, f"Subsection {child_index}")
                    for child_index, child in enumerate(children, start=1)
                ]
                if child_titles:
                    line += " | Subsections: " + "; ".join(child_titles[:12])
                root_lines.append(line)
        else:
            preview = compact_preview(markdown, 2400)
            if preview:
                root_lines.append(f"Overview: {preview}")

        add_piece(
            node_title=title,
            path=[],
            content="\n".join(root_lines),
            level=0,
            node_key="root",
            parent_node_key=None,
            node_kind="root_summary",
            max_chars=3200,
        )

        def visit(
            nodes: list[dict[str, Any]],
            *,
            parents: list[str],
            parent_node_key: str,
            depth: int,
        ) -> None:
            for index, node in enumerate(nodes, start=1):
                node_title = clean_title(node, f"Section {index}")
                node_key = (
                    str(index)
                    if parent_node_key == "root"
                    else f"{parent_node_key}.{index}"
                )
                path = [*parents]
                children = child_nodes(node)
                direct_content = str(node.get("content") or "").strip()

                # A summary exists for every branch and every high-level
                # section. Deeper leaf bodies remain detail-only to avoid
                # doubling the index and the context window.
                if children or depth <= 2:
                    summary_lines: list[str] = []
                    preview = compact_preview(direct_content)
                    if preview:
                        summary_lines.append(f"Summary: {preview}")
                    child_titles = [
                        clean_title(child, f"Subsection {child_index}")
                        for child_index, child in enumerate(children, start=1)
                    ]
                    if child_titles:
                        summary_lines.append(
                            "Subsections: " + "; ".join(child_titles[:16])
                        )
                    if not summary_lines:
                        summary_lines.append(f"Section: {node_title}")
                    add_piece(
                        node_title=node_title,
                        path=path,
                        content="\n".join(summary_lines),
                        level=depth,
                        node_key=node_key,
                        parent_node_key=parent_node_key,
                        node_kind="section_summary",
                        max_chars=1600,
                    )

                if direct_content:
                    add_piece(
                        node_title=node_title,
                        path=path,
                        content=direct_content,
                        level=depth,
                        node_key=node_key,
                        parent_node_key=parent_node_key,
                        node_kind="content",
                    )

                visit(
                    children,
                    parents=[*path, node_title],
                    parent_node_key=node_key,
                    depth=depth + 1,
                )

        if top_level_nodes:
            visit(
                top_level_nodes,
                parents=[],
                parent_node_key="root",
                depth=1,
            )
        elif markdown.strip():
            # A whole-document, no-heading input still gets a root child so
            # targeted retrieval can distinguish its overview from its full
            # evidence without inventing a fake heading tree.
            add_piece(
                node_title=title,
                path=[],
                content=markdown,
                level=1,
                node_key="root-content",
                parent_node_key="root",
                node_kind="content",
            )

        return chunks

    @staticmethod
    def _split_text(text: str, max_chars: int) -> list[str]:
        if not text:
            return []
        if len(text) <= max_chars:
            return [text]
        paragraphs = [
            part.strip()
            for part in re.split(r"\n{2,}", text)
            if part.strip()
        ]
        pieces: list[str] = []
        current = ""
        for paragraph in paragraphs or [text]:
            while len(paragraph) > max_chars:
                cut = paragraph.rfind(" ", 0, max_chars)
                cut = cut if cut > max_chars // 2 else max_chars
                prefix = paragraph[:cut].strip()
                if prefix:
                    pieces.append(prefix)
                paragraph = paragraph[cut:].strip()
            if current and len(current) + len(paragraph) + 2 > max_chars:
                pieces.append(current)
                current = ""
            current = f"{current}\n\n{paragraph}".strip()
        if current:
            pieces.append(current)
        return pieces
