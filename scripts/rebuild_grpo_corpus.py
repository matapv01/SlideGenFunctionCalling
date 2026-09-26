"""Rebuild the GRPO corpus from slide text through the production planning pipeline."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.application.services.image_relevance_service import ImageRelevanceService
from backend.application.services.slide_asset_service import slide_asset_service
from backend.config import (
    IMAGE_SEARCH_MAX_CONCURRENCY,
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_REQUEST_TIMEOUT_SECONDS,
    LLM_TEMPERATURE,
    LLM_TOP_P,
    OUTPUT_DIR,
    PLANNER_MAX_CONCURRENCY,
    VLM_API_KEY,
    VLM_BASE_URL,
    VLM_MODEL,
    VLM_REQUEST_MAX_CONCURRENCY,
    VLM_REQUEST_TIMEOUT_SECONDS,
)
from backend.infrastructure.llm.gemini_provider import GeminiLLMProvider
from backend.infrastructure.llm.request_limiter import LLMRequestLimiter
from backend.workflows.slidegen_workflow.nodes.deck_style_planner import create_deck_style
from backend.workflows.slidegen_workflow.nodes.image_candidate_search import search_image_candidates
from backend.workflows.slidegen_workflow.nodes.image_verifier import verify_slide_images
from backend.workflows.slidegen_workflow.nodes.slide_planner import (
    build_slide_context_maps,
    planning_slide,
)
from backend.workflows.slidegen_workflow.nodes.slide_refiner import refine_slide_plans
from scripts.generate_challenge_dataset import DEFAULT_DATASET_PATH, _group_documents, _load_rows


DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "rl" / "data" / "grpo_replanned_dataset.json"
DEFAULT_ASSET_DIR = OUTPUT_DIR / "grpo_image_cache"


def _write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    temporary.replace(path)


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_pipeline_config(
    allow_external_search: bool,
) -> tuple[dict, ImageRelevanceService]:
    planner_limiter = LLMRequestLimiter(
        max(1, int(PLANNER_MAX_CONCURRENCY))
    )
    planner_provider = GeminiLLMProvider(
        api_keys=[LLM_API_KEY or "local-openai-compatible"],
        model=os.getenv("GRPO_REBUILD_PLANNER_MODEL", LLM_MODEL),
        base_url=os.getenv("GRPO_REBUILD_PLANNER_BASE_URL", LLM_BASE_URL),
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        top_p=LLM_TOP_P,
        request_limiter=planner_limiter,
        request_timeout=LLM_REQUEST_TIMEOUT_SECONDS,
    )
    vision_limiter = LLMRequestLimiter(
        max(1, int(VLM_REQUEST_MAX_CONCURRENCY))
    )
    vision_provider = GeminiLLMProvider(
        api_keys=[VLM_API_KEY or "local-openai-compatible"],
        model=os.getenv("GRPO_IMAGE_VLM_MODEL", VLM_MODEL),
        base_url=os.getenv("GRPO_IMAGE_VLM_BASE_URL", VLM_BASE_URL),
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        top_p=LLM_TOP_P,
        request_limiter=vision_limiter,
        request_timeout=VLM_REQUEST_TIMEOUT_SECONDS,
    )
    verifier = ImageRelevanceService(
        vision_provider,
        model=os.getenv("GRPO_IMAGE_VLM_MODEL", VLM_MODEL),
    )
    config = {
        "configurable": {
            "llm": planner_provider.llm_client,
            "planner_llm": planner_provider.llm_client,
            "image_relevance_verifier": verifier,
            "llm_request_limiter": planner_limiter,
            "strict_grpo_preprocessing": True,
            "disable_external_image_search": not allow_external_search,
        },
        "max_concurrency": max(1, int(IMAGE_SEARCH_MAX_CONCURRENCY)),
    }
    return config, verifier


def _document_state(rows: list[dict], doc_id: int | str) -> dict:
    chunks = []
    positions = []
    section_ids = []
    for index, row in enumerate(rows):
        content = str(row.get("slide_content") or "").strip()
        heading = content.splitlines()[0][:160] if content else f"Slide {index + 1}"
        chunks.append(
            {
                "heading": heading,
                "content": content,
                "position": 0 if index == 0 else index,
            }
        )
        positions.append(0 if index == 0 else index)
        section_ids.append(f"doc-{doc_id}")
    title = chunks[0]["heading"] if chunks else f"Document {doc_id}"
    context_maps = build_slide_context_maps(chunks, intro_mode="detect")
    return {
        "slide_chunks": chunks,
        "slide_context_maps": context_maps,
        "slide_positions": positions,
        "section_ids": section_ids,
        "slide_options": {"presentation_instruction": ""},
        "document_title": title,
        "document_outline": context_maps,
        "document_structure": context_maps,
    }


def _materialize_assignments(
    assignments: list[dict],
    asset_dir: Path,
) -> dict[int, list[dict]]:
    by_slide: dict[int, list[dict]] = {}
    for item in assignments:
        try:
            slide_index = int(item.get("slide_index", -1))
            source_url = str(item.get("source_url") or "").strip()
            confidence = float(item.get("confidence") or 0.0)
            if slide_index < 0 or not source_url or confidence < 0.5:
                continue
            source_path = slide_asset_service.materialize(source_url, asset_dir)
            if not source_path.startswith("/static/output/"):
                continue
            local_path = (
                OUTPUT_DIR / source_path.removeprefix("/static/output/")
            ).resolve()
            local_path.relative_to(OUTPUT_DIR.resolve())
            if not local_path.is_file():
                continue
        except Exception as exc:
            print(
                f"  Image rejected after VLM approval "
                f"({item.get('source_id', '?')}): {exc}"
            )
            continue
        record = {
            "source_id": str(item.get("source_id") or ""),
            "source_type": "vlm_verified_search",
            "selected_source_url": source_url,
            "source_path": source_path,
            "local_path": str(local_path),
            "role": str(item.get("role") or "illustration"),
            "query": str(item.get("query") or ""),
            "visual_notes": str(item.get("visual_notes") or "")[:500],
            "caption_hint": str(item.get("caption_hint") or "")[:300],
            "placement_hint": str(item.get("placement_hint") or "")[:300],
            "confidence": confidence,
        }
        by_slide.setdefault(slide_index, []).append(record)
    return by_slide


def _rebuild_document(
    source_rows: list[dict],
    config: dict,
    verifier: ImageRelevanceService,
    asset_dir: Path,
) -> list[dict]:
    doc_id = source_rows[0]["doc_id"]
    state = _document_state(source_rows, doc_id)
    create_deck_style(state, config)
    planning_slide(state, config)
    if len(state.get("slide_plans") or []) != len(source_rows):
        raise RuntimeError(f"Planner returned an incomplete document {doc_id}")

    search_image_candidates(state, config)
    verify_slide_images(state, config)
    candidates = [
        item
        for item in state.get("image_search_candidates") or []
        if item.get("candidates")
    ]
    if candidates and getattr(verifier, "_vision_available", None) is False:
        raise RuntimeError(
            "Qwen-VL image verification is unavailable. Set "
            "GRPO_IMAGE_VLM_BASE_URL and GRPO_IMAGE_VLM_MODEL to a live vision endpoint."
        )
    refine_slide_plans(state, config)
    materialized = _materialize_assignments(
        list(state.get("approved_image_assignments") or []),
        asset_dir,
    )
    plans = state.get("slide_plans") or []
    refinements = state.get("slide_refinements") or []
    rows = []
    for index, (source, chunk) in enumerate(
        zip(source_rows, state["slide_chunks"])
    ):
        plan = dict(plans[index]) if index < len(plans) else {}
        refinement = (
            dict(refinements[index])
            if index < len(refinements) and isinstance(refinements[index], dict)
            else {}
        )
        final_content = str(
            refinement.get("final_content")
            or plan.get("final_content")
            or chunk.get("content")
            or ""
        ).strip()
        topic = str(
            plan.get("slide_topic")
            or chunk.get("heading")
            or final_content.splitlines()[0][:160]
        ).strip()
        design = str(
            refinement.get("visual_layout_request")
            or plan.get("visual_layout_request")
            or plan.get("thought")
            or ""
        ).strip()
        retrieval_query = str(refinement.get("retrieval_query") or "").strip()
        approved = materialized.get(index, [])
        plan_record = {
            "action": str(plan.get("action") or "CONTENT_TOOLS"),
            "slide_topic": topic,
            "slide_purpose": str(plan.get("slide_purpose") or "").strip(),
            "retrieval_query": retrieval_query,
            "visual_layout_request": design,
            "image_mode": "semantic" if approved else "none",
            "approved_image_ids": [image["source_id"] for image in approved],
            "image_search_intents": [],
        }
        rows.append(
            {
                "corpus_version": 2,
                "doc_id": source["doc_id"],
                "slide_index": int(source.get("slide_index", index)),
                "category": plan_record["action"],
                "slide_content": final_content,
                "source_slide_content": str(source.get("slide_content") or ""),
                "design_instruction": design,
                "style_context": json.dumps(
                    state.get("deck_style_plan") or {},
                    ensure_ascii=False,
                ),
                "plan": plan_record,
                "approved_images": approved,
            }
        )
    return rows


def rebuild_corpus(
    source_path: Path,
    output_path: Path,
    asset_dir: Path,
    *,
    max_docs: int | None = None,
    max_slides: int | None = None,
    resume: bool = True,
    allow_external_search: bool = False,
) -> list[dict]:
    source_rows = _load_rows(source_path)
    documents = _group_documents(source_rows)
    if max_docs is not None:
        if max_docs < 1:
            raise ValueError("--max-docs must be positive")
        documents = documents[:max_docs]
    if max_slides is not None:
        if max_slides < 1:
            raise ValueError("--max-slides must be positive")
        remaining = max_slides
        limited = []
        for document in documents:
            if remaining <= 0:
                break
            selected = document[:remaining]
            limited.append(selected)
            remaining -= len(selected)
        documents = limited

    manifest_path = output_path.with_suffix(output_path.suffix + ".manifest.json")
    if output_path.exists() and not manifest_path.exists() and resume:
        raise FileExistsError(
            f"Output exists without a resume manifest: {output_path}. "
            "Choose a new --output path."
        )
    manifest = _read_json(
        manifest_path,
        {"version": 1, "completed_docs": [], "source": str(source_path.resolve())},
    )
    if not resume:
        manifest = {
            "version": 1,
            "completed_docs": [],
            "source": str(source_path.resolve()),
        }
    if manifest.get("version") != 1:
        raise ValueError(f"Unsupported rebuild manifest version: {manifest_path}")
    completed = (
        set(str(value) for value in manifest.get("completed_docs", []))
        if resume
        else set()
    )
    output_rows = _read_json(output_path, []) if resume else []
    if not isinstance(output_rows, list):
        raise ValueError(f"Rebuilt corpus must be a JSON list: {output_path}")
    output_rows = [
        row for row in output_rows
        if str(row.get("doc_id")) in completed
    ]
    config, verifier = _build_pipeline_config(allow_external_search)
    try:
        for document in documents:
            doc_id = document[0]["doc_id"]
            key = str(doc_id)
            if key in completed:
                continue
            print(f"Rebuilding document {doc_id} ({len(document)} slides)")
            rebuilt = _rebuild_document(document, config, verifier, asset_dir)
            output_rows.extend(rebuilt)
            completed.add(key)
            manifest.update(
                {
                    "version": 1,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "source": str(source_path.resolve()),
                    "output": str(output_path.resolve()),
                    "asset_dir": str(asset_dir.resolve()),
                    "completed_docs": sorted(completed),
                    "completed_slides": len(output_rows),
                    "approved_image_slots": sum(
                        len(row.get("approved_images") or [])
                        for row in output_rows
                    ),
                    "external_search_enabled": allow_external_search,
                }
            )
            _write_json_atomic(output_path, output_rows)
            _write_json_atomic(manifest_path, manifest)
            print(
                f"Saved {len(rebuilt)} slides; "
                f"approved images={sum(bool(row['approved_images']) for row in rebuilt)}"
            )
    finally:
        del verifier
    print(
        f"Rebuilt {len(output_rows)} slides across {len(completed)} documents "
        f"into {output_path}"
    )
    return output_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument(
        "--asset-dir",
        type=Path,
        default=DEFAULT_ASSET_DIR,
        help="Image cache directory under static/output",
    )
    parser.add_argument("--max-docs", type=int, default=None)
    parser.add_argument("--max-slides", type=int, default=None)
    parser.add_argument(
        "--allow-external-search",
        action="store_true",
        help="Send queries derived from slide text to DuckDuckGo image search",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Start from empty state; output must not already exist",
    )
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    output = args.output.expanduser().resolve()
    asset_dir = args.asset_dir.expanduser().resolve()
    asset_dir.relative_to(OUTPUT_DIR.resolve())
    if args.no_resume and output.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing output: {output}. Choose a new path."
        )
    rebuild_corpus(
        source,
        output,
        asset_dir,
        max_docs=args.max_docs,
        max_slides=args.max_slides,
        resume=not args.no_resume,
        allow_external_search=args.allow_external_search,
    )


if __name__ == "__main__":
    main()
