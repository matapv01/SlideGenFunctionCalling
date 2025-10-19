from __future__ import annotations
import re

from base import BaseService
from typing import Tuple, Any

from markitdown import MarkItDown
from graph.shared.agent import SlidegenState
from logger import get_logger

logger = get_logger(__name__)


class ConvertDocumentService(BaseService):
    
    def process(self, input: SlidegenState) -> dict:
        logger.info('Converting docx to markdown', extra={'docx_file': input.get('docx_file')})

        markdown_text = MarkItDown().convert(input.get('docx_file')).text_content

        title, structure = self.__parse_markdown_to_hierarchical_json(markdown_text=markdown_text)

        logger.info('Parsed document', extra={'title': title, 'top_level_sections': len(structure)})

        return {'document_title': title, 'document_structure': structure}
        
    ### TODO
    def __parse_markdown_to_hierarchical_json(self, markdown_text: str) -> Tuple[str, list[dict[str, Any]]]:
        """
        Parses a Markdown string into a hierarchical JSON structure.
        **IMPROVEMENT**: This version now strips pre-existing numbering from titles.
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

        def _join_content_recursively(node):
            node['content'] = "\n".join(node.get('content', [])).strip()
            for child in node.get('children', []):
                _join_content_recursively(child)

        for root_node in root_nodes:
            _join_content_recursively(root_node)

        preamble_content = "\n".join(preamble_lines).strip()
        return preamble_content, root_nodes