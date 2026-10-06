"""Automatic test-set table from scored outputs (composite DAPO reward and each component).

Usage: python scripts/testset_summary.py  -> slidegen_data/testset/summary.{md,json}
"""
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORED = ROOT / "slidegen_data" / "testset" / "scored"
COMPONENTS = ["lexical", "semantic", "numeric_fact", "language", "dom", "aesthetic", "image_loaded"]
ISSUES = ["text_height", "text_width", "bbox_collision", "slide_boundary", "markup_leak", "max_lines"]


def load(system):
    return [json.loads(line) for line in (SCORED / f"{system}.jsonl").read_text().splitlines() if line.strip()]


def deck_ci(records, value, rounds=2000):
    decks = defaultdict(list)
    for r in records:
        decks[r["key"].split("_")[0]].append(value(r))
    keys, rng, stats = list(decks), random.Random(0), []
    for _ in range(rounds):
        xs = [x for k in (rng.choice(keys) for _ in keys) for x in decks[k]]
        stats.append(sum(xs) / len(xs))
    stats.sort()
    return stats[int(.025 * rounds)], stats[int(.975 * rounds) - 1]


systems = {"base": [r for r in load("base") if r["sample"] == 0], "dapo": [r for r in load("dapo") if r["sample"] == 0],
           "gemini": [r for r in load("gemini") if r["sample"] == 0]}
by_key = defaultdict(list)
for r in load("base"):
    by_key[r["key"]].append(r)
systems["best8"] = [max(v, key=lambda r: (r["reward"], -r["sample"])) for v in by_key.values()]
# All samples (more stable estimate of each policy's average behaviour).
systems_all = {"base (all 8)": load("base"), "dapo (all 4)": load("dapo"), "gemini (all 4)": load("gemini")}

rows, out = [], {}
header = "| System | n | Reward [95% CI] | Valid | " + " | ".join(COMPONENTS) + " | " + " | ".join(ISSUES) + " |"
rows += [header, "|" + "---|" * (4 + len(COMPONENTS) + len(ISSUES))]
for name, recs in {**systems, **systems_all}.items():
    valid = [r for r in recs if r["valid"]]
    lo, hi = deck_ci(recs, lambda r: r["reward"])
    mean = sum(r["reward"] for r in recs) / len(recs)
    comp = {c: sum(r["components"][c] for r in valid) / len(valid) for c in COMPONENTS}
    issues = {i: sum(i in (r["dom_issues"] or []) for r in valid) / len(valid) for i in ISSUES}
    out[name] = {"n": len(recs), "reward": mean, "ci": [lo, hi], "valid": len(valid) / len(recs), **comp, **{f"issue_{k}": v for k, v in issues.items()}}
    rows.append(f"| {name} | {len(recs)} | {mean:.3f} [{lo:.3f}, {hi:.3f}] | {len(valid)/len(recs):.3f} | "
                + " | ".join(f"{comp[c]:.3f}" for c in COMPONENTS) + " | " + " | ".join(f"{issues[i]:.3f}" for i in ISSUES) + " |")
note = ("Sample 0 per slide unless noted; components and issue rates over valid slides; invalid = reward -2. "
        "This is the DAPO training objective itself, so DAPO is favoured by construction; human evaluation is the primary result.")
(SCORED.parent / "summary.md").write_text("\n".join(["# Automatic test-set scores", "", note, ""] + rows) + "\n")
(SCORED.parent / "summary.json").write_text(json.dumps(out, indent=1))
print("\n".join(rows))
