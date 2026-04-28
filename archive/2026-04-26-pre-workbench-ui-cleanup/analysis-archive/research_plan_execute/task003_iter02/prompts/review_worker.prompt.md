# Research Plan-Execute Context: review_worker

Mission: Apply the hard review gate and decide approval, bounded progress, or repair routing.

## Role Boundary
- Do not repair artifacts directly.
- Do not approve causality claims without ablation.
- Route failures to repair requests instead of controller-side fixes.

## Task And Evidence
- Task refs: task.power.ieee69_renewable_reactive_opt
- Evaluator refs: evaluator.power.ieee69_renewable_reactive_opt.default
- Baseline refs: baseline.power.ieee69_renewable_reactive_opt.fixed_inverter_q
- Prior artifact refs: skill_agent_iteration_request.power.ieee69_renewable_reactive_opt.0002, skill_agent_iteration_result.power.ieee69_renewable_reactive_opt.0002, agentic_cognition_to_skill_update.power.ieee69_renewable_reactive_opt.0002, agentic_loop_iteration_review.power.ieee69_renewable_reactive_opt.0002, run.power.ieee69_renewable_reactive_opt.0021
- Review history refs: agentic_loop_iteration_review.power.ieee69_renewable_reactive_opt.0002

## Allowed Changes
- research review
- repair request
- approval record

## Blocked Paths
- skills/active_dev/**
- evaluators/**
- tasks/**
- agents/skill/results/**

## Current Hypothesis
The previous loop review verdict is real_progress; only approved verdicts proceed freely.

## Output Contract
- Required output schema: schema.research_review
- Runtime binding: worker_runtime_binding.power.ieee69_renewable_reactive_opt.review_worker.0002
- Provenance digest: sha256:b105b9486fc948378b1ac4e258059851217f95cdb24fcec7b306c8ffe9da9cc4

## Stop Conditions
- missing required artifact reference
- attempt to relax evaluator or baseline
- attempt to claim cognition causality without ablation

## Redaction Policy
Never include provider tokens, local secrets, or ~/.claude and ~/.pi auth material.
