import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.config import TEMP_DIR
from backend.infrastructure.workflow_common import (
    create_context_map,
    create_slides_from_leaves,
    renumber_structure,
    render_slide_content,
)
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
    slide_options = state.get("slide_options", {}) or {}
    output_format = "xml"

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
    final_result = _sort_and_format_results(
        gen_context,
        session_id,
        title,
        renumbered_structure,
        output_format,
    )

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
    state["slide_options"] = {**slide_options, "output_format": output_format}
    state["approved_result"] = final_result

    context_maps = state["slide_context_maps"]
    logger.info("Generated %d slide_context_maps for session %s", len(context_maps), session_id)
    for i, context_map in enumerate(context_maps[:3], start=1):
        logger.info("slide_context_map[%d]:\n%s", i, context_map)

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
            context_map = create_context_map(ctx["full_structure"], [node.get("index", "")])
            _add_slide(ctx, transition_content, pos, context_map, "transition")

        # 2) Children status
        has_leaves = any(not child.get("children") for child in node.get("children", []))
        has_sub_trees = any(child.get("children") for child in node.get("children", []))
        is_transition_node = node.get("is_transition") is True

        # 3) Content slide for current node
        if not is_transition_node and not has_leaves and not has_sub_trees:
            pos = [node.get("index", "")]
            content = render_slide_content("", [node])
            if not content.strip():
                content = node.get("numbered_title", node.get("title", ""))
            context_map = create_context_map(ctx["full_structure"], pos)
            _add_slide(ctx, content, pos, context_map, "content")

        # 4) Process leaves
        leaves = [child for child in node.get("children", []) if not child.get("children")]
        if leaves:
            create_slides_from_leaves(
                parent=node,
                leaves=leaves,
                full_structure=ctx["full_structure"],
                threshold_char_limit=THRESHOLD_CHAR_LIMIT,
                include_parent_content_in_header=True,
                add_slide=lambda content, pos, context_map, _first_item_title: _add_slide(
                    ctx, content, pos, context_map, "content"
                ),
            )

        # 5) Process sub trees
        sub_trees = [child for child in node.get("children", []) if child.get("children")]
        if sub_trees:
            _traverse_dfs(sub_trees, ctx, is_root_level=False)


def _renumber_structure(
    nodes: List[Dict[str, Any]],
    counters: Optional[List[int]] = None,
    parent_level: int = 0,
) -> List[Dict[str, Any]]:
    return renumber_structure(
        nodes=nodes,
        counters=counters,
        parent_level=parent_level,
        keep_transition_number=True,
    )


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
    output_format: str = "xml",
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
        "output_format": output_format,
    }
