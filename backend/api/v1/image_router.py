# File: backend/api/v1/image_router.py

from __future__ import annotations

import ipaddress
import mimetypes
import socket
import urllib.request
from urllib.error import HTTPError, URLError
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response
from backend.config import OUTPUT_DIR, UPLOAD_DIR
import logging

router = APIRouter(prefix="/image-serve", tags=["IMAGE SERVING"])
logger = logging.getLogger("SlideGen-image-serve")

_MAX_REMOTE_IMAGE_BYTES = 15 * 1024 * 1024


def _validate_remote_url(url: str) -> None:
    """Allow public HTTP(S) images while avoiding local-network proxying."""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(status_code=400, detail="URL ảnh phải dùng http hoặc https")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".local"):
        raise HTTPException(status_code=400, detail="Không thể proxy địa chỉ nội bộ")

    # Resolve the host before fetching it so a browser cannot turn this endpoint
    # into a simple proxy for loopback/private addresses.
    try:
        addresses = {
            info[4][0]
            for info in socket.getaddrinfo(
                hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
            )
        }
    except socket.gaierror as exc:
        raise HTTPException(status_code=502, detail="Không phân giải được máy chủ ảnh") from exc

    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            continue
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
        ):
            raise HTTPException(status_code=400, detail="Không thể proxy địa chỉ nội bộ")


@router.get("/remote-proxy")
def proxy_remote_image(url: str = Query(..., min_length=1, max_length=4096)):
    """Fetch a remote slide image through the same origin as the editor.

    Generated XML intentionally keeps the original URL so PowerPoint export can
    download it. The editor uses this endpoint only when the browser cannot load
    that URL directly (hotlink protection, CORS, or a network policy).
    """
    _validate_remote_url(url)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 SlideGen image proxy"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as remote:
            content_type = (remote.headers.get_content_type() or "").lower()
            data = remote.read(_MAX_REMOTE_IMAGE_BYTES + 1)
            if not content_type.startswith("image/"):
                # A few CDNs send ``application/octet-stream`` for an image;
                # use the URL extension as a safe fallback for the browser.
                guessed_type, _ = mimetypes.guess_type(urlsplit(url).path)
                content_type = (guessed_type or "").lower()
            if not content_type.startswith("image/"):
                raise HTTPException(status_code=415, detail="URL không trả về dữ liệu ảnh")
    except HTTPException:
        raise
    except HTTPError as exc:
        logger.warning("Remote image returned HTTP %s: %s", exc.code, url)
        raise HTTPException(status_code=502, detail="Không tải được ảnh từ máy chủ") from exc
    except (URLError, TimeoutError, OSError) as exc:
        logger.warning("Remote image download failed for %s: %s", url, exc)
        raise HTTPException(status_code=502, detail="Không tải được ảnh từ máy chủ") from exc

    if len(data) > _MAX_REMOTE_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Ảnh từ xa vượt quá kích thước cho phép")

    return Response(
        content=data,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/project-asset")
def get_project_asset(
    path: str = Query(..., min_length=1, max_length=2048),
):
    """Serve an image copied into a generated project's output assets.

    The browser receives only a path relative to ``static/output``.  Resolve
    and validate it against that directory before serving so this compatibility
    bridge cannot expose arbitrary files from the container.
    """
    relative_path = Path(path.replace("\\", "/"))
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise HTTPException(status_code=400, detail="Đường dẫn asset không hợp lệ")

    output_root = OUTPUT_DIR.resolve()
    image_path = (output_root / relative_path).resolve()
    try:
        image_path.relative_to(output_root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Đường dẫn asset không hợp lệ") from exc

    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy asset của project")

    content_type = (mimetypes.guess_type(image_path.name)[0] or "").lower()
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Asset không phải là ảnh")

    return FileResponse(
        image_path,
        media_type=content_type,
        headers={"Cache-Control": "private, max-age=3600"},
    )


@router.get("/{image_name}")
async def get_image(image_name: str):
    """
    Serve an image file from the uploads directory.
    """
    safe_name = image_name.replace("\\", "/").split("/")[-1]
    image_path = UPLOAD_DIR / safe_name
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy hình ảnh")
    return FileResponse(image_path)
