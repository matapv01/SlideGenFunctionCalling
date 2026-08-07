"""
Script pre-retrieve candidate tools cho từng sample trong merged_sft_dataset.json.

Sử dụng GeminiToolRetrieveProvider (RAG với FAISS) để lấy ra danh sách tên tool
dựa vào `action` (category) và `thought` (hoặc slide_content).

Lưu kết quả ra file mới: rl/data/dataset_with_candidate_tools.json
Mỗi entry sẽ có thêm key: "candidate_tools": ["generate_main_points_slide", ...]

HƯỚNG DẪN SỬ DỤNG (CHẠY THEO BATCH ĐỂ TRÁNH RATE LIMIT 40 RPM):
-------------------------------------------------------------------------
1. Chạy đợt 1 (50 mẫu đầu tiên từ index 0 đến 50):
    python scripts/pre_retrieve_candidate_tools.py --start 0 --end 50

2. Chạy đợt 2 (50 mẫu tiếp theo từ index 50 đến 100):
    python scripts/pre_retrieve_candidate_tools.py --start 50 --end 100

3. Chạy toàn bộ dữ liệu (tự động sleep 1.5s/mẫu):
    python scripts/pre_retrieve_candidate_tools.py

GHI CHÚ:
- Script tự động nạp file JSON đầu ra hiện có và cập nhật/nối đợt chạy mới vào.
- Nếu chạy đè một dải index cũ (ví dụ 40 -> 80), dữ liệu sẽ được cập nhật lại theo (doc_id, slide_index) mà KHÔNG bị trùng lặp.
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv
import time
# Path setup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from backend.infrastructure.rag.gemini_provider import GeminiToolRetrieveProvider
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend.config import TOOL_RETRIEVER_TOP_K


def pre_retrieve_tools(input_path: str, output_path: str, start: int = 0, end: int = None, top_k: int = TOOL_RETRIEVER_TOP_K) -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Lỗi: Chưa cấu hình GEMINI_API_KEY trong file .env!")
        return

    print(f"[1] Đọc dữ liệu từ: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        dataset: list[dict] = json.load(f)
    total_dataset = len(dataset)
    print(f"    → Tổng số mẫu trong dataset: {total_dataset}")

    # Xác định phạm vi start - end
    if end is None or end > total_dataset:
        end = total_dataset
    if start < 0:
        start = 0

    sliced_dataset = dataset[start:end]
    print(f"    → Sẽ xử lý từ chỉ số index {start} đến {end - 1} (Tổng: {len(sliced_dataset)} mẫu)")

    # Đọc file output hiện tại nếu đã có để cập nhật tiếp
    output_dict_by_id = {}
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                for item in existing_data:
                    key = (item.get("doc_id"), item.get("slide_index"))
                    output_dict_by_id[key] = item
            print(f"    → Đã nạp {len(existing_data)} mẫu hiện có từ: {output_path}")
        except Exception:
            output_dict_by_id = {}

    # Khởi tạo Tool Retriever với FAISS index
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

    print(f"[3] Bắt đầu Pre-retrieval candidate tools (có rate-limit sleep 1.5s)...")
    total_slice = len(sliced_dataset)

    for idx, sample in enumerate(sliced_dataset, start=1):
        global_idx = start + idx - 1
        tool_category = sample.get("action") or sample.get("category") or "CONTENT_TOOLS"
        creative_thought = sample.get("thought", "")
        slide_idx = sample.get("slide_index", 0)
        doc_id = sample.get("doc_id", 0)

        # Query cho retrieval
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
            print(f"\n⚠️ Lỗi ở sample idx {global_idx} (doc_{doc_id}_slide_{slide_idx}): {e}")
            tool_names = []

        # Fallback về danh sách theo category nếu retrieval rỗng
        if not tool_names:
            category_tools = TOOLS_DICT.get(tool_category, TOOLS_DICT.get("CONTENT_TOOLS", []))
            tool_names = [t.name for t in category_tools]

        new_sample = dict(sample)
        new_sample["candidate_tools"] = tool_names
        
        # Cập nhật vào dictionary theo (doc_id, slide_index)
        output_dict_by_id[(doc_id, slide_idx)] = new_sample

        print(f"    → [{idx:3d}/{total_slice:3d}] Index #{global_idx} (doc_{doc_id}_slide_{slide_idx}): {len(tool_names)} tools {tool_names[:3]}...", end="\r", flush=True)

        # Sleep nhẹ 1.5 giây để tránh dính Rate Limit 40 RPM của Gemini Embeddings
        time.sleep(1.5)

    print("\n✅ Hoàn thành batch này!")

    # Ghép lại danh sách kết quả (giữ đúng thứ tự dataset gốc)
    final_output_list = []
    for item in dataset:
        key = (item.get("doc_id"), item.get("slide_index"))
        if key in output_dict_by_id:
            final_output_list.append(output_dict_by_id[key])
        else:
            final_output_list.append(item)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output_list, f, indent=2, ensure_ascii=False)
        
    print(f"[4] Đã lưu tổng cộng {len(final_output_list)} mẫu vào: {output_path}")


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_input = os.path.join(root, "rl", "data", "merged_sft_dataset.json")
    default_output = os.path.join(root, "rl", "data", "dataset_with_candidate_tools.json")

    parser = argparse.ArgumentParser(description="Pre-retrieve candidate tools for SFT dataset.")
    parser.add_argument("--input", default=default_input, help="Path to input merged dataset JSON")
    parser.add_argument("--output", default=default_output, help="Path to output JSON with candidate_tools")
    parser.add_argument("--start", type=int, default=0, help="Start index (inclusive)")
    parser.add_argument("--end", type=int, default=None, help="End index (exclusive)")
    parser.add_argument("--top_k", type=int, default=TOOL_RETRIEVER_TOP_K, help="Top K tools to retrieve")

    args = parser.parse_args()
    pre_retrieve_tools(args.input, args.output, args.start, args.end, args.top_k)
