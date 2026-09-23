"""Materialize verified slide images into stable project assets.

The XML workflow may receive either an embedded DOCX path or a remote search
URL.  Keeping those values directly in XML makes the result dependent on a
temporary directory, browser CORS, hotlink protection, or a remote server's
content type.  This service gives every approved image one local, validated
asset and returns the URL format understood by both the editor and the PPTX
converter.
"""

from __future__ import annotations

import hashlib
import ipaddress
import io
import logging
import mimetypes
import socket
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import OrderedDict
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image

from backend.config import OUTPUT_DIR, STATIC_DIR

logger = logging.getLogger(__name__)


class SlideAssetError(ValueError):
    """Raised when an approved image cannot be made into a local asset."""


class SlideAssetService:
    """Copy or download validated images and rewrite XML image sources."""

    MAX_REMOTE_BYTES = 15 * 1024 * 1024
    CACHE_TTL_SECONDS = 30 * 60
    CACHE_MAX_ITEMS = 64
    CACHE_MAX_BYTES = 32 * 1024 * 1024

    def __init__(self) -> None:
        self._remote_cache: OrderedDict[str, tuple[float, bytes, str]] = OrderedDict()
        self._remote_cache_bytes = 0
        self._cache_lock = threading.Lock()

    def remember_remote(self, source: str, raw: bytes, mime_type: str = "") -> None:
        """Cache a validated/normalized remote image for the current process."""
        key = str(source or "").strip()
        payload = bytes(raw or b"")
        if not key or not payload or len(payload) > self.CACHE_MAX_BYTES:
            return
        now = time.monotonic()
        with self._cache_lock:
            previous = self._remote_cache.pop(key, None)
            if previous:
                self._remote_cache_bytes -= len(previous[1])
            self._remote_cache[key] = (now, payload, str(mime_type or ""))
            self._remote_cache_bytes += len(payload)
            self._trim_cache_locked(now)

    def get_cached_remote(self, source: str) -> tuple[bytes, str] | None:
        """Return a fresh cached image and refresh its LRU position."""
        key = str(source or "").strip()
        if not key:
            return None
        now = time.monotonic()
        with self._cache_lock:
            item = self._remote_cache.pop(key, None)
            if item is None:
                return None
            created_at, raw, mime_type = item
            if now - created_at >= self.CACHE_TTL_SECONDS:
                self._remote_cache_bytes -= len(raw)
                return None
            self._remote_cache[key] = (created_at, raw, mime_type)
            return raw, mime_type

    def _trim_cache_locked(self, now: float) -> None:
        while self._remote_cache:
            oldest_key, (created_at, raw, _) = next(iter(self._remote_cache.items()))
            expired = now - created_at >= self.CACHE_TTL_SECONDS
            over_limit = (
                len(self._remote_cache) > self.CACHE_MAX_ITEMS
                or self._remote_cache_bytes > self.CACHE_MAX_BYTES
            )
            if not expired and not over_limit:
                break
            self._remote_cache.pop(oldest_key, None)
            self._remote_cache_bytes -= len(raw)

    def materialize(self, source: str, asset_dir: str | Path) -> str:
        """Materialize one image and return a browser/converter-safe source."""
        value = str(source or "").strip()
        if not value:
            raise SlideAssetError("Image source is empty")

        raw, suffix = self._read_source(value)
        digest = hashlib.sha256(raw).hexdigest()[:24]
        target_root = Path(asset_dir) / "image_assets"
        target_root.mkdir(parents=True, exist_ok=True)
        target = target_root / f"{digest}{suffix}"
        if not target.exists() or target.stat().st_size != len(raw):
            target.write_bytes(raw)
        return self._public_source(target)

    def rewrite_xml_sources(
        self,
        xml_content: str,
        asset_dir: str | Path,
    ) -> str:
        """Copy all XML image sources into a permanent project asset folder."""
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            return xml_content

        changed = False
        for image in root.iter("image"):
            source = str(image.get("src") or "").strip()
            if not source:
                continue
            try:
                materialized = self.materialize(source, asset_dir)
            except (OSError, SlideAssetError) as exc:
                # Keep a remote source as a last-resort browser fallback. A
                # failed local copy must not corrupt an otherwise editable XML.
                logger.warning(
                    "Could not materialize image asset '%s': %s",
                    source[:120],
                    exc,
                )
                continue
            if materialized != source:
                image.set("src", materialized)
                changed = True

        if not changed:
            return xml_content
        return ET.tostring(root, encoding="unicode")

    def _read_source(self, source: str) -> tuple[bytes, str]:
        lowered = source.lower()
        if lowered.startswith(("http://", "https://")):
            return self._read_remote(source)
        if lowered.startswith("data:image/"):
            return self._read_data_url(source)

        path = self._local_path(source)
        if not path.is_file():
            raise SlideAssetError(f"Image file does not exist: {path}")
        return self._validate_bytes(path.read_bytes(), path.suffix)

    @staticmethod
    def _local_path(source: str) -> Path:
        value = unquote(source)
        normalized = value.replace("\\", "/")
        if normalized.lower().startswith("/static/output/"):
            return OUTPUT_DIR / normalized[len("/static/output/"):]
        if normalized.lower().startswith("/static/temp/"):
            return STATIC_DIR / "temp" / normalized[len("/static/temp/"):]
        if value.lower().startswith("file://"):
            parsed = urlsplit(value)
            value = parsed.path
            if parsed.netloc and parsed.netloc.lower() != "localhost":
                value = f"//{parsed.netloc}{value}"
        return Path(value)

    def read_remote(self, source: str, *, timeout: float = 30) -> tuple[bytes, str]:
        """Read one validated remote image, reusing the process cache."""
        return self._read_remote(source, timeout=timeout)

    def _read_remote(self, source: str, *, timeout: float = 30) -> tuple[bytes, str]:
        cached = self.get_cached_remote(source)
        if cached is not None:
            # The verifier may cache a MIME type (e.g. ``image/png``), while
            # materialization needs a safe filename suffix. Re-validate the
            # cached bytes so the detected image format remains authoritative.
            raw, format_hint = cached
            return self._validate_bytes(raw, format_hint)
        self._validate_remote_host(source)
        request = urllib.request.Request(
            source,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
                )
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read(self.MAX_REMOTE_BYTES + 1)
                content_type = (response.headers.get_content_type() or "").lower()
        except Exception as exc:
            raise SlideAssetError(f"Remote image download failed: {exc}") from exc
        if len(raw) > self.MAX_REMOTE_BYTES:
            raise SlideAssetError("Remote image exceeds the asset size limit")
        suffix = Path(urlsplit(source).path).suffix
        if content_type.startswith("image/"):
            suffix = mimetypes.guess_extension(content_type) or suffix
        validated = self._validate_bytes(raw, suffix)
        self.remember_remote(source, *validated)
        return validated

    @staticmethod
    def _read_data_url(source: str) -> tuple[bytes, str]:
        header, payload = source.split(",", 1)
        if ";base64" not in header.lower():
            raise SlideAssetError("Only base64 image data URLs are supported")
        import base64

        try:
            raw = base64.b64decode(payload, validate=True)
        except Exception as exc:
            raise SlideAssetError("Invalid image data URL") from exc
        mime = header[5:].split(";", 1)[0].lower()
        suffix = mimetypes.guess_extension(mime) or ".img"
        return SlideAssetService._validate_bytes(raw, suffix)

    @staticmethod
    def _validate_bytes(raw: bytes, suffix: str = "") -> tuple[bytes, str]:
        if not raw:
            raise SlideAssetError("Image is empty")
        normalized_suffix = str(suffix or "").lower()
        if normalized_suffix == ".svg" or raw.lstrip().startswith(b"<svg"):
            return raw, ".svg"
        try:
            with Image.open(io.BytesIO(raw)) as image:
                image.verify()
                detected = (image.format or "").lower()
        except Exception as exc:
            raise SlideAssetError("Downloaded content is not a valid image") from exc
        extension = {
            "jpeg": ".jpg",
            "jpg": ".jpg",
            "png": ".png",
            "gif": ".gif",
            "webp": ".webp",
            "bmp": ".bmp",
            "tiff": ".tif",
        }.get(detected)
        if not extension:
            extension = normalized_suffix if normalized_suffix in {
                ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"
            } else ".img"
        return raw, extension

    @staticmethod
    def _validate_remote_host(source: str) -> None:
        parsed = urlsplit(source)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise SlideAssetError("Image URL must use http or https")
        hostname = parsed.hostname.rstrip(".").lower()
        if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
            raise SlideAssetError("Private image host is not allowed")
        try:
            addresses = {
                result[4][0]
                for result in socket.getaddrinfo(
                    hostname,
                    parsed.port or (443 if parsed.scheme == "https" else 80),
                )
            }
        except socket.gaierror as exc:
            raise SlideAssetError("Image host cannot be resolved") from exc
        for address in addresses:
            ip = ipaddress.ip_address(address)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise SlideAssetError("Private image host is not allowed")

    @staticmethod
    def _public_source(path: Path) -> str:
        resolved = path.resolve()
        output_root = OUTPUT_DIR.resolve()
        try:
            relative = resolved.relative_to(output_root)
        except ValueError:
            return str(resolved)
        return f"/static/output/{relative.as_posix()}"


slide_asset_service = SlideAssetService()
