#!/usr/bin/env bash
set -e

# =============================================================================
# SlideGen - Quick Setup Script
# Cài đặt tất cả dependencies và tạo file .env nếu chưa có
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║               SlideGen - Quick Setup                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' is not installed!"
    echo ""
    echo "📋 Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "   Or via pip:"
    echo "   pip install uv"
    echo ""
    exit 1
fi

# Check if node/npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ 'npm' is not installed!"
    echo ""
    echo "📋 Please install Node.js first:"
    echo "   https://nodejs.org/"
    echo ""
    exit 1
fi

echo "==> Step 1: Install Python dependencies (uv)"
uv sync
echo "✅ Python dependencies installed"
echo ""

echo "==> Step 2: Install Playwright Chromium"
uv run python -m playwright install chromium
echo "✅ Playwright Chromium installed"
echo ""

echo "==> Step 3: Install backend JS dependencies"
cd web/backend
npm install
npx puppeteer browsers install chrome
cd ../../
echo "✅ Node.js dependencies installed"
echo ""

echo "==> Step 4: Setup .env file"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY"
        echo "   Get your API key at: https://aistudio.google.com/app/apikey"
    else
        echo "⚠️  No .env.example found, creating basic .env"
        echo 'GEMINI_API_KEY=your_api_key_here' > .env
        echo 'DISABLE_CONVERTER=0' >> .env
        echo 'LOG_LEVEL=INFO' >> .env
        echo "✅ Created basic .env file"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete! 🎉                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env and add your GEMINI_API_KEY"
echo "   2. Run: ./run_local.sh --both"
echo "   3. Open: http://localhost:8000"
echo ""
