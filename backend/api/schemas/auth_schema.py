# File: backend/schemas/auth_schema.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# --- TOKEN SCHEMAS ---

class Token(BaseModel):
    """Schema trả về khi login thành công"""
    access_token: str
    token_type: str = "bearer"


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


class UserResponse(UserBase):
    """
    Schema trả về cho Client.
    QUAN TRỌNG: Không bao giờ trả về hashed_password ở đây.
    """
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Cho phép map từ ORM object hoặc Dictionary


class ChangePasswordRequest(BaseModel):
    """Schema cho API đổi mật khẩu (Thay thế cho dict thuần)"""
    current_password: str
    new_password: str = Field(..., min_length=6)
