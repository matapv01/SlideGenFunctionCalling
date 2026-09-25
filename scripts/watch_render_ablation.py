#!/usr/bin/env python3
"""Incrementally render completed ablation XML files without gating generation."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from backend.infrastructure.capture.playwright_provider import PlaywrightCaptureProvider
from backend.workflows.slidegen_workflow.utils.xml_preview import build_xml_preview_html


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--max-attempts", type=int, default=3)
    return parser.parse_args()


def natural_key(path: Path) -> tuple:
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    )


def generation_status(root: Path) -> str:
    path = root / "generation_summary.json"
    if not path.is_file():
        return "starting"
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("status", "running"))
    except (OSError, json.JSONDecodeError):
        return "running"


def output_paths(root: Path, xml_path: Path) -> tuple[Path, Path]:
    relative = xml_path.relative_to(root)
    parts = relative.parts
    if len(parts) < 7 or parts[0] != "decks" or parts[3:6] != ("output", "xml", xml_path.name):
        # Expected: decks/<doc>/<mode>/output/xml/<slide>.xml
        if len(parts) != 6 or parts[0] != "decks" or parts[3:5] != ("output", "xml"):
            raise ValueError(f"Unexpected XML path: {relative}")
    doc_slug, mode = parts[1], parts[2]
    png_path = root / "decks" / doc_slug / mode / "output" / "png" / f"{xml_path.stem}.png"
    eval_path = root / "evaluation_input" / doc_slug / mode / f"{xml_path.stem}.png"
    return png_path, eval_path


def write_summary(root: Path, payload: dict) -> None:
    (root / "render_summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


async def main() -> int:
    args = parse_args()
    root = args.run_root.resolve()
    capture = PlaywrightCaptureProvider()
    attempts: dict[str, int] = {}
    rendered = 0
    started = datetime.now(timezone.utc).isoformat()

    while True:
        xml_paths = sorted(root.glob("decks/*/*/output/xml/*.xml"), key=natural_key)
        pending = []
        for xml_path in xml_paths:
            png_path, eval_path = output_paths(root, xml_path)
            if png_path.is_file():
                if not eval_path.is_file():
                    eval_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(png_path, eval_path)
                continue
            if attempts.get(str(xml_path), 0) < args.max_attempts:
                pending.append((xml_path, png_path, eval_path))

        for xml_path, png_path, eval_path in pending:
            key = str(xml_path)
            attempts[key] = attempts.get(key, 0) + 1
            try:
                xml = xml_path.read_text(encoding="utf-8")
                html = build_xml_preview_html(xml, slide_index=0)
                png_path.parent.mkdir(parents=True, exist_ok=True)
                await capture.generate_slide_from_html(html, str(png_path))
                eval_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(png_path, eval_path)
                rendered += 1
                print(f"Rendered {xml_path.relative_to(root)} -> {eval_path.relative_to(root)}", flush=True)
            except Exception as exc:
                print(
                    f"Render attempt {attempts[key]}/{args.max_attempts} failed for "
                    f"{xml_path.relative_to(root)}: {exc!r}",
                    flush=True,
                )

        status = generation_status(root)
        all_xml = list(root.glob("decks/*/*/output/xml/*.xml"))
        all_png = list(root.glob("decks/*/*/output/png/*.png"))
        failed = [
            path for path in all_xml
            if not output_paths(root, path)[0].is_file()
            and attempts.get(str(path), 0) >= args.max_attempts
        ]
        payload = {
            "status": "running",
            "started_at_utc": started,
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "generation_status": status,
            "xml_count": len(all_xml),
            "png_count": len(all_png),
            "rendered_by_watcher": rendered,
            "failed_files": [str(path.relative_to(root)) for path in failed],
        }

        if status not in {"starting", "running"} and len(all_png) + len(failed) >= len(all_xml):
            payload["status"] = "completed" if not failed else "completed_with_failures"
            payload["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
            write_summary(root, payload)
            return 0 if not failed else 1

        write_summary(root, payload)
        await asyncio.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
