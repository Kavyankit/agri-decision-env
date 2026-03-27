# File: baseline/heuristic_agent.py
from __future__ import annotations

from env.constants import ACTION_BUDGET_COST, ACTION_TIME_COST_HOURS, TRAVEL_TIME_PER_ZONE_HOURS
from models import Action, ActionType, Observation, TaskAction

# Heuristic tuning knobs (kept local for clarity in Phase 11).
HEALTH_PRIORITY_WEIGHT = 0.6
UNCERTAINTY_PRIORITY_WEIGHT = 0.25
STALENESS_PRIORITY_WEIGHT = 0.15

READING_UNCERTAINTY_THRESHOLD = 0.45
READING_STALENESS_THRESHOLD = 3
IRRIGATION_MOISTURE_THRESHOLD = 0.45
NUTRIENT_INPUT_THRESHOLD = 0.40
SECONDARY_READING_UNCERTAINTY_THRESHOLD = 0.30


class HeuristicAgent:
    """
    Simple deterministic baseline policy.

    Policy idea (kept intentionally transparent):
    - Rank zones by urgency (low crop health, high uncertainty, high staleness).
    - For high uncertainty/staleness: prefer TAKE_READING.
    - For low moisture: prefer IRRIGATE.
    - For weak nutrient signals: prefer APPLY_INPUT (mixed input).
    - Respect per-step budget/time by estimating action + travel cost before adding tasks.
    """

    def __init__(self) -> None:
        self._last_zone_id: int | None = None

    def reset(self) -> None:
        """Reset per-episode internal memory."""
        self._last_zone_id = None

    @staticmethod
    def _zone_priority(zone_obs) -> float:
        """Higher score means higher urgency."""
        health = float(zone_obs.crop_health if zone_obs.crop_health is not None else 0.5)
        uncertainty = float(zone_obs.uncertainty)
        staleness = float(zone_obs.stale_days)
        # Low health should increase priority, so we use (1 - health).
        return (
            (1.0 - health) * HEALTH_PRIORITY_WEIGHT
            + uncertainty * UNCERTAINTY_PRIORITY_WEIGHT
            + min(1.0, staleness / 10.0) * STALENESS_PRIORITY_WEIGHT
        )

    @staticmethod
    def _estimate_task_budget(action_type: ActionType) -> float:
        """Estimate budget using same fallback table as environment."""
        return float(ACTION_BUDGET_COST.get(action_type.value, 0.0))

    @staticmethod
    def _estimate_task_time(action_type: ActionType) -> float:
        """Estimate operation time using same fallback table as environment."""
        return float(ACTION_TIME_COST_HOURS.get(action_type.value, 0.0))

    def _estimate_travel_time(self, from_zone: int | None, to_zone: int) -> float:
        """
        Estimate travel time under the current simple linear-zone model.

        First move has zero travel, matching environment behavior.
        """
        if from_zone is None:
            return 0.0
        return abs(to_zone - from_zone) * TRAVEL_TIME_PER_ZONE_HOURS

    def _decide_candidate(self, zone_obs) -> TaskAction:
        """Pick one candidate task for a zone using simple threshold rules."""
        metrics = zone_obs.observed_metrics
        soil_moisture = metrics.get("soil_moisture")
        nitrogen = metrics.get("nitrogen")
        phosphorus = metrics.get("phosphorus")
        potassium = metrics.get("potassium")

        # If information quality is poor, refresh observation first.
        if (
            zone_obs.uncertainty > READING_UNCERTAINTY_THRESHOLD
            or zone_obs.stale_days >= READING_STALENESS_THRESHOLD
        ):
            return TaskAction(zone_id=zone_obs.zone_id, action_type=ActionType.TAKE_READING)

        # Moisture stress handling.
        if soil_moisture is not None and soil_moisture < IRRIGATION_MOISTURE_THRESHOLD:
            return TaskAction(
                zone_id=zone_obs.zone_id,
                action_type=ActionType.IRRIGATE,
                amount=1.0,
            )

        # Nutrient stress handling (when any visible core nutrient is low).
        nutrient_values = [v for v in [nitrogen, phosphorus, potassium] if v is not None]
        if nutrient_values and min(nutrient_values) < NUTRIENT_INPUT_THRESHOLD:
            return TaskAction(
                zone_id=zone_obs.zone_id,
                action_type=ActionType.APPLY_INPUT,
                input_type="mixed",
                amount=1.0,
            )

        # Default to observation refresh for uncertain conditions, else wait.
        if zone_obs.uncertainty > SECONDARY_READING_UNCERTAINTY_THRESHOLD:
            return TaskAction(zone_id=zone_obs.zone_id, action_type=ActionType.TAKE_READING)
        return TaskAction(zone_id=zone_obs.zone_id, action_type=ActionType.WAIT)

    def act(self, observation: Observation, max_actions_per_day: int) -> Action:
        """Build one deterministic action plan for the current observation."""
        # Rank zones from most urgent to least urgent.
        # Python sorting is stable, so equal-priority zones keep input order.
        ranked_zones = sorted(
            observation.zones,
            key=self._zone_priority,
            reverse=True,
        )

        planned: list[TaskAction] = []
        remaining_budget = float(observation.remaining_budget)
        remaining_time = float(observation.remaining_time_budget)
        moving_from = self._last_zone_id

        for zone_obs in ranked_zones:
            if len(planned) >= max_actions_per_day:
                break

            candidate = self._decide_candidate(zone_obs)
            if candidate.action_type == ActionType.WAIT:
                continue

            est_budget = self._estimate_task_budget(candidate.action_type)
            est_time = self._estimate_task_time(candidate.action_type)
            est_travel = self._estimate_travel_time(moving_from, candidate.zone_id)
            total_est_time = est_time + est_travel

            # Only include task if we can still afford it under current observation budgets.
            if est_budget <= remaining_budget and total_est_time <= remaining_time:
                planned.append(candidate)
                remaining_budget -= est_budget
                remaining_time -= total_est_time
                moving_from = candidate.zone_id

        # Persist end position to keep movement coherent across days.
        self._last_zone_id = moving_from
        return Action(tasks=planned)

