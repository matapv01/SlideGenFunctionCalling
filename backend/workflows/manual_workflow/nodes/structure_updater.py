import json
from typing import Any, Dict, List, Optional

from backend.config import TEMP_DIR
from backend.workflows.manual_workflow.graph.stage import State


def update_manual_structure(state: State) -> State:
    """Persist editor structure into temp storage for later approve workflow."""
    session_id = str(state.get("session_id", "")).strip()
    if not session_id:
        raise ValueError("Missing session_id for manual update workflow")

    structure = state.get("document_structure", [])
    intro_slide = state.get("intro_slide")
    slide_options = state.get("slide_options", {}) or {}
    output_format = "xml"

    document_title = "Untitled Document"
    if intro_slide:
        document_title = intro_slide.get("content") or "Untitled Document"

    raw_structure: List[Dict[str, Any]] = []
    if intro_slide:
        raw_structure.append(intro_slide)
    raw_structure.extend(structure)

    merged_structure = _merge_title_content_nodes(raw_structure)

    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    file_path = TEMP_DIR / f"structure_{session_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "session_id": session_id,
                "document_title": document_title,
                "document_structure": merged_structure,
                "output_format": output_format,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    state["document_title"] = document_title
    state["document_structure"] = merged_structure
    state["slide_options"] = {**slide_options, "output_format": output_format}
    state["update_result"] = {"success": True, "message": "Cấu trúc đã được lưu"}
    return state


def _merge_title_content_nodes(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    i = 0
    while i < len(nodes):
        node = nodes[i]
        has_title = node.get("title", "").strip() != ""
        has_no_content = not node.get("content", "").strip()

        is_next_content = False
        if i + 1 < len(nodes):
            next_node = nodes[i + 1]
            has_no_title = not next_node.get("title", "").strip()
            has_content = next_node.get("content", "").strip() != ""
            same_level = next_node.get("level") == node.get("level")
            is_next_content = has_no_title and has_content and same_level

        if has_title and has_no_content and is_next_content:
            next_node = nodes[i + 1]
            merged_node = {
                "level": node.get("level"),
                "title": node.get("title"),
                "content": next_node.get("content"),
                "children": _merge_title_content_nodes(node.get("children", [])),
                "is_transition": node.get("is_transition", False),
            }
            merged.append(merged_node)
            i += 2
        else:
            merged_node = node.copy()
            merged_node["children"] = _merge_title_content_nodes(node.get("children", []))
            merged.append(merged_node)
            i += 1

    return merged
