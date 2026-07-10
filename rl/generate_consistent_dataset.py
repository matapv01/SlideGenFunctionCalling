import os
import sys
import json
import random
import asyncio
from PIL import Image
import torch
from torchvision import transforms
from transformers import AutoImageProcessor, AutoModel

# Đảm bảo PYTHONPATH nhận diện được backend của dự án
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT, execute_tool
from backend.infrastructure.capture.playwright_provider import PlaywrightCaptureProvider
from backend.workflows.slidegen_workflow.utils.helper import sanitize_to_placeholders, get_slide_style_context

# Khởi tạo Playwright Renderer để render slide tạm thời
capture_provider = PlaywrightCaptureProvider()

# Xây dựng bảng tra cứu nhanh tên tool sang đối tượng LangChain Tool thật
flat_tools = {}
for category, tools_list in TOOLS_DICT.items():
    for tool in tools_list:
        flat_tools[tool.name] = tool

def format_tool_for_qwen(tool):
    """Chuyển đổi một LangChain tool sang định dạng JSON Schema mà Qwen yêu cầu"""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.args
        }
    }


# Khởi tạo mô hình DINOv2 để trích xuất đặc trưng visual
print("[DINOv2] Loading Meta DINOv2 model locally on CPU...")
processor = AutoImageProcessor.from_pretrained('facebook/dinov2-base')
dinov2_model = AutoModel.from_pretrained('facebook/dinov2-base')
dinov2_model.eval()

def get_dinov2_embedding(image_path) -> list:
    """Trích xuất véc-tơ đặc trưng 768 chiều từ ảnh PNG bằng DINOv2"""
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = dinov2_model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    return embeddings

def render_html_to_png_sync(html_content, output_path):
    """Render HTML sang PNG đồng bộ"""
    if not html_content:
        return
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(capture_provider.generate_slide_from_html(html_content, output_path))

# Các bảng mã màu phong cách mẫu để sinh ngẫu nhiên
THEME_COLORS = ["#2563EB", "#10B981", "#EF4444", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6"]
BG_COLORS = ["#FFFFFF", "#F9FAFB", "#F3F4F6", "#1F2937", "#111827", "#0F172A"]
FONT_SIZES = [0.9, 1.0, 1.1, 1.2]
PADDINGS = ["1.0rem", "1.5rem", "2.0rem"]

def generate_dummy_args(args_schema, prev_theme_color, prev_bg_color, prev_font_size, prev_padding):
    """Tự động sinh các đối số hợp lệ (Pydantic-compliant) dựa trên schema"""
    dummy_args = {}
    for param_name, param_info in args_schema.items():
        # A. Điền các tham số phong cách (Style parameters)
        if param_name in ["theme_color", "accent_color", "highlight_color"]:
            dummy_args[param_name] = prev_theme_color
        elif param_name in ["background_color", "bg_color_left", "bg_color_right"]:
            dummy_args[param_name] = prev_bg_color
        elif param_name == "font_size_multiplier":
            dummy_args[param_name] = prev_font_size
        elif param_name in ["card_padding", "border_width"]:
            dummy_args[param_name] = prev_padding
        elif param_name in ["text_color", "title_color", "main_title_color"]:
            dummy_args[param_name] = "#555555" if prev_bg_color in ["#FFFFFF", "#F9FAFB", "#F3F4F6"] else "#CCCCCC"
            
        # B. Sinh các tham số nội dung mẫu dựa trên kiểu dữ liệu (Content parameters)
        else:
            param_type = param_info.get("type")
            if param_type == "string":
                dummy_args[param_name] = "Dummy text"
            elif param_type in ["number", "integer"]:
                dummy_args[param_name] = 1.0 if param_type == "number" else 1
            elif param_type == "boolean":
                dummy_args[param_name] = True
            elif param_type == "array":
                items_info = param_info.get("items", {})
                item_type = items_info.get("type")
                if item_type == "string":
                    dummy_args[param_name] = ["Dummy string 1", "Dummy string 2"]
                else:
                    if param_name == "points":
                        dummy_args[param_name] = [
                            {"title": "Dummy Title 1", "description": "Dummy Description 1", "icon_name": "star"},
                            {"title": "Dummy Title 2", "description": "Dummy Description 2", "icon_name": "thumbs-up"}
                        ]
                    elif param_name == "items":
                        dummy_args[param_name] = [
                            {"label": "Category A", "value": 45},
                            {"label": "Category B", "value": 55}
                        ]
                    elif param_name in ["columns", "reference_items"]:
                        dummy_args[param_name] = [
                            {"title": "Col Title 1", "description": "Column Description 1"},
                            {"title": "Col Title 2", "description": "Column Description 2"}
                        ]
                    elif param_name == "steps":
                        dummy_args[param_name] = [
                            {"step_number": "01", "title": "Step Title 1", "description": "Step Description 1"},
                            {"step_number": "02", "title": "Step Title 2", "description": "Step Description 2"}
                        ]
                    elif param_name == "data_points":
                        dummy_args[param_name] = [
                            {"label": "Jan", "value": 15},
                            {"label": "Feb", "value": 25}
                        ]
                    else:
                        dummy_args[param_name] = [{"title": "Dummy title", "description": "Dummy description"}]
            elif param_type == "object":
                dummy_args[param_name] = {}
    return dummy_args

def main():
    input_path = "rl/data/slidegen_challenge_dataset.json"
    output_path = "rl/data/slidegen_consistent_dataset.json"
    
    if not os.path.exists(input_path):
        input_path = "/home/llm/MinhPV/SlideGenFunctionCalling/rl/data/slidegen_challenge_dataset.json"
        output_path = "/home/llm/MinhPV/SlideGenFunctionCalling/rl/data/slidegen_consistent_dataset.json"
        
    if not os.path.exists(input_path):
        input_path = "data/slidegen_challenge_dataset.json"
        output_path = "data/slidegen_consistent_dataset.json"
        
    if not os.path.exists(input_path):
        print(f"[ERROR] Input challenge dataset not found at '{input_path}'.")
        sys.exit(1)
        
    print(f"Reading challenge dataset from '{input_path}'...")
    with open(input_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    consistent_samples = []
    
    # Tạo thư mục tạm để render ảnh slide trước
    temp_dir = "rl/temp_dataset_renders"
    os.makedirs(temp_dir, exist_ok=True)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=200, help="Giới hạn số mẫu sinh")
    args = parser.parse_args(args=[] if 'ipykernel' in sys.modules else None)
    
    target_samples = samples[:args.limit]
    print(f"Processing {len(target_samples)} samples for style consistency...")
    
    for idx, sample in enumerate(target_samples):
        user_prompt = sample["user_prompt"]
        candidates = sample["tools"]
        candidate_names = [c["function"]["name"] for c in candidates]
        
        # 1. Xác định selected_tool_name (Correct Tool)
        selected_tool_name = None
        if "generate_bar_chart_slide_2" in candidate_names:
            if "biểu đồ tròn" in user_prompt or "tròn" in user_prompt:
                selected_tool_name = "generate_pie_chart_slide_1"
            elif "biểu đồ đường" in user_prompt or "đường" in user_prompt:
                selected_tool_name = "generate_line_chart_slide_2"
            else:
                selected_tool_name = "generate_bar_chart_slide_2"
        elif "generate_process_steps_slide" in candidate_names:
            selected_tool_name = "generate_process_steps_slide"
        elif "generate_comparison_slide" in candidate_names:
            selected_tool_name = "generate_comparison_slide"
        elif "generate_icon_list_slide" in candidate_names:
            selected_tool_name = "generate_icon_list_slide"
        else:
            selected_tool_name = "generate_content_slide"
            
        if selected_tool_name not in flat_tools:
            selected_tool_name = candidate_names[0]
            
        # 2. Sinh ngẫu nhiên Style Context của slide trước
        prev_theme_color = random.choice(THEME_COLORS)
        prev_bg_color = random.choice(BG_COLORS)
        prev_font_size = random.choice(FONT_SIZES)
        prev_padding = random.choice(PADDINGS)
        
        # 3. Tự động tạo đối số hợp lệ cho slide trước để render
        tool_args_schema = flat_tools[selected_tool_name].args
        dummy_args = generate_dummy_args(tool_args_schema, prev_theme_color, prev_bg_color, prev_font_size, prev_padding)
        
        prev_tool_call = {
            "name": selected_tool_name,
            "arguments": dummy_args
        }
        
        # Tạo chuỗi [PREVIOUS SLIDE STYLE CONTEXT] sử dụng core BE function
        style_context_str = get_slide_style_context(prev_tool_call)
        
        # Ráp prompt mới
        full_user_prompt = (
            "You are a slide layout generator. Based on the slide content, the available layout tool schemas, "
            "and the style context of the previous slide, generate the optimal tool call in JSON format.\n"
            "Your goal is to maintain visual consistency (matching the color palette and design tone of the previous slide) "
            "while selecting the best tool layout for the new content.\n\n"
            f"{style_context_str}\n\n"
            f"[CURRENT SLIDE CONTENT]\n{user_prompt}\n\n"
            "Choose the single most appropriate tool from the available tools below, populate its arguments with the content, "
            "and align the style parameters to ensure visual consistency with the previous slide."
        )
        
        # Chuẩn hóa slide trước và render PNG tạm thời
        sanitized_prev = sanitize_to_placeholders(prev_tool_call)
        html_prev = execute_tool(sanitized_prev)
        
        temp_img_path = os.path.join(temp_dir, f"prev_slide_{idx}.png")
        render_html_to_png_sync(html_prev, temp_img_path)
        
        # Trích xuất véc-tơ DINOv2 768 chiều
        try:
            prev_embedding = get_dinov2_embedding(temp_img_path)
        except Exception as e:
            print(f"Error extracting embedding for index {idx}: {e}")
            # Fallback embedding nếu bị lỗi
            prev_embedding = [0.0] * 768
        
        # Xóa ảnh tạm
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
            
        # Format các candidate tools
        tool_schemas = [format_tool_for_qwen(flat_tools[name]) for name in candidate_names if name in flat_tools]
        
        consistent_samples.append({
            "system_prompt": "You are a helpful assistant that calls slide layout functions.",
            "user_prompt": full_user_prompt,
            "tools": tool_schemas,
            "previous_slide_embedding": prev_embedding,
            "target_style": {
                "theme_color": prev_theme_color,
                "background_color": prev_bg_color,
                "font_size_multiplier": prev_font_size,
                "card_padding": prev_padding
            }
        })
        
        if (idx + 1) % 10 == 0:
            print(f"-> Pre-embedded {idx + 1}/{len(target_samples)} slides.")
            
    # Lưu tệp dataset nhất quán trực quan
    print(f"Saving consistent training dataset to '{output_path}'...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(consistent_samples, f, ensure_ascii=False, indent=2)
        
    # Dọn dẹp thư mục tạm
    if os.path.exists(temp_dir):
        try:
            os.rmdir(temp_dir)
        except OSError:
            pass
            
    print(f"[SUCCESS] Style Consistent dataset generated successfully! Saved to '{output_path}'.")

if __name__ == "__main__":
    main()
