"""
Script gộp sft_function_call_dataset.json với step_0001_cache.json.

- sft_function_call_dataset.json : list of dicts, mỗi entry có doc_id + slide_index + tool_call...
- step_0001_cache.json           : {"plans": {"<doc_id>_<slide_index>": {"action":..., "thought":...}}}

Kết quả: mỗi entry trong sft dataset sẽ được bổ sung action + thought từ cache (nếu tìm thấy).
Lưu ra file merged_sft_dataset.json.

Dùng:
    python scripts/merge_sft_with_cache.py
    python scripts/merge_sft_with_cache.py --sft path/sft.json --cache path/cache.json --out path/out.json
"""

import argparse
import json
import os


def merge(sft_path: str, cache_path: str, out_path: str) -> None:
    print(f"[1] Đọc SFT dataset: {sft_path}")
    with open(sft_path, "r", encoding="utf-8") as f:
        sft_data: list = json.load(f)
    print(f"    → {len(sft_data)} entries")

    print(f"[2] Đọc Cache (plans): {cache_path}")
    with open(cache_path, "r", encoding="utf-8") as f:
        cache_raw: dict = json.load(f)
    plans: dict = cache_raw.get("plans", cache_raw)   # hỗ trợ cả 2 format
    print(f"    → {len(plans)} plan keys")

    matched = 0
    not_found = 0
    merged = []

    total = len(sft_data)
    for idx, entry in enumerate(sft_data, start=1):
        doc_id     = entry.get("doc_id")
        slide_idx  = entry.get("slide_index")
        cache_key  = f"{doc_id}_{slide_idx}"

        plan = plans.get(cache_key)

        new_entry = dict(entry)   # copy để không sửa gốc

        if plan:
            # Override / bổ sung action và thought từ cache
            new_entry["action"]  = plan.get("action",  new_entry.get("action",  ""))
            new_entry["thought"] = plan.get("thought", new_entry.get("thought", ""))
            matched += 1
        else:
            # Giữ nguyên action/thought cũ nếu có, không thêm gì
            not_found += 1

        merged.append(new_entry)
        
        if idx % 100 == 0 or idx == total:
            print(f"    → Đã xử lý {idx}/{total} mẫu (Matched: {matched})", end="\r")
    print()

    print(f"[3] Kết quả ghép:")
    print(f"    Matched  : {matched} entries")
    print(f"    No plan  : {not_found} entries (giữ nguyên fields gốc)")
    print(f"    Total    : {len(merged)} entries")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"[4] Đã lưu → {out_path}")


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_sft   = os.path.join(root, "rl", "data", "sft_function_call_dataset.json")
    default_cache = os.path.join(root, "rl", "data", "step_0001_cache.json")
    default_out   = os.path.join(root, "rl", "data", "merged_sft_dataset.json")

    parser = argparse.ArgumentParser(description="Merge SFT dataset with step cache plans.")
    parser.add_argument("--sft",   default=default_sft,   help="Path to sft_function_call_dataset.json")
    parser.add_argument("--cache", default=default_cache, help="Path to step_XXXX_cache.json")
    parser.add_argument("--out",   default=default_out,   help="Path to output merged JSON file")
    args = parser.parse_args()

    merge(args.sft, args.cache, args.out)
