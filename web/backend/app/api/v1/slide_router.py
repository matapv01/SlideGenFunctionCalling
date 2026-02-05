from fastapi import HTTPException, Depends, APIRouter
from web.backend.app.models import UserResponse
from web.backend.app.api.v1.authentication_router import (
    get_current_active_user
)
from web.backend.app.resource.database import (
    get_project, update_project,
    get_project_slides as db_get_project_slides,
    get_project_slides as db_get_project_slides, get_slide,
    update_slide, delete_slide
)
import logging

router = APIRouter(prefix="/slides", tags=["SLIDES"])
logger = logging.getLogger("SlideGen-Slides")

@router.get("/{slide_id}")
async def get_slide_detail(
    slide_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get slide details"""
    slide = get_slide(slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")

    # Verify ownership through project
    project = get_project(slide["project_id"])
    if not project or project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return slide


@router.put("/{slide_id}")
async def update_slide_content(
    slide_id: int,
    slide_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update slide content"""
    slide = get_slide(slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")

    # Verify ownership through project
    project = get_project(slide["project_id"])
    if not project or project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    update_slide(
        slide_id=slide_id,
        title=slide_data.get("title"),
        content_text=slide_data.get("content_text"),
        html_content=slide_data.get("html_content"),
        design_settings=slide_data.get("design_settings")
    )
    return {"message": "Slide updated"}


@router.delete("/{slide_id}")
async def delete_slide_detail(
    slide_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Delete a slide"""
    slide = get_slide(slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")

    # Verify ownership through project
    project = get_project(slide["project_id"])
    if not project or project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    delete_slide(slide_id)

    # Update project slide count
    slides = db_get_project_slides(slide["project_id"])
    update_project(slide["project_id"], slide_count=len(slides))

    return {"message": "Slide deleted"}