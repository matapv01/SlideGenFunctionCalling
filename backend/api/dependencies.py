# File: backend/api/dependencies.py

from backend.config import (
    setup_environment,
    CAPTURES_DIR, PROJECT_DIR, STATIC_DIR,
    LLM_MODEL, LLM_BASE_URL, LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TOP_P,
    IDEA_STRUCTURE_LLM_MODEL, IDEA_STRUCTURE_LLM_TEMPERATURE, IDEA_STRUCTURE_LLM_MAX_TOKENS
)
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
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
from backend.infrastructure.database.repositories.sqlite_user_repo import SqliteUserRepository
from backend.infrastructure.database.repositories.sqlite_project_repo import SqliteProjectRepository
from backend.infrastructure.capture.playwright_provider import PlaywrightCaptureProvider
from backend.infrastructure.parser.markitdown_parser import MarkItDownParser
from backend.infrastructure.rag.gemini_provider import GeminiToolRetrieveProvider

# --- 3. Imports Services (Application) ---
from backend.application.services.auth_service import AuthService
from backend.application.services.user_service import UserService
from backend.application.services.project_service import ProjectService
from backend.application.services.idea_service import IdeaService
from backend.application.services.capture_service import CaptureService
from backend.application.services.structure_service import StructureService
from backend.application.services.slide_service import SlideService
from backend.application.services.doc_workflow_service import DocWorkflowService
from backend.application.services.idea_workflow_service import IdeaWorkflowService
from backend.application.services.manual_workflow_service import ManualWorkflowService
from backend.application.services.slidegen_workflow_service import SlideGenWorkflowService
from backend.application.services.subscription_service import SubscriptionService
from backend.application.services.collaboration_service import CollaborationService

from backend.api.schemas.auth_schema import UserResponse

security = HTTPBearer()

# ===== SINGLETON INFRASTRUCTURE INSTANCES =====
# Khởi tạo 1 lần duy nhất khi Server start

# 1. Load Env
env_keys = setup_environment()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 2. Infrastructure Global Instances
_capture_infra = PlaywrightCaptureProvider()
_parser_infra = MarkItDownParser()

_idea_llm = GeminiLLMProvider(
    api_keys=[GEMINI_API_KEY] if GEMINI_API_KEY else [],
    model=IDEA_STRUCTURE_LLM_MODEL,
    base_url=LLM_BASE_URL,
    temperature=IDEA_STRUCTURE_LLM_TEMPERATURE,
    max_tokens=IDEA_STRUCTURE_LLM_MAX_TOKENS,
)
_slidegen_llm = GeminiLLMProvider(
    api_keys=[GEMINI_API_KEY] if GEMINI_API_KEY else [],
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    temperature=LLM_TEMPERATURE,
    max_tokens=LLM_MAX_TOKENS,
    top_p=LLM_TOP_P
)

_retriever_infra = GeminiToolRetrieveProvider(
    tools_dict=TOOLS_DICT,
    index_path="backend/infrastructure/faiss_tool_retriever_index",
    api_key = GEMINI_API_KEY
)

# ===== SINGLETON SERVICES =====
_structure_service = StructureService()
_slide_service = SlideService(static_dir=STATIC_DIR)

_idea_workflow_service = IdeaWorkflowService(
    project_dir=str(PROJECT_DIR),
    llm_provider=_idea_llm
)

_manual_workflow_service = ManualWorkflowService(
    project_dir=str(PROJECT_DIR)
)

_doc_workflow_service = DocWorkflowService(
    project_dir=str(PROJECT_DIR),
    llm_provider=_slidegen_llm,
)

_slidegen_workflow_service = SlideGenWorkflowService(
    project_dir=str(PROJECT_DIR),
    llm_provider=_slidegen_llm,
    planner_llm_provider=_idea_llm,
    capture_provider=_capture_infra,
    parser_provider=_parser_infra,
    tool_retriever=_retriever_infra,
    doc_workflow_service=_doc_workflow_service
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


def get_idea_workflow_service() -> IdeaWorkflowService:
    return _idea_workflow_service


def get_manual_workflow_service() -> ManualWorkflowService:
    return _manual_workflow_service


def get_doc_workflow_service() -> DocWorkflowService:
    return _doc_workflow_service


def get_idea_service(
    workflow_service: IdeaWorkflowService = Depends(get_idea_workflow_service)
) -> IdeaService:
    return IdeaService(workflow_service)


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
        created_at=user.created_at, is_active=bool(user.is_active)
    )


def get_subscription_service() -> SubscriptionService:
    return SubscriptionService(SqliteUserRepository())


def get_collaboration_service(
    project_repo: ProjectRepository = Depends(get_project_repo),
) -> CollaborationService:
    return CollaborationService(project_repo)
