"""Safe access to images embedded in a user's chatbot documents.

The answer model receives stable document/image identifiers, not local paths.
When it explicitly calls the image tool, this service verifies ownership and
session scope before converting the private asset into a bounded data URI for
the configured multimodal provider.
"""

from __future__ import annotations

import base64
import io
import logging
import mimetypes
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any

from PIL import Image

from backend.config import (
    CHATBOT_DOCUMENTS_DIR,
    VLM_MAX_IMAGE_BYTES,
    VLM_MAX_IMAGE_EDGE,
)
from backend.domain.ports.chat_document_repository import ChatDocumentRepository

logger = logging.getLogger(__name__)

_CACHE_MAX_ITEMS = 128


class DocumentImageTool:
    """Resolve one private document image for a multimodal chat turn."""

    name = "get_document_image"

    def __init__(self, repository: ChatDocumentRepository) -> None:
        self.repository = repository
        self._cache: OrderedDict[tuple[str, int, int], tuple[str, str]] = OrderedDict()
        self._cache_lock = threading.Lock()

    @staticmethod
    def schema() -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": DocumentImageTool.name,
                "description": (
                    "Inspect one image embedded in a document attached to the "
                    "current conversation. Use this only when the user's "
                    "question requires seeing the image itself."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "document_id": {
                            "type": "string",
                            "description": "The document id from the image reference.",
                        },
                        "image_id": {
                            "type": "string",
                            "description": "The image id from the image reference.",
                        },
                    },
                    "required": ["document_id", "image_id"],
                    "additionalProperties": False,
                },
            },
        }

    def get_document_image(
        self,
        *,
        session_id: str,
        user_id: int,
        document_id: str,
        image_id: str,
    ) -> dict[str, Any] | None:
        """Return a bounded multimodal payload after scope validation."""
        clean_document_id = str(document_id or "").strip()
        clean_image_id = str(image_id or "").strip()
        if not clean_document_id or not clean_image_id:
            return None

        documents = self.repository.list_session_documents(session_id, user_id)
        document = next(
            (item for item in documents if str(item.id) == clean_document_id),
            None,
        )
        if document is None or str(document.status).lower() != "ready":
            return None

        image = next(
            (
                item
                for item in (getattr(document, "images", []) or [])
                if isinstance(item, dict)
                and str(item.get("image_id") or "").strip() == clean_image_id
            ),
            None,
        )
        if image is None:
            return None

        path = self._owned_path(image.get("source_path"))
        if path is None or not path.is_file():
            logger.warning(
                "Document image is missing or outside the asset root: %s/%s",
                clean_document_id,
                clean_image_id,
            )
            return None

        try:
            stat = path.stat()
            cache_key = (str(path), int(stat.st_mtime_ns), int(stat.st_size))
            data_uri, mime_type = self._get_cached(cache_key)
            if not data_uri:
                raw, mime_type = self._normalize(path.read_bytes(), path)
                data_uri = (
                    f"data:{mime_type};base64,{base64.b64encode(raw).decode('ascii')}"
                )
                self._set_cached(cache_key, data_uri, mime_type)
        except (OSError, ValueError) as exc:
            logger.warning("Unable to read document image %s: %s", path, exc)
            return None

        return {
            "document_id": clean_document_id,
            "image_id": clean_image_id,
            "filename": str(image.get("filename") or "document-image"),
            "section_path": str(image.get("section_path") or ""),
            "nearby_text": str(image.get("nearby_text") or "")[:1800],
            "alt_text": str(image.get("alt_text") or "")[:500],
            "mime_type": mime_type,
            "data_uri": data_uri,
        }

    @staticmethod
    def _owned_path(raw_path: Any) -> Path | None:
        root = CHATBOT_DOCUMENTS_DIR.resolve()
        try:
            path = Path(str(raw_path or "")).resolve()
        except (OSError, RuntimeError, ValueError):
            return None
        if path == root or root not in path.parents:
            return None
        return path

    @staticmethod
    def _normalize(raw: bytes, source: Path) -> tuple[bytes, str]:
        if not raw:
            raise ValueError("empty image")
        mime_type = mimetypes.guess_type(source.name)[0] or "image/png"
        try:
            with Image.open(io.BytesIO(raw)) as image:
                image.load()
                image.thumbnail((VLM_MAX_IMAGE_EDGE, VLM_MAX_IMAGE_EDGE), Image.Resampling.LANCZOS)
                has_alpha = image.mode in {"RGBA", "LA"} or (
                    image.mode == "P" and "transparency" in image.info
                )
                if has_alpha:
                    converted = image.convert("RGBA")
                    output_format = "PNG"
                    mime_type = "image/png"
                else:
                    converted = image.convert("RGB")
                    output_format = "JPEG"
                    mime_type = "image/jpeg"
                output = io.BytesIO()
                save_options: dict[str, Any] = {
                    "format": output_format,
                    "optimize": True,
                }
                if output_format == "JPEG":
                    save_options["quality"] = 82
                converted.save(output, **save_options)
                normalized = output.getvalue()
        except Exception as exc:
            raise ValueError(f"unsupported image: {exc}") from exc

        if len(normalized) <= VLM_MAX_IMAGE_BYTES:
            return normalized, mime_type

        # A second bounded pass keeps the tool useful for high-resolution
        # screenshots without allowing a large local asset into the request.
        with Image.open(io.BytesIO(normalized)) as image:
            image.thumbnail((max(256, VLM_MAX_IMAGE_EDGE // 2),) * 2, Image.Resampling.LANCZOS)
            output = io.BytesIO()
            image.convert("RGB").save(output, format="JPEG", quality=65, optimize=True)
            normalized = output.getvalue()
        if len(normalized) > VLM_MAX_IMAGE_BYTES:
            raise ValueError("normalized image exceeds the multimodal request limit")
        return normalized, "image/jpeg"

    def _get_cached(self, key: tuple[str, int, int]) -> tuple[str | None, str | None]:
        with self._cache_lock:
            value = self._cache.pop(key, None)
            if value is None:
                return None, None
            self._cache[key] = value
            return value

    def _set_cached(self, key: tuple[str, int, int], data_uri: str, mime_type: str) -> None:
        with self._cache_lock:
            self._cache.pop(key, None)
            self._cache[key] = (data_uri, mime_type)
            while len(self._cache) > _CACHE_MAX_ITEMS:
                self._cache.popitem(last=False)
