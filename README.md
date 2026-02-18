# 1. Cài dependencies
uv sync
npm install

## Tạo file .env (root project)
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY1=your_key_here
TAVILY_API_KEY2=your_key_here
TAVILY_API_KEY3=your_key_here


## Chạy Backend (Terminal 1)
uv run backend/main.py
→ Backend: http://localhost:12008

## Chạy Frontend (Terminal 2)
python -m http.server 8000 --directory frontend
→ Frontend: http://localhost:8000/index.html
