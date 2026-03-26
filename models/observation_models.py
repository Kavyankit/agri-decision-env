# File: models/observation_models.py
from __future__ import annotations

from pydantic import BaseModel, Field


class ForecastDay(BaseModel):
    # Structured forecast object to avoid brittle free-text weather strings.
    rain_probability: float = Field(ge=0.0, le=1.0)
    temperature: float


class ZoneObservation(BaseModel):
    zone_id: int
    # Sparse/dense metric map; key count changes with task difficulty.
    observed_metrics: dict[str, float | None] = Field(default_factory=dict)
    crop_health: float | None = Field(default=None, ge=0.0, le=1.0)
    crop_stage: float | None = Field(default=None, ge=0.0, le=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0, default=0.1)
    # Tracks how old the latest reading is for this zone.
    stale_days: int = Field(ge=0, default=0)


class Observation(BaseModel):
    day: int = Field(ge=0)
    zones: list[ZoneObservation]
    remaining_budget: float = Field(ge=0.0)
    remaining_time_budget: float = Field(ge=0.0)
    forecast: list[ForecastDay] = Field(default_factory=list)
