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

# Tự động phát hiện và sử dụng Python trong virtualenv của dự án để tránh lỗi thiếu thư viện
if [ -f "$SCRIPT_DIR/../.venv/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/../.venv/bin/python"
elif [ -f "$SCRIPT_DIR/../env/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/../env/bin/python"
elif command -v uv &> /dev/null; then
    PYTHON_BIN="uv run python3"
else
    PYTHON_BIN="python3"
fi

echo "--------------------------------------------------------"
echo "Starting vLLM Server..."
echo "Model target: $MODEL"
echo "Python binary: $PYTHON_BIN"
echo "Port: 8000"
echo "--------------------------------------------------------"

# Khởi chạy vLLM Server
$PYTHON_BIN -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port 8000 \
    --trust-remote-code \
    "${ARGS[@]}"
