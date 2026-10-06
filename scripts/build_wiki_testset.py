"""Turn Vietnamese Wikipedia articles into topic-disjoint test decks by verbatim extraction.

No LLM rewrites the source: every slide_content sentence is copied from the article, so
faithfulness is judged against real text and no baseline model authored the inputs.

Usage: python scripts/build_wiki_testset.py slidegen_data/testset/wiki_articles.json \
           slidegen_data/testset/wiki_testset_rows.json
"""

import json
import re
import sys

SKIP_SECTIONS = re.compile(
    r"^(xem thêm|tham khảo|liên kết ngoài|chú thích|ghi chú|đọc thêm|thư mục|nguồn|"
    r"thư viện ảnh|hình ảnh|ảnh|tài liệu|tài liệu tham khảo|danh sách)\b",
    re.IGNORECASE,
)
TARGET_CHARS = 550
YEAR = re.compile(r"(?:1[0-9]|20)\d\d")
NUMBER = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)*\s*%?(?![\w])")


def _clean(text: str) -> str:
    text = re.sub(r"\[\d+\]|\[cần dẫn nguồn\]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{2,}", "\n", text).strip()


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZĐÀ-Ỹ0-9\"“(])", _clean(text).replace("\n", " "))
    return [part.strip() for part in parts if len(part.strip()) > 20]


def _take(text: str, limit: int = TARGET_CHARS) -> str:
    chosen, size = [], 0
    for sentence in _sentences(text):
        if chosen and size + len(sentence) > limit:
            break
        chosen.append(sentence)
        size += len(sentence) + 1
    return " ".join(chosen)


def _data_points(text: str) -> int:
    return sum(not YEAR.fullmatch(match.strip()) for match in NUMBER.findall(text))


def _sections(article_text: str) -> tuple[str, list[tuple[str, str]]]:
    """Use top-level sections; fall back to any heading level when an article has few of them."""
    lead = re.split(r"^=+\s*.*?\s*=+\s*$", article_text, maxsplit=1, flags=re.MULTILINE)[0]
    for pattern in (r"^==\s*([^=].*?)\s*==\s*$", r"^={2,4}\s*([^=].*?)\s*={2,4}\s*$"):
        parts = re.split(pattern, article_text, flags=re.MULTILINE)
        sections, skipping = [], False
        for heading, body in zip(parts[1::2], parts[2::2]):
            body = re.sub(r"^=+\s*.*?\s*=+\s*$", "", body, flags=re.MULTILINE)
            if SKIP_SECTIONS.match(heading):
                continue
            if len(_take(body)) >= 200:
                sections.append((heading, body))
        if len(sections) >= 4:
            return lead, sections
    return lead, sections


def build_deck(article: dict, doc_id: int) -> list[dict] | None:
    lead, sections = _sections(article["text"])
    intro = _take(lead)
    if len(intro) < 200 or len(sections) < 4:
        return None
    chart_index = max(range(len(sections)), key=lambda i: _data_points(_take(sections[i][1])))
    chart = sections[chart_index] if _data_points(_take(sections[chart_index][1])) >= 3 else None
    content = [section for i, section in enumerate(sections) if chart is None or i != chart_index][:4]

    slides = [("INTRO_TOOLS", article["title"], intro)]
    outline = "; ".join(heading for heading, _ in content + ([chart] if chart else []))
    slides.append(("TRANSITION_TOOLS", "Nội dung chính", f"Bài trình bày về {article['title']} gồm các phần: {outline}."))
    slides += [("CONTENT_TOOLS", heading, _take(body)) for heading, body in content]
    if chart:
        slides.append(("CHART_TOOLS", chart[0], _take(chart[1])))
    slides.append(("THANK_YOU_TOOLS", "Cảm ơn", f"Cảm ơn quý vị đã theo dõi phần trình bày về {article['title']}."))
    return [
        {
            "doc_id": doc_id,
            "slide_index": index,
            "category": category,
            "slide_content": f"{heading}\n{body}",
            "style_context": "",
            "design_instruction": "",
            "source": {"title": article["title"], "url": article["url"], "revid": article["revid"],
                       "domain": article["domain"], "license": "CC BY-SA 4.0"},
        }
        for index, (category, heading, body) in enumerate(slides)
    ]


def main() -> None:
    articles = json.load(open(sys.argv[1], encoding="utf-8"))
    rows, skipped = [], []
    for offset, article in enumerate(articles):
        deck = build_deck(article, 1000 + offset)
        if deck is None:
            skipped.append(article["title"])
        else:
            rows.extend(deck)
    json.dump(rows, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    decks = len({row["doc_id"] for row in rows})
    print(f"decks {decks} | slides {len(rows)} | skipped {skipped}")


if __name__ == "__main__":
    main()
