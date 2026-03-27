# File: env/transition_engine.py
from __future__ import annotations

from collections import defaultdict

from models.action_models import Action, ActionType, TaskAction
from models.zone_models import ZoneState


def _clamp01(value: float) -> float:
    """Clamp a float to the [0, 1] range."""
    return max(0.0, min(1.0, value))


def _metric_add(zone: ZoneState, metric: str, delta: float) -> None:
    """Add delta to a hidden metric while preserving [0, 1] bounds."""
    if metric not in zone.true_metrics:
        raise ValueError(f"Unknown metric: {metric}")
    current = zone.true_metrics[metric]
    zone.true_metrics[metric] = _clamp01(current + delta)


def _apply_irrigation(zone: ZoneState, task: TaskAction, scale: float) -> float:
    """Apply irrigation effects and return degradation recovery amount."""
    amount = max(0.0, task.amount)
    if amount == 0.0:
        return 0.0
    moisture_boost = 0.06 * amount * scale
    _metric_add(zone, "soil_moisture", moisture_boost)

    # Irrigation modestly reduces near-term degradation if not overused.
    return 0.02 * amount * scale


def _apply_input(zone: ZoneState, task: TaskAction, scale: float) -> float:
    """Apply nutrient/input effects and return degradation recovery amount."""
    amount = max(0.0, task.amount)
    if amount == 0.0:
        return 0.0
    input_type = (task.input_type or "mixed").strip().lower()

    nutrient_boost = 0.07 * amount * scale
    if input_type in {"nitrogen", "n"}:
        _metric_add(zone, "nitrogen", nutrient_boost)
    elif input_type in {"phosphorus", "p"}:
        _metric_add(zone, "phosphorus", nutrient_boost)
    elif input_type in {"potassium", "k"}:
        _metric_add(zone, "potassium", nutrient_boost)
    elif input_type == "organic":
        _metric_add(zone, "organic_matter", 0.08 * amount * scale)
        _metric_add(zone, "nitrogen", 0.02 * amount * scale)
        _metric_add(zone, "phosphorus", 0.02 * amount * scale)
        _metric_add(zone, "potassium", 0.02 * amount * scale)
    else:
        # Default "mixed" input if type is missing or unknown.
        _metric_add(zone, "nitrogen", 0.03 * amount * scale)
        _metric_add(zone, "phosphorus", 0.03 * amount * scale)
        _metric_add(zone, "potassium", 0.03 * amount * scale)

    return 0.015 * amount * scale


def _apply_take_reading(zone: ZoneState, scale: float) -> None:
    """Reading action reduces uncertainty slightly for the zone."""
    zone.uncertainty = _clamp01(zone.uncertainty - 0.04 * scale)


def apply_action_effects(zones: list[ZoneState], action: Action) -> dict:
    """Apply deterministic Phase-4 action effects to hidden zone state."""
    zone_by_id = {z.zone_id: z for z in zones}
    action_counts: dict[tuple[int, ActionType], int] = defaultdict(int)
    interventions_by_zone: dict[int, int] = defaultdict(int)
    recovery_by_zone: dict[int, float] = defaultdict(float)

    total_recovery = 0.0
    total_overuse_penalty = 0.0
    task_effects: list[dict] = []

    for task in action.tasks:
        zone = zone_by_id.get(task.zone_id)
        if zone is None:
            raise ValueError(f"Invalid zone_id: {task.zone_id}")

        action_counts[(task.zone_id, task.action_type)] += 1
        repeats = action_counts[(task.zone_id, task.action_type)] - 1
        # Diminishing returns: repeated same action on same zone has lower impact.
        scale = max(0.2, 1.0 / (1.0 + 0.5 * repeats))

        if task.action_type == ActionType.IRRIGATE:
            interventions_by_zone[task.zone_id] += 1
            recovery = _apply_irrigation(zone, task, scale)
            recovery_by_zone[task.zone_id] += recovery
            total_recovery += recovery
        elif task.action_type == ActionType.APPLY_INPUT:
            interventions_by_zone[task.zone_id] += 1
            recovery = _apply_input(zone, task, scale)
            recovery_by_zone[task.zone_id] += recovery
            total_recovery += recovery
        elif task.action_type == ActionType.TAKE_READING:
            _apply_take_reading(zone, scale)
        elif task.action_type == ActionType.WAIT:
            # WAIT intentionally has no direct hidden-state intervention effect.
            continue

        task_effects.append(
            {
                "zone_id": task.zone_id,
                "action_type": task.action_type.value,
                "scale": scale,
                "recovery": recovery if task.action_type in {ActionType.IRRIGATE, ActionType.APPLY_INPUT} else 0.0,
            }
        )

    # Overuse consequence: too many interventions in one zone/day increases degradation.
    for zone_id, count in interventions_by_zone.items():
        if count <= 2:
            continue
        zone = zone_by_id[zone_id]
        extra = count - 2
        penalty = 0.01 * (extra**1.5)
        zone.degradation_level = _clamp01(zone.degradation_level + penalty)
        total_overuse_penalty += penalty

    # Apply recovery where it was earned, per zone.
    for zone_id, recovery in recovery_by_zone.items():
        zone = zone_by_id[zone_id]
        zone.degradation_level = _clamp01(zone.degradation_level - recovery)

    return {
        "recovery_applied": total_recovery,
        "overuse_penalty_applied": total_overuse_penalty,
        "interventions_zones": len(interventions_by_zone),
        "task_effects": task_effects,
    }
