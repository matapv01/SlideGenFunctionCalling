"""Deterministic document split for the offline tool-call evaluator."""

from __future__ import annotations

import hashlib
from collections import defaultdict


def split_by_doc(
    samples: list[dict],
    eval_ratio: float = 0.1,
    test_ratio: float = 0.1,
    seed: int = 42,
) -> dict[str, list[dict]]:
    """Assign every sample to one stable split without separating documents."""
    if not 0 <= eval_ratio <= 1 or not 0 <= test_ratio <= 1:
        raise ValueError("eval_ratio and test_ratio must be between 0 and 1")
    if eval_ratio + test_ratio > 1:
        raise ValueError("eval_ratio + test_ratio must not exceed 1")

    documents: dict[str, list[dict]] = defaultdict(list)
    for index, row in enumerate(samples):
        doc_id = str(row.get("doc_id", f"sample-{index}"))
        documents[doc_id].append(row)

    splits: dict[str, list[dict]] = {"train": [], "eval": [], "test": []}
    for doc_id, rows in documents.items():
        digest = hashlib.sha256(f"{seed}:{doc_id}".encode()).hexdigest()
        value = (int(digest[:8], 16) % 10_000) / 10_000
        if value < test_ratio:
            split = "test"
        elif value < test_ratio + eval_ratio:
            split = "eval"
        else:
            split = "train"
        splits[split].extend(rows)
    return splits
