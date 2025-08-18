# /app/src/nodes/prepare_slide.py 

from src.graph.stage import State

def provide_next_slide(state: State) -> State:
    """
    Node chuẩn bị slide tiếp theo từ hàng đợi.
    """
    print("\n---------------- Executing Node: prepare_next_slide ----------------")
    if state['slide_chunks']:
        # Lấy slide tiếp theo từ hàng đợi
        next_chunk = state['slide_chunks'][0]
        state['current_slide_text'] = next_chunk
        state['current_slide_index'] += 1
        # Reset retry_count cho slide mới
        state['retry_count'] = 0
        print(f"Hàng đợi còn {len(state['slide_chunks'])} chunks. Chuẩn bị xử lý slide {state['current_slide_index'] + 1}.")
        print(f"Reset retry_count cho slide mới: {state['retry_count']}")
    return state
