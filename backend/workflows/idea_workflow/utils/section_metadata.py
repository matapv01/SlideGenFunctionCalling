"""Normalize flat Idea output into canonical presentation sections."""

from typing import Any, Dict, List


def normalize_section_metadata(
    slide_chunks: List[Dict[str, Any]],
    estimated_sections: int,
) -> List[Dict[str, Any]]:
    chunks = [dict(chunk) for chunk in slide_chunks]
    estimated_sections = max(1, estimated_sections)
    content_indices = [
        index for index, chunk in enumerate(chunks)
        if str(chunk.get("slide_type", "content")).lower() == "content"
    ]
    has_transition = any(
        str(chunk.get("slide_type", "content")).lower() == "transition"
        for chunk in chunks
    )
    has_explicit_sections = any(
        chunk.get("section_id") for chunk in chunks
        if str(chunk.get("slide_type", "content")).lower() in ("content", "transition")
    )

    distributed_sections: Dict[int, int] = {}
    if content_indices and not has_transition and not has_explicit_sections:
        section_count = min(estimated_sections, len(content_indices))
        for rank, chunk_index in enumerate(content_indices):
            distributed_sections[chunk_index] = min(
                section_count,
                rank * section_count // len(content_indices) + 1,
            )

    current_section = 1
    section_has_content = False
    order_counters: Dict[str, int] = {}
    normalized: List[Dict[str, Any]] = []
    for index, chunk in enumerate(chunks):
        slide_type = str(chunk.get("slide_type", "content")).lower()
        if slide_type == "intro":
            section_id, section_order = "intro", 0
        elif slide_type in ("thank_you", "thankyou"):
            section_id, section_order = "closing", 999
        else:
            explicit = str(chunk.get("section_id") or "").strip()
            if explicit:
                section_id = explicit
                digits = "".join(character for character in explicit if character.isdigit())
                section_order = int(chunk.get("section_order") or digits or current_section)
                current_section = max(current_section, section_order)
            elif index in distributed_sections:
                section_order = distributed_sections[index]
                section_id = f"section_{section_order}"
            else:
                if slide_type == "transition" and section_has_content:
                    current_section += 1
                    section_has_content = False
                section_order = current_section
                section_id = f"section_{section_order}"
            if slide_type == "content":
                section_has_content = True

        order_in_section = order_counters.get(section_id, 0)
        order_counters[section_id] = order_in_section + 1
        chunk.update(
            {
                "section_id": section_id,
                "section_order": section_order,
                "order_in_section": order_in_section,
            }
        )
        normalized.append(chunk)
    return normalized
