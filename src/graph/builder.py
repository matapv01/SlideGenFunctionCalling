# builder.py
from src.nodes.initialize_and_provider import initialize_and_provide
from src.nodes.next_slide_provider import provide_next_slide
from src.nodes.slide_generator import slide_generator
from src.nodes.slide_evaluator import slide_evaluator
from src.nodes.finalize_slide import finalize_slide
from src.nodes.html_renderer import html_renderer
from src.graph.stage import State
from langgraph.graph import StateGraph
from langgraph.graph import END


def route_to_task(state: State) -> str:
    """
    Router chính: Chỉ kiểm tra xem còn slide để xử lý không và định tuyến.
    """
    print("--- Router: route_to_task ---")
    if state.get('slide_chunks'):
        # Nếu còn slide, đi đến node chuẩn bị
        return "generator"
    else:
        # Nếu hết, kết thúc
        print("Không còn slide nào trong hàng đợi. Kết thúc luồng.")
        return END

def evaluate_vlm_decision(state: State) -> str:
    """
    Đánh giá quyết định của VLM và quyết định luồng tiếp theo.
    """
    print("--- Router: evaluate_vlm_decision ---")
    
    # Đảm bảo vlm_decision luôn tồn tại trong state
    decision = state.get('vlm_decision', 'deny')  # Mặc định deny nếu không có quyết định
    print(f"Đang xử lý quyết định VLM: {decision}")
    
    # Lấy retry_count hiện tại
    retry_count = state.get('retry_count', 0)
    max_retries = state.get('max_retries', 3)
    print(f"Giá trị retry_count hiện tại: {retry_count}")
    
    if decision == "accept":
        print("Slide được chấp nhận. Chuyển đến bước hoàn tất.")

        return "finalizer"
    else: # deny
        # Kiểm tra nếu đã đạt số lần thử lại tối đa
        if retry_count >= max_retries:
            print(f"Đã đạt số lần thử lại tối đa ({max_retries}). Buộc chấp nhận slide.")
            return "finalizer"  # Đi thẳng đến finalizer
        else:
            print(f"Slide bị từ chối. Thử lại lần {retry_count}.")
            return "generator"  # Quay lại node generator để thử lại slide

def build_workflow(router_flags: bool) -> StateGraph:
    """
    Hàm xây dựng đồ thị công việc dựa trên các cờ định tuyến.
    """
    # Định nghĩa đồ thị
    workflow = StateGraph(State)
    if router_flags:
        # Thêm các node
        workflow.add_node("initialize_and_provide", initialize_and_provide)
        workflow.add_node("provide_next_slide", provide_next_slide)
        workflow.add_node("generator", slide_generator)
        workflow.add_node("renderer", html_renderer)
        workflow.add_node("evaluator", slide_evaluator)
        workflow.add_node("finalizer", finalize_slide)

        # Thiết lập điểm bắt đầu
        workflow.set_entry_point("initialize_and_provide")

        # Thêm các cạnh (edges)
        workflow.add_edge("initialize_and_provide", "provide_next_slide")
        workflow.add_conditional_edges("provide_next_slide", route_to_task, {"generator": "generator", END: END})
        workflow.add_edge("generator", "renderer")
        workflow.add_edge("renderer", "evaluator")
        workflow.add_conditional_edges("evaluator", evaluate_vlm_decision, {"finalizer": "finalizer", "generator": "generator"})
        workflow.add_edge("finalizer", "provide_next_slide")
    else:
        # Thêm các node
        workflow.add_node("initialize_and_provide", initialize_and_provide)
        workflow.add_node("provide_next_slide", provide_next_slide)
        workflow.add_node("generator", slide_generator)
        workflow.add_node("renderer", html_renderer)
        workflow.add_node("finalizer", finalize_slide)

        # Thiết lập điểm bắt đầu
        workflow.set_entry_point("initialize_and_provide")

        # Thêm các cạnh (edges)
        workflow.add_edge("initialize_and_provide", "provide_next_slide")
        workflow.add_conditional_edges("provide_next_slide", route_to_task, {"generator": "generator", END: END})
        workflow.add_edge("generator", "renderer")
        workflow.add_edge("renderer", "finalizer")
        workflow.add_edge("finalizer", "provide_next_slide")

    return workflow