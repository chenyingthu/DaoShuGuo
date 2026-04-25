# DaoShuGuo Research Loop for Pi

DaoShuGuo-on-Pi package for bounded research-loop execution.

## Purpose

This package turns Pi into a harness for DaoShuGuo research work.

It does **not** replace the existing Python runtime. Instead:

- Pi acts as the upper-layer agent harness
- DaoShuGuo Python code remains the domain runtime
- `research_loop.md` and `research_loop.jsonl` act as durable loop memory

## Package Contents

- `extensions/daoshuguo-research-loop/index.ts`
- `skills/daoshuguo-research-create/SKILL.md`

## Tools

- `init_research_task`
- `log_research_iteration`
- `record_skill_trial`
- `record_cognition_constraint`
- `record_iteration_review`
- `run_task003_trial`

## Command

- `/daoshuguo`

## Design Rules

- Skill workers change candidate skill code only.
- Cognition workers write bounded next-round constraints only.
- Effectiveness claims must remain below the evidence ceiling.
- The durable loop record must always live in:
  - `research_loop.md`
  - `research_loop.jsonl`

## Install

From a local path:

```bash
pi install /path/to/DaoShuGuo-v1/pi-packages/daoshuguo-research-loop
```

## Repo-local Verification

Pi package discovery:

```bash
HOME=/tmp/daoshuguo-pi-feasibility/home \
node /tmp/daoshuguo-pi-feasibility/pi-mono/packages/coding-agent/dist/cli.js list
```

Local durable-loop simulation:

```bash
python scripts/simulate_pi_research_loop.py
```

task003 bridge:

```bash
python scripts/verify_pi_task003_bridge.py
```

## Current Scope

Current vertical slice:

- `task003`

Deferred:

- `task004`
- `task005`
- full Pi RPC orchestration
- full cognition-driven next-iteration loop

## Resume Rule

Resume by reading:

1. `research_loop.md`
2. latest relevant entries from `research_loop.jsonl`

The package is designed so a future Pi session does not depend on hidden conversation state.
