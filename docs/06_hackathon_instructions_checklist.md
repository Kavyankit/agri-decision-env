# Hackathon / OpenEnv submission checklist

Use this list when switching from **builder mode** to **submission mode**. Items marked **done in repo** are satisfied by the current codebase or docs. Items marked **you (manual)** require your Hugging Face account, API keys, or a machine with Docker / `openenv` CLI installed.

---

## Repository & compliance (automated / in-repo)

| Status | Task |
|--------|------|
| [x] | **Real-world-style environment** — multi-zone sim, partial observability, constraints (`env/`, `models/`, `config/`). |
| [x] | **OpenEnv-style API** — FastAPI (`/health`, `/tasks`, `/grader`, `/baseline`), `main.py`, `Dockerfile`, port **7860**, `openenv.yaml`. |
| [x] | **Three tasks + graders** — `easy` / `medium` / `hard`, deterministic scores (`tasks/`, `grader/`). |
| [x] | **Reward shaping** — `env/reward_engine.py`, `RewardBreakdown`. |
| [x] | **Heuristic baseline** — `baseline/`, `scripts/run_baseline.py`. |
| [x] | **OpenAI baseline script** — `scripts/openai_baseline.py` (initializes `OpenAI` client, calls `/tasks` + `/baseline`; requires `OPENAI_API_KEY` + running server). |
| [x] | **README baseline scores** — see [README](../README.md) section **Baseline results** (heuristic, seed **42**). |
| [x] | **Docs** — problem statement, design, PRD, judging alignment, heuristic runs (`docs/01`–`05`), this checklist (`docs/06`). |
| [x] | **Validation scripts** — `scripts/smoke_test.py`, `scripts/check_submission.py`. |

---

## What you must do manually

| Status | Task | Notes |
|--------|------|--------|
| [ ] **you** | **Deploy Hugging Face Space (Docker)** | Create Space → SDK **Docker** → public → push/connect this repo. Confirm `Dockerfile` exposes **7860** and `CMD` runs `uvicorn`. **Cannot be done by the repo alone.** |
| [ ] **you** | **Smoke-test live Space** | After deploy: `GET /health`, `GET /tasks`, `POST /baseline` (e.g. `{"seed": 42}`). Optional: `POST /grader` with a valid `episode_summary`. |
| [ ] **you** | **Run `openenv validate .`** | Install the OpenEnv CLI if the hackathon provides it, then run from repo root. **Not run in this workspace** (CLI not installed here). |
| [ ] **you** | **Docker build locally** (optional but recommended) | `docker build -t agri-decision-env .` then `docker run -p 7860:7860 agri-decision-env`. **Skipped here** if Docker is not installed on your PATH. |
| [ ] **you** | **`scripts/openai_baseline.py` against a live URL** | Set `OPENAI_API_KEY`, set `OPENENV_BASE_URL` to your Space URL if not localhost, start server (local or deployed), run script. |

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

## Summary: what’s left for you

1. **HF Space deployment** (mandatory if required by brief).  
2. **Live endpoint checks** on the Space URL.  
3. **`openenv validate`** when the CLI is available.  
4. **Local Docker test** (optional).  
5. **OpenAI script** against production URL + real key (if required for demo).

Everything else in the checklist above is already in the repository.
