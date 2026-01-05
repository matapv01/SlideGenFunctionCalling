#!/usr/bin/env bash
set -e

# Load environment variables silently
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    echo "⚠️  No .env file found"
fi

# Set production mode
export PRODUCTION_MODE=true

uv run ./web/backend/run.py
