"""
API Router for slide generation endpoints.
Handles HTTP requests and delegates to application service.
"""

from __future__ import annotations

from fastapi import Request
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from logger import get_logger

from tools.api.helpers.exception_handler import ExceptionHandler

from tools.application import ListToolsService
from tools.shared.utils import get_settings

logger = get_logger(__name__)

settings = get_settings()

tool_router = APIRouter(prefix='/v1')

@tool_router.get(
    '/slides/tools',
    summary="List all available tools",
    tags=["tools"],
)
async def list_all_tools(request: Request):
    """
    Get all available slide generation tools grouped by category.
    
    Categories:
    - intro: Introduction/title slides
    - transitions: Transition/section header slides
    - content: Content body slides
    - team: Team member slides
    - thank_you: Thank you/closing slides
    """
    
    exception_handler = ExceptionHandler(
        logger=logger.bind(),
        service_name=__name__,
    )
    
    try:
        list_tool_service = ListToolsService(
            request=request,
            settings=settings,
        )

    except Exception as e:
        logger.error('Error initializing tool service', extra={'error': str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")
    
    try:
        response = list_tool_service.process()
        
    except Exception as e:
        return exception_handler.handle_exception(
            e=f'Error during application initialization: {str(e)}',
            extra={},
        )
        
    return exception_handler.handle_success(
        jsonable_encoder(
            response,
        )
    )