This document provides the complete scaffolding specification for the project.

It defines the recommended structure, interfaces, and implementation order for the engineering team.

---

# Geo-Agricultural Decision Environment

## Complete Scaffolding Specs / Project Structure

---

# 1. High-level goals

The project must provide:

* an **OpenEnv-style environment**
* 3 tasks:

  * easy
  * medium
  * hard
* deterministic graders
* a baseline runner
* a FastAPI service with required endpoints
* Docker packaging
* Hugging Face Spaces deployment readiness

The project should be:

* modular
* easy to review
* easy to extend
* lightweight enough to run on a normal laptop

---

# 2. Top-level repository structure

```text
agri-env/
├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── routes_tasks.py
│   ├── routes_grader.py
│   ├── routes_baseline.py
│   ├── schemas.py
│   └── dependencies.py
│
├── env/
│   ├── __init__.py
│   ├── environment.py
│   ├── state_engine.py
│   ├── transition_engine.py
│   ├── reward_engine.py
│   ├── sensor_model.py
│   ├── weather_engine.py
│   ├── action_validator.py
│   ├── task_factory.py
│   └── constants.py
│
├── grader/
│   ├── __init__.py
│   ├── base_grader.py
│   ├── easy_grader.py
│   ├── medium_grader.py
│   ├── hard_grader.py
│   ├── grader_factory.py
│   └── scoring_utils.py
│
├── baseline/
│   ├── __init__.py
│   ├── heuristic_agent.py
│   ├── llm_agent.py
│   ├── runner.py
│   ├── prompt_builder.py
│   └── parsing.py
│
├── models/
│   ├── __init__.py
│   ├── config_models.py
│   ├── zone_models.py
│   ├── observation_models.py
│   ├── action_models.py
│   ├── reward_models.py
│   ├── weather_models.py
│   ├── task_models.py
│   ├── grader_models.py
│   └── api_models.py
│
├── config/
│   ├── __init__.py
│   ├── env_presets.py
│   ├── sensor_presets.py
│   ├── weather_presets.py
│   ├── task_presets.py
│   ├── reward_weights.py
│   └── fertilizer_catalog.py
│
├── data/
│   ├── weather_scenarios.json
│   ├── fertilizer_catalog.json
│   ├── crop_profiles.json
│   └── example_tasks.json
│
├── tasks/
│   ├── __init__.py
│   ├── easy_task.py
│   ├── medium_task.py
│   ├── hard_task.py
│   └── task_registry.py
│
├── scripts/
│   ├── run_local_api.py
│   ├── run_baseline.py
│   ├── simulate_episode.py
│   ├── check_submission.py
│   └── smoke_test.py
│
├── tests/
│   ├── __init__.py
│   ├── test_environment.py
│   ├── test_transitions.py
│   ├── test_reward.py
│   ├── test_graders.py
│   ├── test_api.py
│   ├── test_baseline.py
│   └── test_configs.py
│
├── .env.example
├── .gitignore
├── README.md
├── openenv.yaml
├── Dockerfile
├── requirements.txt
└── main.py
```

---

# 3. Responsibilities of each folder

---

## `api/`

Purpose:
Expose the environment and benchmark through HTTP endpoints.

### Files

### `app.py`

* create FastAPI app
* register routers
* healthcheck endpoint optional

### `routes_tasks.py`

* implements `/tasks`

### `routes_grader.py`

* implements `/grader`

### `routes_baseline.py`

* implements `/baseline`

### `schemas.py`

* request/response schemas for API
* can reuse models from `models/` if clean

### `dependencies.py`

* shared dependency wiring
* load config
* build env/task objects

---

## `env/`

Purpose:
Core environment logic.

### `environment.py`

Main `AgriEnv` class.

Must expose:

* `reset()`
* `step(action)`
* `state()`

This file should orchestrate, not contain all business logic.

### `state_engine.py`

Responsible for:

* initializing episode state
* updating per-zone ground truth
* advancing day counters
* maintaining hidden state

### `transition_engine.py`

Responsible for:

* applying actions
* fertilizer effects
* irrigation effects
* degradation and recovery transitions
* crop progression

### `reward_engine.py`

Responsible for:

* step reward computation
* dense reward shaping
* reward breakdown

### `sensor_model.py`

Responsible for:

* converting hidden ground truth into observed noisy values
* noise
* bias
* staleness drift
* missing/outlier simulation

### `weather_engine.py`

Responsible for:

* loading weather scenarios
* sampling scenario per episode
* exposing 3-day forecast
* applying weather impact to zones

### `action_validator.py`

Responsible for:

* validating action schema
* validating bounds
* validating time budget
* validating budget remaining
* validating task legality

### `task_factory.py`

Responsible for:

* building env instances for easy/medium/hard
* injecting correct presets

### `constants.py`

Shared enums, strings, action names, lifecycle labels.

---

## `grader/`

Purpose:
Task scoring.

### `base_grader.py`

Common interface:

* `grade(trajectory_or_summary) -> GradeResult`

### `easy_grader.py`

Scoring for easy task

### `medium_grader.py`

Scoring for medium task

### `hard_grader.py`

Scoring for hard task, especially sacrifice correctness

### `grader_factory.py`

Returns correct grader for task ID

### `scoring_utils.py`

Shared normalization helpers, clamps, score composition

---

## `baseline/`

Purpose:
Reference agents and runner.

### `heuristic_agent.py`

Mandatory first baseline.
Should be:

* deterministic
* cheap
* valid
* not brilliant

### `llm_agent.py`

Optional second baseline.
Uses OpenAI API through `OPENAI_API_KEY`.

### `runner.py`

Runs baseline over all tasks and returns summary.

### `prompt_builder.py`

For LLM baseline only.
Converts structured obs into prompt.

### `parsing.py`

Parses LLM output into valid `Action`.

---

## `models/`

Purpose:
Typed Pydantic models.

### `config_models.py`

* `EnvConfig`
* `SensorNoiseConfig`
* `RewardWeights`
* `TaskConfig`

### `zone_models.py`

* hidden zone state
* observed zone state
* lifecycle state enums

### `observation_models.py`

* `Observation`
* `ZoneObservation`
* forecast structures

### `action_models.py`

* `Action`
* `TaskAction`
* action parameter schemas

### `reward_models.py`

* `RewardBreakdown`
* `RewardResult`

### `weather_models.py`

* `WeatherDay`
* `ForecastWindow`
* `WeatherScenario`

### `task_models.py`

* task metadata
* task descriptor
* task registry output

### `grader_models.py`

* `GradeResult`
* subscore models

### `api_models.py`

* API request/response payloads if you want separation

---

## `config/`

Purpose:
Preset configs.

### `env_presets.py`

Defines:

* easy env config
* medium env config
* hard env config

### `sensor_presets.py`

Noise presets by difficulty

### `weather_presets.py`

Scenario presets

### `task_presets.py`

Task-specific parameters:

* horizon
* zone count
* starting distributions

### `reward_weights.py`

Default reward coefficients

### `fertilizer_catalog.py`

Defines available intervention types and their:

* cost
* speed
* risk
* effect profile

---

## `data/`

Purpose:
Non-code static data.

Keep small and human-editable.

### `weather_scenarios.json`

* normal
* drought
* erratic
* delayed monsoon

### `fertilizer_catalog.json`

Optional if not hardcoded in config

### `crop_profiles.json`

Simple crop behavior profiles if needed later

### `example_tasks.json`

Optional example task descriptors

---

## `tasks/`

Purpose:
Task construction and registration.

### `easy_task.py`

Defines task metadata + config preset

### `medium_task.py`

Defines task metadata + config preset

### `hard_task.py`

Defines task metadata + config preset

### `task_registry.py`

Single source of truth for task list returned by `/tasks`

---

## `scripts/`

Purpose:
Dev utilities.

### `run_local_api.py`

Run FastAPI locally

### `run_baseline.py`

Run baseline over all tasks

### `simulate_episode.py`

Debug one episode manually

### `check_submission.py`

Pre-submission sanity checks

### `smoke_test.py`

Simple end-to-end check

---

## `tests/`

Purpose:
Lightweight confidence checks.

Need not be huge, but enough to catch breakage.

---

# 4. Entry points

---

## `main.py`

Single entrypoint for deployment.

Should expose FastAPI app for Spaces / uvicorn.

Example responsibility:

* import `create_app()` from `api.app`
* expose `app`

---

# 5. Core interfaces

These are the most important contracts in the whole repo.

---

## Environment interface

```python
class AgriEnv:
    def reset(self) -> Observation: ...
    def step(self, action: Action) -> tuple[Observation, float, bool, dict]: ...
    def state(self) -> dict: ...
```

### Notes

* `state()` may return internal debug state, not raw observation
* `step()` must be deterministic under fixed seeds

---

## Grader interface

```python
class BaseGrader:
    def grade(self, episode_summary: dict) -> GradeResult: ...
```

---

## Baseline agent interface

```python
class BaseAgent:
    def act(self, observation: Observation) -> Action: ...
```

---

# 6. Internal domain model design

---

## Hidden zone state vs observed zone state

This separation is mandatory.

### Hidden state

Contains:

* true nutrient values
* true health score
* degradation level
* hidden recoverability class
* expected yield potential

### Observed state

Contains:

* noisy sensor values
* uncertainty score
* last measured day
* visible crop health proxy

This avoids mixing simulation truth with what the agent sees.

---

# 7. Recommended domain enums

Put these in `env/constants.py` or `models/zone_models.py`.

```python
class LifecycleState(str, Enum):
    HEALTHY = "HEALTHY"
    AT_RISK = "AT_RISK"
    DEGRADED = "DEGRADED"

class StrategicClass(str, Enum):
    RECOVERABLE = "RECOVERABLE"
    SALVAGEABLE = "SALVAGEABLE"
    NOT_WORTH_SAVING = "NOT_WORTH_SAVING"

class ActionType(str, Enum):
    TAKE_READING = "TAKE_READING"
    APPLY_INPUT = "APPLY_INPUT"
    IRRIGATE = "IRRIGATE"
    WAIT = "WAIT"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
```

---

# 8. Configuration scaffolding

Use a config-driven approach. Do not hardcode gameplay values all over the codebase.

---

## `EnvConfig` should include

```python
class EnvConfig(BaseModel):
    difficulty: str
    max_days: int
    zone_count: int
    daily_time_budget: float
    max_tasks_per_day: int
    starting_budget: float
    travel_time_per_unit: float
    forecast_days: int
    random_seed: int
    sensor_config: SensorNoiseConfig
    reward_weights: RewardWeights
```

---

## `SensorNoiseConfig`

```python
class SensorNoiseConfig(BaseModel):
    measurement_noise_std: float
    measurement_bias_std: float
    staleness_drift_per_day: float
    missing_reading_prob: float
    outlier_prob: float
    metric_specific_noise: dict[str, float] = {}
```

---

## `RewardWeights`

```python
class RewardWeights(BaseModel):
    yield_weight: float = 1.0
    efficiency_weight: float = 0.4
    sacrifice_weight: float = 0.5
    cost_penalty_weight: float = 0.3
    overuse_penalty_weight: float = 0.5
    waste_penalty_weight: float = 0.4
```

---

# 9. Task presets

---

## Easy

* max_days = 10
* zone_count = 6
* near-infinite/large budget
* no meaningful time pressure beyond daily action formatting
* 5 metrics
* low noise

## Medium

* max_days = 14
* zone_count = 10
* budget-limited
* moderate time pressure
* 10 metrics
* moderate noise

## Hard

* max_days = 21
* zone_count = 14
* budget-limited
* strong time pressure
* 18 metrics
* higher noise
* deliberate sacrifice opportunities in some episodes

---

# 10. API scaffolding specs

---

## `/tasks`

### Method

`GET`

### Returns

List of supported tasks.

### Response

```json
{
  "tasks": [
    {
      "id": "easy",
      "difficulty": "easy",
      "description": "Basic diagnosis under abundant resources"
    },
    {
      "id": "medium",
      "difficulty": "medium",
      "description": "Allocation under budget constraints"
    },
    {
      "id": "hard",
      "difficulty": "hard",
      "description": "Time-critical planning with sacrifice decisions"
    }
  ]
}
```

---

## `/grader`

### Method

`POST`

### Request

Should accept:

* task id
* episode summary or trajectory summary

### Response

```json
{
  "score": 0.81,
  "subscores": {
    "yield": 0.84,
    "efficiency": 0.76,
    "sustainability": 0.79,
    "prioritization": 0.86
  },
  "explanation": "Good prioritization and one correct sacrifice; moderate overuse penalty."
}
```

---

## `/baseline`

### Method

`POST` or `GET` depending on how simple you want it

Recommended:

* `POST` with optional model settings
* synchronous execution

### Response

```json
{
  "results": [
    {"task_id": "easy", "score": 0.72},
    {"task_id": "medium", "score": 0.64},
    {"task_id": "hard", "score": 0.51}
  ],
  "aggregate_score": 0.62,
  "agent_type": "heuristic"
}
```

---

# 11. Baseline runner scaffolding

The runner should:

1. load tasks from registry
2. build env per task
3. reset env
4. loop until done
5. collect trajectory summary
6. call grader
7. aggregate task scores

---

# 12. Episode summary structure

Instead of passing the full raw trajectory to graders at first, create a normalized summary.

Example:

```python
episode_summary = {
    "task_id": "hard",
    "days_run": 21,
    "total_yield_score": 0.78,
    "total_cost": 42.0,
    "overuse_events": 2,
    "wasted_actions": 1,
    "correct_sacrifices": 1,
    "missed_recoverable_zones": 1,
    "final_zone_states": [...],
}
```

This makes graders easier to implement and test.

---

# 13. Suggested implementation order by file

Implementation should be phased rather than built all at once.

---

## Phase 1: Models and config

Build first:

* `models/config_models.py`
* `models/zone_models.py`
* `models/observation_models.py`
* `models/action_models.py`
* `config/env_presets.py`

---

## Phase 2: Core environment

Then:

* `env/environment.py`
* `env/state_engine.py`
* `env/action_validator.py`

At this stage, step logic can be minimal.

---

## Phase 3: Simulation engines

Then:

* `env/transition_engine.py`
* `env/weather_engine.py`
* `env/sensor_model.py`
* `env/reward_engine.py`

---

## Phase 4: Tasks and graders

Then:

* `tasks/*.py`
* `grader/*.py`

---

## Phase 5: Baseline

Then:

* `baseline/heuristic_agent.py`
* `baseline/runner.py`

---

## Phase 6: API layer

Then:

* `api/app.py`
* routes

---

## Phase 7: Packaging

Then:

* `main.py`
* `Dockerfile`
* `openenv.yaml`
* `README.md`

---

# 14. Minimal MVP behavior requirements

Before adding polish, the repo must be able to:

* instantiate easy env
* reset
* step through a full episode
* produce a reward every step
* produce done at end
* create episode summary
* grade it
* run baseline on all three tasks
* expose `/tasks`, `/grader`, `/baseline`

That is the true MVP.

---

# 15. Non-goals for MVP

Do **not** expand into these areas too early:

* fancy visualizations
* database
* async job queue
* authentication
* frontend UI
* advanced crop science realism beyond what affects decisions
* training an RL model
* huge test suite

All of that is post-MVP.

---

# 16. Docker / deployment scaffolding

You need:

---

## `requirements.txt`

Keep it minimal:

* fastapi
* uvicorn
* pydantic
* python-dotenv
* openai
* pytest

Possibly:

* numpy

Avoid heavy unnecessary packages.

---

## `Dockerfile`

Should:

* use slim Python image
* install requirements
* copy repo
* expose service port
* run uvicorn

---

## `openenv.yaml`

Should include:

* name
* description
* task list
* endpoint information
* how to run baseline
* metadata

---

# 17. README structure spec

The `README.md` should be structured with the following sections:

1. Project overview
2. Why this environment matters
3. Task breakdown
4. Environment design
5. Observation and action spaces
6. Reward design
7. Grading
8. API endpoints
9. Baseline runner
10. Local run instructions
11. Docker instructions
12. Deployment notes

---

# 18. Pre-submission scripts

Must have:

## `scripts/check_submission.py`

Checks:

* imports work
* tasks load
* env resets
* one episode runs
* graders output valid score
* API app imports
* baseline runner works

## `scripts/smoke_test.py`

Tiny fast sanity run.

---

# 19. Implementation Guidelines

Apply the following engineering rules consistently:

* keep business logic out of API routes
* keep `environment.py` orchestration-only
* use Pydantic everywhere for typed contracts
* never mix hidden state and observed state
* make graders deterministic
* baseline must work without LLM
* keep all hardcoded gameplay values inside config/presets
* keep modules small and readable
* prefer simple functions over giant classes where possible

---

# 20. Ultimate directory tree with file intent

```text
agri-env/
├── api/                  # HTTP layer only
├── env/                  # environment mechanics
├── grader/               # deterministic task scoring
├── baseline/             # reference agents and runner
├── models/               # typed data models
├── config/               # presets and weights
├── data/                 # static JSON data
├── tasks/                # task registry and task presets
├── scripts/              # local dev and validation scripts
├── tests/                # smoke/unit tests
├── README.md             # judge-facing explanation
├── openenv.yaml          # submission metadata
├── Dockerfile            # deployment
├── requirements.txt      # dependencies
└── main.py               # app entrypoint
```

---

# 21. Final build philosophy

This project should feel like:

* a **small game engine**
* a **benchmark service**
* a **clean simulation system**

Not:

* a monolithic script
* a notebook pile
* an overbuilt enterprise app

---

This specification can be used directly as a file-by-file scaffolding checklist for initial implementation.
