#!/usr/bin/env bash
set -e

echo "==> Starting frontend server"
python3 -m http.server 8000 --directory web/frontend
