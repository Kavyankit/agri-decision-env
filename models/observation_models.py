# File: models/observation_models.py
from __future__ import annotations

from pydantic import BaseModel, Field


class ForecastDay(BaseModel):
    """One forecast entry exposed to the agent."""
    # Structured forecast object to avoid brittle free-text weather strings.
    # Chance of rainfall for this forecast day (0..1).
    rain_probability: float = Field(ge=0.0, le=1.0)
    # Expected daily temperature in project-defined units.
    temperature: float


class ZoneObservation(BaseModel):
    """Observable per-zone view available to the agent at step time."""
    # Numeric zone index in the field.
    zone_id: int
    # Sparse/dense metric map; key count changes with task difficulty.
    observed_metrics: dict[str, float | None] = Field(default_factory=dict)
    # Estimated crop health in this zone (optional because of partial observability).
    crop_health: float | None = Field(default=None, ge=0.0, le=1.0)
    # Estimated growth progress in this zone (optional because of partial observability).
    crop_stage: float | None = Field(default=None, ge=0.0, le=1.0)
    # Confidence/uncertainty proxy for current observation quality.
    uncertainty: float = Field(ge=0.0, le=1.0, default=0.1)
    # Tracks how old the latest reading is for this zone.
    stale_days: int = Field(ge=0, default=0)


class Observation(BaseModel):
    """Top-level observation returned by reset() and step()."""
    # Current simulation day index.
    day: int = Field(ge=0)
    # Per-zone observations visible to the agent at this step.
    zones: list[ZoneObservation]
    # Budget left for the current episode.
    remaining_budget: float = Field(ge=0.0)
    # Time budget left for the current day.
    remaining_time_budget: float = Field(ge=0.0)
    # Forecast horizon provided to the agent.
    forecast: list[ForecastDay] = Field(default_factory=list)
