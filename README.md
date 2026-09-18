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

Quyền admin được lưu trong database ở trường `users.is_admin`, không lấy từ
`.env`. Admin có thêm trang quản trị tại `/slidegen/admin`, nơi có thể chỉnh
phần trăm usage của từng model/effort, limit của từng plan, quản lý user, đặt
lại mật khẩu, reset usage và cấp/gỡ quyền admin. Backend kiểm tra quyền ở mỗi
request; thay đổi role có hiệu lực ngay mà không cần rebuild.

### Trang quản trị

Sau khi đăng nhập bằng tài khoản admin, mở trực tiếp:

```text
http://localhost:8082/slidegen/admin
```

Nếu deploy qua domain, thay `http://localhost:8082` bằng domain tương ứng, ví dụ:
`https://ptitai.org/slidegen/admin`.

Trong tab **Quản lý user**, admin nhập mật khẩu mặc định cho lần reset (tối thiểu 6 ký tự),
sau đó có thể đặt lại mật khẩu hoặc reset riêng cửa sổ 5 giờ của từng user. Mật khẩu chỉ được gửi
để hash ở backend, không được lưu trong cấu hình admin.

Tài khoản admin khởi tạo được quy ước là `admin@email.com`, mật khẩu khởi tạo là
`123456`. Mật khẩu này đủ 6 ký tự theo policy hiện tại; nên đổi ngay sau lần
đăng nhập đầu tiên.

Nếu tài khoản `admin@email.com` đã tồn tại nhưng chưa có quyền admin, chạy lệnh
sau để cấp quyền trực tiếp:

```bash
# Production
docker compose exec slidegen python scripts/manage_admin.py grant admin@email.com

# Development
docker compose -f docker-compose.dev.yml exec slidegen-dev \
  python scripts/manage_admin.py grant admin@email.com
```

Sau khi chạy lệnh, đăng nhập tài khoản đó, mở tab **Admin** → **Quản lý user**
để cấp hoặc gỡ quyền cho các tài khoản khác.

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

### Kiểm chứng ảnh bằng Qwen-VL

Workflow chatbot có node `image_verifier` nằm trước planner. Node này nhận các
ảnh đã tách từ DOCX cùng section/heading gần nhất, gửi ảnh và toàn bộ slide
chunks cho model vision để chọn slide phù hợp; executor sau đó mới inject ảnh
đã được duyệt vào asset của project. Ảnh từ DDGS cũng được so sánh với nội
dung slide trước khi dùng. Nếu endpoint đang chạy model text-only hoặc không
khả dụng, verifier tự ngắt trong process và giữ nguyên luồng tạo slide hiện có.

Model dùng cho kiểm chứng ảnh được cấu hình tập trung trong
`backend/config.py` bằng `VLM_MODEL = LLM_MODEL`; hiện tại cả hai cùng là
`qwen` và dùng chung endpoint/API key của LLM. Khi triển khai một model vision
riêng, chỉ cần đổi hằng số này và provider tương ứng trong composition root,
không thêm override rải rác trong `.env`. Ảnh DOCX được lưu private dưới
`static/chatbot_documents` và được copy vào asset của project khi được chọn;
không trả đường dẫn nội bộ ra API.
- Generator dùng Gemini API: system prompt = slide-type rules + tool binding.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/chat/sessions/{id}/messages` | Chat, hỏi tài liệu hoặc tạo deck |
| POST | `/api/v1/chat/sessions/{id}/documents` | Đính kèm DOCX vào conversation |
| GET/PUT | `/api/v1/admin/usage/config` | Xem/cập nhật trọng số usage và plan limits (admin) |
| POST | `/api/v1/admin/usage/reset` | Reset usage toàn bộ người dùng (admin) |
| GET | `/api/v1/admin/users` | Xem danh sách user và cửa sổ usage riêng (admin) |
| PATCH | `/api/v1/admin/users/{id}/admin` | Cấp hoặc gỡ quyền admin (admin) |
| POST | `/api/v1/admin/users/{id}/password-reset` | Đặt lại mật khẩu user (admin) |
| POST | `/api/v1/admin/users/{id}/usage-reset` | Reset usage và bắt đầu lại 5 giờ cho một user (admin) |
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
