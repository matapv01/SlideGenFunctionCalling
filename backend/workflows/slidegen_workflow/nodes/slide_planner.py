# File: backend/workflows/slidegen_workflow/nodes/slide_planner.py

import json
from typing import Dict, List

from langchain_core.prompts import ChatPromptTemplate
from backend.workflows.slidegen_workflow.graph.stage import State, SlidePlan
from langchain_core.runnables import RunnableConfig
from backend.config import (
    PLANNER_OUTLINE_MAX_CHARS,
    PLANNING_BATCH_SIZE,
    SLIDE_MAX_CONCURRENCY,
)
from backend.workflows.slidegen_workflow.utils.prompts import SLIDE_PLANNER_SYSTEM_PROMPT, SLIDE_PLANNER_HUMAN_PROMPT
import time


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


VALID_SLIDE_ACTIONS = {
    "INTRO_TOOLS",
    "TRANSITION_TOOLS",
    "CONTENT_TOOLS",
    "TEAM_TOOLS",
    "THANK_YOU_TOOLS",
    "CHART_TOOLS",
}
VALID_IMAGE_STRATEGIES = {"semantic", "decorative"}


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


def _normalize_image_strategy(plan: Dict, content, index: int) -> str:
    """Use generic supporting imagery for identity and structural slides."""
    action = str(plan.get("action", "CONTENT_TOOLS")).upper()
    strategy = str(plan.get("image_strategy", "decorative")).lower()
    metadata_action = _metadata_action(content, index)
    if metadata_action in {
        "INTRO_TOOLS",
        "TRANSITION_TOOLS",
        "TEAM_TOOLS",
        "THANK_YOU_TOOLS",
    } or action in {
        "INTRO_TOOLS",
        "TRANSITION_TOOLS",
        "TEAM_TOOLS",
        "THANK_YOU_TOOLS",
    }:
        return "decorative"
    if strategy not in VALID_IMAGE_STRATEGIES:
        return "decorative"
    return strategy


def planning_slide(state: State, config: RunnableConfig) -> State:
    """
    Analyzes all slide content in manageable chunks (batches) to create a design
    plan for every slide, avoiding API rate limits.
    """
    print("\n---------------- Executing Node: slide_planner (Chunked Batch Mode) ----------------")

    start_time = time.time()
    configurable = config["configurable"]
    llm = configurable.get('planner_llm') or configurable.get('llm')

    # Emit streaming event
    stream_callback = configurable.get('stream_callback')
    if stream_callback:
        stream_callback('status', {
            'step': 3,
            'title': 'Prepare Content',
            'description': 'Planning slide design...',
            'message': 'Analyzing content to design slides'
        })

    if not llm:
        raise ValueError("LLM instance not found in config.")

    slide_chunks = state.get('slide_chunks', [])
    slide_context_maps = state.get('slide_context_maps', [])
    slide_positions = state.get('slide_positions', [])
    section_ids = state.get('section_ids', [])
    document_structure = state.get('document_structure', {})
    deck_style_plan = state.get('deck_style_plan', {})

    if not slide_chunks:
        print("WARNING: No slide chunks found. Skipping planning.")
        state['slide_plans'] = []
        return state

    # --- AUTO-CREATE INTRO SLIDE IF MISSING ---
    # Kiểm tra xem đã có intro slide thực (heading=='INTRO' và position==0) chưa
    # NOTE: Chỉ log cảnh báo, KHÔNG insert ở đây vì slide_planner chạy TRƯỚC provide_next_slide
    # Nếu insert ở đây, length_slide_chunks sẽ bị set sai (thiếu 1 slide)
    has_intro = any(c.get('heading') == 'INTRO' and c.get('position') == 0 for c in slide_chunks)
    if not has_intro:
        print("ℹ️  No INTRO slide in chunks (expected for manual mode without explicit intro)")

    # --- REMOVE DUPLICATE THANK YOU SLIDES ---
    thank_you_positions = []
    for i, chunk in enumerate(slide_chunks):
        if chunk.get('position') == -2 or chunk.get('heading') == 'THANK_YOU':
            thank_you_positions.append(i)

    if len(thank_you_positions) > 1:
        print(f"⚠️  Found {len(thank_you_positions)} thank you slides at positions: {thank_you_positions}")
        # Keep only the last one (remove duplicates from end to start to preserve indices)
        for pos in reversed(thank_you_positions[:-1]):
            print(f"   Removing duplicate thank you slide at index {pos}")
            slide_chunks.pop(pos)
            # IMPORTANT: Also remove corresponding context map to keep arrays in sync
            if slide_context_maps and pos < len(slide_context_maps):
                slide_context_maps.pop(pos)
            if slide_positions and pos < len(slide_positions):
                slide_positions.pop(pos)
            if section_ids and pos < len(section_ids):
                section_ids.pop(pos)
        print("✅ Kept only the last thank you slide")

    # Update state with cleaned chunks
    state['slide_chunks'] = slide_chunks
    state['slide_positions'] = slide_positions
    state['section_ids'] = section_ids

    # Recreate or update context maps to match current chunks
    if not slide_context_maps or len(slide_context_maps) != len(slide_chunks):
        print(f"⚠️  Context maps mismatch (maps: {len(slide_context_maps)}, chunks: {len(slide_chunks)}). Regenerating...")
        slide_context_maps = build_slide_context_maps(slide_chunks, intro_mode='detect')

        # Also clear slide_plans so they get regenerated with correct number of chunks
        state['slide_plans'] = []
        print(f"   ✓ Cleared slide_plans for regeneration (will be recreated with correct count)")

    prompt = ChatPromptTemplate.from_messages([
        ("system", SLIDE_PLANNER_SYSTEM_PROMPT),
        ("human", SLIDE_PLANNER_HUMAN_PROMPT)
    ])

    planner_chain = prompt | llm.with_structured_output(SlidePlan)

    # --- CHUNKED BATCH PROCESSING LOGIC ---

    # SAFETY CHECK: Ensure arrays are in sync before building inputs
    if len(slide_chunks) != len(slide_context_maps):
        print(f"❌ CRITICAL: Array mismatch detected during batch processing!")
        print(f"   slide_chunks: {len(slide_chunks)}, slide_context_maps: {len(slide_context_maps)}")
        print(f"   Regenerating context_maps to match chunks...")
        slide_context_maps = build_slide_context_maps(slide_chunks, intro_mode='detect')
        print(f"   ✓ Context maps regenerated with {len(slide_context_maps)} items")

    full_outline = build_compact_slide_outline(
        slide_chunks,
        slide_context_maps,
    )

    # 1. Prepare a list of all inputs.
    all_inputs = []
    for i, content in enumerate(slide_chunks):
        # SAFETY: Verify index exists in context_maps
        if i >= len(slide_context_maps):
            print(f"⚠️  WARNING: Index {i} out of bounds for slide_context_maps (length: {len(slide_context_maps)})")
            context_map = f"[Slide {i+1}] Content Slide"
        else:
            context_map = slide_context_maps[i]

        all_inputs.append({
            "slide_number": i + 1,  # Add slide number (1-indexed)
            "slide_context_map": context_map,
            "full_outline": full_outline,
            "slide_content": content,
            "deck_style_plan": json.dumps(deck_style_plan, ensure_ascii=False, indent=2),
        })

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

            # Invoke the chain with the current chunk.
            batch_results = planner_chain.batch(
                chunk_inputs,
                config={"max_concurrency": max(1, int(SLIDE_MAX_CONCURRENCY))},
            )

            # Add the results from this chunk to the main list.
            chunk_plans = []
            for j, plan in enumerate(batch_results):
                global_idx = i + j
                plan_dict = (
                    plan.model_dump()
                    if hasattr(plan, "model_dump")
                    else plan.dict()
                )
                plan_dict["slide_topic"] = str(
                    plan_dict.get("slide_topic")
                    or _fallback_slide_topic(slide_chunks[global_idx], global_idx)
                ).strip()[:160]
                plan_dict["image_strategy"] = _normalize_image_strategy(
                    plan_dict,
                    slide_chunks[global_idx],
                    global_idx,
                )

                normalized_action = _normalize_plan_action(
                    plan_dict,
                    slide_chunks[global_idx],
                    global_idx,
                )
                if normalized_action != plan_dict.get("action"):
                    print(
                        f"  -> Normalized slide {global_idx + 1} action "
                        f"from '{plan_dict.get('action')}' to '{normalized_action}'"
                    )
                    plan_dict["action"] = normalized_action
                
                chunk_plans.append(plan_dict)
                
            all_slide_plans.extend(chunk_plans)
            print("     ... done.")

        print(f"\n  -> Successfully generated plans for all {len(all_slide_plans)} slides.")
        state['slide_plans'] = all_slide_plans
        # Save context maps to state (important for idea workflow)
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
        print(f"  -> FAILED during batch planning. Error: {e}")
        # As a fallback, create default plans for all slides.
        state['slide_plans'] = []
        for index, content in enumerate(slide_chunks):
            state['slide_plans'].append(
                {
                    "slide_topic": _fallback_slide_topic(content, index),
                    "thought": "Use a readable layout with concise editable text.",
                    "image_strategy": _normalize_image_strategy({}, content, index),
                    "action": _normalize_plan_action({}, content, index),
                }
            )
        state['slide_context_maps'] = slide_context_maps  # Still save context maps
        print(f"  -> Created {len(state['slide_plans'])} default plans as a fallback.")

    end_time = time.time()
    print(f"Planning completed in {end_time - start_time:.2f} seconds.")
    print("Slide planning process complete.")
    return state
