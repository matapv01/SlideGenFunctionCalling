"""RL-facing adapter for the XML-only SlideGen pipeline.

Compatibility stays here instead of re-introducing the removed HTML API into
backend, which remains aligned with minh_dep.
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path

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
from backend.workflows.slidegen_workflow.utils.xml_preview import build_xml_preview_html


def execute_tool(tool_call: dict) -> str:
    """Execute one XML tool call and surface invalid calls to reward functions."""
    return _execute_xml_tool(tool_call, raise_on_error=True)


def render_xml_to_png(xml_content: str, output_path: str) -> None:
    """Render XML locally and fail loudly instead of scoring a fallback image."""
    from playwright.sync_api import sync_playwright

    html_content = build_xml_preview_html(xml_content)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    configured_browser = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    system_browser = Path("/usr/bin/google-chrome")
    launch_options = {
        "headless": True,
        "args": ["--disable-gpu", "--disable-software-rasterizer"],
    }
    if configured_browser:
        launch_options["executable_path"] = configured_browser
    elif system_browser.is_file():
        launch_options["executable_path"] = str(system_browser)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch_options)
        try:
            page = browser.new_page(viewport={"width": 1600, "height": 900})
            page.set_content(html_content, wait_until="load")
            page.evaluate("() => document.fonts && document.fonts.ready")
            page.screenshot(path=str(destination), full_page=False)
        finally:
            browser.close()


def render_xml_batch_to_png(
    xml_contents: list[str],
    output_paths: list[str],
    max_concurrency: int = 4,
) -> None:
    """Render a rollout batch concurrently through one Chromium process."""
    if len(xml_contents) != len(output_paths):
        raise ValueError("xml_contents and output_paths must have equal length")
    if not xml_contents:
        return

    import asyncio
    from playwright.async_api import async_playwright

    async def run() -> None:
        configured_browser = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
        system_browser = Path("/usr/bin/google-chrome")
        launch_options = {
            "headless": True,
            "args": ["--disable-gpu", "--disable-software-rasterizer"],
        }
        if configured_browser:
            launch_options["executable_path"] = configured_browser
        elif system_browser.is_file():
            launch_options["executable_path"] = str(system_browser)

        semaphore = asyncio.Semaphore(max(1, max_concurrency))
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(**launch_options)

            async def render_one(xml_content: str, output_path: str) -> None:
                async with semaphore:
                    destination = Path(output_path)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    page = await browser.new_page(
                        viewport={"width": 1600, "height": 900}
                    )
                    try:
                        await page.set_content(
                            build_xml_preview_html(xml_content),
                            wait_until="load",
                        )
                        await page.evaluate(
                            "() => document.fonts && document.fonts.ready"
                        )
                        await page.screenshot(
                            path=str(destination),
                            full_page=False,
                        )
                    finally:
                        await page.close()

            try:
                await asyncio.gather(
                    *[
                        render_one(xml_content, output_path)
                        for xml_content, output_path in zip(
                            xml_contents, output_paths, strict=True
                        )
                    ]
                )
            finally:
                await browser.close()

    asyncio.run(run())

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
) -> str:
    """Mirror production prompt semantics; only the tool transport differs."""
    return HUMAN_PROMPT_TEMPLATE.format(
        slide_context_map="Offline GRPO corpus sample.",
        deck_style_contract=deck_style_contract,
        slide_topic=slide_topic,
        presentation_instruction="",
        image_mode="none",
        visual_layout_request=design_instruction,
        approved_images="None — use a layout with no image fields.",
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
