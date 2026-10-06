#!/usr/bin/env bash
set -euo pipefail
cd /data/SlideGenFunctionCalling
export HF_HOME=/data/hf_cache PLAYWRIGHT_BROWSERS_PATH=/data/playwright RL_REWARD_RENDER_WORKERS=16 REWARD_MODEL_DEVICE=cuda EMBEDDING_DEVICE=cuda
export PYTHONPATH=/data/venvs/kernels:/data/venvs/kernels_cc:/data/venvs/kernels_tl
curl -sf -m 3 127.0.0.1:12008/health >/dev/null || { tmux new-session -d -s slidegen-renderer "./.uv/uv run --locked uvicorn backend.api.app:app --host 127.0.0.1 --port 12008"; until curl -sf -m 2 127.0.0.1:12008/health >/dev/null; do sleep 3; done; }
exec /data/venvs/qwen35/bin/python scripts/testset_generate.py score --batch-size 32
