"""
Conversion Service - Handle HTML slide conversion
EXACT COPY from main_web.py HTMLConverter class
"""
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ConversionService:
    """Service for HTML conversion operations - EXACT COPY from main_web.py"""
    def __init__(self, project_dir: Path):
        self.project_dir = str(project_dir)  # Convert to string like main_web.py
        # converter.js and node_modules now in backend folder
        backend_dir = os.path.join(self.project_dir, "backend")
        self.converter_js = os.path.join(backend_dir, "converter.js")
        self.node_modules = os.path.join(backend_dir, "node_modules")

    def is_available(self) -> bool:
        """Check if conversion service is available"""
        return self.check_dependencies()

    def convert_slides_batch(self, input_folder: Path, output_folder: Path) -> Dict[str, List[str]]:
        """Convert HTML slides using Node.js converter.js - EXACT COPY from main_web.py"""
        # Convert Path to string like main_web.py
        input_folder = str(input_folder)
        output_folder = str(output_folder)

        os.makedirs(output_folder, exist_ok=True)

        result = {'success': [], 'failed': []}
        html_files = [f for f in os.listdir(input_folder) if f.endswith('.html')]

        for html_file in html_files:
            try:
                input_path = os.path.join(input_folder, html_file)
                output_path = os.path.join(output_folder, f"converted_{html_file}")

                # Run converter.js với nhiều phương pháp encoding backup
                cmd = ['node', self.converter_js, input_path, output_path]

                # Thử UTF-8 trước
                try:
                    process = subprocess.run(
                        cmd,
                        cwd=self.project_dir,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        encoding='utf-8',
                        errors='ignore'
                    )
                except UnicodeDecodeError:
                    # Nếu UTF-8 lỗi, thử với cp1252 và ignore errors
                    try:
                        process = subprocess.run(
                            cmd,
                            cwd=self.project_dir,
                            capture_output=True,
                            text=True,
                            timeout=30,
                            encoding='cp1252',
                            errors='ignore'
                        )
                    except UnicodeDecodeError:
                        # Nếu vẫn lỗi, dùng bytes mode
                        process = subprocess.run(
                            cmd,
                            cwd=self.project_dir,
                            capture_output=True,
                            timeout=30
                        )
                        # Convert bytes to string nếu cần
                        if hasattr(process, 'stdout') and isinstance(process.stdout, bytes):
                            process.stdout = process.stdout.decode('utf-8', errors='ignore')
                        if hasattr(process, 'stderr') and isinstance(process.stderr, bytes):
                            process.stderr = process.stderr.decode('utf-8', errors='ignore')

                if process.returncode == 0:
                    result['success'].append(html_file)
                    logger.info(f"Successfully converted: {html_file}")
                else:
                    result['failed'].append(html_file)
                    logger.warning(f"Conversion failed for {html_file}: {process.stderr}")

            except subprocess.TimeoutExpired:
                result['failed'].append(html_file)
                logger.error(f"Conversion timeout for {html_file}")
            except Exception as e:
                result['failed'].append(html_file)
                logger.error(f"Error converting {html_file}: {e}")

        logger.info(f"Conversion completed: {len(result['success'])} success, {len(result['failed'])} failed")
        return result

    def check_dependencies(self) -> bool:
        """Check if Node.js and dependencies are available - EXACT COPY from main_web.py"""
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
            return os.path.exists(self.converter_js) and os.path.exists(self.node_modules)
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
            return False

    def get_conversion_status(self, html_folder: Path, converted_folder: Path) -> str:
        """Get conversion status - EXACT COPY from main_web.py"""
        # Convert Path to string like main_web.py
        html_folder = str(html_folder)
        converted_folder = str(converted_folder)

        if not os.path.exists(converted_folder):
            return "not_converted"

        html_files = [f for f in os.listdir(html_folder) if f.endswith('.html')]
        converted_files = [f for f in os.listdir(converted_folder) if f.endswith('.html')]

        if len(converted_files) >= len(html_files):
            return "completed"
        elif len(converted_files) > 0:
            return "partial"
        else:
            return "not_converted"

    def check_health(self) -> Dict[str, Any]:
        """Check converter system health - EXACT COPY from main_web.py"""
        health_status = {
            "dependencies_ok": self.check_dependencies(),
            "converter_js_exists": os.path.exists(self.converter_js),
            "node_modules_exists": os.path.exists(self.node_modules)
        }

        all_ok = all(health_status.values())

        return {
            "healthy": all_ok,
            "details": health_status,
            "message": "Converter system is ready" if all_ok else "Converter system has issues"
        }
