from datetime import datetime

from backend.domain.ports.usage_config_repository import UsageConfigRepository
from backend.infrastructure.database.connection import get_db_connection


class SqliteUsageConfigRepository(UsageConfigRepository):
    """SQLite adapter for admin-controlled chatbot usage policy."""

    def get_weights(self, kind: str) -> dict[str, float]:
        with get_db_connection() as conn:
            rows = conn.execute(
                "SELECT name, multiplier FROM chatbot_usage_weights WHERE kind = ?",
                (kind,),
            ).fetchall()
        return {str(row["name"]): float(row["multiplier"]) for row in rows}

    def set_weight(self, kind: str, name: str, multiplier: float) -> None:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO chatbot_usage_weights (kind, name, multiplier, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(kind, name) DO UPDATE SET
                    multiplier = excluded.multiplier,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (kind, name, multiplier),
            )
            conn.commit()

    def get_plan_limits(self) -> dict[str, dict[str, float | int]]:
        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT tier, chat_credits, docx_upload, max_docx_slides
                       , max_docx_file_mb, max_docx_total_mb
                FROM subscription_plan_limits
                ORDER BY CASE tier
                    WHEN 'free' THEN 1
                    WHEN 'plus' THEN 2
                    WHEN 'ultra' THEN 3
                    ELSE 4
                END
                """
            ).fetchall()
        return {
            str(row["tier"]): {
                "chat_credits": float(row["chat_credits"]),
                "docx_upload": int(row["docx_upload"]),
                "max_docx_slides": int(row["max_docx_slides"]),
                "max_docx_file_mb": int(row["max_docx_file_mb"]),
                "max_docx_total_mb": int(row["max_docx_total_mb"]),
            }
            for row in rows
        }

    def set_plan_limits(
        self,
        tier: str,
        *,
        chat_credits: float,
        docx_upload: int,
        max_docx_slides: int,
        max_docx_file_mb: int,
        max_docx_total_mb: int,
    ) -> None:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO subscription_plan_limits
                    (tier, chat_credits, docx_upload, max_docx_slides,
                     max_docx_file_mb, max_docx_total_mb, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(tier) DO UPDATE SET
                    chat_credits = excluded.chat_credits,
                    docx_upload = excluded.docx_upload,
                    max_docx_slides = excluded.max_docx_slides,
                    max_docx_file_mb = excluded.max_docx_file_mb,
                    max_docx_total_mb = excluded.max_docx_total_mb,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    tier,
                    chat_credits,
                    docx_upload,
                    max_docx_slides,
                    max_docx_file_mb,
                    max_docx_total_mb,
                ),
            )
            conn.commit()

    def reset_all_usage(self) -> int:
        now = datetime.now()
        with get_db_connection() as conn:
            cursor = conn.execute(
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
                """,
                (now, now.date()),
            )
            conn.commit()
            return max(0, int(cursor.rowcount))
