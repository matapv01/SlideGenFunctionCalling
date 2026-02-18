# File: backend/api/v1/image_router.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.config import IMAGE_DIR
import logging

router = APIRouter(prefix="/image-serve", tags=["IMAGE SERVING"])
logger = logging.getLogger("SlideGen-image-serve")


@router.get("/{image_name}")
async def get_image(image_name: str):
    """
    Serve an image file from the static image directory.
    """
    image_path = IMAGE_DIR / image_name
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy hình ảnh")
    return FileResponse(image_path)