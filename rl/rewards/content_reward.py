import json
import re
from typing import List

def extract_text_from_json(json_str: str) -> str:
    """Trích xuất tất cả các giá trị text từ chuỗi JSON của tool call để kiểm tra nội dung"""
    try:
        # Làm sạch markdown blocks nếu có
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        data = json.loads(json_str)
        text_parts = []
        
        # Hàm đệ quy duyệt qua các trường để lấy text
        def recurse(node):
            if isinstance(node, str):
                text_parts.append(node)
            elif isinstance(node, list):
                for item in node:
                    recurse(item)
            elif isinstance(node, dict):
                for val in node.values():
                    recurse(val)
                    
        recurse(data)
        return " ".join(text_parts)
    except Exception:
        return ""

def clean_words(text: str) -> List[str]:
    """Làm sạch văn bản và tách thành tập hợp các từ khóa (loại bỏ từ nối ngắn)"""
    text = text.lower()
    # Chỉ giữ lại chữ và số
    words = re.findall(r'\b\w{2,}\b', text)
    # Loại bỏ các từ nối quá phổ biến trong tiếng Việt (stopwords cơ bản)
    stopwords = {"và", "của", "các", "cho", "trong", "để", "này", "được", "với", "như", "một", "những"}
    return [w for w in words if w not in stopwords]

def content_preservation_reward(prompts: List[str], completions: List[str], **kwargs) -> List[float]:
    """
    Hàm thưởng bảo toàn nội dung.
    Điểm số dao động từ 0.0 đến 1.0:
    - Trả về 0.0 nếu completion không phải JSON hợp lệ hoặc rỗng.
    - Điểm cộng dựa trên tỷ lệ bảo toàn từ khóa chính (Keyword Overlap).
    - Phạt nếu độ dài bị co ngắn quá mức (Length Penalty).
    """
    rewards = []
    
    for prompt, completion in zip(prompts, completions):
        # 1. Parse thử JSON
        generated_text = extract_text_from_json(completion)
        if not generated_text:
            rewards.append(0.0) # Phạt nặng nếu JSON lỗi hoặc không gọi tool
            continue
            
        # 2. Tách từ khóa từ prompt thô (Chỉ lấy phần slide_content ở cuối prompt)
        # Tìm phần nội dung slide gốc trong prompt
        prompt_content = prompt
        if "CONTENT:" in prompt:
            prompt_content = prompt.split("CONTENT:")[-1]
            
        original_words = clean_words(prompt_content)
        generated_words = clean_words(generated_text)
        
        if not original_words:
            rewards.append(1.0) # Fallback nếu prompt không có chữ
            continue
            
        # 3. Tính tỷ lệ từ khóa gốc xuất hiện trong slide được tạo
        original_set = set(original_words)
        generated_set = set(generated_words)
        
        preserved_keywords = original_set.intersection(generated_set)
        overlap_ratio = len(preserved_keywords) / len(original_set)
        
        # 4. Tính điểm phạt độ dài (Length Penalty)
        # Nếu slide quá ngắn so với văn bản gốc (ví dụ Qwen xóa hết chữ để slide trông 'đẹp')
        ratio_len = len(generated_words) / len(original_words)
        length_penalty = 1.0
        if ratio_len < 0.3: # Slide ít hơn 30% số từ của văn bản gốc
            length_penalty = ratio_len / 0.3 # Giảm điểm tuyến tính về 0
            
        # Điểm cuối cùng = tỷ lệ bảo toàn từ khóa * điểm phạt độ dài
        final_score = overlap_ratio * length_penalty
        
        # Chuẩn hóa về khoảng [0.0, 1.0]
        final_score = max(0.0, min(1.0, final_score))
        rewards.append(final_score)
        
    return rewards
