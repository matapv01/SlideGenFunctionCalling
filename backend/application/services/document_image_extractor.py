"""Extract DOCX image assets together with their document-tree location.

The DOCX converter remains responsible for canonical text/structure.  This
small companion service only reads the package relationships and records where
each embedded image occurred.  It deliberately does not decide relevance;
that decision belongs to the multimodal verifier at slide-generation time.
"""

from __future__ import annotations

import hashlib
import mimetypes
import posixpath
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}
_RID = f"{{{_NS['r']}}}embed"
_MAX_IMAGE_BYTES = 20 * 1024 * 1024


def _safe_name(value: str, fallback: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(value).name).strip("._")
    return clean or fallback


def _paragraph_text(paragraph: ET.Element) -> str:
    return " ".join(
        text.strip()
        for text in paragraph.findall(".//w:t", _NS)
        if text.text and text.text.strip()
    ).strip()


def _heading_level(paragraph: ET.Element) -> int | None:
    style = paragraph.find("./w:pPr/w:pStyle", _NS)
    style_name = str(style.get(f"{{{_NS['w']}}}val") or "") if style is not None else ""
    match = re.search(r"heading\s*([1-9][0-9]*)", style_name, re.IGNORECASE)
    if match:
        return max(1, int(match.group(1)))

    outline = paragraph.find("./w:pPr/w:outlineLvl", _NS)
    if outline is not None:
        try:
            return max(1, int(outline.get(f"{{{_NS['w']}}}val", "0")) + 1)
        except (TypeError, ValueError):
            return None
    return None


def _image_size(paragraph: ET.Element) -> tuple[int | None, int | None]:
    extent = paragraph.find(".//wp:extent", _NS)
    if extent is None:
        return None, None
    try:
        # Word stores drawing dimensions in English Metric Units.  Keeping the
        # original integer units is unnecessary for the verifier; pixels are
        # only a weak visual hint, so a conservative 96-DPI conversion is
        # enough and avoids another image-decoding dependency here.
        width = max(1, round(int(extent.get("cx", "0")) / 9525))
        height = max(1, round(int(extent.get("cy", "0")) / 9525))
        return width, height
    except (TypeError, ValueError):
        return None, None


class DocumentImageExtractor:
    """Extract embedded image occurrences from a private DOCX package."""

    def extract(
        self,
        *,
        docx_path: str | Path,
        document_id: str,
        output_root: str | Path,
    ) -> list[dict[str, Any]]:
        source = Path(docx_path)
        if not source.is_file():
            raise FileNotFoundError(f"DOCX source not found: {source}")

        image_root = Path(output_root) / f"{document_id}_images"
        image_root.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(source) as package:
            try:
                document_xml = ET.fromstring(package.read("word/document.xml"))
                relationship_xml = ET.fromstring(
                    package.read("word/_rels/document.xml.rels")
                )
            except KeyError:
                return []

            relationships: dict[str, str] = {}
            for relationship in relationship_xml.findall("pr:Relationship", _NS):
                rel_id = str(relationship.get("Id") or "")
                target = str(relationship.get("Target") or "")
                if rel_id and target:
                    relationships[rel_id] = target

            paragraphs = document_xml.findall(".//w:body//w:p", _NS)
            paragraph_texts = [_paragraph_text(paragraph) for paragraph in paragraphs]
            section_stack: list[tuple[int, str]] = []
            images: list[dict[str, Any]] = []

            for paragraph_index, paragraph in enumerate(paragraphs):
                text = paragraph_texts[paragraph_index]
                heading_level = _heading_level(paragraph)
                if heading_level is not None and text:
                    while section_stack and section_stack[-1][0] >= heading_level:
                        section_stack.pop()
                    section_stack.append((heading_level, text))

                embedded_ids = [
                    str(blip.get(_RID) or "").strip()
                    for blip in paragraph.findall(".//a:blip", _NS)
                ]
                embedded_ids = [rid for rid in embedded_ids if rid]
                if not embedded_ids:
                    continue

                section_titles = [title for _, title in section_stack]
                section_path = " > ".join(section_titles)
                previous_text = next(
                    (
                        paragraph_texts[index]
                        for index in range(paragraph_index - 1, -1, -1)
                        if paragraph_texts[index]
                    ),
                    "",
                )
                next_text = next(
                    (
                        paragraph_texts[index]
                        for index in range(paragraph_index + 1, len(paragraph_texts))
                        if paragraph_texts[index]
                    ),
                    "",
                )
                nearby_text = " ".join(
                    part for part in (text, previous_text, next_text) if part
                )[:1800]
                width, height = _image_size(paragraph)

                for rid in embedded_ids:
                    target = relationships.get(rid, "")
                    package_target = target.replace("\\", "/").lstrip("/")
                    package_path = posixpath.normpath(
                        package_target
                        if package_target.startswith("word/")
                        else posixpath.join("word", package_target)
                    )
                    if not package_path.startswith("word/media/"):
                        continue
                    try:
                        image_bytes = package.read(package_path)
                    except KeyError:
                        continue
                    if not image_bytes or len(image_bytes) > _MAX_IMAGE_BYTES:
                        continue

                    ordinal = len(images)
                    original_name = Path(package_path).name
                    suffix = Path(original_name).suffix.lower() or ".img"
                    file_name = f"{ordinal:04d}_{_safe_name(original_name, f'image{ordinal}{suffix}')}"
                    destination = image_root / file_name
                    destination.write_bytes(image_bytes)
                    digest = hashlib.sha256(image_bytes).hexdigest()
                    mime_type = mimetypes.guess_type(original_name)[0] or "application/octet-stream"
                    images.append(
                        {
                            "image_id": f"{document_id}:{ordinal}",
                            "document_id": document_id,
                            "ordinal": ordinal,
                            "source_path": str(destination),
                            "filename": original_name,
                            "mime_type": mime_type,
                            "content_hash": digest,
                            "section_path": section_path,
                            "section_title": section_titles[-1] if section_titles else "",
                            "nearby_text": nearby_text,
                            "width": width,
                            "height": height,
                        }
                    )

        return images

    @staticmethod
    def remove_assets(images: list[dict[str, Any]]) -> None:
        """Remove extracted files after their owning document is detached."""
        roots: set[Path] = set()
        for image in images or []:
            raw_path = str(image.get("source_path") or "").strip()
            if not raw_path:
                continue
            path = Path(raw_path)
            roots.add(path.parent)
        for root in roots:
            try:
                shutil.rmtree(root)
            except FileNotFoundError:
                continue
            except OSError:
                # File cleanup is best effort; the document row is already
                # detached and a later maintenance pass can remove leftovers.
                continue
