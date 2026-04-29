# Real LLM E2E Test Report - task006_near_neighbor

Date: 2026-04-29

## Scope

This run tested the real LLM-backed generic loop workflow, not the deterministic harness.

- Task/topic adapter: `adapters/task006_near_neighbor.yaml`
- Workflow entry: `scripts/run_generic_loop_engine.py`
- Runtime backend: `pi_baidu_glm5`
- Runtime profile: `pi:baidu-anthropic:glm-5`
- Workspace: `/tmp/daoshuguo-real-llm-e2e-task006`
- Raw LLM traces: `analysis/full_loop_validation/llm_worker_raw/pi_baidu_glm5/task.power.task006_near_neighbor/`

## Command

```bash
DAOSHUGUO_WRITE_TEMP_PI_CONFIG=1 python3 scripts/run_generic_loop_engine.py \
  --task-adapter adapters/task006_near_neighbor.yaml \
  --backend pi_baidu_glm5 \
  --workspace-root /tmp/daoshuguo-real-llm-e2e-task006
```

The successful run required network-enabled execution because the Pi runtime calls the configured LLM provider.

## Result

PASS.

`run.yaml` ended with:

- `status: completed`
- `backend: pi_baidu_glm5`
- `task_ref: task.power.task006_near_neighbor`
- `verification.status: passed`
- `verification.issues: []`

All standard phases completed:

- `skill_change_request`
- `skill_execution`
- `effectiveness_assessment`
- `cognition_diagnosis`
- `loop_routing_decision`

Supporting artifacts also existed:

- `diagnosis_input`
- `cognition_to_skill_update`
- `loop_review`
- `artifact_index.json`
- phase transition records `01` through `10`

## Evidence Summary

The raw worker records contain assistant text JSON and nonzero token usage after network-enabled execution. The earlier sandboxed run exposed `Connection error`; this was intentionally not accepted as success after fixing the JSON extractor to reject assistant error events.

Key persisted judgments:

- Skill request summary: candidate `+0.06` improvement is a bounded skill-use gain.
- Effectiveness assessment: baseline `0.72`, candidate `0.78`, delta `0.06`, no new constraint violations.
- Cognition diagnosis: `skill_use_problem`.
- Routing decision: continue to `skill_worker` with `continue_skill_evolution`.
- Next discriminating test: validate on at least one alternative grid topology.

## Fixes Needed To Run Real Backend

Two runtime files were restored/added:

- `scripts/pi_runtime.py`
- `scripts/llm_full_loop_workers.py`

The LLM worker extractor was tightened so Pi event JSON cannot be mistaken for an assistant-authored worker JSON object when the provider returns an error.

The repo-local Pi package also needed local dependency resolution for the Baidu Anthropic extension. A local ignored symlink was used:

- `pi-packages/daoshuguo-research-loop/node_modules -> /tmp/daoshuguo-pi-feasibility/pi-mono/node_modules`

This symlink is runtime-local and is ignored by git.

## Remaining Risks

This proves the real LLM/agent/workflow/task adapter path can complete one full loop. It does not prove research-quality skill improvement.

The result remains bounded by the task006 validation scenario. The cognition output correctly treats the result as skill-use improvement, not structural skill improvement or a publishable research claim.
