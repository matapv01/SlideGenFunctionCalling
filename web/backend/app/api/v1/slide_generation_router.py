from pathlib import Path
from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
import logging
import os
import shutil
import zipfile
import json
import asyncio
from datetime import datetime
from typing import AsyncGenerator
from web.backend.app.config import (
    OUTPUT_DIR, TEMP_DIR
)
from web.backend.app.models import UserResponse
from web.backend.app.application.workflow_service import workflow_service
from web.backend.app.application.conversion_service import conversion_service

from web.backend.app.api.v1.authentication_router import (
    get_current_active_user, get_current_user_from_token_param
)
from web.backend.app.resource.database import (
    create_project, update_project,
    create_slide, save_project_metadata
)
import logging
import re

router = APIRouter(prefix="/generate", tags=["GENERATE"])
logger = logging.getLogger("SlideGen-generate")

def extract_slide_index(path):
    """
    Extract slide index from filename like:
    slide_10_0.html → 10
    """
    match = re.search(r"slide_(\d+)", path.stem)
    return int(match.group(1)) if match else float("inf")

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
            logger.info("🔄 Converting HTML slides to absolute positioning...")
            conversion_result = conversion_service.convert_slides_batch(html_folder, converted_folder)

            if conversion_result['success']:
                logger.info(f"✅ Successfully converted {len(conversion_result['success'])} slides")
            if conversion_result['failed']:
                logger.warning(f"⚠️ Failed to convert {len(conversion_result['failed'])} slides")

            # Read and save converted slides (prioritize converted, fallback to original)
            html_files = sorted(
                html_folder.glob("*.html"),
                key=extract_slide_index
            )

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

@router.get("/from-manual-structure-stream")
async def generate_from_manual_structure_stream(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user_from_token_param)
):
    """Stream processing of manual structure from structure editor with SSE"""
    
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
        raise HTTPException(status_code=400, detail="No slide chunks found")
    
    logger.info(f"📋 Manual structure session: {session_id}")
    logger.info(f"📄 Document title: {document_title}")
    logger.info(f"📊 Total chunks: {len(slide_chunks)}")
    
    # Create project name
    project_name = document_title.replace(' ', '_')
    output_folder = OUTPUT_DIR / project_name
    
    # Handle existing folder
    if output_folder.exists():
        try:
            shutil.rmtree(output_folder)
        except PermissionError:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_name = f"{project_name}_{timestamp}"
            output_folder = OUTPUT_DIR / project_name
    
    output_folder.mkdir(parents=True, exist_ok=True)
    
    temp_workflow_dir = None
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate Server-Sent Events for workflow progress"""
        nonlocal temp_workflow_dir
        
        event_queue = asyncio.Queue()
        workflow_done = asyncio.Event()
        workflow_error = None
        
        def stream_callback(event_type: str, data: dict):
            """Callback to receive events from workflow"""
            try:
                logger.info(f"🔔 Stream callback: {event_type} - {data}")
                
                if event_type == 'slide_completed' and 'html_path' in data:
                    temp_path = data['html_path']
                    data['html_path'] = temp_path
                    data['is_temp'] = True
                    logger.info(f"🎯 Streaming temp file: {temp_path}")
                
                event_queue.put_nowait((event_type, data))
            except Exception as e:
                logger.error(f"Error in stream callback: {e}")
        
        async def run_workflow():
            """Run workflow in background"""
            nonlocal workflow_error, temp_workflow_dir
            try:
                if not workflow_service or not workflow_service.is_available():
                    raise Exception("Workflow service not available")
                
                workflow_result = await workflow_service.process_manual_structure(
                    slide_chunks=slide_chunks,
                    document_title=document_title,
                    output_folder=str(output_folder),
                    callback=stream_callback
                )
                
                if not workflow_result:
                    raise Exception("Workflow did not produce valid output")
                
                result_zip, temp_workflow_dir = workflow_result
                logger.info(f"📁 Temp directory: {temp_workflow_dir}")
                logger.info(f"📦 Result ZIP: {result_zip}")
                
                if result_zip and os.path.exists(result_zip):
                    html_folder = output_folder / "html"
                    html_folder.mkdir(exist_ok=True)
                    
                    with zipfile.ZipFile(result_zip, 'r') as zip_ref:
                        for file_info in zip_ref.infolist():
                            if not file_info.filename.endswith('/') and 'temp_debug' not in file_info.filename:
                                try:
                                    zip_ref.extract(file_info, output_folder)
                                except Exception as e:
                                    logger.warning(f"Error extracting {file_info.filename}: {e}")
                    
                    if conversion_service and conversion_service.is_available():
                        converted_folder = output_folder / "converted"
                        converted_folder.mkdir(exist_ok=True)
                        conversion_service.convert_slides_batch(html_folder, converted_folder)
                    
                    html_files = list(html_folder.glob("*.html"))
                    total_slides = len(html_files)
                    logger.info(f"📁 Found {total_slides} HTML files")
                    
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
        
        workflow_task = asyncio.create_task(run_workflow())
        
        try:
            while not workflow_done.is_set() or not event_queue.empty():
                try:
                    event_type, data = await asyncio.wait_for(event_queue.get(), timeout=0.5)
                    
                    logger.info(f"📤 Sending SSE: {event_type} - {data}")
                    event_data = json.dumps(data)
                    yield f"event: {event_type}\ndata: {event_data}\n\n"
                    
                except asyncio.TimeoutError:
                    yield f": keepalive\n\n"
                    continue
            
            if workflow_error:
                error_data = json.dumps({"message": workflow_error})
                yield f"event: error_event\ndata: {error_data}\n\n"
            
        except Exception as e:
            logger.error(f"Error in event generator: {e}")
            error_data = json.dumps({"message": str(e)})
            yield f"event: error_event\ndata: {error_data}\n\n"
        finally:
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

@router.post("/from-idea")
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


@router.get("/from-idea-stream")
async def generate_from_idea_stream(
    session_id: str = Query(..., description="Session ID for idea-based generation"),
    token: str = Query(..., description="Authentication token (required)")
):
    """Stream processing of idea-generated slides with Server-Sent Events - Requires Authentication"""
    
    # Required authentication - validate token
    logger.info(f"🔐 Authenticating idea generation request with token: {token[:20] if token else 'None'}...")
    
    # Check if token is missing or is the string "null"
    if not token or token == "null" or not token.strip():
        logger.error("❌ Authentication failed: No valid token provided")
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in to generate slides."
        )
    
    # Decode and validate token
    try:
        from authentication_router import decode_access_token
        token_data = decode_access_token(token)
        from web.backend.app.resource.database import get_user_by_email
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