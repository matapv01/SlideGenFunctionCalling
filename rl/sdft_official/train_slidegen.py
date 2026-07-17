
"""Official-style SDFT entrypoint for SlideGen.

This adapts the repo's SlideGen prompts to the vendored TRL/Transformers
DistilTrainer path with official PEFT support. No Unsloth, no custom SFT loop.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import random
import shutil
import sys
import types
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "300")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "300")
os.environ.setdefault("PYTORCH_ALLOC_CONF", "expandable_segments:True")

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() == "true"


def _ensure_trl_compat() -> None:
    try:
        import trl.extras
        import trl.models
        import trl.trainer
    except ImportError as exc:
        raise ImportError(
            "SDFT official training requires TRL and its dependencies installed."
        ) from exc

    if not hasattr(trl.extras, "vllm_client"):
        mod = types.ModuleType("trl.extras.vllm_client")

        class _StubVLLMClient:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("vLLM is not available in this environment.")

        mod.VLLMClient = _StubVLLMClient
        trl.extras.vllm_client = mod
        sys.modules["trl.extras.vllm_client"] = mod

    if not hasattr(trl.models, "prepare_peft_model"):
        from peft import get_peft_model

        def _prepare_peft_model(model, peft_config, args):
            return get_peft_model(model, peft_config) if peft_config is not None else model

        trl.models.prepare_peft_model = _prepare_peft_model

    if not hasattr(trl.trainer, "base_trainer"):
        from trl.trainer.grpo_trainer import _BaseTrainer

        trl.trainer.base_trainer = types.ModuleType("trl.trainer.base_trainer")
        trl.trainer.base_trainer.BaseTrainer = _BaseTrainer
        sys.modules["trl.trainer.base_trainer"] = trl.trainer.base_trainer


_ensure_trl_compat()

from rl.common import (
    LORA_ALPHA,
    LORA_DROPOUT,
    LORA_R,
    LORA_TARGET_MODULES,
    auto_select_gpu,
    build_flat_tools,
)

auto_select_gpu()

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from backend.workflows.slidegen_workflow.tools.tool_des import TOOLS_DICT
from backend.workflows.slidegen_workflow.utils.helper import (
    QWEN_CHAT_TEMPLATE,
    format_tool_for_qwen,
)
from backend.workflows.slidegen_workflow.utils.prompts import (
    QWEN_GENERATOR_HUMAN_TEMPLATE,
    QWEN_GENERATOR_SYSTEM_PROMPT,
)
from rl.sdft_official.distil_config import DistilConfig
from rl.sdft_official.distil_trainer import DistilTrainer
from rl.run_artifacts import (
    append_jsonl,
    get_runtime_metadata,
    save_metric_trend_image,
    save_text_summary_image,
    start_run_logging,
    write_json,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Official-style SDFT for SlideGen")
    parser.add_argument("--model_name", default=os.getenv("TRAINING_MODEL_ID", "Qwen/Qwen3-8B"))
    parser.add_argument(
        "--data_path",
        default=os.getenv(
            "SDFT_DATA_PATH",
            os.path.join(project_root, "rl", "data", "sft_function_call_dataset.json"),
        ),
    )
    parser.add_argument("--output_dir", default=os.getenv("SDFT_OUTPUT_DIR", "./qwen_slidegen_sdft"))
    parser.add_argument("--learning_rate", type=float, default=float(os.getenv("SDFT_LEARNING_RATE", "2e-5")))
    parser.add_argument("--num_train_epochs", type=int, default=int(os.getenv("SDFT_EPOCHS", "2")))
    parser.add_argument(
        "--per_device_train_batch_size", type=int, default=int(os.getenv("SFT_BATCH_SIZE", "1"))
    )
    parser.add_argument(
        "--gradient_accumulation_steps", type=int, default=int(os.getenv("SFT_GRAD_ACCUM", "32"))
    )
    parser.add_argument("--max_prompt_length", type=int, default=int(os.getenv("SDFT_MAX_PROMPT_LENGTH", "2048")))
    parser.add_argument(
        "--max_completion_length", type=int, default=int(os.getenv("SDFT_MAX_COMPLETION_LENGTH", "512"))
    )
    parser.add_argument("--num_generations", type=int, default=int(os.getenv("SDFT_NUM_GENERATIONS", "1")))
    parser.add_argument(
        "--ref_model_mixup_alpha", type=float, default=float(os.getenv("SDFT_MIXUP_ALPHA", "0.01"))
    )
    parser.add_argument("--alpha", type=float, default=float(os.getenv("SDFT_ALPHA", "0.0")))
    parser.add_argument("--beta", type=float, default=float(os.getenv("SDFT_BETA", "0.0")))
    parser.add_argument(
        "--use_vllm",
        action=argparse.BooleanOptionalAction,
        default=_env_bool("SDFT_USE_VLLM", "true"),
    )
    parser.add_argument("--vllm_mode", default=os.getenv("SDFT_VLLM_MODE", "colocate"))
    parser.add_argument(
        "--vllm_tensor_parallel_size",
        type=int,
        default=int(os.getenv("SDFT_VLLM_TENSOR_PARALLEL_SIZE", "1")),
    )
    parser.add_argument(
        "--vllm_gpu_memory_utilization",
        type=float,
        default=float(os.getenv("SDFT_VLLM_GPU_MEMORY_UTILIZATION", "0.6")),
    )
    parser.add_argument(
        "--vllm_enable_sleep_mode",
        action=argparse.BooleanOptionalAction,
        default=_env_bool("SDFT_VLLM_ENABLE_SLEEP_MODE", "true"),
    )
    parser.add_argument("--seed", type=int, default=int(os.getenv("SDFT_SEED", "42")))
    parser.add_argument(
        "--num_loss_tokens_to_skip",
        type=int,
        default=int(os.getenv("SDFT_NUM_LOSS_TOKENS_TO_SKIP", "3")),
    )
    return parser.parse_args()


def _build_lora_config() -> LoraConfig:
    return LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        bias="none",
    )


def _pick_tools(category: str, correct_name: str, flat_tools: dict) -> list[dict]:
    if correct_name not in flat_tools:
        return [format_tool_for_qwen(tool) for tool in list(flat_tools.values())[:6]]

    names = [t.name for t in TOOLS_DICT.get(category, []) if t.name in flat_tools]
    others = [name for name in names if name != correct_name]
    random.shuffle(others)
    selected = [correct_name] + others[:5]
    return [format_tool_for_qwen(flat_tools[name]) for name in selected]


def _build_user_text(sample: dict) -> str:
    return QWEN_GENERATOR_HUMAN_TEMPLATE.format(
        style_context=(sample.get("style_context") or "")[:500],
        design_instruction=(sample.get("design_instruction") or "")[:600],
        slide_content=(sample.get("slide_content") or sample.get("content", ""))[:1200],
    )


def _render_prompt(tokenizer, user_text: str, tools: list[dict]) -> str:
    messages = [
        {"role": "system", "content": QWEN_GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]
    return tokenizer.apply_chat_template(messages, tools=tools, tokenize=False, add_generation_prompt=True)


def _build_example(tokenizer, sample: dict, flat_tools: dict) -> dict:
    tool_call = sample["tool_call"]
    tools = _pick_tools(sample["category"], tool_call["name"], flat_tools)
    user_text = _build_user_text(sample)
    prompt = _render_prompt(tokenizer, user_text, tools)

    teacher_text = (
        f"{user_text}\n\n"
        "This is an example for a response to the slide layout task:\n"
        f"<tool_call>{json.dumps(tool_call, ensure_ascii=False)}</tool_call>\n\n"
        "Now answer with a response of your own, using the same function-call format."
    )
    teacher_prompt = _render_prompt(tokenizer, teacher_text, tools)
    return {"prompt": prompt, "teacher_prompt": teacher_prompt}


def build_dataset(data_path: str, tokenizer) -> Dataset:
    with open(data_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
    random.shuffle(samples)

    flat_tools = build_flat_tools(TOOLS_DICT)
    return Dataset.from_list([_build_example(tokenizer, sample, flat_tools) for sample in samples])


def main():
    args = parse_args()
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    use_cuda = torch.cuda.is_available()
    use_bf16 = use_cuda and torch.cuda.is_bf16_supported()
    model_dtype = torch.bfloat16 if use_bf16 else (torch.float16 if use_cuda else torch.float32)

    if args.use_vllm and (not use_cuda or importlib.util.find_spec("vllm") is None):
        print("vLLM is unavailable here; falling back to transformers.generate().")
        args.use_vllm = False

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(project_root, "rl", "log", "sdft_official", f"run_{run_id}")
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    run_log_path = start_run_logging(log_dir)
    print(f"  Run log: {run_log_path}")
    if args.use_vllm and args.vllm_mode == "colocate" and args.vllm_gpu_memory_utilization > 0.65:
        print(
            f"  [WARN] SDFT_VLLM_GPU_MEMORY_UTILIZATION={args.vllm_gpu_memory_utilization} is too high "
            "for colocated SDFT on one 48GB GPU; capping to 0.6."
        )
        args.vllm_gpu_memory_utilization = 0.6

    print(f"Loading model: {args.model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        torch_dtype=model_dtype,
        trust_remote_code=True,
    )
    teacher_model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        torch_dtype=model_dtype,
        trust_remote_code=True,
    )

    peft_config = _build_lora_config()
    model = get_peft_model(model, peft_config)
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    teacher_model = get_peft_model(teacher_model, _build_lora_config())
    teacher_model.load_state_dict(model.state_dict())
    teacher_model.eval()
    teacher_model.requires_grad_(False)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    tokenizer.chat_template = QWEN_CHAT_TEMPLATE
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dataset = build_dataset(args.data_path, tokenizer)
    print(f"Dataset: {len(dataset)} samples")

    sample_count = len(dataset)
    prompt_lengths = [len(dataset[i]["prompt"]) for i in range(sample_count)] if sample_count else [0]
    teacher_lengths = [len(dataset[i]["teacher_prompt"]) for i in range(sample_count)] if sample_count else [0]
    preview_count = min(3, sample_count)
    preview_samples = []
    preview_sections = [
        {
            "title": "Dataset Stats",
            "body": "\n".join(
                [
                    f"Samples: {sample_count}",
                    f"Prompt chars avg/min/max: {sum(prompt_lengths) / len(prompt_lengths):.1f} / {min(prompt_lengths)} / {max(prompt_lengths)}",
                    f"Teacher chars avg/min/max: {sum(teacher_lengths) / len(teacher_lengths):.1f} / {min(teacher_lengths)} / {max(teacher_lengths)}",
                    f"Data path: {args.data_path}",
                    f"Output dir: {args.output_dir}",
                ]
            ),
        }
    ]
    for idx in range(preview_count):
        sample = dataset[idx]
        preview_samples.append(
            {
                "index": idx,
                "prompt": sample["prompt"],
                "teacher_prompt": sample["teacher_prompt"],
                "prompt_chars": len(sample["prompt"]),
                "teacher_chars": len(sample["teacher_prompt"]),
            }
        )
        preview_sections.append(
            {
                "title": f"Sample {idx + 1}",
                "body": "\n".join(
                    [
                        f"Prompt chars: {len(sample['prompt'])}",
                        f"Teacher chars: {len(sample['teacher_prompt'])}",
                        "Prompt:",
                        sample["prompt"][:900],
                        "Teacher prompt:",
                        sample["teacher_prompt"][:900],
                    ]
                ),
            }
        )

    manifest = get_runtime_metadata(
        {
            "run_name": "sdft_official",
            "run_id": run_id,
            "log_dir": log_dir,
            "output_dir": args.output_dir,
            "model_name": args.model_name,
            "data_path": args.data_path,
            "learning_rate": args.learning_rate,
            "num_train_epochs": args.num_train_epochs,
            "per_device_train_batch_size": args.per_device_train_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "max_prompt_length": args.max_prompt_length,
            "max_completion_length": args.max_completion_length,
            "num_generations": args.num_generations,
            "ref_model_mixup_alpha": args.ref_model_mixup_alpha,
            "alpha": args.alpha,
            "beta": args.beta,
            "use_vllm": args.use_vllm,
            "vllm_mode": args.vllm_mode,
            "vllm_tensor_parallel_size": args.vllm_tensor_parallel_size,
            "vllm_gpu_memory_utilization": args.vllm_gpu_memory_utilization,
            "vllm_enable_sleep_mode": args.vllm_enable_sleep_mode,
            "num_loss_tokens_to_skip": args.num_loss_tokens_to_skip,
            "dataset": {
                "samples": sample_count,
                "prompt_chars_avg": sum(prompt_lengths) / len(prompt_lengths),
                "prompt_chars_min": min(prompt_lengths),
                "prompt_chars_max": max(prompt_lengths),
                "teacher_chars_avg": sum(teacher_lengths) / len(teacher_lengths),
                "teacher_chars_min": min(teacher_lengths),
                "teacher_chars_max": max(teacher_lengths),
            },
        }
    )
    write_json(os.path.join(log_dir, "manifest.json"), manifest)
    write_json(os.path.join(log_dir, "dataset_preview.json"), {"stats": manifest["dataset"], "samples": preview_samples})
    save_text_summary_image(
        os.path.join(log_dir, "dataset_preview.png"),
        "SDFT Dataset Preview",
        preview_sections,
        subtitle=f"Run {run_id}",
        footer=f"Log: {run_log_path.name}",
    )

    config = DistilConfig(
        seed=args.seed,
        output_dir=args.output_dir,
        logging_dir=log_dir,
        learning_rate=args.learning_rate,
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",
        logging_steps=1,
        bf16=use_bf16,
        fp16=use_cuda and not use_bf16,
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        max_prompt_length=args.max_prompt_length,
        max_completion_length=args.max_completion_length,
        num_train_epochs=args.num_train_epochs,
        num_iterations=1,
        num_generations=args.num_generations,
        save_strategy="steps",
        save_steps=100,
        max_grad_norm=1.0,
        report_to="none",
        remove_unused_columns=False,
        alpha=args.alpha,
        beta=args.beta,
        generate_from_teacher=True,
        use_vllm=args.use_vllm,
        vllm_mode=args.vllm_mode,
        vllm_tensor_parallel_size=args.vllm_tensor_parallel_size,
        vllm_gpu_memory_utilization=args.vllm_gpu_memory_utilization,
        vllm_enable_sleep_mode=args.vllm_enable_sleep_mode,
        sync_ref_model=True,
        ref_model_sync_steps=1,
        ref_model_mixup_alpha=args.ref_model_mixup_alpha,
        vllm_importance_sampling_correction=True,
        num_loss_tokens_to_skip=args.num_loss_tokens_to_skip,
    )

    with open(os.path.join(log_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "model_name": args.model_name,
                "data_path": args.data_path,
                "output_dir": args.output_dir,
                "learning_rate": args.learning_rate,
                "num_train_epochs": args.num_train_epochs,
                "per_device_train_batch_size": args.per_device_train_batch_size,
                "gradient_accumulation_steps": args.gradient_accumulation_steps,
                "max_prompt_length": args.max_prompt_length,
                "max_completion_length": args.max_completion_length,
                "num_generations": args.num_generations,
                "ref_model_mixup_alpha": args.ref_model_mixup_alpha,
                "alpha": args.alpha,
                "beta": args.beta,
                "use_vllm": args.use_vllm,
                "vllm_mode": args.vllm_mode,
                "vllm_enable_sleep_mode": args.vllm_enable_sleep_mode,
                "num_loss_tokens_to_skip": args.num_loss_tokens_to_skip,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\n{'=' * 60}")
    print(f"SDFT Training - {run_id}")
    print(f"  Model: {args.model_name}")
    print(f"  Dataset: {len(dataset)} samples")
    print(f"  Loss: forward KL alpha={args.alpha}, beta={args.beta}")
    print(f"  VLLM: {args.use_vllm} ({args.vllm_mode})")
    print(f"  VLLM GPU util: {args.vllm_gpu_memory_utilization}")
    print(f"  Log dir: {log_dir}")
    print(f"{'=' * 60}")

    trainer = DistilTrainer(
        model=model,
        ref_model=teacher_model,
        args=config,
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    trainer.train()

    history = list(trainer.state.log_history or [])
    metric_rows = [row for row in history if any(isinstance(v, (int, float)) for v in row.values())]
    write_json(os.path.join(log_dir, "metrics.json"), history)
    append_jsonl(os.path.join(log_dir, "metrics.jsonl"), metric_rows)
    if metric_rows:
        save_metric_trend_image(
            metric_rows,
            os.path.join(log_dir, "metrics_trend.png"),
            title="SDFT Training Metrics",
            preferred_keys=["loss", "reward", "learning_rate", "grad_norm", "entropy", "kl"],
        )

    final_metrics = metric_rows[-1] if metric_rows else {}
    manifest["final_metrics"] = final_metrics
    manifest["history_rows"] = len(history)
    manifest["artifacts"] = {
        "metrics_json": os.path.join(log_dir, "metrics.json"),
        "metrics_jsonl": os.path.join(log_dir, "metrics.jsonl"),
        "metrics_trend_png": os.path.join(log_dir, "metrics_trend.png"),
        "dataset_preview_png": os.path.join(log_dir, "dataset_preview.png"),
        "summary_png": os.path.join(log_dir, "training_summary.png"),
        "run_log": str(run_log_path),
    }
    write_json(os.path.join(log_dir, "manifest.json"), manifest)
    summary_lines = [
        f"Model: {args.model_name}",
        f"Samples: {len(dataset)}",
        f"History rows: {len(history)}",
    ]
    if final_metrics:
        summary_lines.append(f"Final metrics: {json.dumps(final_metrics, ensure_ascii=False, default=str)}")
    save_text_summary_image(
        os.path.join(log_dir, "training_summary.png"),
        "SDFT Run Summary",
        [
            {
                "title": "Run",
                "body": "\n".join(summary_lines),
            }
        ],
        subtitle=f"Run {run_id}",
        footer=f"Log: {run_log_path.name}",
    )

    final_dir = os.path.join(os.path.abspath(args.output_dir), "final_adapter")
    if os.path.exists(final_dir):
        shutil.rmtree(final_dir)
    os.makedirs(final_dir, exist_ok=True)

    trained = trainer.accelerator.unwrap_model(trainer.model)
    trained.save_pretrained(final_dir, safe_serialization=True)
    tokenizer.save_pretrained(final_dir)
    print(f"Saved final adapter to {final_dir}")
    print(f"Done. Logs: {log_dir}")


if __name__ == "__main__":
    main()
