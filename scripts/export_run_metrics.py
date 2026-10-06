"""Export a GRPO/DAPO run's metrics as CSV/JSON tables plus training-curve plots.

Usage: python scripts/export_run_metrics.py <run_dir> <out_dir>
Reads the newest checkpoint's trainer_state.json and the early-stopping state.
"""

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HEADLINE = {
    "reward": "eval_reward",
    "valid": "eval_reward/valid_fraction",
    "dom": "eval_reward_component/dom",
    "numeric_fact": "eval_reward_component/numeric_fact",
    "fabricated_number": "eval_reward_content/unsupported_number_fraction",
    "semantic": "eval_reward_component/semantic",
    "lexical": "eval_reward_component/lexical",
    "language": "eval_reward_component/language",
    "aesthetic": "eval_reward_component/aesthetic",
    "image_loaded": "eval_reward_component/image_loaded",
    "overflow": "eval_reward_dom/text_height_fraction",
    "markup_leak": "eval_reward_dom/markup_leak_fraction",
}


def _write_csv(path: Path, rows: list[dict]) -> None:
    keys = sorted({key for row in rows for key in row}, key=lambda k: (k != "step", k))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def _rolling(values: list[float], window: int = 10) -> list[float]:
    return [sum(values[max(0, i - window + 1): i + 1]) / len(values[max(0, i - window + 1): i + 1]) for i in range(len(values))]


def main() -> None:
    run, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    checkpoint = max(run.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[1]))
    history = json.loads((checkpoint / "trainer_state.json").read_text())["log_history"]
    evals = [row for row in history if "eval_reward" in row]
    train = [row for row in history if "reward" in row and "eval_reward" not in row]
    _write_csv(out / "eval_metrics.csv", evals)
    _write_csv(out / "train_metrics.csv", train)

    stopping = json.loads((run / "early_stopping_state.json").read_text())
    best = max(evals, key=lambda row: row["eval_reward"])
    pick = lambda row: {name: round(row[key], 4) for name, key in HEADLINE.items() if key in row}  # noqa: E731
    summary = {
        "run": run.name,
        "base_step0": pick(evals[0]),
        "best": {"step": best["step"], **pick(best)},
        "last": {"step": evals[-1]["step"], **pick(evals[-1])},
        "early_stopping": stopping,
        "eval_history": [{"step": row["step"], **pick(row)} for row in evals],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))

    panels = [("reward", "Composite reward"), ("valid", "Valid tool call"), ("dom", "DOM layout"),
              ("overflow", "Text overflow rate"), ("fabricated_number", "Fabricated-number rate"),
              ("aesthetic", "ViT aesthetic"), ("semantic", "Semantic"), ("language", "Language")]
    fig, axes = plt.subplots(2, 4, figsize=(18, 7.5))
    steps = [row["step"] for row in evals]
    for ax, (name, title) in zip(axes.flat, panels):
        key = HEADLINE[name]
        ax.plot(steps, [row[key] for row in evals], "o-", label="eval")
        train_key = key.removeprefix("eval_")
        if any(train_key in row for row in train):
            points = [(row["step"], row[train_key]) for row in train if train_key in row]
            ax.plot([s for s, _ in points], _rolling([v for _, v in points]), alpha=.6, label="train (rolling 10)")
        ax.axvline(best["step"], color="grey", ls="--", lw=1)
        ax.set_title(title)
        ax.set_xlabel("step")
        ax.legend(fontsize=8)
    fig.suptitle(f"{run.name} (dashed line: best eval step {best['step']})")
    fig.tight_layout()
    fig.savefig(out / "curves.png", dpi=110)
    print(f"{len(evals)} evals, {len(train)} train rows -> {out}")


if __name__ == "__main__":
    main()
