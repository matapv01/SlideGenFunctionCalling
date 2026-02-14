from fastapi import APIRouter
from .v1.authentication_router import router as auth_router
from .v1.capture_router import router as capture_router
from .v1.converter_router import router as converter_router
from .v1.edit_router import router as edit_router
from .v1.export_router import router as export_router
from .v1.image_router import router as image_router
from .v1.profile_router import router as profile_router
from .v1.slide_generation_router import router as slide_generation_router
from .v1.slide_router import router as slide_router
from .v1.temp_router import router as temp_router
from .v1.upload_router import router as upload_router
from .v1.project_router import router as project_router

def create_router():
    """Create and configure the main API router"""
    router = APIRouter(prefix="/api/v1", tags=["api"])
    
    # Include all v1 endpoints
    router.include_router(auth_router)
    router.include_router(capture_router)
    router.include_router(converter_router)
    router.include_router(edit_router)
    router.include_router(export_router)
    router.include_router(image_router)
    router.include_router(profile_router)
    router.include_router(slide_generation_router)
    router.include_router(slide_router)
    router.include_router(temp_router)
    router.include_router(upload_router)
    router.include_router(project_router)
    
    return router