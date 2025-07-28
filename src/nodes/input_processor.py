import logging
import src
import tempfile
import os
from typing import Dict, Any
from src.graph_state import graph_state
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# source = "https://arxiv.org/pdf/2408.09869"  # PDF path or URL
# source = "C:\\Users\\pvmkt\\OneDrive\\Desktop\\SlideGenSourceCode\\SlideGenFunctionCalling\\Document\\test_ttcs.docx"

def input_processor(source):
    from docling.document_converter import DocumentConverter
    converter = DocumentConverter()
    result = converter.convert(source)
    # print(result.document.export_to_markdown())  # output: "### Docling Technical Report[...]"
    # print("-" * 20)


    doc = result.document

    from docling.chunking import HierarchicalChunker

    chunker = HierarchicalChunker()
    chunk_iter = chunker.chunk(dl_doc=doc)

    # for i, chunk in enumerate(chunk_iter):
    #     print(f"=== {i} ===")
    #     print(f"chunk.text:\n{f'{chunk.text[:300]}…'!r}") # noi dung goc

    #     enriched_text = chunker.contextualize(chunk=chunk)
    #     print(f"chunker.contextualize(chunk):\n{f'{enriched_text[:300]}…'!r}") # Noi dung da duoc lam giau

    #     print()

    returnArray = []
    for i, chunk in enumerate(chunk_iter):
        # print(f"=== {i} ===")
        # print(f"chunk.text:\n{f'{chunk.text[:300]}…'!r}") # noi dung goc

        enriched_text = chunker.contextualize(chunk=chunk)
        # print(f"chunker.contextualize(chunk):\n{f'{enriched_text[:300]}…'!r}") # Noi dung da duoc lam giau

        returnArray.append(enriched_text)

    return returnArray

def create_slide_list(chunks):
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





def initialize_and_prepare(state: graph_state) -> Dict[str, Any]:
    """
    Node khởi tạo: Đọc DOCX, chia chunks, và thiết lập trạng thái ban đầu.
    """
    logger.info(f"--- Node: initialize_and_prepare ---")
    docx_file = state['docx_file']
    
    # Sử dụng các hàm gốc của bạn
    chunks = input_processor(docx_file) # inputProcessor bao gồm extract_text và split_text
    slide_list = create_slide_list(chunks)
    
    logger.info(f"Đã tạo {len(slide_list)} slide chunks ban đầu.")
    
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