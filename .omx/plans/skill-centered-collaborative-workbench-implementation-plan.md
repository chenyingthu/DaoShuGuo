# Skill-Centered Collaborative Workbench Implementation Plan

## 1. Requirements Summary

DaoShuGuo must move from a topic-centered collaborative workbench to a skill-centered research workbench.

The guiding principle is:

```text
topic 是研究容器
skill 是推进对象
effectiveness 是评价门
cognition 是结构化解释
human decision 是技能迭代路由约束
```

The next implementation must make this visible and actionable for `real-task-001` first, without hardcoding all conclusions into the UI. Existing research artifacts already answer the core skill questions and should be aggregated into workbench objects.

Key source evidence:

- [docs/skill-centered-workbench-synthesis-2026-04-26.md](/home/chenying/root-research/DaoShuGuo-v1/docs/skill-centered-workbench-synthesis-2026-04-26.md:9) establishes that research progress should be organized around skill work.
- [docs/skill-centered-workbench-synthesis-2026-04-26.md](/home/chenying/root-research/DaoShuGuo-v1/docs/skill-centered-workbench-synthesis-2026-04-26.md:23) identifies the current target skill as `skill.power.renewable_capacity_optimizer_task004`.
- [docs/skill-centered-workbench-synthesis-2026-04-26.md](/home/chenying/root-research/DaoShuGuo-v1/docs/skill-centered-workbench-synthesis-2026-04-26.md:37) lists the method families and their skill dimensions.
- [docs/skill-centered-workbench-synthesis-2026-04-26.md](/home/chenying/root-research/DaoShuGuo-v1/docs/skill-centered-workbench-synthesis-2026-04-26.md:58) records that current gains are not verified structural skill improvement.
- [docs/skill-centered-workbench-synthesis-2026-04-26.md](/home/chenying/root-research/DaoShuGuo-v1/docs/skill-centered-workbench-synthesis-2026-04-26.md:82) breaks the next structural skill request into method, process, and standard changes.
- [docs/skill-centered-workbench-synthesis-2026-04-26.md](/home/chenying/root-research/DaoShuGuo-v1/docs/skill-centered-workbench-synthesis-2026-04-26.md:143) records the current effectiveness evidence: primary delta 0, boundary not triggered, secondary gains, increased control effort.
- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:177) currently aggregates `real-task-001` mainly from taste, delivery, effectiveness, and cognition diagnosis.
- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:293) currently creates a claim-boundary attention item, not a skill-centered attention queue.
- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:363) currently builds a researcher lens around claim/taste/blocking issue, not active skill/method/process/standard.
- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:574) already compiles human objects into routing constraints, but constraints are currently stage-generic.

## 2. Design Principles

1. **Skill First**
   The first workbench screen must answer what skill is being improved, what dimension changed, and whether the evidence supports structural improvement.

2. **Evidence Before Narrative**
   UI labels and briefs must be derived from YAML/JSON artifacts wherever possible. Natural-language summaries must point back to object IDs and source paths.

3. **No Claim Inflation**
   Operational-quality gains, readable briefs, or UI improvements must not be displayed as primary hosting-capacity or verified structural skill improvement.

4. **Human Decisions Must Route Skill Work**
   Human feedback should compile into constraints for the next `skill_worker`, not only into generic loop notes.

5. **Keep The Backend Thin**
   Do not rebuild evaluator, loop engine, onboarding, or Pi runtime inside the workbench. The workbench aggregates, displays, writes decisions, and compiles constraints.

## 3. RALPLAN-DR Summary

### Principles

- Make skill progression, not topic metadata, the first-class visible object.
- Preserve deterministic evidence grounding before adding LLM-authored briefs.
- Keep the first UI local/file-backed to avoid product architecture drift.
- Make every human action produce an auditable object and routing impact.

### Decision Drivers

1. **Research Correctness**
   The workbench must not misclassify skill-use observations as structural skill improvement.

2. **Interaction Value**
   A researcher should understand the skill status without opening raw YAML, while still being able to audit the evidence.

3. **Implementation Momentum**
   Reuse current scripts and `workbench_data/` instead of introducing new platform infrastructure.

### Viable Options

#### Option A: Extend Existing File-Backed Workbench First

Add skill-chain aggregation to `scripts/workbench_common.py`, generate skill-centered JSON/YAML artifacts, update briefs and constraints, then build a minimal local UI/API.

Pros:

- Lowest risk to existing verification.
- Uses current scripts and artifact layout.
- Makes the skill-centered model visible quickly.

Cons:

- `workbench_common.py` may grow too broad if not factored carefully.
- File-backed API may need refactoring later.

#### Option B: Build A New Workbench Backend Package First

Create a new `workbench/` Python package with modules for sources, skill lens, API, and UI.

Pros:

- Cleaner long-term separation.
- Easier to test unit-by-unit.

Cons:

- More upfront architecture before user-visible value.
- Risks duplicating existing file-backed helpers.

#### Option C: Build Static UI Directly From Existing JSON

Skip backend changes and build a UI that reads current `cockpit.json`, `researcher_lens.json`, and briefs.

Pros:

- Fastest visible UI.
- Minimal backend risk.

Cons:

- Current JSON lacks skill-centered fields.
- UI would need hardcoded or inferred skill logic, violating evidence-first design.

### Favored Option

Option A.

It gives the minimum coherent path: first enrich the existing workbench object layer with skill-centered aggregation, then expose it through a small UI/API.

## 4. Architecture

### 4.1 Active Data Flow

```text
analysis/real_task_001/literature/*.yaml
analysis/real_task_001/reframing/*.yaml
analysis/real_task_001_upgrade/reports/*.yaml
analysis/real_task_001_upgrade/delivery/*.yaml
        |
        v
scripts/workbench_common.py skill aggregation helpers
        |
        v
workbench_data/topics/{topic}/skill_cockpit.json
workbench_data/topics/{topic}/skill_progression.json
workbench_data/topics/{topic}/researcher_lens.json
workbench_data/attention/*.yaml
workbench_data/briefs/*.yaml
        |
        v
file-backed API / static UI
        |
        v
human decision object
        |
        v
routing_constraint targeting next skill worker
```

### 4.2 New Workbench Artifacts

First implementation can use JSON outputs before adding new schemas:

- `workbench_data/topics/{topic}/skill_cockpit.json`
- `workbench_data/topics/{topic}/skill_progression.json`
- `workbench_data/topics/{topic}/skill_judgment_card.json`

If these stabilize, add schema objects later:

- `skill_workbench_summary`
- `skill_progression_event`
- `skill_judgment_card`

Do not add schema until the JSON shape proves useful.

### 4.3 Source Artifacts To Aggregate

For `real-task-001`, aggregate these:

- `analysis/real_task_001/literature/method_family_map.yaml`
- `analysis/real_task_001/literature/metric_taxonomy.yaml`
- `analysis/real_task_001/literature/claim_thresholds.yaml`
- `analysis/real_task_001/literature/experiment_design_recommendation.yaml`
- `analysis/real_task_001/reframing/skill_structure_diagnosis.yaml`
- `analysis/real_task_001/reframing/structural_skill_change_request.yaml`
- `analysis/real_task_001_upgrade/reports/upgrade_effectiveness_assessment.yaml`
- `analysis/real_task_001_upgrade/reports/upgrade_cognition_diagnosis.yaml`
- `analysis/real_task_001_upgrade/reports/upgrade_loop_review.yaml`
- `analysis/real_task_001_upgrade/delivery/taste_assessment.yaml`

If any artifact is missing, the workbench should degrade gracefully:

- status: `degraded`
- missing source list
- human attention item asking whether to repair evidence before continuing

## 5. Implementation Steps

### Step 1: Add Skill Source Loading Helpers

Files:

- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:131)

Add helpers:

```python
def real_task_skill_sources(topic_id: str) -> dict[str, Any]:
    ...

def build_skill_cockpit(topic: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
    ...

def build_skill_progression(topic: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
    ...

def build_skill_judgment_card(topic: dict[str, Any], sources: dict[str, Any]) -> dict[str, Any]:
    ...
```

Expected behavior:

- For `real-task-001`, load the source artifacts listed above.
- For other topics, produce a degraded but valid skill cockpit:
  - `active_skill_ref: unknown`
  - `skill_status: insufficient_skill_evidence`
  - `missing_sources: [...]`
- Do not fail the whole topic build if one optional artifact is missing.

Acceptance criteria:

- `python scripts/build_workbench_topic.py --topic real-task-001 --dry-run` returns successfully.
- `skill_cockpit` contains:
  - `active_skill_ref`
  - `candidate_family`
  - `candidate_dimension`
  - `skill_status`
  - `method_changes`
  - `process_changes`
  - `standard_changes`
  - `forbidden_shortcuts`
  - `required_validation`
  - `metric_evidence`
  - `next_worker`
  - `next_action`
  - `source_refs`

### Step 2: Write Skill-Centered Topic Outputs

Files:

- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:399)
- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:416)

Update `build_topic_bundle()` to include:

```python
"skill_cockpit": skill_cockpit,
"skill_progression": skill_progression,
"skill_judgment_card": skill_judgment_card,
```

Update `write_topic_bundle()` to write:

```text
workbench_data/topics/{topic}/skill_cockpit.json
workbench_data/topics/{topic}/skill_progression.json
workbench_data/topics/{topic}/skill_judgment_card.json
```

Acceptance criteria:

- Running `python scripts/build_workbench_topic.py --topic real-task-001` creates the three files.
- Existing files continue to be produced:
  - `cockpit.json`
  - `timeline.json`
  - `evidence_graph.json`
  - `human_attention_queue.json`
  - `researcher_lens.json`

### Step 3: Update Researcher Lens Around Skill Status

Files:

- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:363)
- [workbench_data/topics/real-task-001/researcher_lens.yaml](/home/chenying/root-research/DaoShuGuo-v1/workbench_data/topics/real-task-001/researcher_lens.yaml:1)

Change `researcher_lens()` to accept `skill_cockpit`.

Add to `executive_layer`:

- `active_skill_ref`
- `candidate_family`
- `skill_status`
- `primary_metric_delta`
- `boundary_triggered`
- `control_effort_delta`

Add to `research_layer`:

- `method_changes`
- `process_changes`
- `standard_changes`
- `skill_use_vs_structure_judgment`
- `forbidden_shortcuts`
- `required_validation`
- `human_skill_questions`

Add to `audit_layer`:

- source artifact refs
- object refs from skill chain

Acceptance criteria:

- `researcher_lens.real-task-001` answers these without opening raw YAML:
  - current active skill
  - why this is not verified structural improvement
  - what evidence blocks stronger claim
  - what next skill worker should do

### Step 4: Replace Claim-Only Attention With Skill-Centered Attention

Files:

- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:293)

Generate multiple attention items for `real-task-001`:

1. `skill_direction`
   - Should `voltage_sensitivity_q_allocation` remain the next skill direction?

2. `scenario_boundary`
   - Should the next iteration first repair boundary-triggering scenario evidence?

3. `effort_gate`
   - Should control effort be a hard gate?

4. `claim_boundary`
   - Should claim remain at internal technical note / diaomu?

Each item must include:

- `why_human_needed`
- `agent_recommendation`
- `evidence_refs`
- `allowed_actions`
- `writeback_object_type`

Acceptance criteria:

- `workbench_data/topics/real-task-001/human_attention_queue.json` includes skill-centered questions.
- Existing validation still passes.

### Step 5: Make Briefs Skill-Centered

Files:

- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:652)

Update `build_briefs()` to incorporate `skill_cockpit`.

Mentor brief must include:

- active skill
- candidate family
- method/process/standard changes
- current evidence judgment
- what is not proven
- next skill question

Claim brief must include:

- supported claim: structural attempt with operational-quality gain
- forbidden claims:
  - verified structural skill improvement
  - hosting-capacity boundary improvement
  - paper-candidate result

Failure brief must explain:

- primary metric did not improve
- boundary not triggered
- control effort increased
- why that is useful diagnostic evidence

Acceptance criteria:

- `python scripts/build_research_communication_briefs.py --topic real-task-001` produces briefs where the main narrative is skill-centered.
- Briefs do not say that UI/communication improvement is scientific improvement.

### Step 6: Compile Human Decisions Into Skill Worker Constraints

Files:

- [scripts/workbench_common.py](/home/chenying/root-research/DaoShuGuo-v1/scripts/workbench_common.py:574)

Extend default `direction_override` and `iteration_steering` objects for skill-centered defaults:

Default `direction_override` should be about:

- target worker: `skill_worker`
- must do:
  - compare `voltage_sensitivity_q_allocation` against `uniform_q_support`
  - use equal or bounded control effort
  - run extended-until-violation / boundary-neighborhood scenario
- must not do:
  - q_step-only escalation
  - secondary-metric overclaim
  - boundary claim without `boundary_triggered=true`

Extend `compile_constraints()` output so constraints can include:

- `applies_to_stage: skill`
- `target_worker: skill_worker`
- `constraint_type: must_do | must_not_do | require_evidence | claim_limit`

If schema does not yet allow `target_worker`, either:

- add it under `metadata`, or
- update `routing_constraint.schema.yaml` conservatively.

Acceptance criteria:

- `python scripts/compile_human_decision_constraints.py --topic real-task-001 --dry-run` shows constraints that explicitly target next skill work.
- `python scripts/verify_workbench_loop_integration.py --topic real-task-001 --dry-run` still passes.

### Step 7: Add A Minimal File-Backed API

Files:

- Add `scripts/serve_workbench_api.py`

Use only Python standard library unless a current dependency already exists.

Endpoints:

```text
GET /topics
GET /topics/{topic}/cockpit
GET /topics/{topic}/skill-cockpit
GET /topics/{topic}/skill-progression
GET /topics/{topic}/briefs
GET /topics/{topic}/evidence-graph
GET /topics/{topic}/human-attention-queue
GET /topics/{topic}/loop-context
POST /topics/{topic}/direction-override
POST /topics/{topic}/compile-constraints
```

POST implementation can call the existing writer/compiler functions directly.

Acceptance criteria:

- `curl http://localhost:<port>/topics` returns topic list.
- `curl http://localhost:<port>/topics/real-task-001/skill-cockpit` returns the skill cockpit object.
- POST direction override writes a new YAML object or supports a documented dry-run mode.

### Step 8: Add Minimal Researcher UI

Files:

- Add `workbench_ui/index.html`
- Add `workbench_ui/app.js`
- Add `workbench_ui/styles.css`

UI sections:

1. Topic selector.
2. Skill-centered cockpit header.
3. Skill judgment card.
4. Method / process / standard columns.
5. Metric evidence cards.
6. Skill progression strip.
7. Human attention queue.
8. Mentor brief.
9. Evidence graph simplified list.
10. Direction override form.
11. Routing constraints / loop context preview.

No landing page. The first screen is the workbench.

Acceptance criteria:

- Opens `real-task-001` by default.
- First viewport shows active skill, candidate family, skill status, boundary status, and next action.
- Text does not present secondary metric improvement as primary skill improvement.
- UI can submit or dry-run a direction override through the API.

### Step 9: Add Targeted Verification

Files:

- Add `scripts/verify_skill_centered_workbench.py`
- Optionally add `tests/test_skill_centered_workbench.py`

Verification checks:

- `skill_cockpit.json` exists for `real-task-001`.
- `active_skill_ref == skill.power.renewable_capacity_optimizer_task004`.
- `candidate_family == voltage_sensitivity_q_allocation`.
- `skill_status` is not `verified_structural_improvement`.
- `primary_delta == 0.0`.
- `boundary_triggered is false`.
- `forbidden_claims` includes verified structural skill improvement and hosting-capacity boundary improvement.
- human attention queue includes at least one skill-direction question.
- generated constraints include skill-worker relevant content.

Acceptance criteria:

- `python scripts/verify_skill_centered_workbench.py --topic real-task-001` passes.
- Existing workbench verification commands continue to pass.

### Step 10: Update Documentation

Files:

- Update [docs/skill-centered-workbench-synthesis-2026-04-26.md](/home/chenying/root-research/DaoShuGuo-v1/docs/skill-centered-workbench-synthesis-2026-04-26.md:217) with implementation status.
- Add `docs/skill-centered-workbench-usage.md`.

Usage doc must explain:

- how to rebuild workbench topic data
- how to start API server
- how to open UI
- how to write a direction override
- how to verify that routing constraints changed
- how to interpret skill-use vs structural improvement status

## 6. Acceptance Criteria

### Minimum Acceptance

- `real-task-001` generates `skill_cockpit.json`, `skill_progression.json`, and `skill_judgment_card.json`.
- Researcher lens includes active skill, candidate family, skill-use vs structure judgment, and next skill-worker action.
- Human attention queue includes skill-centered questions.
- Mentor brief is skill-centered.
- Direction override compiles into constraints relevant to next skill work.
- Existing workbench verification passes.

### Good Acceptance

- Minimal API serves all required topic and skill cockpit endpoints.
- UI opens `real-task-001` by default and makes skill status visible in the first viewport.
- UI can write or dry-run a direction override and show routing impact.
- Verification script catches accidental claim inflation.

### High-Quality Acceptance

- Researcher can answer, from the UI alone:
  - What skill is being improved?
  - What is the candidate method family?
  - What changed in method/process/standard?
  - Why is this not verified structural improvement?
  - What must the next skill worker do?
  - What claims are forbidden?
- A human decision visibly changes `loop_context.json` or routing constraints.
- The UI supports executive/research/audit drilldown without becoming a YAML browser.

## 7. Verification Commands

Run after implementation:

```bash
python scripts/build_workbench_topic.py --topic real-task-001
python scripts/build_researcher_lens.py --topic real-task-001
python scripts/build_research_communication_briefs.py --topic real-task-001
python scripts/verify_workbench_topic.py --topic real-task-001
python scripts/verify_workbench_topic.py --topic task003
python scripts/verify_workbench_topic.py --topic synthetic-topic-fixture
python scripts/verify_researcher_lens.py --topic real-task-001
python scripts/verify_research_communication_briefs.py --topic real-task-001
python scripts/compile_human_decision_constraints.py --topic real-task-001 --dry-run
python scripts/verify_workbench_loop_integration.py --topic real-task-001 --dry-run
python scripts/validate_schemas.py --artifacts workbench
python scripts/verify_skill_centered_workbench.py --topic real-task-001
```

For UI/API:

```bash
python scripts/serve_workbench_api.py --port 8765
curl http://localhost:8765/topics
curl http://localhost:8765/topics/real-task-001/skill-cockpit
```

If Playwright or browser tooling is available:

- load UI at local URL
- screenshot desktop and mobile
- verify first viewport contains active skill, candidate family, skill status, and attention queue
- test direction override form

## 8. Risks And Mitigations

### Risk: Workbench Becomes Another YAML Viewer

Mitigation:

- UI first viewport must show skill judgment, not raw YAML.
- Raw artifact paths appear only in audit/drilldown.

### Risk: Claim Inflation

Mitigation:

- Verification script asserts no `verified_structural_improvement` status for current evidence.
- Claim brief must include forbidden claims from taste assessment.

### Risk: `workbench_common.py` Becomes Too Large

Mitigation:

- Keep first implementation localized.
- If helpers exceed a clear size threshold, split into `scripts/workbench_skill_sources.py` in a follow-up, not before value is visible.

### Risk: UI Writes Unsafe Objects

Mitigation:

- POST writes through existing writer/compiler functions.
- Provide dry-run mode first.
- Validate schema after write.

### Risk: Static `real-task-001` Special-Case Logic

Mitigation:

- Real-task-specific source mapping may exist for first milestone, but functions must degrade generically for other topics.
- Do not hardcode conclusions in UI; aggregate from artifacts.

## 9. ADR

### Decision

Implement a skill-centered extension of the existing file-backed workbench before building a larger backend or product UI.

### Drivers

- The project’s research progression is skill-centered.
- Existing artifacts already encode the active skill, method family, structural diagnosis, effectiveness evidence, and claim boundary.
- The next milestone must be visible and usable without replatforming.

### Alternatives Considered

- Build new backend package first.
- Build UI directly from current topic JSON.
- Continue adding schemas before UI/API.

### Why Chosen

The chosen path is the shortest coherent route that preserves evidence grounding and makes the skill-centered research state visible to humans.

### Consequences

- Some code initially remains in `scripts/workbench_common.py`.
- The first UI will be local/file-backed rather than a polished multi-user app.
- The design can still evolve toward API/package separation once the interaction proves useful.

### Follow-Ups

- Add stable schemas for skill cockpit objects after JSON shapes are validated.
- Integrate `loop_context.json` into the generic loop worker prompt.
- Add LLM mentor brief worker with grounding and overclaim gates.

## 10. Follow-Up Staffing Guidance

### Direct / Ralph Path

Recommended for a single-session implementation.

Suggested lanes:

- `executor`: implement workbench_common skill aggregation, API, UI.
- `test-engineer`: add verification script and focused tests.
- `code-reviewer`: review claim-boundary and skill-status correctness.

Ralph launch hint:

```text
$ralph implement .omx/plans/skill-centered-collaborative-workbench-implementation-plan.md
```

### Team Path

Recommended if parallel implementation is desired.

Suggested workers:

- Worker 1: backend/object aggregation in `scripts/workbench_common.py`.
- Worker 2: verification and tests in `scripts/verify_skill_centered_workbench.py` and `tests/`.
- Worker 3: API and UI in `scripts/serve_workbench_api.py` and `workbench_ui/`.
- Worker 4: docs and final evidence report.

Team launch hint:

```text
$team implement .omx/plans/skill-centered-collaborative-workbench-implementation-plan.md
```

Team verification path:

- Team proves all backend and UI acceptance checks pass.
- Leader reruns the full command list in Section 7.
- Final report must include changed files, verification output, and remaining risks.
