# File: backend/application/services/slidegen_workflow_service.py

import logging
from typing import Optional, Dict, Any
from backend.domain.ports.llm_provider import LLMProvider
from backend.domain.ports.capture_provider import CaptureProvider
from backend.domain.ports.parser_provider import ParserProvider
from backend.domain.ports.tool_retrieve_provider import ToolRetrieveProvider
from backend.application.services.base_workflow_service import BaseWorkflowService
from backend.application.services.doc_workflow_service import DocWorkflowService
from backend.application.services.pdf_workflow_service import PdfWorkflowService

logger = logging.getLogger(__name__)

class SlideGenWorkflowService(BaseWorkflowService):
    """
    Service chuyên trách chạy 'SlideGen Workflow'.
    Nhiệm vụ: Nhận (DOCX hoặc Chunks) -> Chạy Graphic Engine -> Trả về ZIP (HTML/PNG).
    """

    def __init__(
        self, 
        project_dir: str,
        llm_provider: LLMProvider,
        capture_provider: CaptureProvider,
        parser_provider: ParserProvider,
        tool_retriever: ToolRetrieveProvider,
        doc_workflow_service: DocWorkflowService,
        pdf_workflow_service: PdfWorkflowService,
        conversion_service=None
    ):
        super().__init__(project_dir)
        self.llm_provider = llm_provider
        self.capture_provider = capture_provider
        self.parser_provider = parser_provider
        self.tool_retriever = tool_retriever
        self.doc_workflow_service = doc_workflow_service
        self.pdf_workflow_service = pdf_workflow_service
        self.conversion_service = conversion_service

    def _get_providers(self) -> Dict[str, Any]:
        """Gói các providers cần thiết để inject vào workflow"""
        return {
            "llm_provider": self.llm_provider,
            "capture_provider": self.capture_provider,
            "parser_provider": self.parser_provider,
            "tool_retriever": self.tool_retriever,
            "conversion_service": self.conversion_service
        }

    async def process_docx(self, docx_path: str, output_folder: str = None, **kwargs) -> Optional[str]:
        """Tạo slide từ file DOCX"""
        from backend.workflows.slidegen_workflow.main import main_workflow

        async def run_logic(output_folder, **kw):
            _slide_options = kw.get('slide_options', {})
            _workflow_mode = _slide_options.get('workflow_mode', 'auto_no_heading')
            _stream_callback = kw.get('callback')

            # Step 1: Run dedicated doc_workflow service first.
            doc_state = await self.doc_workflow_service.preprocess_docx(
                docx_file=docx_path,
                workflow_mode=_workflow_mode,
                slide_options=_slide_options,
                callback=_stream_callback,
            )

            # Step 2: Run slidegen_workflow only after doc_workflow finished.
            # Hàm main_workflow trả về đường dẫn file ZIP
            return await main_workflow(
                docx_file=docx_path,
                output_folder=output_folder,
                doc_state=doc_state,
                infra_providers=self._get_providers(),
                router_flags=kw.get('router_flags', False),
                callback=_stream_callback,
                slide_options=_slide_options
            )
        
        if output_folder:
            kwargs['output_folder'] = output_folder
            
        raw_result, temp_dir = await self._execute_workflow_logic(run_logic, "docx", **kwargs)
        
        # Hàm main_workflow giờ trả về folder output thay vì ZIP.
        if raw_result and isinstance(raw_result, str):
            return raw_result
        elif temp_dir:
            return str(temp_dir)
        return None

    async def process_chunks(self, slide_chunks: list, title: str, output_folder: str = None, **kwargs) -> Optional[str]:
        """Tạo slide từ danh sách chunks (Kết quả của Idea Workflow)"""
        from backend.workflows.slidegen_workflow.main import main_workflow_from_chunks

        async def run_logic(output_folder, **kw):
            return await main_workflow_from_chunks(
                slide_chunks=slide_chunks,
                title=title,
                output_folder=output_folder,
                infra_providers=self._get_providers(),
                callback=kw.get('callback'),
                slide_options=kw.get('slide_options', {})
            )

        if output_folder:
            kwargs['output_folder'] = output_folder

        raw_result, temp_dir = await self._execute_workflow_logic(run_logic, "chunk", **kwargs)
        
        if raw_result and isinstance(raw_result, str):
            return raw_result
        elif temp_dir:
            return str(temp_dir)
        return None

    async def process_pdf(self, pdf_path: str, output_folder: str = None, **kwargs) -> Optional[str]:
        """Tạo slide từ file PDF (luồng preprocess PDF riêng)."""
        from backend.workflows.slidegen_workflow.main import main_workflow

        async def run_logic(output_folder, **kw):
            _slide_options = dict(kw.get('slide_options', {}))  # mutable copy
            _workflow_mode = _slide_options.get('workflow_mode', 'auto_no_heading')
            _stream_callback = kw.get('callback')

            # Inject output_folder so pdf_converter.py can write images to the
            # correct final directory (<output_folder>/markdown/images/).
            _slide_options['output_folder'] = output_folder

            # Step 1: Run dedicated pdf_workflow service first.
            doc_state = await self.pdf_workflow_service.preprocess_pdf(
                pdf_file=pdf_path,
                workflow_mode=_workflow_mode,
                slide_options=_slide_options,
                callback=_stream_callback,
            )

            # Step 2: Run slidegen_workflow after pdf_workflow finished.
            return await main_workflow(
                docx_file=pdf_path,  # keep existing slidegen state compatibility
                output_folder=output_folder,
                doc_state=doc_state,
                infra_providers=self._get_providers(),
                router_flags=kw.get('router_flags', False),
                callback=_stream_callback,
                slide_options=_slide_options
            )

        if output_folder:
            kwargs['output_folder'] = output_folder

        raw_result, temp_dir = await self._execute_workflow_logic(run_logic, "pdf", **kwargs)

        if raw_result and isinstance(raw_result, str):
            return raw_result
        elif temp_dir:
            return str(temp_dir)
        return None