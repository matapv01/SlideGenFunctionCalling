"""Qwen-VL based image relevance checks shared by search and DOCX assets."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import logging
import math
import mimetypes
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from PIL import Image

from backend.config import (
    VLM_DOCUMENT_IMAGE_BATCH_SIZE,
    VLM_MAX_IMAGE_BYTES,
    VLM_MAX_IMAGE_EDGE,
    VLM_MAX_SEARCH_CANDIDATES,
    VLM_REQUEST_MAX_CONCURRENCY,
)
from backend.domain.ports.llm_provider import LLMProvider
from backend.application.services.slide_asset_service import slide_asset_service

logger = logging.getLogger(__name__)

_VISION_RETRY_SECONDS = 60.0
_DECISION_CACHE_TTL_SECONDS = 30 * 60
_DECISION_CACHE_MAX_ITEMS = 256


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


class ImageRelevanceService:
    """Ask a vision-capable configured model whether images support content.

    The service is intentionally domain-neutral.  It does not contain topic
    rules or keyword lists: Qwen receives the actual slide/document context and
    returns a small structured decision.  If the configured endpoint is
    text-only or unavailable, callers receive ``available=False`` and can
    switch the current slide to a no-image layout without inventing an image.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        *,
        model: str | None = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.model = model or None
        self._cache: OrderedDict[str, tuple[float, dict[str, Any]]] = OrderedDict()
        self._cache_lock = threading.Lock()
        self._request_semaphore = threading.BoundedSemaphore(
            max(1, int(VLM_REQUEST_MAX_CONCURRENCY))
        )
        self._vision_available: bool | None = None
        self._vision_retry_at = 0.0

    def verify_search_candidates(
        self,
        *,
        candidates: list[str],
        query: str,
        slide_content: str,
        target_description: str,
        presentation_instruction: str = "",
        slide_topic: str = "",
        slide_purpose: str = "",
        deck_topic: str = "",
        deck_outline: str = "",
        rendered_slide_content: str = "",
    ) -> dict[str, Any]:
        """Return approved search URLs in relevance order.

        One multimodal request compares several candidates, which is much
        cheaper than issuing one Qwen call per URL and lets the model reject
        broadly related but factually wrong images.
        """
        urls = [
            str(url).strip()
            for url in candidates
            if isinstance(url, str) and str(url).strip()
        ][: VLM_MAX_SEARCH_CANDIDATES]
        if not urls:
            return {"available": False, "approved": [], "decisions": []}
        # Do not download and normalize every candidate after a recent vision
        # failure. The executor will immediately retry the slide without an
        # image, so another multimodal probe would only add latency.
        if (
            self._vision_available is False
            and time.monotonic() < self._vision_retry_at
        ):
            return {"available": False, "approved": [], "decisions": []}

        parts: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": (
                    "Compare the following image-search candidates with the full "
                    "semantic requirement of the slide. First understand the deck "
                    "subject and the slide's purpose, then inspect the candidate "
                    "image. Reject an image when it is only broadly related, "
                    "depicts a different entity, event, place, or time period, or "
                    "cannot support the requested visual role. Do not reward "
                    "aesthetic quality alone. A title-only or intro slide must be "
                    "judged from the deck topic and slide purpose, not from the "
                    "amount of text on that slide. The rendered slide arguments "
                    "are the most concrete representation of what will be shown. "
                    "For factual or document-grounded slides, reject generic stock "
                    "photos, generic icons, and broad concept art when the slide "
                    "names a specific person, institution, place, event, product, "
                    "document, or period. Approve a generic illustration only when "
                    "the slide purpose is explicitly conceptual and the visual role "
                    "is illustrative rather than evidentiary. "
                    "Return JSON only in the form "
                    '{"candidates":[{"index":0,"use":true,"confidence":0.0,'
                    '"reason":"...","caption_hint":"...",'
                    '"placement_hint":"..."}]}.'
                    " Candidate indexes are zero-based. Return exactly one decision "
                    "for EVERY supplied candidate, including rejected images. "
                    "Keep reasons and hints concise.\n\n"
                    f"Deck topic: {str(deck_topic or '')[:800]}\n"
                    f"Deck outline: {str(deck_outline or '')[:2200]}\n"
                    f"Slide topic: {str(slide_topic or '')[:500]}\n"
                    f"Slide purpose: {str(slide_purpose or '')[:900]}\n"
                    f"Search query: {query}\n"
                    f"Image slot role: {target_description}\n"
                    f"Source slide content:\n{str(slide_content or '')[:2600]}\n"
                    f"Rendered slide content:\n{str(rendered_slide_content or '')[:3200]}\n"
                    f"Deck-level visual instruction:\n{str(presentation_instruction or '')[:1200]}\n"
                ),
            }
        ]
        loaded: list[tuple[int, str, str]] = []
        for index, url in enumerate(urls):
            data_uri = self._to_data_uri(url)
            if not data_uri:
                continue
            parts.append(
                {
                    "type": "text",
                    "text": f"Candidate {index}: {url[:500]}",
                }
            )
            parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": data_uri},
                }
            )
            loaded.append((index, url, data_uri))

        if not loaded:
            logger.warning(
                "VLM image review had no downloadable candidates (requested=%d)",
                len(urls),
            )
            return {"available": False, "approved": [], "decisions": []}

        cache_key = self._cache_key(
            "search",
            [self._source_hash(data_uri) for _, _, data_uri in loaded],
            query,
            slide_content,
            target_description,
            slide_topic,
            slide_purpose,
            deck_topic,
            deck_outline,
            rendered_slide_content,
        )
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        logger.info(
            "VLM search verification: images=%d payload_kb=%.1f",
            len(loaded),
            sum(len(data_uri) for _, _, data_uri in loaded) / 1024,
        )
        raw = self._invoke(parts, max_tokens=max(700, 400 * len(loaded)))
        if raw is None:
            logger.warning("VLM returned no response for image candidate review")
            return {"available": False, "approved": [], "decisions": []}
        parsed = self._parse_json(raw)
        decisions = parsed.get("candidates") if isinstance(parsed, dict) else None
        if not isinstance(decisions, list):
            logger.warning(
                "VLM image review did not return a parseable candidates array (response_chars=%d)",
                len(raw),
            )
            return {"available": False, "approved": [], "decisions": []}

        normalized: list[dict[str, Any]] = []
        by_index = {index: url for index, url, _ in loaded}
        seen_indices: set[int] = set()
        invalid_indices: set[int] = set()
        for item in decisions:
            if not isinstance(item, dict):
                continue
            raw_index = item.get("index")
            if isinstance(raw_index, bool):
                continue
            if isinstance(raw_index, int):
                index = raw_index
            elif isinstance(raw_index, str) and raw_index.strip().lstrip("-").isdigit():
                index = int(raw_index)
            else:
                continue
            if index not in by_index:
                continue
            if index in seen_indices:
                invalid_indices.add(index)
                continue
            seen_indices.add(index)
            raw_use = item.get("use")
            if isinstance(raw_use, bool):
                use = raw_use
            elif str(raw_use or "").strip().lower() in {"1", "true", "yes", "y"}:
                use = True
            elif str(raw_use or "").strip().lower() in {"0", "false", "no", "n"}:
                use = False
            else:
                invalid_indices.add(index)
                continue
            raw_confidence = item.get("confidence")
            if isinstance(raw_confidence, bool):
                invalid_indices.add(index)
                continue
            try:
                confidence = float(raw_confidence)
            except (TypeError, ValueError):
                invalid_indices.add(index)
                continue
            if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
                invalid_indices.add(index)
                continue
            normalized.append(
                {
                    "index": index,
                    "url": by_index[index],
                    "use": use,
                    "confidence": confidence,
                    "reason": str(item.get("reason") or "")[:500],
                    "caption_hint": str(item.get("caption_hint") or "")[:300],
                    "placement_hint": str(item.get("placement_hint") or "")[:300],
                }
            )
        if invalid_indices:
            normalized = [
                item for item in normalized if item["index"] not in invalid_indices
            ]
            seen_indices.difference_update(invalid_indices)
        missing_indices = set(by_index).difference(seen_indices)
        if missing_indices:
            logger.warning(
                "VLM omitted %d/%d image decisions; omitted candidates are rejected",
                len(missing_indices),
                len(by_index),
            )
            normalized.extend(
                {
                    "index": index,
                    "url": by_index[index],
                    "use": False,
                    "confidence": 0.0,
                    "reason": "VLM omitted a decision; rejected by default",
                    "caption_hint": "",
                    "placement_hint": "",
                }
                for index in sorted(missing_indices)
            )
        approved = [
            item["url"]
            for item in sorted(normalized, key=lambda item: item["confidence"], reverse=True)
            if item["use"] and item["confidence"] >= 0.5
        ]
        result = {
            "available": True,
            "approved": approved,
            "decisions": normalized,
        }
        self._set_cache(cache_key, result)
        return result

    def assign_document_images(
        self,
        *,
        images: list[dict[str, Any]],
        slide_chunks: list[dict[str, Any]],
        user_request: str,
        model: str | None = None,
        slide_plans: list[dict[str, Any]] | None = None,
        deck_topic: str = "",
        deck_outline: str = "",
        presentation_instruction: str = "",
    ) -> list[dict[str, Any]]:
        """Assign every usable DOCX image to its best supporting slide.

        The complete deck plan is supplied to every small image batch. This
        keeps the vision request bounded without silently dropping images from
        larger documents.
        """
        usable_images = [
            image for image in images or []
            if isinstance(image, dict) and str(image.get("source_path") or "").strip()
        ]
        if not usable_images or not slide_chunks:
            return []

        slide_lines: list[str] = []
        for index, chunk in enumerate(slide_chunks):
            data = chunk if isinstance(chunk, dict) else {}
            plan = (
                slide_plans[index]
                if slide_plans
                and index < len(slide_plans)
                and isinstance(slide_plans[index], dict)
                else {}
            )
            title = str(data.get("title") or data.get("heading") or "").strip()
            content = str(data.get("content") or "").strip()
            slide_lines.append(
                f"Slide {index} | title: {title[:220]} | "
                f"topic: {str(plan.get('slide_topic') or '')[:260]} | "
                f"purpose: {str(plan.get('slide_purpose') or '')[:420]} | "
                f"action: {str(plan.get('action') or '')[:80]} | "
                f"content: {content[:900]}"
            )
        batch_jobs = [
            usable_images[offset : offset + VLM_DOCUMENT_IMAGE_BATCH_SIZE]
            for offset in range(0, len(usable_images), VLM_DOCUMENT_IMAGE_BATCH_SIZE)
        ]

        def verify_batch(batch_images: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return self._verify_document_image_batch(
                batch_images,
                slide_lines=slide_lines,
                slide_count=len(slide_chunks),
                user_request=user_request,
                deck_topic=deck_topic,
                deck_outline=deck_outline,
                presentation_instruction=presentation_instruction,
                model=model,
            )

        assignments: list[dict[str, Any]] = []
        with ThreadPoolExecutor(
            max_workers=min(
                max(1, int(VLM_REQUEST_MAX_CONCURRENCY)),
                len(batch_jobs),
            )
        ) as executor:
            # executor.map preserves the original image-batch order while the
            # requests themselves run concurrently.
            for batch_assignments in executor.map(verify_batch, batch_jobs):
                assignments.extend(batch_assignments)

        return [dict(item) for item in assignments]

    def _invoke(
        self,
        content: list[dict[str, Any]],
        *,
        model: str | None = None,
        max_tokens: int,
    ) -> str | None:
        started = time.perf_counter()
        if (
            self._vision_available is False
            and time.monotonic() < self._vision_retry_at
        ):
            return None
        try:
            request = [
                {
                    "role": "system",
                    "content": (
                        "You are a precise multimodal image relevance "
                        "reviewer. Inspect the supplied images and return "
                        "only the requested JSON object. Do not invent "
                        "visual details that are not visible."
                    ),
                },
                {"role": "user", "content": content},
            ]

            def invoke() -> str:
                return str(
                    self.llm_provider.generate_completion(
                        request,
                        model=model or self.model,
                        max_tokens=max_tokens,
                        temperature=0.1,
                        top_p=0.9,
                    )
                )

            # Production providers already own the shared endpoint limiter.
            # The local fallback semaphore keeps lightweight/fake providers
            # bounded without acquiring the same semaphore twice.
            if getattr(self.llm_provider, "request_limiter", None) is None:
                with self._request_semaphore:
                    result = invoke()
            else:
                result = invoke()
            result = result.strip()
            self._vision_available = True
            self._vision_retry_at = 0.0
            logger.info(
                "VLM request completed in %.2fs (payload_parts=%d)",
                time.perf_counter() - started,
                len(content),
            )
            return result
        except Exception as exc:
            self._vision_available = False
            self._vision_retry_at = time.monotonic() + _VISION_RETRY_SECONDS
            logger.warning(
                "Multimodal image verification unavailable after %.2fs: %s",
                time.perf_counter() - started,
                exc,
            )
            return None

    @staticmethod
    def _parse_json(raw: str) -> dict[str, Any] | None:
        text = str(raw or "").strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(lines[1:-1] if len(lines) > 2 else lines).strip()
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            start, end = text.find("{"), text.rfind("}")
            if start < 0 or end <= start:
                return None
            try:
                parsed = json.loads(text[start : end + 1])
                return parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                return None

    @staticmethod
    def _cache_key(kind: str, sources: list[str], *contexts: str) -> str:
        raw = "\n".join([kind, *sources, *[str(context or "") for context in contexts]])
        return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest()

    def _get_cache(self, key: str) -> dict[str, Any] | None:
        now = time.monotonic()
        with self._cache_lock:
            cached = self._cache.pop(key, None)
            if cached is None:
                return None
            created_at, value = cached
            if now - created_at >= _DECISION_CACHE_TTL_SECONDS:
                return None
            self._cache[key] = (created_at, value)
            return dict(value)

    def _set_cache(self, key: str, value: dict[str, Any]) -> None:
        with self._cache_lock:
            # Keep this process-local cache bounded; image bytes themselves are
            # not stored, only the structured decision and provenance.
            self._cache.pop(key, None)
            self._cache[key] = (time.monotonic(), dict(value))
            while len(self._cache) > _DECISION_CACHE_MAX_ITEMS:
                self._cache.popitem(last=False)

    @staticmethod
    def _source_hash(source: str) -> str:
        return hashlib.sha256(str(source).encode("utf-8")).hexdigest()

    def _verify_document_image_batch(
        self,
        batch_images: list[dict[str, Any]],
        *,
        slide_lines: list[str],
        slide_count: int,
        user_request: str,
        deck_topic: str,
        deck_outline: str,
        presentation_instruction: str,
        model: str | None,
    ) -> list[dict[str, Any]]:
        """Verify one independent DOCX-image batch.

        Every batch receives the same deck context, so batches do not depend on
        one another and can safely run concurrently. The caller is responsible
        for restoring their original order.
        """
        batch: list[tuple[str, dict[str, Any], str]] = []
        for image in batch_images:
            image_id = str(image.get("image_id") or image.get("content_hash") or "")
            data_uri = self._to_data_uri(str(image.get("source_path") or ""))
            if image_id and data_uri:
                batch.append((image_id, image, data_uri))
        if not batch:
            return []

        by_id = {image_id: image for image_id, image, _ in batch}
        parts: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": (
                    "Review every embedded document image in this batch. "
                    "For each image, decide whether it materially supports one "
                    "slide in the proposed deck. Use the image itself, its local "
                    "heading context, the complete deck plan, and target slide "
                    "content together. Do not force an image into a slide when it "
                    "is unrelated, redundant, or ambiguous. Each image must appear "
                    "exactly once in the JSON response, with use=false when it "
                    "should not be used. Slide indexes are zero-based. Return JSON "
                    "only as "
                    '{"images":[{"image_id":"...","use":true,'
                    '"slide_index":0,"confidence":0.0,'
                    '"role":"evidence|illustration|chart|diagram|photo",'
                    '"reason":"...","caption_hint":"...",'
                    '"placement_hint":"..."}]}\n\n'
                    f"User presentation request:\n{str(user_request or '')[:1800]}\n\n"
                    f"Deck topic:\n{str(deck_topic or '')[:800]}\n\n"
                    f"Deck outline:\n{str(deck_outline or '')[:2600]}\n\n"
                    f"Presentation instruction:\n{str(presentation_instruction or '')[:1400]}\n\n"
                    f"Candidate slides:\n{chr(10).join(slide_lines)}"
                ),
            }
        ]
        for image_id, image, data_uri in batch:
            parts.append(
                {
                    "type": "text",
                    "text": (
                        f"Embedded image id: {image_id}\n"
                        f"Original filename: {str(image.get('filename') or '')[:200]}\n"
                        f"Heading path: {str(image.get('section_path') or '')[:500]}\n"
                        f"Displayed size: {image.get('width') or '?'}x{image.get('height') or '?'}\n"
                        f"Alt text: {str(image.get('alt_text') or '')[:500]}\n"
                        f"Nearby document text: {str(image.get('nearby_text') or '')[:1200]}"
                    ),
                }
            )
            parts.append({"type": "image_url", "image_url": {"url": data_uri}})

        cache_key = self._cache_key(
            "document",
            [
                f"{image_id}:{self._source_hash(data_uri)}"
                for image_id, _, data_uri in batch
            ],
            user_request,
            deck_topic,
            deck_outline,
            presentation_instruction,
            "\n".join(slide_lines),
        )
        cached = self._get_cache(cache_key)
        if cached is not None:
            return [dict(item) for item in cached.get("assignments", [])]

        logger.info(
            "VLM document verification: images=%d payload_kb=%.1f",
            len(batch),
            sum(len(data_uri) for _, _, data_uri in batch) / 1024,
        )
        raw = self._invoke(parts, model=model, max_tokens=1200)
        if raw is None:
            return []
        parsed = self._parse_json(raw)
        decisions = parsed.get("images") if isinstance(parsed, dict) else None
        if not isinstance(decisions, list):
            return []

        assignments: list[dict[str, Any]] = []
        for item in decisions:
            if not isinstance(item, dict) or not _as_bool(item.get("use")):
                continue
            image_id = str(item.get("image_id") or "").strip()
            if image_id not in by_id:
                continue
            try:
                slide_index = int(item.get("slide_index"))
                confidence = max(0.0, min(1.0, float(item.get("confidence", 0))))
            except (TypeError, ValueError):
                continue
            if slide_index < 0 or slide_index >= slide_count or confidence < 0.5:
                continue
            source = by_id[image_id]
            assignments.append(
                {
                    **source,
                    "slide_index": slide_index,
                    "confidence": confidence,
                    "role": str(item.get("role") or "illustration")[:40],
                    "reason": str(item.get("reason") or "")[:500],
                    "caption_hint": str(item.get("caption_hint") or "")[:300],
                    "placement_hint": str(item.get("placement_hint") or "")[:300],
                }
            )

        self._set_cache(cache_key, {"assignments": assignments})
        return assignments

    @classmethod
    def _to_data_uri(cls, source: str) -> str | None:
        try:
            if source.lower().startswith(("http://", "https://")):
                raw, mime_type = slide_asset_service.read_remote(source, timeout=12)
            else:
                path = Path(source)
                if not path.is_file():
                    return None
                raw = path.read_bytes()
                mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
            if not raw:
                return None
            raw, mime_type = cls._normalize_image(raw, mime_type)
            if source.lower().startswith(("http://", "https://")):
                # The verifier and the later XML executor share this bounded
                # process-local cache, so an approved image is not downloaded
                # a second time before it is materialized into the deck.
                slide_asset_service.remember_remote(source, raw, mime_type)
            return f"data:{mime_type};base64,{base64.b64encode(raw).decode('ascii')}"
        except Exception as exc:
            logger.debug("Cannot prepare image for Qwen-VL: %s", exc)
            return None

    @staticmethod
    def _normalize_image(raw: bytes, mime_type: str) -> tuple[bytes, str]:
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            image.thumbnail((VLM_MAX_IMAGE_EDGE, VLM_MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
            has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
            if has_alpha:
                output = io.BytesIO()
                image.convert("RGBA").save(output, format="PNG", optimize=True)
                normalized, normalized_type = output.getvalue(), "image/png"
            else:
                output = io.BytesIO()
                image.convert("RGB").save(output, format="JPEG", quality=82, optimize=True)
                normalized, normalized_type = output.getvalue(), "image/jpeg"
        if len(normalized) > VLM_MAX_IMAGE_BYTES:
            # Re-encode once more at a smaller quality rather than sending a
            # multi-megabyte image to every Qwen verification request.
            with Image.open(io.BytesIO(normalized)) as image:
                output = io.BytesIO()
                image.convert("RGB").save(output, format="JPEG", quality=65, optimize=True)
                normalized, normalized_type = output.getvalue(), "image/jpeg"
        return normalized, normalized_type
