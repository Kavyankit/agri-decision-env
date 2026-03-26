# File: models/config_models.py
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SensorNoiseConfig(BaseModel):
    # Standard deviation for zero-mean Gaussian perturbation on observed metrics.
    gaussian_std: float = Field(ge=0.0, default=0.05)
    # Systematic offset applied to readings to model biased sensors.
    bias: float = Field(default=0.0)
    # Chance that a reading is unavailable for a metric on a given step.
    missing_probability: float = Field(ge=0.0, le=1.0, default=0.0)
    # Chance that a reading is replaced by an extreme value.
    outlier_probability: float = Field(ge=0.0, le=1.0, default=0.0)
    # Additional drift added as readings become stale between sensing events.
    staleness_drift: float = Field(ge=0.0, default=0.0)


class RewardWeights(BaseModel):
    # Coefficients used by reward_engine; these are not runtime reward values.
    yield_weight: float = 1.0
    efficiency_weight: float = 0.2
    sacrifice_weight: float = 0.4
    cost_penalty_weight: float = 0.2
    overuse_penalty_weight: float = 0.4
    waste_penalty_weight: float = 0.2


class TaskConfig(BaseModel):
    task_id: str
    difficulty: Difficulty
    max_days: int = Field(ge=1)
    zone_count: int = Field(ge=1)
    # Number of metrics exposed from ALL_METRICS for this difficulty.
    visible_metrics: int = Field(ge=1)
    max_actions_per_day: int = Field(ge=1)
    daily_time_budget: float = Field(gt=0)
    initial_budget: float = Field(ge=0)


class EnvConfig(BaseModel):
    seed: int | None = None
    task: TaskConfig
    sensor_noise: SensorNoiseConfig
    reward_weights: RewardWeights
    # Toggle to include weather effects in dynamics and observations.
    weather_enabled: bool = True
    # Number of forecast days exposed in Observation.forecast.
    forecast_horizon: int = Field(ge=0, default=3)
    # Enables travel-time feasibility constraints (not monetary travel cost).
    travel_constraints_enabled: bool = True
    # Master switch for sensor noise/bias/missingness.
    noise_enabled: bool = True
    # If set, caps how many zones can be observed per day.
    max_zones_observable_per_day: int | None = Field(default=None, ge=1)
    # Controls whether initial zone hidden state is randomized on reset.
    random_zone_init: bool = True
