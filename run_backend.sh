#!/usr/bin/env bash
set -e

echo "==> Loading environment variables"
# export $(grep -v '^#' .env | xargs)

echo "==> Starting backend"
uv run ./web/backend/run.py
