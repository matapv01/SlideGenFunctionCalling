from typing import List, Dict, TypedDict, Optional, Any
from src.utils.slide_context import slide_context
from src.utils.debug_info import debug_info
from src.models.llm import LLM

class State(TypedDict):
    """Trạng thái tổng thể của luồng công việc."""
    # Input
    docx_file: str
    output_folder: str
    max_retries: int
    
    
    # Hàng đợi công việc
    slide_chunks: List[str]
    
    # LLM
    llm: Optional[LLM]
    tools: List[Any]  # Danh sách các công cụ LLM
    playwright_instance: Optional[Any]  # Playwright instance nếu cần


    # Trạng thái vòng lặp
    current_slide_index: int
    length_slide_chunks: int  # Tổng số slide chunks
    current_slide_text: str
    current_tool_call: Optional[Dict]
    current_html_content: Optional[str]
    current_html_path: Optional[str]
    current_image_path: Optional[str]
    retry_count: int
    is_redundant: bool
    previous_image_path: Optional[str]  # Đường dẫn ảnh trước đó

    # Context giữa các slide
    previous_slide_context: Optional[slide_context]

    # Thông tin đánh giá
    vlm_decision: Optional[str]  # Quyết định của VLM về slide hiện tại
    vlm_feedback: Optional[str]  # Phản hồi từ VLM nếu có


    # Lịch sử tin nhắn giữa người dùng và AI
    messages: List[Dict[str, Any]]  
    
    # Thư mục tạm
    temp_dir: str
    temp_debug_dir: str
    # Kết quả cuối cùng
    final_slides: List[Dict]
    all_debug_info: List[Dict]
