"""Create one immutable visual direction before slide-level planning starts."""

from __future__ import annotations

import json
from typing import Any, Dict

from langchain_core.runnables import RunnableConfig

from backend.config import ENABLE_DECK_STYLE_PLAN
from backend.workflows.slidegen_workflow.graph.stage import DeckStylePlan, State


def _as_dict(value: Any) -> Dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return dict(value or {})


def _default_style(deck_topic: str = "Untitled presentation") -> Dict[str, Any]:
    style = _as_dict(DeckStylePlan())
    style["deck_topic"] = deck_topic
    return style


def create_deck_style(state: State, config: RunnableConfig) -> State:
    """Plan deck styling once so parallel workers never depend on slide N-1."""
    if state.get("deck_style_plan"):
        existing = dict(state["deck_style_plan"])
        existing.setdefault(
            "deck_topic",
            state.get("document_title") or "Untitled presentation",
        )
        existing.setdefault(
            "visual_direction",
            "Coherent editorial presentation with clear hierarchy",
        )
        state["deck_style_plan"] = existing
        return state

    configurable = config.get("configurable", {}) if config else {}
    llm = configurable.get("planner_llm") or configurable.get("llm")
    title = state.get("document_title") or "Untitled presentation"
    if not ENABLE_DECK_STYLE_PLAN or not llm:
        state["deck_style_plan"] = _default_style(title)
        return state

    stream_callback = configurable.get("stream_callback")
    request_limiter = configurable.get("llm_request_limiter")
    if stream_callback:
        stream_callback(
            "status",
            {
                "step": 3,
                "title": "Define visual style",
                "description": "Creating one style system for the whole deck",
                "message": "Defining typography, colors, and visual direction",
            },
        )

    outline = state.get("document_outline") or state.get("document_structure") or []
    slide_options = state.get("slide_options") or {}
    prompt = f"""
You are the art director for a presentation deck. Create ONE coherent visual
style contract that every slide must follow. Keep title typography readable:
title_font_max must not exceed 48pt and body_font_max must not exceed 28pt.
Return colors as #RRGGBB. Layouts may vary from slide to slide, but typography,
palette, image treatment, and chart treatment must remain consistent.
Return a concise deck_topic describing the presentation's subject and a
visual_direction describing the shared visual language. These are immutable
inputs for every slide generator; do not invent a different theme per slide.

Presentation title: {title}
Requested options: {json.dumps(slide_options, ensure_ascii=False)}
Outline: {json.dumps(outline, ensure_ascii=False, default=str)[:12000]}

Populate only the DeckStylePlan structured fields. Do not return prose,
markdown, or a manually serialized JSON object.
"""

    try:
        if request_limiter is None:
            result = llm.with_structured_output(DeckStylePlan).invoke(prompt)
        else:
            with request_limiter.slot():
                result = llm.with_structured_output(DeckStylePlan).invoke(prompt)
        style = _as_dict(result)
        style["deck_topic"] = str(style.get("deck_topic") or title)
        style["visual_direction"] = str(
            style.get("visual_direction")
            or "Coherent editorial presentation with clear hierarchy"
        )
        style["title_font_max"] = min(48, int(style.get("title_font_max", 48)))
        style["body_font_max"] = min(28, int(style.get("body_font_max", 28)))
        state["deck_style_plan"] = style
    except Exception as exc:
        if configurable.get("strict_grpo_preprocessing"):
            raise RuntimeError("Deck-style planning failed during GRPO corpus rebuild") from exc
        print(f"Warning: deck style planner failed, using defaults: {exc}")
        state["deck_style_plan"] = _default_style(title)
    return state
