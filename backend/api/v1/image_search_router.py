"""Authenticated image search endpoint backed by the workflow's DDGS tool."""

from __future__ import annotations

import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api.dependencies import get_current_active_user
from backend.api.schemas.auth_schema import UserResponse
from backend.workflows.slidegen_workflow.tools.ddgs_tool import search_ddgs_images


router = APIRouter(prefix="/image-search", tags=["IMAGE SEARCH"])


@router.get("")
def search_images(
    query: str = Query(..., min_length=1, max_length=160),
    layout: Literal["Wide", "Tall", "Square"] | None = Query(default=None),
    size: Literal["Large", "Medium", "Small"] = Query(default="Large"),
    max_results: int = Query(default=12, ge=1, le=20),
    _current_user: UserResponse = Depends(get_current_active_user),
):
    """Search images with the same DuckDuckGo tool used by slide generation."""
    clean_query = query.strip()
    if not clean_query:
        raise HTTPException(status_code=422, detail="Từ khóa tìm ảnh không được để trống")

    raw_result = search_ddgs_images(
        query=clean_query,
        layout=layout,
        size=size,
        max_results=max_results,
    )
    try:
        urls = json.loads(raw_result)
    except (TypeError, json.JSONDecodeError):
        urls = []

    if not isinstance(urls, list):
        urls = []

    # Keep the response intentionally small and remove duplicate URLs returned
    # by search providers or the fallback list.
    unique_urls: list[str] = []
    seen: set[str] = set()
    for value in urls:
        url = str(value or "").strip()
        if url and url not in seen:
            seen.add(url)
            unique_urls.append(url)

    return {
        "query": clean_query,
        "images": [{"url": url} for url in unique_urls[:max_results]],
    }
