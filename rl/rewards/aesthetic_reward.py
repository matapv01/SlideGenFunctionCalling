import os
import sys
import json
import torch
import asyncio
from PIL import Image
from torchvision import transforms
from transformers import ViTForImageClassification

# Đảm bảo PYTHONPATH nhận diện được backend của dự án
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.workflows.slidegen_workflow.tools.tool_des import execute_tool
from backend.infrastructure.capture.playwright_provider import PlaywrightCaptureProvider

# Xác định đường dẫn tuyệt đối đến file best_model_pairwise.pt
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
reward_model_path = os.path.join(project_root, "best_model_pairwise.pt")

# Fallback tìm trong thư mục rl/model/ nếu không thấy ở root
if not os.path.exists(reward_model_path):
    reward_model_path = os.path.join(project_root, "rl", "model", "best_model_pairwise.pt")

# Khởi tạo thiết bị chạy và nạp Reward Model (ViT)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"\n[Reward Module] Loading Frozen ViT Reward Model on {device} from '{reward_model_path}'...")
vit_model = ViTForImageClassification.from_pretrained(
    'WinKawaks/vit-small-patch16-224',
    num_labels=1,
    ignore_mismatched_sizes=True
)

if os.path.exists(reward_model_path):
    vit_model.load_state_dict(torch.load(reward_model_path, map_location=device))
else:
    print(f"Warning: Checkpoint '{reward_model_path}' not found. Please train ViT first.")

vit_model.to(device)
vit_model.eval()

# Tiền xử lý ảnh
img_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Khởi tạo Capture Provider có sẵn của dự án
capture_provider = PlaywrightCaptureProvider()


def evaluate_slide_aesthetics(image_path) -> float:
    """Đưa ảnh slide qua ViT chấm điểm thẩm mỹ (0.0 đến 1.0)"""
    image = Image.open(image_path).convert("RGB")
    image_tensor = img_transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = vit_model(pixel_values=image_tensor).logits
        score = torch.sigmoid(logits).item()
    return score


def render_html_to_png(html_content, output_path):
    """Sử dụng CaptureProvider có sẵn để render HTML thành ảnh"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(capture_provider.generate_slide_from_html(html_content, output_path))


def slide_aesthetics_reward(prompts, completions, **kwargs):
    """
    Hàm tính điểm Reward thẩm mỹ cho thuật toán GRPO.
    """
    rewards = []
    temp_dir = os.path.join(project_root, "rl", "temp_rl_renders")
    os.makedirs(temp_dir, exist_ok=True)

    for idx, completion in enumerate(completions):
        temp_img_path = os.path.join(temp_dir, f"render_{idx}.png")
        try:
            # A. Parse JSON tool call từ LLM
            cleaned_text = completion.strip()
            if "```json" in cleaned_text:
                cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
            
            tool_call = json.loads(cleaned_text)
            if isinstance(tool_call, list) and len(tool_call) > 0:
                tool_call = tool_call[0]
            
            # B. Thực thi tool dựng HTML
            html_content = execute_tool(tool_call)
            if not html_content:
                rewards.append(0.0)
                continue
            
            # C. Chụp ảnh màn hình slide bằng CaptureProvider
            render_html_to_png(html_content, temp_img_path)
            
            # D. Chấm điểm qua Reward Model ViT
            score = evaluate_slide_aesthetics(temp_img_path)
            
            # Dọn dẹp ảnh tạm
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
                
            rewards.append(score)
            
        except Exception as e:
            print(f"[Reward Module] Error evaluating generation {idx}: {e}")
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
            rewards.append(0.0)
            
    return rewards
