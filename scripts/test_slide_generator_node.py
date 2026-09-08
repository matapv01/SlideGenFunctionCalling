import os
import sys
import json
from dotenv import load_dotenv

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from backend.infrastructure.rag.gemini_provider import GeminiToolRetrieveProvider
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
from backend import config as backend_config

class DummyLLM:
    """Mock LLM object carrying model, base_url, and api_key attributes for generate_slide node."""
    def __init__(self):
        self.model_name = os.environ.get("OPENAI_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
        self.openai_api_base = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
        self.openai_api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.max_tokens = 4096
        self.temperature = 0.3

def run_test_on_dataset_sample(sample_index: int = 0):
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "rl", "data", "sft_function_call_dataset.json")
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset file not found at: {dataset_path}")
        return
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    if sample_index >= len(dataset):
        print(f"❌ sample_index {sample_index} out of range. Dataset has {len(dataset)} samples.")
        return
        
    sample = dataset[sample_index]
    print("=" * 70)
    print(f"🧪 Testing node `generate_slide` on Sample #{sample_index}")
    print(f"Category: {sample.get('category')}")
    print(f"Doc ID: {sample.get('doc_id')}, Slide Index: {sample.get('slide_index')}")
    print("-" * 70)
    print(f"Slide Content:\n{sample.get('slide_content')[:200]}...")
    print("=" * 70)
    
    # Construct state for generate_slide node
    state = {
        "current_slide_index": sample.get("slide_index", 0),
        "length_slide_chunks": 5,
        "current_slide_text": sample["slide_content"],
        "current_slide_plan": {
            "action": sample.get("category", "CONTENT_TOOLS"),
            "thought": "Create an impactful layout matching the design instructions."
        },
        "current_slide_context_map": sample.get("style_context", ""),
        "use_cot": True,
    }
    
    # Try to initialize real tool_retriever if index or GEMINI_API_KEY is available
    tool_retriever = None
    try:
        gemini_key = os.environ.get("GEMINI_API_KEY")
        faiss_index_path = getattr(backend_config, "FAISS_INDEX_PATH", "faiss_tool_retriever_index")
        tool_retriever = GeminiToolRetrieveProvider(
            tools_dict=TOOLS_DICT,
            index_path=faiss_index_path,
            api_key=gemini_key
        )
        print("🔍 Successfully initialized GeminiToolRetrieveProvider (FAISS Vector Search ready)!")
    except Exception as e:
        print(f"⚠️ ToolRetriever info: {e}. (Will fallback to category tool list if unavailable)")

    # Construct RunnableConfig for LangGraph node
    llm = DummyLLM()
    config = {
        "configurable": {
            "llm": llm,
            "planner_llm": llm,
            "tools_dict": TOOLS_DICT,
            "tool_retriever": tool_retriever,
            "output_format": "xml",
        }
    }
    
    # Execute the actual generate_slide node
    try:
        new_state = generate_slide(state, config)
        print("\n✅ NODE EXECUTION SUCCESSFUL!")
        print("-" * 70)
        tool_call = new_state.get("current_tool_call")
        print("Generated Tool Call:")
        print(json.dumps(tool_call, indent=2, ensure_ascii=False))
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ NODE EXECUTION FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Change index to test different samples from sft_function_call_dataset.json
    run_test_on_dataset_sample(sample_index=15)
