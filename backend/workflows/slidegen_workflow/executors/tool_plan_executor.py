"""Validate and execute the image-search portion of a slide tool plan."""

from __future__ import annotations

import copy
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from backend.workflows.slidegen_workflow.tools.ddgs_tool import search_ddgs_images


SEARCH_TOOL_NAME = "search_ddgs_images"
_FALLBACK_IMAGE_URL = (
    "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"
    "?auto=compress&cs=tinysrgb&w=1600"
)


class ToolPlanError(ValueError):
    """Raised when the generator returns an invalid ordered tool plan."""


def _is_image_param_name(name: str) -> bool:
    normalized = (name or "").lower()
    return (
        "image_url" in normalized
        or "image_path" in normalized
        or normalized in {"bg_image", "background_image"}
    )


def _path_to_string(path: list[Any]) -> str:
    result = ""
    for part in path:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += f".{part}" if result else part
    return result


def _collect_runtime_image_paths(value: Any, path: list[Any]) -> list[list[Any]]:
    """Collect nested image fields already represented in generated arguments."""
    result: list[list[Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = [*path, key]
            if _is_image_param_name(key):
                result.append(child_path)
            else:
                result.extend(_collect_runtime_image_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.extend(_collect_runtime_image_paths(child, [*path, index]))
    return result


def get_image_targets_in_order(tool, arguments: dict) -> list[dict]:
    """
    Return image targets in schema declaration order.

    Top-level image fields come from the selected tool schema even when the
    generator omits them. Nested fields are discovered recursively from the
    generated arguments (for example team_members[0].image_url).
    """
    arguments = arguments if isinstance(arguments, dict) else {}
    targets: list[dict] = []
    seen: set[str] = set()

    try:
        schema = tool.args_schema.model_json_schema()
        properties = schema.get("properties", {})
    except Exception:
        properties = {}

    for name, property_schema in properties.items():
        description = (
            property_schema.get("description", "")
            if isinstance(property_schema, dict)
            else ""
        )
        if _is_image_param_name(name):
            path = [name]
            path_string = _path_to_string(path)
            targets.append(
                {
                    "path": path,
                    "path_string": path_string,
                    "description": description,
                }
            )
            seen.add(path_string)
            continue

        if name not in arguments:
            continue
        for path in _collect_runtime_image_paths(arguments[name], [name]):
            path_string = _path_to_string(path)
            if path_string not in seen:
                targets.append(
                    {
                        "path": path,
                        "path_string": path_string,
                        "description": description,
                    }
                )
                seen.add(path_string)

    # Fallback for lightweight/fake tools without a JSON schema.
    if not properties:
        for path in _collect_runtime_image_paths(arguments, []):
            path_string = _path_to_string(path)
            if path_string not in seen:
                targets.append(
                    {
                        "path": path,
                        "path_string": path_string,
                        "description": "",
                    }
                )
                seen.add(path_string)

    return targets


def tool_has_image_slots(tool) -> bool:
    """Detect image fields from a tool schema, including nested list objects."""
    try:
        schema = tool.args_schema.model_json_schema()
    except Exception:
        return False

    def contains_image_field(node: Any) -> bool:
        if not isinstance(node, dict):
            return False

        properties = node.get("properties")
        if isinstance(properties, dict):
            if any(_is_image_param_name(name) for name in properties):
                return True
            if any(contains_image_field(child) for child in properties.values()):
                return True

        items = node.get("items")
        if contains_image_field(items):
            return True

        for key in ("$defs", "definitions", "anyOf", "oneOf", "allOf"):
            value = node.get(key)
            if isinstance(value, dict):
                if any(contains_image_field(child) for child in value.values()):
                    return True
            elif isinstance(value, list):
                if any(contains_image_field(child) for child in value):
                    return True
        return False

    return contains_image_field(schema)


def tool_matches_image_mode(tool, image_mode: str) -> bool:
    """Match a layout to the planner's none/semantic/decorative decision."""
    if image_mode not in {"none", "semantic", "decorative"}:
        return True
    has_images = tool_has_image_slots(tool)
    return not has_images if image_mode == "none" else has_images


def _infer_layout(description: str) -> str:
    normalized = (description or "").lower()
    if any(token in normalized for token in ("portrait", "tall", "vertical")):
        return "Tall"
    if any(token in normalized for token in ("square", "circle", "avatar")):
        return "Square"
    return "Wide"


def _set_value_at_path(root: dict, path: list[Any], value: str) -> None:
    current: Any = root
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = value


def validate_tool_plan(tool_calls: list[dict], tool_lookup: dict) -> tuple[dict, list[dict], list[dict]]:
    """
    Validate plan ordering and return (slide_call, search_calls, image_targets).

    New order: slide XML call FIRST (index 0), search calls AFTER (index 1..N).
    """
    if not isinstance(tool_calls, list) or not tool_calls:
        raise ToolPlanError("The generator did not return any tool calls.")

    normalized_calls = []
    for index, call in enumerate(tool_calls, start=1):
        if not isinstance(call, dict) or not call.get("name"):
            raise ToolPlanError(f"Tool call {index} is malformed.")
        arguments = call.get("arguments", {})
        if not isinstance(arguments, dict):
            raise ToolPlanError(f"Arguments for tool call {index} must be an object.")
        normalized_calls.append({"name": call["name"], "arguments": arguments})

    # XML slide tool is FIRST, search calls come AFTER
    xml_call = normalized_calls[0]
    search_calls = normalized_calls[1:]
    xml_tool_name = xml_call["name"]

    if xml_tool_name == SEARCH_TOOL_NAME:
        raise ToolPlanError("The first tool call must be a slide XML tool, not an image search.")
    if xml_tool_name not in tool_lookup:
        raise ToolPlanError(
            f"XML tool '{xml_tool_name}' is not available. "
            f"Valid slide tools are: {list(tool_lookup.keys())}"
        )

    for index, call in enumerate(search_calls, start=1):
        if call["name"] != SEARCH_TOOL_NAME:
            raise ToolPlanError(
                f"Tool call {index + 1} must be '{SEARCH_TOOL_NAME}'; "
                "all image search calls must appear after the slide XML tool."
            )
        query = call["arguments"].get("query")
        if not isinstance(query, str) or not query.strip():
            raise ToolPlanError(f"Image search {index} has an empty query.")
        layout = call["arguments"].get("layout")
        if layout not in (None, "Wide", "Tall", "Square"):
            raise ToolPlanError(f"Image search {index} has invalid layout '{layout}'.")
        size = call["arguments"].get("size")
        if size not in (None, "Large", "Medium", "Small"):
            raise ToolPlanError(f"Image search {index} has invalid size '{size}'.")

    image_targets = get_image_targets_in_order(
        tool_lookup[xml_tool_name],
        xml_call["arguments"],
    )
    if len(search_calls) != len(image_targets):
        target_names = [target["path_string"] for target in image_targets]
        example_slide_args = "{...all_args_with_real_values...}"
        example_search_args = '{"query": "<describe the image you need>", "layout": "Wide", "size": "Large"}'
        raise ToolPlanError(
            f"XML tool '{xml_tool_name}' requires {len(image_targets)} image "
            f"search call(s) for {target_names}, but the generator returned "
            f"{len(search_calls)}.\n"
            f"You MUST output BOTH the slide tool AND a search_ddgs_images call together, like this:\n"
            f'<tool_call>{{"name": "{xml_tool_name}", "arguments": {example_slide_args}}}</tool_call>\n'
            f'<tool_call>{{"name": "search_ddgs_images", "arguments": {example_search_args}}}</tool_call>'
        )

    return xml_call, search_calls, image_targets



def _pick_live_url(urls: list, timeout: float = 5.0) -> str | None:
    """
    Lần lượt gửi HEAD request đến từng URL trong danh sách.
    Trả về URL đầu tiên trả về HTTP 2xx/3xx (còn sống).
    Bỏ qua URL hỏng (4xx, 5xx, timeout, connection error).
    """
    import urllib.request
    import urllib.error

    first_candidate = None
    for url in urls:
        if not isinstance(url, str) or not url.strip():
            continue
        if first_candidate is None:
            first_candidate = url
        try:
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "Mozilla/5.0")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status < 400:
                    return url
        except Exception:
            continue   # URL hỏng, thử cái tiếp theo
    # CDNs commonly reject HEAD while still serving the image on GET. Keep
    # the first result from the image provider instead of discarding every
    # search result and replacing it with the generic fallback image.
    return first_candidate


def _run_one_search(index: int, call: dict, target: dict) -> tuple[int, str, dict]:
    arguments = call["arguments"]
    query = arguments["query"].strip()
    layout = arguments.get("layout") or _infer_layout(target.get("description", ""))
    size = arguments.get("size") or "Large"

    try:
        raw_result = search_ddgs_images(
            query=query,
            layout=layout,
            size=size,
            max_results=12,
            target_description=target.get("description", ""),
        )
        urls = json.loads(raw_result)
        url = _pick_live_url(urls)  # Check từng URL, bỏ qua những cái hỏng
    except Exception as exc:
        url = None
        error = str(exc)
    else:
        error = ""

    final_url = url or _FALLBACK_IMAGE_URL
    history = {
        "name": SEARCH_TOOL_NAME,
        "arguments": {
            "query": query,
            "layout": layout,
            "size": size,
        },
        "target_param": target["path_string"],
        "result_url": final_url,
    }
    if error:
        history["error"] = error
    return index, final_url, history


def execute_image_search_plan(
    tool_calls: list[dict],
    tool_lookup: dict,
) -> tuple[dict, list[dict]]:
    """
    Run all LLM-provided searches, inject URLs by rule, and return the XML call.

    Searches execute concurrently, while their result positions remain stable so
    Search N always maps to image target N.
    """
    html_call, search_calls, image_targets = validate_tool_plan(
        tool_calls,
        tool_lookup,
    )
    final_html_call = copy.deepcopy(html_call)
    if not search_calls:
        return final_html_call, []

    results: list[str | None] = [None] * len(search_calls)
    histories: list[dict | None] = [None] * len(search_calls)
    with ThreadPoolExecutor(max_workers=len(search_calls)) as executor:
        futures = {
            executor.submit(_run_one_search, index, call, image_targets[index]): index
            for index, call in enumerate(search_calls)
        }
        for future in as_completed(futures):
            index, url, history = future.result()
            results[index] = url
            histories[index] = history

    for target, url in zip(image_targets, results):
        _set_value_at_path(
            final_html_call["arguments"],
            target["path"],
            url or _FALLBACK_IMAGE_URL,
        )

    return final_html_call, [history for history in histories if history]
