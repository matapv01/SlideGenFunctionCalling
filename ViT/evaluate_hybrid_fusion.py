"""Fuse frozen OCR-rule predictions with locked-test ViT predictions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, hamming_loss, precision_score, recall_score

from train_vit_multilabel import CRITERIA


def parse_args() -> argparse.Namespace:
    root = Path(__file__).parent / "experiments" / "train_test_protocol"
    parser = argparse.ArgumentParser()
    parser.add_argument("--vit-predictions", type=Path, default=root / "test_evaluation" / "predictions.csv")
    parser.add_argument("--vit-metrics", type=Path, default=root / "test_evaluation" / "metrics.json")
    parser.add_argument("--rule-predictions", type=Path, default=root / "frozen_ocr_rules" / "predictions.csv")
    parser.add_argument("--rule-metrics", type=Path, default=root / "frozen_ocr_rules" / "metrics.json")
    parser.add_argument("--output-dir", type=Path, default=root / "hybrid_fusion")
    return parser.parse_args()


def summarize(labels: np.ndarray, predictions: np.ndarray) -> dict:
    slide_labels = (labels.sum(axis=1) > 0).astype(np.int64)
    slide_predictions = (predictions.sum(axis=1) > 0).astype(np.int64)
    result = {
        "macro_precision": float(precision_score(labels, predictions, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(labels, predictions, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "exact_match_accuracy": float(accuracy_score(labels, predictions)),
        "hamming_loss": float(hamming_loss(labels, predictions)),
        "slide_level": {
            "precision": float(precision_score(slide_labels, slide_predictions, zero_division=0)),
            "recall": float(recall_score(slide_labels, slide_predictions, zero_division=0)),
            "f1": float(f1_score(slide_labels, slide_predictions, zero_division=0)),
            "accuracy": float(accuracy_score(slide_labels, slide_predictions)),
        },
        "per_criterion": {},
    }
    for index, name in enumerate(CRITERIA):
        result["per_criterion"][name] = {
            "precision": float(precision_score(labels[:, index], predictions[:, index], zero_division=0)),
            "recall": float(recall_score(labels[:, index], predictions[:, index], zero_division=0)),
            "f1": float(f1_score(labels[:, index], predictions[:, index], zero_division=0)),
        }
    return result


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    vit = pd.read_csv(args.vit_predictions).sort_values("local_path").reset_index(drop=True)
    rules = pd.read_csv(args.rule_predictions).sort_values("local_path").reset_index(drop=True)
    if vit["local_path"].tolist() != rules["local_path"].tolist():
        raise RuntimeError("ViT and rule predictions do not describe the same test images")

    labels = vit[CRITERIA].to_numpy(dtype=np.int64)
    rule_predictions = rules[[f"rule_prediction_{name}" for name in CRITERIA]].to_numpy(dtype=np.int64)
    configurations = {"rule_only": rule_predictions}
    for mode in ["shared", "binary"]:
        probabilities = vit[[f"{mode}_probability_{name}" for name in CRITERIA]].to_numpy(dtype=float)
        vit_predictions = (probabilities >= 0.5).astype(np.int64)
        configurations[f"{mode}_vit"] = vit_predictions
        configurations[f"rules_plus_{mode}_vit"] = np.logical_or(rule_predictions, vit_predictions).astype(np.int64)

    vit_metrics = json.loads(args.vit_metrics.read_text())
    rule_metrics = json.loads(args.rule_metrics.read_text())
    results = {name: summarize(labels, predictions) for name, predictions in configurations.items()}
    rule_latency = 1000 * float(rule_metrics.get("elapsed_seconds_total", rule_metrics["elapsed_seconds_this_run"])) / len(vit)
    results["rule_only"]["latency_ms_per_slide"] = rule_latency
    for mode in ["shared", "binary"]:
        vit_latency = float(vit_metrics[mode]["latency_ms_per_slide"])
        results[f"{mode}_vit"]["latency_ms_per_slide"] = vit_latency
        results[f"rules_plus_{mode}_vit"]["latency_ms_per_slide"] = rule_latency + vit_latency

    output = {
        "fusion": "criterion-wise logical OR; a frozen-rule failure cannot be cancelled by ViT",
        "test_samples": len(vit),
        "threshold": 0.5,
        "results": results,
    }
    (args.output_dir / "metrics.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    prediction_output = vit[["path", "local_path", *CRITERIA]].copy()
    for config_name, predictions in configurations.items():
        for index, criterion in enumerate(CRITERIA):
            prediction_output[f"{config_name}_{criterion}"] = predictions[:, index]
    prediction_output.to_csv(args.output_dir / "predictions.csv", index=False)
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
