"""Analyze blind pairwise human ratings against systems and the DAPO composite reward.

Usage: python scripts/analyze_annotations.py ratings.json slidegen_data/annotation/secret_mapping.json [--out report]

ratings.json is the /api/export response. Reports:
  - win rates per comparison and criterion, with deck-level bootstrap 95% CIs
    (human-only, and with invalid outputs counted as automatic losses)
  - severe-error flag rates per system
  - inter-annotator agreement (Krippendorff's alpha, ordinal) and attention-check consistency
  - agreement between humans and the composite reward / each mapped reward component
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

CRITERIA = ["faithful", "coverage", "language", "layout", "aesthetic", "overall"]
FLAGS = ["fabricated", "broken", "wrong_language"]
# Reward signal that is supposed to capture each human criterion.
REWARD_FOR = {
    "faithful": ["numeric_fact"],
    "coverage": ["semantic", "lexical"],
    "language": ["language"],
    "layout": ["dom"],
    "aesthetic": ["aesthetic"],
    "overall": ["composite"],
}
VALUE = {"A": 1, "tie": 0, "B": -1}


def _bootstrap(units: dict[str, list[float]], statistic, rounds: int = 2000, seed: int = 0):
    """95% CI resampling whole decks (units) to respect within-deck correlation."""
    keys = list(units)
    rng = random.Random(seed)
    values = []
    for _ in range(rounds):
        sample = [x for key in (rng.choice(keys) for _ in keys) for x in units[key]]
        if sample:
            values.append(statistic(sample))
    values.sort()
    return values[int(0.025 * len(values))], values[int(0.975 * len(values)) - 1]


def _alpha_ordinal(units: list[list[int]]) -> float | None:
    """Krippendorff's alpha (ordinal metric) for values in {-1, 0, 1}."""
    categories = [-1, 0, 1]
    coincidence = defaultdict(float)
    for values in units:
        m = len(values)
        if m < 2:
            continue
        for i, a in enumerate(values):
            for j, b in enumerate(values):
                if i != j:
                    coincidence[(a, b)] += 1 / (m - 1)
    totals = {c: sum(coincidence[(c, k)] for k in categories) for c in categories}
    n = sum(totals.values())
    if n <= 1:
        return None

    def delta(c, k):
        lo, hi = sorted((categories.index(c), categories.index(k)))
        inner = sum(totals[categories[g]] for g in range(lo, hi + 1))
        return (inner - (totals[c] + totals[k]) / 2) ** 2

    observed = sum(coincidence[(c, k)] * delta(c, k) for c in categories for k in categories)
    expected = sum(totals[c] * totals[k] * delta(c, k) for c in categories for k in categories) / (n - 1)
    return None if expected == 0 else 1 - observed / expected


def _reward_value(side: dict, name: str) -> float | None:
    if name == "composite":
        return side["reward"]
    return (side.get("components") or {}).get(name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ratings", type=Path)
    parser.add_argument("mapping", type=Path)
    parser.add_argument("--out", type=Path, default=Path("slidegen_data/annotation/report"))
    parser.add_argument("--eps", type=float, default=1e-3, help="reward differences below this count as ties")
    args = parser.parse_args()
    export = json.loads(args.ratings.read_text(encoding="utf-8"))
    secret = json.loads(args.mapping.read_text(encoding="utf-8"))
    pairs = secret["pairs"]
    ratings = [r for r in export["ratings"] if r["pair_id"] in pairs]
    for rating in ratings:
        if isinstance(rating["answers"], str):
            rating["answers"] = json.loads(rating["answers"])

    # Attention checks: the duplicate shows the same slides with sides swapped.
    checks = defaultdict(lambda: [0, 0])
    by_annotator_pair = {(r["annotator_id"], r["pair_id"]): r for r in ratings}
    for rating in ratings:
        original = pairs[rating["pair_id"]]["attention_check_of"]
        if original and (rating["annotator_id"], original) in by_annotator_pair:
            first = by_annotator_pair[(rating["annotator_id"], original)]["answers"]["overall"]
            second = rating["answers"]["overall"]
            checks[rating["annotator_id"]][0] += VALUE[first] == -VALUE[second]
            checks[rating["annotator_id"]][1] += 1
    ratings = [r for r in ratings if not pairs[r["pair_id"]]["attention_check_of"]]

    # Per pair and criterion: mean human score from the first-listed system's view (+1 = it wins).
    per_pair = defaultdict(lambda: defaultdict(list))
    flag_counts = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for rating in ratings:
        entry = pairs[rating["pair_id"]]
        first_system = entry["comparison"].split("_vs_")[0]
        sign = 1 if entry["a"]["system"] == first_system else -1
        for criterion in CRITERIA:
            per_pair[rating["pair_id"]][criterion].append(sign * VALUE[rating["answers"][criterion]])
        for side_name in ("A", "B"):
            system = entry[side_name.lower()]["system"]
            for flag in FLAGS:
                counts = flag_counts[system][flag]
                counts[0] += bool(rating["answers"]["flags"][side_name].get(flag))
                counts[1] += 1

    lines = ["# Human evaluation report", ""]
    attention = {name: f"{ok}/{n}" for name, (ok, n) in sorted(checks.items())}
    lines += [f"Ratings: {len(ratings)} (+ attention checks), annotators: {sorted({r['annotator_id'] for r in ratings})}",
              f"Attention-check consistency (overall, mirrored): {attention}", ""]
    results = {"win_rates": {}, "flags": {}, "alpha": {}, "reward_agreement": {}}

    comparisons = sorted({entry["comparison"] for entry in pairs.values()})
    automatic = defaultdict(list)
    for entry in secret.get("automatic", []):
        first, second = entry["sides"]
        if first["valid"] != second["valid"]:
            automatic[entry["comparison"]].append((entry["doc_id"], 1.0 if first["valid"] else -1.0))
    for comparison in comparisons:
        first, second = comparison.split("_vs_")
        lines += [f"## {first} vs {second}", "",
                  "| Criterion | Pairs | Win | Tie | Loss | Win rate (ties = 1/2) [95% CI] | incl. invalid as loss |",
                  "|---|---|---|---|---|---|---|"]
        for criterion in CRITERIA:
            units = defaultdict(list)
            for pair_id, scores in per_pair.items():
                if pairs[pair_id]["comparison"] == comparison:
                    units[pairs[pair_id]["doc_id"]].append(sum(scores[criterion]) / len(scores[criterion]))
            flat = [x for values in units.values() for x in values]
            if not flat:
                continue
            rate = lambda xs: sum((x + 1) / 2 for x in xs) / len(xs)  # noqa: E731
            low, high = _bootstrap(units, rate)
            with_invalid = defaultdict(list, {k: list(v) for k, v in units.items()})
            for doc_id, value in automatic[comparison]:
                with_invalid[doc_id].append(value)
            all_values = [x for values in with_invalid.values() for x in values]
            wins, ties = sum(x > 0 for x in flat), sum(x == 0 for x in flat)
            lines.append(f"| {criterion} | {len(flat)} | {wins} | {ties} | {len(flat) - wins - ties} | "
                         f"{rate(flat):.3f} [{low:.3f}, {high:.3f}] | {rate(all_values):.3f} (n={len(all_values)}) |")
            results["win_rates"][f"{comparison}/{criterion}"] = {"rate": rate(flat), "ci": [low, high], "n": len(flat),
                                                                "rate_with_invalid": rate(all_values)}
        lines.append("")

    lines += ["## Severe-error flags (fraction of ratings)", "", "| System | " + " | ".join(FLAGS) + " |",
              "|---|" + "---|" * len(FLAGS)]
    for system, counts in sorted(flag_counts.items()):
        lines.append(f"| {system} | " + " | ".join(f"{c[0] / c[1]:.3f}" for c in (counts[f] for f in FLAGS)) + " |")
        results["flags"][system] = {flag: counts[flag][0] / counts[flag][1] for flag in FLAGS}
    lines.append("")

    lines += ["## Inter-annotator agreement (Krippendorff's alpha, ordinal)", ""]
    for criterion in CRITERIA:
        alpha = _alpha_ordinal([scores[criterion] for scores in per_pair.values()])
        results["alpha"][criterion] = alpha
        lines.append(f"- {criterion}: {alpha:.3f}" if alpha is not None else f"- {criterion}: n/a")
    lines.append("")

    # Reward vs human: does the reward prefer the slide humans preferred?
    lines += ["## Reward vs human agreement", "",
              "Pairs where the human majority is not a tie and the reward difference exceeds eps.", "",
              "| Criterion | Reward signal | Pairs | Agreement [95% CI] |", "|---|---|---|---|"]
    for criterion, signals in REWARD_FOR.items():
        for signal in signals:
            units = defaultdict(list)
            for pair_id, scores in per_pair.items():
                human = sum(scores[criterion]) / len(scores[criterion])
                if human == 0:
                    continue
                a, b = _reward_value(pairs[pair_id]["a"], signal), _reward_value(pairs[pair_id]["b"], signal)
                if a is None or b is None or abs(a - b) < args.eps:
                    continue
                # Express the reward preference from the first-listed system's view, like the human score.
                entry = pairs[pair_id]
                first_is_a = entry["a"]["system"] == entry["comparison"].split("_vs_")[0]
                reward_pref = (a - b) if first_is_a else (b - a)
                units[entry["doc_id"]].append(float((reward_pref > 0) == (human > 0)))
            flat = [x for values in units.values() for x in values]
            if not flat:
                continue
            mean = lambda xs: sum(xs) / len(xs)  # noqa: E731
            low, high = _bootstrap(units, mean)
            results["reward_agreement"][f"{criterion}/{signal}"] = {"agreement": mean(flat), "ci": [low, high], "n": len(flat)}
            lines.append(f"| {criterion} | {signal} | {len(flat)} | {mean(flat):.3f} [{low:.3f}, {high:.3f}] |")

    durations = sorted(r["duration_ms"] / 1000 for r in ratings if r.get("duration_ms"))
    if durations:
        lines += ["", f"Median seconds per pair: {durations[len(durations) // 2]:.0f}"]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (args.out / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
