"""
Application Configuration
"""
import os
from pathlib import Path

# Base directories
PROJECT_DIR = Path(__file__).parent.parent.parent  # web/
STATIC_DIR = PROJECT_DIR / "static"
FRONTEND_DIR = PROJECT_DIR / "frontend"
IMAGE_DIR = PROJECT_DIR / "Image"

# Upload and output directories
UPLOAD_DIR = STATIC_DIR / "uploads"
OUTPUT_DIR = STATIC_DIR / "output"
TEMP_DIR = STATIC_DIR / "temp"
CAPTURES_DIR = STATIC_DIR / "captures"

# Create directories
for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR, CAPTURES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Feature flags
DISABLE_CONVERTER = os.getenv('DISABLE_CONVERTER', '0').lower() in ('1', 'true', 'yes')

# CORS settings
CORS_ORIGINS = ["*"]  # Configure for production

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 3000
