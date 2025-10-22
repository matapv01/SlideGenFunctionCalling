from __future__ import annotations


from base import BaseModel

class PlanningSlideSettings(BaseModel):
    model: str
    planning_batch_size: int