# SlideGen Architecture

## Inference Pipeline

```
Chat request (+ optional DOCX)
    │
    ▼
[DOC PREPROCESSOR]   Scan explicit headings; preserve them. Infer only
                     unstructured regions and merge them into the tree.
    │
    ▼
[RAG CONTEXT]        SQLite conversation-scoped chunks + local embeddings
    │
    ▼
[SLIDE SCRIPT]       One LLM pass turns prompt + retrieved context into Markdown
    │
    ▼
[CANONICAL CHUNKS]   Normalize script into the shared slide chunk contract
    │
    ▼
[SLIDE PLANNER]     Gemini → classify slide type
    │                (INTRO/TRANSITION/CONTENT/CHART/TEAM/THANK_YOU)
    ▼
[SLIDE PREPARER]    Gemini → design_instruction
    │                (theme, layout, formatting rules)
    ▼
[SLIDE GENERATOR]   Qwen → tool call JSON → XML
    │
    ▼
[SLIDE EVALUATOR]   VLM → score + feedback (retry ×3)
    │
    ▼
[FINALIZE]          Save XML + preview assets
```

Manual editing is intentionally outside this path. The `/manual` workspace
entry uploads a DOCX to the existing Structure Editor; it has its own session
and then hands approved chunks to the same renderer. It does not share chatbot
state or conversation retrieval.

### Application boundaries

- `DocumentPreprocessingService` owns DOCX conversion, automatic heading
  detection, mixed-region structure inference, and the canonical Markdown/JSON
  artifact. Chatbot RAG calls only `preprocess_for_chatbot`; it does not choose
  a document mode.
- `SlideGenerationService` owns the chatbot request-to-script step. It passes
  canonical chunks to `SlideGenWorkflowService`, which is only the XML
  renderer.
- `LegacyDocxGenerationService` is the explicit adapter for old DOCX routes.
  It composes the preprocessor and the same renderer without adding another
  generation graph.

### Renderer paths
- **Chat path**: request → optional DOCX preprocessing/RAG → Markdown script → canonical chunks → shared XML renderer.
- **Manual path**: Structure Editor → approved canonical chunks → shared XML renderer.
- **Legacy API paths**: old Doc/Idea endpoints remain compatibility adapters;
  they are not exposed by the new workspace UI.

### Generator details
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
