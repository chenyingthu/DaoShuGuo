## Code Review Round 1 — 2026-04-21

**Scope**: `plans/framework-validation-capability-absorption-plan.md` 第一轮实现审查，覆盖 preflight / light probe、experiment index、diagnosis memory 及其接入 integration checks
**Build Status**: PASS

### Issues

无 High/Critical 问题。

### Notes

- 已新增：
  - [run_preflight_checks.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/run_preflight_checks.py)
  - [run_light_probe.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/run_light_probe.py)
  - [build_experiment_index.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/build_experiment_index.py)
  - [update_diagnosis_memory.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/update_diagnosis_memory.py)
- 已形成：
  - [preflight_report.json](/home/chenying/root-research/DaoShuGuo-v1/analysis/preflight/preflight_report.json)
  - [light_probe.json](/home/chenying/root-research/DaoShuGuo-v1/analysis/preflight/light_probe.json)
  - [experiment_index.json](/home/chenying/root-research/DaoShuGuo-v1/analysis/experiment_index.json)
  - [experiment_index.md](/home/chenying/root-research/DaoShuGuo-v1/analysis/experiment_index.md)
  - [diagnosis_memory.jsonl](/home/chenying/root-research/DaoShuGuo-v1/memory/diagnosis_memory.jsonl)
- 这些能力都保持为辅层，没有重造 task/run/evidence/cognition 主对象。
- `scripts/run_integration_checks.py` 已纳入这四个新脚本，且不破坏 task002/003/004 主线验证。

### Verification

- `python -m py_compile scripts/run_preflight_checks.py scripts/run_light_probe.py scripts/build_experiment_index.py scripts/update_diagnosis_memory.py`
- `python scripts/run_preflight_checks.py`
- `python scripts/run_light_probe.py`
- `python scripts/build_experiment_index.py`
- `python scripts/update_diagnosis_memory.py`
- `python scripts/run_integration_checks.py`

### Remaining Scope

- 当前 preflight / light probe 仍然很轻，只做最必要的 readiness 判断。
- experiment index 目前是 artifact 清单层，还未扩展到“推荐路径”或“best known path”。
- diagnosis memory 目前以 failure cognition 回填为主，尚未进入更复杂的检索/推荐流程。

### Verdict: APPROVED
