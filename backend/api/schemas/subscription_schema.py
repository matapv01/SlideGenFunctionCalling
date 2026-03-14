# File: backend/api/schemas/subscription_schema.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SubscriptionInfoResponse(BaseModel):
    """User subscription information response"""
    tier: str
    is_active: bool
    expires_at: Optional[datetime]
    daily_limits: Dict[str, int]
    current_usage: Dict[str, int]
    usage_reset_date: str
    cancel_at_period_end: bool = False


class RedeemCodeRequest(BaseModel):
    """Request to redeem subscription code"""
    code: str = Field(..., min_length=1, max_length=50)


class RedeemCodeResponse(BaseModel):
    """Response after redeeming subscription code"""
    success: bool
    message: str
    new_tier: str
    expires_at: Optional[datetime]


class PricingInfoResponse(BaseModel):
    """Subscription pricing information"""
    tiers: list[Dict[str, Any]]


class UpgradePlanRequest(BaseModel):
    """Request to upgrade subscription plan"""
    tier: str = Field(..., pattern="^(plus|ultra)$")
    payment_token: Optional[str] = None  # For future payment integration