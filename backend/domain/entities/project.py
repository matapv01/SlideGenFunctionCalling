# File: backend/domain/entities/project.py

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Slide:
    id: Optional[int]
    project_id: int
    slide_index: int
    slide_type: str # 'intro', 'content', 'thank_you'
    title: str
    content_text: str
    html_content: str
    design_settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Project:
    id: Optional[int]
    user_id: int
    title: str
    description: Optional[str]
    source_type: str # 'docx', 'idea'
    status: str # 'processing', 'completed'
    updated_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    slides: List[Slide] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Business Logic nằm ở đây (Ví dụ)
    def add_slide(self, slide: Slide):
        self.slides.append(slide)
        self.slides.sort(key=lambda x: x.slide_index)