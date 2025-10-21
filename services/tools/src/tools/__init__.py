from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from tools.api.helpers import LoggingMiddleware
from tools.api.routers import tool_router

from tools.shared.utils import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from litellm import LiteLLMService
from chromadb_client import ChromaDB

from tool_registry import ToolRegistryService

from logger import get_logger
from logger import setup_logging

setup_logging(json_logs=False)
logger = get_logger('api')

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    
    app.state.litellm = LiteLLMService(
        url=settings.litellm.url,
        model=settings.litellm.model,
        embedding_model=settings.litellm.embedding_model,
        frequency_penalty=settings.litellm.frequency_penalty,
        n=settings.litellm.n,
        presence_penalty=settings.litellm.presence_penalty,
        temperature=settings.litellm.temperature,
        top_p=settings.litellm.top_p,
        max_completion_tokens=settings.litellm.max_completion_tokens,
        encoding_format=settings.litellm.encoding_format,
        dimensions=settings.litellm.dimensions,
        max_length=settings.litellm.max_length,
    )

    app.state.chromadb = ChromaDB(
        chromadb_setting=settings.chromadb
    )
    
    app.state.registry = ToolRegistryService()
    
    yield


app = FastAPI(
    lifespan=lifespan,
)

# add middleware to generate correlation id
app.add_middleware(LoggingMiddleware, logger=logger)
app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(
    tool_router,
)


def main() -> None:

    uvicorn.run('tools:app', host='0.0.0.0', port=9229, reload=True)