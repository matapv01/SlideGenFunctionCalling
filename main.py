# main.py
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langchain_core.messages import AIMessage
import zipfile
from docx import Document
import shutil
from src.models.llm import LLM
from src.nodes.initialize_and_provider import initialize_and_provide
from src.nodes.next_slide_provider import provide_next_slide
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

def check_redundancy(state: State) -> str:
    """
    Kiểm tra xem slide có bị LLM đánh dấu là dư thừa không.
    """
    print("--- Router: check_redundancy ---")
    is_redundant = state.get('is_redundant', False)
    print(f"Slide có bị đánh dấu là dư thừa: {is_redundant}")
    
    if is_redundant:
        # Nếu dư thừa, quay lại router chính để lấy slide khác
        print("Slide bị đánh dấu là dư thừa, quay lại node initialize_and_provide")
        return "initialize_and_provide"
    else:
        # Nếu không, tiếp tục render
        print("Slide không dư thừa, tiếp tục đến node renderer")
        return "renderer"

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
    
    # Tạo thư mục debug
    temp_debug_dir = os.path.join(output_folder, "temp_debug")
    debug_html_dir = os.path.join(temp_debug_dir, "html")
    debug_png_dir = os.path.join(temp_debug_dir, "png")
    
    # Tạo tất cả các thư mục cần thiết
    for dir_path in [temp_dir, html_dir, png_dir, temp_debug_dir, debug_html_dir, debug_png_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Đã tạo thư mục: {dir_path}")
            
    # Định nghĩa đồ thị
    workflow = StateGraph(State)

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
    workflow.add_conditional_edges("generator", check_redundancy, {"initialize_and_provide": "initialize_and_provide", "renderer": "renderer"})
    workflow.add_edge("renderer", "evaluator")
    workflow.add_conditional_edges("evaluator", evaluate_vlm_decision, {"finalizer": "finalizer", "generator": "generator"})
    workflow.add_edge("finalizer", "provide_next_slide")

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
        "temp_debug_dir": temp_debug_dir,
        "is_redundant": False,
        "all_debug_info": [],  # Thêm khởi tạo cho all_debug_info
        "vlm_decision": "accept",  # Đặt mặc định là accept
    }
    
    # Chạy graph
    # Sử dụng try-finally để đảm bảo driver luôn được đóng
    try:
        final_state = app.invoke(initial_input)
    finally:
        if driver:
            driver.quit()
            print("Đã đóng ChromeDriver.")
            
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


    zip_debug_file_path = os.path.join(final_state['temp_debug_dir'], "slides_debug.zip")
    # Tạo zip file debug nếu có thông tin debug
    with zipfile.ZipFile(zip_debug_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for slide in final_state['all_debug_info']:
            if os.path.exists(slide['html_path']):
                zipf.write(slide['html_path'], os.path.join("html", os.path.basename(slide['html_path'])))
            if os.path.exists(slide['png_path']):
                zipf.write(slide['png_path'], os.path.join("png", os.path.basename(slide['png_path'])))
            if 'feedback' in slide:
                feedback_filename = f"feedback_{slide['index'] + 1}_{slide['retry_count']}.txt"
                feedback_path = os.path.join(final_state['temp_dir'], "feedback", feedback_filename)
                if not os.path.exists(os.path.dirname(feedback_path)):
                    os.makedirs(os.path.dirname(feedback_path))
                with open(feedback_path, 'w', encoding='utf-8') as f:
                    f.write(slide['feedback'])
                zipf.write(feedback_path, os.path.join("feedback", feedback_filename))
            if 'tool_call' in slide:
                tool_call_filename = f"tool_call_{slide['index'] + 1}_{slide['retry_count']}.json"
                tool_call_path = os.path.join(final_state['temp_dir'], "tool_calls", tool_call_filename)
                if not os.path.exists(os.path.dirname(tool_call_path)):
                    os.makedirs(os.path.dirname(tool_call_path))
                with open(tool_call_path, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(slide['tool_call'], f, ensure_ascii=False, indent=4)
                zipf.write(tool_call_path, os.path.join("tool_calls", tool_call_filename))


    # Sao chép file zip debug cuối cùng ra output folder
    final_zip_debug_path = os.path.join(output_folder, "slides_debug_langgraph.zip")
    shutil.copy2(zip_debug_file_path, final_zip_debug_path)
    if os.path.exists(final_state['temp_debug_dir']):
        shutil.rmtree(final_state['temp_debug_dir'])  # Xóa thư mục tạm debug

    print(f"Hoàn thành! File kết quả đã được lưu tại: {final_zip_path}")
    return final_zip_path

# --- Ví dụ cách chạy ---
if __name__ == "__main__":
    # Tạo các thư mục test nếu chưa có
    if not os.path.exists("test_input"):
        os.makedirs("test_input")
    if not os.path.exists("test_output"):
        os.makedirs("test_output")

    # Tạo một file docx giả để test
    sample_docx_path = os.path.join("test_input", "nature.docx")

    # Chạy quy trình
    try:
        process_slides_with_langgraph(sample_docx_path, "test_output")
    except Exception as e:
        print(f"Một lỗi không mong muốn đã xảy ra trong quá trình xử lý: {e}")