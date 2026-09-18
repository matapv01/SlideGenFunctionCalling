# File: backend/application/services/slidegen_workflow_service.py

import logging
from typing import Optional, Dict, Any
from backend.domain.ports.llm_provider import LLMProvider
from backend.domain.ports.capture_provider import CaptureProvider
from backend.domain.ports.parser_provider import ParserProvider
from backend.domain.ports.tool_retrieve_provider import ToolRetrieveProvider
from backend.application.services.base_workflow_service import BaseWorkflowService

logger = logging.getLogger(__name__)

class SlideGenWorkflowService(BaseWorkflowService):
    """
    Core XML slide renderer shared by every application entry point.

    Source-specific preparation happens before this service. The renderer
    receives canonical chunks and does not know about DOCX, chatbot, Idea, or
    Manual workflows.
    """

    def __init__(
        self, 
        project_dir: str,
        llm_provider: LLMProvider,
        planner_llm_provider: LLMProvider,
        capture_provider: CaptureProvider,
        parser_provider: ParserProvider,
        tool_retriever: ToolRetrieveProvider,
        image_relevance_verifier: Any | None = None,
    ):
        super().__init__(project_dir)
        self.llm_provider = llm_provider
        self.planner_llm_provider = planner_llm_provider
        self.capture_provider = capture_provider
        self.parser_provider = parser_provider
        self.tool_retriever = tool_retriever
        self.image_relevance_verifier = image_relevance_verifier

    def _get_providers(self) -> Dict[str, Any]:
        """Gói các providers cần thiết để inject vào workflow"""
        return {
            "llm_provider": self.llm_provider,
            "planner_llm_provider": self.planner_llm_provider,
            "capture_provider": self.capture_provider,
            "parser_provider": self.parser_provider,
            "tool_retriever": self.tool_retriever,
            "image_relevance_verifier": self.image_relevance_verifier,
        }

    async def generate_from_chunks(self, slide_chunks: list, title: str, output_folder: str = None, **kwargs) -> Optional[str]:
        """Render canonical slide chunks into the XML project output."""
        from backend.workflows.slidegen_workflow.main import (
            run_canonical_slide_workflow,
        )

        async def run_logic(output_folder, **kw):
            return await run_canonical_slide_workflow(
                slide_chunks=slide_chunks,
                title=title,
                output_folder=output_folder,
                infra_providers=self._get_providers(),
                callback=kw.get('callback'),
                slide_options=kw.get('slide_options', {}),
                slide_positions=kw.get('slide_positions', []),
                slide_context_maps=kw.get('slide_context_maps', []),
                section_ids=kw.get('section_ids', []),
                max_retries_per_slide=kw.get('max_retries_per_slide', 1),
            )

        if output_folder:
            kwargs['output_folder'] = output_folder

        raw_result, _ = await self._execute_workflow_logic(run_logic, "chunk", **kwargs)
        
        if raw_result and isinstance(raw_result, str):
            return raw_result
        return None
