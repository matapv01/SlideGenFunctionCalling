# Direct GRPO Training

SlideGen trains the XML tool-calling policy directly with TRL GRPO and PEFT
LoRA. There is no SDFT stage and training makes no remote Gemini/LLM/search API
calls; retrieval and reward embeddings use the configured local model. The old
`sft_function_call_dataset.json` remains only as the offline evaluator's default
gold set; `train.py` does not train from it.

Tài liệu thiết kế, rollout plan, reward plan và checklist vận hành chi tiết:
[GRPO_TRAINING_PLAN.md](GRPO_TRAINING_PLAN.md).

Sơ đồ luồng GRPO và phần giải thích vai trò từng file:
[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md).

## Pipeline

1. Load the rebuilt offline corpus once and split it by document into train and
   held-out evaluation sets.
2. Reuse production image/no-image filtering and deck-wide layout assignment.
3. Give each sample exactly one assigned XML tool and the same deck-style,
   planning, and content contract used by production.
4. Generate bounded rollout batches, execute each valid XML call once, render
   all valid samples concurrently in one Chromium process, and score ViT in one
   batch.
5. Train with DAPO, normalize rollout losses across an optimizer update, and
   periodically evaluate/save full Trainer checkpoints.

The composite reward validates the assigned tool and uses the Qwen native tool-call format and declared schema as a hard gate. Valid completions receive a
weighted sum of bounded [0, 1] signals: lexical coverage, multilingual semantic
similarity, numeric-fact preservation, normalized DOM layout, image-load status,
and ViT aesthetics. Text overflow, slide-boundary violations, and textbox collisions zero the DOM component. Literal numeric tokens are excluded from the lexical and
semantic inputs so number fidelity is measured only by `numeric_fact`. Each signal contributes once through an explicit
weighted sum. If no image is expected, image loading is neutral (1.0); a missing
expected image lowers only the image component. Production deck style is applied
before approved assets are injected and XML is rendered.

## Run on the H100 host

A Git checkout alone does not contain the complete training inputs. Before renting
GPU time for the training run, prepare and transfer the rebuilt corpus plus these
artifacts, preserving their paths relative to the repository:

- `rl/data/grpo_replanned_dataset.json` (or set `GRPO_OFFLINE_DATASET`).
- `static/output/grpo_image_cache/`, including all assets referenced by the corpus.
- `models/vit/best_model_pairwise.pt` (or set `REWARD_MODEL_PATH`).
- The Qwen3-8B base checkpoint, available locally or through the configured model ID.

ViT is a frozen reward model only: its parameters have gradients disabled and
scoring runs in inference mode. Only Qwen3-8B LoRA adapters are updated.
Do not transfer ViT training datasets, notebooks, or all experiment outputs:
only the compatible trained `best.pt` checkpoint is needed.

For the default paths, bundle the inputs without credentials or unrelated files:

    tar -czf /tmp/grpo-inputs.tar.gz rl/data/grpo_replanned_dataset.json static/output/grpo_image_cache models/vit/best_model_pairwise.pt
    (cd /tmp && sha256sum grpo-inputs.tar.gz > grpo-inputs.tar.gz.sha256)

Transfer both files to `/tmp` on H100, verify with
`(cd /tmp && sha256sum -c grpo-inputs.tar.gz.sha256)`, then inspect with
`tar -tzf /tmp/grpo-inputs.tar.gz` and extract into the fresh repository root
using `tar -xzf /tmp/grpo-inputs.tar.gz`.
For custom dataset/cache/checkpoint paths, adapt the file list; do not archive
the repository root or `.env`. The policy and local embedding model/cache are
separate prerequisites; preflight loads the configured embedding model.

On a fresh checkout, install the locked Python environment and build the FE:

    uv sync --locked
    uv pip check
    uv run --locked python -m playwright install --with-deps chromium
    cd frontend
    npm ci
    npm run build
    cd ..

Start the backend in a separate terminal after building the FE:

    uv run --locked uvicorn backend.api.app:app --host 127.0.0.1 --port 12008

The backend serves the built preview used by the reward renderer. `frontend/dist/`
and `static/` are ignored by Git, so build/copy them on the target host. An unset
`PLAYWRIGHT_CHROMIUM_EXECUTABLE` uses Playwright's installed Chromium; do not copy
a system Chrome path from another machine unless that executable exists there.
Use a dedicated environment: unrelated manually installed OCR packages can cause
`uv pip check` conflicts, and an unsupported extra `chardet` can produce a
Requests warning even when the project lockfile is consistent.

Before loading policy weights, validate the complete corpus and runtime:

    uv run --locked python rl/train.py --preflight-only

This uses the same preparation, split, RAG, context-budget, resume-contract and
renderer/ViT checks as training, but does not load Qwen weights or create an
optimizer. It always runs reward preflight, even if `GRPO_PREFLIGHT=false`.
A successful run writes `rl/log/grpo/run_*/preflight.json`; failures exit nonzero.
It creates logs and may populate the retriever/model cache.

To run this check on a machine without CUDA, use
`USE_CPU=true GRPO_OUTPUT_DIR=/tmp/grpo-cpu-preflight GRPO_RESUME=false uv run --locked python rl/train.py --preflight-only`.
CPU preflight does not certify H100 memory usage or checkpoint compatibility
with a different GPU training configuration. Run it again on the target host
with the actual training settings.

Point TRAINING_MODEL_ID to the model available on that host, then run:

    export TRAINING_MODEL_ID=/path/to/local/base-model
    export GRPO_OUTPUT_DIR=/data/checkpoints/slidegen-grpo/smoke_1
    export TOTAL_STEPS=1
    export GRPO_SAVE_STEPS=1
    export GRPO_EVAL_STEPS=0
    export GRPO_RESUME=false
    uv run --locked python rl/train.py

This runs one optimizer step as an infrastructure smoke test. Run the 10-step and 50-step pilots in
`GRPO_TRAINING_PLAN.md` before starting a 500-step job.

Choose an unused output directory for a fresh run. When restarting an interrupted
run, use that exact directory and set `GRPO_RESUME=true` with the same model,
dataset, and training configuration.

The GRPO corpus is rebuilt from the slide text in the existing JSON.
This reruns the production deck planner, image search, Qwen-VL verification,
and image-aware layout refinement. GRPO reads the exact source slide text for
both its prompt and reward, even if an older corpus contains rewritten text.
When no image is approved, the phase-one layout brief is retained and the slide
uses a no-image layout. Empty search results are valid no-image outcomes.
Verified image files are stored under `static/output/grpo_image_cache/`. Planner
and vision model names/base URLs come from `backend/config.py`: `LLM_MODEL` /
`LLM_BASE_URL` and `VLM_MODEL` / `VLM_BASE_URL`. Change those config values for a
different deployment; keep provider credentials only in `.env` (`LLM_API_KEY`,
and `VLM_API_KEY` only when the vision provider has a separate credential). The
default BE config points both roles at the same Qwen endpoint.

Smoke-check two slides into a separate file, then build the full corpus:

    uv run --locked python scripts/rebuild_grpo_corpus.py --max-docs 1 --max-slides 2 --output /tmp/grpo_replanned_smoke.json
    uv run --locked python scripts/rebuild_grpo_corpus.py
    export GRPO_OFFLINE_DATASET=rl/data/grpo_replanned_dataset.json

Image search is enabled by default. Use `--no-allow-external-search` for an
explicit no-search rebuild; `--allow-external-search` remains supported.
The resume manifest checks the search setting: use a new output path when
changing that setting, or retain the original setting to resume an older build.
Search sends short queries derived from slide text to DuckDuckGo. Copy the rebuilt
JSON corpus and `static/output/grpo_image_cache/` to the H100 host at the same
paths. `TRAINING_MODEL_ID=Qwen/Qwen3-8B` remains the text model that learns to
emit the function calls; `VLM_MODEL` must be vision-capable and is
used only while rebuilding the corpus.

TRAINING_GPU is optional. If unset, the script selects the GPU with the most
free memory. Set it explicitly only when the host exposes multiple GPUs.

Important defaults:

| Variable | Default | Meaning |
|---|---:|---|
| GRPO_IMAGE_CACHE_DIR | static/output/grpo_image_cache | Locally cached images approved by Qwen-VL |
| GRPO_OFFLINE_DATASET | rl/data/grpo_replanned_dataset.json | Rebuilt corpus used directly for training |
| GRPO_REQUIRE_IMAGE_ASSETS | true | Fail fast unless both train and eval have image-backed prompts |
| TRAINING_MODEL_ID | Qwen/Qwen3-8B | Base model ID/path; use the matching 8B checkpoint on H100 |
| TRAINING_MODEL_REVISION | unset | Optional immutable Hub revision; local model files are fingerprinted |
| GRPO_OUTPUT_DIR | ./qwen3_8b_slidegen_grpo | Isolated 8B checkpoints and final adapter |
| GRPO_FAISS_INDEX_PATH | GRPO_OUTPUT_DIR/tool_retriever_index | RL-only FAISS cache |
| GRPO_RESUME | true | Resume latest complete checkpoint only if its training contract matches |
| TOTAL_STEPS | 500 | Optimizer updates |
| NUM_GENERATIONS | 4 | Completions per prompt |
| GRPO_GENERATION_BATCH_SIZE | 4 | Completions per rollout window (one prompt × 4 generations) |
| GRADIENT_ACCUMULATION_STEPS | 16 | Micro-batches per optimizer update |
| GRPO_TOP_K | 20 | Qwen3 sampling cutoff in non-thinking mode |
| MAX_COMPLETION_LENGTH | 3072 | Maximum completion tokens; chosen from the Qwen3 reference-call length audit |
| GRPO_SAVE_STEPS | 25 | Full checkpoint interval |
| GRPO_EVAL_STEPS | 50 | Held-out evaluation interval; 0 disables it |
| GRPO_EVAL_DOCS | 5 | Documents reserved for evaluation |
| RL_REWARD_RENDER_WORKERS | 4 | Concurrent isolated pages in one persistent browser |
| RL_RENDER_TIMEOUT_SECONDS | 60 | Per-sample render timeout, excluding queue wait |
| RL_SOURCE_EMBEDDING_CACHE_SIZE | 4096 | Maximum cached source chunks; 0 disables retention |
| REWARD_MODEL_PATH | models/vit/best_model_pairwise.pt | ViT-Base pairwise checkpoint |
| RL_PAIRWISE_CENTER | 0 | Fixed utility center |
| RL_PAIRWISE_TEMPERATURE | 1 | Positive fixed sigmoid temperature |
| RL_VIT_BATCH_SIZE | 4 | Maximum screenshots per ViT forward |
| PLAYWRIGHT_CHROMIUM_EXECUTABLE | unset; Playwright Chromium | Optional existing browser executable override |
| BROWSER_PREVIEW_URL (backend/config.py) | Local XML preview route | Frontend endpoint used by Playwright; not an environment override |

An audit of the 414 source tool calls with the Qwen3 tokenizer found p95=1,136
tokens and max=2,419; a 512-token cap would truncate 92 examples (22.2%).
The 3,072 default covers the longest reference with margin. The longest
prepared prompt (4,389) plus this completion budget uses 7,461 of Qwen3-8B's
40,960-token context. Generated rollout lengths can differ, so monitor
`completions/clipped_ratio` during the H100 pilot.

Planner model/URL and vision model/URL are configuration constants in
`backend/config.py`, not `.env` variables. Only API credentials belong in `.env`.

Before loading the 8B model, startup prepares the corpus/layouts, checks prompt
length plus the completion budget against the model context, and validates the
resume contract. Preflight then checks strict pairwise ViT loading and a finite bounded score
on an actual frontend screenshot. Every distinct approved image is decoded locally
and checked through `BROWSER_PREVIEW_URL`; an unrelated loaded image cannot satisfy
this check. The FE preview, browser, retriever, and reward model must be available.
No interactive browser window is needed: Chromium runs headlessly.

Image layouts must have exactly as many image slots as approved assets. GRPO
fails before training if no compatible layout exists; fix/rebuild the affected
slide instead of silently discarding its images. The production BE still has an
explicit no-image fallback. Rebuilt-corpus resume manifests now use version 3;
use a new rebuild output when an older manifest is rejected.

One browser is reused across reward batches, with separate pages for samples.
Source embeddings are deduplicated and cached with a bounded LRU cache. Metrics
`reward_time/render_seconds`, `reward_time/vit_seconds`, and
`reward_time/semantic_seconds` expose reward-stage timings. Batch size and completion
length still require a measured smoke run on the target H100.

Qwen3 uses its native tokenizer template with `enable_thinking=False`. The
pairwise aesthetic reward is sigmoid of centered, temperature-scaled utility;
higher utility means preferred. Content similarity and overflow/collision are computed from the
rendered frontend text and DOM. Source number/context records are extracted once
while preparing each training sample. `reward_component/numeric_fact` reports the
heuristic number-to-context score; it is an independent component, not multiplied
into lexical/semantic scores and not subtracted again as a second penalty. DOM
layout issues and expected-image loading also contribute once each. No-image
samples receive a neutral image-loading score.

The aesthetic component uses a trained local pairwise ViT-Base checkpoint.
Its score mapping and the coefficients combining reward components are
uncalibrated baselines. Numeric attribution is also a
heuristic based on local context and direction cues, not a general entailment or
factuality model; it can miss negation, causal reversal, equivalent units, and
numbers written as words. Validate reward ranking and component distributions on a
labeled held-out set before a long H100 run; unit tests establish code invariants,
not reward quality.

`GRPO_GENERATION_BATCH_SIZE=4` is four completions for one prompt, not four
prompts. TRL splits that prompt group over four microsteps; with accumulation 16,
one full optimizer update sees four prompt groups (16 completions). Token-normalized
losses (`dapo`, `cispo`, `vespo`) are averaged over the actual optimizer window:
full windows divide by `gradient_accumulation_steps / steps_per_generation`; a
shorter final update uses its actual factor only when it contains whole generation
windows. A partial generation window fails fast. The nominal factor is recorded
in each checkpoint and run manifest.

Semantic reward token-chunks both source content and frontend-rendered text before
embedding, then combines source coverage and generated-text precision. This avoids
silently ignoring content after the embedder's context limit and penalizes
unsupported extra text. Standalone numeric literals are masked from lexical and
semantic inputs; numeric_fact independently checks number preservation and
limited number-to-context attribution. It is a heuristic, not an entailment judge:
general factual paraphrases, equivalent units, negation/causal reversal, and
numbers written as words are not reliably resolved. ViT remains an aesthetic/error
signal, not a full judge of content correctness or image relevance.

## Pairwise reward and pilot tuning

The frozen ViT-Base/16 was trained with Bradley–Terry preferences: higher utility
means preferred. The loader supports the notebook's raw state_dict and a
model_state_dict wrapper, loaded strictly without a pretrained Hub download.
Inference matches RGB, resize 224×224 and ImageNet normalization from the notebook.

Aesthetic = sigmoid((logit - center) / temperature). RL_PAIRWISE_CENTER=0 and
RL_PAIRWISE_TEMPERATURE=1 are uncalibrated defaults. Pairwise training does not
identify the absolute origin of utility; this is not a probability of quality.
Choose fixed center/temperature using a separate calibration set of policy-like
screenshots, then freeze them. Never normalize per rollout batch. Changes affect
the resume contract and require a fresh run.

RL_VIT_BATCH_SIZE=4 bounds each forward while preserving score order.
REWARD_MODEL_DEVICE=cpu conserves policy VRAM. On H100, profile CPU versus cuda
with actual rollouts; use cuda if ViT time is a bottleneck and memory permits.
ViT stays FP32, frozen, eval-only, with inference_mode.

Monitor reward_pairwise/{raw_mean,raw_std,raw_min,raw_max,score_std,saturated_fraction}
and reward_time/vit_seconds. Saturation counts valid scores below 0.01 or above
0.99. Inspect examples before adjusting calibration; saturation can flatten useful
group differences. Keep content/numeric/DOM/image rewards because preference alone
does not establish correctness.

Start the pilot at LR=1e-6, 4 generations, 3072 completion tokens and existing
component weights. Measure throughput, peak VRAM, invalid fraction, clipped_ratio,
frac_reward_zero_std and held-out components before tuning. Use fresh directories
for smoke 1, pilot 10, calibration 50 and full 500. Reward growth alone does not
show slide quality improved; inspect held-out rankings and rendered samples.

The notebook records 189/193 validation pairs correct (97.93%), using that same
validation set for checkpoint selection. This is not an independent rollout
evaluation. Its slide-ID split construction cell is commented out and training
reads prebuilt CSVs; audit those CSVs for leakage and keep a separate final test
set. The former five-label checkpoint is incompatible with this pairwise loader.

For a fresh H100 infrastructure smoke after preflight (one optimizer update):

    OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 REWARD_MODEL_DEVICE=cuda \
    RL_PAIRWISE_CENTER=0 RL_PAIRWISE_TEMPERATURE=1 RL_VIT_BATCH_SIZE=4 \
    GRPO_OUTPUT_DIR=/data/checkpoints/slidegen-grpo/pairwise_smoke_01 \
    GRPO_RESUME=false TOTAL_STEPS=1 GRPO_SAVE_STEPS=1 GRPO_EVAL_STEPS=0 \
    uv run --locked python rl/train.py

Repeat with the exact same settings and GRPO_RESUME=true to verify full state
resume. These calibration defaults are suitable for infrastructure checks;
select calibration on representative held-out screenshots before a long run.

## Training logs

Every run writes live artifacts under `rl/log/grpo/run_<timestamp>/`:

- `run.log` captures stdout/stderr.
- `training_metrics.jsonl` appends one structured JSON record per optimizer update, epoch summary, evaluation, checkpoint, and run start/end.
- `training_readable.log` records the same events as readable lines.
- `manifest.json` stores model, GPU, code revision, dataset, hyperparameters, and log paths.
- `metrics.json` and `metrics_trend.png` summarize Trainer history after the run.

Each update includes epoch/global step, learning rate, loss, gradient norm, token/completion lengths, clipping, total and component rewards, pairwise ViT utility/score distribution, saturation, entropy, reward timings, and all Trainer metrics available at that step. Epoch averages are written at epoch boundaries, with a partial-epoch summary at the end. The JSONL and readable files flush after each event so they remain useful if a job stops early.

## Checkpoints and resume

Checkpoints are stored under GRPO_OUTPUT_DIR/checkpoint-*. A resumable
checkpoint must contain LoRA/model weights, optimizer.pt, scheduler.pt,
trainer_state.json, and `rl_checkpoint_metadata.json`. Metadata must match the
configured base model, loss type, accumulation factor and training-contract hash.
The contract fingerprints corpus/prepared rows, cached assets, local base-model
weights or resolved Hub revision, reward/ViT settings, renderer config and code,
lockfiles, LoRA/training settings and runtime package versions. A
canonical copy is logged as `training_contract.json`. The latest complete checkpoint
is rejected if incompatible; training does not silently restart or select an older
compatible run. Old checkpoints without a contract require a new output directory.
For a local base-model directory, config/tokenizer files and recognized weight
shards are hashed; Hub models use their resolved revision. `GRPO_RESUME=false`
also requires an unused checkpoint output directory.

Resume preserves Adam moments, learning-rate schedule, Trainer/RNG state, and
global step. There is no historical EMA advantage fallback; zero-variance groups
keep the standard GRPO group-relative advantage. The completed LoRA adapter is
written to GRPO_OUTPUT_DIR/final_adapter.

## OOM tuning

Keep NUM_GENERATIONS at least 2 and keep GRPO_GENERATION_BATCH_SIZE divisible by
it. Reduce generation batch first. If OOM persists, lower completion length to
2,048 and monitor the clipped ratio; 3 of the 414 reference calls exceed 2,048:

    NUM_GENERATIONS=2 \
    GRPO_GENERATION_BATCH_SIZE=2 \
    MAX_COMPLETION_LENGTH=2048 \
    uv run python rl/train.py

## Verification

    uv run pytest -q rl/test_grpo_pipeline.py rl/test_grpo_runtime.py rl/test_eval_tooluse.py rl/test_pairwise_reward.py

Key files:

- rl/train.py: direct GRPO entrypoint
- rl/grpo_trainer.py: DAPO accumulation normalization and model-aware checkpoint metadata
- rl/train_data.py: production-compatible corpus normalization, layout, prompts, and document split
- rl/training_contract.py: data/model/code/runtime fingerprint for safe checkpoint resume
- rl/slidegen_adapter.py: Qwen prompt setup and production frontend batch renderer
- rl/rewards/content_reward.py: lexical, semantic, and numeric-fact metrics
- rl/rewards/composite_reward.py: strict tool/schema checks, rendered-text reward, and component metrics
- scripts/generate_challenge_dataset.py: deterministic offline corpus loader
