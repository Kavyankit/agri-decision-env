# File: grader/base_grader.py
from __future__ import annotations

from dataclasses import dataclass

from grader.scoring_utils import build_short_explanation, clamp01, safe_ratio, weighted_average

# Phase 10 normalization constants.
# Keeping them named avoids "magic numbers" and makes later tuning easier.
REWARD_SCALE = 10.0
REWARD_PER_DAY_SCALE = 2.0


@dataclass(frozen=True)
class GradeResult:
    """Structured deterministic grading output."""
    score: float
    subscores: dict[str, float]
    explanation: str


class BaseGrader:
    """
    Deterministic base grader for episode summaries.

    Expected `episode_summary` keys (all optional; safe defaults are applied):
    - total_reward: float
    - max_days: int
    - days_elapsed: int
    - initial_budget: float
    - remaining_budget: float
    - overuse_penalty_total: float
    - waste_actions: int
    - total_actions: int
    - final_avg_degradation: float in [0, 1]
    - final_avg_crop_health: float in [0, 1]
    """

    # Default component weights. Child graders override for task-specific emphasis.
    COMPONENT_WEIGHTS = {
        "outcome": 0.35,
        "efficiency": 0.25,
        "sustainability": 0.25,
        "discipline": 0.15,
    }

    def _compute_subscores(self, episode_summary: dict) -> dict[str, float]:
        """Convert an episode summary into normalized subscores."""
        total_reward = float(episode_summary.get("total_reward", 0.0))
        max_days = max(1.0, float(episode_summary.get("max_days", 1)))
        days_elapsed = max(0.0, float(episode_summary.get("days_elapsed", max_days)))

        initial_budget = max(1e-9, float(episode_summary.get("initial_budget", 1.0)))
        remaining_budget = max(0.0, float(episode_summary.get("remaining_budget", 0.0)))
        overuse_penalty_total = max(0.0, float(episode_summary.get("overuse_penalty_total", 0.0)))

        waste_actions = max(0.0, float(episode_summary.get("waste_actions", 0.0)))
        total_actions = max(1.0, float(episode_summary.get("total_actions", 1.0)))

        final_avg_degradation = clamp01(float(episode_summary.get("final_avg_degradation", 0.5)))
        final_avg_crop_health = clamp01(float(episode_summary.get("final_avg_crop_health", 0.5)))

        # Outcome: reward transformed into [0,1] with a smooth bounded mapping.
        # This avoids brittle hard thresholds in early-stage environment versions.
        outcome = clamp01(
            0.5 + 0.5 * safe_ratio(total_reward, abs(total_reward) + REWARD_SCALE, default=0.0)
        )

        # Efficiency: reward per day plus budget preservation.
        reward_per_day = safe_ratio(total_reward, days_elapsed, default=0.0)
        reward_eff = clamp01(
            0.5
            + 0.5 * safe_ratio(reward_per_day, abs(reward_per_day) + REWARD_PER_DAY_SCALE, default=0.0)
        )
        budget_eff = clamp01(safe_ratio(remaining_budget, initial_budget, default=0.0))
        efficiency = clamp01(0.6 * reward_eff + 0.4 * budget_eff)

        # Sustainability: high crop health and low degradation score well.
        sustainability = clamp01(0.55 * final_avg_crop_health + 0.45 * (1.0 - final_avg_degradation))

        # Discipline: penalize overuse and wasteful action selection.
        waste_ratio = clamp01(safe_ratio(waste_actions, total_actions, default=0.0))
        overuse_term = clamp01(1.0 - min(1.0, overuse_penalty_total * 2.0))
        discipline = clamp01(0.5 * (1.0 - waste_ratio) + 0.5 * overuse_term)

        return {
            "outcome": outcome,
            "efficiency": efficiency,
            "sustainability": sustainability,
            "discipline": discipline,
            # Extra transparency subscore (not weighted in Phase 10).
            # It is returned for diagnostics and can be weighted in future phases.
            "horizon_utilization": clamp01(safe_ratio(days_elapsed, max_days, default=0.0)),
        }

    def grade(self, episode_summary: dict) -> GradeResult:
        """Return deterministic score, subscores, and short explanation."""
        subscores = self._compute_subscores(episode_summary)
        score = weighted_average(subscores, self.COMPONENT_WEIGHTS)
        explanation = build_short_explanation(score, subscores)
        return GradeResult(score=score, subscores=subscores, explanation=explanation)

