# File: env/action_validator.py
from models.action_models import Action
from models.config_models import EnvConfig


def validate_action(action: Action, config: EnvConfig, day: int, remaining_budget: float, remaining_time_budget: float) -> None:
    """Validate high-level action plan constraints for the current step."""
    # Phase-2 validation focuses on shape/episode guardrails; richer feasibility comes later.
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
