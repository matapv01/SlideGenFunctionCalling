# File: backend/api/v1/edit_router.py

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
import logging
import os
import uuid
from pathlib import Path

from backend.api.schemas.edit_schema import (
    StructureUpdateRequest,
    StructureApproveRequest,
    StructureResponse,
    ApprovedStructureResponse
)
from backend.api.schemas.auth_schema import UserResponse
from backend.api.dependencies import get_current_active_user, get_manual_workflow_service, get_structure_service
from backend.application.services.manual_workflow_service import ManualWorkflowService
from backend.application.services.structure_service import StructureService
from backend.config import TEMP_DIR

router = APIRouter(prefix="/structure", tags=["STRUCTURE"])
logger = logging.getLogger("SlideGen-Structure")


@router.post("/manual-session")
async def create_manual_session(
    file: UploadFile = File(...),
    service: StructureService = Depends(get_structure_service)
):
    """Upload DOCX, persist images locally, normalize markdown, and create manual editor session."""
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
    except Exception as exc:
        logger.error("Không thể lưu tệp DOCX: %s", exc)
        raise HTTPException(status_code=500, detail="Không thể xử lý tệp tải lên")

    try:
        from markitdown import MarkItDown
        from backend.workflows.doc_workflow.nodes.document_converter import parse_markdown_to_hierarchical_json
        from backend.workflows.slidegen_workflow.main import _extract_images_with_positions, _replace_base64_with_local_paths

        converter = MarkItDown()
        markdown_text = converter.convert(str(temp_path)).text_content or ""

        session_id = service.create_session(
            filename=safe_name,
            full_text=markdown_text,
            paragraphs=[],
            docx_path=str(temp_path)
        )

        session_temp_dir = TEMP_DIR / f"slidegen_{session_id}"
        session_temp_dir.mkdir(parents=True, exist_ok=True)
        images_dir = session_temp_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        image_infos = _extract_images_with_positions(str(temp_path), str(images_dir))
        normalized_markdown = _replace_base64_with_local_paths(markdown_text, image_infos, str(images_dir))
        normalized_markdown = normalized_markdown.replace("images/", f"{session_temp_dir.as_posix()}/images/")

        document_title, document_structure = parse_markdown_to_hierarchical_json(normalized_markdown)
        if not document_title.strip():
            document_title = Path(safe_name).stem

        service._sessions[session_id]["document_title"] = document_title
        service._sessions[session_id]["document_text"] = normalized_markdown
        service._sessions[session_id]["document_structure"] = document_structure
        service._sessions[session_id]["manual_images_dir"] = str(images_dir)

        service.update_session_structure(
            session_id=session_id,
            structure=document_structure,
            intro_slide=None,
        )

        logger.info("✅ Manual session created: %s (%s image(s))", session_id, len(image_infos))

        return {
            "success": True,
            "session_id": session_id,
            "document_title": document_title,
            "text_length": len(normalized_markdown),
            "paragraph_count": len(document_structure)
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
    service: StructureService = Depends(get_structure_service),
    manual_workflow_service: ManualWorkflowService = Depends(get_manual_workflow_service),
):
    """Lấy cấu trúc hiện tại để biên tập"""
    session_data = service.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session không tồn tại hoặc đã hết hạn")

    document_title = session_data.get("document_title", "Untitled")
    document_structure = session_data.get("document_structure", [])

    persisted = manual_workflow_service.get_persisted_structure(session_id)
    if persisted:
        try:
            document_title = persisted.get("document_title", document_title)
            document_structure = persisted.get("document_structure", document_structure)
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
    _: UserResponse = Depends(get_current_active_user),
    manual_workflow_service: ManualWorkflowService = Depends(get_manual_workflow_service),
):
    """Lưu thay đổi cấu trúc từ người dùng"""
    try:
        result = await manual_workflow_service.update_structure(
            session_id=request.session_id,
            document_structure=[node.model_dump() for node in request.document_structure],
            intro_slide=request.intro_slide.model_dump() if request.intro_slide else None,
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật: {str(e)}")


@router.post("/approve", response_model=ApprovedStructureResponse)
async def approve_structure(
    request: StructureApproveRequest,
    _: UserResponse = Depends(get_current_active_user),
    manual_workflow_service: ManualWorkflowService = Depends(get_manual_workflow_service),
):
    """Xác nhận cấu trúc và chuẩn bị dữ liệu cho AI Workflow qua manual_workflow."""
    try:
        return await manual_workflow_service.approve_structure_from_session(request.session_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý cấu trúc: {str(e)}")
