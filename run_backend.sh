#!/usr/bin/env bash
set -e

echo "==> Loading environment variables"
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
    echo "✅ Loaded .env file"
else
    echo "⚠️  No .env file found - using defaults"
fi

# Set production mode (backend will bind to 0.0.0.0)
export PRODUCTION_MODE=true

echo "==> Starting backend in PRODUCTION mode"
echo "    Backend will be accessible at: http://0.0.0.0:12008"
echo "    API Docs: http://0.0.0.0:12008/docs"
uv run ./web/backend/run.py
