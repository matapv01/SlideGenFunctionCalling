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
def create_slide_list(chunks: List[str]) -> List[str]:
    """
    Tạo danh sách slide từ các chunks đã chia.
    NEW LOGIC:
    1. First, groups all chunks by their common heading.
    2. Then, for each heading group:
       - If it fits on one slide, create one slide.
       - If it's too long, split it intelligently across multiple slides.
    """
    print("Creating slide list with improved, structure-aware logic...")
    
    # 1. Group paragraphs by their heading to restore document structure
    grouped_content = OrderedDict()
    for chunk in chunks:
        # The chunk format is assumed to be "Heading\nParagraph text."
        # We split it once to separate the heading from the paragraph.
        try:
            # =================== THIS IS THE FIX ===================
            # Changed from .split('\n\n', 1) to .split('\n', 1)
            # This is more robust and handles the actual output from your chunker.
            heading, paragraph = chunk.strip().split('\n', 1)
            # =======================================================
        except ValueError:
            # If a chunk has no heading or is malformed, we skip it.
            # You could add a print here for debugging if you want:
            # print(f"Warning: Skipping malformed chunk: {chunk}")
            continue
        
        # Add the paragraph to its heading's list
        if heading not in grouped_content:
            grouped_content[heading] = []
        # The paragraph might have leading/trailing newlines from the split, so strip it.
        grouped_content[heading].append(paragraph.strip())

    # 2. Process the grouped content into final slides
    final_slides = []
    for heading, paragraphs in grouped_content.items():
        full_content_text = "\n\n".join(paragraphs)
        total_len = len(heading) + len(full_content_text) + 2

        # Case 1: The entire section fits on one slide
        if total_len <= SLIDE_CHAR_LIMIT:
            slide = f"{heading}\n\n{full_content_text}"
            final_slides.append(slide)
        # Case 2: The section is too long and must be split
        else:
            split_slides = _split_long_section_into_slides(heading, paragraphs)
            final_slides.extend(split_slides)
            
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