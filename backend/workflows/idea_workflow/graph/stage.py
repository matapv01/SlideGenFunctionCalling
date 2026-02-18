# File: backend/workflows/idea_workflow/graph/stage.py

from typing import TypedDict, List, Dict, Any

class State(TypedDict):
    """
    State cho Idea Workflow.
    Chỉ tập trung vào dữ liệu văn bản và cấu trúc.
    """
    # --- INPUT ---
    title: str
    user_prompt: str
    
    # Các ràng buộc kỹ thuật (được tính toán từ main.py trước khi vào graph)
    constraints: Dict[str, Any] 
    # Ví dụ: { 'min_total': 10, 'max_total': 15, 'enable_transition_slides': True, ... }

    # --- OUTPUT ---
    slide_chunks: List[Dict[str, Any]] # Kết quả JSON cuối cùng
    agent_trace: List[Any]             # Log suy nghĩ của Agent (để debug nếu cần)
