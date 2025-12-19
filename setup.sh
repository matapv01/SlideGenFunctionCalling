#!/usr/bin/env bash
set -e

echo "==> Step 1: Install Python dependencies (uv)"
uv sync

echo "==> Step 2: Install Playwright Chromium"
# uv run python -m playwright install chromium
# echo 'export PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright' >> ~/.bashrc
# source ~/.bashrc

echo "==> Step 3: Install backend JS dependencies"
cd web/backend
npm install
npx puppeteer browsers install chrome
cd ../../

echo "==> Setup completed successfully"
