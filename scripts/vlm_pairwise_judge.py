#!/usr/bin/env python3
"""Pairwise VLM judge on the blind human-eval pairs, asked the same six questions the annotators answered.

Each pair is judged twice (A/B and swapped) to cancel position bias; the vote from DAPO's side is the mean of the two.
Talks to an OpenAI-compatible server (vllm serve ... --limit-mm-per-prompt '{"image": 2}').

Usage:
  python scripts/vlm_pairwise_judge.py --round 2 --out slidegen_data/annotation/vlm_judge/r2_qwen25vl32b.jsonl
  python scripts/vlm_pairwise_judge.py --round 1 --out slidegen_data/annotation/vlm_judge/r1_qwen25vl32b.jsonl
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import re
import subprocess
from pathlib import Path

from openai import AsyncOpenAI

ROOT = Path(__file__).resolve().parents[1]
ROUNDS = {
    # round 1's public pairs.json was replaced by round 2's; read it from the commit that deployed round 1.
    1: {"pairs": "git:c940f93c:annotation_web/public/data/pairs.json", "images": "slidegen_data/annotation/images_r1/img",
        "mapping": "slidegen_data/annotation/secret_mapping.json"},
    2: {"pairs": "annotation_web/public/data/pairs.json", "images": "slidegen_data/annotation/round2/images",
        "mapping": "slidegen_data/annotation/round2/secret_mapping.json"},
}
CRITERIA = ["faithful", "coverage", "language", "layout", "aesthetic", "overall"]

# Same wording as the annotation site (annotation_web/public/app.js), in Vietnamese like the annotators saw it.
PROMPT = """Bạn là người chấm slide thuyết trình tiếng Việt. Dưới đây là NỘI DUNG NGUỒN của một slide, rồi hai ảnh slide A và B
được tạo từ nguồn đó (ảnh thứ nhất là A, ảnh thứ hai là B). So sánh A với B theo 6 tiêu chí:

1. faithful – Trung thực với nguồn: ít thông tin sai/bịa hơn.
2. coverage – Đầy đủ, đúng trọng tâm: giữ được ý chính của nguồn.
3. language – Ngôn ngữ: chính tả, ngữ pháp, không ký tự lạ.
4. layout – Bố cục, khả năng đọc: không tràn/cắt/đè chữ, dễ đọc.
5. aesthetic – Thẩm mỹ: đẹp, chuyên nghiệp.
6. overall – Lựa chọn tổng thể: slide bạn sẽ dùng thật.

Với mỗi tiêu chí trả lời "A", "B" hoặc "tie" (chỉ chọn tie khi thật sự không phân biệt được).
Chỉ trả lời một đối tượng JSON, không giải thích:
{"faithful": "...", "coverage": "...", "language": "...", "layout": "...", "aesthetic": "...", "overall": "..."}

TIÊU ĐỀ BÀI: {title}
LOẠI SLIDE: {kind}
NỘI DUNG NGUỒN:
{text}"""


def load_pairs(spec: str) -> dict:
    if spec.startswith("git:"):
        _, rev, path = spec.split(":", 2)
        return json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", f"{rev}:{path}"]))
    return json.loads((ROOT / spec).read_text())


def data_url(path: Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


def parse(text: str) -> dict | None:
    match = re.search(r"\{.*?\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    answers = {c: str(payload.get(c, "")).strip().strip('"') for c in CRITERIA}
    answers = {c: "tie" if v.lower() == "tie" else v.upper() for c, v in answers.items()}
    return answers if all(v in {"A", "B", "tie"} for v in answers.values()) else None


async def ask(client: AsyncOpenAI, model: str, pair: dict, first: Path, second: Path) -> tuple[dict | None, str]:
    prompt = PROMPT.replace("{title}", pair.get("title", "")).replace("{kind}", pair.get("kind", "")).replace(
        "{text}", pair.get("text", ""))
    content = [{"type": "text", "text": prompt},
               {"type": "image_url", "image_url": {"url": data_url(first)}},
               {"type": "image_url", "image_url": {"url": data_url(second)}}]
    for _ in range(3):
        response = await client.chat.completions.create(model=model, messages=[{"role": "user", "content": content}],
                                                        temperature=0.0, max_tokens=200)
        raw = response.choices[0].message.content or ""
        answers = parse(raw)
        if answers:
            return answers, raw
    return None, raw


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=int, choices=sorted(ROUNDS), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--base-url", default="http://127.0.0.1:8004/v1")
    parser.add_argument("--model", default="qwen2.5-vl-32b")
    parser.add_argument("--concurrency", type=int, default=24)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    config = ROUNDS[args.round]
    mapping = json.loads((ROOT / config["mapping"]).read_text())["pairs"]
    images = ROOT / config["images"]
    pairs = [p for p in load_pairs(config["pairs"])["pairs"]
             if p["id"] in mapping and not mapping[p["id"]]["attention_check_of"]]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(line)["pair_id"] for line in args.out.read_text().splitlines()} if args.out.exists() else set()
    todo = [p for p in pairs if p["id"] not in done][: args.limit]
    missing = [p["id"] for p in todo if not (images / p["a"]).exists() or not (images / p["b"]).exists()]
    if missing:
        raise SystemExit(f"{len(missing)} pairs miss images, e.g. {missing[:3]}")
    print(f"round {args.round}: {len(pairs)} pairs, {len(done)} done, {len(todo)} to judge", flush=True)

    client, gate, out = AsyncOpenAI(base_url=args.base_url, api_key="local"), asyncio.Semaphore(args.concurrency), args.out.open("a")
    finished = 0

    async def judge(pair: dict) -> None:
        nonlocal finished
        async with gate:
            a, b = images / pair["a"], images / pair["b"]
            forward, raw_forward = await ask(client, args.model, pair, a, b)
            swapped, raw_swapped = await ask(client, args.model, pair, b, a)
        flip = {"A": "B", "B": "A", "tie": "tie"}
        record = {"pair_id": pair["id"], "model": args.model, "forward": forward,
                  "swapped": {c: flip[v] for c, v in swapped.items()} if swapped else None,
                  "raw": [raw_forward, raw_swapped]}
        out.write(json.dumps(record, ensure_ascii=False) + "\n")
        out.flush()
        finished += 1
        if finished % 50 == 0:
            print(f"{finished}/{len(todo)}", flush=True)

    await asyncio.gather(*(judge(p) for p in todo))
    out.close()
    print("done", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
