from fastapi import APIRouter, Depends, Query

from backend.api.dependencies import get_collaboration_service, get_current_active_user
from backend.api.schemas.auth_schema import UserResponse
from backend.api.schemas.collaboration_schema import (
    CollaboratorCreate,
    CollaboratorRoleUpdate,
    CommentCreate,
    CommentUpdate,
    VersionCreate,
)
from backend.application.services.collaboration_service import CollaborationService

router = APIRouter(prefix="/projects", tags=["COLLABORATION"])


@router.get("/{project_id}/collaborators")
async def list_collaborators(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return {"collaborators": service.list_collaborators(project_id, current_user.id)}


@router.post("/{project_id}/collaborators")
async def invite_collaborator(
    project_id: int,
    data: CollaboratorCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return service.invite_collaborator(project_id, current_user.id, data.email, data.role)


@router.patch("/{project_id}/collaborators/{member_id}")
async def update_collaborator(
    project_id: int,
    member_id: int,
    data: CollaboratorRoleUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return service.update_collaborator(project_id, current_user.id, member_id, data.role)


@router.delete("/{project_id}/collaborators/{member_id}")
async def remove_collaborator(
    project_id: int,
    member_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    service.remove_collaborator(project_id, current_user.id, member_id)
    return {"message": "Đã xóa thành viên"}


@router.get("/{project_id}/versions")
async def list_versions(
    project_id: int,
    limit: int = Query(default=50, ge=1, le=200),
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return {"versions": service.list_versions(project_id, current_user.id, limit)}


@router.post("/{project_id}/versions")
async def create_version(
    project_id: int,
    data: VersionCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return service.create_version(project_id, current_user.id, data.snapshot, data.label)


@router.get("/{project_id}/versions/{version_id}")
async def get_version(
    project_id: int,
    version_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return service.get_version(project_id, current_user.id, version_id)


@router.post("/{project_id}/versions/{version_id}/restore")
async def restore_version(
    project_id: int,
    version_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return service.restore_version(project_id, current_user.id, version_id)


@router.get("/{project_id}/comments")
async def list_comments(
    project_id: int,
    include_resolved: bool = True,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return {"comments": service.list_comments(project_id, current_user.id, include_resolved)}


@router.post("/{project_id}/comments")
async def create_comment(
    project_id: int,
    data: CommentCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return service.create_comment(project_id, current_user.id, data.body, data.slide_index, data.element_id)


@router.patch("/{project_id}/comments/{comment_id}")
async def update_comment(
    project_id: int,
    comment_id: int,
    data: CommentUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    return service.update_comment(project_id, current_user.id, comment_id, data.body, data.resolved)


@router.delete("/{project_id}/comments/{comment_id}")
async def delete_comment(
    project_id: int,
    comment_id: int,
    current_user: UserResponse = Depends(get_current_active_user),
    service: CollaborationService = Depends(get_collaboration_service),
):
    service.delete_comment(project_id, current_user.id, comment_id)
    return {"message": "Đã xóa bình luận"}
