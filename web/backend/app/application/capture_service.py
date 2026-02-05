"""
Capture Service - Handle slide capture and PDF export
"""
import os
import logging
import zipfile
import uuid
from pathlib import Path
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any
from web.backend.app.config import (
    PROJECT_DIR, CAPTURES_DIR
)
import sys
from web.backend.capture import SlideCapture

logger = logging.getLogger(__name__)


class CaptureService:
    """Service for slide capture operations"""

    def __init__(self, captures_dir: Path, slide_capture=None):
        self.captures_dir = captures_dir
        self.slide_capture = slide_capture
        self.captures_dir.mkdir(parents=True, exist_ok=True)

    def is_available(self) -> bool:
        """Check if capture service is available"""
        return self.slide_capture is not None

    async def capture_single_slide(self, html_content: str, slide_name: str) -> Dict[str, Any]:
        """Capture single slide from HTML content"""
        if not self.is_available():
            raise Exception("Slide capture system not available")

        if not html_content:
            raise ValueError("No HTML content provided")
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{slide_name}_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        output_path = self.captures_dir / filename

        # Generate slide image
        logger.info(f"📸 Capturing slide: {slide_name}")
        await self.slide_capture.generate_slide_from_html(html_content, str(output_path))

        # Return relative path
        relative_path = output_path.relative_to(self.captures_dir.parent)

        return {
            'success': True,
            'image_url': f'/static/{relative_path.as_posix()}',
            'download_url': f'/api/download-capture/{filename}',
            'message': f'Slide "{slide_name}" captured successfully',
            'filename': filename
        }

    async def capture_multiple_slides(self, slides_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Capture multiple slides and return as ZIP"""
        if not self.is_available():
            raise Exception("Slide capture system not available")

        if not slides_data:
            raise ValueError("No slides data provided")

        # Create ZIP file in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            successful_slides = []

            for i, slide_data in enumerate(slides_data):
                html_content = slide_data.get('html_content')
                slide_name = slide_data.get('slide_name', f'slide_{i+1}')

                if html_content:
                    # Create temporary file
                    temp_filename = f"temp_{uuid.uuid4().hex[:8]}.png"
                    temp_path = self.captures_dir / temp_filename

                    try:
                        logger.info(f"📸 Capturing slide {i+1}/{len(slides_data)}: {slide_name}")
                        await self.slide_capture.generate_slide_from_html(html_content, str(temp_path))

                        # Add to ZIP
                        zip_filename = f"{slide_name.replace(' ', '_')}.png"
                        zip_file.write(str(temp_path), zip_filename)
                        successful_slides.append(slide_name)

                        # Clean up temp file
                        temp_path.unlink()

                    except Exception as e:
                        logger.error(f"Error capturing slide {i+1}: {e}")
                        continue

        if not successful_slides:
            raise Exception("No slides could be captured")

        zip_buffer.seek(0)

        # Save ZIP file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"slides_capture_{timestamp}.zip"
        zip_path = self.captures_dir / zip_filename

        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())

        logger.info(f"✅ Successfully captured {len(successful_slides)} slides to ZIP")

        return {
            'success': True,
            'download_url': f'/api/download-capture/{zip_filename}',
            'message': f'Captured {len(successful_slides)} slides successfully',
            'filename': zip_filename,
            'captured_slides': successful_slides
        }

    async def export_slide_to_pdf(self, html_content: str, slide_name: str) -> Dict[str, Any]:
        """Export single slide to PDF"""
        if not self.is_available():
            raise Exception("Slide capture system not available")

        if not html_content:
            raise ValueError("No HTML content provided")

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{slide_name}_{timestamp}_{uuid.uuid4().hex[:8]}.pdf"
        output_path = self.captures_dir / filename

        # Generate slide PDF
        logger.info(f"📄 Exporting slide to PDF: {slide_name}")
        await self.slide_capture.capture_and_export_pdf(html_content, str(output_path))

        return {
            'success': True,
            'download_url': f'/api/download-capture/{filename}',
            'message': f'Slide "{slide_name}" exported to PDF successfully',
            'filename': filename
        }

    async def export_slides_to_pdf(self, slides_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export multiple slides to a single PDF"""
        if not self.is_available():
            raise Exception("Slide capture system not available")

        if not slides_data:
            raise ValueError("No slides data provided")

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"slides_export_{timestamp}.pdf"
        output_path = self.captures_dir / filename

        # Export slides to PDF
        logger.info(f"📄 Exporting {len(slides_data)} slides to PDF")
        await self.slide_capture.capture_slides_and_export_pdf(slides_data, str(output_path))

        logger.info(f"✅ Successfully exported {len(slides_data)} slides to PDF")

        return {
            'success': True,
            'download_url': f'/api/download-capture/{filename}',
            'message': f'Exported {len(slides_data)} slides to PDF successfully',
            'filename': filename
        }

    def get_capture_file(self, filename: str) -> Path:
        """Get capture file path"""
        file_path = self.captures_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        return file_path

    def check_health(self) -> Dict[str, Any]:
        """Check capture system health"""
        if not self.is_available():
            return {
                "healthy": False,
                "message": "Slide capture system not initialized"
            }

        # Check if captures directory is writable
        captures_writable = os.access(self.captures_dir, os.W_OK)

        # Check playwright availability
        try:
            playwright_available = True
        except ImportError:
            playwright_available = False

        health_status = {
            "captures_dir_exists": self.captures_dir.exists(),
            "captures_dir_writable": captures_writable,
            "playwright_available": playwright_available,
            "captures_dir_path": str(self.captures_dir)
        }

        all_ok = all([
            health_status["captures_dir_exists"],
            health_status["captures_dir_writable"],
            health_status["playwright_available"]
        ])

        return {
            "healthy": all_ok,
            "details": health_status,
            "message": "Capture system is ready" if all_ok else "Capture system has issues"
        }


sys.path.insert(0, str(PROJECT_DIR))
slide_capture = SlideCapture()
capture_service = CaptureService(CAPTURES_DIR, slide_capture)