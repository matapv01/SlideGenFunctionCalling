from fastapi import Depends, APIRouter
from web.backend.app.models import UserResponse
from web.backend.app.api.v1.authentication_router import (
    get_current_active_user
)
import logging
from web.backend.app.resource.database import (
    get_user_profile, create_or_update_user_profile,
    get_user_settings, create_default_settings, update_user_settings,
)

# ========================== USER PROFILE & SETTINGS ==========================

router = APIRouter(prefix="/profile", tags=["PROFILE"])
logger = logging.getLogger("SlideGen-Profile")

@router.get("/")
async def get_profile(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user profile"""
    profile = get_user_profile(current_user.id)
    if not profile:
        # Return empty profile
        return {
            "user_id": current_user.id,
            "full_name": None,
            "avatar_url": None,
            "bio": None
        }
    return profile


@router.put("/")
async def update_profile(
    profile_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update user profile"""
    create_or_update_user_profile(
        user_id=current_user.id,
        full_name=profile_data.get("full_name"),
        avatar_url=profile_data.get("avatar_url"),
        bio=profile_data.get("bio")
    )
    return {"message": "Profile updated"}


@router.get("/settings")
async def get_settings(current_user: UserResponse = Depends(get_current_active_user)):
    """Get user settings"""
    settings = get_user_settings(current_user.id)
    if not settings:
        # Create default settings
        create_default_settings(current_user.id)
        settings = get_user_settings(current_user.id)
    return settings


@router.put("/settings")
async def update_settings(
    settings_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update user settings"""
    update_user_settings(
        user_id=current_user.id,
        theme=settings_data.get("theme"),
        default_transition_enabled=settings_data.get("default_transition_enabled"),
        default_thank_you_enabled=settings_data.get("default_thank_you_enabled"),
        default_content_length=settings_data.get("default_content_length"),
        language=settings_data.get("language"),
        settings_json=settings_data.get("settings_json")
    )
    return {"message": "Settings updated"}