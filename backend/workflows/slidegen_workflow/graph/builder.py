# builder.py
from backend.workflows.slidegen_workflow.nodes.document_converter import convert_document
from backend.workflows.slidegen_workflow.nodes.content_splitter import split_content
from backend.workflows.slidegen_workflow.nodes.chunk_organizer import organize_chunks
from backend.workflows.slidegen_workflow.nodes.slide_planner import planning_slide
from backend.workflows.slidegen_workflow.nodes.next_slide_provider import provide_next_slide
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.slide_evaluator import slide_evaluator
from backend.workflows.slidegen_workflow.nodes.finalize_slide import finalize_slide
from backend.workflows.slidegen_workflow.nodes.html_renderer import render_html
from backend.workflows.slidegen_workflow.graph.stage import State
from backend.workflows.slidegen_workflow.nodes.auto_structure_generator import generate_structure_from_plaintext
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

def route_after_convert(state: State) -> str:
    """
    Router: Determines whether to use auto-structure generation or proceed normally.
    Routes based on presence of document structure.
    """
    print("--- Router: route_after_convert ---")
    
    # Check if document structure exists and is not empty
    doc_structure = state.get('document_structure', [])
    plain_text = state.get('plain_text', None)
    
    print(f"🔍 DEBUG Router state:")
    print(f"   - document_structure length: {len(doc_structure)}")
    print(f"   - plain_text exists: {plain_text is not None}")
    if plain_text:
        print(f"   - plain_text length: {len(plain_text)} chars")
    
    if doc_structure and len(doc_structure) > 0:
        # Has structure from hierarchical headings, skip auto-structure
        print("✅ Document has hierarchical structure. Proceeding to split_content.")
        return "split_content"
    else:
        # No structure, need to generate it
        print("🤖 Document has no structure. Routing to auto_structure generation.")
        return "auto_structure"



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

def build_workflow(router_flags: bool) -> StateGraph:
    """
    Hàm xây dựng đồ thị công việc dựa trên các cờ định tuyến.
    """
    # Định nghĩa đồ thị
    workflow = StateGraph(State)
    if router_flags:
        # Thêm các node
        workflow.add_node("convert_document", convert_document)
        workflow.add_node("auto_structure", generate_structure_from_plaintext)
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
        # Conditional routing: check if structure exists
        workflow.add_conditional_edges(
            "convert_document",
            route_after_convert,
            {"split_content": "split_content", "auto_structure": "auto_structure"}
        )
        workflow.add_edge("auto_structure", "split_content")
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
        workflow.add_node("auto_structure", generate_structure_from_plaintext)
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
        # Conditional routing: check if structure exists
        workflow.add_conditional_edges(
            "convert_document",
            route_after_convert,
            {"split_content": "split_content", "auto_structure": "auto_structure"}
        )
        workflow.add_edge("auto_structure", "split_content")
        workflow.add_edge("split_content", "organize_chunks")
        workflow.add_edge("organize_chunks", "planning_slide")
        workflow.add_edge("planning_slide", "provide_next_slide")
        workflow.add_conditional_edges("provide_next_slide", route_to_task, {"generate_slide": "generate_slide", END: END})
        workflow.add_edge("generate_slide", "render_html")
        workflow.add_edge("render_html", "finalizer")
        workflow.add_edge("finalizer", "provide_next_slide")

    return workflow