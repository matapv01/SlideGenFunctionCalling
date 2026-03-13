# File: backend/workflows/slidegen_workflow/main.py

import zipfile
import os
import time
import logging
from typing import Optional, Callable, Dict, Any, Tuple
from backend.workflows.slidegen_workflow.graph.builder import build_workflow
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend.domain.ports.llm_provider import LLMProvider
from backend.domain.ports.capture_provider import CaptureProvider
from backend.domain.ports.parser_provider import ParserProvider
from backend.domain.ports.tool_retrieve_provider import ToolRetrieveProvider

logger = logging.getLogger(__name__)


# HELPER FUNCTIONS
def _setup_output_dirs(output_folder: str) -> Tuple[str, str]:
    """Creates necessary directories for output."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    output_dir = os.path.join(output_folder, "output")
    output_debug_dir = os.path.join(output_folder, "output_debug")
    
    for base in [output_dir, output_debug_dir]:
        os.makedirs(os.path.join(base, "html"), exist_ok=True)
        os.makedirs(os.path.join(base, "png"), exist_ok=True)
        
    return output_dir, output_debug_dir

def _emit_event(callback, event_type: str, data: Dict[Any, Any]):
    """Safe event emission."""
    if callback:
        try:
            callback(event_type, data)
        except Exception as e:
            logger.error(f"Error in callback: {e}")

# ==============================================================================
# MAIN WORKFLOWS
# ==============================================================================

async def main_workflow(
    router_flags: bool,
    docx_file: str,
    output_folder: str,
    infra_providers: Dict[str, Any], # 🟢 NHẬN TỪ WORKFLOW SERVICE
    max_retries_per_slide: int = 1,
    callback: Optional[Callable[[str, Dict[Any, Any]], None]] = None,
    slide_options: Optional[Dict[str, bool]] = None
):
    output_dir, output_debug_dir = _setup_output_dirs(output_folder)
    _emit_event(callback, 'status', {'step': 1, 'title': 'Starting', 'message': 'System ready'})

    try:
        # 1. 🟢 LẤY CÁC INSTANCE ĐÃ CÓ SẴN (KHÔNG KHỞI TẠO MỚI)
        llm_provider: LLMProvider = infra_providers['llm_provider']
        capture_provider: CaptureProvider = infra_providers['capture_provider']
        parser_provider: ParserProvider = infra_providers['parser_provider']
        tool_retriever: ToolRetrieveProvider = infra_providers['tool_retriever']
        conversion_service = infra_providers.get('conversion_service')

        # Vì node slide_generator cần LangChain Runnable, ta lấy từ client
        langchain_llm = llm_provider.llm_client 

        # 2. Setup Graph
        workflow = build_workflow(router_flags)
        app = workflow.compile()

        # 3. Graph Config (Inject công cụ vào các Node)
        graph_config = {
            "configurable": {
                "llm": langchain_llm,
                "tool_retriever": tool_retriever,
                "capture_provider": capture_provider,
                "parser_provider": parser_provider,
                "tools_dict": TOOLS_DICT,
                "conversion_service": conversion_service,
                "output_folder": output_folder,
                "temp_dir": output_dir,
                "temp_debug_dir": output_debug_dir,
                "stream_callback": lambda t, d: _emit_event(callback, t, d),
            },
            "recursion_limit": 500
        }

        initial_input = {
            "docx_file": docx_file,
            "current_slide_index": -1,
            "retry_count": 0,
            "final_slides": [],
            "all_debug_info": [],
            "vlm_decision": "accept",
            "slide_options": slide_options or {}
        }

        # Run
        print("\n🚀 Running Workflow with Singleton Infrastructure...")
        final_state = await app.ainvoke(initial_input, config=graph_config)
        print("\n🚀 Workflow completed.")
        return output_folder

    except Exception as e:
        logger.error(f"❌ Workflow Error: {e}")
        return None


async def main_workflow_from_chunks(
    slide_chunks: list,
    title: str,
    output_folder: str,
    infra_providers: Dict[str, Any], # 🟢 NHẬN TỪ WORKFLOW SERVICE
    callback: Optional[Callable[[str, Dict[Any, Any]], None]] = None,
    slide_options: Optional[Dict[str, bool]] = None
):
    """
    Idea Workflow: Chunks -> Slides
    Bypasses Parser, uses same Infrastructure for everything else.
    """
    output_dir, output_debug_dir = _setup_output_dirs(output_folder)
    
    _emit_event(callback, 'status', {
        'step': 1, 'title': 'Starting', 'description': 'Initializing Infrastructure...', 'message': 'Booting System'
    })

    try:
        # --- INFRASTRUCTURE INITIALIZATION ---
        llm_provider: LLMProvider = infra_providers['llm_provider']
        capture_provider: CaptureProvider = infra_providers['capture_provider']
        parser_provider: ParserProvider = infra_providers['parser_provider']
        tool_retriever: ToolRetrieveProvider = infra_providers['tool_retriever']
        conversion_service = infra_providers.get('conversion_service')
        langchain_llm = llm_provider.llm_client

        # Router flag is False because we don't need to route document conversion
        workflow = build_workflow(router_flags=False) 
        app = workflow.compile()

        if slide_options is None:
            slide_options = {"enable_transition_slides": True, "enable_thank_you_slide": True}

        # --- CONFIG & INPUT ---
        graph_config = {
            "configurable": {
                "llm": langchain_llm,
                "tool_retriever": tool_retriever,
                "capture_provider": capture_provider,
                "parser_provider": parser_provider,
                "tools_dict": TOOLS_DICT,
                "conversion_service": conversion_service,
                "output_folder": output_folder,
                "max_retries": 1,
                "temp_dir": output_dir,
                "temp_debug_dir": output_debug_dir,
                "stream_callback": lambda t, d: _emit_event(callback, t, d),
            },
            "recursion_limit": 500
        }

        initial_input = {
            "docx_file": None,
            "slide_chunks": slide_chunks,
            "document_structure": {"title": title},
            "current_slide_index": -1,
            "retry_count": 0,
            "final_slides": [],
            "all_debug_info": [],
            "vlm_decision": "accept",
            "slide_options": slide_options
        }

        # --- EXECUTION ---
        print(f"\n🚀 Starting Workflow (Idea Mode - {len(slide_chunks)} chunks)...")
        start_time = time.time()

        _emit_event(callback, 'status', {
            'step': 2, 'title': 'Creating Slides', 'description': f'Generating {len(slide_chunks)} slides...', 'message': 'Generating Slides'
        })

        final_state = await app.ainvoke(initial_input, config=graph_config)

        print(f"✅ Workflow completed in {time.time() - start_time:.2f}s")

        # --- FINALIZE ---
        if not final_state or not final_state.get('final_slides'):
            _emit_event(callback, 'error', {'message': 'No slides were created'})
            return None

        _emit_event(callback, 'status', {
            'step': 3, 'title': 'Completed', 'description': 'Packaging...', 
            'message': f'Created {len(final_state.get("final_slides", []))} slides'
        })

        print(f"📦 Output saved to folder: {output_folder}")
        return output_folder

    except Exception as e:
        print(f"❌ Workflow Failed: {e}")
        import traceback; traceback.print_exc()
        return None