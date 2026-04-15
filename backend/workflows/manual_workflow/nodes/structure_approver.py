import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.config import TEMP_DIR
from backend.workflows.manual_workflow.graph.stage import State

logger = logging.getLogger(__name__)


THRESHOLD_CHAR_LIMIT = 1000


def approve_manual_structure(state: State) -> State:
    """Approve manual structure by flattening tree data into ordered slide chunks."""
    session_id = str(state.get("session_id", "")).strip()
    if not session_id:
        raise ValueError("Missing session_id for manual approve workflow")

    structure = state.get("document_structure", [])
    title = state.get("document_title", "Untitled")

    # 1) Extract special slides
    intro_slide, thank_you_slide, filtered_structure = _extract_special_slides(structure)

    # 2) Renumber hierarchy
    renumbered_structure = _renumber_structure(filtered_structure)

    # 3) DFS flattening
    gen_context = {
        "content": [],
        "positions": [],
        "maps": [],
        "types": [],
        "full_structure": renumbered_structure,
    }

    if intro_slide:
        _add_slide(gen_context, intro_slide, ["0"], "INTRO SLIDE", "intro")

    _traverse_dfs(renumbered_structure, gen_context, is_root_level=True)

    if thank_you_slide:
        _add_slide(gen_context, thank_you_slide, ["999"], "THANK YOU SLIDE", "thank_you")

    # 4) Sort + format
    final_result = _sort_and_format_results(gen_context, session_id, title, renumbered_structure)

    # 5) Persist approved file for downstream stream endpoint
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    approved_file = TEMP_DIR / f"approved_structure_{session_id}.json"
    with open(approved_file, "w", encoding="utf-8") as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)

    state["document_outline"] = final_result.get("document_outline", [])
    state["slide_chunks"] = final_result.get("slide_chunks", [])
    state["slide_positions"] = final_result.get("slide_positions", [])
    state["slide_context_maps"] = final_result.get("slide_context_maps", [])
    state["slide_types"] = final_result.get("slide_types", [])
    state["approved_result"] = final_result
    return state


def _add_slide(ctx: Dict[str, Any], content: str, pos: List[str], map_content: str, slide_type: str) -> None:
    ctx["content"].append(content)
    ctx["positions"].append(pos)
    ctx["maps"].append(map_content)
    ctx["types"].append(slide_type)


def _traverse_dfs(nodes: List[Dict[str, Any]], ctx: Dict[str, Any], is_root_level: bool = False) -> None:
    for node in nodes:
        # 1) Transition slide
        if is_root_level and node.get("is_transition") is True:
            title = node.get("numbered_title", node.get("title", ""))
            transition_content = f"TRANSITION SLIDE\n\n{title}"
            pos = [f"{node.get('index', '')}.T"]
            context_map = _create_context_map(ctx["full_structure"], [node.get("index", "")])
            _add_slide(ctx, transition_content, pos, context_map, "transition")

        # 2) Children status
        has_leaves = any(not child.get("children") for child in node.get("children", []))
        has_sub_trees = any(child.get("children") for child in node.get("children", []))
        is_transition_node = node.get("is_transition") is True

        # 3) Content slide for current node
        if not is_transition_node and not has_leaves and not has_sub_trees:
            pos = [node.get("index", "")]
            content = _render_slide_content("", [node])
            if not content.strip():
                content = node.get("numbered_title", node.get("title", ""))
            context_map = _create_context_map(ctx["full_structure"], pos)
            _add_slide(ctx, content, pos, context_map, "content")

        # 4) Process leaves
        leaves = [child for child in node.get("children", []) if not child.get("children")]
        if leaves:
            _create_slides_from_leaves(node, leaves, ctx)

        # 5) Process sub trees
        sub_trees = [child for child in node.get("children", []) if child.get("children")]
        if sub_trees:
            _traverse_dfs(sub_trees, ctx, is_root_level=False)


def _create_slides_from_leaves(parent: Dict[str, Any], leaves: List[Dict[str, Any]], ctx: Dict[str, Any]) -> None:
    if not leaves:
        return

    buffer: List[Dict[str, Any]] = []
    header_parts = [parent.get("numbered_title", "")]
    if parent.get("content"):
        header_parts.append(parent["content"])
    header = "\n".join(header_parts)

    for item in leaves:
        tentative_buffer = buffer + [item]
        if len(_render_slide_content(header, tentative_buffer)) > THRESHOLD_CHAR_LIMIT and buffer:
            content = _render_slide_content(header, buffer)
            pos = [i.get("index", "") for i in buffer]
            context_map = _create_context_map(ctx["full_structure"], pos)
            _add_slide(ctx, content, pos, context_map, "content")
            buffer = [item]
        else:
            buffer.append(item)

    if buffer:
        content = _render_slide_content(header, buffer)
        pos = [i.get("index", "") for i in buffer]
        context_map = _create_context_map(ctx["full_structure"], pos)
        _add_slide(ctx, content, pos, context_map, "content")


def _create_context_map(outline_nodes: List[Dict[str, Any]], active_indices: List[str]) -> str:
    map_lines: List[str] = []
    if not isinstance(active_indices, list):
        active_indices = [active_indices]

    def _generate(nodes: List[Dict[str, Any]], indent: int) -> None:
        for node in nodes:
            node_index = node.get("index", "")
            marker = " <--- YOU ARE HERE" if node_index in active_indices else ""
            map_lines.append(f"{'  ' * indent}{node_index}. {node.get('title', '')}{marker}")
            if node.get("children"):
                _generate(node["children"], indent + 1)

    _generate(outline_nodes, 0)
    return "\n".join(map_lines)


def _render_slide_content(group_header: str, items: List[Dict[str, Any]]) -> str:
    parts = [group_header] if group_header else []
    if len(items) > 1:
        for item in items:
            parts.append(f"\n\t- {item.get('title', '')}")
            if item.get("content"):
                indented = "\n\t  ".join(item["content"].splitlines())
                parts.append(f"\t  {indented}")
    else:
        item = items[0]
        parts.append(f"\n{item.get('numbered_title', item.get('title', ''))}")
        if item.get("content"):
            parts.append(f"{item['content']}")
    return "\n".join(parts)


def _renumber_structure(
    nodes: List[Dict[str, Any]],
    counters: Optional[List[int]] = None,
    parent_level: int = 0,
) -> List[Dict[str, Any]]:
    counters = [0] * 6 if counters is None else counters
    for node in nodes:
        is_transition = node.get("is_transition") is True

        counters[parent_level] += 1
        for i in range(parent_level + 1, len(counters)):
            counters[i] = 0

        index = ".".join(map(str, counters[: parent_level + 1]))
        node["index"] = index
        node["numbered_title"] = f"{index}. {node['title']}"
        node["level"] = parent_level + 1

        if is_transition:
            counters[parent_level] -= 1

        if node.get("children"):
            _renumber_structure(node["children"], list(counters), parent_level + 1)
    return nodes


def _extract_special_slides(structure: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[str], List[Dict[str, Any]]]:
    intro_node = None
    filtered: List[Dict[str, Any]] = []
    for node in structure:
        if node.get("level") == 0:
            intro_node = node
        else:
            filtered.append(node)

    intro_slide = f"INTRO SLIDE\n\nTitle: {intro_node.get('content', '')}" if intro_node else None

    thank_you_slide = None
    if filtered:
        last = filtered[-1]
        keywords = ["thank", "cảm ơn", "cam on", "lời cảm ơn"]
        if any(k in last.get("title", "").lower() for k in keywords):
            thank_node = filtered.pop()
            thank_you_slide = (
                f"THANK YOU SLIDE\n\n{thank_node.get('title', '')}\n\n{thank_node.get('content', '')}"
            )

    return intro_slide, thank_you_slide, filtered


def _sort_and_format_results(
    ctx: Dict[str, Any],
    session_id: str,
    title: str,
    outline: List[Dict[str, Any]],
) -> Dict[str, Any]:
    combined = list(zip(ctx["content"], ctx["positions"], ctx["maps"], ctx["types"]))

    def sort_key(item: Tuple[str, List[str], str, str]) -> Tuple[int, ...]:
        pos_str = str(item[1][0]) if item[1] else "0"
        if pos_str == "0":
            return (0,)
        if pos_str == "999":
            return (999999,)

        is_transition = pos_str.endswith(".T")
        clean_pos = pos_str.replace(".T", "")
        parts = tuple(int(p) for p in clean_pos.split("."))
        return parts + (0,) if is_transition else parts + (1,)

    sorted_combined = sorted(combined, key=sort_key)

    if sorted_combined:
        s_chunks, s_pos, s_maps, s_types = zip(*sorted_combined)
    else:
        s_chunks, s_pos, s_maps, s_types = [], [], [], []

    converted_chunks = []
    for i, (text, c_type, _) in enumerate(zip(s_chunks, s_types, s_pos)):
        lines = text.strip().split("\n")

        if c_type == "intro":
            position = 0
            heading = "INTRO"
        elif c_type == "transition":
            position = -1
            heading = "TRANSITION"
        elif c_type == "thank_you":
            position = -2
            heading = "THANK_YOU"
        else:
            position = i + 1
            raw_heading = lines[0] if lines else ""
            heading = re.sub(r"^\d+(\.\d+)*\.?\s*", "", raw_heading)

        converted_chunks.append(
            {
                "position": position,
                "heading": heading,
                "text_content": text,
            }
        )

    return {
        "success": True,
        "session_id": session_id,
        "document_title": title,
        "document_outline": outline,
        "slide_chunks": converted_chunks,
        "slide_positions": list(s_pos),
        "slide_context_maps": list(s_maps),
        "slide_types": list(s_types),
    }