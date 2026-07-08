import os
import sys
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from dotenv import load_dotenv

# Đảm bảo PYTHONPATH nhận diện được backend của dự án để gọi tool render
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rl.rewards.aesthetic_reward import execute_tool, render_html_to_png

# Load các biến môi trường từ file .env
load_dotenv()

# Cho phép chỉ định model ID qua biến môi trường để kiểm thử
base_model_id = os.getenv("TRAINING_MODEL_ID", "Qwen/Qwen2.5-Coder-0.5B-Instruct")
adapter_path = os.getenv("LORA_ADAPTER_PATH", "")

# Nếu không truyền adapter qua env, tự động tìm checkpoint mới nhất dưới thư mục qwen_slidegen_grpo
if not adapter_path:
    checkpoints_dir = os.path.join(os.path.dirname(__file__), "qwen_slidegen_grpo")
    if os.path.exists(checkpoints_dir):
        checkpoints = [
            os.path.join(checkpoints_dir, d)
            for d in os.listdir(checkpoints_dir)
            if d.startswith("checkpoint-") and os.path.isdir(os.path.join(checkpoints_dir, d))
        ]
        if checkpoints:
            # Sắp xếp theo số của checkpoint để lấy checkpoint cuối cùng
            checkpoints.sort(key=lambda x: int(x.split("checkpoint-")[-1]))
            adapter_path = checkpoints[-1]

print(f"Base model ID: {base_model_id}")
if adapter_path:
    print(f"LoRA adapter detected: {adapter_path}")
else:
    print("No LoRA adapter found. Running inference with base model only.")

# Xác định GPU/CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_id)

# Load base model
torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
print(f"Loading base model into memory...")
model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    torch_dtype=torch_dtype,
    device_map="auto"
)

# Load LoRA adapter if available
if adapter_path:
    print(f"Loading LoRA weights from '{adapter_path}'...")
    model = PeftModel.from_pretrained(model, adapter_path)

print("Model loaded successfully!")

# Định nghĩa prompt test slidegen function calling
prompt = os.getenv("INFER_PROMPT", "Hãy thiết kế slide giới thiệu về tập đoàn FPT. Nội dung: thành lập năm 1988, dẫn đầu lĩnh vực công nghệ thông tin và chuyển đổi số tại Việt Nam. Sử dụng layout tiêu đề và các gạch đầu dòng.")
system_prompt = (
    "You are a helpful assistant. You must respond ONLY with a JSON tool call in this format:\n"
    "{\n"
    "  \"name\": \"title_and_bullets_layout\",\n"
    "  \"arguments\": {\n"
    "    \"title\": \"string\",\n"
    "    \"bullets\": [\"string\", \"string\", ...]\n"
    "  }\n"
    "}"
)

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": prompt}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

print("\n--- Sending Input Prompt ---")
print(prompt)
print("----------------------------")

inputs = tokenizer([text], return_tensors="pt").to(device)

print("Running model generation...")
with torch.no_grad():
    generated_ids = model.generate(
        **inputs,
        max_new_tokens=512,
        temperature=0.1,
        do_sample=False
    )

# Cắt bỏ phần prompt tokens trong đầu ra
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

print("\n--- Model Response ---")
print(response)
print("----------------------")

# Thử nghiệm thực thi và render slide sang HTML/PNG
try:
    print("\nParsing model response to render slide...")
    cleaned_text = response
    if "```json" in cleaned_text:
        cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned_text:
        cleaned_text = cleaned_text.split("```")[1].split("```")[0].strip()
        
    tool_call = json.loads(cleaned_text)
    if isinstance(tool_call, list) and len(tool_call) > 0:
        tool_call = tool_call[0]
        
    print(f"Parsed tool call: {json.dumps(tool_call, indent=2, ensure_ascii=False)}")
    
    # Thực thi tool dựng HTML
    html_content = execute_tool(tool_call)
    if html_content:
        # Lưu file HTML
        html_path = os.path.join(os.path.dirname(__file__), "infer_output.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"-> Saved HTML layout to: {html_path}")
        
        # Chụp ảnh slide PNG
        png_path = os.path.join(os.path.dirname(__file__), "infer_output.png")
        render_html_to_png(html_content, png_path)
        print(f"-> Captured slide image to: {png_path}")
        print("\nSUCCESS! You can open 'rl/infer_output.png' or 'rl/infer_output.html' to check the slide layout!")
    else:
        print("Failed to execute tool (returned empty HTML).")
except Exception as e:
    print(f"Failed to parse or render slide: {e}")
