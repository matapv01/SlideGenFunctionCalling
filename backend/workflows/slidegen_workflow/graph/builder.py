# builder.py
from backend.workflows.slidegen_workflow.nodes.slide_planner import planning_slide
from backend.workflows.slidegen_workflow.nodes.next_slide_provider import provide_next_slide
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.slide_evaluator import slide_evaluator
from backend.workflows.slidegen_workflow.nodes.finalize_slide import finalize_slide
from backend.workflows.slidegen_workflow.nodes.html_renderer import render_html
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import tool_call_executor
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.config import EXECUTOR_MAX_RETRIES
from langgraph.graph import StateGraph
from langgraph.graph import END


def route_to_task(state: State) -> str:
    """
    Router: kiểm tra còn slide nào cần generate không.
    Dùng current_slide_index vs length_slide_chunks thay vì kiểm tra queue rỗng
    vì slide cuối bị pop trước khi route_to_task chạy.
    """
    print("--- Router: route_to_task ---")
    current_index = state.get('current_slide_index', -1)
    length = state.get('length_slide_chunks', 0)

    if current_index < length:
        return "generate_slide"
    else:
        print("Tất cả slides đã được generate. Kết thúc luồng.")
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
            return "generate_slide"  # Quay lại node generate_slide để thử lại slide

def evaluate_executor_decision(state: State) -> str:
    """
    Router: kiểm tra kết quả của executor validator.
    Nếu pass → chuyển sang render_html.
    Nếu fail và chưa hết retry → quay lại generate_slide.
    Nếu fail và hết retry → ép buộc chuyển sang render_html.
    """
    print("--- Router: evaluate_executor_decision ---")
    decision = state.get('executor_decision', 'fail')
    retry_count = state.get('retry_count', 0)
    
    if decision == 'pass':
        print("✅ Executor PASSED. Proceeding to render.")
        return "render_html"
    else:
        if retry_count >= EXECUTOR_MAX_RETRIES:
            print(f"⚠️ Executor FAILED but max retries ({EXECUTOR_MAX_RETRIES}) reached. Force rendering.")
            return "render_html"
        else:
            print(f"🔄 Executor FAILED (retry {retry_count}/{EXECUTOR_MAX_RETRIES}). Retrying generation.")
            return "generate_slide"


def build_workflow(router_flags: bool) -> StateGraph:
    """
    Hàm xây dựng đồ thị công việc dựa trên các cờ định tuyến.
    """
    # Định nghĩa đồ thị
    workflow = StateGraph(State)
    if router_flags:
        # Thêm các node
        workflow.add_node("planning_slide", planning_slide)
        workflow.add_node("provide_next_slide", provide_next_slide)
        workflow.add_node("generate_slide", generate_slide)
        workflow.add_node("executor", tool_call_executor)
        workflow.add_node("render_html", render_html)
        workflow.add_node("evaluator", slide_evaluator)
        workflow.add_node("finalizer", finalize_slide)

        # Thiết lập điểm bắt đầu
        workflow.set_entry_point("planning_slide")

        # Thêm các cạnh (edges)
        # planning → next_slide → generate → executor → render → evaluator → finalizer → next_slide
        workflow.add_edge("planning_slide", "provide_next_slide")
        workflow.add_conditional_edges("provide_next_slide", route_to_task, {"generate_slide": "generate_slide", END: END})
        workflow.add_edge("generate_slide", "executor")
        workflow.add_conditional_edges("executor", evaluate_executor_decision, {"render_html": "render_html", "generate_slide": "generate_slide"})
        workflow.add_edge("render_html", "evaluator")
        workflow.add_conditional_edges("evaluator", evaluate_vlm_decision, {"finalizer": "finalizer", "generate_slide": "generate_slide"})
        workflow.add_edge("finalizer", "provide_next_slide")
    else:
        # Thêm các node (không có VLM evaluator)
        workflow.add_node("planning_slide", planning_slide)
        workflow.add_node("provide_next_slide", provide_next_slide)
        workflow.add_node("generate_slide", generate_slide)
        workflow.add_node("executor", tool_call_executor)
        workflow.add_node("render_html", render_html)
        workflow.add_node("finalizer", finalize_slide)

        # Thiết lập điểm bắt đầu
        workflow.set_entry_point("planning_slide")

        # Thêm các cạnh (edges)
        # planning → next_slide → generate → executor → render → finalizer → next_slide
        workflow.add_edge("planning_slide", "provide_next_slide")
        workflow.add_conditional_edges("provide_next_slide", route_to_task, {"generate_slide": "generate_slide", END: END})
        workflow.add_edge("generate_slide", "executor")
        workflow.add_conditional_edges("executor", evaluate_executor_decision, {"render_html": "render_html", "generate_slide": "generate_slide"})
        workflow.add_edge("render_html", "finalizer")
        workflow.add_edge("finalizer", "provide_next_slide")

    return workflow
