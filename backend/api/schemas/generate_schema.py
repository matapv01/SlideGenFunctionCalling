# File: backend/schemas/generate_schema.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class IdeaStructureRequest(BaseModel):
    title: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)
    content_length: str = "standard" # brief, standard, detailed, extensive
    enable_transition_slides: bool = True
    enable_thank_you_slide: bool = True

class IdeaStructureResponse(BaseModel):
    session_id: str
    filename: str
    slide_count: int
    is_from_idea: bool = True

class DocxPrepareResponse(BaseModel):
    filename: str

class ManualSessionResponse(BaseModel):
    success: bool
    session_id: str
    document_title: str