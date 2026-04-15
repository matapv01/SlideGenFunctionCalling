from typing import Any, Callable, Dict, List, Optional


def renumber_structure(
    nodes: List[Dict[str, Any]],
    counters: Optional[List[int]] = None,
    parent_level: int = 0,
    keep_transition_number: bool = False,
) -> List[Dict[str, Any]]:
    """Assign hierarchical index/numbered_title recursively."""
    counters = [0] * 6 if counters is None else counters

    for node in nodes:
        is_transition = node.get("is_transition") is True

        counters[parent_level] += 1
        for i in range(parent_level + 1, len(counters)):
            counters[i] = 0

        index = ".".join(map(str, counters[: parent_level + 1]))
        node["index"] = index
        node["numbered_title"] = f"{index}. {node.get('title', '')}"
        node["level"] = parent_level + 1

        # For transition slides, keep same number for subsequent children/content.
        if keep_transition_number and is_transition:
            counters[parent_level] -= 1

        if node.get("children"):
            renumber_structure(
                node["children"],
                list(counters),
                parent_level + 1,
                keep_transition_number=keep_transition_number,
            )

    return nodes


def create_context_map(outline_nodes: List[Dict[str, Any]], active_indices: List[str]) -> str:
    """Generate TOC-like context map and mark active indices."""
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


def render_slide_content(group_header: str, items: List[Dict[str, Any]]) -> str:
    """Render one slide text block from grouped items."""
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


def create_slides_from_leaves(
    parent: Dict[str, Any],
    leaves: List[Dict[str, Any]],
    full_structure: List[Dict[str, Any]],
    threshold_char_limit: int,
    add_slide: Callable[[str, List[str], str, str], None],
    include_parent_content_in_header: bool = False,
) -> None:
    """Group leaf nodes into chunks under threshold, and emit via callback."""
    if not leaves:
        return

    buffer: List[Dict[str, Any]] = []
    header_parts = [parent.get("numbered_title", "")]
    if include_parent_content_in_header and parent.get("content"):
        header_parts.append(parent["content"])
    header = "\n".join(header_parts)

    for item in leaves:
        tentative_buffer = buffer + [item]
        if len(render_slide_content(header, tentative_buffer)) > threshold_char_limit and buffer:
            content = render_slide_content(header, buffer)
            pos = [i.get("index", "") for i in buffer]
            context_map = create_context_map(full_structure, pos)
            first_item_title = str(buffer[0].get("title", "")) if buffer else ""
            add_slide(content, pos, context_map, first_item_title)
            buffer = [item]
        else:
            buffer.append(item)

    if buffer:
        content = render_slide_content(header, buffer)
        pos = [i.get("index", "") for i in buffer]
        context_map = create_context_map(full_structure, pos)
        first_item_title = str(buffer[0].get("title", "")) if buffer else ""
        add_slide(content, pos, context_map, first_item_title)
