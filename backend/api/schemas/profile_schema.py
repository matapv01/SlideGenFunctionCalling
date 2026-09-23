# File: backend/schemas/profile_schema.py 

from pydantic import BaseModel, ConfigDict
from typing import Optional

# --- PROFILE SCHEMAS ---

class UserProfileBase(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class UserProfileUpdate(UserProfileBase):
    """Schema cho request cập nhật profile"""
    pass

class UserProfileResponse(UserProfileBase):
    """Schema trả về thông tin profile"""
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- SETTINGS SCHEMAS ---

class UserSettingsUpdate(BaseModel):
    """
    Định nghĩa các cài đặt cụ thể để validate.
    Nếu bạn muốn linh động (schema-less), có thể dùng Dict[str, Any],
    nhưng tốt nhất là nên định nghĩa rõ.
    """
    theme: Optional[str] = "light"  # light, dark, system
    language: Optional[str] = "vi"
    notifications_enabled: bool = True
    
    # Cho phép thêm các trường khác linh động nếu cần
    model_config = ConfigDict(extra="allow")

class UserSettingsResponse(UserSettingsUpdate):
    user_id: int
    
    model_config = ConfigDict(extra="allow", from_attributes=True)
