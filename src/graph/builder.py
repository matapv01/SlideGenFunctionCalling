# builder.py
from src.nodes.document_converter import convert_document
from src.nodes.content_splitter import split_content
from src.nodes.chunk_organizer import organize_chunks
from src.nodes.slide_planner import planning_slide
from src.nodes.next_slide_provider import provide_next_slide
from src.nodes.slide_generator import generate_slide
from src.nodes.slide_evaluator import slide_evaluator
from src.nodes.finalize_slide import finalize_slide
from src.nodes.html_renderer import render_html
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
        return "generate_slide"
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
    else:
        # Kiểm tra nếu đã đạt số lần thử lại tối đa
        if retry_count >= max_retries:
            print(f"Đã đạt số lần thử lại tối đa ({max_retries}). Buộc chấp nhận slide.")
            return "finalizer"  # Đi thẳng đến finalizer
        else:
            print(f"Slide bị từ chối. Thử lại lần {retry_count}.")
            return "generate_slide"  # Quay lại node generate_slide để thử lại slide


def build_workflow(router_flags: bool) -> StateGraph:
    """
    Hàm xây dựng đồ thị công việc dựa trên các cờ định tuyến.
    """
    # Định nghĩa đồ thị
    workflow = StateGraph(State)
    if router_flags:
        # Thêm các node
        workflow.add_node("convert_document", convert_document)
        workflow.add_node("split_content", split_content)
        workflow.add_node("organize_chunks", organize_chunks)
        workflow.add_node("planning_slide", planning_slide)
        workflow.add_node("provide_next_slide", provide_next_slide)
        workflow.add_node("generate_slide", generate_slide)
        workflow.add_node("render_html", render_html)
        workflow.add_node("evaluator", slide_evaluator)
        workflow.add_node("finalizer", finalize_slide)

        # Thiết lập điểm bắt đầu
        workflow.set_entry_point("convert_document")

        # Thêm các cạnh (edges)
        workflow.add_edge("convert_document", "split_content")
        workflow.add_edge("split_content", "organize_chunks")
        workflow.add_edge("organize_chunks", "planning_slide")
        workflow.add_edge("planning_slide", "provide_next_slide")
        workflow.add_conditional_edges("provide_next_slide", route_to_task, {"generate_slide": "generate_slide", END: END})
        workflow.add_edge("generate_slide", "render_html")
        workflow.add_edge("render_html", "evaluator")
        workflow.add_conditional_edges("evaluator", evaluate_vlm_decision, {"finalizer": "finalizer", "generate_slide": "generate_slide"})
        workflow.add_edge("finalizer", "provide_next_slide")
    else:
        # Thêm các node
        workflow.add_node("convert_document", convert_document)
        workflow.add_node("split_content", split_content)
        workflow.add_node("organize_chunks", organize_chunks)
        workflow.add_node("planning_slide", planning_slide)
        workflow.add_node("provide_next_slide", provide_next_slide)
        workflow.add_node("generate_slide", generate_slide)
        workflow.add_node("render_html", render_html)
        workflow.add_node("finalizer", finalize_slide)

        # Thiết lập điểm bắt đầu
        workflow.set_entry_point("convert_document")

        # Thêm các cạnh (edges)
        workflow.add_edge("convert_document", "split_content")
        workflow.add_edge("split_content", "organize_chunks")
        workflow.add_edge("organize_chunks", "planning_slide")
        workflow.add_edge("planning_slide", "provide_next_slide")
        workflow.add_conditional_edges("provide_next_slide", route_to_task, {"generate_slide": "generate_slide", END: END})
        workflow.add_edge("generate_slide", "render_html")
        workflow.add_edge("render_html", "finalizer")
        workflow.add_edge("finalizer", "provide_next_slide")

    return workflow
