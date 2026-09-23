# SlideGen

AI-powered presentation generator. Upload tài liệu hoặc nhập ý tưởng -> nhận slide HTML/PNG.

## Cách dùng

### 1. Web UI
Mở trình duyệt -> chọn **Idea -> Enter Prompt** để nhập ý tưởng tiếng Việt, hoặc **Upload Document** để tải DOCX/PDF. Hệ thống chạy pipeline và trả về slide HTML/PNG.

### 2. REST API
```bash
curl -X POST http://localhost:12008/generate/idea/structure \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Giới thiệu về công ty FPT: thành lập 1988, lĩnh vực CNTT, 40000 nhân viên",
    "content_length": "medium",
    "min_slides": 5,
    "max_slides": 10
  }'
```

### 3. Pipeline kiến trúc
```
User Input (Idea / Document)
    │
    ▼
[IDEA WORKFLOW]          Gemini Agent -> research + tạo cấu trúc slide
    │
    ▼
[SLIDE PLANNER]          Gemini -> phân loại từng slide (INTRO/CONTENT/CHART/...)
    │
    ▼
[SLIDE PREPARER]         Gemini -> viết design instruction (màu sắc, font, layout)
    │
    ▼
[SLIDE GENERATOR]        Qwen / Gemini -> gọi layout tool -> HTML
    │
    ▼
[SLIDE EVALUATOR]        VLM -> chấm điểm + feedback (retry tối đa 3 lần)
    │
    ▼
[FINALIZE]               Lưu HTML + render PNG
```

- Generator dùng Qwen local: minimal system prompt + tool schemas + design instruction từ Gemini Preparer.
- Generator dùng Gemini API: system prompt = slide-type rules + tool binding.

## Training
Tài liệu training nằm ở [rl/README.md](rl/README.md).

- Direct GRPO: TRL `GRPOTrainer` + PEFT LoRA + XML rollout/reward custom.
- GRPO starts from the base model or resumes a complete GRPO checkpoint.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/generate/idea/structure` | Tạo slide từ ý tưởng |
| POST | `/generate/doc/structure` | Phân tích document -> cấu trúc |
| POST | `/auth/login` | Login |
| POST | `/auth/register` | Register |
| GET  | `/health` | Health check |

## Development

```bash
# Build & chạy
docker compose -f docker-compose.dev.yml up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:12008
# API Docs: http://localhost:12008/docs
```

Code hot-reload: sửa file backend -> auto reload, sửa frontend -> Vite HMR.

## Production

```bash
cp .env.example .env   # điền API keys
docker compose up -d --build
docker compose logs -f
```

Truy cập: `http://localhost:12008`

## Cấu trúc thư mục

```
backend/
├── domain/ports/           # Interfaces (LLM, Capture, Embedding, Aesthetic)
├── infrastructure/         # Implementations (Gemini, Playwright, DINOv2, ViT)
└── workflows/
    ├── slidegen_workflow/  # Pipeline chính (nodes, graph, tools, prompts)
    ├── doc_workflow/       # Xử lý document
    └── idea_workflow/      # Idea -> structure
frontend/                   # React + TypeScript
rl/                         # Direct GRPO training (xem rl/README.md)
```

Xem [ARCHITECTURE.md](ARCHITECTURE.md) để hiểu chi tiết thiết kế hệ thống.
