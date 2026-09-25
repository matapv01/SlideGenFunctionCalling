"""Train frozen-rule complementary ViT evaluators on the SlideGen benchmark.

The supplied CSV split is preserved. Labels use 1=error and 0=no error.
Kaggle absolute paths are remapped to the local ``ViT/data`` directory.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from transformers import ViTForImageClassification, get_cosine_schedule_with_warmup


CRITERIA = ["mau_nen", "mau_chu", "size_chu", "de_nhau", "tran_chu"]
KAGGLE_MARKER = "/anh_slide/anh_slide/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "experiments" / "vit_binary")
    parser.add_argument("--model", default="WinKawaks/vit-small-patch16-224")
    parser.add_argument("--criteria", nargs="+", choices=CRITERIA, default=CRITERIA)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=5e-5)
    parser.add_argument("--weight-decay", type=float, default=5e-3)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=45)
    parser.add_argument("--device", default="cuda:0")
    return parser.parse_args()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def remap_path(raw_path: str, data_dir: Path) -> Path:
    normalized = str(raw_path).replace("\\", "/")
    if KAGGLE_MARKER not in normalized:
        candidate = Path(normalized)
    else:
        suffix = normalized.split(KAGGLE_MARKER, 1)[1]
        candidate = data_dir / "anh_slide" / "anh_slide" / suffix
    return candidate.resolve()


def load_split(csv_path: Path, data_dir: Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path)
    missing_columns = [column for column in ["path", *CRITERIA] if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in {csv_path}: {missing_columns}")
    frame["local_path"] = frame["path"].map(lambda value: str(remap_path(value, data_dir)))
    missing = [path for path in frame["local_path"] if not Path(path).is_file()]
    if missing:
        raise FileNotFoundError(f"{len(missing)} images are missing; first missing path: {missing[0]}")
    return frame


class SlideDataset(Dataset):
    def __init__(self, frame: pd.DataFrame, criterion: str, transform) -> None:
        self.paths = frame["local_path"].tolist()
        self.labels = frame[criterion].astype(np.float32).to_numpy()
        self.transform = transform

    def __len__(self) -> int:
        return len(self.paths)

    def __getitem__(self, index: int):
        with Image.open(self.paths[index]) as image:
            pixel_values = self.transform(image.convert("RGB"))
        return pixel_values, torch.tensor(self.labels[index], dtype=torch.float32)


def make_loaders(train_frame, val_frame, criterion, batch_size, workers, seed):
    image_mean = [0.485, 0.456, 0.406]
    image_std = [0.229, 0.224, 0.225]
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(3),
        transforms.ColorJitter(brightness=0.08, contrast=0.08, saturation=0.05),
        transforms.ToTensor(),
        transforms.Normalize(image_mean, image_std),
    ])
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(image_mean, image_std),
    ])
    generator = torch.Generator().manual_seed(seed)
    common = dict(batch_size=batch_size, num_workers=workers, pin_memory=True, persistent_workers=workers > 0)
    train_loader = DataLoader(
        SlideDataset(train_frame, criterion, train_transform),
        shuffle=True,
        generator=generator,
        **common,
    )
    val_loader = DataLoader(SlideDataset(val_frame, criterion, val_transform), shuffle=False, **common)
    return train_loader, val_loader


def compute_metrics(labels: np.ndarray, probabilities: np.ndarray, threshold: float) -> dict[str, float]:
    predictions = (probabilities >= threshold).astype(np.int64)
    metrics = {
        "threshold": float(threshold),
        "accuracy": float(accuracy_score(labels, predictions)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "auprc": float(average_precision_score(labels, probabilities)),
    }
    metrics["auroc"] = float(roc_auc_score(labels, probabilities)) if len(np.unique(labels)) == 2 else float("nan")
    return metrics


def tune_threshold(labels: np.ndarray, probabilities: np.ndarray) -> tuple[float, dict[str, float]]:
    candidates = np.linspace(0.05, 0.95, 181)
    scored = [(threshold, compute_metrics(labels, probabilities, threshold)) for threshold in candidates]
    threshold, metrics = max(scored, key=lambda item: (item[1]["f1"], item[1]["recall"], -item[0]))
    return float(threshold), metrics


@torch.inference_mode()
def evaluate(model, loader, device, criterion_loss):
    model.eval()
    losses, probabilities, labels = [], [], []
    for pixel_values, batch_labels in loader:
        pixel_values = pixel_values.to(device, non_blocking=True)
        batch_labels = batch_labels.to(device, non_blocking=True)
        logits = model(pixel_values=pixel_values).logits.squeeze(-1)
        losses.append(float(criterion_loss(logits, batch_labels).item()))
        probabilities.extend(torch.sigmoid(logits).cpu().numpy().tolist())
        labels.extend(batch_labels.cpu().numpy().astype(np.int64).tolist())
    return float(np.mean(losses)), np.asarray(labels), np.asarray(probabilities)


def train_one(args, criterion, train_frame, val_frame, output_dir, device):
    criterion_dir = output_dir / criterion
    criterion_dir.mkdir(parents=True, exist_ok=True)
    train_loader, val_loader = make_loaders(
        train_frame, val_frame, criterion, args.batch_size, args.workers, args.seed
    )
    positives = float(train_frame[criterion].sum())
    negatives = float(len(train_frame) - positives)
    pos_weight = torch.tensor([negatives / max(positives, 1.0)], device=device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    model = ViTForImageClassification.from_pretrained(
        args.model,
        num_labels=1,
        ignore_mismatched_sizes=True,
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    total_steps = len(train_loader) * args.epochs
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, int(total_steps * 0.05)),
        num_training_steps=total_steps,
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")

    best_f1, stale_epochs, history = -1.0, 0, []
    checkpoint_path = criterion_dir / "best.pt"
    started = time.time()
    for epoch in range(1, args.epochs + 1):
        model.train()
        train_losses = []
        for pixel_values, labels in train_loader:
            pixel_values = pixel_values.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
                logits = model(pixel_values=pixel_values).logits.squeeze(-1)
                loss = loss_fn(logits, labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            train_losses.append(float(loss.item()))

        val_loss, val_labels, val_probabilities = evaluate(model, val_loader, device, loss_fn)
        metrics_05 = compute_metrics(val_labels, val_probabilities, 0.5)
        record = {
            "epoch": epoch,
            "train_loss": float(np.mean(train_losses)),
            "val_loss": val_loss,
            **{f"val_{key}_05": value for key, value in metrics_05.items()},
        }
        history.append(record)
        print(json.dumps({"criterion": criterion, **record}, ensure_ascii=False), flush=True)

        if metrics_05["f1"] > best_f1:
            best_f1 = metrics_05["f1"]
            stale_epochs = 0
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "criterion": criterion,
                    "label_semantics": "1=error,0=no_error",
                    "base_model": args.model,
                    "epoch": epoch,
                    "val_metrics_05": metrics_05,
                },
                checkpoint_path,
            )
        else:
            stale_epochs += 1
            if stale_epochs >= args.patience:
                break

    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    val_loss, labels, probabilities = evaluate(model, val_loader, device, loss_fn)
    threshold, tuned_metrics = tune_threshold(labels, probabilities)
    result = {
        "criterion": criterion,
        "checkpoint": str(checkpoint_path),
        "best_epoch": int(checkpoint["epoch"]),
        "train_samples": len(train_frame),
        "val_samples": len(val_frame),
        "train_positive": int(positives),
        "val_positive": int(val_frame[criterion].sum()),
        "pos_weight": float(pos_weight.item()),
        "val_loss": val_loss,
        "metrics_at_0_5": compute_metrics(labels, probabilities, 0.5),
        "validation_tuned_metrics": tuned_metrics,
        "validation_tuned_threshold": threshold,
        "elapsed_seconds": time.time() - started,
        "history": history,
    }
    (criterion_dir / "metrics.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    pd.DataFrame({"label": labels, "probability": probabilities}).to_csv(
        criterion_dir / "predictions.csv", index=False
    )
    return result


def main() -> None:
    args = parse_args()
    seed_everything(args.seed)
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")
    device = torch.device(args.device)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_frame = load_split(args.data_dir / "train_dataset.csv", args.data_dir)
    val_frame = load_split(args.data_dir / "val_dataset.csv", args.data_dir)
    config = vars(args).copy()
    config.update({key: str(value) for key, value in config.items() if isinstance(value, Path)})
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")

    results = []
    for criterion in args.criteria:
        results.append(train_one(args, criterion, train_frame, val_frame, args.output_dir, device))
    summary = pd.DataFrame([
        {
            "criterion": item["criterion"],
            "best_epoch": item["best_epoch"],
            **{f"at_0.5_{key}": value for key, value in item["metrics_at_0_5"].items()},
            **{f"tuned_{key}": value for key, value in item["validation_tuned_metrics"].items()},
        }
        for item in results
    ])
    summary.to_csv(args.output_dir / "summary.csv", index=False)
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
