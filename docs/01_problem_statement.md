# Problem Statement

## Build a Real-World OpenEnv Environment

Create a complete, real-world OpenEnv environment that an AI agent can learn from through the standard API:
- `step()`
- `reset()`
- `state()`

The environment must model a genuine practical task (not a toy or game), support agent learning and evaluation, and be deployable and reproducible end to end.

---

## Objective

Design and implement an OpenEnv project that is:
- realistic in domain behavior,
- spec-compliant and technically robust,
- well-graded across difficulty levels,
- deployable to Hugging Face Spaces,
- reproducible via a baseline inference script.

---

## Functional Requirements (Mandatory)

1. **Real-world task simulation**
   - Simulate a task humans actually perform.
   - Must not be toy/artificial gameplay.

2. **OpenEnv spec compliance**
   - Implement full OpenEnv interface with typed models:
     - `Observation`
     - `Action`
     - `Reward` (Pydantic models)
   - Required methods:
     - `step(action)` -> returns `observation, reward, done, info`
     - `reset()` -> returns initial observation
     - `state()` -> returns current state
   - Include `openenv.yaml` with required metadata.
   - Must pass validation (`openenv validate`).

3. **At least 3 tasks with graders**
   - Define 3 or more concrete tasks.
   - Difficulty progression required: **easy -> medium -> hard**.
   - Each task must have a programmatic grader.
   - Graders must return deterministic, meaningful scores in range **0.0 to 1.0**.

4. **Meaningful reward function**
   - Reward must provide informative trajectory feedback (not only terminal binary result).
   - Reward should reflect partial progress toward completion.
   - Clearly penalize undesirable behavior (for example: infinite loops, destructive actions).

5. **Baseline inference script**
   - Provide a baseline script using the OpenAI API client.
   - Read credentials from environment variable: `OPENAI_API_KEY`.
   - Script must run all tasks and produce reproducible baseline scores.

---

## Non-Functional Requirements (Mandatory)

1. **Hugging Face Space deployment**
   - Environment must run as a containerized HF Space tagged with OpenEnv.

2. **Containerized execution**
   - Include a working `Dockerfile`.
   - Project must start cleanly with `docker build` + `docker run`.

3. **Documentation quality**
   - `README.md` must include:
     - environment description and motivation,
     - action and observation space definitions,
     - task descriptions with expected difficulty,
     - setup and usage instructions,
     - baseline scores.

---

## Evaluation Criteria (Weights)

1. **Real-world utility (30%)**
   - Does the environment model a genuine useful task?
   - Is it valuable for training/evaluating agents?

2. **Task and grader quality (25%)**
   - Are tasks well-defined with clear objectives?
   - Do graders fairly and accurately measure success?
   - Is difficulty progression meaningful?

3. **Environment design (20%)**
   - Clean state management.
   - Sensible action/observation spaces.
   - Useful reward shaping.
   - Proper episode boundaries.

4. **Code quality and spec compliance (15%)**
   - Follows OpenEnv spec.
   - Typed and documented models.
   - Clean structure.
   - Tested.
   - Docker works.

5. **Creativity and novelty (10%)**
   - Fresh domain or approach.
   - Interesting mechanics/reward design.
   - Engaging environment behavior.

---

## Scoring Breakdown Insights

### Real-world utility (30%)
- 0-5: Toy/artificial, no practical application.
- 6-15: Valid domain but shallow modeling.
- 16-25: Good domain modeling, useful for agent evaluation.
- 26-30: Excellent; fills a real gap with immediate value.

### Task and grader quality (25%)
- Includes 3+ tasks with clear difficulty range.
- Graders produce scores between `0.0` and `1.0`.
- Graders are deterministic and reproducible.
- Hard task meaningfully challenges strong models.

### Environment design (20%)
- `reset()` produces a clean initial state.
- Action/observation types are well-designed and documented.
- Reward signal is informative and not overly sparse.
- Episode boundaries are sensible and enforceable.

### Code quality and spec compliance (15%)
- `openenv validate` passes.
- `docker build` and `docker run` succeed.
- HF Space deploys and responds.
- Baseline script runs and reproduces scores.

### Creativity and novelty (10%)
- New/less-explored problem domain in OpenEnv.
- Reward design has non-trivial, interesting properties.
- Mechanics increase engagement and realism.

---

## Judging Process

### Phase 1: Automated Validation
Must pass:
- HF Space deploys and responds.
- OpenEnv spec compliance checks.
- Docker build checks.
- Baseline script reproducibility checks.
- 3+ tasks with graders checks.

### Phase 2: Agentic Evaluation
- Baseline agent re-run.
- Standard Open LLM agent run across environments.
- Score variance checks.

### Phase 3: Human Review
- Top submissions reviewed by Meta and Hugging Face engineers.
- Reviewed for real-world utility, creativity, and exploit checks.

---

## Pre-Submission Checklist (All Required)

- HF Space endpoint responds (including `reset()`).
- OpenEnv endpoints and schema validate.
- Docker image builds successfully.
- Baseline inference script completes without errors and produces scores.
- 3+ tasks and graders are present and score correctly in `0.0-1.0`.
- Additional endpoints exposed:
  - `/baseline` -> triggers inference script and returns baseline score for all 3 tasks.
  - `/grader` -> returns grader score after completed episode.
  - `/tasks` -> returns list of tasks and action schema (required fields for each action step).
- Validator script run before submission.

---

## Disqualification Criteria

- Environment does not deploy or respond.
- Plagiarized or trivially modified existing environment.
- Graders always return the same score.
- Missing baseline inference script.

---

## Submission Outcome Target

A successful submission should be:
- practically useful,
- technically complete,
- reproducible,
- robustly graded,
- and demonstrably deployable.

