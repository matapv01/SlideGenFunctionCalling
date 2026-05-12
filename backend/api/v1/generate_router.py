# File: backend/api/v1/generate_router.py

import os
import json
import logging
import asyncio
import re
from typing import AsyncGenerator, Optional
from pathlib import Path
from datetime import datetime
from backend.api.schemas.generate_schema import (
    IdeaStructureRequest, IdeaStructureResponse, IdeaStructureDetailResponse, IdeaStructureUpdateRequest,
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
    get_idea_service,
    get_subscription_service,
    get_conversion_service
)
from backend.application.services.subscription_service import SubscriptionService
from backend.application.services.conversion_service import ConversionService
from backend.infrastructure.database.repositories.sqlite_user_repo import SqliteUserRepository
from backend.api.rate_limiting import idea_structure_rate_limiter, idea_stream_rate_limiter
from backend.api.constants import EventTypes, SourceTypes, FilePatterns
from backend.utils.session_utils import SessionManager

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


def _check_docx_slide_limit(temp_path, subscription_service, user):
    """Estimate slide count from DOCX and validate subscription limits."""
    try:
        from docx import Document
        doc = Document(temp_path)
        slide_count = 0
        for paragraph in doc.paragraphs:
            if paragraph.style.name.startswith('Heading'):
                slide_count += 1
        slide_count = max(slide_count, len(doc.paragraphs) // 10, 1)
        subscription_service.check_feature_access(user, "docx_upload", slide_count=slide_count)
    except Exception as e:
        logger.warning(f"Could not estimate slide count: {e}")
        subscription_service.check_feature_access(user, "docx_upload", slide_count=25)


def _check_pdf_slide_limit(temp_path, subscription_service, user):
    """Estimate PDF slide count (best effort) and validate subscription limits."""
    try:
        size_bytes = os.path.getsize(temp_path)
        approx_slides = max(1, min(50, int(size_bytes // 300000)))
        subscription_service.check_feature_access(user, "docx_upload", slide_count=approx_slides)
    except Exception as e:
        logger.warning(f"Could not estimate PDF slide count: {e}")
        subscription_service.check_feature_access(user, "docx_upload", slide_count=25)

def prepare_output_folder(name: str):
    """Helper to create unique output folder"""
    raw_name = str(name or "Untitled")
    raw_name = re.sub(r"[\x00-\x1f\x7f]", " ", raw_name)
    raw_name = re.sub(r"[\\/:*?\"<>|]", " ", raw_name)
    safe_name = re.sub(r"\s+", "_", raw_name).strip("._")
    if not safe_name:
        safe_name = "Untitled"

    if len(safe_name) > 120:
        safe_name = safe_name[:120].rstrip("._")

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


def ensure_converted_slides(output_folder: Path, conversion_service: Optional[ConversionService]) -> None:
    """Best-effort conversion pass to ensure converted HTML exists for import/view."""
    if conversion_service is None:
        return

    base_output = output_folder / "output"
    html_folder = (base_output / "html") if (base_output / "html").exists() else (output_folder / "html")

    if not html_folder.exists():
        logger.warning(f"Conversion skipped: HTML folder not found at {html_folder}")
        return

    converted_folder = output_folder / "converted"
    converted_folder.mkdir(parents=True, exist_ok=True)

    result = conversion_service.convert_slides_batch(html_folder, converted_folder)
    logger.info(
        "Idea/manual conversion batch complete: %s success, %s failed",
        len(result.get("success", [])),
        len(result.get("failed", []))
    )


def _to_idea_text(value: Optional[str], fallback: str = "") -> str:
    if value is None:
        return fallback
    txt = str(value).strip()
    return txt if txt else fallback


def _parse_intro_title_subtitle(raw_content: str, fallback_title: str) -> tuple[str, str]:
    """
    Parse intro content formatted like:
      Title: ...\nSubtitle: ...
    Returns clean (title, subtitle) without labels.
    """
    text = _to_idea_text(raw_content, "")
    if not text:
        return fallback_title, ""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    parsed_title = ""
    parsed_subtitle = ""

    for line in lines:
        lower_line = line.lower()
        if lower_line.startswith("title:"):
            parsed_title = line.split(":", 1)[1].strip()
        elif lower_line.startswith("subtitle:"):
            parsed_subtitle = line.split(":", 1)[1].strip()

    if parsed_title or parsed_subtitle:
        return parsed_title or fallback_title, parsed_subtitle

    # Fallback: no explicit labels, use first line as title and the rest as subtitle.
    first = lines[0]
    rest = "\n".join(lines[1:]).strip()
    return first or fallback_title, rest

# ==========================================
# 1. GENERATE FROM FILE (DOCX)
# ==========================================


@router.post("/docx")
async def generate_from_docx_normal(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_active_user),
    project_service: ProjectService = Depends(get_project_service),
    slide_service: SlideService = Depends(get_slide_service),
    slidegen_workflow_service: SlideGenWorkflowService = Depends(get_slidegen_workflow_service),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    [Synchronous] Upload DOCX -> Wait -> Return Slides JSON
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Chỉ chấp nhận tệp DOCX")

    # Get full user from repository with subscription data
    user_repo = SqliteUserRepository()
    user = user_repo.get_by_id(current_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check subscription limits for docx upload
    subscription_service.check_feature_access(user, "docx_upload")

    # 1. Setup paths
    project_name = os.path.splitext(file.filename)[0]
    output_folder = prepare_output_folder(project_name)

    temp_path = TEMP_DIR / file.filename
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Estimate slide count and validate subscription limits
    _check_docx_slide_limit(temp_path, subscription_service, user)

    try:
        # Increment usage counter
        subscription_service.increment_usage(current_user.id, "docx_upload")

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
    workflow_mode: str = Form("auto_no_heading"),
    enable_transition_slides: str = Form("true"),
    enable_thank_you_slide: str = Form("true"),
    current_user: UserResponse = Depends(get_current_active_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    [Step 1 Stream] Upload DOCX & Save Options -> Return Filename
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Chỉ chấp nhận tệp DOCX")

    # Get full user from repository with subscription data
    user_repo = SqliteUserRepository()
    user = user_repo.get_by_id(current_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check subscription limits for docx upload
    subscription_service.check_feature_access(user, "docx_upload")

    _cleanup_temp_dir()

    temp_path = TEMP_DIR / file.filename
    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)

    # Estimate slide count and validate subscription limits
    _check_docx_slide_limit(temp_path, subscription_service, user)

    options = {
        "workflow_mode": workflow_mode.strip() or "auto_no_heading",
        "enable_transition_slides": enable_transition_slides.lower() in ('true', '1', 'yes', 'on'),
        "enable_thank_you_slide": enable_thank_you_slide.lower() in ('true', '1', 'yes', 'on')
    }
    with open(TEMP_DIR / f"{file.filename}.options.json", "w") as f:
        json.dump(options, f)

    return {"filename": file.filename}


@router.post("/pdf/prepare-stream", response_model=DocxPrepareResponse)
async def prepare_pdf_stream(
    file: UploadFile = File(...),
    workflow_mode: str = Form("auto_no_heading"),
    enable_transition_slides: str = Form("true"),
    enable_thank_you_slide: str = Form("true"),
    current_user: UserResponse = Depends(get_current_active_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    [Step 1 Stream] Upload PDF & Save Options -> Return Filename
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Chỉ chấp nhận tệp PDF")

    user_repo = SqliteUserRepository()
    user = user_repo.get_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    subscription_service.check_feature_access(user, "docx_upload")
    _cleanup_temp_dir()

    temp_path = TEMP_DIR / file.filename
    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)

    _check_pdf_slide_limit(temp_path, subscription_service, user)

    options = {
        "workflow_mode": workflow_mode.strip() or "auto_no_heading",
        "enable_transition_slides": enable_transition_slides.lower() in ('true', '1', 'yes', 'on'),
        "enable_thank_you_slide": enable_thank_you_slide.lower() in ('true', '1', 'yes', 'on')
    }
    with open(TEMP_DIR / f"{file.filename}.options.json", "w") as f:
        json.dump(options, f)

    return {"filename": file.filename}


# ==========================================
# MARKDOWN PARSER - Reusable for Manual & Idea
# ==========================================

@router.post("/markdown/parse")
async def parse_markdown(
    content: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Parse markdown text into hierarchical structure.
    Can be used by both Manual Mode and Idea Mode.
    
    Request body:
    {
        "markdown": "# Title\\nContent...",
        "default_title": "Optional title"
    }
    """
    try:
        from backend.workflows.slidegen_workflow.utils.markdown_parser import markdown_to_manual_structure, validate_markdown_structure
        
        markdown_text = content.get('markdown', '').strip()
        default_title = content.get('default_title', 'Document')
        
        if not markdown_text:
            raise ValueError("Markdown content is empty")
        
        # Parse markdown
        document_title, structure = markdown_to_manual_structure(markdown_text, default_title)
        
        # Validate
        is_valid, errors = validate_markdown_structure(structure)
        if not is_valid:
            logger.warning(f"Markdown validation issues: {errors}")
        
        return {
            "success": True,
            "document_title": document_title,
            "structure": structure,
            "validation_warnings": errors if not is_valid else [],
            "node_count": len(structure)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Markdown parse error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse markdown")


@router.get("/docx/stream")
async def stream_docx_generation(
    filename: str = Query(..., description="DOCX filename"),
    current_user: UserResponse = Depends(get_current_user_from_token_param),
    project_service: ProjectService = Depends(get_project_service),
    slidegen_workflow_service: SlideGenWorkflowService = Depends(get_slidegen_workflow_service),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    [Step 2 Stream] SSE Generation for DOCX
    """
    temp_path = TEMP_DIR / os.path.basename(filename)
    if not temp_path.exists(): raise HTTPException(400, "Tệp không tồn tại hoặc đã hết hạn")

    # Increment usage counter (actual processing starts here)
    subscription_service.increment_usage(current_user.id, "docx_upload")

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
                await queue.put((EventTypes.ERROR_EVENT, {'message': "Workflow failed"}))
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
            _html_dir = output_folder / "output" / "html"
            if not _html_dir.exists():
                _html_dir = output_folder / "html"
            if _html_dir.exists():
                actual_slide_count = len(list(_html_dir.glob("*.html")))

            workflow_temp_dir = str(output_folder)

            await queue.put((EventTypes.COMPLETE, {
                'project_id': pid,
                'project_name': project_name,
                'total_slides': actual_slide_count,
                'temp_dir': workflow_temp_dir
            }))

        asyncio.create_task(run_bg())

        # Common streaming loop
        while True:
            try:
                ev = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield f"event: {ev[0]}\ndata: {json.dumps(ev[1])}\n\n"
                if ev[0] in [EventTypes.COMPLETE, EventTypes.ERROR_EVENT]: break
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
        
        # Cleanup input file after stream
        if temp_path.exists(): temp_path.unlink()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/pdf/stream")
async def stream_pdf_generation(
    filename: str = Query(..., description="PDF filename"),
    current_user: UserResponse = Depends(get_current_user_from_token_param),
    project_service: ProjectService = Depends(get_project_service),
    slidegen_workflow_service: SlideGenWorkflowService = Depends(get_slidegen_workflow_service),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    [Step 2 Stream] SSE Generation for PDF (separate PDF workflow).
    """
    temp_path = TEMP_DIR / os.path.basename(filename)
    if not temp_path.exists():
        raise HTTPException(400, "Tệp không tồn tại hoặc đã hết hạn")

    subscription_service.increment_usage(current_user.id, "docx_upload")

    options_path = TEMP_DIR / f"{filename}.options.json"
    slide_options = {}
    if options_path.exists():
        with open(options_path, "r") as f:
            slide_options = json.load(f)

    project_name = os.path.splitext(filename)[0]
    output_folder = prepare_output_folder(project_name)

    async def event_generator():
        queue = asyncio.Queue()

        def callback(event_type, data):
            safe_data = sanitize_event_data(event_type, data)
            queue.put_nowait((event_type, safe_data))

        async def run_bg():
            res = await slidegen_workflow_service.process_pdf(
                pdf_path=str(temp_path),
                output_folder=str(output_folder),
                router_flags=False,
                callback=callback,
                slide_options=slide_options
            )

            if not res:
                await queue.put((EventTypes.ERROR_EVENT, {'message': "Workflow failed"}))
                return

            pid = project_service.import_project_from_workflow(
                user_id=current_user.id,
                project_name=project_name,
                source_type='pdf',
                source_data={'filename': filename},
                slide_options=slide_options,
                output_folder=output_folder
            )

            actual_slide_count = 0
            _html_dir = output_folder / "output" / "html"
            if not _html_dir.exists():
                _html_dir = output_folder / "html"
            if _html_dir.exists():
                actual_slide_count = len(list(_html_dir.glob("*.html")))

            workflow_temp_dir = str(output_folder)
            await queue.put((EventTypes.COMPLETE, {
                'project_id': pid,
                'project_name': project_name,
                'total_slides': actual_slide_count,
                'temp_dir': workflow_temp_dir
            }))

        asyncio.create_task(run_bg())

        while True:
            try:
                ev = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield f"event: {ev[0]}\ndata: {json.dumps(ev[1])}\n\n"
                if ev[0] in [EventTypes.COMPLETE, EventTypes.ERROR_EVENT]:
                    break
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"

        if temp_path.exists():
            temp_path.unlink()

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/docx/manual-session", response_model=ManualSessionResponse)
async def create_manual_session_from_docx(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_active_user),
    structure_service: StructureService = Depends(get_structure_service),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Upload DOCX -> Parse Text -> Create Editing Session for Manual Mode
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(400, "Chỉ chấp nhận tệp DOCX")

    # Get full user from repository with subscription data
    user_repo = SqliteUserRepository()
    user = user_repo.get_by_id(current_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check subscription limits for docx upload
    subscription_service.check_feature_access(user, "docx_upload")

    temp_path = TEMP_DIR / file.filename
    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)

    # Estimate slide count and validate subscription limits
    _check_docx_slide_limit(temp_path, subscription_service, user)

    try:
        # Increment usage counter
        subscription_service.increment_usage(current_user.id, "docx_upload")

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
    current_user: UserResponse = Depends(idea_structure_rate_limiter),
    idea_service: IdeaService = Depends(get_idea_service),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Step 1 Idea: Generate structure from prompt"""
    # Get full user from repository with subscription data
    user_repo = SqliteUserRepository()
    user = user_repo.get_by_id(current_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check subscription limits for idea generation
    subscription_service.check_feature_access(user, "idea_generation")

    # Check content length restrictions
    data = request.model_dump()
    content_length = data.get('content_length', 'standard')
    subscription_service.check_feature_access(user, "content_length", content_length=content_length)

    try:
        # Increment usage counter
        subscription_service.increment_usage(current_user.id, "idea_generation")

        return await idea_service.generate_structure(
            title=data.get('title', '').strip(),
            prompt=data.get('prompt', '').strip(),
            content_length=content_length,
            enable_transition=data.get('enable_transition_slides', True),
            enable_thank_you=data.get('enable_thank_you_slide', True)
        )
    except Exception as e:
        logger.error(f"Idea structure error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/idea/structure/{session_id}/manual-session", response_model=ManualSessionResponse)
async def convert_idea_to_manual_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    structure_service: StructureService = Depends(get_structure_service)
):
    """
    Convert idea JSON session into StructureEditor-compatible manual session.
    This pre-populates L0 intro + L1 blocks so user can edit with manual UI immediately.
    """
    try:
        idea_data = await SessionManager.read_session_json(session_id, "idea")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Idea session read error: {e}")
        raise HTTPException(status_code=500, detail="Không thể đọc dữ liệu idea session")

    document_title = _to_idea_text(idea_data.get("title"), "Untitled")
    slide_chunks = idea_data.get("slide_chunks", [])

    if not slide_chunks:
        raise HTTPException(status_code=400, detail="Idea session không có slide chunk để chuyển đổi")

    manual_structure = []
    intro_title = document_title
    intro_subtitle = ""
    plain_text_parts = []

    for idx, chunk in enumerate(slide_chunks):
        title = _to_idea_text(chunk.get("title") or chunk.get("heading"), f"Slide {idx + 1}")
        content = _to_idea_text(
            chunk.get("content") or chunk.get("description") or chunk.get("text_content"),
            ""
        )
        slide_type = _to_idea_text(chunk.get("slide_type"), "content").lower()

        if slide_type == "intro":
            intro_title, intro_subtitle = _parse_intro_title_subtitle(
                content or title or document_title,
                document_title,
            )
            continue

        plain_text_parts.append(title)
        if content:
            plain_text_parts.append(content)

        manual_structure.append({
            "node_id": f"idea_node_{idx + 1}",
            "level": 1,
            "title": title,
            "content": content,
            "children": [],
            "is_transition": slide_type == "transition",
        })

    full_text = "\n\n".join(plain_text_parts) if plain_text_parts else document_title

    manual_session_id = structure_service.create_session(
        filename=f"{document_title}.docx",
        full_text=full_text,
        paragraphs=[],
        docx_path=""
    )

    intro_node = {
        "node_id": "intro_slide_0",
        "level": 0,
        "title": intro_title,
        "content": intro_subtitle,
        "children": [],
        "is_transition": False,
    }

    # Put intro directly into structure so StructureEditor can render L0 immediately on first load.
    structure_with_intro = [intro_node] + manual_structure

    structure_service.update_session_structure(
        session_id=manual_session_id,
        structure=structure_with_intro,
        intro_slide=None
    )

    return {
        "success": True,
        "session_id": manual_session_id,
        "document_title": document_title,
    }


@router.get("/idea/stream")
async def stream_idea_generation(
    session_id: str = Query(...),
    current_user: UserResponse = Depends(idea_stream_rate_limiter),
    project_service: ProjectService = Depends(get_project_service),
    slidegen_workflow_service: SlideGenWorkflowService = Depends(get_slidegen_workflow_service),
    conversion_service: ConversionService = Depends(get_conversion_service)
):
    """Step 2 Idea: SSE Generation"""
    try:
        idea_data = await SessionManager.read_session_json(session_id, "idea")
    except HTTPException as e:
        # Re-raise with localized message
        raise HTTPException(400, "Phiên không hợp lệ")

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

            # Ensure idea output has converted HTML (absolute positioning), matching full docx flow.
            ensure_converted_slides(output_folder, conversion_service)

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
                if ev[0] in [EventTypes.COMPLETE, EventTypes.ERROR_EVENT]: break
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"

        # Cleanup idea session file after stream
        await SessionManager.delete_session(session_id, "idea")

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/idea/structure/{session_id}", response_model=IdeaStructureDetailResponse)
async def get_idea_structure(
    session_id: str,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get idea structure details for preview/editing"""
    try:
        data = await SessionManager.read_session_json(session_id, "idea")

        # Sanitize slide_chunks to ensure all required fields are present
        slide_chunks = data.get('slide_chunks', [])
        sanitized_chunks = []

        for i, chunk in enumerate(slide_chunks):
            # Map different field formats to expected schema
            title = chunk.get("title") or chunk.get("heading", f"Slide {i + 1}")
            content = chunk.get("content") or chunk.get("description", "Content not available")

            sanitized_chunk = {
                "title": str(title).strip() if title else f"Slide {i + 1}",
                "content": str(content).strip() if content else "Content not available",
                "slide_type": chunk.get("slide_type", "content")
            }
            sanitized_chunks.append(sanitized_chunk)

        return IdeaStructureDetailResponse(
            session_id=session_id,
            title=data.get('title', ''),
            slide_chunks=sanitized_chunks,
            enable_transition_slides=data.get('enable_transition_slides', True),
            enable_thank_you_slide=data.get('enable_thank_you_slide', True),
            metadata=data.get('metadata', {})
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error reading structure: {e}")
        raise HTTPException(500, "Failed to read structure")


@router.put("/idea/structure/{session_id}", response_model=IdeaStructureDetailResponse)
async def update_idea_structure(
    session_id: str,
    request: IdeaStructureUpdateRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update idea structure before generation"""
    try:
        # Read existing data to preserve metadata
        existing_data = await SessionManager.read_session_json(session_id, "idea")

        # Update with new data
        updated_data = {
            'title': request.title.strip(),
            'slide_chunks': [chunk.dict() for chunk in request.slide_chunks],
            'enable_transition_slides': request.enable_transition_slides,
            'enable_thank_you_slide': request.enable_thank_you_slide,
            'prompt': existing_data.get('prompt', ''),  # Keep original prompt
            'is_from_idea': True,
            'metadata': existing_data.get('metadata', {})
        }

        # Save updated structure
        await SessionManager.write_session_json(session_id, updated_data, "idea")

        return IdeaStructureDetailResponse(
            session_id=session_id,
            title=updated_data['title'],
            slide_chunks=updated_data['slide_chunks'],
            enable_transition_slides=updated_data['enable_transition_slides'],
            enable_thank_you_slide=updated_data['enable_thank_you_slide'],
            metadata=updated_data.get('metadata', {})
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error updating structure: {e}")
        raise HTTPException(500, "Failed to update structure")


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
            slide_options = {
                'enable_transition_slides': data.get('enable_transition_slides', False),
                'enable_thank_you_slide': data.get('enable_thank_you_slide', False),
            }
            slide_chunks = data.get('slide_chunks', [])
            logger.info(f"[Manual Stream] Starting with {len(slide_chunks)} chunks, options={slide_options}")
            res = await slidegen_workflow_service.process_chunks(
                slide_chunks=slide_chunks,
                title=title,
                output_folder=str(output_folder),
                callback=callback,
                slide_options=slide_options
            )
            
            if not res:
                await queue.put((EventTypes.ERROR_EVENT, {'message': "Workflow failed"}))
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

            # Derive actual generated slide count from output HTML files to avoid 0-total regressions.
            actual_slide_count = 0
            try:
                _out = Path(output_folder)
                _html_dir = (_out / "output" / "html") if (_out / "output" / "html").exists() else (_out / "html")
                if _html_dir.exists():
                    actual_slide_count = len(list(_html_dir.glob("*.html")))
            except Exception as count_err:
                logger.warning(f"[Manual Stream] Could not count generated slides: {count_err}")

            if actual_slide_count <= 0:
                actual_slide_count = len(data.get('slide_chunks', []))

            await queue.put((EventTypes.COMPLETE, {
                'project_id': pid,
                'project_name': title,
                'total_slides': actual_slide_count,
                'temp_dir': workflow_temp_dir
            }))

        asyncio.create_task(run_bg())

        while True:
            try:
                ev = await asyncio.wait_for(queue.get(), timeout=1.0)
                yield f"event: {ev[0]}\ndata: {json.dumps(ev[1])}\n\n"
                if ev[0] in [EventTypes.COMPLETE, EventTypes.ERROR_EVENT]: break
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")