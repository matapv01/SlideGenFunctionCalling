# File: backend/schemas/auth_schema.py

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import Literal, Optional
from datetime import datetime

# --- TOKEN SCHEMAS ---

class Token(BaseModel):
    """Schema trả về khi login thành công"""
    access_token: str
    token_type: str = "bearer"


class EmailVerificationChallenge(BaseModel):
    """Short-lived challenge returned before an access token is issued."""

    challenge_id: str
    email: EmailStr
    expires_in: int
    message: str = "A verification code was sent to your email."


class EmailVerificationRequest(BaseModel):
    challenge_id: str = Field(..., min_length=20, max_length=200)
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class EmailVerificationResendRequest(BaseModel):
    challenge_id: str = Field(..., min_length=20, max_length=200)


class TokenData(BaseModel):
    """Schema dùng để decode token (lấy email từ payload)"""
    email: Optional[str] = None


# --- USER SCHEMAS ---

class UserBase(BaseModel):
    """Các trường chung cho User"""
    email: EmailStr


class UserLogin(BaseModel):
    """Schema cho API Login"""
    email: EmailStr
    password: str


class UserCreate(UserBase):
    """Schema cho API Register (cần password)"""
    full_name: str = Field(..., min_length=3, max_length=50, description="Họ và tên của người dùng")
    password: str = Field(..., min_length=6, description="Mật khẩu tối thiểu 6 ký tự")
    password_confirmation: str = Field(..., min_length=6, description="Xác nhận mật khẩu")

    @model_validator(mode="after")
    def passwords_must_match(self):
        if self.password != self.password_confirmation:
            raise ValueError("Mật khẩu xác nhận không khớp")
        return self


class UserResponse(UserBase):
    """
    Schema trả về cho Client.
    QUAN TRỌNG: Không bao giờ trả về hashed_password ở đây.
    """
    id: int
    is_active: bool
    is_admin: bool = False
    created_at: datetime
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    onboarding_completed: bool = True
    workspace_tour_version: int = 1

    model_config = ConfigDict(from_attributes=True)


class OnboardingAnswers(BaseModel):
    use_cases: list[Literal["work", "study", "pitch", "marketing", "reports", "personal"]] = Field(default_factory=list, max_length=6)
    role: Optional[Literal["student", "educator", "founder", "professional", "creative", "other"]] = None


class WorkspaceTourCompleteRequest(BaseModel):
    """Versioned completion marker for the first-workspace tour."""

    version: int = Field(default=1, ge=1, le=100)


class ChangePasswordRequest(BaseModel):
    """Schema cho API đổi mật khẩu (Thay thế cho dict thuần)"""
    current_password: str
    new_password: str = Field(..., min_length=6)
