# File: backend/domain/entities/user.py

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any

USAGE_WINDOW_HOURS = 5

@dataclass
class User:
    id: Optional[int]
    email: str
    hashed_password: str
    subscription_tier: str = "free"
    subscription_expires_at: Optional[datetime] = None
    # Loaded from the administrator-managed subscription policy table. It is
    # optional so lightweight domain/unit-test users remain constructible.
    plan_limits: Optional[Dict[str, float | int]] = None
    daily_usage_reset_date: date = field(default_factory=date.today)
    idea_usage_today: int = 0
    docx_usage_today: int = 0
    usage_window_started_at: datetime = field(default_factory=datetime.now)
    # Chat usage is stored as weighted credits. One default Genius 3/Medium
    # turn costs 1.0 credit; model and effort choices may cost less or more.
    chat_usage: float = 0.0
    chat_message_count: int = 0
    docx_usage: int = 0
    is_active: bool = True
    # New accounts must verify once during registration. Existing accounts
    # are migrated as verified so a policy change does not lock them out.
    email_verified: bool = True
    # Authorization is persisted per account and managed through the admin
    # console. It is not derived from deployment environment variables.
    is_admin: bool = False
    cancel_at_period_end: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def is_subscription_active(self) -> bool:
        """Check if subscription is active"""
        if self.subscription_tier == "free":
            return True
        if self.subscription_tier == "ultra" and self.subscription_expires_at is None:
            return True  # Ultra with no expiry date = permanent
        if self.subscription_expires_at is None:
            return False
        return self.subscription_expires_at > datetime.now()

    def get_usage_limits(self) -> Dict[str, float | int]:
        """Return limits loaded from the runtime subscription policy."""
        return dict(self.plan_limits or {})

    def get_daily_limits(self) -> Dict[str, float | int]:
        """Backward-compatible name for callers that still ask for plan limits."""
        return self.get_usage_limits()

    def can_use_feature(self, feature_type: str) -> bool:
        """Check if user can use a feature in the current five-hour window."""
        if not self.is_subscription_active():
            return self.subscription_tier == "free"  # Only free features allowed

        limits = self.get_usage_limits()

        if feature_type in {"chat_message", "chat_messages", "idea_generation"}:
            limit = limits.get("chat_messages", 0)
            return limit == -1 or self.chat_usage < limit
        elif feature_type == "docx_upload":
            limit = limits.get("docx_upload", 0)
            return limit == -1 or self.docx_usage < limit

        return True

    def reset_daily_usage_if_needed(self) -> bool:
        """Backward-compatible alias that resets the rolling usage window."""
        now = datetime.now(tz=self.usage_window_started_at.tzinfo)
        if now >= self.usage_reset_at:
            self.usage_window_started_at = now
            self.daily_usage_reset_date = now.date()
            self.idea_usage_today = 0
            self.docx_usage_today = 0
            self.chat_usage = 0
            self.chat_message_count = 0
            self.docx_usage = 0
            return True
        return False

    @property
    def usage_reset_at(self) -> datetime:
        return self.usage_window_started_at + timedelta(hours=USAGE_WINDOW_HOURS)

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
    max_uses: int = 1       # -1 = no cap; only applies when code_type = "limited"
    current_uses: int = 0
    is_active: bool = True
    code_type: str = "limited"  # "unlimited" | "limited"
    created_at: datetime = field(default_factory=datetime.now)

    def can_redeem(self) -> bool:
        """Check if code can still be redeemed (ignores per-account policy)"""
        if not self.is_active:
            return False
        if self.code_type == "unlimited":
            return True
        # limited: respect max_uses cap (-1 = no cap)
        return self.max_uses == -1 or self.current_uses < self.max_uses

@dataclass
class CodeRedemption:
    id: Optional[int]
    user_id: int
    code: str
    tier_granted: str
    expires_at: Optional[datetime]
    redeemed_at: datetime = field(default_factory=datetime.now)
