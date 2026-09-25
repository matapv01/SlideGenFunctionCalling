"""Run the frozen shared ViT evaluator on generated SlideGen PNG outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from transformers import ViTForImageClassification


DEFAULT_CRITERIA = ["mau_nen", "mau_chu", "size_chu", "de_nhau", "tran_chu"]
CRITERION_NAMES = {
    "mau_nen": "background_color",
    "mau_chu": "text_color",
    "size_chu": "font_size",
    "de_nhau": "overlap",
    "tran_chu": "text_overflow",
}


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=root.parent / "report_paper" / "img" / "qualitative",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=root / "experiments" / "train_test_protocol" / "shared_base" / "best.pt",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=root / "experiments" / "generated_output_evaluation",
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--device", default="cuda:0")
    return parser.parse_args()


def natural_key(path: Path) -> tuple:
    import re

    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    )


class GeneratedSlideDataset(Dataset):
    def __init__(self, paths: list[Path]) -> None:
        self.paths = paths
        self.transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, index: int) -> torch.Tensor:
        with Image.open(self.paths[index]) as image:
            return self.transform(image.convert("RGB"))


def checkpoint_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_model(checkpoint_path: Path, device: torch.device):
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    criteria = checkpoint.get("criteria", DEFAULT_CRITERIA)
    if criteria != DEFAULT_CRITERIA:
        raise ValueError(f"Unexpected criterion order: {criteria}")
    model = ViTForImageClassification.from_pretrained(
        checkpoint["base_model"],
        num_labels=len(criteria),
        problem_type="multi_label_classification",
        ignore_mismatched_sizes=True,
        local_files_only=True,
    )
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    return model.to(device).eval(), checkpoint, criteria


@torch.inference_mode()
def predict(model, loader: DataLoader, device: torch.device) -> tuple[np.ndarray, float]:
    probabilities = []
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    started = time.perf_counter()
    for pixels in loader:
        logits = model(pixel_values=pixels.to(device, non_blocking=True)).logits
        probabilities.append(torch.sigmoid(logits).cpu().numpy())
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elapsed = time.perf_counter() - started
    return np.concatenate(probabilities), elapsed


def summarize(probabilities: np.ndarray, threshold: float, criteria: list[str]) -> dict:
    predictions = probabilities >= threshold
    has_defect = predictions.any(axis=1)
    return {
        "slides": int(len(probabilities)),
        "pass_count": int((~has_defect).sum()),
        "defect_count": int(has_defect.sum()),
        "pass_rate": float((~has_defect).mean()),
        "defect_rate": float(has_defect.mean()),
        "mean_defect_probability": float(probabilities.mean()),
        "mean_predicted_defects_per_slide": float(predictions.sum(axis=1).mean()),
        "per_criterion": {
            CRITERION_NAMES[name]: {
                "predicted_defect_count": int(predictions[:, index].sum()),
                "predicted_defect_rate": float(predictions[:, index].mean()),
                "mean_probability": float(probabilities[:, index].mean()),
            }
            for index, name in enumerate(criteria)
        },
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.resolve()
    checkpoint_path = args.checkpoint.resolve()
    output_dir = args.output_dir.resolve()
    if not 0.0 < args.threshold < 1.0:
        raise ValueError("threshold must be between zero and one")
    paths = sorted(input_dir.rglob("*.png"), key=lambda path: (path.parent.name, natural_key(path)))
    if not paths:
        raise FileNotFoundError(f"No PNG files found under {input_dir}")
    if not checkpoint_path.is_file():
        raise FileNotFoundError(checkpoint_path)

    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    model, checkpoint, criteria = load_model(checkpoint_path, device)
    dataset = GeneratedSlideDataset(paths)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.workers,
        pin_memory=device.type == "cuda",
        persistent_workers=args.workers > 0,
    )
    probabilities, elapsed = predict(model, loader, device)
    predictions = probabilities >= args.threshold

    slide_rows = []
    for index, path in enumerate(paths):
        relative = path.relative_to(input_dir)
        row = {
            "deck": relative.parent.as_posix(),
            "slide": path.name,
            "relative_path": relative.as_posix(),
            "predicted_defect_count": int(predictions[index].sum()),
            "pass": int(not predictions[index].any()),
        }
        for criterion_index, criterion in enumerate(criteria):
            name = CRITERION_NAMES[criterion]
            row[f"probability_{name}"] = float(probabilities[index, criterion_index])
            row[f"prediction_{name}"] = int(predictions[index, criterion_index])
        slide_rows.append(row)

    deck_rows = []
    deck_summaries = {}
    deck_names = sorted({row["deck"] for row in slide_rows})
    for deck in deck_names:
        indices = [index for index, row in enumerate(slide_rows) if row["deck"] == deck]
        deck_summary = summarize(probabilities[indices], args.threshold, criteria)
        deck_summaries[deck] = deck_summary
        deck_rows.append(
            {
                "deck": deck,
                "slides": deck_summary["slides"],
                "pass_count": deck_summary["pass_count"],
                "pass_rate": deck_summary["pass_rate"],
                "defect_rate": deck_summary["defect_rate"],
                "mean_defect_probability": deck_summary["mean_defect_probability"],
                "mean_predicted_defects_per_slide": deck_summary[
                    "mean_predicted_defects_per_slide"
                ],
            }
        )

    overall = summarize(probabilities, args.threshold, criteria)
    deck_pass_rates = np.asarray([row["pass_rate"] for row in deck_rows])
    deck_defect_probabilities = np.asarray(
        [row["mean_defect_probability"] for row in deck_rows]
    )
    overall["deck_level"] = {
        "decks": len(deck_rows),
        "mean_pass_rate": float(deck_pass_rates.mean()),
        "std_pass_rate": float(deck_pass_rates.std(ddof=1)) if len(deck_rows) > 1 else 0.0,
        "mean_defect_probability": float(deck_defect_probabilities.mean()),
        "std_defect_probability": float(deck_defect_probabilities.std(ddof=1))
        if len(deck_rows) > 1
        else 0.0,
    }

    result = {
        "protocol": "frozen shared ViT inference on generated SlideGen outputs",
        "input_set": str(input_dir),
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": checkpoint_sha256(checkpoint_path),
        "checkpoint_epoch": int(checkpoint["epoch"]),
        "base_model": checkpoint["base_model"],
        "label_semantics": checkpoint.get("label_semantics", "1=error,0=no_error"),
        "criteria_order": criteria,
        "threshold": args.threshold,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "inference_seconds": elapsed,
        "latency_ms_per_slide_batch": elapsed * 1000 / len(paths),
        "overall": overall,
        "by_deck": deck_summaries,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "predictions.csv", slide_rows)
    write_csv(output_dir / "deck_metrics.csv", deck_rows)
    (output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
