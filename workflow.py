# main.py
import zipfile
import shutil
from src.models.llm import LLM
from src.utils import config
import os
from src.tools.tool_des import TOOLS_DICT
from src.graph.builder import build_workflow
import asyncio


# -- Xây dựng và thực thi Graph ---

def process_slides_with_langgraph(router_flags: bool, docx_file: str, output_folder: str, max_retries_per_slide: int = 6):
    """
    Hàm chính để xây dựng và chạy luồng công việc LangGraph.
    """

    if not os.path.exists("test_output"):
        os.makedirs("test_output")

    # ===== KHỞI TẠO LLM INSTANCE =====
    # KHỞI TẠO LLM INSTANCE
    env_keys = config.setup_environment()
    api_keys = [v for v in env_keys.values() if v]
    if not api_keys:
        raise RuntimeError("Không có API key hợp lệ trong biến môi trường.")

    llm = LLM(
        api_keys=api_keys,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        # model="gemini-2.5-flash",
        model="gemini-2.5-pro",
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
            
    # ===== TẠO GRAPH VỚI CÁC NODE =====
    workflow = build_workflow(router_flags)

    # Biên dịch đồ thị với các tùy chọn
    app = workflow.compile()

    # ===== TRUYỀN LLM_INSTANCE VÀO STATE BAN ĐẦU =====
    # Chuẩn bị input ban đầu cho graph
    initial_input = {
        "docx_file": docx_file,
        "output_folder": output_folder,
        "max_retries": max_retries_per_slide,
        "llm": llm,
        "tools": TOOLS_DICT,  # Truyền vào danh sách công cụ
        "current_slide_index": -1,
        "retry_count": 0,
        "final_slides": [],
        "temp_dir": os.path.join(output_folder, "temp"),
        "temp_debug_dir": temp_debug_dir,
        "all_debug_info": [],  # Thêm khởi tạo cho all_debug_info
        "vlm_decision": "accept"  # Đặt mặc định là accept
    }
    
    # Chạy graph
    recursionLimit = {"recursion_limit": 500}
    final_state = asyncio.run(app.ainvoke(initial_input, config=recursionLimit))

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

# # --- Ví dụ cách chạy ---
# if __name__ == "__main__":
#     # Tạo các thư mục test nếu chưa có
#     if not os.path.exists("test_input"):
#         os.makedirs("test_input")
#     if not os.path.exists("test_output"):
#         os.makedirs("test_output")

#     # Tạo một file docx giả để test
#     sample_docx_path = os.path.join("test_input", "test_ttcs - heading.docx")

#     # Chạy quy trình
#     try:
#         process_slides_with_langgraph(True, sample_docx_path, "test_output")
#     except Exception as e:
#         print(f"Một lỗi không mong muốn đã xảy ra trong quá trình xử lý: {e}")