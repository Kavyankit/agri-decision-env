# File: env/environment.py
from models.action_models import Action
from models.config_models import EnvConfig
from models.observation_models import Observation
from env.action_validator import validate_action
from env.constants import ACTION_BUDGET_COST, ACTION_TIME_COST_HOURS
from env.state_engine import build_observation, evolve_zones, initialize_zones
from env.transition_engine import apply_action_effects


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

    def reset(self) -> Observation:
        """Start a new episode and return the initial agent observation."""
        # Reset episode counters/resources and rebuild initial hidden state.
        self.day = 0
        self.done = False
        self.zones = initialize_zones(self.config)
        self.remaining_budget = self.config.task.initial_budget
        self.remaining_time_budget = self.config.task.daily_time_budget
        self.history = []
        return build_observation(
            day=self.day,
            zones=self.zones,
            remaining_budget=self.remaining_budget,
            remaining_time_budget=self.remaining_time_budget,
            visible_metrics_count=self.config.task.visible_metrics,
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
        for task in action.tasks:
            action_key = task.action_type.value
            # If explicit cost/time are provided, use them; else fall back to constants.
            spent_budget += task.cost if task.cost > 0 else ACTION_BUDGET_COST.get(action_key, 0.0)
            spent_time += task.duration_hours if task.duration_hours > 0 else ACTION_TIME_COST_HOURS.get(action_key, 0.0)

        if spent_budget > self.remaining_budget:
            raise ValueError("Action exceeds remaining budget")
        if spent_time > self.remaining_time_budget:
            raise ValueError("Action exceeds remaining time budget")

        self.remaining_budget -= spent_budget
        self.remaining_time_budget -= spent_time

        # Step order for Phase 4:
        # 1) apply actions to hidden state, 2) advance time/crop stage, 3) apply passive evolution.
        transition_info = apply_action_effects(self.zones, action)

        # Crop stage still advances passively each day.
        for zone in self.zones:
            zone.crop_stage = min(1.0, zone.crop_stage + 0.02)

        # Phase 3: purely passive lifecycle evolution (no intervention effects yet).
        evolve_zones(self.zones, self.config)

        # Temporary placeholder reward (cost-only); full state-aligned reward is added in Phase 8.
        reward = -0.01 * spent_budget
        self.day += 1
        self.done = self.day >= self.config.task.max_days

        if not self.done:
            self.remaining_time_budget = self.config.task.daily_time_budget

        obs = build_observation(
            day=self.day,
            zones=self.zones,
            remaining_budget=self.remaining_budget,
            remaining_time_budget=self.remaining_time_budget,
            visible_metrics_count=self.config.task.visible_metrics,
        )
        info = {
            "spent_budget": spent_budget,
            "spent_time": spent_time,
            "actions_count": len(action.tasks),
            "phase": "phase_4_transition_logic",
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
        }
