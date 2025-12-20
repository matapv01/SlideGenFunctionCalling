# main.py
import zipfile
import shutil
import os
import asyncio
from src.models.llm import LLM
from src.utils import config
from src.tools.tool_des import TOOLS_DICT
from src.utils.tool_retriever import ToolRetriever
from src.graph.builder import build_workflow
from src.utils.config import (
    initialize_playwright,
    LLM_MODEL,
    LLM_BASE_URL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_TOP_P,
    VLM_MAX_RETRIES
)
import time
from typing import Optional, Callable, Dict, Any

FAISS_INDEX_PATH = "faiss_tool_retriever_index"

# --- 1. Wrap the entire logic in an async function ---
async def main_workflow(
    router_flags: bool, 
    docx_file: str, 
    output_folder: str, 
    max_retries_per_slide: int = 1,
    callback: Optional[Callable[[str, Dict[Any, Any]], None]] = None,
    slide_options: Optional[Dict[str, bool]] = None,
    workflow_mode: str = 'auto'
):
    """
    Asynchronous main function to build and run the LangGraph workflow
    within a single, consistent event loop.
    
    Args:
        router_flags: Enable router flags for workflow
        docx_file: Path to input DOCX file
        output_folder: Output folder for generated slides
        max_retries_per_slide: Maximum retry attempts per slide
        callback: Optional callback function for streaming updates
                  Signature: callback(event_type: str, data: Dict[Any, Any])
        slide_options: Options for slide generation (enable_transition_slides, enable_thank_you_slide)
        workflow_mode: Workflow mode (auto, no_structure, manual)
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Helper function to emit events
    def emit_event(event_type: str, data: Dict[Any, Any]):
        if callback:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"Error in callback: {e}")

    # ===== INITIALIZE STATIC RESOURCES =====
    emit_event('status', {
        'step': 1,
        'title': 'Khởi động hệ thống',
        'description': 'Đang khởi tạo AI models...',
        'message': 'Khởi động LangGraph workflow'
    })
    
    playwright_instance = None
    final_state = None
    try:
        # Initialize LLM
        emit_event('status', {
            'step': 1,
            'title': 'Khởi động hệ thống',
            'description': 'Đang kết nối AI model...',
            'message': 'Đang khởi tạo LLM'
        })
        
        env_keys = config.setup_environment()
        api_keys = [v for v in env_keys.values() if v]
        if not api_keys:
            raise RuntimeError("Không có API key hợp lệ trong biến môi trường.")
        
        llm = LLM(
            api_keys=api_keys,
            base_url=LLM_BASE_URL,
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            top_p=LLM_TOP_P
        )

        tool_retriever = ToolRetriever(
            tools_dict=TOOLS_DICT,
            index_path=FAISS_INDEX_PATH # Pass the path to the retriever
        )
        
        emit_event('status', {
            'step': 1,
            'title': 'Khởi động hệ thống',
            'description': 'Đang khởi động trình duyệt...',
            'message': 'Khởi tạo Playwright'
        })

        # Initialize Playwright - use 'await' directly
        playwright_instance = await initialize_playwright()

        emit_event('status', {
            'step': 1,
            'title': 'Phân tích nội dung',
            'description': 'Đang đọc và phân tích tài liệu...',
            'message': 'Chuẩn bị xử lý tài liệu'
        })

        # Create temporary directories
        output_dir = os.path.join(output_folder, "output")
        output_debug_dir = os.path.join(output_folder, "output_debug")
        for dir_path in [os.path.join(output_dir, "html"), os.path.join(output_dir, "png"),
                         os.path.join(output_debug_dir, "html"), os.path.join(output_debug_dir, "png")]:
            os.makedirs(dir_path, exist_ok=True)

        # ===== BUILD AND COMPILE GRAPH =====
        workflow = build_workflow(router_flags)
        app = workflow.compile()

        # ===== DEFINE CONFIG AND INITIAL INPUT =====
        # Default slide options
        if slide_options is None:
            slide_options = {
                "enable_transition_slides": True,
                "enable_thank_you_slide": True
            }
        
        print(f"🔧 DEBUG workflow.py: slide_options = {slide_options}")
        print(f"🔧 DEBUG workflow.py: type = {type(slide_options)}")
        
        initial_input = {
            "docx_file": docx_file,
            "current_slide_index": -1,
            "retry_count": 0,
            "final_slides": [],
            "all_debug_info": [],
            "llm": llm,
            "vlm_decision": "accept",
            "slide_options": slide_options,
            "workflow_mode": workflow_mode
        }

        graph_config = {
            "configurable": {
                "llm": llm,
                "tool_retriever": tool_retriever,
                "tools_dict": TOOLS_DICT,
                "playwright_instance": playwright_instance,
                "output_folder": output_folder,
                "max_retries": max_retries_per_slide,
                "temp_dir": output_dir,
                "temp_debug_dir": output_debug_dir,
                "stream_callback": emit_event,  # Pass callback to nodes
            },
            "recursion_limit": 500
        }

        # ===== RUN THE GRAPH =====
        # Use 'await' directly instead of asyncio.run()
        print("\nStarting LangGraph workflow...")
        start_time = time.time()
        
        emit_event('status', {
            'step': 1,
            'title': 'Phân tích nội dung',
            'description': 'Đang xử lý tài liệu...',
            'message': 'Bắt đầu workflow'
        })
        
        final_state = await app.ainvoke(initial_input, config=graph_config)
        end_time = time.time()
        print(f"LangGraph workflow completed in {end_time - start_time:.2f} seconds.")

    except Exception as e:
        error_msg = str(e)
        print(f"\nAn error occurred during the workflow: {error_msg}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
        
        # Propagate error to callback
        emit_event('error_event', {
            'message': error_msg
        })
        # Re-raise so final_state remains None
        raise e
    finally:
        # ===== CLEAN UP RESOURCES =====
        if playwright_instance:
            print("\nCleaning up Playwright instance...")
            # Use 'await' directly
            await playwright_instance['browser'].close()
            await playwright_instance['playwright'].stop()
            print("Playwright instance cleaned up successfully.")

    # ===== 5. PROCESS FINAL OUTPUT =====
    if not final_state or not final_state.get('final_slides'):
        print("Processing finished, but no final slides were generated.")
        emit_event('error_event', {
            'message': 'Không có slide nào được tạo'
        })
        return

    emit_event('status', {
        'step': 3,
        'title': 'Hoàn tất',
        'description': 'Đang đóng gói kết quả...',
        'message': f'Đã tạo {len(final_state.get("final_slides", []))} slide'
    })

    # --- Zip final slides ---
    final_zip_path = os.path.join(output_folder, "slides_langgraph.zip")
    with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for slide in final_state.get('final_slides', []):
            if slide.get('html_path') and os.path.exists(slide['html_path']):
                zipf.write(slide['html_path'], os.path.join("html", os.path.basename(slide['html_path'])))
            if slide.get('png_path') and os.path.exists(slide['png_path']):
                zipf.write(slide['png_path'], os.path.join("png", os.path.basename(slide['png_path'])))
    
    # --- Zip debug slides ---
    debug_zip_path = os.path.join(output_folder, "slides_debug_langgraph.zip")
    with zipfile.ZipFile(debug_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
         for slide in final_state.get('all_debug_info', []):
            if slide.get('html_path') and os.path.exists(slide['html_path']):
                zipf.write(slide['html_path'], os.path.join("html", os.path.basename(slide['html_path'])))
            if slide.get('png_path') and os.path.exists(slide['png_path']):
                zipf.write(slide['png_path'], os.path.join("png", os.path.basename(slide['png_path'])))

    print(f"\nHoàn thành! Files have been saved and cleaned up.")
    
    # Note: Don't emit 'complete' event here, let backend emit it with correct project_name
    # emit_event('complete', {
    #     'project_name': os.path.basename(output_folder),
    #     'total_slides': len(final_state.get('final_slides', [])),
    #     'zip_path': final_zip_path
    # })

    return final_zip_path


async def main_workflow_from_chunks(
    slide_chunks: list,
    title: str,
    output_folder: str,
    callback: Optional[Callable[[str, Dict[Any, Any]], None]] = None,
    slide_options: Optional[Dict[str, bool]] = None
):
    """
    Asynchronous workflow starting from pre-generated slide chunks (bypasses document conversion)
    Used for "Create with Idea" feature where LLM generates structure directly
    
    Args:
        slide_chunks: Pre-generated slide structure from LLM
        title: Presentation title
        output_folder: Output folder for generated slides
        callback: Optional callback for streaming updates
        slide_options: Options for slide generation
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Helper function to emit events
    def emit_event(event_type: str, data: Dict[Any, Any]):
        if callback:
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    # Output directories
    output_dir = os.path.join(output_folder, "output")
    output_debug_dir = os.path.join(output_folder, "output_debug")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_debug_dir, exist_ok=True)
    
    # Create html and png subdirectories
    os.makedirs(os.path.join(output_dir, "html"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "png"), exist_ok=True)
    os.makedirs(os.path.join(output_debug_dir, "html"), exist_ok=True)
    os.makedirs(os.path.join(output_debug_dir, "png"), exist_ok=True)
    
    playwright_instance = None
    final_state = None
    
    try:
        # Initialize resources
        emit_event('status', {
            'step': 1,
            'title': 'Khởi động hệ thống',
            'description': 'Đang khởi tạo AI models...',
            'message': 'Khởi động workflow từ ý tưởng'
        })
        
        # Initialize LLM
        env_keys = config.setup_environment()
        api_keys = [v for v in env_keys.values() if v]
        if not api_keys:
            raise RuntimeError("Không có API key hợp lệ trong biến môi trường.")
        
        llm = LLM(
            api_keys=api_keys,
            base_url=LLM_BASE_URL,
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            top_p=LLM_TOP_P
        )
        
        tool_retriever = ToolRetriever(
            tools_dict=TOOLS_DICT,
            index_path=FAISS_INDEX_PATH
        )
        
        # Initialize Playwright
        emit_event('status', {
            'step': 1,
            'title': 'Khởi động hệ thống',
            'description': 'Đang khởi động trình duyệt...',
            'message': 'Khởi tạo Playwright'
        })
        
        playwright_instance = await initialize_playwright()
        
        # Build workflow
        workflow = build_workflow(False)
        app = workflow.compile()
        
        # Default slide options
        if slide_options is None:
            slide_options = {
                "enable_transition_slides": True,
                "enable_thank_you_slide": True
            }
        
        print(f"🔧 DEBUG: Processing {len(slide_chunks)} pre-generated chunks")
        print(f"🔧 DEBUG: slide_options = {slide_options}")
        
        # Initial input with pre-loaded slide_chunks (skip document conversion)
        initial_input = {
            "docx_file": None,  # No DOCX file
            "slide_chunks": slide_chunks,  # Pre-loaded chunks
            "document_structure": {"title": title},  # Minimal structure
            "current_slide_index": -1,
            "retry_count": 0,
            "final_slides": [],
            "all_debug_info": [],
            "llm": llm,
            "vlm_decision": "accept",
            "slide_options": slide_options
        }
        
        graph_config = {
            "configurable": {
                "llm": llm,
                "tool_retriever": tool_retriever,
                "tools_dict": TOOLS_DICT,
                "playwright_instance": playwright_instance,
                "output_folder": output_folder,
                "max_retries": 1,
                "temp_dir": output_dir,
                "temp_debug_dir": output_debug_dir,
                "stream_callback": emit_event,
            },
            "recursion_limit": 500
        }
        
        # Run workflow
        print("\nStarting idea-based workflow...")
        start_time = time.time()
        
        emit_event('status', {
            'step': 2,
            'title': 'Tạo slides',
            'description': f'Đang tạo {len(slide_chunks)} slides...',
            'message': 'Bắt đầu tạo slides'
        })
        
        final_state = await app.ainvoke(initial_input, config=graph_config)
        end_time = time.time()
        print(f"Idea workflow completed in {end_time - start_time:.2f} seconds.")
        
    except Exception as e:
        error_msg = str(e)
        print(f"\nError in idea workflow: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Propagate error to callback
        emit_event('error_event', {
            'message': error_msg
        })
        raise e
    finally:
        # Clean up Playwright
        if playwright_instance:
            print("\nCleaning up Playwright...")
            await playwright_instance['browser'].close()
            await playwright_instance['playwright'].stop()
    
    # Process final output
    if not final_state or not final_state.get('final_slides'):
        print("No final slides generated")
        emit_event('error_event', {'message': 'Không có slide nào được tạo'})
        return None
    
    emit_event('status', {
        'step': 3,
        'title': 'Hoàn tất',
        'description': 'Đang đóng gói kết quả...',
        'message': f'Đã tạo {len(final_state.get("final_slides", []))} slide'
    })
    
    # Zip final slides
    final_zip_path = os.path.join(output_folder, "slides_langgraph.zip")
    with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for slide in final_state.get('final_slides', []):
            if slide.get('html_path') and os.path.exists(slide['html_path']):
                zipf.write(slide['html_path'], os.path.join("html", os.path.basename(slide['html_path'])))
            if slide.get('png_path') and os.path.exists(slide['png_path']):
                zipf.write(slide['png_path'], os.path.join("png", os.path.basename(slide['png_path'])))
    
    # Zip debug slides
    debug_zip_path = os.path.join(output_folder, "slides_debug_langgraph.zip")
    with zipfile.ZipFile(debug_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for slide in final_state.get('all_debug_info', []):
            if slide.get('html_path') and os.path.exists(slide['html_path']):
                zipf.write(slide['html_path'], os.path.join("html", os.path.basename(slide['html_path'])))
            if slide.get('png_path') and os.path.exists(slide['png_path']):
                zipf.write(slide['png_path'], os.path.join("png", os.path.basename(slide['png_path'])))
    
    print(f"\nCompleted! ZIP saved at: {final_zip_path}")
    return final_zip_path


# # --- 2. Call the async main function using asyncio.run() only ONCE ---
# if __name__ == "__main__":
#     sample_docx_path = os.path.join("data", "input", "test_ttcs - heading.docx")
    
#     # This single call starts the event loop, runs everything inside main_workflow,
#     # and then closes the loop correctly after all tasks are done.
#     asyncio.run(main_workflow(False, sample_docx_path, "data"))