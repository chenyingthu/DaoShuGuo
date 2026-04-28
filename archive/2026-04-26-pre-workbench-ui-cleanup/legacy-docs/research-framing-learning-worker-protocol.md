# Research Framing Learning Worker Protocol

## 1. Purpose

This protocol defines how external learning enters a real research-task loop.

It extends the structural learning chain from local skill-use diagnosis into research framing:

`real evidence -> learning_need -> learning_context_pack -> framing/method/metric/claim maps -> cognition reframing -> structural change request -> upgraded effectiveness test`

The learning worker is not a report-polishing worker. Its job is to expose the external method space, metric space, and claim threshold space so that the cognition worker can make better research judgments.

## 2. Role Boundary

The learning worker may:

1. Curate source material.
2. Summarize method families.
3. Map problem framings.
4. Map metrics to supportable claims.
5. Recommend experiment designs and evidence thresholds.

The learning worker must not:

1. Decide final research value.
2. Claim structural skill improvement.
3. Rewrite evaluator standards to make a result look better.
4. Treat more citations as cognition improvement.

The cognition worker interprets the learning pack. The controller only schedules, validates, stores, and routes objects.

## 3. Required Objects

The minimal research-framing learning chain contains:

1. `learning_need`
2. `learning_context_pack`
3. `research_framing_map`
4. `method_family_map`
5. `metric_taxonomy`
6. `claim_threshold_map`
7. `experiment_design_recommendation`
8. `skill_structure_diagnosis`
9. `structural_skill_change_request`

## 4. Source Modes

Allowed source modes:

1. `curated_seed`
2. `manual_summary`
3. `abstract_excerpt`
4. `fulltext_excerpt`
5. `external_search`

Early MVP runs may use `curated_seed`, but must label it. A curated seed pack can support framework validation and low-to-medium confidence reframing. It cannot support high-confidence literature claims.

## 5. Map Responsibilities

`research_framing_map` answers:

1. What problem definitions exist externally?
2. Which definitions match the current task?
3. Which definitions are out of scope?
4. What claim boundary follows from each framing?

`method_family_map` answers:

1. What method families are available?
2. Which skill dimension each family affects: method, process, standard, or mixed?
3. Which family is only a parameter-use variant?
4. What minimum validation is needed?

`metric_taxonomy` answers:

1. Which metrics are primary.
2. Which metrics are secondary.
3. Which claims each metric can support.
4. Which claims each metric cannot support.

`claim_threshold_map` answers:

1. What is required for `diaomu`.
2. What is required for `zhuoshi`.
3. What is required for paper-candidate routing.
4. Which claims remain forbidden.

`experiment_design_recommendation` answers:

1. What minimum matrix can test the reframed problem.
2. Which shortcuts are excluded.
3. Which evidence is needed before structural improvement can be claimed.

## 6. Claim Discipline

No loop may claim `verified_structural_improvement` unless:

1. A learning chain exists.
2. A cognition worker has produced `skill_structure_diagnosis`.
3. A structural change request targets method, process, or standard.
4. An upgraded effectiveness test validates the change.
5. A review gate confirms the claim boundary.

If only parameters, scan range, or resource budget changed, the strongest allowed claim is:

`skill-use condition changed and was evaluated under the current standard`

## 7. Verification

A valid research-framing learning chain must pass:

```bash
python scripts/validate_schemas.py --artifacts real-task-001-reframing
python scripts/verify_real_task001_reframing.py
```

The verifier must check:

1. Required objects exist.
2. Object references form a connected chain.
3. The method map includes at least one non-parameter structural candidate.
4. The metric taxonomy preserves the primary metric boundary.
5. The claim threshold map prevents secondary metric overclaim.
6. The structural change request does not only request parameter tuning.
