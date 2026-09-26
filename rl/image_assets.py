"""Offline image-asset cache for GRPO data recovered from legacy tool calls."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from backend.config import OUTPUT_DIR


DEFAULT_IMAGE_CACHE_DIR = OUTPUT_DIR / "grpo_image_cache"
IMAGE_MANIFEST_NAME = "manifest.json"


def image_cache_dir() -> Path:
    """Return the persistent cache under the backend's publicly served output."""
    path = Path(
        os.getenv("GRPO_IMAGE_CACHE_DIR", str(DEFAULT_IMAGE_CACHE_DIR))
    ).expanduser().resolve()
    try:
        path.relative_to(OUTPUT_DIR.resolve())
    except ValueError as exc:
        raise ValueError(
            "GRPO_IMAGE_CACHE_DIR must be inside static/output so the "
            "XML preview can load cached assets."
        ) from exc
    return path


def _is_image_field(name: str) -> bool:
    lowered = str(name or "").lower()
    return (
        "image_url" in lowered
        or "image_path" in lowered
        or lowered in {"bg_image", "background_image"}
    )


def _usable_source(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    source = value.strip()
    if not source:
        return None
    lowered = source.lower()
    if "placeholder" in lowered or lowered.startswith("/path/to/"):
        return None
    parsed = urlsplit(source)
    if parsed.scheme in {"http", "https"} and parsed.hostname:
        return source
    if lowered.startswith("data:image/"):
        return source
    return None


def extract_image_candidates(arguments: Any) -> list[dict[str, str]]:
    """Extract only schema-style image fields, excluding CSS and ordinary URLs."""
    candidates: list[dict[str, str]] = []

    def visit(value: Any, path: list[str | int]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = [*path, str(key)]
                if _is_image_field(str(key)):
                    source = _usable_source(child)
                    if source:
                        # Build a readable field path without depending on
                        # the original model's argument ordering elsewhere.
                        path_text = ""
                        for part in child_path:
                            path_text += (
                                f"[{part}]" if isinstance(part, int)
                                else (f".{part}" if path_text else part)
                            )
                        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
                        lowered_path = path_text.lower()
                        role = (
                            "portrait"
                            if any(token in lowered_path for token in (
                                "team", "member", "profile", "avatar", "portrait"
                            ))
                            else "illustration"
                        )
                        candidates.append(
                            {
                                "source_id": f"legacy-img-{digest[:16]}",
                                "source_url": source,
                                "role": role,
                                "placement_hint": path_text,
                                "context_hint": _image_context_hint(value),
                            }
                        )
                else:
                    visit(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, [*path, index])

    visit(arguments, [])
    return candidates


def _image_context_hint(container: dict[str, Any]) -> str:
    """Return nearby semantic labels for a legacy image slot."""
    preferred = (
        "name", "title", "main_title", "heading", "role", "caption",
        "subtitle", "label",
    )
    parts: list[str] = []
    for key in preferred:
        value = container.get(key)
        if isinstance(value, str) and value.strip() and not _is_image_field(key):
            parts.append(value.strip())
    return " | ".join(parts)[:500]


def image_occurrence_id(row: dict, candidate: dict[str, str]) -> str:
    """Identify one image slot even when a legacy URL is reused elsewhere."""
    identity = "\n".join(
        (
            str(row.get("doc_id", "")),
            str(row.get("slide_index", "")),
            str(candidate.get("placement_hint") or ""),
            str(candidate.get("source_url") or ""),
        )
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return f"legacy-slot-{digest[:20]}"


def read_image_manifest(cache_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load VLM-approved image-slot assignments from the offline manifest."""
    directory = cache_dir or image_cache_dir()
    manifest_path = directory / IMAGE_MANIFEST_NAME
    if not manifest_path.is_file():
        return {}
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or payload.get("version") != 2:
        return {}
    assets = payload.get("assignments", {})
    if not isinstance(assets, dict):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for occurrence_id, record in assets.items():
        if not isinstance(occurrence_id, str) or not isinstance(record, dict):
            continue
        try:
            confidence = float(record.get("confidence") or 0.0)
        except (TypeError, ValueError):
            continue
        if confidence < 0.5 or not str(record.get("selected_source_url") or ""):
            continue
        source_path = str(record.get("source_path") or "").strip()
        relative_path = source_path.removeprefix("/static/output/")
        local_path = (OUTPUT_DIR / relative_path).resolve()
        if not source_path.startswith("/static/output/"):
            continue
        try:
            local_path.relative_to(OUTPUT_DIR.resolve())
        except ValueError:
            continue
        if not local_path.is_file():
            continue
        # Derive the local path from the portable public path. Manifests can
        # therefore be copied from a preparation machine to the H100 host.
        result[occurrence_id] = {**record, "local_path": str(local_path)}
    return result


def approved_images_for_row(
    row: dict,
    image_manifest: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Resolve row-attached legacy candidates to validated cached assets."""
    tool_call = row.get("tool_call")
    arguments = (
        tool_call.get("arguments", {}) if isinstance(tool_call, dict) else {}
    )
    if int(row.get("corpus_version") or 0) >= 2:
        resolved = []
        for asset in row.get("approved_images") or []:
            if not isinstance(asset, dict):
                return []
            source_path = str(asset.get("source_path") or "").strip()
            if not source_path.startswith("/static/output/"):
                return []
            local_path = (
                OUTPUT_DIR / source_path.removeprefix("/static/output/")
            ).resolve()
            try:
                local_path.relative_to(OUTPUT_DIR.resolve())
                confidence = float(asset.get("confidence") or 0.0)
            except (ValueError, TypeError):
                return []
            if (
                not local_path.is_file()
                or confidence < 0.5
                or not asset.get("selected_source_url")
            ):
                return []
            resolved.append(
                {
                    **asset,
                    "source_id": str(asset.get("source_id") or ""),
                    "source_type": "vlm_verified_search",
                    "source_url": asset.get("selected_source_url"),
                    "source_path": source_path,
                    "local_path": str(local_path),
                    "confidence": confidence,
                }
            )
        return resolved

    candidates = extract_image_candidates(arguments)
    resolved = []
    if not candidates:
        return []
    for candidate in candidates:
        occurrence_id = image_occurrence_id(row, candidate)
        asset = image_manifest.get(occurrence_id)
        if not asset:
            # Never train on a partial image set: the remaining images may
            # represent one semantic composition in the legacy tool call.
            return []
        resolved.append(
            {
                "source_id": occurrence_id,
                "source_type": "vlm_verified_legacy_or_search",
                "source_url": asset.get("selected_source_url"),
                "source_path": asset["source_path"],
                "local_path": asset["local_path"],
                "role": candidate["role"],
                "placement_hint": candidate["placement_hint"],
                "visual_notes": (
                    f"VLM-verified cached asset: "
                    f"{asset.get('verification_reason', '')} "
                    f"({asset.get('width', '?')}x{asset.get('height', '?')})."
                ),
                "confidence": asset.get("confidence", 0.0),
            }
        )
    return resolved
