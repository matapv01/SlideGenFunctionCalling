"""
SlideGen Backend - Main FastAPI Application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import shutil
import zipfile
import json
import re
import asyncio
from pathlib import Path
from datetime import datetime
from typing import AsyncGenerator

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
            "slides": "GET /api/slides/{project_name}",
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


@app.post("/api/upload-docx-for-stream")
async def upload_docx_for_stream(file: UploadFile = File(...)):
    """Upload DOCX file and return filename for streaming"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only DOCX files accepted")
    
    # Save temp file
    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return JSONResponse(content={"filename": file.filename})


@app.get("/api/upload-docx-stream")
async def upload_docx_stream(filename: str):
    """Stream processing of DOCX file with Server-Sent Events"""
    
    # Validate file
    temp_path = TEMP_DIR / filename
    if not temp_path.exists() or not filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Invalid file")
    
    # Create project name from filename
    project_name = os.path.splitext(filename)[0]
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
    
    # Store temp directory path for cleanup later
    temp_workflow_dir = None
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events for workflow progress"""
        nonlocal temp_workflow_dir
        
        # Queue for events
        event_queue = asyncio.Queue()
        workflow_done = asyncio.Event()
        workflow_error = None
        
        def stream_callback(event_type: str, data: dict):
            """Callback to receive events from workflow"""
            try:
                logger.info(f"🔔 Stream callback: {event_type} - {data}")
                
                # For slide_completed, keep the temp path for real-time access
                if event_type == 'slide_completed' and 'html_path' in data:
                    # Keep the original temp path from workflow
                    # Format: /tmp/slidegen_workflow_xxx/output/html/slide_1.html
                    temp_path = data['html_path']
                    # Store as temp path for frontend to access
                    data['html_path'] = temp_path
                    data['is_temp'] = True
                    logger.info(f"🎯 Streaming temp file: {temp_path}")
                
                # Send all events immediately for real-time streaming
                event_queue.put_nowait((event_type, data))
            except Exception as e:
                logger.error(f"Error in stream callback: {e}")
        
        async def run_workflow():
            """Run workflow in background"""
            nonlocal workflow_error, temp_workflow_dir
            try:
                if not workflow_service or not workflow_service.is_available():
                    raise Exception("Workflow service not available")
                
                # Workflow now returns tuple of (result_zip, temp_dir)
                workflow_result = await workflow_service.process_docx_with_workflow(
                    docx_path=str(temp_path),
                    output_folder=str(output_folder),
                    router_flags=False,
                    callback=stream_callback
                )
                
                if not workflow_result:
                    raise Exception("Workflow did not produce valid output")
                
                # Unpack result
                result_zip, temp_workflow_dir = workflow_result
                logger.info(f"📁 Temp workflow directory: {temp_workflow_dir}")
                logger.info(f"📦 Result ZIP: {result_zip}")
                
                if result_zip and os.path.exists(result_zip):
                    # Extract ZIP to output folder
                    html_folder = output_folder / "html"
                    html_folder.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(result_zip, 'r') as zip_ref:
                        for file_info in zip_ref.infolist():
                            if not file_info.filename.endswith('/') and 'temp_debug' not in file_info.filename:
                                try:
                                    zip_ref.extract(file_info, output_folder)
                                except Exception as e:
                                    logger.warning(f"Error extracting {file_info.filename}: {e}")
                    
                    # Convert slides if converter available
                    if conversion_service and conversion_service.is_available():
                        converted_folder = output_folder / "converted"
                        converted_folder.mkdir(exist_ok=True)
                        conversion_service.convert_slides_batch(html_folder, converted_folder)
                    
                    # Count total slides
                    html_files = list(html_folder.glob("*.html"))
                    total_slides = len(html_files)
                    logger.info(f"📁 Found {total_slides} HTML files")
                    
                    # Emit complete event with temp directory path for cleanup
                    await event_queue.put(('complete', {
                        'project_name': project_name,
                        'total_slides': total_slides,
                        'temp_dir': temp_workflow_dir
                    }))
                else:
                    raise Exception("Workflow did not produce valid output")
                    
            except Exception as e:
                logger.error(f"Workflow error: {e}")
                workflow_error = str(e)
            finally:
                workflow_done.set()
                # Delete uploaded temp file but keep workflow temp directory
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except:
                        pass
                # DON'T delete temp_workflow_dir yet - will be cleaned when user goes to editor
        
        # Start workflow in background
        workflow_task = asyncio.create_task(run_workflow())
        
        try:
            # Stream events
            while not workflow_done.is_set() or not event_queue.empty():
                try:
                    # Wait for event with timeout
                    event_type, data = await asyncio.wait_for(event_queue.get(), timeout=0.5)
                    
                    logger.info(f"📤 Sending SSE: {event_type} - {data}")
                    
                    # Format SSE message
                    event_data = json.dumps(data)
                    yield f"event: {event_type}\ndata: {event_data}\n\n"
                    
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield f": keepalive\n\n"
                    continue
            
            # Check for errors
            if workflow_error:
                error_data = json.dumps({"message": workflow_error})
                yield f"event: error_event\ndata: {error_data}\n\n"
            
        except Exception as e:
            logger.error(f"Error in event generator: {e}")
            error_data = json.dumps({"message": str(e)})
            yield f"event: error_event\ndata: {error_data}\n\n"
        finally:
            # Ensure workflow completes
            try:
                await workflow_task
            except:
                pass
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


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


# ========================== TEMP FILE SERVING ==========================

@app.get("/api/temp-file")
async def serve_temp_file(path: str):
    """Serve file from temporary workflow directory via query parameter"""
    logger.info(f"📂 Serving temp file request: {path}")
    
    # Security: only allow serving from slidegen_workflow_* directories (both Linux and Windows)
    normalized_path = path.replace('\\', '/')
    is_linux_temp = normalized_path.startswith('/tmp/slidegen_workflow_')
    is_windows_temp = 'slidegen_workflow_' in normalized_path and ('Temp' in path or 'temp' in path)
    
    if not (is_linux_temp or is_windows_temp):
        logger.warning(f"⚠️ Access denied for path: {path}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = Path(path)
    if not file_path.exists():
        logger.warning(f"⚠️ File not found: {path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    logger.info(f"✅ Serving temp file: {path}")
    return FileResponse(file_path)


@app.post("/api/cleanup-temp")
async def cleanup_temp_directory(request: Request):
    """Clean up temporary workflow directory when user navigates to editor"""
    try:
        data = await request.json()
        temp_dir = data.get('temp_dir')
        
        if not temp_dir:
            return JSONResponse(content={"success": False, "message": "No temp directory specified"})
        
        # Security: only allow deleting slidegen_workflow_* directories (both Linux and Windows)
        normalized_path = temp_dir.replace('\\', '/')
        is_linux_temp = normalized_path.startswith('/tmp/slidegen_workflow_')
        is_windows_temp = 'slidegen_workflow_' in normalized_path and ('Temp' in temp_dir or 'temp' in temp_dir)
        
        if not (is_linux_temp or is_windows_temp):
            raise HTTPException(status_code=403, detail="Invalid temp directory")
        
        temp_path = Path(temp_dir)
        if temp_path.exists():
            shutil.rmtree(temp_path)
            logger.info(f"🗑️ Cleaned up temp directory: {temp_dir}")
            return JSONResponse(content={"success": True, "message": "Temp directory cleaned"})
        else:
            return JSONResponse(content={"success": False, "message": "Temp directory not found"})
    
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
