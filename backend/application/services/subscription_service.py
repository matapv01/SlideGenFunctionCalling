# File: backend/application/services/subscription_service.py

from datetime import datetime, timedelta, timezone
import math
from typing import Dict
from fastapi import HTTPException
from backend.config import (
    CHATBOT_EFFORT_CONFIGS,
    CHATBOT_MODEL_CONFIGS,
)
from backend.domain.entities.user import User, USAGE_WINDOW_HOURS
from backend.domain.ports.user_repository import UserRepository
from backend.domain.ports.usage_config_repository import UsageConfigRepository


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

    def __init__(
        self,
        user_repo: UserRepository,
        usage_config_repo: UsageConfigRepository | None = None,
    ):
        self.user_repo = user_repo
        self.usage_config_repo = usage_config_repo

    def _usage_weights(self, kind: str) -> dict[str, float]:
        source = CHATBOT_MODEL_CONFIGS if kind == "model" else CHATBOT_EFFORT_CONFIGS
        persisted = (
            self.usage_config_repo.get_weights(kind)
            if self.usage_config_repo is not None
            else {}
        )
        # The database is the runtime source of truth. A neutral 1.0 fallback
        # only keeps lightweight service/unit-test adapters functional before
        # they provide a usage-config repository.
        return {name: float(persisted.get(name, 1.0)) for name in source}

    def get_plan_limits(self) -> dict[str, dict[str, float | int]]:
        if self.usage_config_repo is None:
            return {}
        return self.usage_config_repo.get_plan_limits()

    def get_plan_limits_for_user(self, user: User) -> Dict[str, float | int]:
        if self.usage_config_repo is not None:
            limits = self.get_plan_limits().get(user.subscription_tier)
            if limits is None:
                return {
                    "chat_messages": 0,
                    "docx_upload": 0,
                    "max_docx_slides": 0,
                    "max_docx_file_mb": 0,
                    "max_docx_total_mb": 0,
                }
            return {
                "chat_messages": float(limits["chat_credits"]),
                "docx_upload": int(limits["docx_upload"]),
                "max_docx_slides": int(limits["max_docx_slides"]),
                "max_docx_file_mb": int(limits["max_docx_file_mb"]),
                "max_docx_total_mb": int(limits["max_docx_total_mb"]),
            }

        # Compatibility path for isolated tests/legacy adapters. All normal
        # application dependencies provide the SQLite policy repository.
        return user.get_usage_limits()

    def get_upload_limits_for_user(self, user_id: int) -> dict[str, int]:
        """Return the administrator-managed DOCX byte limits for one user."""
        user = self.get_user(user_id)
        limits = self.get_plan_limits_for_user(user)
        file_mb = int(limits.get("max_docx_file_mb", 0))
        total_mb = int(limits.get("max_docx_total_mb", 0))
        if file_mb <= 0 or total_mb <= 0 or file_mb > total_mb:
            raise RuntimeError("DOCX upload limits are not configured")
        return {
            "max_file_bytes": file_mb * 1024 * 1024,
            "max_total_bytes": total_mb * 1024 * 1024,
        }

    def get_chat_usage_cost(self, model: str | None, effort: str | None) -> float:
        """Return the persisted model × effort credit cost for one turn."""
        model_key = (model or "genius-3").strip().lower()
        effort_key = (effort or "medium").strip().lower()
        model_weight = self._usage_weights("model").get(model_key, 1.0)
        effort_weight = self._usage_weights("effort").get(effort_key, 1.0)
        return round(max(0.01, model_weight * effort_weight), 2)

    def get_admin_usage_config(self) -> Dict:
        """Return the editable usage policy for the administrator console."""
        return {
            "usage_window_hours": USAGE_WINDOW_HOURS,
            "model_weights": [
                {
                    "id": name,
                    "percentage": round(weight * 100, 2),
                    "multiplier": weight,
                }
                for name, weight in self._usage_weights("model").items()
            ],
            "effort_weights": [
                {
                    "id": name,
                    "percentage": round(weight * 100, 2),
                    "multiplier": weight,
                }
                for name, weight in self._usage_weights("effort").items()
            ],
            "plan_limits": self.get_plan_limits(),
        }

    def update_admin_usage_config(
        self,
        model_percentages: dict[str, float],
        effort_percentages: dict[str, float],
        plan_limits: dict[str, dict[str, float | int]] | None = None,
    ) -> Dict:
        """Validate and persist the complete administrator usage policy."""
        if self.usage_config_repo is None:
            raise RuntimeError("Usage configuration storage is not available")
        allowed = {
            "model": set(CHATBOT_MODEL_CONFIGS),
            "effort": set(CHATBOT_EFFORT_CONFIGS),
        }
        for kind, values in (("model", model_percentages), ("effort", effort_percentages)):
            unknown = set(values) - allowed[kind]
            if unknown:
                raise ValueError(f"Unsupported {kind} usage weight: {', '.join(sorted(unknown))}")
            for name, percentage in values.items():
                value = float(percentage)
                if not math.isfinite(value) or value < 10 or value > 500:
                    raise ValueError(f"{kind} usage percentage must be between 10 and 500")
                self.usage_config_repo.set_weight(kind, name, round(value / 100, 4))

        if plan_limits:
            allowed_tiers = {"free", "plus", "ultra"}
            unknown_tiers = set(plan_limits) - allowed_tiers
            if unknown_tiers:
                raise ValueError(
                    f"Unsupported plan tier: {', '.join(sorted(unknown_tiers))}"
                )
            missing_tiers = allowed_tiers - set(plan_limits)
            if missing_tiers:
                raise ValueError(
                    "Cần cấu hình đầy đủ các plan: "
                    + ", ".join(sorted(missing_tiers))
                )
            for tier, values in plan_limits.items():
                chat_credits = float(values["chat_credits"])
                docx_upload = int(values["docx_upload"])
                max_docx_slides = int(values["max_docx_slides"])
                max_docx_file_mb = int(values["max_docx_file_mb"])
                max_docx_total_mb = int(values["max_docx_total_mb"])
                if (
                    not math.isfinite(chat_credits)
                    or (chat_credits < 0 and chat_credits != -1)
                    or docx_upload < -1
                    or max_docx_slides < -1
                    or max_docx_file_mb < 1
                    or max_docx_total_mb < 1
                    or max_docx_file_mb > max_docx_total_mb
                ):
                    raise ValueError(
                        "DOCX file limits must be positive and the per-file limit "
                        "cannot exceed the per-conversation limit"
                    )
                self.usage_config_repo.set_plan_limits(
                    tier,
                    chat_credits=chat_credits,
                    docx_upload=docx_upload,
                    max_docx_slides=max_docx_slides,
                    max_docx_file_mb=max_docx_file_mb,
                    max_docx_total_mb=max_docx_total_mb,
                )
        return self.get_admin_usage_config()

    def reset_all_usage(self) -> int:
        if self.usage_config_repo is None:
            raise RuntimeError("Usage configuration storage is not available")
        return self.usage_config_repo.reset_all_usage()

    @staticmethod
    def _parse_admin_datetime(value) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.now(timezone.utc)

    def get_admin_users(self) -> list[dict]:
        """Return user usage snapshots without exposing password material."""
        list_users = getattr(self.user_repo, "list_admin_users", None)
        if not callable(list_users):
            raise RuntimeError("User administration storage is not available")

        result = []
        for row in list_users():
            window_started_at = self._as_utc(
                self._parse_admin_datetime(row.get("usage_window_started_at"))
            )
            full_name = row.get("full_name") or ""
            email = str(row.get("email") or "")
            result.append(
                {
                    "id": int(row["id"]),
                    "email": email,
                    "full_name": full_name or None,
                    "username": full_name or email.split("@", 1)[0],
                    "subscription_tier": row.get("subscription_tier") or "free",
                    "is_active": bool(row.get("is_active")),
                    "is_admin": bool(row.get("is_admin")),
                    "created_at": self._as_utc(self._parse_admin_datetime(row.get("created_at"))),
                    "chat_usage": round(float(row.get("chat_usage") or 0), 2),
                    "chat_message_count": int(row.get("chat_message_count") or 0),
                    "docx_usage": int(row.get("docx_usage") or 0),
                    "usage_window_started_at": window_started_at,
                    "usage_reset_at": window_started_at + timedelta(hours=USAGE_WINDOW_HOURS),
                }
            )
        return result

    def update_admin_role(
        self,
        *,
        actor_user_id: int,
        target_user_id: int,
        is_admin: bool,
    ) -> dict:
        """Grant or revoke admin access while preventing lockout."""
        target = self.user_repo.get_by_id(target_user_id)
        if target is None:
            raise LookupError("User not found")

        if target_user_id == actor_user_id and not is_admin:
            raise ValueError("Bạn không thể tự gỡ quyền admin của chính mình")

        if target.is_admin and not is_admin:
            count_admins = getattr(self.user_repo, "count_admin_users", None)
            if not callable(count_admins):
                raise RuntimeError("Admin role storage is not available")
            if count_admins() <= 1:
                raise ValueError("Không thể gỡ admin cuối cùng của hệ thống")

        set_admin = getattr(self.user_repo, "set_admin_status", None)
        if not callable(set_admin):
            raise RuntimeError("Admin role storage is not available")
        if not set_admin(target_user_id, bool(is_admin)):
            raise LookupError("User not found")
        return self.get_admin_user(target_user_id)

    def get_admin_user(self, user_id: int) -> dict:
        for user in self.get_admin_users():
            if user["id"] == user_id:
                return user
        raise LookupError("User not found")

    def reset_user_usage(self, user_id: int) -> dict:
        """Start a new five-hour window for exactly one user."""
        if self.user_repo.get_by_id(user_id) is None:
            raise LookupError("User not found")
        force_reset = getattr(self.user_repo, "force_reset_usage_window", None)
        if not callable(force_reset):
            raise RuntimeError("User usage reset is not available")
        if not force_reset(user_id):
            raise LookupError("User not found")
        return self.get_admin_user(user_id)

    def delete_user(self, *, actor_user_id: int, target_user_id: int) -> dict:
        """Delete a user while protecting the acting admin and admin lockout."""
        target = self.user_repo.get_by_id(target_user_id)
        if target is None:
            raise LookupError("User not found")
        if target_user_id == actor_user_id:
            raise ValueError("Bạn không thể tự xóa tài khoản admin của chính mình")
        if target.is_admin:
            count_admins = getattr(self.user_repo, "count_admin_users", None)
            if not callable(count_admins):
                raise RuntimeError("Admin role storage is not available")
            if count_admins() <= 1:
                raise ValueError("Không thể xóa admin cuối cùng của hệ thống")
        delete_user = getattr(self.user_repo, "delete_user", None)
        if not callable(delete_user):
            raise RuntimeError("User deletion storage is not available")
        return delete_user(target_user_id)

    def get_subscription_info(self, user: User) -> Dict:
        """Get detailed subscription information for user"""
        self._refresh_usage_window(user)
        limits = self.get_plan_limits_for_user(user)
        legacy_limits = {**limits, "idea_generation": limits["chat_messages"]}
        window_started_at = self._as_utc(user.usage_window_started_at)
        reset_at = self._as_utc(user.usage_reset_at)

        return {
            "tier": user.subscription_tier,
            "is_active": user.is_subscription_active(),
            "expires_at": user.subscription_expires_at,
            "usage_limits": limits,
            # Keep the old key while clients roll forward from the daily model.
            "daily_limits": legacy_limits,
            "current_usage": {
                "chat_messages": round(user.chat_usage, 2),
                "chat_message_count": user.chat_message_count,
                "docx_upload": user.docx_usage,
                "idea_generation": round(user.chat_usage, 2),
            },
            "usage_window_hours": USAGE_WINDOW_HOURS,
            "usage_window_started_at": window_started_at,
            "usage_reset_at": reset_at,
            "usage_reset_date": str(reset_at),
            "cancel_at_period_end": user.cancel_at_period_end
        }

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        """Make rolling-window timestamps unambiguous for browser clients."""
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)

    def _refresh_usage_window(self, user: User) -> None:
        """Reset persisted counters lazily when the five-hour window expires."""
        if user.reset_daily_usage_if_needed() and user.id is not None:
            reset_window = getattr(self.user_repo, "reset_usage_window", None)
            if callable(reset_window):
                reset_window(user.id)

    def get_user(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if user is None:
            raise LookupError("User not found")
        self._refresh_usage_window(user)
        return user

    def check_feature_access_for_user(self, user_id: int, feature_type: str, **kwargs) -> bool:
        """Check a feature using a fresh user snapshot at an API boundary."""
        return self.check_feature_access(self.get_user(user_id), feature_type, **kwargs)

    def consume_feature(self, user_id: int, feature_type: str, **kwargs) -> None:
        """Check and record one successful usage event for a feature."""
        user = self.get_user(user_id)
        self.check_feature_access(user, feature_type, **kwargs)
        self.increment_usage(
            user_id,
            feature_type,
            usage_cost=float(kwargs.get("usage_cost", 1.0)),
        )

    def get_max_slide_count(self, user: User) -> int:
        """Return the canonical per-plan slide limit (-1 means unlimited)."""
        return int(self.get_plan_limits_for_user(user).get("max_docx_slides", 0))

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
        """Check if user can access a feature in the current five-hour window."""
        self._refresh_usage_window(user)

        # Check basic subscription status
        if not user.is_subscription_active() and user.subscription_tier != "free":
            raise HTTPException(
                status_code=402,
                detail="Gói đăng ký đã hết hạn. Vui lòng nâng cấp để tiếp tục sử dụng tính năng cao cấp."
            )

        # Check feature-specific limits
        limits = self.get_plan_limits_for_user(user)
        if feature_type in {"chat_message", "chat_messages", "idea_generation"}:
            chat_limit = limits["chat_messages"]
            try:
                usage_cost = max(0.01, float(kwargs.get("usage_cost", 1.0)))
            except (TypeError, ValueError):
                usage_cost = 1.0
            if chat_limit != -1 and user.chat_usage + usage_cost > chat_limit + 1e-9:
                raise HTTPException(
                    status_code=429,
                    detail=(
                        f"Gói {user.subscription_tier.title()} đã đạt giới hạn chat "
                        f"({chat_limit} credits trong {USAGE_WINDOW_HOURS} giờ; "
                        f"lượt này cần {usage_cost:g} credit). "
                        "Vui lòng chờ reset hoặc nâng cấp gói."
                    ),
                )

        elif feature_type == "docx_upload":
            slide_count = kwargs.get("slide_count", 0)
            docx_limit = limits["docx_upload"]

            if docx_limit != -1 and user.docx_usage >= docx_limit:
                raise HTTPException(
                    status_code=429,
                    detail=(
                        f"Gói {user.subscription_tier.title()} đã đạt giới hạn tài liệu "
                        f"({docx_limit} file trong {USAGE_WINDOW_HOURS} giờ). "
                        "Vui lòng chờ reset hoặc nâng cấp gói."
                    ),
                )

            # Check slide count limit
            max_slides = limits["max_docx_slides"]
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

    def increment_usage(self, user_id: int, feature_type: str, *, usage_cost: float = 1.0) -> None:
        """Increment feature usage counter"""
        self.user_repo.update_usage_count(user_id, feature_type, 1, usage_cost)

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
        plan_limits = self.get_plan_limits()

        def limit_text(tier: str, key: str, suffix: str) -> str:
            value = plan_limits.get(tier, {}).get(key, 0)
            if value == -1:
                return f"Unlimited {suffix}"
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            return f"{value} {suffix}"

        return {
            "tiers": [
                {
                    "name": "free",
                    "display_name": "Free",
                    "price": 0,
                    "currency": "USD",
                    "period": "forever",
                    "features": {
                        "chat_messages": f"{limit_text('free', 'chat_credits', 'weighted chat credits')} / 5 hours",
                        "docx_upload": f"{limit_text('free', 'docx_upload', 'DOCX files')} / 5 hours",
                        "max_slides": limit_text("free", "max_docx_slides", "slides max"),
                        "usage_reset": "Resets every 5 hours",
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
                        "chat_messages": f"{limit_text('plus', 'chat_credits', 'weighted chat credits')} / 5 hours",
                        "docx_upload": f"{limit_text('plus', 'docx_upload', 'DOCX files')} / 5 hours",
                        "max_slides": limit_text("plus", "max_docx_slides", "slides max"),
                        "usage_reset": "Resets every 5 hours",
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
                        "chat_messages": f"{limit_text('ultra', 'chat_credits', 'weighted chat credits')} / 5 hours",
                        "docx_upload": f"{limit_text('ultra', 'docx_upload', 'DOCX files')} / 5 hours",
                        "max_slides": limit_text("ultra", "max_docx_slides", "slides max"),
                        "usage_reset": "Usage window resets every 5 hours",
                        "content_length": "All lengths",
                        "priority_support": True,
                        "advanced_features": True
                    }
                }
            ]
        }
