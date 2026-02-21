# File: backend/api/v1/profile_router.py

from fastapi import APIRouter, Depends
from backend.api.schemas.auth_schema import UserResponse
from backend.api.schemas.profile_schema import (
    UserProfileResponse, 
    UserProfileUpdate, 
    UserSettingsResponse, 
    UserSettingsUpdate
)
from backend.api.dependencies import get_current_active_user, get_user_service
from backend.application.services.user_service import UserService

router = APIRouter(prefix="/profile", tags=["PROFILE"])


@router.get("/", response_model=UserProfileResponse)
async def get_profile(
    current_user: UserResponse = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """Get current user's profile information"""
    return service.get_profile(current_user.id)


@router.put("/")
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """Update current user's profile information"""
    service.update_profile(current_user.id, profile_data)
    return {"message": "Profile updated successfully"}


@router.get("/settings", response_model=UserSettingsResponse)
async def get_settings(
    current_user: UserResponse = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """Get current user's settings"""
    return service.get_settings(current_user.id)


@router.put("/settings")
async def update_settings(
    settings_data: UserSettingsUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """Update current user's settings"""
    service.update_settings(current_user.id, settings_data)
    return {"message": "Settings updated successfully"}