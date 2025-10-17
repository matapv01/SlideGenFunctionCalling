from __future__ import annotations

from base import BaseModel

class ContentSplitterSettings(BaseModel):
    CONTENT_CHAR_LIMIT_FOR_SPLIT: int = 1000