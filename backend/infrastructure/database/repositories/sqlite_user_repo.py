# File: backend/infrastructure/database/repositories/sqlite_user_repo.py

from typing import Optional, List, Dict
import json
from datetime import datetime, date, timedelta
from backend.domain.entities.user import User, UserProfile, UserSettings, SubscriptionCode, CodeRedemption
from backend.domain.ports.user_repository import UserRepository
from backend.infrastructure.database.connection import get_db_connection


class SqliteUserRepository(UserRepository):
    def _map_user(self, row) -> Optional[User]:
        if not row: return None

        # Parse dates properly - use try/except for safe column access
        expires_at = None
        try:
            if row['subscription_expires_at']:
                if isinstance(row['subscription_expires_at'], str):
                    expires_at = datetime.fromisoformat(row['subscription_expires_at'].replace('Z', ''))
                else:
                    expires_at = row['subscription_expires_at']
        except (KeyError, TypeError):
            expires_at = None

        reset_date = date.today()
        try:
            if row['daily_usage_reset_date']:
                if isinstance(row['daily_usage_reset_date'], str):
                    reset_date = date.fromisoformat(row['daily_usage_reset_date'])
                else:
                    reset_date = row['daily_usage_reset_date']
        except (KeyError, TypeError):
            reset_date = date.today()

        # Safe column access with defaults
        subscription_tier = 'free'
        try:
            subscription_tier = row['subscription_tier'] or 'free'
        except (KeyError, TypeError):
            subscription_tier = 'free'

        idea_usage_today = 0
        try:
            idea_usage_today = row['idea_usage_today'] or 0
        except (KeyError, TypeError):
            idea_usage_today = 0

        docx_usage_today = 0
        try:
            docx_usage_today = row['docx_usage_today'] or 0
        except (KeyError, TypeError):
            docx_usage_today = 0

        return User(
            id=row['id'],
            email=row['email'],
            hashed_password=row['hashed_password'],
            subscription_tier=subscription_tier,
            subscription_expires_at=expires_at,
            daily_usage_reset_date=reset_date,
            idea_usage_today=idea_usage_today,
            docx_usage_today=docx_usage_today,
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
            cursor.execute("""
                INSERT INTO users (
                    email, hashed_password, subscription_tier,
                    daily_usage_reset_date, idea_usage_today, docx_usage_today, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user.email, user.hashed_password, user.subscription_tier,
                user.daily_usage_reset_date, user.idea_usage_today, user.docx_usage_today, user.is_active
            ))
            conn.commit()
            user_id = cursor.lastrowid
            # Fetch back to get created_at from database
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return self._map_user(cursor.fetchone())


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
            cursor.execute("SELECT id, email, created_at, is_active FROM users")
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

    # === SUBSCRIPTION MANAGEMENT ===

    def update_usage_count(self, user_id: int, feature_type: str, increment: int = 1) -> None:
        """Update daily usage count for a specific feature"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Reset daily usage if needed
            cursor.execute("""
                UPDATE users SET
                    daily_usage_reset_date = CURRENT_DATE,
                    idea_usage_today = 0,
                    docx_usage_today = 0
                WHERE id = ? AND daily_usage_reset_date < CURRENT_DATE
            """, (user_id,))

            # Update specific usage counter
            if feature_type == "idea_generation":
                cursor.execute("""
                    UPDATE users SET idea_usage_today = idea_usage_today + ? WHERE id = ?
                """, (increment, user_id))
            elif feature_type == "docx_upload":
                cursor.execute("""
                    UPDATE users SET docx_usage_today = docx_usage_today + ? WHERE id = ?
                """, (increment, user_id))

            # Log usage for analytics
            cursor.execute("""
                INSERT INTO daily_usage_logs (user_id, feature_type, usage_date)
                VALUES (?, ?, CURRENT_DATE)
            """, (user_id, feature_type))

            conn.commit()

    def update_subscription(self, user_id: int, tier: str, expires_at: Optional[datetime] = None) -> None:
        """Update user's subscription tier and expiration"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET
                    subscription_tier = ?,
                    subscription_expires_at = ?
                WHERE id = ?
            """, (tier, expires_at, user_id))
            conn.commit()

    def get_subscription_code(self, code: str) -> Optional[SubscriptionCode]:
        """Get subscription code by code string"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subscription_codes WHERE code = ? AND is_active = 1", (code,))
            row = cursor.fetchone()
            if not row:
                return None
            return SubscriptionCode(
                id=row['id'],
                code=row['code'],
                tier=row['tier'],
                duration_days=row['duration_days'],
                max_uses=row['max_uses'],
                current_uses=row['current_uses'],
                is_active=bool(row['is_active']),
                created_at=row['created_at']
            )

    def redeem_code(self, user_id: int, code: str) -> bool:
        """Redeem subscription code for user"""
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get and validate code
            sub_code = self.get_subscription_code(code)
            if not sub_code or not sub_code.can_redeem():
                return False

            # Check if user already redeemed this code
            cursor.execute("""
                SELECT COUNT(*) as count FROM code_redemptions
                WHERE user_id = ? AND code = ?
            """, (user_id, code))
            if cursor.fetchone()['count'] > 0:
                return False

            # Calculate expiration date
            expires_at = None
            if sub_code.tier != "ultra":  # Ultra is permanent
                expires_at = datetime.now() + timedelta(days=sub_code.duration_days)

            try:
                # Update user subscription
                cursor.execute("""
                    UPDATE users SET
                        subscription_tier = ?,
                        subscription_expires_at = ?
                    WHERE id = ?
                """, (sub_code.tier, expires_at, user_id))

                # Increment code usage
                cursor.execute("""
                    UPDATE subscription_codes SET current_uses = current_uses + 1
                    WHERE code = ?
                """, (code,))

                # Record redemption
                cursor.execute("""
                    INSERT INTO code_redemptions (user_id, code, tier_granted, expires_at)
                    VALUES (?, ?, ?, ?)
                """, (user_id, code, sub_code.tier, expires_at))

                conn.commit()
                return True
            except:
                conn.rollback()
                return False