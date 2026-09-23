# Direct GRPO Training

SlideGen trains the XML tool-calling policy directly with TRL GRPO and PEFT
LoRA. There is no SDFT stage and no Gemini/API dependency in training.

## Pipeline

1. Load the tracked offline corpus once and split it by document into train and
   held-out evaluation sets.
2. Reuse the production backend no-image filtering and deck-wide layout
   assignment.
3. Give each sample exactly one assigned XML tool and the same deck-style,
   planning, and content contract used by production.
4. Generate bounded rollout batches, execute each valid XML call once, render
   all valid samples concurrently in one Chromium process, and score ViT in one
   batch.
5. Train with DAPO and periodically evaluate/save full Trainer checkpoints.

The composite reward validates the assigned tool, then combines validity,
content overlap, multilingual semantic similarity, exact serialization, XML
overflow/collision, and ViT aesthetics. Production deck style is applied before
XML execution and rendering.

## Run on the H100 host

Point TRAINING_MODEL_ID to the model available on that host, then run:

    TRAINING_MODEL_ID=/path/to/local/base-model \
    GRPO_RESUME=true \
    uv run python rl/train.py

TRAINING_GPU is optional. If unset, the script selects the GPU with the most
free memory. Set it explicitly only when the host exposes multiple GPUs.

Important defaults:

| Variable | Default | Meaning |
|---|---:|---|
| TRAINING_MODEL_ID | Qwen/Qwen3-4B-Instruct-2507 | Base model ID/path; override on H100 |
| GRPO_OUTPUT_DIR | ./qwen_slidegen_grpo | Full Trainer checkpoints and final adapter |
| GRPO_FAISS_INDEX_PATH | GRPO_OUTPUT_DIR/tool_retriever_index | RL-only FAISS cache |
| GRPO_RESUME | true | Resume latest compatible full checkpoint |
| TOTAL_STEPS | 500 | Optimizer updates |
| NUM_GENERATIONS | 4 | Completions per prompt |
| GRPO_GENERATION_BATCH_SIZE | 4 | Completions generated concurrently |
| GRADIENT_ACCUMULATION_STEPS | 16 | Micro-batches per optimizer update |
| MAX_COMPLETION_LENGTH | 512 | Maximum completion tokens |
| GRPO_SAVE_STEPS | 25 | Full checkpoint interval |
| GRPO_EVAL_STEPS | 50 | Held-out evaluation interval; 0 disables it |
| GRPO_EVAL_DOCS | 5 | Documents reserved for evaluation |
| RL_REWARD_RENDER_WORKERS | 4 | Concurrent pages in the shared browser |
| REWARD_MODEL_PATH | ViT small checkpoint | Aesthetic reward checkpoint |
| PLAYWRIGHT_CHROMIUM_EXECUTABLE | system Chrome | Optional browser override |

At startup, preflight loads the ViT checkpoint and launches Chromium. Retriever,
browser, or reward-model failures stop before training unless an explicit
fallback is enabled.

## Checkpoints and resume

Checkpoints are stored under GRPO_OUTPUT_DIR/checkpoint-*. A resumable
checkpoint must contain LoRA/model weights, optimizer.pt, scheduler.pt,
trainer_state.json, and historical_reward_baseline.json.

This preserves Adam moments, learning-rate schedule, Trainer/RNG state, global
step, and the EMA reward baseline. Legacy adapter-only checkpoints are
intentionally ignored. The completed LoRA adapter is written to
GRPO_OUTPUT_DIR/final_adapter.

## OOM tuning

Keep NUM_GENERATIONS at least 2 and keep GRPO_GENERATION_BATCH_SIZE divisible by
it. Reduce generation batch first, then completion length:

    NUM_GENERATIONS=2 \
    GRPO_GENERATION_BATCH_SIZE=2 \
    MAX_COMPLETION_LENGTH=384 \
    uv run python rl/train.py

## Verification

    uv run pytest -q rl/test_grpo_pipeline.py rl/test_eval_tooluse.py

Key files:

- rl/train.py: direct GRPO entrypoint
- rl/grpo_trainer.py: resumable historical-baseline fallback
- rl/slidegen_adapter.py: production-aligned prompt and batch renderer
- rl/rewards/composite_reward.py: single-pass reward
- scripts/generate_challenge_dataset.py: deterministic offline corpus loader
