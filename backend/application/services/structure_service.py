# File: backend/application/services/structure_service.py

import json
import uuid
from typing import Dict, List, Optional

from backend.config import TEMP_DIR


class StructureService:
    """
    Service quản lý session và lưu cấu trúc tài liệu thủ công.
    """

    def __init__(self):
        # In-memory session storage
        self._sessions: Dict[str, Dict] = {}

    def create_session(
        self,
        filename: str,
        full_text: str,
        paragraphs: List[Dict],
        docx_path: str,
        output_format: str = "xml",
    ) -> str:
        normalized_output_format = str(output_format or "xml").lower()
        if normalized_output_format != "xml":
            raise ValueError("This service is XML-only; output_format must be 'xml'.")

        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            'document_title': filename.replace('.docx', ''),
            'document_text': full_text,
            'paragraphs': paragraphs,
            'document_structure': [],
            'docx_file': docx_path,
            'filename': filename,
            'output_format': normalized_output_format,
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        return self._sessions.get(session_id)

    def update_session_structure(
        self,
        session_id: str,
        structure: List[Dict],
        intro_slide: Optional[Dict] = None,
        output_format: Optional[str] = None,
    ):
        if session_id not in self._sessions:
            self._sessions[session_id] = {}

        if output_format is not None:
            normalized_output_format = str(output_format or "xml").lower()
            if normalized_output_format != "xml":
                raise ValueError("This service is XML-only; output_format must be 'xml'.")
            self._sessions[session_id]["output_format"] = "xml"
        
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
                "document_structure": merged_structure,
                "output_format": self._sessions[session_id].get("output_format", "xml"),
            }, f, indent=2, ensure_ascii=False)

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
