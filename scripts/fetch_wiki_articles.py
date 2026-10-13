"""Fetch Vietnamese Wikipedia articles (plain text + revision id) for a topic-disjoint test set.

Usage: python scripts/fetch_wiki_articles.py <titles.json> <out_articles.json>
titles.json maps a domain name to a list of article titles.
"""

import json
import sys
import time
import urllib.parse

import requests

API = "https://vi.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "SlideGenResearch/1.0 (academic evaluation set; contact via repository)"}


def fetch(title: str) -> dict | None:
    params = {"action": "query", "format": "json", "prop": "extracts|revisions|info", "explaintext": 1,
              "exsectionformat": "wiki", "redirects": 1, "rvprop": "ids", "inprop": "url", "titles": title}
    for attempt in range(4):
        response = requests.get(API, params=params, headers=HEADERS, timeout=60)
        if response.ok:
            page = next(iter(response.json()["query"]["pages"].values()))
            if "missing" in page or not page.get("extract"):
                return None
            return {"query": title, "title": page["title"], "revid": page["revisions"][0]["revid"],
                    "url": "https://vi.wikipedia.org/wiki/" + urllib.parse.quote(page["title"].replace(" ", "_")),
                    "text": page["extract"]}
        time.sleep(3 * (attempt + 1))
    return None


def main() -> None:
    titles = json.load(open(sys.argv[1], encoding="utf-8"))
    articles, missing = [], []
    for domain, names in titles.items():
        for name in names:
            article = fetch(name)
            if article is None:
                missing.append(name)
                continue
            articles.append({"domain": domain, **article})
            time.sleep(0.3)
    json.dump(articles, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"fetched {len(articles)} | missing {missing}")


if __name__ == "__main__":
    main()
