"""
SlideGen Backend - Main FastAPI Application
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form, Depends
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

# Initialize database
from .database import init_db
init_db()

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

def save_workflow_to_database(
    user_id: int,
    project_name: str,
    source_type: str,
    source_data: dict,
    slide_options: dict,
    output_folder: Path
) -> int:
    """Save completed workflow to database with converted HTML"""
    try:
        # Create project
        project_id = create_project(
            user_id=user_id,
            title=project_name,
            description=source_data.get('description', ''),
            source_type=source_type,
            source_data=source_data
        )
        
        # Save project metadata
        save_project_metadata(
            project_id=project_id,
            slide_options=slide_options,
            workflow_config={},
            generation_params={}
        )
        
        # Convert HTML slides to absolute positioning before saving
        html_folder = output_folder / "html"
        converted_folder = output_folder / "converted"
        
        if html_folder.exists():
            # Convert HTML slides using converter.js
            logger.info(f"🔄 Converting HTML slides to absolute positioning...")
            conversion_result = conversion_service.convert_slides_batch(html_folder, converted_folder)
            
            if conversion_result['success']:
                logger.info(f"✅ Successfully converted {len(conversion_result['success'])} slides")
            if conversion_result['failed']:
                logger.warning(f"⚠️ Failed to convert {len(conversion_result['failed'])} slides")
            
            # Read and save converted slides (prioritize converted, fallback to original)
            html_files = sorted(html_folder.glob("*.html"))
            
            for idx, html_file in enumerate(html_files):
                # Try to read converted HTML first
                converted_file = converted_folder / f"converted_{html_file.name}"
                if converted_file.exists():
                    logger.info(f"📄 Reading converted HTML: {converted_file.name}")
                    with open(converted_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                else:
                    # Fallback to original HTML if conversion failed
                    logger.warning(f"⚠️ Using original HTML (conversion failed): {html_file.name}")
                    with open(html_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                
                # Extract slide type from filename
                slide_name = html_file.stem
                slide_type = 'content'  # Default
                
                if 'intro' in slide_name.lower() or idx == 0:
                    slide_type = 'intro'
                elif 'transition' in slide_name.lower():
                    slide_type = 'transition'
                elif 'thank' in slide_name.lower():
                    slide_type = 'thank_you'
                
                # Create slide in database with converted HTML
                create_slide(
                    project_id=project_id,
                    slide_index=idx,
                    slide_type=slide_type,
                    title=f"Slide {idx + 1}",
                    html_content=html_content,
                    design_settings={}
                )
            
            # Update project slide count and status
            update_project(
                project_id=project_id,
                slide_count=len(html_files),
                status='completed'
            )
            
            logger.info(f"✅ Saved project {project_id} with {len(html_files)} slides to database")
        
        return project_id
        
    except Exception as e:
        logger.error(f"Failed to save workflow to database: {e}")
        return 0

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


# ========================== AUTHENTICATION ENDPOINTS ==========================

from .models import UserCreate, UserLogin, Token, UserResponse, User
from .auth import (
    get_password_hash, 
    verify_password,
    authenticate_user, 
    create_access_token,
    get_current_active_user
)
from .database import get_user_by_email, create_user, get_db
from datetime import timedelta

@app.post("/api/auth/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user_id = create_user(user_data.email, user_data.username, hashed_password)
    
    # Get created user
    user = get_user_by_email(user_data.email)
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        username=user["username"],
        created_at=user["created_at"],
        is_active=bool(user["is_active"])
    )

@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user and return JWT token"""
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=60 * 24)  # 24 hours
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@app.post("/api/auth/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}


@app.put("/api/auth/change-password")
async def change_password(
    password_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Change user password"""
    current_password = password_data.get('current_password')
    new_password = password_data.get('new_password')
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    # Update password in database
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            new_hashed_password = get_password_hash(new_password)
            cursor.execute(
                'UPDATE users SET hashed_password = ? WHERE id = ?',
                (new_hashed_password, current_user.id)
            )
            conn.commit()
            return {"message": "Password changed successfully"}
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")


# ========================== USER PROFILE & SETTINGS ==========================

from .database import (
    get_user_profile, create_or_update_user_profile,
    get_user_settings, create_default_settings, update_user_settings,
    create_project, get_user_projects, get_project, update_project, delete_project,
    create_slide, get_project_slides as db_get_project_slides, get_slide, 
    update_slide, delete_slide, save_project_metadata, get_project_metadata
)

@app.get("/api/profile")
async def get_profile(current_user: UserResponse = Depends(get_current_active_user)):
    """Get current user profile"""
    profile = get_user_profile(current_user.id)
    if not profile:
        # Return empty profile
        return {
            "user_id": current_user.id,
            "full_name": None,
            "avatar_url": None,
            "bio": None
        }
    return profile

@app.put("/api/profile")
async def update_profile(
    profile_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update user profile"""
    create_or_update_user_profile(
        user_id=current_user.id,
        full_name=profile_data.get("full_name"),
        avatar_url=profile_data.get("avatar_url"),
        bio=profile_data.get("bio")
    )
    return {"message": "Profile updated"}

@app.get("/api/settings")
async def get_settings(current_user: UserResponse = Depends(get_current_active_user)):
    """Get user settings"""
    settings = get_user_settings(current_user.id)
    if not settings:
        # Create default settings
        create_default_settings(current_user.id)
        settings = get_user_settings(current_user.id)
    return settings

@app.put("/api/settings")
async def update_settings(
    settings_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update user settings"""
    update_user_settings(
        user_id=current_user.id,
        theme=settings_data.get("theme"),
        default_transition_enabled=settings_data.get("default_transition_enabled"),
        default_thank_you_enabled=settings_data.get("default_thank_you_enabled"),
        default_content_length=settings_data.get("default_content_length"),
        language=settings_data.get("language"),
        settings_json=settings_data.get("settings_json")
    )
    return {"message": "Settings updated"}


# ========================== PROJECTS API ==========================

@app.get("/api/projects")
async def list_projects(
    limit: int = 50,
    offset: int = 0,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get all projects for current user"""
    projects = get_user_projects(current_user.id, limit, offset)
    return {
        "projects": projects,
        "total": len(projects)
    }

@app.post("/api/projects")
async def create_new_project(
    project_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Create new project"""
    project_id = create_project(
        user_id=current_user.id,
        title=project_data.get("title", "Untitled Project"),
        description=project_data.get("description"),
        source_type=project_data.get("source_type", "idea"),
        source_data=project_data.get("source_data")
    )
    return {"project_id": project_id, "message": "Project created"}

@app.get("/api/projects/{project_id}")
async def get_project_detail(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get project details with slides"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get slides
    slides = db_get_project_slides(project_id)
    
    # Get metadata
    metadata = get_project_metadata(project_id)
    
    return {
        "project": project,
        "slides": slides,
        "metadata": metadata
    }

@app.put("/api/projects/{project_id}")
async def update_project_detail(
    project_id: int,
    project_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update project"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_project(
        project_id=project_id,
        title=project_data.get("title"),
        description=project_data.get("description"),
        status=project_data.get("status"),
        slide_count=project_data.get("slide_count"),
        thumbnail_url=project_data.get("thumbnail_url")
    )
    return {"message": "Project updated"}

@app.delete("/api/projects/{project_id}")
async def delete_project_detail(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Delete project"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    delete_project(project_id)
    return {"message": "Project deleted"}


# ========================== SLIDES API (DATABASE) ==========================

@app.get("/api/projects/{project_id}/slides")
async def get_project_slides_list(
    project_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get all slides for a project"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    slides = db_get_project_slides(project_id)
    return {"slides": slides, "total": len(slides)}

@app.post("/api/projects/{project_id}/slides")
async def create_new_slide(
    project_id: int,
    slide_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Create a new slide in a project"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify ownership
    if project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create slide
    slide_id = create_slide(
        project_id=project_id,
        slide_index=slide_data.get("slide_index", 0),
        slide_type=slide_data.get("slide_type", "content"),
        title=slide_data.get("title"),
        content_text=slide_data.get("content_text"),
        html_content=slide_data.get("html_content"),
        design_settings=slide_data.get("design_settings")
    )
    
    # Update project slide count
    slides = db_get_project_slides(project_id)
    update_project(project_id, slide_count=len(slides))
    
    return {"id": slide_id, "message": "Slide created"}

@app.get("/api/slides/{slide_id}")
async def get_slide_detail(
    slide_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get slide details"""
    slide = get_slide(slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    # Verify ownership through project
    project = get_project(slide["project_id"])
    if not project or project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return slide

@app.put("/api/slides/{slide_id}")
async def update_slide_content(
    slide_id: int,
    slide_data: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Update slide content"""
    slide = get_slide(slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    # Verify ownership through project
    project = get_project(slide["project_id"])
    if not project or project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_slide(
        slide_id=slide_id,
        title=slide_data.get("title"),
        content_text=slide_data.get("content_text"),
        html_content=slide_data.get("html_content"),
        design_settings=slide_data.get("design_settings")
    )
    return {"message": "Slide updated"}

@app.delete("/api/slides/{slide_id}")
async def delete_slide_detail(
    slide_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Delete a slide"""
    slide = get_slide(slide_id)
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    # Verify ownership through project
    project = get_project(slide["project_id"])
    if not project or project["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    delete_slide(slide_id)
    
    # Update project slide count
    slides = db_get_project_slides(slide["project_id"])
    update_project(slide["project_id"], slide_count=len(slides))
    
    return {"message": "Slide deleted"}


# ========================== UPLOAD ENDPOINTS ==========================

@app.post("/api/upload-docx")
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


from .auth import get_current_user_from_token_param

@app.get("/api/upload-docx-stream")
async def upload_docx_stream(
    filename: str,
    current_user: UserResponse = Depends(get_current_user_from_token_param)
):
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
                    
                    # Save to database
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


# ========================== SLIDES API ==========================

@app.get("/api/projects/by-name/{project_name}/slides")
async def get_project_slides_by_name(project_name: str):
    """Get slides for a project by name - uses converted HTML from database (public access)"""
    logger.info(f"🔓 Public API: Loading slides for project name: {project_name}")
    try:
        # Find project by title/name
        from .database import get_all_projects
        projects = get_all_projects()
        project = next((p for p in projects if p["title"] == project_name), None)
        
        if not project:
            logger.warning(f"Project not found by name: {project_name}")
            raise HTTPException(status_code=404, detail=f"Project '{project_name}' not found")
        
        # Get slides from database (already converted HTML)
        from .database import get_project_slides as get_db_slides
        db_slides = get_db_slides(project["id"])
        
        if not db_slides:
            raise HTTPException(status_code=404, detail=f"No slides found for project: {project_name}")
        
        # Format for frontend
        slides = []
        for slide in db_slides:
            slides.append({
                "id": slide["id"],
                "title": slide["title"],
                "content": slide["html_content"],  # Already converted HTML
                "type": slide["slide_type"],
                "index": slide["slide_index"]
            })
        
        logger.info(f"✅ Loaded {len(slides)} slides from database for {project_name}")
        return JSONResponse(content={
            "project_name": project_name,
            "project_id": project["id"],
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
    
    # Security: only allow serving from slidegen_workflow_* or slidegen_idea_* directories
    normalized_path = path.replace('\\', '/')
    is_linux_workflow = normalized_path.startswith('/tmp/slidegen_workflow_')
    is_linux_idea = normalized_path.startswith('/tmp/slidegen_idea_')
    is_windows_temp = ('slidegen_workflow_' in normalized_path or 'slidegen_idea_' in normalized_path) and ('Temp' in path or 'temp' in path)
    
    if not (is_linux_workflow or is_linux_idea or is_windows_temp):
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
        
        # Security: only allow deleting slidegen_workflow_* or slidegen_idea_* directories
        normalized_path = temp_dir.replace('\\', '/')
        is_linux_workflow = normalized_path.startswith('/tmp/slidegen_workflow_')
        is_linux_idea = normalized_path.startswith('/tmp/slidegen_idea_')
        is_windows_temp = ('slidegen_workflow_' in normalized_path or 'slidegen_idea_' in normalized_path) and ('Temp' in temp_dir or 'temp' in temp_dir)
        
        if not (is_linux_workflow or is_linux_idea or is_windows_temp):
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


@app.post("/api/generate-from-idea")
async def generate_from_idea(
    request: Request,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Generate slides from natural language idea using LLM (Protected route)"""
    try:
        data = await request.json()
        title = data.get('title', '').strip()
        prompt = data.get('prompt', '').strip()
        content_length = data.get('content_length', 'standard')
        enable_transition_slides = data.get('enable_transition_slides', True)
        enable_thank_you_slide = data.get('enable_thank_you_slide', True)
        
        if not title or not prompt:
            raise HTTPException(status_code=400, detail="Title and prompt are required")
        
        # Map content length to slide range (TOTAL slides including all types)
        length_map = {
            'brief': {'min': 5, 'max': 8, 'desc': 'Quick overview'},
            'standard': {'min': 8, 'max': 12, 'desc': 'Balanced coverage'},
            'detailed': {'min': 12, 'max': 18, 'desc': 'Comprehensive'},
            'extensive': {'min': 18, 'max': 25, 'desc': 'In-depth analysis'}
        }
        length_info = length_map.get(content_length, length_map['standard'])
        
        # Calculate actual content slide target by subtracting overhead
        # Assumptions:
        # - 1 intro slide (always)
        # - Estimate sections: brief=2, standard=3, detailed=4, extensive=5
        # - 1 transition per section (if enabled)
        # - 1 thank you slide (if enabled)
        
        estimated_sections = {
            'brief': 2,
            'standard': 3,
            'detailed': 4,
            'extensive': 5
        }.get(content_length, 3)
        
        overhead_slides = 1  # Always 1 intro
        if enable_transition_slides:
            # Estimate transitions: typically sections - 1 (no transition before first section)
            estimated_transitions = max(0, estimated_sections - 1)
            overhead_slides += estimated_transitions
            logger.info(f"   Estimated {estimated_transitions} transition slides for {estimated_sections} sections")
        
        if enable_thank_you_slide:
            overhead_slides += 1
            logger.info(f"   Including 1 thank you slide")
        
        # Calculate target content slide range
        content_min = max(1, length_info['min'] - overhead_slides)
        content_max = max(content_min + 1, length_info['max'] - overhead_slides)
        
        logger.info(f"🤖 Generating slides from idea:")
        logger.info(f"   Title: {title}")
        logger.info(f"   Prompt length: {len(prompt)} chars")
        logger.info(f"   Total slide range: {length_info['min']}-{length_info['max']} slides")
        logger.info(f"   Overhead slides: {overhead_slides} (intro + transitions + thank you)")
        logger.info(f"   Target content slides: {content_min}-{content_max}")
        logger.info(f"   Options: transitions={enable_transition_slides}, thank_you={enable_thank_you_slide}")
        
        # Call LLM to generate slide structure
        from src.models.llm import LLM
        import os
        
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Import config for idea structure LLM
        from src.utils.config import (
            IDEA_STRUCTURE_LLM_MODEL,
            IDEA_STRUCTURE_LLM_TEMPERATURE,
            IDEA_STRUCTURE_LLM_MAX_TOKENS,
            LLM_BASE_URL
        )
        
        llm = LLM(
            api_keys=[gemini_api_key],
            base_url=LLM_BASE_URL,
            model=IDEA_STRUCTURE_LLM_MODEL,
            temperature=IDEA_STRUCTURE_LLM_TEMPERATURE,
            max_tokens=IDEA_STRUCTURE_LLM_MAX_TOKENS
        )
        
        # Build structured prompt for slide generation
        structure_prompt = f"""You are a presentation structure generator. Given a title and description, create a logical slide structure.

PRESENTATION TITLE: {title}

USER DESCRIPTION:
{prompt}

CONTENT DEPTH: {content_length.upper()} ({length_info['desc']})
TOTAL SLIDE TARGET: {length_info['min']}-{length_info['max']} slides (including ALL types)
CONTENT SLIDE TARGET: {content_min}-{content_max} slides (after accounting for intro, transitions, thank you)

SLIDE COMPOSITION:
- 1 intro slide (position 0) - MANDATORY
- {content_min} to {content_max} content slides (position 1, 2, 3...) - MAIN CONTENT
- {"~" + str(estimated_sections - 1) + " transition slides (position -1) - between sections" if enable_transition_slides else "No transition slides"}
- {"1 thank you slide (position -2) - at end" if enable_thank_you_slide else "No thank you slide"}
- Expected total: {length_info['min']}-{length_info['max']} slides

INSTRUCTIONS:
1. Organize content into approximately {estimated_sections} major sections
2. First slide MUST be intro/title slide (position 0)
3. Generate EXACTLY {content_min} to {content_max} content slides (position 1, 2, 3...)
4. Each section should have a clear heading (use markdown ## for major sections)
5. Provide brief bullet points for each slide's content (3-5 points per slide)
6. If transitions enabled: Add transition slide (position -1) BETWEEN each major section
7. If thank you enabled: End with thank you slide (position -2)

OUTPUT FORMAT (JSON):
{{
  "slide_chunks": [
    {{"position": 0, "heading": "", "text_content": "Title: [title]\\nSubtitle: [subtitle]"}},
    {{"position": 1, "heading": "Section 1 Title", "text_content": "- Point 1\\n- Point 2\\n- Point 3"}},
    {{"position": -1, "heading": "TRANSITION", "text_content": "Moving to: Next Section"}},
    {{"position": 2, "heading": "Section 2 Title", "text_content": "- Point A\\n- Point B"}},
    ...
    {{"position": -2, "heading": "THANK_YOU", "text_content": "Thank you for your attention!"}}
  ]
}}

IMPORTANT RULES - FOLLOW EXACTLY:
- position: 0 for intro, -1 for transitions, -2 for thank you, regular numbers (1,2,3...) for content slides
- heading: Empty string for intro, "TRANSITION" for transitions, "THANK_YOU" for thank you, actual section titles for content
- text_content: For intro use "Title: X\\nSubtitle: Y" format, for content use bullet points with "-", keep concise

CRITICAL REQUIREMENTS:
1. Generate EXACTLY {content_min} to {content_max} CONTENT slides (position 1, 2, 3...)
   - This is calculated to ensure total slides fit in range {length_info['min']}-{length_info['max']}
   - DO NOT exceed {content_max} content slides
   
2. Structure with approximately {estimated_sections} major sections
   - Distribute content slides across these sections
   - Each section should have multiple slides
   
3. Transition slides (position -1):
   - {"Add transition between each major section change" if enable_transition_slides else "DO NOT add any transitions"}
   - {"Expected ~" + str(estimated_sections - 1) + " transitions total" if enable_transition_slides else ""}
   
4. Thank you slide (position -2):
   - {"Add ONE thank you slide at the very end" if enable_thank_you_slide else "DO NOT add thank you slide"}

FINAL CHECK:
- Intro: 1 slide
- Content: {content_min}-{content_max} slides
- Transitions: {"~" + str(estimated_sections - 1) if enable_transition_slides else "0"} slides
- Thank you: {"1" if enable_thank_you_slide else "0"} slide
- TOTAL should be approximately {length_info['min']}-{length_info['max']} slides

Now generate the slide structure as valid JSON only (no markdown code blocks):"""
        
        # Call LLM
        logger.info("📤 Calling LLM for slide structure generation...")
        response_text = llm.invoke(structure_prompt)
        logger.info(f"📥 LLM response length: {len(response_text)} chars")
        
        # Parse JSON response
        import json
        import re
        
        # Try to extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response_text
        
        try:
            structure_data = json.loads(json_str)
            slide_chunks = structure_data.get('slide_chunks', [])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            raise HTTPException(status_code=500, detail="Failed to parse LLM response")
        
        if not slide_chunks:
            raise HTTPException(status_code=500, detail="No slides generated")
        
        # Validate and adjust slide count
        content_slides = [s for s in slide_chunks if isinstance(s.get('position'), int) and s.get('position') > 0]
        intro_slides = [s for s in slide_chunks if s.get('position') == 0]
        transition_slides = [s for s in slide_chunks if s.get('position') == -1]
        thank_you_slides = [s for s in slide_chunks if s.get('position') == -2]
        
        total_slides = len(slide_chunks)
        
        logger.info(f"📊 Slide breakdown:")
        logger.info(f"   Intro: {len(intro_slides)}")
        logger.info(f"   Content: {len(content_slides)}")
        logger.info(f"   Transitions: {len(transition_slides)}")
        logger.info(f"   Thank you: {len(thank_you_slides)}")
        logger.info(f"   TOTAL: {total_slides} slides")
        
        # Validate content slide count
        if not (content_min <= len(content_slides) <= content_max):
            logger.warning(f"⚠️  Content slides: {len(content_slides)} (expected: {content_min}-{content_max})")
        
        # Validate total slide count
        if not (length_info['min'] <= total_slides <= length_info['max']):
            logger.warning(f"⚠️  Total slides: {total_slides} (target range: {length_info['min']}-{length_info['max']})")
        else:
            logger.info(f"✅ Total slide count within target range!")
        
        logger.info(f"✅ Generated {len(slide_chunks)} total slide chunks")
        
        # Save to temp file (mimic DOCX upload flow)
        import uuid
        session_id = str(uuid.uuid4())[:8]
        temp_filename = f"idea_{session_id}.json"
        temp_path = TEMP_DIR / temp_filename
        
        # Save slide chunks
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump({
                'title': title,
                'slide_chunks': slide_chunks,
                'enable_transition_slides': enable_transition_slides,
                'enable_thank_you_slide': enable_thank_you_slide
            }, f, indent=2, ensure_ascii=False)
        
        # Save options file
        options_path = TEMP_DIR / f"{temp_filename}.options.json"
        with open(options_path, 'w') as f:
            json.dump({
                'enable_transition_slides': enable_transition_slides,
                'enable_thank_you_slide': enable_thank_you_slide
            }, f, indent=2)
        
        logger.info(f"💾 Saved slide structure to {temp_path}")
        
        return JSONResponse(content={
            'session_id': session_id,
            'filename': temp_filename,
            'slide_count': len(slide_chunks),
            'is_from_idea': True  # Flag to use different streaming endpoint
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating from idea: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate slides: {str(e)}")


@app.get("/api/generate-from-idea-stream")
async def generate_from_idea_stream(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user_from_token_param)
):
    """Stream processing of idea-generated slides with Server-Sent Events"""
    
    # Validate session file
    temp_filename = f"idea_{session_id}.json"
    temp_path = TEMP_DIR / temp_filename
    if not temp_path.exists():
        raise HTTPException(status_code=400, detail="Invalid session")
    
    # Load slide chunks and options
    try:
        with open(temp_path, 'r', encoding='utf-8') as f:
            idea_data = json.load(f)
        
        title = idea_data.get('title', 'Untitled')
        slide_chunks = idea_data.get('slide_chunks', [])
        slide_options = {
            'enable_transition_slides': idea_data.get('enable_transition_slides', True),
            'enable_thank_you_slide': idea_data.get('enable_thank_you_slide', True)
        }
        
        logger.info(f"📋 Loaded idea data: {len(slide_chunks)} chunks, title='{title}'")
        
    except Exception as e:
        logger.error(f"Failed to load idea data: {e}")
        raise HTTPException(status_code=500, detail="Failed to load idea data")
    
    # Create project name
    project_name = f"idea_{session_id}"
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
                    temp_path_slide = data['html_path']
                    data['html_path'] = temp_path_slide
                    data['is_temp'] = True
                    logger.info(f"🎯 Streaming temp file: {temp_path_slide}")
                
                # Send all events immediately for real-time streaming
                event_queue.put_nowait((event_type, data))
            except Exception as e:
                logger.error(f"Error in stream callback: {e}")
        
        async def run_workflow():
            """Run workflow in background with pre-loaded slide chunks"""
            nonlocal workflow_error, temp_workflow_dir
            try:
                if not workflow_service or not workflow_service.is_available():
                    raise Exception("Workflow service not available")
                
                # Call workflow with slide_chunks directly (skip document conversion)
                workflow_result = await workflow_service.process_idea_with_workflow(
                    slide_chunks=slide_chunks,
                    title=title,
                    output_folder=str(output_folder),
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
                    
                    # Save to database
                    project_id = save_workflow_to_database(
                        user_id=current_user.id,
                        project_name=project_name,
                        source_type='idea',
                        source_data={
                            'title': title,
                            'prompt': idea_data.get('prompt', ''),
                            'description': f'Slides generated from idea: {title}'
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
                    raise Exception("Workflow did not produce output files")
                
            except Exception as e:
                workflow_error = str(e)
                logger.error(f"Workflow error: {e}")
                import traceback
                logger.error(traceback.format_exc())
            finally:
                workflow_done.set()
        
        # Start workflow task
        workflow_task = asyncio.create_task(run_workflow())
        
        try:
            while not workflow_done.is_set() or not event_queue.empty():
                try:
                    # Wait for event with timeout
                    event_type, data = await asyncio.wait_for(
                        event_queue.get(),
                        timeout=1.0
                    )
                    
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
