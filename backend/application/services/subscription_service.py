# File: backend/application/services/subscription_service.py

from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException
from backend.domain.entities.user import User
from backend.domain.ports.user_repository import UserRepository


class SubscriptionService:
    """Service for managing user subscriptions and usage limits"""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_subscription_info(self, user: User) -> Dict:
        """Get detailed subscription information for user"""
        limits = user.get_daily_limits()

        return {
            "tier": user.subscription_tier,
            "is_active": user.is_subscription_active(),
            "expires_at": user.subscription_expires_at,
            "daily_limits": limits,
            "current_usage": {
                "idea_generation": user.idea_usage_today,
                "docx_upload": user.docx_usage_today
            },
            "usage_reset_date": user.daily_usage_reset_date
        }

    def check_feature_access(self, user: User, feature_type: str, **kwargs) -> bool:
        """Check if user can access a specific feature"""
        # Reset usage if new day
        if user.reset_daily_usage_if_needed():
            self.user_repo.update_usage_count(user.id, "reset", 0)

        # Check basic subscription status
        if not user.is_subscription_active() and user.subscription_tier != "free":
            raise HTTPException(
                status_code=402,
                detail="Gói đăng ký đã hết hạn. Vui lòng nâng cấp để tiếp tục sử dụng tính năng cao cấp."
            )

        # Check feature-specific limits
        if feature_type == "idea_generation":
            if user.subscription_tier == "free" and user.idea_usage_today >= 2:
                raise HTTPException(
                    status_code=429,
                    detail="Gói Free đã đạt giới hạn (2 ý tưởng/ngày). Nâng cấp lên Plus để có 10 ý tưởng/ngày hoặc Ultra để không giới hạn."
                )
            elif user.subscription_tier == "plus" and user.idea_usage_today >= 10:
                raise HTTPException(
                    status_code=429,
                    detail="Gói Plus đã đạt giới hạn (10 ý tưởng/ngày). Nâng cấp lên Ultra để không giới hạn."
                )

        elif feature_type == "docx_upload":
            slide_count = kwargs.get("slide_count", 0)

            # Check daily upload limit
            if user.subscription_tier == "free" and user.docx_usage_today >= 3:
                raise HTTPException(
                    status_code=429,
                    detail="Gói Free đã đạt giới hạn (3 lần upload/ngày). Nâng cấp lên Plus để có 10 lần upload/ngày."
                )
            elif user.subscription_tier == "plus" and user.docx_usage_today >= 10:
                raise HTTPException(
                    status_code=429,
                    detail="Gói Plus đã đạt giới hạn (10 lần upload/ngày). Nâng cấp lên Ultra để không giới hạn."
                )

            # Check slide count limit
            if user.subscription_tier in ["free", "plus"] and slide_count > 20:
                raise HTTPException(
                    status_code=429,
                    detail=f"Tài liệu quá lớn ({slide_count} slides). Gói Free và Plus giới hạn 20 slides. Nâng cấp lên Ultra để không giới hạn."
                )

        elif feature_type == "content_length":
            content_length = kwargs.get("content_length", "standard")
            if user.subscription_tier == "free" and content_length != "brief":
                raise HTTPException(
                    status_code=402,
                    detail="Gói Free chỉ được dùng nội dung ngắn gọn. Nâng cấp lên Plus hoặc Ultra để dùng nội dung dài hơn."
                )

        return True

    def increment_usage(self, user_id: int, feature_type: str) -> None:
        """Increment feature usage counter"""
        self.user_repo.update_usage_count(user_id, feature_type, 1)

    def cancel_subscription(self, user_id: int, immediate: bool) -> dict:
        """Cancel subscription immediately or at period end"""
        user = self.user_repo.get_by_id(user_id)
        if not user or user.subscription_tier == "free":
            raise HTTPException(status_code=400, detail="No active subscription to cancel")
        if immediate:
            self.user_repo.cancel_subscription(user_id, immediate=True)
            return {"success": True, "immediate": True}
        else:
            # Non-immediate: just return the natural expiry date
            return {"success": True, "immediate": False, "expires_at": user.subscription_expires_at}

    def redeem_subscription_code(self, user_id: int, code: str) -> Dict:
        """Redeem subscription upgrade code"""
        code = code.strip().upper()

        if not code:
            raise HTTPException(status_code=400, detail="Vui lòng nhập mã code")

        success = self.user_repo.redeem_code(user_id, code)

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Mã code không hợp lệ hoặc đã được sử dụng. Vui lòng kiểm tra lại mã code."
            )

        # Get updated user to return new subscription status
        user = self.user_repo.get_by_id(user_id)
        return {
            "success": True,
            "message": f"Successfully upgraded to {user.subscription_tier.title()} tier!",
            "new_tier": user.subscription_tier,
            "expires_at": user.subscription_expires_at
        }

    def get_pricing_info(self) -> Dict:
        """Get subscription tier pricing information"""
        return {
            "tiers": [
                {
                    "name": "free",
                    "display_name": "Free",
                    "price": 0,
                    "currency": "USD",
                    "period": "forever",
                    "features": {
                        "idea_generation": "2 per day",
                        "docx_upload": "3 per day",
                        "max_slides": "20 slides max",
                        "content_length": "Brief only",
                        "priority_support": False
                    }
                },
                {
                    "name": "plus",
                    "display_name": "Plus",
                    "price": 20,
                    "currency": "USD",
                    "period": "month",
                    "features": {
                        "idea_generation": "10 per day",
                        "docx_upload": "10 per day",
                        "max_slides": "20 slides max",
                        "content_length": "All lengths",
                        "priority_support": True
                    }
                },
                {
                    "name": "ultra",
                    "display_name": "Ultra",
                    "price": 200,
                    "currency": "USD",
                    "period": "month",
                    "features": {
                        "idea_generation": "Unlimited",
                        "docx_upload": "Unlimited",
                        "max_slides": "Unlimited",
                        "content_length": "All lengths",
                        "priority_support": True,
                        "advanced_features": True
                    }
                }
            ]
        }