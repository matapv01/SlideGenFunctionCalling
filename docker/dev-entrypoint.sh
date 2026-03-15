#!/bin/bash
set -e

echo "=========================================="
echo "  SlideGen — DEV Environment"
echo "=========================================="

# ── 1. DB migrations ──────────────────────────────────────────────────────────
echo "[1/3] Running DB migrations..."
python /app/migrate_db.py

# ── 2. Vite dev server (background) ──────────────────────────────────────────
# --host 0.0.0.0 cần thiết để bind ra ngoài container (port 5173)
echo "[2/3] Starting Vite dev server on :5173..."
cd /app/frontend && npm run dev -- --host 0.0.0.0 &

# ── 3. FastAPI backend với hot reload (foreground / PID 1) ────────────────────
# exec → uvicorn trở thành PID 1, nhận SIGTERM từ Docker khi container stop
# --reload-dir /app/backend → chỉ watch source code, không watch node_modules/cache
echo "[3/3] Starting backend on :12008 (hot reload)..."
exec uv run uvicorn backend.api.app:app \
    --host 0.0.0.0 \
    --port 12008 \
    --reload \
    --reload-dir /app/backend \
    --log-level info
