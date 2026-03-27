# File: grader/grader_factory.py
from __future__ import annotations

from grader.base_grader import BaseGrader
from grader.easy_grader import EasyGrader
from grader.hard_grader import HardGrader
from grader.medium_grader import MediumGrader
from models import Difficulty


def get_grader(task_id_or_difficulty: str) -> BaseGrader:
    """
    Return the deterministic grader for a task identifier.

    Accepted values:
    - "easy", "medium", "hard"
    - Difficulty enum string values
    """

    # Normalize user input so " EASY ", "easy", and Difficulty.EASY all resolve.
    key = str(task_id_or_difficulty).strip().lower()
    if key == Difficulty.EASY.value:
        return EasyGrader()
    if key == Difficulty.MEDIUM.value:
        return MediumGrader()
    if key == Difficulty.HARD.value:
        return HardGrader()
    raise KeyError(f"Unknown grader key: {task_id_or_difficulty!r}")

