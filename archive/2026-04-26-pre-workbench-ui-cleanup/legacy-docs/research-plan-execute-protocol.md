# Research Plan-Execute Protocol

## 1. Purpose

`research-plan-execute` is the execution discipline layer for the DaoShuGuo autonomous research framework.

It does not replace the existing generic loop engine. It adds the missing plan, context, review, repair, approval, and resume protocol required to make agentic research work auditable and reusable.

## 2. Layering

The protocol uses existing framework layers instead of duplicating them:

- `generic loop engine`: phase orchestration, artifact chain, state transitions, task adapter access.
- `generic diagnosis layer`: problem class, routing policy, diagnosis validation.
- `research-plan-execute`: research plan batches, context packs, runtime binding, review gates, repair routing, approval records, execution ledger.

If a capability already exists in the generic loop engine or diagnosis layer, this protocol must call or extend it rather than reimplementing it.

## 3. Standard Batch Flow

One research batch follows this order:

1. Read `research_plan`.
2. Create `research_batch`.
3. Create `worker_runtime_binding`.
4. Create `agent_context_pack`.
5. Run the assigned worker.
6. Validate produced artifacts.
7. Run review gate and produce `research_review`.
8. If approved, write `approval_record`.
9. If not approved, write `repair_request` and route to a repair worker.
10. Record every state transition in `execution_ledger`.

## 4. Review Gate Rules

Only `approved` can proceed without restriction.

`real_progress` may proceed only as `bounded_next_iteration`, and must include at least one of:

- claim boundary
- required ablation
- required repair note

The following verdicts must route to repair or human review:

- `needs_fix`
- `stagnation`
- `cheating_suspected`
- `insufficient_evidence`
- `pause_for_human_review`

`approved_with_ablation_required` may continue execution, but all causality claims remain frozen until ablation evidence exists.

## 5. Repair Rules

Each repair must produce both:

- `repair_request`
- `repair_result`

The same `repair_request` may be automatically retried at most two times. A third failure routes to `human_review`.

Repairs must not lower the quality bar by:

- weakening evaluator criteria
- deleting required references
- relaxing schema constraints
- erasing failure artifacts

## 6. Context Pack Rules

Every agent call must be driven by a persisted `agent_context_pack`.

The prompt may be rendered from the context pack, but scripts must not scatter task-specific prompt construction logic outside the context pack builder.

The context pack must include:

- mission
- role boundary
- task references
- prior artifacts
- allowed changes
- blocked paths
- evaluator and baseline references
- review history
- current hypothesis
- required output schema
- stop conditions
- token and context budget
- artifact provenance digest
- redaction and secret policy
- expected failure modes
- previous repair attempts

## 7. Runtime Binding

Every worker call must have a `worker_runtime_binding` declaring:

- runtime kind
- provider/model binding
- tool permission profile
- session reuse policy
- timeout and retry policy
- raw transcript path

Every worker output must reference the runtime binding or record equivalent runtime provenance in metadata.

## 8. Immutability And Resume

Verified artifacts are immutable by default.

Reruns must not silently overwrite existing artifacts. They must create:

- a new iteration
- a new repair attempt
- or an explicit superseding artifact

`execution_ledger` records batch states:

- started
- context_created
- worker_completed
- validation_passed
- validation_failed
- review_completed
- repair_requested
- approved
- stopped

An interrupted executor must resume from the ledger rather than infer state from file existence alone.

## 9. Causality Claims

Performance improvement is not sufficient evidence that cognition caused skill improvement.

Without ablation, the strongest allowed claim is:

`skill performance improved under current evaluator`

The following claims require an `ablation_result`:

- cognition caused skill improvement
- research taste improved the method
- agent autonomously discovered a superior principle

Minimum ablation requirements:

1. Compare old skill and new skill under the same evaluator.
2. Compare cognition-guided request and deterministic or metric-only baseline request.
3. Fix search budget.
4. Separate search-space expansion effects from cognition-constraint effects.

## 10. Skill Improvement Semantics

In this project, a skill is not only an algorithm file. A complete skill contains:

1. Method: functions, algorithms, and concrete logic for processing information or data.
2. Process: the organization of methods, including branching, parallelism, conditions, loops, and data flow.
3. Standard: measurable quality criteria, metrics, evaluation rules, and comparative judgment.

Every skill worker output must state which of these dimensions changed.

The protocol distinguishes two improvement classes:

1. Skill-use improvement.
   - Better metrics caused by changed parameters, search envelope, boundary conditions, invocation strategy, or resource budget.
   - This is valid evidence, but it is not sufficient to claim structural skill improvement.
2. Skill-structure improvement.
   - Method becomes more accurate, efficient, scalable, generalizable, or explainable.
   - Process becomes clearer, simpler, reusable, or better controlled.
   - Standard becomes richer, more measurable, more determinate, or demonstrably stronger.

The review gate must not approve a claim of `skill improved` unless the review identifies whether the improvement is skill-use or skill-structure.

The strongest allowed claim for a pure skill-use improvement is:

`skill performance improved under current evaluator and current use conditions`

It must not be rewritten as:

- `the skill structure improved`
- `the method became generally stronger`
- `the agent discovered a better research principle`

A useful research loop may start from skill-use improvement, but the loop must convert it into questions about method, process, or standard. If repeated iterations only tune boundary conditions without improving method/process/standard, the loop must be labeled:

`local_skill_use_optimization`

It must not be labeled:

`agentic_skill_evolution_verified`

## 11. Deterministic Baseline

Every agentic judgment should keep a deterministic baseline comparison.

If no baseline exists, the batch must be labeled:

`agentic_trial_without_baseline`

It must not be labeled:

`agentic_improvement_verified`

## 12. MVP Scope

The first implementation must cover only:

- protocol schemas
- task003 iter02 context-pack reconstruction
- context pack rendering
- protocol validation

It must not implement a full new loop runner before the context and review gates are stable.
