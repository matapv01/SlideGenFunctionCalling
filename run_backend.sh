#!/usr/bin/env bash
set -e

echo "==> Loading environment variables"
# export $(grep -v '^#' .env | xargs)

# Set production mode (backend will bind to 0.0.0.0)
export PRODUCTION_MODE=true

echo "==> Starting backend in PRODUCTION mode"
echo "    Backend will be accessible at: http://10.170.100.160:12008"
uv run ./web/backend/run.py
