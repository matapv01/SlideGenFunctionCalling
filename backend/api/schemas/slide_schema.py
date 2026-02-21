# File: backend/domain/schemas/slide_schema.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

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