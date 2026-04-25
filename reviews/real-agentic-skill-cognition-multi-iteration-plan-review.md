---

## Code Review Round 1 — 2026-04-22

**Scope**: real agentic loop infrastructure, runner, verifier, orchestrator/integration wiring
**Build Status**: FAIL

### Issues

#### Issue 1 (High): Heavy real-agentic verifier was added to general integration checks
**File**: `scripts/run_integration_checks.py`
The integration suite now runs `scripts/verify_real_agentic_loop.py` unconditionally. That verifier requires a fully completed two-iteration real agentic experiment and therefore turns a reusable repository-wide integration check into a stateful experiment gate. This couples routine validation to a heavy long-running research workflow.
**Fix**: Remove `verify_real_agentic_loop.py` from the default integration commands. Keep only schema/artifact-set validation in the general integration path, and leave the real agentic loop verification on an explicit command path.

#### Issue 2 (High): Agentic cognition update is not compressed to skill-agent-executable constraints
**File**: `scripts/run_real_agentic_loop.py`
`build_agentic_update()` currently forwards long-form cognition outputs almost verbatim into `search_priority_updates` and `required_discriminating_tests`. The resulting iteration-2 request asks the skill agent to solve evaluator semantics, matched comparison design, multi-scenario validation, and claim-transfer justification, which exceeds the bounded role of a single skill-coding agent and leads to execution stall rather than meaningful next-step skill evolution.
**Fix**: Add an explicit compression layer from cognition output to skill-agent request. Keep only code-local, single-agent-executable next-step constraints in the request, and move broader research asks into a separate review/report field.

### Verdict: NEEDS_FIX
