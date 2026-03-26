# File: config/env_presets.py
from __future__ import annotations

from collections.abc import Callable

from models.config_models import Difficulty, EnvConfig, RewardWeights, SensorNoiseConfig, TaskConfig

# Metric semantics reference (Phase 1 doc-comment):
# - soil_moisture: Root-zone water availability; low values increase crop stress.
# - ph: Acidity/alkalinity balance; out-of-range values reduce nutrient uptake.
# - nitrogen: Primary vegetative nutrient; low levels reduce growth rate.
# - phosphorus: Root/energy-transfer nutrient; low levels hurt establishment.
# - potassium: Water regulation/stress nutrient; low levels reduce resilience.
# - canopy_temp: Heat stress proxy; elevated values can indicate water stress.
# - salinity: Salt load in soil; high salinity suppresses uptake and growth.
# - organic_matter: Soil quality proxy; supports moisture retention and fertility.
# - evapotranspiration: Water loss demand; higher values increase irrigation need.
# - leaf_wetness: Surface moisture proxy; persistent wetness can raise disease risk.
# - chlorophyll_index: Plant vigor proxy; lower values often reflect nutrient stress.
# - pest_pressure: Biotic stress level; higher pressure can degrade crop health.
# - disease_risk: Probability/intensity of disease conditions.
# - root_zone_stress: Composite subsurface stress indicator affecting growth.
# - water_table_depth: Subsurface water availability proxy; extremes can hurt roots.
# - compaction_index: Soil density proxy; high compaction limits root penetration.
# - solar_radiation: Photosynthetic energy input affecting growth potential.
# - wind_speed: Microclimate stress factor influencing evapotranspiration.

ALL_METRICS: list[str] = [
    "soil_moisture",
    "ph",
    "nitrogen",
    "phosphorus",
    "potassium",
    "canopy_temp",
    "salinity",
    "organic_matter",
    "evapotranspiration",
    "leaf_wetness",
    "chlorophyll_index",
    "pest_pressure",
    "disease_risk",
    "root_zone_stress",
    "water_table_depth",
    "compaction_index",
    "solar_radiation",
    "wind_speed",
]


def get_visible_metrics(visible_count: int) -> list[str]:
    """Return the first N metric names exposed for a task difficulty."""
    # Enforces difficulty ladder bounds (easy/medium/hard metric exposure).
    if visible_count < 1 or visible_count > len(ALL_METRICS):
        raise ValueError(f"visible_count must be between 1 and {len(ALL_METRICS)}")
    return ALL_METRICS[:visible_count]


def easy_preset(seed: int | None = 42) -> EnvConfig:
    """Low-noise, high-resource environment for baseline learning."""
    return EnvConfig(
        seed=seed,
        task=TaskConfig(
            task_id="easy",
            difficulty=Difficulty.EASY,
            max_days=10,
            zone_count=6,
            visible_metrics=5,
            max_actions_per_day=6,
            daily_time_budget=10.0,  # hours per day
            initial_budget=150.0,  # normalized cost units
        ),
        sensor_noise=SensorNoiseConfig(
            gaussian_std=0.03,
            bias=0.0,
            missing_probability=0.01,
            outlier_probability=0.01,
            staleness_drift=0.01,
        ),
        reward_weights=RewardWeights(
            yield_weight=1.0,
            efficiency_weight=0.1,
            sacrifice_weight=0.0,
            cost_penalty_weight=0.1,
            overuse_penalty_weight=0.1,
            waste_penalty_weight=0.1,
        ),
        max_zones_observable_per_day=6,
    )


def medium_preset(seed: int | None = 42) -> EnvConfig:
    """Balanced constraints and moderate uncertainty for general evaluation."""
    return EnvConfig(
        seed=seed,
        task=TaskConfig(
            task_id="medium",
            difficulty=Difficulty.MEDIUM,
            max_days=14,
            zone_count=10,
            visible_metrics=10,
            max_actions_per_day=5,
            daily_time_budget=8.0,  # hours per day
            initial_budget=100.0,  # normalized cost units
        ),
        sensor_noise=SensorNoiseConfig(
            gaussian_std=0.03,
            bias=0.01,
            missing_probability=0.03,
            outlier_probability=0.03,
            staleness_drift=0.03,
        ),
        reward_weights=RewardWeights(
            yield_weight=1.0,
            efficiency_weight=0.1,
            sacrifice_weight=0.0,
            cost_penalty_weight=0.1,
            overuse_penalty_weight=0.1,
            waste_penalty_weight=0.1,
        ),
        max_zones_observable_per_day=8,
    )


def hard_preset(seed: int | None = 42) -> EnvConfig:
    """High-uncertainty, resource-tight setup emphasizing strategic tradeoffs."""
    return EnvConfig(
        seed=seed,
        task=TaskConfig(
            task_id="hard",
            difficulty=Difficulty.HARD,
            max_days=21,
            zone_count=14,
            visible_metrics=18,
            max_actions_per_day=4,
            daily_time_budget=6.0,  # hours per day
            initial_budget=70.0,  # normalized cost units
        ),
        sensor_noise=SensorNoiseConfig(
            gaussian_std=0.05,
            bias=0.02,
            missing_probability=0.06,
            outlier_probability=0.06,
            staleness_drift=0.05,
        ),
        reward_weights=RewardWeights(
            yield_weight=1.0,
            efficiency_weight=0.25,
            sacrifice_weight=0.6,
            cost_penalty_weight=0.1,
            overuse_penalty_weight=0.5,
            waste_penalty_weight=0.3,
        ),
        max_zones_observable_per_day=10,
    )


PRESETS: dict[Difficulty, Callable[[int | None], EnvConfig]] = {
    Difficulty.EASY: easy_preset,
    Difficulty.MEDIUM: medium_preset,
    Difficulty.HARD: hard_preset,
}


def get_config(difficulty: Difficulty, seed: int | None = 42) -> EnvConfig:
    """Build and return a fresh EnvConfig for the requested difficulty."""
    # Return a fresh config object per call to avoid shared mutable state.
    return PRESETS[difficulty](seed)
