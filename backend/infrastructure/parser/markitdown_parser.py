# File: backend/infrastructure/parser/markitdown_parser.py

import os
from markitdown import MarkItDown
import re
from typing import Tuple, List, Dict, Any
from backend.domain.ports.parser_provider import ParserProvider

class MarkItDownParser(ParserProvider):
    def _join_content_recursively(self, node):
        node['content'] = "\n".join(node.get('content', [])).strip()
        for child in node.get('children', []):
            self._join_content_recursively(child)

    def parse_markdown_to_hierarchical_json(self, markdown_text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Chuyển đổi một chuỗi Markdown thành cấu trúc JSON phân cấp.
        Mỗi node trong cấu trúc sẽ có: level, title, content, children.
        """
        lines = markdown_text.strip().split('\n')
        root_nodes, ancestry_stack, preamble_lines = [], [], []
        first_heading_found = False

        for line in lines:
            line = line.strip()
            if not line:
                continue
            heading_match = re.match(r'^(#+)\s+(.*)', line)

            if heading_match:
                first_heading_found = True
                level = len(heading_match.group(1))
                raw_title = heading_match.group(2).strip().replace('**', '')

                # --- KEY IMPROVEMENT: Strip leading numbers like "1.", "3.1", etc. ---
                clean_title = re.sub(r'^\s*(\d+(\.\d+)*)\.?\s*', '', raw_title).strip()

                new_node = {"level": level, "title": clean_title, "content": [], "children": []}

                while ancestry_stack and ancestry_stack[-1]['level'] >= level:
                    ancestry_stack.pop()
                if not ancestry_stack:
                    root_nodes.append(new_node)
                else:
                    ancestry_stack[-1]['children'].append(new_node)
                ancestry_stack.append(new_node)
            else:
                if not first_heading_found:
                    preamble_lines.append(line.replace('**', ''))
                elif ancestry_stack:
                    ancestry_stack[-1]['content'].append(line)

        for root_node in root_nodes:
            self._join_content_recursively(root_node)

        preamble_content = "\n".join(preamble_lines).strip()
        return preamble_content, root_nodes
    
    def parse(self, file_path: str):
        """Đọc file DOCX, chuyển sang Markdown, và parse thành cấu trúc JSON phân cấp"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        converter = MarkItDown()
        markdown_text = converter.convert(file_path).text_content
        
        # Tận dụng helper cũ nhưng gói gọn trong Infra
        title, structure = self.parse_markdown_to_hierarchical_json(markdown_text)
        return title, structure