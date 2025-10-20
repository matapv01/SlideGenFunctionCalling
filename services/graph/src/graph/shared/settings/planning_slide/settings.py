from __future__ import annotations


from base import BaseModel

class PlanningSlideSettings(BaseModel):
    model: str = 'gemini-2.0-flash'
    planning_batch_size: int = 5