# File: backend/api/v1/export_router.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from backend.api.schemas.capture_schema import (
    CaptureSlideItem, 
    CaptureMultipleSlidesRequest, 
)
from backend.api.schemas.export_schema import PDFExportResponse
from backend.api.dependencies import get_capture_service
from backend.application.services.capture_service import CaptureService
import logging

router = APIRouter(prefix="/export", tags=["EXPORT"])
logger = logging.getLogger("SlideGen-export")


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