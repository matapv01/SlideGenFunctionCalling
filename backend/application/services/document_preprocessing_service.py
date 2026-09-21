"""Application service for turning DOCX files into canonical document data."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from backend.application.services.base_workflow_service import BaseWorkflowService
from backend.application.services.document_image_extractor import DocumentImageExtractor
from backend.config import WORKFLOW_RECURSION_LIMIT
from backend.domain.ports.llm_provider import LLMProvider
from backend.workflows.doc_workflow.main import run_doc_workflow

logger = logging.getLogger(__name__)


class DocumentPreprocessingService(BaseWorkflowService):
    """Prepare DOCX content before either RAG indexing or slide generation.

    The converter is the single place that decides whether a document already
    has headings, contains mixed structured/unstructured regions, or needs a
    whole-document LLM structure pass. Callers do not duplicate that logic.

    Chatbot ingestion uses :meth:`preprocess_for_chatbot`, which deliberately
    has no user-selectable workflow mode and stops after the canonical
    Markdown/JSON artifact plus private embedded-image assets are ready. The old DOCX endpoint is kept
    behind :meth:`preprocess_for_slide_generation` while it is being migrated
    to the same canonical chunk renderer.
    """

    def __init__(
        self,
        project_dir: str,
        llm_provider: LLMProvider,
        llm_request_limiter=None,
    ):
        super().__init__(project_dir)
        self.llm_provider = llm_provider
        self.llm_request_limiter = llm_request_limiter
        self.image_extractor = DocumentImageExtractor()

    async def preprocess_document(
        self,
        docx_file: str,
        *,
        workflow_mode: str = "auto",
        slide_options: Optional[Dict[str, Any]] = None,
        callback=None,
        include_slide_chunks: bool = False,
        document_id: str | None = None,
        image_output_root: str | None = None,
        atomic_section_titles: list[str] | None = None,
    ) -> Dict[str, Any]:
        """Run the canonical DOCX analysis graph.

        ``workflow_mode`` is an internal compatibility input for the legacy
        DOCX API. New application flows use the default automatic scan.
        """
        graph_config = {
            "configurable": {
                "llm": self.llm_provider.llm_client,
                "stream_callback": callback,
                "llm_request_limiter": self.llm_request_limiter,
            },
            "recursion_limit": WORKFLOW_RECURSION_LIMIT,
        }

        doc_state = await run_doc_workflow(
            docx_file=docx_file,
            workflow_mode=workflow_mode,
            slide_options=slide_options or {},
            graph_config=graph_config,
            include_slide_chunks=include_slide_chunks,
            atomic_section_titles=atomic_section_titles,
        )

        if not doc_state or not doc_state.get("plain_text"):
            raise ValueError("Document preprocessing produced no canonical text")

        if document_id and image_output_root:
            try:
                doc_state["document_images"] = self.image_extractor.extract(
                    docx_path=docx_file,
                    document_id=document_id,
                    output_root=image_output_root,
                )
            except Exception:
                # Image extraction is an enrichment step. A malformed drawing
                # relationship must not make otherwise valid DOCX text
                # unavailable to RAG.
                logger.exception("Unable to extract embedded DOCX images")
                doc_state["document_images"] = []

        return doc_state
    async def preprocess_for_chatbot(
        self,
        docx_file: str,
        document_id: str | None = None,
        image_output_root: str | None = None,
        callback=None,
        atomic_section_titles: list[str] | None = None,
    ) -> Dict[str, Any]:
        """Create the canonical document artifact used by chatbot RAG."""
        return await self.preprocess_document(
            docx_file=docx_file,
            callback=callback,
            include_slide_chunks=False,
            document_id=document_id,
            image_output_root=image_output_root,
            atomic_section_titles=atomic_section_titles,
        )

    async def preprocess_for_slide_generation(
        self,
        docx_file: str,
        *,
        workflow_mode: str = "auto_no_heading",
        slide_options: Optional[Dict[str, Any]] = None,
        callback=None,
    ) -> Dict[str, Any]:
        """Prepare legacy DOCX input all the way to canonical slide chunks."""
        doc_state = await self.preprocess_document(
            docx_file=docx_file,
            workflow_mode=workflow_mode,
            slide_options=slide_options,
            callback=callback,
            include_slide_chunks=True,
        )
        if not doc_state.get("slide_chunks"):
            raise ValueError("Document preprocessing produced no slide chunks")
        return doc_state
