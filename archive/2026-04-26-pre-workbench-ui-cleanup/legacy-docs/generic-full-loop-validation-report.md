# Generic Full Loop Validation Report

Date: 2026-04-25

Updated: 2026-04-26

## Verdict

The current framework has reached `level_3_cross_task_agentic_full_loop` and now has Pi-runtime matrix evidence for fixture-level backend/model robustness.

This means the framework is no longer only an onboarding/readiness checker. It can run a generic `skill -> effectiveness -> cognition -> next decision` loop across multiple fixture task classes, and Pi-agent GPT-5.5 can act as real worker runtime for several of those classes through the same agent runtime registry path.

It does not yet prove Codex/OMX runtime support or research-quality autonomous cognition.

## Evidence

Primary reports:

- `analysis/full_loop_validation/generic_full_loop_validation_report.yaml`
- `analysis/full_loop_validation/backend_comparison_report.yaml`
- `analysis/runtime_matrix/agent_runtime_matrix_report.yaml`
- `analysis/runtime_matrix/agent_runtime_experiment_matrix.yaml`

Verified outcomes:

- `task006_near_neighbor`: deterministic full loop passed; Pi GPT-5.5 full loop passed.
- `task007_missing_runtime`: deterministic and Pi GPT-5.5 blocked routing passed.
- `task008_bad_candidate`: deterministic full loop passed; Pi GPT-5.5 full loop passed after generic JSON retry hardening.
- `task009_evaluator_gap`: deterministic full loop passed; Pi GPT-5.5 full loop passed.
- `task010_literature_required`: deterministic full loop passed; Pi GPT-5.5 full loop passed and routed to `literature_worker`.
- `task011_portfolio_stop`: deterministic full loop passed; Pi GPT-5.5 full loop passed and routed to `portfolio_worker`.

Runtime matrix outcome:

- Tasks: `task006_near_neighbor`, `task008_bad_candidate`, `task009_evaluator_gap`, `task010_literature_required`, `task011_portfolio_stop`.
- Runtimes: `pi_gpt55`, `pi_baidu_glm5`, `pi_baidu_kimi_k25`, `pi_baidu_minimax_m25`.
- Matrix result: 20/20 task-runtime cases passed.
- Entry point: `python scripts/run_agent_runtime_matrix.py --tasks ... --runtimes ...`.
- Case artifacts: `analysis/runtime_matrix/cases/{runtime}/{task}/`.

Agent runtime selection is now registry-driven:

- `configs/agent_runtimes/registry.yaml`
- `scripts/backend_registry.py`
- `scripts/llm_full_loop_workers.py`

The formal invocation is:

```bash
python scripts/run_generic_loop_engine.py --task-adapter adapters/task006_near_neighbor.yaml --backend pi_gpt55
```

`--worker-module` is retained only as a debug override. It is not the formal runtime switching mechanism.

The Pi GPT-5.5 worker artifacts are under:

- `analysis/full_loop_validation/runs/pi_gpt55/`
- `analysis/full_loop_validation/llm_worker_raw/pi_gpt55/`

The multi-runtime artifacts are under:

- `analysis/full_loop_validation/runs/pi_baidu_glm5/`
- `analysis/full_loop_validation/runs/pi_baidu_kimi_k25/`
- `analysis/full_loop_validation/runs/pi_baidu_minimax_m25/`
- `analysis/full_loop_validation/llm_worker_raw/{runtime}/`

## Harness Finding

Pi GPT-5.5 is usable as a bounded worker backend when constrained to structured JSON outputs and when the deterministic controller persists objects. The worker layer produced meaningful cognition judgments for:

- bounded skill-use improvement
- degraded candidate / skill-structure problem
- evaluator weakness
- evidence insufficiency requiring literature alignment
- research-value stop/pause routing

Two important contract failures were observed during the first multi-runtime matrix:

- `pi_baidu_glm5/task006_near_neighbor` produced a semantically meaningful but invalid `problem_class`: `skill_use_improvement_not_structural`.
- `pi_baidu_minimax_m25/task009_evaluator_gap` produced a semantically meaningful but invalid `recommended_next_worker`: `evaluator_repair_worker`.

The fix was not task-specific or model-specific. `scripts/llm_full_loop_workers.py` now gives cognition workers explicit allowed diagnosis/routing vocabulary and uses verifier feedback to request a corrected JSON object from the same worker. The controller still does not author the judgment.

After this generic harness repair, the full 5 task x 4 Pi runtime matrix passed.

## Boundaries

The controller still does not author downstream reasoning. It writes artifacts, verifies contracts, and routes from worker outputs.

The current proof is still fixture-level. The framework cannot yet claim:

- Level 4 including Codex/OMX framework-callable runtime
- Codex/OMX full-loop backend success
- cross-backend semantic equivalence beyond contract-level pass/fail
- Level 5 research-quality autonomous cognition

## Next Work

The next necessary step is not another task-specific replay. It is to strengthen the generic proof in two directions:

- implement or keep explicitly blocked Codex/OMX framework-callable worker runtime
- compare worker judgments semantically across passed Pi runtimes, not only artifact validity
- add disagreement adjudication for task/runtime combinations that pass contracts but diverge in scientific judgment
- graduate one fixture task into a real research-quality task to test Level 5 claims
