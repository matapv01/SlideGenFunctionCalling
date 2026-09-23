from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_auth_service, get_current_admin_user, get_subscription_service
from backend.api.schemas.admin_schema import (
    AdminRoleUpdate,
    AdminPasswordResetRequest,
    AdminUser,
    AdminUserActionResponse,
    AdminUsageConfigResponse,
    AdminUsageConfigUpdate,
    AdminUsageResetResponse,
)
from backend.api.schemas.auth_schema import UserResponse
from backend.application.services.auth_service import AuthService
from backend.application.services.subscription_service import SubscriptionService
from backend.domain.entities.user import USAGE_WINDOW_HOURS


router = APIRouter(prefix="/admin", tags=["ADMIN"])


@router.get("/usage/config", response_model=AdminUsageConfigResponse)
async def get_admin_usage_config(
    _: UserResponse = Depends(get_current_admin_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> AdminUsageConfigResponse:
    return AdminUsageConfigResponse(**subscription_service.get_admin_usage_config())


@router.put("/usage/config", response_model=AdminUsageConfigResponse)
async def update_admin_usage_config(
    body: AdminUsageConfigUpdate,
    _: UserResponse = Depends(get_current_admin_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> AdminUsageConfigResponse:
    try:
        result = subscription_service.update_admin_usage_config(
            body.model_percentages,
            body.effort_percentages,
            {
                tier: values.model_dump()
                for tier, values in body.plan_limits.items()
            },
        )
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return AdminUsageConfigResponse(**result)


@router.post("/usage/reset", response_model=AdminUsageResetResponse)
async def reset_all_usage(
    _: UserResponse = Depends(get_current_admin_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> AdminUsageResetResponse:
    try:
        reset_users = subscription_service.reset_all_usage()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return AdminUsageResetResponse(
        reset_users=reset_users,
        usage_window_hours=USAGE_WINDOW_HOURS,
    )


@router.get("/users", response_model=list[AdminUser])
async def list_admin_users(
    _: UserResponse = Depends(get_current_admin_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> list[AdminUser]:
    try:
        return [AdminUser(**user) for user in subscription_service.get_admin_users()]
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.patch("/users/{user_id}/admin", response_model=AdminUser)
async def update_user_admin_role(
    user_id: int,
    body: AdminRoleUpdate,
    current_admin: UserResponse = Depends(get_current_admin_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> AdminUser:
    try:
        return AdminUser(
            **subscription_service.update_admin_role(
                actor_user_id=current_admin.id,
                target_user_id=user_id,
                is_admin=body.is_admin,
            )
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post("/users/{user_id}/password-reset", response_model=AdminUserActionResponse)
async def reset_user_password(
    user_id: int,
    body: AdminPasswordResetRequest,
    _: UserResponse = Depends(get_current_admin_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdminUserActionResponse:
    auth_service.reset_password(user_id, body.password)
    return AdminUserActionResponse(
        user_id=user_id,
        message="Mật khẩu người dùng đã được đặt lại",
    )


@router.post("/users/{user_id}/usage-reset", response_model=AdminUser)
async def reset_user_usage(
    user_id: int,
    _: UserResponse = Depends(get_current_admin_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> AdminUser:
    try:
        return AdminUser(**subscription_service.reset_user_usage(user_id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.delete("/users/{user_id}", response_model=AdminUserActionResponse)
async def delete_admin_user(
    user_id: int,
    current_admin: UserResponse = Depends(get_current_admin_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
) -> AdminUserActionResponse:
    try:
        deleted = subscription_service.delete_user(
            actor_user_id=current_admin.id,
            target_user_id=user_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return AdminUserActionResponse(
        user_id=int(deleted["id"]),
        message=f"Đã xóa tài khoản {deleted['email']}",
    )
