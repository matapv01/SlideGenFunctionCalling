#!/usr/bin/env bash
# Test-set generation for base Qwen3.5-35B-A3B and the DAPO adapter (resumes from outputs/*.jsonl).
set -euo pipefail
cd /data/SlideGenFunctionCalling
export HF_HOME=/data/hf_cache PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONPATH=/data/venvs/kernels:/data/venvs/kernels_cc:/data/venvs/kernels_tl
exec /data/venvs/qwen35/bin/python scripts/testset_generate.py qwen \
  --adapter qwen3_5_35b_dapo_content_final_v3_20261005/checkpoint-150 --rl-samples 4 --base-samples 8 --batch-size 32
