# SlideGen

AI-powered presentation generator. Chat với Slidegenius, đính kèm tài liệu khi cần,
và nhận một project slide XML hoàn chỉnh.

## Cách dùng

### 1. Web UI
Mở trình duyệt tại `/slidegen/`, đăng nhập rồi vào **Slidegenius**. Đây là workflow
tạo slide duy nhất: nhập yêu cầu tự do trong chatbot, hoặc bấm dấu `+` để đính kèm
DOCX rồi yêu cầu chatbot hỏi đáp / tạo deck từ tài liệu.

**Manual** là tab độc lập tại `/slidegen/manual`: upload DOCX, chỉnh cấu trúc trong
Structure Editor và duyệt trước khi chạy bộ máy thiết kế. Tab này không dùng state
hay lịch sử của chatbot.

### 2. REST API
```bash
curl http://localhost:12008/api/v1/chat/config
```

### 3. Pipeline kiến trúc
```
Chat request (+ optional DOCX)
    │
    ▼
[DOC PREPROCESSOR]       Scan heading; chỉ gọi LLM cho vùng chưa có cấu trúc
    │
    ▼
[RAG CONTEXT]            Chunk + embedding trên SQLite, truy hồi theo conversation
    │
    ▼
[SLIDE SCRIPT]           LLM viết prompt + context thành một kịch bản Markdown
    │
    ▼
[SLIDE PLANNER]          Gemini -> phân loại từng slide (INTRO/CONTENT/CHART/...)
    │
    ▼
[SLIDE PREPARER]         Gemini -> viết design instruction (màu sắc, font, layout)
    │
    ▼
[SLIDE GENERATOR]        Qwen / Gemini -> gọi layout tool -> XML
    │
    ▼
[SLIDE EVALUATOR]        VLM -> chấm điểm + feedback (retry tối đa 3 lần)
    │
    ▼
[FINALIZE]               Lưu XML + preview assets vào project
```

- Generator dùng Qwen local: minimal system prompt + tool schemas + design instruction từ Gemini Preparer.
- Generator dùng Gemini API: system prompt = slide-type rules + tool binding.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/chat/sessions/{id}/messages` | Chat, hỏi tài liệu hoặc tạo deck |
| POST | `/api/v1/chat/sessions/{id}/documents` | Đính kèm DOCX vào conversation |
| POST | `/generate/doc/structure` | Legacy compatibility endpoint |
| POST | `/auth/login` | Login |
| POST | `/auth/register` | Register |
| GET  | `/health` | Health check |

## Development

```bash
# Build & chạy
docker compose -f docker-compose.dev.yml up --build

# Frontend: http://localhost:5173/slidegen/
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

Truy cập qua reverse proxy: `http://localhost:8082/slidegen/`

Dev và production dùng chung một source FE trong `frontend/`. Dev chỉ bind-mount
source để HMR; production build chính source đó thành `frontend/dist`. Vì vậy
sửa giao diện chỉ thực hiện trong `frontend/src`; sau khi sửa cần rebuild image
production để cập nhật snapshot `dist`:

```bash
docker compose -f docker-compose.dev.yml up --build   # dev/HMR
docker compose up -d --build                          # production-like
```

## Cấu trúc thư mục

```
backend/
├── domain/ports/           # Interfaces (LLM, Capture, Embedding, Aesthetic)
├── application/services/   # Use cases: chat, RAG, DOCX preprocessing, renderer
├── infrastructure/         # Implementations (Gemini, Playwright, local embeddings, ViT)
└── workflows/
    ├── slidegen_workflow/  # Một renderer XML nhận canonical chunks
    ├── doc_workflow/       # Tiền xử lý DOCX thành Markdown/JSON/chunks
    └── manual_workflow/    # Workflow độc lập cho Structure Editor
frontend/                   # React + TypeScript
```

Xem [ARCHITECTURE.md](ARCHITECTURE.md) để hiểu chi tiết thiết kế hệ thống.
