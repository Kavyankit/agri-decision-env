# File: env/weather_engine.py
from __future__ import annotations

from dataclasses import dataclass

from models.config_models import Difficulty, EnvConfig
from models.observation_models import ForecastDay
from models.zone_models import ZoneState


@dataclass(frozen=True)
class WeatherDay:
    """Macro weather for a single simulation day.

    temperature and rain_probability are normalized to [0, 1] to keep
    downstream math stable.
    """

    rain_probability: float
    temperature: float


def _clamp01(value: float) -> float:
    """Clamp a float to [0, 1]."""
    return max(0.0, min(1.0, value))


def choose_weather_scenario(config: EnvConfig) -> str:
    """Pick a simple episode-level weather scenario (deterministic by seed)."""
    difficulty = config.task.difficulty
    # Keep scenario selection deterministic by difficulty in Phase 6.
    # Future extension: use RNG to sample scenarios per episode.
    if difficulty == Difficulty.EASY:
        return "mild_wet"
    if difficulty == Difficulty.MEDIUM:
        return "mixed"
    return "dry_hot"


def generate_weather_sequence(config: EnvConfig, rng) -> list[WeatherDay]:
    """Generate deterministic daily weather for the full episode."""
    max_days = config.task.max_days
    horizon = config.forecast_horizon
    total_days = max_days + horizon + 2

    scenario = choose_weather_scenario(config)

    # Scenario parameters (all in normalized [0, 1] space).
    if scenario == "mild_wet":
        rain_base, rain_var = 0.6, 0.15
        temp_base, temp_var = 0.45, 0.12
    elif scenario == "mixed":
        rain_base, rain_var = 0.45, 0.2
        temp_base, temp_var = 0.55, 0.18
    else:  # "dry_hot"
        rain_base, rain_var = 0.25, 0.18
        temp_base, temp_var = 0.7, 0.18

    days: list[WeatherDay] = []
    for _ in range(total_days):
        rain = _clamp01(rain_base + rng.gauss(0.0, rain_var))
        temp = _clamp01(temp_base + rng.gauss(0.0, temp_var))
        days.append(WeatherDay(rain_probability=rain, temperature=temp))
    return days


def apply_weather_effects(zones: list[ZoneState], weather: WeatherDay) -> dict:
    """Apply weather impact to hidden state (Phase 6 macro factors).

    This is intentionally simple:
    - rain increases soil moisture
    - heat/drought increase degradation
    - existing soil moisture mitigates degradation from stress
    """

    # Base rain contribution before per-zone saturation adjustment.
    rain_moisture_boost = 0.03 * weather.rain_probability
    heat_stress = max(0.0, weather.temperature - 0.5)
    drought_stress = 1.0 - weather.rain_probability
    baseline_stress = 0.015 * heat_stress + 0.01 * drought_stress

    stress_applied = 0.0
    for zone in zones:
        # Keep metric handling strict for consistency with earlier phases.
        if "soil_moisture" not in zone.true_metrics:
            raise ValueError(f"Missing required metric 'soil_moisture' for zone {zone.zone_id}")

        # Rain boosts moisture, but saturated soil gets less extra benefit.
        # At 0 moisture -> full benefit; near 1 moisture -> strong diminishing return.
        current_moisture = zone.true_metrics["soil_moisture"]
        saturation_factor = max(0.1, 1.0 - current_moisture)
        zone.true_metrics["soil_moisture"] = _clamp01(
            current_moisture + rain_moisture_boost * saturation_factor
        )

        # More moisture means less degradation from the same weather.
        soil_moisture = zone.true_metrics["soil_moisture"]
        # mitigation is higher when soil_moisture is high.
        mitigation = 0.35 + 0.65 * soil_moisture  # [0.35..1.0]
        degradation_delta = baseline_stress * (1.0 - mitigation * 0.7)

        zone.degradation_level = _clamp01(zone.degradation_level + degradation_delta)
        stress_applied += degradation_delta

    return {
        "rain_probability": weather.rain_probability,
        "temperature": weather.temperature,
        "stress_applied_total": stress_applied,
    }


def build_forecast(weather_days: list[WeatherDay], day: int, horizon: int) -> list[ForecastDay]:
    """Build a forecast list for the agent."""
    if horizon <= 0:
        return []
    slice_ = weather_days[day : day + horizon]
    return [ForecastDay(rain_probability=w.rain_probability, temperature=w.temperature) for w in slice_]

