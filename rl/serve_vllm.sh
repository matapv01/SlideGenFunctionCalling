#!/bin/bash
# File: rl/serve_vllm.sh

# Tìm đường dẫn tuyệt đối của thư mục model local
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MODEL_DIR="$SCRIPT_DIR/model"

echo "--------------------------------------------------------"
echo "Starting vLLM Server for Qwen3-30B-A3B-Instruct-2507-AWQ..."
echo "Model path: $MODEL_DIR"
echo "Port: 8000"
echo "--------------------------------------------------------"

# Khởi chạy vLLM Server phục vụ OpenAI-Compatible API
python3 -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_DIR" \
    --quantization awq \
    --port 8000 \
    --trust-remote-code \
    --max-model-len 32768
