"""Evaluate selected shared and binary ViTs once on the locked test split."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from transformers import ViTForImageClassification

from train_vit_multilabel import CRITERIA, load_split, metrics


def parse_args() -> argparse.Namespace:
    root = Path(__file__).parent / "experiments" / "train_test_protocol"
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument("--test-csv", type=Path, default=root / "data" / "test_dataset.csv")
    parser.add_argument("--shared-dir", type=Path, default=root / "shared_base")
    parser.add_argument("--frozen-dir", type=Path)
    parser.add_argument("--binary-color-dir", type=Path, default=root / "binary_small")
    parser.add_argument("--binary-structural-dir", type=Path, default=root / "binary_base_structural")
    parser.add_argument("--output-dir", type=Path, default=root / "test_evaluation")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--workers", type=int, default=8)
    return parser.parse_args()


class TestDataset(Dataset):
    def __init__(self, frame: pd.DataFrame, transform) -> None:
        self.paths = frame["local_path"].tolist()
        self.labels = frame[CRITERIA].astype(np.float32).to_numpy()
        self.transform = transform

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, index: int):
        with Image.open(self.paths[index]) as image:
            pixels = self.transform(image.convert("RGB"))
        return pixels, torch.from_numpy(self.labels[index])


def load_model(path: Path, device: torch.device, num_labels: int):
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    model_kwargs = {
        "num_labels": num_labels,
        "ignore_mismatched_sizes": True,
        "local_files_only": True,
    }
    if num_labels > 1:
        model_kwargs["problem_type"] = "multi_label_classification"
    model = ViTForImageClassification.from_pretrained(checkpoint["base_model"], **model_kwargs)
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    return model.to(device).eval(), checkpoint


@torch.inference_mode()
def predict_shared(model, loader, device):
    labels, probabilities = [], []
    for pixels, targets in loader:
        logits = model(pixel_values=pixels.to(device, non_blocking=True)).logits
        labels.append(targets.numpy())
        probabilities.append(torch.sigmoid(logits).cpu().numpy())
    return np.concatenate(labels), np.concatenate(probabilities)


@torch.inference_mode()
def predict_binary(models, loader, device):
    labels, probability_batches = [], []
    for pixels, targets in loader:
        pixels = pixels.to(device, non_blocking=True)
        columns = [
            torch.sigmoid(models[name](pixel_values=pixels).logits).reshape(-1, 1)
            for name in CRITERIA
        ]
        labels.append(targets.numpy())
        probability_batches.append(torch.cat(columns, dim=1).cpu().numpy())
    return np.concatenate(labels), np.concatenate(probability_batches)


@torch.inference_mode()
def latency_ms(models, dataset, device, shared: bool) -> float:
    pixels, _ = dataset[0]
    pixels = pixels.unsqueeze(0).to(device)
    for _ in range(10):
        if shared:
            models["shared"](pixel_values=pixels)
        else:
            for name in CRITERIA:
                models[name](pixel_values=pixels)
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    started = time.perf_counter()
    for index in range(len(dataset)):
        pixels, _ = dataset[index]
        pixels = pixels.unsqueeze(0).to(device)
        if shared:
            models["shared"](pixel_values=pixels)
        else:
            for name in CRITERIA:
                models[name](pixel_values=pixels)
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    return (time.perf_counter() - started) * 1000 / len(dataset)


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device(args.device)
    frame = load_split(args.test_csv, args.data_dir)
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    dataset = TestDataset(frame, transform)
    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.workers,
        pin_memory=device.type == "cuda",
        persistent_workers=args.workers > 0,
    )

    shared, shared_checkpoint = load_model(args.shared_dir / "best.pt", device, len(CRITERIA))
    labels, shared_probabilities = predict_shared(shared, loader, device)
    shared_dev = json.loads((args.shared_dir / "metrics.json").read_text())
    shared_thresholds = np.asarray(
        [shared_dev["validation_tuned_thresholds"][name] for name in CRITERIA]
    )
    shared_result = {
        "checkpoint_epoch": int(shared_checkpoint["epoch"]),
        "threshold_0_5": metrics(labels, shared_probabilities, 0.5),
        "development_tuned_thresholds": dict(zip(CRITERIA, shared_thresholds.tolist())),
        "development_tuned": metrics(labels, shared_probabilities, shared_thresholds),
    }
    shared_result["latency_ms_per_slide"] = latency_ms(
        {"shared": shared}, dataset, device, shared=True
    )
    del shared
    if device.type == "cuda":
        torch.cuda.empty_cache()

    frozen_result, frozen_probabilities = None, None
    if args.frozen_dir is not None:
        frozen, frozen_checkpoint = load_model(
            args.frozen_dir / "best.pt", device, len(CRITERIA)
        )
        frozen_labels, frozen_probabilities = predict_shared(frozen, loader, device)
        if not np.array_equal(labels, frozen_labels):
            raise RuntimeError("Shared and frozen test labels differ")
        frozen_dev = json.loads((args.frozen_dir / "metrics.json").read_text())
        frozen_thresholds = np.asarray(
            [frozen_dev["validation_tuned_thresholds"][name] for name in CRITERIA]
        )
        frozen_result = {
            "checkpoint": str(args.frozen_dir / "best.pt"),
            "checkpoint_epoch": int(frozen_checkpoint["epoch"]),
            "learning_rate": frozen_dev.get("learning_rate"),
            "trainable_parameters": frozen_dev.get("trainable_parameters"),
            "total_parameters": frozen_dev.get("total_parameters"),
            "threshold_0_5": metrics(labels, frozen_probabilities, 0.5),
            "development_tuned_thresholds": dict(zip(CRITERIA, frozen_thresholds.tolist())),
            "development_tuned": metrics(labels, frozen_probabilities, frozen_thresholds),
        }
        frozen_result["latency_ms_per_slide"] = latency_ms(
            {"shared": frozen}, dataset, device, shared=True
        )
        del frozen
        if device.type == "cuda":
            torch.cuda.empty_cache()

    binary_models, binary_thresholds, binary_epochs = {}, [], {}
    for name in CRITERIA:
        model_dir = args.binary_color_dir if name in {"mau_nen", "mau_chu"} else args.binary_structural_dir
        model, checkpoint = load_model(model_dir / name / "best.pt", device, 1)
        binary_models[name] = model
        criterion_result = json.loads((model_dir / name / "metrics.json").read_text())
        binary_thresholds.append(criterion_result["validation_tuned_threshold"])
        binary_epochs[name] = int(checkpoint["epoch"])
    binary_labels, binary_probabilities = predict_binary(binary_models, loader, device)
    if not np.array_equal(labels, binary_labels):
        raise RuntimeError("Shared and binary test labels differ")
    binary_thresholds = np.asarray(binary_thresholds)
    binary_result = {
        "checkpoint_epochs": binary_epochs,
        "threshold_0_5": metrics(labels, binary_probabilities, 0.5),
        "development_tuned_thresholds": dict(zip(CRITERIA, binary_thresholds.tolist())),
        "development_tuned": metrics(labels, binary_probabilities, binary_thresholds),
    }
    binary_result["latency_ms_per_slide"] = latency_ms(
        binary_models, dataset, device, shared=False
    )

    result = {
        "protocol": "train/development selection followed by one locked-test evaluation",
        "test_samples": len(frame),
        "threshold_semantics": "probability of error",
        "shared": shared_result,
        "frozen": frozen_result,
        "binary": binary_result,
    }
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    predictions = frame[["path", "local_path", *CRITERIA]].copy()
    for index, name in enumerate(CRITERIA):
        predictions[f"shared_probability_{name}"] = shared_probabilities[:, index]
        if frozen_probabilities is not None:
            predictions[f"frozen_probability_{name}"] = frozen_probabilities[:, index]
        predictions[f"binary_probability_{name}"] = binary_probabilities[:, index]
    predictions.to_csv(args.output_dir / "predictions.csv", index=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
