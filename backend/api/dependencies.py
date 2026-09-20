# File: backend/api/dependencies.py

from backend.config import (
    CAPTURES_DIR, PROJECT_DIR, STATIC_DIR,
    LLM_API_KEY,
    LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TOP_P,
    VLM_API_KEY, VLM_MODEL, VLM_BASE_URL,
    LLM_REQUEST_MAX_CONCURRENCY,
    LLM_REQUEST_TIMEOUT_SECONDS, VLM_REQUEST_TIMEOUT_SECONDS,
    CHATBOT_MAX_HISTORY_TURNS,
    FAISS_INDEX_PATH,
)
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.workflows.slidegen_workflow.tools.tool_des_xml import TOOLS_DICT

# --- 1. Imports Interfaces (Ports) ---
from backend.domain.ports.user_repository import UserRepository
from backend.domain.ports.project_repository import ProjectRepository
from backend.domain.ports.llm_provider import LLMProvider
from backend.domain.ports.capture_provider import CaptureProvider
from backend.domain.ports.parser_provider import ParserProvider
from backend.domain.ports.tool_retrieve_provider import ToolRetrieveProvider

# --- 2. Imports Implementation (Infrastructure) ---
from backend.infrastructure.llm.gemini_provider import GeminiLLMProvider
from backend.infrastructure.llm.request_limiter import LLMRequestLimiter
from backend.infrastructure.database.repositories.sqlite_user_repo import SqliteUserRepository
from backend.infrastructure.database.repositories.sqlite_project_repo import SqliteProjectRepository
from backend.infrastructure.capture.playwright_provider import PlaywrightCaptureProvider
from backend.infrastructure.parser.markitdown_parser import MarkItDownParser
from backend.infrastructure.rag.gemini_provider import LocalEmbeddingToolRetrieveProvider
from backend.infrastructure.database.repositories.sqlite_chat_repo import SqliteChatRepository
from backend.infrastructure.database.repositories.sqlite_chat_document_repo import SqliteChatDocumentRepository
from backend.infrastructure.database.repositories.sqlite_usage_config_repo import SqliteUsageConfigRepository

# --- 3. Imports Services (Application) ---
from backend.application.services.auth_service import AuthService
from backend.application.services.user_service import UserService
from backend.application.services.project_service import ProjectService
from backend.application.services.capture_service import CaptureService
from backend.application.services.structure_service import StructureService
from backend.application.services.slide_service import SlideService
from backend.application.services.document_preprocessing_service import (
    DocumentPreprocessingService,
)
from backend.application.services.manual_workflow_service import ManualWorkflowService
from backend.application.services.legacy_docx_generation_service import (
    LegacyDocxGenerationService,
)
from backend.application.services.slidegen_workflow_service import SlideGenWorkflowService
from backend.application.services.subscription_service import SubscriptionService
from backend.application.services.collaboration_service import CollaborationService
from backend.application.services.chatbot_service import ChatbotService
from backend.application.services.document_rag_service import DocumentRagService
from backend.application.services.rag_query_planner import RagQueryPlanner
from backend.application.services.slide_generation_service import SlideGenerationService
from backend.application.services.image_relevance_service import ImageRelevanceService

from backend.api.schemas.auth_schema import UserResponse

security = HTTPBearer()

# ===== SINGLETON INFRASTRUCTURE INSTANCES =====
# Khởi tạo 1 lần duy nhất khi Server start

# Infrastructure global instances
_capture_infra = PlaywrightCaptureProvider()
_parser_infra = MarkItDownParser()

# LLM and VLM currently point to the same Qwen endpoint. Use one endpoint-wide
# gate so planner/generator traffic and multimodal verification cannot combine
# into an accidental 5 + 5 concurrent burst.
_qwen_request_limiter = LLMRequestLimiter(LLM_REQUEST_MAX_CONCURRENCY)

_slidegen_llm = GeminiLLMProvider(
    api_keys=[LLM_API_KEY] if LLM_API_KEY else [],
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    temperature=LLM_TEMPERATURE,
    max_tokens=LLM_MAX_TOKENS,
    top_p=LLM_TOP_P,
    request_limiter=_qwen_request_limiter,
    request_timeout=LLM_REQUEST_TIMEOUT_SECONDS,
)
_vlm_provider = GeminiLLMProvider(
    api_keys=[VLM_API_KEY] if VLM_API_KEY else [],
    model=VLM_MODEL,
    base_url=VLM_BASE_URL,
    temperature=LLM_TEMPERATURE,
    max_tokens=LLM_MAX_TOKENS,
    top_p=LLM_TOP_P,
    request_limiter=_qwen_request_limiter,
    request_timeout=VLM_REQUEST_TIMEOUT_SECONDS,
)
_retriever_infra = LocalEmbeddingToolRetrieveProvider(
    tools_dict=TOOLS_DICT,
    index_path=str(FAISS_INDEX_PATH),
)
_image_relevance_service = ImageRelevanceService(
    _vlm_provider,
    model=VLM_MODEL,
)

# ===== SINGLETON SERVICES =====
_structure_service = StructureService()
_slide_service = SlideService(static_dir=STATIC_DIR)

_manual_workflow_service = ManualWorkflowService(
    project_dir=str(PROJECT_DIR)
)

_document_preprocessing_service = DocumentPreprocessingService(
    project_dir=str(PROJECT_DIR),
    llm_provider=_slidegen_llm,
    llm_request_limiter=_qwen_request_limiter,
)

_slidegen_workflow_service = SlideGenWorkflowService(
    project_dir=str(PROJECT_DIR),
    llm_provider=_slidegen_llm,
    planner_llm_provider=_slidegen_llm,
    capture_provider=_capture_infra,
    parser_provider=_parser_infra,
    tool_retriever=_retriever_infra,
    image_relevance_verifier=_image_relevance_service,
    llm_request_limiter=_qwen_request_limiter,
)

# The old DOCX endpoints are adapters. They preprocess the file and then call
# the same canonical chunk renderer used by chatbot generation.
_legacy_docx_generation_service = LegacyDocxGenerationService(
    document_preprocessor=_document_preprocessing_service,
    slide_workflow=_slidegen_workflow_service,
)

# Chatbot document RAG reuses the existing local embedding model and SQLite
# connection. It does not create a second database or import the clone's
# PostgreSQL runtime.
_chat_document_repo = SqliteChatDocumentRepository()
_document_rag_service = DocumentRagService(
    repository=_chat_document_repo,
    embedding_provider=_retriever_infra.embeddings,
    preprocessing_service=_document_preprocessing_service,
)
_chat_project_service = ProjectService(SqliteProjectRepository())
_chatbot_user_repository = SqliteUserRepository()
_chatbot_usage_config_repository = SqliteUsageConfigRepository()
_chatbot_subscription_service = SubscriptionService(
    _chatbot_user_repository,
    _chatbot_usage_config_repository,
)
_slide_generation_service = SlideGenerationService(
    llm_provider=_slidegen_llm,
    slide_workflow=_slidegen_workflow_service,
    project_service=_chat_project_service,
)
_rag_query_planner = RagQueryPlanner(_slidegen_llm)

# Chatbot is an isolated application service with its own session repository,
# while reusing the existing configured LLM, document preprocessing and
# project slide workflow.
_chatbot_service = ChatbotService(
    repository=SqliteChatRepository(),
    llm_provider=_slidegen_llm,
    context_provider=_document_rag_service,
    slide_generator=_slide_generation_service,
    rag_query_planner=_rag_query_planner,
    user_repository=_chatbot_user_repository,
    subscription_service=_chatbot_subscription_service,
    default_max_turns=CHATBOT_MAX_HISTORY_TURNS,
)

def get_user_repo() -> UserRepository:
    return SqliteUserRepository()


def get_project_repo() -> ProjectRepository:
    return SqliteProjectRepository()


def get_llm_provider() -> LLMProvider:
    return _slidegen_llm


def get_capture_infra() -> CaptureProvider:
    return _capture_infra


def get_auth_service(user_repo: UserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)


def get_user_service(user_repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo)


def get_manual_workflow_service() -> ManualWorkflowService:
    return _manual_workflow_service


def get_document_preprocessing_service() -> DocumentPreprocessingService:
    return _document_preprocessing_service


def get_doc_workflow_service() -> DocumentPreprocessingService:
    """Legacy dependency name; canonical code uses the preprocessor getter."""
    return _document_preprocessing_service


def get_legacy_docx_generation_service() -> LegacyDocxGenerationService:
    return _legacy_docx_generation_service


def get_capture_service(
    infra: CaptureProvider = Depends(get_capture_infra)
) -> CaptureService:
    return CaptureService(captures_dir=CAPTURES_DIR, slide_capture=infra)


def get_project_service(
    project_repo: ProjectRepository = Depends(get_project_repo)
) -> ProjectService:
    return ProjectService(project_repo)


def get_structure_service() -> StructureService:
    return _structure_service


def get_slide_service() -> SlideService:
    return _slide_service


def get_slidegen_workflow_service() -> SlideGenWorkflowService:
    return _slidegen_workflow_service


def get_chatbot_service() -> ChatbotService:
    return _chatbot_service


def get_document_rag_service() -> DocumentRagService:
    return _document_rag_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repo)
) -> UserResponse:

    token = credentials.credentials
    email = auth_service.decode_access_token(token)

    user = user_repo.get_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vui lòng đăng nhập để sử dụng tính năng này",
            headers={"X-Auth-Required": "true"}
        )

    # Fetch profile to get full_name and avatar_url
    profile = user_repo.get_profile(user.id)
    full_name = profile.full_name if profile else None
    avatar_url = profile.avatar_url if profile else None
    username = full_name or user.email.split("@")[0]

    return UserResponse(
        id=user.id, email=user.email,
        created_at=user.created_at, is_active=bool(user.is_active),
        is_admin=bool(user.is_admin),
        onboarding_completed=bool(user.onboarding_completed),
        full_name=full_name, avatar_url=avatar_url, username=username
    )


async def get_current_active_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    return current_user


async def require_authentication_with_message():
    """Dependency that requires authentication and shows friendly login message"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Vui lòng đăng nhập để sử dụng tính năng này",
        headers={"X-Auth-Required": "true"}
    )


async def get_current_user_from_token_param(
    token: str = Query(...),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repo)
) -> UserResponse:
    email = auth_service.decode_access_token(token)
    user = user_repo.get_by_email(email)
    
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Không tìm thấy người dùng hoặc người dùng không hoạt động")

    return UserResponse(
        id=user.id, email=user.email,
        created_at=user.created_at, is_active=bool(user.is_active),
        is_admin=bool(user.is_admin),
    )


def get_subscription_service() -> SubscriptionService:
    return SubscriptionService(SqliteUserRepository(), SqliteUsageConfigRepository())


async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_active_user),
) -> UserResponse:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def get_collaboration_service(
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> CollaborationService:
    return CollaborationService(project_repo)
