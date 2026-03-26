# File: models/zone_models.py
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class LifecycleState(str, Enum):
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    DEGRADED = "degraded"


class StrategicClass(str, Enum):
    RECOVERABLE = "recoverable"
    SALVAGEABLE = "salvageable"
    NOT_WORTH_SAVING = "not_worth_saving"


class ZoneState(BaseModel):
    zone_id: int
    # Canonical hidden state map for all low-level agronomic metrics.
    true_metrics: dict[str, float] = Field(default_factory=dict)
    crop_health: float = Field(ge=0.0, le=1.0)
    # Normalized growth progress across the crop lifecycle (0..1).
    crop_stage: float = Field(ge=0.0, le=1.0)
    # Zone-level confidence proxy; can increase with poor sensing quality.
    uncertainty: float = Field(ge=0.0, le=1.0, default=0.1)
    # Aggregated health indicator derived from multiple hidden factors.
    health_score: float = Field(ge=0.0, le=1.0, default=1.0)
    degradation_level: float = Field(ge=0.0, le=1.0, default=0.0)
    lifecycle_state: LifecycleState = LifecycleState.HEALTHY
    strategic_class: StrategicClass = StrategicClass.RECOVERABLE
