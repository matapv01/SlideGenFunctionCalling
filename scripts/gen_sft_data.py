"""
Generate SFT function-calling dataset using Gemini.

Output: rl/data/sft_function_call_dataset.json
"""

import os, sys, json, re, concurrent.futures, itertools, random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.helper import format_tool_for_qwen, QWEN_CHAT_TEMPLATE
from backend.workflows.slidegen_workflow.utils.prompts import (
    QWEN_GENERATOR_SYSTEM_PROMPT, QWEN_GENERATOR_HUMAN_TEMPLATE)

DOC_PROMPT = """Bạn là chuyên gia viết nội dung thuyết trình và thiết kế slide.

Viết bài TIẾNG VIỆT dài (1000-2500 từ) về chủ đề: {topic}

Tạo danh sách các slide (chunks) cho bài thuyết trình này. Mỗi slide gồm: heading, content, category, thought, tool_name, tool_args.

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
- tool_name: chọn 1 function name phù hợp từ danh sách theo category bên dưới
- tool_args: dict các tham số cho function đó (xem schema mẫu)
- KHÔNG lặp nội dung giữa các slide

CATEGORY_TOOLS:
{category_tools}

QUAN TRỌNG: Trước khi output, KIỂM TRA danh sách chunks của bạn. Đếm số lượng mỗi category.
Nếu thiếu bất kỳ category nào trong [INTRO_TOOLS, CONTENT_TOOLS, CHART_TOOLS, TEAM_TOOLS, TRANSITION_TOOLS, THANK_YOU_TOOLS], hãy THÊM slide phù hợp cho category đó.

JSON output:
{{
  "title": "Tiêu đề",
  "chunks": [
    {{
      "heading": "...",
      "content": "...",
      "category": "INTRO_TOOLS",
      "thought": "Thiết kế: ...",
      "tool_name": "generate_introduction_slide",
      "tool_args": {{"main_title": "...", "subtitle": "..."}}
    }}
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


def _format_category_tools():
    lines = []
    for cat, tools in TOOLS_DICT.items():
        sample = random.sample(tools, min(3, len(tools)))
        names = [t.name for t in tools]
        lines.append(f"\n{cat}: {', '.join(names)}")
        for t in sample:
            args_sample = json.dumps(t.args, ensure_ascii=False)[:250]
            lines.append(f"  - {t.name}: desc={t.description[:80]} | args={args_sample}")
    return "\n".join(lines)


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
    "Ngân hàng số và tương lai tài chính Việt Nam",
    "Bất động sản Việt Nam 2025: Cơ hội đầu tư",
    "Công nghiệp bán dẫn: Chiến lược phát triển của Việt Nam",
    "Thể thao điện tử Việt Nam trên trường quốc tế",
    "Khởi nghiệp công nghệ tại Việt Nam",
    "Bảo vệ dữ liệu cá nhân trong thời đại số",
    "Nông nghiệp thông minh và công nghệ IoT",
    "Du học và hợp tác giáo dục quốc tế",
    "Thương hiệu quốc gia Việt Nam thời kỳ hội nhập",
    "Phát triển hạ tầng giao thông đô thị tại Hà Nội",
    "Cách mạng công nghiệp 4.0 và thị trường lao động",
    "Bảo hiểm nhân thọ tại Việt Nam: Xu hướng mới",
    "Thị trường chứng khoán Việt Nam năm 2025",
    "Chuyển đổi số trong giáo dục phổ thông",
    "Phát triển bền vững và tín chỉ carbon",
    "Trí tuệ nhân tạo tạo sinh trong kinh doanh",
    "Logistics và chuỗi cung ứng thông minh",
    "Y học tái tạo và công nghệ tế bào gốc",
    "An ninh mạng trong kỷ nguyên IoT",
    "Thị trường game Việt Nam: Tiềm năng và thách thức",
    "Dịch vụ ăn uống và xu hướng F&B hiện đại",
    "Mỹ phẩm Việt: Từ nội địa ra toàn cầu",
    "Thời trang bền vững tại Việt Nam",
    "Công nghệ xử lý rác thải nhựa đại dương",
    "Trung tâm tài chính quốc tế tại TP. Hồ Chí Minh",
    "Năng lượng mặt trời tại Việt Nam: Hiện trạng và triển vọng",
    "Phát triển khu công nghiệp xanh",
    "Xe điện và hạ tầng trạm sạc tại Việt Nam",
    "Smart city và quản lý đô thị thông minh",
    "Kinh tế số và thương mại điện tử xuyên biên giới",
    "Công nghệ sinh học trong nông nghiệp",
    "Bảo tồn di sản văn hóa Việt Nam",
    "Phát triển du lịch sinh thái bền vững",
    "Thị trường fintech Việt Nam bùng nổ",
]


def _build_tool_call(chunk: dict) -> dict:
    """Build tool_call from chunk fields, looking up the tool by name."""
    name = chunk.get("tool_name", "")
    args = chunk.get("tool_args", {})
    return {"name": name, "arguments": args}


def _generate_one_doc(llm, topic: str, doc_id: int) -> list:
    cat_tools_str = _format_category_tools()
    prompt = DOC_PROMPT.format(topic=topic, category_tools=cat_tools_str)
    try:
        resp = llm.invoke(prompt)
        text = resp.content.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        obj = json.loads(text)
        title = obj.get("title", f"Chủ đề {doc_id+1}")
        chunks = obj.get("chunks", [])
        if not chunks:
            print(f"  Doc {doc_id}: 0 chunks")
            return []

        cats = set(c.get("category") for c in chunks)
        missing = {"INTRO_TOOLS", "CONTENT_TOOLS", "CHART_TOOLS", "TEAM_TOOLS", "TRANSITION_TOOLS", "THANK_YOU_TOOLS"} - cats
        if missing:
            print(f"  Doc {doc_id}: missing categories: {missing}")

        slides = []
        for si, chunk in enumerate(chunks):
            content = (chunk.get("content") or "").strip()
            if not content:
                continue
            category = chunk.get("category", "CONTENT_TOOLS")
            tc = _build_tool_call(chunk)
            slides.append({
                "category": category,
                "slide_content": content,
                "style_context": "No <b>, <i>, <em>, <strong>, <ul>, <ol>, <li> tags. Use <br> or <p> for line breaks.",
                "design_instruction": chunk.get("thought", f"Design brief for {category}: {chunk.get('heading', '')}"),
                "tool_call": tc,
                "doc_id": doc_id,
                "slide_index": si,
            })

        print(f"  Doc {doc_id}: '{title[:40]}...' → {len(slides)} slides | cats: {cats}")
        return slides
    except Exception as e:
        print(f"  Doc '{topic[:40]}' failed: {e}")
        return []


def generate_sft_data(num_docs: int = 49):
    llm = _get_llm()
    
    topics = TOPICS[:num_docs]
    if num_docs > len(topics):
        topics = topics * ((num_docs // len(topics)) + 1)
    topics = topics[:num_docs]
    
    print(f"Generating {num_docs} docs...")
    
    all_slides = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(_generate_one_doc, llm, t, i): i for i, t in enumerate(topics)}
        for f in concurrent.futures.as_completed(futures):
            idx = futures[f]
            slides = f.result()
            all_slides.extend(slides)
    
    all_slides.sort(key=lambda s: (s["doc_id"], s["slide_index"]))
    print(f"\nGenerated {len(all_slides)} total slides")
    return all_slides


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-docs", type=int, default=49)
    parser.add_argument("--output", type=str,
                        default=os.path.join(os.path.dirname(__file__), "..", "rl", "data", "sft_function_call_dataset.json"))
    args = parser.parse_args()
    
    data = generate_sft_data(args.num_docs)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(data)} samples to {args.output}")
