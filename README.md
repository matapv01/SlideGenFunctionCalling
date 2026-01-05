# SlideGen - AI Slide Generator

Hệ thống tạo slide tự động sử dụng AI (Gemini).

## 🚀 Quick Start (Chạy Local)

### Bước 1: Cài đặt dependencies

```bash
# Cài Python dependencies (cần có uv - https://github.com/astral-sh/uv)
uv sync

# Cài Playwright browser (cho capture slides)
uv run python -m playwright install chromium

# Cài Node.js dependencies cho converter
cd web/backend
npm install
npx puppeteer browsers install chrome
cd ../..
```

### Bước 2: Tạo file .env

```bash
# Copy file mẫu
cp .env.example .env

# Sửa file .env và thêm GEMINI_API_KEY của bạn
# Lấy API key tại: https://aistudio.google.com/app/apikey
```

### Bước 3: Chạy ứng dụng

**Cách 1: Chạy cả frontend + backend (đơn giản nhất)**
```bash
./run_local.sh --both
```
→ Frontend: http://localhost:8000  
→ Backend: http://localhost:12008

**Cách 2: Chạy riêng từng service (khuyên dùng khi develop)**
```bash
# Terminal 1 - Backend
./run_local.sh

# Terminal 2 - Frontend
./run_frontend.sh
```

## 📁 File cấu hình

| File | Mô tả |
|------|-------|
| `.env` | Chứa API keys và config (copy từ `.env.example`) |
| `.env.example` | Template cho file .env |
| `run_local.sh` | Chạy local development mode |
| `run_backend.sh` | Chạy backend production mode |
| `run_frontend.sh` | Chạy frontend server |
| `setup.sh` | Cài đặt tất cả dependencies |

## 🔑 Environment Variables

| Variable | Required | Default | Mô tả |
|----------|----------|---------|-------|
| `GEMINI_API_KEY` | ✅ Yes | - | API key từ Google AI Studio |
| `DISABLE_CONVERTER` | No | `0` | Set `1` để tắt HTML converter |
| `LOG_LEVEL` | No | `INFO` | Log level: DEBUG, INFO, WARNING, ERROR |

## 🛠️ Development

### Cấu trúc thư mục

```
SlideGenFunctionCalling/
├── src/                    # Core slide generation logic
│   ├── graph/              # LangGraph workflow
│   ├── models/             # LLM configurations
│   ├── nodes/              # Processing nodes
│   ├── tools/              # HTML generation tools
│   └── utils/              # Utilities
├── web/
│   ├── backend/            # FastAPI backend server
│   │   ├── app/            # Main application
│   │   └── run.py          # Entry point
│   └── frontend/           # HTML/JS frontend
├── data/                   # Input/output data
└── faiss_tool_retriever_index/  # Tool retrieval index
```

### URLs khi chạy local

- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:12008
- **API Documentation**: http://localhost:12008/docs
- **Capture Health**: http://localhost:12008/api/capture-health

## 🚀 Production Deployment

```bash
# Chạy backend với PRODUCTION_MODE=true
./run_backend.sh

# Hoặc dùng Docker
cd docker
docker-compose up -d
```

## 🔧 Troubleshooting

### Lỗi: "GEMINI_API_KEY not set"
- Kiểm tra file `.env` đã có `GEMINI_API_KEY=your_key`
- API key lấy từ https://aistudio.google.com/app/apikey

### Lỗi: "Playwright browser not found"
```bash
uv run python -m playwright install chromium
```

### Lỗi: "Converter not available"
```bash
cd web/backend
npm install
npx puppeteer browsers install chrome
```

### Reset VIP member (development)
```bash
cd web/backend && python3 -c "from app.database import get_db; conn = get_db().__enter__(); conn.execute('UPDATE users SET is_vip = 0'); conn.commit(); conn.close(); print('✅ Done!')"
```