# File: grader/scoring_utils.py
from __future__ import annotations


def clamp01(value: float) -> float:
    """Clamp a numeric value to the closed [0, 1] interval."""
    return max(0.0, min(1.0, float(value)))


def safe_ratio(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Return numerator / denominator safely.

    If denominator is zero (or very close to zero), return `default` so the
    grader remains deterministic and stable.
    """
    if abs(float(denominator)) < 1e-12:
        return float(default)
    return float(numerator) / float(denominator)


def weighted_average(subscores: dict[str, float], weights: dict[str, float]) -> float:
    """
    Compute a deterministic weighted average in [0, 1].

    - Subscores are first clamped to [0, 1].
    - Negative weights are treated as zero to avoid accidental inversions.
    - If total weight is zero, return 0.0.
    """
    weighted_sum = 0.0
    weight_total = 0.0
    for key, raw_weight in weights.items():
        w = max(0.0, float(raw_weight))
        s = clamp01(subscores.get(key, 0.0))
        weighted_sum += w * s
        weight_total += w
    return clamp01(safe_ratio(weighted_sum, weight_total, default=0.0))


def build_short_explanation(score: float, subscores: dict[str, float]) -> str:
    """
    Create a short human-readable explanation from top and bottom subscores.

    This keeps grader outputs interpretable for debugging and leaderboard review.
    """
    if not subscores:
        return f"Score {score:.3f}. No subscores available."

    # Pick strongest and weakest signal for a compact explanation.
    # This keeps output short while still showing one positive and one weak area.
    ordered = sorted(subscores.items(), key=lambda item: item[1], reverse=True)
    best_name, best_value = ordered[0]
    worst_name, worst_value = ordered[-1]
    return (
        f"Score {score:.3f}. "
        f"Strongest area: {best_name} ({best_value:.2f}); "
        f"weakest area: {worst_name} ({worst_value:.2f})."
    )

