"""Build deterministic GRPO document batches from the tracked offline corpus."""

from __future__ import annotations

import argparse
import json
import os
import random
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "rl" / "data" / "sft_function_call_dataset.json"
REQUIRED_FIELDS = {"category", "slide_content", "doc_id", "slide_index"}


def _load_rows(dataset_path: str | os.PathLike[str] | None = None) -> list[dict]:
    path = Path(
        dataset_path
        or os.getenv("GRPO_OFFLINE_DATASET")
        or DEFAULT_DATASET_PATH
    ).expanduser()
    if not path.is_file():
        raise FileNotFoundError(
            f"Offline GRPO dataset not found: {path}. "
            "Set GRPO_OFFLINE_DATASET to a compatible JSON corpus."
        )

    with path.open("r", encoding="utf-8") as handle:
        rows = json.load(handle)
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"Offline GRPO dataset must be a non-empty JSON list: {path}")

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Dataset row {index} is not an object")
        missing = REQUIRED_FIELDS.difference(row)
        if missing:
            raise ValueError(f"Dataset row {index} is missing fields: {sorted(missing)}")
    return rows


def _group_documents(rows: list[dict]) -> list[list[dict]]:
    grouped: dict[int | str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["doc_id"]].append(row)

    documents = []
    for doc_id in sorted(grouped, key=lambda value: (str(type(value)), str(value))):
        slides = sorted(grouped[doc_id], key=lambda row: int(row["slide_index"]))
        if slides:
            documents.append(slides)
    if not documents:
        raise ValueError("Offline GRPO dataset does not contain any documents")
    return documents


def _select_documents(
    documents: list[list[dict]],
    num_docs: int,
    step: int,
    seed: int,
) -> list[list[dict]]:
    if num_docs < 1:
        return []
    if step < 1:
        raise ValueError(f"step must be >= 1, got {step}")

    selected = []
    absolute_offset = (step - 1) * num_docs
    while len(selected) < num_docs:
        epoch = absolute_offset // len(documents)
        epoch_offset = absolute_offset % len(documents)
        order = list(range(len(documents)))
        random.Random(seed + epoch).shuffle(order)
        take = min(num_docs - len(selected), len(documents) - epoch_offset)
        selected.extend(documents[index] for index in order[epoch_offset : epoch_offset + take])
        absolute_offset += take
    return selected


def generate_docs(
    num_docs: int,
    step: int = 1,
    dataset_path: str | os.PathLike[str] | None = None,
    seed: int | None = None,
) -> list[list[dict]]:
    """Return a deterministic offline batch in the shape expected by GRPO."""
    rows = _load_rows(dataset_path)
    corpus = _group_documents(rows)
    effective_seed = (
        int(os.getenv("GRPO_DATA_SEED", "42"))
        if seed is None
        else int(seed)
    )
    selected = _select_documents(corpus, num_docs, step, effective_seed)

    result = []
    for batch_doc_id, source_slides in enumerate(selected):
        slides = []
        source_doc_id = source_slides[0]["doc_id"]
        for slide_index, row in enumerate(source_slides):
            content = str(row.get("slide_content") or "").strip()
            if not content:
                continue
            category = str(row.get("category") or "CONTENT_TOOLS")
            design_instruction = str(row.get("design_instruction") or "").strip()
            slides.append(
                {
                    "doc_id": batch_doc_id,
                    "source_doc_id": source_doc_id,
                    "slide_index": slide_index,
                    "heading": "",
                    "user_prompt": content,
                    "plan": {
                        "action": category,
                        "thought": design_instruction,
                    },
                }
            )
        if slides:
            result.append(slides)

    total_slides = sum(len(document) for document in result)
    print(
        f"Loaded {len(result)} offline docs ({total_slides} slides) "
        f"for GRPO step {step} from {len(corpus)} corpus docs."
    )
    return result



def load_offline_documents(
    dataset_path: str | os.PathLike[str] | None = None,
) -> list[list[dict]]:
    """Load the complete corpus once while preserving source document IDs."""
    documents = _group_documents(_load_rows(dataset_path))
    result = []
    for source_slides in documents:
        source_doc_id = source_slides[0]["doc_id"]
        slides = []
        for slide_index, row in enumerate(source_slides):
            content = str(row.get("slide_content") or "").strip()
            if not content:
                continue
            slides.append(
                {
                    "doc_id": source_doc_id,
                    "source_doc_id": source_doc_id,
                    "slide_index": slide_index,
                    "heading": "",
                    "user_prompt": content,
                    "plan": {
                        "action": str(row.get("category") or "CONTENT_TOOLS"),
                        "thought": str(
                            row.get("design_instruction") or ""
                        ).strip(),
                    },
                }
            )
        if slides:
            result.append(slides)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--dataset", default=None)
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "rl" / "data" / "slidegen_challenge_dataset.json"),
    )
    args = parser.parse_args()

    docs = generate_docs(args.limit, step=args.step, dataset_path=args.dataset)
    all_slides = [slide for document in docs for slide in document]
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(all_slides, handle, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_slides)} slides to {output_path}")
