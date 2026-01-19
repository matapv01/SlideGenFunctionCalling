# File: src/nodes/next_slide_provider.py

from src.graph.stage import State
import time


def provide_next_slide(state: State) -> State:
    """
    Node to prepare the next slide from the queue and update loop counters.
    """
    print("\n---------------- Executing Node: prepare_next_slide ----------------")

    start_time = time.time()
    slide_chunks = state.get('slide_chunks', [])

    # --- THE FIX: SET THE TOTAL LENGTH ON THE FIRST RUN ---
    # Check if length_slide_chunks has been initialized. If not, this is the first slide.
    if 'length_slide_chunks' not in state:
        state['length_slide_chunks'] = len(slide_chunks)

    if slide_chunks:
        # Get the next slide from the queue
        # We use pop(0) to remove the item from the list so the queue gets smaller
        next_chunk = slide_chunks[0]

        state['current_slide_text'] = next_chunk
        state['slide_chunks'] = slide_chunks  # Update the state with the shorter list

        # Increment the index for the new slide
        current_index = state.get('current_slide_index', -1)
        state['current_slide_index'] = current_index + 1

        # Reset retry_count for the new slide
        state['retry_count'] = 0

        print(f"Queue has {len(slide_chunks)} chunks remaining. Preparing to process slide {state['current_slide_index'] + 1}/{state['length_slide_chunks']}.")
        print("Reset retry_count for new slide: 0")
    else:
        # This branch will be taken when the queue is empty, signaling the router to end.
        print("Slide chunk queue is empty.")

    end_time = time.time()
    print(f"Preparation of next slide took {end_time - start_time:.2f} seconds.")
    return state
