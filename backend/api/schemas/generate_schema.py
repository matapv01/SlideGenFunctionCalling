# File: backend/schemas/generate_schema.py

from pydantic import BaseModel
from typing import Literal

class DocxPrepareResponse(BaseModel):
    filename: str

class ManualSessionResponse(BaseModel):
    success: bool
    session_id: str
    document_title: str
    output_format: Literal["xml"] = "xml"
