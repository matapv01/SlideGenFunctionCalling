import os
import sys
import json
import httpx

# Đảm bảo PYTHONPATH nhận diện được backend của dự án
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT

# Thư mục chứa vLLM endpoint
vllm_base_url = "http://localhost:8008/v1"
vllm_url = f"{vllm_base_url}/chat/completions"

# Xây dựng bảng tra cứu nhanh tên tool sang đối tượng LangChain Tool thật
flat_tools = {}
for category, tools_list in TOOLS_DICT.items():
    for tool in tools_list:
        flat_tools[tool.name] = tool

def format_tool_for_qwen(tool):
    """Chuyển đổi một LangChain tool sang định dạng JSON Schema mà Qwen3 yêu cầu"""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.args
        }
    }

def get_active_model_name():
    """Truy vấn vLLM để lấy tên mô hình đang được phục vụ thực tế"""
    try:
        response = httpx.get(f"{vllm_base_url}/models", timeout=10.0)
        response.raise_for_status()
        models_data = response.json()
        model_name = models_data["data"][0]["id"]
        print(f"Detected active served model: {model_name}")
        return model_name
    except Exception as e:
        default_model = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
        print(f"Could not fetch active model name ({e}). Falling back to default: {default_model}")
        return default_model

def generate_batch(model_name, batch_size=10, batch_idx=1):
    """Gọi local Qwen để sinh một batch prompts nhỏ kèm Few-Shot Example"""
    print(f"Generating Batch {batch_idx} ({batch_size} samples) via local LLM ({model_name})...")
    
    # Liệt kê danh sách tên các công cụ có sẵn để LLM chọn lựa
    available_tool_names = list(flat_tools.keys())
    tools_list_str = ", ".join([f"'{name}'" for name in available_tool_names])

    system_prompt = (
        "You are a dataset generator. You must output ONLY a raw JSON object containing a list under the key 'samples'. "
        "All content, text guidelines, messages, and user queries MUST be written in Vietnamese (tiếng Việt). "
        "Each item represents a slide generation request. "
        "The 'user_prompt' MUST be a request to design a specific slide, specifying slide index, layout requirement, and actual Vietnamese content (such as VinFast, FPT, or Vietnam history).\n"
        "It MUST NOT be a chatbot greeting or conversation.\n"
        f"For the 'tools' field, choose ONLY from these available tool names: [{tools_list_str}].\n\n"
        "VÍ DỤ MẪU HỢP LỆ (FEW-SHOT EXAMPLE):\n"
        "{\n"
        "  \"samples\": [\n"
        "    {\n"
        "      \"system_prompt\": \"Bạn là chuyên gia thiết kế slide chuyên nghiệp. Hãy tạo mã HTML tương ứng...\",\n"
        "      \"user_prompt\": \"Thiết kế slide 2/5 giới thiệu 'Tập đoàn FPT'. Nội dung: thành lập năm 1988, dẫn đầu lĩnh vực công nghệ thông tin và chuyển đổi số tại Việt Nam. Sử dụng layout có tiêu đề chính và các gạch đầu dòng.\",\n"
        "      \"tools\": [\"title_and_bullets_layout\", \"list_layout\"]\n"
        "    }\n"
        "  ]\n"
        "}"
    )
    
    user_query = (
        f"Hãy sinh ra một danh sách gồm đúng {batch_size} mẫu dữ liệu thiết kế slide dạng JSON bằng TIẾNG VIỆT 100% dựa theo định dạng ví dụ trên. "
        "Nội dung của 'user_prompt' phải là yêu cầu thiết kế một slide cụ thể về Việt Nam như:\n"
        "- Lịch sử Việt Nam (ví dụ: chiến thắng Điện Biên Phủ, vương triều nhà Trần, di sản cố đô Huế).\n"
        "- Doanh nghiệp & Kinh tế Việt Nam (ví dụ: hành trình VinFast toàn cầu hóa, tập đoàn FPT, Viettel, Vietcombank, thị trường chứng khoán Việt Nam, startup công nghệ).\n"
        "- Địa lý & Du lịch Việt Nam (ví dụ: Vịnh Hạ Long, du lịch Hà Nội, văn hóa ẩm thực sông nước miền Tây, Phong Nha - Kẻ Bàng).\n"
        "- Giáo dục & Xã hội Việt Nam.\n"
        "Đảm bảo định dạng đầu ra chỉ chứa danh sách tên các công cụ (tools) gợi ý ở dạng string. "
        "Chỉ trả về JSON thô, không giải thích."
    )
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.85,
        "max_tokens": 4096,
        "response_format": {"type": "json_object"} # Bắt buộc vLLM trả về JSON hợp lệ
    }
    
    response = httpx.post(vllm_url, json=payload, timeout=120.0)
    response.raise_for_status()
    result = response.json()
    raw_text = result["choices"][0]["message"]["content"].strip()
    
    # Parse JSON
    parsed_res = json.loads(raw_text)
    samples = parsed_res.get("samples", [])
    
    # Bước cực kỳ quan trọng: Điền ngược cấu trúc JSON Schema thật cho từng tool name
    enriched_samples = []
    for sample in samples:
        tool_names = sample.get("tools", [])
        real_schemas = []
        for name in tool_names:
            if name in flat_tools:
                real_schemas.append(format_tool_for_qwen(flat_tools[name]))
        
        # Tạo sample hoàn chỉnh chứa schema thật
        enriched_samples.append({
            "system_prompt": sample.get("system_prompt", ""),
            "user_prompt": sample.get("user_prompt", ""),
            "tools": real_schemas
        })
        
    return enriched_samples

def generate_prompts_via_qwen(total_samples=200, batch_size=10):
    model_name = get_active_model_name()
    all_samples = []
    num_batches = (total_samples + batch_size - 1) // batch_size
    
    print(f"Starting generation of {total_samples} samples in {num_batches} batches...")
    
    for i in range(1, num_batches + 1):
        try:
            batch_data = generate_batch(model_name=model_name, batch_size=batch_size, batch_idx=i)
            if isinstance(batch_data, list):
                all_samples.extend(batch_data)
                print(f"-> Batch {i} added {len(batch_data)} samples. Current total: {len(all_samples)}")
            else:
                print(f"Warning: Batch {i} did not return a list. Skipping.")
        except Exception as e:
            print(f"Error during Batch {i} generation: {e}")
            
    if all_samples:
        output_file = "./slidegen_rl_dataset.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_samples, f, indent=2, ensure_ascii=False)
        print(f"\n[Prompt Generator] SUCCESS! Generated {len(all_samples)} synthetic prompts and saved to {output_file}!")
    else:
        # Fallback dữ liệu nếu toàn bộ các batch lỗi
        fallback_data = [
            {
                "system_prompt": "You are a helpful assistant. You must respond ONLY with a JSON tool call.",
                "user_prompt": "Hãy thiết kế slide số 1/5 về 'Hành trình VinFast' với nội dung giới thiệu lịch sử thành lập năm 2017 và mục tiêu vươn tầm toàn cầu. Sử dụng layout có tiêu đề chính và các gạch đầu dòng.",
                "tools": [
                    format_tool_for_qwen(flat_tools["title_and_bullets_layout"])
                ]
            }
        ]
        with open("./slidegen_rl_dataset.json", "w", encoding="utf-8") as f:
            json.dump(fallback_data, f, indent=2, ensure_ascii=False)
        print("[Prompt Generator] Saved fallback sample dataset due to generation failure.")

if __name__ == "__main__":
    generate_prompts_via_qwen(total_samples=200, batch_size=10)
