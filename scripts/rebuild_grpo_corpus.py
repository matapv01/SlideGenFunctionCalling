"""Rebuild the GRPO corpus from slide text through the production planning pipeline."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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
    LLM_REQUEST_MAX_CONCURRENCY,
    VLM_API_KEY,
    VLM_BASE_URL,
    VLM_MODEL,
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
MANIFEST_VERSION = 3


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


def _document_key(doc_id: Any) -> str:
    return json.dumps(
        [type(doc_id).__name__, doc_id],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _resume_signature(source_path: Path, asset_dir: Path, allow_external_search: bool) -> dict:
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    pipeline_settings = {
        "planner_model": LLM_MODEL,
        "planner_base_url": LLM_BASE_URL,
        "vision_model": VLM_MODEL,
        "vision_base_url": VLM_BASE_URL,
        "allow_external_search": bool(allow_external_search),
    }
    pipeline_hash = hashlib.sha256(
        json.dumps(pipeline_settings, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return {
        "source_path": str(source_path.resolve()),
        "source_sha256": source_hash,
        "asset_dir": str(asset_dir.resolve()),
        "pipeline_sha256": pipeline_hash,
    }


def _build_pipeline_config(
    allow_external_search: bool,
) -> tuple[dict, ImageRelevanceService]:
    planner_limiter = LLMRequestLimiter(
        max(1, int(LLM_REQUEST_MAX_CONCURRENCY))
    )
    planner_provider = GeminiLLMProvider(
        api_keys=[LLM_API_KEY] if LLM_API_KEY else [],
        model=LLM_MODEL,
        base_url=LLM_BASE_URL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        top_p=LLM_TOP_P,
        request_limiter=planner_limiter,
        request_timeout=LLM_REQUEST_TIMEOUT_SECONDS,
    )
    # Match BE: planner and vision share the same endpoint capacity.
    vision_limiter = planner_limiter
    vision_provider = GeminiLLMProvider(
        api_keys=[VLM_API_KEY] if VLM_API_KEY else [],
        model=VLM_MODEL,
        base_url=VLM_BASE_URL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        top_p=LLM_TOP_P,
        request_limiter=vision_limiter,
        request_timeout=VLM_REQUEST_TIMEOUT_SECONDS,
    )
    verifier = ImageRelevanceService(
        vision_provider,
        model=VLM_MODEL,
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
            if not isinstance(item, dict):
                raise ValueError("assignment is not an object")
            slide_index = int(item.get("slide_index", -1))
            source_url = str(item.get("source_url") or "").strip()
            confidence = float(item.get("confidence") or 0.0)
            if (
                slide_index < 0
                or not source_url
                or not math.isfinite(confidence)
                or confidence < 0.5
            ):
                raise ValueError("approved assignment has invalid metadata")
            source_path = slide_asset_service.materialize(source_url, asset_dir)
            if not source_path.startswith("/static/output/"):
                raise ValueError("materialized image is outside static/output")
            local_path = (
                OUTPUT_DIR / source_path.removeprefix("/static/output/")
            ).resolve()
            local_path.relative_to(OUTPUT_DIR.resolve())
            if not local_path.is_file():
                raise FileNotFoundError(local_path)
        except Exception as exc:
            source_id = item.get("source_id", "?") if isinstance(item, dict) else "?"
            raise RuntimeError(
                f"Could not materialize VLM-approved image {source_id!r}; "
                "refusing to downgrade the slide to no-image"
            ) from exc
        record = {
            "source_id": str(item.get("source_id") or ""),
            "source_type": "vlm_verified_search",
            "slide_index": slide_index,
            "source_url": source_url,
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

    configurable = config.get("configurable", {})
    strict = bool(configurable.get("strict_grpo_preprocessing"))
    planned_image_intents = any(
        isinstance(plan, dict) and plan.get("image_search_intents")
        for plan in state.get("slide_plans") or []
    )
    if strict and planned_image_intents and verifier is None:
        raise RuntimeError("Strict GRPO preprocessing requires image search and verification services")
    search_image_candidates(state, config)
    search_groups = list(state.get("image_search_candidates") or [])
    if strict:
        failed_searches = [
            item for item in search_groups if item.get("status") == "search_failed"
        ]
        if failed_searches:
            first = failed_searches[0]
            raise RuntimeError(
                "Image search failed during strict GRPO preprocessing "
                f"(slide={first.get('slide_index')}, query={first.get('query')!r}): "
                f"{first.get('error', 'unknown error')}"
            )
        # Empty results are a normal no-image decision. Transport/search errors
        # remain fatal above so an outage cannot masquerade as image rejection.
    verify_slide_images(state, config)
    materialized = _materialize_assignments(
        list(state.get("approved_image_assignments") or []),
        asset_dir,
    )
    # Phase two must only describe assets that were successfully cached and
    # will actually be available to the H100 training process.
    state["approved_image_assignments"] = [
        item for items in materialized.values() for item in items
    ]
    refine_slide_plans(state, config)
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
    allow_external_search: bool = True,
) -> list[dict]:
    source_rows = _load_rows(source_path)
    all_documents = _group_documents(source_rows)
    expected_by_key = {
        _document_key(document[0]["doc_id"]): document
        for document in all_documents
    }
    documents = all_documents
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
    if not resume:
        if output_path.exists() or manifest_path.exists():
            raise FileExistsError(
                "Refusing to overwrite an existing corpus or manifest; choose a new output path."
            )
        manifest = {"version": MANIFEST_VERSION, "completed_docs": []}
    else:
        manifest = _read_json(
            manifest_path,
            {"version": MANIFEST_VERSION, "completed_docs": []},
        )
    if not isinstance(manifest, dict):
        raise ValueError(f"Invalid rebuild manifest: {manifest_path}")
    if manifest.get("version") != MANIFEST_VERSION:
        raise ValueError(f"Unsupported rebuild manifest version: {manifest_path}")

    signature = _resume_signature(source_path, asset_dir, allow_external_search)
    if manifest.get("signature") not in (None, signature):
        raise ValueError(
            "Resume inputs differ from the existing corpus build (source, image "
            "cache path, search setting, or planner/VLM endpoint). Choose a new "
            "output path to rebuild from scratch."
        )
    if manifest.get("signature") is None and manifest.get("completed_docs"):
        raise ValueError(
            "Existing manifest has no input signature; choose a new output path "
            "to avoid mixing corpora."
        )
    manifest["signature"] = signature
    raw_completed = manifest.get("completed_docs", []) if resume else []
    if not isinstance(raw_completed, list) or any(not isinstance(key, str) for key in raw_completed):
        raise ValueError(f"Invalid completed_docs in manifest: {manifest_path}")
    completed = set(raw_completed)
    if resume and manifest_path.exists() and not output_path.is_file():
        raise FileNotFoundError(
            f"Resume manifest exists but corpus output is missing: {output_path}. "
            "Restore the output or choose a new path."
        )
    output_rows = _read_json(output_path, []) if resume else []
    if not isinstance(output_rows, list) or any(not isinstance(row, dict) for row in output_rows):
        raise ValueError(f"Rebuilt corpus must be a JSON list: {output_path}")
    output_rows = [
        row for row in output_rows
        if _document_key(row.get("doc_id")) in completed
    ]
    rows_by_doc: dict[str, list[dict]] = {}
    for row in output_rows:
        rows_by_doc.setdefault(_document_key(row.get("doc_id")), []).append(row)
    for key in completed:
        source_document = expected_by_key.get(key)
        if source_document is None:
            raise ValueError("Completed document is missing from the current source corpus")
        expected_indices = {
            int(row.get("slide_index", index))
            for index, row in enumerate(source_document)
        }
        complete_rows = rows_by_doc.get(key, [])
        actual_indices = {
            int(row["slide_index"])
            for row in complete_rows
            if "slide_index" in row
        }
        if actual_indices != expected_indices or len(complete_rows) != len(expected_indices):
            raise ValueError(
                f"Manifest marks document {source_document[0]['doc_id']!r} complete "
                "but its output rows are incomplete or duplicated."
            )

    config, verifier = _build_pipeline_config(allow_external_search)
    try:
        for document in documents:
            doc_id = document[0]["doc_id"]
            key = _document_key(doc_id)
            if key in completed:
                continue
            print(f"Rebuilding document {doc_id} ({len(document)} slides)")
            rebuilt = _rebuild_document(document, config, verifier, asset_dir)
            if len(rebuilt) != len(document):
                raise RuntimeError(
                    f"Rebuilder returned {len(rebuilt)} of {len(document)} slides "
                    f"for document {doc_id!r}"
                )
            output_rows.extend(rebuilt)
            if len(document) == len(expected_by_key[key]):
                completed.add(key)
            manifest.update(
                {
                    "version": MANIFEST_VERSION,
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
                    "signature": signature,
                }
            )
            _write_json_atomic(output_path, output_rows)
            _write_json_atomic(manifest_path, manifest)
            print(
                f"Saved {len(rebuilt)} slides; approved images={sum(bool(row['approved_images']) for row in rebuilt)}"
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
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Search DuckDuckGo for slide images (enabled by default)",
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
