# File: backend/main.py

import sys
import io
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# --- QUAN TRỌNG: Cấu hình sys.path TRƯỚC khi import các module trong backend ---

# Lấy đường dẫn tuyệt đối của file hiện tại
current_file = Path(__file__).resolve()

# Lấy thư mục gốc dự án: D:\Projects\TeamProject\SlideGenFunctionCalling
project_root = current_file.parent.parent 

# Thêm thư mục gốc vào sys.path để Python hiểu "backend" là một package
sys.path.insert(0, str(project_root))

# --- Bây giờ mới được import các module bên trong backend ---
from backend.api.app import app
from backend.config import API_HOST, API_PORT

# Load .env
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"[OK] Loaded .env from: {env_file}")
else:
    print(f"⚠️  No .env file found at: {env_file}")

if __name__ == "__main__":
    print("=" * 60)
    print("Starting SlideGen Backend Server")
    print("=" * 60)
    print(f"Server URL: http://{API_HOST}:{API_PORT}")
    print(f"API Docs: http://{API_HOST}:{API_PORT}/docs")
    print(f"Capture Health: http://{API_HOST}:{API_PORT}/health")
    print("=" * 60)

    uvicorn.run(
        app,  # Pass app object directly
        host=API_HOST,
        port=API_PORT,
        reload=False, 
        log_level="info"
    )