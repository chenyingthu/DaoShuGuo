# Research Plan-Execute Protocol Plan Review

## Code Review Round 1 - 2026-04-25

**Scope**: `plans/research-plan-execute-protocol-plan.md`
**Build Status**: PASS for document review; implementation not started.

### Issues

#### Issue 1 (High): `real_progress` could be misread as unconditional approval

The first draft allowed `approved` or `real_progress` to enter the next iteration. That would recreate the current weakness where a positive but bounded result advances the loop without a hard claim boundary.

**Fix applied**: The plan now states that only `approved` can proceed unconditionally. `real_progress` can only enter `bounded_next_iteration` with claim boundary, required ablation, or repair note.

#### Issue 2 (High): Research-plan-execute risked duplicating the generic loop engine

The first draft did not explicitly define how the new protocol relates to the existing generic loop engine and diagnosis layer. This could lead to another parallel task-specific runner.

**Fix applied**: Added a non-duplication principle: generic loop engine keeps phase orchestration; research-plan-execute owns plan/batch/context/review/repair/approval discipline.

#### Issue 3 (High): Missing runtime binding and transcript accountability

The first draft did not require a formal runtime binding. Given the project's Codex/Pi provider history, this would leave agent provenance weak.

**Fix applied**: Added `worker_runtime_binding`, runtime/provider/model/tool/session/timeout/transcript requirements, and runtime repair routing.

#### Issue 4 (High): No hard ablation gate for cognition-causality claims

The first draft recognized task003 iter02 causality risk but did not make it a hard gate.

**Fix applied**: Added ablation gate and deterministic baseline requirements. Without ablation, the system may claim skill performance improved but may not claim cognition caused the improvement.

#### Issue 5 (Medium): Repair loop lacked retry bounds

The first draft defined repair worker types but did not prevent infinite automatic repair.

**Fix applied**: Added maximum two automatic retries per repair request; third failure routes to human review.

#### Issue 6 (Medium): Context pack was under-specified

The first draft listed core context fields but omitted provenance, redaction, budgets, expected failure modes, and previous repair attempts.

**Fix applied**: Expanded context pack requirements and made context pack a persisted object from which prompts are rendered.

### Verdict: APPROVED

---

## Code Review Round 3 - 2026-04-25

**Scope**: Phase 3 review gate engine implementation
**Build Status**: PASS

### Issues

No blocking issues found in the Phase 3 implementation.

### Checks Performed

- Confirmed `scripts/run_research_review_gate.py` acts as a gate, not as a worker or loop runner.
- Confirmed the gate reads existing task003 iter02 evidence and emits `research_review.yaml`.
- Confirmed task003 iter02 is not unconditionally approved: the verdict is `approved_with_ablation_required`.
- Confirmed bounded approval freezes causality claims including `cognition caused skill improvement`.
- Confirmed `scripts/verify_research_review_gate.py` rejects missing review-gate artifacts, unconditional `real_progress`, missing repair routing for blocked verdicts, and missing frozen claims for ablation-required approval.
- Confirmed negative tests cover metric failure and missing cognition discriminating tests.

### Verification

- `python -m py_compile scripts/run_research_review_gate.py scripts/verify_research_review_gate.py scripts/verify_research_plan_execute_protocol.py`
- `python scripts/run_research_review_gate.py --task task003 --iteration 2`
- `python scripts/verify_research_review_gate.py`
- `python scripts/verify_research_plan_execute_protocol.py`
- `pytest tests/test_research_review_gate.py -q`
- `python scripts/validate_schemas.py`
- `python scripts/validate_schemas.py --artifacts research-plan-execute-protocol`
- `python scripts/validate_schemas.py --artifacts real-agentic-loop`
- `python scripts/run_light_probe.py`

### Remaining Risks

- The review gate is deterministic for the MVP case. It enforces hard protocol rules but does not yet invoke an LLM review worker.
- The gate currently supports only `--task task003 --iteration 2`.
- Full repair worker execution remains Phase 4; Phase 3 only generates the route when repair verdicts occur.

### Verdict: APPROVED

The plan is now suitable as the next-stage implementation guide. Main remaining risk is execution scope: Phase 1 and Phase 2 should be implemented before any new task expansion.

---

## Code Review Round 2 - 2026-04-25

**Scope**: Phase 1/2 implementation for `research-plan-execute`
**Build Status**: PASS

### Issues

No blocking issues found in the Phase 1/2 implementation.

### Checks Performed

- Confirmed the implementation stayed within the approved scope: protocol docs, schemas, schema samples, context pack builder, and protocol verifier.
- Confirmed no new loop runner was introduced and no task006 expansion was added.
- Confirmed `scripts/build_agent_context_pack.py` reconstructs task003 iter02 into persisted `research_batch`, `worker_runtime_binding`, `agent_context_pack`, rendered prompts, and `execution_ledger`.
- Confirmed context packs separate `skill_worker`, `effectiveness_worker`, `cognition_worker`, and `review_worker` boundaries.
- Confirmed the verifier checks runtime binding, rendered prompts, review history refs, blocked paths, allowed changes, provenance digest, and causality stop conditions.
- Confirmed the schema validator recognizes the new object types and validates the `research-plan-execute-protocol` artifact set.

### Verification

- `python -m py_compile scripts/build_agent_context_pack.py scripts/verify_research_plan_execute_protocol.py scripts/validate_schemas.py`
- `python scripts/build_agent_context_pack.py --task task003 --iteration 2`
- `python scripts/verify_research_plan_execute_protocol.py`
- `python scripts/validate_schemas.py`
- `python scripts/validate_schemas.py --artifacts research-plan-execute-protocol`

### Remaining Risks

- This is still a context/protocol layer, not a full review gate engine.
- The generated context packs are reconstructed from task003 iter02; the builder intentionally supports only `--task task003 --iteration 2` in this MVP.
- Real worker invocation through this protocol is deferred to Phase 3+.

### Verdict: APPROVED
