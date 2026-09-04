from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CollaboratorCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=320)
    role: str = Field(default="viewer", pattern="^(viewer|editor)$")


class CollaboratorRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(viewer|editor)$")


class VersionCreate(BaseModel):
    snapshot: Dict[str, Any]
    label: Optional[str] = Field(default=None, max_length=160)


class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)
    slide_index: Optional[int] = Field(default=None, ge=0)
    element_id: Optional[str] = Field(default=None, max_length=160)


class CommentUpdate(BaseModel):
    body: Optional[str] = Field(default=None, min_length=1, max_length=5000)
    resolved: Optional[bool] = None


class VersionResponse(BaseModel):
    id: int
    project_id: int
    label: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Dict[str, Any] = Field(default_factory=dict)
    snapshot: Optional[Dict[str, Any]] = None


class CollaboratorResponse(BaseModel):
    id: Optional[int] = None
    project_id: int
    user_id: int
    email: str
    name: str
    role: str
    owner: bool = False
    created_at: Optional[datetime] = None


class CommentResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    author: Dict[str, Any] = Field(default_factory=dict)
    body: str
    slide_index: Optional[int] = None
    element_id: Optional[str] = None
    resolved: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
