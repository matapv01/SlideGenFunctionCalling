"""
========================================================================================
🚀 SCRIPT TEST NHANH HÀM process_doc TRONG rl/grpo/train.py
========================================================================================
Chạy lệnh:
    python scripts/test_process_doc.py
========================================================================================
"""

import os
import sys
import json
from dotenv import load_dotenv

# Setup import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from rl.grpo.rollout_processor import process_doc
from backend.infrastructure.llm_providers import NvidiaQwenLLMProvider, GeminiAPIProvider
from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT
from backend.infrastructure.rag.gemini_provider import GeminiToolRetrieveProvider

def main():
    print("=" * 80)
    print("🧪 TESTING process_doc FROM rl/rollout_processor.py")
    print("=" * 80)

    # 1. Đọc dataset_with_candidate_tools.json
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "rl", "data", "dataset_with_candidate_tools.json")
    if not os.path.exists(dataset_path):
        print(f"❌ Không tìm thấy dataset tại {dataset_path}")
        return

    with open(dataset_path, "r", encoding="utf-8") as f:
        all_slides = json.load(f)

    # Lấy toàn bộ slide của tài liệu (doc) đầu tiên trong dataset
    first_doc_id = all_slides[0].get("doc_id", 0)
    doc_slides = [s for s in all_slides if s.get("doc_id") == first_doc_id]
    print(f"📦 Loaded doc_id={first_doc_id} with {len(doc_slides)} slides.")

    # 2. Khởi tạo Provider phù hợp theo .env
    use_gemini = os.environ.get("USE_GEMINI", "false").lower() == "true"
    if use_gemini:
        print("🤖 Provider: GeminiAPIProvider")
        llm = GeminiAPIProvider(
            api_keys=os.environ.get("GEMINI_API_KEY"),
            base_url=os.environ.get("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
            model=os.environ.get("GEMINI_GENERATION_MODEL", "gemini-2.5-flash")
        )
    else:
        print("🤖 Provider: NvidiaQwenLLMProvider")
        model_name = os.environ.get("OPENAI_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
        api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
        llm = NvidiaQwenLLMProvider(model_name=model_name, base_url=base_url, api_key=api_key)

    # 3. Tạo grpo_config
    grpo_config = {
        "configurable": {
            "llm": llm,
            "planner_llm": llm,
            "tools_dict": TOOLS_DICT,
            "tool_retriever": None,
            "output_format": "xml",
        }
    }

    # 4. Chạy thẳng process_doc
    print(f"\n🚀 Running process_doc() on Doc #{first_doc_id}...")
    prompts_data = process_doc(
        doc_slides=doc_slides,
        step_num=1,
        doc_idx=0,
        grpo_config=grpo_config
    )

    print("\n" + "=" * 80)
    print("📊 RESULT SUMMARY")
    print("=" * 80)
    print(f"✅ Generated {len(prompts_data)} prompts successfully!")
    for idx, p in enumerate(prompts_data, 1):
        print(f"   Slide {idx}: Prompt length = {len(p.get('prompt', ''))} chars")

if __name__ == "__main__":
    main()
