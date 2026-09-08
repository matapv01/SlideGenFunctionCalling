"""Convert planned slides into ordered jobs grouped by top-level DFS section."""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Dict, List, Tuple

from backend.config import SECTION_FALLBACK_BATCH_SIZE


def _position_text(position: Any) -> str:
    if isinstance(position, (list, tuple)):
        return str(position[0]) if position else ""
    return str(position) if position is not None else ""


def _special_kind(chunk: Any, plan: Dict[str, Any], index: int) -> str:
    data = chunk if isinstance(chunk, dict) else {}
    heading = str(data.get("heading", "")).upper()
    slide_type = str(data.get("slide_type", "")).lower()
    position = data.get("position")
    action = str((plan or {}).get("action", ""))

    if action == "INTRO_TOOLS" or slide_type == "intro" or (
        index == 0 and heading == "INTRO"
    ):
        return "intro"
    if action == "THANK_YOU_TOOLS" or slide_type in ("thank_you", "thankyou") or heading == "THANK_YOU" or position == -2:
        return "thank_you"
    if action == "TRANSITION_TOOLS" or slide_type == "transition" or heading == "TRANSITION" or position == -1:
        return "transition"
    return "content"


def _section_from_position(position: Any, fallback: int) -> Tuple[str, int | None]:
    raw = _position_text(position).strip()
    if raw == "0":
        return "000_intro", None
    if raw in ("999", "-2"):
        return "999_thank_you", None

    clean = raw[:-2] if raw.endswith(".T") else raw
    first = clean.split(".", 1)[0]
    try:
        root = int(first)
        return f"section_{root:04d}", root
    except (TypeError, ValueError):
        return f"section_{fallback:04d}", fallback


def _section_from_id(section_id: Any, fallback: int) -> Tuple[str, int | None]:
    raw = str(section_id or "").strip()
    if not raw:
        return f"section_{fallback:04d}", fallback
    lowered = raw.lower()
    if lowered in ("intro", "opening", "000_intro"):
        return "000_intro", None
    if lowered in ("closing", "thank_you", "thankyou", "999_thank_you"):
        return "999_thank_you", None

    digits = "".join(character for character in raw if character.isdigit())
    if digits:
        order = int(digits)
        return f"section_{order:04d}", order
    return f"section_{fallback:04d}_{lowered.replace(' ', '_')}", fallback


def build_slide_jobs(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    chunks = list(state.get("slide_chunks") or [])
    contexts = list(state.get("slide_context_maps") or [])
    plans = list(state.get("slide_plans") or [])
    positions = list(state.get("slide_positions") or [])
    state_section_ids = list(state.get("section_ids") or [])
    has_explicit_section_ids = any(state_section_ids) or any(
        isinstance(chunk, dict) and chunk.get("section_id") for chunk in chunks
    )
    has_outline_positions = len(positions) == len(chunks) and any(
        _position_text(pos).strip() for pos in positions
    )
    has_transition_markers = any(
        _special_kind(
            chunk,
            plans[index] if index < len(plans) else {},
            index,
        ) == "transition"
        for index, chunk in enumerate(chunks)
    )

    jobs: List[Dict[str, Any]] = []
    fallback_section = 1
    fallback_section_has_content = False
    fallback_content_index = 0
    for index, chunk in enumerate(chunks):
        plan = plans[index] if index < len(plans) else {
            "thought": "Use a readable content layout.",
            "action": "CONTENT_TOOLS",
        }
        context = contexts[index] if index < len(contexts) else f"[Slide {index + 1}] Content Slide"
        kind = _special_kind(chunk, plan, index)
        chunk_data = chunk if isinstance(chunk, dict) else {}
        explicit_section_id = (
            state_section_ids[index]
            if index < len(state_section_ids) and state_section_ids[index]
            else chunk_data.get("section_id")
        )

        if explicit_section_id:
            position = positions[index] if index < len(positions) else None
            batch_id, root_section = _section_from_id(explicit_section_id, fallback_section)
            if kind == "intro":
                batch_id, root_section = "000_intro", None
            elif kind == "thank_you":
                batch_id, root_section = "999_thank_you", None
        elif has_outline_positions:
            position = positions[index]
            batch_id, root_section = _section_from_position(position, fallback_section)
            if kind == "intro":
                batch_id, root_section = "000_intro", None
            elif kind == "thank_you":
                batch_id, root_section = "999_thank_you", None
        else:
            # Idea/manual input may not expose DFS positions. A transition marks
            # the start of the next section, so it stays with the slides it introduces.
            if (
                not has_explicit_section_ids
                and not has_outline_positions
                and not has_transition_markers
                and kind == "content"
            ):
                fallback_section = fallback_content_index // SECTION_FALLBACK_BATCH_SIZE + 1
                fallback_content_index += 1
            elif kind == "transition" and fallback_section_has_content:
                fallback_section += 1
                fallback_section_has_content = False
            if kind == "intro":
                batch_id, root_section = "000_intro", None
            elif kind == "thank_you":
                batch_id, root_section = "999_thank_you", None
            else:
                batch_id, root_section = f"section_{fallback_section:04d}", fallback_section
                if kind == "content":
                    fallback_section_has_content = True
            position = None

        jobs.append(
            {
                "index": index,
                "content": chunk,
                "context_map": context,
                "plan": plan,
                "position": position,
                "slide_type": kind,
                "batch_id": batch_id,
                "section_id": batch_id,
                "section_order": (
                    chunk_data.get("section_order")
                    if chunk_data.get("section_order") is not None
                    else root_section
                ),
                "order_in_section": chunk_data.get("order_in_section"),
                "root_section": root_section,
                "assigned_tool_candidates": [],
                "excluded_tools": [],
            }
        )
    return jobs


def group_slide_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: "OrderedDict[str, List[Dict[str, Any]]]" = OrderedDict()
    for job in jobs:
        grouped.setdefault(str(job["batch_id"]), []).append(job)
    for batch_jobs in grouped.values():
        for order, job in enumerate(batch_jobs):
            if job.get("order_in_section") is None:
                job["order_in_section"] = order
    return [
        {
            "batch_id": batch_id,
            "order": min(job["index"] for job in batch_jobs),
            "jobs": batch_jobs,
        }
        for batch_id, batch_jobs in grouped.items()
    ]


def build_section_batches(state: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    jobs = build_slide_jobs(state)
    return jobs, group_slide_jobs(jobs)
