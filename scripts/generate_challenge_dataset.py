"""Build deterministic GRPO document batches from the tracked offline corpus."""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rl.image_assets import approved_images_for_row, read_image_manifest


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
                raise ValueError(
                    f"Empty slide_content in doc {source_doc_id!r}, "
                    f"slide {row.get('slide_index', slide_index)!r}"
                )
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
    """Load rebuilt content, its original source, planned style, and assets."""
    documents = _group_documents(_load_rows(dataset_path))
    has_legacy_rows = any(
        int(row.get("corpus_version") or 0) < 2
        for document in documents
        for row in document
    )
    image_manifest = read_image_manifest() if has_legacy_rows else {}
    result = []
    for source_slides in documents:
        source_doc_id = source_slides[0]["doc_id"]
        slides = []
        for slide_index, row in enumerate(source_slides):
            corpus_version = int(row.get("corpus_version") or 0)
            source_plan = dict(row.get("plan") or {})
            content = str(row.get("slide_content") or "").strip()
            if not content:
                raise ValueError(
                    f"Empty slide_content in doc {source_doc_id!r}, "
                    f"slide {row.get('slide_index', slide_index)!r}"
                )
            approved_images = approved_images_for_row(row, image_manifest)
            if corpus_version >= 2:
                raw_style = row.get("style_context")
                try:
                    style_context = (
                        json.loads(raw_style) if isinstance(raw_style, str) else raw_style
                    )
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid style_context for doc {source_doc_id!r}, "
                        f"slide {row.get('slide_index')!r}"
                    ) from exc
                if not isinstance(style_context, dict) or not style_context:
                    raise ValueError(
                        f"Missing style_context for doc {source_doc_id!r}, "
                        f"slide {row.get('slide_index')!r}"
                    )
                if "source_slide_content" not in row:
                    raise ValueError(
                        f"Missing source_slide_content for doc {source_doc_id!r}, "
                        f"slide {row.get('slide_index')!r}"
                    )
                source_content = str(row.get("source_slide_content") or "").strip()
                if not source_content:
                    raise ValueError(
                        f"Empty source_slide_content for doc {source_doc_id!r}, "
                        f"slide {row.get('slide_index')!r}"
                    )
                image_mode = str(source_plan.get("image_mode") or "none")
                if image_mode not in {"none", "semantic"}:
                    raise ValueError(
                        f"Invalid image_mode for doc {source_doc_id!r}, "
                        f"slide {row.get('slide_index')!r}: {image_mode!r}"
                    )
                expected_image_ids = {
                    str(image_id) for image_id in source_plan.get("approved_image_ids") or []
                }
                actual_image_ids = {str(image.get("source_id") or "") for image in approved_images}
                if image_mode == "semantic" and not approved_images:
                    raise ValueError(
                        f"Semantic image sample has no usable asset for doc "
                        f"{source_doc_id!r}, slide {row.get('slide_index')!r}"
                    )
                if image_mode == "none" and approved_images:
                    raise ValueError(
                        f"No-image sample unexpectedly contains approved assets for doc "
                        f"{source_doc_id!r}, slide {row.get('slide_index')!r}"
                    )
                if expected_image_ids != actual_image_ids:
                    raise ValueError(
                        f"Approved image IDs do not match cached assets for doc "
                        f"{source_doc_id!r}, slide {row.get('slide_index')!r}"
                    )
            else:
                style_context = {}
                source_content = content
            slides.append(
                {
                    "doc_id": source_doc_id,
                    "source_doc_id": source_doc_id,
                    "slide_index": int(row.get("slide_index", slide_index)),
                    "heading": str(source_plan.get("slide_topic") or ""),
                    # Train and reward against the same immutable source text,
                    # including when loading an older corpus with rewritten targets.
                    "user_prompt": source_content,
                    "source_content": source_content,
                    "style_context": style_context,
                    "plan": {
                        **source_plan,
                        "action": str(
                            source_plan.get("action")
                            or row.get("category")
                            or "CONTENT_TOOLS"
                        ),
                        "thought": str(
                            source_plan.get("visual_layout_request")
                            or row.get("design_instruction")
                            or ""
                        ).strip(),
                        "slide_topic": str(source_plan.get("slide_topic") or ""),
                        "slide_purpose": str(source_plan.get("slide_purpose") or ""),
                        "retrieval_query": str(source_plan.get("retrieval_query") or ""),
                        "image_mode": "semantic" if approved_images else "none",
                    },
                    "approved_images": approved_images,
                }
            )
        if slides:
            if any(slide["style_context"] != slides[0]["style_context"] for slide in slides[1:]):
                raise ValueError(
                    f"Inconsistent style_context within document {source_doc_id!r}"
                )
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
