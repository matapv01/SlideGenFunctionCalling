"""Train one shared five-output ViT on the SlideGen multi-label benchmark."""

from __future__ import annotations

import argparse
import json
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
    hamming_loss,
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
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "experiments" / "vit_multilabel")
    parser.add_argument("--model", default="WinKawaks/vit-small-patch16-224")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--learning-rate", type=float, default=5e-5)
    parser.add_argument("--weight-decay", type=float, default=5e-3)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=45)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument(
        "--freeze-backbone",
        action="store_true",
        help="Freeze the pretrained ViT encoder and train only the classification head.",
    )
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
    if KAGGLE_MARKER in normalized:
        normalized = normalized.split(KAGGLE_MARKER, 1)[1]
        return (data_dir / "anh_slide" / "anh_slide" / normalized).resolve()
    return Path(normalized).resolve()


def load_split(csv_path: Path, data_dir: Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path)
    missing_columns = [name for name in ["path", *CRITERIA] if name not in frame.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in {csv_path}: {missing_columns}")
    frame["local_path"] = frame["path"].map(lambda value: str(remap_path(value, data_dir)))
    missing = [path for path in frame["local_path"] if not Path(path).is_file()]
    if missing:
        raise FileNotFoundError(f"{len(missing)} images missing; first: {missing[0]}")
    return frame


class SlideDataset(Dataset):
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


def make_loaders(train_frame, val_frame, batch_size, workers, seed):
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
    )
    train_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(3),
            transforms.ColorJitter(brightness=0.08, contrast=0.08, saturation=0.05),
            transforms.ToTensor(),
            normalize,
        ]
    )
    val_transform = transforms.Compose(
        [transforms.Resize((224, 224)), transforms.ToTensor(), normalize]
    )
    common = dict(
        batch_size=batch_size,
        num_workers=workers,
        pin_memory=True,
        persistent_workers=workers > 0,
    )
    generator = torch.Generator().manual_seed(seed)
    return (
        DataLoader(SlideDataset(train_frame, train_transform), shuffle=True, generator=generator, **common),
        DataLoader(SlideDataset(val_frame, val_transform), shuffle=False, **common),
    )


def metrics(labels: np.ndarray, probabilities: np.ndarray, thresholds=0.5) -> dict:
    predictions = (probabilities >= np.asarray(thresholds)).astype(np.int64)
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


def tune_thresholds(labels: np.ndarray, probabilities: np.ndarray) -> np.ndarray:
    candidates = np.linspace(0.05, 0.95, 181)
    selected = []
    for index in range(len(CRITERIA)):
        scored = [
            (threshold, f1_score(labels[:, index], probabilities[:, index] >= threshold, zero_division=0))
            for threshold in candidates
        ]
        selected.append(max(scored, key=lambda item: (item[1], -item[0]))[0])
    return np.asarray(selected)


@torch.inference_mode()
def evaluate(model, loader, device, loss_fn):
    model.eval()
    losses, labels, probabilities = [], [], []
    for pixels, targets in loader:
        pixels = pixels.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)
        logits = model(pixel_values=pixels).logits
        losses.append(float(loss_fn(logits, targets).item()))
        labels.append(targets.cpu().numpy())
        probabilities.append(torch.sigmoid(logits).cpu().numpy())
    return float(np.mean(losses)), np.concatenate(labels), np.concatenate(probabilities)


def main() -> None:
    args = parse_args()
    seed_everything(args.seed)
    device = torch.device(args.device)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_frame = load_split(args.data_dir / "train_dataset.csv", args.data_dir)
    val_frame = load_split(args.data_dir / "val_dataset.csv", args.data_dir)
    train_loader, val_loader = make_loaders(
        train_frame, val_frame, args.batch_size, args.workers, args.seed
    )
    positives = train_frame[CRITERIA].sum().to_numpy(dtype=np.float32)
    pos_weight = torch.tensor(
        (len(train_frame) - positives) / np.maximum(positives, 1), device=device
    )
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    model = ViTForImageClassification.from_pretrained(
        args.model,
        num_labels=len(CRITERIA),
        problem_type="multi_label_classification",
        ignore_mismatched_sizes=True,
    ).to(device)
    if args.freeze_backbone:
        for parameter in model.vit.parameters():
            parameter.requires_grad = False
    trainable_parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
    optimizer = torch.optim.AdamW(
        trainable_parameters, lr=args.learning_rate, weight_decay=args.weight_decay
    )
    total_steps = len(train_loader) * args.epochs
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, int(total_steps * 0.05)),
        num_training_steps=total_steps,
    )
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    checkpoint_path = args.output_dir / "best.pt"
    history, best_f1, stale, started = [], -1.0, 0, time.time()
    for epoch in range(1, args.epochs + 1):
        model.train()
        if args.freeze_backbone:
            model.vit.eval()
        train_losses = []
        for pixels, targets in train_loader:
            pixels = pixels.to(device, non_blocking=True)
            targets = targets.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
                logits = model(pixel_values=pixels).logits
                loss = loss_fn(logits, targets)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            train_losses.append(float(loss.item()))
        val_loss, labels, probabilities = evaluate(model, val_loader, device, loss_fn)
        val_metrics = metrics(labels, probabilities)
        record = {
            "epoch": epoch,
            "train_loss": float(np.mean(train_losses)),
            "val_loss": val_loss,
            **{key: value for key, value in val_metrics.items() if key != "per_criterion"},
        }
        history.append(record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
        if val_metrics["macro_f1"] > best_f1:
            best_f1, stale = val_metrics["macro_f1"], 0
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "criteria": CRITERIA,
                    "label_semantics": "1=error,0=no_error",
                    "base_model": args.model,
                    "epoch": epoch,
                    "freeze_backbone": args.freeze_backbone,
                    "val_metrics_05": val_metrics,
                },
                checkpoint_path,
            )
        else:
            stale += 1
            if stale >= args.patience:
                break
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    val_loss, labels, probabilities = evaluate(model, val_loader, device, loss_fn)
    tuned = tune_thresholds(labels, probabilities)
    result = {
        "checkpoint": str(checkpoint_path),
        "base_model": args.model,
        "best_epoch": checkpoint["epoch"],
        "train_samples": len(train_frame),
        "val_samples": len(val_frame),
        "pos_weight": pos_weight.cpu().tolist(),
        "freeze_backbone": args.freeze_backbone,
        "learning_rate": args.learning_rate,
        "trainable_parameters": sum(parameter.numel() for parameter in trainable_parameters),
        "total_parameters": sum(parameter.numel() for parameter in model.parameters()),
        "val_loss": val_loss,
        "metrics_at_0_5": metrics(labels, probabilities),
        "validation_tuned_thresholds": dict(zip(CRITERIA, tuned.tolist())),
        "validation_tuned_metrics": metrics(labels, probabilities, tuned),
        "elapsed_seconds": time.time() - started,
        "history": history,
    }
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    )
    prediction_frame = pd.DataFrame(labels, columns=[f"label_{name}" for name in CRITERIA])
    for i, name in enumerate(CRITERIA):
        prediction_frame[f"probability_{name}"] = probabilities[:, i]
    prediction_frame.to_csv(args.output_dir / "predictions.csv", index=False)
    config = {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()}
    (args.output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
