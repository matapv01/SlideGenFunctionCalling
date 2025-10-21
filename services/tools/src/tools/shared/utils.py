from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from functools import lru_cache

from tools.shared.settings import Settings
from copy import deepcopy

from base import BaseModel

from logger import get_logger

logger = get_logger(__name__)


@lru_cache
def get_settings():
    return Settings()


async def semaphore_gather(
    *coroutines: Coroutine,
    max_coroutines: int,
):
    semaphore = asyncio.Semaphore(max_coroutines)

    async def _wrap_coroutine(coroutine):
        async with semaphore:
            return await coroutine

    return await asyncio.gather(*(_wrap_coroutine(coroutine) for coroutine in coroutines))


def _make_serializable_response(response):
    """Convert input_schema classes into JSON serializable forms."""
    safe_response = deepcopy(response)

    if hasattr(safe_response, "all_tools"):
        for tool_name, tool_info in safe_response.all_tools.items():
            schema = tool_info.get("input_schema")
            if isinstance(schema, type) and issubclass(schema, BaseModel):
                # Convert to JSON schema
                safe_response.all_tools[tool_name]["input_schema"] = schema.model_json_schema()
            else:
                # Fallback to class name
                safe_response.all_tools[tool_name]["input_schema"] = str(schema)

    return safe_response