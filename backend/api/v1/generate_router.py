# File: backend/api/v1/generate_router.py

import os
import shutil
import json
import logging
import asyncio
from typing import AsyncGenerator, Optional
from pathlib import Path
from datetime import datetime
from backend.api.schemas.generate_schema import (
    IdeaStructureRequest, IdeaStructureResponse, 
    DocxPrepareResponse, ManualSessionResponse
)
from backend.api.schemas.auth_schema import UserResponse
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

# Config & Domain
from backend.config import TEMP_DIR, OUTPUT_DIR

# Dependencies
from backend.api.dependencies import (
    get_current_active_user,
    get_current_user_from_token_param,
    get_project_service,
    get_structure_service,
    get_slide_service,
    get_slidegen_workflow_service,
    get_idea_service
)

# Services
from backend.application.services.project_service import ProjectService
from backend.application.services.structure_service import StructureService
from backend.application.services.slide_service import SlideService
from backend.application.services.slidegen_workflow_service import SlideGenWorkflowService
from backend.application.services.idea_service import IdeaService

router = APIRouter(prefix="/generate", tags=["GENERATE"])
logger = logging.getLogger("SlideGen-Generation")


def _cleanup_temp_dir():
    """Helper to clean temp files"""
    try:
        if not TEMP_DIR.exists(): return
        for old_file in TEMP_DIR.glob("*"):
            if old_file.is_file():
                try: old_file.unlink()
                except: pass
    except: pass

def prepare_output_folder(name: str):
    """Helper to create unique output folder"""
    safe_name = name.replace(' ', '_')
    folder = OUTPUT_DIR / safe_name
    if folder.exists():
        folder = OUTPUT_DIR / f"{safe_name}_{int(datetime.now().timestamp())}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def sanitize_event_data(event_type: str, data: dict):
    """Helper to mark temp files for frontend viewer"""
    new_data = data.copy()
    if event_type == 'slide_completed':
        if 'html_path' in new_data: new_data['is_temp'] = True
        if 'image_path' in new_data: new_data['is_temp'] = True
    return new_data

# ==========================================
# 1. GENERATE FROM FILE (DOCX)
# ==========================================


@router.post("/docx")
async def generate_from_docx_normal(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_active_user),
    project_service: ProjectService = Depends(get_project_service),
    slide_service: SlideService = Depends(get_slide_service),
    slidegen_workflow_service: SlideGenWorkflowService = Depends(get_slidegen_workflow_service)
):
    """
    [Synchronous] Upload DOCX -> Wait -> Return Slides JSON
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Chỉ chấp nhận tệp DOCX")

    # 1. Setup paths
    project_name = os.path.splitext(file.filename)[0]
    output_folder = prepare_output_folder(project_name)
    
    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        # 2. Run Workflow
        logger.info(f"🤖 Processing DOCX: {file.filename}")
        if not slidegen_workflow_service.is_available():
            raise HTTPException(503, "Dịch vụ workflow không khả dụng")

        output_folder_path = await slidegen_workflow_service.process_docx(
            docx_path=str(temp_path),
            output_folder=str(output_folder),
            router_flags=False
        )

        if not output_folder_path:
            raise HTTPException(500, "Workflow thất bại")

        # 3. Import Project
        project_service.import_project_from_workflow(
            user_id=current_user.id,
            project_name=project_name,
            source_type='docx',
            source_data={'filename': file.filename},
            slide_options={},
            output_folder=output_folder
        )

        # 4. Build Response
        slides = slide_service.build_slides_from_output(str(output_folder))
        return JSONResponse({"slides": slides, "project_name": project_name})

    except Exception as e:
        logger.error(f"DOCX Upload failed: {e}")
        raise HTTPException(500, str(e))
    finally:
        if temp_path.exists(): temp_path.unlink()


@router.post("/docx/prepare-stream", response_model=DocxPrepareResponse)
async def prepare_docx_stream(
    file: UploadFile = File(...),
    enable_transition_slides: str = Form("true"),
    enable_thank_you_slide: str = Form("true")
):
    """
    [Step 1 Stream] Upload DOCX & Save Options -> Return Filename
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Chỉ chấp nhận tệp DOCX")

    _cleanup_temp_dir()

    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f: f.write(await file.read())

    options = {
        "enable_transition_slides": enable_transition_slides.lower() in ('true', '1', 'yes', 'on'),
        "enable_thank_you_slide": enable_thank_you_slide.lower() in ('true', '1', 'yes', 'on')
    }
    with open(TEMP_DIR / f"{file.filename}.options.json", "w") as f:
        json.dump(options, f)

    return {"filename": file.filename}


@router.get("/docx/stream")
async def stream_docx_generation(
    filename: str = Query(..., description="DOCX filename"),
    current_user: UserResponse = Depends(get_current_user_from_token_param),
    project_service: ProjectService = Depends(get_project_service),
    slidegen_workflow_service: SlideGenWorkflowService = Depends(get_slidegen_workflow_service)
):
    """
    [Step 2 Stream] SSE Generation for DOCX
    """
    temp_path = TEMP_DIR / os.path.basename(filename)
    if not temp_path.exists(): raise HTTPException(400, "Tệp không tồn tại hoặc đã hết hạn")

    # Load options
    options_path = TEMP_DIR / f"{filename}.options.json"
    slide_options = {}
    if options_path.exists():
        with open(options_path, "r") as f: slide_options = json.load(f)

    project_name = os.path.splitext(filename)[0]
    output_folder = prepare_output_folder(project_name)

    async def event_generator():
        queue = asyncio.Queue()
        
        def callback(event_type, data):
            safe_data = sanitize_event_data(event_type, data)
            queue.put_nowait((event_type, safe_data))

        async def run_bg():
            res = await slidegen_workflow_service.process_docx(
                docx_path=str(temp_path),
                output_folder=str(output_folder),
                router_flags=False,
                callback=callback,
                slide_options=slide_options
            )
            
            if not res:
                await queue.put(('error_event', {'message': "Workflow failed"}))
                return

            pid = project_service.import_project_from_workflow(
                user_id=current_user.id,
                project_name=project_name,
                source_type='docx',
                source_data={'filename': filename},
                slide_options=slide_options,
                output_folder=output_folder
            )

            # Lấy số lượng slide thực tế từ kết quả workflow thay vì slide_options
            actual_slide_count = 0
            if os.path.exists(output_folder / "html"):
                actual_slide_count = len(list((output_folder / "html").glob("*.html")))

            workflow_temp_dir = str(output_folder)

            await queue.put(('complete', {
                'project_id': pid,
                'project_name': project_name,        # Frontend cần cái này
                'total_slides': actual_slide_count, # Hoặc lấy số lượng thực tế
                'temp_dir': workflow_temp_dir       # Frontend cần cái này để cleanup
            }))

        asyncio.create_task(run_bg())

        # Common streaming loop
        while True:
            try:
                ev = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield f"event: {ev[0]}\ndata: {json.dumps(ev[1])}\n\n"
                if ev[0] in ['complete', 'error_event']: break
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
        
        # Cleanup input file after stream
        if temp_path.exists(): temp_path.unlink()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/docx/manual-session", response_model=ManualSessionResponse)
async def create_manual_session_from_docx(
    file: UploadFile = File(...),
    structure_service: StructureService = Depends(get_structure_service)
):
    """
    Upload DOCX -> Parse Text -> Create Editing Session for Manual Mode
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Chỉ chấp nhận tệp DOCX")

    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f: f.write(await file.read())

    try:
        from docx import Document
        doc = Document(temp_path)
        full_text = ""
        paragraphs_data = []
        for idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if text:
                start_pos = len(full_text)
                full_text += text + "\n\n"
                paragraphs_data.append({
                    "index": idx, "text": text,
                    "start_pos": start_pos, "end_pos": len(full_text)
                })

        session_id = structure_service.create_session(
            filename=file.filename,
            full_text=full_text,
            paragraphs=paragraphs_data,
            docx_path=str(temp_path)
        )

        return {
        "success": True,
        "session_id": session_id,
        "document_title": file.filename.replace('.docx', ''),
        }
    except Exception as e:
        logger.error(f"Manual upload error: {e}")
        raise HTTPException(500, str(e))


# ==========================================
# 2. GENERATE FROM IDEA (AI)
# ==========================================


@router.post("/idea/structure", response_model=IdeaStructureResponse)
async def generate_idea_structure(
    request: IdeaStructureRequest,
    idea_service: IdeaService = Depends(get_idea_service)
):
    """Step 1 Idea: Generate structure from prompt"""
    data = request.model_dump()
    try:
        return await idea_service.generate_structure(
            title=data.get('title', '').strip(),
            prompt=data.get('prompt', '').strip(),
            content_length=data.get('content_length', 'standard'),
            enable_transition=data.get('enable_transition_slides', True),
            enable_thank_you=data.get('enable_thank_you_slide', True)
        )
    except Exception as e:
        logger.error(f"Idea structure error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/idea/stream")
async def stream_idea_generation(
    session_id: str = Query(...),
    current_user: UserResponse = Depends(get_current_user_from_token_param),
    project_service: ProjectService = Depends(get_project_service),
    slidegen_workflow_service: SlideGenWorkflowService = Depends(get_slidegen_workflow_service)
):
    """Step 2 Idea: SSE Generation"""
    file_path = TEMP_DIR / f"idea_{session_id}.json"
    if not file_path.exists(): raise HTTPException(400, "Phiên không hợp lệ")
    
    with open(file_path, 'r', encoding='utf-8') as f: idea_data = json.load(f)
    
    title = idea_data.get('title', 'Untitled')
    output_folder = prepare_output_folder(f"idea_{session_id}")

    async def event_generator():
        queue = asyncio.Queue()
        
        def callback(event_type, data):
            safe_data = sanitize_event_data(event_type, data)
            queue.put_nowait((event_type, safe_data))

        async def run_bg():
            res = await slidegen_workflow_service.process_chunks(
                slide_chunks=idea_data.get('slide_chunks', []),
                title=title,
                output_folder=str(output_folder),
                callback=callback,
                slide_options={
                    'enable_transition_slides': idea_data.get('enable_transition_slides'),
                    'enable_thank_you_slide': idea_data.get('enable_thank_you_slide')
                }
            )
            
            if not res:
                await queue.put(('error_event', {'message': "Workflow failed"}))
                return

            pid = project_service.import_project_from_workflow(
                user_id=current_user.id,
                project_name=f"idea_{session_id}",
                source_type='idea',
                source_data=idea_data,
                slide_options={},
                output_folder=output_folder
            )

            workflow_temp_dir = str(output_folder)

            await queue.put(('complete', {
                'project_id': pid,
                'project_name': f"idea_{session_id}",
                'total_slides': len(idea_data.get('slide_chunks', [])),
                'temp_dir': workflow_temp_dir
            }))

        asyncio.create_task(run_bg())

        while True:
            try:
                ev = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield f"event: {ev[0]}\ndata: {json.dumps(ev[1])}\n\n"
                if ev[0] in ['complete', 'error_event']: break
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ==========================================
# 3. GENERATE FROM MANUAL STRUCTURE
# ==========================================


@router.get("/manual/stream")
async def stream_manual_generation(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user_from_token_param),
    project_service: ProjectService = Depends(get_project_service),
    slidegen_workflow_service: SlideGenWorkflowService = Depends(get_slidegen_workflow_service)
):
    """Step 2 Manual: SSE Generation"""
    file_path = TEMP_DIR / f"approved_structure_{session_id}.json"
    if not file_path.exists(): raise HTTPException(404, "Không tìm thấy cấu trúc")
    
    with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
    
    title = data.get('document_title', 'Untitled')
    output_folder = prepare_output_folder(title)

    async def event_generator():
        queue = asyncio.Queue()
        
        def callback(event_type, data):
            safe_data = sanitize_event_data(event_type, data)
            queue.put_nowait((event_type, safe_data))

        async def run_bg():
            res = await slidegen_workflow_service.process_chunks(
                slide_chunks=data.get('slide_chunks', []),
                document_title=title,
                output_folder=str(output_folder),
                callback=callback
            )
            
            if not res: 
                await queue.put(('error_event', {'message': "Workflow failed"}))
                return

            pid = project_service.import_project_from_workflow(
                user_id=current_user.id,
                project_name=title,
                source_type='manual_structure',
                source_data={'session_id': session_id, 'title': title},
                slide_options={'manual_mode': True},
                output_folder=output_folder
            )

            workflow_temp_dir = str(output_folder)

            await queue.put(('complete', {
                'project_id': pid,
                'project_name': title,
                'total_slides': len(data.get('slide_chunks', [])),
                'temp_dir': workflow_temp_dir
            }))

        asyncio.create_task(run_bg())
        
        while True:
            try:
                ev = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield f"event: {ev[0]}\ndata: {json.dumps(ev[1])}\n\n"
                if ev[0] in ['complete', 'error_event']: break
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")