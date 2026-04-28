# task001 Analysis Index

## Purpose

This index identifies the current recommended task001 analysis artifacts and distinguishes them from historical intermediate outputs.

## Current Recommended Artifacts

### Result comparison

- Object: `comparison.power.ieee33_reactive_opt.0002`
- Path: [compare_0002](/home/chenying/root-research/DaoShuGuo-v1/analysis/task001/compare_0002)
- Purpose: compares real ext-grid and weak-shunt runs.

### Semantic comparison

- Object: `semantic_comparison.power.ieee33_reactive_opt.0001`
- Path: [semantic_0001](/home/chenying/root-research/DaoShuGuo-v1/analysis/task001/semantic_0001)
- Purpose: compares metric winner vs research-semantic value.

### Literature alignment

- Object: `literature_alignment.power.ieee33_reactive_opt.0001`
- Path: [literature_0001](/home/chenying/root-research/DaoShuGuo-v1/analysis/task001/literature_0001)
- Purpose: maps ext-grid to Volt/Var control and weak-shunt to capacitor placement/reactive compensation.

### Explanation alignment

- Current high-evidence object: latest `explanations_*` with `evidence_strength: high`
- Purpose: provides excerpt-level support/supplement relations.

### Cognition upgrade

- Current high-evidence object: latest `upgrade_*` with `evidence_strength: high` and `decision: upgrade`
- Purpose: proves evidence strength materially changes cognition-upgrade decisions.

## Historical Artifacts

Older `explanations_*` and `upgrade_*` directories are retained to document:

- medium-evidence retain behavior
- earlier card-level alignment
- intermediate review/fix rounds

They are useful for method-history analysis but should not be treated as the latest recommended conclusion.

## Validation

Use:

```bash
python scripts/validate_schemas.py --artifacts literature-alignment-plan
python scripts/run_integration_checks.py
```
