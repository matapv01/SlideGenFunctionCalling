#!/usr/bin/env python3
"""How well do automatic judges agree with the human pairwise verdicts? VLM judge vs ViT/metric deltas vs human-human.

Usage: python scripts/analyze_vlm_judge.py --round 2 --ratings slidegen_data/annotation/round2/ratings_interim.json \
           --vlm slidegen_data/annotation/vlm_judge/r2_qwen25vl32b.jsonl --out report.md

All votes are taken from the A side of the blind pair (+1 A better, 0 tie, -1 B better). Agreement on a criterion is
counted over pairs where the humans' mean vote is not a tie and the judge takes a side; "decisive" is the share of
those human-decided pairs where the judge takes a side at all.
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = {1: ROOT / "slidegen_data/annotation/secret_mapping.json",
           2: ROOT / "slidegen_data/annotation/round2/secret_mapping.json"}
# Scored records (visible text) per round and the scored file each system's slide comes from.
SCORED = {1: (ROOT / "slidegen_data/testset/scored_asrated", {"dapo": "dapo", "base": "base", "gemini": "gemini", "best8": "base"}),
          2: (ROOT / "slidegen_data/testset_v2/scored_5880", {"dapo": "dapo_final_t03", "base": "base_final_t03",
                                                             "gemini": "gemini_final_t03", "best4": "base_best4"})}
CRITERIA = ["faithful", "coverage", "language", "layout", "aesthetic", "overall"]
VOTE = {"A": 1, "tie": 0, "B": -1}
# Automatic baselines: the component whose A-minus-B difference stands in for each criterion.
METRIC_FOR = {"faithful": "numeric_fact", "coverage": "keypoint", "language": "language", "layout": "dom",
              "aesthetic": "aesthetic", "overall": "reward"}
sign = lambda x: (x > 0) - (x < 0)  # noqa: E731


def metric(side: dict, name: str) -> float | None:
    if name == "reward":
        return side.get("reward")
    return (side.get("components") or {}).get(name)


def agreement(pairs: list[tuple[float, float]]) -> tuple[int, int, int]:
    """(pairs humans decided, of those the judge decided, of those the same side)."""
    decided = [(h, j) for h, j in pairs if sign(h)]
    both = [(h, j) for h, j in decided if sign(j)]
    return len(decided), len(both), sum(sign(h) == sign(j) for h, j in both)


def cell(stats: tuple[int, int, int]) -> str:
    decided, both, same = stats
    if not both:
        return "n/a"
    return f"{same / both:.2f} ({same}/{both}; decides {both / decided:.0%})"


def win_rate_ci(units: dict[str, list[float]]) -> str:
    flat = [v for vs in units.values() for v in vs]
    rate = lambda xs: sum((v + 1) / 2 for v in xs) / len(xs)  # noqa: E731
    keys, rng, stats = list(units), random.Random(0), []
    for _ in range(2000):
        stats.append(rate([v for k in (rng.choice(keys) for _ in keys) for v in units[k]]))
    stats.sort()
    return f"{rate(flat):.3f} [{stats[50]:.3f}, {stats[1949]:.3f}]"


def luminance(path: Path) -> float:
    from PIL import Image
    image = Image.open(path).convert("L").resize((160, 90))
    return sum(image.getdata()) / (255 * 160 * 90)


def bias_section(round_: int, mapping: dict, ids: list[str], human: dict, vlm: dict) -> list[str]:
    """Do judges prefer the longer slide, or the brighter one? Same question for humans and the VLM."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from vlm_pairwise_judge import ROUNDS, load_pairs
    directory, stems = SCORED[round_]
    records = {}
    for stem in set(stems.values()):
        for line in (directory / f"{stem}.jsonl").read_text().splitlines():
            if line.strip():
                record = json.loads(line)
                records[(stem, record["key"], record["sample"])] = record
    images = ROOT / ROUNDS[round_]["images"]
    blind = {p["id"]: p for p in load_pairs(ROUNDS[round_]["pairs"])["pairs"]}
    words = lambda side: len((records[(stems[side["system"]], side["key"], side["sample"])].get("visible_text") or "").split())  # noqa: E731
    rows = []
    for i in ids:
        a, b = words(mapping[i]["a"]), words(mapping[i]["b"])
        if a and b:
            rows.append({"ratio": a / b, "lum": luminance(images / blind[i]["a"]) - luminance(images / blind[i]["b"]),
                         "human": {c: sum(human[i][c]) / len(human[i][c]) for c in CRITERIA},
                         "vlm": {c: (VOTE[vlm[i]["forward"][c]] + VOTE[vlm[i]["swapped"][c]]) / 2 for c in CRITERIA}})
    lines = ["## Length and brightness preferences (pairs where the judge takes a side)", "",
             "Longer = A has > 1.1x or < 0.9x B's visible words; brighter = |mean luminance A - B| > 0.03.", "",
             "| Criterion | Humans pick longer | VLM picks longer | Humans pick brighter | VLM picks brighter |",
             "|---|---|---|---|---|"]
    for c in CRITERIA:
        row = []
        for key, test in (("ratio", lambda r: abs(r["ratio"] - 1) > 0.1), ("lum", lambda r: abs(r["lum"]) > 0.03)):
            for who in ("human", "vlm"):
                chosen = [r for r in rows if test(r) and sign(r[who][c])]
                same = sum((r[key] > (1 if key == "ratio" else 0)) == (r[who][c] > 0) for r in chosen)
                row.append(f"{same / len(chosen):.2f} ({same}/{len(chosen)})" if chosen else "n/a")
        lines.append(f"| {c} | {row[0]} | {row[1]} | {row[2]} | {row[3]} |")
    return lines + [""]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=int, choices=[1, 2], required=True)
    parser.add_argument("--ratings", type=Path, required=True)
    parser.add_argument("--vlm", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    mapping = json.loads(MAPPING[args.round].read_text())["pairs"]
    vlm = {r["pair_id"]: r for r in map(json.loads, args.vlm.read_text().splitlines()) if r["forward"] and r["swapped"]}

    human = collections.defaultdict(lambda: collections.defaultdict(list))
    raters = collections.defaultdict(dict)
    for rating in json.loads(args.ratings.read_text())["ratings"]:
        entry = mapping.get(rating["pair_id"])
        if not entry or entry["attention_check_of"] or rating["pair_id"] == "r2-test":
            continue
        answers = rating["answers"] if isinstance(rating["answers"], dict) else json.loads(rating["answers"])
        raters[rating["pair_id"]][rating["annotator_id"]] = answers
        for c in CRITERIA:
            human[rating["pair_id"]][c].append(VOTE[answers[c]])

    ids = sorted(set(human) & set(vlm))
    lines = [f"# Automatic judges vs human verdicts, round {args.round}", "",
             f"Pairs with human ratings and a parsed VLM verdict: {len(ids)} (VLM file {len(vlm)}, human {len(human)}).",
             f"VLM: {next(iter(vlm.values()))['model']}, each pair judged in both orders; vote = mean of the two.", ""]

    # Position consistency of the VLM.
    same = {c: sum(vlm[i]["forward"][c] == vlm[i]["swapped"][c] for i in vlm) / len(vlm) for c in CRITERIA}
    first = {c: sum(VOTE[vlm[i]["forward"][c]] for i in vlm) / len(vlm) for c in CRITERIA}
    lines += ["## VLM self-consistency (same answer when A/B are swapped)", "",
              "| Criterion | Same verdict both orders | Mean forward vote (+ = prefers first image) |", "|---|---|---|"]
    lines += [f"| {c} | {same[c]:.2f} | {first[c]:+.2f} |" for c in CRITERIA] + [""]

    # Agreement table: VLM, metric deltas, human-human.
    lines += ["## Agreement with the human pair verdict (same side, on pairs both decided)", "",
              "| Criterion | VLM (both orders) | VLM forward only | Metric Δ (" + ", ".join(
                  f"{c}:{m}" for c, m in METRIC_FOR.items()) + ") | Human vs other human |", "|---|---|---|---|---|"]
    for c in CRITERIA:
        v = [(sum(human[i][c]) / len(human[i][c]),
              (VOTE[vlm[i]["forward"][c]] + VOTE[vlm[i]["swapped"][c]]) / 2) for i in ids]
        f = [(sum(human[i][c]) / len(human[i][c]), VOTE[vlm[i]["forward"][c]]) for i in ids]
        m = []
        for i in ids:
            a, b = metric(mapping[i]["a"], METRIC_FOR[c]), metric(mapping[i]["b"], METRIC_FOR[c])
            if a is not None and b is not None:
                m.append((sum(human[i][c]) / len(human[i][c]), round(a - b, 4)))
        hh = []
        for votes in raters.values():
            names = sorted(votes)
            for x in range(len(names)):
                for y in range(x + 1, len(names)):
                    hh.append((VOTE[votes[names[x]][c]], VOTE[votes[names[y]][c]]))
        lines.append(f"| {c} | {cell(agreement(v))} | {cell(agreement(f))} | {cell(agreement(m))} | {cell(agreement(hh))} |")
    lines.append("")

    # Agreement by comparison for the main criteria.
    lines += ["## VLM agreement by comparison", "", "| Comparison | " + " | ".join(CRITERIA) + " |",
              "|---|" + "---|" * len(CRITERIA)]
    for comparison in sorted({mapping[i]["comparison"] for i in ids}):
        sub = [i for i in ids if mapping[i]["comparison"] == comparison]
        row = []
        for c in CRITERIA:
            v = [(sum(human[i][c]) / len(human[i][c]), (VOTE[vlm[i]["forward"][c]] + VOTE[vlm[i]["swapped"][c]]) / 2)
                 for i in sub]
            row.append(cell(agreement(v)))
        lines.append(f"| {comparison} ({len(sub)}) | " + " | ".join(row) + " |")
    lines.append("")

    # DAPO win rates as seen by humans and by the VLM on all judged pairs (VLM covers pairs no human has rated yet).
    lines += ["## DAPO win rate: humans vs VLM (deck bootstrap 95% CI)", "",
              "| Comparison | Criterion | Humans (rated pairs) | VLM (same pairs) | VLM (all judged pairs) |", "|---|---|---|---|---|"]
    for comparison in sorted({mapping[i]["comparison"] for i in vlm}):
        for c in ("overall", "aesthetic", "coverage", "layout", "faithful"):
            units = {"h": collections.defaultdict(list), "v": collections.defaultdict(list), "all": collections.defaultdict(list)}
            for i, record in vlm.items():
                entry = mapping[i]
                if entry["comparison"] != comparison:
                    continue
                side = 1 if entry["a"]["system"] == "dapo" else -1
                vote = side * (VOTE[record["forward"][c]] + VOTE[record["swapped"][c]]) / 2
                units["all"][entry["doc_id"]].append(vote)
                if i in human:
                    units["v"][entry["doc_id"]].append(vote)
                    units["h"][entry["doc_id"]].append(side * sum(human[i][c]) / len(human[i][c]))
            if units["all"]:
                lines.append(f"| {comparison} | {c} | " + " | ".join(
                    win_rate_ci(units[k]) if units[k] else "n/a" for k in ("h", "v", "all")) + " |")
    lines.append("")

    lines += bias_section(args.round, mapping, ids, human, vlm)
    text = "\n".join(lines) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
