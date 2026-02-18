# File: backend/api/app.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import create_router
import logging
from backend.config import STATIC_DIR, FRONTEND_DIR, CORS_ORIGINS, LOG_LEVEL
from backend.infrastructure.database.connection import init_db

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

def create_app():
    # Initialize FastAPI app
    app = FastAPI(
        title="SlideGen API",
        description="API for slide generation and management",
        version="1.0.0"
    )

    init_db()

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

    app.include_router(create_router())

    @app.get("/")
    async def read_root():
        """
        API Root - Returns API information
        """
        return {
            "name": "SlideGen Backend API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "endpoints": {
                "upload_docx": "POST /api/upload-docx",
                "slides": "GET /api/slides/{project_name}",
                "export_pdf": "POST /api/export-slides-pdf",
                "images": "GET /api/images/{name}"
            },
            "frontend": "http://localhost:8000"
        }

    return app

app = create_app()