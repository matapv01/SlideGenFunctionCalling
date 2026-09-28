# SlideGen Architecture

## Inference Pipeline

```
User Input (Idea / Document)
    │
    ▼
[MANUAL WORKFLOW]    Structure → Intro/Transition/Content/Team/ThankYou
    │
    ▼
[SLIDE PLANNER]     Gemini → classify slide type
    │                (INTRO/TRANSITION/CONTENT/CHART/TEAM/THANK_YOU)
    ▼
[SLIDE PREPARER]    Gemini → design_instruction
    │                (theme, layout, formatting rules)
    ▼
[SLIDE GENERATOR]   Qwen → tool call JSON → HTML
    │
    ▼
[SLIDE EVALUATOR]   VLM → score + feedback (retry ×3)
    │
    ▼
[FINALIZE]          Save HTML + PNG
```

### Generator paths
- **Qwen path**: system prompt = `QWEN_GENERATOR_SYSTEM_PROMPT` + tools via `format_tool_for_qwen()`. Human prompt = `QWEN_GENERATOR_HUMAN_TEMPLATE`. Tools in system message (match training format).
- **Gemini path**: per-slide-type system prompt (from Preparer) + tool binding via LangChain.

---

## RL Training Pipeline

Đây là mô tả hiện hành của luồng GRPO trực tiếp; chi tiết thiết kế, loss,
reward, checkpoint và vai trò từng file nằm trong [rl/SYSTEM_OVERVIEW.md](rl/SYSTEM_OVERVIEW.md)
và [rl/GRPO_TRAINING_PLAN.md](rl/GRPO_TRAINING_PLAN.md).

```text
source slide corpus
  -> rebuild bằng production planning/image pipeline (chỉ ở bước chuẩn bị corpus)
  -> strict loader, split theo document và gán một tool tương thích mỗi slide
  -> Qwen3-8B + LoRA sinh nhiều rollout cho cùng prompt
  -> validate, execute XML, render frontend và tính composite reward
  -> scalar reward -> group-relative advantage / DAPO -> optimizer update
```

Training không sinh lại tài liệu theo từng step, không chạy tuần tự theo slide,
không dùng DINO consistency reward; việc gọi planner/VLM API chỉ thuộc bước
rebuild corpus. Entrypoint train và reward pipeline chạy trên dữ liệu/model local.

## Directory Structure

```
.
├── ARCHITECTURE.md
├── README.md
├── backend/
│   ├── domain/ports/
│   ├── infrastructure/
│   │   ├── capture/playwright_provider.py
│   │   ├── embedding/dinov2_provider.py
│   │   └── aesthetic/vit_aesthetic_provider.py
│   └── workflows/slidegen_workflow/
│       ├── nodes/          # slide_planner, slide_preparer, slide_generator
│       ├── tools/           # tool_des.py (TOOLS_DICT, execute_tool)
│       └── utils/
│           ├── prompts.py  # tất cả prompt templates
│           └── helper.py   # sanitize, render, format_tool
├── scripts/
│   ├── rebuild_grpo_corpus.py         # chuẩn bị corpus qua pipeline BE
│   └── generate_challenge_dataset.py  # strict offline corpus loader
└── rl/
    ├── README.md
    ├── SYSTEM_OVERVIEW.md
    ├── GRPO_TRAINING_PLAN.md
    ├── train.py            # Qwen3-8B direct GRPO + LoRA
    ├── grpo_trainer.py     # DAPO accumulation/checkpoint contract
    ├── slidegen_adapter.py # tool-call format, BE execute/render bridge
    ├── render_runtime.py
    ├── training_contract.py
    ├── rewards/
    │   ├── composite_reward.py
    │   ├── aesthetic_reward.py
    │   └── content_reward.py
```
