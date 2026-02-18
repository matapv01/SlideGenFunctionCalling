# File: backend/schemas/export_schema.py

from pydantic import BaseModel
from typing import Optional

class PDFExportResponse(BaseModel):
    """Schema trả về cho Frontend sau khi xuất PDF thành công"""
    success: bool
    download_url: Optional[str] = None
    message: str
    filename: Optional[str] = None
    error: Optional[str] = None