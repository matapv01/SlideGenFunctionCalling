# File: backend/infrastructure/converter/nodejs_provider.py

import os
import subprocess
import logging
from backend.domain.ports.convert_provider import ConvertProvider
from backend.config import PROJECT_DIR

logger = logging.getLogger(__name__)


class NodeJsConvertProvider(ConvertProvider):
    """
    Infrastructure class để gọi script Node.js (converter.js).
    Nhiệm vụ: Chỉ lo việc chạy lệnh shell 'node converter.js ...'
    """
    def __init__(self):
        self.project_dir = PROJECT_DIR
        self.converter_js = os.path.join(PROJECT_DIR, "backend", "infrastructure", "converter", "converter.js")
        self.node_modules = os.path.join(PROJECT_DIR, "backend", "infrastructure", "converter", "node_modules")


    def check_dependencies(self) -> bool:
        """Kiểm tra xem Node.js và converter.js có sẵn sàng không"""
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            return os.path.exists(self.converter_js) and os.path.exists(self.node_modules)
        except Exception as e:
            logger.error(f"Node.js dependency check failed: {e}")
            return False


    def run_conversion_command(self, input_path: str, output_path: str) -> subprocess.CompletedProcess:
        """Chạy lệnh convert cho 1 file với debug logging đầy đủ"""

        cmd = ['node', self.converter_js, input_path, output_path]
        TIMEOUT_SECONDS = 200

        logger.info("=== NodeJsConvertProvider.run_conversion_command ===")
        logger.info(f"PROJECT_DIR: {self.project_dir}")
        logger.info(f"converter_js exists: {os.path.exists(self.converter_js)}")
        logger.info(f"input_path exists: {os.path.exists(input_path)}")
        logger.info(f"output_path (will create): {output_path}")
        logger.info(f"Command: {' '.join(cmd)}")
        logger.info(f"CWD: {self.project_dir}")

        try:
            process = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                encoding='utf-8',
                errors='ignore'
            )

            logger.info(f"Return code: {process.returncode}")
            logger.info(f"STDOUT:\n{process.stdout}")
            logger.info(f"STDERR:\n{process.stderr}")

            if process.returncode != 0:
                logger.error("Conversion failed!")
            else:
                logger.info("Conversion succeeded!")

            return process

        except subprocess.TimeoutExpired as e:
            logger.error("Conversion timeout!")
            logger.error(f"Command: {' '.join(cmd)}")
            logger.error(f"Timeout: {TIMEOUT_SECONDS}s")
            raise

        except Exception as e:
            logger.exception("Unexpected error during conversion")
            raise