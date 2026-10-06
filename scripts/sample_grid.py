"""Build one comparison sheet per watched eval slide: renders across steps, labeled with reward and issues.

Usage: python scripts/sample_grid.py <run_output_dir>/samples [--last N]
"""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

THUMB_W = 640


def _font(size):
    for path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _tile(step_dir: Path, stem: str) -> Image.Image:
    record = json.loads((step_dir / f"{stem}.json").read_text(encoding="utf-8"))
    png = step_dir / f"{stem}.png"
    if png.exists():
        image = Image.open(png).convert("RGB")
        image = image.resize((THUMB_W, int(image.height * THUMB_W / image.width)))
    else:
        image = Image.new("RGB", (THUMB_W, THUMB_W * 9 // 16), "#f3d6d6")
        ImageDraw.Draw(image).text((20, 20), "INVALID OUTPUT\n" + record["completion"][:300], fill="#600", font=_font(16))
    parts = record.get("components") or {}
    caption = (
        f"step {record['step']}  reward {record['reward']:.2f}\n"
        f"dom {parts.get('dom', 0):.2f}  num {parts.get('numeric_fact', 0):.2f}  "
        f"sem {parts.get('semantic', 0):.2f}  lang {parts.get('language', 0):.2f}  aes {parts.get('aesthetic', 0):.2f}\n"
        f"issues: {', '.join(record.get('dom_issues') or []) or 'none'}"
    )
    tile = Image.new("RGB", (THUMB_W, image.height + 78), "white")
    tile.paste(image, (0, 0))
    ImageDraw.Draw(tile).multiline_text((8, image.height + 4), caption, fill="black", font=_font(17))
    return tile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("samples_dir", type=Path)
    parser.add_argument("--last", type=int, default=6, help="max steps per sheet (always keeps the first)")
    parser.add_argument("--steps", help="comma-separated steps to show, e.g. 0,150,250 (overrides --last)")
    args = parser.parse_args()
    steps = sorted(p for p in args.samples_dir.glob("step_*") if p.is_dir())
    if args.steps:
        wanted = {int(step) for step in args.steps.split(",")}
        steps = [p for p in steps if int(p.name.split("_")[1]) in wanted]
    elif len(steps) > args.last:
        steps = [steps[0], *steps[-(args.last - 1):]]
    stems = sorted({p.stem for step in steps for p in step.glob("*.json")})
    out_dir = args.samples_dir / "compare"
    out_dir.mkdir(exist_ok=True)
    for stem in stems:
        tiles = [_tile(step, stem) for step in steps if (step / f"{stem}.json").exists()]
        sheet = Image.new("RGB", (THUMB_W * len(tiles) + 10 * (len(tiles) - 1), max(t.height for t in tiles)), "#ddd")
        for i, tile in enumerate(tiles):
            sheet.paste(tile, (i * (THUMB_W + 10), 0))
        target = out_dir / f"{stem}.png"
        sheet.save(target)
        print(target)


if __name__ == "__main__":
    main()
