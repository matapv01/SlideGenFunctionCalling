# 1. Cài Python dependencies
uv sync

# 2. Cài browsers cho conversion
python -m playwright install chromium
cd web\backend
npm install
npm uninstall puppeteer-core
npm install puppeteer
npx puppeteer browsers install chrome


## Tạo file .env (root project)

env
GEMINI_API_KEY=your_key_here
DISABLE_CONVERTER=0
LOG_LEVEL=INFO


## Chạy Backend (Terminal 1)

uv run ./web/backend/run.py



→ Backend: http://localhost:3000

## Chạy Frontend (Terminal 2)


python -m http.server 8000 --directory web/frontend


→ Frontend: http://localhost:8000/index.html
