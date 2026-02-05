from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging
import json
from web.backend.app.config import TEMP_DIR
from web.backend.app.schemas import StructureUpdateRequest, StructureApproveRequest

router = APIRouter(prefix="/structure", tags=["STRUCTURE"])
logger = logging.getLogger("SlideGen-structure")

# In-memory storage for structure editor sessions
structure_sessions = {}


@router.get("/current")
async def get_current_structure(session_id: str):
    """Get current document structure and text for editing"""
    logger.info(f"📋 Getting structure for session: {session_id}")

    # Check if session exists
    if session_id not in structure_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = structure_sessions[session_id]

    return JSONResponse(content={
        "document_title": session_data.get("document_title", "Untitled"),
        "document_text": session_data.get("document_text", ""),  # Full plain text for selection
        "document_structure": session_data.get("document_structure", []),
        "can_edit": True
    })


@router.put("/update")
async def update_structure(request: StructureUpdateRequest):
    """Update document structure in session"""
    logger.info(f"💾 Updating structure for session: {request.session_id}")

    # Update session in memory
    if request.session_id not in structure_sessions:
        structure_sessions[request.session_id] = {}

    structure_sessions[request.session_id]["document_structure"] = request.document_structure

    # EXTRACT document_title from intro_slide
    document_title = "Untitled Document"
    if request.intro_slide:
        document_title = request.intro_slide.content or "Untitled Document"
        logger.info(f"📌 Document title: {document_title}")

    # PREPEND intro_slide if exists
    raw_structure = []
    if request.intro_slide:
        raw_structure.append(request.intro_slide.dict())

    # Add document structure
    raw_structure.extend([node.dict() for node in request.document_structure])

    # MERGE title + content nodes BEFORE saving
    def merge_title_content_nodes(nodes):
        """Merge consecutive title/content node pairs into single nodes"""
        merged = []
        i = 0

        while i < len(nodes):
            node = nodes[i]
            node_dict = node if isinstance(node, dict) else node

            # Check if this is a title node (has title, empty/missing content)
            has_title = node_dict.get('title', '').strip() != ''
            has_no_content = not node_dict.get('content', '').strip()

            # Check if next node is content node (has content, empty/missing title)
            is_next_content = False
            if i + 1 < len(nodes):
                next_node = nodes[i + 1]
                next_dict = next_node if isinstance(next_node, dict) else next_node
                has_no_title = not next_dict.get('title', '').strip()
                has_content = next_dict.get('content', '').strip() != ''
                same_level = next_dict.get('level') == node_dict.get('level')
                is_next_content = has_no_title and has_content and same_level

            # Merge if current is title and next is content
            if has_title and has_no_content and is_next_content:
                next_node = nodes[i + 1]
                next_dict = next_node if isinstance(next_node, dict) else next_node
                merged_node = {
                    'level': node_dict.get('level'),
                    'title': node_dict.get('title'),
                    'content': next_dict.get('content'),
                    'children': merge_title_content_nodes(node_dict.get('children', [])),
                    'is_transition': node_dict.get('is_transition', False)
                }
                merged.append(merged_node)
                i += 2  # Skip next node as it's been merged
            else:
                # Keep node as-is, but recurse into children
                merged_node = {
                    'level': node_dict.get('level'),
                    'title': node_dict.get('title', ''),
                    'content': node_dict.get('content', ''),
                    'children': merge_title_content_nodes(node_dict.get('children', [])),
                    'is_transition': node_dict.get('is_transition', False)
                }
                merged.append(merged_node)
                i += 1

        return merged

    # SAVE TO FILE with merged format
    try:
        # Ensure TEMP_DIR exists
        TEMP_DIR.mkdir(parents=True, exist_ok=True)

        structure_file = TEMP_DIR / f"structure_{request.session_id}.json"

        # Merge title/content pairs
        merged_structure = merge_title_content_nodes(raw_structure)

        structure_data = {
            "session_id": request.session_id,
            "document_title": document_title,  # Save title here!
            "document_structure": merged_structure
        }

        # Save to file
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(structure_data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Structure updated: {request.session_id} ({len(raw_structure)} nodes → {len(merged_structure)} merged)")
        logger.info(f"📁 Saved to file: {structure_file}")

    except Exception as e:
        logger.error(f"Error saving structure to file: {e}")
        import traceback
        logger.error(traceback.format_exc())

    return JSONResponse(content={"success": True})


@router.post("/approve")
async def approve_structure(request: StructureApproveRequest):
    """
    Approve structure and generate slide chunks using chunk_organizer logic.
    Returns State-compatible output for downstream slide generation.
    """
    logger.info(f"✅ Approving structure for session: {request.session_id}")

    THRESHOLD_CHAR_LIMIT = 1000

    try:
        # ======================== Load Structure ========================
        structure_file = TEMP_DIR / f"structure_{request.session_id}.json"

        if not structure_file.exists():
            logger.warning(f"No structure found for session: {request.session_id}")
            return JSONResponse(content={
                "success": False,
                "message": "No structure found for this session"
            }, status_code=404)

        with open(structure_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        document_structure = data.get('document_structure', [])
        document_title = data.get('document_title', 'Untitled Document')

        logger.info(f"📋 Loaded structure: {len(document_structure)} nodes")
        logger.info(f"📄 Document title: {document_title}")

        # ======================== Extract Special Slides ========================

        # Extract intro slide from level 0
        intro_slide = None
        intro_node = None
        filtered_structure = []

        for node in document_structure:
            if node.get('level') == 0:
                intro_node = node
            else:
                filtered_structure.append(node)

        if intro_node:
            intro_slide = f"INTRO SLIDE\n\nTitle: {intro_node.get('content', '')}"
            logger.info(f"✅ Extracted intro slide from level 0: {intro_node.get('content')}")

        # Extract thank you slide (hybrid approach)
        thank_you_slide = None
        thank_you_node = None

        if filtered_structure and len(filtered_structure) > 0:
            last_node = filtered_structure[-1]
            # Check if last node title contains any thank you keyword
            thank_you_keywords = ['thank', 'thanks', 'thank you', 'cảm ơn', 'cam on']
            if any(keyword in last_node.get('title', '').lower() for keyword in thank_you_keywords):
                thank_you_node = last_node
                filtered_structure = filtered_structure[:-1]  # Remove from structure
                thank_you_slide = f"THANK YOU SLIDE\n\n{thank_you_node.get('title', '')}\n\n{thank_you_node.get('content', '')}"
                logger.info(f"✅ Extracted thank you slide from last node: {thank_you_node.get('title')}")

        document_structure = filtered_structure

        # ======================== Renumber Structure ========================

        def _add_numbering_recursively(nodes, counters=None, parent_level=0):
            counters = [0] * 6 if counters is None else counters
            for node in nodes:
                # For transition nodes: peek at next index (increment then decrement)
                if node.get('is_transition') is True:
                    # Temporarily increment to get the "next" index
                    counters[parent_level] += 1
                    for i in range(parent_level + 1, len(counters)):
                        counters[i] = 0

                    # Assign index
                    index = ".".join(map(str, counters[:parent_level + 1]))
                    node['index'] = index
                    node['numbered_title'] = f"{index}. {node['title']}"
                    node['level'] = parent_level + 1

                    # Decrement back (so next content node gets same index)
                    counters[parent_level] -= 1
                else:
                    # For content nodes: normal increment
                    counters[parent_level] += 1
                    for i in range(parent_level + 1, len(counters)):
                        counters[i] = 0

                    # Assign index
                    index = ".".join(map(str, counters[:parent_level + 1]))
                    node['index'] = index
                    node['numbered_title'] = f"{index}. {node['title']}"
                    node['level'] = parent_level + 1

                if node.get('children'):
                    _add_numbering_recursively(node['children'], list(counters), parent_level + 1)
            return nodes

        renumbered_structure = _add_numbering_recursively(document_structure)
        logger.info(f"✅ Renumbered structure")

        # ======================== Generate Slides ========================

        final_slides_content = []
        final_slides_positions = []
        final_slides_context_maps = []
        final_slides_types = []

        # Add intro slide first
        if intro_slide:
            final_slides_content.append(intro_slide)
            final_slides_positions.append(['0'])
            final_slides_context_maps.append("INTRO SLIDE")
            final_slides_types.append('intro')
            logger.info("✅ Added intro slide")

        # Helper functions
        def _create_context_map(outline_nodes, active_indices):
            map_lines = []
            # Ensure active_indices is a list
            if not isinstance(active_indices, list):
                active_indices = [active_indices]

            def _generate(nodes, indent):
                for node in nodes:
                    node_index = node.get("index", "")
                    # Check if this node's index is in active_indices
                    marker = " <--- YOU ARE HERE" if node_index in active_indices else ""
                    map_lines.append(f'{"  " * indent}{node_index}. {node.get("title", "")}{marker}')
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
            # Include parent's title AND content in header
            header_parts = [parent.get('numbered_title', '')]
            if parent.get('content'):
                header_parts.append(parent['content'])
            header = '\n'.join(header_parts)

            for item in leaves:
                tentative_buffer = buffer + [item]
                if len(_render_slide_content(header, tentative_buffer)) > THRESHOLD_CHAR_LIMIT and buffer:
                    content = _render_slide_content(header, buffer)
                    pos = [i.get('index', '') for i in buffer]
                    final_slides_content.append(content)
                    final_slides_positions.append(pos)
                    final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))
                    final_slides_types.append('content')
                    buffer = [item]
                else:
                    buffer.append(item)
            if buffer:
                content = _render_slide_content(header, buffer)
                pos = [i.get('index', '') for i in buffer]
                final_slides_content.append(content)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))
                final_slides_types.append('content')

        def _traverse_dfs(nodes, is_root_level=False):
            for node in nodes:
                try:
                    # Create transition slide ONLY if is_transition=true
                    if is_root_level and node.get('is_transition') is True:
                        transition_content = f"TRANSITION SLIDE\n\n{node.get('numbered_title', node.get('title', ''))}"
                        pos = [f"{node.get('index', '')}.T"]
                        final_slides_content.append(transition_content)
                        final_slides_positions.append(pos)

                        node_index_list = [node.get('index', '')]
                        logger.info(f"🔍 Creating transition context map with indices: {node_index_list} (type: {type(node_index_list)})")
                        context_map = _create_context_map(renumbered_structure, node_index_list)
                        final_slides_context_maps.append(context_map)
                        final_slides_types.append('transition')
                        logger.info(f"✅ Created transition slide: {node.get('numbered_title', '')}")
                    # Check if node has children
                    has_leaves = any(not child.get("children") for child in node.get("children", []))
                    has_sub_trees = any(child.get("children") for child in node.get("children", []))

                    # Process content ONLY for non-transition nodes WITHOUT children
                    # If node has children, content will be merged via _create_slides_from_leaves
                    if node.get("content") and node.get('is_transition') is not True and not has_leaves and not has_sub_trees:
                        pos = [node.get('index', '')]
                        final_slides_content.append(_render_slide_content("", [node]))
                        final_slides_positions.append(pos)

                        logger.info(f"🔍 Creating content context map with indices: {pos} (type: {type(pos)})")
                        context_map = _create_context_map(renumbered_structure, pos)
                        final_slides_context_maps.append(context_map)
                        final_slides_types.append('content')

                    # Process children
                    leaves = [child for child in node.get("children", []) if not child.get("children")]
                    if leaves:
                        _create_slides_from_leaves(node, leaves)

                    sub_trees = [child for child in node.get("children", []) if child.get("children")]
                    if sub_trees:
                        _traverse_dfs(sub_trees, is_root_level=False)

                except Exception as e:
                    logger.error(f"❌ Error in _traverse_dfs for node {node.get('title')}: {e}")
                    logger.error(f"   Node data: {node}")
                    import traceback
                    logger.error(traceback.format_exc())
                    raise

        # Traverse structure and create content slides
        _traverse_dfs(renumbered_structure, is_root_level=True)

        # Add thank you slide at the end
        if thank_you_slide:
            final_slides_content.append(thank_you_slide)
            final_slides_positions.append(['999'])
            final_slides_context_maps.append("THANK YOU SLIDE")
            final_slides_types.append('thank_you')
            logger.info("✅ Added thank you slide")

        logger.info(f"✅ Generated {len(final_slides_content)} slides:")
        logger.info(f"   - Intro: {final_slides_types.count('intro')}")
        logger.info(f"   - Transitions: {final_slides_types.count('transition')}")
        logger.info(f"   - Content: {final_slides_types.count('content')}")
        logger.info(f"   - Thank You: {final_slides_types.count('thank_you')}")
        
        # ======================== Sort Slides ========================
        
        def _get_version_key(pos_str):
            # Type safety: ensure pos_str is a string
            if isinstance(pos_str, (list, tuple)):
                logger.warning(f"⚠️ _get_version_key received {type(pos_str)}: {pos_str}, converting to string")
                pos_str = str(pos_str[0]) if pos_str else '0'
            
            pos_str = str(pos_str)  # Force to string
            
            if pos_str == '0':
                return (0,)
            if pos_str == '999':
                return (999999,)
            if pos_str.endswith('.T'):
                # Transition slides: place before content of same section
                parts = pos_str[:-2].split('.')
                return tuple(int(p) for p in parts) + (0,)  # e.g. "1.T" → (1, 0)
            
            # Content slides: place after transitions
            parts = pos_str.split('.')
            return tuple(int(p) for p in parts) + (1,)  # e.g. "1" → (1, 1)
        
        combined = list(zip(final_slides_content, final_slides_positions, final_slides_context_maps, final_slides_types))
        
        def sort_key(slide_data):
            return _get_version_key(slide_data[1][0]) if slide_data[1] else ()
        
        sorted_combined = sorted(combined, key=sort_key)
        
        if sorted_combined:
            sorted_chunks, sorted_positions, sorted_maps, sorted_types = zip(*sorted_combined)
        else:
            sorted_chunks, sorted_positions, sorted_maps, sorted_types = [], [], [], []
        
        logger.info(f"✅ Sorted {len(sorted_chunks)} slides")
        
        # Log samples
        for i, (chunk, slide_type) in enumerate(list(zip(sorted_chunks, sorted_types))[:3]):
            logger.info(f"\n--- Sample Slide {i+1} ({slide_type}) ---\n{chunk[:200]}...\n")
        
        # ======================== Save Results to File ========================
        
        # CONVERT slide_chunks to workflow-compatible format
        # slide_planner expects dicts with: position, heading, text_content
        converted_chunks = []
        for i, (chunk_text, chunk_type, positions) in enumerate(zip(sorted_chunks, sorted_types, sorted_positions)):
            # Determine position value based on type
            if chunk_type == 'intro':
                position = 0
            elif chunk_type == 'transition':
                position = -1
            elif chunk_type == 'thank_you':
                position = -2
            else:
                position = i  # Content slides get sequential position
            
            # Extract heading from chunk text (first line usually)
            lines = chunk_text.strip().split('\n')
            if chunk_type == 'intro':
                heading = 'INTRO'
            elif chunk_type == 'transition':
                heading = 'TRANSITION'
            elif chunk_type == 'thank_you':
                heading = 'THANK_YOU'
            else:
                # For content, extract heading from first line
                heading = lines[0] if lines else ''
                # Remove numbering if present (e.g. "1.2. Title" -> "Title")
                import re
                heading = re.sub(r'^\d+(\.\d+)*\.?\s*', '', heading)
            
            # Create workflow-compatible chunk dict
            chunk_dict = {
                'position': position,
                'heading': heading,
                'text_content': chunk_text
            }
            converted_chunks.append(chunk_dict)
        
        logger.info(f"✅ Converted {len(converted_chunks)} chunks to workflow format")
        
        # Log sample converted chunk
        if converted_chunks:
            logger.info(f"Sample converted chunk: {converted_chunks[0]}")
        
        try:
            # Save approved result to file for debugging/monitoring
            approved_file = TEMP_DIR / f"approved_structure_{request.session_id}.json"
            
            result_data = {
                "success": True,
                "message": "Structure approved successfully",
                "session_id": request.session_id,
                "document_title": document_title,
                "document_outline": renumbered_structure,
                "slide_chunks": converted_chunks,  # Use converted format
                "slide_positions": list(sorted_positions),
                "slide_context_maps": list(sorted_maps),
                "slide_types": list(sorted_types)
            }
            
            with open(approved_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved approved result to: {approved_file}")
            
        except Exception as e:
            logger.error(f"⚠️ Error saving approved result to file: {e}")
        
        # ======================== Return State Output ========================
        
        return JSONResponse(content={
            "success": True,
            "message": "Structure approved successfully",
            "session_id": request.session_id,
            "document_title": document_title,
            "document_outline": renumbered_structure,
            "slide_chunks": converted_chunks,  # Return converted format
            "slide_positions": list(sorted_positions),
            "slide_context_maps": list(sorted_maps),
            "slide_types": list(sorted_types)
        })
        
    except Exception as e:
        logger.error(f"Error approving structure: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(content={
            "success": False,
            "message": f"Error processing structure: {str(e)}"
        }, status_code=500)


@router.post("/test-session")
async def create_test_session():
    """Create test session with sample structure for testing"""
    import uuid
    session_id = str(uuid.uuid4())
    
    # Sample structure
    structure_sessions[session_id] = {
        "document_title": "Test Document - Manual Structure Editor",
        "document_structure": [
            {
                "level": 1,
                "title": "Giới thiệu",
                "content": "Đây là phần giới thiệu của tài liệu. Nội dung này khá dài để test tính năng split. " * 50,
                "children": [
                    {
                        "level": 2,
                        "title": "Bối cảnh",
                        "content": "Nội dung về bối cảnh dự án.",
                        "children": []
                    },
                    {
                        "level": 2,
                        "title": "Mục tiêu",
                        "content": "Mục tiêu của dự án là xây dựng hệ thống tạo slide tự động.",
                        "children": []
                    }
                ]
            },
            {
                "level": 1,
                "title": "Phương pháp",
                "content": "Mô tả các phương pháp được sử dụng trong dự án.",
                "children": [
                    {
                        "level": 2,
                        "title": "Công nghệ",
                        "content": "Sử dụng Python, FastAPI, React.",
                        "children": []
                    }
                ]
            },
            {
                "level": 1,
                "title": "Kết luận",
                "content": "Tóm tắt các kết quả đạt được.",
                "children": []
            }
        ]
    }
    
    logger.info(f"✅ Created test session: {session_id}")
    
    return JSONResponse(content={
        "success": True,
        "session_id": session_id,
        "redirect_url": f"/frontend/structure-editor.html?session={session_id}"
    })