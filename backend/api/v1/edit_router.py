# File: backend/api/v1/edit_router.py

from fastapi import APIRouter, HTTPException, Depends
import logging
from backend.api.schemas.edit_schema import (
    StructureUpdateRequest, 
    StructureApproveRequest, 
    StructureResponse,
    ApprovedStructureResponse
)
from backend.api.dependencies import get_structure_service
from backend.application.services.structure_service import StructureService

router = APIRouter(prefix="/structure", tags=["STRUCTURE"])
logger = logging.getLogger("SlideGen-Structure")


@router.get("/current", response_model=StructureResponse)
async def get_current_structure(
    session_id: str,
    service: StructureService = Depends(get_structure_service)
):
    """Lấy cấu trúc hiện tại để biên tập"""
    session_data = service.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session không tồn tại hoặc đã hết hạn")

    return {
        "document_title": session_data.get("document_title", "Untitled"),
        "document_text": session_data.get("document_text", ""),
        "document_structure": session_data.get("document_structure", []),
        "can_edit": True
    }


@router.put("/update")
async def update_structure(
    request: StructureUpdateRequest,
    service: StructureService = Depends(get_structure_service)
):
    """Lưu thay đổi cấu trúc từ người dùng"""
    try:
        service.update_session_structure(
            session_id=request.session_id,
            structure=[node.model_dump() for node in request.document_structure],
            intro_slide=request.intro_slide.model_dump() if request.intro_slide else None
        )
        return {"success": True, "message": "Cấu trúc đã được lưu"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật: {str(e)}")


@router.post("/approve", response_model=ApprovedStructureResponse)
async def approve_structure(
    request: StructureApproveRequest,
    service: StructureService = Depends(get_structure_service)
):
    """Xác nhận cấu trúc và chuẩn bị dữ liệu cho AI Workflow"""
    try:
        # Service thực hiện thuật toán Tree -> Flattened List
        result = service.approve_structure(request.session_id)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Không tìm thấy file cấu trúc tạm thời")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý cấu trúc: {str(e)}")


@router.post("/test-session")
async def create_test_session(service: StructureService = Depends(get_structure_service)):
    """Tạo session giả lập để debug giao diện editor"""
    session_id = service.create_session(
        filename="Demo_Tài_Liệu.docx",
        full_text="Nội dung giả lập...",
        paragraphs=[],
        docx_path=""
    )
    # Khởi tạo cấu trúc mặc định
    service.update_session_structure(session_id, [
        {"level": 1, "title": "Giới thiệu chung", "content": "Nội dung mục 1", "children": []}
    ])
    
    return {
        "success": True, 
        "session_id": session_id,
        "redirect_url": f"/frontend/structure-editor.html?session={session_id}"
    }