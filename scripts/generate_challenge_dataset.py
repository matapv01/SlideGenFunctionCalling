import os
import sys
import json
import concurrent.futures
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

DOC_PROMPT = """Bạn là chuyên gia viết nội dung thuyết trình và thiết kế slide.

Viết bài TIẾNG VIỆT dài (1000-2500 từ) về chủ đề: {topic}

Tạo danh sách các slide (chunks) cho bài thuyết trình này. Mỗi slide gồm: heading, content, category, thought.

DANH SÁCH CATEGORY BẮT BUỘC — tất cả 6 category này ĐỀU phải xuất hiện trong chunks:
- INTRO_TOOLS (1 slide): Mở đầu, giới thiệu chủ đề, bối cảnh, mục tiêu
- CONTENT_TOOLS (ít nhất 3 slide): Nội dung chính — phân tích, mô tả, giải thích, luận điểm (thuần nội dung, không yêu cầu số liệu)
- CHART_TOOLS (1 slide): Số liệu thô, bảng thống kê, so sánh %, tăng trưởng — PHẢI có dữ liệu số cụ thể
- TEAM_TOOLS (1 slide): Đội ngũ — PHẢI liệt kê từng người (tên + chức vụ + mô tả)
- TRANSITION_TOOLS (1 slide): Câu chuyển ý ngắn gọn
- THANK_YOU_TOOLS (1 slide): Cảm ơn + email, hotline, website, địa chỉ

YÊU CẦU NỘI DUNG:
- Mỗi slide 3-7 câu
- CONTENT_TOOLS: nội dung thuần — phân tích, giải thích, mô tả (có thể có số liệu nhưng không bắt buộc)
- CHART_TOOLS: số liệu thô — %, tỷ VNĐ, số lượng, so sánh theo quý/năm, so đối thủ
- TEAM_TOOLS: danh sách 3-5 người với tên đầy đủ + chức vụ + mô tả
- THANK_YOU_TOOLS: email, số điện thoại, website, địa chỉ cụ thể
- thought: mô tả THIẾT KẾ cho slide (màu sắc, layout, font) — không phải heading
- KHÔNG lặp nội dung giữa các slide

QUAN TRỌNG: Trước khi output, KIỂM TRA danh sách chunks của bạn. Đếm số lượng mỗi category.
Nếu thiếu bất kỳ category nào trong [INTRO_TOOLS, CONTENT_TOOLS, CHART_TOOLS, TEAM_TOOLS, TRANSITION_TOOLS, THANK_YOU_TOOLS], hãy THÊM slide phù hợp cho category đó.

JSON output:
{{
  "title": "Tiêu đề",
  "chunks": [
    {{"heading": "...", "content": "...", "category": "INTRO_TOOLS", "thought": "Mô tả thiết kế: ..."}},
    {{"heading": "...", "content": "...", "category": "TEAM_TOOLS", "thought": "Thiết kế dạng grid 3 cột..."}}
  ]
}}
"""


def _get_llm():
    return ChatOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
        model=os.getenv("GEMINI_GENERATION_MODEL", "gemini-2.5-pro"),
        temperature=0.8, max_tokens=32768,
    )


def _generate_one_doc(llm, topic: str) -> dict:
    prompt = DOC_PROMPT.format(topic=topic)
    try:
        resp = llm.invoke(prompt)
        text = resp.content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        print(f"  Doc '{topic[:40]}' failed: {e}")
        return {"title": topic[:60], "chunks": []}


TOPICS = [
    "FPT Corporation và hành trình chuyển đổi số toàn cầu",
    "VinFast: Từ startup ô tô Việt đến thương hiệu xe điện quốc tế",
    "Chiến dịch Điện Biên Phủ 1954 và ý nghĩa lịch sử",
    "Vịnh Hạ Long: Kỳ quan thiên nhiên thế giới",
    "Công nghệ AI trong y tế: Cơ hội và thách thức",
    "Giáo dục đại học Việt Nam thời kỳ hội nhập",
    "Năng lượng tái tạo: Giải pháp cho tương lai bền vững",
    "Blockchain và tiềm năng ứng dụng tại Việt Nam",
    "Du lịch Việt Nam sau đại dịch",
    "Văn hóa ẩm thực ba miền Bắc - Trung - Nam",
    "Viettel và cuộc cách mạng viễn thông số",
    "Cà phê Việt Nam trên thị trường quốc tế",
    "Tác động của biến đổi khí hậu đến đồng bằng sông Cửu Long",
    "Thương mại điện tử Việt Nam: Thực trạng và xu hướng",
    "Phát triển đô thị thông minh tại TP. Hồ Chí Minh",
]


def generate_docs(num_docs: int) -> list:
    llm = _get_llm()

    topics = TOPICS[:num_docs]
    if num_docs > len(topics):
        topics = topics * ((num_docs // len(topics)) + 1)
    topics = topics[:num_docs]

    print(f"Generating {num_docs} docs (1 call/topic)...")
    docs_raw = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(_generate_one_doc, llm, t): i for i, t in enumerate(topics)}
        for f in concurrent.futures.as_completed(futures):
            docs_raw.append((futures[f], f.result()))
    docs_raw.sort(key=lambda x: x[0])
    docs_raw = [d[1] for d in docs_raw]

    result = []
    for doc_id, doc in enumerate(docs_raw):
        title = doc.get("title", f"Chủ đề {doc_id+1}")
        chunks = doc.get("chunks", [])
        if not chunks:
            print(f"  [WARN] Doc {doc_id}: '{title[:40]}' has 0 chunks, skipping")
            continue

        cats = set(c.get("category") for c in chunks)
        missing = {"INTRO_TOOLS", "CONTENT_TOOLS", "CHART_TOOLS", "TEAM_TOOLS", "TRANSITION_TOOLS", "THANK_YOU_TOOLS"} - cats
        if missing:
            print(f"  [WARN] Doc {doc_id}: missing categories: {missing}")

        slides = []
        for si, chunk in enumerate(chunks):
            content = chunk.get("content", "").strip()
            if not content:
                continue
            category = chunk.get("category", "CONTENT_TOOLS")
            slides.append({
                "doc_id": doc_id,
                "slide_index": si,
                "title": title,
                "heading": chunk.get("heading", ""),
                "user_prompt": content,
                "plan": {
                    "action": category,
                    "thought": chunk.get("thought", f"Design brief for {category} slide: {chunk.get('heading', '')}"),
                },
            })

        result.append(slides)
        print(f"  Doc {doc_id}: '{title[:40]}...' → {len(slides)} slides | cats: {cats}")

    total_slides = sum(len(s) for s in result)
    print(f"Generated {len(result)} docs, {total_slides} total slides.")
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    docs = generate_docs(args.limit)
    all_slides = [s for d in docs for s in d]

    out = os.path.join(os.path.dirname(__file__), "..", "rl", "data", "slidegen_challenge_dataset.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_slides, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_slides)} slides to {out}")
