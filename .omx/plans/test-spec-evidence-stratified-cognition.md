# Test Spec: Evidence-Stratified Cognition Upgrade

## Verification Commands

1. `python scripts/validate_schemas.py`
2. `python scripts/validate_schemas.py --artifacts literature-alignment-plan`
3. `python -m py_compile orchestrator/main.py`
4. `python orchestrator/main.py verify-task001-pipeline`

## Expected Evidence

- Schema validation passes
- Artifact validation passes
- Orchestrator compiles
- Vertical pipeline verifier reports `Task001 pipeline verification passed.`
- Latest evidence chain includes:
  - `literature/sources/*.fulltext*.yaml`
  - `analysis/task001/explanations_*`
  - `analysis/task001/upgrade_*`
  - `cognition/cards/upgraded_strategy_comparison_*.yaml`

## Failure Conditions

- Missing generated objects
- broken object references
- `evidence_strength` missing from explanation alignment
- `evidence_strength` missing from novelty assessment
- no excerpt-level evidence in cognition upgrade
