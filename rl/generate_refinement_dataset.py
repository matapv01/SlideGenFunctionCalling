import os
import sys
import json
import random

# Đảm bảo PYTHONPATH nhận diện được backend của dự án
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT

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

def main():
    input_path = "rl/slidegen_challenge_dataset.json"
    output_path = "rl/slidegen_refinement_dataset.json"
    
    # Check both potential paths
    if not os.path.exists(input_path):
        input_path = "/home/llm/MinhPV/SlideGenFunctionCalling/rl/slidegen_challenge_dataset.json"
        output_path = "/home/llm/MinhPV/SlideGenFunctionCalling/rl/slidegen_refinement_dataset.json"
        
    if not os.path.exists(input_path):
        input_path = "slidegen_challenge_dataset.json"
        output_path = "slidegen_refinement_dataset.json"
        
    if not os.path.exists(input_path):
        print(f"[ERROR] Input challenge dataset not found at '{input_path}'. Please run generate_challenge_dataset.py first.")
        sys.exit(1)
        
    print(f"Reading challenge dataset from '{input_path}'...")
    with open(input_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
        
    refinement_samples = []
    
    system_prompt = (
        "You are a slide style generator. Based on the selected layout tool schema and user content, "
        "generate the optimal tool call using the best matching visual parameters (theme colors, contrast, "
        "background colors, paddings, and font sizes) to maximize aesthetic appeal."
    )
    
    for idx, sample in enumerate(samples):
        user_prompt = sample["user_prompt"]
        candidates = sample["tools"]
        candidate_names = [c["function"]["name"] for c in candidates]
        
        # Xác định tool duy nhất được chọn dựa vào category của candidates
        selected_tool_name = None
        
        if "generate_bar_chart_slide_2" in candidate_names:
            # Chọn loại biểu đồ tương thích
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
            # Fallback nếu không có trong flat_tools
            selected_tool_name = candidate_names[0]
            
        tool_schema = format_tool_for_qwen(flat_tools[selected_tool_name])
        
        refinement_samples.append({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "tools": [tool_schema]
        })
        
    print(f"Processed {len(refinement_samples)} samples. Saving to '{output_path}'...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(refinement_samples, f, ensure_ascii=False, indent=2)
        
    print("[SUCCESS] Refinement dataset generated successfully!")

if __name__ == "__main__":
    main()
