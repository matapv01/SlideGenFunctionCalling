"""
========================================================================================
🚀 HƯỚNG DẪN CHẠY BENCHMARK: GENERATOR 🔄 EXECUTOR LOOP
========================================================================================

🎯 Chạy 1 mẫu duy nhất theo Dataset Index (Ví dụ: mẫu #119):
    python scripts/test_generator_executor_loop.py --sample 119

🔍 Chạy 1 mẫu kèm in CHI TIẾT JSON Output của Generator để debug:
    python scripts/test_generator_executor_loop.py --sample 119 -v

📦 Chạy mặc định (Mẫu từ index 0 đến 4):
    python scripts/test_generator_executor_loop.py

📍 Chạy theo khoảng index cụ thể (Ví dụ: từ mẫu 0 đến mẫu 49):
    python scripts/test_generator_executor_loop.py --start 0 --end 49

🎲 Chạy ngẫu nhiên N mẫu trong dataset (Ví dụ: 10 mẫu):
    python scripts/test_generator_executor_loop.py --n 10

🔄 Chạy kèm tùy chỉnh số lần thử lại tối đa (max retries):
    python scripts/test_generator_executor_loop.py --start 0 --end 49 --max-retries 3

💾 Kết quả chi tiết sẽ tự động lưu vào thư mục:
    C:\\vscode\\SlideGen\\scripts\\result_test_CoT\\test_generator_executor_results_start<start>_end<end>.json
========================================================================================
"""

from typing import Optional
import os
import sys
import json
import time
import random
from collections import Counter
from dotenv import load_dotenv

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from backend.infrastructure.rag.gemini_provider import GeminiToolRetrieveProvider
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import tool_call_executor
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend import config as backend_config


class DummyLLM:
    """Mock LLM object carrying model, base_url, and api_key attributes for generate_slide node."""
    def __init__(self):
        self.model_name = os.environ.get("OPENAI_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
        self.openai_api_base = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
        self.openai_api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
        self.max_tokens = 4096
        self.temperature = 0.3

    def invoke(self, messages):
        class DummyResponse:
            content = "Use a clean layout with consistent colors and clear visual hierarchy."
        return DummyResponse()


def test_single_sample_loop(sample: dict, config: dict, max_retries: int = 5) -> dict:
    """
    Run the generate_slide 🔄 tool_call_executor loop on a single dataset sample.
    """
    ground_truth = sample.get("tool_call", {})
    gt_tool_name = ground_truth.get("name") if isinstance(ground_truth, dict) else (sample.get("ground_truth_tool") or sample.get("tool_name", "Unknown"))
    category = sample.get("category", "CONTENT_TOOLS")
    
    result = {
        "category": category,
        "slide_index": sample.get("slide_index"),
        "doc_id": sample.get("doc_id"),
        "ground_truth_tool": gt_tool_name,
        "use_cot": True,
        "attempts": 0,
        "final_status": "fail",
        "predicted_tool": None,
        "tool_name_match": False,
        "executor_errors": [],
        "thinking_text": "",
        "latency_seconds": 0.0,
    }
    
    slide_idx = sample.get("slide_index", 0)
    state = {
        "current_slide_index": slide_idx,
        "length_slide_chunks": max(5, slide_idx + 1),
        "current_slide_text": sample.get("slide_content", ""),
        "current_slide_plan": {
            "action": category,
            "thought": "Create an impactful layout matching design instructions."
        },
        "current_slide_context_map": sample.get("style_context", ""),
        "use_cot": True,
        "retry_count": 0,
        "executor_feedback": "",
        "executor_decision": "fail"
    }
    
    start_time = time.time()
    
    for attempt in range(1, max_retries + 1):
        result["attempts"] = attempt
        
        # 1. Run Node: slide_generator
        state = generate_slide(state, config)
        tool_call = state.get("current_tool_call", {})
        predicted_name = tool_call.get("name", "default_fallback")
        result["predicted_tool"] = predicted_name
        
        # If verbose mode is enabled, print raw LLM output for THIS attempt immediately
        if config.get("verbose"):
            raw_resp = state.get("raw_llm_response", "")
            print(f"\n  📄 [Attempt {attempt}] RAW LLM RESPONSE:")
            print("     " + raw_resp.replace("\n", "\n     ") if raw_resp else "     (Empty response)")
            print(f"\n  📦 [Attempt {attempt}] PARSED TOOL CALL:")
            print(f"     Name: {predicted_name}")
            print("     Arguments:")
            print(json.dumps(tool_call.get("arguments", {}), indent=8, ensure_ascii=False))
        
        # 2. Run Node: tool_call_executor
        state = tool_call_executor(state, config)
        
        decision = state.get("executor_decision")
        if decision == "pass":
            result["final_status"] = "pass"
            result["tool_name_match"] = (predicted_name == gt_tool_name)
            break
        else:
            # Capture errors from executor feedback for statistics
            fb = state.get("executor_feedback", "")
            for line in fb.split("\n"):
                if line.startswith("- ") or line.startswith("• "):
                    err_text = line.split(":", 1)[0].replace("- ", "").replace("• ", "").strip()
                    result["executor_errors"].append(err_text)
                    
    result["latency_seconds"] = round(time.time() - start_time, 2)
    return result, state


def run_benchmark(
    num_samples: Optional[int] = None,
    start_index: Optional[int] = None,
    end_index: Optional[int] = None,
    sample_index: Optional[int] = None,
    max_retries: int = backend_config.EXECUTOR_MAX_RETRIES,
    verbose: bool = False,
    seed: int = 42
):
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "rl", "data", "sft_function_call_dataset.json")
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset file not found at: {dataset_path}")
        return
        
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    # Range / Single sample slicing logic
    if sample_index is not None:
        if 0 <= sample_index < len(dataset):
            test_samples = [dataset[sample_index]]
            print(f"🎯 Selected SINGLE sample: Dataset Index #{sample_index}")
        else:
            print(f"❌ sample_index {sample_index} out of range (0..{len(dataset)-1})")
            return
    elif start_index is not None or end_index is not None:
        start_idx = max(0, start_index if start_index is not None else 0)
        end_idx = min(len(dataset), (end_index + 1) if end_index is not None else len(dataset))
        test_samples = dataset[start_idx:end_idx]
        print(f"📍 Selected dataset range: Index {start_idx} to {end_idx - 1} ({len(test_samples)} samples)")
    elif num_samples and num_samples < len(dataset):
        random.seed(seed)
        test_samples = random.sample(dataset, num_samples)
        print(f"🎲 Randomly sampled {len(test_samples)} items from dataset")
    else:
        test_samples = dataset
        print(f"📦 Selected all {len(test_samples)} items from dataset")
        
    num_samples = len(test_samples)
    if num_samples == 0:
        print("❌ No samples selected. Please check your start and end index.")
        return

    print("=" * 80)
    print(f"🚀 BENCHMARK: Generator 🔄 Executor Loop ({num_samples} samples, Max Retries: {max_retries})")
    print("=" * 80)
    
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
        print("🔍 ToolRetriever initialized successfully!")
    except Exception as e:
        print(f"⚠️ ToolRetriever info: {e}. (Falling back to category tool list)")

    llm = DummyLLM()
    config = {
        "configurable": {
            "llm": llm,
            "planner_llm": llm,
            "tools_dict": TOOLS_DICT,
            "tool_retriever": tool_retriever,
        },
        "verbose": verbose or (sample_index is not None)
    }
    
    results = []
    dash_line = "─" * 80
    
    for idx, sample in enumerate(test_samples, start=1):
        gt_tool = sample.get("tool_call", {}).get("name", "Unknown") if isinstance(sample.get("tool_call"), dict) else (sample.get("ground_truth_tool") or sample.get("tool_name", "Unknown"))
        sample_dataset_index = dataset.index(sample) if sample in dataset else idx - 1
        print(f"\n{dash_line}")
        print(f"📝 SAMPLE {idx}/{num_samples} (Dataset Index #{sample_dataset_index}) — doc={sample.get('doc_id')}, slide={sample.get('slide_index')}, cat={sample.get('category')}")
        print(f"   Ground Truth Tool: {gt_tool}")
        print(f"   Content snippet: {sample.get('slide_content', '')[:100]}...")
        
        result, final_state = test_single_sample_loop(sample, config, max_retries=max_retries)
        results.append(result)

        status_icon = "✅" if result["final_status"] == "pass" else "❌"
        print(f"\n  {status_icon} Result: {result['final_status'].upper()} (Attempt {result['attempts']}/{max_retries}, {result['latency_seconds']}s)")
        print(f"     Predicted Tool: {result['predicted_tool']}")

    # 📊 Compute Benchmark Statistics
    total = len(results)
    passed = sum(1 for r in results if r["final_status"] == "pass")
    tool_matches = sum(1 for r in results if r["tool_name_match"])
    first_try_pass = sum(1 for r in results if r["final_status"] == "pass" and r["attempts"] == 1)
    avg_attempts = sum(r["attempts"] for r in results) / total if total else 0
    avg_latency = sum(r["latency_seconds"] for r in results) / total if total else 0

    # Breakdown by attempt count
    attempts_counter = Counter(r["attempts"] for r in results if r["final_status"] == "pass")
    failed_count = sum(1 for r in results if r["final_status"] != "pass")
    attempts_breakdown = {f"attempt_{att}": attempts_counter.get(att, 0) for att in range(1, max_retries + 1)}
    attempts_breakdown["failed"] = failed_count

    print("\n" + "=" * 80)
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("=" * 80)
    print(f"  Pass Rate:          {passed}/{total} ({100*passed/total:.1f}%)")
    print(f"  First-Try Pass:     {first_try_pass}/{total} ({100*first_try_pass/total:.1f}%)")
    print(f"  Tool Name Match:    {tool_matches}/{total} ({100*tool_matches/total:.1f}%)")
    print(f"  Avg Attempts:       {avg_attempts:.1f}")
    print(f"  Avg Total Latency:  {avg_latency:.1f}s")
    
    print("\n  📋 ATTEMPTS BREAKDOWN (Passed samples):")
    for att in range(1, max_retries + 1):
        cnt = attempts_counter.get(att, 0)
        pct = (100 * cnt / total) if total else 0
        print(f"     Attempt {att}: {cnt}/{total} ({pct:.1f}%)")
    if failed_count > 0:
        print(f"     Failed (>{max_retries} attempts): {failed_count}/{total} ({100*failed_count/total:.1f}%)")

    # Error breakdown
    all_errors = []
    for r in results:
        all_errors.extend(r["executor_errors"])
    if all_errors:
        print(f"\n  📋 ERROR BREAKDOWN ({len(all_errors)} total error flags):")
        for err, cnt in Counter(all_errors).most_common(10):
            print(f"     {err}: {cnt}")

    # Per-category breakdown
    categories = set(r["category"] for r in results)
    if len(categories) > 1:
        print(f"\n  📋 PER-CATEGORY BREAKDOWN:")
        for cat in sorted(categories):
            cat_results = [r for r in results if r["category"] == cat]
            cat_pass = sum(1 for r in cat_results if r["final_status"] == "pass")
            print(f"     {cat}: {cat_pass}/{len(cat_results)} pass")

    # Save detailed JSON benchmark results to disk
    output_dir = os.path.join(os.path.dirname(__file__), "result_test_CoT")
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine sample index bounds for filename
    start_sample_idx = dataset.index(test_samples[0]) if test_samples and test_samples[0] in dataset else 0
    end_sample_idx = dataset.index(test_samples[-1]) if test_samples and test_samples[-1] in dataset else len(test_samples) - 1
    
    filename = f"test_generator_executor_results_start{start_sample_idx}_end{end_sample_idx}.json"
    output_json_path = os.path.join(output_dir, filename)
    with open(output_json_path, "w", encoding="utf-8") as f_json:
        json.dump({
            "summary": {
                "total": total,
                "passed": passed,
                "pass_rate_pct": round(100 * passed / total, 1),
                "first_try_pass_pct": round(100 * first_try_pass / total, 1),
                "tool_match_pct": round(100 * tool_matches / total, 1),
                "avg_attempts": round(avg_attempts, 2),
                "avg_latency_s": round(avg_latency, 2),
                "attempts_breakdown": attempts_breakdown
            },
            "results": results
        }, f_json, indent=2, ensure_ascii=False)
        
    print(f"\n💾 Detailed benchmark results saved to:\n   {output_json_path}")
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test Generator 🔄 Executor Loop Benchmark")
    parser.add_argument("--sample", type=int, default=None, help="Run a single dataset index sample (e.g., --sample 119)")
    parser.add_argument("--start", type=int, default=None, help="Start sample index in dataset (0-indexed)")
    parser.add_argument("--end", type=int, default=None, help="End sample index in dataset (0-indexed, inclusive)")
    parser.add_argument("--n", type=int, default=None, help="Number of random samples to test")
    parser.add_argument("--max-retries", type=int, default=backend_config.EXECUTOR_MAX_RETRIES, help="Max retries per sample")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print full Generator output arguments")
    args, _ = parser.parse_known_args()

    # Default behavior
    if args.sample is not None:
        run_benchmark(sample_index=args.sample, max_retries=args.max_retries, verbose=args.verbose)
    elif args.start is None and args.end is None and args.n is None:
        run_benchmark(start_index=0, end_index=4, max_retries=args.max_retries, verbose=args.verbose)
    else:
        run_benchmark(
            num_samples=args.n,
            start_index=args.start,
            end_index=args.end,
            max_retries=args.max_retries,
            verbose=args.verbose
        )
