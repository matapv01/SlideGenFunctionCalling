import tempfile
import os
from typing import Dict, Any
from src.stage import State
from docling.document_converter import DocumentConverter
from docling.chunking import HierarchicalChunker
import time

def input_processor(source):
    """
    Node khởi tạo: Đọc DOCX, chia chunks, và thiết lập trạng thái ban đầu.
    """
    converter = DocumentConverter()
    result = converter.convert(source)
    doc = result.document
    chunker = HierarchicalChunker()
    chunk_iter = chunker.chunk(dl_doc=doc)

    returnArray = []
    for i, chunk in enumerate(chunk_iter):
        enriched_text = chunker.contextualize(chunk=chunk)
        returnArray.append(enriched_text)

    return returnArray

def create_slide_list(chunks):
    """
    Tạo danh sách slide từ các chunks đã chia.
    Mỗi slide sẽ chứa tối đa 600 ký tự.
    """
    print("Creating slide list")
    slide_list = []
    current_slide = ""
    for section in chunks:
        section = section.strip()
        if not section:
            continue
        if not current_slide:
            current_slide = section
        else:
            if len(current_slide) + len(section) <= 600:
                current_slide += "\n" + section
            else:
                slide_list.append(current_slide)
                current_slide = section
    if current_slide:
        slide_list.append(current_slide)
    return slide_list


def initialize_and_prepare(state: State) -> Dict[str, Any]:
    """
    Node khởi tạo: Đọc DOCX, chia chunks, và thiết lập trạng thái ban đầu.
    """
    print("\n---------------- Executing Node: initialize_and_prepare ----------------")
    time.sleep(20)
    docx_file = state['docx_file']
    
    # Sử dụng các hàm gốc của bạn
    chunks = input_processor(docx_file) # inputProcessor bao gồm extract_text và split_text
    slide_list = create_slide_list(chunks)
    
    print(f"Đã tạo {len(slide_list)} slide chunks ban đầu.")
    
    temp_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp_dir, "html"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "png"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "debug"), exist_ok=True)

    return {
        "slide_chunks": slide_list,
        "current_slide_index": -1, # Bắt đầu từ -1 để router tăng lên 0
        "final_slides": [],
        "all_debug_info": [],
        "previous_slide_context": None,
        "temp_dir": temp_dir,
    }