# File: backend/application/services/user_service.py

from typing import Dict
from backend.domain.ports.user_repository import UserRepository
from backend.api.schemas.profile_schema import UserProfileUpdate, UserSettingsUpdate
from backend.domain.entities.user import UserProfile, UserSettings


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo


    def get_profile(self, user_id: int) -> UserProfile:
        profile = self.user_repo.get_profile(user_id)
        if not profile:
            return UserProfile(
                user_id=user_id,
                full_name=None,
                avatar_url=None,
                bio=None
            )
        return profile


    def update_profile(self, user_id: int, data: UserProfileUpdate) -> None:
        update_dict = data.model_dump(exclude_unset=True)
        user_profile = UserProfile(
            user_id=user_id,
            full_name=update_dict.get("full_name"),
            avatar_url=update_dict.get("avatar_url"),
            bio=update_dict.get("bio")
        )

        self.user_repo.create_or_update_profile(user_profile)


    def get_settings(self, user_id: int) -> UserSettings:
        settings = self.user_repo.get_settings(user_id)
        if not settings:
            # Logic nghiệp vụ: Tự động tạo default nếu chưa có
            self.user_repo.create_default_settings(user_id)
            settings = self.user_repo.get_settings(user_id)
        return settings


    def update_settings(self, user_id: int, data: UserSettingsUpdate) -> None:
        update_dict = data.model_dump(exclude_unset=True)
        user_settings = UserSettings(
            user_id=user_id,
            theme=update_dict.get("theme"),
            language=update_dict.get("language"),
            default_transition_enabled=update_dict.get("notifications_enabled"), # Giả sử bạn map notifications_enabled thành default_transition_enabled
            default_thank_you_enabled=None, # Không cập nhật nếu không có trong request
            default_content_length=None, # Không cập nhật nếu không có trong request
            settings_json={k: v for k, v in update_dict.items() if k not in ["theme", "language", "notifications_enabled"]}
        )
        self.user_repo.update_settings(settings=user_settings)