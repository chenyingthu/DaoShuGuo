---

## Code Review Round 1 — 2026-04-19

**Scope**: `plans/literature-excerpt-alignment-plan.md` 对应的当前实现状态审查，重点覆盖 `scripts/validate_schemas.py`、`orchestrator/main.py` 与文献对象/对齐链路
**Build Status**: PASS

### Issues

#### Issue 1 (High): 当前验证器没有校验新生成的文献与分析对象，计划中的质量门槛实际上未被证明
**File**: [validate_schemas.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/validate_schemas.py):74
当前校验器只收集 `schemas/core|assets|quality|reporting` 下的 schema，以及 `schemas/samples` 下的样例对象；真正运行时生成的对象，例如 `literature/sources/*.yaml`、`literature/papers/*.yaml`、`literature/cards/*/*.yaml`、`analysis/task001/**`、`cognition/cards/upgraded_*.yaml` 并未进入校验范围。这样会导致计划里“所有新增对象符合 schema”“新对象链条完整可回溯”等判断缺乏真实验证依据。
**Fix**: 扩展验证器，至少增加一个“artifact validation”模式，显式校验 `literature/`、`analysis/`、`cognition/cards` 中由本计划生成的对象，并对关键引用做存在性校验。

#### Issue 2 (High): explanation alignment 仍然主要基于卡片标签做判断，片段对象还没有真正参与关系判定
**File**: [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py):848
当前 `align_explanations()` 的 `relation` 判定只看本地认知 statement 中是否包含“问题本体”，以及 explanation card 的 `concept_tags` 是否包含 `reactive compensation` / `volt/var control`。虽然 `excerpt_relations` 已经被附着到输出对象，但这些 excerpt 内容并没有参与 `supports/supplements/unclear` 的实际判定逻辑。这意味着系统还没有真正达到计划中“片段级支持/补充/冲突判断”的要求，只是把片段当成附属证据列出来。
**Fix**: 将 relation 判定下沉到 excerpt 粒度，至少让 explanation point excerpt 的内容特征进入规则判断，并区分“卡片标签支持”和“片段内容支持”两种证据来源。

### Verdict: NEEDS_FIX

---

## Code Review Round 3 — 2026-04-19

**Scope**: 复核 artifact 级校验、excerpt 粒度对齐、计划 checklist 回填
**Build Status**: PASS

### Issues

#### Suggestion: `literature_source` 仍以 seed-curated 为主，尚未真正覆盖更真实输入类型
**File**: [main.py](/home/chenying/root-research/DaoShuGuo-v1/orchestrator/main.py):588
当前 `ingest-seed-literature()` 已经把 seed 文献物化为 `literature_source`，并且卡片生成优先从 source 层读取。但 `manual_summary`、`abstract_excerpt`、`fulltext_excerpt` 仍主要停留在 schema 支持层，尚未形成实际输入流程。这不阻塞当前计划闭环，但会限制下一阶段向更真实文献源推进的速度。
**Fix**: 在下一轮实现中优先增加至少一种非 `seed_curated` 的真实 source 输入路径，例如 `manual_summary`。

### Verdict: APPROVED

---

## Code Review Round 2 — 2026-04-19

**Scope**: 第二轮审查，重点复核 excerpt 粒度对齐、文献源对象层与计划状态回填
**Build Status**: PASS

### Issues

#### Issue 1 (High): 运行生成对象仍未进入统一校验范围，质量门槛依旧无法被完整证明
**File**: [validate_schemas.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/validate_schemas.py):74
第一轮指出的核心问题仍然存在。当前验证器依然只校验 `schemas/samples`，没有覆盖本计划真正新增和反复生成的对象，例如 `literature/sources/*.yaml`、`literature/papers/*.yaml`、`literature/cards/*/*.yaml`、`analysis/task001/**`、`cognition/cards/upgraded_*.yaml`。这意味着“所有新增对象符合 schema”这个验收项还没有被真实验证。
**Fix**: 为 `validate_schemas.py` 增加一个 artifact validation 模式，至少覆盖：
- `literature/sources`
- `literature/papers`
- `literature/excerpts`
- `literature/cards`
- `analysis/task001`
- `cognition/cards/upgraded_*`

#### Issue 2 (Medium): 计划 checklist 仍未根据当前实现状态回填，执行状态与代码状态脱节
**File**: [literature-excerpt-alignment-plan.md](/home/chenying/root-research/DaoShuGuo-v1/plans/literature-excerpt-alignment-plan.md):124
当前实现已经明显满足若干项，例如：
- source 层已被物化
- card 生成已优先从 source 层读取
- point excerpt 已生成
- explanation alignment 已保留 excerpt 粒度证据
- upgrade 已吸收 explanation alignment

但计划文件仍保留大量未勾选条目，导致计划不能真实反映当前阶段完成度。这会影响后续按计划持续推进和审查。
**Fix**: 在不高估完成度的前提下，按事实更新 checklist，只保留真正未完成的项，例如“更真实输入类型支持”和“统一 artifact validation”等。

### Verdict: NEEDS_FIX
