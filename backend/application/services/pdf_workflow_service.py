from typing import Any, Dict, Optional

from backend.application.services.base_workflow_service import BaseWorkflowService
from backend.domain.ports.llm_provider import LLMProvider
from backend.workflows.pdf_workflow.main import run_pdf_workflow


class PdfWorkflowService(BaseWorkflowService):
    """Service chuyên trách chạy pdf_workflow (preprocess PDF)."""

    def __init__(self, project_dir: str, llm_provider: LLMProvider):
        super().__init__(project_dir)
        self.llm_provider = llm_provider

    async def preprocess_pdf(
        self,
        pdf_file: str,
        workflow_mode: str,
        slide_options: Optional[Dict[str, Any]] = None,
        callback=None,
    ) -> Dict[str, Any]:
        graph_config = {
            "configurable": {
                "llm": self.llm_provider.llm_client,
                "stream_callback": callback,
            },
            "recursion_limit": 500,
        }

        doc_state = await run_pdf_workflow(
            pdf_file=pdf_file,
            workflow_mode=workflow_mode,
            slide_options=slide_options or {},
            graph_config=graph_config,
        )

        if not doc_state or not doc_state.get("slide_chunks"):
            raise ValueError("PDF preprocessing produced no slide chunks")

        return doc_state
