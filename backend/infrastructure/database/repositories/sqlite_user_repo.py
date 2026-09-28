# File: backend/infrastructure/database/repositories/sqlite_user_repo.py

from typing import Optional, List, Dict
import json
import shutil
from datetime import datetime, date, timedelta
from pathlib import Path
from backend.domain.entities.user import User, UserProfile, UserSettings, SubscriptionCode, CodeRedemption
from backend.domain.entities.user import USAGE_WINDOW_HOURS
from backend.domain.ports.user_repository import UserRepository
from backend.infrastructure.database.connection import get_db_connection
from backend.config import CHATBOT_DOCUMENTS_DIR


class SqliteUserRepository(UserRepository):
    @staticmethod
    def _load_plan_limits(tier: str) -> Optional[Dict[str, float | int]]:
        """Hydrate the user entity from the admin-managed policy table."""
        try:
            with get_db_connection() as conn:
                row = conn.execute(
                    """
                    SELECT chat_credits, docx_upload, max_docx_slides,
                           max_docx_file_mb, max_docx_total_mb
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
            "max_docx_file_mb": int(row["max_docx_file_mb"]),
            "max_docx_total_mb": int(row["max_docx_total_mb"]),
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
            docx_usage = float(row['docx_usage_5h'] or 0)
        except (KeyError, TypeError, IndexError):
            docx_usage = float(docx_usage_today)

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

        email_verified = True
        try:
            email_verified = bool(row['email_verified'])
        except (KeyError, TypeError, IndexError):
            email_verified = True

        onboarding_completed = True
        try:
            onboarding_completed = bool(row['onboarding_completed'])
        except (KeyError, TypeError, IndexError):
            pass

        workspace_tour_version = 1
        try:
            workspace_tour_version = int(row['workspace_tour_version'])
        except (KeyError, TypeError, IndexError, ValueError):
            pass

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
            email_verified=email_verified,
            onboarding_completed=onboarding_completed,
            workspace_tour_version=workspace_tour_version,
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
                    is_active, email_verified, is_admin, onboarding_completed,
                    workspace_tour_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user.email, user.hashed_password, user.subscription_tier,
                user.daily_usage_reset_date, user.idea_usage_today, user.docx_usage_today,
                user.usage_window_started_at, user.chat_message_count,
                user.chat_usage, user.chat_message_count, user.docx_usage,
                user.is_active, user.email_verified, user.is_admin, user.onboarding_completed,
                user.workspace_tour_version
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


    def mark_email_verified(self, user_id: int) -> None:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "UPDATE users SET email_verified = 1 WHERE id = ?",
                (user_id,),
            )
            if cursor.rowcount == 0:
                raise LookupError("User not found")
            conn.commit()

    def complete_onboarding(self, user_id: int, use_cases: list[str], role: str | None) -> None:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE users SET onboarding_completed = 1,
                    onboarding_use_cases = ?, onboarding_role = ?
                WHERE id = ?
                """,
                (json.dumps(use_cases), role, user_id),
            )
            if cursor.rowcount == 0:
                raise LookupError("User not found")
            conn.commit()


    def complete_workspace_tour(self, user_id: int, version: int = 1) -> None:
        with get_db_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE users SET workspace_tour_version = MAX(workspace_tour_version, ?)
                WHERE id = ?
                """,
                (version, user_id),
            )
            if cursor.rowcount == 0:
                raise LookupError("User not found")
            conn.commit()


    def delete_user(self, user_id: int) -> dict:
        """Delete an account and its owned workspace data in one transaction."""
        document_paths: list[str] = []
        document_ids: list[str] = []
        deleted_user: dict | None = None

        with get_db_connection() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            tables = {
                row[0]
                for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
            }
            user_row = conn.execute(
                "SELECT id, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            if user_row is None:
                raise LookupError("User not found")
            deleted_user = {"id": int(user_row["id"]), "email": user_row["email"]}

            def ids_for(table: str, column: str, values: list) -> list:
                if table not in tables or not values:
                    return []
                placeholders = ",".join("?" for _ in values)
                return [
                    row[0]
                    for row in conn.execute(
                        f"SELECT id FROM {table} WHERE {column} IN ({placeholders})",
                        values,
                    ).fetchall()
                ]

            def delete_by(table: str, column: str, values: list) -> None:
                if table not in tables or not values:
                    return
                placeholders = ",".join("?" for _ in values)
                conn.execute(
                    f"DELETE FROM {table} WHERE {column} IN ({placeholders})",
                    values,
                )

            project_ids = ids_for("projects", "user_id", [user_id])

            relation_clauses = ["user_id = ?"]
            relation_values: list = [user_id]
            if project_ids:
                project_placeholders = ",".join("?" for _ in project_ids)
                relation_clauses.append(f"project_id IN ({project_placeholders})")
                relation_values.extend(project_ids)
            relation_where = " OR ".join(relation_clauses)

            session_ids = []
            if "chatbot_sessions" in tables:
                session_ids = [
                    row[0]
                    for row in conn.execute(
                        f"SELECT id FROM chatbot_sessions WHERE {relation_where}",
                        relation_values,
                    ).fetchall()
                ]

            if "chatbot_documents" in tables:
                document_rows = conn.execute(
                    f"SELECT id, markdown_path FROM chatbot_documents WHERE {relation_where}",
                    relation_values,
                ).fetchall()
                document_ids = [str(row["id"]) for row in document_rows]
                document_paths = [
                    str(row["markdown_path"])
                    for row in document_rows
                    if row["markdown_path"]
                ]

            message_ids = ids_for("chatbot_messages", "session_id", session_ids)
            chunk_ids = ids_for("chatbot_document_chunks", "document_id", document_ids)
            delete_by("chatbot_message_citations", "message_id", message_ids)
            delete_by("chatbot_message_citations", "document_id", document_ids)
            delete_by("chatbot_message_citations", "chunk_id", chunk_ids)
            delete_by("chatbot_session_documents", "session_id", session_ids)
            delete_by("chatbot_session_documents", "document_id", document_ids)
            delete_by("chatbot_document_chunks", "document_id", document_ids)
            delete_by("chatbot_messages", "session_id", session_ids)
            delete_by("chatbot_documents", "id", document_ids)
            delete_by("chatbot_sessions", "id", session_ids)

            delete_by("slides", "project_id", project_ids)
            delete_by("project_metadata", "project_id", project_ids)
            delete_by("project_collaborators", "project_id", project_ids)
            delete_by("project_versions", "project_id", project_ids)
            delete_by("project_comments", "project_id", project_ids)
            delete_by("project_collaborators", "user_id", [user_id])
            delete_by("project_collaborators", "invited_by", [user_id])
            delete_by("project_versions", "user_id", [user_id])
            delete_by("project_comments", "user_id", [user_id])

            for table in (
                "user_profiles",
                "user_settings",
                "code_redemptions",
                "daily_usage_logs",
                "user_assets",
            ):
                delete_by(table, "user_id", [user_id])

            delete_by("projects", "id", project_ids)
            delete_by("users", "id", [user_id])
            conn.commit()

        storage_root = Path(CHATBOT_DOCUMENTS_DIR).resolve()
        for raw_path in document_paths:
            try:
                path = Path(raw_path).resolve()
                if storage_root in path.parents:
                    path.unlink(missing_ok=True)
            except OSError:
                pass
        for document_id in document_ids:
            for path in (
                storage_root / f"{document_id}.docx",
                storage_root / f"{document_id}.md",
                storage_root / f"{document_id}_images",
            ):
                try:
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                    else:
                        path.unlink(missing_ok=True)
                except OSError:
                    pass

        return deleted_user or {"id": user_id, "email": ""}


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
                """, (usage_cost, usage_cost, user_id))

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
