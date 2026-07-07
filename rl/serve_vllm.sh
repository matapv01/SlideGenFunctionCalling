#!/bin/bash
# File: rl/serve_vllm.sh

# Đường dẫn mặc định đến mô hình local
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
DEFAULT_LOCAL_MODEL="$SCRIPT_DIR/model"

# Nhận tên mô hình từ tham số đầu tiên, mặc định là mô hình nhỏ 1.5B/2B để test nhẹ
# Bạn có thể truyền vào repo ID của Hugging Face hoặc đường dẫn thư mục local
MODEL="${1:-Qwen/Qwen2.5-Coder-1.5B-Instruct}"

# Nếu tham số truyền vào là "local", ta dùng thư mục model local (Qwen3 30B AWQ)
if [ "$MODEL" = "local" ]; then
    MODEL="$DEFAULT_LOCAL_MODEL"
fi

# Tự động phát hiện quantization dựa trên tên mô hình/đường dẫn
ARGS=()
if [[ "$MODEL" == *"-AWQ"* || "$MODEL" == *"-awq"* || "$MODEL" == *"/model"* || "$MODEL" == *"model" ]]; then
    echo "-> AWQ Quantization detected. Enabling --quantization awq..."
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
