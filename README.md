# 1. Cài dependencies
// backend
uv sync
// frontend
cd frontend
npm install



cd frontend
npm install jszip @types/jszip --legacy-peer-deps

## Tạo file .env (root project)
GEMINI_API_KEY=your_key_here
TAVILY_API_KEY1=your_key_here
TAVILY_API_KEY2=your_key_here
TAVILY_API_KEY3=your_key_here


## Chạy Backend (Terminal 1)
uv run backend/main.py
→ Backend: http://localhost:12008

## Chạy Frontend (Terminal 2)
cd frontend
npm run dev
→ Frontend: http://localhost:8080
