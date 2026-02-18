# File: backend/application/services/slide_service.py

import re
import logging
from pathlib import Path
from typing import List, Dict, Any
from backend.config import (
    STATIC_DIR, IMAGE_DIR,
)

logger = logging.getLogger(__name__)


class SlideService:
    """Service for slide operations"""

    def __init__(self, static_dir: Path, image_dir: Path):
        self.static_dir = static_dir
        self.image_dir = image_dir

    def build_slides_from_output(self, output_folder: str) -> List[Dict[str, Any]]:
        """Build slides data from output folder"""
        slides = []

        # Prioritize converted slides
        converted_dir = Path(output_folder) / 'converted'
        html_dir = Path(output_folder) / 'html'
        png_dir = Path(output_folder) / 'png'

        # Choose HTML directory
        source_html_dir = converted_dir if converted_dir.exists() else html_dir
        use_converted = converted_dir.exists()

        if not source_html_dir.exists():
            raise FileNotFoundError("HTML directory not found in output")

        logger.info(f"Building slides from {'converted' if use_converted else 'original'} HTML directory")

        # Sort files by slide number (extract "slide_X" pattern)
        def extract_slide_number(filepath):
            """Extract slide number from filename like 'slide_1_0.html' or 'converted_slide_1_0.html'"""
            filename = filepath.stem  # Get filename without extension
            # Match patterns: slide_1, slide_1_0, converted_slide_1, converted_slide_1_0
            match = re.search(r'slide_(\d+)(?:_(\d+))?', filename)
            if match:
                slide_num = int(match.group(1))  # First number (slide index)
                retry_num = int(match.group(2)) if match.group(2) else 0  # Second number (retry attempt)
                return (slide_num, retry_num)
            return (float('inf'), 0)  # Put unmatched files at the end

        html_files = sorted(
            [f for f in source_html_dir.iterdir() if f.suffix == '.html'],
            key=extract_slide_number
        )

        for index, html_file in enumerate(html_files):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix image paths
            content = re.sub(
                r'src="([^"]*)"',
                lambda m: f'src="/api/images/{m.group(1)}"' if not m.group(1).startswith(('http', '/', 'data:')) else m.group(0),
                content
            )

            # Extract metadata
            slide_metadata = self.extract_slide_metadata(content, html_file.name)

            # Find preview image
            preview_url = None
            if use_converted and html_file.name.startswith('converted_'):
                original_name = html_file.name.replace('converted_', '')
                png_file = original_name.replace('.html', '.png')
            else:
                png_file = html_file.name.replace('.html', '.png')

            png_path = png_dir / png_file
            if png_path.exists():
                relative_path = png_path.relative_to(self.static_dir)
                preview_url = f"/static/{relative_path.as_posix()}"

            slides.append({
                "content": content,
                "type": "html" if not use_converted else "html_absolute",
                "isConverted": use_converted,
                "preview": preview_url,
                "title": slide_metadata.get("title", f"Slide {index + 1}"),
                "backgroundColor": slide_metadata.get("backgroundColor", "white"),
                "elements": slide_metadata.get("elements", []),
                "metadata": slide_metadata
            })

        return slides

    def extract_slide_metadata(self, html_content: str, filename: str) -> Dict[str, Any]:
        """Extract metadata from HTML content"""
        metadata = {
            "title": filename.replace('.html', '').replace('slide_', 'Slide '),
            "backgroundColor": "white",
            "elements": []
        }

        try:
            # Extract title from h1, h2 tags
            title_match = re.search(r'<h[12][^>]*>([^<]+)</h[12]>', html_content, re.IGNORECASE)
            if title_match:
                metadata["title"] = title_match.group(1).strip()

            # Extract background color
            bg_match = re.search(r'background(?:-color)?:\s*([^;]+)', html_content)
            if bg_match:
                metadata["backgroundColor"] = bg_match.group(1).strip()

        except Exception as e:
            logger.warning(f"Error extracting metadata from {filename}: {e}")

        return metadata

