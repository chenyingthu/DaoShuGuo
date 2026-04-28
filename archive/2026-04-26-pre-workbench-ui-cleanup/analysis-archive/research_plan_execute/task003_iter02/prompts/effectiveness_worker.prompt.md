# Research Plan-Execute Context: effectiveness_worker

Mission: Assess baseline and candidate evidence without changing skills or task definitions.

## Role Boundary
- Do not modify candidate skill code.
- Do not convert metric improvement into cognition causality.
- Do not weaken evaluator or baseline requirements.

## Task And Evidence
- Task refs: task.power.ieee69_renewable_reactive_opt
- Evaluator refs: evaluator.power.ieee69_renewable_reactive_opt.default
- Baseline refs: baseline.power.ieee69_renewable_reactive_opt.fixed_inverter_q
- Prior artifact refs: skill_agent_iteration_request.power.ieee69_renewable_reactive_opt.0002, skill_agent_iteration_result.power.ieee69_renewable_reactive_opt.0002, agentic_cognition_to_skill_update.power.ieee69_renewable_reactive_opt.0002, agentic_loop_iteration_review.power.ieee69_renewable_reactive_opt.0002, run.power.ieee69_renewable_reactive_opt.0021
- Review history refs: agentic_loop_iteration_review.power.ieee69_renewable_reactive_opt.0002

## Allowed Changes
- evaluation run artifact
- metrics comparison artifact
- metric boundary note

## Blocked Paths
- skills/active_dev/**
- tasks/**
- cognition/**

## Current Hypothesis
Current evidence reports loss 139.67066814649814 -> 88.5302433764974 and constraint_violation 8 -> 5.

## Output Contract
- Required output schema: schema.run
- Runtime binding: worker_runtime_binding.power.ieee69_renewable_reactive_opt.effectiveness_worker.0002
- Provenance digest: sha256:4317e0bf11e44d0cc9eeee8b2b39cb4c6da47ceed3ae9010b8947f8a18fb1066

## Stop Conditions
- missing required artifact reference
- attempt to relax evaluator or baseline
- attempt to claim cognition causality without ablation

## Redaction Policy
Never include provider tokens, local secrets, or ~/.claude and ~/.pi auth material.
