"""Create and audit the leakage-safe train/development/test protocol.

The original training CSV is stratified by the complete five-label signature.
The supplied 410-image CSV is copied only to the locked test split and is never
used for checkpoint selection or threshold tuning in the new protocol.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from train_vit_multilabel import CRITERIA, load_split


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "experiments" / "train_test_protocol" / "data",
    )
    parser.add_argument("--development-ratio", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=45)
    return parser.parse_args()


def label_signature(frame: pd.DataFrame) -> pd.Series:
    return frame[CRITERIA].astype(int).astype(str).agg("".join, axis=1)


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def distribution(frame: pd.DataFrame) -> dict:
    labels = frame[CRITERIA].astype(int)
    return {
        "images": len(frame),
        "clean": int((labels.sum(axis=1) == 0).sum()),
        "defective": int((labels.sum(axis=1) > 0).sum()),
        "criterion_positives": {name: int(labels[name].sum()) for name in CRITERIA},
        "label_signatures": label_signature(frame).value_counts().sort_index().to_dict(),
    }


def original_columns(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[["path", *CRITERIA]].copy()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    source_train = load_split(args.data_dir / "train_dataset.csv", args.data_dir)
    locked_test = load_split(args.data_dir / "val_dataset.csv", args.data_dir)
    fit, development = train_test_split(
        source_train,
        test_size=args.development_ratio,
        random_state=args.seed,
        shuffle=True,
        stratify=label_signature(source_train),
    )
    fit = fit.sort_index().reset_index(drop=True)
    development = development.sort_index().reset_index(drop=True)
    locked_test = locked_test.reset_index(drop=True)

    original_columns(fit).to_csv(args.output_dir / "train_dataset.csv", index=False)
    original_columns(development).to_csv(args.output_dir / "val_dataset.csv", index=False)
    original_columns(locked_test).to_csv(args.output_dir / "test_dataset.csv", index=False)

    split_paths = {
        "train": set(fit["local_path"]),
        "development": set(development["local_path"]),
        "test": set(locked_test["local_path"]),
    }
    path_overlap = {
        "train_development": len(split_paths["train"] & split_paths["development"]),
        "train_test": len(split_paths["train"] & split_paths["test"]),
        "development_test": len(split_paths["development"] & split_paths["test"]),
    }

    all_frames = pd.concat(
        [
            fit.assign(protocol_split="train"),
            development.assign(protocol_split="development"),
            locked_test.assign(protocol_split="test"),
        ],
        ignore_index=True,
    )
    all_frames["sha256"] = all_frames["local_path"].map(sha256)
    duplicate_groups = []
    for digest, group in all_frames.groupby("sha256"):
        if len(group) < 2:
            continue
        duplicate_groups.append(
            {
                "sha256": digest,
                "count": len(group),
                "splits": sorted(group["protocol_split"].unique().tolist()),
                "paths": group["local_path"].tolist(),
            }
        )
    cross_split_duplicates = [item for item in duplicate_groups if len(item["splits"]) > 1]

    audit = {
        "protocol": "stratified train/development with a locked supplied test split",
        "seed": args.seed,
        "development_ratio": args.development_ratio,
        "criteria": CRITERIA,
        "distribution": {
            "train": distribution(fit),
            "development": distribution(development),
            "test": distribution(locked_test),
        },
        "all_files_exist": True,
        "path_overlap": path_overlap,
        "duplicate_byte_groups": len(duplicate_groups),
        "cross_split_duplicate_byte_groups": len(cross_split_duplicates),
        "cross_split_duplicates": cross_split_duplicates,
    }
    (args.output_dir.parent / "split_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if any(path_overlap.values()) or cross_split_duplicates:
        raise RuntimeError("Leakage audit failed; inspect split_audit.json")
    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
