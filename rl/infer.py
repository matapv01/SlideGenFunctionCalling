import os
import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Cho phép chỉ định model ID qua biến môi trường để kiểm thử
# Mặc định sử dụng mô hình siêu nhỏ 0.5B để chạy nhẹ nhàng tránh OOM
model_id = os.getenv("TRAINING_MODEL_ID", "Qwen/Qwen2.5-Coder-0.5B-Instruct")

print(f"Loading model '{model_id}' directly from Hugging Face...")

# Xác định GPU/CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Load model (tự động phát hiện kiểu lượng tử hóa như AWQ nếu là mô hình 30B AWQ)
torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    device_map="auto"
)

print("Model loaded successfully!")

# Định nghĩa prompt test slidegen function calling
prompt = "Hãy tạo 1 slide giới thiệu về dự án SlideGen với tiêu đề 'Giới thiệu' và 3 mục tiêu chính."
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

print("Running local inference...")
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

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print("\n--- Model Response ---")
print(response)
print("----------------------")
