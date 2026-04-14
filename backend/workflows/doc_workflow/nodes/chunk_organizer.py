import time
from typing import Any, Dict, List, Tuple

from backend.config import THRESHOLD_CHAR_LIMIT
from backend.workflows.doc_workflow.graph.stage import State

def organize_chunks(state: State) -> State:
    """
    Renumber document structure and group content into ordered slide chunks.
    """
    print("\n---------------- Node Organizing Chunks ----------------")

    start_time = time.time()

    if state.get("slide_chunks"):
        print("Using pre-generated chunks from idea workflow")
        slide_chunks = state["slide_chunks"]
        state["slide_chunks"] = slide_chunks

        if (
            "slide_context_maps" not in state
            or not state["slide_context_maps"]
            or len(state.get("slide_context_maps", [])) != len(slide_chunks)
        ):
            # Defer generic context-map generation to planning node.
            state["slide_context_maps"] = []

        return state

    document_structure = state.get("document_structure", [])
    document_title = state.get("document_title", "")

    if not document_structure:
        print("Document structure is empty. Skipping slide generation.")
        return state

    def _add_numbering_recursively(
        nodes: List[Dict[str, Any]], counters: List[int] | None = None, parent_level: int = 0
    ) -> List[Dict[str, Any]]:
        counters = [0] * 6 if counters is None else counters
        for node in nodes:
            counters[parent_level] += 1
            for i in range(parent_level + 1, len(counters)):
                counters[i] = 0
            index = ".".join(map(str, counters[: parent_level + 1]))
            node["index"] = index
            node["numbered_title"] = f"{index}. {node['title']}"
            node["level"] = parent_level + 1
            if node.get("children"):
                _add_numbering_recursively(node["children"], list(counters), parent_level + 1)
        return nodes

    renumbered_structure = _add_numbering_recursively(document_structure)
    state["document_structure"] = renumbered_structure

    final_slides_content: List[Dict[str, Any]] = []
    final_slides_positions: List[List[str]] = []
    final_slides_context_maps: List[str] = []

    if document_title:
        intro_chunk = {
            "position": 0,
            "heading": "INTRO",
            "text_content": f"Title: {document_title}",
        }
        final_slides_content.append(intro_chunk)
        final_slides_positions.append(["0"])
        final_slides_context_maps.append("INTRO SLIDE")

    def _create_context_map(outline_nodes: List[Dict[str, Any]], active_indices: List[str]) -> str:
        map_lines: List[str] = []

        def _generate(nodes: List[Dict[str, Any]], indent: int) -> None:
            for node in nodes:
                marker = " <--- YOU ARE HERE" if node.get("index") in active_indices else ""
                map_lines.append(
                    f"{'  ' * indent}{node.get('index', '')}. {node.get('title', '')}{marker}"
                )
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

    def _create_slides_from_leaves(parent: Dict[str, Any], leaves: List[Dict[str, Any]]) -> None:
        if not leaves:
            return

        buffer: List[Dict[str, Any]] = []
        header = parent.get("numbered_title", "")

        for item in leaves:
            tentative_buffer = buffer + [item]
            if len(_render_slide_content(header, tentative_buffer)) > THRESHOLD_CHAR_LIMIT and buffer:
                content_text = _render_slide_content(header, buffer)
                pos = [i.get("index", "") for i in buffer]
                content_chunk = {
                    "position": len(final_slides_content) + 1,
                    "heading": header or buffer[0].get("title", ""),
                    "text_content": content_text,
                }
                final_slides_content.append(content_chunk)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))
                buffer = [item]
            else:
                buffer.append(item)

        if buffer:
            content_text = _render_slide_content(header, buffer)
            pos = [i.get("index", "") for i in buffer]
            content_chunk = {
                "position": len(final_slides_content) + 1,
                "heading": header or buffer[0].get("title", ""),
                "text_content": content_text,
            }
            final_slides_content.append(content_chunk)
            final_slides_positions.append(pos)
            final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))

    def _traverse_dfs(nodes: List[Dict[str, Any]]) -> None:
        for node in nodes:
            if node.get("content"):
                pos = [node.get("index", "")]
                content_text = _render_slide_content("", [node])
                content_chunk = {
                    "position": len(final_slides_content) + 1,
                    "heading": node.get("numbered_title", node.get("title", "")),
                    "text_content": content_text,
                }
                final_slides_content.append(content_chunk)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))

            leaves = [child for child in node.get("children", []) if not child.get("children")]
            if leaves:
                _create_slides_from_leaves(node, leaves)

            sub_trees = [child for child in node.get("children", []) if child.get("children")]
            if sub_trees:
                _traverse_dfs(sub_trees)

    _traverse_dfs(renumbered_structure)

    def _get_version_key(pos_str: str) -> Tuple[int, ...]:
        if pos_str == "0":
            return (0,)
        if pos_str == "999":
            return (999,)
        if pos_str.endswith(".T"):
            base = pos_str[:-2]
            return tuple(map(int, base.split("."))) + (0,)
        return tuple(map(int, pos_str.split("."))) + (1,)

    combined = list(zip(final_slides_content, final_slides_positions, final_slides_context_maps))

    def sort_key(slide_data: Tuple[Dict[str, Any], List[str], str]) -> Tuple[int, ...]:
        return _get_version_key(slide_data[1][0]) if slide_data[1] else tuple()

    sorted_combined = sorted(combined, key=sort_key)

    if sorted_combined:
        sorted_chunks, sorted_positions, sorted_maps = zip(*sorted_combined)
    else:
        sorted_chunks, sorted_positions, sorted_maps = [], [], []

    end_time = time.time()
    print(f"Slide organization took {end_time - start_time:.2f} seconds.")

    state["document_outline"] = renumbered_structure
    state["slide_chunks"] = list(sorted_chunks)
    state["slide_positions"] = list(sorted_positions)
    state["slide_context_maps"] = list(sorted_maps)

    return state
