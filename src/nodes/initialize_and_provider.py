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
from collections import OrderedDict
from typing import List

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
        print(f"Chunk {i + 1}: {enriched_text[:100]}...")  # Log first 100 chars of each chunk

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



def create_slide_list(chunks: List[str]) -> List[str]:
    """
    Gộp các phần có cùng subheading nếu tổng độ dài <= SLIDE_CHAR_LIMIT.
    Nếu vượt quá giới hạn, giữ nguyên từng phần.
    """
    print("Creating slide list with conditional subheading grouping...")

    heading = None
    subheading_map = OrderedDict()

    # 1. Tách thông tin từ các chunk
    for chunk in chunks:
        lines = chunk.strip().split('\n')
        if len(lines) < 3:
            continue

        # Lấy heading chung từ dòng đầu
        if heading is None:
            heading = lines[0].split(':', 1)[-1].strip()

        subheading = lines[1].strip()
        content = "\n".join(lines[2:]).strip()

        if subheading not in subheading_map:
            subheading_map[subheading] = []
        subheading_map[subheading].append(content)

    # 2. Gộp theo subheading nếu tổng chiều dài <= SLIDE_CHAR_LIMIT
    final_slides = []
    for subheading, content_list in subheading_map.items():
        # Gộp thử các đoạn nội dung
        combined_content = "\n".join(content_list)
        slide_text = f"{heading}\n\n{subheading}\n\n{combined_content}"

        if len(slide_text) <= SLIDE_CHAR_LIMIT:
            final_slides.append(slide_text)
        else:
            # Nếu quá dài, giữ nguyên từng đoạn
            for content in content_list:
                single_slide = f"{heading}\n\n{subheading}\n\n{content}"
                final_slides.append(single_slide)
    print(f"Created {len(final_slides)} slides from {len(chunks)} chunks.")
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