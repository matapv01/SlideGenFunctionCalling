"""Decompose round-2 human judgements: where DAPO wins and loses, and why (see the pre-registration).

Usage: python scripts/decompose_round2.py ratings.json [--split exploration|confirmation|all] [--out file.md]

Splits follow experiments/2026-10-21-human-eval-round2-decomposition/PREREGISTRATION.md: exploration = ratings
updated before the cutoff, confirmation = A3 ratings and A2 ratings updated after it.
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "slidegen_data" / "annotation" / "round2" / "secret_mapping.json"
SCORED = ROOT / "slidegen_data" / "testset_v2" / "scored_5880"
ROWS = ROOT / "slidegen_data" / "testset_v2" / "eval_rows_r4.json"
CUTOFF = "2026-10-21T04:10:22"
STEMS = {"dapo": "dapo_final_t03", "base": "base_final_t03", "best4": "base_best4", "gemini": "gemini_final_t03"}
VISIBLE = {"low_contrast", "text_cutoff", "slide_boundary", "bbox_collision", "markup_leak", "tiny_text", "plate_spill",
           "panel_spill"}
CRITERIA = ["overall", "aesthetic", "layout", "coverage", "language", "faithful"]
VOTE = {"A": 1, "tie": 0, "B": -1}
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
# Capitalised runs of Vietnamese words (proper names), e.g. "Ngân hàng Nhà nước", "Hà Nội".
NAME = re.compile(r"(?:[A-ZĐÂĂÊÔƠƯÁÀẢÃẠ][\wÀ-ỹ]*)(?:\s+[A-ZĐÂĂÊÔƠƯÁÀẢÃẠ][\wÀ-ỹ]*)+")


def in_split(rating: dict, split: str) -> bool:
    after = str(rating["updated_at"]) >= CUTOFF
    if split == "exploration":
        return not after and rating["annotator_id"] in {"A1", "A2"}
    if split == "confirmation":
        return rating["annotator_id"] == "A3" or (rating["annotator_id"] == "A2" and after)
    return True


def words(record: dict) -> int:
    return len((record.get("visible_text") or "").split())


def bad(record: dict) -> bool:
    return (not record["valid"]) or bool(VISIBLE & set(record.get("dom_issues") or []))


def rate(values: list[float]) -> float:
    return sum((v + 1) / 2 for v in values) / len(values)


def bootstrap(units: dict[str, list[float]], statistic, rounds: int = 2000) -> tuple[float, float]:
    keys, rng, stats = list(units), random.Random(0), []
    for _ in range(rounds):
        sample = [units[rng.choice(keys)] for _ in keys]
        value = statistic(sample)
        if value is not None:
            stats.append(value)
    stats.sort()
    return stats[int(0.025 * len(stats))], stats[int(0.975 * len(stats)) - 1]


def win_line(label: str, pairs: list[dict], criterion: str) -> str:
    if not pairs:
        return f"| {label} | 0 | | | | n/a |"
    units = collections.defaultdict(list)
    for pair in pairs:
        units[pair["deck"]].append(pair["mean"][criterion])
    flat = [v for vs in units.values() for v in vs]
    low, high = bootstrap(units, lambda s: rate([v for vs in s for v in vs]))
    wins, ties = sum(v > 0 for v in flat), sum(v == 0 for v in flat)
    return f"| {label} | {len(flat)} | {wins} | {ties} | {len(flat) - wins - ties} | {rate(flat):.3f} [{low:.3f}, {high:.3f}] |"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ratings", type=Path)
    parser.add_argument("--split", default="all", choices=["exploration", "confirmation", "all"])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    mapping = json.loads(MAPPING.read_text())["pairs"]
    rows = {row["key"]: row for row in json.loads(ROWS.read_text(encoding="utf-8"))}
    scored = {name: {r["key"]: r for r in map(json.loads, (SCORED / f"{stem}.jsonl").read_text().splitlines()) if r}
              for name, stem in STEMS.items()}
    ratings = [r for r in json.loads(args.ratings.read_text())["ratings"]
               if r["pair_id"] in mapping and not mapping[r["pair_id"]]["attention_check_of"] and in_split(r, args.split)]

    votes = collections.defaultdict(lambda: collections.defaultdict(list))
    for rating in ratings:
        entry = mapping[rating["pair_id"]]
        answers = rating["answers"] if isinstance(rating["answers"], dict) else json.loads(rating["answers"])
        sign = 1 if entry["a"]["system"] == "dapo" else -1
        for criterion in CRITERIA:
            votes[rating["pair_id"]][criterion].append(sign * VOTE[answers[criterion]])
    pairs = []
    for pair_id, by_criterion in votes.items():
        entry = mapping[pair_id]
        other = entry["comparison"].split("_vs_")[1]
        dapo, rival = scored["dapo"][entry["key"]], scored[other][entry["key"]]
        pairs.append({"id": pair_id, "comparison": entry["comparison"], "key": entry["key"], "deck": entry["doc_id"],
                      "category": entry["category"], "dapo": dapo, "rival": rival,
                      "mean": {c: sum(v) / len(v) for c, v in by_criterion.items()},
                      "differ": dapo.get("visible_text") != rival.get("visible_text"),
                      "clean": not bad(dapo) and not bad(rival),
                      "ratio": words(dapo) / words(rival) if words(rival) else None})

    sign = lambda x: (x > 0) - (x < 0)  # noqa: E731
    lines = [f"# Round-2 decomposition ({args.split} split)", "",
             f"Ratings: {len(ratings)} from {sorted({r['annotator_id'] for r in ratings})}; pairs: {len(pairs)}.", ""]
    for comparison in ("dapo_vs_base", "dapo_vs_best4", "dapo_vs_gemini"):
        group = [p for p in pairs if p["comparison"] == comparison]
        if not group:
            continue
        differ = [p for p in group if p["differ"]]
        clean = [p for p in differ if p["clean"]]
        lines += [f"## {comparison} ({len(group)} pairs, {len(differ)} with different visible text)", ""]

        lines += ["### Win rate of DAPO by criterion: all pairs vs differing pairs vs differing and defect-free", "",
                  "| Criterion / subset | Pairs | Win | Tie | Loss | Win rate [95% CI] |", "|---|---|---|---|---|---|"]
        for criterion in CRITERIA:
            for label, subset in (("all", group), ("differing", differ), ("differing, both defect-free", clean)):
                lines.append(win_line(f"{criterion} · {label}", subset, criterion))
        lines.append("")

        lines += ["### Coverage and overall by length (DAPO visible words / rival visible words), differing pairs", "",
                  "| Length ratio | Pairs | Coverage win rate | Overall win rate | Aesthetic win rate |", "|---|---|---|---|---|"]
        bins = [(0, 0.7, "< 0.70"), (0.7, 0.85, "0.70–0.85"), (0.85, 1.0, "0.85–1.00"), (1.0, 99, "≥ 1.00")]
        for low, high, label in bins:
            subset = [p for p in differ if p["ratio"] is not None and low <= p["ratio"] < high]
            if subset:
                lines.append(f"| {label} | {len(subset)} | " + " | ".join(
                    f"{rate([p['mean'][c] for p in subset]):.3f}" for c in ("coverage", "overall", "aesthetic")) + " |")
        units = collections.defaultdict(list)
        for p in differ:
            if p["ratio"] is not None:
                units[p["deck"]].append((p["ratio"] < 0.85, p["mean"]["coverage"]))

        def gap(sample):
            short = [v for unit in sample for s, v in unit if s]
            long = [v for unit in sample for s, v in unit if not s]
            return rate(short) - rate(long) if short and long else None

        flat = [x for vs in units.values() for x in vs]
        if gap([flat]) is not None:
            low, high = bootstrap(units, gap)
            lines += ["", f"Coverage win rate, ratio < 0.85 minus ≥ 0.85: {gap([flat]):+.3f} [{low:+.3f}, {high:+.3f}]"]
        lines.append("")

        lines += ["### What decides the overall verdict (pair verdicts; rows = criterion, cols = overall)", "",
                  "| Criterion verdict | Overall DAPO wins | Overall tie | Overall DAPO loses |", "|---|---|---|---|"]
        for criterion in ("aesthetic", "coverage", "layout", "faithful"):
            table = collections.Counter((sign(p["mean"][criterion]), sign(p["mean"]["overall"])) for p in group)
            for verdict, label in ((1, "wins"), (-1, "loses")):
                lines.append(f"| {criterion}: DAPO {label} | {table[(verdict, 1)]} | {table[(verdict, 0)]} | {table[(verdict, -1)]} |")
        lines.append("")

        lines += ["### By slide type (differing pairs)", "",
                  "| Slide type | Pairs | Overall | Aesthetic | Coverage |", "|---|---|---|---|---|"]
        for category in sorted({p["category"] for p in differ}):
            subset = [p for p in differ if p["category"] == category]
            lines.append(f"| {category} | {len(subset)} | " + " | ".join(
                f"{rate([p['mean'][c] for p in subset]):.3f}" for c in ("overall", "aesthetic", "coverage")) + " |")
        lines.append("")

        lines += ["### What DAPO leaves out, by coverage verdict (differing pairs)", "",
                  "Source numbers / proper names that the rival shows and DAPO does not (mean per pair), and automatic "
                  "metric differences DAPO minus rival.", "",
                  "| Coverage verdict | Pairs | Words DAPO/rival | Numbers dropped | Names dropped | Δ keypoint | Δ numeric_fact | Δ ViT |",
                  "|---|---|---|---|---|---|---|---|"]
        for verdict, label in ((-1, "DAPO loses"), (0, "tie"), (1, "DAPO wins")):
            subset = [p for p in differ if sign(p["mean"]["coverage"]) == verdict]
            if not subset:
                continue
            numbers, names, deltas = [], [], collections.defaultdict(list)
            for p in subset:
                source = rows[p["key"]]["source_content"]
                mine, theirs = p["dapo"].get("visible_text") or "", p["rival"].get("visible_text") or ""
                numbers.append(len({n for n in NUMBER.findall(theirs) if n in source} - set(NUMBER.findall(mine))))
                names.append(len({n for n in NAME.findall(theirs) if n in source and n not in mine}))
                for metric in ("keypoint", "numeric_fact", "aesthetic"):
                    a, b = (p["dapo"].get("components") or {}).get(metric), (p["rival"].get("components") or {}).get(metric)
                    if a is not None and b is not None:
                        deltas[metric].append(a - b)
            ratios = sorted(p["ratio"] for p in subset if p["ratio"] is not None)
            mean = lambda xs: sum(xs) / len(xs) if xs else float("nan")  # noqa: E731
            lines.append(f"| {label} | {len(subset)} | {ratios[len(ratios) // 2]:.2f} | {mean(numbers):.2f} | {mean(names):.2f} | "
                         f"{mean(deltas['keypoint']):+.3f} | {mean(deltas['numeric_fact']):+.3f} | {mean(deltas['aesthetic']):+.3f} |")
        lines.append("")

        examples = {"coverage_loss": [p["key"] for p in differ if p["mean"]["coverage"] < 0],
                    "aesthetic_win_clean": [p["key"] for p in clean if p["mean"]["aesthetic"] > 0],
                    "overall_loss": [p["key"] for p in differ if p["mean"]["overall"] < 0]}
        lines += [f"Examples ({comparison}): " + json.dumps(examples), ""]

    text = "\n".join(lines) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
