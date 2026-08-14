# File: backend/api/v1/export_router.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from backend.api.schemas.capture_schema import (
    CaptureSlideItem, 
    CaptureMultipleSlidesRequest, 
)
from backend.api.schemas.export_schema import (
    PDFExportResponse,
    PowerPointExportRequest,
    PowerPointExportResponse,
)
from backend.api.dependencies import get_capture_service
from backend.application.services.capture_service import CaptureService
from backend.config import CAPTURES_DIR, TEMP_DIR
from backend.workflows.slidegen_workflow.utils.rich_text import (
    materialize_math_fields_in_xml,
)
from pathlib import Path
import re
import tempfile
import uuid
import logging

router = APIRouter(prefix="/export", tags=["EXPORT"])
logger = logging.getLogger("SlideGen-export")


def _safe_export_stem(value: str) -> str:
    stem = Path(value or "presentation").stem
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._")
    return stem[:80] or "presentation"


@router.post("/xml-pptx", response_model=PowerPointExportResponse)
async def export_xml_to_powerpoint(request: PowerPointExportRequest):
    """Convert the current XML document to an editable .pptx file."""
    if not request.xml_content.strip():
        raise HTTPException(status_code=400, detail="XML content is empty")

    try:
        # Import lazily so the rest of the API can still boot when the optional
        # PowerPoint dependency is unavailable.
        from backend.infrastructure.converter.convert_universal import XMLSlideConverter
    except Exception as exc:
        logger.exception("PowerPoint converter is unavailable")
        raise HTTPException(
            status_code=503,
            detail=f"PowerPoint converter is unavailable: {exc}",
        ) from exc

    stem = _safe_export_stem(request.file_name)
    filename = f"{stem}_{uuid.uuid4().hex[:8]}.pptx"
    output_path = Path(CAPTURES_DIR) / filename
    Path(CAPTURES_DIR).mkdir(parents=True, exist_ok=True)
    Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)

    try:
        # The editor may send a previously saved XML document in which
        # <math-field> is still text escaped as &lt;math-field&gt;.  Normalize
        # it before the converter parses the document, so the formula renderer
        # receives a real XML node in every export path.
        export_xml = materialize_math_fields_in_xml(request.xml_content)
        if export_xml != request.xml_content:
            logger.info("Materialized escaped math-field nodes before PPTX export")

        with tempfile.TemporaryDirectory(
            dir=str(TEMP_DIR),
            prefix="slidegen_pptx_",
        ) as work_dir:
            xml_path = Path(work_dir) / "presentation.xml"
            xml_path.write_text(export_xml, encoding="utf-8")
            XMLSlideConverter(
                xml_path=xml_path,
                output_path=output_path,
                open_after_convert=False,
            ).convert()

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError("Converter did not create a valid PPTX file")

        logger.info("Created PowerPoint export: %s", output_path)
        return {
            "success": True,
            "download_url": f"/capture/download-capture/{filename}",
            "filename": filename,
            "message": "PowerPoint exported successfully",
        }
    except Exception as exc:
        output_path.unlink(missing_ok=True)
        logger.exception("XML to PowerPoint export failed")
        return {
            "success": False,
            "message": "Could not export PowerPoint",
            "error": str(exc),
        }


@router.post("/slide-pdf", response_model=PDFExportResponse)
async def export_slide_pdf(
    request: CaptureSlideItem,
    service: CaptureService = Depends(get_capture_service)
):
    """Xuất một slide đơn lẻ sang định dạng PDF"""
    if not service.is_available():
        raise HTTPException(status_code=503, detail="Dịch vụ PDF không khả dụng")
    try:
        result = await service.export_slide_to_pdf(request.html_content, request.slide_name)
        return result
    except Exception as e:
        logger.error(f"Lỗi xuất PDF đơn: {e}")
        return {
            "success": False, 
            "message": "Không thể xuất PDF", 
            "error": str(e)
        }


@router.post("/slides-pdf", response_model=PDFExportResponse)
async def export_slides_pdf(
    request: CaptureMultipleSlidesRequest,
    service: CaptureService = Depends(get_capture_service)
):
    """Xuất toàn bộ danh sách slide sang một file PDF duy nhất"""
    if not service.is_available(): raise HTTPException(status_code=503, detail="Dịch vụ PDF không khả dụng")
    try:
        # Giả sử bạn đã thêm hàm export_slides_to_pdf vào CaptureService
        result = await service.export_slides_to_pdf(request.slides)
        return result
    except Exception as e:
        logger.error(f"Lỗi xuất PDF hàng loạt: {e}")
        return {
            "success": False, 
            "message": "Không thể xuất PDF hàng loạt", 
            "error": str(e)
        }
