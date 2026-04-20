# PRD: Evidence-Stratified Cognition Upgrade

## Goal

Complete the evidence-stratified cognition upgrade path for `task001`.

## Scope

In scope:

- `abstract_excerpt` and `fulltext_excerpt` source kinds participate in the literature source layer
- source strength propagates into explanation alignment
- explanation evidence strength propagates into novelty assessment and cognition upgrade
- a one-command task001 vertical verification proves the chain

Out of scope:

- automatic PDF parsing
- large-scale literature search
- multi-task generalization

## Acceptance Criteria

- `python scripts/validate_schemas.py` passes
- `python scripts/validate_schemas.py --artifacts literature-alignment-plan` passes
- `python -m py_compile orchestrator/main.py` passes
- task001 vertical verification passes
- latest `novelty_assessment` includes `evidence_strength: high`
- latest `novelty_assessment` uses `continue_investment: prioritize`
- latest `cognition_upgrade` references excerpt-level evidence

## Deliverables

- updated orchestration logic
- updated schemas if necessary
- generated literature and analysis artifacts
- updated plans and records
- Git commit preserving the final state
