"""Qwen-VL based image relevance checks shared by search and DOCX assets."""

from __future__ import annotations

import base64
import hashlib
import ipaddress
import io
import json
import logging
import mimetypes
import socket
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from PIL import Image

from backend.domain.ports.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

_MAX_REMOTE_BYTES = 8 * 1024 * 1024
_MAX_MODEL_IMAGE_BYTES = 2 * 1024 * 1024
_MAX_IMAGE_EDGE = 1400
_MAX_SEARCH_CANDIDATES = 10
_DOCUMENT_IMAGE_BATCH_SIZE = 4
_VISION_RETRY_SECONDS = 60.0


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
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_lock = threading.Lock()
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
        ][: _MAX_SEARCH_CANDIDATES]
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
                    "Return JSON only in the form "
                    '{"candidates":[{"index":0,"use":true,"confidence":0.0,'
                    '"reason":"...","caption_hint":"...",'
                    '"placement_hint":"..."}]}.'
                    " Candidate indexes are zero-based.\n\n"
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

        raw = self._invoke(parts, max_tokens=700)
        if raw is None:
            return {"available": False, "approved": [], "decisions": []}
        parsed = self._parse_json(raw)
        decisions = parsed.get("candidates") if isinstance(parsed, dict) else None
        if not isinstance(decisions, list):
            return {"available": False, "approved": [], "decisions": []}

        normalized: list[dict[str, Any]] = []
        by_index = {index: url for index, url, _ in loaded}
        for item in decisions:
            if not isinstance(item, dict):
                continue
            try:
                index = int(item.get("index"))
            except (TypeError, ValueError):
                continue
            if index not in by_index:
                continue
            try:
                confidence = max(0.0, min(1.0, float(item.get("confidence", 0))))
            except (TypeError, ValueError):
                confidence = 0.0
            normalized.append(
                {
                    "index": index,
                    "url": by_index[index],
                    "use": _as_bool(item.get("use")),
                    "confidence": confidence,
                    "reason": str(item.get("reason") or "")[:500],
                    "caption_hint": str(item.get("caption_hint") or "")[:300],
                    "placement_hint": str(item.get("placement_hint") or "")[:300],
                }
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
        assignments: list[dict[str, Any]] = []
        for offset in range(0, len(usable_images), _DOCUMENT_IMAGE_BATCH_SIZE):
            batch_images = usable_images[offset : offset + _DOCUMENT_IMAGE_BATCH_SIZE]
            batch: list[tuple[str, dict[str, Any], str]] = []
            for image in batch_images:
                image_id = str(
                    image.get("image_id") or image.get("content_hash") or ""
                )
                data_uri = self._to_data_uri(str(image.get("source_path") or ""))
                if image_id and data_uri:
                    batch.append((image_id, image, data_uri))
            if not batch:
                continue

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
                        '"placement_hint":"..."}]}.\n\n'
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
                assignments.extend(dict(item) for item in cached.get("assignments", []))
                continue

            raw = self._invoke(parts, model=model, max_tokens=1200)
            if raw is None:
                # The provider has marked vision as unavailable. Do not make
                # up assignments for images that were not actually reviewed.
                break
            parsed = self._parse_json(raw)
            decisions = parsed.get("images") if isinstance(parsed, dict) else None
            if not isinstance(decisions, list):
                continue

            batch_assignments: list[dict[str, Any]] = []
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
                if slide_index < 0 or slide_index >= len(slide_chunks) or confidence < 0.5:
                    continue
                source = by_id[image_id]
                batch_assignments.append(
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

            self._set_cache(cache_key, {"assignments": batch_assignments})
            assignments.extend(batch_assignments)

        return [dict(item) for item in assignments]

    def _invoke(
        self,
        content: list[dict[str, Any]],
        *,
        model: str | None = None,
        max_tokens: int,
    ) -> str | None:
        if (
            self._vision_available is False
            and time.monotonic() < self._vision_retry_at
        ):
            return None
        try:
            result = str(
                self.llm_provider.generate_completion(
                    [
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
                    ],
                    model=model or self.model,
                    max_tokens=max_tokens,
                    temperature=0.1,
                    top_p=0.9,
                )
            ).strip()
            self._vision_available = True
            self._vision_retry_at = 0.0
            return result
        except Exception as exc:
            self._vision_available = False
            self._vision_retry_at = time.monotonic() + _VISION_RETRY_SECONDS
            logger.warning("Multimodal image verification unavailable: %s", exc)
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
        with self._cache_lock:
            value = self._cache.get(key)
            return dict(value) if value is not None else None

    def _set_cache(self, key: str, value: dict[str, Any]) -> None:
        with self._cache_lock:
            # Keep this process-local cache bounded; image bytes themselves are
            # not stored, only the structured decision and provenance.
            if len(self._cache) >= 256:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = dict(value)

    @staticmethod
    def _source_hash(source: str) -> str:
        return hashlib.sha256(str(source).encode("utf-8")).hexdigest()

    @classmethod
    def _to_data_uri(cls, source: str) -> str | None:
        try:
            if source.lower().startswith(("http://", "https://")):
                raw, mime_type = cls._download_remote(source)
            else:
                path = Path(source)
                if not path.is_file():
                    return None
                raw = path.read_bytes()
                mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
            if not raw:
                return None
            raw, mime_type = cls._normalize_image(raw, mime_type)
            return f"data:{mime_type};base64,{base64.b64encode(raw).decode('ascii')}"
        except Exception as exc:
            logger.debug("Cannot prepare image for Qwen-VL: %s", exc)
            return None

    @staticmethod
    def _download_remote(url: str) -> tuple[bytes, str]:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("Unsupported image URL")
        hostname = parsed.hostname.rstrip(".").lower()
        if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
            raise ValueError("Private image host")
        try:
            addresses = {
                result[4][0]
                for result in socket.getaddrinfo(
                    hostname,
                    parsed.port or (443 if parsed.scheme == "https" else 80),
                )
            }
        except socket.gaierror as exc:
            raise ValueError("Image host cannot be resolved") from exc
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise ValueError("Private image host")
        request = urllib.request.Request(url, headers={"User-Agent": "SlideGen image verifier"})
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read(_MAX_REMOTE_BYTES + 1)
            if len(raw) > _MAX_REMOTE_BYTES:
                raise ValueError("Image is too large")
            mime_type = (response.headers.get_content_type() or "image/jpeg").lower()
        return raw, mime_type if mime_type.startswith("image/") else "image/jpeg"

    @staticmethod
    def _normalize_image(raw: bytes, mime_type: str) -> tuple[bytes, str]:
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            image.thumbnail((_MAX_IMAGE_EDGE, _MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
            has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
            if has_alpha:
                output = io.BytesIO()
                image.convert("RGBA").save(output, format="PNG", optimize=True)
                normalized, normalized_type = output.getvalue(), "image/png"
            else:
                output = io.BytesIO()
                image.convert("RGB").save(output, format="JPEG", quality=82, optimize=True)
                normalized, normalized_type = output.getvalue(), "image/jpeg"
        if len(normalized) > _MAX_MODEL_IMAGE_BYTES:
            # Re-encode once more at a smaller quality rather than sending a
            # multi-megabyte image to every Qwen verification request.
            with Image.open(io.BytesIO(normalized)) as image:
                output = io.BytesIO()
                image.convert("RGB").save(output, format="JPEG", quality=65, optimize=True)
                normalized, normalized_type = output.getvalue(), "image/jpeg"
        return normalized, normalized_type
