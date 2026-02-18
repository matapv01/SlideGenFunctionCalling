# File: backend/api/v1/temp_router.py

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
import logging
import shutil
from pathlib import Path
from backend.config import TEMP_DIR

router = APIRouter(prefix="/temp", tags=["TEMP"])
logger = logging.getLogger("SlideGen-temp")


@router.get("/file")
async def serve_temp_file(path: str):
    """Serve file from temporary workflow directory via query parameter"""
    try:
        requested_path = Path(path).resolve()
        base_temp_dir = Path(TEMP_DIR).resolve()

        if not requested_path.is_relative_to(base_temp_dir):
            logger.warning(f"⚠️ Access denied (Path Traversal attempt): {path}")
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối: Tệp nằm ngoài thư mục tạm")

        if not requested_path.exists() or not requested_path.is_file():
            logger.warning(f"⚠️ File not found: {path}")
            raise HTTPException(status_code=404, detail="Không tìm thấy tệp")
        
        relative_path = requested_path.relative_to(base_temp_dir)
        root_folder_name = relative_path.parts[0]
        
        if not root_folder_name.startswith("slidegen_"):
             logger.warning(f"⚠️ Access denied (Invalid folder name): {root_folder_name}")
             raise HTTPException(status_code=403, detail="Truy cập bị từ chối: Thư mục tạm không hợp lệ")

        return FileResponse(requested_path)
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_temp_directory(request: Request):
    """Clean up temporary workflow directory when user navigates to editor"""
    try:
        data = await request.json()
        temp_dir = data.get('temp_dir')
        
        if not temp_dir:
            return JSONResponse(content={"success": False, "message": "No temp directory specified"})
        
        # 1. Chuẩn hóa và Resolve
        target_path = Path(temp_dir).resolve()
        base_temp_dir = Path(TEMP_DIR).resolve()

        # 2. Kiểm tra bảo mật: Phải nằm trong TEMP_DIR
        if not target_path.is_relative_to(base_temp_dir):
             raise HTTPException(status_code=403, detail="Thư mục tạm không hợp lệ: Nằm ngoài phạm vi")
        
        # 3. Kiểm tra tên folder (chỉ xóa folder slidegen_*)
        if not target_path.name.startswith("slidegen_"):
             raise HTTPException(status_code=403, detail="Thư mục tạm không hợp lệ: Sai quy ước đặt tên")

        # 4. Xóa
        if target_path.exists():
            shutil.rmtree(target_path)
            logger.info(f"🗑️ Cleaned up temp directory: {temp_dir}")
            return JSONResponse(content={"success": True, "message": "Temp directory cleaned"})
        else:
            return JSONResponse(content={"success": False, "message": "Temp directory not found"})
    
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)