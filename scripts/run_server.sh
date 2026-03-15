#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "[ERROR] uv is not installed. Install uv first: https://docs.astral.sh/uv/"
  exit 1
fi

if [[ ! -f .env ]]; then
  if [[ -f env_template.txt ]]; then
    cp env_template.txt .env
    echo "[ERROR] Created .env from env_template.txt. Please fill API keys, then run again."
    exit 1
  fi
  echo "[ERROR] Missing .env and env_template.txt"
  exit 1
fi

echo "[INFO] Syncing backend dependencies with uv..."
uv sync

# Build frontend so BE can serve it at /
export NVM_DIR="${HOME}/.nvm"
if [[ -s "${NVM_DIR}/nvm.sh" ]]; then
  # shellcheck disable=SC1090
  . "${NVM_DIR}/nvm.sh"
  nvm use 22 >/dev/null 2>&1 || nvm install 22 >/dev/null
fi

if command -v node >/dev/null 2>&1; then
  echo "[INFO] Building frontend (Node $(node -v))..."
  cd "${ROOT_DIR}/frontend"
  rm -rf dist
  [[ ! -d node_modules ]] && npm install --legacy-peer-deps --silent
  npm run build
  cd "${ROOT_DIR}"
  echo "[INFO] Frontend built → frontend/dist/"

  echo "[INFO] Installing converter dependencies (puppeteer)..."
  cd "${ROOT_DIR}/backend/infrastructure/converter"
  [[ ! -d node_modules ]] && npm install --legacy-peer-deps --silent
  cd "${ROOT_DIR}"
else
  echo "[WARN] Node not found, skipping frontend build."
  echo "[HINT] Install nvm + Node 22 then re-run this script."
fi

echo "[INFO] Starting backend on http://0.0.0.0:12008"
exec uv run backend/main.py
