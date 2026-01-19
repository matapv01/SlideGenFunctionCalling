# File: src/nodes/slide_planner.py

from langchain_core.prompts import ChatPromptTemplate
from src.graph.stage import State, SlidePlan
from langchain_core.runnables import RunnableConfig
from src.utils.config import PLANNING_BATCH_SIZE
import time

# --- Prompts for the Slide Planner ---

SLIDE_PLANNER_SYSTEM_PROMPT = """
You are an expert presentation designer and slide planner. Your task is to analyze the content for a single slide and create a high-level plan for its visual design and type.

**INSTRUCTIONS:**

1.  **Check Slide Number FIRST:** Before anything else, check the SLIDE NUMBER provided.
2.  **Develop a Creative Vision (`thought`):** Based on the content, describe your vision for the slide.
    *   What is the key message?
    *   What layout would be best (e.g., two-column, grid, single image with text)?
    *   What is the appropriate mood or tone (e.g., professional, playful, minimalist, high-tech)?
    *   Suggest color themes, font styles, and whether an image or icon would enhance the message.
3.  **Select the Right Tool Category (`action`):** Based on the slide number and content type, choose the appropriate tool category.

**CRITICAL RULES FOR TOOL SELECTION:**
- **SLIDE NUMBER 1 ONLY**: MUST use 'INTRO_TOOLS' - This is the title/introduction slide
- **SLIDE NUMBER 2+**: Choose based on content:
  * If content starts with "TRANSITION SLIDE" → use 'TRANSITION_TOOLS'
  * If content starts with "THANK YOU SLIDE" → use 'THANK_YOU_TOOLS'
  * If content is about team members → use 'TEAM_TOOLS'
  * For all other content (main points, details, lists) → use 'CONTENT_TOOLS'
- **NEVER use INTRO_TOOLS for slides after slide 1**

**CRITICAL OUTPUT REQUIREMENT:**
- You MUST return ONLY a single, valid JSON object that strictly follows the required schema.
- Do not add any text, explanations, or markdown formatting before or after the JSON object.
- The 'action' key must be one of the following exact strings: 'INTRO_TOOLS', 'TRANSITION_TOOLS', 'CONTENT_TOOLS', 'TEAM_TOOLS', 'THANK_YOU_TOOLS'.
"""

SLIDE_PLANNER_HUMAN_PROMPT = """
===============================================
🔢 SLIDE NUMBER: {slide_number}
===============================================

IMPORTANT:
- If slide number is 1 → MUST use INTRO_TOOLS
- If slide number is 2 or higher → NEVER use INTRO_TOOLS

---
**PRESENTATION CONTEXT (OUTLINE):**
This is the structure of the entire presentation. The "YOU ARE HERE" marker shows the position of the current slide you are planning.

{slide_context_map}

---
**SLIDE CONTENT TO PLAN:**
This is the raw text content for the slide you need to create a plan for.

{slide_content}
"""


def planning_slide(state: State, config: RunnableConfig) -> State:
    """
    Analyzes all slide content in manageable chunks (batches) to create a design
    plan for every slide, avoiding API rate limits.
    """
    print("\n---------------- Executing Node: slide_planner (Chunked Batch Mode) ----------------")

    start_time = time.time()
    configurable = config["configurable"]
    llm = configurable.get('llm')

    # Emit streaming event
    stream_callback = configurable.get('stream_callback')
    if stream_callback:
        stream_callback('status', {
            'step': 3,
            'title': 'Thiết kế slide',
            'description': 'Đang lập kế hoạch thiết kế cho các slide...',
            'message': 'Đang phân tích nội dung để thiết kế slide'
        })

    if not llm:
        raise ValueError("LLM instance not found in config.")

    slide_chunks = state.get('slide_chunks', [])
    slide_context_maps = state.get('slide_context_maps', [])
    document_structure = state.get('document_structure', {})

    if not slide_chunks:
        print("WARNING: No slide chunks found. Skipping planning.")
        state['slide_plans'] = []
        return state

    # --- AUTO-CREATE INTRO SLIDE IF MISSING ---
    first_chunk = slide_chunks[0] if slide_chunks else {}
    if first_chunk.get('position', 0) != 0:
        print("⚠️  First chunk is not an intro slide. Creating intro slide...")

        # Get title from document structure (handle both dict and list)
        if isinstance(document_structure, dict):
            title = document_structure.get('title', 'Presentation Title')
        elif isinstance(document_structure, list) and len(document_structure) > 0:
            title = document_structure[0].get('title', 'Presentation Title') if isinstance(document_structure[0], dict) else 'Presentation Title'
        else:
            title = 'Presentation Title'

        # Create intro chunk
        intro_chunk = {
            'position': 0,
            'heading': '',
            'text_content': f"Title: {title}\nSubtitle: Overview"
        }

        # Insert at beginning
        slide_chunks.insert(0, intro_chunk)
        print(f"✅ Created intro slide with title: {title}")

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
        print("✅ Kept only the last thank you slide")

    # Update state with cleaned chunks
    state['slide_chunks'] = slide_chunks

    # Recreate or update context maps to match current chunks
    if not slide_context_maps or len(slide_context_maps) != len(slide_chunks):
        print(f"⚠️  Context maps mismatch (maps: {len(slide_context_maps)}, chunks: {len(slide_chunks)}). Regenerating...")
        slide_context_maps = []
        for i, chunk in enumerate(slide_chunks):
            heading = chunk.get('heading', '')
            position = chunk.get('position', i)

            if position == 0 or i == 0:
                context = f"[Slide {i+1}] INTRO SLIDE"
            elif heading == 'TRANSITION' or position == -1:
                context = f"[Slide {i+1}] TRANSITION SLIDE"
            elif heading == 'THANK_YOU' or position == -2:
                context = f"[Slide {i+1}] THANK YOU SLIDE"
            else:
                context = f"[Slide {i+1}] {heading}"
            slide_context_maps.append(context)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SLIDE_PLANNER_SYSTEM_PROMPT),
        ("human", SLIDE_PLANNER_HUMAN_PROMPT)
    ])

    planner_chain = prompt | llm.with_structured_output(SlidePlan)

    # --- CHUNKED BATCH PROCESSING LOGIC ---

    # 1. Prepare a list of all inputs.
    all_inputs = []
    for i, content in enumerate(slide_chunks):
        all_inputs.append({
            "slide_number": i + 1,  # Add slide number (1-indexed)
            "slide_context_map": slide_context_maps[i],
            "slide_content": content
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
            chunk_plans = [plan.dict() for plan in batch_results]
            all_slide_plans.extend(chunk_plans)
            print("     ... done.")

        print(f"\n  -> Successfully generated plans for all {len(all_slide_plans)} slides.")
        state['slide_plans'] = all_slide_plans
        # Save context maps to state (important for idea workflow)
        state['slide_context_maps'] = slide_context_maps

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
