# File: backend/application/services/structure_service.py

import json
import logging
import uuid
import re
from typing import Dict, List, Any, Optional, Tuple

from backend.config import TEMP_DIR

logger = logging.getLogger(__name__)

class StructureService:
    """
    Service quản lý cấu trúc document và thuật toán sinh slide (Tree -> Linear Slides).
    """
    def __init__(self):
        # In-memory session storage
        self._sessions: Dict[str, Dict] = {}
        self.THRESHOLD_CHAR_LIMIT = 1000

    def create_session(self, filename: str, full_text: str, paragraphs: List[Dict], docx_path: str) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            'document_title': filename.replace('.docx', ''),
            'document_text': full_text,
            'paragraphs': paragraphs,
            'document_structure': [],
            'docx_file': docx_path,
            'filename': filename
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        return self._sessions.get(session_id)

    def update_session_structure(self, session_id: str, structure: List[Dict], intro_slide: Optional[Dict] = None):
        if session_id not in self._sessions:
            self._sessions[session_id] = {}
        
        self._sessions[session_id]["document_structure"] = structure
        
        document_title = "Untitled Document"
        if intro_slide:
            document_title = intro_slide.get('content') or "Untitled Document"
            self._sessions[session_id]["document_title"] = document_title

        # Merge Intro & Content
        raw_structure = []
        if intro_slide: raw_structure.append(intro_slide)
        raw_structure.extend(structure)

        # Merge logic
        merged_structure = self._merge_title_content_nodes(raw_structure)

        # Save to file
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        file_path = TEMP_DIR / f"structure_{session_id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": session_id,
                "document_title": document_title,
                "document_structure": merged_structure
            }, f, indent=2, ensure_ascii=False)

    def approve_structure(self, session_id: str) -> Dict[str, Any]:
        """Biến đổi cấu trúc cây thành danh sách slide phẳng"""
        file_path = TEMP_DIR / f"structure_{session_id}.json"
        if not file_path.exists():
            raise FileNotFoundError("Structure file not found")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        structure = data.get('document_structure', [])
        title = data.get('document_title', 'Untitled')

        # 1. Extract Special Slides
        intro_slide, thank_you_slide, filtered_structure = self._extract_special_slides(structure)
        
        # 2. Renumbering (Đánh số 1.1, 1.2...)
        renumbered_structure = self._renumber_structure(filtered_structure)
        
        # 3. Generate Slides (DFS Traversal)
        # Chúng ta dùng 1 dict 'context' để chứa kết quả thay vì biến global
        gen_context = {
            'content': [],
            'positions': [],
            'maps': [],
            'types': [],
            'full_structure': renumbered_structure # Để tạo context map
        }

        # 3a. Add Intro
        if intro_slide:
            self._add_slide(gen_context, intro_slide, ['0'], "INTRO SLIDE", 'intro')

        # 3b. Run DFS
        self._traverse_dfs(renumbered_structure, gen_context, is_root_level=True)

        # 3c. Add Thank You
        if thank_you_slide:
            self._add_slide(gen_context, thank_you_slide, ['999'], "THANK YOU SLIDE", 'thank_you')

        # 4. Sorting & Formatting
        final_result = self._sort_and_format_results(gen_context, session_id, title, renumbered_structure)
        
        # 5. Save Approved File
        approved_file = TEMP_DIR / f"approved_structure_{session_id}.json"
        with open(approved_file, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)

        return final_result

    def _add_slide(self, ctx: Dict, content: str, pos: List[str], map_content: str, slide_type: str):
        """Helper để thêm slide vào kết quả"""
        ctx['content'].append(content)
        ctx['positions'].append(pos)
        ctx['maps'].append(map_content)
        ctx['types'].append(slide_type)

    def _traverse_dfs(self, nodes: List[Dict], ctx: Dict, is_root_level: bool = False):
        """
        DFS Traversal logic - Đã chuyển từ hàm lồng ra method của class.
        """
        for node in nodes:
            try:
                # 1. TRANSITION SLIDE
                if is_root_level and node.get('is_transition') is True:
                    title = node.get('numbered_title', node.get('title', ''))
                    transition_content = f"TRANSITION SLIDE\n\n{title}"
                    pos = [f"{node.get('index', '')}.T"]
                    
                    # Create Context Map
                    context_map = self._create_context_map(ctx['full_structure'], [node.get('index', '')])
                    
                    self._add_slide(ctx, transition_content, pos, context_map, 'transition')

                # 2. CHECK CHILDREN STATUS
                has_leaves = any(not child.get("children") for child in node.get("children", []))
                has_sub_trees = any(child.get("children") for child in node.get("children", []))
                is_transition_node = node.get('is_transition') is True

                # 3. CONTENT SLIDE (For current node)
                # Chỉ tạo slide nội dung nếu node có content VÀ (không phải transition HOẶC không có lá/nhánh con)
                if node.get("content") and not is_transition_node and not has_leaves and not has_sub_trees:
                    pos = [node.get('index', '')]
                    content = self._render_slide_content("", [node])
                    context_map = self._create_context_map(ctx['full_structure'], pos)
                    
                    self._add_slide(ctx, content, pos, context_map, 'content')

                # 4. PROCESS LEAVES (Children without children)
                leaves = [child for child in node.get("children", []) if not child.get("children")]
                if leaves:
                    self._create_slides_from_leaves(node, leaves, ctx)

                # 5. PROCESS SUB-TREES (Children with children) -> Recursion
                sub_trees = [child for child in node.get("children", []) if child.get("children")]
                if sub_trees:
                    self._traverse_dfs(sub_trees, ctx, is_root_level=False)

            except Exception as e:
                logger.error(f"❌ Error in _traverse_dfs for node {node.get('title')}: {e}")
                raise

    def _create_slides_from_leaves(self, parent: Dict, leaves: List[Dict], ctx: Dict):
        """Gộp các node lá thành slide, ngắt trang nếu dài quá"""
        if not leaves: return
        
        buffer = []
        # Header bao gồm title của cha và nội dung cha (nếu có)
        header_parts = [parent.get('numbered_title', '')]
        if parent.get('content'):
            header_parts.append(parent['content'])
        header = '\n'.join(header_parts)

        for item in leaves:
            tentative_buffer = buffer + [item]
            # Check length limit
            if len(self._render_slide_content(header, tentative_buffer)) > self.THRESHOLD_CHAR_LIMIT and buffer:
                # Flush buffer
                content = self._render_slide_content(header, buffer)
                pos = [i.get('index', '') for i in buffer]
                context_map = self._create_context_map(ctx['full_structure'], pos)
                
                self._add_slide(ctx, content, pos, context_map, 'content')
                buffer = [item]
            else:
                buffer.append(item)
        
        # Flush remaining buffer
        if buffer:
            content = self._render_slide_content(header, buffer)
            pos = [i.get('index', '') for i in buffer]
            context_map = self._create_context_map(ctx['full_structure'], pos)
            self._add_slide(ctx, content, pos, context_map, 'content')

    def _create_context_map(self, outline_nodes: List[Dict], active_indices: List[str]) -> str:
        """Tạo bản đồ mục lục (Table of Contents)"""
        map_lines = []
        if not isinstance(active_indices, list): active_indices = [active_indices]

        def _generate(nodes, indent):
            for node in nodes:
                node_index = node.get("index", "")
                marker = " <--- YOU ARE HERE" if node_index in active_indices else ""
                map_lines.append(f'{"  " * indent}{node_index}. {node.get("title", "")}{marker}')
                if node.get("children"):
                    _generate(node["children"], indent + 1)
        
        _generate(outline_nodes, 0)
        return "\n".join(map_lines)

    def _render_slide_content(self, group_header: str, items: List[Dict]) -> str:
        """Format text cho slide"""
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

    def _renumber_structure(self, nodes: List[Dict], counters=None, parent_level=0) -> List[Dict]:
        """Đánh số 1, 1.1, 1.2..."""
        counters = [0] * 6 if counters is None else counters
        for node in nodes:
            is_transition = node.get('is_transition') is True
            
            # Logic tăng số
            if is_transition:
                counters[parent_level] += 1
                for i in range(parent_level + 1, len(counters)): counters[i] = 0
            else:
                counters[parent_level] += 1
                for i in range(parent_level + 1, len(counters)): counters[i] = 0

            index = ".".join(map(str, counters[:parent_level + 1]))
            node['index'] = index
            node['numbered_title'] = f"{index}. {node['title']}"
            node['level'] = parent_level + 1

            # Nếu là transition, giảm counter lại để nội dung bên trong vẫn giữ số đó
            if is_transition:
                counters[parent_level] -= 1

            if node.get('children'):
                self._renumber_structure(node['children'], list(counters), parent_level + 1)
        return nodes

    def _merge_title_content_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """Merge title node + content node thành 1"""
        merged = []
        i = 0
        while i < len(nodes):
            node = nodes[i]
            node_dict = node
            
            has_title = node_dict.get('title', '').strip() != ''
            has_no_content = not node_dict.get('content', '').strip()
            
            is_next_content = False
            if i + 1 < len(nodes):
                next_node = nodes[i+1]
                has_no_title = not next_node.get('title', '').strip()
                has_content = next_node.get('content', '').strip() != ''
                same_level = next_node.get('level') == node_dict.get('level')
                is_next_content = has_no_title and has_content and same_level

            if has_title and has_no_content and is_next_content:
                next_node = nodes[i+1]
                merged_node = {
                    'level': node_dict.get('level'),
                    'title': node_dict.get('title'),
                    'content': next_node.get('content'),
                    'children': self._merge_title_content_nodes(node_dict.get('children', [])),
                    'is_transition': node_dict.get('is_transition', False)
                }
                merged.append(merged_node)
                i += 2
            else:
                merged_node = node_dict.copy()
                merged_node['children'] = self._merge_title_content_nodes(node_dict.get('children', []))
                merged.append(merged_node)
                i += 1
        return merged

    def _extract_special_slides(self, structure: List[Dict]) -> Tuple[Optional[str], Optional[str], List[Dict]]:
        intro_node = None
        filtered = []
        for node in structure:
            if node.get('level') == 0: intro_node = node
            else: filtered.append(node)
            
        intro_slide = f"INTRO SLIDE\n\nTitle: {intro_node.get('content', '')}" if intro_node else None
        
        thank_you_slide = None
        if filtered:
            last = filtered[-1]
            keywords = ['thank', 'cảm ơn', 'cam on', 'lời cảm ơn']
            if any(k in last.get('title', '').lower() for k in keywords):
                thank_node = filtered.pop()
                thank_you_slide = f"THANK YOU SLIDE\n\n{thank_node.get('title', '')}\n\n{thank_node.get('content', '')}"
                
        return intro_slide, thank_you_slide, filtered

    def _sort_and_format_results(self, ctx: Dict, session_id: str, title: str, outline: List[Dict]) -> Dict:
        """Sắp xếp kết quả và format về dạng JSON response"""
        
        # 1. Zip data
        combined = list(zip(ctx['content'], ctx['positions'], ctx['maps'], ctx['types']))
        
        # 2. Sort Key Function
        def sort_key(item):
            pos_str = str(item[1][0]) if item[1] else '0'
            if pos_str == '0': return (0,)
            if pos_str == '999': return (999999,)
            
            is_transition = pos_str.endswith('.T')
            clean_pos = pos_str.replace('.T', '')
            parts = tuple(int(p) for p in clean_pos.split('.'))
            
            # Transition (0) đứng trước Content (1)
            return parts + (0,) if is_transition else parts + (1,)

        # 3. Sort
        sorted_combined = sorted(combined, key=sort_key)
        
        if sorted_combined:
            s_chunks, s_pos, s_maps, s_types = zip(*sorted_combined)
        else:
            s_chunks, s_pos, s_maps, s_types = [], [], [], []

        # 4. Convert to Workflow format (Chunk Dict)
        converted_chunks = []
        for i, (text, c_type, _) in enumerate(zip(s_chunks, s_types, s_pos)):
            heading = ""
            position = i
            
            lines = text.strip().split('\n')
            
            if c_type == 'intro':
                position = 0; heading = "INTRO"
            elif c_type == 'transition':
                position = -1; heading = "TRANSITION"
            elif c_type == 'thank_you':
                position = -2; heading = "THANK_YOU"
            else:
                # Content: lấy dòng đầu, bỏ số thứ tự đầu dòng
                raw_heading = lines[0] if lines else ''
                heading = re.sub(r'^\d+(\.\d+)*\.?\s*', '', raw_heading)

            converted_chunks.append({
                'position': position,
                'heading': heading,
                'text_content': text
            })

        return {
            "success": True,
            "session_id": session_id,
            "document_title": title,
            "document_outline": outline,
            "slide_chunks": converted_chunks,
            "slide_positions": list(s_pos),
            "slide_context_maps": list(s_maps),
            "slide_types": list(s_types)
        }