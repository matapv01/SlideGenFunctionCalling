# File: backend/application/services/base_workflow_service.py

import os
import sys
import logging
import tempfile
import shutil
import zipfile
import uuid
from typing import Callable, Optional, Dict, Any
from backend.config import TEMP_DIR

logger = logging.getLogger(__name__)

class BaseWorkflowService:
    """
    Base Service chứa các logic dùng chung cho mọi Workflow (Idea, SlideGen...):
    - Quản lý thư mục tạm (Temp dirs)
    - Kiểm tra module availability
    - Đóng gói kết quả (Zip)
    """

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.workflow_available = self._check_workflow_availability()

    def _check_workflow_availability(self) -> bool:
        """Kiểm tra xem module workflow có import được không"""
        try:
            parent_dir = os.path.dirname(self.project_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            return True
        except Exception as e:
            logger.warning(f"⚠️ Workflow module not available: {e}")
            return False

    def is_available(self) -> bool:
        return self.workflow_available

    def _create_subdirs(self, base_dir: str):
        """Tạo cấu trúc thư mục chuẩn cho output"""
        subdirs = ["html", "png", "temp_debug", "temp_debug/html", "temp_debug/png"]
        for subdir in subdirs:
            os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)

    def _create_standardized_zip(self, temp_dir: str) -> Optional[str]:
        """
        Tìm kiếm folder 'html' và nén lại theo cấu trúc phẳng.
        Hỗ trợ tìm kiếm trong folder lồng nhau (do cấu trúc output của LangGraph đôi khi thay đổi).
        """
        html_source = os.path.join(temp_dir, "html")
        png_source = os.path.join(temp_dir, "png")
        
        # 1. Kiểm tra folder lồng 'output/html'
        nested_output = os.path.join(temp_dir, "output")
        if not (os.path.exists(html_source) and os.listdir(html_source)):
            if os.path.exists(nested_output):
                nested_html = os.path.join(nested_output, "html")
                if os.path.exists(nested_html) and os.listdir(nested_html):
                    html_source = nested_html
                    png_source = os.path.join(nested_output, "png")
                    logger.info(f"📂 Found nested content in: {html_source}")

        # 2. Nếu vẫn không thấy HTML, fail
        if not os.path.exists(html_source) or not os.listdir(html_source):
            return None

        # 3. Tạo file ZIP
        zip_path = os.path.join(temp_dir, f"slides_final_{uuid.uuid4().hex[:8]}.zip")
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add HTML files
                for f in os.listdir(html_source):
                    if f.endswith('.html'):
                        zipf.write(os.path.join(html_source, f), f"html/{f}")
                
                # Add PNG files if exist
                if os.path.exists(png_source):
                    for f in os.listdir(png_source):
                        if f.endswith('.png'):
                            zipf.write(os.path.join(png_source, f), f"png/{f}")
            
            logger.info(f"📦 Created standardized ZIP at: {zip_path}")
            return zip_path
        except Exception as e:
            logger.error(f"Failed to create standardized zip: {e}")
            return None

    async def _execute_workflow_logic(self, workflow_func: Callable, prefix: str, **kwargs):
        """Wrapper an toàn để thực thi workflow trong môi trường Temp"""
        if not self.workflow_available:
            return None
        
        # Check if output_folder is provided in kwargs
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
            # remove output_folder from kwargs if it exists to avoid duplicate argument error
            kwargs.pop('output_folder', None)
            # pass output_folder to the workflow function
            result = await workflow_func(output_folder=temp_workflow_dir, **kwargs)
            return result, temp_workflow_dir

        except Exception as e:
            logger.error(f"❌ Error executing workflow {prefix}: {e}")
            if is_temp:
                shutil.rmtree(temp_workflow_dir, ignore_errors=True)
            return None, None

    def check_health(self) -> Dict[str, Any]:
        """Kiểm tra sức khỏe chung của module workflow"""
        health = {
            "workflow_available": self.workflow_available,
            "can_import": False,
            "langgraph_installed": False
        }
        if self.workflow_available:
            try:
                # Try dummy import check
                health["can_import"] = True
            except Exception as e:
                health["import_error"] = str(e)

            try:
                import langgraph
                health["langgraph_installed"] = True
                health["langgraph_version"] = getattr(langgraph, "__version__", "unknown")
            except ImportError:
                health["langgraph_installed"] = False
        return health
