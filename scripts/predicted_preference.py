"""Predicted human preference of each system over a reference system on the same slides.

A logistic model of round-1 human verdicts (342 non-tie pairs, overall question) on reward-feature
differences (lexical, semantic, numeric_fact, language, aesthetic, any visible defect, text_height) scores
every slide pair; an invalid slide loses to a valid one. The interval is a bootstrap over decks.

Usage: python scripts/predicted_preference.py <scored_dir> <reference_system> <system> [<system> ...]
"""
import collections
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "slidegen_data"
VISIBLE = {"low_contrast", "text_cutoff", "slide_boundary", "bbox_collision", "markup_leak", "tiny_text",
           "plate_spill", "panel_spill"}


def _load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def features(record: dict) -> np.ndarray:
    c, issues = record["components"], set(record["dom_issues"])
    return np.array([c["lexical"], c["semantic"], c["numeric_fact"], c["language"], c["aesthetic"],
                     float(bool(VISIBLE & issues)), float("text_height" in issues)])


def fit() -> LogisticRegression:
    ratings = json.loads((DATA / "annotation/ratings.json").read_text())["ratings"]
    pairs = json.loads((DATA / "annotation/secret_mapping.json").read_text())["pairs"]
    rated = {(system, r["key"], r["sample"]): r for system in ("dapo", "base", "gemini")
             for r in _load(DATA / f"testset/scored_asrated/{system}.jsonl")}
    votes = collections.defaultdict(list)
    for rating in ratings:
        if not pairs[rating["pair_id"]]["attention_check_of"]:
            votes[rating["pair_id"]].append({"A": 1, "tie": 0, "B": -1}[rating["answers"]["overall"]])
    side = lambda s: ("base" if s["system"] == "best8" else s["system"], s["key"], s["sample"])
    x, y = [], []
    for pair_id, vote in votes.items():
        mean = sum(vote) / len(vote)
        if mean == 0:
            continue
        pair = pairs[pair_id]
        x.append(features(rated[side(pair["a"])]) - features(rated[side(pair["b"])]))
        y.append(int(mean > 0))
    x, y = np.array(x), np.array(y)
    return LogisticRegression(fit_intercept=False).fit(np.vstack([x, -x]), np.concatenate([y, 1 - y]))


def main() -> None:
    scored, reference, systems = sys.argv[1], sys.argv[2], sys.argv[3:]
    model = fit()
    first = lambda name: {r["key"]: r for r in sorted(_load(DATA / "testset" / scored / f"{name}.jsonl"),
                                                       key=lambda r: -r["sample"])}
    base = first(reference)
    for name in systems:
        other, by_deck = first(name), collections.defaultdict(list)
        for key, ref in base.items():
            mine = other.get(key)
            if mine is None:
                continue
            if mine["valid"] and ref["valid"]:
                p = model.predict_proba([features(mine) - features(ref)])[0, 1]
            else:
                p = 1.0 if mine["valid"] else 0.0 if ref["valid"] else 0.5
            by_deck[key.split("_")[0]].append(p)
        decks = list(by_deck)
        mean = float(np.mean([p for d in decks for p in by_deck[d]]))
        rng = np.random.default_rng(0)
        boot = [np.mean([p for d in rng.choice(decks, len(decks)) for p in by_deck[d]]) for _ in range(2000)]
        print(f"{name:20s} P(preferred over {reference}) = {mean:.3f} "
              f"[{np.percentile(boot, 2.5):.3f}, {np.percentile(boot, 97.5):.3f}]  n={sum(map(len, by_deck.values()))}")


if __name__ == "__main__":
    main()
