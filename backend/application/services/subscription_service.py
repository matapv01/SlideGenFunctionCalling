# File: backend/application/services/subscription_service.py

from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import HTTPException
from backend.config import DOCX_MAX_SLIDES
from backend.domain.entities.user import User
from backend.domain.ports.user_repository import UserRepository


class SlideCountLimitError(ValueError):
    """Raised before generation when a deck exceeds the user's plan limit."""

    def __init__(self, requested: int, maximum: int, tier: str) -> None:
        self.requested = requested
        self.maximum = maximum
        self.tier = tier
        super().__init__(
            f"Gói {tier.title()} chỉ hỗ trợ tối đa {maximum} slide; "
            f"yêu cầu hiện tại là {requested} slide."
        )


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
            "usage_reset_date": user.daily_usage_reset_date,
            "cancel_at_period_end": user.cancel_at_period_end
        }

    @staticmethod
    def get_max_slide_count(user: User) -> int:
        """Return the canonical per-plan slide limit (-1 means unlimited)."""
        return int(user.get_daily_limits().get("max_docx_slides", 0))

    def validate_slide_count(self, user: User, slide_count: int) -> int:
        """Validate a requested deck size before any LLM/workflow work starts."""
        if not user.is_subscription_active() and user.subscription_tier != "free":
            raise HTTPException(
                status_code=402,
                detail="Gói đăng ký đã hết hạn. Vui lòng nâng cấp để tiếp tục sử dụng tính năng này.",
            )

        requested = int(slide_count)
        if requested < 1:
            raise ValueError("Số lượng slide phải lớn hơn 0.")

        maximum = self.get_max_slide_count(user)
        if maximum != -1 and requested > maximum:
            raise SlideCountLimitError(requested, maximum, user.subscription_tier)
        return requested

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
            max_slides = user.get_daily_limits()["max_docx_slides"]
            if max_slides != -1 and slide_count > max_slides:
                raise HTTPException(
                    status_code=413,
                    detail=(
                        f"Tài liệu quá dài ({slide_count} slides). "
                        f"Gói hiện tại chỉ hỗ trợ tối đa {max_slides} slides. "
                        "Vui lòng rút ngắn tài liệu hoặc nâng cấp lên Ultra để không giới hạn."
                    ),
                )

        elif feature_type == "slide_generation":
            self.validate_slide_count(user, kwargs.get("slide_count", 0))

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
        self.user_repo.cancel_subscription(user_id, immediate=immediate)
        if immediate:
            return {"success": True, "immediate": True}
        else:
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
                        "max_slides": f"{DOCX_MAX_SLIDES} slides max",
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
                        "max_slides": f"{DOCX_MAX_SLIDES} slides max",
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
