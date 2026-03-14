# File: backend/api/v1/subscription_router.py

from fastapi import APIRouter, Depends, HTTPException
from backend.api.schemas.subscription_schema import (
    SubscriptionInfoResponse, RedeemCodeRequest, RedeemCodeResponse,
    PricingInfoResponse, UpgradePlanRequest
)
from backend.api.schemas.auth_schema import UserResponse
from backend.api.dependencies import get_current_active_user
from backend.application.services.subscription_service import SubscriptionService
from backend.infrastructure.database.repositories.sqlite_user_repo import SqliteUserRepository

router = APIRouter(prefix="/subscription", tags=["subscription"])

def get_subscription_service() -> SubscriptionService:
    user_repo = SqliteUserRepository()
    return SubscriptionService(user_repo)


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
        usage_reset_date=str(info["usage_reset_date"])
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


@router.post("/upgrade")
async def upgrade_subscription(
    request: UpgradePlanRequest,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Upgrade subscription plan (placeholder for payment integration)"""
    raise HTTPException(
        status_code=501,
        detail="Payment integration not yet available. Please use a subscription code to upgrade."
    )