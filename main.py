# main.py
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langchain_core.messages import AIMessage
import logging
import zipfile
from docx import Document
import shutil
from src.models.llm import LLM
from src.nodes.input_processor import input_processor, initialize_and_prepare
from src.nodes.prepare_next_slide import prepare_next_slide
from src.nodes.slide_generator import slide_generator
from src.nodes.slide_evaluator import slide_evaluator
from src.nodes.finalize_slide import finalize_slide
from src.nodes.html_renderer import html_renderer
from src.stage import State
from src.utils import config
from langgraph.graph import StateGraph
import os
from src.tools.tool_des import ALL_TOOLS
from langgraph.graph import END

logger = logging.getLogger(__name__)

def route_to_task(state: State) -> str:
    """
    Router chính: Chỉ kiểm tra xem còn slide để xử lý không và định tuyến.
    """
    logger.info("--- Router: route_to_task ---")
    if state.get('slide_chunks'):
        # Nếu còn slide, đi đến node chuẩn bị
        return "prepare_slide"
    else:
        # Nếu hết, kết thúc
        logger.info("Không còn slide nào trong hàng đợi. Kết thúc luồng.")
        return END

def check_redundancy(state: State) -> str:
    """
    Kiểm tra xem slide có bị LLM đánh dấu là dư thừa không.
    """
    logger.info("--- Router: check_redundancy ---")
    is_redundant = state.get('is_redundant', False)
    logger.info(f"Slide có bị đánh dấu là dư thừa: {is_redundant}")
    
    if is_redundant:
        # Nếu dư thừa, quay lại router chính để lấy slide khác
        logger.info("Slide bị đánh dấu là dư thừa, quay lại node initializer")
        return "initializer"
    else:
        # Nếu không, tiếp tục render
        logger.info("Slide không dư thừa, tiếp tục đến node renderer")
        return "renderer"

def evaluate_vlm_decision(state: State) -> str:
    """
    Đánh giá quyết định của VLM và quyết định luồng tiếp theo.
    """
    logger.info("--- Router: evaluate_vlm_decision ---")
    
    # Đảm bảo vlm_decision luôn tồn tại trong state
    decision = state.get('vlm_decision', 'deny')  # Mặc định deny nếu không có quyết định
    logger.info(f"Đang xử lý quyết định VLM: {decision}")
    
    # Lấy retry_count hiện tại
    retry_count = state.get('retry_count', 0)
    logger.info(f"Giá trị retry_count hiện tại: {retry_count}")
    
    if decision == "accept":
        logger.info("Slide được chấp nhận. Chuyển đến bước hoàn tất.")
        # Reset retry_count
        state['retry_count'] = 0
        return "finalizer"
    else: # deny
        # Kiểm tra nếu đã đạt số lần thử lại tối đa
        if retry_count >= state.get('max_retries', 3):
            logger.warning(f"Đã đạt số lần thử lại tối đa ({state.get('max_retries', 3)}). Buộc chấp nhận slide.")
            # Reset retry_count
            state['retry_count'] = 0
            return "finalizer"  # Đi thẳng đến finalizer
        else:
            logger.info(f"Slide bị từ chối. Thử lại lần {retry_count}.")
            return "renderer"



# -- Xây dựng và thực thi Graph ---

def process_slides_with_langgraph(docx_file: str, output_folder: str, max_retries_per_slide: int = 3):
    """
    Hàm chính để xây dựng và chạy luồng công việc LangGraph.
    """
    # Khởi tạo WebDriver một lần duy nhất
    driver = config.initialize_chromedriver()
    if not driver:
        raise RuntimeError("Không thể khởi tạo ChromeDriver.")
        
    # ===== KHỞI TẠO LLM INSTANCE =====
    # KHỞI TẠO LLM INSTANCE
    env_keys = config.setup_environment()
    api_keys = [v for v in env_keys.values() if v]
    if not api_keys:
        raise RuntimeError("Không có API key hợp lệ trong biến môi trường.")

    llm = LLM(
        api_keys=api_keys,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model="gemini-2.5-flash",
        temperature=0.5,
        max_tokens=4096,
    )

    # Tạo thư mục temp nếu chưa có
    temp_dir = os.path.join(output_folder, "temp")
    html_dir = os.path.join(temp_dir, "html")
    png_dir = os.path.join(temp_dir, "png")
    
    for dir_path in [temp_dir, html_dir, png_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"Đã tạo thư mục: {dir_path}")
            
    # Định nghĩa đồ thị
    workflow = StateGraph(State)
    
    # Cấu hình logger chi tiết hơn
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Thêm các node
    workflow.add_node("initializer", initialize_and_prepare)
    workflow.add_node("prepare_slide", prepare_next_slide)
    workflow.add_node("generator", slide_generator)
    workflow.add_node("renderer", html_renderer)
    workflow.add_node("evaluator", slide_evaluator)
    workflow.add_node("finalizer", finalize_slide)

    # Thiết lập điểm bắt đầu
    workflow.set_entry_point("initializer")

    # Thêm các cạnh (edges)
    workflow.add_conditional_edges("initializer", route_to_task, {"prepare_slide": "prepare_slide", END: END})
    workflow.add_edge("prepare_slide", "generator")
    workflow.add_conditional_edges("generator", check_redundancy, {"initializer": "initializer", "renderer": "renderer"})
    workflow.add_edge("renderer", "evaluator")
    workflow.add_conditional_edges("evaluator", evaluate_vlm_decision, {"finalizer": "finalizer", "renderer": "renderer"})
    workflow.add_edge("finalizer", "initializer")

    # Biên dịch đồ thị với các tùy chọn
    app = workflow.compile()
    
    # ===== TRUYỀN LLM_INSTANCE VÀO STATE BAN ĐẦU =====
    # Chuẩn bị input ban đầu cho graph
    initial_input = {
        "docx_file": docx_file,
        "output_folder": output_folder,
        "max_retries": max_retries_per_slide,
        "driver": driver, 
        "llm": llm,
        "tools": ALL_TOOLS,  # Truyền vào danh sách công cụ
        "current_slide_index": -1,
        "retry_count": 0,
        "final_slides": [],
        "temp_dir": os.path.join(output_folder, "temp"),
        "is_redundant": False,
    }
    
    # Chạy graph
    # Sử dụng try-finally để đảm bảo driver luôn được đóng
    try:
        final_state = app.invoke(initial_input)
    finally:
        if driver:
            driver.quit()
            logger.info("Đã đóng ChromeDriver.")
            
    # Đảm bảo driver đã đóng và không còn được sử dụng
    zip_file_path = os.path.join(final_state['temp_dir'], "slides.zip")
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for slide in final_state['final_slides']:
            if os.path.exists(slide['html_path']):
                zipf.write(slide['html_path'], os.path.join("html", os.path.basename(slide['html_path'])))
            if os.path.exists(slide['png_path']):
                zipf.write(slide['png_path'], os.path.join("png", os.path.basename(slide['png_path'])))

    # Sao chép file zip cuối cùng ra output folder
    final_zip_path = os.path.join(output_folder, "slides_langgraph.zip")
    shutil.copy2(zip_file_path, final_zip_path)
    shutil.rmtree(final_state['temp_dir']) # Xóa thư mục tạm

    logger.info(f"Hoàn thành! File kết quả đã được lưu tại: {final_zip_path}")
    return final_zip_path

# --- Ví dụ cách chạy ---
if __name__ == "__main__":
    # Tạo các thư mục test nếu chưa có
    if not os.path.exists("test_input"):
        os.makedirs("test_input")
    if not os.path.exists("test_output"):
        os.makedirs("test_output")

    # Tạo một file docx giả để test
    sample_docx_path = os.path.join("test_input", "sample.docx")
    doc = Document()
    doc.add_heading('Slide 1: Giới thiệu về LangGraph', level=1)
    doc.add_paragraph('LangGraph là một thư viện giúp xây dựng các ứng dụng LLM phức tạp, có trạng thái.')
    doc.add_paragraph('Nó cho phép tạo các đồ thị có chu trình, rất phù hợp cho các tác vụ lặp đi lặp lại như agent.')
    
    doc.add_heading('Slide 2: Các lợi ích chính', level=1)
    doc.add_paragraph('- Dễ dàng quản lý trạng thái qua các bước.')
    doc.add_paragraph('- Hỗ trợ các chu trình và vòng lặp một cách tự nhiên.')
    doc.add_paragraph('- Tăng khả năng gỡ lỗi và quan sát luồng dữ liệu.')
    
    doc.add_heading('Slide 3: Một ví dụ về nội dung dài', level=1)
    doc.add_paragraph('Nội dung này được thiết kế để rất dài và có thể không vừa một slide duy nhất. Nó buộc LLM phải sử dụng khả năng chia tách nội dung của mình. Đây là dòng 1. Đây là dòng 2. Đây là dòng 3. Đây là dòng 4. Đây là dòng 5. Đây là dòng 6. Đây là dòng 7. Đây là dòng 8. Đây là dòng 9. Đây là dòng 10. LLM nên nhận ra điều này và đặt phần còn lại vào `remaining_content`.')
    
    doc.save(sample_docx_path)
    logger.info(f"Đã tạo file test tại: {sample_docx_path}")

    # Chạy quy trình
    try:
        process_slides_with_langgraph(sample_docx_path, "test_output")
    except Exception as e:
        logger.error(f"Một lỗi không mong muốn đã xảy ra trong quá trình xử lý: {e}", exc_info=True)