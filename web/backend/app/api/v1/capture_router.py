from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from web.backend.app.schemas import (
    CaptureMultipleSlidesRequest
)
from web.backend.app.application.capture_service import capture_service
import logging

router = APIRouter(prefix="/capture", tags=["CAPTURE"])
logger = logging.getLogger("SlideGen-Capture")

@router.post("/capture-slides-batch")
async def capture_slides_batch(request: CaptureMultipleSlidesRequest):
    """Capture multiple slides and return as ZIP"""
    if capture_service is None or not capture_service.is_available():
        raise HTTPException(status_code=503, detail="Capture service not available")
    
    try:
        result = await capture_service.capture_multiple_slides(request.slides)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Batch capture error: {e}")
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


@router.get("/download-capture/{filename}")
async def download_capture(filename: str):
    """Download captured slide or ZIP file"""
    try:
        if capture_service is None:
            raise HTTPException(status_code=503, detail="Capture service not available")
        
        file_path = capture_service.get_capture_file(filename)
        return FileResponse(
            file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))