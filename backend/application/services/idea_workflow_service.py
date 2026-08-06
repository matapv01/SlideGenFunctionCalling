# File: backend/application/services/idea_workflow_service.py

import logging
from typing import Dict, Any
from backend.domain.ports.llm_provider import LLMProvider
from backend.application.services.base_workflow_service import BaseWorkflowService

logger = logging.getLogger(__name__)

class IdeaWorkflowService(BaseWorkflowService):
    """
    Service chuyên trách chạy 'Idea Workflow'.
    Nhiệm vụ: Nhận Prompt -> Gọi Agent -> Trả về JSON Structure.
    """

    def __init__(self, project_dir: str, llm_provider: LLMProvider):
        super().__init__(project_dir)
        self.llm_provider = llm_provider

    async def generate_structure_from_idea(
        self, 
        title: str, 
        prompt: str, 
        content_length: str, 
        enable_transition: bool, 
        enable_thank_you: bool
    ) -> Dict[str, Any]:
        """
        Thực thi Idea Workflow để lấy slide chunks.
        """
        # Lazy import để tránh lỗi nếu module chưa sẵn sàng lúc khởi động
        from backend.workflows.idea_workflow.main import run_idea_generation

        async def run_logic(output_folder, **kwargs):
            # Gọi hàm main của idea_workflow
            # Lưu ý: Hàm này trả về Dict (JSON), không phải file Zip
            infra_providers = {"llm_provider": self.llm_provider}
            
            return await run_idea_generation(
                title=title,
                prompt=prompt,
                content_length=content_length,
                enable_transition=enable_transition,
                enable_thank_you=enable_thank_you,
                infra_providers=infra_providers
            )

        # Execute
        result, _ = await self._execute_workflow_logic(run_logic, "idea_gen")
        
        if not result:
            raise ValueError("Idea Workflow returned no result.")
            
        return result
