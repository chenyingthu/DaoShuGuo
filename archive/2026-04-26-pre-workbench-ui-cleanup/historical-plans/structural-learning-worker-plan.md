# Structural Learning Worker Plan

## 1. Purpose

This plan introduces a lightweight learning/literature worker layer.

The goal is not to add complexity for its own sake. The goal is to prevent the research loop from staying at local skill-use optimization and to create a structured path toward skill-structure improvement.

The target object chain is:

`skill-use observation -> learning_need -> learning_context_pack -> skill_structure_diagnosis -> structural_skill_change_request`

## 2. Background

The current task003 iter02 review gate correctly classifies the observed improvement as:

`skill-use improvement, not verified skill-structure improvement`

This is honest but insufficient. If the loop only continues with the same context, it will likely produce more parameter tuning, search-envelope expansion, or task-specific adaptation.

A research-grade loop needs a learning step:

1. Identify what external knowledge is missing.
2. Retrieve or curate relevant learning material.
3. Convert that material into method/process/standard insights.
4. Generate a structural change request instead of another metric-only tuning request.

## 3. Role Separation

### 3.1 Cognition Worker

The cognition worker owns research judgment.

It should:

- Identify whether an observation is skill-use or skill-structure.
- Produce `learning_need` when external knowledge is required.
- Read `learning_context_pack`.
- Produce `skill_structure_diagnosis`.
- Propose `structural_skill_change_request`.

It should not:

- Silently invent literature knowledge.
- Hide source uncertainty.
- Directly fetch and rewrite source evidence without a learning artifact.

### 3.2 Learning Worker

The learning worker owns material acquisition and curation.

It should:

- Read `learning_need`.
- Gather or curate papers, code references, standards, reports, and existing method cards.
- Produce `learning_context_pack`.
- Summarize source relevance, evidence grade, method/process/standard relevance, and boundaries.

It should not:

- Decide final cognition upgrades.
- Claim that a skill has structurally improved.
- Decide next skill implementation.

### 3.3 Skill Worker

The skill worker owns implementation.

It should:

- Read `structural_skill_change_request`.
- Implement bounded method/process/standard changes.
- Report whether it changed method, process, standard, or only usage parameters.

It should not:

- Use learning material to bypass evaluator/review gates.
- Claim causality or research value.

## 4. New Objects

### 4.1 `learning_need`

Captures what the cognition worker needs to learn.

Minimum fields:

- task ref
- source review ref
- observation type
- skill dimension focus
- learning questions
- required source types
- exclusion criteria
- success criteria

### 4.2 `learning_context_pack`

Curated evidence package produced by the learning worker.

Minimum fields:

- learning need ref
- source refs
- source summaries
- method insights
- process insights
- standard insights
- applicability boundaries
- confidence and gaps

### 4.3 `skill_structure_diagnosis`

Cognition-worker judgment after reading the learning context.

Minimum fields:

- learning context ref
- diagnosis class
- method diagnosis
- process diagnosis
- standard diagnosis
- skill-use vs skill-structure judgment
- reusable principle candidates
- unresolved uncertainty

### 4.4 `structural_skill_change_request`

Request to the skill worker for structural change.

Minimum fields:

- diagnosis ref
- target skill ref
- change type
- method changes
- process changes
- standard changes
- forbidden usage-only shortcuts
- required validation
- claim boundary

## 5. MVP Scope

The first implementation must:

- Add schemas and samples for the four objects.
- Add a deterministic builder that reconstructs task003 iter02 into the new object chain.
- Use existing local literature/method artifacts if available.
- If no suitable local source exists, produce a seed learning context explicitly marked as curated seed material.
- Add a verifier that checks the chain and prevents structural-skill claims without method/process/standard evidence.

The first implementation must not:

- Introduce a full new agent runtime.
- Perform uncontrolled web search inside the core script.
- Replace the existing review gate.
- Claim task003 has achieved skill-structure improvement.

## 6. Acceptance Criteria

- [x] `learning_need` exists for task003 iter02 and is linked to the review gate result.
- [x] `learning_context_pack` exists and is linked to source material.
- [x] `skill_structure_diagnosis` explicitly classifies task003 iter02 as `skill_use_improvement_only` unless new evidence supports otherwise.
- [x] `structural_skill_change_request` targets method/process/standard changes, not only parameter tuning.
- [x] `skill_structure_assessment` evaluates method/process/standard/skill-use evidence separately.
- [x] Schema validation passes.
- [x] Verifier catches missing learning context, missing source refs, and missing skill-use/skill-structure classification.
- [x] Verifier blocks verified structural improvement claims unless structural evidence is validated.

## 7. Long-Term Direction

After the MVP, the learning worker can be upgraded to a real agent that performs literature/code search through approved providers. Even then, the output must remain objectized and reviewable.

The learning worker is not a magic knowledge source. It is a disciplined research assistant that turns the cognition worker's learning needs into reusable, auditable learning material.
