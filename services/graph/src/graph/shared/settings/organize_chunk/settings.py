from __future__ import annotations

from base import BaseModel

class OrganizeChunkSettings(BaseModel):
    THRESHOLD_CHAR_LIMIT: int = 1000