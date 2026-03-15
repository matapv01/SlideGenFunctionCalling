# File: backend/api/v1/temp_router.py

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import FileResponse, JSONResponse
import logging
import shutil
from pathlib import Path
from backend.config import TEMP_DIR
from backend.api.dependencies import get_current_active_user
from backend.api.schemas.auth_schema import UserResponse

router = APIRouter(prefix="/temp", tags=["TEMP"])
logger = logging.getLogger("SlideGen-temp")


@router.get("/file")
async def serve_temp_file(path: str):
    """Serve file from temporary workflow or output directory via query parameter"""
    try:
        requested_path = Path(path).resolve()
        base_temp_dir = Path(TEMP_DIR).resolve()
        base_output_dir = Path(TEMP_DIR).parent / "output" # or import OUTPUT_DIR
        from backend.config import OUTPUT_DIR
        base_output_dir = Path(OUTPUT_DIR).resolve()

        is_in_temp = requested_path.is_relative_to(base_temp_dir)
        is_in_output = requested_path.is_relative_to(base_output_dir)

        if not (is_in_temp or is_in_output):
            logger.warning(f"⚠️ Access denied (Path Traversal attempt): {path}")
            logger.info(f"DEBUG: requested_path={requested_path}, base_temp={base_temp_dir}, base_output={base_output_dir}")
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối: Tệp nằm ngoài khu vực cho phép")

        if not requested_path.exists() or not requested_path.is_file():
            logger.warning(f"⚠️ File not found: {path}")
            raise HTTPException(status_code=404, detail="Không tìm thấy tệp")
        
        # Only check naming convention if it's in TEMP_DIR
        if is_in_temp:
            relative_path = requested_path.relative_to(base_temp_dir)
            root_folder_name = relative_path.parts[0]
            if not root_folder_name.startswith("slidegen_"):
                 logger.warning(f"⚠️ Access denied (Invalid temp folder name): {root_folder_name}")
                 raise HTTPException(status_code=403, detail="Truy cập bị từ chối: Thư mục tạm không hợp lệ")

        return FileResponse(requested_path)
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_temp_directory(
    request: Request,
    _: UserResponse = Depends(get_current_active_user),
):
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
             logger.warning(f"⚠️ Cleanup denied (Outside TEMP_DIR): {temp_dir}")
             return JSONResponse(content={"success": False, "message": "Không được phép xóa thư mục này"})
        
        # 3. Kiểm tra tên folder (chỉ xóa folder slidegen_*)
        if not target_path.name.startswith("slidegen_"):
             logger.warning(f"⚠️ Cleanup denied (Invalid folder name): {target_path.name}")
             return JSONResponse(content={"success": False, "message": "Tên thư mục không hợp lệ để xóa"})

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