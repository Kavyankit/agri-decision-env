# File: env/environment.py
import random

from models.action_models import Action, ActionType
from models.config_models import EnvConfig
from models.observation_models import Observation
from env.action_validator import validate_action
from env.constants import ACTION_BUDGET_COST, ACTION_TIME_COST_HOURS, TRAVEL_TIME_PER_ZONE_HOURS
from env.state_engine import build_observation, evolve_zones, initialize_zones
from env.transition_engine import apply_action_effects
from env.weather_engine import apply_weather_effects, build_forecast, generate_weather_sequence


class AgriEnv:
    def __init__(self, config: EnvConfig) -> None:
        """Initialize a runnable environment instance for one task preset."""
        self.config = config
        self.day = 0
        self.done = False
        self.zones = []
        self.remaining_budget = config.task.initial_budget
        self.remaining_time_budget = config.task.daily_time_budget
        # Lightweight per-step trace for debugging and later grading integration.
        self.history: list[dict] = []
        # Phase 5 sensor state: deterministic RNG + staleness per zone.
        # `_rng` keeps randomness reproducible when a seed is provided.
        self._rng = random.Random(config.seed)
        # Stores "days since last reading" for each zone_id.
        self._stale_days_by_zone: dict[int, int] = {}
        # Phase 6 weather sequence (generated at reset).
        self._weather_days = []

    def reset(self) -> Observation:
        """Start a new episode and return the initial agent observation."""
        # Reset episode counters/resources and rebuild initial hidden state.
        self.day = 0
        self.done = False
        self.zones = initialize_zones(self.config)
        self.remaining_budget = self.config.task.initial_budget
        self.remaining_time_budget = self.config.task.daily_time_budget
        self.history = []
        # Re-seed RNG at reset so episodes are repeatable with same seed.
        self._rng = random.Random(self.config.seed)
        # Generate a deterministic weather timeline per episode.
        self._weather_days = generate_weather_sequence(self.config, self._rng)
        # At episode start, all zones are fresh (stale_days = 0).
        self._stale_days_by_zone = {z.zone_id: 0 for z in self.zones}

        forecast = build_forecast(
            weather_days=self._weather_days,
            day=self.day,
            horizon=self.config.forecast_horizon,
        )

        # Build an observation that includes both:
        # - noisy per-zone readings (sensor model, Phase 5)
        # - a weather forecast (macro context, Phase 6)
        return build_observation(
            day=self.day,
            zones=self.zones,
            remaining_budget=self.remaining_budget,
            remaining_time_budget=self.remaining_time_budget,
            visible_metrics_count=self.config.task.visible_metrics,
            config=self.config,
            stale_days_by_zone=self._stale_days_by_zone,
            rng=self._rng,
            forecast=forecast,
        )

    def step(self, action: Action) -> tuple[Observation, float, bool, dict]:
        """Apply one day of actions and return next observation, reward, done, and info."""
        if self.done:
            raise ValueError("Cannot call step() after episode is done; call reset()")

        validate_action(
            action=action,
            config=self.config,
            day=self.day,
            remaining_budget=self.remaining_budget,
            remaining_time_budget=self.remaining_time_budget,
        )

        spent_budget = 0.0
        spent_time = 0.0
        travel_time = 0.0
        # Current simple rule: first task has no travel cost ("start already on first zone").
        # Future extension could use a configurable depot/base zone.
        last_zone_id: int | None = None
        for task in action.tasks:
            action_key = task.action_type.value
            # If explicit cost/time are provided, use them; else fall back to constants.
            spent_budget += task.cost if task.cost > 0 else ACTION_BUDGET_COST.get(action_key, 0.0)
            spent_time += task.duration_hours if task.duration_hours > 0 else ACTION_TIME_COST_HOURS.get(action_key, 0.0)

            # Phase 7 travel realism:
            # moving between zones consumes time, reducing what can be done in one day.
            if self.config.travel_constraints_enabled and task.action_type != ActionType.WAIT:
                # WAIT does not reset movement position; the agent remains at last worked zone.
                if last_zone_id is not None:
                    # `abs(...)` makes travel symmetric in this simple linear layout:
                    # moving 2->5 and 5->2 has the same distance cost.
                    zone_distance = abs(task.zone_id - last_zone_id)
                    travel_time += zone_distance * TRAVEL_TIME_PER_ZONE_HOURS
                last_zone_id = task.zone_id

        # Add travel overhead after summing direct task durations.
        spent_time += travel_time

        if spent_budget > self.remaining_budget:
            raise ValueError("Action exceeds remaining budget")
        if spent_time > self.remaining_time_budget:
            raise ValueError("Action exceeds remaining time budget")

        self.remaining_budget -= spent_budget
        self.remaining_time_budget -= spent_time

        # Step order for Phase 4:
        # 1) apply actions, 2) apply weather effects, 3) advance time/crop stage, 4) apply passive evolution.
        transition_info = apply_action_effects(self.zones, action)

        # Phase 6 weather effects (macro factors impacting moisture and degradation).
        today_weather = self._weather_days[self.day]
        weather_info = apply_weather_effects(self.zones, today_weather)

        # Crop stage still advances each day, with a simple growth multiplier from temperature.
        growth_multiplier = 0.85 + 0.3 * today_weather.temperature
        for zone in self.zones:
            zone.crop_stage = min(1.0, zone.crop_stage + 0.02 * growth_multiplier)

        # Phase 3: purely passive lifecycle evolution (no intervention effects yet).
        evolve_zones(self.zones, self.config)

        # Phase 5 staleness: all zones age by one day; TAKE_READING refreshes selected zones.
        read_zone_ids = {
            t.zone_id for t in action.tasks if t.action_type == ActionType.TAKE_READING
        }
        for zone in self.zones:
            # Cap stale-day accumulation for stability in long episodes.
            next_stale = self._stale_days_by_zone.get(zone.zone_id, 0) + 1
            self._stale_days_by_zone[zone.zone_id] = min(10, next_stale)
        for zone_id in read_zone_ids:
            # Reading a zone refreshes its information immediately.
            self._stale_days_by_zone[zone_id] = 0

        # Temporary placeholder reward (cost-only); full state-aligned reward is added in Phase 8.
        reward = -0.01 * spent_budget
        self.day += 1
        self.done = self.day >= self.config.task.max_days

        if not self.done:
            self.remaining_time_budget = self.config.task.daily_time_budget

        forecast = build_forecast(
            weather_days=self._weather_days,
            day=self.day,
            horizon=self.config.forecast_horizon,
        )

        obs = build_observation(
            day=self.day,
            zones=self.zones,
            remaining_budget=self.remaining_budget,
            remaining_time_budget=self.remaining_time_budget,
            visible_metrics_count=self.config.task.visible_metrics,
            config=self.config,
            stale_days_by_zone=self._stale_days_by_zone,
            rng=self._rng,
            forecast=forecast,
        )
        info = {
            "spent_budget": spent_budget,
            "spent_time": spent_time,
            "travel_time_spent": travel_time,
            "actions_count": len(action.tasks),
            "phase": "phase_7_constraints",
            "zones_refreshed": len(read_zone_ids),
            "weather": {
                "rain_probability": weather_info["rain_probability"],
                "temperature": weather_info["temperature"],
                "stress_applied_total": weather_info["stress_applied_total"],
            },
            **transition_info,
        }
        self.history.append({"day": self.day, **info})
        return obs, reward, self.done, info

    def state(self) -> dict:
        """Return debug-friendly internal environment state for inspection/testing."""
        # Debug-focused internal state snapshot.
        return {
            "day": self.day,
            "done": self.done,
            "remaining_budget": self.remaining_budget,
            "remaining_time_budget": self.remaining_time_budget,
            "zone_count": len(self.zones),
            "history_length": len(self.history),
            "travel_constraints_enabled": self.config.travel_constraints_enabled,
            "avg_stale_days": (
                sum(self._stale_days_by_zone.values()) / max(1, len(self._stale_days_by_zone))
            ),
        }
