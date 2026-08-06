"""Build editor payloads from XML workflow artifacts."""

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List

from backend.config import STATIC_DIR

logger = logging.getLogger(__name__)


class SlideService:
    """Service for XML slide operations."""

    def __init__(self, static_dir: Path = STATIC_DIR):
        self.static_dir = static_dir

    def build_slides_from_output(
        self,
        output_folder: str,
        output_format: str = "xml",
    ) -> List[Dict[str, Any]]:
        if str(output_format or "xml").lower() != "xml":
            raise ValueError("This service is XML-only; output_format must be 'xml'.")
        return self.build_xml_slides_from_output(output_folder)

    def build_xml_slides_from_output(self, output_folder: str) -> List[Dict[str, Any]]:
        root_folder = Path(output_folder)
        xml_dir = root_folder / "output" / "xml"
        if not xml_dir.exists():
            xml_dir = root_folder / "xml"
        if not xml_dir.exists():
            raise FileNotFoundError("XML directory not found in output")

        png_dir = root_folder / "output" / "png"
        if not png_dir.exists():
            png_dir = root_folder / "png"

        def slide_index(path: Path):
            match = re.search(r"slide_(\d+)", path.stem)
            return int(match.group(1)) if match else float("inf")

        slides = []
        for index, xml_file in enumerate(sorted(xml_dir.glob("*.xml"), key=slide_index)):
            xml_content = xml_file.read_text(encoding="utf-8")
            metadata = {
                "title": f"Slide {index + 1}",
                "backgroundColor": "white",
                "elements": [],
                "format": "xml",
                "sourceFile": xml_file.name,
            }
            try:
                root = ET.fromstring(xml_content)
                slide_node = root.find("./slide")
                if slide_node is not None:
                    metadata["backgroundColor"] = slide_node.get("background", "white")
                    metadata["canvasWidth"] = root.get("width", "1600")
                    metadata["canvasHeight"] = root.get("height", "900")
            except ET.ParseError as exc:
                logger.warning("Invalid XML in %s: %s", xml_file.name, exc)

            preview_url = None
            png_file = png_dir / f"{xml_file.stem}.png"
            if png_file.exists():
                try:
                    relative_path = png_file.relative_to(self.static_dir)
                    preview_url = f"/static/{relative_path.as_posix()}"
                except ValueError:
                    preview_url = None

            slides.append(
                {
                    "content": xml_content,
                    "xmlContent": xml_content,
                    "type": "xml",
                    "format": "xml",
                    "isConverted": False,
                    "preview": preview_url,
                    "title": metadata["title"],
                    "backgroundColor": metadata["backgroundColor"],
                    "elements": metadata["elements"],
                    "metadata": metadata,
                }
            )

        return slides
