# Orchestrator Decoupling Plan

## Current Issue

`orchestrator/main.py` currently hosts multiple ability domains:

- task execution
- literature source ingestion
- literature card generation
- strategy comparison
- semantic comparison
- explanation alignment
- cognition upgrade
- task001 pipeline verification

This is acceptable for the first vertical slice, but it should not remain the long-term architecture.

## Target Direction

Keep CLI behavior stable while extracting internal application modules:

1. `orchestrator/literature_app.py`
2. `orchestrator/comparison_app.py`
3. `orchestrator/cognition_app.py`
4. `orchestrator/task001_pipeline.py`

## Low-Risk First Extraction

The first extraction should be `literature_app.py` because it has relatively clear boundaries:

- load seed papers
- ingest literature sources
- build paper/method/explanation cards
- resolve paper excerpts

## Constraints

- Do not change CLI commands during extraction.
- Do not change object IDs.
- Do not change generated artifact schemas.
- Run integration checks before and after each extraction.

## Acceptance Criteria

- `python scripts/run_integration_checks.py` remains green.
- `python orchestrator/main.py verify-task001-pipeline` remains green.
- No generated object shape changes unless explicitly planned.

## Deferred

Full extraction is deferred until task001 stabilization is complete.
