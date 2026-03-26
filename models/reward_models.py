# File: models/reward_models.py
from pydantic import BaseModel


class RewardBreakdown(BaseModel):
    # Engine-computed total reward for the step.
    total: float
    # Interpretable components for debugging and grader alignment checks.
    yield_delta: float = 0.0
    efficiency_bonus: float = 0.0
    correct_sacrifice_bonus: float = 0.0
    cost_penalty: float = 0.0
    overuse_penalty: float = 0.0
    waste_penalty: float = 0.0
