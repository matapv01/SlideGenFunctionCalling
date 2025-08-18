import tempfile
import os
from typing import Dict, Any, List
# Assuming 'src.stage.State' is defined in your project
from src.graph.stage import State 
# The following imports are kept for compatibility with your environment
from docling.document_converter import DocumentConverter
from docling.chunking import HierarchicalChunker
from src.utils.config import SLIDE_CHAR_LIMIT
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



import re
from typing import List

NUM_PREFIX = re.compile(r'^\s*(\d+(?:\.\d+)*)\s*[\.\)]?\s*')  # "2", "2.", "2.3", "2.3." ...

def _strip_slide_prefix(line: str) -> str:
    # Bỏ tiền tố "Slide 1:" nếu có
    if ":" in line:
        left, right = line.split(":", 1)
        if left.strip().lower().startswith("slide") and left.strip()[5:].strip().isdigit():
            return right.strip()
    return line.strip()

def _level_of(line: str) -> int:
    """
    Số cấp của chỉ mục ở đầu dòng:
    - "2" -> 1
    - "2.3" -> 2
    - Không có số -> rất lớn (coi như nội dung, không phải heading số)
    """
    m = NUM_PREFIX.match(line)
    if not m:
        return 999
    return len(m.group(1).split("."))

def _parse_chunk(chunk: str):
    """
    Trả về (section_heading, headline, content)
    - section_heading: heading cấp 1 (ví dụ "2. Phương pháp được đề xuất")
    - headline: tiêu đề con sâu hơn nếu có (ví dụ "2.3. HTML Functions Library"), nếu không có thì = section_heading
    - content: phần nội dung sau headline
    """
    lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
    if not lines:
        return None

    # Bỏ "Slide N:" ở dòng đầu, nếu có
    lines[0] = _strip_slide_prefix(lines[0])

    # Thu thập các dòng “ứng viên heading” trước khi gặp dòng nội dung kiểu bullet/đoạn
    # Quy ước đơn giản: dừng lại khi gặp dòng bắt đầu bằng '-'/'•' hoặc khi đã đi quá 5 dòng đầu.
    header_candidates = []
    for i, ln in enumerate(lines[:5]):
        if ln.startswith('-') or ln.startswith('•'):
            break
        header_candidates.append(ln)

    # Nếu có >=2 ứng viên có số thứ tự, lấy:
    #   - heading cấp 1: ứng viên có level nhỏ nhất (thường là 1)
    #   - headline: ứng viên có level lớn nhất (>= heading)
    numbered = [(ln, _level_of(ln)) for ln in header_candidates]
    numbered = [(ln, lv) for ln, lv in numbered if lv != 999]

    if numbered:
        # heading cấp 1
        section_heading, section_lv = min(numbered, key=lambda x: x[1])
        # headline sâu nhất (nếu không sâu hơn thì dùng luôn heading)
        headline, head_lv = max(numbered, key=lambda x: x[1])
    else:
        # Không tìm thấy số thứ tự -> dùng 2 dòng đầu làm heading/headline dự phòng
        section_heading = header_candidates[0] if header_candidates else lines[0]
        headline = header_candidates[1] if len(header_candidates) > 1 else section_heading

    # Xác định vị trí bắt đầu content = sau lần xuất hiện cuối của headline/section_heading trong đoạn đầu
    meta_set = {section_heading, headline}
    start_idx = 0
    last_meta_idx = -1
    for i, ln in enumerate(lines[:8]):  # nhìn trong vài dòng đầu
        if ln in meta_set:
            last_meta_idx = i
    start_idx = (last_meta_idx + 1) if last_meta_idx >= 0 else 1

    content_lines = lines[start_idx:]
    # Loại bỏ những dòng lặp lại heading/headline nằm sót trong content
    content_lines = [ln for ln in content_lines if ln not in meta_set]
    content = "\n".join(content_lines).strip()

    # Nếu headline rỗng, đặt bằng section_heading
    if not headline:
        headline = section_heading

    return section_heading, headline, content

def _render_group(section_heading: str, items: List[tuple]) -> str:
    """
    items: list[(headline, content)]
    In section_heading 1 lần, sau đó liệt kê các headline + content.
    """
    parts = [section_heading, ""]
    for hl, cnt in items:
        parts.append(hl)
        parts.append("")  # dòng trống
        if cnt:
            parts.append(cnt)
            parts.append("")  # khoảng cách giữa các headline
    # Xóa dòng trống dư ở cuối
    while parts and parts[-1] == "":
        parts.pop()
    return "\n".join(parts)

def create_slide_list(chunks: List[str]) -> List[str]:
    """
    Logic:
    - Mỗi headline là 1 đơn vị (kèm metadata).
    - Gộp các headline LIỀN KỀ cùng section_heading nếu tổng chiều dài <= SLIDE_CHAR_LIMIT.
    - Khi đổi section_heading hoặc vượt giới hạn -> flush nhóm hiện tại.
    """
    print("Creating slide list with section-aware grouping...")

    parsed = []
    for ch in chunks:
        res = _parse_chunk(ch)
        if res is None:
            continue
        parsed.append(res)  # (section_heading, headline, content)

    slides = []
    cur_section = None
    buf_items: List[tuple] = []  # (headline, content)

    def flush():
        nonlocal buf_items, cur_section
        if not buf_items:
            return
        # thử gộp tất cả thành 1 slide
        combined = _render_group(cur_section, buf_items)
        if len(combined) <= SLIDE_CHAR_LIMIT:
            slides.append(combined)
        else:
            # nếu quá dài, tách ra theo từng headline, nhưng vẫn in section_heading cho từng phần
            for item in buf_items:
                single = _render_group(cur_section, [item])
                slides.append(single)
        buf_items = []

    for section_heading, headline, content in parsed:
        # đổi section -> flush
        if cur_section is None:
            cur_section = section_heading
        if section_heading != cur_section:
            flush()
            cur_section = section_heading

        # thử thêm item vào nhóm hiện tại
        tentative = _render_group(cur_section, buf_items + [(headline, content)])
        if len(tentative) <= SLIDE_CHAR_LIMIT:
            buf_items.append((headline, content))
        else:
            # flush nhóm hiện tại rồi bắt đầu nhóm mới với item này
            flush()
            buf_items.append((headline, content))

    # flush phần còn lại
    flush()

    print(f"Created {len(slides)} slides from {len(chunks)} chunks")
    return slides




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
    print(f"Slide chunks:")
    for i, slide in enumerate(slide_list):
        print(f"  Slide {i + 1}: {slide}")  

    temp_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(temp_dir, "html"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "png"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "debug"), exist_ok=True)
    
    state['length_slide_chunks'] = len(slide_list)
    state['slide_chunks'] = slide_list
    state['current_slide_index'] = -1  # Bắt đầu từ -1 để router tăng lên 0
    state['final_slides'] = []
    state['all_debug_info'] = []
    state['previous_slide_context'] = None
    state['temp_dir'] = temp_dir

    return state