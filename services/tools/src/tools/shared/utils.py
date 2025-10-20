from __future__ import annotations

import asyncio
import re
from collections.abc import Coroutine
from functools import lru_cache
from typing import List
from typing import Union

from tools.shared.settings import Settings
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
