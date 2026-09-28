"""Shared GPU and LoRA settings for direct GRPO training."""

import os
import subprocess


def auto_select_gpu(preferred_gpu: str | None = None):
    gpu_override = None
    for env_name in ("TRAINING_GPU", "GPU_ID", "GPU", "PREFERRED_GPU"):
        value = os.getenv(env_name)
        if value and value.strip():
            gpu_override = value.strip()
            break

    # Training-specific GPU settings from .env should win over a stale shell export.
    if gpu_override:
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_override
        return

    if os.getenv("CUDA_VISIBLE_DEVICES", "").strip():
        return

    if gpu_override is None and preferred_gpu:
        gpu_override = preferred_gpu.strip()
    if gpu_override:
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_override
        return

    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,nounits,noheader"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2,
        )
        free_mems = [int(x) for x in res.stdout.splitlines() if x.strip().isdigit()]
        os.environ["CUDA_VISIBLE_DEVICES"] = str(free_mems.index(max(free_mems))) if free_mems else "0"
    except Exception:
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"


# LoRA configuration used by direct GRPO
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0
LORA_TARGET_MODULES = [
    "q_proj", "v_proj", "k_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj",
]
