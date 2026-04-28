# Research Plan-Execute Context: skill_worker

Mission: Create or revise a bounded candidate skill artifact from approved constraints only.

## Role Boundary
- Do not judge final research value.
- Do not modify evaluator, task, review, or cognition artifacts.
- Do not make causality claims.

## Task And Evidence
- Task refs: task.power.ieee69_renewable_reactive_opt
- Evaluator refs: evaluator.power.ieee69_renewable_reactive_opt.default
- Baseline refs: baseline.power.ieee69_renewable_reactive_opt.fixed_inverter_q
- Prior artifact refs: skill_agent_iteration_request.power.ieee69_renewable_reactive_opt.0002, skill_agent_iteration_result.power.ieee69_renewable_reactive_opt.0002, agentic_cognition_to_skill_update.power.ieee69_renewable_reactive_opt.0002, agentic_loop_iteration_review.power.ieee69_renewable_reactive_opt.0002, run.power.ieee69_renewable_reactive_opt.0021
- Review history refs: agentic_loop_iteration_review.power.ieee69_renewable_reactive_opt.0002

## Allowed Changes
- candidate skill file
- skill iteration result
- self report of implementation risks

## Blocked Paths
- evaluators/**
- tasks/**
- analysis/agentic_loop/**
- cognition/**
- docs/**

## Current Hypothesis
Bounded candidate changes may improve task003 metrics, but only within review-approved constraints.

## Output Contract
- Required output schema: schema.skill_agent_iteration_request
- Runtime binding: worker_runtime_binding.power.ieee69_renewable_reactive_opt.skill_worker.0002
- Provenance digest: sha256:c84cbc628a5c2503d8a4bc794616da1fdf02d22dd693f59679c1d84174bfe895

## Stop Conditions
- missing required artifact reference
- attempt to relax evaluator or baseline
- attempt to claim cognition causality without ablation

## Redaction Policy
Never include provider tokens, local secrets, or ~/.claude and ~/.pi auth material.
