from typing import Dict, TypedDict, List, Optional

class debug_info(TypedDict):
    """Lưu trữ thông tin gỡ lỗi cho mỗi slide."""
    slide_index: int
    attempts: List[Dict]