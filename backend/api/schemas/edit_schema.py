# File: backend/schemas/edit_schema.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal

class DocumentNode(BaseModel):
    """Schema chuẩn khớp với cả logic gộp node của Frontend"""
    node_id: Optional[str] = None
    level: int
    title: str = ""
    content: str = ""
    children: List['DocumentNode'] = []
    is_transition: bool = False

    class Config:
        from_attributes = True

# Cho phép Pydantic hiểu kiểu đệ quy của children
DocumentNode.model_rebuild()

class StructureResponse(BaseModel):
    """Schema trả về cho Frontend hiển thị trình biên tập"""
    document_title: str
    document_text: Optional[str] = ""
    document_structure: List[DocumentNode]
    can_edit: bool = True
    output_format: Literal["xml"] = "xml"

class StructureUpdateRequest(BaseModel):
    """Schema gửi lên khi người dùng nhấn Save hoặc thay đổi cấu trúc"""
    session_id: str
    document_structure: List[DocumentNode]
    intro_slide: Optional[DocumentNode] = None
    output_format: Literal["xml"] = "xml"

class StructureApproveRequest(BaseModel):
    """Schema gửi lên khi người dùng nhấn Approve để bắt đầu tạo slide"""
    session_id: str
    output_format: Literal["xml"] = "xml"

class ApprovedStructureResponse(BaseModel):
    """Schema trả về sau khi Approve (dạng phẳng để đưa vào Workflow)"""
    success: bool
    session_id: str
    document_title: str
    document_outline: List[Dict[str, Any]]
    slide_chunks: List[Dict[str, Any]]
    slide_positions: List[Any]
    slide_context_maps: List[str]
    slide_types: List[str]
    output_format: Literal["xml"] = "xml"
