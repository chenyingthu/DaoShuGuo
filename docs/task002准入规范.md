# task002 准入规范

## Purpose

This document defines when the project is allowed to start testing `task002`.

## Admission Criteria

`task002` may begin only after:

1. `task001` integration checks pass.
2. `task001` pipeline verification passes.
3. schema and artifact validation pass.
4. task001 run/analysis indexes identify current recommended artifacts.
5. task002 plan explicitly reuses existing schemas, registry conventions, and evaluator/taste/writeback flow.

## Required Reuse

task002 must reuse:

- schema envelope conventions
- task / baseline / evaluator / run objects
- skill registry
- cognition registry
- evidence bundle
- taste assessment
- artifact validation
- integration-check style verification

## Allowed Variation

task002 may change:

- research object
- simulator/model
- baseline skill
- candidate skill
- evaluator metrics
- literature seeds

## Minimum Task Package

task002 must provide:

- `tasks/task002/task.md`
- `tasks/task002/task.yaml`
- `tasks/task002/constraints.yaml`
- `tasks/task002/baseline.yaml`
- `tasks/task002/targets.yaml`
- at least one evaluator spec
- at least one baseline skill
- at least one candidate skill

## Minimum Success Criteria

task002 succeeds if it can:

- run a real or clearly scoped executable task
- compare baseline and candidate
- generate run / metrics / evidence / taste / report
- write back skill and cognition records
- pass task-specific integration checks

## Failure Also Counts If

task002 may count as useful even if the candidate fails, provided:

- evaluator truly ran
- failure is recorded
- negative cognition is generated
- report does not overclaim

## Prohibited

task002 must not:

- bypass evaluator
- create a parallel schema system
- bypass taste assessment
- report success without evidence
- ignore task001 lessons and reimplement the framework from scratch
