from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .router import create_router
import logging
from web.backend.app.config import STATIC_DIR, FRONTEND_DIR, CORS_ORIGINS, LOG_LEVEL
from web.backend.app.application.conversion_service import conversion_service
from web.backend.app.application.capture_service import capture_service
from web.backend.app.application.workflow_service import workflow_service
from web.backend.app.resource.database import init_db

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
    
    @app.get("/health")
    async def health_check():
        """Overall system health check"""
        return JSONResponse(content={
            "status": "healthy",
            "services": {
                "conversion": conversion_service is not None and conversion_service.is_available(),
                "capture": capture_service is not None and capture_service.is_available(),
                "workflow": workflow_service is not None and workflow_service.is_available(),
            }
        })

    return app

app = create_app()