from typing import Any, Dict, List


def _is_intro_slide(chunk: Dict[str, Any], index: int, intro_mode: str) -> bool:
    heading = str(chunk.get("heading", "")).upper()
    position = chunk.get("position", -99)
    slide_type = str(chunk.get("slide_type", "")).lower()

    if intro_mode == "first_slide":
        return index == 0

    return (position == 0 and heading == "INTRO") or slide_type == "intro"


def build_slide_context_maps(
    slide_chunks: List[Dict[str, Any]],
    intro_mode: str = "detect",
) -> List[str]:
    """Build context labels for slide chunks.

    intro_mode:
    - "detect": intro only when chunk explicitly marks intro semantics.
    - "first_slide": always treat the first chunk as intro.
    """
    context_maps: List[str] = []

    for i, chunk in enumerate(slide_chunks):
        heading = str(chunk.get("heading", ""))
        heading_upper = heading.upper()
        position = chunk.get("position", -99)
        slide_type = str(chunk.get("slide_type", "")).lower()

        if _is_intro_slide(chunk, i, intro_mode=intro_mode):
            context = f"[Slide {i + 1}] INTRO SLIDE"
        elif heading_upper == "TRANSITION" or position == -1 or slide_type == "transition":
            context = f"[Slide {i + 1}] TRANSITION SLIDE"
        elif heading_upper == "THANK_YOU" or position == -2 or slide_type in ("thank_you", "thankyou"):
            context = f"[Slide {i + 1}] THANK YOU SLIDE"
        else:
            context = f"[Slide {i + 1}] {heading}" if heading else f"[Slide {i + 1}] Content Slide"

        context_maps.append(context)

    return context_maps