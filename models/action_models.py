# File: models/action_models.py
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Supported action categories for one environment step."""
    TAKE_READING = "take_reading"
    APPLY_INPUT = "apply_input"
    IRRIGATE = "irrigate"
    WAIT = "wait"


class TaskAction(BaseModel):
    """Single zone-level operation requested by the agent."""
    zone_id: int
    action_type: ActionType
    # Used by APPLY_INPUT to specify nutrient/input category.
    input_type: str | None = None
    # Quantity of water/input to apply; interpretation depends on action_type.
    amount: float = Field(ge=0.0, default=0.0)
    duration_hours: float = Field(ge=0.0, default=0.0)
    cost: float = Field(ge=0.0, default=0.0)


class Action(BaseModel):
    """Collection of zone-level tasks executed in one step/day."""
    tasks: list[TaskAction] = Field(default_factory=list)
