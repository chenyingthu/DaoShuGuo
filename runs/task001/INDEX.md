# task001 Run Index

## Purpose

This index identifies the current recommended task001 run artifacts and explains why historical runs are retained.

## Current Recommended Runs

### Real ext-grid reference

- Run: `run.power.ieee33_reactive_opt.0009`
- Path: [run_0009](/home/chenying/root-research/DaoShuGuo-v1/runs/task001/run_0009)
- Purpose: strongest current metric result for the ext-grid strategy.

### Real weak-shunt skill run

- Run: `run.power.ieee33_reactive_opt.0011`
- Path: [run_0011](/home/chenying/root-research/DaoShuGuo-v1/runs/task001/run_0011)
- Purpose: current representative run for the more research-semantically meaningful weak-shunt candidate skill.

## Historical Runs

Runs `run_0001` through `run_0008` are retained as development history:

- demo runs
- failed runs
- early real-run attempts
- writeback-path validation

They should not be used as the primary evidence for task001 conclusions unless specifically studying framework evolution.

## Validation

Use:

```bash
python orchestrator/main.py verify-task001-pipeline
python scripts/run_integration_checks.py
```
