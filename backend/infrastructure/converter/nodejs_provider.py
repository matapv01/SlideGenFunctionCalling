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
        self.node_modules = os.path.join(PROJECT_DIR, "node_modules")


    def check_dependencies(self) -> bool:
        """Kiểm tra xem Node.js và converter.js có sẵn sàng không"""
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            return os.path.exists(self.converter_js) and os.path.exists(self.node_modules)
        except Exception as e:
            logger.error(f"Node.js dependency check failed: {e}")
            return False


    def run_conversion_command(self, input_path: str, output_path: str) -> subprocess.CompletedProcess:
        """Chạy lệnh convert cho 1 file"""
        cmd = ['node', self.converter_js, input_path, output_path]
        
        TIMEOUT_SECONDS = 200 # 200 giây, có thể điều chỉnh tùy theo độ phức tạp của slide

        # Thử với UTF-8
        try:
            return subprocess.run(
                cmd, cwd=self.project_dir, capture_output=True, 
                text=True, timeout=TIMEOUT_SECONDS, encoding='utf-8', errors='ignore'
            )
        except UnicodeDecodeError:
            # Fallback sang cp1252 nếu lỗi font/encoding
            try:
                process = subprocess.run(
                    cmd, cwd=self.project_dir, capture_output=True, 
                    text=True, timeout=TIMEOUT_SECONDS, encoding='cp1252', errors='ignore'
                )
                return process
            except UnicodeDecodeError:
                # Nếu vẫn lỗi, dùng bytes mode
                process = subprocess.run(
                    cmd,
                    cwd=self.project_dir,
                    capture_output=True,
                    timeout=TIMEOUT_SECONDS
                )
                # Convert bytes to string nếu cần
                if hasattr(process, 'stdout') and isinstance(process.stdout, bytes):
                    process.stdout = process.stdout.decode('utf-8', errors='ignore')
                if hasattr(process, 'stderr') and isinstance(process.stderr, bytes):
                    process.stderr = process.stderr.decode('utf-8', errors='ignore')
                return process