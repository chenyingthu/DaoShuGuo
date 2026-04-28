# Generic Full Loop Validation

## Purpose

This document defines how DaoShuGuo tests whether a new task can move beyond onboarding into a complete research loop:

`skill -> effectiveness -> cognition -> next decision`

The claim is limited to power-research tasks that satisfy the task package, adapter, evaluator, and runtime contracts.

## Proof Boundary

The framework must not claim arbitrary universality.

It may claim bounded generality only when new tasks enter through data packages and adapters without task-specific framework code.

## Required Objects

A full-loop iteration requires:

- `task_readiness_report`
- `skill_change_request`
- `skill_change_result`
- `effectiveness_assessment`
- `cognition_diagnosis`
- `loop_routing_decision`
- `loop_review`
- `artifact_index`
- `run.yaml`

Blocked tasks must not enter the full loop.

## Backend Roles

`deterministic` validates contracts and controller structure.

`codex_omx` validates the canonical Codex/OMX agentic path.

`pi_gpt55` validates whether Pi-agent using GPT-5.5 is a better harness substrate.

Text-only backend success is not enough. A backend must write required loop objects to count as full-loop proof.

## Proof Levels

- Level 0: onboarding only
- Level 1: deterministic full loop
- Level 2: single agentic full loop
- Level 3: cross-task agentic full loop
- Level 4: backend-robust agentic full loop
- Level 5: research-quality autonomous loop

## Current Validation Discipline

Bad outcomes are valid if correctly diagnosed:

- degraded candidate
- blocked task
- evaluator gap
- evidence insufficiency
- portfolio stop

The controller must not author skill, effectiveness, or cognition judgments.
