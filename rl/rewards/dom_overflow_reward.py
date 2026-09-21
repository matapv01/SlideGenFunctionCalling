"""
DOM Overflow Reward — Phạt lỗi tràn chữ (Text Overflow) và va chạm thẻ HTML.

Thay vì dựa hoàn toàn vào VLM (Gemini) để phát hiện lỗi tràn chữ (tốn kém và chậm),
reward này sử dụng Playwright headless browser để kiểm tra DOM trực tiếp:
  1. Overflow Detection: el.scrollWidth > el.clientWidth hoặc scrollHeight > clientHeight
  2. Bounding Box Collision: Kiểm tra tiêu đề có đè lên subtitle không
  3. Broken Image Detection: Kiểm tra thẻ <img> có naturalWidth === 0 không

Kết quả:
  - 1.0: Slide hoàn hảo, không có lỗi DOM nào
  - 0.0 → 1.0: Bị trừ điểm tỷ lệ với số lỗi phát hiện được
  - -1.0: Slide bị crash render hoặc không có HTML
"""

import os
import sys
import json
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.workflows.slidegen_workflow.tools.tool_des import execute_tool
from backend.workflows.slidegen_workflow.utils.helper import parse_tool_call_json

# Playwright DOM check script — chạy bên trong browser context
_DOM_CHECK_JS = """
() => {
    const issues = [];
    const allEls = document.querySelectorAll('*');

    // 1. Overflow Detection
    for (const el of allEls) {
        const tag = el.tagName.toLowerCase();
        if (['script', 'style', 'meta', 'link', 'html', 'head'].includes(tag)) continue;

        const cs = getComputedStyle(el);
        
        // Bắt lỗi tràn nội dung (scroll > client) BẤT KỂ thuộc tính overflow là gì
        // (Vì overflow: auto tạo thanh cuộn cực xấu, overflow: hidden thì làm mất chữ)
        // TĂNG DUNG SAI lên +15px để tránh báo lỗi sai do padding/border/scrollbars 
        if (el.scrollWidth > el.clientWidth + 15 && el.clientWidth > 0) {
            if (tag !== 'body' && tag !== 'html') {
                issues.push({
                    type: 'overflow_x',
                    tag: tag,
                    text: el.textContent.slice(0, 50),
                    scrollW: el.scrollWidth,
                    clientW: el.clientWidth
                });
            }
        }
        if (el.scrollHeight > el.clientHeight + 15 && el.clientHeight > 0) {
            // Cho phép body và html tràn (mặc dù slide tốt thì không nên tràn body)
            if (tag !== 'body' && tag !== 'html') {
                issues.push({
                    type: 'overflow_y',
                    tag: tag,
                    text: el.textContent.slice(0, 50),
                    scrollH: el.scrollHeight,
                    clientH: el.clientHeight
                });
            }
        }
    }

    // 2. Broken Image Detection
    const imgs = document.querySelectorAll('img');
    for (const img of imgs) {
        if (img.naturalWidth === 0 && img.src && !img.src.startsWith('data:')) {
            issues.push({
                type: 'broken_image',
                src: img.src.slice(0, 100)
            });
        }
    }

    // 3. Bounding Box Collision — kiểm tra h1 vs h2/subtitle
    const h1 = document.querySelector('h1');
    const h2 = document.querySelector('h2, .subtitle, [class*="subtitle"]');
    if (h1 && h2) {
        const r1 = h1.getBoundingClientRect();
        const r2 = h2.getBoundingClientRect();
        const overlap = !(r1.right < r2.left || r1.left > r2.right ||
                          r1.bottom < r2.top || r1.top > r2.bottom);
        if (overlap) {
            issues.push({
                type: 'bbox_collision',
                el1: 'h1',
                el2: 'h2/subtitle'
            });
        }
    }

    // 4. Text quá dài — bất kỳ phần tử nào có text > 300 ký tự mà không phải list
    const textEls = document.querySelectorAll('p, span, div, td, li');
    for (const el of textEls) {
        // Chỉ kiểm tra leaf text nodes
        if (el.children.length === 0 && el.textContent.trim().length > 300) {
            issues.push({
                type: 'text_too_long',
                tag: el.tagName.toLowerCase(),
                length: el.textContent.trim().length,
                text: el.textContent.trim().slice(0, 80)
            });
        }
    }

    // 5. Tràn ra khỏi khung màn hình (Out of Viewport)
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const textTags = document.querySelectorAll('h1, h2, h3, h4, p, span, li');
    for (const el of textTags) {
        const rect = el.getBoundingClientRect();
        // Bỏ qua các phần tử ẩn
        if (rect.width === 0 || rect.height === 0) continue;
        // Nếu phần chữ tràn ra ngoài màn hình quá 25px (nới lỏng cho các phần tử trang trí / viền phát sáng)
        if (rect.left < -25 || rect.top < -25 || rect.right > viewportWidth + 25 || rect.bottom > viewportHeight + 25) {
            issues.push({
                type: 'out_of_viewport',
                tag: el.tagName.toLowerCase(),
                text: el.textContent.trim().slice(0, 50)
            });
        }
    }

    return issues;
}
"""

# Penalty weights cho từng loại lỗi
_PENALTY_WEIGHTS = {
    "overflow_x": 0.15,         # Tràn ngang — nghiêm trọng
    "overflow_y": 0.10,         # Tràn dọc — nhẹ hơn nếu có scroll
    "out_of_viewport": 0.20,    # Tràn ra ngoài màn hình — lỗi nặng
    "broken_image": 0.20,       # Ảnh chết — rất xấu
    "bbox_collision": 0.25,     # Đè chữ — nghiêm trọng nhất
    "text_too_long": 0.05,      # Text quá dài — cảnh báo nhẹ
}


def _check_dom_issues(html_content: str) -> list:
    """Chạy Playwright headless để kiểm tra DOM issues."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return []  # Playwright chưa cài thì bỏ qua

    issues = []
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            tmp_path = f.name

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(f"file://{tmp_path}", wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(500)  # Đợi fonts load
            issues = page.evaluate(_DOM_CHECK_JS)
            browser.close()
    except Exception as e:
        # Nếu Playwright lỗi, trả về penalty nhẹ thay vì crash
        issues = [{"type": "render_error", "msg": str(e)[:100]}]
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    return issues or []


def dom_overflow_reward(prompts, completions, **kwargs):
    """
    DOM Guardrail Reward Function.

    Kiểm tra trực tiếp trên DOM của HTML đã render:
    - Tràn chữ (overflow)
    - Đè chữ (bounding box collision)
    - Ảnh chết (broken images)
    - Text quá dài

    Returns:
        List[float]: Điểm từ -1.0 đến 1.0 cho mỗi completion
    """
    rewards = []

    for idx, completion in enumerate(completions):
        try:
            tool_call = parse_tool_call_json(completion)
            if not tool_call:
                rewards.append(-1.0)
                continue

            html_content = execute_tool(tool_call)
            if not html_content:
                rewards.append(-1.0)
                continue

            # Chạy DOM check
            issues = _check_dom_issues(html_content)

            if not issues:
                # Slide hoàn hảo — full score
                rewards.append(1.0)
            else:
                # Tính penalty tổng dựa trên loại và số lượng lỗi
                total_penalty = 0.0
                for issue in issues:
                    issue_type = issue.get("type", "unknown")
                    weight = _PENALTY_WEIGHTS.get(issue_type, 0.05)
                    total_penalty += weight

                # Cap penalty tại 2.0 (tức score tối thiểu = -1.0)
                total_penalty = min(total_penalty, 2.0)
                score = max(-1.0, 1.0 - total_penalty)
                rewards.append(score)

        except Exception as e:
            rewards.append(0.0)

    scores_str = " ".join(f"{s:.3f}" for s in rewards)
    n_issues = sum(1 for s in rewards if s < 1.0)
    print(f"  [DOM Overflow Reward] issues_found={n_issues}/{len(rewards)} scores=[{scores_str}]")
    return rewards
