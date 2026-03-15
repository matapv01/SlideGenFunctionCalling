#!/usr/bin/env bash
set -euo pipefail

# ── Point Puppeteer to Playwright's Chromium ─────────────────────────────────
# Both tools share a single Chromium binary to keep the image lean.
CHROMIUM_BIN=$(find /root/.cache/ms-playwright -name 'chrome' -type f 2>/dev/null | head -1)
if [[ -n "$CHROMIUM_BIN" ]]; then
    export PUPPETEER_EXECUTABLE_PATH="$CHROMIUM_BIN"
    echo "[OK] PUPPETEER_EXECUTABLE_PATH=$PUPPETEER_EXECUTABLE_PATH"
else
    echo "[WARN] Playwright Chromium not found; Puppeteer may fail to start"
fi

# ── Database migration ────────────────────────────────────────────────────────
echo "[INFO] Running database migrations..."
python migrate_db.py

# ── Start application ─────────────────────────────────────────────────────────
echo "[INFO] Starting SlideGen on http://0.0.0.0:12008"
exec python backend/main.py
