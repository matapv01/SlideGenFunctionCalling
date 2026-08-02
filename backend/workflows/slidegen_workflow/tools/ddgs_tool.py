"""DuckDuckGo image search tool used by the slide execution plan."""

import json
import logging
import math
import re
from typing import Literal, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# Global in-memory cache — 0ms latency on repeated queries
_IMAGE_CACHE = {}


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
    max_results: int = 3,
    target_description: str = None,
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
    )
    if cache_key in _IMAGE_CACHE:
        logger.info(f"⚡ [CACHE HIT] '{query}'")
        return _IMAGE_CACHE[cache_key]

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
                res_json = json.dumps(urls[:3], ensure_ascii=False)
                _IMAGE_CACHE[cache_key] = res_json
                return res_json

    except Exception as e:
        logger.error(f"Lỗi khi gọi DDGS API cho query '{query}': {e}")

    # Fallback nếu DDG chặn (403 Ratelimit)
    fallback_urls = [
        "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg?auto=compress&cs=tinysrgb&w=1600",
        "https://images.pexels.com/photos/317356/pexels-photo-317356.jpeg?auto=compress&cs=tinysrgb&w=1600",
    ]
    logger.info(f"Using fallback image URLs for '{query}'")
    res_fallback_json = json.dumps(fallback_urls, ensure_ascii=False)
    _IMAGE_CACHE[cache_key] = res_fallback_json
    return res_fallback_json


class SearchDDGSImagesInput(BaseModel):
    """Arguments the slide generator is allowed to choose for one image search."""

    query: str = Field(
        ...,
        min_length=1,
        description=(
            "A concise English image query derived from the slide content and "
            "the semantic role of this exact image slot. Use 2-5 concrete nouns "
            "or noun phrases. Do not include URLs, pixel sizes, orientation "
            "words, or generic words such as image, photo, wallpaper, beautiful, "
            "or modern."
        ),
    )
    layout: Optional[Literal["Wide", "Tall", "Square"]] = Field(
        default=None,
        description=(
            "Image orientation derived from the corresponding image parameter "
            "description in the selected slide tool schema. Use Tall for "
            "portrait, vertical, full-height, or height greater than width; "
            "Wide for landscape, horizontal, banner, background, full-width, "
            "or width greater than height; Square for avatar, circle, profile, "
            "logo, icon, square, or near-equal width and height."
        ),
    )
    size: Optional[Literal["Large", "Medium", "Small"]] = Field(
        default="Large",
        description=(
            "Requested image size derived from the image parameter description "
            "and visual importance. Use Large for max dimension >= 900px, hero, "
            "background, full-height, full-width, half-slide, or main feature "
            "images; Medium for cards, portraits, thumbnails, profile/team "
            "photos, or max dimension around 400-899px; Small for icons, logos, "
            "badges, decorations, or max dimension below 400px."
        ),
    )


SEARCH_DDGS_TOOL = StructuredTool.from_function(
    func=search_ddgs_images,
    name="search_ddgs_images",
    description=(
        "Search for one real image needed by a slide. Emit one call for each "
        "image parameter, in the same declaration order as the final slide "
        "HTML tool. All image-search calls must appear after the slide HTML tool."
    ),
    args_schema=SearchDDGSImagesInput,
)
