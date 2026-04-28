# Structural Learning Worker Protocol

## 1. Purpose

This protocol defines how external learning enters the autonomous research loop.

It exists because repeated skill loops can otherwise collapse into local parameter tuning. The learning layer forces the system to ask whether an observed improvement reveals a deeper method, process, or standard improvement.

## 2. Required Chain

The minimal chain is:

1. `learning_need`
2. `learning_context_pack`
3. `skill_structure_diagnosis`
4. `structural_skill_change_request`

No structural skill improvement claim is allowed without this chain.

## 3. Learning Need

`learning_need` is produced by a cognition worker or review gate after observing a gap.

It must answer:

- What is missing?
- Which skill dimension is involved: method, process, standard, or mixed?
- What sources are needed?
- What sources are excluded?
- What evidence would be sufficient to move beyond skill-use improvement?

## 4. Learning Context Pack

`learning_context_pack` is produced by a learning worker.

It must contain:

- source references
- source summaries
- method insights
- process insights
- standard insights
- applicability boundaries
- confidence and gaps

It may use curated seed material in early MVP tests, but must label it as such.

## 5. Skill Structure Diagnosis

`skill_structure_diagnosis` is produced by a cognition worker after reading the learning context.

It must classify the current observation as one of:

- `skill_use_improvement_only`
- `potential_method_improvement`
- `potential_process_improvement`
- `potential_standard_improvement`
- `verified_structural_improvement`
- `insufficient_learning_evidence`

Only `verified_structural_improvement` can support a structural skill improvement claim, and only if validation evidence also exists.

## 6. Structural Skill Change Request

`structural_skill_change_request` tells the skill worker what to change structurally.

It must specify:

- target skill
- change type
- method changes
- process changes
- standard changes
- forbidden usage-only shortcuts
- required validation
- claim boundary

If it only changes parameters, search grid, or boundary conditions, it must be classified as `skill_use_tuning`, not structural change.

## 7. Review Gate Integration

The review gate must check:

- Does a structural claim have a learning chain?
- Does the diagnosis distinguish skill-use from skill-structure?
- Does the request target method/process/standard rather than only parameters?
- Are source refs and applicability boundaries present?

Without these checks, the strongest allowed claim remains:

`skill performance improved under current evaluator and current use conditions`

## 8. Structural Skill Assessment

`skill_structure_assessment` is the evaluator object for the most important claim:

> Did this loop produce a structural skill improvement, or only a skill-use improvement?

It evaluates four dimensions:

1. `method_score`: whether the method became more accurate, efficient, generalizable, explainable, or principled.
2. `process_score`: whether the workflow became clearer, simpler, reusable, or better controlled.
3. `standard_score`: whether the evaluation standard became richer, more measurable, more determinate, or stronger.
4. `skill_use_score`: whether the observed improvement is mainly due to parameters, boundary conditions, search envelope, invocation, or resource budget.

The score scale is:

- `0`: no evidence
- `1`: planned or weak evidence
- `2`: implemented evidence
- `3`: validated evidence

Verdict rules:

- `verified_structural_improvement`: at least one of method/process/standard score is 3, no blocking overclaim, and validation evidence exists.
- `structural_attempt_ready`: method/process/standard changes are specified but not validated.
- `skill_use_improvement_only`: skill-use score is stronger than structural evidence.
- `insufficient_evidence`: required evidence is missing.
- `rejected_overclaim`: the output claims structural improvement without evidence.

No report, review, or loop controller may claim structural skill improvement unless a `skill_structure_assessment` has verdict `verified_structural_improvement`.

## 9. Role Boundary

The learning worker curates material. It does not make final research judgments.

The cognition worker interprets material. It does not silently invent source evidence.

The skill worker implements bounded changes. It does not claim research value.
