import os
import sys
import json
import torch
import asyncio
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModel

# Đảm bảo PYTHONPATH nhận diện được backend của dự án
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

from backend.workflows.slidegen_workflow.tools.tool_des import execute_tool
from backend.infrastructure.capture.playwright_provider import PlaywrightCaptureProvider
from backend.workflows.slidegen_workflow.utils.helper import sanitize_to_placeholders

capture_provider = PlaywrightCaptureProvider()
device = torch.device("cpu")

print("\n[Consistency Module] Loading Meta DINOv2 model on CPU for visual consistency checks...")
processor = AutoImageProcessor.from_pretrained('facebook/dinov2-base')
dinov2_model = AutoModel.from_pretrained('facebook/dinov2-base').to(device)
dinov2_model.eval()


def get_dinov2_embedding(image_path) -> np.ndarray:
    """Trích xuất véc-tơ đặc trưng 768 chiều từ ảnh PNG bằng DINOv2"""
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = dinov2_model(**inputs)
        # Lấy mean của last_hidden_state
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding

def render_html_to_png(html_content, output_path):
    """Render HTML sang PNG bằng Playwright"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(capture_provider.generate_slide_from_html(html_content, output_path))

def calculate_cosine_similarity(a, b) -> float:
    """Tính Cosine Similarity giữa 2 véc-tơ"""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))

def visual_consistency_reward(prompts, completions, previous_slide_embedding, **kwargs):
    """
    Hàm tính điểm nhất quán phong cách hình học & màu sắc cho GRPO.
    """
    rewards = []
    temp_dir = os.path.join(project_root, "rl", "temp_rl_renders")
    os.makedirs(temp_dir, exist_ok=True)
    
    for idx, completion in enumerate(completions):
        temp_img_path = os.path.join(temp_dir, f"consistency_render_{idx}.png")
        try:
            # A. Parse JSON tool call từ mô hình sinh
            cleaned_text = completion.strip()
            if "```json" in cleaned_text:
                cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_text:
                cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
                
            tool_call = json.loads(cleaned_text)
            if isinstance(tool_call, list) and len(tool_call) > 0:
                tool_call = tool_call[0]
                
            # B. Chuẩn hóa nội dung thành text mẫu cố định
            sanitized_tool_call = sanitize_to_placeholders(tool_call)
            
            # C. Thực thi dựng HTML & Render PNG
            html_content = execute_tool(sanitized_tool_call)
            if not html_content:
                rewards.append(0.0)
                continue
                
            render_html_to_png(html_content, temp_img_path)
            
            # D. Trích xuất đặc trưng visual và so sánh Cosine Similarity
            curr_embedding = get_dinov2_embedding(temp_img_path)
            
            # Lấy véc-tơ slide trước đã lưu sẵn trong dataset
            # Lưu ý: previous_slide_embedding được GRPOTrainer truyền vào tự động ứng với mẫu thứ idx
            prev_embedding = np.array(previous_slide_embedding[idx])
            
            sim_score = calculate_cosine_similarity(curr_embedding, prev_embedding)
            
            # Đưa điểm số về dải [0.0, 1.0]
            sim_score = max(0.0, min(1.0, sim_score))
            
            # Dọn dẹp ảnh tạm
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
                
            rewards.append(sim_score)
            
        except Exception:
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
            rewards.append(0.0)
            
    return rewards
