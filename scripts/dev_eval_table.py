"""Dev-set table for scored systems. Usage: python scripts/dev_eval_table.py <scored_dir> name=system[:bestN] ..."""
import collections
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISIBLE = {"low_contrast", "text_cutoff", "slide_boundary", "bbox_collision", "markup_leak", "tiny_text", "plate_spill", "panel_spill"}


def load(scored: str, system: str):
    path = ROOT / "slidegen_data" / "testset" / scored / f"{system}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def pick(records, best_of):
    by_key = collections.defaultdict(list)
    for record in records:
        by_key[record["key"]].append(record)
    if best_of:
        return [max(sorted(g, key=lambda r: r["sample"])[:best_of], key=lambda r: (r["reward"], -r["sample"])) for g in by_key.values()]
    return [min(g, key=lambda r: r["sample"]) for g in by_key.values()]


def ci(records, value, rounds=2000):
    decks = collections.defaultdict(list)
    for record in records:
        decks[record["key"].split("_")[0]].append(value(record))
    keys, rng, stats = list(decks), random.Random(0), []
    for _ in range(rounds):
        xs = [x for k in (rng.choice(keys) for _ in keys) for x in decks[k]]
        stats.append(sum(xs) / len(xs))
    stats.sort()
    return stats[int(.025 * rounds)], stats[int(.975 * rounds) - 1]


def row(name, records):
    valid = [r for r in records if r["valid"]]
    n = len(records)
    visible = sum(bool(VISIBLE & set(r["dom_issues"])) for r in valid)
    comp = lambda k: sum(r["components"][k] for r in valid) / len(valid)  # noqa: E731
    issue = lambda k: sum(k in r["dom_issues"] for r in valid) / n  # noqa: E731
    lo, hi = ci(records, lambda r: r["reward"])
    return {"system": name, "n": n, "reward": sum(r["reward"] for r in records) / n, "ci": [lo, hi], "valid": len(valid) / n,
            "usable": (len(valid) - visible) / n, "visible": visible / n, "cutoff": issue("text_cutoff"),
            "collision": issue("bbox_collision"), "low_contrast": issue("low_contrast"), "markup_leak": issue("markup_leak"),
            "lexical": comp("lexical"), "semantic": comp("semantic"), "numeric_fact": comp("numeric_fact"),
            "language": comp("language"), "aesthetic": comp("aesthetic")}


def main():
    rows = []
    for spec in sys.argv[1:]:
        name, _, rest = spec.partition("=")
        scored, _, system = rest.partition("/")
        system, _, best = system.partition(":")
        rows.append(row(name, pick(load(scored, system), int(best) if best else 0)))
    cols = ["reward", "valid", "usable", "visible", "cutoff", "collision", "lexical", "numeric_fact", "aesthetic"]
    print("| system | n | " + " | ".join(cols) + " |")
    print("|---|---|" + "---|" * len(cols))
    for r in rows:
        print(f"| {r['system']} | {r['n']} | {r['reward']:.3f} [{r['ci'][0]:.2f}, {r['ci'][1]:.2f}] | "
              + " | ".join(f"{r[c]:.3f}" for c in cols[1:]) + " |")
    print(json.dumps(rows))


if __name__ == "__main__":
    main()
