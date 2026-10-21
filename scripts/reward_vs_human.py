#!/usr/bin/env python3
"""Where does DAPO's reward gain over the base model come from, and do the human annotators see it?

Recomputes the round-4 training reward from the scored components, splits the DAPO - rival gain by component, and
sets each pair's reward gap against the human verdict (round 2, all ratings in the export).

Usage: python scripts/reward_vs_human.py --ratings slidegen_data/annotation/round2/ratings_latest.json --out report.md
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "slidegen_data/annotation/round2/secret_mapping.json"
SCORED = ROOT / "slidegen_data/testset_v2/scored_5880"
STEMS = {"dapo": "dapo_final_t03", "base": "base_final_t03", "best4": "base_best4", "gemini": "gemini_final_t03"}
# experiments/2026-10-14-dapo-round4-keypoint-three-seeds/config.yaml; invalid completions get RL_INVALID_REWARD = -2.
WEIGHTS = {"keypoint": 1.5, "semantic": 0.4, "numeric_fact": 0.7, "dom": 2.1, "aesthetic": 1.5, "image_loaded": 0.25,
           "lexical": 0.0}
INVALID = -2.0
# Criterion a human would use to notice a change in this component.
CRITERION = {"keypoint": "coverage", "semantic": "coverage", "numeric_fact": "faithful", "dom": "layout",
             "aesthetic": "aesthetic", "image_loaded": "layout", "language": "language", "validity": "overall"}
CRITERIA = ["faithful", "coverage", "language", "layout", "aesthetic", "overall"]
VOTE = {"A": 1, "tie": 0, "B": -1}
VISIBLE = {"low_contrast", "text_cutoff", "slide_boundary", "bbox_collision", "markup_leak", "tiny_text", "plate_spill",
           "panel_spill"}
sign = lambda x: (x > 0) - (x < 0)  # noqa: E731


def train_reward(record: dict) -> float:
    if not record["valid"]:
        return INVALID
    c = record["components"]
    return sum(WEIGHTS[n] * c[n] for n in WEIGHTS) * c["language"]


def contributions(mine: dict, theirs: dict) -> dict[str, float]:
    """Split train_reward(mine) - train_reward(theirs) into additive parts that sum exactly to the gap."""
    if not (mine["valid"] and theirs["valid"]):
        return {"validity": train_reward(mine) - train_reward(theirs)}
    a, b = mine["components"], theirs["components"]
    parts = {n: WEIGHTS[n] * (a[n] - b[n]) * b["language"] for n in WEIGHTS if WEIGHTS[n]}
    parts["language"] = sum(WEIGHTS[n] * a[n] for n in WEIGHTS) * (a["language"] - b["language"])
    return parts


def rate(values: list[float]) -> str:
    return f"{sum((v + 1) / 2 for v in values) / len(values):.3f}" if values else "n/a"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ratings", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    scored = {name: {r["key"]: r for r in map(json.loads, (SCORED / f"{stem}.jsonl").read_text().splitlines()) if r}
              for name, stem in STEMS.items()}
    mapping = json.loads(MAPPING.read_text())["pairs"]
    human = collections.defaultdict(lambda: collections.defaultdict(list))
    for rating in json.loads(args.ratings.read_text())["ratings"]:
        entry = mapping.get(rating["pair_id"])
        if not entry or entry["attention_check_of"]:
            continue
        answers = rating["answers"] if isinstance(rating["answers"], dict) else json.loads(rating["answers"])
        side = 1 if entry["a"]["system"] == "dapo" else -1
        for c in CRITERIA:
            human[rating["pair_id"]][c].append(side * VOTE[answers[c]])

    lines = ["# DAPO's reward gain vs what the annotators saw (round 2)", "",
             "Training reward = round-4 weights " + json.dumps(WEIGHTS) + " x language; invalid = -2.", ""]
    for rival in ("base", "best4", "gemini"):
        keys = sorted(set(scored["dapo"]) & set(scored[rival]))
        totals, gaps = collections.Counter(), []
        for key in keys:
            parts = contributions(scored["dapo"][key], scored[rival][key])
            totals.update(parts)
            gaps.append(sum(parts.values()))
        n = len(keys)
        lines += [f"## DAPO vs {rival}", "",
                  f"Test set ({n} slides): mean training reward DAPO {sum(train_reward(scored['dapo'][k]) for k in keys) / n:.3f}, "
                  f"{rival} {sum(train_reward(scored[rival][k]) for k in keys) / n:.3f}, gap {sum(gaps) / n:+.3f}; "
                  f"DAPO higher on {sum(g > 0.01 for g in gaps)}, lower on {sum(g < -0.01 for g in gaps)}, "
                  f"within 0.01 on {sum(abs(g) <= 0.01 for g in gaps)}.", "",
                  "### Where the mean gap comes from (per-slide mean contribution, sums to the gap)", "",
                  "| Component | Contribution | Share of gap |", "|---|---|---|"]
        gap = sum(gaps) / n
        for name, value in sorted(totals.items(), key=lambda kv: -abs(kv[1])):
            lines.append(f"| {name} | {value / n:+.3f} | {value / n / gap:+.0%} |" if gap else f"| {name} | {value / n:+.3f} | |")
        lines.append("")

        rated = [(i, e) for i, e in mapping.items() if e["comparison"] == f"dapo_vs_{rival}" and i in human]
        pairs = []
        for i, entry in rated:
            parts = contributions(scored["dapo"][entry["key"]], scored[rival][entry["key"]])
            pairs.append({"gap": sum(parts.values()), "parts": parts,
                          "votes": {c: sum(v) / len(v) for c, v in human[i].items()}})
        lines += [f"### Reward gap vs human verdict ({len(pairs)} rated pairs)", "",
                  "| Reward gap DAPO - rival | Pairs | Human overall win rate | Human overall: DAPO wins / tie / loses | Sum of reward gap |",
                  "|---|---|---|---|---|"]
        bins = [(-99, -0.3, "< -0.3"), (-0.3, -0.05, "-0.3 .. -0.05"), (-0.05, 0.05, "-0.05 .. 0.05"),
                (0.05, 0.3, "0.05 .. 0.3"), (0.3, 99, ">= 0.3")]
        for low, high, label in bins:
            sub = [p for p in pairs if low <= p["gap"] < high]
            if sub:
                v = [p["votes"]["overall"] for p in sub]
                lines.append(f"| {label} | {len(sub)} | {rate(v)} | {sum(x > 0 for x in v)} / {sum(x == 0 for x in v)} / "
                             f"{sum(x < 0 for x in v)} | {sum(p['gap'] for p in sub):+.2f} |")
        seen = sum(p["gap"] for p in pairs if sign(p["votes"]["overall"]) == sign(p["gap"]) != 0)
        unseen = sum(p["gap"] for p in pairs if p["votes"]["overall"] == 0)
        against = sum(p["gap"] for p in pairs if sign(p["votes"]["overall"]) == -sign(p["gap"]) != 0)
        lines += ["", f"Sum of reward gap on rated pairs {sum(p['gap'] for p in pairs):+.2f}: on pairs where humans agree with "
                  f"the reward's direction {seen:+.2f}, where humans call it a tie {unseen:+.2f}, where humans disagree {against:+.2f}.", ""]

        lines += ["### Per component: when it favours one side by > 0.05, does the matching human criterion follow?", "",
                  "| Component (criterion) | Favours DAPO: pairs, human win rate on criterion, ties | Favours rival: pairs, win rate, ties |",
                  "|---|---|---|"]
        for name in ("validity", "dom", "aesthetic", "keypoint", "semantic", "numeric_fact", "language", "image_loaded"):
            criterion = CRITERION[name]
            row = []
            for direction in (1, -1):
                sub = [p["votes"][criterion] for p in pairs if direction * p["parts"].get(name, 0) > 0.05]
                row.append(f"{len(sub)}, {rate(sub)}, ties {sum(v == 0 for v in sub)}" if sub else "0")
            lines.append(f"| {name} ({criterion}) | {row[0]} | {row[1]} |")
        lines.append("")

        if rival == "base":
            # Visible defects: does removing one (metric) register with people (layout)?
            fixed = [p for (i, e), p in zip(rated, pairs)
                     if VISIBLE & set(scored[rival][e["key"]].get("dom_issues") or [])
                     and not VISIBLE & set(scored["dapo"][e["key"]].get("dom_issues") or [])]
            added = [p for (i, e), p in zip(rated, pairs)
                     if VISIBLE & set(scored["dapo"][e["key"]].get("dom_issues") or [])
                     and not VISIBLE & set(scored[rival][e["key"]].get("dom_issues") or [])]
            lines += [f"Visible defect only on the base slide: {len(fixed)} pairs, human layout win rate "
                      f"{rate([p['votes']['layout'] for p in fixed])}, overall {rate([p['votes']['overall'] for p in fixed])}; "
                      f"only on DAPO: {len(added)} pairs, layout {rate([p['votes']['layout'] for p in added])}, "
                      f"overall {rate([p['votes']['overall'] for p in added])}.", ""]

    text = "\n".join(lines) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
