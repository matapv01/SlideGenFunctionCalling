# 1. Cài Python dependencies
uv sync

# 2. Cài browsers cho conversion
python -m playwright install chromium
cd web\backend
npm install
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



# 3. reset vip member
cd /home/iec/QuangNM/SlideGenFunctionCalling/web/backend && python3 -c "from app.database import get_db; conn = get_db().__enter__(); conn.execute('UPDATE users SET is_vip = 0'); conn.commit(); conn.close(); print('✅ Đã reset TOÀN BỘ database về trạng thái non-VIP!')"