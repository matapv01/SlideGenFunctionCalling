"""Extract PDF image objects and their local metadata."""

from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


_VISUAL_CAPTION_RE = re.compile(
    r"(?im)^[ \t]*(?P<label>"
    r"(?:fig(?:ure)?|hình|image|diagram|chart|biểu\s*đồ)"
    r"\s*\.?\s*(?P<number>\d+(?:[.\-]\d+)*(?:[a-z])?))"
    r"\s*[.:\-–—]\s*(?P<caption>[^\r\n]{3,})"
)


@dataclass(frozen=True)
class PdfImageExtraction:
    """Ordered image blocks extracted from one PDF."""

    assets: list[dict[str, Any]] = field(default_factory=list)


class PdfImageExtractor:
    """Extract raster objects and captioned vector visuals from a PDF.

    PDF figures are frequently composed from paths, text, and several small
    raster objects. Such a figure is not exposed by PDFium as one image
    object. In addition to raw image objects, this extractor therefore renders
    the visual region above a detected caption. The result gives the RAG layer
    one coherent image while preserving the caption as its anchor.
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
        image_type = pdfium.raw.FPDF_PAGEOBJ_IMAGE
        with self._pdfium_lock:
            pdf = pdfium.PdfDocument(str(source))
            try:
                for page_index in range(len(pdf)):
                    page = pdf.get_page(page_index)
                    text_page = None
                    try:
                        try:
                            text_page = page.get_textpage()
                            page_width, page_height = page.get_size()
                        except Exception:
                            text_page = None
                            page_width, page_height = (0.0, 0.0)
                        for page_object in page.get_objects(filter=[image_type]):
                            asset = self._extract_asset(
                                page_object,
                                page_index=page_index,
                                ordinal=len(assets),
                                document_id=document_id,
                                image_root=image_root,
                                text_page=text_page,
                                page_width=float(page_width or 0),
                                page_height=float(page_height or 0),
                            )
                            if asset is not None:
                                assets.append(asset)
                        assets.extend(
                            self._extract_captioned_visuals(
                                page=page,
                                text_page=text_page,
                                page_index=page_index,
                                ordinal_start=len(assets),
                                document_id=document_id,
                                image_root=image_root,
                                page_width=float(page_width or 0),
                                page_height=float(page_height or 0),
                            )
                        )
                    finally:
                        if text_page is not None:
                            text_page.close()
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
        return PdfImageExtraction(assets=assets)

    @staticmethod
    def _caption_occurrences(page_text: str) -> list[dict[str, Any]]:
        """Locate explicit visual captions without assuming document topics."""
        occurrences: list[dict[str, Any]] = []
        for match in _VISUAL_CAPTION_RE.finditer(str(page_text or "")):
            caption = " ".join(match.group(0).split()).strip()
            if not caption:
                continue
            occurrences.append(
                {
                    "start": match.start(),
                    "end": match.end(),
                    "label": " ".join(match.group("label").split()),
                    "number": match.group("number"),
                    "caption": caption,
                }
            )
        return occurrences

    @staticmethod
    def _text_range_bounds(
        text_page: Any,
        start: int,
        end: int,
    ) -> tuple[float, float, float, float] | None:
        boxes: list[tuple[float, float, float, float]] = []
        for index in range(max(0, start), max(start, end)):
            try:
                box = tuple(float(value) for value in text_page.get_charbox(index))
            except Exception:
                continue
            if len(box) == 4:
                boxes.append(box)
        if not boxes:
            return None
        return (
            min(box[0] for box in boxes),
            min(box[1] for box in boxes),
            max(box[2] for box in boxes),
            max(box[3] for box in boxes),
        )

    @staticmethod
    def _visual_crop_bounds(
        caption_bounds: tuple[float, float, float, float],
        *,
        page_width: float,
        page_height: float,
    ) -> tuple[float, float, float, float]:
        """Return a page-space crop containing a caption and its visual."""
        _, caption_bottom, _, caption_top = caption_bounds
        return (
            0.0,
            max(0.0, caption_bottom - page_height * 0.055),
            page_width,
            min(page_height, caption_top + page_height * 0.48),
        )

    @classmethod
    def _extract_captioned_visuals(
        cls,
        *,
        page: Any,
        text_page: Any | None,
        page_index: int,
        ordinal_start: int,
        document_id: str,
        image_root: Path,
        page_width: float,
        page_height: float,
    ) -> list[dict[str, Any]]:
        if text_page is None or page_width <= 0 or page_height <= 0:
            return []
        try:
            char_count = int(text_page.count_chars())
            page_text = str(text_page.get_text_range(0, char_count) or "")
        except Exception:
            return []
        occurrences = cls._caption_occurrences(page_text)
        if not occurrences:
            return []

        try:
            bitmap = page.render(scale=1.5)
            rendered_page = bitmap.to_pil()
        except Exception as exc:
            logger.warning(
                "Unable to render captioned visuals on PDF page %s: %s",
                page_index + 1,
                exc,
            )
            return []

        assets: list[dict[str, Any]] = []
        image_root.mkdir(parents=True, exist_ok=True)
        try:
            rendered_width, rendered_height = rendered_page.size
            for occurrence in occurrences:
                caption_bounds = cls._text_range_bounds(
                    text_page,
                    int(occurrence["start"]),
                    int(occurrence["end"]),
                )
                if caption_bounds is None:
                    continue
                crop_bounds = cls._visual_crop_bounds(
                    caption_bounds,
                    page_width=page_width,
                    page_height=page_height,
                )
                left, bottom, right, top = crop_bounds
                pixel_box = (
                    max(0, int(left / page_width * rendered_width)),
                    max(0, int((page_height - top) / page_height * rendered_height)),
                    min(rendered_width, int(right / page_width * rendered_width)),
                    min(
                        rendered_height,
                        int((page_height - bottom) / page_height * rendered_height),
                    ),
                )
                if pixel_box[2] - pixel_box[0] < 64 or pixel_box[3] - pixel_box[1] < 64:
                    continue
                ordinal = ordinal_start + len(assets)
                destination = image_root / f"{ordinal:04d}_visual.png"
                visual = rendered_page.crop(pixel_box)
                try:
                    visual.save(destination, format="PNG", optimize=True)
                finally:
                    visual.close()
                caption = str(occurrence["caption"])
                assets.append(
                    {
                        "image_id": (
                            f"{document_id}:pdf:visual:"
                            f"{page_index + 1}:{len(assets)}"
                        ),
                        "document_id": document_id,
                        "ordinal": ordinal,
                        "source_path": str(destination),
                        "relative_path": f"{image_root.name}/{destination.name}",
                        "filename": destination.name,
                        "mime_type": "image/png",
                        "anchor_text": caption,
                        "section_title": f"Page {page_index + 1}",
                        "section_path": f"Page {page_index + 1}",
                        "nearby_text": caption,
                        "alt_text": caption,
                        "visual_label": str(occurrence["label"]),
                        "visual_number": str(occurrence["number"]),
                        "page": page_index + 1,
                        "bbox": list(crop_bounds),
                        "block_index": page_index * 1_000_000
                        + max(0, int((page_height - crop_bounds[3]) * 1000)),
                        "width": pixel_box[2] - pixel_box[0],
                        "height": pixel_box[3] - pixel_box[1],
                        "source_kind": "rendered_visual",
                    }
                )
        finally:
            rendered_page.close()
        return assets

    @staticmethod
    def _extract_asset(
        page_object: Any,
        *,
        page_index: int,
        ordinal: int,
        document_id: str,
        image_root: Path,
        text_page: Any | None,
        page_width: float,
        page_height: float,
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
            bounds: tuple[float, float, float, float] | None = None
            try:
                bounds = tuple(float(value) for value in page_object.get_pos())
            except Exception:
                pass
            anchor_text, nearby_text = PdfImageExtractor._spatial_text_context(
                text_page=text_page,
                bounds=bounds,
                page_width=page_width,
                page_height=page_height,
            )
            top = bounds[3] if bounds is not None else page_height
            block_index = page_index * 1_000_000 + max(
                0,
                int((max(page_height, top) - top) * 1000),
            )
            return {
                "image_id": f"{document_id}:pdf:{ordinal}",
                "document_id": document_id,
                "ordinal": ordinal,
                "source_path": str(destination),
                "relative_path": f"{image_root.name}/{destination.name}",
                "filename": destination.name,
                "mime_type": "image/png",
                "anchor_text": anchor_text,
                "section_title": f"Page {page_index + 1}",
                "section_path": f"Page {page_index + 1}",
                "nearby_text": nearby_text,
                "alt_text": anchor_text or f"Image on page {page_index + 1}",
                "page": page_index + 1,
                "bbox": list(bounds) if bounds is not None else None,
                "block_index": block_index,
                "width": int(width or 0),
                "height": int(height or 0),
            }
        except Exception as exc:
            # One unusual image encoding must not block OCR/text processing.
            logger.warning(
                "Unable to extract PDF image %s on page %s: %s",
                ordinal,
                page_index + 1,
                exc,
            )
            destination.unlink(missing_ok=True)
            return None

    @staticmethod
    def _spatial_text_context(
        *,
        text_page: Any | None,
        bounds: tuple[float, float, float, float] | None,
        page_width: float,
        page_height: float,
    ) -> tuple[str, str]:
        """Return the closest readable text around an image occurrence.

        This is layout based rather than figure-name based: it works for
        figures, charts, screenshots, photographs, and any other image block.
        The closest text below is preferred as the insertion anchor, followed
        by text above and text overlapping the image bounds.
        """
        if text_page is None or bounds is None or page_width <= 0 or page_height <= 0:
            return "", ""

        left, bottom, right, top = bounds
        margin = max(36.0, min(144.0, page_height * 0.18))

        def bounded(box: tuple[float, float, float, float]) -> str:
            try:
                value = text_page.get_text_bounded(*box)
            except Exception:
                return ""
            lines = [
                " ".join(line.split()).strip()
                for line in str(value or "").replace("\r", "\n").split("\n")
            ]
            return "\n".join(line for line in lines if line).strip()

        below = bounded((0.0, max(0.0, bottom - margin), page_width, bottom))
        above = bounded((0.0, top, page_width, min(page_height, top + margin)))
        overlap = bounded(
            (
                max(0.0, left),
                max(0.0, bottom),
                min(page_width, right),
                min(page_height, top),
            )
        )
        candidates = [value for value in (above, overlap, below) if value]
        unique: list[str] = []
        seen: set[str] = set()
        for value in candidates:
            key = value.casefold()
            if key in seen:
                continue
            seen.add(key)
            unique.append(value)
        if below:
            anchor_lines = below.splitlines()
            anchor = anchor_lines[0].strip() if anchor_lines else ""
        elif above:
            anchor_lines = above.splitlines()
            anchor = anchor_lines[-1].strip() if anchor_lines else ""
        else:
            anchor_lines = overlap.splitlines()
            anchor = anchor_lines[0].strip() if anchor_lines else ""
        return anchor[:500], "\n".join(unique)[:1800]
