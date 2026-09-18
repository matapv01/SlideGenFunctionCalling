from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UsageWeightOut(BaseModel):
    id: str
    percentage: float
    multiplier: float


class PlanLimit(BaseModel):
    chat_credits: float
    docx_upload: int
    max_docx_slides: int
    max_docx_file_mb: int = 10
    max_docx_total_mb: int = 50


class AdminUsageConfigResponse(BaseModel):
    usage_window_hours: int
    model_weights: list[UsageWeightOut]
    effort_weights: list[UsageWeightOut]
    plan_limits: dict[str, PlanLimit]


class AdminUsageConfigUpdate(BaseModel):
    model_percentages: dict[str, float] = Field(default_factory=dict)
    effort_percentages: dict[str, float] = Field(default_factory=dict)
    plan_limits: dict[str, PlanLimit] = Field(default_factory=dict)


class AdminUsageResetResponse(BaseModel):
    reset_users: int
    usage_window_hours: int


class AdminUser(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    username: str
    subscription_tier: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    chat_usage: float
    chat_message_count: int
    docx_usage: int
    usage_window_started_at: datetime
    usage_reset_at: datetime


class AdminRoleUpdate(BaseModel):
    is_admin: bool


class AdminPasswordResetRequest(BaseModel):
    password: str = Field(..., min_length=6, max_length=128)


class AdminUserActionResponse(BaseModel):
    user_id: int
    message: str
