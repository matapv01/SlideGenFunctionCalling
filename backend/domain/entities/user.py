# File: backend/domain/entities/user.py

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any

@dataclass
class User:
    id: Optional[int]
    email: str
    hashed_password: str
    subscription_tier: str = "free"
    subscription_expires_at: Optional[datetime] = None
    daily_usage_reset_date: date = field(default_factory=date.today)
    idea_usage_today: int = 0
    docx_usage_today: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def is_subscription_active(self) -> bool:
        """Check if subscription is active"""
        if self.subscription_tier == "free":
            return True
        if self.subscription_expires_at is None:
            return False
        return self.subscription_expires_at > datetime.now()

    def get_daily_limits(self) -> Dict[str, int]:
        """Get daily usage limits based on subscription tier"""
        if self.subscription_tier == "free":
            return {"idea_generation": 2, "docx_upload": 3, "max_docx_slides": 20}
        elif self.subscription_tier == "plus":
            return {"idea_generation": 10, "docx_upload": 10, "max_docx_slides": 20}
        elif self.subscription_tier == "ultra":
            return {"idea_generation": -1, "docx_upload": -1, "max_docx_slides": -1}  # -1 = unlimited
        return {"idea_generation": 0, "docx_upload": 0, "max_docx_slides": 0}

    def can_use_feature(self, feature_type: str) -> bool:
        """Check if user can use a specific feature today"""
        if not self.is_subscription_active():
            return self.subscription_tier == "free"  # Only free features allowed

        limits = self.get_daily_limits()

        if feature_type == "idea_generation":
            limit = limits["idea_generation"]
            return limit == -1 or self.idea_usage_today < limit
        elif feature_type == "docx_upload":
            limit = limits["docx_upload"]
            return limit == -1 or self.docx_usage_today < limit

        return True

    def reset_daily_usage_if_needed(self) -> bool:
        """Reset usage counters if it's a new day"""
        today = date.today()
        if self.daily_usage_reset_date < today:
            self.daily_usage_reset_date = today
            self.idea_usage_today = 0
            self.docx_usage_today = 0
            return True
        return False

@dataclass
class UserProfile:
    user_id: int
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class UserSettings:
    user_id: int
    theme: str = "light"
    language: str = "vi"
    default_transition_enabled: bool = True
    default_thank_you_enabled: bool = True
    default_content_length: str = "standard"
    settings_json: Dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class SubscriptionCode:
    id: Optional[int]
    code: str
    tier: str
    duration_days: int = 30
    max_uses: int = 1
    current_uses: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def can_redeem(self) -> bool:
        """Check if code can still be redeemed"""
        return self.is_active and self.current_uses < self.max_uses

@dataclass
class CodeRedemption:
    id: Optional[int]
    user_id: int
    code: str
    tier_granted: str
    expires_at: Optional[datetime]
    redeemed_at: datetime = field(default_factory=datetime.now)