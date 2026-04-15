# File: backend/api/v1/edit_router.py

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
import logging
import os
import json
import uuid
from pathlib import Path

from backend.api.schemas.edit_schema import (
    StructureUpdateRequest,
    StructureApproveRequest,
    StructureResponse,
    ApprovedStructureResponse
)
from backend.api.schemas.auth_schema import UserResponse
from backend.api.dependencies import get_structure_service, get_current_active_user
from backend.application.services.structure_service import StructureService
from backend.config import TEMP_DIR
from backend.workflows.manual_workflow.main import run_manual_approve_workflow, run_manual_update_workflow

router = APIRouter(prefix="/structure", tags=["STRUCTURE"])
logger = logging.getLogger("SlideGen-Structure")


@router.post("/manual-session")
async def create_manual_session(
    file: UploadFile = File(...),
    service: StructureService = Depends(get_structure_service)
):
    """Upload DOCX và khởi tạo session cho trình chỉnh sửa thủ công"""
    filename = file.filename or "document.docx"
    if not filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận tệp DOCX")

    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = os.path.basename(filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    temp_path = TEMP_DIR / unique_name

    try:
        file_bytes = await file.read()
        temp_path.write_bytes(file_bytes)
        from docx import Document
    except ImportError as exc:
        logger.error("python-docx chưa được cài đặt: %s", exc)
        raise HTTPException(status_code=500, detail="Thiếu thư viện python-docx")
    except Exception as exc:
        logger.error("Không thể lưu tệp DOCX: %s", exc)
        raise HTTPException(status_code=500, detail="Không thể xử lý tệp tải lên")

    try:
        doc = Document(temp_path)
        full_text = ""
        paragraphs_data = []
        for idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue
            start_pos = len(full_text)
            full_text += text + "\n\n"
            paragraphs_data.append({
                "index": idx,
                "text": text,
                "start_pos": start_pos,
                "end_pos": len(full_text)
            })

        session_id = service.create_session(
            filename=safe_name,
            full_text=full_text,
            paragraphs=paragraphs_data,
            docx_path=str(temp_path)
        )

        logger.info("✅ Manual session created: %s (%s paragraphs)", session_id, len(paragraphs_data))

        return {
            "success": True,
            "session_id": session_id,
            "document_title": Path(safe_name).stem,
            "text_length": len(full_text),
            "paragraph_count": len(paragraphs_data)
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Manual session error: %s", exc)
        raise HTTPException(status_code=500, detail="Không thể phân tích tài liệu")

@router.get("/current", response_model=StructureResponse)
async def get_current_structure(
    session_id: str,
    _: UserResponse = Depends(get_current_active_user),
    service: StructureService = Depends(get_structure_service)
):
    """Lấy cấu trúc hiện tại để biên tập"""
    session_data = service.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session không tồn tại hoặc đã hết hạn")

    document_title = session_data.get("document_title", "Untitled")
    document_structure = session_data.get("document_structure", [])

    # Prefer persisted structure from update-workflow when available.
    structure_file = TEMP_DIR / f"structure_{session_id}.json"
    if structure_file.exists():
        try:
            with open(structure_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            document_title = data.get("document_title", document_title)
            document_structure = data.get("document_structure", document_structure)
            session_data["document_title"] = document_title
            session_data["document_structure"] = document_structure
        except Exception as exc:
            logger.warning("Failed to read persisted structure for session %s: %s", session_id, exc)

    return {
        "document_title": document_title,
        "document_text": session_data.get("document_text", ""),
        "document_structure": document_structure,
        "can_edit": True
    }


@router.put("/update")
async def update_structure(
    request: StructureUpdateRequest,
    _: UserResponse = Depends(get_current_active_user)
):
    """Lưu thay đổi cấu trúc từ người dùng"""
    try:
        workflow_state = await run_manual_update_workflow(
            session_id=request.session_id,
            document_structure=[node.model_dump() for node in request.document_structure],
            intro_slide=request.intro_slide.model_dump() if request.intro_slide else None,
            graph_config={}
        )

        result = workflow_state.get("update_result")
        if not result:
            raise HTTPException(status_code=500, detail="Không thể lưu cấu trúc qua manual workflow")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật: {str(e)}")


@router.post("/approve", response_model=ApprovedStructureResponse)
async def approve_structure(
    request: StructureApproveRequest,
    _: UserResponse = Depends(get_current_active_user)
):
    """Xác nhận cấu trúc và chuẩn bị dữ liệu cho AI Workflow qua manual_workflow."""
    try:
        file_path = TEMP_DIR / f"structure_{request.session_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Không tìm thấy file cấu trúc tạm thời")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        document_title = data.get("document_title", "Untitled")
        document_structure = data.get("document_structure", [])

        workflow_state = await run_manual_approve_workflow(
            session_id=request.session_id,
            document_title=document_title,
            document_structure=document_structure,
            slide_options={},
            graph_config={}
        )

        result = workflow_state.get("approved_result")
        if not result:
            raise HTTPException(status_code=500, detail="Không thể tạo dữ liệu approve từ manual workflow")

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý cấu trúc: {str(e)}")
