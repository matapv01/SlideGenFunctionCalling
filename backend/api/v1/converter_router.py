# File: backend/api/v1/converter_router.py

from fastapi import APIRouter, HTTPException, Depends
from backend.api.dependencies import get_conversion_service
from backend.application.services.conversion_service import ConversionService
import logging
from backend.config import (
    OUTPUT_DIR
)
from backend.api.schemas.converter_schema import (
    ConvertRequest,
    ConversionResponse,
    ConversionStatusResponse,
    ConverterHealthResponse
)

router = APIRouter(prefix="/convert", tags=["CONVERT"])
logger = logging.getLogger("SlideGen-Convert")

@router.post("", response_model=ConversionResponse)
async def convert_slides(
    data: ConvertRequest,
    service: ConversionService = Depends(get_conversion_service)
):
    """Convert HTML slides to absolute positioning"""
    if service is None:
        raise HTTPException(status_code=503, detail="Bộ chuyển đổi không khả dụng")
    
    project_name = data.get("project_name")
    if not project_name:
        raise HTTPException(status_code=400, detail="Thiếu project_name")
    
    output_folder = OUTPUT_DIR / project_name
    if not output_folder.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    
    html_folder = output_folder / "html"
    converted_folder = output_folder / "converted"
    
    if not html_folder.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy thư mục HTML")
    
    try:
        converted_folder.mkdir(exist_ok=True)
        conversion_result = service.convert_slides_batch(html_folder, converted_folder)
        
        return {
            "success": True,
            "conversion_result": conversion_result,
            "message": f"Converted {len(conversion_result['success'])} slides successfully"
        }
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        raise HTTPException(status_code=500, detail=f"Chuyển đổi thất bại: {str(e)}")


@router.get("/status/{project_name}", response_model=ConversionStatusResponse)
async def get_conversion_status(
    project_name: str,
    service: ConversionService = Depends(get_conversion_service)
):
    """Get conversion status for a project"""
    if service is None:
        raise HTTPException(status_code=503, detail="Bộ chuyển đổi không khả dụng")
    
    output_folder = OUTPUT_DIR / project_name
    if not output_folder.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy dự án")
    
    html_folder = output_folder / "html"
    converted_folder = output_folder / "converted"
    
    if not html_folder.exists():
        raise HTTPException(status_code=404, detail="Không tìm thấy thư mục HTML")
    
    status = service.get_conversion_status(html_folder, converted_folder)
    
    return {
        "project_name": project_name,
        "status": status,
        "has_converted": converted_folder.exists()
    }


@router.get("/health", response_model=ConverterHealthResponse)
async def check_converter_health(
    service: ConversionService = Depends(get_conversion_service)
):
    """Check converter system health"""
    if service is None:
        return {
            "healthy": False,
            "message": "Converter is disabled or not initialized"
        }
    
    return service.check_health()