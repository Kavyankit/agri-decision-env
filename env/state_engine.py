# File: env/state_engine.py
import random

from models.config_models import EnvConfig
from models.observation_models import Observation, ForecastDay
from models.zone_models import LifecycleState, StrategicClass, ZoneState
from config.env_presets import ALL_METRICS, get_visible_metrics
from env.constants import DEFAULT_CROP_HEALTH, DEFAULT_CROP_STAGE, DEFAULT_METRIC_VALUE
from env.sensor_model import observe_zone


def initialize_zones(config: EnvConfig) -> list[ZoneState]:
    """Create initial hidden zone states for a new episode."""
    # Phase 3: initialize hidden truth with the full metric universe.
    # Observability will be applied in build_observation() using task.visible_metrics.
    metrics = list(ALL_METRICS)
    zones: list[ZoneState] = []
    for zone_id in range(config.task.zone_count):
        zones.append(
            ZoneState(
                zone_id=zone_id,
                true_metrics={metric: DEFAULT_METRIC_VALUE for metric in metrics},
                crop_health=DEFAULT_CROP_HEALTH,
                crop_stage=DEFAULT_CROP_STAGE,
                # Start fully recoverable (no hidden degradation yet).
                uncertainty=0.1,
                health_score=1.0,
                degradation_level=0.0,
            )
        )
    return zones


def evolve_zone_lifecycle(zone: ZoneState, config: EnvConfig) -> None:
    """Update hidden lifecycle fields using simple passive deterioration."""
    # Passive deterioration rate tuned for Phase 3 only.
    # As crop_stage advances, we apply slightly more stress each day.
    # `config` reserved for future Phase-4/5 intervention/recovery dynamics.
    passive_rate = 0.01 + 0.01 * float(zone.crop_stage)

    zone.degradation_level = min(1.0, zone.degradation_level + passive_rate)
    zone.health_score = max(0.0, min(1.0, 1.0 - zone.degradation_level))

    # crop_health is a coarse survivability proxy; keep it correlated with degradation.
    zone.crop_health = max(0.0, min(1.0, 1.0 - 0.85 * zone.degradation_level))

    # Without a sensor model, "uncertainty" is treated as internal state volatility.
    zone.uncertainty = max(0.0, min(1.0, 0.1 + 0.5 * zone.degradation_level))

    if zone.degradation_level < 0.33:
        zone.lifecycle_state = LifecycleState.HEALTHY
        zone.strategic_class = StrategicClass.RECOVERABLE
    elif zone.degradation_level < 0.66:
        zone.lifecycle_state = LifecycleState.AT_RISK
        # Still potentially worth saving, but no longer "easy recovery".
        zone.strategic_class = StrategicClass.RECOVERABLE
    else:
        zone.lifecycle_state = LifecycleState.DEGRADED
        zone.strategic_class = StrategicClass.NOT_WORTH_SAVING


def evolve_zones(zones: list[ZoneState], config: EnvConfig) -> None:
    """Evolve lifecycle for all zones once per environment step/day."""
    for z in zones:
        evolve_zone_lifecycle(z, config)


def build_observation(
    day: int,
    zones: list[ZoneState],
    remaining_budget: float,
    remaining_time_budget: float,
    visible_metrics_count: int,
    config: EnvConfig,
    stale_days_by_zone: dict[int, int],
    rng: random.Random,
    forecast: list[ForecastDay],
) -> Observation:
    """Convert hidden state and resource counters into an agent observation."""
    # Difficulty controls how many metric names are visible to the agent.
    visible_metric_names = get_visible_metrics(visible_metrics_count)

    # Phase 5: observation layer uses sensor model (noise/bias/stale/missing/outlier).
    # `forecast` is provided by the weather engine (Phase 6).
    zone_obs = [
        observe_zone(
            zone=z,
            visible_metric_names=visible_metric_names,
            stale_days=stale_days_by_zone.get(z.zone_id, 0),
            config=config,
            rng=rng,
        )
        for z in zones
    ]
    return Observation(
        day=day,
        zones=zone_obs,
        remaining_budget=remaining_budget,
        remaining_time_budget=remaining_time_budget,
        forecast=forecast,
    )
