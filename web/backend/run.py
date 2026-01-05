"""
Run script for SlideGen Backend
"""
import uvicorn
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env from root project directory
root_dir = Path(__file__).parent.parent.parent  # SlideGenFunctionCalling/
env_file = root_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    print("⚠️  No .env file found")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app
from app.config import API_HOST, API_PORT

if __name__ == "__main__":
    print("")
    print("╔═══════════════════════════════════════════╗")
    print("║       SlideGen Backend Server             ║")
    print("╚═══════════════════════════════════════════╝")
    print("")
    print("✅ Server started successfully")
    print("")
    
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="warning"  # Reduce log verbosity
    )
