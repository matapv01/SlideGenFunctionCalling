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

### Overview

```
for step in range(TOTAL_STEPS):
    ┌──────────────────────────────────────────────────────┐
    │ 1. GEN DOC + CHUNK (Gemini, 1 call/batch)           │
    │    Gen bài viết dài (600-1500 từ) + chunk luôn       │
    │    Gemini tự quyết số chunk → 6-15 slides/doc        │
    │    Lưu vào rl/data/step_{step}_docs.json             │
    │                                                      │
    │ 2. PLAN + PREPARE (Gemini, từng slide)               │
    │    Planner → action (từ heading + content)           │
    │    Preparer → design_instruction                     │
    │                                                      │
    │ 3. ROLLOUT (Qwen, song song theo doc)                │
    │    Doc 1: s0→s1→s2→...  (sequential trong doc)      │
    │    Doc 2: s0→s1→s2→...  (song song)                 │
    │    Doc M: ...                                        │
    │                                                      │
    │    Mỗi slide:                                        │
    │      - Qwen gen completion → tool_call               │
    │      - sanitize_to_placeholders("Aa" token)          │
    │      - execute → render → DINOv2 embedding           │
    │      → prev_embedding cho slide kế                   │
    │                                                      │
    │ 4. GRPO UPDATE                                       │
    │    Collect all prompts → Dataset                      │
    │    GRPOTrainer → K completions/prompt                 │
    │    → reward → advantage → policy update               │
    │    Lưu dataset vào rl/data/step_{step}_dataset.json   │
    └──────────────────────────────────────────────────────┘
```

### Sequential trong doc

```
  prev_embedding = [0]*768
  for slide in doc:                              # tuần tự
    heading = slide["heading"]
    action = Planner(slide_number, heading, content)
    design = Preparer(slide, action, prev_tool_call)
    prompt = build(slide, design, tools)
    completion = qwen.generate(prompt)
    tool_call = parse_json(completion)
    sanitized = sanitize_to_placeholders(tool_call)  # "Aa" token
    html = execute_tool(sanitized)
    render(html, path)
    prev_embedding = DINOv2(path)                # cho slide sau
    prev_tool_call = tool_call
```

### sanitize_to_placeholders

Thay toàn bộ text content bằng cùng 1 token `"Aa"`, giữ nguyên cấu trúc (list length, dict keys, nesting). Embedding chỉ capture khác biệt về layout/cấu trúc, không bị ảnh hưởng bởi content text.

### Song song giữa các doc

```python
with ThreadPoolExecutor(max_workers=batch_docs) as ex:
    futures = [ex.submit(process_doc, doc, step_id) for doc, step_id in ...]
    all_prompts = [r for f in futures for r in f.result()]

trainer = GRPOTrainer(model, dataset=Dataset.from_list(all_prompts), ...)
trainer.train()
```

---

## Prompt Format

```python
messages = [
    {"role": "system", "content": QWEN_GENERATOR_SYSTEM_PROMPT + tools},
    {"role": "user", "content": QWEN_GENERATOR_HUMAN_TEMPLATE.format(
        style_context=style_context_str,
        design_instruction=design_instruction,
        slide_content=slide_content,
    )},
]
prompt = tokenizer.apply_chat_template(messages, tools=tools,
                                         tokenize=False, add_generation_prompt=True)
```

---

## Reward Functions

| Reward | Implementation | Input | Description |
|--------|---------------|-------|-------------|
| **Aesthetic** | `ViTAestheticProvider` | rendered PNG | Score 0.0–1.0 |
| **Consistency** | `DINOv2EmbeddingProvider` | prev_embedding, current_embedding | Cosine similarity (sanitized) |
| **Content** | Rule-based | completion text, slide content | Keyword overlap + length penalty |

---

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
│   └── generate_challenge_dataset.py  # Gemini gen doc + chunk
└── rl/
    ├── README.md
    ├── train.py            # GRPO training (on-policy sequential)
    ├── rewards/
    │   ├── aesthetic_reward.py
    │   ├── consistency_reward.py
    │   └── content_reward.py
    ├── data/               # step docs + dataset snapshots
    └── qwen_slidegen_grpo/ # LoRA adapters
```
