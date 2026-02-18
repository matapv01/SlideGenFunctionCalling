# File: backend/infrastructure/database/repositories/sqlite_user_repo.py

from typing import Optional, List, Dict
import json
from backend.domain.entities.user import User, UserProfile, UserSettings
from backend.domain.ports.user_repository import UserRepository
from backend.infrastructure.database.connection import get_db_connection


class SqliteUserRepository(UserRepository):
    def _map_user(self, row) -> Optional[User]:
        if not row: return None
        return User(
            id=row['id'],
            email=row['email'],
            username=row['username'],
            hashed_password=row['hashed_password'],
            is_active=bool(row['is_active']),
            created_at=row['created_at'] # Giả sử DB trả về datetime hoặc string parse được
        )


    def _map_profile(self, row) -> Optional[UserProfile]:
        if not row: return None
        return UserProfile(
            user_id=row['user_id'],
            full_name=row['full_name'],
            avatar_url=row['avatar_url'],
            bio=row['bio'],
            updated_at=row['updated_at']
        )


    def _map_settings(self, row) -> Optional[UserSettings]:
        if not row: return None
        return UserSettings(
            user_id=row['user_id'],
            theme=row['theme'],
            language=row['language'],
            default_transition_enabled=bool(row['default_transition_enabled']),
            default_thank_you_enabled=bool(row['default_thank_you_enabled']),
            default_content_length=row['default_content_length'],
            settings_json=json.loads(row['settings_json']) if row['settings_json'] else {},
            updated_at=row['updated_at']
        )


    def get_by_email(self, email: str) -> Optional[User]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            return self._map_user(cursor.fetchone())


    def get_by_id(self, user_id: int) -> Optional[User]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return self._map_user(cursor.fetchone())


    def create(self, user: User) -> User:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, username, hashed_password, is_active) VALUES (?, ?, ?, ?)",
                (user.email, user.username, user.hashed_password, user.is_active)
            )
            conn.commit()
            user.id = cursor.lastrowid
            return user


    def update_password(self, user_id: int, new_hashed_password: str) -> None:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET hashed_password = ? WHERE id = ?',
                (new_hashed_password, user_id)
            )
            conn.commit()


    def get_all(self) -> List[dict]:
        """Get all users (for admin purposes)"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, username, created_at, is_active FROM users")
            return [dict(row) for row in cursor.fetchall()]


    def get_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
            return self._map_profile(cursor.fetchone())


    def create_or_update_profile(self, profile: UserProfile) -> None:
        """Create or update user profile"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_profiles (user_id, full_name, avatar_url, bio, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    full_name = COALESCE(?, full_name),
                    avatar_url = COALESCE(?, avatar_url),
                    bio = COALESCE(?, bio),
                    updated_at = CURRENT_TIMESTAMP
            """, (profile.user_id, profile.full_name, profile.avatar_url, profile.bio, profile.full_name, profile.avatar_url, profile.bio))
            conn.commit()


    def get_settings(self, user_id: int) -> Optional[UserSettings]:
        """Get user settings"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return self._map_settings(row)


    def create_default_settings(self, user_id: int):
        """Create default settings for new user"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_settings (user_id) VALUES (?)
            """, (user_id,))
            conn.commit()


    def update_settings(self, settings: UserSettings):
        """Update user settings"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            settings_json_str = json.dumps(settings.settings_json) if settings.settings_json else None
            cursor.execute("""
                INSERT INTO user_settings (user_id, theme, default_transition_enabled,
                                        default_thank_you_enabled, default_content_length,
                                        language, settings_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    theme = COALESCE(?, theme),
                    default_transition_enabled = COALESCE(?, default_transition_enabled),
                    default_thank_you_enabled = COALESCE(?, default_thank_you_enabled),
                    default_content_length = COALESCE(?, default_content_length),
                    language = COALESCE(?, language),
                    settings_json = COALESCE(?, settings_json),
                    updated_at = CURRENT_TIMESTAMP
            """, (settings.user_id, settings.theme, settings.default_transition_enabled, settings.default_thank_you_enabled,
                settings.default_content_length, settings.language, settings_json_str,
                settings.theme, settings.default_transition_enabled, settings.default_thank_you_enabled,
                settings.default_content_length, settings.language, settings_json_str))
            conn.commit()