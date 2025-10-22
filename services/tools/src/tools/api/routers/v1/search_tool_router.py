from __future__ import annotations

from fastapi import Request
from fastapi import APIRouter

from tools.api.helpers import ExceptionHandler
from tools.application import SearchToolService
from tools.application import SearchToolInput

from tools.shared.utils import get_logger
from tools.shared.utils import get_settings

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from tools.shared.utils import _make_serializable_response

settings = get_settings()

logger = get_logger(__name__)

search_tool_router = APIRouter()
 
@search_tool_router.post('/tools/search')
def search_relevant_tool(request: Request, inputs: SearchToolInput) -> JSONResponse:
    
    exception_handler = ExceptionHandler(
        logger=logger.bind(),
        service_name=__name__
    )
    
    try:
        search_tool_service = SearchToolService(
            request=request,
            settings=settings,
        )
        
    except Exception as e:
        logger.error('Error initializing search tool service', extra={'error': str(e)})
        return exception_handler.handle_exception(
            e=f'Error initializing search tool service: {str(e)}',
            extra={},
        )
        
    try:
        response = search_tool_service.process(inputs=inputs)
    except Exception as e:
        return exception_handler.handle_exception(
            e=f'Error during search tool processing: {str(e)}',
            extra={},
        )
        
    return exception_handler.handle_success(
        jsonable_encoder(
            _make_serializable_response(response),
        )
    )