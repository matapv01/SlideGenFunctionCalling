"""
========================================================================================
🎨 SCRIPT PREVIEW SLIDE THEO DOCUMENT (Doc-level Generator 🔄 Executor Preview)
========================================================================================
Chạy luồng sinh toàn bộ các slide thuộc cùng 1 Document liên tiếp:
1. Truyền style_context / previous_accepted_tool_call xuyên suốt giữa các slide trong doc.
2. Sử dụng RemoteLLMProvider (FastAPI) hoặc config tương tự test_generator_executor_loop.py.
3. Xuất ra 2 định dạng xem trước:
   - 🌐 Web Preview tương tác: preview_runs/doc_<id>/index.html (có sidebar chọn slide, scaler 1920x1080)
   - 🖼️ Ảnh ghép tổng thể Contact Sheet: preview_runs/doc_<id>/overview.png
4. Tự động mở trình duyệt hiển thị kết quả cho người dùng.

📌 Ví dụ sử dụng:
    # Xem toàn bộ slide của Document 0 (Mặc định):
    python scripts/preview_doc_slides.py --doc 0

    # Xem Document khác (ví dụ Doc 1, Doc 2):
    python scripts/preview_doc_slides.py --doc 1

    # Tùy chỉnh số lần thử lại tối đa (mặc định 5):
    python scripts/preview_doc_slides.py --doc 0 --max-retries 3
========================================================================================
"""

import os
import sys
import json
import time
import webbrowser
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
load_dotenv()

from backend.infrastructure.rag.gemini_provider import GeminiToolRetrieveProvider
from backend.workflows.slidegen_workflow.nodes.slide_generator import generate_slide
from backend.workflows.slidegen_workflow.nodes.tool_call_executor import tool_call_executor
from backend.workflows.slidegen_workflow.utils.helper import render_html_to_png
from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend import config as backend_config
from rl.run_artifacts import save_contact_sheet

from backend.infrastructure.llm_providers import (
    RemoteLLMProvider,
    GeminiAPIProvider,
    NvidiaQwenLLMProvider,
)


def load_dataset():
    paths = [
        os.path.join("rl", "data", "sft_function_call_dataset.json"),
        os.path.join("rl", "data", "dataset_with_candidate_tools.json"),
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f), p
    raise FileNotFoundError("Không tìm thấy file dataset sft_function_call_dataset.json")


def generate_web_preview_html(output_dir: Path, doc_id: int, slide_meta_list: list) -> Path:
    """Tạo giao diện web tương tác để xem danh sách slide dạng trình chiếu 1920x1080."""
    index_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Slide Preview - Document #{doc_id}</title>
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; margin: 0; padding: 0; height: 100vh; overflow: hidden; background: #18181b; color: #f4f4f5; }}
#sidebar {{ width: 380px; background: #27272a; border-right: 1px solid #3f3f46; display: flex; flex-direction: column; }}
.sidebar-header {{ padding: 18px 20px; border-bottom: 1px solid #3f3f46; background: #202023; }}
.sidebar-header h2 {{ margin: 0 0 6px 0; font-size: 18px; color: #38bdf8; display: flex; align-items: center; gap: 8px; }}
.sidebar-header p {{ margin: 0; font-size: 13px; color: #a1a1aa; }}
#slide-list {{ list-style: none; padding: 12px; margin: 0; overflow-y: auto; flex: 1; }}
li {{ margin-bottom: 10px; }}
a.slide-item {{
    text-decoration: none; color: inherit; display: block; padding: 12px 14px;
    border-radius: 8px; background: #3f3f46; border: 1px solid #52525b;
    transition: all 0.2s ease; cursor: pointer;
}}
a.slide-item:hover {{ background: #52525b; border-color: #38bdf8; }}
a.slide-item.active {{ background: #0284c7; border-color: #38bdf8; box-shadow: 0 4px 12px rgba(2,132,199,0.3); }}
.slide-idx {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.8; margin-bottom: 4px; font-weight: bold; }}
.slide-tool {{ font-size: 14px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.slide-category {{ font-size: 11px; margin-top: 4px; color: #cbd5e1; }}
#content {{ flex: 1; display: flex; flex-direction: column; background: #09090b; }}
.topbar {{ background: #18181b; padding: 12px 24px; border-bottom: 1px solid #27272a; display: flex; justify-content: space-between; align-items: center; }}
.topbar h3 {{ margin: 0; font-size: 16px; color: #fafafa; }}
.topbar-actions a {{ color: #38bdf8; text-decoration: none; font-size: 13px; background: #27272a; padding: 6px 12px; border-radius: 6px; border: 1px solid #3f3f46; margin-left: 8px; }}
.topbar-actions a:hover {{ background: #3f3f46; }}
.iframe-wrapper {{ flex: 1; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
.scaler {{ width: 1920px; height: 1080px; position: absolute; left: 50%; top: 50%; transform-origin: center center; background: white; box-shadow: 0 20px 50px rgba(0,0,0,0.8); border-radius: 4px; overflow: hidden; }}
iframe {{ width: 1920px; height: 1080px; border: none; }}
</style>
</head>
<body>
<div id="sidebar">
    <div class="sidebar-header">
        <h2>📑 Document #{doc_id}</h2>
        <p>Tổng cộng: {len(slide_meta_list)} slides | Generated by SlideGen</p>
    </div>
    <ul id="slide-list">
"""

    for i, item in enumerate(slide_meta_list):
        active_cls = " active" if i == 0 else ""
        index_html += f"""
        <li>
            <a href="{item['file_name']}" class="slide-item{active_cls}" onclick="loadSlide(this, '{item['file_name']}', '{item['tool_name']}'); return false;">
                <div class="slide-idx">SLIDE {item['slide_index'] + 1} / {len(slide_meta_list)} ({item['attempts']} attempt)</div>
                <div class="slide-tool">🛠️ {item['tool_name']}</div>
                <div class="slide-category">🏷️ {item['category']}</div>
            </a>
        </li>
"""

    first_file = slide_meta_list[0]['file_name'] if slide_meta_list else ""
    first_tool = slide_meta_list[0]['tool_name'] if slide_meta_list else ""

    index_html += f"""
    </ul>
</div>
<div id="content">
    <div class="topbar">
        <h3 id="current-slide-title">🛠️ {first_tool}</h3>
        <div class="topbar-actions">
            <a href="overview.png" target="_blank">🖼️ Xem Ảnh Lưới Overview</a>
            <a id="open-raw-link" href="{first_file}" target="_blank">🔍 Mở HTML Gốc</a>
        </div>
    </div>
    <div class="iframe-wrapper">
        <div class="scaler" id="scaler">
            <iframe id="preview_frame" src="{first_file}"></iframe>
        </div>
    </div>
</div>

<script>
function resizeScaler() {{
    var wrapper = document.querySelector('.iframe-wrapper');
    var scaler = document.getElementById('scaler');
    if (!wrapper || !scaler) return;
    var w = wrapper.clientWidth - 40;
    var h = wrapper.clientHeight - 40;
    var scale = Math.min(w / 1920, h / 1080);
    scaler.style.transform = 'translate(-50%, -50%) scale(' + scale + ')';
}}
window.addEventListener('resize', resizeScaler);
window.addEventListener('DOMContentLoaded', resizeScaler);

function loadSlide(element, url, title) {{
    document.querySelectorAll('.slide-item').forEach(el => el.classList.remove('active'));
    element.classList.add('active');
    document.getElementById('preview_frame').src = url;
    document.getElementById('current-slide-title').innerText = '🛠️ ' + title;
    document.getElementById('open-raw-link').href = url;
    resizeScaler();
}}
</script>
</body>
</html>
"""
    preview_index_path = output_dir / "index.html"
    with open(preview_index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    return preview_index_path


def main():
    parser = argparse.ArgumentParser(description="Preview Slide Generation by Document")
    parser.add_argument("--doc", type=int, default=None, help="Document ID to preview (single doc)")
    parser.add_argument("--start-doc", type=int, default=None, help="Start document ID (range)")
    parser.add_argument("--end-doc", type=int, default=None, help="End document ID (range, inclusive)")
    parser.add_argument("--max-retries", type=int, default=backend_config.EXECUTOR_MAX_RETRIES, help="Max retry attempts per slide")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open web browser")
    args = parser.parse_args()

    dataset, data_file = load_dataset()
    available_docs = sorted(list(set(s.get("doc_id") for s in dataset if s.get("doc_id") is not None)))

    # Xác định danh sách các document cần chạy
    if args.start_doc is not None and args.end_doc is not None:
        target_docs = [d for d in available_docs if args.start_doc <= d <= args.end_doc]
    elif args.doc is not None:
        target_docs = [args.doc] if args.doc in available_docs else []
    else:
        # Mặc định doc đầu tiên
        target_docs = [0] if 0 in available_docs else available_docs[:1]

    if not target_docs:
        print(f"❌ Không tìm thấy document hợp lệ!")
        print(f"👉 Các Document hiện có trong dataset: {available_docs}")
        return

    print("=" * 80)
    print(f"🎬 BẮT ĐẦU CHẠY PREVIEW CHO {len(target_docs)} DOCUMENT(S): {target_docs}")
    print(f"📂 Nguồn dữ liệu: {data_file}")
    print("=" * 80)

    # 1. Initialize tool_retriever
    tool_retriever = None
    try:
        gemini_key = os.environ.get("GEMINI_API_KEY")
        faiss_index_path = getattr(backend_config, "FAISS_INDEX_PATH", "faiss_tool_retriever_index")
        tool_retriever = GeminiToolRetrieveProvider(
            tools_dict=TOOLS_DICT,
            index_path=faiss_index_path,
            api_key=gemini_key
        )
        print("🔍 ToolRetriever initialized successfully!")
    except Exception as e:
        print(f"⚠️ ToolRetriever info: {e}. (Falling back to category tool list)")

    # 2. Initialize LLM Provider (Same as test_generator_executor_loop.py)
    use_remote = os.environ.get("USE_REMOTE_API", "true").lower() == "true"
    use_gemini = os.environ.get("USE_GEMINI", "false").lower() == "true"
    
    if use_remote:
        print("🤖 Using RemoteLLMProvider (FastAPI Server)")
        llm = RemoteLLMProvider()
    elif use_gemini:
        print("🤖 Using GeminiAPIProvider")
        llm = GeminiAPIProvider(
            api_keys=os.environ.get("GEMINI_API_KEY"),
            base_url=os.environ.get("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
            model=os.environ.get("GEMINI_GENERATION_MODEL", "gemini-2.5-flash")
        )
    else:
        print("🤖 Using NvidiaQwenLLMProvider")
        model_name = os.environ.get("OPENAI_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
        api_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("OPENAI_API_KEY")
        llm = NvidiaQwenLLMProvider(model_name=model_name, base_url=base_url, api_key=api_key)

    config = {
        "configurable": {
            "llm": llm,
            "planner_llm": llm,
            "tools_dict": TOOLS_DICT,
            "tool_retriever": tool_retriever,
        },
        "verbose": False
    }

    # Chuẩn bị lưu kết quả của tất cả các documents
    last_web_preview_path = None

    for current_doc_id in target_docs:
        doc_slides = [s for s in dataset if s.get("doc_id") == current_doc_id]
        doc_slides.sort(key=lambda s: s.get("slide_index", 0))

        print("\n" + "=" * 80)
        print(f"📁 [DOCUMENT #{current_doc_id}] — Tổng cộng: {len(doc_slides)} slides")
        print("=" * 80)

        # Prepare output preview directory for this doc
        preview_output_dir = Path("preview_runs") / f"doc_{current_doc_id}"
        preview_output_dir.mkdir(parents=True, exist_ok=True)

        previous_accepted_tool_call = {}
        rendered_png_paths = []
        slide_meta_list = []

        # 3. Sequential slide generation with style context propagation
        for si, sample in enumerate(doc_slides):
            slide_idx = sample.get("slide_index", si)
            category = sample.get("category", "CONTENT_TOOLS")
            sample_thought = sample.get("thought") or sample.get("slide_content", "")[:300]

            print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"🖥️ SLIDE {si + 1}/{len(doc_slides)} (Doc #{current_doc_id}, Slide #{slide_idx}) — Category: {category}")
            print(f"   Content snippet: {sample.get('slide_content', '')[:90]}...")

            state = {
                "current_slide_index": slide_idx,
                "last_processed_slide_index": -1,
                "length_slide_chunks": len(doc_slides),
                "current_slide_text": sample.get("slide_content", ""),
                "current_slide_plan": {
                    "action": category,
                    "thought": sample_thought
                },
                "current_slide_context_map": sample.get("style_context", ""),
                "design_instruction": sample.get("design_instruction", ""),
                "previous_accepted_tool_call": previous_accepted_tool_call,  # 🎯 Context từ slide trước
                "use_cot": True,
                "retry_count": 0,
                "executor_feedback": "",
                "executor_decision": "fail"
            }

            # Attempt loop
            t0 = time.time()
            final_html = ""
            predicted_tool_name = "default_fallback"
            success_attempt = 1

            for attempt in range(1, args.max_retries + 1):
                success_attempt = attempt
                print(f"  -> Attempt {attempt}/{args.max_retries}...")
                
                # Node 1: Generator
                state = generate_slide(state, config)
                tool_call = state.get("current_tool_call", {})
                predicted_tool_name = tool_call.get("name", "NO_CALL")
                
                # Node 2: Executor
                state = tool_call_executor(state, config)
                decision = state.get("executor_decision")

                if decision == "pass":
                    final_html = state.get("current_html_content", "")
                    previous_accepted_tool_call = tool_call  # Cập nhật style context cho slide kế tiếp
                    print(f"  ✅ PASS! Tool: '{predicted_tool_name}' ({time.time() - t0:.1f}s)")
                    break
                else:
                    print(f"  ❌ FAIL attempt {attempt} — Feedback: {state.get('executor_feedback', '')[:70]}...")

            # Save individual HTML file
            html_file_name = f"slide_{slide_idx:02d}_{predicted_tool_name}.html"
            html_file_path = preview_output_dir / html_file_name
            with open(html_file_path, "w", encoding="utf-8") as f_html:
                f_html.write(final_html or "<h1>Slide Generation Failed</h1>")

            # Render PNG for contact sheet
            png_file_name = f"slide_{slide_idx:02d}.png"
            png_file_path = preview_output_dir / png_file_name
            if final_html:
                try:
                    render_html_to_png(final_html, str(png_file_path))
                    if png_file_path.exists():
                        rendered_png_paths.append(png_file_path)
                except Exception as e:
                    print(f"  ⚠️ Render PNG failed: {e}")

            slide_meta_list.append({
                "slide_index": slide_idx,
                "tool_name": predicted_tool_name,
                "category": category,
                "attempts": success_attempt,
                "file_name": html_file_name,
            })

        # 4. Create Overview Contact Sheet (Ảnh ghép lưới tổng thể)
        overview_img_path = preview_output_dir / "overview.png"
        if rendered_png_paths:
            print(f"\n🎨 Đang tạo ảnh ghép Contact Sheet cho {len(rendered_png_paths)} slides...")
            save_contact_sheet(
                rendered_png_paths,
                str(overview_img_path),
                title=f"Doc #{current_doc_id} Presentation Overview",
                subtitle=f"Generated {len(slide_meta_list)} slides with continuous style context",
                columns=min(4, len(rendered_png_paths)),
                thumb_size=(420, 236)
            )
            print(f"  🖼️ Ảnh tổng quan đã lưu: {overview_img_path}")

        # 5. Create Interactive Web Preview
        web_preview_path = generate_web_preview_html(preview_output_dir, current_doc_id, slide_meta_list)
        last_web_preview_path = web_preview_path
        print(f"  🌐 Web Preview HTML đã lưu: {web_preview_path}")

    # 6. Automatically open browser for the last generated doc
    if not args.no_browser and last_web_preview_path:
        print("\n🚀 Đang mở trình duyệt để xem trước slide...")
        webbrowser.open(last_web_preview_path.resolve().as_uri())

    print("\n" + "=" * 80)
    print(f"🎉 HOÀN TẤT TẤT CẢ {len(target_docs)} DOCUMENT(S)!")
    print(f"📂 Xem toàn bộ các documents tại thư mục: preview_runs/")
    print("=" * 80)


if __name__ == "__main__":
    main()
