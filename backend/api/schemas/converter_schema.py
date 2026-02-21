# File: backend/schemas/convert_schema.py

from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class ConvertRequest(BaseModel):
    """Schema input cho API convert"""
    project_name: str

class ConversionResult(BaseModel):
    success: List[str]
    failed: List[str]

class ConversionResponse(BaseModel):
    """Schema output cho API convert"""
    success: bool
    conversion_result: ConversionResult
    message: str

class ConversionStatusResponse(BaseModel):
    """Schema output cho API check status"""
    project_name: str
    status: str # 'not_converted', 'partial', 'completed', 'empty'
    has_converted: bool

class ConverterHealthResponse(BaseModel):
    healthy: bool
    message: str
    details: Optional[Dict[str, Any]] = None