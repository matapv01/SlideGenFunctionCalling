import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_dir = "/home/MinhPV/SlideGenFunctionCalling/rl/model"

if not os.path.exists(model_dir) or not os.listdir(model_dir):
    print(f"Error: Model directory '{model_dir}' is empty or does not exist. Please make sure the download completes first.")
    exit(1)

print(f"Loading local Qwen3 model from '{model_dir}'...")

# Determine device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_dir)

# Load model (optimized for AWQ 4-bit)
# AutoModelForCausalLM automatically detects the AWQ config and loads it using autoawq
model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    torch_dtype="auto",
    device_map="auto"
)

print("Model loaded successfully!")

# Define test prompt for SlideGen function calling
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
generated_ids = model.generate(
    **inputs,
    max_new_tokens=512,
    temperature=0.1,  # Low temperature for stable structure
    do_sample=False
)

# Strip the prompt tokens
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print("\n--- Model Response ---")
print(response)
print("----------------------")
