# File: src/nodes/document_converter.py

import os
import time
import json
from typing import Optional
from markitdown import MarkItDown
from src.graph.stage import State
from langchain_core.runnables import RunnableConfig
from src.utils.helper import parse_markdown_to_hierarchical_json


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
