# File: backend/api/v1/slide_router.py

from fastapi import APIRouter, Depends
from backend.api.schemas.auth_schema import UserResponse
from backend.api.schemas.project_schema import SlideResponse, SlideUpdate
from backend.api.dependencies import get_current_active_user, get_project_service
from backend.application.services.project_service import ProjectService

router = APIRouter(prefix="/slides", tags=["SLIDES"])


@router.get("/{slide_id}", response_model=SlideResponse)
async def get_slide_detail(
    slide_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """Get single slide content"""
    return service.get_slide(slide_id, current_user.id)


@router.put("/{slide_id}")
async def update_slide_content(
    slide_id: int,
    slide_data: SlideUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """Update slide content/html/settings"""
    service.update_slide(slide_id, current_user.id, slide_data)
    return {"message": "Slide updated"}


@router.delete("/{slide_id}")
async def delete_slide(
    slide_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """Delete a single slide"""
    service.delete_slide(slide_id, current_user.id)
    return {"message": "Slide deleted"}