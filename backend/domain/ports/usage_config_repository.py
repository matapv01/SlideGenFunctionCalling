from typing import Protocol


class UsageConfigRepository(Protocol):
    """Persistence boundary for administrator-managed usage policy."""

    def get_weights(self, kind: str) -> dict[str, float]: ...

    def set_weight(self, kind: str, name: str, multiplier: float) -> None: ...

    def get_plan_limits(self) -> dict[str, dict[str, float | int]]: ...

    def set_plan_limits(
        self,
        tier: str,
        *,
        chat_credits: float,
        docx_upload: int,
        max_docx_slides: int,
        max_docx_file_mb: int,
        max_docx_total_mb: int,
    ) -> None: ...

    def reset_all_usage(self) -> int: ...
