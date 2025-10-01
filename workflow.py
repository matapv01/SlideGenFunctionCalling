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
from src.utils.config import initialize_playwright
import time

FAISS_INDEX_PATH = "faiss_tool_retriever_index"

# --- 1. Wrap the entire logic in an async function ---
async def main_workflow(router_flags: bool, docx_file: str, output_folder: str, max_retries_per_slide: int = 1):
    """
    Asynchronous main function to build and run the LangGraph workflow
    within a single, consistent event loop.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # ===== INITIALIZE STATIC RESOURCES =====
    playwright_instance = None
    final_state = None
    try:
        # Initialize LLM
        env_keys = config.setup_environment()
        api_keys = [v for v in env_keys.values() if v]
        if not api_keys:
            raise RuntimeError("Không có API key hợp lệ trong biến môi trường.")
        
        llm = LLM(
            api_keys=api_keys,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model="gemini-2.5-flash",
            temperature=0.5,
            max_tokens=20000,
        )

        tool_retriever = ToolRetriever(
            tools_dict=TOOLS_DICT,
            index_path=FAISS_INDEX_PATH # Pass the path to the retriever
        )
        

        # Initialize Playwright - use 'await' directly
        playwright_instance = await initialize_playwright()

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
        initial_input = {
            "docx_file": docx_file,
            "current_slide_index": -1,
            "retry_count": 0,
            "final_slides": [],
            "all_debug_info": [],
            "vlm_decision": "accept"
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
            },
            "recursion_limit": 500
        }

        # ===== RUN THE GRAPH =====
        # Use 'await' directly instead of asyncio.run()
        print("\nStarting LangGraph workflow...")
        start_time = time.time()
        final_state = await app.ainvoke(initial_input, config=graph_config)
        end_time = time.time()
        print(f"LangGraph workflow completed in {end_time - start_time:.2f} seconds.")

    except Exception as e:
        print(f"\nAn error occurred during the workflow: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
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
        return

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


# --- 2. Call the async main function using asyncio.run() only ONCE ---
if __name__ == "__main__":
    sample_docx_path = os.path.join("data", "input", "test_ttcs - heading.docx")
    
    # This single call starts the event loop, runs everything inside main_workflow,
    # and then closes the loop correctly after all tasks are done.
    asyncio.run(main_workflow(False, sample_docx_path, "data"))