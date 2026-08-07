"""
Script pre-retrieve candidate tools cho từng sample trong merged_sft_dataset.json.

Sử dụng GeminiToolRetrieveProvider (RAG với FAISS) để lấy ra danh sách tên tool
dựa vào `action` (category) và `thought` (hoặc slide_content).

Lưu kết quả ra file mới: dataset_with_candidate_tools.json
Mỗi entry sẽ có thêm key: "candidate_tools": ["generate_main_points_slide", ...]
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv

# Path setup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from backend.infrastructure.rag.gemini_provider import GeminiToolRetrieveProvider
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend.config import TOOL_RETRIEVER_TOP_K


def pre_retrieve_tools(input_path: str, output_path: str, top_k: int = TOOL_RETRIEVER_TOP_K) -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Lỗi: Chưa cấu hình GEMINI_API_KEY trong file .env!")
        return

    print(f"[1] Đọc dữ liệu từ: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        dataset: list[dict] = json.load(f)
    print(f"    → {len(dataset)} samples")

    # Khởi tạo Tool Retriever với FAISS index (tái sử dụng index hiện có nếu có)
    faiss_index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "faiss_tool_retriever_index"))
    print(f"[2] Khởi tạo GeminiToolRetrieveProvider (FAISS index at: {faiss_index_path})...")
    
    try:
        tool_retriever = GeminiToolRetrieveProvider(
            tools_dict=TOOLS_DICT,
            index_path=faiss_index_path,
            api_key=api_key
        )
    except Exception as e:
        print(f"❌ Lỗi khởi tạo ToolRetriever: {e}")
        return

    print(f"[3] Bắt đầu Pre-retrieval candidate tools cho {len(dataset)} mẫu...")
    total = len(dataset)
    updated_dataset = []

    for idx, sample in enumerate(dataset, start=1):
        tool_category = sample.get("action") or sample.get("category") or "CONTENT_TOOLS"
        creative_thought = sample.get("thought", "")
        slide_idx = sample.get("slide_index", 0)

        # Nếu không có thought, fallback dùng slide_content[:300]
        query = creative_thought.strip() if creative_thought.strip() else sample.get("slide_content", "")[:300]

        try:
            retrieved_tools = tool_retriever.get_relevant_tools(
                category=tool_category,
                query=query,
                top_k=top_k,
                current_slide_index=slide_idx
            )
            tool_names = [t.name for t in retrieved_tools] if retrieved_tools else []
        except Exception as e:
            print(f"\n⚠️ Lỗi ở sample #{idx} (doc_{sample.get('doc_id')}_slide_{slide_idx}): {e}")
            tool_names = []

        # Fallback về danh sách theo category nếu retrieval rỗng
        if not tool_names:
            category_tools = TOOLS_DICT.get(tool_category, TOOLS_DICT.get("CONTENT_TOOLS", []))
            tool_names = [t.name for t in category_tools]

        new_sample = dict(sample)
        new_sample["candidate_tools"] = tool_names
        updated_dataset.append(new_sample)

        print(f"    → [{idx:3d}/{total:3d}] ({int(idx/total*100):2d}%) doc_{sample.get('doc_id')}_slide_{slide_idx} ({tool_category}): {len(tool_names)} tools {tool_names[:3]}...", end="\r", flush=True)

    print("\n✅ Hoàn thành retrieval!")
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(updated_dataset, f, indent=2, ensure_ascii=False)
        
    print(f"[4] Đã lưu dataset mới kèm 'candidate_tools' vào: {output_path}")


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_input = os.path.join(root, "rl", "data", "merged_sft_dataset.json")
    default_output = os.path.join(root, "rl", "data", "dataset_with_candidate_tools.json")

    parser = argparse.ArgumentParser(description="Pre-retrieve candidate tools for SFT dataset.")
    parser.add_argument("--input", default=default_input, help="Path to input merged dataset JSON")
    parser.add_argument("--output", default=default_output, help="Path to output JSON with candidate_tools")
    parser.add_argument("--top_k", type=int, default=TOOL_RETRIEVER_TOP_K, help="Top K tools to retrieve")

    args = parser.parse_args()
    pre_retrieve_tools(args.input, args.output, args.top_k)
