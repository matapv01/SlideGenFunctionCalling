# File: backend/api/v1/subscription_router.py

from fastapi import APIRouter, Depends, HTTPException
from backend.api.schemas.subscription_schema import (
    SubscriptionInfoResponse, RedeemCodeRequest, RedeemCodeResponse,
    PricingInfoResponse
)
from backend.api.schemas.auth_schema import UserResponse
from backend.api.dependencies import get_current_active_user, get_subscription_service
from backend.application.services.subscription_service import SubscriptionService
from backend.infrastructure.database.repositories.sqlite_user_repo import SqliteUserRepository

router = APIRouter(prefix="/subscription", tags=["subscription"])


@router.get("/info", response_model=SubscriptionInfoResponse)
async def get_subscription_info(
    current_user: UserResponse = Depends(get_current_active_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get current user's subscription information"""
    # Get full user from repository with subscription data
    user_repo = SqliteUserRepository()
    user = user_repo.get_by_id(current_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    info = subscription_service.get_subscription_info(user)
    return SubscriptionInfoResponse(
        tier=info["tier"],
        is_active=info["is_active"],
        expires_at=info["expires_at"],
        daily_limits=info["daily_limits"],
        current_usage=info["current_usage"],
        usage_reset_date=str(info["usage_reset_date"]),
        cancel_at_period_end=info.get("cancel_at_period_end", False)
    )


@router.post("/redeem", response_model=RedeemCodeResponse)
async def redeem_subscription_code(
    request: RedeemCodeRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Redeem subscription upgrade code"""
    result = subscription_service.redeem_subscription_code(current_user.id, request.code)
    return RedeemCodeResponse(**result)


@router.get("/pricing", response_model=PricingInfoResponse)
async def get_pricing_info(
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Get subscription pricing information (public endpoint)"""
    pricing_info = subscription_service.get_pricing_info()
    return PricingInfoResponse(**pricing_info)


@router.post("/cancel")
async def cancel_subscription(
    immediate: bool = True,
    current_user: UserResponse = Depends(get_current_active_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    """Cancel subscription. immediate=True downgrades to free now; immediate=False lets it expire naturally."""
    user_repo = SqliteUserRepository()
    user = user_repo.get_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return subscription_service.cancel_subscription(user.id, immediate=immediate)