"""DuckDuckGo candidate search used before slide generation."""

import json
import logging
import math
import re
import threading
import time
from collections import OrderedDict
from typing import Optional

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# Bounded process-local cache. Search results are intentionally short-lived:
# image providers can change ranking and an unbounded dict would grow forever
# under varied user queries.
_IMAGE_CACHE_TTL_SECONDS = 15 * 60
_IMAGE_CACHE_MAX_ITEMS = 256
_IMAGE_CACHE: OrderedDict[tuple, tuple[float, str]] = OrderedDict()
_IMAGE_CACHE_LOCK = threading.Lock()


def _get_cached_images(key: tuple) -> str | None:
    now = time.monotonic()
    with _IMAGE_CACHE_LOCK:
        cached = _IMAGE_CACHE.pop(key, None)
        if cached is None:
            return None
        created_at, result = cached
        if now - created_at >= _IMAGE_CACHE_TTL_SECONDS:
            return None
        _IMAGE_CACHE[key] = (created_at, result)
        return result


def _cache_images(key: tuple, result: str) -> None:
    with _IMAGE_CACHE_LOCK:
        _IMAGE_CACHE.pop(key, None)
        _IMAGE_CACHE[key] = (time.monotonic(), result)
        while len(_IMAGE_CACHE) > _IMAGE_CACHE_MAX_ITEMS:
            _IMAGE_CACHE.popitem(last=False)


def _to_int(value) -> Optional[int]:
    try:
        if value is None:
            return None
        return int(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _parse_target_dimensions(description: str) -> tuple[Optional[int], Optional[int]]:
    """Extract the first WxH pixel hint from an image parameter description."""
    if not description:
        return None, None
    match = re.search(r"(\d{2,5})\s*[xX\u00d7]\s*(\d{2,5})", description)
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def _target_ratio(layout: str = None, target_width: int = None, target_height: int = None) -> float:
    if target_width and target_height and target_width > 0 and target_height > 0:
        return target_width / target_height
    if layout == "Tall":
        return 3 / 4
    if layout == "Square":
        return 1.0
    return 16 / 9


def _minimum_max_dimension(size: str = None) -> int:
    if size == "Small":
        return 200
    if size == "Medium":
        return 400
    return 900


def _layout_penalty(width: int, height: int, layout: str = None) -> float:
    if not width or not height:
        return 2.0
    ratio = width / height
    if layout == "Tall":
        return 0.0 if height > width else 4.0
    if layout == "Wide":
        return 0.0 if width > height else 4.0
    if layout == "Square":
        return 0.0 if 0.80 <= ratio <= 1.25 else 3.0
    return 0.0


def _rank_image_results(
    results: list[dict],
    *,
    target_description: str = None,
    layout: str = None,
    size: str = None,
) -> list[dict]:
    """
    Prefer DDGS results whose metadata fits the selected image slot.

    DuckDuckGo supports coarse filters such as layout/size, but not exact
    960x1080-style constraints. Its results include width/height metadata, so
    rank locally after search and keep the best URLs first.
    """
    target_width, target_height = _parse_target_dimensions(target_description or "")
    ratio_goal = _target_ratio(layout, target_width, target_height)
    min_dimension = _minimum_max_dimension(size)
    explicit_max_dimension = max(target_width or 0, target_height or 0)

    def score(item_with_index: tuple[int, dict]) -> float:
        index, item = item_with_index
        width = _to_int(item.get("width"))
        height = _to_int(item.get("height"))
        if not width or not height:
            return 100.0 + index

        ratio = width / height
        ratio_penalty = abs(math.log(max(ratio, 0.01) / ratio_goal)) * 6.0
        orientation_penalty = _layout_penalty(width, height, layout)

        max_dimension = max(width, height)
        size_penalty = 0.0
        if max_dimension < min_dimension:
            size_penalty += (min_dimension - max_dimension) / min_dimension * 6.0
        if explicit_max_dimension and max_dimension < explicit_max_dimension * 0.70:
            size_penalty += 4.0

        return ratio_penalty + orientation_penalty + size_penalty + (index * 0.02)

    return [
        item
        for _, item in sorted(
            enumerate(results),
            key=score,
        )
    ]


def search_ddgs_images(
    query: str,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    timelimit: str = None,
    size: str = None,
    color: str = None,
    type_image: str = "photo",
    layout: str = None,
    license_image: str = None,
    max_results: int = 5,
    target_description: str = None,
    raise_on_error: bool = False,
    backend: str | None = None,
):
    """
    Search and return a JSON list of real image URLs from DuckDuckGo.
    """
    cache_key = (
        query.lower().strip(),
        region,
        safesearch,
        timelimit,
        size,
        color,
        type_image,
        layout,
        license_image,
        max_results,
        target_description,
        backend,
    )
    cached = _get_cached_images(cache_key)
    if cached is not None:
        logger.info(f"⚡ [CACHE HIT] '{query}'")
        return cached

    search_succeeded = False
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(
                query=query,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                size=size,
                color=color,
                type_image=type_image,
                layout=layout,
                license_image=license_image,
                max_results=max_results,
                **({"backend": backend} if backend else {}),
            ))

        logger.info(f"DDGS search: '{query}' - Found {len(results)} images")

        if results:
            results = _rank_image_results(
                results,
                target_description=target_description,
                layout=layout,
                size=size,
            )
            urls = [res.get("image") for res in results if res.get("image")]
            if urls:
                # Return a bounded candidate set. Relevance is decided by the
                # multimodal verifier; this tool must never invent a fallback
                # image when the provider returns no result.
                res_json = json.dumps(urls[:10], ensure_ascii=False)
                _cache_images(cache_key, res_json)
                return res_json
        search_succeeded = True

    except Exception as e:
        logger.error(f"Lỗi khi gọi DDGS API cho query '{query}': {e}")
        if raise_on_error:
            raise

    # Do not cache transport failures as genuine empty results. Corpus rebuilds
    # request propagation so infrastructure failures cannot silently become
    # no-image training examples.
    empty_result = json.dumps([], ensure_ascii=False)
    if search_succeeded:
        _cache_images(cache_key, empty_result)
    return empty_result
