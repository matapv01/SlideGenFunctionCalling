"""
Test script: CoT Generator + Executor Validator (Isolated Test)

Uses the SFT dataset as input and NVIDIA API (Qwen3) for generation.
Tests the generator → executor → retry loop WITHOUT the full LangGraph workflow.

Usage:
    python scripts/test_cot_generator.py                   # Test 5 random samples
    python scripts/test_cot_generator.py --n 20             # Test 20 samples
    python scripts/test_cot_generator.py --no-cot           # Compare without CoT
    python scripts/test_cot_generator.py --category INTRO_TOOLS  # Filter by category
"""

import os
import sys
import json
import time
import random
import argparse
import re
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv
import requests

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.helper import format_tool_for_qwen, parse_tool_call_json
from backend.workflows.slidegen_workflow.utils.prompts import (
    QWEN_GENERATOR_SYSTEM_PROMPT,
    QWEN_COT_GENERATOR_SYSTEM_PROMPT,
    QWEN_GENERATOR_HUMAN_TEMPLATE,
    MATH_EQUATION_RULES,
    XML_CONTENT_PROMPT,
)
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import validate_tool_call
from backend.config import EXECUTOR_MAX_RETRIES


# ─── NVIDIA API Client ────────────────────────────────────────────────

class NvidiaLLMClient:
    """OpenAI-compatible client for NVIDIA API (Qwen3 models)."""

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        timeout: int = 180,
    ):
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1")).rstrip("/")
        self.model = model or os.environ.get("OPENAI_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        if not self.api_key:
            raise RuntimeError("NVIDIA_API_KEY is not set in .env")

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """Send chat completion request and return the response content."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(f"API error: {resp.status_code} — {resp.text[:500]}") from exc

        result = resp.json()
        content = result["choices"][0]["message"].get("content")
        if not content:
            raise RuntimeError("API returned empty content.")
        return content


# ─── Helper Functions ──────────────────────────────────────────────────

def strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks from the response."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def extract_thinking(text: str) -> str:
    """Extract the <think>...</think> block content."""
    match = re.search(r"<think>(.*?)</think>", text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def get_tools_for_category(category: str) -> list:
    """Get the list of LangChain tools for a given category."""
    return TOOLS_DICT.get(category, TOOLS_DICT.get("CONTENT_TOOLS", []))


def build_tool_schemas(tools: list) -> list:
    """Convert LangChain tools to Qwen-compatible JSON schemas."""
    return [format_tool_for_qwen(t) for t in tools]


def build_tool_description_text(tool_schemas: list) -> str:
    """Build a structured section listing available layout tools and parameter constraints for the LLM."""
    lines = [
        "🛠️ AVAILABLE LAYOUT TOOLS (YOU MUST SELECT EXACTLY ONE TOOL FROM THIS LIST):",
        "Below are the allowed layout tools for this slide. You MUST pick the single best matching tool from this list and strictly supply all required parameters:"
    ]
    for schema in tool_schemas:
        func = schema.get("function", {})
        name = func.get("name", "?")
        desc = func.get("description", "")[:180]
        params = func.get("parameters", {})
        properties = params.get("properties", {})
        required = params.get("required", [])
        
        lines.append(f"\n• Tool Name: `{name}`")
        lines.append(f"  Description: {desc}")
        
        param_desc_list = []
        for prop_name, prop_spec in properties.items():
            prop_type = prop_spec.get("type", "any")
            is_req = " (REQUIRED)" if prop_name in required else ""
            
            if prop_type == "array":
                item_spec = prop_spec.get("items", {})
                if item_spec.get("type") == "object":
                    item_props = list(item_spec.get("properties", {}).keys())
                    param_desc_list.append(f"`{prop_name}`: List[dict with keys: {item_props}]{is_req}")
                else:
                    item_type = item_spec.get("type", "string")
                    param_desc_list.append(f"`{prop_name}`: List[{item_type}]{is_req}")
            else:
                param_desc_list.append(f"`{prop_name}`: {prop_type}{is_req}")
                
        if param_desc_list:
            lines.append(f"  Parameters: {', '.join(param_desc_list)}")
            
    return "\n".join(lines)


# ─── Core Test Logic ───────────────────────────────────────────────────

def run_single_test(
    client: NvidiaLLMClient,
    sample: Dict[str, Any],
    use_cot: bool = True,
    max_retries: int = EXECUTOR_MAX_RETRIES,
) -> Dict[str, Any]:
    """
    Run a single generator → executor → retry test on one dataset sample.
    
    Returns a result dict with metrics.
    """
    category = sample["category"]
    slide_content = sample["slide_content"]
    style_context = sample.get("style_context", "")
    design_instruction = sample.get("design_instruction", "")
    ground_truth = sample.get("tool_call", {})
    
    # Get tools for this category
    tools = get_tools_for_category(category)
    tool_schemas = build_tool_schemas(tools)
    available_tool_names = [t.name for t in tools]
    tool_desc_text = build_tool_description_text(tool_schemas)
    
    # Select system prompt
    slide_type_prompt = XML_CONTENT_PROMPT
    generator_system_prompt = MATH_EQUATION_RULES + "\n\n" + slide_type_prompt
    
    system_prompt = generator_system_prompt + "\n\n" + (QWEN_COT_GENERATOR_SYSTEM_PROMPT if use_cot else QWEN_GENERATOR_SYSTEM_PROMPT)
    
    # Build user prompt
    user_prompt = QWEN_GENERATOR_HUMAN_TEMPLATE.format(
        style_context=style_context,
        design_instruction=design_instruction,
        slide_content=slide_content,
    )
    
    result = {
        "category": category,
        "slide_index": sample.get("slide_index", -1),
        "doc_id": sample.get("doc_id", -1),
        "ground_truth_tool": ground_truth.get("name", "?"),
        "use_cot": use_cot,
        "attempts": 0,
        "final_status": "fail",
        "predicted_tool": None,
        "tool_name_match": False,
        "executor_errors": [],
        "thinking_text": "",
        "latency_seconds": 0.0,
    }
    
    executor_feedback = ""
    
    for attempt in range(1, max_retries + 1):
        result["attempts"] = attempt
        start_time = time.time()
        
        # Build messages
        full_system = system_prompt + "\n\n" + tool_desc_text
        
        current_user_prompt = user_prompt
        if executor_feedback:
            current_user_prompt += f"\n\n[PREVIOUS ERROR — YOU MUST FIX THIS]\n{executor_feedback}"
        
        messages = [
            {"role": "system", "content": full_system},
            {"role": "user", "content": current_user_prompt},
        ]
        
        print(f"\n  📤 Attempt {attempt}/{max_retries} — calling {client.model}...")
        
        try:
            raw_response = client.generate(messages)
        except Exception as e:
            print(f"  ❌ API Error: {e}")
            result["executor_errors"].append(f"API_ERROR: {e}")
            continue
        
        elapsed = time.time() - start_time
        result["latency_seconds"] += elapsed
        
        # Extract thinking if CoT
        if use_cot:
            thinking = extract_thinking(raw_response)
            if thinking:
                result["thinking_text"] = thinking
                print(f"  💭 Thinking ({len(thinking)} chars): {thinking[:150]}...")
        
        # Strip thinking, parse tool call
        clean_response = strip_thinking(raw_response)
        tool_call = parse_tool_call_json(clean_response)
        
        if not tool_call:
            error_msg = "PARSE_FAILURE: Could not parse any tool call JSON from model output."
            print(f"  ❌ {error_msg}")
            print(f"     Raw (first 300 chars): {clean_response[:300]}")
            executor_feedback = error_msg + f"\n\nYour raw output was:\n{clean_response[:500]}\n\nYou MUST output a valid JSON inside <tool_call> tags."
            result["executor_errors"].append(error_msg)
            continue
        
        result["predicted_tool"] = tool_call.get("name")
        print(f"  🔧 Parsed tool: {tool_call.get('name')}")
        print(f"     Args keys: {list(tool_call.get('arguments', {}).keys())}")
        
        # Run executor validation
        is_valid, errors = validate_tool_call(tool_call, available_tool_names)
        
        if is_valid:
            print(f"  ✅ Executor PASSED! (attempt {attempt}, {elapsed:.1f}s)")
            result["final_status"] = "pass"
            result["tool_name_match"] = (tool_call.get("name") == ground_truth.get("name"))
            break
        else:
            error_report = "\n".join(f"    • {e}" for e in errors)
            print(f"  ❌ Executor FAILED ({len(errors)} errors):")
            print(error_report)
            result["executor_errors"].extend(errors)
            
            # Build feedback for retry
            executor_feedback = (
                f"EXECUTOR VALIDATION FAILED ({len(errors)} errors):\n"
                + "\n".join(f"- {e}" for e in errors)
                + "\n\nFix ALL errors above and regenerate the tool call."
            )
    else:
        # All retries exhausted
        print(f"  ⚠️ All {max_retries} attempts failed.")
        result["final_status"] = "fail_exhausted"
        if result["predicted_tool"]:
            result["tool_name_match"] = (result["predicted_tool"] == ground_truth.get("name"))
    
    return result


# ─── Main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Test CoT Generator + Executor Validator")
    parser.add_argument("--n", type=int, default=5, help="Number of samples to test (default: 5)")
    parser.add_argument("--no-cot", action="store_true", help="Disable CoT thinking (use original prompt)")
    parser.add_argument("--category", type=str, default=None, help="Filter by category (e.g., CONTENT_TOOLS)")
    parser.add_argument("--max-retries", type=int, default=EXECUTOR_MAX_RETRIES, help="Max retries per sample")
    parser.add_argument("--temperature", type=float, default=0.6, help="LLM temperature")
    parser.add_argument("--max-tokens", type=int, default=4096, help="Max tokens for generation")
    parser.add_argument("--model", type=str, default=None, help="Override model name")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "rl", "data", "sft_function_call_dataset.json")
    print(f"📂 Loading dataset from: {dataset_path}")
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    print(f"   Total samples: {len(dataset)}")
    
    # Filter by category if specified
    if args.category:
        dataset = [s for s in dataset if s.get("category") == args.category]
        print(f"   Filtered to category '{args.category}': {len(dataset)} samples")
    
    if not dataset:
        print("❌ No samples found!")
        return
    
    # Sample
    samples = random.sample(dataset, min(args.n, len(dataset)))
    
    # Init client
    client = NvidiaLLMClient(
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        model=args.model,
    )
    use_cot = not args.no_cot
    
    print(f"\n{'='*70}")
    print(f"  🧪 TEST CONFIG")
    print(f"  Model:       {client.model}")
    print(f"  CoT Enabled: {use_cot}")
    print(f"  Samples:     {len(samples)}")
    print(f"  Max Retries: {args.max_retries}")
    print(f"  Temperature: {args.temperature}")
    print(f"{'='*70}")
    
    # Run tests
    results = []
    for i, sample in enumerate(samples):
        print(f"\n{'─'*70}")
        print(f"  📝 SAMPLE {i+1}/{len(samples)} — doc={sample.get('doc_id')}, slide={sample.get('slide_index')}, cat={sample['category']}")
        print(f"  Ground Truth Tool: {sample.get('tool_call', {}).get('name', '?')}")
        print(f"  Content (first 100 chars): {sample['slide_content'][:100]}...")
        
        result = run_single_test(
            client=client,
            sample=sample,
            use_cot=use_cot,
            max_retries=args.max_retries,
        )
        results.append(result)
    
    # ─── Summary ───────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  📊 RESULTS SUMMARY")
    print(f"{'='*70}")
    
    total = len(results)
    passed = sum(1 for r in results if r["final_status"] == "pass")
    failed = sum(1 for r in results if r["final_status"] != "pass")
    tool_matches = sum(1 for r in results if r["tool_name_match"])
    avg_attempts = sum(r["attempts"] for r in results) / total if total else 0
    avg_latency = sum(r["latency_seconds"] for r in results) / total if total else 0
    
    first_try_pass = sum(1 for r in results if r["final_status"] == "pass" and r["attempts"] == 1)
    
    print(f"  Pass Rate:          {passed}/{total} ({100*passed/total:.1f}%)")
    print(f"  First-Try Pass:     {first_try_pass}/{total} ({100*first_try_pass/total:.1f}%)")
    print(f"  Tool Name Match:    {tool_matches}/{total} ({100*tool_matches/total:.1f}%)")
    print(f"  Avg Attempts:       {avg_attempts:.1f}")
    print(f"  Avg Total Latency:  {avg_latency:.1f}s")
    print(f"  CoT Enabled:        {use_cot}")
    
    # Error breakdown
    all_errors = []
    for r in results:
        all_errors.extend(r["executor_errors"])
    
    if all_errors:
        print(f"\n  📋 ERROR BREAKDOWN ({len(all_errors)} total errors):")
        error_types = {}
        for e in all_errors:
            etype = e.split(":")[0] if ":" in e else "OTHER"
            error_types[etype] = error_types.get(etype, 0) + 1
        for etype, count in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f"     {etype}: {count}")
    
    # Per-category breakdown
    categories = set(r["category"] for r in results)
    if len(categories) > 1:
        print(f"\n  📋 PER-CATEGORY BREAKDOWN:")
        for cat in sorted(categories):
            cat_results = [r for r in results if r["category"] == cat]
            cat_pass = sum(1 for r in cat_results if r["final_status"] == "pass")
            print(f"     {cat}: {cat_pass}/{len(cat_results)} pass")
    
    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), "result_test_CoT")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "test_cot_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  💾 Detailed results saved to: {output_path}")

    # Also save text summary format to result_test_CoT/result_summary.txt
    summary_txt_path = os.path.join(output_dir, "result_summary.txt")
    with open(summary_txt_path, "w", encoding="utf-8") as f_txt:
        f_txt.write("======================================================================\n")
        f_txt.write("  📊 RESULTS SUMMARY\n")
        f_txt.write("======================================================================\n")
        f_txt.write(f"  Pass Rate:          {passed}/{total} ({100*passed/total:.1f}%)\n")
        f_txt.write(f"  First-Try Pass:     {first_try_pass}/{total} ({100*first_try_pass/total:.1f}%)\n")
        f_txt.write(f"  Tool Name Match:    {tool_matches}/{total} ({100*tool_matches/total:.1f}%)\n")
        f_txt.write(f"  Avg Attempts:       {avg_attempts:.1f}\n")
        f_txt.write(f"  Avg Total Latency:  {avg_latency:.1f}s\n")
        f_txt.write(f"  CoT Enabled:        {use_cot}\n\n")
        if all_errors:
            f_txt.write(f"  📋 ERROR BREAKDOWN ({len(all_errors)} total errors):\n")
            for etype, count in sorted(error_types.items(), key=lambda x: -x[1]):
                f_txt.write(f"     {etype}: {count}\n")
            f_txt.write("\n")
        if len(categories) > 1:
            f_txt.write("  📋 PER-CATEGORY BREAKDOWN:\n")
            for cat in sorted(categories):
                cat_results = [r for r in results if r["category"] == cat]
                cat_pass = sum(1 for r in cat_results if r["final_status"] == "pass")
                f_txt.write(f"     {cat}: {cat_pass}/{len(cat_results)} pass\n")

    print(f"  💾 Summary text saved to: {summary_txt_path}")
    
    print(f"\n{'='*70}")
    print(f"  ✨ Done!")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
