# Judging Alignment

This document explains how the Geo-Agricultural Decision Environment aligns with each evaluation criterion.

## 1. Real-world Utility (30%)

### What the criterion expects
A genuine, practical task with clear real-world relevance for agent evaluation.

### How this project satisfies it
- Models agricultural field decision-making under real operational constraints.
- Requires trade-offs across yield, cost, time, and soil health.
- Uses multi-zone spatial planning and weather-aware interventions.
- Reflects uncertainty and delayed consequences common in real farm operations.

### Evidence in project design
- Geolocated zones and travel-time constraints.
- Limited budget and daily executor time.
- Partial observability with active sensing requirements.

---

## 2. Task and Grader Quality (25%)

### What the criterion expects
Well-defined tasks, meaningful progression, and accurate deterministic graders.

### How this project satisfies it
- Defines three task levels:
  - Easy: diagnosis and understanding
  - Medium: constrained allocation
  - Hard: strategic sacrifice under irreversible pressure
- Uses task-specific graders with shared score components.
- Returns scalar score in `[0,1]`, with optional subscores and explanation.
- Maintains deterministic behavior with fixed environment/task/weather/sensor seeds.

### Evidence in project design
- Difficulty-specific horizons and zone counts.
- Explicit grading dimensions: yield, efficiency, sustainability, prioritization.
- Opportunity-dependent sacrifice logic in hard scenarios.

---

## 3. Environment Design (20%)

### What the criterion expects
Clean state management, sensible interfaces, informative reward shaping, and proper episode boundaries.

### How this project satisfies it
- Separates hidden ground-truth state from observable agent state.
- Uses structured action and observation models with explicit constraints.
- Includes dense reward components for progress plus penalties for undesirable actions.
- Applies clear termination conditions tied to horizon and viability.
- Keeps weather coherent per episode with a forward forecast window for planning.

### Evidence in project design
- `reset()`, `step(action)`, `state()` interface.
- Sensor model with bias, noise, drift, missing values, and outliers.
- Lifecycle and strategic class modeling for long-horizon planning.

---

## 4. Code Quality and Spec Compliance (15%)

### What the criterion expects
OpenEnv compatibility, typed contracts, clean project structure, reproducibility, and deployment reliability.

### How this project satisfies it
- Implements typed `Observation`, `Action`, and reward/grader models.
- Uses modular architecture (`env`, `models`, `grader`, `baseline`, `api`, `config`, `tasks`).
- Defines required API endpoints: `/tasks`, `/grader`, `/baseline`.
- Uses `openenv.yaml`, Docker packaging, and pre-submission validation script.
- Includes a deterministic heuristic baseline and optional LLM baseline extension.

### Evidence in project design
- Config-driven presets and reward weights.
- Submission checks for env execution, grader output range, endpoint health, and baseline run.

---

## 5. Creativity and Novelty (10%)

### What the criterion expects
Original mechanics, non-trivial reasoning pressure, and compelling benchmark behavior.

### How this project satisfies it
- Introduces strategic sacrifice as a first-class evaluation behavior.
- Uses reversible lifecycle transitions with hysteresis (recovery harder than degradation).
- Encodes uncertain sensing and delayed intervention impacts.
- Evaluates prioritization quality, not just local optimization.

### Evidence in project design
- Internal strategic classes: `RECOVERABLE`, `SALVAGEABLE`, `NOT_WORTH_SAVING`.
- Correct-sacrifice reward and grader components.
- Hard-task episodes that sometimes require sacrifice and sometimes do not.

---

## Summary

The project is aligned with all rubric categories through:
- practical domain grounding,
- deterministic multi-level evaluation,
- robust simulation mechanics,
- spec-compliant architecture and deployment readiness,
- and original decision-intelligence dynamics suited for agent benchmarking.

