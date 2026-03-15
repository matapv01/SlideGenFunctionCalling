#!/usr/bin/env bash
set -euo pipefail

# ── Database migration ────────────────────────────────────────────────────────
echo "[INFO] Running database migrations..."
python migrate_db.py

# ── Start application ─────────────────────────────────────────────────────────
echo "[INFO] Starting SlideGen on http://0.0.0.0:12008"
exec python backend/main.py
