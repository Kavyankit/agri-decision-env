# Hackathon / OpenEnv submission checklist

Use this list when switching from **builder mode** to **submission mode**. Items marked **done in repo** are satisfied by the current codebase or docs. Items in **manual / deployment** were owner actions outside the repo (HF account, API keys, live Space).

**OpenEnv spec validation** (`openenv validate`, etc.) is **run by judges after submission** — it is not a local dependency (see `requirements.txt`).

---

## Repository & compliance (automated / in-repo)

| Status | Task |
|--------|------|
| [x] | **Real-world-style environment** — multi-zone sim, partial observability, constraints (`env/`, `models/`, `config/`). |
| [x] | **OpenEnv-style API** — FastAPI (`/health`, `/tasks`, `/grader`, `/baseline`, `/reset`, `/step`, `/state`), `main.py`, `Dockerfile`, port **7860**, `openenv.yaml`. |
| [x] | **Three tasks + graders** — `easy` / `medium` / `hard`, deterministic scores (`tasks/`, `grader/`). |
| [x] | **Reward shaping** — `env/reward_engine.py`, `RewardBreakdown`. |
| [x] | **Heuristic baseline** — `baseline/`, `scripts/run_baseline.py`. |
| [x] | **OpenAI baseline script** — `scripts/openai_baseline.py` (initializes `OpenAI` client, calls `/tasks` + `/baseline`; requires `OPENAI_API_KEY` + running server). |
| [x] | **README baseline scores** — see [README](../README.md) section **Baseline results** (heuristic, seed **42**). |
| [x] | **Docs** — problem statement, design, PRD, judging alignment, heuristic runs (`docs/01`–`05`), this checklist (`docs/06`). |
| [x] | **Validation scripts** — `scripts/smoke_test.py`, `scripts/check_submission.py`. |

---

## Manual / deployment (completed)

| Status | Task | Notes |
|--------|------|--------|
| [x] | **Deploy Hugging Face Space (Docker)** | Space created, repo connected, `Dockerfile` on **7860** with `uvicorn`. |
| [x] | **Smoke-test live Space** | `GET /health`, `GET /tasks`, `POST /baseline` verified against production URL. |
| [x] | **`scripts/openai_baseline.py` against live URL** | `OPENAI_API_KEY` + `OPENENV_BASE_URL` set (e.g. `.env`); script runs against deployed Space. |

---

## Quick local verification (before submit)

Run from repo root (after `pip install -r requirements.txt`):

```bash
python scripts/smoke_test.py
python scripts/check_submission.py
```

Heuristic baseline scores (reference) — **seed 42**:

```bash
python scripts/run_baseline.py
```

---

## Reproducibility note

Baseline **scores** in the README are from the **heuristic** agent with **seed = 42**. Same code + same deps → same numbers (see `docs/05_heuristic_agent_simulation_runs.md`).

---

## After submission

Judges run **OpenEnv validation** and any competition checks on the submitted artifact — this is **not** pinned in `requirements.txt`.

Everything else for this project is **complete** in-repo and deployed as configured above.
