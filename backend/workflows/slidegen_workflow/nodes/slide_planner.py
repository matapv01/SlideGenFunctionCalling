# File: backend/workflows/slidegen_workflow/nodes/slide_planner.py

import json
from typing import Dict, List

from langchain_core.prompts import ChatPromptTemplate
from backend.workflows.slidegen_workflow.graph.stage import State, SlidePlan
from langchain_core.runnables import RunnableConfig
from backend.config import PLANNING_BATCH_SIZE
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
        time.sleep(2) # Delay for UX

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
            batch_results = planner_chain.batch(chunk_inputs, config={"max_concurrency": 5})

            # Add the results from this chunk to the main list.
            chunk_plans = []
            for j, plan in enumerate(batch_results):
                global_idx = i + j
                plan_dict = plan.dict()
                
                # --- HARD RULE cho Slide 1 ---
                # Ép slide đầu tiên luôn dùng INTRO_TOOLS vì LLM nhiều lúc bị nhầm
                if global_idx == 0 and plan_dict.get('action') != 'INTRO_TOOLS':
                    print(f"  -> 🛡️ OVERRIDE: Forced slide 1 action from '{plan_dict.get('action')}' to 'INTRO_TOOLS'")
                    plan_dict['action'] = 'INTRO_TOOLS'
                
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
        default_plan = {"thought": "Default plan due to a batch error.", "action": "CONTENT_TOOLS"}
        state['slide_plans'] = [default_plan for _ in slide_chunks]
        state['slide_context_maps'] = slide_context_maps  # Still save context maps
        print(f"  -> Created {len(state['slide_plans'])} default plans as a fallback.")

    end_time = time.time()
    print(f"Planning completed in {end_time - start_time:.2f} seconds.")
    print("Slide planning process complete.")
    return state
