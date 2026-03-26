# File: models/reward_models.py
from pydantic import BaseModel


class RewardBreakdown(BaseModel):
    """Interpretable decomposition of a single step reward."""
    # Engine-computed total reward for the step.
    total: float
    # Interpretable components for debugging and grader alignment checks.
    # Change in expected yield this step.
    yield_delta: float = 0.0
    # Reward for efficient use of limited actions/time/budget.
    efficiency_bonus: float = 0.0
    # Bonus when strategic sacrifice decisions are judged correct.
    correct_sacrifice_bonus: float = 0.0
    # Penalty for expensive interventions.
    cost_penalty: float = 0.0
    # Penalty for excessive or repeated interventions.
    overuse_penalty: float = 0.0
    # Penalty for low-value or unnecessary actions.
    waste_penalty: float = 0.0
