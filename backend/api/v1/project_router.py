# File: backend/api/v1/project_router.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from backend.api.schemas.auth_schema import UserResponse
from backend.api.schemas.project_schema import (
    ProjectCreate, ProjectUpdate, 
    ProjectDetailResponse, ProjectListResponse,
    SlideCreate, ViewerProjectResponse, CreateResourceResponse
)
from backend.api.dependencies import get_current_active_user, get_project_service
from backend.application.services.project_service import ProjectService
from backend.config import OUTPUT_DIR
from pathlib import Path

router = APIRouter(prefix="/projects", tags=["PROJECTS"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    limit: int = 50,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """List all projects for current user"""
    projects = service.get_user_projects(current_user.id, limit, offset)
    return {"projects": projects, "total": len(projects)}


@router.post("", response_model=CreateResourceResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """Create a new empty project"""
    project_id = service.create_project(current_user.id, project_data)
    return {"project_id": project_id, "message": "Project created"}


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_detail(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """Get project details & metadata"""
    return service.get_project_details(project_id, current_user.id)

@router.get("/{project_id}/markdown")
async def get_project_markdown(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service),
):
    """
    Return extracted Markdown (DOCX/PDF -> Markdown) used for auto-structure.
    """
    details = service.get_project_details(project_id, current_user.id)
    metadata = details.metadata or {}
    md_path = metadata.get("markdown_path")
    if not md_path:
        raise HTTPException(status_code=404, detail="Markdown not found for this project")

    md_file = Path(md_path)
    try:
        resolved = md_file.resolve()
        base = Path(OUTPUT_DIR).resolve()
        if not resolved.is_relative_to(base):
            raise HTTPException(status_code=403, detail="Access denied to markdown file")
    except FileNotFoundError:
        # If resolve() fails because file doesn't exist, handle below.
        pass

    if not md_file.exists() or not md_file.is_file():
        raise HTTPException(status_code=404, detail="Markdown file not found")

    markdown_text = md_file.read_text(encoding="utf-8")
    return JSONResponse({"success": True, "markdown": markdown_text})


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """Update project metadata"""
    service.update_project(project_id, current_user.id, project_data)
    return {"message": "Project updated"}


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """Delete project and all its slides"""
    service.delete_project(project_id, current_user.id)
    return {"message": "Project deleted"}


# --- Nested Resource: Project Slides ---

@router.get("/{project_id}/slides")
async def get_project_slides_list(
    project_id: int,
    limit: int | None = None,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """Get slides belonging to a project. Use limit=1 for preview thumbnail."""
    data = service.get_project_details(project_id, current_user.id)
    slides = data.slides
    if limit is not None and limit > 0:
        slides = slides[:limit]
    return {"slides": slides, "total": len(data.slides)}


@router.post("/{project_id}/slides", response_model=CreateResourceResponse)
async def create_slide(
    project_id: int,
    slide_data: SlideCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service)
):
    """Add a new slide to a project"""
    slide_id = service.create_slide(project_id, current_user.id, slide_data)
    return {"project_id": slide_id, "message": "Slide created"}


@router.get("/by-name/{project_name}/slides", response_model=ViewerProjectResponse)
async def get_project_slides_by_name(
    project_name: str,
    current_user: UserResponse = Depends(get_current_active_user),
    service: ProjectService = Depends(get_project_service),
):
    """
    Get slides for viewer/export by project name (owner only).
    """
    project_id, db_slides = service.get_project_slides_by_name(project_name)
    # Verify the requesting user owns this project
    service.get_project_details(project_id, current_user.id)
    
    # Format for frontend viewer
    slides = []
    for slide in db_slides:
        slides.append({
            "id": slide.id,
            "title": slide.title,
            "content": slide.html_content,
            "type": slide.slide_type,
            "index": slide.slide_index,
            "design_settings": slide.design_settings
        })
    
    return {
        "project_name": project_name,
        "project_id": project_id,
        "slides": slides,
        "count": len(slides)
    }