#!/usr/bin/env bash
# FINAL: fresh LoRA from base model with all reward/prompt/tool fixes; single reproducible contract.
set -euo pipefail
cd /data/SlideGenFunctionCalling
export HF_HOME=/data/hf_cache PLAYWRIGHT_BROWSERS_PATH=/data/playwright UV_CACHE_DIR=/data/uv_cache
command -v tmux >/dev/null || apt-get install -y -qq tmux
curl -sf -m 3 127.0.0.1:12008/health >/dev/null || {
  tmux new-session -d -s slidegen-renderer "./.uv/uv run --locked uvicorn backend.api.app:app --host 127.0.0.1 --port 12008"
  until curl -sf -m 2 127.0.0.1:12008/health >/dev/null; do sleep 3; done
}
export TRAINING_MODEL_ID=Qwen/Qwen3.5-35B-A3B
export TRAINING_MODEL_REVISION=59d61f3ce65a6d9863b86d2e96597125219dc754
export GRPO_OUTPUT_DIR=./qwen3_5_35b_dapo_content_final_v3_20261005
export GRPO_FAISS_INDEX_PATH=$GRPO_OUTPUT_DIR/tool_retriever_index
export GRPO_RESUME=${GRPO_RESUME:-false}
export GRPO_LOAD_IN_4BIT=true GRPO_LOSS_TYPE=dapo
export TOTAL_STEPS=0 GRPO_MAX_TRAIN_EPOCHS=3
export GRADIENT_ACCUMULATION_STEPS=16 NUM_GENERATIONS=4 GRPO_GENERATION_BATCH_SIZE=16 GRPO_EVAL_BATCH_SIZE=12
export MAX_COMPLETION_LENGTH=1024 LEARNING_RATE=1e-5
export GRPO_EVAL_STEPS=25 GRPO_SAVE_STEPS=25 GRPO_EVAL_ON_START=true
export GRPO_SCALE_REWARDS=batch GRPO_TEMPERATURE=1.0 GRPO_TOP_P=0.95 GRPO_TOP_K=0
# FLA + causal-conv1d kernels; tilelang makes FLA's Hopper backward correct (otherwise route FLA to no-grad only).
export PYTHONPATH=/data/venvs/kernels:/data/venvs/kernels_cc:/data/venvs/kernels_tl
export GRPO_FLA_ROLLOUT_ONLY=${GRPO_FLA_ROLLOUT_ONLY:-false}
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True RL_REWARD_RENDER_WORKERS=16
exec /data/venvs/qwen35/bin/python rl/train.py
