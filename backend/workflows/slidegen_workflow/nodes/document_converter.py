# src/nodes/document_converter.py

import tempfile
import os
import re
import json
from typing import Dict, Any, List, Tuple, Optional
from markitdown import MarkItDown
from backend.workflows.slidegen_workflow.graph.stage import State
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
    Node 1: Reads DOCX, converts to Markdown, parses it into a clean hierarchical
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
                'title': 'Analyze Content',
                'description': 'Reading and converting document...',
                'message': f'Processing file: {os.path.basename(docx_file) if docx_file else "Unknown"}'
            })

    print(f"--- Processing DOCX file: {docx_file} ---")
    if not os.path.exists(docx_file):
        raise FileNotFoundError(f"The specified DOCX file was not found: {docx_file}")

    converter = MarkItDown()
    markdown_text = converter.convert(docx_file).text_content
    print("Successfully converted DOCX to Markdown.")
    print(f"📄 Markdown text length: {len(markdown_text)} characters")

    title, structure = parse_markdown_to_hierarchical_json(markdown_text)
    print(f"Parsed Markdown. Found title '{title}' and {len(structure)} root items.")

    # Always store plain text for potential auto-structure generation
    state['plain_text'] = markdown_text
    
    # Check if document has hierarchical structure
    has_structure = len(structure) > 0
    
    print(f"🔍 DEBUG: has_structure = {has_structure}, structure length = {len(structure)}")
    
    # Get workflow mode from state
    workflow_mode = state.get('workflow_mode', 'auto')
    print(f"🔍 DEBUG: workflow_mode = {workflow_mode}")
    
    # VALIDATION: If user chose 'auto' (Doc With Heading) but document has no structure, raise error
    if workflow_mode == 'auto' and not has_structure:
        error_msg = (
            "❌ Document không có cấu trúc heading!\n\n"
            "Bạn đã chọn chế độ 'Auto With Doc Heading' nhưng tài liệu không có tiêu đề heading (H1, H2, H3...).\n\n"
            "Vui lòng:\n"
            "1. Thêm heading vào document, hoặc\n"
            "2. Chọn chế độ 'Auto' để AI tự tạo cấu trúc"
        )
        print(f"\n{'='*60}")
        print(error_msg)
        print(f"{'='*60}\n")
        raise ValueError(error_msg)
    
    if has_structure:
        # Document has headings - use normal flow
        print(f"✅ Document has {len(structure)} sections with headings")
        state['document_title'] = title
        state['document_structure'] = structure
        print("Document Structure (first level):")
        print(json.dumps(structure, indent=2, ensure_ascii=False))
    else:
        # No structure detected - will use auto-structure generation
        print("⚠️  No hierarchical structure detected (no headings found)")
        print("📄 Will use AI to generate structure from plain text")
        
        # Use title or filename as document title
        if not title or title.strip() == '':
            title = os.path.splitext(os.path.basename(docx_file))[0]
        
        state['document_title'] = title
        state['document_structure'] = []  # Empty - will be generated by auto_structure node
        
        print(f"📊 Plain text stored: {len(markdown_text)} characters")
        print(f"📝 Document title: {title}")
    
    end_time = time.time()
    print(f"Document conversion took {end_time - start_time:.2f} seconds.")

    return state