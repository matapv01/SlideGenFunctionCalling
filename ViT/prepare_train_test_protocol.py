"""Create and audit a slide-family-disjoint train/test protocol."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from PIL import Image
from sklearn.model_selection import StratifiedGroupKFold

from train_vit_multilabel import CRITERIA, KAGGLE_MARKER, load_split


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "experiments" / "train_test_protocol" / "data",
    )
    parser.add_argument("--seed", type=int, default=45)
    parser.add_argument("--test-fold", type=int, default=3)
    parser.add_argument("--development-fold", type=int, default=0)
    return parser.parse_args()


def label_signature(frame: pd.DataFrame) -> pd.Series:
    return frame[CRITERIA].astype(int).astype(str).agg("".join, axis=1)


def slide_family(path: str) -> str:
    normalized = str(path).replace("\\", "/")
    suffix = normalized.split(KAGGLE_MARKER, 1)[1]
    contributor = suffix.split("/", 1)[0]
    return f"{contributor}::{Path(normalized).stem}"


def labels_from_directory(path: str) -> dict[str, int]:
    """Recover the intended corruption labels from the dataset directory name."""
    normalized = str(path).replace("\\", "/").lower()
    suffix = normalized.split(KAGGLE_MARKER.lower(), 1)[1]
    parts = suffix.split("/")
    quality_group = parts[1]
    defect_folder = parts[2] if len(parts) > 3 else ""
    if quality_group == "dep":
        return {name: 0 for name in CRITERIA}
    keywords = {
        "mau_nen": ("mau_nen",),
        "mau_chu": ("mau_chu",),
        "size_chu": ("size_chu", "kich_thuoc"),
        "de_nhau": ("de_nhau", "de_len_nhau"),
        "tran_chu": ("tran_chu", "tran_ra_ngoai"),
    }
    return {
        name: int(any(keyword in defect_folder for keyword in aliases))
        for name, aliases in keywords.items()
    }


def split_fold(frame: pd.DataFrame, fold: int, seed: int):
    splitter = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=seed)
    folds = list(splitter.split(frame, label_signature(frame), frame["slide_family"]))
    if not 0 <= fold < len(folds):
        raise ValueError(f"fold must be in [0, {len(folds) - 1}]")
    train_indices, holdout_indices = folds[fold]
    return frame.iloc[train_indices].copy(), frame.iloc[holdout_indices].copy()


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_image(path: str) -> tuple[int, int]:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return image.size


def distribution(frame: pd.DataFrame) -> dict:
    labels = frame[CRITERIA].astype(int)
    return {
        "images": len(frame),
        "slide_families": int(frame["slide_family"].nunique()),
        "clean": int((labels.sum(axis=1) == 0).sum()),
        "defective": int((labels.sum(axis=1) > 0).sum()),
        "criterion_positives": {name: int(labels[name].sum()) for name in CRITERIA},
        "label_signatures": label_signature(frame).value_counts().sort_index().to_dict(),
    }


def original_columns(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[["path", *CRITERIA]].copy()


def overlap_counts(parts: dict[str, set]) -> dict:
    return {
        "train_development": len(parts["train"] & parts["development"]),
        "train_test": len(parts["train"] & parts["test"]),
        "development_test": len(parts["development"] & parts["test"]),
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    first = load_split(args.data_dir / "train_dataset.csv", args.data_dir)
    second = load_split(args.data_dir / "val_dataset.csv", args.data_dir)
    complete = pd.concat([first, second], ignore_index=True).drop_duplicates("path")
    complete["slide_family"] = complete["path"].map(slide_family)

    training_pool, test = split_fold(complete, args.test_fold, args.seed)
    train, development = split_fold(training_pool, args.development_fold, args.seed + 1)
    train = train.sort_index().reset_index(drop=True)
    development = development.sort_index().reset_index(drop=True)
    test = test.sort_index().reset_index(drop=True)

    original_columns(train).to_csv(args.output_dir / "train_dataset.csv", index=False)
    original_columns(development).to_csv(args.output_dir / "val_dataset.csv", index=False)
    original_columns(test).to_csv(args.output_dir / "test_dataset.csv", index=False)

    frames = {"train": train, "development": development, "test": test}
    path_overlap = overlap_counts({name: set(frame["local_path"]) for name, frame in frames.items()})
    family_overlap = overlap_counts({name: set(frame["slide_family"]) for name, frame in frames.items()})
    audited = pd.concat(
        [frame.assign(protocol_split=name) for name, frame in frames.items()], ignore_index=True
    )
    audited["sha256"] = audited["local_path"].map(sha256)
    audited["dimensions"] = audited["local_path"].map(verify_image)
    directory_labels = audited["path"].map(labels_from_directory)
    label_mismatches = []
    for index, inferred in directory_labels.items():
        csv_labels = {name: int(audited.at[index, name]) for name in CRITERIA}
        if csv_labels != inferred:
            label_mismatches.append(
                {"path": audited.at[index, "path"], "csv": csv_labels, "directory": inferred}
            )
    duplicate_groups = []
    for digest, group in audited.groupby("sha256"):
        if len(group) > 1:
            duplicate_groups.append(
                {
                    "sha256": digest,
                    "count": len(group),
                    "splits": sorted(group["protocol_split"].unique().tolist()),
                    "paths": group["local_path"].tolist(),
                }
            )
    cross_split_duplicates = [row for row in duplicate_groups if len(row["splits"]) > 1]
    audit = {
        "protocol": "group-stratified train/test; all variants of a source slide stay together",
        "seed": args.seed,
        "test_fold": args.test_fold,
        "development_fold": args.development_fold,
        "group_key": "contributor::slide_stem",
        "criteria": CRITERIA,
        "distribution": {name: distribution(frame) for name, frame in frames.items()},
        "all_files_exist": True,
        "all_images_decodable": True,
        "directory_label_mismatches": len(label_mismatches),
        "directory_label_mismatch_examples": label_mismatches[:20],
        "path_overlap": path_overlap,
        "slide_family_overlap": family_overlap,
        "duplicate_byte_groups": len(duplicate_groups),
        "cross_split_duplicate_byte_groups": len(cross_split_duplicates),
        "cross_split_duplicates": cross_split_duplicates,
    }
    audit_path = args.output_dir.parent / "split_audit.json"
    audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if (
        any(path_overlap.values())
        or any(family_overlap.values())
        or cross_split_duplicates
        or label_mismatches
    ):
        raise RuntimeError(f"Leakage audit failed; inspect {audit_path}")
    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
