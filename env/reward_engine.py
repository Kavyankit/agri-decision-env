# File: env/reward_engine.py
from __future__ import annotations

from models.action_models import Action, ActionType
from models.config_models import EnvConfig
from models.reward_models import RewardBreakdown


def _count_waste_actions(action: Action) -> int:
    """
    Count actions that are likely "wasted" for this step.

    Here we treat IRRIGATE / APPLY_INPUT with amount <= 0 as wasteful:
    the agent spent time/budget on an intervention that does not actually
    change hidden state in a meaningful way.
    """
    wasted = 0
    for task in action.tasks:
        if task.action_type in {ActionType.IRRIGATE, ActionType.APPLY_INPUT} and task.amount <= 0.0:
            wasted += 1
    return wasted


def compute_reward(
    *,
    action: Action,
    config: EnvConfig,
    spent_budget: float,
    spent_time: float,
    yield_before_total: float,
    yield_after_total: float,
    overuse_penalty_applied: float,
    not_worth_saved_zone_ids_before: set[int],
) -> RewardBreakdown:
    """
    Compute dense, interpretable per-step reward (Phase 8).

    The reward is a weighted combination of:
    - yield_delta:    change in a simple yield proxy (`crop_health * crop_stage`)
    - efficiency:     how much yield improved per unit cost/time
    - sacrifice:      whether we avoided wasting inputs on NOT_WORTH_SAVING zones
    - cost_penalty:   cost relative to the starting episode budget
    - overuse_penalty and waste_penalty: punish over-intervention and no-op actions
    """

    zone_count = max(1, config.task.zone_count)
    weights = config.reward_weights

    # Normalize by zone_count so reward magnitude is comparable across presets
    # (otherwise harder tasks with more zones would naturally have larger signals).
    yield_delta_raw_total = yield_after_total - yield_before_total
    yield_delta_raw = yield_delta_raw_total / zone_count
    # Encourages improvements; still allows negative reinforcement if things get worse.
    yield_delta = weights.yield_weight * yield_delta_raw

    # Efficiency: only reward positive improvements, normalized by how much we spent.
    # This keeps the signal stable even when agents waste actions with no net benefit.
    denom = 1.0 + spent_budget + spent_time
    efficiency_bonus_raw = 0.0
    if yield_delta_raw > 0.0:
        efficiency_bonus_raw = yield_delta_raw / denom
    efficiency_bonus = weights.efficiency_weight * efficiency_bonus_raw

    # Correct sacrifice: if we avoid intervening NOT_WORTH_SAVING zones, we get a small bonus.
    intervention_not_saved = 0
    if not_worth_saved_zone_ids_before:
        acted_on_not_saved: set[int] = set()
        for task in action.tasks:
            if (
                task.action_type in {ActionType.IRRIGATE, ActionType.APPLY_INPUT}
                and task.amount > 0.0
            ):
                acted_on_not_saved.add(task.zone_id)
        intervention_not_saved = len(acted_on_not_saved & not_worth_saved_zone_ids_before)

        sacrifice_ratio = 1.0 - (intervention_not_saved / max(1, len(not_worth_saved_zone_ids_before)))
        # Shift ratio so "about half" becomes near zero reward.
        sacrifice_centered = sacrifice_ratio - 0.5  # range [-0.5, 0.5]
        correct_sacrifice_bonus = weights.sacrifice_weight * sacrifice_centered * 0.1
    else:
        correct_sacrifice_bonus = 0.0

    # Cost scales reward by how much of the starting budget we consumed.
    cost_penalty = -weights.cost_penalty_weight * (spent_budget / max(1.0, config.task.initial_budget))

    # Overuse penalty is already aggregated by transition_engine into a positive scalar.
    overuse_penalty = -weights.overuse_penalty_weight * float(overuse_penalty_applied)

    waste_actions = _count_waste_actions(action)
    # Normalise by number of tasks so this stays comparable across different action sizes.
    waste_penalty = -weights.waste_penalty_weight * (waste_actions / max(1, len(action.tasks))) * 0.1

    total = (
        yield_delta
        + efficiency_bonus
        + correct_sacrifice_bonus
        + cost_penalty
        + overuse_penalty
        + waste_penalty
    )

    return RewardBreakdown(
        total=total,
        yield_delta=yield_delta,
        efficiency_bonus=efficiency_bonus,
        correct_sacrifice_bonus=correct_sacrifice_bonus,
        cost_penalty=cost_penalty,
        overuse_penalty=overuse_penalty,
        waste_penalty=waste_penalty,
    )

