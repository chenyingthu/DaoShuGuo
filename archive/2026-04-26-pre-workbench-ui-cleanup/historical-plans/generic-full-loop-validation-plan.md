# Generic Full Loop Validation Plan

## Execution Status — 2026-04-25

Updated: 2026-04-26

Status: matrix completed and verified for the Pi runtime family.

Current proof level:

`level_3_cross_task_agentic_full_loop`

What is now proven:

- Six blind/new task packages can be onboarded through the same readiness layer.
- Deterministic full-loop artifacts are verified for normal, degraded-candidate, evaluator-gap, literature-required, and portfolio-stop fixture classes.
- Blocked runtime routing is verified for `task007_missing_runtime` without entering a full loop.
- Pi-agent GPT-5.5 through `codex-relay` produced verified full-loop artifact chains for:
  - `task006_near_neighbor`
  - `task008_bad_candidate`
  - `task009_evaluator_gap`
  - `task010_literature_required`
  - `task011_portfolio_stop`
- Pi-agent GPT-5.5 blocked routing is verified for `task007_missing_runtime`.
- A 5 task x 4 Pi runtime matrix passed through the same generic entrypoint and runtime registry:
  - tasks: `task006_near_neighbor`, `task008_bad_candidate`, `task009_evaluator_gap`, `task010_literature_required`, `task011_portfolio_stop`
  - runtimes: `pi_gpt55`, `pi_baidu_glm5`, `pi_baidu_kimi_k25`, `pi_baidu_minimax_m25`
  - result: 20/20 passed

What remains unproven:

- Level 4 backend-robust agentic full loop is not proven because Codex/OMX full-loop backend dispatch is not implemented.
- Level 5 research-quality autonomous cognition is not proven because the current agentic runs are fixture-level validation runs.
- Cross-runtime semantic equivalence is not proven; the matrix verifies artifact chains and routing contracts.

Key artifacts:

- `analysis/full_loop_validation/generic_full_loop_validation_report.yaml`
- `analysis/full_loop_validation/backend_comparison_report.yaml`
- `docs/generic-full-loop-validation-report.md`
- `reviews/generic-full-loop-validation-plan-review.md`
- `configs/agent_runtimes/registry.yaml`
- `scripts/llm_full_loop_workers.py`
- `analysis/runtime_matrix/agent_runtime_matrix_report.yaml`
- `analysis/runtime_matrix/agent_runtime_experiment_matrix.yaml`

Agent runtime architecture correction:

- Formal runtime switching is now through `--backend` and `configs/agent_runtimes/registry.yaml`.
- Pi GPT-5.5 no longer requires `--worker-module` in the normal path.
- `--worker-module` is retained only as a debug override.
- `codex_omx` is present in the registry as `blocked` until a framework-callable runner adapter exists.
- Pi provider/model/API/auth configuration remains delegated to Pi profiles; DaoShuGuo records runtime profiles but does not duplicate provider credentials or base URLs.

## 1. Plan Position

This is a framework-validation plan, not a task-optimization plan.

The previous `generic-task-onboarding-readiness-plan.md` proved one necessary condition:

> A task can be checked, diagnosed, and routed through a generic onboarding layer without task-specific framework code.

That is not enough.

The next question is harder:

> Can a new task complete a generic skill -> effectiveness -> cognition -> next decision research loop without adding task-specific framework code?

This plan defines how to test that claim.

It also tests whether Pi-agent using the same foundation model class as the current Codex session, currently GPT-5.5, is a better harness substrate for this framework than Codex/OMX-native execution.

## 2. Claim To Prove

The project must not claim mathematical universality over arbitrary tasks.

The strongest defensible claim is:

> For a defined family of power-research tasks satisfying the task package contract, the framework can onboard the task, execute at least one full skill-effectiveness-cognition loop, make an evidence-grounded next-step decision, and preserve auditable artifacts without modifying framework code.

This plan proves or falsifies that claim.

## 3. Task Family Boundary

### 3.1 In Scope

Tasks are in scope if they satisfy all conditions:

- They are power-system research or power-system-adjacent engineering research tasks.
- They can define `task.yaml`, `baseline.yaml`, `task_adapter.yaml`, and evaluator contract objects.
- They have measurable effectiveness criteria.
- They can expose candidate skill behavior through a runtime entry.
- They can produce baseline/candidate comparison evidence.
- They can support at least one cognition diagnosis based on evidence.
- They can be represented as data and adapter objects without new framework Python.

### 3.2 Out Of Scope

Tasks are out of scope for full-loop proof if:

- There is no evaluator or no meaningful measurable criterion.
- The task cannot produce baseline/candidate evidence.
- The task requires a new domain simulator before any framework loop can run.
- The task is purely narrative and has no effectiveness layer.
- The task requires private external data not available to the runtime.

Out-of-scope tasks are not failures of the loop. They must be routed to blocked/framing/repair states.

## 4. Non-Negotiable Principles

### 4.1 No Task-Specific Framework Code

Adding a new task may add:

- `tasks/{task_id}/...`
- `adapters/{task_id}.yaml`
- evaluator contract objects
- skill candidate files
- literature/evidence seed files
- task-specific runtime modules only if declared as task assets

Adding a new task must not require:

- new `if task_id == ...` logic in generic framework scripts
- new task-specific generic loop runner
- new task-specific verifier
- new task-specific cognition controller
- new task-specific portfolio controller

If new framework code is required, the result is:

`framework_gap_detected`

not:

`generic_loop_validated`

### 4.2 Controller Must Not Downstream-Reason

The loop controller may:

- schedule phases
- route artifacts
- validate contracts
- bind evidence
- write state

The loop controller must not:

- invent skill changes
- judge scientific value directly
- diagnose cognition itself
- reinterpret failed results as progress
- suppress negative effectiveness outcomes

Worker artifacts must carry worker reasoning.

### 4.3 Bad Results Must Be First-Class Outcomes

The loop is valid if it correctly handles:

- skill improvement
- skill degradation
- no-change outcomes
- insufficient evidence
- evaluator weakness
- task mismatch
- research-value pause
- blocked package

The loop is invalid if it only works when candidate metrics improve.

## 5. Required Loop Objects

To claim one full loop iteration, all of the following must exist:

1. `task_readiness_report`
2. `skill_change_request`
3. `skill_candidate` or `skill_change_result`
4. `effectiveness_assessment`
5. `cognition_diagnosis`
6. `loop_routing_decision`
7. `research_review`
8. `artifact_index`
9. `run_record`

Optional but preferred:

- `learning_need`
- `learning_context_pack`
- `literature_alignment`
- `deliverable_package`
- `claim_routing`
- `portfolio_assessment`

## 6. Backend Comparison

This plan treats execution backend as a core research variable.

### 6.1 Backend A: Codex/OMX-Native

Purpose:

Test whether the current Codex/OMX-native harness can execute the framework without legacy Claude wrappers.

Requirements:

- Use canonical skills under `/home/chenying/.codex/skills`.
- Do not use `~/.agents/skills`.
- Do not use `~/.claude/skills/codex/scripts/ask_codex.sh`.
- Use current Codex session and native subagents only when useful.
- Preserve all artifacts in repository-defined output paths.

### 6.2 Backend B: Pi-Agent With GPT-5.5

Purpose:

Test whether Pi-agent, configured with GPT-5.5 or the same current frontier model family used by Codex, is easier to harness for autonomous research loops.

Hypothesis:

Pi-agent may be more suitable for this project if it provides:

- more stable tool-calling loops
- clearer agent runtime harnessing
- more controllable prompt harnessing
- better separation between agent reasoning and deterministic tools
- easier state recovery
- less conflict with Codex's native safety/orchestration layers

Requirements:

- Verify a Pi agent profile for GPT-5.5 exists in Pi's own configuration.
- Record exact provider, model, thinking mode, and CLI invocation.
- Use the same task package, adapter, evaluator, and framework contracts as Backend A.
- Do not create Pi-only task logic; Pi should be selected through the generic agent runtime registry.
- Do not accept text-only Pi responses as full-loop proof unless required loop objects are written.

### 6.3 Backend C: Deterministic Baseline

Purpose:

Keep a non-agent baseline for falsification.

The deterministic baseline may execute fixed worker modules and produce valid schemas, but it must be labeled:

`deterministic_baseline`

It cannot be used as proof of autonomous cognition.

## 7. Validation Task Matrix

The proof requires a portfolio, not a single task.

### 7.1 Existing Anchor Tasks

#### task003

Role:

Near-neighbor skill loop anchor.

Expected outcome:

- Full loop should run.
- Improvement may be modest.
- Must distinguish skill-use tuning from skill-structure improvement.

Failure condition:

- The system claims structural skill progress from parameter-only gains.

#### task004

Role:

Boundary and claim-discipline anchor.

Expected outcome:

- Full loop should run or route to boundary-aware cognition.
- Must prevent hosting-capacity overclaim.
- Must distinguish internal report readiness from paper readiness.

Failure condition:

- The system treats secondary metric improvement as hosting-capacity breakthrough.

#### task005

Role:

Evaluator/standard weakness anchor.

Expected outcome:

- Should not blindly run skill evolution if claim gate or cost-benefit standard is weak.
- May route to framing/evaluator repair rather than full skill loop.

Failure condition:

- The system claims resilience progress without repairing effectiveness standards.

### 7.2 New Blind Fixture Tasks

These tasks must be created as task packages and adapters only.

#### task006_near_neighbor

Purpose:

Test near-neighbor generalization from task003/task004.

Suggested topic:

Reactive optimization under a different feeder condition or load envelope.

Expected result:

- Generic onboarding succeeds.
- Full loop runs under both Codex/OMX and Pi-agent.
- Candidate may or may not improve metrics.

#### task007_missing_runtime

Purpose:

Test blocked routing for incomplete packages.

Expected result:

- Onboarding detects missing runtime/evaluator support.
- No full loop is attempted.
- Failure is recorded as correct blocked outcome.

#### task008_bad_candidate

Purpose:

Test effectiveness gate protection.

Expected result:

- Candidate skill degrades metrics.
- Effectiveness worker rejects it.
- Cognition worker explains failure without upgrading it.
- Loop routing decision selects repair or stop.

#### task009_evaluator_gap

Purpose:

Test evaluator weakness detection.

Expected result:

- Task package is complete enough to run.
- Effectiveness worker identifies that metrics do not support the intended claim.
- Cognition routes to evaluator/standard repair.

#### task010_literature_required

Purpose:

Test whether cognition can use external/literature evidence.

Expected result:

- Cognition worker must produce learning needs.
- Literature/context worker must provide evidence seed or alignment.
- Final cognition must cite evidence levels.

#### task011_portfolio_stop

Purpose:

Test avoidance of local research traps.

Expected result:

- Loop may run once.
- Portfolio worker determines low continuation value.
- System stops or pauses instead of continuing mechanical iterations.

## 8. Test Matrix

Each valid task must be tested across backends.

| Task | Deterministic Baseline | Codex/OMX Native | Pi-Agent GPT-5.5 | Expected Class |
| --- | --- | --- | --- | --- |
| task003 | required | required | required | full loop |
| task004 | required | required | required | full loop with boundary claim |
| task005 | required | required | required | framing/evaluator route |
| task006_near_neighbor | required | required | required | blind full loop |
| task007_missing_runtime | required | required | required | blocked route |
| task008_bad_candidate | required | required | required | degradation handling |
| task009_evaluator_gap | required | required | required | evaluator repair |
| task010_literature_required | optional | required | required | learning/cognition |
| task011_portfolio_stop | optional | required | required | stop/pause decision |

## 9. Required Metrics

### 9.1 Framework Generality Metrics

- Number of new tasks added without framework code changes.
- Number of tasks requiring only data/adapter additions.
- Number of generic scripts reused across all tasks.
- Number of task-specific branches detected in framework code.
- Number of blocked tasks correctly diagnosed.

### 9.2 Loop Completeness Metrics

- Percentage of runs producing all required loop objects.
- Percentage of runs with valid schema artifacts.
- Percentage of runs with complete evidence back-links.
- Number of successful loop resumes after interruption.
- Number of loop decisions that correctly stop, repair, or continue.

### 9.3 Cognition Quality Metrics

- Whether cognition distinguishes:
  - skill-use improvement
  - skill-structure improvement
  - task mismatch
  - evaluator weakness
  - evidence insufficiency
- Whether cognition cites evidence artifacts.
- Whether cognition avoids overclaim.
- Whether cognition creates actionable next-step requests.
- Whether cognition uses external/literature evidence when required.

### 9.4 Effectiveness Quality Metrics

- Baseline/candidate comparison exists.
- Candidate degradation is detected.
- Missing standard is detected.
- Claim gate affects routing.
- Effectiveness result can veto cognition upgrade.

### 9.5 Backend Harness Metrics

For Codex/OMX-native and Pi-agent GPT-5.5:

- tool-call success rate
- loop completion rate
- malformed artifact rate
- retry count
- context leakage or task-specific shortcut count
- state recovery success
- average human intervention count
- evidence quality score
- reproducibility across two runs

## 10. Phases

### Phase 1: Proof Contract And Test Harness Spec

Deliverables:

- `docs/generic-full-loop-validation.md`
- `schemas/quality/full_loop_validation_report.schema.yaml`
- `schemas/quality/backend_comparison_report.schema.yaml`
- sample objects for both schemas
- artifact set `generic-full-loop-validation`

Acceptance:

- The proof claim, task family boundary, loop object requirements, and backend comparison rules are documented.
- Schema validation includes the new report types.

### Phase 2: Generic Full-Loop Verifier

Deliverables:

- `scripts/verify_generic_full_loop.py`
- `scripts/compare_loop_backends.py`

Verifier must check:

- all required loop objects exist
- object refs resolve
- no task-specific framework branch exists for blind tasks
- controller did not write worker-only reasoning artifacts
- effectiveness can veto cognition upgrade
- blocked tasks do not enter full loop

Acceptance:

```bash
python scripts/verify_generic_full_loop.py --task task003 --backend deterministic
python scripts/verify_generic_full_loop.py --task task004 --backend deterministic
python scripts/compare_loop_backends.py --help
```

### Phase 3: Backend Adapter Normalization

Deliverables:

- generic agent runtime harness contract
- Codex/OMX runtime harness entry
- Pi-agent runtime harness entry
- deterministic runtime harness entry

Backend adapter fields:

- `backend_id`
- `provider`
- `model`
- `thinking_mode`
- `runner_entry`
- `tool_call_mode`
- `state_root`
- `artifact_root`
- `known_limitations`

Pi-agent GPT-5.5 requirements:

- Add or verify Pi model profile for GPT-5.5.
- Record provider config source without leaking secrets.
- Run text-only, single-tool, and full-loop smoke tests.
- Store results under `analysis/backend_matrix/pi_gpt55/`.

Acceptance:

```bash
python scripts/evaluate_pi_provider_matrix.py --provider openai --model gpt-5.5
python scripts/compare_loop_backends.py --list-backends
```

If `gpt-5.5` is not accepted by Pi/provider config, the run must produce:

`backend_blocked_model_unavailable`

not silent fallback.

### Phase 4: Blind Task Package Set

Deliverables:

- `tasks/task006_near_neighbor/`
- `tasks/task007_missing_runtime/`
- `tasks/task008_bad_candidate/`
- `tasks/task009_evaluator_gap/`
- `tasks/task010_literature_required/`
- `tasks/task011_portfolio_stop/`
- matching adapters

Rules:

- Add task data and adapters only.
- Do not add new framework code for each task.
- If a task requires a domain runtime asset, declare it as task/runtime asset and bind through adapter.
- All new tasks must pass generic onboarding or produce blocked readiness.

Acceptance:

```bash
python scripts/run_task_onboarding_check.py --task task006_near_neighbor
python scripts/run_task_onboarding_check.py --task task007_missing_runtime
python scripts/run_task_onboarding_check.py --task task008_bad_candidate
python scripts/run_task_onboarding_check.py --task task009_evaluator_gap
python scripts/run_task_onboarding_check.py --task task010_literature_required
python scripts/run_task_onboarding_check.py --task task011_portfolio_stop
```

### Phase 5: Deterministic Baseline Runs

Purpose:

Separate schema/framework validity from agent autonomy.

Deliverables:

- deterministic full-loop artifacts for task003/task004/task005/task006/task008/task009
- baseline validation report

Acceptance:

```bash
python scripts/run_generic_loop_engine.py --task-adapter adapters/task003.yaml --backend deterministic
python scripts/run_generic_loop_engine.py --task-adapter adapters/task004.yaml --backend deterministic
python scripts/verify_generic_full_loop.py --task task003 --backend deterministic
python scripts/verify_generic_full_loop.py --task task004 --backend deterministic
```

### Phase 6: Codex/OMX-Native Agent Runs

Purpose:

Test whether canonical Codex/OMX can run full loops without legacy wrappers.

Deliverables:

- Codex/OMX full-loop artifacts
- Codex/OMX backend report
- failure report for any blocked task

Acceptance:

```bash
python scripts/run_research_pipeline.py --task task003 --backend codex_omx --iterations 1
python scripts/run_research_pipeline.py --task task004 --backend codex_omx --iterations 1
python scripts/verify_generic_full_loop.py --task task003 --backend codex_omx
python scripts/verify_generic_full_loop.py --task task004 --backend codex_omx
```

If current scripts do not support `--backend`, this phase must first introduce a generic backend dispatch layer. That change is framework code and is allowed because it generalizes the framework rather than serving one task.

### Phase 7: Pi-Agent GPT-5.5 Runs

Purpose:

Test whether Pi-agent with GPT-5.5 can execute the same full-loop contracts more reliably or cleanly.

Deliverables:

- Pi GPT-5.5 backend profile
- Pi GPT-5.5 smoke matrix
- Pi GPT-5.5 full-loop artifacts for task003/task004/task006
- Pi GPT-5.5 blocked/repair artifacts for task005/task007/task008/task009
- Pi GPT-5.5 backend comparison report

Required tests:

1. text-only smoke
2. single tool-call smoke
3. state write smoke
4. task onboarding read smoke
5. one full deterministic-assisted loop
6. one full agentic loop
7. one degraded candidate loop
8. one blocked task route

Acceptance:

```bash
python scripts/evaluate_pi_provider_matrix.py --provider openai --model gpt-5.5
python scripts/run_research_pipeline.py --task task003 --backend pi_gpt55 --iterations 1
python scripts/run_research_pipeline.py --task task004 --backend pi_gpt55 --iterations 1
python scripts/verify_generic_full_loop.py --task task003 --backend pi_gpt55
python scripts/verify_generic_full_loop.py --task task004 --backend pi_gpt55
python scripts/compare_loop_backends.py --tasks task003 task004 task006_near_neighbor --backends codex_omx pi_gpt55
```

### Phase 8: Cross-Task Proof Report

Deliverables:

- `analysis/full_loop_validation/generic_full_loop_validation_report.yaml`
- `analysis/full_loop_validation/backend_comparison_report.yaml`
- `docs/generic-full-loop-validation-report.md`

The report must answer:

- Which task classes are validated?
- Which task classes are blocked?
- Which failures are correct framework behavior?
- Which failures expose framework gaps?
- Is Pi-agent GPT-5.5 better than Codex/OMX for this harness?
- What cannot yet be claimed?

Acceptance:

```bash
python scripts/validate_schemas.py --artifacts generic-full-loop-validation
python scripts/verify_generic_full_loop.py --all
python scripts/compare_loop_backends.py --all
```

## 11. Proof Levels

### Level 0: Onboarding Only

Task package can be diagnosed.

Current project status after `generic-task-onboarding-readiness-plan`.

### Level 1: Deterministic Full Loop

All loop artifacts can be produced by deterministic workers.

Proves schema and controller structure, not agent autonomy.

### Level 2: Single Agentic Full Loop

One backend can complete full loop on one task.

Proves feasibility, not generality.

### Level 3: Cross-Task Agentic Full Loop

One backend can complete correct outcomes across at least four task classes:

- normal full loop
- blocked task
- degraded candidate
- evaluator gap

Proves framework generality within limited task family.

### Level 4: Backend-Robust Agentic Full Loop

Two independent backends, Codex/OMX and Pi-agent GPT-5.5, produce compatible decisions on the same task matrix.

This is the first level where the project may claim:

> The framework design is not merely an artifact of one agent runtime.

### Level 5: Research-Quality Autonomous Loop

The system produces:

- credible skill change
- credible effectiveness assessment
- evidence-grounded cognition
- proper claim boundary
- useful next research decision
- possible deliverable routing

This is the level required before claiming the framework helps generate high-quality research outcomes.

## 12. Stop Conditions

Stop and report framework gap if:

- a blind task requires task-specific framework Python
- the controller writes cognition in place of cognition worker
- effectiveness failure is ignored
- Pi-agent only emits prose and no required objects
- Codex/OMX or Pi backend silently changes model/provider
- task-specific branches are introduced to pass tests
- schema validation passes but evidence refs are missing

Stop and report task gap if:

- evaluator cannot be defined
- baseline cannot be defined
- metrics cannot support claim
- task has no meaningful candidate skill surface

## 13. Final Acceptance Criteria

This plan is complete only when:

1. At least six tasks are onboarded through the same readiness CLI.
2. At least four task classes are represented:
   - valid full loop
   - blocked task
   - degraded candidate
   - evaluator/claim gap
3. At least one blind new task completes a full loop without framework code changes.
4. At least one blind new task is correctly blocked without framework code changes.
5. Codex/OMX-native backend has at least one verified full loop.
6. Pi-agent GPT-5.5 backend has either:
   - at least one verified full loop, or
   - a documented `backend_blocked_*` report explaining why not.
7. Backend comparison report exists.
8. Generic full-loop validation report exists.
9. The report explicitly states what has not been proven.
10. No legacy `.agents` or `.claude` wrapper path is used.

## 14. Expected Conclusions

The likely outcomes are:

### Outcome A: Framework Validated, Pi Better

Pi-agent GPT-5.5 completes the same loop with fewer harness failures and cleaner state.

Conclusion:

Use Pi-agent as the primary runtime backend for future research loops, with Codex/OMX as engineering and review environment.

### Outcome B: Framework Validated, Codex/OMX Better

Codex/OMX completes the loop more reliably.

Conclusion:

Keep Pi as experimental backend and strengthen Codex-native skill/cognition worker design.

### Outcome C: Both Backends Fail For Same Reason

Both fail at object contracts, evaluator weakness, or worker boundary.

Conclusion:

The framework design is incomplete. Fix contracts and loop controller before more task testing.

### Outcome D: Backends Disagree Semantically

Both run, but produce different cognition or routing decisions.

Conclusion:

This is valuable. The project needs adjudication, evidence weighting, and backend disagreement analysis.

## 15. Immediate Next Step

Before implementation, review this plan against three questions:

1. Does it test framework generality rather than task-specific replay?
2. Does it test agentic cognition rather than deterministic templates?
3. Does it make Pi-agent GPT-5.5 a real backend comparison rather than a side experiment?

If yes, execute this plan with `$plan-execute plans/generic-full-loop-validation-plan.md`.
