# File: src/nodes/chunk_organizer.py

from backend.workflows.slidegen_workflow.graph.stage import State
import time
from backend.config import THRESHOLD_CHAR_LIMIT


def organize_chunks(state: State) -> State:
    """
    Hàm hợp nhất xử lý đánh số lại cấu trúc tài liệu,
    nhóm nội dung vào các slide và sắp xếp chúng theo thứ tự cuối cùng đúng.
    Tạo slide giới thiệu, slide chuyển tiếp cho các tiêu đề cấp 1 và các slide nội dung.
    BỎ QUA đánh số nếu slide_chunks đã tồn tại (từ quá trình tạo ý tưởng).
    """
    print("\n---------------- Node Organizing Chunks ----------------")

    start_time = time.time()

    # Check if slide_chunks already exists (idea-based workflow)
    if state.get('slide_chunks'):
        print("⏭️  Using pre-generated chunks from idea workflow")
        print(f"   Using {len(state['slide_chunks'])} pre-generated chunks")

        # Even for idea workflows, we need to ensure transition and thank you slides are properly set up
        slide_chunks = state['slide_chunks']
        slide_options = state.get('slide_options', {})

        # Get options with defaults
        enable_transition_slides = slide_options.get('enable_transition_slides', True)
        enable_thank_you_slide = slide_options.get('enable_thank_you_slide', True)

        print(f"✅ Slide options: transitions={enable_transition_slides}, thank_you={enable_thank_you_slide}")

        # Verify and ensure transition/thank you slides match options
        has_transitions = any(chunk.get('position') == -1 or chunk.get('heading') == 'TRANSITION' for chunk in slide_chunks)
        has_thank_you = any(chunk.get('position') == -2 or chunk.get('heading') == 'THANK_YOU' for chunk in slide_chunks)

        print(f"   Current state - Transitions: {has_transitions}, Thank you: {has_thank_you}")

        # If transitions disabled but present, remove them
        if not enable_transition_slides and has_transitions:
            slide_chunks = [c for c in slide_chunks if c.get('position') != -1 and c.get('heading') != 'TRANSITION']
            print("   ✓ Removed transition slides (disabled in options)")

        # If thank you disabled but present, remove it
        if not enable_thank_you_slide and has_thank_you:
            slide_chunks = [c for c in slide_chunks if c.get('position') != -2 and c.get('heading') != 'THANK_YOU']
            print("   ✓ Removed thank you slide (disabled in options)")

        # If transitions enabled but MISSING, auto-create one between intro and content
        if enable_transition_slides and not has_transitions and len(slide_chunks) > 1:
            # Get first content heading for transition title
            first_content = next((c for c in slide_chunks if c.get('position', 0) > 0), None)
            if first_content:
                heading = first_content.get('heading', 'Content')
                transition_chunk = {
                    'position': -1,
                    'heading': heading,
                    'text_content': heading,
                    'is_auto_created': True
                }
                slide_chunks.insert(1, transition_chunk)  # After intro
                print("   ✓ Auto-created transition slide")

        # If thank you enabled but MISSING, add at end
        if enable_thank_you_slide and not has_thank_you:
            thank_you_chunk = {
                'position': -2,
                'heading': 'THANK_YOU',
                'text_content': 'Thank you for your attention!',
                'is_auto_created': True
            }
            slide_chunks.append(thank_you_chunk)
            print("   ✓ Auto-created thank you slide")

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

        return state

    document_structure = state.get('document_structure', [])
    document_title = state.get('document_title', '')
    slide_options = state.get('slide_options', {})

    print(f"🔧 DEBUG: Raw slide_options from state: {slide_options}")
    print(f"🔧 DEBUG: Type of slide_options: {type(slide_options)}")

    # Get options with defaults
    enable_transition_slides = slide_options.get('enable_transition_slides', True)
    enable_thank_you_slide = slide_options.get('enable_thank_you_slide', True)

    print(f"✅ Slide options: transitions={enable_transition_slides}, thank_you={enable_thank_you_slide}")

    if not document_structure:
        print("Document structure is empty. Skipping slide generation.")
        return state

    # --- Part 1: Renumber Structure ---
    def _add_numbering_recursively(nodes, counters=None, parent_level=0):
        counters = [0] * 6 if counters is None else counters
        for node in nodes:
            counters[parent_level] += 1
            for i in range(parent_level + 1, len(counters)):
                counters[i] = 0
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

    # Create intro slide first
    if document_title:
        intro_chunk = {
            'position': 0,
            'heading': 'INTRO',
            'text_content': f"Title: {document_title}"
        }
        final_slides_content.append(intro_chunk)
        final_slides_positions.append(['0'])  # Special position for intro
        final_slides_context_maps.append("INTRO SLIDE")
        print("Created intro slide with document title.")

    def _create_context_map(outline_nodes, active_indices):
        map_lines = []

        def _generate(nodes, indent):
            for node in nodes:
                marker = " <--- YOU ARE HERE" if node.get("index") in active_indices else ""
                map_lines.append(f'{"  " * indent}{node.get("index", "")}. {node.get("title", "")}{marker}')
                if node.get("children"):
                    _generate(node["children"], indent + 1)
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
            if item.get('content'):
                parts.append(f"{item['content']}")
        return "\n".join(parts)

    def _create_slides_from_leaves(parent, leaves):
        if not leaves:
            return
        buffer = []
        header = parent.get('numbered_title', '')
        for item in leaves:
            tentative_buffer = buffer + [item]
            if len(_render_slide_content(header, tentative_buffer)) > THRESHOLD_CHAR_LIMIT and buffer:
                content_text = _render_slide_content(header, buffer)
                pos = [i.get('index', '') for i in buffer]
                content_chunk = {
                    'position': len(final_slides_content) + 1,
                    'heading': header or buffer[0].get('title', ''),
                    'text_content': content_text
                }
                final_slides_content.append(content_chunk)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))
                buffer = [item]
            else:
                buffer.append(item)
        if buffer:
            content_text = _render_slide_content(header, buffer)
            pos = [i.get('index', '') for i in buffer]
            content_chunk = {
                'position': len(final_slides_content) + 1,  # Sequential position
                'heading': header or buffer[0].get('title', ''),
                'text_content': content_text
            }
            final_slides_content.append(content_chunk)
            final_slides_positions.append(pos)
            final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))

    def _traverse_dfs(nodes, is_root_level=False):
        for node in nodes:
            # Create transition slide for level 1 headings (root level) - if enabled
            if enable_transition_slides and is_root_level and node.get('level') == 1:
                transition_chunk = {
                    'position': -1,  # Special position for transitions
                    'heading': node.get('numbered_title', node.get('title', '')),
                    'text_content': node.get('numbered_title', node.get('title', ''))
                }
                pos = [f"{node.get('index', '')}.T"]  # Special marker for transition
                final_slides_content.append(transition_chunk)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(_create_context_map(renumbered_structure, [node.get('index', '')]))
                print(f"Created transition slide for: {node.get('numbered_title', '')}")

            if node.get("content"):
                pos = [node.get('index', '')]
                content_text = _render_slide_content("", [node])
                content_chunk = {
                    'position': len(final_slides_content) + 1,
                    'heading': node.get('numbered_title', node.get('title', '')),
                    'text_content': content_text
                }
                final_slides_content.append(content_chunk)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))
            leaves = [child for child in node.get("children", []) if not child.get("children")]
            if leaves:
                _create_slides_from_leaves(node, leaves)
            sub_trees = [child for child in node.get("children", []) if child.get("children")]
            if sub_trees:
                _traverse_dfs(sub_trees, is_root_level=False)

    _traverse_dfs(renumbered_structure, is_root_level=True)

    # Add thank you slide at the end (if enabled)
    if enable_thank_you_slide:
        thank_you_chunk = {
            'position': -2,  # Special position for thank you
            'heading': 'THANK_YOU',
            'text_content': 'Thank you for your attention!'
        }
        final_slides_content.append(thank_you_chunk)
        final_slides_positions.append(['999'])  # Special position for thank you (always last)
        final_slides_context_maps.append("THANK YOU SLIDE")
        print("Created thank you slide.")

    print(f"Grouping complete. Generated {len(final_slides_content)} slides (pre-sort).")

    # --- Part 3: Sort Slides ---
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
    print("Final slide chunks prepared for output.")

    # Show samples
    for i, chunk in enumerate(sorted_chunks[:5]):
        print(f"\n--- Sample Slide Chunk {i+1} ---\n{chunk}\n")

    # --- Final State Update ---
    state['document_outline'] = renumbered_structure
    state['slide_chunks'] = list(sorted_chunks)
    state['slide_positions'] = list(sorted_positions)
    state['slide_context_maps'] = list(sorted_maps)

    return state
