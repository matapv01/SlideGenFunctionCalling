"""Search, VLM-verify, and persist per-slot images for offline GRPO."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image

from backend.application.services.image_relevance_service import ImageRelevanceService
from backend.application.services.slide_asset_service import slide_asset_service
from backend.config import (
    IMAGE_SEARCH_MAX_RESULTS,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_TOP_P,
    OUTPUT_DIR,
    VLM_API_KEY,
    VLM_BASE_URL,
    VLM_MODEL,
    VLM_REQUEST_MAX_CONCURRENCY,
    VLM_REQUEST_TIMEOUT_SECONDS,
)
from backend.infrastructure.llm.gemini_provider import GeminiLLMProvider
from backend.infrastructure.llm.request_limiter import LLMRequestLimiter
from backend.workflows.slidegen_workflow.tools.ddgs_tool import search_ddgs_images
from rl.image_assets import (
    DEFAULT_IMAGE_CACHE_DIR,
    IMAGE_MANIFEST_NAME,
    extract_image_candidates,
    image_cache_dir,
    image_occurrence_id,
    read_image_manifest,
)
from scripts.generate_challenge_dataset import DEFAULT_DATASET_PATH, _load_rows



def _read_previous_manifest(path: Path) -> dict:
    if not path.is_file():
        return {"version": 2, "assignments": {}, "failures": {}}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Unsupported GRPO image manifest: {path}")
    if payload.get("version") == 1:
        # Version 1 only checked bytes, not semantic relevance. Never promote
        # those records into GRPO automatically.
        return {"version": 2, "assignments": {}, "failures": {}}
    if payload.get("version") != 2:
        raise ValueError(f"Unsupported GRPO image manifest: {path}")
    payload.setdefault("assignments", {})
    payload.setdefault("failures", {})
    return payload


def _build_verifier() -> ImageRelevanceService:
    limiter = LLMRequestLimiter(
        max(1, int(VLM_REQUEST_MAX_CONCURRENCY))
    )
    provider = GeminiLLMProvider(
        api_keys=[VLM_API_KEY] if VLM_API_KEY else [],
        model=VLM_MODEL,
        base_url=VLM_BASE_URL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        top_p=LLM_TOP_P,
        request_limiter=limiter,
        request_timeout=VLM_REQUEST_TIMEOUT_SECONDS,
    )
    return ImageRelevanceService(provider, model=VLM_MODEL)


def _search_query(row: dict, candidate: dict[str, str]) -> str:
    nearby = str(candidate.get("context_hint") or "").strip()
    content = " ".join(str(row.get("slide_content") or "").split())
    lead = content.split(".", 1)[0][:300]
    query = f"{nearby} {lead}" if nearby else lead
    role = str(candidate.get("role") or "illustration")
    if role == "portrait" and "portrait" not in query.lower():
        query = f"{query} portrait photo"
    return " ".join(query.split())[:240]


def _discover_urls(original_url: str, query: str) -> list[str]:
    urls = [original_url]
    raw = search_ddgs_images(
        query=query, size="Large", max_results=IMAGE_SEARCH_MAX_RESULTS
    )
    try:
        discovered = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError, json.JSONDecodeError):
        discovered = []
    for value in discovered if isinstance(discovered, list) else []:
        url = str(value or "").strip()
        if url and url not in urls:
            urls.append(url)
    return urls


def cache_corpus_images(
    dataset_path: Path,
    cache_dir: Path,
    *,
    max_assets: int | None = None,
    allow_external_search: bool = False,
) -> dict:
    cache_dir = cache_dir.expanduser().resolve()
    cache_dir.relative_to(OUTPUT_DIR.resolve())
    cache_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = cache_dir / IMAGE_MANIFEST_NAME
    manifest = _read_previous_manifest(manifest_path)
    usable_assignments = read_image_manifest(cache_dir)
    rows = _load_rows(dataset_path)
    occurrences = []
    for row in rows:
        tool_call = row.get("tool_call")
        arguments = tool_call.get("arguments", {}) if isinstance(tool_call, dict) else {}
        for candidate in extract_image_candidates(arguments):
            occurrences.append(
                (image_occurrence_id(row, candidate), row, candidate)
            )

    assignments = manifest["assignments"]
    failures = manifest["failures"]
    valid_occurrence_ids = {item[0] for item in occurrences}
    for records in (assignments, failures):
        for occurrence_id in list(records):
            if occurrence_id not in valid_occurrence_ids:
                records.pop(occurrence_id, None)
    if max_assets is not None:
        if max_assets < 1:
            raise ValueError("--max-assets must be positive")
        occurrences = occurrences[:max_assets]

    verifier = _build_verifier()

    assignments = manifest["assignments"]
    failures = manifest["failures"]
    for index, (occurrence_id, row, candidate) in enumerate(
        occurrences, start=1
    ):
        existing = assignments.get(occurrence_id)
        if existing and occurrence_id in usable_assignments:
            failures.pop(occurrence_id, None)
            continue
        original_url = candidate["source_url"]
        query = _search_query(row, candidate)
        try:
            candidate_urls = [original_url]
            if allow_external_search:
                candidate_urls = _discover_urls(original_url, query)
            verification = verifier.verify_search_candidates(
                candidates=candidate_urls,
                query=query,
                slide_content=str(row.get("slide_content") or ""),
                target_description=(
                    f"{candidate.get('role', 'illustration')} for "
                    f"{candidate.get('placement_hint', 'image slot')}"
                ),
                presentation_instruction="",
                slide_topic=str(candidate.get("context_hint") or query),
                slide_purpose=str(row.get("design_instruction") or ""),
                rendered_slide_content=str(row.get("slide_content") or ""),
            )
            if not verification.get("available"):
                if getattr(verifier, "_vision_available", None) is False:
                    raise RuntimeError(
                        f"Qwen-VL verifier is unavailable at {VLM_BASE_URL}; "
                        "no image was approved"
                    )
                raise ValueError("no candidate image could be loaded and verified")
            approved = list(verification.get("approved") or [])
            if not approved:
                raise ValueError("all candidate images were rejected by Qwen-VL")
            selected_url = str(approved[0])
            decisions = {
                str(item.get("url")): item
                for item in verification.get("decisions") or []
                if isinstance(item, dict)
            }
            decision = decisions.get(selected_url, {})
            source_path = slide_asset_service.materialize(selected_url, cache_dir)
            relative = source_path.removeprefix("/static/output/")
            local_path = (OUTPUT_DIR / relative).resolve()
            if not local_path.is_file():
                raise FileNotFoundError(f"Cached image was not written: {local_path}")
            width = height = None
            image_format = local_path.suffix.lower().lstrip(".")
            if image_format != "svg":
                with Image.open(local_path) as image:
                    image.verify()
                    width, height = image.size
                    image_format = str(image.format or image_format).lower()
            assignments[occurrence_id] = {
                "source_id": occurrence_id,
                "doc_id": row.get("doc_id"),
                "slide_index": row.get("slide_index"),
                "placement_hint": candidate.get("placement_hint"),
                "role": candidate.get("role"),
                "original_source_url": original_url,
                "selected_source_url": selected_url,
                "search_query": query,
                "verification_reason": str(decision.get("reason") or "")[:500],
                "confidence": float(decision.get("confidence") or 0.0),
                "source_path": source_path,
                "local_path": str(local_path),
                "relative_path": local_path.relative_to(OUTPUT_DIR.resolve()).as_posix(),
                "sha256": hashlib.sha256(local_path.read_bytes()).hexdigest(),
                "width": width,
                "height": height,
                "format": image_format,
                "byte_size": local_path.stat().st_size,
            }
            failures.pop(occurrence_id, None)
            print(
                f"[{index}/{len(occurrences)}] VLM-approved {occurrence_id} "
                f"confidence={float(decision.get('confidence') or 0.0):.2f}"
            )
        except Exception as exc:
            assignments.pop(occurrence_id, None)
            failures[occurrence_id] = {
                "error": f"{type(exc).__name__}: {exc}",
                "original_source_url": original_url,
                "search_query": query,
            }
            print(
                f"[{index}/{len(occurrences)}] rejected {occurrence_id}: {exc}"
            )

    manifest.update(
        {
            "version": 2,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "dataset": str(dataset_path.resolve()),
            "cache_dir": str(cache_dir),
            "external_search_enabled": allow_external_search,
            "assignments": assignments,
            "failures": failures,
        }
    )
    temporary_path = manifest_path.with_suffix(".json.tmp")
    with temporary_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
    temporary_path.replace(manifest_path)
    print(
        f"Cached {len(assignments)} VLM-approved image slots; "
        f"{len(failures)} slots rejected. "
        f"Manifest: {manifest_path}"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Legacy offline corpus JSON path",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help=(
            "Persistent cache directory under static/output; defaults to "
            f"{DEFAULT_IMAGE_CACHE_DIR}"
        ),
    )
    parser.add_argument(
        "--max-assets",
        type=int,
        default=None,
        help="Process only the first N image slots (useful for a smoke check)",
    )
    parser.add_argument(
        "--allow-external-search",
        action="store_true",
        help="Send derived slide queries to DuckDuckGo to replace dead legacy URLs",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero if any selected image slot was not VLM-approved",
    )
    args = parser.parse_args()
    cache_dir = args.cache_dir.resolve() if args.cache_dir else image_cache_dir()
    manifest = cache_corpus_images(
        args.dataset,
        cache_dir,
        max_assets=args.max_assets,
        allow_external_search=args.allow_external_search,
    )
    if args.strict and manifest["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
