# 🌾 Agri Decision Environment (OpenEnv)

A real-world agricultural decision-making environment for training and evaluating AI agents under uncertainty, resource constraints, and time pressure.

## 📚 Documentation

This project is structured to simulate real-world agricultural decision-making under uncertainty. The following documents describe the system in increasing depth:

- [Problem Statement](docs/01_problem_statement.md)
- [Design](docs/02_design.md)
- [PRD & HLD](docs/03_prd_hld.md)
- [Judging Alignment](docs/04_judging_alignment.md)

## 🚧 Project Status

- Phase 1 complete: Typed models and configuration system
- Phase 2 complete: Minimal environment loop (`reset` / `step` / `state`)
- Phase 3 complete: Hidden state evolution and lifecycle dynamics
- Phase 4 complete: Deterministic action effects and transition logic
- Phase 5 complete: Sensor model with noise, partial observability, and staleness dynamics
- Phase 6 complete: Weather engine with external dynamics and forecast integration
- Phase 7 complete: Operational constraints with travel-time and observation limits
- Phase 8 complete: Dense reward shaping with interpretable breakdown
- Phase 9 complete: Task layer and registry for easy/medium/hard benchmarks
- Phase 10 complete: Deterministic graders with score, subscores, and explanation
- Phase 11 complete: Heuristic baseline agent and multi-task runner

Next: API integration and validation scripts

## ⚙️ Quick Example

```python
from config import get_config
from env import AgriEnv
from models import Action, Difficulty

config = get_config(Difficulty.EASY)
env = AgriEnv(config)

obs = env.reset()

for _ in range(5):
    action = Action(tasks=[])  # no-op action
    obs, reward, done, info = env.step(action)
    if done:
        break
```

### Baseline Runner Example

```python
from baseline import run_all_tasks

# Runs deterministic heuristic baseline on easy/medium/hard.
results = run_all_tasks(seed=42)
for r in results:
    print(r["task_id"], round(r["score"], 3), r["explanation"])
```

## 🧩 Core Concepts

- **Zones**: field segments with soil, crop, and health state.
- **Hidden State vs Observations**: true field state evolves internally and is only partially observable.
- **Lifecycle Dynamics**: zones transition between healthy, at-risk, and degraded states over time.
- **Strategic Classes**: zones are categorized as recoverable, salvageable, or not worth saving.
- **Actions**: agents can take readings, apply inputs, irrigate, or wait.
- **Sensor Model**: observations include noise, bias, missing values, and occasional outliers.
- **Staleness**: information degrades over time unless refreshed via `TAKE_READING`.
- **Weather Engine**: external environmental factors (rain, temperature) affect soil moisture, degradation, and crop growth.
- **Forecast**: agents receive a limited-horizon weather forecast to enable planning under uncertainty.
- **Travel Constraints**: moving between zones consumes time, introducing spatial cost to decision-making.
- **Observation Limits**: only a limited number of zones can be observed per day, forcing prioritization.
- **Reward Shaping**: step-wise rewards combine yield change, efficiency, sacrifice choices, and cost/overuse/waste signals.
- **Deterministic Grading**: episode summaries are scored into `[0,1]` with reproducible subscores and explanation text.
- **Constraints**: limited time, budget, and daily operational capacity.
- **Objective**: maximize yield and efficiency while making strategic trade-offs.

## 🎯 Difficulty Levels

- **Easy**: lower noise, more resources, fewer exposed metrics.
- **Medium**: balanced resource pressure and uncertainty.
- **Hard**: tighter constraints, higher uncertainty, stronger sacrifice trade-offs.

## 🏗️ Architecture (High-Level)

Agent -> Environment -> State Engine -> Reward -> Grader

- `models/`: typed domain contracts
- `config/`: presets and tunable parameters
- `env/`: simulation engine (loop + lifecycle + transition logic implemented)
- `tasks/`: easy/medium/hard benchmark task wrappers over presets
- `grader/`: deterministic scoring stack (`base`, `easy`, `medium`, `hard`, factory)
- `baseline/`: heuristic reference agent and runner across tasks

## 🧠 Simulation Behavior

- Zones undergo passive degradation over time
- Crop stage progression increases risk of deterioration
- Health, uncertainty, and degradation are internally coupled
- Lifecycle classification is derived from hidden state
- Observations expose only a subset of metrics depending on difficulty
- Actions apply deterministic causal effects per zone (`IRRIGATE`, `APPLY_INPUT`, `TAKE_READING`)
- Repeated same-zone interventions have diminishing returns
- Over-intervention applies non-linear degradation penalties
- Hidden state updates are metric-validated and clamped to `[0, 1]`
- Observations are generated through a sensor model (noise, bias, missing values, outliers)
- Observation quality degrades with staleness (time since last reading)
- `TAKE_READING` resets staleness and improves information quality
- Uncertainty reflects both hidden degradation and sensor noise intensity
- Staleness accumulation is capped to maintain simulation stability
- Daily weather affects hidden state through moisture recovery and stress factors (heat + drought)
- Soil moisture mitigates weather-induced degradation (non-linear interaction)
- Rain impact has diminishing returns when soil is already saturated
- Crop growth rate is influenced by temperature
- Agents receive a rolling weather forecast for future decision-making
- Movement between zones incurs travel time based on distance (zone index difference)
- Action ordering affects total travel cost (path-dependent execution)
- First action starts at its zone without travel cost (simplified starting position)
- Observation actions (`TAKE_READING`) are limited per day to model operational capacity
- Information gathering now competes with action execution under shared time constraints
- Per-step reward is computed from a yield proxy (`crop_health * crop_stage`) and weighted components
- Reward breakdown is exposed in `info.reward_breakdown` to aid debugging and grader alignment
- Benchmark tasks (easy/medium/hard) are defined as thin wrappers around configuration presets
- Episode summaries can be mapped deterministically to normalized benchmark scores
- A deterministic heuristic agent can run full episodes for all benchmark tasks

## 🛠️ Current Capabilities

- Typed environment configuration system
- Difficulty-based presets (`easy`, `medium`, `hard`)
- Structured action and observation contracts
- Hidden-state and observation-layer separation
- Runnable environment loop (`reset`, `step`, `state`)
- Resource constraints (time, budget) enforcement
- Passive lifecycle dynamics (degradation, health, uncertainty)
- Strategic zone classification (recoverable / not-worth-saving)
- Phase 4 transition engine with action effects and per-zone recovery
- Transition debug metadata in `info` (`recovery_applied`, `overuse_penalty_applied`, `interventions_zones`)
- Observation layer may include missing metric values (`None`), and agents must handle them safely
- Phase 5 sensor model with noisy, partial, and stale observations
- Staleness tracking per zone with refresh via `TAKE_READING`
- Deterministic mode support (noise toggle via config)
- Phase 6 weather engine with deterministic scenario-based generation
- Daily weather application affecting moisture, degradation, and growth
- Forecast exposure with configurable horizon for planning
- Integrated external dynamics alongside action and sensor systems
- Phase 7 travel-time model introducing spatial movement cost between zones
- Action sequencing affects total time via path-dependent travel overhead
- Daily observation cap enforcing limited sensing operations
- Config-driven toggles for travel constraints and observation limits
- Extended debug info (`travel_time_spent`, `zones_refreshed`) for analysis
- Phase 8 reward engine with configurable `RewardWeights`
- Per-step `RewardBreakdown` logging yield, efficiency, sacrifice, cost, overuse, and waste terms
- Phase 9 task layer exposing easy/medium/hard presets via a simple registry
- Phase 10 deterministic grader package returning `score`, `subscores`, and short explanation
- Phase 11 baseline package with `HeuristicAgent`, `run_task`, and `run_all_tasks`

## 🧪 Design Philosophy

This environment is designed to simulate real-world agricultural decision-making under:

- partial observability
- noisy measurements
- resource constraints
- strategic trade-offs
- exogenous environmental dynamics and planning signals
- operational constraints and spatial decision costs
- interpretable reward signals that stay aligned with future grading
