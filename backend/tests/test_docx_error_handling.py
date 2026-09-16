import asyncio
from datetime import date

import pytest
from fastapi import HTTPException

from backend.api.constants import EventTypes
from backend.api.v1.generate_router import (
    _run_stream_task,
    _workflow_error_payload,
)
from backend.application.services.subscription_service import SubscriptionService
from backend.domain.entities.user import User


class _FakeUserRepository:
    def update_usage_count(self, *args, **kwargs):
        return None


def _user(tier: str = "free") -> User:
    return User(
        id=1,
        email="test@example.com",
        hashed_password="hashed",
        subscription_tier=tier,
        daily_usage_reset_date=date.today(),
    )


def test_docx_slide_limit_is_expanded_and_has_clear_error() -> None:
    user = _user()
    service = SubscriptionService(_FakeUserRepository())

    assert user.get_daily_limits()["max_docx_slides"] == 50

    with pytest.raises(HTTPException) as error:
        service.check_feature_access(user, "docx_upload", slide_count=51)

    assert error.value.status_code == 413
    assert "Tài liệu quá dài" in str(error.value.detail)
    assert "50" in str(error.value.detail)


def test_workflow_error_payload_keeps_document_too_long_reason() -> None:
    payload = _workflow_error_payload(
        HTTPException(status_code=413, detail="Tài liệu quá dài (51 slides).")
    )

    assert payload["code"] == "DOCUMENT_TOO_LONG"
    assert payload["message"] == "Tài liệu quá dài (51 slides)."


def test_stream_task_emits_runtime_error_instead_of_generic_failure() -> None:
    async def failing_runner() -> None:
        raise RuntimeError("Connection error")

    async def run_test() -> tuple[str, dict]:
        queue = asyncio.Queue()
        await _run_stream_task(queue, failing_runner, "TEST")
        return await queue.get()

    event_type, payload = asyncio.run(run_test())

    assert event_type == EventTypes.ERROR_EVENT
    assert payload["message"] == "Không thể tạo slide: Connection error"
