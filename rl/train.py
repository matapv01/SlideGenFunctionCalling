"""Direct GRPO training for the production XML SlideGen pipeline."""

from __future__ import annotations

import argparse
import json
import math
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
    ValidationStopCallback,
)
from rl.image_assets import image_cache_dir
from rl.rewards.composite_reward import (
    preflight_reward_runtime,
    configure_sample_dump,
    slidegen_composite_reward,
)
from rl.rewards.content_reward import set_text_embedder
from rl.run_artifacts import (
    DetailedTrainingLogCallback,
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
TOTAL_STEPS = int(os.getenv("TOTAL_STEPS", "0"))
MAX_TRAIN_EPOCHS = float(os.getenv("GRPO_MAX_TRAIN_EPOCHS", "3"))
EARLY_STOPPING = os.getenv("GRPO_EARLY_STOPPING", "true").lower() in {"1", "true", "yes", "on"}
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "1e-6"))
TRAIN_BATCH_SIZE = int(os.getenv("PER_DEVICE_TRAIN_BATCH_SIZE", "1"))
GRAD_ACCUMULATION = int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "16"))
NUM_GENERATIONS = int(os.getenv("NUM_GENERATIONS", "4"))
GENERATION_BATCH_SIZE = int(os.getenv("GRPO_GENERATION_BATCH_SIZE", "4"))
EVAL_BATCH_SIZE = int(os.getenv("GRPO_EVAL_BATCH_SIZE", str(NUM_GENERATIONS)))
MAX_COMPLETION_LENGTH = int(os.getenv("MAX_COMPLETION_LENGTH", "3072"))
LOSS_TYPE = os.getenv("GRPO_LOSS_TYPE", "dapo")
EVAL_STEPS = int(os.getenv("GRPO_EVAL_STEPS", "25"))
SAVE_STEPS = int(os.getenv("GRPO_SAVE_STEPS", str(EVAL_STEPS or 25)))
EVAL_DOCS = int(os.getenv("GRPO_EVAL_DOCS", "5"))
EVAL_ON_START = os.getenv("GRPO_EVAL_ON_START", "false").lower() in {"1", "true", "yes", "on"}
DATA_SEED = int(os.getenv("GRPO_DATA_SEED", "42"))
USE_CPU = os.getenv("USE_CPU", "false").lower() in {"1", "true", "yes", "on"}
USE_LORA = os.getenv("USE_LORA", "true").lower() in {"1", "true", "yes", "on"}
USE_GRAD_CHECKPOINT = os.getenv("USE_GRAD_CHECKPOINT", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
LOAD_IN_4BIT = os.getenv("GRPO_LOAD_IN_4BIT", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
INIT_ADAPTER = os.getenv("GRPO_INIT_ADAPTER", "").strip()
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
    if TOTAL_STEPS < 0:
        raise ValueError("TOTAL_STEPS must be zero (derive from epochs) or positive")
    if MAX_TRAIN_EPOCHS <= 0:
        raise ValueError("GRPO_MAX_TRAIN_EPOCHS must be positive")
    if EARLY_STOPPING and EVAL_STEPS < 1:
        raise ValueError("Early stopping requires GRPO_EVAL_STEPS > 0")
    if min(TRAIN_BATCH_SIZE, GRAD_ACCUMULATION, GENERATION_BATCH_SIZE, SAVE_STEPS) < 1:
        raise ValueError("Batch sizes, accumulation and save steps must be positive")
    if NUM_GENERATIONS < 2:
        raise ValueError("NUM_GENERATIONS must be >= 2 for GRPO")
    if EVAL_BATCH_SIZE < 1 or EVAL_BATCH_SIZE % NUM_GENERATIONS:
        raise ValueError("GRPO_EVAL_BATCH_SIZE must be a positive multiple of NUM_GENERATIONS")
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


def _prepare_qwen35_moe_for_kbit_training(model):
    """Freeze the BF16 MoE base without PEFT's blanket FP32 upcast."""
    for name, param in model.named_parameters():
        param.requires_grad = False
        # Keep the large fused expert matrices in BF16; upcast only small norms.
        if "norm" in name.lower() and param.dtype in (torch.float16, torch.bfloat16):
            param.data = param.data.to(torch.float32)
    if USE_GRAD_CHECKPOINT and hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    return model


def _warm_start_lora(model, adapter_dir: str) -> None:
    """Initialize LoRA from a finished run's adapter (fresh optimizer/scheduler, current contract)."""
    from safetensors.torch import load_file

    # Copy tensors by name: PEFT's set_peft_model_state_dict breaks on Transformers 5.x weight converters.
    state = load_file(str(Path(adapter_dir) / "adapter_model.safetensors"))
    targets = {
        name.replace(".default.", "."): parameter
        for name, parameter in model.named_parameters()
        if "lora_" in name
    }
    if set(state) != set(targets):
        raise RuntimeError(
            "Warm-start adapter does not match the LoRA config: "
            f"missing={sorted(set(targets) - set(state))[:3]} extra={sorted(set(state) - set(targets))[:3]}"
        )
    with torch.no_grad():
        for name, tensor in state.items():
            target = targets[name]
            if target.shape != tensor.shape:
                raise RuntimeError(f"Warm-start shape mismatch for {name}: {tuple(tensor.shape)} vs {tuple(target.shape)}")
            target.copy_(tensor.to(device=target.device, dtype=target.dtype))
    print(f"Warm-started LoRA from {adapter_dir} ({len(state)} tensors)")


def _route_gated_delta_kernel_by_grad() -> str:
    """Use FLA's chunk kernel for rollouts only; its backward is wrong on Hopper with Triton < 3.7.1 (fla #640)."""
    from transformers.models.qwen3_5_moe import modeling_qwen3_5_moe as qwen

    fast = qwen.torch_chunk_gated_delta_rule
    reference = getattr(fast, "__wrapped__", None)
    if reference is None or getattr(fast, "_routed_by_grad", False):
        return "unchanged"

    def routed(*args, **kwargs):
        return (reference if torch.is_grad_enabled() else fast)(*args, **kwargs)

    routed._routed_by_grad = True
    qwen.torch_chunk_gated_delta_rule = routed
    return "fla_no_grad_torch_grad"


def _load_model(tokenizer=None, revision=None):
    device, dtype = _model_runtime()
    if os.getenv("GRPO_FLA_ROLLOUT_ONLY", "true").lower() in {"1", "true", "yes", "on"}:
        print(f"Gated-delta kernel routing: {_route_gated_delta_kernel_by_grad()}")
    model_kwargs = {
        "torch_dtype": dtype,
        "trust_remote_code": True,
        "low_cpu_mem_usage": True,
        "revision": revision,
    }
    if LOAD_IN_4BIT:
        if device != "cuda":
            raise RuntimeError("GRPO_LOAD_IN_4BIT requires CUDA")
        from peft import prepare_model_for_kbit_training
        from transformers import BitsAndBytesConfig

        model_kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=dtype,
            bnb_4bit_use_double_quant=True,
        )
        # Quantized weights are placed during loading and cannot be moved later.
        model_kwargs["device_map"] = {"": 0}
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **model_kwargs)
    if tokenizer is None:
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID, trust_remote_code=True, revision=revision
        )
    if LOAD_IN_4BIT:
        if getattr(model.config, "model_type", "") in {"qwen3_5_moe", "qwen3_5_moe_text"}:
            # Routed experts are fused Parameter tensors, not Linear modules, so
            # bnb leaves them in BF16. PEFT's generic helper would copy every
            # such tensor to FP32 and exhaust an 80GB GPU before training starts.
            model = _prepare_qwen35_moe_for_kbit_training(model)
        else:
            model = prepare_model_for_kbit_training(
                model,
                use_gradient_checkpointing=USE_GRAD_CHECKPOINT,
            )
    model = get_peft_model(model, _lora_config())
    if INIT_ADAPTER:
        _warm_start_lora(model, INIT_ADAPTER)
    if USE_GRAD_CHECKPOINT and device == "cuda" and not LOAD_IN_4BIT:
        model.gradient_checkpointing_enable()
    model.config.use_cache = False
    if device == "cuda" and not LOAD_IN_4BIT:
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
    global_batch_size = TRAIN_BATCH_SIZE * int(os.getenv("WORLD_SIZE", "1"))
    prompts_per_update = (
        GRAD_ACCUMULATION * global_batch_size // NUM_GENERATIONS
    )
    steps_per_epoch = max(1, math.ceil(len(train_rows) / prompts_per_update))
    max_steps = TOTAL_STEPS or max(1, math.ceil(steps_per_epoch * MAX_TRAIN_EPOCHS))
    if EARLY_STOPPING and SAVE_STEPS != EVAL_STEPS:
        raise ValueError(
            "GRPO_SAVE_STEPS must equal GRPO_EVAL_STEPS when best-checkpoint "
            "selection and early stopping are enabled"
        )
    scheduler_type = os.getenv(
        "GRPO_LR_SCHEDULER_TYPE",
        "reduce_lr_on_plateau" if eval_enabled else "linear",
    )
    default_warmup_steps = 0 if scheduler_type == "reduce_lr_on_plateau" else max(2, round(max_steps * 0.03))
    warmup_steps = int(os.getenv("WARMUP_STEPS", str(default_warmup_steps)))
    training_args = GRPOConfig(
        output_dir=str(OUTPUT_DIR),
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=EVAL_BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUMULATION,
        generation_batch_size=GENERATION_BATCH_SIZE,
        max_steps=max_steps,
        warmup_steps=warmup_steps,
        lr_scheduler_type=scheduler_type,
        lr_scheduler_kwargs={
            "mode": "max", "factor": float(os.getenv("GRPO_LR_REDUCE_FACTOR", "0.5")),
            "patience": int(os.getenv("GRPO_LR_REDUCE_PATIENCE", "1")),
            "threshold": float(os.getenv("GRPO_LR_REDUCE_THRESHOLD", "0.02")),
            "threshold_mode": "abs", "cooldown": 0,
            "min_lr": float(os.getenv("GRPO_MIN_LEARNING_RATE", "1e-7")),
        } if scheduler_type == "reduce_lr_on_plateau" else {},
        metric_for_best_model="eval_reward" if eval_enabled else None,
        greater_is_better=True if eval_enabled else None,
        load_best_model_at_end=EARLY_STOPPING and eval_enabled,
        logging_steps=1,
        logging_first_step=True,
        save_strategy="steps",
        save_steps=SAVE_STEPS,
        save_total_limit=int(os.getenv("GRPO_SAVE_TOTAL_LIMIT", "3")),
        eval_strategy="steps" if eval_enabled else "no",
        eval_steps=EVAL_STEPS if eval_enabled else None,
        eval_on_start=EVAL_ON_START and eval_enabled,
        report_to="none",
        num_generations=NUM_GENERATIONS,
        num_generations_eval=NUM_GENERATIONS,
        max_completion_length=MAX_COMPLETION_LENGTH,
        temperature=float(os.getenv("GRPO_TEMPERATURE", "1.0")),
        top_p=float(os.getenv("GRPO_TOP_P", "0.95")),
        top_k=int(os.getenv("GRPO_TOP_K", "0")),
        beta=float(os.getenv("GRPO_BETA", "0.0")),
        epsilon=float(os.getenv("GRPO_EPSILON", "0.2")),
        epsilon_high=float(os.getenv("GRPO_EPSILON_HIGH", "0.28")),
        mask_truncated_completions=True,
        loss_type=LOSS_TYPE,
        # Group-std scaling turns ViT noise in near-tied groups into full-size advantages.
        scale_rewards=os.getenv("GRPO_SCALE_REWARDS", "batch"),
        use_cpu=device == "cpu",
        bf16=dtype == torch.bfloat16,
        fp16=dtype == torch.float16,
        tf32=True if device == "cuda" else None,
        gradient_checkpointing=USE_GRAD_CHECKPOINT and device == "cuda",
        seed=DATA_SEED,
        data_seed=DATA_SEED,
        remove_unused_columns=False,
    )
    # Transformers 5.17 does not expose eval_seed on GRPOConfig, so attach it
    # after construction for the trainer's deterministic evaluation wrapper.
    training_args.eval_seed = int(os.getenv("GRPO_EVAL_SEED", str(DATA_SEED + 1)))

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
    sample_count = min(len(eval_rows), int(os.getenv("GRPO_SAMPLE_SLIDES", "4")))
    if sample_count:
        picked = [eval_rows[i * len(eval_rows) // sample_count] for i in range(sample_count)]
        configure_sample_dump(
            OUTPUT_DIR / "samples", [(row["source_doc_id"], row["slide_index"]) for row in picked]
        )
        print("Sample slides saved each eval:",
              [f"{row['source_doc_id']}#{row['slide_index']}:{row['assigned_tool_name']}" for row in picked])
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
    trainer.add_callback(DetailedTrainingLogCallback(run_log_dir, run_id))
    if EARLY_STOPPING and eval_enabled:
        min_steps = steps_per_epoch * int(os.getenv("GRPO_EARLY_STOP_MIN_EPOCHS", "1"))
        trainer.add_callback(ValidationStopCallback(
            metric_name="eval_reward",
            patience=int(os.getenv("GRPO_EARLY_STOP_PATIENCE", "4")),
            threshold=float(os.getenv("GRPO_EARLY_STOP_THRESHOLD", "0.02")),
            min_steps=min_steps,
            state_path=OUTPUT_DIR / "early_stopping_state.json",
        ))
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
            "total_steps": max_steps,
            "max_train_epochs": MAX_TRAIN_EPOCHS,
            "steps_per_epoch_estimate": steps_per_epoch,
            "prompts_per_optimizer_update_estimate": prompts_per_update,
            "lr_scheduler_type": training_args.lr_scheduler_type,
            "lr_scheduler_kwargs": training_args.lr_scheduler_kwargs,
            "init_adapter": INIT_ADAPTER or None,
            "early_stopping": EARLY_STOPPING and eval_enabled,
            "eval_on_start": training_args.eval_on_start,
            "early_stopping_metric": "eval_reward",
            "early_stopping_patience": int(os.getenv("GRPO_EARLY_STOP_PATIENCE", "4")),
            "early_stopping_min_steps": steps_per_epoch * int(os.getenv("GRPO_EARLY_STOP_MIN_EPOCHS", "1")),
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
            "load_in_4bit": LOAD_IN_4BIT,
            "dapo_accumulation_factor": dapo_accumulation_factor,
            "steps_per_generation": training_args.steps_per_generation,
            "epsilon": training_args.epsilon,
            "epsilon_high": training_args.epsilon_high,
            "mask_truncated_completions": True,
            "offline_dataset": corpus_path,
            "tool_retriever_index": str(RETRIEVER_INDEX_DIR),
            "device": device,
            "run_log": str(run_log_path),
            "training_metrics_jsonl": str(run_log_dir / "training_metrics.jsonl"),
            "training_readable_log": str(run_log_dir / "training_readable.log"),
        }
    )
    write_json(run_log_dir / "manifest.json", manifest)

    print(
        f"Starting GRPO: steps={max_steps}, prompts={len(train_rows)}, "
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
                    f"Steps: {trainer.state.global_step}/{max_steps}\n"
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
