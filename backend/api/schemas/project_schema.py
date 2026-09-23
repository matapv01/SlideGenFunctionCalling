# File: backend/schemas/project_schema.py

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

# --- SLIDE SCHEMAS ---

class SlideBase(BaseModel):
    title: str = "Untitled Slide"
    slide_index: int = 0
    slide_type: str = "content" # intro, content, transition, thank_you
    content_text: Optional[str] = None
    html_content: Optional[str] = None
    design_settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SlideCreate(SlideBase):
    """Schema khi Frontend gọi POST /projects/{id}/slides"""
    pass

class SlideUpdate(BaseModel):
    """Schema khi update slide (cho phép update từng phần)"""
    title: Optional[str] = None
    slide_index: Optional[int] = None
    content_text: Optional[str] = None
    html_content: Optional[str] = None
    design_settings: Optional[Dict[str, Any]] = None

class SlideResponse(SlideBase):
    """Schema trả về thông tin slide đầy đủ"""
    id: int
    project_id: int
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- PROJECT SCHEMAS ---

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "draft" # draft, processing, completed, error

class ProjectCreate(BaseModel):
    """Schema khi tạo Project mới"""
    title: str = "Untitled Project"
    description: Optional[str] = None
    source_type: str = "manual" # chatbot, docx, manual
    source_data: Optional[Dict[str, Any]] = None

class ProjectUpdate(BaseModel):
    """Schema update project (VD: đổi tên title)"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    slide_count: Optional[int] = None
    thumbnail_url: Optional[str] = None

class ProjectResponse(ProjectBase):
    """Schema trả về thông tin Project cơ bản"""
    id: int
    user_id: int
    source_type: Optional[str]
    slide_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class ProjectDetailResponse(ProjectResponse):
    """Schema trả về chi tiết Project kèm danh sách Slides"""
    slides: List[SlideResponse] = []
    metadata: Optional[Dict[str, Any]] = {}

class ProjectListResponse(BaseModel):
    """Schema cho danh sách project (Pagination)"""
    projects: List[ProjectResponse]
    total: int

# --- PUBLIC / VIEWER SCHEMAS ---

class ViewerSlideResponse(BaseModel):
    """Schema tối giản cho Viewer (Export/Public View)"""
    id: int
    title: str
    content: str  # Map từ html_content
    type: str     # Map từ slide_type
    index: int
    design_settings: Dict[str, Any]

class ViewerProjectResponse(BaseModel):
    project_name: str
    project_id: int
    slides: List[ViewerSlideResponse]
    count: int

class CreateResourceResponse(BaseModel):
    """Response chuẩn khi tạo mới (Project/Slide)"""
    message: str
    project_id: int
