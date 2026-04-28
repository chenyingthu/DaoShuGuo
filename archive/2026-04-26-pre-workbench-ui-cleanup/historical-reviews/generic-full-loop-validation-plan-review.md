---

## Code Review Round 1 — 2026-04-25

**Scope**: `plans/generic-full-loop-validation-plan.md` execution, generic full-loop verifier, Pi GPT-5.5 worker backend, validation reports.
**Verification Status**: PASS

### Issues

No unresolved blocking issues found.

Resolved issues:

- `generic-full-loop-validation` schema artifact set initially included internal runtime YAMLs and worker-chain objects that do not have global schemas. The artifact set was narrowed to formal validation reports; worker-chain semantics are checked by `scripts/verify_generic_full_loop.py`.
- Pi GPT-5.5 initially returned a truncated JSON object on `task008_bad_candidate` during `skill_execution_worker`. A generic compact-output retry now lives in `scripts/llm_full_loop_workers.py`, and the same task then completed successfully.
- `compare_loop_backends.py` initially described Pi full-loop as unproven after Pi runs existed. The backend profile and findings were updated to reflect three verified Pi full-loop artifact chains.

### Execution Deviations

- The plan names `scripts/run_research_pipeline.py`, but the repository currently has no such generic entrypoint. The implementation now uses `scripts/run_generic_loop_engine.py` plus registry-driven backend resolution.
- Codex/OMX full-loop backend dispatch was not implemented in this round. The report explicitly marks Level 4 as not proven.
- Pi GPT-5.5 was tested on fixture-level tasks, not on research-quality task outputs.

### Verification Evidence

```bash
python scripts/verify_generic_full_loop.py --all
python scripts/compare_loop_backends.py --all
python scripts/validate_schemas.py --artifacts generic-full-loop-validation
python scripts/validate_schemas.py --artifacts generic-task-onboarding
pytest tests/test_task_onboarding.py -q
python scripts/run_light_probe.py
python scripts/evaluate_pi_provider_matrix.py --provider codex-relay --model gpt-5.5 --thinking off
```

All commands passed.

### Verdict: APPROVED

---

## Code Review Round 3 — 2026-04-26

**Scope**: multi-task and multi-runtime validation matrix for the generic full-loop framework.
**Verification Status**: PASS

### Issues

Resolved issues:

- The first full Pi runtime matrix exposed that LLM cognition workers may produce scientifically meaningful labels that are outside the deterministic diagnosis contract.
- `pi_baidu_glm5/task006_near_neighbor` produced `problem_class = skill_use_improvement_not_structural`, which is a useful explanation but not an allowed `problem_class`.
- `pi_baidu_minimax_m25/task009_evaluator_gap` produced `recommended_next_worker = evaluator_repair_worker`, while the generic routing policy expects evaluator repair to route through `effectiveness_worker` or `adapter_repair_worker`.

### Changes

- `scripts/llm_full_loop_workers.py` now injects explicit diagnosis/routing vocabulary into cognition worker prompts.
- The LLM worker harness now applies semantic contract validation during the retry loop.
- On contract violation, verifier feedback is sent back to the same LLM worker for corrected JSON expression. The controller does not author or rewrite the research judgment.
- A formal runtime experiment matrix is persisted at `analysis/runtime_matrix/agent_runtime_experiment_matrix.yaml`.

### Matrix Evidence

```bash
python scripts/run_agent_runtime_matrix.py \
  --tasks task006_near_neighbor task008_bad_candidate task009_evaluator_gap task010_literature_required task011_portfolio_stop \
  --runtimes pi_gpt55 pi_baidu_glm5 pi_baidu_kimi_k25 pi_baidu_minimax_m25 \
  --max-workers 3 \
  --timeout 240
```

Result:

- `pi_gpt55`: 5/5 passed.
- `pi_baidu_glm5`: 5/5 passed.
- `pi_baidu_kimi_k25`: 5/5 passed.
- `pi_baidu_minimax_m25`: 5/5 passed.
- Total: 20/20 passed.

### Remaining Risks

- The proof is still fixture-level.
- Codex/OMX remains a blocked framework-callable runtime.
- The matrix proves artifact-chain and routing-contract robustness, not deep semantic equivalence among models.
- A future round should add semantic disagreement analysis across passed runtime outputs.

### Verdict: APPROVED

---

## Code Review Round 2 — 2026-04-26

**Scope**: agent runtime generalization cleanup after identifying Pi-specific worker-module coupling.
**Verification Status**: PASS

### Issues

Resolved issues:

- The previous Pi run path depended on a Pi-specific worker-module override, which made runtime switching look like a special-case worker replacement rather than a generic runtime harness configuration.
- Runtime definitions were duplicated between the runner and backend comparison report, creating drift risk.

### Changes

- Added registry-driven runtime selection through `configs/agent_runtimes/registry.yaml`.
- Added `scripts/backend_registry.py` as the single backend resolution helper.
- Added `scripts/llm_full_loop_workers.py` as a generic LLM worker runtime. Pi GPT-5.5 is now one backend config, not a separate worker architecture.
- Updated `scripts/run_generic_loop_engine.py` so `--backend pi_gpt55` resolves the worker module and runtime config automatically.
- Updated `scripts/compare_loop_backends.py` to read runtime profiles from the same registry.

### Execution Deviations

`--worker-module` still exists, but only as a debug override. Formal validation now uses `--backend` only.

Codex/OMX remains explicitly blocked in the registry because its framework-callable runner adapter is not implemented yet.

### Verification Evidence

```bash
python scripts/run_generic_loop_engine.py --task-adapter adapters/task006_near_neighbor.yaml --backend deterministic --run-intent full_loop_validation
python scripts/run_generic_loop_engine.py --task-adapter adapters/task006_near_neighbor.yaml --backend pi_gpt55 --run-intent full_loop_validation
python scripts/run_generic_loop_engine.py --task-adapter adapters/task008_bad_candidate.yaml --backend pi_gpt55 --run-intent full_loop_validation
python scripts/run_generic_loop_engine.py --task-adapter adapters/task009_evaluator_gap.yaml --backend pi_gpt55 --run-intent full_loop_validation
python scripts/verify_generic_full_loop.py --all
python scripts/compare_loop_backends.py --all
python scripts/validate_schemas.py --artifacts generic-full-loop-validation
python -m py_compile scripts/backend_registry.py scripts/llm_full_loop_workers.py scripts/run_generic_loop_engine.py scripts/compare_loop_backends.py
```

All commands passed.

### Verdict: APPROVED
