"""
Run script for SlideGen Backend
"""
import uvicorn
import sys
from pathlib import Path
from dotenv import load_dotenv
from app.main import app
from app.config import API_HOST, API_PORT


# Load .env from root project directory
root_dir = Path(__file__).parent.parent.parent  # SlideGenFunctionCalling/
env_file = root_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded .env from: {env_file}")
else:
    print(f"⚠️  No .env file found at: {env_file}")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    print("=" * 60)
    print("🌐 Starting SlideGen Backend Server")
    print("=" * 60)
    print(f"🚀 Server URL: http://{API_HOST}:{API_PORT}")
    print(f"📡 API Docs: http://{API_HOST}:{API_PORT}/docs")
    print(f"📸 Capture Health: http://{API_HOST}:{API_PORT}/api/capture-health")
    print(f"🔧 Converter Health: http://{API_HOST}:{API_PORT}/api/converter-health")
    print("=" * 60)

    uvicorn.run(
        app,  # Pass app object directly instead of string when using sys.path manipulation
        host=API_HOST,
        port=API_PORT,
        reload=False,  # Disable reload to avoid sys.path issues
        log_level="info"
    )
