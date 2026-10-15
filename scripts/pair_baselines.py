"""Baselines on the held-out good/bad slide pairs (slidegen_data/pairs/val_data.csv, 193 pairs).

Each judge picks the better-designed slide of a pair; accuracy = share of pairs where it picks the good one.
  clip  - CLIP zero-shot: cosine to "a well-designed presentation slide" minus "a badly designed ..." prompt
  vlm   - Qwen3.5-35B-A3B (the policy's own base, a VLM) shown both slides, asked which is better designed;
          run in both orders, a pair counts as correct only by the average of the two orders (position bias removed)
Results go to slidegen_data/pairs/baselines.json, per defect type.

Usage: HF_HOME=/data/hf_cache /data/venvs/qwen35/bin/python scripts/pair_baselines.py [clip|vlm ...]
"""
import collections
import csv
import json
import re
import sys
from pathlib import Path

import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ROOT / "slidegen_data" / "pairs"
KAGGLE = "/kaggle/input/datasets/trungnguyen2710t/slidegen/anh_slide"
DEFECTS = ("cac_khoi_de_nhau", "size_chu", "mau_nen_xau", "mau_chu_xau", "tran_chu")


def load_pairs() -> list[dict]:
    rows = list(csv.DictReader(open(PAIRS / "val_data.csv")))
    local = lambda p: str(ROOT / "slidegen_data" / "anh_slide" / p.removeprefix(KAGGLE + "/"))  # noqa: E731
    return [{"good": local(r["good_path"]), "bad": local(r["bad_path"]),
             "defects": [d for d in DEFECTS if d in r["bad_path"].split("/")[-2]]} for r in rows]


def clip_scores(pairs: list[dict]) -> list[float]:
    from transformers import CLIPModel, CLIPProcessor

    name = "openai/clip-vit-base-patch32"
    model, processor = CLIPModel.from_pretrained(name).cuda().eval(), CLIPProcessor.from_pretrained(name)
    texts = ["a beautiful, well-designed, readable presentation slide",
             "an ugly, badly designed presentation slide with overlapping or unreadable text"]
    out = []
    tensor = lambda x: x if torch.is_tensor(x) else x.pooler_output  # noqa: E731  (transformers 5 returns an output object)
    with torch.no_grad():
        text = tensor(model.get_text_features(**processor(text=texts, return_tensors="pt", padding=True).to("cuda")))
        text = text / text.norm(dim=-1, keepdim=True)
        for pair in pairs:
            images = [Image.open(pair[k]).convert("RGB") for k in ("good", "bad")]
            feats = tensor(model.get_image_features(**processor(images=images, return_tensors="pt").to("cuda")))
            feats = feats / feats.norm(dim=-1, keepdim=True)
            score = (feats @ text.T)[:, 0] - (feats @ text.T)[:, 1]
            out.append(1.0 if score[0] > score[1] else 0.5 if score[0] == score[1] else 0.0)
    return out


PROMPT = ("Two versions of the same presentation slide are shown: Slide A first, then Slide B. Which one is better "
          "designed: readable text, good colour contrast, no overlapping or overflowing elements, appropriate font "
          "sizes? Answer with a single letter, A or B.")


def vlm_scores(pairs: list[dict]) -> list[float]:
    from transformers import AutoModelForImageTextToText, AutoProcessor

    name, revision = "Qwen/Qwen3.5-35B-A3B", "59d61f3ce65a6d9863b86d2e96597125219dc754"
    processor = AutoProcessor.from_pretrained(name, revision=revision)
    model = AutoModelForImageTextToText.from_pretrained(name, revision=revision, dtype=torch.bfloat16,
                                                        device_map="cuda").eval()
    letters = [processor.tokenizer.encode(x, add_special_tokens=False)[0] for x in ("A", "B")]

    processor.tokenizer.padding_side = "left"
    messages = [{"role": "user", "content": [
        {"type": "text", "text": "Slide A:"}, {"type": "image"}, {"type": "text", "text": "Slide B:"},
        {"type": "image"}, {"type": "text", "text": PROMPT}]}]
    text = processor.apply_chat_template(messages, add_generation_prompt=True, enable_thinking=False)

    def prefer_first(orders: list[tuple[str, str]]) -> list[float]:
        images = [Image.open(p).convert("RGB").resize((960, 540)) for order in orders for p in order]
        inputs = processor(text=[text] * len(orders), images=images, return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            logits = model(**inputs, logits_to_keep=1).logits[:, -1]
        return logits[:, letters].float().softmax(-1)[:, 0].tolist()

    out, batch = [], 4
    for start in range(0, len(pairs), batch):
        chunk = pairs[start:start + batch]
        probs = prefer_first([(p["good"], p["bad"]) for p in chunk] + [(p["bad"], p["good"]) for p in chunk])
        for i in range(len(chunk)):
            p = 0.5 * (probs[i] + 1 - probs[len(chunk) + i])
            out.append(1.0 if p > 0.5 else 0.5 if p == 0.5 else 0.0)
        print(f"vlm {len(out)}/{len(pairs)} running acc {sum(out) / len(out):.3f}", flush=True)
    return out


def human_pairs(criterion: str) -> list[dict]:
    """Round-1 human-rated pairs of model-generated slides with a non-tie majority on `criterion`."""
    ann = ROOT / "slidegen_data" / "annotation"
    images = {p["id"]: p for p in json.loads((ROOT / "annotation_web/public/data/pairs.json").read_text())["pairs"]}
    mapping = json.loads((ann / "secret_mapping.json").read_text())["pairs"]
    votes = collections.defaultdict(list)
    for rating in json.loads((ann / "ratings.json").read_text())["ratings"]:
        if not mapping[rating["pair_id"]]["attention_check_of"]:
            votes[rating["pair_id"]].append({"A": 1, "tie": 0, "B": -1}[rating["answers"][criterion]])
    out = []
    for pid, vote in votes.items():
        mean = sum(vote) / len(vote)
        entry = mapping[pid]
        if mean == 0 or not (entry["a"].get("valid") and entry["b"].get("valid")):
            continue
        a, b = (ann / "images" / images[pid]["a"]), (ann / "images" / images[pid]["b"])
        good, bad = (a, b) if mean > 0 else (b, a)
        side = (entry["a"], entry["b"]) if mean > 0 else (entry["b"], entry["a"])
        out.append({"good": str(good), "bad": str(bad), "defects": [],
                    "vit": float(side[0]["components"]["aesthetic"] > side[1]["components"]["aesthetic"]),
                    "reward": float(side[0]["reward"] > side[1]["reward"])})
    return out


def main() -> None:
    pairs = load_pairs()
    path = PAIRS / "baselines.json"
    results = json.loads(path.read_text()) if path.exists() else {}
    for judge in [j for j in sys.argv[1:] if j.startswith("human_")]:
        criterion = judge.removeprefix("human_")
        pairs_h = human_pairs(criterion)
        vlm = vlm_scores(pairs_h)
        results[judge] = {"n": len(pairs_h), "vlm": sum(vlm) / len(vlm),
                          "vit": sum(p["vit"] for p in pairs_h) / len(pairs_h),
                          "reward": sum(p["reward"] for p in pairs_h) / len(pairs_h)}
        print(judge, json.dumps(results[judge]), flush=True)
        path.write_text(json.dumps(results, indent=1, ensure_ascii=False))
    for judge in [j for j in sys.argv[1:] if not j.startswith("human_")] or ([] if sys.argv[1:] else ["clip", "vlm"]):
        correct = {"clip": clip_scores, "vlm": vlm_scores}[judge](pairs)
        per = collections.defaultdict(list)
        for pair, c in zip(pairs, correct):
            for d in pair["defects"]:
                per[d].append(c)
        results[judge] = {"n": len(pairs), "accuracy": sum(correct) / len(correct),
                          "by_defect": {d: {"n": len(v), "accuracy": sum(v) / len(v)} for d, v in per.items()}}
        print(judge, json.dumps(results[judge], ensure_ascii=False), flush=True)
        path.write_text(json.dumps(results, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
