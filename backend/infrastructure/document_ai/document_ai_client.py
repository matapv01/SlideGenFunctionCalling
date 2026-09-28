"""Small, authenticated-by-network client for the Document AI OCR service."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class DocumentAiError(RuntimeError):
    """Raised when the external OCR service cannot produce a valid response."""


@dataclass(frozen=True)
class OcrResult:
    """Stable OCR response; callers do not depend on the vendor JSON shape."""

    text: str
    pages: int = 0
    tables: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentAiClient:
    """Call the OCR endpoint without leaking transport details into services."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 60,
        max_response_bytes: int = 20 * 1024 * 1024,
    ) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        self.max_response_bytes = max(1, int(max_response_bytes))

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    async def ocr(self, file_path: str | Path) -> OcrResult:
        """Extract text and raw tables from one local document."""
        if not self.enabled:
            raise DocumentAiError("Document AI OCR is not configured")
        source = Path(file_path)
        if not source.is_file():
            raise DocumentAiError(f"OCR source does not exist: {source}")

        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout_seconds),
                follow_redirects=False,
            ) as client:
                with source.open("rb") as handle:
                    response = await client.post(
                        "/api/v1/ocr",
                        files={
                            "file": (
                                source.name,
                                handle,
                                _content_type(source),
                            )
                        },
                    )
            response.raise_for_status()
        except (OSError, httpx.HTTPError) as exc:
            raise DocumentAiError(f"OCR request failed: {exc}") from exc

        if len(response.content) > self.max_response_bytes:
            raise DocumentAiError("OCR response exceeds the configured size limit")
        try:
            payload = response.json()
        except (ValueError, json.JSONDecodeError) as exc:
            raise DocumentAiError("OCR service returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise DocumentAiError("OCR service returned an invalid response")

        text = str(payload.get("text") or "").strip()
        tables = payload.get("tables")
        normalized_tables = [
            table for table in tables if isinstance(table, dict)
        ] if isinstance(tables, list) else []
        if not text and not normalized_tables:
            raise DocumentAiError("OCR service returned no readable content")

        return OcrResult(
            text=text,
            pages=_as_non_negative_int(payload.get("pages")),
            tables=normalized_tables,
            metadata={
                "file_name": str(payload.get("file_name") or source.name),
                "table_count": _as_non_negative_int(payload.get("table_count")),
                "processing_time": payload.get("processing_time"),
            },
        )


def _content_type(path: Path) -> str:
    return {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".txt": "text/plain",
    }.get(path.suffix.lower(), "application/octet-stream")


def _as_non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0
