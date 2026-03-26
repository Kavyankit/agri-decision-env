# 🌾 Geo-Agricultural Decision Environment (OpenEnv-Compliant)
## Full Design + PRD + HLD (v3 – Submission Ready)

# 1. 🧠 Problem Statement
Design a realistic, deployable AI environment where an agent manages a geolocated agricultural field over time under:
- partial observability
- resource constraints
- uncertainty
- delayed consequences

The agent must:
- interpret soil and environmental signals
- decide when to gather information
- allocate farmer resources
- perform interventions

to optimize:
- crop yield
- cost efficiency
- long-term soil health

# 2. 🎯 Product Goal
Build a deployable OpenEnv benchmark environment that evaluates real-world sequential decision-making under uncertainty.

# 3. 🧠 Core Philosophy
- partial information
- irreversible state transitions
- resource constraints
- tradeoffs over optimal answers
- global optimization > local fairness

# 4. 🧩 System Overview
Agent → API → Environment → State Engine → Reward Engine → Grader

# 5. 🌍 Environment Design
## Field
- Geolocated
- 6–20 zones

## Zones
- soil_metrics: Dict[str, float]
- crop_health: float
- crop_stage: str
- uncertainty: float
- last_measured_day: int
- health_score: float
- degradation_level: float
- expected_yield: float

## Zone Lifecycle
HEALTHY → AT_RISK → DEGRADED

Derived:
- Recoverable
- Salvageable
- Not worth saving

# 6. 👨‍🌾 Farmer Constraints
- daily_time_budget
- max_tasks_per_day
- travel_time_between_zones
- budget_remaining

# 7. 🧾 Observation Space
Global:
- day
- weather
- budget_remaining
- farmer_time_remaining

Zone:
- soil_metrics (noisy)
- uncertainty
- crop_health
- crop_stage
- last_measured

Hidden:
- true state

# 8. 🎮 Actions
- TAKE_READING
- APPLY_INPUT
- IRRIGATE
- WAIT

# 9. 🌦️ Weather
- normal
- drought
- erratic
- delayed monsoon

# 10. 🔁 State Transitions
- soil dynamics
- time decay
- uncertainty evolution

# 11. 🧪 Sensor Model
observed = true + bias + noise + drift

Configurable noise.

# 12. 📊 Metrics Scaling
Easy: 5 metrics
Medium: 10 metrics
Hard: 18 metrics

# 13. 💰 Cost Model
- monetary
- time
- soil degradation

# 14. 💰 Reward
reward =
+ yield
+ efficiency
+ correct sacrifice
- cost
- overuse
- waste

# 15. 🧪 Grader
score ∈ [0,1]

# 16. 🎯 Tasks
Easy: understanding  
Medium: allocation  
Hard: sacrifice  

# 17. ⚠️ Failure Modes
- over-fertilization
- wasted time
- poor prioritization
- ignoring uncertainty

# 18. 🏗️ Architecture
Modules:
- env
- state_engine
- transition_engine
- reward_engine
- grader
- sensor_model

API:
- /tasks
- /grader
- /baseline

# 19. 🧪 Baseline Agent
Uses OpenAI API key.

# 20. 📦 Structure
agri_env/
- env
- models
- tasks
- grader
- baseline
- api
- config
- data
- openenv.yaml
- Dockerfile
- README.md

# 21. 🐳 Deployment
- Docker
- Hugging Face Spaces

# 22. 🚀 Pitch
Geolocated agricultural decision environment with uncertainty, resource constraints, and irreversible dynamics.

# 23. 🧠 Summary
Easy = understanding  
Medium = allocation  
Hard = sacrifice

# 24. ❓ Clarification Questions
To avoid implementation ambiguity following questions need to researched/clarified:

1. **Episode horizon**
   - What is the default episode length (number of days/steps) per difficulty?

2. **Termination conditions**
   - Should episodes end only by horizon, or also by budget/time exhaustion and crop failure thresholds?

3. **Action granularity**
   - For `APPLY_INPUT`, what are the allowed input types and amount ranges?
   - For `IRRIGATE`, what amount units and min/max bounds should be enforced?

4. **Travel model**
   - Is travel time computed using Euclidean distance, Manhattan distance, or a fixed matrix?
   - Should travel consume only time, or time + monetary fuel cost?

5. **Zone initialization**
   - Should zone count be fixed per task or randomly sampled within 6-20 using a seed?
   - Do we have canonical starting distributions for soil/crop health by difficulty?

6. **Weather dynamics**
   - Are weather scenarios sampled once per episode or can they switch mid-episode?
   - Do we need a forecast window (for example, next 3 days) in observations?

7. **Sensor model defaults**
   - What are baseline values/ranges for bias, noise, and drift by difficulty?
   - Should sensor noise be metric-specific (for example moisture less noisy than micronutrients)?

8. **Lifecycle transition thresholds**
   - What numeric thresholds map hidden state into `HEALTHY -> AT_RISK -> DEGRADED`?
   - Are transitions strictly monotonic, or can a zone recover lifecycle class after intervention?

9. **Derived strategic classes**
   - Do we need deterministic formulas for `RECOVERABLE/SALVAGEABLE/NOT_WORTH_SAVING`, or grader-only internal labels?

10. **Reward coefficients**
    - What default weights should be used for:
      - yield
      - efficiency
      - correct sacrifice
      - cost penalty
      - overuse penalty
      - waste penalty

11. **Correct sacrifice definition**
    - What exact conditions count as a successful sacrifice decision in hard tasks?
    - Is there a minimum number/ratio of deprioritized zones expected?

12. **Grader protocol**
    - Are graders task-specific with separate formulas, or unified with task-weighted criteria?
    - Should grader output include sub-scores/explanations or only a single scalar score?

13. **Reproducibility standard**
    - Which seeds must be fixed (env seed, task seed, weather seed, model seed)?
    - What tolerance is acceptable for baseline reproducibility across runs?

14. **API contract details**
    - Confirm expected request/response schemas for `/tasks`, `/grader`, `/baseline`.
    - Should `/baseline` run synchronously or async job-style with polling?

15. **Performance constraints**
    - Any expected max runtime per episode and per baseline full run?
    - Any memory/CPU limits to optimize for HF Space tier constraints?

16. **Validation requirements**
    - Beyond `openenv validate`, do we need custom pre-submission checks/scripts?

17. **Baseline agent expectations**
    - Should baseline be intentionally simple (weak but valid), or target a competitiveness threshold?
    - Any required model name/version constraints for the OpenAI client?

# 25. Clarification Answers

## 1. Episode horizon

Use fixed default horizons by difficulty:

- **Easy**: 10 days
- **Medium**: 14 days
- **Hard**: 21 days

These values should remain configurable through `EnvConfig`, while the above values serve as project defaults.

## 2. Termination conditions

Episodes terminate when any of the following conditions is met:

1. horizon reached
2. budget exhausted and no valid actions remain
3. farmer time exhausted for the remaining episode and no meaningful actions remain
4. catastrophic crop failure threshold crossed for too many zones

MVP termination logic:

- `done = True` if `current_day >= max_days`
- OR `budget_remaining <= 0 and no_affordable_actions`
- OR `all_zones_dead_or_unsalvageable`

Exhausting a single day's time budget should end the day only, not the full episode.

## 3. Action granularity

### `APPLY_INPUT`

Allowed types:

- `nitrogen`
- `phosphorus`
- `potassium`
- `organic`

Optional extension:

- `balanced_npk`

Amount range:

- float in **[1.0, 10.0]** normalized agronomic units

Recommended discrete-friendly values:

- 1, 2.5, 5, 7.5, 10

### `IRRIGATE`

Amount units:

- normalized water units

Range:

- float in **[1.0, 10.0]**

## 4. Travel model

Use **Euclidean distance** between zone coordinates.

Travel cost for MVP:

- **time only** (no direct monetary fuel cost)

Formula:

- `travel_time = distance * travel_time_per_unit`

## 5. Zone initialization

### Zone count

Use fixed counts by default:

- **Easy**: 6 zones
- **Medium**: 10 zones
- **Hard**: 14 zones

Randomized counts may be added later, but fixed counts are preferred for reproducibility.

### Starting distributions

Define canonical defaults by difficulty:

#### Easy

- mostly healthy/recoverable
- low uncertainty
- mild deficiencies

#### Medium

- mixed recoverable and at-risk
- moderate uncertainty
- uneven nutrient distribution

#### Hard

- mixed field with some degraded zones
- higher uncertainty
- one or two likely sacrifice candidates

## 6. Weather dynamics

Sample weather scenario **once per episode** and keep it coherent throughout the episode.

Scenario switching mid-episode is out of scope for MVP.

### Forecast window

Include a **3-day forecast window** in observations.

Observation should expose:

- today
- next 3 days forecast:
  - rain probability
  - temperature
  - optional heat stress score

## 7. Sensor model defaults

Sensor noise should be **metric-specific**.

### Baseline defaults

#### Easy

- noise_std: 0.01
- bias_std: 0.00
- drift_per_day: 0.005
- missing_prob: 0.00
- outlier_prob: 0.00

#### Medium

- noise_std: 0.03
- bias_std: 0.01
- drift_per_day: 0.01
- missing_prob: 0.02
- outlier_prob: 0.01

#### Hard

- noise_std: 0.05
- bias_std: 0.02
- drift_per_day: 0.02
- missing_prob: 0.05
- outlier_prob: 0.03

### Metric-specific guidance

- moisture: lower noise
- pH: low to moderate noise
- N/P/K: moderate noise
- micronutrients: highest noise

## 8. Lifecycle transition thresholds

Use hidden `health_score` in [0,1].

### Numeric thresholds

- `HEALTHY`: `health_score >= 0.70`
- `AT_RISK`: `0.40 <= health_score < 0.70`
- `DEGRADED`: `health_score < 0.40`

### Transition behavior

Transitions are not strictly monotonic; lifecycle class may improve after intervention.

Design constraint:

- recovery should be harder than degradation
- degraded zones should recover slowly and at higher cost
- hysteresis should be preserved

## 9. Derived strategic classes

Define deterministic internal formulas for:

- `RECOVERABLE`
- `SALVAGEABLE`
- `NOT_WORTH_SAVING`

These labels remain internal and are used by reward and grading logic.

### Suggested rule inputs

- current `health_score`
- `crop_stage`
- `recovery_cost_estimate`
- `expected_yield_remaining`

MVP guidance:

- **Recoverable**:
  - `health_score >= 0.60`
  - low/moderate recovery cost
  - sufficient crop-stage time remaining

- **Salvageable**:
  - `0.30 <= health_score < 0.60`
  - high recovery cost
  - meaningful expected yield remains

- **Not worth saving**:
  - `health_score < 0.30`
  - or late stage + high cost + low expected yield remaining

## 10. Reward coefficients

Use the following default weights:

- yield: **+1.0**
- efficiency: **+0.4**
- correct sacrifice: **+0.5**
- cost penalty: **-0.3**
- overuse penalty: **-0.5**
- waste penalty: **-0.4**

Formula:

```text
reward =
  1.0 * yield_delta
+ 0.4 * efficiency_bonus
+ 0.5 * correct_sacrifice_bonus
- 0.3 * cost_penalty
- 0.5 * overuse_penalty
- 0.4 * waste_penalty
```

Normalize intermediate components to avoid domination by any single term.

## 11. Correct sacrifice definition

A correct sacrifice decision occurs when the agent:

- intentionally deprioritizes one or more internally `NOT_WORTH_SAVING` zones,
- reallocates saved resources to `RECOVERABLE` or high-value `SALVAGEABLE` zones,
- and achieves better overall field outcomes than thin, uniform allocation.

No fixed sacrifice ratio is required. Sacrifice remains opportunity-dependent and should not be mandatory in every hard episode.

## 12. Grader protocol

Use task-specific graders with shared metric components.

Shared components:

- yield score
- efficiency score
- sustainability score
- prioritization score

Output requirements:

- mandatory scalar `score` in `[0,1]`
- optional `subscores`
- short `explanation`

Example:

```json
{
  "score": 0.78,
  "subscores": {
    "yield": 0.82,
    "efficiency": 0.74,
    "sustainability": 0.71,
    "prioritization": 0.85
  },
  "explanation": "Good allocation with one correct sacrifice; slight overuse penalty."
}
```

## 13. Reproducibility standard

Fix the following seeds:

- environment seed
- task seed
- weather seed
- sensor noise seed

Model seed determinism is not required for API-based LLM baselines.

Acceptable baseline variance:

- target within **+/-0.03 to +/-0.05**

For stronger reproducibility, use a heuristic-first baseline.

## 14. API contract details

Use simple synchronous contracts for MVP.

### `/tasks`

Returns task definitions and configs.

```json
{
  "tasks": [
    {"id": "easy", "difficulty": "easy"},
    {"id": "medium", "difficulty": "medium"},
    {"id": "hard", "difficulty": "hard"}
  ]
}
```

### `/grader`

Request:

- task id
- trajectory or final episode summary

Response:

- scalar score
- optional subscores
- explanation

### `/baseline`

Runs synchronously for MVP.

Response should include:

- per-task scores
- aggregate score
- logs or summary

Async job polling is out of scope unless explicitly required by the brief.

## 15. Performance constraints

Targets:

- per episode runtime: **under 1 second**
- full baseline run across all tasks: **under 60 seconds** (preferred: under 30 seconds)

HF Space constraints:

- optimize for low CPU and memory
- keep core runtime in-memory
- avoid unnecessary heavy dependencies

## 16. Validation requirements

In addition to `openenv validate`, add pre-submission checks.

Recommended script:

- `scripts/check_submission.py`

Checks should include:

- environment reset and step execution
- all 3 tasks run
- graders return scores in `[0,1]`
- baseline runs end-to-end
- API endpoints respond
- required config files exist
- Docker build basics validated where possible

## 17. Baseline agent expectations

Baseline objectives:

> **simple, valid, reproducible, and clearly better than random**
> not optimized to maximize benchmark rank

Guidelines:

- intentionally modest behavior
- sufficient to demonstrate environment usage
- avoid over-tuning

### Model/version constraints

If an OpenAI API baseline is included:

- keep model configurable via environment/config
- default to a lightweight stable model where allowed
- avoid hardcoding expensive models

Preferred rollout:

- implement a **heuristic baseline first**
- add an optional LLM baseline second

Benefits:

- deterministic fallback
- easier testing
- easier deployment

## Final decisions

- fixed horizons: 10 / 14 / 21
- fixed zone counts: 6 / 10 / 14
- Euclidean travel with time-only cost
- 3-day forecast window
- task-specific deterministic graders with scalar + subscores
- synchronous `/baseline`
- metric-specific configurable sensor noise
- lifecycle can improve, with recovery harder than degradation
- sacrifice is situational, not mandatory
- baseline is simple and reproducible, heuristic-first