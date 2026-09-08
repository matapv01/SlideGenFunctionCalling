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


def _default_style() -> Dict[str, Any]:
    return _as_dict(DeckStylePlan())


def create_deck_style(state: State, config: RunnableConfig) -> State:
    """Plan deck styling once so parallel workers never depend on slide N-1."""
    if state.get("deck_style_plan"):
        return state

    configurable = config.get("configurable", {}) if config else {}
    llm = configurable.get("planner_llm") or configurable.get("llm")
    if not ENABLE_DECK_STYLE_PLAN or not llm:
        state["deck_style_plan"] = _default_style()
        return state

    stream_callback = configurable.get("stream_callback")
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

    title = state.get("document_title") or "Untitled presentation"
    outline = state.get("document_outline") or state.get("document_structure") or []
    slide_options = state.get("slide_options") or {}
    prompt = f"""
You are the art director for a presentation deck. Create ONE coherent visual
style contract that every slide must follow. Keep title typography readable:
title_font_max must not exceed 48pt and body_font_max must not exceed 28pt.
Return colors as #RRGGBB. Layouts may vary from slide to slide, but typography,
palette, image treatment, and chart treatment must remain consistent.

Presentation title: {title}
Requested options: {json.dumps(slide_options, ensure_ascii=False)}
Outline: {json.dumps(outline, ensure_ascii=False, default=str)[:12000]}
"""

    try:
        result = llm.with_structured_output(DeckStylePlan).invoke(prompt)
        style = _as_dict(result)
        style["title_font_max"] = min(48, int(style.get("title_font_max", 48)))
        style["body_font_max"] = min(28, int(style.get("body_font_max", 28)))
        state["deck_style_plan"] = style
    except Exception as exc:
        print(f"Warning: deck style planner failed, using defaults: {exc}")
        state["deck_style_plan"] = _default_style()
    return state
