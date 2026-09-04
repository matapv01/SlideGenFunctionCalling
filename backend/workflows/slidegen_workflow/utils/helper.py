import json
import logging
import asyncio
import base64
import html
import re
import textwrap
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont


def _convert_llm_tree_to_nodes(llm_json_list: List[Dict], parent_level: int) -> List[Dict]:
    """
    Recursively converts the LLM's nested JSON output into the standard
    node format used by the document_structure.
    """
    new_nodes = []
    for item in llm_json_list:
        if "sub_headline" not in item or "sub_content" not in item:
            continue  # Skip malformed items

        new_node = {
            "level": parent_level + 1,
            "title": item["sub_headline"],
            "content": "\n".join(item.get("sub_content", [])),
            "children": []  # Default to empty
        }

        # If there are nested sections, recurse!
        if item.get("sub_sections") and isinstance(item["sub_sections"], list):
            new_node["children"] = _convert_llm_tree_to_nodes(item["sub_sections"], parent_level + 1)

        new_nodes.append(new_node)
    return new_nodes


def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string."""
    if image_path is None:
        logging.warning("Image path is None, cannot convert to base64")
        return ""

    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error encoding image to base64: {image_path}, Error: {e}")
        return ""


def create_default_html(content_data) -> str:
    """Create default HTML when unable to get from LLM"""
    # Handle both dict and string formats
    if isinstance(content_data, dict):
        title = content_data.get('heading', 'Slide')
        content_text = content_data.get('text_content', 'Default slide content')
    else:
        content_text = content_data if content_data else "Default slide content"
        title = "Slide"

    lines = content_text.split('\n')
    if not title:
        title = lines[0] if lines else "Slide"
    content = '<br>'.join(lines[1:]) if len(lines) > 1 else content_text

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .slide {{ width: 800px; height: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); padding: 40px; position: relative; }}
        .title {{ font-size: 32px; color: #2c3e50; margin-bottom: 30px; text-align: center; }}
        .content {{ font-size: 24px; line-height: 1.5; color: #34495e; }}
    </style>
</head>
<body>
    <div class="slide">
        <div class="title">{title}</div>
        <div class="content">{content}</div>
    </div>
</body>
</html>"""
    return html


# Keys that carry slide *content* — these must NOT leak into the next slide's prompt
_CONTENT_KEYS = {
    "main_title", "subtitle", "content_text", "description_text", "title",
    "main_content", "content1", "content2", "left_text", "right_text",
    "items", "list_items", "steps", "agenda_items", "subtitle1", "subtitle2",
    "header_text", "headline", "top_text", "author_line", "top_left_text",
    "bottom_text", "year", "section_title", "section_subtitle", "mission_items",
    "left_title", "right_title", "left_content", "right_content", "description"
}


TOKEN = "Aa"

def _sanitize_value(v):
    if isinstance(v, str):
        return TOKEN
    if isinstance(v, list):
        return [_sanitize_value(item) for item in v]
    if isinstance(v, dict):
        return {ik: _sanitize_value(iv) for ik, iv in v.items()}
    return v

def sanitize_to_placeholders(tool_call: dict) -> dict:
    """
    Replaces all text content with the same token "Aa", preserving structure
    (list lengths, dict keys, nesting) so the rendered layout is identical
    in element count but content text cannot influence embeddings.
    """
    if not tool_call:
        return {}

    result = {"name": tool_call.get("name", "")}
    args = tool_call.get("arguments", {})
    sanitized_args = {}

    for k, v in args.items():
        if k in _CONTENT_KEYS:
            sanitized_args[k] = _sanitize_value(v)
        elif k == "image_url":
            sanitized_args[k] = "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?q=80&w=200"
        elif k in ("theme_color", "accent_color", "highlight_color",
                   "background_color", "bg_color", "bg_color_left", "bg_color_right",
                   "font_size_multiplier", "card_padding", "border_width"):
            sanitized_args[k] = v
        else:
            sanitized_args[k] = v

    result["arguments"] = sanitized_args
    return result


def get_slide_style_context(tool_call: dict) -> str:
    """
    Extracts key design/style properties from the previous slide's tool call
    and returns a compact, standardized visual context prompt string.
    """
    if not tool_call:
        return (
            "[PREVIOUS SLIDE STYLE CONTEXT]\n"
            "- Layout Category: CONTENT_TOOLS\n"
            "- Primary Theme Color: #2563EB\n"
            "- Background Style: Light background (#FFFFFF)\n"
            "- Font Scale Multiplier: 1.0\n"
            "- Padding/Margins: 1.5rem"
        )
        
    name = tool_call.get("name", "")
    args = tool_call.get("arguments", {})
    
    # 1. Classify layout category
    layout_category = "LIST_TOOLS"
    if "chart" in name:
        layout_category = "CHART_TOOLS"
    elif "process" in name or "timeline" in name:
        layout_category = "TIMELINE_TOOLS"
    elif "intro" in name or "title" in name:
        layout_category = "INTRO_TOOLS"
        
    # 2. Extract style parameters (using typical parameter names)
    theme_color = args.get("theme_color") or args.get("accent_color") or args.get("highlight_color") or "#2563EB"
    bg_color = args.get("background_color") or args.get("bg_color") or args.get("bg_color_left") or "#FFFFFF"
    font_size = args.get("font_size_multiplier") or 1.0
    padding = args.get("card_padding") or args.get("border_width") or "1.5rem"
    
    bg_brightness = "Dark background" if bg_color in ["#1F2937", "#111827", "#0F172A", "#1A1A1A"] else "Light background"
    bg_style_str = f"{bg_brightness} ({bg_color})"
    
    style_context_str = (
        "[PREVIOUS SLIDE STYLE CONTEXT]\n"
        f"- Layout Category: {layout_category}\n"
        f"- Primary Theme Color: {theme_color}\n"
        f"- Background Style: {bg_style_str}\n"
        f"- Font Scale Multiplier: {font_size}\n"
        f"- Padding/Margins: {padding}"
    )
    return style_context_str


# ====================================================================
# RL / Training Shared Utilities
# ====================================================================

def format_tool_for_qwen(tool) -> dict:
    """Convert a LangChain tool to Qwen's expected JSON Schema format."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.args
        }
    }


QWEN_CHAT_TEMPLATE = """{%- if messages[0].role == 'system' %}
{%- if tools is defined and tools %}
<|im_start|>system
{{ messages[0].content }}

Available tools:
<tools>
{% for tool in tools %}
{{ tool | tojson }}
{% endfor %}
</tools>

Output ONLY ordered JSON function calls, each within its own <tool_call> tags.
Example: <tool_call>{% raw %}{"name": "generate_title_slide", "arguments": {"main_title": "Title"}}{% endraw %}</tool_call>
<|im_end|>
{%- else %}
<|im_start|>system
{{ messages[0].content }}<|im_end|>
{%- endif %}
{%- endif %}
{%- for message in messages %}
{%- if message.role == 'assistant' and message.tool_calls is defined and message.tool_calls %}
<|im_start|>assistant
{% for tc in message.tool_calls %}
<tool_call>
{{ tc | tojson }}
</tool_call>
{% endfor %}<|im_end|>
{%- elif message.role != 'system' %}
<|im_start|>{{ message.role }}
{{ message.content }}<|im_end|>
{%- endif %}
{%- endfor %}
{%- if add_generation_prompt %}
<|im_start|>assistant
{%- endif %}"""


def _normalize_tool_call(value) -> Optional[dict]:
    """Normalize common native/raw tool-call shapes to {name, arguments}."""
    if not isinstance(value, dict):
        return None

    function_value = value.get("function")
    if isinstance(function_value, dict):
        name = function_value.get("name")
        arguments = function_value.get("arguments", {})
    else:
        name = value.get("name")
        arguments = value.get("arguments")
        if arguments is None:
            arguments = value.get("args", {})

    if not name:
        return None
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except Exception:
            return None
    if not isinstance(arguments, dict):
        return None
    return {"name": name, "arguments": arguments}


def _normalize_tool_call_collection(value) -> List[dict]:
    if isinstance(value, dict) and isinstance(value.get("tool_calls"), list):
        values = value["tool_calls"]
    elif isinstance(value, list):
        values = value
    else:
        values = [value]
    return [
        normalized
        for item in values
        if (normalized := _normalize_tool_call(item)) is not None
    ]


def repair_and_parse_json(s: str) -> Optional[Any]:
    """Robustly parse JSON string, applying heuristics to repair common LLM syntax defects."""
    if not s or not s.strip():
        return None
    s = s.strip()

    # 0. Try json_repair library if installed
    try:
        import importlib
        json_repair = importlib.import_module("json_repair")
        return json_repair.loads(s)
    except Exception:
        pass

    # 1. Direct standard parse
    try:
        return json.loads(s)
    except Exception:
        pass

    # Helper cleaner
    def _clean_str(text_to_clean: str) -> str:
        in_string = False
        chars = []
        for i, char in enumerate(text_to_clean):
            if char == '"' and (i == 0 or text_to_clean[i-1] != '\\'):
                in_string = not in_string
            if char == '\n' and in_string:
                chars.append('\\n')
            elif char == '\r' and in_string:
                continue
            else:
                chars.append(char)
        cleaned = "".join(chars)
        # Remove trailing commas before closing brackets/braces
        cleaned = re.sub(r',\s*([\]}])', r'\1', cleaned)
        return cleaned

    cleaned = _clean_str(s)
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 2. Heuristic: Fix unclosed array before a key-value property
    # e.g., "points": [ {...}, {...}, "bg_color": ... -> "points": [ {...}, {...} ], "bg_color": ...
    try:
        open_brackets = cleaned.count('[')
        close_brackets = cleaned.count(']')
        if open_brackets > close_brackets:
            diff = open_brackets - close_brackets
            # Insert missing ']' after the last object inside the array before the next key
            fixed_array = re.sub(r'(\}\s*),\s*("(?=[a-zA-Z0-9_]+"\s*:))', r'\1], \2', cleaned, count=diff)
            fixed_array = re.sub(r',\s*([\]}])', r'\1', fixed_array)
            return json.loads(fixed_array)
    except Exception:
        pass

    # 3. Heuristic: Balance unclosed trailing brackets and braces
    try:
        open_braces = cleaned.count('{') - cleaned.count('}')
        open_brackets = cleaned.count('[') - cleaned.count(']')
        balanced = cleaned + (']' * max(0, open_brackets)) + ('}' * max(0, open_braces))
        balanced = re.sub(r',\s*([\]}])', r'\1', balanced)
        return json.loads(balanced)
    except Exception:
        pass

    return None


def parse_tool_calls_json(text: str) -> List[dict]:
    """
    Extract all ordered tool calls from Qwen/raw model output.

    Supported forms:
      - repeated <tool_call>{...}</tool_call> blocks
      - {"tool_calls": [{...}, ...]}
      - a raw JSON list of tool calls
      - a single raw tool call
    """
    if not text:
        return []

    cleaned = text.strip()

    # 1. Try extracting repeated <tool_call>...</tool_call> blocks first.
    tool_call_blocks = re.findall(
        r"<tool_call>\s*(.*?)\s*</tool_call>",
        cleaned,
        flags=re.DOTALL,
    )
    if tool_call_blocks:
        calls: List[dict] = []
        for block in tool_call_blocks:
            parsed = repair_and_parse_json(block)
            if parsed is not None:
                calls.extend(_normalize_tool_call_collection(parsed))
            else:
                logging.warning(f"Failed to parse tool call block after repair: {block}")
        if calls:
            return calls

    # 2. Try extracting from a single unclosed <tool_call> tag.
    tool_call_match = re.search(r"<tool_call>\s*(\{.*)", cleaned, re.DOTALL)
    if tool_call_match:
        raw_json_str = tool_call_match.group(1)
        if "</tool_call>" in raw_json_str:
            raw_json_str = raw_json_str.split("</tool_call>")[0].strip()
        cleaned = raw_json_str.strip()

    # 3. Try code blocks ```json ... ```
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()

    # 4. Direct/Repaired JSON parse
    parsed = repair_and_parse_json(cleaned)
    if parsed is not None:
        return _normalize_tool_call_collection(parsed)

    # 5. Fallback: Search for any JSON object containing "name" and "arguments" / "args"
    try:
        json_obj_match = re.search(r'\{[^{}]*"name"\s*:\s*"[^"]+"\s*,\s*"(?:arguments|args)"\s*:\s*\{.*?\}\s*\}', text, re.DOTALL)
        if json_obj_match:
            parsed = repair_and_parse_json(json_obj_match.group(0))
            if parsed is not None:
                return _normalize_tool_call_collection(parsed)
    except Exception:
        pass

    return []


def parse_tool_call_json(text: str) -> Optional[dict]:
    """
    Return the primary slide HTML tool call from raw model output.

    If image-search calls are present, prefer the first non-search call so both
    legacy search-first outputs and the current slide-first plan resolve to the
    actual slide generator tool.
    """
    calls = parse_tool_calls_json(text)
    for call in calls:
        if call.get("name") != "search_ddgs_images":
            return call
    return calls[0] if calls else None


def render_html_to_png(html_content: str, output_path: str) -> None:
    """Render HTML string to PNG image using Playwright (sync wrapper)."""
    def _fallback_render(reason: str) -> None:
        text = re.sub(r"<script.*?</script>", " ", html_content, flags=re.S | re.I)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        preview = text[:1200] if text else "Render fallback"

        img = Image.new("RGB", (1280, 720), "white")
        draw = ImageDraw.Draw(img)
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        draw.text((48, 36), "Playwright render fallback", fill="#0F172A", font=title_font)
        for idx, line in enumerate(textwrap.wrap(reason, width=95) or ["render failed"]):
            draw.text((48, 68 + idx * 16), line, fill="#475569", font=body_font)
        y = 120
        for line in textwrap.wrap(preview, width=90):
            if y > 680:
                break
            draw.text((48, y), line, fill="#111827", font=body_font)
            y += 16
        img.save(output_path)

    try:
        from backend.infrastructure.capture.playwright_provider import PlaywrightCaptureProvider

        capture = PlaywrightCaptureProvider()
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(capture.generate_slide_from_html(html_content, output_path))
    except Exception as exc:
        logging.warning(f"Playwright render failed, using fallback PNG: {exc}")
        _fallback_render(str(exc))



