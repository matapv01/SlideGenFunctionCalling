# File: backend/api/app.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from backend.api.router import create_router
import logging
from backend.config import STATIC_DIR, FRONTEND_DIST_DIR, CORS_ORIGINS, LOG_LEVEL
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

    # API routes - MUST be registered before the SPA catch-all
    app.include_router(create_router())

    # Both production and local Docker expose the new FE at /slidegen. Keep
    # public assets and client-side routes under that single mount point.
    @app.get("/slidegen")
    @app.get("/slidegen/")
    async def serve_slidegen_root():
        index = FRONTEND_DIST_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index), headers={"Cache-Control": "no-store, must-revalidate"})
        return JSONResponse({"error": "Frontend not built"}, status_code=404)

    @app.get("/slidegen/{full_path:path}")
    async def serve_slidegen(full_path: str):
        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        index = FRONTEND_DIST_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index), headers={"Cache-Control": "no-store, must-revalidate"})
        return JSONResponse({"error": "Frontend not built"}, status_code=404)

    @app.get("/health")
    async def health_check():
        """Lightweight JSON health endpoint used by Docker and diagnostics."""
        return {
            "status": "ok",
            "services": {
                "api": "ok",
                "workflow": "available",
            },
        }

    # Serve frontend SPA from dist build
    @app.get("/")
    async def serve_root():
        index = FRONTEND_DIST_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index), headers={"Cache-Control": "no-store, must-revalidate"})
        return JSONResponse({
            "name": "SlideGen API", "version": "1.0.0", "status": "running",
            "docs": "/docs",
            "note": "Frontend not built. Run: cd frontend && npm run build"
        })

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Never intercept API routes — let them fall through to a proper 404
        if full_path.startswith("api/"):
            return JSONResponse({"error": "Not found"}, status_code=404)
        # Try to serve a real file from dist (JS, CSS, images, etc.)
        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Fallback: serve index.html for client-side SPA routing
        index = FRONTEND_DIST_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index), headers={"Cache-Control": "no-store, must-revalidate"})
        return JSONResponse({"error": "Frontend not built. Run: cd frontend && npm run build"}, status_code=404)

    return app

app = create_app()
