"""
Pydantic Schemas for API Request/Response
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class CaptureSlideRequest(BaseModel):
    """Request schema for capturing a single slide"""
    html_content: str
    slide_name: str = "slide"


class CaptureMultipleSlidesRequest(BaseModel):
    """Request schema for capturing multiple slides"""
    slides: List[Dict[str, Any]]


class SlideMetadata(BaseModel):
    """Slide metadata schema"""
    title: str
    backgroundColor: str = "white"
    elements: List[Dict[str, Any]] = []


class SlideResponse(BaseModel):
    """Response schema for slide data"""
    content: str
    type: str
    isConverted: bool = False
    preview: Optional[str] = None
    title: str
    backgroundColor: str
    elements: List[Dict[str, Any]]
    metadata: SlideMetadata


class ProjectUploadResponse(BaseModel):
    """Response schema for project upload"""
    slides: List[SlideResponse]
    project_name: str


class ConversionStatusResponse(BaseModel):
    """Response schema for conversion status"""
    project_name: str
    status: str
    has_converted: bool


class HealthCheckResponse(BaseModel):
    """Response schema for health check"""
    healthy: bool
    message: str
    details: Optional[Dict[str, Any]] = None


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


class PDFExportResponse(BaseModel):
    """Response schema for PDF export"""
    success: bool
    download_url: Optional[str] = None
    message: str
    filename: Optional[str] = None
    error: Optional[str] = None
