"""RL-facing adapter for the XML-only SlideGen pipeline.

Compatibility stays here instead of re-introducing the removed HTML API into
backend, which remains aligned with minh_dep.
"""

from __future__ import annotations

import asyncio
import json
import os
from copy import deepcopy
from pathlib import Path

from backend.infrastructure.capture.playwright_provider import PlaywrightCaptureProvider
from backend.workflows.slidegen_workflow.tools.tool_des_xml import (
    TOOLS_DICT,
    execute_tool as _execute_xml_tool,
)
from backend.workflows.slidegen_workflow.utils.helper import parse_tool_call_json
from backend.workflows.slidegen_workflow.utils.prompts import (
    HUMAN_PROMPT_TEMPLATE,
    MATH_EQUATION_RULES,
    XML_CONTENT_PROMPT,
)


def execute_tool(tool_call: dict) -> str:
    """Execute one XML tool call and surface invalid calls to reward functions."""
    return _execute_xml_tool(tool_call, raise_on_error=True)


_DOM_METRICS_SCRIPT = r"""() => {
  const canvas = document.querySelector('[data-xml-slide-canvas="true"]');
  if (!canvas) throw new Error("XML slide canvas was not found in frontend preview");
  const canvasRect = canvas.getBoundingClientRect();
  const logicalWidth = canvas.offsetWidth || canvasRect.width || 1;
  const logicalHeight = canvas.offsetHeight || canvasRect.height || 1;
  const scaleX = canvasRect.width / logicalWidth || 1;
  const scaleY = canvasRect.height / logicalHeight || 1;
  const toX = value => value / scaleX;
  const toY = value => value / scaleY;
  const tolerance = 1.5;
  const union = rects => rects.length ? rects.reduce((result, rect) => ({
    left: Math.min(result.left, rect.left), top: Math.min(result.top, rect.top),
    right: Math.max(result.right, rect.right), bottom: Math.max(result.bottom, rect.bottom),
  }), {left: rects[0].left, top: rects[0].top,
      right: rects[0].right, bottom: rects[0].bottom}) : null;
  const lineCount = rects => {
    const tops = [];
    for (const rect of rects) {
      if (!tops.some(top => Math.abs(top - rect.top) <= 2)) tops.push(rect.top);
    }
    return tops.length;
  };
  const boxes = Array.from(document.querySelectorAll('[data-xml-textbox="true"]'))
    .map(box => {
      const content = box.querySelector('[data-xml-text-content="true"]');
      if (!content || !content.textContent?.trim()) return null;
      const rect = box.getBoundingClientRect();
      const textRects = [];
      const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT);
      let node = walker.nextNode();
      while (node) {
        if (node.textContent?.trim()) {
          const range = document.createRange();
          range.selectNodeContents(node);
          textRects.push(...Array.from(range.getClientRects()));
        }
        node = walker.nextNode();
      }
      const visibleRects = textRects.filter(item => item.width > 0 && item.height > 0);
      const textRect = union(visibleRects);
      const reasons = [];
      if (rect.left < canvasRect.left - tolerance || rect.top < canvasRect.top - tolerance ||
          rect.right > canvasRect.right + tolerance || rect.bottom > canvasRect.bottom + tolerance) {
        reasons.push('slide_boundary');
      }
      if (textRect && (textRect.left < rect.left - tolerance || textRect.right > rect.right + tolerance)) {
        reasons.push('text_width');
      }
      if (textRect && (textRect.top < rect.top - tolerance || textRect.bottom > rect.bottom + tolerance)) {
        reasons.push('text_height');
      }
      const maxLinesValue = box.getAttribute('data-xml-max-lines');
      const maxLines = maxLinesValue ? Number(maxLinesValue) : null;
      const lines = lineCount(visibleRects);
      if (maxLines && lines > maxLines) reasons.push('max_lines');
      return {
        id: box.getAttribute('data-xml-element-id') || 'textbox',
        text: content.innerText || content.textContent || '',
        x: toX(rect.left - canvasRect.left), y: toY(rect.top - canvasRect.top),
        width: toX(rect.width), height: toY(rect.height), reasons,
      };
    }).filter(Boolean);
  const issues = boxes.flatMap(box => box.reasons.map(type => ({type, textbox: box.id})));
  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], b = boxes[j];
      const width = Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x);
      const height = Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y);
      const smaller = Math.min(a.width * a.height, b.width * b.height);
      if (width > 0 && height > 0 && smaller > 0 && width * height / smaller > 0.05) {
        issues.push({type: 'bbox_collision', textbox: a.id, other: b.id});
      }
    }
  }
  const accessibleText = Array.from(
    document.querySelectorAll('[role="img"][aria-label], math-span[aria-label]')
  ).map(node => node.getAttribute('aria-label') || '').filter(Boolean);
  const imageStatus = Array.from(canvas.querySelectorAll('img')).map(image => ({
    loaded: image.complete && image.naturalWidth > 0,
  }));
  return {
    visible_text: [...boxes.map(box => box.text).filter(Boolean), ...accessibleText].join(' '),
    issues,
    image_status: imageStatus,
  };
}"""


def render_xml_batch_to_png(
    xml_contents: list[str],
    output_paths: list[str],
    max_concurrency: int = 4,
) -> list[dict]:
    """Render and measure slides through the same frontend route used by BE."""
    if len(xml_contents) != len(output_paths):
        raise ValueError("xml_contents and output_paths must have equal length")
    if not xml_contents:
        return []

    from playwright.async_api import async_playwright

    capture = PlaywrightCaptureProvider()

    async def run() -> list[dict]:
        executable = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
        options = {
            "headless": True,
            "args": ["--disable-gpu", "--disable-software-rasterizer"],
        }
        if executable:
            path = Path(executable).expanduser()
            if not path.is_file():
                raise FileNotFoundError(f"Configured Chromium not found: {path}")
            options["executable_path"] = str(path)
        semaphore = asyncio.Semaphore(max(1, max_concurrency))
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(**options)

            async def render_one(xml_content: str, output_path: str) -> dict:
                async with semaphore:
                    destination = Path(output_path)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    page = await browser.new_page(
                        viewport=capture.viewport,
                        device_scale_factor=capture.device_scale_factor,
                    )
                    try:
                        await capture._prepare_xml_preview_page(
                            page, xml_content, 0, wait_images=True
                        )
                        metrics = await page.evaluate(_DOM_METRICS_SCRIPT)
                        await page.screenshot(
                            path=str(destination), full_page=False,
                            clip={
                                "x": 0, "y": 0,
                                "width": capture.viewport["width"],
                                "height": capture.viewport["height"],
                            },
                        )
                        return metrics
                    finally:
                        await page.close()

            try:
                return await asyncio.gather(*(
                    render_one(xml, output)
                    for xml, output in zip(xml_contents, output_paths, strict=True)
                ))
            finally:
                await browser.close()

    return asyncio.run(run())


def render_xml_to_png(xml_content: str, output_path: str) -> None:
    """Render one slide using the production frontend XML preview."""
    render_xml_batch_to_png([xml_content], [output_path], max_concurrency=1)


def format_tool_for_qwen(tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.args_schema.model_json_schema(),
        },
    }


QWEN_CHAT_TEMPLATE = """{%- if messages and messages[0].role == 'system' %}
<|im_start|>system
{{ messages[0].content }}
{%- if tools is defined and tools %}

Available tools:
<tools>
{% for tool in tools %}{{ tool | tojson }}
{% endfor %}</tools>
{% endif %}<|im_end|>
{% endif %}
{%- for message in messages %}
{%- if message.role != 'system' %}
<|im_start|>{{ message.role }}
{{ message.content }}<|im_end|>
{% endif %}
{%- endfor %}
{%- if add_generation_prompt %}<|im_start|>assistant
{% endif %}"""


QWEN_GENERATOR_SYSTEM_PROMPT = (
    MATH_EQUATION_RULES
    + "\n\n"
    + XML_CONTENT_PROMPT
    + """

RL SERIALIZATION CONTRACT:
- Return exactly one call to the supplied XML tool.
- Serialize it exactly as <tool_call>{"name":"...","arguments":{...}}</tool_call>.
- Do not add prose, markdown, image-search calls, or raw XML.
"""
)


def build_generator_human_prompt(
    *,
    deck_style_contract: str,
    slide_topic: str,
    slide_plan: str,
    design_instruction: str,
    slide_content: str,
    assigned_tool_name: str,
    slide_index: int,
    deck_length: int,
    image_mode: str = "none",
    approved_images: list[dict] | None = None,
) -> str:
    """Mirror production prompt semantics; only the tool transport differs."""
    return HUMAN_PROMPT_TEMPLATE.format(
        slide_context_map="Offline GRPO corpus sample.",
        deck_style_contract=deck_style_contract,
        slide_topic=slide_topic,
        presentation_instruction="",
        image_mode=image_mode,
        visual_layout_request=design_instruction,
        approved_images=(
            json.dumps(approved_images or [], ensure_ascii=False)
            if image_mode == "semantic"
            else "None — use a layout with no image fields."
        ),
        recent_tools=(
            f"Use only the assigned XML layout tool: {assigned_tool_name}"
        ),
        slide_plan=slide_plan,
        design_instruction=design_instruction,
        slide_index=slide_index + 1,
        length_slide_chunks=deck_length,
        slide_content=slide_content,
        previous_function_call="None — this is the first attempt for this slide.",
        previous_evaluation="None — this is the first attempt for this slide.",
    ) + "\n\nOutput exactly one serialized <tool_call> JSON object."


_CONTENT_KEYS = {
    "title", "subtitle", "headline", "description", "intro_text", "footer_text",
    "content", "content_text", "main_content", "left_text", "right_text", "quote",
    "items", "bullet_items", "list_items", "steps", "topics", "cards", "labels",
    "values", "series", "categories", "names", "roles", "bios",
}


def sanitize_to_placeholders(tool_call: dict) -> dict:
    """Remove content/image identity while preserving layout and visual style."""
    sanitized = deepcopy(tool_call)
    args = sanitized.get("arguments") or sanitized.get("args") or {}
    for key, value in list(args.items()):
        lowered = key.lower()
        if "image" in lowered or lowered.endswith(("_url", "_path")):
            args[key] = ""
        elif key in _CONTENT_KEYS:
            if isinstance(value, list):
                args[key] = ["Text" for _ in value]
            elif isinstance(value, dict):
                args[key] = {k: "Text" for k in value}
            elif isinstance(value, str):
                args[key] = "Text"
    sanitized["arguments"] = args
    sanitized.pop("args", None)
    return sanitized


def get_slide_style_context(tool_call: dict | None) -> str:
    if not tool_call:
        return ""
    args = tool_call.get("arguments") or tool_call.get("args") or {}
    style = {
        key: value
        for key, value in args.items()
        if key not in _CONTENT_KEYS
        and not ("image" in key.lower() or key.lower().endswith(("_url", "_path")))
    }
    return json.dumps(
        {"previous_layout": tool_call.get("name"), "style": style},
        ensure_ascii=False,
    )
