#!/usr/bin/env bash
set -e

# =============================================================================
# SlideGen - Local Development Runner
# Chạy cả backend và frontend trong 2 terminal riêng
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           SlideGen - Local Development Mode                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"

# Check .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "❌ Error: .env file not found!"
    echo ""
    echo "📋 Please create .env file:"
    echo "   cp .env.example .env"
    echo "   # Then edit .env and add your GEMINI_API_KEY"
    echo ""
    exit 1
fi

# Check GEMINI_API_KEY
if ! grep -q "GEMINI_API_KEY=." .env || grep -q "GEMINI_API_KEY=your_" .env; then
    echo ""
    echo "⚠️  Warning: GEMINI_API_KEY may not be set in .env"
    echo "   Please ensure you have a valid API key"
    echo ""
fi

echo ""
echo "🔧 Loading environment from .env..."
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Set LOCAL mode
export PRODUCTION_MODE=false

echo ""
echo "📍 Local URLs:"
echo "   Frontend: http://localhost:8000"
echo "   Backend:  http://localhost:12008"
echo "   API Docs: http://localhost:12008/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Option 1: Run both in background (recommended for quick testing)
if [ "$1" == "--both" ] || [ "$1" == "-b" ]; then
    echo "🚀 Starting both backend and frontend..."
    echo ""
    
    # Start backend in background
    echo "📡 Starting Backend (port 12008)..."
    uv run ./web/backend/run.py &
    BACKEND_PID=$!
    
    # Wait a bit for backend to start
    sleep 2
    
    # Start frontend in background
    echo "🌐 Starting Frontend (port 8000)..."
    python3 -m http.server 8000 --directory web/frontend &
    FRONTEND_PID=$!
    
    echo ""
    echo "✅ Both servers started!"
    echo "   Backend PID: $BACKEND_PID"
    echo "   Frontend PID: $FRONTEND_PID"
    echo ""
    echo "🌐 Open http://localhost:8000 in your browser"
    echo ""
    echo "Press Ctrl+C to stop both servers..."
    
    # Trap Ctrl+C to kill both processes
    trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
    
    # Wait for both processes
    wait
    
# Option 2: Run backend only (default)
else
    echo "🚀 Starting Backend only..."
    echo "   Run frontend separately: ./run_frontend.sh"
    echo ""
    uv run ./web/backend/run.py
fi
