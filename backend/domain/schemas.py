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


# Structure Editor Schemas
class DocumentNode(BaseModel):
    """Schema for a document structure node"""
    level: int
    title: str
    content: str
    children: List['DocumentNode'] = []
    is_transition: bool = False  # Flag for transition slides


class StructureUpdateRequest(BaseModel):
    """Request schema for updating document structure"""
    session_id: str
    document_structure: List[DocumentNode]
    intro_slide: Optional[DocumentNode] = None  # Optional intro slide (level 0)


class StructureResponse(BaseModel):
    """Response schema for getting document structure"""
    document_title: str
    document_structure: List[DocumentNode]
    can_edit: bool = True


class StructureApproveRequest(BaseModel):
    """Request schema for approving structure"""
    session_id: str


class StateOutputResponse(BaseModel):
    """Response schema matching State output from chunk_organizer"""
    success: bool
    message: str
    session_id: str

    # State fields (matching chunk_organizer output)
    document_title: str
    document_outline: List[Dict[str, Any]]
    slide_chunks: List[str]
    slide_positions: List[List[str]]
    slide_context_maps: List[str]
    slide_types: List[str]  # 'intro', 'transition', 'content', 'thank_you'
