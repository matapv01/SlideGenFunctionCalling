# File: backend/workflows/slidegen_workflow/nodes/slide_planner.py

import json
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from langchain_core.prompts import ChatPromptTemplate
from backend.workflows.slidegen_workflow.graph.stage import (
    State,
    SlidePlan,
    SlidePlanBatch,
)
from langchain_core.runnables import RunnableConfig
from backend.config import (
    PLANNER_OUTLINE_MAX_CHARS,
    PLANNING_BATCH_SIZE,
    PLANNER_MAX_CONCURRENCY,
)
from backend.workflows.slidegen_workflow.utils.prompts import SLIDE_PLANNER_SYSTEM_PROMPT, SLIDE_PLANNER_HUMAN_PROMPT
import time


_BATCH_PLANNER_HUMAN_PROMPT = """
Plan every slide in the following small batch. Return exactly one plan per
input slide, in the same order. Do not merge slides, omit slides, or add extra
plans. Each plan must describe only the slide's message, purpose, visual intent,
and tool category; do not generate XML or prose outside the structured result.

BATCH INPUT (JSON):
{batch_inputs}
"""


def _as_plain_dict(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return dict(value or {}) if isinstance(value, dict) else {}


def _extract_batch_plans(value) -> List[Dict]:
    """Read both Pydantic and simple fake-model batch responses."""
    payload = _as_plain_dict(value)
    raw_plans = payload.get("plans") if payload else value
    if not isinstance(raw_plans, list):
        return []
    return [_as_plain_dict(plan) for plan in raw_plans]


def _invoke_planner_batch(
    batch_chain,
    legacy_chain,
    batch_inputs: List[Dict],
    config: RunnableConfig,
):
    """Invoke one real structured batch, retaining a compatibility fallback."""
    request_limiter = (config or {}).get("configurable", {}).get(
        "llm_request_limiter"
    )
    if batch_chain is not None:
        first_input = batch_inputs[0] if batch_inputs else {}
        compact_inputs = [
            {
                "slide_number": item.get("slide_number"),
                "slide_context_map": item.get("slide_context_map", ""),
                "slide_content": item.get("slide_content", ""),
            }
            for item in batch_inputs
        ]
        payload = {
            "batch_inputs": json.dumps(
                {
                    "shared": {
                        "full_outline": first_input.get("full_outline", ""),
                        "presentation_instruction": first_input.get(
                            "presentation_instruction", ""
                        ),
                        "deck_style_plan": first_input.get(
                            "deck_style_plan", ""
                        ),
                    },
                    "slides": compact_inputs,
                },
                ensure_ascii=False,
                default=str,
            )
        }
        try:
            if request_limiter is None:
                result = batch_chain.invoke(payload)
            else:
                with request_limiter.slot():
                    result = batch_chain.invoke(payload)
            plans = _extract_batch_plans(result)
            if len(plans) == len(batch_inputs):
                return plans
            raise ValueError(
                f"Planner returned {len(plans)} plans for {len(batch_inputs)} slides"
            )
        except Exception:
            # A malformed batch response should not silently turn the whole
            # deck into deterministic fallback plans. Retry only this planner
            # batch through the older one-slide path.
            if legacy_chain is None:
                raise

    # Older integrations and focused tests may only inject the single-slide
    # chain. Keep that path working until they migrate to the batch chain.
    if hasattr(legacy_chain, "invoke"):
        def invoke_one(item):
            if request_limiter is None:
                return legacy_chain.invoke(item)
            with request_limiter.slot():
                return legacy_chain.invoke(item)

        with ThreadPoolExecutor(
            max_workers=min(max(1, int(PLANNER_MAX_CONCURRENCY)), len(batch_inputs))
        ) as executor:
            return list(executor.map(invoke_one, batch_inputs))

    return legacy_chain.batch(
        batch_inputs,
        config={"max_concurrency": max(1, int(PLANNER_MAX_CONCURRENCY))},
    )


def _is_intro_slide(chunk: Dict, index: int, intro_mode: str) -> bool:
    heading = str(chunk.get("heading", "")).upper()
    position = chunk.get("position", -99)
    slide_type = str(chunk.get("slide_type", "")).lower()

    if intro_mode == "first_slide":
        return index == 0

    return (position == 0 and heading == "INTRO") or slide_type == "intro"


def build_slide_context_maps(
    slide_chunks: List[Dict],
    intro_mode: str = "detect",
) -> List[str]:
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


def _fallback_slide_topic(content, index: int) -> str:
    """Derive a stable topic when a structured planner omits the field."""
    if isinstance(content, dict):
        for key in ("heading", "title", "section_title", "name"):
            value = str(content.get(key) or "").strip()
            if value:
                return value[:160]
    if isinstance(content, str):
        first_line = next((line.strip() for line in content.splitlines() if line.strip()), "")
        if first_line:
            return first_line[:160]
    return f"Slide {index + 1}"


def _fallback_slide_purpose(content, index: int) -> str:
    """Derive a compact semantic brief when the planner omits it."""
    topic = _fallback_slide_topic(content, index)
    if topic.startswith("Slide "):
        return f"This slide presents the main idea for slide {index + 1}."
    return f"This slide explains {topic}."


VALID_SLIDE_ACTIONS = {
    "INTRO_TOOLS",
    "TRANSITION_TOOLS",
    "CONTENT_TOOLS",
    "TEAM_TOOLS",
    "THANK_YOU_TOOLS",
    "CHART_TOOLS",
}
VALID_IMAGE_MODES = {"none", "semantic"}


def build_compact_slide_outline(
    slide_chunks: List[Dict],
    slide_context_maps: List[str],
    max_chars: int = PLANNER_OUTLINE_MAX_CHARS,
) -> str:
    """Build a whole-deck map without repeating raw slide content."""
    lines = []
    for index, chunk in enumerate(slide_chunks):
        context = (
            slide_context_maps[index]
            if index < len(slide_context_maps)
            else ""
        )
        if not context:
            context = _fallback_slide_topic(chunk, index)
        context = " ".join(str(context).split())
        lines.append(f"{index + 1}. {context[:220]}")

    outline = "\n".join(lines)
    if len(outline) <= max_chars:
        return outline
    truncated = outline[:max_chars].rsplit("\n", 1)[0]
    return f"{truncated}\n… (outline truncated)"


def _metadata_action(content, index: int) -> str:
    data = content if isinstance(content, dict) else {}
    heading = str(data.get("heading", "")).upper()
    slide_type = str(data.get("slide_type", "")).lower()
    raw_position = data.get("position", "")
    if isinstance(raw_position, (list, tuple)):
        raw_position = raw_position[0] if raw_position else ""
    position = str(raw_position).strip()
    if index == 0:
        return "INTRO_TOOLS"
    if position in {"-2", "999"} or heading == "THANK_YOU" or slide_type in {"thank_you", "thankyou"}:
        return "THANK_YOU_TOOLS"
    if position == "-1" or heading == "TRANSITION" or slide_type == "transition":
        return "TRANSITION_TOOLS"
    return ""


def _normalize_plan_action(plan: Dict, content, index: int) -> str:
    """Keep structured planner output aligned with document markers."""
    action = str(plan.get("action", "CONTENT_TOOLS")).upper()
    metadata_action = _metadata_action(content, index)
    if metadata_action:
        return metadata_action
    if action == "INTRO_TOOLS" and index > 0:
        return "CONTENT_TOOLS"
    return action if action in VALID_SLIDE_ACTIONS else "CONTENT_TOOLS"


def _normalize_image_mode(plan: Dict) -> str:
    """Accept only the explicit image mode emitted by the current planner."""
    mode = str(plan.get("image_mode") or "").lower()
    if mode in VALID_IMAGE_MODES:
        return mode
    return "none"


def _normalize_image_search_intents(plan: Dict) -> List[Dict]:
    """Normalize planner image intents without inventing a search query.

    The active planner emits explicit intents. Missing or empty intents mean
    that the slide must not trigger image search.
    """
    raw_intents = plan.get("image_search_intents")
    if not isinstance(raw_intents, list):
        raw_intents = []
    normalized: List[Dict] = []
    valid_roles = {"evidence", "illustration", "chart", "diagram", "photo"}
    valid_layouts = {"Wide", "Tall", "Square"}
    for item in raw_intents[:1]:
        if hasattr(item, "model_dump"):
            item = item.model_dump()
        elif hasattr(item, "dict"):
            item = item.dict()
        if not isinstance(item, dict):
            continue
        query = " ".join(str(item.get("query") or "").split())[:240]
        if not query:
            continue
        layout = item.get("layout")
        layout = layout if layout in valid_layouts else None
        role = str(item.get("role") or "illustration").lower()
        if role not in valid_roles:
            role = "illustration"
        normalized.append(
            {
                "query": query,
                "role": role,
                "layout": layout,
                "required": bool(item.get("required", False)),
            }
        )

    return normalized


def normalize_planner_result(plan, content, index: int) -> Dict:
    """Convert one structured planner response into the canonical plan shape."""
    if hasattr(plan, "model_dump"):
        plan_dict = plan.model_dump()
    elif hasattr(plan, "dict"):
        plan_dict = plan.dict()
    else:
        plan_dict = dict(plan or {})

    plan_dict["slide_topic"] = str(
        plan_dict.get("slide_topic") or _fallback_slide_topic(content, index)
    ).strip()[:160]
    plan_dict["slide_purpose"] = " ".join(
        str(
            plan_dict.get("slide_purpose")
            or _fallback_slide_purpose(content, index)
        ).split()
    ).strip()[:320]
    normalized_action = _normalize_plan_action(plan_dict, content, index)
    if normalized_action != plan_dict.get("action"):
        print(
            f"  -> Normalized slide {index + 1} action "
            f"from '{plan_dict.get('action')}' to '{normalized_action}'"
        )
        plan_dict["action"] = normalized_action
    plan_dict["image_mode"] = _normalize_image_mode(plan_dict)
    plan_dict["image_search_intents"] = _normalize_image_search_intents(plan_dict)
    plan_dict["image_mode"] = (
        "semantic" if plan_dict["image_search_intents"] else "none"
    )
    plan_dict["visual_layout_request"] = " ".join(
        str(plan_dict.get("visual_layout_request") or "").split()
    )[:320]
    return plan_dict


def fallback_slide_plan(content, index: int) -> Dict:
    """Return the safe plan used when one planner request cannot be completed."""
    return {
        "slide_topic": _fallback_slide_topic(content, index),
        "slide_purpose": _fallback_slide_purpose(content, index),
        "thought": "Use a readable layout with concise editable text.",
        "image_mode": "none",
        "image_search_intents": [],
        "visual_layout_request": "Use a clear no-image composition with readable hierarchy.",
        "action": _normalize_plan_action({}, content, index),
    }


def normalize_image_sequence(plans: List[Dict]) -> List[Dict]:
    """Normalize one explicit visual intent per slide without inventing one."""
    for plan in plans:
        intents = _normalize_image_search_intents(plan)
        plan["image_search_intents"] = intents
        plan["image_mode"] = "semantic" if intents else "none"
    return plans


def prepare_planner_context(state: State, config: RunnableConfig) -> Dict:
    """Prepare shared planner inputs once for both batch and pipeline modes."""
    configurable = config.get("configurable", {}) if config else {}
    llm = configurable.get("planner_llm") or configurable.get("llm")
    if not llm:
        raise ValueError("LLM instance not found in config.")

    stream_callback = configurable.get("stream_callback")
    if stream_callback:
        stream_callback(
            "status",
            {
                "step": 3,
                "title": "Prepare Content",
                "description": "Planning slide design...",
                "message": "Analyzing content to design slides",
            },
        )

    slide_chunks = list(state.get("slide_chunks") or [])
    slide_context_maps = list(state.get("slide_context_maps") or [])
    slide_positions = list(state.get("slide_positions") or [])
    section_ids = list(state.get("section_ids") or [])
    deck_style_plan = state.get("deck_style_plan", {})

    if not slide_chunks:
        print("WARNING: No slide chunks found. Skipping planning.")
        state["slide_plans"] = []
        return {
            "slide_chunks": [],
            "slide_context_maps": [],
            "slide_positions": slide_positions,
            "section_ids": section_ids,
            "all_inputs": [],
            "planner_chain": None,
            "stream_callback": stream_callback,
        }

    has_intro = any(
        isinstance(chunk, dict)
        and chunk.get("heading") == "INTRO"
        and chunk.get("position") == 0
        for chunk in slide_chunks
    )
    if not has_intro:
        print("ℹ️  No INTRO slide in chunks; the planner will use content slides")

    thank_you_positions = [
        index
        for index, chunk in enumerate(slide_chunks)
        if isinstance(chunk, dict)
        and (chunk.get("position") == -2 or chunk.get("heading") == "THANK_YOU")
    ]
    if len(thank_you_positions) > 1:
        print(
            f"⚠️  Found {len(thank_you_positions)} thank you slides at positions: "
            f"{thank_you_positions}"
        )
        for position in reversed(thank_you_positions[:-1]):
            print(f"   Removing duplicate thank you slide at index {position}")
            slide_chunks.pop(position)
            if position < len(slide_context_maps):
                slide_context_maps.pop(position)
            if position < len(slide_positions):
                slide_positions.pop(position)
            if position < len(section_ids):
                section_ids.pop(position)
        print("✅ Kept only the last thank you slide")

    if not slide_context_maps or len(slide_context_maps) != len(slide_chunks):
        print(
            f"⚠️  Context maps mismatch (maps: {len(slide_context_maps)}, "
            f"chunks: {len(slide_chunks)}). Regenerating..."
        )
        slide_context_maps = build_slide_context_maps(slide_chunks, intro_mode="detect")
        state["slide_plans"] = []

    if len(slide_chunks) != len(slide_context_maps):
        print("❌ CRITICAL: Array mismatch detected during batch processing!")
        slide_context_maps = build_slide_context_maps(slide_chunks, intro_mode="detect")

    slide_options = state.get("slide_options") or {}
    presentation_instruction = str(
        slide_options.get("presentation_instruction") or ""
    ).strip()
    if not presentation_instruction:
        presentation_instruction = "No additional deck-level presentation instruction."

    state["slide_chunks"] = slide_chunks
    state["slide_context_maps"] = slide_context_maps
    state["slide_positions"] = slide_positions
    state["section_ids"] = section_ids

    full_outline = build_compact_slide_outline(slide_chunks, slide_context_maps)
    all_inputs = []
    for index, content in enumerate(slide_chunks):
        context_map = (
            slide_context_maps[index]
            if index < len(slide_context_maps)
            else f"[Slide {index + 1}] Content Slide"
        )
        all_inputs.append(
            {
                "slide_number": index + 1,
                "slide_context_map": context_map,
                "full_outline": full_outline,
                "slide_content": content,
                "presentation_instruction": presentation_instruction,
                "deck_style_plan": json.dumps(
                    deck_style_plan,
                    ensure_ascii=False,
                    indent=2,
                ),
            }
        )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SLIDE_PLANNER_SYSTEM_PROMPT),
            ("human", SLIDE_PLANNER_HUMAN_PROMPT),
        ]
    )
    batch_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SLIDE_PLANNER_SYSTEM_PROMPT
                + "\n\nBATCH MODE: The user message contains several slides. "
                "Return one independent structured plan for every slide, in input order.",
            ),
            ("human", _BATCH_PLANNER_HUMAN_PROMPT),
        ]
    )
    return {
        "slide_chunks": slide_chunks,
        "slide_context_maps": slide_context_maps,
        "slide_positions": slide_positions,
        "section_ids": section_ids,
        "all_inputs": all_inputs,
        "presentation_instruction": presentation_instruction,
        "planner_chain": prompt | llm.with_structured_output(SlidePlan),
        "planner_batch_chain": batch_prompt
        | llm.with_structured_output(SlidePlanBatch),
        "stream_callback": stream_callback,
    }


def planning_slide(state: State, config: RunnableConfig) -> State:
    """
    Analyzes all slide content in manageable chunks (batches) to create a design
    plan for every slide, avoiding API rate limits.
    """
    print("\n---------------- Executing Node: slide_planner (Chunked Batch Mode) ----------------")

    start_time = time.time()
    planner_context = prepare_planner_context(state, config)
    slide_chunks = planner_context["slide_chunks"]
    slide_context_maps = planner_context["slide_context_maps"]
    all_inputs = planner_context["all_inputs"]
    planner_chain = planner_context["planner_chain"]
    planner_batch_chain = planner_context.get("planner_batch_chain")
    stream_callback = planner_context["stream_callback"]

    if not all_inputs or planner_chain is None:
        return state

    total_slides = len(all_inputs)
    all_slide_plans = []

    print(f"Total slides to plan: {total_slides}. Processing in chunks of {PLANNING_BATCH_SIZE}.")

    try:
        # 2. Process the inputs in chunks.
        for i in range(0, total_slides, PLANNING_BATCH_SIZE):
            # Get the current chunk of inputs
            chunk_inputs = all_inputs[i : i + PLANNING_BATCH_SIZE]
            chunk_start_num = i + 1
            chunk_end_num = min(i + PLANNING_BATCH_SIZE, total_slides)

            print(f"  -> Processing chunk: slides {chunk_start_num}-{chunk_end_num}...")

            # One structured request plans the whole small batch. The legacy
            # single-slide batch remains available for older injected chains.
            batch_results = _invoke_planner_batch(
                planner_batch_chain,
                planner_chain,
                chunk_inputs,
                config,
            )

            # Add the results from this chunk to the main list.
            chunk_plans = []
            for j, plan in enumerate(batch_results):
                global_idx = i + j
                chunk_plans.append(
                    normalize_planner_result(
                        plan,
                        slide_chunks[global_idx],
                        global_idx,
                    )
                )

            all_slide_plans.extend(chunk_plans)
            print("     ... done.")

        print(f"\n  -> Successfully generated plans for all {len(all_slide_plans)} slides.")
        state['slide_plans'] = normalize_image_sequence(all_slide_plans)
        # Save context maps for the canonical renderer and project metadata.
        state['slide_context_maps'] = slide_context_maps

        # Emit final status to signal Stage 2 (Design Slides)
        if stream_callback:
            stream_callback('status', {
                'step': 3,
                'title': 'Design Slides',
                'description': 'Planning complete',
                'message': 'Starting slide generation'
            })

    except Exception as e:
        if (config or {}).get("configurable", {}).get("strict_grpo_preprocessing"):
            raise RuntimeError("Slide planning failed during GRPO corpus rebuild") from e
        print(f"  -> FAILED during batch planning. Error: {e}")
        # As a fallback, create default plans for all slides.
        state['slide_plans'] = []
        for index, content in enumerate(slide_chunks):
            state['slide_plans'].append(
                {
                    **fallback_slide_plan(
                        content,
                        index,
                    ),
                }
            )
        state['slide_context_maps'] = slide_context_maps  # Still save context maps
        print(f"  -> Created {len(state['slide_plans'])} default plans as a fallback.")

    end_time = time.time()
    print(f"Planning completed in {end_time - start_time:.2f} seconds.")
    print("Slide planning process complete.")
    return state
