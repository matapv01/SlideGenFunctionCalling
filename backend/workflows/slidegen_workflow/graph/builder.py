# builder.py
from backend.workflows.slidegen_workflow.nodes.slide_planner import planning_slide
from backend.workflows.slidegen_workflow.nodes.next_slide_provider import provide_next_slide
from backend.workflows.slidegen_workflow.nodes.slide_preparer import prepare_slide
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.slide_evaluator import slide_evaluator
from backend.workflows.slidegen_workflow.nodes.finalize_slide import finalize_slide
from backend.workflows.slidegen_workflow.nodes.html_renderer import render_html
from backend.workflows.slidegen_workflow.graph.stage import State
from langgraph.graph import StateGraph
from langgraph.graph import END


def route_to_task(state: State) -> str:
    """
    Router: kiểm tra còn slide nào cần chuẩn bị không.
    """
    print("--- Router: route_to_task ---")
    current_index = state.get('current_slide_index', -1)
    length = state.get('length_slide_chunks', 0)

    if current_index < length:
        return "prepare_slide"
    else:
        print("Tất cả slides đã được generate. Kết thúc luồng.")
        return END


def evaluate_vlm_decision(state: State) -> str:
    """
    Đánh giá quyết định của VLM và quyết định luồng tiếp theo.
    """
    print("--- Router: evaluate_vlm_decision ---")
    
    decision = state.get('vlm_decision', 'deny')
    print(f"Đang xử lý quyết định VLM: {decision}")
    
    retry_count = state.get('retry_count', 0)
    max_retries = state.get('max_retries', 3)
    print(f"Giá trị retry_count hiện tại: {retry_count}")
    
    if decision == "accept":
        print("Slide được chấp nhận. Chuyển đến bước hoàn tất.")
        return "finalizer"
    else: # deny
        if retry_count >= max_retries:
            print(f"Đã đạt số lần thử lại tối đa ({max_retries}). Buộc chấp nhận slide.")
            return "finalizer"
        else:
            print(f"Slide bị từ chối. Thử lại lần {retry_count}.")
            return "prepare_slide"


def build_workflow(router_flags: bool) -> StateGraph:
    """
    Hàm xây dựng đồ thị công việc với node slide_preparer mới.
    """
    workflow = StateGraph(State)
    if router_flags:
        # Thêm các node
        workflow.add_node("planning_slide", planning_slide)
        workflow.add_node("provide_next_slide", provide_next_slide)
        workflow.add_node("prepare_slide", prepare_slide)
        workflow.add_node("generate_slide", generate_slide)
        workflow.add_node("render_html", render_html)
        workflow.add_node("evaluator", slide_evaluator)
        workflow.add_node("finalizer", finalize_slide)

        # Thiết lập điểm bắt đầu
        workflow.set_entry_point("planning_slide")

        # Thêm các cạnh (edges)
        workflow.add_edge("planning_slide", "provide_next_slide")
        workflow.add_conditional_edges("provide_next_slide", route_to_task, {"prepare_slide": "prepare_slide", END: END})
        workflow.add_edge("prepare_slide", "generate_slide")
        workflow.add_edge("generate_slide", "render_html")
        workflow.add_edge("render_html", "evaluator")
        workflow.add_conditional_edges("evaluator", evaluate_vlm_decision, {"finalizer": "finalizer", "prepare_slide": "prepare_slide"})
        workflow.add_edge("finalizer", "provide_next_slide")
    else:
        # Thêm các node
        workflow.add_node("planning_slide", planning_slide)
        workflow.add_node("provide_next_slide", provide_next_slide)
        workflow.add_node("prepare_slide", prepare_slide)
        workflow.add_node("generate_slide", generate_slide)
        workflow.add_node("render_html", render_html)
        workflow.add_node("finalizer", finalize_slide)

        # Thiết lập điểm bắt đầu
        workflow.set_entry_point("planning_slide")

        # Thêm các cạnh (edges)
        workflow.add_edge("planning_slide", "provide_next_slide")
        workflow.add_conditional_edges("provide_next_slide", route_to_task, {"prepare_slide": "prepare_slide", END: END})
        workflow.add_edge("prepare_slide", "generate_slide")
        workflow.add_edge("generate_slide", "render_html")
        workflow.add_edge("render_html", "finalizer")
        workflow.add_edge("finalizer", "provide_next_slide")

    return workflow