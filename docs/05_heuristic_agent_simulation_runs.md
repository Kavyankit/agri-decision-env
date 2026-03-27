# Heuristic agent: example CLI simulation run

This document demonstrates how the baseline heuristic agent behaves across difficulty levels using reproducible CLI runs.

This page is **not** a formal API reference. It walks through **three reproducible examples** you can run yourself from the terminal: **`easy`**, **`medium`**, and **`hard`**, all with **seed `42`**. Same command, same seed → same transcript on the same codebase—handy for demos and judging packets.

If you only need the commands, jump to [Commands](#commands). If you want to understand **why** the log shows “no tasks” on some days and a burst of **readings** on others, read [What the agent sees each day](#what-the-agent-sees-each-day) and [Why “no tasks” vs take a reading](#why-no-tasks-vs-take-a-reading).

---

## Commands

From the **repository root**, with dependencies installed (`pip install -r requirements.txt`).

Swap **`easy`** / **`medium`** / **`hard`** in the commands below to match the section you’re reading.

**1. Human-readable day-by-day transcript**

```bash
python scripts/simulate_episode.py --task easy --seed 42 --mode heuristic --format text
python scripts/simulate_episode.py --task medium --seed 42 --mode heuristic --format text
python scripts/simulate_episode.py --task hard --seed 42 --mode heuristic --format text
```

**2. Machine-readable JSON** with an optional per-step `trace` (actions, rewards, `reward_breakdown`, spend, travel):

```bash
python scripts/simulate_episode.py --task easy --seed 42 --mode heuristic --verbose
python scripts/simulate_episode.py --task medium --seed 42 --mode heuristic --verbose
python scripts/simulate_episode.py --task hard --seed 42 --mode heuristic --verbose
```

**3. Benchmark score + grader explanation** after the episode (same policy path as the baseline runner):

```bash
python scripts/run_baseline.py --task easy --seed 42
python scripts/run_baseline.py --task medium --seed 42
python scripts/run_baseline.py --task hard --seed 42
```

- `--mode noop` runs the environment with **empty actions every day** (useful only as a sanity check).
- Omit `--task` on `run_baseline.py` to run **easy, medium, and hard** in one go.

---

## What the agent sees each day

The heuristic does **not** see hidden ground truth. It only gets whatever the environment puts in the **current `Observation`**, roughly:

- **Per zone** (`ZoneObservation`):
  - **`crop_health`** — how good the crop looks from the agent’s perspective (may differ from hidden truth because of the sensor layer).
  - **`uncertainty`** — how unsure the model is about that zone (higher → “I need better intel”).
  - **`stale_days`** — how long since a fresh reading; information goes stale unless you **`TAKE_READING`**.
  - **`observed_metrics`** — things like `soil_moisture`, nitrogen / phosphorus / potassium, etc. Some values can be **`None`** (missing reading).
- **Global**: **`remaining_budget`**, **`remaining_time_budget`**, weather **forecast**, and the **current day**.

So when we explain decisions below, we mean: “given **this** noisy, possibly stale snapshot, the rule-based policy does **this**.”

---

## Why “no tasks” vs take a reading

The baseline policy lives in `baseline/heuristic_agent.py`. In plain language:

1. **Zones are ranked by urgency** (lower health, higher uncertainty, higher staleness → more urgent).
2. For each zone, the policy picks **one candidate** action: reading, irrigate, apply input, or **wait**.
3. **Important detail:** **`WAIT` is not sent to the environment as a task.** The agent only submits a list of **non-wait** tasks. So if every zone’s candidate is “wait,” the printed plan is **empty** — that is what **`(no tasks)`** means in the transcript: *the heuristic chose not to schedule any concrete intervention for that day*, not that “nothing happened in the world.” Weather, passive dynamics, and rewards can still move.

**When it prefers `TAKE_READING`**

Roughly (see code for exact numbers):

- **Uncertainty** is above a threshold → “refresh this zone,” or  
- **`stale_days`** has grown large enough → “this intel is too old,” or  
- A softer rule: uncertainty is in a middle band → still prefer a reading over doing nothing.

**When it might irrigate or apply inputs**

- **Soil moisture** (if visible) looks dry enough → irrigate.  
- **N, P, or K** (if visible) look low enough → apply a mixed input.

**When you see `(no tasks)`**

- For every zone, the candidate was **`WAIT`**: metrics and staleness/uncertainty looked **good enough** that the rules did not ask for a reading or an intervention, **or**
- The policy wanted actions but **budget or time** (including **travel** between zones) could not fit more tasks that day.

In the **runs below** (same seed), **easy** shows mostly quiet days with **reading** waves when staleness builds; **medium** adds **irrigate** and splits readings across days because of the daily task cap. **Hard** is **14 zones**, **21 days**, and a **leaner starting budget**—so you rarely get an all-`WAIT` day: the same rules keep firing **irrigate**, **apply_input**, and **take_reading** as urgency and visible N/P/K and moisture dictate. That matches the design: **observe when information quality drops**, and **intervene when the (noisy) visible metrics say so**—with **hard** grader emphasis on sustainability and discipline.

---

## What these runs demonstrate

Across difficulty levels, the baseline agent:

- alternates between observation and intervention based on uncertainty and visible metrics
- respects time, budget, and travel constraints
- scales behavior with task difficulty (from periodic observation to constant intervention)
- produces stable, reproducible outputs under fixed seeds

**Reproducibility check:** On this repository, each of **`easy` / `medium` / `hard`** was run **twice** with **seed `42`** (same machine, same `simulate_episode.py` and `run_baseline.py`). **JSON output matched exactly** between runs (`total_reward`, `steps`, scores, episode summaries). **`--format text`** transcripts were **byte-for-byte identical** between runs. Your numbers should match if you use the same commit and dependency versions.

---

## Example transcript — easy (seed 42)

### Easy insight

Mostly observation-driven due to low pressure and sufficient resources.

Below is **real output** from `--format text`. Your line breaks and float formatting should match if you use the same seed and task.

```text
=== Heuristic episode | task=easy seed=42 mode=heuristic ===
max_days=10 zones=6

Day  1 | reward +0.042035 | rb_total 0.04203454958255609 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  2 | reward +0.020165 | rb_total 0.020165242678128876 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  3 | reward +0.017974 | rb_total 0.017974052985698957 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  4 | reward +0.015034 | rb_total 0.015033932895883268 | budget 3.0 time 2.5 travel 1.0
         | take_reading z0; take_reading z1; take_reading z2; take_reading z3; take_reading z4; take_reading z5

Day  5 | reward +0.018133 | rb_total 0.018132722624485474 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  6 | reward +0.018272 | rb_total 0.018272263098140628 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  7 | reward +0.017124 | rb_total 0.017124276949601492 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  8 | reward +0.012317 | rb_total 0.01231736532973892 | budget 3.0 time 2.5 travel 1.0
         | take_reading z0; take_reading z1; take_reading z2; take_reading z3; take_reading z4; take_reading z5

Day  9 | reward +0.016551 | rb_total 0.01655128224550411 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day 10 | reward +0.015100 | rb_total 0.015100167067509825 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

--- total_reward=0.192706 steps=10 ---
```

---

## Example transcript — medium (seed 42)

### Medium insight

Balanced intervention and observation under moderate constraints.

**Medium** uses **more zones (10)** and a **longer horizon (14 days)** than easy, with **tighter default budget** in the preset. The **same heuristic** still applies: rank zones, then schedule up to **`max_actions_per_day`** tasks that fit time and budget (including **travel** between zone indices).

You’ll see differences from easy:

- **Day 2** schedules **`irrigate z3`** — on that day’s observation, zone 3’s visible soil moisture looked dry enough to cross the irrigation threshold (noise included).  
- **Reading days** often show **five** `take_reading` lines, not ten: the daily task cap means the agent **covers the field in waves** (different zone IDs on consecutive reading days, e.g. low-index zones first, then the rest—see days 4–5, 8–9, 12–13). Non-zero **`travel`** appears when the path between chosen zones isn’t free.

Real output from `--format text`:

```text
=== Heuristic episode | task=medium seed=42 mode=heuristic ===
max_days=14 zones=10

Day  1 | reward +0.042509 | rb_total 0.042508922720541305 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  2 | reward +0.018219 | rb_total 0.01821881161535859 | budget 1.5 time 0.5 travel 0.0
         | irrigate z3 amt=1

Day  3 | reward +0.017872 | rb_total 0.017872108254000502 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  4 | reward +0.014887 | rb_total 0.014887218453904278 | budget 2.5 time 2.25 travel 1.0
         | take_reading z0; take_reading z1; take_reading z2; take_reading z4; take_reading z5

Day  5 | reward +0.014530 | rb_total 0.014530498226293887 | budget 2.5 time 3.0500000000000003 travel 1.8000000000000003
         | take_reading z6; take_reading z7; take_reading z8; take_reading z9; take_reading z3

Day  6 | reward +0.018765 | rb_total 0.01876456461630795 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  7 | reward +0.017334 | rb_total 0.017334058298801858 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day  8 | reward +0.011651 | rb_total 0.011651443214855808 | budget 2.5 time 2.25 travel 1.0
         | take_reading z0; take_reading z1; take_reading z2; take_reading z4; take_reading z5

Day  9 | reward +0.013010 | rb_total 0.013009827558884258 | budget 2.5 time 3.0500000000000003 travel 1.8000000000000003
         | take_reading z6; take_reading z7; take_reading z8; take_reading z9; take_reading z3

Day 10 | reward +0.015065 | rb_total 0.0150650328334484 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day 11 | reward +0.013258 | rb_total 0.013257864375288992 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

Day 12 | reward +0.010457 | rb_total 0.01045661795077139 | budget 2.5 time 2.25 travel 1.0
         | take_reading z0; take_reading z1; take_reading z2; take_reading z4; take_reading z5

Day 13 | reward +0.009749 | rb_total 0.0097492622879348 | budget 2.5 time 3.0500000000000003 travel 1.8000000000000003
         | take_reading z6; take_reading z7; take_reading z8; take_reading z9; take_reading z3

Day 14 | reward +0.012692 | rb_total 0.01269226226644225 | budget 0.0 time 0.0 travel 0.0
         | (no tasks)

--- total_reward=0.229998 steps=14 ---
```

---

## Example transcript — hard (seed 42)

### Hard insight

Continuous intervention with strong resource trade-offs and efficiency pressure.

**Hard** stretches the **horizon (21 days)** and **zone count (14)**, with a **smaller initial budget** than easy/medium. With the same heuristic, you should expect **something scheduled almost every day**: more **visible metrics** and more stress in the preset means **irrigate** / **apply_input** show up whenever the observed soil or nutrients look bad, and **readings** fill the rest under the daily cap.

You will see **four** tasks on many days (`max_actions_per_day` on hard), **heavier travel** when the policy jumps between distant zone indices, and **mixed lines** (e.g. readings plus an input) when budget and time still allow.

Real output from `--format text`:

```text
=== Heuristic episode | task=hard seed=42 mode=heuristic ===
max_days=21 zones=14

Day  1 | reward +0.032516 | rb_total 0.032516317978470946 | budget 5.5 time 2.7 travel 1.2
         | apply_input z5 amt=1 in=mixed; irrigate z6 amt=1; apply_input z11 amt=1 in=mixed

Day  2 | reward +0.012550 | rb_total 0.012549865883698955 | budget 5.5 time 2.7 travel 1.2
         | irrigate z0 amt=1; apply_input z1 amt=1 in=mixed; apply_input z6 amt=1 in=mixed

Day  3 | reward +0.016384 | rb_total 0.01638356374843509 | budget 1.5 time 0.5 travel 0.0
         | irrigate z7 amt=1

Day  4 | reward +0.015615 | rb_total 0.015615435844099627 | budget 2.0 time 1.6 travel 0.6000000000000001
         | take_reading z2; take_reading z3; take_reading z4; take_reading z5

Day  5 | reward +0.015174 | rb_total 0.015174227717943134 | budget 2.0 time 1.6 travel 0.6000000000000001
         | take_reading z8; take_reading z9; take_reading z10; take_reading z11

Day  6 | reward +0.014965 | rb_total 0.014965492201218556 | budget 2.0 time 4.6000000000000005 travel 3.6000000000000005
         | take_reading z12; take_reading z13; take_reading z1; take_reading z6

Day  7 | reward +0.010394 | rb_total 0.010393969985334036 | budget 4.5 time 3.9000000000000004 travel 2.4000000000000004
         | take_reading z0; take_reading z7; apply_input z5 amt=1 in=mixed; irrigate z8 amt=1

Day  8 | reward +0.012127 | rb_total 0.012126529761873516 | budget 2.0 time 1.6 travel 0.6000000000000001
         | take_reading z2; take_reading z3; take_reading z4; take_reading z5

Day  9 | reward +0.013103 | rb_total 0.013102789990428233 | budget 2.0 time 2.0 travel 1.0
         | take_reading z9; take_reading z10; take_reading z11; take_reading z8

Day 10 | reward +0.011131 | rb_total 0.011131023839811332 | budget 2.0 time 4.6000000000000005 travel 3.6000000000000005
         | take_reading z12; take_reading z13; take_reading z1; take_reading z6

Day 11 | reward +0.009727 | rb_total 0.009727332376210821 | budget 2.0 time 3.6000000000000005 travel 2.6000000000000005
         | take_reading z0; take_reading z7; take_reading z2; take_reading z3

Day 12 | reward +0.008147 | rb_total 0.00814659254291239 | budget 3.5 time 2.45 travel 1.2
         | take_reading z4; take_reading z5; take_reading z9; apply_input z10 amt=1 in=mixed

Day 13 | reward +0.009294 | rb_total 0.0092943326602376 | budget 2.0 time 2.4000000000000004 travel 1.4000000000000001
         | take_reading z11; take_reading z10; take_reading z8; take_reading z12

Day 14 | reward +0.008438 | rb_total 0.008438345039446288 | budget 2.0 time 5.2 travel 4.2
         | take_reading z13; take_reading z1; take_reading z6; take_reading z2

Day 15 | reward +0.007338 | rb_total 0.007338054304205137 | budget 2.0 time 3.6 travel 2.6
         | take_reading z3; take_reading z0; take_reading z7; take_reading z4

Day 16 | reward +0.006266 | rb_total 0.006266102358588925 | budget 2.0 time 3.2 travel 2.2
         | take_reading z9; take_reading z5; take_reading z11; take_reading z12

Day 17 | reward +0.005308 | rb_total 0.005307647135084666 | budget 2.0 time 4.800000000000001 travel 3.8000000000000003
         | take_reading z10; take_reading z8; take_reading z2; take_reading z13

Day 18 | reward +0.005134 | rb_total 0.005134411372697411 | budget 2.0 time 2.8 travel 1.8
         | take_reading z1; take_reading z6; take_reading z3; take_reading z4

Day 19 | reward +0.002540 | rb_total 0.002539989060612589 | budget 3.5 time 3.45 travel 2.2
         | take_reading z0; take_reading z7; apply_input z9 amt=1 in=mixed; take_reading z11

Day 20 | reward +0.003705 | rb_total 0.0037048664730878196 | budget 2.0 time 4.6000000000000005 travel 3.6000000000000005
         | take_reading z12; take_reading z5; take_reading z9; take_reading z2

Day 21 | reward +0.002728 | rb_total 0.0027278369489304025 | budget 2.0 time 3.0 travel 2.0
         | take_reading z13; take_reading z10; take_reading z8; take_reading z3

--- total_reward=0.222585 steps=21 ---
```

---

**How to read the columns** (easy, medium, and hard)

- **`reward` / `rb_total`**: step reward and its breakdown total (should align).  
- **`budget` / `time` / `travel`**: what that day’s **scheduled tasks** spent; quiet days show zeros because **no tasks were submitted** (all-internal `WAIT`).  
- **Reading / irrigation rows** show non-zero spend because those actions cost time and budget like any other operation.

---

## Example grader output (seed 42)

After each run, `run_baseline.py` packages the episode and applies the task-specific grader. You get **`score`** in **`[0, 1]`**, **`subscores`**, and a short **`explanation`**.

**Easy** (`python scripts/run_baseline.py --task easy --seed 42`):

```json
{
  "results": [
    {
      "task_id": "easy",
      "episode_summary": {
        "task_id": "easy",
        "max_days": 10,
        "initial_budget": 150.0,
        "remaining_budget": 144.0,
        "days_elapsed": 10,
        "total_reward": 0.19270585545724767,
        "overuse_penalty_total": 0.0,
        "total_actions": 12,
        "waste_actions": 0,
        "final_avg_degradation": 0.14267900182333224,
        "final_avg_crop_health": 0.8787228484501676
      },
      "score": 0.6747880601369161,
      "subscores": {
        "outcome": 0.5094531255090655,
        "efficiency": 0.6868630019696716,
        "sustainability": 0.8690920158270927,
        "discipline": 1.0,
        "horizon_utilization": 1.0
      },
      "explanation": "Score 0.675. Strongest area: discipline (1.00); weakest area: outcome (0.51)."
    }
  ]
}
```

**Medium** (`python scripts/run_baseline.py --task medium --seed 42`):

```json
{
  "results": [
    {
      "task_id": "medium",
      "episode_summary": {
        "task_id": "medium",
        "max_days": 14,
        "initial_budget": 100.0,
        "remaining_budget": 83.5,
        "days_elapsed": 14,
        "total_reward": 0.22999849267283426,
        "overuse_penalty_total": 0.0,
        "total_actions": 31,
        "waste_actions": 0,
        "final_avg_degradation": 0.2196602266204307,
        "final_avg_crop_health": 0.8132888073726339
      },
      "score": 0.6876609647676563,
      "subscores": {
        "outcome": 0.5112413747097602,
        "efficiency": 0.6364441924012061,
        "sustainability": 0.7984617420757548,
        "discipline": 1.0,
        "horizon_utilization": 1.0
      },
      "explanation": "Score 0.688. Strongest area: discipline (1.00); weakest area: outcome (0.51)."
    }
  ]
}
```

**Hard** (`python scripts/run_baseline.py --task hard --seed 42`):

```json
{
  "results": [
    {
      "task_id": "hard",
      "episode_summary": {
        "task_id": "hard",
        "max_days": 21,
        "initial_budget": 70.0,
        "remaining_budget": 16.0,
        "days_elapsed": 21,
        "total_reward": 0.22258472722332748,
        "overuse_penalty_total": 0.0,
        "total_actions": 79,
        "waste_actions": 0,
        "final_avg_degradation": 0.3734940450751549,
        "final_avg_crop_health": 0.6825300616861183
      },
      "score": 0.6363854685486202,
      "subscores": {
        "outcome": 0.5108869103638032,
        "efficiency": 0.3930100809121428,
        "sustainability": 0.6573192136435453,
        "discipline": 1.0,
        "horizon_utilization": 1.0
      },
      "explanation": "Score 0.636. Strongest area: discipline (1.00); weakest area: efficiency (0.39)."
    }
  ]
}
```

---

## See also

- `baseline/heuristic_agent.py` — exact thresholds and priority weights.  
- `scripts/simulate_episode.py` — CLI flags (`--verbose`, `--format text`).  
- `scripts/run_baseline.py` — baseline + grading in one command.
