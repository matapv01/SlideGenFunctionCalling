# File: backend/application/services/conversion_service.py

import os
import logging
from pathlib import Path
from typing import Dict, Any, List
from backend.config import PROJECT_DIR
from backend.domain.ports.convert_provider import ConvertProvider

logger = logging.getLogger(__name__)


class ConversionService:
    """
    Service quản lý việc chuyển đổi HTML (Absolute Positioning).
    Sử dụng NodeJsConverter (Infra).
    """
    def __init__(self, converter_infra: ConvertProvider):
        self.infra = converter_infra

    def is_available(self) -> bool:
        return self.infra.check_dependencies()

    def convert_slides_batch(self, input_folder: Path, output_folder: Path) -> Dict[str, List[str]]:
        input_str = str(input_folder)
        output_str = str(output_folder)
        os.makedirs(output_str, exist_ok=True)

        result = {'success': [], 'failed': []}
        # Liệt kê file html
        if not os.path.exists(input_str):
            return result
        html_files = [f for f in os.listdir(input_str) if f.endswith('.html')]

        for html_file in html_files:
            input_path = os.path.join(input_str, html_file)
            output_path = os.path.join(output_str, f"converted_{html_file}")

            try:
                # Gọi Infra để chạy lệnh
                process = self.infra.run_conversion_command(input_path, output_path)

                if process.returncode == 0:
                    result['success'].append(html_file)
                    logger.info(f"Converted: {html_file}")
                else:
                    result['failed'].append(html_file)
                    logger.warning(f"Failed {html_file}: {process.stderr}")
            except Exception as e:
                result['failed'].append(html_file)
                logger.error(f"Error {html_file}: {e}")

        return result

    def get_conversion_status(self, html_folder: Path, converted_folder: Path) -> str:
        if not converted_folder.exists(): return "not_converted"
        
        src_files = [f for f in os.listdir(html_folder) if f.endswith('.html')]
        done_files = [f for f in os.listdir(converted_folder) if f.endswith('.html')]

        if not src_files: return "empty"
        if len(done_files) >= len(src_files): return "completed"
        if len(done_files) > 0: return "partial"
        return "not_converted"

    def check_health(self) -> dict:
        is_ok = self.is_available()
        return {
            "healthy": is_ok,
            "message": "Converter ready" if is_ok else "Converter missing dependencies"
        }
