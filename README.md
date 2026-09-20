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

Trong bảng **Giới hạn plan**, hai cột DOCX là nguồn cấu hình duy nhất cho việc
upload tài liệu: `DOCX tối đa / file (MB)` giới hạn từng file, còn
`DOCX tối đa / cuộc trò chuyện (MB)` giới hạn tổng tất cả file đã đính kèm trong
một conversation. Hai giá trị này được áp dụng riêng theo plan `Free`, `Plus` và
`Ultra` cho cả chatbot RAG lẫn các luồng upload DOCX cũ; không cần sửa code hay
`.env`. Mức bootstrap hiện tại là `Free: 30/150 MB`, `Plus: 50/250 MB`,
`Ultra: 80/400 MB`. Giới hạn file không được lớn hơn giới hạn conversation.

### Trang quản trị

Sau khi đăng nhập bằng tài khoản admin, mở trực tiếp:

```text
http://localhost:8082/slidegen/admin
```

Nếu deploy qua domain, thay `http://localhost:8082` bằng domain tương ứng, ví dụ:
`https://ptitai.org/slidegen/admin`.

### Google OAuth callback

Google Cloud Console must contain the exact authorized redirect URI for the
environment:

- Production: `https://ptitai.org/api/v1/auth/google/callback`
- Local Docker: `http://localhost:8082/api/v1/auth/google/callback`

Do not add `/slidegen` to the callback path. `/slidegen` is the frontend mount;
the OAuth callback is served by the API under `/api/v1/auth`.

Để cấp quyền admin cho một tài khoản đã tồn tại, chạy:

```bash
docker compose exec slidegen python scripts/manage_admin.py grant email@example.com
```

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
[SLIDE PLANNER]          Qwen -> phân loại từng slide và visual intent
    │
    ▼
[IMAGE SEARCH]            Backend -> lấy tối đa 10 candidate/intent, song song tối đa 5
    │
    ▼
[IMAGE VERIFIER]          Qwen-VL -> chọn ảnh phù hợp với toàn bộ ngữ cảnh deck/slide
    │
    ▼
[SLIDE REFINER]           Qwen -> chốt nội dung và bố cục sau khi biết asset được duyệt
    │
    ▼
[SLIDE GENERATOR]        Qwen -> gọi đúng một layout tool -> XML
    │
    ▼
[FINALIZE]               Lưu XML + preview assets vào project
```

- Generator dùng model OpenAI-compatible được cấu hình trong `backend/config.py`;
  hiện tại là Qwen, với tool schema XML và design instruction dùng chung toàn deck.

### Kiểm chứng ảnh bằng Qwen-VL

Workflow chatbot chạy planner phase 1 để tạo visual intent, backend search tối
đa 10 candidate song song, rồi node `image_verifier` so sánh chúng cùng ảnh
DOCX với topic/purpose và outline toàn deck. Planner phase 2 tiếp nhận các ảnh
được duyệt cùng visual notes để chốt lại nội dung, brief hình ảnh và bố cục dựa
trên context đã truy hồi ở application layer; XML generator chỉ nhận asset đã
duyệt và không tự search ảnh. Nếu endpoint text-only,
search không có ứng viên hoặc verifier không khả dụng, workflow không chèn ảnh
stock mặc định và slide chuyển sang layout không ảnh.

Model và endpoint kiểm chứng ảnh được cấu hình tập trung trong
`backend/config.py` qua `VLM_MODEL` và `VLM_BASE_URL`; hiện tại cả hai cùng
trỏ tới Qwen như generator. Credential đọc từ `VLM_API_KEY` trong `.env` và
tạm thời fallback sang `LLM_API_KEY` nếu chưa khai báo biến riêng. Khi triển
khai một model vision riêng, chỉ cần đổi hằng số VLM và credential tương ứng,
không thêm override URL/model rải rác trong `.env`. Ảnh DOCX được lưu private dưới
`static/chatbot_documents` và được copy vào asset của project khi được chọn;
không trả đường dẫn nội bộ ra API.

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
