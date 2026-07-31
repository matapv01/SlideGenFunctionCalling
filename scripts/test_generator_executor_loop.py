import os
import sys
import json
import time
from dotenv import load_dotenv

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from backend.infrastructure.rag.gemini_provider import GeminiToolRetrieveProvider
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import tool_call_executor
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT, execute_tool
from backend import config as backend_config


class DummyLLM:
    """Mock LLM object carrying model, base_url, and api_key attributes for generate_slide node."""
    def __init__(self):
        self.model_name = os.environ.get("OPENAI_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
        self.openai_api_base = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
        self.openai_api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.max_tokens = 4096
        self.temperature = 0.3


def run_generator_executor_test(sample_index: int = 1, max_retries: int = 3):
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
    print("=" * 80)
    print(f"🧪 TEST LOOP: `slide_generator` 🔄 `tool_call_executor` (Sample #{sample_index})")
    print(f"Category: {sample.get('category')}")
    print(f"Doc ID: {sample.get('doc_id')}, Slide Index: {sample.get('slide_index')}")
    print("-" * 80)
    print(f"Slide Content:\n{sample.get('slide_content')[:180]}...")
    print("=" * 80)
    
    # Construct initial state
    state = {
        "current_slide_index": sample.get("slide_index", 0),
        "length_slide_chunks": 5,
        "current_slide_text": sample["slide_content"],
        "current_slide_plan": {
            "action": sample.get("category", "CONTENT_TOOLS"),
            "thought": "Create an impactful layout matching design instructions."
        },
        "current_slide_context_map": sample.get("style_context", ""),
        "use_cot": True,
        "retry_count": 0,
        "executor_feedback": "",
        "executor_decision": "fail"
    }
    
    # Initialize tool_retriever
    tool_retriever = None
    try:
        gemini_key = os.environ.get("GEMINI_API_KEY")
        faiss_index_path = getattr(backend_config, "FAISS_INDEX_PATH", "faiss_tool_retriever_index")
        tool_retriever = GeminiToolRetrieveProvider(
            tools_dict=TOOLS_DICT,
            index_path=faiss_index_path,
            api_key=gemini_key
        )
        print("🔍 ToolRetriever ready!")
    except Exception as e:
        print(f"⚠️ ToolRetriever info: {e}. (Falling back to category tool list)")

    llm = DummyLLM()
    config = {
        "configurable": {
            "llm": llm,
            "planner_llm": llm,
            "tools_dict": TOOLS_DICT,
            "tool_retriever": tool_retriever,
        }
    }
    
    start_time = time.time()
    success = False
    
    dash_line = "─" * 80
    for loop_attempt in range(1, max_retries + 1):
        print(f"\n{dash_line}")
        print(f"🔄 LOOP ATTEMPT {loop_attempt}/{max_retries}")
        print(f"{dash_line}")
        
        # 1. Run Node: slide_generator
        print("1️⃣ [NODE] slide_generator generating tool call...")
        state = generate_slide(state, config)
        tool_call = state.get("current_tool_call", {})
        print(f"   Generated Tool: {tool_call.get('name')}")
        print(f"   Args Keys: {list(tool_call.get('arguments', {}).keys())}")
        
        # 2. Run Node: tool_call_executor
        print("\n2️⃣ [NODE] tool_call_executor validating tool call...")
        state = tool_call_executor(state, config)
        
        decision = state.get("executor_decision")
        if decision == "pass":
            print("\n✅ EXECUTOR PASSED! Tool call validation successful.")
            html_content = execute_tool(tool_call)
            state["current_html_content"] = html_content
            
            if html_content:
                output_html_path = os.path.join(os.path.dirname(__file__), "test_output_slide.html")
                with open(output_html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                clean_path = output_html_path.replace("\\", "/")
                print(f"📄 HTML Rendered Length: {len(html_content)} characters")
                print(f"🖼️ Saved rendered HTML slide file to: [test_output_slide.html](file:///{clean_path})")
                success = True
            else:
                print("⚠️ execute_tool returned empty HTML. Tool call execution failed.")
            break
        else:
            print(f"\n❌ EXECUTOR FAILED on attempt {loop_attempt}!")
            print(f"Feedback passed to generator for attempt {loop_attempt + 1}:")
            print(f"   {state.get('executor_feedback')}")

    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    if success:
        print(f"🎉 TEST PASSED IN {state.get('retry_count', 1)} ATTEMPT(S)! Total Time: {total_time:.2f}s")
        print("Final Tool Call:")
        print(json.dumps(state.get("current_tool_call"), indent=2, ensure_ascii=False))
    else:
        print(f"❌ TEST FAILED AFTER {max_retries} ATTEMPTS. Total Time: {total_time:.2f}s")
    print("=" * 80)


if __name__ == "__main__":
    # Test on sample_index=1 or change index to test other dataset samples
    run_generator_executor_test(sample_index=20, max_retries=3)
