import os
import sys

# Đảm bảo chỉ sử dụng 1 GPU để tránh lỗi DataParallel/NCCL khi huấn luyện mô hình quantized (QLoRA)
if "CUDA_VISIBLE_DEVICES" not in os.environ:
    import subprocess
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,nounits,noheader"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=2
        )
        free_mems = [int(x) for x in res.stdout.strip().split("\n") if x.strip().isdigit()]
        if free_mems:
            best_gpu = free_mems.index(max(free_mems))
            os.environ["CUDA_VISIBLE_DEVICES"] = str(best_gpu)
            print(f"[System] Automatically selected GPU {best_gpu} with the most free VRAM ({free_mems[best_gpu]} MiB).")
        else:
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    except Exception:
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import json
import torch

# Hạn chế phân mảnh bộ nhớ VRAM của PyTorch
os.environ["PYTORCH_ALLOC_CONF"] = "expandable_segments:True"
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOTrainer, GRPOConfig
from datasets import Dataset

# Đảm bảo PYTHONPATH nhận diện được backend của dự án
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rl.rewards import slide_aesthetics_reward, content_preservation_reward

# ==============================================================================
# 1. KHỞI TẠO TOKENIZER & LOAD DATASET TỪ FILE JSON
# ==============================================================================
# Load trực tiếp từ Hugging Face qua Model ID (mặc định là mô hình siêu nhỏ 0.5B để tránh OOM bộ nhớ)
model_id = os.getenv("TRAINING_MODEL_ID", "Qwen/Qwen2.5-Coder-0.5B-Instruct")

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

# Đọc cấu hình môi trường để hỗ trợ huấn luyện chất lượng cao trên H100 hoặc chạy CPU để tránh OOM
USE_CPU = os.getenv("USE_CPU", "False").lower() == "true"
USE_LORA = os.getenv("USE_LORA", "True").lower() == "true"
USE_GRAD_CHECKPOINT = os.getenv("USE_GRAD_CHECKPOINT", "True").lower() == "true"

# Kiểm tra GPU thích hợp để sử dụng dtype tối ưu
torch_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

if USE_CPU:
    print("USE_CPU is enabled! Forcing CPU execution (0 VRAM footprint)...")
    torch_dtype = torch.float32
    # Load model hoàn toàn trên CPU
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        device_map={"": "cpu"}
    )
else:
    # Xác định device_map phù hợp cho huấn luyện
    device_map = {"": torch.cuda.current_device()} if torch.cuda.is_available() else "auto"

    # Kiểm tra xem bitsandbytes có sẵn không để tự động kích hoạt QLoRA 4-bit giúp tiết kiệm tối đa VRAM
    try:
        from transformers import BitsAndBytesConfig
        from peft import prepare_model_for_kbit_training
        
        is_awq_or_gptq = "awq" in model_id.lower() or "gptq" in model_id.lower()
        if is_awq_or_gptq:
            print(f"Pre-quantized model detected ('{model_id}'). Loading directly in quantized precision...")
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map=device_map
            )
        else:
            print("bitsandbytes detected! Activating 4-bit QLoRA to minimize VRAM usage (~250MB weight footprint)...")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch_dtype
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map=device_map
            )
        model = prepare_model_for_kbit_training(model)
    except ImportError:
        print("Warning: bitsandbytes is not installed. Loading model in standard precision.")
        print("-> Tip: Install it via 'uv pip install bitsandbytes' to enable 4-bit QLoRA and save massive VRAM!")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            device_map=device_map
        )


# ==============================================================================
# 3. CẤU HÌNH & KHỞI CHẠY GRPO TRAINER VỚI LORA & GRADIENT CHECKPOINTING
# ==============================================================================
from peft import LoraConfig

print(f"Training strategy configuration:")
print(f"-> Run on CPU: {USE_CPU}")
print(f"-> Use LoRA (PEFT): {USE_LORA}")
print(f"-> Use Gradient Checkpointing: {USE_GRAD_CHECKPOINT}")

# Cấu hình LoRA (PEFT) nếu được bật
peft_config = None
if USE_LORA:
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
    num_generations=2,      # Giảm xuống 2 để tiết kiệm tối đa VRAM khi sinh mẫu
    max_completion_length=512, # Giảm xuống 512 để tránh Out of Memory VRAM trên các GPU trong khi vẫn đủ cho JSON và content
    use_cpu=USE_CPU,        # Ép chạy trên CPU nếu được cấu hình
    bf16=use_bf16 if not USE_CPU else False,
    fp16=not use_bf16 if not USE_CPU else False,
    gradient_checkpointing=USE_GRAD_CHECKPOINT if not USE_CPU else False, # Tiết kiệm VRAM nếu bật
)

trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=[slide_aesthetics_reward, content_preservation_reward],
    args=training_args,
    train_dataset=dataset,
    peft_config=peft_config, # Kích hoạt LoRA nếu peft_config không phải None
)

print("Starting GRPO training loop...")
trainer.train()
