# src/nodes/chunk_organizer.py
import json
from typing import Dict, Any, List
from src.graph.stage import State
import time

THRESHOLD_CHAR_LIMIT = 1000

def organize_chunks(state: State) -> State:
    """
    Node 3: A consolidated function that handles renumbering the document structure,
    grouping content into slides, and sorting them into the correct final order.
    """
    print("\n---------------- Executing Node: organize_chunks ----------------")

    start_time = time.time()
    document_structure = state.get('document_structure', [])
    if not document_structure:
        print("Document structure is empty. Skipping slide generation.")
        return state

    # --- Part 1: Renumber Structure ---
    def _add_numbering_recursively(nodes, counters=None, parent_level=0):
        counters = [0] * 6 if counters is None else counters
        for node in nodes:
            counters[parent_level] += 1
            for i in range(parent_level + 1, len(counters)): counters[i] = 0
            index = ".".join(map(str, counters[:parent_level + 1]))
            node['index'] = index
            node['numbered_title'] = f"{index}. {node['title']}"
            node['level'] = parent_level + 1
            if node.get('children'):
                _add_numbering_recursively(node['children'], list(counters), parent_level + 1)
        return nodes

    renumbered_structure = _add_numbering_recursively(document_structure)
    state['document_structure'] = renumbered_structure
    print("Successfully re-numbered the entire document structure.")

    # --- Part 2: Group into Slides (Structure Grouper) ---
    final_slides_content, final_slides_positions, final_slides_context_maps = [], [], []

    def _create_context_map(outline_nodes, active_indices):
        map_lines = []
        def _generate(nodes, indent):
            for node in nodes:
                marker = " <--- YOU ARE HERE" if node.get("index") in active_indices else ""
                map_lines.append(f'{"  " * indent}{node.get("index", "")}. {node.get("title", "")}{marker}')
                if node.get("children"): _generate(node["children"], indent + 1)
        _generate(outline_nodes, 0)
        return "\n".join(map_lines)

    def _render_slide_content(group_header, items):
        parts = [group_header] if group_header else []
        if len(items) > 1:
            for item in items:
                parts.append(f"\n\t- {item.get('title', '')}")
                if item.get('content'):
                    indented = "\n\t  ".join(item['content'].splitlines())
                    parts.append(f"\t  {indented}")
        else:
            item = items[0]
            parts.append(f"\n{item.get('numbered_title', item.get('title', ''))}")
            if item.get('content'): parts.append(f"{item['content']}")
        return "\n".join(parts)

    def _create_slides_from_leaves(parent, leaves):
        if not leaves: return
        buffer = []
        header = parent.get('numbered_title', '')
        for item in leaves:
            tentative_buffer = buffer + [item]
            if len(_render_slide_content(header, tentative_buffer)) > THRESHOLD_CHAR_LIMIT and buffer:
                content = _render_slide_content(header, buffer)
                pos = [i.get('index', '') for i in buffer]
                final_slides_content.append(content)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))
                buffer = [item]
            else:
                buffer.append(item)
        if buffer:
            content = _render_slide_content(header, buffer)
            pos = [i.get('index', '') for i in buffer]
            final_slides_content.append(content)
            final_slides_positions.append(pos)
            final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))

    def _traverse_dfs(nodes):
        for node in nodes:
            if node.get("content"):
                pos = [node.get('index', '')]
                final_slides_content.append(_render_slide_content("", [node]))
                final_slides_positions.append(pos)
                final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))
            leaves = [child for child in node.get("children", []) if not child.get("children")]
            if leaves: _create_slides_from_leaves(node, leaves)
            sub_trees = [child for child in node.get("children", []) if child.get("children")]
            if sub_trees: _traverse_dfs(sub_trees)

    _traverse_dfs(renumbered_structure)
    print(f"Grouping complete. Generated {len(final_slides_content)} slides (pre-sort).")

    # --- Part 3: Sort Slides ---
    def _get_version_key(pos_str):
        try: return tuple(map(int, pos_str.split('.')))
        except: return ()

    combined = list(zip(final_slides_content, final_slides_positions, final_slides_context_maps))
    def sort_key(slide_data):
        return _get_version_key(slide_data[1][0]) if slide_data[1] else ()

    sorted_combined = sorted(combined, key=sort_key)

    if sorted_combined:
        sorted_chunks, sorted_positions, sorted_maps = zip(*sorted_combined)
    else:
        sorted_chunks, sorted_positions, sorted_maps = [], [], []

    end_time = time.time()
    print(f"Slide organization took {end_time - start_time:.2f} seconds.")
    print(f"Successfully sorted {len(sorted_chunks)} slides by their outline position.")
    print(f"Final slide chunks prepared for output.")
    for i, chunk in enumerate(sorted_chunks[:2]):
        print(f"\n--- Sample Slide Chunk {i+1} ---\n{chunk}\n")
    # --- Final State Update ---
    state['document_outline'] = renumbered_structure
    state['slide_chunks'] = list(sorted_chunks)
    state['slide_positions'] = list(sorted_positions)
    state['slide_context_maps'] = list(sorted_maps)

    return state