"""Discover image candidates from planner intents before slide generation."""

from __future__ import annotations

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from langchain_core.runnables import RunnableConfig

from backend.config import IMAGE_SEARCH_MAX_CONCURRENCY, IMAGE_SEARCH_MAX_RESULTS
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.tools.ddgs_tool import search_ddgs_images

logger = logging.getLogger(__name__)


def _parse_urls(raw_result: Any) -> list[str]:
    try:
        values = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
    except (TypeError, ValueError, json.JSONDecodeError):
        return []
    if not isinstance(values, list):
        return []
    urls: list[str] = []
    seen: set[str] = set()
    for value in values:
        url = str(value or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls[:IMAGE_SEARCH_MAX_RESULTS]


def _search_one(index: int, intent_index: int, intent: dict[str, Any]) -> dict[str, Any]:
    query = " ".join(str(intent.get("query") or "").split())[:240]
    if not query:
        return {
            "slide_index": index,
            "intent_index": intent_index,
            "query": "",
            "role": str(intent.get("role") or "illustration"),
            "layout": intent.get("layout"),
            "required": bool(intent.get("required", False)),
            "candidates": [],
            "status": "empty_query",
        }

    try:
        raw = search_ddgs_images(
            query=query,
            layout=intent.get("layout"),
            size="Large",
            max_results=IMAGE_SEARCH_MAX_RESULTS,
        )
        urls = _parse_urls(raw)
        return {
            "slide_index": index,
            "intent_index": intent_index,
            "query": query,
            "role": str(intent.get("role") or "illustration"),
            "layout": intent.get("layout"),
            "required": bool(intent.get("required", False)),
            "candidates": [
                {
                    "source_id": f"search:{index}:{intent_index}:{candidate_index}",
                    "source_type": "search",
                    "source_url": url,
                    "candidate_index": candidate_index,
                }
                for candidate_index, url in enumerate(urls)
            ],
            "status": "candidates_found" if urls else "empty_result",
        }
    except Exception as exc:
        logger.warning("Image search failed for slide %s: %s", index + 1, exc)
        return {
            "slide_index": index,
            "intent_index": intent_index,
            "query": query,
            "role": str(intent.get("role") or "illustration"),
            "layout": intent.get("layout"),
            "required": bool(intent.get("required", False)),
            "candidates": [],
            "status": "search_failed",
            "error": str(exc)[:300],
        }


def search_image_candidates(state: State, config: RunnableConfig) -> State:
    """Execute planner image intents concurrently and store bounded candidates.

    This node performs discovery only. Relevance decisions belong exclusively
    to the verifier node, and no candidate is injected into XML here.
    """
    print("\n---------------- Executing Node: image_candidate_search ----------------")
    started = time.perf_counter()
    options = dict(state.get("slide_options") or {})
    verifier = (config or {}).get("configurable", {}).get("image_relevance_verifier")
    plans = list(state.get("slide_plans") or [])
    if verifier is None or not plans:
        state["image_search_candidates"] = []
        options["image_search_candidates"] = []
        state["slide_options"] = options
        return state

    jobs: list[tuple[int, int, dict[str, Any]]] = []
    for slide_index, plan in enumerate(plans):
        if not isinstance(plan, dict):
            continue
        for intent_index, intent in enumerate(plan.get("image_search_intents") or []):
            if isinstance(intent, dict):
                jobs.append((slide_index, intent_index, intent))

    if not jobs:
        state["image_search_candidates"] = []
        options["image_search_candidates"] = []
        state["slide_options"] = options
        return state

    stream_callback = (config or {}).get("configurable", {}).get("stream_callback")
    if stream_callback:
        stream_callback(
            "status",
            {
                "stage": "image_search",
                "title": "Finding visual candidates",
                "description": f"Searching up to {IMAGE_SEARCH_MAX_RESULTS} candidates per visual intent...",
                "message": "Finding visual candidates",
            },
        )

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(
        max_workers=min(IMAGE_SEARCH_MAX_CONCURRENCY, len(jobs))
    ) as executor:
        futures = [
            executor.submit(_search_one, slide_index, intent_index, intent)
            for slide_index, intent_index, intent in jobs
        ]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda item: (int(item.get("slide_index", 0)), int(item.get("intent_index", 0))))
    state["image_search_candidates"] = results
    options["image_search_candidates"] = results
    state["slide_options"] = options
    print(
        f"  -> Discovered {sum(bool(item.get('candidates')) for item in results)} "
        f"image intent result(s) across {len(results)} intent(s)"
    )
    logger.info(
        "Image candidate search completed in %.2fs (%d intents)",
        time.perf_counter() - started,
        len(results),
    )
    return state
