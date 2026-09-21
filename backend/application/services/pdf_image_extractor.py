"""Extract PDF image objects and their local metadata."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PdfImageExtraction:
    """Image occurrences found in one PDF."""

    image_count: int
    assets: list[dict[str, Any]] = field(default_factory=list)


class PdfImageExtractor:
    """Use PDFium page objects instead of asking an LLM to count images.

    ``image_count`` counts image occurrences placed on pages. If the same
    source image is placed twice, both visible occurrences are counted.
    """

    def __init__(self) -> None:
        # PDFium is not safe to call concurrently from multiple threads. The
        # surrounding service may process documents concurrently, so serialize
        # only the short PDFium section instead of blocking the event loop.
        self._pdfium_lock = threading.Lock()

    def extract(
        self,
        *,
        pdf_path: str | Path,
        document_id: str,
        output_root: str | Path,
    ) -> PdfImageExtraction:
        try:
            import pypdfium2 as pdfium
        except ImportError as exc:  # pragma: no cover - guarded by the lockfile
            raise RuntimeError("pypdfium2 is required to inspect PDF images") from exc

        source = Path(pdf_path)
        image_root = Path(output_root) / f"{document_id}_images"
        assets: list[dict[str, Any]] = []
        image_count = 0
        image_type = pdfium.raw.FPDF_PAGEOBJ_IMAGE
        with self._pdfium_lock:
            pdf = pdfium.PdfDocument(str(source))
            try:
                for page_index in range(len(pdf)):
                    page = pdf.get_page(page_index)
                    try:
                        for page_object in page.get_objects(filter=[image_type]):
                            image_count += 1
                            asset = self._extract_asset(
                                page_object,
                                page_index=page_index,
                                ordinal=image_count - 1,
                                document_id=document_id,
                                image_root=image_root,
                            )
                            if asset is not None:
                                assets.append(asset)
                    finally:
                        page.close()
            finally:
                pdf.close()
        if not assets:
            try:
                image_root.rmdir()
            except OSError:
                # The directory may contain assets from a previous interrupted
                # attempt. Leaving it in place is safer than deleting anything
                # that is not owned by this extraction pass.
                pass
        return PdfImageExtraction(image_count=image_count, assets=assets)

    @staticmethod
    def _extract_asset(
        page_object: Any,
        *,
        page_index: int,
        ordinal: int,
        document_id: str,
        image_root: Path,
    ) -> dict[str, Any] | None:
        image_root.mkdir(parents=True, exist_ok=True)
        destination = image_root / f"{ordinal:04d}.png"
        try:
            page_object.extract(destination, fb_format="png")
            if not destination.is_file() or destination.stat().st_size <= 0:
                return None
            width, height = (0, 0)
            try:
                width, height = page_object.get_px_size()
            except Exception:
                pass
            return {
                "image_id": f"{document_id}:pdf:{ordinal}",
                "document_id": document_id,
                "ordinal": ordinal,
                "source_path": str(destination),
                "relative_path": f"{image_root.name}/{destination.name}",
                "filename": destination.name,
                "mime_type": "image/png",
                "anchor_text": "",
                "section_title": f"Page {page_index + 1}",
                "section_path": f"Page {page_index + 1}",
                "nearby_text": "",
                "alt_text": f"PDF image {ordinal + 1} on page {page_index + 1}",
                "page": page_index + 1,
                "width": int(width or 0),
                "height": int(height or 0),
            }
        except Exception as exc:
            # Counting remains accurate even when one unusual image encoding
            # cannot be decoded. OCR/text processing can still finish.
            logger.warning(
                "Unable to extract PDF image %s on page %s: %s",
                ordinal,
                page_index + 1,
                exc,
            )
            destination.unlink(missing_ok=True)
            return None
