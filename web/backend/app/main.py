"""
SlideGen Backend - Main FastAPI Application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
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
    PROJECT_DIR, STATIC_DIR, FRONTEND_DIR, IMAGE_DIR, UPLOAD_DIR, 
    OUTPUT_DIR, TEMP_DIR, CAPTURES_DIR, CORS_ORIGINS, 
    DISABLE_CONVERTER, LOG_LEVEL
)
from .schemas import (
    CaptureSlideRequest, CaptureMultipleSlidesRequest,
    ProjectUploadResponse, ConversionStatusResponse,
    HealthCheckResponse, StructureUpdateRequest, StructureResponse,
    StructureApproveRequest
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
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

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
async def upload_docx_for_stream(
    file: UploadFile = File(...),
    enable_transition_slides: str = Form("true"),
    enable_thank_you_slide: str = Form("true")
):
    """Upload DOCX file and return filename for streaming"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only DOCX files accepted")
    
    # Clean up old temp files first
    try:
        deleted_count = 0
        for old_file in TEMP_DIR.glob("*"):
            if old_file.is_file():
                try:
                    old_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Could not delete {old_file}: {e}")
        if deleted_count > 0:
            logger.info(f"🗑️ Cleaned up {deleted_count} old temp files")
    except Exception as e:
        logger.warning(f"Error cleaning temp directory: {e}")
    
    # Convert string to boolean
    def str_to_bool(value: str) -> bool:
        if isinstance(value, bool):
            return value
        return value.lower() in ('true', '1', 'yes', 'on')
    
    logger.info(f"📥 Received form data:")
    logger.info(f"   - enable_transition_slides (raw): '{enable_transition_slides}' (type: {type(enable_transition_slides)})")
    logger.info(f"   - enable_thank_you_slide (raw): '{enable_thank_you_slide}' (type: {type(enable_thank_you_slide)})")
    
    enable_transition = str_to_bool(enable_transition_slides)
    enable_thank_you = str_to_bool(enable_thank_you_slide)
    
    logger.info(f"🔄 After parsing:")
    logger.info(f"   - enable_transition: {enable_transition}")
    logger.info(f"   - enable_thank_you: {enable_thank_you}")
    
    # Save temp file
    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Save options to JSON file with same name
    import json
    options_path = TEMP_DIR / f"{file.filename}.options.json"
    
    # Delete old options file if exists to avoid caching
    if options_path.exists():
        try:
            options_path.unlink()
            logger.info(f"🗑️ Deleted old options file: {options_path}")
        except Exception as e:
            logger.warning(f"⚠️ Could not delete old options file: {e}")
    
    # Write new options
    options_data = {
        "enable_transition_slides": enable_transition,
        "enable_thank_you_slide": enable_thank_you
    }
    
    try:
        with open(options_path, "w") as f:
            json.dump(options_data, f, indent=2)
        logger.info(f"💾 Successfully saved slide options to {options_path}")
        logger.info(f"📄 File content: {options_data}")
        
        # Verify file was written correctly
        with open(options_path, "r") as f:
            verified = json.load(f)
        logger.info(f"✅ Verified saved options: {verified}")
    except Exception as e:
        logger.error(f"❌ Error saving options: {e}")
    
    return JSONResponse(content={"filename": file.filename})


@app.post("/api/upload-docx-for-manual")
async def upload_docx_for_manual(file: UploadFile = File(...)):
    """Upload DOCX for manual structure editing workflow - Extract plain text for user to manually structure"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only DOCX files accepted")
    
    logger.info(f"📝 Manual workflow: Processing {file.filename}")
    
    # Save temp file
    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Extract plain text from DOCX using python-docx
        from docx import Document
        
        doc = Document(temp_path)
        
        # Extract all paragraphs with their positions
        full_text = ""
        paragraphs_data = []
        
        for idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if text:  # Skip empty paragraphs
                start_pos = len(full_text)
                full_text += text + "\n\n"
                end_pos = len(full_text)
                
                paragraphs_data.append({
                    "index": idx,
                    "text": text,
                    "start_pos": start_pos,
                    "end_pos": end_pos
                })
        
        logger.info(f"✅ Extracted {len(paragraphs_data)} paragraphs from document")
        logger.info(f"� Total text length: {len(full_text)} characters")
        
        # Create session
        import uuid
        session_id = str(uuid.uuid4())
        
        # Store in structure_sessions with EMPTY structure for user to build
        structure_sessions[session_id] = {
            'document_title': file.filename.replace('.docx', ''),
            'document_text': full_text,  # Full plain text
            'paragraphs': paragraphs_data,  # Paragraph metadata
            'document_structure': [],  # Empty - user will build this
            'docx_file': str(temp_path),
            'filename': file.filename
        }
        
        logger.info(f"✅ Created manual session: {session_id}")
        
        return JSONResponse(content={
            "success": True,
            "session_id": session_id,
            "document_title": file.filename.replace('.docx', ''),
            "text_length": len(full_text),
            "paragraph_count": len(paragraphs_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Error in manual workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
    finally:
        # Keep temp file for now (will be deleted after workflow completes)
        pass


@app.get("/api/upload-docx-stream")
async def upload_docx_stream(filename: str):
    """Stream processing of DOCX file with Server-Sent Events"""
    
    # Validate file
    temp_path = TEMP_DIR / filename
    if not temp_path.exists() or not filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Invalid file")
    
    # Load slide options
    options_path = TEMP_DIR / f"{filename}.options.json"
    slide_options = {
        "enable_transition_slides": True,
        "enable_thank_you_slide": True
    }
    if options_path.exists():
        try:
            with open(options_path, "r") as f:
                slide_options = json.load(f)
            logger.info(f"📋 Loaded slide options from file: {slide_options}")
            logger.info(f"   - Transition slides: {slide_options.get('enable_transition_slides')}")
            logger.info(f"   - Thank you slide: {slide_options.get('enable_thank_you_slide')}")
        except Exception as e:
            logger.warning(f"⚠️ Could not load slide options: {e}")
    else:
        logger.warning(f"⚠️ Options file not found: {options_path}")
    
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
                    callback=stream_callback,
                    slide_options=slide_options
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


# ========================== STRUCTURE EDITOR ENDPOINTS ==========================

# In-memory storage for structure editor sessions
# TODO: Replace with Redis for production
structure_sessions = {}

@app.get("/api/structure/current")
async def get_current_structure(session_id: str):
    """Get current document structure and text for editing"""
    logger.info(f"📋 Getting structure for session: {session_id}")
    
    # Check if session exists
    if session_id not in structure_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = structure_sessions[session_id]
    
    return JSONResponse(content={
        "document_title": session_data.get("document_title", "Untitled"),
        "document_text": session_data.get("document_text", ""),  # Full plain text for selection
        "document_structure": session_data.get("document_structure", []),
        "can_edit": True
    })


@app.put("/api/structure/update")
async def update_structure(request: StructureUpdateRequest):
    """Update document structure in session"""
    logger.info(f"💾 Updating structure for session: {request.session_id}")
    
    # Update session in memory
    if request.session_id not in structure_sessions:
        structure_sessions[request.session_id] = {}
    
    structure_sessions[request.session_id]["document_structure"] = request.document_structure
    
    # EXTRACT document_title from intro_slide
    document_title = "Untitled Document"
    if request.intro_slide:
        document_title = request.intro_slide.content or "Untitled Document"
        logger.info(f"📌 Document title: {document_title}")
    
    # PREPEND intro_slide if exists
    raw_structure = []
    if request.intro_slide:
        raw_structure.append(request.intro_slide.dict())
    
    # Add document structure
    raw_structure.extend([node.dict() for node in request.document_structure])
    
    # MERGE title + content nodes BEFORE saving
    def merge_title_content_nodes(nodes):
        """Merge consecutive title/content node pairs into single nodes"""
        merged = []
        i = 0
        
        while i < len(nodes):
            node = nodes[i]
            node_dict = node if isinstance(node, dict) else node
            
            # Check if this is a title node (has title, empty/missing content)
            has_title = node_dict.get('title', '').strip() != ''
            has_no_content = not node_dict.get('content', '').strip()
            
            # Check if next node is content node (has content, empty/missing title)
            is_next_content = False
            if i + 1 < len(nodes):
                next_node = nodes[i + 1]
                next_dict = next_node if isinstance(next_node, dict) else next_node
                has_no_title = not next_dict.get('title', '').strip()
                has_content = next_dict.get('content', '').strip() != ''
                same_level = next_dict.get('level') == node_dict.get('level')
                is_next_content = has_no_title and has_content and same_level
            
            # Merge if current is title and next is content
            if has_title and has_no_content and is_next_content:
                next_node = nodes[i + 1]
                next_dict = next_node if isinstance(next_node, dict) else next_node
                merged_node = {
                    'level': node_dict.get('level'),
                    'title': node_dict.get('title'),
                    'content': next_dict.get('content'),
                    'children': merge_title_content_nodes(node_dict.get('children', [])),
                    'is_transition': node_dict.get('is_transition', False)
                }
                merged.append(merged_node)
                i += 2  # Skip next node as it's been merged
            else:
                # Keep node as-is, but recurse into children
                merged_node = {
                    'level': node_dict.get('level'),
                    'title': node_dict.get('title', ''),
                    'content': node_dict.get('content', ''),
                    'children': merge_title_content_nodes(node_dict.get('children', [])),
                    'is_transition': node_dict.get('is_transition', False)
                }
                merged.append(merged_node)
                i += 1
        
        return merged
    
    # SAVE TO FILE with merged format
    try:
        # Ensure TEMP_DIR exists
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        
        structure_file = TEMP_DIR / f"structure_{request.session_id}.json"
        
        # Merge title/content pairs
        merged_structure = merge_title_content_nodes(raw_structure)
        
        structure_data = {
            "session_id": request.session_id,
            "document_title": document_title,  # Save title here!
            "document_structure": merged_structure
        }
        
        # Save to file
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(structure_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Structure updated: {request.session_id} ({len(raw_structure)} nodes → {len(merged_structure)} merged)")
        logger.info(f"📁 Saved to file: {structure_file}")
        
    except Exception as e:
        logger.error(f"Error saving structure to file: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return JSONResponse(content={"success": True})


@app.post("/api/structure/approve")
async def approve_structure(request: StructureApproveRequest):
    """
    Approve structure and generate slide chunks using chunk_organizer logic.
    Returns State-compatible output for downstream slide generation.
    """
    logger.info(f"✅ Approving structure for session: {request.session_id}")
    
    THRESHOLD_CHAR_LIMIT = 1000
    
    try:
        # ======================== Load Structure ========================
        structure_file = TEMP_DIR / f"structure_{request.session_id}.json"
        
        if not structure_file.exists():
            logger.warning(f"No structure found for session: {request.session_id}")
            return JSONResponse(content={
                "success": False,
                "message": "No structure found for this session"
            }, status_code=404)
        
        with open(structure_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        document_structure = data.get('document_structure', [])
        document_title = data.get('document_title', 'Untitled Document')
        
        logger.info(f"📋 Loaded structure: {len(document_structure)} nodes")
        logger.info(f"📄 Document title: {document_title}")
        
        # ======================== Extract Special Slides ========================
       
        # Extract intro slide from level 0
        intro_slide = None
        intro_node = None
        filtered_structure = []
        
        for node in document_structure:
            if node.get('level') == 0:
                intro_node = node
            else:
                filtered_structure.append(node)
        
        if intro_node:
            intro_slide = f"INTRO SLIDE\n\nTitle: {intro_node.get('content', '')}"
            logger.info(f"✅ Extracted intro slide from level 0: {intro_node.get('content')}")
        else:
            intro_slide = f"INTRO SLIDE\n\nTitle: {document_title}"
            logger.info(f"✅ Extracted intro slide from level 0: {document_title}")
        
        # Extract thank you slide (hybrid approach)
        thank_you_slide = None
        thank_you_node = None
        
        if filtered_structure and len(filtered_structure) > 0:
            last_node = filtered_structure[-1]
            # Check if last node title contains any thank you keyword
            thank_you_keywords = ['thank', 'thanks', 'thank you', 'cảm ơn', 'cam on']
            if any(keyword in last_node.get('title', '').lower() for keyword in thank_you_keywords):
                thank_you_node = last_node
                filtered_structure = filtered_structure[:-1]  # Remove from structure
                thank_you_slide = f"THANK YOU SLIDE\n\n{thank_you_node.get('title', '')}\n\n{thank_you_node.get('content', '')}"
                logger.info(f"✅ Extracted thank you slide from last node: {thank_you_node.get('title')}")
        
        # Fallback to default thank you
        if not thank_you_slide:
            thank_you_slide = "THANK YOU SLIDE\n\nThank you for your attention!"
            logger.info(f"📝 Using default thank you slide")
        
        document_structure = filtered_structure
        
        # ======================== Renumber Structure ========================
        
        def _add_numbering_recursively(nodes, counters=None, parent_level=0):
            counters = [0] * 6 if counters is None else counters
            for node in nodes:
                # For transition nodes: peek at next index (increment then decrement)
                if node.get('is_transition') == True:
                    # Temporarily increment to get the "next" index
                    counters[parent_level] += 1
                    for i in range(parent_level + 1, len(counters)):
                        counters[i] = 0
                    
                    # Assign index
                    index = ".".join(map(str, counters[:parent_level + 1]))
                    node['index'] = index
                    node['numbered_title'] = f"{index}. {node['title']}"
                    node['level'] = parent_level + 1
                    
                    # Decrement back (so next content node gets same index)
                    counters[parent_level] -= 1
                else:
                    # For content nodes: normal increment
                    counters[parent_level] += 1
                    for i in range(parent_level + 1, len(counters)):
                        counters[i] = 0
                    
                    # Assign index
                    index = ".".join(map(str, counters[:parent_level + 1]))
                    node['index'] = index
                    node['numbered_title'] = f"{index}. {node['title']}"
                    node['level'] = parent_level + 1
                
                if node.get('children'):
                    _add_numbering_recursively(node['children'], list(counters), parent_level + 1)
            return nodes
        
        renumbered_structure = _add_numbering_recursively(document_structure)
        logger.info(f"✅ Renumbered structure")
        
        # ======================== Generate Slides ========================
        
        final_slides_content = []
        final_slides_positions = []
        final_slides_context_maps = []
        final_slides_types = []
        
        # Add intro slide first
        if intro_slide:
            final_slides_content.append(intro_slide)
            final_slides_positions.append(['0'])
            final_slides_context_maps.append("INTRO SLIDE")
            final_slides_types.append('intro')
            logger.info("✅ Added intro slide")
        
        # Helper functions
        def _create_context_map(outline_nodes, active_indices):
            map_lines = []
            # Ensure active_indices is a list
            if not isinstance(active_indices, list):
                active_indices = [active_indices]
            
            def _generate(nodes, indent):
                for node in nodes:
                    node_index = node.get("index", "")
                    # Check if this node's index is in active_indices
                    marker = " <--- YOU ARE HERE" if node_index in active_indices else ""
                    map_lines.append(f'{"  " * indent}{node_index}. {node.get("title", "")}{marker}')
                    if node.get("children"):
                        _generate(node["children"], indent + 1)
            _generate(outline_nodes, 0)
            return "\n".join(map_lines)
        
        def _render_slide_content(group_header, items):
            parts = [group_header] if group_header else []
            if len(items) > 1:
                for item in items:
                    parts.append(f"\n\t- {item.get('title', '')}")
                    if item.get('content'):
                        indented = "\n\t  ".join(item['content'].splitlines())
                        parts.append(f"\t  {indented}")
            else:
                item = items[0]
                parts.append(f"\n{item.get('numbered_title', item.get('title', ''))}")
                if item.get('content'):
                    parts.append(f"{item['content']}")
            return "\n".join(parts)
        
        def _create_slides_from_leaves(parent, leaves):
            if not leaves:
                return
            buffer = []
            header = parent.get('numbered_title', '')
            for item in leaves:
                tentative_buffer = buffer + [item]
                if len(_render_slide_content(header, tentative_buffer)) > THRESHOLD_CHAR_LIMIT and buffer:
                    content = _render_slide_content(header, buffer)
                    pos = [i.get('index', '') for i in buffer]
                    final_slides_content.append(content)
                    final_slides_positions.append(pos)
                    final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))
                    final_slides_types.append('content')
                    buffer = [item]
                else:
                    buffer.append(item)
            if buffer:
                content = _render_slide_content(header, buffer)
                pos = [i.get('index', '') for i in buffer]
                final_slides_content.append(content)
                final_slides_positions.append(pos)
                final_slides_context_maps.append(_create_context_map(renumbered_structure, pos))
                final_slides_types.append('content')
        
        def _traverse_dfs(nodes, is_root_level=False):
            for node in nodes:
                try:
                    # Create transition slide ONLY if is_transition=true
                    if is_root_level and node.get('is_transition') == True:
                        transition_content = f"TRANSITION SLIDE\n\n{node.get('numbered_title', node.get('title', ''))}"
                        pos = [f"{node.get('index', '')}.T"]
                        final_slides_content.append(transition_content)
                        final_slides_positions.append(pos)
                        
                        node_index_list = [node.get('index', '')]
                        logger.info(f"🔍 Creating transition context map with indices: {node_index_list} (type: {type(node_index_list)})")
                        context_map = _create_context_map(renumbered_structure, node_index_list)
                        final_slides_context_maps.append(context_map)
                        final_slides_types.append('transition')
                        logger.info(f"✅ Created transition slide: {node.get('numbered_title', '')}")
                    
                    # Process content ONLY for non-transition nodes (is_transition=False)
                    if node.get("content") and node.get('is_transition') != True:
                        pos = [node.get('index', '')]
                        final_slides_content.append(_render_slide_content("", [node]))
                        final_slides_positions.append(pos)
                        
                        logger.info(f"🔍 Creating content context map with indices: {pos} (type: {type(pos)})")
                        context_map = _create_context_map(renumbered_structure, pos)
                        final_slides_context_maps.append(context_map)
                        final_slides_types.append('content')
                    
                    # Process children
                    leaves = [child for child in node.get("children", []) if not child.get("children")]
                    if leaves:
                        _create_slides_from_leaves(node, leaves)
                    
                    sub_trees = [child for child in node.get("children", []) if child.get("children")]
                    if sub_trees:
                        _traverse_dfs(sub_trees, is_root_level=False)
                        
                except Exception as e:
                    logger.error(f"❌ Error in _traverse_dfs for node {node.get('title')}: {e}")
                    logger.error(f"   Node data: {node}")
                    import traceback
                    logger.error(traceback.format_exc())
                    raise
        
        # Traverse structure and create content slides
        _traverse_dfs(renumbered_structure, is_root_level=True)
        
        # Add thank you slide at the end
        if thank_you_slide:
            final_slides_content.append(thank_you_slide)
            final_slides_positions.append(['999'])
            final_slides_context_maps.append("THANK YOU SLIDE")
            final_slides_types.append('thank_you')
            logger.info("✅ Added thank you slide")
        
        logger.info(f"✅ Generated {len(final_slides_content)} slides:")
        logger.info(f"   - Intro: {final_slides_types.count('intro')}")
        logger.info(f"   - Transitions: {final_slides_types.count('transition')}")
        logger.info(f"   - Content: {final_slides_types.count('content')}")
        logger.info(f"   - Thank You: {final_slides_types.count('thank_you')}")
        
        # ======================== Sort Slides ========================
        
        def _get_version_key(pos_str):
            # Type safety: ensure pos_str is a string
            if isinstance(pos_str, (list, tuple)):
                logger.warning(f"⚠️ _get_version_key received {type(pos_str)}: {pos_str}, converting to string")
                pos_str = str(pos_str[0]) if pos_str else '0'
            
            pos_str = str(pos_str)  # Force to string
            
            if pos_str == '0':
                return (0,)
            if pos_str == '999':
                return (999999,)
            if pos_str.endswith('.T'):
                # Transition slides: place before content of same section
                parts = pos_str[:-2].split('.')
                return tuple(int(p) for p in parts) + (0,)  # e.g. "1.T" → (1, 0)
            
            # Content slides: place after transitions
            parts = pos_str.split('.')
            return tuple(int(p) for p in parts) + (1,)  # e.g. "1" → (1, 1)
        
        combined = list(zip(final_slides_content, final_slides_positions, final_slides_context_maps, final_slides_types))
        
        def sort_key(slide_data):
            return _get_version_key(slide_data[1][0]) if slide_data[1] else ()
        
        sorted_combined = sorted(combined, key=sort_key)
        
        if sorted_combined:
            sorted_chunks, sorted_positions, sorted_maps, sorted_types = zip(*sorted_combined)
        else:
            sorted_chunks, sorted_positions, sorted_maps, sorted_types = [], [], [], []
        
        logger.info(f"✅ Sorted {len(sorted_chunks)} slides")
        
        # Log samples
        for i, (chunk, slide_type) in enumerate(list(zip(sorted_chunks, sorted_types))[:3]):
            logger.info(f"\n--- Sample Slide {i+1} ({slide_type}) ---\n{chunk[:200]}...\n")
        
        # ======================== Save Results to File ========================
        
        try:
            # Save approved result to file for debugging/monitoring
            approved_file = TEMP_DIR / f"approved_structure_{request.session_id}.json"
            
            result_data = {
                "success": True,
                "message": "Structure approved successfully",
                "session_id": request.session_id,
                "document_title": document_title,
                "document_outline": renumbered_structure,
                "slide_chunks": list(sorted_chunks),
                "slide_positions": list(sorted_positions),
                "slide_context_maps": list(sorted_maps),
                "slide_types": list(sorted_types)
            }
            
            with open(approved_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved approved result to: {approved_file}")
            
        except Exception as e:
            logger.error(f"⚠️ Error saving approved result to file: {e}")
        
        # ======================== Return State Output ========================
        
        return JSONResponse(content={
            "success": True,
            "message": "Structure approved successfully",
            "session_id": request.session_id,
            "document_title": document_title,
            "document_outline": renumbered_structure,
            "slide_chunks": list(sorted_chunks),
            "slide_positions": list(sorted_positions),
            "slide_context_maps": list(sorted_maps),
            "slide_types": list(sorted_types)
        })
        
    except Exception as e:
        logger.error(f"Error approving structure: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return JSONResponse(content={
            "success": False,
            "message": f"Error processing structure: {str(e)}"
        }, status_code=500)


@app.post("/api/structure/test-session")
async def create_test_session():
    """Create test session with sample structure for testing"""
    import uuid
    session_id = str(uuid.uuid4())
    
    # Sample structure
    structure_sessions[session_id] = {
        "document_title": "Test Document - Manual Structure Editor",
        "document_structure": [
            {
                "level": 1,
                "title": "Giới thiệu",
                "content": "Đây là phần giới thiệu của tài liệu. Nội dung này khá dài để test tính năng split. " * 50,
                "children": [
                    {
                        "level": 2,
                        "title": "Bối cảnh",
                        "content": "Nội dung về bối cảnh dự án.",
                        "children": []
                    },
                    {
                        "level": 2,
                        "title": "Mục tiêu",
                        "content": "Mục tiêu của dự án là xây dựng hệ thống tạo slide tự động.",
                        "children": []
                    }
                ]
            },
            {
                "level": 1,
                "title": "Phương pháp",
                "content": "Mô tả các phương pháp được sử dụng trong dự án.",
                "children": [
                    {
                        "level": 2,
                        "title": "Công nghệ",
                        "content": "Sử dụng Python, FastAPI, React.",
                        "children": []
                    }
                ]
            },
            {
                "level": 1,
                "title": "Kết luận",
                "content": "Tóm tắt các kết quả đạt được.",
                "children": []
            }
        ]
    }
    
    logger.info(f"✅ Created test session: {session_id}")
    
    return JSONResponse(content={
        "success": True,
        "session_id": session_id,
        "redirect_url": f"/frontend/structure-editor.html?session={session_id}"
    })


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
