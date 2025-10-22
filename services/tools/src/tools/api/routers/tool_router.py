from __future__ import annotations

from tools.shared.utils import get_logger
from tools.shared.utils import get_settings

from fastapi import APIRouter
from .v1 import list_tool_router
from .v1 import search_tool_router

logger = get_logger(__name__)
settings = get_settings()

tool_router = APIRouter(prefix='/v1')

tool_router.include_router(
    list_tool_router,
    tags=['tools'],
)

tool_router.include_router(
    search_tool_router,
    tags=['tools'],
)