# File: grader/medium_grader.py
from __future__ import annotations

from grader.base_grader import BaseGrader


class MediumGrader(BaseGrader):
    """
    Medium-task grader.

    Medium mode balances outcome and sustainability while keeping
    efficiency important under moderate constraints.
    """

    COMPONENT_WEIGHTS = {
        "outcome": 0.35,
        "efficiency": 0.25,
        "sustainability": 0.25,
        "discipline": 0.15,
    }

