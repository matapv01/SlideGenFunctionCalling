#!/usr/bin/env bash
set -e

# =============================================================================
# SlideGen - Local Development Runner
# Chạy cả backend và frontend trong 2 terminal riêng
# =============================================================================

echo ""
echo "╔═══════════════════════════════════════════╗"
echo "║       SlideGen - Development Mode         ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "   Run: cp .env.example .env"
    exit 1
fi

# Check GEMINI_API_KEY silently
if ! grep -q "GEMINI_API_KEY=." .env || grep -q "GEMINI_API_KEY=your_" .env; then
    echo "⚠️  Warning: GEMINI_API_KEY may not be configured"
    echo ""
fi

# Load environment silently
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Set LOCAL mode
export PRODUCTION_MODE=false

# Option 1: Run both in background (recommended for quick testing)
if [ "$1" == "--both" ] || [ "$1" == "-b" ]; then
    echo "🚀 Starting services..."
    
    # Start backend in background
    uv run ./web/backend/run.py &
    BACKEND_PID=$!
    
    # Wait a bit for backend to start
    sleep 2
    
    # Start frontend in background (suppress output)
    python3 -m http.server 8000 --directory web/frontend > /dev/null 2>&1 &
    FRONTEND_PID=$!
    
    echo "✅ All services started"
    echo ""
    echo "Press Ctrl+C to stop..."
    
    # Trap Ctrl+C to kill both processes
    trap "echo ''; echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
    
    # Wait for both processes
    wait
    
# Option 2: Run backend only (default)
else
    echo "🚀 Starting backend..."
    uv run ./web/backend/run.py
fi
