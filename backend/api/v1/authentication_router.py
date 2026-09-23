# File: backend/api/v1/authentication_router.py

import asyncio
import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from threading import Lock
from urllib.parse import urlencode, quote

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from backend.api.schemas.auth_schema import (
    UserCreate, 
    UserLogin, 
    Token, 
    EmailVerificationChallenge,
    EmailVerificationRequest,
    EmailVerificationResendRequest,
    UserResponse,
    OnboardingAnswers,
    WorkspaceTourCompleteRequest,
    ChangePasswordRequest  # Import thêm cái này
)
from backend.api.dependencies import get_auth_service, get_current_active_user
from backend.application.services.auth_service import AuthService
from backend.config import (
    AUTH_OTP_EXPIRE_MINUTES,
    AUTH_OTP_MAX_ATTEMPTS,
    AUTH_OTP_RESEND_COOLDOWN_SECONDS,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_FRONTEND_URL,
    GOOGLE_REDIRECT_URI,
    SECRET_KEY,
)
from backend.domain.entities.user import UserProfile
from backend.application.services.email_verification_service import (
    EmailDeliveryError,
    send_verification_code,
)
from backend.infrastructure.database.repositories.sqlite_user_repo import SqliteUserRepository

router = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])

# This route is mounted below the API router at /api/v1. Keep the callback
# path explicit instead of deriving it from the incoming request path; the
# public frontend mount (/slidegen) is unrelated to the API mount.
_GOOGLE_CALLBACK_PATH = "/api/v1/auth/google/callback"

_google_oauth_states: dict[str, float] = {}
_GOOGLE_STATE_TTL_SECONDS = 600


@dataclass
class _PendingEmailVerification:
    email: str
    code_hash: str
    created_at: float
    expires_at: float
    last_sent_at: float
    attempts: int = 0


_pending_email_verifications: dict[str, _PendingEmailVerification] = {}
_verification_lock = Lock()


def _verification_code_hash(challenge_id: str, code: str) -> str:
    payload = f"{challenge_id}:{code}".encode("utf-8")
    return hmac.new(SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def _cleanup_verifications(now: float) -> None:
    expired = [
        challenge_id
        for challenge_id, challenge in _pending_email_verifications.items()
        if challenge.expires_at <= now
    ]
    for challenge_id in expired:
        _pending_email_verifications.pop(challenge_id, None)


async def _issue_email_verification(email: str) -> EmailVerificationChallenge:
    now = time.time()
    challenge_id = secrets.token_urlsafe(32)
    code = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = now + AUTH_OTP_EXPIRE_MINUTES * 60

    try:
        await asyncio.to_thread(send_verification_code, email, code)
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    with _verification_lock:
        _cleanup_verifications(now)
        _pending_email_verifications[challenge_id] = _PendingEmailVerification(
            email=email,
            code_hash=_verification_code_hash(challenge_id, code),
            created_at=now,
            expires_at=expires_at,
            last_sent_at=now,
        )

    return EmailVerificationChallenge(
        challenge_id=challenge_id,
        email=email,
        expires_in=AUTH_OTP_EXPIRE_MINUTES * 60,
    )


def _get_pending_verification(challenge_id: str) -> _PendingEmailVerification:
    now = time.time()
    with _verification_lock:
        _cleanup_verifications(now)
        challenge = _pending_email_verifications.get(challenge_id)
        if challenge is None:
            raise HTTPException(status_code=400, detail="Verification code expired or is invalid.")
        return challenge


def _consume_verification(challenge_id: str, code: str) -> str:
    now = time.time()
    with _verification_lock:
        _cleanup_verifications(now)
        challenge = _pending_email_verifications.get(challenge_id)
        if challenge is None:
            raise HTTPException(status_code=400, detail="Verification code expired or is invalid.")
        if challenge.attempts >= AUTH_OTP_MAX_ATTEMPTS:
            _pending_email_verifications.pop(challenge_id, None)
            raise HTTPException(status_code=429, detail="Too many verification attempts. Request a new code.")

        expected_hash = _verification_code_hash(challenge_id, code)
        if not hmac.compare_digest(challenge.code_hash, expected_hash):
            challenge.attempts += 1
            raise HTTPException(status_code=400, detail="The verification code is incorrect.")

        _pending_email_verifications.pop(challenge_id, None)
        return challenge.email


def _is_email_verification_exempt(user) -> bool:
    """Keep a role-based bypass for manually managed administrator accounts."""
    return bool(user and user.is_admin)


def _server_origin(request: Request) -> str:
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip().lower()
    host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc)).split(",")[0].strip()
    hostname = host.rsplit("@", 1)[-1].split(":", 1)[0].lower().rstrip(".")
    # Public OAuth callbacks must use HTTPS. Some upstream reverse proxies
    # forward the internal HTTP hop as X-Forwarded-Proto=http even though the
    # browser reached the public domain over HTTPS. Keep localhost usable for
    # Docker development, but normalize every non-local public host to HTTPS.
    if scheme == "http" and hostname not in {"localhost", "127.0.0.1", "::1"}:
        scheme = "https"
    return f"{scheme}://{host}"


def _frontend_base(request: Request) -> str:
    return GOOGLE_FRONTEND_URL or f"{_server_origin(request)}/slidegen"


def _google_callback_url(request: Request) -> str:
    if GOOGLE_REDIRECT_URI:
        return GOOGLE_REDIRECT_URI.rstrip("/")
    # The frontend lives at /slidegen, while OAuth callbacks stay under the
    # API mount. This remains correct behind nginx because _server_origin()
    # uses the forwarded public scheme and host.
    return f"{_server_origin(request)}{_GOOGLE_CALLBACK_PATH}"


def _google_result_redirect(
    request: Request,
    *,
    token: str | None = None,
    error: str | None = None,
    is_new_user: bool = False,
) -> RedirectResponse:
    if token:
        fragment = f"google_token={quote(token)}"
    else:
        fragment = f"google_error={quote(error or 'oauth_failed')}"
    auth_page = "register" if is_new_user else "login"
    return RedirectResponse(url=f"{_frontend_base(request)}/{auth_page}#{fragment}", status_code=303)


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
    # Google userinfo returns a boolean here. Require the actual boolean value
    # instead of accepting a truthy string supplied by an unexpected provider
    # response.
    if not email or userinfo.get("email_verified") is not True:
        return _google_result_redirect(request, error="email_not_verified")

    user_repo = SqliteUserRepository()
    auth_service = AuthService(user_repo)
    user = user_repo.get_by_email(email)
    is_new_user = user is None or not user.email_verified
    full_name = str(userinfo.get("name", "")).strip() or email.split("@", 1)[0]
    avatar_url = str(userinfo.get("picture", "")).strip() or None

    try:
        if user is None:
            # Google already verified the identity, so create the account and
            # issue a token directly. The random password is not shown to the
            # user; Google remains the sign-in provider for this account.
            user = auth_service.register_user(
                email,
                full_name,
                secrets.token_urlsafe(48),
                email_verified=True,
            )
            if user.id is not None:
                user_repo.create_or_update_profile(
                    UserProfile(user_id=user.id, full_name=full_name, avatar_url=avatar_url)
                )
        elif not user.is_active:
            return _google_result_redirect(request, error="account_inactive")
        elif user.id is not None and not user.email_verified:
            # A user who initially registered with password can also prove
            # ownership through Google's verified identity.
            user_repo.mark_email_verified(user.id)
            user = user_repo.get_by_email(email) or user
        if user.id is not None:
            user_repo.create_or_update_profile(UserProfile(user_id=user.id, full_name=full_name, avatar_url=avatar_url))
    except Exception:
        return _google_result_redirect(request, error="account_failed")

    # A successful Google OAuth flow has already verified the email identity.
    # It must never enter Slidegen's email OTP flow, including when the account
    # was originally created with password authentication.
    return _google_result_redirect(
        request,
        token=auth_service.create_access_token(data={"sub": user.email}),
        is_new_user=is_new_user,
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.register_user(user_data.email, user_data.full_name, user_data.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=EmailVerificationChallenge | Token)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Tài khoản hiện không hoạt động.")
    if user.email_verified or _is_email_verification_exempt(user):
        return Token(
            access_token=auth_service.create_access_token(data={"sub": user.email}),
        )
    return await _issue_email_verification(user.email)


@router.post("/verify-email-code", response_model=Token)
async def verify_email_code(
    verification_data: EmailVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    email = _consume_verification(verification_data.challenge_id, verification_data.code)
    user = auth_service.user_repo.get_by_email(email)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Tài khoản không còn hoạt động.")
    if user.id is not None:
        auth_service.user_repo.mark_email_verified(user.id)
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/resend-email-code", response_model=EmailVerificationChallenge)
async def resend_email_code(verification_data: EmailVerificationResendRequest):
    challenge = _get_pending_verification(verification_data.challenge_id)
    now = time.time()
    if now - challenge.last_sent_at < AUTH_OTP_RESEND_COOLDOWN_SECONDS:
        retry_after = max(1, int(AUTH_OTP_RESEND_COOLDOWN_SECONDS - (now - challenge.last_sent_at)))
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {retry_after} seconds before requesting another code.",
        )

    code = f"{secrets.randbelow(1_000_000):06d}"
    try:
        await asyncio.to_thread(send_verification_code, challenge.email, code)
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    now = time.time()
    with _verification_lock:
        challenge.code_hash = _verification_code_hash(verification_data.challenge_id, code)
        challenge.expires_at = now + AUTH_OTP_EXPIRE_MINUTES * 60
        challenge.last_sent_at = now
        challenge.attempts = 0

    return EmailVerificationChallenge(
        challenge_id=verification_data.challenge_id,
        email=challenge.email,
        expires_in=AUTH_OTP_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_active_user)):
    return current_user


@router.post("/onboarding", response_model=UserResponse)
async def complete_onboarding(
    answers: OnboardingAnswers,
    current_user: UserResponse = Depends(get_current_active_user),
):
    if current_user.onboarding_completed:
        return current_user
    SqliteUserRepository().complete_onboarding(current_user.id, answers.use_cases, answers.role)
    return current_user.model_copy(update={"onboarding_completed": True})


@router.post("/workspace-tour/complete", response_model=UserResponse)
async def complete_workspace_tour(
    request: WorkspaceTourCompleteRequest,
    current_user: UserResponse = Depends(get_current_active_user),
):
    """Persist that the account has seen or skipped the current workspace tour."""
    SqliteUserRepository().complete_workspace_tour(current_user.id, request.version)
    return current_user.model_copy(
        update={"workspace_tour_version": max(current_user.workspace_tour_version, request.version)}
    )


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
