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
    Service chuyên trách chạy 'SlideGen Workflow'.
    Nhiệm vụ: Nhận (DOCX hoặc Chunks) -> Chạy Graphic Engine -> Trả về ZIP (HTML/PNG).
    """

    def __init__(
        self, 
        project_dir: str,
        llm_provider: LLMProvider,
        capture_provider: CaptureProvider,
        parser_provider: ParserProvider,
        tool_retriever: ToolRetrieveProvider
    ):
        super().__init__(project_dir)
        self.llm_provider = llm_provider
        self.capture_provider = capture_provider
        self.parser_provider = parser_provider
        self.tool_retriever = tool_retriever

    def _get_providers(self) -> Dict[str, Any]:
        """Gói các providers cần thiết để inject vào workflow"""
        return {
            "llm_provider": self.llm_provider,
            "capture_provider": self.capture_provider,
            "parser_provider": self.parser_provider,
            "tool_retriever": self.tool_retriever
        }

    async def process_docx(self, docx_path: str, output_folder: str = None, **kwargs) -> Optional[str]:
        """Tạo slide từ file DOCX"""
        from backend.workflows.slidegen_workflow.main import main_workflow

        async def run_logic(output_folder, **kw):
            # Hàm main_workflow trả về đường dẫn file ZIP
            return await main_workflow(
                docx_file=docx_path,
                output_folder=output_folder,
                infra_providers=self._get_providers(),
                router_flags=kw.get('router_flags', False),
                callback=kw.get('callback'),
                slide_options=kw.get('slide_options', {})
            )
        
        raw_result, temp_dir = await self._execute_workflow_logic(run_logic, "docx", **kwargs)
        
        # Nếu hàm main_workflow trả về zip path hợp lệ thì dùng luôn
        if raw_result and isinstance(raw_result, str) and raw_result.endswith('.zip'):
            return raw_result
            
        # Nếu không, thử dùng base service để zip lại folder html
        if temp_dir:
            return self._create_standardized_zip(temp_dir)
            
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

        raw_result, temp_dir = await self._execute_workflow_logic(run_logic, "chunk", **kwargs)
        
        if raw_result and isinstance(raw_result, str) and raw_result.endswith('.zip'):
            return raw_result
            
        if temp_dir:
            return self._create_standardized_zip(temp_dir)
            
        return None