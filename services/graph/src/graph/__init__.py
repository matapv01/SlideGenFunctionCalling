from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from graph.api.helpers import LoggingMiddleware
from graph.api.routers import graph_router

from graph.shared.utils import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from litellm import LiteLLMService
from logger import get_logger
from logger import setup_logging

setup_logging(json_logs=False)
logger = get_logger('api')

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    
    app.state.litellm_service = LiteLLMService(
        settings=app.state.settings.litellm,
    )
    
    yield


app = FastAPI(
    lifespan=lifespan,
)
origins = [
    'http://localhost',
    'http://localhost:8080',
]


# add middleware to generate correlation id
app.add_middleware(LoggingMiddleware, logger=logger)
app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(
    graph_router,
)


def main() -> None:

    uvicorn.run('graph:app', host='0.0.0.0', port=9527, reload=True)