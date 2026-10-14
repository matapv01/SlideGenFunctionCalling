"""Stack the per-slide comparison strips from sample_grid.py into a few sheets that are easy to read at once.

Usage: python scripts/sample_sheets.py <run_dir>/samples <out_prefix> [slides_per_sheet=6]
"""
import sys
from pathlib import Path

from PIL import Image

compare = sorted((Path(sys.argv[1]) / "compare").glob("*.png"))
per = int(sys.argv[3]) if len(sys.argv) > 3 else 6
for index in range(0, len(compare), per):
    strips = [Image.open(path) for path in compare[index:index + per]]
    width = max(strip.width for strip in strips)
    sheet = Image.new("RGB", (width, sum(strip.height for strip in strips) + 10 * len(strips)), "#888")
    y = 0
    for strip in strips:
        sheet.paste(strip, (0, y))
        y += strip.height + 10
    target = f"{sys.argv[2]}_{index // per + 1}.png"
    sheet.save(target)
    print(target)
