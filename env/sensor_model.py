# File: env/sensor_model.py
from __future__ import annotations

import random

from models.config_models import EnvConfig
from models.observation_models import ZoneObservation
from models.zone_models import ZoneState


def _clamp01(value: float) -> float:
    """Clamp values to the stable metric range [0, 1]."""
    return max(0.0, min(1.0, value))


def _observe_metric(true_value: float, stale_days: int, config: EnvConfig, rng: random.Random) -> float | None:
    """Map hidden metric truth to observed value with Phase-5 sensor effects."""
    if not config.noise_enabled:
        # Deterministic mode: return true value (still clamped for safety).
        return _clamp01(true_value)

    noise = config.sensor_noise
    # Staler readings are more likely to be missing.
    missing_prob = min(1.0, noise.missing_probability * (1.0 + 0.15 * stale_days))
    if rng.random() < missing_prob:
        # None means "sensor could not produce this reading."
        return None

    # Noise grows with staleness so old readings become less reliable.
    std = noise.gaussian_std * (1.0 + noise.staleness_drift * stale_days)
    observed = true_value + noise.bias + rng.gauss(0.0, std)

    if rng.random() < noise.outlier_probability:
        # Outliers represent occasional bad sensor spikes.
        # The cap avoids extreme values dominating the signal.
        outlier_mag = min(0.2, max(0.05, 2.5 * max(std, 0.01)))
        observed += outlier_mag if rng.random() < 0.5 else -outlier_mag

    return _clamp01(observed)


def observe_zone(
    zone: ZoneState,
    visible_metric_names: list[str],
    stale_days: int,
    config: EnvConfig,
    rng: random.Random,
) -> ZoneObservation:
    """Build one zone observation with partial observability and sensor noise."""
    observed_metrics: dict[str, float | None] = {}
    for name in visible_metric_names:
        if name not in zone.true_metrics:
            raise ValueError(f"Unknown metric in observation slice: {name}")
        # Convert hidden truth into what the agent "sees" through sensors.
        observed_metrics[name] = _observe_metric(zone.true_metrics[name], stale_days, config, rng)

    if not config.noise_enabled:
        # In deterministic mode, use internal uncertainty directly.
        uncertainty = _clamp01(zone.uncertainty)
    else:
        # Uncertainty increases with stale readings and sensor noise intensity.
        noise = config.sensor_noise
        uncertainty = _clamp01(
            zone.uncertainty
            + noise.staleness_drift * stale_days
            + noise.gaussian_std * 0.5
            + noise.missing_probability * 0.2
        )

    return ZoneObservation(
        zone_id=zone.zone_id,
        observed_metrics=observed_metrics,
        crop_health=_clamp01(zone.crop_health),
        crop_stage=_clamp01(zone.crop_stage),
        uncertainty=uncertainty,
        stale_days=stale_days,
    )
