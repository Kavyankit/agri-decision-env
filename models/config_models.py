# File: models/config_models.py
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    """Supported benchmark difficulty tiers."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SensorNoiseConfig(BaseModel):
    """Noise model parameters used to transform hidden truth into observations."""
    # Random noise level added to observed metrics.
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
    """Reward component multipliers used by reward_engine."""
    # These are tunable multipliers used by reward_engine.
    # They control scoring emphasis, not measured field values.
    # Higher positive weights encourage that behavior; higher penalty weights discourage it.
    # Keep values comparable (same rough scale) to avoid one term dominating rewards.
    # Rewards can still be computed from raw signals in reward_models.py (RewardBreakdown).
    # This config only decides how strongly each signal contributes to the final score.
    # Encourages preserving/improving yield potential over time.
    yield_weight: float = 1.0
    # Rewards doing more with fewer actions/resources.
    efficiency_weight: float = 0.2
    # Rewards strategic deprioritization when sacrifice is the better long-term choice.
    sacrifice_weight: float = 0.4
    # Penalizes expensive actions to model limited resources.
    cost_penalty_weight: float = 0.2
    # Penalizes repeated or excessive interventions.
    overuse_penalty_weight: float = 0.4
    # Penalizes actions with little/no value added.
    waste_penalty_weight: float = 0.2


class TaskConfig(BaseModel):
    """Task-level scenario settings (horizon, scale, and constraints)."""
    # Task ID used across the system.
    task_id: str
    # Difficulty tier controlling preset constraints and observability.
    difficulty: Difficulty
    # Number of days in one episode.
    max_days: int = Field(ge=1)
    # Number of field zones active in this task.
    zone_count: int = Field(ge=1)
    # Number of exposed metrics from ALL_METRICS for this difficulty.
    visible_metrics: int = Field(ge=1)
    # Daily cap on number of executable actions.
    max_actions_per_day: int = Field(ge=1)
    # Daily operational time available to the agent.
    daily_time_budget: float = Field(gt=0)
    # Starting resource budget for the full episode.
    initial_budget: float = Field(ge=0)


class EnvConfig(BaseModel):
    """Top-level environment configuration bundle."""
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
    # Turns sensor noise effects on/off.
    noise_enabled: bool = True
    # If set, caps how many zones can be observed per day.
    max_zones_observable_per_day: int | None = Field(default=None, ge=1)
    # Randomize initial hidden zone state at reset.
    random_zone_init: bool = True
