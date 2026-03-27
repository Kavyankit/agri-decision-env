# File: env/constants.py
# Baseline hidden-state initialization values for Phase 2.
DEFAULT_METRIC_VALUE = 0.5
DEFAULT_CROP_HEALTH = 0.8
DEFAULT_CROP_STAGE = 0.1

# Fallback per-task time cost (hours) when action omits duration_hours.
ACTION_TIME_COST_HOURS = {
    "take_reading": 0.25,
    "apply_input": 0.5,
    "irrigate": 0.5,
    "wait": 0.0,
}

# Fallback per-task budget cost when action omits explicit cost.
ACTION_BUDGET_COST = {
    "take_reading": 0.5,
    "apply_input": 2.0,
    "irrigate": 1.5,
    "wait": 0.0,
}

# Travel-time model (Phase 7):
# Moving between two zones costs this many hours per zone-index step.
# Example: moving from zone 2 -> zone 5 adds 3 * TRAVEL_TIME_PER_ZONE_HOURS.
TRAVEL_TIME_PER_ZONE_HOURS = 0.2
