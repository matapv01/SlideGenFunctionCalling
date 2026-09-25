"""Benchmark the exact ViT provider used by the SlideGen workflow."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    hamming_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)

from backend.infrastructure.aesthetic.vit_aesthetic_provider import (
    CRITERIA,
    DISPLAY_NAMES,
    ViTAestheticProvider,
)
from ViT.train_vit_multilabel import load_split


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["multilabel", "binary"], required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def compute_metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict:
    predictions = (probabilities >= 0.5).astype(np.int64)
    result = {
        "macro_precision": float(precision_score(labels, predictions, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(labels, predictions, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "micro_f1": float(f1_score(labels, predictions, average="micro", zero_division=0)),
        "exact_match_accuracy": float(accuracy_score(labels, predictions)),
        "hamming_loss": float(hamming_loss(labels, predictions)),
        "macro_auprc": float(average_precision_score(labels, probabilities, average="macro")),
        "macro_auroc": float(roc_auc_score(labels, probabilities, average="macro")),
    }
    result["per_criterion"] = {
        name: {
            "precision": float(precision_score(labels[:, i], predictions[:, i], zero_division=0)),
            "recall": float(recall_score(labels[:, i], predictions[:, i], zero_division=0)),
            "f1": float(f1_score(labels[:, i], predictions[:, i], zero_division=0)),
            "auprc": float(average_precision_score(labels[:, i], probabilities[:, i])),
            "auroc": float(roc_auc_score(labels[:, i], probabilities[:, i])),
        }
        for i, name in enumerate(CRITERIA)
    }
    return result


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame = load_split(args.data_dir / "val_dataset.csv", args.data_dir)
    provider = ViTAestheticProvider(device=args.device, mode=args.mode)
    reverse_names = {display: criterion for criterion, display in DISPLAY_NAMES.items()}

    # Warm up CUDA before latency measurement.
    provider.evaluate(frame.iloc[0]["local_path"])
    if torch.cuda.is_available() and args.device.startswith("cuda"):
        torch.cuda.synchronize(torch.device(args.device))

    probability_rows = []
    started = time.perf_counter()
    for index, row in frame.iterrows():
        _, _, scores = provider.evaluate(row["local_path"])
        probability_rows.append(
            [scores[DISPLAY_NAMES[name]] for name in CRITERIA]
        )
        if (index + 1) % 50 == 0:
            print(json.dumps({"mode": args.mode, "processed": index + 1}), flush=True)
    if torch.cuda.is_available() and args.device.startswith("cuda"):
        torch.cuda.synchronize(torch.device(args.device))
    elapsed = time.perf_counter() - started

    labels = frame[CRITERIA].to_numpy(dtype=np.int64)
    probabilities = np.asarray(probability_rows, dtype=np.float64)
    result = {
        "mode": args.mode,
        "evaluator": provider.evaluator_name,
        "samples": len(frame),
        "threshold": 0.5,
        "elapsed_seconds": elapsed,
        "latency_ms_per_slide": elapsed * 1000 / len(frame),
        "metrics": compute_metrics(labels, probabilities),
    }
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    output = frame[["local_path", *CRITERIA]].copy()
    for i, name in enumerate(CRITERIA):
        output[f"probability_{name}"] = probabilities[:, i]
    output.to_csv(args.output_dir / "predictions.csv", index=False)
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
