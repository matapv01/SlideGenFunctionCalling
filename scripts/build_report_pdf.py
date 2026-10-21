"""Render BAO_CAO_DAPO.md to a print-ready PDF (A4, numbered figures, one section per page).

Usage: /home/llm/MinhPV/.venvs/plot/bin/python scripts/build_report_pdf.py [--md BAO_CAO_DAPO.md] [--out docs/bao_cao/BAO_CAO_DAPO.pdf]
Needs `markdown` and `playwright` (Chromium) in the interpreter.
"""
import argparse
import re
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

CSS = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
:root { --ink:#1f2328; --muted:#57606a; --navy:#1B365D; --line:#d8dee4; --soft:#f3f6fa; --warm:#fbf6ec; }
html { font-family: "Noto Sans", sans-serif; font-size: 10.2pt; color: var(--ink); line-height: 1.5; background: #fff; }
body { margin: 0; }
.cover { height: 255mm; display: flex; flex-direction: column; justify-content: center; page-break-after: always;
         border-left: 6px solid var(--navy); padding-left: 14mm; }
.cover .kicker { letter-spacing: .25em; color: var(--muted); font-size: 9pt; }
.cover h1 { font-size: 27pt; line-height: 1.2; color: var(--navy); margin: 8mm 0 5mm; }
.cover .sub { font-size: 13pt; color: var(--muted); max-width: 150mm; }
.cover .meta { margin-top: 14mm; font-size: 10pt; color: var(--muted); }
.toc { page-break-after: always; }
.toc p { font-size: 12pt; line-height: 2.1; white-space: pre-line; }
h2 { page-break-before: always; color: var(--navy); font-size: 17pt; margin: 0 0 4mm; padding-bottom: 2mm;
     border-bottom: 2px solid var(--navy); }
.toc h2 { page-break-before: avoid; }
h3 { color: var(--navy); font-size: 12pt; margin: 6mm 0 2mm; page-break-after: avoid; }
p { margin: 2mm 0; }
p.lead { background: var(--soft); border-left: 4px solid var(--navy); padding: 3mm 4mm; font-size: 11pt; margin: 3mm 0 4mm; }
ul, ol { margin: 2mm 0; padding-left: 6mm; }
li { margin: 1mm 0; }
table { border-collapse: collapse; width: 100%; margin: 3mm 0 4mm; font-size: 8.8pt; page-break-inside: avoid; }
th { background: var(--navy); color: #fff; font-weight: 600; text-align: left; padding: 1.6mm 2mm; }
td { padding: 1.4mm 2mm; border-bottom: 1px solid var(--line); vertical-align: top; }
tr:nth-child(even) td { background: #fafbfc; }
figure { margin: 4mm 0 5mm; page-break-inside: avoid; text-align: center; }
img { max-width: 100%; }
figure img { max-height: 150mm; }
figcaption { font-size: 9pt; color: var(--muted); margin-top: 1.5mm; text-align: left; }
figcaption b { color: var(--navy); }
blockquote { margin: 4mm 0; padding: 3mm 4mm; background: var(--warm); border-left: 4px solid #d08b2c;
             page-break-inside: avoid; }
blockquote p { margin: 0; }
code { font-family: "Noto Sans Mono", monospace; font-size: 8.8pt; background: #f1f3f5; padding: 0 1mm; border-radius: 2px; }
hr { display: none; }
strong { color: #111; }
"""


def build_html(md_text: str) -> str:
    cover_md, toc_md, body_md = [part.strip() for part in md_text.split("\n---\n", 2)]
    lines = [line for line in cover_md.splitlines() if line.strip()]
    kicker, title, subtitle, meta = lines[0], lines[1].lstrip("# "), lines[2], lines[3]
    cover = (f'<section class="cover"><div class="kicker">{kicker}</div><h1>{title}</h1>'
             f'<div class="sub">{subtitle}</div><div class="meta">{meta}</div></section>')
    toc = '<section class="toc">' + markdown.markdown(toc_md) + "</section>"
    body = markdown.markdown(body_md, extensions=["tables", "sane_lists"])
    count = 0

    def figure(match: re.Match) -> str:
        nonlocal count
        count += 1
        tag = match.group(1)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        alt = re.search(r'alt="([^"]*)"', tag).group(1)
        return f'<figure><img src="{src}"><figcaption><b>Hình {count}.</b> {alt}</figcaption></figure>'

    body = re.sub(r"<p>(<img [^>]+>)</p>", figure, body)
    body = re.sub(r"<p><strong>(Kết luận[^<]*)</strong></p>", r'<p class="lead"><strong>\1</strong></p>', body)
    return (f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><base href="{ROOT.as_uri()}/">'
            f"<style>{CSS}</style></head><body>{cover}{toc}{body}</body></html>")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--md", type=Path, default=ROOT / "BAO_CAO_DAPO.md")
    parser.add_argument("--out", type=Path, default=ROOT / "docs" / "bao_cao" / "BAO_CAO_DAPO.pdf")
    args = parser.parse_args()
    html_path = args.out.with_suffix(".html")
    html_path.write_text(build_html(args.md.read_text(encoding="utf-8")), encoding="utf-8")
    footer = ('<div style="width:100%;font-family:Noto Sans;font-size:8px;color:#8b949e;padding:0 15mm;'
              'display:flex;justify-content:space-between"><span>DAPO cho SlideGen · bản 3</span>'
              '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.pdf(path=str(args.out), format="A4", print_background=True, display_header_footer=True,
                 header_template="<div></div>", footer_template=footer,
                 margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
        browser.close()
    print(f"wrote {args.out} ({args.out.stat().st_size / 1e6:.1f} MB) and {html_path.name}")


if __name__ == "__main__":
    main()
