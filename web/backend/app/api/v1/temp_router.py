from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import logging
import shutil
from pathlib import Path

router = APIRouter(prefix="/temp", tags=["TEMP"])
logger = logging.getLogger("SlideGen-temp")

@router.get("/file")
async def serve_temp_file(path: str):
    """Serve file from temporary workflow directory via query parameter"""
    logger.info(f"📂 Serving temp file request: {path}")
    
    # Security: only allow serving from slidegen_workflow_*, slidegen_idea_*, or slidegen_manual_* directories
    normalized_path = path.replace('\\', '/')
    is_linux_workflow = normalized_path.startswith('/tmp/slidegen_workflow_')
    is_linux_idea = normalized_path.startswith('/tmp/slidegen_idea_')
    is_linux_manual = normalized_path.startswith('/tmp/slidegen_manual_')
    is_windows_temp = ('slidegen_workflow_' in normalized_path or 'slidegen_idea_' in normalized_path or 'slidegen_manual_' in normalized_path) and ('Temp' in path or 'temp' in path)
    
    if not (is_linux_workflow or is_linux_idea or is_linux_manual or is_windows_temp):
        logger.warning(f"⚠️ Access denied for path: {path}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = Path(path)
    if not file_path.exists():
        logger.warning(f"⚠️ File not found: {path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    logger.info(f"✅ Serving temp file: {path}")
    return FileResponse(file_path)


@router.post("/cleanup")
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