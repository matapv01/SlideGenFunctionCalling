from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import JSONResponse
from web.backend.app.models import UserResponse
from web.backend.app.api.v1.authentication_router import (
    get_current_active_user
)
from web.backend.app.resource.database import (
    create_project, get_user_projects, get_project, update_project, delete_project,
    get_project_slides as db_get_project_slides,
    create_slide, get_project_slides as db_get_project_slides, get_slide,
    get_all_projects, get_project_metadata
)

import logging

router = APIRouter(prefix="/projects", tags=["PROJECTS"])
logger = logging.getLogger("SlideGen-Projects")

@router.get("/")
async def list_(
    limit: int = 50,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get all projects for current user"""
    projects = get_user_projects(current_user.id, limit, offset)
    return {
        "projects": projects,
        "total": len(projects)
    }


@router.post("/")
async def create_new_project(
    project_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Create new project"""
    project_id = create_project(
        user_id=current_user.id,
        title=project_data.get("title", "Untitled Project"),
        description=project_data.get("description"),
        source_type=project_data.get("source_type", "idea"),
        source_data=project_data.get("source_data")
    )
    return {"project_id": project_id, "message": "Project created"}


@router.get("/{project_id}")
async def get_project_detail(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get project details with slides"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get slides
    slides = db_get_project_slides(project_id)

    # Get metadata
    metadata = get_project_metadata(project_id)

    return {
        "project": project,
        "slides": slides,
        "metadata": metadata
    }


@router.put("/{project_id}")
async def update_project_detail(
    project_id: int,
    project_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update project"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    update_project(
        project_id=project_id,
        title=project_data.get("title"),
        description=project_data.get("description"),
        status=project_data.get("status"),
        slide_count=project_data.get("slide_count"),
        thumbnail_url=project_data.get("thumbnail_url")
    )
    return {"message": "Project updated"}


@router.delete("/{project_id}")
async def delete_project_detail(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Delete project"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    delete_project(project_id)
    return {"message": "Project deleted"}

@router.get("/{project_id}/slides")
async def get_project_slides_list(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get all slides for a project"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    slides = db_get_project_slides(project_id)
    return {"slides": slides, "total": len(slides)}


@router.post("/{project_id}/slides")
async def create_new_slide(
    project_id: int,
    slide_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Create a new slide in a project"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Create slide
    slide_id = create_slide(
        project_id=project_id,
        slide_index=slide_data.get("slide_index", 0),
        slide_type=slide_data.get("slide_type", "content"),
        title=slide_data.get("title"),
        content_text=slide_data.get("content_text"),
        html_content=slide_data.get("html_content"),
        design_settings=slide_data.get("design_settings")
    )

    # Update project slide count
    slides = db_get_project_slides(project_id)
    update_project(project_id, slide_count=len(slides))

    return {"id": slide_id, "message": "Slide created"}

@router.get("/by-name/{project_name}/slides")
async def get_project_slides_by_name(project_name: str):
    """Get slides for a project by name - uses converted HTML from database (public access)"""
    logger.info(f"🔓 Public API: Loading slides for project name: {project_name}")
    try:
        # Find project by title/name
        projects = get_all_projects()
        project = next((p for p in projects if p["title"] == project_name), None)
        
        if not project:
            logger.warning(f"Project not found by name: {project_name}")
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        # Get slides from database (already converted HTML)
        db_slides = db_get_project_slides(project["id"])
        
        if not db_slides:
            raise HTTPException(status_code=404, detail=f"No slides found for project: {project_name}")
        
        # Format for frontend
        slides = []
        for slide in db_slides:
            slides.append({
                "id": slide["id"],
                "title": slide["title"],
                "content": slide["html_content"],  # Already converted HTML
                "type": slide["slide_type"],
                "index": slide["slide_index"]
            })
        
        logger.info(f"✅ Loaded {len(slides)} slides from database for {project_name}")
        return JSONResponse(content={
            "project_name": project_name,
            "project_id": project["id"],
            "slides": slides,
            "count": len(slides)
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting slides for project {project_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))