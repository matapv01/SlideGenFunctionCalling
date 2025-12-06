"""
SlideGen Backend - Main FastAPI Application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import shutil
import zipfile
import json
import re
from pathlib import Path
from datetime import datetime

from .config import (
    PROJECT_DIR, STATIC_DIR, IMAGE_DIR, UPLOAD_DIR, 
    OUTPUT_DIR, TEMP_DIR, CAPTURES_DIR, CORS_ORIGINS, 
    DISABLE_CONVERTER, LOG_LEVEL
)
from .schemas import (
    CaptureSlideRequest, CaptureMultipleSlidesRequest,
    ProjectUploadResponse, ConversionStatusResponse,
    HealthCheckResponse
)
from .services import SlideService, CaptureService, ConversionService, WorkflowService

# Setup logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SlideGen API",
    description="API for slide generation and management",
    version="1.0.0"
)

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

# Initialize services
slide_service = SlideService(STATIC_DIR, IMAGE_DIR)

# Initialize conversion service
conversion_service = None
if not DISABLE_CONVERTER:
    try:
        conversion_service = ConversionService(PROJECT_DIR)
        if conversion_service.is_available():
            logger.info('✅ ConversionService initialized successfully')
        else:
            logger.warning('⚠️  ConversionService dependencies not available')
            conversion_service = None
    except Exception as e:
        logger.warning(f'Failed to initialize ConversionService: {e}')
        conversion_service = None
else:
    logger.info('DISABLE_CONVERTER set: converter functionality is disabled')

# Initialize capture service
capture_service = None
try:
    # Import capture module dynamically
    import sys
    sys.path.insert(0, str(PROJECT_DIR))
    from capture import SlideCapture
    
    slide_capture = SlideCapture()
    capture_service = CaptureService(CAPTURES_DIR, slide_capture)
    logger.info('✅ CaptureService initialized successfully')
except Exception as e:
    logger.warning(f'Failed to initialize CaptureService: {e}')
    capture_service = None

# Initialize workflow service
workflow_service = None
try:
    workflow_service = WorkflowService(str(PROJECT_DIR))
    if workflow_service.is_available():
        logger.info('✅ WorkflowService initialized successfully')
    else:
        logger.warning('⚠️  WorkflowService not available - using fallback slides')
except Exception as e:
    logger.warning(f'Failed to initialize WorkflowService: {e}')
    workflow_service = None


# ========================== UTILITY FUNCTIONS ==========================

def clear_temp_dir(temp_dir: Path):
    """Clear temporary directory"""
    if temp_dir.exists():
        for item in temp_dir.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                logger.warning(f"Could not remove {item}: {e}")


# ========================== ROOT ENDPOINTS ==========================

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
            "upload_zip": "POST /api/upload-zip",
            "slides": "GET /api/slides/{project_name}",
            "capture": "POST /api/capture-slide",
            "export_pdf": "POST /api/export-slides-pdf",
            "images": "GET /api/images/{name}"
        },
        "frontend": "http://localhost:8000"
    }


# ========================== UPLOAD ENDPOINTS ==========================

@app.post("/api/upload-docx")
async def upload_docx(file: UploadFile = File(...)):
    """Upload and process DOCX file with AI workflow"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only DOCX files accepted")
    
    # Create project name from filename
    project_name = os.path.splitext(file.filename)[0]
    output_folder = OUTPUT_DIR / project_name
    
    # Handle existing project folder
    if output_folder.exists():
        try:
            shutil.rmtree(output_folder)
        except PermissionError:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_name = f"{project_name}_{timestamp}"
            output_folder = OUTPUT_DIR / project_name
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Save temp file
    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Try to process with AI workflow first
        if workflow_service and workflow_service.is_available():
            logger.info(f"🤖 Processing DOCX with AI workflow: {file.filename}")
            
            result_zip = await workflow_service.process_docx_with_workflow(
                docx_path=str(temp_path),
                output_folder=str(output_folder),
                router_flags=False
            )
            
            if result_zip and os.path.exists(result_zip):
                logger.info(f"✅ Successfully processed with workflow")
                
                # Extract ZIP to output folder
                html_folder = output_folder / "html"
                html_folder.mkdir(exist_ok=True)
                
                try:
                    with zipfile.ZipFile(result_zip, 'r') as zip_ref:
                        for file_info in zip_ref.infolist():
                            # Skip directories and temp_debug
                            if file_info.filename.endswith('/') or 'temp_debug' in file_info.filename:
                                continue
                            try:
                                zip_ref.extract(file_info, output_folder)
                            except Exception as e:
                                logger.warning(f"Error extracting {file_info.filename}: {e}")
                    
                    logger.info(f"Successfully extracted workflow results")
                except Exception as e:
                    logger.error(f"Error extracting ZIP: {e}")
                    raise
            else:
                raise Exception("Workflow did not produce valid output")
        else:
            logger.warning("⚠️ Workflow not available, using sample slides")
            raise Exception("Workflow not available")
            
    except Exception as e:
        # Fallback: use sample HTML slides
        logger.warning(f"⚠️ Fallback to sample slides: {e}")
        
        html_folder = output_folder / "html"
        html_folder.mkdir(exist_ok=True)
        
        # Copy sample HTML files
        sample_html_dir = STATIC_DIR / "sample_html"
        if sample_html_dir.exists():
            for html_file in sample_html_dir.glob("*.html"):
                shutil.copy2(html_file, html_folder / html_file.name)
        
    finally:
        if temp_path.exists():
            temp_path.unlink()
    
    # Convert slides if converter available
    if conversion_service and conversion_service.is_available():
        html_folder = output_folder / "html"
        converted_folder = output_folder / "converted"
        
        if html_folder.exists():
            try:
                converted_folder.mkdir(exist_ok=True)
                conversion_result = conversion_service.convert_slides_batch(html_folder, converted_folder)
                logger.info(f"Conversion: {len(conversion_result['success'])} success, {len(conversion_result['failed'])} failed")
            except Exception as e:
                logger.error(f"Conversion error: {e}")
                logger.error(f"Conversion error: {e}")
    
    # Build slides response
    slides = slide_service.build_slides_from_output(str(output_folder))
    
    return JSONResponse(content={"slides": slides, "project_name": project_name})


@app.post("/api/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    """Upload and extract ZIP file"""
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files accepted")
    
    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    project_name = os.path.splitext(file.filename)[0]
    output_folder = OUTPUT_DIR / project_name
    
    # Handle existing folder
    if output_folder.exists():
        try:
            shutil.rmtree(output_folder)
        except Exception as e:
            logger.warning(f"Could not remove existing folder: {e}")
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Extract ZIP
    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)
    
    # Build slides
    slides = slide_service.build_slides_from_output(str(output_folder))
    
    temp_path.unlink()
    
    return JSONResponse(content={"slides": slides})


# ========================== SLIDES API ==========================

@app.get("/api/slides/{project_name}")
async def get_project_slides(project_name: str):
    """Get slides for a specific project"""
    try:
        output_folder = OUTPUT_DIR / project_name
        if not output_folder.exists():
            raise HTTPException(status_code=404, detail=f"Project not found: {project_name}")
        
        slides = slide_service.build_slides_from_output(str(output_folder))
        
        if not slides:
            raise HTTPException(status_code=404, detail=f"No slides found for project: {project_name}")
        
        return JSONResponse(content={
            "project_name": project_name,
            "slides": slides,
            "count": len(slides)
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting slides for project {project_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================== IMAGE ENDPOINTS ==========================

@app.get("/api/images/{image_name}")
async def get_image(image_name: str):
    """Serve image files"""
    image_path = IMAGE_DIR / image_name
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)


# ========================== CONVERSION ENDPOINTS ==========================

@app.post("/api/convert-slides")
async def convert_slides(data: dict):
    """Convert HTML slides to absolute positioning"""
    if conversion_service is None:
        raise HTTPException(status_code=503, detail="Converter not available")
    
    project_name = data.get("project_name")
    if not project_name:
        raise HTTPException(status_code=400, detail="Missing project_name")
    
    output_folder = OUTPUT_DIR / project_name
    if not output_folder.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    html_folder = output_folder / "html"
    converted_folder = output_folder / "converted"
    
    if not html_folder.exists():
        raise HTTPException(status_code=404, detail="HTML folder not found")
    
    try:
        converted_folder.mkdir(exist_ok=True)
        conversion_result = conversion_service.convert_slides_batch(html_folder, converted_folder)
        
        return JSONResponse(content={
            "success": True,
            "conversion_result": conversion_result,
            "message": f"Converted {len(conversion_result['success'])} slides successfully"
        })
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.get("/api/conversion-status/{project_name}")
async def get_conversion_status(project_name: str):
    """Get conversion status for a project"""
    if conversion_service is None:
        raise HTTPException(status_code=503, detail="Converter not available")
    
    output_folder = OUTPUT_DIR / project_name
    if not output_folder.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    html_folder = output_folder / "html"
    converted_folder = output_folder / "converted"
    
    if not html_folder.exists():
        raise HTTPException(status_code=404, detail="HTML folder not found")
    
    status = conversion_service.get_conversion_status(html_folder, converted_folder)
    
    return JSONResponse(content={
        "project_name": project_name,
        "status": status,
        "has_converted": converted_folder.exists()
    })


@app.get("/api/converter-health")
async def check_converter_health():
    """Check converter system health"""
    if conversion_service is None:
        return JSONResponse(content={
            "healthy": False,
            "message": "Converter is disabled or not initialized"
        })
    
    return JSONResponse(content=conversion_service.check_health())


# ========================== CAPTURE ENDPOINTS ==========================

@app.post("/api/capture-slide")
async def capture_slide(request: CaptureSlideRequest):
    """Capture single slide from HTML content"""
    if capture_service is None or not capture_service.is_available():
        raise HTTPException(status_code=503, detail="Capture service not available")
    
    try:
        result = await capture_service.capture_single_slide(
            request.html_content,
            request.slide_name
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Capture error: {e}")
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


@app.post("/api/capture-slides-batch")
async def capture_slides_batch(request: CaptureMultipleSlidesRequest):
    """Capture multiple slides and return as ZIP"""
    if capture_service is None or not capture_service.is_available():
        raise HTTPException(status_code=503, detail="Capture service not available")
    
    try:
        result = await capture_service.capture_multiple_slides(request.slides)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Batch capture error: {e}")
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


@app.get("/api/download-capture/{filename}")
async def download_capture(filename: str):
    """Download captured slide or ZIP file"""
    try:
        if capture_service is None:
            raise HTTPException(status_code=503, detail="Capture service not available")
        
        file_path = capture_service.get_capture_file(filename)
        return FileResponse(
            file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/capture-health")
async def check_capture_health():
    """Check capture system health"""
    if capture_service is None:
        return JSONResponse(content={
            "healthy": False,
            "message": "Capture service not initialized"
        })
    
    return JSONResponse(content=capture_service.check_health())


# ========================== PDF EXPORT ENDPOINTS ==========================

@app.post("/api/export-slide-pdf")
async def export_slide_pdf(request: CaptureSlideRequest):
    """Export single slide to PDF"""
    if capture_service is None or not capture_service.is_available():
        raise HTTPException(status_code=503, detail="Capture service not available")
    
    try:
        result = await capture_service.export_slide_to_pdf(
            request.html_content,
            request.slide_name
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


@app.post("/api/export-slides-pdf")
async def export_slides_pdf(request: CaptureMultipleSlidesRequest):
    """Export multiple slides to a single PDF"""
    if capture_service is None or not capture_service.is_available():
        raise HTTPException(status_code=503, detail="Capture service not available")
    
    try:
        result = await capture_service.export_slides_to_pdf(request.slides)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


# ========================== HEALTH CHECK ==========================

@app.get("/api/health")
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


@app.get("/api/workflow-health")
async def check_workflow_health():
    """Check AI workflow system health"""
    try:
        if workflow_service is None:
            return JSONResponse(content={
                "healthy": False,
                "message": "Workflow service not initialized"
            })
        
        health = workflow_service.check_health()
        all_ok = health.get("workflow_available", False) and health.get("can_import", False)
        
        return JSONResponse(content={
            "healthy": all_ok,
            "details": health,
            "message": "Workflow system is ready" if all_ok else "Workflow system has issues"
        })
        
    except Exception as e:
        logger.error(f"Workflow health check error: {e}")
        return JSONResponse(content={
            "healthy": False,
            "error": str(e),
            "message": "Workflow health check failed"
        })
