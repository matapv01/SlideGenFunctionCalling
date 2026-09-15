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
- **Qwen path**: system prompt = `QWEN_GENERATOR_SYSTEM_PROMPT` + tools via `format_tool_for_qwen()`. Human prompt = `QWEN_GENERATOR_HUMAN_TEMPLATE`. Tools are passed in the tool-calling format.
- **Gemini path**: per-slide-type system prompt (from Preparer) + tool binding via LangChain.

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

## Directory Structure

```
.
├── ARCHITECTURE.md
├── README.md
├── backend/
│   ├── domain/ports/
│   ├── infrastructure/
│   │   ├── capture/playwright_provider.py
│   │   ├── embedding/                 # Local sentence-transformer embeddings
│   │   └── aesthetic/vit_aesthetic_provider.py
│   └── workflows/slidegen_workflow/
│       ├── nodes/          # slide_planner, slide_preparer, slide_generator
│       ├── tools/           # tool_des.py (TOOLS_DICT, execute_tool)
│       └── utils/
│           ├── prompts.py  # tất cả prompt templates
│           └── helper.py   # sanitize, render, format_tool
└── scripts/                # Development and deployment utilities
```
