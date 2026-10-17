"""Re-download the test-set image caches from their source URLs.

Cached files are named by the first 24 hex digits of the SHA-256 of their bytes, so a
re-downloaded image that hashes to its name is byte-identical ("restored"). Image hosts
often re-encode over time; with --accept-changed such an image is stored under the old
name anyway ("changed"), so every system is scored against the same, current image.

Usage: python scripts/restore_image_cache.py [--accept-changed] slidegen_data/testset_v2/wiki_testset_planned.json [...]
"""
from __future__ import annotations

import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.application.services.slide_asset_service import SlideAssetService  # noqa: E402


def image_sources(value, found: dict[str, set[str]]) -> None:
    """Collect every cached path -> candidate source URLs in a planned corpus."""
    if isinstance(value, dict):
        path = str(value.get("source_path") or "")
        if path.startswith("/static/output/"):
            for key in ("selected_source_url", "source_url"):
                if str(value.get(key) or "").startswith("http"):
                    found.setdefault(path, set()).add(value[key])
        for item in value.values():
            image_sources(item, found)
    elif isinstance(value, list):
        for item in value:
            image_sources(item, found)


def restore(path: str, urls: set[str], service: SlideAssetService, accept_changed: bool) -> str:
    target = ROOT / path.lstrip("/")
    if target.exists():
        return "present"
    target.parent.mkdir(parents=True, exist_ok=True)
    for url in sorted(urls):
        try:
            raw, _ = service.read_remote(url)
        except Exception:  # noqa: BLE001
            continue
        identical = hashlib.sha256(raw).hexdigest()[:24] == target.stem
        if identical or accept_changed:
            target.write_bytes(raw)
        return "restored" if identical else "changed"
    return "unreachable"


def main() -> None:
    accept_changed = "--accept-changed" in sys.argv
    found: dict[str, set[str]] = {}
    for corpus in [arg for arg in sys.argv[1:] if not arg.startswith("--")]:
        image_sources(json.loads(Path(corpus).read_text(encoding="utf-8")), found)
    service = SlideAssetService()
    with ThreadPoolExecutor(16) as pool:
        results = dict(zip(found, pool.map(lambda item: restore(*item, service, accept_changed), found.items())))
    for status in ("present", "restored", "changed", "unreachable"):
        print(status, sum(value == status for value in results.values()))
    for path, status in sorted(results.items()):
        if status == "unreachable":
            print(status, path, sorted(found[path])[0][:120])


if __name__ == "__main__":
    main()
