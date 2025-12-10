"""
Manual Structure Workflow Endpoint
Streaming endpoint for manual structure-based slide generation
"""
import json
import asyncio
import os
from typing import AsyncGenerator
from fastapi import Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pathlib import Path

from .auth import get_current_user_from_token_param
from .schemas import UserResponse
from .config import TEMP_DIR, OUTPUT_DIR
from .database import save_workflow_to_database


async def generate_from_manual_structure_stream_endpoint(
    session_id: str,
    current_user: UserResponse,
    workflow_service,
    conversion_service,
    logger
):
    """Stream processing of manual structure from structure editor"""
    
    # Load approved structure
    approved_file = TEMP_DIR / f"approved_structure_{session_id}.json"
    if not approved_file.exists():
        logger.error(f"Approved structure not found: {approved_file}")
        raise HTTPException(status_code=404, detail="Approved structure not found")
    
    try:
        with open(approved_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading approved structure: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading structure: {str(e)}")
    
    slide_chunks = data.get('slide_chunks', [])
    document_title = data.get('document_title', 'Untitled')
    
    if not slide_chunks:
        raise HTTPException(status_code=400, detail="No slide chunks found in approved structure")
    
    logger.info(f"📋 Manual structure session: {session_id}")
    logger.info(f"📄 Document title: {document_title}")
    logger.info(f"📊 Total chunks: {len(slide_chunks)}")
    
    # Create project name from title
    project_name = document_title.replace(' ', '_')
    output_folder = OUTPUT_DIR / project_name
    
    # Handle existing project folder
    if output_folder.exists():
        try:
            import shutil
            shutil.rmtree(output_folder)
        except PermissionError:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_name = f"{project_name}_{timestamp}"
            output_folder = OUTPUT_DIR / project_name
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Store temp directory path for cleanup
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
                
                # For slide_completed, use temp path for real-time access
                if event_type == 'slide_completed' and 'html_path' in data:
                    temp_path = data['html_path']
                    data['html_path'] = temp_path
                    data['is_temp'] = True
                    logger.info(f"🎯 Streaming temp file: {temp_path}")
                
                # Send all events immediately
                event_queue.put_nowait((event_type, data))
            except Exception as e:
                logger.error(f"Error in stream callback: {e}")
        
        async def run_workflow():
            """Run workflow in background"""
            nonlocal workflow_error, temp_workflow_dir
            try:
                if not workflow_service or not workflow_service.is_available():
                    raise Exception("Workflow service not available")
                
                # Run manual structure workflow
                workflow_result = await workflow_service.process_manual_structure(
                    slide_chunks=slide_chunks,
                    document_title=document_title,
                    output_folder=str(output_folder),
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
                    
                    import zipfile
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
                    
                    # Save to database
                    project_id = save_workflow_to_database(
                        user_id=current_user.id,
                        project_name=project_name,
                        source_type='manual_structure',
                        source_data={
                            'session_id': session_id,
                            'document_title': document_title,
                            'description': f'Slides from manual structure: {document_title}'
                        },
                        slide_options={'manual_mode': True},
                        output_folder=output_folder
                    )
                    
                    # Emit complete event
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
