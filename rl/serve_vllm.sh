#!/bin/bash
# File: rl/serve_vllm.sh

# Bắt buộc vLLM sử dụng động cơ ổn định v0 thay vì v1 thử nghiệm (tránh lỗi Engine core initialization failed)
export VLLM_USE_V1=0
# Sử dụng phương pháp 'spawn' cho multiprocessing để tránh xung đột CUDA GPU context
export VLLM_WORKER_MULTIPROC_METHOD=spawn



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

# Thiết lập cổng chạy vLLM (mặc định chuyển sang 8008 để tránh xung đột cổng 8000)
VLLM_PORT="${VLLM_PORT:-8008}"

# Khai báo mức sử dụng tối đa VRAM (mặc định là 0.3 để chạy vừa khít trong bộ nhớ còn trống khi test)
GPU_MEM_UTIL="${GPU_MEMORY_UTILIZATION:-0.3}"

echo "--------------------------------------------------------"
echo "Starting vLLM Server..."
echo "Model target: $MODEL"
echo "Python binary: $PYTHON_BIN"
echo "Port: $VLLM_PORT"
echo "GPU Memory Util: $GPU_MEM_UTIL"
echo "--------------------------------------------------------"

# Khởi chạy vLLM Server
$PYTHON_BIN -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --port "$VLLM_PORT" \
    --gpu-memory-utilization "$GPU_MEM_UTIL" \
    --trust-remote-code \
    "${ARGS[@]}"
