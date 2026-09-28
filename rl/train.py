"""Direct GRPO training for the production XML SlideGen pipeline."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

from rl.common import (
    LORA_ALPHA,
    LORA_DROPOUT,
    LORA_R,
    LORA_TARGET_MODULES,
    auto_select_gpu,
)

# Environment loading and device selection belong to the CLI, not module import.
if __name__ == "__main__":
    load_dotenv()
    os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "300")
    os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "300")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
    os.environ.setdefault("PYTORCH_ALLOC_CONF", "expandable_segments:True")
    auto_select_gpu()

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig

from backend.infrastructure.rag.gemini_provider import (
    LocalEmbeddingToolRetrieveProvider,
)
from rl.grpo_trainer import (
    DapoAccumulationGRPOTrainer,
)
from rl.image_assets import image_cache_dir
from rl.rewards.composite_reward import (
    preflight_reward_runtime,
    slidegen_composite_reward,
)
from rl.rewards.content_reward import set_text_embedder
from rl.run_artifacts import (
    get_runtime_metadata,
    save_metric_trend_image,
    save_text_summary_image,
    start_run_logging,
    write_json,
)
from scripts.generate_challenge_dataset import load_offline_documents
from rl.training_contract import build_training_contract, contract_digest
from rl.render_runtime import close_render_runtime
from rl.slidegen_adapter import TOOLS_DICT
from rl.train_data import prepare_document, split_documents


MODEL_ID = os.getenv("TRAINING_MODEL_ID", "Qwen/Qwen3-8B")
MODEL_REVISION = os.getenv("TRAINING_MODEL_REVISION") or None
OUTPUT_DIR = Path(os.getenv("GRPO_OUTPUT_DIR", "./qwen3_8b_slidegen_grpo"))
RETRIEVER_INDEX_DIR = Path(
    os.getenv("GRPO_FAISS_INDEX_PATH", str(OUTPUT_DIR / "tool_retriever_index"))
)
TOTAL_STEPS = int(os.getenv("TOTAL_STEPS", "500"))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "1e-6"))
TRAIN_BATCH_SIZE = int(os.getenv("PER_DEVICE_TRAIN_BATCH_SIZE", "1"))
GRAD_ACCUMULATION = int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "16"))
NUM_GENERATIONS = int(os.getenv("NUM_GENERATIONS", "4"))
GENERATION_BATCH_SIZE = int(os.getenv("GRPO_GENERATION_BATCH_SIZE", "4"))
MAX_COMPLETION_LENGTH = int(os.getenv("MAX_COMPLETION_LENGTH", "3072"))
LOSS_TYPE = os.getenv("GRPO_LOSS_TYPE", "dapo")
SAVE_STEPS = int(os.getenv("GRPO_SAVE_STEPS", "25"))
EVAL_STEPS = int(os.getenv("GRPO_EVAL_STEPS", "50"))
EVAL_DOCS = int(os.getenv("GRPO_EVAL_DOCS", "5"))
DATA_SEED = int(os.getenv("GRPO_DATA_SEED", "42"))
USE_CPU = os.getenv("USE_CPU", "false").lower() in {"1", "true", "yes", "on"}
USE_LORA = os.getenv("USE_LORA", "true").lower() in {"1", "true", "yes", "on"}
USE_GRAD_CHECKPOINT = os.getenv("USE_GRAD_CHECKPOINT", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
RESUME = os.getenv("GRPO_RESUME", "true").lower() in {"1", "true", "yes", "on"}
RUN_PREFLIGHT = os.getenv("GRPO_PREFLIGHT", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
REQUIRE_IMAGE_ASSETS = os.getenv("GRPO_REQUIRE_IMAGE_ASSETS", "true").lower() in {
    "1", "true", "yes", "on",
}


def _validate_config() -> None:
    if TOTAL_STEPS < 1:
        raise ValueError("TOTAL_STEPS must be positive")
    if min(TRAIN_BATCH_SIZE, GRAD_ACCUMULATION, GENERATION_BATCH_SIZE, SAVE_STEPS) < 1:
        raise ValueError("Batch sizes, accumulation and save steps must be positive")
    if NUM_GENERATIONS < 2:
        raise ValueError("NUM_GENERATIONS must be >= 2 for GRPO")
    if GENERATION_BATCH_SIZE % NUM_GENERATIONS:
        raise ValueError(
            "GRPO_GENERATION_BATCH_SIZE must be divisible by NUM_GENERATIONS"
        )
    if GENERATION_BATCH_SIZE % TRAIN_BATCH_SIZE:
        raise ValueError(
            "GRPO_GENERATION_BATCH_SIZE must be divisible by "
            "PER_DEVICE_TRAIN_BATCH_SIZE"
        )
    if MAX_COMPLETION_LENGTH < 64:
        raise ValueError("MAX_COMPLETION_LENGTH is too small for XML tool calls")
    if EVAL_DOCS < 1:
        raise ValueError("GRPO_EVAL_DOCS must be >= 1")
    if not USE_LORA:
        raise ValueError(
            "This training entrypoint intentionally requires LoRA so checkpoints "
            "remain small and safely resumable."
        )


def _lora_config() -> LoraConfig:
    return LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        bias="none",
    )


def _checkpoint_complete(
    path: Path,
    model_id: str,
    loss_type: str,
    dapo_accumulation_factor: int,
    training_contract: str | None = None,
) -> bool:
    metadata_path = path / "rl_checkpoint_metadata.json"
    if not metadata_path.is_file():
        return False
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(metadata, dict):
        return False
    if metadata.get("model_id") != model_id:
        return False
    if metadata.get("loss_type") != loss_type:
        return False
    if metadata.get("dapo_accumulation_factor") != dapo_accumulation_factor:
        return False
    if training_contract is not None and metadata.get("training_contract") != training_contract:
        return False
    return _checkpoint_files_present(path)


def _checkpoint_files_present(path: Path) -> bool:
    model_exists = any(
        (path / filename).is_file()
        for filename in (
            "adapter_model.safetensors",
            "adapter_model.bin",
            "model.safetensors",
            "pytorch_model.bin",
        )
    )
    state_exists = all(
        (path / filename).is_file()
        for filename in ("optimizer.pt", "scheduler.pt", "trainer_state.json")
    )
    return model_exists and state_exists


def _latest_checkpoint(
    model_id: str,
    loss_type: str,
    dapo_accumulation_factor: int,
    training_contract: str | None = None,
) -> Path | None:
    if not RESUME or not OUTPUT_DIR.is_dir():
        return None
    paths = list(OUTPUT_DIR.glob("checkpoint-*"))
    candidates = []
    for path in paths:
        try:
            step = int(path.name.rsplit("-", 1)[1])
        except (IndexError, ValueError):
            continue
        if _checkpoint_files_present(path):
            candidates.append((step, path))
    if not candidates:
        if paths or (OUTPUT_DIR / "final_adapter").exists():
            raise ValueError("No complete resumable checkpoint in output directory; use a new directory")
        return None
    checkpoint = max(candidates)[1]
    if not _checkpoint_complete(checkpoint, model_id, loss_type, dapo_accumulation_factor, training_contract):
        raise ValueError(
            f"Latest complete checkpoint {checkpoint} is incompatible with the current "
            "data, reward, code, or training configuration. Use a new output directory."
        )
    return checkpoint


def _model_runtime():
    if USE_CPU:
        return "cpu", torch.float32
    if not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA is unavailable. GRPO is configured for GPU training; "
            "set USE_CPU=true only for small diagnostic runs."
        )
    device = "cuda"
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    return device, dtype


def _load_model(tokenizer=None, revision=None):
    device, dtype = _model_runtime()
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        revision=revision,
    )
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID, trust_remote_code=True, revision=revision
        )
    model = get_peft_model(model, _lora_config())
    if USE_GRAD_CHECKPOINT and device == "cuda":
        model.gradient_checkpointing_enable()
    model.config.use_cache = False
    if device == "cuda":
        model = model.to(device)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    return model, tokenizer, device, dtype


def _train_main(*, preflight_only: bool = False) -> None:
    _validate_config()
    device, dtype = _model_runtime()
    print(f"Training device: {device} ({dtype})")
    if not RESUME and OUTPUT_DIR.exists() and (
        any(OUTPUT_DIR.glob("checkpoint-*")) or (OUTPUT_DIR / "final_adapter").exists()
    ):
        raise FileExistsError("Fresh training requires an unused checkpoint output directory")
    default_grpo_corpus = PROJECT_ROOT / "rl" / "data" / "grpo_replanned_dataset.json"
    corpus_path = os.getenv("GRPO_OFFLINE_DATASET") or str(default_grpo_corpus)
    documents = load_offline_documents(corpus_path)
    image_prompts = sum(
        bool(slide.get("approved_images"))
        for document in documents
        for slide in document
    )
    if REQUIRE_IMAGE_ASSETS and image_prompts == 0:
        raise RuntimeError(
            f"No VLM-approved image prompts were found in {corpus_path}. "
            "Run scripts/rebuild_grpo_corpus.py, point GRPO_OFFLINE_DATASET at "
            "the rebuilt corpus, or set GRPO_REQUIRE_IMAGE_ASSETS=false for "
            "a deliberate no-image run."
        )
    print(
        f"GRPO corpus: {image_prompts} image-backed slides; cache={image_cache_dir()}"
    )
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log_dir = PROJECT_ROOT / "rl" / "log" / "grpo" / f"run_{run_id}"
    run_log_dir.mkdir(parents=True, exist_ok=True)
    run_log_path = start_run_logging(run_log_dir)
    model_config = AutoConfig.from_pretrained(
        MODEL_ID, trust_remote_code=True, revision=MODEL_REVISION
    )
    model_revision = getattr(model_config, "_commit_hash", None) or MODEL_REVISION
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, trust_remote_code=True, revision=model_revision
    )
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token

    print(f"Initializing local XML tool retriever at {RETRIEVER_INDEX_DIR}")
    try:
        tool_retriever = LocalEmbeddingToolRetrieveProvider(
            TOOLS_DICT, str(RETRIEVER_INDEX_DIR)
        )
    except Exception:
        if os.getenv("GRPO_ALLOW_RETRIEVER_FALLBACK", "false").lower() not in {
            "1",
            "true",
            "yes",
            "on",
        }:
            raise
        tool_retriever = None
        print("WARNING: retriever unavailable; layout assignment uses category order")
    if tool_retriever is not None:
        set_text_embedder(tool_retriever.embeddings.model)

    train_documents, eval_documents = split_documents(documents, EVAL_DOCS, DATA_SEED)
    print(
        f"Preparing {len(train_documents)} train docs and "
        f"{len(eval_documents)} held-out eval docs..."
    )
    train_rows = [
        sample
        for document in train_documents
        for sample in prepare_document(
            document,
            tokenizer,
            tool_retriever,
            strict_tool_retrieval=tool_retriever is not None,
        )
    ]
    eval_rows = [
        sample
        for document in eval_documents
        for sample in prepare_document(
            document,
            tokenizer,
            tool_retriever,
            strict_tool_retrieval=tool_retriever is not None,
        )
    ]
    if not train_rows or not eval_rows:
        raise RuntimeError("Prepared GRPO train/eval data is empty")
    train_image_prompts = sum(
        row["image_mode"] == "semantic" for row in train_rows
    )
    eval_image_prompts = sum(
        row["image_mode"] == "semantic" for row in eval_rows
    )
    if REQUIRE_IMAGE_ASSETS and (
        not train_image_prompts or not eval_image_prompts
    ):
        raise RuntimeError(
            "Image assets were found in the corpus, but image-compatible layouts "
            "were not assigned to both train and eval splits. Inspect image-cache "
            "coverage and category/layout compatibility before training."
        )

    context_limit = getattr(model_config, "max_position_embeddings", None)
    prompt_lengths = [len(tokenizer.encode(row["prompt"], add_special_tokens=False))
                      for row in [*train_rows, *eval_rows]]
    if context_limit and max(prompt_lengths) + MAX_COMPLETION_LENGTH > context_limit:
        raise ValueError(
            f"Longest prompt ({max(prompt_lengths)}) plus completion budget "
            f"({MAX_COMPLETION_LENGTH}) exceeds model context ({context_limit})"
        )
    print(f"Prompt token lengths: min={min(prompt_lengths)}, max={max(prompt_lengths)}")

    eval_enabled = EVAL_STEPS > 0
    training_args = GRPOConfig(
        output_dir=str(OUTPUT_DIR),
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=NUM_GENERATIONS,
        gradient_accumulation_steps=GRAD_ACCUMULATION,
        generation_batch_size=GENERATION_BATCH_SIZE,
        max_steps=TOTAL_STEPS,
        warmup_steps=int(os.getenv("WARMUP_STEPS", "0")),
        logging_steps=1,
        logging_first_step=True,
        save_strategy="steps",
        save_steps=SAVE_STEPS,
        save_total_limit=int(os.getenv("GRPO_SAVE_TOTAL_LIMIT", "3")),
        eval_strategy="steps" if eval_enabled else "no",
        eval_steps=EVAL_STEPS if eval_enabled else None,
        report_to="none",
        num_generations=NUM_GENERATIONS,
        num_generations_eval=NUM_GENERATIONS,
        max_completion_length=MAX_COMPLETION_LENGTH,
        temperature=float(os.getenv("GRPO_TEMPERATURE", "0.7")),
        top_p=float(os.getenv("GRPO_TOP_P", "0.8")),
        top_k=int(os.getenv("GRPO_TOP_K", "20")),
        beta=float(os.getenv("GRPO_BETA", "0.0")),
        epsilon=float(os.getenv("GRPO_EPSILON", "0.2")),
        epsilon_high=float(os.getenv("GRPO_EPSILON_HIGH", "0.28")),
        mask_truncated_completions=True,
        loss_type=LOSS_TYPE,
        scale_rewards="group",
        use_cpu=device == "cpu",
        bf16=dtype == torch.bfloat16,
        fp16=dtype == torch.float16,
        tf32=True if device == "cuda" else None,
        gradient_checkpointing=USE_GRAD_CHECKPOINT and device == "cuda",
        seed=DATA_SEED,
        data_seed=DATA_SEED,
        remove_unused_columns=False,
    )

    if training_args.loss_type in {"dapo", "cispo", "vespo"}:
        if training_args.gradient_accumulation_steps % training_args.steps_per_generation:
            raise ValueError(
                "For token-normalized losses, gradient_accumulation_steps must be "
                "divisible by steps_per_generation"
            )
        dapo_accumulation_factor = (
            training_args.gradient_accumulation_steps // training_args.steps_per_generation
        )
    else:
        dapo_accumulation_factor = 1

    contract = build_training_contract(
        train_rows, eval_rows, training_args, MODEL_ID, _lora_config(), corpus_path,
        model_revision=model_revision,
    )
    fingerprint = contract_digest(contract)
    checkpoint = _latest_checkpoint(
        MODEL_ID, training_args.loss_type, dapo_accumulation_factor, fingerprint,
    )
    if RUN_PREFLIGHT or preflight_only:
        print("Running frontend/ViT preflight and checking corpus image URLs...")
        preflight_reward_runtime([
            asset for row in [*train_rows, *eval_rows]
            for asset in row.get("approved_images") or []
        ])
    write_json(run_log_dir / "training_contract.json", contract)
    if preflight_only:
        report = {
            "mode": "preflight_only",
            "status": "passed",
            "device": device,
            "model_id": MODEL_ID,
            "training_contract": fingerprint,
            "train_prompts": len(train_rows),
            "eval_prompts": len(eval_rows),
            "train_image_prompts": train_image_prompts,
            "eval_image_prompts": eval_image_prompts,
            "min_prompt_tokens": min(prompt_lengths),
            "max_prompt_tokens": max(prompt_lengths),
            "max_completion_length": MAX_COMPLETION_LENGTH,
            "model_context_limit": context_limit,
            "max_prompt_plus_completion_tokens": max(prompt_lengths) + MAX_COMPLETION_LENGTH,
            "resume_checkpoint": str(checkpoint) if checkpoint else None,
            "policy_loaded": False,
            "optimizer_step_tested": False,
        }
        write_json(run_log_dir / "preflight.json", report)
        print(f"Preflight passed; policy was not loaded. Report: {run_log_dir / 'preflight.json'}")
        print("This does not verify GPU memory, generation or an optimizer step.")
        return
    snapshots = OUTPUT_DIR / "dataset_snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    write_json(snapshots / "train.json", train_rows)
    write_json(snapshots / "eval.json", eval_rows)
    train_dataset = Dataset.from_list(train_rows)
    eval_dataset = Dataset.from_list(eval_rows)

    print(f"Loading base model for direct GRPO: {MODEL_ID}")
    model, tokenizer, device, dtype = _load_model(tokenizer, model_revision)

    trainer = DapoAccumulationGRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=[slidegen_composite_reward],
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset if eval_enabled else None,
    )
    trainer.model_id = MODEL_ID
    trainer.dapo_accumulation_factor = dapo_accumulation_factor
    trainer.training_contract = fingerprint

    manifest = get_runtime_metadata(
        {
            "run_name": "direct_grpo",
            "run_id": run_id,
            "model_id": MODEL_ID,
            "training_contract": fingerprint,
            "output_dir": str(OUTPUT_DIR),
            "resume_checkpoint": str(checkpoint) if checkpoint else None,
            "total_steps": TOTAL_STEPS,
            "train_documents": len(train_documents),
            "eval_documents": len(eval_documents),
            "train_prompts": len(train_rows),
            "eval_prompts": len(eval_rows),
            "image_cache_dir": str(image_cache_dir()),
            "train_image_prompts": train_image_prompts,
            "eval_image_prompts": eval_image_prompts,
            "num_generations": NUM_GENERATIONS,
            "generation_batch_size": GENERATION_BATCH_SIZE,
            "gradient_accumulation_steps": GRAD_ACCUMULATION,
            "max_completion_length": MAX_COMPLETION_LENGTH,
            "loss_type": training_args.loss_type,
            "dapo_accumulation_factor": dapo_accumulation_factor,
            "steps_per_generation": training_args.steps_per_generation,
            "epsilon": training_args.epsilon,
            "epsilon_high": training_args.epsilon_high,
            "mask_truncated_completions": True,
            "offline_dataset": corpus_path,
            "tool_retriever_index": str(RETRIEVER_INDEX_DIR),
            "device": device,
            "run_log": str(run_log_path),
        }
    )
    write_json(run_log_dir / "manifest.json", manifest)

    print(
        f"Starting GRPO: steps={TOTAL_STEPS}, prompts={len(train_rows)}, "
        f"generations={NUM_GENERATIONS}, generation_batch={GENERATION_BATCH_SIZE}"
    )
    if checkpoint:
        print(f"Resuming full trainer state from {checkpoint}")
    train_result = trainer.train(
        resume_from_checkpoint=str(checkpoint) if checkpoint else None
    )

    final_adapter = OUTPUT_DIR / "final_adapter"
    trainer.model.save_pretrained(final_adapter)
    tokenizer.save_pretrained(final_adapter)
    trainer.save_state()

    history = list(trainer.state.log_history or [])
    numeric_history = [
        {
            key: value
            for key, value in row.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        }
        for row in history
    ]
    write_json(run_log_dir / "metrics.json", numeric_history)
    save_metric_trend_image(
        numeric_history,
        run_log_dir / "metrics_trend.png",
        title="Direct GRPO Metrics",
        preferred_keys=[
            "loss",
            "reward",
            "eval_reward",
            "learning_rate",
            "grad_norm",
            "kl",
            "entropy",
        ],
    )
    final_metrics = dict(train_result.metrics or {})
    manifest.update(
        {
            "final_adapter": str(final_adapter),
            "global_step": trainer.state.global_step,
            "final_metrics": final_metrics,
        }
    )
    write_json(run_log_dir / "manifest.json", manifest)
    save_text_summary_image(
        run_log_dir / "run_summary.png",
        "Direct GRPO Run Summary",
        [
            {
                "title": "Result",
                "body": (
                    f"Steps: {trainer.state.global_step}/{TOTAL_STEPS}\n"
                    f"Train prompts: {len(train_rows)}\n"
                    f"Eval prompts: {len(eval_rows)}\n"
                    f"Final adapter: {final_adapter}\n"
                    f"Metrics: {json.dumps(final_metrics, default=str)}"
                ),
            }
        ],
        subtitle=f"Run {run_id}",
        footer=f"Log: {run_log_path.name}",
    )
    print(f"Training complete. Final adapter: {final_adapter}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preflight-only", action="store_true",
        help="Validate data, config, RAG, renderer and rewards without loading policy weights",
    )
    args = parser.parse_args(argv)
    try:
        _train_main(preflight_only=args.preflight_only)
    finally:
        close_render_runtime()


if __name__ == "__main__":
    main()
