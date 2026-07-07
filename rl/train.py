import os
import sys
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOTrainer, GRPOConfig
from datasets import Dataset

# Đảm bảo PYTHONPATH nhận diện được backend của dự án
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rl.rewards import slide_aesthetics_reward, content_preservation_reward

# ==============================================================================
# 1. KHỞI TẠO TOKENIZER & LOAD DATASET TỪ FILE JSON
# ==============================================================================
# Load trực tiếp từ Hugging Face qua Model ID (mặc định là mô hình nhỏ 1.5B/2B để test nhẹ)
model_id = os.getenv("TRAINING_MODEL_ID", "Qwen/Qwen2.5-Coder-1.5B-Instruct")

print(f"Loading tokenizer for model: '{model_id}'...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

dataset_path = "./slidegen_rl_dataset.json"

if not os.path.exists(dataset_path):
    print(f"Error: Dataset '{dataset_path}' not found. Please run 'generate_synthetic_prompts.py' first.")
    sys.exit(1)

print(f"Loading raw dataset from '{dataset_path}'...")
with open(dataset_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Format các mẫu đã capture sang Qwen Chat Template
formatted_samples = []
for sample in raw_data:
    messages = [
        {"role": "system", "content": sample["system_prompt"]},
        {"role": "user", "content": sample["user_prompt"]}
    ]
    # Nhúng danh sách schema tools động vào template của Qwen
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tools=sample["tools"],
        tokenize=False,
        add_generation_prompt=True
    )
    formatted_samples.append({
        "prompt": formatted_prompt
    })

dataset = Dataset.from_list(formatted_samples)
print(f"Dataset prepared successfully! Created {len(dataset)} training samples.")


# ==============================================================================
# 2. KHỞI TẠO MÔ HÌNH GENERATOR CHẠY TRÊN GPU
# ==============================================================================
print(f"Loading Generator LLM ({model_id}) into memory...")

# Kiểm tra GPU thích hợp để sử dụng dtype tối ưu
torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch_dtype,
    device_map="auto"
)


# ==============================================================================
# 3. CẤU HÌNH & KHỞI CHẠY GRPO TRAINER VỚI LORA & GRADIENT CHECKPOINTING
# ==============================================================================
from peft import LoraConfig

# Cấu hình LoRA (PEFT) để tiết kiệm VRAM (chỉ cập nhật ~1% trọng số)
peft_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# Tự động phát hiện kiểu độ chính xác tối ưu của GPU
use_bf16 = torch.cuda.is_bf16_supported()

training_args = GRPOConfig(
    output_dir="./qwen_slidegen_grpo",
    learning_rate=1e-6,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    num_train_epochs=3,
    save_steps=100,
    logging_steps=10,
    report_to="none",
    num_generations=4,      # G: Số mẫu sinh ra cho mỗi prompt để chấm điểm
    max_completion_length=1024,
    bf16=use_bf16,          # Sử dụng bfloat16 nếu GPU hỗ trợ
    fp16=not use_bf16,      # Sử dụng float16 làm fallback
    gradient_checkpointing=True, # Tiết kiệm VRAM cực mạnh bằng cách tính toán lại activation
)

trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=[slide_aesthetics_reward, content_preservation_reward],
    args=training_args,
    train_dataset=dataset,
    peft_config=peft_config, # Kích hoạt LoRA
)

print("Starting GRPO training loop...")
trainer.train()
