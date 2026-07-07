import os
import sys
import json
import httpx

# Thư mục chứa vLLM endpoint
vllm_base_url = "http://localhost:8000/v1"
vllm_url = f"{vllm_base_url}/chat/completions"

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
        # Fallback về tên mặc định nếu không lấy được
        default_model = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
        print(f"Could not fetch active model name ({e}). Falling back to default payload model name: {default_model}")
        return default_model

def generate_batch(model_name, batch_size=40, batch_idx=1):
    """Gọi local Qwen để sinh một batch prompts nhỏ"""
    print(f"Generating Batch {batch_idx} ({batch_size} samples) via local LLM ({model_name})...")
    
    # Prompt hướng dẫn sinh bằng tiếng Việt
    system_prompt = (
        "You are a dataset generator. You must output ONLY a raw JSON list containing synthetic "
        "slide generation requests. All content, text guidelines, messages, and user queries MUST be written in Vietnamese (tiếng Việt). "
        "Each item in the list MUST have this exact format:\n"
        "{\n"
        "  \"system_prompt\": \"Specific layout guidelines in Vietnamese based on the slide type (e.g. intro, content, transition). Include typography and mathematical equation rules in Vietnamese.\",\n"
        "  \"user_prompt\": \"Detailed human prompt in Vietnamese specifying the context, slide index, and content.\",\n"
        "  \"tools\": [List of tool schemas representing visual templates recommended by FAISS (e.g. title_and_bullets_layout)]\n"
        "}"
    )
    
    user_query = (
        f"Hãy sinh ra một danh sách gồm đúng {batch_size} mẫu dữ liệu thiết kế slide dạng JSON bằng TIẾNG VIỆT 100%. "
        "Nội dung các slide phải tập trung hoàn toàn vào dữ liệu, chủ đề của Việt Nam như:\n"
        "- Lịch sử Việt Nam (ví dụ: chiến thắng Điện Biên Phủ, vương triều nhà Trần, di sản cố đô Huế).\n"
        "- Doanh nghiệp & Kinh tế Việt Nam (ví dụ: hành trình VinFast toàn cầu hóa, tập đoàn FPT, Viettel, Vietcombank, thị trường chứng khoán Việt Nam, startup công nghệ).\n"
        "- Địa lý & Du lịch Việt Nam (ví dụ: Vịnh Hạ Long, du lịch Hà Nội, văn hóa ẩm thực sông nước miền Tây, Phong Nha - Kẻ Bàng).\n"
        "- Giáo dục & Xã hội Việt Nam.\n"
        "Mỗi mẫu phải bao gồm đầy đủ system_prompt thiết kế bằng tiếng Việt, user_prompt yêu cầu cụ thể bằng tiếng Việt, "
        "và danh sách tools gợi ý tương ứng (chứa JSON schema của các layout như title_and_bullets_layout, list_layout, intro_layout, v.v.). "
        "Chỉ trả về JSON list thô, không viết thêm bất kỳ chữ giải thích nào."
    )
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.85, # Tăng nhẹ sáng tạo giữa các batch để đa dạng
        "max_tokens": 4096   # Phù hợp với 1 batch 40 mẫu
    }
    
    response = httpx.post(vllm_url, json=payload, timeout=120.0)
    response.raise_for_status()
    result = response.json()
    raw_text = result["choices"][0]["message"]["content"].strip()
    
    # Làm sạch markdown codeblock
    if "```json" in raw_text:
        raw_text = raw_text.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_text:
        raw_text = raw_text.split("```")[1].split("```")[0].strip()
        
    return json.loads(raw_text)

def generate_prompts_via_qwen(total_samples=200, batch_size=40):
    """
    Hàm lặp chạy nhiều batch để gom đủ dữ liệu huấn luyện mà không bị tràn max_tokens.
    """
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
                "user_prompt": "Hãy tạo 1 slide giới thiệu về dự án SlideGen với tiêu đề 'Giới thiệu' và 3 mục tiêu chính.",
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "title_and_bullets_layout",
                            "description": "Intro slide layout with title and bullet points.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "bullets": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["title", "bullets"]
                            }
                        }
                    }
                ]
            }
        ]
        with open("./slidegen_rl_dataset.json", "w", encoding="utf-8") as f:
            json.dump(fallback_data, f, indent=2, ensure_ascii=False)
        print("[Prompt Generator] Saved fallback sample dataset due to generation failure.")

if __name__ == "__main__":
    generate_prompts_via_qwen(total_samples=200, batch_size=40)
