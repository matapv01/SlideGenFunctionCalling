"""Canonical slide-chunk contract shared by independent application flows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def _aligned_values(values: Sequence[Any] | None, size: int) -> list[Any]:
    """Keep positional metadata only when it can be trusted."""
    if values is None:
        return []
    materialized = list(values)
    return materialized if len(materialized) == size else []


def normalize_canonical_chunks(
    slide_chunks: Sequence[Any] | None,
    *,
    slide_positions: Sequence[Any] | None = None,
    slide_context_maps: Sequence[Any] | None = None,
    section_ids: Sequence[Any] | None = None,
) -> dict[str, list[Any]]:
    """Return one stable shape for every source feeding slide generation.

    Chatbot scripts, preprocessed DOCX files, and the legacy editor can all
    provide slightly different metadata. The renderer should receive one
    canonical state and must not need to know which source produced it.
    Positional metadata is discarded when its length does not match the
    chunks, allowing the renderer's planner to regenerate safe context maps.
    """
    chunks: list[Any] = []
    for index, chunk in enumerate(slide_chunks or []):
        if isinstance(chunk, Mapping):
            chunks.append(dict(chunk))
            continue
        chunks.append(
            {
                "heading": f"Slide {index + 1}",
                "title": f"Slide {index + 1}",
                "content": str(chunk or ""),
                "slide_type": "content",
            }
        )

    return {
        "slide_chunks": chunks,
        "slide_positions": _aligned_values(slide_positions, len(chunks)),
        "slide_context_maps": _aligned_values(slide_context_maps, len(chunks)),
        "section_ids": _aligned_values(section_ids, len(chunks)),
    }
