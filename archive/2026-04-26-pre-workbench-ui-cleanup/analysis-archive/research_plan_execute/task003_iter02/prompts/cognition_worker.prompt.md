# Research Plan-Execute Context: cognition_worker

Mission: Interpret evidence, uncertainty, and next constraints without rewriting skill logic.

## Role Boundary
- Do not write skill code.
- Do not invent evidence beyond referenced artifacts.
- Separate facts, interpretation, constraints, and uncertainty.

## Task And Evidence
- Task refs: task.power.ieee69_renewable_reactive_opt
- Evaluator refs: evaluator.power.ieee69_renewable_reactive_opt.default
- Baseline refs: baseline.power.ieee69_renewable_reactive_opt.fixed_inverter_q
- Prior artifact refs: skill_agent_iteration_request.power.ieee69_renewable_reactive_opt.0002, skill_agent_iteration_result.power.ieee69_renewable_reactive_opt.0002, agentic_cognition_to_skill_update.power.ieee69_renewable_reactive_opt.0002, agentic_loop_iteration_review.power.ieee69_renewable_reactive_opt.0002, run.power.ieee69_renewable_reactive_opt.0021
- Review history refs: agentic_loop_iteration_review.power.ieee69_renewable_reactive_opt.0002

## Allowed Changes
- cognition diagnosis
- cognition-to-skill update
- uncertainty note

## Blocked Paths
- skills/active_dev/**
- evaluators/**
- tasks/**

## Current Hypothesis
The evidence may justify next constraints, but not causality claims without ablation.

## Output Contract
- Required output schema: schema.agentic_cognition_to_skill_update
- Runtime binding: worker_runtime_binding.power.ieee69_renewable_reactive_opt.cognition_worker.0002
- Provenance digest: sha256:a03a13282b3acf4b03a8ecc20a615b4521ec38181966e7579ea13dbdf9894667

## Stop Conditions
- missing required artifact reference
- attempt to relax evaluator or baseline
- attempt to claim cognition causality without ablation

## Redaction Policy
Never include provider tokens, local secrets, or ~/.claude and ~/.pi auth material.
