from datetime import datetime, timedelta

import pytest

from backend.application.services.auth_service import AuthService
from backend.application.services.subscription_service import SubscriptionService
from backend.infrastructure.database import connection
from backend.infrastructure.database.repositories.sqlite_usage_config_repo import (
    SqliteUsageConfigRepository,
)
from backend.infrastructure.database.repositories.sqlite_user_repo import (
    SqliteUserRepository,
)


def _insert_user(email: str, started_at: datetime) -> int:
    with connection.get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (
                email, hashed_password, usage_window_started_at,
                chat_usage_credits_5h, chat_messages_5h, docx_usage_5h
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (email, "old-password-hash", started_at, 1.5, 2, 1),
        )
        conn.commit()
        return int(cursor.lastrowid)


def test_admin_user_reset_starts_a_new_individual_window_and_resets_password(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        connection,
        "DATABASE_PATH",
        str(tmp_path / "admin-user-management.db"),
    )
    connection.init_db()

    old_start = datetime.now() - timedelta(hours=1)
    user_id = _insert_user("managed@example.com", old_start)
    user_repo = SqliteUserRepository()
    service = SubscriptionService(user_repo, SqliteUsageConfigRepository())

    before = service.get_admin_user(user_id)
    assert before["chat_usage"] == 1.5
    assert before["docx_usage"] == 1

    refreshed = service.reset_user_usage(user_id)

    assert refreshed["chat_usage"] == 0
    assert refreshed["chat_message_count"] == 0
    assert refreshed["docx_usage"] == 0
    assert refreshed["usage_window_started_at"] > before["usage_window_started_at"]
    assert refreshed["usage_reset_at"] - refreshed["usage_window_started_at"] == timedelta(hours=5)

    auth_service = AuthService(user_repo)
    auth_service.reset_password(user_id, "default-password")
    updated = user_repo.get_by_id(user_id)
    assert updated is not None
    assert auth_service.verify_password("default-password", updated.hashed_password)


def test_admin_role_is_persisted_and_cannot_remove_the_last_admin(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        connection,
        "DATABASE_PATH",
        str(tmp_path / "admin-role.db"),
    )
    connection.init_db()

    first_id = _insert_user("first-admin@example.com", datetime.now())
    second_id = _insert_user("second-admin@example.com", datetime.now())
    user_repo = SqliteUserRepository()
    user_repo.set_admin_status(first_id, True)
    service = SubscriptionService(user_repo, SqliteUsageConfigRepository())

    promoted = service.update_admin_role(
        actor_user_id=first_id,
        target_user_id=second_id,
        is_admin=True,
    )
    assert promoted["is_admin"] is True

    demoted = service.update_admin_role(
        actor_user_id=first_id,
        target_user_id=second_id,
        is_admin=False,
    )
    assert demoted["is_admin"] is False

    with pytest.raises(ValueError, match="cuối cùng"):
        service.update_admin_role(
            actor_user_id=999,
            target_user_id=first_id,
            is_admin=False,
        )
