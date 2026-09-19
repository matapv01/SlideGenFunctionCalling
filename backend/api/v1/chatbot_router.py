from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse

from backend.config import (
    CHATBOT_DEFAULT_EFFORT,
    CHATBOT_DEFAULT_MODEL,
    CHATBOT_EFFORT_CONFIGS,
    CHATBOT_MODEL_CONFIGS,
)
from backend.api.dependencies import (
    get_current_active_user,
    get_project_service,
    get_chatbot_service,
    get_document_rag_service,
    get_subscription_service,
)
from backend.api.schemas.auth_schema import UserResponse
from backend.api.schemas.chatbot_schema import (
    ChatMessageCreate,
    ChatMessageOut,
    ChatbotConfigOut,
    ChatbotEffortConfigOut,
    ChatbotModelConfigOut,
    ChatSessionCreate,
    ChatSessionOut,
    ChatTurnOut,
    ChatDocumentOut,
    ChatMessageJobOut,
    ChatSlideGenerationOut,
)
from backend.application.services.chatbot_service import (
    ChatbotService,
    ChatMessageInProgressError,
    SlideGenerationInProgressError,
)
from backend.application.services.project_service import ProjectService
from backend.application.services.document_rag_service import (
    DocumentRagService,
    DocumentUploadLimitError,
)
from backend.application.services.subscription_service import SlideCountLimitError, SubscriptionService
from backend.domain.entities.chat import ChatMessage, ChatSession

router = APIRouter(prefix="/chat", tags=["CHATBOT"])
logger = logging.getLogger(__name__)


def _sse_event(event_type: str, payload: dict) -> str:
    return (
        f"event: {event_type}\n"
        f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"
    )


@router.get("/config", response_model=ChatbotConfigOut)
async def get_chatbot_config(
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> ChatbotConfigOut:
    limits = chatbot.get_slide_generation_limits(current_user.id)
    usage_config = subscription_service.get_admin_usage_config()
    upload_limits = subscription_service.get_upload_limits_for_user(current_user.id)
    model_weights = {item["id"]: item["multiplier"] for item in usage_config["model_weights"]}
    effort_weights = {item["id"]: item["multiplier"] for item in usage_config["effort_weights"]}
    return ChatbotConfigOut(
        default_model=CHATBOT_DEFAULT_MODEL,
        default_effort=CHATBOT_DEFAULT_EFFORT,
        models=[
            ChatbotModelConfigOut(
                id=model_id,
                temperature=float(config["temperature"]),
                top_p=float(config["top_p"]),
                usage_multiplier=float(model_weights.get(model_id, 1.0)),
            )
            for model_id, config in CHATBOT_MODEL_CONFIGS.items()
        ],
        efforts=[
            ChatbotEffortConfigOut(
                id=effort_id,
                max_tokens=int(config["max_tokens"]),
                temperature_delta=float(config["temperature_delta"]),
                usage_multiplier=float(effort_weights.get(effort_id, 1.0)),
            )
            for effort_id, config in CHATBOT_EFFORT_CONFIGS.items()
        ],
        max_slide_count=limits["max_slide_count"],
        max_upload_bytes=upload_limits["max_file_bytes"],
        max_total_upload_bytes=upload_limits["max_total_bytes"],
    )


def _session_out(session: ChatSession) -> ChatSessionOut:
    return ChatSessionOut(
        id=session.id,
        project_id=session.project_id,
        title=session.title,
        history_summary=session.history_summary,
        max_turns=session.max_turns,
        created_at=session.created_at,
        updated_at=session.updated_at,
        archived=session.archived,
    )


def _message_out(message: ChatMessage) -> ChatMessageOut:
    return ChatMessageOut(
        id=message.id,
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        standalone_query=message.standalone_query,
        model=message.model,
        effort=message.effort,
        metadata=message.metadata,
        created_at=message.created_at,
    )


def _document_out(document) -> ChatDocumentOut:
    return ChatDocumentOut(
        id=document.id,
        original_filename=document.original_filename,
        title=document.title,
        status=document.status,
        content_hash=document.content_hash,
        size_bytes=document.size_bytes,
        error_message=document.error_message,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


@router.post("/sessions", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    body: ChatSessionCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
    project_service: ProjectService = Depends(get_project_service),
) -> ChatSessionOut:
    if body.project_id is not None:
        project_service.require_project_access(body.project_id, current_user.id)
    return _session_out(
        chatbot.create_session(
            current_user.id, project_id=body.project_id, title=body.title
        )
    )


@router.get("/sessions", response_model=list[ChatSessionOut])
async def list_chat_sessions(
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> list[ChatSessionOut]:
    return [_session_out(session) for session in chatbot.list_sessions(current_user.id)]


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageOut])
async def list_chat_messages(
    session_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> list[ChatMessageOut]:
    if chatbot.get_session(session_id, current_user.id) is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
    return [
        _message_out(message)
        for message in chatbot.list_messages(session_id, current_user.id)
    ]


@router.post(
    "/sessions/{session_id}/documents",
    response_model=ChatDocumentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_chat_document(
    session_id: str,
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
    rag: DocumentRagService = Depends(get_document_rag_service),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> ChatDocumentOut:
    session = chatbot.get_session(session_id, current_user.id)
    if session is None or session.archived:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
    upload_limits = subscription_service.get_upload_limits_for_user(current_user.id)
    content = await file.read(upload_limits["max_file_bytes"] + 1)
    # Uploading only stores the source document; it still consumes one
    # document unit in the shared five-hour window.
    subscription_service.check_feature_access_for_user(current_user.id, "docx_upload")
    try:
        document = await rag.create_pending_docx(
            session=session,
            original_filename=file.filename or "document.docx",
            content=content,
            max_file_bytes=upload_limits["max_file_bytes"],
            max_total_bytes=upload_limits["max_total_bytes"],
        )
        subscription_service.increment_usage(current_user.id, "docx_upload")
    except DocumentUploadLimitError as exc:
        raise HTTPException(status_code=413, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        logger.exception("Chat document upload failed for session %s", session_id)
        raise HTTPException(status_code=503, detail="Không thể tải tài liệu DOCX")
    return _document_out(document)


@router.get(
    "/sessions/{session_id}/documents",
    response_model=list[ChatDocumentOut],
)
async def list_chat_documents(
    session_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
    rag: DocumentRagService = Depends(get_document_rag_service),
) -> list[ChatDocumentOut]:
    session = chatbot.get_session(session_id, current_user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
    return [
        _document_out(document)
        for document in rag.list_session_documents(session_id, current_user.id)
    ]


@router.delete(
    "/sessions/{session_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat_document(
    session_id: str,
    document_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
    rag: DocumentRagService = Depends(get_document_rag_service),
) -> None:
    session = chatbot.get_session(session_id, current_user.id)
    if session is None or session.archived:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
    try:
        rag.remove_document_from_session(session=session, document_id=document_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")


@router.post("/sessions/{session_id}/messages", response_model=ChatTurnOut)
async def send_chat_message(
    session_id: str,
    body: ChatMessageCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> ChatTurnOut:
    try:
        result = await chatbot.send_message(
            session_id,
            current_user.id,
            body.content,
            model_name=body.model,
            effort=body.effort,
            canvas_enabled=body.canvas,
            slide_count=body.slide_count,
            document_ids=body.document_ids,
        )
    except HTTPException:
        raise
    except LookupError:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
    except SlideGenerationInProgressError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except SlideCountLimitError as exc:
        raise HTTPException(
            status_code=413,
            detail={
                "code": "slide_count_limit",
                "requested": exc.requested,
                "max_slide_count": exc.maximum,
                "tier": exc.tier,
                "message": str(exc),
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        logger.exception("Chatbot request failed for session %s", session_id)
        raise HTTPException(status_code=503, detail="Chatbot unavailable")
    return ChatTurnOut(
        session=_session_out(result.session),
        user_message=_message_out(result.user_message),
        assistant_message=_message_out(result.assistant_message),
        standalone_query=result.standalone_query,
        citations=result.citations,
        project_id=result.project_id,
    )


def _chat_message_stream(
    chatbot: ChatbotService,
    job_id: str,
    user_id: int,
) -> StreamingResponse:
    try:
        job, events = chatbot.subscribe_chat_message(job_id, user_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Không tìm thấy tiến trình chat")

    async def event_stream():
        try:
            while True:
                _, event_type, payload = await events.get()
                yield _sse_event(event_type, payload)
                if event_type in {"complete", "error_event", "cancelled"}:
                    break
        finally:
            # The detached task keeps working after the browser disconnects.
            chatbot.unsubscribe_chat_message(job, events)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/message-jobs/active",
    response_model=ChatMessageJobOut | None,
)
async def get_active_chat_message_job(
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> dict | None:
    """Return an ordinary chat job that a new tab can reconnect to."""
    return chatbot.get_active_chat_message(current_user.id)


@router.post("/message-jobs/active/cancel")
async def cancel_active_chat_message(
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> dict[str, bool]:
    """Interrupt the user's current ordinary chat response."""
    return {"cancelled": chatbot.cancel_active_chat_message(current_user.id)}


@router.get("/message-jobs/{job_id}/stream")
async def reconnect_chat_message_job(
    job_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> StreamingResponse:
    return _chat_message_stream(chatbot, job_id, current_user.id)


@router.post("/sessions/{session_id}/message-stream")
async def stream_chat_message(
    session_id: str,
    body: ChatMessageCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> StreamingResponse:
    """Start a reconnectable ordinary chat response and subscribe to it."""
    try:
        job = chatbot.start_chat_message(
            session_id,
            current_user.id,
            body.content,
            model_name=body.model,
            effort=body.effort,
            slide_count=body.slide_count,
            document_ids=body.document_ids,
        )
    except ChatMessageInProgressError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except LookupError:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _chat_message_stream(chatbot, job.id, current_user.id)


def _slide_generation_stream(
    chatbot: ChatbotService,
    generation_id: str,
    user_id: int,
) -> StreamingResponse:
    try:
        job, events = chatbot.subscribe_slide_generation(generation_id, user_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Không tìm thấy tiến trình tạo slide")

    async def event_stream():
        try:
            while True:
                _, event_type, payload = await events.get()
                yield _sse_event(event_type, payload)
                if event_type in {"complete", "error_event", "limit_event"}:
                    break
        finally:
            # Disconnecting a browser stream only removes this subscriber. The
            # detached generation task intentionally continues in the service.
            chatbot.unsubscribe_slide_generation(job, events)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/slide-generations/active",
    response_model=ChatSlideGenerationOut | None,
)
async def get_active_chat_slide_generation(
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> dict | None:
    """Return the current user's detached job so a browser can restore it."""
    return chatbot.get_active_slide_generation(current_user.id)


@router.get("/slide-generations/{generation_id}/stream")
async def reconnect_chat_slide_generation(
    generation_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> StreamingResponse:
    """Reconnect to a job after a tab reload or route change."""
    return _slide_generation_stream(chatbot, generation_id, current_user.id)


@router.post("/sessions/{session_id}/slide-stream")
async def stream_chat_slide_generation(
    session_id: str,
    body: ChatMessageCreate,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> StreamingResponse:
    """Start one detached job and subscribe to its event stream."""
    try:
        job = chatbot.start_slide_generation(
            session_id,
            current_user.id,
            body.content,
            model_name=body.model,
            effort=body.effort,
            slide_count=body.slide_count,
            document_ids=body.document_ids,
        )
    except SlideGenerationInProgressError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except LookupError:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return _slide_generation_stream(chatbot, job.id, current_user.id)


@router.post("/sessions/{session_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_chat_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    chatbot: ChatbotService = Depends(get_chatbot_service),
) -> None:
    try:
        chatbot.archive_session(session_id, current_user.id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat")
