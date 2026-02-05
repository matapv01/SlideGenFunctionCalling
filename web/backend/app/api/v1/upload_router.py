from fastapi import File, UploadFile, HTTPException, APIRouter, Form, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
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
from web.backend.app.config import STATIC_DIR, OUTPUT_DIR, TEMP_DIR
from web.backend.app.models import UserResponse
from web.backend.app.api.v1.authentication_router import (
    get_current_active_user, decode_access_token
)
from web.backend.app.resource.database import get_user_by_email
from web.backend.app.application.conversion_service import conversion_service
from web.backend.app.application.slide_service import slide_service
from web.backend.app.application.workflow_service import workflow_service
from web.backend.app.api.v1.slide_generation_router import save_workflow_to_database

router = APIRouter(prefix="/upload", tags=["UPLOAD"])
logger = logging.getLogger("SlideGen-upload")

@router.post("/docx")
async def upload_docx(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Upload and process DOCX file with AI workflow (Protected route)"""
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

                    logger.info("Successfully extracted workflow results")
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


@router.post("/docx-for-stream")
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


@router.post("/docx-for-manual")
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
        from edit_router import structure_sessions
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

@router.get("/docx-stream")
async def upload_docx_stream(
    filename: str = Query(..., description="DOCX filename to process"),
    token: str = Query(..., description="Authentication token (required)")
):
    """Stream processing of DOCX file with Server-Sent Events - Requires Authentication"""
    
    # Required authentication - validate token
    logger.info(f"🔐 Authenticating request with token: {token[:20] if token else 'None'}...")
    
    # Check if token is missing or is the string "null" (JavaScript encodes null as "null")
    if not token or token == "null" or not token.strip():
        logger.error("❌ Authentication failed: No valid token provided")
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in to generate slides."
        )
    
    # Decode and validate token
    try:
        token_data = decode_access_token(token)
        user = get_user_by_email(token_data.email)
        
        if not user or not user.get("is_active"):
            logger.error(f"❌ Authentication failed: User not found or inactive")
            raise HTTPException(
                status_code=401,
                detail="User not found or inactive"
            )
        
        current_user = UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            created_at=user["created_at"],
            is_active=bool(user["is_active"])
        )
        logger.info(f"✅ Authenticated user: {current_user.email}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token. Please log in again."
        )
    
    # Normalize filename for cross-platform compatibility
    safe_filename = os.path.basename(filename)
    safe_filename = Path(safe_filename).name  # Remove any path traversal
    # Replace backslashes with forward slashes (Windows compatibility)
    safe_filename = safe_filename.replace('\\', '/').replace('/', '')
    # Optionally, remove any remaining illegal characters
    safe_filename = re.sub(r'[^\w\-. ]', '', safe_filename)

    temp_path = TEMP_DIR / safe_filename
    if not temp_path.exists() or not safe_filename.lower().endswith('.docx'):
        logger.error(f"DOCX file not found or invalid: {temp_path}")
        raise HTTPException(status_code=400, detail="Invalid file")
    
    # Load slide options
    options_path = TEMP_DIR / f"{safe_filename}.options.json"
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
    project_name = os.path.splitext(safe_filename)[0]
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
                    
                    # Save to database (user is always authenticated now)
                    project_id = save_workflow_to_database(
                        user_id=current_user.id,
                        project_name=project_name,
                        source_type='docx',
                        source_data={
                            'filename': filename,
                            'description': f'Slides generated from {filename}'
                        },
                        slide_options=slide_options,
                        output_folder=output_folder
                    )
                    
                    # Emit complete event with temp directory path for cleanup
                    await event_queue.put(('complete', {
                        'project_name': project_name,
                        'total_slides': total_slides,
                        'temp_dir': temp_workflow_dir,
                        'project_id': project_id
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