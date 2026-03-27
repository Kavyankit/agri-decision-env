# File: env/action_validator.py
from models.action_models import Action
from models.config_models import EnvConfig


def validate_action(action: Action, config: EnvConfig, day: int, remaining_budget: float, remaining_time_budget: float) -> None:
    """Validate high-level action plan constraints for the current step."""
    # Phase-2/7 validation focuses on structural guardrails:
    # - count limits
    # - zone-id validity
    # - observation-operation caps
    # Full time feasibility (including travel overhead) is checked in environment.step(),
    # where task order and movement path are available.
    if len(action.tasks) > config.task.max_actions_per_day:
        raise ValueError("Too many actions for current day")

    if day >= config.task.max_days:
        raise ValueError("Episode already exceeded configured horizon")

    if remaining_budget < 0 or remaining_time_budget < 0:
        raise ValueError("Invalid negative budget/time state")

    zone_count = config.task.zone_count
    for task in action.tasks:
        if task.zone_id < 0 or task.zone_id >= zone_count:
            raise ValueError("Invalid zone_id")

    # Phase 7: enforce sensing-operation limits to model real daily operations.
    # We count unique zones targeted by TAKE_READING on this day.
    if config.max_zones_observable_per_day is not None:
        # Set() ensures repeated readings of the same zone count only once.
        observed_zones = {
            task.zone_id
            for task in action.tasks
            if task.action_type.value == "take_reading"
        }
        if len(observed_zones) > config.max_zones_observable_per_day:
            raise ValueError("Too many zones observed in one day")
