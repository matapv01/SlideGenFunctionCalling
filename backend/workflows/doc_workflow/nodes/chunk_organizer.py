import time
from typing import Any, Dict, List, Tuple

from backend.config import THRESHOLD_CHAR_LIMIT
from backend.infrastructure.workflow_common import (
    create_context_map,
    create_slides_from_leaves,
    renumber_structure,
    render_slide_content,
)
from backend.workflows.doc_workflow.graph.stage import State

def organize_chunks(state: State) -> State:
    """
    Hàm hợp nhất xử lý đánh số lại cấu trúc tài liệu,
    nhóm nội dung vào các slide và sắp xếp chúng theo thứ tự cuối cùng đúng.
    Tạo slide giới thiệu, slide chuyển tiếp cho các tiêu đề cấp 1 và các slide nội dung.
    BỎ QUA đánh số nếu slide_chunks đã tồn tại (từ quá trình tạo ý tưởng).    """
    print("\n---------------- Node Organizing Chunks ----------------")

    start_time = time.time()

     # Check if slide_chunks already exists (idea-based workflow)
    if state.get('slide_chunks'):
        print("⏭️  Using pre-generated chunks from idea workflow")
        print(f"   Using {len(state['slide_chunks'])} pre-generated chunks")

        # Even for idea workflows, we need to ensure transition and thank you slides are properly set up
        slide_chunks = state['slide_chunks']


        state['slide_chunks'] = slide_chunks

        # Context maps — slide đầu luôn là INTRO SLIDE (planner sẽ dùng INTRO_TOOLS)
        if 'slide_context_maps' not in state or not state['slide_context_maps'] or len(state.get('slide_context_maps', [])) != len(slide_chunks):
            slide_context_maps = []
            for i, chunk in enumerate(slide_chunks):
                heading = chunk.get('heading', '')
                position = chunk.get('position', -99)
                slide_type = chunk.get('slide_type', '').lower()

                if i == 0:
                    # Slide đầu luôn là INTRO
                    context = f"[Slide 1] INTRO SLIDE"
                elif heading == 'TRANSITION' or position == -1 or slide_type == 'transition':
                    context = f"[Slide {i+1}] TRANSITION SLIDE"
                elif heading == 'THANK_YOU' or position == -2 or slide_type in ('thank_you', 'thankyou'):
                    context = f"[Slide {i+1}] THANK YOU SLIDE"
                else:
                    context = f"[Slide {i+1}] {heading}" if heading else f"[Slide {i+1}] Content Slide"
                slide_context_maps.append(context)

            state['slide_context_maps'] = slide_context_maps
            print(f"   ✓ Initialized {len(slide_context_maps)} context maps")

        context_maps = state.get('slide_context_maps', [])
        print(f"🗺️ slide_context_maps count: {len(context_maps)}")
        for i, context_map in enumerate(context_maps[:3], start=1):
            print(f"--- slide_context_map[{i}] ---\n{context_map}\n")

        return state

    document_structure = state.get("document_structure", [])
    document_title = state.get("document_title", "")
    slide_options = state.get('slide_options', {})
    print(f"🔧 DEBUG: Raw slide_options from state: {slide_options}")
    print(f"🔧 DEBUG: Type of slide_options: {type(slide_options)}")

    # Get options with defaults
    print(f"🔧 DEBUG: Raw slide_options from state: {slide_options}")
    print(f"🔧 DEBUG: Type of slide_options: {type(slide_options)}")
    if not document_structure:
        print("Document structure is empty. Skipping slide generation.")
        return state

    renumbered_structure = renumber_structure(document_structure)
    state["document_structure"] = renumbered_structure
    print("Successfully re-numbered the entire document structure.")


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
        print("Created intro slide with document title.")

    def _create_slides_from_leaves(parent: Dict[str, Any], leaves: List[Dict[str, Any]]) -> None:
        def _append_grouped_slide(
            content: str,
            pos: List[str],
            context_map: str,
            first_item_title: str,
        ) -> None:
            content_chunk = {
                "position": len(final_slides_content) + 1,
                "heading": parent.get("numbered_title", "") or first_item_title,
                "text_content": content,
            }
            final_slides_content.append(content_chunk)
            final_slides_positions.append(pos)
            final_slides_context_maps.append(context_map)

        create_slides_from_leaves(
            parent=parent,
            leaves=leaves,
            full_structure=renumbered_structure,
            threshold_char_limit=THRESHOLD_CHAR_LIMIT,
            include_parent_content_in_header=False,
            add_slide=_append_grouped_slide,
        )

    def _traverse_dfs(nodes: List[Dict[str, Any]]) -> None:
        for node in nodes:
            if node.get("content"):
                pos = [node.get("index", "")]
                content_text = render_slide_content("", [node])
                content_chunk = {
                    "position": len(final_slides_content) + 1,
                    "heading": node.get("numbered_title", node.get("title", "")),
                    "text_content": content_text,
                }
                final_slides_content.append(content_chunk)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(create_context_map(renumbered_structure, pos))

            leaves = [child for child in node.get("children", []) if not child.get("children")]
            if leaves:
                _create_slides_from_leaves(node, leaves)

            sub_trees = [child for child in node.get("children", []) if child.get("children")]
            if sub_trees:
                _traverse_dfs(sub_trees)

    _traverse_dfs(renumbered_structure)
    print(f"Grouping complete. Generated {len(final_slides_content)} slides (pre-sort).")

    def _get_version_key(pos_str):
        # Handle special positions: '0' for intro, 'X.T' for transitions, '999' for thank you
        if pos_str == '0':
            return (0,)  # Intro always first
        if pos_str == '999':
            return (999,)  # Thank you always last
        if pos_str.endswith('.T'):
            # Transition slides: extract the number before .T
            base = pos_str[:-2]
            try:
                key = tuple(map(int, base.split('.')))
                # Place transition just before its content (by adding a small decimal)
                return key + (0,)  # This ensures transition comes before content of same section
            except Exception as e:
                print(f"Error parsing transition position '{pos_str}': {e}")
                return ()
        try:
            return tuple(map(int, pos_str.split('.'))) + (1,)  # Content slides come after transitions
        except Exception as e:
            print(f"Error parsing position '{pos_str}': {e}")
            return ()

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
    print(f"Successfully sorted {len(sorted_chunks)} slides by their outline position.")
    print("Final slide chunks prepared for output.")

    for i, chunk in enumerate(sorted_chunks[:5]):
        print(f"\n--- Sample Slide Chunk {i+1} ---\n{chunk}\n")

    state["document_outline"] = renumbered_structure
    state["slide_chunks"] = list(sorted_chunks)
    state["slide_positions"] = list(sorted_positions)
    state["slide_context_maps"] = list(sorted_maps)

    print(f"🗺️ slide_context_maps count: {len(state['slide_context_maps'])}")
    for i, context_map in enumerate(state["slide_context_maps"][:3], start=1):
        print(f"--- slide_context_map[{i}] ---\n{context_map}\n")

    return state
