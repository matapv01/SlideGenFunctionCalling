#!/usr/bin/env bash
set -e

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║       SlideGen Frontend Server            ║"
echo "╚═══════════════════════════════════════════╝"
echo ""
echo "✅ Frontend server started"
echo ""

python3 -m http.server 8000 --directory web/frontend > /dev/null 2>&1
