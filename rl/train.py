"""Direct GRPO training for the production XML SlideGen pipeline."""

from __future__ import annotations

import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("HF_HUB_ETAG_TIMEOUT", "300")
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "300")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
os.environ.setdefault("PYTORCH_ALLOC_CONF", "expandable_segments:True")

from rl.common import (
    LORA_ALPHA,
    LORA_DROPOUT,
    LORA_R,
    LORA_TARGET_MODULES,
    auto_select_gpu,
    setup_tokenizer,
)

auto_select_gpu()

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig

from backend.infrastructure.rag.gemini_provider import (
    LocalEmbeddingToolRetrieveProvider,
)
from backend.workflows.slidegen_workflow.executors.tool_plan_executor import (
    tool_matches_image_mode,
)
from backend.workflows.slidegen_workflow.graph.stage import DeckStylePlan
from backend.workflows.slidegen_workflow.nodes.section_batch_orchestrator import (
    assign_layouts,
)
from rl.grpo_trainer import (
    HistoricalBaselineGRPOTrainer,
    HistoricalRewardBaseline,
)
from rl.rewards.composite_reward import (
    preflight_reward_runtime,
    set_text_embedder,
    slidegen_composite_reward,
)
from rl.run_artifacts import (
    get_runtime_metadata,
    save_metric_trend_image,
    save_text_summary_image,
    start_run_logging,
    write_json,
)
from rl.slidegen_adapter import (
    QWEN_CHAT_TEMPLATE,
    QWEN_GENERATOR_SYSTEM_PROMPT,
    TOOLS_DICT,
    build_generator_human_prompt,
    format_tool_for_qwen,
)
from scripts.generate_challenge_dataset import (
    DEFAULT_DATASET_PATH,
    load_offline_documents,
)


MODEL_ID = os.getenv("TRAINING_MODEL_ID", "Qwen/Qwen3-4B-Instruct-2507")
OUTPUT_DIR = Path(os.getenv("GRPO_OUTPUT_DIR", "./qwen_slidegen_grpo"))
RETRIEVER_INDEX_DIR = Path(
    os.getenv("GRPO_FAISS_INDEX_PATH", str(OUTPUT_DIR / "tool_retriever_index"))
)
TOTAL_STEPS = int(os.getenv("TOTAL_STEPS", "500"))
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "1e-6"))
TRAIN_BATCH_SIZE = int(os.getenv("PER_DEVICE_TRAIN_BATCH_SIZE", "1"))
GRAD_ACCUMULATION = int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "16"))
NUM_GENERATIONS = int(os.getenv("NUM_GENERATIONS", "4"))
GENERATION_BATCH_SIZE = int(os.getenv("GRPO_GENERATION_BATCH_SIZE", "4"))
MAX_COMPLETION_LENGTH = int(os.getenv("MAX_COMPLETION_LENGTH", "512"))
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


def _validate_config() -> None:
    if TOTAL_STEPS < 1:
        raise ValueError("TOTAL_STEPS must be positive")
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


def _checkpoint_complete(path: Path) -> bool:
    if not (path / "historical_reward_baseline.json").is_file():
        return False
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


def _latest_checkpoint() -> Path | None:
    if not RESUME or not OUTPUT_DIR.is_dir():
        return None
    candidates = []
    for path in OUTPUT_DIR.glob("checkpoint-*"):
        try:
            step = int(path.name.rsplit("-", 1)[1])
        except (IndexError, ValueError):
            continue
        if _checkpoint_complete(path):
            candidates.append((step, path))
    return max(candidates, default=(0, None))[1]


_PALETTES = (
    ("#F8FAFC", "#0F172A", "#475569", "#0D9488", "#1F2937"),
    ("#FFF7ED", "#431407", "#9A3412", "#EA580C", "#292524"),
    ("#F5F3FF", "#2E1065", "#6D28D9", "#7C3AED", "#1F2937"),
    ("#F0FDF4", "#052E16", "#166534", "#16A34A", "#14532D"),
)


def _deck_style(document: list[dict]) -> dict:
    source_id = str(document[0].get("source_doc_id", "0"))
    palette = _PALETTES[sum(source_id.encode("utf-8")) % len(_PALETTES)]
    topic = str(document[0].get("user_prompt") or "Untitled presentation")
    topic = topic.splitlines()[0][:120]
    style = DeckStylePlan(deck_topic=topic).model_dump()
    (
        style["background_color"],
        style["primary_color"],
        style["secondary_color"],
        style["accent_color"],
        style["text_color"],
    ) = palette
    return style


def _normalise_jobs(document: list[dict]) -> list[dict]:
    jobs = []
    for index, slide in enumerate(document):
        plan = dict(slide.get("plan") or {})
        if index == 0:
            plan["action"] = "INTRO_TOOLS"
        action = str(plan.get("action") or "CONTENT_TOOLS")
        compatible = [
            tool
            for tool in TOOLS_DICT.get(action, [])
            if tool_matches_image_mode(tool, "none", 0)
        ]
        if not compatible:
            action = "CONTENT_TOOLS"
        content = str(slide.get("user_prompt") or "").strip()
        design = str(plan.get("thought") or slide.get("design_instruction") or "")
        plan.update(
            {
                "action": action,
                "image_mode": "none",
                "slide_topic": content.splitlines()[0][:160],
                "visual_layout_request": design,
            }
        )
        jobs.append(
            {
                "index": index,
                "batch_id": f"document-{slide.get('source_doc_id', 'unknown')}",
                "section_id": f"document-{slide.get('source_doc_id', 'unknown')}",
                "plan": plan,
                "content": content,
                "approved_images": [],
                "source_slide": slide,
            }
        )
    return jobs


def _prepare_document(document: list[dict], tokenizer, tool_retriever) -> list[dict]:
    jobs = _normalise_jobs(document)
    assigned = assign_layouts(
        {"slide_jobs": jobs},
        {
            "configurable": {
                "tools_dict": TOOLS_DICT,
                "tool_retriever": tool_retriever,
            }
        },
    )["slide_jobs"]
    deck_style = _deck_style(document)
    style_json = json.dumps(deck_style, ensure_ascii=False, indent=2)
    samples = []
    for job in assigned:
        tool_name = str(job.get("preferred_tool_name") or "")
        if not tool_name:
            raise RuntimeError(
                f"No compatible no-image layout for slide {job.get('index')}"
            )
        category = job["plan"]["action"]
        tool = next(
            (
                candidate
                for candidate in TOOLS_DICT[category]
                if candidate.name == tool_name
            ),
            None,
        )
        if tool is None:
            raise RuntimeError(f"Assigned layout is unavailable: {tool_name}")
        source = job["source_slide"]
        content = str(job.get("content") or "")
        design = str(job["plan"].get("visual_layout_request") or "")
        human_prompt = build_generator_human_prompt(
            deck_style_contract=style_json,
            slide_topic=str(job["plan"].get("slide_topic") or ""),
            slide_plan=json.dumps(job["plan"], ensure_ascii=False, indent=2),
            design_instruction=design,
            slide_content=content,
            assigned_tool_name=tool_name,
            slide_index=int(job["index"]),
            deck_length=len(jobs),
        )
        prompt = tokenizer.apply_chat_template(
            [
                {"role": "system", "content": QWEN_GENERATOR_SYSTEM_PROMPT},
                {"role": "user", "content": human_prompt},
            ],
            tools=[format_tool_for_qwen(tool)],
            tokenize=False,
            add_generation_prompt=True,
        )
        samples.append(
            {
                "prompt": prompt,
                "assigned_tool_name": tool_name,
                "source_content": content,
                "deck_style": deck_style,
                "source_doc_id": str(source.get("source_doc_id", "")),
                "slide_index": int(source.get("slide_index", job["index"])),
            }
        )
    return samples


def _split_documents(documents: list[list[dict]]) -> tuple[list, list]:
    if len(documents) <= EVAL_DOCS:
        raise ValueError(
            f"Corpus has {len(documents)} documents but GRPO_EVAL_DOCS={EVAL_DOCS}"
        )
    shuffled = list(documents)
    random.Random(DATA_SEED).shuffle(shuffled)
    eval_documents = shuffled[:EVAL_DOCS]
    return shuffled[EVAL_DOCS:], eval_documents


def _load_model():
    device = "cuda" if torch.cuda.is_available() and not USE_CPU else "cpu"
    if device == "cuda" and torch.cuda.is_bf16_supported():
        dtype = torch.bfloat16
    elif device == "cuda":
        dtype = torch.float16
    else:
        dtype = torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
    )
    model = get_peft_model(model, _lora_config())
    if USE_GRAD_CHECKPOINT and device == "cuda":
        model.gradient_checkpointing_enable()
    model.config.use_cache = False
    if device == "cuda":
        model = model.to(device)
    setup_tokenizer(tokenizer, QWEN_CHAT_TEMPLATE)
    return model, tokenizer, device, dtype


def main() -> None:
    _validate_config()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log_dir = PROJECT_ROOT / "rl" / "log" / "grpo" / f"run_{run_id}"
    run_log_dir.mkdir(parents=True, exist_ok=True)
    run_log_path = start_run_logging(run_log_dir)
    if RUN_PREFLIGHT:
        print("Running reward infrastructure preflight...")
        preflight_reward_runtime()

    print(f"Loading base model for direct GRPO: {MODEL_ID}")
    model, tokenizer, device, dtype = _load_model()

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

    corpus_path = os.getenv("GRPO_OFFLINE_DATASET") or str(DEFAULT_DATASET_PATH)
    documents = load_offline_documents(corpus_path)
    train_documents, eval_documents = _split_documents(documents)
    print(
        f"Preparing {len(train_documents)} train docs and "
        f"{len(eval_documents)} held-out eval docs..."
    )
    train_rows = [
        sample
        for document in train_documents
        for sample in _prepare_document(document, tokenizer, tool_retriever)
    ]
    eval_rows = [
        sample
        for document in eval_documents
        for sample in _prepare_document(document, tokenizer, tool_retriever)
    ]
    if not train_rows or not eval_rows:
        raise RuntimeError("Prepared GRPO train/eval data is empty")

    snapshots = OUTPUT_DIR / "dataset_snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    write_json(snapshots / "train.json", train_rows)
    write_json(snapshots / "eval.json", eval_rows)
    train_dataset = Dataset.from_list(train_rows)
    eval_dataset = Dataset.from_list(eval_rows)

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
        temperature=float(os.getenv("GRPO_TEMPERATURE", "0.9")),
        top_p=float(os.getenv("GRPO_TOP_P", "0.95")),
        beta=float(os.getenv("GRPO_BETA", "0.0")),
        epsilon=float(os.getenv("GRPO_EPSILON", "0.2")),
        epsilon_high=float(os.getenv("GRPO_EPSILON_HIGH", "0.28")),
        mask_truncated_completions=True,
        loss_type=os.getenv("GRPO_LOSS_TYPE", "dapo"),
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

    baseline = HistoricalRewardBaseline(
        decay=float(os.getenv("GRPO_BASELINE_DECAY", "0.99")),
        sigma_floor=float(os.getenv("GRPO_BASELINE_SIGMA_FLOOR", "0.05")),
    )
    trainer = HistoricalBaselineGRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=[slidegen_composite_reward],
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset if eval_enabled else None,
    )
    trainer.historical_baseline = baseline
    checkpoint = _latest_checkpoint()

    manifest = get_runtime_metadata(
        {
            "run_name": "direct_grpo",
            "run_id": run_id,
            "model_id": MODEL_ID,
            "output_dir": str(OUTPUT_DIR),
            "resume_checkpoint": str(checkpoint) if checkpoint else None,
            "total_steps": TOTAL_STEPS,
            "train_documents": len(train_documents),
            "eval_documents": len(eval_documents),
            "train_prompts": len(train_rows),
            "eval_prompts": len(eval_rows),
            "num_generations": NUM_GENERATIONS,
            "generation_batch_size": GENERATION_BATCH_SIZE,
            "gradient_accumulation_steps": GRAD_ACCUMULATION,
            "max_completion_length": MAX_COMPLETION_LENGTH,
            "loss_type": training_args.loss_type,
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


if __name__ == "__main__":
    main()
