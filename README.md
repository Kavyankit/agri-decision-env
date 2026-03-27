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

Next: Reward engine and optimization objectives

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

## 🧩 Core Concepts

- **Zones**: field segments with soil, crop, and health state.
- **Hidden State vs Observations**: true field state evolves internally and is only partially observable.
- **Lifecycle Dynamics**: zones transition between healthy, at-risk, and degraded states over time.
- **Strategic Classes**: zones are categorized as recoverable, salvageable, or not worth saving.
- **Actions**: agents can take readings, apply inputs, irrigate, or wait.
- **Sensor Model**: observations include noise, bias, missing values, and occasional outliers.
- **Staleness**: information degrades over time unless refreshed via `TAKE_READING`.
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
- `grader/`: deterministic scoring (planned)
- `baseline/`: reference agents (planned)

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

## 🧪 Design Philosophy

This environment is designed to simulate real-world agricultural decision-making under:

- partial observability
- noisy measurements
- resource constraints
- strategic trade-offs
