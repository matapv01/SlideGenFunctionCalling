from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from web.backend.app.config import (
    IMAGE_DIR,
)
import logging

router = APIRouter(prefix="/image-serve", tags=["IMAGE SERVING"])
logger = logging.getLogger("SlideGen-image-serve")

@router.get("/{image_name}")
async def get_image(image_name: str):
    """Serve image files"""
    image_path = IMAGE_DIR / image_name
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)