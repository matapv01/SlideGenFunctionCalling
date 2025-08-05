import tempfile
import os
from typing import Dict, Any, List
from collections import OrderedDict
# Assuming 'src.stage.State' is defined in your project
from src.stage import State 
# The following imports are kept for compatibility with your environment
from docling.document_converter import DocumentConverter
from docling.chunking import HierarchicalChunker
from src.utils.config import SLIDE_CHAR_LIMIT
import time

def input_processor(source):
    """
    Node khởi tạo: Đọc DOCX, chia chunks, và thiết lập trạng thái ban đầu.
    --- THIS FUNCTION IS UNCHANGED ---
    It provides the flat list of chunks that our new logic will process.
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

# --- NEW HELPER FUNCTION FOR THE IMPROVED LOGIC ---
# This function handles splitting a single large section.
def _split_long_section_into_slides(heading: str, paragraphs: List[str]) -> List[str]:
    """
    Takes a single, oversized section and splits it into multiple slides,
    each with the same heading. This is a helper for create_slide_list.
    """
    sub_slides = []
    current_slide_content = ""
    heading_len = len(heading) + 2  # Account for heading and two newlines

    for p in paragraphs:
        # If adding the next paragraph exceeds the limit, finalize the current slide
        if current_slide_content and (heading_len + len(current_slide_content) + len(p) + 2 > SLIDE_CHAR_LIMIT):
            sub_slides.append(f"{heading}\n\n{current_slide_content}")
            current_slide_content = p  # Start the new slide with the current paragraph
        else:
            # Otherwise, add the paragraph to the current slide
            if not current_slide_content:
                current_slide_content = p
            else:
                current_slide_content += f"\n\n{p}"

    # Add the last remaining slide content
    if current_slide_content:
        sub_slides.append(f"{heading}\n\n{current_slide_content}")

    return sub_slides

# --- THE LOGIC OF THIS FUNCTION IS REPLACED ---
from collections import OrderedDict
from typing import List

SLIDE_CHAR_LIMIT = 1000  # hoặc một giới hạn bạn định nghĩa

def create_slide_list(chunks: List[str]) -> List[str]:
    """
    Tạo danh sách slide từ các chunks đã chia.
    Logic:
    - Giữ nguyên chunks.
    - Gộp nhiều chunks cùng heading nếu tổng chiều dài vẫn trong SLIDE_CHAR_LIMIT.
    - Nếu quá dài, giữ nguyên từng chunk như là một slide.
    """
    print("Creating slide list with grouping-only logic (no splitting)...")

    # 1. Gom chunks theo heading
    grouped_content = OrderedDict()
    for chunk in chunks:
        try:
            heading, paragraph = chunk.strip().split('\n', 1)
        except ValueError:
            continue

        if heading not in grouped_content:
            grouped_content[heading] = []
        grouped_content[heading].append(paragraph.strip())

    # 2. Xử lý tạo slides (gộp nếu vừa, giữ nguyên nếu không)
    final_slides = []
    for heading, paragraphs in grouped_content.items():
        current_slide = ""
        current_len = 0
        buffer = []

        for para in paragraphs:
            para_text = para.strip()
            estimated_len = current_len + len(para_text) + 2  # +2 cho khoảng cách giữa các đoạn

            if estimated_len + len(heading) <= SLIDE_CHAR_LIMIT:
                buffer.append(para_text)
                current_len = estimated_len
            else:
                # Thêm slide đã tích lũy
                if buffer:
                    slide = f"{heading}\n\n" + "\n\n".join(buffer)
                    final_slides.append(slide)
                # Bắt đầu slide mới với đoạn này
                slide = f"{heading}\n\n{para_text}"
                final_slides.append(slide)
                buffer = []
                current_len = 0

        # Thêm phần còn lại trong buffer
        if buffer:
            slide = f"{heading}\n\n" + "\n\n".join(buffer)
            final_slides.append(slide)

    return final_slides



def initialize_and_provide(state: State) -> Dict[str, Any]: # Renamed back based on your error log
    """
    Node khởi tạo: Đọc DOCX, chia chunks, và thiết lập trạng thái ban đầu.
    """
    print("\n---------------- Executing Node: initialize_and_prepare ----------------")
    # time.sleep(20) # You can re-enable this if needed
    docx_file = state['docx_file']
    
    # Sử dụng các hàm gốc của bạn
    # The output of input_processor is now correctly handled by the new create_slide_list
    chunks = input_processor(docx_file)
    print(f"Đã đọc {len(chunks)} chunks từ file DOCX.")
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