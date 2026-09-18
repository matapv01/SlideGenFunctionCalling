# File: backend/infrastructure/database/repositories/sqlite_user_repo.py

from typing import Optional, List, Dict
import json
from datetime import datetime, date, timedelta
from backend.domain.entities.user import User, UserProfile, UserSettings, SubscriptionCode, CodeRedemption
from backend.domain.entities.user import USAGE_WINDOW_HOURS
from backend.domain.ports.user_repository import UserRepository
from backend.infrastructure.database.connection import get_db_connection


class SqliteUserRepository(UserRepository):
    @staticmethod
    def _load_plan_limits(tier: str) -> Optional[Dict[str, float | int]]:
        """Hydrate the user entity from the admin-managed policy table."""
        try:
            with get_db_connection() as conn:
                row = conn.execute(
                    """
                    SELECT chat_credits, docx_upload, max_docx_slides
                    FROM subscription_plan_limits
                    WHERE tier = ?
                    """,
                    (tier,),
                ).fetchone()
        except Exception:
            # Keep auth/user reads compatible with databases during migration;
            # SubscriptionService remains the authoritative policy boundary.
            return None
        if row is None:
            return None
        return {
            "chat_messages": float(row["chat_credits"]),
            "docx_upload": int(row["docx_upload"]),
            "max_docx_slides": int(row["max_docx_slides"]),
        }

    @staticmethod
    def _parse_usage_window_start(value) -> Optional[datetime]:
        if not value:
            return None
        try:
            return (
                datetime.fromisoformat(value.replace("Z", ""))
                if isinstance(value, str)
                else value
            )
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _now_for_window(window_start: Optional[datetime]) -> datetime:
        return datetime.now(tz=window_start.tzinfo) if window_start and window_start.tzinfo else datetime.now()

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
        except (KeyError, TypeError, IndexError):
            docx_usage_today = 0

        try:
            raw_window_start = row['usage_window_started_at']
        except (KeyError, TypeError, IndexError):
            raw_window_start = None
        usage_window_started_at = self._parse_usage_window_start(raw_window_start) or datetime.now()

        legacy_chat_usage = int(idea_usage_today)
        try:
            legacy_chat_usage = int(row['chat_usage_5h'] or 0)
        except (KeyError, TypeError, IndexError):
            pass

        chat_message_count = legacy_chat_usage
        try:
            chat_message_count = int(row['chat_messages_5h'] or legacy_chat_usage)
        except (KeyError, TypeError, IndexError):
            pass

        chat_usage = float(legacy_chat_usage)
        try:
            raw_chat_credits = row['chat_usage_credits_5h']
            if raw_chat_credits is not None:
                chat_usage = float(raw_chat_credits)
        except (KeyError, TypeError, IndexError, ValueError):
            pass

        docx_usage = 0
        try:
            docx_usage = int(row['docx_usage_5h'] or 0)
        except (KeyError, TypeError, IndexError):
            docx_usage = int(docx_usage_today)

        cancel_at_period_end = False
        try:
            cancel_at_period_end = bool(row['cancel_at_period_end'])
        except (KeyError, TypeError):
            cancel_at_period_end = False

        is_admin = False
        try:
            is_admin = bool(row['is_admin'])
        except (KeyError, TypeError, IndexError):
            is_admin = False

        return User(
            id=row['id'],
            email=row['email'],
            hashed_password=row['hashed_password'],
            subscription_tier=subscription_tier,
            subscription_expires_at=expires_at,
            daily_usage_reset_date=reset_date,
            idea_usage_today=idea_usage_today,
            docx_usage_today=docx_usage_today,
            usage_window_started_at=usage_window_started_at,
            plan_limits=self._load_plan_limits(subscription_tier),
            chat_usage=chat_usage,
            chat_message_count=chat_message_count,
            docx_usage=docx_usage,
            is_active=bool(row['is_active']),
            is_admin=is_admin,
            cancel_at_period_end=cancel_at_period_end,
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


    def list_admin_users(self) -> List[dict]:
        """Return the non-sensitive user fields needed by the admin console."""
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    u.id,
                    u.email,
                    u.subscription_tier,
                    u.is_active,
                    u.is_admin,
                    u.created_at,
                    u.usage_window_started_at,
                    COALESCE(u.chat_usage_credits_5h, 0) AS chat_usage,
                    COALESCE(u.chat_messages_5h, 0) AS chat_message_count,
                    COALESCE(u.docx_usage_5h, 0) AS docx_usage,
                    p.full_name
                FROM users AS u
                LEFT JOIN user_profiles AS p ON p.user_id = u.id
                ORDER BY u.id ASC
                """
            ).fetchall()
        return [dict(row) for row in rows]


    def count_admin_users(self) -> int:
        with get_db_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM users WHERE is_admin = 1 AND is_active = 1"
            ).fetchone()
        return int(row["count"] if row else 0)


    def set_admin_status(self, user_id: int, is_admin: bool) -> bool:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "UPDATE users SET is_admin = ? WHERE id = ?",
                (1 if is_admin else 0, user_id),
            )
            conn.commit()
        return cursor.rowcount > 0


    def create(self, user: User) -> User:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (
                    email, hashed_password, subscription_tier,
                    daily_usage_reset_date, idea_usage_today, docx_usage_today,
                    usage_window_started_at, chat_usage_5h,
                    chat_usage_credits_5h, chat_messages_5h, docx_usage_5h,
                    is_active, is_admin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.email, user.hashed_password, user.subscription_tier,
                user.daily_usage_reset_date, user.idea_usage_today, user.docx_usage_today,
                user.usage_window_started_at, user.chat_message_count,
                user.chat_usage, user.chat_message_count, user.docx_usage,
                user.is_active, user.is_admin
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

    def reset_usage_window(self, user_id: int) -> None:
        """Reset the user's rolling five-hour window when it has expired."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(
                "SELECT usage_window_started_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            if not row:
                return
            window_start = self._parse_usage_window_start(row['usage_window_started_at'])
            now = self._now_for_window(window_start)
            if window_start is not None and now < window_start + timedelta(hours=USAGE_WINDOW_HOURS):
                return

            cursor.execute(
                """
                UPDATE users SET
                    usage_window_started_at = ?,
                    daily_usage_reset_date = ?,
                    idea_usage_today = 0,
                    docx_usage_today = 0,
                    chat_usage_5h = 0,
                    chat_usage_credits_5h = 0,
                    chat_messages_5h = 0,
                    docx_usage_5h = 0
                WHERE id = ?
                """,
                (now, now.date(), user_id),
            )
            conn.commit()

    def force_reset_usage_window(self, user_id: int) -> bool:
        """Force a fresh five-hour window for one user right now."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(
                "SELECT usage_window_started_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            if not row:
                return False

            window_start = self._parse_usage_window_start(row["usage_window_started_at"])
            now = self._now_for_window(window_start)
            cursor.execute(
                """
                UPDATE users SET
                    usage_window_started_at = ?,
                    daily_usage_reset_date = ?,
                    idea_usage_today = 0,
                    docx_usage_today = 0,
                    chat_usage_5h = 0,
                    chat_usage_credits_5h = 0,
                    chat_messages_5h = 0,
                    docx_usage_5h = 0
                WHERE id = ?
                """,
                (now, now.date(), user_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def update_usage_count(
        self,
        user_id: int,
        feature_type: str,
        increment: int = 1,
        usage_cost: float = 1.0,
    ) -> None:
        """Update usage in the shared rolling five-hour window."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            row = cursor.execute(
                "SELECT usage_window_started_at FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            if not row:
                return

            window_start = self._parse_usage_window_start(row['usage_window_started_at'])
            now = self._now_for_window(window_start)
            if window_start is None or now >= window_start + timedelta(hours=USAGE_WINDOW_HOURS):
                cursor.execute(
                    """
                    UPDATE users SET
                        usage_window_started_at = ?,
                        daily_usage_reset_date = ?,
                        idea_usage_today = 0,
                        docx_usage_today = 0,
                        chat_usage_5h = 0,
                        chat_usage_credits_5h = 0,
                        chat_messages_5h = 0,
                        docx_usage_5h = 0
                    WHERE id = ?
                    """,
                    (now, now.date(), user_id),
                )

            if feature_type in {"chat_message", "chat_messages", "idea_generation"}:
                cursor.execute("""
                    UPDATE users SET
                        chat_usage_5h = COALESCE(chat_usage_5h, 0) + ?,
                        chat_usage_credits_5h = COALESCE(chat_usage_credits_5h, 0) + ?,
                        chat_messages_5h = COALESCE(chat_messages_5h, 0) + ?,
                        idea_usage_today = COALESCE(idea_usage_today, 0) + ?
                    WHERE id = ?
                """, (increment, usage_cost, increment, increment, user_id))
            elif feature_type == "docx_upload":
                cursor.execute("""
                    UPDATE users SET
                        docx_usage_5h = docx_usage_5h + ?,
                        docx_usage_today = docx_usage_today + ?
                    WHERE id = ?
                """, (increment, increment, user_id))

            if feature_type != "reset":
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
                code_type=row['code_type'] if row['code_type'] else 'limited',
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

            # Per-account check: limited codes can only be used once per account
            if sub_code.code_type == "limited":
                cursor.execute("""
                    SELECT COUNT(*) as count FROM code_redemptions
                    WHERE user_id = ? AND code = ?
                """, (user_id, code))
                if cursor.fetchone()['count'] > 0:
                    return False

            # Calculate expiration date — always duration_days from redemption
            expires_at = datetime.now() + timedelta(days=sub_code.duration_days)

            try:
                # Update user subscription
                cursor.execute("""
                    UPDATE users SET
                        subscription_tier = ?,
                        subscription_expires_at = ?,
                        cancel_at_period_end = 0
                    WHERE id = ?
                """, (sub_code.tier, expires_at, user_id))

                # Increment code usage (for limited codes only, for tracking)
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

    def cancel_subscription(self, user_id: int, immediate: bool = True) -> None:
        """Cancel user subscription. If immediate, downgrade to free right now."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if immediate:
                cursor.execute("""
                    UPDATE users SET
                        subscription_tier = 'free',
                        subscription_expires_at = NULL,
                        cancel_at_period_end = 0
                    WHERE id = ?
                """, (user_id,))
            else:
                cursor.execute("""
                    UPDATE users SET cancel_at_period_end = 1 WHERE id = ?
                """, (user_id,))
            conn.commit()
