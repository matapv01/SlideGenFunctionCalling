from __future__ import annotations

import atexit
import json
import logging
import math
import numbers
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from PIL import Image, ImageDraw, ImageFont


PALETTE = {
    "bg": "#FFFFFF",
    "panel": "#F8FAFC",
    "panel_alt": "#EEF2FF",
    "border": "#CBD5E1",
    "text": "#0F172A",
    "muted": "#475569",
    "accent": "#2563EB",
    "accent_2": "#0F766E",
    "accent_3": "#7C3AED",
    "grid": "#E2E8F0",
}


class TeeStream:
    def __init__(self, *streams):
        self.streams = streams
        self._primary = streams[0] if streams else sys.__stdout__

    @property
    def encoding(self):
        return getattr(self._primary, "encoding", None)

    @property
    def errors(self):
        return getattr(self._primary, "errors", None)

    @property
    def closed(self):
        return all(getattr(stream, "closed", False) for stream in self.streams)

    def write(self, data):
        for stream in self.streams:
            if getattr(stream, "closed", False):
                continue
            try:
                stream.write(data)
                stream.flush()
            except ValueError:
                continue
        return len(data)

    def flush(self):
        for stream in self.streams:
            if getattr(stream, "closed", False):
                continue
            try:
                stream.flush()
            except ValueError:
                continue

    def fileno(self):
        return self._primary.fileno()

    def isatty(self):
        return self._primary.isatty()

    def writable(self):
        return True

    def __getattr__(self, name):
        return getattr(self._primary, name)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def start_run_logging(log_dir: str | Path, filename: str = "run.log") -> Path:
    ensure_dir(log_dir)
    log_path = Path(log_dir) / filename
    log_file = open(log_path, "a", encoding="utf-8")
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = TeeStream(old_stdout, log_file)
    sys.stderr = TeeStream(old_stderr, log_file)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )

    def restore_streams():
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        log_file.close()

    atexit.register(restore_streams)
    return log_path


def _run_command(cmd: Sequence[str], timeout: int = 3) -> str | None:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
    except Exception:
        return None
    output = (result.stdout or result.stderr or "").strip()
    return output or None


def _git_info() -> dict[str, str | None]:
    return {
        "branch": _run_command(["git", "branch", "--show-current"]),
        "commit": _run_command(["git", "rev-parse", "--short", "HEAD"]),
        "remote": _run_command(["git", "remote", "get-url", "origin"]),
    }


def _gpu_snapshot() -> list[dict[str, str]]:
    output = _run_command(
        [
            "nvidia-smi",
            "--query-gpu=index,uuid,name,memory.total,memory.used,memory.free",
            "--format=csv,noheader,nounits",
        ],
        timeout=4,
    )
    if not output:
        return []

    rows: list[dict[str, str]] = []
    for line in output.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 6:
            continue
        rows.append(
            {
                "index": parts[0],
                "uuid": parts[1],
                "name": parts[2],
                "memory_total_mib": parts[3],
                "memory_used_mib": parts[4],
                "memory_free_mib": parts[5],
            }
        )
    return rows


def get_runtime_metadata(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "executable": sys.executable,
        "cwd": os.getcwd(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "nvidia_visible_devices": os.environ.get("NVIDIA_VISIBLE_DEVICES"),
        "git": _git_info(),
        "gpus": _gpu_snapshot(),
    }

    try:
        import torch

        meta["torch"] = {
            "version": torch.__version__,
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": (
                torch.cuda.device_count() if torch.cuda.is_available() else 0
            ),
        }
        if torch.cuda.is_available():
            meta["torch"]["device_name"] = torch.cuda.get_device_name(0)
            meta["torch"]["capability"] = ".".join(map(str, torch.cuda.get_device_capability(0)))
    except Exception as exc:
        meta["torch_error"] = str(exc)

    if extra:
        meta.update(extra)
    return meta


def write_json(path: str | Path, data: Any) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    return path


def _load_font(size: int, bold: bool = False):
    system_fonts = (
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        (
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ),
        ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),
        ("Arial.ttf", "Arial Bold.ttf"),
    )
    candidates = [font_pair[bool(bold)] for font_pair in system_fonts]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _measure_text(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _wrap_paragraph(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    if not text:
        return [""]
    if not text.strip():
        return [""]

    words = text.split()
    if not words:
        return [text]

    lines: list[str] = []
    current = words[0]

    def _break_long_word(word: str) -> list[str]:
        if draw.textlength(word, font=font) <= max_width:
            return [word]
        chunks: list[str] = []
        part = ""
        for ch in word:
            test = part + ch
            if draw.textlength(test, font=font) <= max_width:
                part = test
            else:
                if part:
                    chunks.append(part)
                part = ch
        if part:
            chunks.append(part)
        return chunks or [word]

    for word in words[1:]:
        test = f"{current} {word}"
        if draw.textlength(test, font=font) <= max_width:
            current = test
            continue
        lines.append(current)
        if draw.textlength(word, font=font) <= max_width:
            current = word
        else:
            chunks = _break_long_word(word)
            lines.extend(chunks[:-1])
            current = chunks[-1]
    lines.append(current)
    return lines


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines():
        wrapped = _wrap_paragraph(draw, paragraph, font, max_width)
        lines.extend(wrapped if wrapped else [""])
    return lines or [""]


def save_text_summary_image(
    path: str | Path,
    title: str,
    sections: Sequence[dict[str, Any] | tuple[str, Any]],
    subtitle: str | None = None,
    footer: str | None = None,
    width: int = 1600,
) -> Path:
    title_font = _load_font(44, bold=True)
    subtitle_font = _load_font(24, bold=False)
    section_font = _load_font(28, bold=True)
    body_font = _load_font(22, bold=False)
    tiny_font = _load_font(18, bold=False)

    temp = Image.new("RGB", (width, 100), PALETTE["bg"])
    draw = ImageDraw.Draw(temp)
    content_width = width - 128

    section_data: list[dict[str, Any]] = []
    total_height = 64 + 14 + 8 + 24
    title_h = _measure_text(draw, title, title_font)[1]
    total_height += title_h
    if subtitle:
        total_height += _measure_text(draw, subtitle, subtitle_font)[1] + 12
    total_height += 24

    for raw in sections:
        if isinstance(raw, tuple):
            sec_title, sec_body = raw
        else:
            sec_title = str(raw.get("title", ""))
            sec_body = raw.get("body", "")
        if isinstance(sec_body, list):
            sec_body = "\n".join(str(item) for item in sec_body)
        sec_body = str(sec_body)
        body_lines = _wrap_text(draw, sec_body, body_font, content_width - 72)
        body_line_height = _measure_text(draw, "Ag", body_font)[1] + 8
        header_h = _measure_text(draw, sec_title, section_font)[1] + 6
        panel_h = 28 + header_h + 18 + max(body_line_height * len(body_lines), body_line_height) + 24
        section_data.append(
            {
                "title": sec_title,
                "body_lines": body_lines,
                "panel_h": panel_h,
                "header_h": header_h,
                "body_line_height": body_line_height,
            }
        )
        total_height += panel_h + 18

    if footer:
        total_height += _measure_text(draw, footer, tiny_font)[1] + 28
    total_height = max(total_height + 32, 900)

    img = Image.new("RGB", (width, int(total_height)), PALETTE["bg"])
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width, 14], fill=PALETTE["accent"])
    draw.text((64, 40), title, fill=PALETTE["text"], font=title_font)
    y = 40 + title_h + 12
    if subtitle:
        draw.text((64, y), subtitle, fill=PALETTE["muted"], font=subtitle_font)
        y += _measure_text(draw, subtitle, subtitle_font)[1] + 24
    else:
        y += 16

    left = 64
    right = width - 64
    panel_width = right - left

    for idx, sec in enumerate(section_data):
        top = y
        bottom = top + sec["panel_h"]
        fill = PALETTE["panel"] if idx % 2 == 0 else PALETTE["panel_alt"]
        draw.rounded_rectangle(
            [left, top, right, bottom],
            radius=18,
            fill=fill,
            outline=PALETTE["border"],
            width=2,
        )
        accent = PALETTE["accent_2"] if idx % 2 == 0 else PALETTE["accent_3"]
        draw.rectangle([left, top, left + 8, bottom], fill=accent)
        draw.text(
            (left + 28, top + 18),
            sec["title"],
            fill=PALETTE["text"],
            font=section_font,
        )
        body_y = top + 18 + sec["header_h"] + 6
        for line in sec["body_lines"]:
            draw.text((left + 28, body_y), line, fill=PALETTE["text"], font=body_font)
            body_y += sec["body_line_height"]
        y = bottom + 18

    if footer:
        draw.text((64, int(total_height) - 54), footer, fill=PALETTE["muted"], font=tiny_font)

    path = Path(path)
    ensure_dir(path.parent)
    img.save(path)
    return path


def save_metric_trend_image(
    rows: Sequence[dict[str, Any]],
    out_path: str | Path,
    title: str,
    preferred_keys: Sequence[str] | None = None,
    width: int = 1600,
    height: int = 900,
) -> Path:
    numeric_rows = [row for row in rows if isinstance(row, dict)]
    if not numeric_rows:
        return save_text_summary_image(
            out_path,
            title,
            [{"title": "No metrics", "body": "No numeric metric rows were available."}],
        )

    if preferred_keys:
        keys = [
            key
            for key in preferred_keys
            if any(isinstance(row.get(key), (int, float)) for row in numeric_rows)
        ]
    else:
        counts: dict[str, int] = {}
        for row in numeric_rows:
            for key, value in row.items():
                if isinstance(value, numbers.Number) and not isinstance(value, bool):
                    if key.lower() in {"step", "epoch", "global_step", "step_num", "iteration"}:
                        continue
                    counts[key] = counts.get(key, 0) + 1
        keys = [
            key
            for key, _ in sorted(
                counts.items(), key=lambda item: (-item[1], item[0])
            )[:4]
        ]

    if not keys:
        return save_text_summary_image(
            out_path,
            title,
            [{"title": "No plottable metrics", "body": "No numeric metrics could be selected for plotting."}],
        )

    series: dict[str, list[float | None]] = {key: [] for key in keys}
    x_labels: list[str] = []
    for idx, row in enumerate(numeric_rows):
        x_labels.append(str(row.get("step", row.get("global_step", idx + 1))))
        for key in keys:
            value = row.get(key)
            numeric_value = (
                float(value)
                if isinstance(value, numbers.Number) and not isinstance(value, bool)
                else None
            )
            series[key].append(numeric_value)

    values = [value for values in series.values() for value in values if value is not None]
    if not values:
        return save_text_summary_image(
            out_path,
            title,
            [{"title": "No plottable metrics", "body": "The selected metrics did not contain numeric values."}],
        )

    min_v = min(values)
    max_v = max(values)
    if math.isclose(min_v, max_v):
        min_v -= 1.0
        max_v += 1.0
    span = max_v - min_v
    margin_left, margin_top, margin_right, margin_bottom = 110, 120, 70, 90
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    img = Image.new("RGB", (width, height), PALETTE["bg"])
    draw = ImageDraw.Draw(img)
    title_font = _load_font(40, bold=True)
    legend_font = _load_font(20, bold=False)
    axis_font = _load_font(18, bold=False)

    draw.rectangle([0, 0, width, 12], fill=PALETTE["accent"])
    draw.text((64, 30), title, fill=PALETTE["text"], font=title_font)
    draw.text(
        (64, 78),
        f"Selected metrics: {', '.join(keys)}",
        fill=PALETTE["muted"],
        font=legend_font,
    )

    left = margin_left
    top = margin_top
    right = width - margin_right
    bottom = height - margin_bottom
    draw.rectangle([left, top, right, bottom], outline=PALETTE["border"], width=2)

    for grid_idx in range(6):
        gy = top + int(plot_h * grid_idx / 5)
        draw.line([(left, gy), (right, gy)], fill=PALETTE["grid"], width=1)
        value = max_v - span * grid_idx / 5
        label = f"{value:.3f}" if abs(value) < 1000 else f"{value:.1f}"
        tw, th = _measure_text(draw, label, axis_font)
        draw.text(
            (left - tw - 14, gy - th / 2),
            label,
            fill=PALETTE["muted"],
            font=axis_font,
        )

    colors = [PALETTE["accent"], PALETTE["accent_2"], PALETTE["accent_3"], "#DC2626"]
    count = max(len(x_labels) - 1, 1)
    for idx, key in enumerate(keys):
        points: list[tuple[float, float]] = []
        for i, value in enumerate(series[key]):
            if value is None:
                continue
            x = left + (plot_w * i / count)
            y = bottom - ((value - min_v) / span) * plot_h
            points.append((x, y))
        if len(points) >= 2:
            draw.line(points, fill=colors[idx % len(colors)], width=4)
        for x, y in points:
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=colors[idx % len(colors)])

    legend_x = left + 10
    legend_y = bottom + 18
    for idx, key in enumerate(keys):
        color = colors[idx % len(colors)]
        draw.rectangle(
            [legend_x, legend_y + idx * 32, legend_x + 18, legend_y + idx * 32 + 18],
            fill=color,
        )
        draw.text(
            (legend_x + 28, legend_y + idx * 32 - 1),
            key,
            fill=PALETTE["text"],
            font=legend_font,
        )

    if x_labels:
        draw.text((left, bottom + 48), f"first: {x_labels[0]}", fill=PALETTE["muted"], font=axis_font)
        middle_label = x_labels[len(x_labels) // 2]
        draw.text(
            (left + plot_w / 2 - 50, bottom + 48),
            f"mid: {middle_label}",
            fill=PALETTE["muted"],
            font=axis_font,
        )
        draw.text((right - 130, bottom + 48), f"last: {x_labels[-1]}", fill=PALETTE["muted"], font=axis_font)

    out_path = Path(out_path)
    ensure_dir(out_path.parent)
    img.save(out_path)
    return out_path
