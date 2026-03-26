# File: models/zone_models.py
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class LifecycleState(str, Enum):
    """Coarse health lifecycle labels for a zone."""
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    DEGRADED = "degraded"


class StrategicClass(str, Enum):
    """Strategic priority classes used for triage decisions."""
    RECOVERABLE = "recoverable"
    SALVAGEABLE = "salvageable"
    NOT_WORTH_SAVING = "not_worth_saving"


class ZoneState(BaseModel):
    """Hidden per-zone state tracked internally by the environment."""
    zone_id: int
    # Hidden map of core agronomic metrics.
    true_metrics: dict[str, float] = Field(default_factory=dict)
    crop_health: float = Field(ge=0.0, le=1.0)
    # Crop growth progress (0..1).
    crop_stage: float = Field(ge=0.0, le=1.0)
    # Observation confidence for this zone.
    uncertainty: float = Field(ge=0.0, le=1.0, default=0.1)
    # Aggregated health indicator derived from multiple hidden factors.
    health_score: float = Field(ge=0.0, le=1.0, default=1.0)
    # Cumulative damage severity; higher means harder recovery.
    degradation_level: float = Field(ge=0.0, le=1.0, default=0.0)
    # High-level lifecycle label.
    lifecycle_state: LifecycleState = LifecycleState.HEALTHY
    # Priority class for decision-making.
    strategic_class: StrategicClass = StrategicClass.RECOVERABLE
