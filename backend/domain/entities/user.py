# File: backend/domain/entities/user.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class User:
    id: Optional[int]
    email: str
    username: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

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