# File: backend/api/v1/authentication_router.py

import secrets
import time
from urllib.parse import urlencode, quote

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from backend.api.schemas.auth_schema import (
    UserCreate, 
    UserLogin, 
    Token, 
    UserResponse, 
    ChangePasswordRequest  # Import thêm cái này
)
from backend.api.dependencies import get_auth_service, get_current_active_user
from backend.application.services.auth_service import AuthService
from backend.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_FRONTEND_URL, GOOGLE_REDIRECT_URI
from backend.domain.entities.user import UserProfile
from backend.infrastructure.database.repositories.sqlite_user_repo import SqliteUserRepository

router = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])

_google_oauth_states: dict[str, float] = {}
_GOOGLE_STATE_TTL_SECONDS = 600


def _frontend_origin(request: Request) -> str:
    if GOOGLE_FRONTEND_URL:
        return GOOGLE_FRONTEND_URL
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip()
    host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc)).split(",")[0].strip()
    return f"{scheme}://{host}"


def _google_callback_url(request: Request) -> str:
    if GOOGLE_REDIRECT_URI:
        return GOOGLE_REDIRECT_URI
    return f"{_frontend_origin(request)}{request.url.path}"


def _google_result_redirect(request: Request, *, token: str | None = None, error: str | None = None) -> RedirectResponse:
    if token:
        fragment = f"google_token={quote(token)}"
    else:
        fragment = f"google_error={quote(error or 'oauth_failed')}"
    return RedirectResponse(url=f"{_frontend_origin(request)}/login#{fragment}", status_code=303)


@router.get("/google/login", name="google_login")
async def google_login(request: Request):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return _google_result_redirect(request, error="not_configured")

    now = time.time()
    _google_oauth_states.update({key: value for key, value in _google_oauth_states.items() if value > now})
    state = secrets.token_urlsafe(32)
    _google_oauth_states[state] = now + _GOOGLE_STATE_TTL_SECONDS
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": _google_callback_url(request),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
        "state": state,
    }
    return RedirectResponse(
        url="https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params),
        status_code=303,
    )


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        return _google_result_redirect(request, error="cancelled")
    if not code or not state or _google_oauth_states.pop(state, 0) < time.time():
        return _google_result_redirect(request, error="invalid_state")
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return _google_result_redirect(request, error="not_configured")

    try:
        async with httpx.AsyncClient(timeout=12) as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": _google_callback_url(request),
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            google_tokens = token_response.json()
            userinfo_response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {google_tokens['access_token']}"},
            )
            userinfo_response.raise_for_status()
            userinfo = userinfo_response.json()
    except (httpx.HTTPError, KeyError, ValueError):
        return _google_result_redirect(request, error="provider_failed")

    email = str(userinfo.get("email", "")).strip().lower()
    if not email or not userinfo.get("email_verified", False):
        return _google_result_redirect(request, error="email_not_verified")

    user_repo = SqliteUserRepository()
    auth_service = AuthService(user_repo)
    user = user_repo.get_by_email(email)
    full_name = str(userinfo.get("name", "")).strip() or email.split("@", 1)[0]
    avatar_url = str(userinfo.get("picture", "")).strip() or None

    try:
        if user is None:
            user = auth_service.register_user(email, full_name, secrets.token_urlsafe(48))
        elif not user.is_active:
            return _google_result_redirect(request, error="account_inactive")
        if user.id is not None:
            user_repo.create_or_update_profile(UserProfile(user_id=user.id, full_name=full_name, avatar_url=avatar_url))
        access_token = auth_service.create_access_token(data={"sub": user.email})
    except Exception:
        return _google_result_redirect(request, error="account_failed")

    return _google_result_redirect(request, token=access_token)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.register_user(user_data.email, user_data.full_name, user_data.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")
    
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_active_user)):
    return current_user


@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}


@router.put("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    current_password = password_data.current_password
    new_password = password_data.new_password

    user_obj = auth_service.user_repo.get_by_id(current_user.id)

    auth_service.change_password(
        user_id=current_user.id,
        current_password=current_password,
        new_password=new_password,
        user_hashed_password=user_obj.hashed_password
    )
    
    return {"message": "Password changed successfully"}
