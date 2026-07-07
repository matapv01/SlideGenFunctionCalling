#!/bin/bash
# File: rl/serve_vllm.sh

# Nhận tên mô hình từ tham số đầu tiên, mặc định là mô hình nhỏ 1.5B/2B để test nhẹ
# Mô hình sẽ được tải trực tiếp từ Hugging Face Hub và lưu vào cache của hệ thống
MODEL="${1:-Qwen/Qwen2.5-Coder-1.5B-Instruct}"

# Tự động phát hiện quantization dựa trên tên mô hình
ARGS=()
if [[ "$MODEL" == *"-AWQ"* || "$MODEL" == *"-awq"* ]]; then
    echo "-> AWQ Quantization detected in Hugging Face Repo. Enabling --quantization awq..."
    ARGS+=(--quantization awq)
fi

echo "--------------------------------------------------------"
echo "Starting vLLM Server..."
echo "Model target: $MODEL"
echo "Port: 8000"
echo "--------------------------------------------------------"

# Khởi chạy vLLM Server
python3 -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port 8000 \
    --trust-remote-code \
    "${ARGS[@]}"
