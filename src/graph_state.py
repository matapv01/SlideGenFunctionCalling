from typing import List, Dict, TypedDict, Optional, Any
from src.utils.slide_context import slide_context
from src.utils.debug_info import debug_info
from src.models.llm import llm

class graph_state(TypedDict):
    """Trạng thái tổng thể của luồng công việc."""
    # Input
    docx_file: str
    output_folder: str
    max_retries: int
    
    # Hàng đợi công việc
    slide_chunks: List[str]
    
    # LLM
    llm_instance: llm

    # Trạng thái vòng lặp
    current_slide_index: int
    current_slide_text: str
    current_tool_call: Optional[Dict]
    current_html_path: Optional[str]
    current_image_path: Optional[str]
    retry_count: int
    is_redundant: bool
    
    # Context giữa các slide
    previous_slide_context: Optional[slide_context]
    
    # Thư mục tạm
    temp_dir: str
    
    # Kết quả cuối cùng
    final_slides: List[Dict]
    all_debug_info: List[debug_info]
