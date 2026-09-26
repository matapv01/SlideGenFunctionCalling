# Direct GRPO Training

SlideGen trains the XML tool-calling policy directly with TRL GRPO and PEFT
LoRA. There is no SDFT stage and no Gemini/API dependency in training.

Tài liệu thiết kế, rollout plan, reward plan và checklist vận hành chi tiết:
[GRPO_TRAINING_PLAN.md](GRPO_TRAINING_PLAN.md).

## Pipeline

1. Load the tracked offline corpus once and split it by document into train and
   held-out evaluation sets.
2. Reuse production image/no-image filtering and deck-wide layout assignment.
3. Give each sample exactly one assigned XML tool and the same deck-style,
   planning, and content contract used by production.
4. Generate bounded rollout batches, execute each valid XML call once, render
   all valid samples concurrently in one Chromium process, and score ViT in one
   batch.
5. Train with DAPO, normalize rollout losses across an optimizer update, and
   periodically evaluate/save full Trainer checkpoints.

The composite reward validates the assigned tool, then combines validity,
content overlap, multilingual semantic similarity, exact serialization, XML
overflow/collision, approved-image loading, and ViT aesthetics. Production deck
style is applied before approved assets are injected and XML is rendered.

## Run on the H100 host

Point TRAINING_MODEL_ID to the model available on that host, then run:

    TRAINING_MODEL_ID=/path/to/local/base-model \
    GRPO_OUTPUT_DIR=/data/checkpoints/slidegen-grpo/full_500_run01 \
    GRPO_RESUME=false \
    uv run --locked python rl/train.py

Choose an unused output directory for a fresh run. When restarting an interrupted
run, use that exact directory and set `GRPO_RESUME=true` with the same model,
dataset, and training configuration.

The GRPO corpus is rebuilt from the slide text in the existing JSON.
This reruns the production deck planner, image search, Qwen-VL verification,
phase-two refinement, and then stores verified images under
`static/output/grpo_image_cache/`. Start both planner and vision endpoints:

    export GRPO_REBUILD_PLANNER_BASE_URL=http://127.0.0.1:8080/v1
    export GRPO_IMAGE_VLM_BASE_URL=http://127.0.0.1:8080/v1
    export GRPO_IMAGE_VLM_MODEL=<vision-capable-model>

Smoke-check two slides into a separate file, then build the full corpus:

    uv run --locked python scripts/rebuild_grpo_corpus.py --max-docs 1 --max-slides 2 --output /tmp/grpo_replanned_smoke.json --allow-external-search
    uv run --locked python scripts/rebuild_grpo_corpus.py --allow-external-search
    export GRPO_OFFLINE_DATASET=rl/data/grpo_replanned_dataset.json

Search sends short queries derived from slide text to DuckDuckGo. Copy the rebuilt
JSON corpus and `static/output/grpo_image_cache/` to the H100 host at the same
paths. `TRAINING_MODEL_ID=Qwen/Qwen3-8B` remains the text model that learns to
emit the function calls; `GRPO_IMAGE_VLM_MODEL` must be vision-capable and is
used only while rebuilding the corpus.

TRAINING_GPU is optional. If unset, the script selects the GPU with the most
free memory. Set it explicitly only when the host exposes multiple GPUs.

Important defaults:

| Variable | Default | Meaning |
|---|---:|---|
| GRPO_REBUILD_PLANNER_BASE_URL | backend `LLM_BASE_URL` | Endpoint for fresh deck/slide planning and image-aware refinement |
| GRPO_IMAGE_VLM_BASE_URL | backend `VLM_BASE_URL` | OpenAI-compatible vision endpoint used during corpus rebuilding |
| GRPO_IMAGE_VLM_MODEL | backend `VLM_MODEL` | Vision-capable model used to approve and describe images |
| GRPO_IMAGE_CACHE_DIR | static/output/grpo_image_cache | Locally cached images approved by Qwen-VL |
| GRPO_OFFLINE_DATASET | rl/data/sft_function_call_dataset.json | Corpus path; point it to `grpo_replanned_dataset.json` after rebuilding |
| GRPO_REQUIRE_IMAGE_ASSETS | true | Fail fast unless both train and eval have image-backed prompts |
| TRAINING_MODEL_ID | Qwen/Qwen3-8B | Base model ID/path; use the matching 8B checkpoint on H100 |
| GRPO_OUTPUT_DIR | ./qwen3_8b_slidegen_grpo | Isolated 8B checkpoints and final adapter |
| GRPO_FAISS_INDEX_PATH | GRPO_OUTPUT_DIR/tool_retriever_index | RL-only FAISS cache |
| GRPO_RESUME | true | Resume latest compatible full checkpoint |
| TOTAL_STEPS | 500 | Optimizer updates |
| NUM_GENERATIONS | 4 | Completions per prompt |
| GRPO_GENERATION_BATCH_SIZE | 4 | Completions per rollout window (one prompt × 4 generations) |
| GRADIENT_ACCUMULATION_STEPS | 16 | Micro-batches per optimizer update |
| GRPO_TOP_K | 20 | Qwen3 sampling cutoff in non-thinking mode |
| MAX_COMPLETION_LENGTH | 512 | Maximum completion tokens |
| GRPO_SAVE_STEPS | 25 | Full checkpoint interval |
| GRPO_EVAL_STEPS | 50 | Held-out evaluation interval; 0 disables it |
| GRPO_EVAL_DOCS | 5 | Documents reserved for evaluation |
| RL_REWARD_RENDER_WORKERS | 4 | Concurrent pages in the shared browser |
| REWARD_MODEL_PATH | ViT small checkpoint | Aesthetic reward checkpoint |
| PLAYWRIGHT_CHROMIUM_EXECUTABLE | system Chrome | Optional browser override |
| BROWSER_PREVIEW_URL | Local XML preview route | Frontend endpoint used by Playwright |

At startup, preflight checks ViT label semantics, renders a sample through
`BROWSER_PREVIEW_URL` (the BE XML frontend route), and verifies a finite ViT
score on that screenshot. The frontend preview, browser, retriever, and reward
model must be available before training.

Qwen3 uses its native tokenizer template with `enable_thinking=False`. Since the
ViT labels `1=error`, the aesthetic reward is one minus the mean error
probability. Content similarity and overflow/collision are computed from the
rendered frontend text and DOM.

`GRPO_GENERATION_BATCH_SIZE=4` is four completions for one prompt, not four
prompts. TRL splits that prompt group over four microsteps; with accumulation 16,
one full optimizer update sees four prompt groups (16 completions). Token-normalized
losses (`dapo`, `cispo`, `vespo`) are averaged over the actual optimizer window:
full windows divide by `gradient_accumulation_steps / steps_per_generation`, while
a shorter final window uses its actual microstep count. The configured factor is
recorded in each checkpoint and run manifest.

Semantic reward token-chunks both source content and frontend-rendered text before
embedding, then combines source coverage and generated-text precision. This avoids
silently ignoring content after the embedder's context limit and penalizes
unsupported extra text.

## Checkpoints and resume

Checkpoints are stored under GRPO_OUTPUT_DIR/checkpoint-*. A resumable
checkpoint must contain LoRA/model weights, optimizer.pt, scheduler.pt,
trainer_state.json, and `rl_checkpoint_metadata.json`. Metadata must match the
configured base model, loss type, and accumulation factor, so incompatible or
pre-fix checkpoints are skipped instead of being loaded into the 8B run.

Resume preserves Adam moments, learning-rate schedule, Trainer/RNG state, and
global step. There is no historical EMA advantage fallback; zero-variance groups
keep the standard GRPO group-relative advantage. The completed LoRA adapter is
written to GRPO_OUTPUT_DIR/final_adapter.

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
- rl/grpo_trainer.py: DAPO accumulation normalization and model-aware checkpoint metadata
- rl/slidegen_adapter.py: Qwen prompt setup and production frontend batch renderer
- rl/rewards/composite_reward.py: strict tool/schema checks, rendered-text reward, and component metrics
- scripts/generate_challenge_dataset.py: deterministic offline corpus loader
