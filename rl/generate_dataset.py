import os
import sys
import json
import asyncio
from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv()
from langchain_core.callbacks import BaseCallbackHandler

# Đảm bảo PYTHONPATH nhận diện được backend của dự án
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.api.dependencies import (
    _retriever_infra as tool_retriever,
    _slidegen_llm as llm_provider,
    _capture_infra as capture_provider,
    _parser_infra as parser_provider
)
from backend.workflows.slidegen_workflow.graph.builder import build_workflow
from backend.workflows.doc_workflow.main import run_doc_workflow
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT


class PromptCaptureCallbackHandler(BaseCallbackHandler):
    """
    Lắng nghe sự kiện chạy của LangGraph để trích xuất 
    ngữ cảnh prompt và tool schemas thật tại node slide_generator.
    """
    def __init__(self):
        self.captured_samples = []

    def on_chat_model_start(self, serialized, messages, **kwargs):
        # Trích xuất tools
        tools = []
        if "tools" in kwargs:
            tools = kwargs["tools"]
        elif "kwargs" in kwargs and "tools" in kwargs["kwargs"]:
            tools = kwargs["kwargs"]["tools"]
        elif "invocation_params" in kwargs and "tools" in kwargs["invocation_params"]:
            tools = kwargs["invocation_params"]["tools"]

        # Trích xuất System Prompt và User Prompt
        chat_messages = messages[0] if isinstance(messages[0], list) else messages
        system_prompt = ""
        user_prompt = ""
        for msg in chat_messages:
            if msg.type == "system":
                system_prompt = msg.content
            elif msg.type == "human":
                user_prompt = msg.content

        self.captured_samples.append({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "tools": tools
        })


async def build_dataset_from_workflow_async(docx_path: str, output_json_path: str):
    # 1. Chạy tiền xử lý DOCX để lấy chunks
    doc_config = {
        "configurable": {
            "llm": llm_provider.llm_client,
        },
        "recursion_limit": 500,
    }
    
    print(f"\n[Dataset Gen] Preprocessing docx: {docx_path}...")
    doc_state = await run_doc_workflow(
        docx_file=docx_path,
        workflow_mode="auto_no_heading",
        slide_options={},
        graph_config=doc_config,
    )
    
    # 2. Biên dịch slidegen_workflow
    workflow = build_workflow(router_flags=False)
    app = workflow.compile()
    
    # Đăng ký callback bắt prompt
    capture_handler = PromptCaptureCallbackHandler()
    
    graph_config = {
        "configurable": {
            "llm": llm_provider.llm_client,
            "tool_retriever": tool_retriever,
            "capture_provider": capture_provider,
            "parser_provider": parser_provider,
            "tools_dict": TOOLS_DICT,
            "output_folder": "./temp_dataset_out",
            "temp_dir": "./temp_dataset_out/output",
            "temp_debug_dir": "./temp_dataset_out/output_debug",
        },
        "callbacks": [capture_handler],
        "recursion_limit": 500
    }
    
    initial_input = {
        "docx_file": docx_path,
        "workflow_mode": "auto_no_heading",
        "document_title": doc_state.get("document_title"),
        "document_structure": doc_state.get("document_structure", []),
        "document_outline": doc_state.get("document_outline", []),
        "slide_chunks": doc_state.get("slide_chunks", []),
        "slide_positions": doc_state.get("slide_positions", []),
        "slide_context_maps": doc_state.get("slide_context_maps", []),
        "current_slide_index": -1,
        "retry_count": 0,
        "final_slides": [],
        "all_debug_info": [],
        "vlm_decision": "accept",
        "slide_options": {}
    }
    
    print("[Dataset Gen] Executing LangGraph workflow and capturing prompts...")
    await app.ainvoke(initial_input, config=graph_config)
    
    # 3. Lưu danh sách prompt đã capture ra file JSON sạch
    print(f"[Dataset Gen] Captured {len(capture_handler.captured_samples)} prompts.")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(capture_handler.captured_samples, f, indent=2, ensure_ascii=False)
    print(f"[Dataset Gen] Dataset saved successfully to: {output_json_path}")

def main():
    input_docx = os.getenv("INPUT_DOCX", "../Mô tả chi tiết về dự án SlideGen.docx")
    output_json = os.getenv("OUTPUT_JSON", "./slidegen_rl_dataset.json")
    
    if not os.path.exists(input_docx):
        print(f"Error: Input document '{input_docx}' not found.")
        sys.exit(1)
        
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(build_dataset_from_workflow_async(input_docx, output_json))

if __name__ == "__main__":
    main()
