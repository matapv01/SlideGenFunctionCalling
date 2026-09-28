import asyncio
from types import SimpleNamespace

from backend.application.services.document_rag_service import DocumentRagService
from backend.application.services.chatbot_service import ChatbotService
from backend.application.services.rag_query_planner import RagQueryPlan
from backend.domain.entities.chat import ChatSession
from backend.domain.entities.chat_document import ChatDocumentChunk, RetrievedContext


class _EmbeddingProvider:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # The test only needs deterministic ranking. Lexical scoring in the
        # service then decides which document node is the anchor.
        return [[1.0, 0.0] for _ in texts]


class _TopicEmbeddingProvider:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [
            [1.0, 0.0]
            if "astronomy" in text.casefold()
            else [0.0, 1.0]
            for text in texts
        ]


class _DocumentRepository:
    def __init__(self, chunks: list[ChatDocumentChunk], documents=None) -> None:
        self.chunks = chunks
        self.documents = list(documents or [])

    def list_session_chunks(
        self, session_id: str, user_id: int
    ) -> list[ChatDocumentChunk]:
        return self.chunks

    def list_session_documents(self, session_id: str, user_id: int) -> list:
        return self.documents


class _Planner:
    async def plan(self, *args, **kwargs) -> RagQueryPlan:
        return RagQueryPlan(
            needs_rag=True,
            queries=("revenue",),
            reason="document evidence",
            source="llm",
            mode="deck_from_document",
            source_policy="document_preferred",
            include_root=True,
            include_ancestors=True,
            include_siblings=False,
            max_detail_nodes=4,
        )


class _PlannedContextProvider:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def retrieve_many(self, session, queries, **kwargs):
        self.calls.append({"session": session, "queries": queries, **kwargs})
        return RetrievedContext(context="retrieved", citations=[])


def _session() -> ChatSession:
    return ChatSession(
        id="session-1",
        user_id=7,
        project_id=None,
        title=None,
        history_summary=None,
        max_turns=5,
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )


def test_build_chunks_materializes_root_sections_and_detail_nodes():
    structure = [
        {
            "level": 1,
            "title": "Finance",
            "content": "Revenue increased year over year.",
            "children": [
                {
                    "level": 2,
                    "title": "Revenue",
                    "content": "Revenue reached 100 million.",
                    "children": [],
                }
            ],
        }
    ]

    chunks = DocumentRagService._build_chunks(
        structure,
        "# Finance\nRevenue increased year over year.",
        document_title="Annual report",
    )

    root = next(chunk for chunk in chunks if chunk["node_key"] == "root")
    finance_summary = next(
        chunk
        for chunk in chunks
        if chunk["node_key"] == "1" and chunk["node_kind"] == "section_summary"
    )
    revenue_detail = next(
        chunk
        for chunk in chunks
        if chunk["node_key"] == "1.1" and chunk["node_kind"] == "content"
    )

    assert root["level"] == 0
    assert root["parent_node_key"] is None
    assert root["node_kind"] == "root_summary"
    assert finance_summary["parent_node_key"] == "root"
    assert revenue_detail["parent_node_key"] == "1"
    assert "Finance" in root["content"]
    assert "Revenue reached 100 million" in revenue_detail["content"]


def test_build_chunks_keeps_searchable_image_handles_without_local_paths():
    chunks = DocumentRagService._build_chunks(
        [
            {
                "level": 1,
                "title": "Architecture",
                "content": "The system uses a document image.",
                "children": [],
            }
        ],
        "",
        document_title="Technical notes",
        images=[
            {
                "image_id": "doc-1:0",
                "source_path": "/private/static/chatbot_documents/image.png",
                "filename": "architecture.png",
                "section_path": "Architecture",
                "nearby_text": "The architecture diagram.",
            }
        ],
    )

    architecture = next(
        chunk
        for chunk in chunks
        if chunk["node_key"] == "1" and chunk["node_kind"] == "content"
    )
    assert "doc-1:0" in architecture["content"]
    assert "architecture.png" in architecture["content"]
    assert "/private/static" not in architecture["content"]


def test_build_chunks_places_an_image_only_in_its_matching_text_chunk():
    chunks = DocumentRagService._build_chunks(
        [
            {
                "level": 1,
                "title": "Method",
                "content": "Figure 1 shows the complete GRACE processing pipeline.",
                "children": [],
            },
            {
                "level": 1,
                "title": "Results",
                "content": "Accuracy improves on the evaluation benchmark.",
                "children": [],
            },
        ],
        "",
        document_title="Paper",
        images=[
            {
                "image_id": "doc-1:figure-1",
                "filename": "figure-1.png",
                "anchor_text": "Figure 1 shows the complete GRACE processing pipeline.",
                "nearby_text": "Figure 1 shows the complete GRACE processing pipeline.",
                "ordinal": 0,
            }
        ],
    )

    method_chunks = [chunk for chunk in chunks if chunk["node_key"] == "1"]
    results_chunks = [chunk for chunk in chunks if chunk["node_key"] == "2"]
    assert any(
        "document-image://doc-1:figure-1" in chunk["content"]
        for chunk in method_chunks
    )
    assert all(
        "document-image://doc-1:figure-1" not in chunk["content"]
        for chunk in results_chunks
    )


def test_structural_references_normalize_visual_and_table_coordinates():
    assert DocumentRagService._structural_references(
        "Giải thích fig1, Hình 2a và Bảng 4"
    ) == {"visual:1", "visual:2a", "table:4"}


def test_normalized_text_span_maps_compact_ocr_caption_to_source_offsets():
    text = "Before\nFig.1.GRACEconstructionpipeline.Thequestion remains fixed\nAfter"
    fragment = "Fig. 1. GRACE construction pipeline. The question remains fixed"

    span = DocumentRagService._normalized_text_span(text, fragment)

    assert span is not None
    assert text[span[0] : span[1]].startswith("Fig.1.GRACE")


def test_explicit_figure_reference_outweighs_unrelated_semantic_match():
    matching = ChatDocumentChunk(
        id=1,
        document_id="doc-1",
        ordinal=0,
        title="Method",
        section_path="Method",
        content="Fig. 1. GRACE construction pipeline.",
        level=1,
        embedding=[0.0, 1.0],
        node_key="1",
        parent_node_key="root",
        node_kind="content",
    )
    unrelated = ChatDocumentChunk(
        id=2,
        document_id="doc-1",
        ordinal=1,
        title="References",
        section_path="References",
        content="Other material",
        level=1,
        embedding=[1.0, 0.0],
        node_key="2",
        parent_node_key="root",
        node_kind="content",
    )
    service = DocumentRagService(
        _DocumentRepository([]),
        _EmbeddingProvider(),
        preprocessing_service=None,
    )
    refs, _, _ = service._build_tree_index([matching, unrelated])
    scores = {
        ref.chunk.id: service._score_ref("giải thích fig1", [1.0, 0.0], ref)
        for ref in refs
    }

    assert scores[1] > scores[2]


def test_retrieved_chunk_exposes_only_images_present_in_that_chunk():
    chunks = [
        ChatDocumentChunk(
            id=1,
            document_id="doc-1",
            ordinal=0,
            title="Figure 1",
            section_path="Method",
            content=(
                "Figure 1 shows the pipeline.\n"
                "![Pipeline](document-image://doc-1:figure-1)"
            ),
            level=1,
            embedding=[1.0, 0.0],
            node_key="1",
            parent_node_key="root",
            node_kind="content",
        ),
        ChatDocumentChunk(
            id=2,
            document_id="doc-1",
            ordinal=1,
            title="Figure 2",
            section_path="Results",
            content="![Chart](document-image://doc-1:figure-2)",
            level=1,
            embedding=[0.0, 1.0],
            node_key="2",
            parent_node_key="root",
            node_kind="content",
        ),
    ]
    document = SimpleNamespace(
        id="doc-1",
        status="ready",
        images=[
            {"image_id": "doc-1:figure-1", "filename": "figure-1.png"},
            {"image_id": "doc-1:figure-2", "filename": "figure-2.png"},
        ],
    )
    service = DocumentRagService(
        _DocumentRepository(chunks, [document]),
        _EmbeddingProvider(),
        preprocessing_service=None,
    )

    refs = service._image_refs_for_citations(
        session=_session(),
        citations=[{"chunk_id": 1, "document_id": "doc-1"}],
        chunks=chunks,
    )

    assert [ref["image_id"] for ref in refs] == ["doc-1:figure-1"]


def test_targeted_retrieval_keeps_the_matching_node_in_its_tree_context():
    logical_chunks = DocumentRagService._build_chunks(
        [
            {
                "level": 1,
                "title": "Finance",
                "content": "Revenue increased year over year.",
                "children": [
                    {
                        "level": 2,
                        "title": "Revenue",
                        "content": "Revenue reached 100 million.",
                        "children": [],
                    }
                ],
            },
            {
                "level": 1,
                "title": "Operations",
                "content": "Operations remained stable.",
                "children": [],
            },
        ],
        "",
        document_title="Annual report",
    )
    chunks = [
        ChatDocumentChunk(
            id=index + 1,
            document_id="doc-1",
            ordinal=chunk["ordinal"],
            title=chunk["title"],
            section_path=chunk["section_path"],
            content=chunk["content"],
            level=chunk["level"],
            embedding=[1.0, 0.0],
            node_key=chunk["node_key"],
            parent_node_key=chunk["parent_node_key"],
            node_kind=chunk["node_kind"],
        )
        for index, chunk in enumerate(logical_chunks)
    ]
    service = DocumentRagService(
        _DocumentRepository(chunks),
        _EmbeddingProvider(),
        preprocessing_service=None,
    )

    retrieved = asyncio.run(
        service.retrieve_many(
            _session(),
            ["revenue"],
            mode="targeted_section",
            include_root=True,
            include_ancestors=True,
        )
    )

    assert "Annual report" in retrieved.context
    assert "Finance" in retrieved.context
    assert "Revenue reached 100 million" in retrieved.context
    assert any(citation["role"] == "root" for citation in retrieved.citations)
    assert any(citation["role"] == "anchor" for citation in retrieved.citations)


def test_targeted_retrieval_honours_the_detail_node_budget():
    logical_chunks = DocumentRagService._build_chunks(
        [
            {
                "level": 1,
                "title": "Finance",
                "content": "Revenue increased year over year.",
                "children": [
                    {
                        "level": 2,
                        "title": "Revenue",
                        "content": "Revenue reached 100 million.",
                        "children": [],
                    }
                ],
            }
        ],
        "",
        document_title="Annual report",
    )
    chunks = [
        ChatDocumentChunk(
            id=index + 1,
            document_id="doc-1",
            ordinal=chunk["ordinal"],
            title=chunk["title"],
            section_path=chunk["section_path"],
            content=chunk["content"],
            level=chunk["level"],
            embedding=[1.0, 0.0],
            node_key=chunk["node_key"],
            parent_node_key=chunk["parent_node_key"],
            node_kind=chunk["node_kind"],
        )
        for index, chunk in enumerate(logical_chunks)
    ]
    service = DocumentRagService(
        _DocumentRepository(chunks),
        _EmbeddingProvider(),
        preprocessing_service=None,
    )

    retrieved = asyncio.run(
        service.retrieve_many(
            _session(),
            ["revenue"],
            mode="targeted_section",
            include_root=True,
            max_detail_nodes=1,
        )
    )

    assert sum(
        citation["role"] in {"anchor", "detail"}
        for citation in retrieved.citations
    ) <= 1


def test_topic_retrieval_does_not_expand_an_unrelated_document_branch():
    logical_chunks = DocumentRagService._build_chunks(
        [
            {
                "level": 1,
                "title": "Finance",
                "content": "Revenue increased year over year.",
                "children": [],
            },
            {
                "level": 1,
                "title": "Operations",
                "content": "Operations remained stable.",
                "children": [],
            },
        ],
        "",
        document_title="Annual report",
    )
    chunks = [
        ChatDocumentChunk(
            id=index + 1,
            document_id="doc-1",
            ordinal=chunk["ordinal"],
            title=chunk["title"],
            section_path=chunk["section_path"],
            content=chunk["content"],
            level=chunk["level"],
            embedding=[0.0, 1.0],
            node_key=chunk["node_key"],
            parent_node_key=chunk["parent_node_key"],
            node_kind=chunk["node_kind"],
        )
        for index, chunk in enumerate(logical_chunks)
    ]
    service = DocumentRagService(
        _DocumentRepository(chunks),
        _TopicEmbeddingProvider(),
        preprocessing_service=None,
    )

    retrieved = asyncio.run(
        service.retrieve_many(
            _session(),
            ["astronomy"],
            mode="topic_grounded",
            max_detail_nodes=6,
        )
    )

    assert [citation["role"] for citation in retrieved.citations] == ["root"]
    assert "Revenue increased" in retrieved.context
    assert "Revenue reached" not in retrieved.context


def test_chatbot_forwards_the_plan_and_slide_budget_to_tree_retrieval():
    context_provider = _PlannedContextProvider()
    service = ChatbotService(
        repository=object(),
        llm_provider=object(),
        context_provider=context_provider,
        rag_query_planner=_Planner(),
    )

    retrieved, _ = asyncio.run(
        service._retrieve_with_plan(
            session=_session(),
            query="tạo slide từ tài liệu",
            history=[],
            generation_config={
                "provider_model": "test-model",
                "max_tokens": 4096,
                "temperature": 0.6,
                "top_p": 1.0,
            },
            document_attached=True,
            slide_request=True,
            target_slide_count=10,
        )
    )

    assert retrieved.context == "retrieved"
    assert context_provider.calls == [
        {
            "session": _session(),
            "queries": ["revenue"],
            "mode": "deck_from_document",
            "include_root": True,
            "include_ancestors": True,
            "include_siblings": False,
            "max_detail_nodes": 4,
            "target_slide_count": 10,
        }
    ]


def test_chatbot_attachment_fallback_exposes_only_standalone_images():
    class _ContextProvider:
        def list_session_documents(self, session_id, user_id):
            return [
                SimpleNamespace(
                    id="paper",
                    status="ready",
                    original_filename="paper.pdf",
                    images=[{"document_id": "paper", "image_id": "paper:fig-1"}],
                ),
                SimpleNamespace(
                    id="paste",
                    status="ready",
                    original_filename="pasted.png",
                    images=[{"document_id": "paste", "image_id": "paste:source"}],
                ),
            ]

    service = ChatbotService(
        repository=object(),
        llm_provider=object(),
        context_provider=_ContextProvider(),
    )

    refs = service._attached_standalone_image_refs(
        _session(),
        ["paper", "paste"],
    )

    assert [ref["image_id"] for ref in refs] == ["paste:source"]
