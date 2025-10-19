from __future__ import annotations

from base import BaseModel

class ContentSplitterSettings(BaseModel):
    content_char_limit_for_split: int