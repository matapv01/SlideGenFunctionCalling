"""
DuckDuckGo Search (DDGS) Tool - Tìm kiếm hình ảnh từ DuckDuckGo
"""
import json
import logging

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# Global in-memory cache — 0ms latency on repeated queries
_IMAGE_CACHE = {}


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
    max_results: int = 3
):
    """
    Search and return a JSON list of real image URLs from DuckDuckGo.

    STEP 1 — PLAN BEFORE CALLING:
    You have already chosen which slide tool to call (e.g. generate_dynamic_intro_slide).
    Before calling that slide tool, do the following:
      a) Read its full parameter schema and identify ALL image parameters (any param whose description mentions URL, image, photo).
      b) For EACH image parameter, call THIS search tool once to get a real URL.
      c) Only AFTER collecting all image URLs, call the slide tool with those URLs filled in.
    Use the description of each image parameter to fill in the search parameters below correctly.

    STEP 2 — Choose `query`: 1-2 English nouns only — the single most prominent subject.
    Examples: 'mountain', 'lion', 'city skyline', 'teamwork', 'ocean'.
    NO adjectives (beautiful, stunning, modern), NO filler words (image, photo, background, wallpaper).

    STEP 3 — Choose `layout` based on image orientation hints in the description:
    - "full-height", "tall", "right side", "left side", "portrait", "vertical" → layout="Tall"
    - "background", "panoramic", "wide", "banner", "full-width", "landscape"  → layout="Wide"
    - "circle", "avatar", "square", "thumbnail", "icon"                       → layout="Square"
    - No hint                                                                  → layout=None

    STEP 4 — Choose `size` based on how large the image appears in the slide:
    - Image fills a large section (e.g., half the slide, full background) → size="Large"
    - Image is medium-sized (e.g., a card image, column image)           → size="Medium"
    - Image is small (e.g., avatar, thumbnail, icon)                     → size="Small"

    STEP 5 — Choose `color` only if the slide has a strong theme color (e.g., all blue slide → color="Blue").
    Otherwise leave color=None.

    STEP 6 — Set `type_image="photo"` for realistic images (default). Use "clipart" or "gif" only if slide explicitly needs it.

    OTHER RULES:
    - Use this tool ONLY when the slide tool has image parameters (image_url, image_url_1, image_url_2, etc.).
    - If a slide requires N images, call this tool N times with separate, specific queries.
    - NEVER call this tool if the slide tool does not accept image arguments.
    """
    cache_key = query.lower().strip()
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
