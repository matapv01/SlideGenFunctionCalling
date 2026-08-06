# File: backend/schemas/generate_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class SlideChunk(BaseModel):
    """Individual slide content structure"""
    title: str
    content: str
    slide_type: Optional[str] = "content"

class SlideOptionsBase(BaseModel):
    """Base class for slide generation options"""
    enable_transition_slides: bool = True
    enable_thank_you_slide: bool = True
    output_format: Literal["xml"] = "xml"

class IdeaStructureRequest(SlideOptionsBase):
    title: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)
    content_length: str = "standard" # brief, standard, detailed, extensive

class IdeaStructureResponse(BaseModel):
    session_id: str
    filename: str
    slide_count: int
    is_from_idea: bool = True
    output_format: Literal["xml"] = "xml"

class IdeaStructureDetailResponse(SlideOptionsBase):
    session_id: str
    title: str
    slide_chunks: List[SlideChunk]
    metadata: Optional[Dict[str, Any]] = None

class IdeaStructureUpdateRequest(SlideOptionsBase):
    title: str = Field(..., min_length=1)
    slide_chunks: List[SlideChunk]

class DocxPrepareResponse(BaseModel):
    filename: str

class ManualSessionResponse(BaseModel):
    success: bool
    session_id: str
    document_title: str
    output_format: Literal["xml"] = "xml"
