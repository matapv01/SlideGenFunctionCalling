# File: backend/api/router.py

from fastapi import APIRouter
from backend.api.v1.authentication_router import router as auth_router
from backend.api.v1.capture_router import router as capture_router
from backend.api.v1.converter_router import router as converter_router
from backend.api.v1.edit_router import router as edit_router
from backend.api.v1.export_router import router as export_router
from backend.api.v1.image_router import router as image_router
from backend.api.v1.profile_router import router as profile_router
from backend.api.v1.generate_router import router as generate_router
from backend.api.v1.slide_router import router as slide_router
from backend.api.v1.temp_router import router as temp_router
from backend.api.v1.project_router import router as project_router
from backend.api.v1.subscription_router import router as subscription_router

def create_router():
    """Create and configure the main API router"""
    router = APIRouter(prefix="/api/v1", tags=["api"])
    
    # Include router for user authentication and profile management
    router.include_router(auth_router)
    router.include_router(project_router)
    router.include_router(profile_router)
    router.include_router(subscription_router)

    # Include router for infrastructure-related endpoints
    router.include_router(capture_router)
    router.include_router(converter_router)

    # Include router for structure editing and slide management
    router.include_router(edit_router)
    router.include_router(export_router)
    router.include_router(image_router)
    router.include_router(slide_router)
    router.include_router(temp_router)

    # Include router for slide generation workflow  
    router.include_router(generate_router)
    
    return router