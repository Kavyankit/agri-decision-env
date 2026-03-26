# 🌾 Agri Decision Environment (OpenEnv)

A real-world agricultural decision-making environment for training and evaluating AI agents under uncertainty, resource constraints, and time pressure.

## 📚 Documentation

This project is structured to simulate real-world agricultural decision-making under uncertainty. The following documents describe the system in increasing depth:

- [Problem Statement](docs/01_problem_statement.md)
- [Design](docs/02_design.md)
- [PRD & HLD](docs/03_prd_hld.md)
- [Judging Alignment](docs/04_judging_alignment.md)

## 🚧 Project Status

Phase 1 complete: core typed models and configuration presets are implemented.

Next: build the environment execution loop (`reset` / `step`) and simulation skeleton.

## 🧩 Core Concepts

- **Zones**: field segments with soil, crop, and health state.
- **Hidden state vs observations**: true field state is partially observable through noisy readings.
- **Actions**: agents can take readings, apply inputs, irrigate, or wait.
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
- `env/`: simulation logic (in progress)
- `grader/`: deterministic scoring (planned)
- `baseline/`: reference agents (planned)

## 🛠️ Current Capabilities

- Typed environment configuration system
- Difficulty-based presets (`easy`, `medium`, `hard`)
- Structured action and observation contracts
- Hidden-state and observation-layer separation
