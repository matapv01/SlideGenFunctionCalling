import json
from typing import Any, Dict, List, Optional

from backend.application.services.base_workflow_service import BaseWorkflowService
from backend.config import TEMP_DIR
from backend.workflows.manual_workflow.main import run_manual_approve_workflow, run_manual_update_workflow


class ManualWorkflowService(BaseWorkflowService):
    """Service chuyên trách chạy các luồng manual workflow (update/approve)."""

    def get_persisted_structure(self, session_id: str) -> Optional[Dict[str, Any]]:
        file_path = TEMP_DIR / f"structure_{session_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def update_structure(
        self,
        session_id: str,
        document_structure: List[Dict[str, Any]],
        intro_slide: Optional[Dict[str, Any]] = None,
        slide_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        workflow_state = await run_manual_update_workflow(
            session_id=session_id,
            document_structure=document_structure,
            intro_slide=intro_slide,
            slide_options=slide_options or {},
            graph_config={},
        )

        result = workflow_state.get("update_result")
        if not result:
            raise ValueError("Không thể lưu cấu trúc qua manual workflow")
        return result

    async def approve_structure(
        self,
        session_id: str,
        document_title: str,
        document_structure: List[Dict[str, Any]],
        slide_options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        workflow_state = await run_manual_approve_workflow(
            session_id=session_id,
            document_title=document_title,
            document_structure=document_structure,
            slide_options=slide_options or {},
            graph_config={},
        )

        result = workflow_state.get("approved_result")
        if not result:
            raise ValueError("Không thể tạo dữ liệu approve từ manual workflow")
        return result

    async def approve_structure_from_session(self, session_id: str) -> Dict[str, Any]:
        persisted = self.get_persisted_structure(session_id)
        if not persisted:
            raise FileNotFoundError("Không tìm thấy file cấu trúc tạm thời")

        document_title = persisted.get("document_title", "Untitled")
        document_structure = persisted.get("document_structure", [])
        slide_options = {"output_format": persisted.get("output_format", "xml")}

        return await self.approve_structure(
            session_id=session_id,
            document_title=document_title,
            document_structure=document_structure,
            slide_options=slide_options,
        )
