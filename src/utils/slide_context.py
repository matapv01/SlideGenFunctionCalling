from typing import Dict, TypedDict


class slide_context(TypedDict):
    """Lưu trữ context của slide trước đó."""
    content: str
    function_call: Dict
    image_path: str
