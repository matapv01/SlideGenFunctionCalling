"""Validate slide layouts and inject assets approved by the image workflow."""

from __future__ import annotations

import copy
from typing import Any

from backend.application.services.slide_asset_service import (
    SlideAssetError,
    slide_asset_service,
)


class NoApprovedImageError(ValueError):
    """Signal that the current image layout must be regenerated without images."""


class ToolPlanError(ValueError):
    """Raised when the generator returns an invalid XML tool call."""


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


def get_image_targets_in_order(tool, arguments: dict) -> list[dict[str, Any]]:
    """Return image targets in schema declaration order.

    Top-level image fields come from the selected tool schema even when the
    generator omits them. Nested fields are discovered from generated
    arguments, for example ``team_members[0].image_url``.
    """
    arguments = arguments if isinstance(arguments, dict) else {}
    targets: list[dict[str, Any]] = []
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
            if path_string in seen:
                continue
            targets.append(
                {
                    "path": path,
                    "path_string": path_string,
                    "description": description,
                }
            )
            seen.add(path_string)

    # Keep lightweight test doubles and external integrations usable when they
    # do not expose a Pydantic JSON schema.
    if not properties:
        for path in _collect_runtime_image_paths(arguments, []):
            path_string = _path_to_string(path)
            if path_string in seen:
                continue
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
        if contains_image_field(node.get("items")):
            return True
        for key in ("$defs", "definitions", "anyOf", "oneOf", "allOf"):
            value = node.get(key)
            if isinstance(value, dict) and any(
                contains_image_field(child) for child in value.values()
            ):
                return True
            if isinstance(value, list) and any(
                contains_image_field(child) for child in value
            ):
                return True
        return False

    return contains_image_field(schema)


def tool_image_slot_count(tool) -> int:
    """Return the number of top-level image fields exposed by a layout schema."""
    return len(get_image_targets_in_order(tool, {}))


def tool_matches_image_mode(
    tool,
    image_mode: str,
    approved_image_count: int | None = None,
) -> bool:
    """Match a layout to the planner's explicit none/semantic decision."""
    if image_mode not in {"none", "semantic"}:
        return True
    has_images = tool_has_image_slots(tool)
    if image_mode == "none":
        return not has_images
    if not has_images:
        return False
    if approved_image_count is not None:
        return approved_image_count > 0 and tool_image_slot_count(tool) == approved_image_count
    return True


def _set_value_at_path(root: dict, path: list[Any], value: str) -> None:
    current: Any = root
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = value


def _approved_image_url(
    image: dict[str, Any],
    asset_dir: str | None,
) -> str | None:
    """Resolve one verified assignment to a validated local asset."""
    if not asset_dir:
        # Lightweight integrations and unit tests may execute the XML tool
        # without a workflow output directory. Preserve their verified URL;
        # every real workflow supplies ``asset_dir`` and takes the local path.
        return next(
            (
                str(image.get(key) or "").strip()
                for key in ("source_path", "source_url", "result_url", "url")
                if str(image.get(key) or "").strip()
            ),
            None,
        )
    for key in ("source_path", "source_url", "result_url", "url"):
        value = str(image.get(key) or "").strip()
        if not value:
            continue
        try:
            return slide_asset_service.materialize(value, asset_dir)
        except (OSError, SlideAssetError):
            continue
    return None


def inject_approved_images(
    tool_call: dict[str, Any],
    *,
    tool,
    approved_images: list[dict[str, Any]] | None,
    asset_dir: str | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Bind only verifier-approved assets to XML fields in schema order.

    Search and relevance decisions belong to graph nodes before generation.
    This executor never searches, downloads candidates, or trusts a raw URL
    emitted by the generator as evidence of relevance.
    """
    final_call = copy.deepcopy(tool_call)
    image_targets = get_image_targets_in_order(
        tool,
        final_call.get("arguments") or {},
    )
    images = list(approved_images or [])
    if not image_targets and not images:
        return final_call, []
    if len(images) != len(image_targets):
        raise NoApprovedImageError(
            f"IMAGE_ASSIGNMENT_EMPTY: layout '{final_call.get('name', '')}' "
            f"requires {len(image_targets)} approved image(s), received {len(images)}."
        )

    histories: list[dict[str, Any]] = []
    for target, image in zip(image_targets, images):
        url = _approved_image_url(image, asset_dir)
        if not url:
            raise NoApprovedImageError(
                "IMAGE_ASSIGNMENT_UNAVAILABLE: an approved image asset could "
                "not be materialized; regenerate this slide without images."
            )
        _set_value_at_path(final_call["arguments"], target["path"], url)
        histories.append(
            {
                "name": "approved_image",
                "arguments": {
                    "source_id": image.get("source_id") or image.get("image_id", ""),
                    "role": image.get("role", "illustration"),
                },
                "target_param": target["path_string"],
                "result_url": url,
                "source": image.get("source_type", "verified"),
                "visual_notes": image.get("visual_notes", ""),
                "caption_hint": image.get("caption_hint", ""),
                "placement_hint": image.get("placement_hint", ""),
            }
        )
    return final_call, histories
