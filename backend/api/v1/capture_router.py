# File: backend/api/v1/capture_router.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from backend.api.schemas.capture_schema import (
    CaptureMultipleSlidesRequest, 
    BatchCaptureResponse
)
from backend.api.dependencies import get_capture_service
from backend.application.services.capture_service import CaptureService
import logging

router = APIRouter(prefix="/capture", tags=["CAPTURE"])
logger = logging.getLogger("SlideGen-Capture")

@router.post("/capture-slides-batch", response_model=BatchCaptureResponse)
async def capture_slides_batch(
    request: CaptureMultipleSlidesRequest,
    service: CaptureService = Depends(get_capture_service)
):
    if not service.is_available():
        raise HTTPException(503, "Dịch vụ chụp không khả dụng")
    try:
        result = await service.capture_multiple_slides(request.slides)
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse({'success': False, 'error': str(e)}, status_code=500)

@router.get("/download-capture/{filename}")
async def download_capture(
    filename: str,
    service: CaptureService = Depends(get_capture_service)
):
    try:
        return FileResponse(service.get_capture_file(filename))
    except FileNotFoundError:
        raise HTTPException(404, "Không tìm thấy tệp")