# Harness E2E Testing

This guide describes the deterministic E2E lane for the Generic Loop Engine
validation harness.

## Purpose

The E2E tests prove that the harness changes research-record quality, not only
that individual functions can be called. The core comparison is:

- baseline: fixture workers return the sparse engine contract without harness
  requirement injection
- experiment: the same fixture workers return harness-visible research records
  and pass phase validation before persistence

The test is intentionally deterministic. It validates harness enforcement,
retry behavior, and measurable A/B quality gain. It does not claim external
power-system research effectiveness.

## Commands

Run the complete harness E2E suite:

```bash
pytest tests/test_harness_phase_validation.py tests/test_harness_retry_mechanism.py tests/test_harness_ab_comparison.py tests/test_harness_e2e_full_workflow.py -q
```

Run only the full workflow test:

```bash
pytest tests/test_harness_e2e_full_workflow.py -q
```

Generate the report:

```bash
python3 - <<'PY'
from pathlib import Path
from tests.e2e_utils import baseline_phase_outputs, harness_phase_outputs, quality_for_outputs, generate_e2e_report

baseline = quality_for_outputs(baseline_phase_outputs())
experiment = quality_for_outputs(harness_phase_outputs())
generate_e2e_report(Path("plans/E2E_TEST_REPORT.md"), baseline, experiment)
PY
```

## Evidence Boundary

The harness validates the worker return value before the engine writes
canonical worker-chain artifacts. The artifact index stores the harness
validation summary so full workflow tests can verify both:

- the complete persisted worker chain exists
- the pre-persistence harness quality gate passed

This avoids pretending that canonical chain objects are the same schema as the
research-record objects used for quality enforcement.
