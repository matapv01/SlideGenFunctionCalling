# File: src/nodes/document_converter.py

import os
import re
import json
from typing import Dict, Any, List, Tuple, Optional
from markitdown import MarkItDown
from src.graph.stage import State
from langchain_core.runnables import RunnableConfig
import time


def parse_markdown_to_hierarchical_json(markdown_text: str) -> Tuple[str, List[Dict[str, Any]]]:
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

    def _join_content_recursively(node):
        node['content'] = "\n".join(node.get('content', [])).strip()
        for child in node.get('children', []):
            _join_content_recursively(child)

    for root_node in root_nodes:
        _join_content_recursively(root_node)

    preamble_content = "\n".join(preamble_lines).strip()
    return preamble_content, root_nodes


def convert_document(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    Reads DOCX, converts to Markdown, parses it into a clean hierarchical
    JSON structure, and initializes the state.
    SKIP if slide_chunks already exists (from idea generation)
    """
    print("\n---------------- Executing Node: convert_document ----------------")

    # Skip if slide_chunks already provided (idea-based workflow)
    if state.get('slide_chunks'):
        print("⏭️  Skipping convert_document: slide_chunks already exists")
        return state

    start_time = time.time()
    docx_file = state['docx_file']

    # Emit streaming event
    if config:
        configurable = config.get('configurable', {})
        stream_callback = configurable.get('stream_callback')
        if stream_callback:
            stream_callback('status', {
                'step': 1,
                'title': 'Phân tích nội dung',
                'description': 'Đang đọc và chuyển đổi tài liệu...',
                'message': f'Đang xử lý file: {os.path.basename(docx_file)}'
            })

    print(f"--- Processing DOCX file: {docx_file} ---")
    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The specified DOCX file was not found: {docx_file}")

    converter = MarkItDown()
    markdown_text = converter.convert(docx_file).text_content
    print("Successfully converted DOCX to Markdown.")

    title, structure = parse_markdown_to_hierarchical_json(markdown_text)
    print(f"Parsed Markdown. Found title '{title}' and {len(structure)} root items.")

    state['document_title'] = title
    state['document_structure'] = structure
    print("Document Structure (first level):")
    print(json.dumps(structure, indent=2, ensure_ascii=False))
    end_time = time.time()
    print(f"Document conversion took {end_time - start_time:.2f} seconds.")

    return state
