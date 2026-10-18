"""Build the blind pairwise human-evaluation set from scored test-set outputs.

Systems (one slide per system per source slide):
  round 1 (testset, scored/):  dapo, base (sample 0), best8 (base, best of 8 by composite reward), gemini
  round 2 (testset_v2, scored_5880/, round-4 prompts, T=0.3): dapo_final_t03, base_final_t03, gemini_final_t03
          (sample 0) and base_best4 (base_final_t10, best of 4 by composite reward; rendered as outputs/base_best4)

Comparisons are stratified by slide category and image mode, then every pair's left/right
order and the global order are shuffled; ~5% of pairs reappear later with sides swapped as
attention checks. Pairs where a side produced no valid slide are not shown to people: they
are recorded as automatic decisions in the secret mapping.

Outputs:
  annotation_web/public/data/pairs.json        (public: source text + opaque image names)
  annotation_web/public/data/assignments.json  (public: per-annotator shuffled queues)
  slidegen_data/annotation[/round2]/secret_mapping.json (private: pair -> systems, scores)
  slidegen_data/annotation[/round2]/images/<opaque>.jpg (upload with --upload; round 2 goes to img2/)

Round 2 uses the same protocol and site; its pair ids carry an "r2-" prefix so both rounds share one table.

Usage: python scripts/build_annotation_set.py [--round 2] [--upload] [--annotators 3]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import secrets
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WEB_DATA = ROOT / "annotation_web" / "public" / "data"
HF_DATASET = "mata01/slidegen-human-eval-images"
KIND = {"INTRO_TOOLS": "Slide mở đầu", "TRANSITION_TOOLS": "Slide chuyển ý", "CONTENT_TOOLS": "Slide nội dung",
        "CHART_TOOLS": "Slide số liệu", "THANK_YOU_TOOLS": "Slide cảm ơn"}
# name -> scored file stem (best-of-N systems pick from it), per round; same comparison sizes in both rounds.
ROUNDS = {
    1: {"testset": "testset", "rows": "eval_rows.json", "scored": "scored", "out": "annotation", "prefix": "", "img": "img",
        "systems": {"dapo": "dapo", "base": "base", "gemini": "gemini", "best8": "base"}, "best_of": {"best8"},
        "comparisons": {("dapo", "base"): None, ("dapo", "gemini"): 180, ("dapo", "best8"): 150}},
    2: {"testset": "testset_v2", "rows": "eval_rows_r4.json", "scored": "scored_5880", "out": "annotation/round2",
        "prefix": "r2-", "img": "img2",
        "systems": {"dapo": "dapo_final_t03", "base": "base_final_t03", "gemini": "gemini_final_t03",
                    "best4": "base_best4"}, "best_of": set(),
        "comparisons": {("dapo", "base"): None, ("dapo", "gemini"): 180, ("dapo", "best4"): 150}},
}


def _load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _pick_systems(scored: dict[str, list[dict]], config: dict) -> dict[str, dict[str, dict]]:
    by_key = defaultdict(lambda: defaultdict(list))
    for stem, records in scored.items():
        for record in records:
            by_key[stem][record["key"]].append(record)
    picks = defaultdict(dict)
    for name, stem in config["systems"].items():
        for key, samples in by_key[stem].items():
            if name in config["best_of"]:
                picks[name][key] = max(samples, key=lambda r: (r["reward"], -r["sample"]))
            else:
                picks[name][key] = min(samples, key=lambda r: r["sample"])
    return picks


def _stratified(keys: list[str], rows: dict, count: int | None, rng: random.Random) -> list[str]:
    if count is None or count >= len(keys):
        return list(keys)
    strata = defaultdict(list)
    for key in keys:
        strata[(rows[key]["category"], rows[key]["image_mode"])].append(key)
    chosen = []
    for members in strata.values():
        rng.shuffle(members)
        chosen += members[: round(count * len(members) / len(keys))]
    rest = [key for key in keys if key not in set(chosen)]
    rng.shuffle(rest)
    return (chosen + rest)[:count]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=int, default=1, choices=sorted(ROUNDS))
    parser.add_argument("--annotators", type=int, default=3)
    parser.add_argument("--per-pair", type=int, default=2, help="annotators per pair")
    parser.add_argument("--triple-fraction", type=float, default=0.15, help="pairs rated by every annotator")
    parser.add_argument("--check-fraction", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=20261006)
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()
    config = ROUNDS[args.round]
    testset = ROOT / "slidegen_data" / config["testset"]
    out = ROOT / "slidegen_data" / config["out"]
    rng = random.Random(args.seed)
    salt = secrets.token_hex(16)

    rows = {row["key"]: row for row in json.loads((testset / config["rows"]).read_text(encoding="utf-8"))}
    planned = json.loads((testset / "wiki_testset_planned.json").read_text(encoding="utf-8"))
    category = {f"{r['doc_id']}_{int(r['slide_index']):02d}": r["category"] for r in planned}
    # Role of the source passage (what annotators see) vs. the planner's layout category (used for strata).
    extracted = json.loads((testset / "wiki_testset_rows.json").read_text(encoding="utf-8"))
    role = {f"{r['doc_id']}_{int(r['slide_index']):02d}": r["category"] for r in extracted}
    for key, row in rows.items():
        row["category"] = category.get(key, "CONTENT_TOOLS")
        row["role"] = role.get(key, row["category"])
    stems = set(config["systems"].values())
    scored = {path.stem: _load(path) for path in (testset / config["scored"]).glob("*.jsonl") if path.stem in stems}
    picks = _pick_systems(scored, config)

    image_dir = out / "images"
    shutil.rmtree(image_dir, ignore_errors=True)
    image_dir.mkdir(parents=True)

    def image_name(record: dict) -> str:
        name = hashlib.sha256(f"{salt}:{record['system']}:{record['key']}:{record['sample']}".encode()).hexdigest()[:20] + ".jpg"
        if not (image_dir / name).exists():
            # 4K renders are ~1.5 MB; 1920x1080 JPEG keeps text crisp at a fraction of the size.
            Image.open(ROOT / record["png"]).convert("RGB").resize((1920, 1080), Image.LANCZOS).save(
                image_dir / name, quality=90, optimize=True)
        return name

    def side(record: dict, system: str) -> dict:
        return {"system": system, "key": record["key"], "sample": record["sample"], "reward": record["reward"],
                "valid": record["valid"], "components": record["components"], "dom_issues": record["dom_issues"],
                "png": record["png"]}

    shown, automatic = [], []
    for (left, right), count in config["comparisons"].items():
        keys = sorted(key for key in picks[left] if key in picks[right])
        for key in _stratified(keys, rows, count, rng):
            first, second = picks[left][key], picks[right][key]
            entry = {"comparison": f"{left}_vs_{right}", "key": key, "doc_id": rows[key]["source_doc_id"],
                     "category": rows[key]["category"], "image_mode": rows[key]["image_mode"],
                     "sides": [side(first, left), side(second, right)]}
            if not (first["png"] and second["png"]):
                automatic.append(entry)
            else:
                shown.append(entry)

    rng.shuffle(shown)
    checks = rng.sample(range(len(shown)), round(len(shown) * args.check_fraction))
    pairs_public, mapping = [], {}
    for entry in shown:
        if rng.random() < 0.5:
            entry["sides"].reverse()
    items = [(entry, None) for entry in shown] + [(shown[i], i) for i in checks]
    order = list(range(len(items)))
    rng.shuffle(order)
    ids = {}
    for position, item_index in enumerate(order):
        ids[item_index] = f"{config['prefix']}p{position + 1:04d}"
    for item_index, (entry, check_of) in enumerate(items):
        a, b = entry["sides"] if check_of is None else entry["sides"][::-1]
        pair_id = ids[item_index]
        row = rows[entry["key"]]
        text = row["source_content"]
        title = (row.get("source_meta") or {}).get("title", "")
        pairs_public.append({"id": pair_id, "title": title, "kind": KIND.get(row["role"], ""), "text": text,
                             "a": image_name(a), "b": image_name(b)})
        mapping[pair_id] = {**{k: v for k, v in entry.items() if k != "sides"}, "a": a, "b": b,
                            "attention_check_of": ids[check_of] if check_of is not None else None}
    pairs_public.sort(key=lambda pair: pair["id"])

    # Each pair goes to `per_pair` annotators (balanced); a subset goes to everyone.
    names = [f"A{i + 1}" for i in range(args.annotators)]
    queues = {name: [] for name in names}
    base_ids = [ids[i] for i in range(len(shown))]
    triple = set(rng.sample(base_ids, round(len(base_ids) * args.triple_fraction)))
    for offset, pair_id in enumerate(base_ids):
        chosen = names if pair_id in triple else [names[(offset + j) % len(names)] for j in range(args.per_pair)]
        for name in chosen:
            queues[name].append(pair_id)
    for original_index, check_index in zip(checks, range(len(shown), len(items))):
        for name in names:
            if ids[original_index] in queues[name]:
                queues[name].append(ids[check_index])
    for name in names:
        rng.shuffle(queues[name])

    image_base = f"https://huggingface.co/datasets/{HF_DATASET}/resolve/main/{config['img']}/"
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    (WEB_DATA / "pairs.json").write_text(json.dumps({"round": args.round, "image_base": image_base, "pairs": pairs_public}, ensure_ascii=False))
    (WEB_DATA / "assignments.json").write_text(json.dumps(queues))
    out.mkdir(parents=True, exist_ok=True)
    (out / "secret_mapping.json").write_text(json.dumps(
        {"round": args.round, "seed": args.seed, "salt": salt, "pairs": mapping, "automatic": automatic}, ensure_ascii=False, indent=1))
    print(f"pairs shown {len(shown)} + checks {len(checks)}; automatic {len(automatic)}; "
          f"queues {[len(q) for q in queues.values()]}; images {len(list(image_dir.iterdir()))}")
    for name in sorted({entry['comparison'] for entry in shown}):
        print(f"  {name}: {sum(e['comparison'] == name for e in shown)} shown, "
              f"{sum(e['comparison'] == name for e in automatic)} automatic")

    if args.upload:
        import os

        from dotenv import load_dotenv
        from huggingface_hub import HfApi

        load_dotenv(ROOT / ".env")
        api = HfApi(token=os.environ["HF_TOKEN"])
        api.create_repo(HF_DATASET, repo_type="dataset", private=False, exist_ok=True)
        api.upload_folder(repo_id=HF_DATASET, repo_type="dataset", folder_path=str(image_dir), path_in_repo=config["img"],
                          delete_patterns=[f"{config['img']}/*"], commit_message="Blind slide images for human evaluation")
        print(f"uploaded to {image_base}")


if __name__ == "__main__":
    main()
