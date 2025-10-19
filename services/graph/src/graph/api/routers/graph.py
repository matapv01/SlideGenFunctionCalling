from __future__ import annotations

import asyncio

from graph.api.helpers.exception_handler import ExceptionHandler
from fastapi import APIRouter
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import UploadFile
from logger import get_logger

from graph.application import GraphInput
from graph.application import GraphService

from graph.shared.utils import get_settings

graph_router = APIRouter(prefix='/v1')
logger = get_logger(__name__)

settings = get_settings()


@graph_router.post('/graph', response_model=None)
def chatbot(
    request: Request,
    docx_file: UploadFile,
) -> JSONResponse:
    exception_handler = ExceptionHandler(
        logger=logger.bind(),
        service_name=__name__,
    )

    try:
        graph_service = GraphService(request=request, settings=settings)
    except Exception as e:
        return exception_handler.handle_exception(
            e=f'Error during application initialization: {str(e)}',
            extra={},
        )

    try:
        response = asyncio.run(
            graph_service.process(
                inputs=GraphInput(
                    docx_file=docx_file,
                ),
            ),
        )

    except Exception as e:
        return exception_handler.handle_exception(e=str(e), extra={'docx_file': docx_file.filename})

    return exception_handler.handle_success(
        jsonable_encoder(
            response,
        ),
    )