"""Content fingerprints for safe full-state GRPO checkpoint resumption."""
from __future__ import annotations

import hashlib
import json
from importlib.metadata import version
from pathlib import Path


def file_digest(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_value(value):
    if isinstance(value, dict):
        return {str(key): canonical_value(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted((canonical_value(item) for item in value), key=lambda item: json.dumps(item, sort_keys=True))
    if isinstance(value, (list, tuple)):
        return [canonical_value(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def contract_digest(value):
    payload = json.dumps(canonical_value(value), sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def _local_model_files(model_id):
    model_dir = Path(model_id).expanduser()
    if not model_dir.is_dir():
        return {}
    names = (
        "config.json", "generation_config.json", "tokenizer.json",
        "tokenizer_config.json", "special_tokens_map.json", "vocab.json",
        "merges.txt", "model.safetensors.index.json", "pytorch_model.bin.index.json",
    )
    files = {model_dir / name for name in names if (model_dir / name).is_file()}
    for pattern in ("model-*.safetensors", "pytorch_model-*.bin"):
        files.update(model_dir.glob(pattern))
    files.update(
        model_dir / name for name in ("model.safetensors", "pytorch_model.bin")
        if (model_dir / name).is_file()
    )
    weight_files = [path for path in files if path.suffix in {".safetensors", ".bin"}]
    if not weight_files:
        raise ValueError(f"Local model directory has no recognized weight files: {model_dir}")
    return {
        str(path.relative_to(model_dir)): file_digest(path)
        for path in sorted(files)
    }


def build_training_contract(
    train_rows, eval_rows, args, model_id, lora_config, corpus_path, model_revision=None,
):
    from backend import config
    from rl.rewards.aesthetic_reward import _model_path, reward_model_settings
    from rl.rewards.composite_reward import reward_weights
    import os

    root = Path(__file__).resolve().parents[1]
    fields = (
        "learning_rate", "per_device_train_batch_size", "per_device_eval_batch_size",
        "gradient_accumulation_steps", "generation_batch_size", "steps_per_generation",
        "max_steps", "warmup_steps", "warmup_ratio", "lr_scheduler_type",
        "lr_scheduler_kwargs", "metric_for_best_model", "greater_is_better",
        "load_best_model_at_end", "eval_seed", "optim",
        "save_strategy", "save_steps", "save_total_limit", "eval_strategy", "eval_steps", "eval_on_start",
        "logging_steps", "dataloader_drop_last",
        "weight_decay", "adam_beta1", "adam_beta2", "adam_epsilon", "max_grad_norm",
        "num_generations", "num_generations_eval", "num_iterations", "max_completion_length",
        "temperature", "top_p", "top_k", "min_p", "repetition_penalty",
        "beta", "epsilon", "epsilon_high", "loss_type", "scale_rewards",
        "router_aux_loss_coef",
        "mask_truncated_completions", "seed", "data_seed", "bf16", "fp16",
        "gradient_checkpointing", "gradient_checkpointing_kwargs", "use_vllm",
    )
    assets = {}
    for row in [*train_rows, *eval_rows]:
        for asset in row.get("approved_images") or []:
            key = asset.get("source_path") or asset.get("source_id")
            if not key or not asset.get("local_path"):
                raise ValueError("Approved corpus assets require a stable id and local file")
            if key not in assets:
                assets[key] = file_digest(asset["local_path"])
    code_paths = [
        *root.joinpath("rl").glob("*.py"),
        *root.joinpath("rl/rewards").glob("*.py"),
        *root.joinpath("backend/workflows/slidegen_workflow").rglob("*.py"),
        root / "backend/infrastructure/capture/playwright_provider.py",
        root / "backend/infrastructure/rag/gemini_provider.py",
        root / "backend/config.py",
        root / "scripts/generate_challenge_dataset.py",
        root / "frontend/src/components/XmlSlideCanvas.tsx",
        root / "frontend/src/lib/xmlSlide.ts",
        root / "frontend/package.json",
        root / "frontend/package-lock.json",
        root / "frontend/bun.lockb",
        root / "pyproject.toml",
        root / "uv.lock",
    ]
    def portable_rows(rows):
        return [{**row, "approved_images": [
            {k: v for k, v in asset.items() if k != "local_path"}
            for asset in row.get("approved_images") or []
        ]} for row in rows]
    return {
        "version": 3,
        "model_id": model_id,
        "model_revision": model_revision,
        "model_files": _local_model_files(model_id),
        "load_in_4bit": os.getenv("GRPO_LOAD_IN_4BIT", "false").lower()
        in {"1", "true", "yes", "on"},
        "corpus_sha256": file_digest(corpus_path),
        "train_sha256": contract_digest(portable_rows(train_rows)),
        "eval_sha256": contract_digest(portable_rows(eval_rows)),
        "assets": assets,
        "training": {key: getattr(args, key, None) for key in fields},
        "world_size": int(os.getenv("WORLD_SIZE", "1")),
        "lora": canonical_value(lora_config.to_dict()),
        "reward_weights": reward_weights(),
        "invalid_reward": float(os.getenv("RL_INVALID_REWARD", "-2.0")),
        "vit_sha256": file_digest(_model_path()),
        "reward_model": reward_model_settings(),
        "embedding": {
            "model": config.EMBEDDING_MODEL_NAME,
            "device": config.EMBEDDING_DEVICE,
        },
        "render": {
            "preview_url_sha256": hashlib.sha256(
                config.BROWSER_PREVIEW_URL.encode("utf-8")
            ).hexdigest(),
            "width": config.BROWSER_VIEWPORT_WIDTH,
            "height": config.BROWSER_VIEWPORT_HEIGHT,
            "scale": config.BROWSER_DEVICE_SCALE_FACTOR,
            "chromium_executable": os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE"),
            "workers": int(os.getenv("RL_REWARD_RENDER_WORKERS", "4")),
            "timeout_seconds": float(os.getenv("RL_RENDER_TIMEOUT_SECONDS", "60")),
        },
        "reward_model_device": os.getenv("REWARD_MODEL_DEVICE", "cpu"),
        "packages": {name: version(name) for name in (
            "torch", "trl", "transformers", "peft", "accelerate",
            "sentence-transformers", "datasets", "numpy", "pillow",
            "playwright", "tokenizers", "pydantic",
        )},
        "code": {str(path.relative_to(root)): file_digest(path)
                 for path in sorted(set(code_paths)) if not path.name.startswith("test_")},
    }
