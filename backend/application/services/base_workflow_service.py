# File: backend/application/services/base_workflow_service.py

import os
import logging
import tempfile
import shutil
from typing import Callable, Optional, Dict, Any
from backend.config import TEMP_DIR

logger = logging.getLogger(__name__)

class BaseWorkflowService:
    """Shared execution helpers for the document, manual, and slide workflows."""

    def __init__(self, project_dir: str):
        self.project_dir = project_dir

    def is_available(self) -> bool:
        return True

    def _create_subdirs(self, base_dir: str):
        """Tạo cấu trúc thư mục chuẩn cho output"""
        subdirs = ["html", "png", "temp_debug", "temp_debug/html", "temp_debug/png"]
        for subdir in subdirs:
            os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)

    async def _execute_workflow_logic(self, workflow_func: Callable, prefix: str, **kwargs):
        """Wrapper an toàn để thực thi workflow trong môi trường Temp"""
        output_folder = kwargs.get('output_folder')
        is_temp = False

        if output_folder:
            temp_workflow_dir = output_folder
        else:
            os.makedirs(TEMP_DIR, exist_ok=True)
            safe_prefix = f"slidegen_{prefix}_"
            temp_workflow_dir = tempfile.mkdtemp(prefix=safe_prefix, dir=str(TEMP_DIR))
            is_temp = True

        self._create_subdirs(temp_workflow_dir)

        try:
            kwargs.pop('output_folder', None)
            result = await workflow_func(output_folder=temp_workflow_dir, **kwargs)
            return result, temp_workflow_dir

        except Exception as e:
            logger.error(f"❌ Error executing workflow {prefix}: {e}")
            if is_temp:
                shutil.rmtree(temp_workflow_dir, ignore_errors=True)
            # Do not hide the original exception. API/SSE layers need the
            # concrete reason to show the user instead of "Workflow failed".
            raise

    def check_health(self) -> Dict[str, Any]:
        """Kiểm tra sức khỏe chung của module workflow"""
        health = {
            "workflow_available": True,
            "can_import": True,
            "langgraph_installed": False
        }
        try:
            import langgraph
            health["langgraph_installed"] = True
            health["langgraph_version"] = getattr(langgraph, "__version__", "unknown")
        except ImportError:
            pass
        return health
