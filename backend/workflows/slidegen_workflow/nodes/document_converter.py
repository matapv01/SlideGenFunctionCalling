# File: backend/workflows/slidegen_workflow/nodes/document_converter.py

import os
import time
import json
from typing import Optional
from backend.workflows.slidegen_workflow.graph.stage import State
from langchain_core.runnables import RunnableConfig


def convert_document(state: State, config: Optional[RunnableConfig] = None) -> State:
    """
    Node: Document Converter
    Responsibility: Delegate the parsing of the input file to the injected ParserProvider.
    """
    print("\n---------------- Executing Node: convert_document ----------------")

    # 1. Skip logic (Giữ nguyên)
    if state.get('slide_chunks'):
        print("⏭️  Skipping convert_document: slide_chunks already exists")
        return state

    start_time = time.time()
    docx_file = state.get('docx_file')

    # 2. Get Dependencies from Config (Dependency Injection)
    if not config:
        raise ValueError("Configuration is missing.")
    
    configurable = config.get('configurable', {})
    parser_provider = configurable.get('parser_provider') # 🟢 Lấy Provider từ config
    stream_callback = configurable.get('stream_callback')

    # 3. Emit Event (UX)
    if stream_callback:
        stream_callback('status', {
            'step': 1,
            'title': 'Phân tích nội dung',
            'description': 'Đang đọc và chuyển đổi tài liệu...',
            'message': f'Đang xử lý file: {os.path.basename(docx_file) if docx_file else "Unknown"}'
        })

    # 4. Validation
    if not docx_file or not os.path.exists(docx_file):
        raise FileNotFoundError(f"The specified DOCX file was not found: {docx_file}")

    if not parser_provider:
        raise ValueError("Parser Provider is not initialized in the workflow config.")

    print(f"--- Processing DOCX file: {docx_file} ---")

    # 5. 🟢 DELEGATE TO INFRASTRUCTURE
    # Node không cần biết bên dưới dùng MarkItDown, PyPDF2 hay gì cả.
    # Nó chỉ cần biết: đưa file path -> nhận về title và structure.
    try:
        title, structure = parser_provider.parse(docx_file)
        print("Successfully parsed document via Infrastructure Provider.")
    except Exception as e:
        print(f"❌ Error during document parsing: {e}")
        raise e

    print(f"Parsed Document. Found title '{title}' and {len(structure)} root items.")

    # 6. Update State
    state['document_title'] = title
    state['document_structure'] = structure
    
    # Debug print
    # print("Document Structure (first level):")
    # print(json.dumps(structure, indent=2, ensure_ascii=False))

    end_time = time.time()
    print(f"Document conversion took {end_time - start_time:.2f} seconds.")

    return state
