# File: backend/domain/schemas/capture_schema.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- INPUT SCHEMAS ---

class CaptureSlideItem(BaseModel):
    """Schema cho từng slide trong danh sách request"""
    html_content: str
    slide_name: str = "slide"
    # Có thể thêm các options khác như width, height nếu cần


class CaptureMultipleSlidesRequest(BaseModel):
    """Request Body cho API capture-slides-batch"""
    slides: List[Dict[str, Any]] 
    # Hoặc chặt chẽ hơn: slides: List[CaptureSlideItem]


# --- OUTPUT SCHEMAS ---

class CaptureResponse(BaseModel):
    """Response schema for slide capture"""
    success: bool
    image_url: Optional[str] = None
    download_url: Optional[str] = None
    message: str
    filename: Optional[str] = None
    error: Optional[str] = None


class BatchCaptureResponse(BaseModel):
    """Response schema for batch capture"""
    success: bool
    download_url: Optional[str] = None
    message: str
    filename: Optional[str] = None
    captured_slides: Optional[List[str]] = None
    error: Optional[str] = None